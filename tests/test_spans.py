import json
import unittest

import server
from pytrainer import content, runner, spans


class SpanParsingTests(unittest.TestCase):
    def test_keeps_good_rows_and_skips_bad_ones(self):
        rows = [
            {"name": "agent.run", "span_id": "a", "start": 1.0, "end": 2.0, "status": "ok",
             "attributes": {"q": "x" * 5000, "tags": ["a", "b"]}},
            {"name": "no-times"},
            {"name": "backwards", "start": 3.0, "end": 2.0},
            {"name": "bool-times", "start": True, "end": 2.0},
            {"name": "child", "span_id": "b", "parent_id": "a", "start": 1.1, "end": 1.5, "status": "error"},
        ]
        text = "\n".join(json.dumps(r) for r in rows) + "\nnot json\n[1, 2]\n\n"
        got = spans.parse(text)
        self.assertEqual([s["name"] for s in got], ["agent.run", "child"])
        self.assertEqual(len(got[0]["attributes"]["q"]), spans.MAX_ATTR)
        self.assertEqual(got[0]["attributes"]["tags"], '["a", "b"]')
        self.assertEqual(got[1]["status"], "error")
        self.assertEqual(got[1]["parent_id"], "a")
        self.assertIsNone(got[0]["parent_id"])

    def test_caps_the_number_of_spans(self):
        line = json.dumps({"name": "s", "start": 0, "end": 1})
        self.assertEqual(len(spans.parse("\n".join([line] * (spans.MAX_SPANS + 50)))), spans.MAX_SPANS)

    def test_sample_is_a_valid_trace(self):
        got = spans.parse(spans.SAMPLE)
        self.assertEqual(len(got), 10)
        self.assertEqual(sum(s["parent_id"] is None for s in got), 1)
        self.assertTrue(any(s["status"] == "error" for s in got))


class RunCollectsSpansTests(unittest.TestCase):
    def test_run_returns_spans_from_traces_jsonl(self):
        code = ("import json\n"
                "with open('traces.jsonl', 'w') as fh:\n"
                "    fh.write(json.dumps({'name': 'work', 'start': 0.0, 'end': 0.5}) + '\\n')\n"
                "print('done')\n")
        r = runner.run_code({"solution.py": code})
        self.assertEqual(r["stdout"].strip(), "done")
        self.assertEqual([s["name"] for s in r["spans"]], ["work"])

    def test_no_spans_key_without_a_trace_file(self):
        self.assertNotIn("spans", runner.run_code({"solution.py": "print(1)"}))

    def test_project_demo_draws_a_trace(self):
        p = content.load()["projects_by_id"]["agent-tracing"]
        r = server.api_project_run("agent-tracing", {"files": p["solution_files"]})
        self.assertIn("10 spans written", r["stdout"])
        names = {s["name"] for s in r["spans"]}
        self.assertEqual(names, {"agent.run", "agent.step", "llm.call", "tool.get_order", "tool.search_docs"})
        self.assertEqual(sum(s["status"] == "error" for s in r["spans"]), 1)


class TraceViewerApiTests(unittest.TestCase):
    def test_parse_and_sample(self):
        r = server.api_traces_parse({"text": json.dumps({"name": "x", "start": 0, "end": 1})})
        self.assertEqual(r["spans"][0]["name"], "x")
        with self.assertRaises(server.ApiError):
            server.api_traces_parse({"text": "nothing here"})
        self.assertEqual(len(server.api_traces_sample()["spans"]), 10)


if __name__ == "__main__":
    unittest.main()
