TOPIC = {
    "id": "conditionals",
    "title": "Conditionals",
    "track": "foundations",
    "order": 3,
    "requires": ["data-types"],
    "summary": """
        Making decisions: if/elif/else, boolean logic, comparison chaining,
        truthiness, early returns, conditional expressions and the match statement.
    """,
    "concepts": ["if/elif/else", "boolean operators", "comparison chaining", "truthiness",
                 "early return", "ternary expression", "match statement"],
}

LESSON = r'''
## Chapter notes: Conditionals

**if / elif / else** - checked top to bottom; only the **first** true branch runs.
Lines end with `:`, blocks are indented.

```python
tokens = 700
if tokens > 1000:
    print("too long")
elif tokens > 500:
    print("long")
else:
    print("short")
```

**Comparisons**: `==` `!=` `<` `<=` `>` `>=` give a `bool`. `=` stores, `==` compares.
**Chained**: `0 <= t <= 2` means `0 <= t and t <= 2`.
**Combine**: `and` (both), `or` (at least one), `not` (flip).
**Membership**: `reason in ("tool_calls", "function_call")`.

**Early return**: `return` leaves the function at once, so a chain of
`if ...: return ...` works like `elif`, and the last `return` is the "otherwise".

**Truthiness in if**: `if text:` is false for `""`, `0`, `None`. Use `is None` /
`is not None` when `0` or `""` are real values.
**`or` fallback**: `a or b` gives `a` if truthy, else `b`; `(name or "").strip()`
turns `None` into `""`.

**Conditional expression**: `"pass" if score >= 0.5 else "fail"`.

**match** (3.10+): compares one value against patterns, first match wins.

```python
role = "user"
match role:
    case "system":
        print("instructions")
    case "user" | "assistant":
        print("chat")
    case _:
        print("unknown")
```

Tuple patterns: `case ("user", str(text)) if text:` - shape and length must match,
`str(text)` matches only strings and captures the value, `if ...` is a *guard*.

**Gotchas**
- `if reason == "a" or "b":` is always true -> `reason == "a" or reason == "b"` / `in`.
- Check the most specific / biggest threshold first.
- A missing final `return` makes some inputs return `None`.
'''

