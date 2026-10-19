import importlib.util
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sqlite3
import select
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/make-bot-ui/scripts/webhook.py'
SPEC = importlib.util.spec_from_file_location('bot_webhook', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'routine.md').write_text('Only report the supplied action. No tools.')
        (self.root / 'sender.key').write_text('s' * 43)
        (self.root / 'sender.key').chmod(0o600)
        self.cli = self.root / 'fake-cli'
        self.cli.write_text('#!/usr/bin/env python3\nimport sys,json,time,pathlib\np=sys.stdin.read()\n'
                            'if "wait_for_release" in p:\n while not pathlib.Path("release").exists(): time.sleep(.01)\n'
                            'print(json.dumps({"prompt":p,"args":sys.argv[1:]}))\nsys.exit(3 if "force_failure" in p else 0)\n')
        self.cli.chmod(0o700)
        (self.root / 'config.json').write_text(json.dumps({'project': str(self.root), 'prompt': str(self.root / 'routine.md'),
                                                         'host': 'codex', 'executable': str(self.cli)}))
        self.runtime = MODULE.Runtime(self.root)
        self.ui, self.receiver = MODULE.servers(self.runtime, port=0, receiver_port=0)
        for server in (self.ui, self.receiver):
            threading.Thread(target=server.serve_forever, daemon=True).start()
        self.worker = threading.Thread(target=self.runtime.worker, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.runtime.stop(self.worker)
        for server in (self.ui, self.receiver):
            server.shutdown()
            server.server_close()
        self.tmp.cleanup()

    def hostile_cli(self):
        grandchild = ('import signal,time,pathlib,os; '
                      'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                      'pathlib.Path("grandchild.pid").write_text(str(os.getpid())); time.sleep(60)')
        self.cli.write_text('#!/usr/bin/env python3\nimport subprocess,sys,time,pathlib\n'
                            'sys.stdin.read()\n'
                            f'subprocess.Popen([sys.executable,"-c",{grandchild!r}],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                            'while not pathlib.Path("grandchild.pid").exists(): time.sleep(.01)\n'
                            'print("ready",flush=True)\ntime.sleep(60)\n')

    def test_stop_between_loop_check_and_condition_does_not_lose_notification(self):
        runtime = MODULE.Runtime(self.root)
        observed = threading.Event()
        release = threading.Event()
        is_set = runtime.stopping.is_set

        def pause_first_check():
            stopped = is_set()
            if not observed.is_set():
                observed.set()
                release.wait(2)
            return stopped

        with patch.object(runtime.stopping, 'is_set', pause_first_check):
            worker = threading.Thread(target=runtime.worker, daemon=True)
            worker.start()
            self.assertTrue(observed.wait(2))
            stopper = threading.Thread(target=runtime.stop, args=(worker,), daemon=True)
            stopper.start()
            self.assertTrue(runtime.stopping.wait(2))
            with runtime.condition:
                pass
            release.set()
            stopper.join(2)
            try:
                self.assertFalse(worker.is_alive())
                self.assertFalse(stopper.is_alive())
            finally:
                with runtime.condition:
                    runtime.condition.notify_all()
                worker.join(2)
                stopper.join(2)

    def wait_grandchild(self):
        path = self.root / 'grandchild.pid'
        for _ in range(500):
            if path.exists():
                return int(path.read_text())
            time.sleep(.01)
        self.fail('Grandchild did not become ready')

    def assert_process_stopped(self, pid):
        for _ in range(200):
            state = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True).stdout.strip()
            if not state or state.startswith('Z'):
                return
            time.sleep(.01)
        self.fail('Grandchild survived its dedicated process group cleanup')

    def test_timeout_kills_detached_stdio_grandchild_after_leader_exits(self):
        self.hostile_cli()
        with patch.object(MODULE, 'CLI_TIMEOUT', 5):
            _, accepted = self.post(self.ui.server_port, '/actions', b'{"action":"probe"}')
            pid = self.wait_grandchild()
            event = self.wait_event(accepted['event_id'])
        self.assertEqual(event['state'], 'failed')
        self.assertIn('exceeded', event['error'])
        self.assert_process_stopped(pid)

    def test_stop_kills_detached_stdio_grandchild_after_leader_exits(self):
        self.hostile_cli()
        self.post(self.ui.server_port, '/actions', b'{"action":"probe"}')
        pid = self.wait_grandchild()
        self.runtime.stop(self.worker)
        self.assertFalse(self.worker.is_alive())
        self.assert_process_stopped(pid)

    def post(self, port, path, data, headers=None):
        request = urllib.request.Request(f'http://127.0.0.1:{port}{path}', data=data,
                                         headers={'Content-Type': 'application/json', **(headers or {})}, method='POST')
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    def wait_event(self, event_id):
        for _ in range(300):
            event = self.runtime.status(event_id)
            if event and event['state'] in ('completed', 'failed'):
                return event
            time.sleep(.02)
        self.fail('CLI did not finish')

    def test_real_http_to_cli_and_no_browser_key(self):
        with urllib.request.urlopen(f'http://127.0.0.1:{self.ui.server_port}/') as response:
            self.assertNotIn(self.runtime.key, response.read().decode())
        status, result = self.post(self.ui.server_port, '/actions', b'{"action":"probe"}')
        self.assertEqual(status, 200)
        event = self.wait_event(result['event_id'])
        self.assertEqual(event['state'], 'completed')
        output = json.loads(json.loads(event['result'])['stdout'])
        self.assertIn('<webhook_event>', output['prompt'])
        self.assertIn('body_digest', output['prompt'])
        self.assertNotIn(self.runtime.key, json.dumps(event))
        self.assertIn('--sandbox', output['args'])

    def test_database_connections_close_after_commit_and_rollback(self):
        with self.runtime.db() as committed:
            committed.execute('INSERT INTO failed_posts VALUES (?,?,?)', ('committed', '{}', 'failure'))
        with self.assertRaises(sqlite3.ProgrammingError):
            committed.execute('SELECT 1')
        with self.assertRaisesRegex(RuntimeError, 'rollback'):
            with self.runtime.db() as rolled_back:
                rolled_back.execute('INSERT INTO failed_posts VALUES (?,?,?)', ('rolled_back', '{}', 'failure'))
                raise RuntimeError('rollback')
        with self.assertRaises(sqlite3.ProgrammingError):
            rolled_back.execute('SELECT 1')
        with self.runtime.db() as reopened:
            rows = reopened.execute('SELECT event_id FROM failed_posts').fetchall()
        self.assertEqual([row['event_id'] for row in rows], ['committed'])

    def test_cli_init_serve_and_http_execution_for_both_hosts(self):
        for host in ('codex', 'claude-code'):
            with self.subTest(host=host):
                directory = self.root / f'cli-{host}'
                initialized = subprocess.run(
                    [sys.executable, str(SCRIPT), 'init', '--directory', str(directory),
                     '--host', host, '--project', str(self.root), '--prompt', str(self.root / 'routine.md'),
                     '--executable', str(self.cli)], capture_output=True, text=True, timeout=10)
                self.assertEqual(initialized.returncode, 0, initialized.stderr)
                key_file = directory / 'sender.key'
                self.assertEqual(key_file.stat().st_mode & 0o777, 0o600)
                key = key_file.read_text()
                self.assertNotIn(key, initialized.stdout + initialized.stderr)
                process = subprocess.Popen(
                    [sys.executable, str(SCRIPT), 'serve', '--directory', str(directory),
                     '--port', '0', '--receiver-port', '0'], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True)
                try:
                    self.assertTrue(select.select([process.stdout], [], [], 10)[0], 'serve did not start')
                    line = process.stdout.readline()
                    self.assertTrue(line, 'serve exited before announcing its URLs')
                    endpoints = json.loads(line)
                    port = int(endpoints['ui'].split(':')[-1].rstrip('/'))
                    with urllib.request.urlopen(endpoints['ui']) as response:
                        self.assertNotIn(key, response.read().decode())
                    code, accepted = self.post(port, '/actions', b'{"action":"probe"}')
                    self.assertEqual(code, 200)
                    event = None
                    deadline = time.monotonic() + 10
                    while time.monotonic() < deadline:
                        with urllib.request.urlopen(endpoints['ui'].rstrip('/') + accepted['status_url']) as response:
                            event = json.load(response)
                        if event['state'] in ('completed', 'failed'):
                            break
                        time.sleep(.02)
                    self.assertEqual(event['state'], 'completed')
                    self.assertNotIn(key, json.dumps(event))
                    result = json.loads(event['result'])
                    self.assertEqual(result['exit_code'], 0)
                    self.assertIn('<webhook_event>', json.loads(result['stdout'])['prompt'])
                finally:
                    process.send_signal(signal.SIGINT)
                    try:
                        stdout, stderr = process.communicate(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        stdout, stderr = process.communicate()
                    self.assertNotIn(key, stdout + stderr)

    def test_auth_json_limit_and_same_origin(self):
        self.assertEqual(self.post(self.receiver.server_port, '/webhook', b'{}')[0], 401)
        self.assertEqual(self.post(self.ui.server_port, '/actions', b'[]')[0], 400)
        self.assertEqual(self.post(self.ui.server_port, '/actions', b' ' * 65537)[0], 400)
        self.assertEqual(self.post(self.ui.server_port, '/actions', b'{}', {'Origin': 'https://foreign.example'})[0], 403)
        evil = {'Host': f'rebinding.example:{self.ui.server_port}', 'Origin': f'http://rebinding.example:{self.ui.server_port}'}
        self.assertEqual(self.post(self.ui.server_port, '/actions', b'{}', evil)[0], 403)
        request = urllib.request.Request(f'http://127.0.0.1:{self.ui.server_port}/', headers={'Host': evil['Host']})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code, 403)
        self.runtime.public_origins = [f'http://chosen.tailnet.ts.net:{self.ui.server_port}']
        chosen = {'Host': f'chosen.tailnet.ts.net:{self.ui.server_port}', 'Origin': self.runtime.public_origins[0]}
        self.assertEqual(self.post(self.ui.server_port, '/actions', b'{"action":"probe"}', chosen)[0], 200)

    def test_concurrent_http_retries_claim_failed_event_once(self):
        import uuid
        event_id = str(uuid.uuid4())
        with self.runtime.db() as db:
            db.execute('INSERT INTO events VALUES (?,?,?,?,?,?,NULL,NULL)',
                       (event_id, '{"action":"wait_for_release"}', 'digest', '{}', 1, 'failed'))
        barrier = threading.Barrier(2)
        def retry():
            barrier.wait()
            return self.post(self.ui.server_port, '/retry', b'{}', {'X-Event-ID': event_id})[0]
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                calls = [executor.submit(retry) for _ in range(2)]
                self.assertEqual(sorted(call.result() for call in calls), [200, 409])
        finally:
            (self.root / 'release').touch()
        self.assertEqual(self.wait_event(event_id)['state'], 'completed')

    def test_dedupe_and_conflicting_event_body(self):
        import uuid
        event_id = str(uuid.uuid4())
        for _ in range(2):
            self.assertEqual(self.post(self.ui.server_port, '/actions', b'{"action":"probe"}', {'X-Event-ID': event_id})[0], 200)
        self.wait_event(event_id)
        self.assertFalse(self.runtime.accept(event_id, '{"different":true}', {}))
        with self.runtime.db() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0], 1)

    def test_one_forward_attempt_timeout_and_failure_body(self):
        class Broken:
            def open(self, request, timeout):
                self.timeout = timeout
                raise OSError('offline')
        broken = Broken()
        with patch.object(MODULE.urllib.request, 'build_opener', return_value=broken) as factory:
            self.assertFalse(self.runtime.forward('event', '{"action":"probe"}'))
            self.assertEqual(factory.call_count, 1)
            self.assertEqual(broken.timeout, 8)
        with self.runtime.db() as db:
            row = db.execute('SELECT body FROM failed_posts WHERE event_id="event"').fetchone()
            self.assertEqual(row['body'], '{"action":"probe"}')

    def test_nonzero_and_explicit_recovery(self):
        _, result = self.post(self.ui.server_port, '/actions', b'{"action":"force_failure"}')
        event = self.wait_event(result['event_id'])
        self.assertEqual(event['state'], 'failed')
        self.assertEqual(json.loads(event['result'])['exit_code'], 3)
        with self.runtime.db() as db:
            db.execute("UPDATE events SET state='running' WHERE event_id=?", (result['event_id'],))
        MODULE.Runtime(self.root)  # status/read must not reset a live worker
        self.assertEqual(self.runtime.status(result['event_id'])['state'], 'running')
        self.runtime.recover()
        self.assertEqual(self.runtime.status(result['event_id'])['state'], 'interrupted')

    def test_both_native_commands_and_private_key(self):
        self.assertIn('read-only', self.runtime.command())
        config_path = self.root / 'config.json'
        config = json.loads(config_path.read_text())
        config['sandbox_mode'] = 'workspace-write'
        config_path.write_text(json.dumps(config))
        self.assertIn('workspace-write', MODULE.Runtime(self.root).command())
        for invalid in ('danger-full-access', 'invented', ['workspace-write']):
            config['sandbox_mode'] = invalid
            config_path.write_text(json.dumps(config))
            with self.assertRaises(ValueError):
                MODULE.Runtime(self.root)
        config['sandbox_mode'] = 'read-only'
        config_path.write_text(json.dumps(config))
        self.runtime.config['host'] = 'claude-code'
        self.assertEqual(self.runtime.command()[1:], ['-p', '--output-format', 'json', '--permission-mode', 'dontAsk'])
        (self.root / 'sender.key').chmod(0o644)
        with self.assertRaises(ValueError):
            MODULE.Runtime(self.root)


if __name__ == '__main__':
    unittest.main()
