import http.client
import json
import threading
import unittest
from datetime import date, timedelta

import server
from pytrainer import achievements, content, db, progress


def first_step():
    return next(e for e in content.load()["exercises"].values()
                if e.get("mode", "function") == "function" and not e.get("extra") and e.get("topic") != "exam")


class AchievementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.httpd.daemon_threads = True
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        for table in ("achievements", "exercise_state", "attempts", "activity", "submissions", "drills"):
            db.ex(f"DELETE FROM {table}")

    def post(self, path, body):
        port = self.httpd.server_address[1]
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
        conn.request("POST", path, json.dumps(body), {"Host": f"127.0.0.1:{port}", "Content-Type": "application/json"})
        data = json.loads(conn.getresponse().read())
        conn.close()
        return data

    def test_ids_are_unique_and_stats_cover_every_achievement(self):
        ids = [a[0] for a in achievements.ACHIEVEMENTS]
        self.assertEqual(len(ids), len(set(ids)))
        stats = achievements.stats()
        for a in achievements.ACHIEVEMENTS:
            self.assertIn(a[4], stats, a[0])
            self.assertIn(a[1], achievements.GROUPS, a[0])

    def test_first_solve_is_awarded_once_through_the_api(self):
        ex = first_step()
        r = self.post(f"/api/exercise/{ex['id']}/check", {"files": {"solution.py": ex["solution"]}, "duration_s": 60})
        self.assertEqual(r["result"]["status"], "passed")
        self.assertIn("first-step", [a["id"] for a in r["awards"]])
        again = self.post(f"/api/exercise/{ex['id']}/check", {"files": {"solution.py": ex["solution"]}})
        self.assertNotIn("awards", again)
        # Non-rewarding routes never carry awards.
        self.assertNotIn("awards", self.post("/api/draft", {"item_id": ex["id"], "files": {}}))

    def test_overview_progress_and_secrets(self):
        ov = achievements.overview()
        self.assertEqual(ov["total"], len(achievements.ACHIEVEMENTS))
        owl = next(i for i in ov["items"] if i["id"] == "night-owl")
        self.assertEqual(owl["title"], "???")
        self.assertNotIn("value", owl)
        ten = next(i for i in ov["items"] if i["id"] == "ten-steps")
        self.assertEqual((ten["value"], ten["target"]), (0, 10))
        self.assertIsNone(ten["unlocked_at"])

    def test_night_owl_and_comeback(self):
        ex = first_step()
        db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?,?,?,?,?,?,?)",
              (ex["id"], "practice", "{}", "passed", 1, 1, "2026-01-05T02:30:00"))
        today = date.today()
        for d in (today - timedelta(days=20), today):
            db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES(?, 900, 0, 0)", (d.isoformat(),))
        new = {a["id"] for a in achievements.check()}
        self.assertTrue({"night-owl", "comeback"} <= new)
        owl = next(i for i in achievements.overview()["items"] if i["id"] == "night-owl")
        self.assertEqual(owl["title"], "Night owl")

    def test_unlocks_are_kept_when_the_evidence_goes(self):
        ex = first_step()
        progress.save_state(progress.get_state(ex["id"]) | {"status": "solved", "attempts": 1})
        self.assertIn("first-step", {a["id"] for a in achievements.check()})
        db.ex("DELETE FROM exercise_state")
        self.assertIn("first-step", achievements.unlocked())

    def test_stats_endpoint_summarises(self):
        st = server.api_stats()
        self.assertEqual(st["achievements"]["total"], len(achievements.ACHIEVEMENTS))


if __name__ == "__main__":
    unittest.main()
