import unittest
from unittest import mock

import server
from pytrainer import ai, content, db, progress


class ExplainBackTests(unittest.TestCase):
    def setUp(self):
        self.ex = next(e for e in content.load()["exercises"].values() if e.get("mode", "function") == "function"
                       and e["difficulty"] >= 1)
        db.ex("DELETE FROM explanations")
        db.ex("DELETE FROM exercise_state WHERE exercise_id=?", (self.ex["id"],))
        self.body = {"item_id": self.ex["id"], "files": {"solution.py": self.ex["solution"]},
                     "text": "It loops over every item once and keeps a running total, so empty input gives 0."}

    def test_needs_a_solved_step_and_a_real_explanation(self):
        with self.assertRaises(server.ApiError):
            server.api_explain_back(self.body)
        progress.save_state(progress.get_state(self.ex["id"]) | {"status": "solved"})
        with self.assertRaises(server.ApiError):
            server.api_explain_back(self.body | {"text": "it works"})

    def test_graded_and_remembered(self):
        progress.save_state(progress.get_state(self.ex["id"]) | {"status": "solved"})
        reply = {"score": 9, "verdict": "got it", "feedback": "Clear.", "right": ["running total"], "missing": [],
                 "misconception": None}
        with mock.patch.object(ai, "complete_json", return_value=reply) as call:
            r = server.api_explain_back(self.body)
        self.assertEqual(r["result"]["score"], 5, "scores are clamped to 1-5")
        self.assertIn("running total", call.call_args.args[1])
        self.assertIn(self.ex["title"], call.call_args.args[1])
        again = server.api_exercise(self.ex["id"])["explain_back"]
        self.assertEqual((again["text"], again["result"]["verdict"]), (self.body["text"], "got it"))


if __name__ == "__main__":
    unittest.main()
