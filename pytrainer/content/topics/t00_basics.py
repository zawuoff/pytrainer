TOPIC = {
    "id": "basics",
    "title": "Python Basics",
    "track": "foundations",
    "order": 0,
    "requires": [],
    "summary": """
        Day one: print(), comments, calling functions, and writing your answers as
        def + return with indentation. Plus how to read error messages and failing checks.
    """,
    "concepts": ["print", "comments", "calling functions", "def", "return", "indentation",
                 "error messages", "reading test output"],
}

LESSON = r'''
## Chapter notes: Python Basics

**Running code.** A program runs top to bottom, one line at a time. **Run** (Alt+Enter)
runs your file and shows what it prints. **Check** (Ctrl+Enter) runs hidden tests that
call your function and lists each check as pass or fail.

**print()** shows values. Text goes in quotes, numbers don't. Commas put one space
between values. Each `print` makes one line.

```python
print("Hello, AI!")
print("tokens:", 2 + 3)
```

**Comments** start with `#`. Python skips everything after `#` on that line.

**Text vs numbers.** `"2" + "3"` glues text into `"23"`; `2 + 3` adds to `5`.

**Calling a function**: its name, then parentheses with the inputs (*arguments*).
`len("hello")` is `5`, `max(3, 9, 4)` is `9`, `round(2.567, 1)` is `2.6`.
Calls can be nested: `print(len("hi"))`.

**Defining a function** - the answer format of almost every exercise:

```python
def add(a, b):
    return a + b

print(add(2, 3))
```

- `def name(parameters):` ends with a colon.
- The body is indented 4 spaces.
- `return value` hands the value back and ends the function.
- `a` and `b` are *parameters*; each call fills them with *arguments*.

**return vs print.** `print` only shows text. `return` gives the value back to the code
that called the function (the tests!). No `return` means the function returns `None`.

**Reading errors.** An error names the file, the **line number** and the problem:
- `SyntaxError: expected ':'` - a missing colon (or other typo) on that line.
- `IndentationError: expected an indented block` - the body is not indented.
- `NameError: name 'Name' is not defined` - a typo, or capital letters that don't match.

**Reading a failing check.** `add(2, 3) returned None` means "I called your function with
these inputs and got this back". `None` almost always means a missing `return`.

**Docs.** Every built-in has an entry at docs.python.org (e.g. *Built-in Functions*).
Reading them is a real engineering skill.
'''

