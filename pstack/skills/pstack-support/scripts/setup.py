#!/usr/bin/env python3
"""Project-scoped host setup. Python 3.11+, standard library only."""
import argparse
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib

SUPPORT = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation"
INSTALL = f"npx skills@1.7.2 add {SOURCE} --skill pstack-support --agent codex claude-code"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_manifest():
    try:
        manifest = json.loads((SUPPORT / "manifest.json").read_text())
        if manifest["schema"] != 1 or not re.fullmatch(r"[0-9a-f]{40}", manifest["source_commit"]):
            raise ValueError("invalid provenance")
        if not isinstance(manifest["skills"], dict) or not isinstance(manifest["support_files"], dict):
            raise ValueError("invalid file catalog")
        required = {"scripts/setup.py", "references/host-instructions.md", "agents/poteto-agent.md", "agents/comment-sicko.md", "LICENSE"}
        if not required.issubset(manifest["support_files"]):
            raise ValueError("incomplete support catalog")
        for name, expected in manifest["support_files"].items():
            if not isinstance(name, str) or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError("invalid support hash")
            path = SUPPORT / name
            if not path.resolve().is_relative_to(SUPPORT) or digest(path.read_bytes()) != expected:
                raise ValueError(f"damaged support file: {name}")
        for name, skill in manifest["skills"].items():
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]+", name) or not isinstance(skill, dict) or not isinstance(skill.get("files"), dict) or "SKILL.md" not in skill["files"]:
                raise ValueError("invalid skill catalog")
            if any(not isinstance(file, str) or not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum) for file, checksum in skill["files"].items()):
                raise ValueError("invalid skill hash")
        return manifest
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(f"Invalid pstack-support installation: {error}. Reinstall with: {INSTALL}") from error


def skill_roots(project, host):
    project_dirs = [".agents/skills", ".codex/skills"] if host == "codex" else [".claude/skills", ".agents/skills"]
    home = Path.home()
    global_dirs = [home / ".agents/skills", Path(os.environ.get("CODEX_HOME", home / ".codex")) / "skills"] if host == "codex" else [home / ".claude/skills", home / ".agents/skills"]
    return [project / d for d in project_dirs] + global_dirs


def preflight(project, host, required=(), skill_location=None):
    manifest = read_manifest()
    roots = skill_roots(project, host)
    installed_support = next((r / "pstack-support" for r in roots if (r / "pstack-support").exists()), None)
    if installed_support is None or installed_support.resolve() != SUPPORT:
        raise ValueError(f"This support copy is not the active {host} installation. Project skills override global copies. {INSTALL}")
    required = set(required)
    seen = set()
    for name, spec in manifest["skills"].items():
        location = next((r / name for r in roots if (r / name).exists()), None)
        if location is None:
            if name in required:
                raise ValueError(f"Missing project or global skill {name}; install it with pstack-support from {SOURCE}")
            continue
        seen.add(location.resolve())
        for file, expected in spec["files"].items():
            path = location / file
            if not path.resolve().is_relative_to(location.resolve()) or not path.is_file() or digest(path.read_bytes()) != expected:
                raise ValueError(f"Mixed, modified or incomplete pstack installation at {path}. Reinstall matching skills and support from {SOURCE}")
    if required - manifest["skills"].keys():
        raise ValueError("Unknown required skill")
    if skill_location and Path(skill_location).resolve() not in seen:
        raise ValueError("The invoking skill location is not the active installed version")
    return manifest


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        temporary = Path(tmp.name)
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
    try:
        temporary.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o600)
        temporary.replace(path)
        if path.read_bytes() != data:
            raise ValueError(f"Readback failed: {path}")
    finally:
        temporary.unlink(missing_ok=True)


def parse_agent(text, host):
    if host == "codex":
        return tomllib.loads(text)
    front, body = text.split("\n---\n", 1)
    fields = {}
    for line in front.removeprefix("---\n").splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key] = value.strip().strip('"')
    fields["developer_instructions"] = body.lstrip("\n")
    return fields


