import json
import unittest
from datetime import datetime, timedelta

from pytrainer import content, db, progress, radar


def failed(*names, error=None, status="failed"):
    return {"status": status, "error": error,
            "tests": [{"name": n, "passed": False, "message": ""} for n in names]}


def record(item_id, result, days_ago=0):
    stamp = (datetime.now() - timedelta(days=days_ago)).isoformat(timespec="seconds")
    db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, duration_s, result, created_at) "
          "VALUES(?, 'practice', '{}', ?, 0, 1, 0, ?, ?)", (item_id, result["status"], json.dumps(result), stamp))


class ClassifyTests(unittest.TestCase):
    def test_words_in_check_names(self):
        self.assertEqual(radar._classify(failed("empty list returns zero"))[0][0], "empty")
        self.assertEqual(radar._classify(failed("input not modified and new list returned"))[0][0], "mutation")
        self.assertEqual(radar._classify(failed("text exactly at the limit is unchanged"))[0][0], "boundaries")
        self.assertEqual(radar._classify(failed("ties in title order"))[0][0], "order")

    def test_errors_and_timeouts(self):
        self.assertEqual(radar._classify(failed(error="SyntaxError in solution.py line 3"))[0][0], "syntax")
        self.assertEqual(radar._classify({"status": "timeout", "tests": []})[0][0], "slow")
        self.assertEqual(radar._classify(failed(error="Your file crashed while loading:\nKeyError: 'x'"))[0][0], "keys")

    def test_passed_checks_are_ignored(self):
        res = {"status": "failed", "tests": [{"name": "empty input", "passed": True, "message": ""}]}
        self.assertEqual(radar._classify(res), [])


class AnalyseTests(unittest.TestCase):
    def setUp(self):
        db.ex("DELETE FROM attempts")
        db.ex("DELETE FROM exercise_state")

    def test_recent_patterns_rank_first_and_feed_the_session(self):
        exs = [e for e in content.load()["exercises"].values() if not e.get("extra")][:6]
        for e in exs[:3]:
            record(e["id"], failed("empty list returns zero"))
            progress.save_state(progress.get_state(e["id"]) | {"status": "attempted", "attempts": 1})
        for e in exs[3:6]:
            record(e["id"], failed("ties in title order"), days_ago=60)
        out = radar.analyse()
        self.assertEqual([p["id"] for p in out["patterns"]][:2], ["empty", "order"])
        self.assertEqual(out["patterns"][0]["count"], 3)
        self.assertGreater(out["patterns"][0]["score"], 4 * out["patterns"][1]["score"], "old failures count much less")
        ids = [s["id"] for s in out["session"]]
        self.assertTrue({e["id"] for e in exs[:3]} <= set(ids))
        self.assertLessEqual(len(ids), radar.SESSION_SIZE)
        self.assertTrue(all(s["href"].startswith("#/step/") for s in out["session"]))

    def test_no_failures_no_patterns(self):
        out = radar.analyse()
        self.assertEqual(out["patterns"], [])


if __name__ == "__main__":
    unittest.main()
