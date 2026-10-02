TOPIC = {
    "id": "env",
    "title": "Environment & Env Variables",
    "track": "working-python",
    "order": 5,
    "requires": ["functions", "errors"],
    "summary": """
        Reading configuration and secrets from environment variables: defaults, required
        values, type conversion, .env files, precedence and keeping API keys out of logs.
    """,
    "concepts": ["os.environ", "os.getenv", "defaults", "required config", "type conversion",
                 ".env files", "precedence", "secret masking", "exit codes"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["environment", "env", "variable", "os.environ", "getenv", "config", "setting",
                 "default", "api key", "secret", "dotenv", ".env", "keyerror", "runtimeerror", "export"],
    "cards": [
        {
            "syntax": 'os.environ["NAME"]',
            "explain": "Reads or sets one environment variable. Reading a name that is not set raises KeyError.",
            "example": r'''
                import os

                os.environ["APP_MODE"] = "demo"
                print(os.environ["APP_MODE"])
                # demo
                print("APP_MODE" in os.environ)
                # True
            ''',
        },
        {
            "syntax": "os.environ.get(name, default)",
            "explain": "Returns the variable's value, or default when the name is not set. os.getenv does the same.",
            "example": r'''
                import os

                os.environ.pop("PT_THEME", None)
                print(os.environ.get("PT_THEME", "light"))
                # light
                print(os.getenv("PT_THEME"))
                # None
            ''',
        },
        {
            "syntax": 'int(os.environ.get(name, "256"))',
            "explain": "Every value is a string. Write the default as a string too, then convert with int() or float().",
            "example": r'''
                import os

                os.environ["MAX_TOKENS"] = "512"
                raw = os.environ.get("MAX_TOKENS", "256")
                print(raw + "0")
                # 5120
                print(int(raw) + 1)
                # 513
            ''',
        },
        {
            "syntax": 'os.environ.get(name, "").lower() == "true"',
            "explain": 'Reads an on/off setting. Do not use bool(): bool("false") is True, as for any non-empty string.',
            "example": r'''
                import os

                os.environ["DEBUG"] = "False"
                print(bool(os.environ["DEBUG"]))
                # True
                print(os.environ.get("DEBUG", "").lower() == "true")
                # False
            ''',
        },
        {
            "syntax": 'if not os.environ.get(name, "").strip(): raise ...',
            "explain": "Stops early when a required variable is not set, empty or only spaces. Name the variable in the message.",
            "example": r'''
                import os
                os.environ["PT_KEY"] = "   "
                try:
                    if not os.environ.get("PT_KEY", "").strip():
                        raise RuntimeError("Missing variable: PT_KEY")
                except RuntimeError as exc:
                    print(exc)
                # Missing variable: PT_KEY
            ''',
        },
        {
            "syntax": 'key, value = line.split("=", 1)',
            "explain": "Splits one KEY=value line of a .env file at the first = only, so the value may contain = signs.",
            "example": r'''
                line = "URL=http://x/?a=b"
                key, value = line.split("=", 1)
                print(key)
                # URL
                print(value)
                # http://x/?a=b
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Environment & Env Variables

An **environment variable** is a named string that the operating system keeps for a
running program. The full set of them is the program's **environment**. A program gets a
copy of the environment of the program that started it. That is usually your **terminal**:
the window where you type commands.

An **API key** is a secret string that identifies you to an online service. API keys and
settings such as the model name go in environment variables, not in your code. Code gets
shared with other people, and a key written in the code is shared with it.

### Setting variables in the terminal

The **shell** is the program that reads the commands you type in a terminal (bash or zsh).
In the shell, `$NAME` inserts the value of a variable, and `echo` prints its arguments.

```bash
export LLM_MODEL=gpt-4o           # no spaces around =; lasts for this terminal session
echo $LLM_MODEL                   # gpt-4o ($LLM_MODEL becomes the value, echo prints it)
LLM_MODEL=o3-mini python3 app.py  # set it for ONE command only
unset LLM_MODEL                   # remove it
printenv                          # list everything
```

A new terminal window does not have the variables you exported in another one.

### Reading variables in Python

A **module** is a file of Python code that you load with `import`. The **standard library**
is the set of modules that is installed together with Python. `os` is one of them.
`os.environ` is an object that maps each variable name to its value. You read and set
entries with the same syntax as a dict.

```python
import os

os.environ["LLM_MODEL"] = "gpt-4o"
os.environ["MAX_TOKENS"] = "256"
print(os.environ["LLM_MODEL"])
# gpt-4o
print(os.environ.get("PT_UNSET_VAR"))
# None
print(os.environ.get("PT_UNSET_VAR", "gpt-4o-mini"))
# gpt-4o-mini
print("PT_UNSET_VAR" in os.environ)
# False
```

`os.environ["PT_UNSET_VAR"]` raises `KeyError: 'PT_UNSET_VAR'` because that name is not
set. `.get` returns `None`, or its second argument, instead of raising.
`os.getenv(name, default)` returns the same result as `os.environ.get(name, default)`.

Type a name that is not set, then compare `d[key]` with `d.get(key)`.

```diagram
{"type":"dict","title":"Lookups in os.environ","name":"os.environ","entries":[["LLM_MODEL","gpt-4o"],["MAX_TOKENS","256"]]}
```

### Values are always strings

Every value in `os.environ` is a `str`. Convert it yourself with `int()` or `float()`.
`bool()` does not work for on/off settings, because `bool()` of any non-empty string is `True`.
Compare the text instead.

```python
import os

os.environ["MAX_TOKENS"] = "256"
os.environ["STREAM"] = "false"
raw = os.environ["MAX_TOKENS"]
print(type(raw))
# <class 'str'>
print(int(raw) + 1)
# 257
print(float(os.environ.get("PT_UNSET_VAR", "0.7")))
# 0.7
print(bool(os.environ["STREAM"]))
# True
print(os.environ["STREAM"].lower() == "true")
# False
```

### Required values and secrets

A required value such as an API key must be checked early. If it is missing or blank,
raise `RuntimeError` with the variable's name in the message. Never print or log a full
key. Print a masked version made from its first and last characters.

```python
import os

name = "PT_UNSET_API_KEY"
value = os.environ.get(name, "")
try:
    if not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
except RuntimeError as exc:
    print(exc)
# Missing required environment variable: PT_UNSET_API_KEY

key = "sk-proj-a1b2c3d4abcd"
print(f"{key[:3]}...{key[-4:]}")
# sk-...abcd
```

### .env files

A **`.env` file** is a text file of `KEY=value` lines kept next to the project. It can
also contain `#` comments, blank lines, an optional `export ` prefix and quotes around the
value. The program reads it when it starts.

The file holds secrets. Most projects save and share their code with a tool named git.
Never add the `.env` file to git: list `.env` in the file `.gitignore`, which names the
files that git must skip.

A value can contain `=`, so split each line on the first `=` only.

```python
line = "DB_URL=postgres://host/db?sslmode=require"
print(line.split("="))
# ['DB_URL', 'postgres://host/db?sslmode', 'require']
print(line.split("=", 1))
# ['DB_URL', 'postgres://host/db?sslmode=require']
```

**Precedence** is the order in which sources are checked. The usual order is: the real
environment first, then the `.env` file, then the default in the code.

Step through the stages to follow one setting from the shell to an `int`.

```diagram
{"type":"flow","title":"From the shell to a typed Python value","steps":[
{"label":"Shell","detail":"You run export in the terminal. The shell stores the name and the string value in its own environment.","code":"export LLM_MAX_TOKENS=1024"},
{"label":"Program start","detail":"The shell starts python3. The new program gets a copy of the shell's exported variables.","code":"python3 app.py"},
{"label":"os.environ","detail":"Python fills os.environ when it starts. Every value in it is a str.","code":"os.environ[\"LLM_MAX_TOKENS\"]\n# '1024'"},
{"label":".env file and default","detail":"If the name is not in os.environ, the loader uses the value it parsed from the .env file. If the file does not have it either, the loader uses the default written in the code.","code":"raw = os.environ.get(\"LLM_MAX_TOKENS\", file_values.get(\"LLM_MAX_TOKENS\", \"256\"))\n# '1024'"},
{"label":"Typed value","detail":"int() converts the string to an integer. The rest of the program uses the integer.","code":"max_tokens = int(raw)\n# 1024"}
]}
```

### Common mistakes

- Writing an API key in the code or adding the `.env` file to git.
- Doing maths on the raw string: `"256" + "1"` is `"2561"`. Convert with `int()` first.
- Using `bool(value)` for an on/off setting: `bool("false")` is `True`.
- Reading a variable once at the top of the file. Read it inside the function, so each
  call gets the current value.
- Using `os.environ[name]` for an optional setting. It raises `KeyError` when the name is not set.
- Splitting a `.env` line with `split("=")` instead of `split("=", 1)`.
'''

EXERCISES = [
    {
        "id": "env-s1",
        "lesson": r'''
            ## Environment variables

            An **environment variable** is a named string that a program receives when it starts.
            The **terminal** is the window where you type commands. A program that you start from
            the terminal receives the terminal's variables. Examples are `HOME=/home/ada`,
            `LLM_MODEL=gpt-4o` and `OPENAI_API_KEY=sk-...`. An **API key** is a secret string that
            identifies you to an online service.

            Your code reads these values instead of having them written into it. The same code can
            then run with a different model or key on another computer.

            A **module** is a file of Python code that you load with `import`. The **standard
            library** is the set of modules that is installed together with Python. `os` is one of
            them. `os.environ` is an object that maps each variable name to its value. You read and
            set entries with the same syntax as a dict.

            ```python
            import os

            os.environ["APP_MODE"] = "demo"
            os.environ["PT_RETRIES"] = "3"
            print(os.environ["APP_MODE"])
            # demo
            print(type(os.environ["PT_RETRIES"]))
            # <class 'str'>
            print(os.environ.get("PT_NOT_SET_ANYWHERE", "default"))
            # default
            ```

            Every value in `os.environ` is a string, even when it contains only digits. `"3"` is
            text, not the integer `3`.

            Square brackets raise `KeyError` for a name that is not set, the same as a dict does.
            `.get(name, default)` returns the default instead.

            Type a name that is not set, then compare `d[key]` with `d.get(key)`.

            ```diagram
            {"type":"dict","title":"Lookups in os.environ","name":"os.environ","entries":[["APP_MODE","demo"],["PT_RETRIES","3"]]}
            ```

            Assigning to `os.environ[...]` changes the variable for this running program only. The
            terminal that started it is not affected.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            import os

            os.environ["MAX_TOKENS"] = "512"
            os.environ.pop("PT_MISSING", None)
            value = os.environ["MAX_TOKENS"]
            print(value + "0")
            print(int(value) + 1)
            print(os.environ.get("PT_MISSING", "none"))
        ''',
        "solution": r'''
            5120
            513
            none
        ''',
        "explanation": r'''
            Every value in `os.environ` is a string. `value + "0"` joins the strings `"512"` and
            `"0"` into `"5120"`. `int(value)` creates the integer `512`, and `512 + 1` is `513`.
            `PT_MISSING` is not set, so `.get` returns its second argument, `"none"`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Remember what type every environment variable value has.",
            "Adding two strings joins them; adding two numbers does maths. The last line uses a default because the variable is missing.",
            "Line 1: `\"512\"` joined with `\"0\"`. Line 2: the number 512 plus one. Line 3: `.get` returns its second argument when the name is not set.",
        ],
    },
    {
        "id": "env-s2",
        "lesson": r'''
            ## Default values

            Most settings are optional. When nobody sets the variable, the program uses a
            **default value**: a value written in the code that is used when no other value is
            given. Another name for it is a **fallback**.

            `os.environ.get(name, default)` looks up `name`. If the variable is set, it returns the
            variable's value. If it is not set, it returns `default`.

            ```python
            import os

            os.environ.pop("PT_THEME", None)
            print(os.environ.get("PT_THEME", "light"))
            # light
            os.environ["PT_THEME"] = "dark"
            print(os.environ.get("PT_THEME", "light"))
            # dark
            ```

            `os.environ.pop("PT_THEME", None)` removes the variable if it is set and does nothing
            otherwise. The example uses it so that the variable starts unset.

            The default is the second argument of `.get`. Every environment value is a string, so
            the default is usually a string too. Without a second argument, `.get` returns `None`
            for a name that is not set.
        ''',
        "title": "A sensible default",
        "difficulty": 0,
        "prompt": r'''
            Your app should run in a region picked by the environment variable `APP_REGION`,
            falling back to `"eu"` when nobody set it.

            **Write:** fill in the blank (`___`) in `get_region()`

            - takes no arguments
            - **Returns:** the text of `APP_REGION` (a string), or `"eu"` when it is not set

            **Rules**
            - If `APP_REGION` is not set, return `"eu"`.
            - If `APP_REGION` is set, return its value unchanged.

            **Examples**
            ```python
            # APP_REGION not set
            get_region()   # returns "eu"
            # APP_REGION=us
            get_region()   # returns "us"
            ```
        ''',
        "starter": r'''
            import os


            def get_region():
                return os.environ.get("APP_REGION", ___)
        ''',
        "tests": r'''
            import os
            from solution import get_region

            def _with(value):
                old = os.environ.pop("APP_REGION", None)
                try:
                    if value is not None:
                        os.environ["APP_REGION"] = value
                    return get_region()
                finally:
                    os.environ.pop("APP_REGION", None)
                    if old is not None:
                        os.environ["APP_REGION"] = old

            def test_unset_region_returns_eu():
                got = _with(None)
                assert got == "eu", f"got {got!r}"

            def test_set_region_returns_its_value():
                got = _with("us")
                assert got == "us", f"got {got!r}"
        ''',
        "solution": r'''
            import os


            def get_region():
                return os.environ.get("APP_REGION", "eu")
        ''',
        "hints": [
            "The second argument of `.get()` is what you get back when the name is missing.",
            "Put the default region there, as a string.",
            "Replace `___` with the string `\"eu\"` (with quotes).",
        ],
    },
    {
        "id": "env-s3",
        "lesson": r'''
            ## Type conversion

            Every environment value is a string. `+` between two strings joins them. It does not
            add numbers.

            **Type conversion** creates a value of one type from a value of another type. It is also
            called **casting**. `int()` converts a string to a whole number. `float()` converts a
            string to a decimal number.

            ```python
            import os

            os.environ["PT_TEMPERATURE"] = "0.2"
            raw = os.environ["PT_TEMPERATURE"]
            print(raw + raw)
            # 0.20.2
            print(float(raw) + float(raw))
            # 0.4
            ```

            `raw + raw` joins the two strings into `0.20.2`. After `float(raw)`, `+` adds two numbers.

            For an optional setting, write the default as a string and convert the result of `.get`.

            ```python
            import os

            top_p = float(os.environ.get("PT_TOP_P_UNSET", "1.0"))
            print(top_p)
            # 1.0
            print(type(top_p))
            # <class 'float'>
            ```

            `.get` returns a string in both cases: the variable's value or the default `"1.0"`.
            `float()` then converts whichever string it got. The result has the same type whether the
            variable is set or not.
        ''',
        "title": "Fix the token limit",
        "difficulty": 0,
        "prompt": r'''
            A token limit read from the environment must be a number before you can do maths with it.
            `get_max_tokens()` returns the wrong type. Find the bug and fix it.

            **Write:** fix `get_max_tokens()`

            - takes no arguments
            - **Returns:** the `MAX_TOKENS` environment variable **as an `int`**, or the `int` `256`
              when it is not set

            **Rules**
            - If `MAX_TOKENS` is not set, return `256` (an `int`, not the string `"256"`).
            - If `MAX_TOKENS` is set (e.g. to `"1024"`), return it converted to an `int`.

            **Examples**
            ```python
            # MAX_TOKENS not set
            get_max_tokens()   # returns 256
            # MAX_TOKENS=1024
            get_max_tokens()   # returns 1024   (an int, not "1024")
            ```
        ''',
        "starter": r'''
            import os


            def get_max_tokens():
                return os.environ.get("MAX_TOKENS", "256")
        ''',
        "tests": r'''
            import os
            from solution import get_max_tokens

            def _with(value):
                old = os.environ.pop("MAX_TOKENS", None)
                try:
                    if value is not None:
                        os.environ["MAX_TOKENS"] = value
                    return get_max_tokens()
                finally:
                    os.environ.pop("MAX_TOKENS", None)
                    if old is not None:
                        os.environ["MAX_TOKENS"] = old

            def test_unset_returns_int_256():
                got = _with(None)
                assert got == 256 and isinstance(got, int), f"got {got!r}"

            def test_set_value_is_converted_to_int():
                got = _with("1024")
                assert got == 1024 and isinstance(got, int), f"got {got!r}"
        ''',
        "solution": r'''
            import os


            def get_max_tokens():
                return int(os.environ.get("MAX_TOKENS", "256"))
        ''',
        "hints": [
            "What type are environment variable values? What type should this function return?",
            "The value (or the default) is text. Convert it to a whole number before returning.",
            "Wrap the whole `os.environ.get(...)` call in `int(...)`.",
        ],
    },
    {
        "id": "env-s4",
        "lesson": r'''
            ## Missing, empty or set

            A variable is in one of three states: not set, set to the empty string (`KEY=`), or set
            to some text. For an API key, both "not set" and "empty" mean there is no key.

            ```python
            import os

            os.environ.pop("PT_TOKEN", None)
            print(os.environ.get("PT_TOKEN", "") != "")
            # False
            os.environ["PT_TOKEN"] = ""
            print(os.environ.get("PT_TOKEN", "") != "")
            # False
            os.environ["PT_TOKEN"] = "abc"
            print(os.environ.get("PT_TOKEN", "") != "")
            # True
            ```

            With `""` as the default, `.get` returns `""` for a variable that is not set and for one
            that is empty. One comparison then covers both states.

            A comparison such as `!= ""` produces a bool: `True` or `False`. You can return it
            directly. No `if` is needed.

            ```python
            import os

            os.environ["PT_TOKEN"] = ""
            print("PT_TOKEN" in os.environ)
            # True
            ```

            `"PT_TOKEN" in os.environ` only tells you that the name is set. It is `True` even when
            the value is empty.
        ''',
        "title": "Is the key there?",
        "difficulty": 0,
        "prompt": r'''
            Before calling an LLM API, check that the API key is actually there.

            **Write:** `has_api_key()`

            - takes no arguments
            - **Returns:** a bool: `True` if the environment variable `OPENAI_API_KEY` is set
              **and not empty**, otherwise `False`

            **Rules**
            - Set to a non-empty value (e.g. `"sk-123"`) -> `True`.
            - Not set at all -> `False` (must not raise `KeyError`).
            - Set to the empty string `""` -> `False`.
            - Return the real bools `True`/`False`, not the key itself.

            **Examples**
            ```python
            # OPENAI_API_KEY=sk-123
            has_api_key()   # returns True
            # OPENAI_API_KEY not set
            has_api_key()   # returns False
            # OPENAI_API_KEY=""  (empty)
            has_api_key()   # returns False
            ```
        ''',
        "starter": r'''
            import os


            def has_api_key():
                ...
        ''',
        "tests": r'''
            import os
            from solution import has_api_key

            def _with(value):
                old = os.environ.pop("OPENAI_API_KEY", None)
                try:
                    if value is not None:
                        os.environ["OPENAI_API_KEY"] = value
                    return has_api_key()
                finally:
                    os.environ.pop("OPENAI_API_KEY", None)
                    if old is not None:
                        os.environ["OPENAI_API_KEY"] = old

            def test_non_empty_key_returns_true():
                assert _with("sk-123") is True

            def test_unset_key_returns_false():
                assert _with(None) is False

            def test_empty_key_returns_false():
                assert _with("") is False
        ''',
        "solution": r'''
            import os


            def has_api_key():
                return os.environ.get("OPENAI_API_KEY", "") != ""
        ''',
        "hints": [
            "Use `os.environ.get` so a missing variable does not crash.",
            "Get the value with an empty-string default, then check whether it is not empty.",
            "Return the result of comparing `os.environ.get(\"OPENAI_API_KEY\", \"\")` with `\"\"` using `!=` (that comparison is already True or False).",
        ],
    },
    {
        "id": "env-s5",
        "lesson": r'''
            ## Setting variables and running a script

            You set environment variables in the terminal:

            ```bash
            export USER_NAME=Ada          # for this terminal session
            python3 solution.py
            USER_NAME=Bob python3 solution.py   # for this one command only
            ```

            Do not put spaces around `=`. An exported variable is gone when you close the terminal.

            A **script** is a Python file that you run directly. Python executes its lines from top
            to bottom. The code does not need to be inside a function, and it can read the
            environment directly.

            ```python
            import os

            os.environ["PT_CITY"] = "Lyon"
            city = os.environ.get("PT_CITY", "somewhere")
            print(f"Weather for {city}")
            # Weather for Lyon
            ```

            This example sets `PT_CITY` in Python only because the Run button cannot type terminal
            commands. In a real script, the terminal sets it.

            An **exit code** is a whole number that a program reports to the terminal when it ends.
            A script that runs to the end without an error has exit code `0`, which means success.
            A script that stops with an exception that no `except` caught has exit code `1`.
        ''',
        "title": "Greeting script",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            Scripts often personalise their output from an environment variable.

            **Write a script** (top-level code, no function needed) that reads the environment
            variable `USER_NAME` and prints one greeting line.

            **Rules**
            - Print exactly `Hello, <name>!` (comma, one space, exclamation mark) where `<name>`
              is the value of `USER_NAME`.
            - If `USER_NAME` is not set, use `stranger` as the name.
            - The script must finish without an error (exit code 0).

            **Examples**

            Running `USER_NAME=Ada python3 solution.py` prints:
            ```
            Hello, Ada!
            ```

            Running `python3 solution.py` (with `USER_NAME` not set) prints:
            ```
            Hello, stranger!
            ```
        ''',
        "starter": r'''
            import os

            # read USER_NAME and print the greeting
        ''',
        "tests": r'''
            def test_prints_hello_with_user_name():
                r = run_script(env={"USER_NAME": "Ada"})
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "Hello, Ada!", f"printed {r.stdout!r}"

            def test_prints_hello_stranger_when_unset():
                r = run_script()
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "Hello, stranger!", f"printed {r.stdout!r}"
        ''',
        "solution": r'''
            import os

            name = os.environ.get("USER_NAME", "stranger")
            print(f"Hello, {name}!")
        ''',
        "hints": [
            "Read the variable with a default, then print an f-string.",
            "Two lines: one gets the name (falling back to `stranger`), one prints the greeting.",
            "Store `os.environ.get(\"USER_NAME\", \"stranger\")` in `name`, then `print` an f-string with `name` between `Hello, ` and `!`.",
        ],
    },
    {
        "id": "env-s6",
        "lesson": r'''
            ## On/off settings

            A **feature flag** is a setting that turns one behaviour on or off, such as `DEBUG` or
            `STREAM`. The variable holds text, not a bool. `bool()` of a string is `False` only for
            the empty string. Every other string gives `True`.

            ```python
            import os

            os.environ["PT_VERBOSE"] = "false"
            value = os.environ["PT_VERBOSE"]
            print(bool(value))
            # True
            print(bool(""))
            # False
            ```

            `bool("false")` is `True` because `"false"` is a non-empty string. Do not convert a
            flag with `bool()`. Compare the text with the word you expect instead.

            ```python
            import os

            os.environ["PT_VERBOSE"] = "false"
            value = os.environ["PT_VERBOSE"]
            print(value == "true")
            # False
            print("TRUE".lower())
            # true
            print("TRUE".lower() == "true")
            # True
            ```

            `.lower()` returns a copy of the string with every letter in lower case. Call it before
            the comparison, so `TRUE`, `True` and `true` all compare equal to `"true"`.
        ''',
        "title": "Debug switch",
        "difficulty": 0,
        "prompt": r'''
            Turn extra logging on with the environment variable `DEBUG`.

            **Write:** `debug_enabled()`

            - takes no arguments
            - **Returns:** a bool: `True` when `DEBUG` is the word `true` in any letter case,
              otherwise `False`

            **Rules**
            - `"true"`, `"True"`, `"TRUE"` -> `True`.
            - Anything else -> `False`, including `"false"`, `"no"` and the empty string.
            - Not set at all -> `False` (must not raise `KeyError`).
            - Return the real bools `True`/`False`.

            **Examples**
            ```python
            # DEBUG=TRUE
            debug_enabled()   # returns True
            # DEBUG=false
            debug_enabled()   # returns False
            # DEBUG not set
            debug_enabled()   # returns False
            ```
        ''',
        "starter": r'''
            import os


            def debug_enabled():
                return bool(os.environ.get("DEBUG", ""))
        ''',
        "tests": r'''
            import os
            from solution import debug_enabled

            def _with(value):
                old = os.environ.pop("DEBUG", None)
                try:
                    if value is not None:
                        os.environ["DEBUG"] = value
                    return debug_enabled()
                finally:
                    os.environ.pop("DEBUG", None)
                    if old is not None:
                        os.environ["DEBUG"] = old

            def test_true_in_any_case_returns_true():
                for raw in ["true", "True", "TRUE"]:
                    got = _with(raw)
                    assert got is True, f"DEBUG={raw!r} -> {got!r}"

            def test_false_or_other_words_return_false():
                for raw in ["false", "no", ""]:
                    got = _with(raw)
                    assert got is False, f"DEBUG={raw!r} -> {got!r}"

            def test_unset_returns_false():
                assert _with(None) is False
        ''',
        "solution": r'''
            import os


            def debug_enabled():
                return os.environ.get("DEBUG", "").lower() == "true"
        ''',
        "hints": [
            "The starter uses `bool()` on the text. What is `bool(\"false\")`?",
            "Instead of converting with `bool`, compare the text with the word you want, after making the letter case uniform.",
            "Get `DEBUG` with `.get` and an empty-string default, call `.lower()` on it, and return whether it equals `\"true\"` (a `==` comparison is already a bool).",
        ],
    },
    {
        "id": "env-1",
        "lesson": r'''
            ## Read the variable on every call

            **Import time** is the moment Python runs the top-level lines of a file. That happens
            once, when the file is first run or imported. A variable read there is read once. A
            variable read inside a function is read each time the function is called.

            ```python
            import os

            os.environ["PT_COLOR"] = "red"
            SAVED = os.environ["PT_COLOR"]

            def current():
                return os.getenv("PT_COLOR", "none")

            os.environ["PT_COLOR"] = "blue"
            print(SAVED)
            # red
            print(current())
            # blue
            ```

            `SAVED` got the string `"red"` when its line ran. Changing the environment later does not
            change `SAVED`. `current()` looks the variable up on every call, so it returns `blue`.

            Step through the code and watch `SAVED` stay `'red'` after line 9 runs.

            ```diagram
            {"type": "trace", "title": "Read once at the top versus read on every call", "code": ["import os", "", "os.environ[\"PT_COLOR\"] = \"red\"", "SAVED = os.environ[\"PT_COLOR\"]", "", "def current():", "    return os.getenv(\"PT_COLOR\", \"none\")", "", "os.environ[\"PT_COLOR\"] = \"blue\"", "print(SAVED)", "print(current())"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 3, "vars": {}, "out": ""},
              {"line": 4, "vars": {}, "out": ""},
              {"line": 6, "vars": {"SAVED": "'red'"}, "out": ""},
              {"line": 9, "vars": {"SAVED": "'red'"}, "out": ""},
              {"line": 10, "vars": {"SAVED": "'red'"}, "out": ""},
              {"line": 11, "vars": {"SAVED": "'red'"}, "out": "red\n"},
              {"line": 7, "vars": {}, "out": "red\n"},
              {"line": null, "vars": {"SAVED": "'red'"}, "out": "red\nblue\n"}
            ]}
            ```

            `os.getenv(name, default)` returns the same result as `os.environ.get(name, default)`.
            Reading on every call matters for tests (small programs that check your code), which set variables with `os.environ[...] = ...` before they call the function.
        ''',
        "research": {"note": "Skim the official docs for `os.environ` and `os.getenv` - note what each returns for a missing name.",
         "links": [{"title": "os.environ - Python docs", "url": "https://docs.python.org/3/library/os.html#os.environ"},
                   {"title": "os.getenv - Python docs", "url": "https://docs.python.org/3/library/os.html#os.getenv"}]},
        "hints": [
            "`os.getenv` (or `os.environ.get`) takes a default for when the variable is missing.",
            "Read the variable inside the function body, so it is looked up fresh on every call, and fall back to the default model.",
            "Import `os` at the top of the file. Inside `get_model`, return the result of `os.getenv` called with the variable name as the first argument and the default model name as the second.",
        ],
        "title": "Model from the environment",
        "difficulty": 1,
        "prompt": r'''
            Apps let you switch the LLM model without editing code, by reading it from the environment.

            **Write:** `get_model()`

            - takes no arguments
            - **Returns:** a string: the value of the environment variable `LLM_MODEL`, or
              `"gpt-4o-mini"` when it is not set

            **Rules**
            - If `LLM_MODEL` is not set, return `"gpt-4o-mini"` (must not raise `KeyError`).
            - If `LLM_MODEL` is set, return its value unchanged.
            - Read the variable **each time the function is called**, not once when the file is
              imported: if `LLM_MODEL` changes while the program runs, the next call returns the new value.

            **Examples**
            ```python
            # LLM_MODEL not set
            get_model()   # returns "gpt-4o-mini"
            # LLM_MODEL=claude-sonnet
            get_model()   # returns "claude-sonnet"
            # LLM_MODEL=model-a, then later LLM_MODEL=model-b
            get_model()   # returns "model-a", then "model-b" on the next call
            ```
        ''',
        "starter": r'''
            def get_model():
                ...
        ''',
        "tests": r'''
            import os
            from solution import get_model

            def _with(value):
                old = os.environ.pop("LLM_MODEL", None)
                try:
                    if value is not None:
                        os.environ["LLM_MODEL"] = value
                    return get_model()
                finally:
                    os.environ.pop("LLM_MODEL", None)
                    if old is not None:
                        os.environ["LLM_MODEL"] = old

            def test_unset_returns_gpt_4o_mini():
                got = _with(None)
                assert got == "gpt-4o-mini", f"got {got!r}"

            def test_set_variable_is_returned():
                got = _with("claude-sonnet")
                assert got == "claude-sonnet", f"got {got!r}"

            def test_reads_variable_on_every_call():
                a = _with("model-a")
                b = _with("model-b")
                assert (a, b) == ("model-a", "model-b"), f"got {a!r} then {b!r}"

            def test_unset_does_not_raise_key_error():
                try:
                    _with(None)
                except KeyError:
                    raise AssertionError("a missing variable raised KeyError instead of using the default")
        ''',
        "solution": r'''
            import os

            def get_model():
                return os.getenv("LLM_MODEL", "gpt-4o-mini")
        ''',
    },
    {
        "id": "env-2",
        "lesson": r'''
            ## Required variables

            Some settings are not optional. Without an API key, no API call can work. Check required
            values early and stop with a clear message. Otherwise the program fails later, inside an
            API call, with an error that does not name the cause.

            A value that contains only spaces is as useless as an empty one. `.strip()` returns the
            string without leading and trailing whitespace, so a blank value becomes `""`. An empty
            string is falsy, so `not value.strip()` is `True` for a missing, empty or blank value.

            ```python
            import os

            os.environ["PT_PORT"] = "   "
            port = os.environ.get("PT_PORT", "")
            print(repr(port))
            # '   '
            print(repr(port.strip()))
            # ''
            print(not port.strip())
            # True
            ```

            You stop the program with `raise`. `RuntimeError` is the usual exception type when the
            program is not set up correctly.

            ```python
            import os

            os.environ["PT_PORT"] = "   "
            port = os.environ.get("PT_PORT", "")
            try:
                if not port.strip():
                    raise RuntimeError("Missing required environment variable: PT_PORT")
            except RuntimeError as exc:
                print("stopped:", exc)
            # stopped: Missing required environment variable: PT_PORT
            ```

            Put the variable's name in the message. The person who reads it needs to know exactly
            which variable to set.
        ''',
        "hints": [
            "Read with `.get` and a default so a missing variable does not raise `KeyError`; then decide yourself whether to raise.",
            "Treat a missing variable and a blank one the same way: if the value is empty after stripping spaces, raise `RuntimeError` with a message that includes the name.",
            "`value = os.environ.get(name, \"\")`. `if not value.strip():` raise `RuntimeError(f\"Missing required environment variable: {name}\")`. Otherwise return `value`.",
        ],
        "title": "Required variable",
        "difficulty": 1,
        "prompt": r'''
            Some settings (like an API key) are required: the app should stop early with a clear
            message instead of failing later in a confusing way.

            **Write:** `require_env(name)`

            - `name`: the name of an environment variable, a string, e.g. `"OPENAI_API_KEY"`
            - **Returns:** the variable's value (a string, unchanged)

            **Rules**
            - If the variable is set and not blank, return its value.
            - If the variable is **not set**, raise `RuntimeError` (not `KeyError`).
            - If the variable is **empty or only whitespace** (e.g. `"   "`), also raise `RuntimeError`.
            - The error message must contain the variable's name, e.g.
              `"Missing required environment variable: OPENAI_API_KEY"`.

            **Examples**
            ```python
            # PT_API_KEY=sk-123
            require_env("PT_API_KEY")        # returns "sk-123"
            # OPENAI_API_KEY not set
            require_env("OPENAI_API_KEY")    # raises RuntimeError("Missing required environment variable: OPENAI_API_KEY")
            # PT_EMPTY="   "
            require_env("PT_EMPTY")          # raises RuntimeError (message contains "PT_EMPTY")
            ```
        ''',
        "starter": r'''
            def require_env(name):
                ...
        ''',
        "tests": r'''
            import os
            from solution import require_env

            def _call(name, value):
                old = os.environ.pop(name, None)
                try:
                    if value is not None:
                        os.environ[name] = value
                    return require_env(name)
                finally:
                    os.environ.pop(name, None)
                    if old is not None:
                        os.environ[name] = old

            def test_set_variable_returns_value():
                got = _call("PT_API_KEY", "sk-123")
                assert got == "sk-123", f"got {got!r}"

            def test_missing_raises_runtime_error_naming_variable():
                try:
                    _call("PT_SECRET_TOKEN", None)
                except RuntimeError as e:
                    assert "PT_SECRET_TOKEN" in str(e), f"message does not name the variable: {e}"
                else:
                    raise AssertionError("no RuntimeError for a missing variable")

            def test_blank_value_raises_runtime_error_naming_variable():
                try:
                    _call("PT_EMPTY", "   ")
                except RuntimeError as e:
                    assert "PT_EMPTY" in str(e), f"message does not name the variable: {e}"
                else:
                    raise AssertionError("no RuntimeError for a blank variable")

            def test_missing_does_not_raise_key_error():
                try:
                    _call("PT_OTHER", None)
                except KeyError:
                    raise AssertionError("raised KeyError; the spec asks for RuntimeError")
                except RuntimeError:
                    pass
        ''',
        "solution": r'''
            import os

            def require_env(name):
                value = os.environ.get(name, "")
                if not value.strip():
                    raise RuntimeError(f"Missing required environment variable: {name}")
                return value
        ''',
    },
    {
        "id": "env-7",
        "lesson": r'''
            ## A config dict

            Real apps read all their settings in one place. A **config dict** is a dict built when
            the program starts. It maps each setting name to its value, already converted to the
            right type.

            ```python
            import os

            os.environ["PT_RETRIES"] = "5"
            os.environ.pop("PT_TIMEOUT", None)
            config = {
                "retries": int(os.environ.get("PT_RETRIES", "3")),
                "timeout": float(os.environ.get("PT_TIMEOUT", "30")),
            }
            print(config)
            # {'retries': 5, 'timeout': 30.0}
            print(config["retries"] + 1)
            # 6
            ```

            Each entry does two things. `.get` reads the variable with a string default. `int()` or
            `float()` then converts that string to the right type.

            `PT_RETRIES` is set, so `"retries"` is `5`. `PT_TIMEOUT` is not set, so `.get` returns the
            default `"30"` and `float("30")` gives `30.0`.

            The rest of the app reads `config["retries"]`, which is an `int`, and never reads
            `os.environ` itself. All the defaults are in one place, so the dict also documents every
            setting the app accepts.
        ''',
        "title": "Model settings dict",
        "difficulty": 1,
        "prompt": r'''
            Gather the model settings from the environment into one config dict, with defaults
            and the right types.

            **Write:** `load_config()`

            - takes no arguments
            - **Returns:** a dict with exactly these three keys:

            | key | environment variable | type | default |
            | --- | --- | --- | --- |
            | `"model"` | `LLM_MODEL` | `str` | `"gpt-4o-mini"` |
            | `"temperature"` | `LLM_TEMPERATURE` | `float` | `0.7` |
            | `"max_tokens"` | `LLM_MAX_TOKENS` | `int` | `256` |

            **Rules**
            - A variable that is not set uses its default.
            - `"temperature"` is always a `float` and `"max_tokens"` always an `int`, whether the
              value came from the environment or from the default.
            - Read the variables each time the function is called.

            **Examples**
            ```python
            # nothing set
            load_config()   # returns {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}
            # LLM_MODEL=o3-mini  LLM_TEMPERATURE=0  LLM_MAX_TOKENS=1024
            load_config()   # returns {"model": "o3-mini", "temperature": 0.0, "max_tokens": 1024}
            ```
        ''',
        "starter": r'''
            import os


            def load_config():
                ...
        ''',
        "tests": r'''
            import os
            from solution import load_config

            NAMES = ("LLM_MODEL", "LLM_TEMPERATURE", "LLM_MAX_TOKENS")

            def _call(env):
                saved = {n: os.environ.pop(n, None) for n in NAMES}
                try:
                    for k, v in env.items():
                        os.environ[k] = v
                    return load_config()
                finally:
                    for n in NAMES:
                        os.environ.pop(n, None)
                        if saved[n] is not None:
                            os.environ[n] = saved[n]

            def test_nothing_set_gives_defaults():
                got = _call({})
                assert got == {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}, f"got {got!r}"

            def test_values_from_environment_are_converted():
                got = _call({"LLM_MODEL": "o3-mini", "LLM_TEMPERATURE": "0", "LLM_MAX_TOKENS": "1024"})
                assert got == {"model": "o3-mini", "temperature": 0.0, "max_tokens": 1024}, f"got {got!r}"

            def test_types_are_float_and_int():
                got = _call({"LLM_TEMPERATURE": "1"})
                assert isinstance(got["temperature"], float), f"temperature is {got['temperature']!r}"
                assert isinstance(got["max_tokens"], int), f"max_tokens is {got['max_tokens']!r}"
                got = _call({})
                assert isinstance(got["temperature"], float), "default temperature must be a float"

            def test_reads_environment_on_every_call():
                a = _call({"LLM_MODEL": "a"})["model"]
                b = _call({"LLM_MODEL": "b"})["model"]
                assert (a, b) == ("a", "b"), f"got {a!r} then {b!r}"
        ''',
        "solution": r'''
            import os


            def load_config():
                return {
                    "model": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
                    "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.7")),
                    "max_tokens": int(os.environ.get("LLM_MAX_TOKENS", "256")),
                }
        ''',
        "hints": [
            "Each entry is one `os.environ.get` with a default, plus a type conversion where needed.",
            "Write the defaults as strings and convert the result of `.get`, so the type is right in both cases.",
            "Return a dict literal: `\"model\"` from `.get(\"LLM_MODEL\", \"gpt-4o-mini\")`, `\"temperature\"` as `float(...get(\"LLM_TEMPERATURE\", \"0.7\"))`, `\"max_tokens\"` as `int(...get(\"LLM_MAX_TOKENS\", \"256\"))`.",
        ],
    },
    {
        "id": "env-8",
        "lesson": r'''
            ## .env files

            Typing `export` for ten variables in every new terminal takes time. Projects keep the
            variables in a **`.env` file**: a text file next to the code with one `KEY=value` per line.

            ```text
            OPENAI_API_KEY=sk-abc123
            LLM_MODEL=gpt-4o
            ```

            The program reads the file when it starts. The file holds secrets such as API keys.
            Most projects save and share their code with a tool named git. The `.env` file is
            never added to git.

            `str.split("=")` splits a string at every `=` and returns a list of the pieces.

            ```python
            line = "DB_URL=postgres://host/db?sslmode=require"
            parts = line.split("=")
            print(parts)
            # ['DB_URL', 'postgres://host/db?sslmode', 'require']
            print(len(parts))
            # 3
            ```

            The value itself contains `=`, so the split produces 3 pieces instead of 2. You need to
            split at the first `=` only. `str.split` can do that with one extra argument, the same
            one you used in the strings chapter. Finding it in the docs is part of this step.

            Unpacking a list into two names raises `ValueError` if the list does not have exactly
            two items.

            ```python
            key, value = "PT_MODE=fast".split("=")
            print(key, value)
            # PT_MODE fast
            try:
                key, value = "no equals sign here".split("=")
            except ValueError as exc:
                print("ValueError:", exc)
            # ValueError: not enough values to unpack (expected 2, got 1)
            ```
        ''',
        "research": {"note": "Read the `str.split` documentation and find how to limit the number of splits, then come back.",
         "links": [{"title": "str.split - Python docs", "url": "https://docs.python.org/3/library/stdtypes.html#str.split"}]},
        "title": "Parse one .env line",
        "difficulty": 1,
        "prompt": r'''
            The first building block of a `.env` loader: split one `KEY=value` line.

            **Write:** `parse_env_line(line)`

            - `line`: one line of a `.env` file, a string like `"LLM_MODEL=gpt-4o"`
            - **Returns:** a tuple `(key, value)` of two strings

            **Rules**
            - Split at the **first** `=` only: everything after it is the value, even if it
              contains more `=` signs.
            - Strip spaces (and a trailing newline) from both the key and the value.
            - `"EMPTY="` gives `("EMPTY", "")`.
            - A line with no `=` at all raises `ValueError` (any message).

            **Examples**
            ```python
            parse_env_line("LLM_MODEL=gpt-4o")        # returns ("LLM_MODEL", "gpt-4o")
            parse_env_line(" API_KEY = sk-1 \n")      # returns ("API_KEY", "sk-1")
            parse_env_line("URL=http://x/?a=b&c=d")   # returns ("URL", "http://x/?a=b&c=d")
            parse_env_line("EMPTY=")                  # returns ("EMPTY", "")
            parse_env_line("nonsense")                # raises ValueError
            ```
        ''',
        "starter": r'''
            def parse_env_line(line):
                ...
        ''',
        "tests": r'''
            from solution import parse_env_line

            def test_simple_line():
                got = parse_env_line("LLM_MODEL=gpt-4o")
                assert got == ("LLM_MODEL", "gpt-4o"), f"got {got!r}"

            def test_spaces_and_newline_are_stripped():
                got = parse_env_line(" API_KEY = sk-1 \n")
                assert got == ("API_KEY", "sk-1"), f"got {got!r}"

            def test_value_keeps_later_equals_signs():
                got = parse_env_line("URL=http://x/?a=b&c=d")
                assert got == ("URL", "http://x/?a=b&c=d"), f"got {got!r}"

            def test_empty_value_is_empty_string():
                got = parse_env_line("EMPTY=")
                assert got == ("EMPTY", ""), f"got {got!r}"

            def test_line_without_equals_raises_value_error():
                try:
                    parse_env_line("nonsense")
                except ValueError:
                    return
                raise AssertionError("expected ValueError for a line without '='")
        ''',
        "solution": r'''
            def parse_env_line(line):
                if "=" not in line:
                    raise ValueError(f"not a KEY=value line: {line!r}")
                key, value = line.split("=", 1)
                return key.strip(), value.strip()
        ''',
        "hints": [
            "`str.split` has an optional second argument that limits how many splits happen.",
            "Split the line once at `=`, then clean both halves. Check first whether there is an `=` at all.",
            "If `\"=\"` is not in `line`, `raise ValueError(...)`. Otherwise `key, value = line.split(\"=\", 1)` and return `key.strip(), value.strip()`.",
        ],
    },
    {
        "id": "env-3",
        "hints": [
            "Both helpers start the same way: get the raw string, strip it, and return the default if it is empty.",
            "For ints, try `int()` and turn a failure into a `ValueError` that names the variable. For bools, lower-case the text and compare against the allowed true words and false words.",
            "`raw = os.environ.get(name, \"\").strip()`; `if not raw: return default`. env_int: `try: return int(raw)` / `except ValueError: raise ValueError(f\"{name} ...\")`. env_bool: lower-case `raw`, return True if it is in a set of true words, False if in a set of false words, else raise ValueError mentioning `name`.",
        ],
        "title": "Typed settings",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Environment variables are always strings. Real apps need numbers and on/off flags, so
            you write small typed readers for them.

            **Write:** `env_int(name, default)` and `env_bool(name, default)`

            - `name`: the environment variable's name, a string, e.g. `"MAX_TOKENS"`
            - `default`: the value to return when the variable is unset or empty (an `int` for
              `env_int`, a `bool` for `env_bool`)
            - **Returns:** `env_int` returns an `int`; `env_bool` returns `True` or `False`

            **Rules for `env_int`**
            - Unset, or set to `""` -> return `default`.
            - Otherwise return the value converted to `int`; surrounding spaces are allowed
              (`" 512 "` -> `512`).
            - Not a valid integer (e.g. `"three"`) -> raise `ValueError` whose message contains `name`.

            **Rules for `env_bool`**
            - Unset, or set to `""` -> return `default`.
            - `"1"`, `"true"`, `"yes"`, `"on"` -> `True`.
            - `"0"`, `"false"`, `"no"`, `"off"` -> `False`.
            - Case-insensitive (`"TRUE"`, `"False"` work) and surrounding spaces are ignored (`" OFF "` -> `False`).
            - Anything else (e.g. `"maybe"`) -> raise `ValueError` whose message contains `name`.
            - Return the real bools `True`/`False`.

            **Examples**
            ```python
            # MAX_TOKENS=" 512 "   STREAM=False   DEBUG not set   RETRIES=three
            env_int("MAX_TOKENS", 256)   # returns 512
            env_int("RETRIES", 3)        # raises ValueError (message contains "RETRIES")
            env_bool("STREAM", True)     # returns False
            env_bool("DEBUG", False)     # returns False  (unset -> default)
            ```
        ''',
        "starter": r'''
            def env_int(name, default):
                ...


            def env_bool(name, default):
                ...
        ''',
        "tests": r'''
            import os
            from solution import env_int, env_bool

            def _call(fn, name, value, default):
                old = os.environ.pop(name, None)
                try:
                    if value is not None:
                        os.environ[name] = value
                    return fn(name, default)
                finally:
                    os.environ.pop(name, None)
                    if old is not None:
                        os.environ[name] = old

            def test_env_int_parses_value_with_spaces():
                got = _call(env_int, "PT_MAX", " 512 ", 256)
                assert got == 512 and isinstance(got, int), f"got {got!r}"

            def test_env_int_unset_or_empty_returns_default():
                assert _call(env_int, "PT_MAX", None, 256) == 256
                assert _call(env_int, "PT_MAX", "", 256) == 256, "empty string should use the default"

            def test_env_int_invalid_raises_value_error_naming_variable():
                try:
                    _call(env_int, "PT_RETRIES", "three", 3)
                except ValueError as e:
                    assert "PT_RETRIES" in str(e), f"message does not name the variable: {e}"
                else:
                    raise AssertionError("no ValueError for 'three'")

            def test_env_bool_false_words_any_case_return_false():
                for raw in ["false", "False", "0", "no", " OFF "]:
                    got = _call(env_bool, "PT_STREAM", raw, True)
                    assert got is False, f"{raw!r} -> {got!r}"

            def test_env_bool_true_words_any_case_return_true():
                for raw in ["true", "TRUE", "1", "yes", "on"]:
                    got = _call(env_bool, "PT_STREAM", raw, False)
                    assert got is True, f"{raw!r} -> {got!r}"

            def test_env_bool_default_and_invalid_raises_value_error():
                assert _call(env_bool, "PT_DEBUG", None, False) is False
                assert _call(env_bool, "PT_DEBUG", "", True) is True
                try:
                    _call(env_bool, "PT_DEBUG", "maybe", False)
                except ValueError as e:
                    assert "PT_DEBUG" in str(e), f"message does not name the variable: {e}"
                else:
                    raise AssertionError("no ValueError for 'maybe'")
        ''',
        "solution": r'''
            import os

            TRUE = {"1", "true", "yes", "on"}
            FALSE = {"0", "false", "no", "off"}


            def env_int(name, default):
                raw = os.environ.get(name, "").strip()
                if not raw:
                    return default
                try:
                    return int(raw)
                except ValueError:
                    raise ValueError(f"{name} must be an integer, got {raw!r}") from None


            def env_bool(name, default):
                raw = os.environ.get(name, "").strip().lower()
                if not raw:
                    return default
                if raw in TRUE:
                    return True
                if raw in FALSE:
                    return False
                raise ValueError(f"{name} must be a boolean, got {raw!r}")
        ''',
    },
    {
        "id": "env-4",
        "hints": [
            "Handle the special cases first (empty/None, then short), then use slicing.",
            "An empty value or None gives an empty string; 8 characters or fewer gives the fixed mask; otherwise join the first 3 characters, three dots and the last 4.",
            "`if not value: return \"\"`. `if len(value) <= 8: return \"****\"`. Otherwise return an f-string built from `value[:3]`, `\"...\"` and `value[-4:]`.",
        ],
        "title": "Mask a secret",
        "difficulty": 2,
        "prompt": r'''
            Logs and error messages must never show a full API key. Show just enough to recognise it.

            **Write:** `mask_secret(value)`

            - `value`: a secret string such as `"sk-proj-a1b2c3d4e5f6abcd"`, or `None`
            - **Returns:** a string that hides the middle of the secret

            **Rules**
            - `None` or `""` -> return `""`.
            - 8 characters or fewer -> return `"****"` (too short to reveal anything).
            - Longer than 8 characters -> the first 3 characters, then `...` (three dots), then the
              last 4 characters. Nothing from the middle may appear.

            **Examples**
            ```python
            mask_secret("sk-proj-a1b2c3d4e5f6abcd")   # returns "sk-...abcd"
            mask_secret("abc123456")                  # returns "abc...3456"   (9 chars)
            mask_secret("12345678")                   # returns "****"         (8 chars)
            mask_secret(None)                         # returns ""
            ```
        ''',
        "starter": r'''
            def mask_secret(value):
                ...
        ''',
        "tests": r'''
            from solution import mask_secret

            def test_long_key_keeps_first_3_and_last_4():
                got = mask_secret("sk-proj-a1b2c3d4e5f6abcd")
                assert got == "sk-...abcd", f"got {got!r}"

            def test_nine_characters_is_masked_with_dots():
                got = mask_secret("abc123456")
                assert got == "abc...3456", f"got {got!r}"

            def test_eight_or_fewer_chars_become_four_stars():
                for v in ["short", "12345678", "a"]:
                    got = mask_secret(v)
                    assert got == "****", f"mask_secret({v!r}) -> {got!r}"

            def test_empty_string_and_none_return_empty_string():
                assert mask_secret("") == ""
                assert mask_secret(None) == ""

            def test_middle_of_key_is_never_shown():
                key = "sk-SECRETMIDDLEPART-wxyz"
                got = mask_secret(key)
                assert "SECRET" not in got and "MIDDLE" not in got, f"leaked: {got!r}"
        ''',
        "solution": r'''
            def mask_secret(value):
                if not value:
                    return ""
                if len(value) <= 8:
                    return "****"
                return f"{value[:3]}...{value[-4:]}"
        ''',
    },
    {
        "id": "env-5",
        "hints": [
            "Loop over the file's lines and decide for each one: skip it, or split it into key and value.",
            "Strip each line; skip blanks, comments and lines without `=`. Remove a leading `export `, split on the first `=` only, then clean the value: unwrap matching quotes, or cut off an inline ` #` comment.",
            "Use `line.split(\"=\", 1)` to split once. For the value: strip it; if it has length >= 2 and starts and ends with the same quote character, return `value[1:-1]`; else if `\" #\"` is in it, keep only the part before it and strip. Store in a dict so later keys overwrite earlier ones.",
        ],
        "title": "Parse a .env file",
        "difficulty": 3,
        "prompt": r'''
            Many projects keep local settings in a `.env` file. You will write a small parser for it
            (the `python-dotenv` library does this, but here you write it yourself with plain Python).

            **Write:** `parse_dotenv(path)`

            - `path`: the file path to read, a string, e.g. `"sample.env"`
            - **Returns:** a `dict` mapping each variable name (string) to its value (string)

            **Rules**
            - Skip blank lines, and lines whose first non-space character is `#` (comments, even indented).
            - Skip lines that contain no `=`.
            - Remove an optional leading `export ` before the name.
            - Split on the **first** `=` only (so `URL=http://x/?a=b` keeps `http://x/?a=b`);
              strip spaces around the key and the value.
            - `EMPTY=` gives the empty string `""`.
            - A value wrapped in matching quotes (`"..."` or `'...'`) is unwrapped and kept exactly
              as written inside the quotes, including `#` and spaces.
            - In an **unquoted** value, ` #` (space + hash) starts a comment: drop it and everything
              after it, then strip.
            - If a key appears twice, the later line wins.
            - Do **not** change `os.environ`, and don't use libraries that you have to install separately.

            **Examples**

            A file `sample.env` containing:
            ```
            # config
            export OPENAI_API_KEY="sk-abc#123"
            MODEL = gpt-4o   # default model
            GREETING='hello world'
            URL=http://x/?a=b
            not a variable line
            EMPTY=
            MODEL=gpt-4o-mini
            ```
            ```python
            parse_dotenv("sample.env")
            # returns {"OPENAI_API_KEY": "sk-abc#123", "MODEL": "gpt-4o-mini",
            #          "GREETING": "hello world", "URL": "http://x/?a=b", "EMPTY": ""}
            ```

            A file with `TEMP = 0.2   # creative` and `NAME="a # b"` gives
            `{"TEMP": "0.2", "NAME": "a # b"}`.
        ''',
        "starter": r'''
            def parse_dotenv(path):
                ...
        ''',
        "setup_files": {
            "sample.env": "# config\n"
                          "export OPENAI_API_KEY=\"sk-abc#123\"\n"
                          "\n"
                          "MODEL = gpt-4o   # default model\n"
                          "   # indented comment\n"
                          "GREETING='hello world'\n"
                          "URL=http://x/?a=b\n"
                          "not a variable line\n"
                          "EMPTY=\n"
                          "MODEL=gpt-4o-mini\n",
        },
        "tests": r'''
            import os
            from solution import parse_dotenv

            def _parse():
                return parse_dotenv("sample.env")

            def test_returns_dict_with_only_variable_lines():
                got = _parse()
                assert isinstance(got, dict), f"got {type(got).__name__}"
                assert set(got) == {"OPENAI_API_KEY", "MODEL", "GREETING", "URL", "EMPTY"}, f"keys: {sorted(got)}"

            def test_export_prefix_removed_and_quotes_unwrapped():
                got = _parse()
                assert got.get("OPENAI_API_KEY") == "sk-abc#123", f"OPENAI_API_KEY -> {got.get('OPENAI_API_KEY')!r}"
                assert got.get("GREETING") == "hello world", f"GREETING -> {got.get('GREETING')!r}"

            def test_splits_on_first_equals_only():
                got = _parse()
                assert got.get("URL") == "http://x/?a=b", f"URL -> {got.get('URL')!r}"

            def test_last_duplicate_wins_and_empty_value_is_empty_string():
                got = _parse()
                assert got.get("MODEL") == "gpt-4o-mini", f"MODEL -> {got.get('MODEL')!r}"
                assert got.get("EMPTY") == "", f"EMPTY -> {got.get('EMPTY')!r}"

            def test_inline_comment_removed_from_unquoted_value():
                with open("b.env", "w") as fh:
                    fh.write("TEMP = 0.2   # creative\nNAME=\"a # b\"\n")
                got = parse_dotenv("b.env")
                assert got == {"TEMP": "0.2", "NAME": "a # b"}, f"got {got!r}"

            def test_does_not_modify_os_environ():
                os.environ.pop("GREETING", None)
                _parse()
                assert "GREETING" not in os.environ, "parse_dotenv must not modify os.environ"
        ''',
        "solution": r'''
            def _clean_value(raw):
                raw = raw.strip()
                if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
                    return raw[1:-1]
                if " #" in raw:
                    raw = raw.split(" #", 1)[0]
                return raw.strip()


            def parse_dotenv(path):
                result = {}
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        if line.startswith("export "):
                            line = line[len("export "):]
                        key, value = line.split("=", 1)
                        result[key.strip()] = _clean_value(value)
                return result
        ''',
    },
    {
        "id": "env-6",
        "hints": [
            "Build one dict of settings from two sources: first the `.env` file's values, then the real environment on top so it wins.",
            "Write a small helper that reads the `.env` file into a dict (skip blanks and comments, remove `export `, split on the first `=`, unwrap quotes; empty dict if the file is missing). Then look each setting up in the real environment first and fall back to the file's dict. A missing or blank key raises `RuntimeError`.",
            "1) Helper: `try` to open the path, loop over lines, `.strip()`, skip empty/`#` lines/lines without `=`, remove a leading `export `, `split(\"=\", 1)`, unwrap matching quotes; `except FileNotFoundError` return `{}`. 2) `key = os.environ.get(\"OPENAI_API_KEY\", file_values.get(\"OPENAI_API_KEY\", \"\")).strip()`. 3) If empty, raise `RuntimeError` naming the variable. 4) Model the same way, with `gpt-4o-mini` as the last fallback. 5) Return the dict with `key[:3] + \"...\" + key[-4:]`.",
        ],
        "title": "Settings loader",
        "difficulty": 3,
        "prompt": r'''
            A real app reads settings from a local `.env` file, but lets the shell environment
            override it (so production can set real values). Build that loader.

            **Write:** `load_settings(path=".env")`

            - `path`: path of the `.env` file, a string (default `".env"`); the file may not exist
            - **Returns:** a dict with exactly two keys: `{"model": <model name>, "key": <masked API key>}`

            **Rules**
            - Read the `.env` file at `path` if it exists. Its format: `KEY=value` lines, `#` comment
              lines, blank lines, an optional `export ` prefix, and optional surrounding quotes
              (`"..."` or `'...'`) around the value, which are removed.
            - If the file does not exist, just use the environment (no error).
            - A variable set in the real environment (`os.environ`) **overrides** the same name in the file.
            - `LLM_MODEL` is optional: if it is in neither place, the model is `"gpt-4o-mini"`.
            - `OPENAI_API_KEY` is required: if it is missing, or empty/only spaces, raise
              `RuntimeError` with a message that contains `OPENAI_API_KEY`.
            - `"key"` is the **masked** key: first 3 characters + `...` + last 4 characters.
              The full key must never appear in the result.
            - Do **not** change `os.environ`.

            **Examples**

            A `.env` file containing:
            ```
            # local dev settings

            export LLM_MODEL="gpt-4o"
            OPENAI_API_KEY='sk-dotenv-key-9f3a'
            ```
            ```python
            load_settings()               # returns {"model": "gpt-4o", "key": "sk-...9f3a"}
            # with OPENAI_API_KEY=sk-from-shell-1234 and LLM_MODEL=o3-mini set in the environment:
            load_settings()               # returns {"model": "o3-mini", "key": "sk-...1234"}
            # no file, OPENAI_API_KEY=sk-only-env-abcd in the environment:
            load_settings("missing.env")  # returns {"model": "gpt-4o-mini", "key": "sk-...abcd"}
            # no file, OPENAI_API_KEY not set:
            load_settings("missing.env")  # raises RuntimeError (message contains "OPENAI_API_KEY")
            ```
        ''',
        "starter": r'''
            import os


            def load_settings(path=".env"):
                ...
        ''',
        "setup_files": {
            ".env": "# local dev settings\n"
                    "\n"
                    "export LLM_MODEL=\"gpt-4o\"\n"
                    "OPENAI_API_KEY='sk-dotenv-key-9f3a'\n",
        },
        "tests": r'''
            import os
            from solution import load_settings

            NAMES = ("LLM_MODEL", "OPENAI_API_KEY")

            def _call(env=None, path=".env"):
                saved = {n: os.environ.pop(n, None) for n in NAMES}
                try:
                    for k, v in (env or {}).items():
                        os.environ[k] = v
                    return load_settings(path)
                finally:
                    for n in NAMES:
                        os.environ.pop(n, None)
                        if saved[n] is not None:
                            os.environ[n] = saved[n]

            def test_reads_model_and_masked_key_from_dotenv():
                got = _call()
                assert got == {"model": "gpt-4o", "key": "sk-...9f3a"}, f"got {got!r}"

            def test_real_environment_overrides_dotenv():
                got = _call({"OPENAI_API_KEY": "sk-from-shell-1234", "LLM_MODEL": "o3-mini"})
                assert got == {"model": "o3-mini", "key": "sk-...1234"}, f"got {got!r}"

            def test_missing_file_uses_default_model():
                got = _call({"OPENAI_API_KEY": "sk-only-env-abcd"}, path="missing.env")
                assert got == {"model": "gpt-4o-mini", "key": "sk-...abcd"}, f"got {got!r}"

            def test_missing_key_raises_runtime_error():
                try:
                    _call(path="missing.env")
                except RuntimeError as exc:
                    assert "OPENAI_API_KEY" in str(exc), f"message was {str(exc)!r}"
                else:
                    raise AssertionError("expected RuntimeError when the key is missing")

            def test_blank_key_raises_runtime_error():
                try:
                    _call({"OPENAI_API_KEY": "  "}, path="missing.env")
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("a blank key should count as missing")

            def test_full_key_never_in_result():
                got = _call()
                assert "dotenv-key" not in str(got), "the full key is in the result"

            def test_does_not_modify_os_environ():
                saved = {n: os.environ.pop(n, None) for n in NAMES}
                try:
                    load_settings(".env")
                    leaked = [n for n in NAMES if n in os.environ]
                    assert not leaked, f"load_settings set {leaked} in os.environ"
                finally:
                    for n in NAMES:
                        os.environ.pop(n, None)
                        if saved[n] is not None:
                            os.environ[n] = saved[n]
        ''',
        "solution": r'''
            import os


            def read_dotenv(path):
                values = {}
                try:
                    with open(path, encoding="utf-8") as fh:
                        for line in fh:
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            if line.startswith("export "):
                                line = line[len("export "):]
                            key, value = line.split("=", 1)
                            value = value.strip()
                            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                                value = value[1:-1]
                            values[key.strip()] = value
                except FileNotFoundError:
                    pass
                return values


            def load_settings(path=".env"):
                file_values = read_dotenv(path)
                key = os.environ.get("OPENAI_API_KEY", file_values.get("OPENAI_API_KEY", "")).strip()
                if not key:
                    raise RuntimeError("OPENAI_API_KEY is not set")
                model = os.environ.get("LLM_MODEL", file_values.get("LLM_MODEL", "")).strip()
                if not model:
                    model = "gpt-4o-mini"
                return {"model": model, "key": f"{key[:3]}...{key[-4:]}"}
        ''',
    },
]
