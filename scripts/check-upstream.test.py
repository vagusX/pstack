"""Exercise the update checker against real local Git repositories."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / "pstack/skills/check-upstream/scripts/check.py"


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, text=True, capture_output=True
    ).stdout.strip()


class CheckUpstreamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pstack-check-upstream-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upstream = self.root / "upstream"
        self.local = self.root / "local"
        self.upstream.mkdir()
        git(self.upstream, "init", "--quiet", "--initial-branch=main")
        self.identity(self.upstream)
        self.commit(self.upstream, "baseline")
        git(self.root, "clone", "--quiet", str(self.upstream), str(self.local))
        self.identity(self.local)
        git(self.local, "remote", "add", "upstream", str(self.upstream))

    def identity(self, repo):
        git(repo, "config", "user.name", "Checker test")
        git(repo, "config", "user.email", "checker@example.invalid")
        git(repo, "config", "commit.gpgsign", "false")

    def commit(self, repo, name):
        (repo / name).write_text(name + "\n")
        git(repo, "add", name)
        git(repo, "commit", "--quiet", "-m", name)
        return git(repo, "rev-parse", "HEAD")

    def run_checker(self):
        return subprocess.run(
            [sys.executable, str(CHECKER)], cwd=self.local, text=True, capture_output=True
        )

    def report(self):
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_current(self):
        report = self.report()
        self.assertEqual(report["status"], "up-to-date")
        self.assertEqual(report["upstream_only_commits"], 0)
        self.assertEqual(report["missing_commits"], [])

    def test_fresh_upstream_commits_without_changing_branch_or_dirty_files(self):
        upstream_tip = self.commit(self.upstream, "upstream-change")
        git(self.local, "switch", "-c", "work-in-progress")
        (self.local / "baseline").write_text("uncommitted user work\n")
        (self.local / "untracked").write_text("keep this\n")
        before = git(self.local, "status", "--porcelain")
        local_tip = git(self.local, "rev-parse", "main")
        report = self.report()
        self.assertEqual(report["status"], "behind")
        self.assertEqual(report["upstream_only_commits"], 1)
        self.assertEqual(report["upstream_commit"], upstream_tip)
        self.assertEqual(report["upstream_changed_files"], ["A\tupstream-change"])
        self.assertEqual(git(self.local, "rev-parse", "main"), local_tip)
        self.assertEqual(git(self.local, "branch", "--show-current"), "work-in-progress")
        self.assertEqual(git(self.local, "status", "--porcelain"), before)
        self.assertEqual((self.local / "baseline").read_text(), "uncommitted user work\n")
        self.assertEqual((self.local / "untracked").read_text(), "keep this\n")

    def test_local_commits_are_not_reported_as_upstream_updates(self):
        self.commit(self.local, "local-change")
        report = self.report()
        self.assertEqual(report["status"], "ahead")
        self.assertEqual(report["local_only_commits"], 1)
        self.assertEqual(report["upstream_only_commits"], 0)
        self.assertEqual(report["upstream_changed_files"], [])

    def test_divergence_reports_only_upstream_file_changes(self):
        self.commit(self.local, "local-change")
        self.commit(self.upstream, "upstream-change")
        report = self.report()
        self.assertEqual(report["status"], "diverged")
        self.assertEqual((report["local_only_commits"], report["upstream_only_commits"]), (1, 1))
        self.assertEqual(report["upstream_changed_files"], ["A\tupstream-change"])

    def test_missing_remote_fails(self):
        git(self.local, "remote", "remove", "upstream")
        result = self.run_checker()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Upstream check failed", result.stderr)

    def test_failed_fetch_does_not_report_cached_ref_as_current(self):
        self.report()
        git(self.local, "remote", "set-url", "upstream", str(self.root / "absent"))
        result = self.run_checker()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_shallow_clone_fails(self):
        shallow = self.root / "shallow"
        git(self.root, "clone", "--quiet", "--depth", "1", self.upstream.as_uri(), str(shallow))
        result = subprocess.run(
            [sys.executable, str(CHECKER)], cwd=shallow, text=True, capture_output=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Shallow history", result.stderr)


if __name__ == "__main__":
    unittest.main()
