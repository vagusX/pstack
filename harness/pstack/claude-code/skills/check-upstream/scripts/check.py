#!/usr/bin/env python3
"""Fetch upstream main and report commits missing from local main."""

import json
import os
import subprocess
import sys


def git(*args):
    result = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
        timeout=60,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} exited {result.returncode}")
    return result.stdout.strip()


def check():
    git("rev-parse", "--show-toplevel")
    if git("rev-parse", "--is-shallow-repository") == "true":
        raise RuntimeError("Shallow history cannot prove ahead/behind counts; fetch full history first.")
    local = git("rev-parse", "--verify", "refs/heads/main^{commit}")
    git("remote", "get-url", "upstream")
    git("fetch", "--no-tags", "upstream", "+refs/heads/main:refs/remotes/upstream/main")
    upstream = git("rev-parse", "--verify", "refs/remotes/upstream/main^{commit}")
    base = git("merge-base", local, upstream)
    ahead, behind = map(int, git("rev-list", "--left-right", "--count", f"{local}...{upstream}").split())
    status = "diverged" if ahead and behind else "behind" if behind else "ahead" if ahead else "up-to-date"
    return {
        "local_ref": "refs/heads/main",
        "local_commit": local,
        "upstream_ref": "refs/remotes/upstream/main",
        "upstream_commit": upstream,
        "merge_base": base,
        "status": status,
        "local_only_commits": ahead,
        "upstream_only_commits": behind,
        "missing_commits": git("log", "--format=%h %s", f"{local}..{upstream}").splitlines(),
        "upstream_changed_files": git("diff", "--name-status", "--no-renames", base, upstream, "--").splitlines(),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(check(), indent=2))
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Upstream check failed: {error}", file=sys.stderr)
        sys.exit(1)
