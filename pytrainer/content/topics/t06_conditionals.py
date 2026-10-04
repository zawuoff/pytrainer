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
            ## Do something only when it is true

            Until now, every line of your programs ran, from top to bottom, every time. A useful program
            makes decisions. It refuses a prompt that is too long. It warns you when the bill gets high.
            For that, Python needs a way to run some lines only some of the time.

            ```python
            cost = 12
            if cost > 10:
                print("over budget")
            print("checked")
            # over budget
            # checked
            ```

            Read `if cost > 10:` as a question. When the answer is `True`, Python runs the indented line
            under it. When the answer is `False`, Python skips that line. The last line is not indented,
            so it runs either way.

            The question after `if` is called the **condition**. It is a comparison like the ones in the
            last chapter, or anything else that gives `True` or `False`. The indented lines are the `if`
            **block**, and programmers also call them a **branch**. The shape is the same as for `def`: a
            line that ends with a colon, and under it a block indented by 4 spaces.

            ```try
            cost = 12
            if cost > 10:
                print("over budget")
            print("checked")
            ---
            Change the first line so that the program prints only `checked`.
            ---
            cost = 8
            if cost > 10:
                print("over budget")
            print("checked")
            ---
            With a cost of 10 or less the condition is `False`, so Python skips the indented line. The last line is outside the block and runs every time.
            ```

            ### An if inside a function

            Decisions get more useful inside a function, together with `return`:

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

            A `return` ends the call at once. So the line `return "ok"` is only reached when the
            condition was `False`. Press Next and follow both calls:

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

            ```quiz
            What does `check(10)` hand back?
            - [x] `"ok"` :: Right. `10 > 10` is `False`, because `>` means "more than" and does not include the limit itself. Python skips the block and reaches the last line.
            - [ ] `"over budget"` :: That needs a cost above 10. For the limit itself to count, the condition would have to use `>=`.
            - [ ] `None` :: `None` comes back only when a call reaches the end without a `return`. Here the last line of the function is a `return`.
            ```

            **Watch out:** the `if` line ends with a colon. Without it, Python stops with
            `SyntaxError: expected ':'`.

            **In short:** `if condition:` runs its indented block only when the condition is `True`, and
            Python then carries on with the lines after the block.
        ''',
        "prompt": r'''
            An AI model refuses a prompt that is too long, so your app checks the length first and reports
            what it found.

            **Your job:** finish `check_length(tokens)`. It is written except for one gap, marked `___`.
            The gap is the condition of the `if`.

            **What goes in**
            - `tokens`: the length of the prompt in tokens, a whole number, for example `5000`

            **What comes out**
            - the string `"too long"` or the string `"ok"`

            **Rules**
            - More than `4000` tokens is too long.
            - Everything else is ok. Exactly `4000` tokens is still ok.

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
            "The gap is a condition: a comparison that is `True` only when the prompt is too long.",
            "Compare `tokens` with the limit from the task. \"More than\" does not include the limit itself.",
            "Write the parameter, then the operator for \"greater than\", then the limit. Do not use the operator that also accepts equal values.",
        ],
    },
    {
        "id": "conditionals-s3",
        "title": "Fix: compare, don't assign",
        "difficulty": 0,
        "lesson": r'''
            ## One equals sign stores, two compare

            In a chat, the message with the role `system` holds the instructions for the model. To treat
            it differently, your code has to ask: is this role equal to `"system"`? The natural thing to
            type is `if role = "system":`, and Python refuses to run it.

            The reason is that `=` already has a job. It stores a value under a name. A question needs a
            sign of its own, and that sign is `==`:

            ```python
            role = "user"
            print(role == "system")
            # False
            print(role == "user")
            # True
            print(role != "system")
            # True
            ```

            `==` is called the **equality operator**. It compares two values and gives a bool, and it
            changes nothing. `=` is the **assignment operator**. `!=` asks the opposite question: are the
            two values different?

            ```match
            `role = "user"` :: stores the string under the name `role`
            `role == "user"` :: asks whether `role` is equal to `"user"`
            `role != "user"` :: asks whether `role` is different from `"user"`
            ```

            When you do type one `=` in a condition, Python's message is unusually helpful:

            ```text
            SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
            ```

            It even suggests `==`. (The other sign it mentions, `:=`, is one you do not need yet.) Because
            this is a syntax error, Python finds it before it runs anything, so not one line of the file
            runs.

            Strings are compared exactly, character by character, and a capital letter is a different
            character from its small letter:

            ```predict
            role = "User"
            print(role == "user")
            print(role.lower() == "user")
            print(role != "user")
            ---
            `"User"` and `"user"` differ in their first character, so the first line is `False` and the third is `True`. `role.lower()` hands back `"user"`, which is equal to `"user"`, so the second line is `True`.
            ```

            **Watch out:** `=` inside a condition is always this mistake. When the error message asks
            "Maybe you meant '=='?", the answer is yes.

            **In short:** `=` stores a value under a name, and `==` asks whether two values are equal.
        ''',
        "prompt": r'''
            In a chat with an AI model every message has a role. The message with the role `"system"`
            holds the instructions for the model. This function should say whether a role is the system
            role, but Check fails with a `SyntaxError` before any of the code runs.

            **Your job:** find the bug in `is_system(role)` and fix it. The code is already in the editor.

            **What goes in**
            - `role`: the role of a message, a string, for example `"user"`

            **What comes out**
            - a bool: `True` when `role` is exactly `"system"`, and `False` otherwise

            **Rules**
            - Only the lowercase word `"system"` gives `True`.
            - Every other role gives `False`. That includes `"System"` with a capital S.
            - The result is the bool `True` or `False`, not the text `"True"`.

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
            "Read the error message. It names the line, and it even suggests what you may have meant.",
            "A single `=` stores a value. The `if` line needs the operator that compares two values.",
            "On the `if` line, replace the sign that stores with the sign that compares. Nothing else has to change.",
        ],
    },
    {
        "id": "conditionals-s4",
        "title": "Pass or fail",
        "difficulty": 0,
        "lesson": r'''
            ## One way or the other

            An `if` on its own either does something or does nothing. Often you want one thing or
            another: fast or slow, pass or fail. For the second half, add `else:`.

            ```python
            latency = 3.2
            if latency <= 2:
                print("fast")
            else:
                print("slow")
            # slow
            ```

            (Latency is the time an answer takes, here in seconds.) The `else:` line has no condition of
            its own. Its block runs whenever the condition of the `if` was `False`. So exactly one of the
            two blocks runs, never both and never neither.

            ```fill
            stock = 0
            if stock > 0:
                print("available")
            ___
                print("sold out")
            ---
            - [x] else: :: Right. `stock > 0` is `False`, so the block under `else:` runs and the program prints `sold out`.
            - [ ] else :: The colon is missing. Like `if`, an `else` line ends with a colon, and without it Python stops with a `SyntaxError`.
            - [ ] else stock == 0: :: An `else` never has a condition. It takes every case that the `if` did not, so Python stops with a `SyntaxError`.
            ```

            ### Inside a function you can leave else out

            A `return` ends the call. So the line after the `if` block is only reached when the condition
            was `False`, and that makes it the "else" without the word:

            ```python
            def speed(latency):
                if latency <= 2:
                    return "fast"
                return "slow"

            print(speed(2), speed(3.2))
            # fast slow
            ```

            Look at `speed(2)`. It is `"fast"`, because `2 <= 2` is `True`. "At most" is written `<=` and
            "at least" is written `>=`, and both include the limit itself. The value at which the answer
            flips is called the **boundary**. Whenever you write a condition, try the boundary value.

            ```quiz
            A ride is free for children under 6. Which condition is right for "free"?
            - [x] `age < 6` :: Right. "Under 6" does not include 6 itself, so a child of exactly 6 pays.
            - [ ] `age <= 6` :: This also lets a 6-year-old ride free. "Under" leaves the boundary out.
            - [ ] `age > 6` :: This is `True` for everyone older than 6, which is the opposite group.
            ```

            **Watch out:** `else:` starts at the same indentation as its `if`. An `else` that is
            indented differently either stops with a `SyntaxError` or attaches to the wrong `if`.

            **In short:** `if` and `else` give two blocks of which exactly one runs, and in a function a
            `return` after the `if` block does the job of `else`.
        ''',
        "prompt": r'''
            A tool that tests AI answers gives each answer a score from 0 to 1. Such a test is called an
            eval. Your report does not need the number, only a verdict: pass or fail.

            **Your job:** write `grade(score)` so that it gives back the verdict.

            **What goes in**
            - `score`: a number from `0` to `1`, for example `0.9`

            **What comes out**
            - the string `"pass"` or the string `"fail"`

            **Rules**
            - A score of at least `0.5` is a pass. `0.5` itself passes.
            - Every lower score is a fail. That includes `0.49` and `0`.

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
            "The function has two possible results, so it needs a condition. \"At least\" includes the boundary value itself.",
            "When the score is high enough, the function hands back one word. In every other case it hands back the other word.",
            "Write an `if` that compares `score` with 0.5, using the operator for \"greater than or equal to\", and hand back the passing word inside its block. After the block, at the indentation of the `if`, hand back the failing word.",
        ],
    },
    {
        "id": "conditionals-s5",
        "title": "Small, medium, large",
        "difficulty": 0,
        "lesson": r'''
            ## More than two outcomes

            Fast, normal, slow, timed out: that is four outcomes, and `if` with `else` only gives two.
            `elif`, short for "else if", adds another question to the same decision:

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

            Python asks the questions from the top. It runs the block under the first one that is `True`
            and then skips everything else in the decision, even questions that would also be `True`.
            Here `250 < 5000` is true as well, but Python never gets to ask it. An `if` followed by
            `elif` and `else` lines is called a **conditional chain**.

            Press Next and watch which lines are skipped:

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

            ### Each question can rely on the ones before it

            Python only reaches `elif ms < 1000` when `ms < 200` was `False`. At that point `ms` is
            already known to be 200 or more, so the second question does not have to say so again.

            It also means that the order of the questions matters:

            ```predict
            ms = 50
            if ms < 1000:
                print("normal")
            elif ms < 200:
                print("fast")
            else:
                print("slow")
            ---
            The first question is already `True` for 50, so Python prints `normal` and never asks the second one. With the questions in this order, `fast` can never be printed. Ask the narrowest question first.
            ```

            ```quiz
            A chain has an `if`, two `elif` lines and an `else`. How many of its four blocks run?
            - [x] Exactly one :: Right. Python runs the block of the first condition that is `True`, or the `else` block when none is, and skips the rest.
            - [ ] One for every condition that is `True` :: Python stops asking after the first `True`. Later conditions are not even checked.
            - [ ] Possibly none :: That can happen in a chain without `else`. With an `else`, there is always a block that runs.
            ```

            **Watch out:** only the first match counts. A question that is too wide, placed too early,
            swallows the cases that were meant for the questions below it.

            **In short:** an `if` / `elif` / `else` chain asks its questions from the top and runs
            exactly one block: the first one whose condition is `True`.
        ''',
        "prompt": r'''
            Before your app processes a document it sorts it by size, because small, medium and large
            documents are handled in different ways.

            **Your job:** write `size_label(tokens)` so that it gives back the label for a document of
            that length.

            **What goes in**
            - `tokens`: the length of the document in tokens, a whole number, for example `500`

            **What comes out**
            - one of the strings `"small"`, `"medium"` and `"large"`

            **Rules**
            - Fewer than `100` tokens is `"small"`.
            - From `100` up to `999` tokens is `"medium"`. `100` itself is medium.
            - `1000` tokens or more is `"large"`. `1000` itself is large.

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
            "Three outcomes need a chain with three branches.",
            "Ask about the smallest size first. Because the first match wins, the second question does not have to repeat the lower limit.",
            "The first branch takes fewer than 100 tokens and hands back the first label. The second branch, with `elif`, takes fewer than 1000 and hands back the middle label. The last branch, with `else`, hands back the remaining label.",
        ],
    },
    {
        "id": "conditionals-s6",
        "title": "Both must be true",
        "difficulty": 0,
        "lesson": r'''
            ## Two questions in one

            Many decisions depend on two things at once. Retry a request only if the API was busy and you
            have not tried too often already. Publish an answer only if its score is high and it was not
            flagged. Three small words combine conditions:

            - `a and b` is `True` only when both sides are `True`.
            - `a or b` is `True` when at least one side is `True`.
            - `not a` turns `True` into `False`, and `False` into `True`.

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

            `and`, `or` and `not` are called **boolean operators**, or logical operators.

            ```match
            `True and False` :: `False`, because `and` needs both sides
            `True or False` :: `True`, because `or` needs only one side
            `not True` :: the opposite of `True`
            ```

            The result of a boolean operator is a bool. You can use it as the condition of an `if`, or
            hand it straight back from a function:

            ```python
            def can_publish(score, flagged):
                return score >= 0.5 and not flagged

            print(can_publish(0.9, False), can_publish(0.9, True))
            # True False
            ```

            ```predict
            tokens = 300
            cached = True
            print(tokens < 500 and cached)
            print(tokens > 500 or cached)
            print(not cached)
            ---
            `300 < 500` is `True` and `cached` is `True`, so `and` gives `True`. `300 > 500` is `False`, but `or` only needs one side, and `cached` is `True`. `not` turns `True` into `False`.
            ```

            ```quiz
            A shop gives a discount to students and to everyone over 65. A customer has `student = False` and `age = 70`. What is `student or age > 65`?
            - [x] `True` :: Right. `student` is `False`, but `70 > 65` is `True`, and `or` needs only one side.
            - [ ] `False` :: That would be the result of `and`, which needs both sides. `or` is satisfied by one.
            - [ ] An error :: Mixing a bool and a comparison is fine, because a comparison produces a bool too.
            ```

            **Watch out:** each side of `and` and `or` has to be a complete condition.
            `score >= 0.5 and < 1` is a `SyntaxError`. Write the name again: `score >= 0.5 and score < 1`.

            **In short:** `and` needs both sides to be `True`, `or` needs one, and `not` flips a bool.
        ''',
        "prompt": r'''
            When an API is busy, it answers with the status code `429`, which means "too many requests,
            try again later". Your app does try again, but only a few times.

            **Your job:** finish `should_retry(status, attempts)`. It is written except for one gap,
            marked `___`. The gap is the word that joins the two conditions.

            **What goes in**
            - `status`: the status code of the answer, a whole number, for example `429`
            - `attempts`: the number of attempts made so far, a whole number, for example `1`

            **What comes out**
            - a bool: `True` only when `status` is `429` and `attempts` is less than `3`

            **Rules**
            - Every other status gives `False`.
            - `3` or more attempts gives `False`, even when the status is `429`.

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
            "The gap joins two conditions into one.",
            "The result should be `True` only when the status check and the attempts check are both `True`. Which boolean operator needs both sides?",
            "Replace the three underscores with the boolean operator from the lesson that means \"both must be true\". It is a plain English word.",
        ],
    },
    {
        "id": "conditionals-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Reading a chain before you run it

            Before you press Run, you can work out what a program will do by reading it line by line,
            the way Python does. This helps you find bugs without changing random lines, and a chain of conditions gives you a clear place to practise.

            Two rules are all you need.

            1. In an `if` / `elif` / `else` chain, exactly one block runs: the block under the first
               condition that is `True`. When no condition is `True`, the `else` block runs.
            2. A line that is back at the indentation of the `if` comes after the chain. It runs every
               time, whichever block ran.

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

            Following execution line by line is called **tracing**.

            Trace it. `50 > 100` is `False`, so Python skips `print("big")` and runs the `else` block.
            The last line is not indented, so it runs next. `50 < 100` is `True` and `50 > 10` is `True`,
            so `and` gives `True`.

            ```quiz
            In the program above, why does the last `print` run although the `else` block has already run?
            - [x] It is not indented, so it is not part of the chain :: Right. The chain ends where the indentation goes back to the left edge. Everything after that runs in every case.
            - [ ] Because its condition is `True` :: The last line has no condition of its own. It prints the result of a comparison, whatever that result is.
            - [ ] Because `else` always runs the next two lines :: A block is exactly the lines that are indented under its line, here one line.
            ```

            Now reason the other way round. Decide which block you want, then find a value that leads to
            it:

            ```try
            tokens = 50
            if tokens > 100:
                print("big")
            elif tokens > 10:
                print("medium")
            else:
                print("small")
            ---
            Change only the first line so that the program prints `small`.
            ---
            tokens = 5
            if tokens > 100:
                print("big")
            elif tokens > 10:
                print("medium")
            else:
                print("small")
            ---
            The `else` block is reached only when both conditions are `False`, which means a value of 10 or less.
            ```

            **Watch out:** check the conditions in order and stop at the first one that is `True`. A
            later condition that is also true does not matter.

            **In short:** to trace a chain, find the first condition that is `True`, run only its block,
            and then carry on after the chain.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line.
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
            `900 > 1000` is `False`, so the first block is skipped. `900 > 500` is `True`, so `long` is
            printed, and the `else` block is skipped. The last line is not indented, so it is outside the
            chain and always runs. `900 >= 900` is `True` and `900 < 1000` is `True`, so `and` gives
            `True`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Check each condition from the top, with `tokens` standing for 900. Only one block of the chain runs.",
            "The first condition is `False` and the second is `True`. The last `print` is not part of the chain.",
            "Your first line is the text printed by the block whose condition is the first to be `True`. Your second line is `True` or `False`: ask whether 900 is at least 900 and also less than 1000.",
        ],
    },
    {
        "id": "conditionals-2",
        "hints": [
            "A comparison already produces `True` or `False`, so the function can hand it straight back.",
            "One chained comparison can say \"`t` lies between 0 and 2, with both ends included\".",
            "Write one `return` line with `t` in the middle: the lower limit, the operator that includes the limit, `t`, the same operator again, and the upper limit. No `if` is needed.",
        ],
        "title": "Temperature in range",
        "difficulty": 1,
        "lesson": r'''
            ## Between two limits

            The temperature setting of a model has to lie between 0 and 2. In maths you would write that
            with the value in the middle of two signs. Python lets you write almost the same:

            ```python
            t = 1.5
            print(0 <= t <= 2)
            # True
            t = 3
            print(0 <= t <= 2)
            # False
            ```

            `0 <= t <= 2` means `0 <= t and t <= 2`. Both comparisons have to be `True`. Two comparison
            operators in one expression are called a **chained comparison**.

            `<=` includes its limit. A range in which both ends count is called **inclusive**, and it has
            `<=` on both sides. Use `<` on a side whose limit should not count:

            ```python
            def is_small(n):
                return 0 <= n < 100

            print(is_small(5), is_small(500), is_small(100))
            # True False False
            ```

            `is_small(100)` is `False`, because `100 < 100` is `False`.

            ```quiz
            For which value of `n` is `10 < n <= 20` `True`?
            - [x] For 20, but not for 10 :: Right. `10 < n` leaves 10 out, and `n <= 20` lets 20 in.
            - [ ] For 10, but not for 20 :: It is the other way round. The side with `<` leaves its limit out, and that is the side with 10.
            - [ ] For both 10 and 20 :: That would need `<=` on both sides.
            ```

            ### A comparison is already the answer

            Notice that `is_small` has no `if`. A comparison produces `True` or `False`, and a function
            can hand that bool straight back. Writing `if ...: return True` followed by `return False`
            gives the same result in three lines.

            ```fill
            def is_teen(age):
                return ___

            print(is_teen(13), is_teen(19), is_teen(20))
            ---
            - [x] 13 <= age <= 19 :: Right. Both ends count, so 13 and 19 are teens and 20 is not. The program prints `True True False`.
            - [ ] 13 < age < 19 :: `<` on both sides leaves out 13 and 19 themselves. The program prints `False False False`.
            - [ ] 13 <= age < 19 :: The upper end is left out, so 19 does not count. The program prints `True False False`.
            ```

            **Watch out:** decide for each end whether the limit itself counts. "Between 0 and 2, both
            included" needs `<=` twice.

            **In short:** `low <= x <= high` is `True` when `x` lies between the two limits, and a
            function can return that comparison directly.
        ''',
        "prompt": r'''
            Model APIs accept a `temperature` setting only between 0 and 2. The temperature controls how
            much variety the answers have. A request with a value outside that range is refused, so your
            app checks the value before it sends anything.

            **Your job:** write `valid_temperature(t)` so that it says whether the value is allowed.

            **What goes in**
            - `t`: the temperature, a whole number or a float, for example `0.7`

            **What comes out**
            - a bool: `True` when `t` is between `0` and `2`, and `False` otherwise

            **Rules**
            - Both ends are included: `0` and `2` are allowed.
            - Use a chained comparison, which means two comparison operators in one expression. A check
              looks for it.

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
        "hints": [
            "Each row of the table is one branch of an `if` / `elif` / `else` chain.",
            "Test each known reason in turn and hand back its label. Two different reasons share one label, and everything else, `None` included, ends in the last branch.",
            "Write five branches in the order of the table. Four of them compare `reason` with one string. The branch for the two tool reasons asks whether `reason` is one of them, with `in` and a tuple. The `else` branch hands back the label for everything else.",
        ],
        "title": "Classify finish_reason",
        "difficulty": 1,
        "lesson": r'''
            ## Several values, one answer

            When a model stops writing, it gives a reason. Two of the possible reasons, `"tool_calls"` and
            the older `"function_call"`, mean the same thing to your app. Two branches that do the same
            thing would be clumsy. One question that covers both values is better.

            You met `in` with sets. It works with a tuple as well:

            ```python
            reason = "function_call"
            print(reason in ("tool_calls", "function_call"))
            # True
            print("stop" in ("tool_calls", "function_call"))
            # False
            ```

            `value in (a, b)` is `True` when the value is equal to one of the items. `in` is called the
            **membership operator**.

            Inside a chain, each branch can take one value with `==`, or a group of values with `in`. The
            `else` branch takes everything that is left. That includes `None`, and text with different
            capital letters, because `==` and `in` compare strings exactly.

            ```python
            def label(role):
                if role == "user":
                    return "person"
                elif role in ("assistant", "model"):
                    return "AI"
                else:
                    return "unrecognised"

            print(label("model"), label(None), label("User"))
            # AI unrecognised unrecognised
            ```

            ```predict
            def kind(ext):
                if ext in ("jpg", "png"):
                    return "image"
                elif ext == "txt":
                    return "text"
                else:
                    return "other"

            print(kind("png"), kind("txt"), kind("PNG"))
            ---
            `"png"` is one of the two items in the tuple, so the first call gives `image`. `"txt"` matches the second branch. `"PNG"` in capitals is a different string from `"png"`, so no branch matches and the `else` gives `other`.
            ```

            ### A tempting line that does not work

            ```quiz
            Someone writes `if reason == "length" or "stop":` to catch two reasons. For which values of `reason` does the block run?
            - [x] For every value :: Right. Python reads it as `(reason == "length") or "stop"`. The right side is a string that is not empty, so it is truthy, and the whole condition always counts as true.
            - [ ] Only for `"length"` and `"stop"` :: That is what the author wanted. It needs `reason in ("length", "stop")`.
            - [ ] Only for `"length"` :: The left side is true only for `"length"`, but the right side is a truthy string, and `or` needs only one side.
            ```

            **Watch out:** `x == "a" or "b"` does not ask whether `x` is one of the two. Write
            `x in ("a", "b")`.

            **In short:** `value in (a, b, c)` asks whether the value is one of several, and the `else`
            of a chain takes everything that is left.
        ''',
        "prompt": r'''
            When a model finishes its answer, the API tells you why it stopped, in a short string called
            the `finish_reason`. Your logs should show a label that a person can read instead.

            **Your job:** write `explain_finish(reason)` so that it translates the reason into its label.

            **What goes in**
            - `reason`: the finish reason, usually a string such as `"stop"`. It can also be `None`.

            **What comes out**
            - one of the strings `"complete"`, `"truncated"`, `"needs tool"`, `"blocked"` and `"unknown"`

            **Rules**

            | `reason` | label |
            | --- | --- |
            | `"stop"` | `"complete"` |
            | `"length"` | `"truncated"` |
            | `"tool_calls"` or `"function_call"` | `"needs tool"` |
            | `"content_filter"` | `"blocked"` |
            | anything else | `"unknown"` |

            - The match is exact: `"STOP"` in capitals is `"unknown"`.
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
            ## When a value might be missing

            Every document in your app should show a title. Some arrive without one: the title is
            `None`, or an empty string, or a string of nothing but spaces. This step collects three small
            tools for that situation.

            ### A condition does not have to be a comparison

            `if name:` tests the truthiness of `name`, which you know from the last chapter. An empty
            string, `0` and `None` are falsy. A string with at least one character is truthy.

            ```python
            name = ""
            if name:
                print("hi", name)
            else:
                print("no name")
            # no name
            ```

            ### or hands back one of its two values

            So far `or` gave you `True` or `False`. In fact it does something more useful. `a or b` hands
            back `a` when `a` is truthy, and otherwise it hands back `b`:

            ```python
            print("draft" or "Untitled")
            # draft
            print(None or "Untitled")
            # Untitled
            ```

            A value that is used when the real one is missing is called a **fallback**, or a **default**.

            ```predict
            print("" or "empty")
            print("Ada" or "nobody")
            print(0 or 5)
            ---
            The empty string is falsy, so `or` hands back the right side, `empty`. `"Ada"` is truthy, so it is handed back and the right side is ignored. `0` is falsy, so the result is 5.
            ```

            ### Cleaning a value that may be None

            `None` is not a string, so it has no `.strip()` method. `None.strip()` stops the program with
            `AttributeError: 'NoneType' object has no attribute 'strip'`. The fallback trick solves that.
            `(note or "")` is the empty string when `note` is `None`, and an empty string can be
            stripped:

            ```python
            note = None
            note = (note or "").strip()
            print(note == "")
            # True
            ```

            After that line `note` is always a string, with no spaces or newlines at its ends. A plain
            `if note:` then tells you whether any characters are left.

            ```quiz
            `count` is `0`, and 0 is a perfectly good count. What does `count or 10` give?
            - [x] `10` :: Right, and that is the danger. `0` is falsy, so `or` throws it away and hands back the fallback, although 0 was a real value.
            - [ ] `0` :: `or` only hands back its left side when that side is truthy, and `0` is falsy.
            - [ ] `True` :: `or` hands back one of its two values. It does not turn them into a bool.
            ```

            **Watch out:** when `0` is a valid value, do not test truthiness. Ask `is None` or
            `is not None` instead.

            **In short:** `value or fallback` gives the fallback when the value is empty or `None`, and
            `if value:` asks whether there is anything in it.
        ''',
        "prompt": r'''
            The documents in the search index of your RAG app should always show a title. Some arrive
            with no title at all (`None`), some with an empty one, and some with a title that is nothing
            but spaces.

            **Your job:** write `clean_title(title)` so that it gives back a title that can be shown.

            **What goes in**
            - `title`: a string such as `"  Intro to RAG "`, or `None`

            **What comes out**
            - a string: the title without spaces and newlines at both ends, or `"Untitled"` when nothing
              is left

            **Rules**
            - `None`, `""` and text that is only spaces or newlines, such as `"   "` or `"\n"`, all give
              `"Untitled"`.
            - Spaces in the middle of a title stay.

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
            "`None` cannot be stripped, so first turn a possible `None` into an empty string. An empty string is falsy.",
            "Replace `None` by an empty string with `or`, strip the result, and hand it back when anything is left. Otherwise hand back the fallback.",
            "The body has three steps. Store the cleaned title under a name: the parameter or an empty string, in parentheses, with the trimming method called on it. When that name is truthy, hand it back. After the `if`, hand back the fallback text from the task.",
        ],
    },
    {
        "id": "conditionals-8",
        "title": "1 token, 2 tokens",
        "difficulty": 1,
        "lesson": r'''
            ## Choosing a value in one line

            A usage line should read `1 token` but `2 tokens`. That is a tiny choice between two words,
            and a four-line `if` and `else` feels heavy for it. Python has a compact form for exactly
            this:

            ```python
            score = 0.8
            verdict = "pass" if score >= 0.5 else "fail"
            print(verdict)
            # pass
            ```

            Read it aloud: "pass, if the score is at least 0.5, else fail". The order is: the value for
            `True`, then `if` and the condition, then `else` and the value for `False`.

            This form is called a **conditional expression**. Other languages call it the **ternary
            operator**, because it has three parts. The important word is expression. An `if` statement
            runs a block. A conditional expression produces a value, so you can assign it, return it, or
            join it to a string.

            ```fill
            stock = 0
            label = ___
            print(label)
            ---
            - [x] "in stock" if stock > 0 else "sold out" :: Right. `stock > 0` is `False`, so the value after `else` is chosen and the program prints `sold out`.
            - [ ] "sold out" if stock > 0 else "in stock" :: The two values are the wrong way round. The value before `if` is the one for `True`, so this prints `in stock`.
            - [ ] if stock > 0 "in stock" else "sold out" :: The value for `True` comes first, before the `if`. In this order Python stops with a `SyntaxError`.
            ```

            ```quiz
            What does `"even" if 7 % 2 == 0 else "odd"` give?
            - [x] `"odd"` :: Right. `7 % 2` is 1, so the condition is `False` and the value after `else` is chosen.
            - [ ] `"even"` :: That is the value for `True`. The remainder of 7 divided by 2 is 1, not 0.
            - [ ] `False` :: The expression hands back one of its two values. The bool only decides which one.
            ```

            ### Parentheses when you join

            When a conditional expression is joined to something else, put it in parentheses:

            ```python
            n = 3
            print(str(n) + (" item" if n == 1 else " items"))
            # 3 items
            print(str(n) + " item" if n == 1 else " items")
            #  items
            ```

            Without the parentheses, Python reads the second line as
            `(str(n) + " item") if n == 1 else " items"`. So when `n` is not 1, the number is lost.

            **Watch out:** a conditional expression is for a short choice between two values. For
            anything longer, an ordinary `if` statement is easier to read.

            **In short:** `a if condition else b` is the value `a` when the condition is `True`, and the
            value `b` when it is `False`.
        ''',
        "prompt": r'''
            A line that reports usage should read naturally: `1 token`, but `2 tokens` and `0 tokens`.

            **Your job:** write `token_label(n)` so that it gives back the count followed by the right
            word.

            **What goes in**
            - `n`: a number of tokens, a whole number, for example `5`

            **What comes out**
            - a string: the number, a space, and then `token` when `n` is exactly `1`, or `tokens` for
              every other number: `"5 tokens"` for the example value

            **Rules**
            - Pick the word with a conditional expression, the one-line form `a if condition else b`. A
              check looks for it.
            - `0` takes the plural: `"0 tokens"`.

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
            "A conditional expression picks between two values in one line: the value for `True`, then `if` and the condition, then `else` and the value for `False`.",
            "Pick the word with a conditional expression that asks whether `n` is equal to 1. Then join the number as text, a space and the word.",
            "First store the word under a name: the singular if `n` equals 1, else the plural. Then hand back three pieces joined with `+`: the number turned into a string, a string with one space, and the word.",
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
            ## One value, many cases

            A chain such as `if status == 200 ... elif status == 404 ...` repeats the same name on every
            line. When all the questions are about one value, the `match` statement is tidier:

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

            - `match status:` names the value that is being looked at.
            - Each `case` line is one possibility, and it has its own indented block. What stands after
              `case` is called a **pattern**.
            - Python tries the cases from top to bottom and runs only the block of the first pattern
              that matches.
            - `|` inside a pattern means "or", so `404 | 410` matches either number.
            - `_` matches anything. It is called the **wildcard**, and `case _:` goes last, where it
              does the job of `else`.

            Press Next to see which `case` lines Python tries:

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

            ```quiz
            In the program above, what is printed when `status` is `500`?
            - [x] `something else` and then `handled` :: Right. 500 matches neither 200 nor `404 | 410`, so the wildcard case takes it. The last line is outside the `match` and always runs.
            - [ ] Only `handled` :: That would happen without the `case _:` line. With it, there is a case for every value.
            - [ ] Nothing, because of an error :: A value that matches no earlier case is not an error. It falls through to the wildcard.
            ```

            Put a `match` statement together yourself:

            ```order
            color = "red"
            match color:
                case "red" | "orange":
                    print("warm")
                case _:
                    print("other")
            ---
            The value has to exist before `match` looks at it. Each `case` line is followed by its own block, and the wildcard case comes last. The program prints `warm`.
            ```

            Inside a function, each `case` block can hand back its result with `return`.

            **Watch out:** the indentation has two levels. The `case` lines are indented under `match`,
            and each block is indented under its `case`.

            **In short:** `match value:` compares one value with the pattern of each `case`, from the
            top, and `case _:` takes whatever is left.
        ''',
        "prompt": r'''
            A chat app sorts every message by its role, because instructions, chat messages and results
            from tools are shown in different ways.

            **Your job:** write `role_kind(role)` so that it gives back the kind of a message with that
            role.

            **What goes in**
            - `role`: the role of a message, usually a string such as `"user"`. It can be anything,
              `None` included.

            **What comes out**
            - one of the strings `"instructions"`, `"chat"`, `"tool result"` and `"unknown"`

            **Rules**
            - Use a `match` statement. A check looks for it.

            | `role` | kind |
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
            "Start with `match role:`, and give each row of the table a `case` of its own.",
            "One case takes the system role. One case takes two roles at once, joined with `|`. One takes the tool role, and a wildcard case comes last.",
            "Under `match role:`, write four `case` lines in the order of the table, each with a block that hands back the kind for that row. The second pattern is two strings with `|` between them, and the last pattern is `_`.",
        ],
    },
    {
        "id": "conditionals-3",
        "hints": [
            "The rules are checked in a fixed order, and the first one that matches decides. A `return` inside an `if` ends the function, which gives you exactly that behaviour.",
            "Write one `if` for each rule, in the order of the task, and let each hand back its model name. Rule 3 needs two conditions joined with `and`. The last line of the function is the \"everything else\".",
            "Five steps, top to bottom: more than 128000 tokens gives the reject string. A request that needs vision gives the vision string. Budget mode together with at most 8000 tokens gives the mini string. More than 32000 tokens gives the long-context string. A final line outside every `if` gives the standard string.",
        ],
        "title": "Route to a model tier",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            An AI app often has several models to choose from: a cheap small one, a standard one, one
            that can read very long prompts, and one that can look at images. A router decides which of
            them handles each request.

            **Your job:** write `pick_model(prompt_tokens, needs_vision=False, budget_mode=False)` so
            that it gives back the name of the right model tier.

            The `=False` in the `def` line is a default value, as in the signature of `round`. A call may
            leave that argument out, or give it by name, as in `pick_model(500, budget_mode=True)`.

            **What goes in**
            - `prompt_tokens`: the length of the prompt in tokens, a whole number, for example `500`
            - `needs_vision`: `True` when the request contains images. When it is left out it is `False`.
            - `budget_mode`: `True` when the user wants the cheapest option. When it is left out it is
              `False`.

            **What comes out**
            - one of the strings `"reject"`, `"vision-large"`, `"mini"`, `"long-context"` and `"standard"`

            **Rules**

            Check the rules in this order. The first rule that matches decides the result.

            1. More than `128000` prompt tokens gives `"reject"`, whatever the other two arguments are.
            2. `needs_vision` gives `"vision-large"`, even in budget mode.
            3. `budget_mode` together with `8000` prompt tokens or fewer gives `"mini"`.
            4. More than `32000` prompt tokens gives `"long-context"`.
            5. Everything else gives `"standard"`.

            The boundaries: `8000` can be mini and `8001` cannot. `32000` is standard and `32001` is
            long-context. `128000` is long-context and `128001` is rejected.

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
            A chat screen shows a name next to each message. The app has up to three sources for that
            name: a nickname, a full name and a numeric user id. Any of them can be missing, so the app
            takes the best one that is there.

            **Your job:** write `display_name(nickname, full_name, user_id)` so that it gives back the
            name to show.

            **What goes in**
            - `nickname`: a string such as `" ada "`, or `None`
            - `full_name`: a string such as `"Ada Lovelace"`, or `None`
            - `user_id`: a whole number such as `42`, or `None`

            **What comes out**
            - a string, chosen by the first of these rules that applies

            **Rules**
            1. When `nickname` has real characters, the result is the nickname without the spaces and
               newlines at its ends.
            2. Otherwise, when `full_name` has real characters, the result is the full name without the
               spaces and newlines at its ends.
            3. Otherwise, when `user_id` is not `None`, the result is `user-` followed by the id, for
               example `"user-42"`. The id `0` is a real id and gives `"user-0"`.
            4. Otherwise the result is `"Anonymous"`.

            `None`, `""` and text that is only spaces or newlines, such as `"   "` or `" \n"`, have no
            real characters.

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
            "`None` has no `.strip()`, so turn a possible `None` into an empty string first. An empty string is falsy. For the id, 0 is falsy but valid, so truthiness is the wrong test there.",
            "Go through the three sources in order, with an early `return` for each: clean the nickname and hand it back when anything is left, do the same for the full name, then look at the id, and end with the fallback.",
            "For each of the two names: replace `None` by an empty string with `or`, strip the result, and hand it back when it is truthy. Then, when the id is not `None`, hand back the text `user-` joined to the id as a string. The last line hands back the fallback name from rule 4.",
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
            Chat messages reach your code as tuples of different shapes: a role and a text, or, when the
            assistant wants to use a tool, three items. Your logs need one readable line for each
            message, and anything with an unexpected shape should be marked as invalid.

            **Your job:** write `summarize(message)` so that it gives back that line. Use a `match`
            statement whose patterns have the shapes of the tuples.

            **What goes in**
            - `message`: usually a tuple such as `("user", "hi")` or `("assistant", "tool", "search")`.
              It can be anything: a string, `None`, or a tuple of the wrong length.

            **What comes out**
            - a string, chosen by this table

            | `message` | result |
            | --- | --- |
            | `("system", text)`, where `text` is a `str` | `"system: "` followed by the text |
            | `("user", text)`, where `text` is a `str` that is not empty | `"user: "` followed by the text |
            | `("assistant", "tool", name)`, where `name` is a `str` | `"assistant calls "` followed by the name |
            | `("assistant", text)`, where `text` is a `str` | `"assistant: "` followed by the text |
            | anything else | `"invalid"` |

            **Rules**
            - A `match` statement is required. A check looks for it.
            - "Anything else" covers: unknown roles such as `"tool"`, the wrong number of items
              (`("user",)` or `("system", "a", "b")`), an empty user text, a text that is not a string
              (`("user", 42)` or `("assistant", 5)`), and values that are not tuples (`"hello"` or `None`).

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
            "`match` can compare a tuple with patterns that are shaped like a tuple. Inside a pattern, `str(text)` matches only a string and gives it the name `text`. A case can also carry an extra condition, called a guard: `case pattern if condition:`.",
            "Write one `case` for each row of the table, with a pattern shaped like the tuple in that row. The \"not empty\" rule needs a guard. A last `case _` takes everything else.",
            "Five cases, in the order of the table: the system pair, the user pair with a guard that tests the text, the assistant triple with `\"tool\"` in the middle, the assistant pair, and the wildcard. Build each result by joining the fixed text and the captured name with `+`.",
        ],
    },
    {
        "id": "conditionals-6",
        "title": "Rate limit status",
        "difficulty": 3,
        "prompt": r'''
            An API allows only a certain number of requests in a period of time. That number is its rate
            limit. A dashboard shows how much of the limit is used: fine, close to the limit, or blocked.
            The two numbers come from different places, so each may be a number, text that holds a
            number, or missing.

            **Your job:** write `rate_status(used, limit)` so that it gives back the status line for the
            dashboard.

            **What goes in**
            - `used`: the requests used so far: a whole number, numeric text such as `" 85 "`, or `None`
            - `limit`: the highest number allowed: a whole number, numeric text such as `"100\n"`, or
              `None`

            **What comes out**
            - a string in exactly one of the formats below

            **Rules**

            Check the rules in this order. The first rule that matches decides the result.

            1. When either argument is `None`, the result is `"ERROR: missing value"`, even when the other
               argument is `0`.
            2. Numeric text is converted to a whole number. Spaces and newlines around it are allowed.
            3. When `limit` is `0` or negative, the result is `"ERROR: limit must be positive"`.
            4. When `used` is equal to `limit` or more, the result is `"BLOCKED"`.
            5. When `used` is at least 80% of `limit`, the result is `"WARN <p>%"`. Here `<p>` is the
               whole percent, `used * 100 / limit` rounded down. For example, 5 of 6 is 83.33..., which
               gives `"WARN 83%"`. Exactly 80% counts (4 of 5, or 56 of 70), and a tiny float error must
               not make it slip through.
            6. In every other case the result is `"OK <remaining> left"`, where `<remaining>` is `limit`
               minus `used`.

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
            "Use early returns in the order of the rules. `int()` accepts whole numbers as well as numeric text, and it ignores spaces around the digits. `//` divides and rounds down.",
            "Test for `None` before you convert anything. After converting, go through the rules from top to bottom. To test \"at least 80%\" without floats, multiply instead of dividing: compare 100 times the used count with 80 times the limit.",
            "Six steps: when either value is `None`, give the missing-value error. Convert both values with `int()`. A limit of 0 or less gives the other error. A used count at or above the limit gives the blocked text. Then the 80% test with whole numbers gives `WARN`, a space, the percent from floor division as text, and `%`. In every other case give `OK`, the remaining count as text, and `left`.",
        ],
    },
]