EXERCISES = [
    {
        "id": "basics-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            A program is a **recipe**: Python reads it from the top, one line at a time, and does
            what each line says.

            The first instruction you need is `print()`. Whatever you put between the parentheses
            is shown on the screen. Text goes inside quotes. Maths is worked out *before* printing.
            Commas let you show several values on one line, with a space between them.

            ```python
            print("Hello, AI!")
            print(2 + 3)
            print("tokens:", 120)
            ```

            A line that starts with `#` is a **comment**: a note for humans. Python skips it
            completely, even if it looks like code.

            ```python
            # print("this never runs")
            print("this runs")  # a comment can sit at the end of a line too
            ```

            Vocabulary: a line of code is a *statement*; the text in quotes is a *string*.

            Watch out: comments are skipped, so they print nothing at all.
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints, one line per `print`.
        ''',
        "code": r'''
            print("Hello")
            # print("Goodbye")
            print(2 + 3)
            print("tokens:", 40)
        ''',
        "solution": r'''
            Hello
            5
            tokens: 40
        ''',
        "explanation": r'''
            The second line is a comment, so it never runs. `2 + 3` is calculated before
            printing, so you see `5`, not `2 + 3`. Commas in `print` put a single space
            between the values.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Go line by line from the top. Lines starting with # are comments.",
            "Comments are skipped. Maths inside print() is calculated first. Commas become spaces.",
            "Write one output line for each print that actually runs: 3 prints run, so 3 lines.",
        ],
    },
    {
        "id": "basics-s4",
        "title": "Two lines of output",
        "difficulty": 0,
        "mode": "script",
        "lesson": r'''
            So far you ran code by reading it. Now you write a whole **script**: a file that does its
            job when you run it, like a to-do list Python works through from top to bottom.

            Each `print()` call makes **one line** of output. Two calls, two lines:

            ```python
            print("loading model")
            print("done")
            ```

            Try the **Run** button (Alt+Enter) on your own file: it runs the file like a real
            program and shows exactly what it printed. Use it before you press **Check**, so you can
            compare your output with what the task asks for.

            Vocabulary: what a program prints is called its *output* (sometimes *stdout*, short for
            "standard output").

            Watch out: output must match exactly - capital letters, spelling and spaces all count.
            `Ready` is not `ready`.
        ''',
        "prompt": r'''
            A *script* is a file that does its work when you run it - no function needed.

            **Write a script** that prints two lines.

            **Rules**
            - Line 1 is exactly `PyTrainer` (capital P and capital T).
            - Line 2 is exactly `ready` (all lowercase).
            - Print nothing else, and the script must run without errors.

            **Examples**

            Running `python3 solution.py` prints:
            ```
            PyTrainer
            ready
            ```

            Press **Run** to see your output before you press **Check**.
        ''',
        "starter": r'''
            # print the two lines here
        ''',
        "tests": r'''
            def test_prints_exactly_the_two_lines():
                r = run_script()
                assert r.returncode == 0, r.stderr
                assert r.stdout.strip().splitlines() == ["PyTrainer", "ready"], f"printed {r.stdout!r}"

            def test_first_line_is_pytrainer():
                r = run_script()
                lines = r.stdout.strip().splitlines()
                assert lines and lines[0] == "PyTrainer", f"first line was {lines[:1]!r}"
        ''',
        "solution": r'''
            print("PyTrainer")
            print("ready")
        ''',
        "hints": [
            "Each call to print() shows one line.",
            "You need two print calls, one per line, each with its text in quotes.",
            "Line 1: print the text PyTrainer. Line 2: print the text ready. Check spelling and capitals.",
        ],
    },
    {
        "id": "basics-s6",
        "title": "Text or number?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            Values come in different kinds. A **number** is something you can do maths
            with. **Text** is a row of characters, like letters on a name badge, even if some
            of those characters happen to be digits. Quotes are what make something text.

            ```python
            print(2 + 3)
            print("2" + "3")
            ```

            The first line adds two numbers and prints `5`. The second line *glues* two
            pieces of text together and prints `23`. Same `+` sign, different job - it depends
            on what kind of values are on each side.

            Gluing is handy for building messages:

            ```python
            print("Hello, " + "Ada" + "!")
            ```

            Vocabulary: text in Python is called a *string* (a string of characters). A whole
            number is an *integer*, or *int*. Gluing strings together is called
            *concatenation*.

            Watch out: anything inside quotes is printed as-is. `print("2 + 3")` shows the
            characters `2 + 3`, it does no maths.
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints, one line per `print`.
        ''',
        "code": r'''
            print(2 + 3)
            print("2" + "3")
            print("2 + 3")
            print("AI" + " " + "app")
        ''',
        "solution": r'''
            5
            23
            2 + 3
            AI app
        ''',
        "explanation": r'''
            `2 + 3` adds numbers. `"2" + "3"` glues two strings into `23`. `"2 + 3"` is one
            string, printed exactly as written. The last line glues three strings, and the
            middle one is a single space.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Look for quotes: values in quotes are text, values without quotes are numbers.",
            "+ adds numbers but glues text end to end. Text inside quotes is printed exactly as written.",
            "Line 1: the sum. Line 2: the two characters stuck together. Line 3: the text between the quotes. Line 4: the three pieces glued, including the space.",
        ],
    },
    {
        "id": "basics-s7",
        "title": "Call a built-in",
        "difficulty": 0,
        "mode": "script",
        "lesson": r'''
            Python ships with ready-made tools you can use straight away. Think of them as
            **kitchen appliances**: you don't build a blender, you put ingredients in and
            press the button.

            `len()` is one of them. Give it some text, and it counts the characters:

            ```python
            print(len("hello"))
            print(len("hi there"))
            ```

            That prints `5` and then `8` - the space counts as a character too.

            Notice the shape: `len("hello")` is the tool's name, then parentheses with the
            input inside. And you can put one call inside another: `print(len("hello"))`
            first counts, then prints the count.

            Vocabulary: using a function is called *calling* it. The input between the
            parentheses is an *argument*. Tools that come with Python are *built-in
            functions* (or *built-ins*).

            Watch out: don't count by hand and type the number - let `len` do the work.
        ''',
        "prompt": r'''
            Before sending a prompt you check its size.

            **Write a script** that prints the number of characters in the text
            `Explain RAG in one sentence.`

            **Rules**
            - Use the built-in `len()` to count; don't type the number yourself (a check looks for a `len(...)` call).
            - Spaces and the full stop count as characters.
            - Print only the number, on one line.

            **Examples**

            Running `python3 solution.py` prints a single whole number, e.g. for the text
            `hi there` it would print:
            ```
            8
            ```
        ''',
        "starter": r'''
            # print the length of the text here
        ''',
        "tests": r'''
            import ast

            def test_prints_the_character_count():
                r = run_script()
                assert r.returncode == 0, r.stderr
                assert r.stdout.strip() == "28", f"printed {r.stdout!r}"

            def test_uses_len_to_count():
                calls = [n for n in ast.walk(ast.parse(source()))
                         if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "len"]
                assert calls, "count with len(...), don't type the number"
        ''',
        "solution": r'''
            print(len("Explain RAG in one sentence."))
        ''',
        "hints": [
            "You need two built-ins: one that counts characters and one that shows a value.",
            "Put the text (in quotes) inside len(...), and put that whole call inside print(...).",
            "Write print, open a parenthesis, write len, open another parenthesis, the text in double quotes exactly as given, then close both parentheses.",
        ],
    },
    {
        "id": "basics-s2",
        "title": "Fill in the return",
        "difficulty": 0,
        "lesson": r'''
            A **function** is a small machine with a name. You build it once, then use it as often
            as you like. This is the answer format of almost every exercise here: you write the
            machine, the checks switch it on and look at what comes out.

            ```python
            def model_name():
                return "gpt-4o-mini"

            print(model_name())
            ```

            How to read it:
            - `def model_name():` means "define a function called model_name". The line ends with a colon `:`.
            - The line below is pushed in by 4 spaces. That *indentation* says "this belongs to the function".
            - `return` hands a value back to whoever called the function.

            `model_name()` (name + parentheses) *calls* the function: it runs the body and gives back
            the returned value. The proper name for that value is the *return value*.

            Watch out: text must be inside quotes. `return Hello` (no quotes) makes Python look for
            a name called Hello and fail.
        ''',
        "prompt": r'''
            A function that always gives back the same greeting text.

            **Write:** replace the `___` in `greeting()` (it takes no inputs)

            - **Returns:** the text (a *string*) `Hello, AI!`

            **Rules**
            - The text must match exactly: capital `H`, a comma after `Hello`, one space, `AI` in capitals, and `!` at the end.
            - Return it as text (inside quotes), not `None` and not a number.

            **Examples**
            ```python
            greeting()   # returns "Hello, AI!"
            ```

            Reminder: text goes inside quotes, and `return` hands it back to the caller.
        ''',
        "starter": r'''
            def greeting():
                return ___
        ''',
        "tests": r'''
            from solution import greeting

            def test_returns_exactly_hello_ai():
                got = greeting()
                assert got == "Hello, AI!", f"greeting() returned {got!r}"

            def test_returns_text_not_none():
                got = greeting()
                assert got is not None, "greeting() returned None - is there a return?"
                assert isinstance(got, str), f"greeting() returned {got!r}, which is not text"
        ''',
        "solution": r'''
            def greeting():
                return "Hello, AI!"
        ''',
        "hints": [
            "The blank needs a piece of text (a string). Strings are written inside quotes.",
            "Put the exact words Hello, AI! inside double quotes after return.",
            "Delete the three underscores and type the text in quotes. Watch the capital H, the comma and the !.",
        ],
    },
    {
        "id": "basics-s5",
        "title": "Write add()",
        "difficulty": 0,
        "lesson": r'''
            Most machines need something to work on. A coffee machine needs beans; `add` needs two
            numbers. You list the inputs inside the parentheses of the `def` line.

            ```python
            def double(n):
                return n * 2

            print(double(4))
            print(double(10))
            ```

            `n` is a placeholder. Each call fills it in: `double(4)` runs the body with `n` being 4,
            `double(10)` runs it again with `n` being 10.

            Vocabulary: the placeholder names in the `def` line are *parameters*. The actual values
            you pass in a call are *arguments*. A function can have several parameters, separated by
            commas: `def area(width, height):`.

            The maths signs work as you expect: `+` add, `-` subtract, `*` multiply, `/` divide.

            Watch out: use the parameter names in the body, not fixed numbers. `return 2 + 3` would
            give 5 for every call.
        ''',
        "prompt": r'''
            Your first real function: it takes two numbers and hands back their total.

            **Write:** the body of `add(a, b)` (the `def` line is already there)

            - `a`: a whole number (an *int*), e.g. `2`
            - `b`: another whole number, e.g. `3`
            - **Returns:** the sum `a + b`, as a number (not text), e.g. `5`

            **Rules**
            - **Return** the result (don't just `print` it) - the checks call `add(...)` and look at what comes back.
            - Negative numbers must work too.

            **Examples**
            ```python
            add(2, 3)      # returns 5
            add(100, 28)   # returns 128
            add(-1, 1)     # returns 0
            ```
        ''',
        "starter": r'''
            def add(a, b):
                ...
        ''',
        "tests": r'''
            from solution import add

            def test_add_2_and_3_returns_5():
                assert add(2, 3) == 5, f"add(2, 3) returned {add(2, 3)!r}"

            def test_adds_bigger_and_negative_numbers():
                assert add(100, 28) == 128, f"add(100, 28) returned {add(100, 28)!r}"
                assert add(-1, 1) == 0, f"add(-1, 1) returned {add(-1, 1)!r}"
        ''',
        "solution": r'''
            def add(a, b):
                return a + b
        ''',
        "hints": [
            "The body needs one line that starts with return.",
            "Return the result of adding the two parameters a and b together.",
            "Replace the ... with: return, then a, then +, then b. Keep the 4-space indent.",
        ],
    },
    {
        "id": "basics-s3",
        "title": "Fix: print is not return",
        "difficulty": 0,
        "lesson": r'''
            `print` and `return` look similar but do very different jobs. `print` is like **saying
            the answer out loud** in an empty room: it shows up on screen, but nobody can use it.
            `return` is **handing the answer to the person who asked**, so they can use it.

            The checks are that person. They call your function and look at what it hands back.

            ```python
            def shows(n):
                print(n * 2)

            def gives(n):
                return n * 2

            print(gives(4))
            print(shows(4))
            ```

            The last line prints `8` (said out loud inside `shows`) and then `None` - what `shows`
            handed back. A function with no `return` gives back `None`, Python's "nothing here" value.

            Vocabulary: a check message like `double(4) returned None` means "I called it with 4
            and got nothing back". That almost always means a missing `return`.
        ''',
        "prompt": r'''
            `double(n)` should hand back twice its input, but Check says it returns `None`.
            Find and fix the one bug.

            **Fix:** `double(n)`

            - `n`: a whole number, e.g. `4`
            - **Returns:** `n` times 2, as a number, e.g. `8`

            **Rules**
            - The value must be **returned**, not printed.
            - Zero and negative numbers must work too.

            **Examples**
            ```python
            double(4)     # returns 8
            double(0)     # returns 0
            double(-3)    # returns -6
            ```
        ''',
        "starter": r'''
            def double(n):
                print(n * 2)
        ''',
        "tests": r'''
            from solution import double

            def test_double_4_returns_8():
                got = double(4)
                assert got == 8, f"double(4) returned {got!r}"

            def test_doubles_zero_and_negative_numbers():
                assert double(0) == 0, f"double(0) returned {double(0)!r}"
                assert double(-3) == -6, f"double(-3) returned {double(-3)!r}"
        ''',
        "solution": r'''
            def double(n):
                return n * 2
        ''',
        "hints": [
            "The failing check says the function returned None. What does a function give back when it has no return?",
            "print only shows the value on screen. The tests need the value handed back.",
            "Replace the word print and its parentheses with return, keeping n * 2.",
        ],
    },
    {
        "id": "basics-s8",
        "title": "Fix: indent the body",
        "difficulty": 0,
        "lesson": r'''
            Python uses **indentation** (spaces at the start of a line) the way a book uses
            paragraphs: it shows which lines belong together. Everything that belongs to a
            function is pushed in by 4 spaces under its `def` line.

            ```python
            def excited(text):
                return text + "!"

            print(excited("ready"))
            ```

            The `return` line is indented, so it is part of `excited`. The `print` line is
            back at the left edge, so it is *not* part of the function - it runs on its own.

            If the body is not indented, Python stops before running anything:

            ```text
            IndentationError: expected an indented block after function definition on line 1
            ```

            Vocabulary: the indented lines under `def` are the function's *body*, and a group
            of lines with the same indentation is a *block*.

            Watch out: use the same amount of indentation (4 spaces) for every line in a block.
        ''',
        "prompt": r'''
            `shout(text)` should add an exclamation mark to a piece of text, but Check fails
            with an `IndentationError`. Fix the one bug.

            **Fix:** `shout(text)`

            - `text`: a string, e.g. `"hi"`
            - **Returns:** a string: `text` followed by `!`, e.g. `"hi!"`

            **Rules**
            - No space before the `!`.
            - It must work for any text, including the empty string `""` (gives `"!"`).

            **Examples**
            ```python
            shout("hi")      # returns "hi!"
            shout("ready")   # returns "ready!"
            shout("")        # returns "!"
            ```
        ''',
        "starter": r'''
            def shout(text):
            return text + "!"
        ''',
        "tests": r'''
            from solution import shout

            def test_adds_an_exclamation_mark():
                got = shout("hi")
                assert got == "hi!", f"shout('hi') returned {got!r}"

            def test_works_for_other_text():
                got = shout("ready")
                assert got == "ready!", f"shout('ready') returned {got!r}"
                got = shout("")
                assert got == "!", f"shout('') returned {got!r}"
        ''',
        "solution": r'''
            def shout(text):
                return text + "!"
        ''',
        "hints": [
            "Read the error: it names the line and says an indented block was expected.",
            "The return line belongs to the function, so it must be pushed in under the def line.",
            "Put 4 spaces at the start of the return line. Don't change anything else.",
        ],
    },
    {
        "id": "basics-1",
        "title": "Count the characters",
        "difficulty": 1,
        "lesson": r'''
            Python comes with a toolbox of ready-made functions called **built-ins**. You call them
            like your own functions: name, parentheses, inputs inside.

            ```python
            print(len("hello"))
            print(max(3, 9, 4))
            print(min(3, 9, 4))
            ```

            - `len(text)` counts the characters in a text, spaces and punctuation included.
            - `max(...)` gives the biggest of its inputs, `min(...)` the smallest.

            You can use a built-in inside your own function and return what it gives back:

            ```python
            def biggest(a, b):
                return max(a, b)

            print(biggest(7, 12))
            ```

            Vocabulary: when a function gives a value back, people say it *returns* that value, and
            calling `len("hello")` *evaluates to* `5`.

            Watch out: `len` counts characters in text. `len(5)` (a number) is an error.
        ''',
        "prompt": r'''
            Before sending a prompt to a model you often check how long it is.

            **Write:** `prompt_length(prompt)`

            - `prompt`: a piece of text (a *string*), e.g. `"hello"`
            - **Returns:** the number of characters in `prompt`, as a whole number, e.g. `5`

            **Rules**
            - Every character counts, including spaces and punctuation.
            - An empty text `""` has length `0`.
            - Return the number (don't print it). A built-in function can do the counting for you.

            **Examples**
            ```python
            prompt_length("hello")            # returns 5
            prompt_length("Summarize this")   # returns 14 (the space counts)
            prompt_length("")                 # returns 0
            ```
        ''',
        "starter": r'''
            def prompt_length(prompt):
                ...
        ''',
        "tests": r'''
            from solution import prompt_length

            def test_hello_has_5_characters():
                got = prompt_length("hello")
                assert got == 5, f"prompt_length('hello') returned {got!r}"

            def test_spaces_count_as_characters():
                got = prompt_length("Summarize this")
                assert got == 14, f"prompt_length('Summarize this') returned {got!r}"

            def test_empty_prompt_returns_zero():
                got = prompt_length("")
                assert got == 0, f"prompt_length('') returned {got!r}"
        ''',
        "solution": r'''
            def prompt_length(prompt):
                return len(prompt)
        ''',
        "hints": [
            "The lesson shows a built-in function that counts characters in text.",
            "Call that built-in on the parameter prompt and return what it gives back.",
            "Write return, then len, then the parameter name prompt inside the parentheses.",
        ],
    },
    {
        "id": "basics-4",
        "title": "Read the failing check",
        "difficulty": 1,
        "lesson": r'''
            When your code runs but gives the wrong answer, there is no error message. Instead
            the **check** tells you what happened, like a teacher writing next to your sum:
            "you said -70, look again".

            A failing check reads like this:

            ```text
            FAIL  subtracts used from limit
                  tokens_left(100, 30) returned -70
            ```

            Read it as three facts:
            1. **What was tested**: the check's name, "subtracts used from limit".
            2. **The call**: your function was called with `100` and `30`.
            3. **What came back**: `-70`.

            Now compare with the Examples in the task. If the task says `tokens_left(100, 30)`
            should be `70`, the sign is flipped - so the subtraction is the wrong way round.

            You can test the same call yourself: add a `print(...)` of the call at the bottom
            of the file and press Run.

            ```python
            def gap(a, b):
                return a - b

            print(gap(100, 30))
            print(gap(30, 100))
            ```

            Vocabulary: a wrong result without an error is called a *logic error* (or just a
            *bug*).
        ''',
        "prompt": r'''
            Your app tracks how many tokens are left in a limit. The code runs, but Check fails.
            Press **Check** first and read the message, then fix the one bug.

            **Fix:** `tokens_left(limit, used)`

            - `limit`: the token limit, an int, e.g. `100`
            - `used`: tokens already used, an int, e.g. `30`
            - **Returns:** the tokens left: `limit` minus `used`, as an int, e.g. `70`

            **Rules**
            - If `used` is bigger than `limit`, return the negative number (e.g. `-15`).
            - Using exactly the limit leaves `0`.

            **Examples**
            ```python
            tokens_left(100, 30)   # returns 70
            tokens_left(50, 50)    # returns 0
            tokens_left(10, 25)    # returns -15
            ```
        ''',
        "starter": r'''
            def tokens_left(limit, used):
                return used - limit
        ''',
        "tests": r'''
            from solution import tokens_left

            def test_subtracts_used_from_limit():
                got = tokens_left(100, 30)
                assert got == 70, f"tokens_left(100, 30) returned {got!r}"

            def test_using_the_whole_limit_leaves_zero():
                got = tokens_left(50, 50)
                assert got == 0, f"tokens_left(50, 50) returned {got!r}"

            def test_overuse_gives_a_negative_number():
                got = tokens_left(10, 25)
                assert got == -15, f"tokens_left(10, 25) returned {got!r}"
        ''',
        "solution": r'''
            def tokens_left(limit, used):
                return limit - used
        ''',
        "hints": [
            "Compare what the failing check says your function returned with the value in the Examples.",
            "The number has the right size but the wrong sign. Which value should come first in the subtraction?",
            "Swap the two names around the minus sign so it reads limit minus used.",
        ],
    },
    {
        "id": "basics-2",
        "title": "Fix the broken welcome",
        "difficulty": 1,
        "lesson": r'''
            Error messages are not scary - they are **a note from Python pointing at the problem**.
            Read them from the bottom: the last line says what went wrong, and the message also
            names the **line number**.

            ```text
            SyntaxError in solution.py line 1: expected ':'
                def add(a, b)
            ```

            The three errors you will meet most on day one:

            - `SyntaxError: expected ':'` - something is missing, often the colon at the end of a `def` line.
            - `IndentationError: expected an indented block` - the body of a function is not indented.
            - `NameError: name 'Total' is not defined` - you used a name Python has never seen.
              Names are case-sensitive: `Total` and `total` are different names.

            ```python
            text = "hello"
            print(text)
            # print(Text)  <- this would be a NameError: capital T
            ```

            Fix one error, run again, read the next one. Errors often come one at a time.

            Vocabulary: a *syntax error* means the code breaks Python's grammar, so nothing runs at all.
        ''',
        "prompt": r'''
            A greeting for a new user of your AI app. The file has **three** small bugs.
            Press **Check** (or **Run**) and read each error message: it tells you the line
            number and what is wrong. Fix one, check again, repeat.

            **Fix:** `welcome(name)`

            - `name`: the user's name (a string), e.g. `"Ada"`
            - **Returns:** the text `Welcome, ` then the name then `!`, e.g. `"Welcome, Ada!"`

            **Rules**
            - Keep the exact format: `Welcome,` + one space + the name + `!` (no space before `!`).
            - It must work for any name, not just `"Ada"`.

            **Examples**
            ```python
            welcome("Ada")    # returns "Welcome, Ada!"
            welcome("team")   # returns "Welcome, team!"
            ```
        ''',
        "starter": r'''
            def welcome(name)
            return "Welcome, " + Name + "!"
        ''',
        "tests": r'''
            from solution import welcome

            def test_welcomes_ada_with_exact_format():
                got = welcome("Ada")
                assert got == "Welcome, Ada!", f"welcome('Ada') returned {got!r}"

            def test_works_for_any_name():
                got = welcome("team")
                assert got == "Welcome, team!", f"welcome('team') returned {got!r}"
        ''',
        "solution": r'''
            def welcome(name):
                return "Welcome, " + name + "!"
        ''',
        "hints": [
            "Read the error message: it gives a line number and says what Python expected there.",
            "The def line is missing something at its end, the body is not indented, and one name does not match the parameter (capital letters matter).",
            "1) Add a colon at the end of the def line. 2) Indent the return line by 4 spaces. 3) Use the parameter exactly as it is spelled in the def line.",
        ],
    },
    {
        "id": "basics-5",
        "title": "Round a score",
        "difficulty": 1,
        "lesson": r'''
            Nobody memorises every tool. Real engineers **look things up** all the time, the
            way a cook checks a recipe book. Python's official docs at docs.python.org describe
            every built-in: what inputs it takes and what it gives back.

            A doc entry starts with a *signature*, like `round(number, ndigits=None)`. It tells
            you the function's name and its inputs. An input shown with `=` has a default, so
            you may leave it out:

            ```python
            print(round(2.567))
            print(max(3, 9, 4))
            ```

            `round(2.567)` gives the nearest whole number, `3`. The docs tell you what the
            second input changes - that is exactly what this step asks you to find out.

            Vocabulary: an input you may leave out is an *optional argument*. The text
            explaining a function is its *documentation* (or *docs*).

            Watch out: a function's name, its parentheses and the order of its inputs must
            match the docs exactly.
        ''',
        "research": {
            "note": "Read the entry for the built-in round() - especially what its second input (ndigits) does - then come back.",
            "links": [
                {"title": "round() - Python docs", "url": "https://docs.python.org/3/library/functions.html#round"},
            ],
        },
        "prompt": r'''
            An eval tool gives long scores like `0.87654`. Your dashboard shows them with
            2 decimal places.

            **Write:** `short_score(score)`

            - `score`: a decimal number, e.g. `0.87654`
            - **Returns:** `score` rounded to **2** decimal places, as a number (not text), e.g. `0.88`

            **Rules**
            - Return the number, don't print it.
            - Numbers with fewer decimals stay the same: `0.5` gives `0.5`.

            **Examples**
            ```python
            short_score(0.87654)   # returns 0.88
            short_score(0.123)     # returns 0.12
            short_score(0.5)       # returns 0.5
            ```
        ''',
        "starter": r'''
            def short_score(score):
                ...
        ''',
        "tests": r'''
            from solution import short_score

            def test_rounds_up_to_two_decimals():
                got = short_score(0.87654)
                assert got == 0.88, f"short_score(0.87654) returned {got!r}"

            def test_rounds_down_to_two_decimals():
                got = short_score(0.123)
                assert got == 0.12, f"short_score(0.123) returned {got!r}"

            def test_short_numbers_stay_the_same():
                got = short_score(0.5)
                assert got == 0.5, f"short_score(0.5) returned {got!r}"
                assert not isinstance(got, str), "return a number, not text"
        ''',
        "solution": r'''
            def short_score(score):
                return round(score, 2)
        ''',
        "hints": [
            "The built-in round() can do this; its docs explain the second input.",
            "Call round with the score first and the number of decimal places second, and return the result.",
            "Write return, then round, then in the parentheses: the parameter score, a comma, and 2.",
        ],
    },
    {
        "id": "basics-3",
        "title": "Credits for a request",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            An AI service charges **credits**: each prompt token (text you send) costs 2
            credits and each output token (text the model writes back) costs 6 credits.

            **Write** three things in `solution.py`:

            1. `prompt_cost(tokens)`
               - `tokens`: number of prompt tokens (an int), e.g. `10`
               - **Returns:** the credits for those prompt tokens (an int), e.g. `20`
            2. `request_cost(prompt_tokens, output_tokens)`
               - `prompt_tokens`: number of prompt tokens (an int), e.g. `10`
               - `output_tokens`: number of output tokens (an int), e.g. `1`
               - **Returns:** the total credits for one request (an int), e.g. `26`
            3. A `print(...)` line at the bottom of the file, **not indented** (outside both functions).

            **Rules**
            - `request_cost` must **call `prompt_cost(...)`** to work out the prompt part (a check looks for that call).
            - Zero tokens cost `0` credits.
            - The bottom line prints the cost of a request with 1000 prompt tokens and 200 output
              tokens. Running the file must print **only** that number, nothing else.

            **Examples**
            ```python
            prompt_cost(10)           # returns 20
            prompt_cost(0)            # returns 0
            request_cost(10, 1)       # returns 26
            request_cost(0, 5)        # returns 30
            ```

            Running `python3 solution.py` prints:
            ```
            3200
            ```
        ''',
        "starter": r'''
            # write prompt_cost, then request_cost, then print one result
        ''',
        "tests": r'''
            import ast
            from solution import prompt_cost, request_cost

            def test_prompt_cost_is_2_credits_per_token():
                got = prompt_cost(10)
                assert got == 20, f"prompt_cost(10) returned {got!r}"
                assert prompt_cost(0) == 0, f"prompt_cost(0) returned {prompt_cost(0)!r}"

            def test_request_cost_adds_prompt_and_output_credits():
                got = request_cost(10, 1)
                assert got == 26, f"request_cost(10, 1) returned {got!r}"
                got = request_cost(0, 5)
                assert got == 30, f"request_cost(0, 5) returned {got!r}"

            def test_request_cost_calls_prompt_cost():
                tree = ast.parse(source())
                fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "request_cost"][0]
                calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                         and isinstance(n.func, ast.Name) and n.func.id == "prompt_cost"]
                assert calls, "request_cost should call prompt_cost(...) for the prompt part"

            def test_running_the_file_prints_only_3200():
                r = run_script()
                assert r.returncode == 0, r.stderr
                assert r.stdout.strip() == "3200", f"running the file printed {r.stdout!r}"
        ''',
        "solution": r'''
            def prompt_cost(tokens):
                return tokens * 2


            def request_cost(prompt_tokens, output_tokens):
                return prompt_cost(prompt_tokens) + output_tokens * 6


            print(request_cost(1000, 200))
        ''',
        "hints": [
            "You need two def blocks and one print at the left edge of the file. A function can call another function.",
            "prompt_cost multiplies its input by 2. request_cost adds prompt_cost(prompt_tokens) to the output tokens times 6. The print calls request_cost with 1000 and 200.",
            "1) def prompt_cost(tokens): with an indented return of tokens * 2. 2) def request_cost(prompt_tokens, output_tokens): with an indented return that adds the prompt_cost call and output_tokens * 6. 3) An unindented print of request_cost(1000, 200). Press Run to see 3200.",
        ],
    },
    {
        "id": "basics-6",
        "title": "Longest prompt",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: calls can be nested inside other calls. Python works from
            the inside out - it finishes the inner calls first, then passes their results to
            the outer one.

            ```python
            print(min(len("abc"), len("hi")))
            ```
        ''',
        "prompt": r'''
            You have three candidate prompts and want to know how long the longest one is.

            **Write:** `longest_length(a, b, c)`

            - `a`, `b`, `c`: three strings, e.g. `"hi"`, `"hello"`, `"hey"`
            - **Returns:** an int: the number of characters in the longest of the three, e.g. `5`

            **Rules**
            - Return the length (a number), not the text itself.
            - If all three are empty, return `0`.
            - If several are equally long, return that length.

            **Examples**
            ```python
            longest_length("hi", "hello", "hey")   # returns 5
            longest_length("ab", "cd", "ef")       # returns 2
            longest_length("", "", "")             # returns 0
            ```
        ''',
        "starter": r'''
            def longest_length(a, b, c):
                ...
        ''',
        "tests": r'''
            from solution import longest_length

            def test_returns_length_of_longest():
                got = longest_length("hi", "hello", "hey")
                assert got == 5, f"longest_length('hi', 'hello', 'hey') returned {got!r}"

            def test_longest_can_be_in_any_position():
                got = longest_length("summarize this", "hi", "ok")
                assert got == 14, f"longest_length('summarize this', 'hi', 'ok') returned {got!r}"
                got = longest_length("a", "b", "tokens")
                assert got == 6, f"longest_length('a', 'b', 'tokens') returned {got!r}"

            def test_equal_lengths():
                got = longest_length("ab", "cd", "ef")
                assert got == 2, f"longest_length('ab', 'cd', 'ef') returned {got!r}"

            def test_all_empty_returns_zero():
                got = longest_length("", "", "")
                assert got == 0, f"longest_length('', '', '') returned {got!r}"
        ''',
        "solution": r'''
            def longest_length(a, b, c):
                return max(len(a), len(b), len(c))
        ''',
        "hints": [
            "Two built-ins do all the work: one counts characters, one picks the biggest number.",
            "Get the length of each of the three texts, then pick the biggest of those three numbers.",
            "Return max(...) with three arguments inside: len of a, len of b, and len of c.",
        ],
    },
]
