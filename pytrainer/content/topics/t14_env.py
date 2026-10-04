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
            ## Keeping a secret out of your code

            Your program asks a model for answers through an online service. The service has to know who
            is calling, so it gives you a long secret string, something like `sk-a1b2c3...`. Every call
            that is made with that string goes on your bill.

            That string is called an **API key**. Where do you put it? The obvious place is a line of
            code: `key = "sk-a1b2c3..."`. But code gets shared. You send the file to a colleague, or you
            publish it online. The key travels with every copy, and whoever finds it can make calls that
            you pay for. So the rule is: a secret is never written into the code.

            ```quiz
            You typed your API key into `app.py` and then shared the file. What is the problem?
            - [x] Everyone who gets the file also gets the key :: Right. The key is part of the text of the file, so it goes wherever the file goes, and anyone who has it can make calls that you pay for.
            - [ ] Python refuses to run a file that contains a key :: Python does not know what a key is. To Python it is an ordinary string, and the program runs. That is the danger: nothing warns you.
            - [ ] The key stops working once it is saved in a file :: A key keeps working until you cancel it at the service. That is why a key that has been shared by accident must be replaced.
            ```

            ### A place outside the code

            Your computer hands every program a set of named text values at the moment the program
            starts. One such value is called an **environment variable**, and the whole set is the
            program's **environment**. That is where the key goes. The code only asks for it by name, so
            the code can be shared while the key stays on your computer.

            Settings fit there too. With the model name in an environment variable, the same code can use
            a different model on another computer.

            Python reaches the environment through `os`, a module that comes with Python, as `json` does.
            `os.environ` works like a dict of names and values:

            ```python
            import os

            os.environ["APP_MODE"] = "demo"
            print(os.environ["APP_MODE"])
            # demo
            ```

            Normally a variable is set outside the program, and a later step shows how. The examples in
            this chapter set their own, so that they print the same thing on every computer.

            ### Every value is text

            The environment can hold `3`, but only as the text `"3"`:

            ```python
            import os

            os.environ["PT_RETRIES"] = "3"
            retries = os.environ["PT_RETRIES"]
            print(type(retries))
            # <class 'str'>
            ```

            What happens when you calculate with such a value? Make a guess, then find out:

            ```predict
            import os

            os.environ["PT_WIDTH"] = "40"
            width = os.environ["PT_WIDTH"]
            print(width + width)
            print(int(width) + int(width))
            ---
            `width` is the string `"40"`, so the first `+` joins two strings into `4040`. `int(width)` is the number 40, and `40 + 40` is 80.
            ```

            ### A name that is not set

            The dict tools you know work here too. Square brackets stop the program with a `KeyError`
            when the name is not set. `.get(name, default)` hands back the default instead. And
            `.pop(name, None)` removes a variable, or does nothing when it is not set.

            Type a name that is not set, then compare `d[key]` with `d.get(key)`:

            ```diagram
            {"type":"dict","title":"Lookups in os.environ","name":"os.environ","entries":[["APP_MODE","demo"],["PT_RETRIES","3"]]}
            ```

            **Watch out:** you cannot store a number in the environment. `os.environ["PT_RETRIES"] = 3`
            stops with `TypeError: str expected, not int`. Write `"3"`, with quotes.

            **In short:** an environment variable is a named string that is kept outside your code, and
            `os.environ` reads it like a dict.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
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
            The first line of the program stores the text `"512"` under the name `MAX_TOKENS`. The `pop`
            line makes sure that `PT_MISSING` is not set. `value` is then the string `"512"`, so
            `value + "0"` joins two strings into `5120`. `int(value)` is the number 512, and `512 + 1` is
            `513`. `PT_MISSING` is not set, so `.get` hands back its second argument, the text `none`.
            `print` shows text without the quotes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Ask yourself what type `value` has. The example under \"Every value is text\" in the lesson shows it.",
            "`+` between two strings joins them. After `int()`, the same `+` adds two numbers. And `.get` with two arguments hands back the second one when the name is not set.",
            "Your first line is the text of the variable with one more character joined on at its end. Your second line is a number: the variable as a whole number, plus one. Your third line is the fallback text, the way `print` shows text.",
        ],
    },
    {
        "id": "env-s2",
        "lesson": r'''
            ## A setting that nobody has to set

            Your app can show its screens in a light theme or a dark one, and the choice is read from an
            environment variable. Most people never set it. If the program read it with square brackets,
            it would stop with a `KeyError` on every computer where nobody had made a choice.

            A setting like this should have a sensible value of its own:

            ```python
            import os

            os.environ.pop("PT_THEME", None)
            theme = os.environ.get("PT_THEME", "light")
            print(theme)
            # light
            ```

            `.get` is given two things: the name to look up, and the value to hand back when that name is
            not set. The `pop` line makes sure that nobody has set `PT_THEME`, so the program carries on
            with `light`.

            The value that is used when nobody has chosen one is called a **default value**, or a
            **fallback**. It only steps in when the variable is not set. Make a guess about this program,
            then find out:

            ```predict
            import os

            os.environ["PT_THEME"] = "dark"
            print(os.environ.get("PT_THEME", "light"))
            os.environ.pop("PT_THEME", None)
            print(os.environ.get("PT_THEME", "light"))
            ---
            The first time, the variable is set, so `.get` hands back its value, `dark`, and ignores the default. Then `pop` removes the variable, and the very same line hands back the default, `light`.
            ```

            ### Three ways to read, three results

            You now know three ways to read a variable. They only differ when the name is not set. Pick
            the one that lets this program run:

            ```fill
            import os

            os.environ.pop("PT_LANG", None)
            language = os.environ___
            print("language: " + language)
            ---
            - [x] .get("PT_LANG", "en") :: Right. The name is not set, so `.get` hands back the default `"en"`, and the program prints `language: en`.
            - [ ] ["PT_LANG"] :: Square brackets have no fallback. The name is not set, so the program stops with `KeyError: 'PT_LANG'`.
            - [ ] .get("PT_LANG") :: Without a second argument, `.get` hands back `None` for a name that is not set. The next line cannot join text and `None`, so the program stops with a `TypeError`.
            ```

            Notice that the default is written as a string. A value from the environment is always a
            string, so with a string as the default the rest of your program gets the same type in both
            cases.

            **Watch out:** square brackets are for a variable that must be there. For an optional
            setting they stop the program with a message such as `KeyError: 'PT_THEME'`, which is the
            name of the variable and nothing more.

            **In short:** `os.environ.get(name, default)` hands back the variable when it is set and the
            default when it is not.
        ''',
        "title": "A sensible default",
        "difficulty": 0,
        "prompt": r'''
            Your app sends its requests to a data centre in one region of the world, such as `eu` or `us`.
            The region is chosen with the environment variable `APP_REGION`. Most people never set it, and
            the app should still work for them.

            **Your job:** finish `get_region()` so that it gives back the region to use. The function is
            already written except for one gap, marked `___`. Replace the gap.

            **What goes in**
            - nothing. The function takes no arguments. It reads the environment variable `APP_REGION`.

            **What comes out**
            - a string: the value of `APP_REGION`, or `"eu"` when the variable is not set

            **Rules**
            - When `APP_REGION` is not set, the result is `"eu"`.
            - When `APP_REGION` is set, the result is its value, unchanged.

            **Examples**
            ```python
            # APP_REGION is not set
            get_region()   # returns "eu"

            # APP_REGION is set to us
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
            "Look at the first example in the lesson. What is the job of the second value that `.get` is given?",
            "The gap is the value that the function hands back when nobody has set `APP_REGION`. The task says which region that is.",
            "Put the fallback region from the task in the gap. It is text, so it needs quotes, like every string.",
        ],
    },
    {
        "id": "env-s3",
        "lesson": r'''
            ## Doing maths with a setting

            A model has a setting called the temperature, a number that controls how much variety its
            answers have. You keep it in an environment variable, so that you can change it without
            touching the code. Then your program calculates with it:

            ```python
            import os

            os.environ["PT_TEMPERATURE"] = "0.2"
            raw = os.environ["PT_TEMPERATURE"]
            print(raw + raw)
            # 0.20.2
            ```

            Not 0.4. Every value in the environment is a string, and `+` joins two strings. Nothing warns
            you. The program runs, and the result is wrong.

            In the Data types chapter you turned text into a number with `int()` and `float()`. That type
            conversion is the fix here too:

            ```python
            import os

            os.environ["PT_TEMPERATURE"] = "0.2"
            temperature = float(os.environ["PT_TEMPERATURE"])
            print(temperature + temperature)
            # 0.4
            ```

            ```quiz
            `PT_STEPS` is set to `"12"`. What does `os.environ["PT_STEPS"] + 1` do?
            - [x] It stops the program with a `TypeError` :: Right. The left side is the string `"12"` and the right side is a number. `+` can add two numbers or join two strings, but not one of each: `TypeError: can only concatenate str (not "int") to str`.
            - [ ] It gives `13` :: That needs a number on both sides. The value from the environment is the string `"12"`, so it has to go through `int()` first.
            - [ ] It gives `"121"` :: That is the result of `"12" + "1"`, with two strings. Here the right side is the number `1`, and Python does not turn it into text for you.
            ```

            ### With a default

            An optional setting has a default, as in the last step. Write the default as a string, and
            convert whatever `.get` hands back:

            ```python
            import os

            os.environ.pop("PT_TOP_K", None)
            top_k = int(os.environ.get("PT_TOP_K", "5"))
            print(top_k + 1)
            # 6
            print(type(top_k))
            # <class 'int'>
            ```

            Read that line from the inside out. `.get` hands back a string in both cases: the text of the
            variable, or the default `"5"`. `int()` then converts whichever string it got. So the result
            is an `int` on every computer, whether the variable is set there or not.

            This program forgot the conversion. Repair it:

            ```try
            import os

            os.environ["PT_TEMPERATURE"] = "0.5"
            temperature = os.environ.get("PT_TEMPERATURE", "0.7")
            print(temperature + temperature)
            ---
            The program should add the temperature to itself and print `1.0`. It prints `0.50.5`. Change one line so that `temperature` is a number with a decimal point.
            ---
            import os

            os.environ["PT_TEMPERATURE"] = "0.5"
            temperature = float(os.environ.get("PT_TEMPERATURE", "0.7"))
            print(temperature + temperature)
            ---
            The conversion goes around the whole `.get` call, so it converts the text of the variable and the default alike.
            ```

            **Watch out:** the text must be a number and nothing else. With the variable set to `lots`,
            `int()` stops with `ValueError: invalid literal for int() with base 10: 'lots'`. `int("0.5")`
            fails in the same way. For a number with a decimal point, use `float()`.

            **In short:** a value from the environment is text, so put the read inside `int()` or
            `float()` before you calculate with it.
        ''',
        "title": "Fix the token limit",
        "difficulty": 0,
        "prompt": r'''
            A model stops writing when it reaches its token limit. Your app reads that limit from the
            environment variable `MAX_TOKENS` and calculates with it later, for example to work out how
            many tokens are left. Someone wrote `get_max_tokens()` for this. It has a bug: it gives back
            text, such as `"1024"`, where the rest of the app needs a number.

            **Your job:** find the bug in `get_max_tokens()` and fix it. The code is already in the
            editor, and only one line needs to change.

            **What goes in**
            - nothing. The function takes no arguments. It reads the environment variable `MAX_TOKENS`.

            **What comes out**
            - the token limit as an `int`

            **Rules**
            - When `MAX_TOKENS` is not set, the result is the whole number `256`, not the string `"256"`.
            - When `MAX_TOKENS` is set, for example to `1024`, the result is that number as an `int`:
              `1024`, not `"1024"`.

            **Examples**
            ```python
            # MAX_TOKENS is not set
            get_max_tokens()   # returns 256

            # MAX_TOKENS is set to 1024
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
            "What type does `.get` hand back here, both when the variable is set and when it is not? And what type does the task ask for?",
            "The function reads the right variable and has the right default. What is missing is the step from text to a whole number.",
            "Look at the `PT_TOP_K` example in the lesson. The function that builds a whole number out of text goes around the whole `.get` call, so that it converts the text of the variable and the default alike.",
        ],
    },
    {
        "id": "env-s4",
        "lesson": r'''
            ## Is a value really there?

            Before your app calls a model, it should know whether it has an API key at all. Finding that
            out first is better than a confusing error from the service halfway through the work.

            "Is the key there?" sounds like a question with two answers. In fact a variable can be in
            three states: it is not set, it is set to an empty string, or it is set to some text. The
            middle one happens when someone writes the name into a settings file and leaves the value
            blank. For a key, the first two states mean the same thing: there is no key.

            Your first idea may be `in`, the test from the Dicts chapter that asks whether a name is
            there:

            ```python
            import os

            os.environ["PT_TOKEN"] = ""
            print("PT_TOKEN" in os.environ)
            # True
            ```

            The name is set, so `in` says `True`, and the value is still useless. `in` cannot tell the
            second state from the third.

            ### One default for both empty states

            `.get` with `""` as its default hands back an empty string for a name that is not set. A
            variable that is set to nothing is an empty string already. So after that read, both "no key"
            states look the same:

            ```predict
            import os

            os.environ["PT_TOKEN"] = ""
            print("PT_TOKEN" in os.environ)
            print(os.environ.get("PT_TOKEN", "") == "")
            os.environ.pop("PT_TOKEN", None)
            print("PT_TOKEN" in os.environ)
            print(os.environ.get("PT_TOKEN", "") == "")
            ---
            While the variable is set to an empty string, `in` says `True`, because the name is there. After `pop`, `in` says `False`. But `.get` with `""` as its default hands back an empty string both times, so the comparison is `True` both times.
            ```

            Match each state with what the two tools say about it:

            ```match
            not set :: `.get(name, "")` gives `""`, and `in` says `False`
            set to an empty string :: `.get(name, "")` gives `""`, and `in` says `True`
            set to `abc` :: `.get(name, "")` gives `"abc"`, and `in` says `True`
            ```

            A comparison such as `==` or `!=` is already `True` or `False`. A function can hand that
            result straight back. No `if` is needed.

            ```quiz
            A function has one line in its body: `return os.environ["PT_TOKEN"] != ""`. What happens when `PT_TOKEN` is not set?
            - [x] The program stops with a `KeyError` :: Right. Square brackets stop the program for a name that is not set, before the comparison is ever made.
            - [ ] The function hands back `False` :: That is the answer you would want. But Python reads the variable first, and the square brackets stop the program at that point.
            - [ ] The function hands back `None` :: `None` is what `.get` without a default hands back. Square brackets never give `None` for a name that is not set.
            ```

            **Watch out:** `"PT_TOKEN" in os.environ` is `True` for a variable that is set to nothing. On
            its own it does not tell you that a usable value is there.

            **In short:** read with `.get(name, "")`, and a variable that is not set looks the same as an
            empty one.
        ''',
        "title": "Is the key there?",
        "difficulty": 0,
        "prompt": r'''
            Before your app sends a request to a model, it should know whether it has an API key. Finding
            that out first is better than a confusing error from the service in the middle of the work.

            **Your job:** write `has_api_key()` so that it says whether the environment variable
            `OPENAI_API_KEY` holds a key.

            **What goes in**
            - nothing. The function takes no arguments. It reads the environment variable
              `OPENAI_API_KEY`.

            **What comes out**
            - `True` when the variable holds some text, `False` when there is no key

            **Rules**
            - A variable that is set to text, such as `sk-123`, gives `True`.
            - A variable that is not set gives `False`. The function must not stop with a `KeyError`.
            - A variable that is set to the empty string `""` gives `False` too.
            - The result is `True` or `False` itself, never the key.

            **Examples**
            ```python
            # OPENAI_API_KEY is set to sk-123
            has_api_key()   # returns True

            # OPENAI_API_KEY is not set
            has_api_key()   # returns False

            # OPENAI_API_KEY is set to "" (an empty string)
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
            "Two of the three states mean \"no key\". Which way of reading a variable gives the same result for both of them? The predict box in the lesson shows it.",
            "Read the variable so that a name that is not set comes back as an empty string. After that, one comparison with the empty string answers the question.",
            "The body can be a single line. Read `OPENAI_API_KEY` with the method that takes a default, and give it an empty string as the default. Compare what comes back with an empty string, using the operator that means \"is not equal to\", and hand back the result of that comparison.",
        ],
    },
    {
        "id": "env-s5",
        "lesson": r'''
            ## Setting a variable from outside the program

            Every example so far set a variable and then read it back in the same program. The whole
            point of the environment is that the value comes from outside. So who sets it?

            Usually you do, in a terminal. A **terminal** is a window in which you type commands instead
            of clicking on things. You start a Python file there by typing `python3` and the name of the
            file. A program that is started from a terminal gets a copy of that terminal's environment
            variables.

            ```bash
            export PT_CITY=Lyon
            python3 weather.py
            PT_CITY=Oslo python3 weather.py
            ```

            The `export` line sets `PT_CITY` for every program that is started from this terminal window
            afterwards. The last line sets it for that one run only. In both, there are no spaces around
            the `=`. (This is how macOS and Linux write it. Windows has its own commands for the same
            job.)

            ```match
            `export PT_CITY=Lyon` :: sets the variable for every program started from this terminal afterwards
            `PT_CITY=Oslo python3 weather.py` :: sets the variable for this one run only
            `python3 weather.py` :: starts the script with the variables the terminal already has
            ```

            ### The script that reads it

            `weather.py` is a script, as in the Basics chapter: statements at the left edge, with no
            `def`, run from top to bottom. A script can read the environment directly:

            ```python
            import os

            os.environ["PT_CITY"] = "Lyon"
            city = os.environ.get("PT_CITY", "somewhere")
            print(f"Weather for {city}")
            # Weather for Lyon
            ```

            The Run button cannot type terminal commands, so this copy sets the variable itself, in the
            line under the `import`. The real `weather.py` does not have that line.

            ```quiz
            You type `export PT_CITY=Lyon` in one terminal window. Then you open a second terminal window and start the real `weather.py` there. What does it print?
            - [x] `Weather for somewhere` :: Right. `export` sets the variable in the window where you typed it. The second window has an environment of its own, the variable is not set there, and the script uses its default.
            - [ ] `Weather for Lyon` :: The variable belongs to the window where you typed `export`. A second window does not get it, so the script there finds nothing under that name.
            - [ ] Nothing, the script stops with a `KeyError` :: That would happen with square brackets. This script reads with `.get` and a default, so a variable that is not set is no problem.
            ```

            Put the lines of this script in order. The finished program should print `Level 4 is next`.

            ```order
            import os
            os.environ["PT_LEVEL"] = "3"
            level = int(os.environ.get("PT_LEVEL", "1"))
            print(f"Level {level + 1} is next")
            ---
            A script runs from top to bottom. The module has to be imported before it is used, the variable has to be set before it is read, and `level` has to exist before the `print` uses it.
            ```

            When a program ends, it reports one whole number to the terminal. That number is called the
            **exit code**. `0` means that the program ran to its last line, and `1` means that an error
            stopped it.

            **Watch out:** a script that reads an optional variable with square brackets stops with a
            `KeyError` when the variable is not set, and its exit code is then 1.

            **In short:** the terminal sets the variable, and the script reads it with `os.environ`.
        ''',
        "title": "Greeting script",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A command-line tool greets the person who runs it. It finds out who that is from the
            environment variable `USER_NAME`.

            **Your job:** write a script that reads `USER_NAME` and prints one line that greets that
            person. A script has no function: the statements start at the left edge. The `import os` line
            is already in the editor.

            **What goes in**
            - the environment variable `USER_NAME`, for example `Ada`. It may not be set.

            **What comes out**
            - one printed line: `Hello, Ada!` for the example value

            **Rules**
            - The line is the word `Hello`, a comma, one space, the name, and an exclamation mark, with
              nothing between the name and the `!`.
            - When `USER_NAME` is not set, the name is `stranger`.
            - The script prints nothing else.
            - The script runs to its end without an error, so that its exit code is 0. A check looks at
              the exit code.

            **Examples**

            Started with `USER_NAME=Ada python3 solution.py`, the script prints:
            ```text
            Hello, Ada!
            ```

            Started with `python3 solution.py`, with `USER_NAME` not set, it prints:
            ```text
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
            "This is the pattern from step 2 of this chapter: read a variable, with a fallback for when nobody has set it.",
            "Two statements are enough. The first stores the name, or the fallback word from the task, under a variable. The second prints the greeting with that variable in it.",
            "Under the `import` line, read `USER_NAME` with the method that takes a default, give it the fallback word from the task as the default, and store the result under a name of your choice. Then print an f-string: the greeting word, a comma, a space, your variable in curly braces, and the exclamation mark.",
        ],
    },
    {
        "id": "env-s6",
        "lesson": r'''
            ## A switch that is on or off

            While you hunt for a bug, you want your app to print extra details. Once the bug is found,
            you want it quiet again. That is a setting with two positions, on and off, and it suits an
            environment variable well: you flip it in the terminal and leave the code alone.

            In Python, on and off are `True` and `False`. But the environment holds text. How do you get
            from the text `false` to the bool `False`? The obvious tool is `bool()`, the conversion for
            that type. Make a guess, then find out:

            ```predict
            import os

            os.environ["PT_VERBOSE"] = "false"
            value = os.environ["PT_VERBOSE"]
            print(bool(value))
            print(bool("0"))
            print(bool(""))
            ---
            `bool()` does not read the word. It only asks whether the string is empty. `"false"` and `"0"` contain characters, so they are truthy and give `True`. Only the empty string gives `False`.
            ```

            So `bool()` is the wrong tool here. With it, `false`, `no` and `off` would all turn the
            switch on. Compare the text with the one word that means "on" instead:

            ```python
            import os

            os.environ["PT_VERBOSE"] = "false"
            value = os.environ["PT_VERBOSE"]
            print(value == "true")
            # False
            ```

            A setting that turns one behaviour on or off is called a **flag**.

            ### Capital letters

            One problem is left. People type `True` or `TRUE`, and to Python those are different strings
            from `true`. In the Strings chapter you met `.lower()`, which hands back a copy of a string in
            small letters. Call it before you compare:

            ```python
            print("TRUE" == "true")
            # False
            print("TRUE".lower() == "true")
            # True
            ```

            ```fill
            import os

            os.environ["PT_COLOR"] = "Yes"
            use_color = os.environ.get("PT_COLOR", "")___
            print(use_color)
            ---
            - [x] .lower() == "yes" :: Right. `"Yes".lower()` is `"yes"`, the comparison is true, and `use_color` is the bool `True`.
            - [ ] == "yes" :: Without `.lower()`, `"Yes"` and `"yes"` are different strings, so this prints `False` although the switch is on.
            - [ ] .lower() :: That only changes the letters. `use_color` would be the string `yes`, not a bool.
            ```

            **Watch out:** give `.get` an empty string as its default. Without a default, `.get` hands
            back `None` for a name that is not set, and calling `.lower()` on `None` stops the program with
            `AttributeError: 'NoneType' object has no attribute 'lower'`.

            **In short:** never use `bool()` on text from the environment. Make it small letters and
            compare it with the word that means "on".
        ''',
        "title": "Debug switch",
        "difficulty": 0,
        "prompt": r'''
            While you look for a bug, you want your app to print extra details. The switch for that is
            the environment variable `DEBUG`: the word `true` turns the details on, and anything else
            leaves them off. Someone wrote `debug_enabled()` to read the switch. It has a bug: it says
            "on" for almost every value, even for `false`.

            **Your job:** find the bug in `debug_enabled()` and fix it. The code is already in the
            editor, and only one line needs to change.

            **What goes in**
            - nothing. The function takes no arguments. It reads the environment variable `DEBUG`.

            **What comes out**
            - `True` when the switch is on, `False` when it is off

            **Rules**
            - The switch is on only when `DEBUG` is the word `true`. Capital letters make no difference:
              `true`, `True` and `TRUE` all give `True`.
            - Every other text gives `False`. The checks try `false`, `no` and the empty string.
            - When `DEBUG` is not set, the result is `False`. The function must not stop with an error.
            - The result is `True` or `False` itself, not a string.

            **Examples**
            ```python
            # DEBUG is set to TRUE
            debug_enabled()   # returns True

            # DEBUG is set to false
            debug_enabled()   # returns False

            # DEBUG is not set
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
            "What does `bool()` give for the text `false`? The predict box in the lesson shows it.",
            "`bool()` only asks whether a string is empty. The task asks something else: whether the text is one particular word, in any mix of capital and small letters.",
            "Keep the `.get` call with its empty default, and take `bool()` away from around it. Turn the text into small letters with the method from the lesson, then compare it with the word that switches the details on. That comparison is already `True` or `False`, so hand it back.",
        ],
    },
    {
        "id": "env-1",
        "lesson": r'''
            ## A fresh look at the variable on every call

            Your app reads a setting from the environment, and you decide to store it in a constant at the
            top of the file, as in the Variables chapter. It looks tidy. Then the variable changes while
            the program is running, and the constant does not notice:

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

            `SAVED` was given the string `"red"` when its line ran. That string is not connected to the
            environment any more, so changing the variable later does not change `SAVED`. The function is
            different. Its body runs at every call, so every call looks the variable up again, and this
            one finds `blue`.

            `os.getenv(name, default)` in the body is a shorter way to write
            `os.environ.get(name, default)`. The two do the same thing.

            Press Next and watch `SAVED` stay `'red'` after line 9 has changed the variable:

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

            Statements at the left edge of a file run once, when the file is loaded. That moment is called
            **import time**, because the same thing happens when another file imports yours. The body of
            a function runs each time the function is called.

            ```predict
            import os

            def current_lang():
                return os.getenv("PT_LANG", "en")

            os.environ["PT_LANG"] = "fr"
            print(current_lang())
            os.environ["PT_LANG"] = "de"
            print(current_lang())
            os.environ.pop("PT_LANG", None)
            print(current_lang())
            ---
            Each call reads the variable again. The first call finds `fr` and the second finds `de`. Then `pop` removes the variable, and the third call falls back on the default, `en`.
            ```

            This matters whenever a setting can change while the program runs. It matters for the checks
            of this step too: they set the variable, call your function, set it to something else and
            call again.

            ```quiz
            A file holds the lines below. Later, while the program runs, `PT_MODE` is changed to `fast`. What does `mode()` hand back after that?

            ~~~python
            import os

            os.environ["PT_MODE"] = "slow"
            MODE = os.getenv("PT_MODE", "slow")

            def mode():
                return MODE
            ~~~
            - [x] `"slow"` :: Right. The environment was read once, in the line at the left edge, and the string `"slow"` was stored under `MODE`. The function only hands back that stored string.
            - [ ] `"fast"` :: The call comes after the change, but the body of the function never looks at the environment. It hands back `MODE`, which was filled in once, when the file was loaded.
            - [ ] Nothing, it stops with a `NameError` :: A function may read a name that is defined at the left edge of its file, so `MODE` is found. The trouble is the old value in it.
            ```

            **Watch out:** a file that uses `os` needs `import os` at its top. Without that line the
            program stops with `NameError: name 'os' is not defined. Did you forget to import 'os'?`

            **In short:** read an environment variable inside the function that needs it, and every call
            gets the current value.
        ''',
        "research": {"note": "Skim the official docs for `os.environ` and `os.getenv` - note what each returns for a missing name.",
         "links": [{"title": "os.environ - Python docs", "url": "https://docs.python.org/3/library/os.html#os.environ"},
                   {"title": "os.getenv - Python docs", "url": "https://docs.python.org/3/library/os.html#os.getenv"}]},
        "hints": [
            "Where does the line that reads the variable have to be, so that it runs again at every call? The first example in the lesson shows both places.",
            "The read belongs in the body of the function, not at the left edge of the file. It needs a fallback for when nobody has set the variable.",
            "First make `os` available with an import line at the top of the file. In the body of the function, read `LLM_MODEL` with `os.getenv` or with `os.environ.get`, give it the fallback model name from the task as the default, and hand back what comes out.",
        ],
        "title": "Model from the environment",
        "difficulty": 1,
        "prompt": r'''
            An app that talks to a model should let you switch to another model without editing the code.
            So the name of the model comes from the environment variable `LLM_MODEL`, with a fallback for
            when nobody has chosen one.

            **Your job:** write `get_model()` so that it gives back the name of the model to use. The
            editor holds only the empty function. Anything else that the file needs, such as an import,
            you add yourself.

            **What goes in**
            - nothing. The function takes no arguments. It reads the environment variable `LLM_MODEL`.

            **What comes out**
            - a string: the value of `LLM_MODEL`, or `"gpt-4o-mini"` when the variable is not set

            **Rules**
            - When `LLM_MODEL` is not set, the result is `"gpt-4o-mini"`. The function must not stop with
              a `KeyError`.
            - When `LLM_MODEL` is set, the result is its value, unchanged.
            - The variable is read at every call, not once when the file is loaded. A check sets
              `LLM_MODEL` to `model-a`, calls the function, sets it to `model-b` and calls again. The two
              calls must give `"model-a"` and then `"model-b"`.

            **Examples**
            ```python
            # LLM_MODEL is not set
            get_model()   # returns "gpt-4o-mini"

            # LLM_MODEL is set to claude-sonnet
            get_model()   # returns "claude-sonnet"

            # LLM_MODEL is set to model-a, and changed to model-b after the first call
            get_model()   # returns "model-a"
            get_model()   # returns "model-b"
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
            ## A setting the program cannot run without

            Some settings have no sensible default. Without an API key, no call to a model can work. If
            your program carries on anyway, it fails much later, deep inside the call, with a message from
            the service that does not say what is wrong on your side. It is kinder to check at the start,
            and to stop with a message that says exactly which setting is missing.

            What counts as missing? You know two cases from step 4: not set, and empty. There is a third.
            A value that is only spaces, as happens when a key is copied badly, is as useless as an empty
            one. Programmers call such a value **blank**.

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

            `.strip()` hands back the string without the spaces at its ends, as in the Strings chapter, so
            a blank value becomes `""`. An empty string is falsy, so `not port.strip()` is `True`. With
            `""` as the default of `.get`, that one test covers all three cases.

            ```predict
            import os

            os.environ["PT_A"] = "  x  "
            os.environ["PT_B"] = "  "
            os.environ.pop("PT_C", None)
            print(not os.environ.get("PT_A", "").strip())
            print(not os.environ.get("PT_B", "").strip())
            print(not os.environ.get("PT_C", "").strip())
            ---
            `PT_A` still has an `x` after stripping, so it is truthy and `not` gives `False`. `PT_B` is blank: nothing is left after stripping, and `not ""` is `True`. `PT_C` is not set, so `.get` hands back `""`, and the result is `True` as well.
            ```

            ### Stopping with a clear message

            In the Errors chapter you stopped a function with `raise` when its input was bad. Do the same
            here. `RuntimeError` is the usual exception type for a program that is not set up correctly.

            ```python
            import os

            os.environ["PT_PORT"] = "   "
            port = os.environ.get("PT_PORT", "")
            try:
                if not port.strip():
                    raise RuntimeError("PT_PORT must be set")
            except RuntimeError as exc:
                print("stopped:", exc)
            # stopped: PT_PORT must be set
            ```

            The message contains the name of the variable. The person who reads it then knows exactly
            what to set. A message such as `a setting is missing` would leave them searching.

            ```fill
            import os

            os.environ["PT_HOST"] = "  "
            host = os.environ.get("PT_HOST", "")
            try:
                if ___:
                    raise RuntimeError("PT_HOST must be set")
                print("host is", host)
            except RuntimeError as exc:
                print("stopped:", exc)
            ---
            - [x] not host.strip() :: Right. The two spaces are stripped away, an empty string is left, and `not` turns that falsy value into `True`. The program prints `stopped: PT_HOST must be set`.
            - [ ] not host :: `host` is a string of two spaces. It is not empty, so it is truthy, and the test lets the blank value through.
            - [ ] host == "" :: Two spaces are not the same string as an empty one, so the test lets the blank value through.
            ```

            **Watch out:** do not read a required variable with square brackets and leave it at that.
            They stop the program with `KeyError: 'PT_PORT'` when the variable is not set, which names the
            variable but does not say what to do. And they let an empty or a blank value through without
            any error.

            **In short:** check a required variable at the start, and `raise RuntimeError` with its name
            when it is not set, empty or blank.
        ''',
        "hints": [
            "The lesson has two pieces: one test that is true for a variable that is not set, empty or blank, and `raise` to stop with a message. This function needs both.",
            "Read the variable in a way that never stops the program, with an empty string as the fallback. Then decide yourself: when nothing is left after the spaces are stripped away, raise the error. Otherwise hand the text back.",
            "Import `os` at the top. In the function, read the variable whose name is in `name` with the method that takes a default, and store the text. Test whether the text is empty once the spaces at its ends are stripped away. Under that test, raise a `RuntimeError` whose message is an f-string with `name` in it. After the `if`, hand back the text you stored.",
        ],
        "title": "Required variable",
        "difficulty": 1,
        "prompt": r'''
            Some settings have no sensible default. Without an API key, for example, no call to a model
            can work. An app should notice that at the start and stop with a message that names the
            missing variable, instead of failing later in a confusing way.

            **Your job:** write `require_env(name)` so that it gives back the value of a required
            environment variable, or stops with a clear error when there is no usable value. The editor
            holds only the empty function. Anything else that the file needs, such as an import, you add
            yourself.

            **What goes in**
            - `name`: the name of an environment variable, as a string, for example `"OPENAI_API_KEY"`

            **What comes out**
            - the text stored in that variable, exactly as it is: `"sk-123"` when the variable is set to
              `sk-123`

            **Rules**
            - When the variable is set to some text, the result is that text.
            - When the variable is not set, the function raises `RuntimeError`. A `KeyError` does not pass
              the check.
            - When the variable is empty or holds only spaces, such as `"   "`, the function raises
              `RuntimeError` as well.
            - The message of the error contains the name of the variable, for example
              `Missing required environment variable: OPENAI_API_KEY`. The wording around the name is up
              to you.

            **Examples**
            ```python
            # PT_API_KEY is set to sk-123
            require_env("PT_API_KEY")       # returns "sk-123"

            # OPENAI_API_KEY is not set
            require_env("OPENAI_API_KEY")   # raises RuntimeError: Missing required environment variable: OPENAI_API_KEY

            # PT_EMPTY is set to "   " (three spaces)
            require_env("PT_EMPTY")         # raises RuntimeError, and the message contains PT_EMPTY
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
            ## All the settings in one place

            An app grows. Soon five files each read their own environment variable, each with its own
            default and its own conversion. To find out which settings the app has, you would have to
            search all of the code. And when two files give the same variable two different defaults, the
            app disagrees with itself.

            It is better to read everything in one place and to keep the results together in a dict:

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

            Each entry is the pattern from step 3: `.get` with a default that is written as a string,
            inside the conversion for the type you want. `PT_RETRIES` is set, so `"retries"` is 5.
            `PT_TIMEOUT` is not set, so `.get` hands back `"30"`, and `float("30")` is `30.0`.

            A dict like this is called a **config dict**. "Config" is short for configuration: the
            settings that a program runs with. The rest of the app reads `config["retries"]` and gets a
            number. It never touches `os.environ` itself, and all the defaults can be read in one glance.

            A setting that is text needs no conversion. Make a guess about this one:

            ```predict
            import os

            os.environ["PT_RATE"] = "2"
            os.environ.pop("PT_LABEL", None)
            config = {
                "rate": float(os.environ.get("PT_RATE", "1.5")),
                "label": os.environ.get("PT_LABEL", "draft"),
            }
            print(config["rate"])
            print(config["label"])
            ---
            `PT_RATE` is set to the text `2`, and `float("2")` is `2.0`: Python always shows a float with a decimal point. `PT_LABEL` is not set, so the entry is the default `draft`, which is text already.
            ```

            ```fill
            import os

            os.environ.pop("PT_BATCH", None)
            config = {"batch": ___}
            print(config["batch"] + 1)
            ---
            - [x] int(os.environ.get("PT_BATCH", "8")) :: Right. `.get` hands back the default `"8"`, `int()` makes it the number 8, and the program prints `9`.
            - [ ] os.environ.get("PT_BATCH", "8") :: Without the conversion the entry is the string `"8"`, and `+` cannot join a string and a number. The program stops with a `TypeError`.
            - [ ] int(os.environ["PT_BATCH"]) :: The variable is not set, so the square brackets stop the program with `KeyError: 'PT_BATCH'` before `int()` is given anything.
            ```

            Remember the step before last: a read at the left edge of a file happens once. Build the dict
            inside a function, and every call reads the environment as it is at that moment.

            **Watch out:** convert every entry that is a number, also when it has a default.
            `os.environ.get("PT_RETRIES", 3)` without `int()` gives the number `3` on your computer and
            the string `"5"` on a computer where the variable is set. No error tells you about it.

            **In short:** build one dict of settings with the conversions inside it, and let the rest of
            the program read the dict.
        ''',
        "title": "Model settings dict",
        "difficulty": 1,
        "prompt": r'''
            An app that calls a model has several settings: which model to use, how much variety its
            answers may have (the temperature), and how many tokens it may write. Each one can be changed
            through an environment variable. The app wants them together in one dict, with the defaults
            filled in and the numbers already converted.

            **Your job:** write `load_config()` so that it gives back that dict.

            **What goes in**
            - nothing. The function takes no arguments. It reads three environment variables, and each of
              them may not be set.

            **What comes out**
            - a dict with exactly these three keys:

            | key | environment variable | type of the value | default |
            | --- | --- | --- | --- |
            | `"model"` | `LLM_MODEL` | `str` | `"gpt-4o-mini"` |
            | `"temperature"` | `LLM_TEMPERATURE` | `float` | `0.7` |
            | `"max_tokens"` | `LLM_MAX_TOKENS` | `int` | `256` |

            **Rules**
            - A variable that is not set gets its default from the table.
            - `"temperature"` is always a `float` and `"max_tokens"` is always an `int`, whether the value
              came from the environment or from the default. With `LLM_TEMPERATURE` set to `0` or `1`,
              the value in the dict is `0.0` or `1.0`.
            - The variables are read at every call. A check changes `LLM_MODEL` between two calls and
              expects the second call to give the new value.

            **Examples**
            ```python
            # none of the three variables is set
            load_config()   # returns {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}

            # LLM_MODEL is set to o3-mini, LLM_TEMPERATURE to 0, LLM_MAX_TOKENS to 1024
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
            "Each entry of the dict is one read with a default. Which entries also need a conversion? Look at the first example in the lesson.",
            "Write each default as a string, and put the conversion around the whole read. Then the type is right in both cases. The model name is text already and needs no conversion.",
            "Hand back a dict with the three keys from the table. Each value is a `.get` read of the variable in that row, with the default of that row written as a string. Put the float conversion around the read for the temperature, and the int conversion around the read for the token limit. Build the dict inside the function, so that every call reads the environment again.",
        ],
    },
    {
        "id": "env-8",
        "lesson": r'''
            ## Cutting a KEY=value line in two

            Your app needs an API key, a model name and a few more settings. Typing an `export` line for each of them in every new terminal window gets tiring. So many projects write the settings down once, in a plain text file, with one setting on each line:

            ```text
            OPENAI_API_KEY=sk-abc123
            LLM_MODEL=gpt-4o
            ```

            Each line is a name, an equals sign and a value. The program opens the file when it starts and sets itself up from it. Such a file is called a **`.env` file**, said "dot env". The dot at the start is part of its name.

            The file holds secrets, so it stays on your computer. Code is usually shared with a tool called git, which keeps a history of every change to your files. A `.env` file is kept out of git, so the code can travel and the keys do not.

            To use a line, the program has to cut it into the name and the value. `split` cuts a string at a separator and hands back a list of pieces. Two names on the left of `=` can take the two pieces:

            ```python
            line = "LLM_TEMP=0.2"
            pieces = line.split("=")
            print(pieces)
            # ['LLM_TEMP', '0.2']
            name, value = pieces
            print(name)
            # LLM_TEMP
            ```

            A value can contain an `=` of its own. A web address often does:

            ```python
            line = "DB_URL=postgres://host/db?sslmode=require"
            print(line.split("="))
            # ['DB_URL', 'postgres://host/db?sslmode', 'require']
            ```

            Three pieces: the value was cut in two. `split` accepts a second value after the separator, which is the most cuts it may make. Use it to keep the address in one piece:

            ```try
            line = "DB_URL=postgres://host/db?sslmode=require"
            print(line.split("="))
            ---
            Change the `print` line so that the program prints a list of two items: the name, and the whole address after the first `=`.
            ---
            line = "DB_URL=postgres://host/db?sslmode=require"
            print(line.split("=", 1))
            ---
            With a limit of 1, `split` makes one cut, at the first `=`, and keeps everything after it together.
            ```

            ### Spaces and the newline

            People put spaces around the `=` to make a file easier to read. And a line that is read from a file ends with a newline, the invisible character `\n` that ends the line. All of that stays in the pieces:

            ```python
            line = " MODE = fast \n"
            print(line.split("=", 1))
            # [' MODE ', ' fast \n']
            ```

            `.strip()` removes spaces and newlines from both ends of a string. Predict what this prints:

            ```predict
            line = "  PT_SIZE =  large  \n"
            left, right = line.split("=", 1)
            print("[" + left.strip() + "]")
            print("[" + right.strip() + "]")
            ---
            `split` cut the line once, at the `=`. Each half still had spaces at its ends, and the right half also had the newline. `strip` removed all of them, so the brackets sit right against the text. Spaces in the middle of a piece would have stayed.
            ```

            ### A line with no equals sign

            A line that has no `=` at all, such as a note or a typo, gives `split` nothing to cut. It hands back a list with one piece, and two names cannot share one piece.

            ```quiz
            What happens when this program runs?

            ~~~python
            line = "just some notes"
            name, value = line.split("=", 1)
            print(name)
            ~~~
            - [x] It stops with `ValueError: not enough values to unpack (expected 2, got 1)` :: Right. `split` hands back a list with one item, and `name, value =` needs two. Python stops at that line, before the `print`.
            - [ ] It prints `just some notes` :: The `print` is never reached. Python stops at the line before it, because one piece cannot fill two names.
            - [ ] It prints an empty line :: Python does not invent a missing piece. It does not fill `value` with an empty string, it stops with an error.
            - [ ] It stops with a `KeyError` :: `KeyError` belongs to a dict that is asked for a key it does not have. Nothing is looked up in a dict here, and the error is a `ValueError`.
            ```

            A `ValueError` is also what you raise yourself, as in the Errors chapter, when a text is not in the shape that a function expects.

            **Watch out:** cut at every `=` and unpack into two names, and a value that contains an `=` stops the program with `ValueError: too many values to unpack (expected 2, got 3)`.

            **In short:** cut a `NAME=value` line once, at the first `=`, and strip both halves.
        ''',
        "research": {"note": "Read the `str.split` documentation and find how to limit the number of splits, then come back.",
         "links": [{"title": "str.split - Python docs", "url": "https://docs.python.org/3/library/stdtypes.html#str.split"}]},
        "title": "Parse one .env line",
        "difficulty": 1,
        "prompt": r'''
            A `.env` file is a list of settings, one on each line, written as a name, an equals sign and a value. A program that reads such a file has to cut every line in two. This step builds that one piece. A later step reads a whole file.

            **Your job:** write `parse_env_line(line)`, which cuts one line into its name and its value and gives both back.

            **What goes in**
            - `line`: one line of a `.env` file, as a string, for example `"LLM_MODEL=gpt-4o"`. The line can have spaces around its parts, and it can end with a newline (`"\n"`, the invisible character that ends a line).

            **What comes out**
            - a tuple of two strings: `(name, value)`. For the example line it is `("LLM_MODEL", "gpt-4o")`.

            **Rules**
            - The line is cut at the first `=` only. Everything after it is the value, even when the value contains more `=` signs.
            - Spaces and the newline at the ends of the name and of the value are removed.
            - A line that ends right after the `=` has an empty value: `"EMPTY="` gives `("EMPTY", "")`.
            - A line that has no `=` at all raises `ValueError`. The message is up to you.

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
            "Think about the third example: its value contains an `=`. Which option of `split` did the lesson use to keep such a value in one piece?",
            "Cut the line once, at the first `=`, into two pieces. Then clean each piece with the method that removes spaces and newlines from both ends. A line with no `=` cannot be cut into two pieces, and the task says what must happen then.",
            "First deal with the line that has no `=`: either test for it before you cut and raise `ValueError` with a message of your own, or let the unpacking raise it. Then cut the line once at `=`, so that the name and the value are two separate names. Strip both, and hand them back together as a tuple.",
        ],
    },
    {
        "id": "env-3",
        "hints": [
            "Both functions start the same way. Look at the lesson \"A setting the program cannot run without\": one test covers a variable that is not set, empty or only spaces.",
            "Read the variable as text with an empty string as the fallback, strip it, and give the default when nothing is left. For `env_int`, the conversion to a number is the step that can fail, so catch that error and raise a new one that names the variable. For `env_bool`, make the text lower case first, so that every spelling is one case, and compare it with a group of words for yes and a group of words for no.",
            "For `env_int`, in order: read the text and strip it; if it is empty, hand back the default; try the conversion to a whole number and hand the number back; when the conversion fails, raise a `ValueError` with an f-string message that has `name` in it. For `env_bool`, in order: read, strip and lower-case the text; if it is empty, hand back the default; if it is in the group of yes words, hand back `True`; if it is in the group of no words, hand back `False`; for anything else, raise a `ValueError` with `name` in the message. A set is a good home for each group of words.",
        ],
        "title": "Typed settings",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A value from the environment is always text. An app needs whole numbers, such as a token limit, and on/off switches, such as "stream the answer". Instead of converting in every place that reads a setting, you write two small readers: one for numbers and one for switches. Each of them also decides what happens when the value is missing or makes no sense.

            **Your job:** write two functions in the same file. `env_int(name, default)` reads a variable as a whole number. `env_bool(name, default)` reads a variable as `True` or `False`.

            **What goes in** (for both functions)
            - `name`: the name of an environment variable, as a string, for example `"MAX_TOKENS"`
            - `default`: what to use when the variable has no value. It is a whole number for `env_int` and `True` or `False` for `env_bool`.

            **What comes out**
            - `env_int`: an `int`, for example `512`
            - `env_bool`: `True` or `False` themselves, never a string

            **Rules for both functions**
            - A variable that is not set gives `default`. A variable that is set to the empty string gives `default` too.
            - Spaces around the value are ignored.
            - An error is a `ValueError` whose message contains `name`, so that whoever reads it knows which setting is wrong.

            **Rules for `env_int`**
            - The value is converted to a whole number: `" 512 "` gives `512`.
            - A value that is not a whole number, such as `"three"`, raises the `ValueError`.

            **Rules for `env_bool`**
            - The words `1`, `true`, `yes` and `on` give `True`. The words `0`, `false`, `no` and `off` give `False`.
            - Capital letters make no difference: `TRUE` and `False` work, and `" OFF "` gives `False`.
            - Any other text, such as `"maybe"`, raises the `ValueError`.

            **Examples**
            ```python
            # MAX_TOKENS is set to " 512 ", STREAM to False, RETRIES to three,
            # VERBOSE to maybe, and DEBUG is not set
            env_int("MAX_TOKENS", 256)   # returns 512
            env_int("RETRIES", 3)        # raises ValueError, the message contains "RETRIES"
            env_bool("STREAM", True)     # returns False
            env_bool("DEBUG", False)     # returns False   (not set, so the default)
            env_bool("VERBOSE", True)    # raises ValueError, the message contains "VERBOSE"
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
            "The function has three cases. Which two can you settle first, before you cut the text into parts?",
            "Settle the two special cases at the top: nothing there at all, and too short. For everything else, take a slice from the start of the text and a slice from the end, and put the three dots between them. The slicing from the Lists chapter works on strings too, including counting from the end.",
            "In order: if there is no text (`None` and the empty string are both falsy), hand back the empty string; if the length is 8 or less, hand back the four stars; otherwise build one f-string. Its first part is the slice that starts at the beginning and stops before position 3. Its last part is the slice that starts 4 places from the end and runs to the end of the text. Put three dots between them.",
        ],
        "title": "Mask a secret",
        "difficulty": 2,
        "prompt": r'''
            Sometimes a program has to show a secret in a log or in an error message, so that a person can tell which key was used. It must never show the whole secret. A common way is to show the first few characters and the last few, and to hide everything in between.

            **Your job:** write `mask_secret(value)`, which gives back a version of a secret with the middle hidden.

            **What goes in**
            - `value`: a secret as a string, for example `"sk-proj-a1b2c3d4e5f6abcd"`, or `None` when there is no secret

            **What comes out**
            - a string. For the example above it is `"sk-...abcd"`.

            **Rules**
            - `None` and the empty string give the empty string.
            - A secret of 8 characters or fewer gives the four stars `"****"`. Showing 3 characters at the front and 4 at the back would reveal almost all of a short secret.
            - A longer secret gives its first 3 characters, then three dots, then its last 4 characters. Nothing from the middle appears in the result.

            **Examples**
            ```python
            mask_secret("sk-proj-a1b2c3d4e5f6abcd")   # returns "sk-...abcd"
            mask_secret("abc123456")                  # returns "abc...3456"   (9 characters)
            mask_secret("12345678")                   # returns "****"         (8 characters)
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
            "Treat the file as a loop over its lines. For each line you decide one of two things: skip it, or turn it into one entry of the dict. Which rules in the task are about skipping and which are about the entry?",
            "Strip each line first. Skip the lines that the rules name. Remove a leading `export `, cut once at the first `=`, and clean the value. Check for quotes before you look for a comment, because a `#` inside quotes belongs to the value. A dict assigns later keys over earlier ones, which gives you \"the later line wins\" for free.",
            "Write a small helper that cleans one value, in order: strip it; if it has at least two characters and its first and last character are the same quote mark, hand back what is between them; otherwise, if a space followed by `#` appears in it, keep only the part before that and strip it; hand back the result. In the main function, open the file, go through its lines, strip each one, skip the blank ones, the comment ones and the ones without `=`, remove a leading `export `, cut once at the first `=`, strip the name, clean the value with the helper, and store it in a dict under the name. Hand the dict back at the end.",
        ],
        "title": "Parse a .env file",
        "difficulty": 3,
        "prompt": r'''
            A `.env` file holds a project's settings, one `NAME=value` on each line. Real files are messier than the single lines you cut in an earlier step: they have comments, blank lines, quotes and sometimes the word `export`. A library named `python-dotenv` reads such files. Here you write the reader yourself, with plain Python only.

            **Your job:** write `parse_dotenv(path)`, which reads a `.env` file and gives back its settings in a dict.

            **What goes in**
            - `path`: the path of the file to read, as a string, for example `"sample.env"`. The file exists.

            **What comes out**
            - a dict. Each name is a key (a string) and each value is the text for it (a string).

            **Rules**
            - Lines to skip: blank lines, comment lines, and lines that have no `=`. A comment line is a line whose first character that is not a space is `#`, even when the line is indented.
            - An optional `export ` at the start of a line is removed before the name.
            - Each line is cut at the first `=` only, so `URL=http://x/?a=b` keeps its whole value. Spaces around the name and around the value are removed.
            - `EMPTY=` gives the empty string.
            - A value that starts and ends with the same kind of quote mark (`"` or `'`) loses the quotes. What is inside is kept exactly as written, with any `#` and any spaces.
            - A value without quotes can end in a comment: a space followed by `#` starts the comment. Drop it and everything after it, then remove the spaces at the end.
            - When a name appears twice, the later line wins.
            - The function does not change `os.environ`, and it uses nothing that has to be installed.

            **Examples**

            A file `sample.env` with this content:
            ```text
            # config
            export OPENAI_API_KEY="sk-abc#123"

            MODEL = gpt-4o   # default model
               # indented comment
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

            A file with the two lines `TEMP = 0.2   # creative` and `NAME="a # b"` gives
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
            "Think of two sources of settings: the file and the real environment. The environment is looked at first, and the file only fills in what the environment does not have. The step \"Parse a .env file\" has the reader that you need for the file.",
            "Write a helper that turns the file into a dict, with an empty dict when the file does not exist. Then, for each setting, look in the real environment first and fall back to the file's dict. After that comes the check for a missing or blank key, the default for the model, and the hiding of the key.",
            "In order: the helper opens the path inside a `try` and goes through the lines, skipping the ones the rules name, removing `export `, cutting once at the first `=`, unwrapping quotes and storing the pair in a dict; when the file is not found, it hands back an empty dict. Then read the key from the environment with the file's value as the fallback, and strip it. If nothing is left, raise `RuntimeError` with the variable's name in the message. Read the model the same way, and use `gpt-4o-mini` when nothing is left. Hand back a dict with the model and the key, where the key is built from its first 3 characters, three dots and its last 4 characters.",
        ],
        "title": "Settings loader",
        "difficulty": 3,
        "prompt": r'''
            On your own computer, an app reads its settings from a local `.env` file. On a server, the people who run it set real environment variables instead. When a name is in both places, the real environment must win, because that is how a server overrides a file without anyone editing it. You build the loader that does this, and that never exposes the full key.

            **Your job:** write `load_settings(path=".env")`, which gathers the model name and the API key from the file and the environment and gives them back in a dict. You wrote the pieces in earlier steps, reading a `.env` file and hiding a secret. Write them again inside this file.

            **What goes in**
            - `path`: the path of the `.env` file, as a string. It is optional: `load_settings()` reads a file named `.env`. The file may not exist.

            **What comes out**
            - a dict with exactly two keys: `"model"` is the name of the model, and `"key"` is the API key with its middle hidden

            **Rules**
            - The file is read when it exists. Its lines are `NAME=value`. Blank lines, comment lines that start with `#`, and lines without `=` are skipped. An optional `export ` at the start of a line is ignored, and quotes (`"` or `'`) around a value are removed.
            - When the file does not exist, only the environment is used. That is not an error.
            - A variable in the real environment (`os.environ`) wins over the same name in the file.
            - `LLM_MODEL` is optional. When neither place has it, the model is `"gpt-4o-mini"`.
            - `OPENAI_API_KEY` is required. When it is missing, empty or only spaces, the function raises `RuntimeError` with a message that contains `OPENAI_API_KEY`.
            - The `"key"` is the first 3 characters of the key, three dots, and its last 4 characters. The full key never appears in the dict.
            - The function does not change `os.environ`.

            **Examples**

            A `.env` file with this content:
            ```text
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
            load_settings("missing.env")  # raises RuntimeError, the message contains "OPENAI_API_KEY"
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
