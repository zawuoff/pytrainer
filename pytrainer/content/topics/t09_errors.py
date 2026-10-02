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

LESSON = r'''
## Chapter notes: Error Handling

**Exception** = Python's way of saying "I can't do this". It has a **type** and a
**message**; the last line of a traceback shows both:
`ValueError: invalid literal for int() with base 10: 'abc'`.

| Code | Raises |
| --- | --- |
| `int("abc")` | `ValueError` |
| `int(None)`, `"a" + 1` | `TypeError` |
| `{"a": 1}["b"]` | `KeyError` |
| `[1, 2][5]` | `IndexError` |
| `1 / 0` | `ZeroDivisionError` |

**Catching**
```python
try:
    n = int("abc")            # only the risky line
except (ValueError, TypeError) as e:
    print("bad value:", e)    # str(e) is the message
else:
    print("no error:", n)     # runs only if try raised nothing
finally:
    print("always runs")      # cleanup, even when an error escapes
```

- `except X` catches `X` **and its sub-types**; the first matching `except` wins,
  so list specific types before general ones.
- An exception you don't catch keeps going up to the caller (it *propagates*).

**Raising**
- `raise ValueError("max_tokens must be at least 1")` - stop and report bad input.
- `TypeError` = wrong kind of value, `ValueError` = right kind, bad value.
- Bare `raise` inside `except` re-raises the same exception object.
- `raise NewError("...") from e` chains: the new error's `__cause__` is `e`.

**Custom exceptions** (one-line classes)
```python
class APIError(Exception):
    pass

class RateLimitError(APIError):   # a sub-type: except APIError catches it too
    pass
```

**Gotchas**
- Bare `except:` / `except Exception` hide real bugs - name the types you expect.
- Keep `try` blocks small, so you only catch errors from the line you meant.
- Raise, don't `return "error..."`: callers can't tell an error string from data.
- `True`/`False` pass `isinstance(x, int)` - reject bools explicitly when validating.
- Retry only *temporary* errors (`TimeoutError`, `ConnectionError`), with a limit
  and growing waits (exponential backoff: 1, 2, 4...).
'''

