#!/usr/bin/env python3
"""Durable external-write intents; a pending intent requires external reconciliation."""
import argparse
import json
from pathlib import Path
import re
import sqlite3

EFFECTS = ("tracker", "triage-reply", "repro-reply", "draft-pr")
MARKERS = ("[benny:bug]", "[benny:performance]", "[benny:other]")


def coordinates(channel, thread):
    if not re.fullmatch(r"[CG][A-Z0-9]+", channel) or not re.fullmatch(r"[0-9]+\.[0-9]+", thread):
        raise ValueError("A Slack channel ID and original root thread timestamp are required")


def trusted_verdict(message, channel, thread, identity):
    coordinates(channel, thread)
    if not identity or message.get("user") != identity or message.get("channel") != channel:
        return None
    if message.get("thread_ts") != thread or message.get("ts") == thread:
        return None
    found = [marker for marker in MARKERS for _ in range(message.get("text", "").count(marker))]
    return found[0] if len(found) == 1 else None


class Journal:
    def __init__(self, project):
        project = Path(project).resolve()
        directory = project / ".pstack"
        if directory.is_symlink():
            raise ValueError("Linked Benny state directory")
        directory.mkdir(exist_ok=True)
        self.path = directory / "benny-state.sqlite"
        if self.path.is_symlink():
            raise ValueError("Linked Benny state file")
        self.db = sqlite3.connect(self.path, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS effects (channel TEXT, thread TEXT, effect TEXT, status TEXT NOT NULL, external_id TEXT, PRIMARY KEY(channel,thread,effect))")
        self.db.commit()

    def claim(self, channel, thread, effect):
        coordinates(channel, thread)
        if effect not in EFFECTS:
            raise ValueError("Unknown external effect")
        with self.db:
            cursor = self.db.execute("INSERT OR IGNORE INTO effects VALUES (?,?,?,'pending',NULL)", (channel, thread, effect))
        record = self.status(channel, thread, effect)
        return {**record, "action": "execute-once" if cursor.rowcount else "reconcile" if record["status"] == "pending" else "skip"}

    def status(self, channel, thread, effect):
        coordinates(channel, thread)
        row = self.db.execute("SELECT status,external_id FROM effects WHERE channel=? AND thread=? AND effect=?", (channel, thread, effect)).fetchone()
        return {"status": row[0], "external_id": row[1]} if row else {"status": "absent", "external_id": None}

    def complete(self, channel, thread, effect, external_id):
        coordinates(channel, thread)
        if not external_id:
            raise ValueError("Successful external object ID is required")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute("SELECT status,external_id FROM effects WHERE channel=? AND thread=? AND effect=?", (channel, thread, effect)).fetchone()
            if row is None:
                raise ValueError("Claim the intent before writing externally")
            if row[0] == "done" and row[1] != external_id:
                raise ValueError("Cannot replace an existing external object")
            self.db.execute("UPDATE effects SET status='done',external_id=? WHERE channel=? AND thread=? AND effect=?", (external_id, channel, thread, effect))
        return self.status(channel, thread, effect)

    def pending(self):
        return [{"channel": channel, "thread": thread, "effect": effect} for channel, thread, effect in self.db.execute("SELECT channel,thread,effect FROM effects WHERE status='pending'")]

    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("claim", "status", "complete", "pending"))
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--channel")
    parser.add_argument("--thread")
    parser.add_argument("--effect", choices=EFFECTS)
    parser.add_argument("--external-id")
    args = parser.parse_args()
    if args.action != "pending" and not all((args.channel, args.thread, args.effect)):
        parser.error("channel, original thread and effect are required")
    journal = None
    try:
        journal = Journal(args.project)
        if args.action == "pending":
            result = journal.pending()
        elif args.action == "complete":
            result = journal.complete(args.channel, args.thread, args.effect, args.external_id)
        else:
            result = getattr(journal, args.action)(args.channel, args.thread, args.effect)
        print(json.dumps(result))
    except (ValueError, sqlite3.Error) as error:
        parser.exit(1, f"benny: {error}\n")
    finally:
        if journal:
            journal.close()


if __name__ == "__main__":
    main()
