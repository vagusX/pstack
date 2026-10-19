import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'skills/pstack-support/automations/benny/feishu_readonly.py'
spec = importlib.util.spec_from_file_location('feishu_readonly', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def message(mid='om_root', **changes):
    return dict(message_id=mid, chat_id='oc_test', thread_id='omt_topic',
                sender={'id': 'ou_anonymous', 'id_type': 'open_id', 'sender_type': 'user'},
                content='Anonymous test report', msg_type='text', create_time='1000',
                deleted=False, updated=False, **changes)


class FeishuReadonlyTests(unittest.TestCase):
    def test_native_coordinates_replies_and_restart_edit(self):
        records = module.normalize('oc_test', [message()], {'omt_topic': [message(), message('om_reply')]})
        self.assertEqual(len(records), 2)
        self.assertEqual(records[1]['root_message_id'], 'om_root')
        self.assertEqual(records[1]['thread_id'], 'omt_topic')
        self.assertNotIn('thread_ts', records[1])
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / 'state.json'
            self.assertEqual(len(module.ingest(state, records)), 2)
            self.assertEqual(module.ingest(state, records), [])
            changed = dict(records[1], content='Edited anonymous report', update_time='2000')
            self.assertEqual(module.ingest(state, [changed])[0]['change'], 'updated')
            self.assertEqual(module.ingest(state, [changed]), [])
            self.assertEqual(len(json.loads(state.read_text())['reports']), 3)

    def test_wrong_chat_thread_and_conflicting_roots_fail(self):
        root = message()
        with self.assertRaises(ValueError):
            module.normalize('oc_other', [root])
        with self.assertRaises(ValueError):
            module.normalize('oc_test', [root], {'omt_topic': [dict(message('om_reply'), thread_id='omt_other')]})
        with self.assertRaises(ValueError):
            module.normalize('oc_test', [root, message('om_other')], {'omt_topic': [message('om_reply')]})

    def test_only_fixed_reads_and_cache_success(self):
        envelope = {'ok': True, 'data': {'messages': [message()], 'has_more': False}}
        with tempfile.TemporaryDirectory() as folder, patch.object(module.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps(envelope)
            reader = module.Reader(folder)
            self.assertEqual(len(reader.messages('chat', 'oc_test')), 1)
            reader.messages('chat', 'oc_test')
            self.assertEqual(run.call_count, 1)
            argv = run.call_args.args[0]
            self.assertEqual(argv[:3], ['lark-cli', 'im', '+chat-messages-list'])
            self.assertIn('--no-reactions', argv)
            self.assertNotIn('--download-resources', argv)
            with self.assertRaises(ValueError):
                reader.messages('+messages-send', 'oc_test')
            with self.assertRaises(ValueError):
                reader.messages('chat', '--help')
            self.assertEqual(run.call_count, 1)

    def test_failed_read_not_cached_and_bad_pagination_rejected(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(module.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({'ok': False})
            with self.assertRaises(ValueError):
                module.Reader(folder).messages('chat', 'oc_test')
            self.assertEqual(list(Path(folder).iterdir()), [])
            run.return_value.stdout = json.dumps({'ok': True, 'data': {'messages': [], 'has_more': True}})
            with self.assertRaises(ValueError):
                module.Reader(folder).messages('chat', 'oc_test')

    def test_pagination_and_thread_reads_use_only_returned_coordinates(self):
        pages = [
            {'ok': True, 'data': {'messages': [message()], 'has_more': True, 'page_token': 'next'}},
            {'ok': True, 'data': {'messages': [], 'has_more': False}},
            {'ok': True, 'data': {'messages': [message('om_reply')], 'has_more': False}},
        ]
        with tempfile.TemporaryDirectory() as folder, patch.object(module.subprocess, 'run') as run:
            from subprocess import CompletedProcess
            run.side_effect = [CompletedProcess([], 0, json.dumps(page)) for page in pages]
            records = module.Reader(folder, start='2026-01-01T00:00:00+08:00').collect('oc_test')
            self.assertEqual(len(records), 2)
            calls = [call.args[0] for call in run.call_args_list]
            self.assertIn('--page-token=next', calls[1])
            for call in calls[:2]:
                self.assertIn('--start=2026-01-01T00:00:00+08:00', call)
            self.assertFalse(any(arg.startswith('--start') for arg in calls[2]))
            self.assertEqual(calls[2][:5], ['lark-cli', 'im', '+threads-messages-list', '--thread', 'omt_topic'])

    def test_enrichment_does_not_emit_an_edit(self):
        records = module.normalize('oc_test', [message()])
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / 'state.json'
            module.ingest(state, records)
            self.assertEqual(module.ingest(state, [dict(records[0], sender={'name': 'Anonymous'})]), [])


if __name__ == '__main__':
    unittest.main()
