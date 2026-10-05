import unittest
from unittest import mock

import server
from pytrainer import assist


def names(code, line=None, col=None):
    lines = code.split("\n")
    line = line or len(lines)
    col = len(lines[line - 1]) if col is None else col
    with mock.patch.object(assist, "_jedi", return_value=None):  # the stdlib engine, even if Jedi is installed
        r = assist.complete(code, line, col)
    return r["prefix"], [i["text"] for i in r["items"]]


class DiagnoseTests(unittest.TestCase):
    def test_syntax_error_position(self):
        [p] = assist.diagnose("for i in range(3)\n    print(i)\n")
        self.assertEqual((p["line"], p["severity"]), (1, "error"))
        self.assertIn("SyntaxError", p["message"])
        self.assertGreaterEqual(p["end_col"], p["col"] + 1)

    def test_undefined_names_with_suggestion(self):
        probs = assist.diagnose("def area(width, height):\n    return width * heigth\n")
        self.assertEqual(len(probs), 1)
        self.assertEqual((probs[0]["line"], probs[0]["severity"]), (2, "warning"))
        self.assertIn("Did you mean 'height'", probs[0]["message"])

    def test_correct_code_is_never_flagged(self):
        code = '''
import json, os.path as osp
from collections import Counter

class Box:
    size = 3
    def grow(self, by=1):
        global total
        total = self.size + by
        return [x for x in range(by) if x] or {k: v for k, v in {}.items()}

try:
    data = json.loads("{}")
except ValueError as err:
    print(err)
with open(__file__) as fh, open(osp.join(".", "x")) as other:
    pass
match data:
    case {"a": first, **rest}:
        print(first, rest)
    case [one, *more]:
        print(one, more)
    case other_value:
        print(other_value)
lam = lambda q: q * 2
print(Counter, Box().grow(), lam(2), capture, run_script)
'''
        self.assertEqual(assist.diagnose(code), [])

    def test_star_import_disables_name_checks(self):
        self.assertEqual(assist.diagnose("from math import *\nprint(sqrt(2))\n"), [])


class CompleteTests(unittest.TestCase):
    def test_module_and_from_import_attributes(self):
        self.assertEqual(names("import json\njson.du"), ("du", ["dump", "dumps"]))
        self.assertIn("most_common", names("from collections import Counter\nCounter.mo")[1])
        self.assertIn("join", names("import os.path\nos.path.jo")[1])

    def test_literals_self_and_parameters(self):
        self.assertEqual(names('name = "ada"\nname.up'), ("up", ["upper"]))
        self.assertIn("append", names("words = []\nwords.")[1])
        self.assertEqual(names("class A:\n    def __init__(self):\n        self.count = 0\n    def inc(self):\n        self.")[1],
                         ["count", "inc"])
        self.assertEqual(names("def greet(person):\n    return per")[1][0], "person")

    def test_survives_broken_code_elsewhere(self):
        self.assertEqual(names("def f(:\n    pass\ntotal = 3\ntot")[1], ["total"])

    def test_imports_keywords_and_builtins(self):
        self.assertIn("collections", names("import coll")[1])
        self.assertIn("chain", names("from itertools import ch")[1])
        self.assertIn("print", names("pri")[1])
        self.assertIn("return", names("def f():\n    ret")[1])

    def test_unsafe_modules_are_never_imported(self):
        self.assertNotIn("antigravity", assist.SAFE_MODULES)
        self.assertEqual(names("import antigravity\nantigravity.")[1], [])
        self.assertNotIn("antigravity", names("import anti")[1])

    def test_unknown_objects_offer_nothing(self):
        self.assertEqual(names("import json\nx = json.loads(s)\nx.")[1], [])
        self.assertEqual(names("x = 1.")[1], [])

    @unittest.skipUnless(assist.jedi_available(), "Jedi isn't installed")
    def test_jedi_engine(self):
        r = assist.complete("import json\njson.du", 2, 7)
        self.assertEqual(r["engine"], "jedi")
        self.assertIn("dumps", [i["text"] for i in r["items"]])


class AssistApiTests(unittest.TestCase):
    def test_endpoints(self):
        r = server.api_assist_complete({"code": "import json\njson.lo", "line": 2, "ch": 7})
        self.assertIn("loads", [i["text"] for i in r["items"]])
        self.assertEqual(server.api_assist_diagnose({"code": "print(x)"})["problems"][0]["line"], 1)
        with self.assertRaises(server.ApiError):
            server.api_assist_complete({"code": "", "line": "a"})
        st = server.api_state()
        self.assertIn("jedi", st["assist"])
        self.assertTrue(st["settings"]["editor_assist"])


if __name__ == "__main__":
    unittest.main()
