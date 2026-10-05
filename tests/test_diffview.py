import unittest

from pytrainer import diffview, runner

TESTS = r'''
from solution import greet, nums, add, table
def test_greet():
    assert greet("ada") == "Hello, Ada!", "greeting is off"
def test_list():
    assert nums() == [1, 2, 3, 4]
def test_scalar_shown_in_message():
    got = add(2, 2)
    assert got == 5, f"expected 5, got {got}"
def test_types():
    expected = "4"
    assert expected == add(2, 2)
def test_long_output():
    assert table() == "\n".join(f"row {i}" for i in range(20))
def test_evaluated_once():
    calls = []
    def f():
        calls.append(1)
        return 1
    assert f() == 1
    assert len(calls) == 1, f"called {len(calls)} times"
def test_not_an_eq():
    assert add(1, 1) > 5, "too small"
'''

CODE = '''
def greet(n):
    return "Hello,  " + n.title() + "!"
def nums():
    return [1, 2, 4]
def add(a, b):
    return a + b
def table():
    return "\\n".join(f"row {i}" if i != 12 else "row twelve" for i in range(20))
'''


class DiffViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = runner.run_tests({"solution.py": CODE}, TESTS)
        cls.by_name = {t["name"]: t for t in r["tests"]}

    def test_whitespace_mistake_is_marked(self):
        d = self.by_name["greet"]["diff"]
        self.assertEqual(d["note"], "Only spaces, tabs or line breaks differ.")
        row = d["rows"][0]
        self.assertEqual(row["t"], "change")
        self.assertIn([" ", True], row["a"])
        self.assertEqual(self.by_name["greet"]["message"], "greeting is off", "the test's own message is kept")

    def test_values_not_in_the_message_get_a_diff(self):
        d = self.by_name["list"]["diff"]
        self.assertEqual(d["kind"], "repr")
        self.assertIn(["3, ", True], d["rows"][0]["e"])

    def test_short_values_already_in_the_message_get_none(self):
        self.assertNotIn("diff", self.by_name["scalar shown in message"])

    def test_expected_side_is_detected_and_types_noted(self):
        d = self.by_name["types"]["diff"]
        self.assertEqual(d["note"], "Different types: expected a str, your code gave an int.")
        self.assertEqual("".join(t for t, _ in d["rows"][0]["e"]), "'4'")

    def test_long_output_folds_unchanged_lines(self):
        rows = self.by_name["long output"]["diff"]["rows"]
        kinds = [r["t"] for r in rows]
        self.assertIn("change", kinds)
        self.assertIn("skip", kinds)
        self.assertLess(len(rows), 8)

    def test_rewriting_keeps_semantics(self):
        self.assertTrue(self.by_name["evaluated once"]["passed"], "each side of == must be evaluated exactly once")
        failed = self.by_name["not an eq"]
        self.assertFalse(failed["passed"])
        self.assertEqual(failed["message"], "too small")
        self.assertNotIn("diff", failed)

    def test_build_edge_cases(self):
        self.assertIsNone(diffview.build(None))
        self.assertIsNone(diffview.build({"expected": "x", "actual": "x", "kind": "text"}))
        d = diffview.build({"expected": "a\nb", "actual": "a\nb\nc", "kind": "text", "types": ["str", "str"]})
        self.assertEqual(d["rows"][-1]["t"], "extra")
        d = diffview.build({"expected": "Hi\n", "actual": "Hi", "kind": "text", "types": ["str", "str"]})
        self.assertEqual(d["note"], "Only the newlines at the end differ.")


if __name__ == "__main__":
    unittest.main()
