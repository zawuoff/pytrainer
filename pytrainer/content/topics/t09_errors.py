TOPIC = {
    "id": "errors",
    "title": "Error Handling",
    "track": "foundations",
    "order": 9,
    "requires": ["functions"],
    "summary": """
        Handling and raising exceptions: try/except/else/finally, specific exception
        types, custom exception hierarchies, exception chaining and retries.
    """,
    "concepts": ["try/except", "else and finally", "specific exceptions", "raise",
                 "custom exceptions", "exception hierarchy", "raise from", "re-raising",
                 "retries", "input validation"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["error", "exception", "try", "except", "finally", "raise", "traceback", "catch",
                 "valueerror", "typeerror", "keyerror", "custom exception", "validate", "retry"],
    "cards": [
        {
            "syntax": "try: ...  except ValueError: ...",
            "explain": "Runs the try block. If a line in it raises ValueError, Python runs the except block and the program continues.",
            "example": r'''
                try:
                    print(int("abc"))
                except ValueError:
                    print("not a number")
                print("still running")
                # not a number
                # still running
            ''',
        },
        {
            "syntax": "except (TypeA, TypeB) as e:",
            "explain": "Catches either type and assigns the exception object to e. str(e) and print(e) give its message.",
            "example": r'''
                try:
                    float("abc")
                except (ValueError, TypeError) as e:
                    print("failed:", e)
                # failed: could not convert string to float: 'abc'
            ''',
        },
        {
            "syntax": "try: ...  except E: ...  finally: ...",
            "explain": "The finally block runs in every case, with or without an exception. An else block runs only when try raises nothing.",
            "example": r'''
                try:
                    print(10 / 0)
                except ZeroDivisionError:
                    print("cannot divide")
                finally:
                    print("always runs")
                # cannot divide
                # always runs
            ''',
        },
        {
            "syntax": 'raise ValueError("message")',
            "explain": "Stops the function and raises the exception. Use TypeError for a wrong type, ValueError for an unacceptable value.",
            "example": r'''
                t = 5
                try:
                    if t > 2:
                        raise ValueError(f"must be at most 2, got {t}")
                except ValueError as e:
                    print("error:", e)
                # error: must be at most 2, got 5
            ''',
        },
        {
            "syntax": "class MyError(Exception): pass",
            "explain": "Defines your own exception type. You raise it and catch it by name, the same way as a built-in type.",
            "example": r'''
                class TooLongError(Exception):
                    pass

                try:
                    raise TooLongError("prompt too long")
                except TooLongError as e:
                    print("caught:", e)
                # caught: prompt too long
            ''',
        },
        {
            "syntax": 'raise NewError("message") from e',
            "explain": "Raises a new exception inside an except block and stores the caught one, e, as its __cause__.",
            "example": r'''
                try:
                    try:
                        int("hi")
                    except ValueError as e:
                        raise RuntimeError("bad prompt") from e
                except RuntimeError as err:
                    print(err, "| cause:", type(err.__cause__).__name__)
                # bad prompt | cause: ValueError
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Error Handling

### Exceptions

An **exception** is an object Python creates when a line of code cannot finish its work.
Creating and sending that object is called **raising** the exception. If nothing handles
it, the program stops and Python prints a **traceback**: the list of lines that were
running. The last line of the traceback shows the exception **type** and its **message**:

`ValueError: invalid literal for int() with base 10: 'abc'`

| Code | Raises |
| --- | --- |
| `int("abc")` | `ValueError` |
| `int(None)`, `"a" + 1` | `TypeError` |
| `{"a": 1}["b"]` | `KeyError` |
| `[1, 2][5]` | `IndexError` |
| `1 / 0` | `ZeroDivisionError` |

### try, except, else, finally

A `try` statement runs a block of code and **catches** exceptions raised inside it.
Catching means running an `except` block instead of stopping the program.

```python
for text in ["8", "abc"]:
    try:
        n = int(text)
    except ValueError as e:
        print("bad value:", e)
    else:
        print("no error:", n)
    finally:
        print("always runs")
# no error: 8
# always runs
# bad value: invalid literal for int() with base 10: 'abc'
# always runs
```

- The `except` block runs only when the `try` block raises a matching exception.
  `as e` assigns the exception object to `e`, and `str(e)` is its message.
- The `else` block runs only when the `try` block raises nothing.
- The `finally` block runs in every case, even when an exception is not caught.

Step through the code to see which lines run for `"8"` and which run for `"abc"`.

```diagram
{"type": "trace", "title": "Which lines run with and without an exception", "code": ["for text in [\"8\", \"abc\"]:", "    try:", "        n = int(text)", "    except ValueError as e:", "        print(\"bad value:\", e)", "    else:", "        print(\"no error:\", n)", "    finally:", "        print(\"always runs\")"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {"text": "'8'"}, "out": ""},
  {"line": 3, "vars": {"text": "'8'"}, "out": ""},
  {"line": 7, "vars": {"text": "'8'", "n": "8"}, "out": ""},
  {"line": 9, "vars": {"text": "'8'", "n": "8"}, "out": "no error: 8\n"},
  {"line": 1, "vars": {"text": "'8'", "n": "8"}, "out": "no error: 8\nalways runs\n"},
  {"line": 2, "vars": {"text": "'abc'", "n": "8"}, "out": "no error: 8\nalways runs\n"},
  {"line": 3, "vars": {"text": "'abc'", "n": "8"}, "out": "no error: 8\nalways runs\n"},
  {"line": 4, "vars": {"text": "'abc'", "n": "8"}, "out": "no error: 8\nalways runs\n"},
  {"line": 5, "vars": {"text": "'abc'", "n": "8", "e": "ValueError(\"invalid literal for int() with base 10: 'abc'\")"}, "out": "no error: 8\nalways runs\n"},
  {"line": 9, "vars": {"text": "'abc'", "n": "8"}, "out": "no error: 8\nalways runs\nbad value: invalid literal for int() with base 10: 'abc'\n"},
  {"line": 1, "vars": {"text": "'abc'", "n": "8"}, "out": "no error: 8\nalways runs\nbad value: invalid literal for int() with base 10: 'abc'\nalways runs\n"},
  {"line": null, "vars": {"text": "'abc'", "n": "8"}, "out": "no error: 8\nalways runs\nbad value: invalid literal for int() with base 10: 'abc'\nalways runs\n"}
]}
```

`except (ValueError, TypeError):` catches either type. A **sub-type** is a more
specific kind of another type: `KeyError` and `IndexError` are sub-types of
`LookupError`, and almost every exception type is a sub-type of `Exception`. `except X`
also catches every sub-type of `X`. Python checks the `except` lines from top to bottom and runs the first
one that matches, so write specific types before general ones.

### Propagation

When no `except` matches, the function stops and the exception moves to the line that
called the function. This is called **propagation**. It repeats for each caller until
an `except` matches or the program stops.

```python
def parse(text):
    return int(text)

def load(text):
    return parse(text) + 1

try:
    print(load("41"))
    print(load("abc"))
except ValueError as e:
    print("caught:", e)
# 42
# caught: invalid literal for int() with base 10: 'abc'
```

Click each stage to follow the exception raised by `load("abc")`.

```diagram
{"type": "flow", "title": "How the ValueError propagates from parse to the except block", "steps": [{"label": "int raises", "detail": "Inside parse, int(\"abc\") cannot build a number. It creates a ValueError object and raises it.", "code": "def parse(text):\n    return int(text)   # ValueError raised here"}, {"label": "parse stops", "detail": "The raising line is not inside a try block in parse. parse stops at that line without returning a value. The exception moves to the line that called parse.", "code": "def load(text):\n    return parse(text) + 1   # the exception arrives here"}, {"label": "load stops", "detail": "That line is not inside a try block in load either. load stops too. The + 1 never runs. The exception moves to the line that called load.", "code": "try:\n    print(load(\"abc\"))   # the exception arrives here"}, {"label": "except matches", "detail": "This line is inside a try block. Python compares the exception type with each except line. ValueError matches except ValueError, so that block runs.", "code": "except ValueError as e:\n    print(\"caught:\", e)\n# caught: invalid literal for int() with base 10: 'abc'"}, {"label": "Program continues", "detail": "The exception is handled. The program continues with the first line after the try statement. If no except had matched, Python would stop the program and print a traceback."}]}
```

### Raising

`raise` followed by an exception object stops the function and raises that exception.
Calling the type with a string, as in `ValueError("too high")`, creates an exception
object with that message.

```python
def check_temperature(t):
    if t > 2:
        raise ValueError(f"temperature must be at most 2, got {t}")
    return t

print(check_temperature(0.7))
# 0.7
try:
    check_temperature(5)
except ValueError as e:
    print("error:", e)
# error: temperature must be at most 2, got 5
```

Use `TypeError` when the value has the wrong type. Use `ValueError` when the type is
right but the value is not acceptable.

`raise` with nothing after it, inside an `except` block, raises the same exception
object again. `raise NewError("...") from e` raises a new exception and stores `e` in
it. You read the stored exception by writing `.__cause__` after the new one. This is
called **exception chaining**.

```python
try:
    try:
        int("hi")
    except ValueError as e:
        raise RuntimeError("bad prompt") from e
except RuntimeError as err:
    print(err, "| cause:", type(err.__cause__).__name__)
# bad prompt | cause: ValueError
```

The inner `except` catches the `ValueError` and raises a `RuntimeError`. The outer
`except` catches that one. `err.__cause__` is the original `ValueError` object.

### Custom exceptions

A **custom exception** is an exception type you define yourself. `class` is a statement
that creates a new type. Write `class`, a name, an existing exception type in
parentheses, and `pass` as the body. `pass` is a statement that does nothing. It is
there because the body cannot be empty. The new type is a sub-type of the type in the
parentheses. Classes get their own topic later. For now, copy this form and change the names.

```python
class APIError(Exception):
    pass

class RateLimitError(APIError):
    pass

try:
    raise RateLimitError("slow down")
except APIError as e:
    print(type(e).__name__, e)
# RateLimitError slow down
```

`except APIError` catches `RateLimitError` because `RateLimitError` is a sub-type of
`APIError`.

### Common mistakes

- `except:` with no type or `except Exception:` also catches exceptions caused by bugs in your
  own code, such as `NameError`, which Python raises for a name that is misspelled or not defined.
  Name the types you expect.
- A large `try` block catches exceptions from lines you did not intend to cover. Put
  only the line that can fail inside `try`.
- `return "error: ..."` gives the caller a string that looks like normal data. Raise an
  exception instead.
- `isinstance(x, int)` checks a type: it is `True` when `x` is an int. `isinstance(True, int)` is also
  `True`, because `bool` is a sub-type of `int`. Reject bools
  with a separate `isinstance(x, bool)` check when you validate numbers.
- Retry only temporary errors such as `TimeoutError` and `ConnectionError`. Set a
  maximum number of attempts and double the wait each time (1, 2, 4 seconds). This is
  called **exponential backoff**.

Docs: https://docs.python.org/3/tutorial/errors.html
'''

EXERCISES = [
    {
        "id": "errors-s1",
        "lesson": r'''
            ## try and except

            Some lines of code can fail. `int("three")` fails because `"three"` is not a number.
            When a line fails, Python creates an **exception**: an object that describes what went
            wrong. We say the line **raises** the exception.

            If nothing handles the exception, the program stops and prints a **traceback**: the
            list of lines that were running, followed by the error.

            A `try` statement handles the exception instead. Put the line that can fail in the
            `try` block. Put the code to run on failure in the `except` block. We say `except`
            **catches** the exception.

            ```python
            for text in ["3", "three"]:
                try:
                    tokens = int(text)
                    print("converted:", tokens)
                except ValueError:
                    print("could not convert", text)
            print("still running")
            # converted: 3
            # could not convert three
            # still running
            ```

            `ValueError` is the kind of exception that `int("three")` raises.

            Python does this, in order:

            1. It runs the lines in the `try` block from the top.
            2. If a line raises an exception, Python stops the `try` block at that line and runs
               the `except` block.
            3. If no line raises, Python skips the `except` block.
            4. The program continues with the code after the `try` statement.

            Step through the code and watch which line runs after `int("three")` raises.

            ```diagram
            {"type": "trace", "title": "Where Python jumps when int(text) raises", "code": ["for text in [\"3\", \"three\"]:", "    try:", "        tokens = int(text)", "        print(\"converted:\", tokens)", "    except ValueError:", "        print(\"could not convert\", text)", "print(\"still running\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"text": "'3'"}, "out": ""},
              {"line": 3, "vars": {"text": "'3'"}, "out": ""},
              {"line": 4, "vars": {"text": "'3'", "tokens": "3"}, "out": ""},
              {"line": 1, "vars": {"text": "'3'", "tokens": "3"}, "out": "converted: 3\n"},
              {"line": 2, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\n"},
              {"line": 3, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\n"},
              {"line": 5, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\n"},
              {"line": 6, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\n"},
              {"line": 1, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\ncould not convert three\n"},
              {"line": 7, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\ncould not convert three\n"},
              {"line": null, "vars": {"text": "'three'", "tokens": "3"}, "out": "converted: 3\ncould not convert three\nstill running\n"}
            ]}
            ```

            The lines in `try` after the failing line never run. For `"three"`, the
            `print("converted:", tokens)` line is skipped.
        ''',
        "title": "Where does it jump?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            for text in ["7", "seven"]:
                try:
                    n = int(text)
                    print("number", n)
                except ValueError:
                    print("skip", text)
            print("done")
        ''',
        "solution": r'''
            number 7
            skip seven
            done
        ''',
        "explanation": r'''
            `int("7")` works, so the rest of the `try` block runs. `int("seven")` raises
            `ValueError`, so Python skips the remaining `try` lines and runs the `except`
            block instead. The loop and the program carry on normally.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Go through the loop once per item. Ask: does int() succeed on this text?",
            "If int() fails, the print inside try is skipped and the except block runs instead.",
            "First item converts fine (print from try). Second item fails (print from except). After the loop, the final print runs.",
        ],
    },
    {
        "id": "errors-s2",
        "lesson": r'''
            ## Exception types

            Every exception has a **type**: a name that says which kind of problem happened. It
            also has a **message**: text with the details.

            This program raises on purpose. Read the last line of the error it prints.

            ```python
            print(int("abc"))
            # ValueError: invalid literal for int() with base 10: 'abc'
            ```

            The part before the colon is the exception type, `ValueError`. The part after the colon
            is the message.

            After `except` you write the type you want to catch.

            ```python
            try:
                print(10 / 2)
                print(int("abc"))
            except ValueError:
                print("that text is not a number")
            # 5.0
            # that text is not a number
            ```

            These are the types you meet most often:

            - `ValueError`: the value has the right type but cannot be used, as in `int("abc")`.
            - `TypeError`: the value has the wrong type, as in `int(None)`.
            - `KeyError`: a dict does not have the key you asked for.
            - `ZeroDivisionError`: you divided by zero.

            To find out which type a line raises, run the line without `try` and read the last
            line of the traceback. Copy the type name exactly. No type is called `ZeroDivision`, so
            `except ZeroDivision:` raises `NameError` as soon as an exception reaches that line, because Python looks up the name `ZeroDivision` and does not find it.
        ''',
        "title": "Catch the right error",
        "difficulty": 0,
        "prompt": r'''
            A division helper that doesn't crash when the divisor is zero.
            The code is almost complete: replace the `___`.

            **Write:** `safe_divide(a, b)` (fill in the blank)

            - `a`, `b`: numbers, e.g. `10` and `4`
            - **Returns:** `a / b`, or `None` when `b` is `0`

            **Rules**
            - The `___` must be the name of the exception type that dividing by zero
              raises (run `print(1 / 0)` and read the last line of the error to find it).

            **Examples**
            ```python
            safe_divide(10, 4)   # returns 2.5
            safe_divide(1, 0)    # returns None
            ```
        ''',
        "starter": r'''
            def safe_divide(a, b):
                try:
                    return a / b
                except ___:
                    return None
        ''',
        "tests": r'''
            from solution import safe_divide

            def test_normal_division_returns_the_quotient():
                got = safe_divide(10, 4)
                assert got == 2.5, f"got {got!r}"

            def test_dividing_by_zero_returns_none():
                got = safe_divide(1, 0)
                assert got is None, f"got {got!r}"
        ''',
        "solution": r'''
            def safe_divide(a, b):
                try:
                    return a / b
                except ZeroDivisionError:
                    return None
        ''',
        "hints": [
            "Run print(1 / 0) and read the last line of the traceback: it names the exception type.",
            "The name before the colon on that last line is exactly what goes after except.",
            "Replace ___ with ZeroDivisionError.",
        ],
    },
    {
        "id": "errors-s3",
        "lesson": r'''
            ## except only catches the type it names

            An `except ValueError:` block catches `ValueError` exceptions. It does not catch a
            `KeyError` or a `TypeError`.

            When a line in `try` raises, Python compares the exception's type with the type written
            after `except`. If they match, the `except` block runs.

            ```python
            try:
                print(int("oops"))
            except ValueError:
                print("not a number")
            # not a number
            ```

            If they do not match, the `except` block does not run and the exception is not
            caught. It moves on to the code that called this code.
            This is called **propagation**. If nothing there catches it either, the program stops.

            The next program raises on purpose. `int("oops")` raises `ValueError`, but the `except`
            line names `KeyError`.

            ```python
            try:
                print(int("oops"))
            except KeyError:
                print("never printed")
            # ValueError: invalid literal for int() with base 10: 'oops'
            ```

            The program stops with a traceback. Its last line names `ValueError`, which is the type
            the `except` line needed.

            When a `try` statement does not catch an error, compare two things: the type on the
            last line of the traceback, and the type after `except`. They must be the same.
        ''',
        "title": "Fix: wrong exception type",
        "difficulty": 0,
        "prompt": r'''
            A counter arrives as text. This function should read it as a number, but it
            still crashes on `"lots"`. Find and fix the one bug.

            **Write:** `read_count(text)` (fix the given code)

            - `text`: a string, e.g. `"12"` or `"lots"`
            - **Returns:** the int value of `text`, or `-1` when `text` is not a number

            **Rules**
            - `int("lots")` raises an exception: catch that exact exception type and
              return `-1`.

            **Examples**
            ```python
            read_count("12")     # returns 12
            read_count("lots")   # returns -1
            ```
        ''',
        "starter": r'''
            def read_count(text):
                try:
                    return int(text)
                except KeyError:
                    return -1
        ''',
        "tests": r'''
            from solution import read_count

            def test_number_text_returns_the_int():
                assert read_count("12") == 12

            def test_non_number_text_returns_minus_one():
                got = read_count("lots")
                assert got == -1, f"got {got!r}"
        ''',
        "solution": r'''
            def read_count(text):
                try:
                    return int(text)
                except ValueError:
                    return -1
        ''',
        "hints": [
            "The except only catches the exception type it names. Is KeyError what int() raises?",
            "Try int(\"lots\") yourself and read the traceback to see the real exception type.",
            "Change KeyError to ValueError.",
        ],
    },
    {
        "id": "errors-s4",
        "lesson": r'''
            ## Raising an exception

            So far Python raised the exceptions. Your own code can raise them too, with the `raise`
            keyword. Use it when a function receives a value it cannot work with.

            ```python
            def check_temperature(t):
                if t > 2:
                    raise ValueError(f"temperature must be at most 2, got {t}")
                return t

            print(check_temperature(0.7))
            # 0.7
            try:
                check_temperature(5)
            except ValueError as e:
                print("error:", e)
            # error: temperature must be at most 2, got 5
            ```

            After `raise` you write the exception type, then the message in parentheses:
            `raise ValueError("...")`.

            `as e` on the `except` line assigns the caught exception to the name `e`.
            Printing `e` prints its message. A later step covers this.

            `raise` stops the function at that line. No later line in the function runs, so the
            `return t` is skipped. The exception goes to the code that called the function. That
            code can catch it with `try` and `except`. If it does not, the program stops with a
            traceback.

            Choose the type that describes the problem:

            - `ValueError`: the type is right but the value is not acceptable, such as a negative
              count.
            - `TypeError`: the type is wrong, such as a string where a number is required.

            Do not write `return "error: too high"` instead. The caller receives a string and
            cannot tell it apart from a normal result. An exception that is not caught stops the
            program, so the problem is always visible.
        ''',
        "title": "Raise on bad input",
        "difficulty": 0,
        "prompt": r'''
            Before calling a model, check that `max_tokens` makes sense. A value below 1
            is a bug in the caller's code, so stop with an error.

            **Write:** `check_max_tokens(n)`

            - `n`: an int, e.g. `256`
            - **Returns:** `n` itself when it is valid

            **Rules**
            - If `n` is less than `1` (e.g. `0` or `-5`), **raise** a `ValueError`
              (any message) instead of returning.
            - `1` is valid.

            **Examples**
            ```python
            check_max_tokens(256)   # returns 256
            check_max_tokens(1)     # returns 1
            check_max_tokens(0)     # raises ValueError
            check_max_tokens(-5)    # raises ValueError
            ```
        ''',
        "starter": r'''
            def check_max_tokens(n):
                ...
        ''',
        "tests": r'''
            from solution import check_max_tokens

            def test_valid_value_is_returned():
                assert check_max_tokens(256) == 256
                assert check_max_tokens(1) == 1

            def test_zero_raises_valueerror():
                try:
                    check_max_tokens(0)
                except ValueError:
                    return
                raise AssertionError("check_max_tokens(0) should raise ValueError")

            def test_negative_raises_valueerror():
                try:
                    check_max_tokens(-5)
                except ValueError:
                    return
                raise AssertionError("check_max_tokens(-5) should raise ValueError")
        ''',
        "solution": r'''
            def check_max_tokens(n):
                if n < 1:
                    raise ValueError("max_tokens must be at least 1")
                return n
        ''',
        "hints": [
            "Use an if to detect the bad case, and the raise keyword to signal it.",
            "If n is too small, raise a ValueError with a message. Otherwise just return n.",
            "Write: if n < 1, then raise ValueError(\"some message\"). On the next line (outside the if) return n.",
        ],
    },
    {
        "id": "errors-s5",
        "lesson": r'''
            ## KeyError

            Reading a dict with square brackets raises `KeyError` when the key is not in the dict.
            The exception's message is the missing key. For a string key, the message
            includes the quotes.

            ```python
            settings = {"temperature": 0.2}
            try:
                print(settings["max_tokens"])
            except KeyError as e:
                print("missing key:", e)
            print("program continues")
            # missing key: 'max_tokens'
            # program continues
            ```

            You can use this to supply a **fallback value**: a value to use when the real one is
            missing. Put the lookup in `try`, and return the fallback in `except KeyError`.

            ```python
            def get_max_tokens(settings):
                try:
                    return settings["max_tokens"]
                except KeyError:
                    return 256

            print(get_max_tokens({"max_tokens": 100}))
            # 100
            print(get_max_tokens({"temperature": 0.2}))
            # 256
            ```

            `settings.get("max_tokens", 256)` gives the same result. Both forms are correct Python.
            The `try` form has a name: **EAFP**, short for "easier to ask forgiveness than
            permission". You run the operation first and handle the exception if it happens.

            The type after `except` must be `KeyError`. `except ValueError:` does not catch a
            missing key, and the program stops with a traceback.
        ''',
        "title": "Missing config key",
        "difficulty": 0,
        "prompt": r'''
            A model config may or may not say which model to use. When it doesn't, fall
            back to a default model.

            **Write:** `get_model(config)`

            - `config`: a dict, e.g. `{"model": "claude", "temperature": 0.2}`
            - **Returns:** the string stored under the key `"model"`, or `"gpt-4o-mini"`
              when that key is missing

            **Rules**
            - Look up the key with square brackets, `config["model"]`. When the key is
              missing this raises `KeyError`.
            - Catch that `KeyError` with a `try` / `except` block and return
              `"gpt-4o-mini"` (a check looks for `try` in your code, so don't use `.get()`).
            - Other keys in the dict don't matter.

            **Examples**
            ```python
            get_model({"model": "claude"})       # returns "claude"
            get_model({"temperature": 0.2})      # returns "gpt-4o-mini"
            get_model({})                        # returns "gpt-4o-mini"
            ```
        ''',
        "starter": r'''
            def get_model(config):
                ...
        ''',
        "tests": r'''
            from solution import get_model

            def test_returns_model_when_key_present():
                assert get_model({"model": "claude"}) == "claude"

            def test_missing_model_key_returns_gpt_4o_mini():
                got = get_model({"temperature": 0.2})
                assert got == "gpt-4o-mini", f"got {got!r}"

            def test_code_uses_try_except():
                import ast
                assert any(isinstance(n, ast.Try) for n in ast.walk(ast.parse(source()))), \
                    "use try / except KeyError"
        ''',
        "solution": r'''
            def get_model(config):
                try:
                    return config["model"]
                except KeyError:
                    return "gpt-4o-mini"
        ''',
        "hints": [
            "Looking up a missing key with square brackets raises KeyError. Wrap that lookup in try.",
            "Return the lookup inside try; in the except KeyError block return the default model name.",
            "try: return config[\"model\"]. Then except KeyError: return \"gpt-4o-mini\".",
        ],
    },
    {
        "id": "errors-s6",
        "lesson": r'''
            ## Reading the exception message

            Add `as e` to the `except` line to get the exception object. Python assigns the caught
            exception to the name `e`. You can then read its message.

            ```python
            try:
                int("ten")
            except ValueError as e:
                print("caught it")
                print(str(e))
            # caught it
            # invalid literal for int() with base 10: 'ten'
            ```

            `str(e)` returns the exception's **message** as a string. It is the same text that
            appears after the colon on the last line of a traceback.

            `e` is an ordinary variable name. `err` and `exc` are also common. The name exists only
            inside the `except` block. Python deletes it when the block ends, so using `e` after
            the block raises `NameError`.

            An f-string converts the exception the same way, so you can build a longer message.

            ```python
            try:
                int("ten")
            except ValueError as e:
                print(f"request failed: {e}")
            # request failed: invalid literal for int() with base 10: 'ten'
            ```

            In an AI app, an API call can fail for many reasons. Printing the message, or showing it
            to the user, tells them which reason it was.

            `print(e)` and `str(e)` give the message only. They do not include the type name
            `ValueError`.
        ''',
        "title": "Read the error message",
        "difficulty": 0,
        "prompt": r'''
            When a conversion fails, show the user *why*, using the exception's own message.

            **Write:** `check_number(text)`

            - `text`: a string, e.g. `"12"` or `"ten"`
            - **Returns:** the string `"ok"` when `int(text)` works, otherwise the
              **message** of the exception that `int(text)` raised (`str(e)`)

            **Rules**
            - Catch the `ValueError` with `except ValueError as e` and return its message.
            - Return the message exactly as Python wrote it, with nothing added.

            **Examples**
            ```python
            check_number("12")    # returns "ok"
            check_number("ten")   # returns "invalid literal for int() with base 10: 'ten'"
            check_number("")      # returns "invalid literal for int() with base 10: ''"
            ```
        ''',
        "starter": r'''
            def check_number(text):
                try:
                    int(text)
                except ValueError:
                    return "error"
                return "ok"
        ''',
        "tests": r'''
            from solution import check_number

            def test_number_text_returns_ok():
                got = check_number("12")
                assert got == "ok", f"got {got!r}"

            def test_bad_text_returns_the_exception_message():
                got = check_number("ten")
                assert got == "invalid literal for int() with base 10: 'ten'", f"got {got!r}"

            def test_empty_text_returns_its_message():
                got = check_number("")
                assert got == "invalid literal for int() with base 10: ''", f"got {got!r}"
        ''',
        "solution": r'''
            def check_number(text):
                try:
                    int(text)
                except ValueError as e:
                    return str(e)
                return "ok"
        ''',
        "hints": [
            "The except line can give the exception a name with `as`, so you can use it inside the block.",
            "Name the caught exception (e.g. e) and turn it into its message text with str().",
            "Change the except line to `except ValueError as e:` and return str(e) instead of \"error\".",
        ],
    },
    {
        "id": "errors-1",
        "research": {
            "note": "Skim the list of built-in exceptions to see which errors int(), dict lookups and division can raise, then come back.",
            "links": [{"title": "Built-in exceptions - Python docs",
                       "url": "https://docs.python.org/3/library/exceptions.html#concrete-exceptions"}],
        },
        "lesson": r'''
            ## Catching several types

            One `except` line can catch more than one exception type. Write the types in round
            brackets, separated by commas. This comma-separated group in round brackets is a
            **tuple**.

            ```python
            def to_number(value):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None

            print(to_number("1.5"))
            # 1.5
            print(to_number("abc"))
            # None
            print(to_number([1]))
            # None
            ```

            `float("abc")` raises `ValueError`. `float([1])` raises `TypeError`. The `except` block
            runs for either one.

            ### Why not catch everything

            `except:` with no type and `except Exception:` catch almost every exception. That
            includes exceptions caused by bugs in your own code.

            ```python
            def count_chars(text):
                try:
                    return len(txt)
                except Exception:
                    return 0

            print(count_chars("three short words"))
            # 0
            ```

            The name `txt` is a typing mistake for `text`, so the line raises `NameError`.
            `except Exception:` catches it and the function returns `0`. No error is shown, and the
            caller cannot tell this `0` from a correct count.

            Catch only the types you expect. Any other exception then stops the program with a
            traceback that shows you the line to fix.
        ''',
        "title": "Safe token count",
        "hints": [
            "Wrap the risky int(value) call in try, and handle the failures in except.",
            "An except clause can catch several types at once if you put them in a tuple. In that case return 0.",
            "try: return int(value). Then except (ValueError, TypeError): return 0. Do not use a bare except or except Exception.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Usage data from an API sometimes arrives as strings, and sometimes is junk.
            Turn it into a token count without crashing.

            **Write:** `parse_tokens(value)`

            - `value`: anything, usually a string like `"42"` or an int like `7`, but it
              can be junk like `"n/a"` or `None`
            - **Returns:** `int(value)` as an int, or `0` when the conversion fails

            **Rules**
            - `int("n/a")` raises `ValueError` and `int(None)` raises `TypeError`: in both
              cases return `0`.
            - Catch **only** `ValueError` and `TypeError`, by name. A check rejects a bare
              `except:` and `except Exception` (these are too broad).

            **Examples**
            ```python
            parse_tokens("42")    # returns 42
            parse_tokens(7)       # returns 7
            parse_tokens("n/a")   # returns 0
            parse_tokens(None)    # returns 0
            ```
        ''',
        "starter": r'''
            def parse_tokens(value):
                return int(value)
        ''',
        "tests": r'''
            from solution import parse_tokens

            def test_number_strings_and_ints_are_converted():
                assert parse_tokens("42") == 42
                assert parse_tokens(7) == 7

            def test_non_number_string_returns_zero():
                assert parse_tokens("n/a") == 0, f"got {parse_tokens('n/a')!r}"

            def test_none_returns_zero():
                assert parse_tokens(None) == 0, f"got {parse_tokens(None)!r}"

            def test_catches_only_valueerror_and_typeerror_by_name():
                import ast
                for n in ast.walk(ast.parse(source())):
                    if isinstance(n, ast.ExceptHandler):
                        assert n.type is not None, "no bare except: - name the exception types"
                        names = [e.id for e in ast.walk(n.type) if isinstance(e, ast.Name)]
                        assert "Exception" not in names and "BaseException" not in names, \
                            "catch the specific exception types only"
        ''',
        "solution": r'''
            def parse_tokens(value):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return 0
        ''',
    },
    {
        "id": "errors-2",
        "lesson": r'''
            ## Validating input

            To **validate** a value is to check that it is acceptable before you use it. Write one
            `if` per rule. Each `if` raises an exception when its rule is broken. The first broken
            rule stops the function, so later checks do not run.

            `isinstance(value, int)` returns `True` when `value` is an int. Pass a tuple of types
            to accept any of them.

            ```python
            print(isinstance(5, int))
            # True
            print(isinstance("5", int))
            # False
            print(isinstance(0.5, (int, float)))
            # True
            ```

            Raise `TypeError` when the value has the wrong type, such as a string where a number
            is required. Raise `ValueError` when the type is right but the value is out of range.

            ```python
            def check_top_k(top_k):
                if not isinstance(top_k, int) or isinstance(top_k, bool):
                    raise TypeError("top_k must be an int")
                if top_k < 1:
                    raise ValueError("top_k must be at least 1")

            check_top_k(40)
            print("40 is valid")
            # 40 is valid
            try:
                check_top_k("40")
            except TypeError as e:
                print(e)
            # top_k must be an int
            ```

            Put the parameter's name in the message. `"top_k must be an int"` tells the caller
            which argument to fix.

            Checking at the start of a function is called **failing fast**. The error appears at
            the call with the bad value, not later in a line that only uses it.

            `isinstance(True, int)` returns `True`, because Python defines `bool` as a
            **sub-type** of `int`: every bool also counts as an int. To reject `True` and `False`, add the `isinstance(x, bool)` check shown above.
        ''',
        "title": "Validate generation params",
        "hints": [
            "Use isinstance() to check types, comparisons to check ranges, and raise to report a problem. Watch out: True and False count as ints for isinstance.",
            "Do four checks one after another, each an if that raises. For the type checks, also reject values where isinstance(x, bool) is True.",
            "1) if max_tokens is not an int or is a bool: raise TypeError naming max_tokens. 2) if max_tokens < 1: raise ValueError. 3) if temperature is not (int, float) or is a bool: raise TypeError. 4) if not 0 <= temperature <= 2: raise ValueError. If nothing raised, the function ends and returns None.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Check generation parameters before sending them to a model API, and fail
            early with a clear error.

            **Write:** `validate_params(max_tokens, temperature)`

            - `max_tokens`: should be an int, e.g. `256`
            - `temperature`: should be an int or a float, e.g. `0.7`
            - **Returns:** `None` when both are valid (just let the function end)

            **Rules** (check in this order and raise at the first problem)
            1. `max_tokens` is not an `int` -> raise `TypeError`. A float like `12.0`, a
               string like `"256"` and a bool like `True` are all rejected (careful:
               Python counts `True`/`False` as ints, so reject bools explicitly).
            2. `max_tokens` is less than `1` -> raise `ValueError`.
            3. `temperature` is not an `int` or `float` -> raise `TypeError` (bools like
               `False` rejected too).
            4. `temperature` is below `0` or above `2` -> raise `ValueError`. `0` and `2`
               themselves are valid.
            - Every error message must contain the parameter's name (`"max_tokens"` or
              `"temperature"`), e.g. `"max_tokens must be an int"`.
            - When both are wrong, the `max_tokens` error wins (it is checked first).

            **Examples**
            ```python
            validate_params(256, 0.7)     # returns None
            validate_params(1, 2)         # returns None
            validate_params("256", 0.7)   # raises TypeError("max_tokens must be an int")
            validate_params(0, 0.7)       # raises ValueError (message mentions max_tokens)
            validate_params(10, "hot")    # raises TypeError (message mentions temperature)
            validate_params(256, 2.5)     # raises ValueError("temperature must be between 0 and 2")
            ```
        ''',
        "starter": r'''
            def validate_params(max_tokens, temperature):
                ...
        ''',
        "tests": r'''
            from solution import validate_params

            def raises(exc_type, *args):
                try:
                    validate_params(*args)
                except exc_type as e:
                    return str(e)
                except Exception as e:
                    raise AssertionError(f"validate_params{args!r} raised {type(e).__name__}, expected {exc_type.__name__}")
                raise AssertionError(f"validate_params{args!r} did not raise {exc_type.__name__}")

            def test_valid_params_return_none_including_limits():
                assert validate_params(256, 0.7) is None
                assert validate_params(1, 0) is None
                assert validate_params(1, 2) is None

            def test_non_int_or_bool_max_tokens_raises_typeerror():
                msg = raises(TypeError, "256", 0.7)
                assert "max_tokens" in msg, f"message {msg!r} should name the parameter"
                raises(TypeError, 12.0, 0.7)
                raises(TypeError, True, 0.7)

            def test_max_tokens_below_one_raises_valueerror():
                msg = raises(ValueError, 0, 0.7)
                assert "max_tokens" in msg, f"message {msg!r} should name the parameter"

            def test_non_number_or_bool_temperature_raises_typeerror():
                msg = raises(TypeError, 10, "hot")
                assert "temperature" in msg, f"message {msg!r} should name the parameter"
                raises(TypeError, 10, False)

            def test_temperature_outside_0_to_2_raises_valueerror():
                msg = raises(ValueError, 10, 2.5)
                assert "temperature" in msg, f"message {msg!r} should name the parameter"
                raises(ValueError, 10, -0.1)

            def test_max_tokens_is_checked_before_temperature():
                raises(TypeError, "x", 99)
        ''',
        "solution": r'''
            def validate_params(max_tokens, temperature):
                if not isinstance(max_tokens, int) or isinstance(max_tokens, bool):
                    raise TypeError("max_tokens must be an int")
                if max_tokens < 1:
                    raise ValueError("max_tokens must be at least 1")
                if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
                    raise TypeError("temperature must be a number")
                if not 0 <= temperature <= 2:
                    raise ValueError("temperature must be between 0 and 2")
        ''',
    },
    {
        "id": "errors-7",
        "lesson": r'''
            ## Custom exceptions

            The built-in exception names are general. A **custom exception** is an exception type
            you define yourself, with a name that describes a problem in your program, such as
            `RateLimitError` or `TooLongError`.

            You define one with a **class**: a statement that creates a new type. Write `class`,
            the new name, and `Exception` in parentheses. The body is the single word `pass`.

            ```python
            class TooLongError(Exception):
                pass

            def check_prompt(text):
                if len(text) > 10:
                    raise TooLongError("prompt too long")
                return text

            print(check_prompt("hi"))
            # hi
            try:
                check_prompt("a very long prompt")
            except TooLongError as e:
                print("caught:", e)
            # caught: prompt too long
            ```

            `(Exception)` makes the new type a kind of `Exception`, so it works with `raise` and
            `except`. `pass` is a statement that does nothing. It is there because a class body
            cannot be empty.

            Classes are covered in a later topic. For now, copy the two-line form and change the
            name.

            The new type works the same way as the built-in ones. You raise it with a message,
            catch it by name, and read the message with `str(e)`.

            `except TooLongError:` catches only that type. A `ValueError` raised by the same code
            is not caught, so callers can handle each problem separately.

            Python runs the file from top to bottom. Define the class before the first line that
            raises it runs. Raising a name that is not defined yet raises `NameError`.
        ''',
        "title": "Your own exception",
        "difficulty": 1,
        "prompt": r'''
            An agent has a spending budget for API calls. When a call would cost more
            than what's left, stop with an error type of your own (a *custom exception*).

            **Write:** a class `BudgetExceededError`, then `spend(budget, cost)`

            - `BudgetExceededError`: a one-line custom exception based on `Exception`
              (`class Name(Exception): pass`)
            - `budget`: a number, the dollars left, e.g. `1.0`
            - `cost`: a number, the price of the next call, e.g. `0.25`
            - **Returns:** the budget left after paying, `budget - cost`

            **Rules**
            - If `cost` is greater than `budget`, raise
              `BudgetExceededError("budget exceeded")` (exactly this message).
            - Spending exactly the whole budget is allowed (returns `0`).

            **Examples**
            ```python
            spend(1.0, 0.25)   # returns 0.75
            spend(2, 2)        # returns 0
            spend(1.0, 1.5)    # raises BudgetExceededError("budget exceeded")
            ```
        ''',
        "starter": r'''
            def spend(budget, cost):
                return budget - cost
        ''',
        "tests": r'''
            import solution

            def test_budget_exceeded_error_is_an_exception_class():
                assert issubclass(solution.BudgetExceededError, Exception)

            def test_returns_what_is_left():
                assert solution.spend(1.0, 0.25) == 0.75
                assert solution.spend(2, 2) == 0, "spending the whole budget is allowed"

            def test_too_expensive_raises_budget_exceeded_error():
                try:
                    solution.spend(1.0, 1.5)
                except solution.BudgetExceededError as e:
                    assert str(e) == "budget exceeded", f"message was {str(e)!r}"
                else:
                    raise AssertionError("spend(1.0, 1.5) should raise BudgetExceededError")
        ''',
        "solution": r'''
            class BudgetExceededError(Exception):
                pass


            def spend(budget, cost):
                if cost > budget:
                    raise BudgetExceededError("budget exceeded")
                return budget - cost
        ''',
        "hints": [
            "First create the exception type with the two-line class form, then use raise inside spend.",
            "Define the class above the function. In spend, check whether cost is bigger than budget before doing the subtraction.",
            "Write class BudgetExceededError(Exception): with pass inside. In spend: if cost > budget, raise BudgetExceededError with the message \"budget exceeded\"; otherwise return budget minus cost.",
        ],
    },
    {
        "id": "errors-8",
        "lesson": r'''
            ## finally

            A `finally` block holds code that runs every time the `try` block ends, whichever way
            it ends.

            ```python
            def risky(n):
                print("open")
                try:
                    return 10 / n
                finally:
                    print("close")

            print(risky(2))
            # open
            # close
            # 5.0
            try:
                risky(0)
            except ZeroDivisionError:
                print("error reached the caller")
            # open
            # close
            # error reached the caller
            ```

            The `finally` block runs in all three cases:

            - The `try` block reaches its end.
            - The `try` block runs `return`. Python runs `finally` first, then returns the value.
            - The `try` block raises an exception. Python runs `finally` first, then the exception
              continues to the caller.

            `finally` does not catch the exception. `risky(0)` prints `close` and the
            `ZeroDivisionError` still reaches the caller.

            Step through both calls and watch line 6 run after line 4 each time.

            ```diagram
            {"type": "trace", "title": "finally runs on return and on an exception", "code": ["def risky(n):", "    print(\"open\")", "    try:", "        return 10 / n", "    finally:", "        print(\"close\")", "", "print(risky(2))", "try:", "    risky(0)", "except ZeroDivisionError:", "    print(\"error reached the caller\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 8, "vars": {}, "out": ""},
              {"line": 2, "vars": {"n": "2"}, "out": ""},
              {"line": 3, "vars": {"n": "2"}, "out": "open\n"},
              {"line": 4, "vars": {"n": "2"}, "out": "open\n"},
              {"line": 6, "vars": {"n": "2"}, "out": "open\n"},
              {"line": 9, "vars": {}, "out": "open\nclose\n5.0\n"},
              {"line": 10, "vars": {}, "out": "open\nclose\n5.0\n"},
              {"line": 2, "vars": {"n": "0"}, "out": "open\nclose\n5.0\n"},
              {"line": 3, "vars": {"n": "0"}, "out": "open\nclose\n5.0\nopen\n"},
              {"line": 4, "vars": {"n": "0"}, "out": "open\nclose\n5.0\nopen\n"},
              {"line": 6, "vars": {"n": "0"}, "out": "open\nclose\n5.0\nopen\n"},
              {"line": 11, "vars": {}, "out": "open\nclose\n5.0\nopen\nclose\n"},
              {"line": 12, "vars": {}, "out": "open\nclose\n5.0\nopen\nclose\n"},
              {"line": null, "vars": {}, "out": "open\nclose\n5.0\nopen\nclose\nerror reached the caller\n"}
            ]}
            ```

            A `try` statement can have `finally` and no `except`. Use this form for **cleanup**:
            work that must happen in every case, such as closing a file, stopping a timer or
            printing a "done" message.

            Do not write `return` inside `finally`. That `return` discards the exception, and the
            caller never sees the error.
        ''',
        "title": "Always log the end",
        "difficulty": 1,
        "research": {
            "note": "Read the section on clean-up actions (finally) in the official tutorial, then come back.",
            "links": [{"title": "Defining clean-up actions - Python tutorial",
                       "url": "https://docs.python.org/3/tutorial/errors.html#defining-clean-up-actions"}],
        },
        "prompt": r'''
            Every model call should leave a trace in the log: when it started and when it
            ended, even if it crashed.

            **Write:** `logged_call(func, log)`

            - `func`: a function with no arguments; you call it as `func()`
            - `log`: a list of strings you append to, e.g. `[]`
            - **Returns:** whatever `func()` returned

            **Rules**
            - Append `"start"` to `log` before calling `func`.
            - Append `"end"` to `log` after the call, **in every case**, using a `finally`
              block (a check looks for it).
            - Don't catch any exception: if `func()` raises, the same exception must reach
              the caller (after `"end"` was logged).

            **Examples**
            ```python
            def answer():
                return 42

            def crash():
                return 1 / 0

            log = []
            logged_call(answer, log)   # returns 42; log is now ["start", "end"]

            log = []
            logged_call(crash, log)    # raises ZeroDivisionError; log is now ["start", "end"]
            ```
        ''',
        "starter": r'''
            def logged_call(func, log):
                log.append("start")
                result = func()
                log.append("end")
                return result
        ''',
        "tests": r'''
            from solution import logged_call

            def answer():
                return 42

            def crash():
                return 1 / 0

            def test_success_returns_result_and_logs_start_end():
                log = []
                got = logged_call(answer, log)
                assert got == 42, f"returned {got!r}"
                assert log == ["start", "end"], f"log is {log!r}"

            def test_error_reaches_caller_and_end_is_still_logged():
                log = []
                try:
                    logged_call(crash, log)
                except ZeroDivisionError:
                    pass
                else:
                    raise AssertionError("the ZeroDivisionError should reach the caller")
                assert log == ["start", "end"], f"log is {log!r}"

            def test_code_uses_finally():
                import ast
                tries = [n for n in ast.walk(ast.parse(source())) if isinstance(n, ast.Try)]
                assert tries and tries[0].finalbody, "use a try block with finally"
        ''',
        "solution": r'''
            def logged_call(func, log):
                log.append("start")
                try:
                    return func()
                finally:
                    log.append("end")
        ''',
        "hints": [
            "A try block doesn't need an except: try + finally is enough when you only want cleanup.",
            "Log \"start\", then put the func() call in try, and the \"end\" logging in finally.",
            "Append \"start\". Then try: return func(). Then finally: append \"end\". No except block at all.",
        ],
    },
    {
        "id": "errors-3",
        "title": "API error hierarchy",
        "hints": [
            "Custom exceptions are one-line classes: class Name(Parent): pass. Using another custom exception as the parent makes a sub-type. except catches the named type AND its sub-types.",
            "raise_for_status picks which exception to raise based on the status code. describe_failure calls it inside try and has one except block per type. The specific ones (AuthError, RateLimitError) must come before APIError.",
            "Define APIError(Exception), RateLimitError(APIError), AuthError(APIError), each with pass. raise_for_status: return None for 200..299; message = body.get(\"error\", \"unknown error\"); raise AuthError(message) for 401/403, RateLimitError(message) for 429, otherwise APIError(message). describe_failure: try raise_for_status and return \"ok\"; except AuthError as e: return f\"auth: {e}\"; then RateLimitError, then APIError.",
        ],
        "difficulty": 2,
        "prompt": r'''
            An LLM client turns HTTP status codes into specific exceptions, so callers can
            handle "bad API key" differently from "slow down". Sub-types of one base error
            form an *exception hierarchy*.

            **Write:** three exception classes, then `raise_for_status(status, body)` and
            `describe_failure(status, body)`

            - Classes (one-line classes, `class Name(Parent): pass`):
              - `APIError`, based on `Exception` (already in the starter)
              - `RateLimitError`, based on `APIError`
              - `AuthError`, based on `APIError` (not on `RateLimitError`)
            - `status`: an int HTTP status code, e.g. `200`, `429`
            - `body`: a dict, e.g. `{"error": "slow down"}` or `{}`
            - **`raise_for_status` returns:** `None` when the status is OK, otherwise raises
            - **`describe_failure` returns:** a label string like `"auth: bad key"`

            **Rules for `raise_for_status`**
            - Status `200` to `299` (both included): return `None`.
            - Otherwise raise, with message `body["error"]`, or `"unknown error"` when the
              body has no `"error"` key:
              - `401` or `403` -> `AuthError`
              - `429` -> `RateLimitError`
              - any other code (e.g. `300`, `404`, `500`) -> `APIError` itself
            - The exception's message is exactly that text (so `str(error)` is `"slow down"`).

            **Rules for `describe_failure`**
            - Call `raise_for_status(status, body)`; don't let its error escape.
            - Return `"ok"` when nothing was raised.
            - Otherwise return `"auth: <message>"`, `"rate limit: <message>"` or
              `"api error: <message>"` depending on the error type.

            **Examples**
            ```python
            raise_for_status(200, {})                      # returns None
            raise_for_status(429, {"error": "slow down"})  # raises RateLimitError("slow down")
            raise_for_status(404, {})                      # raises APIError("unknown error")
            describe_failure(200, {})                      # returns "ok"
            describe_failure(403, {"error": "bad key"})    # returns "auth: bad key"
            describe_failure(429, {"error": "slow down"})  # returns "rate limit: slow down"
            describe_failure(500, {})                      # returns "api error: unknown error"
            ```
        ''',
        "starter": r'''
            class APIError(Exception):
                pass


            def raise_for_status(status, body):
                ...


            def describe_failure(status, body):
                ...
        ''',
        "tests": r'''
            from solution import APIError, RateLimitError, AuthError, raise_for_status, describe_failure

            def catch(status, body):
                try:
                    raise_for_status(status, body)
                except Exception as e:
                    return e
                return None

            def test_ratelimit_and_auth_errors_are_apierror_subclasses():
                assert issubclass(RateLimitError, APIError)
                assert issubclass(AuthError, APIError)
                assert issubclass(APIError, Exception)
                assert not issubclass(AuthError, RateLimitError)

            def test_success_codes_return_none():
                for s in (200, 201, 299):
                    assert catch(s, {}) is None, f"status {s} raised"

            def test_429_raises_ratelimiterror_with_body_message():
                e = catch(429, {"error": "slow down"})
                assert type(e) is RateLimitError, f"got {type(e).__name__}"
                assert str(e) == "slow down", f"message is {str(e)!r}"

            def test_401_and_403_raise_autherror():
                for s in (401, 403):
                    e = catch(s, {"error": "bad key"})
                    assert type(e) is AuthError, f"status {s} raised {type(e).__name__}"
                    assert str(e) == "bad key"

            def test_other_codes_raise_apierror_with_unknown_error():
                for s in (300, 404, 500, 503):
                    e = catch(s, {})
                    assert type(e) is APIError, f"status {s} raised {type(e).__name__}"
                    assert str(e) == "unknown error", f"message is {str(e)!r}"

            def test_describe_failure_returns_ok_or_labels():
                assert describe_failure(200, {}) == "ok"
                got = describe_failure(403, {"error": "bad key"})
                assert got == "auth: bad key", f"got {got!r}"
                got = describe_failure(429, {"error": "slow down"})
                assert got == "rate limit: slow down", f"got {got!r}"
                got = describe_failure(500, {})
                assert got == "api error: unknown error", f"got {got!r}"
        ''',
        "solution": r'''
            class APIError(Exception):
                pass


            class RateLimitError(APIError):
                pass


            class AuthError(APIError):
                pass


            def raise_for_status(status, body):
                if 200 <= status <= 299:
                    return None
                message = body.get("error", "unknown error")
                if status in (401, 403):
                    raise AuthError(message)
                if status == 429:
                    raise RateLimitError(message)
                raise APIError(message)


            def describe_failure(status, body):
                try:
                    raise_for_status(status, body)
                except AuthError as e:
                    return f"auth: {e}"
                except RateLimitError as e:
                    return f"rate limit: {e}"
                except APIError as e:
                    return f"api error: {e}"
                return "ok"
        ''',
    },
    {
        "id": "errors-4",
        "placement": True,
        "title": "Step runner with cleanup",
        "hints": [
            "A try statement can have four parts: try, except, else (runs only if try raised nothing) and finally (always runs).",
            "Only call step() inside try. Handle KeyError in except. Put the success logging and return in else. Put the \"done\" logging in finally.",
            "try: result = step(). except KeyError: append \"missing key\" and return None. else: append \"ok\" and return result. finally: append \"done\". Do not catch any other exception type.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A pipeline runs one step at a time and keeps a log of what happened. Some
            failures are expected and handled; others must reach the caller, but the log
            must always be closed.

            **Write:** `run_step(step, log)`

            - `step`: a function that takes no arguments, e.g. `works` below. You call it
              as `step()`.
            - `log`: a list of strings you append to, e.g. `[]`
            - **Returns:** whatever `step()` returned, or `None` when it raised `KeyError`

            **Rules**
            - Use one `try` statement with `except`, `else` **and** `finally` blocks (a
              check looks for the `else` and the `finally`).
            - Only the `step()` call goes inside `try`.
            - If `step()` raises `KeyError`: append `"missing key"` to `log` and return
              `None` (the error is swallowed).
            - If `step()` succeeds: in the `else` block, append `"ok"` to `log` and return
              the result. Because this is in `else`, a `KeyError` raised while appending
              `"ok"` is **not** caught: it propagates to the caller.
            - Any other exception from `step()` (e.g. `ZeroDivisionError`) is **not**
              caught: it propagates to the caller.
            - In **every** case, `"done"` is appended to `log` last (in `finally`), even
              when an exception propagates.

            **Examples**
            ```python
            def works():
                return 5

            def missing():
                return {}["x"]

            def broken():
                return 1 / 0

            log = []
            run_step(works, log)      # returns 5;    log is now ["ok", "done"]

            log = []
            run_step(missing, log)    # returns None; log is now ["missing key", "done"]

            log = []
            run_step(broken, log)     # raises ZeroDivisionError; log is now ["done"]
            ```

            Note: the function itself is passed in (`works`, no brackets); `run_step`
            calls it.
        ''',
        "starter": r'''
            def run_step(step, log):
                ...
        ''',
        "tests": r'''
            from solution import run_step

            def test_success_returns_result_and_logs_ok_then_done():
                log = []
                got = run_step(lambda: 5, log)
                assert got == 5, f"returned {got!r}"
                assert log == ["ok", "done"], f"log is {log!r}"

            def test_key_error_returns_none_and_logs_missing_key_then_done():
                log = []
                got = run_step(lambda: {}["x"], log)
                assert got is None
                assert log == ["missing key", "done"], f"log is {log!r}"

            def test_other_errors_propagate_and_log_done():
                log = []
                try:
                    run_step(lambda: 1 / 0, log)
                except ZeroDivisionError:
                    pass
                else:
                    raise AssertionError("ZeroDivisionError should propagate")
                assert log == ["done"], f"log is {log!r}"

            def test_code_uses_try_with_else_and_finally():
                import ast
                tries = [n for n in ast.walk(ast.parse(source())) if isinstance(n, ast.Try)]
                assert tries, "use a try statement"
                t = tries[0]
                assert t.orelse, "put the success handling in an else block"
                assert t.finalbody, "use finally for the cleanup"

            def test_key_error_while_logging_ok_is_not_caught():
                class ExplodingLog(list):
                    def append(self, item):
                        if item == "ok":
                            raise KeyError("log is broken")
                        super().append(item)
                log = ExplodingLog()
                try:
                    run_step(lambda: 1, log)
                except KeyError:
                    pass
                else:
                    raise AssertionError("an error in the success path must not be caught as a step failure")
                assert list(log) == ["done"], f"log is {list(log)!r}"
        ''',
        "solution": r'''
            def run_step(step, log):
                try:
                    result = step()
                except KeyError:
                    log.append("missing key")
                    return None
                else:
                    log.append("ok")
                    return result
                finally:
                    log.append("done")
        ''',
    },
    {
        "id": "errors-5",
        "title": "Retry with backoff",
        "hints": [
            "Loop a fixed number of times with a try/except inside. A bare `raise` inside an except block re-raises the exception currently being handled.",
            "On success return straight away. On a retryable error, if it was the last attempt re-raise it; otherwise sleep for the current delay and double the delay.",
            "Validate attempts first (ValueError if < 1). Set delay = 1. For each attempt number from 1 to attempts: try return func(); except (TimeoutError, ConnectionError): if this is the last attempt, `raise`; if sleep is not None call sleep(delay); multiply delay by 2.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Network calls to a model API fail now and then. Retry the temporary failures,
            waiting longer each time (this is called *exponential backoff*).

            **Write:** `call_with_retry(func, attempts=3, sleep=None)`

            - `func`: a function with no arguments; you call it as `func()`
            - `attempts`: an int, the maximum number of calls **in total** (default `3`)
            - `sleep`: a function taking a number of seconds, e.g. `time.sleep`, or `None`
              (default) meaning "don't wait". Tests pass a function that records the values.
            - **Returns:** the result of the first `func()` call that succeeds

            **Rules**
            - If `attempts` is less than `1`, raise `ValueError` **before** calling `func`.
            - A call that succeeds is returned straight away (no sleep, no more calls).
            - If `func()` raises `TimeoutError` or `ConnectionError`, try again, up to
              `attempts` calls in total.
            - Between two attempts, if `sleep` is not `None`, call `sleep(delay)` with
              delays `1`, then `2`, then `4`, ... (doubling). Never sleep after the final
              attempt.
            - If every attempt fails, re-raise the **last** exception: the very same
              exception object, not a new one.
            - Any **other** exception (e.g. `KeyError`) propagates immediately, with no
              retry.

            **Examples**
            ```python
            calls = []

            def flaky():
                calls.append(1)
                if len(calls) < 3:
                    raise TimeoutError("too slow")
                return "ok"

            call_with_retry(flaky, attempts=5, sleep=print)   # prints 1, then 2; returns "ok"
            ```
            With `attempts=3` and a `func` that always raises `TimeoutError`: `func` is
            called 3 times, `sleep` receives `1` then `2`, and the third `TimeoutError`
            is raised. `call_with_retry(func, attempts=0)` raises `ValueError`.
        ''',
        "starter": r'''
            def call_with_retry(func, attempts=3, sleep=None):
                ...
        ''',
        "tests": r'''
            from solution import call_with_retry

            def flaky(*outcomes):
                calls = []
                it = iter(outcomes)
                def func():
                    calls.append(1)
                    r = next(it)
                    if isinstance(r, BaseException):
                        raise r
                    return r
                return func, calls

            def test_success_on_first_call_returns_without_sleeping():
                f, calls = flaky("ok")
                sleeps = []
                assert call_with_retry(f, sleep=sleeps.append) == "ok"
                assert len(calls) == 1 and sleeps == [], f"calls={len(calls)} sleeps={sleeps}"

            def test_retries_temporary_errors_with_1_then_2_second_waits():
                f, calls = flaky(TimeoutError("t1"), ConnectionError("c"), "ok")
                sleeps = []
                got = call_with_retry(f, attempts=5, sleep=sleeps.append)
                assert got == "ok", f"got {got!r}"
                assert sleeps == [1, 2], f"slept {sleeps}"

            def test_after_last_attempt_reraises_the_same_last_exception():
                last = TimeoutError("third")
                f, calls = flaky(TimeoutError("1"), ConnectionError("2"), last, "never")
                sleeps = []
                try:
                    call_with_retry(f, attempts=3, sleep=sleeps.append)
                except TimeoutError as e:
                    assert e is last, f"re-raise the last exception itself, got {e!r}"
                else:
                    raise AssertionError("should raise after all attempts fail")
                assert len(calls) == 3, f"made {len(calls)} calls, expected 3"
                assert sleeps == [1, 2], f"slept {sleeps} (no sleep after the last attempt)"

            def test_other_errors_propagate_without_retry():
                f, calls = flaky(KeyError("k"), "ok")
                try:
                    call_with_retry(f, attempts=3)
                except KeyError:
                    pass
                else:
                    raise AssertionError("KeyError should propagate")
                assert len(calls) == 1, f"retried a non-retryable error ({len(calls)} calls)"

            def test_works_when_sleep_is_none():
                f, calls = flaky(ConnectionError("x"), 42)
                assert call_with_retry(f) == 42

            def test_attempts_below_one_raises_valueerror_before_calling():
                f, calls = flaky("ok")
                try:
                    call_with_retry(f, attempts=0)
                except ValueError:
                    assert calls == [], "validate before calling func"
                    return
                raise AssertionError("attempts=0 should raise ValueError")
        ''',
        "solution": r'''
            def call_with_retry(func, attempts=3, sleep=None):
                if attempts < 1:
                    raise ValueError("attempts must be at least 1")
                delay = 1
                for attempt in range(1, attempts + 1):
                    try:
                        return func()
                    except (TimeoutError, ConnectionError):
                        if attempt == attempts:
                            raise
                        if sleep is not None:
                            sleep(delay)
                        delay *= 2
        ''',
    },
    {
        "id": "errors-6",
        "title": "Chain parse errors",
        "hints": [
            "You need a one-line custom exception class, dict lookups with .get(), int() inside a try, and `raise ... from ...` for chaining.",
            "parse_tool_call validates the name, reads the args list (default empty) and, for \"add\", converts every arg inside a try so a ValueError can be re-raised as a ToolCallError from it. run_all loops over the calls, catches only ToolCallError, and builds one line per call.",
            "class ToolCallError(Exception): pass. parse_tool_call: name = call.get(\"name\"); if not name raise ToolCallError(\"malformed tool call\"); args = call.get(\"args\", []); if name is \"add\": try building a new list with int(a) for each a, except ValueError as exc: raise ToolCallError(\"bad arguments for add\") from exc. Return (name, args). run_all: for each call, try parse; except ToolCallError as e append f\"error: {e}\"; else append f\"{name} -> {args}\". Return the list.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A model asks your app to call tools. Each tool call arrives as a dict like
            `{"name": "search", "args": ["cats", "dogs"]}`. Parse them, and report bad
            ones with your own exception type.

            **Write:** a class `ToolCallError`, then `parse_tool_call(call)` and `run_all(calls)`

            - `ToolCallError`: a one-line custom exception class based on `Exception`
            - `call`: a dict with a `"name"` string and an optional `"args"` list
            - `calls`: a list of such dicts
            - **`parse_tool_call` returns:** a tuple `(name, args)`, e.g. `("now", [])`
            - **`run_all` returns:** a list of strings, one per call, in the same order

            **Rules for `parse_tool_call`**
            - If `"name"` is missing or is the empty string `""`, raise
              `ToolCallError("malformed tool call")`.
            - A missing `"args"` means `[]`.
            - Args are returned unchanged, **except** when the name is `"add"`: then
              return a new list with every arg converted by `int()` (e.g. `["1", "20"]`
              -> `[1, 20]`).
            - If `int()` raises `ValueError` for an `"add"` arg, raise
              `ToolCallError("bad arguments for add")` **chained** from that `ValueError`
              (this is called *exception chaining*: `raise NewError(...) from original`,
              so the new error's `__cause__` is the `ValueError`).
            - Only `ValueError` is converted. Any other error (e.g. `int(None)` raises
              `TypeError`) is not caught.
            - Never change the caller's dict or args list.

            **Rules for `run_all`**
            - For each call, add `"<name> -> <args>"` where `<args>` is the list as
              Python prints it (e.g. `"search -> ['cats', 'dogs']"`).
            - If parsing raised `ToolCallError`, add `"error: <message>"` instead.
            - Catch only `ToolCallError`: a `TypeError` (e.g. from `"args": [None]` on
              `"add"`) must propagate out of `run_all`.

            **Examples**
            ```python
            parse_tool_call({"name": "search", "args": ["cats", "dogs"]})  # returns ("search", ["cats", "dogs"])
            parse_tool_call({"name": "now"})                               # returns ("now", [])
            parse_tool_call({"name": "add", "args": ["1", "20"]})          # returns ("add", [1, 20])
            parse_tool_call({"name": "", "args": []})    # raises ToolCallError("malformed tool call")
            parse_tool_call({"name": "add", "args": ["1", "x"]})
            # raises ToolCallError("bad arguments for add"), chained from the ValueError

            run_all([{"name": "search", "args": ["cats", "dogs"]},
                     {"name": "add", "args": ["1", "2"]},
                     {"name": "add", "args": ["1", "x"]},
                     {"args": ["oops"]}])
            # returns ["search -> ['cats', 'dogs']", "add -> [1, 2]",
            #          "error: bad arguments for add", "error: malformed tool call"]
            ```
        ''',
        "starter": r'''
            def parse_tool_call(call):
                ...


            def run_all(calls):
                ...
        ''',
        "tests": r'''
            import solution

            def test_returns_name_and_args_tuple_with_add_args_as_ints():
                assert solution.parse_tool_call({"name": "search", "args": ["cats", "dogs"]}) == ("search", ["cats", "dogs"])
                assert solution.parse_tool_call({"name": "now"}) == ("now", [])
                got = solution.parse_tool_call({"name": "add", "args": ["1", "20"]})
                assert got == ("add", [1, 20]), f"got {got!r}"

            def test_missing_or_empty_name_raises_toolcallerror():
                assert issubclass(solution.ToolCallError, Exception)
                for call in ({"args": ["x"]}, {"name": "", "args": []}):
                    try:
                        solution.parse_tool_call(call)
                    except solution.ToolCallError as e:
                        assert str(e) == "malformed tool call", f"message was {str(e)!r}"
                    else:
                        raise AssertionError(f"{call!r} should raise ToolCallError")

            def test_bad_add_args_raise_toolcallerror_chained_from_valueerror():
                try:
                    solution.parse_tool_call({"name": "add", "args": ["1", "x"]})
                except solution.ToolCallError as e:
                    assert str(e) == "bad arguments for add", f"message was {str(e)!r}"
                    assert isinstance(e.__cause__, ValueError), "chain it from the ValueError with raise ... from"
                else:
                    raise AssertionError("add with a non-number should raise ToolCallError")

            def test_callers_args_list_is_not_changed():
                args = ["1", "2"]
                solution.parse_tool_call({"name": "add", "args": args})
                assert args == ["1", "2"], f"the caller's list was changed to {args!r}"

            def test_run_all_returns_one_line_per_call():
                got = solution.run_all([
                    {"name": "search", "args": ["cats", "dogs"]},
                    {"name": "add", "args": ["1", "2"]},
                    {"name": "add", "args": ["1", "x"]},
                    {"args": ["oops"]},
                ])
                want = ["search -> ['cats', 'dogs']", "add -> [1, 2]",
                        "error: bad arguments for add", "error: malformed tool call"]
                assert got == want, f"got {got!r}"

            def test_run_all_lets_other_errors_propagate():
                try:
                    solution.run_all([{"name": "add", "args": [None]}])
                except TypeError:
                    return
                raise AssertionError("only ToolCallError should be caught (int(None) raises TypeError)")
        ''',
        "solution": r'''
            class ToolCallError(Exception):
                pass


            def parse_tool_call(call):
                name = call.get("name")
                if not name:
                    raise ToolCallError("malformed tool call")
                args = call.get("args", [])
                if name == "add":
                    try:
                        numbers = []
                        for arg in args:
                            numbers.append(int(arg))
                    except ValueError as exc:
                        raise ToolCallError("bad arguments for add") from exc
                    args = numbers
                return name, args


            def run_all(calls):
                lines = []
                for call in calls:
                    try:
                        name, args = parse_tool_call(call)
                    except ToolCallError as exc:
                        lines.append(f"error: {exc}")
                    else:
                        lines.append(f"{name} -> {args}")
                return lines
        ''',
    },
]
