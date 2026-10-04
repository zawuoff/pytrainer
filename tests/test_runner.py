import os
import sys
import unittest

from pytrainer import runner, sandbox

TESTS = """
from solution import add

def test_adds_numbers():
    assert add(2, 3) == 5

def test_adds_negatives():
    assert add(-1, -1) == -2
"""


class RunTestsTests(unittest.TestCase):
    def test_correct_solution_passes(self):
        r = runner.run_tests({"solution.py": "def add(a, b):\n    return a + b\n"}, TESTS)
        self.assertEqual(r["status"], "passed")
        self.assertEqual((r["passed"], r["total"]), (2, 2))
        self.assertEqual(r["tests"][0]["name"], "adds numbers")

    def test_wrong_solution_fails(self):
        r = runner.run_tests({"solution.py": "def add(a, b):\n    return a - b\n"}, TESTS)
        self.assertEqual(r["status"], "failed")
        self.assertEqual(r["passed"], 0)

    def test_syntax_error_is_reported(self):
        r = runner.run_tests({"solution.py": "def add(a, b)\n    return a + b\n"}, TESTS)
        self.assertEqual(r["status"], "error")
        self.assertIn("SyntaxError", r["error"])

    def test_infinite_loop_times_out(self):
        r = runner.run_tests({"solution.py": "def add(a, b):\n    while True: pass\n"}, TESTS, timeout=2)
        self.assertEqual(r["status"], "timeout")


class BudgetTests(unittest.TestCase):
    TESTS = """
def test_fast_enough():
    print("BUDGET|time for the batch|0.40|1.2|s")

def test_cheap_enough():
    print("BUDGET|texts embedded|20|14|texts")
    assert 20 <= 14, "embedded 20 texts; the budget is 14"

def test_prints_normally():
    print("hello")
"""

    def test_budget_lines_become_budgets_and_leave_the_output(self):
        r = runner.run_tests({"solution.py": "x = 1\n"}, self.TESTS)
        self.assertEqual(r["budgets"], [
            {"label": "time for the batch", "used": 0.4, "limit": 1.2, "unit": "s", "ok": True},
            {"label": "texts embedded", "used": 20.0, "limit": 14.0, "unit": "texts", "ok": False}])
        self.assertEqual(r["stdout"].strip(), "hello")
        self.assertEqual(r["status"], "failed")

    def test_no_budgets_no_key(self):
        r = runner.run_tests({"solution.py": "def add(a, b):\n    return a + b\n"}, TESTS)
        self.assertNotIn("budgets", r)


class RunCodeTests(unittest.TestCase):
    def test_prints_and_reads_stdin(self):
        r = runner.run_code({"solution.py": "print(input().upper())"}, stdin="hi\n")
        self.assertEqual(r["stdout"], "HI\n")
        self.assertEqual(r["returncode"], 0)

    def test_home_is_the_temp_folder(self):
        r = runner.run_code({"solution.py": "import os, pathlib\nprint(os.path.samefile(pathlib.Path.home(), os.getcwd()))"})
        self.assertEqual(r["stdout"].strip(), "True")

    def test_tracebacks_show_paths_relative_to_the_run_folder(self):
        import tempfile
        from pathlib import Path
        real = Path(tempfile.mkdtemp())
        link = real.parent / (real.name + "-link")
        try:
            link.symlink_to(real, target_is_directory=True)
        except OSError:
            self.skipTest("can't create symlinks here")
        old = tempfile.tempdir
        tempfile.tempdir = str(link)   # like macOS, where the temp dir sits behind a symlink
        try:
            r = runner.run_code({"solution.py": "def f():\n    raise KeyError('x')\nf()\n"})
        finally:
            tempfile.tempdir = old
            link.unlink()
        self.assertIn('File "solution.py", line 3', r["stderr"])

    def test_prediction_is_graded_line_by_line(self):
        r = runner.check_prediction("print(1)\nprint(2)", "1\n3")
        self.assertEqual((r["passed"], r["total"]), (1, 2))


@unittest.skipUnless(sys.platform.startswith("linux"), "OS sandboxes are Linux-only")
class SandboxTests(unittest.TestCase):
    PROBE = r"""
import os, socket
srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)
socket.create_connection(srv.getsockname(), timeout=2).close()
print("loopback")
try:
    socket.create_connection(("1.1.1.1", 53), timeout=2).close(); print("network")
except OSError:
    print("offline")
data = os.environ["DATA"]
seen = os.path.exists(os.path.join(data, "marker"))
try:
    open(os.path.join(data, "planted"), "w").close()
except OSError:
    pass
print("data-visible" if seen else "data-hidden")
"""

    def run_probe(self):
        from pytrainer import db
        db.DATA_DIR.mkdir(parents=True, exist_ok=True)
        (db.DATA_DIR / "marker").write_text("x")
        code = self.PROBE.replace('os.environ["DATA"]', repr(str(db.DATA_DIR)))
        try:
            return runner.run_code({"solution.py": code})["stdout"].split()
        finally:
            self.planted = (db.DATA_DIR / "planted").exists()
            (db.DATA_DIR / "planted").unlink(missing_ok=True)

    def test_level_is_known(self):
        self.assertIn(sandbox.level(), sandbox.LEVELS)
        self.assertIn("detail", sandbox.status())

    def test_loopback_always_works(self):
        self.assertEqual(self.run_probe()[0], "loopback")

    def test_network_is_cut_when_sandboxed(self):
        if sandbox.level() == "basic":
            self.skipTest("no OS sandbox on this machine")
        self.assertEqual(self.run_probe()[1], "offline")

    def test_data_dir_is_protected_by_bwrap(self):
        if sandbox.level() != "bwrap":
            self.skipTest("bubblewrap not available")
        self.assertEqual(self.run_probe()[2], "data-hidden")
        self.assertFalse(self.planted, "a file written in the sandbox reached the real data dir")

    def test_forcing_basic_turns_it_off(self):
        old = os.environ.get("PYTRAINER_SANDBOX")
        os.environ["PYTRAINER_SANDBOX"] = "basic"
        sandbox._level = None
        try:
            self.assertEqual(sandbox.level(), "basic")
        finally:
            sandbox._level = None
            if old is None:
                os.environ.pop("PYTRAINER_SANDBOX")
            else:
                os.environ["PYTRAINER_SANDBOX"] = old


if __name__ == "__main__":
    unittest.main()