EXERCISES = [
    {
        "id": "errors-s1",
        "lesson": r'''
            Think of `try` as a trapeze act with a **safety net**. You try the risky move. If
            you fall, the net (`except`) catches you and the show goes on. Without a net, one
            fall ends the whole show - that is your program crashing.

            ```python
            for text in ["3", "three"]:
                try:
                    print("converted:", int(text))
                except ValueError:
                    print("could not convert", text)
            print("still running")
            ```

            When a line inside `try` fails, Python **jumps straight** to the `except` block. The
            rest of the `try` block is skipped. After the `except` block, the program carries
            on as normal.

            The proper name for "something went wrong" is an **exception**. We say a line
            *raises* an exception, and `except` *catches* (or *handles*) it. An exception
            nobody catches stops the program and prints a *traceback*.

            Watch out: lines in `try` **after** the failing line never run.
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
            Every exception has a **name tag**, like a warning light on a car dashboard: "oil",
            "battery", "brakes". Each light means a different problem. Python's warning lights
            are exception *types*.

            You find the name on the **last line** of the traceback, before the colon:

            ```python
            try:
                print(10 / 2)
                print(int("abc"))
            except ValueError as e:
                print("type: ValueError | message:", e)
            ```

            If you ran `int("abc")` without the `try`, the last line of the error would read
            `ValueError: invalid literal for int() with base 10: 'abc'`. The part before the
            colon is the **exception type**; the part after is the **message**.

            Common types you will meet:
            - `ValueError` - right kind of value, but unusable (`int("abc")`)
            - `TypeError` - wrong kind of value (`int(None)`)
            - `KeyError` - dict key not found
            - `ZeroDivisionError` - dividing by zero

            After `except` you write the **type name** you want to catch. To discover a type,
            make the error happen on purpose and read the last line.
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
            `except` is like a **bouncer checking names on a list**. He only stops the people
            whose name is on his list. Anyone else walks straight past him - into your program,
            which crashes.

            ```python
            try:
                print(int("oops"))
            except KeyError:
                print("never printed")
            ```

            Run it: the program still crashes with `ValueError`, because the `except` only
            names `KeyError`. The names don't match, so the "net" isn't there.

            So an `except TypeName:` block catches **only that type** (and its sub-types, which
            you'll meet later). Everything else keeps going up - we say it **propagates**.

            Watch out: when a `try`/`except` "doesn't work", the first thing to check is
            whether the type in `except` matches the type in the traceback.
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
            So far Python raised errors for you. You can raise them **yourself**. It's like a
            machine with an emergency **stop button**: when the input is dangerous, you press
            it instead of carrying on and producing garbage.

            ```python
            def set_volume(level):
                if level > 10:
                    raise ValueError(f"volume must be at most 10, got {level}")
                return level

            print(set_volume(7))
            try:
                set_volume(99)
            except ValueError as e:
                print("error:", e)
            ```

            The keyword is **`raise`**, followed by an exception type called like a function
            with a message: `raise ValueError("...")`. The function stops right there - no
            `return` runs after it. The caller can catch it with `try`/`except`, or let it
            crash the program.

            Pick the type that fits: `ValueError` when a value is the right kind but not
            acceptable (a negative count), `TypeError` when it's the wrong kind (a string
            where a number belongs).

            Watch out: don't `return "error: ..."`. A string looks like normal data; an
            exception can't be missed.
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
            A dict is a coat check: you give a ticket (the key), you get a coat (the value).
            Hand over a ticket that doesn't exist and the attendant doesn't shrug - he raises
            the alarm. With square brackets, that alarm is a **`KeyError`**.

            ```python
            settings = {"temperature": 0.2}
            try:
                print(settings["max_tokens"])
            except KeyError as e:
                print("missing key:", e)
            print("carry on")
            ```

            Remember the safety net? You can put a dict lookup inside `try` and catch the
            `KeyError` to use a **fallback value** instead.

            You already know `.get(key, default)` does something similar. Both are fine
            Python; the `try` version is called "**EAFP**" - *easier to ask forgiveness than
            permission*: just try it, and handle the failure if it happens.

            Watch out: a `KeyError` is not a `ValueError` - the bouncer only stops the name
            on his list.
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
            "try: return config[\"model\"]  -  then except KeyError: return \"gpt-4o-mini\".",
        ],
    },
    {
        "id": "errors-s6",
        "lesson": r'''
            When the safety net catches you, you can also **read the incident report**: what
            exactly went wrong. Add `as e` to the `except` line and `e` holds the exception
            object.

            ```python
            try:
                int("ten")
            except ValueError as e:
                print("caught it!")
                print(str(e))
            ```

            `str(e)` turns the exception into its **message** - the same text you see after
            the colon in a traceback. Here that is `invalid literal for int() with base 10: 'ten'`.

            The name `e` is just a variable name (people also use `err` or `exc`). It only
            exists inside the `except` block.

            This matters in AI apps: when an API call fails, you want to log *why* it failed,
            or show the message to the user, not just "something broke".

            Watch out: `print(e)` and `str(e)` show the message only, not the type name.
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
            One net can catch **several kinds of falls**. Put the exception types in brackets,
            separated by commas - a *tuple* of types.

            ```python
            def to_number(value):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None

            print(to_number("1.5"), to_number("abc"), to_number([1]))
            ```

            Here `float("abc")` raises `ValueError` and `float([1])` raises `TypeError`; the
            single `except` handles both the same way.

            Why not catch *everything* with a bare `except:` or `except Exception:`? Because
            that net also catches your own bugs - a typo in a variable name (`NameError`)
            would silently turn into "return None" and you'd never find it.

            The rule of thumb: **catch the specific exceptions you expect**, and let the rest
            crash loudly so you can fix them.
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

            - `value`: anything - usually a string like `"42"` or an int like `7`, but it
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
            Validating input is like a **bouncer at the door with a checklist**: check each
            rule in order, and turn someone away at the *first* failed rule, saying why.

            ```python
            def check_age(age):
                if not isinstance(age, int) or isinstance(age, bool):
                    raise TypeError("age must be an int")
                if age < 0:
                    raise ValueError("age must not be negative")

            check_age(30)
            try:
                check_age("30")
            except TypeError as e:
                print(e)
            ```

            `isinstance(value, int)` asks "is this an int?". You can pass a tuple of types:
            `isinstance(x, (int, float))` means "int or float".

            Two kinds of "no":
            - **`TypeError`**: wrong *kind* of thing (a string where a number belongs).
            - **`ValueError`**: right kind, bad *value* (a number out of range).

            Put the parameter's name in the message: `"max_tokens must be an int"` tells the
            caller exactly what to fix. This is called *failing fast*: stop at the door, before
            the bad value causes a confusing error deep inside your program.

            Watch out: `isinstance(True, int)` is `True` - Python treats bools as ints. Reject
            them with an extra `isinstance(x, bool)` check.
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
            Built-in exception names are generic. Your app can have **its own warning lights**
            with names that mean something in *your* world: `RateLimitError`,
            `BudgetExceededError`.

            Making one takes two lines - a *class* that is based on `Exception`:

            ```python
            class TooLongError(Exception):
                pass

            def check_prompt(text):
                if len(text) > 10:
                    raise TooLongError("prompt too long")
                return text

            try:
                check_prompt("a very long prompt")
            except TooLongError as e:
                print("caught:", e)
            ```

            We haven't studied classes yet, and you don't need to: treat
            `class Name(Exception): pass` as a recipe. `pass` means "nothing else to add".
            The new type behaves like any other exception: you `raise` it with a message and
            catch it by name.

            The proper name is a **custom exception**. Callers can now write
            `except TooLongError:` and be sure they only catch *that* problem.
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
            "First create the exception type with the two-line class recipe, then use raise inside spend.",
            "Define the class above the function. In spend, check whether cost is bigger than budget before doing the subtraction.",
            "Write class BudgetExceededError(Exception): with pass inside. In spend: if cost > budget, raise BudgetExceededError with the message \"budget exceeded\"; otherwise return budget minus cost.",
        ],
    },
    {
        "id": "errors-8",
        "lesson": r'''
            Imagine borrowing a library book. Whatever happens while you read - you finish
            it, you fall asleep, the fire alarm goes off - **you always return the book**.
            That's `finally`: code that runs no matter how the `try` block ends.

            ```python
            def risky(n):
                print("open")
                try:
                    return 10 / n
                finally:
                    print("close")

            print(risky(2))
            try:
                risky(0)
            except ZeroDivisionError:
                print("error reached the caller")
            ```

            `finally` runs when the `try` block finishes normally, when it `return`s, **and**
            when an exception flies out of it. It doesn't stop the exception: after `finally`
            runs, the error keeps going to the caller.

            You can use `try` + `finally` with no `except` at all. That's the pattern for
            **cleanup**: closing a file, stopping a timer, writing "done" to a log.

            Watch out: don't `return` from inside `finally` - it would swallow the error.
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
            "raise_for_status picks which exception to raise based on the status code. describe_failure calls it inside try and has one except block per type - the specific ones (AuthError, RateLimitError) must come before APIError.",
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
              `"ok"` is **not** caught - it propagates to the caller.
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
            - If every attempt fails, re-raise the **last** exception - the very same
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
