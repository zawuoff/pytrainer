TOPIC = {
    "id": "files",
    "title": "Reading & Writing Files",
    "track": "working-python",
    "order": 4,
    "requires": ["errors", "loops"],
    "summary": """
        open() with context managers, read/write/append modes, encodings, pathlib,
        walking folders of documents and handling missing files.
    """,
    "concepts": ["open / with", "read / readlines / iteration", "write / append modes",
                 "encoding", "pathlib.Path", "glob", "suffix / stem", "mkdir",
                 "read_text / write_text", "FileNotFoundError"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["file", "open", "read", "write", "append", "mode", "encoding", "with",
                 "close", "path", "pathlib", "glob", "mkdir", "read_text", "write_text",
                 "filenotfounderror"],
    "cards": [
        {
            "syntax": 'with open(path, encoding="utf-8") as fh:',
            "explain": "Opens a file for reading and closes it after the block. A for loop over fh gives one line per pass.",
            "example": r'''
                with open("todo.txt", "w", encoding="utf-8") as fh:
                    fh.write("buy milk\ncall Ada\n")
                with open("todo.txt", encoding="utf-8") as fh:
                    for line in fh:
                        print(line.strip())
                # buy milk
                # call Ada
            ''',
        },
        {
            "syntax": 'open(path, "w", encoding="utf-8")',
            "explain": "Write mode: creates the file, or erases its content first. fh.write() adds no newline, so add it yourself.",
            "example": r'''
                with open("note.txt", "w", encoding="utf-8") as fh:
                    fh.write("draft\n")
                with open("note.txt", "w", encoding="utf-8") as fh:
                    fh.write("final\n")
                with open("note.txt", encoding="utf-8") as fh:
                    print(repr(fh.read()))
                # 'final\n'
            ''',
        },
        {
            "syntax": 'open(path, "a", encoding="utf-8")',
            "explain": "Append mode: keeps the existing content and puts every write at the end. Creates the file if it is missing.",
            "example": r'''
                with open("chat.log", "a", encoding="utf-8") as fh:
                    fh.write("user: hi\n")
                with open("chat.log", "a", encoding="utf-8") as fh:
                    fh.write("bot: hello\n")
                with open("chat.log", encoding="utf-8") as fh:
                    print(fh.read())
                # user: hi
                # bot: hello
            ''',
        },
        {
            "syntax": "p.read_text()  /  p.write_text(text)",
            "explain": "Read or write a whole file in one call. Each opens the file and closes it for you.",
            "example": r'''
                from pathlib import Path

                note = Path("note.txt")
                note.write_text("hi\n", encoding="utf-8")
                print(note.read_text(encoding="utf-8"))
                # hi
            ''',
        },
        {
            "syntax": 'path.glob("*.txt")',
            "explain": "Gives the paths in that folder whose names match the pattern. * matches any characters. Sort the results.",
            "example": r'''
                from pathlib import Path
                box = Path("in")
                box.mkdir()
                for name in ["b.txt", "a.txt", "c.csv"]:
                    (box / name).write_text("x", encoding="utf-8")
                print(sorted(p.name for p in box.glob("*.txt")))
                # ['a.txt', 'b.txt']
            ''',
        },
        {
            "syntax": "except FileNotFoundError:",
            "explain": "Raised when you open a missing file in read mode. Catch it when a missing file is normal, then use a default.",
            "example": r'''
                try:
                    with open("history.txt", encoding="utf-8") as fh:
                        text = fh.read()
                except FileNotFoundError:
                    text = "(empty)"
                print(text)
                # (empty)
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Reading & Writing Files

Python deletes every variable when a program stops. A **file** is a named sequence of
characters stored on disk, so its data is still there on the next run. AI apps keep prompts,
documents, chat logs and results in files.

## Opening a file

`open(path, mode, encoding="utf-8")` returns a **file object**: a value with methods that
read from or write to the file. A file object must be **closed** when you are done, which
tells the operating system (Windows, macOS or Linux) to finish writing and release the file.

A `with` statement closes the file for you. `with open(...) as fh:` assigns the file object
to the name `fh`, runs the indented block, then closes the file. It closes the file even
when the block raises an exception. `fh.closed` is an attribute of the file object. It is
`False` while the file is open and `True` after the `with` block closes it.

```python
with open("prompt.txt", "w", encoding="utf-8") as fh:
    fh.write("You are helpful.\n")

with open("prompt.txt", encoding="utf-8") as fh:
    text = fh.read()
print(repr(text))
# 'You are helpful.\n'
print(fh.closed)
# True
```

Step through the second `with` block to see when the file is open and when it is closed.

```diagram
{"type":"flow","title":"What a with block does to prompt.txt","steps":[{"label":"open()","detail":"Python asks the operating system to open prompt.txt in read mode. open() returns a file object.","code":"open(\"prompt.txt\", encoding=\"utf-8\")"},{"label":"as fh","detail":"The with statement assigns the file object to the name fh. The file is open.","code":"fh.closed is False"},{"label":"Run the block","detail":"The indented lines run. fh.read() returns every character in the file as one string.","code":"text = fh.read()\ntext is 'You are helpful.\\n'"},{"label":"Close","detail":"The block ends, so Python closes the file. This also happens when the block raises an exception.","code":"fh.closed is True"},{"label":"After the block","detail":"The name text still refers to the string. Calling fh.read() now raises ValueError because the file is closed.","code":"print(repr(text))\n# 'You are helpful.\\n'"}]}
```

## Modes

The second argument of `open()` is the **mode**: a string that says what you will do with
the file.

| mode | meaning | if the file exists | if it is missing |
| --- | --- | --- | --- |
| `"r"` (default) | read | Python reads it | `FileNotFoundError` |
| `"w"` | write | the content is **erased** first | the file is created |
| `"a"` | append | new text goes at the end | the file is created |

The next example writes a **log**: a file that records what happened, one line per
event.

```python
with open("run.log", "w", encoding="utf-8") as fh:
    fh.write("started\n")
with open("run.log", "a", encoding="utf-8") as fh:
    fh.write("done\n")
with open("run.log", encoding="utf-8") as fh:
    print(repr(fh.read()))
# 'started\ndone\n'
```

`fh.write(text)` writes exactly the characters in `text`. It adds no newline, so you write
`line + "\n"` yourself.

## Reading

`fh.read()` returns the whole file as one string, newlines included. A `for` loop over a
file object gives one line per pass, and each line still ends with `"\n"`. The string method
`splitlines()` returns a list of the lines without their newlines.

```python
with open("run.log", "w", encoding="utf-8") as fh:
    fh.write("started\ndone\n")

with open("run.log", encoding="utf-8") as fh:
    for line in fh:
        print(repr(line), repr(line.strip()))
# 'started\n' 'started'
# 'done\n' 'done'

with open("run.log", encoding="utf-8") as fh:
    print(fh.read().splitlines())
# ['started', 'done']
```

## Encoding

An **encoding** is the rule that converts characters to the bytes (small numbers) that are
stored on disk. Always
pass `encoding="utf-8"`. Model output contains accented letters and emoji, and the default
encoding differs between computers.

## Missing files

Opening a missing file in read mode raises `FileNotFoundError`. Catch it when a missing
file is normal, and use a default value.

```python
try:
    with open("no_such_file.txt", encoding="utf-8") as fh:
        history = fh.read()
except FileNotFoundError:
    history = ""
print(repr(history))
# ''
```

## pathlib

The `pathlib` module provides `Path`: an object that holds a file path and has attributes
and methods for working with it. `from pathlib import Path` loads only the `Path` object from
the module, so you can write `Path(...)` without the module name. The `/` operator joins
path parts.

```python
from pathlib import Path

p = Path("docs") / "guide.md"
print(p.name, p.stem, p.suffix, p.parent)
# guide.md guide .md docs
Path("docs").mkdir(parents=True, exist_ok=True)
p.write_text("# Guide\n", encoding="utf-8")
print(p.read_text(encoding="utf-8").strip())
# # Guide
print(sorted(f.name for f in Path("docs").glob("*.md")))
# ['guide.md']
```

- `.name` is the last part of the path, `.stem` is the name without its extension and
  `.suffix` is the extension with its dot.
- `mkdir(parents=True, exist_ok=True)` creates the folder and any missing parent folders.
  It raises no error if the folder already exists.
- `write_text(text, encoding="utf-8")` creates or replaces the file. `read_text(encoding="utf-8")`
  returns the whole file as a string.
- `glob("*.md")` gives the matching paths directly inside the folder. `rglob("*")` gives
  every path in the folder and in all of its subfolders.
- `is_file()` and `is_dir()` return `True` or `False`. `relative_to(root)` returns the path
  without the leading `root` part.

## Common mistakes

- `open(path)` with no mode is read mode, so `fh.write()` raises an error. Pass `"w"` or `"a"`.
- `"w"` erases the existing content. Use `"a"` to add to a file.
- Without `"\n"`, `write()` puts all the text on one line. Without `.strip()`, each line
  you read still ends with `"\n"`.
- `glob` returns paths in no guaranteed order. Wrap the result in `sorted()`.
'''

EXERCISES = [
    {
        "id": "files-s1",
        "lesson": r'''
            ## Reading a file, one line at a time

            Every variable in a program is gone the moment the program stops. A chat app that kept its
            conversation only in a list would forget everything each time you closed it. Whatever has to
            last is stored on disk, in a file: some text with a name, such as `todo.txt`.

            This program makes a small file and then reads it back:

            ```python
            with open("todo.txt", "w", encoding="utf-8") as fh:
                fh.write("buy milk\ncall Ada\n")

            with open("todo.txt", encoding="utf-8") as fh:
                for line in fh:
                    print("item:", line.strip())
            # item: buy milk
            # item: call Ada
            ```

            The first two lines only make a file to practise on: they put two lines of text into
            `todo.txt`. Writing comes two steps from now, so look past them for the moment. The reading
            happens in the second half:

            - `open("todo.txt", encoding="utf-8")` asks for the file by its name and opens it.
            - `with ... as fh:` gives the opened file the name `fh` for the indented lines under it.
            - `for line in fh:` is the loop you know. An open file hands the loop one line of text on
              each iteration.

            What `open` hands back is called a **file object**. It is not the text itself. It is your
            connection to the file, and the text comes to you through it. When the indented block under
            `with` is over, Python **closes** the file, which tells the operating system (Windows, macOS
            or Linux) that your program is done with it. You do not have to remember that yourself.

            A disk stores numbers, not letters. `encoding="utf-8"` names the rule that turns the stored
            numbers back into characters. Pass it on every `open`, so that accented letters and emoji are
            read the same way on every computer.

            ### The newline that comes with every line

            Why does the example print `line.strip()` and not `line`? Find out:

            ```try
            with open("todo.txt", "w", encoding="utf-8") as fh:
                fh.write("buy milk\ncall Ada\n")

            with open("todo.txt", encoding="utf-8") as fh:
                for line in fh:
                    print(line)
            ---
            Run it first. There is an empty line after each item. Then change the last line so that the two items are printed directly under each other, with no empty lines.
            ---
            with open("todo.txt", "w", encoding="utf-8") as fh:
                fh.write("buy milk\ncall Ada\n")

            with open("todo.txt", encoding="utf-8") as fh:
                for line in fh:
                    print(line.strip())
            ---
            Each line came out of the file as `"buy milk\n"`, with its newline still attached, and `print` added a second one. `strip()` takes the newline off before `print` adds its own.
            ```

            In a file, every line ends with the newline character `\n` that you met in the Data Types
            chapter. The loop hands you each line with that character still on it.

            ```predict
            with open("pets.txt", "w", encoding="utf-8") as fh:
                fh.write("cat\nhorse\n")

            with open("pets.txt", encoding="utf-8") as fh:
                for line in fh:
                    print(len(line), len(line.strip()))
            ---
            The first line the loop gets is `"cat\n"`: three letters and a newline, so 4 characters, and 3 after `strip()`. The second is `"horse\n"`: 6 characters, and 5 after `strip()`.
            ```

            To a `for` loop, an open file behaves like a list of its lines. The trace below uses such a
            list, so that you can see every value. Press Next and compare `line` with `item`:

            ```diagram
            {"type": "trace", "title": "Looping over the lines of todo.txt", "code": ["lines = [\"buy milk\\n\", \"call Ada\\n\"]", "for line in lines:", "    item = line.strip()", "    print(\"item:\", item)", "print(\"done\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']"}, "out": ""},
              {"line": 3, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'buy milk\\n'"}, "out": ""},
              {"line": 4, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'buy milk\\n'", "item": "'buy milk'"}, "out": ""},
              {"line": 2, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'buy milk\\n'", "item": "'buy milk'"}, "out": "item: buy milk\n"},
              {"line": 3, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'call Ada\\n'", "item": "'buy milk'"}, "out": "item: buy milk\n"},
              {"line": 4, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'call Ada\\n'", "item": "'call Ada'"}, "out": "item: buy milk\n"},
              {"line": 2, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'call Ada\\n'", "item": "'call Ada'"}, "out": "item: buy milk\nitem: call Ada\n"},
              {"line": 5, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'call Ada\\n'", "item": "'call Ada'"}, "out": "item: buy milk\nitem: call Ada\n"},
              {"line": null, "vars": {"lines": "['buy milk\\n', 'call Ada\\n']", "line": "'call Ada\\n'", "item": "'call Ada'"}, "out": "item: buy milk\nitem: call Ada\ndone\n"}
            ]}
            ```

            **Watch out:** the file is open only inside the `with` block. A loop that is not indented
            under the `with` runs after the file was closed, and Python stops with
            `ValueError: I/O operation on closed file.`

            **In short:** `with open(name, encoding="utf-8") as fh:` opens a file, and `for line in fh:`
            hands you its lines one at a time, each still ending in `\n`.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            The file `notes.txt` holds two lines of text: `hello` and `world`. Read the program in the
            editor and type exactly what it prints, one line for each `print` that runs.
        ''',
        "setup_files": {
            "notes.txt": r'''
                hello
                world
            ''',
        },
        "code": r'''
            count = 0
            with open("notes.txt", encoding="utf-8") as fh:
                for line in fh:
                    count += 1
                    print(count, line.strip().upper())
            print("lines:", count)
        ''',
        "solution": r'''
            1 HELLO
            2 WORLD
            lines: 2
        ''',
        "explanation": r'''
            The loop runs once for each line of the file, so twice. On the first iteration `count` goes
            from 0 to 1, and `line` is `"hello\n"`. `strip()` takes off the newline and `upper()` makes
            capital letters, so the program prints `1 HELLO`. The second iteration prints `2 WORLD` in the
            same way. The last `print` is not indented under the `with`, so it runs once, after the loop
            is over and the file is closed. `count` is an ordinary variable, and it still holds 2.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "A `for` loop over an open file runs its body once for each line of the file. How many lines does `notes.txt` have?",
            "On every iteration `count` goes up by 1 first. Then one line is printed: the count, followed by the line of the file without its newline and in capital letters.",
            "Your first two lines each have a number, a space and one word in capitals. Your third line comes from the `print` after the loop: the text `lines:`, a space, and the value that `count` has at the end.",
        ],
    },
    {
        "id": "files-s2",
        "lesson": r'''
            ## The whole file as one string

            A chat app keeps its instructions for the model in a text file, so that someone can edit them
            without touching the code. The app does not want those instructions line by line. It wants the
            entire text in one string, ready to send.

            ```python
            with open("poem.txt", "w", encoding="utf-8") as fh:
                fh.write("Roses are red\nViolets are blue\n")

            with open("poem.txt", encoding="utf-8") as fh:
                text = fh.read()
            print(text)
            # Roses are red
            # Violets are blue
            ```

            `fh.read()` hands back everything in the file as one string. The loop from the last step gave
            you one line per iteration. `read()` gives you all of it in one go.

            Look at where the `print` is: it is not indented, so it runs after the `with` block. The file
            is closed by then, and that is fine. `text` is an ordinary string and it is yours to keep. It
            is only `fh` that stops working when the block ends.

            ```quiz
            The `with` block of the example has ended. Which of these lines still works after it?
            - [x] `print(len(text))` :: Right. `text` is a normal string. It was filled while the file was open, and it stays after the file is closed.
            - [ ] `print(fh.read())` :: The block is over, so the file is closed. Python stops with `ValueError: I/O operation on closed file.`
            - [ ] `for line in fh:` with a `print` under it :: A loop reads from the file as well, and the file is closed. It stops with the same `ValueError` as any other read.
            ```

            ### Seeing every character

            The string holds more than you can see. In the file, each line ends with a newline, and
            `read()` changes nothing: you get exactly the characters that are stored. To make them
            visible, print `repr(text)`. `repr` shows a string the way you would type it in code, with
            its quotes and with `\n` for every newline.

            ```python
            with open("poem.txt", "w", encoding="utf-8") as fh:
                fh.write("Roses are red\nViolets are blue\n")

            with open("poem.txt", encoding="utf-8") as fh:
                text = fh.read()
            print(repr(text))
            # 'Roses are red\nViolets are blue\n'
            ```

            ```predict
            with open("pair.txt", "w", encoding="utf-8") as fh:
                fh.write("yes\nno\n")

            with open("pair.txt", encoding="utf-8") as fh:
                text = fh.read()
            print(len(text))
            print(repr(text))
            ---
            `read()` hands back one string with both lines in it. `len` counts every character: the three letters of `yes`, a newline, the two letters of `no` and one more newline. That makes 7.
            ```

            Inside a function you may `return` straight from inside the `with` block. Python still closes
            the file on the way out.

            **Watch out:** a text file normally ends with a newline, so the string from `read()` does
            too. When a file holds the one line `hello`, the test `text == "hello"` is `False`, because
            `text` is `"hello\n"`.

            **In short:** `fh.read()` hands back the whole file as one string, exactly as it is stored,
            newlines included.
        ''',
        "title": "Read the whole file",
        "difficulty": 0,
        "prompt": r'''
            A chat app keeps its system prompt in a text file. The system prompt is the set of
            instructions that is sent to the model before every conversation. To use it, the app needs the
            whole file as one string.

            **Your job:** finish `read_file(path)` so that it gives back everything that is in the file.
            The function is already written except for one gap, marked `___`. Replace the gap.

            **What goes in**
            - `path`: the name of a text file, for example `"prompt.txt"`

            **What comes out**
            - one string with the whole content of the file, for example `"You are helpful.\n"`

            **Rules**
            - The text comes back exactly as it is stored. Nothing is removed, so the newline at the end
              stays.
            - A file with several lines comes back as one string, with a `\n` at the end of each line.

            **Examples**
            ```python
            # prompt.txt holds one line: You are helpful.
            read_file("prompt.txt")   # returns "You are helpful.\n"

            # two.txt holds two lines: a and b
            read_file("two.txt")      # returns "a\nb\n"
            ```
        ''',
        "starter": r'''
            def read_file(path):
                with open(path, encoding="utf-8") as fh:
                    return fh.___()
        ''',
        "setup_files": {
            "prompt.txt": r'''
                You are helpful.
            ''',
        },
        "tests": r'''
            from solution import read_file

            def test_reads_whole_file_keeping_final_newline():
                got = read_file("prompt.txt")
                assert got == "You are helpful.\n", f"got {got!r}"

            def test_reads_all_lines_of_multi_line_file():
                with open("two.txt", "w", encoding="utf-8") as fh:
                    fh.write("a\nb\n")
                got = read_file("two.txt")
                assert got == "a\nb\n", f"got {got!r}"
        ''',
        "solution": r'''
            def read_file(path):
                with open(path, encoding="utf-8") as fh:
                    return fh.read()
        ''',
        "hints": [
            "The chapter has shown two ways to get text out of an open file. One of them hands over everything at once.",
            "No loop is needed here. One method of the file object gives back the whole content as a single string, newlines included.",
            "The gap is the name of that method. It is the one that the lesson's example calls on `fh` to fill the variable `text`.",
        ],
    },
    {
        "id": "files-s3",
        "lesson": r'''
            ## Saving text in a file

            Every example so far began with two lines that made a file. It is time to look at them.
            Suppose your app has a note that should still be there tomorrow:

            ```python
            with open("status.txt", "w", encoding="utf-8") as fh:
                fh.write("draft")

            with open("status.txt", encoding="utf-8") as fh:
                print(fh.read())
            # draft
            ```

            The first `open` has one more argument than the second: `"w"`, for "write". It tells Python
            what you plan to do with the file. With `"w"`, Python makes the file when it does not exist
            yet. `fh.write("draft")` then stores those five characters in it. `write` stores exactly what
            you pass it. Unlike `print`, it does not add a newline.

            This second argument of `open` is called the **mode**. When you leave it out you get `"r"`,
            for "read". That is the mode of every `open` you have used for reading.

            ### "w" always starts from an empty file

            What happens to a file that already has something in it? Make a guess, then find out:

            ```predict
            with open("plan.txt", "w", encoding="utf-8") as fh:
                fh.write("first idea")
            with open("plan.txt", "w", encoding="utf-8") as fh:
                fh.write("better idea")
            with open("plan.txt", encoding="utf-8") as fh:
                print(fh.read())
            ---
            Opening a file in `"w"` mode empties it before anything is written. The second `open` threw `first idea` away, so the file holds only `better idea`.
            ```

            That is what you want when you save a new version of something. It is also how a file gets
            wiped by accident, so use `"w"` only when the old content may go.

            ```fill
            with open("memo.txt", ___, encoding="utf-8") as fh:
                fh.write("call back at 3")
            with open("memo.txt", encoding="utf-8") as fh:
                print(fh.read())
            ---
            - [x] "w" :: Right. Write mode makes `memo.txt`, and `write` can then store the text. The second block reads it back.
            - [ ] "r" :: Read mode never makes a file. There is no `memo.txt` yet, so the `open` line stops with `FileNotFoundError`.
            - [ ] "write" :: The mode is a short fixed code, not a word. Python stops with `ValueError: invalid mode: 'write'`.
            ```

            ### When the mode is left out

            ```quiz
            The file `status.txt` exists. What does this program do?

            ~~~python
            with open("status.txt", encoding="utf-8") as fh:
                fh.write("final")
            ~~~
            - [x] It stops with an error on the `write` line :: Right. With no mode, the file is open for reading only. Python stops with `io.UnsupportedOperation: not writable`.
            - [ ] It replaces the content of the file with `final` :: That needs `"w"` as the second argument. Without a mode, the file is open for reading only, and `write` fails.
            - [ ] It adds `final` to the end of the file :: Nothing is written at all. Without a mode, the file is open for reading only, and `write` fails.
            ```

            **Watch out:** an `open` without a mode can only read. When the file is missing, the `open`
            line stops with `FileNotFoundError: [Errno 2] No such file or directory: 'status.txt'`. When
            the file exists, the `write` line stops with `io.UnsupportedOperation: not writable`. The two
            messages have the same cause: the mode.

            **In short:** `open(name, "w", encoding="utf-8")` makes the file or empties it, and
            `fh.write(text)` stores exactly `text` in it.
        ''',
        "title": "Fix the save",
        "difficulty": 0,
        "prompt": r'''
            A note-taking tool saves the current note under a file name. Saving again under the same name
            replaces the old note. Someone wrote the function for this, and it stops with an error every
            time it is called.

            **Your job:** find the bug in `save_note(path, text)` and fix it. The code is already in the
            editor, and only one line needs to change.

            **What goes in**
            - `path`: the name of the file, for example `"note.txt"`
            - `text`: the text to save, for example `"remember the RAG demo"`

            **What comes out**
            - nothing is returned. The result is the file on disk: after the call it holds exactly `text`.

            **Rules**
            - When the file does not exist yet, it is created.
            - When the file already exists, its old content is replaced, not added to.
            - The file holds `text` exactly as given. No newline is added.

            **Examples**
            ```python
            save_note("note.txt", "remember the RAG demo")
            # note.txt now holds exactly: remember the RAG demo

            save_note("n.txt", "old text")
            save_note("n.txt", "new")
            # n.txt now holds exactly: new
            ```
        ''',
        "starter": r'''
            def save_note(path, text):
                with open(path, encoding="utf-8") as fh:
                    fh.write(text)
        ''',
        "tests": r'''
            from solution import save_note

            def read(path):
                with open(path, encoding="utf-8") as fh:
                    return fh.read()

            def test_creates_file_with_exact_text():
                save_note("note.txt", "remember the RAG demo")
                got = read("note.txt")
                assert got == "remember the RAG demo", f"file contains {got!r}"

            def test_second_save_replaces_old_content():
                save_note("n.txt", "old text")
                save_note("n.txt", "new")
                got = read("n.txt")
                assert got == "new", f"file contains {got!r}"
        ''',
        "solution": r'''
            def save_note(path, text):
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(text)
        ''',
        "hints": [
            "Run the code and read the last line of the error. Then look at the `open` line: which mode does `open` use when you give it none?",
            "With no mode, the file is opened for reading only. A file that does not exist cannot be read, and a file that is open for reading cannot be written to.",
            "Change only the `open` line. Between the path and `encoding`, add the mode from the lesson that makes a missing file and empties an existing one. The `write` line is already right.",
        ],
    },
    {
        "id": "files-s4",
        "lesson": r'''
            ## Add an entry without erasing earlier ones

            A run records when it starts, then records later events as they happen. Replacing the whole log for every event would lose the history. Open the file in a mode that keeps the existing contents and adds new text at the end.

            ```python
            with open("append_demo.txt", "w", encoding="utf-8") as stream:
                stream.write("opened\n")
            with open("append_demo.txt", "a", encoding="utf-8") as stream:
                stream.write("finished\n")
            with open("append_demo.txt", encoding="utf-8") as stream:
                print(repr(stream.read()))
            # 'opened\nfinished\n'
            ```

            The initial write establishes a known starting file. The second block uses **append mode**, written `"a"`, so the earlier line survives. If there were no file yet, append mode would create it. Remember that the `with` block closes the file after the operation.

            ```quiz
            Which mode keeps yesterday's entries when adding today's entry?
            - [x] Append mode. :: Each write goes after the existing contents.
            - [ ] Write mode. :: Opening with write mode first removes the existing contents.
            ```

            A log is a record of events, often with one event per line. The newline is part of that format, not something `write` supplies automatically. Unlike `print`, writing a string stores exactly the characters you pass. If separate entries should be separate lines, each entry needs its line-ending character.

            ```predict
            parts = ["opened", "finished"]
            print(repr("".join(parts)))
            print(repr("\n".join(parts)))
            ---
            Without a separator the words touch. Inserting newline characters creates a boundary between the entries.
            ```

            **Watch out:** append mode does not repair an existing file that lacks a final newline. It begins writing immediately after the last existing character.

            Choose append mode to preserve history and include the separators your file format requires.
        ''',
        "title": "Add a line",
        "difficulty": 0,
        "prompt": r'''
            Add one line to the end of a to-do or log file.

            **Your job:** write `add_line(path, text)`

            **What goes in**
            - `path`: the file name, a string like `"todo.txt"`
            - `text`: the line to add, without a newline, e.g. `"ship it"`

            **What comes out**
            - nothing (`None`). The result is the file on disk.

            **Rules**
            - Write `text` followed by a newline (`"\n"`) at the **end** of the file.
            - Keep everything already in the file (this is called *appending*).
            - If the file does not exist, create it.

            **Examples**
            ```python
            # todo.txt starts with one line: "first\n"
            add_line("todo.txt", "second")
            # todo.txt is now "first\nsecond\n"

            # new.txt does not exist yet
            add_line("new.txt", "write tests")
            add_line("new.txt", "ship it")
            # new.txt is now "write tests\nship it\n"
            ```
        ''',
        "starter": r'''
            def add_line(path, text):
                ...
        ''',
        "setup_files": {
            "todo.txt": r'''
                first
            ''',
        },
        "tests": r'''
            from solution import add_line

            def read(path):
                with open(path, encoding="utf-8") as fh:
                    return fh.read()

            def test_creates_missing_file_and_appends_in_order():
                add_line("new.txt", "write tests")
                add_line("new.txt", "ship it")
                got = read("new.txt")
                assert got == "write tests\nship it\n", f"file contains {got!r}"

            def test_keeps_existing_lines():
                add_line("todo.txt", "second")
                got = read("todo.txt")
                assert got == "first\nsecond\n", f"file contains {got!r}"
        ''',
        "solution": r'''
            def add_line(path, text):
                with open(path, "a", encoding="utf-8") as fh:
                    fh.write(text + "\n")
        ''',
        "hints": [
            "Choose a mode that preserves what is already on disk.",
            "Each added entry needs its own ending newline.",
            "Open for appending in a with block, write the supplied text and line ending, and leave the function without returning a file value.",
        ],
    },
    {
        "id": "files-s5",
        "lesson": r'''
            ## Choose a fallback for a missing file

            A first run may have no saved notes yet. That can be an expected starting condition rather than a reason to stop the application. Decide which fallback to use when the requested file has not been created.

            ```python
            with open("reading_demo.txt", "w", encoding="utf-8") as stream:
                stream.write("saved notes")
            try:
                with open("reading_demo.txt", encoding="utf-8") as stream:
                    loaded = stream.read()
            except FileNotFoundError as missing:
                loaded = "no saved notes"
            print(loaded)
            # saved notes
            ```

            The try block includes opening and reading. Opening for reading does not create a missing file: it raises `FileNotFoundError`. The named handler supplies a **fallback**, a value chosen when the intended value is unavailable. On the successful path, the actual file contents are used instead.

            ```quiz
            A file exists but contains no text. Is that the same event as FileNotFoundError?
            - [x] No; reading succeeded and returned an empty string. :: Missing content and a missing file are different conditions.
            - [ ] Yes; every empty read raises the missing-file exception. :: Empty files can be opened and read normally.
            ```

            Catch the specific absence you intend to tolerate. Other failures, such as permission problems, can mean something different and should remain visible unless the contract explicitly handles them. A broad exception handler could even hide a bug in your own code.

            ```match
            successful read :: use the file's contents
            missing file :: select the specified fallback
            unrelated programming error :: leave the error visible
            ```

            **Watch out:** trimming the loaded text is an additional transformation. If the task promises exact contents, surrounding spaces and the final newline belong to the returned value too.

            Handle the missing-file case without silently changing successful reads.
        ''',
        "title": "Missing file? No problem",
        "difficulty": 0,
        "prompt": r'''
            Read a file that may or may not exist, without crashing.

            **Your job:** write `read_or_empty(path)`

            **What goes in**
            - `path`: the file name, a string like `"notes.txt"`

            **What comes out**
            - a string: the file's full contents, or `""` (an empty string)

            **Rules**
            - If the file exists, return its contents exactly as stored (do not strip).
            - If the file does not exist, return `""`. Opening a missing file raises
              `FileNotFoundError`, so catch that.

            **Examples**
            ```python
            # notes.txt contains one line: some notes
            read_or_empty("notes.txt")     # returns "some notes\n"
            read_or_empty("missing.txt")   # returns ""
            ```
        ''',
        "starter": r'''
            def read_or_empty(path):
                ...
        ''',
        "setup_files": {
            "notes.txt": r'''
                some notes
            ''',
        },
        "tests": r'''
            from solution import read_or_empty

            def test_existing_file_returns_full_contents():
                got = read_or_empty("notes.txt")
                assert got == "some notes\n", f"got {got!r}"

            def test_missing_file_returns_empty_string():
                got = read_or_empty("missing.txt")
                assert got == "", f"got {got!r}"
        ''',
        "solution": r'''
            def read_or_empty(path):
                try:
                    with open(path, encoding="utf-8") as fh:
                        return fh.read()
                except FileNotFoundError:
                    return ""
        ''',
        "hints": [
            "Distinguish an absent file from an existing file with empty contents.",
            "Catch the missing-file exception around the open and read operation.",
            "Give back the full successful read unchanged, or the specified fallback only when the file cannot be found.",
        ],
    },
    {
        "id": "files-s6",
        "lesson": r'''
            ## Work with a file name's parts

            A pipeline reads a document in a nested folder and needs a related output name. Cutting the path by hand becomes awkward when folders or filenames contain extra dots. Use a path object to ask for the specific part you need.

            ```python
            from pathlib import Path
            source = Path("archive/reports/draft.v2.md")
            print(source.name)
            # draft.v2.md
            print(source.stem)
            # draft.v2
            print(source.suffix)
            # .md
            ```

            The `pathlib` module provides `Path`, which represents a filesystem location. The import makes that name available directly. The **stem** is the filename with its final extension removed; the **suffix** is that final extension, including the dot. The full filename is available as `name`.

            ```match
            `Path("a/b.txt").name` :: b.txt
            `Path("a/b.txt").stem` :: b
            `Path("a/b.txt").suffix` :: .txt
            ```

            A Path can represent a location that does not exist. Reading these parts only examines the path; it does not open or create the file. That makes it useful for planning output names before doing any disk work.

            ```predict
            from pathlib import Path
            location = Path("reports") / "new.txt"
            print(str(location))
            print(Path("bundle.tar.gz").stem)
            ---
            The slash joins a folder and name. Only the final .gz extension is removed from the second path's stem.
            ```

            The slash operator joins a Path with another path component. Converting a Path with `str` gives its text representation when a function contract requires a string rather than a Path object.

            **Watch out:** splitting at the first dot discards meaningful earlier parts such as `draft.v2`. Use the final-extension behavior when that is the requirement.

            Ask a Path for its parts instead of guessing where to cut a filename.
        ''',
        "title": "Name the output file",
        "difficulty": 0,
        "prompt": r'''
            A pipeline reads `docs/guide.md` and saves its results as `guide.json`. Build that
            output file name.

            **Your job:** write `output_name(src)` using `pathlib.Path`

            **What goes in**
            - `src`: a file path as a string, e.g. `"docs/guide.md"`

            **What comes out**
            - a string: the source file name **without its folders and extension**,
              followed by `.json`

            **Rules**
            - Drop every folder part: `"a/b/notes.txt"` gives `"notes.json"`.
            - Only the **last** extension is replaced: `"data.tar.gz"` gives `"data.tar.json"`.
            - Import and use `pathlib` (a check looks for it).

            **Examples**
            ```python
            output_name("docs/guide.md")    # returns "guide.json"
            output_name("a/b/notes.txt")    # returns "notes.json"
            output_name("data.tar.gz")      # returns "data.tar.json"
            ```
        ''',
        "starter": r'''
            from pathlib import Path


            def output_name(src):
                ...
        ''',
        "tests": r'''
            from solution import output_name

            def test_folder_is_dropped_and_extension_replaced():
                got = output_name("docs/guide.md")
                assert got == "guide.json", f"got {got!r}"

            def test_deeper_folders_are_dropped():
                got = output_name("a/b/notes.txt")
                assert got == "notes.json", f"got {got!r}"

            def test_only_last_extension_is_replaced():
                got = output_name("data.tar.gz")
                assert got == "data.tar.json", f"got {got!r}"

            def test_returns_a_string_and_uses_pathlib():
                assert isinstance(output_name("x.md"), str), "return a str, not a Path"
                assert "pathlib" in source(), "use pathlib"
        ''',
        "solution": r'''
            from pathlib import Path


            def output_name(src):
                return Path(src).stem + ".json"
        ''',
        "hints": [
            "Path has an attribute for the final filename without its last extension.",
            "Ignore folder components and preserve any earlier dots in the filename.",
            "Create the path representation, read the appropriate filename part, and attach the new extension as text.",
        ],
    },
    {
        "id": "files-1",
        "lesson": r'''
            ## Clean the outside of a loaded prompt

            An instruction file often ends with a newline and may have blank lines around its contents. Those outer characters are usually editor layout, while spaces and line breaks inside the instruction can matter. Read the text first, then remove only the unwanted outer whitespace.

            ```python
            with open("prompt_demo.txt", "w", encoding="utf-8") as stream:
                stream.write("\n  Keep answers short.\nUse examples.  \n")
            with open("prompt_demo.txt", encoding="utf-8") as stream:
                instruction = stream.read().strip()
            print(repr(instruction))
            # 'Keep answers short.\nUse examples.'
            ```

            The two sentences still have their internal newline. `strip` acts at the boundaries, not throughout the text. This is different from the whitespace normalisation you practiced in Strings, which rebuilt text from individual words.

            ```predict
            raw = "  Be brief.\nKeep CODE intact.  "
            print(repr(raw.strip()))
            ---
            Only the leading and trailing spaces are removed. The internal newline and capital letters are preserved.
            ```

            Combine that successful-read behavior with the missing-file policy from the previous step. A missing file may need a standard instruction, while an existing whitespace-only file successfully cleans to an empty string. Do not silently treat those two events as identical unless the task says to.

            Using an explicit UTF-8 encoding tells Python how stored bytes represent characters. It avoids relying on a machine's default encoding when the prompt includes accented letters or another writing system.

            ```quiz
            If you return from inside a with block, is the file still closed?
            - [x] Yes; leaving the block performs its cleanup. :: A normal return still exits the context correctly.
            - [ ] No; return always skips file cleanup. :: The with statement is specifically designed to handle exits from its body.
            ```

            **Watch out:** catching every exception as a missing prompt can hide a decoding or permission problem. Handle the specific missing-file error.

            Preserve the instruction's interior while cleaning its outer boundary.
        ''',
        "hints": [
            "The successful-read cleanup and missing-file fallback are different cases.",
            "Read with the required encoding and remove only outer whitespace.",
            "Use a with block inside the protected read, return its trimmed text, and provide the standard prompt only for a missing file.",
        ],
        "title": "Load a system prompt",
        "difficulty": 1,
        "prompt": r'''
            Chat apps often keep the system prompt in a text file. Load it, with a safe default.

            **Your job:** write `load_prompt(path)`

            **What goes in**
            - `path`: the file name, a string like `"system.txt"`

            **What comes out**
            - a string: the file's text with surrounding whitespace stripped

            **Rules**
            - Remove whitespace (spaces, tabs, blank lines, newlines) from the **start and end**
              of the text. Whitespace inside the text stays.
            - If the file does not exist, return `"You are a helpful assistant."` instead of crashing.
            - Open the file with a `with` statement and pass `encoding="utf-8"` (a check looks for
              both), so accented letters and other writing systems are read correctly.

            **Examples**
            ```python
            # system.txt contains: You are a terse code reviewer.  (plus a newline)
            load_prompt("system.txt")    # returns "You are a terse code reviewer."

            # padded.txt contains "\n\n   Answer in JSON.  \t\n\n"
            load_prompt("padded.txt")    # returns "Answer in JSON."

            load_prompt("missing.txt")   # returns "You are a helpful assistant."
            ```
        ''',
        "starter": r'''
            def load_prompt(path):
                ...
        ''',
        "setup_files": {
            "system.txt": r'''
                You are a terse code reviewer.
            ''',
        },
        "tests": r'''
            from solution import load_prompt

            def test_reads_prompt_file():
                got = load_prompt("system.txt")
                assert got == "You are a terse code reviewer.", f"got {got!r}"

            def test_strips_surrounding_whitespace_and_blank_lines():
                with open("padded.txt", "w", encoding="utf-8") as fh:
                    fh.write("\n\n   Answer in JSON.  \t\n\n")
                got = load_prompt("padded.txt")
                assert got == "Answer in JSON.", f"got {got!r}"

            def test_missing_file_returns_default_prompt():
                got = load_prompt("missing.txt")
                assert got == "You are a helpful assistant.", f"got {got!r}"

            def test_reads_accented_utf8_text():
                with open("unicode.txt", "w", encoding="utf-8") as fh:
                    fh.write("Réponds en français.\n")
                got = load_prompt("unicode.txt")
                assert got == "Réponds en français.", f"got {got!r}"

            def test_uses_with_statement_and_encoding():
                src = source()
                assert "with " in src, "open the file in a with statement"
                assert "encoding" in src, "pass an explicit encoding"
        ''',
        "solution": r'''
            DEFAULT = "You are a helpful assistant."


            def load_prompt(path):
                try:
                    with open(path, encoding="utf-8") as fh:
                        return fh.read().strip()
                except FileNotFoundError:
                    return DEFAULT
        ''',
    },
    {
        "id": "files-2",
        "lesson": r'''
            ## Write a line format you can read back

            A log needs enough structure to tell which event produced each line. If every writer uses a different separator, the reader becomes unreliable. Choose an exact line format and preserve it in both directions.

            ```python
            with open("events_demo.txt", "w", encoding="utf-8") as stream:
                stream.write("info: ready\n\nwarn: slow \n")
            with open("events_demo.txt", encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        print(repr(line.rstrip("\n")))
            # 'info: ready'
            # 'warn: slow '
            ```

            Iterating over the open file gives one line at a time, normally including its newline. The condition uses a trimmed copy to decide whether there is content. The output removes only the newline, so meaningful surrounding spaces in a nonblank entry survive.

            ```predict
            line = "warn: slow \n"
            print(repr(line.strip()))
            print(repr(line.rstrip("\n")))
            ---
            Strip removes both the trailing space and newline. Restricting rstrip to newline preserves the trailing space.
            ```

            A **line format** is the agreement about separators, field order, and line endings. Follow it exactly when writing: a missing space after a colon may still look readable but violate what another program expects. Append mode keeps previous entries, while a final newline makes the next entry begin on its own line.

            ```quiz
            Why test a trimmed copy but keep a less-trimmed result?
            - [x] Detect blank lines without destroying spaces in useful entries. :: Selection and output cleaning have different responsibilities.
            - [ ] File readers cannot return strings containing spaces. :: They can; preserving or removing spaces is your choice.
            ```

            **Watch out:** assigning or returning the number produced by `write` does not return the written text. Writing changes the file; the reader separately reconstructs the lines.

            Keep writing rules exact and reading transformations no broader than required.
        ''',
        "hints": [
            "The writer adds formatted lines; the reader preserves their order.",
            "Use append mode when writing and remove only line endings when reading useful lines.",
            "Write the exact separator format plus newline, then have the reader skip blank lines and collect the remaining entries without their newline characters.",
        ],
        "title": "Conversation log",
        "difficulty": 1,
        "prompt": r'''
            Keep a simple conversation log on disk: one line per message.

            **Your job:** write two functions.

            `log_message(path, role, content)`
            - `path`: the log file name, e.g. `"chat.log"`
            - `role`: a string like `"user"` or `"assistant"`
            - `content`: the message text, e.g. `"hi"`

            **What comes out**
            - nothing (`None`). It adds one line to the file.

            `read_log(path)`
            - `path`: the log file name

            **What comes out**
            - a list of strings, one per line of the file

            **Rules**
            - `log_message` writes exactly `<role>: <content>` (colon, one space) followed by `"\n"`.
            - `log_message` **appends**: lines already in the file are kept. A missing file is created.
            - `read_log` returns the lines in file order, **without** their trailing `"\n"`.
            - `read_log` skips empty (blank) lines.

            **Examples**
            ```python
            log_message("chat.log", "user", "hi")
            log_message("chat.log", "assistant", "hello")
            # chat.log now contains "user: hi\nassistant: hello\n"
            read_log("chat.log")   # returns ["user: hi", "assistant: hello"]

            # old.log contains "system: be brief\n\nuser: first\n" (note the blank line)
            log_message("old.log", "assistant", "ok")
            read_log("old.log")    # returns ["system: be brief", "user: first", "assistant: ok"]
            ```
        ''',
        "starter": r'''
            def log_message(path, role, content):
                ...


            def read_log(path):
                ...
        ''',
        "setup_files": {
            "old.log": r'''
                system: be brief

                user: first
            ''',
        },
        "tests": r'''
            from solution import log_message, read_log

            def test_log_message_appends_exact_lines():
                log_message("chat.log", "user", "hi")
                log_message("chat.log", "assistant", "hello")
                with open("chat.log", encoding="utf-8") as fh:
                    text = fh.read()
                assert text == "user: hi\nassistant: hello\n", f"file contains {text!r}"

            def test_keeps_existing_lines_and_skips_blank_ones():
                log_message("old.log", "assistant", "ok")
                got = read_log("old.log")
                assert got == ["system: be brief", "user: first", "assistant: ok"], f"got {got!r}"

            def test_read_log_returns_lines_without_newlines():
                got = read_log("chat.log")
                assert all(not line.endswith("\n") for line in got), f"got {got!r}"
                assert got == ["user: hi", "assistant: hello"], f"got {got!r}"
        ''',
        "solution": r'''
            def log_message(path, role, content):
                with open(path, "a", encoding="utf-8") as fh:
                    fh.write(f"{role}: {content}\n")


            def read_log(path):
                with open(path, encoding="utf-8") as fh:
                    return [line.rstrip("\n") for line in fh if line.strip()]
        ''',
    },
    {
        "id": "files-7",
        "lesson": r'''
            ## Prepare a folder before writing into it

            A document job saves results into a new output folder. Creating the file does not automatically create every folder above it. Prepare the destination structure first so the same code works on both the first run and later runs.

            ```python
            from pathlib import Path
            folder = Path("chunk_demo")
            folder.mkdir(exist_ok=True)
            output = folder / "sample.txt"
            output.write_text("stored text", encoding="utf-8")
            print(output.read_text(encoding="utf-8"))
            # stored text
            print(output.is_file())
            # True
            ```

            The `mkdir` method creates a directory, another word for a folder. `exist_ok=True` accepts a directory that is already there, so rerunning the example is harmless. The joined output path then identifies the file inside it.

            ```quiz
            Does constructing `Path("new/folder/file.txt")` create those folders?
            - [x] No; it only represents the location. :: Creation needs a filesystem operation such as mkdir.
            - [ ] Yes; every Path constructor writes to disk. :: You can represent nonexistent locations without creating them.
            ```

            `write_text` opens the file, writes the supplied string, and closes it. It replaces an existing file's contents and adds no newline of its own. `read_text` performs the corresponding whole-file read. Supplying UTF-8 in both directions makes the intended character encoding explicit.

            A destination can have several missing folder levels. The Path documentation lists an additional `mkdir` option for creating missing parents. Read that entry and distinguish it from the option that tolerates an existing destination: they solve different problems.

            ```match
            `mkdir` :: create the destination directory
            `write_text` :: replace file contents with text
            `str(path)` :: obtain a path's string representation
            ```

            **Watch out:** without creating missing parent directories, writing the final file raises `FileNotFoundError` even though you intended to create that file.

            Prepare the directory tree, then write the file at the joined destination.
        ''',
        "research": {"note": "Read the documentation of `Path.mkdir` to find how to create missing parent folders too, then come back.",
         "links": [{"title": "pathlib Path.mkdir - Python docs", "url": "https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir"}]},
        "title": "Save a chunk into a folder",
        "difficulty": 1,
        "prompt": r'''
            A document splitter saves each chunk as its own file inside an output folder that
            may not exist yet.

            **Your job:** write `save_chunk(folder, name, text)` using `pathlib`

            **What goes in**
            - `folder`: the output folder, a string like `"out/chunks"` (may be several levels deep)
            - `name`: the file name, a string like `"c1.txt"`
            - `text`: the chunk text, e.g. `"RAG = retrieval + generation"`

            **What comes out**
            - a string: the path of the written file, `folder` and `name` joined with
              `/`, e.g. `"out/chunks/c1.txt"`

            **Rules**
            - Create `folder`, **including any missing parent folders**. If it already exists,
              that is fine (no error).
            - Write `text` exactly as given (no newline added), with UTF-8 encoding
              (accented letters must work). An existing file with that name is replaced.
            - Import and use `pathlib` (a check looks for it).

            **Examples**
            ```python
            save_chunk("out/chunks", "c1.txt", "RAG = retrieval + generation")
            # returns "out/chunks/c1.txt"; that file now contains exactly the text

            save_chunk("out/chunks", "c2.txt", "café")   # folder already exists: fine
            # returns "out/chunks/c2.txt"
            ```
        ''',
        "starter": r'''
            from pathlib import Path


            def save_chunk(folder, name, text):
                ...
        ''',
        "tests": r'''
            from pathlib import Path
            from solution import save_chunk

            def test_creates_nested_folders_and_writes_text():
                got = save_chunk("out/chunks", "c1.txt", "RAG = retrieval + generation")
                assert got == "out/chunks/c1.txt", f"returned {got!r}"
                content = Path("out/chunks/c1.txt").read_text(encoding="utf-8")
                assert content == "RAG = retrieval + generation", f"file contains {content!r}"

            def test_existing_folder_is_fine_and_utf8_works():
                save_chunk("box", "a.txt", "one")
                got = save_chunk("box", "b.txt", "café")
                assert got == "box/b.txt", f"returned {got!r}"
                assert Path("box/b.txt").read_text(encoding="utf-8") == "café"

            def test_existing_file_is_replaced():
                save_chunk("r", "x.txt", "old text")
                save_chunk("r", "x.txt", "new")
                assert Path("r/x.txt").read_text(encoding="utf-8") == "new"

            def test_uses_pathlib():
                assert "pathlib" in source(), "use pathlib"
        ''',
        "solution": r'''
            from pathlib import Path


            def save_chunk(folder, name, text):
                out = Path(folder)
                out.mkdir(parents=True, exist_ok=True)
                path = out / name
                path.write_text(text, encoding="utf-8")
                return str(path)
        ''',
        "hints": [
            "Represent the destination directory and filename separately before joining them.",
            "Directory creation must handle both missing parents and an already-existing destination.",
            "Prepare the full directory tree, join the filename, write the exact text with UTF-8, and return the written path as a string.",
        ],
    },
    {
        "id": "files-8",
        "lesson": r'''
            ## Find matching names in one folder

            Your document importer should consider text documents but ignore images and unrelated files. Instead of opening everything, ask the folder for names matching a pattern. Then choose how those results should be presented.

            ```python
            from pathlib import Path
            folder = Path("glob_demo")
            folder.mkdir(exist_ok=True)
            for name in ["b.txt", "a.txt", "c.csv"]:
                (folder / name).write_text("example", encoding="utf-8")
            print(sorted(path.name for path in folder.glob("*.txt")))
            # ['a.txt', 'b.txt']
            ```

            The star stands for any sequence of characters. A filename pattern such as this is a **glob pattern**. A simple pattern looks directly inside the selected directory; it does not descend into every subfolder. Each match is a Path, whose `name` gives only the final filename.

            ```match
            `*.txt` :: names ending in .txt
            `path.name` :: final name without its folder prefix
            `sorted(names)` :: names in predictable increasing order
            ```

            Filesystem listing order is not a promise. If your importer or its tests need alphabetical output, explicitly sort the names. Sorting creates a new ordered list; the Sorting chapter will explore more ways to control that order later.

            ```quiz
            Why sort after gathering matching names?
            - [x] The order returned by the filesystem may vary. :: Explicit ordering makes results repeatable.
            - [ ] Glob always returns names backwards. :: There is no guaranteed default alphabetical direction to reverse.
            ```

            A missing folder yields no matches for this basic glob operation. Decide whether that means an empty result or an application error according to the task's contract. Also remember that a name match alone is not a universal proof that the path is a regular file; `is_file` can check that when required.

            **Watch out:** returning the whole Path gives a folder prefix the caller may not want. Match the promised output shape.

            Select the matching locations, extract the requested names, and order them explicitly.
        ''',
        "title": "List the markdown docs",
        "difficulty": 1,
        "prompt": r'''
            Find the markdown documents your RAG app should index.

            **Your job:** write `list_docs(folder)` using `pathlib`

            **What goes in**
            - `folder`: a folder name, a string like `"kb"`

            **What comes out**
            - a list of file **names** (strings like `"faq.md"`, no folder part) of
              every `.md` file **directly** inside `folder`

            **Rules**
            - Only names ending in `.md`. Other files are ignored.
            - Files in subfolders are ignored.
            - The list is sorted alphabetically.
            - An empty folder, or a folder that does not exist, gives `[]`.

            **Examples**
            ```text
            kb/
              intro.md
              faq.md
              notes.txt        (ignored)
              old/archive.md   (ignored: in a subfolder)
            ```
            ```python
            list_docs("kb")         # returns ["faq.md", "intro.md"]
            list_docs("nowhere")    # returns []
            ```
        ''',
        "starter": r'''
            from pathlib import Path


            def list_docs(folder):
                ...
        ''',
        "setup_files": {
            "kb/intro.md": "# Intro\n",
            "kb/faq.md": "# FAQ\n",
            "kb/notes.txt": "not markdown\n",
            "kb/old/archive.md": "# Old\n",
        },
        "tests": r'''
            import os
            from solution import list_docs

            def test_lists_md_names_sorted():
                got = list_docs("kb")
                assert got == ["faq.md", "intro.md"], f"got {got!r}"

            def test_names_have_no_folder_part():
                got = list_docs("kb")
                assert all("/" not in n and "kb" not in n for n in got), f"got {got!r}"

            def test_empty_or_missing_folder_gives_empty_list():
                os.mkdir("empty")
                assert list_docs("empty") == [], f"got {list_docs('empty')!r}"
                assert list_docs("nowhere") == [], f"got {list_docs('nowhere')!r}"
        ''',
        "solution": r'''
            from pathlib import Path


            def list_docs(folder):
                names = []
                for path in Path(folder).glob("*.md"):
                    names.append(path.name)
                return sorted(names)
        ''',
        "hints": [
            "A simple glob pattern searches directly inside one folder.",
            "Keep only each matched name rather than its full path, then choose a predictable order.",
            "Gather names matching the markdown suffix and sort the resulting strings; no matches should produce an empty list.",
        ],
    },
    {
        "id": "files-3",
        "hints": [
            "All four measurements can come from the same full-text read.",
            "Count characters before removing line endings, but compare line lengths without them.",
            "Read once, derive words and lines, track the earliest strictly longest line using one-based numbering, and assemble the four fields with the empty-file defaults.",
        ],
        "title": "Document stats",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Before chunking a document for an AI app, it helps to know its size.

            **Your job:** write `file_stats(path)`

            **What goes in**
            - `path`: the file name, a string like `"doc.txt"`

            **What comes out**
            - a dict with exactly these four keys (all ints):
              `{"lines": ..., "words": ..., "chars": ..., "longest_line": ...}`

            **Rules**
            - `lines`: number of lines. A last line without a trailing newline still counts.
              An empty file has `0` lines.
            - `words`: number of whitespace-separated words in the whole file.
            - `chars`: total number of characters in the file, **including** newline characters.
            - `longest_line`: the **1-based** line number (first line is `1`) of the longest line,
              not counting its newline. On a tie, the first one wins. `0` for an empty file.
            - If the file does not exist, a `FileNotFoundError` must be raised (just let `open`
              raise it).

            **Examples**
            ```python
            # doc.txt contains these 3 lines (each ends with a newline):
            #   Retrieval augmented generation
            #   combines search with a language model.
            #   Neat.
            file_stats("doc.txt")
            # returns {"lines": 3, "words": 10, "chars": 76, "longest_line": 2}

            # n.txt contains "aa\nbbbb\ncc" (no newline at the end)
            file_stats("n.txt")   # returns {"lines": 3, "words": 3, "chars": 10, "longest_line": 2}

            # t.txt contains "xyz\nabc\n" (a tie)
            file_stats("t.txt")["longest_line"]   # returns 1

            # e.txt is empty
            file_stats("e.txt")   # returns {"lines": 0, "words": 0, "chars": 0, "longest_line": 0}

            file_stats("missing.txt")   # raises FileNotFoundError
            ```
        ''',
        "starter": r'''
            def file_stats(path):
                ...
        ''',
        "setup_files": {
            "doc.txt": r'''
                Retrieval augmented generation
                combines search with a language model.
                Neat.
            ''',
            "empty.txt": "",
        },
        "tests": r'''
            from solution import file_stats

            def test_stats_for_three_line_doc():
                got = file_stats("doc.txt")
                expected = {"lines": 3, "words": 10, "chars": 76, "longest_line": 2}
                assert got == expected, f"got {got!r}"

            def test_last_line_without_newline_still_counts():
                with open("n.txt", "w", encoding="utf-8") as fh:
                    fh.write("aa\nbbbb\ncc")
                got = file_stats("n.txt")
                assert got == {"lines": 3, "words": 3, "chars": 10, "longest_line": 2}, f"got {got!r}"

            def test_tie_for_longest_line_first_wins():
                with open("t.txt", "w", encoding="utf-8") as fh:
                    fh.write("xyz\nabc\n")
                assert file_stats("t.txt")["longest_line"] == 1

            def test_empty_file_is_all_zeros():
                with open("e.txt", "w", encoding="utf-8") as fh:
                    fh.write("")
                got = file_stats("e.txt")
                assert got == {"lines": 0, "words": 0, "chars": 0, "longest_line": 0}, f"got {got!r}"

            def test_missing_file_raises_file_not_found():
                try:
                    file_stats("missing.txt")
                except FileNotFoundError:
                    return
                assert False, "expected FileNotFoundError"
        ''',
        "solution": r'''
            def file_stats(path):
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                lines = text.splitlines()
                longest, best_len = 0, -1
                for i, line in enumerate(lines, start=1):
                    if len(line) > best_len:
                        longest, best_len = i, len(line)
                return {
                    "lines": len(lines),
                    "words": len(text.split()),
                    "chars": len(text),
                    "longest_line": longest,
                }
        ''',
    },
    {
        "id": "files-4",
        "hints": [
            "Separate naming and grouping from the actual file writes.",
            "Advance through the word list by the chunk size, giving each slice the next number.",
            "Prepare the destination, read and split the source, write each space-joined group under its numbered stem-based name, and return only those names in order.",
        ],
        "title": "Split into chunk files",
        "difficulty": 2,
        "prompt": r'''
            RAG pipelines split long documents into small chunks. Write each chunk to its own file.

            **Your job:** write `write_chunks(src, out_dir, size)` using `pathlib`

            **What goes in**
            - `src`: the source text file, a string like `"notes.md"` or a `Path`
            - `out_dir`: the output folder, a string like `"build/chunks"` or a `Path`
            - `size`: max words per chunk, an int like `2`

            **What comes out**
            - a list of the written file **names** (just names like `"notes_1.txt"`,
              not full paths), in order

            **Rules**
            - Split the file's text into whitespace-separated words, then group them into chunks of
              at most `size` words (the last chunk may be shorter).
            - Create `out_dir`, including any missing parent folders. If it already exists, that is fine.
            - Write each chunk, words joined by single spaces, to `<out_dir>/<stem>_<n>.txt`, where
              `<stem>` is the source file name without its extension and `n` starts at `1`.
            - Both `src` and `out_dir` may be strings or `Path` objects.
            - Import and use `pathlib` (a check looks for it).

            **Examples**
            ```python
            # notes.md contains "one two\nthree four five\n" (5 words)
            write_chunks("notes.md", "build/chunks", 2)
            # returns ["notes_1.txt", "notes_2.txt", "notes_3.txt"]
            # build/chunks/notes_1.txt contains "one two"
            # build/chunks/notes_2.txt contains "three four"
            # build/chunks/notes_3.txt contains "five"

            write_chunks("notes.md", "a/b/c", 10)             # returns ["notes_1.txt"] (a/b/c is created)
            write_chunks(Path("notes.md"), Path("exists"), 5)  # returns ["notes_1.txt"]
            ```
        ''',
        "starter": r'''
            from pathlib import Path


            def write_chunks(src, out_dir, size):
                ...
        ''',
        "setup_files": {
            "notes.md": r'''
                one two
                three four five
            ''',
        },
        "tests": r'''
            from pathlib import Path
            from solution import write_chunks

            def test_returns_chunk_file_names_in_order():
                got = write_chunks("notes.md", "build/chunks", 2)
                assert got == ["notes_1.txt", "notes_2.txt", "notes_3.txt"], f"got {got!r}"

            def test_chunk_files_contain_space_joined_words():
                write_chunks("notes.md", "out", 2)
                texts = [Path("out", f"notes_{i}.txt").read_text(encoding="utf-8").strip()
                         for i in (1, 2, 3)]
                assert texts == ["one two", "three four", "five"], f"got {texts!r}"

            def test_creates_missing_nested_folders():
                write_chunks("notes.md", "a/b/c", 10)
                assert Path("a/b/c/notes_1.txt").is_file(), "nested output dir not created"

            def test_accepts_path_objects_and_existing_folder():
                Path("exists").mkdir()
                got = write_chunks(Path("notes.md"), Path("exists"), 5)
                assert got == ["notes_1.txt"], f"got {got!r}"

            def test_imports_pathlib():
                assert "pathlib" in source(), "use pathlib"
        ''',
        "solution": r'''
            from pathlib import Path


            def write_chunks(src, out_dir, size):
                src = Path(src)
                out = Path(out_dir)
                out.mkdir(parents=True, exist_ok=True)
                words = src.read_text(encoding="utf-8").split()
                names = []
                for n, start in enumerate(range(0, len(words), size), start=1):
                    name = f"{src.stem}_{n}.txt"
                    (out / name).write_text(" ".join(words[start:start + size]), encoding="utf-8")
                    names.append(name)
                return names
        ''',
    },
    {
        "id": "files-5",
        "research": {"note": "This one needs two pathlib tools you have not used yet: walking a folder recursively and turning a full path into one relative to a root folder. Read about them, then come back.",
         "links": [{"title": "pathlib Path.rglob - Python docs", "url": "https://docs.python.org/3/library/pathlib.html#pathlib.Path.rglob"},
                   {"title": "pathlib PurePath.relative_to - Python docs", "url": "https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.relative_to"}]},
        "hints": [
            "This search includes subfolders, unlike the previous direct-folder listing.",
            "Determine eligible files first, then compute each file's path, type, word count, and title.",
            "Check the root, gather matching paths recursively with case-insensitive extensions, sort the relative path strings, and build entries with the specified title fallback.",
        ],
        "title": "Index a document folder",
        "difficulty": 3,
        "prompt": r'''
            Before building a RAG index you need an inventory of the source documents.

            **Your job:** write `index_folder(root)`

            **What goes in**
            - `root`: a folder name, a string like `"docs"` (or a `Path`)

            **What comes out**
            - a list of dicts, one per document, like
              `{"path": "guides/setup.md", "type": "md", "words": 6, "title": "Setup guide"}`

            **Rules**
            - Include every `.txt` and `.md` file anywhere under `root`, including subfolders.
              The extension match ignores case (`NOTES.MD` counts). All other files are ignored.
            - `path`: the path relative to `root`, with `/` separators (e.g. `"guides/setup.md"`).
            - `type`: the extension without the dot, lower-case (`"md"` or `"txt"`).
            - `words`: the number of whitespace-separated words in the whole file (so a `#` on its
              own counts as a word).
            - `title`: the first non-blank line, stripped, with leading `#` characters and spaces
              removed. If the file has no non-blank line, use the file name without extension
              (its *stem*).
            - Sort the list by `path` as plain strings (capital letters sort before lowercase ones).
            - If `root` does not exist, raise `FileNotFoundError`.

            **Examples**
            ```text
            docs/
              intro.txt            "Welcome to the handbook\nThis is the intro.\n"
              paper.pdf            (ignored)
              data/raw.json        (ignored)
              guides/setup.md      "\n# Setup guide\n\nInstall the package.\n"
              guides/NOTES.MD      "## Notes\n"
              guides/empty.txt     "" (empty)
            ```
            ```python
            index_folder("docs")
            # returns [
            #   {"path": "guides/NOTES.MD",  "type": "md",  "words": 2, "title": "Notes"},
            #   {"path": "guides/empty.txt", "type": "txt", "words": 0, "title": "empty"},
            #   {"path": "guides/setup.md",  "type": "md",  "words": 6, "title": "Setup guide"},
            #   {"path": "intro.txt",        "type": "txt", "words": 8, "title": "Welcome to the handbook"},
            # ]

            index_folder("no_such_dir")   # raises FileNotFoundError
            ```
        ''',
        "starter": r'''
            from pathlib import Path


            def index_folder(root):
                ...
        ''',
        "setup_files": {
            "docs/intro.txt": r'''
                Welcome to the handbook
                This is the intro.
            ''',
            "docs/guides/setup.md": r'''

                # Setup guide

                Install the package.
            ''',
            "docs/guides/NOTES.MD": r'''
                ## Notes
            ''',
            "docs/guides/empty.txt": "",
            "docs/data/raw.json": r'''
                {"skip": true}
            ''',
            "docs/paper.pdf": "not really a pdf",
        },
        "tests": r'''
            from solution import index_folder

            def test_finds_only_txt_and_md_files_sorted_by_path():
                got = [d["path"] for d in index_folder("docs")]
                expected = ["guides/NOTES.MD", "guides/empty.txt", "guides/setup.md", "intro.txt"]
                assert got == expected, f"got {got!r}"

            def test_entry_has_path_type_words_and_title():
                entries = {d["path"]: d for d in index_folder("docs")}
                setup = entries["guides/setup.md"]
                assert setup == {"path": "guides/setup.md", "type": "md", "words": 6,
                                 "title": "Setup guide"}, f"got {setup!r}"
                intro = entries["intro.txt"]
                assert intro["title"] == "Welcome to the handbook", f"got {intro!r}"
                assert intro["words"] == 8, f"got {intro!r}"

            def test_uppercase_extension_matches_and_type_is_lowercase():
                entries = {d["path"]: d for d in index_folder("docs")}
                notes = entries.get("guides/NOTES.MD")
                assert notes is not None, "uppercase extensions should match"
                assert notes["type"] == "md" and notes["title"] == "Notes", f"got {notes!r}"

            def test_empty_file_title_is_file_stem():
                entries = {d["path"]: d for d in index_folder("docs")}
                empty = entries["guides/empty.txt"]
                assert empty["title"] == "empty" and empty["words"] == 0, f"got {empty!r}"

            def test_missing_root_raises_file_not_found():
                try:
                    index_folder("no_such_dir")
                except FileNotFoundError:
                    return
                assert False, "expected FileNotFoundError for a missing folder"
        ''',
        "solution": r'''
            from pathlib import Path

            EXTENSIONS = {".txt", ".md"}


            def _title(text, fallback):
                for line in text.splitlines():
                    if line.strip():
                        return line.strip().lstrip("# ").strip()
                return fallback


            def index_folder(root):
                root = Path(root)
                if not root.is_dir():
                    raise FileNotFoundError(root)
                relative = []
                for path in root.rglob("*"):
                    if path.is_file() and path.suffix.lower() in EXTENSIONS:
                        relative.append(path.relative_to(root).as_posix())
                entries = []
                for rel in sorted(relative):
                    path = root / rel
                    text = path.read_text(encoding="utf-8")
                    entries.append({
                        "path": rel,
                        "type": path.suffix.lower().lstrip("."),
                        "words": len(text.split()),
                        "title": _title(text, path.stem),
                    })
                return entries
        ''',
    },
    {
        "id": "files-6",
        "hints": [
            "Validate the source folder before creating an output file.",
            "Collect the per-file rows and totals in filename order, distinguishing nonblank lines from all lines.",
            "Read the eligible direct children, calculate their counts, write the exact header, rows, and final total with newlines, then return the matching summary text.",
        ],
        "title": "Corpus report",
        "difficulty": 3,
        "prompt": r'''
            Summarise a folder of text documents into a small CSV report (CSV means
            comma-separated values: a text file where each line is one table row).

            **Your job:** write `write_report(folder, report_path)`

            **What goes in**
            - `folder`: a folder name, a string like `"corpus"`
            - `report_path`: the report file to write, a string like `"report.csv"`

            **What comes out**
            - a summary string `"<n> files, <words> words -> <report_path>"`,
              e.g. `"2 files, 10 words -> report.csv"`

            **Rules**
            - Read every `*.txt` file directly inside `folder`. Ignore subfolders and other extensions.
            - Write the report to `report_path` (replace it if it exists). Every line ends with `"\n"`:
              - first the header, exactly `file,lines,words`
              - then one row `<file name>,<lines>,<words>` per file, sorted by file name
              - then a final row `TOTAL,<sum of lines>,<sum of words>`
            - `lines` counts **non-blank** lines only. `words` counts whitespace-separated words.
            - An empty folder gives just the header and `TOTAL,0,0`.
            - If `folder` does not exist, raise `FileNotFoundError` with a message that contains the
              folder name, and do **not** create the report file.

            **Examples**
            ```text
            corpus/
              a.txt      "alpha beta\n\none two three four five\n"
              b.txt      "gamma delta epsilon\n"
              skip.md    (ignored)
              sub/c.txt  (ignored: in a subfolder)
            ```
            ```python
            write_report("corpus", "report.csv")   # returns "2 files, 10 words -> report.csv"
            # report.csv now contains:
            # file,lines,words
            # a.txt,2,7
            # b.txt,1,3
            # TOTAL,3,10

            write_report("emptydir", "e.csv")      # returns "0 files, 0 words -> e.csv"
            # e.csv contains "file,lines,words\nTOTAL,0,0\n"

            write_report("nowhere", "x.csv")       # raises FileNotFoundError, message mentions "nowhere"
            ```
        ''',
        "starter": r'''
            from pathlib import Path


            def write_report(folder, report_path):
                ...
        ''',
        "setup_files": {
            "corpus/b.txt": r'''
                gamma delta epsilon
            ''',
            "corpus/a.txt": r'''
                alpha beta

                one two three four five
            ''',
            "corpus/skip.md": r'''
                not counted at all
            ''',
            "corpus/sub/c.txt": r'''
                nested file is ignored
            ''',
        },
        "tests": r'''
            import os
            from solution import write_report

            def read(path):
                with open(path, encoding="utf-8") as fh:
                    return fh.read()

            def test_report_has_header_rows_and_total():
                write_report("corpus", "report.csv")
                got = read("report.csv").splitlines()
                expected = ["file,lines,words", "a.txt,2,7", "b.txt,1,3", "TOTAL,3,10"]
                assert got == expected, f"report.csv lines: {got!r}"

            def test_returns_summary_string():
                got = write_report("corpus", "out.csv")
                assert got == "2 files, 10 words -> out.csv", f"returned {got!r}"

            def test_empty_folder_gives_zero_totals():
                os.mkdir("emptydir")
                got = write_report("emptydir", "e.csv")
                assert got == "0 files, 0 words -> e.csv", f"returned {got!r}"
                lines = read("e.csv").splitlines()
                assert lines == ["file,lines,words", "TOTAL,0,0"], f"got {lines!r}"

            def test_missing_folder_raises_and_writes_nothing():
                try:
                    write_report("nowhere", "x.csv")
                except FileNotFoundError as exc:
                    assert "nowhere" in str(exc), f"message was {str(exc)!r}"
                else:
                    raise AssertionError("expected FileNotFoundError for a missing folder")
                assert not os.path.exists("x.csv"), "the report should not be created"
        ''',
        "solution": r'''
            from pathlib import Path


            def write_report(folder, report_path):
                folder_path = Path(folder)
                if not folder_path.is_dir():
                    raise FileNotFoundError(f"no such folder: {folder}")

                rows = []
                total_lines = 0
                total_words = 0
                for path in sorted(folder_path.glob("*.txt")):
                    text = path.read_text(encoding="utf-8")
                    lines = 0
                    for line in text.splitlines():
                        if line.strip():
                            lines += 1
                    words = len(text.split())
                    rows.append((path.name, lines, words))
                    total_lines += lines
                    total_words += words

                with open(report_path, "w", encoding="utf-8") as fh:
                    fh.write("file,lines,words\n")
                    for name, lines, words in rows:
                        fh.write(f"{name},{lines},{words}\n")
                    fh.write(f"TOTAL,{total_lines},{total_words}\n")

                return f"{len(rows)} files, {total_words} words -> {report_path}"
        ''',
    },
]
