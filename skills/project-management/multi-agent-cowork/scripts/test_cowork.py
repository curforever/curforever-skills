#!/usr/bin/env python3
"""Isolated CLI integration checks; no model calls or user projects."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("cowork.py")


class CoworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="multi-agent-cowork-test-")
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        (self.root / "src").mkdir()
        (self.root / "src" / "answer.py").write_text("value = 0\n")
        self.plan = Path(self.temp.name) / "plan.md"
        self.plan.write_text("# Goal\nSet value to 42 within src; preserve unrelated files.\n"
                             "# Acceptance\nRead value and report actual checks.\n")
        self.report = Path(self.temp.name) / "report.md"
        self.report.write_text("# Result\nRead src/answer.py; value documented; no live tests claimed.\n")
        self.call("init")
        self.feature = self.call("feature", "--title", "feature one")["id"]

    def tearDown(self):
        self.temp.cleanup()

    def raw(self, *args, root=None):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root or self.root),
                               *map(str, args)], capture_output=True, text=True)

    def call(self, *args, **kwargs):
        p = self.raw(*args, **kwargs)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def reject(self, *args, **kwargs):
        p = self.raw(*args, **kwargs)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        return p.stderr

    def task(self, feature=None, **extra):
        args = ["task", "--feature", feature or self.feature, "--title", "bounded change",
                "--goal", "set answer", "--plan", self.plan, "--scope", "src/**",
                "--acceptance", "answer is 42"]
        for key, value in extra.items():
            args += ["--" + key.replace("_", "-"), value]
        return self.call(*args)

    def show(self, task):
        return self.call("show", "--task", task["task_path"])

    def claim(self, task, actor="Agent2", purpose="execute"):
        s = self.show(task)
        return self.call("claim", "--task", task["id"], "--actor", actor,
                         "--purpose", purpose, "--expect-version", s["version"])

    def checkpoint(self, task, run, disposition):
        return self.call("checkpoint", "--task", task["id"], "--token", run["token"],
                         "--expect-version", self.show(task)["version"], "--report", self.report,
                         "--disposition", disposition)

    def finish(self, task, run, *args):
        return self.call("finish", "--task", task["id"], "--token", run["token"],
                         "--expect-version", self.show(task)["version"], "--report", self.report, *args)

    def review(self, task, *args):
        s = self.show(task)
        return self.call("review", "--task", task["id"], "--actor", "Agent3",
                         "--expect-version", s["version"], "--revision", s["revision"],
                         "--expect-run", s["last_run"], "--expected-evidence", s["evidence"],
                         "--verdict", "accepted", "--report", self.report, *args)

    def test_rotation_repair_and_return_same_task(self):
        t = self.task()
        original_plan = Path(t["plan_path"]).read_bytes()
        r2 = self.claim(t)
        self.checkpoint(t, r2, "blocked")
        r1 = self.claim(t, "Agent1", "repair")
        (self.root / "src" / "answer.py").write_text("value = 42\n")
        self.checkpoint(t, r1, "paused")
        r2b = self.claim(t, "Agent2")
        self.finish(t, r2b)
        reviewed = self.review(t)
        self.assertEqual(reviewed["status"], "accepted")
        self.assertEqual([r["actor"] for r in reviewed["runs"]], ["Agent2", "Agent1", "Agent2"])
        self.assertEqual(len({r["id"] for r in reviewed["runs"]}), 3)
        self.assertEqual(Path(t["plan_path"]).read_bytes(), original_plan)
        self.assertEqual((self.root / "src" / "answer.py").read_text(), "value = 42\n")

    def test_recover_stopped_run_and_reject_old_token(self):
        t = self.task()
        old = self.claim(t)
        (self.root / "src" / "answer.py").write_text("value = 7\n")
        recovered = self.call("recover", "--task", t["id"], "--expect-version", old["version"],
                              "--expect-run", old["run"], "--reason", "user requested takeover",
                              "--stopped-evidence", "isolated fake worker never spawned")
        self.assertEqual(recovered["runs"][0]["status"], "interrupted")
        new = self.claim(t, "Agent1", "repair")
        self.reject("finish", "--task", t["id"], "--token", old["token"],
                    "--expect-version", new["version"], "--report", self.report)
        self.assertEqual(self.show(t)["active_run"], new["run"])
        self.finish(t, new)

    def test_same_workspace_lock_across_features(self):
        t = self.task()
        f2 = self.call("feature", "--title", "feature two")["id"]
        t2 = self.task(feature=f2)
        self.claim(t)
        self.reject("claim", "--task", t2["id"], "--actor", "other", "--expect-version", 1)
        self.assertEqual(self.show(t2)["status"], "planned")
        self.assertEqual(len(self.call("list")), 2)

    def test_racing_claim_has_one_winner(self):
        t = self.task()
        cmd = [sys.executable, str(SCRIPT), "--root", str(self.root), "claim",
               "--task", t["id"], "--actor", "race", "--expect-version", "1"]
        procs = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for _ in range(2)]
        codes = []
        for proc in procs:
            proc.communicate(timeout=10)
            codes.append(proc.returncode)
        self.assertEqual(sorted(codes), [0, 1])
        self.assertEqual(len(self.show(t)["runs"]), 1)

    def test_continue_checkpoint_keeps_lock_and_version(self):
        t = self.task()
        r = self.claim(t)
        s = self.checkpoint(t, r, "continue")
        self.assertEqual(s["status"], "running")
        self.assertIsNotNone(s["workspace_owner"])
        self.reject("finish", "--task", t["id"], "--token", r["token"],
                    "--expect-version", r["version"], "--report", self.report)
        self.finish(t, r)

    def test_handoff_is_complete_readonly_no_token(self):
        t = self.task()
        r = self.claim(t)
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (self.root / ".ai-cowork").rglob("*") if p.is_file()}
        result = self.raw("handoff", "--task", t["id"], "--action", "repair")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(t["task_path"], result.stdout)
        self.assertIn(str(self.root.resolve()), result.stdout)
        self.assertIn("Set value to 42", result.stdout)
        self.assertNotIn(r["token"], result.stdout)
        after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (self.root / ".ai-cowork").rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_revision_preserved_stale_versions_refused(self):
        t = self.task()
        original = Path(t["plan_path"]).read_text()
        self.plan.write_text("# New plan\nSet value to 43; same allowed files.\n")
        s = self.call("revise", "--task", t["id"], "--expect-version", 1, "--plan", self.plan)
        self.assertEqual(s["revision"], 2)
        self.assertEqual(Path(t["plan_path"]).read_text(), original)
        self.reject("claim", "--task", t["id"], "--actor", "stale", "--expect-version", 1)

    def test_scope_drift_and_plan_tamper_refused(self):
        t = self.task()
        (self.root / "src" / "answer.py").write_text("value = 8\n")
        self.reject("claim", "--task", t["id"], "--actor", "drift", "--expect-version", 1)
        Path(t["plan_path"]).write_text("silently changed")
        self.reject("show", "--task", t["id"])

    def test_stale_review_rejected_without_state_change(self):
        t = self.task()
        self.finish(t, self.claim(t))
        s = self.show(t)
        (self.root / "src" / "answer.py").write_text("value = 99\n")
        self.reject("review", "--task", t["id"], "--actor", "Agent3", "--expect-version", s["version"],
                    "--revision", s["revision"], "--expect-run", s["last_run"],
                    "--expected-evidence", s["evidence"], "--verdict", "accepted", "--report", self.report)
        self.assertEqual(self.show(t)["status"], "awaiting_review")
        self.assertFalse((self.root / ".ai-cowork" / "workspace.lock").exists())

    def test_self_check_not_independent(self):
        t = self.task()
        self.finish(t, self.claim(t))
        s = self.show(t)
        common = ["review", "--task", t["id"], "--actor", "Agent2", "--expect-version", s["version"],
                  "--revision", s["revision"], "--expect-run", s["last_run"],
                  "--expected-evidence", s["evidence"], "--verdict", "accepted", "--report", self.report]
        self.reject(*common)
        self.reject(*common, "--review-kind", "self-check")
        self.assertEqual(self.call(*common, "--review-kind", "self-check",
                                   "--waiver", "user explicitly accepted self-check")["status"], "accepted")

    def test_no_automatic_repeat_from_review_or_completion(self):
        t = self.task()
        self.finish(t, self.claim(t))
        s = self.show(t)
        self.reject("claim", "--task", t["id"], "--actor", "Agent2", "--expect-version", s["version"])
        self.finish(t, self.claim(t, "Agent1", "repair"))
        self.review(t)
        s = self.show(t)
        self.reject("claim", "--task", t["id"], "--actor", "Agent2", "--purpose", "repair",
                    "--expect-version", s["version"])

    def test_symlink_scope_never_reads_outside_and_missing_create_detected(self):
        external = Path(self.temp.name) / "outside"
        external.mkdir()
        (external / "secret.txt").write_text("one")
        try:
            (self.root / "src" / "link").symlink_to(external, target_is_directory=True)
        except OSError as exc:
            if getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows account lacks symlink privilege; symlink behavior not verified")
            raise
        t = self.task()
        (external / "secret.txt").write_text("two")
        self.assertEqual(t["evidence"], self.show(t)["evidence"])
        (self.root / "src" / "new.py").write_text("new")
        self.assertNotEqual(t["evidence"], self.show(t)["evidence"])

    def test_subdirectory_canonicalizes_and_corrupt_state_fails(self):
        t = self.task()
        s = self.call("show", "--task", t["id"], root=self.root / "src")
        self.assertEqual(s["id"], t["id"])
        Path(t["task_path"], "state.json").write_text("{broken")
        self.reject("list")

    def test_crash_lock_after_terminal_state_recover_preserves_result(self):
        t = self.task()
        old = self.claim(t)
        lock = self.root / ".ai-cowork" / "workspace.lock"
        owner = lock.read_text()
        self.finish(t, old)
        lock.write_text(owner)  # Simulate interruption after state commit, before lock unlink.
        s = self.show(t)
        recovered = self.call("recover", "--task", t["id"], "--expect-version", s["version"],
                              "--expect-run", old["run"], "--reason", "residual lock",
                              "--stopped-evidence", "completion committed; fake worker stopped")
        self.assertEqual(recovered["status"], "awaiting_review")
        self.assertEqual(recovered["runs"][0]["status"], "awaiting_review")
        self.assertEqual(len(recovered["runs"][0]["reports"]), 2)
        self.review(t)

    def test_previous_repair_actor_is_not_independent(self):
        t = self.task()
        self.checkpoint(t, self.claim(t), "blocked")
        repaired = self.claim(t, "Agent1", "repair")
        (self.root / "src" / "answer.py").write_text("value = 42\n")
        self.checkpoint(t, repaired, "paused")
        self.finish(t, self.claim(t, "Agent2"))
        s = self.show(t)
        self.reject("review", "--task", t["id"], "--actor", "Agent1",
                    "--expect-version", s["version"], "--revision", s["revision"],
                    "--expect-run", s["last_run"], "--expected-evidence", s["evidence"],
                    "--verdict", "accepted", "--report", self.report)
        self.assertEqual(self.show(t)["status"], "awaiting_review")

    def test_residual_lock_recovery_does_not_bless_unreported_edits(self):
        t = self.task()
        old = self.claim(t)
        lock = self.root / ".ai-cowork" / "workspace.lock"
        owner = lock.read_text()
        self.finish(t, old)
        lock.write_text(owner)
        (self.root / "src" / "answer.py").write_text("value = 999\n")
        s = self.show(t)
        recovered = self.call("recover", "--task", t["id"], "--expect-version", s["version"],
                              "--expect-run", old["run"], "--reason", "residual",
                              "--stopped-evidence", "fake worker ended")
        self.assertNotEqual(recovered["evidence"], recovered["submitted_evidence"])
        self.reject("review", "--task", t["id"], "--actor", "Agent3",
                    "--expect-version", recovered["version"], "--revision", recovered["revision"],
                    "--expect-run", recovered["last_run"], "--expected-evidence", recovered["evidence"],
                    "--verdict", "accepted", "--report", self.report)

    def test_review_crash_recovery_preserves_execution_history(self):
        t = self.task()
        self.finish(t, self.claim(t))
        s = self.show(t)
        lock = self.root / ".ai-cowork" / "workspace.lock"
        lock.write_text(json.dumps({"schema": 1, "task": t["task_path"], "run": "review-simulated",
                                    "token": "simulation-token", "actor": "Agent3", "operation": "review"}))
        recovered = self.call("recover", "--task", t["id"], "--expect-version", s["version"],
                              "--expect-run", "review-simulated", "--reason", "review process ended",
                              "--stopped-evidence", "no live review process in isolated test")
        self.assertEqual(recovered["status"], "awaiting_review")
        self.assertEqual(recovered["last_run"], s["last_run"])
        self.assertEqual(len(recovered["runs"]), 1)
        self.assertEqual(recovered["submitted_evidence"], s["submitted_evidence"])
        self.review(t)

    def test_different_record_roots_share_workspace_lock(self):
        t = self.task()
        other = Path(self.temp.name) / "other-record-root"
        other.mkdir()
        self.call("init", root=other)
        fid = self.call("feature", "--title", "external records", root=other)["id"]
        t2 = self.call("task", "--feature", fid, "--title", "second task", "--goal", "same workspace",
                       "--plan", self.plan, "--scope", "src/**", "--acceptance", "same evidence",
                       "--workspace", self.root, root=other)
        self.claim(t)
        self.reject("claim", "--task", t2["id"], "--actor", "Agent4",
                    "--expect-version", 1, root=other)
        self.assertEqual(self.call("show", "--task", t2["id"], root=other)["status"], "planned")

    def test_crash_before_claim_state_commit_preserves_orphan_history(self):
        t = self.task()
        lock = self.root / ".ai-cowork" / "workspace.lock"
        lock.write_text(json.dumps({"schema": 1, "task": t["task_path"], "run": "run-orphan",
                                    "token": "orphan-token", "actor": "Agent2", "operation": "execute"}))
        recovered = self.call("recover", "--task", t["id"], "--expect-version", 1,
                              "--expect-run", "run-orphan", "--reason", "interrupted before state commit",
                              "--stopped-evidence", "isolated process ended")
        self.assertEqual(recovered["status"], "paused")
        self.assertTrue(recovered["runs"][0]["orphan"])
        self.finish(t, self.claim(t, "Agent1", "repair"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
