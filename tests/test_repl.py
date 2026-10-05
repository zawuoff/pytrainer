import time
import unittest
from unittest import mock

import server
from pytrainer import repl


class ReplTests(unittest.TestCase):
    def tearDown(self):
        repl.stop_all()

    def run_all(self, sid, *commands):
        return [repl.run(sid, c) for c in commands]

    def test_state_persists_and_expressions_echo(self):
        sid = repl.start()["id"]
        a, b, c = self.run_all(sid, "x = 21", "x * 2", "_ + 1")
        self.assertEqual((a["out"], b["out"], c["out"]), ("", "42\n", "43\n"))

    def test_blocks_ask_for_more_until_a_blank_line(self):
        sid = repl.start()["id"]
        self.assertTrue(repl.run(sid, "def f(n):")["more"])
        self.assertTrue(repl.run(sid, "def f(n):\n    return n + 1")["more"])
        self.assertFalse(repl.run(sid, "def f(n):\n    return n + 1\n")["more"])
        self.assertEqual(repl.run(sid, "f(1)")["out"], "2\n")

    def test_pasted_block_errors_and_fd_output(self):
        sid = repl.start()["id"]
        r = repl.run(sid, 'print("hi")\n1/0')
        self.assertEqual(r["out"], "hi\n")
        self.assertIn('File "<stdin>", line 2', r["err"])
        self.assertNotIn("_repl_agent", r["err"])
        self.assertNotIn("During handling", r["err"])
        self.assertIn("fd!", repl.run(sid, 'import os; os.write(1, b"fd!\\n")')["out"])
        self.assertIn("SyntaxError", repl.run(sid, "syntax error here")["err"])
        self.assertIn("EOFError", repl.run(sid, "input()")["err"])
        self.assertIn("Restart", repl.run(sid, "exit()")["err"])
        self.assertEqual(repl.run(sid, "1 + 1")["out"], "2\n", "the session survives all of that")

    def test_load_my_code_runs_the_file_first(self):
        files = {"app.py": 'def add(a, b):\n    return a + b\nif __name__ == "__main__":\n    print(add(2, 3))\n'}
        s = repl.start(files, run_file="app.py")
        self.assertEqual(s["out"], "5\n")
        self.assertEqual(repl.run(s["id"], "add(10, 5)")["out"], "15\n")
        broken = repl.start({"app.py": "def f():\n    return 1\nf(2)\n"}, run_file="app.py")
        self.assertIn('File "app.py", line 3', broken["err"])
        self.assertNotIn("_repl_agent", broken["err"])
        with self.assertRaises(ValueError):
            repl.start({}, run_file="missing.py")

    def test_a_runaway_command_resets_the_session(self):
        sid = repl.start()["id"]
        repl.run(sid, "x = 1")
        with mock.patch.object(repl, "COMMAND_TIMEOUT", 1.5):
            started = time.monotonic()
            r = repl.run(sid, "while True: pass\n")
            self.assertLess(time.monotonic() - started, 6)
        self.assertTrue(r["restarted"])
        self.assertIn("Stopped", r["err"])
        self.assertIn("NameError", repl.run(sid, "x")["err"], "a fresh session has no old variables")

    def test_session_limit_and_stop(self):
        ids = [repl.start()["id"] for _ in range(repl.MAX_SESSIONS + 1)]
        with self.assertRaises(KeyError):
            repl.run(ids[0], "1")  # the oldest was closed to make room
        repl.stop(ids[-1])
        with self.assertRaises(KeyError):
            repl.run(ids[-1], "1")

    def test_sessions_outlive_the_thread_that_started_them(self):
        # Each HTTP request runs on its own thread; the sandbox kills children of a thread that exits.
        import threading
        box = {}


        def request():  # the first command is what starts the process
            box["s"] = repl.start()
            repl.run(box["s"]["id"], "kept = 7")
        t = threading.Thread(target=request)
        t.start()
        t.join()
        time.sleep(0.3)
        r = repl.run(box["s"]["id"], "kept")
        self.assertEqual((r["out"], r["restarted"]), ("7\n", False))

    def test_endpoints(self):
        s = server.api_repl_start({"files": {"solution.py": "y = 5\n", "notes.txt": "x"}, "run": "solution.py"})
        self.assertEqual(server.api_repl_run(s["id"], {"code": "y * 2"})["out"], "10\n")
        server.api_repl_stop(s["id"])
        with self.assertRaises(server.ApiError) as ctx:
            server.api_repl_run(s["id"], {"code": "1"})
        self.assertEqual(ctx.exception.status, 404)
        with self.assertRaises(server.ApiError):
            server.api_repl_start({"files": {"notes.txt": "x"}, "run": "notes.txt"})


if __name__ == "__main__":
    unittest.main()
