TOPIC = {
    "id": "variables",
    "title": "Variables & Assignment",
    "track": "foundations",
    "order": 1,
    "requires": ["basics"],
    "summary": """
        Naming values, reassigning them, swapping, augmented assignment and
        multiple and nested unpacking, and building new tuples instead of changing old ones.
    """,
    "concepts": ["assignment", "reassignment", "augmented assignment", "tuple unpacking",
                 "swapping", "constants", "naming conventions"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["variable", "name", "assignment", "assign", "equals", "reassign", "+=",
                 "augmented", "swap", "tuple", "unpack", "unpacking", "constant", "keyword",
                 "local variable", "valueerror"],
    "cards": [
        {
            "syntax": "name = value",
            "explain": "Works out the right side, then makes the name refer to the result. A second assignment replaces it.",
            "example": r'''
                tokens = 100
                tokens = tokens + 50
                print(tokens)
                # 150
            ''',
        },
        {
            "syntax": "name += value",
            "explain": "Same result as name = name + value. The operators -=, *= and /= work the same way.",
            "example": r'''
                used = 100
                used += 5
                print(used)
                # 105
                used -= 55
                print(used)
                # 50
            ''',
        },
        {
            "syntax": "a, b = b, a",
            "explain": "Assigns several names in one statement. The whole right side is built first, so this swaps a and b.",
            "example": r'''
                a, b = "x", "y"
                a, b = b, a
                print(a, b)
                # y x
            ''',
        },
        {
            "syntax": "return a, b",
            "explain": "Returns one tuple that groups the values in order. Python prints a tuple inside parentheses.",
            "example": r'''
                def limits():
                    return 128000, 16000

                print(limits())
                # (128000, 16000)
            ''',
        },
        {
            "syntax": "first, second = pair",
            "explain": "Unpacking: assigns each item of a tuple to its own name. It needs exactly one name per item.",
            "example": r'''
                record = ("openai", "gpt-4o")
                provider, model = record
                print(model)
                # gpt-4o
                route = ("openai", ("gpt-4o", 128000))
                provider, (model, context) = route
                print(context)
                # 128000
            ''',
        },
        {
            "syntax": "MAX_RETRIES = 3",
            "explain": "A constant: a name in capital letters, assigned once at the top of the file and never reassigned.",
            "example": r'''
                MAX_RETRIES = 3
                retry_count = 1
                print(MAX_RETRIES - retry_count)
                # 2
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Variables & Assignment

### Assignment

A **variable** is a name that refers to a value. An **assignment** statement
`name = value` creates the name. Python evaluates the right side first: it works out its
value. Then it makes the name on the left refer to the result.

```python
max_tokens = 256
remaining = max_tokens - 56
print(remaining)
# 200
```

A single `=` assigns. A double `==` compares two values, and a later topic covers it.

### Reassignment

**Reassignment** is an assignment to a name that already exists. The name then refers to
the new value and no longer refers to the old one. The right side can use the name's
current value.

```python
tokens = 100
tokens = tokens + 50
print(tokens)
# 150
```

### Augmented assignment

An **operator** is a sign that does something with the values next to it, such as `+` or
`-`. **Augmented assignment** combines a calculation and an assignment in one operator. For
numbers, `tokens += 5` gives the same result as `tokens = tokens + 5`. The operators `-=`,
`*=` and `/=` subtract, multiply and divide in the same way.

```python
tokens = 150
tokens += 5
print(tokens)
# 155
tokens -= 55
print(tokens)
# 100
```

Press Step to run one line at a time and see which value `tokens` refers to after each line.

```diagram
{"type": "trace", "title": "Assignment, reassignment and augmented assignment", "code": ["tokens = 100", "tokens = tokens + 50", "print(tokens)", "tokens += 5", "print(tokens)", "tokens -= 55", "print(tokens)"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {"tokens": "100"}, "out": "", "note": "Python evaluates tokens + 50 with the current value 100."},
  {"line": 3, "vars": {"tokens": "150"}, "out": ""},
  {"line": 4, "vars": {"tokens": "150"}, "out": "150\n"},
  {"line": 5, "vars": {"tokens": "155"}, "out": "150\n"},
  {"line": 6, "vars": {"tokens": "155"}, "out": "150\n155\n"},
  {"line": 7, "vars": {"tokens": "100"}, "out": "150\n155\n"},
  {"line": null, "vars": {"tokens": "100"}, "out": "150\n155\n100\n"}
]}
```

### Multiple assignment and swapping

**Multiple assignment** assigns several names in one statement. Python matches the values
on the right to the names on the left, in order. Python builds the whole right side before
it assigns anything, so `a, b = b, a` swaps two values.

```python
provider, model = "openai", "gpt-4o"
provider, model = model, provider
print(provider, model)
# gpt-4o openai
```

### Tuples and unpacking

A **tuple** is a value that groups other values in a fixed order. You write one with
commas, usually inside parentheses. `return a, b` returns one tuple with two items.

**Unpacking** assigns each item of a tuple to its own name in one statement. The left side
needs exactly one name per item. If an item is itself a tuple, put parentheses around its
names on the left. That is **nested unpacking**.

```python
record = ("anthropic", "claude", 200000)
provider, model, context = record
print(model, context)
# claude 200000
route = ("openai", ("gpt-4o", 128000))
provider, (model, context) = route
print(provider, model, context)
# openai gpt-4o 128000
```

With the wrong number of names, Python stops with a `ValueError`, an error for a value of the
right kind with unacceptable contents. The message is
`too many values to unpack` or `not enough values to unpack`, followed by the counts.

### Names and constants

A name can contain letters, digits and `_`. It cannot start with a digit. Capital letters
matter: `Model` and `model` are two different names. A **keyword** is a word that has a
fixed meaning in Python, such as `def`, `return`, `global`, `class` and `if`. A keyword
cannot be a name.

PEP 8, the official style guide for Python code, uses `lower_snake_case` for normal names:
small letters, with `_` between words. A **constant** is a name
that you assign once at the top of a file and never reassign. Constants use
`UPPER_SNAKE_CASE`.

```python
MAX_RETRIES = 3
retry_count = 1
print(MAX_RETRIES - retry_count)
# 2
```

### Common mistakes

- `used + extra` on a line by itself calculates a result and discards it. Nothing is
  assigned without `=` or an augmented operator such as `+=`.
- A swap in two statements (`a = b`, then `b = a`) loses a value. After `a = b`, both names
  refer to the old value of `b`.
- `return "b, a"` returns one piece of text. `return b, a` returns a tuple of two values.
- A **local variable** is a variable created inside a function. It exists only while that
  function runs. Using it outside the function gives a `NameError`.
'''

EXERCISES = [
    {
        "id": "variables-s2",
        "title": "Fill in the total",
        "difficulty": 0,
        "lesson": r'''
            ## Variables and assignment

            A **variable** is a name that refers to a value. You create a variable with an
            **assignment** statement: the name, a single `=`, then the value. After that line,
            you can write the name anywhere you need the value.

            ```python
            model = "gpt-4o-mini"
            max_tokens = 256
            print(model, max_tokens)
            # gpt-4o-mini 256
            ```

            Python evaluates the right side of `=` first: it works out its value. Then it makes
            the name on the left refer to the result. So the right side can be a calculation that uses other variables.

            ```python
            context = 1000
            used = 400
            free = context - used
            print(free)
            # 600
            ```

            Here `free` is assigned the value `600`.

            Parameters are variables too. Each call makes the parameter names refer to the
            arguments of that call.

            The name always goes on the left of `=`. `150 = total` is a `SyntaxError`, because
            `150` is a value and not a name.
        ''',
        "prompt": r'''
            A request uses some prompt tokens (what you send) and some completion tokens
            (what the model writes back). You want the total.

            **Fill in the blank:** replace `___` in `total_tokens(prompt, completion)`.

            - `prompt`: the number of prompt tokens, an `int`, e.g. `120`
            - `completion`: the number of completion tokens, an `int`, e.g. `30`
            - **Returns:** an `int`: the two counts added together

            **Rules**
            - If `completion` is `0`, the result is just `prompt`.

            **Examples**
            ```python
            total_tokens(120, 30)   # returns 150
            total_tokens(50, 0)     # returns 50
            ```
        ''',
        "starter": r'''
            def total_tokens(prompt, completion):
                total = ___
                return total
        ''',
        "tests": r'''
            from solution import total_tokens

            def test_adds_prompt_and_completion_tokens():
                got = total_tokens(120, 30)
                assert got == 150, f"total_tokens(120, 30) returned {got!r}"

            def test_zero_completion_returns_prompt_count():
                got = total_tokens(50, 0)
                assert got == 50, f"total_tokens(50, 0) returned {got!r}"
        ''',
        "solution": r'''
            def total_tokens(prompt, completion):
                total = prompt + completion
                return total
        ''',
        "hints": [
            "The blank is the value that the name total should point at.",
            "You want the two parameters added together.",
            "Replace ___ with the first parameter, a plus sign, and the second parameter.",
        ],
    },
    {
        "id": "variables-s6",
        "title": "Relabel the box",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Reassignment

            **Reassignment** is an assignment to a name that already exists. After it, the name
            refers to the new value and no longer refers to the old one.

            ```python
            status = "waiting"
            print(status)
            # waiting
            status = "done"
            print(status)
            # done
            ```

            The right side can use the name's current value. Python evaluates the right side
            first, with the value the name has at that point. Then it makes the name refer to
            the result.

            ```python
            retries = 2
            retries = retries + 1
            print(retries)
            # 3
            ```

            In `retries = retries + 1`, Python reads the current value `2`, calculates `3`, and
            assigns `3` to `retries`.

            Press Step to run one line at a time and see each name's value change.

            ```diagram
            {"type": "trace", "title": "Reassigning status and retries", "code": ["status = \"waiting\"", "print(status)", "status = \"done\"", "print(status)", "retries = 2", "retries = retries + 1", "print(retries)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"status": "'waiting'"}, "out": ""},
              {"line": 3, "vars": {"status": "'waiting'"}, "out": "waiting\n"},
              {"line": 4, "vars": {"status": "'done'"}, "out": "waiting\n"},
              {"line": 5, "vars": {"status": "'done'"}, "out": "waiting\ndone\n"},
              {"line": 6, "vars": {"status": "'done'", "retries": "2"}, "out": "waiting\ndone\n"},
              {"line": 7, "vars": {"status": "'done'", "retries": "3"}, "out": "waiting\ndone\n"},
              {"line": null, "vars": {"status": "'done'", "retries": "3"}, "out": "waiting\ndone\n3\n"}
            ]}
            ```

            Lines run from top to bottom. Each `print` shows the value the name refers to when
            that line runs, not a value assigned on a later line.
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            model = "gpt-4o"
            print(model)
            model = "claude"
            print(model)
            tokens = 100
            tokens = tokens + 50
            print(tokens)
        ''',
        "solution": r'''
            gpt-4o
            claude
            150
        ''',
        "explanation": r'''
            Each `print` shows the value the name has at that line. `model` is reassigned
            between the two prints. `tokens + 50` uses the old value 100, and the result 150
            is stored back into `tokens`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Go line by line and keep track of what each name holds right now.",
            "Reassignment replaces the old value. The right side of = is worked out with the current value first.",
            "Line 1: the first model name. Line 2: the second model name. Line 3: 100 plus 50.",
        ],
    },
    {
        "id": "variables-s3",
        "title": "Fix: the lost update",
        "difficulty": 0,
        "lesson": r'''
            ## Augmented assignment

            Programs often update a variable from its own current value. **Augmented
            assignment** is a shorter way to write that update. An **operator** is a sign that
            does something with the values next to it, such as `+` or `-`. Augmented assignment
            combines a calculation and an assignment in one operator, such as `+=`.

            ```python
            used = 100
            used = used + 20   # the long form
            used += 5          # augmented assignment
            print(used)
            # 125
            ```

            For `used += 5`, Python reads the current value of `used`, adds `5`, and assigns the
            result to `used`. Other operators work the same way: `-=` subtracts, `*=` multiplies
            and `/=` divides.

            ```python
            budget = 1000
            budget -= 300
            print(budget)
            # 700
            ```

            A calculation on a line by itself does not change any variable. Python calculates
            the result and discards it. A variable only changes when the line has `=` or an
            augmented operator such as `+=`.

            ```python
            count = 10
            count + 1
            print(count)
            # 10
            ```
        ''',
        "prompt": r'''
            A usage counter adds the tokens of a new request to what was already used.

            **Fix the bug** in `add_tokens(used, extra)`: it always returns the original
            `used`. Only one line is wrong.

            - `used`: tokens used so far, an `int`, e.g. `10`
            - `extra`: tokens to add, an `int`, e.g. `5`
            - **Returns:** an `int`: `used` increased by `extra`

            **Rules**
            - If `extra` is `0`, return `used` unchanged.

            **Examples**
            ```python
            add_tokens(10, 5)   # returns 15
            add_tokens(7, 0)    # returns 7
            ```
        ''',
        "starter": r'''
            def add_tokens(used, extra):
                used + extra
                return used
        ''',
        "tests": r'''
            from solution import add_tokens

            def test_adds_extra_tokens_to_used():
                got = add_tokens(10, 5)
                assert got == 15, f"add_tokens(10, 5) returned {got!r}"

            def test_adding_zero_keeps_used():
                got = add_tokens(7, 0)
                assert got == 7, f"add_tokens(7, 0) returned {got!r}"
        ''',
        "solution": r'''
            def add_tokens(used, extra):
                used += extra
                return used
        ''',
        "hints": [
            "Calculating used + extra on its own line does not store the result anywhere.",
            "The new value has to be assigned back to the name used.",
            "Change the middle line to use augmented assignment: used, then +=, then extra.",
        ],
    },
    {
        "id": "variables-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Multiple assignment and swapping

            **Multiple assignment** assigns several names in one statement. Write the names on
            the left and the values on the right, separated by commas. The first name gets the
            first value, the second name gets the second value.

            ```python
            provider, model = "openai", "gpt-4o"
            print(provider)
            # openai
            print(model)
            # gpt-4o
            ```

            A **swap** exchanges the values of two names. Python evaluates the whole right side
            first, with the current values. Only then does it assign to the names on the left.

            ```python
            first, second = 1, 2
            first, second = second, first
            print(first, second)
            # 2 1
            ```

            A swap written as two separate statements loses a value. After `a = b`, both names
            refer to `2`, so `b = a` assigns `2` again.

            ```python
            a = 1
            b = 2
            a = b
            b = a
            print(a, b)
            # 2 2
            ```

            Press Step to compare the two-statement swap with the one-statement swap.

            ```diagram
            {"type": "trace", "title": "Swapping in two statements and in one", "code": ["a = 1", "b = 2", "a = b", "b = a", "print(a, b)", "first, second = 1, 2", "first, second = second, first", "print(first, second)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"a": "1"}, "out": ""},
              {"line": 3, "vars": {"a": "1", "b": "2"}, "out": ""},
              {"line": 4, "vars": {"a": "2", "b": "2"}, "out": "", "note": "The value 1 is no longer assigned to any name."},
              {"line": 5, "vars": {"a": "2", "b": "2"}, "out": ""},
              {"line": 6, "vars": {"a": "2", "b": "2"}, "out": "2 2\n"},
              {"line": 7, "vars": {"a": "2", "b": "2", "first": "1", "second": "2"}, "out": "2 2\n"},
              {"line": 8, "vars": {"a": "2", "b": "2", "first": "2", "second": "1"}, "out": "2 2\n"},
              {"line": null, "vars": {"a": "2", "b": "2", "first": "2", "second": "1"}, "out": "2 2\n2 1\n"}
            ]}
            ```
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            tokens = 10
            tokens = tokens + 5
            tokens += 1
            print(tokens)
            a, b = "x", "y"
            a, b = b, a
            print(a, b)
        ''',
        "solution": r'''
            16
            y x
        ''',
        "explanation": r'''
            `tokens` starts at 10. `tokens = tokens + 5` assigns 15, and `tokens += 1` assigns
            16, so the first `print` shows `16`. For `a, b = b, a`, Python first evaluates the
            right side with the current values, which gives `"y", "x"`. Then it assigns `"y"`
            to `a` and `"x"` to `b`. `print(a, b)` puts one space between the two values.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Track the value of each name on paper as you go down the lines.",
            "tokens changes three times. For the swap, the right side is worked out before anything is assigned.",
            "Line 1: 10. Line 2: 10 + 5. Line 3: add 1 more. Then a gets b's old value and b gets a's old value; print shows them with a space.",
        ],
    },
    {
        "id": "variables-s4",
        "title": "Return two values",
        "difficulty": 0,
        "lesson": r'''
            ## Returning two values

            A function can return more than one value. Write the values after `return` and
            separate them with a comma.

            ```python
            def limits():
                return 128000, 16000

            print(limits())
            # (128000, 16000)
            ```

            The function still returns one value. That value is a **tuple**: a value that groups
            other values in a fixed order. Python prints a tuple with parentheses around its
            items.

            You can also write a tuple yourself with parentheses, for example
            `("gpt-4o", 128000)`. The order is part of the tuple: the first item stays first.

            Quotes create text. `return "128000, 16000"` returns one piece of text that contains
            a comma, not a tuple of two numbers.

            ```python
            def limits_text():
                return "128000, 16000"

            print(limits_text())
            # 128000, 16000
            ```
        ''',
        "prompt": r'''
            Your app needs a default model and the size of its context window (how many
            tokens it can read).

            **Write:** `default_model()` (it takes no parameters)

            - **Returns:** **two values** together (a *tuple* of 2 items): the text
              `"gpt-4o-mini"` first, then the whole number `128000`

            **Rules**
            - The name comes first, the number second.
            - The number is a number (`128000`), not text (`"128000"`).
            - Return exactly two values, separated by a comma after `return`.

            **Examples**
            ```python
            default_model()   # returns ("gpt-4o-mini", 128000)
            ```
        ''',
        "starter": r'''
            def default_model():
                ...
        ''',
        "tests": r'''
            from solution import default_model

            def test_returns_model_name_then_context_window():
                got = default_model()
                assert got == ("gpt-4o-mini", 128000), f"default_model() returned {got!r}"

            def test_returns_a_tuple_of_two():
                got = default_model()
                assert isinstance(got, tuple) and len(got) == 2, (
                    f"default_model() returned {got!r} - return two values separated by a comma")
        ''',
        "solution": r'''
            def default_model():
                return "gpt-4o-mini", 128000
        ''',
        "hints": [
            "One return statement can hand back several values if you separate them with commas.",
            "Return the text first (in quotes), then the number (no quotes).",
            "Write return, then the model name in double quotes, a comma, then 128000.",
        ],
    },
    {
        "id": "variables-s5",
        "title": "Unpack the pair",
        "difficulty": 0,
        "lesson": r'''
            ## Unpacking a tuple

            **Unpacking** assigns each item of a tuple to its own name in one statement. It is
            also called **tuple unpacking**. Write one name per item on the left of `=` and the
            tuple on the right.

            ```python
            limits = (128000, 16000)
            context, output = limits
            print(context)
            # 128000
            print(output)
            # 16000
            ```

            Python assigns the items in order. The first name gets the first item and the second
            name gets the second item. The tuple itself does not change.

            The right side can be a function call that returns a tuple.

            ```python
            def newest_model():
                return "anthropic", "claude"

            provider, model = newest_model()
            print(model, "from", provider)
            # claude from anthropic
            ```

            The number of names must equal the number of items. With 2 items and 3 names,
            Python stops with `ValueError: not enough values to unpack (expected 3, got 2)`.
        ''',
        "prompt": r'''
            A model is often stored as a pair: who provides it, and its name.

            **Fill in the blank:** replace `___` in `model_of(record)` so the line splits
            the pair into `provider` and `model` (this is called *unpacking*).

            - `record`: a pair (tuple of 2 strings) `(provider, model)`, e.g.
              `("openai", "gpt-4o")`
            - **Returns:** a string: the second item, the model name

            **Rules**
            - Works for any provider/model pair, not just the examples.

            **Examples**
            ```python
            model_of(("openai", "gpt-4o"))       # returns "gpt-4o"
            model_of(("anthropic", "claude"))    # returns "claude"
            ```
        ''',
        "starter": r'''
            def model_of(record):
                provider, model = ___
                return model
        ''',
        "tests": r'''
            from solution import model_of

            def test_returns_model_of_openai_pair():
                got = model_of(("openai", "gpt-4o"))
                assert got == "gpt-4o", f"model_of(('openai', 'gpt-4o')) returned {got!r}"

            def test_returns_model_of_anthropic_pair():
                got = model_of(("anthropic", "claude"))
                assert got == "claude", f"model_of(('anthropic', 'claude')) returned {got!r}"
        ''',
        "solution": r'''
            def model_of(record):
                provider, model = record
                return model
        ''',
        "hints": [
            "Unpacking puts a group on the right side of = and several names on the left.",
            "The group you want to take apart is the parameter.",
            "Replace ___ with the parameter name record.",
        ],
    },
    {
        "id": "variables-1",
        "title": "Swap without a temp",
        "difficulty": 1,
        "lesson": r'''
            ## Returning values in a new order

            `a, b = b, a` swaps two values because Python builds the right side `b, a` as a tuple
            first. A function can return such a tuple directly. It does not need to reassign its
            parameters. It lists them after `return` in any order.

            ```python
            def rotate(first, second, third):
                return second, third, first

            print(rotate("primary", "backup", "spare"))
            # ('backup', 'spare', 'primary')
            ```

            A tuple can contain values of any kind: numbers, text, or both together. `rotate`
            never inspects its arguments, so it works for all of them.

            ```python
            def rotate(first, second, third):
                return second, third, first

            print(rotate("gpt-4o", 0.5, 3))
            # (0.5, 3, 'gpt-4o')
            ```

            A **temporary variable** is a name that exists only to keep a value for a few lines,
            as in `temp = a`. Returning a tuple makes one unnecessary here.

            Use commas only. `return [second, first]` with square brackets returns a different
            kind of value. A later topic covers that kind.
        ''',
        "prompt": r'''
            Sometimes two settings need to trade places, e.g. a primary and a backup model.

            **Write:** `swap(a, b)`

            - `a`: any value, e.g. `1` or `"x"`
            - `b`: any value, e.g. `2` or `0.5`
            - **Returns:** a tuple of two values: `b` first, then `a`

            **Rules**
            - Works for values of any type (numbers, text, a mix).
            - Return two values together (a tuple), not a list and not a single value.
            - Don't create any extra variable inside the function (no line like
              `temp = a`). It can be done in one line.

            **Examples**
            ```python
            swap(1, 2)        # returns (2, 1)
            swap("x", 0.5)    # returns (0.5, "x")
            ```
        ''',
        "starter": r'''
            def swap(a, b):
                ...
        ''',
        "tests": r'''
            from solution import swap

            def test_swaps_two_numbers():
                assert swap(1, 2) == (2, 1), f"swap(1, 2) returned {swap(1, 2)!r}"

            def test_swaps_text_and_number():
                got = swap("x", 0.5)
                assert got == (0.5, "x"), f"swap('x', 0.5) returned {got!r}"

            def test_returns_a_tuple():
                assert isinstance(swap(3, 4), tuple), f"swap(3, 4) returned {swap(3, 4)!r}, not a tuple"

            def test_no_temporary_variable():
                import ast
                fn = [n for n in ast.walk(ast.parse(source())) if isinstance(n, ast.FunctionDef)][0]
                names = {t.id for n in ast.walk(fn) if isinstance(n, ast.Assign)
                         for t in n.targets if isinstance(t, ast.Name)}
                assert not names, f"no temporary variables allowed (found {sorted(names)})"
        ''',
        "solution": r'''
            def swap(a, b):
                return b, a
        ''',
        "hints": [
            "Remember how a function returns two values at once (see 'Returning two values' in the lesson).",
            "You do not need to change a or b at all. Just return them in the opposite order.",
            "Write a single return line: the second parameter, a comma, then the first parameter. No quotes.",
        ],
    },
    {
        "id": "variables-2",
        "title": "Remaining budget",
        "difficulty": 1,
        "lesson": r'''
            ## Local variables

            A function can create its own variables to store a result while it works. You assign
            a starting value, update it line by line, and return it.

            ```python
            def tokens_used(start, first, second):
                used = start
                used += first
                used += second
                return used

            print(tokens_used(50, 200, 300))
            # 550
            ```

            `used` starts with the same value as `start`. Each `+=` line assigns a larger value
            to `used`. The last line returns the final value. `-=` works the same way and
            subtracts.

            A **local variable** is a variable created inside a function. It exists only while
            the function runs. Code outside the function cannot use `used`: that gives
            `NameError: name 'used' is not defined`.

            Subtraction can go below zero. Python does not stop at `0`.

            ```python
            balance = 100
            balance -= 130
            print(balance)
            # -30
            ```

            Return the name you updated (`used`), not the original parameter (`start`).
        ''',
        "prompt": r'''
            A token budget tracker: how many tokens are left after one request?

            **Write:** `remaining_budget(budget, prompt_tokens, output_tokens)`

            - `budget`: tokens available at the start, an `int`, e.g. `1000`
            - `prompt_tokens`: tokens the prompt used, an `int`, e.g. `100`
            - `output_tokens`: tokens the answer used, an `int`, e.g. `250`
            - **Returns:** an `int`: the budget minus both amounts

            **Rules**
            - Subtract each amount with **augmented assignment** `-=` (two `-=` lines:
              one for the prompt tokens, one for the output tokens). A check looks for them.
            - If the request used more than the budget, return the negative number (don't
              stop at 0).
            - If nothing was used, return the budget unchanged.

            **Examples**
            ```python
            remaining_budget(1000, 100, 250)   # returns 650
            remaining_budget(100, 80, 50)      # returns -30
            remaining_budget(500, 0, 0)        # returns 500
            ```
        ''',
        "starter": r'''
            def remaining_budget(budget, prompt_tokens, output_tokens):
                ...
        ''',
        "tests": r'''
            from solution import remaining_budget

            def test_subtracts_both_token_counts():
                got = remaining_budget(1000, 100, 250)
                assert got == 650, f"remaining_budget(1000, 100, 250) returned {got!r}"

            def test_nothing_used_keeps_budget():
                got = remaining_budget(500, 0, 0)
                assert got == 500, f"remaining_budget(500, 0, 0) returned {got!r}"

            def test_overspend_goes_negative():
                got = remaining_budget(100, 80, 50)
                assert got == -30, f"remaining_budget(100, 80, 50) returned {got!r}"

            def test_uses_minus_equals_twice():
                assert source().count("-=") >= 2, "subtract each amount with augmented assignment (-=)"
        ''',
        "solution": r'''
            def remaining_budget(budget, prompt_tokens, output_tokens):
                left = budget
                left -= prompt_tokens
                left -= output_tokens
                return left
        ''',
        "hints": [
            "Augmented assignment (-=) changes a name's value in place: x -= 5 means x = x - 5.",
            "Keep a name for what is left, reduce it twice (once per token count), then return it.",
            "1) Make a name like left point at budget. 2) left -= the prompt tokens. 3) left -= the output tokens. 4) return left.",
        ],
    },
    {
        "id": "variables-6",
        "title": "Config script",
        "difficulty": 1,
        "mode": "script",
        "lesson": r'''
            ## Constants and scripts

            Some values are settings that you choose once and never change, such as a provider
            name or a retry limit. A **constant** is a name that you assign once at the top of a
            file and never reassign.

            ```python
            PROVIDER = "openai"
            MAX_RETRIES = 3
            print(PROVIDER, MAX_RETRIES)
            # openai 3
            ```

            By convention, constants use `UPPER_SNAKE_CASE`: capital letters, with `_` between
            words. Normal names use `lower_snake_case`, such as `user_name`.

            A **script** is a file of Python code that does its work when you press Run. Here its
            lines start at the left edge, with no `def`. Python runs them from top to bottom. Assign the constants at the
            top, then use them by name below.

            ```python
            TIMEOUT_SECONDS = 1.5
            print("timeout is", TIMEOUT_SECONDS)
            # timeout is 1.5
            ```

            Python does not prevent you from reassigning a constant. The capital letters are a
            convention that tells other programmers not to change the value.

            Numbers do not take quotes. `1.5` is a number and `"1.5"` is text.
        ''',
        "prompt": r'''
            Model settings are usually kept as *constants*: names in UPPER_SNAKE_CASE that
            are set once at the top of a file.

            **Write a script** (top-level code at the left edge, no function) that defines
            three constants and prints them.

            **Rules**
            - Define exactly these names and values:
              - `MODEL` = the text `"gpt-4o-mini"`
              - `TEMPERATURE` = the number `0.2`
              - `MAX_TOKENS` = the whole number `512`
            - Then print all three on **one** line, separated by single spaces.
            - The `print` must use the three names (`MODEL`, `TEMPERATURE`, `MAX_TOKENS`),
              not text you typed out again. A check looks for this.
            - The script prints nothing else.

            **Examples**

            Running `python3 solution.py` prints:
            ```
            gpt-4o-mini 0.2 512
            ```
        ''',
        "starter": r'''
            # define the constants, then print the line
        ''',
        "tests": r'''
            def test_prints_the_three_values_on_one_line():
                r = run_script()
                assert r.returncode == 0, r.stderr
                assert r.stdout.strip() == "gpt-4o-mini 0.2 512", f"printed {r.stdout!r}"

            def test_constants_have_the_right_names_and_values():
                mod = load()
                assert getattr(mod, "MODEL", None) == "gpt-4o-mini", "MODEL is missing or wrong"
                assert getattr(mod, "TEMPERATURE", None) == 0.2, "TEMPERATURE is missing or wrong"
                assert getattr(mod, "MAX_TOKENS", None) == 512, "MAX_TOKENS is missing or wrong"

            def test_print_uses_the_constants():
                import ast
                calls = [n for n in ast.walk(ast.parse(source()))
                         if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"]
                used = {a.id for c in calls for a in c.args if isinstance(a, ast.Name)}
                assert {"MODEL", "TEMPERATURE", "MAX_TOKENS"} <= used, "print the constants by name, not typed-out text"
        ''',
        "solution": r'''
            MODEL = "gpt-4o-mini"
            TEMPERATURE = 0.2
            MAX_TOKENS = 512

            print(MODEL, TEMPERATURE, MAX_TOKENS)
        ''',
        "hints": [
            "Script mode: write lines at the left edge of the file, no def. print() with commas puts spaces between values.",
            "Create three names with =, text in quotes and numbers without. Then one print that uses the three names.",
            "1) MODEL = the text in quotes. 2) TEMPERATURE = 0.2. 3) MAX_TOKENS = 512. 4) print(MODEL, TEMPERATURE, MAX_TOKENS). Press Run to compare.",
        ],
    },
    {
        "id": "variables-8",
        "title": "Fix: a reserved name",
        "difficulty": 1,
        "research": {
            "note": 'Python reserves a small set of words for itself. Read the list of keywords, and skim the naming conventions in PEP 8, then come back.',
            "links": [
                {"title": 'Keywords - Python reference', "url": 'https://docs.python.org/3/reference/lexical_analysis.html#keywords'},
                {"title": 'PEP 8 - Naming conventions', "url": 'https://peps.python.org/pep-0008/#naming-conventions'},
            ],
        },
        "lesson": r'''
            ## Names and keywords

            An **identifier** is a valid name for a variable, a parameter or a function. A
            **keyword** is a word that has a fixed meaning in Python, such as `def`,
            `return`, `if`, `class` and `global`. Python has 35 keywords, and none of them can
            be used as a name.

            The rules for an identifier:

            - It contains only letters, digits and `_`. Spaces and hyphens are not allowed.
            - It does not start with a digit. `model_2` is valid and `2nd_model` is not.
            - Capital letters matter. `Zone` and `zone` are two different names.
            - It is not a keyword.

            ```python
            zone = "west"
            model_2 = "claude"
            print(model_2 + "/" + zone)
            # claude/west
            ```

            A keyword used as a name is a `SyntaxError`. Python finds the error before it runs
            any line, so nothing in the file runs. The message is often only `invalid syntax`,
            with a marker under the keyword. For the line `class = "large"`, Python reports:

            ```text
            SyntaxError: invalid syntax
            ```
        ''',
        "prompt": r'''
            `endpoint(model, global)` builds the id of a model deployed in one region, but
            the file doesn't even run: Check shows a `SyntaxError`. The second parameter uses
            a reserved word as its name.

            **Fix:** rename the second parameter to `region` (in the `def` line **and** where
            it is used).

            - `model`: a model name, a string, e.g. `"gpt-4o"`
            - `region`: a region code, a string, e.g. `"eu"`
            - **Returns:** a string: the model, `@`, then the region, e.g. `"gpt-4o@eu"` (no spaces)

            **Rules**
            - The parameters must be named exactly `model` and `region`, in that order (a check looks at the names).

            **Examples**
            ```python
            endpoint("gpt-4o", "eu")     # returns "gpt-4o@eu"
            endpoint("claude", "us")     # returns "claude@us"
            ```
        ''',
        "starter": r'''
            def endpoint(model, global):
                return model + "@" + global
        ''',
        "tests": r'''
            import inspect
            from solution import endpoint

            def test_joins_model_and_region_with_at_sign():
                got = endpoint("gpt-4o", "eu")
                assert got == "gpt-4o@eu", f"endpoint('gpt-4o', 'eu') returned {got!r}"
                got = endpoint("claude", "us")
                assert got == "claude@us", f"endpoint('claude', 'us') returned {got!r}"

            def test_parameters_are_named_model_and_region():
                names = list(inspect.signature(endpoint).parameters)
                assert names == ["model", "region"], f"the parameters are named {names}"
        ''',
        "solution": r'''
            def endpoint(model, region):
                return model + "@" + region
        ''',
        "hints": [
            "The error points at the word global: it is one of Python's keywords.",
            "Choose the name the task asks for and use it in both places the old name appears.",
            "Replace global with region in the def line, and again in the return line.",
        ],
    },
    {
        "id": "variables-7",
        "title": "Fix: one name per item",
        "difficulty": 1,
        "lesson": r'''
            ## Unpacking needs one name per item

            Unpacking works only when the left side has exactly one name for each item of the
            tuple. A tuple with three items needs three names.

            ```python
            window = (200000, 8000, 192000)
            context, output, free = window
            print(free)
            # 192000
            ```

            With the wrong number of names, Python stops with a `ValueError`. A `ValueError`
            means a value is the right kind of value but its contents are not acceptable. Here
            the value is a tuple, but it has the wrong number of items. Unpacking three items
            into two names gives this message:

            ```text
            ValueError: too many values to unpack (expected 2, got 3)
            ```

            Python versions before 3.14 end that message at `(expected 2)`. `too many values`
            means the tuple has more items than you wrote names. `not enough values` means it
            has fewer. Count the items, then count the names.

            An item you do not need still requires a name. Many programmers use the name `_`
            for an item they will not use.

            ```python
            window = (200000, 8000, 192000)
            context, _, _ = window
            print(context)
            # 200000
            ```
        ''',
        "prompt": r'''
            A usage record is a tuple of three counts: `(prompt_tokens, completion_tokens,
            total_tokens)`. `total_of` should return the last one, but it crashes with
            `ValueError: too many values to unpack (expected 2)`. Fix the unpacking line.

            **Fix:** `total_of(usage)`

            - `usage`: a tuple of three ints `(prompt, completion, total)`, e.g. `(120, 30, 150)`
            - **Returns:** an int: the **third** item, the total, e.g. `150`

            **Rules**
            - Keep using unpacking: take the tuple apart in **one** assignment line (a check
              looks for it).
            - Don't use square brackets / indexing like `usage[2]` (a check enforces this).

            **Examples**
            ```python
            total_of((120, 30, 150))   # returns 150
            total_of((0, 0, 0))        # returns 0
            ```
        ''',
        "starter": r'''
            def total_of(usage):
                prompt, total = usage
                return total
        ''',
        "tests": r'''
            import ast
            from solution import total_of

            def test_returns_the_third_item():
                got = total_of((120, 30, 150))
                assert got == 150, f"total_of((120, 30, 150)) returned {got!r}"

            def test_all_zero_usage_returns_zero():
                got = total_of((0, 0, 0))
                assert got == 0, f"total_of((0, 0, 0)) returned {got!r}"

            def test_unpacks_in_one_assignment():
                tree = ast.parse(source())
                ok = any(isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
                         for n in ast.walk(tree))
                assert ok, "take the tuple apart with unpacking"

            def test_does_not_use_indexing():
                assert not any(isinstance(n, ast.Subscript) for n in ast.walk(ast.parse(source()))), (
                    "no indexing - use unpacking")
        ''',
        "solution": r'''
            def total_of(usage):
                prompt, completion, total = usage
                return total
        ''',
        "hints": [
            "The error message says how many names Python expected and that there were more values than names.",
            "The tuple has three items, so the left side of the unpacking needs three names.",
            "Add a name for the middle item (e.g. completion) between prompt and total on the unpacking line.",
        ],
    },
    {
        "id": "variables-3",
        "title": "Unpack a record",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            An API returns model info as a tuple of four items. You want a short id for
            logs and the number of tokens left for the input.

            **Write:** `describe(record)`

            - `record`: a tuple `(provider, model_name, context_window, max_output)`:
              two strings then two ints, e.g. `("openai", "gpt-4o", 128000, 16000)`
            - **Returns:** **two values** (a tuple of 2):
              1. the full model id, a string: provider, a `/`, then the model name,
                 e.g. `"openai/gpt-4o"` (no spaces)
              2. the input budget, an int: `context_window` minus `max_output`

            **Rules**
            - Take the record apart into four names in **one** assignment line (this is
              called *unpacking*). A check looks for it.
            - Return exactly two values.

            **Examples**
            ```python
            describe(("openai", "gpt-4o", 128000, 16000))
            # returns ("openai/gpt-4o", 112000)
            describe(("anthropic", "claude", 200000, 8000))
            # returns ("anthropic/claude", 192000)
            ```
        ''',
        "starter": r'''
            def describe(record):
                ...
        ''',
        "tests": r'''
            from solution import describe

            def test_builds_id_and_budget_for_openai():
                got = describe(("openai", "gpt-4o", 128000, 16000))
                assert got == ("openai/gpt-4o", 112000), f"got {got!r}"

            def test_builds_id_and_budget_for_anthropic():
                got = describe(("anthropic", "claude", 200000, 8000))
                assert got == ("anthropic/claude", 192000), f"got {got!r}"

            def test_returns_exactly_two_values():
                got = describe(("a", "b", 10, 1))
                assert isinstance(got, tuple) and len(got) == 2, f"got {got!r}"

            def test_unpacks_record_in_one_assignment():
                import ast
                tree = ast.parse(source())
                ok = any(isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
                         for n in ast.walk(tree))
                assert ok, "unpack the record into separate names in one assignment"
        ''',
        "solution": r'''
            def describe(record):
                provider, model, context_window, max_output = record
                return provider + "/" + model, context_window - max_output
        ''',
        "hints": [
            "Unpacking splits a tuple into several names in one line; returning with a comma gives back two values.",
            "First unpack the record into four names. Then build the id by joining text with +, and compute the budget with -.",
            "1) Four names, comma separated, = record. 2) return: provider + the slash text + model, then a comma, then context_window - max_output.",
        ],
    },
    {
        "id": "variables-4",
        "title": "Nested unpacking",
        "difficulty": 2,
        "lesson": r'''
            ## Nested unpacking

            An item of a tuple can itself be a tuple. **Nested unpacking** takes both tuples
            apart in one assignment. Write the left side with the same structure as the value,
            and put parentheses around the names for the inner tuple.

            ```python
            call = (("search", 2), "ok")
            (tool, attempts), status = call
            print(tool, attempts, status)
            # search 2 ok
            ```

            Python assigns the inner tuple's items to `tool` and `attempts`, and `"ok"` to
            `status`. If you write `inner, status = call` instead, the left side has two names, and
            `inner` gets the whole inner tuple `("search", 2)`.
        ''',
        "prompt": r'''
            A router returns a pair whose second item is itself a pair. You want all
            three pieces side by side.

            **Write:** `flatten(route)`

            - `route`: a tuple `(provider, (model_name, context_window))`, e.g.
              `("openai", ("gpt-4o", 128000))`
            - **Returns:** a flat tuple of **three** values:
              `(provider, model_name, context_window)`

            **Rules**
            - Take `route` apart with **one** assignment whose left side has a pair inside
              a pair (this is called *nested unpacking*). A check looks for it.
            - Don't use indexing anywhere (no square brackets like `route[1]`).
            - Return exactly three values, in the order shown.

            **Examples**
            ```python
            flatten(("openai", ("gpt-4o", 128000)))
            # returns ("openai", "gpt-4o", 128000)
            flatten(("anthropic", ("claude", 200000)))
            # returns ("anthropic", "claude", 200000)
            ```
        ''',
        "starter": r'''
            def flatten(route):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import flatten

            def test_flattens_openai_route():
                got = flatten(("openai", ("gpt-4o", 128000)))
                assert got == ("openai", "gpt-4o", 128000), f"got {got!r}"

            def test_flattens_anthropic_route():
                got = flatten(("anthropic", ("claude", 200000)))
                assert got == ("anthropic", "claude", 200000), f"got {got!r}"

            def test_returns_exactly_three_values():
                got = flatten(("a", ("b", 1)))
                assert isinstance(got, tuple) and len(got) == 3, f"got {got!r}"

            def test_uses_one_nested_unpacking_assignment():
                tree = ast.parse(source())
                ok = any(isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
                         and any(isinstance(e, ast.Tuple) for e in n.targets[0].elts)
                         for n in ast.walk(tree))
                assert ok, "unpack route in one assignment whose left side has a pair inside a pair"

            def test_does_not_use_indexing():
                assert not any(isinstance(n, ast.Subscript) for n in ast.walk(ast.parse(source()))), (
                    "no indexing - use unpacking")
        ''',
        "solution": r'''
            def flatten(route):
                provider, (model, context_window) = route
                return provider, model, context_window
        ''',
        "hints": [
            "The left side of an unpacking assignment can have the same shape as the value, including parentheses for an inner pair.",
            "Mirror the shape of route on the left of =: one name, then a parenthesised pair of two names. Then return the three names.",
            "1) Write: name, (name, name) = route. 2) Return the three names separated by commas, in the order provider, model, context window.",
        ],
    },
    {
        "id": "variables-5",
        "title": "Rolling stats",
        "difficulty": 3,
        "prompt": r'''
            You track response latencies (in ms) of a model API as a **stats tuple**
            `(count, total, lowest, highest)`. Tuples cannot be changed, so each update
            builds a new one.

            **Write three functions:**

            1. `start_stats(value)`
               - `value`: the first latency, an int, e.g. `120`
               - **Returns:** the stats tuple after that one measurement:
                 count `1`, and `value` as the total, the lowest and the highest
            2. `add_value(stats, value)`
               - `stats`: a stats tuple, e.g. `(1, 120, 120, 120)`
               - `value`: one more latency, an int, e.g. `80`
               - **Returns:** a **new** stats tuple: count + 1, total + value, the smaller
                 of (lowest, value), the bigger of (highest, value)
            3. `average(stats)`
               - `stats`: a stats tuple (count is at least 1)
               - **Returns:** a float: `total / count` rounded to **2** decimals

            **Rules**
            - `add_value` must not change the tuple it was given (build and return a new one).
            - `add_value` can be called many times in a row, each time on the previous result.
            - `min()` works like `max()`. No `if` is needed.

            **Examples**
            ```python
            s = start_stats(120)     # s is (1, 120, 120, 120)
            s = add_value(s, 80)     # s is (2, 200, 80, 120)
            s = add_value(s, 301)    # s is (3, 501, 80, 301)
            average(s)               # returns 167.0
            average((3, 100, 10, 50))   # returns 33.33
            ```
        ''',
        "starter": r'''
            def start_stats(value):
                ...


            def add_value(stats, value):
                ...


            def average(stats):
                ...
        ''',
        "tests": r'''
            from solution import start_stats, add_value, average

            def test_start_stats_has_count_one():
                got = start_stats(120)
                assert got == (1, 120, 120, 120), f"start_stats(120) returned {got!r}"

            def test_adding_lower_value_updates_lowest():
                got = add_value((1, 120, 120, 120), 80)
                assert got == (2, 200, 80, 120), f"got {got!r}"

            def test_adding_higher_value_updates_highest():
                got = add_value((2, 200, 80, 120), 301)
                assert got == (3, 501, 80, 301), f"got {got!r}"

            def test_several_updates_in_a_row():
                s = start_stats(50)
                for v in (70, 10, 90):
                    s = add_value(s, v)
                assert s == (4, 220, 10, 90), f"after 50, 70, 10, 90 stats were {s!r}"

            def test_given_stats_are_unchanged():
                before = (1, 5, 5, 5)
                add_value(before, 9)
                assert before == (1, 5, 5, 5), f"the stats passed in became {before!r}"

            def test_average_rounded_to_two_decimals():
                got = average((3, 501, 80, 301))
                assert got == 167.0, f"average returned {got!r}"
                got = average((3, 100, 10, 50))
                assert got == 33.33, f"average((3, 100, ...)) returned {got!r}"
        ''',
        "solution": r'''
            def start_stats(value):
                return 1, value, value, value


            def add_value(stats, value):
                count, total, lowest, highest = stats
                return count + 1, total + value, min(lowest, value), max(highest, value)


            def average(stats):
                count, total, lowest, highest = stats
                return round(total / count, 2)
        ''',
        "hints": [
            "Unpack the stats tuple into four names, compute the new values, return them as a new tuple.",
            "After one measurement the count is 1 and the value is the total, the lowest and the highest. Each update: one more in the count, add to the total, keep the smaller lowest and the bigger highest.",
            "1) start_stats: return 1 followed by the value three times. 2) add_value: unpack stats into four names, then return a new tuple of: count plus one, total plus value, the smaller of lowest and value (min), the bigger of highest and value (max). 3) average: unpack, divide total by count, round to 2 places.",
        ],
    },
]
