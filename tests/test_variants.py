import unittest
from datetime import date
from unittest import mock

from pytrainer import ai, db, progress, variants

ORIGINAL = {
    "id": "demo-1", "title": "Count words", "difficulty": 1, "mode": "function", "topic": "demo",
    "prompt": "Write count_words(text).",
    "solution": "def count_words(text):\n    return len(text.split())\n",
    "tests": ("from solution import count_words\n\n"
              "def test_two():\n    assert count_words('a b') == 2\n\n"
              "def test_empty():\n    assert count_words('') == 0\n\n"
              "def test_spaces():\n    assert count_words('  a  ') == 1\n"),
}

GOOD = {
    "title": "Count tokens",
    "prompt": "Write count_tokens(reply).",
    "starter": "def count_tokens(reply):\n    ...\n",
    "solution": "def count_tokens(reply):\n    return len(reply.split())\n",
    "tests": ("from solution import count_tokens\n\n"
              "def test_three():\n    assert count_tokens('x y z') == 3\n\n"
              "def test_blank():\n    assert count_tokens('   ') == 0\n\n"
              "def test_newlines():\n    assert count_tokens('a\\nb') == 2\n"),
}


class ValidateTests(unittest.TestCase):
    def test_a_sound_changed_variant_passes(self):
        self.assertEqual(variants.validate(ORIGINAL, GOOD), "")

    def test_missing_keys_are_rejected(self):
        self.assertIn("missing keys", variants.validate(ORIGINAL, {"title": "x"}))

    def test_a_broken_reference_is_rejected(self):
        bad = dict(GOOD, solution="def count_tokens(reply):\n    return 0\n")
        self.assertIn("reference solution", variants.validate(ORIGINAL, bad))

    def test_a_starter_that_already_passes_is_rejected(self):
        bad = dict(GOOD, starter=GOOD["solution"])
        self.assertIn("starter", variants.validate(ORIGINAL, bad))

    def test_a_variant_the_old_answer_still_passes_is_rejected(self):
        same = dict(GOOD, tests=ORIGINAL["tests"], solution=ORIGINAL["solution"],
                    starter="def count_words(text):\n    ...\n")
        self.assertIn("nothing really changed", variants.validate(ORIGINAL, same))


class GenerateTests(unittest.TestCase):
    def test_a_rejected_variant_is_retried_with_the_reason(self):
        replies = [dict(GOOD, starter=GOOD["solution"]), GOOD]
        with mock.patch.object(ai, "complete_json", side_effect=replies) as call:
            v = variants.generate(ORIGINAL)
        self.assertEqual(v["title"], "Count tokens")
        self.assertEqual(v["based_on"], "demo-1")
        self.assertIn("rejected", call.call_args_list[1].args[1])

    def test_gives_up_after_the_last_try(self):
        with mock.patch.object(ai, "complete_json", return_value={"title": "x"}):
            with self.assertRaises(ai.AIError):
                variants.generate(ORIGINAL)


class WorkerTests(unittest.TestCase):
    def test_worker_prepares_due_reviews_once(self):
        st = progress.get_state("demo-1") | {"status": "solved", "next_review": date.today().isoformat()}
        progress.save_state(st)
        variants.drop("demo-1")
        with mock.patch.object(variants, "generate", return_value=GOOD | {"based_on": "demo-1"}) as gen:
            variants._work({"demo-1": ORIGINAL})
            variants._work({"demo-1": ORIGINAL})
        self.assertEqual(gen.call_count, 1)
        self.assertIn("demo-1", variants.ready_ids())
        variants.drop("demo-1")
        db.ex("DELETE FROM exercise_state WHERE exercise_id='demo-1'")

    def test_off_without_an_ai_connection(self):
        db.set_setting("ai", {"provider": "none", "model": ""})
        self.assertFalse(variants.enabled())
        self.assertFalse(variants.prepare({}))


if __name__ == "__main__":
    unittest.main()
