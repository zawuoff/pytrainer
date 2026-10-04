import unittest

from pytrainer import tracer


def events(trace):
    return [(s["event"], s["file"], s["line"]) for s in trace["steps"]]


def variables(step, frame=-1):
    return {name: value for name, _type, value in step["stack"][frame]["vars"]}


class TraceTests(unittest.TestCase):
    def test_loop_records_each_line_with_variables_and_output(self):
        t = tracer.trace_code({"solution.py": "total = 0\nfor n in [1, 2, 3]:\n    total += n\nprint(total)\n"})
        self.assertIsNone(t["error"])
        self.assertEqual(t["stdout"], "6\n")
        lines = [s["line"] for s in t["steps"] if s["event"] == "line"]
        self.assertEqual(lines, [1, 2, 3, 2, 3, 2, 3, 2, 4])
        third = [s for s in t["steps"] if s["event"] == "line"][3]
        self.assertEqual(variables(third), {"total": "1", "n": "1"})
        last = t["steps"][-1]
        self.assertEqual(last["event"], "return")
        self.assertEqual(t["stdout"][:last["out"]], "6\n")

    def test_call_steps_into_the_function_and_returns_its_value(self):
        src = "def add(a, b):\n    c = a + b\n    return c\n"
        t = tracer.trace_code({"solution.py": src}, call="add(2, 3)")
        self.assertEqual(t["result"], "5")
        call = next(s for s in t["steps"] if s["event"] == "call")
        self.assertEqual((call["func"], variables(call)), ("add", {"a": "2", "b": "3"}))
        ret = next(s for s in t["steps"] if s["event"] == "return" and s["func"] == "add")
        self.assertEqual(ret["value"], "5")
        self.assertEqual([f["name"] for f in ret["stack"]], ["Global", "add()"])
        self.assertIn(("line", "call", 1), events(t))

    def test_uncaught_exception_is_a_step_and_an_error(self):
        t = tracer.trace_code({"solution.py": "def f(x):\n    return 1 / x\nprint(f(0))\n"})
        self.assertEqual(t["error"], "ZeroDivisionError: division by zero (line 2)")
        exc = [s for s in t["steps"] if s["event"] == "exception"]
        self.assertEqual(len(exc), 1)
        self.assertEqual(exc[0]["line"], 2)

    def test_infinite_loop_is_cut_short(self):
        t = tracer.trace_code({"solution.py": "while True:\n    x = 1\n"}, max_steps=50)
        self.assertTrue(t["truncated"])
        self.assertEqual(len(t["steps"]), 50)

    def test_input_reads_from_stdin(self):
        t = tracer.trace_code({"solution.py": "name = input()\nprint('hi', name)\n"}, stdin="Ada\n")
        self.assertEqual(t["stdout"], "hi Ada\n")

    def test_syntax_error_is_reported_without_steps(self):
        t = tracer.trace_code({"solution.py": "def f(:\n    pass\n"})
        self.assertEqual(t["steps"], [])
        self.assertIn("SyntaxError (line 1)", t["error"])

    def test_library_code_is_not_traced_but_callbacks_are(self):
        t = tracer.trace_code({"solution.py": "xs = sorted([3, 1, 2], key=lambda v: -v)\n"})
        funcs = {s["func"] for s in t["steps"]}
        self.assertEqual(funcs, {"<module>", "<lambda>"})

    def test_long_reprs_are_shortened(self):
        t = tracer.trace_code({"solution.py": "s = 'x' * 1000\n"})
        value = variables(t["steps"][-1])["s"]
        self.assertLessEqual(len(value), 120)
        self.assertTrue(value.endswith("…"))


class SuggestCallTests(unittest.TestCase):
    SOLUTION = "import re\nPREFIXES = ('a', 'b')\n\ndef clean(text, limit=3):\n    return text[:limit]\n"

    def test_picks_a_call_with_literal_arguments(self):
        tests = "from solution import clean\n\ndef test_a():\n    assert clean('hello there', 4) == 'hell'\n"
        self.assertEqual(tracer.suggest_call(self.SOLUTION, tests), "clean('hello there', 4)")

    def test_inlines_names_bound_to_literals(self):
        tests = ("from solution import clean\nWORD = 'hello'\n\n"
                 "def test_a():\n    text = [WORD, 'x']\n    assert clean(text, limit=1) == ['hello']\n")
        self.assertEqual(tracer.suggest_call(self.SOLUTION, tests), "clean(['hello', 'x'], limit=1)")

    def test_module_style_calls_are_unwrapped(self):
        tests = "import solution\n\ndef test_a():\n    assert solution.clean('abc') == 'abc'\n"
        self.assertEqual(tracer.suggest_call(self.SOLUTION, tests), "clean('abc')")

    def test_skips_calls_with_computed_arguments(self):
        tests = "from solution import clean\n\ndef test_a():\n    assert clean(make()) == ''\n"
        self.assertEqual(tracer.suggest_call(self.SOLUTION, tests), "")

    def test_scripts_need_no_call(self):
        self.assertEqual(tracer.suggest_call("print('hi')\n", "def test_a():\n    pass\n"), "")


if __name__ == "__main__":
    unittest.main()
