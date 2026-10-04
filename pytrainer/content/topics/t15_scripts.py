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
            ## Reading the words typed after the file name

            Every script you have written so far kept its data inside the file. A weather script that
            begins with `city = "Paris"` can only ever report on Paris. To ask about Oslo, you would have
            to open the file and change that line.

            Real tools get their data at the moment you start them. Outside this app, you start a Python
            file by typing a line like this one and pressing Enter:

            ```text
            python3 weather.py Paris tomorrow
            ```

            `python3` starts Python, and `weather.py` is the file to run. The two words after the file name
            are meant for the script. The window in which you type such a line is called a **terminal**,
            and the line itself is the **command line**.

            How does the script get at those two words? Before the first line of your file runs, Python
            puts them in a list. The list is kept in `sys`, a module that comes with Python, under the
            name `argv`:

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

            One line here needs an explanation. The Run button starts an example with nothing typed after
            the file name, so there would be no words to read. The line `sys.argv = [...]` fills the list
            by hand with what Python would have put there for the command above. In a terminal you never
            write that line.

            Now look at index 0. Python always puts the name of the script there. The words you typed come
            after it, from index 1 on. They are called **command-line arguments**: they are handed to the
            script when it starts, the way arguments are handed to a function when it is called. Click a
            cell to read that item:

            ```diagram
            {"type":"list-index","title":"sys.argv for python3 weather.py Paris tomorrow","name":"sys.argv","items":["weather.py","Paris","tomorrow"]}
            ```

            ```quiz
            A script is started with `python3 ask.py hello`. What is `sys.argv[0]`?
            - [x] `"ask.py"` :: Right. Index 0 always holds the name of the script. The words typed after it start at index 1.
            - [ ] `"hello"` :: That is the first argument, and it sits at index 1. Index 0 is taken by the name of the script.
            - [ ] `"python3"` :: `python3` is the program that runs your script. It is not put in the list. The list starts with the name of the script.
            ```

            `sys.argv` is an ordinary list, so everything from the Lists chapter works on it. `len` counts
            all its items, the script name included. The slice `sys.argv[1:]` means "from index 1 to the
            end", so it holds the arguments without the script name.

            ```predict
            import sys

            sys.argv = ["translate.py", "hello", "French", "formal"]
            print(len(sys.argv))
            print(sys.argv[-1])
            print(sys.argv[1:])
            ---
            The list has 4 items, because the script name counts as one. Index `-1` is the last item, `formal`. The slice `[1:]` leaves out index 0 and keeps the three arguments. A slice is a list, so Python prints it with square brackets.
            ```

            **Watch out:** the first argument is `sys.argv[1]`, not `sys.argv[0]`. Index 0 is never
            something the user typed as data. It is the name of the script.

            **In short:** `sys.argv` is a list of strings: the name of the script at index 0, then one item
            for each command-line argument.
        ''',
        "title": "What is in sys.argv?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            The line `sys.argv = [...]` fills the list by hand, as if the script had been started with
            `python3 ask.py summarize report.txt`. Type exactly what the program prints, one line for each
            `print`.
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
            `sys.argv` has three items: the script name `ask.py` at index 0, and then the two arguments.
            `len` counts all three, so the first line is `3`. Index 1 is the first argument, `summarize`.
            The slice `[1:]` takes everything from index 1 to the end, which is both arguments. A slice is
            a list, so Python prints it with square brackets and with single quotes around each string.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`sys.argv` is an ordinary list. Write down its items with their indexes, starting at 0.",
            "`len` counts every item, and the script name is one of them. Index 1 is the item that comes after the script name.",
            "Your first line is a number: how many items the list has. Your second line is the item at index 1, without quotes, because `print` shows a string without them. Your third line is a list: every item from index 1 to the end, written the way Python prints a list, with square brackets and with single quotes around each string.",
        ],
    },
    {
        "id": "scripts-s2",
        "lesson": r'''
            ## Where one argument ends and the next begins

            You have a script that sends a question to a model, and you start it like this:

            ```text
            python3 ask.py Explain vector search
            ```

            You meant one question. The script received three arguments: `Explain`, `vector` and `search`.
            Its `sys.argv[1]` is only the word `Explain`.

            The command line is cut into pieces at every space, and each piece becomes one item of
            `sys.argv`. To keep several words together, put quotes around them:

            ```text
            python3 ask.py "Explain vector search" short
            ```

            Now the list is `["ask.py", "Explain vector search", "short"]`. The quotes are not part of the
            argument. They only mark where it starts and where it ends.

            ```python
            import sys

            sys.argv = ["ask.py", "Explain vector search", "short"]
            print("question:", sys.argv[1])
            # question: Explain vector search
            print("style:", sys.argv[2])
            # style: short
            ```

            The cutting happens before Python starts. It is done by the program that reads what you type
            in the terminal, which is called the **shell**. Python receives the finished pieces.

            ```match
            `python3 tool.py red blue` :: 2 arguments
            `python3 tool.py "red blue"` :: 1 argument
            `python3 tool.py` :: 0 arguments
            `python3 tool.py "red blue" green "a b c"` :: 3 arguments
            ---
            Count the pieces after the file name. A space starts a new piece, unless the space is inside quotes.
            ```

            A program that takes its data from the command line like this is called a command-line tool,
            or **CLI** for short. The letters stand for "command-line interface".

            ### Trying arguments in this app

            From this step on, your scripts read arguments. The app runs your file under the name
            `solution.py`. To give it arguments, open the **Output** tab under the editor, type them in the
            box that says `command-line args`, and press **Run**. There is one difference from a real
            terminal: this box cuts at every space and does not understand quotes.

            ```quiz
            You type `one two three` in that box and press Run. What is `sys.argv[1]` in your script?
            - [x] `"one"` :: Right. The box holds three arguments, and the first of them sits at index 1.
            - [ ] `"solution.py"` :: That is `sys.argv[0]`, the name the app gives your file. The arguments start at index 1.
            - [ ] `"one two three"` :: The text is cut at the spaces, so it is three arguments, not one.
            ```

            **Watch out:** in a terminal, an argument with spaces in it needs quotes. Without them the
            script does not fail. It quietly receives more arguments than you meant, and `sys.argv[1]` is
            only the first word.

            **In short:** the shell cuts the command line at spaces, quotes keep words together, and each
            piece becomes one item of `sys.argv`.
        ''',
        "title": "Echo the first argument",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            `echo` is one of the oldest command-line tools. It prints back whatever you type after its
            name. This script is a small version of it: it prints its first argument and nothing else.

            **Your job:** the script is already in the editor, with one gap marked `___` where an index
            belongs. Replace the gap so that the script prints its first command-line argument.

            **What goes in**
            - the command-line arguments: one or more words typed after the file name, for example `hello`

            **What comes out**
            - one line of output: the first argument, exactly as it was typed

            **Rules**
            - Only the first argument is printed. When there are more arguments, the others are ignored.
            - The name of the script is not an argument, so it is not printed.
            - The checks always start the script with at least one argument.

            **Examples**

            Running `python3 solution.py hello` prints:
            ```text
            hello
            ```

            Running `python3 solution.py first second` prints:
            ```text
            first
            ```

            To try it, type `hello` in the `command-line args` box of the Output tab and press **Run**.
            With the box empty there is no first argument, and the script stops with an `IndexError`. A
            later step deals with that.
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
            "Which index of `sys.argv` holds the name of the script, and where do the arguments start? The first lesson of this chapter has a diagram of it.",
            "The script name takes the first place in the list, so the first argument is one place further on.",
            "Count the places from 0: first the name of the script, then the first argument. The number you stop at belongs in the gap. Then type an argument in the `command-line args` box and press Run to see whether it comes back.",
        ],
    },
    {
        "id": "scripts-s3",
        "lesson": r'''
            ## How many arguments did the script get?

            A tool that summarizes files is started with `python3 summarize.py a.txt b.txt`. Before it
            starts working, it wants to report how many files it was given. The arguments are in a list,
            so `len` looks like the obvious tool:

            ```python
            import sys

            sys.argv = ["summarize.py", "a.txt", "b.txt"]
            print(len(sys.argv))
            # 3
            ```

            Two files, and the answer is 3. Nothing is broken. `len` counts every item in the list, and the
            script name at index 0 is one of them. The result is always 1 higher than the number of
            arguments.

            There are two ways to get the right number. Take 1 away for the script name, or count only the
            slice that holds the arguments:

            ```python
            import sys

            sys.argv = ["summarize.py", "a.txt", "b.txt"]
            print(len(sys.argv) - 1)
            # 2
            print(len(sys.argv[1:]))
            # 2
            ```

            A count that is 1 too high or 1 too low is such a common bug that it has a name: an
            **off-by-one error**. It is hard to spot, because the program runs without any error message
            and the number looks reasonable.

            ```quiz
            A script is started with `python3 tool.py --fast notes.txt`. What is `len(sys.argv)`?
            - [x] `3` :: Right. The list holds `tool.py`, `--fast` and `notes.txt`. That is 3 items for 2 arguments.
            - [ ] `2` :: That is the number of arguments. `len(sys.argv)` also counts the script name at index 0.
            - [ ] `4` :: `python3` is not put in the list. The list starts with the name of the script.
            ```

            What about a script that is started with no arguments at all? Make a guess, then find out:

            ```predict
            import sys

            sys.argv = ["summarize.py"]
            print(len(sys.argv))
            print(sys.argv[1:])
            print(len(sys.argv[1:]))
            ---
            The list still holds the script name, so its length is 1, not 0. The slice from index 1 to the end has nothing to take, so it is the empty list `[]`, and the length of an empty list is 0. A slice that starts past the last item is not an error.
            ```

            **Watch out:** `len(sys.argv)` is never 0. Python always puts the script name in the list, so
            a script that is started with no arguments has a list of length 1.

            **In short:** the number of arguments is `len(sys.argv) - 1`, because the script name takes one
            place in the list.
        ''',
        "title": "Fix the counter",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            Before a command-line tool starts its work, it often reports how many arguments it was given.
            Someone wrote a script that does this, and its number is always 1 too high.

            **Your job:** find the bug in the script and fix it, so that it prints how many arguments came
            after the file name. The code is already in the editor, and only one line needs to change.

            **What goes in**
            - the command-line arguments: any number of words typed after the file name, or none at all

            **What comes out**
            - one line of output: the number of arguments, one space, and the word `arguments`

            **Rules**
            - The name of the script does not count as an argument.
            - With no arguments at all, the script prints `0 arguments`.

            **Examples**

            Running `python3 solution.py a b c` prints:
            ```text
            3 arguments
            ```

            Running `python3 solution.py` prints:
            ```text
            0 arguments
            ```

            To try it, type `a b c` in the `command-line args` box of the Output tab and press **Run**.
            Then empty the box and press Run again.
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
            "What is always in `sys.argv`, even when nothing is typed after the file name?",
            "`len` counts every item in the list, and one of those items is not an argument. The number has to leave that item out.",
            "Change the line that works out `count`. Either take 1 away from the length of the list, or measure the slice of the list that starts after the script name. The `print` line can stay as it is.",
        ],
    },
    {
        "id": "scripts-s4",
        "lesson": r'''
            ## Let a caller leave an argument out

            Someone runs your command without a name because they want the usual behavior. Reading the first user argument immediately would crash before your script can choose a sensible default. Check whether the argument exists first.

            ```python
            import sys
            sys.argv = ["report.py"]
            if len(sys.argv) >= 2:
                title = sys.argv[1]
            else:
                title = "Untitled"
            print(title)
            # Untitled
            ```

            This example supplies a sample argument list so it works in the lesson editor. In a real command, Python fills `sys.argv` for you. Position zero holds the script name; the first user-supplied value would be at position one. A list containing only the script name therefore has no user arguments.

            ```predict
            sample = ["report.py", "Weekly"]
            print(len(sample))
            print(sample[1])
            ---
            There are two list items, but only one user argument. Its value is Weekly.
            ```

            The alternative value is a **default**. Choose it only when the argument is absent, not merely because its text happens to be empty. An explicitly supplied empty string is still a supplied argument if the caller's command passes one.

            ```quiz
            A script receives no user arguments. Which length does sys.argv normally have?
            - [x] One. :: The script name remains at position zero.
            - [ ] Zero. :: That forgets the entry naming the script itself.
            ```

            A normally completed script reports exit code zero, meaning success. A missing optional argument need not be a failure if the program defines useful behavior for that case.

            **Watch out:** reading position one before checking the length raises `IndexError` when it is absent. A later fallback cannot undo an exception that already stopped the script.

            Check for an optional value before trying to read it.
        ''',
        "title": "Hello, argument",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A tiny CLI that greets whoever you name on the command line.

            **Your job:** write a script that greets the name given as the first command-line argument
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
            "An absent first user argument still leaves the script-name entry.",
            "Choose the supplied name when present and the specified default otherwise.",
            "Check the argument count before reading, select the greeting name, then print one line with the required punctuation.",
        ],
    },
    {
        "id": "scripts-s5",
        "lesson": r'''
            ## Run a file without starting it on import

            You want to run a report from the terminal, but another program also wants to reuse its helper functions. Importing those helpers should not start the whole report. Python gives the file a name that reveals how it was loaded.

            ```python
            def announce():
                print("report started")

            print(__name__)
            # __main__
            if __name__ == "__main__":
                announce()
            # report started
            ```

            When Python runs the file directly, its `__name__` value is `"__main__"`. When another file imports it, that value is the module's name instead. The condition selecting direct execution is the **main guard**. The guarded body runs only in the direct-run case.

            ```match
            running a file directly :: its name is __main__
            importing a file named report.py :: its name is report
            executing a def statement :: creates a function without calling its body
            ```

            The guard does not prevent the rest of the file from being read. Python still executes top-level statements during import, including function definitions and any unguarded print calls. Only the indented body of the false condition is skipped.

            ```quiz
            A print statement sits above the guard. Will importing the file execute it?
            - [x] Yes. :: Import executes top-level statements; only the guarded body is skipped.
            - [ ] No; a guard protects the entire file. :: Its scope is only the statements indented beneath it.
            ```

            Keep the distinction between defining and calling a function in mind while predicting output. A definition makes the name available. A later call actually runs its body, then execution returns to the line after that call.

            **Watch out:** putting a startup call outside the guard starts the program during import too, possibly reading input unexpectedly.

            Guard the startup action while leaving reusable definitions available to importers.
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
            The definition makes main available but produces no output. Execution next reaches the unguarded print. Because the file is being run directly, its execution name satisfies the guard, which calls main and produces another line. The final print displays that execution name after the call finishes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Definitions create functions without executing their bodies.",
            "Follow top-level statements in order and consider the name assigned during direct execution.",
            "Track the first output, whether the guarded call runs, and the final display of the file's execution name.",
        ],
    },
    {
        "id": "scripts-s6",
        "lesson": r'''
            ## Convert command-line text before arithmetic

            A budget command receives a value that looks like a number, but multiplying it repeats digits instead of calculating a larger amount. The terminal supplied text. Python needs an explicit conversion before numeric arithmetic can begin.

            ```python
            import sys
            sys.argv = ["scale.py", "8"]
            received = sys.argv[1]
            print(received * 3)
            # 888
            print(int(received) * 3)
            # 24
            ```

            The multiplication sign has different behavior for different types. A string multiplied by an integer repeats the string. Two numbers are multiplied arithmetically. Because repetition is valid Python, the incorrect version may finish without any error message.

            ```predict
            value = "12"
            print(type(value).__name__)
            print(int(value) + 3)
            ---
            The supplied value is a string. Converting it first allows numeric addition, producing fifteen.
            ```

            `int` converts suitable text into a whole number. `float` handles decimal-number text when the task allows it. Choose the conversion that matches the input contract instead of converting everything to floats and later adjusting the display.

            ```quiz
            Why does a successful exit code not prove the calculation is right?
            - [x] String repetition can complete normally while producing the wrong answer. :: Exit status reports whether the program failed, not whether its logic matched the task.
            - [ ] Python always checks the intended meaning of every operator. :: Python follows operand types, not the author's intent.
            ```

            This is a useful boundary habit: convert incoming text near the point where it enters the numeric part of your program. Later lines can then work with a known type.

            **Watch out:** `int("eight")` raises `ValueError`. If invalid text is allowed by the input contract, plan an error response; if the task guarantees numeric text, use that guarantee.

            An argument's appearance does not determine its type: command-line values arrive as strings.
        ''',
        "title": "Fix the budget doubler",
        "difficulty": 0,
        "mode": "script",
        "prompt": r'''
            A command doubles a token budget, but the supplied script repeats the digits instead of producing the expected amount.

            **Your job:** fix the script so it prints twice the supplied whole-number budget.

            **What goes in**
            - One command-line argument containing a whole number, such as `21` or `500`.

            **What comes out**
            - One line containing the doubled whole number, with no label or other text.

            **Rules**
            - The input is guaranteed to be a valid whole number.
            - The result must be numeric doubling, not digit repetition.
            - Print the result as a whole number and finish normally.

            **Examples**
            Running `python3 solution.py 21` prints:
            ```text
            42
            ```
            Running `python3 solution.py 500` prints:
            ```text
            1000
            ```
            Running `python3 solution.py 0` prints:
            ```text
            0
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
            "Check the type of the value read from the command line.",
            "The repeated digits come from string multiplication rather than numeric arithmetic.",
            "Convert the supplied whole-number text before the existing multiplication, then keep the output as a whole number.",
        ],
    },
    {
        "id": "scripts-1",
        "lesson": r'''
            ## Separate reusable work from terminal output

            A command needs to display a result, while a test needs to inspect the same result without capturing terminal output. Put the calculation in a helper that returns a value, then let a startup function decide what to print.

            ```python
            def caption(title):
                return f"Document: {title}"

            def main():
                print(caption("Notes"))

            if __name__ == '__main__':
                main()
            # Document: Notes
            ```

            The helper can now be called by another program without producing output. The startup function, conventionally named `main`, handles the visible action. The main guard ensures that action happens when the file runs directly, while importing makes the definitions available without starting the command.

            ```quiz
            Which part should an importing program call when it only needs the value?
            - [x] The returning helper. :: It supplies data without forcing a terminal display.
            - [ ] The startup function that prints. :: That function is designed around the command's visible behavior.
            ```

            The name `main` itself has no special automatic behavior in Python. Defining a function with that name does not run it. The explicit call beneath the guard is what starts it during direct execution.

            ```order
            def caption(title):
                return f"Document: {title}"
            result = caption("Guide")
            print(result)
            ---
            The helper is defined, then called to obtain a value. Printing is a separate final action.
            ```

            Keeping output at the outer edge also makes tests clearer: they can compare a return value and separately check that the command displays the expected line. Those are two different promises.

            **Watch out:** an unguarded call at the bottom of the file still runs during import. Moving the logic into functions is only half the change; guard the startup call too.

            Return reusable answers from helpers and let the command entry point display them.
        ''',
        "hints": [
            "Returning a greeting and displaying a greeting are separate responsibilities.",
            "Keep the reusable helper quiet and start the displaying function only for direct execution.",
            "Implement the returning helper, call it from the printing entry point, then guard the startup call so imports do not run it.",
        ],
        "title": "Main guard",
        "difficulty": 1,
        "prompt": r'''
            Real tools keep their code in functions and only start the program when the file is
            run directly - so other files can `import` them safely.

            **Your job:** write `greet(name)` and `main()`, plus the code that runs `main()`

            **What goes in**
            - `name`: a string, e.g. `"Ada"`
            - `greet` **returns:** the string `"Hello, <name>!"`, e.g. `"Hello, Ada!"`
            - `main()` prints `greet("world")`

            **Rules**
            - `greet` must **return** the string, not print it.
            - Running the file (`python3 solution.py`) prints `Hello, world!` and exits with code 0.
            - **Importing** the file (`import solution` from another file) must print nothing.
              Use a main guard that checks whether this file is being run directly.

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
            ## Visit every supplied argument in order

            A command accepts several document names, and you want to show exactly what it received. Treat the arguments as a list, while remembering that the first list item describes the script itself rather than a document.

            ```python
            import sys
            sys.argv = ["inspect.py", "notes", "weekly report"]
            arguments = sys.argv[1:]
            print(len(arguments))
            # 2
            for position, value in enumerate(arguments, start=1):
                print(position, value)
            # 1 notes
            # 2 weekly report
            ```

            The slice removes the script-name entry once. `enumerate` then supplies each value together with a number. Choosing `start=1` makes the displayed numbering match ordinary human lists even though Python list positions start at zero.

            ```predict
            arguments = ["red blue", "green"]
            for position, value in enumerate(arguments, start=1):
                print(position, value)
            ---
            The string containing a space is still one list item, so there are two numbered lines rather than three.
            ```

            Quoting a phrase in the shell keeps it together as one argument. By the time Python receives the list, those boundaries have already been decided. Splitting each received string again would destroy the caller's grouping.

            ```quiz
            What does a loop over an empty argument list do?
            - [x] It runs its body zero times. :: You can print the count first and let the loop naturally produce no item lines.
            - [ ] It runs once with an empty string. :: An empty list contains no item to bind to the loop variable.
            ```

            A predictable display format is useful for debugging: the count and numbered lines reveal missing quotes or unexpected extra arguments without guessing what the caller typed.

            **Watch out:** counting `sys.argv` directly includes the script name. Use the user-argument portion for both the count and the listing.

            Separate the script name once, then preserve the arguments' order and boundaries.
        ''',
        "hints": [
            "The user inputs begin after the script-name entry.",
            "Count that portion once, then pair its values with human-friendly positions.",
            "Print the argument count and visit the received items in order with numbering from one, preserving spaces inside each item.",
        ],
        "title": "Numbered arguments",
        "difficulty": 1,
        "mode": "script",
        "prompt": r'''
            Printing what a script received is a handy way to debug a CLI.

            **Your job:** write a script that reads its command-line arguments from `sys.argv`.

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
            ## Keep error messages separate from results

            Another program may read your command's output as data. If a failure message appears in that same output, the next program can mistake it for a result. Python provides a separate destination for diagnostic messages.

            ```python
            import sys
            print("report complete")
            # report complete
            print("warning: no cached results", file=sys.stderr)
            ```

            The first line goes to **standard output**, or **stdout**, where ordinary results belong. The warning goes to **standard error**, or **stderr**. Both are output streams: destinations receiving text. A terminal may display them together, but a caller can capture them separately. The warning above is on stderr, not part of the displayed result on stdout.

            ```match
            stdout :: ordinary result text
            stderr :: diagnostic text
            exit code zero :: successful completion
            ```

            The exit code is separate from both text streams. A program can print an error and still accidentally report success if it then ends normally. `sys.exit` ends the process with the chosen code; nonzero codes report failure. In this small demonstration, the stop is caught only to inspect its value.

            ```predict
            import sys
            try:
                sys.exit(4)
            except SystemExit as stopped:
                print(stopped.code)
            ---
            The requested exit code is four. Real command-line code normally leaves SystemExit uncaught so the process ends.
            ```

            Check for missing arguments before indexing them. That lets your program report the exact intended message instead of an unexpected traceback.

            **Watch out:** printing to stderr alone does not change the exit code. Error text and failure status are two promises to the caller.

            Send results, diagnostics, and completion status through their respective channels.
        ''',
        "title": "Errors go to stderr",
        "difficulty": 1,
        "mode": "script",
        "prompt": r'''
            A CLI must fail cleanly when its input is missing: error text on stderr and a
            non-zero exit code.

            **Your job:** write a script that expects one command-line argument, the prompt.

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
            "Check the absent-input case before attempting to read the prompt.",
            "Failure needs both a diagnostic on stderr and a nonzero completion status.",
            "For missing input, send the exact error to the error stream and stop; otherwise print the supplied first prompt to the ordinary output stream.",
        ],
    },
    {
        "id": "scripts-8",
        "lesson": r'''
            ## Declare a command's arguments once

            Your command now has a required destination and an optional number of copies. Manually checking every ordering, missing value, and invalid number would repeat work. Let the standard library read arguments from a small declaration of what you accept.

            ```python
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("destination")
            parser.add_argument("--copies", type=int, default=2)
            options = parser.parse_args(["archive", "--copies", "4"])
            print(options.destination, options.copies)
            # archive 4
            ```

            The `argparse` module provides an **argument parser**, which turns command-line strings into named values. A name without dashes declares a required positional input. A name beginning with two dashes declares an option. Its `type` controls conversion, and its `default` supplies the value when omitted.

            ```predict
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("destination")
            parser.add_argument("--copies", type=int, default=2)
            options = parser.parse_args(["archive"])
            print(options.copies)
            ---
            No copies option was supplied, so the parser uses the declared default of two.
            ```

            The examples provide a list to make them runnable here. In your real script, calling `parse_args` without that list reads the actual user arguments. The returned object stores values under dotted names, such as `options.copies`.

            ```quiz
            What happens when an integer option receives the text many?
            - [x] The parser reports usage on stderr and exits with code two. :: The declared conversion lets argparse handle invalid input consistently.
            - [ ] The default silently replaces it. :: Defaults cover omitted options, not supplied invalid values.
            ```

            The parser also supplies help text describing the declared interface. Keeping argument rules together makes that help match what the program actually accepts.

            **Watch out:** a hard-coded demonstration list ignores the real command line. Remove it when implementing the actual script.

            Declare the accepted inputs, then use the parser's converted values.
        ''',
        "research": {"note": "Skim the official argparse tutorial (positional arguments, optional arguments, `type=`) - it is short and shows exactly what argparse does for you.",
         "links": [{"title": "Argparse Tutorial - Python docs", "url": "https://docs.python.org/3/howto/argparse.html"},
                   {"title": "argparse reference - Python docs", "url": "https://docs.python.org/3/library/argparse.html"}]},
        "title": "First argparse CLI",
        "difficulty": 1,
        "mode": "script",
        "prompt": r'''
            Build a small greeter CLI with **argparse** instead of reading `sys.argv` by hand.

            **Your job:** write a script that uses `argparse.ArgumentParser` with:

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
            "The parser declarations should reflect the argument table.",
            "Give the named count option an integer conversion and its default, while keeping the name required.",
            "Declare both inputs, parse the real command line, then print the greeting for the requested number of repetitions.",
        ],
    },
    {
        "id": "scripts-3",
        "hints": [
            "Distinguish value-taking options from a presence-only flag.",
            "Declare conversions and defaults in the parser so the output already receives the right types.",
            "Add the required prompt and each option, use the flag action for stream, parse, and format exactly the two specified output lines.",
        ],
        "title": "ask.py options",
        "difficulty": 2,
        "placement": True,
        "mode": "script",
        "prompt": r'''
            An `ask.py` CLI needs to read a prompt and a few model settings from the command line.

            **Your job:** write a script that parses its arguments with **argparse** (`argparse.ArgumentParser`)
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
            "Missing input, unknown input, and accepted input are three separate outcomes.",
            "Decide the diagnostic destination and exit status for each outcome before formatting text.",
            "Check absence first, then membership in the known models, send the correct message to its channel, and exit with the outcome's code.",
        ],
        "title": "Exit codes",
        "difficulty": 2,
        "mode": "script",
        "prompt": r'''
            Scripts tell the caller whether they succeeded through their *exit code*: `0` means
            success, anything else means an error. Error messages go to *stderr*, not stdout.

            **Your job:** write a script that checks the model name given as its single argument (read it
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
            "Preserve physical input line numbering before skipping blank lines.",
            "Split at only the first colon, since the remaining content may contain more.",
            "Visit and number input lines, skip blanks, validate the cleaned role, print valid content or an error, track valid count and any failure, then report both final count and status.",
        ],
        "title": "Chat log filter",
        "difficulty": 3,
        "mode": "script",
        "prompt": r'''
            Chat transcripts often need cleaning before you send them to a model. This script is a
            filter: it reads from **stdin** (piped input) and writes clean lines to stdout.

            **Your job:** write a script that reads a transcript from `sys.stdin`, one message per line, in the
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
            "The entry point should accept a supplied argument list and return a status for its caller.",
            "Let the parser handle options, then distinguish direct text from the stdin marker.",
            "Read the chosen source, trim it, handle an empty result, calculate the rounded-up estimate, print the result, and reserve process exit for the guarded startup call.",
        ],
        "title": "Testable token CLI",
        "difficulty": 3,
        "prompt": r'''
            A CLI is easier to test when its logic lives in a function you can call with a list of
            arguments, instead of only running it as a separate process.

            **Your job:** write `main(argv=None)`, plus the code that runs it when the file is executed

            **What goes in**
            - `argv`: a list of argument strings like `["hello world", "--provider", "anthropic"]`;
              `None` means "use the real command line" (pass it straight to `parser.parse_args`).

            **What comes out**
            - the exit code as an int (`0` or `1`) - it does not call `sys.exit` itself.

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
              (the guarded startup code passes the return value to the process exit function).
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
