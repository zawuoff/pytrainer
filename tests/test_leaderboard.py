import json
import unittest

import server
from pytrainer import capstone, content, db, leaderboard
from pytrainer.content import leaderboard as lb_data


def solution(pid):
    return content.load()["projects_by_id"][pid]["solution_files"]


class LeaderboardTests(unittest.TestCase):
    def setUp(self):
        db.ex("DELETE FROM submissions")
        db.ex("DELETE FROM leaderboard_runs")

    def pass_capstone(self, extra=""):
        for pid in capstone.STAGES:
            server.api_project_submit(pid, {"files": solution(pid)})
        files = dict(solution("capstone"))
        files["app.py"] += extra
        r = server.api_project_submit("capstone", {"files": files})
        self.assertEqual(r["result"]["status"], "passed")

    def test_needs_a_passing_capstone(self):
        with self.assertRaises(server.ApiError):
            server.api_leaderboard_run({})
        self.assertFalse(server.api_leaderboard()["ready"])

    def test_scores_dev_and_held_out_and_tracks_the_best(self):
        self.pass_capstone()
        first = server.api_leaderboard_run({})
        self.assertEqual(first["settings"], leaderboard.DEFAULTS)
        self.assertTrue(0 <= first["dev"] <= 100 and 0 <= first["test"] <= 100)
        self.assertGreaterEqual(first["test"], 50, "the reference solution should do reasonably well")
        self.assertTrue(first["new_best"])
        self.assertEqual(len(first["dev_rows"]), len(lb_data.DEV))

        self.pass_capstone('\nEVAL_SETTINGS = {"threshold": 0.45}\n')
        strict = server.api_leaderboard_run({})
        self.assertEqual(strict["settings"]["threshold"], 0.45)
        self.assertLess(strict["test"], first["test"], "refusing almost everything should score worse")
        self.assertFalse(strict["new_best"])
        over = server.api_leaderboard()
        self.assertEqual(over["best"], first["test"])
        self.assertEqual([r["test"] for r in over["runs"]], [strict["test"], first["test"]])
        self.assertNotIn("source", json.dumps(over["runs"]), "held-out answers are never sent to the page")


if __name__ == "__main__":
    unittest.main()
