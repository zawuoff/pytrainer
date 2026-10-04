import unittest

import server
from pytrainer import content, db


class TracebackStepTests(unittest.TestCase):
    ID = "dicts-tb1"   # the KeyError surfaces on line 5; the typo is on line 2

    def setUp(self):
        db.ex("DELETE FROM exercise_state WHERE exercise_id=?", (self.ID,))

    def test_the_step_shows_a_real_traceback_but_not_the_answer(self):
        d = server.api_exercise(self.ID)
        self.assertIn("Traceback", d["traceback"])
        self.assertIn("KeyError", d["traceback"])
        self.assertIn('File "solution.py", line 5', d["traceback"])
        self.assertNotIn("answer_line", d["exercise"])
        self.assertEqual(d["checks"], [])

    def test_clicking_where_it_surfaced_explains_the_difference(self):
        r = server.api_check(self.ID, {"answer": 5})
        self.assertEqual(r["result"]["status"], "failed")
        self.assertIn("surfaced", r["result"]["tests"][0]["message"])

    def test_the_line_to_change_passes_and_explains(self):
        r = server.api_check(self.ID, {"answer": 2})
        self.assertEqual(r["result"]["status"], "passed")
        self.assertIn("temprature", r["result"]["explanation"])
        self.assertIn("temperature", r["reference"])

    def test_no_line_picked_is_refused(self):
        with self.assertRaises(server.ApiError):
            server.api_check(self.ID, {})

    def test_running_is_locked_until_answered(self):
        with self.assertRaises(server.ApiError):
            server.api_run(self.ID, {})


if __name__ == "__main__":
    unittest.main()
