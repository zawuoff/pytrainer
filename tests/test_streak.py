import unittest
from datetime import date, timedelta

import server
from pytrainer import db, progress


class StreakFreezeTests(unittest.TestCase):
    def setUp(self):
        db.ex("DELETE FROM activity")
        db.ex("DELETE FROM settings WHERE key='streak_freezes'")

    def days(self, pattern):
        """`pattern` is one char per day ending today: '#' active, '.' missed."""
        start = date.today() - timedelta(days=len(pattern) - 1)
        for i, ch in enumerate(pattern):
            if ch == "#":
                db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES(?, 900, 0, 0)",
                      ((start + timedelta(days=i)).isoformat(),))

    def test_plain_streak_without_freezes_earned(self):
        self.days("###.##")
        st = progress.streak()
        self.assertEqual((st["current"], st["best"], st["freezes"]), (2, 3, 0))
        self.assertEqual(st["next_freeze_in"], 5)

    def test_a_week_earns_a_freeze_that_covers_a_missed_day(self):
        self.days("#######.##")
        st = progress.streak()
        self.assertEqual(st["current"], 9, "the frozen day keeps the streak but doesn't add to it")
        self.assertEqual(st["freezes"], 0, "the freeze was spent")
        self.assertEqual(len(st["frozen_days"]), 1)
        self.assertFalse(st["saved_yesterday"])

    def test_two_missed_days_with_one_freeze_break_the_streak(self):
        self.days("#######..##")
        st = progress.streak()
        self.assertEqual((st["current"], st["best"]), (2, 7))

    def test_freezes_are_capped(self):
        self.days("#" * 30)
        st = progress.streak()
        self.assertEqual(st["freezes"], progress.MAX_FREEZES)

    def test_today_is_not_judged_until_it_ends(self):
        self.days("#######" + ".")
        st = progress.streak()
        self.assertEqual((st["current"], st["freezes"]), (7, 1), "an inactive today neither spends a freeze nor breaks the streak")
        self.assertFalse(st["today_active"])

    def test_saved_yesterday_and_heatmap_mark(self):
        self.days("#######.#")  # a week, yesterday missed, today active
        st = progress.streak()
        self.assertTrue(st["saved_yesterday"])
        self.assertEqual(st["current"], 8)
        heat = {d["day"]: d for d in progress.heatmap(10)}
        self.assertTrue(heat[(date.today() - timedelta(days=1)).isoformat()]["frozen"])

    def test_can_be_turned_off(self):
        self.days("#######.##")
        server.api_settings({"streak_freezes": False})
        st = progress.streak()
        self.assertEqual((st["current"], st["freezes"], st["freezes_on"]), (2, 0, False))
        self.assertFalse(server.api_state()["settings"]["streak_freezes"])


if __name__ == "__main__":
    unittest.main()
