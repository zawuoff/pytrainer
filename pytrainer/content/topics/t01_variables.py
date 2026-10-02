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

LESSON = r'''
## Chapter notes: Variables & Assignment

**Assignment** `name = value`: the right side is worked out first, then the name points
at the result. `=` stores; `==` compares (next chapters).

```python
max_tokens = 256
remaining = max_tokens - 56
print(remaining)
```

**Reassignment**: a name can point at a new value later; the old one is forgotten.
`tokens = tokens + 50` uses the old value to make the new one.

**Augmented assignment** - shortcuts: `x += 5` is `x = x + 5`. Also `-=`, `*=`, `/=`.
`used + extra` on its own line calculates but stores nothing.

**Multiple assignment**: `provider, model = "openai", "gpt-4o"` (matched left to right).

**Swap** without a temporary name: `a, b = b, a` (the whole right side is built first).

**Tuples**: `return a, b` returns two values together as a *tuple* `(a, b)`.

**Unpacking** splits a group into names in one line; the counts must match:

```python
record = ("anthropic", "claude", 200000)
provider, model, context = record
route = ("openai", ("gpt-4o", 128000))
provider, (model, context) = route   # nested unpacking: same shape on the left
print(provider, model, context)
```

Wrong count -> `ValueError: too many values to unpack (expected 2)` or
`not enough values to unpack`.

**Names**: letters, digits and `_`, not starting with a digit, case-sensitive
(`Model` is not `model`). Keywords (`def`, `return`, `global`, `class`, `if`...) can't be
names. Style (PEP 8): `lower_snake_case` for normal names, `UPPER_SNAKE_CASE` for
*constants* (values set once at the top of a file and never changed).

**Gotchas**
- Swapping in two steps (`a = b` then `b = a`) loses a value.
- `return "b, a"` returns one string; `return b, a` returns a tuple.
- A variable made inside a function only exists inside it (a *local variable*).
'''

