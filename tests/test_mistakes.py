import json
import unittest
from unittest import mock

import server
from pytrainer import ai, content, db, mistakes, progress

GOOD = {"title": "Average of nothing", "topic": "functions", "difficulty": 2, "targets": "empty inputs",
        "prompt": "Write mean(xs); [] gives 0.0.", "starter": "def mean(xs):\n    ...\n",
        "solution": "def mean(xs):\n    return sum(xs) / len(xs) if xs else 0.0\n",
        "tests": ("from solution import mean\n\ndef test_a():\n    assert mean([2, 4]) == 3\n\n"
                  "def test_empty():\n    assert mean([]) == 0.0\n\ndef test_one():\n    assert mean([5]) == 5\n")}
BROKEN = dict(GOOD, title="Broken", solution="def mean(xs):\n    return 1\n")


class MistakeDrillTests(unittest.TestCase):
    def setUp(self):
        db.ex("DELETE FROM attempts")
        db.ex("DELETE FROM custom_exercises")
        db.ex("DELETE FROM settings WHERE key='mistake_drill'")

    def fail_one(self):
        ex = next(e for e in content.load()["exercises"].values() if e.get("mode", "function") == "function"
                  and not e.get("extra"))
        progress.record_attempt(ex, {"solution.py": "def x(): pass"},
                                {"status": "failed", "passed": 0, "total": 1, "error": None,
                                 "tests": [{"name": "empty list", "passed": False, "message": "got None"}]}, "practice", 10)
        return ex

    def test_needs_failures(self):
        with self.assertRaises(server.ApiError):
            server.api_mistake_drill({})

    def test_keeps_only_valid_exercises_and_remembers_the_drill(self):
        ex = self.fail_one()
        reply = {"summary": "You forget empty inputs.", "exercises": [GOOD, BROKEN]}
        with mock.patch.object(ai, "complete_json", return_value=reply) as call:
            drill = server.api_mistake_drill({})
        self.assertIn(ex["title"], call.call_args.args[1], "the prompt carries the failed task")
        self.assertIn("got None", call.call_args.args[1])
        self.assertEqual([s["title"] for s in drill["steps"]], ["Average of nothing"])
        saved = progress.all_exercises()[drill["steps"][0]["id"]]
        self.assertTrue(saved["generated"] and saved["from_mistakes"])
        self.assertEqual(saved["topic"], "functions")
        radar = server.api_radar()
        self.assertEqual(radar["mistake_drill"]["summary"], "You forget empty inputs.")
        self.assertEqual(radar["mistakes"], 1)

    def test_all_invalid_is_an_ai_error(self):
        self.fail_one()
        with mock.patch.object(ai, "complete_json", return_value={"summary": "x", "exercises": [BROKEN]}):
            with self.assertRaises(ai.AIError):
                mistakes.make_drill()


if __name__ == "__main__":
    unittest.main()
