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
            ## The same digits, two different things

            A settings file contains the line `max_tokens=512`. Your program reads it and gets `"512"`,
            in quotes. That is text. Watch what happens when you try to calculate with it:

            ```python
            limit = "512"
            print(limit + limit)
            # 512512
            ```

            Not 1024. As you saw in the Basics chapter, `+` joins two strings. Python treats `"512"` and
            `512` as two different kinds of value, even though they look the same to you.

            Every value has a kind, and the kind is called its **type**. The built-in `type()` tells you
            the type of any value:

            ```python
            print(type(512))
            # <class 'int'>
            print(type("512"))
            # <class 'str'>
            print(type(0.7))
            # <class 'float'>
            ```

            An `int` is a whole number. A `str`, short for string, is text. A `float` is a number with a
            decimal point. The type decides what you can do with a value: you can multiply two `int`
            values, and you can join two `str` values.

            ```match
            `512` :: `int`, a whole number
            `"512"` :: `str`, text
            `0.7` :: `float`, a number with a decimal point
            ```

            ### From one type to another

            To calculate with text, turn it into a number first. Each type comes with a function that has
            the same name as the type and builds a value of that type:

            ```python
            text = "0.25"
            number = float(text)
            print(number * 2)
            # 0.5
            ```

            This is called **type conversion**. The text itself is not changed. The function hands back
            a new value of the other type.

            ```predict
            price = "4"
            print(price + price)
            print(int(price) + int(price))
            print(float(price))
            ---
            `price` is a string, so the first line joins two strings into `44`. `int(price)` is the number 4, and `4 + 4` is 8. `float(price)` is the same number with a decimal point, and Python shows it as `4.0`.
            ```

            `int()` and `float()` are forgiving about spaces: `int(" 42 ")` gives `42`. They are strict
            about everything else.

            ```quiz
            Which call stops the program with a `ValueError`?
            - [x] `int("12 apples")` :: Right. The text holds more than a number, and `int()` does not guess which part you meant.
            - [ ] `int(" 12 ")` :: Spaces around the digits are ignored, so this gives 12.
            - [ ] `float("12")` :: A whole number can become a float. The result is 12.0.
            ```

            **Watch out:** `int()` needs text that is a whole number and nothing else. `int("abc")` stops
            with `ValueError: invalid literal for int() with base 10: 'abc'`.

            **In short:** every value has a type, and `int()`, `float()` and `str()` build a new value of
            that type from another value.
        ''',
        "prompt": r'''
            Settings in a file are stored as text. When a program reads the line `max_tokens=512`, it gets
            the string `"512"`, sometimes with spaces around it. Before the program can calculate with the
            setting, the text has to become a number.

            **Your job:** finish `to_int(text)`. It is written except for one gap, marked `___`. The gap is
            the name of the function that does the conversion.

            **What goes in**
            - `text`: a string that holds a whole number, possibly with spaces around it, for example
              `" 42 "`

            **What comes out**
            - that number as an `int`, not as a string: `42` for the example value

            **Rules**
            - The result has the type `int`: `512`, not `"512"`.
            - Spaces around the digits make no difference.

            **Examples**
            ```python
            to_int("512")    # returns 512
            to_int(" 42 ")   # returns 42
            ```
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
            "Each type has a function that converts a value into that type.",
            "The function has the same name as the type it produces. Which type is a whole number?",
            "Replace the three underscores with the name of the type for whole numbers. The parentheses and `text` are already there.",
        ],
    },
    {
        "id": "data-types-s3",
        "title": "Fix: text plus number",
        "difficulty": 0,
        "lesson": r'''
            ## Why text and numbers will not join

            You want to build a label such as `tokens used: 5`. One part is text and the other is a
            number. The plus sign seems the obvious tool. But `+` already has two jobs: it adds numbers,
            and it joins strings. With a string on one side and a number on the other, Python cannot
            know which job you mean. Should `"5" + 5` be `10`, or `"55"`? It refuses to guess and stops
            with this message:

            ```text
            TypeError: can only concatenate str (not "int") to str
            ```

            Read it piece by piece. "Concatenate" is the word for joining strings that you met in the
            Basics chapter. So the message says: I can only join a `str` to a `str`, and you gave me an
            `int`. A `TypeError` always means that an operation does not work for a value of that type.

            The fix is to make both sides the same type. `str()` hands back the text form of any value:

            ```python
            price = 0.25
            line = "cost: " + str(price)
            print(line)
            # cost: 0.25
            ```

            ```predict
            print("3" + "4")
            print(int("3") + 4)
            print("3" + str(4))
            ---
            The first line joins two strings into `34`. In the second, `int("3")` is the number 3, and `3 + 4` is 7. In the third, `str(4)` is the string `"4"`, so the two strings are joined into `34` again.
            ```

            ```quiz
            `age` is the number `30`. Which expression builds the text `Age: 30`?
            - [x] `"Age: " + str(age)` :: Right. `str(age)` is the string `"30"`, and two strings can be joined.
            - [ ] `"Age: " + age` :: A string on one side and an `int` on the other. Python stops with a `TypeError`.
            - [ ] `"Age: " + "age"` :: The quotes turn `age` into three letters of text. The result is `Age: age`.
            ```

            **Watch out:** a variable name inside quotes is no longer a variable. `"cost: " + "price"`
            joins the word `price`, not the value that `price` stands for.

            **In short:** `+` needs both sides to have the same type, and `str(x)` turns any value into
            text that can be joined.
        ''',
        "prompt": r'''
            A dashboard shows short labels such as `tokens: 5`. The function `label` should build that
            text from a number, but it stops with
            `TypeError: can only concatenate str (not "int") to str`.

            **Your job:** find the bug in `label(count)` and fix it. The code is already in the editor.

            **What goes in**
            - `count`: a whole number, for example `5`

            **What comes out**
            - a string: `tokens: `, with one space after the colon, followed by the number: `"tokens: 5"`
              for the example value

            **Rules**
            - The text is handed back with `return`, not printed.
            - The number appears as plain digits, with no extra spaces or punctuation.

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
            "The error says that `+` can only join a `str` to a `str`. What is the type of `count`?",
            "The number has to become text before it can be joined to the other text.",
            "On the `return` line, pass `count` through the conversion function that gives the text form of a value. Leave the rest of the line as it is.",
        ],
    },
    {
        "id": "data-types-s6",
        "title": "Clean up an answer",
        "difficulty": 0,
        "lesson": r'''
            ## Cleaning up text

            You ask a model a yes-or-no question and its answer arrives as `"  YES\n"`: two spaces in
            front, capital letters, and an odd `\n` at the end. Your program wants to compare the answer
            with `"yes"`, so the answer needs cleaning first.

            The `\n` is the **newline** character, the single character that ends a line of text. It is
            typed as two signs and counts as one character.

            Strings bring their own tools. You use one by writing a dot after the string, then the name
            of the tool:

            ```python
            city = "Paris"
            print(city.lower())
            # paris
            print(city.upper())
            # PARIS
            ```

            Read `city.lower()` as "city, give me yourself in small letters". A function that belongs to
            a value and is called with a dot is a **method**.

            The method `.strip()` removes spaces and newlines from both ends of a string. Spaces in the
            middle stay.

            ```python
            raw = "  New York\n"
            print(len(raw))
            # 11
            print(len(raw.strip()))
            # 8
            ```

            ### A method never changes the string

            A string cannot change once it exists. Programmers say that strings are **immutable**. A
            method hands back a new string, and the original stays as it was.

            ```quiz
            What does this program print?

            ~~~python
            name = "Ada"
            name.upper()
            print(name)
            ~~~
            - [x] `Ada` :: Right. `name.upper()` handed back the new string `"ADA"`, and the program did nothing with it. `name` still stands for the original.
            - [ ] `ADA` :: That needs an assignment, `name = name.upper()`. The method alone does not change `name`.
            - [ ] Nothing, because of an error :: Calling a method and ignoring its result is allowed. It only has no effect.
            ```

            Because the result of a method is a string again, you can call the next method straight on
            it. Python works from left to right. Press Next and compare `raw` with `trimmed`:

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

            ```predict
            reply = " Done.\n"
            print(reply.strip())
            print(reply.strip().upper())
            print(len(reply))
            ---
            `strip()` removes the space in front and the newline at the end, which leaves `Done.`. The second line strips first and then makes capitals: `DONE.`. `reply` itself never changed, so it still has 7 characters: a space, the five characters of `Done.` and the newline.
            ```

            **Watch out:** a method needs its parentheses. `raw.strip` without `()` does not call the
            method, so nothing is stripped.

            **In short:** `text.strip()` trims both ends and `text.lower()` makes small letters. Each
            hands back a new string, so the calls can follow one another.
        ''',
        "prompt": r'''
            Answers from a model often arrive with stray spaces, a newline at the end, or capital letters
            in odd places. Before a program compares an answer with the one it expects, it cleans the
            answer up.

            **Your job:** write `normalize(answer)` so that it gives back the cleaned-up text.

            **What goes in**
            - `answer`: a string, for example `"  YES\n"`

            **What comes out**
            - a string: `answer` without spaces and newlines at both ends, and with every letter small:
              `"yes"` for the example value

            **Rules**
            - Spaces in the middle stay: `" New York "` gives `"new york"`.
            - The empty string gives `""`.

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
            "Strings have a method that trims both ends and a method that changes the case of the letters.",
            "Two things happen to the text, one after the other: the ends are trimmed, and the letters become small. Each method hands back a new string.",
            "Write one `return` line. Start with `answer`, call the trimming method on it, and call the lowercase method on the result of that.",
        ],
    },
    {
        "id": "data-types-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The name of a type, and values that count as "nothing"

            This step brings two small tools. You will use both of them for the rest of the course.

            ### Only the name, please

            `type(512)` prints as `<class 'int'>`. Often you only want the word `int`. Add `.__name__`
            after the call, with two underscores on each side, and you get the name of the type as a
            string:

            ```python
            print(type(0.5).__name__)
            # float
            print(type(True).__name__)
            # bool
            ```

            That second example shows a new type. `True` and `False` are the two values of the type
            **bool**, short for boolean. They are Python's answers to yes-or-no questions. Both are
            written with a capital first letter and without quotes.

            ### Turning any value into True or False

            Every value can be turned into a bool with `bool()`. The rule is simple: values that are
            "empty" or "zero" become `False`, and everything else becomes `True`.

            ```python
            print(bool(0), bool(0.0), bool(""), bool(None))
            # False False False False
            print(bool(3), bool("no"))
            # True True
            ```

            A value that turns into `False` is called **falsy**, and a value that turns into `True` is
            **truthy**. The falsy values you know so far are `0`, `0.0`, the empty string `""` and
            `None`. The whole idea is called **truthiness**, and the next chapter builds on it.

            ```quiz
            What is `bool("false")`?
            - [x] `True` :: Right. `"false"` is a string with five characters, and every string that is not empty is truthy. Python does not read the word.
            - [ ] `False` :: `bool()` looks at whether the string is empty, not at what it says. Only `""` is a falsy string.
            - [ ] An error :: `bool()` accepts every value, so it never stops with an error here.
            ```

            ```predict
            print(type(1.5).__name__)
            print(bool(""), bool(" "))
            print(bool(0), bool(-1))
            ---
            `1.5` has a decimal point, so its type is `float`. The empty string is falsy, but a string that holds one space is not empty, so it is truthy. `0` is falsy, and every other number is truthy, negative numbers included.
            ```

            **Watch out:** a string that looks empty is not always empty. `" "` holds a space, and
            `"0"` holds a digit. Both are truthy.

            **In short:** `type(x).__name__` is the name of a value's type as a string, and `bool(x)` is
            `False` for zero, empty and `None`, and `True` for everything else.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line.
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
            `42` is a whole number, so its type name is `int`. `"42"` is in quotes, so its type name is
            `str`. `int("7")` hands back the number 7, and `7 + 3` is `10`. `"7" + "3"` joins two strings
            into `73`. `bool(0)` is `False`, because 0 is falsy, and `bool("hi")` is `True`, because a
            string that is not empty is truthy. A `print` with a comma puts one space between them.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Look for quotes first. Quotes make a value a `str`, even when it holds digits.",
            "`type(x).__name__` gives the name of the type. `+` adds numbers and joins strings. `bool()` is `False` only for zero, empty and `None`.",
            "Lines one and two are the type names of a whole number and of text. Line three is a sum of two numbers. Line four is two characters joined together. Line five is two bools with one space between them.",
        ],
    },
    {
        "id": "data-types-s5",
        "title": "Missing or zero?",
        "difficulty": 0,
        "lesson": r'''
            ## "Nothing was set" is not the same as zero

            A settings form has a field called "max retries". One user types `0`, meaning "never retry".
            Another user leaves the field empty. Your program has to tell these two apart. Zero is an
            answer. An empty field is no answer at all.

            Python's value for "no answer" is `None`. You met it in the Basics chapter as the thing a
            function hands back when it has no `return`. `None` is not `0` and it is not `""`. It is a
            value of its own, with a type of its own, `NoneType`.

            So how do you test for it? `bool()` does not help, because `0` and `None` are both falsy:

            ```python
            retries = 0
            setting = None
            print(bool(retries), bool(setting))
            # False False
            ```

            The precise question is `is None`:

            ```python
            retries = 0
            setting = None
            print(retries is None)
            # False
            print(setting is None)
            # True
            ```

            `value is None` asks "is this value `None`?", and the answer is a bool. Like any value, you
            can print that bool, store it under a name, or hand it back with `return`.

            ```predict
            limit = None
            count = 0
            print(limit is None, count is None)
            print(bool(limit), bool(count))
            ---
            Only `limit` is `None`, so the first line is `True False`. Both values are falsy, so `bool()` gives `False False` and cannot tell them apart.
            ```

            ```quiz
            For which values does `value is None` give `True`?
            - [x] Only for `None` :: Right. `is None` asks one exact question, and only `None` answers yes.
            - [ ] For `None`, `0` and `""` :: Those are the falsy values, which `bool()` treats alike. `is None` is stricter: `0` and `""` are real values.
            - [ ] For every value that has not been printed yet :: Printing has nothing to do with it. A value is `None` only when nothing was set.
            ```

            **Watch out:** `None` is written with a capital `N` and without quotes. `"None"` is a string
            of four letters, and it is not `None`.

            **In short:** `value is None` is `True` only when no value was set. `0` and `""` are values,
            so for them it is `False`.
        ''',
        "prompt": r'''
            A setting in an app can be missing, which Python writes as `None`. It can also be set to a
            value that looks empty, such as `0` or `""`. Those are different situations: `0` retries is a
            real choice, and a missing setting means that nobody chose anything.

            **Your job:** write `is_missing(value)` so that it tells the two apart.

            **What goes in**
            - `value`: any value, for example `None`, `0`, `""` or `512`

            **What comes out**
            - a bool: `True` when `value` is `None`, and `False` for everything else

            **Rules**
            - Only `None` is missing.
            - `0`, `0.0`, `""` and `False` are not missing, so they give `False`.
            - An ordinary value such as `512` gives `False`.
            - The result is the bool `True` or `False`, not text such as `"True"`.

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
            "The lesson shows a test that says yes for `None` and no for `0` and for an empty string.",
            "That test already gives `True` or `False`, so the function can hand its result straight back. `bool()` is the wrong tool here, because it treats `0` and `None` alike.",
            "Write a single `return` line. After `return` comes the question from the lesson that asks whether `value` is `None`.",
        ],
    },
    {
        "id": "data-types-s4",
        "title": "Average tokens",
        "difficulty": 0,
        "lesson": r'''
            ## Dividing, and tidying up the result

            A chat has used 10 tokens in 4 messages. How many tokens is that per message, on average?
            That is a division, and Python's sign for it is `/`:

            ```python
            print(10 / 4)
            # 2.5
            print(9 / 3)
            # 3.0
            print(8 / 3)
            # 2.6666666666666665
            ```

            Two things are worth noticing. First, the result of `/` is always a `float`, even when the
            division comes out even: `9 / 3` is `3.0`, not `3`. Second, a result can have a long tail of
            digits that nobody wants to read.

            `round` tidies that up. You met it in the Basics chapter, where you looked up its second
            argument. That argument is the number of **decimal places** to keep, which means the digits
            after the decimal point:

            ```python
            print(round(8 / 3, 2))
            # 2.67
            ```

            Python works from the inside out, so the division happens first and `round` gets its result.

            ```predict
            print(7 / 2)
            print(6 / 2)
            print(round(20 / 3, 1))
            ---
            `7 / 2` is 3.5. `6 / 2` comes out even, but `/` always gives a float, so Python shows `3.0`. `20 / 3` is 6.666..., and rounded to 1 decimal place that is 6.7.
            ```

            The order matters: divide first, then round the result.

            ```quiz
            A bill of 20 is shared by 3 people, and you want each share rounded to 2 decimal places. Which expression gives `6.67`?
            - [x] `round(20 / 3, 2)` :: Right. The division gives 6.666..., and `round` keeps 2 digits after the point.
            - [ ] `round(20, 2) / round(3, 2)` :: This rounds the two inputs, which changes nothing, and then divides. The long tail of digits is still there.
            - [ ] `round(20 / 3)` :: Without a second argument, `round` gives the nearest whole number, which is 7.
            ```

            **Watch out:** nothing can be divided by zero. `10 / 0` stops the program with
            `ZeroDivisionError: division by zero`.

            **In short:** `/` divides and always gives a float, and `round(x, n)` keeps `n` digits after
            the decimal point.
        ''',
        "prompt": r'''
            A chat app wants to show how many tokens a message uses on average. It knows the total number
            of tokens in the conversation and the number of messages.

            **Your job:** write `average_tokens(total, count)` so that it gives back the average, rounded
            to 1 decimal place.

            **What goes in**
            - `total`: the total number of tokens, a whole number, for example `10`
            - `count`: the number of messages, a whole number greater than 0, for example `4`

            **What comes out**
            - a float: `total` divided by `count`, rounded to 1 decimal place: `2.5` for the example values

            **Rules**
            - Use ordinary division, so that the result can have decimals.
            - The result has exactly 1 decimal place: `3.333...` becomes `3.3`, and `0.666...` becomes `0.7`.

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
            "Two tools from the lesson are needed: the operator for ordinary division, and the built-in that rounds a number.",
            "Divide the total by the count first. Then round the result of that division, not the two inputs.",
            "Write one `return` line with a call to `round`. Its first argument is the division of the two parameters. Its second argument is the number of decimal places that the task asks for.",
        ],
    },
    {
        "id": "data-types-1",
        "title": "Name the type",
        "difficulty": 1,
        "lesson": r'''
            ## Building a sentence about any value

            When data from an API looks wrong, the first question is often: is that `42` a number, or is
            it text? A line such as `42 is str` answers it at a glance. To build such a line you need two
            pieces of text, and you have a tool for each.

            The first tool gives the name of the type. `type(x).__name__` is a string, so it can be joined
            to other strings:

            ```python
            value = True
            print("type: " + type(value).__name__)
            # type: bool
            ```

            The second tool gives the value itself as text. `str()` works for every value. A string
            passes through it unchanged, and no quotes are added:

            ```python
            print(str(0.7) + "!")
            # 0.7!
            print(str(None), str((1, 2)), str("42"))
            # None (1, 2) 42
            ```

            Joining strings with `+` is called **string concatenation**, and every piece must be a `str`.
            That is why both tools matter: each of them turns something that is not text into text.

            ```predict
            print("kind: " + type(None).__name__)
            print(str(10) + str(5))
            print(str("hi") + "!")
            ---
            The type of `None` is called `NoneType`. `str(10)` and `str(5)` are the strings `"10"` and `"5"`, so `+` joins them into `105`. A string passed to `str()` stays as it is, so the last line is `hi!`.
            ```

            ```fill
            score = 0.9
            print("score " + ___ + " ok")
            ---
            - [x] str(score) :: Right. `str(score)` is the string `"0.9"`, so all three pieces are strings and the program prints `score 0.9 ok`.
            - [ ] score :: `score` is a float, and `+` cannot join a string to a float. Python stops with a `TypeError`.
            - [ ] type(score) :: `type(score)` is a type, not a string, so this is a `TypeError` too. The name of the type would be `type(score).__name__`.
            ```

            **Watch out:** `type(x)` on its own is not text. `"is " + type(x)` stops with a `TypeError`.
            Add `.__name__` to get the name as a string.

            **In short:** `str(x)` is the value as text and `type(x).__name__` is the name of its type as
            text, and text can be joined with `+`.
        ''',
        "prompt": r'''
            When you inspect data that came from an API, it helps to see each value together with its
            type. The value `42` might be a number or it might be text, and the difference matters.

            **Your job:** write `describe_value(value)` so that it gives back one line of text about the
            value, such as `"512 is int"`.

            **What goes in**
            - `value`: any value, for example `512`, `0.7`, `"42"`, `True`, `None` or `(1, 2)`

            **What comes out**
            - a string made of three parts: the value as text, then ` is ` (a space, the word `is`, a
              space), then the name of the value's type

            **Rules**
            - The string is handed back with `return`, not printed.
            - The value part is the value turned into text. A string such as `"42"` appears as `42`,
              without quotes.
            - The type part is only the name of the type, such as `int`, and not `<class 'int'>`.
            - It works for every type, not only for the ones in the examples.

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
            "You need two pieces of text: the value turned into text, and the name of its type as text. The lesson has a tool for each.",
            "One built-in turns any value into a string. For the type, `type(value)` alone is not a string, so the name has to be taken from it. Join the pieces with `+`.",
            "Write one `return` line with three pieces joined by `+`: the value passed through the text conversion, then the text `\" is \"` with a space on each side, then the name of the value's type.",
        ],
    },
    {
        "id": "data-types-2",
        "title": "Add up string numbers",
        "difficulty": 1,
        "lesson": r'''
            ## Turn text into numbers before you do the maths

            A usage report says that a request used `"120"` prompt tokens and `"30\n"` completion tokens.
            Both numbers arrive as text, one of them with a newline at the end. You want the total.

            Adding them straight away goes wrong in a way you have seen before:

            ```python
            print("120" + "30")
            # 12030
            ```

            `+` joined the two strings. Turning raw text into values of the right type is called
            **parsing**, and it has to happen before any calculation. `int()` and `float()` make it easy,
            because they ignore spaces and newlines around the digits:

            ```python
            print(int(" 7 ") * 2)
            # 14
            print(float(" 0.5\n"))
            # 0.5
            ```

            The order of the steps decides the result. Convert each piece of text on its own, and add
            the numbers afterwards:

            ```python
            print(int("12" + "3"))
            # 123
            print(int("12") + int("3"))
            # 15
            ```

            In the first line the strings were joined before the conversion, so `int` saw `"123"`. Press
            Next to watch what `+` does before and after the conversion:

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

            Put this small program in an order that works:

            ```order
            price_text = " 20 "
            count_text = "3\n"
            price = int(price_text)
            count = int(count_text)
            print(price * count)
            ---
            Each text has to exist before it is converted, and both numbers have to exist before they are multiplied. The program prints 60.
            ```

            ```quiz
            What does `int("1.5")` do?
            - [x] It stops with a `ValueError` :: Right. `int()` only accepts text that is a whole number. Text with a decimal point needs `float()`.
            - [ ] It gives `1` :: `int()` does not cut off the decimals of a string. It refuses the text.
            - [ ] It gives `2` :: `int()` does not round text either. Rounding is the job of `round`, and it works on numbers.
            ```

            **Watch out:** choose the conversion that fits the text. `"1.5"` needs `float()`, and `int()`
            stops on it with a `ValueError`.

            **In short:** convert each piece of text to a number first, and calculate with the numbers
            afterwards.
        ''',
        "prompt": r'''
            A usage report gives the token counts of a request as text, sometimes with spaces around the
            digits or a newline at the end. Your app needs the total as a number.

            **Your job:** write `total_tokens(prompt_text, completion_text)` so that it gives back the two
            counts added together.

            **What goes in**
            - `prompt_text`: a string that holds a whole number, for example `"120"` or `" 1000 "`
            - `completion_text`: a string that holds a whole number, for example `"30"` or `"24\n"`

            **What comes out**
            - the sum of the two numbers, as an `int`: `150` for `"120"` and `"30"`

            **Rules**
            - The counts are added as numbers: `"120"` and `"30"` give `150`, not `"12030"`.
            - The result has the type `int`. It is not a string and not a float.
            - Spaces and newlines around the digits make no difference.

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
            "Both inputs are strings. What does `+` do with two strings?",
            "Turn each piece of text into a whole number first, and add the two numbers afterwards.",
            "Write one `return` line: the first parameter passed through the conversion to a whole number, a plus sign, and the second parameter passed through the same conversion. The conversion ignores the spaces and newlines for you.",
        ],
    },
    {
        "id": "data-types-7",
        "title": "Does it fit?",
        "difficulty": 1,
        "lesson": r'''
            ## Asking a yes-or-no question

            Before a request goes to a model, your app should ask: does it fit? Programs ask questions
            like this all the time. Is this number bigger than that one? Are these two values the same?
            The answer to such a question is always a bool.

            ```python
            tokens = 1200
            print(tokens > 1000)
            # True
            print(tokens == 1200, tokens != 1200)
            # True False
            print(tokens <= 1199)
            # False
            ```

            A question of this kind is called a **comparison**. Python has six comparison operators:

            ```match
            `==` :: is equal to
            `!=` :: is not equal to
            `<=` :: is less than or equal to
            `>=` :: is greater than or equal to
            ```

            The other two are `<`, less than, and `>`, greater than.

            ### A comparison is a value

            Any piece of code that produces a value is called an **expression**. `2 + 3` is an
            expression, and so is `tokens > 1000`. One that produces a bool is a **boolean expression**.
            Its result is an ordinary value, so a function can hand it straight back:

            ```python
            def is_long(tokens):
                return tokens > 1000

            print(is_long(50))
            # False
            ```

            Arithmetic is done before the comparison, so both sides may be calculations:

            ```predict
            used = 900
            print(used + 200 > 1000)
            print(used + 100 >= 1000)
            print(used == 900.0)
            ---
            `900 + 200` is 1100, which is greater than 1000. `900 + 100` is exactly 1000, and `>=` also says yes when both sides are equal. An int and a float with the same value are equal, so the last line is `True` as well.
            ```

            **Watch out:** one `=` assigns a value to a name, and two `==` compare two values. Also,
            floats are not exact: `0.1 + 0.2 == 0.3` is `False`. Use whole numbers when a comparison has
            to be exact.

            **In short:** a comparison such as `a <= b` is an expression that produces `True` or `False`,
            and you can store it or return it like any other value.
        ''',
        "prompt": r'''
            A model can only handle a limited number of tokens at once. That limit is called its context
            window. The prompt and the answer share it, so before a request your app checks that the
            prompt, plus the room kept free for the answer, fits into the window.

            **Your job:** write `fits_context(prompt_tokens, output_tokens, window)` so that it says
            whether the request fits.

            **What goes in**
            - `prompt_tokens`: the tokens in the prompt, a whole number, for example `1000`
            - `output_tokens`: the tokens kept free for the answer, a whole number, for example `500`
            - `window`: the size of the context window, a whole number, for example `4096`

            **What comes out**
            - a bool: `True` when the two token counts added together are not more than `window`, and
              `False` otherwise

            **Rules**
            - A request that fills the window exactly still fits, so it gives `True`.
            - The result is the bool `True` or `False`, not text such as `"True"`.

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
            "A comparison already produces `True` or `False`, so a function can return it directly.",
            "Add the two token counts, then compare that sum with the window. \"Not more than\" also covers the case where both sides are equal.",
            "Write one `return` line: the two token counts added together, then the comparison operator that means \"less than or equal to\", then the window.",
        ],
    },
    {
        "id": "data-types-8",
        "title": "Full pages and leftovers",
        "difficulty": 1,
        "lesson": r'''
            ## How many whole times, and what is left over

            Seventeen documents are shown five to a page. That makes 3 full pages, with 2 documents left
            over for a last page. It is the division you learned at school, the kind with a remainder,
            and Python has one operator for each part of the answer:

            ```python
            print(17 // 5)
            # 3
            print(17 % 5)
            # 2
            print(17 / 5)
            # 3.4
            ```

            `//` is called **floor division**. It divides and rounds down to a whole number, and with two
            ints the result is an int. `%` gives the **remainder**, the part that is left over. Its name
            is the **modulo** operator. The two belong together: 5 times 3, plus 2, is 17.

            `/` is the ordinary division from a few steps ago, which always gives a float.

            ```predict
            print(20 // 5, 20 % 5)
            print(3 // 5, 3 % 5)
            print(23 // 10, 23 % 10)
            ---
            20 divides by 5 exactly, so the remainder is 0. 5 does not fit into 3 even once, so the whole part is 0 and all 3 are left over. 10 fits into 23 twice, with 3 left over.
            ```

            ```quiz
            A video is 200 seconds long. Which expression gives the seconds that are left over after the full minutes?
            - [x] `200 % 60` :: Right. 60 fits into 200 three times, which is 180, and 20 seconds are left over.
            - [ ] `200 // 60` :: That is the number of full minutes, 3. The question asks for what is left over.
            - [ ] `200 / 60` :: Ordinary division gives 3.33..., a float that mixes the minutes and the leftover seconds.
            ```

            ### Why not just int(17 / 5)?

            It gives 3 as well, but it takes a detour through a float, and floats are not exact for very
            large numbers. `//` on two ints stays exact however large they are:

            ```python
            big = 1000000000000000001
            print(big // 1)
            # 1000000000000000001
            print(int(big / 1))
            # 1000000000000000000
            ```

            **Watch out:** `%` has nothing to do with percent. `50 % 100` is `50`, the remainder when 50
            is divided by 100.

            **In short:** `a // b` is how many whole times `b` fits into `a`, and `a % b` is what is left
            over.
        ''',
        "prompt": r'''
            A dashboard lists documents, a fixed number on each page. To draw the page buttons, it needs
            to know how many pages are completely full and how many documents are left for a last page
            that is only partly filled.

            **Your job:** write `split_into_pages(total, per_page)` so that it gives back both numbers.

            **What goes in**
            - `total`: the number of documents, a whole number, for example `250`
            - `per_page`: the number of documents on a page, a whole number greater than 0, for example `100`

            **What comes out**
            - a tuple of two ints, `(full_pages, leftover)`: `(2, 50)` for the example values

            **Rules**
            - Both values have the type `int`, not `float`.
            - When the documents fill the pages exactly, `leftover` is `0`.
            - When `total` is smaller than `per_page`, there are `0` full pages.

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
            "One operator tells you how many whole times a number fits into another. A second operator tells you what is left over.",
            "The full pages come from floor division, and the leftover comes from the remainder operator. The function hands back both, as a tuple.",
            "Write one `return` line with two values and a comma between them: first the total floor-divided by the page size, then the remainder of the same division.",
        ],
    },
    {
        "id": "data-types-9",
        "title": "Count unique tags",
        "difficulty": 1,
        "lesson": r'''
            ## Keeping one of each

            The documents in a search index carry tags, and the same tag turns up again and again. The
            tag `rag` might appear forty times. How many different tags are there?

            A tuple cannot tell you, because a tuple keeps everything you put into it, repeats included.
            For this question Python has another type. A **set** keeps one copy of each distinct value,
            and it has no order:

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

            `set(models)` builds a set from the tuple and drops the repeats. `len` counts the items that
            remain. The word `in` asks whether a value is in the set, and the answer is a bool. This
            question is called a **membership test**.

            ```quiz
            `tags = {"rag", "llm"}`. What is `"RAG" in tags`?
            - [x] `False` :: Right. Capital letters matter, so `"RAG"` and `"rag"` are different strings, and only `"rag"` is in the set.
            - [ ] `True` :: The set holds `"rag"` in small letters. A string with other capitals is a different value.
            - [ ] `2` :: `in` asks a yes-or-no question, so its answer is a bool. The number of items is `len(tags)`.
            ```

            ### Two sets together

            As the quiz shows, you can write a set directly with curly braces. Two operators combine
            sets. `a & b` is the set of values that are in both. `a | b` is the set of values that are in
            either one. Click an operator to see which values the result holds:

            ```diagram
            {"type": "set-ops", "title": "Tags in a and b", "a": {"name": "a", "items": ["rag", "llm"]}, "b": {"name": "b", "items": ["llm", "eval"]}}
            ```

            ```predict
            a = {"rag", "llm", "eval"}
            b = {"llm", "agents"}
            print(len(a & b))
            print(len(a | b))
            print("eval" in b)
            ---
            Only `llm` is in both sets, so `a & b` has 1 item. Together the sets hold four different tags: rag, llm, eval and agents. `eval` is in `a` but not in `b`, so the last line is `False`.
            ```

            **Watch out:** `{}` with nothing in it is not an empty set. It makes an empty dict, another
            type that a later chapter covers. Write `set()` for an empty set.

            **In short:** `set(group)` keeps one copy of each value, `len` counts them, and `&` and `|`
            combine two sets.
        ''',
        "research": {
            "note": 'Read the short tutorial section on sets (what they are for and how to build one), then come back.',
            "links": [
                {"title": 'Sets - Python tutorial', "url": 'https://docs.python.org/3/tutorial/datastructures.html#sets'},
            ],
        },
        "prompt": r'''
            The documents in the search index of a RAG app carry tags. (RAG means that the app looks up
            documents and hands them to the model.) The same tag is often repeated, and you want to know
            how many different tags there are.

            **Your job:** write `count_unique(tags)` so that it gives back the number of distinct tags.

            **What goes in**
            - `tags`: a tuple of strings, for example `("rag", "llm", "rag")`

            **What comes out**
            - a whole number, the count of different tags: `2` for the example value

            **Rules**
            - A tag that is repeated counts once.
            - Capital letters matter: `"RAG"` and `"rag"` are two different tags.
            - The empty tuple `()` gives `0`.

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
            "Build that kind of group from the tuple. Then count how many items it has.",
            "Write one `return` line with a nested call: the counting built-in on the outside, and inside it the tuple turned into a set.",
        ],
    },
    {
        "id": "data-types-3",
        "title": "Parse request settings",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Settings that a program reads from a file or from the command line always arrive as text,
            often with stray spaces or a newline. Three settings of a request to an AI model need their
            real types: the temperature (how much variety the answers may have), the maximum number of
            tokens, and whether the answer is streamed, which means sent piece by piece.

            **Your job:** write `parse_settings(temperature_text, max_tokens_text, stream_text)` so that
            it gives back the three settings with the right types.

            **What goes in**
            - `temperature_text`: text that holds a number, for example `" 0.7 "` or `"1"`
            - `max_tokens_text`: text that holds a whole number, for example `"512\n"`
            - `stream_text`: text such as `"true"`, `" TRUE "`, `"false"`, `"yes"` or `""`

            **What comes out**
            - a tuple of 3 values, `(temperature, max_tokens, stream)`: a float, an int and a bool

            **Rules**
            - `temperature` is always a `float`, even for `"1"`, which gives `1.0`, and for `"0"`, which
              gives `0.0`.
            - `max_tokens` is an `int`.
            - `stream` is `True` only when `stream_text` is the word `true`, in any mix of capital and
              small letters, with or without spaces and newlines around it.
            - Every other text gives `False` for `stream`: `"false"`, `" False\n"`, `"yes"` and `""`.
            - Spaces and newlines around any of the three texts make no difference.

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
            "Two of the three settings are plain conversions. The third is not: `bool(\"false\")` is `True`, because every string that is not empty is truthy.",
            "Use the conversion functions for the two numbers. For `stream`, clean the text first (trim the ends, make it lowercase), then compare it with the word you are looking for. The comparison itself is the bool.",
            "The body has four lines: a float made from the first text, an int made from the second, a bool that comes from comparing the cleaned third text with the lowercase word for true, and a `return` with the three names separated by commas.",
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
            A request to an AI model has three costs in dollars: the prompt, the output and the tool
            calls. You want the total, and you want to know whether it stays within a budget. The costs
            are floats, and floats are not exact: in Python, `0.1 + 0.1 + 0.1` is
            `0.30000000000000004`. Your function has to give sensible answers in spite of that.

            **Your job:** write `check_budget(prompt_cost, output_cost, tool_cost, budget)` so that it
            gives back the total and whether the total is within the budget.

            **What goes in**
            - `prompt_cost`, `output_cost`, `tool_cost`: three costs in dollars, floats, for example `0.1`
            - `budget`: the highest total that is allowed, a number, for example `0.3`

            **What comes out**
            - a tuple `(total, within)`: a float and a bool

            **Rules**
            - `total` is the sum of the three costs, rounded to 6 decimal places. `0.1 + 0.1 + 0.1` gives
              `0.3`, and `0.0000014 + 0.0000027` gives `4e-06`, which is how Python writes 0.000004.
            - `within` is `True` when the sum is not more than `budget`, and `False` otherwise.
            - A tiny float error must not make a request look too expensive. A sum that is above the
              budget by at most `1e-9`, which is 0.000000001, still counts as within.
            - `within` is decided from the sum before it is rounded. A sum of `0.1000004` is over a budget
              of `0.1`, even though its rounded total is `0.1`.
            - Anything that is clearly above the budget is over, even by a little: `0.3001` is over `0.3`.

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
            "Three tools are enough: `round` with a second argument, a comparison (which is already a bool), and a small allowance for float errors.",
            "Add the three costs once, and keep that sum under a name. Round it for the total. For `within`, compare the sum before rounding with the budget plus the tiny allowance.",
            "Line one: a name for the three costs added together. Line two: `return` two values. The first is that sum rounded to 6 places. The second is a comparison that asks whether the unrounded sum is at most the budget plus the allowance from the task.",
        ],
    },
    {
        "id": "data-types-5",
        "title": "Tag overlap",
        "difficulty": 3,
        "prompt": r'''
            Each document in the search index of a RAG app has a tuple of tags, and a tag may be
            repeated. To measure how alike two documents are, you compare their tags with an **overlap
            score**: the number of distinct tags that they share, divided by the number of distinct tags
            that appear in either of them.

            **Your job:** write `overlap(tags_a, tags_b)` so that it gives back the overlap score.

            **What goes in**
            - `tags_a`: a tuple of strings, for example `("rag", "llm", "rag")`
            - `tags_b`: a tuple of strings, for example `("llm", "eval")`

            **What comes out**
            - the score as a float, rounded to 3 decimal places: `0.333` for the example values (1 shared
              tag out of 3 different tags)

            **Rules**
            - A repeated tag counts once: `("a", "a")` has 1 distinct tag.
            - No shared tags gives `0.0`. That includes the case where one tuple is empty.
            - When both tuples are empty, the result is `0.0`. The function must not stop with an error.
            - The result is always a float: `1.0`, not `1`.
            - Use only what this chapter and the earlier ones taught. A check fails when the code
              contains `if`, `for`, `while` or `try`, which are tools from later chapters.

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
            "Sets drop repeats for you. The lesson on sets shows `&` for the values in both sets and `|` for the values in either, and `len` counts the items of a set.",
            "Turn each tuple into a set. Count the shared tags, count all the tags, divide the first count by the second, and round. For two empty tuples, think about how to make sure that you never divide by zero.",
            "Make two sets. Take `len` of their `&` and `len` of their `|`. Divide the shared count by the bigger of the total count and 1, which the built-in `max` picks for you. When the total is 0, the shared count is 0 as well, so the result is 0.0. Round to 3 places.",
        ],
    },
    {
        "id": "data-types-6",
        "title": "Batch planner",
        "difficulty": 3,
        "prompt": r'''
            To turn documents into embeddings, which are lists of numbers that capture what a text means,
            you send the documents to an API in batches of a fixed size. Before a job starts you want a
            plan: how many batches are completely full, how many documents are left over, and how many
            API calls the job needs in total.

            **Your job:** write `plan_batches(total_text, batch_size)` so that it gives back those three
            numbers.

            **What goes in**
            - `total_text`: the number of documents as text, possibly with spaces or a newline around it,
              for example `" 1000\n"`
            - `batch_size`: the number of documents in a batch, a whole number greater than 0, for
              example `100`

            **What comes out**
            - a tuple of three ints, `(full_batches, leftover, batches_needed)`:
              - `full_batches`: the number of batches that are completely full
              - `leftover`: the number of documents that remain after the full batches
              - `batches_needed`: the number of batches in total. A batch that is only partly filled
                still needs a call.

            **Rules**
            - All three values have the type `int`, not `float`.
            - The results are exact even for a huge total such as `10**18 + 1` (a 1 followed by 18 zeros,
              plus 1). Floats are not exact at that size, so use whole-number arithmetic only.
            - A total of `0` needs `0` batches.
            - A check fails when the code contains `if`, which is a tool from the next chapter.

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
            "`//` and `%` give the full batches and the leftover. The hard part is the third number: a division that rounds up, done with whole numbers only.",
            "To round a division up, first add just enough to the total that a partly filled batch becomes a full one, then use `//`. Stay away from `/`, because it makes a float.",
            "Convert the text to an int first. The full batches are the total floor-divided by the batch size, and the leftover is the remainder of that division. For the batches needed, add one less than the batch size to the total, and floor-divide that by the batch size. Return the three values.",
        ],
    },
]
