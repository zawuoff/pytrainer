TOPIC = {
    "id": "evals",
    "title": "Evals: Measuring LLM Quality",
    "track": "evals",
    "order": 1,
    "requires": ["rag-answers"],
    "summary": """
        Turning "it seems to work" into numbers: eval datasets in JSONL, graders (exact,
        contains, regex, numeric, LLM-as-judge), pass rates per tag, retrieval metrics,
        comparing runs and a release gate.
    """,
    "concepts": ["eval case", "JSONL dataset", "grader", "exact match", "contains grader",
                 "regex grader", "numeric tolerance", "LLM-as-judge", "pass rate",
                 "per-tag metrics", "precision@k", "recall@k", "MRR", "regression",
                 "release gate"],
}

LESSON = r'''
## Chapter notes: evals

**Why**: trying a few prompts by hand ("vibes") does not scale. An *eval* runs your app on a
fixed set of questions and scores the answers, so every change gets a number you can compare.

**Vocabulary**
- *Eval case*: one input plus what a good answer looks like (`{"id", "input", "expected", "tags"}`).
- *Dataset*: many cases, usually stored as **JSONL** (one JSON object per line).
- *Grader*: a function `grader(output, expected) -> bool` that marks one answer.
- *Harness*: the loop that runs the model on every case and collects results.
- *Metric*: a number summarising results: pass rate, per-tag pass rate, precision@k, MRR.
- *Regression*: a case that passed before and fails now.
- *Release gate*: rules that must hold before you ship (min pass rate, no regressions).

**Graders, cheapest first**
| grader | passes when | watch out |
| --- | --- | --- |
| exact | `out.strip().lower() == exp.strip().lower()` | too strict for prose |
| contains | every required phrase is in the output | case-insensitive; empty list passes |
| regex | `re.search(pattern, out, re.IGNORECASE)` finds a match | return `bool(...)`, not the Match |
| numeric | `abs(float(out) - exp) <= tol` | `float("four")` raises ValueError: fail, don't crash |
| LLM judge | a judge model replies `VERDICT: PASS` | parse strictly; unparseable is an error |

**Metrics**
- pass rate = passed / total (0.0 for an empty run). `sum(list_of_bools)` counts the Trues.
- per tag: group results by each tag, then pass rate per group. Averages hide weak spots.
- precision@k = relevant items in the top k / k. recall@k = relevant items in the top k / all relevant.
- reciprocal rank = 1 / (position of the first relevant item, counting from 1), 0 if none.
  MRR = average reciprocal rank over queries.

**Comparing runs**: match cases by `id`. *fixed* = failed before, passes now. *regressed* =
passed before, fails now. Two runs can have the same pass rate and still behave differently.

**Gotchas**
- Inject the model (`model(input) -> str`) so evals run offline with a fake.
- A model that raises must count as a failed case, not stop the whole run.
- Keep graders deterministic; if you use an LLM judge, pin its prompt and parse its verdict.
'''

