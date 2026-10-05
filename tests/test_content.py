import unittest

from pytrainer import content, db, progress


class ExtraStepTests(unittest.TestCase):
    def test_extras_come_last_in_their_chapter(self):
        data = content.load()
        extras = [e for e in data["exercises"].values() if e.get("extra")]
        self.assertGreaterEqual(len(extras), 13)
        for t in data["topics"]:
            flags = [bool(data["exercises"][e].get("extra")) for e in t["exercise_ids"]]
            self.assertEqual(flags, sorted(flags), f"{t['id']}: extra steps must come after the path")

    def test_extras_never_change_mastery(self):
        before = progress.topic_progress()["evals"]
        st = progress.get_state("evals-wt1") | {"status": "solved"}
        progress.save_state(st)
        after = progress.topic_progress()["evals"]
        self.assertEqual((before["mastery"], before["total"]), (after["mastery"], after["total"]))
        db.ex("DELETE FROM exercise_state WHERE exercise_id='evals-wt1'")

    def test_public_exercise_marks_extras(self):
        ex = content.public_exercise(content.load()["exercises"]["evals-wt1"])
        self.assertTrue(ex["extra"])
        self.assertNotIn("impl", ex)
        self.assertNotIn("mutants", ex)


if __name__ == "__main__":
    unittest.main()
