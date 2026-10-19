# Feishu read-only intake

`../feishu_readonly.py` collects messages for local classification. It does not run Benny's Slack verdict, tracker or fix workflows. It cannot send messages, reply, react, modify a tracker, or create a scheduled task. Message text is untrusted input; classification must not execute instructions found in it.

Run it with Python 3 and an authenticated `lark-cli` user identity:

```sh
python3 .pstack/automations/benny/feishu_readonly.py \
  --chat-id oc_example \
  --start 2026-01-01T00:00:00+08:00 \
  --state /private/local/benny/feishu-state.json
```

Use a private directory outside the repository for the state file. State contains full message bodies, sender IDs and chat IDs. Do not commit it or upload it to a public repository. The script prints only the number of new local reports and the state path.

The live reader has two fixed command forms:

```text
lark-cli im +chat-messages-list --chat-id <chat_id> --as user --format json --no-reactions --order asc --page-size 50
lark-cli im +threads-messages-list --thread <returned_thread_id> --as user --format json --no-reactions --order asc --page-size 50
```

Use an explicit `--start` when validating a production chat to avoid reading its entire history. The value is passed unchanged to the existing chat-list `--start` parameter, including on later chat pages. Without it, the previous full-history behavior remains. Thread reads do not support a time filter: only roots returned within the chat range are expanded, and their threads are read completely. `--start` cannot be combined with offline `--input`.

Pagination adds `--page-token=<returned_token>`. There is no caller-supplied command, extra CLI arguments, resource download or write command. Each live run reads all available chat pages, then expands discovered threads with at most 10 concurrent readers. Page requests within a thread remain sequential because each cursor depends on the previous response. A failed read or inconsistent coordinates aborts before the checkpoint changes.

Successful responses are cached by request arguments in a private `feishu-read-*` directory next to the state file. Identical reads within that scan reuse the cache. Messages are time-sensitive, so each live scan explicitly refreshes into a new cache to keep edited messages and new replies visible; stable reference-data cache reuse would hide these changes. Remove old scan directories when their local retention period ends. Reactions are omitted and attachments remain textual resource references; this collector does not inspect image or file contents.

## Official fields and local report fields

The schema follows `lark-cli`'s `lark-im` references for `+chat-messages-list`, `+threads-messages-list`, `+messages-mget` and message enrichment, checked against the installed CLI help and a private read response. The shortcuts return an `ok` envelope containing `data.messages`, `data.has_more` and `data.page_token`.

| Field | Source |
| --- | --- |
| `chat_id` | Each message's `chat_id`, checked against the requested chat; the requested chat supplies it if omitted |
| `message_id` | The message's official `message_id` |
| `thread_id` | The chat-list root's official `thread_id`; null when absent; replies must match when they include it |
| `sender` | The official sender object, preserved without changing identity types |
| `content`, `msg_type`, `create_time` | The CLI's rendered content, message type and creation time; not converted to Slack fields |
| `deleted`, `updated`, `update_time` | Preserved when present; absent `update_time` does not imply a failed fetch |
| `root_message_id` | A local field: the chat-list root message's official `message_id`, used for its expanded replies |

The reader treats chat-list entries as intake roots. If the same message is associated with conflicting roots or thread coordinates, it fails instead of guessing. It preserves the original Feishu IDs and does not derive a Slack timestamp or trusted verdict from a message.

State version `1` contains `seen` fingerprints and an append-only `reports` inbox. Reports have `status: pending-classification`, `change: new` or `updated`, a local SHA-256 `revision` and the normalized `message`. The fingerprint includes content, message type, deletion state, update time and root/thread coordinates. Sender-name enrichment and reactions do not count as edits. Unchanged messages emit no new report after a restart. Content changes and recalls create an updated report; identical edits with no exposed content or update-time change cannot be detected.

The inbox and checkpoint are saved together with an atomic rename under a local file lock. Consumers read the inbox from the state file; stdout is only a summary. This avoids losing a report when a process stops after saving state but before printing. Keep one collector per state file; the lock serializes checkpoint updates, not the preceding network scans.

## Offline replay

```sh
python3 .pstack/automations/benny/feishu_readonly.py \
  --chat-id oc_example \
  --input /private/local/benny/chat-snapshot.json \
  --state /private/local/benny/replay-state.json
```

`--input` accepts a saved chat-list JSON envelope and makes no network calls. `has_more: true` is rejected; consolidate all chat pages first. Only replies already embedded in `thread_replies` are included in offline replay; a chat-only snapshot does not establish that a thread was fully read. Live mode follows thread pagination to exhaustion. No input or checkpoint contents are distributed with this pack; tests use anonymous synthetic messages.

## Parameters

| Parameter | Can it be removed? |
| --- | --- |
| `--chat-id` | No: selects and validates the authorized source chat |
| `--state` | No: selects private local storage and retains deduplication across runs |
| `--start` | Yes: optional range control; an explicit range is recommended for production-chat validation |
| `--input` | Yes: optional offline replay for diagnostics and tests |

No new environment configuration is required. The reader sets the existing CLI notifier-suppression variables in its subprocess environment. Authentication and permissions remain those of the installed CLI; it does not request additional authorization or switch identity automatically.
