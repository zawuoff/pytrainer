import unittest
from datetime import date, timedelta

from pytrainer import srs

TODAY = date(2026, 1, 10)


def card(**kw):
    st = {"exercise_id": "lists-3", "attempts": 1, "hints_used": 0, "revealed": 0, "stability": None,
          "difficulty": None, "last_review": None, "next_review": None, "interval_days": 0, "lapses": 0}
    st.update(kw)
    return st


class FormulaTests(unittest.TestCase):
    def test_retrievability_is_ninety_percent_after_stability_days(self):
        self.assertAlmostEqual(srs.retrievability(12, 12), 0.9, places=6)
        self.assertEqual(srs.retrievability(0, 5), 1.0)

    def test_interval_equals_stability_at_ninety_percent_retention(self):
        self.assertEqual(srs.interval(10.0), 10)
        self.assertEqual(srs.interval(0.2), 1)
        self.assertEqual(srs.interval(10_000), srs.MAX_INTERVAL)

    def test_fuzz_is_small_and_stable_per_item(self):
        a, b = srs.interval(40, "a-1"), srs.interval(40, "a-1")
        self.assertEqual(a, b)
        self.assertTrue(38 <= a <= 42)

    def test_better_ratings_grow_stability_more(self):
        d, s, r = 5.0, 10.0, srs.retrievability(10, 10)
        hard, good, easy = (srs.next_stability(d, s, r, g) for g in (srs.HARD, srs.GOOD, srs.EASY))
        self.assertLess(s, hard)
        self.assertLess(hard, good)
        self.assertLess(good, easy)

    def test_failure_lowers_stability(self):
        self.assertLess(srs.next_stability(5.0, 30.0, 0.9, srs.AGAIN), 30.0)

    def test_difficulty_stays_in_range(self):
        d = 9.9
        for _ in range(20):
            d = srs.next_difficulty(d, srs.AGAIN)
        self.assertLessEqual(d, 10)
        for _ in range(50):
            d = srs.next_difficulty(d, srs.EASY)
        self.assertGreaterEqual(d, 1)


class FirstSolveTests(unittest.TestCase):
    def test_clean_first_try_is_scheduled_furthest(self):
        clean, retried, revealed = card(), card(attempts=3), card(attempts=4, revealed=1)
        for st in (clean, retried, revealed):
            srs.on_first_solve(st, TODAY)
        self.assertEqual(clean["interval_days"], 4)
        self.assertEqual(retried["interval_days"], 1)
        self.assertEqual(revealed["interval_days"], 1)
        self.assertEqual(clean["last_review"], TODAY.isoformat())
        self.assertEqual(clean["next_review"], (TODAY + timedelta(days=4)).isoformat())

    def test_hints_count_as_struggle(self):
        st = card(hints_used=2)
        srs.on_first_solve(st, TODAY)
        self.assertEqual(st["interval_days"], 1)


class ReviewTests(unittest.TestCase):
    def solved(self):
        st = card()
        srs.on_first_solve(st, TODAY)
        return st

    def test_successful_reviews_space_out(self):
        st, day, gaps = self.solved(), TODAY, []
        for _ in range(4):
            day = date.fromisoformat(st["next_review"])
            self.assertEqual(srs.on_review(st, True, 300, day), srs.GOOD)
            gaps.append(st["interval_days"])
        self.assertEqual(gaps, sorted(gaps))
        self.assertGreater(gaps[-1], 30)

    def test_fast_rebuild_counts_as_easy(self):
        a, b = self.solved(), self.solved()
        day = date.fromisoformat(a["next_review"])
        self.assertEqual(srs.on_review(a, True, 40, day), srs.EASY)
        srs.on_review(b, True, 400, day)
        self.assertGreater(a["interval_days"], b["interval_days"])

    def test_failure_keeps_it_due_and_only_first_check_of_the_day_is_rated(self):
        st = self.solved()
        day = date.fromisoformat(st["next_review"])
        self.assertEqual(srs.on_review(st, False, 100, day), srs.AGAIN)
        self.assertEqual(st["next_review"], day.isoformat())
        lowered = st["stability"]
        self.assertEqual(srs.on_review(st, False, 100, day), 0)
        self.assertEqual(srs.on_review(st, True, 100, day), 0)
        self.assertEqual(st["stability"], lowered)
        self.assertGreater(date.fromisoformat(st["next_review"]), day)

    def test_rows_from_the_old_fixed_schedule_are_picked_up(self):
        st = card(interval_days=16, next_review=(TODAY - timedelta(days=2)).isoformat(), lapses=1)
        self.assertEqual(srs.on_review(st, True, 200, TODAY), srs.GOOD)
        self.assertGreater(st["stability"], 16)
        self.assertGreater(st["interval_days"], 16)
        self.assertIsNotNone(st["difficulty"])


if __name__ == "__main__":
    unittest.main()
