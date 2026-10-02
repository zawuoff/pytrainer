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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["print", "output", "comment", "string", "function", "call", "argument",
                 "parameter", "def", "return", "indentation", "len", "none", "nameerror",
                 "syntaxerror", "indentationerror"],
    "cards": [
        {
            "syntax": "print(value, value)",
            "explain": "Writes the values on one line of output, with one space between them.",
            "example": r'''
                print("Hello, AI!")
                # Hello, AI!
                print("tokens:", 2 + 3)
                # tokens: 5
            ''',
        },
        {
            "syntax": '"text" + "text"',
            "explain": "Between two strings, + joins them into one new string. Between two numbers, + adds them.",
            "example": r'''
                print("Hello, " + "Ada" + "!")
                # Hello, Ada!
                print("2" + "3")
                # 23
                print(2 + 3)
                # 5
            ''',
        },
        {
            "syntax": "name(argument, argument)",
            "explain": "Calls a function with input values. An inner call runs first and its result is passed on.",
            "example": r'''
                print(len("hi there"))
                # 8
                print(max(3, 9, 4))
                # 9
                print(round(2.567, 1))
                # 2.6
            ''',
        },
        {
            "syntax": "def name(parameter):",
            "explain": "Defines a function. The indented lines are its body. They run each time the function is called.",
            "example": r'''
                def double(n):
                    return n * 2

                print(double(4))
                # 8
                print(double(10))
                # 20
            ''',
        },
        {
            "syntax": "return value",
            "explain": "Ends the function and sends value to the code that called it. Without return, the call gives None.",
            "example": r'''
                def shows(n):
                    print(n + 1)

                result = shows(4)
                # 5
                print(result)
                # None
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Python Basics

### Running code

A **program** is a text file of instructions. Python runs it from top to bottom, one line
at a time. **Run** (Alt+Enter) runs your file and shows its **output**: the text it prints.
**Check** (Ctrl+Enter) runs the **tests** of the step. A test is a small piece of code that
uses your code and compares the result with the expected result. Each test is listed as a
**check** that passes or fails.

### print()

`print()` writes values to the screen. A **value** is a piece of data, such as a number or
a piece of text. A piece of text is called a **string**. Strings go inside quotes and
numbers do not. Commas between values put one space between them in the output. Each
`print(...)` writes one line.

```python
print("Hello, AI!")
# Hello, AI!
print("tokens:", 2 + 3)
# tokens: 5
```

### Comments

A **comment** starts with `#`. Python ignores everything after `#` on that line.

### Strings and numbers

`+` adds two numbers. `+` joins two strings end to end.

```python
print(2 + 3)
# 5
print("2" + "3")
# 23
```

### Calling a function

A **function** is a named piece of code that takes input values and produces a result. To
use a function, you **call** it. A call is the function name followed by parentheses that
hold the input values. The input values are called **arguments**. `print` is a function, and
`print("hi")` is a call with one argument.

A call can be written inside another call. Python runs the inner call first and passes its
result to the outer call as an argument.

```python
print(len("hello"))
# 5
print(max(3, 9, 4))
# 9
print(round(2.567, 1))
# 2.6
```

`len` counts the characters in a string. `max` gives the largest of its arguments. `round`
rounds a number, here to 1 digit after the decimal point.

### Defining a function

You can write your own functions. Almost every exercise asks you to define a function with
`def` and `return`.

```python
def add(a, b):
    return a + b

print("start")
print(add(2, 3))
print(add(100, 28))
```

- The `def name(parameters):` line ends with a colon.
- The lines that belong to the function start with 4 spaces. Spaces at the start of a line are called **indentation**.
- `return value` ends the function and sends `value` back to the code that called it.
- `a` and `b` are **parameters**. Each call sets them to the arguments of that call.

Step through the program to see which line runs next and what `a` and `b` are in each call.

```diagram
{"type": "trace", "title": "Defining add and calling it twice", "code": ["def add(a, b):", "    return a + b", "", "print(\"start\")", "print(add(2, 3))", "print(add(100, 28))"], "steps": [
  {"line": 1, "vars": {}, "out": "", "note": "The def line creates the function. It does not run the indented line."},
  {"line": 4, "vars": {}, "out": ""},
  {"line": 5, "vars": {}, "out": "start\n"},
  {"line": 2, "vars": {"a": "2", "b": "3"}, "out": "start\n", "note": "The call add(2, 3) sets a to 2 and b to 3."},
  {"line": 6, "vars": {}, "out": "start\n5\n"},
  {"line": 2, "vars": {"a": "100", "b": "28"}, "out": "start\n5\n"},
  {"line": null, "vars": {}, "out": "start\n5\n128\n"}
]}
```

### return and print

`print` only writes text to the screen. `return` sends the value back to the code that called
the function. The tests are that code, so they need a `return`. A function that ends without
`return` returns `None`, the value Python uses for "no value".

### Common mistakes

An error message names the file, the **line number** and the problem.

- `SyntaxError: expected ':'` means a colon is missing on that line.
- `IndentationError: expected an indented block` means the lines under `def` are not indented.
- `NameError: name 'Name' is not defined` means a name is misspelled or its capital letters do not match.

A failing check such as `add(2, 3) returned None` means the test called your function with
those arguments and got that value back. `None` almost always means a missing `return`.

Anything inside quotes is a string. `print("2 + 3")` prints the characters `2 + 3` and does no maths.

### Docs

Every built-in function (built-in means it comes with Python, with no setup needed)
has an entry at docs.python.org, on the page *Built-in Functions*.
Reading these entries is a normal part of an engineer's work.
'''

EXERCISES = [
    {
        "id": "basics-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## print() and comments

            A **program** is a text file of instructions. Python runs it from the top, one line at a
            time. Each instruction is called a **statement**.

            `print()` writes a value to the screen. A **value** is a piece of data, such as a number
            or a piece of text. You put the value between the parentheses.

            - Text goes inside quotes. Text in quotes is called a **string**.
            - Python calculates a sum such as `2 + 3` first and prints the result, not the sum.
            - Commas separate several values. Python prints them on one line with one space between them.

            ```python
            print("Hello, AI!")
            # Hello, AI!
            print(2 + 3)
            # 5
            print("tokens:", 120)
            # tokens: 120
            ```

            The lines that start with `#` are **comments**: notes for the people who read the code.
            Python ignores everything from the `#` to the end of the line. In these lessons, a comment
            under a `print` shows what that `print` writes.

            The examples use words from AI work, such as `tokens`. A **token** is a small piece of text
            that an AI model reads. Here it is only a label, and you need no AI knowledge to follow the code.

            A comment is ignored even when its text is valid code.

            ```python
            print("loading model")
            # print("skipped")
            print(2 + 3)
            print("tokens:", 120)
            ```

            Step through the program. Line 2 never becomes the next line to run.

            ```diagram
            {"type": "trace", "title": "Python skips the comment on line 2", "code": ["print(\"loading model\")", "# print(\"skipped\")", "print(2 + 3)", "print(\"tokens:\", 120)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 3, "vars": {}, "out": "loading model\n", "note": "Line 2 is a comment, so Python goes from line 1 to line 3."},
              {"line": 4, "vars": {}, "out": "loading model\n5\n"},
              {"line": null, "vars": {}, "out": "loading model\n5\ntokens: 120\n"}
            ]}
            ```

            A comment prints nothing. This program has four lines and prints three lines.
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
            ## Scripts and output

            A **script** is a file of Python code that does its work when you run it. Python runs the
            statements in the file from top to bottom.

            Writing `print(...)` runs the `print` function. This is called a **call** to `print`. Each call
            writes one line. Two calls write two lines, in the order they appear in the file.

            ```python
            print("loading model")
            # loading model
            print("done")
            # done
            ```

            The text a program prints is called its **output**. You will also see the name **stdout**,
            which is another name for the output.

            The **Run** button (Alt+Enter) runs your file and shows its output. The **Check** button
            (Ctrl+Enter) runs the **checks** of the step: small tests that decide whether your code
            does what the task asks. Press Run before you press Check, and compare your output with
            the output the task asks for.

            A check of a script compares the output character by character. Capital letters, spelling and spaces
            all count. `Ready` and `ready` are different strings, so one does not pass for the other.
        ''',
        "prompt": r'''
            A *script* is a file that does its work when you run it. No function is needed.

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
            ## Strings and numbers

            A **string** is a piece of text: a sequence of characters. You write a string inside
            quotes. A number is written without quotes. A whole number is called an **integer**, or
            **int**.

            The `+` sign does a different thing for each kind of value. Between two numbers, it adds
            them. Between two strings, it joins them end to end into one new string. Joining strings
            is called **concatenation**.

            ```python
            print(7 + 1)
            # 8
            print("7" + "1")
            # 71
            ```

            `"7"` is a string that contains the character `7`. It is not the number `7`. So
            `"7" + "1"` joins two characters and gives the string `"71"`.

            Concatenation builds a message from parts. Python adds no spaces between the parts, so
            any space must be inside one of the strings.

            ```python
            print("Hello, " + "Ada" + "!")
            # Hello, Ada!
            ```

            Python does no maths on the characters inside quotes. `print("7 + 1")` prints the
            characters `7 + 1` exactly as written.
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
            `2 + 3` adds two numbers. `"2" + "3"` joins two strings into `23`. `"2 + 3"` is one
            string, so Python prints it exactly as written. The last line joins three strings,
            and the middle one is a single space.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Look for quotes: values in quotes are text, values without quotes are numbers.",
            "+ adds numbers but joins text end to end. Text inside quotes is printed exactly as written.",
            "Line 1: the sum. Line 2: the two characters joined together. Line 3: the text between the quotes. Line 4: the three pieces joined, including the space.",
        ],
    },
    {
        "id": "basics-s7",
        "title": "Call a built-in",
        "difficulty": 0,
        "mode": "script",
        "lesson": r'''
            ## Calling a built-in function

            A **function** is a named piece of code that takes input values and produces a result.
            Python comes with many functions that are ready to use. They are called **built-in
            functions**, or **built-ins**. `print` is one of them.

            To use a function, you **call** it: you write its name, then parentheses with the input
            inside. An input value that you pass in a call is called an **argument**.

            `len()` is a built-in that counts the characters in a string.

            ```python
            print(len("hello"))
            # 5
            print(len("hi there"))
            # 8
            ```

            `"hi there"` has 8 characters because the space counts as a character.

            `print(len("hello"))` contains two calls. Python runs the inner call first:
            `len("hello")` produces `5`. Then Python calls `print` with `5` as its argument.

            Do not count the characters by hand and type the number. Call `len`, and Python counts
            them when the program runs.
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
            ## def and return

            You can define your own functions. Almost every exercise here asks you to write one. The
            checks then call your function and compare the value it produces with the expected value.

            ```python
            def model_name():
                return "gpt-4o-mini"

            print(model_name())
            # gpt-4o-mini
            ```

            - `def model_name():` defines a function named `model_name`. The line ends with a colon `:`.
            - The next line starts with 4 spaces. Spaces at the start of a line are called **indentation**. The indentation tells Python that the line is part of the function.
            - `return` ends the function and sends a value back to the code that called it. That value is called the **return value**.

            The `def` statement creates the function. It does not run it. `model_name()` is the name
            plus parentheses, and that calls the function: Python runs the indented line, and the
            call produces the return value `"gpt-4o-mini"`. `print` then writes it to the screen.

            A string must be inside quotes. Without quotes, `Hello` is read as a **name**, like the
            name `model_name` above. With `return Hello`, Python looks for something called
            `Hello`. No such name exists, so the call stops with `NameError: name 'Hello' is not defined`.
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
            ## Parameters and arguments

            A function can take inputs. You name the inputs inside the parentheses of the `def` line.
            These names are called **parameters**.

            ```python
            def double(n):
                return n * 2

            print(double(4))
            # 8
            print(double(10))
            # 20
            ```

            `n` is a parameter. The values `4` and `10` are **arguments**: the values you pass in a
            call. For each call, Python sets `n` to the argument and then runs the indented line.
            `*` means multiply, so `n * 2` is `n` times 2. `double(4)` runs with `n` set to `4`. `double(10)` runs again with `n` set to `10`.

            Step through the program to see the value of `n` in each call.

            ```diagram
            {"type": "trace", "title": "Each call sets the parameter n", "code": ["def double(n):", "    return n * 2", "", "print(double(4))", "print(double(10))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 4, "vars": {}, "out": ""},
              {"line": 2, "vars": {"n": "4"}, "out": "", "note": "The call double(4) sets n to 4."},
              {"line": 5, "vars": {}, "out": "8\n"},
              {"line": 2, "vars": {"n": "10"}, "out": "8\n", "note": "The call double(10) sets n to 10."},
              {"line": null, "vars": {}, "out": "8\n20\n"}
            ]}
            ```

            A function can have several parameters, separated by commas. Python matches the arguments
            to the parameters by position: the first argument goes to the first parameter.

            ```python
            def area(width, height):
                return width * height

            print(area(3, 5))
            # 15
            ```

            The arithmetic signs are `+` for add, `-` for subtract, `*` for multiply and `/` for divide.

            Use the parameter names in the function, not fixed numbers. A function that contains
            `return 4 * 2` returns `8` for every call, whatever argument you pass.
        ''',
        "prompt": r'''
            Your first real function: it takes two numbers and hands back their total.

            **Write:** the body of `add(a, b)` (the `def` line is already there)

            - `a`: a whole number (an *int*), e.g. `2`
            - `b`: another whole number, e.g. `3`
            - **Returns:** the sum `a + b`, as a number (not text), e.g. `5`

            **Rules**
            - **Return** the result (don't just `print` it): the checks call `add(...)` and look at what comes back.
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
            ## print is not return

            `print` and `return` do different things. `print` writes a value to the screen. The code
            that called the function receives nothing from it. `return` sends the value back to the
            code that called the function, so that code can use the value.

            The checks call your function and compare its return value with the expected value. They
            do not read what your function prints.

            ```python
            def shows(n):
                print(n * 2)

            def gives(n):
                return n * 2

            print(gives(4))
            # 8
            print(shows(4))
            # 8
            # None
            ```

            `print(gives(4))` writes `8`, the return value of `gives`.

            `print(shows(4))` writes two lines. First the `print` inside `shows` writes `8`. Then
            `shows` ends without a `return`, so the call produces `None`, and the outer `print`
            writes `None`.

            **`None`** is the value Python uses for "no value". A function that ends without `return`
            returns `None`.

            Step through the program and watch when each line of output appears.

            ```diagram
            {"type": "trace", "title": "A function without return gives None", "code": ["def shows(n):", "    print(n * 2)", "", "def gives(n):", "    return n * 2", "", "print(gives(4))", "print(shows(4))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 4, "vars": {}, "out": ""},
              {"line": 7, "vars": {}, "out": ""},
              {"line": 5, "vars": {"n": "4"}, "out": "", "note": "gives returns 8 to line 7, and line 7 prints it."},
              {"line": 8, "vars": {}, "out": "8\n"},
              {"line": 2, "vars": {"n": "4"}, "out": "8\n", "note": "shows prints 8 itself and then ends with no return."},
              {"line": null, "vars": {}, "out": "8\n8\nNone\n", "note": "The call shows(4) produced None, so line 8 printed None."}
            ]}
            ```

            A check message like `double(4) returned None` means the check called the function with
            `4` and got `None` back. The usual cause is a missing `return`.
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
            ## Indentation

            **Indentation** is the spaces at the start of a line. Python uses indentation to decide
            which lines belong to a function. The lines that belong to a function are called its
            **body**. You indent each of them by 4 spaces under the `def` line.

            ```python
            def excited(text):
                return text + "!"

            print(excited("ready"))
            # ready!
            ```

            The `return` line is indented, so it is part of `excited`. The `print` line starts at
            the left edge, so it is not part of the function. It runs when Python reaches it in the file.

            If the line after `def` is not indented, Python stops before it runs any line and reports
            this error:

            ```text
            IndentationError: expected an indented block after function definition on line 1
            ```

            A group of lines with the same indentation is called a **block**. The error says that
            Python expected a block after the `def` line and did not find one.

            Use the same indentation, 4 spaces, for every line in a block.
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
            ## Built-ins inside your functions

            Python's **built-in functions** are available in every program without any setup. You
            call them the same way you call your own functions: the name, then parentheses with the
            arguments inside.

            ```python
            print(len("hello"))
            # 5
            print(max(3, 9, 4))
            # 9
            print(min(3, 9, 4))
            # 3
            ```

            - `len(text)` returns the number of characters in a string. Spaces and punctuation count.
            - `max(...)` returns the largest of its arguments. `min(...)` returns the smallest.

            You can call a built-in inside your own function and return its result.

            ```python
            def biggest(a, b):
                return max(a, b)

            print(biggest(7, 12))
            # 12
            ```

            When a call produces a value, you say the call **evaluates to** that value.
            `len("hello")` evaluates to `5`.

            `len` does not accept a number. `len(5)` stops the program with
            `TypeError: object of type 'int' has no len()`. A `TypeError` means the operation
            does not work for that kind of value.
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
            ## Reading a failing check

            Code can run without an error and still return the wrong value. This is called a
            **logic error**, or a **bug**. Python shows no error message for it. The failing
            **check** tells you what happened.

            ```text
            FAIL  subtracts used from limit
                  tokens_left(100, 30) returned -70
            ```

            The message contains three facts:

            1. **What was tested**: the name of the check, "subtracts used from limit".
            2. **The call**: the check called your function with the arguments `100` and `30`.
            3. **The return value**: your function returned `-70`.

            Compare the return value with the Examples in the task. The task says that
            `tokens_left(100, 30)` returns `70`. The digits are right and the sign is wrong. That
            happens when the two values of a subtraction are in the wrong order.

            You can run the same call yourself. Add a `print(...)` of the call at the bottom of the
            file and press Run.

            ```python
            def gap(a, b):
                return a - b

            print(gap(100, 30))
            # 70
            print(gap(30, 100))
            # -70
            ```

            Subtraction depends on the order of its values. `a - b` and `b - a` have opposite signs.
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
            ## Reading error messages

            When Python cannot run your code, it prints an **error message**. The message names the
            file, the **line number** and the problem. When the message has several lines, find the line
            with the error name, such as `SyntaxError`: it states what went wrong.

            ```text
            SyntaxError in solution.py line 1: expected ':'
                def add(a, b)
            ```

            A **syntax error** means the code breaks the grammar rules of Python. Python reads the
            whole file before it runs it, so with a syntax error no line runs at all.

            These are the three errors you see most often at the start:

            - `SyntaxError: expected ':'` means a colon `:` is missing on that line. Often it is the colon at the end of a `def` line.
            - `IndentationError: expected an indented block` means the body of a function is not indented.
            - `NameError: name 'Total' is not defined` means you used a name that Python does not know. A name is a word in your code, such as `print`, `add` or a parameter name like `total`.

            Names are **case-sensitive**: an uppercase letter and its lowercase letter are different
            characters. `total` and `Total` are two different names.

            ```python
            def show(total):
                return total

            print(show(5))
            # 5
            ```

            With `return Total` in the body, the call stops with
            `NameError: name 'Total' is not defined. Did you mean: 'total'?`.

            Fix one error, run again and read the next message. Python reports one error at a time.
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
            ## Reading the docs

            Python's official **documentation**, or **docs**, is at docs.python.org. It describes
            every built-in function: the arguments it takes and the value it returns. Engineers look
            functions up there all the time. You do not need to memorise them.

            A docs entry starts with a **signature**: the function's name followed by its parameters
            in parentheses. The signature of `round` is `round(number, ndigits=None)`.

            A parameter written with `=` has a **default value**. Python uses the default when you
            leave that argument out. An argument that you may leave out is called an **optional argument**.

            ```python
            print(round(2.567))
            # 3
            print(max(3, 9, 4))
            # 9
            ```

            `round(2.567)` passes one argument, so `ndigits` keeps its default. The call returns the
            nearest whole number, `3`. The docs entry explains what a second argument changes. Read
            it to solve this step.

            In a call, the function's name and the order of the arguments must match the signature.
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
            ## Nested calls

            A call is **nested** when it is written inside the parentheses of another call. Python
            runs the inner calls first. Their return values become the arguments of the outer call.

            ```python
            print(min(len("abc"), len("hi")))
            # 2
            ```

            Python runs this line in three steps. `len("abc")` returns `3` and `len("hi")` returns
            `2`. Then `min(3, 2)` returns `2`. Then `print(2)` writes `2`.
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
