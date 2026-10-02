TOPIC = {
    "id": "data-types",
    "title": "Data Types",
    "track": "foundations",
    "order": 2,
    "requires": ["variables"],
    "summary": """
        The built-in scalar types (int, float, str, bool, None), converting between
        them, truthiness, float precision, and the basics of tuples and sets.
    """,
    "concepts": ["int", "float", "str", "bool", "None", "type conversion", "ValueError",
                 "truthiness", "float precision", "round", "tuples", "sets", "hashability"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["type", "int", "float", "str", "bool", "none", "convert", "conversion",
                 "valueerror", "typeerror", "round", "division", "remainder", "truthy",
                 "set", "strip"],
    "cards": [
        {
            "syntax": "type(value).__name__",
            "explain": "type(value) returns the type of a value. Adding .__name__ gives the name of the type as a string.",
            "example": r'''
                print(type(512))
                # <class 'int'>
                print(type("512").__name__)
                # str
                print(type(0.7).__name__, type(None).__name__)
                # float NoneType
            ''',
        },
        {
            "syntax": "int(text)  /  float(text)  /  str(value)",
            "explain": "Builds a new value of that type. int() and float() ignore spaces and newlines around the digits.",
            "example": r'''
                print(int(" 42\n") + 1)
                # 43
                print(float("0.25") * 2)
                # 0.5
                print("tokens: " + str(5))
                # tokens: 5
            ''',
        },
        {
            "syntax": "text.strip().lower()",
            "explain": "strip() removes spaces and newlines at both ends. lower() and upper() change the letter case. Each returns a new string.",
            "example": r'''
                answer = "  YES\n"
                print(answer.strip().lower())
                # yes
                print(answer.strip().upper() + "!")
                # YES!
            ''',
        },
        {
            "syntax": "a / b    a // b    a % b    round(x, n)",
            "explain": "/ always gives a float. // divides and rounds down. % gives the remainder. round(x, n) keeps n decimal places.",
            "example": r'''
                print(7 / 2, 7 // 2, 7 % 2)
                # 3.5 3 1
                print(round(8 / 3, 2))
                # 2.67
                print(0.1 + 0.2)
                # 0.30000000000000004
            ''',
        },
        {
            "syntax": "a == b    a <= b    value is None",
            "explain": "A comparison gives the bool True or False. bool(x) is False for 0, 0.0, \"\", None and empty groups.",
            "example": r'''
                used = 900
                print(used <= 1000, used == 1000, used != 1000)
                # True False True
                print(used is None, bool(used), bool(""))
                # False True False
            ''',
        },
        {
            "syntax": "set(group)    value in s    a & b    a | b",
            "explain": "A set keeps one copy of each value. in tests membership. & gives values in both sets, | in either.",
            "example": r'''
                tags = set(("rag", "llm", "rag"))
                print(len(tags), "rag" in tags)
                # 2 True
                print(tags & {"llm", "eval"})
                # {'llm'}
                print(len(tags | {"llm", "eval"}))
                # 3
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Data Types

Every value in Python has a **type**. The type decides which operations work on the value.

| type | examples | what it holds |
| --- | --- | --- |
| `int` | `512`, `-3` | A whole number. It is exact at any size. |
| `float` | `0.7`, `1.0` | A number with a decimal point. It is not exact. |
| `str` | `"512"`, `""` | Text. It is text even when it holds digits. |
| `bool` | `True`, `False` | The result of a comparison. |
| `NoneType` | `None` | The single value `None`, which means "no value". |
| `tuple` | `("user", "hi")` | A fixed group. It keeps the order and repeated values. |
| `set` | `{"rag", "llm"}` | A group of unique values with no order. |

### Reading a type

`type(x)` returns the type of `x`. A dot after a value reaches something that belongs to
that value. `type(x).__name__` reads the `__name__` of the type object. It has no
parentheses because it is stored text, not an action. It is the name of the type as a string.

```python
print(type(512))
# <class 'int'>
print(type("512").__name__)
# str
```

### Converting between types

Each type has a function with the same name that builds a value of that type: `int()`,
`float()`, `str()`, `bool()` and `set()`. Inside a string, `\n` is the **newline** character:
the character that ends a line. `int()` and `float()` ignore spaces and newlines around the
digits. `int()` on a float drops the decimal part. It does not round.

```python
print(int(" 42\n") + 1)
# 43
print(float("0.25"))
# 0.25
print(int(3.9))
# 3
```

Step through this program to see which type each variable gets.

```diagram
{"type": "trace", "title": "From text to numbers and back to text", "code": ["text = \" 512\\n\"", "max_tokens = int(text)", "used = 200", "left = max_tokens - used", "share = left / max_tokens", "label = \"left: \" + str(left)", "print(label)", "print(round(share, 2))"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {"text": "' 512\\n'"}, "out": ""},
  {"line": 3, "vars": {"text": "' 512\\n'", "max_tokens": "512"}, "out": ""},
  {"line": 4, "vars": {"text": "' 512\\n'", "max_tokens": "512", "used": "200"}, "out": ""},
  {"line": 5, "vars": {"text": "' 512\\n'", "max_tokens": "512", "used": "200", "left": "312"}, "out": ""},
  {"line": 6, "vars": {"text": "' 512\\n'", "max_tokens": "512", "used": "200", "left": "312", "share": "0.609375"}, "out": ""},
  {"line": 7, "vars": {"text": "' 512\\n'", "max_tokens": "512", "used": "200", "left": "312", "share": "0.609375", "label": "'left: 312'"}, "out": ""},
  {"line": 8, "vars": {"text": "' 512\\n'", "max_tokens": "512", "used": "200", "left": "312", "share": "0.609375", "label": "'left: 312'"}, "out": "left: 312\n"},
  {"line": null, "vars": {"text": "' 512\\n'", "max_tokens": "512", "used": "200", "left": "312", "share": "0.609375", "label": "'left: 312'"}, "out": "left: 312\n0.61\n"}
]}
```

### The + operator

`+` adds two numbers and joins two strings. A string plus a number stops the program with
a `TypeError`. Convert the number with `str()` first.

```python
print(2 + 3)
# 5
print("2" + "3")
# 23
print("tokens: " + str(5))
# tokens: 5
```

### String methods

A **method** is a function that belongs to a value. You call it with a dot after the value.
`.strip()` returns a new string without the spaces and newlines at both ends. `.lower()`
and `.upper()` return a new string in lowercase or uppercase. The original string does not
change. Each result is a string, so you can call the next method on it directly.

```python
text = "  Hello\n"
print(text.strip().lower())
# hello
```

### Division and rounding

`/` always gives a float. `//` divides and rounds down to a whole number. `%` gives the
remainder. `round(x, n)` rounds `x` to `n` decimal places.

```python
print(7 / 2)
# 3.5
print(7 // 2)
# 3
print(7 % 2)
# 1
print(round(2.3456, 2))
# 2.35
```

### Comparisons

The operators `==`, `!=`, `<`, `<=`, `>` and `>=` compare two values and give a `bool`.
You can return that bool directly.

```python
used = 900
limit = 1000
print(used <= limit)
# True
```

### Floats are not exact

A float stores most decimal numbers as a close approximation. Round a float before you
show it. When you compare floats, allow a small **tolerance**: an amount by which the two
values may differ. `1e-9` is a way to write `0.000000001`. In the last line below, the left
side is larger than `0.3` by less than the tolerance, so the comparison gives `True`.

```python
print(0.1 + 0.2)
# 0.30000000000000004
print(round(0.1 + 0.2, 2))
# 0.3
print(0.1 + 0.2 <= 0.3 + 1e-9)
# True
```

### Truthiness

`bool(x)` is `False` for `0`, `0.0`, `""`, `None` and the empty tuple `()`. These values are called
**falsy**. It is `True` for almost every other value. Those values are called **truthy**.
Use `x is None` to test for a missing value.

```python
print(bool(0), bool(""), bool(None))
# False False False
print(bool(3), bool("false"))
# True True
```

### Sets

`set(group)` builds a set and keeps one copy of each value. `len()` counts the items.
`value in s` checks whether the value is in the set. `a & b` is the set of values in both
sets. `a | b` is the set of values in either set.

```python
tags = set(("a", "a", "b"))
print(len(tags))
# 2
print("a" in tags)
# True
print(tags & {"b", "c"})
# {'b'}
```

A set can only hold **hashable** values. A value is hashable when Python can compute a
fixed whole number from it, called its hash. Python uses the hash to find the value in the
set quickly. Numbers, strings, `True`, `False` and `None` are hashable. A tuple is hashable
when every item in it is hashable. A set is not hashable, so a set cannot be an item of
another set. Trying it stops the program with
`TypeError: cannot use 'set' as a set element (unhashable type: 'set')`.

```python
pairs = set(((1, 2), (1, 2), (3, 4)))
print(len(pairs))
# 2
```

### Common mistakes

- `int("abc")` and `int("1.5")` stop the program with a `ValueError`. Text with a decimal point needs `float()`.
- `"tokens: " + 5` stops the program with a `TypeError`. Write `"tokens: " + str(5)`.
- `bool("false")` is `True` because the string is not empty. Compare the text with `"true"` instead.
- `0.1 + 0.2 == 0.3` is `False`. Compare floats with a tolerance.
- `{}` creates an empty dict, a different type that a later chapter covers. Write `set()` for an empty set.
'''

EXERCISES = [
    {
        "id": "data-types-s2",
        "title": "Text to number",
        "difficulty": 0,
        "lesson": r'''
            ## Types and conversion

            Every value in Python has a **type**. The type decides what you can do with the
            value. `type()` returns the type of a value. Python prints a type in the form
            `<class 'name'>`, where `name` is the name of the type.

            ```python
            print(type(512))
            # <class 'int'>
            print(type("512"))
            # <class 'str'>
            print(type(0.7))
            # <class 'float'>
            ```

            The main types are `int` (whole numbers), `float` (numbers with a decimal point),
            `str` (text), `bool` (`True` or `False`) and `NoneType` (the value `None`, which
            means "no value").

            `"512"` is a `str` because of the quotes. Text read from files, forms and settings
            is always a `str`. You cannot do maths with it until you convert it.

            **Type conversion**, also called **casting**, builds a new value of another type
            from a value. Each type has a conversion function with the same name as the type.

            ```python
            text = "0.25"
            number = float(text)
            print(number * 2)
            # 0.5
            ```

            `int()` and `float()` ignore spaces around the digits. `int()` needs text that
            holds a whole number. `int("abc")` stops the program with a `ValueError`.
        ''',
        "prompt": r'''
            Settings read from files arrive as text. Finish `to_int` so it turns that text into a
            whole number.

            **Write:** replace `___` in `to_int(text)`

            - `text`: a string holding a whole number, maybe with spaces around it, e.g. `" 42 "`
            - **Returns:** that number as an `int` (not a string), e.g. `42`

            **Rules**
            - The result must be of type `int`: `512`, not `"512"`.
            - Spaces around the digits must not matter.

            **Examples**
            ```python
            to_int("512")    # returns 512
            to_int(" 42 ")   # returns 42
            ```

            Reminder: each type has a conversion function with the same name as the type.
        ''',
        "starter": r'''
            def to_int(text):
                return ___(text)
        ''',
        "tests": r'''
            from solution import to_int

            def test_text_512_becomes_int_512():
                got = to_int("512")
                assert got == 512 and type(got) is int, f"to_int('512') returned {got!r}"

            def test_spaces_around_digits_are_ignored():
                got = to_int(" 42 ")
                assert got == 42 and type(got) is int, f"to_int(' 42 ') returned {got!r}"
        ''',
        "solution": r'''
            def to_int(text):
                return int(text)
        ''',
        "hints": [
            "Each type has a function with the same name that converts a value into that type.",
            "You want a whole number, so use the conversion function named after that type.",
            "Replace ___ with int, so the line reads return int(text).",
        ],
    },
    {
        "id": "data-types-s3",
        "title": "Fix: text plus number",
        "difficulty": 0,
        "lesson": r'''
            ## Joining text and numbers

            The `+` operator does two different things. With two numbers, it adds them. With
            two strings, it joins them into one string.

            ```python
            print(2 + 3)
            # 5
            print("2" + "3")
            # 23
            ```

            With a string on one side and a number on the other, Python does neither. The
            program stops with a `TypeError`. A **TypeError** means that the operation does
            not work for a value of that type.

            ```text
            TypeError: can only concatenate str (not "int") to str
            ```

            To fix it, make both sides the same type. `str()` returns the text form of any
            value: a number, `True` or `None`.

            ```python
            price = 0.25
            line = "cost: " + str(price)
            print(line)
            # cost: 0.25
            ```

            `"cost: " + "price"` joins the word `price`, not the value `0.25`. Write the
            variable name without quotes.
        ''',
        "prompt": r'''
            `label(count)` builds a short text label for a token count, but it crashes with
            `TypeError: can only concatenate str (not "int") to str`. Find and fix the bug.

            **Write:** fix `label(count)`

            - `count`: an `int`, e.g. `5`
            - **Returns:** a string: `tokens: ` (with one space after the colon) followed by the number

            **Rules**
            - Return text, don't print it.
            - The number appears as plain digits, no extra spaces or punctuation.

            **Examples**
            ```python
            label(5)      # returns "tokens: 5"
            label(1200)   # returns "tokens: 1200"
            ```
        ''',
        "starter": r'''
            def label(count):
                return "tokens: " + count
        ''',
        "tests": r'''
            from solution import label

            def test_label_for_5_is_tokens_5():
                got = label(5)
                assert got == "tokens: 5", f"label(5) returned {got!r}"

            def test_label_for_1200_is_tokens_1200():
                got = label(1200)
                assert got == "tokens: 1200", f"label(1200) returned {got!r}"
        ''',
        "solution": r'''
            def label(count):
                return "tokens: " + str(count)
        ''',
        "hints": [
            "The error says + can only join a str to another str, and count is an int.",
            "Convert the number to text before joining it on.",
            "Wrap count in str(...) on the return line.",
        ],
    },
    {
        "id": "data-types-s6",
        "title": "Clean up an answer",
        "difficulty": 0,
        "lesson": r'''
            ## String methods

            A **method** is a function that belongs to a value. You call it with a dot after
            the value: `value.method()`. `.lower()` returns the text in lowercase and
            `.upper()` returns it in uppercase.

            ```python
            city = "Paris"
            print(city.lower())
            # paris
            print(city.upper())
            # PARIS
            ```

            `.strip()` returns the text without the spaces and newlines at both ends. Inside a
            string, `\n` is the **newline** character: the character that ends a line. It counts
            as one character. Spaces in the middle stay.

            Strings are **immutable**: a string cannot change after it is created. Each method
            returns a new string and the original stays the same. The result is a string, so
            you can call the next method on it directly. Python runs the calls left to right.

            Step through the program and compare `raw` with `trimmed`.

            ```diagram
            {"type": "trace", "title": "strip() and upper() return new strings", "code": ["raw = \"  Paris\\n\"", "print(len(raw))", "trimmed = raw.strip()", "print(len(trimmed))", "shout = trimmed.upper()", "print(shout)", "print(raw.strip().upper())", "print(len(raw))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"raw": "'  Paris\\n'"}, "out": ""},
              {"line": 3, "vars": {"raw": "'  Paris\\n'"}, "out": "8\n"},
              {"line": 4, "vars": {"raw": "'  Paris\\n'", "trimmed": "'Paris'"}, "out": "8\n"},
              {"line": 5, "vars": {"raw": "'  Paris\\n'", "trimmed": "'Paris'"}, "out": "8\n5\n"},
              {"line": 6, "vars": {"raw": "'  Paris\\n'", "trimmed": "'Paris'", "shout": "'PARIS'"}, "out": "8\n5\n"},
              {"line": 7, "vars": {"raw": "'  Paris\\n'", "trimmed": "'Paris'", "shout": "'PARIS'"}, "out": "8\n5\nPARIS\n"},
              {"line": 8, "vars": {"raw": "'  Paris\\n'", "trimmed": "'Paris'", "shout": "'PARIS'"}, "out": "8\n5\nPARIS\nPARIS\n"},
              {"line": null, "vars": {"raw": "'  Paris\\n'", "trimmed": "'Paris'", "shout": "'PARIS'"}, "out": "8\n5\nPARIS\nPARIS\n8\n"}
            ]}
            ```

            `raw.strip` without `()` does not call the method. Always write the parentheses.
        ''',
        "prompt": r'''
            Model answers often come back with stray spaces, a trailing newline or random
            capitals. Before comparing them, you clean them up.

            **Write:** `normalize(answer)`

            - `answer`: a string, e.g. `"  YES\n"`
            - **Returns:** a string: `answer` with spaces/newlines removed from both ends and
              all letters lowercase, e.g. `"yes"`

            **Rules**
            - Spaces in the middle stay: `" New York "` gives `"new york"`.
            - An empty string gives `""`.

            **Examples**
            ```python
            normalize("  YES\n")       # returns "yes"
            normalize("Paris")         # returns "paris"
            normalize(" New York ")    # returns "new york"
            normalize("")              # returns ""
            ```
        ''',
        "starter": r'''
            def normalize(answer):
                ...
        ''',
        "tests": r'''
            from solution import normalize

            def test_strips_and_lowercases():
                got = normalize("  YES\n")
                assert got == "yes", f"normalize('  YES\\n') returned {got!r}"

            def test_lowercases_clean_text():
                got = normalize("Paris")
                assert got == "paris", f"normalize('Paris') returned {got!r}"

            def test_keeps_spaces_in_the_middle():
                got = normalize(" New York ")
                assert got == "new york", f"normalize(' New York ') returned {got!r}"

            def test_empty_text_stays_empty():
                got = normalize("")
                assert got == "", f"normalize('') returned {got!r}"
        ''',
        "solution": r'''
            def normalize(answer):
                return answer.strip().lower()
        ''',
        "hints": [
            "Strings have methods for trimming the ends and for changing letter case.",
            "Trim the text first, then make it lowercase, and return the result.",
            "Return answer, then .strip(), then .lower(), chained in one expression.",
        ],
    },
    {
        "id": "data-types-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Type names and truthiness

            `type(x)` prints as `<class 'int'>`. Add `.__name__` (two underscores on each
            side) to get only the name of the type, as a string.

            ```python
            print(type(0.5).__name__)
            # float
            print(type(True).__name__)
            # bool
            ```

            `bool()` converts any value to `True` or `False`. A value that converts to `False`
            is **falsy**. The falsy values you know so far are `0`, `0.0`, `""` and `None`.
            A value that converts to `True` is **truthy**. Every other number and every
            non-empty string is truthy. This rule is called **truthiness**.

            ```python
            print(bool(0.0), bool(""), bool(None))
            # False False False
            print(bool(3), bool("no"))
            # True True
            ```

            `bool("false")` is `True`. The string holds five characters, so it is not empty.
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            print(type(42).__name__)
            print(type("42").__name__)
            print(int("7") + 3)
            print("7" + "3")
            print(bool(0), bool("hi"))
        ''',
        "solution": r'''
            int
            str
            10
            73
            False True
        ''',
        "explanation": r'''
            `42` is an `int` and `"42"` in quotes is a `str`, so the first two lines print
            those type names. `int("7")` returns the number `7`, and `7 + 3` is `10`.
            `"7" + "3"` joins two strings into `"73"`. `bool(0)` is `False` because `0` is
            falsy. `bool("hi")` is `True` because a non-empty string is truthy.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Quotes make a value a str, even if it contains digits.",
            "type(x).__name__ prints the type's name. + adds numbers but joins strings. bool(0) is False.",
            "Line 1: the type of a whole number. Line 2: the type of text. Line 3: 7 + 3. Line 4: the two characters joined together. Line 5: two bools separated by a space.",
        ],
    },
    {
        "id": "data-types-s5",
        "title": "Missing or zero?",
        "difficulty": 0,
        "lesson": r'''
            ## None

            `None` is a value that means "no value". It is the only value of the type
            `NoneType`. A function that ends without a `return` returns `None`.

            `None` is not `0` and it is not `""`. `0` is a number and `""` is a string with no
            characters. `retries = 0` says that the number of retries is zero. `retries = None`
            says that no number was set.

            `0` and `None` are both falsy, so `bool()` gives `False` for both. To test for a
            missing value, write `is None`. It gives `True` only when the value is `None`.

            ```python
            retries = 0
            print(bool(retries), retries is None)
            # False False
            setting = None
            print(bool(setting), setting is None)
            # False True
            ```

            The result of `is None` is already a `bool`. You can store it or return it directly.

            `==` compares two values and gives `True` when they are equal. `value == None` also works, but `value is None` is the
            standard way to write it.
        ''',
        "prompt": r'''
            An optional setting can be *missing* (`None`) or set to an "empty-looking" value like
            `0`. Those are different things, and your function must tell them apart.

            **Write:** `is_missing(value)`

            - `value`: any value, e.g. `None`, `0`, `""`, `512`
            - **Returns:** a `bool`: `True` if `value` is `None`, otherwise `False`

            **Rules**
            - Only `None` is missing: return `True` for it.
            - `0`, `0.0`, `""` and `False` are **not** missing: return `False` for them.
            - Any normal value (like `512`) is not missing: return `False`.
            - Return the actual `True`/`False` values, not text like `"True"`.

            **Examples**
            ```python
            is_missing(None)   # returns True
            is_missing(0)      # returns False
            is_missing("")     # returns False
            is_missing(512)    # returns False
            ```
        ''',
        "starter": r'''
            def is_missing(value):
                ...
        ''',
        "tests": r'''
            from solution import is_missing

            def test_none_returns_true():
                assert is_missing(None) is True, f"is_missing(None) returned {is_missing(None)!r}"

            def test_zero_empty_text_and_false_return_false():
                for v in (0, "", False, 0.0):
                    got = is_missing(v)
                    assert got is False, f"is_missing({v!r}) returned {got!r}"

            def test_normal_value_returns_false():
                assert is_missing(512) is False, f"is_missing(512) returned {is_missing(512)!r}"
        ''',
        "solution": r'''
            def is_missing(value):
                return value is None
        ''',
        "hints": [
            "The lesson shows a way to test for None that does not treat 0 or empty text as missing.",
            "Return the result of checking whether value is None. That check already gives True or False.",
            "Write a single return line: value, then the keyword is, then None. Do not use bool() or not here.",
        ],
    },
    {
        "id": "data-types-s4",
        "title": "Average tokens",
        "difficulty": 0,
        "lesson": r'''
            ## Division and rounding

            The `/` operator divides one number by another. The result is always a `float`,
            even when the division is exact.

            ```python
            print(9 / 2)
            # 4.5
            print(9 / 3)
            # 3.0
            print(8 / 3)
            # 2.6666666666666665
            ```

            `round(number, places)` returns the number rounded to `places` **decimal places**:
            the digits after the decimal point.

            ```python
            print(round(8 / 3, 2))
            # 2.67
            print(round(20 / 3, 2))
            # 6.67
            ```

            Divide first, then round the result. Rounding the inputs first gives a different
            number: `round(7.4 / 2.6, 1)` is `2.8`, but `round(7.4) / round(2.6)` is `7 / 3`,
            which is about `2.33`.
        ''',
        "prompt": r'''
            Work out the average number of tokens per message.

            **Write:** `average_tokens(total, count)`

            - `total`: an `int`, the total number of tokens, e.g. `10`
            - `count`: an `int` greater than 0, the number of messages, e.g. `4`
            - **Returns:** a `float`: `total` divided by `count`, **rounded to 1 decimal place**

            **Rules**
            - Use normal division (the result can have decimals).
            - Round the result to exactly 1 decimal place (`3.333...` becomes `3.3`, `0.666...` becomes `0.7`).

            **Examples**
            ```python
            average_tokens(10, 4)    # returns 2.5
            average_tokens(10, 3)    # returns 3.3
            average_tokens(2, 3)     # returns 0.7
            ```
        ''',
        "starter": r'''
            def average_tokens(total, count):
                ...
        ''',
        "tests": r'''
            from solution import average_tokens

            def test_10_divided_by_4_is_2_5():
                got = average_tokens(10, 4)
                assert got == 2.5, f"average_tokens(10, 4) returned {got!r}"

            def test_result_is_rounded_to_one_decimal():
                got = average_tokens(10, 3)
                assert got == 3.3, f"average_tokens(10, 3) returned {got!r}"
                got = average_tokens(2, 3)
                assert got == 0.7, f"average_tokens(2, 3) returned {got!r}"
        ''',
        "solution": r'''
            def average_tokens(total, count):
                return round(total / count, 1)
        ''',
        "hints": [
            "Use normal division and the built-in that rounds a number.",
            "Divide total by count with /, then round that result to 1 decimal place.",
            "Return round( total / count , 1 ). The second argument of round is the number of decimals.",
        ],
    },
    {
        "id": "data-types-1",
        "title": "Name the type",
        "difficulty": 1,
        "lesson": r'''
            ## Type names in text

            `type(x).__name__` is a `str`. You can join it to other strings with `+`.

            ```python
            value = True
            print("type: " + type(value).__name__)
            # type: bool
            ```

            `str()` returns the text form of any value. A string passed to `str()` comes back
            unchanged, with no quotes added.

            ```python
            print(str(0.7) + "!")
            # 0.7!
            print(str(None), str((1, 2)), str("42"))
            # None (1, 2) 42
            ```

            Joining strings with `+` is called **string concatenation**. Every piece must be
            a `str`.

            `type(x)` on its own is not a string. `"is " + type(x)` stops the program with a
            `TypeError`. Add `.__name__` to get the name as a string.
        ''',
        "prompt": r'''
            When debugging API data it helps to see a value together with its type.

            **Write:** `describe_value(value)`

            - `value`: any value, e.g. `512`, `0.7`, `"42"`, `True`, `None`, `(1, 2)`
            - **Returns:** a string: the value as text, then ` is ` (a space, the word is, a space),
              then the **name** of the value's type (like `int`, not `<class 'int'>`)

            **Rules**
            - Return a string, don't print it.
            - The value part is the value converted to text: a string like `"42"` shows as `42`
              with no quotes.
            - The type part is just the type's name: `int`, `float`, `str`, `bool`, `NoneType`, `tuple`...
            - It must work for any type, not only the ones in the examples.

            **Examples**
            ```python
            describe_value(512)     # returns "512 is int"
            describe_value(0.7)     # returns "0.7 is float"
            describe_value("42")    # returns "42 is str"
            describe_value(True)    # returns "True is bool"
            describe_value(None)    # returns "None is NoneType"
            describe_value((1, 2))  # returns "(1, 2) is tuple"
            ```
        ''',
        "starter": r'''
            def describe_value(value):
                ...
        ''',
        "tests": r'''
            from solution import describe_value

            def check(value, expected):
                got = describe_value(value)
                assert got == expected, f"describe_value({value!r}) returned {got!r}"

            def test_returns_a_string():
                got = describe_value(512)
                assert isinstance(got, str), f"describe_value(512) returned {got!r}, which is not a string"

            def test_int_and_float_names():
                check(512, "512 is int")
                check(0.7, "0.7 is float")

            def test_text_that_looks_like_a_number_is_str():
                check("42", "42 is str")

            def test_bool_and_nonetype_names():
                check(True, "True is bool")
                check(None, "None is NoneType")

            def test_works_for_any_type_like_tuple():
                check((1, 2), "(1, 2) is tuple")
        ''',
        "solution": r'''
            def describe_value(value):
                return str(value) + " is " + type(value).__name__
        ''',
        "hints": [
            "You need two pieces of text: the value turned into text, and the type's name as text. Both are in the lesson.",
            "str(value) turns the value into text. type(value) alone is a type object, not text; add .__name__ to get the plain name. Then join the pieces with +.",
            "1) Convert value to text with str(). 2) Join on the text \" is \" (spaces on both sides). 3) Join on type(value).__name__. 4) Return the result.",
        ],
    },
    {
        "id": "data-types-2",
        "title": "Add up string numbers",
        "difficulty": 1,
        "lesson": r'''
            ## Convert first, then add

            Data read from files, form fields and other programs is text. It often
            has spaces around it or a newline at the end. `"42\n"` is the characters `42`
            followed by a newline. **Parsing** means turning raw text into values of the
            right type.

            `int()` and `float()` ignore spaces and newlines around the digits.

            ```python
            print(int(" 7 ") * 2)
            # 14
            print(float(" 0.5\n"))
            # 0.5
            ```

            The order matters. `+` on two strings joins them. Convert each string to a number
            first, then do the maths.

            ```python
            print(int("12" + "3"))
            # 123
            print(int("12") + int("3"))
            # 15
            ```

            Step through the program to see what `+` does before and after the conversion.

            ```diagram
            {"type": "trace", "title": "Joining strings versus adding numbers", "code": ["input_text = \" 120 \"", "output_text = \"30\\n\"", "joined = input_text + output_text", "print(len(joined))", "a = int(input_text)", "b = int(output_text)", "total = a + b", "print(total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"input_text": "' 120 '"}, "out": ""},
              {"line": 3, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'"}, "out": ""},
              {"line": 4, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'", "joined": "' 120 30\\n'"}, "out": ""},
              {"line": 5, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'", "joined": "' 120 30\\n'"}, "out": "8\n"},
              {"line": 6, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'", "joined": "' 120 30\\n'", "a": "120"}, "out": "8\n"},
              {"line": 7, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'", "joined": "' 120 30\\n'", "a": "120", "b": "30"}, "out": "8\n"},
              {"line": 8, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'", "joined": "' 120 30\\n'", "a": "120", "b": "30", "total": "150"}, "out": "8\n"},
              {"line": null, "vars": {"input_text": "' 120 '", "output_text": "'30\\n'", "joined": "' 120 30\\n'", "a": "120", "b": "30", "total": "150"}, "out": "8\n150\n"}
            ]}
            ```

            `int("1.5")` stops the program with a `ValueError`. Text with a decimal point
            needs `float()`.
        ''',
        "prompt": r'''
            A usage report gives token counts as **text**, sometimes with spaces or a trailing
            newline. Add them up as numbers.

            **Write:** `total_tokens(prompt_text, completion_text)`

            - `prompt_text`: a string holding a whole number, e.g. `"120"` or `" 1000 "`
            - `completion_text`: a string holding a whole number, e.g. `"30"` or `"24\n"`
            - **Returns:** the sum of the two numbers as an `int`

            **Rules**
            - Add them as numbers: `"120"` and `"30"` give `150`, not `"12030"`.
            - The result must be of type `int` (not a string or a float).
            - Spaces and newlines around the digits must not matter.

            **Examples**
            ```python
            total_tokens("120", "30")       # returns 150
            total_tokens(" 1000 ", "24\n")  # returns 1024
            total_tokens("0", "0")          # returns 0
            ```
        ''',
        "starter": r'''
            def total_tokens(prompt_text, completion_text):
                ...
        ''',
        "tests": r'''
            from solution import total_tokens

            def test_adds_the_numbers_not_the_text():
                got = total_tokens("120", "30")
                assert got == 150, f"total_tokens('120', '30') returned {got!r}"

            def test_result_is_an_int():
                got = total_tokens("1", "2")
                assert type(got) is int, f"total_tokens('1', '2') returned {got!r} ({type(got).__name__})"

            def test_ignores_spaces_and_newlines():
                got = total_tokens(" 1000 ", "24\n")
                assert got == 1024, f"got {got!r}"

            def test_zero_plus_zero_is_zero():
                assert total_tokens("0", "0") == 0
        ''',
        "solution": r'''
            def total_tokens(prompt_text, completion_text):
                return int(prompt_text) + int(completion_text)
        ''',
        "hints": [
            "The inputs are strings. What does + do to two strings?",
            "Convert each piece of text to a whole number first, then add the numbers.",
            "1) int(prompt_text). 2) int(completion_text). 3) Return the two added together. int() already ignores surrounding spaces and newlines.",
        ],
    },
    {
        "id": "data-types-7",
        "title": "Does it fit?",
        "difficulty": 1,
        "lesson": r'''
            ## Comparisons

            A **comparison** checks one value against another and gives a `bool`: `True` or
            `False`. These two values are called **booleans**.

            ```python
            tokens = 1200
            print(tokens > 1000)
            # True
            print(tokens == 1200, tokens != 1200)
            # True False
            print(tokens <= 1199)
            # False
            ```

            There are six comparison operators. `==` means equal and `!=` means not equal.
            `<` means less than and `<=` means less than or equal. `>` means greater than and
            `>=` means greater than or equal.

            An **expression** is a piece of code that produces a value. An expression that
            produces a bool is a **boolean expression**. Its result is a normal value, so you
            can store it or return it.

            ```python
            def is_long(tokens):
                return tokens > 1000

            print(is_long(50))
            # False
            ```

            `=` assigns a value to a name and `==` compares two values. Floats are not exact:
            `0.1 + 0.2 == 0.3` is `False`. Use whole numbers for exact checks.
        ''',
        "prompt": r'''
            Before a request, check that the prompt plus the room reserved for the answer fits
            in the model's context window.

            **Write:** `fits_context(prompt_tokens, output_tokens, window)`

            - `prompt_tokens`: tokens in the prompt, an int, e.g. `1000`
            - `output_tokens`: tokens reserved for the answer, an int, e.g. `500`
            - `window`: the context window size, an int, e.g. `4096`
            - **Returns:** a `bool`: `True` if the two token counts added together are **not more than** `window`, otherwise `False`

            **Rules**
            - Exactly filling the window fits (`True`).
            - Return the bool values `True`/`False`, not text like `"True"`.

            **Examples**
            ```python
            fits_context(1000, 500, 4096)   # returns True
            fits_context(3000, 96, 3096)    # returns True  (exactly full)
            fits_context(4000, 500, 4096)   # returns False
            ```
        ''',
        "starter": r'''
            def fits_context(prompt_tokens, output_tokens, window):
                ...
        ''',
        "tests": r'''
            from solution import fits_context

            def test_small_request_fits():
                got = fits_context(1000, 500, 4096)
                assert got is True, f"fits_context(1000, 500, 4096) returned {got!r}"

            def test_exactly_full_window_fits():
                got = fits_context(3000, 96, 3096)
                assert got is True, f"fits_context(3000, 96, 3096) returned {got!r}"

            def test_too_big_request_does_not_fit():
                got = fits_context(4000, 500, 4096)
                assert got is False, f"fits_context(4000, 500, 4096) returned {got!r}"
                got = fits_context(0, 4097, 4096)
                assert got is False, f"fits_context(0, 4097, 4096) returned {got!r}"
        ''',
        "solution": r'''
            def fits_context(prompt_tokens, output_tokens, window):
                return prompt_tokens + output_tokens <= window
        ''',
        "hints": [
            "A comparison already produces True or False, so you can return it directly.",
            "Add the two token counts, then compare the sum with the window. 'Not more than' includes being equal.",
            "Return: prompt_tokens + output_tokens, then the less-than-or-equal operator <=, then window.",
        ],
    },
    {
        "id": "data-types-8",
        "title": "Full pages and leftovers",
        "difficulty": 1,
        "lesson": r'''
            ## Floor division and remainder

            17 divided by 5 is 3 with 2 left over, because `5 * 3 + 2` is `17`. Python has
            one operator for each part of that result.

            ```python
            print(17 // 5)
            # 3
            print(17 % 5)
            # 2
            print(17 / 5)
            # 3.4
            ```

            `//` is **floor division**: it divides and rounds down to a whole number. With two
            ints, the result is an `int`. `%` is the **modulo** operator: it gives the
            remainder, the amount left over after floor division. `/` is normal division and
            always gives a float.

            When the division is exact, the remainder is `0`: `20 % 5` is `0`. When the first
            number is smaller than the second, `//` gives `0` and `%` gives the first number:
            `3 // 5` is `0` and `3 % 5` is `3`.

            `int(17 / 5)` is also `3`, but `/` produces a float and floats are not exact for
            very large numbers. `//` on two ints stays exact.

            ```python
            big = 1000000000000000001
            print(big // 1)
            # 1000000000000000001
            print(int(big / 1))
            # 1000000000000000000
            ```
        ''',
        "prompt": r'''
            A dashboard lists documents, a fixed number per page. Work out how many pages are
            completely full and how many documents are left for the last, partial page.

            **Write:** `split_into_pages(total, per_page)`

            - `total`: number of documents, an int, e.g. `250`
            - `per_page`: documents per page, an int greater than 0, e.g. `100`
            - **Returns:** a tuple of two ints `(full_pages, leftover)`

            **Rules**
            - Both values must be of type `int` (not `float`).
            - If it divides exactly, `leftover` is `0`.
            - If `total` is smaller than `per_page`, there are `0` full pages.

            **Examples**
            ```python
            split_into_pages(250, 100)   # returns (2, 50)
            split_into_pages(300, 100)   # returns (3, 0)
            split_into_pages(5, 100)     # returns (0, 5)
            ```
        ''',
        "starter": r'''
            def split_into_pages(total, per_page):
                ...
        ''',
        "tests": r'''
            from solution import split_into_pages

            def check(total, per_page, expected):
                got = split_into_pages(total, per_page)
                assert got == expected and all(type(x) is int for x in got), (
                    f"split_into_pages({total}, {per_page}) returned {got!r}")

            def test_partial_last_page():
                check(250, 100, (2, 50))

            def test_exact_fit_has_no_leftover():
                check(300, 100, (3, 0))

            def test_fewer_than_one_page():
                check(5, 100, (0, 5))

            def test_values_are_ints():
                check(7, 2, (3, 1))
        ''',
        "solution": r'''
            def split_into_pages(total, per_page):
                return total // per_page, total % per_page
        ''',
        "hints": [
            "One operator gives how many whole times a number fits; another gives what is left.",
            "Use floor division for the full pages and the remainder operator for the leftover, then return both.",
            "Return total // per_page, a comma, then total % per_page.",
        ],
    },
    {
        "id": "data-types-9",
        "title": "Count unique tags",
        "difficulty": 1,
        "lesson": r'''
            ## Tuples and sets

            A **tuple** keeps every value you put in, in order, including repeated values. A
            **set** keeps one copy of each distinct value and has no order.

            ```python
            models = ("gpt-4o", "claude", "gpt-4o")
            print(len(models))
            # 3
            unique = set(models)
            print(len(unique))
            # 2
            print("claude" in unique)
            # True
            ```

            `set(group)` builds a set from a tuple and drops the duplicates. `len()` counts
            the items. `value in s` is a **membership test**: it gives `True` when the value
            is in the set and `False` when it is not.

            You can write a set directly with curly braces. `a & b` is the set of values that
            are in both sets. `a | b` is the set of values that are in either set.

            ```python
            a = {"rag", "llm"}
            b = {"llm", "eval"}
            print(a & b)
            # {'llm'}
            print(len(a | b))
            # 3
            ```

            Click an operator to see which values the result holds.

            ```diagram
            {"type": "set-ops", "title": "Tags in a and b", "a": {"name": "a", "items": ["rag", "llm"]}, "b": {"name": "b", "items": ["llm", "eval"]}}
            ```

            `{}` creates an empty dict, a different type that a later chapter covers. Write
            `set()` for an empty set.
        ''',
        "research": {
            "note": 'Read the short tutorial section on sets (what they are for and how to build one), then come back.',
            "links": [
                {"title": 'Sets - Python tutorial', "url": 'https://docs.python.org/3/tutorial/datastructures.html#sets'},
            ],
        },
        "prompt": r'''
            Documents in a RAG index carry tags, and the same tag is often repeated. How many
            **different** tags are there?

            **Write:** `count_unique(tags)`

            - `tags`: a tuple of strings, e.g. `("rag", "llm", "rag")`
            - **Returns:** an int: the number of distinct tags, e.g. `2`

            **Rules**
            - A tag repeated several times counts once.
            - Capitals matter: `"RAG"` and `"rag"` are different tags.
            - An empty tuple `()` gives `0`.

            **Examples**
            ```python
            count_unique(("rag", "llm", "rag"))   # returns 2
            count_unique(("a", "a", "a"))         # returns 1
            count_unique(("RAG", "rag"))          # returns 2
            count_unique(())                      # returns 0
            ```
        ''',
        "starter": r'''
            def count_unique(tags):
                ...
        ''',
        "tests": r'''
            from solution import count_unique

            def test_repeated_tag_counts_once():
                got = count_unique(("rag", "llm", "rag"))
                assert got == 2, f"count_unique(('rag', 'llm', 'rag')) returned {got!r}"
                got = count_unique(("a", "a", "a"))
                assert got == 1, f"count_unique(('a', 'a', 'a')) returned {got!r}"

            def test_capitals_make_different_tags():
                got = count_unique(("RAG", "rag"))
                assert got == 2, f"count_unique(('RAG', 'rag')) returned {got!r}"

            def test_empty_tuple_gives_zero():
                got = count_unique(())
                assert got == 0, f"count_unique(()) returned {got!r}"
        ''',
        "solution": r'''
            def count_unique(tags):
                return len(set(tags))
        ''',
        "hints": [
            "One of the types in this chapter keeps only one copy of each value.",
            "Build that kind of group from the tuple, then count how many items it has.",
            "Return len of set(tags).",
        ],
    },
    {
        "id": "data-types-3",
        "title": "Parse request settings",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Values read from `.env` files and CLI flags always arrive as **text**, often with stray
            spaces or newlines. Convert three request settings to their real types.

            **Write:** `parse_settings(temperature_text, max_tokens_text, stream_text)`

            - `temperature_text`: text holding a number, e.g. `" 0.7 "` or `"1"`
            - `max_tokens_text`: text holding a whole number, e.g. `"512\n"`
            - `stream_text`: text such as `"true"`, `" TRUE "`, `"false"`, `"yes"` or `""`
            - **Returns:** a tuple of 3 values `(temperature, max_tokens, stream)`

            **Rules**
            - `temperature` is always a `float`, even for `"1"` (gives `1.0`) or `"0"` (gives `0.0`).
            - `max_tokens` is an `int`.
            - `stream` is the bool `True` only if `stream_text` is the word `true` in any letter case
              (`"true"`, `"TRUE"`, `"True"`...), ignoring spaces/newlines around it.
            - Anything else for `stream` (`"false"`, `" False\n"`, `"yes"`, `""`) gives `False`.
            - Spaces and newlines around any of the three texts must not matter.

            **Examples**
            ```python
            parse_settings(" 0.7 ", "512\n", " TRUE ")   # returns (0.7, 512, True)
            parse_settings("1", "64", "false")           # returns (1.0, 64, False)
            parse_settings("0", "10", "yes")             # returns (0.0, 10, False)
            parse_settings("0", "10", "")                # returns (0.0, 10, False)
            ```
        ''',
        "starter": r'''
            def parse_settings(temperature_text, max_tokens_text, stream_text):
                ...
        ''',
        "tests": r'''
            from solution import parse_settings

            def check(args, expected):
                got = parse_settings(*args)
                assert isinstance(got, tuple) and len(got) == 3, f"parse_settings{args!r} returned {got!r}"
                for g, e, name in zip(got, expected, ("temperature", "max_tokens", "stream")):
                    assert g == e and type(g) is type(e), (
                        f"parse_settings{args!r}: {name} was {g!r} ({type(g).__name__})")

            def test_messy_spaces_and_uppercase_true():
                check((" 0.7 ", "512\n", " TRUE "), (0.7, 512, True))

            def test_temperature_is_always_float():
                check(("1", "64", "true"), (1.0, 64, True))

            def test_text_false_gives_false():
                check(("0.2", "64", "false"), (0.2, 64, False))
                check(("0.2", "64", " False\n"), (0.2, 64, False))

            def test_any_other_text_gives_false():
                check(("0", "10", "yes"), (0.0, 10, False))
                check(("0", "10", ""), (0.0, 10, False))
        ''',
        "solution": r'''
            def parse_settings(temperature_text, max_tokens_text, stream_text):
                temperature = float(temperature_text)
                max_tokens = int(max_tokens_text)
                stream = stream_text.strip().lower() == "true"
                return temperature, max_tokens, stream
        ''',
        "hints": [
            "Use the conversion functions for the numbers. Careful: bool(\"false\") is True, because any non-empty text is truthy.",
            "Convert the first two with float() and int(). For stream, clean the text (strip, lowercase) and compare it with \"true\": the comparison itself is the bool you need.",
            "1) temperature = float(...). 2) max_tokens = int(...). 3) stream = the stripped, lowercased text == \"true\". 4) Return the three names separated by commas.",
        ],
    },
    {
        "id": "data-types-4",
        "title": "Budget with floats",
        "difficulty": 2,
        "research": {
            "note": "Floats can't store most decimals exactly. Read the short tutorial page on floating-point arithmetic to see why 0.1 + 0.2 is not exactly 0.3, then come back.",
            "links": [
                {"title": 'Floating-point arithmetic: issues and limitations - Python tutorial', "url": 'https://docs.python.org/3/tutorial/floatingpoint.html'},
            ],
        },
        "prompt": r'''
            A request has three costs in dollars: prompt, output and tool calls. Report the total
            and whether it fits the budget.

            **Write:** `check_budget(prompt_cost, output_cost, tool_cost, budget)`

            - `prompt_cost`, `output_cost`, `tool_cost`: `float` costs in dollars, e.g. `0.1`
            - `budget`: the maximum allowed total, a number, e.g. `0.3`
            - **Returns:** a tuple `(total, within)`

            **Rules**
            - `total` is the sum of the three costs, **rounded to 6 decimal places**
              (`0.1 + 0.1 + 0.1` gives `0.3`, `0.0000014 + 0.0000027` gives `4e-06`).
            - `within` is the bool `True` if the sum does not exceed `budget`, otherwise `False`.
            - Floating-point noise must not cause a false "over budget": a sum that is above the
              budget by at most `1e-9` (0.000000001) still counts as within.
            - Decide `within` from the **unrounded** sum: a sum of `0.1000004` is over a `0.1`
              budget even though its rounded total is `0.1`.
            - Anything clearly above the budget is over, even by a little (`0.3001` vs `0.3`).

            **Examples**
            ```python
            check_budget(0.1, 0.1, 0.1, 0.3)        # returns (0.3, True)
            check_budget(0.25, 0.5, 0.0, 0.7)       # returns (0.75, False)
            check_budget(0.3, 0.0001, 0.0, 0.3)     # returns (0.3001, False)
            check_budget(0.1, 0.0000004, 0.0, 0.1)  # returns (0.1, False)
            ```
        ''',
        "starter": r'''
            def check_budget(prompt_cost, output_cost, tool_cost, budget):
                ...
        ''',
        "tests": r'''
            from solution import check_budget

            def test_tiny_float_noise_counts_as_within_budget():
                total, within = check_budget(0.1, 0.1, 0.1, 0.3)
                assert within is True, "0.1 + 0.1 + 0.1 should count as within a 0.3 budget"

            def test_total_is_rounded_to_6_decimals():
                total, _ = check_budget(0.1, 0.1, 0.1, 0.3)
                assert total == 0.3, f"total was {total!r}"
                total, _ = check_budget(0.1, 0.2, 0.0, 1)
                assert total == 0.3, f"total was {total!r}"
                total, _ = check_budget(0.0000014, 0.0000027, 0.0, 1)
                assert total == 0.000004, f"total was {total!r}"

            def test_over_budget_returns_false():
                assert check_budget(0.25, 0.5, 0.0, 0.7) == (0.75, False)

            def test_slightly_over_budget_is_still_over():
                total, within = check_budget(0.3, 0.0001, 0.0, 0.3)
                assert within is False, "0.3001 exceeds a 0.3 budget"

            def test_within_uses_unrounded_sum():
                total, within = check_budget(0.1, 0.0000004, 0.0, 0.1)
                assert within is False, "0.1000004 exceeds a 0.1 budget even though it rounds to 0.1"
        ''',
        "solution": r'''
            def check_budget(prompt_cost, output_cost, tool_cost, budget):
                raw = prompt_cost + output_cost + tool_cost
                return round(raw, 6), raw <= budget + 1e-9
        ''',
        "hints": [
            "round(x, 6) rounds; a comparison like a <= b is already a bool; floats need a small tolerance.",
            "Add the three costs once. Round that for the returned total, but decide 'within' by comparing the raw (unrounded) sum with the budget plus a tiny tolerance.",
            "1) raw = the three costs added. 2) total = round(raw, 6). 3) within = raw <= budget + 1e-9. 4) Return total and within, separated by a comma.",
        ],
    },
    {
        "id": "data-types-5",
        "title": "Tag overlap",
        "difficulty": 3,
        "prompt": r'''
            Two documents in a RAG index each have a tuple of tags (possibly with repeats). Measure
            how similar their tags are with an **overlap score**:

            *number of distinct tags they share* / *number of distinct tags in either*

            **Write:** `overlap(tags_a, tags_b)`

            - `tags_a`: a tuple of strings, e.g. `("rag", "llm", "rag")`
            - `tags_b`: a tuple of strings, e.g. `("llm", "eval")`
            - **Returns:** the score as a `float`, rounded to 3 decimal places

            **Rules**
            - Repeated tags count once (`("a", "a")` has 1 distinct tag).
            - No shared tags gives `0.0`; that includes one tuple being empty.
            - If both tuples are empty, return `0.0` (it must not crash).
            - The result is always a `float` (`1.0`, not `1`).
            - Don't use `if` statements, `x if c else y` expressions, `for`/`while` loops or `try`
              (a check enforces this).

            **Examples**
            ```python
            overlap(("rag", "llm", "rag"), ("llm", "eval"))   # returns 0.333  (1 shared / 3 total)
            overlap(("x", "x", "y"), ("y", "y"))              # returns 0.5
            overlap(("a",), ("a", "a"))                       # returns 1.0
            overlap(("a", "b"), ("c",))                       # returns 0.0
            overlap((), ())                                   # returns 0.0
            ```
        ''',
        "starter": r'''
            def overlap(tags_a, tags_b):
                ...
        ''',
        "tests": r'''
            from solution import overlap

            def check(a, b, expected):
                got = overlap(a, b)
                assert got == expected and type(got) is float, f"overlap({a!r}, {b!r}) returned {got!r}"

            def test_one_shared_of_three_gives_0_333():
                check(("rag", "llm", "rag"), ("llm", "eval"), 0.333)

            def test_repeated_tags_count_once():
                check(("a",), ("a", "a"), 1.0)
                check(("x", "x", "y"), ("y", "y"), 0.5)

            def test_no_shared_tags_gives_zero():
                check(("a", "b"), ("c",), 0.0)

            def test_one_empty_tuple_gives_zero():
                check((), ("a", "b"), 0.0)

            def test_both_empty_does_not_crash():
                check((), (), 0.0)

            def test_no_if_loops_or_try():
                import ast
                tree = ast.parse(source())
                bad = [n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.IfExp, ast.For, ast.While, ast.Try))]
                assert not bad, "solve it without if, loops or try"
        ''',
        "solution": r'''
            def overlap(tags_a, tags_b):
                a = set(tags_a)
                b = set(tags_b)
                shared = len(a & b)
                total = len(a | b)
                return round(shared / max(total, 1), 3)
        ''',
        "hints": [
            "Sets drop repeats for you. The lesson shows & (in both) and | (in either). len() counts a set.",
            "Turn each tuple into a set, count the shared tags and the combined tags, divide, round. For the empty case, think about what to divide by so it can never be zero without using if.",
            "1) a = set(tags_a), b = set(tags_b). 2) shared = len of a & b. 3) total = len of a | b. 4) Divide shared by max(total, 1) (when total is 0, shared is 0 too). 5) Round to 3 places.",
        ],
    },
    {
        "id": "data-types-6",
        "title": "Batch planner",
        "difficulty": 3,
        "prompt": r'''
            You embed documents in batches. Plan how many API calls a job needs.

            **Write:** `plan_batches(total_text, batch_size)`

            - `total_text`: the number of documents as **text**, maybe with spaces/newline, e.g. `" 1000\n"`
            - `batch_size`: an `int` greater than 0, e.g. `100`
            - **Returns:** a tuple of three `int`s `(full_batches, leftover, batches_needed)`:
              - `full_batches`: how many completely full batches
              - `leftover`: how many documents are left over after the full batches
              - `batches_needed`: batches needed in total (a partial batch still needs a call)

            **Rules**
            - All three values must be of type `int` (not `float`).
            - Results must be exact even for huge totals like `10**18 + 1`: use whole-number
              arithmetic only (floats are not exact at that size).
            - A total of `0` needs `0` batches.
            - Don't use `if` statements or `x if c else y` expressions (a check enforces this).

            **Examples**
            ```python
            plan_batches("1050", 100)     # returns (10, 50, 11)
            plan_batches(" 1000\n", 100)  # returns (10, 0, 10)
            plan_batches("5", 100)        # returns (0, 5, 1)
            plan_batches("0", 100)        # returns (0, 0, 0)
            plan_batches("7", 1)          # returns (7, 0, 7)
            ```
        ''',
        "starter": r'''
            def plan_batches(total_text, batch_size):
                ...
        ''',
        "tests": r'''
            from solution import plan_batches

            def check(text, size, expected):
                got = plan_batches(text, size)
                assert got == expected and all(type(x) is int for x in got), (
                    f"plan_batches({text!r}, {size}) returned {got!r}")

            def test_partial_last_batch_needs_extra_call():
                check("1050", 100, (10, 50, 11))

            def test_exact_fit_with_spaces_in_text():
                check(" 1000\n", 100, (10, 0, 10))

            def test_fewer_than_one_batch_needs_one_call():
                check("5", 100, (0, 5, 1))

            def test_zero_documents_need_zero_batches():
                check("0", 100, (0, 0, 0))

            def test_batch_size_one():
                check("7", 1, (7, 0, 7))

            def test_huge_totals_are_exact_ints():
                check(str(10**18 + 1), 1, (10**18 + 1, 0, 10**18 + 1))
                check(str(10**18 + 1), 10, (10**17, 1, 10**17 + 1))

            def test_no_if_statements_or_expressions():
                import ast
                bad = [n for n in ast.walk(ast.parse(source())) if isinstance(n, (ast.If, ast.IfExp))]
                assert not bad, "solve it with arithmetic, without if"
        ''',
        "solution": r'''
            def plan_batches(total_text, batch_size):
                total = int(total_text)
                full_batches = total // batch_size
                leftover = total % batch_size
                batches_needed = (total + batch_size - 1) // batch_size
                return full_batches, leftover, batches_needed
        ''',
        "hints": [
            "// and % give the full batches and the leftover. The hard part is 'round up' division using only whole numbers.",
            "Rounding up a division means: add just enough to the total that any partial batch becomes a full one, then use // . Avoid / because it makes a float.",
            "1) total = int(total_text). 2) full = total // batch_size. 3) leftover = total % batch_size. 4) needed: add one less than batch_size to the total, then divide with //. 5) Return the three values.",
        ],
    },
]
