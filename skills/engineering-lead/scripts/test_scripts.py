"""Run with: python -m unittest discover -s skills/engineering-lead/scripts -p "test_*.py" """

import argparse
import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import workers  # noqa: E402

HERE = pathlib.Path(__file__).parent


def run_watch(*args):
    out = subprocess.run(
        [sys.executable, str(HERE / "watch.py"), *args],
        capture_output=True, encoding="utf-8", timeout=60, check=False,
    )
    return out.returncode, json.loads(out.stdout)


def py_cmd(code):
    return f'"{sys.executable}" -c "{code}"'


class FakeHerdr:
    def __init__(self, statuses=(), agents=(), screen_text=""):
        self.calls = []
        self.statuses = list(statuses)
        self.agents = list(agents)
        self.screen_text = screen_text

    def __call__(self, *args, timeout=60):
        self.calls.append(args)
        if args[:2] == ("agent", "get"):
            current = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
            return json.dumps({"result": {"agent": {"agent_status": current}}})
        if args[:2] == ("agent", "list"):
            return json.dumps({"result": {"agents": self.agents}})
        if args[:2] == ("agent", "read"):
            return self.screen_text
        if args[:2] == ("worktree", "create"):
            return json.dumps({"result": {"workspace": {"panes": [{"pane_id": "w9:p1"}]}}})
        return "{}"


def call(fn, args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), mock.patch.object(workers.time, "sleep"):
        with self_raises() as code:
            fn(args)
    return code.value, json.loads(buf.getvalue())


class self_raises:
    def __enter__(self):
        return self

    def __exit__(self, kind, err, tb):
        if kind is SystemExit:
            self.value = err.code
            return True
        return False


class WatchTest(unittest.TestCase):
    def test_null_reviews_still_reports_a_push(self):
        cmd = py_cmd("print('{\\\"head\\\": \\\"b\\\", \\\"reviews\\\": null}')")
        code, event = run_watch("pr", "--cmd", cmd, "--head", "a", "--seen", "0", "--interval", "0")
        self.assertEqual((code, event["event"], event["reviews"]), (0, "pushed", 0))

    def test_a_broken_pr_command_is_reported_not_waited_out(self):
        cmd = py_cmd("print('not json')")
        code, event = run_watch("pr", "--cmd", cmd, "--head", "a", "--seen", "0", "--interval", "0", "--timeout", "30")
        self.assertEqual((code, event["event"]), (1, "unreadable"))


class WorkersTest(unittest.TestCase):
    def args(self, **kw):
        return argparse.Namespace(**kw)

    def test_refuses_the_home_folder(self):
        code, event = call(workers.spawn, self.args(repo=str(pathlib.Path.home()), max=None))
        self.assertEqual((code, event["event"]), (2, "refused"))

    def test_refuses_a_folder_that_is_not_a_repository(self):
        with tempfile.TemporaryDirectory() as d:
            code, event = call(workers.spawn, self.args(repo=d, max=None))
        self.assertEqual(event["reason"], "not a Git repository")

    def test_refuses_to_start_past_the_cap(self):
        fake = FakeHerdr(agents=[{"name": "a"}, {"name": "b"}])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(workers, "herdr", fake):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(workers.spawn, self.args(repo=d, max=2))
        self.assertEqual((code, event["event"]), (1, "over_cap"))
        self.assertNotIn("worktree", [c[0] for c in fake.calls])

    def test_spawn_passes_a_forward_slash_path_and_starts_the_named_agent(self):
        fake = FakeHerdr(statuses=["idle"])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(workers, "herdr", fake):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(workers.spawn, self.args(repo=d, branch="t", base="main", label="t1", name="t1-coder", max=None))
        create = next(c for c in fake.calls if c[0] == "worktree")
        self.assertNotIn("\\", create[create.index("--cwd") + 1])
        self.assertIn(("agent", "start", "t1-coder", "--kind", "claude", "--pane", "w9:p1"), fake.calls)
        self.assertEqual((code, event["event"]), (0, "started"))

    def test_spawn_reports_a_prompt_only_the_user_may_answer(self):
        fake = FakeHerdr(statuses=["blocked"], screen_text="Do you trust this folder?")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(workers, "herdr", fake):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(workers.spawn, self.args(repo=d, branch="t", base="main", label="t1", name="t1-coder", max=None))
        self.assertEqual((code, event["event"]), (1, "blocked"))
        self.assertIn("trust", event["screen"])

    def test_brief_text_reaches_herdr_unchanged(self):
        fake = FakeHerdr(statuses=["working"])
        brief = "Read C:/work/$id-brief.md and /metrics/config first."
        with tempfile.TemporaryDirectory() as d, mock.patch.object(workers, "herdr", fake):
            f = pathlib.Path(d) / "brief.md"
            f.write_text(brief, encoding="utf-8")
            code, event = call(workers.send, self.args(worker="t1-coder", brief_file=str(f), slash="poteto-mode", settle=1))
        self.assertIn(("agent", "prompt", "t1-coder", "/poteto-mode " + brief), fake.calls)
        self.assertEqual((code, event["event"]), (0, "working"))

    def test_an_unsubmitted_prompt_gets_one_more_enter(self):
        fake = FakeHerdr(statuses=["idle", "idle", "working"], screen_text="> /poteto-mode Fix the retry")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(workers, "herdr", fake), \
                mock.patch.object(workers.time, "time", side_effect=[0, 0, 100, 0, 0, 0]):
            f = pathlib.Path(d) / "brief.md"
            f.write_text("Fix the retry", encoding="utf-8")
            code, event = call(workers.send, self.args(worker="t1-coder", brief_file=str(f), slash="poteto-mode", settle=1))
        self.assertEqual(sum(1 for c in fake.calls if c[:2] == ("agent", "send-keys")), 2)
        self.assertEqual(event["event"], "working")

    def test_list_shows_only_the_task_workers_and_flags_the_cap(self):
        agents = [{"name": "t1-coder", "agent_status": "idle"}, {"name": "t2-coder"}, {"agent_status": "working"}]
        with mock.patch.object(workers, "herdr", FakeHerdr(agents=agents)):
            code, out = call(workers.list_workers, self.args(task="t1", max=2))
        self.assertEqual([w["name"] for w in out["workers"]], ["t1-coder"])
        self.assertEqual((code, out["live"]), (1, 3))


if __name__ == "__main__":
    unittest.main()
