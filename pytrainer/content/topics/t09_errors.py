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
            ## Carrying on after a line fails

            Your chat app asks how many answers the user wants, and the user types `three`. You know from
            the Data Types chapter what `int("three")` does. It cannot make a number out of that text, so
            Python stops the whole program with an error:

            ```text
            ValueError: invalid literal for int() with base 10: 'three'
            ```

            Stopping is what Python does when nobody has told it what else to do. One bad value should
            not end a whole app, though. You can tell Python in advance: try these lines, and if one of
            them fails, do this instead.

            ```python
            try:
                count = int("three")
                print("you asked for", count)
            except ValueError:
                print("that is not a number")
            print("still running")
            # that is not a number
            # still running
            ```

            Here is what happened, in order:

            1. Python started on the lines that are indented under `try:`.
            2. `int("three")` failed. Python left the `try` block at that line, so the `print` under it
               never ran.
            3. Python jumped to the lines under `except ValueError:` and ran those.
            4. It carried on with the first line after the whole statement. No error message appeared,
               and the program did not stop.

            Now the names. What Python creates when a line fails is called an **exception**. Programmers
            say that the line **raises** an exception, and that the `except` block **catches** it.
            `ValueError` is the kind of exception that `int()` raises for text that is not a number.

            When no line fails, the `except` block is not needed. What does Python do with it then?

            ```predict
            try:
                count = int("3")
                print("you asked for", count)
            except ValueError:
                print("that is not a number")
            print("still running")
            ---
            `int("3")` works, so both lines of the `try` block run. Nothing was raised, so Python skips the `except` block and goes on to the last line.
            ```

            Press Next to step through a loop that tries two texts. Watch which line comes after line 3
            each time.

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

            ```quiz
            Which letters does this program print?

            ~~~python
            try:
                print("a")
                n = int("x")
                print("b")
            except ValueError:
                print("c")
            print("d")
            ~~~
            - [x] a, c, d :: Right. `a` is printed before anything goes wrong. `int("x")` raises, so `b` is skipped, the `except` block prints `c`, and the program carries on to `d`.
            - [ ] a, b, c, d :: After the line that raises, Python does not come back to the rest of the `try` block. `b` is never printed.
            - [ ] c, d :: The lines above the failing line have already run by the time it fails, so `a` is printed.
            - [ ] a, c :: Catching the exception means that the program carries on. The line after the `try` statement runs and prints `d`.
            ```

            **Watch out:** the `except` block is not a place that Python visits on every run. It runs only
            when a line in the `try` block raises, and then the rest of the `try` block is skipped for
            good.

            **In short:** Python runs the `try` block, and when a line in it raises an exception, Python
            jumps to the `except` block and carries on from there.
        ''',
        "title": "Where does it jump?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output on each line.
        ''',
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
            The loop runs twice. For `"7"`, `int` works, so the `try` block runs to its end and prints
            `number 7`, and the `except` block is skipped. For `"seven"`, `int` raises a `ValueError`.
            Python leaves the `try` block before its `print` and runs the `except` block, which prints
            `skip seven`. The exception was caught, so the loop ends in the normal way and the last line
            prints `done`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Go through the loop once for each item in the list. Each time, ask: can `int()` turn this text into a number?",
            "When `int()` works, the `try` block runs to its end and the `except` block is skipped. When `int()` fails, the rest of the `try` block is skipped and the `except` block runs.",
            "You should end up with three lines: one from the first time through the loop, one from the second time, and one from the line after the loop. A `print` with two values puts one space between them.",
        ],
    },
    {
        "id": "errors-s2",
        "lesson": r'''
            ## Finding the name that goes after except

            In the last step, `except ValueError:` caught a failed `int()`. How would you have known to
            write `ValueError` there, and not some other word? You do not have to guess. Python tells you
            the name every time a program stops with an error.

            Here is what Python shows when a program looks up a price that is not in a dict:

            ```text
            Traceback (most recent call last):
              File "solution.py", line 2, in <module>
                print(prices["large"])
                      ~~~~~~^^^^^^^^^
            KeyError: 'large'
            ```

            This report is called a **traceback**, because it traces the error back to the line where it
            happened. As in the Basics chapter, read the last line first. It has two parts, with a colon
            between them:

            - Before the colon stands the kind of exception, here `KeyError`. The kind is called the
              **exception type**.
            - After the colon stands the **message**, the details of this one failure. For a `KeyError`
              the message is the key that was not found.

            The type is the name to write after `except`, letter for letter:

            ```python
            prices = {"small": 1, "medium": 3}
            try:
                print(prices["large"])
            except KeyError:
                print("no price for that model")
            # no price for that model
            ```

            You have met several exception types in earlier chapters, each time as an error that stopped
            a program. Match each line with the type that it raises:

            ```match
            `int("abc")` :: `ValueError`
            `{"a": 1}["b"]` :: `KeyError`
            `[1, 2][5]` :: `IndexError`
            `"a" + 1` :: `TypeError`
            ---
            A `ValueError` means that the value cannot be used, such as text that is not a number. A `KeyError` is a key that is missing from a dict, and an `IndexError` is a position that does not exist in a list. A `TypeError` means that the value is the wrong kind of thing for the operation, such as text added to a number.
            ```

            ```quiz
            A program stops with this traceback. Which line catches the exception?

            ~~~text
            Traceback (most recent call last):
              File "solution.py", line 1, in <module>
                print("total: " + 5)
                      ~~~~~~~~~~^~~
            TypeError: can only concatenate str (not "int") to str
            ~~~
            - [x] `except TypeError:` :: Right. The type is the word before the colon on the last line.
            - [ ] `except can only concatenate str:` :: That is the message, the part after the colon. A message describes one failure. `except` needs the type.
            - [ ] `except Error:` :: Python has no exception type with the plain name `Error`. Write the full name from the traceback.
            - [ ] `except Traceback:` :: `Traceback` is the first word of the report, not the name of an exception. The type is on the last line.
            ```

            You do not need to know the names by heart. When you are not sure which type a line raises,
            make it fail on purpose: run the line on its own, without `try`, and read the traceback.

            ```try
            models = ["small", "large"]
            print(models[2])
            ---
            Run it and read the last line of the traceback. Then put the `print` line inside a `try` block, and add an `except` block for that type which prints `no such model`.
            ---
            models = ["small", "large"]
            try:
                print(models[2])
            except IndexError:
                print("no such model")
            ---
            The traceback ended in `IndexError: list index out of range`, so `IndexError` is the name after `except`.
            ```

            **Watch out:** the name must be exact, capital letters included. Python looks at the name
            after `except` only at the moment an exception arrives. So `except keyerror:` runs without
            complaint for as long as nothing fails. On the day something does, the program stops with
            `NameError: name 'keyerror' is not defined. Did you mean: 'KeyError'?`

            **In short:** the last line of a traceback starts with the exception type, and that type is
            the name to write after `except`.
        ''',
        "title": "Catch the right error",
        "difficulty": 0,
        "prompt": r'''
            Dividing by zero is not possible, so Python raises an exception when a program tries it. A
            helper function should survive that. Instead of stopping the program, it gives back `None`,
            the value for "no answer".

            **Your job:** finish `safe_divide(a, b)`. The function is already written except for one gap,
            marked `___`. The gap is the name of the exception type that a division by zero raises.

            **What goes in**
            - `a`: a number, for example `10`
            - `b`: the number to divide by, for example `4`. It may be `0`.

            **What comes out**
            - `a` divided by `b`: `2.5` for the example values
            - `None` when `b` is `0`

            **Rules**
            - The name in the gap must be written exactly as Python writes it. You are not expected to
              know it. Find it the way the lesson shows: make the error happen, and read the traceback.

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
            "The last line of a traceback starts with the exception type. Which line of code do you have to run to see the traceback for a division by zero?",
            "Make the error happen on purpose. On a new line below the function, at the left edge, print the result of dividing 1 by 0. Then press Run.",
            "Read the last line of the traceback. Copy the word that stands before the colon into the gap, with the same capital letters. Then delete the extra line that you added, and press Check.",
        ],
    },
    {
        "id": "errors-s3",
        "lesson": r'''
            ## When except does not catch

            You put a risky line inside `try`, you run the program, and it still stops with a traceback.
            It looks as if `try` did nothing. What went wrong?

            Start with a version that works. A chat history has two messages, and the program asks for a
            position that does not exist:

            ```python
            history = ["hi", "hello"]
            try:
                print(history[5])
            except IndexError:
                print("no message at that position")
            print("still running")
            # no message at that position
            # still running
            ```

            `history[5]` raises an `IndexError`, and the `except` line names `IndexError`. The two are the
            same, so the block runs.

            ```quiz
            Here is the same program with one word changed. What does it do?

            ~~~python
            history = ["hi", "hello"]
            try:
                print(history[5])
            except KeyError:
                print("no message at that position")
            print("still running")
            ~~~
            - [x] It stops with a traceback that ends in `IndexError: list index out of range` :: Right. The exception is an `IndexError`, and the block is only for a `KeyError`. Nothing catches the exception, so the program stops, exactly as it would without `try`.
            - [ ] It prints `no message at that position` and `still running` :: That needs an `except` block for the type that was raised. `history[5]` raises an `IndexError`, and this block names `KeyError`.
            - [ ] It skips the `except` block and prints `still running` :: The block is skipped, that part is true. But an exception that nobody catches does not go away. It stops the program before the last line runs.
            ```

            That is the rule. When a line in the `try` block raises, Python compares the type of the
            exception with the type that is written after `except`. When they are the same, the block
            runs. When they differ, the block is skipped, and the exception carries on as if the `try`
            were not there.

            It is a useful rule. An `except KeyError:` block is your plan for a missing key. It should
            not hide a different problem that you never planned for.

            The traceback also tells you how to repair a `try` statement that does not catch. Compare two
            names: the type on the last line of the traceback, and the type after `except`. Change the
            second one until they are the same.

            ```fill
            settings = {"model": "small"}
            try:
                print(settings["top_p"])
            except ___:
                print("top_p is not set")
            ---
            - [x] KeyError :: Right. A key that is missing from a dict raises a `KeyError`. This block catches it, and the program prints `top_p is not set`.
            - [ ] IndexError :: An `IndexError` is for a position that does not exist in a list. `settings` is a dict, so the exception is a `KeyError`, and this block lets it through.
            - [ ] ValueError :: A `ValueError` is what `int("abc")` raises. A missing key raises a `KeyError`, so the program stops with a traceback.
            ```

            **Watch out:** an `except` block with the wrong type gives no warning of its own. The program
            runs well for as long as nothing fails, and it stops on the first bad value. So try out every
            `try` statement once with a value that makes the line fail.

            **In short:** an `except` block catches only the type it names, so that name has to be the
            type on the last line of the traceback.
        ''',
        "title": "Fix: wrong exception type",
        "difficulty": 0,
        "prompt": r'''
            An API reports a count as text, for example `"12"`. `read_count(text)` should turn that text
            into a number, and give back `-1` when the text is not a number at all. Someone has written
            it with `try` and `except`, but it has a bug: for text such as `"lots"`, the program still
            stops with an error.

            **Your job:** find the one bug in `read_count(text)` and fix it. The code is already in the
            editor, and only one word needs to change.

            **What goes in**
            - `text`: a string, for example `"12"` or `"lots"`

            **What comes out**
            - the number in the text, as an `int`: `12` for `"12"`
            - `-1` when the text cannot be turned into a number

            **Rules**
            - Text that is not a number must not stop the program. The result for it is `-1`.

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
            "Press Check before you change anything. The failing check shows the exception that got through. Which type does it name?",
            "An `except` block catches only the type that it names. Compare the type in the failing check with the type that the code names after `except`.",
            "The two types are different, so the block never runs. On the `except` line, replace the type with the one that the failing check names. Leave the other lines as they are.",
        ],
    },
    {
        "id": "errors-s4",
        "lesson": r'''
            ## Refusing a value that makes no sense

            A function is about to send a request to a model with `temperature` set to `5`. The API
            accepts 0 to 2. If the function passes the 5 along, the mistake shows up later and somewhere
            else, as a rejected request that is hard to explain. It is better for the function to refuse
            at once, and to say why.

            Until now, Python raised the exceptions and you caught them. Your own code can raise one too:

            ```python
            def check_temperature(t):
                if t > 2:
                    raise ValueError("temperature must be at most 2")
                return t

            print(check_temperature(0.7))
            # 0.7
            ```

            The new line has three parts: the word `raise`, an exception type, and a message in
            parentheses. The message is yours to write. For `0.7` the `if` is false, so the `raise` line
            is skipped and the function returns as usual.

            For `check_temperature(5)` the `raise` line runs. The function stops at that line, in the
            same way as at a failing `int()`. The `return` below it never runs, and no value is handed
            back. The exception goes to the caller, the line that called the function. If nothing catches
            it there, it moves on to the caller of that line, and so on. Programmers say that the
            exception **propagates**. When nothing catches it anywhere, the program stops with a
            traceback, and the last line shows your message:

            ```text
            ValueError: temperature must be at most 2
            ```

            The caller can also catch it. What does this program print?

            ```predict
            def check_temperature(t):
                if t > 2:
                    raise ValueError("temperature must be at most 2")
                return t

            try:
                print(check_temperature(1))
                print(check_temperature(5))
                print(check_temperature(0))
            except ValueError:
                print("refused")
            ---
            The first call returns 1, and it is printed. The second call raises, so it returns nothing and nothing is printed for it. Python leaves the `try` block, which means that the third call never happens, and the `except` block prints `refused`.
            ```

            `ValueError` is the right type when the value is the right kind of thing but is not
            acceptable: a number that is too big, or a count below zero.

            ```quiz
            A function must refuse a negative count. Which line, placed under `if n < 0:`, does that?
            - [x] `raise ValueError("count must not be negative")` :: Right. `raise` stops the function and sends the exception to the caller.
            - [ ] `return ValueError("count must not be negative")` :: This hands the exception back as an ordinary value. Nothing stops, and the caller carries on with a result that it cannot use.
            - [ ] `print("count must not be negative")` :: This shows some text and goes on. The function then returns as if the value were fine.
            - [ ] `ValueError("count must not be negative")` :: Without the word `raise`, this line creates an exception and throws it away. No error appears.
            ```

            **Watch out:** do not return a text such as `"error: too high"` in place of raising. To the
            caller, that text looks like a normal result, and the mistake travels on unnoticed. An
            exception cannot be overlooked: either somebody catches it, or the program stops.

            **In short:** `raise ValueError("message")` stops the function at that line and sends the
            exception to the caller.
        ''',
        "title": "Raise on bad input",
        "difficulty": 0,
        "prompt": r'''
            Before your app calls a model, it checks the setting `max_tokens`, the largest number of
            tokens that the model may write. A value below 1 makes no sense. It can only come from a
            mistake in the code that called the function, so the function refuses it with an exception.

            **Your job:** write `check_max_tokens(n)`. It gives back `n` when the value is acceptable, and
            it raises a `ValueError` when the value is not.

            **What goes in**
            - `n`: a whole number, for example `256`

            **What comes out**
            - `n` itself, unchanged, when `n` is 1 or more

            **Rules**
            - When `n` is less than `1`, for example `0` or `-5`, the function raises a `ValueError`. It
              does not return anything in that case.
            - The message of the exception is yours to choose.
            - `1` is acceptable.

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
            "Look at `check_temperature` in the lesson. Which word makes a function stop with an exception?",
            "Test for the bad case first, with an `if`. Under the `if`, raise the exception with a message. A value that gets past the test is handed back below it.",
            "The first line of the body is an `if` that is true when `n` is less than 1. Indented under it: the word `raise`, then the type `ValueError` with a message of your own in parentheses. After that, back at the indentation of the `if`, hand back `n`.",
        ],
    },
    {
        "id": "errors-s5",
        "lesson": r'''
            ## A spare value for when the real one is missing

            A model config comes from a file that people edit by hand, so now and then a setting is not
            there. Your app should not stop for that. It should carry on with a sensible spare value.

            So far, your `except` blocks printed a message. Inside a function they can do something more
            useful, and hand back a value. Here the `try` block returns the real value, and the `except`
            block returns the spare one:

            ```python
            def first_tool(tools):
                try:
                    return tools[0]
                except IndexError:
                    return "no tools"

            print(first_tool(["search", "email"]))
            # search
            print(first_tool([]))
            # no tools
            ```

            In the first call, `tools[0]` works and the function returns it. The `except` block is never
            reached. In the second call the list is empty, so `tools[0]` raises an `IndexError`. The
            `return` in the `try` block does not happen, and the `return` in the `except` block runs in
            its place. Either way, the caller gets exactly one value and never sees an error.

            A value that stands in for a missing one is called a **fallback value**.

            The same shape works for a dict. Only the type changes, because a missing key is not the same
            exception as a missing list position:

            ```fill
            def get_limit(settings):
                try:
                    return settings["max_tokens"]
                except ___:
                    return 256

            print(get_limit({"max_tokens": 100}))
            print(get_limit({"temperature": 0.2}))
            ---
            - [x] KeyError :: Right. The second dict has no `"max_tokens"` key, so the lookup raises a `KeyError` and the function returns the fallback. The program prints `100` and `256`.
            - [ ] IndexError :: That is the type for a list position that does not exist. A dict raises a `KeyError`, and this block lets it through, so the second call stops the program.
            - [ ] ValueError :: A missing key is a `KeyError`. This block does not catch it, so the second call stops the program.
            ```

            ```quiz
            With the right type in the gap, what does `get_limit({"max_tokens": 0})` return?
            - [x] `0` :: Right. The key is there, so the lookup works and nothing is raised. The fallback is only for a key that is missing.
            - [ ] `256` :: The fallback is used only when the lookup raises an exception. A key that holds `0` is still a key that exists.
            - [ ] `None` :: Both ways through the function end in a `return` with a value: the stored one, or the fallback.
            ```

            In the Dicts chapter you used `settings.get("max_tokens", 256)` for this, and for a dict that
            is still a good choice. `try` with `except` is the general tool. It works for any line that
            can fail, not only for a lookup. This step practises it on a dict.

            **Watch out:** the fallback is only reached when the `except` line names the right type. For
            a dict that is `KeyError`. With `IndexError` there, a missing key still stops the program
            with `KeyError: 'max_tokens'`.

            **In short:** return the real value in the `try` block, and the fallback value in the
            `except` block.
        ''',
        "title": "Missing config key",
        "difficulty": 0,
        "prompt": r'''
            A model config says which model to use, most of the time. When that setting is missing, your
            app should fall back to a small default model and carry on.

            **Your job:** write `get_model(config)`. It gives back the model name that is stored in the
            config, or the fallback `"gpt-4o-mini"` when the config has no model name.

            **What goes in**
            - `config`: a dict of settings, for example `{"model": "claude", "temperature": 0.2}`. The
              key `"model"` may be missing, and the dict may be empty.

            **What comes out**
            - the string stored under the key `"model"`: `"claude"` for the example value
            - the string `"gpt-4o-mini"` when there is no `"model"` key

            **Rules**
            - Other keys in the dict make no difference.
            - Read the key with square brackets, and handle the missing key with `try` and `except`. A
              check looks for a `try` statement in your code, so `.get()` is not accepted in this step.

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
            "The lesson has a function of the same shape for a list, `first_tool`. Which line of your function can fail, and which exception type does it raise then?",
            "Put the lookup with square brackets in a `try` block, and hand its result back from there. The `except` block names the type that a missing dict key raises, and it hands back the fallback.",
            "Four lines go under the `def` line. First `try:`. Then, indented, the lookup of the key `\"model\"`, handed back. Then an `except` line with the type for a missing key. Then, indented, the fallback string, handed back.",
        ],
    },
    {
        "id": "errors-s6",
        "lesson": r'''
            ## Getting the message out of an exception

            A user types something your app cannot use, and the app answers "error". Which error? The
            user cannot tell, and neither can you when you read the log a week later.

            Python had already written a precise sentence about the problem. You have seen it after the
            colon on the last line of a traceback. When you catch an exception, no traceback is printed,
            but the message is not lost. It travels inside the exception, and you can ask for it.

            ```python
            try:
                print(10 / 0)
            except ZeroDivisionError as e:
                print("caught:", e)
            # caught: division by zero
            ```

            The two new words are `as e`. They give the caught exception a name, here `e`. Inside the
            `except` block, `e` is the exception itself, and printing it shows its message.

            To do more than print, turn the exception into a string with `str()`. Then you can store the
            message, join it to other text, or return it:

            ```python
            def reply(text):
                try:
                    number = float(text)
                except ValueError as err:
                    return "Sorry: " + str(err)
                return f"Half of that is {number / 2}"

            print(reply("9"))
            # Half of that is 4.5
            print(reply("nine"))
            # Sorry: could not convert string to float: 'nine'
            ```

            The name after `as` is your choice. This example uses `err`. Most programmers write `e`.

            ```predict
            settings = {"model": "small"}
            try:
                print(settings["top_p"])
            except KeyError as e:
                print("missing:", e)
            ---
            The message of a `KeyError` is the key that was not found, shown with its quotes. It is the same text that stands after the colon in the traceback, `KeyError: 'top_p'`.
            ```

            ```quiz
            `int("3.5")` raises an exception, and the program catches it with `as e`. What is `str(e)`?
            - [x] `invalid literal for int() with base 10: '3.5'` :: Right. `str(e)` is the message, which is everything after the colon on the last line of the traceback.
            - [ ] `ValueError: invalid literal for int() with base 10: '3.5'` :: That is the whole last line of the traceback. The type name and the colon are not part of the message.
            - [ ] `ValueError` :: That is the type of the exception. The message is the sentence that comes with it.
            - [ ] `3.5` :: The message mentions the text that could not be converted, but it is a whole sentence.
            ```

            **Watch out:** the name `e` exists only inside the `except` block. When the block ends,
            Python removes the name, and a later line that uses `e` stops with
            `NameError: name 'e' is not defined`. Take whatever you need from the exception while you are
            inside the block.

            **In short:** `except SomeType as e:` gives the caught exception a name, and `str(e)` is its
            message.
        ''',
        "title": "Read the error message",
        "difficulty": 0,
        "prompt": r'''
            When a user types something that is not a number, the answer "error" is not much help.
            Python's own message says exactly what was wrong with the text. `check_number(text)` should
            pass that message on.

            **Your job:** change `check_number(text)` so that, for text that is not a number, it gives
            back the message of the exception. The code in the editor already catches the exception, but
            it gives back the fixed text `"error"` every time.

            **What goes in**
            - `text`: a string, for example `"12"` or `"ten"`

            **What comes out**
            - the string `"ok"` when `int(text)` works
            - otherwise the message of the exception that `int(text)` raised, as a string

            **Rules**
            - The message is exactly the text that Python wrote, with nothing added in front of it or
              after it.
            - The empty string `""` is not a number either. It gets the message that Python writes for it.

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
            "The message is inside the exception. What do you add to an `except` line to give the caught exception a name?",
            "Give the exception a name on the `except` line. Inside the block, turn the exception into a string, and hand that string back in place of the fixed text.",
            "Two lines change. On the `except` line, add the word `as` and a name after the type. On the line under it, replace `\"error\"` with a call of `str()` on that name.",
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
            ## Recover from two expected conversion failures

            A settings form supplies a number as text, but sometimes it supplies text that is not numeric, or no value at all. Those are different problems for Python even if your application wants the same fallback for both.

            ```python
            def as_decimal(value):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            print(as_decimal("2.5"))
            # 2.5
            print(as_decimal("missing"))
            # None
            print(as_decimal([]))
            # None
            ```

            A numeric-looking string converts successfully. An unsuitable string raises `ValueError`; an unsupported kind of input raises `TypeError`. Parentheses on the except line group both exception types into a tuple. Either type can select the same recovery block.

            ```match
            `ValueError` during conversion :: input kind is accepted but its contents are unsuitable
            `TypeError` during conversion :: input kind is not supported
            an unrelated `NameError` :: a programming mistake that should remain visible
            ```

            Keep the protected code small and name only failures you intend to handle. Catching every exception can also catch a misspelled variable. The application then returns a plausible fallback instead of showing the mistake, making the bug harder to find.

            ```quiz
            A conversion handler catches ValueError and TypeError. What should a misspelled variable do?
            - [x] Raise NameError to the caller. :: That error is outside the intended recovery policy and should remain visible.
            - [ ] Return the conversion fallback. :: Hiding a programming mistake would make bad code appear successful.
            ```

            **Watch out:** a bare `except` or `except Exception` is broader than these two conversion errors. A program that never crashes can still be silently producing wrong results.

            Recover from the failures you expect, while leaving other failures visible.
        ''',
        "title": "Safe token count",
        "hints": [
            "Review which exceptions a conversion can raise for bad text and unsupported types.",
            "Protect only the conversion and handle the two named error types together.",
            "Return a successful conversion normally; for either specified failure, give back the fallback while letting unrelated errors escape.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Usage data from an API sometimes arrives as strings, and sometimes is junk.
            Turn it into a token count without crashing.

            **Your job:** write `parse_tokens(value)`

            **What goes in**
            - `value`: anything, usually a string like `"42"` or an int like `7`, but it
              can be junk like `"n/a"` or `None`

            **What comes out**
            - `int(value)` as an int, or `0` when the conversion fails

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
            ## Reject unsuitable values before using them

            A caller asks for a negative number of search results. Waiting until a later operation fails would hide what was wrong with the request. Check the input at the boundary and name the value the caller needs to fix.

            ```python
            def check_count(count):
                if not isinstance(count, int) or isinstance(count, bool):
                    raise TypeError("count must be an integer")
                if count < 0:
                    raise ValueError("count must not be negative")

            check_count(3)
            print("accepted")
            # accepted
            ```

            Checking whether a value is acceptable is **validation**. First establish its type, then compare its value with the allowed range. `TypeError` describes the wrong kind of input; `ValueError` describes unacceptable contents of an otherwise suitable type. Checking in this order avoids accidentally comparing text with a number.

            ```predict
            print(isinstance(True, int))
            print(isinstance(3.5, (int, float)))
            ---
            Both print True. Booleans count as integers in Python, while the tuple accepts either listed numeric type.
            ```

            Python treats booleans as a kind of integer. If a setting means a quantity rather than yes or no, reject booleans explicitly. Otherwise `True` could quietly pass as one. When several inputs are wrong, the first raised exception stops the function; later checks never run.

            ```quiz
            Why should a validation error mention the parameter name?
            - [x] The caller can identify which supplied value to change. :: A specific message makes the failure actionable.
            - [ ] Python requires parameter names in every exception message. :: Python allows arbitrary messages; clarity is your responsibility.
            ```

            **Watch out:** converting every input before checking changes the contract. Text containing digits may still be forbidden when the caller must provide an actual integer.

            Validate types before ranges and make the first failure explain the offending input.
        ''',
        "title": "Validate generation params",
        "hints": [
            "Separate each parameter's type check from its range check.",
            "Check the first parameter completely before the second, explicitly excluding booleans from numeric inputs.",
            "For each rule in the given order, raise the required error type with that parameter's name; otherwise let the function finish normally.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Check generation parameters before sending them to a model API, and fail
            early with a clear error.

            **Your job:** write `validate_params(max_tokens, temperature)`

            **What goes in**
            - `max_tokens`: should be an int, e.g. `256`
            - `temperature`: should be an int or a float, e.g. `0.7`

            **What comes out**
            - `None` when both are valid (just let the function end)

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
            ## Give an application problem its own error name

            Your app can fail because a document is too large or because a numeric conversion went wrong. Both failures deserve attention, but a caller may want to recover from only the document problem. Give that problem a distinct type.

            ```python
            class DocumentTooLargeError(Exception):
                pass

            try:
                raise DocumentTooLargeError("document exceeds size limit")
            except DocumentTooLargeError as problem:
                print(problem)
            # document exceeds size limit
            ```

            The `class` statement creates a new type. Here the parentheses say the new type is a kind of `Exception`, which lets Python raise and catch it. The body contains `pass`, a statement that does nothing; Python requires a body even when you have no extra behavior to add. This small form is enough for a **custom exception**. The classes chapter will explain other uses of classes later.

            ```order
            class MissingDocumentError(Exception):
                pass
            problem = MissingDocumentError("document unavailable")
            print(str(problem))
            ---
            Define the type before creating an error of that type. Converting the error to text reads its message.
            ```

            Choose the type to identify the kind of problem and the message to explain the particular failure. Callers can catch the named type without accidentally swallowing a `ValueError` from unrelated code. Creating an exception object alone does not stop execution; raising it starts the error-handling process.

            ```quiz
            What makes a new exception type usable with raise and except?
            - [x] Defining it as a kind of Exception. :: The parent type supplies the exception behavior.
            - [ ] Naming any variable with the word Error. :: A name alone does not create an exception type.
            ```

            **Watch out:** raising an exception name before defining it causes `NameError`, hiding the application problem you meant to report.

            Use a distinct exception type when callers need to distinguish a particular failure.
        ''',
        "title": "Your own exception",
        "difficulty": 1,
        "prompt": r'''
            An agent has a spending budget for API calls. When a call would cost more
            than what's left, stop with an error type of your own (a *custom exception*).

            **Your job:** write a class `BudgetExceededError`, then `spend(budget, cost)`

            **What goes in**
            - `BudgetExceededError`: a one-line custom exception based on `Exception`
              (`class Name(Exception): pass`)
            - `budget`: a number, the dollars left, e.g. `1.0`
            - `cost`: a number, the price of the next call, e.g. `0.25`

            **What comes out**
            - the budget left after paying, `budget - cost`

            **Rules**
            - If `cost` is greater than `budget`, raise a `BudgetExceededError` with the exact message `"budget exceeded"`.
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
            "A distinct error type lets callers recognize budget failures.",
            "Define the custom exception before using it, and distinguish an excessive cost from an exact-budget cost.",
            "Raise your named error only when spending would exceed the budget; otherwise give back the remaining amount.",
        ],
    },
    {
        "id": "errors-8",
        "lesson": r'''
            ## Finish the cleanup even when work fails

            A task announces that it has opened a resource. Whether the work succeeds or raises an error, you still need the closing action to happen. Placing that action after an ordinary return would skip it entirely.

            ```python
            def calculate(divisor):
                try:
                    return 12 / divisor
                finally:
                    print("finished")

            print(calculate(3))
            # finished
            # 4.0
            ```

            The `finally` block runs as the protected work finishes, before a pending return leaves the function. Work that must happen on both success and failure is called **cleanup**. The same block also runs when an exception is on its way to the caller.

            ```predict
            try:
                try:
                    raise ValueError("bad value")
                finally:
                    print("cleanup")
            except ValueError:
                print("handled")
            ---
            Cleanup prints first. Finally does not catch the failure, so the outer handler then prints handled.
            ```

            An `except` block decides whether to recover from an error. A `finally` block guarantees an action during ordinary Python control flow without deciding whether the error should be recovered from. You can use `try` with only `finally` when your helper must preserve the original failure.

            ```quiz
            A protected operation raises an error and finally only prints. What happens next?
            - [x] The same error continues to the caller. :: Cleanup does not automatically handle the exception.
            - [ ] The function succeeds because finally ran. :: Running cleanup says nothing about whether the operation succeeded.
            ```

            Keep cleanup small and avoid adding a new return there. A return in `finally` can replace the original return value or suppress the pending exception, changing what the caller observes.

            **Watch out:** putting cleanup after the try statement instead of in finally leaves it skipped when an error escapes.

            Cleanup should run without hiding the result or failure of the original work.
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

            **Your job:** write `logged_call(func, log)`

            **What goes in**
            - `func`: a function with no arguments; you call it as `func()`
            - `log`: a list of strings you append to, e.g. `[]`

            **What comes out**
            - whatever `func()` returned

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
            "Cleanup belongs in the block that runs even during a return or exception.",
            "Keep the start event before the call and the end event in guaranteed cleanup.",
            "Append the opening event, call the function inside try while preserving its result, and append the closing event in finally without catching errors.",
        ],
    },
    {
        "id": "errors-3",
        "title": "API error hierarchy",
        "hints": [
            "A handler for a parent exception also catches its more specific child types.",
            "Choose the error type from the status, then handle specific types before the shared parent.",
            "Define the hierarchy, implement the status-to-error rules, and have the describing helper call that checker and turn each outcome into its required label.",
        ],
        "difficulty": 2,
        "prompt": r'''
            An LLM client turns HTTP status codes into specific exceptions, so callers can
            handle "bad API key" differently from "slow down". Sub-types of one base error
            form an *exception hierarchy*.

            **Your job:** write three exception classes, then `raise_for_status` (parameters `status`, then `body`) and
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
            - Call `raise_for_status` with the supplied status and body; don't let its error escape.
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
            "Recall when except, else, and finally run.",
            "Keep the risky step alone in try so a later logging failure is not mistaken for a step failure.",
            "Handle the specified missing-key error, log success only in else, and place the final event in finally so other errors still reach the caller.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A pipeline runs one step at a time and keeps a log of what happened. Some
            failures are expected and handled; others must reach the caller, but the log
            must always be closed.

            **Your job:** write `run_step(step, log)`

            **What goes in**
            - `step`: a function that takes no arguments, e.g. `works` below. You call it
              as `step()`.
            - `log`: a list of strings you append to, e.g. `[]`

            **What comes out**
            - whatever `step()` returned, or `None` when it raised `KeyError`

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
            "Count attempts as total calls, and distinguish temporary failures from other errors.",
            "After a temporary failure, wait only if another attempt remains; preserve the final original exception.",
            "Validate the attempt count first, return on success, re-raise at the last allowed failure, and double the optional wait between earlier retries.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Network calls to a model API fail now and then. Retry the temporary failures,
            waiting longer each time (this is called *exponential backoff*).

            **Your job:** write `call_with_retry(func, attempts=3, sleep=None)`

            **What goes in**
            - `func`: a function with no arguments; you call it as `func()`
            - `attempts`: an int, the maximum number of calls **in total** (default `3`)
            - `sleep`: a function taking a number of seconds, e.g. `time.sleep`, or `None`
              (default) meaning "don't wait". Tests pass a function that records the values.

            **What comes out**
            - the result of the first `func()` call that succeeds

            **Rules**
            - If `attempts` is less than `1`, raise `ValueError` **before** calling `func`.
            - A call that succeeds is returned straight away (no sleep, no more calls).
            - If `func()` raises `TimeoutError` or `ConnectionError`, try again, up to
              `attempts` calls in total.
            - Between two attempts, if `sleep` is not `None`, call the supplied sleep function with
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
            "Separate malformed calls from bad numeric arguments, preserving the cause of the latter.",
            "Convert add arguments into a new list and catch only the specified conversion error.",
            "Define the custom error, validate and parse each call, chain numeric conversion failures, and have the batch helper turn only your custom errors into output lines.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A model asks your app to call tools. Each tool call arrives as a dict like
            `{"name": "search", "args": ["cats", "dogs"]}`. Parse them, and report bad
            ones with your own exception type.

            **Your job:** write a class `ToolCallError`, then `parse_tool_call(call)` and `run_all(calls)`

            **What goes in**
            - `ToolCallError`: a one-line custom exception class based on `Exception`
            - `call`: a dict with a `"name"` string and an optional `"args"` list
            - `calls`: a list of such dicts
            - **`parse_tool_call` returns:** a tuple `(name, args)`, e.g. `("now", [])`
            - **`run_all` returns:** a list of strings, one per call, in the same order

            **Rules for `parse_tool_call`**
            - If `"name"` is missing or is the empty string `""`, raise a `ToolCallError` with the exact message `"malformed tool call"`.
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
