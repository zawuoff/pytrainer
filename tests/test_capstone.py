import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import server
from pytrainer import capstone, content, db


def solution(pid):
    return content.load()["projects_by_id"][pid]["solution_files"]


class CapstoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.ex("DELETE FROM submissions")

    def test_1_needs_the_five_parts_first(self):
        with self.assertRaises(server.ApiError) as err:
            server.api_project_submit("capstone", {"files": solution("capstone")})
        self.assertIn("Pass these first", str(err.exception))
        with self.assertRaises(ValueError):
            capstone.export(Path(tempfile.mkdtemp()))
        self.assertFalse(capstone.status()["ready"])

    def test_2_runs_on_your_own_passing_code_and_exports_a_working_repo(self):
        for pid in capstone.STAGES:
            r = server.api_project_submit(pid, {"files": solution(pid)})
            self.assertEqual(r["result"]["status"], "passed", (pid, r["result"]))
        self.assertTrue(capstone.status()["ready"])
        info = server.api_project("capstone")
        self.assertTrue(all(b["passed"] for b in info["builds_on"]))

        r = server.api_project_submit("capstone", {"files": solution("capstone")})
        self.assertEqual(r["result"]["status"], "passed", r["result"])
        starter = content.load()["projects_by_id"]["capstone"]["starter_files"]
        self.assertNotEqual(server.api_project_submit("capstone", {"files": starter})["result"]["status"], "passed")

        dest = Path(tempfile.mkdtemp()) / "repo"
        out = capstone.export(dest)
        for name in ("app.py", "chunker.py", "search.py", "rag.py", "evals.py", "agent.py", "README.md",
                     "run_tests.py", "pyproject.toml", ".gitignore", "docs/faq.txt", "tests/test_app.py"):
            self.assertTrue((dest / name).is_file(), name)
        self.assertFalse((dest / "docs/notes.bin").exists(), "only text docs are exported")
        readme = (dest / "README.md").read_text()
        self.assertIn("```mermaid", readme)
        self.assertIn("`app.py`", readme)
        self.assertTrue(out["has_app"])
        if out["git"]["available"]:
            self.assertTrue((dest / ".git").is_dir())

        cp = subprocess.run([sys.executable, "run_tests.py"], cwd=dest, capture_output=True, text=True, timeout=300)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(cp.stdout.count("ok  "), 6, cp.stdout)

        cp = subprocess.run([sys.executable, "app.py", "docs", "How do I install it?"], cwd=dest,
                            capture_output=True, text=True, timeout=60)
        self.assertIn("guides/setup.md", cp.stdout)

        again = capstone.export(dest)
        if again["git"]["available"] and out["git"]["committed"]:
            self.assertIn("Nothing changed", again["git"]["message"])


if __name__ == "__main__":
    unittest.main()
