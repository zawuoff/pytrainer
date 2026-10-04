import unittest

import server
from pytrainer import content, db, progress, xp


def steps(n, difficulty):
    return [e for e in content.load()["exercises"].values()
            if e["difficulty"] == difficulty and not e.get("extra") and e.get("topic") != "exam"][:n]


class LevelMathTests(unittest.TestCase):
    def test_thresholds_and_levels(self):
        self.assertEqual([xp.threshold(n) for n in (1, 2, 3, 10)], [0, 100, 300, 4500])
        for total, level in [(0, 1), (99, 1), (100, 2), (299, 2), (300, 3), (4499, 9), (4500, 10), (10**7, 447)]:
            self.assertEqual(xp.level_for(total), level, total)
        self.assertEqual(xp.title(1), "Beginner")
        self.assertEqual(xp.title(12), "Practitioner")

    def test_summary_fields(self):
        s = xp.summary(350)
        self.assertEqual((s["level"], s["into_level"], s["level_size"]), (3, 50, 300))
        self.assertEqual(s["next_title"], "Apprentice")


class XPTests(unittest.TestCase):
    def setUp(self):
        for table in ("exercise_state", "attempts", "activity", "submissions", "achievements", "settings",
                      "lab_state", "drills", "interviews", "explanations"):
            db.ex(f"DELETE FROM {table}")

    def test_breakdown_rewards_difficulty_clean_tries_and_halves_revealed(self):
        easy, hard = steps(1, 1)[0], steps(1, 3)[0]
        revealed = steps(2, 2)[1]
        progress.save_state(progress.get_state(easy["id"]) | {"status": "solved", "first_try": 1, "attempts": 1})
        progress.save_state(progress.get_state(hard["id"]) | {"status": "solved", "first_try": 0, "attempts": 3})
        progress.save_state(progress.get_state(revealed["id"]) | {"status": "solved", "revealed": 1, "first_try": 1})
        self.assertEqual(xp.breakdown()["steps"], (10 + 5) + 30 + 10)

    def test_projects_days_and_reviews(self):
        db.ex("INSERT INTO submissions(project_id, files, result, created_at) VALUES('chunker', '{}', '{\"status\": \"passed\"}', 'x')")
        db.ex("INSERT INTO submissions(project_id, files, result, created_at) VALUES('capstone', '{}', '{\"status\": \"passed\"}', 'x')")
        db.ex("INSERT INTO submissions(project_id, files, result, created_at) VALUES('chunker', '{}', '{\"status\": \"failed\"}', 'x')")
        db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES('2026-01-01', 700, 0, 0), ('2026-01-02', 30, 0, 0)")
        db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES('a', 'review', '{}', 'passed', 1, 1, 'x')")
        b = xp.breakdown()
        self.assertEqual(b["projects"], xp.PROJECT + xp.CAPSTONE)
        self.assertEqual(b["days"], xp.ACTIVE_DAY)
        self.assertEqual(b["reviews"], xp.REVIEW)

    def test_gains_start_from_a_baseline_and_report_level_ups(self):
        self.assertIsNone(xp.gained(), "the first call only sets the baseline")
        for e in steps(4, 3):  # 4 hard steps, clean: 4 * 35 = 140 XP -> level 2
            progress.save_state(progress.get_state(e["id"]) | {"status": "solved", "first_try": 1, "attempts": 1})
        g = xp.gained()
        self.assertEqual(g["gained"], 140)
        self.assertTrue(g["level_up"])
        self.assertEqual(g["level"], 2)
        self.assertIsNone(xp.gained(), "nothing new since the last call")

    def test_state_sets_the_baseline_so_the_first_solve_counts(self):
        server.api_state()
        e = steps(1, 1)[0]
        r = server.api_check(e["id"], {"files": {"solution.py": e["solution"]}, "duration_s": 30})
        self.assertEqual(r["result"]["status"], "passed")
        rewards = server._rewards()
        self.assertGreaterEqual(rewards["xp_gain"]["gained"], 15)
        self.assertIn("first-step", [a["id"] for a in rewards["awards"]])

    def test_stats_include_breakdown(self):
        st = server.api_stats()
        self.assertEqual(st["xp"]["total"], sum(st["xp"]["breakdown"].values()))


if __name__ == "__main__":
    unittest.main()
