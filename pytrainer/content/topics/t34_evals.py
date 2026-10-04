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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["eval", "evaluation", "grader", "exact match", "tolerance", "pass rate",
                 "metric", "precision", "recall", "mrr", "reciprocal rank", "regression",
                 "baseline", "release gate", "judge", "jsonl"],
    "cards": [
        {
            "syntax": "output.strip().lower() == expected.strip().lower()",
            "explain": "Exact-match grader. Removes outer whitespace and lowercases both strings, then compares them.",
            "example": r'''
                def exact(output, expected):
                    return output.strip().lower() == expected.strip().lower()

                print(exact(" paris\n", "Paris"))
                # True
                print(exact("Paris.", "Paris"))
                # False
            ''',
        },
        {
            "syntax": "abs(float(output) - expected) <= tolerance",
            "explain": "Numeric grader. Passes when the answer differs from the expected number by at most tolerance.",
            "example": r'''
                print(abs(float("3.1416") - 3.14) <= 0.01)
                # True
                print(abs(float("3.2") - 3.14) <= 0.01)
                # False
            ''',
        },
        {
            "syntax": "sum(results) / len(results)",
            "explain": "Pass rate: passed cases divided by all cases. sum() counts the True values. Check for an empty list first.",
            "example": r'''
                results = [True, False, True, True]
                print(sum(results), "of", len(results))
                # 3 of 4
                print(sum(results) / len(results))
                # 0.75
            ''',
        },
        {
            "syntax": "hits / k   and   hits / len(relevant)",
            "explain": "precision@k and recall@k. hits is how many of the first k retrieved ids are relevant.",
            "example": r'''
                top = ["d3", "d1", "d7"]
                relevant = {"d1", "d2"}
                hits = len([d for d in top if d in relevant])
                print(hits)
                # 1
                print(round(hits / 3, 2), hits / len(relevant))
                # 0.33 0.5
            ''',
        },
        {
            "syntax": "sum(reciprocal_ranks) / len(reciprocal_ranks)",
            "explain": "MRR. Each query scores 1 / rank of its first relevant result, or 0 with none. MRR is the average.",
            "example": r'''
                first_ranks = [1, 2, None]
                scores = [1 / r if r else 0.0 for r in first_ranks]
                print(scores)
                # [1.0, 0.5, 0.0]
                print(sum(scores) / len(scores))
                # 0.5
            ''',
        },
        {
            "syntax": "before[i] and not after[i]",
            "explain": "A regression: case i passed in the baseline run and fails in the candidate run.",
            "example": r'''
                before = {"q1": True, "q2": False}
                after = {"q1": False, "q2": True}
                print([i for i in before if before[i] and not after[i]])
                # ['q1']
                print([i for i in before if not before[i] and after[i]])
                # ['q2']
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: evals

An **eval** is a program that runs your app on a fixed set of inputs and scores every output.
Trying a few prompts by hand only tests the inputs you thought of that day. An eval tests the
same inputs after every change, so each change gets a number you can compare.

### Eval cases and datasets

An **eval case** is one input plus a description of a correct answer. A case is usually a dict
with the keys `"id"`, `"input"`, `"expected"` and `"tags"`. A **dataset** is a list of cases.
Datasets are usually stored as **JSONL**: a text file with one JSON object per line.

### Graders

A **grader** is a function `grader(output, expected)` that returns `True` when one answer is
acceptable and `False` when it is not.

```python
def exact(output, expected):
    return output.strip().lower() == expected.strip().lower()

print(exact(" paris\n", "Paris"))
# True
print(exact("Paris.", "Paris"))
# False
```

The common graders, from cheapest to most expensive:

- **Exact match** compares both strings after `.strip().lower()`. It is too strict for long answers.
- **Contains** passes when every required phrase is in the output, ignoring letter case. An
  empty list of phrases passes.
- **Regex** passes when `re.search(pattern, output, re.IGNORECASE)` finds a match. Return
  `bool(...)` of the result, because `re.search` returns a Match object (an object that
  describes where the pattern matched) or `None`.
- **Numeric** passes when `abs(float(output) - expected) <= tolerance`, where `tolerance` is the
  largest difference that still counts as correct. `float("four")` raises
  `ValueError`, so catch it and return `False`.
- **LLM-as-judge** sends the question and the answer to a second model, which replies with
  `VERDICT: PASS` or `VERDICT: FAIL`. Any other reply is an error.

### The eval run

A **harness** is the loop that calls the model on every case, grades each output and collects
the results. The model is passed in as a function `model(text)` that returns a string. A test
passes a fake function, so the eval runs without a network call.

```python
def exact(output, expected):
    return output.strip().lower() == expected.strip().lower()

def fake_model(text):
    return {"capital of France?": " paris\n"}.get(text, "five")

cases = [
    {"id": "q1", "input": "capital of France?", "expected": "Paris"},
    {"id": "q2", "input": "2 + 2?", "expected": "4"},
]
results = []
for case in cases:
    output = fake_model(case["input"])
    results.append({"id": case["id"], "passed": exact(output, case["expected"])})
print(results)
# [{'id': 'q1', 'passed': True}, {'id': 'q2', 'passed': False}]
passed = sum(r["passed"] for r in results)
print(passed / len(results))
# 0.5
```

Step through the stages to see the data that each one produces.

```diagram
{"type":"flow","title":"One eval run","steps":[
{"label":"Dataset","detail":"The dataset is a list of cases. Each case has an id, an input and an expected answer.","code":"{\"id\": \"q1\", \"input\": \"capital of France?\", \"expected\": \"Paris\"}\n{\"id\": \"q2\", \"input\": \"2 + 2?\", \"expected\": \"4\"}"},
{"label":"Run the model","detail":"The harness calls the model once per case with the case input. The return value is the output string.","code":"fake_model(\"capital of France?\")  returns ' paris\\n'\nfake_model(\"2 + 2?\")              returns 'five'"},
{"label":"Grade each output","detail":"The grader compares each output with the expected answer of the same case and returns True or False.","code":"exact(' paris\\n', 'Paris')  returns True\nexact('five', '4')          returns False"},
{"label":"Collect results","detail":"The harness stores one result per case, in dataset order, with the case id.","code":"[{'id': 'q1', 'passed': True},\n {'id': 'q2', 'passed': False}]"},
{"label":"Aggregate","detail":"The pass rate is the number of passed cases divided by the number of cases.","code":"passed = 1\ntotal = 2\npass rate = 1 / 2 = 0.5"}
]}
```

### Metrics

A **metric** is one number that summarises the results of a run.

- The **pass rate** is passed cases divided by total cases. Use `0.0` for an empty run.
  `sum()` of a list of booleans counts the `True` values.
- The **pass rate per tag** groups the results by tag and computes one pass rate per group. A
  high overall pass rate can include a tag with a low one.

The next three metrics score a retriever. A document is **relevant** to a question when it
contains the answer. You write down the relevant ids for each question yourself. `k` is how
many results you look at, counted from the start of the ranked list.

- **precision@k** is the number of relevant items in the top `k` results divided by `k`.
- **recall@k** is the number of relevant items in the top `k` results divided by the number
  of relevant items.
- The **rank** of a result is its position in the list, counting from 1. The **reciprocal
  rank** of a query is `1 / rank` of the first relevant result. It is `0` when no result is
  relevant. **MRR** (mean reciprocal rank) is the average reciprocal rank over all queries.

```python
retrieved = ["d3", "d1", "d7", "d2"]
relevant = {"d1", "d2"}
hits = 0
for doc in retrieved[:3]:
    if doc in relevant:
        hits += 1
print(hits)
# 1
print(round(hits / 3, 2))
# 0.33
print(hits / len(relevant))
# 0.5
reciprocal_rank = 0.0
for rank, doc in enumerate(retrieved, start=1):
    if doc in relevant:
        reciprocal_rank = 1 / rank
        break
print(reciprocal_rank)
# 0.5
```

The top 3 results are `d3`, `d1` and `d7`. Only `d1` is relevant, so there is 1 relevant item.
precision@3 is `1 / 3`, which rounds to `0.33`. There are 2 relevant ids, so recall@3 is
`1 / 2`. The first relevant result is `d1` at rank 2, so the reciprocal rank is `1 / 2`.

For MRR, take three queries with reciprocal ranks `1`, `0.5` and `0`. The MRR is
`(1 + 0.5 + 0) / 3`, which is `0.5`.

### Comparing runs

The **baseline** is the run of the current version of your app. The **candidate** is the run
of the version with your change. Match the cases of the two runs by `"id"`. A case is
**fixed** when it failed in the baseline and passes in the candidate. A case is a
**regression** when it passed in the baseline and fails in the candidate. Two runs can have
the same pass rate and still pass different cases.

A **release gate** is a set of rules that a run must meet before the change is released to
users, for example a minimum pass rate and zero regressions.

### Common mistakes

- Calling a real API inside the harness. Pass the model in as a function so tests can use a fake.
- Letting one model error stop the run. Catch the exception and record that case as failed.
- Checking `"PASS" in reply` for a judge. `"I would not PASS this"` contains it too. Compare the
  whole last line.
- Dividing by `len(results)` without checking for an empty list. That raises `ZeroDivisionError`.
'''

EXERCISES = [
    {
        "id": "evals-s1",
        "title": "Marking against an answer key",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Check the same questions after every change

            You change the wording of a prompt and the answers look better. But did yesterday's working answers survive? You need a repeatable way to ask the same questions and compare what came back.

            ```python
            expected = ["red", "7"]
            answers = ["red", "seven"]
            checks = [answers[i] == expected[i] for i in range(2)]
            print(checks)
            # [True, False]
            print(sum(checks), "passed")
            # 1 passed
            ```

            Each comparison produces a boolean. The first answer matches exactly; the second uses a word where the expected answer uses a digit. Nothing in this comparison decides whether those mean the same thing. You chose a rule that compares characters.

            A repeatable check of an app's answers is an **evaluation**, usually shortened to **eval**. One question and its expected answer form a **case**. The collection of cases is the **dataset**. The rule that marks an answer is the **grader**. These names describe different parts of the process; the dataset does not decide what counts as correct.

            ```match
            case :: one input with its expected answer
            dataset :: the collection of cases
            grader :: the rule that marks an answer
            ---
            Keeping these parts separate lets you improve the marking rule without changing the questions.
            ```


            Try one more small check before moving to the task.

            ```predict
            print("seven" == "7")
            ---
            Character equality does not decide whether different text has the same numerical meaning.
            ```

            **Watch out:** A correct meaning can fail an exact text comparison. Seeing a failed case tells you to inspect both the answer and the grading rule.

            **In short:** An eval repeats chosen questions and marks each answer with a chosen rule.
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
            formatted with `:.2f` is `0.33`. A grader this strict fails correct answers, so the
            next step converts both strings to the same form before comparing them.

            Follow each printed line in execution order. Changes to a variable affect later lines; they do not change output that was already printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Look at the comparison used for each case, rather than deciding whether its meaning sounds right.",
            "Track the boolean produced for each pair of strings, including differences in case.",
            "Count the successful comparisons, then follow the two print calls and their number formatting.",
        ],
    },
    {
        "id": "evals-s2",
        "title": "A forgiving exact match",
        "difficulty": 0,
        "lesson": r'''
            ## Ignore harmless differences in an answer

            Your answer key says "London", but the model writes " LONDON ". You want that answer to pass while still rejecting another city. Decide which differences are harmless before comparing the strings.

            ```python
            reply = "  LONDON\n"
            key = "London"
            clean_reply = reply.strip().lower()
            clean_key = key.strip().lower()
            print(clean_reply)
            # london
            print(clean_reply == clean_key)
            # True
            ```

            The first method removes whitespace from the ends. The second changes uppercase letters to lowercase. Neither removes spaces inside a sentence or punctuation. Both strings now have the same chosen form, so comparing them is meaningful.

            Converting values to a shared form is called **normalisation**. A grader that compares the complete normalised strings is a **normalised exact-match grader**. "London." would still differ from "London" because its full stop survives these two methods. You are deliberately allowing a narrow set of differences, rather than accepting anything that resembles the expected answer.

            Apply the same rule to the answer and the answer key. The key may have its own uppercase letters or extra whitespace.

            ```predict
            print("  Green ".strip().lower() == "GREEN".strip().lower())
            print("green.".strip().lower() == "green".strip().lower())
            ---
            The first pair becomes the same string. The full stop in the second pair is preserved, so that comparison is False.
            ```


            Try one more small check before moving to the task.

            ```predict
            print("Blue sky".lower() == "blue  sky".lower())
            ---
            Case normalisation preserves the extra internal space, so these strings remain different.
            ```

            **Watch out:** Cleaning only one side can reject a correct answer. The methods return new strings; the original strings stay unchanged.

            **In short:** Choose harmless differences, remove them from both strings, then compare.
        ''',
        "prompt": r'''
            An answer can have the right text with harmless whitespace or case differences. Complete the gap in `exact_match` so those differences are accepted.

            **Your job:** `exact_match(output, expected)`

            **What goes in**
            - `output`: a string, the model's answer, e.g. `" Paris\n"`
            - `expected`: a string, the correct answer, e.g. `"Paris"`

            **What comes out**
            - `True` if they match after normalising both, otherwise `False`

            **Rules**
            - Ignore whitespace at the start and end of both strings, and compare without regard to letter case.
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
            "Which two harmless differences does the lesson remove?",
            "Compare two strings that have both been put into the same form.",
            "Follow the already-completed side of the comparison: clean the ends, make the case consistent, and compare the resulting text.",
        ],
    },
    {
        "id": "evals-s3",
        "title": "Fix: the contains grader",
        "difficulty": 0,
        "lesson": r'''
            ## Check every required point before passing

            A support answer must mention a receipt and a deadline. Finding one of those does not establish that both are there. You need to keep checking until a missing point is found or all the points are accounted for.

            ```python
            def has_labels(text, labels):
                for label in labels:
                    if label not in text:
                        return False
                return True
            print(has_labels("red blue", ["red", "blue"]))
            # True
            print(has_labels("red blue", ["red", "yellow"]))
            # False
            ```

            A missing label settles the result immediately: the text cannot contain every required label. A present label does not settle it, because another label may still be missing. That is why the successful return happens after the loop. Python reaches that line only if none of the checks has failed.

            Checking that required phrases occur somewhere in an answer is called a **contains grader**. When case should not matter, bring the answer and each phrase to the same case before checking membership. Remember that string membership checks a stretch of characters, not a word boundary. A phrase may occur inside a longer word.

            An empty requirements list has no missing point. The loop runs zero times and reaches its successful result.

            ```quiz
            You have found the first required phrase. Can you pass the answer now?
            - [x] No; another required phrase may be absent. :: Only checking every requirement establishes that all of them are present.
            - [ ] Yes; finding one proves the list is covered. :: One successful check says nothing about requirements that have not been checked.
            ```


            Try one more small check before moving to the task.

            ```predict
            requirements = []
            print(all(word in "hello" for word in requirements))
            ---
            With no requirements there is no failed requirement, so all returns True.
            ```

            **Watch out:** A return inside the loop ends the whole function, not only that pass through the loop. Check its indentation when later requirements are ignored.

            **In short:** One missing requirement proves failure; success needs all requirements checked.
        ''',
        "prompt": r'''
            An answer that misses a required point should not pass. Fix the supplied `contains_all` function, which currently accepts an answer too early.

            **Your job:** `contains_all(output, required)`

            **What goes in**
            - `output`: a string, the model's answer
            - `required`: a list of strings that must all appear, e.g. `["30 days", "refund"]`

            **What comes out**
            - `True` if every phrase appears in `output`, otherwise `False`

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
            "Look at when the starter stops checking phrases.",
            "A present phrase is a reason to continue; a missing phrase settles failure.",
            "Use the same case for the text and phrases, test each requirement, and leave the successful return until all requirements have been considered.",
        ],
    },
    {
        "id": "evals-s4",
        "title": "Pass rate",
        "difficulty": 0,
        "lesson": r'''
            ## Turn case results into one score

            You have marked a batch of answers, but a long list of True and False values is difficult to compare with yesterday's run. You want one number that says what fraction passed, while keeping the detailed results for investigation.

            ```python
            marked = [False, True, True, False, True]
            print(sum(marked))
            # 3
            print(round(sum(marked) / len(marked), 2))
            # 0.6
            ```

            In arithmetic, Python counts True as one and False as zero. Adding the results therefore counts the passed cases. Dividing by the number of cases produces a fraction between zero and one. Here three out of five is 0.6, which is also 60 percent.

            This fraction is the **pass rate**. A number summarising a run is called a **metric**. It helps you compare runs with different numbers of cases, although the dataset still matters: an easier dataset can inflate the score.

            Rounding gives the report a consistent precision. `round(number, 2)` returns a number, so it may display one decimal when no second decimal is needed. An empty batch needs a separate convention because there is no denominator to divide by.

            ```fill
            marks = [True, False, True]
            print(___(marks))
            ---
            - [x] sum :: Adding the booleans counts the two successful cases.
            - [ ] len :: The length counts all three cases, including the failure.
            ```


            Try one more small check before moving to the task.

            ```predict
            print(round(2 / 5, 2))
            ---
            Two passed cases out of five give a pass rate of 0.4.
            ```

            **Watch out:** Dividing by the length of an empty list raises ZeroDivisionError. Handle the empty-run rule before calculating a fraction.

            **In short:** Pass rate is passed cases divided by all cases, with an explicit empty-run rule.
        ''',
        "prompt": r'''
            A report needs one score for a batch of marked cases. Write a function that returns the fraction that passed.

            **Your job:** `pass_rate(results)`

            **What goes in**
            - `results`: a list of booleans, e.g. `[True, False, True, True]`

            **What comes out**
            - a float, the fraction of `True` values, rounded to 2 decimals

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
            "Which part of the calculation counts successful cases, and which counts all cases?",
            "Treat an empty run separately so there is no division by zero.",
            "Count the True values, divide by the total when there are cases, and round the resulting fraction to the required precision.",
        ],
    },
    {
        "id": "evals-s5",
        "title": "Close enough: numeric grader",
        "difficulty": 0,
        "lesson": r'''
            ## Accept a number within an agreed distance

            A model reports a measurement as text. You would accept a small rounding difference, but a sentence such as "about ten" is not a usable number. Your grading rule needs to distinguish conversion failure from an acceptable numerical difference.

            ```python
            target = 8.0
            reading = float(" 8.04 ")
            print(abs(reading - target) <= 0.05)
            # True
            print(abs(7.8 - target) <= 0.05)
            # False
            ```

            `float` converts the string to a number and accepts whitespace at its ends. Subtracting the target measures the difference. `abs` removes the sign, so being above or below the target is treated the same way. The comparison includes the boundary: a difference equal to the allowed distance passes.

            That allowed distance is called a **tolerance**. You choose it to match the application's needs, not to rescue a particular answer after seeing it. A tolerance suitable for a rounded estimate may be unsuitable for a financial total.

            Conversion can raise ValueError when the string does not represent a number. Catch that expected failure and mark the answer as wrong. Otherwise one unusable answer would interrupt the evaluation of all the remaining cases.

            ```quiz
            The allowed distance is 0.25. A number differs from its target by exactly 0.25. Does it pass?
            - [x] Yes, the boundary is included. :: The rule accepts differences less than or equal to the tolerance.
            - [ ] No, the difference must be strictly smaller. :: A strict comparison would reject a boundary that this rule explicitly accepts.
            ```


            Try one more small check before moving to the task.

            ```predict
            print(abs(9.75 - 10.0) <= 0.25)
            ---
            The unsigned distance is exactly the inclusive allowed boundary.
            ```

            **Watch out:** A text answer must be converted before numerical subtraction. An invalid conversion is a failed answer, not evidence that the whole dataset is broken.

            **In short:** Convert the answer, measure its absolute difference, and compare with the tolerance.
        ''',
        "prompt": r'''
            A numerical answer may differ by acceptable rounding. Grade it using the specified maximum difference.

            **Your job:** `numeric_match(output, expected, tolerance=0.01)`

            **What goes in**
            - `output`: a string, the model's answer, e.g. `" 3.1416 "`
            - `expected`: a number, e.g. `3.14`
            - `tolerance`: a number, the largest allowed difference (default `0.01`)

            **What comes out**
            - `True` if `output` is a number within `tolerance` of `expected`
              (difference `<=` tolerance), otherwise `False`

            **Rules**
            - Whitespace around the number is allowed.
            - If `output` is not a number (`float()` raises `ValueError`), the result is `False`; the function must not crash.

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
            "Look at the difference between comparing text and comparing quantities.",
            "Separate the conversion failure from the successful conversion path.",
            "Attempt the numeric conversion, mark invalid text as failed, then compare the unsigned difference with the inclusive tolerance.",
        ],
    },
    {
        "id": "evals-s6",
        "title": "Load a JSONL dataset",
        "difficulty": 0,
        "lesson": r'''
            ## Read a dataset one record at a time

            You want to keep adding questions to an eval file without rebuilding one enormous JSON list. A text file can hold one complete record on each line. Each record then becomes a case you can parse and inspect independently.

            ```python
            import json
            records = '{"name": "north"}\n\n{"name": "south"}'
            for row in records.splitlines():
                if row.strip():
                    print(json.loads(row)["name"])
            # north
            # south
            ```

            The string contains two JSON objects separated by line breaks, with a blank line between them. `splitlines` gives you the individual lines. The condition skips a line with no visible content. Each remaining line is passed to the JSON parser on its own.

            This format is called **JSON Lines**, often written **JSONL**. Each line is a whole JSON value; in this dataset each value is a dictionary. The line break separates records rather than becoming part of a surrounding JSON array.

            The order of the records is useful. It lets you compare a report with the source file and reproduce an earlier run. Blank lines do not produce cases. A line containing spaces is also blank for this purpose. Parsing errors in a non-blank line are different from blank lines and should not be silently treated as missing cases.

            ```predict
            rows = [" ", '{"n": 6}', "", '{"n": 9}']
            print(len([row for row in rows if row.strip()]))
            ---
            Only the two lines with JSON text survive. The empty string and the whitespace-only string are both skipped.
            ```


            Try one more small check before moving to the task.

            ```predict
            print("   ".strip() == "")
            ---
            A whitespace-only row becomes empty after stripping, so it can be skipped.
            ```

            **Watch out:** Parsing the entire text as one JSON document raises JSONDecodeError because a second object follows the first. Parse non-blank records separately.

            **In short:** JSONL stores one complete record per non-blank line, in a repeatable order.
        ''',
        "prompt": r'''
            Keep an evaluation dataset as one JSON case per line. Read those cases from the supplied text.

            **Your job:** `load_cases(text)`

            **What goes in**
            - `text`: a string holding JSONL: one JSON object per line

            **What comes out**
            - a list of dicts, one per non-blank line, in file order

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
            "Remember which part of a JSONL file is a complete JSON document.",
            "Whitespace-only lines are separators, not cases to parse.",
            "Walk through the lines in order, skip blank ones, parse each remaining record, and collect the parsed values.",
        ],
    },
    {
        "id": "evals-s7",
        "title": "Same score, different story",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Find what changed behind the overall score

            Two prompt versions pass the same number of questions. You might assume nothing changed, but one may have fixed a question while breaking another. Compare the individual cases before trusting the overall score.

            ```python
            old = {"oak": True, "pine": False}
            new = {"pine": True, "oak": False}
            print(sum(old.values()), sum(new.values()))
            # 1 1
            for name in old:
                print(name, old[name], new[name])
            # oak True False
            # pine False True
            ```

            The totals are equal, but the case named oak changed from passing to failing. Pine changed in the opposite direction. The dictionary lookup uses the name, so the order of entries in the new run does not matter.

            A newly failing case is a **regression**. A newly passing case is a **fix**. The current version you compare against is the **baseline**, and the proposed version is the **candidate**. You need both views: the total tells you how much changed; the case comparison tells you what changed.

            Keeping a stable case identifier makes this possible. Comparing the first result with the first result is unreliable when a dataset has been reordered. In a real review, open the regressed cases and read their answers. The boolean is a signal to investigate, not a complete explanation of the failure.

            ```quiz
            A run fixes one case and regresses another. What can happen to its pass rate?
            - [x] It can stay the same. :: A newly passed case and a newly failed case can cancel in the total.
            - [ ] It must improve. :: Counting only the fixed case ignores the regression.
            ```


            Try one more small check before moving to the task.

            ```predict
            before = {"x": True, "y": False}
            after = {"y": True, "x": True}
            print(before["x"] == after["x"])
            ---
            Lookup by identity finds the unchanged x result even though the dictionary order differs.
            ```

            **Watch out:** Equal pass rates do not establish equal behaviour. Match cases by identity before deciding what was fixed or regressed.

            **In short:** Compare case identities as well as totals so regressions cannot hide inside a score.
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
            passed before and fails now: a *regression*. `sum()` counts the `True` values, and
            both runs have 2, so the pass rates are identical. Only the per-case comparison
            shows that the behaviour changed.

            Follow each printed line in execution order. Changes to a variable affect later lines; they do not change output that was already printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Follow each named case from the baseline to the candidate.",
            "A fix and a regression move in opposite directions even when the totals balance.",
            "Work out the before-and-after pair for every case, identify both kinds of change, and then follow the printed totals.",
        ],
    },
    {
        "id": "evals-1",
        "title": "Regex grader",
        "difficulty": 1,
        "lesson": r'''
            ## Mark an answer by the shape of its text

            An answer may include an identifier anywhere in a sentence. You care whether the identifier has the required shape, not whether the whole sentence matches an answer key. A text pattern can express that rule.

            ```python
            import re
            text = "Ticket ref-82 is ready"
            found = re.search(r"REF-[0-9]{2}", text, re.IGNORECASE)
            print(bool(found))
            # True
            print(bool(re.search(r"REF-[0-9]{2}", "nothing here")))
            # False
            ```

            The search scans the string for a prefix followed by two digits. The flag permits a lowercase prefix to match the uppercase pattern. A successful search returns an object describing the match; an unsuccessful one returns None. Converting either result to a boolean gives the grader's required yes-or-no answer.

            This is a **regex grader**: the marking rule is a regular expression. You met regular expressions in the text-processing chapter. Here the new idea is choosing one as a grading rule and reporting its result consistently.

            A pattern match confirms a shape, not the truth of the answer. A correctly shaped but invented ticket number can still pass this check. Choose a different grader if factual correctness is the requirement. Also distinguish searching anywhere from matching only at the beginning, because introductory text is allowed here.

            ```fill
            import re
            print(bool(re.___(r"ID-[0-9]+", "Found ID-19")))
            ---
            - [x] search :: Searching inspects the whole string and finds the identifier after the introductory word.
            - [ ] match :: Matching at the start fails because the text begins with Found.
            ```


            Try one more small check before moving to the task.

            ```predict
            import re
            print(bool(re.search(r"[0-9]+", "no digits")))
            ---
            A search with no match returns None, which converts to False.
            ```

            **Watch out:** Returning a Match object is different from returning True, even though both are truthy. Convert the search result to the promised boolean.

            **In short:** A regex grader searches for a required text shape and reports a real boolean.
        ''',
        "prompt": r'''
            Some answers must include text with a specified shape. Grade whether the supplied pattern occurs in the answer.

            **Your job:** `regex_grade(output, pattern)`

            **What goes in**
            - `output`: a string, the model's answer
            - `pattern`: a string, a regular expression, e.g. `r"ORD-\d{4}"`

            **What comes out**
            - `True` if the pattern is found anywhere in `output`, otherwise `False`

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
            "Recall which regex function looks beyond the start of a string.",
            "Make the comparison case-insensitive, then consider the type of its result.",
            "Search the answer with the supplied pattern and case flag, and turn the presence or absence of a match into a boolean.",
        ],
    },
    {
        "id": "evals-2",
        "title": "The eval harness",
        "difficulty": 1,
        "lesson": r'''
            ## Keep running when one model call fails

            An evaluation has hundreds of questions. One model timeout should become one failed case, so you can still see what happened on the other questions. Keep the model call and the marking step distinct.

            ```python
            def fake_reply(text):
                if text == "slow":
                    raise TimeoutError("late")
                return text.upper()
            for question in ["hello", "slow", "bye"]:
                try:
                    print(fake_reply(question))
                except TimeoutError:
                    print("call failed")
            # HELLO
            # call failed
            # BYE
            ```

            The fake function makes the failure repeatable and uses no network. On the middle input it raises an exception. The except branch records the failure, and the loop proceeds to the final input. That is the behaviour you want when the real provider has a temporary problem.

            The code coordinating the calls, marking rules and result records is called the **eval harness**. Its job is orchestration: keeping the pieces in the right order, rather than knowing every grading rule itself. Receiving the model and grader as function arguments makes both pieces replaceable.

            Only an answer that was actually returned can be passed to the grader. A call failure has no answer to grade. Preserve the case identifier and order in the report so a failure can be traced back to the dataset. Keep the original returned answer too; a pass flag alone is often insufficient for debugging.

            ```quiz
            A model call raises before producing an answer. What should happen to that case?
            - [x] Record failure and continue without grading an answer. :: There is no returned output to give to the grader, but later cases can still run.
            - [ ] Skip the case entirely. :: Dropping failures changes the denominator and makes the run look better than it was.
            ```


            **Watch out:** Catch the model's failure at the model-call boundary. A bug in the grading rule should not be disguised as a provider timeout.

            **In short:** The harness runs every case and preserves a result even when the model call fails.
        ''',
        "prompt": r'''
            Run a repeatable batch of questions and preserve a result for each, including model-call failures.

            **Your job:** `run_eval(cases, model, grader)`

            **What goes in**
            - `cases`: a list of dicts with keys `"id"`, `"input"`, `"expected"`
            - `model`: a function taking the input string and returning the answer string
            - `grader`: a function `grader(output, expected)` returning `True`/`False`

            **What comes out**
            - a list of dicts, one per case, in the same order:
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
            "Separate the responsibilities of the model, the grader and the result record.",
            "A failed call needs a record, but cannot supply an answer to the grader.",
            "Visit each case in order, attempt its model call once, record failures immediately, and otherwise grade and store the returned answer.",
        ],
    },
    {
        "id": "evals-3",
        "title": "Pass rate per tag",
        "difficulty": 1,
        "lesson": r'''
            ## See which kind of question needs work

            Your overall score looks good, yet users asking questions in another language report failures. A single average can hide that problem. Group the cases by what they test and look at a score for each group.

            ```python
            groups = {"dates": [True, False, False], "names": [True, True]}
            for label, marks in groups.items():
                print(label, round(sum(marks) / len(marks), 2))
            # dates 0.33
            # names 1.0
            ```

            The dates group passes one of its three cases. The names group passes both. Each calculation uses its own group's size; dividing both counts by the whole dataset would answer a different question.

            A label attached to a case is called a **tag**. One case can have several tags, such as dates and French. It contributes to each corresponding group because those labels describe overlapping properties, not exclusive buckets. You can keep a total and a passed count for each tag while walking through the results.

            A missing tags field means there are no groups to update for that case. It still exists in the overall dataset, but this particular report leaves it out. An empty tags list has the same effect. Start a tag's counts only when you encounter it, so the report does not invent groups that the dataset never contained.

            ```quiz
            A case has tags dates and French. Which group counts it?
            - [x] Both groups. :: Each tag describes a property of the case, so the case belongs to both groups.
            - [ ] Only whichever tag comes first. :: Tag order does not make one property more real than another.
            ```


            **Watch out:** Use the group's own denominator. A small weak group can disappear inside a large strong overall score.

            **In short:** Tag scores reveal weaknesses that an overall pass rate can hide.
        ''',
        "prompt": r'''
            Find which kinds of questions are struggling. Return a pass rate for every tag represented in the results.

            **Your job:** `per_tag_pass_rate(results)`

            **What goes in**
            - `results`: a list of dicts like `{"id": "q1", "passed": True, "tags": ["math"]}`

            **What comes out**
            - a dict mapping each tag to its pass rate (passed / total for cases
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
            "For each tag, ask how many cases belong to it and how many passed.",
            "One case may contribute to several tag totals; untagged cases contribute to none.",
            "Accumulate total and successful cases for each encountered tag, then divide each tag's successes by its own total and round.",
        ],
    },
    {
        "id": "evals-4",
        "title": "Precision@k and recall@k",
        "difficulty": 1,
        "lesson": r'''
            ## Measure whether retrieval finds useful documents

            A RAG answer can fail because the model never received the useful document. Evaluate the retrieved list before changing the answering prompt. You need to ask both how clean that list is and how much of the known useful material it covers.

            ```python
            ranked = ["map", "guide", "ad"]
            useful = {"guide", "map", "hours", "tickets"}
            first_two = ranked[:2]
            hits = sum(doc in useful for doc in first_two)
            print(hits / 2)
            # 1.0
            print(hits / len(useful))
            # 0.5
            ```

            Both of the first two results are useful, so that selected list has no irrelevant result. But it contains only half of the four useful documents. Those are two different measurements of the same retrieval.

            **Precision at k** measures the useful hits among the requested top k results, divided by k. **Recall at k** measures those hits divided by the number of known useful documents. The phrase at k means you consider only the beginning of the ranked list. Later results cannot rescue a weak top section.

            The dataset supplies which document identifiers are useful, called the **relevant** identifiers. That judgement is independent of the retriever's score. For this exercise, precision uses the requested k even when fewer results were returned. Recall needs a stated rule when there are no relevant identifiers, because otherwise its denominator would be zero.

            ```match
            precision at k :: hits divided by requested result count
            recall at k :: hits divided by relevant document count
            top k :: the first k items in ranked order
            ---
            The same hits appear in both metrics; their denominators answer different questions.
            ```


            **Watch out:** Do not count useful documents below the cutoff. Validate a positive k before using it as a denominator.

            **In short:** Precision measures result quality; recall measures coverage of known relevant documents.
        ''',
        "prompt": r'''
            Assess the retrieved documents before judging the generated answer. Implement both requested retrieval metrics.

            **Your job:** two functions, `precision_at_k(retrieved, relevant, k)` and
            `recall_at_k(retrieved, relevant, k)`

            **What goes in**
            - `retrieved`: a list of document ids in ranked order, e.g. `["d3", "d1", "d7"]`
            - `relevant`: a list or set of the ids that are actually relevant, e.g. `{"d1", "d2"}`
            - `k`: an int, how many top results to look at


            **What comes out**
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
            "Identify the cutoff and the relevant identifiers before counting hits.",
            "Both metrics use the same selected hits but different denominators.",
            "Reject a non-positive cutoff, count relevant identifiers in the selected prefix, then apply each metric's denominator and the stated empty-relevance rule.",
        ],
    },
    {
        "id": "evals-5",
        "title": "LLM-as-judge",
        "difficulty": 1,
        "lesson": r'''
            ## Read a judge response without guessing

            A summary can be accurate without sharing the source's wording. A text comparison cannot judge that well. You can ask another model to assess it, but your code still needs an unambiguous way to read that model's decision.

            ```python
            reply = "The explanation covers the facts.\nRESULT: ACCEPT\n\n"
            nonblank = [row.strip() for row in reply.splitlines() if row.strip()]
            print(nonblank[-1])
            # RESULT: ACCEPT
            print(nonblank[-1] == "RESULT: ACCEPT")
            # True
            ```

            The explanation is free text, while the last non-blank line follows a fixed agreement. Splitting into lines and discarding blanks gives you a place to inspect. Comparing the whole line keeps an incidental word in the explanation from becoming the decision.

            Using another model as a marking rule is called **LLM-as-judge**. The judge receives the question, the answer and instructions describing the accepted verdicts. In our exercises the judge is a fake function, so its reply is repeatable and costs nothing.

            A parseable verdict is not proof that the judgement is right. Judges can make errors, favour particular wording, or be influenced by the answer being graded. Review representative cases and compare the judge with human assessments. Separately, if the judge breaks the agreed output format, report that problem instead of inventing a verdict. An empty reply has no final line to inspect.

            ```quiz
            The explanation says "I would not PASS this", with no agreed verdict line. Is searching for PASS enough?
            - [x] No; the required whole verdict line must be checked. :: A word can occur in a negative sentence without expressing the agreed decision.
            - [ ] Yes; the word PASS proves acceptance. :: The word alone loses both the sentence meaning and the output-format agreement.
            ```


            **Watch out:** Indexing the last item of an empty list raises IndexError. Check whether a non-blank line exists before trying to read it.

            **In short:** Give the judge a fixed verdict format and reject replies that cannot be parsed.
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
            Ask a judge function to assess an answer and read only its agreed verdict format.

            **Your job:** `judge_verdict(question, answer, judge)`

            **What goes in**
            - `question`: a string
            - `answer`: a string, the answer being graded
            - `judge`: a function taking one prompt string and returning the judge's reply string

            **What comes out**
            - `True` for a PASS verdict, `False` for a FAIL verdict

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
            "Distinguish the explanatory text from the one line that carries the verdict.",
            "Use the last non-blank line and only accept the two agreed verdicts.",
            "Send one prompt containing the question, answer and accepted formats, normalise the final non-blank line, and return or raise according to that whole line.",
        ],
    },
    {
        "id": "evals-6",
        "title": "Mean reciprocal rank",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A relevant document near the start of the retrieved list is more useful than one far down. Summarise the first relevant position across queries.

            **Your job:** `mean_reciprocal_rank(queries)`

            **What goes in**
            - `queries`: a list of dicts, each `{"retrieved": [ids in ranked order], "relevant": [ids]}`

            **What comes out**
            - a float, the average of the reciprocal ranks, rounded to 3 decimals

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
            "Recall how a ranked list differs from an unordered set of relevant identifiers.",
            "Only the earliest relevant result earns a reciprocal-rank score; a miss contributes zero.",
            "Handle no queries separately, find the first relevant position in each ranked list, accumulate its reciprocal, and average over all queries before rounding.",
        ],
    },
    {
        "id": "evals-7",
        "title": "Compare two runs",
        "difficulty": 2,
        "prompt": r'''
            A new version can fix some questions and break others. Compare runs by case identifier and report both changes.

            **Your job:** `compare_runs(baseline, candidate)`

            **What goes in**
            - `baseline`, `candidate`: lists of results like `{"id": "q1", "passed": True}`

            **What comes out**
            - a dict with three keys:
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
            "Match cases by their identifiers rather than their positions.",
            "Only shared identifiers can be fixed or regressed, but each run has its own pass-rate denominator.",
            "Build an identity lookup for each run, classify shared cases by their before-and-after result, sort the two change lists, and subtract the separately calculated rates.",
        ],
    },
    {
        "id": "evals-8",
        "title": "Release gate",
        "difficulty": 3,
        "lesson": r'''
            ## Make the release decision from explicit rules

            A candidate improves the average but drops a critical case. Another candidate has no regressions but too many failures. Before shipping, turn your acceptance rules into a repeatable decision and collect the reasons that block it.

            ```python
            score = 0.7
            new_failures = 2
            blocks = []
            if score < 0.75:
                blocks.append("score below target")
            if new_failures > 1:
                blocks.append("too many newly failing cases")
            print(bool(blocks), len(blocks))
            # True 2
            ```

            This small example keeps checking after the first failure. A reviewer receives both reasons and can address them together. An empty reasons list would mean that every rule was satisfied.

            A decision function of this kind is a **release gate**. Putting it together means combining the pass-rate calculation, case-identity comparison and completeness check. Plan the three checks independently so a missing case is not mistaken for a successful case or silently removed from the denominator.

            Use the specified order when reporting reasons. Stable ordering makes reports easier to compare and is part of this task's interface. Sorting the identifiers inside a reason also gives a predictable message. Boundary conditions matter: a score exactly at the minimum is acceptable, and a regression count exactly at its allowed maximum is acceptable. An empty candidate still needs its agreed rate and missing-case checks.

            ```quiz
            The minimum score is 0.75 and the candidate scores exactly 0.75. Does this rule block it?
            - [x] No; it meets the minimum. :: A minimum includes the boundary itself. Other rules still need to be checked.
            - [ ] Yes; it must exceed the minimum. :: That would impose a stricter rule than the stated minimum.
            ```


            **Watch out:** Returning after the first failure hides other reasons. Collect all required reasons before deciding whether the change passes.

            **In short:** A release gate checks every agreed rule and returns every blocking reason.
        ''',
        "prompt": r'''
            A release needs enough successful cases without hiding missing cases or regressions. Return a decision with all blocking reasons.

            **Your job:** `release_gate(baseline, candidate, min_pass_rate=0.8, max_regressions=0)`

            **What goes in**
            - `baseline`, `candidate`: lists of results like `{"id": "q1", "passed": True}`
            - `min_pass_rate`: a float, the lowest acceptable candidate pass rate
            - `max_regressions`: an int, the most regressions allowed

            **What comes out**
            - a tuple `(ok, reasons)`: `reasons` is a list of strings, `ok` is
              `True` exactly when `reasons` is empty

            **Rules**: check in this order and add one reason per failed rule:
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
            "List the three independent ways this candidate can be unacceptable.",
            "Compute completeness, candidate score and shared-case regressions separately.",
            "Collect failed-rule messages in the required order with sorted identifiers, then decide success from whether any reasons were collected.",
        ],
    },
    {
        "id": "evals-9",
        "title": "A full eval suite",
        "difficulty": 3,
        "lesson": r'''
            ## Combine a dataset, graders and a useful report

            Your eval file now mixes short factual answers, required phrases and numeric answers. One grading rule will not suit every case. You need a runner that uses each case's chosen rule while producing a consistent report.

            ```python
            checks = {"short": lambda text: len(text) < 6,
                      "has_digit": lambda text: any(ch.isdigit() for ch in text)}
            for kind, answer in [("short", "hello"), ("has_digit", "abc")]:
                print(kind, checks[kind](answer))
            # short True
            # has_digit False
            ```

            The dictionary holds functions as values. The selected key determines which function runs; the report format does not change. This is the same lookup idea you used for tools, now applied to grading rules.

            Putting it together means planning the run in stages. Read the JSONL cases first. Establish which grader a case requests. Attempt the model call, and record that case's success or failure. Then update overall totals, failure identifiers and the tag groups. Keep the dataset order for the failure list so a reader can find the corresponding rows.

            There are two distinct failure categories. An exception from the model is a failed case and the run continues. An unknown grading-rule name is an invalid dataset configuration and must raise the specified error. Do not put both categories under one broad catch. Otherwise a typo in the eval file could look like a genuine weakness in the model.

            ```predict
            rules = {"ends": lambda s: s.endswith("!"), "upper": lambda s: s.isupper()}
            print(rules["ends"]("Ready!"))
            print(rules["upper"]("Ready!"))
            ---
            The same answer passes the punctuation rule but fails the uppercase rule. Rule selection determines what is being tested.
            ```


            **Watch out:** A reporting loop can accidentally count a failed call twice or omit it entirely. Every parsed case must contribute exactly once to the overall total.

            **In short:** Choose the grader per case, isolate model failures, and build one consistent report.
        ''',
        "prompt": r'''
            A realistic dataset chooses different grading rules for different questions. Run it and return one overall report.

            **Your job:** `run_suite(jsonl_text, model)`

            **What goes in**
            - `jsonl_text`: a string, one JSON case per line (skip blank lines). Each case has
              `"id"`, `"input"`, `"grader"`, `"expected"` and optionally `"tags"` (list of strings)
            - `model`: a function taking the input string and returning an answer string

            **What comes out**
            - a dict:
              `{"total": int, "passed": int, "pass_rate": float, "by_tag": dict, "failed_ids": list}`

            **Graders** (by the case's `"grader"` value):
            - `"exact"`: the complete strings must match after ignoring outer whitespace and letter case
            - `"contains"`: `expected` is a list; every item appears in the output, ignoring case
            - `"regex"`: `expected` is a pattern; the pattern occurs anywhere in the answer, ignoring case
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
            "Think about case reading, rule selection, model execution and reporting as separate stages.",
            "An unknown rule is a configuration error; a model exception is an ordinary failed case.",
            "Parse non-blank records, resolve each grader before the model failure handler, run and grade each case once, and aggregate overall and per-tag results.",
        ],
    },
]
