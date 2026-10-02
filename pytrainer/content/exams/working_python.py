"""Module test: Everyday Python (strings -> sorting)."""

EXAM = {
    "module": "working-python",
    "title": "Everyday Python: module test",
    "intro": r'''
        This is a **test**, not a lesson. It checks the whole Everyday Python module:
        strings, comprehensions, JSON, files, environment variables, scripts and sorting -
        the daily plumbing of every AI app.

        **How it works**

        - There are **no hints and no tutor** while you take it. You get the prompt, the
          checks and your own knowledge.
        - Every rule the checks test is written in the prompt or shown in the examples.
          Read each prompt twice before you code.
        - Two exercises are *research* tasks: one links to the official docs to read first,
          the other asks you to find a standard-library tool on your own. Looking things up
          is part of the job, so it's part of the test.

        **Passing**

        Pass at least **70%** of the exercises and the module counts as done: you can skip
        its chapters and move on. If you don't pass, no problem - the chapters are there to
        close the gaps.
    ''',
    "pass_ratio": 0.7,
}

EXERCISES = [
    {
        "id": "exam-working-python-1",
        "title": "Normalise document tags",
        "difficulty": 2,
        "prompt": r'''
            Users tag documents in a knowledge base by typing comma-separated tags. Before
            indexing, the tags need cleaning.

            **Write:** `normalize_tags(raw)`

            - `raw`: a string of comma-separated tags, e.g. `"  RAG, llm,, Agents ,rag "`
            - **Returns:** a list of clean tags, e.g. `["rag", "llm", "agents"]`

            **Rules**
            - Split on commas. Strip spaces around each tag and make it lowercase.
            - Drop tags that are empty after stripping.
            - Keep only the first occurrence of each tag (compare after cleaning), in the
              order they first appear.
            - An empty or blank string returns `[]`.

            **Examples**
            ```python
            normalize_tags("  RAG, llm,, Agents ,rag ")   # returns ["rag", "llm", "agents"]
            normalize_tags("Vector DB, vector db")        # returns ["vector db"]
            normalize_tags("   ")                         # returns []
            ```
        ''',
        "starter": r'''
            def normalize_tags(raw):
                ...
        ''',
        "tests": r'''
            from solution import normalize_tags

            def test_example_tags():
                got = normalize_tags("  RAG, llm,, Agents ,rag ")
                assert got == ["rag", "llm", "agents"], f"got {got!r}"

            def test_inner_spaces_are_kept():
                got = normalize_tags("Vector DB, vector db")
                assert got == ["vector db"], f"got {got!r}"

            def test_first_occurrence_order_is_kept():
                got = normalize_tags("b, A, a, c, B")
                assert got == ["b", "a", "c"], f"got {got!r}"

            def test_blank_string_returns_empty_list():
                assert normalize_tags("   ") == []
                assert normalize_tags("") == []

            def test_only_commas_returns_empty_list():
                assert normalize_tags(" , ,, ") == []
        ''',
        "solution": r'''
            def normalize_tags(raw):
                cleaned = [tag.strip().lower() for tag in raw.split(",")]
                result = []
                for tag in cleaned:
                    if tag and tag not in result:
                        result.append(tag)
                return result
        ''',
        "hints": [
            "String methods (split, strip, lower) plus a way to skip empties and duplicates.",
            "First clean every piece (a list comprehension works well). Then walk through the cleaned tags and keep a tag only if it's not empty and not already kept.",
            "1) pieces = [t.strip().lower() for t in raw.split(',')]. 2) result = []. 3) For each piece: if it is non-empty and not in result, append it. 4) Return result.",
        ],
    },
    {
        "id": "exam-working-python-2",
        "title": "Load a JSONL dataset",
        "difficulty": 3,
        "research": {
            "note": "Eval sets and fine-tuning data are usually stored as JSON Lines: one JSON "
                    "object per line. Read how `json.loads` parses a single string and what "
                    "exception it raises on invalid input, then how to read a text file line by line.",
            "links": [
                {"title": "json.loads - Python docs",
                 "url": "https://docs.python.org/3/library/json.html#json.loads"},
                {"title": "json.JSONDecodeError - Python docs",
                 "url": "https://docs.python.org/3/library/json.html#json.JSONDecodeError"},
                {"title": "Reading and writing files - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files"},
                {"title": "JSON Lines format", "url": "https://jsonlines.org/"},
            ],
        },
        "prompt": r'''
            An eval dataset is stored as a `.jsonl` file: each non-blank line is one JSON object.

            **Write:** `load_jsonl(path)`

            - `path`: the file path, a string like `"cases.jsonl"`
            - **Returns:** a list of dicts, one per JSON line, in file order

            **Rules**
            - Blank lines (empty or only whitespace) are skipped.
            - If a line isn't valid JSON, raise `ValueError` with the message
              `"line <n>: invalid JSON"`, where `<n>` is the line number in the file,
              counting from 1 and counting blank lines too.
            - If a line is valid JSON but not an object (e.g. a list or a number), raise
              `ValueError` with the message `"line <n>: expected an object"`.
            - If the file doesn't exist, let the normal `FileNotFoundError` happen.

            **Examples**

            With `cases.jsonl` containing:
            ```text
            {"input": "2+2", "expected": "4"}

            {"input": "capital of France", "expected": "Paris"}
            ```
            ```python
            load_jsonl("cases.jsonl")
            # returns [{"input": "2+2", "expected": "4"},
            #          {"input": "capital of France", "expected": "Paris"}]
            ```
            A file whose 3rd line is `{"input": oops}` raises `ValueError("line 3: invalid JSON")`.
        ''',
        "starter": r'''
            def load_jsonl(path):
                ...
        ''',
        "tests": r'''
            from pathlib import Path
            from solution import load_jsonl

            def write(name, text):
                Path(name).write_text(text, encoding="utf-8")
                return name

            def expect_error(name, message):
                try:
                    load_jsonl(name)
                except ValueError as e:
                    assert str(e) == message, f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError raised")

            def test_reads_objects_and_skips_blank_lines():
                write("cases.jsonl", '{"input": "2+2", "expected": "4"}\n\n'
                                     '{"input": "capital of France", "expected": "Paris"}\n')
                got = load_jsonl("cases.jsonl")
                assert got == [{"input": "2+2", "expected": "4"},
                               {"input": "capital of France", "expected": "Paris"}], f"got {got!r}"

            def test_whitespace_only_lines_are_skipped():
                write("ws.jsonl", '   \n{"a": 1}\n\t\n')
                got = load_jsonl("ws.jsonl")
                assert got == [{"a": 1}], f"got {got!r}"

            def test_invalid_json_reports_line_number_counting_blank_lines():
                write("bad.jsonl", '{"a": 1}\n\n{"input": oops}\n')
                expect_error("bad.jsonl", "line 3: invalid JSON")

            def test_non_object_line_is_rejected():
                write("list.jsonl", '{"a": 1}\n[1, 2]\n')
                expect_error("list.jsonl", "line 2: expected an object")

            def test_empty_file_returns_empty_list():
                write("empty.jsonl", "")
                assert load_jsonl("empty.jsonl") == []

            def test_missing_file_raises_file_not_found():
                try:
                    load_jsonl("nope.jsonl")
                except FileNotFoundError:
                    pass
                else:
                    raise AssertionError("expected FileNotFoundError")
        ''',
        "solution": r'''
            import json


            def load_jsonl(path):
                rows = []
                with open(path, encoding="utf-8") as f:
                    for number, line in enumerate(f, start=1):
                        if not line.strip():
                            continue
                        try:
                            row = json.loads(line)
                        except json.JSONDecodeError:
                            raise ValueError(f"line {number}: invalid JSON")
                        if not isinstance(row, dict):
                            raise ValueError(f"line {number}: expected an object")
                        rows.append(row)
                return rows
        ''',
        "hints": [
            "Open the file, loop over its lines with a line counter, and parse each non-blank line with json.loads.",
            "Keep the line number as you go (enumerate starting at 1). Skip blank lines, but they still count. Catch the JSON error and re-raise as ValueError with the number; check the parsed value is a dict.",
            "1) with open(path, encoding='utf-8') as f. 2) for n, line in enumerate(f, start=1). 3) if not line.strip(): continue. 4) try json.loads(line) except json.JSONDecodeError: raise ValueError(f'line {n}: invalid JSON'). 5) If not isinstance(row, dict), raise the 'expected an object' error. 6) Append and return the list.",
        ],
    },
    {
        "id": "exam-working-python-3",
        "title": "Settings from the environment",
        "difficulty": 2,
        "prompt": r'''
            An LLM app reads its configuration from environment variables so secrets never
            live in the code.

            **Write:** `load_settings()`

            - Takes no arguments; reads `os.environ`.
            - **Returns:** a dict `{"api_key": str, "model": str, "max_tokens": int, "debug": bool}`

            **Rules**
            - `APP_API_KEY` is required. If it's missing or an empty string, raise
              `RuntimeError` with the message `"APP_API_KEY is not set"`.
            - `APP_MODEL` defaults to `"gpt-4o-mini"`.
            - `APP_MAX_TOKENS` defaults to `512`. If set, it must be a whole number (surrounding
              spaces are fine); otherwise raise `ValueError` with the message
              `"APP_MAX_TOKENS must be an integer"`.
            - `APP_DEBUG` is `True` when its value is `"1"`, `"true"` or `"yes"` in any
              upper/lower case, with surrounding spaces ignored. Anything else, or unset, is `False`.
            - Read the environment each time the function is called (not once at import).

            **Examples**
            ```python
            # with APP_API_KEY="sk-test" and nothing else set
            load_settings()
            # returns {"api_key": "sk-test", "model": "gpt-4o-mini", "max_tokens": 512, "debug": False}

            # with APP_API_KEY="k", APP_MODEL="claude-x", APP_MAX_TOKENS=" 1024 ", APP_DEBUG="TRUE"
            load_settings()
            # returns {"api_key": "k", "model": "claude-x", "max_tokens": 1024, "debug": True}

            # with APP_MAX_TOKENS="lots" -> raises ValueError("APP_MAX_TOKENS must be an integer")
            ```
        ''',
        "starter": r'''
            import os


            def load_settings():
                ...
        ''',
        "tests": r'''
            import os
            from solution import load_settings

            KEYS = ["APP_API_KEY", "APP_MODEL", "APP_MAX_TOKENS", "APP_DEBUG"]

            def call_with(env):
                saved = {k: os.environ.get(k) for k in KEYS}
                try:
                    for k in KEYS:
                        os.environ.pop(k, None)
                    os.environ.update(env)
                    return load_settings()
                finally:
                    for k, v in saved.items():
                        if v is None:
                            os.environ.pop(k, None)
                        else:
                            os.environ[k] = v

            def test_defaults_when_only_key_is_set():
                got = call_with({"APP_API_KEY": "sk-test"})
                assert got == {"api_key": "sk-test", "model": "gpt-4o-mini",
                               "max_tokens": 512, "debug": False}, f"got {got!r}"

            def test_all_values_read_and_converted():
                got = call_with({"APP_API_KEY": "k", "APP_MODEL": "claude-x",
                                 "APP_MAX_TOKENS": " 1024 ", "APP_DEBUG": "TRUE"})
                assert got == {"api_key": "k", "model": "claude-x",
                               "max_tokens": 1024, "debug": True}, f"got {got!r}"

            def test_debug_accepts_yes_and_1_and_rejects_others():
                assert call_with({"APP_API_KEY": "k", "APP_DEBUG": " yes "})["debug"] is True
                assert call_with({"APP_API_KEY": "k", "APP_DEBUG": "1"})["debug"] is True
                assert call_with({"APP_API_KEY": "k", "APP_DEBUG": "0"})["debug"] is False
                assert call_with({"APP_API_KEY": "k", "APP_DEBUG": "no"})["debug"] is False

            def test_missing_or_empty_key_raises_runtime_error():
                for env in ({}, {"APP_API_KEY": ""}):
                    try:
                        call_with(env)
                    except RuntimeError as e:
                        assert str(e) == "APP_API_KEY is not set", f"message was {str(e)!r}"
                    else:
                        raise AssertionError(f"no RuntimeError for {env!r}")

            def test_bad_max_tokens_raises_value_error():
                try:
                    call_with({"APP_API_KEY": "k", "APP_MAX_TOKENS": "lots"})
                except ValueError as e:
                    assert str(e) == "APP_MAX_TOKENS must be an integer", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for APP_MAX_TOKENS='lots'")
        ''',
        "solution": r'''
            import os


            def load_settings():
                api_key = os.environ.get("APP_API_KEY", "")
                if not api_key:
                    raise RuntimeError("APP_API_KEY is not set")
                raw_tokens = os.environ.get("APP_MAX_TOKENS", "512")
                try:
                    max_tokens = int(raw_tokens)
                except ValueError:
                    raise ValueError("APP_MAX_TOKENS must be an integer")
                debug = os.environ.get("APP_DEBUG", "").strip().lower() in ("1", "true", "yes")
                return {
                    "api_key": api_key,
                    "model": os.environ.get("APP_MODEL", "gpt-4o-mini"),
                    "max_tokens": max_tokens,
                    "debug": debug,
                }
        ''',
        "hints": [
            "os.environ.get(name, default) inside the function, plus int() in a try/except and a string check for the debug flag.",
            "Check the key first and raise if it's empty. Convert max tokens with int() (it tolerates spaces) and turn its error into your own. For debug, clean the value and check membership in a small tuple.",
            "1) key = os.environ.get('APP_API_KEY', ''); raise RuntimeError if falsy. 2) try int(os.environ.get('APP_MAX_TOKENS', '512')) except ValueError: raise the exact ValueError. 3) debug = value.strip().lower() in ('1', 'true', 'yes'). 4) Return the dict with the model default.",
        ],
    },
    {
        "id": "exam-working-python-4",
        "title": "Folder word report (CLI)",
        "difficulty": 3,
        "mode": "script",
        "prompt": r'''
            Before chunking documents for RAG, you want a quick report of what's in a folder.

            **Write a script** (`solution.py`) run as `python3 solution.py FOLDER` that prints a
            JSON report about the `.txt` files directly inside `FOLDER`.

            **Output:** JSON printed with `indent=2`, shaped like
            ```json
            {
              "files": [{"name": "a.txt", "words": 3}, {"name": "b.txt", "words": 10}],
              "total_words": 13,
              "longest": "b.txt"
            }
            ```

            **Rules**
            - Only files ending in `.txt` count; other files are ignored. Don't look in subfolders.
            - Words are what `.split()` gives you.
            - `"files"` is sorted by file name (A-Z).
            - `"longest"` is the name of the file with the most words; on a tie, the one that
              comes first by name. If there are no `.txt` files, `"files"` is `[]`,
              `"total_words"` is `0` and `"longest"` is `null`.
            - No argument given: print `usage: solution.py FOLDER` to **stderr** and exit with code `2`.
            - Folder doesn't exist: print `error: folder not found: <FOLDER>` to **stderr** and
              exit with code `1`.

            **Examples**

            Running `python3 solution.py docs` (where `docs/` has `a.txt` = "one two three" and
            `b.txt` = "hello") prints:
            ```json
            {
              "files": [
                {
                  "name": "a.txt",
                  "words": 3
                },
                {
                  "name": "b.txt",
                  "words": 1
                }
              ],
              "total_words": 4,
              "longest": "a.txt"
            }
            ```
            Running `python3 solution.py missing` prints `error: folder not found: missing` to
            stderr and exits with code 1.
        ''',
        "starter": r'''
            # Read the folder from the command line, then print the JSON report.
        ''',
        "tests": r'''
            import json
            from pathlib import Path

            def make_docs(name, files):
                folder = Path(name)
                folder.mkdir(exist_ok=True)
                for fname, text in files.items():
                    (folder / fname).write_text(text, encoding="utf-8")
                return name

            def test_report_for_a_folder():
                make_docs("docs", {"b.txt": "hello", "a.txt": "one two three", "notes.md": "x y z w"})
                r = run_script(["docs"])
                assert r.returncode == 0, f"exit code {r.returncode}, stderr: {r.stderr}"
                got = json.loads(r.stdout)
                assert got == {"files": [{"name": "a.txt", "words": 3}, {"name": "b.txt", "words": 1}],
                               "total_words": 4, "longest": "a.txt"}, f"got {got!r}"

            def test_output_is_indented_with_two_spaces():
                make_docs("docs2", {"a.txt": "hi"})
                r = run_script(["docs2"])
                assert '\n  "files"' in r.stdout, f"output was not indent=2 JSON:\n{r.stdout}"

            def test_tie_for_longest_goes_to_first_name():
                make_docs("tie", {"z.txt": "a b", "m.txt": "c d"})
                got = json.loads(run_script(["tie"]).stdout)
                assert got["longest"] == "m.txt", f"longest was {got['longest']!r}"

            def test_folder_without_txt_files():
                make_docs("none", {"readme.md": "hello"})
                got = json.loads(run_script(["none"]).stdout)
                assert got == {"files": [], "total_words": 0, "longest": None}, f"got {got!r}"

            def test_missing_argument_prints_usage_and_exits_2():
                r = run_script([])
                assert r.returncode == 2, f"exit code was {r.returncode}"
                assert "usage: solution.py FOLDER" in r.stderr, f"stderr was {r.stderr!r}"

            def test_missing_folder_prints_error_and_exits_1():
                r = run_script(["missing"])
                assert r.returncode == 1, f"exit code was {r.returncode}"
                assert "error: folder not found: missing" in r.stderr, f"stderr was {r.stderr!r}"
        ''',
        "solution": r'''
            import json
            import sys
            from pathlib import Path


            def main(argv):
                if len(argv) < 2:
                    print("usage: solution.py FOLDER", file=sys.stderr)
                    return 2
                folder = Path(argv[1])
                if not folder.is_dir():
                    print(f"error: folder not found: {argv[1]}", file=sys.stderr)
                    return 1
                files = []
                for path in sorted(folder.glob("*.txt"), key=lambda p: p.name):
                    words = len(path.read_text(encoding="utf-8").split())
                    files.append({"name": path.name, "words": words})
                longest = None
                best = -1
                for entry in files:
                    if entry["words"] > best:
                        best = entry["words"]
                        longest = entry["name"]
                report = {
                    "files": files,
                    "total_words": sum(f["words"] for f in files),
                    "longest": longest,
                }
                print(json.dumps(report, indent=2))
                return 0


            if __name__ == "__main__":
                sys.exit(main(sys.argv))
        ''',
        "hints": [
            "sys.argv for the folder, pathlib for listing files, json.dumps(..., indent=2) for output, sys.exit for the codes.",
            "Check the argument count and folder existence first (printing to sys.stderr). Then gather the .txt files sorted by name, count words for each, compute the total and the longest, and print the dict as JSON.",
            "1) If len(sys.argv) < 2: print usage to stderr, sys.exit(2). 2) folder = Path(sys.argv[1]); if not folder.is_dir(): print the error to stderr, sys.exit(1). 3) Loop over sorted(folder.glob('*.txt')) and build [{'name', 'words'}]. 4) Find the longest by keeping the first strictly-larger count. 5) print(json.dumps(report, indent=2)).",
        ],
    },
    {
        "id": "exam-working-python-5",
        "title": "Rank models on a leaderboard",
        "difficulty": 2,
        "prompt": r'''
            You ran the same eval on several models and want a leaderboard.

            **Write:** `rank_models(results, n)`

            - `results`: a list of dicts like `{"model": "a", "score": 0.91, "latency_ms": 820}`
            - `n`: how many models to return, an `int`
            - **Returns:** a list of the top `n` model names, best first

            **Rules**
            - Higher `score` is better.
            - On equal scores, lower `latency_ms` is better.
            - If score and latency are both equal, order by model name A-Z.
            - If `n` is larger than the number of results, return all of them.
            - Don't change the list you were given (its order must stay the same).

            **Examples**
            ```python
            results = [
                {"model": "a", "score": 0.80, "latency_ms": 500},
                {"model": "b", "score": 0.91, "latency_ms": 900},
                {"model": "c", "score": 0.91, "latency_ms": 300},
            ]
            rank_models(results, 2)    # returns ["c", "b"]
            rank_models(results, 10)   # returns ["c", "b", "a"]
            rank_models([], 3)         # returns []
            ```
        ''',
        "starter": r'''
            def rank_models(results, n):
                ...
        ''',
        "tests": r'''
            from solution import rank_models

            RESULTS = [
                {"model": "a", "score": 0.80, "latency_ms": 500},
                {"model": "b", "score": 0.91, "latency_ms": 900},
                {"model": "c", "score": 0.91, "latency_ms": 300},
            ]

            def test_top_two_uses_latency_to_break_ties():
                got = rank_models(RESULTS, 2)
                assert got == ["c", "b"], f"got {got!r}"

            def test_n_larger_than_results_returns_all():
                got = rank_models(RESULTS, 10)
                assert got == ["c", "b", "a"], f"got {got!r}"

            def test_full_tie_is_ordered_by_name():
                rows = [{"model": "zeta", "score": 0.5, "latency_ms": 100},
                        {"model": "alpha", "score": 0.5, "latency_ms": 100}]
                got = rank_models(rows, 2)
                assert got == ["alpha", "zeta"], f"got {got!r}"

            def test_empty_results():
                assert rank_models([], 3) == []

            def test_input_order_not_changed():
                rows = [dict(r) for r in RESULTS]
                rank_models(rows, 3)
                assert rows == RESULTS, "the input list was reordered or changed"
        ''',
        "solution": r'''
            def rank_models(results, n):
                ranked = sorted(results, key=lambda r: (-r["score"], r["latency_ms"], r["model"]))
                return [r["model"] for r in ranked[:n]]
        ''',
        "hints": [
            "sorted() with a key function that returns a tuple, then a comprehension to pull out names.",
            "Tuples compare item by item, so a key of (something for score, latency, name) sorts by all three. To make higher scores come first while the others go low-to-high, negate the score.",
            "1) ranked = sorted(results, key=lambda r: (-r['score'], r['latency_ms'], r['model'])). 2) Slice the first n. 3) Return [r['model'] for r in that slice]. sorted() returns a new list, so the input stays untouched.",
        ],
    },
    {
        "id": "exam-working-python-6",
        "title": "Quote a reply for an email",
        "difficulty": 2,
        "research": {
            "note": "Python ships a small standard-library module whose whole job is wrapping and "
                    "filling paragraphs of text to a fixed line width. Find it in the standard "
                    "library docs and use it instead of writing the line-breaking loop yourself.",
            "links": [],
        },
        "prompt": r'''
            A support bot emails its answers. The answer should be wrapped to a fixed width and
            quoted with `"> "` at the start of every line.

            **Write:** `quote_reply(text, width)`

            - `text`: the model's answer, a string
            - `width`: the maximum length of each output line **including** the `"> "` prefix,
              an `int` (at least 10)
            - **Returns:** the quoted text as one string, lines joined with `"\n"`

            **Rules**
            - First treat any run of whitespace (spaces, tabs, newlines) as a single space.
            - Break lines only between words and put as many words on each line as fit
              (so each line, prefix included, is at most `width` characters).
            - Every line starts with `"> "`. No trailing spaces on lines.
            - No word in the tests is longer than a line.
            - Empty or whitespace-only `text` returns `""`.

            **Examples**
            ```python
            quote_reply("The capital of France is Paris.", 16)
            # returns "> The capital of\n> France is\n> Paris."
            quote_reply("Hello   there,\n\nfriend", 40)
            # returns "> Hello there, friend"
            quote_reply("   ", 20)   # returns ""
            ```
        ''',
        "starter": r'''
            def quote_reply(text, width):
                ...
        ''',
        "tests": r'''
            from solution import quote_reply

            def test_wraps_and_quotes():
                got = quote_reply("The capital of France is Paris.", 16)
                assert got == "> The capital of\n> France is\n> Paris.", f"got {got!r}"

            def test_whitespace_runs_collapse():
                got = quote_reply("Hello   there,\n\nfriend", 40)
                assert got == "> Hello there, friend", f"got {got!r}"

            def test_lines_fit_width_and_are_filled_greedily():
                text = "retrieval augmented generation grounds answers in your own documents"
                got = quote_reply(text, 24)
                assert got == ("> retrieval augmented\n> generation grounds\n"
                               "> answers in your own\n> documents"), f"got {got!r}"
                assert all(len(line) <= 24 for line in got.split("\n"))

            def test_word_exactly_filling_the_line():
                got = quote_reply("abcdefgh ij", 10)
                assert got == "> abcdefgh\n> ij", f"got {got!r}"

            def test_blank_text_returns_empty_string():
                assert quote_reply("   ", 20) == ""
                assert quote_reply("", 20) == ""
        ''',
        "solution": r'''
            import textwrap


            def quote_reply(text, width):
                cleaned = " ".join(text.split())
                lines = textwrap.wrap(cleaned, width - 2)
                return "\n".join("> " + line for line in lines)
        ''',
        "hints": [
            "Look in the standard library's 'Text Processing Services' section of the docs.",
            "Clean the whitespace with split/join, wrap to width minus the prefix length (the module returns a list of lines), then add the prefix to each line and join with newlines.",
            "1) cleaned = ' '.join(text.split()). 2) import textwrap; lines = textwrap.wrap(cleaned, width - 2). 3) Return '\\n'.join('> ' + line for line in lines). An empty list joins to ''.",
        ],
    },
    {
        "id": "exam-working-python-7",
        "title": "Write a usage summary file",
        "difficulty": 2,
        "prompt": r'''
            At the end of a batch job, save a token-usage summary to disk as JSON.

            **Write:** `write_summary(records, path)`

            - `records`: a list of dicts like `{"model": "small", "tokens": 120, "ok": True}`
            - `path`: where to write the file, a string like `"reports/usage.json"`
            - **Returns:** the summary dict that was written

            **Summary shape**
            ```python
            {"by_model": {<model>: <total tokens of its ok records>},
             "failed": <number of records with ok False>,
             "total_tokens": <total tokens of all ok records>}
            ```

            **Rules**
            - Only records with `"ok": True` count towards tokens. A model that only has failed
              records does not appear in `"by_model"`.
            - Write the file as UTF-8 JSON using `indent=2` and `sort_keys=True`.
            - Create any missing parent folders of `path`.
            - An empty list writes and returns `{"by_model": {}, "failed": 0, "total_tokens": 0}`.

            **Examples**
            ```python
            write_summary([
                {"model": "small", "tokens": 120, "ok": True},
                {"model": "big", "tokens": 300, "ok": True},
                {"model": "small", "tokens": 80, "ok": True},
                {"model": "huge", "tokens": 999, "ok": False},
            ], "reports/usage.json")
            # returns {"by_model": {"small": 200, "big": 300}, "failed": 1, "total_tokens": 500}
            # and reports/usage.json now holds that dict as indented, key-sorted JSON
            ```
        ''',
        "starter": r'''
            def write_summary(records, path):
                ...
        ''',
        "tests": r'''
            import json
            from pathlib import Path
            from solution import write_summary

            RECORDS = [
                {"model": "small", "tokens": 120, "ok": True},
                {"model": "big", "tokens": 300, "ok": True},
                {"model": "small", "tokens": 80, "ok": True},
                {"model": "huge", "tokens": 999, "ok": False},
            ]
            EXPECTED = {"by_model": {"small": 200, "big": 300}, "failed": 1, "total_tokens": 500}

            def test_returns_the_summary():
                got = write_summary(RECORDS, "out1.json")
                assert got == EXPECTED, f"got {got!r}"

            def test_file_holds_the_same_summary():
                write_summary(RECORDS, "out2.json")
                got = json.loads(Path("out2.json").read_text(encoding="utf-8"))
                assert got == EXPECTED, f"file held {got!r}"

            def test_file_is_indented_and_key_sorted():
                write_summary(RECORDS, "out3.json")
                text = Path("out3.json").read_text(encoding="utf-8").strip()
                assert text == json.dumps(EXPECTED, indent=2, sort_keys=True), f"file text was:\n{text}"

            def test_creates_missing_parent_folders():
                write_summary(RECORDS, "reports/2026/usage.json")
                assert Path("reports/2026/usage.json").exists(), "file was not created"

            def test_empty_records():
                got = write_summary([], "empty.json")
                assert got == {"by_model": {}, "failed": 0, "total_tokens": 0}, f"got {got!r}"
        ''',
        "solution": r'''
            import json
            from pathlib import Path


            def write_summary(records, path):
                by_model = {}
                failed = 0
                for record in records:
                    if not record["ok"]:
                        failed += 1
                        continue
                    by_model[record["model"]] = by_model.get(record["model"], 0) + record["tokens"]
                summary = {"by_model": by_model, "failed": failed,
                           "total_tokens": sum(by_model.values())}
                target = Path(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
                return summary
        ''',
        "hints": [
            "A loop to total things up, then pathlib to make folders and json.dumps to write the file.",
            "Count failures and add up ok tokens per model in one pass. Build the summary dict. Before writing, make sure the file's parent folder exists (pathlib can create it with all its parents).",
            "1) Loop: if not ok, failed += 1; else add tokens to by_model[model] with .get(model, 0). 2) total = sum(by_model.values()). 3) p = Path(path); p.parent.mkdir(parents=True, exist_ok=True). 4) p.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf-8'). 5) Return summary.",
        ],
    },
]
