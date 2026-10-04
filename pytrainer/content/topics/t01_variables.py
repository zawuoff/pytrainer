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
            ## Give a value a name

            In the last chapter every value was used on the spot, as in `print(2 + 3)`. Real programs
            need to keep a value and use it again a few lines later: the name of the model, the number
            of tokens used so far. To keep a value, you give it a name.

            ```python
            model = "gpt-4o-mini"
            max_tokens = 256
            print(model, max_tokens)
            # gpt-4o-mini 256
            ```

            Read `model = "gpt-4o-mini"` as "let `model` be the name for this text". From that line on,
            wherever you write `model`, Python uses the text. The name works like a label stuck on the
            value.

            A name with a value attached is called a **variable**, and the line that creates it is an
            **assignment**. The `=` in an assignment does not mean "is equal to", as it does in maths. It
            means "store the value on the right under the name on the left".

            ```quiz
            Which line stores the number 150 under the name `total`?
            - [x] `total = 150` :: Right. The name goes on the left and the value on the right.
            - [ ] `150 = total` :: The name must be on the left. Python stops with a `SyntaxError`, because 150 is a value and a value cannot be given a value.
            - [ ] `"total" = 150` :: With quotes, `"total"` is a string, which is a value. Only a bare name can receive a value.
            ```

            ### The right side is worked out first

            Python handles an assignment in two steps. First it works out the right side. Then it attaches
            the name on the left to the result. So the right side can be a whole calculation, and it can
            use other variables:

            ```python
            context = 1000
            used = 400
            free = context - used
            print(free)
            # 600
            ```

            ```predict
            width = 4
            height = 5
            area = width * height
            print(area)
            print(width)
            ---
            `area` gets the result of `4 * 5`, which is 20. Using `width` on the right side only reads its value, so `width` is still 4.
            ```

            The parameters of a function are variables too. Each call attaches the parameter names to the
            arguments of that call, and inside the function you can create more variables with `=`.

            **Watch out:** a name has to be assigned before it is used. A line that uses `free` before any
            line has created it stops with `NameError: name 'free' is not defined`.

            **In short:** `name = value` works out the right side, then stores the result under the name
            on the left.
        ''',
        "prompt": r'''
            Every request to an AI model uses tokens twice: once for the prompt that you send, and once
            for the completion, which is the text the model writes back. Your app wants the total for the
            request.

            **Your job:** finish `total_tokens(prompt, completion)`. The function is already written
            except for one gap, marked `___`. Replace the gap so that `total` holds the two counts added
            together.

            **What goes in**
            - `prompt`: the number of prompt tokens, a whole number, for example `120`
            - `completion`: the number of completion tokens, a whole number, for example `30`

            **What comes out**
            - the two counts added together, a whole number: `150` for the example values

            **Rules**
            - When `completion` is `0`, the result is the same as `prompt`.

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
            "The gap is the right side of an assignment: the value that the name `total` should get.",
            "The function receives two numbers through its parameters. The total is what you get when you put them together with the sign for adding.",
            "Replace the three underscores with a small calculation that uses both parameter names. Do not type fixed numbers, because the function must work for every call.",
        ],
    },
    {
        "id": "variables-s6",
        "title": "Relabel the box",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## A name can move to a new value

            A request starts as "waiting" and ends as "done". A retry counter goes from 2 to 3. Values
            change while a program runs, so a variable must be able to change with them. To change what a
            name stands for, assign to it again:

            ```python
            status = "waiting"
            print(status)
            # waiting
            status = "done"
            print(status)
            # done
            ```

            The second assignment does not create a second `status`. The same name now stands for the new
            value, and the old value is forgotten. Assigning to a name that already exists is called
            **reassignment**.

            ### Using the old value to make the new one

            The right side of a reassignment may use the name itself:

            ```python
            retries = 2
            retries = retries + 1
            print(retries)
            # 3
            ```

            In maths, `retries = retries + 1` would be nonsense. In Python it is two steps, in the order
            you already know. First the right side is worked out with the value the name has now: `2 + 1`
            is 3. Then the name gets that 3.

            Press Next and watch the Variables box change after each line:

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

            ```quiz
            What does this program print?

            ~~~python
            credits = 5
            credits = credits - 2
            credits = credits - 2
            print(credits)
            ~~~
            - [x] `1` :: Right. 5 becomes 3, and then 3 becomes 1. Each line starts from the value the name has at that moment.
            - [ ] `3` :: That is the value after the first subtraction. The third line takes 2 off once more.
            - [ ] `5` :: `print` shows the value the name has when the `print` line runs. By then the name has been reassigned twice.
            ```

            Now change a program yourself:

            ```try
            status = "waiting"
            print(status)
            ---
            Add one line between the two lines so that the program prints `sent`. Leave the first line as it is.
            ---
            status = "waiting"
            status = "sent"
            print(status)
            ---
            The reassignment replaced the value before `print` looked at it.
            ```

            **Watch out:** a `print` shows the value a name has at the moment that line runs. A
            reassignment further down the file does not reach back and change earlier output.

            **In short:** assigning to a name again replaces its value, and the right side is worked out
            first, with the value the name had before.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line.
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
            The first `print` runs while `model` stands for `gpt-4o`. Then `model` is reassigned, so the
            second `print` shows `claude`. `tokens` starts at 100. In `tokens = tokens + 50` the right side
            is worked out first with the old value, `100 + 50`, and the result 150 is stored back under
            `tokens`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Go down the program line by line, and keep a note of what each name stands for at that moment.",
            "An assignment to a name that already exists replaces its value. The right side is worked out first, with the value the name has before the line runs.",
            "The first `print` shows the first model name. The second shows the name that replaced it. For the last line of output, work out what `tokens` is after 50 has been added to its starting value.",
        ],
    },
    {
        "id": "variables-s3",
        "title": "Fix: the lost update",
        "difficulty": 0,
        "lesson": r'''
            ## A shorter way to update a variable

            Programs count things all the time: one more retry, 20 more tokens used. You know the long way
            to write that: `used = used + 20`. The pattern is so common that Python has a shorter spelling
            for it.

            ```python
            used = 100
            used += 20
            print(used)
            # 120
            ```

            `used += 20` means exactly the same as `used = used + 20`: take the current value, add 20, and
            store the result back under the same name.

            Signs such as `+` and `-` are called **operators**. `+=` joins an operator to the `=`, and the
            combination is called **augmented assignment**. There is one for every arithmetic operator,
            including `/`, which divides:

            ```python
            budget = 1000
            budget -= 300
            print(budget)
            # 700
            budget *= 2
            print(budget)
            # 1400
            ```

            ```predict
            count = 10
            count += 5
            count -= 3
            count *= 2
            print(count)
            ---
            `10 + 5` is 15, `15 - 3` is 12, and `12 * 2` is 24. Each line starts from the value that the line before left behind.
            ```

            ### A calculation alone changes nothing

            Here is a line that looks as if it should work:

            ```python
            count = 10
            count + 1
            print(count)
            # 10
            ```

            Python did work out `10 + 1`. Then it threw the 11 away, because the line does not say where
            to store it. A variable changes only when a line assigns to it, with `=` or with an augmented
            assignment such as `+=`.

            ```quiz
            `points` is 7. Which line makes it 8?
            - [x] `points += 1` :: Right. It adds 1 to the current value and stores the result back under `points`.
            - [ ] `points + 1` :: Python works out 8 and throws it away. Nothing is stored, so `points` stays 7.
            - [ ] `points =+ 1` :: With the signs in this order, Python reads `points = +1`, an ordinary assignment of the number 1. `points` becomes 1.
            ```

            **Watch out:** the operator comes first and the `=` second: `+=`, not `=+`. The wrong order is
            not an error, so Python gives no warning. It quietly assigns the wrong value.

            **In short:** `x += n` is short for `x = x + n`, and a calculation without an assignment
            changes no variable.
        ''',
        "prompt": r'''
            A usage counter keeps track of how many tokens your app has used. After each request, it adds
            the tokens of that request to the count. The function below is meant to do that, but it always
            gives back the old count, as if nothing had been added.

            **Your job:** find the bug in `add_tokens(used, extra)` and fix it. The code is already in the
            editor, and only one line is wrong.

            **What goes in**
            - `used`: the tokens used so far, a whole number, for example `10`
            - `extra`: the tokens to add, a whole number, for example `5`

            **What comes out**
            - `used` increased by `extra`, a whole number: `15` for the example values

            **Rules**
            - When `extra` is `0`, the result is `used` unchanged.

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
            "Look at the middle line. It works something out. Where does the result go?",
            "A calculation on a line of its own changes no variable. The new value has to be stored back under the name `used`.",
            "Turn the middle line into an update of `used`. You can use the long form with `=`, or the short form from the lesson that joins the plus sign and the equals sign.",
        ],
    },
    {
        "id": "variables-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Several names in one line, and trading places

            Sometimes two values belong together and you want to set them in one go:

            ```python
            provider, model = "openai", "gpt-4o"
            print(provider)
            # openai
            print(model)
            # gpt-4o
            ```

            Names on the left, values on the right, commas in between. The first name gets the first
            value and the second name gets the second value. This is called **multiple assignment**.

            It looks like a small convenience, but it solves a real puzzle. Suppose two names should trade
            their values, for example when the backup model becomes the primary one. The obvious attempt
            fails:

            ```python
            a = 1
            b = 2
            a = b
            b = a
            print(a, b)
            # 2 2
            ```

            After `a = b`, both names stand for 2. The 1 is gone, so nothing is left to give to `b`.

            Multiple assignment does the trade in one line:

            ```python
            first, second = 1, 2
            first, second = second, first
            print(first, second)
            # 2 1
            ```

            It works because of the rule you already know: Python works out the whole right side first.
            `second, first` is worked out as 2 and 1 while both names still have their old values. Only
            then are the two names assigned. Trading the values of two names is called a **swap**.

            Press Next to compare the attempt that fails with the one that works:

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

            ```fill
            low, high = 9, 2
            ___
            print(low, high)
            ---
            - [x] low, high = high, low :: Right. The right side is worked out first, as 2 and 9, and then both names are assigned. The program prints `2 9`.
            - [ ] low = high :: Now both names stand for 2 and the 9 is lost. The program prints `2 2`.
            - [ ] high, low = high, low :: This gives each name the value it already has, so nothing changes. The program prints `9 2`.
            ```

            **Watch out:** the number of names must match the number of values. `a, b = 1, 2, 3` stops
            with `ValueError: too many values to unpack (expected 2, got 3)`.

            **In short:** `a, b = b, a` swaps two values, because the right side is worked out before
            either name changes.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line.
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
            `tokens` starts at 10. `tokens = tokens + 5` makes it 15, and `tokens += 1` makes it 16, so the
            first `print` shows `16`. In `a, b = b, a`, Python works out the right side first, with the
            current values, which gives `"y"` and `"x"`. Then `a` gets `"y"` and `b` gets `"x"`. A `print`
            with a comma puts one space between the two values.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Keep a note of each name's value as you go down the lines.",
            "`tokens` changes three times before it is printed. In the line that has names on both sides of the `=`, the right side is worked out completely before either name changes.",
            "For the first line of output, start from 10, add 5 and then add 1. For the second, `a` and `b` have traded their values, and `print` puts one space between them.",
        ],
    },
    {
        "id": "variables-s4",
        "title": "Return two values",
        "difficulty": 0,
        "lesson": r'''
            ## Handing back two values at once

            A function often has two things to report. A model has a name and a size. A request has a
            status and a duration. You could write two functions, but it is simpler to let one function
            hand back both values. Put a comma between them after `return`:

            ```python
            def limits():
                return 128000, 16000

            print(limits())
            # (128000, 16000)
            ```

            Look at the output: Python shows both numbers inside one pair of parentheses. The function
            still hands back one thing. That thing is a small package that holds both numbers, in order.
            Such a package is called a **tuple**, and each value in it is an **item**.

            You can also write a tuple yourself, with parentheses: `("gpt-4o", 128000)`. A tuple may mix
            kinds of values, and the order is part of it: the first item stays first.

            ```predict
            def newest():
                return "claude", 3

            print(newest())
            print(len(newest()))
            ---
            The call hands back one tuple with two items. Python shows text inside a tuple with single quotes, so the first line is `('claude', 3)`. `len` works on tuples too: it counts the items, which gives 2.
            ```

            ### Quotes change everything

            Compare these two functions. Only the quotes differ.

            ```python
            def as_tuple():
                return 128000, 16000

            def as_text():
                return "128000, 16000"

            print(as_tuple())
            # (128000, 16000)
            print(as_text())
            # 128000, 16000
            ```

            The second function hands back one string that happens to contain a comma. No code can do
            arithmetic with it.

            ```quiz
            Which line hands back two separate values, a name and a number?
            - [x] `return "small", 512` :: Right. The comma stands between two values, so they go back together as a tuple of two items.
            - [ ] `return "small, 512"` :: The quotes go around everything, so this is one string with a comma inside it.
            - [ ] `return "small" 512` :: Without a comma Python cannot tell where one value ends and the next begins. It stops with a `SyntaxError`.
            ```

            **Watch out:** a number inside quotes is text. `"128000"` is a string, and `128000` is a
            number. A check that expects a number does not accept the string.

            **In short:** `return a, b` hands back one tuple that holds both values, in that order.
        ''',
        "prompt": r'''
            Your app has a default AI model. Other parts of the app need two facts about it: its name, and
            the size of its context window, which is the number of tokens the model can read at once.

            **Your job:** write `default_model()` so that it gives back both facts together.

            **What goes in**
            - nothing: the function takes no parameters

            **What comes out**
            - two values together, as a tuple of 2 items: first the string `"gpt-4o-mini"`, then the whole
              number `128000`

            **Rules**
            - The name comes first and the number second.
            - The number is a number, `128000`, and not the text `"128000"`.
            - Exactly two values come back.

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
            "One `return` can hand back more than one value. What goes between the values?",
            "The first value is text and the second is a number. Only one of them is written with quotes.",
            "Write a single `return` line: the model name as a string, then a comma, then the number without quotes.",
        ],
    },
    {
        "id": "variables-s5",
        "title": "Unpack the pair",
        "difficulty": 0,
        "lesson": r'''
            ## Taking a tuple apart

            A function has handed you a tuple with two values in it. Most of the time you do not want the
            package. You want the things inside it, each under its own name.

            ```python
            limits = (128000, 16000)
            context, output = limits
            print(context)
            # 128000
            print(output)
            # 16000
            ```

            Look at the middle line: names on the left, a tuple on the right. Python gives the first item
            to the first name and the second item to the second name. It is the multiple assignment from
            two steps ago. The only new part is that the values arrive packed in a tuple. Taking a tuple
            apart like this is called **unpacking**. The tuple itself does not change.

            Very often the right side is a call to a function that returns a tuple:

            ```python
            def newest_model():
                return "anthropic", "claude"

            provider, model = newest_model()
            print(model, "from", provider)
            # claude from anthropic
            ```

            Put this program in an order that works:

            ```order
            def size():
                return 1920, 1080
            width, height = size()
            print(height)
            ---
            The function has to exist before it can be called, and `height` only exists after the unpacking line has run.
            ```

            ```quiz
            `pair = ("eu", "gpt-4o")`. After the line `region, model = pair`, what is `model`?
            - [x] `"gpt-4o"` :: Right. The second name gets the second item.
            - [ ] `"eu"` :: That is the first item. It went to the first name, `region`.
            - [ ] `("eu", "gpt-4o")` :: With two names on the left, the tuple is taken apart. Neither name gets the whole tuple.
            ```

            **Watch out:** the number of names must equal the number of items. Three names for a tuple of
            two stops with `ValueError: not enough values to unpack (expected 3, got 2)`.

            **In short:** `a, b = some_tuple` gives each item of the tuple its own name, in order.
        ''',
        "prompt": r'''
            Apps often keep a model as a pair of two strings: the company that provides it, and the name
            of the model, for example `("openai", "gpt-4o")`. This function receives such a pair and should
            give back only the model name.

            **Your job:** finish `model_of(record)`. It is written except for one gap, marked `___`.
            Replace the gap so that the line takes the pair apart into `provider` and `model`.

            **What goes in**
            - `record`: a tuple of 2 strings, the provider first and the model name second, for example
              `("openai", "gpt-4o")`

            **What comes out**
            - the second item, the model name, as a string: `"gpt-4o"` for the example value

            **Rules**
            - It must work for every pair, not only for the ones in the examples.

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
            "The line with the gap is an unpacking: two names on the left, and on the right the tuple that is taken apart.",
            "Which name in the function stands for the pair that was handed in?",
            "The pair arrives through the function's parameter. Put the name of that parameter in the gap, with no quotes and no parentheses.",
        ],
    },
    {
        "id": "variables-1",
        "title": "Swap without a temp",
        "difficulty": 1,
        "lesson": r'''
            ## Hand the values back in a new order

            Two steps ago you swapped two names with `a, b = b, a`. It worked because Python builds the
            right side, `b, a`, as a tuple before it assigns anything. A function can use the same idea
            more directly. It does not have to move any values around. It can list them after `return` in
            whatever order it wants.

            ```python
            def rotate(first, second, third):
                return second, third, first

            print(rotate("primary", "backup", "spare"))
            # ('backup', 'spare', 'primary')
            ```

            `rotate` never looks at what its arguments are. It only passes them back in a different order.
            So it works for every kind of value, and for a mix of kinds as well:

            ```predict
            def rotate(first, second, third):
                return second, third, first

            print(rotate("gpt-4o", 0.5, 3))
            ---
            The first argument moves to the end, so the result is `(0.5, 3, 'gpt-4o')`. Python shows text inside a tuple with single quotes.
            ```

            People who know other programming languages often reach for an extra name to park a value for
            a moment, as in `temp = a`. A name that exists only to hold a value for a few lines is called
            a **temporary variable**. With tuples you rarely need one.

            ```quiz
            A function should hand back its two parameters together, as a tuple. Which line belongs in its body?

            ~~~python
            def pair(x, y):
                ...
            ~~~
            - [x] `return x, y` :: Right. Commas between the values make a tuple.
            - [ ] `return [x, y]` :: Square brackets make a different kind of value, a list, which a later chapter covers. A check that asks for a tuple fails.
            - [ ] `return "x, y"` :: The quotes make one string with the letters x and y in it. The parameters are not used at all.
            ```

            **Watch out:** parameter names are written without quotes. With quotes you hand back the
            letters of the name, not the value that the name stands for.

            **In short:** a function can return its values in any order, by listing them after `return`
            with commas between them.
        ''',
        "prompt": r'''
            Sometimes two settings need to trade places: the backup model becomes the primary one, and the
            primary becomes the backup. A function that takes two values and gives them back the other way
            round does that job.

            **Your job:** write `swap(a, b)` so that it gives back the two values in the opposite order.

            **What goes in**
            - `a`: any value, for example `1` or `"x"`
            - `b`: any value, for example `2` or `0.5`

            **What comes out**
            - a tuple of two values: `b` first, then `a`. For `1` and `2` that is `(2, 1)`.

            **Rules**
            - It works for values of any kind: numbers, text, or one of each.
            - The result is a tuple, not a list and not a single value.
            - The function creates no extra variable. A line such as `temp = a` fails a check. One line is
              enough.

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
            "Look at `rotate` in the lesson. It gives its values back in a new order without changing any of them.",
            "Nothing has to be stored or moved. The function only decides the order in which its two parameters go back.",
            "Write a single `return` line that lists both parameters with a comma between them, the second parameter first. Use no quotes and no square brackets.",
        ],
    },
    {
        "id": "variables-2",
        "title": "Remaining budget",
        "difficulty": 1,
        "lesson": r'''
            ## A name that lives inside the function

            Bigger functions do their work in stages. For that, a function can create a variable of its
            own to hold a result while it is being built: give it a starting value, update it line by
            line, and hand it back at the end.

            ```python
            def tokens_used(start, first, second):
                used = start
                used += first
                used += second
                return used

            print(tokens_used(50, 200, 300))
            # 550
            ```

            Press Next and watch `used` grow in the Variables box. Notice the last step too: once the
            function has returned, its variables are gone.

            ```diagram
            {"type": "trace", "title": "A local variable is built up and then returned", "code": ["def tokens_used(start, first, second):", "    used = start", "    used += first", "    used += second", "    return used", "", "print(tokens_used(50, 200, 300))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 7, "vars": {}, "out": ""},
              {"line": 2, "vars": {"start": "50", "first": "200", "second": "300"}, "out": "", "note": "The call set the three parameters. used does not exist yet."},
              {"line": 3, "vars": {"start": "50", "first": "200", "second": "300", "used": "50"}, "out": ""},
              {"line": 4, "vars": {"start": "50", "first": "200", "second": "300", "used": "250"}, "out": ""},
              {"line": 5, "vars": {"start": "50", "first": "200", "second": "300", "used": "550"}, "out": ""},
              {"line": null, "vars": {}, "out": "550\n", "note": "The function has returned 550. Its parameters and used no longer exist."}
            ]}
            ```

            A variable that is created inside a function is called a **local variable**. It exists only
            while the function runs, and code outside the function cannot see it.

            ```quiz
            What happens on the last line of this program?

            ~~~python
            def doubled(n):
                result = n * 2
                return result

            print(doubled(4))
            print(result)
            ~~~
            - [x] Python stops with `NameError: name 'result' is not defined` :: Right. `result` is a local variable of `doubled`. It disappeared when the function returned, so outside the function the name does not exist.
            - [ ] It prints `8` a second time :: The value 8 went back to the caller, but the name `result` stayed inside the function and is gone.
            - [ ] It prints `None` :: `None` is what a call hands back when there is no `return`. Here the trouble is a name that does not exist.
            ```

            The same pattern works with any augmented assignment. This function forgets one of its
            stages:

            ```try
            def total_cost(price, shipping):
                cost = price
                return cost

            print(total_cost(40, 5))
            ---
            The function ignores the shipping. Add one line with `+=` so that the program prints `45`.
            ---
            def total_cost(price, shipping):
                cost = price
                cost += shipping
                return cost

            print(total_cost(40, 5))
            ---
            The local variable `cost` starts at the price, grows by the shipping, and is handed back.
            ```

            One more fact you will need: subtraction does not stop at zero. After `balance = 100`, the
            line `balance -= 130` leaves `balance` at `-30`.

            **Watch out:** return the name that you updated, not the parameter you started from. In the
            example, `return start` would hand back 50.

            **In short:** a local variable holds a result while the function builds it, and it is gone
            when the function returns.
        ''',
        "prompt": r'''
            A token budget tracker answers one question: after a request, how many tokens are left? A
            request uses tokens twice, once for the prompt and once for the answer, and both amounts come
            off the budget.

            **Your job:** write `remaining_budget(budget, prompt_tokens, output_tokens)` so that it gives
            back what is left of the budget after both amounts are taken off.

            **What goes in**
            - `budget`: the tokens available at the start, a whole number, for example `1000`
            - `prompt_tokens`: the tokens the prompt used, a whole number, for example `100`
            - `output_tokens`: the tokens the answer used, a whole number, for example `250`

            **What comes out**
            - the budget minus both amounts, a whole number: `650` for the example values

            **Rules**
            - Take each amount off with the augmented assignment `-=`, on a line of its own: one `-=` line
              for the prompt tokens and one for the output tokens. A check counts them.
            - When the request used more than the budget, give back the negative number. Do not stop at `0`.
            - When nothing was used, give back the budget unchanged.

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
            "`x -= 5` is short for `x = x - 5`. The `tokens_used` function in the lesson does the same kind of job with `+=`.",
            "Keep one local variable for what is left. Start it at the budget, make it smaller twice, and hand it back.",
            "The body has four lines: give a new name the value of `budget`, take the prompt tokens off it with `-=`, take the output tokens off it with `-=`, and return that name.",
        ],
    },
    {
        "id": "variables-6",
        "title": "Config script",
        "difficulty": 1,
        "mode": "script",
        "lesson": r'''
            ## Settings that never change

            Some values are decided once and then used all over a program: which model to call, how many
            times to retry. If the number 3 is typed in five places, changing it later means finding all
            five. It is safer to give the value one name at the top of the file and use the name
            everywhere else.

            ```python
            PROVIDER = "openai"
            MAX_RETRIES = 3
            print(PROVIDER, MAX_RETRIES)
            # openai 3
            ```

            A name that is assigned once at the top of a file and never reassigned is called a
            **constant**. Constants are written in capital letters, with `_` between the words. Ordinary
            names, such as `user_name`, are written in small letters.

            Python itself does not protect a constant. You could reassign `MAX_RETRIES` and no error would
            appear. The capital letters are a message to people: this value is a setting, leave it alone.

            ```quiz
            By convention, which of these names is a constant?
            - [x] `MAX_TOKENS` :: Right. All capitals, with an underscore between the words.
            - [ ] `max_tokens` :: Small letters mark an ordinary variable, one that may change while the program runs.
            - [ ] `MaxTokens` :: A capital at the start of each word is the style for a different kind of name, which a later chapter covers.
            ```

            ### A script that uses its constants

            This step asks for a script again, as in the Basics chapter: statements that start at the left
            edge, with no `def`, run from top to bottom. The constants come first, and the lines below use
            them by name.

            ```python
            TIMEOUT_SECONDS = 1.5
            print("timeout is", TIMEOUT_SECONDS)
            # timeout is 1.5
            ```

            The whole point of a constant is that the value is typed once. The script below breaks that
            rule:

            ```try
            MODEL = "gpt-4o"
            RETRIES = 3
            print("gpt-4o", 3)
            ---
            The `print` line types both values out a second time. Change `RETRIES` to `5`, and change the `print` line so that it uses the two names. The program should print `gpt-4o 5`.
            ---
            MODEL = "gpt-4o"
            RETRIES = 5
            print(MODEL, RETRIES)
            ---
            Each value now lives in one place. Changing a setting means changing one line.
            ```

            **Watch out:** numbers take no quotes. `0.2` is a number, and `"0.2"` is a string that only
            looks like one.

            **In short:** a constant is a name in capital letters that is set once at the top of the file
            and used by name below.
        ''',
        "prompt": r'''
            The settings of an AI model are usually kept as constants at the top of a file: which model to
            use, how much variety its answers may have (called the temperature), and how many tokens it
            may write.

            **Your job:** write a script that defines three constants and prints them on one line. A
            script has no function: the statements start at the left edge.

            **What the script defines**
            - `MODEL`: the string `"gpt-4o-mini"`
            - `TEMPERATURE`: the number `0.2`
            - `MAX_TOKENS`: the whole number `512`

            **What comes out**
            - one line of output with the three values, separated by single spaces

            **Rules**
            - The names and the values are exactly the ones above.
            - The `print` uses the three names. A check fails when the values are typed out a second time
              inside the `print`.
            - The script prints nothing else.

            **Examples**

            Running the script prints:
            ```text
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
            "A script is written at the left edge of the file, without `def`. Remember what `print` does with several values that are separated by commas.",
            "Three assignments come first: the text value in quotes, the two numbers without quotes. Then comes one `print` that uses the names.",
            "Write one assignment for each of the three names from the task, in capital letters. Under them, write a single `print` with the three names separated by commas. Press Run and compare your output with the example.",
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
            ## Names Python will not let you use

            You may call a variable almost anything. Almost. A few rules decide what counts as a name:

            - A name is made of letters, digits and `_`. Spaces and hyphens are not allowed.
            - It does not start with a digit. `model_2` is fine, and `2nd_model` is not.
            - Capital letters matter: `Zone` and `zone` are two different names.

            A word that follows these rules is called an **identifier**.

            ```python
            zone = "west"
            model_2 = "claude"
            print(model_2 + "/" + zone)
            # claude/west
            ```

            ```quiz
            Which of these can be the name of a variable?
            - [x] `model_2` :: Right. Letters, a digit and an underscore, and it does not start with the digit.
            - [ ] `2nd_model` :: A name may not start with a digit. Python stops with a `SyntaxError`.
            - [ ] `model-name` :: The hyphen is the minus sign, so Python reads this as `model` minus `name`.
            ```

            ### Words that are already taken

            There is one more rule, and it is the one that catches people. Some words already mean
            something to Python. `def` starts a function and `return` hands a value back. Python keeps
            such words for itself, and they are called **keywords**. There are 35 of them, among them
            `if`, `class`, `global` and `import`. A keyword cannot be used as a name.

            Python's message for this mistake is not very helpful. For the line `class = "large"` it only
            says:

            ```text
            SyntaxError: invalid syntax
            ```

            It does not say "that word is a keyword". You have to recognise it yourself. The editor helps:
            it shows keywords in a different colour from ordinary names.

            ```try
            class = "large"
            print(class)
            ---
            `class` is a keyword, so this program does not run. Rename the variable to `size` in both places, so that the program prints `large`.
            ---
            size = "large"
            print(size)
            ---
            A name is yours to choose, as long as Python has not already taken the word.
            ```

            **Watch out:** when you rename something, rename it in every place it is used. A name that is
            changed in one place and not in the other gives a `NameError`.

            **In short:** a name uses letters, digits and `_`, does not start with a digit, and is not one
            of Python's keywords.
        ''',
        "prompt": r'''
            Models are often deployed in several regions of the world, and each deployment has an id such
            as `gpt-4o@eu`: the model, an `@`, then the region. The function `endpoint` builds that id. But
            the file does not run at all. Check shows a `SyntaxError`, because the second parameter was
            given a name that Python keeps for itself.

            **Your job:** repair `endpoint` so the file runs and the function returns the deployment id
            for the supplied model and region.

            **What goes in**
            - `model`: a model name, a string, for example `"gpt-4o"`
            - `region`: a region code, a string, for example `"eu"`

            **What comes out**
            - one string: the model, then `@`, then the region, with no spaces: `"gpt-4o@eu"` for the
              example values

            **Rules**
            - The parameters are named exactly `model` and `region`, in that order. A check looks at the
              names.

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
            "Look at the colours in the editor. One word in the `def` line is shown like `def` and `return`, not like an ordinary name.",
            "That word is one of Python's keywords, so it cannot be the name of a parameter. The task tells you which name to use instead.",
            "Choose the valid parameter name required by the task, then check that references inside the function consistently use the corresponding parameter. Keep the deployment-id format unchanged.",
        ],
    },
    {
        "id": "variables-7",
        "title": "Fix: one name per item",
        "difficulty": 1,
        "lesson": r'''
            ## One name for every item

            Unpacking has one strict rule: the left side needs exactly as many names as the tuple has
            items. Three items, three names.

            ```python
            window = (200000, 8000, 192000)
            context, output, free = window
            print(free)
            # 192000
            ```

            With the wrong number of names, Python stops and tells you both numbers:

            ```text
            ValueError: too many values to unpack (expected 2, got 3)
            ```

            Read it word for word. "Expected 2" is the number of names you wrote. "Got 3" is the number of
            items in the tuple. "Too many values" means the tuple has more items than you have names, and
            "not enough values" means it has fewer. A `ValueError` in general means that a value is the
            right kind of thing, here a tuple, but something about its contents does not fit.

            ```quiz
            `point = (4, 7)`. Which line stops with `ValueError: not enough values to unpack (expected 3, got 2)`?
            - [x] `x, y, z = point` :: Right. Three names are waiting, and the tuple has only two items to give.
            - [ ] `x, y = point` :: Two names and two items match, so this line runs.
            - [ ] `x = point` :: One name without a comma is an ordinary assignment. `x` becomes the whole tuple, and there is no error.
            ```

            ### When you do not need every item

            Every item still needs a name, even one you will never use. Many programmers call such an item
            `_`, a name that says "not needed":

            ```python
            window = (200000, 8000, 192000)
            context, _, _ = window
            print(context)
            # 200000
            ```

            ```fill
            reply = ("ok", 200, "done")
            ___ = reply
            print(code)
            ---
            - [x] status, code, text :: Right. Three names for three items, and `code` is the second, so the program prints 200.
            - [ ] status, code :: Two names for three items. Python stops with `ValueError: too many values to unpack`.
            - [ ] code, status, text :: The count is right, but the names are in the wrong positions. `code` gets the first item, so the program prints `ok`.
            ```

            **Watch out:** the position of a name decides which item it gets. Names in the wrong order
            give no error. They give the wrong value.

            **In short:** count the items of the tuple, then write exactly that many names, in the same
            order.
        ''',
        "prompt": r'''
            An AI API reports the token usage of a request as a tuple of three counts: the prompt tokens,
            the completion tokens (the model's answer) and the total, for example `(120, 30, 150)`. The
            function `total_of` should give back the last of the three. Instead it stops with
            `ValueError: too many values to unpack (expected 2, got 3)`.

            **Your job:** fix the unpacking line in `total_of(usage)`. The code is already in the editor.

            **What goes in**
            - `usage`: a tuple of three whole numbers, `(prompt, completion, total)`, for example
              `(120, 30, 150)`

            **What comes out**
            - the third item, the total, as a whole number: `150` for the example value

            **Rules**
            - Keep the unpacking: the tuple is taken apart in one assignment line. A check looks for it.
            - Do not use square brackets, as in `usage[2]`. They are another way to read an item, which a
              later chapter covers, and a check fails when they appear.

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
            "Read the error message: it says how many names Python expected and how many values it got.",
            "The tuple has three items, but the unpacking line has only two names. Every item needs a name, even an item you do not use.",
            "Add one more name to the left side of the unpacking line, in the middle, so that the three names line up with the three counts. The `return` line can stay as it is.",
        ],
    },
    {
        "id": "variables-3",
        "title": "Unpack a record",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            An API describes each model as a tuple of four items, for example
            `("openai", "gpt-4o", 128000, 16000)`: the provider, the model name, the context window (how
            many tokens the model can handle in total) and the maximum output (how many of those it may
            write). Your logs need two things made from that record: a short id such as `openai/gpt-4o`,
            and the number of tokens that are left for the input.

            **Your job:** write `describe(record)` so that it gives back both.

            **What goes in**
            - `record`: a tuple `(provider, model_name, context_window, max_output)`: two strings, then two
              whole numbers

            **What comes out**
            - two values together, as a tuple of 2:
              1. the model id, a string: the provider, a `/`, then the model name, with no spaces, for
                 example `"openai/gpt-4o"`
              2. the input budget, a whole number: `context_window` minus `max_output`, for example `112000`

            **Rules**
            - Take the record apart into four names in one assignment line, by unpacking. A check looks
              for it.
            - Exactly two values come back.

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
            "Two ideas from this chapter meet here: unpacking a tuple into names, and returning two values with a comma between them.",
            "First take the record apart into four names. Then build the id by joining strings with `+`, and work out the budget with `-`.",
            "Line one of the body: four names, separated by commas, then `=` and the parameter. Line two: `return`, then the provider joined to a slash and to the model name, then a comma, then the context window minus the maximum output.",
        ],
    },
    {
        "id": "variables-4",
        "title": "Nested unpacking",
        "difficulty": 2,
        "lesson": r'''
            ## Putting it together: a tuple inside a tuple

            An item of a tuple can itself be a tuple. This one has two items: a pair, and a string.

            ```python
            call = (("search", 2), "ok")
            print(len(call))
            # 2
            ```

            You can take both layers apart in one assignment. Write the left side in the same shape as
            the value, with parentheses around the names for the inner tuple:

            ```python
            call = (("search", 2), "ok")
            (tool, attempts), status = call
            print(tool, attempts, status)
            # search 2 ok
            ```

            Unpacking two layers at once is called **nested unpacking**. The parentheses on the left are
            what tell Python to open the inner tuple as well. Leave them out and see what the first name
            gets:

            ```predict
            call = (("search", 2), "ok")
            inner, status = call
            print(inner)
            print(status)
            ---
            `call` has two items, and the left side has two names. So `inner` gets the whole first item, which is the pair `('search', 2)`, and `status` gets `ok`.
            ```

            ```quiz
            `entry = ("europe", ("fast", 0.2), "on")`. Which left side matches its shape?
            - [x] `region, (speed, price), state = entry` :: Right. A name, then a pair of names in parentheses, then a name: the same shape as the value.
            - [ ] `(region, speed), price, state = entry` :: The parentheses are around the wrong part. The first item is a single string, not a pair, so Python stops with a `ValueError`.
            - [ ] `region, speed, price, state = entry` :: Four names, but `entry` has only three items. The pair in the middle counts as one item.
            ```

            To plan a function like the one in this step, look at the shape of the value first. Count its
            items, find the one that is itself a tuple, and copy that shape onto the left side of the
            assignment.

            **Watch out:** count the items of the outer tuple, not every value you can see. A pair inside
            a tuple is one item.

            **In short:** the left side of an unpacking can mirror the shape of the value, with
            parentheses around the names for an inner tuple.
        ''',
        "prompt": r'''
            A router decides which model handles a request. It reports its choice as a pair whose second
            item is itself a pair, for example `("openai", ("gpt-4o", 128000))`: the provider, and then
            the model name together with its context window. For a log line you want the three pieces
            side by side.

            **Your job:** write `flatten(route)` so that it gives back the three pieces as one flat tuple.

            **What goes in**
            - `route`: a tuple `(provider, (model_name, context_window))`, for example
              `("openai", ("gpt-4o", 128000))`

            **What comes out**
            - a tuple of three values with no tuple inside it: `(provider, model_name, context_window)`

            **Rules**
            - Take `route` apart in one assignment whose left side has a pair inside it (nested
              unpacking). A check looks for it.
            - Do not use square brackets anywhere, as in `route[1]`. A check fails when they appear.
            - Exactly three values come back, in the order shown.

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
            "The left side of an unpacking can have the same shape as the value, with parentheses around the names for an inner tuple.",
            "Copy the shape of `route` onto the left side: one name, then a pair of names in parentheses. After that line you have three names to hand back.",
            "Line one of the body: a name, a comma, two names in parentheses, then `=` and the parameter. Line two: `return` and the three names with commas between them, in the order provider, model name, context window.",
        ],
    },
    {
        "id": "variables-5",
        "title": "Rolling stats",
        "difficulty": 3,
        "prompt": r'''
            Your app measures how long each call to a model API takes. Such a waiting time is called a
            latency, and it is measured in milliseconds (ms). Instead of keeping every measurement, the
            app keeps a running summary in one tuple of four numbers, the **stats tuple**:
            `(count, total, lowest, highest)`. A tuple cannot be changed once it exists, so every new
            measurement builds a new stats tuple from the old one.

            **Your job:** write three functions that create, update and read a stats tuple.

            **1. `start_stats(value)`**
            - goes in: `value`, the first latency, a whole number, for example `120`
            - comes out: the stats tuple after that one measurement. The count is `1`, and `value` is the
              total, the lowest and the highest all at once: `(1, 120, 120, 120)` for the example value

            **2. `add_value(stats, value)`**
            - goes in: `stats`, a stats tuple, for example `(1, 120, 120, 120)`, and `value`, one more
              latency, for example `80`
            - comes out: a new stats tuple: the count plus 1, the total plus `value`, the smaller of the
              old lowest and `value`, and the bigger of the old highest and `value`: `(2, 200, 80, 120)`
              for the example values

            **3. `average(stats)`**
            - goes in: `stats`, a stats tuple whose count is at least 1
            - comes out: the total divided by the count (the operator `/` divides), rounded to 2 decimal
              places

            **Rules**
            - `add_value` gives back a new tuple. The tuple it was given stays as it was.
            - `add_value` can be called many times in a row, each time on the result of the call before.
            - The built-ins `min` and `max` pick the smaller and the bigger of two values. Nothing more is
              needed for that part.

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
            "`add_value` and `average` start the same way: take the stats tuple apart into four names. Then work out the new values and hand them back.",
            "After one measurement the count is 1, and the same value is the total, the lowest and the highest. Every update adds one to the count, adds the value to the total, keeps the smaller lowest and keeps the bigger highest.",
            "`start_stats` returns four values: 1, and then the value three times. `add_value` unpacks `stats` into four names and returns four new values, with `min` for the lowest and `max` for the highest. `average` unpacks, divides the total by the count, and rounds the result with the second argument of `round`.",
        ],
    },
]
