EXAM = {
    "module": "evals",
    "title": "Evals & Observability: module test",
    "intro": r'''
        This is a **test**, not a lesson. It covers the whole *Evals* module: graders, eval
        datasets, retrieval metrics, LLM-as-judge, comparing runs, tracing and latency numbers.

        - There are **no hints and no tutor** during the test. Every rule the checks test is
          in the prompt.
        - Models, judges and clocks are **fakes** passed into your code, so results are exact
          and repeatable. Standard library only, no network.
        - One task links to real documentation. Another asks you to find a standard-library
          tool yourself, with no links.
        - Pass at least **70%** of the exercises and you can skip the module.
    ''',
    "pass_ratio": 0.7,
}

EXERCISES = [
    {
        "id": "exam-evals-1",
        "title": "Four graders",
        "difficulty": 2,
        "prompt": r'''
            An eval case says how its output should be graded. Implement the four simple graders.

            **Write:** `grade(case, output)`

            - `case`: a dict with `"grader"` (one of `"exact"`, `"contains"`, `"regex"`, `"numeric"`),
              `"expected"` and, for `"numeric"` only, an optional `"tolerance"` (default `0`)
            - `output`: the model's output string
            - **Returns:** `True` or `False`

            **Rules**
            - `"exact"`: `output` with surrounding whitespace stripped equals `expected` (case matters).
            - `"contains"`: `expected` appears in `output`, ignoring upper/lower case.
            - `"regex"`: `expected` is a regular expression that matches **somewhere** in `output`.
            - `"numeric"`: take the **first** number in `output` (optional `-`, digits, optional
              `.` and digits, e.g. `42`, `-3.5`); pass if it differs from `expected` (a number)
              by at most `tolerance`. No number in the output means `False`.
            - Any other grader raises `ValueError("unknown grader: <grader>")`.

            **Examples**
            ```python
            grade({"grader": "exact", "expected": "Paris"}, "  Paris\n")            # True
            grade({"grader": "contains", "expected": "refund"}, "A REFUND is due")  # True
            grade({"grader": "regex", "expected": r"\d{3}-\d{4}"}, "Call 555-1234")  # True
            grade({"grader": "numeric", "expected": 3.14, "tolerance": 0.01}, "About 3.141 or so")  # True
            grade({"grader": "numeric", "expected": 10}, "ten")                    # False
            ```
        ''',
        "starter": r'''
            import re


            def grade(case, output):
                ...
        ''',
        "tests": r'''
            from solution import grade

            def test_exact_strips_but_is_case_sensitive():
                assert grade({"grader": "exact", "expected": "Paris"}, "  Paris\n") is True
                assert grade({"grader": "exact", "expected": "Paris"}, "paris") is False
                assert grade({"grader": "exact", "expected": "Paris"}, "Paris, France") is False

            def test_contains_ignores_case():
                assert grade({"grader": "contains", "expected": "refund"}, "A REFUND is due") is True
                assert grade({"grader": "contains", "expected": "Refund"}, "no money back") is False

            def test_regex_searches_anywhere():
                assert grade({"grader": "regex", "expected": r"\d{3}-\d{4}"}, "Call 555-1234 now") is True
                assert grade({"grader": "regex", "expected": r"^\d+$"}, "abc 12") is False

            def test_numeric_uses_first_number_and_tolerance():
                assert grade({"grader": "numeric", "expected": 3.14, "tolerance": 0.01}, "About 3.141 or 7") is True
                assert grade({"grader": "numeric", "expected": 7, "tolerance": 0.5}, "About 3.141 or 7") is False
                assert grade({"grader": "numeric", "expected": -2}, "It dropped to -2 degrees") is True
                assert grade({"grader": "numeric", "expected": 42}, "42.5") is False
                assert grade({"grader": "numeric", "expected": 10}, "ten") is False

            def test_unknown_grader_raises():
                try:
                    grade({"grader": "vibes", "expected": "x"}, "x")
                except ValueError as e:
                    assert str(e) == "unknown grader: vibes", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
        ''',
        "solution": r'''
            import re


            def grade(case, output):
                kind, expected = case["grader"], case["expected"]
                if kind == "exact":
                    return output.strip() == expected
                if kind == "contains":
                    return expected.lower() in output.lower()
                if kind == "regex":
                    return re.search(expected, output) is not None
                if kind == "numeric":
                    m = re.search(r"-?\d+(?:\.\d+)?", output)
                    if m is None:
                        return False
                    return abs(float(m.group()) - expected) <= case.get("tolerance", 0)
                raise ValueError(f"unknown grader: {kind}")
        ''',
        "hints": [
            "One `if` branch per grader; the `re` module handles both the regex grader and finding the first number.",
            "`re.search` returns a match object or `None`. For numeric, search for the number pattern, convert it with `float`, compare the absolute difference.",
            "exact: `output.strip() == expected`. contains: compare `.lower()` versions with `in`. regex: `re.search(expected, output) is not None`. numeric: `re.search(r'-?\\d+(?:\\.\\d+)?', output)`, then `abs(float(m.group()) - expected) <= case.get('tolerance', 0)`. Else raise.",
        ],
    },
    {
        "id": "exam-evals-2",
        "title": "Run an eval set from JSONL",
        "difficulty": 2,
        "setup_files": {
            "cases.jsonl": r'''
                {"id": "c1", "input": "Capital of France?", "expected": "paris", "tags": ["geo"]}
                {"id": "c2", "input": "2+2?", "expected": "4", "tags": ["math"]}

                {"id": "c3", "input": "Capital of Japan?", "expected": "tokyo", "tags": ["geo", "hard"]}
                {"id": "c4", "input": "Say hi", "expected": "hello"}
            ''',
        },
        "prompt": r'''
            Eval datasets are usually stored as **JSONL**: one JSON object per line. Load one,
            run a model on every case and report pass rates, overall and per tag.

            **Write:** `run_eval(path, model)`

            - `path`: path to a `.jsonl` file. Each non-blank line is an object with `"id"`,
              `"input"`, `"expected"` and optionally `"tags"` (a list of strings, default `[]`).
            - `model`: a function `model(input_text) -> str` (a fake in the tests)
            - **Returns:**
              `{"total": int, "passed": int, "pass_rate": float, "by_tag": {tag: {"total": int, "passed": int, "pass_rate": float}}, "failures": [ids]}`

            **Rules**
            - Skip blank lines (empty or only whitespace).
            - A line that is not valid JSON raises `ValueError("line <n>: invalid JSON")`, where
              `n` is the line number in the file, counting from 1 and counting blank lines too.
            - A case passes when `expected` appears in the model's output, ignoring case.
            - If `model` raises an exception for a case, that case fails (don't crash).
            - `pass_rate` values are `passed / total` rounded with `round(value, 3)`; `0.0` when `total` is 0.
            - `failures`: ids of failed cases in file order.
            - `by_tag` has one entry per tag that appears; cases without tags only count in the totals.

            **Examples**
            ```python
            # cases.jsonl (the file in your folder) has 4 cases; the model answers c1, c2, c4 correctly
            run_eval("cases.jsonl", model)
            # {"total": 4, "passed": 3, "pass_rate": 0.75,
            #  "by_tag": {"geo": {"total": 2, "passed": 1, "pass_rate": 0.5},
            #             "math": {"total": 1, "passed": 1, "pass_rate": 1.0},
            #             "hard": {"total": 1, "passed": 0, "pass_rate": 0.0}},
            #  "failures": ["c3"]}
            ```
        ''',
        "starter": r'''
            import json


            def run_eval(path, model):
                ...
        ''',
        "tests": r'''
            from pathlib import Path
            from solution import run_eval

            ANSWERS = {"Capital of France?": "It is Paris.", "2+2?": "4", "Capital of Japan?": "Kyoto", "Say hi": "HELLO!"}

            def test_example_file():
                got = run_eval("cases.jsonl", lambda text: ANSWERS[text])
                assert got == {"total": 4, "passed": 3, "pass_rate": 0.75,
                               "by_tag": {"geo": {"total": 2, "passed": 1, "pass_rate": 0.5},
                                          "math": {"total": 1, "passed": 1, "pass_rate": 1.0},
                                          "hard": {"total": 1, "passed": 0, "pass_rate": 0.0}},
                               "failures": ["c3"]}, f"got {got!r}"

            def test_model_errors_count_as_failures():
                def flaky(text):
                    if text == "2+2?":
                        raise TimeoutError("slow")
                    return ANSWERS[text]
                got = run_eval("cases.jsonl", flaky)
                assert got["failures"] == ["c2", "c3"], f"got {got!r}"
                assert got["passed"] == 2 and got["pass_rate"] == 0.5, f"got {got!r}"

            def test_rounding_to_three_places():
                Path("three.jsonl").write_text("\n".join(
                    '{"id": "%d", "input": "q", "expected": "%s"}' % (i, e) for i, e in enumerate("aab")) + "\n")
                got = run_eval("three.jsonl", lambda t: "a")
                assert got["pass_rate"] == 0.667 and got["by_tag"] == {}, f"got {got!r}"

            def test_empty_file():
                Path("empty.jsonl").write_text("\n  \n")
                got = run_eval("empty.jsonl", lambda t: "x")
                assert got == {"total": 0, "passed": 0, "pass_rate": 0.0, "by_tag": {}, "failures": []}, f"got {got!r}"

            def test_invalid_line_reports_its_number():
                Path("bad.jsonl").write_text('{"id": "a", "input": "q", "expected": "x"}\n\n{oops\n')
                try:
                    run_eval("bad.jsonl", lambda t: "x")
                except ValueError as e:
                    assert str(e) == "line 3: invalid JSON", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
        ''',
        "solution": r'''
            import json


            def _rate(passed, total):
                return round(passed / total, 3) if total else 0.0


            def run_eval(path, model):
                cases = []
                with open(path, encoding="utf-8") as f:
                    for n, line in enumerate(f, start=1):
                        if not line.strip():
                            continue
                        try:
                            cases.append(json.loads(line))
                        except json.JSONDecodeError:
                            raise ValueError(f"line {n}: invalid JSON") from None
                passed, failures, tags = 0, [], {}
                for case in cases:
                    try:
                        ok = case["expected"].lower() in model(case["input"]).lower()
                    except Exception:
                        ok = False
                    passed += ok
                    if not ok:
                        failures.append(case["id"])
                    for tag in case.get("tags", []):
                        t = tags.setdefault(tag, {"total": 0, "passed": 0})
                        t["total"] += 1
                        t["passed"] += ok
                by_tag = {tag: {"total": t["total"], "passed": t["passed"], "pass_rate": _rate(t["passed"], t["total"])}
                          for tag, t in tags.items()}
                return {"total": len(cases), "passed": passed, "pass_rate": _rate(passed, len(cases)),
                        "by_tag": by_tag, "failures": failures}
        ''',
        "hints": [
            "Read the file line by line with `enumerate(..., start=1)` so you know line numbers; `json.loads` each non-blank line.",
            "First load all cases (raising on bad JSON), then run the model on each inside try/except, keeping overall counters and a dict of per-tag counters.",
            "Per case: `ok = expected.lower() in output.lower()` (False on exception); add to passed; record failures; for each tag update `tags.setdefault(tag, {...})`. At the end compute rates with a helper that returns 0.0 for total 0 and rounds to 3.",
        ],
    },
    {
        "id": "exam-evals-3",
        "title": "Retrieval metrics",
        "difficulty": 2,
        "prompt": r'''
            To know whether retrieval got better, measure it on a set of queries with known
            relevant documents.

            **Write:** `retrieval_metrics(runs, k)`

            - `runs`: a list of dicts `{"retrieved": [doc ids, best first], "relevant": [doc ids]}`, one per query
            - `k`: how many top results to look at
            - **Returns:** `{"precision@k": float, "recall@k": float, "mrr": float}`, each the
              **average over queries**, rounded with `round(value, 4)`

            **Rules** (for one query, `top` = the first `k` retrieved ids)
            - precision@k = (number of ids in `top` that are relevant) / `k` (divide by `k` even
              if fewer than `k` were retrieved).
            - recall@k = (number of relevant ids found in `top`) / (number of relevant ids).
            - reciprocal rank = `1 / position` of the first relevant id in `top` (positions start
              at 1); `0` if none is in `top`. `mrr` is its average.
            - First remove duplicate ids from `retrieved` (keep the first occurrence of each), **then**
              take the first `k` as `top`.
            - Queries with an empty `relevant` list are skipped entirely. If no query is left,
              return all three as `0.0`.
            - If `k < 1`, raise `ValueError("k must be at least 1")`.

            **Examples**
            ```python
            retrieval_metrics([
                {"retrieved": ["a", "b", "c"], "relevant": ["b", "z"]},
                {"retrieved": ["d", "e", "f"], "relevant": ["d"]},
            ], k=2)
            # {"precision@k": 0.5, "recall@k": 0.75, "mrr": 0.75}

            retrieval_metrics([], k=3)   # {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0}
            ```
        ''',
        "starter": r'''
            def retrieval_metrics(runs, k):
                ...
        ''',
        "tests": r'''
            from solution import retrieval_metrics

            def test_example():
                got = retrieval_metrics([
                    {"retrieved": ["a", "b", "c"], "relevant": ["b", "z"]},
                    {"retrieved": ["d", "e", "f"], "relevant": ["d"]},
                ], k=2)
                assert got == {"precision@k": 0.5, "recall@k": 0.75, "mrr": 0.75}, f"got {got!r}"

            def test_only_top_k_counts():
                got = retrieval_metrics([{"retrieved": ["x", "y", "a"], "relevant": ["a"]}], k=2)
                assert got == {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0}, f"got {got!r}"
                got = retrieval_metrics([{"retrieved": ["x", "y", "a"], "relevant": ["a"]}], k=3)
                assert got == {"precision@k": 0.3333, "recall@k": 1.0, "mrr": 0.3333}, f"got {got!r}"

            def test_precision_divides_by_k_even_with_few_results():
                got = retrieval_metrics([{"retrieved": ["a"], "relevant": ["a"]}], k=4)
                assert got == {"precision@k": 0.25, "recall@k": 1.0, "mrr": 1.0}, f"got {got!r}"

            def test_duplicates_count_once():
                got = retrieval_metrics([{"retrieved": ["a", "a", "c", "b"], "relevant": ["a", "b"]}], k=2)
                assert got == {"precision@k": 0.5, "recall@k": 0.5, "mrr": 1.0}, f"got {got!r}"

            def test_queries_without_relevant_docs_are_skipped():
                got = retrieval_metrics([{"retrieved": ["a"], "relevant": []},
                                         {"retrieved": ["b", "c"], "relevant": ["c"]}], k=2)
                assert got == {"precision@k": 0.5, "recall@k": 1.0, "mrr": 0.5}, f"got {got!r}"
                assert retrieval_metrics([], k=3) == {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0}
                assert retrieval_metrics([{"retrieved": ["a"], "relevant": []}], k=3) == {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0}

            def test_bad_k_raises():
                try:
                    retrieval_metrics([], k=0)
                except ValueError as e:
                    assert str(e) == "k must be at least 1", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
        ''',
        "solution": r'''
            def retrieval_metrics(runs, k):
                if k < 1:
                    raise ValueError("k must be at least 1")
                p_sum = r_sum = rr_sum = 0.0
                count = 0
                for run in runs:
                    relevant = set(run["relevant"])
                    if not relevant:
                        continue
                    count += 1
                    unique = list(dict.fromkeys(run["retrieved"]))
                    top = unique[:k]
                    hits = [d for d in top if d in relevant]
                    p_sum += len(hits) / k
                    r_sum += len(hits) / len(relevant)
                    for pos, d in enumerate(top, start=1):
                        if d in relevant:
                            rr_sum += 1 / pos
                            break
                if count == 0:
                    return {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0}
                return {"precision@k": round(p_sum / count, 4), "recall@k": round(r_sum / count, 4),
                        "mrr": round(rr_sum / count, 4)}
        ''',
        "hints": [
            "Compute the three numbers for one query, add them to running sums, and divide by the number of queries you actually counted.",
            "Remove duplicates while keeping order before slicing the top k. A set of relevant ids makes membership checks easy.",
            "`list(dict.fromkeys(retrieved))[:k]` gives the unique top k. hits = ids in top that are relevant. precision = len(hits)/k, recall = len(hits)/len(relevant). Loop with `enumerate(top, start=1)` and stop at the first relevant for 1/pos. Round the averages at the end.",
        ],
    },
    {
        "id": "exam-evals-4",
        "title": "LLM as judge",
        "difficulty": 3,
        "research": {
            "note": "Read how the providers suggest grading open-ended answers with a model: a "
                    "clear rubric, a fixed output format you can parse, and checking the judge itself.",
            "links": [
                {"title": "Anthropic docs: define success criteria and build evaluations",
                 "url": "https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests"},
                {"title": "OpenAI docs: evals", "url": "https://platform.openai.com/docs/guides/evals"},
            ],
        },
        "prompt": r'''
            Some answers can't be graded with a regex. A second model (the *judge*) scores them
            against a rubric. Your code must build the judge prompt and parse the verdict
            defensively, because judges don't always follow the format.

            **Write:** `judge(llm, question, answer, rubric, pass_score=4, max_attempts=2)`

            - `llm`: a fake judge, `llm(prompt) -> str`
            - **Returns:** `{"score": int or None, "reason": str, "passed": bool}`

            **Rules**
            - The prompt is exactly:
              `"Grade the answer.\nQuestion: <question>\nAnswer: <answer>\nRubric: <rubric>\nReply with two lines:\nSCORE: <1-5>\nREASON: <one sentence>"`
            - A valid reply has a line that is `SCORE:` (uppercase, exactly) followed by one digit from 1 to 5
              (spaces allowed after the colon and at the end of the line). The line may be
              anywhere in the reply.
            - `reason` is the text after `REASON:` on its line, stripped; `""` if there is no REASON line.
            - `passed` is `score >= pass_score`.
            - If the reply has no valid SCORE line, call `llm` again with the original prompt +
              `"\n\nYour previous reply was not in the required format."`, up to `max_attempts`
              calls in total.
            - If no attempt gives a valid score, return `{"score": None, "reason": "judge failed", "passed": False}`.

            **Examples**
            ```python
            judge(llm, "What is 2+2?", "4", "Correct and concise")
            # llm got "Grade the answer.\nQuestion: What is 2+2?\nAnswer: 4\nRubric: Correct and concise\nReply with two lines:\nSCORE: <1-5>\nREASON: <one sentence>"
            # llm replied "SCORE: 5\nREASON: Correct."   ->  {"score": 5, "reason": "Correct.", "passed": True}

            # llm replied "I'd give it 4/5"  then  "SCORE: 3"
            # -> {"score": 3, "reason": "", "passed": False}
            ```
        ''',
        "starter": r'''
            import re


            def judge(llm, question, answer, rubric, pass_score=4, max_attempts=2):
                ...
        ''',
        "tests": r'''
            from solution import judge

            PROMPT = ("Grade the answer.\nQuestion: What is 2+2?\nAnswer: 4\nRubric: Correct and concise\n"
                      "Reply with two lines:\nSCORE: <1-5>\nREASON: <one sentence>")

            def fake(*replies):
                seen, queue = [], list(replies)
                def llm(prompt):
                    seen.append(prompt)
                    return queue.pop(0)
                return llm, seen

            def test_prompt_and_valid_verdict():
                llm, seen = fake("SCORE: 5\nREASON:  Correct and short. ")
                got = judge(llm, "What is 2+2?", "4", "Correct and concise")
                assert seen == [PROMPT], f"prompt was {seen!r}"
                assert got == {"score": 5, "reason": "Correct and short.", "passed": True}, f"got {got!r}"

            def test_score_line_anywhere_and_pass_threshold():
                llm, _ = fake("Thinking about it...\nREASON: Mostly right\nSCORE:4  \nThanks")
                assert judge(llm, "q", "a", "r") == {"score": 4, "reason": "Mostly right", "passed": True}
                llm, _ = fake("SCORE: 4")
                assert judge(llm, "q", "a", "r", pass_score=5) == {"score": 4, "reason": "", "passed": False}

            def test_invalid_scores_trigger_a_retry():
                for bad in ("I'd give it 4/5", "SCORE: 7", "SCORE: 4.5", "score: 4", "SCORE: 45"):
                    llm, seen = fake(bad, "SCORE: 3")
                    got = judge(llm, "What is 2+2?", "4", "Correct and concise")
                    assert got == {"score": 3, "reason": "", "passed": False}, f"after {bad!r} got {got!r}"
                    assert seen[1] == PROMPT + "\n\nYour previous reply was not in the required format.", f"retry prompt was {seen[1]!r}"

            def test_judge_failed_after_max_attempts():
                llm, seen = fake("meh", "nope", "SCORE: 5")
                got = judge(llm, "q", "a", "r", max_attempts=2)
                assert got == {"score": None, "reason": "judge failed", "passed": False}, f"got {got!r}"
                assert len(seen) == 2, f"llm called {len(seen)} times"
        ''',
        "solution": r'''
            import re


            def judge(llm, question, answer, rubric, pass_score=4, max_attempts=2):
                prompt = (f"Grade the answer.\nQuestion: {question}\nAnswer: {answer}\nRubric: {rubric}\n"
                          "Reply with two lines:\nSCORE: <1-5>\nREASON: <one sentence>")
                current = prompt
                for _ in range(max_attempts):
                    reply = llm(current)
                    m = re.search(r"^SCORE:\s*([1-5])\s*$", reply, re.MULTILINE)
                    if m:
                        score = int(m.group(1))
                        r = re.search(r"^REASON:(.*)$", reply, re.MULTILINE)
                        reason = r.group(1).strip() if r else ""
                        return {"score": score, "reason": reason, "passed": score >= pass_score}
                    current = prompt + "\n\nYour previous reply was not in the required format."
                return {"score": None, "reason": "judge failed", "passed": False}
        ''',
        "hints": [
            "Regular expressions with the MULTILINE flag let `^` and `$` match at the start and end of every line.",
            "Loop up to max_attempts: call the judge, search for a strict SCORE line; if found, also look for the REASON line and return; otherwise switch to the retry prompt.",
            "Use `re.search(r'^SCORE:\\s*([1-5])\\s*$', reply, re.MULTILINE)` and `re.search(r'^REASON:(.*)$', reply, re.MULTILINE)`; strip the reason group. After the loop, return the 'judge failed' dict.",
        ],
    },
    {
        "id": "exam-evals-5",
        "title": "Release gate",
        "difficulty": 2,
        "prompt": r'''
            You changed a prompt. Before shipping, compare the new eval run with the last good one.
            A higher average is not enough: cases that used to pass and now fail (*regressions*)
            block the release.

            **Write:** `release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0)`

            - `baseline`, `candidate`: dicts mapping a case id to `True` (passed) or `False` (failed)
            - **Returns:**
              `{"ship": bool, "pass_rate": float, "regressions": list, "fixed": list, "missing": list}`

            **Rules**
            - `pass_rate`: share of `candidate` cases that passed, `round(value, 3)`; `0.0` if `candidate` is empty.
            - `regressions`: ids that passed in `baseline` and failed in `candidate`, sorted.
            - `fixed`: ids that failed in `baseline` and passed in `candidate`, sorted.
            - `missing`: ids in `baseline` that are not in `candidate` at all, sorted.
            - Ids only in `candidate` (new cases) count in `pass_rate` but in none of the lists.
            - `ship` is `True` only if `pass_rate >= min_pass_rate`, the number of regressions is
              `<= max_regressions`, **and** nothing is missing.

            **Examples**
            ```python
            base = {"a": True, "b": True, "c": False}
            cand = {"a": True, "b": False, "c": True, "d": True}
            release_gate(base, cand)
            # {"ship": False, "pass_rate": 0.75, "regressions": ["b"], "fixed": ["c"], "missing": []}

            release_gate(base, cand, min_pass_rate=0.7, max_regressions=1)["ship"]   # True
            ```
        ''',
        "starter": r'''
            def release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0):
                ...
        ''',
        "tests": r'''
            from solution import release_gate

            BASE = {"a": True, "b": True, "c": False}
            CAND = {"a": True, "b": False, "c": True, "d": True}

            def test_example_blocked_by_regression():
                got = release_gate(BASE, CAND)
                assert got == {"ship": False, "pass_rate": 0.75, "regressions": ["b"], "fixed": ["c"], "missing": []}, f"got {got!r}"

            def test_thresholds_can_allow_it():
                assert release_gate(BASE, CAND, min_pass_rate=0.7, max_regressions=1)["ship"] is True
                assert release_gate(BASE, CAND, min_pass_rate=0.76, max_regressions=1)["ship"] is False

            def test_lists_are_sorted_and_rounding():
                base = {"z": True, "m": True, "k": False, "b": False}
                cand = {"z": False, "m": False, "k": True, "b": True, "n": False, "o": False}
                got = release_gate(base, cand, min_pass_rate=0.0, max_regressions=5)
                assert got == {"ship": True, "pass_rate": 0.333, "regressions": ["m", "z"], "fixed": ["b", "k"], "missing": []}, f"got {got!r}"

            def test_missing_cases_block_the_release():
                got = release_gate({"a": True, "b": True, "q": False}, {"a": True}, min_pass_rate=0.5)
                assert got["missing"] == ["b", "q"] and got["ship"] is False, f"got {got!r}"

            def test_empty_candidate():
                got = release_gate({}, {}, min_pass_rate=0.0)
                assert got == {"ship": True, "pass_rate": 0.0, "regressions": [], "fixed": [], "missing": []}, f"got {got!r}"
        ''',
        "solution": r'''
            def release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0):
                rate = round(sum(candidate.values()) / len(candidate), 3) if candidate else 0.0
                regressions = sorted(i for i, ok in baseline.items() if ok and candidate.get(i) is False)
                fixed = sorted(i for i, ok in baseline.items() if not ok and candidate.get(i) is True)
                missing = sorted(i for i in baseline if i not in candidate)
                ship = rate >= min_pass_rate and len(regressions) <= max_regressions and not missing
                return {"ship": ship, "pass_rate": rate, "regressions": regressions, "fixed": fixed, "missing": missing}
        ''',
        "hints": [
            "Loop over the baseline ids and look each one up in the candidate with `.get()`.",
            "Build the three lists with comprehensions and `sorted`, compute the pass rate from the candidate only, then combine the three conditions for `ship`.",
            "`sum(candidate.values())` counts the Trues. regressions: baseline True and `candidate.get(id) is False`. fixed: baseline False and candidate True. missing: `id not in candidate`. ship = rate check and len(regressions) check and `not missing`.",
        ],
    },
    {
        "id": "exam-evals-6",
        "title": "A span recorder",
        "difficulty": 3,
        "research": {
            "note": "Read what a trace and a span are in OpenTelemetry (name, parent, start/end "
                    "time, attributes, status). You'll build a tiny version of the same idea.",
            "links": [
                {"title": "OpenTelemetry: traces", "url": "https://opentelemetry.io/docs/concepts/signals/traces/"},
            ],
        },
        "prompt": r'''
            To see where a slow request spends its time (retrieval? the LLM call? a tool?), wrap
            each step in a *span*. Spans nest: the LLM call happens inside the request.

            **Write:** a class `Tracer`

            - `Tracer(clock=time.perf_counter)`: `clock()` returns the current time in seconds
              (tests pass a fake clock)
            - `span(name, **attrs)`: a **context manager** used as
              `with tracer.span("llm", model="m1") as rec: ...`. It yields the span's record dict.
            - `tracer.spans`: a list of finished span records

            **Rules**
            - A record is `{"name": str, "parent": str or None, "attrs": dict, "status": str, "duration_ms": float}`.
            - `parent` is the name of the span that was open when this one started, or `None`.
            - `attrs` starts as a copy of the keyword arguments; code inside the `with` may add
              keys to `rec["attrs"]`.
            - Call `clock()` exactly once when the span starts and once when it ends.
              `duration_ms = round((end - start) * 1000, 3)`.
            - `status` is `"ok"`, or `"error"` if an exception escaped the `with` block. Then also
              set `attrs["error"]` to the exception's class name, and **let the exception propagate**.
            - A record is appended to `spans` when its span ends (so inner spans come before outer ones).

            **Examples**
            ```python
            times = iter([0.0, 0.010, 0.250, 0.300])
            t = Tracer(clock=lambda: next(times))
            with t.span("request", user="u1"):
                with t.span("llm", model="m1") as rec:
                    rec["attrs"]["tokens"] = 42
            t.spans
            # [{"name": "llm", "parent": "request", "attrs": {"model": "m1", "tokens": 42}, "status": "ok", "duration_ms": 240.0},
            #  {"name": "request", "parent": None, "attrs": {"user": "u1"}, "status": "ok", "duration_ms": 300.0}]
            ```
        ''',
        "starter": r'''
            import time


            class Tracer:
                def __init__(self, clock=time.perf_counter):
                    ...
        ''',
        "tests": r'''
            from solution import Tracer

            def clock(*times):
                calls = []
                items = list(times)
                def now():
                    calls.append(1)
                    return items.pop(0)
                return now, calls

            def test_nested_spans_in_finish_order():
                now, calls = clock(0.0, 0.010, 0.250, 0.300)
                t = Tracer(clock=now)
                with t.span("request", user="u1"):
                    with t.span("llm", model="m1") as rec:
                        rec["attrs"]["tokens"] = 42
                assert t.spans == [
                    {"name": "llm", "parent": "request", "attrs": {"model": "m1", "tokens": 42}, "status": "ok", "duration_ms": 240.0},
                    {"name": "request", "parent": None, "attrs": {"user": "u1"}, "status": "ok", "duration_ms": 300.0},
                ], f"got {t.spans!r}"
                assert len(calls) == 4, f"clock was called {len(calls)} times"

            def test_siblings_share_the_parent_and_parent_resets():
                now, _ = clock(0, 1, 2, 3, 4, 5, 6, 7)
                t = Tracer(clock=now)
                with t.span("request"):
                    with t.span("retrieve"):
                        pass
                    with t.span("llm"):
                        pass
                with t.span("next"):
                    pass
                got = [(s["name"], s["parent"]) for s in t.spans]
                assert got == [("retrieve", "request"), ("llm", "request"), ("request", None), ("next", None)], f"got {got!r}"

            def test_error_status_and_exception_propagates():
                now, _ = clock(1.0, 1.5, 1.5004, 2.0)
                t = Tracer(clock=now)
                try:
                    with t.span("request"):
                        with t.span("tool", tool="search"):
                            raise TimeoutError("slow")
                except TimeoutError:
                    pass
                else:
                    assert False, "the exception must propagate out of the with block"
                tool, req = t.spans
                assert tool == {"name": "tool", "parent": "request", "attrs": {"tool": "search", "error": "TimeoutError"},
                                "status": "error", "duration_ms": 0.4}, f"got {tool!r}"
                assert req["status"] == "error" and req["duration_ms"] == 1000.0, f"got {req!r}"

            def test_attrs_are_copied_and_default_clock_works():
                attrs = {"k": 1}
                t = Tracer(clock=clock(0, 1)[0])
                with t.span("s", **attrs) as rec:
                    rec["attrs"]["extra"] = True
                assert attrs == {"k": 1}
                t2 = Tracer()
                with t2.span("real"):
                    pass
                assert t2.spans[0]["duration_ms"] >= 0
        ''',
        "solution": r'''
            import time
            from contextlib import contextmanager


            class Tracer:
                def __init__(self, clock=time.perf_counter):
                    self.clock = clock
                    self.spans = []
                    self._open = []

                @contextmanager
                def span(self, name, **attrs):
                    rec = {"name": name, "parent": self._open[-1] if self._open else None,
                           "attrs": dict(attrs), "status": "ok", "duration_ms": 0.0}
                    self._open.append(name)
                    start = self.clock()
                    try:
                        yield rec
                    except BaseException as exc:
                        rec["status"] = "error"
                        rec["attrs"]["error"] = type(exc).__name__
                        raise
                    finally:
                        rec["duration_ms"] = round((self.clock() - start) * 1000, 3)
                        self._open.pop()
                        self.spans.append(rec)
        ''',
        "hints": [
            "`contextlib.contextmanager` turns a generator method with one `yield` into a context manager. A list used as a stack tracks which span is open.",
            "Before the yield: build the record (parent = top of the stack), push the name, read the clock. Wrap the yield in try/except/finally to mark errors and always finish the span.",
            "In `except Exception as exc`: set status and `attrs['error'] = type(exc).__name__`, then bare `raise`. In `finally`: compute duration from a second clock reading, pop the stack, append the record to `self.spans`.",
        ],
    },
    {
        "id": "exam-evals-7",
        "title": "Latency percentiles",
        "difficulty": 2,
        "research": {
            "note": "You need a standard-library function that computes percentile cut points of a "
                    "list of numbers, and the option that makes the smallest value the 0th percentile "
                    "and the largest the 100th (so results never go outside the data). Find both in the "
                    "Python docs. (Writing the interpolation yourself is also allowed.)",
            "links": [],
        },
        "prompt": r'''
            Averages hide slow requests. Dashboards show **p50** (the typical request) and **p95**
            (the slow tail). Summarise a batch of request records.

            **Write:** `latency_report(records)`

            - `records`: a list of dicts `{"ms": float, "ok": bool, "tokens": int}`
            - **Returns:** `{"count": int, "error_rate": float, "p50_ms": float, "p95_ms": float, "tokens": int}`

            **Rules**
            - `count`: number of records. `tokens`: sum of all `tokens`.
            - `error_rate`: share of records with `ok == False`, `round(value, 3)`.
            - `p50_ms` / `p95_ms`: the 50th / 95th percentile of **all** `ms` values (failed
              requests too), using **linear interpolation between the sorted values, where the
              smallest value is the 0th percentile and the largest is the 100th**. Round each with
              `round(value, 1)`.
            - One record: both percentiles are its `ms`.
            - No records: raise `ValueError("no records")`.

            **Examples**
            ```python
            ms = [120, 80, 95, 300, 110, 90, 105, 2000, 100, 85]
            latency_report([{"ms": m, "ok": m < 1000, "tokens": 10} for m in ms])
            # {"count": 10, "error_rate": 0.1, "p50_ms": 102.5, "p95_ms": 1235.0, "tokens": 100}

            latency_report([{"ms": 42.0, "ok": True, "tokens": 5}])
            # {"count": 1, "error_rate": 0.0, "p50_ms": 42.0, "p95_ms": 42.0, "tokens": 5}
            ```
        ''',
        "starter": r'''
            def latency_report(records):
                ...
        ''',
        "tests": r'''
            from solution import latency_report

            def recs(ms, bad=()):
                return [{"ms": m, "ok": i not in bad, "tokens": 10} for i, m in enumerate(ms)]

            def test_example_batch():
                got = latency_report(recs([120, 80, 95, 300, 110, 90, 105, 2000, 100, 85], bad=(7,)))
                assert got == {"count": 10, "error_rate": 0.1, "p50_ms": 102.5, "p95_ms": 1235.0, "tokens": 100}, f"got {got!r}"

            def test_small_batches_stay_inside_the_data():
                got = latency_report(recs([200.0, 100.0]))
                assert (got["p50_ms"], got["p95_ms"]) == (150.0, 195.0), f"got {got!r}"
                got = latency_report(recs([5, 1, 3], bad=(0, 2)))
                assert (got["p50_ms"], got["p95_ms"]) == (3.0, 4.8), f"got {got!r}"
                assert got["error_rate"] == 0.667, f"got {got!r}"

            def test_single_record():
                got = latency_report([{"ms": 42.0, "ok": True, "tokens": 5}])
                assert got == {"count": 1, "error_rate": 0.0, "p50_ms": 42.0, "p95_ms": 42.0, "tokens": 5}, f"got {got!r}"

            def test_no_records_raises():
                try:
                    latency_report([])
                except ValueError as e:
                    assert str(e) == "no records", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
        ''',
        "solution": r'''
            import statistics


            def latency_report(records):
                if not records:
                    raise ValueError("no records")
                ms = [r["ms"] for r in records]
                if len(ms) == 1:
                    p50 = p95 = ms[0]
                else:
                    cuts = statistics.quantiles(ms, n=100, method="inclusive")
                    p50, p95 = cuts[49], cuts[94]
                errors = sum(1 for r in records if not r["ok"])
                return {"count": len(records), "error_rate": round(errors / len(records), 3),
                        "p50_ms": round(p50, 1), "p95_ms": round(p95, 1),
                        "tokens": sum(r["tokens"] for r in records)}
        ''',
        "hints": [
            "The `statistics` module has a function that splits data into n equal groups and returns the cut points; look at its `method` parameter.",
            "Ask for 100 groups: the returned list has 99 cut points; the 50th percentile is at index 49 and the 95th at index 94. Handle 0 and 1 records before calling it.",
            "`statistics.quantiles(ms, n=100, method='inclusive')`, take `[49]` and `[94]`, round to 1. error_rate = failed / count rounded to 3; tokens = sum.",
        ],
    },
]
