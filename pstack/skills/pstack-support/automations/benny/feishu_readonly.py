#!/usr/bin/env python3
"""Collect Feishu messages into a local pending-classification inbox. No writes to Feishu."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    os.replace(temporary, path)


def identifier(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(prefix + r'[A-Za-z0-9_]+', value):
        raise ValueError('Invalid Feishu identifier')
    return value


def response_data(envelope):
    if envelope.get('ok') is not True or not isinstance(envelope.get('data'), dict):
        raise ValueError('Feishu read failed or returned an invalid envelope')
    data = envelope['data']
    if not isinstance(data.get('messages'), list) or not isinstance(data.get('has_more', False), bool):
        raise ValueError('Invalid Feishu message page')
    return data


class Reader:
    """Fixed read operations only; callers cannot supply a command or extra flags."""
    def __init__(self, cache, start=None):
        self.cache = Path(cache)
        self.start = start

    def _page(self, operation, value, token=None):
        if operation == 'chat':
            args = ['+chat-messages-list', '--chat-id', identifier(value, 'oc_')]
            if self.start is not None:
                args += ['--start=' + self.start]
        elif operation == 'thread':
            args = ['+threads-messages-list', '--thread', identifier(value, '(?:om_|omt_)')]
        else:
            raise ValueError('Unsupported read operation')
        args += ['--as', 'user', '--format', 'json', '--no-reactions', '--order', 'asc', '--page-size', '50']
        if token is not None:
            if not isinstance(token, str) or not token:
                raise ValueError('Invalid pagination token')
            args += ['--page-token=' + token]
        key = hashlib.sha256(json.dumps(args).encode()).hexdigest()
        cached = self.cache / (key + '.json')
        if cached.exists():
            result = json.loads(cached.read_text())
        else:
            env = dict(os.environ, LARKSUITE_CLI_NO_UPDATE_NOTIFIER='1', LARKSUITE_CLI_NO_SKILLS_NOTIFIER='1')
            completed = subprocess.run(['lark-cli', 'im', *args], capture_output=True, text=True, env=env, timeout=120)
            if completed.returncode:
                raise RuntimeError('Feishu read failed; checkpoint unchanged')
            result = json.loads(completed.stdout)
            response_data(result)
            atomic_json(cached, result)
        return response_data(result)

    def messages(self, operation, value):
        items, token, seen = [], None, set()
        while True:
            data = self._page(operation, value, token)
            items.extend(data['messages'])
            if not data.get('has_more', False):
                return items
            token = data.get('page_token')
            if not token or token in seen:
                raise ValueError('Incomplete or repeated pagination cursor')
            seen.add(token)

    def collect(self, chat_id):
        roots = self.messages('chat', chat_id)
        threads = sorted({m['thread_id'] for m in roots if m.get('thread_id')})
        with ThreadPoolExecutor(max_workers=10) as pool:
            replies = dict(zip(threads, pool.map(lambda thread: self.messages('thread', thread), threads)))
        return normalize(chat_id, roots, replies)


def normalize(chat_id, roots, replies=None):
    """Keep official fields; root_message_id comes from the chat-list root message_id."""
    identifier(chat_id, 'oc_')
    result = {}
    for root in roots:
        root_id = identifier(root.get('message_id'), 'om_')
        thread_id = root.get('thread_id')
        if thread_id:
            identifier(thread_id, '(?:om_|omt_)')
        messages = [root, *root.get('thread_replies', []), *(replies or {}).get(thread_id, [])]
        for message in messages:
            message_id = identifier(message.get('message_id'), 'om_')
            if message.get('chat_id', chat_id) != chat_id:
                raise ValueError('Message belongs to a different chat')
            if message.get('thread_id') and message['thread_id'] != thread_id:
                raise ValueError('Message belongs to a different thread')
            if not isinstance(message.get('content'), str) or not isinstance(message.get('sender'), dict):
                raise ValueError('Missing message content or sender')
            record = {key: message[key] for key in ('message_id', 'msg_type', 'create_time', 'sender', 'content', 'deleted', 'updated', 'update_time') if key in message}
            record.update(chat_id=chat_id, root_message_id=root_id, thread_id=thread_id)
            if message_id in result and result[message_id] != record:
                raise ValueError('Conflicting message coordinates or versions in one scan')
            result[message_id] = record
    return list(result.values())


def ingest(state_path, records):
    """Persist fingerprints and the local inbox together; never lose a report on output failure."""
    state_path = Path(state_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(state_path) + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(state_path.read_text()) if state_path.exists() else {'version': 1, 'seen': {}, 'reports': []}
        if state.get('version') != 1 or not isinstance(state.get('seen'), dict) or not isinstance(state.get('reports'), list):
            raise ValueError('Invalid local checkpoint')
        emitted = []
        for record in records:
            key = record['chat_id'] + '/' + record['message_id']
            # Enrichment (e.g. sender display name or reactions) is not a message edit.
            revision = {field: record.get(field) for field in ('content', 'msg_type', 'deleted', 'update_time', 'root_message_id', 'thread_id')}
            digest = hashlib.sha256(json.dumps(revision, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            if state['seen'].get(key) == digest:
                continue
            report = {'change': 'updated' if key in state['seen'] else 'new', 'status': 'pending-classification', 'revision': digest, 'message': record}
            state['seen'][key] = digest
            state['reports'].append(report)
            emitted.append(report)
        atomic_json(state_path, state)
        return emitted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chat-id', required=True)
    parser.add_argument('--state', required=True, type=Path, help='Private local JSON checkpoint and pending inbox')
    parser.add_argument('--input', type=Path, help='Offline +chat-messages-list JSON envelope; no network calls')
    parser.add_argument('--start', help='Chat-list start time (ISO 8601 or date), passed unchanged to lark-cli')
    args = parser.parse_args()
    identifier(args.chat_id, 'oc_')
    if args.input:
        if args.start is not None:
            parser.error('--start applies to live reads only; an offline snapshot cannot be refiltered')
        data = response_data(json.loads(args.input.read_text()))
        if data.get('has_more'):
            raise ValueError('Offline input is incomplete; fetch all pages first')
        records = normalize(args.chat_id, data['messages'])
    else:
        # A new cache per live scan keeps edits/replies visible; snapshots remain local for replay.
        args.state.parent.mkdir(parents=True, exist_ok=True)
        cache = tempfile.mkdtemp(prefix='feishu-read-', dir=args.state.parent)
        records = Reader(cache, start=args.start).collect(args.chat_id)
    emitted = ingest(args.state, records)
    print(json.dumps({'new_reports': len(emitted), 'state': str(args.state)}))


if __name__ == '__main__':
    main()