def agent_text(name, host):
    original = (SUPPORT / "agents" / f"{name}.md").read_text()
    fields = parse_agent(original, "claude-code")
    body = fields["developer_instructions"]
    if host == "codex":
        return "\n".join(f"{key} = {json.dumps(value)}" for key, value in {
            "name": name, "description": fields["description"], "developer_instructions": body,
        }.items()) + "\n"
    background = "background: true\n" if name == "poteto-agent" else ""
    return f'---\nname: {name}\ndescription: {json.dumps(fields["description"])}\nmodel: inherit\n{background}---\n\n{body}'


def update_agent(current, desired, previous, host):
    if current == previous:
        # Preserve user-owned model, effort, permission, tool and other fields.
        old = parse_agent(current, host)
        new = parse_agent(desired, host)
        if all(old.get(key) == new[key] for key in ("name", "description", "developer_instructions")):
            return current
        if host == "codex":
            for key in ("name", "description", "developer_instructions"):
                current = re.sub(rf"(?m)^{key}[ \t]*=[ \t]*\"(?:[^\"\\]|\\.)*\"[ \t]*$",
                                 lambda _: f"{key} = {json.dumps(new[key])}", current)
            updated = parse_agent(current, host)
            if any(updated.get(key) != new[key] for key in ("name", "description", "developer_instructions")):
                raise ValueError("Agent uses a custom TOML representation; review and merge this update")
            return current
        front, _ = current.split("\n---\n", 1)
        front = re.sub(r"(?m)^description:.*$", lambda _: f'description: {json.dumps(new["description"])}', front)
        return front + "\n---\n\n" + new["developer_instructions"]
    raise ValueError("local modifications")


def managed_block(text, host):
    begin, end = "<!-- pstack:begin -->", "<!-- pstack:end -->"
    if text.count(begin) != text.count(end) or text.count(begin) > 1:
        raise ValueError("Invalid pstack instruction block")
    existing = re.search(re.escape(begin) + r".*?" + re.escape(end), text, re.S)
    if begin in text and existing is None:
        raise ValueError("Invalid pstack instruction block order")
    models = "\n".join(line for line in (existing.group() if existing else "").splitlines() if line.startswith("pstack-role "))
    content = (SUPPORT / "references/host-instructions.md").read_text().strip()
    block = f"{begin}\n{content}\n\nHost: {host}.\n{models}\n{end}"
    return text[:existing.start()] + block + text[existing.end():] if existing else text.rstrip() + "\n\n" + block + "\n"