EXERCISES = [
    {
        "id": "conditionals-s2",
        "title": "Fill in the condition",
        "difficulty": 0,
        "lesson": r'''
            So far every line ran. Now you'll make code **decide**. An `if` is like a **bouncer at a
            door**: it checks a condition, and only if the answer is `True` does it let the indented
            block run.

            ```python
            tokens = 5000
            if tokens > 4000:
                print("too long")
            print("checked")
            ```

            The shape: `if`, a condition, a colon `:`, then the block indented by 4 spaces. The
            unindented `print("checked")` is outside the `if`, so it always runs.

            Inside a function, a `return` in the block hands back a value and leaves straight away.
            If the condition is `False`, Python skips the block and carries on below:

            ```python
            def check(tokens):
                if tokens > 4000:
                    return "too long"
                return "ok"

            print(check(100))
            ```

            Vocabulary: the thing after `if` is the *condition*; the indented lines are the
            *if block* (or *branch*).

            Watch out: "more than" is `>`; `>=` also includes the limit itself.
        ''',
        "prompt": r'''
            A request is refused when the prompt is too long. Finish the check.

            **Write:** replace `___` in `check_length(tokens)`

            - `tokens`: the prompt length, an `int`, e.g. `5000`
            - **Returns:** the string `"too long"` or the string `"ok"`

            **Rules**
            - Return `"too long"` when `tokens` is **more than** `4000`.
            - Otherwise return `"ok"`. Exactly `4000` is `"ok"`.

            **Examples**
            ```python
            check_length(5000)   # returns "too long"
            check_length(100)    # returns "ok"
            check_length(4000)   # returns "ok"
            ```
        ''',
        "starter": r'''
            def check_length(tokens):
                if ___:
                    return "too long"
                return "ok"
        ''',
        "tests": r'''
            from solution import check_length

            def test_5000_tokens_is_too_long():
                got = check_length(5000)
                assert got == "too long", f"check_length(5000) returned {got!r}"

            def test_100_tokens_is_ok():
                got = check_length(100)
                assert got == "ok", f"check_length(100) returned {got!r}"

            def test_exactly_4000_tokens_is_ok():
                got = check_length(4000)
                assert got == "ok", f"check_length(4000) returned {got!r}"
        ''',
        "solution": r'''
            def check_length(tokens):
                if tokens > 4000:
                    return "too long"
                return "ok"
        ''',
        "hints": [
            "The blank is a comparison that is True only for values bigger than the limit.",
            "Compare tokens to 4000. 'More than' does not include 4000 itself.",
            "Replace ___ with tokens, the greater-than sign, and 4000 (not >=).",
        ],
    },
    {
        "id": "conditionals-s3",
        "title": "Fix: compare, don't assign",
        "difficulty": 0,
        "lesson": r'''
            One `=` and two `==` look alike but mean completely different things:
            - `role = "system"` **stores**: put "system" in the box called role.
            - `role == "system"` **asks**: is what's in role equal to "system"? The answer is `True`
              or `False`.

            ```python
            role = "user"
            print(role == "system")
            print(role == "user")
            ```

            Inside an `if` you always want to ask, never store. Python protects you: `if role = "system":`
            is a `SyntaxError` and nothing runs.

            Comparison of text is exact, letter by letter: `"System" == "system"` is `False`,
            because capital S and lowercase s are different characters.

            Vocabulary: `=` is the *assignment operator*; `==` is the *equality operator*. `!=` means
            "not equal".
        ''',
        "prompt": r'''
            Only messages with the `"system"` role hold the model's instructions. This check
            has one bug: Check fails with a `SyntaxError`. Read the message, find the line, fix it.

            **Write:** fix `is_system(role)`

            - `role`: a message role, a string, e.g. `"user"`
            - **Returns:** the boolean `True` or `False` (not the text `"True"`)

            **Rules**
            - Return `True` only when `role` is exactly `"system"` (lowercase).
            - Any other role returns `False`, including `"System"` with a capital S.

            **Examples**
            ```python
            is_system("system")      # returns True
            is_system("assistant")   # returns False
            is_system("System")      # returns False
            ```
        ''',
        "starter": r'''
            def is_system(role):
                if role = "system":
                    return True
                return False
        ''',
        "tests": r'''
            from solution import is_system

            def test_system_role_returns_true():
                assert is_system("system") is True, f"is_system('system') returned {is_system('system')!r}"

            def test_other_roles_and_capital_system_return_false():
                for r in ("user", "assistant", "System"):
                    got = is_system(r)
                    assert got is False, f"is_system({r!r}) returned {got!r}"
        ''',
        "solution": r'''
            def is_system(role):
                if role == "system":
                    return True
                return False
        ''',
        "hints": [
            "The error points at the if line. A single = means 'store', not 'compare'.",
            "To compare two values for equality you need a different operator.",
            "Change the single = on the if line to a double ==.",
        ],
    },
    {
        "id": "conditionals-s4",
        "title": "Pass or fail",
        "difficulty": 0,
        "lesson": r'''
            An `if` alone says "do this or do nothing". Often you want **one thing or the other** -
            like a fork in the road. Add `else:` for the other way:

            ```python
            score = 0.3
            if score >= 0.5:
                print("pass")
            else:
                print("fail")
            ```

            Exactly one of the two blocks runs. `else` has no condition: it catches everything the
            `if` didn't.

            Inside a function there's a shortcut: since `return` leaves the function, a `return`
            after the `if` block acts like an `else`:

            ```python
            def verdict(score):
                if score >= 0.5:
                    return "pass"
                return "fail"

            print(verdict(0.5), verdict(0.2))
            ```

            Vocabulary: "at least" means `>=` (greater than *or equal*); the value where behaviour
            switches is the *boundary*. Always test the boundary itself.
        ''',
        "prompt": r'''
            An eval gives each answer a score from 0 to 1. Turn the score into a verdict.

            **Write:** `grade(score)`

            - `score`: a number from `0` to `1`, e.g. `0.9`
            - **Returns:** the string `"pass"` or the string `"fail"`

            **Rules**
            - Return `"pass"` when `score` is **at least** `0.5` (so `0.5` itself passes).
            - Otherwise return `"fail"` (this includes `0.49` and `0`).

            **Examples**
            ```python
            grade(0.9)    # returns "pass"
            grade(0.5)    # returns "pass"
            grade(0.49)   # returns "fail"
            grade(0)      # returns "fail"
            ```
        ''',
        "starter": r'''
            def grade(score):
                ...
        ''',
        "tests": r'''
            from solution import grade

            def test_score_0_9_passes():
                assert grade(0.9) == "pass", f"grade(0.9) returned {grade(0.9)!r}"

            def test_score_exactly_0_5_passes():
                assert grade(0.5) == "pass", f"grade(0.5) returned {grade(0.5)!r}"

            def test_scores_below_0_5_fail():
                for s in (0.2, 0.49, 0):
                    assert grade(s) == "fail", f"grade({s}) returned {grade(s)!r}"
        ''',
        "solution": r'''
            def grade(score):
                if score >= 0.5:
                    return "pass"
                return "fail"
        ''',
        "hints": [
            "Use an if with a comparison. 'At least' includes the boundary value.",
            "If score is greater than or equal to 0.5 return one word, otherwise return the other.",
            "1) An if that compares score with 0.5 using >=, returning pass inside it. 2) After the if block (not indented under it), return fail.",
        ],
    },
    {
        "id": "conditionals-s5",
        "title": "Small, medium, large",
        "difficulty": 0,
        "lesson": r'''
            Some decisions have more than two outcomes. Picture a **sorting machine** with several
            slots: the item drops into the **first** slot it fits. Python writes the extra slots
            with `elif` ("else if"):

            ```python
            tokens = 500
            if tokens < 100:
                print("small")
            elif tokens < 1000:
                print("medium")
            else:
                print("large")
            ```

            Python checks from the top. The first true condition wins, and every branch after it is
            skipped - even if it would also be true. That's why the `elif` only needs `< 1000`: if we
            got there, we already know `tokens` is not below 100.

            Vocabulary: an `if` / `elif` / `else` sequence is a *conditional chain*. You can have as
            many `elif`s as you need, and `else` is optional.

            Watch out: order matters. Put `< 1000` first and 50 would be called "medium".
        ''',
        "prompt": r'''
            Label a document by its size so you can decide how to process it.

            **Write:** `size_label(tokens)`

            - `tokens`: the document length, an `int`, e.g. `500`
            - **Returns:** one of the strings `"small"`, `"medium"`, `"large"`

            **Rules**
            - Fewer than `100` tokens: return `"small"`.
            - From `100` up to `999` tokens: return `"medium"` (`100` is medium).
            - `1000` tokens or more: return `"large"` (`1000` is large).

            **Examples**
            ```python
            size_label(50)      # returns "small"
            size_label(100)     # returns "medium"
            size_label(999)     # returns "medium"
            size_label(1000)    # returns "large"
            ```
        ''',
        "starter": r'''
            def size_label(tokens):
                ...
        ''',
        "tests": r'''
            from solution import size_label

            def test_under_100_is_small():
                assert size_label(50) == "small", f"size_label(50) returned {size_label(50)!r}"

            def test_100_to_999_is_medium():
                for n in (100, 500, 999):
                    assert size_label(n) == "medium", f"size_label({n}) returned {size_label(n)!r}"

            def test_1000_or_more_is_large():
                for n in (1000, 50000):
                    assert size_label(n) == "large", f"size_label({n}) returned {size_label(n)!r}"
        ''',
        "solution": r'''
            def size_label(tokens):
                if tokens < 100:
                    return "small"
                elif tokens < 1000:
                    return "medium"
                else:
                    return "large"
        ''',
        "hints": [
            "Three outcomes means if, elif, else (or two ifs with early returns and a final return).",
            "Check the smallest range first. Because the first match wins, the second check only needs '< 1000'.",
            "1) First condition: under 100 gives small. 2) An elif: under 1000 gives medium. 3) An else gives large. Each branch returns its word, indented under its line.",
        ],
    },
    {
        "id": "conditionals-s6",
        "title": "Both must be true",
        "difficulty": 0,
        "lesson": r'''
            Real decisions often depend on **two** things. Think of a door with two locks: it
            opens only when **both** are unlocked. That's `and`. A door with two keys - either
            one opens it - is `or`.

            ```python
            status = 429
            attempts = 1
            print(status == 429 and attempts < 3)
            print(status == 500 or attempts < 3)
            print(not attempts < 3)
            ```

            - `a and b` is `True` only if both are `True`.
            - `a or b` is `True` if at least one is `True`.
            - `not a` flips `True` to `False` and back.

            The result is a `bool`, so you can put it in an `if` or return it directly.

            Vocabulary: `and`, `or`, `not` are *boolean operators* (or *logical operators*).

            Watch out: each side needs a full comparison. `status == 429 and < 3` is a syntax
            error; write `attempts < 3` in full.
        ''',
        "prompt": r'''
            When an API answers with status `429` (rate limited) you may retry - but only a
            few times.

            **Write:** replace `___` in `should_retry(status, attempts)`

            - `status`: the HTTP status code, an int, e.g. `429`
            - `attempts`: how many attempts were already made, an int, e.g. `1`
            - **Returns:** a `bool`: `True` only if `status` is `429` **and** `attempts` is less than `3`

            **Rules**
            - Any other status gives `False`.
            - `3` or more attempts gives `False`, even for `429`.

            **Examples**
            ```python
            should_retry(429, 1)   # returns True
            should_retry(429, 3)   # returns False
            should_retry(500, 0)   # returns False
            ```
        ''',
        "starter": r'''
            def should_retry(status, attempts):
                return status == 429 ___ attempts < 3
        ''',
        "tests": r'''
            from solution import should_retry

            def test_rate_limited_with_few_attempts_retries():
                for a in (0, 1, 2):
                    got = should_retry(429, a)
                    assert got is True, f"should_retry(429, {a}) returned {got!r}"

            def test_three_or_more_attempts_stops():
                for a in (3, 10):
                    got = should_retry(429, a)
                    assert got is False, f"should_retry(429, {a}) returned {got!r}"

            def test_other_status_does_not_retry():
                for s in (500, 200):
                    got = should_retry(s, 0)
                    assert got is False, f"should_retry({s}, 0) returned {got!r}"
        ''',
        "solution": r'''
            def should_retry(status, attempts):
                return status == 429 and attempts < 3
        ''',
        "hints": [
            "The blank joins two conditions. Which boolean operator means 'both must be true'?",
            "The result should be True only when the status check and the attempts check are both True.",
            "Replace ___ with the word and.",
        ],
    },
    {
        "id": "conditionals-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            Time to read a complete decision. Two things to remember:

            1. In an `if` / `elif` / `else` chain, **only one** block runs: the first whose condition
               is true.
            2. A line back at the left edge is **after** the chain. It always runs, whatever the
               chain decided.

            ```python
            tokens = 50
            if tokens > 100:
                print("big")
            else:
                print("small")
            print(tokens < 100 and tokens > 10)
            ```

            That prints `small`, then `True`. Remember `and` from the last step: both sides must be
            true.

            Vocabulary: following code line by line in your head is called *tracing*. Good engineers
            trace code before running it.
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            tokens = 900
            if tokens > 1000:
                print("too long")
            elif tokens > 500:
                print("long")
            else:
                print("short")
            print(tokens >= 900 and tokens < 1000)
        ''',
        "solution": r'''
            long
            True
        ''',
        "explanation": r'''
            900 is not greater than 1000, so the first block is skipped. It is greater
            than 500, so `long` prints and the `else` is skipped. The last line is outside
            the if (not indented), so it always runs: both sides of `and` are true.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Check each condition from the top with tokens = 900. Only one block of an if/elif/else chain runs.",
            "The first condition is false, the second is true. The last print is not part of the if chain.",
            "Line 1: the text of the first block whose condition is true. Line 2: is 900 >= 900 and 900 < 1000? Print True or False.",
        ],
    },
    {
        "id": "conditionals-2",
        "hints": ['A comparison already produces True or False, so you can return it directly.', "Write one chained comparison that says 't is between 0 and 2, both ends included'.", 'Return 0, then <=, then t, then <=, then 2 in a single expression. No if needed.'],
        "title": "Temperature in range",
        "difficulty": 1,
        "lesson": r'''
            Model settings often have to sit inside a range, like a **thermostat** that only accepts
            temperatures between two marks. Python lets you write a range check just like maths:

            ```python
            t = 1.5
            print(0 <= t <= 2)
            print(0 <= 3 <= 2)
            ```

            `0 <= t <= 2` means `0 <= t and t <= 2`. It's shorter and reads like a sentence.

            And remember: a comparison **is already** a `True`/`False` value. You don't need an `if`
            to turn it into one:

            ```python
            def is_small(n):
                return 0 <= n < 100

            print(is_small(5), is_small(500))
            ```

            Vocabulary: this is a *chained comparison*. "Both ends included" (*inclusive*) means
            `<=`; "excluding the end" means `<`.

            Watch out: `if ...: return True else: return False` works, but returning the
            comparison itself is cleaner.
        ''',
        "prompt": r'''
            Model APIs only accept a `temperature` between 0 and 2. Validate it before sending.

            **Write:** `valid_temperature(t)`

            - `t`: the temperature, an `int` or `float`, e.g. `0.7`
            - **Returns:** the boolean `True` or `False`

            **Rules**
            - Return `True` when `t` is between `0` and `2`, **both ends included**.
            - Otherwise return `False`.
            - Use a **chained comparison** (two comparison operators in one expression, like
              `low <= value <= high`). A check looks for it.

            **Examples**
            ```python
            valid_temperature(0)      # returns True
            valid_temperature(0.7)    # returns True
            valid_temperature(2.0)    # returns True
            valid_temperature(2.01)   # returns False
            valid_temperature(-0.1)   # returns False
            ```
        ''',
        "starter": r'''
            def valid_temperature(t):
                ...
        ''',
        "tests": r'''
            from solution import valid_temperature

            def test_0_and_2_are_valid():
                assert valid_temperature(0) is True, f"0 -> {valid_temperature(0)!r}"
                assert valid_temperature(2.0) is True, f"2.0 -> {valid_temperature(2.0)!r}"

            def test_value_inside_range_is_valid():
                assert valid_temperature(0.7) is True

            def test_values_outside_range_are_invalid():
                for t in (2.01, -0.1, 100):
                    assert valid_temperature(t) is False, f"{t} -> {valid_temperature(t)!r}"

            def test_uses_chained_comparison():
                import ast
                ok = any(isinstance(n, ast.Compare) and len(n.ops) == 2
                         for n in ast.walk(ast.parse(source())))
                assert ok, "use a chained comparison like a <= x <= b"
        ''',
        "solution": r'''
            def valid_temperature(t):
                return 0 <= t <= 2
        ''',
    },
    {
        "id": "conditionals-1",
        "hints": ['An if / elif / else chain that compares reason with each string using ==.', 'Check each known reason in turn and return its label. Two different reasons share one label, and everything else (including None) ends in the final else.', '1) reason == stop -> complete. 2) elif length -> truncated. 3) elif reason is one of the two tool reasons (use in with a tuple, or or) -> needs tool. 4) elif content_filter -> blocked. 5) else -> unknown.'],
        "title": "Classify finish_reason",
        "difficulty": 1,
        "lesson": r'''
            When one answer covers **several** values, don't write a long `or` chain. Ask "is it one
            of these?" with `in` and a tuple:

            ```python
            reason = "function_call"
            print(reason in ("tool_calls", "function_call"))
            print("stop" in ("tool_calls", "function_call"))
            ```

            That fits neatly in a long `elif` chain, like a **translation table**: each branch
            handles one known value, and `else` catches anything unexpected - including `None` or
            text with the wrong capitals.

            ```python
            def label(role):
                if role == "user":
                    return "person"
                elif role in ("assistant", "model"):
                    return "AI"
                else:
                    return "unknown"

            print(label("model"), label(None))
            ```

            Vocabulary: `in` is the *membership operator*.

            Watch out: `if reason == "a" or "b":` is **always** true, because `"b"` on its own is
            truthy. Write `reason in ("a", "b")`.
        ''',
        "prompt": r'''
            A chat completion ends with a `finish_reason` string. Translate it into a short
            label for your logs.

            **Write:** `explain_finish(reason)`

            - `reason`: the finish reason, usually a string like `"stop"`, but it can be `None`
            - **Returns:** one of the strings `"complete"`, `"truncated"`, `"needs tool"`, `"blocked"`, `"unknown"`

            **Rules**

            | `reason` | return |
            | --- | --- |
            | `"stop"` | `"complete"` |
            | `"length"` | `"truncated"` |
            | `"tool_calls"` or `"function_call"` | `"needs tool"` |
            | `"content_filter"` | `"blocked"` |
            | anything else | `"unknown"` |

            - Matching is exact: `"STOP"` (capitals) is `"unknown"`.
            - `None` and the empty string `""` are `"unknown"`.

            **Examples**
            ```python
            explain_finish("stop")           # returns "complete"
            explain_finish("function_call")  # returns "needs tool"
            explain_finish("STOP")           # returns "unknown"
            explain_finish(None)             # returns "unknown"
            ```
        ''',
        "starter": r'''
            def explain_finish(reason):
                ...
        ''',
        "tests": r'''
            from solution import explain_finish

            def test_stop_returns_complete():
                assert explain_finish("stop") == "complete", f"got {explain_finish('stop')!r}"

            def test_length_returns_truncated():
                assert explain_finish("length") == "truncated"

            def test_tool_calls_and_function_call_return_needs_tool():
                for r in ("tool_calls", "function_call"):
                    got = explain_finish(r)
                    assert got == "needs tool", f"{r!r} -> {got!r}"

            def test_content_filter_returns_blocked():
                assert explain_finish("content_filter") == "blocked"

            def test_none_empty_capitals_and_other_reasons_return_unknown():
                for r in (None, "", "STOP", "eos"):
                    got = explain_finish(r)
                    assert got == "unknown", f"{r!r} -> {got!r}"
        ''',
        "solution": r'''
            def explain_finish(reason):
                if reason == "stop":
                    return "complete"
                elif reason == "length":
                    return "truncated"
                elif reason in ("tool_calls", "function_call"):
                    return "needs tool"
                elif reason == "content_filter":
                    return "blocked"
                else:
                    return "unknown"
        ''',
    },
    {
        "id": "conditionals-7",
        "title": "A title or Untitled",
        "difficulty": 1,
        "lesson": r'''
            Remember truthiness? An `if` doesn't need a comparison: `if text:` means "if text
            has something in it". Empty text, `0` and `None` count as "nothing".

            ```python
            name = ""
            if name:
                print("hi", name)
            else:
                print("no name")
            ```

            Missing data is often `None`, and `None` has no `.strip()`. `or` gives you a
            **spare tyre**: `a or b` gives `a` if it's truthy, otherwise `b`.

            ```python
            title = None
            print((title or "").strip() == "")
            print("draft" or "Untitled")
            ```

            So `(title or "").strip()` turns `None` into `""`, then trims spaces - safe for any
            input. After that one line, a plain `if title:` tells you whether anything is left.

            Vocabulary: a value used when the real one is missing is a *fallback* (or
            *default*).

            Watch out: if `0` is a real value, don't use truthiness - use `is None` /
            `is not None`.
        ''',
        "prompt": r'''
            Documents in your RAG index should always show a title. Some arrive with no title
            (`None`), an empty one, or one full of spaces.

            **Write:** `clean_title(title)`

            - `title`: a string like `"  Intro to RAG "`, or `None`
            - **Returns:** a string: the title with spaces/newlines removed from both ends,
              or `"Untitled"` if nothing is left

            **Rules**
            - `None`, `""` and whitespace-only text (like `"   "` or `"\n"`) all give `"Untitled"`.
            - Spaces in the middle stay.

            **Examples**
            ```python
            clean_title("  Intro to RAG ")   # returns "Intro to RAG"
            clean_title("Evals")             # returns "Evals"
            clean_title("   ")               # returns "Untitled"
            clean_title(None)                # returns "Untitled"
            ```
        ''',
        "starter": r'''
            def clean_title(title):
                ...
        ''',
        "tests": r'''
            from solution import clean_title

            def test_strips_spaces_around_title():
                got = clean_title("  Intro to RAG ")
                assert got == "Intro to RAG", f"clean_title('  Intro to RAG ') returned {got!r}"

            def test_clean_title_is_unchanged():
                got = clean_title("Evals")
                assert got == "Evals", f"clean_title('Evals') returned {got!r}"

            def test_empty_or_whitespace_gives_untitled():
                for t in ("", "   ", "\n"):
                    got = clean_title(t)
                    assert got == "Untitled", f"clean_title({t!r}) returned {got!r}"

            def test_none_gives_untitled():
                got = clean_title(None)
                assert got == "Untitled", f"clean_title(None) returned {got!r}"
        ''',
        "solution": r'''
            def clean_title(title):
                title = (title or "").strip()
                if title:
                    return title
                return "Untitled"
        ''',
        "hints": [
            "None can't be stripped, so first turn it into empty text. Empty text is falsy.",
            "Replace None with an empty string using or, strip the result, then return it if anything is left - otherwise return the fallback.",
            "1) title = (title or \"\").strip(). 2) if title: return title. 3) After the if, return \"Untitled\".",
        ],
    },
    {
        "id": "conditionals-8",
        "title": "1 token, 2 tokens",
        "difficulty": 1,
        "lesson": r'''
            Sometimes a whole `if` / `else` block is too much for a tiny choice, like picking
            between two words. Python has a **one-line if**: it reads like English,
            "this *if* condition, *else* that".

            ```python
            score = 0.8
            verdict = "pass" if score >= 0.5 else "fail"
            print(verdict)
            ```

            It's an *expression*: it produces a value, so you can store it, return it, or glue
            it into text. Use parentheses when you glue:

            ```python
            n = 3
            print(str(n) + (" item" if n == 1 else " items"))
            ```

            Vocabulary: this is a *conditional expression* (other languages call it a
            *ternary operator*).

            Watch out: the order is value-if-true, then the condition, then value-if-false.
            Keep it for short choices; use a normal `if` for anything longer.
        ''',
        "prompt": r'''
            A usage line should read naturally: `1 token`, but `2 tokens` and `0 tokens`.

            **Write:** `token_label(n)`

            - `n`: a token count, an int, e.g. `5`
            - **Returns:** a string: the number, a space, then `token` if `n` is exactly `1`,
              otherwise `tokens`

            **Rules**
            - Use a **conditional expression** (`x if condition else y`) to pick the word (a check looks for it).
            - `0` uses the plural: `"0 tokens"`.

            **Examples**
            ```python
            token_label(1)     # returns "1 token"
            token_label(5)     # returns "5 tokens"
            token_label(0)     # returns "0 tokens"
            ```
        ''',
        "starter": r'''
            def token_label(n):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import token_label

            def test_one_is_singular():
                got = token_label(1)
                assert got == "1 token", f"token_label(1) returned {got!r}"

            def test_other_counts_are_plural():
                for n, want in ((5, "5 tokens"), (0, "0 tokens"), (1000, "1000 tokens")):
                    got = token_label(n)
                    assert got == want, f"token_label({n}) returned {got!r}"

            def test_uses_a_conditional_expression():
                ok = any(isinstance(n, ast.IfExp) for n in ast.walk(ast.parse(source())))
                assert ok, "pick the word with a conditional expression (x if condition else y)"
        ''',
        "solution": r'''
            def token_label(n):
                word = "token" if n == 1 else "tokens"
                return str(n) + " " + word
        ''',
        "hints": [
            "A one-line if picks between two values: value_if_true if condition else value_if_false.",
            "Pick the word with a conditional expression that checks whether n equals 1, then glue the number (as text), a space and the word.",
            "1) word = \"token\" if n == 1 else \"tokens\". 2) Return str(n) + \" \" + word.",
        ],
    },
    {
        "id": "conditionals-9",
        "title": "Match the role",
        "difficulty": 1,
        "research": {
            "note": 'Read the short tutorial section on match statements (up to the part about combining patterns with |), then come back.',
            "links": [
                {"title": 'match statements - Python tutorial', "url": 'https://docs.python.org/3/tutorial/controlflow.html#match-statements'},
            ],
        },
        "lesson": r'''
            When you compare **one value** against a list of possibilities, a `match` statement
            reads like a **switchboard**: the value comes in, and it's connected to the first
            line that fits.

            ```python
            status = 404
            match status:
                case 200:
                    print("ok")
                case 404 | 410:
                    print("not found")
                case _:
                    print("something else")
            ```

            - `match value:` then one `case` per possibility, each with its own indented block.
            - `|` inside a case means "or": either value matches.
            - `case _:` matches anything - put it last as the catch-all.
            - Cases are tried top to bottom; only the first match runs.

            Inside a function, each case can simply `return` its answer.

            Vocabulary: this is *structural pattern matching*; each thing after `case` is a
            *pattern*, and `_` is the *wildcard*.

            Watch out: `match` needs Python 3.10 or newer.
        ''',
        "prompt": r'''
            A chat app sorts each message by its role.

            **Write:** `role_kind(role)`

            - `role`: a message role, usually a string like `"user"`, but it can be anything (e.g. `None`)
            - **Returns:** one of the strings `"instructions"`, `"chat"`, `"tool result"`, `"unknown"`

            **Rules**
            - Use a **`match` statement** (a check looks for it).

            | `role` | return |
            | --- | --- |
            | `"system"` | `"instructions"` |
            | `"user"` or `"assistant"` | `"chat"` |
            | `"tool"` | `"tool result"` |
            | anything else (other text, `"User"` with a capital, `None`) | `"unknown"` |

            **Examples**
            ```python
            role_kind("system")      # returns "instructions"
            role_kind("assistant")   # returns "chat"
            role_kind("tool")        # returns "tool result"
            role_kind(None)          # returns "unknown"
            ```
        ''',
        "starter": r'''
            def role_kind(role):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import role_kind

            def test_system_is_instructions():
                got = role_kind("system")
                assert got == "instructions", f"role_kind('system') returned {got!r}"

            def test_user_and_assistant_are_chat():
                for r in ("user", "assistant"):
                    got = role_kind(r)
                    assert got == "chat", f"role_kind({r!r}) returned {got!r}"

            def test_tool_is_tool_result():
                got = role_kind("tool")
                assert got == "tool result", f"role_kind('tool') returned {got!r}"

            def test_anything_else_is_unknown():
                for r in ("User", "developer", "", None):
                    got = role_kind(r)
                    assert got == "unknown", f"role_kind({r!r}) returned {got!r}"

            def test_uses_a_match_statement():
                ok = any(isinstance(n, ast.Match) for n in ast.walk(ast.parse(source())))
                assert ok, "use a match statement"
        ''',
        "solution": r'''
            def role_kind(role):
                match role:
                    case "system":
                        return "instructions"
                    case "user" | "assistant":
                        return "chat"
                    case "tool":
                        return "tool result"
                    case _:
                        return "unknown"
        ''',
        "hints": [
            "match role: followed by one case per row of the table. The docs section shows | and _.",
            "Write a case for system, one case that covers user or assistant with |, one for tool, and a wildcard case last.",
            "1) match role: 2) case \"system\": return instructions. 3) case \"user\" | \"assistant\": return chat. 4) case \"tool\": return tool result. 5) case _: return unknown.",
        ],
    },
    {
        "id": "conditionals-3",
        "hints": ['Rules checked in a fixed order with early returns: the first matching rule wins.', "Write one if per rule, in the order given, each returning its model name. Rule 3 needs two conditions joined with and. The final return is the 'otherwise'.", '1) if prompt_tokens > 128000 return reject. 2) if needs_vision return vision-large. 3) if budget_mode and prompt_tokens <= 8000 return mini. 4) if prompt_tokens > 32000 return long-context. 5) return standard.'],
        "title": "Route to a model tier",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A router decides which model tier handles each request.

            **Write:** `pick_model(prompt_tokens, needs_vision=False, budget_mode=False)`

            - `prompt_tokens`: prompt length, an `int`, e.g. `500`
            - `needs_vision`: `True` if the request has images; defaults to `False`
            - `budget_mode`: `True` if the user wants the cheapest option; defaults to `False`
            - **Returns:** one of the strings `"reject"`, `"vision-large"`, `"mini"`, `"long-context"`, `"standard"`

            **Rules** - check them **in this order**, the first one that matches wins:
            1. `prompt_tokens` more than `128000` -> `"reject"` (even if the other flags are set)
            2. `needs_vision` is true -> `"vision-large"` (even in budget mode)
            3. `budget_mode` is true **and** `prompt_tokens` is `8000` or less -> `"mini"`
            4. `prompt_tokens` more than `32000` -> `"long-context"`
            5. otherwise -> `"standard"`

            Boundaries: `8000` can be mini, `8001` cannot; `32000` is standard, `32001` is
            long-context; `128000` is long-context, `128001` is reject.

            **Examples**
            ```python
            pick_model(500)                                            # returns "standard"
            pick_model(8000, budget_mode=True)                         # returns "mini"
            pick_model(8001, budget_mode=True)                         # returns "standard"
            pick_model(40000, budget_mode=True)                        # returns "long-context"
            pick_model(100, needs_vision=True, budget_mode=True)       # returns "vision-large"
            pick_model(200000, needs_vision=True, budget_mode=True)    # returns "reject"
            ```
        ''',
        "starter": r'''
            def pick_model(prompt_tokens, needs_vision=False, budget_mode=False):
                ...
        ''',
        "tests": r'''
            from solution import pick_model

            def test_small_prompt_with_no_flags_is_standard():
                assert pick_model(500) == "standard", f"got {pick_model(500)!r}"

            def test_over_128000_is_rejected_even_with_flags():
                got = pick_model(200000, needs_vision=True, budget_mode=True)
                assert got == "reject", f"got {got!r}"

            def test_vision_wins_over_budget_mode():
                got = pick_model(100, needs_vision=True, budget_mode=True)
                assert got == "vision-large", f"got {got!r}"

            def test_budget_mode_gives_mini_only_up_to_8000_tokens():
                assert pick_model(8000, budget_mode=True) == "mini"
                got = pick_model(8001, budget_mode=True)
                assert got == "standard", f"pick_model(8001, budget_mode=True) -> {got!r}"
                got = pick_model(40000, budget_mode=True)
                assert got == "long-context", f"pick_model(40000, budget_mode=True) -> {got!r}"

            def test_32000_and_128000_boundaries():
                assert pick_model(32000) == "standard"
                assert pick_model(32001) == "long-context"
                assert pick_model(128000) == "long-context"
                assert pick_model(128001) == "reject"
        ''',
        "solution": r'''
            def pick_model(prompt_tokens, needs_vision=False, budget_mode=False):
                if prompt_tokens > 128000:
                    return "reject"
                if needs_vision:
                    return "vision-large"
                if budget_mode and prompt_tokens <= 8000:
                    return "mini"
                if prompt_tokens > 32000:
                    return "long-context"
                return "standard"
        ''',
    },
    {
        "id": "conditionals-4",
        "title": "Truthy defaults",
        "difficulty": 2,
        "prompt": r'''
            A chat UI needs a name to show next to each message, falling back when data is missing.

            **Write:** `display_name(nickname, full_name, user_id)`

            - `nickname`: a string like `" ada "`, or `None`
            - `full_name`: a string like `"Ada Lovelace"`, or `None`
            - `user_id`: an `int` like `42`, or `None`
            - **Returns:** a string

            **Rules** - use the first one that applies:
            1. If `nickname` has real characters, return it with surrounding whitespace removed.
            2. Else if `full_name` has real characters, return it with surrounding whitespace removed.
            3. Else if `user_id` is not `None`, return `"user-"` followed by the id, e.g. `"user-42"`.
               **`0` is a valid id** and gives `"user-0"`.
            4. Else return `"Anonymous"`.

            - `None`, `""` and whitespace-only text (like `"   "` or `" \n"`) all count as empty.

            **Examples**
            ```python
            display_name(" ada ", "Ada L", 1)     # returns "ada"
            display_name("", "Ada Lovelace", 7)   # returns "Ada Lovelace"
            display_name(None, None, 42)          # returns "user-42"
            display_name("   ", None, 0)          # returns "user-0"
            display_name(None, " ", None)         # returns "Anonymous"
            ```
        ''',
        "starter": r'''
            def display_name(nickname, full_name, user_id):
                ...
        ''',
        "tests": r'''
            from solution import display_name

            def test_nickname_wins_and_whitespace_is_removed():
                got = display_name(" ada ", "Ada L", 1)
                assert got == "ada", f"got {got!r}"

            def test_empty_nickname_falls_back_to_full_name():
                got = display_name("", "Ada Lovelace", 7)
                assert got == "Ada Lovelace", f"got {got!r}"

            def test_none_nickname_falls_back_to_full_name():
                got = display_name(None, "Grace", None)
                assert got == "Grace", f"got {got!r}"

            def test_no_names_falls_back_to_user_id():
                got = display_name(None, None, 42)
                assert got == "user-42", f"got {got!r}"

            def test_user_id_zero_gives_user_0():
                got = display_name("   ", None, 0)
                assert got == "user-0", f"got {got!r}"

            def test_nothing_usable_returns_anonymous():
                got = display_name(None, " \n", None)
                assert got == "Anonymous", f"got {got!r}"
        ''',
        "solution": r'''
            def display_name(nickname, full_name, user_id):
                nickname = (nickname or "").strip()
                if nickname:
                    return nickname
                full_name = (full_name or "").strip()
                if full_name:
                    return full_name
                if user_id is not None:
                    return "user-" + str(user_id)
                return "Anonymous"
        ''',
        "hints": [
            "None has no .strip(), so turn None into \"\" first (x or \"\" does that). Empty text is falsy. For the id, 0 is falsy but still valid, so test it with is not None.",
            "Check the three sources in order with early returns: clean the nickname and return it if anything is left, then the same for the full name, then the id, then the fallback.",
            "1) nickname = (nickname or \"\").strip(); if it is truthy return it. 2) Same for full_name. 3) if user_id is not None, return \"user-\" glued to str(user_id). 4) return \"Anonymous\".",
        ],
    },
    {
        "id": "conditionals-5",
        "title": "Match on message shape",
        "difficulty": 3,
        "research": {
            "note": 'match can do much more than compare strings. Read the pattern-matching tutorial (the sections on matching sequences and guards are enough), then come back.',
            "links": [
                {"title": 'PEP 636 - Structural pattern matching tutorial', "url": 'https://peps.python.org/pep-0636/'},
            ],
        },
        "prompt": r'''
            Chat messages arrive as tuples of different shapes. Summarize each one in a line of text.

            **Write:** `summarize(message)`

            - `message`: usually a tuple like `("user", "hi")` or `("assistant", "tool", "search")`,
              but it can be anything (a string, `None`, a tuple of the wrong length)
            - **Returns:** a string

            **Rules**
            - You must use a **`match` statement** (a check looks for it).

            | message | return |
            | --- | --- |
            | `("system", text)` where `text` is a `str` | `"system: "` followed by text |
            | `("user", text)` where `text` is a **non-empty** `str` | `"user: "` followed by text |
            | `("assistant", "tool", name)` where `name` is a `str` | `"assistant calls "` followed by name |
            | `("assistant", text)` where `text` is a `str` | `"assistant: "` followed by text |
            | anything else | `"invalid"` |

            - "Anything else" includes: unknown roles like `"tool"`, the wrong number of items
              (`("user",)`, `("system", "a", "b")`), an empty user text, a text that is not a
              string (`("user", 42)`, `("assistant", 5)`), and values that are not tuples
              (`"hello"`, `None`).

            **Examples**
            ```python
            summarize(("system", "be terse"))            # returns "system: be terse"
            summarize(("user", "hi"))                    # returns "user: hi"
            summarize(("assistant", "tool", "search"))   # returns "assistant calls search"
            summarize(("assistant", "done"))             # returns "assistant: done"
            summarize(("user", ""))                      # returns "invalid"
            summarize(None)                              # returns "invalid"
            ```
        ''',
        "starter": r'''
            def summarize(message):
                ...
        ''',
        "tests": r'''
            from solution import summarize

            def test_system_message():
                got = summarize(("system", "be terse"))
                assert got == "system: be terse", f"got {got!r}"

            def test_user_message():
                got = summarize(("user", "hi"))
                assert got == "user: hi", f"got {got!r}"

            def test_assistant_tool_call():
                got = summarize(("assistant", "tool", "search"))
                assert got == "assistant calls search", f"got {got!r}"

            def test_assistant_text_message():
                got = summarize(("assistant", "done"))
                assert got == "assistant: done", f"got {got!r}"

            def test_wrong_roles_lengths_types_return_invalid():
                for m in (("tool", "x"), ("user", ""), ("user", 42), ("user",),
                          ("assistant", 5), ("system", "a", "b"), "hello", None):
                    got = summarize(m)
                    assert got == "invalid", f"{m!r} -> {got!r}"

            def test_uses_a_match_statement():
                import ast
                ok = any(isinstance(n, ast.Match) for n in ast.walk(ast.parse(source())))
                assert ok, "use a match statement"
        ''',
        "solution": r'''
            def summarize(message):
                match message:
                    case ("system", str(text)):
                        return "system: " + text
                    case ("user", str(text)) if text:
                        return "user: " + text
                    case ("assistant", "tool", str(name)):
                        return "assistant calls " + name
                    case ("assistant", str(text)):
                        return "assistant: " + text
                    case _:
                        return "invalid"
        ''',
        "hints": [
            "match can compare a tuple against tuple patterns. str(text) inside a pattern matches only strings and captures the value. A case can have a guard: case pattern if condition:",
            "Write one case per row of the table, each pattern shaped like the tuple it describes. Use a guard for 'non-empty'. End with case _ for everything else.",
            "1) case (\"system\", str(text)). 2) case (\"user\", str(text)) with the guard if text. 3) case with three items: \"assistant\", \"tool\", str(name). 4) case (\"assistant\", str(text)). 5) case _ returns invalid. Build each result with +.",
        ],
    },
    {
        "id": "conditionals-6",
        "title": "Rate limit status",
        "difficulty": 3,
        "prompt": r'''
            A dashboard shows how much of an API rate limit has been used.

            **Write:** `rate_status(used, limit)`

            - `used`: requests used so far: an `int`, numeric text such as `" 85 "`, or `None`
            - `limit`: the maximum allowed: an `int`, numeric text such as `"100\n"`, or `None`
            - **Returns:** a string, exactly one of the formats below

            **Rules** - check **in this order**, the first one that matches wins:
            1. If either argument is `None`: `"ERROR: missing value"` (even if the other is `0`).
            2. Convert numeric text to a whole number; surrounding spaces/newlines are allowed.
            3. If `limit` is `0` or negative: `"ERROR: limit must be positive"`.
            4. If `used` is equal to or more than `limit`: `"BLOCKED"`.
            5. If `used` is **at least 80%** of `limit`: `"WARN <p>%"`, where `p` is the whole
               percent `used * 100 / limit` rounded **down** (e.g. 5 of 6 is 83.33... -> `"WARN 83%"`).
               Exactly 80% counts (4 of 5, 56 of 70); make sure it is not missed by a tiny float error.
            6. Otherwise: `"OK <remaining> left"`, where remaining is `limit - used`.

            **Examples**
            ```python
            rate_status(10, 100)        # returns "OK 90 left"
            rate_status(79, 100)        # returns "OK 21 left"
            rate_status(56, 70)         # returns "WARN 80%"
            rate_status(5, 6)           # returns "WARN 83%"
            rate_status("85", " 100 ")  # returns "WARN 85%"
            rate_status("150", 100)     # returns "BLOCKED"
            rate_status(0, 0)           # returns "ERROR: limit must be positive"
            rate_status(None, 0)        # returns "ERROR: missing value"
            ```
        ''',
        "starter": r'''
            def rate_status(used, limit):
                ...
        ''',
        "tests": r'''
            from solution import rate_status

            def check(used, limit, expected):
                got = rate_status(used, limit)
                assert got == expected, f"rate_status({used!r}, {limit!r}) returned {got!r}"

            def test_under_80_percent_shows_remaining():
                check(10, 100, "OK 90 left")
                check(79, 100, "OK 21 left")

            def test_80_percent_or_more_warns_with_percent_rounded_down():
                check(80, 100, "WARN 80%")
                check(5, 6, "WARN 83%")
                check(99, 100, "WARN 99%")

            def test_exactly_80_percent_of_odd_limits_warns():
                check(4, 5, "WARN 80%")
                check(56, 70, "WARN 80%")

            def test_numeric_text_is_converted():
                check("85", " 100 ", "WARN 85%")
                check(" 1 ", "10\n", "OK 9 left")

            def test_at_or_over_limit_is_blocked():
                check(100, 100, "BLOCKED")
                check("150", 100, "BLOCKED")

            def test_missing_value_checked_before_non_positive_limit():
                check(None, 100, "ERROR: missing value")
                check(5, None, "ERROR: missing value")
                check(None, 0, "ERROR: missing value")
                check(0, 0, "ERROR: limit must be positive")
                check(5, "-3", "ERROR: limit must be positive")
        ''',
        "solution": r'''
            def rate_status(used, limit):
                if used is None or limit is None:
                    return "ERROR: missing value"
                used = int(used)
                limit = int(limit)
                if limit <= 0:
                    return "ERROR: limit must be positive"
                if used >= limit:
                    return "BLOCKED"
                if used * 100 >= limit * 80:
                    return "WARN " + str(used * 100 // limit) + "%"
                return "OK " + str(limit - used) + " left"
        ''',
        "hints": [
            "Early returns in the given order. int() converts both ints and numeric text (it ignores spaces). // divides and rounds down.",
            "Check None before converting. After converting, go through the rules top to bottom. Compare 'at least 80%' with whole numbers by multiplying both sides by 100 instead of dividing.",
            "1) If either is None, return the missing error. 2) Convert both with int(). 3) limit <= 0 -> positive error. 4) used >= limit -> BLOCKED. 5) used * 100 >= limit * 80 -> WARN plus str(used * 100 // limit) plus %. 6) Otherwise OK plus str(limit - used) plus left.",
        ],
    },
]
