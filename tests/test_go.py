import unittest

import server
from pytrainer import content, db, go, progress, runner


class OnTheGoTests(unittest.TestCase):
    def setUp(self):
        for table in ("exercise_state", "attempts", "lesson_state", "topic_state", "library_opens", "submissions"):
            db.ex(f"DELETE FROM {table}")

    def reached(self):
        tp = progress.topic_progress()
        return {t for t, p in tp.items() if p["unlocked"] or p["attempted"] or p["cleared"]}

    def test_a_new_learner_gets_steps_from_reached_chapters_only(self):
        s = server.api_go()
        reached = self.reached()
        self.assertTrue(s["predict"], "the first chapter has predict steps")
        for item in s["predict"] + s["traceback"]:
            self.assertIn(item["topic"], reached)
            self.assertNotIn("solution", item)
            self.assertNotIn("tests", item)
            self.assertTrue(item["module"])
        self.assertTrue(all(i["mode"] == "predict" for i in s["predict"]))
        self.assertTrue(all(i["mode"] == "traceback" and i["traceback"] for i in s["traceback"]))
        self.assertEqual(s["cards"], [], "no chapter's Library is unlocked yet")
        self.assertEqual(s["reading"]["id"], content.load()["topics"][0]["id"])

    def test_unsolved_steps_come_first(self):
        first = server.api_go()["predict"][0]
        progress.save_state(progress.get_state(first["id"]) | {"status": "solved", "attempts": 1})
        s = go.session(server._traceback, seed=1)
        statuses = [i["status"] for i in s["predict"]]
        self.assertEqual(statuses, sorted(statuses, key=lambda st: st == "solved"))
        self.assertNotEqual(s["predict"][0]["id"], first["id"])

    def test_cards_come_only_from_unlocked_chapters(self):
        data = content.load()
        for e in data["topics_by_id"]["loops"]["exercise_ids"]:
            ex = data["exercises"][e]
            if ex.get("lesson") and ex["difficulty"] <= 1:
                progress.save_state(progress.get_state(e) | {"status": "solved", "attempts": 1})
        cards = server.api_go()["cards"]
        self.assertTrue(cards)
        self.assertEqual({c["id"] for c in cards}, {"loops"})
        ref = data["topics_by_id"]["loops"]["reference"]["cards"]
        self.assertTrue(all(c["syntax"] == ref[c["card"]]["syntax"] for c in cards))

    def test_answers_go_through_the_normal_check(self):
        item = server.api_go()["predict"][0]
        ex = content.load()["exercises"][item["id"]]
        out = runner.check_prediction(ex["code"], "")["_actual"]
        r = server.api_check(item["id"], {"answer": out, "duration_s": 20})
        self.assertEqual(r["result"]["status"], "passed")
        self.assertEqual(progress.get_state(item["id"])["status"], "solved")


if __name__ == "__main__":
    unittest.main()