def setup(project, host, write=False, benny=False, accepted=None, source_commit=None):
    accepted = accepted or {}
    manifest = preflight(project, host, ("setup-pstack", "poteto-mode"))
    state_path = project / ".pstack" / f"setup-{host}.json"
    if not state_path.resolve().is_relative_to(project) or state_path.is_symlink():
        raise ValueError("Linked setup state")
    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
            if state["schema"] != 1 or state["host"] != host or not re.fullmatch(r"[0-9a-f]{40}", state["source_commit"]):
                raise ValueError("Invalid setup provenance")
            records = state["files"]
            for record in records.values():
                if digest(record["written"].encode()) != record["sha256"]:
                    raise ValueError("Invalid last-written hash")
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError(f"Corrupt setup state: {error}") from error
    else:
        records = {}
    if benny:
        other_host = "claude-code" if host == "codex" else "codex"
        other_state = project / ".pstack" / f"setup-{other_host}.json"
        if other_state.exists():
            if other_state.is_symlink() or not other_state.resolve().is_relative_to(project):
                raise ValueError("Linked other-host setup state")
            try:
                other = json.loads(other_state.read_text())
                if other["schema"] != 1 or other["host"] != other_host or not re.fullmatch(r"[0-9a-f]{40}", other["source_commit"]):
                    raise ValueError("Invalid other-host setup provenance")
                for relative, record in other["files"].items():
                    if relative.startswith(".pstack/automations/benny/") and relative not in records:
                        if digest(record["written"].encode()) != record["sha256"]:
                            raise ValueError("Invalid other-host pack hash")
                        records[relative] = record
            except (ValueError, KeyError, TypeError) as error:
                raise ValueError(f"Corrupt other-host pack receipt: {error}") from error
    manifest_hash = digest((SUPPORT / "manifest.json").read_bytes())
    if source_commit is None:
        lock_path = project / "skills-lock.json"
        if lock_path.exists():
            try:
                locked = json.loads(lock_path.read_text())["skills"]["pstack-support"]
                ref = locked.get("ref", "")
                if re.fullmatch(r"[0-9a-f]{40}", ref):
                    source_commit = ref
            except (ValueError, KeyError, TypeError):
                pass
    if source_commit is None and state.get("support_manifest_sha256") == manifest_hash:
        source_commit = state["source_commit"]
    if source_commit is not None and not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("Installed source commit must be a full 40-character Git SHA")
    if write and source_commit is None:
        raise ValueError("Pin the skills install to its actual Git commit, or supply --source-commit <verified installed fork SHA>. Upstream provenance is not the installed fork commit.")
    new_records = dict(records)
    changes, conflicts = {}, []
    agent_dir = ".codex/agents" if host == "codex" else ".claude/agents"
    desired = {f"{agent_dir}/{name}.{'toml' if host == 'codex' else 'md'}": agent_text(name, host)
               for name in ("poteto-agent", "comment-sicko")}
    instruction = "AGENTS.md" if host == "codex" else "CLAUDE.md"
    instruction_path = project / instruction
    desired[instruction] = managed_block(instruction_path.read_text() if instruction_path.exists() else "", host)
    if benny:
        for relative in manifest["support_files"]:
            if relative.startswith("automations/benny/"):
                desired[f".pstack/{relative}"] = (SUPPORT / relative).read_text()
    for relative, candidate in desired.items():
        path = project / relative
        if not path.resolve().is_relative_to(project) or path.is_symlink():
            raise ValueError(f"Refusing linked destination: {path}")
        current = path.read_text() if path.exists() else None
        record = records.get(relative)
        adopted = False
        if relative in accepted:
            if current is None or digest(current.encode()) != accepted[relative]:
                raise ValueError(f"Reviewed merge hash changed: {relative}")
            if relative.startswith(agent_dir):
                parsed = parse_agent(current, host)
                if parsed.get("name") != Path(relative).stem or not parsed.get("description") or not parsed.get("developer_instructions"):
                    raise ValueError(f"Invalid merged agent: {relative}")
            if relative.startswith(agent_dir):
                proposed_fields = parse_agent(candidate, host)
                adopted = any(parsed.get(key) != proposed_fields.get(key) for key in ("name", "description", "developer_instructions"))
            else:
                adopted = True
            candidate = current
        extract_block = lambda text: re.search(r"<!-- pstack:begin -->.*?<!-- pstack:end -->", text or "", re.S)
        adopted_current = current == record["written"] if record else False
        upstream_equal = record.get("upstream") == candidate if record else False
        if record and relative == instruction and record.get("adopted"):
            old_block, live_block = extract_block(record["written"]), extract_block(current)
            upstream_block, next_block = extract_block(record.get("upstream")), extract_block(candidate)
            normalize_roles = lambda block: re.sub(r"(?m)^pstack-role .*\n?", "", block)
            adopted_current = bool(old_block and live_block and normalize_roles(old_block.group()) == normalize_roles(live_block.group()))
            upstream_equal = bool(upstream_block and next_block and normalize_roles(upstream_block.group()) == normalize_roles(next_block.group()))
        if record and record.get("adopted") and adopted_current and relative not in accepted:
            if not upstream_equal:
                conflicts.append(relative)
                print("".join(difflib.unified_diff(current.splitlines(True), candidate.splitlines(True), fromfile=relative, tofile="proposed")))
                continue
            candidate = current
            adopted = True
        if relative == instruction:
            # Only the managed block is owned; surrounding user instructions are preserved.
            extract = lambda text: re.search(r"<!-- pstack:begin -->.*?<!-- pstack:end -->", text, re.S)
            current_block = extract(current or "")
            previous_block = extract(record["written"]) if record else None
            if relative not in accepted and not adopted and current_block and (not previous_block or current_block.group() != previous_block.group()):
                # Model rows are user-owned and can be changed without losing provenance.
                normalize = lambda block: re.sub(r"(?m)^pstack-role .*\n?", "", block)
                if not previous_block or normalize(current_block.group()) != normalize(previous_block.group()):
                    conflicts.append(relative)
                    continue
        elif current is not None and not adopted and relative not in accepted:
            if not record:
                conflicts.append(relative)
                continue
            if current != record["written"]:
                conflicts.append(relative)
                print("".join(difflib.unified_diff(record["written"].splitlines(True), current.splitlines(True), fromfile="last-written", tofile=relative)))
                print("".join(difflib.unified_diff(current.splitlines(True), candidate.splitlines(True), fromfile=relative, tofile="proposed")))
                continue
            if relative.startswith(agent_dir):
                candidate = update_agent(current, candidate, record["written"], host)
        if current != candidate:
            changes[path] = candidate.encode()
        new_records[relative] = {"sha256": digest(candidate.encode()), "written": candidate,
                                 "adopted": adopted, "upstream": desired[relative]}
    if accepted.keys() - desired.keys():
        raise ValueError("Accepted merge path is not a managed target")
    if conflicts:
        raise ValueError("Resolve ownership/local changes before setup: " + ", ".join(conflicts) + ". No managed files written. Review and merge, then pass --accept-merge path=sha256 for each exact reviewed file.")
    receipt = json.dumps({"schema": 1, "host": host, "source_commit": source_commit,
                          "upstream_commit": manifest["source_commit"], "support_manifest_sha256": manifest_hash,
                          "adapter_version": manifest["adapter_version"], "files": new_records}, indent=2) + "\n"
    if not state_path.exists() or state_path.read_text() != receipt:
        changes[state_path] = receipt.encode()
    print(json.dumps({"mode": "write" if write else "preview", "files": [str(p.relative_to(project)) for p in changes]}, indent=2))
    if write:
        for path, content in changes.items():
            atomic_write(path, content)
        print("Readback complete. Open a NEW trusted project session and actually invoke both named agents.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["codex", "claude-code"], required=True)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--skill-location", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--benny", action="store_true")
    parser.add_argument("--accept-merge", action="append", default=[], metavar="PATH=SHA256")
    parser.add_argument("--source-commit", help="Verified installed fork commit, when the installer did not record an immutable ref")
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        parser.error("Project directory must exist")
    try:
        accepted = {}
        for value in args.accept_merge:
            path, separator, checksum = value.partition("=")
            if not separator or not re.fullmatch(r"[0-9a-f]{64}", checksum):
                raise ValueError("--accept-merge must be a repository-relative path and exact SHA-256")
            accepted[path] = checksum
        if args.check:
            manifest = preflight(project, args.host, args.require, args.skill_location)
            print(json.dumps({"source_commit": manifest["source_commit"], "support": str(SUPPORT), "status": "ok"}))
        else:
            if args.write:
                lock_path = project / ".pstack/.setup.lock"
                if not lock_path.resolve().is_relative_to(project):
                    raise ValueError("Linked state directory")
                lock_path.parent.mkdir(exist_ok=True)
                with lock_path.open("a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX)
                    setup(project, args.host, True, args.benny, accepted, args.source_commit)
            else:
                setup(project, args.host, False, args.benny, accepted, args.source_commit)
    except (ValueError, OSError) as error:
        parser.exit(1, f"pstack: {error}\n")


if __name__ == "__main__":
    main()
