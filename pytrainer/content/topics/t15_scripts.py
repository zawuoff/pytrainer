TOPIC = {
    "id": "scripts",
    "title": "Running Scripts & CLIs",
    "track": "working-python",
    "order": 6,
    "requires": ["functions"],
    "summary": """
        Turning Python files into command-line tools: the main guard, sys.argv, argparse,
        exit codes, reading stdin and separating stdout from stderr.
    """,
    "concepts": ["__name__ == '__main__'", "sys.argv", "argparse", "positional arguments",
                 "optional flags", "type and choices", "sys.exit", "exit codes", "stdin",
                 "stderr"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["script", "cli", "command line", "argument", "sys.argv", "argparse", "main guard",
                 "__name__", "__main__", "exit code", "sys.exit", "stdin", "stdout", "stderr",
                 "option", "flag"],
    "cards": [
        {
            "syntax": "sys.argv[1:]",
            "explain": "The list of command-line arguments, all strings. sys.argv[0] is the script name.",
            "example": r'''
                import sys

                sys.argv = ["ask.py", "hello", "21"]
                print(sys.argv[1:])
                # ['hello', '21']
                print(int(sys.argv[2]) * 2)
                # 42
            ''',
        },
        {
            "syntax": 'if __name__ == "__main__":',
            "explain": "The main guard. The code under it runs when the file is run directly, not when it is imported.",
            "example": r'''
                def main():
                    print("running")

                if __name__ == "__main__":
                    main()
                # running
            ''',
        },
        {
            "syntax": "print(msg, file=sys.stderr)  /  sys.exit(code)",
            "explain": "Writes an error message to stderr, not stdout. sys.exit stops the script with that exit code; 0 means success.",
            "example": r'''
                import sys

                print("error: missing prompt", file=sys.stderr)
                try:
                    sys.exit(1)
                except SystemExit as exc:
                    print("exit code", exc.code)
                # exit code 1
            ''',
        },
        {
            "syntax": 'parser.add_argument("--days", type=int, default=3)',
            "explain": "Declares an option. A name with no dashes is a required positional argument. Read both from args.",
            "example": r'''
                import argparse

                parser = argparse.ArgumentParser()
                parser.add_argument("city")
                parser.add_argument("--days", type=int, default=3)
                args = parser.parse_args(["Oslo", "--days", "5"])
                print(args.city, args.days)
                # Oslo 5
            ''',
        },
        {
            "syntax": 'parser.add_argument("--fast", action="store_true")',
            "explain": "Declares a flag: True when it is on the command line, False when it is absent. It takes no value.",
            "example": r'''
                import argparse

                parser = argparse.ArgumentParser()
                parser.add_argument("--fast", action="store_true")
                print(parser.parse_args(["--fast"]).fast)
                # True
                print(parser.parse_args([]).fast)
                # False
            ''',
        },
        {
            "syntax": "for line in sys.stdin:",
            "explain": "Reads the script's input one line at a time. Each line ends with a newline character.",
            "example": r'''
                import io
                import sys

                sys.stdin = io.StringIO("hi\nbye\n")
                for line in sys.stdin:
                    print(line.strip().upper())
                # HI
                # BYE
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Running Scripts & CLIs

A **script** is a Python file that you run from the terminal. A **CLI** (command-line
interface) is a program that takes its input from the text typed after its name.

```bash
python3 ask.py "Explain RAG" --fast
```

The words after the file name are the **command-line arguments**. The script prints its
results and finishes with an **exit code**: a whole number that reports success or failure.

Click a stage to see what happens between the command and the exit code. The stages
name `sys.argv`, the main guard, stdout and stderr. The sections below explain each one.

```diagram
{"type":"flow","title":"From the command line to the exit code","steps":[
{"label":"Type the command","detail":"The shell splits the command line at spaces. Quotes keep several words together as one argument.","code":"python3 ask.py \"Explain RAG\" --fast"},
{"label":"Fill sys.argv","detail":"Python stores the script name and the arguments in the list sys.argv. Every item is a string.","code":"sys.argv == ['ask.py', 'Explain RAG', '--fast']"},
{"label":"Run the file","detail":"Python runs the file from top to bottom. A def statement creates a function. It does not run the function body.","code":"import sys\n\ndef main(argv):\n    ..."},
{"label":"Check the main guard","detail":"The file was run directly, so __name__ is '__main__'. The condition is True and main is called.","code":"if __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))"},
{"label":"Write output","detail":"print writes results to stdout. print with file=sys.stderr writes error messages to stderr.","code":"print(answer)\nprint(\"error: missing prompt\", file=sys.stderr)"},
{"label":"Exit","detail":"sys.exit(code) stops the script with that exit code. A script that reaches the end of the file exits with code 0.","code":"sys.exit(0)   # success\nsys.exit(1)   # error"}
]}
```

### sys.argv

`sys` is a standard library module. `sys.argv` is a list of strings that holds the command
line. Index `0` is the script name.
The arguments start at index `1`, so `sys.argv[1:]` is the list of arguments and
`len(sys.argv) - 1` is their number.

```python
import sys

sys.argv = ["ask.py", "Explain RAG", "--fast"]
print(sys.argv[0])
# ask.py
print(sys.argv[1:])
# ['Explain RAG', '--fast']
print(len(sys.argv) - 1)
# 2
```

The first line of the example assigns a list to `sys.argv`. In a terminal, Python fills it
for you.

Click a cell to read that item of `sys.argv`.

```diagram
{"type":"list-index","title":"sys.argv for python3 ask.py \"Explain RAG\" --fast","name":"sys.argv","items":["ask.py","Explain RAG","--fast"]}
```

Every argument is a string. Convert it with `int()` or `float()` before you do arithmetic.

```python
import sys

sys.argv = ["ask.py", "256"]
print(sys.argv[1] + "1")
# 2561
print(int(sys.argv[1]) + 1)
# 257
```

### The main guard

Python sets the variable `__name__` in every file. It is `"__main__"` when the file is run
directly. It is the module name (the file name without `.py`) when the file is imported. The line
`if __name__ == "__main__":` is the **main guard**. Code under it runs only when the file
is run directly, so importing the file prints nothing.

```python
def main():
    print("running")

if __name__ == "__main__":
    main()
# running
```

### stdout, stderr and exit codes

A script can write text to two separate outputs, called **streams**. `print(...)` writes to
**stdout**, which is for results. `print(..., file=sys.stderr)` writes to **stderr**, which
is for error messages.

`sys.exit(code)` stops the script with that exit code. By convention `0` means success,
`1` means a general error and `2` means the command line was wrong. A common pattern is a `main`
function that returns the exit code.

```python
import sys

def main(argv):
    if len(argv) < 1:
        print("error: missing prompt", file=sys.stderr)
        return 1
    print("prompt:", argv[0])
    return 0

print(main(["Explain RAG"]))
# prompt: Explain RAG
# 0
print(main([]))
# 1
```

The second call also writes `error: missing prompt` to stderr. In a real script the last
line is `sys.exit(main(sys.argv[1:]))` under the main guard. In bash, `echo $?` prints the
exit code of the last command: `$?` is the shell's name for that code.

### argparse

`argparse` is a standard library module that reads the command line for you. You declare
each argument once with `add_argument`, then call `parse_args`.

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("prompt")
parser.add_argument("--max-tokens", type=int, default=256)
parser.add_argument("--stream", action="store_true")
parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
args = parser.parse_args(["Explain RAG", "--max-tokens", "64", "--stream"])
print(args.prompt, args.max_tokens, args.stream, args.provider)
# Explain RAG 64 True openai
```

- `"prompt"` has no dashes, so it is a **positional argument**: it is required and is found by its position.
- `"--max-tokens"` is an **option**. `type=int` converts the string, and `default=256` is used when the option is absent. You read it as `args.max_tokens`: argparse drops the leading dashes and replaces the other dash with an underscore.
- `action="store_true"` makes a **flag**: `True` when present, `False` when absent, with no value after it.
- `choices=[...]` limits the allowed values.
- `nargs="?"` means "zero or one value". Together with `default=...` it makes a positional
  argument optional: when the user leaves it out, the default is used.

`parser.parse_args()` with no list reads `sys.argv[1:]`. Pass a list to test the parser. On
bad input, argparse prints a `usage: ...` message to stderr and exits with code `2`.
argparse also adds a `--help` option that prints the list of arguments.

### stdin

**stdin** (standard input) is the stream that a script reads its input from. In
`echo "hi" | python3 ask.py`, the `|` character is a **pipe**: it sends the output of the
command on its left to the stdin of the command on its right. Without a pipe, stdin is the
text that the user types in the terminal. `for line in sys.stdin:` reads it one line at a
time. `sys.stdin.read()` returns all of it as one string.

```python
import io
import sys

sys.stdin = io.StringIO("user: hi\nassistant: hello\n")
for line in sys.stdin:
    print(line.strip().upper())
# USER: HI
# ASSISTANT: HELLO
```

`io.StringIO(text)` creates an object that you read in the same way as a file, but its
content comes from the string `text`. The example assigns it to `sys.stdin` so that it runs
without a pipe.

### Common mistakes

- `len(sys.argv)` counts the script name. The number of arguments is `len(sys.argv) - 1`.
- `sys.argv[1]` raises `IndexError` when no argument was given. Check `len(sys.argv) > 1` first.
- Arguments are strings. `"21" * 2` is `"2121"`, and `int("21") * 2` is `42`.
- Without a main guard, `import` runs the whole program.
- An error message printed to stdout ends up mixed with the results. Print it to stderr.
'''

EXERCISES = [
    {
        "id": "scripts-s1",
        "lesson": r'''
            ## The `sys.argv` list

            A **script** is a Python file that you run from a terminal. The command
            `python3 weather.py Paris tomorrow` runs the file `weather.py`. The words after the
            file name are the **command-line arguments**.

            Python stores the command line in `sys.argv`, a list of strings. `sys` is a standard library module, so you write `import sys` first.

            ```python
            import sys

            sys.argv = ["weather.py", "Paris", "tomorrow"]
            print(sys.argv)
            # ['weather.py', 'Paris', 'tomorrow']
            print(sys.argv[0])
            # weather.py
            print(sys.argv[2])
            # tomorrow
            ```

            The first line assigns a list to `sys.argv`, because the Run button starts the code
            with no arguments. In a terminal, Python fills the list for you.

            Index `0` is always the script's own name. The arguments start at index `1`.
            `sys.argv` is a normal list, so `len()`, indexes and slices work on it.

            Click a cell to read that item of `sys.argv`.

            ```diagram
            {"type":"list-index","title":"sys.argv for python3 weather.py Paris tomorrow","name":"sys.argv","items":["weather.py","Paris","tomorrow"]}
            ```
        ''',
        "title": "What is in sys.argv?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            The first line pretends the script was started with
            `python3 ask.py summarize report.txt`. Type exactly what it prints.
        ''',
        "code": r'''
            import sys

            sys.argv = ["ask.py", "summarize", "report.txt"]
            print(len(sys.argv))
            print(sys.argv[1])
            print(sys.argv[1:])
        ''',
        "solution": r'''
            3
            summarize
            ['summarize', 'report.txt']
        ''',
        "explanation": r'''
            `sys.argv` includes the script name at index 0, so it has 3 items. The first real
            argument is at index 1. The slice `[1:]` is every argument after the script
            name, printed as a list.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`sys.argv` is a plain list of strings. Count its items, including the script name.",
            "Index 0 is the script name, index 1 is the first real argument, and `[1:]` is a slice of the rest.",
            "Line 1 is the list length (3 items). Line 2 is the item at index 1. Line 3 is a list printed with square brackets and single quotes.",
        ],
    },
    {
        "id": "scripts-s2",
        "lesson": r'''
            ## Arguments and quotes

            The shell (the program that reads what you type in the terminal) splits the
            command line at spaces. Each piece becomes one item of
            `sys.argv`. Quotes keep several words together as one argument.

            ```bash
            python3 tool.py hello             # sys.argv == ["tool.py", "hello"]
            python3 tool.py "hello world" x   # sys.argv == ["tool.py", "hello world", "x"]
            ```

            The script name is at index `0`, so the first argument is always at index `1`.

            ```python
            import sys

            sys.argv = ["tool.py", "hello world", "x"]
            print("script:", sys.argv[0])
            # script: tool.py
            print("first:", sys.argv[1])
            # first: hello world
            print("second:", sys.argv[2])
            # second: x
            ```

            A program that reads its input from the command line is a **CLI** (command-line
            interface). The `python3` command is a CLI: it reads the file name that you type
            after it.
        ''',
        "title": "Echo the first argument",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A script can read the words typed after its file name on the command line.

            **Fill in the blank** (`___`) so the script prints its **first** command-line argument.

            **Rules**
            - Print only the first argument (index `0` of `sys.argv` is the script's own name, not an argument).
            - Ignore any extra arguments.

            **Examples**

            Running `python3 solution.py hello` prints:
            ```
            hello
            ```

            Running `python3 solution.py first second` prints:
            ```
            first
            ```
        ''',
        "starter": r'''
            import sys

            print(sys.argv[___])
        ''',
        "tests": r'''
            def test_prints_first_argument():
                r = run_script(args=["hello"])
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "hello", f"printed {r.stdout!r}"

            def test_ignores_later_arguments():
                r = run_script(args=["first", "second"])
                assert r.stdout.strip() == "first", f"printed {r.stdout!r}"
        ''',
        "solution": r'''
            import sys

            print(sys.argv[1])
        ''',
        "hints": [
            "`sys.argv[0]` is not an argument you typed - it is the script's own name.",
            "The first word after the file name sits right after the script name in the list.",
            "Replace `___` with the index `1`.",
        ],
    },
    {
        "id": "scripts-s3",
        "lesson": r'''
            ## Counting arguments

            `len(sys.argv)` counts every item of the list, and the script name at index `0` is
            one of them. The result is 1 higher than the number of arguments. A count that is
            1 too high or 1 too low is called an **off-by-one error**.

            ```python
            import sys

            sys.argv = ["tool.py", "a", "b"]
            print(len(sys.argv))
            # 3
            print(sys.argv[1:])
            # ['a', 'b']
            print(len(sys.argv[1:]))
            # 2
            ```

            The slice `sys.argv[1:]` is a new list with every item from index `1` to the end.
            Those items are exactly the arguments, so the length of the slice is their number.
            With no arguments, the slice is the empty list `[]` and its length is `0`.

            There are two equivalent ways to get the number of arguments: `len(sys.argv) - 1`
            and `len(sys.argv[1:])`.
        ''',
        "title": "Fix the counter",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A CLI often reports how many arguments it received.

            **Fix the bug:** this script should print how many arguments it was given, **not**
            counting the script name. Right now it is off by one.

            **Rules**
            - Print exactly `N arguments` where `N` is the number of arguments after the file name.
            - With no arguments, print `0 arguments`.

            **Examples**

            Running `python3 solution.py a b c` prints:
            ```
            3 arguments
            ```

            Running `python3 solution.py` prints:
            ```
            0 arguments
            ```
        ''',
        "starter": r'''
            import sys

            count = len(sys.argv)
            print(f"{count} arguments")
        ''',
        "tests": r'''
            def test_three_arguments_prints_3_arguments():
                r = run_script(args=["a", "b", "c"])
                assert r.stdout.strip() == "3 arguments", f"printed {r.stdout!r}"

            def test_no_arguments_prints_0_arguments():
                r = run_script()
                assert r.stdout.strip() == "0 arguments", f"printed {r.stdout!r}"
        ''',
        "solution": r'''
            import sys

            count = len(sys.argv) - 1
            print(f"{count} arguments")
        ''',
        "hints": [
            "What is always in `sys.argv`, even when you type no arguments at all?",
            "The script name is counted by `len(sys.argv)`. Leave it out of the count.",
            "Subtract 1 from `len(sys.argv)` (or take the length of the slice `sys.argv[1:]`).",
        ],
    },
    {
        "id": "scripts-s4",
        "lesson": r'''
            ## Missing arguments

            A user can run a script without any argument. Then `sys.argv` has one item, the
            script name, and `sys.argv[1]` raises `IndexError`. The script stops and prints a
            traceback. To avoid that, check the length of the list before you read index `1`.

            ```python
            import sys

            for argv in (["hi.py", "Lin"], ["hi.py"]):
                sys.argv = argv
                if len(sys.argv) > 1:
                    who = sys.argv[1]
                else:
                    who = "nobody"
                print("argument:", who)
            # argument: Lin
            # argument: nobody
            ```

            `len(sys.argv) > 1` is `True` when there is at least one argument. When it is
            `False`, the `else` branch assigns a **default**: a value to use when none was given.
            `.get(key, default)` does the same for a missing key in a dict.

            A script finishes with an **exit code**: a whole number that tells the terminal how
            the run ended. A script that ends without an exception has exit code `0`, which
            means success. An exception that no `except` catches gives exit code `1`.
        ''',
        "title": "Hello, argument",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A tiny CLI that greets whoever you name on the command line.

            **Write a script** that greets the name given as the first command-line argument
            (`sys.argv[1]`).

            **Rules**
            - Print exactly `Hello, <name>!` (comma, space, exclamation mark).
            - If no argument is given, greet `world` instead - the script must **not crash**
              (exit code 0).

            **Examples**

            Running `python3 solution.py Ada` prints:
            ```
            Hello, Ada!
            ```

            Running `python3 solution.py` prints:
            ```
            Hello, world!
            ```
        ''',
        "starter": r'''
            import sys

            # greet sys.argv[1], or "world" if there is no argument
        ''',
        "tests": r'''
            def test_name_argument_is_greeted():
                r = run_script(args=["Ada"])
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "Hello, Ada!", f"printed {r.stdout!r}"

            def test_no_argument_greets_world():
                r = run_script()
                assert r.returncode == 0, f"crashed: {r.stderr[-300:]}"
                assert r.stdout.strip() == "Hello, world!", f"printed {r.stdout!r}"
        ''',
        "solution": r'''
            import sys

            if len(sys.argv) > 1:
                name = sys.argv[1]
            else:
                name = "world"
            print(f"Hello, {name}!")
        ''',
        "hints": [
            "Check how long `sys.argv` is before reading `sys.argv[1]`.",
            "If there is more than just the script name, use the first argument; otherwise use `world`. Then print.",
            "Use `if len(sys.argv) > 1:` to set `name = sys.argv[1]`, `else:` set `name = \"world\"`, then print an f-string with `name`.",
        ],
    },
    {
        "id": "scripts-s5",
        "lesson": r'''
            ## The `__name__` variable and the main guard

            Python sets a variable called `__name__` in every file before it runs the file. Its
            value depends on how the file is used:

            - When you run the file directly (`python3 tool.py`), `__name__` is `"__main__"`.
            - When another file imports it (`import tool`), `__name__` is `"tool"`.

            ```python
            def main():
                mode = "run directly"
                print("main runs:", mode)

            print("__name__ is", __name__)
            # __name__ is __main__
            if __name__ == "__main__":
                main()
            # main runs: run directly
            print("end of file")
            # end of file
            ```

            The line `if __name__ == "__main__":` is called the **main guard**. The code under it
            runs only when the file is run directly. It does not run when the file is imported.

            Python runs a file from top to bottom. A `def` statement creates the function and
            does not run its body. The body of `main` runs only when a later line calls `main()`.

            Step through the program to see the order in which the lines run.

            ```diagram
            {"type": "trace", "title": "Running a file with a main guard", "code": ["def main():", "    mode = \"run directly\"", "    print(\"main runs:\", mode)", "", "print(\"__name__ is\", __name__)", "if __name__ == \"__main__\":", "    main()", "print(\"end of file\")"], "steps": [
              {"line": 1, "vars": {}, "out": "", "note": "def creates the function main. Its body does not run yet."},
              {"line": 5, "vars": {}, "out": ""},
              {"line": 6, "vars": {}, "out": "__name__ is __main__\n", "note": "The file is run directly, so the condition is True."},
              {"line": 7, "vars": {}, "out": "__name__ is __main__\n"},
              {"line": 2, "vars": {}, "out": "__name__ is __main__\n"},
              {"line": 3, "vars": {"mode": "'run directly'"}, "out": "__name__ is __main__\n"},
              {"line": 8, "vars": {}, "out": "__name__ is __main__\nmain runs: run directly\n"},
              {"line": null, "vars": {}, "out": "__name__ is __main__\nmain runs: run directly\nend of file\n"}
            ]}
            ```
        ''',
        "title": "Run or import?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            This file is **run directly** (`python3 solution.py`).
            Type exactly what it prints.
        ''',
        "code": r'''
            def main():
                print("running main")

            print("top level")
            if __name__ == "__main__":
                main()
            print(__name__)
        ''',
        "solution": r'''
            top level
            running main
            __main__
        ''',
        "explanation": r'''
            Python runs the file from top to bottom. `def` only defines `main`, it does not
            run it. The first print shows `top level`. Because the file is run directly,
            `__name__` is `"__main__"`, so the guard is True and `main()` runs. The last
            line prints `__name__` itself.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Go top to bottom. `def` alone never prints anything.",
            "When a file is run directly (not imported), `__name__` holds a special value.",
            "First the top-level print, then the guard is True so `main()` prints, then the value of `__name__` (`__main__`) is printed.",
        ],
    },
    {
        "id": "scripts-s6",
        "lesson": r'''
            ## Arguments are strings

            Every item of `sys.argv` is a string. If you type `42` on the command line, the
            script receives the string `"42"`, not the integer `42`.

            ```python
            import sys

            sys.argv = ["calc.py", "7"]
            raw = sys.argv[1]
            print(raw * 3)
            # 777
            print(int(raw) * 3)
            # 21
            print(type(raw).__name__, type(int(raw)).__name__)
            # str int
            ```

            `type(raw).__name__` is the name of the type as text, so the last line prints `str int`.

            `"7" * 3` repeats the string three times and gives `"777"`. `int("7")` builds the
            integer `7` from the string, so `int("7") * 3` multiplies numbers and gives `21`.

            The string version raises no exception. The script runs to the end and prints a
            wrong result, so the bug is easy to miss.

            Convert with `int()` for whole numbers and `float()` for numbers with a decimal
            point. Do it on the line where you read the argument.
        ''',
        "title": "Fix the budget doubler",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A tiny CLI doubles a token budget given on the command line. It prints nonsense:
            find the bug and fix it.

            **Fix the script** so it prints twice the number given as its first argument.

            **Rules**
            - The first argument is a whole number, e.g. `21`.
            - Print only the doubled number, as a whole number.

            **Examples**

            Running `python3 solution.py 21` prints:
            ```
            42
            ```

            Running `python3 solution.py 500` prints:
            ```
            1000
            ```
        ''',
        "starter": r'''
            import sys

            budget = sys.argv[1]
            print(budget * 2)
        ''',
        "tests": r'''
            def test_21_prints_42():
                r = run_script(args=["21"])
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "42", f"printed {r.stdout!r}"

            def test_500_prints_1000():
                r = run_script(args=["500"])
                assert r.stdout.strip() == "1000", f"printed {r.stdout!r}"
        ''',
        "solution": r'''
            import sys

            budget = int(sys.argv[1])
            print(budget * 2)
        ''',
        "hints": [
            "What type is every item of `sys.argv`? What does `*` do with that type?",
            "`\"21\" * 2` repeats the text. Turn the argument into a number before doubling it.",
            "Wrap `sys.argv[1]` in `int(...)` on the line that reads the budget.",
        ],
    },
    {
        "id": "scripts-1",
        "lesson": r'''
            ## Functions plus a main guard

            A well-structured script has two parts. The first part is function definitions,
            which other files and tests can use with `import`. The second part is the main
            guard, which calls `main()` only when the file is run directly.

            ```python
            def shout(text):
                return text.upper() + "!"

            def main():
                print(shout("ready"))

            if __name__ == "__main__":
                main()
            # READY!
            ```

            `import` runs every top-level line of the imported file. Tests import your file to
            call its functions. Without the guard, the import would also run the whole program:
            it would print, read input and perhaps call an API. With the guard, `__name__` is
            the module name during an import, the condition is `False`, and `main()` is not called.

            The two functions have different roles. `shout` **returns** a value, so a test can
            call it and compare the result. `main` **prints**, which is the part the user sees.
            Keep that split: functions with logic return values, and `main` prints them.
        ''',
        "hints": [
            "`greet` should `return` the string; `main` prints it; the main guard decides when `main` runs.",
            "Only call `main()` when the file is run directly, never when it is imported.",
            "`greet` returns an f-string `Hello, {name}!`. `main` does `print(greet(\"world\"))`. At the bottom, add `if __name__ == \"__main__\":` with `main()` indented under it.",
        ],
        "title": "Main guard",
        "difficulty": 1,
        "prompt": r'''
            Real tools keep their code in functions and only start the program when the file is
            run directly - so other files can `import` them safely.

            **Write:** `greet(name)` and `main()`, plus the code that runs `main()`

            - `name`: a string, e.g. `"Ada"`
            - `greet` **returns:** the string `"Hello, <name>!"`, e.g. `"Hello, Ada!"`
            - `main()` prints `greet("world")`

            **Rules**
            - `greet` must **return** the string, not print it.
            - Running the file (`python3 solution.py`) prints `Hello, world!` and exits with code 0.
            - **Importing** the file (`import solution` from another file) must print nothing.
              Use the *main guard*: `if __name__ == "__main__":`.

            **Examples**
            ```python
            greet("Bob")    # returns "Hello, Bob!"
            ```

            Running `python3 solution.py` prints:
            ```
            Hello, world!
            ```

            A file containing `import solution` then `print(solution.greet("Ada"))` prints only:
            ```
            Hello, Ada!
            ```
        ''',
        "starter": r'''
            def greet(name):
                ...


            def main():
                ...
        ''',
        "tests": r'''
            def test_running_the_file_prints_hello_world():
                r = run_script()
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "Hello, world!", f"printed {r.stdout!r}"

            def test_importing_the_file_prints_nothing():
                with open("uses_it.py", "w") as fh:
                    fh.write("import solution\nprint(solution.greet('Ada'))\n")
                r = run_script(file="uses_it.py")
                assert r.returncode == 0, r.stderr[-300:]
                assert r.stdout.strip() == "Hello, Ada!", f"importing the module printed: {r.stdout!r}"

            def test_greet_returns_the_string_without_printing():
                mod = load()
                value, printed = capture(mod.greet, "Bob")
                assert value == "Hello, Bob!", f"greet returned {value!r}"
                assert printed == "", "greet should return the string, not print it"
        ''',
        "solution": r'''
            def greet(name):
                return f"Hello, {name}!"


            def main():
                print(greet("world"))


            if __name__ == "__main__":
                main()
        ''',
    },
    {
        "id": "scripts-2",
        "lesson": r'''
            ## Looping over the arguments

            The arguments are items of a list, so a `for` loop can visit them one by one. When
            you also need the position of each item, use `enumerate(args, start=1)`. It produces
            `(number, item)` pairs, and `start=1` makes the numbers begin at 1 instead of 0.

            ```python
            import sys

            sys.argv = ["show.py", "alpha", "beta gamma"]
            args = sys.argv[1:]
            print("got", len(args))
            # got 2
            for pos, word in enumerate(args, start=1):
                print(f"#{pos} -> {word}")
            # #1 -> alpha
            # #2 -> beta gamma
            ```

            Take the slice `sys.argv[1:]` once and store it in a variable such as `args`. After
            that, use only `args`, and the script name is never counted or printed by mistake.

            With no arguments, `args` is the empty list. The loop body runs zero times, so you
            need no extra `if` for that case.

            Printing exactly what a script received is a quick way to debug a CLI that seems to
            ignore its input. A missing quote often turns one argument into two.
        ''',
        "hints": [
            "The real arguments are `sys.argv[1:]` (everything after the script name).",
            "Print the count first, then loop over the arguments printing a position number that starts at 1.",
            "Slice off the script name into a list of arguments. Print `argc=` followed by that list's length. Then loop over the arguments with a position counter that starts at 1 (`enumerate` with `start=1` does this) and print the counter, a colon and a space, and the argument.",
        ],
        "title": "Numbered arguments",
        "difficulty": 1,
        "mode": "script",
        "prompt": r'''
            Printing what a script received is a handy way to debug a CLI.

            **Write a script** that reads its command-line arguments from `sys.argv`.

            **Rules**
            - The script name is **not** an argument: do not count it or print it.
            - First line: `argc=N` where `N` is the number of arguments.
            - Then one line per argument: `<position>: <argument>`, positions start at `1`.
            - An argument in quotes (like `"the report"`) is a single argument.
            - With no arguments, print only `argc=0`.

            **Examples**

            Running `python3 solution.py summarize "the report" --fast` prints:
            ```
            argc=3
            1: summarize
            2: the report
            3: --fast
            ```

            Running `python3 solution.py x` prints:
            ```
            argc=1
            1: x
            ```

            Running `python3 solution.py` prints:
            ```
            argc=0
            ```
        ''',
        "starter": r'''
            import sys
        ''',
        "tests": r'''
            def test_three_args_print_count_then_numbered_lines():
                r = run_script(args=["summarize", "the report", "--fast"])
                assert r.returncode == 0, r.stderr[-300:]
                got = r.stdout.strip().splitlines()
                assert got == ["argc=3", "1: summarize", "2: the report", "3: --fast"], f"printed {got!r}"

            def test_no_args_prints_only_argc_0():
                r = run_script()
                assert r.stdout.strip() == "argc=0", f"printed {r.stdout!r}"

            def test_script_name_is_not_counted_or_printed():
                r = run_script(args=["x"])
                assert "solution.py" not in r.stdout, "the script name is not an argument"
                assert r.stdout.strip().splitlines() == ["argc=1", "1: x"], f"printed {r.stdout!r}"
        ''',
        "solution": r'''
            import sys

            args = sys.argv[1:]
            print(f"argc={len(args)}")
            for i, arg in enumerate(args, start=1):
                print(f"{i}: {arg}")
        ''',
    },
    {
        "id": "scripts-7",
        "lesson": r'''
            ## stdout, stderr and exit codes

            A script can write text to two separate outputs, called **streams**:

            - **stdout** (standard output) is for results. `print(...)` writes to it.
            - **stderr** (standard error) is for error and warning messages. You write to it
              with `print(..., file=sys.stderr)`.

            Both streams appear in the terminal. They can be redirected separately: with
            `python3 tool.py > out.txt` the `>` sends stdout into the file `out.txt`, and the
            error messages still appear on screen.

            A script also reports how the run ended with an **exit code**. `0` means success and
            any other number means failure. `sys.exit(code)` stops the script at that line with
            that code. In bash, `echo $?` prints the exit code of the last command.

            ```python
            import sys

            print("result: 42")
            # result: 42
            print("warning: cache is empty", file=sys.stderr)
            # warning: cache is empty
            try:
                sys.exit(3)
            except SystemExit as exc:
                print("sys.exit stopped with code", exc.code)
            # sys.exit stopped with code 3
            ```

            The second `print` writes its line to stderr. `sys.exit` works by raising the
            exception `SystemExit`. The example catches it only to print the code. In a real
            script you do not catch it, and the script stops.
        ''',
        "title": "Errors go to stderr",
        "difficulty": 1,
        "mode": "script",
        "prompt": r'''
            A CLI must fail cleanly when its input is missing: error text on stderr and a
            non-zero exit code.

            **Write a script** that expects one command-line argument, the prompt.

            **Rules**

            | situation | stdout | stderr | exit code |
            | --- | --- | --- | --- |
            | an argument is given | `prompt: <argument>` | nothing | `0` |
            | no argument | nothing | `error: missing prompt` | `1` |

            - Print the error with `print(..., file=sys.stderr)` and stop with `sys.exit(1)`.
            - No traceback may appear (don't let an `IndexError` escape).
            - Only the first argument is used.

            **Examples**

            Running `python3 solution.py "What is RAG?"` prints on stdout (exit code `0`):
            ```
            prompt: What is RAG?
            ```

            Running `python3 solution.py` prints on **stderr** (exit code `1`):
            ```
            error: missing prompt
            ```
        ''',
        "starter": r'''
            import sys
        ''',
        "tests": r'''
            def test_argument_is_printed_on_stdout_exit_0():
                r = run_script(args=["What is RAG?"])
                assert r.returncode == 0, f"exit code {r.returncode}: {r.stderr[-300:]}"
                assert r.stdout.strip() == "prompt: What is RAG?", f"stdout {r.stdout!r}"
                assert r.stderr == "", f"stderr should be empty, got {r.stderr!r}"

            def test_missing_argument_error_on_stderr_exit_1():
                r = run_script()
                assert r.returncode == 1, f"exit code {r.returncode}"
                assert r.stderr.strip() == "error: missing prompt", f"stderr {r.stderr!r}"
                assert r.stdout == "", f"stdout should be empty, got {r.stdout!r}"

            def test_no_traceback_when_argument_missing():
                r = run_script()
                assert "Traceback" not in r.stderr, "exit with sys.exit, not an exception"
        ''',
        "solution": r'''
            import sys

            if len(sys.argv) < 2:
                print("error: missing prompt", file=sys.stderr)
                sys.exit(1)
            print(f"prompt: {sys.argv[1]}")
        ''',
        "hints": [
            "Check the length of `sys.argv` before reading the argument.",
            "If there is no argument, print the error to the error channel and stop with exit code 1. Otherwise print the prompt line normally.",
            "`if len(sys.argv) < 2:` then `print(\"error: missing prompt\", file=sys.stderr)` and `sys.exit(1)`. After the `if`, print the f-string `prompt: {sys.argv[1]}`.",
        ],
    },
    {
        "id": "scripts-8",
        "lesson": r'''
            ## Parsing arguments with `argparse`

            Reading `sys.argv` yourself needs many `if` checks once a script has options such as
            `--model` or `--days`. **argparse** is a standard library module that does this work.
            You declare each argument once. argparse then reads the command line, converts the
            types, applies the defaults, and generates the error messages and a `--help` text.

            ```python
            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument("city")
            parser.add_argument("--days", type=int, default=3)
            args = parser.parse_args(["Oslo", "--days", "5"])
            print(args.city, args.days, type(args.days).__name__)
            # Oslo 5 int
            ```

            - `"city"` has no dashes, so it is a **positional argument**. It is required, and
              argparse finds it by its position on the command line.
            - `"--days"` starts with two dashes, so it is an **option**. The user may leave it
              out. `type=int` converts the string `"5"` to the integer `5`, and `default=3` is
              the value when the option is absent.
            - `parse_args` returns an object that stores each value under the argument's name.
              You read the values as `args.city` and `args.days`.

            The example passes a list to `parse_args` so that it runs without a terminal. In a
            real script you call `parser.parse_args()` with no list, and it reads `sys.argv[1:]`.
            When a required argument is missing, argparse prints `usage: ...` to stderr and
            exits with code `2`.
        ''',
        "research": {"note": "Skim the official argparse tutorial (positional arguments, optional arguments, `type=`) - it is short and shows exactly what argparse does for you.",
         "links": [{"title": "Argparse Tutorial - Python docs", "url": "https://docs.python.org/3/howto/argparse.html"},
                   {"title": "argparse reference - Python docs", "url": "https://docs.python.org/3/library/argparse.html"}]},
        "title": "First argparse CLI",
        "difficulty": 1,
        "mode": "script",
        "prompt": r'''
            Build a small greeter CLI with **argparse** instead of reading `sys.argv` by hand.

            **Write a script** that uses `argparse.ArgumentParser` with:

            | argument | kind | default |
            | --- | --- | --- |
            | `name` | positional, required | - |
            | `--times` | int | `1` |

            **Rules**
            - Print `Hello, <name>!` exactly `--times` times, one per line. Exit code `0`.
            - A missing `name`, or a `--times` value that is not a whole number, must fail the
              normal argparse way: `usage: ...` on stderr and exit code `2` (argparse does this).
            - Must use `argparse.ArgumentParser` (checked).

            **Examples**

            Running `python3 solution.py Ada` prints:
            ```
            Hello, Ada!
            ```

            Running `python3 solution.py Bob --times 3` prints:
            ```
            Hello, Bob!
            Hello, Bob!
            Hello, Bob!
            ```

            Running `python3 solution.py` (no name) prints a `usage: ...` error on **stderr** and
            exits with code `2`. So does `python3 solution.py Ada --times many`.
        ''',
        "starter": r'''
            import argparse
        ''',
        "tests": r'''
            def test_name_only_greets_once():
                r = run_script(args=["Ada"])
                assert r.returncode == 0, f"exit code {r.returncode}: {r.stderr[-300:]}"
                assert r.stdout.strip().splitlines() == ["Hello, Ada!"], f"printed {r.stdout!r}"

            def test_times_option_repeats_the_greeting():
                r = run_script(args=["Bob", "--times", "3"])
                assert r.stdout.strip().splitlines() == ["Hello, Bob!"] * 3, f"printed {r.stdout!r}"

            def test_missing_name_prints_usage_and_exits_2():
                r = run_script()
                assert r.returncode == 2, f"exit code {r.returncode}"
                assert "usage" in r.stderr.lower(), f"stderr {r.stderr!r}"

            def test_non_numeric_times_exits_2():
                r = run_script(args=["Ada", "--times", "many"])
                assert r.returncode == 2, f"exit code {r.returncode}"

            def test_uses_argparse_argumentparser():
                assert "ArgumentParser" in source(), "use argparse.ArgumentParser"
        ''',
        "solution": r'''
            import argparse

            parser = argparse.ArgumentParser(description="Greet someone.")
            parser.add_argument("name")
            parser.add_argument("--times", type=int, default=1)
            args = parser.parse_args()
            for _ in range(args.times):
                print(f"Hello, {args.name}!")
        ''',
        "hints": [
            "Create an `ArgumentParser`, add one argument per row of the table, then parse.",
            "The name is positional (no dashes). `--times` needs a type conversion and a default. Then loop that many times, printing the greeting.",
            "`parser.add_argument(\"name\")`, `parser.add_argument(\"--times\", type=int, default=1)`, `args = parser.parse_args()`, then `for _ in range(args.times):` print the f-string with `args.name`.",
        ],
    },
    {
        "id": "scripts-3",
        "hints": [
            "Use `argparse.ArgumentParser()` and one `add_argument` call per option.",
            "A positional argument has no dashes. Options take `type=` and `default=`. A flag that is True when present uses a special `action`. Then print the attributes of the parsed result.",
            "`parser.add_argument(\"prompt\")`, `\"--model\"` with a default, `\"--temperature\"` with `type=float`, `\"--max-tokens\"` with `type=int` (read it back as `args.max_tokens`), `\"--stream\"` with `action=\"store_true\"`. Call `parser.parse_args()` and print the two lines with f-strings.",
        ],
        "title": "ask.py options",
        "difficulty": 2,
        "placement": True,
        "mode": "script",
        "prompt": r'''
            An `ask.py` CLI needs to read a prompt and a few model settings from the command line.

            **Write a script** that parses its arguments with **argparse** (`argparse.ArgumentParser`)
            and prints the result.

            | argument | kind | default |
            | --- | --- | --- |
            | `prompt` | positional, required | - |
            | `--model` | string | `gpt-4o-mini` |
            | `--temperature` | float | `0.7` |
            | `--max-tokens` | int | `256` |
            | `--stream` | flag: `True` when present, no value after it | `False` |

            **Rules**
            - Print exactly two lines:
              `model=<model> temperature=<temperature> max_tokens=<max_tokens> stream=<stream>`
              then `prompt=<prompt>`. Exit code 0.
            - `--temperature` is converted to a float (`1` prints as `1.0`) and `--max-tokens` to an
              int (`050` prints as `50`).
            - Options may come before or after the prompt.
            - A missing prompt, or a non-numeric `--temperature`, must fail the normal argparse way:
              a `usage:` message on stderr and exit code `2` (argparse does this for you).
            - Must use `argparse.ArgumentParser` (checked).

            **Examples**

            Running `python3 solution.py hi` prints:
            ```
            model=gpt-4o-mini temperature=0.7 max_tokens=256 stream=False
            prompt=hi
            ```

            Running `python3 solution.py --model o3-mini "Explain RAG" --temperature 0.2 --max-tokens 1024 --stream` prints:
            ```
            model=o3-mini temperature=0.2 max_tokens=1024 stream=True
            prompt=Explain RAG
            ```

            Running `python3 solution.py q --temperature 1 --max-tokens 050` prints (first line):
            ```
            model=gpt-4o-mini temperature=1.0 max_tokens=50 stream=False
            ```

            Running `python3 solution.py` (no prompt) prints a `usage: ...` error on **stderr**
            and exits with code `2`. So does `python3 solution.py hi --temperature hot`.
        ''',
        "starter": r'''
            import argparse
        ''',
        "tests": r'''
            def _lines(r):
                assert r.returncode == 0, f"exit code {r.returncode}: {r.stderr[-300:]}"
                return r.stdout.strip().splitlines()

            def test_only_prompt_uses_all_defaults():
                got = _lines(run_script(args=["hi"]))
                assert got == ["model=gpt-4o-mini temperature=0.7 max_tokens=256 stream=False", "prompt=hi"], f"printed {got!r}"

            def test_all_options_set_in_any_order():
                got = _lines(run_script(args=["--model", "o3-mini", "Explain RAG", "--temperature", "0.2",
                                              "--max-tokens", "1024", "--stream"]))
                assert got == ["model=o3-mini temperature=0.2 max_tokens=1024 stream=True", "prompt=Explain RAG"], f"printed {got!r}"

            def test_temperature_is_float_and_max_tokens_is_int():
                got = _lines(run_script(args=["q", "--temperature", "1", "--max-tokens", "050"]))
                assert got[0] == "model=gpt-4o-mini temperature=1.0 max_tokens=50 stream=False", f"printed {got[0]!r}"

            def test_missing_prompt_prints_usage_and_exits_2():
                r = run_script()
                assert r.returncode == 2, f"exit code {r.returncode}"
                assert "usage" in r.stderr.lower(), f"stderr: {r.stderr!r}"

            def test_non_numeric_temperature_exits_2():
                r = run_script(args=["hi", "--temperature", "hot"])
                assert r.returncode == 2, f"exit code {r.returncode}"

            def test_uses_argparse_argumentparser():
                assert "ArgumentParser" in source(), "use argparse.ArgumentParser"
        ''',
        "solution": r'''
            import argparse


            def parse_args(argv=None):
                parser = argparse.ArgumentParser(description="Ask an LLM a question.")
                parser.add_argument("prompt")
                parser.add_argument("--model", default="gpt-4o-mini")
                parser.add_argument("--temperature", type=float, default=0.7)
                parser.add_argument("--max-tokens", type=int, default=256)
                parser.add_argument("--stream", action="store_true")
                return parser.parse_args(argv)


            if __name__ == "__main__":
                args = parse_args()
                print(f"model={args.model} temperature={args.temperature} "
                      f"max_tokens={args.max_tokens} stream={args.stream}")
                print(f"prompt={args.prompt}")
        ''',
    },
    {
        "id": "scripts-4",
        "hints": [
            "Three outcomes, three exit codes: check for a missing argument first, then whether the model is known.",
            "Error messages go to stderr with `print(..., file=sys.stderr)` and the script stops with `sys.exit(code)`. Success prints to stdout and exits 0.",
            "Put the logic in `main(argv)` that returns a code: `if len(argv) < 1` print usage to stderr and return 2; `if model not in KNOWN` print the error to stderr and return 1; else print `ok: <model>` and return 0. Finish with `sys.exit(main(sys.argv[1:]))` under the main guard.",
        ],
        "title": "Exit codes",
        "difficulty": 2,
        "mode": "script",
        "prompt": r'''
            Scripts tell the caller whether they succeeded through their *exit code*: `0` means
            success, anything else means an error. Error messages go to *stderr*, not stdout.

            **Write a script** that checks the model name given as its single argument (read it
            from `sys.argv`, not argparse). Known models: `gpt-4o`, `gpt-4o-mini`, `claude-sonnet`
            (already in `KNOWN`).

            **Rules**

            | situation | stdout | stderr | exit code |
            | --- | --- | --- | --- |
            | known model | `ok: <model>` | nothing | `0` |
            | unknown model | nothing | `unknown model: <model>` | `1` |
            | no argument | nothing | `usage: solution.py MODEL` | `2` |

            - Print errors with `print(..., file=sys.stderr)`; stdout must stay empty on errors.
            - Exit with `sys.exit(code)`: no exception traceback may appear on stderr.

            **Examples**

            Running `python3 solution.py claude-sonnet` prints on stdout, exit code `0`:
            ```
            ok: claude-sonnet
            ```

            Running `python3 solution.py gpt-5x` prints on **stderr**, exit code `1`:
            ```
            unknown model: gpt-5x
            ```

            Running `python3 solution.py` prints on **stderr**, exit code `2`:
            ```
            usage: solution.py MODEL
            ```
        ''',
        "starter": r'''
            import sys

            KNOWN = {"gpt-4o", "gpt-4o-mini", "claude-sonnet"}
        ''',
        "tests": r'''
            def test_known_model_prints_ok_and_exits_0():
                r = run_script(args=["claude-sonnet"])
                assert r.returncode == 0, f"exit code {r.returncode}"
                assert r.stdout.strip() == "ok: claude-sonnet", f"stdout {r.stdout!r}"

            def test_unknown_model_error_on_stderr_exits_1():
                r = run_script(args=["gpt-5x"])
                assert r.returncode == 1, f"exit code {r.returncode}"
                assert r.stderr.strip() == "unknown model: gpt-5x", f"stderr {r.stderr!r}"
                assert r.stdout == "", f"stdout should be empty, got {r.stdout!r}"

            def test_no_argument_usage_on_stderr_exits_2():
                r = run_script()
                assert r.returncode == 2, f"exit code {r.returncode}"
                assert r.stderr.strip() == "usage: solution.py MODEL", f"stderr {r.stderr!r}"
                assert r.stdout == "", f"stdout should be empty, got {r.stdout!r}"

            def test_errors_exit_cleanly_without_traceback():
                r = run_script(args=["nope"])
                assert "Traceback" not in r.stderr, "exit cleanly with sys.exit, not an exception"
        ''',
        "solution": r'''
            import sys

            KNOWN = {"gpt-4o", "gpt-4o-mini", "claude-sonnet"}


            def main(argv):
                if len(argv) < 1:
                    print("usage: solution.py MODEL", file=sys.stderr)
                    return 2
                model = argv[0]
                if model not in KNOWN:
                    print(f"unknown model: {model}", file=sys.stderr)
                    return 1
                print(f"ok: {model}")
                return 0


            if __name__ == "__main__":
                sys.exit(main(sys.argv[1:]))
        ''',
    },
    {
        "id": "scripts-5",
        "research": {"note": "This script reads piped input from standard input, which we have not used yet. Read what `sys.stdin` is and how to loop over it, then come back.",
         "links": [{"title": "sys.stdin - Python docs", "url": "https://docs.python.org/3/library/sys.html#sys.stdin"}]},
        "hints": [
            "Loop over `sys.stdin` with a line counter; blank lines still count for numbering.",
            "For each non-blank line, split it at the first colon into role and content. Valid roles are printed to stdout in the new format; everything else gets an error line on stderr and marks the run as failed.",
            "Use `enumerate(sys.stdin, start=1)`. `role, sep, content = line.partition(\":\")`; lower-case and strip the role. If there is no colon or the role is not in the allowed set, print `line N: invalid` with `file=sys.stderr` and set a flag. Otherwise print `[ROLE] content` and count it. At the end print the count and `sys.exit(0 or 1)`.",
        ],
        "title": "Chat log filter",
        "difficulty": 3,
        "mode": "script",
        "prompt": r'''
            Chat transcripts often need cleaning before you send them to a model. This script is a
            filter: it reads from **stdin** (piped input) and writes clean lines to stdout.

            **Write a script** that reads a transcript from `sys.stdin`, one message per line, in the
            form `role: content`.

            **Rules**
            - Blank (or whitespace-only) lines are skipped silently.
            - A line is valid if it has a colon and the part before the **first** colon, stripped
              and lowercased, is `system`, `user` or `assistant`. The content may contain more colons.
            - For each valid line print to **stdout**: `[ROLE] content` - role in UPPERCASE,
              content stripped of surrounding spaces.
            - For each invalid line print to **stderr**: `line N: invalid`, where `N` is the 1-based
              line number in the input (blank lines count toward the numbering). Then keep going.
            - At the end print `messages=K` to stdout, where `K` is the number of valid lines.
            - Exit code: `0` if every non-blank line was valid (including empty input), otherwise `1`.
            - When everything is valid, stderr must be empty.

            **Examples**

            Running `printf 'user: hi\n\nbanana\nAssistant:  hello \ntool: x\n' | python3 solution.py` prints on stdout:
            ```
            [USER] hi
            [ASSISTANT] hello
            messages=2
            ```
            and on stderr (exit code `1`):
            ```
            line 3: invalid
            line 5: invalid
            ```

            Running `printf 'user: time is 10:30\n' | python3 solution.py` prints (exit code `0`):
            ```
            [USER] time is 10:30
            messages=1
            ```

            With empty input it prints `messages=0` and exits with code `0`.
        ''',
        "starter": r'''
            import sys
        ''',
        "tests": r'''
            def test_valid_transcript_formats_all_lines_and_exits_0():
                r = run_script(stdin="system: be brief\nuser: What is RAG?\nassistant: Retrieval + generation.\n")
                assert r.returncode == 0, f"exit code {r.returncode}, stderr {r.stderr!r}"
                assert r.stdout.strip().splitlines() == [
                    "[SYSTEM] be brief", "[USER] What is RAG?", "[ASSISTANT] Retrieval + generation.",
                    "messages=3"], f"stdout {r.stdout!r}"
                assert r.stderr == "", f"stderr should be empty, got {r.stderr!r}"

            def test_invalid_lines_reported_on_stderr_with_line_numbers():
                r = run_script(stdin="user: hi\n\nbanana\nAssistant:  hello \ntool: x\n")
                assert r.stdout.strip().splitlines() == ["[USER] hi", "[ASSISTANT] hello", "messages=2"], f"stdout {r.stdout!r}"
                assert r.stderr.strip().splitlines() == ["line 3: invalid", "line 5: invalid"], f"stderr {r.stderr!r}"

            def test_any_invalid_line_gives_exit_code_1():
                r = run_script(stdin="nonsense\n")
                assert r.returncode == 1, f"exit code {r.returncode}"

            def test_content_may_contain_colons():
                r = run_script(stdin="user: time is 10:30\n")
                assert r.stdout.strip().splitlines()[0] == "[USER] time is 10:30", f"stdout {r.stdout!r}"

            def test_empty_input_prints_messages_0_and_exits_0():
                r = run_script(stdin="")
                assert r.returncode == 0, f"exit code {r.returncode}"
                assert r.stdout.strip() == "messages=0", f"stdout {r.stdout!r}"
        ''',
        "solution": r'''
            import sys

            ROLES = {"system", "user", "assistant"}


            def main():
                count = 0
                ok = True
                for n, line in enumerate(sys.stdin, start=1):
                    if not line.strip():
                        continue
                    role, sep, content = line.partition(":")
                    role = role.strip().lower()
                    if not sep or role not in ROLES:
                        print(f"line {n}: invalid", file=sys.stderr)
                        ok = False
                        continue
                    print(f"[{role.upper()}] {content.strip()}")
                    count += 1
                print(f"messages={count}")
                return 0 if ok else 1


            if __name__ == "__main__":
                sys.exit(main())
        ''',
    },
    {
        "id": "scripts-6",
        "hints": [
            "Build the parser inside `main(argv=None)` and call `parser.parse_args(argv)` so tests can pass their own list.",
            "The text positional is optional (`nargs=\"?\"`, default `\"-\"`). Provider uses `choices=`. If the text is `\"-\"`, read stdin. Round up the division, and return exit codes instead of calling exit inside `main`.",
            "Add `text` with `nargs=\"?\", default=\"-\"`, `--provider` with `choices=[...]`, `--chars-per-token` with `type=int, default=4`. Read `sys.stdin.read()` when text is `-`, strip it; if empty, print the error to stderr and return 1. Use `math.ceil(len(text) / n)`, print, return 0. At the bottom: `if __name__ == \"__main__\": sys.exit(main())`.",
        ],
        "title": "Testable token CLI",
        "difficulty": 3,
        "prompt": r'''
            A CLI is easier to test when its logic lives in a function you can call with a list of
            arguments, instead of only running it as a separate process.

            **Write:** `main(argv=None)`, plus the code that runs it when the file is executed

            - `argv`: a list of argument strings like `["hello world", "--provider", "anthropic"]`;
              `None` means "use the real command line" (pass it straight to `parser.parse_args`).
            - **Returns:** the exit code as an int (`0` or `1`) - it does not call `sys.exit` itself.

            Arguments (parse them with **argparse**):
            - `text` - optional positional, default `"-"`; the value `"-"` means read the text from stdin
            - `--provider` - one of `openai`, `anthropic`, `local` (default `openai`)
            - `--chars-per-token` - int, default `4`

            **Rules**
            - Strip the text (spaces/newlines at both ends), then
              tokens = number of characters / chars-per-token, **rounded up** (8 chars / 3 -> `3`).
            - Print `provider=<provider> tokens=<tokens>` to stdout and return `0`.
            - If the stripped text is empty: print `error: empty input` to **stderr**, print nothing
              to stdout, return `1`.
            - An invalid `--provider` fails the normal argparse way (exit code `2`).
            - Running the file must call `main()` and exit with its return value
              (`sys.exit(main())` under `if __name__ == "__main__":`).
            - Importing the file must not run the CLI (and must not read stdin).

            **Examples**
            ```python
            main(["hello world", "--provider", "anthropic"])  # prints provider=anthropic tokens=3, returns 0
            main(["abcdefgh", "--chars-per-token", "3"])       # prints provider=openai tokens=3, returns 0
            ```

            Running `echo "  abcdefgh " | python3 solution.py --provider local` prints (exit code `0`):
            ```
            provider=local tokens=2
            ```

            Running `echo "   " | python3 solution.py -` prints `error: empty input` on **stderr** and
            exits with code `1`.

            Running `python3 solution.py hi --provider gemini` fails with exit code `2`.
        ''',
        "starter": r'''
            import argparse
            import sys


            def main(argv=None):
                ...
        ''',
        "tests": r'''
            from solution import main

            def test_main_with_argv_list_prints_and_returns_0():
                code, out = capture(main, ["hello world", "--provider", "anthropic"])
                assert out.strip() == "provider=anthropic tokens=3", f"printed {out!r}"
                assert code == 0, f"main returned {code!r}"

            def test_tokens_round_up_with_custom_chars_per_token():
                code, out = capture(main, ["abcdefgh", "--chars-per-token", "3"])
                assert out.strip() == "provider=openai tokens=3", f"printed {out!r}"

            def test_reads_stripped_stdin_when_no_text_given():
                r = run_script(args=["--provider", "local"], stdin="  abcdefgh \n")
                assert r.returncode == 0, f"exit code {r.returncode}: {r.stderr[-300:]}"
                assert r.stdout.strip() == "provider=local tokens=2", f"stdout {r.stdout!r}"

            def test_empty_input_error_on_stderr_exits_1():
                r = run_script(args=["-"], stdin="   \n")
                assert r.returncode == 1, f"exit code {r.returncode}"
                assert "empty input" in r.stderr, f"stderr {r.stderr!r}"
                assert r.stdout == "", f"stdout {r.stdout!r}"

            def test_invalid_provider_exits_2():
                r = run_script(args=["hi", "--provider", "gemini"])
                assert r.returncode == 2, f"exit code {r.returncode}"

            def test_importing_does_not_run_the_cli():
                with open("imp.py", "w") as fh:
                    fh.write("import solution\nprint('imported')\n")
                r = run_script(file="imp.py", stdin="should not be read\n")
                assert r.stdout.strip() == "imported" and r.returncode == 0, f"importing ran the CLI: {r!r}"
        ''',
        "solution": r'''
            import argparse
            import math
            import sys


            def main(argv=None):
                parser = argparse.ArgumentParser(description="Estimate token count.")
                parser.add_argument("text", nargs="?", default="-")
                parser.add_argument("--provider", choices=["openai", "anthropic", "local"], default="openai")
                parser.add_argument("--chars-per-token", type=int, default=4)
                args = parser.parse_args(argv)

                text = sys.stdin.read() if args.text == "-" else args.text
                text = text.strip()
                if not text:
                    print("error: empty input", file=sys.stderr)
                    return 1
                tokens = math.ceil(len(text) / args.chars_per_token)
                print(f"provider={args.provider} tokens={tokens}")
                return 0


            if __name__ == "__main__":
                sys.exit(main())
        ''',
    },
]
