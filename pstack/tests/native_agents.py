#!/usr/bin/env python3
"""Run both registered personas through native delegation in an isolated project."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import tomllib

PSTACK = Path(__file__).resolve().parents[1]


def snapshot(project):
    return {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in project.rglob("*") if p.is_file() and ".git" not in p.parts
            and "__pycache__" not in p.parts}


def execute(command, project, env, prompt, output, timeout=240):
    with output.open("w") as stdout, output.with_suffix(".stderr").open("w") as stderr:
        process = subprocess.Popen(command, cwd=project, env=env, stdin=subprocess.PIPE,
                                   text=True, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.communicate(input=prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                pass
            # A child can ignore TERM after its parent exits; stop the whole group.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            return {"exit_code": None, "status": "timeout", "events": []}
    events = [json.loads(line) for line in output.read_text().splitlines() if line.strip()]
    return {"exit_code": process.returncode, "events": events}


def summarize_claude(run):
    events = run.pop("events")
    initial = next((e for e in events if e.get("subtype") == "init"), {})
    terminal = [e for e in events if e.get("type") == "result"]
    started = [e for e in events if e.get("subtype") == "task_started"
               and e.get("task_type") == "local_agent"]
    finished = [e for e in events if e.get("subtype") == "task_notification"]
    completed = {e.get("task_id") for e in finished if e.get("status") == "completed"}
    agents = [{"name": e.get("subagent_type"), "id": e.get("task_id"),
               "run_id": e.get("run_id"), "background": e.get("is_backgrounded"),
               "completed": e.get("task_id") in completed} for e in started]
    run.update(session_id=initial.get("session_id"), agents=agents,
               permission_mode=initial.get("permissionMode"), tools=initial.get("tools"),
               registered_agents=initial.get("agents"),
               terminal_results=[{"is_error": e.get("is_error"),
                                  "subagent_stats": e.get("subagent_stats"),
                                  "permission_denials": e.get("permission_denials"),
                                  "result": e.get("result")} for e in terminal])
    run["status"] = "passed" if run.get("exit_code") == 0 and all(
        any(a["name"] == name and a["completed"] for a in agents)
        for name in ("poteto-agent", "comment-sicko")) else "unverified"
    return run


def summarize_codex(run, home, project):
    events = run.pop("events")
    items = [e["item"] for e in events if e.get("type") == "item.completed"]
    calls = [i for i in items if i.get("type") == "collab_tool_call"]
    run.update(thread_id=next((e.get("thread_id") for e in events
                               if e.get("type") == "thread.started"), None),
               delegation=calls,
               messages=[i.get("text") for i in items if i.get("type") == "agent_message"])
    agents = []
    database = home / "state_5.sqlite"
    if database.is_file():
        with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
            rows = connection.execute(
                "SELECT id, agent_role, rollout_path, sandbox_policy, approval_mode "
                "FROM threads WHERE cwd = ? AND agent_role IS NOT NULL", (str(project),)).fetchall()
        for identifier, name, rollout, sandbox, approval in rows:
            path = Path(rollout)
            records = [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []
            terminals = [e["payload"] for e in records if e.get("type") == "event_msg"
                         and e.get("payload", {}).get("type") == "task_complete"]
            persona = tomllib.loads((project / f".codex/agents/{name}.toml").read_text())["developer_instructions"]
            developer_texts = [content.get("text") for e in records
                               if e.get("type") == "response_item"
                               and e.get("payload", {}).get("role") == "developer"
                               for content in e["payload"].get("content", [])]
            tool_calls = [{"name": e["payload"].get("name"),
                           "input": e["payload"].get("input", e["payload"].get("arguments"))}
                          for e in records if e.get("type") == "response_item"
                          and e.get("payload", {}).get("type") in ("custom_tool_call", "function_call")]
            agents.append({"id": identifier, "name": name, "sandbox_policy": sandbox,
                           "approval_mode": approval, "completed": bool(terminals),
                           "persona_loaded_exactly": persona in developer_texts,
                           "persona_sha256": hashlib.sha256(persona.encode()).hexdigest(),
                           "tool_calls": tool_calls,
                           "terminal": terminals[-1] if terminals else None})
    run["agents"] = agents
    run["status"] = "passed" if run.get("exit_code") == 0 and all(
        any(a["name"] == name and a["completed"] and a["persona_loaded_exactly"] for a in agents)
        for name in ("poteto-agent", "comment-sicko")) else "unverified"
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["codex", "claude-code", "both"], default="both")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Python 3.11+ is required")
    base = Path(tempfile.mkdtemp(prefix="pstack-native-agents-")).resolve()
    project = base / "project"
    project.mkdir()
    for folder in (".agents", ".claude"):
        shutil.copytree(PSTACK / "skills", project / folder / "skills")
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PSTACK, text=True).strip()
    env = {**os.environ, "NODE_OPTIONS": "", "CLAUDECODE": ""}
    hosts = ["codex", "claude-code"] if args.host == "both" else [args.host]
    for host in hosts:
        folder = ".agents" if host == "codex" else ".claude"
        script = project / folder / "skills/pstack-support/scripts/setup.py"
        subprocess.run([sys.executable, str(script), "--host", host, "--project", str(project),
                        "--source-commit", sha, "--write"], check=True, env=env)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    (project / "sample.py").write_text("def identity(value):\n    # Return the value.\n    return value\n")
    (base / "empty-mcp.json").write_text('{"mcpServers":{}}')
    results = {}
    for host in hosts:
        folder = ".agents" if host == "codex" else ".claude"
        skills = project / folder / "skills"
        preflight = (f"{sys.executable} {skills}/pstack-support/scripts/setup.py --host {host} "
                     f"--project {project} --check --require poteto-mode "
                     f"--skill-location {skills}/poteto-mode")
        prompt = ("Native named subagent acceptance. Use the native registered-agent selector for "
                  "poteto-agent (agent_type in Codex, subagent_type in Claude Code). Ask it to read "
                  f"{skills}/poteto-mode/SKILL.md in full and run {preflight}, then report the final "
                  "heading and preflight JSON. Also invoke registered comment-sicko to read sample.py "
                  "and report its redundant comment. No generic agents, no further delegation, no "
                  "file writes. Use a fresh child with no inherited conversation history. "
                  "Wait for BOTH terminal results. If native selection is unavailable, "
                  "report BLOCKED. Do not launch another codex/claude CLI or test harness.")
        host_env = dict(env)
        if host == "codex":
            home = base / "codex-home"
            home.mkdir()
            auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
            if auth.is_file():
                (home / "auth.json").symlink_to(auth)
            (home / "config.toml").write_text(
                f"[projects.{json.dumps(str(project))}]\ntrust_level = \"trusted\"\n")
            host_env["CODEX_HOME"] = str(home)
            command = ["codex", "exec", "--ignore-rules", "--json",
                       "-s", "read-only", "-C", str(project)]
        else:
            command = ["claude", "--print", "--output-format", "stream-json", "--verbose",
                       "--no-session-persistence", "--setting-sources", "project,local",
                       "--strict-mcp-config", "--mcp-config", str(base / "empty-mcp.json"),
                       "--permission-mode", "dontAsk", "--permission-prompts", "none",
                       "--allowedTools", "Agent,Read,Bash", "--tools", "Agent,Read,Bash"]
        before = snapshot(project)
        run = execute(command, project, host_env, prompt, base / f"{host}.jsonl")
        result = summarize_codex(run, home, project) if host == "codex" else summarize_claude(run)
        result["fixture_unchanged"] = before == snapshot(project)
        result["command"] = command
        result["version"] = subprocess.check_output(
            [command[0], "--version"], text=True).strip()
        results[host] = result
    report = {"tested_at": datetime.now(timezone.utc).isoformat(), "source_commit": sha,
              "fixture": str(project), "raw_logs": str(base), "results": results,
              "permission_limit": "Claude Agent/Read/Bash are allowed; no read-only sandbox is claimed."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Evidence: {args.output}; raw logs: {base}")


if __name__ == "__main__":
    main()
