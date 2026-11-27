"""Run with: python -m unittest discover -s skills/engineering-lead/scripts -p "test_*.py" """

import argparse
import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import workers

HERE = pathlib.Path(__file__).parent


def run_watch(*args):
    out = subprocess.run(
        [sys.executable, str(HERE / "watch.py"), *args],
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=False,
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
            current = (
                self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
            )
            current, seq = current if isinstance(current, tuple) else (current, 1)
            return json.dumps(
                {
                    "result": {
                        "agent": {"agent_status": current, "state_change_seq": seq}
                    }
                }
            )
        if args[:2] == ("agent", "list"):
            return json.dumps({"result": {"agents": self.agents}})
        if args[:2] == ("agent", "read"):
            return self.screen_text
        if args[:2] in (("worktree", "create"), ("workspace", "create")):
            return json.dumps(
                {"result": {"workspace": {"panes": [{"pane_id": "w9:p1"}]}}}
            )
        return "{}"


def call(fn, args):
    buf = io.StringIO()
    with (
        contextlib.redirect_stdout(buf),
        mock.patch.object(workers.time, "sleep"),
        self_raises() as code,
    ):
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
        cmd = py_cmd('print(\'{\\"head\\": \\"b\\", \\"reviews\\": null}\')')
        code, event = run_watch(
            "pr", "--cmd", cmd, "--head", "a", "--seen", "0", "--interval", "0"
        )
        self.assertEqual((code, event["event"], event["reviews"]), (0, "pushed", 0))

    def test_a_pair_is_quiet_only_when_both_workers_are(self):
        import watch

        self.assertFalse(
            watch.all_quiet({"t1-coder": "idle", "t1-reviewer": "working"})
        )
        self.assertTrue(watch.all_quiet({"t1-coder": "idle", "t1-reviewer": "done"}))
        self.assertFalse(watch.all_quiet({}))

    def test_a_broken_pr_command_is_reported_not_waited_out(self):
        cmd = py_cmd("print('not json')")
        code, event = run_watch(
            "pr",
            "--cmd",
            cmd,
            "--head",
            "a",
            "--seen",
            "0",
            "--interval",
            "0",
            "--timeout",
            "30",
        )
        self.assertEqual((code, event["event"]), (1, "unreadable"))

    def test_an_approval_already_on_the_head_is_reported_at_start(self):
        cmd = py_cmd(
            'print(\'{\\"head\\": \\"a\\", \\"reviews\\": [{\\"commit\\": \\"a\\", \\"state\\": \\"APPROVED\\"}]}\')'
        )
        code, event = run_watch(
            "pr", "--cmd", cmd, "--head", "a", "--seen", "1", "--interval", "0"
        )
        self.assertEqual(
            (code, event["event"], event["already"]), (0, "reviewed", True)
        )

    def test_an_approval_of_an_older_head_is_not_reported_at_start(self):
        cmd = py_cmd(
            'print(\'{\\"head\\": \\"a\\", \\"reviews\\": [{\\"commit\\": \\"old\\", \\"body\\": \\"Verdict: approve old\\"}]}\')'
        )
        code, event = run_watch(
            "pr",
            "--cmd",
            cmd,
            "--head",
            "a",
            "--seen",
            "1",
            "--interval",
            "0",
            "--timeout",
            "1",
        )
        self.assertEqual((code, event["event"]), (1, "timeout"))

    def test_changes_requested_already_seen_is_not_reported_again(self):
        cmd = py_cmd(
            'print(\'{\\"head\\": \\"a\\", \\"reviews\\": [{\\"commit\\": \\"a\\", \\"body\\": \\"Verdict: changes requested\\"}]}\')'
        )
        code, event = run_watch(
            "pr",
            "--cmd",
            cmd,
            "--head",
            "a",
            "--seen",
            "1",
            "--interval",
            "0",
            "--timeout",
            "1",
        )
        self.assertEqual((code, event["event"]), (1, "timeout"))

    def test_the_next_watch_waits_for_a_log_line_after_an_event(self):
        import os

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "retros.md")
            pathlib.Path(log).write_text("start\n", encoding="utf-8")
            result = os.path.join(d, "coder-1.md")
            pathlib.Path(result).write_text("done\n", encoding="utf-8")
            code, event = run_watch(
                "file", "--path", result, "--log", log, "--interval", "0"
            )
            self.assertEqual((code, event["event"]), (0, "written"))
            code, event = run_watch(
                "file", "--path", result, "--log", log, "--interval", "0"
            )
            self.assertEqual((code, event["event"]), (1, "unlogged"))
            other = os.path.join(d, "other-coder-1.md")
            pathlib.Path(other).write_text("done\n", encoding="utf-8")
            code, event = run_watch(
                "file", "--path", other, "--log", log, "--interval", "0"
            )
            self.assertEqual(
                (code, event["event"]), (0, "written"), "another task is not blocked"
            )
            with open(log, "a", encoding="utf-8") as f:
                f.write("- round 1 done\n")
            code, event = run_watch(
                "file", "--path", result, "--log", log, "--interval", "0"
            )
            self.assertEqual(
                (code, event["event"]),
                (0, "written"),
                "a line written in the same second counts",
            )

    def test_a_push_does_not_ask_for_a_log_line(self):
        import os

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "retros.md")
            pathlib.Path(log).write_text("start\n", encoding="utf-8")
            cmd = py_cmd('print(\'{\\"head\\": \\"b\\", \\"reviews\\": []}\')')
            _code, event = run_watch(
                "pr",
                "--cmd",
                cmd,
                "--head",
                "a",
                "--seen",
                "0",
                "--log",
                log,
                "--interval",
                "0",
            )
            self.assertEqual(event["event"], "pushed")
            _code, event = run_watch(
                "pr",
                "--cmd",
                cmd,
                "--head",
                "a",
                "--seen",
                "0",
                "--log",
                log,
                "--interval",
                "0",
            )
            self.assertEqual(event["event"], "pushed")

    def test_an_acked_approval_lets_the_watcher_wait(self):
        cmd = py_cmd(
            'print(\'{\\"head\\": \\"a\\", \\"reviews\\": [{\\"commit\\": \\"a\\", \\"state\\": \\"APPROVED\\"}]}\')'
        )
        code, event = run_watch(
            "pr",
            "--cmd",
            cmd,
            "--head",
            "a",
            "--seen",
            "1",
            "--acked",
            "a",
            "--interval",
            "0",
            "--timeout",
            "1",
        )
        self.assertEqual((code, event["event"]), (1, "timeout"))

    def test_stamps_live_in_one_file_beside_the_log(self):
        import os

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "retros.md")
            pathlib.Path(log).write_text("start\n", encoding="utf-8")
            for name in ("coder-1.md", "coder-2.md"):
                result = os.path.join(d, name)
                pathlib.Path(result).write_text("done\n", encoding="utf-8")
                run_watch("file", "--path", result, "--log", log, "--interval", "0")
            stamps = json.loads(
                pathlib.Path(d, ".watch-stamps.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(stamps), 2)
            self.assertTrue(all(k.startswith("retros.md:") for k in stamps))
            self.assertEqual(
                sorted(os.listdir(d)),
                [".watch-stamps.json", "coder-1.md", "coder-2.md", "retros.md"],
            )

    def test_an_old_stamp_file_is_moved_into_the_shared_one(self):
        import os

        import watch

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "retros.md")
            pathlib.Path(log).write_text("start\n", encoding="utf-8")
            result = os.path.join(d, "coder-1.md")
            pathlib.Path(result).write_text("done\n", encoding="utf-8")
            legacy = watch.LogGate(log, result).legacy
            pathlib.Path(legacy).write_text(
                f"{os.path.getsize(log)}\n", encoding="utf-8"
            )
            code, event = run_watch(
                "file", "--path", result, "--log", log, "--interval", "0"
            )
            self.assertEqual(
                (code, event["event"]), (1, "unlogged"), "the old stamp still gates"
            )
            self.assertFalse(os.path.exists(legacy))
            self.assertIn(
                watch.LogGate(log, result).key,
                json.loads(
                    pathlib.Path(d, ".watch-stamps.json").read_text(encoding="utf-8")
                ),
            )

    def test_a_newer_old_stamp_replaces_the_shared_one(self):
        import watch

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "retros.md")
            pathlib.Path(log).write_text("a\n", encoding="utf-8")
            gate = watch.LogGate(log, "target")
            gate.close_stage()
            with open(log, "a", encoding="utf-8") as f:
                f.write("b\n")
            pathlib.Path(gate.legacy).write_text(
                f"{os.path.getsize(log)}\n", encoding="utf-8"
            )
            self.assertFalse(gate.logged())
            self.assertFalse(os.path.exists(gate.legacy))

    def test_an_unreadable_old_stamp_is_dropped(self):
        import watch

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "retros.md")
            pathlib.Path(log).write_text("a\n", encoding="utf-8")
            gate = watch.LogGate(log, "target")
            pathlib.Path(gate.legacy).write_text("garbage\n", encoding="utf-8")
            self.assertTrue(gate.logged())
            self.assertFalse(os.path.exists(gate.legacy))


