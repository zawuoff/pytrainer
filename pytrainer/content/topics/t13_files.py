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

LESSON = r'''
## Chapter notes: Reading & Writing Files

Variables vanish when a program stops; files make data survive (prompts, documents for RAG,
chat logs, eval results).

**open + with**: `with open(path, mode, encoding="utf-8") as fh:` - the file is closed
automatically when the block ends, even after an error.

| mode | meaning | if the file exists | if it is missing |
| --- | --- | --- | --- |
| `"r"` (default) | read | read it | `FileNotFoundError` |
| `"w"` | write | **erased** first | created |
| `"a"` | append | new text goes at the end | created |

**Reading**
- `fh.read()` - the whole file as one string, newlines included
- `for line in fh:` - one line at a time; each line still ends with `"\n"`, so `.strip()` it
- `text.splitlines()` - list of lines without the newlines

**Writing**: `fh.write(text)` adds no newline - write `line + "\n"` yourself.

**Always pass `encoding="utf-8"`**: model output is full of accents and emoji, and the
default encoding differs between computers.

**Missing files**: catch `FileNotFoundError` when a missing file is normal (use a default).

**pathlib**

```python
from pathlib import Path

p = Path("docs") / "guide.md"
print(p.name, p.stem, p.suffix, p.parent)
Path("docs").mkdir(parents=True, exist_ok=True)
p.write_text("# Guide\n", encoding="utf-8")
print(p.read_text(encoding="utf-8").strip())
print(sorted(f.name for f in Path("docs").glob("*.md")))
```

- `/` joins path parts; `.name` "guide.md", `.stem` "guide", `.suffix` ".md"
- `mkdir(parents=True, exist_ok=True)` - create nested folders, no error if they exist
- `glob("*.md")` - matching files directly inside; `rglob("*")` - everything, recursively
- `is_file()`, `is_dir()`, `relative_to(root)`

**Gotchas**
- `open(path)` then `write` fails: that is read mode. Use `"w"` or `"a"`.
- `"w"` wipes the file; use `"a"` to add.
- Forgetting `"\n"` glues lines together; forgetting `.strip()` keeps them attached.
- `glob` results come in no guaranteed order - `sorted()` them.
'''

