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
            ## Make Python show something on the screen

            A chat app shows you a reply. A calculator shows you a result. Whatever a program does, at some
            point it has to show something to a person. So that is the first thing you will tell Python to
            do. Python is a language for writing instructions that a computer can carry out.

            Here is a complete program. It is one line long.

            ```python
            print("Good morning")
            # Good morning
            ```

            `print` means "show this on the screen". What you want to show goes between the round brackets,
            which are called parentheses. The quotes mark where a piece of text starts and where it stops.
            They are not shown themselves.

            The second line is not an instruction. A line that starts with `#` is a note for the reader. In
            this course, a note under a `print` shows what that `print` puts on the screen.

            Instructions written down like this are a **program**. To **run** a program is to hand it to
            Python, which carries the instructions out. What the program shows is called its **output**.
            Run this one, then change it:

            ```try
            print("Good morning")
            ---
            Run the program. Then change the text between the quotes so that the output is `Good evening`, and run it again.
            ---
            print("Good evening")
            ---
            You changed the instruction, and the output changed with it. Edit, run, look: all programming is done in that loop.
            ```

            ### Numbers, and two things on one line

            ```python
            print(4 + 6)
            # 10
            print("messages:", 3)
            # messages: 3
            ```

            Numbers are written without quotes. Python works out `4 + 6` first and shows only the result,
            `10`. A comma lets one `print` show several things: Python puts them on one line with one space
            between them.

            Text in quotes has a name of its own. Programmers call it a **string**, because it is a string
            of characters: letters, digits, spaces and other signs, one after another.

            That program has two instructions. Python runs them from top to bottom, one at a time, and each
            `print` starts a new line of output.

            ### Lines that Python skips

            Python ignores everything from a `#` to the end of the line. Such a note is called a
            **comment**. A comment can explain the code. It can also switch an instruction off: put `#` in
            front of it and Python no longer runs it. Press Next below and watch the highlight jump over
            line 2. (Ignore the Variables box for now.)

            ```diagram
            {"type": "trace", "title": "Python skips the comment on line 2", "code": ["print(\"loading\")", "# print(\"skipped\")", "print(4 + 6)", "print(\"messages:\", 3)"], "steps": [
              {"line": 1, "vars": {}, "out": "", "note": "Nothing has run yet. Line 1 is the line Python runs next."},
              {"line": 3, "vars": {}, "out": "loading\n", "note": "Line 1 has run. Line 2 is a comment, so Python goes straight to line 3."},
              {"line": 4, "vars": {}, "out": "loading\n10\n", "note": "Python worked out 4 + 6 and showed the result on a new line."},
              {"line": null, "vars": {}, "out": "loading\n10\nmessages: 3\n", "note": "The program has finished. Four lines of code gave three lines of output."}
            ]}
            ```

            ```quiz
            How many lines of output does this program show?

            ~~~python
            print("one")
            # print("two")
            print(1 + 2)
            ~~~
            - [ ] 3 :: The middle line starts with `#`, so Python skips it. Only two instructions run.
            - [x] 2 :: Yes. The output is `one` and then `3`. The comment in the middle shows nothing.
            - [ ] 1 :: Each `print` that runs starts a new line of output, and two of them run here.
            ```

            **Watch out:** quotes and comments never reach the screen. `print("Good morning")` shows
            `Good morning` without the quotes, and a comment shows nothing at all, not even an empty line.

            **In short:** `print(...)` shows what is between its parentheses, Python runs the lines from top
            to bottom, and it skips everything after a `#`.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line, then press **Check**.
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
            Line 1 prints the text between the quotes, `Hello`, without the quotes. Line 2 starts with `#`,
            so it is a comment: Python skips it and `Goodbye` never appears. Line 3 has no quotes, so Python
            works out `2 + 3` and prints the result, `5`. Line 4 prints two things with a comma between
            them, so they appear on one line with one space in between: `tokens: 40`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Go through the program one line at a time, from the top. For each line, ask first: does Python run this line at all?",
            "A line that starts with `#` gives no output. Quotes are not part of the output. A sum without quotes is worked out before it is shown, and a comma between two things becomes one space.",
            "Your answer has three lines. The first is the text of line 1 without its quotes. The second is the result of the sum. The third is the text and the number from the last line, with one space between them.",
        ],
    },
    {
        "id": "basics-s4",
        "title": "Two lines of output",
        "difficulty": 0,
        "mode": "script",
        "lesson": r'''
            ## Write a program yourself and get it checked

            In the last step you read a program. Now you write one. Two things are new: how to get more
            than one line of output, and how the app decides whether your program is right.

            Start with the output. Each `print` gives one line, and the lines appear in the order in which
            the instructions are written:

            ```python
            print("loading model")
            # loading model
            print("done")
            # done
            ```

            Programmers call one instruction a **statement**. A file of statements that you run is called a
            **script**. Python always runs a script from the top line to the bottom line. Put these four
            statements in the order that counts down to `go`:

            ```order
            print("3")
            print("2")
            print("1")
            print("go")
            ---
            Python runs the statements from top to bottom, so the output appears in the same order as the lines of the script.
            ```

            ### Run and Check

            Your script lives in the editor next to this lesson. Two buttons work on it.

            **Run** runs the script and shows its output in the Output tab. Nothing is judged. Use it as
            often as you like to see what your code does.

            **Check** runs the step's **checks**. A check is a small test: it runs your script and compares
            what it printed with what the task asks for. The Results tab lists each check as passed or
            failed.

            A check compares the two texts one character at a time. A capital letter, a missing space or an
            extra full stop is enough to fail it.

            ```quiz
            A task asks for exactly this output: `all done`. Which statement passes the check?
            - [ ] `print("All done")` :: A capital `A` and a small `a` are different characters, so the output does not match.
            - [x] `print("all done")` :: Yes. Every character matches, including the space in the middle.
            - [ ] `print("all done.")` :: The full stop at the end is one character more than the task asks for.
            - [ ] `print("alldone")` :: The space is missing. A space is a character like any other.
            ```

            **Watch out:** if you leave out a quote or a parenthesis, Python cannot read the line. It shows
            an error message instead of your output, for example `SyntaxError: '(' was never closed`.
            Nothing is broken. The message names the line, so look at that line, add what is missing and
            run again.

            **In short:** write one `print` for each line of output, in the order you want them, and make
            the output match the task character for character.
        ''',
        "prompt": r'''
            Many programs say something when they start, so that you know they are working. This one
            announces the name of the app and then says that it is ready.

            **Your job:** write a script that prints two lines: the name of this app, then the word `ready`.
            The editor starts with a comment that marks where your code goes. You may delete it or leave it.

            **What comes out**
            - line 1 of the output: `PyTrainer`
            - line 2 of the output: `ready`

            **Rules**
            - The text must match exactly. `PyTrainer` has a capital `P` and a capital `T`. `ready` is all
              small letters.
            - The output is these two lines and nothing else.
            - The script must run without an error.

            **Examples**

            Running the script prints:
            ```text
            PyTrainer
            ready
            ```

            Press **Run** to see your output, and press **Check** when it looks right.
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
            "Look at the first example in the lesson. How many lines of output does one `print` give?",
            "You need one statement for each line of output, written in the same order as the output. The text to show goes inside quotes.",
            "Write a `print` for the name of the app, then a second `print` under it for the second word. Press Run and compare your output with the Examples letter by letter, capitals included.",
        ],
    },
    {
        "id": "basics-s6",
        "title": "Text or number?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Why quotes change what + does

            A chat app shows `You have 3 new messages`. Most of that line is fixed text, and one part is a
            number that the program worked out. Python treats text and numbers differently, and the quotes
            are how it tells them apart. The `+` sign shows the difference most clearly.

            ```python
            print(7 + 1)
            # 8
            print("7" + "1")
            # 71
            ```

            Without quotes, `7` and `1` are numbers, and `+` adds them. With quotes, `"7"` and `"1"` are
            strings: pieces of text that happen to contain a digit. Between two strings, `+` does not add.
            It glues the second string onto the end of the first, so you get the string `71`.

            Gluing strings together is called **concatenation**. And anything a program can work with, such
            as a number or a string, is called a **value**. So `+` does a different job for each kind of
            value.

            ### Building a message from parts

            Concatenation is how a program builds a line of text from pieces:

            ```python
            print("Hello, " + "Ada" + "!")
            # Hello, Ada!
            ```

            Look at the space after the comma. It is inside the quotes, so it is part of the first string.
            Python puts nothing of its own between strings that it joins. That is different from the comma
            in `print("a", "b")`, which does put a space between the two values.

            Pick the piece that makes this program print `Good morning`:

            ```fill
            print("Good" + ___)
            ---
            - [x] " morning" :: Right. The space is inside the quotes, so it is part of the string and reaches the output.
            - [ ] "morning" :: This prints `Goodmorning`. Python puts nothing between two strings that it joins.
            - [ ] morning :: Without quotes, Python reads `morning` as a name, finds nothing with that name and stops with a `NameError`.
            ```

            ### Nothing inside quotes is calculated

            Quotes switch the maths off. Python copies the characters between them to the output and does
            not look at what they say:

            ```python
            print("7 + 1")
            # 7 + 1
            ```

            Match each statement to its output:

            ```match
            `print(4 + 4)` :: `8`
            `print("4" + "4")` :: `44`
            `print("4 + 4")` :: `4 + 4`
            `print("4", "4")` :: `4 4`
            ---
            No quotes: two numbers are added. Quotes around each digit: two strings are joined. Quotes around everything: one string, shown as written. A comma: two values with one space between them.
            ```

            **Watch out:** when words run together in your output, as in `Goodmorning`, a space is missing
            inside the quotes. A space can also be a string of its own: `"New" + " " + "York"` gives
            `New York`.

            **In short:** quotes make text, `+` adds numbers and joins strings, and nothing inside quotes is
            ever calculated.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line, then press **Check**.
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
            Line 1 has no quotes, so `2` and `3` are numbers and `+` adds them: `5`. In line 2 each digit is
            in quotes, so they are two strings, and `+` joins them: `23`. In line 3 the quotes go around
            everything, so it is one string and Python prints it as written: `2 + 3`. Line 4 joins three
            strings. The middle one, `" "`, holds a single space, so the result is `AI app`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "For each line, look at the quotes first. What is inside quotes is text. What has no quotes is a number.",
            "Between two numbers, `+` adds. Between two strings, `+` joins them end to end and adds no space of its own. Text inside quotes is never calculated.",
            "Your answer has four lines: the result of a sum, then two characters glued together, then the text of line 3 exactly as it stands between its quotes, then three pieces joined, where the middle piece is a single space.",
        ],
    },
    {
        "id": "basics-s7",
        "title": "Call a built-in",
        "difficulty": 0,
        "mode": "script",
        "lesson": r'''
            ## Let Python do the counting

            An AI model can only read a limited amount of text at once, so AI apps keep measuring how long
            a text is. You could count the characters of a sentence with your finger. That is slow, and one
            slip gives a wrong number. Python can count for you.

            ```python
            print(len("hello"))
            # 5
            print(len("hi there"))
            # 8
            ```

            `len` is short for "length". You hand it a string between the parentheses, and it works out how
            many characters the string has. `"hi there"` has 8, because the space is a character too.

            ### Something that gives an answer back

            `len` and `print` are both **functions**: named pieces of ready-made code that each do one job.
            Writing the name with parentheses after it is a **call**. A call makes the function do its job.
            The value between the parentheses is the **argument**, the thing the function works on.
            Functions that come with Python, like these two, are called **built-in functions**.

            The two do different jobs. `print` puts its argument on the screen. `len` shows nothing. It
            hands the number back to the place where the call was written, as if the call were replaced by
            its answer.

            That is why one call sits inside the other. Python works from the inside out: first
            `len("hello")` becomes `5`, then `print(5)` shows it.

            ```quiz
            In `print(len("good morning"))`, which call does Python run first?
            - [ ] `print`, because it is written first :: `print` cannot show anything yet. It needs its argument, and that argument is a call that has not finished.
            - [x] `len`, because it is the inner call :: Yes. `len("good morning")` hands back `12`, and then `print(12)` shows it.
            - [ ] Both at the same moment :: Python does one thing at a time. The inner call has to finish before the outer call can start.
            ```

            Now predict three counts. Look closely at the quotes and the spaces:

            ```predict
            print(len("AI"))
            print(len("A I"))
            print(len("42"))
            ---
            `AI` has 2 characters. `A I` has 3, because the space in the middle counts. `"42"` is in quotes, so it is a string of 2 characters, not the number forty-two.
            ```

            **Watch out:** a line that says only `len("hello")` shows nothing when you run it. `len` hands
            back `5`, and nobody receives it. To see the number, put the call inside `print(...)`.

            **In short:** `len(text)` hands back the number of characters in a string, and in
            `print(len(...))` the inner call runs first.
        ''',
        "prompt": r'''
            An AI model can only take in a limited amount of text, so an app measures a prompt before it
            sends it. A prompt is the text that you send to a model. In this step the prompt is one fixed
            sentence.

            **Your job:** write a script that prints how many characters this sentence has:
            `Explain RAG in one sentence.` (RAG is a technique from later in the course. Here it is only a
            word in the sentence.)

            **What comes out**
            - one line of output: the number of characters in the sentence, as a whole number

            **Rules**
            - Python must do the counting. A check looks for a call to `len` in your script, so a number
              that you counted and typed yourself does not pass.
            - Count the sentence exactly as it is written above. The capital letters, the spaces and the
              full stop at the end all belong to it.
            - The output is that one number and nothing else.

            **Examples**

            A script that did the same for the text `hi there` would print:
            ```text
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
            "Two built-in functions from the lesson do the whole job. One counts the characters of a string. The other shows a value on the screen.",
            "The sentence has to be a string, so it goes inside quotes. The counting function needs that string as its argument, and the function that shows things needs the count as its argument.",
            "Write the call that counts, with the sentence in quotes between its parentheses. Then wrap that whole call in the call that shows a value, so that the counting call is the inner one. Press Run: you should see one number.",
        ],
    },
    {
        "id": "basics-s2",
        "title": "Fill in the return",
        "difficulty": 0,
        "lesson": r'''
            ## Make a function of your own

            `len` and `print` came with Python. Somebody wrote them once and gave them a name, and since
            then everyone uses them by that name. You can do the same with your own code: write it once,
            name it, and use it wherever you need it.

            Here is a function that hands back the name of an AI model:

            ```python
            def model_name():
                return "gpt-4o-mini"

            print(model_name())
            # gpt-4o-mini
            ```

            Read it piece by piece.

            - `def` is short for "define". `def model_name():` tells Python that a function called
              `model_name` starts here. The line ends with a colon.
            - The next line starts with 4 spaces. The spaces mark the line as part of the function.
            - `return` means "hand this back to whoever called me". The value after it is the function's
              **return value**.

            The two `def` lines only create the function. They are a recipe that has been written down, not
            a meal that has been cooked. Nothing in the function runs until a call, and you call your own
            function the way you called `len`: its name, then parentheses. The call `model_name()` runs the
            function and stands for its return value, and `print` shows that value.

            ```quiz
            What does this program show when you run it?

            ~~~python
            def city():
                return "Paris"
            ~~~
            - [ ] `Paris` :: The function would hand back `Paris`, but nothing calls it and nothing prints, so the screen stays empty.
            - [x] Nothing :: Right. `def` only creates the function. Without a call such as `print(city())`, the `return` line never runs.
            - [ ] An error message :: The code is correct. Creating a function and never using it is allowed. It only does nothing.
            ```

            Now put a whole program in order. Python has to read the `def` before it can run a call to the
            function:

            ```order
            def app_name():
                return "PyTrainer"
            print("Welcome to")
            print(app_name())
            ---
            Python runs from top to bottom. The `def` line and its indented `return` line create the function, and only after that can the last line call it.
            ```

            **Watch out:** text after `return` needs quotes. Without them, as in `return ready`, Python
            takes `ready` for a name, finds nothing with that name and stops with
            `NameError: name 'ready' is not defined`.

            **In short:** `def` creates a function, `return` hands a value back, and nothing in the function
            runs until you call it by its name with `()`.
        ''',
        "prompt": r'''
            A chat app greets every new user with the same line of text. A small function hands that
            greeting to whichever part of the app needs it.

            **Your job:** finish `greeting()` so that it gives back the greeting text. The function is
            already written except for one gap, marked `___`. Replace the gap.

            **What goes in**
            - nothing: `greeting()` takes no input, so its parentheses stay empty

            **What comes out**
            - the string `Hello, AI!`

            **Rules**
            - The text must match exactly: a capital `H`, a comma after `Hello`, one space, `AI` in capitals
              and `!` at the end.
            - The function must hand the text back as a string. The checks call `greeting()` and look at
              what comes back.

            **Examples**
            ```python
            greeting()   # returns "Hello, AI!"
            ```
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
            "The gap sits right after `return`. What kind of value does the example in the lesson have in that spot?",
            "The function has to hand back a piece of text, and Python only treats something as text when it is written as a string.",
            "Delete the three underscores. In their place, write the greeting from the task as a string. Then compare it with the task character by character: the capital letter, the comma, the space and the exclamation mark.",
        ],
    },
    {
        "id": "basics-s5",
        "title": "Write add()",
        "difficulty": 0,
        "lesson": r'''
            ## A function that works with what you hand it

            The function in the last step gave the same answer every time. Most useful functions do not.
            `len` gives a different number for each string you hand it. For that, a function needs a way to
            receive what the caller hands in.

            You give the incoming value a name, inside the parentheses of the `def` line:

            ```python
            def triple(n):
                return n * 3

            print(triple(4))
            # 12
            print(triple(10))
            # 30
            ```

            `*` means "times". When Python runs the call `triple(4)`, it first sets `n` to `4` and then
            runs the function, so `n * 3` is `12`. The call `triple(10)` runs the same line again, now with
            `n` set to `10`.

            A name in the `def` line that receives a value is called a **parameter**. The value itself, the
            one written in the call, is the argument you already know. Press Next and watch the Variables
            box, where `n` gets a new value for each call:

            ```diagram
            {"type": "trace", "title": "Each call gives the parameter n a new value", "code": ["def triple(n):", "    return n * 3", "", "print(triple(4))", "print(triple(10))"], "steps": [
              {"line": 1, "vars": {}, "out": "", "note": "The def line creates the function. Its indented line does not run yet."},
              {"line": 4, "vars": {}, "out": "", "note": "Line 4 calls triple with the argument 4."},
              {"line": 2, "vars": {"n": "4"}, "out": "", "note": "The call triple(4) set n to 4. Now the line inside the function runs."},
              {"line": 5, "vars": {}, "out": "12\n", "note": "The call handed back 12 and line 4 printed it. Line 5 calls triple again."},
              {"line": 2, "vars": {"n": "10"}, "out": "12\n", "note": "The call triple(10) set n to 10."},
              {"line": null, "vars": {}, "out": "12\n30\n", "note": "The program has finished."}
            ]}
            ```

            ### More than one parameter

            A function can take several values. Separate the parameters with commas, and do the same with
            the arguments. Python pairs them up by position: the first argument goes to the first
            parameter, the second to the second.

            ```python
            def area(width, height):
                return width * height

            print(area(3, 5))
            # 15
            ```

            So the order of the arguments matters. Predict what these two calls print:

            ```predict
            def minus(first, second):
                return first - second

            print(minus(10, 4))
            print(minus(4, 10))
            ---
            `-` means "minus". In the first call `first` is 10 and `second` is 4, so the result is 6. The second call hands over the same numbers in the other order, so it works out 4 - 10, which is -6.
            ```

            The `return` line has to use the parameter names. Pick the line that makes both calls right:

            ```fill
            def cost(count, price):
                return ___

            print(cost(3, 5))
            print(cost(10, 2))
            ---
            - [x] count * price :: Right. Each call puts its own arguments into the parameters, so the program prints 15 and then 20.
            - [ ] 3 * 5 :: This is right for the first call only. Fixed numbers ignore the arguments, so the second call prints 15 as well.
            - [ ] count * count :: This multiplies the first argument by itself and never uses `price`. It prints 9 and then 100.
            ```

            **Watch out:** a call must hand over one argument for each parameter. `area(3)` stops with
            `TypeError: area() missing 1 required positional argument: 'height'`. It means that nothing was
            handed in for `height`.

            **In short:** a parameter is a name in the `def` line, and each call fills the parameters with
            its arguments, in order.
        ''',
        "prompt": r'''
            Adding two numbers is about the smallest useful job a function can do. That makes it a good
            first function to write from start to finish.

            **Your job:** write the body of `add(a, b)` so that it gives back the two numbers added
            together. The `def` line is already in the editor. The `...` under it is a placeholder that does
            nothing. Replace it with your own code.

            **What goes in**
            - `a`: a whole number, for example `2`
            - `b`: another whole number, for example `3`

            **What comes out**
            - the two numbers added together, as a number: `5` for the example values

            **Rules**
            - The function must return the result. The checks call `add` and look at what comes back, so
              showing the result on the screen is not enough.
            - It must work for any two whole numbers, negative numbers included.

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
            "Look at the `area` example in the lesson. It also takes two numbers and gives one number back.",
            "The body needs one line. That line hands back the result of a small calculation, and the calculation uses the two parameter names, not fixed numbers.",
            "Replace the `...` with a line that starts with the word that hands a value back. After that word, write the two parameters with the sign for adding between them. Keep the 4 spaces at the start of the line.",
        ],
    },
    {
        "id": "basics-s3",
        "title": "Fix: print is not return",
        "difficulty": 0,
        "lesson": r'''
            ## Showing a value is not the same as handing it back

            Here are two functions that look almost the same. One shows its result on the screen. The
            other hands its result back.

            ```python
            def shows(n):
                print(n + 10)

            def gives(n):
                return n + 10

            shows(5)
            # 15
            print(gives(5))
            # 15
            ```

            Both put `15` on the screen, so it is tempting to think they do the same job. They do not.
            `shows` puts the 15 on the screen itself, and after that the number is gone. `gives` hands the
            15 back to the line that called it, and that line can do anything with it: print it, add to
            it, pass it on to another function.

            The difference appears as soon as a line tries to use the result:

            ```predict
            def shows(n):
                print(n + 10)

            def gives(n):
                return n + 10

            print(gives(5) + 1)
            print(shows(5))
            ---
            `gives(5)` hands back 15, so the first `print` shows 16. In the last line, `shows(5)` runs first and prints 15 itself. Then it reaches its end without a `return`, so it hands back Python's value for "nothing", which is written `None`. The outer `print` shows that `None`.
            ```

            `None` is a word worth remembering. It is the value Python uses when there is no value. A
            function that reaches its end without a `return` hands back `None`.

            Press Next and watch when each line of output appears:

            ```diagram
            {"type": "trace", "title": "A function without return hands back None", "code": ["def shows(n):", "    print(n + 10)", "", "def gives(n):", "    return n + 10", "", "print(gives(5))", "print(shows(5))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 4, "vars": {}, "out": ""},
              {"line": 7, "vars": {}, "out": "", "note": "Both functions exist now. Line 7 calls gives."},
              {"line": 5, "vars": {"n": "5"}, "out": "", "note": "gives hands 15 back to line 7, and line 7 prints it."},
              {"line": 8, "vars": {}, "out": "15\n"},
              {"line": 2, "vars": {"n": "5"}, "out": "15\n", "note": "shows prints 15 itself. Then it ends with no return."},
              {"line": null, "vars": {}, "out": "15\n15\nNone\n", "note": "The call shows(5) handed back None, so line 8 printed None."}
            ]}
            ```

            This matters for every exercise in the course. A check calls your function and looks at what
            comes back. It never looks at the screen. A function that only prints fails its checks, and the
            message says that it returned `None`.

            ```quiz
            A check reports: `half(10) returned None`. What is the most likely cause?
            - [x] The function reaches its end without a `return` :: Right. Without a `return`, a call hands back `None`, even when the function printed the correct number on the way.
            - [ ] The check never called the function :: The message shows the call, `half(10)`, so the function did run.
            - [ ] `None` is how Python writes zero :: `None` is not a number. It means that no value came back at all.
            ```

            **Watch out:** a `print` inside a function is fine when you want to see what is going on. It
            never takes the place of `return`.

            **In short:** `print` shows a value to a person, `return` hands a value to the code that called
            the function, and the checks only see what is returned.
        ''',
        "prompt": r'''
            A function called `double` is meant to take a number and give back twice that number. It works
            the number out correctly, but every check fails and says that the function returned `None`.

            **Your job:** find the one bug in `double(n)` and fix it. The code is already in the editor.

            **What goes in**
            - `n`: a whole number, for example `4`

            **What comes out**
            - `n` times 2, as a number: `8` for the example value

            **Rules**
            - The result must be handed back to the caller. Showing it on the screen does not count.
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
            "The check says that the function returned `None`. When does a call hand back `None`?",
            "The calculation in the function is right. Look at what the function does with the result: does it show it, or does it hand it back?",
            "One word in the body decides what happens to the result. Change that word so that the value goes back to the caller instead of onto the screen. The word that hands a value back needs no parentheses around the value.",
        ],
    },
    {
        "id": "basics-s8",
        "title": "Fix: indent the body",
        "difficulty": 0,
        "lesson": r'''
            ## How Python knows which lines belong to a function

            Look at this program and ask yourself: where does the function end?

            ```python
            def excited(text):
                return text + "!"

            print(excited("ready"))
            # ready!
            ```

            No word says "end of function". Python works it out from the spaces at the start of each line.
            The `return` line starts with 4 spaces, so it belongs to the function above it. The `print`
            line starts at the left edge, so it does not. It is an ordinary statement that runs when Python
            gets to it.

            Spaces at the start of a line are called **indentation**. The indented lines under a `def`
            are the function's **body**: the part that runs on each call. In many languages indentation
            only keeps the code tidy. In Python it is part of the meaning.

            ```quiz
            Which lines are the body of `welcome`?

            ~~~python
            def welcome(name):
                print("New user")
                return "Hello, " + name
            print(welcome("Ada"))
            ~~~
            - [x] Lines 2 and 3 :: Right. Both are indented under the `def` line, so both belong to the function.
            - [ ] Line 2 only :: Line 3 has the same indentation as line 2, so it is part of the body as well.
            - [ ] Lines 2, 3 and 4 :: Line 4 starts at the left edge. That ends the function, and line 4 is the statement that calls it.
            ```

            ### When the indentation is missing

            A `def` line must be followed by at least one indented line. If the next line starts at the
            left edge, Python stops before it runs anything and shows this:

            ```text
            IndentationError: expected an indented block after function definition on line 1
            ```

            Read it slowly. "Function definition on line 1" is the `def` line. A group of lines with the
            same indentation is called a **block**, so "expected an indented block" means: after that
            `def`, Python wanted a body and found none.

            Too much indentation is a mistake as well. In the program below, the last line was meant to
            call the function. Because it is indented, it became part of the body instead, and nothing
            calls the function at all:

            ```try
            def label(tag):
                return "#" + tag
                print(label("python"))
            ---
            Run it: it prints nothing. Fix the indentation of one line so that the program prints `#python`.
            ---
            def label(tag):
                return "#" + tag
            print(label("python"))
            ---
            At the left edge, the `print` line is outside the function, so Python runs it and it calls `label`. (Inside the body it could never run: a function stops at `return`.)
            ```

            **Watch out:** give every line of a body the same indentation, 4 spaces. In the editor, the
            Tab key types the 4 spaces for you.

            **In short:** the indented lines under `def` are the function, and the first line back at the
            left edge is outside it.
        ''',
        "prompt": r'''
            `shout(text)` is meant to make a piece of text louder by putting an exclamation mark after it.
            The idea is right, but the program does not even start: every check fails with an
            `IndentationError`.

            **Your job:** fix the one bug in `shout(text)`. The code is already in the editor.

            **What goes in**
            - `text`: a string, for example `"hi"`

            **What comes out**
            - `text` with `!` added at the end, as a string: `"hi!"` for the example value

            **Rules**
            - There is no space between the text and the `!`.
            - It must work for any text, including the empty string `""`, which gives `"!"`.

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
            "Press Check and read the error. It names a line and says what Python expected to find after it.",
            "The `return` line is meant to be the body of the function. How does Python tell that a line belongs to the function above it?",
            "Move the `return` line to the right by the usual amount, so that it sits under the `def` line as its body. Change nothing else.",
        ],
    },
    {
        "id": "basics-1",
        "title": "Count the characters",
        "difficulty": 1,
        "lesson": r'''
            ## Put a ready-made function to work inside your own

            You have called `len`, and you have written functions of your own. Now the two meet. A function
            that you write can call other functions to get its work done. Often that is all it does: it
            gives a clear name to a small job.

            Python comes with a set of functions that are ready in every program, with nothing to set up.
            They are called **built-in functions**, or built-ins. `print` and `len` are two of them. Here
            are two more:

            ```python
            print(max(3, 9, 4))
            # 9
            print(min(3, 9, 4))
            # 3
            ```

            `max` hands back the largest of its arguments, and `min` the smallest.

            Inside your own function you call a built-in the way you always have, and you hand its result
            back with `return`:

            ```python
            def biggest(a, b):
                return max(a, b)

            print(biggest(7, 12))
            # 12
            ```

            Follow the value. The call `biggest(7, 12)` sets `a` to 7 and `b` to 12. Inside the function,
            `max(a, b)` works out 12. `return` hands that 12 back, and `print` shows it.

            Programmers say that a call **evaluates to** its result: `max(7, 12)` evaluates to `12`.
            Wherever a call stands in your code, you can read it as the value it evaluates to.

            ```fill
            def shortest(a, b, c):
                return ___

            print(shortest(8, 2, 5))
            print(shortest(1, 9, 9))
            ---
            - [x] min(a, b, c) :: Right. The built-in picks the smallest of the three arguments of each call, so the program prints 2 and then 1.
            - [ ] min(8, 2, 5) :: This is right for the first call only. Fixed numbers ignore the arguments, so the second call prints 2 as well.
            - [ ] max(a, b, c) :: `max` picks the largest argument. The program would print 8 and then 9.
            ```

            A call can stand anywhere a value can stand, even in the middle of a sum:

            ```quiz
            What does `len("AI") + len("app")` evaluate to?
            - [x] `5` :: Right. `len("AI")` evaluates to 2 and `len("app")` evaluates to 3, and `+` adds two numbers.
            - [ ] `"AIapp"` :: That would be `"AI" + "app"`. Here each `len` call has already turned its string into a number.
            - [ ] `2` :: That is only `len("AI")`. The sum also has the second call, which adds 3.
            ```

            **Watch out:** `len` works on text, not on numbers. `len(5)` stops the program with
            `TypeError: object of type 'int' has no len()`. A `TypeError` means that an operation does not
            work for that kind of value, and `int` is Python's word for a whole number.

            **In short:** your function can call a built-in and return what the call evaluates to.
        ''',
        "prompt": r'''
            The text you send to an AI model is called a prompt. Models only accept a limited amount of
            text, so apps often measure a prompt before they send it.

            **Your job:** write `prompt_length(prompt)` so that it gives back how many characters the text
            has. The `def` line is already in the editor. Replace the `...` under it.

            **What goes in**
            - `prompt`: a piece of text (a string), for example `"hello"`

            **What comes out**
            - the number of characters in `prompt`, as a whole number: `5` for the example value

            **Rules**
            - Every character counts, spaces and punctuation included.
            - The empty string `""` has `0` characters.
            - Hand the number back with `return`. Showing it on the screen is not enough.

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
            "Which built-in from earlier in this chapter counts the characters of a string?",
            "Your function does not have to count anything itself. It calls that built-in with its parameter and hands back what the call evaluates to.",
            "Replace the `...` with one line. It starts with the word that hands a value back. After that word comes a call to the counting built-in, with the parameter `prompt` as its argument.",
        ],
    },
    {
        "id": "basics-4",
        "title": "Read the failing check",
        "difficulty": 1,
        "lesson": r'''
            ## When the code runs but the answer is wrong

            Some mistakes stop the program, and Python reports them with an error message. Others are
            quieter. The code runs from start to finish, no error appears, and the answer is simply wrong.

            Python cannot point out this kind of mistake, because it does not know what you meant. The
            checks can. When a check fails, it tells you what it tried and what came back:

            ```text
            FAIL  subtracts the discount from the price
                  final_price(100, 30) returned -70
            ```

            There are three facts in that message.

            1. **What was tested:** the name of the check, "subtracts the discount from the price".
            2. **The call:** the check called your function with the arguments `100` and `30`.
            3. **What came back:** your function returned `-70`.

            Now compare the third fact with the Examples in the task. Suppose the task says that
            `final_price(100, 30)` returns `70`. The digits are right and only the sign is wrong. That is
            a strong clue about where to look, because of the way subtraction works:

            ```predict
            def gap(a, b):
                return a - b

            print(gap(100, 30))
            print(gap(30, 100))
            ---
            `100 - 30` is 70, and `30 - 100` is -70. A subtraction gives a different result when its two values trade places, and the difference is exactly the sign.
            ```

            A mistake like this, where the code runs and gives the wrong answer, is called a **bug**. The
            formal name is **logic error**. Finding and fixing bugs is a normal part of the work, and the
            failing check is your best tool for it.

            ```quiz
            A check fails with this message. What do you know for certain?

            ~~~text
            FAIL  adds the tip to the bill
                  total(40, 5) returned 35
            ~~~
            - [x] The function ran without an error and handed back 35 :: Right. The message shows the call and the value that came back. Whether 35 is correct is for you to compare with the task.
            - [ ] Python found an error in the code :: An error would stop the program and show an error message. Here the function ran to its end and returned a value.
            - [ ] The check used the wrong numbers :: The check chooses the arguments. They are part of the test, not part of the mistake.
            ```

            You can also make the same call yourself. Add a line such as `print(total(40, 5))` at the
            bottom of your file and press Run to see what comes back.

            **Watch out:** the bug is in the function, never in the check. Change your code until the call
            gives the value from the Examples.

            **In short:** a failing check shows the call and what came back. Compare that with the Examples
            in the task to find the bug.
        ''',
        "prompt": r'''
            An AI model only accepts a limited number of tokens, which are small pieces of text. Your app
            keeps track of how many are still free: the limit minus the number already used. Someone has
            written the function for that. It runs without an error, but its answers are wrong.

            **Your job:** find the one bug in `tokens_left(limit, used)` and fix it. Press **Check** before
            you change anything, and read what the failing checks say.

            **What goes in**
            - `limit`: the token limit, a whole number, for example `100`
            - `used`: the tokens used so far, a whole number, for example `30`

            **What comes out**
            - the tokens that are left, as a whole number: `70` for the example values

            **Rules**
            - Using exactly the limit leaves `0`.
            - When `used` is bigger than `limit`, the answer is a negative number, for example `-15`.

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
            "Press Check, then compare the value that your function returned with the value in the Examples for the same call.",
            "The size of the number is right and its sign is wrong. Which of the two values should the subtraction start from?",
            "In the `return` line, the two names stand on the wrong sides of the minus sign. Make them trade places.",
        ],
    },
    {
        "id": "basics-2",
        "title": "Fix the broken welcome",
        "difficulty": 1,
        "lesson": r'''
            ## What an error message is telling you

            Sooner or later Python refuses to run your code and shows an error instead. That is normal. It
            happens to people who have programmed for twenty years, several times a day. An error message
            is not a telling-off. It is Python saying, as exactly as it can, where it got stuck.

            Every message answers two questions: where, and what.

            ```text
            SyntaxError in solution.py line 1: expected ':'
                def add(a, b)
            ```

            - **Where:** `line 1` of your file. The line itself is printed underneath.
            - **What:** `SyntaxError` is the kind of error, and `expected ':'` is the reason. Python wanted
              a colon and did not find one.

            When you press Run, Python shows the same facts in its own layout, on several lines. The line
            that names the error is then the last one, so read that line first.

            ### The three errors you will meet first

            A **syntax error** means that the code breaks the grammar of Python: a missing colon, a missing
            quote, a parenthesis that is never closed. Python reads the whole file before it runs any of
            it, so with a syntax error not one line runs.

            An `IndentationError` you know from two steps ago: the body under a `def` is not indented.

            A `NameError` means that Python met a name it does not know. Usually it is a typing slip, and
            often the slip is a capital letter. To Python, `total` and `Total` are two different names.
            Programmers say that names are **case-sensitive**.

            ```quiz
            This program stops with an error. Which one?

            ~~~python
            def show(total):
                return Total

            print(show(5))
            ~~~
            - [x] `NameError: name 'Total' is not defined` :: Right. The parameter is spelled `total`. With a capital `T` it is a different name, and nothing has that name. Python even adds a guess: `Did you mean: 'total'?`
            - [ ] `SyntaxError: expected ':'` :: The `def` line ends with its colon, and every line follows the grammar. The trouble is a name, not the grammar.
            - [ ] No error. It prints `5` :: It would with `return total`. Python does not treat `Total` and `total` as the same name.
            ```

            Match each message with what it is telling you:

            ```match
            `SyntaxError: expected ':'` :: a colon is missing, often at the end of a `def` line
            `IndentationError: expected an indented block` :: the line under a `def` does not start with spaces
            `NameError: name 'Total' is not defined` :: the code uses a name that Python does not know
            ```

            ### One error at a time

            Python stops at the first error it finds and tells you about that one only. Fix it, run again,
            and read the next message. Code with three bugs takes three rounds. Everyone works this way.

            **Watch out:** the line number is where Python noticed the problem. Now and then the mistake is
            on the line just above, for example a parenthesis that was never closed.

            **In short:** find the line that names the error, read the reason after it, and go to the line
            number it gives.
        ''',
        "prompt": r'''
            Your AI app greets each new user by name. Someone typed the function for that in a hurry, and
            it has three small bugs. Python will tell you about them, one at a time.

            **Your job:** fix `welcome(name)` so that it gives back the greeting. Press **Check** (or
            **Run**), read the error message, fix that one bug, and repeat until every check passes.

            **What goes in**
            - `name`: the user's name, a string, for example `"Ada"`

            **What comes out**
            - the text `Welcome, `, then the name, then `!`, as one string: `"Welcome, Ada!"` for the
              example value

            **Rules**
            - The format is exact: `Welcome,`, one space, the name, and `!` with no space before it.
            - It must work for any name, not only `"Ada"`.

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
            "Find the line of the message that names the error. It also gives a line number and a reason.",
            "There are three different bugs, and each gives a different error: one is about a sign that is missing at the end of a line, one is about indentation, and one is about a name that Python does not know.",
            "First give the `def` line the sign it must end with. Then move the `return` line under it as the body. Last, compare the spelling of the name in the `return` line with the parameter in the `def` line, capital letters included.",
        ],
    },
    {
        "id": "basics-5",
        "title": "Round a score",
        "difficulty": 1,
        "lesson": r'''
            ## Looking a function up

            You want to use a function but cannot remember all the inputs it accepts. Python's official website lets you look up what it does and how to call it. Reading an entry there is a skill of its own, and this step is your first practice.

            Take `round`. Its name gives away what it does:

            ```python
            print(round(2.567))
            # 3
            print(round(2.4))
            # 2
            ```

            Python's official **documentation**, or **docs**, records function behaviour at docs.python.org.

            It rounds to the nearest whole number. But the docs entry for `round` starts with a line that
            shows there is more to it:

            ```text
            round(number, ndigits=None)
            ```

            This first line of an entry is called the **signature**. It gives the function's name and its
            parameters, in order. So `round` has two parameters: the number to round, and a second one
            called `ndigits`.

            The `=None` after `ndigits` is new. A parameter written with `=` has a **default value**, the
            value Python uses when the call leaves that argument out. That is why `round(2.567)` worked
            with one argument. An argument that a call may leave out is called an **optional argument**.

            ```match
            signature :: the first line of a docs entry: the function's name and its parameters
            default value :: what a parameter gets when the call leaves it out
            optional argument :: an argument that a call may leave out
            ```

            Reading signatures works the same way for every function. Try one you have not seen:

            ```quiz
            The docs entry of a built-in starts with `pow(base, exp, mod=None)`. Which call is allowed?
            - [x] `pow(2, 3)` :: Right. `base` is 2 and `exp` is 3. `mod` has a default value, so the call may leave it out.
            - [ ] `pow(2)` :: `exp` has no default value, so the call must give it. Python stops with a `TypeError` that names the missing argument.
            - [ ] `pow()` :: Two parameters have no default value, and this call gives neither of them.
            ```

            So what does the second argument of `round` change? That is the kind of question the docs
            answer, and in this step you find the answer yourself. The task has a link to the entry.

            **Watch out:** the arguments of a call go in the order of the signature. With the two
            arguments the wrong way round, Python either stops with an error or quietly works on the wrong
            value.

            **In short:** a signature lists a function's parameters in order, and a parameter written with
            `=` may be left out of the call.
        ''',
        "research": {
            "note": "Read the entry for the built-in round() - especially what its second input (ndigits) does - then come back.",
            "links": [
                {"title": "round() - Python docs", "url": "https://docs.python.org/3/library/functions.html#round"},
            ],
        },
        "prompt": r'''
            A tool that tests AI answers gives each answer a score, a long decimal number such as
            `0.87654`. On a dashboard, two digits after the decimal point are enough.

            **Your job:** write `short_score(score)` so that it gives back the score rounded to 2 decimal
            places. The built-in `round` can do this. Its docs entry, linked above, explains how.

            **What goes in**
            - `score`: a decimal number, for example `0.87654`

            **What comes out**
            - `score` rounded to 2 decimal places, as a number and not as text: `0.88` for the example value

            **Rules**
            - Hand the number back with `return`. Showing it on the screen is not enough.
            - A number with fewer decimals stays as it is: `0.5` gives `0.5`.

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
            "The built-in `round` does the whole job. Its docs entry explains what its second parameter is for.",
            "One call to `round` is enough. It needs two arguments, in the order of the signature, and your function hands back what the call evaluates to.",
            "Replace the `...` with one line that hands back a call to `round`. The first argument is the parameter `score`. The second argument is the number of decimal places the task asks for.",
        ],
    },
    {
        "id": "basics-3",
        "title": "Credits for a request",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            An AI service charges for each request in **credits**. Text is counted in tokens, which are
            small pieces of text. Each prompt token (text you send) costs 2 credits, and each output token
            (text the model writes back) costs 6 credits. You are going to write the small program that
            works out the bill.

            **Your job:** write two functions and one `print` line in `solution.py`.

            **1. `prompt_cost(tokens)`**
            - goes in: `tokens`, the number of prompt tokens, a whole number, for example `10`
            - comes out: the credits for those prompt tokens, a whole number: `20` for the example value

            **2. `request_cost(prompt_tokens, output_tokens)`**
            - goes in: `prompt_tokens`, for example `10`, and `output_tokens`, for example `1`, both whole
              numbers
            - comes out: the credits for the whole request, a whole number: `26` for the example values
              (20 for the prompt and 6 for the output)

            **3. One `print(...)` line at the bottom of the file**
            - It prints the cost of a request with 1000 prompt tokens and 200 output tokens.
            - It starts at the left edge, so that it is outside both functions.

            **Rules**
            - `request_cost` must call `prompt_cost(...)` to work out the prompt part. A check looks for
              that call. (If the price of a prompt token changes later, it then changes in one place.)
            - Zero tokens cost `0` credits.
            - Running the file prints that one number and nothing else.

            **Examples**
            ```python
            prompt_cost(10)           # returns 20
            prompt_cost(0)            # returns 0
            request_cost(10, 1)       # returns 26
            request_cost(0, 5)        # returns 30
            ```

            Running the file prints:
            ```text
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
            "The file needs three parts: two `def` blocks and, under them at the left edge, one `print`. A function may call another function that you wrote.",
            "`prompt_cost` is one multiplication. `request_cost` adds two amounts: the prompt part, which it gets by calling `prompt_cost`, and the output part, which is another multiplication.",
            "Write `prompt_cost` first and try it with Run and a temporary `print`. Then write `request_cost`: its `return` line adds a call to `prompt_cost` for the prompt tokens and the output tokens times their price. Last, replace your temporary `print` with one that calls `request_cost` with the two numbers from the task.",
        ],
    },
    {
        "id": "basics-6",
        "title": "Longest prompt",
        "difficulty": 2,
        "lesson": r'''
            ## Putting it together: a call inside a call

            You know two things that can now be combined. `len` turns a string into a number. `min` and
            `max` pick one number out of several. When the result of one call is what the next call needs,
            you can write the first call right inside the parentheses of the second:

            ```python
            print(min(len("abc"), len("hi")))
            # 2
            ```

            A call that is written inside another call is a **nested** call. Python always works from the
            inside out. Here it runs the two `len` calls first, and they evaluate to 3 and 2. That turns
            the line into `print(min(3, 2))`. Then `min` evaluates to 2, and `print` shows it.

            ```quiz
            In which order does Python run the three calls in `print(min(len("go"), 5))`?
            - [x] `len`, then `min`, then `print` :: Right. The innermost call runs first, because the calls around it need its result.
            - [ ] `print`, then `min`, then `len` :: That is the order you read them in. Python cannot run `print` before it knows what to print, so it starts on the inside.
            - [ ] All three at the same moment :: Python does one thing at a time. Each outer call waits for the value of the call inside it.
            ```

            Work through two lines yourself. Replace each inner call with the value it evaluates to, then
            do the outer call:

            ```predict
            print(len("AI") + len("app"))
            print(max(len("a"), 2, len("abcd")))
            ---
            The first line becomes `print(2 + 3)`, which shows 5. In the second line the inner calls evaluate to 1 and 4, so it becomes `print(max(1, 2, 4))`, which shows 4.
            ```

            To plan a function like the one in this step, say what it has to do in one sentence first.
            Then turn each part of your sentence into a call. The part that has to happen first goes on the
            inside.

            **Watch out:** every `(` needs its `)`. With one missing at the end, as in
            `print(min(len("abc"), len("hi"))`, Python stops with `SyntaxError: '(' was never closed`.
            Count them from the inside out.

            **In short:** inner calls run first, and the values they evaluate to become the arguments of
            the outer call.
        ''',
        "prompt": r'''
            You have written three versions of a prompt and want to know how long the longest one is, for
            example to make sure that even the longest version fits within a limit.

            **Your job:** write `longest_length(a, b, c)` so that it gives back the number of characters in
            the longest of the three texts.

            **What goes in**
            - `a`, `b`, `c`: three strings, for example `"hi"`, `"hello"` and `"hey"`

            **What comes out**
            - a whole number, the length of the longest text: `5` for the example values

            **Rules**
            - Give back the length, which is a number, not the text.
            - The longest text can be in any of the three positions.
            - When several texts share the greatest length, give back that length.
            - When all three are empty strings, give back `0`.

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
            "Two built-ins from this chapter do all the work: one counts characters, and the other picks the biggest of several numbers.",
            "Say the plan in words: find the length of each of the three texts, then pick the biggest of those three numbers.",
            "Write one `return` line. The outer call is the built-in that picks the biggest number. Inside its parentheses go three inner calls, one for each text, and each of them is the built-in that counts characters.",
        ],
    },
]