class WorkersTest(unittest.TestCase):
    def args(self, **kw):
        return argparse.Namespace(**kw)

    def test_refuses_the_home_folder(self):
        fake = FakeHerdr()
        with mock.patch.object(workers, "herdr", fake):
            code, event = call(
                workers.spawn, self.args(repo=str(pathlib.Path.home()), max=None)
            )
        self.assertEqual(fake.calls, [])
        self.assertEqual((code, event["event"]), (2, "refused"))

    def test_refuses_a_folder_that_is_not_a_repository(self):
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", FakeHerdr()),
        ):
            _code, event = call(workers.spawn, self.args(repo=d, max=None))
        self.assertEqual(event["reason"], "not a Git repository")

    def test_refuses_to_start_past_the_cap(self):
        fake = FakeHerdr(agents=[{"name": "a"}, {"name": "b"}])
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(workers.spawn, self.args(repo=d, max=2))
        self.assertEqual((code, event["event"]), (1, "over_cap"))
        self.assertNotIn("worktree", [c[0] for c in fake.calls])

    def test_spawn_passes_a_forward_slash_path_and_starts_the_named_agent(self):
        fake = FakeHerdr(statuses=["idle"])
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(
                workers.spawn,
                self.args(
                    repo=d,
                    branch="t",
                    base="main",
                    label="t1",
                    name="t1-coder",
                    max=None,
                ),
            )
        create = next(c for c in fake.calls if c[0] == "worktree")
        self.assertNotIn("\\", create[create.index("--cwd") + 1])
        self.assertIn(
            ("agent", "start", "t1-coder", "--kind", "claude", "--pane", "w9:p1"),
            fake.calls,
        )
        self.assertEqual((code, event["event"]), (0, "started"))

    def test_spawn_reports_a_prompt_only_the_user_may_answer(self):
        fake = FakeHerdr(statuses=["blocked"], screen_text="Do you trust this folder?")
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(
                workers.spawn,
                self.args(
                    repo=d,
                    branch="t",
                    base="main",
                    label="t1",
                    name="t1-coder",
                    max=None,
                ),
            )
        self.assertEqual((code, event["event"]), (1, "blocked"))
        self.assertIn("trust", event["screen"])

    def test_brief_text_reaches_herdr_unchanged(self):
        fake = FakeHerdr(statuses=["working"])
        brief = "Read C:/work/$id-brief.md and /metrics/config first."
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            f = pathlib.Path(d) / "brief.md"
            f.write_text(brief, encoding="utf-8")
            code, event = call(
                workers.send,
                self.args(
                    worker="t1-coder", brief_file=str(f), slash="poteto-mode", settle=1
                ),
            )
        self.assertIn(
            ("agent", "prompt", "t1-coder", "/poteto-mode " + brief), fake.calls
        )
        self.assertEqual((code, event["event"]), (0, "working"))

    def send_with(self, fake, brief, started):
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
            mock.patch.object(workers, "wait_started", side_effect=started),
        ):
            f = pathlib.Path(d) / "brief.md"
            f.write_text(brief, encoding="utf-8")
            return call(
                workers.send,
                self.args(
                    worker="t1-coder", brief_file=str(f), slash="poteto-mode", settle=1
                ),
            )

    def enters(self, fake):
        return sum(1 for c in fake.calls if c[:2] == ("agent", "send-keys"))

    @staticmethod
    def claude_screen(transcript, input_line):
        rule = "\u2500" * 40
        return f"{transcript}\n\n{rule}\n\u276f {input_line}\n{rule}\n  auto mode on"

    def test_a_brief_left_in_the_input_box_gets_one_more_enter(self):
        fake = FakeHerdr(
            statuses=[("done", 7)],
            screen_text=self.claude_screen(
                "Earlier output", "/poteto-mode Fix the retry that doubles rows"
            ),
        )
        _code, event = self.send_with(
            fake,
            "Fix the retry that doubles rows",
            [("done", False), ("working", True)],
        )
        self.assertEqual((self.enters(fake), event["event"]), (2, "working"))

    def test_a_brief_only_in_the_transcript_gets_no_extra_enter(self):
        screen_text = self.claude_screen(
            "\u276f /poteto-mode Fix the retry that doubles rows\nWorking on it...", ""
        )
        fake = FakeHerdr(statuses=[("done", 7)], screen_text=screen_text)
        code, event = self.send_with(
            fake, "Fix the retry that doubles rows", [("done", False)]
        )
        self.assertEqual(
            (self.enters(fake), code, event["event"]), (1, 1, "not_started")
        )

    def test_a_long_brief_shown_as_pasted_text_gets_one_more_enter(self):
        fake = FakeHerdr(
            statuses=[("done", 7)],
            screen_text=self.claude_screen("", "[Pasted text #1 +40 lines]"),
        )
        _code, event = self.send_with(
            fake,
            "Fix the retry\nthen run the suite",
            [("done", False), ("working", True)],
        )
        self.assertEqual((self.enters(fake), event["event"]), (2, "working"))

    def test_a_suggestion_in_the_input_box_gets_no_enter(self):
        fake = FakeHerdr(
            statuses=[("done", 7)],
            screen_text=self.claude_screen("", "run the tests again"),
        )
        _code, event = self.send_with(fake, "Fix the retry", [("done", False)])
        self.assertEqual((self.enters(fake), event["event"]), (1, "not_started"))

    def test_a_missing_state_counter_stops_before_sending(self):
        fake = FakeHerdr(statuses=[("done", None)])
        code, event = self.send_with(fake, "Fix the retry", [])
        self.assertEqual((code, event["event"]), (1, "failed"))
        self.assertNotIn("prompt", [c[1] for c in fake.calls if len(c) > 1])

    def test_a_turn_finished_after_the_send_counts_as_started(self):
        fake = FakeHerdr(statuses=[("done", 7)])
        code, event = self.send_with(fake, "Fix the retry", [("done", True)])
        self.assertEqual((self.enters(fake), code, event["event"]), (1, 0, "working"))

    def test_done_from_the_previous_round_is_not_taken_as_started(self):
        fake = FakeHerdr(statuses=[("done", 7)])
        with (
            mock.patch.object(workers, "herdr", fake),
            mock.patch.object(workers.time, "sleep"),
            mock.patch.object(workers.time, "time", side_effect=[0, 0, 100]),
        ):
            self.assertEqual(workers.wait_started("t1-coder", 7, 1), ("done", False))

    def test_done_after_a_new_state_change_is_taken_as_started(self):
        fake = FakeHerdr(statuses=[("done", 8)])
        with mock.patch.object(workers, "herdr", fake):
            self.assertEqual(workers.wait_started("t1-coder", 7, 1), ("done", True))

    def test_an_empty_brief_is_refused_before_anything_is_sent(self):
        fake = FakeHerdr()
        code, event = self.send_with(fake, "  \n", [])
        self.assertEqual((code, event["event"], fake.calls), (2, "refused", []))

    def test_spawn_without_a_live_agent_reports_failure(self):
        fake = FakeHerdr(statuses=[None])
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
            mock.patch.object(workers, "wait_for", return_value=None),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(
                workers.spawn,
                self.args(
                    repo=d,
                    branch="t",
                    base="main",
                    label="t1",
                    name="t1-coder",
                    max=None,
                ),
            )
        self.assertEqual((code, event["event"]), (1, "failed"))

    def test_an_unreadable_agent_list_fails_closed(self):
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", lambda *a, **k: '{"result": null}'),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(workers.spawn, self.args(repo=d, max=4))
        self.assertEqual((code, event["event"]), (1, "failed"))

    def test_list_does_not_match_a_longer_task_id(self):
        agents = [{"name": "t1-coder"}, {"name": "t10-coder"}, {"name": "t1"}]
        with mock.patch.object(workers, "herdr", FakeHerdr(agents=agents)):
            _code, out = call(workers.list_workers, self.args(task="t1", max=None))
        self.assertEqual(sorted(w["name"] for w in out["workers"]), ["t1", "t1-coder"])

    def test_list_shows_only_the_task_workers_and_flags_the_cap(self):
        agents = [
            {"name": "t1-coder", "agent_status": "idle"},
            {"name": "t2-coder"},
            {"agent_status": "working"},
        ]
        with mock.patch.object(workers, "herdr", FakeHerdr(agents=agents)):
            code, out = call(workers.list_workers, self.args(task="t1", max=2))
        self.assertEqual([w["name"] for w in out["workers"]], ["t1-coder"])
        self.assertEqual((code, out["live"]), (1, 3))

    def test_handoff_refuses_a_linked_worktree(self):
        fake = FakeHerdr()
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            (pathlib.Path(d) / ".git").write_text(
                "gitdir: /repo/.git/worktrees/x\n", encoding="utf-8"
            )
            code, event = call(
                workers.handoff,
                self.args(
                    repo=d,
                    name="lead-2",
                    resume=".pm/state.md",
                    previous=None,
                    settle=1,
                ),
            )
        self.assertEqual((code, event["event"], fake.calls), (2, "refused", []))
        self.assertIn("linked worktree", event["reason"])

    def test_handoff_refuses_a_folder_that_is_not_a_repository(self):
        fake = FakeHerdr()
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            code, event = call(
                workers.handoff,
                self.args(
                    repo=d,
                    name="lead-2",
                    resume=".pm/state.md",
                    previous=None,
                    settle=1,
                ),
            )
        self.assertEqual(
            (code, event["reason"], fake.calls), (2, "not a Git repository", [])
        )

    def test_handoff_starts_the_lead_in_the_main_checkout_with_the_resume_command(self):
        fake = FakeHerdr(statuses=[("idle", 1), ("idle", 1), ("working", 2)])
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(
                workers.handoff,
                self.args(
                    repo=d,
                    name="lead-2",
                    resume=".pm/state.md",
                    previous="lead-1",
                    settle=1,
                ),
            )
        create = next(c for c in fake.calls if c[:2] == ("workspace", "create"))
        self.assertEqual(
            create[create.index("--cwd") + 1], pathlib.Path(d).resolve().as_posix()
        )
        self.assertIn(
            ("agent", "start", "lead-2", "--kind", "claude", "--pane", "w9:p1"),
            fake.calls,
        )
        self.assertIn(
            (
                "agent",
                "prompt",
                "lead-2",
                "/engineering-lead resume .pm/state.md --previous lead-1",
            ),
            fake.calls,
        )
        self.assertEqual((code, event["event"]), (0, "started"))

    def test_handoff_reports_a_prompt_only_the_user_may_answer(self):
        fake = FakeHerdr(statuses=["blocked"], screen_text="Do you trust this folder?")
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(
                workers.handoff,
                self.args(
                    repo=d,
                    name="lead-2",
                    resume=".pm/state.md",
                    previous=None,
                    settle=1,
                ),
            )
        self.assertEqual((code, event["event"]), (1, "blocked"))
        self.assertNotIn("prompt", [c[1] for c in fake.calls if len(c) > 1])

    def test_handoff_reports_a_resume_that_did_not_start(self):
        fake = FakeHerdr(statuses=[("idle", 1)])
        with (
            tempfile.TemporaryDirectory() as d,
            mock.patch.object(workers, "herdr", fake),
            mock.patch.object(workers, "wait_started", return_value=("idle", False)),
        ):
            (pathlib.Path(d) / ".git").mkdir()
            code, event = call(
                workers.handoff,
                self.args(
                    repo=d,
                    name="lead-2",
                    resume=".pm/state.md",
                    previous=None,
                    settle=1,
                ),
            )
        self.assertEqual((code, event["event"]), (1, "not_started"))


