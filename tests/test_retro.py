import json
import unittest
from datetime import datetime, timedelta

import server
from pytrainer import content, db, retro


def stamp(days_ago):
    return (datetime.now() - timedelta(days=days_ago)).isoformat(timespec="seconds")


class LookBackTests(unittest.TestCase):
    def setUp(self):
        for table in ("exercise_state", "attempts", "retros"):
            db.ex(f"DELETE FROM {table}")
        exs = content.load()["exercises"].values()
        self.ex = next(e for e in exs if e.get("mode", "function") == "function" and e["difficulty"] >= 2
                       and e.get("topic") != "exam" and len(e["solution"].splitlines()) >= 4)

    def passed(self, days_ago, code=None, kind="practice", item=None):
        code = code or self.ex["solution"]
        return db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?,?,?,?,?,?,?)",
                     (item or self.ex["id"], kind, json.dumps({"solution.py": code}), "passed", 1, 1, stamp(days_ago)))

    def test_only_code_from_weeks_ago_comes_back(self):
        self.assertIsNone(server.api_retro()["next_at"])
        self.passed(3)
        r = server.api_retro()
        self.assertIsNone(r["pick"])
        self.assertEqual(r["next_at"], (datetime.now() + timedelta(days=11)).date().isoformat())
        old = self.passed(30, code=self.ex["solution"] + "\n# then\n")
        self.passed(20, kind="review", code="x = 1\ny = 2\nz = 3\n")    # a review rebuild isn't the first version
        pick = server.api_retro()["pick"]
        self.assertEqual(pick["id"], self.ex["id"])
        self.assertEqual(pick["attempt"], old)
        self.assertIn("# then", pick["files"]["solution.py"])
        self.assertGreaterEqual(pick["days_ago"], 30)
        self.assertNotIn("solution", pick)

    def test_rewrite_is_checked_but_not_recorded(self):
        self.passed(30)
        before = db.q1("SELECT COUNT(*) AS n FROM attempts")["n"]
        r = server.api_retro_check(self.ex["id"], {"files": {"solution.py": self.ex["solution"]}})
        self.assertEqual(r["result"]["status"], "passed")
        self.assertEqual(db.q1("SELECT COUNT(*) AS n FROM attempts")["n"], before)

    def test_saving_compares_and_rests_the_step(self):
        old = self.passed(30)
        new = self.ex["solution"].rstrip() + "\n\n# clearer now\n"
        r = server.api_retro_save(self.ex["id"], {"attempt": old, "files": {"solution.py": new}, "notes": "names", "passed": True})
        self.assertTrue(r["rewritten"])
        self.assertTrue(any(row["t"] in ("extra", "change") for row in r["diff"]["rows"]))
        self.assertIsNone(server.api_retro()["pick"], "a step rests after you look back on it")
        hist = server.api_retro()["history"]
        self.assertEqual(hist[0]["notes"], "names")
        self.assertTrue(hist[0]["rewritten"])
        kept = server.api_retro_save(self.ex["id"], {"attempt": old, "notes": "fine as is"})
        self.assertFalse(kept["rewritten"])
        self.assertIsNone(kept["diff"])

    def test_old_code_must_be_the_learners_own_attempt(self):
        old = self.passed(30)
        with self.assertRaises(server.ApiError):
            server.api_retro_save("some-other-step", {"attempt": old, "notes": ""})
        other = next(e for e in content.load()["exercises"].values() if e["id"] != self.ex["id"])
        with self.assertRaises(server.ApiError):
            server.api_retro_save(other["id"], {"attempt": old, "notes": ""})

    def test_skip_moves_to_the_next_one(self):
        self.passed(30)
        other = next(e for e in content.load()["exercises"].values() if e["id"] != self.ex["id"]
                     and e.get("mode", "function") == "function" and e.get("topic") != "exam"
                     and len(e["solution"].splitlines()) >= 4)
        self.passed(40, code=other["solution"], item=other["id"])
        first = server.api_retro()["pick"]["id"]
        second = server.api_retro_pick({"skip": [first]})["pick"]["id"]
        self.assertNotEqual(first, second)
        self.assertIsNone(server.api_retro_pick({"skip": [first, second]})["pick"])
        self.assertEqual(retro.pick([first, second])[1], 2)


if __name__ == "__main__":
    unittest.main()
