import json
import unittest

import server
from pytrainer import content, db, insights, progress


class InsightsTests(unittest.TestCase):
    def setUp(self):
        for table in ("exercise_state", "attempts", "chats"):
            db.ex(f"DELETE FROM {table}")
        exs = [e for e in content.load()["exercises"].values() if e.get("mode", "function") == "function"
               and e.get("topic") != "exam"]
        self.a, self.b, self.c = exs[0], exs[1], exs[2]

    def check(self, ex, status, failing=None, error=None, kind="practice"):
        tests = [{"name": failing, "passed": False, "message": ""}] if failing else []
        result = {"status": status, "tests": tests, "error": error, "passed": 0 if failing or error else 1, "total": 1}
        db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, result, created_at) VALUES(?,?,?,?,?,?,?,?)",
              (ex["id"], kind, "{}", status, result["passed"], 1, json.dumps(result), db.now()))
        st = progress.get_state(ex["id"])
        if status == "passed":
            st |= {"status": "solved"}
        elif st["status"] != "solved":
            st |= {"status": "attempted"}
        progress.save_state(st)

    def test_steps_rank_by_trouble(self):
        for _ in range(3):
            self.check(self.a, "failed", failing="handles empty input")
        self.check(self.a, "error", error="Traceback...\nKeyError: 'x'")
        self.check(self.a, "passed")
        self.check(self.a, "failed", failing="later regression")   # after the solve: not counted
        progress.save_state(progress.get_state(self.a["id"]) | {"hints_used": 2, "revealed": 1})
        self.check(self.b, "passed")
        self.check(self.c, "failed", failing="returns a list")
        self.check(self.c, "failed", failing="returns a list", kind="review")    # only practice counts
        db.ex("INSERT INTO chats(item_id, messages, updated_at) VALUES(?,?,?)",
              (self.c["id"], json.dumps([{"role": "learner", "content": "?"}, {"role": "tutor", "content": "!"}]), db.now()))
        rows = {r["id"]: r for r in insights.steps()}
        a, b, c = rows[self.a["id"]], rows[self.b["id"]], rows[self.c["id"]]
        self.assertEqual((a["fails"], a["hints"], a["revealed"], a["solved"]), (4, 2, True, True))
        self.assertEqual(a["top_failure"], "handles empty input")
        self.assertEqual(a["top_failure_n"], 3)
        self.assertEqual(a["trouble"], 4 + 2 * 2 + 4)
        self.assertTrue(b["first_try"])
        self.assertEqual(b["trouble"], 0)
        self.assertEqual((c["fails"], c["tutor"], c["solved"], c["checks"]), (1, 1, False, 1))
        self.assertEqual(c["trouble"], 1 + 1 + 3)
        self.assertEqual([r["id"] for r in insights.steps()][:2], [self.a["id"], self.c["id"]])

    def test_report_totals_and_chapters(self):
        self.check(self.a, "failed", failing="x")
        self.check(self.a, "passed")
        self.check(self.b, "passed")
        rep = server.api_insights()
        self.assertEqual(rep["totals"]["solved"], 2)
        self.assertEqual(rep["totals"]["fails_per_solve"], 0.5)
        self.assertEqual(rep["totals"]["first_try"], 0.5)
        chapter = next(c for c in rep["chapters"] if c["id"] == self.a["topic"])
        self.assertGreaterEqual(chapter["tried"], 1)

    def test_error_and_timeout_names(self):
        self.assertEqual(insights._failure(json.dumps({"error": "Traceback\nTypeError: bad"}), "error"), "TypeError")
        self.assertEqual(insights._failure("{}", "timeout"), "time limit")
        self.assertIsNone(insights._failure("not json", "failed"))


if __name__ == "__main__":
    unittest.main()