EXERCISES = [
    {
        "id": "files-s1",
        "lesson": r'''
            A file is like a **notebook on a shelf**. `open()` takes it off the shelf so you can read
            it, and when you are done it must go back (be *closed*). The `with` block does the
            putting-back for you, even if something goes wrong in the middle.

            ```python
            with open("todo.txt", "w", encoding="utf-8") as fh:
                fh.write("buy milk\ncall Ada\n")

            with open("todo.txt", encoding="utf-8") as fh:
                for line in fh:
                    print("item:", line.strip())
            ```

            Looping over an open file gives you **one line at a time**. Each line still ends with its
            newline character `"\n"`, so `strip()` it before printing or comparing.

            Vocabulary: `fh` is a **file object** (you will also see `f` or `file`); the `with ... as`
            statement is called a **context manager**. `encoding="utf-8"` tells Python how the letters
            are stored - always pass it, so accents and emoji work on every computer.
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
            Looping over an open file gives you one line at a time. `count` goes up by one
            for each line, `strip()` removes the trailing newline and `upper()` shouts it.
            After the loop, `count` is 2.
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
            Sometimes you do not want line by line - you want the **whole page at once**, like
            photocopying a document. The file object's `read()` method gives you everything as one
            string.

            ```python
            with open("poem.txt", "w", encoding="utf-8") as fh:
                fh.write("Roses are red\nViolets are blue\n")

            with open("poem.txt", encoding="utf-8") as fh:
                text = fh.read()
            print(repr(text))
            print(len(text), "characters")
            ```

            `repr()` shows the string with its hidden characters visible: the `\n` newlines are part of
            the text, including the one at the very end. `read()` changes nothing - you get exactly
            what is stored.

            This is how you load a prompt template or a document you want to feed to a model.
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
            The second argument of `open()` is the **mode**: which door you walk through.

            - `"r"` - **read** only. This is the default when you give no mode.
            - `"w"` - **write**: creates the file, or **wipes** it clean first if it exists.
            - `"a"` - **append**: adds to the end (next step).

            ```python
            with open("status.txt", "w", encoding="utf-8") as fh:
                fh.write("draft")
            with open("status.txt", "w", encoding="utf-8") as fh:
                fh.write("final")
            with open("status.txt", encoding="utf-8") as fh:
                print(fh.read())
            ```

            Only `final` is left: the second `"w"` wiped the first text. `write()` writes exactly what
            you give it - it does **not** add a newline.

            Watch out: if you forget the mode, you are in read mode, and calling `write()` fails with
            an error (and a missing file cannot even be opened).
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
            Mode `"w"` is a whiteboard you wipe before writing. Mode `"a"` (**append**) is a **diary**:
            every new entry goes at the end, and old pages are kept.

            ```python
            for event in ["started", "indexed 3 docs", "done"]:
                with open("run.log", "a", encoding="utf-8") as fh:
                    fh.write(event + "\n")

            with open("run.log", encoding="utf-8") as fh:
                print(fh.read())
            ```

            Each loop opens the file in append mode and adds one line. If the file does not exist yet,
            `"a"` creates it, just like `"w"`.

            Because `write()` adds nothing on its own, you add the `"\n"` yourself - otherwise all
            entries end up glued together on one line. Append mode is how logs of conversations,
            API calls and eval results are written.
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
            Asking for a file that is not there is like asking a librarian for a book the library does
            not own: you get a clear "no" - in Python, a `FileNotFoundError`.

            ```python
            for name in ["exists.txt", "missing.txt"]:
                if name == "exists.txt":
                    with open(name, "w", encoding="utf-8") as fh:
                        fh.write("hi")
                try:
                    with open(name, encoding="utf-8") as fh:
                        print(name, "->", fh.read())
                except FileNotFoundError:
                    print(name, "-> not found, using a default")
            ```

            Sometimes a missing file is a real error and the program should stop. Often it is normal:
            a first run with no cache, no saved history yet, no custom prompt. Then you catch
            `FileNotFoundError` with `try` / `except` and carry on with a **default** value.

            Catch this specific error - not every error - so that other problems still show up.
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
            A file path is like a **postal address**: `docs/guides/setup.md` means "in the `docs`
            folder, in `guides`, the file `setup.md`". The `pathlib` module turns that text into a
            `Path` object that knows its own parts.

            ```python
            from pathlib import Path

            p = Path("reports") / "2024" / "summary.md"
            print(p)
            print(p.name)
            print(p.stem, "+", p.suffix)
            print(p.parent)
            ```

            - `/` between paths **joins** them (no need to glue strings with `"/"`)
            - `.name` - the last part, the file name: `summary.md`
            - `.stem` - the name without its extension: `summary`
            - `.suffix` - the extension, with its dot: `.md`
            - `.parent` - the folder it lives in

            If a name has several dots (`data.tar.gz`), the suffix is only the last part (`.gz`) and
            the stem is everything before it (`data.tar`).
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
            Now combine three things you know into a small, real helper:

            1. read a whole file (`read()`),
            2. clean it with `strip()` (removes spaces, tabs and newlines at **both ends**),
            3. fall back to a **default** when the file is missing.

            ```python
            with open("sys.txt", "w", encoding="utf-8") as fh:
                fh.write("\n\n   Be concise.  \t\n")

            with open("sys.txt", encoding="utf-8") as fh:
                raw = fh.read()
            print(repr(raw))
            print(repr(raw.strip()))
            ```

            For the missing-file part, reuse the `try` / `except FileNotFoundError` pattern from the
            earlier step. A `return` *inside* a `with` block is fine: the file still gets closed.

            Why strip? Text editors add a final newline and people leave blank lines at the top. A
            system prompt with stray whitespace still works, but it wastes tokens and makes logs
            messy. Think of it as trimming the margins before you send a letter.
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
            A log file is a **diary with one entry per line**. Writing means appending one formatted
            line; reading means turning the lines back into a clean list.

            ```python
            with open("events.log", "a", encoding="utf-8") as fh:
                for level, text in [("info", "started"), ("", ""), ("warn", "slow")]:
                    if level:
                        fh.write(f"{level}: {text}\n")
                    else:
                        fh.write("\n")

            with open("events.log", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        print(repr(line.rstrip("\n")))
            ```

            - `line.strip()` is an empty string for a blank line, and an empty string counts as
              `False` in an `if` - that is how blank lines are skipped.
            - `rstrip("\n")` removes only the newline at the end, keeping the rest of the line.

            Keeping a format strict (`role: content`) is what lets you read the file back reliably.
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
            `pathlib` also has **shortcuts** for the whole open-write-close dance:

            - `path.write_text(text, encoding="utf-8")` - create/replace the file with `text`
            - `path.read_text(encoding="utf-8")` - the whole file as a string
            - `path.mkdir()` - create a folder

            ```python
            from pathlib import Path

            box = Path("outbox")
            box.mkdir(exist_ok=True)
            note = box / "hello.txt"
            note.write_text("Bonjour !", encoding="utf-8")
            print(note.read_text(encoding="utf-8"))
            print(str(note), note.is_file())
            ```

            Think of `mkdir` as putting up a new shelf before storing a box on it: writing a file into
            a folder that does not exist fails. `exist_ok=True` means "if the shelf is already there,
            that is fine" (without it, a second run crashes with `FileExistsError`).

            `mkdir` creates **one** folder level. Creating `a/b/c` when `a` does not exist needs one
            more argument - look it up in the docs for this step. `str(path)` turns a `Path` back into
            a plain string.
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
            A RAG app starts by finding its documents. `Path.glob(pattern)` is a **search on a folder**:
            it gives you every path whose name matches a pattern, where `*` means "any characters".

            ```python
            from pathlib import Path

            folder = Path("inbox")
            folder.mkdir(exist_ok=True)
            for name in ["b.txt", "a.txt", "c.csv"]:
                (folder / name).write_text("x", encoding="utf-8")
            for path in folder.glob("*.txt"):
                print("found", path.name)
            print(sorted(p.name for p in folder.glob("*.txt")))
            ```

            - `*.txt` matches every name ending in `.txt`, directly inside the folder (not in
              subfolders).
            - It gives you `Path` objects: use `.name` to get just the file name.
            - The order is **not guaranteed** (it depends on the disk), so wrap results in `sorted()`
              when order matters.

            The pattern language is the same one your terminal uses (`ls *.txt`), called **glob
            patterns**.
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
            Summarise a folder of text documents into a small CSV report.

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
