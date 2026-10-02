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
            ## Opening and reading a file

            A **file** is a named sequence of characters stored on disk. `open()` returns a
            **file object**: a value with methods that read from or write to that file.

            A `with` statement assigns the file object to the name after `as` and runs the
            indented block. When the block ends, Python **closes** the file, which tells the
            operating system that you are done with it. The file is closed even when the block
            raises an exception.

            ```python
            with open("todo.txt", "w", encoding="utf-8") as fh:
                fh.write("buy milk\ncall Ada\n")

            with open("todo.txt", encoding="utf-8") as fh:
                for line in fh:
                    print("item:", line.strip())
            # item: buy milk
            # item: call Ada
            ```

            The first block creates `todo.txt` with two lines. The second block opens it for
            reading. A `for` loop over a file object runs once per line of the file.

            Each line still ends with its newline character `"\n"`. Call `strip()` to remove it
            before you print or compare the line.

            Step through the loop. The list `lines` holds the same two strings that the loop
            over `todo.txt` produces.

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

            `fh` is a common name for a file object. You will also see `f` or `file`. An object
            that works in a `with` statement is called a **context manager**. A file object is one.

            `encoding="utf-8"` tells Python how the characters are stored as bytes on disk.
            Always pass it, so that accented letters and emoji are read the same way on every
            computer.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            A file `notes.txt` contains two lines: `hello` and `world`.
            Read the code and type exactly what it prints.
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
            The `for` loop over the open file runs once per line, so it runs twice. Each pass
            adds 1 to `count`. `strip()` removes the trailing newline and `upper()` returns the
            line in uppercase letters. After the loop, `count` is 2.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "A `for` loop over an open file runs once per line in the file.",
            "Each pass adds 1 to `count` and prints the count next to the uppercased line.",
            "Two lines means two passes: `1 HELLO`, then `2 WORLD`, then the final print after the loop shows the total.",
        ],
    },
    {
        "id": "files-s2",
        "lesson": r'''
            ## Reading the whole file

            A loop gives you one line per pass. When you want all of the text in one value, call
            the file object's `read()` method. It returns the entire content of the file as one
            string.

            ```python
            with open("poem.txt", "w", encoding="utf-8") as fh:
                fh.write("Roses are red\nViolets are blue\n")

            with open("poem.txt", encoding="utf-8") as fh:
                text = fh.read()
            print(repr(text))
            # 'Roses are red\nViolets are blue\n'
            print(len(text), "characters")
            # 31 characters
            ```

            `repr()` returns the string the way you would type it in code, so each newline
            character shows up as `\n`. The newlines are part of the text, including the one at
            the very end. `len(text)` counts them too.

            `read()` changes nothing. You get exactly the characters that are stored in the file.

            Use `read()` to load a prompt template, or a document that you send to a model.
        ''',
        "title": "Read the whole file",
        "difficulty": 0,
        "prompt": r'''
            Load a whole text file (for example a prompt template) into one string.

            **Write:** `read_file(path)` by filling in the blank (`___`) in the starter.

            - `path`: the file name, a string like `"prompt.txt"`
            - **Returns:** the **entire** contents of the file as one string, exactly as stored

            **Rules**
            - Return everything, newlines included. Do not strip anything (the final `\n` stays).
            - It must work for files with several lines.

            **Examples**
            ```python
            # prompt.txt contains one line: You are helpful.
            read_file("prompt.txt")   # returns "You are helpful.\n"

            # two.txt contains the lines a and b
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
            "An open file object has a method that gives you everything in it at once.",
            "You want one string with all the text, newlines included - no looping needed.",
            "Replace `___` with `read` so the line becomes `return fh.read()`.",
        ],
    },
    {
        "id": "files-s3",
        "lesson": r'''
            ## File modes

            The second argument of `open()` is the **mode**: a string that says what you will do
            with the file.

            - `"r"` is **read** mode. You can only read. It is the default when you pass no mode.
            - `"w"` is **write** mode. Python creates the file if it is missing. If the file
              exists, Python **erases** its content first.
            - `"a"` is **append** mode. It adds to the end of the file. The next step covers it.

            ```python
            with open("status.txt", "w", encoding="utf-8") as fh:
                fh.write("draft")
            with open("status.txt", "w", encoding="utf-8") as fh:
                fh.write("final")
            with open("status.txt", encoding="utf-8") as fh:
                print(fh.read())
            # final
            ```

            The second `open()` in `"w"` mode erased `draft`. `write()` writes exactly the
            characters you pass. It does **not** add a newline.

            ### Writing in read mode

            If you leave out the mode, the file is open in read mode. Calling `write()` on it
            raises an error. This example raises on purpose:

            ```python
            with open("status.txt", "w", encoding="utf-8") as fh:
                fh.write("draft")

            with open("status.txt", encoding="utf-8") as fh:
                print(fh.mode)   # `fh.mode` is the mode string the file was opened with
                # r
                fh.write("final")
            # io.UnsupportedOperation: not writable
            ```

            Read mode also cannot open a file that does not exist. That raises
            `FileNotFoundError`.
        ''',
        "title": "Fix the save",
        "difficulty": 0,
        "prompt": r'''
            Save a note to a file, replacing whatever was there before. The starter crashes: find
            the bug and fix it.

            **Write:** `save_note(path, text)` (fix the starter)

            - `path`: the file name, a string like `"note.txt"`
            - `text`: the string to save, e.g. `"remember the RAG demo"`
            - **Returns:** nothing (`None`). The result is the file on disk.

            **Rules**
            - If the file does not exist yet, create it.
            - If it already exists, its old content is **replaced** (not added to).
            - Write `text` exactly as given. Do not add a newline.

            **Examples**
            ```python
            save_note("note.txt", "remember the RAG demo")
            # note.txt now contains exactly: "remember the RAG demo"

            save_note("n.txt", "old text")
            save_note("n.txt", "new")
            # n.txt now contains exactly: "new"
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
            "Look at how the file is opened. What mode does `open()` use when you give it none?",
            "With no mode, the file is opened for reading only, so writing fails (and a missing file cannot even be opened).",
            "Add the write mode `\"w\"` as the second argument to `open()`, before `encoding`.",
        ],
    },
    {
        "id": "files-s4",
        "lesson": r'''
            ## Append mode

            Mode `"w"` erases the file before it writes. Mode `"a"` (**append**) keeps the
            existing content and puts every write at the end of the file.

            ```python
            with open("run.log", "w", encoding="utf-8") as fh:
                fh.write("started\n")

            for event in ["indexed 3 docs", "done"]:
                with open("run.log", "a", encoding="utf-8") as fh:
                    fh.write(event + "\n")

            with open("run.log", encoding="utf-8") as fh:
                print(repr(fh.read()))
            # 'started\nindexed 3 docs\ndone\n'
            ```

            The first block uses `"w"`, so `run.log` starts with one line. Each pass of the loop
            opens the file in append mode and adds one line after the existing ones.

            Click each stage to see the content of `run.log` after it.

            ```diagram
            {"type":"flow","title":"The content of run.log after each step","steps":[{"label":"open \"w\"","detail":"Write mode creates run.log if it is missing. If the file exists, its content is erased.","code":"run.log: ''"},{"label":"write","detail":"write() stores the 8 characters of the string, including the newline at the end.","code":"fh.write(\"started\\n\")\nrun.log: 'started\\n'"},{"label":"open \"a\"","detail":"Append mode keeps the existing content. Every write goes at the end of the file.","code":"run.log: 'started\\n'"},{"label":"write","detail":"The new line is added after the existing line.","code":"fh.write(\"indexed 3 docs\\n\")\nrun.log: 'started\\nindexed 3 docs\\n'"},{"label":"open \"a\", write","detail":"The second pass of the loop opens the file in append mode again and adds one more line.","code":"fh.write(\"done\\n\")\nrun.log: 'started\\nindexed 3 docs\\ndone\\n'"},{"label":"open \"r\", read","detail":"Read mode changes nothing. read() returns all three lines as one string.","code":"'started\\nindexed 3 docs\\ndone\\n'"}]}
            ```

            If the file does not exist yet, `"a"` creates it, the same as `"w"` does.

            `write()` adds no newline, so you add the `"\n"` yourself. Without it, all entries
            end up on one line. A **log** is a file that records what happened, one line per event. Programs use
            append mode to write logs of conversations, API calls and results.
        ''',
        "title": "Add a line",
        "difficulty": 0,
        "prompt": r'''
            Add one line to the end of a to-do or log file.

            **Write:** `add_line(path, text)`

            - `path`: the file name, a string like `"todo.txt"`
            - `text`: the line to add, without a newline, e.g. `"ship it"`
            - **Returns:** nothing (`None`). The result is the file on disk.

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
            "There is a file mode that adds to the end instead of erasing.",
            "Open the file in append mode inside a `with` block and write the text followed by a newline.",
            "Use `open(path, \"a\", encoding=\"utf-8\")` in a `with` block, then call `fh.write()` with `text + \"\\n\"`.",
        ],
    },
    {
        "id": "files-s5",
        "lesson": r'''
            ## Missing files

            Opening a file in read mode raises `FileNotFoundError` when the file does not exist.
            This example raises on purpose:

            ```python
            print("opening")
            # opening
            with open("no_such_file.txt", encoding="utf-8") as fh:
                print(fh.read())
            # FileNotFoundError: [Errno 2] No such file or directory: 'no_such_file.txt'
            ```

            Sometimes a missing file is a real error and the program should stop. Often it is
            normal: a first run with no cache, no saved history yet, no custom prompt. In that
            case, catch `FileNotFoundError` with `try` / `except` and continue with a
            **default**: a value you use when the real one is not available.

            ```python
            with open("exists.txt", "w", encoding="utf-8") as fh:
                fh.write("hi")

            for name in ["exists.txt", "no_such_file.txt"]:
                try:
                    with open(name, encoding="utf-8") as fh:
                        text = fh.read()
                except FileNotFoundError:
                    text = "(default)"
                print(name, "->", text)
            # exists.txt -> hi
            # no_such_file.txt -> (default)
            ```

            Name `FileNotFoundError` in the `except` line. Do not catch every exception. Other
            problems, such as a misspelled variable name, then still stop the program with their
            own error message.
        ''',
        "title": "Missing file? No problem",
        "difficulty": 0,
        "prompt": r'''
            Read a file that may or may not exist, without crashing.

            **Write:** `read_or_empty(path)`

            - `path`: the file name, a string like `"notes.txt"`
            - **Returns:** a string: the file's full contents, or `""` (an empty string)

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
            "Opening a file that does not exist raises an error. Which one? Catch it.",
            "Try to open and read the file. If that raises `FileNotFoundError`, return an empty string instead.",
            "Put the `with open(...)` block and `return fh.read()` inside `try:`, then add `except FileNotFoundError:` that returns `\"\"`.",
        ],
    },
    {
        "id": "files-s6",
        "lesson": r'''
            ## Paths with pathlib

            A **path** is the text that names where a file is stored. `docs/guides/setup.md`
            names the file `setup.md` inside the folder `guides`, which is inside the folder `docs`.

            The `pathlib` module provides `Path`: an object that holds a path and gives you its
            parts as attributes. `from pathlib import Path` loads only `Path` from the module, so you
write `Path(...)` and not `pathlib.Path(...)`. The `/` operator **joins** a `Path` with the next part, so you
            do not build the string with `"/"` yourself.

            ```python
            from pathlib import Path

            p = Path("reports") / "2024" / "summary.md"
            print(p)
            # reports/2024/summary.md
            print(p.name)
            # summary.md
            print(p.stem, "+", p.suffix)
            # summary + .md
            print(p.parent)
            # reports/2024
            ```

            - `.name` is the last part of the path, the file name.
            - `.stem` is the file name without its extension.
            - `.suffix` is the extension, including its dot.
            - `.parent` is the path of the folder that contains the file.

            `.name`, `.stem` and `.suffix` are strings. `.parent` is another `Path`.

            ### Names with several dots

            When a name has several dots, the suffix is only the last part. The stem is
            everything before it.

            ```python
            from pathlib import Path

            archive = Path("backups/data.tar.gz")
            print(archive.suffix)
            # .gz
            print(archive.stem)
            # data.tar
            ```
        ''',
        "title": "Name the output file",
        "difficulty": 0,
        "prompt": r'''
            A pipeline reads `docs/guide.md` and saves its results as `guide.json`. Build that
            output file name.

            **Write:** `output_name(src)` using `pathlib.Path`

            - `src`: a file path as a string, e.g. `"docs/guide.md"`
            - **Returns:** a string: the source file name **without its folders and extension**,
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
            "Turn the string into a `Path`; it knows the parts of its own name.",
            "You need the file name without folders and without the extension - one attribute gives exactly that. Then add the new extension.",
            "Return `Path(src)` followed by `.stem`, plus the string `\".json\"`.",
        ],
    },
    {
        "id": "files-1",
        "lesson": r'''
            ## Read, strip, default

            This exercise combines three things you already know:

            1. Read a whole file with `read()`.
            2. Remove the whitespace at **both ends** with `strip()`. **Whitespace** means
               spaces, tabs and newlines.
            3. Return a **default** value when the file is missing.

            ```python
            with open("sys.txt", "w", encoding="utf-8") as fh:
                fh.write("\n\n   Be concise.  \t\n")

            with open("sys.txt", encoding="utf-8") as fh:
                raw = fh.read()
            print(repr(raw))
            # '\n\n   Be concise.  \t\n'
            print(repr(raw.strip()))
            # 'Be concise.'
            ```

            `strip()` removes whitespace only at the start and the end. The space between `Be`
            and `concise.` stays.

            For the missing file, use `try` / `except FileNotFoundError` from the earlier step.
            A `return` inside a `with` block is fine. Python still closes the file before the
            function returns.

            Strip the text because a file often ends with a newline and people leave blank lines
            at the top of a file. A system prompt with extra whitespace still works, but the
            extra characters are sent to the model with every request, and they make printed
            output harder to read.
        ''',
        "hints": [
            "Combine a `with open(...)` block for reading with a `try` / `except` for the missing-file case.",
            "Read the whole file, strip the whitespace around it and return it. If opening fails because the file is not there, return the default text instead.",
            "In a `try`, open with `encoding=\"utf-8\"` in a `with` block and return `fh.read().strip()`. Add `except FileNotFoundError:` that returns `\"You are a helpful assistant.\"`.",
        ],
        "title": "Load a system prompt",
        "difficulty": 1,
        "prompt": r'''
            Chat apps often keep the system prompt in a text file. Load it, with a safe default.

            **Write:** `load_prompt(path)`

            - `path`: the file name, a string like `"system.txt"`
            - **Returns:** a string: the file's text with surrounding whitespace stripped

            **Rules**
            - Remove whitespace (spaces, tabs, blank lines, newlines) from the **start and end**
              of the text. Whitespace inside the text stays.
            - If the file does not exist, return `"You are a helpful assistant."` instead of crashing.
            - Open the file with a `with` statement and pass `encoding="utf-8"` (a check looks for
              both), so text like `"Réponds en français."` is read correctly.

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
            ## One entry per line

            A **log file** stores one entry per line. To add an entry, you append one formatted
            line. To read the log, you loop over the lines and clean each one.

            ```python
            level, text = "warn", "slow"

            with open("events.log", "w", encoding="utf-8") as fh:
                fh.write("info: started\n\n")
            with open("events.log", "a", encoding="utf-8") as fh:
                fh.write(f"{level}: {text}\n")

            with open("events.log", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        print(repr(line.rstrip("\n")))
            # 'info: started'
            # 'warn: slow'
            ```

            The file holds three lines: `"info: started\n"`, the blank line `"\n"` and
            `"warn: slow\n"`. The loop prints two of them.

            - `line.strip()` returns an empty string for a blank line. An empty string counts as
              `False` in an `if`, so the blank line is skipped.
            - `rstrip("\n")` removes only the newline at the end. The rest of the line stays.

            Step through the loop and watch the second pass skip the `print`. The list `lines`
            holds the same three strings that the loop over `events.log` produces.

            ```diagram
            {"type": "trace", "title": "Skipping the blank line in events.log", "code": ["lines = [\"info: started\\n\", \"\\n\", \"warn: slow\\n\"]", "for line in lines:", "    if line.strip():", "        print(repr(line.rstrip(\"\\n\")))", "print(\"done\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']"}, "out": ""},
              {"line": 3, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'info: started\\n'"}, "out": ""},
              {"line": 4, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'info: started\\n'"}, "out": ""},
              {"line": 2, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'info: started\\n'"}, "out": "'info: started'\n"},
              {"line": 3, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'\\n'"}, "out": "'info: started'\n"},
              {"line": 2, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'\\n'"}, "out": "'info: started'\n"},
              {"line": 3, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'warn: slow\\n'"}, "out": "'info: started'\n"},
              {"line": 4, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'warn: slow\\n'"}, "out": "'info: started'\n"},
              {"line": 2, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'warn: slow\\n'"}, "out": "'info: started'\n'warn: slow'\n"},
              {"line": 5, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'warn: slow\\n'"}, "out": "'info: started'\n'warn: slow'\n"},
              {"line": null, "vars": {"lines": "['info: started\\n', '\\n', 'warn: slow\\n']", "line": "'warn: slow\\n'"}, "out": "'info: started'\n'warn: slow'\ndone\n"}
            ]}
            ```

            Write every entry in the same strict format, such as `level: text`. A fixed format is
            what makes it possible to read the file back reliably.
        ''',
        "hints": [
            "Writing needs append mode; reading means looping over the file's lines.",
            "`log_message` opens in `\"a\"` mode and writes one formatted line ending in a newline. `read_log` collects each line without its newline, skipping blank ones.",
            "Write: open the file in append mode with a UTF-8 encoding, and write an f-string of role, colon, space, content and a newline. Read: start an empty list, loop over the open file, skip lines where `.strip()` gives an empty string, otherwise append the line with its trailing newline removed (`.rstrip`); return the list.",
        ],
        "title": "Conversation log",
        "difficulty": 1,
        "prompt": r'''
            Keep a simple conversation log on disk: one line per message.

            **Write:** two functions.

            `log_message(path, role, content)`
            - `path`: the log file name, e.g. `"chat.log"`
            - `role`: a string like `"user"` or `"assistant"`
            - `content`: the message text, e.g. `"hi"`
            - **Returns:** nothing (`None`). It adds one line to the file.

            `read_log(path)`
            - `path`: the log file name
            - **Returns:** a list of strings, one per line of the file

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
            ## Path methods that read and write

            A `Path` has methods that open the file, read or write it, and close it in one call.

            - `path.write_text(text, encoding="utf-8")` creates the file, or replaces its
              content, with `text`.
            - `path.read_text(encoding="utf-8")` returns the whole file as one string.
            - `path.mkdir()` creates a folder.

            ```python
            from pathlib import Path

            box = Path("outbox")
            box.mkdir(exist_ok=True)
            note = box / "hello.txt"
            note.write_text("Bonjour !", encoding="utf-8")
            print(note.read_text(encoding="utf-8"))
            # Bonjour !
            print(str(note), note.is_file())
            # outbox/hello.txt True
            ```

            `str(path)` converts a `Path` to a plain string. `is_file()` returns `True` when the
            path names an existing file.

            ### mkdir

            Writing a file into a folder that does not exist raises `FileNotFoundError`. Create
            the folder with `mkdir` first.

            `mkdir()` raises `FileExistsError` when the folder already exists, so a second run
            of the program would stop there. Pass `exist_ok=True` and `mkdir` does nothing when
            the folder is already there.

            `mkdir` creates **one** folder level. Creating `a/b/c` when `a` does not exist needs
            one more argument. Find it in the docs linked for this step.
        ''',
        "research": {"note": "Read the documentation of `Path.mkdir` to find how to create missing parent folders too, then come back.",
         "links": [{"title": "pathlib Path.mkdir - Python docs", "url": "https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir"}]},
        "title": "Save a chunk into a folder",
        "difficulty": 1,
        "prompt": r'''
            A document splitter saves each chunk as its own file inside an output folder that
            may not exist yet.

            **Write:** `save_chunk(folder, name, text)` using `pathlib`

            - `folder`: the output folder, a string like `"out/chunks"` (may be several levels deep)
            - `name`: the file name, a string like `"c1.txt"`
            - `text`: the chunk text, e.g. `"RAG = retrieval + generation"`
            - **Returns:** a string: the path of the written file, `folder` and `name` joined with
              `/`, e.g. `"out/chunks/c1.txt"`

            **Rules**
            - Create `folder`, **including any missing parent folders**. If it already exists,
              that is fine (no error).
            - Write `text` exactly as given (no newline added), with UTF-8 encoding
              (`"café"` must work). An existing file with that name is replaced.
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
            "Three steps with `Path`: make the folder, write the file, return its path as a string.",
            "`mkdir` needs two keyword arguments here: one for missing parent folders, one for 'already exists is OK'. Join folder and name with `/`.",
            "`out = Path(folder)`; `out.mkdir(parents=True, exist_ok=True)`; `path = out / name`; `path.write_text(text, encoding=\"utf-8\")`; return `str(path)`.",
        ],
    },
    {
        "id": "files-8",
        "lesson": r'''
            ## Finding files with glob

            An app that answers questions from your own documents starts by finding those
            documents. `Path.glob(pattern)` gives you every path inside a folder whose name
            matches `pattern`. In a pattern, `*` matches any characters.

            ```python
            from pathlib import Path

            folder = Path("inbox")
            folder.mkdir(exist_ok=True)
            for name in ["b.txt", "a.txt", "c.csv"]:
                (folder / name).write_text("x", encoding="utf-8")

            names = []
            for path in folder.glob("*.txt"):
                names.append(path.name)
            print(sorted(names))
            # ['a.txt', 'b.txt']
            ```

            - `*.txt` matches every name that ends in `.txt`. `c.csv` does not match.
            - `glob("*.txt")` looks directly inside the folder. It does not look in subfolders.
            - Each result is a `Path` object. Use `.name` to get the file name as a string.
            - The order of the results is **not guaranteed**, because it depends on the disk.
              Wrap the results in `sorted()` when the order matters.

            A folder that does not exist gives no results and no error.

            ```python
            from pathlib import Path

            print(list(Path("no_such_folder").glob("*.txt")))
            # []
            ```

            These patterns are called **glob patterns**.
        ''',
        "title": "List the markdown docs",
        "difficulty": 1,
        "prompt": r'''
            Find the markdown documents your RAG app should index.

            **Write:** `list_docs(folder)` using `pathlib`

            - `folder`: a folder name, a string like `"kb"`
            - **Returns:** a list of file **names** (strings like `"faq.md"`, no folder part) of
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
            "`Path(folder).glob(pattern)` finds matching files directly inside a folder.",
            "Use a pattern that means 'anything ending in .md', keep only each match's file name, and sort the result.",
            "Loop over `Path(folder).glob(\"*.md\")`, append `path.name` to a list, and return `sorted(...)` of that list.",
        ],
    },
    {
        "id": "files-3",
        "hints": [
            "Read the whole file into one string first; every statistic can be computed from that string.",
            "Characters are the string's length, words come from splitting on whitespace, and lines from splitting into lines. For the longest line, track the best length and its 1-based number as you loop.",
            "`text = fh.read()`; `lines = text.splitlines()`; `words = len(text.split())`; `chars = len(text)`. Loop with `enumerate(lines, start=1)` and only update the best when a line is strictly longer (so the first wins ties). Start the best line number at 0 for an empty file.",
        ],
        "title": "Document stats",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Before chunking a document for an AI app, it helps to know its size.

            **Write:** `file_stats(path)`

            - `path`: the file name, a string like `"doc.txt"`
            - **Returns:** a dict with exactly these four keys (all ints):
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
            "Use `Path` for everything: `read_text`, `mkdir`, `stem`, the `/` operator and `write_text`.",
            "Get the words from the source, step through them `size` at a time, and write each group to a numbered file named after the source's stem. Collect the names as you go.",
            "Convert `src` and `out_dir` to `Path`. Call `out.mkdir(parents=True, exist_ok=True)`. Split the text into words. Loop over `range(0, len(words), size)` with a counter from 1; build the name with an f-string using `src.stem`, write `\" \".join(words[start:start + size])` to `out / name`, append the name.",
        ],
        "title": "Split into chunk files",
        "difficulty": 2,
        "prompt": r'''
            RAG pipelines split long documents into small chunks. Write each chunk to its own file.

            **Write:** `write_chunks(src, out_dir, size)` using `pathlib`

            - `src`: the source text file, a string like `"notes.md"` or a `Path`
            - `out_dir`: the output folder, a string like `"build/chunks"` or a `Path`
            - `size`: max words per chunk, an int like `2`
            - **Returns:** a list of the written file **names** (just names like `"notes_1.txt"`,
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
            "`Path.rglob(\"*\")` walks a folder recursively. Filter by `suffix`, lower-cased.",
            "For each matching file compute the four fields: relative path, extension without the dot, word count, and title from the first non-blank line. Sort the list by path at the end. Check that the root folder exists first.",
            "If `not root.is_dir()`, raise `FileNotFoundError`. Loop `root.rglob(\"*\")`, skip non-files and suffixes not in {`.txt`, `.md`} (after `.lower()`). Use `path.relative_to(root).as_posix()` for the path, `.lstrip(\"#\").strip()` on the first non-blank line for the title (fallback `path.stem`). To get the order right, first collect the relative path strings, `sorted()` that plain list, then build one dict per path in that order.",
        ],
        "title": "Index a document folder",
        "difficulty": 3,
        "prompt": r'''
            Before building a RAG index you need an inventory of the source documents.

            **Write:** `index_folder(root)`

            - `root`: a folder name, a string like `"docs"` (or a `Path`)
            - **Returns:** a list of dicts, one per document, like
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
            "Use `Path(folder).glob(\"*.txt\")` (not `rglob`) to get only the files directly inside the folder, and open the report in `\"w\"` mode.",
            "Check the folder exists first and raise `FileNotFoundError` if not. Then, for each file in sorted order, count its non-blank lines and its words, keep running totals, and write the header, one row per file and the TOTAL row. Finally build and return the summary string.",
            "1) `if not Path(folder).is_dir()`: raise `FileNotFoundError` with an f-string naming the folder. 2) Loop over `sorted(...glob(\"*.txt\"))`; for each, `read_text`, count lines where `.strip()` is not empty, and `len(text.split())` words; store `(path.name, lines, words)` and add to the totals. 3) Open the report with `\"w\"`, write the header, each row and the TOTAL row, each ending in `\\n`. 4) Return the f-string summary.",
        ],
        "title": "Corpus report",
        "difficulty": 3,
        "prompt": r'''
            Summarise a folder of text documents into a small CSV report (CSV means
            comma-separated values: a text file where each line is one table row).

            **Write:** `write_report(folder, report_path)`

            - `folder`: a folder name, a string like `"corpus"`
            - `report_path`: the report file to write, a string like `"report.csv"`
            - **Returns:** a summary string `"<n> files, <words> words -> <report_path>"`,
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
