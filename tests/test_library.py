import unittest

import server
from pytrainer import content, db, progress


def chapter(tid):
    return content.load()["topics_by_id"][tid]


def lesson_steps(tid):
    data = content.load()
    return [data["exercises"][e] for e in chapter(tid)["exercise_ids"]
            if data["exercises"][e].get("lesson") and data["exercises"][e]["difficulty"] <= 1
            and not data["exercises"][e].get("extra")]


class LibraryTests(unittest.TestCase):
    def setUp(self):
        for table in ("exercise_state", "attempts", "lesson_state", "topic_state", "library_opens", "submissions"):
            db.ex(f"DELETE FROM {table}")

    def solve(self, exs):
        for e in exs:
            progress.save_state(progress.get_state(e["id"]) | {"status": "solved", "attempts": 1})

    def test_finishing_a_chapters_lessons_unlocks_just_that_chapter(self):
        self.assertEqual(server.api_library()["unlocked"], 0)
        steps = lesson_steps("loops")
        self.solve(steps[:-1])
        self.assertFalse(progress.topic_progress()["loops"]["library_unlocked"], "every lesson step is needed")
        self.solve(steps[-1:])
        lib = server.api_library()
        self.assertEqual([e["id"] for e in lib["entries"]], ["loops"])
        self.assertEqual(lib["total"], len(content.load()["topics"]))

    def test_locked_chapters_are_not_sent_at_all(self):
        self.solve(lesson_steps("loops"))
        lib = server.api_library()
        self.assertTrue(all(e["unlocked"] and e["cards"] for e in lib["entries"]))
        self.assertNotIn("dicts", [e["id"] for e in lib["entries"]])
        with self.assertRaises(server.ApiError):
            server.api_library_entry("dicts")
        with self.assertRaises(server.ApiError):
            server.api_library_open("dicts", {"card": 0})

    def test_testing_out_of_a_chapter_unlocks_it(self):
        db.ex("INSERT INTO topic_state(topic_id, placed, placed_at) VALUES('strings', 1, 'x')")
        self.assertIn("strings", [e["id"] for e in server.api_library()["entries"]])

    def test_signals_rank_what_you_open_and_practise(self):
        self.solve(lesson_steps("loops") + lesson_steps("lists") + lesson_steps("dicts"))
        for _ in range(3):
            server.api_library_open("dicts", {"card": 1})
        server.api_library_open("lists", {"card": None})
        failed = next(e for e in content.load()["exercises"].values() if e.get("topic") == "loops")
        db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?,?,?,?,?,?,?)",
              (failed["id"], "practice", "{}", "failed", 0, 1, db.now()))
        lib = server.api_library()
        self.assertEqual(max(lib["boost"], key=lib["boost"].get), "dicts")
        self.assertIn("loops", lib["boost"])
        self.assertEqual(lib["recent"][0], {"id": "lists", "card": None, "at": lib["recent"][0]["at"]})
        self.assertEqual(lib["working_on"], ["loops"])
        # Chapters that aren't unlocked never get a boost, even when practised.
        locked = next(e for e in content.load()["exercises"].values() if e.get("topic") == "regex")
        db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, created_at) VALUES(?,?,?,?,?,?,?)",
              (locked["id"], "practice", "{}", "failed", 0, 1, db.now()))
        self.assertNotIn("regex", server.api_library()["boost"])


if __name__ == "__main__":
    unittest.main()
