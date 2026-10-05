import unittest

import server
from pytrainer import content, db, progress


def easy_code_steps(n):
    exs = content.load()["exercises"].values()
    return [e for e in exs if e["difficulty"] <= 1 and e.get("mode", "function") in ("function", "script")
            and not e.get("extra")][:n]


class DrillTests(unittest.TestCase):
    def setUp(self):
        db.ex("DELETE FROM exercise_state")
        db.ex("DELETE FROM drills")

    def test_needs_solved_steps(self):
        d = server.api_drill()
        self.assertFalse(d["enough"])
        self.assertEqual(d["pool"], [])

    def test_pool_is_solved_easy_steps_without_solutions(self):
        steps = easy_code_steps(6)
        for e in steps:
            progress.save_state(progress.get_state(e["id"]) | {"status": "solved"})
        d = server.api_drill()
        self.assertTrue(d["enough"])
        self.assertEqual({e["id"] for e in d["pool"]}, {e["id"] for e in steps})
        self.assertNotIn("solution", d["pool"][0])
        self.assertNotIn("tests", d["pool"][0])

    def test_check_grades_without_recording(self):
        e = easy_code_steps(1)[0]
        progress.save_state(progress.get_state(e["id"]) | {"status": "solved", "attempts": 1})
        before = progress.get_state(e["id"])
        attempts_before = db.q1("SELECT COUNT(*) AS n FROM attempts")["n"]
        ok = server.api_drill_check({"id": e["id"], "files": {"solution.py": e["solution"]}})
        bad = server.api_drill_check({"id": e["id"], "files": {"solution.py": e["starter"]}})
        self.assertEqual(ok["result"]["status"], "passed")
        self.assertNotEqual(bad["result"]["status"], "passed")
        self.assertEqual(progress.get_state(e["id"]), before)
        self.assertEqual(db.q1("SELECT COUNT(*) AS n FROM attempts")["n"], attempts_before)

    def test_finish_keeps_personal_bests(self):
        first = server.api_drill_finish({"seconds": 300, "solved": 4, "skipped": 1, "best_streak": 3})
        self.assertTrue(first["new_best"])
        second = server.api_drill_finish({"seconds": 300, "solved": 2, "skipped": 0, "best_streak": 2})
        self.assertFalse(second["new_best"])
        self.assertEqual(second["best"]["300"], 4)
        self.assertEqual(len(second["recent"]), 2)
        with self.assertRaises(server.ApiError):
            server.api_drill_finish({"seconds": 42, "solved": 1})


if __name__ == "__main__":
    unittest.main()