def run_lesson(*args):
    out = subprocess.run(
        [sys.executable, str(HERE / "lesson.py"), *args],
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    return out.returncode, out.stdout


class LessonTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.dir.name, "retros.md")

    def tearDown(self):
        self.dir.cleanup()

    def text(self):
        return pathlib.Path(self.log).read_text(encoding="utf-8")

    def add(self, *extra):
        return run_lesson(
            "add",
            "--log",
            self.log,
            "--task",
            "t1",
            "--where",
            "a script",
            "--change",
            "check it",
            "--text",
            "It broke.",
            *extra,
        )

    def test_add_numbers_after_the_highest_lesson(self):
        pathlib.Path(self.log).write_text(
            "2026-01-01 t0 lesson 7: Old. Next action: none / x / open\nfree text",
            encoding="utf-8",
        )
        code, _ = self.add("--repeats", "7")
        self.assertEqual(code, 0)
        last = self.text().splitlines()[-1]
        self.assertRegex(
            last,
            r"^\d{4}-\d\d-\d\d t1 lesson 8: Repeats lesson 7\. It broke\. Next action: a script / check it / open$",
        )
        self.assertIn("free text\n", self.text(), "the existing log is kept")

    def test_the_first_lesson_is_one(self):
        self.add()
        self.assertIn(" t1 lesson 1: It broke. Next action:", self.text())

    def test_an_empty_destination_is_refused(self):
        code, _ = run_lesson(
            "add",
            "--log",
            self.log,
            "--task",
            "t1",
            "--where",
            " ",
            "--change",
            "x",
            "--text",
            "y",
        )
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(self.log))

    def test_round_line(self):
        run_lesson(
            "round",
            "--log",
            self.log,
            "--task",
            "t1",
            "--round",
            "2",
            "--verdict",
            "approved",
            "--sha",
            "abc123",
        )
        self.assertRegex(
            self.text(), r"^\d{4}-\d\d-\d\d t1 round 2: approved on abc123\n$"
        )

    def test_done_closes_one_open_lesson_and_open_lists_the_rest(self):
        self.add()
        self.add()
        self.assertEqual(
            run_lesson("done", "--log", self.log, "--n", "1", "--ref", "#12")[0], 0
        )
        lines = self.text().splitlines()
        self.assertTrue(
            lines[0].endswith("Next action: a script / check it / done #12")
        )
        self.assertTrue(lines[1].endswith("/ open"))
        self.assertEqual(
            run_lesson("open", "--log", self.log)[1], "2\tt1\ta script\tcheck it\n"
        )

    def test_done_on_a_missing_or_closed_lesson_fails(self):
        self.add()
        run_lesson("done", "--log", self.log, "--n", "1", "--ref", "#12")
        before = self.text()
        self.assertEqual(
            run_lesson("done", "--log", self.log, "--n", "1", "--ref", "#13")[0], 1
        )
        self.assertEqual(
            run_lesson("done", "--log", self.log, "--n", "5", "--ref", "#13")[0], 1
        )
        self.assertEqual(self.text(), before)


if __name__ == "__main__":
    unittest.main()
