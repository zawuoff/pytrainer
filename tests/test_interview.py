import unittest
from unittest import mock

import server
from pytrainer import ai, db, interview, progress


class InterviewTests(unittest.TestCase):
    def setUp(self):
        db.ex("DELETE FROM interviews")
        db.ex("DELETE FROM exercise_state")

    def test_full_interview(self):
        iv = server.api_interview_start({"minutes": 30})
        ex = progress.all_exercises()[iv["exercise"]["id"]]
        self.assertGreaterEqual(ex["difficulty"], 2)
        self.assertNotIn("solution", iv["exercise"])

        with self.assertRaises(server.ApiError):
            server.api_interview_followup(str(iv["id"]), {})          # nothing submitted yet

        r = server.api_interview_submit(str(iv["id"]), {"files": {"solution.py": ex["solution"]}, "seconds": 600})
        self.assertEqual(r["result"]["status"], "passed")
        self.assertEqual(db.q1("SELECT COUNT(*) AS n FROM attempts WHERE item_id=?", (ex["id"],))["n"], 0,
                         "interviews are not practice attempts")
        with self.assertRaises(server.ApiError):
            server.api_interview_submit(str(iv["id"]), {"files": {"solution.py": "x"}})

        questions = iter(["What is the complexity?", "Which edge case?", "What about a huge input?"])
        with mock.patch.object(ai, "complete", side_effect=lambda system, prompt, **kw: next(questions)) as ask:
            out = server.api_interview_followup(str(iv["id"]), {})
            self.assertEqual(out["transcript"][-1], {"role": "interviewer", "content": "What is the complexity?"})
            self.assertIn(ex["title"], ask.call_args.args[1])
            self.assertIn("10 of 30 minutes", ask.call_args.args[1])
            out = server.api_interview_followup(str(iv["id"]), {"answer": "Linear."})
            out = server.api_interview_followup(str(iv["id"]), {"answer": "Empty input."})
            self.assertFalse(out["done"])
            out = server.api_interview_followup(str(iv["id"]), {"answer": "Stream it."})
        self.assertTrue(out["done"])
        self.assertEqual([m["role"] for m in out["transcript"]], ["interviewer", "candidate"] * 3)

        report = {"scores": {"correctness": 5, "problem_solving": 4, "communication": 3, "code_quality": 4},
                  "verdict": "yes", "summary": "Solid.", "strengths": ["a"], "to_work_on": ["b"], "practice": "c"}
        with mock.patch.object(ai, "complete_json", return_value=report) as judge:
            got = server.api_interview_debrief(str(iv["id"]))
        self.assertEqual(got["debrief"]["verdict"], "yes")
        self.assertIn("CANDIDATE: Stream it.", judge.call_args.args[1])
        hist = server.api_interviews()["history"]
        self.assertEqual((hist[0]["tests"].split("/")[0] == hist[0]["tests"].split("/")[1], hist[0]["verdict"]), (True, "yes"))

    def test_bad_length_is_refused(self):
        with self.assertRaises(server.ApiError):
            server.api_interview_start({"minutes": 7})

    def test_long_interviews_prefer_hard_problems(self):
        from pytrainer import content
        for t in content.load()["topics"]:
            db.ex("INSERT OR REPLACE INTO topic_state(topic_id, placed, placed_at) VALUES(?,1,?)", (t["id"], db.now()))
        try:
            picks = {interview.pick(45)["difficulty"] for _ in range(10)}
            self.assertEqual(picks, {3})
        finally:
            db.ex("DELETE FROM topic_state")


if __name__ == "__main__":
    unittest.main()
