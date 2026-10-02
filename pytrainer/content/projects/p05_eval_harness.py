PROJECT = {
    "id": "eval-harness",
    "title": "LLM Evaluation Harness",
    "order": 5,
    "level": "Intermediate",
    "estimated_hours": 2.5,
    "requires": ["json", "files", "regex", "functions", "errors", "dicts"],
    "tags": ["evals", "testing", "llm-as-judge", "jsonl"],
    "main": "evals.py",
    "files": ["evals.py"],
    "brief": r'''
        # LLM Evaluation Harness

        You cannot unit-test an LLM app with a couple of `assert`s: outputs vary, and a
        prompt tweak that fixes one case silently breaks five others. Teams keep a set
        of **eval cases** (inputs + what a good answer looks like), run the whole set
        on every prompt/model change, and compare **pass rates**. Some checks are
        mechanical (exact match, regex, valid JSON); others need judgement and use a
        second model as a **judge**.

        Build a small eval harness in **`evals.py`**. The model and the judge are
        **injected callables**, so tests use fakes and you can plug in any real API.

        ## Case file format (JSONL)

        One JSON object per line. Blank lines are skipped.

        ```json
        {"id": "capital-fr", "input": "Capital of France?", "expected": "Paris", "grader": "contains", "tags": ["geo"]}
        {"id": "json-out", "input": "Return a JSON user", "expected": ["name", "age"], "grader": "json_valid"}
        ```

        | field | required | default |
        | --- | --- | --- |
        | `id` | yes, non-empty `str`, unique in the file | |
        | `input` | yes, `str` | |
        | `expected` | no | `None` |
        | `grader` | no | `"exact"` |
        | `tags` | no, list of `str` | `[]` |

        ## Interface

        ### `load_cases(path: str) -> list[dict]`
        Return the cases in file order, each with **all five keys** filled (defaults
        applied). Raise `ValueError` whose message contains `line N` (1-based line number
        in the file) for invalid JSON, a line that is not an object, a missing/invalid
        `id` or `input`, or a duplicate `id`. A missing file raises `FileNotFoundError`.

        ### Graders
        Each grader is `grader(output: str, expected) -> bool`.

        | name | function | passes when |
        | --- | --- | --- |
        | `exact` | `grade_exact` | `output.strip() == str(expected).strip()` |
        | `contains` | `grade_contains` | `expected` (a `str`, or a list of `str` that must **all** appear) appears in `output`, case-insensitively |
        | `regex` | `grade_regex` | `re.search(expected, output)` finds a match |
        | `json_valid` | `grade_json_valid` | `output` parses as JSON; if `expected` is a list of keys, the parsed value must also be an object containing every key |

        Expose them in a module-level dict **`GRADERS`** mapping name -> function.

        ### `make_llm_judge(judge) -> grader`
        `judge(prompt: str) -> str` is an injected model call. Return a grader function
        `(output, expected) -> bool` that sends the judge **one** prompt containing the
        model output and the `expected` criteria (plus clear instructions to reply
        PASS or FAIL), and passes when the reply, stripped and upper-cased, starts with
        `"PASS"`.

        ### `run_eval(cases: list[dict], model, judge=None) -> dict`
        `model(input: str) -> str`. Grader name `"llm_judge"` uses
        `make_llm_judge(judge)`.

        - **Before calling the model at all**, raise `ValueError` if any case uses an
          unknown grader, or uses `"llm_judge"` while `judge` is `None`.
        - For each case call the model once. If the model raises, returns a non-`str`,
          or the grader raises, the case **fails** and its `error` is a string starting
          with the exception type name (e.g. `"TimeoutError: slow"`) or mentioning the
          wrong type; the run continues with the next case.
        - Return the report:

        ```python
        {
          "summary":   {"total": 4, "passed": 3, "failed": 1, "pass_rate": 0.75},
          "by_grader": {"contains": {...same keys...}, "exact": {...}},
          "by_tag":    {"geo": {...}},          # a case counts once for each of its tags
          "results": [
            {"id": "capital-fr", "input": "...", "output": "...", "expected": "Paris",
             "grader": "contains", "tags": ["geo"], "passed": True, "error": None},
            ...                                  # same order as cases
          ],
        }
        ```

        `pass_rate` is `passed / total` rounded to 4 decimals (`0.0` when `total` is 0).
        `output` is `None` when the model raised.

        ### `write_report(report: dict, path: str) -> None`
        Write the report as indented JSON (UTF-8), creating parent folders if needed.

        ### `run_file(cases_path: str, model, report_path: str, judge=None) -> dict`
        Load, run, write the report, and return it.

        ## Running it locally

        Write a `cases.jsonl` with 5-10 cases and a fake model (a dict lookup), then run
        `run_file("cases.jsonl", fake_model, "out/report.json")`. Upload `evals.py`.
    ''',
    "explore": r'''
        ## Things to research

        - **LLM evals**: read OpenAI's "evals" guide / the open-source `openai/evals`
          repo and Anthropic's docs on "creating strong empirical evaluations". What
          makes a good eval set (coverage, edge cases, regression cases from real bugs)?
        - **LLM-as-judge**: its known biases (position bias, verbosity bias,
          self-preference), and mitigations: rubrics, pairwise comparison, asking for
          reasoning before the verdict, calibrating the judge against human labels.
        - **Non-determinism**: `temperature`, `seed`, and why you may run each case
          several times and report a mean.
        - Tools in this space: promptfoo, DeepEval, Braintrust, LangSmith.

        ## Make it real (optional, ungraded)

        ```bash
        pip install anthropic
        export ANTHROPIC_API_KEY=sk-ant-...
        ```

        ```python
        import anthropic
        from evals import run_file

        client = anthropic.Anthropic()

        def call(prompt, model="claude-haiku-4-5"):
            resp = client.messages.create(model=model, max_tokens=300,
                                          messages=[{"role": "user", "content": prompt}])
            return resp.content[0].text

        report = run_file("cases.jsonl", model=call, report_path="report.json", judge=call)
        print(report["summary"])
        ```
    ''',
    "rubric": [
        "Graders are small pure functions registered in one GRADERS mapping; adding a grader needs no changes elsewhere",
        "Model and judge are dependency-injected; errors from them are isolated per case and recorded, never crash the run",
        "Configuration errors (unknown grader, missing judge) are detected up front, before any model call",
        "JSONL parsing reports precise line numbers and validates fields",
        "Aggregation code is not copy-pasted per group (one helper computes stats for any subset)",
        "The judge prompt is clear, delimits the output being judged, and asks for a strict PASS/FAIL",
    ],
    "starter_files": {
        "evals.py": r'''
            """A tiny evaluation harness for LLM outputs."""


            def load_cases(path):
                ...


            def grade_exact(output, expected):
                ...


            def grade_contains(output, expected):
                ...


            def grade_regex(output, expected):
                ...


            def grade_json_valid(output, expected=None):
                ...


            GRADERS = {}


            def make_llm_judge(judge):
                ...


            def run_eval(cases, model, judge=None):
                ...


            def write_report(report, path):
                ...


            def run_file(cases_path, model, report_path, judge=None):
                ...
        ''',
    },
    "solution_files": {
        "evals.py": r'''
            """A tiny evaluation harness for LLM outputs."""

            from __future__ import annotations

            import json
            import re
            from pathlib import Path
            from typing import Any, Callable

            Grader = Callable[[str, Any], bool]
            Model = Callable[[str], str]

            JUDGE_PROMPT = (
                "You are grading the output of an AI assistant.\n"
                "Criteria:\n<criteria>\n{criteria}\n</criteria>\n\n"
                "Output to grade:\n<output>\n{output}\n</output>\n\n"
                "Does the output meet the criteria? Reply with exactly PASS or FAIL."
            )


            # ---------- loading ----------

            def _parse_case(line: str, lineno: int, seen: set[str]) -> dict:
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"line {lineno}: invalid JSON ({exc.msg})") from None
                if not isinstance(raw, dict):
                    raise ValueError(f"line {lineno}: expected a JSON object")
                case_id = raw.get("id")
                if not isinstance(case_id, str) or not case_id:
                    raise ValueError(f"line {lineno}: 'id' must be a non-empty string")
                if case_id in seen:
                    raise ValueError(f"line {lineno}: duplicate id {case_id!r}")
                if not isinstance(raw.get("input"), str):
                    raise ValueError(f"line {lineno}: 'input' must be a string")
                seen.add(case_id)
                return {
                    "id": case_id,
                    "input": raw["input"],
                    "expected": raw.get("expected"),
                    "grader": raw.get("grader", "exact"),
                    "tags": list(raw.get("tags", [])),
                }


            def load_cases(path: str) -> list[dict]:
                seen: set[str] = set()
                cases = []
                with open(path, encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        if line.strip():
                            cases.append(_parse_case(line, lineno, seen))
                return cases


            # ---------- graders ----------

            def grade_exact(output: str, expected: Any) -> bool:
                return output.strip() == str(expected).strip()


            def grade_contains(output: str, expected: str | list[str]) -> bool:
                needles = [expected] if isinstance(expected, str) else expected
                haystack = output.lower()
                return all(needle.lower() in haystack for needle in needles)


            def grade_regex(output: str, expected: str) -> bool:
                return re.search(expected, output) is not None


            def grade_json_valid(output: str, expected: list[str] | None = None) -> bool:
                try:
                    value = json.loads(output)
                except json.JSONDecodeError:
                    return False
                if isinstance(expected, list):
                    return isinstance(value, dict) and all(key in value for key in expected)
                return True


            GRADERS: dict[str, Grader] = {
                "exact": grade_exact,
                "contains": grade_contains,
                "regex": grade_regex,
                "json_valid": grade_json_valid,
            }


            def make_llm_judge(judge: Model) -> Grader:
                def grade_llm_judge(output: str, expected: Any) -> bool:
                    reply = judge(JUDGE_PROMPT.format(criteria=expected, output=output))
                    return reply.strip().upper().startswith("PASS")
                return grade_llm_judge


            # ---------- running ----------

            def _resolve_graders(cases: list[dict], judge: Model | None) -> dict[str, Grader]:
                graders = dict(GRADERS)
                if judge is not None:
                    graders["llm_judge"] = make_llm_judge(judge)
                for case in cases:
                    name = case.get("grader", "exact")
                    if name == "llm_judge" and judge is None:
                        raise ValueError(f"case {case['id']!r} needs a judge but none was given")
                    if name not in graders:
                        raise ValueError(f"case {case['id']!r}: unknown grader {name!r}")
                return graders


            def _run_case(case: dict, model: Model, grader: Grader) -> dict:
                result = {
                    "id": case["id"], "input": case["input"], "output": None,
                    "expected": case.get("expected"), "grader": case.get("grader", "exact"),
                    "tags": list(case.get("tags", [])), "passed": False, "error": None,
                }
                try:
                    output = model(case["input"])
                    result["output"] = output
                    if not isinstance(output, str):
                        raise TypeError(f"model returned {type(output).__name__}, expected str")
                    result["passed"] = bool(grader(output, result["expected"]))
                except Exception as exc:  # isolate every failure to its own case
                    result["error"] = f"{type(exc).__name__}: {exc}"
                return result


            def _stats(results: list[dict]) -> dict:
                total = len(results)
                passed = sum(r["passed"] for r in results)
                return {"total": total, "passed": passed, "failed": total - passed,
                        "pass_rate": round(passed / total, 4) if total else 0.0}


            def _group(results: list[dict], keys: Callable[[dict], list[str]]) -> dict:
                groups: dict[str, list[dict]] = {}
                for result in results:
                    for key in keys(result):
                        groups.setdefault(key, []).append(result)
                return {key: _stats(items) for key, items in sorted(groups.items())}


            def run_eval(cases: list[dict], model: Model, judge: Model | None = None) -> dict:
                graders = _resolve_graders(cases, judge)
                results = [_run_case(c, model, graders[c.get("grader", "exact")]) for c in cases]
                return {
                    "summary": _stats(results),
                    "by_grader": _group(results, lambda r: [r["grader"]]),
                    "by_tag": _group(results, lambda r: r["tags"]),
                    "results": results,
                }


            def write_report(report: dict, path: str) -> None:
                target = Path(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


            def run_file(cases_path: str, model: Model, report_path: str,
                         judge: Model | None = None) -> dict:
                report = run_eval(load_cases(cases_path), model, judge)
                write_report(report, report_path)
                return report


            if __name__ == "__main__":
                answers = {"Capital of France?": "Paris is the capital."}
                report = run_eval(
                    [{"id": "fr", "input": "Capital of France?", "expected": "paris",
                      "grader": "contains", "tags": ["geo"]}],
                    model=lambda q: answers.get(q, "I don't know"),
                )
                print(json.dumps(report["summary"]))
        ''',
    },
    "tests": r'''
        import json
        import os
        from evals import (GRADERS, grade_contains, grade_exact, grade_json_valid, grade_regex,
                           load_cases, make_llm_judge, run_eval, run_file, write_report)

        CASES_JSONL = "\n".join([
            json.dumps({"id": "fr", "input": "Capital of France?", "expected": "Paris",
                        "grader": "contains", "tags": ["geo"]}),
            "",
            json.dumps({"id": "math", "input": "2+2", "expected": "4"}),
            json.dumps({"id": "user", "input": "json user", "expected": ["name", "age"],
                        "grader": "json_valid", "tags": ["json", "geo"]}),
            json.dumps({"id": "date", "input": "today?", "expected": r"\d{4}-\d{2}-\d{2}",
                        "grader": "regex", "tags": ["json"]}),
        ]) + "\n"

        ANSWERS = {
            "Capital of France?": "The capital is PARIS.",
            "2+2": " 4\n",
            "json user": '{"name": "Ada"}',
            "today?": "It is 2025-01-31.",
        }

        def fake_model(prompt):
            return ANSWERS[prompt]

        def write(name, text):
            with open(name, "w", encoding="utf-8") as fh:
                fh.write(text)

        def expect_value_error_with(fn, needle):
            try:
                fn()
            except ValueError as exc:
                assert needle in str(exc), f"error message {str(exc)!r} should mention {needle!r}"
                return
            raise AssertionError("expected ValueError")

        def test_load_cases_applies_defaults_and_skips_blank_lines():
            write("cases.jsonl", CASES_JSONL)
            cases = load_cases("cases.jsonl")
            assert [c["id"] for c in cases] == ["fr", "math", "user", "date"], f"got {[c['id'] for c in cases]}"
            assert cases[1] == {"id": "math", "input": "2+2", "expected": "4",
                                "grader": "exact", "tags": []}, f"got {cases[1]!r}"

        def test_load_cases_errors_report_line_numbers():
            good = json.dumps({"id": "a", "input": "x"})
            write("bad1.jsonl", good + "\n\n{not json}\n")
            expect_value_error_with(lambda: load_cases("bad1.jsonl"), "line 3")
            write("bad2.jsonl", good + "\n" + json.dumps({"input": "no id"}) + "\n")
            expect_value_error_with(lambda: load_cases("bad2.jsonl"), "line 2")
            write("bad3.jsonl", good + "\n" + good + "\n")
            expect_value_error_with(lambda: load_cases("bad3.jsonl"), "line 2")
            write("bad4.jsonl", json.dumps({"id": "a", "input": 5}) + "\n")
            expect_value_error_with(lambda: load_cases("bad4.jsonl"), "line 1")
            write("bad5.jsonl", "[1, 2]\n")
            expect_value_error_with(lambda: load_cases("bad5.jsonl"), "line 1")

        def test_basic_graders():
            assert grade_exact("  Paris\n", "Paris") is True
            assert grade_exact("paris", "Paris") is False
            assert grade_exact("42", 42) is True
            assert grade_contains("The capital is PARIS.", "paris") is True
            assert grade_contains("red and blue", ["Blue", "red"]) is True
            assert grade_contains("red only", ["red", "blue"]) is False
            assert grade_regex("id: AB-123", r"[A-Z]{2}-\d+") is True
            assert grade_regex("nothing", r"\d") is False

        def test_json_valid_grader():
            assert grade_json_valid('{"a": 1}') is True
            assert grade_json_valid("[1, 2]") is True
            assert grade_json_valid("{'a': 1}") is False
            assert grade_json_valid('{"name": "x", "age": 3}', ["name", "age"]) is True
            assert grade_json_valid('{"name": "x"}', ["name", "age"]) is False
            assert grade_json_valid('["name", "age"]', ["name", "age"]) is False

        def test_graders_registry():
            assert set(GRADERS) == {"exact", "contains", "regex", "json_valid"}, f"got {set(GRADERS)}"
            assert GRADERS["contains"]("ABC", "b") is True

        def test_llm_judge_prompt_and_verdict():
            prompts = []
            def judge(prompt):
                prompts.append(prompt)
                return "  pass - looks good" if "polite" in prompt else "FAIL"
            grader = make_llm_judge(judge)
            assert grader("Thank you kindly!", "Must be polite") is True
            assert len(prompts) == 1, "the judge should be called exactly once per grade"
            assert "Thank you kindly!" in prompts[0] and "Must be polite" in prompts[0]
            assert grader("whatever", "Must be short") is False

        def test_run_eval_report():
            write("cases.jsonl", CASES_JSONL)
            report = run_eval(load_cases("cases.jsonl"), fake_model)
            assert report["summary"] == {"total": 4, "passed": 3, "failed": 1, "pass_rate": 0.75}, \
                f"summary {report['summary']!r}"
            assert report["by_grader"]["json_valid"] == {"total": 1, "passed": 0, "failed": 1, "pass_rate": 0.0}
            assert report["by_grader"]["exact"]["passed"] == 1
            assert report["by_tag"]["geo"] == {"total": 2, "passed": 1, "failed": 1, "pass_rate": 0.5}, \
                f"by_tag geo {report['by_tag'].get('geo')!r}"
            assert report["by_tag"]["json"]["total"] == 2
            first = report["results"][0]
            assert first == {"id": "fr", "input": "Capital of France?", "output": "The capital is PARIS.",
                             "expected": "Paris", "grader": "contains", "tags": ["geo"],
                             "passed": True, "error": None}, f"got {first!r}"
            assert [r["id"] for r in report["results"]] == ["fr", "math", "user", "date"]

        def test_pass_rate_rounding_and_empty_run():
            cases = [{"id": str(i), "input": "x", "expected": "y" if i else "x",
                      "grader": "exact", "tags": []} for i in range(3)]
            report = run_eval(cases, lambda s: s)
            assert report["summary"]["pass_rate"] == 0.3333, f"got {report['summary']['pass_rate']}"
            empty = run_eval([], lambda s: s)
            assert empty["summary"] == {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}

        def test_model_errors_are_isolated():
            def flaky(prompt):
                if prompt == "boom":
                    raise TimeoutError("slow")
                if prompt == "num":
                    return 42
                return prompt
            cases = [{"id": "a", "input": "boom", "expected": "x", "grader": "exact", "tags": []},
                     {"id": "b", "input": "num", "expected": "42", "grader": "exact", "tags": []},
                     {"id": "c", "input": "ok", "expected": "ok", "grader": "exact", "tags": []}]
            report = run_eval(cases, flaky)
            a, b, c = report["results"]
            assert a["passed"] is False and a["output"] is None
            assert a["error"] and a["error"].startswith("TimeoutError"), f"error {a['error']!r}"
            assert b["passed"] is False and b["error"], "a non-str model output must fail with an error"
            assert c["passed"] is True and c["error"] is None
            assert report["summary"]["passed"] == 1

        def test_config_errors_raised_before_any_model_call():
            calls = []
            def model(prompt):
                calls.append(prompt)
                return prompt
            ok = {"id": "a", "input": "x", "expected": "x", "grader": "exact", "tags": []}
            unknown = {"id": "b", "input": "x", "expected": "x", "grader": "fuzzy", "tags": []}
            judged = {"id": "c", "input": "x", "expected": "nice", "grader": "llm_judge", "tags": []}
            for cases in ([ok, unknown], [ok, judged]):
                try:
                    run_eval(cases, model)
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"expected ValueError for grader {cases[1]['grader']!r}")
            assert calls == [], "the model was called before the configuration was validated"

        def test_llm_judge_used_in_run_eval():
            cases = [{"id": "p", "input": "greet", "expected": "is polite", "grader": "llm_judge", "tags": []},
                     {"id": "r", "input": "insult", "expected": "is polite", "grader": "llm_judge", "tags": []}]
            model = {"greet": "Hello, lovely to meet you", "insult": "Go away"}.get
            judge = lambda prompt: "PASS" if "lovely" in prompt else "FAIL"
            report = run_eval(cases, model, judge=judge)
            assert [r["passed"] for r in report["results"]] == [True, False]
            assert report["by_grader"]["llm_judge"]["pass_rate"] == 0.5

        def test_write_report_and_run_file():
            write("cases.jsonl", CASES_JSONL)
            report = run_file("cases.jsonl", fake_model, "out/nested/report.json")
            assert os.path.exists("out/nested/report.json"), "report file not created"
            with open("out/nested/report.json", encoding="utf-8") as fh:
                text = fh.read()
            assert json.loads(text) == report
            assert "\n" in text, "report JSON should be indented"
            write_report({"summary": {"note": "café"}}, "r2.json")
            with open("r2.json", encoding="utf-8") as fh:
                assert json.load(fh) == {"summary": {"note": "café"}}
    ''',
}