EXERCISES = [
    {
        "id": "variables-s2",
        "title": "Fill in the total",
        "difficulty": 0,
        "lesson": r'''
            A **variable** is a **labelled box**. You put a value in the box and write a name on the
            label. Later you use the name, and Python fetches what is inside.

            ```python
            model = "gpt-4o-mini"
            max_tokens = 256
            print(model, max_tokens)
            ```

            The single `=` means "put the value on the right into the box on the left". Python always
            works out the right side **first**, so the right side can be a calculation:

            ```python
            prompt = 120
            completion = 30
            total = prompt + completion
            print(total)
            ```

            Vocabulary: this is called *assignment*, and people say "`total` is *assigned* the value
            150". Inside a function, parameters are variables too - they're boxes that each call fills.

            Watch out: the name goes on the left. `150 = total` is an error.
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
            A box can get **new contents** at any time. When you assign to a name again, the
            old value is thrown out and the name now points at the new one.

            ```python
            status = "waiting"
            print(status)
            status = "done"
            print(status)
            ```

            The right side can even use the name's **current** value. Python works out the
            right side first, using what is in the box right now, then stores the result back:

            ```python
            tokens = 100
            tokens = tokens + 50
            print(tokens)
            ```

            Read `tokens = tokens + 50` as "the new tokens is the old tokens plus 50".

            Vocabulary: giving a name a new value is called *reassignment*.

            Watch out: lines run top to bottom. A `print` only sees the value the name has at
            that moment.
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
            Updating a box is so common that Python has a shortcut. Think of a **tally counter**:
            you don't write down a brand new number each time, you just click "+1".

            ```python
            used = 100
            used = used + 20   # the long way
            used += 5          # the short way: same meaning
            print(used)
            ```

            `used += 5` means "take what is in `used`, add 5, put the result back in `used`". It works
            for other maths too: `-=` subtracts, `*=` multiplies, `/=` divides.

            ```python
            budget = 1000
            budget -= 300
            print(budget)
            ```

            Vocabulary: this is called *augmented assignment*.

            Watch out: `used + 5` on a line by itself calculates the answer and then throws it away.
            Nothing is stored unless there is an `=` (or `+=`) on the line.
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
            You can fill several boxes in one line. Values on the right are matched with names on
            the left, in order, like handing out name badges down a queue.

            ```python
            provider, model = "openai", "gpt-4o"
            print(provider)
            print(model)
            ```

            This makes a neat trick possible: **swapping** two values. Python builds the whole right
            side first (`b, a` with the *old* values), and only then fills the boxes.

            ```python
            a, b = 1, 2
            a, b = b, a
            print(a, b)
            ```

            Vocabulary: filling several names at once is *multiple assignment*.

            Watch out: swapping in two steps loses a value. After `a = b`, the old `a` is gone, so
            `b = a` just copies the same thing back.
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
            `tokens` goes 10 -> 15 -> 16: each line uses the current value and stores the
            new one. `a, b = b, a` builds the right side (`"y", "x"`) first, then assigns,
            so the values swap.
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
            A function can hand back more than one thing. Think of a **lunch box with two
            compartments**: one `return`, but two items inside. Separate the values with a comma.

            ```python
            def limits():
                return 128000, 16000

            print(limits())
            ```

            That prints `(128000, 16000)`. The parentheses show that the two values travel together
            as one group.

            Vocabulary: a fixed group of values like this is a *tuple*. You'll see tuples written with
            parentheses, e.g. `("gpt-4o", 128000)`. Order matters: the first value stays first.

            Watch out: quotes make text. `return "128000, 16000"` returns one string, not two values.
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
            The opposite of packing a lunch box is **unpacking** it: you take the items out and put
            each one in its own named box, all in one line.

            ```python
            record = ("anthropic", "claude")
            provider, model = record
            print(provider)
            print(model)
            ```

            The group goes on the right of `=`, and one name per item goes on the left, in order.
            The first name gets the first item, the second name the second item.

            It also works with the result of a function:

            ```python
            def limits():
                return 128000, 16000

            context, output = limits()
            print(context - output)
            ```

            Vocabulary: this is called *unpacking* (or *tuple unpacking*).

            Watch out: you need exactly as many names as there are items.
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
            Remember the swap trick, `a, b = b, a`? Inside a function you can do it even more simply:
            you don't need to change the boxes at all. Just **hand the values back in the other order**.

            ```python
            def reverse_pair(first, second):
                return second, first

            print(reverse_pair("primary", "backup"))
            ```

            A tuple can hold anything: numbers, text, or a mix of both. The function doesn't care
            what kind of values it gets - it just rearranges them.

            Vocabulary: a helper name used only to hold a value for a moment (like `temp = a`) is a
            *temporary variable*. With tuples, Python rarely needs one.

            Watch out: `return [second, first]` (square brackets) makes a *list*, not a tuple. Use
            just commas.
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
            Inside a function you can make your own boxes to keep track of work in progress, like a
            **running total on a notepad**.

            ```python
            def after_two_requests(budget, first, second):
                left = budget
                left -= first
                left -= second
                return left

            print(after_two_requests(1000, 200, 300))
            ```

            `left` starts as a copy of the budget, then shrinks twice. Each `-=` line updates the
            value, and the last line hands back what remains.

            Vocabulary: a variable created inside a function is a *local variable*. It exists only
            while the function runs - code outside can't see `left`.

            Numbers can go below zero: `100 - 130` is `-30`. Python doesn't stop at 0 unless you
            tell it to.

            Watch out: return the updated name (`left`), not the original parameter.
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
            Some values are settings you choose once and never change: the model name, the maximum
            retries. Think of them as **the labels on a machine's control panel**: set at the top,
            used everywhere below.

            ```python
            MODEL = "gpt-4o-mini"
            MAX_RETRIES = 3
            print(MODEL, MAX_RETRIES)
            ```

            By convention these are written in `UPPER_SNAKE_CASE`: capitals, words joined with `_`.
            Normal names use `lower_snake_case`, like `user_name`.

            A file of lines at the left edge (no `def`) is a *script*: it runs top to bottom when you
            press Run. Put the settings at the top, then use them by name:

            ```python
            TEMPERATURE = 0.2
            print("temperature is", TEMPERATURE)
            ```

            Vocabulary: these names are called *constants*. Python doesn't lock them - the capitals
            are a promise to other programmers: "don't change this".

            Watch out: numbers don't need quotes. `0.2` is a number, `"0.2"` is text.
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
            You can name boxes almost anything - but a few words are **already taken**, like
            reserved seats with a sign on them. Python uses these words for its own grammar:
            `def`, `return`, `if`, `class`, `global` and a few dozen more.

            The naming rules:
            - letters, digits and `_` only (no spaces or dashes);
            - don't start with a digit (`2nd_model` is not allowed, `model_2` is);
            - capitals matter: `Region` and `region` are different names;
            - not a reserved word.

            ```python
            region = "eu"
            model_2 = "claude"
            print(model_2 + "@" + region)
            ```

            Using a reserved word as a name stops the whole file with a `SyntaxError`, often
            just saying `invalid syntax` and pointing at that word.

            Vocabulary: the reserved words are called *keywords*. A valid name is an
            *identifier*.
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
            Unpacking is like handing out coats at a cloakroom: you need **exactly one hook per
            coat**. If there are three coats and two hooks, Python refuses.

            ```python
            usage = (120, 30, 150)
            prompt, completion, total = usage
            print(total)
            ```

            With the wrong number of names you get a `ValueError`, and its message tells you the
            counts:

            ```text
            ValueError: too many values to unpack (expected 2)
            ```

            "Too many values" means the group has more items than you gave names. "Not enough values"
            means the opposite. Count the items, then count your names.

            If you don't need an item, still give it a name. Many programmers use `_` for "I don't
            care about this one": `_, _, total = usage`.

            Vocabulary: a `ValueError` is Python's way of saying "right kind of thing, wrong
            contents".
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
            Putting it together: a tuple can hold another tuple, like a **box inside a box**. To
            unpack it in one go, give the left side the **same shape**, with parentheses around the
            inner names.

            ```python
            route = ("openai", ("gpt-4o", 128000))
            provider, (model, context) = route
            print(provider, model, context)
            ```

            Vocabulary: this is *nested unpacking*.
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
