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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["if", "elif", "else", "condition", "branch", "comparison", "and", "or", "not",
                 "in", "truthy", "early return", "conditional expression", "ternary", "match",
                 "case"],
    "cards": [
        {
            "syntax": "if condition:  /  elif condition:  /  else:",
            "explain": "Runs the block under the first condition that is True and skips the rest. else runs when none is True.",
            "example": r'''
                tokens = 700
                if tokens > 1000:
                    print("too long")
                elif tokens > 500:
                    print("long")
                else:
                    print("short")
                # long
            ''',
        },
        {
            "syntax": "a and b    a or b    not a",
            "explain": "and needs both sides to be true. or needs at least one. not turns True into False and False into True.",
            "example": r'''
                status = 429
                attempts = 1
                print(status == 429 and attempts < 3)
                # True
                print(status == 500 or attempts >= 3)
                # False
                print(not attempts < 3)
                # False
            ''',
        },
        {
            "syntax": "low <= x <= high    x in (a, b)",
            "explain": "A chained comparison tests both limits at once. in is True when x equals one of the items.",
            "example": r'''
                t = 1.5
                print(0 <= t <= 2)
                # True
                reason = "stop"
                print(reason in ("tool_calls", "function_call"))
                # False
            ''',
        },
        {
            "syntax": "if value:    value or default",
            "explain": "if value: tests truthiness. \"\", 0 and None are falsy. a or b gives a when a is truthy, otherwise b.",
            "example": r'''
                name = None
                print(name or "anonymous")
                # anonymous
                title = (name or "").strip()
                if not title:
                    print("no title")
                # no title
            ''',
        },
        {
            "syntax": "value_a if condition else value_b",
            "explain": "A conditional expression. It produces value_a when the condition is True and value_b otherwise.",
            "example": r'''
                n = 3
                word = "token" if n == 1 else "tokens"
                print(str(n) + " " + word)
                # 3 tokens
            ''',
        },
        {
            "syntax": "match value:  /  case pattern:  /  case _:",
            "explain": "Runs the block of the first case whose pattern matches. | means or. case _: matches any value.",
            "example": r'''
                role = "user"
                match role:
                    case "user" | "assistant":
                        print("chat")
                    case _:
                        print("unknown")
                # chat
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Conditionals

### if, elif, else

An `if` statement runs a block of code only when a condition is `True`. A **condition** is
an expression that Python evaluates to `True` or `False`. Each `if`, `elif` and `else` line
ends with `:`. The block under it is indented by 4 spaces. Such a block is also called a
**branch**.

Python checks the conditions from top to bottom. It runs the block under the first
condition that is `True` and skips every other block. The `else` block runs when no
condition above it is `True`.

```python
tokens = 700
if tokens > 1000:
    print("too long")
elif tokens > 500:
    print("long")
else:
    print("short")
print("done")
# long
# done
```

Step through the code to see which lines Python runs and which it skips.

```diagram
{"type": "trace", "title": "Which branch runs when tokens is 700", "code": ["tokens = 700", "if tokens > 1000:", "    print(\"too long\")", "elif tokens > 500:", "    print(\"long\")", "else:", "    print(\"short\")", "print(\"done\")"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {"tokens": "700"}, "out": ""},
  {"line": 4, "vars": {"tokens": "700"}, "out": ""},
  {"line": 5, "vars": {"tokens": "700"}, "out": ""},
  {"line": 8, "vars": {"tokens": "700"}, "out": "long\n"},
  {"line": null, "vars": {"tokens": "700"}, "out": "long\ndone\n"}
]}
```

### Comparisons

The operators `==`, `!=`, `<`, `<=`, `>` and `>=` compare two values and produce a `bool`.
`=` assigns a value to a name. `==` tests whether two values are equal.

```python
tokens = 700
print(tokens > 500, tokens == 500, tokens != 500)
# True False True
```

A **chained comparison** uses two operators in one expression. `0 <= t <= 2` means
`0 <= t and t <= 2`.

```python
t = 1.5
print(0 <= t <= 2)
# True
```

### and, or, not

`a and b` gives a truthy result only when both sides are truthy. `a or b` gives a truthy
result when at least one side is truthy. `not a` turns `True` into `False` and `False`
into `True`. (Used as plain values rather than conditions, `and` and `or` return one of
their two sides. The section "Truthiness and the or fallback" below shows how.)

```python
status = 429
attempts = 1
print(status == 429 and attempts < 3)
# True
print(status == 500 or attempts < 3)
# True
print(not attempts < 3)
# False
```

### Membership

`value in (a, b)` is `True` when `value` equals one of the items in the tuple.

```python
reason = "function_call"
print(reason in ("tool_calls", "function_call"))
# True
```

### Early return

`return` ends the function call immediately. A sequence of `if ...: return ...` lines
therefore behaves the same as an `elif` chain. The last `return` runs only when no
condition was `True`.

```python
def tier(tokens):
    if tokens > 1000:
        return "large"
    if tokens > 100:
        return "medium"
    return "small"

print(tier(5000), tier(500), tier(5))
# large medium small
```

### Truthiness and the or fallback

`if text:` tests the truthiness of `text`. The values `""`, `0` and `None` are falsy, so
the block is skipped for them. Use `is None` or `is not None` when `0` or `""` is a valid
value.

`a or b` evaluates to `a` when `a` is truthy, and to `b` otherwise.
`(name or "").strip()` replaces `None` with `""` before it calls `.strip()`.

```python
name = None
print(name or "anonymous")
# anonymous
count = 0
print(count is not None)
# True
```

### Conditional expression

A **conditional expression** picks one of two values in a single line. The value before
`if` is used when the condition is `True`. The value after `else` is used otherwise.

```python
score = 0.8
print("pass" if score >= 0.5 else "fail")
# pass
```

### match

A `match` statement (Python 3.10 and newer) compares one value against the pattern of
each `case`, from top to bottom. A **pattern** is the description of a value that you write
after the word `case`. Only the block of the first matching `case` runs. `|` means "or": it
separates several values that one `case` accepts. `case _:` matches any value.

```python
role = "user"
match role:
    case "system":
        print("instructions")
    case "user" | "assistant":
        print("chat")
    case _:
        print("unknown")
# chat
```

A pattern can describe a tuple. The value matches only when it has the same number of
items and each item matches. `str(text)` matches only a string and assigns it to the name
`text`, so `("user", 5)` does not match the first case below. An `if` after the pattern
is a **guard**: an extra condition that must also be true for the case to match. Here the
guard `if text` rejects the empty string, because `""` is falsy.

```python
message = ("user", "hi")
match message:
    case ("user", str(text)) if text:
        print("user said " + text)
    case _:
        print("invalid")
# user said hi
```

### Common mistakes

`if reason == "stop" or "tool_calls":` is always true. Python evaluates it as
`(reason == "stop") or "tool_calls"`, and a non-empty string is truthy. Write
`reason == "stop" or reason == "tool_calls"`, or use `in`.

```python
reason = "length"
if reason == "stop" or "tool_calls":
    print("always runs")
# always runs
```

Order matters in a chain. With `>` thresholds, test the largest threshold first.
Otherwise a smaller threshold matches first and the later branch never runs.

A function that reaches its end without running a `return` statement returns `None`.

```python
def label(score):
    if score >= 0.5:
        return "pass"

print(label(0.2))
# None
```
'''

EXERCISES = [
    {
        "id": "conditionals-s2",
        "title": "Fill in the condition",
        "difficulty": 0,
        "lesson": r'''
            ## The if statement

            An `if` statement runs a block of code only when a condition is `True`. A **condition**
            is an expression that Python evaluates to `True` or `False`, such as `cost > 10`.

            ```python
            cost = 12
            if cost > 10:
                print("over budget")
            print("checked")
            # over budget
            # checked
            ```

            You write `if`, then the condition, then a colon `:`. The lines indented by 4 spaces
            under it are the **if block**, also called a **branch**. Python runs the block when the
            condition is `True` and skips it when the condition is `False`.

            `print("checked")` is not indented, so it is not part of the block. It runs in both cases.

            ### if inside a function

            A `return` statement ends the function call immediately and sends its value to the
            code that called the function. When the condition is `False`, Python skips the block and continues with the
            next line after it.

            ```python
            def check(cost):
                if cost > 10:
                    return "over budget"
                return "ok"

            print(check(3))
            # ok
            print(check(12))
            # over budget
            ```

            Step through both calls to see which `return` line runs each time.

            ```diagram
            {"type": "trace", "title": "Two calls to check(cost)", "code": ["def check(cost):", "    if cost > 10:", "        return \"over budget\"", "    return \"ok\"", "", "print(check(3))", "print(check(12))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 6, "vars": {}, "out": ""},
              {"line": 2, "vars": {"cost": "3"}, "out": ""},
              {"line": 4, "vars": {"cost": "3"}, "out": ""},
              {"line": 7, "vars": {}, "out": "ok\n"},
              {"line": 2, "vars": {"cost": "12"}, "out": "ok\n"},
              {"line": 3, "vars": {"cost": "12"}, "out": "ok\n"},
              {"line": null, "vars": {}, "out": "ok\nover budget\n"}
            ]}
            ```

            `>` means "more than" and does not include the limit itself: `10 > 10` is `False`.
            `>=` means "more than or equal to", so `10 >= 10` is `True`.
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
            ## Assignment and equality

            `=` and `==` are two different operators.

            - `=` is the **assignment operator**. `role = "user"` makes the name `role` refer to the
              string `"user"`.
            - `==` is the **equality operator**. `role == "user"` compares the two values and
              produces `True` or `False`. It does not change `role`.
            - `!=` is the "not equal" operator. It produces `True` when the two values differ.

            ```python
            role = "user"
            print(role == "system")
            # False
            print(role == "user")
            # True
            print(role != "system")
            # True
            ```

            The condition of an `if` must be a comparison, not an assignment. Python rejects
            `if role = "user":` with a `SyntaxError` before it runs any line of the file. The
            message reads `invalid syntax. Maybe you meant '==' or ':=' instead of '='?`. (`:=` is
            another operator that you do not need yet. Use `==` here.)

            Python compares strings character by character, and uppercase and lowercase letters are
            different characters.

            ```python
            print("User" == "user")
            # False
            ```
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
            ## if and else

            An `if` on its own runs its block or does nothing. Add `else:` to give Python a second
            block to run when the condition is `False`.

            ```python
            latency = 3.2
            if latency <= 2:
                print("fast")
            else:
                print("slow")
            # slow
            ```

            Exactly one of the two blocks runs. `else` has no condition. Its block runs every time
            the `if` condition is `False`.

            ### return instead of else

            Inside a function you can leave out `else`. `return` ends the function call, so the
            line after the `if` block only runs when the condition was `False`.

            ```python
            def speed(latency):
                if latency <= 2:
                    return "fast"
                return "slow"

            print(speed(2), speed(3.2))
            # fast slow
            ```

            "At most" means `<=` and "at least" means `>=`. Both include the limit itself. The
            value where the result changes is the **boundary**. `speed(2)` returns `"fast"` because
            `2 <= 2` is `True`. Always test the boundary value itself.
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
            ## elif

            Some decisions have more than two outcomes. `elif` (short for "else if") adds another
            condition to an `if` statement. An `if` followed by `elif` and `else` lines is a
            **conditional chain**.

            ```python
            ms = 250
            if ms < 200:
                print("fast")
            elif ms < 1000:
                print("normal")
            elif ms < 5000:
                print("slow")
            else:
                print("timeout")
            print("labelled")
            # normal
            # labelled
            ```

            Python checks the conditions from the top. It runs the block under the first condition
            that is `True` and skips every branch after it, even a branch whose condition is also
            `True`. Here `ms < 5000` is `True` for 250, but Python never checks it.

            Step through the code to see which lines are skipped.

            ```diagram
            {"type": "trace", "title": "Which branch runs when ms is 250", "code": ["ms = 250", "if ms < 200:", "    print(\"fast\")", "elif ms < 1000:", "    print(\"normal\")", "elif ms < 5000:", "    print(\"slow\")", "else:", "    print(\"timeout\")", "print(\"labelled\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"ms": "250"}, "out": ""},
              {"line": 4, "vars": {"ms": "250"}, "out": ""},
              {"line": 5, "vars": {"ms": "250"}, "out": ""},
              {"line": 10, "vars": {"ms": "250"}, "out": "normal\n"},
              {"line": null, "vars": {"ms": "250"}, "out": "normal\nlabelled\n"}
            ]}
            ```

            The second condition only needs `ms < 1000`. Python reaches that line only when
            `ms < 200` was `False`, so `ms` is already known to be 200 or more.

            A chain can have any number of `elif` lines. The `else` is optional.

            Order matters. If `ms < 1000` came first, a value of 50 would print `normal`, because
            `50 < 1000` is `True` and Python stops at the first match.
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
            ## and, or, not

            A decision often depends on two conditions. The **boolean operators** `and`, `or` and
            `not` combine conditions into one. They are also called **logical operators**.

            - `a and b` is `True` only when both `a` and `b` are `True`.
            - `a or b` is `True` when at least one of `a` and `b` is `True`.
            - `not a` is `False` when `a` is `True`, and `True` when `a` is `False`.

            ```python
            score = 0.9
            flagged = False
            print(score >= 0.5 and flagged == False)
            # True
            print(score < 0.5 or flagged == True)
            # False
            print(not flagged)
            # True
            ```

            Each result is a `bool`. You can use it as the condition of an `if`, or return it
            directly from a function.

            ```python
            def can_publish(score, flagged):
                return score >= 0.5 and not flagged

            print(can_publish(0.9, False), can_publish(0.9, True))
            # True False
            ```

            Each side of `and` and `or` must be a complete expression. `score >= 0.5 and < 1` is a
            `SyntaxError`. Write the name again: `score >= 0.5 and score < 1`.
        ''',
        "prompt": r'''
            When an API answers with status `429` (rate limited) you may retry, but only a
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
            ## Tracing a conditional chain

            **Tracing** means reading code line by line and working out what each line does
            before you run it. Two rules cover a conditional chain.

            1. In an `if` / `elif` / `else` chain, exactly one block runs: the block under the
               first condition that is `True`. If no condition is `True`, the `else` block runs.
            2. A line that is not indented comes after the chain. It runs every time, whichever
               block ran.

            ```python
            tokens = 50
            if tokens > 100:
                print("big")
            else:
                print("small")
            print(tokens < 100 and tokens > 10)
            # small
            # True
            ```

            `50 > 100` is `False`, so Python skips `print("big")` and runs the `else` block. The
            last line is not indented, so it runs next. `50 < 100` is `True` and `50 > 10` is
            `True`, so `and` produces `True`.
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
            ## Chained comparisons

            A setting often has to lie between two limits. A **chained comparison** uses two
            comparison operators in one expression.

            ```python
            t = 1.5
            print(0 <= t <= 2)
            # True
            print(0 <= 3 <= 2)
            # False
            ```

            `0 <= t <= 2` means `0 <= t and t <= 2`. Both comparisons must be `True`. The second
            line prints `False` because `3 <= 2` is `False`.

            `<=` includes the limit. A range with "both ends included" is called **inclusive** and
            uses `<=` on both sides. Use `<` on a side that excludes its limit.

            ### Returning a comparison

            A comparison already produces `True` or `False`. A function can return that value
            directly, without an `if`.

            ```python
            def is_small(n):
                return 0 <= n < 100

            print(is_small(5), is_small(500), is_small(100))
            # True False False
            ```

            `is_small(100)` is `False` because `100 < 100` is `False`.

            `if ...: return True` followed by `else: return False` gives the same result in four
            lines. Returning the comparison itself is shorter and does the same thing.
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
            ## Membership with in

            `in` is the **membership operator**. `value in (a, b)` is `True` when `value` equals
            one of the items in the tuple. Use it when several values share one result.

            ```python
            reason = "function_call"
            print(reason in ("tool_calls", "function_call"))
            # True
            print("stop" in ("tool_calls", "function_call"))
            # False
            ```

            ### in inside an elif chain

            Each branch of a chain can handle one known value, or a group of values with `in`.
            The `else` branch handles every other value. That includes `None` and text with
            different capital letters, because `==` and `in` compare strings exactly.

            ```python
            def label(role):
                if role == "user":
                    return "person"
                elif role in ("assistant", "model"):
                    return "AI"
                else:
                    return "unknown"

            print(label("model"), label(None), label("User"))
            # AI unknown unknown
            ```

            `if reason == "a" or "b":` is always true. Python evaluates it as
            `(reason == "a") or "b"`, and the non-empty string `"b"` is truthy. Write
            `reason in ("a", "b")` instead.
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
            ## Truthiness and the or fallback

            The condition of an `if` does not have to be a comparison. `if name:` tests the
            truthiness of `name`. An empty string, `0` and `None` are falsy. A string with at
            least one character is truthy.

            ```python
            name = ""
            if name:
                print("hi", name)
            else:
                print("no name")
            # no name
            ```

            ### The value of a or b

            `a or b` evaluates to `a` when `a` is truthy. Otherwise it evaluates to `b`. The
            result is one of the two values, not always a `bool`.

            ```python
            print("draft" or "Untitled")
            # draft
            print(None or "Untitled")
            # Untitled
            ```

            A value that is used when the real one is missing is a **fallback**, also called a
            **default**.

            ### Stripping a value that may be None

            Missing data is often `None`. `None` has no `.strip()` method, so `None.strip()` stops
            the program with an `AttributeError`: the value does not have that method. `(note or "")` evaluates to `""` when `note` is `None`, and `""` does
            have `.strip()`.

            ```python
            note = None
            note = (note or "").strip()
            print(note == "")
            # True
            ```

            After that line `note` is always a string with no spaces or newlines at either end.
            A plain `if note:` then tells you whether any characters are left.

            When `0` is a valid value, do not test truthiness, because `0` is falsy. Test
            `is None` or `is not None` instead.
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
            "Replace None with an empty string using or, strip the result, then return it if anything is left. Otherwise return the fallback.",
            "1) title = (title or \"\").strip(). 2) if title: return title. 3) After the if, return \"Untitled\".",
        ],
    },
    {
        "id": "conditionals-8",
        "title": "1 token, 2 tokens",
        "difficulty": 1,
        "lesson": r'''
            ## Conditional expressions

            A **conditional expression** chooses between two values in one line. Other languages
            call it a **ternary operator**, because it has three parts: two values and a condition.

            ```python
            score = 0.8
            verdict = "pass" if score >= 0.5 else "fail"
            print(verdict)
            # pass
            ```

            The order is: the value used when the condition is `True`, then `if` and the
            condition, then `else` and the value used when the condition is `False`.

            An `if` statement runs a block. A conditional expression is an **expression**: it
            produces a value. You can assign that value to a name, return it, or join it to a
            string with `+`.

            Put parentheses around a conditional expression when you join it to something else.

            ```python
            n = 3
            print(str(n) + (" item" if n == 1 else " items"))
            # 3 items
            print(str(n) + " item" if n == 1 else " items")
            #  items
            ```

            Without the parentheses Python reads the second line as
            `(str(n) + " item") if n == 1 else " items"`, so the number is lost when `n` is not 1.

            Use a conditional expression for a short choice between two values. Use a normal
            `if` statement for anything longer.
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
            ## The match statement

            A `match` statement compares one value against several possibilities. Each
            possibility is written after the word `case` and is called a **pattern**. Comparing
            a value against patterns this way is called **structural pattern matching**.

            ```python
            status = 404
            match status:
                case 200:
                    print("ok")
                case 404 | 410:
                    print("not found")
                case _:
                    print("something else")
            print("handled")
            # not found
            # handled
            ```

            - You write `match`, the value, and a colon. Each `case` line is indented and has its
              own indented block.
            - Python tries the cases from top to bottom and runs only the block of the first
              pattern that matches.
            - `|` inside a pattern means "or": `404 | 410` matches either number.
            - `_` is the **wildcard** pattern. `case _:` matches any value, so put it last.

            Step through the code to see which `case` lines Python tries.

            ```diagram
            {"type": "trace", "title": "Matching status 404 against each case", "code": ["status = 404", "match status:", "    case 200:", "        print(\"ok\")", "    case 404 | 410:", "        print(\"not found\")", "    case _:", "        print(\"something else\")", "print(\"handled\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"status": "404"}, "out": ""},
              {"line": 3, "vars": {"status": "404"}, "out": ""},
              {"line": 5, "vars": {"status": "404"}, "out": ""},
              {"line": 6, "vars": {"status": "404"}, "out": ""},
              {"line": 9, "vars": {"status": "404"}, "out": "not found\n"},
              {"line": null, "vars": {"status": "404"}, "out": "not found\nhandled\n"}
            ]}
            ```

            Inside a function, each `case` block can `return` its result.

            `match` needs Python 3.10 or newer. On older versions the `match` line is a
            `SyntaxError`.
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

            **Rules**: check them **in this order**, the first one that matches wins:
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

            **Rules**: use the first one that applies:
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

            **Rules**: check **in this order**, the first one that matches wins:
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
