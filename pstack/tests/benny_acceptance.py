#!/usr/bin/env python3
"""Run local Benny host checks. --output is optional; --artifacts is optional retention location.
Neither option changes the test. External workflows remain explicitly untested.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parents[1]
PACK = SOURCE / 'skills/pstack-support/automations/benny'
OPERATIONAL = [f'.pstack/automations/benny/skills/{name}/INSTRUCTIONS.md' for name in ('triage-issue-reports', 'reproduce-and-fix-issues')]
DEPENDENCIES = ('how', 'why', 'tdd', 'unslop', 'principle-separate-before-serializing-shared-state', 'principle-minimize-reader-load', 'principle-guard-the-context-window', 'principle-sequence-verifiable-units', 'principle-fix-root-causes', 'principle-prove-it-works')
spec = importlib.util.spec_from_file_location('workflow_acceptance', SOURCE / 'tests/workflow_acceptance.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(project, *args):
    return subprocess.check_output(['git', '-C', str(project), *args], text=True).strip()


def fixture(parent, host):
    project = parent / host
    project.mkdir()
    shutil.copytree(PACK, project / '.pstack/automations/benny')
    skill_root = project / ('.agents/skills' if host == 'codex' else '.claude/skills')
    for name in DEPENDENCIES:
        shutil.copytree(SOURCE / 'skills' / name, skill_root / name)
    (project / 'empty-mcp.json').write_text('{"mcpServers": {}}')
    cases = [
        {'id': 'wrong-result', 'report': 'The documented sum of 2 and 3 is 5. The app returns 9.'},
        {'id': 'slow', 'report': 'Opening a 10-row table takes 30 seconds. Baseline is 100 milliseconds.'},
        {'id': 'feature', 'report': 'The documented app intentionally supports CSV only. Please add PDF export.'},
        {'id': 'owned', 'report': 'The save button crashes.', 'replies': [{'user': 'UHUMAN', 'text': 'I am implementing the save crash fix now; please do not patch it.'}]},
        {'id': 'existing', 'report': 'Saving an empty note crashed before the local fix.', 'merged_commit': None},
    ]
    (project / 'app.py').write_text('def save(note):\n    return note[0]\n')
    git(project, 'init', '-q')
    git(project, 'add', '.')
    git(project, '-c', 'user.name=Local fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Local anonymous baseline')
    baseline = git(project, 'rev-parse', 'HEAD')
    (project / 'app.py').write_text('def save(note):\n    return note[0] if note else ""\n')
    git(project, 'add', 'app.py')
    git(project, '-c', 'user.name=Local fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Fix saving empty note')
    cases[-1].update(merged_commit=git(project, 'rev-parse', 'HEAD'), baseline_commit=baseline)
    (project / 'synthetic-threads.json').write_text(json.dumps({'source_channel_id': 'CTEST', 'root_thread_ts': '123.456', 'triage_identity': 'UTRIAGE', 'cases': cases}, indent=2))
    (project / 'existing-fix.patch').write_text(git(project, 'show', '--format=fuller', 'HEAD'))
    git(project, 'add', '.')
    git(project, '-c', 'user.name=Local fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Add synthetic thread evidence')
    return project


def marker_checks(parent):
    spec = importlib.util.spec_from_file_location('benny_journal', PACK / 'journal.py')
    journal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(journal)
    trusted = {'user': 'UTRIAGE', 'channel': 'CTEST', 'ts': '123.500', 'thread_ts': '123.456', 'text': '[benny:bug]'}
    assert journal.trusted_verdict(trusted, 'CTEST', '123.456', 'UTRIAGE') == '[benny:bug]'
    rejected = ({'user': 'UOTHER'}, {'channel': 'COTHER'}, {'thread_ts': '123.999'}, {'ts': '123.456'}, {'text': '[benny:bug] [benny:other]'})
    for change in rejected:
        assert journal.trusted_verdict({**trusted, **change}, 'CTEST', '123.456', 'UTRIAGE') is None
    directory = parent / 'journal-restart'
    directory.mkdir()
    first = journal.Journal(directory)
    assert first.claim('CTEST', '123.456', 'triage-reply')['action'] == 'execute-once'
    first.close()
    second = journal.Journal(directory)
    assert second.claim('CTEST', '123.456', 'triage-reply')['action'] == 'reconcile'
    second.close()
    return {'trusted_marker_accepted': True, 'untrusted_variants_rejected': len(rejected), 'pending_intent_requires_reconciliation_after_restart': True, 'external_objects_created': 0}


def run(host, parent):
    project = fixture(parent, host)
    committed = {path: sha(project / path) for path in OPERATIONAL}
    committed_matches = {path: hashlib.sha256(subprocess.check_output(['git', '-C', str(project), 'show', 'HEAD:' + path])).hexdigest() == value for path, value in committed.items()}
    commit = git(project, 'rev-parse', 'HEAD')
    prompt = (
        'Local, read-only Benny behavioral check. No live automation is enabled. No Slack/Feishu/tracker/PR/scheduler access is configured or authorized. '
        'Do not call any external tools, create tasks, post, edit, run an app or claim a reproduction. Read these actual committed files in full: '
        + ', '.join(OPERATIONAL) + '. Also read .pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md, synthetic-threads.json, existing-fix.patch and app.py. '
        'Use the operational rules to classify the first three reports, determine whether fix ownership stops the fourth, and whether the fifth must verify an existing fix instead of authoring. '
        'This is local decision inspection only: missing connectors and UI prevent enabling or completing any live run. '
        'Return only JSON with keys classifications (map case id to Bug, Performance or Feature request), owned_stop (boolean), existing_verify_only (boolean), authored_fix (false), live_repro_verified (false), automation_enabled (false). '
        'The field names are this test output contract, not product configuration. Do not paraphrase unread operational instructions. Use only local read tools.'
    )
    (project / 'acceptance-prompt.txt').write_text(prompt)
    env = dict(os.environ, NODE_OPTIONS='', CLAUDECODE='')
    if host == 'codex':
        home = parent / 'isolated-codex-home'
        home.mkdir()
        auth = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'auth.json'
        if auth.exists():
            (home / 'auth.json').symlink_to(auth.resolve())
        (home / 'config.toml').write_text('')
        env['CODEX_HOME'] = str(home)
        command = ['codex', 'exec', '--ignore-rules', '--json', '-s', 'read-only', '-C', str(project), '-c', 'approval_policy="never"', '-c', 'features.apps=false', '-c', 'features.plugins=false', '-']
    else:
        command = ['claude', '-p', '--output-format', 'stream-json', '--verbose', '--no-session-persistence', '--setting-sources', 'project,local', '--strict-mcp-config', '--mcp-config', str(project / 'empty-mcp.json'), '--permission-mode', 'dontAsk', '--tools', 'Read,Glob,Grep', '--allowedTools', 'Read,Glob,Grep', '--', prompt]
    events_path, error_path = project / 'events.jsonl', project / 'stderr.log'
    with events_path.open('w') as out, error_path.open('w') as err:
        code, timeout = workflow.run_process(command, project, out, err, prompt if host == 'codex' else None, timeout=360, env=env)
    events = []
    for line in events_path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    if host == 'codex':
        session = next((e.get('thread_id') for e in events if e.get('type') == 'thread.started'), None)
        tools = [e['item'] for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'command_execution']
        responses = [e['item'].get('text', '') for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
        read_evidence = {path: any(path in t.get('command', '') and (project / path).read_text().strip() in t.get('aggregated_output', '') for t in tools) for path in OPERATIONAL}
        terminal = any(e.get('type') == 'turn.completed' for e in events)
    else:
        session = next((e.get('session_id') for e in events if e.get('subtype') == 'init'), None)
        tools = [b for e in events for b in e.get('message', {}).get('content', []) if isinstance(b, dict) and b.get('type') == 'tool_use']
        responses = [e.get('result', '') for e in events if e.get('type') == 'result']
        results = {b.get('tool_use_id'): b for e in events for b in e.get('message', {}).get('content', []) if isinstance(b, dict) and b.get('type') == 'tool_result'}
        read_evidence = {path: any(t.get('name') == 'Read' and t.get('input', {}).get('file_path', '').endswith(path) and t.get('id') in results and not results[t['id']].get('is_error') for t in tools) for path in OPERATIONAL}
        terminal = any(e.get('type') == 'result' and not e.get('is_error') for e in events)
    decision = None
    if responses:
        text = responses[-1].strip()
        try:
            decision = json.loads(text.removeprefix('```json').removesuffix('```').strip())
        except json.JSONDecodeError:
            pass
    expected = {'classifications': {'wrong-result': 'Bug', 'slow': 'Performance', 'feature': 'Feature request'}, 'owned_stop': True, 'existing_verify_only': True, 'authored_fix': False, 'live_repro_verified': False, 'automation_enabled': False}
    checks = {'committed_blobs_match': committed_matches, 'committed_operational_files_read': read_evidence, 'fixture_unchanged': all(sha(project / p) == digest for p, digest in committed.items()), 'synthetic_decision_matches': decision == expected}
    passed = code == 0 and terminal and not timeout and session and all(committed_matches.values()) and all(read_evidence.values()) and checks['fixture_unchanged'] and checks['synthetic_decision_matches']
    return {'status': 'local_checks_passed' if passed else 'not_verified', 'session_id': session, 'exit_code': code, 'timeout': timeout, 'fixture': str(project), 'fixture_commit': commit, 'operational_sha256': committed, 'checks': checks, 'observed_decision': decision, 'events_sha256': sha(events_path), 'artifacts_sha256': {p: sha(project / p) for p in ('synthetic-threads.json', 'existing-fix.patch', 'app.py', 'events.jsonl', 'acceptance-prompt.txt')}, 'host_tools': ['read-only sandbox shell; no MCP configured'] if host == 'codex' else ['Read', 'Glob', 'Grep']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=SOURCE / 'docs/benny-local-checks.json')
    parser.add_argument('--artifacts', type=Path)
    args = parser.parse_args()
    parent = args.artifacts or Path(tempfile.mkdtemp(prefix='pstack-benny-local-'))
    parent.mkdir(parents=True, exist_ok=True)
    report = {'scope': 'Local synthetic decisions and operational-file reads; not live automation acceptance', 'external_writes_authorized': False, 'source_pack_sha256': {str(p.relative_to(PACK)): sha(p) for p in PACK.rglob('*') if p.is_file() and '__pycache__' not in p.parts}, 'marker_and_journal': marker_checks(parent), 'hosts': {}, 'not_tested': ['fresh-session invocation of every shared project skill dependency', 'real automatic trigger', 'Slack thread reply and read-back', 'Feishu sends/replies/reactions (forbidden)', 'tracker search/write/compensation', 'real UI baseline and patched builds twice', 'screenshots/video and attachment inspection', 'worker credential isolation in a live connector session', 'remote draft PR creation', 'scheduler activation']}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {host: pool.submit(run, host, parent) for host in ('codex', 'claude-code')}
        for host, future in futures.items():
            try:
                report['hosts'][host] = future.result()
            except Exception as error:
                report['hosts'][host] = {'status': 'not_verified', 'error': str(error)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(args.output), 'artifact_root': str(parent), 'hosts': {h: r['status'] for h, r in report['hosts'].items()}}))


if __name__ == '__main__':
    main()