EXERCISES = [
    {
        "id": "evals-s1",
        "title": "Marking against an answer key",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Vibes don't scale

            When you change a prompt, you probably try two or three questions and think "looks
            better". That is *vibes*. It misses the question you didn't try.

            An **eval** works like a school exam. You write the questions and the answer key
            once. Every time the app changes, it sits the same exam and gets a score.

            ```python
            answer_key = {"capital of France?": "Paris", "2 + 2?": "4"}
            app_answers = {"capital of France?": "Paris", "2 + 2?": "5"}
            score = 0
            for question in answer_key:
                if app_answers[question] == answer_key[question]:
                    score += 1
            print("score:", score, "/", len(answer_key))
            ```

            The proper names: each question with its expected answer is an **eval case**, the
            collection is a **dataset**, the code that marks one answer is a **grader**, and
            `score / total` is the **pass rate**.

            Watch out: `==` is very strict. The marker in this code has no common sense.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            cases = [
                {"expected": "Paris", "output": "Paris"},
                {"expected": "4", "output": "four"},
                {"expected": "blue", "output": "Blue"},
            ]
            passed = 0
            for case in cases:
                if case["output"] == case["expected"]:
                    passed += 1
            print(passed, "of", len(cases))
            print(f"pass rate: {passed / len(cases):.2f}")
        ''',
        "solution": r'''
            1 of 3
            pass rate: 0.33
        ''',
        "explanation": r'''
            Only `"Paris" == "Paris"` is True. `"four"` is not `"4"`, and `"Blue"` is not
            `"blue"` because `==` compares letter case too. So 1 of 3 passes, and `1 / 3`
            formatted with `:.2f` is `0.33`. A grader this strict marks correct answers as wrong,
            which is why the next step normalises text first.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Check each case: is output exactly equal to expected, character by character?",
            "Capital letters matter to ==, and a word is never equal to a digit.",
            "Count the True comparisons (only one), print 'N of 3', then format N / 3 with two decimals.",
        ],
    },
    {
        "id": "evals-s2",
        "title": "A forgiving exact match",
        "difficulty": 0,
        "lesson": r'''
            ## Normalise before you compare

            A human marker would accept `" Paris\n"` for `"Paris"`. The extra space and the
            newline are noise, not a wrong answer. So before comparing, we **normalise** both
            sides: remove whitespace at the ends and make everything lowercase.

            Think of it as ironing two shirts before checking if they are the same shirt.

            ```python
            output = "  PARIS\n"
            expected = "Paris"
            print(output == expected)
            print(output.strip().lower() == expected.strip().lower())
            ```

            This is the **exact-match grader** most eval tools start with. It is still strict
            about the words themselves: `"Paris."` (with a full stop) is not a match.

            Watch out: normalise **both** sides. Only cleaning the output breaks when the
            expected answer has a capital letter.
        ''',
        "prompt": r'''
            The simplest grader: does the model's answer equal the expected answer, ignoring
            letter case and whitespace at the start/end? Replace the `___`.

            **Write:** `exact_match(output, expected)`

            - `output`: a string, the model's answer, e.g. `" Paris\n"`
            - `expected`: a string, the correct answer, e.g. `"Paris"`
            - **Returns:** `True` if they match after normalising both, otherwise `False`

            **Rules**
            - Normalise both strings: `.strip()` whitespace at the ends, then `.lower()`.
            - Anything else must match exactly (punctuation counts).

            **Examples**
            ```python
            exact_match(" Paris\n", "Paris")   # returns True
            exact_match("PARIS", "paris")      # returns True
            exact_match("Paris.", "Paris")     # returns False
            exact_match("four", "4")           # returns False
            ```
        ''',
        "starter": r'''
            def exact_match(output, expected):
                return ___ == expected.strip().lower()
        ''',
        "tests": r'''
            from solution import exact_match

            def test_whitespace_is_ignored():
                assert exact_match(" Paris\n", "Paris") is True

            def test_case_is_ignored_on_both_sides():
                assert exact_match("PARIS", "paris") is True
                assert exact_match("paris", "PARIS") is True

            def test_punctuation_still_counts():
                assert exact_match("Paris.", "Paris") is False

            def test_different_words_fail():
                assert exact_match("four", "4") is False
        ''',
        "solution": r'''
            def exact_match(output, expected):
                return output.strip().lower() == expected.strip().lower()
        ''',
        "hints": [
            "The right-hand side already shows how `expected` is cleaned. Do the same to `output`.",
            "Chain two string methods: one removes the outer whitespace, the other lowercases.",
            "Replace ___ with output followed by .strip() and then .lower().",
        ],
    },
    {
        "id": "evals-s3",
        "title": "Fix: the contains grader",
        "difficulty": 0,
        "lesson": r'''
            ## Checking for key points

            Long answers never match exactly. Instead, a teacher marking an essay checks a list:
            "did they mention the date? did they mention the cause?" Every point must be there.

            That is a **contains grader**: the answer passes only if **all** required phrases
            appear in it.

            ```python
            answer = "The refund window is 30 days from delivery."
            required = ["30 days", "delivery"]
            missing = []
            for phrase in required:
                if phrase.lower() not in answer.lower():
                    missing.append(phrase)
            print("missing:", missing)
            print("pass:", missing == [])
            ```

            The pattern "fail as soon as one thing is missing, pass only after checking all of
            them" is very common. You return `False` early inside the loop, and `True` only
            **after** the loop has finished.

            Watch out: returning `True` inside the loop means "at least one phrase is present".
            That is *any*, not *all*.
        ''',
        "prompt": r'''
            This grader should pass an answer only if it mentions **every** required phrase.
            Right now it passes answers that mention just one of them. Fix the bug.

            **Write:** `contains_all(output, required)`

            - `output`: a string, the model's answer
            - `required`: a list of strings that must all appear, e.g. `["30 days", "refund"]`
            - **Returns:** `True` if every phrase appears in `output`, otherwise `False`

            **Rules**
            - The check ignores letter case (`"Refund"` counts for `"refund"`).
            - An empty `required` list returns `True` (nothing is missing).

            **Examples**
            ```python
            contains_all("Refunds take 30 days.", ["30 days", "refund"])   # returns True
            contains_all("Refunds take a while.", ["30 days", "refund"])   # returns False
            contains_all("anything", [])                                   # returns True
            ```
        ''',
        "starter": r'''
            def contains_all(output, required):
                text = output.lower()
                for phrase in required:
                    if phrase.lower() in text:
                        return True
                return False
        ''',
        "tests": r'''
            from solution import contains_all

            def test_all_phrases_present_passes():
                assert contains_all("Refunds take 30 days.", ["30 days", "refund"]) is True

            def test_one_missing_phrase_fails():
                assert contains_all("Refunds take a while.", ["30 days", "refund"]) is False
                assert contains_all("It takes 30 days.", ["30 days", "refund"]) is False

            def test_case_is_ignored():
                assert contains_all("REFUND in 30 DAYS", ["30 days", "Refund"]) is True

            def test_empty_required_list_passes():
                assert contains_all("anything", []) is True
        ''',
        "solution": r'''
            def contains_all(output, required):
                text = output.lower()
                for phrase in required:
                    if phrase.lower() not in text:
                        return False
                return True
        ''',
        "hints": [
            "Read the loop: when does it return True? After how many phrases have been checked?",
            "It should give up as soon as one phrase is missing, and only say True once all were checked.",
            "Flip the test to `not in` and return False inside the loop; after the loop, return True.",
        ],
    },
    {
        "id": "evals-s4",
        "title": "Pass rate",
        "difficulty": 0,
        "lesson": r'''
            ## One number to compare

            After grading you have a list like `[True, False, True, True]`. You want one number
            that says how good the run was: the **pass rate**, the share of cases that passed.

            Handy fact: in Python, `True` counts as `1` and `False` as `0`. So `sum()` of a list
            of booleans counts the Trues.

            ```python
            results = [True, False, True, True]
            passed = sum(results)
            print(passed)
            print(passed / len(results))
            print(round(2 / 3, 2))
            ```

            A number that summarises results like this is called a **metric**.

            Watch out: an empty run has no cases, and `0 / 0` raises `ZeroDivisionError`.
            Decide what to return for that case before dividing.
        ''',
        "prompt": r'''
            Turn a list of grader results into a pass rate.

            **Write:** `pass_rate(results)`

            - `results`: a list of booleans, e.g. `[True, False, True, True]`
            - **Returns:** a float, the fraction of `True` values, rounded to 2 decimals

            **Rules**
            - An empty list returns `0.0` (no crash).
            - Round with `round(value, 2)`.

            **Examples**
            ```python
            pass_rate([True, False, True, True])   # returns 0.75
            pass_rate([True, False, False])        # returns 0.33
            pass_rate([])                          # returns 0.0
            ```
        ''',
        "starter": r'''
            def pass_rate(results):
                ...
        ''',
        "tests": r'''
            from solution import pass_rate

            def test_three_of_four():
                got = pass_rate([True, False, True, True])
                assert got == 0.75, f"got {got!r}"

            def test_rounds_to_two_decimals():
                got = pass_rate([True, False, False])
                assert got == 0.33, f"got {got!r}"

            def test_all_pass_is_one():
                got = pass_rate([True, True])
                assert got == 1.0, f"got {got!r}"

            def test_empty_list_is_zero():
                got = pass_rate([])
                assert got == 0.0, f"got {got!r}"
        ''',
        "solution": r'''
            def pass_rate(results):
                if not results:
                    return 0.0
                return round(sum(results) / len(results), 2)
        ''',
        "hints": [
            "sum() of a list of booleans counts how many are True.",
            "Handle the empty list first, then divide the count by the length and round.",
            "If the list is empty return 0.0; otherwise return round(sum(results) / len(results), 2).",
        ],
    },
    {
        "id": "evals-s5",
        "title": "Close enough: numeric grader",
        "difficulty": 0,
        "lesson": r'''
            ## A ruler with some slack

            If the expected answer is `3.14` and the model says `"3.1416"`, is that wrong? For
            most apps, no. Numbers need a **tolerance**: a "close enough" distance.

            Like a carpenter's measurement: 1 mm off is fine, 1 cm is not.

            ```python
            expected = 3.14
            output = "3.1416"
            value = float(output)
            print(abs(value - expected))
            print(abs(value - expected) <= 0.01)
            ```

            `abs()` gives the distance whatever the sign. The model's answer arrives as **text**,
            so you convert it with `float()` first.

            Watch out: `float("about 3")` raises `ValueError`. A grader should never crash on a
            bad answer: catch the error and mark the case as failed.
        ''',
        "prompt": r'''
            Grade numeric answers with a tolerance.

            **Write:** `numeric_match(output, expected, tolerance=0.01)`

            - `output`: a string, the model's answer, e.g. `" 3.1416 "`
            - `expected`: a number, e.g. `3.14`
            - `tolerance`: a number, the largest allowed difference (default `0.01`)
            - **Returns:** `True` if `output` is a number within `tolerance` of `expected`
              (difference `<=` tolerance), otherwise `False`

            **Rules**
            - Whitespace around the number is allowed.
            - If `output` is not a number (`float()` raises `ValueError`), return `False`; don't crash.

            **Examples**
            ```python
            numeric_match("3.1416", 3.14)             # returns True
            numeric_match("3.2", 3.14)                # returns False
            numeric_match("105", 100, tolerance=5)    # returns True
            numeric_match("about 3", 3)               # returns False
            ```
        ''',
        "starter": r'''
            def numeric_match(output, expected, tolerance=0.01):
                ...
        ''',
        "tests": r'''
            from solution import numeric_match

            def test_close_value_passes():
                assert numeric_match("3.1416", 3.14) is True

            def test_far_value_fails():
                assert numeric_match("3.2", 3.14) is False

            def test_custom_tolerance_and_whitespace():
                assert numeric_match(" 105 ", 100, tolerance=5) is True
                assert numeric_match("106", 100, tolerance=5) is False

            def test_non_number_fails_without_crashing():
                assert numeric_match("about 3", 3) is False
                assert numeric_match("", 3) is False
        ''',
        "solution": r'''
            def numeric_match(output, expected, tolerance=0.01):
                try:
                    value = float(output.strip())
                except ValueError:
                    return False
                return abs(value - expected) <= tolerance
        ''',
        "hints": [
            "Convert the text with float(), and use abs() for the distance between the two numbers.",
            "Wrap the conversion in try/except ValueError and return False there. Then compare the distance to the tolerance.",
            "try: value = float(output.strip()) / except ValueError: return False / return abs(value - expected) <= tolerance.",
        ],
    },
    {
        "id": "evals-s6",
        "title": "Load a JSONL dataset",
        "difficulty": 0,
        "lesson": r'''
            ## A box of index cards

            Eval datasets are usually stored as **JSONL** ("JSON Lines"): one complete JSON
            object per line. Think of a box of index cards: one card per test case. You can add
            a card by appending one line, and read them back one at a time.

            ```python
            import json

            text = '{"id": "q1", "input": "2+2?"}\n{"id": "q2", "input": "3+3?"}\n'
            for line in text.splitlines():
                case = json.loads(line)
                print(case["id"], "->", case["input"])
            ```

            Each line goes through `json.loads` on its own. The whole file is **not** one valid
            JSON document, so `json.loads(text)` on all of it fails.

            Watch out: files often end with a newline or contain blank lines. `json.loads("")`
            raises an error, so skip lines that are empty after `.strip()`.
        ''',
        "prompt": r'''
            Read an eval dataset stored as JSONL text.

            **Write:** `load_cases(text)`

            - `text`: a string holding JSONL: one JSON object per line
            - **Returns:** a list of dicts, one per non-blank line, in file order

            **Rules**
            - Skip lines that are empty or only whitespace.
            - Empty text returns `[]`.

            **Examples**
            ```python
            load_cases('{"id": "q1"}\n\n{"id": "q2"}\n')   # returns [{"id": "q1"}, {"id": "q2"}]
            load_cases("")                                 # returns []
            ```
        ''',
        "starter": r'''
            import json

            def load_cases(text):
                ...
        ''',
        "tests": r'''
            from solution import load_cases

            def test_two_cases_in_order():
                got = load_cases('{"id": "q1", "input": "hi"}\n{"id": "q2", "input": "yo"}\n')
                assert got == [{"id": "q1", "input": "hi"}, {"id": "q2", "input": "yo"}], f"got {got!r}"

            def test_blank_lines_are_skipped():
                got = load_cases('\n{"id": "q1"}\n   \n{"id": "q2"}\n\n')
                assert got == [{"id": "q1"}, {"id": "q2"}], f"got {got!r}"

            def test_empty_text_gives_empty_list():
                assert load_cases("") == []
        ''',
        "solution": r'''
            import json

            def load_cases(text):
                cases = []
                for line in text.splitlines():
                    if line.strip():
                        cases.append(json.loads(line))
                return cases
        ''',
        "hints": [
            "Split the text into lines and parse each line separately with json.loads.",
            "Loop over text.splitlines(); ignore lines that are empty after stripping; collect the parsed dicts.",
            "Start with an empty list; for each line, if line.strip() is not empty, append json.loads(line); return the list.",
        ],
    },
    {
        "id": "evals-s7",
        "title": "Same score, different story",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Compare case by case

            Imagine two students who both scored 2 out of 3. Did they get the **same** questions
            right? Not necessarily. One new prompt might fix a question and break another.

            So when you compare two eval runs, you don't only compare the scores. You line up
            the cases by their `id` and look at each one:

            ```python
            before = {"q1": True, "q2": False}
            after = {"q1": False, "q2": True}
            for case_id in before:
                print(case_id, before[case_id], "->", after[case_id])
            print(sum(before.values()), sum(after.values()))
            ```

            A case that passed before and fails now is a **regression**. A case that failed
            before and passes now is **fixed**. Regressions are the thing you most want to catch
            before shipping.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            baseline = {"q1": True, "q2": False, "q3": True}
            candidate = {"q1": True, "q2": True, "q3": False}
            fixed = [k for k in baseline if not baseline[k] and candidate[k]]
            broken = [k for k in baseline if baseline[k] and not candidate[k]]
            print("fixed:", fixed)
            print("broken:", broken)
            print(sum(baseline.values()), sum(candidate.values()))
        ''',
        "solution": r'''
            fixed: ['q2']
            broken: ['q3']
            2 2
        ''',
        "explanation": r'''
            `q2` failed in the baseline and passes in the candidate, so it is *fixed*. `q3`
            passed before and fails now: a *regression*. Both runs pass 2 cases, so the pass
            rates are identical - only the per-case comparison reveals that behaviour changed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Go through q1, q2, q3 and write down the baseline and candidate value for each.",
            "fixed wants False before and True after; broken wants True before and False after. sum() counts Trues.",
            "q2 is the only fixed one, q3 the only broken one, and each run has two Trues.",
        ],
    },
    {
        "id": "evals-1",
        "title": "Regex grader",
        "difficulty": 1,
        "lesson": r'''
            ## Grading by pattern

            Sometimes the answer can be written many ways, but has a shape. "The order number"
            could appear as `ORD-1234` anywhere in a sentence. Remember regular expressions? A
            **regex grader** passes the answer if the pattern is found anywhere in it.

            It's like a sniffer dog: it doesn't care about the whole bag, only whether the thing
            it's looking for is inside.

            ```python
            import re

            answer = "Your order ord-1234 has shipped."
            match = re.search(r"ORD-\d{4}", answer, re.IGNORECASE)
            print(match)
            print(bool(match))
            print(bool(re.search(r"ORD-\d{4}", "no order here")))
            ```

            `re.search` returns a **Match object** (or `None`), not `True`/`False`. Graders
            should return a real boolean, so wrap it in `bool(...)`.

            Watch out: `re.match` only looks at the **start** of the text. For "anywhere", use
            `re.search`.
        ''',
        "prompt": r'''
            Grade an answer by checking that a regular expression matches somewhere in it.

            **Write:** `regex_grade(output, pattern)`

            - `output`: a string, the model's answer
            - `pattern`: a string, a regular expression, e.g. `r"ORD-\d{4}"`
            - **Returns:** `True` if the pattern is found anywhere in `output`, otherwise `False`

            **Rules**
            - Matching ignores letter case (use the `re.IGNORECASE` flag).
            - The pattern may match in the middle of the text, not only at the start.
            - Return a real `bool` (`True`/`False`), not a Match object or `None`.

            **Examples**
            ```python
            regex_grade("Your order ord-1234 shipped", r"ORD-\d{4}")   # returns True
            regex_grade("Order ORD-12 shipped", r"ORD-\d{4}")          # returns False
            regex_grade("Due 2026-01-31.", r"\d{4}-\d{2}-\d{2}")       # returns True
            ```
        ''',
        "starter": r'''
            import re

            def regex_grade(output, pattern):
                ...
        ''',
        "tests": r'''
            from solution import regex_grade

            def test_match_in_middle_ignoring_case():
                assert regex_grade("Your order ord-1234 shipped", r"ORD-\d{4}") is True

            def test_too_few_digits_fails():
                assert regex_grade("Order ORD-12 shipped", r"ORD-\d{4}") is False

            def test_date_pattern():
                assert regex_grade("Due 2026-01-31.", r"\d{4}-\d{2}-\d{2}") is True

            def test_returns_real_booleans():
                yes = regex_grade("abc", "b")
                no = regex_grade("abc", "z")
                assert yes is True and no is False, f"got {yes!r} and {no!r}"
        ''',
        "solution": r'''
            import re

            def regex_grade(output, pattern):
                return bool(re.search(pattern, output, re.IGNORECASE))
        ''',
        "hints": [
            "re.search looks for a pattern anywhere in the text and accepts a flags argument.",
            "Search with the IGNORECASE flag, then convert the result (Match or None) into a boolean.",
            "Return bool(re.search(pattern, output, re.IGNORECASE)).",
        ],
    },
    {
        "id": "evals-2",
        "title": "The eval harness",
        "difficulty": 1,
        "lesson": r'''
            ## The exam room

            You now have graders. The **harness** is the exam room: it hands each question to
            the model, collects the answer, and gives it to the grader.

            To run evals offline (and in tests), the model is **injected** as a plain function
            `model(text) -> str`. In production it wraps a real API call; in tests it's a fake.

            ```python
            def fake_model(question):
                return {"2+2?": "4"}.get(question, "no idea")

            def grader(output, expected):
                return output == expected

            for case in [{"id": "a", "input": "2+2?", "expected": "4"}]:
                out = fake_model(case["input"])
                print(case["id"], out, grader(out, case["expected"]))
            ```

            Real model calls fail sometimes (timeouts, rate limits). One crash must not stop a
            run of 500 cases. Catch the error, record the case as failed, and move on.

            Watch out: keep results in the **same order** as the cases, and keep the `id` so you
            can compare runs later.
        ''',
        "prompt": r'''
            Run a model over a list of eval cases and grade each answer.

            **Write:** `run_eval(cases, model, grader)`

            - `cases`: a list of dicts with keys `"id"`, `"input"`, `"expected"`
            - `model`: a function taking the input string and returning the answer string
            - `grader`: a function `grader(output, expected)` returning `True`/`False`
            - **Returns:** a list of dicts, one per case, in the same order:
              `{"id": <case id>, "output": <model answer>, "passed": <grader result>}`

            **Rules**
            - Call `model` once per case with `case["input"]`.
            - If `model` raises any `Exception`, that case gets `"output": None` and
              `"passed": False` (don't call the grader), and the run continues.
            - An empty `cases` list returns `[]`.

            **Examples**
            ```python
            cases = [{"id": "q1", "input": "2+2?", "expected": "4"},
                     {"id": "q2", "input": "3+3?", "expected": "6"}]
            run_eval(cases, lambda q: "4", lambda out, exp: out == exp)
            # returns [{"id": "q1", "output": "4", "passed": True},
            #          {"id": "q2", "output": "4", "passed": False}]
            ```
        ''',
        "starter": r'''
            def run_eval(cases, model, grader):
                ...
        ''',
        "tests": r'''
            from solution import run_eval

            CASES = [{"id": "q1", "input": "2+2?", "expected": "4"},
                     {"id": "q2", "input": "3+3?", "expected": "6"}]

            def same(out, exp):
                return out == exp

            def test_grades_every_case_in_order():
                got = run_eval(CASES, lambda q: "4", same)
                assert got == [{"id": "q1", "output": "4", "passed": True},
                               {"id": "q2", "output": "4", "passed": False}], f"got {got!r}"

            def test_model_called_once_per_case_with_input():
                seen = []
                def model(q):
                    seen.append(q)
                    return "x"
                run_eval(CASES, model, same)
                assert seen == ["2+2?", "3+3?"], f"model was called with {seen!r}"

            def test_model_error_marks_case_failed_and_continues():
                def flaky(q):
                    if q == "2+2?":
                        raise TimeoutError("slow")
                    return "6"
                got = run_eval(CASES, flaky, same)
                assert got == [{"id": "q1", "output": None, "passed": False},
                               {"id": "q2", "output": "6", "passed": True}], f"got {got!r}"

            def test_empty_cases():
                assert run_eval([], lambda q: "x", same) == []
        ''',
        "solution": r'''
            def run_eval(cases, model, grader):
                results = []
                for case in cases:
                    try:
                        output = model(case["input"])
                    except Exception:
                        results.append({"id": case["id"], "output": None, "passed": False})
                        continue
                    passed = grader(output, case["expected"])
                    results.append({"id": case["id"], "output": output, "passed": passed})
                return results
        ''',
        "hints": [
            "Loop over the cases, call the model, call the grader, and build one result dict per case.",
            "Put only the model call inside try/except Exception; in the except branch append a failed result and continue.",
            "For each case: try output = model(case['input']); on Exception append {id, None, False} and continue; else append {id, output, grader(output, case['expected'])}. Return the list.",
        ],
    },
    {
        "id": "evals-3",
        "title": "Pass rate per tag",
        "difficulty": 1,
        "lesson": r'''
            ## Averages hide weak spots

            A school report shows a grade per subject, not just one average. A student with
            90% overall might still be failing chemistry.

            Evals are the same. Tag each case (`"refunds"`, `"math"`, `"multilingual"`) and
            compute the pass rate **per tag**. An overall 90% can hide a 20% on one kind of
            question.

            ```python
            results = [{"passed": True, "tags": ["math"]},
                       {"passed": False, "tags": ["math", "french"]}]
            counts = {}
            for r in results:
                for tag in r["tags"]:
                    total, ok = counts.get(tag, (0, 0))
                    counts[tag] = (total + 1, ok + int(r["passed"]))
            print(counts)
            ```

            One case can have several tags, and it counts toward **each** of them. Grouping
            like this is often called *slicing* the results.

            Watch out: some cases have no `"tags"` key at all. `r.get("tags", [])` handles that.
        ''',
        "prompt": r'''
            Break an eval run down by tag.

            **Write:** `per_tag_pass_rate(results)`

            - `results`: a list of dicts like `{"id": "q1", "passed": True, "tags": ["math"]}`
            - **Returns:** a dict mapping each tag to its pass rate (passed / total for cases
              with that tag), rounded to 2 decimals

            **Rules**
            - A case with several tags counts toward every one of its tags.
            - A case without a `"tags"` key (or with an empty list) is ignored.
            - No results returns `{}`.

            **Examples**
            ```python
            per_tag_pass_rate([
                {"id": "a", "passed": True, "tags": ["math"]},
                {"id": "b", "passed": False, "tags": ["math", "fr"]},
                {"id": "c", "passed": True, "tags": ["fr"]},
                {"id": "d", "passed": False},
            ])
            # returns {"math": 0.5, "fr": 0.5}
            ```
        ''',
        "starter": r'''
            def per_tag_pass_rate(results):
                ...
        ''',
        "tests": r'''
            from solution import per_tag_pass_rate

            def test_case_counts_for_every_tag():
                got = per_tag_pass_rate([
                    {"id": "a", "passed": True, "tags": ["math"]},
                    {"id": "b", "passed": False, "tags": ["math", "fr"]},
                    {"id": "c", "passed": True, "tags": ["fr"]},
                ])
                assert got == {"math": 0.5, "fr": 0.5}, f"got {got!r}"

            def test_rates_are_rounded():
                got = per_tag_pass_rate([
                    {"id": "a", "passed": True, "tags": ["x"]},
                    {"id": "b", "passed": False, "tags": ["x"]},
                    {"id": "c", "passed": False, "tags": ["x"]},
                ])
                assert got == {"x": 0.33}, f"got {got!r}"

            def test_untagged_cases_are_ignored():
                got = per_tag_pass_rate([{"id": "a", "passed": False},
                                         {"id": "b", "passed": True, "tags": []},
                                         {"id": "c", "passed": True, "tags": ["ok"]}])
                assert got == {"ok": 1.0}, f"got {got!r}"

            def test_no_results():
                assert per_tag_pass_rate([]) == {}
        ''',
        "solution": r'''
            def per_tag_pass_rate(results):
                totals = {}
                passes = {}
                for result in results:
                    for tag in result.get("tags", []):
                        totals[tag] = totals.get(tag, 0) + 1
                        passes[tag] = passes.get(tag, 0) + (1 if result["passed"] else 0)
                return {tag: round(passes[tag] / totals[tag], 2) for tag in totals}
        ''',
        "hints": [
            "Keep two dicts keyed by tag: how many cases had the tag, and how many of those passed.",
            "Loop over results, then over each result's tags (using .get with a default of []), updating both counters.",
            "1) totals[tag] += 1 and passes[tag] += 1 if passed (use .get(tag, 0)). 2) Build the answer with a dict comprehension: round(passes[tag] / totals[tag], 2).",
        ],
    },
    {
        "id": "evals-4",
        "title": "Precision@k and recall@k",
        "difficulty": 1,
        "lesson": r'''
            ## Grading the retriever

            In RAG, a bad answer often starts with bad retrieval. So we grade the retriever on
            its own. For each question you know which documents are **relevant**; the retriever
            returns a ranked list.

            Picture a fishing net pulling up the top `k` items:
            - **precision@k**: of the `k` items in the net, how many are fish you wanted?
            - **recall@k**: of all the fish you wanted, how many are in the net?

            ```python
            retrieved = ["d3", "d1", "d7", "d2"]
            relevant = {"d1", "d2"}
            top = retrieved[:3]
            hits = len([d for d in top if d in relevant])
            print("precision@3:", hits / 3)
            print("recall@3:", hits / len(relevant))
            ```

            Precision divides by `k` (the size of the net), recall by the number of relevant
            documents. Both are between 0 and 1.

            Watch out: if nothing is relevant, recall would divide by zero. Decide on `0.0`.
        ''',
        "prompt": r'''
            Score one retrieval result.

            **Write:** two functions, `precision_at_k(retrieved, relevant, k)` and
            `recall_at_k(retrieved, relevant, k)`

            - `retrieved`: a list of document ids in ranked order, e.g. `["d3", "d1", "d7"]`
            - `relevant`: a list or set of the ids that are actually relevant, e.g. `{"d1", "d2"}`
            - `k`: an int, how many top results to look at
            - `precision_at_k` **returns:** (relevant ids among `retrieved[:k]`) / `k`, a float
            - `recall_at_k` **returns:** (relevant ids among `retrieved[:k]`) / `len(relevant)`, a float

            **Rules**
            - Always divide precision by `k`, even if fewer than `k` ids were retrieved.
            - If `relevant` is empty, `recall_at_k` returns `0.0`.
            - If `k` is less than 1, both functions raise `ValueError`.
            - Results are compared with a tiny tolerance, so no rounding is needed.

            **Examples**
            ```python
            precision_at_k(["d3", "d1", "d7", "d2"], {"d1", "d2"}, 2)   # returns 0.5
            recall_at_k(["d3", "d1", "d7", "d2"], {"d1", "d2"}, 2)      # returns 0.5
            recall_at_k(["d3", "d1", "d7", "d2"], {"d1", "d2"}, 4)      # returns 1.0
            precision_at_k(["d1"], {"d1"}, 3)                           # returns 0.333...
            ```
        ''',
        "starter": r'''
            def precision_at_k(retrieved, relevant, k):
                ...

            def recall_at_k(retrieved, relevant, k):
                ...
        ''',
        "tests": r'''
            import math
            from solution import precision_at_k, recall_at_k

            R = ["d3", "d1", "d7", "d2"]
            REL = {"d1", "d2"}

            def test_precision_at_two():
                got = precision_at_k(R, REL, 2)
                assert math.isclose(got, 0.5), f"got {got!r}"

            def test_recall_grows_with_k():
                a, b = recall_at_k(R, REL, 2), recall_at_k(R, REL, 4)
                assert math.isclose(a, 0.5) and math.isclose(b, 1.0), f"got {a!r} and {b!r}"

            def test_precision_divides_by_k_even_if_short():
                got = precision_at_k(["d1"], ["d1"], 3)
                assert math.isclose(got, 1 / 3), f"got {got!r}"

            def test_empty_relevant_recall_is_zero():
                got = recall_at_k(R, set(), 3)
                assert got == 0.0, f"got {got!r}"

            def test_bad_k_raises_value_error():
                for fn in (precision_at_k, recall_at_k):
                    try:
                        fn(R, REL, 0)
                    except ValueError:
                        continue
                    raise AssertionError(f"{fn.__name__} with k=0 should raise ValueError")
        ''',
        "solution": r'''
            def _hits(retrieved, relevant, k):
                if k < 1:
                    raise ValueError("k must be at least 1")
                relevant = set(relevant)
                return len([doc for doc in retrieved[:k] if doc in relevant])

            def precision_at_k(retrieved, relevant, k):
                return _hits(retrieved, relevant, k) / k

            def recall_at_k(retrieved, relevant, k):
                hits = _hits(retrieved, relevant, k)
                if not relevant:
                    return 0.0
                return hits / len(relevant)
        ''',
        "hints": [
            "Both metrics need the same count: how many of the first k retrieved ids are relevant.",
            "Slice retrieved[:k], count ids that are in relevant, then divide by k (precision) or by len(relevant) (recall). Check k first.",
            "Write a helper that raises ValueError if k < 1 and returns the hit count. precision = hits / k. recall = 0.0 if relevant is empty, else hits / len(relevant).",
        ],
    },
    {
        "id": "evals-5",
        "title": "LLM-as-judge",
        "difficulty": 1,
        "lesson": r'''
            ## A second model as the marker

            Some answers can't be checked with rules: "Is this summary faithful to the
            article?" For these, teams use **LLM-as-judge**: a second model reads the question
            and the answer and gives a verdict.

            Think of a senior colleague reviewing your work with a checklist. You must tell them
            exactly how to reply, and then read their reply carefully.

            ```python
            def fake_judge(prompt):
                return "The answer cites the source.\nVERDICT: PASS"

            reply = fake_judge("Question: ...\nAnswer: ...")
            lines = [line for line in reply.splitlines() if line.strip()]
            print(lines[-1])
            print(lines[-1].strip().upper() == "VERDICT: PASS")
            ```

            Asking for reasoning first and a fixed **verdict line** last makes the reply easy to
            parse. Judges are models, so they sometimes ignore the format: treat anything else
            as an error instead of guessing.

            Watch out: `"PASS" in reply` is a trap - `"I would not PASS this"` contains it too.
        ''',
        "research": {
            "note": "Read the section on grading methods (code-based, human, LLM-based) and the "
                    "tips for LLM-based grading, then come back and build a strict verdict parser.",
            "links": [
                {"title": "Anthropic docs: create strong empirical evaluations",
                 "url": "https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests"},
                {"title": "Anthropic: demystifying evals for AI agents",
                 "url": "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents"},
            ],
        },
        "prompt": r'''
            Ask a judge model whether an answer is correct, and parse its verdict strictly.

            **Write:** `judge_verdict(question, answer, judge)`

            - `question`: a string
            - `answer`: a string, the answer being graded
            - `judge`: a function taking one prompt string and returning the judge's reply string
            - **Returns:** `True` for a PASS verdict, `False` for a FAIL verdict

            **Rules**
            - Call `judge` exactly once. The prompt you send must contain the `question` text,
              the `answer` text, and the words `VERDICT: PASS` and `VERDICT: FAIL` (so the judge
              knows the format). The rest of the wording is up to you.
            - The verdict is the **last non-blank line** of the reply, after `.strip()` and
              `.upper()`: `"VERDICT: PASS"` means `True`, `"VERDICT: FAIL"` means `False`.
            - Any other last line (or an empty reply) raises `ValueError`.

            **Examples**
            ```python
            judge_verdict("2+2?", "4", lambda p: "Correct.\nVERDICT: PASS")     # returns True
            judge_verdict("2+2?", "5", lambda p: "Wrong.\nverdict: fail\n\n")   # returns False
            judge_verdict("2+2?", "4", lambda p: "I would PASS this")          # raises ValueError
            ```
        ''',
        "starter": r'''
            def judge_verdict(question, answer, judge):
                ...
        ''',
        "tests": r'''
            from solution import judge_verdict

            def test_pass_verdict():
                assert judge_verdict("2+2?", "4", lambda p: "Correct.\nVERDICT: PASS") is True

            def test_fail_verdict_is_case_insensitive_and_ignores_trailing_blanks():
                assert judge_verdict("2+2?", "5", lambda p: "Wrong.\nverdict: fail\n\n") is False

            def test_prompt_contains_question_answer_and_format():
                prompts = []
                def judge(p):
                    prompts.append(p)
                    return "VERDICT: PASS"
                judge_verdict("What is the refund window?", "30 days", judge)
                assert len(prompts) == 1, f"judge called {len(prompts)} times"
                p = prompts[0]
                for needed in ("What is the refund window?", "30 days", "VERDICT: PASS", "VERDICT: FAIL"):
                    assert needed in p, f"prompt is missing {needed!r}"

            def test_unparseable_reply_raises_value_error():
                for reply in ("I would PASS this", "", "VERDICT: MAYBE"):
                    try:
                        judge_verdict("q", "a", lambda p: reply)
                    except ValueError:
                        continue
                    raise AssertionError(f"reply {reply!r} should raise ValueError")
        ''',
        "solution": r'''
            def judge_verdict(question, answer, judge):
                prompt = (
                    "You are grading an answer.\n"
                    f"Question: {question}\n"
                    f"Answer: {answer}\n"
                    "Explain your reasoning, then end with exactly one line: "
                    "VERDICT: PASS or VERDICT: FAIL"
                )
                reply = judge(prompt)
                lines = [line for line in reply.splitlines() if line.strip()]
                if not lines:
                    raise ValueError("empty judge reply")
                verdict = lines[-1].strip().upper()
                if verdict == "VERDICT: PASS":
                    return True
                if verdict == "VERDICT: FAIL":
                    return False
                raise ValueError(f"unparseable verdict: {lines[-1]!r}")
        ''',
        "hints": [
            "Two parts: build a prompt string with an f-string, then parse the judge's reply by lines.",
            "Keep only the lines that are not blank, take the last one, normalise it with strip() and upper(), and compare to the two allowed verdicts.",
            "1) prompt includes question, answer and the two verdict phrases. 2) reply = judge(prompt). 3) lines = non-blank lines; if none raise ValueError. 4) Compare lines[-1].strip().upper() to 'VERDICT: PASS' / 'VERDICT: FAIL', else raise ValueError.",
        ],
    },
    {
        "id": "evals-6",
        "title": "Mean reciprocal rank",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            *Mean reciprocal rank* (MRR) scores how high the **first** relevant document
            appears, averaged over many queries. Rank 1 scores 1, rank 2 scores 1/2, rank 3
            scores 1/3, and a query with no relevant result scores 0.

            **Write:** `mean_reciprocal_rank(queries)`

            - `queries`: a list of dicts, each `{"retrieved": [ids in ranked order], "relevant": [ids]}`
            - **Returns:** a float, the average of the reciprocal ranks, rounded to 3 decimals

            **Rules**
            - Ranks count from 1 (the first item in `retrieved` is rank 1).
            - Only the first relevant id counts; later ones are ignored.
            - A query with no relevant id in `retrieved` scores 0.
            - An empty `queries` list returns `0.0`.

            **Examples**
            ```python
            mean_reciprocal_rank([
                {"retrieved": ["a", "b", "c"], "relevant": ["a"]},   # rank 1 -> 1
                {"retrieved": ["x", "y", "b"], "relevant": ["b"]},   # rank 3 -> 0.333...
                {"retrieved": ["x"], "relevant": ["z"]},             # none  -> 0
            ])
            # returns 0.444
            mean_reciprocal_rank([])   # returns 0.0
            ```
        ''',
        "starter": r'''
            def mean_reciprocal_rank(queries):
                ...
        ''',
        "tests": r'''
            from solution import mean_reciprocal_rank

            def test_mixed_ranks():
                got = mean_reciprocal_rank([
                    {"retrieved": ["a", "b", "c"], "relevant": ["a"]},
                    {"retrieved": ["x", "y", "b"], "relevant": ["b"]},
                    {"retrieved": ["x"], "relevant": ["z"]},
                ])
                assert got == 0.444, f"got {got!r}"

            def test_only_first_relevant_counts():
                got = mean_reciprocal_rank([{"retrieved": ["x", "a", "b"], "relevant": ["b", "a"]}])
                assert got == 0.5, f"got {got!r}"

            def test_all_first_is_one():
                got = mean_reciprocal_rank([{"retrieved": ["a"], "relevant": ["a"]},
                                            {"retrieved": ["b", "c"], "relevant": ["b"]}])
                assert got == 1.0, f"got {got!r}"

            def test_empty_queries():
                assert mean_reciprocal_rank([]) == 0.0
        ''',
        "solution": r'''
            def mean_reciprocal_rank(queries):
                if not queries:
                    return 0.0
                total = 0.0
                for query in queries:
                    relevant = set(query["relevant"])
                    for rank, doc in enumerate(query["retrieved"], start=1):
                        if doc in relevant:
                            total += 1 / rank
                            break
                return round(total / len(queries), 3)
        ''',
        "hints": [
            "For each query find the position of the first relevant id; enumerate(..., start=1) gives ranks from 1.",
            "Add 1/rank for the first hit and stop looking (break); queries without a hit add nothing. Divide by the number of queries.",
            "Return 0.0 for no queries. total = 0; for each query loop with enumerate(start=1), on the first doc in relevant add 1 / rank and break. Return round(total / len(queries), 3).",
        ],
    },
    {
        "id": "evals-7",
        "title": "Compare two runs",
        "difficulty": 2,
        "prompt": r'''
            Before merging a prompt change, compare the new eval run (candidate) with the
            current one (baseline), case by case.

            **Write:** `compare_runs(baseline, candidate)`

            - `baseline`, `candidate`: lists of results like `{"id": "q1", "passed": True}`
            - **Returns:** a dict with three keys:
              - `"fixed"`: sorted list of ids that failed in baseline and pass in candidate
              - `"regressed"`: sorted list of ids that passed in baseline and fail in candidate
              - `"delta"`: candidate pass rate minus baseline pass rate, rounded to 3 decimals

            **Rules**
            - Match cases by `"id"`. Ids present in only one run are not fixed or regressed.
            - Each pass rate uses that run's own list (passed / total); an empty run has rate `0.0`.
            - Don't modify the input lists.

            **Examples**
            ```python
            base = [{"id": "q1", "passed": True}, {"id": "q2", "passed": False}, {"id": "q3", "passed": True}]
            cand = [{"id": "q3", "passed": False}, {"id": "q2", "passed": True}, {"id": "q1", "passed": True}]
            compare_runs(base, cand)   # returns {"fixed": ["q2"], "regressed": ["q3"], "delta": 0.0}
            compare_runs([], [{"id": "a", "passed": True}])
            # returns {"fixed": [], "regressed": [], "delta": 1.0}
            ```
        ''',
        "starter": r'''
            def compare_runs(baseline, candidate):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import compare_runs

            BASE = [{"id": "q1", "passed": True}, {"id": "q2", "passed": False}, {"id": "q3", "passed": True}]
            CAND = [{"id": "q3", "passed": False}, {"id": "q2", "passed": True}, {"id": "q1", "passed": True}]

            def test_matches_cases_by_id_not_position():
                got = compare_runs(BASE, CAND)
                assert got == {"fixed": ["q2"], "regressed": ["q3"], "delta": 0.0}, f"got {got!r}"

            def test_lists_are_sorted_and_delta_rounded():
                base = [{"id": "b", "passed": False}, {"id": "a", "passed": False}, {"id": "c", "passed": True}]
                cand = [{"id": "a", "passed": True}, {"id": "b", "passed": True}, {"id": "c", "passed": True}]
                got = compare_runs(base, cand)
                assert got == {"fixed": ["a", "b"], "regressed": [], "delta": 0.667}, f"got {got!r}"

            def test_ids_in_one_run_only_are_ignored():
                got = compare_runs([{"id": "old", "passed": True}], [{"id": "new", "passed": False}])
                assert got == {"fixed": [], "regressed": [], "delta": -1.0}, f"got {got!r}"

            def test_empty_baseline():
                got = compare_runs([], [{"id": "a", "passed": True}])
                assert got == {"fixed": [], "regressed": [], "delta": 1.0}, f"got {got!r}"

            def test_inputs_not_modified():
                base, cand = copy.deepcopy(BASE), copy.deepcopy(CAND)
                compare_runs(base, cand)
                assert base == BASE and cand == CAND, "the input lists were changed"
        ''',
        "solution": r'''
            def _rate(run):
                if not run:
                    return 0.0
                return sum(1 for r in run if r["passed"]) / len(run)

            def compare_runs(baseline, candidate):
                before = {r["id"]: r["passed"] for r in baseline}
                after = {r["id"]: r["passed"] for r in candidate}
                shared = [i for i in before if i in after]
                fixed = sorted(i for i in shared if not before[i] and after[i])
                regressed = sorted(i for i in shared if before[i] and not after[i])
                delta = round(_rate(candidate) - _rate(baseline), 3)
                return {"fixed": fixed, "regressed": regressed, "delta": delta}
        ''',
        "hints": [
            "Turn each run into a dict of id -> passed so you can look cases up by id.",
            "Only ids in both dicts can be fixed or regressed. Compute each run's pass rate separately (guard the empty run) and subtract.",
            "1) before/after dicts via comprehensions. 2) fixed = sorted ids in both with not before and after; regressed the opposite. 3) delta = round(rate(candidate) - rate(baseline), 3).",
        ],
    },
    {
        "id": "evals-8",
        "title": "Release gate",
        "difficulty": 3,
        "lesson": r'''
            ## Putting it together: a gate before shipping

            A release gate is the bouncer at the door: a change ships only if the eval numbers
            meet fixed rules. Teams run it in CI on every pull request, so "is this better?" is
            answered by code, not by opinion.
        ''',
        "prompt": r'''
            Decide whether a candidate may ship, and explain why not when it can't.

            **Write:** `release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0)`

            - `baseline`, `candidate`: lists of results like `{"id": "q1", "passed": True}`
            - `min_pass_rate`: a float, the lowest acceptable candidate pass rate
            - `max_regressions`: an int, the most regressions allowed
            - **Returns:** a tuple `(ok, reasons)`: `reasons` is a list of strings, `ok` is
              `True` exactly when `reasons` is empty

            **Rules** - check in this order and add one reason per failed rule:
            1. Missing cases: ids in `baseline` that are not in `candidate`. Reason:
               `"missing cases: q4, q5"` (ids sorted, joined with `", "`).
            2. Pass rate: candidate pass rate (passed / total, `0.0` if empty) below
               `min_pass_rate`. Reason: `"pass rate 0.50 below 0.80"` (both with 2 decimals).
            3. Regressions (passed in baseline, fail in candidate) more than `max_regressions`.
               Reason: `"2 regressions: q1, q3"` (ids sorted, joined with `", "`).

            **Examples**
            ```python
            base = [{"id": "q1", "passed": True}, {"id": "q2", "passed": True}]
            release_gate(base, [{"id": "q1", "passed": True}, {"id": "q2", "passed": True}])
            # returns (True, [])
            release_gate(base, [{"id": "q1", "passed": False}, {"id": "q2", "passed": True}])
            # returns (False, ["pass rate 0.50 below 0.80", "1 regressions: q1"])
            release_gate(base, [{"id": "q1", "passed": True}], min_pass_rate=0.5)
            # returns (False, ["missing cases: q2"])
            ```
        ''',
        "starter": r'''
            def release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0):
                ...
        ''',
        "tests": r'''
            from solution import release_gate

            BASE = [{"id": "q1", "passed": True}, {"id": "q2", "passed": True}]

            def test_clean_candidate_ships():
                got = release_gate(BASE, [{"id": "q1", "passed": True}, {"id": "q2", "passed": True}])
                assert tuple(got) == (True, []), f"got {got!r}"

            def test_low_rate_and_regression_both_reported_in_order():
                got = release_gate(BASE, [{"id": "q1", "passed": False}, {"id": "q2", "passed": True}])
                assert tuple(got) == (False, ["pass rate 0.50 below 0.80", "1 regressions: q1"]), f"got {got!r}"

            def test_missing_cases_block_release():
                got = release_gate(BASE, [{"id": "q1", "passed": True}], min_pass_rate=0.5)
                assert tuple(got) == (False, ["missing cases: q2"]), f"got {got!r}"

            def test_allowed_regressions_and_sorted_ids():
                base = [{"id": c, "passed": True} for c in ("q3", "q1", "q2")] + [{"id": "q4", "passed": False}]
                cand = [{"id": "q3", "passed": False}, {"id": "q1", "passed": False},
                        {"id": "q2", "passed": True}, {"id": "q4", "passed": True}]
                ok, reasons = release_gate(base, cand, min_pass_rate=0.5, max_regressions=1)
                assert (ok, reasons) == (False, ["2 regressions: q1, q3"]), f"got {(ok, reasons)!r}"
                ok, reasons = release_gate(base, cand, min_pass_rate=0.5, max_regressions=2)
                assert (ok, reasons) == (True, []), f"got {(ok, reasons)!r}"

            def test_empty_candidate():
                ok, reasons = release_gate([], [], min_pass_rate=0.8)
                assert (ok, reasons) == (False, ["pass rate 0.00 below 0.80"]), f"got {(ok, reasons)!r}"
        ''',
        "solution": r'''
            def release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0):
                before = {r["id"]: r["passed"] for r in baseline}
                after = {r["id"]: r["passed"] for r in candidate}
                reasons = []
                missing = sorted(i for i in before if i not in after)
                if missing:
                    reasons.append("missing cases: " + ", ".join(missing))
                rate = sum(1 for r in candidate if r["passed"]) / len(candidate) if candidate else 0.0
                if rate < min_pass_rate:
                    reasons.append(f"pass rate {rate:.2f} below {min_pass_rate:.2f}")
                regressed = sorted(i for i in before if i in after and before[i] and not after[i])
                if len(regressed) > max_regressions:
                    reasons.append(f"{len(regressed)} regressions: " + ", ".join(regressed))
                return not reasons, reasons
        ''',
        "hints": [
            "Build id -> passed dicts for both runs, then check the three rules one after another, appending a reason string for each failure.",
            "Missing = baseline ids not in candidate. Rate = candidate passes / len(candidate), guarding empty. Regressions = ids True before and False after. Format with :.2f and ', '.join(sorted(...)).",
            "1) reasons = []. 2) if missing: append 'missing cases: ' + joined ids. 3) if rate < min_pass_rate: append the f-string. 4) if len(regressed) > max_regressions: append the f-string. 5) return (not reasons, reasons).",
        ],
    },
    {
        "id": "evals-9",
        "title": "A full eval suite",
        "difficulty": 3,
        "lesson": r'''
            ## Putting it together: a real eval run

            Real datasets mix grader types: some cases need exact answers, others key phrases,
            others a pattern or a number. Each case says which grader to use, and one report
            summarises the whole run. This is a small version of what eval frameworks do.
        ''',
        "prompt": r'''
            Run a JSONL eval dataset where every case names its own grader, and summarise it.

            **Write:** `run_suite(jsonl_text, model)`

            - `jsonl_text`: a string, one JSON case per line (skip blank lines). Each case has
              `"id"`, `"input"`, `"grader"`, `"expected"` and optionally `"tags"` (list of strings)
            - `model`: a function taking the input string and returning an answer string
            - **Returns:** a dict:
              `{"total": int, "passed": int, "pass_rate": float, "by_tag": dict, "failed_ids": list}`

            **Graders** (by the case's `"grader"` value):
            - `"exact"`: `output.strip().lower() == expected.strip().lower()`
            - `"contains"`: `expected` is a list; every item appears in the output, ignoring case
            - `"regex"`: `expected` is a pattern; `re.search` finds it, ignoring case
            - `"numeric"`: output converts with `float()` and is within `0.01` of `expected`;
              a non-number fails

            **Rules**
            - An unknown grader name raises `ValueError` with the message `unknown grader: <name>`
              (e.g. `unknown grader: vibes`); this error is not caught.
            - If `model` raises any `Exception`, that case fails; the run continues.
            - `pass_rate` = passed / total rounded to 2 decimals (`0.0` if no cases).
            - `by_tag`: tag -> pass rate rounded to 2 decimals (cases without tags are skipped).
            - `failed_ids`: ids of failed cases in dataset order.

            **Examples**
            ```python
            data = (
                '{"id": "a", "input": "capital of France?", "grader": "exact", "expected": "Paris", "tags": ["geo"]}\n'
                '{"id": "b", "input": "pi?", "grader": "numeric", "expected": 3.14, "tags": ["math"]}\n'
                '{"id": "c", "input": "order?", "grader": "regex", "expected": "ORD-[0-9]+", "tags": ["geo", "math"]}\n'
            )
            answers = {"capital of France?": " paris", "pi?": "3.1416", "order?": "none"}
            run_suite(data, lambda q: answers[q])
            # returns {"total": 3, "passed": 2, "pass_rate": 0.67,
            #          "by_tag": {"geo": 0.5, "math": 0.5}, "failed_ids": ["c"]}
            ```
        ''',
        "starter": r'''
            import json
            import re

            def run_suite(jsonl_text, model):
                ...
        ''',
        "tests": r'''
            import json
            from solution import run_suite

            def jsonl(*cases):
                return "\n".join(json.dumps(c) for c in cases) + "\n"

            DATA = jsonl(
                {"id": "a", "input": "capital of France?", "grader": "exact", "expected": "Paris", "tags": ["geo"]},
                {"id": "b", "input": "pi?", "grader": "numeric", "expected": 3.14, "tags": ["math"]},
                {"id": "c", "input": "order?", "grader": "regex", "expected": "ORD-\\d+", "tags": ["geo", "math"]},
            )
            ANSWERS = {"capital of France?": " paris", "pi?": "3.1416", "order?": "none"}

            def test_mixed_graders_report():
                got = run_suite(DATA, lambda q: ANSWERS[q])
                assert got == {"total": 3, "passed": 2, "pass_rate": 0.67,
                               "by_tag": {"geo": 0.5, "math": 0.5}, "failed_ids": ["c"]}, f"got {got!r}"

            def test_contains_grader_and_blank_lines():
                data = "\n" + jsonl({"id": "r", "input": "refund?", "grader": "contains",
                                     "expected": ["30 days", "Receipt"]}) + "\n\n"
                ok = run_suite(data, lambda q: "Bring your RECEIPT within 30 days")
                bad = run_suite(data, lambda q: "Within 30 days")
                assert ok["passed"] == 1 and bad["failed_ids"] == ["r"], f"got {ok!r} / {bad!r}"
                assert ok["by_tag"] == {}, f"untagged cases should not appear in by_tag: {ok['by_tag']!r}"

            def test_numeric_non_number_and_model_errors_fail():
                data = jsonl({"id": "n", "input": "x", "grader": "numeric", "expected": 2},
                             {"id": "e", "input": "boom", "grader": "exact", "expected": "ok"},
                             {"id": "k", "input": "y", "grader": "exact", "expected": "ok"})
                def model(q):
                    if q == "boom":
                        raise RuntimeError("rate limited")
                    return "two" if q == "x" else "OK"
                got = run_suite(data, model)
                assert got["failed_ids"] == ["n", "e"] and got["passed"] == 1, f"got {got!r}"
                assert got["pass_rate"] == 0.33, f"got {got!r}"

            def test_unknown_grader_raises_value_error():
                data = jsonl({"id": "z", "input": "q", "grader": "vibes", "expected": "?"})
                try:
                    run_suite(data, lambda q: "?")
                except ValueError as exc:
                    assert "unknown grader: vibes" in str(exc), f"message was {str(exc)!r}"
                    return
                raise AssertionError("an unknown grader should raise ValueError")

            def test_empty_dataset():
                got = run_suite("", lambda q: "")
                assert got == {"total": 0, "passed": 0, "pass_rate": 0.0, "by_tag": {}, "failed_ids": []}, f"got {got!r}"
        ''',
        "solution": r'''
            import json
            import re

            def _exact(output, expected):
                return output.strip().lower() == expected.strip().lower()

            def _contains(output, expected):
                text = output.lower()
                return all(item.lower() in text for item in expected)

            def _regex(output, expected):
                return bool(re.search(expected, output, re.IGNORECASE))

            def _numeric(output, expected):
                try:
                    return abs(float(output.strip()) - expected) <= 0.01
                except ValueError:
                    return False

            GRADERS = {"exact": _exact, "contains": _contains, "regex": _regex, "numeric": _numeric}

            def run_suite(jsonl_text, model):
                cases = [json.loads(line) for line in jsonl_text.splitlines() if line.strip()]
                passed = 0
                failed_ids = []
                tag_total, tag_pass = {}, {}
                for case in cases:
                    grader = GRADERS.get(case["grader"])
                    if grader is None:
                        raise ValueError(f"unknown grader: {case['grader']}")
                    try:
                        ok = grader(model(case["input"]), case["expected"])
                    except Exception:
                        ok = False
                    if ok:
                        passed += 1
                    else:
                        failed_ids.append(case["id"])
                    for tag in case.get("tags", []):
                        tag_total[tag] = tag_total.get(tag, 0) + 1
                        tag_pass[tag] = tag_pass.get(tag, 0) + (1 if ok else 0)
                total = len(cases)
                return {
                    "total": total,
                    "passed": passed,
                    "pass_rate": round(passed / total, 2) if total else 0.0,
                    "by_tag": {t: round(tag_pass[t] / tag_total[t], 2) for t in tag_total},
                    "failed_ids": failed_ids,
                }
        ''',
        "hints": [
            "Reuse the graders from earlier steps and keep them in a dict that maps a grader name to a function.",
            "Parse the JSONL, look up each case's grader (raise ValueError if missing), run the model inside try/except, and update the counters and per-tag tallies.",
            "1) cases from non-blank lines via json.loads. 2) GRADERS = {'exact': ..., ...}. 3) For each case: grader lookup, try ok = grader(model(input), expected) except Exception: ok = False; count passes, collect failed ids, tally tags. 4) Build the report dict with the rounded rates.",
        ],
    },
]
