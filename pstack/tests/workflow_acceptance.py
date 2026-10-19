#!/usr/bin/env python3
"""Run explicit pstack entries in disposable projects; keep execution separate from acceptance.

No CLI invocation happens without --run. Reports never infer workflow success from
skill hashes, a zero CLI exit, or the model's own claim. Semantic review remains
open unless an independent observable contract below can establish the result.

--run cannot be removed: it separates inventory generation from paid model work.
--skills is optional and can be removed when all 54 scenarios are intended.
The temporary CODEX_HOME is required to test trusted role loading without global edits.
Clearing inherited NODE_OPTIONS is optional when the launcher already has no preload.
Clearing inherited CLAUDECODE is optional when not launched from a Claude session.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "pstack/skills"
REPORT = ROOT / "pstack/docs/workflow-acceptance.json"

# Each scenario is an application of the entry, rather than a request to summarize it.
TASKS = {
    "architect": ("independent-workflow", "Add a rename command to the local note CLI. Ground the current code, produce two distinct designs, cross-judge them, retain the chosen rationale and implement and exercise rename. Keep native delegate evidence; no external writes.", "Two independent candidates, judge result, rationale, rename behavior and native delegate lifecycle."),
    "arena": ("independent-workflow", "Use two native candidates to design a local note title deduplicator; cross-judge only after both finish, choose and graft a base, implement it and exercise duplicate and unique titles. Keep each candidate and synthesis note.", "Two candidate artifacts, independent judge, synthesis with provenance, actual duplicate/unique output."),
    "automate-me": ("independent-workflow", "Create acceptance-mode from supplied scoped-history.md. User handle is acceptance. Preferences: plain short replies; real CLI proof; project-local skills; no external publication. Author and iterate the skill locally; stop before any external PR. Record every unexercised interview/publication step.", "Project mode skill, two recurring scoped-history evidence pointers per rule, prose review; live interview and publication explicitly outstanding."),
    "benchmark-checklist": ("measurement", "Evaluate a claimed 2x speedup for python3 app.py list versus reading notes.json directly. Run and profile both paths, verify identical work/output, record tuning, repeatability and limiter; reject an unfair speedup claim instead of reporting it.", "Raw repeated samples, profile/counter evidence mapped to source, equivalent-work check, all seven checklist answers."),
    "blast-radius": ("independent-workflow", "Assess changing list_notes() from sorted to insertion order in app.py. Inspect callers beyond the proposed change and write and run a script that proves the actual CLI ordering effect. Do not change production app.py.", "Caller evidence and executable real CLI ordering regression; no production mutation."),
    "bro": ("text", "Previous assistant message: 'The append-only persistence substrate exhibits non-idempotent semantics upon duplicate delivery.' Restate it plainly for a nontechnical user. Write your restatement to result.txt.", "Plain restatement preserves duplicate delivery causing duplicate saved data, without jargon."),
    "correct": ("independent-workflow", "Inspect the local history: duplicate identifiers were fixed and accidentally reintroduced twice. Prevent this mistake structurally in app.py; prove the new check rejects each historical mistake, run the local check, update the rule/enforcement table. Keep commits local.", "Two historical instances, structural fix before docs, historical negative checks, current behavior check, rule table."),
    "create-verification-skill": ("independent-workflow", "Create a project-local verification skill for the note CLI. Discover the run command and user surface from README and app.py, seed its feature map, run every generated command and show real add/list output. Never write global skills.", "Generated verification skill and feature map with commands exercised against actual CLI."),
    "figure-it-out": ("independent-workflow", "Migrate local notes.json string titles to records with id and title. Define falsifiable done checks and workflow before changes, keep a TSV decision trail, then migrate and prove old titles survive and rerunning does not duplicate records. Local changes only.", "Workflow before edits, baseline, rerunnable migration, decision TSV, preservation and second-run proof."),
    "how": ("independent-workflow", "Explain exactly how python3 app.py add TITLE reaches persistent notes.json and list ordering. Use the simple-module native explainer path, cite actual lines and exercise add/list to confirm the explanation. Do not edit app.py.", "Native explainer tool evidence, cited code flow and real CLI output."),
    "in-your-own-words": ("text", "User goal: I keep losing notes when two processes write at once. I want locally stored notes retained without requiring a server. Restate the goal and problem in result.txt; do not implement a fix or add new requirements.", "Restatement includes concurrent overwrite, local storage and no server, without implementation."),
    "interrogate": ("independent-workflow", "Adversarially review the proposed app.py change that writes [] before loading notes. Use two native reviewers with the configured inherited model, synthesize disagreements and lead judgment. Do not apply the change. Never claim vendor diversity from one model.", "Two native reviewers, explicit intent, findings/disagreement map, lead judgment, no auto application."),
    "ketchup": ("text", "Supplied chat: user asked to preserve duplicate titles. Assistant removed a redundant sorting pass, ran CLI checks, found duplicate titles preserved, and has no outstanding user decision. Catch user up read-only. Write result.txt under 150 words. Do not invent an action item.", "Short factual catch-up without technical run identifiers or invented user action."),
    "maintain-verification-skill": ("independent-workflow", "The local .agents/skills/verify-notes/SKILL.md only covers list; app now has add. Maintain that existing skill and feature map with minimal edits. Exercise every updated command against real app.py; preserve list coverage.", "Minimal existing-skill update, preserved list plus add feature coverage and actual command outputs."),
    "make-bot-ui": ("independent-workflow", "Build and exercise a local note-list button using Make Bot UI's native webhook project. Prove the full chain: UI, server-held key, authenticated POST, durable event, native host CLI, result displayed. Preserve the original eight-second one-shot behavior. Do not expose the server key in chat, browser, logs or command arguments. Use only local loopback requests and no external publication. Test invalid authentication, duplicate delivery and restart recovery against real server state, not mocks.", "Working UI-to-server-to-durable-event-to-native-CLI result trace; actual auth rejection, dedup/restart proof, eight-second one-shot behavior, and no server key in client/chat/log artifacts."),
    "no-comments": ("independent-workflow", "Run no-comments on commented.py only. Invoke registered comment-sicko natively, validate its report and remove only narrating comments. Preserve the regex literal and externally constrained comment; exercise transform before/after. Record constraint offers without unapproved encodings.", "Named comment-sicko lifecycle, scoped report, accepted edits, unchanged runtime behavior and exception evidence."),
    "poteto-help": ("text", "Help question only: Which pstack skill should I use to explain why the note CLI was designed this way? Write the concise answer, at most one example prompt and the public source link to result.txt. Do not start the investigation.", "Routes to why, short usable prompt and source link; no task started."),
    "poteto-mode": ("independent-workflow", "Use poteto-mode to fix the obvious local add-then-list bug in app.py: titles must survive process restart. Select its actual relevant playbook/principles and run real CLI regression. Keep changes local, do not ship or open a PR.", "Actual playbook routing, loaded principles, reproduced defect, corrected real restart behavior and scoped verification."),
    "recall": ("independent-workflow", "Recall the supplied scoped-history.md and local git history for this project. Explain current note ordering decisions and next work; inspect source-control shared evidence and explicitly report unavailable tracker/chat/telemetry rather than inventing it. Read only this verified export.", "Project-scoped history evidence, current-state capsule, shared-record search and explicit unavailable-source gaps."),
    "reflect": ("independent-workflow", "Reflect on scoped-history.md for this project: three native reviewers should identify recurring corrections, synthesize and propose concrete edits to the existing verify-notes skill. Do not read other projects or mutate global skills; record any approval still required.", "Three native review results, synthesizer, scoped evidence and concrete existing-skill edits or explicit pending approvals."),
    "setup-pstack": ("independent-workflow", "Run setup-pstack for this isolated project preserving existing user instructions and inheritance. Preview and write only local host files. Then start fresh native sessions invoking poteto-agent and comment-sicko by registered names and prove each reads the local private marker. No global edits.", "Setup receipt and preserved user content, actual fresh named-agent invocations with observed private marker."),
    "sharpen": ("text", "Task: write a short operator instruction for listing notes. Sharpen the task internally, then write usable concrete instructions to result.txt and perform one outside check by running the documented command. Do not hand back a rewritten prompt.", "Usable documented CLI command and independently observed output, not a rewritten request."),
    "show-me-your-work": ("independent-workflow", "Keep a canonical TSV decision trail while you reproduce and fix list ordering to be deterministic. Use the shipped logging script, retain one row per actual decision with real evidence pointers, then audit rows against commands actually executed.", "Shipped logging command output, six-column TSV, real evidence pointers and transcript audit."),
    "swarm": ("independent-workflow", "Use swarm with exactly two native workers: one verifies add persistence, one verifies list sorting. Give each its own output file, wait for both terminal results, aggregate and release. Do not simulate delegation or let workers modify app.py.", "Two native worker IDs and terminal results, disjoint artifacts, aggregate verified against real CLI."),
    "tdd": ("behavior", "Use TDD to fix add-then-list losing the last character of each title. Write and run the smallest real CLI regression before production edits; prove it fails for truncated title, fix, then rerun. Save red and green command output.", "Regression red before fix and green after fix with exact CLI result, not a restated constant."),
    "teach": ("independent-workflow", "Teach why the local note CLI sorts titles and how it reads/writes them. Invoke how and scoped why as real dependencies, preserve confidence language, cite local history, and leave app.py untouched.", "Dependency native calls, readable combined account with citations, original confidence separation."),
    "technical-writing": ("text", "Rewrite draft.md into a short how-to for adding and listing a note. Use actual commands from README and run them. Keep one document mode, plain active sentences and no invented flags. Write result.txt.", "Executable correct add/list instructions and clean how-to prose; observed CLI output."),
    "typescript-best-practices": ("typed-behavior", "Refactor order.ts so open and completed notes cannot form invalid states and UserId cannot be confused with NoteId; external JSON must be parsed at the boundary. Add compile-negative checks and run the existing TypeScript compiler when available. Do not claim a typecheck if no compiler exists.", "Illegal states, swapped IDs and unhandled variants rejected; valid behavior compiles and runs, no unsafe casts."),
    "unslop": ("text", "Rewrite draft.md as result.txt preserving the concrete command and behavior. Remove AI vocabulary, filler and em dashes without inventing facts.", "Concrete command and meaning preserved, banned filler and em dash absent."),
    "why": ("independent-workflow", "Why are note titles sorted? Read local commits, blame and decision.md; use native source-control investigator and synthesizer. Discover evidence categories and record unavailable categories. Cite evidence and keep confidence distinct from inference. No remote writes.", "Native investigator and synthesizer, code/history anchor, seven-category coverage with justified gaps, cited confidence-separated result."),
}

PRINCIPLES = {
    "attack-the-premise": "Two retries and a larger return pool both failed because worker zero always owns all queued jobs. Write the shared premise, create and run a rerunnable per-worker census from jobs.json, then fix the role assignment and rerun the census; do not just add a third compensating pool.",
    "boundary-discipline": "Refactor boundary.py: validate external JSON exactly at entry, use a named typed domain value inside, and extract pure total() logic. Prove bad external data is rejected and valid data returns the exact total.",
    "build-the-lever": "Migrate five .old note files to .txt. Do the first manually, build a small rerunnable migration script, compare the first unit and then execute twice. Prove exact contents and no duplicate output.",
    "encode-lessons-in-structure": "Two scoped history entries corrected duplicate note IDs. Implement a structural/runtime check that rejects the repeated mistake; prove rejection and valid input. Do not just add another instruction paragraph.",
    "exhaust-the-design-space": "Choose a local note search interaction. Build at least two structurally different runnable prototypes and compare their actual behavior before choosing; save both prototypes and comparison. No production implementation yet.",
    "experience-first": "A note CLI proposal adds ten options but still loses typed input on validation errors. Implement a smaller user-facing improvement retaining input and showing a useful error. Exercise the actual failure/retry path and explain user impact.",
    "explain-the-number": "The fixture claims list is 2x faster after caching. Measure actual CLI work, capture run count/spread and a profiler/counter limiter, and rule out skipped output and error paths. Withhold speedup if the evidence does not support it.",
    "fix-root-causes": "Two callers truncate saved titles via save_title(). Reproduce both through actual imports, locate the common cause, fix it rather than adding caller guards, search for other instances and rerun both regressions.",
    "foundational-thinking": "Implement open/done note transitions. Define the core domain data structure before logic, inspect accesses and concurrency ownership, then implement transitions and test invalid and valid states without adding speculative abstractions.",
    "guard-the-context-window": "Inspect 12 independent generated log files for the one error marker. Bound file scope before reading; route bulk scans to native delegates when available and retain only summaries in the parent. Report unavailable delegation honestly, not simulated fan-out.",
    "laziness-protocol": "Simplify wrappers.py: three pass-through wrappers have one caller. Remove unnecessary layers and duplicated decisions with the smallest diff; prove exact outputs before/after instead of introducing a framework.",
    "make-operations-idempotent": "Implement the local text migration as an idempotent command. Execute twice and inject a crash between writing the first and second files; restart and prove the same complete state with no duplicates.",
    "migrate-callers-then-delete-legacy-apis": "Replace internal save_title() with save_note(). Inventory both callers, migrate all in one change, delete the old API, and run both callers. No external users exist, so do not leave a compatibility adapter.",
    "minimize-reader-load": "Refactor wrappers.py to collapse pass-through layers and remove hidden global title state. Keep outputs fixed, compare the number of layers and scope of mutable state with real source pointers.",
    "model-the-domain": "Replace completed:boolean plus optional completedAt in order.ts with a domain model that cannot represent completed-without-time. Demonstrate valid transitions and compiler-rejected impossible states, with no parallel booleans.",
    "never-block-on-the-human": "Fix the reversible title truncation bug in the local fixture and show actual before/after CLI output. Do the authorized local work without asking permission; do not make external writes.",
    "outcome-oriented-execution": "Migrate string notes to identified records in two explicit local units. State the permitted temporary break and verification boundary before edits; remove temporary adapters and prove final CLI behavior at the end.",
    "prove-it-works": "Fix the truncation bug and write a deterministic script that calls the actual CLI and compares its stored and printed title to the literal submitted title. Execute it; do not substitute a build or your own success statement.",
    "redesign-from-first-principles": "Add stable IDs to notes. Read every caller/doc/example first, design as though IDs existed from the start, update every reference, then prove add/list behavior. Do not bolt on a second incompatible storage path.",
    "separate-before-serializing-shared-state": "Two independent log workers currently overwrite one state.json. Determine whether sharing is necessary; give them independent owned state files and merge at reporting. Run them concurrently and prove both facts survive; no lock unless real sharing is required.",
    "sequence-verifiable-units": "Migrate five .old files to .txt. For each unit capture its old contents, change exactly that unit and verify exact output before the next. Save a chronological per-unit command log, and stop if a unit fails.",
    "subtract-before-you-add": "Before adding rename support, remove the unused legacy_format function and stale README reference. Prove existing behavior, then add the minimal rename command and run it. Keep evidence showing removal preceded addition.",
    "test-behavior-not-implementation": "Replace test_weak.py's assertion that a function exists with a test invoking the actual add/list CLI and asserting a literal exact title. Prove it fails when the imported implementation returns a wrong value, then run against the real fix.",
    "type-system-discipline": "Use order.ts to reject completed-without-time, swapped UserId/NoteId and unhandled variants. Parse external unknown once. Run positive and compile-negative checks with the actual compiler; report missing compiler rather than pretending types ran.",
}
for name, task in PRINCIPLES.items():
    TASKS["principle-" + name] = ("principle-application", task, "Concrete requested artifacts and actual behavior; independently review adherence to the principle, not only model self-report.")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_report(data):
    with tempfile.NamedTemporaryFile(mode="w", dir=REPORT.parent, prefix=".workflow-acceptance-", suffix=".tmp", delete=False) as out:
        temporary = Path(out.name)
        json.dump(data, out, indent=2)
        out.write("\n")
    try:
        os.replace(temporary, REPORT)
    finally:
        temporary.unlink(missing_ok=True)


def catalog():
    actual = {p.parent.name for p in SKILLS.glob("*/SKILL.md")} - {"pstack-support"}
    if actual != TASKS.keys():
        raise SystemExit(f"Scenario inventory differs: missing={actual - TASKS.keys()}, extra={TASKS.keys() - actual}")
    return {name: {"category": spec[0], "input": spec[1], "observable_contract": spec[2],
                   "source": str((SKILLS / name / "SKILL.md").relative_to(ROOT)),
                   "source_sha256": digest(SKILLS / name / "SKILL.md"),
                   "hosts": {host: {"status": "not_run", "acceptance": "not_verified"}
                             for host in ("codex", "claude-code")}}
            for name, spec in sorted(TASKS.items())}


def fixture(parent, host, name, commit, source):
    project = parent / host / name
    project.mkdir(parents=True)
    skill_root = project / (".agents/skills" if host == "codex" else ".claude/skills")
    shutil.copytree(source, skill_root)
    files = {
        "README.md": "# Notes\nRun `python3 app.py add TITLE` then `python3 app.py list`. Titles are sorted. Data lives in notes.json. No network required.\n",
        "app.py": "import json,sys\nfrom pathlib import Path\nP=Path(__file__).with_name('notes.json')\ndef list_notes():\n return sorted(json.loads(P.read_text()))\ndef save_title(title):\n data=json.loads(P.read_text());data.append(title[:-1]);P.write_text(json.dumps(data))\ndef caller_a(title):\n save_title(title)\ndef caller_b(title):\n save_title(title)\nif __name__=='__main__':\n if sys.argv[1]=='add':save_title(sys.argv[2])\n elif sys.argv[1]=='list':print('\\n'.join(list_notes()))\n",
        "notes.json": '["zebra", "apple"]\n',
        "id_notes.json": '[{"id":1,"title":"apple"},{"id":2,"title":"zebra"}]\n',
        "jobs.json": '[{"worker":0,"jobs":90},{"worker":1,"jobs":5},{"worker":2,"jobs":5}]\n',
        "boundary.py": "import json\ndef total(raw):\n data=json.loads(raw)\n if not isinstance(data,list):raise ValueError('list required')\n return sum(int(x) for x in data)\n",
        "wrappers.py": "TITLE='hello'\ndef inner():return TITLE.upper()\ndef middle():return inner()\ndef outer():return middle()\n",
        "commented.py": "import re\n# Return the uppercase title.\ndef transform(title):\n return title.upper()\n# RFC example pattern, copied verbatim from external fixture.\nPATTERN=re.compile(r'#\\w+')\n",
        "draft.md": "In order to utilize the pivotal note substrate, run `python3 app.py list`. Additionally, it is important to note that this command showcases all notes—ensuring enhanced visibility.\n",
        "decision.md": "Titles sort alphabetically so repeated list calls return the same order. Original decision is recorded in the fixture git history.\n",
        "scoped-history.md": f"Project: {project}\nSession 1: User corrected duplicate note IDs and asked for short plain replies and actual CLI proof.\nSession 2: User again corrected duplicate note IDs and asked for short plain replies and actual CLI proof.\nNo other project history is authorized.\n",
        "order.ts": "export type Note={completed:boolean;completedAt?:Date;userId:string;id:string};\nexport function label(n:Note){return n.completed ? n.completedAt!.toISOString() : 'open'}\n",
        "test_weak.py": "from app import save_title\ndef test_save():\n assert callable(save_title)\n",
        "empty-mcp.json": '{"mcpServers":{}}\n',
    }
    if name == "principle-subtract-before-you-add":
        files["app.py"] += "\ndef legacy_format(title):\n return 'legacy:' + title\n"
        files["README.md"] += "\nLegacy formatter: `legacy_format` (unused, retained from an earlier draft).\n"
    for filename, content in files.items():
        (project / filename).write_text(content)
    for i in range(5):
        (project / f"note-{i}.old").write_text(f"title-{i}\n")
    for i in range(12):
        (project / f"log-{i}.txt").write_text(("normal event\n" * 50) + ("ERROR acceptance-7319\n" if i == 7 else ""))
    verify = skill_root / "verify-notes"
    verify.mkdir()
    (verify / "SKILL.md").write_text("---\nname: verify-notes\ndescription: Verify the local note CLI.\n---\nRun `python3 app.py list` and assert alphabetical order.\n")
    (verify / "feature-map.md").write_text("# Features\n- list: python3 app.py list\n")
    # A real local history gives rationale and recurring-mistake workflows something scoped to inspect.
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    history = (("Record alphabetical list contract", False),
               ("Accidentally accept duplicate note IDs", True),
               ("Fix duplicate note IDs first time", False),
               ("Reintroduce duplicate note IDs", True),
               ("Fix duplicate note IDs second time", False))
    for message, duplicate in history:
        (project / "id_notes.json").write_text(json.dumps([
            {"id": 1, "title": "apple"}, {"id": 1 if duplicate else 2, "title": "zebra"}]))
        with (project / "decision.md").open("a") as out:
            out.write(message + "\n")
        subprocess.run(["git", "-C", str(project), "add", "."], check=True)
        subprocess.run(["git", "-C", str(project), "-c", "user.name=pstack acceptance", "-c", "user.email=acceptance@invalid", "commit", "-qm", message], check=True)
    instruction = project / ("AGENTS.md" if host == "codex" else "CLAUDE.md")
    instruction.write_text("User instruction preserved: only this disposable project may be changed. No external writes or messages.\n")
    support = skill_root / "pstack-support/scripts/setup.py"
    setup = subprocess.run([sys.executable, str(support), "--host", host, "--project", str(project), "--source-commit", commit, "--write"], capture_output=True, text=True)
    (project / "acceptance-setup.log").write_text(setup.stdout + setup.stderr)
    if setup.returncode:
        raise RuntimeError(f"Fixture setup failed: {setup.stdout[-1000:]} {setup.stderr[-1000:]}")
    return project, skill_root


def observable_checks(name, project, text):
    """Only establish narrow deterministic contracts. Other semantics require review."""
    result = project / "result.txt"
    checks = {"result_exists": result.is_file()} if TASKS[name][0] == "text" else {}
    if name == "unslop" and result.is_file():
        value = result.read_text()
        checks.update({"command_preserved": "python3 app.py list" in value,
                       "filler_removed": all(x not in value.lower() for x in ("in order to", "pivotal", "showcases", "additionally", "important to note", "—"))})
    if name in ("tdd", "principle-never-block-on-the-human", "principle-prove-it-works", "principle-fix-root-causes"):
        added = subprocess.run([sys.executable, "app.py", "add", "acceptance-title-7319"], cwd=project, capture_output=True, text=True)
        listed = subprocess.run([sys.executable, "app.py", "list"], cwd=project, capture_output=True, text=True)
        checks.update({"real_add_exit_zero": added.returncode == 0,
                       "real_list_exact_title": "acceptance-title-7319" in listed.stdout.splitlines(),
                       "stored_exact_title": "acceptance-title-7319" in json.loads((project / "notes.json").read_text())})
        (project / "acceptance-independent-cli.json").write_text(json.dumps({"add": added.stdout, "add_stderr": added.stderr, "list": listed.stdout, "list_stderr": listed.stderr}, indent=2))
    # Passing these checks does not establish the full workflow (for example TDD's red-first order).
    return checks


def run_process(command, project, output, error, prompt=None, timeout=480, env=None):
    """Own one process group so a timeout also stops its native delegates and tools."""
    process = subprocess.Popen(command, stdin=subprocess.PIPE if prompt is not None else subprocess.DEVNULL,
                               text=True, cwd=project, env=env, stdout=output, stderr=error, start_new_session=True)
    try:
        process.communicate(input=prompt, timeout=timeout)
        return process.returncode, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            pass
        # The leader can exit before a child that ignores TERM. Kill the owned
        # group even when communicate has returned, then reap the leader.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        return process.returncode, True


def run_one(host, name, parent, commit, source):
    started = time.time()
    try:
        project, skill_root = fixture(parent, host, name, commit, source)
    except Exception as error:
        return name, host, {"status": "fixture_failed", "acceptance": "not_verified", "error": str(error)}
    skill = skill_root / name / "SKILL.md"
    installed_skill_sha256 = digest(skill)
    installed_manifest_sha256 = digest(skill_root / "pstack-support/manifest.json")
    prefix = "$" + name if host == "codex" else "/" + name
    prompt = (f"Invoke {prefix} explicitly from {skill}. Read its full instructions and actual dependencies; this is a live behavioral acceptance run, not a summary or static check.\n"
              f"Task: {TASKS[name][1]}\n"
              "Work only inside the current disposable project. You may write local artifacts and run local commands. No global changes, network writes, remote PRs, messages, tasks, schedulers or infrastructure. Do not read unrelated session history. "
              "The scoped-history.md export is the only authorized prior conversation. Do not use another host's tools or simulate delegation. "
              "Do not skip a required phase to claim success; report actual capability gaps. Local commits are permitted if the skill requires them. "
              "Keep concrete artifacts, command evidence and native delegate results; the acceptance runner will independently inspect them. "
              "The scenario does not authorize external publication even when an original workflow requests it.\n")
    (project / "acceptance-prompt.txt").write_text(prompt)
    temporary_directory = project / ".pstack/acceptance-tmp"
    temporary_directory.mkdir(parents=True, exist_ok=True)
    host_env = {**os.environ, "NODE_OPTIONS": "", "CLAUDECODE": "", "TMPDIR": str(temporary_directory)}
    execution_environment = {"global_configuration_changed": False, "temporary_directory": str(temporary_directory)}
    if host == "codex":
        # Match native_agents.py's verified trust fixture. Ignoring this isolated
        # config would suppress project role discovery and invalidate delegation tests.
        home = project.parent / (name + "-codex-home")
        home.mkdir()
        auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
        if auth.is_file():
            (home / "auth.json").symlink_to(auth.resolve())
        (home / "config.toml").write_text(f"[projects.{json.dumps(str(project))}]\ntrust_level = \"trusted\"\n")
        host_env["CODEX_HOME"] = str(home)
        execution_environment.update(codex_home=str(home), project_trust="trusted",
                                     auth_handling="Existing auth.json symlink only; contents not copied or logged.")
        command = ["codex", "exec", "--ignore-rules", "--json", "-s", "workspace-write", "-C", str(project), "-c", 'approval_policy="never"', "-c", 'features.multi_agent=true', "-"]
    else:
        command = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--no-session-persistence", "--setting-sources", "project,local", "--strict-mcp-config", "--mcp-config", str(project / "empty-mcp.json"), "--permission-mode", "dontAsk", "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash,Agent", "--disallowedTools", "WebFetch,WebSearch"]
    output = project / "acceptance-events.jsonl"
    error = project / "acceptance-stderr.log"
    with output.open("w") as out, error.open("w") as err:
        if host == "claude-code":
            command += ["--", prompt]
        code, timed_out = run_process(command, project, out, err, prompt if host == "codex" else None, env=host_env)
    text = output.read_text()
    events = []
    for line in text.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    terminal = any(event.get("type") == "turn.completed" for event in events) if host == "codex" else any(event.get("type") == "result" and not event.get("is_error") for event in events)
    successful_execution = code == 0 and terminal
    session_id = next((event.get("thread_id") for event in events if event.get("type") == "thread.started"), None) if host == "codex" else next((event.get("session_id") for event in events if event.get("subtype") == "init"), None)
    native_delegation = [event["item"] for event in events if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "collab_tool_call"] if host == "codex" else [{key: event.get(key) for key in ("subtype", "task_id", "subagent_type", "status", "run_id")} for event in events if event.get("subtype") in ("task_started", "task_notification")]
    try:
        checks = observable_checks(name, project, text)
    except Exception as failure:
        checks = {"independent_check_failed": str(failure)}
    return name, host, {"status": "timed_out" if timed_out else "executed" if successful_execution else "cli_failed",
                        "acceptance": "needs_independent_review" if successful_execution else "not_verified",
                        "exit_code": code, "duration_seconds": round(time.time() - started, 2),
                        "installed_skill_sha256": installed_skill_sha256,
                        "installed_manifest_sha256": installed_manifest_sha256,
                        "installed_skill_unchanged": digest(skill) == installed_skill_sha256,
                        "session_id": session_id,
                        "native_delegation": native_delegation,
                        "execution_environment": execution_environment,
                        "fixture": str(project), "command": command,
                        "events": str(output), "events_sha256": digest(output), "stderr": str(error),
                        "observable_checks": checks,
                        "scope": "scenario only; not every playbook or external integration",
                        "artifacts": [str(p.relative_to(project)) for p in project.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git", ".agents", ".claude", ".codex"))],
                        "artifact_sha256": {str(p.relative_to(project)): digest(p) for p in project.rglob("*") if p.is_file() and not p.is_symlink() and not any(x in p.parts for x in (".git", ".agents", ".claude", ".codex"))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", choices=("codex", "claude-code", "both"), help="Actually invoke the logged-in host; omit to build the scenario inventory only")
    parser.add_argument("--skills", nargs="+", help="Explicit entry directories; omit to run all original 54")
    args = parser.parse_args()
    data = {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "meaning": "Execution is not acceptance. Only independently inspected actual artifacts can establish complete workflow behavior.",
            "scenario_count": 54, "entries": catalog()}
    if REPORT.exists():
        prior = json.loads(REPORT.read_text())
        data["previous_results"] = prior.get("previous_results", [])
        if "runner_timeout_regression" in prior:
            data["runner_timeout_regression"] = prior["runner_timeout_regression"]
        for name, entry in data["entries"].items():
            old = prior.get("entries", {}).get(name, {})
            if old.get("source_sha256") == entry["source_sha256"]:
                entry["hosts"] = old.get("hosts", entry["hosts"])
            elif old:
                data["previous_results"].append({"skill": name, "source_commit": prior.get("source_commit"),
                                                 "source_sha256": old.get("source_sha256"), "hosts": old.get("hosts")})
    names = args.skills or sorted(TASKS)
    if set(names) - TASKS.keys():
        parser.error("Unknown skills: " + ", ".join(sorted(set(names) - TASKS.keys())))
    if args.run:
        parent = Path(tempfile.mkdtemp(prefix="pstack-workflow-acceptance-")).resolve()
        source = parent / "skill-source"
        shutil.copytree(SKILLS, source)
        data["last_run_root"] = str(parent)
        hosts = ("codex", "claude-code") if args.run == "both" else (args.run,)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(run_one, host, name, parent, data["source_commit"], source) for host in hosts for name in names]
            for job in concurrent.futures.as_completed(jobs):
                name, host, result = job.result()
                old = data["entries"][name]["hosts"][host]
                if old["status"] != "not_run":
                    data.setdefault("previous_results", []).append({"skill": name, "host": host,
                        "source_commit": data["source_commit"], "source_sha256": data["entries"][name]["source_sha256"], "result": old})
                data["entries"][name]["hosts"][host] = result
                save_report(data)
                print(f"{host} {name}: {result['status']} / {result['acceptance']}", flush=True)
    save_report(data)
    print(f"{len(data['entries'])} original entry scenarios recorded in {REPORT}")


if __name__ == "__main__":
    main()
