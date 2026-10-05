import unittest
from datetime import date, timedelta
from unittest import mock

import server
from pytrainer import content, db, progress, recap


def some_steps(n):
    return [e for e in content.load()["exercises"].values()
            if e["difficulty"] == 2 and not e.get("extra") and e.get("topic") != "exam"][:n]


class RecapTests(unittest.TestCase):
    def setUp(self):
        for table in ("activity", "attempts", "exercise_state", "submissions", "achievements", "lab_state", "settings"):
            db.ex(f"DELETE FROM {table}")
        self.last = recap.week_start(date.today() - timedelta(days=7))

    def day(self, offset):
        return (self.last + timedelta(days=offset)).isoformat()

    def test_last_week_numbers_and_comparison(self):
        a, b = some_steps(2)
        db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES(?, 1800, 2, 3), (?, 300, 0, 1), (?, 600, 0, 0)",
              (self.day(0), self.day(3), self.day(-3)))
        for ex, fails in ((a, 3), (b, 0)):
            for _ in range(fails):
                db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?, 'practice', '{}', 'failed', 0, 1, ?)",
                      (ex["id"], self.day(0) + "T10:00:00"))
            db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?, 'practice', '{}', 'passed', 1, 1, ?)",
                  (ex["id"], self.day(0) + "T11:00:00"))
            progress.save_state(progress.get_state(ex["id"]) | {"status": "solved", "solved_at": self.day(0) + "T11:00:00",
                                                                 "first_try": int(fails == 0), "attempts": fails + 1})
        db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?, 'review', '{}', 'passed', 1, 1, ?)",
              (a["id"], self.day(5) + "T09:00:00"))
        r = server.api_recap()
        self.assertEqual(r["start"], self.last.isoformat())
        self.assertEqual(r["minutes"], 35)
        self.assertEqual(r["active_days"], 1)
        self.assertEqual((r["solved"], r["clean"], r["reviews"]), (2, 1, 1))
        self.assertEqual(r["previous"]["minutes"], 10)
        self.assertEqual(r["toughest"]["id"], a["id"])
        self.assertEqual(r["toughest"]["fails"], 3)
        self.assertEqual(r["best_day"]["name"], "Mon")
        self.assertEqual(r["xp"], 20 + 25 + 5 + 10)  # two medium steps (one clean), a review, one active day
        self.assertIsNotNone(r["top_chapter"])
        self.assertIn("2 steps solved", r["text"])
        self.assertIn("Toughest win", r["text"])
        self.assertIsNotNone(r["next"])
        self.assertFalse(r["empty"])

    def test_empty_and_future_weeks(self):
        old = server.api_recap((self.last - timedelta(days=70)).isoformat())
        self.assertTrue(old["empty"])
        self.assertIsNone(old["next"])
        with self.assertRaises(server.ApiError):
            server.api_recap((date.today() + timedelta(days=14)).isoformat())
        with self.assertRaises(server.ApiError):
            server.api_recap("2026-13-40")
        this_week = server.api_recap(date.today().isoformat())
        self.assertTrue(this_week["is_current"])

    def test_projects_count_in_the_week_they_first_passed(self):
        db.ex("INSERT INTO submissions(project_id, files, result, created_at) VALUES('chunker', '{}', '{\"status\": \"passed\"}', ?)",
              (self.day(2) + "T12:00:00",))
        db.ex("INSERT INTO submissions(project_id, files, result, created_at) VALUES('chunker', '{}', '{\"status\": \"passed\"}', ?)",
              (self.day(9) + "T12:00:00",))
        self.assertEqual([p["id"] for p in server.api_recap()["projects"]], ["chunker"])
        self.assertEqual(server.api_recap(self.day(7))["projects"], [])

    def test_banner_shows_early_in_the_week_after_a_busy_week(self):
        db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES(?, 60, 0, 1)", (self.day(1),))
        monday = self.last + timedelta(days=7)

        class Monday(date):
            @classmethod
            def today(cls):
                return monday

        class Friday(date):
            @classmethod
            def today(cls):
                return monday + timedelta(days=4)

        with mock.patch.object(recap, "date", Monday):
            self.assertEqual(recap.banner(), {"week": self.last.isoformat(), "ready": True})
        with mock.patch.object(recap, "date", Friday):
            self.assertFalse(recap.banner()["ready"])


if __name__ == "__main__":
    unittest.main()
