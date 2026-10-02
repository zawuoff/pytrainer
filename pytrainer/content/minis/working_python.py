"""Chapter projects for the "Everyday Python" module (working-python)."""

MINIS = [
    # ------------------------------------------------------------------ strings
    {
        "id": "mini-strings",
        "chapter": "strings",
        "title": "Markdown Stripper",
        "estimated_hours": 0.75,
        "main": "mdclean.py",
        "files": ["mdclean.py"],
        "brief": r'''
            LLMs love Markdown: `**bold**`, `# headings`, bullet lists, links. That looks great in a
            chat window and terrible in an SMS, a voice assistant or a plain-text email. Build a
            small cleaner that turns Markdown into readable plain text, plus two helpers a notes
            app would use: a title finder and a "3 min read" label.

            ## What to build

            A file `mdclean.py` with three functions:

            **`md_to_text(markdown)`**
            - `markdown`: a string with Markdown in it (several lines separated by `\n`)
            - **Returns:** a plain-text string (lines joined with `\n`, no `\n` at the very end)

            **`title_of(markdown)`**
            - **Returns:** the text of the first top-level heading (a line starting with `# `),
              stripped, with `**` and backticks removed; `"Untitled"` if there is none.

            **`reading_time(text, wpm=200)`**
            - `text`: any string; `wpm`: words per minute, an int
            - **Returns:** a string like `"3 min read"`

            ## Rules

            `md_to_text` works line by line, in this order:
            - **Code fences:** a line that starts with three backticks (after leading spaces) opens
              or closes a code block. The fence lines themselves are dropped. Lines *inside* a code
              block are kept exactly as they are (only trailing spaces removed) - none of the rules
              below apply to them.
            - **Headings:** a line that starts (at column 0) with one or more `#` followed by a
              space: remove the `#`s and the spaces after them, and make the rest UPPERCASE.
              `#python` (no space) is not a heading and stays as it is.
            - **Bullets:** a line whose first non-space characters are `- `, `* ` or `+ `: replace
              that marker with `• ` (bullet + space). Keep the indentation before it exactly.
            - **Inline markers:** remove every `**` and every backtick from the line.
            - **Links:** `[label](url)` becomes `label (url)`. A line has at most one link.
            - Remove trailing spaces from every line.
            - **Blank lines:** several blank lines in a row become one blank line. No blank lines at
              the start or end of the result. Empty input returns `""`.

            `title_of` looks only at lines starting with exactly `# ` (so `## Setup` doesn't count).

            `reading_time`: count words (split on whitespace), divide by `wpm` and round **up** to a
            whole number of minutes. The minimum is `1` (even for empty text).

            ## Examples

            ```python
            md_to_text("## Setup steps\n- Install **Python**\n  * run `pip`")
            # returns "SETUP STEPS\n• Install Python\n  • run pip"

            md_to_text("Read [the docs](https://docs.python.org) first.\n\n\n\n#python rocks   ")
            # returns "Read the docs (https://docs.python.org) first.\n\n#python rocks"

            md_to_text("Code:\n```python\nx = `**raw**`\n```\n")
            # returns "Code:\nx = `**raw**`"

            md_to_text("")                          # returns ""
            title_of("intro\n## Sub\n# The **Big** Plan\n")   # returns "The Big Plan"
            title_of("no headings here")            # returns "Untitled"
            reading_time("word " * 401)             # returns "3 min read"   (401 / 200 = 2.005 -> 3)
            reading_time("")                        # returns "1 min read"
            reading_time("a b c d", wpm=2)          # returns "2 min read"
            ```

            ## You'll need to find out
            - how to strip only one particular character (like `#`) from the **left** end of a
              string, leaving everything else alone
            - how to round a division result **up** to the next whole number (there's a function
              for it in a standard-library module about maths)

            ## Try it yourself
            ```python
            from mdclean import md_to_text
            print(md_to_text(open("README.md").read()))
            ```
            Or paste a Markdown answer from any chatbot into a string and clean it.
        ''',
        "explore": r'''
            - Handle several links on one line (hint: a `while` loop with `find` and a start position).
            - Turn numbered lists `1. Step` into `1) Step`, and `> quotes` into `"quotes"`.
            - Add `wrap(text, width)` that wraps long lines at word boundaries (then look at the
              `textwrap` module and compare).
        ''',
        "rubric": [
            "Each Markdown rule lives in a small, clearly named step or helper function",
            "Code-block state is tracked with a simple flag, not re-detected in fragile ways",
            "String methods (split/join/strip/replace/startswith) are used instead of manual character loops",
            "No needless repetition between md_to_text and title_of",
        ],
        "starter_files": {"mdclean.py": r'''
            """Turn Markdown into plain text."""


            def md_to_text(markdown):
                ...


            def title_of(markdown):
                ...


            def reading_time(text, wpm=200):
                ...
        '''},
        "solution_files": {"mdclean.py": r'''
            """Turn Markdown into plain text."""

            import math


            def strip_inline(line):
                line = line.replace("**", "").replace("`", "")
                start = line.find("[")
                middle = line.find("](")
                if start != -1 and middle > start:
                    end = line.find(")", middle)
                    if end != -1:
                        label = line[start + 1:middle]
                        url = line[middle + 2:end]
                        line = line[:start] + label + " (" + url + ")" + line[end + 1:]
                return line


            def convert_line(line):
                if line.startswith("#"):
                    rest = line.lstrip("#")
                    if rest.startswith(" "):
                        line = rest.strip().upper()
                else:
                    stripped = line.lstrip()
                    if stripped[:2] in ("- ", "* ", "+ "):
                        indent = line[:len(line) - len(stripped)]
                        line = indent + "• " + stripped[2:]
                return strip_inline(line).rstrip()


            def md_to_text(markdown):
                lines = []
                in_code = False
                for raw in markdown.splitlines():
                    if raw.strip().startswith("```"):
                        in_code = not in_code
                        continue
                    lines.append(raw.rstrip() if in_code else convert_line(raw))
                result = []
                for line in lines:
                    if line == "" and (not result or result[-1] == ""):
                        continue
                    result.append(line)
                if result and result[-1] == "":
                    result.pop()
                return "\n".join(result)


            def title_of(markdown):
                for line in markdown.splitlines():
                    if line.startswith("# "):
                        return line[2:].replace("**", "").replace("`", "").strip()
                return "Untitled"


            def reading_time(text, wpm=200):
                minutes = max(1, math.ceil(len(text.split()) / wpm))
                return f"{minutes} min read"
        '''},
        "tests": r'''
            from mdclean import md_to_text, title_of, reading_time

            def test_headings_lose_hashes_and_become_uppercase():
                got = md_to_text("# Hello\n### Deep   dive")
                assert got == "HELLO\nDEEP   DIVE", f"got {got!r}"

            def test_hash_without_space_is_not_a_heading():
                got = md_to_text("#python rocks")
                assert got == "#python rocks", f"got {got!r}"

            def test_bullets_become_dots_and_keep_indentation():
                got = md_to_text("- one\n* two\n+ three\n    - deep")
                assert got == "• one\n• two\n• three\n    • deep", f"got {got!r}"

            def test_bold_and_backticks_are_removed():
                got = md_to_text("Use **pip** to install `requests` **now**")
                assert got == "Use pip to install requests now", f"got {got!r}"

            def test_link_becomes_label_and_url():
                got = md_to_text("Read [the docs](https://docs.python.org) first.")
                assert got == "Read the docs (https://docs.python.org) first.", f"got {got!r}"

            def test_code_blocks_kept_verbatim_and_fences_dropped():
                got = md_to_text("Code:\n```python\n# not a heading\nx = `**raw**`\n```\n- after")
                assert got == "Code:\n# not a heading\nx = `**raw**`\n• after", f"got {got!r}"

            def test_blank_lines_collapsed_and_trimmed_at_the_ends():
                got = md_to_text("\n\nfirst\n\n\n\nsecond\n   \n\n")
                assert got == "first\n\nsecond", f"got {got!r}"

            def test_trailing_spaces_removed_from_every_line():
                got = md_to_text("hello   \n- item  ")
                assert got == "hello\n• item", f"got {got!r}"

            def test_empty_input_returns_empty_string():
                assert md_to_text("") == "", f"got {md_to_text('')!r}"

            def test_full_document():
                doc = ("# Release **notes**\n\nVersion `2.0` is out!\n\n\n## What changed\n"
                       "- Faster [search](https://x.io/s)\n  * Smaller   \n")
                want = ("RELEASE NOTES\n\nVersion 2.0 is out!\n\nWHAT CHANGED\n"
                        "• Faster search (https://x.io/s)\n  • Smaller")
                got = md_to_text(doc)
                assert got == want, f"got {got!r}"

            def test_title_of_finds_first_top_level_heading():
                got = title_of("intro\n## Sub\n# The **Big** `Plan`\n# Second")
                assert got == "The Big Plan", f"got {got!r}"

            def test_title_of_without_heading_is_untitled():
                got = title_of("## only a subheading\ntext")
                assert got == "Untitled", f"got {got!r}"

            def test_reading_time_rounds_up():
                assert reading_time("word " * 401) == "3 min read", f"got {reading_time('word ' * 401)!r}"
                assert reading_time("word " * 400) == "2 min read", f"got {reading_time('word ' * 400)!r}"

            def test_reading_time_minimum_one_minute_and_custom_wpm():
                assert reading_time("") == "1 min read", f"got {reading_time('')!r}"
                got = reading_time("a b c d", wpm=2)
                assert got == "2 min read", f"got {got!r}"
                got = reading_time("a b c d e", wpm=2)
                assert got == "3 min read", f"got {got!r}"
        ''',
    },
    # ------------------------------------------------------------ comprehensions
    {
        "id": "mini-comprehensions",
        "chapter": "comprehensions",
        "title": "Wordle Helper",
        "estimated_hours": 0.75,
        "main": "wordle.py",
        "files": ["wordle.py"],
        "brief": r'''
            Stuck on today's Wordle? Build the engine of a helper: clean a word list, score a guess,
            filter the words that still fit your clues and rank letters by how common they are.
            Almost every function here is one or two comprehensions - that's the point.

            ## What to build

            A file `wordle.py` with these functions:

            **`clean_words(raw_words, length=5)`**
            - `raw_words`: a list of strings, e.g. `["Crane ", "slate", "don't", "CRANE"]`
            - **Returns:** a new list of the usable words: stripped, lowercase, unique, sorted A-Z

            **`feedback(guess, answer)`**
            - two lowercase words of the same length
            - **Returns:** a string with one character per letter: `"G"` (green), `"Y"` (yellow)
              or `"-"` (gray)

            **`matches(word, green, yellow, gray)`**
            - `word`: a lowercase word, e.g. `"crane"`
            - `green`: a dict position -> letter, e.g. `{0: "c"}` (positions start at 0)
            - `yellow`: a dict letter -> list of positions where that letter is **not**, e.g. `{"a": [1]}`
            - `gray`: a string of letters that are not in the word, e.g. `"sio"`
            - **Returns:** `True` if the word fits every clue, else `False`

            **`filter_words(words, green, yellow, gray)`**
            - **Returns:** a new list of the words that match all the clues, in their original order

            **`letter_counts(words)`**
            - **Returns:** a dict letter -> how many of the words contain that letter

            **`score_words(words)`**
            - **Returns:** a dict word -> score (see Rules)

            ## Rules
            - `clean_words`: strip spaces, lowercase, then keep only words that are exactly `length`
              characters long **and** made only of letters (`"don't"` and `"ab1de"` are dropped).
              Duplicates (after lowercasing) appear once. Result sorted A-Z. Don't change `raw_words`.
            - `feedback`: position `i` is `"G"` if `guess[i] == answer[i]`, otherwise `"Y"` if that
              letter appears anywhere in `answer`, otherwise `"-"`. (Simpler than the real game:
              repeated letters are not special.)
            - `matches`: every green position holds its letter; every yellow letter is in the word
              but not at any of its listed positions; no gray letter appears anywhere in the word.
              Empty clues (`{}`, `{}`, `""`) match every word.
            - `letter_counts`: a word counts **once** per letter even if the letter repeats
              (`"eerie"` adds 1 to `e`, not 3). Only letters that appear get a key.
            - `score_words`: a word's score is the sum of `letter_counts(words)` for each **different**
              letter in it (repeated letters count once).

            ## Examples
            ```python
            clean_words(["Crane ", "slate", "don't", "CRANE", "ab1de", "cat"])  # ["crane", "slate"]
            clean_words(["cat", "Dog", "bird"], length=3)                     # ["cat", "dog"]

            feedback("slate", "plate")     # "-GGGG"
            feedback("crane", "react")     # "YYG-Y"   (c: Y, r: Y, a: G, n: -, e: Y)
            feedback("abc", "xyz")         # "---"

            matches("crane", {0: "c"}, {"a": [1]}, "sio")   # True
            matches("cairn", {0: "c"}, {"a": [1]}, "sio")   # False ("a" is at position 1, and "i" is gray)
            filter_words(["crane", "cairn", "caper", "slate"], {0: "c"}, {"e": [4]}, "")
            # ["caper"]   ("crane" has e at position 4, "cairn" has no e, "slate" doesn't start with c)

            letter_counts(["eerie", "err"])     # {"e": 2, "r": 2, "i": 1}
            score_words(["eerie", "err"])       # {"eerie": 5, "err": 4}
            ```

            ## You'll need to find out
            - how to check that a string is made **only of letters** (one string method does it)

            ## Try it yourself
            ```python
            from wordle import clean_words, filter_words
            words = clean_words(open("/usr/share/dict/words").read().split())
            print(filter_words(words, {0: "s"}, {"a": [2]}, "rtie")[:20])
            ```
        ''',
        "explore": r'''
            - Add `best_guess(words)`: the word with the highest score (you'll meet `max(..., key=...)`
              in the sorting chapter).
            - Make `feedback` handle repeated letters exactly like the real game.
            - Build a tiny loop that plays against a random answer and counts the guesses it needs.
        ''',
        "rubric": [
            "Comprehensions (list/dict/set) and any()/all() are used where they read naturally",
            "No comprehension is so nested that a plain loop would be clearer",
            "letter_counts is reused by score_words rather than duplicated",
            "Inputs are never modified",
        ],
        "starter_files": {"wordle.py": r'''
            """A Wordle helper built from comprehensions."""


            def clean_words(raw_words, length=5):
                ...


            def feedback(guess, answer):
                ...


            def matches(word, green, yellow, gray):
                ...


            def filter_words(words, green, yellow, gray):
                ...


            def letter_counts(words):
                ...


            def score_words(words):
                ...
        '''},
        "solution_files": {"wordle.py": r'''
            """A Wordle helper built from comprehensions."""


            def clean_words(raw_words, length=5):
                cleaned = {w.strip().lower() for w in raw_words}
                return sorted(w for w in cleaned if len(w) == length and w.isalpha())


            def feedback(guess, answer):
                return "".join("G" if g == a else "Y" if g in answer else "-"
                               for g, a in zip(guess, answer))


            def matches(word, green, yellow, gray):
                return (all(word[pos] == letter for pos, letter in green.items())
                        and all(letter in word and all(word[p] != letter for p in spots)
                                for letter, spots in yellow.items())
                        and not any(letter in word for letter in gray))


            def filter_words(words, green, yellow, gray):
                return [w for w in words if matches(w, green, yellow, gray)]


            def letter_counts(words):
                letters = {c for w in words for c in w}
                return {c: sum(c in w for w in words) for c in letters}


            def score_words(words):
                counts = letter_counts(words)
                return {w: sum(counts[c] for c in set(w)) for w in words}
        '''},
        "tests": r'''
            from wordle import clean_words, feedback, matches, filter_words, letter_counts, score_words

            def test_clean_words_strips_lowercases_dedupes_and_sorts():
                got = clean_words(["Slate", " crane ", "CRANE", "adieu"])
                assert got == ["adieu", "crane", "slate"], f"got {got!r}"

            def test_clean_words_drops_wrong_length_and_non_letters():
                got = clean_words(["don't", "ab1de", "cat", "planet", "crane", "e-mai"])
                assert got == ["crane"], f"got {got!r}"

            def test_clean_words_custom_length_and_input_unchanged():
                raw = ["cat", "Dog", "bird", "c4t"]
                got = clean_words(raw, length=3)
                assert got == ["cat", "dog"], f"got {got!r}"
                assert raw == ["cat", "Dog", "bird", "c4t"], "clean_words changed its input list"

            def test_feedback_green_yellow_gray():
                assert feedback("slate", "plate") == "-GGGG", f"got {feedback('slate', 'plate')!r}"
                assert feedback("crane", "react") == "YYG-Y", f"got {feedback('crane', 'react')!r}"
                assert feedback("abc", "xyz") == "---", f"got {feedback('abc', 'xyz')!r}"
                assert feedback("plate", "plate") == "GGGGG", f"got {feedback('plate', 'plate')!r}"

            def test_matches_checks_green_positions():
                assert matches("crane", {0: "c", 4: "e"}, {}, "") is True
                assert matches("crane", {1: "a"}, {}, "") is False

            def test_matches_yellow_letter_present_but_not_at_listed_positions():
                assert matches("crane", {}, {"a": [1]}, "") is True
                assert matches("cairn", {}, {"a": [1]}, "") is False, "a is at position 1"
                assert matches("slept", {}, {"a": [0]}, "") is False, "a is not in the word at all"

            def test_matches_gray_letters_absent():
                assert matches("crane", {}, {}, "sio") is True
                assert matches("cairn", {}, {}, "sio") is False

            def test_empty_clues_match_everything():
                assert matches("zzzzz", {}, {}, "") is True

            def test_filter_words_keeps_original_order():
                words = ["crane", "cairn", "caper", "slate", "cider"]
                got = filter_words(words, {0: "c"}, {"e": [4]}, "")
                assert got == ["caper", "cider"], f"got {got!r}"
                got = filter_words(words, {}, {}, "")
                assert got == words, f"got {got!r}"

            def test_letter_counts_counts_each_word_once_per_letter():
                got = letter_counts(["eerie", "err"])
                assert got == {"e": 2, "r": 2, "i": 1}, f"got {got!r}"
                assert letter_counts([]) == {}, f"got {letter_counts([])!r}"

            def test_score_words_sums_counts_of_different_letters():
                got = score_words(["eerie", "err"])
                assert got == {"eerie": 5, "err": 4}, f"got {got!r}"
                got = score_words(["crane", "slate"])
                assert got == {"crane": 7, "slate": 7}, f"got {got!r}"
        ''',
    },
    # --------------------------------------------------------------------- json
    {
        "id": "mini-json",
        "chapter": "json",
        "title": "Quiz Bank Builder",
        "estimated_hours": 1,
        "main": "quizbank.py",
        "files": ["quizbank.py"],
        "brief": r'''
            You asked a model to "write 10 multiple-choice questions about Python as JSON". It
            answered with a friendly sentence, a JSON array, some half-broken questions and a
            "Good luck!". Build the part of a quiz app that rescues the JSON, checks every
            question, keeps the good ones and saves a clean question bank.

            ## What to build

            A file `quizbank.py` with four functions:

            **`extract_array(reply)`**
            - `reply`: the model's whole answer, a string
            - **Returns:** the parsed JSON array (a Python list)

            **`check_question(item)`**
            - `item`: one element of that list (should be a dict, but models make mistakes)
            - **Returns:** a list of problem strings; an empty list `[]` means the question is valid

            **`build_bank(reply, topic)`**
            - `reply`: the model's answer; `topic`: a string like `"python"`
            - **Returns:** a dict with exactly these keys:
              `{"topic": topic, "count": <number of valid questions>, "questions": [...], "rejected": [...]}`

            **`to_json(bank)`**
            - **Returns:** the bank as a pretty JSON string

            ## Rules
            - `extract_array`: the JSON is the text from the **first** `[` to the **last** `]`
              (both included). Strings have a method that searches from the right - use it or a loop.
            - If there is no `[`, or no `]` after it, raise `ValueError("no JSON array found")`.
            - If that text isn't valid JSON, raise `ValueError` with the message
              `bad JSON at line L, column C`, where `L` and `C` are the line and column the JSON
              parser reports for the extracted text (its `[` is line 1, column 1).
            - `check_question` checks, and reports problems in exactly this order:
              - if `item` is not a dict: return `["not an object"]` (nothing else is checked)
              - `"missing question"` - unless `"question"` is a string with something besides spaces
              - `"need 2-4 choices"` - unless `"choices"` is a list of 2, 3 or 4 items, all strings
              - `"answer not in choices"` - unless `"choices"` is a list and `"answer"` is one of its items
              (missing keys count as problems, they don't crash)
            - `build_bank`: `"questions"` holds the valid questions in their original order, each as a
              **new** dict with only the keys `"question"` (stripped), `"choices"` and `"answer"`
              (extra keys like `"id"` are dropped). `"rejected"` holds one dict
              `{"index": i, "problems": [...]}` per invalid item, where `i` is its 0-based position in
              the array. Errors from `extract_array` are not caught.
            - `to_json`: 2-space indentation, and non-English characters stay readable (`é`, not `é`).
              `json.loads(to_json(bank))` must give back the same bank.

            ## Examples
            ```python
            reply = ('Sure! Here you go: [{"question": " 2 + 2? ", "choices": ["3", "4"], "answer": "4", "id": 1},'
                     ' {"question": "", "choices": ["Paris"], "answer": "Rome"}, "oops"] Good luck!')

            extract_array("[1, 2] and [3]")    # raises ValueError: bad JSON at line 1, column 8
            extract_array("no json here")      # raises ValueError: no JSON array found
            extract_array('Here:\n[\n  {"question": "Q?",\n   "answer": oops}\n]')
            # raises ValueError: bad JSON at line 3, column 14

            check_question({"question": "2 + 2?", "choices": ["3", "4"], "answer": "4"})   # []
            check_question({"question": "", "choices": ["Paris"], "answer": "Rome"})
            # ["missing question", "need 2-4 choices", "answer not in choices"]
            check_question("oops")             # ["not an object"]

            build_bank(reply, "maths")
            # {"topic": "maths", "count": 1,
            #  "questions": [{"question": "2 + 2?", "choices": ["3", "4"], "answer": "4"}],
            #  "rejected": [{"index": 1, "problems": ["missing question", "need 2-4 choices", "answer not in choices"]},
            #               {"index": 2, "problems": ["not an object"]}]}

            print(to_json({"topic": "café", "count": 0, "questions": [], "rejected": []}))
            # {
            #   "topic": "café",
            #   "count": 0,
            #   "questions": [],
            #   "rejected": []
            # }
            ```

            ## You'll need to find out
            - how to check whether a value is of a certain type (is it a dict? a list? a string?)
            - where a JSON parsing error stores the **line** and **column** of the mistake

            ## Try it yourself
            ```python
            from quizbank import build_bank, to_json
            reply = open("reply.txt", encoding="utf-8").read()   # paste a real model answer in there
            print(to_json(build_bank(reply, "python")))
            ```
        ''',
        "explore": r'''
            - Add `merge(bank_a, bank_b)` that combines two banks and skips duplicate questions
              (compare them case-insensitively).
            - Save the bank to `bank.json` with `json.dump`, and load it back next time.
            - Ask a real model for questions and see how often each problem shows up.
        ''',
        "rubric": [
            "Each problem check is a small, readable condition; the order of problems matches the spec",
            "JSONDecodeError is caught narrowly and re-raised as a clear ValueError",
            "build_bank reuses extract_array and check_question instead of repeating their logic",
            "No mutation of the parsed input when building clean question dicts",
        ],
        "starter_files": {"quizbank.py": r'''
            """Rescue quiz questions from a chatty model reply."""

            import json


            def extract_array(reply):
                ...


            def check_question(item):
                ...


            def build_bank(reply, topic):
                ...


            def to_json(bank):
                ...
        '''},
        "solution_files": {"quizbank.py": r'''
            """Rescue quiz questions from a chatty model reply."""

            import json


            def extract_array(reply):
                start = reply.find("[")
                end = reply.rfind("]")
                if start == -1 or end < start:
                    raise ValueError("no JSON array found")
                try:
                    return json.loads(reply[start:end + 1])
                except json.JSONDecodeError as exc:
                    raise ValueError(f"bad JSON at line {exc.lineno}, column {exc.colno}") from exc


            def check_question(item):
                if not isinstance(item, dict):
                    return ["not an object"]
                problems = []
                question = item.get("question")
                if not (isinstance(question, str) and question.strip()):
                    problems.append("missing question")
                choices = item.get("choices")
                good_choices = (isinstance(choices, list) and 2 <= len(choices) <= 4
                                and all(isinstance(c, str) for c in choices))
                if not good_choices:
                    problems.append("need 2-4 choices")
                if not (isinstance(choices, list) and item.get("answer") in choices):
                    problems.append("answer not in choices")
                return problems


            def build_bank(reply, topic):
                questions, rejected = [], []
                for i, item in enumerate(extract_array(reply)):
                    problems = check_question(item)
                    if problems:
                        rejected.append({"index": i, "problems": problems})
                    else:
                        questions.append({"question": item["question"].strip(),
                                          "choices": item["choices"],
                                          "answer": item["answer"]})
                return {"topic": topic, "count": len(questions),
                        "questions": questions, "rejected": rejected}


            def to_json(bank):
                return json.dumps(bank, indent=2, ensure_ascii=False)
        '''},
        "tests": r'''
            import json
            from quizbank import extract_array, check_question, build_bank, to_json

            FENCE = "`" * 3
            REPLY = ("Sure! Here are your questions:\n" + FENCE + "json\n[\n"
                     '  {"question": " What does len([1, 2]) return? ", "choices": ["1", "2"], "answer": "2", "id": 1},\n'
                     '  {"question": "", "choices": ["Paris"], "answer": "Rome"},\n'
                     '  "oops",\n'
                     '  {"question": "Which is a list?", "choices": ["(1,)", "[1]", "{1}"], "answer": "[1]"}\n'
                     "]\n" + FENCE + "\nGood luck!")

            def test_extract_array_finds_json_inside_chatty_reply():
                got = extract_array(REPLY)
                assert isinstance(got, list) and len(got) == 4, f"got {got!r}"
                assert got[2] == "oops", f"got {got!r}"

            def test_extract_array_without_array_raises_value_error():
                for text in ("no json here", "only an opening [ bracket", "backwards ] then ["):
                    try:
                        extract_array(text)
                    except ValueError as exc:
                        assert str(exc) == "no JSON array found", f"message was {str(exc)!r}"
                    else:
                        raise AssertionError(f"expected ValueError for {text!r}")

            def test_broken_json_reports_line_and_column():
                cases = [('Here:\n[\n  {"question": "Q?",\n   "answer": oops}\n]', "bad JSON at line 3, column 14"),
                         ("[1, 2] and [3]", "bad JSON at line 1, column 8")]
                for text, want in cases:
                    try:
                        extract_array(text)
                    except ValueError as exc:
                        assert str(exc) == want, f"for {text!r}: message was {str(exc)!r}, expected {want!r}"
                    else:
                        raise AssertionError(f"expected ValueError for {text!r}")

            def test_valid_question_has_no_problems():
                got = check_question({"question": "2 + 2?", "choices": ["3", "4", "5", "22"], "answer": "4"})
                assert got == [], f"got {got!r}"

            def test_non_dict_item_is_not_an_object():
                for item in ("oops", 42, None, ["question"]):
                    got = check_question(item)
                    assert got == ["not an object"], f"for {item!r} got {got!r}"

            def test_missing_or_blank_question():
                base = {"choices": ["a", "b"], "answer": "a"}
                for q in (None, "   ", 7):
                    item = dict(base) if q is None else dict(base, question=q)
                    got = check_question(item)
                    assert got == ["missing question"], f"for question={q!r} got {got!r}"

            def test_choices_must_be_2_to_4_strings():
                for choices in (["a"], ["a", "b", "c", "d", "e"], ["a", 2], "ab"):
                    got = check_question({"question": "Q?", "choices": choices, "answer": "a"})
                    assert "need 2-4 choices" in got, f"for choices={choices!r} got {got!r}"

            def test_answer_must_be_one_of_the_choices():
                got = check_question({"question": "Q?", "choices": ["a", "b"], "answer": "c"})
                assert got == ["answer not in choices"], f"got {got!r}"
                got = check_question({"question": "Q?", "choices": ["a", "b"]})
                assert got == ["answer not in choices"], f"missing answer: got {got!r}"

            def test_problems_reported_in_order():
                got = check_question({"question": "", "choices": ["Paris"], "answer": "Rome"})
                assert got == ["missing question", "need 2-4 choices", "answer not in choices"], f"got {got!r}"
                got = check_question({})
                assert got == ["missing question", "need 2-4 choices", "answer not in choices"], f"empty dict: got {got!r}"

            def test_build_bank_keeps_clean_valid_questions():
                bank = build_bank(REPLY, "python")
                assert set(bank) == {"topic", "count", "questions", "rejected"}, f"keys {sorted(bank)!r}"
                assert bank["topic"] == "python" and bank["count"] == 2, f"got {bank!r}"
                assert bank["questions"] == [
                    {"question": "What does len([1, 2]) return?", "choices": ["1", "2"], "answer": "2"},
                    {"question": "Which is a list?", "choices": ["(1,)", "[1]", "{1}"], "answer": "[1]"},
                ], f"questions {bank['questions']!r}"

            def test_build_bank_lists_rejected_items_by_index():
                bank = build_bank(REPLY, "python")
                assert bank["rejected"] == [
                    {"index": 1, "problems": ["missing question", "need 2-4 choices", "answer not in choices"]},
                    {"index": 2, "problems": ["not an object"]},
                ], f"rejected {bank['rejected']!r}"

            def test_to_json_is_pretty_and_keeps_accents():
                bank = {"topic": "café", "count": 0, "questions": [], "rejected": []}
                got = to_json(bank)
                want = '{\n  "topic": "café",\n  "count": 0,\n  "questions": [],\n  "rejected": []\n}'
                assert got == want, f"got {got!r}"

            def test_to_json_round_trips():
                bank = build_bank(REPLY, "prüfung")
                assert json.loads(to_json(bank)) == bank, "json.loads(to_json(bank)) is not the same bank"
        ''',
    },
    # -------------------------------------------------------------------- files
    {
        "id": "mini-files",
        "chapter": "files",
        "title": "Notes Search",
        "estimated_hours": 1,
        "main": "notes.py",
        "files": ["notes.py"],
        "brief": r'''
            You keep notes as `.md` and `.txt` files in a folder, with sub-folders for projects.
            Build a tiny search tool for it - the same "walk a folder of documents" step that
            starts every RAG pipeline. It finds the notes, greps them, reports sizes and saves
            search results to a file.

            ## What to build

            A file `notes.py` with four functions. Every path in a result is **relative to the
            notes folder** and written with `/`, like `"work/ideas.txt"`.

            **`find_notes(folder)`**
            - `folder`: path of the notes folder, a string like `"notes"`
            - **Returns:** a sorted list of relative paths (strings) of every `.md` and `.txt` file
              in the folder, at any depth

            **`search(folder, query)`**
            - **Returns:** a list of strings `"path:line: text"`, one per matching line

            **`note_sizes(folder)`**
            - **Returns:** a dict relative path -> file size in **bytes** (an int), for every note

            **`save_results(results, out_path)`**
            - `results`: a list of strings (like the ones `search` returns); `out_path`: a string
            - **Returns:** the number of results written (an int)

            ## Rules
            - `find_notes`: only files whose name ends in `.md` or `.txt` (other files and folders are
              ignored). Sorted A-Z as strings. If `folder` doesn't exist, raise `FileNotFoundError`
              with a message that contains the folder name. (`search` and `note_sizes` behave the same.)
            - `search`: strip the query; a blank query returns `[]`. A line matches if it contains the
              query, ignoring upper/lower case. `line` is the 1-based line number, `text` is the line
              stripped of surrounding spaces. Results come file by file in `find_notes` order, then by
              line number.
            - Some notes were saved by old tools and contain bytes that are **not valid UTF-8**.
              Reading them must not crash: invalid bytes become the replacement character `�`
              (`"�"`), and the rest of the file is searched normally.
            - `note_sizes`: the real size on disk in bytes (`"café\n"` is 6 bytes, not 5 characters).
            - `save_results`: write each result on its own line (every line ends with `\n`), UTF-8.
              If `results` is empty, write the single line `no matches`. Create any missing parent
              folders of `out_path`. An existing file is replaced.

            ## Examples

            With this folder:
            ```
            notes/todo.md            "Buy milk\n  Call Ada about the RAG demo  \n"
            notes/work/ideas.txt     "rag pipeline\nEval harness\n"
            notes/work/2026/q3.md    "# Q3\nShip the RAG bot\n"
            notes/work/data.json     (ignored: not a note)
            ```
            ```python
            find_notes("notes")    # ["todo.md", "work/2026/q3.md", "work/ideas.txt"]
            search("notes", "rag")
            # ["todo.md:2: Call Ada about the RAG demo",
            #  "work/2026/q3.md:2: Ship the RAG bot",
            #  "work/ideas.txt:1: rag pipeline"]
            search("notes", "   ")         # []
            note_sizes("notes")["work/ideas.txt"]   # 26
            save_results(search("notes", "rag"), "out/rag.txt")    # 3  (creates the out/ folder)
            save_results([], "out/none.txt")                       # 0  (file contains "no matches\n")
            find_notes("nope")             # raises FileNotFoundError (message contains "nope")
            ```

            ## You'll need to find out
            - how to get a file's size in bytes from a `Path` (without reading the file)
            - how to tell `open()` / `read_text()` to **replace** undecodable bytes instead of crashing

            ## Try it yourself
            ```python
            from notes import search, save_results
            hits = search("/path/to/your/notes", "todo")
            print(save_results(hits, "reports/todo.txt"), "hits saved")
            ```
        ''',
        "explore": r'''
            - Skip hidden files and folders (names starting with `.`).
            - Show one line of context before and after each hit, like `grep -C 1`.
            - Turn it into a command-line tool after the scripts chapter: `python3 notes.py rag --folder notes`.
        ''',
        "rubric": [
            "pathlib is used for paths (joining, globbing, relative paths) instead of string concatenation",
            "Files are read and written with an explicit encoding and closed properly",
            "find_notes is the single place that decides what counts as a note; the others reuse it",
            "The missing-folder case is handled in one clear place",
        ],
        "starter_files": {"notes.py": r'''
            """Search a folder of notes."""

            from pathlib import Path


            def find_notes(folder):
                ...


            def search(folder, query):
                ...


            def note_sizes(folder):
                ...


            def save_results(results, out_path):
                ...
        '''},
        "solution_files": {"notes.py": r'''
            """Search a folder of notes."""

            from pathlib import Path

            SUFFIXES = (".md", ".txt")


            def find_notes(folder):
                root = Path(folder)
                if not root.is_dir():
                    raise FileNotFoundError(f"notes folder not found: {folder}")
                return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                              if p.is_file() and p.suffix in SUFFIXES)


            def search(folder, query):
                paths = find_notes(folder)
                query = query.strip().lower()
                if not query:
                    return []
                results = []
                for rel in paths:
                    text = (Path(folder) / rel).read_text(encoding="utf-8", errors="replace")
                    for number, line in enumerate(text.splitlines(), start=1):
                        if query in line.lower():
                            results.append(f"{rel}:{number}: {line.strip()}")
                return results


            def note_sizes(folder):
                return {rel: (Path(folder) / rel).stat().st_size for rel in find_notes(folder)}


            def save_results(results, out_path):
                out = Path(out_path)
                out.parent.mkdir(parents=True, exist_ok=True)
                lines = results if results else ["no matches"]
                with open(out, "w", encoding="utf-8") as fh:
                    for line in lines:
                        fh.write(line + "\n")
                return len(results)
        '''},
        "tests": r'''
            from pathlib import Path
            from notes import find_notes, search, note_sizes, save_results

            NOTES = {
                "todo.md": "Buy milk\n  Call Ada about the RAG demo  \n",
                "work/ideas.txt": "rag pipeline\nEval harness\n",
                "work/2026/q3.md": "# Q3\nShip the RAG bot\n",
                "work/data.json": '{"rag": true}\n',
                "script.py": "rag = 1\n",
            }

            def make(folder, files=NOTES):
                for rel, content in files.items():
                    p = Path(folder) / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    if isinstance(content, bytes):
                        p.write_bytes(content)
                    else:
                        p.write_text(content, encoding="utf-8")
                return folder

            def test_find_notes_lists_md_and_txt_at_any_depth_sorted():
                got = find_notes(make("n_find"))
                assert got == ["todo.md", "work/2026/q3.md", "work/ideas.txt"], f"got {got!r}"

            def test_find_notes_missing_folder_raises_file_not_found():
                try:
                    find_notes("no_such_notes_dir")
                except FileNotFoundError as exc:
                    assert "no_such_notes_dir" in str(exc), f"message was {str(exc)!r}"
                else:
                    raise AssertionError("expected FileNotFoundError for a missing folder")

            def test_search_is_case_insensitive_with_line_numbers():
                got = search(make("n_search"), "rag")
                assert got == ["todo.md:2: Call Ada about the RAG demo",
                               "work/2026/q3.md:2: Ship the RAG bot",
                               "work/ideas.txt:1: rag pipeline"], f"got {got!r}"

            def test_search_strips_the_query_and_blank_query_returns_empty():
                folder = make("n_blank")
                assert search(folder, "  harness ") == ["work/ideas.txt:2: Eval harness"], \
                    f"got {search(folder, '  harness ')!r}"
                assert search(folder, "   ") == [], f"got {search(folder, '   ')!r}"
                assert search(folder, "") == [], f"got {search(folder, '')!r}"

            def test_search_with_no_hits_returns_empty_list():
                assert search(make("n_none"), "kubernetes") == []

            def test_search_missing_folder_raises_file_not_found():
                try:
                    search("missing_notes_folder", "x")
                except FileNotFoundError:
                    pass
                else:
                    raise AssertionError("expected FileNotFoundError for a missing folder")

            def test_invalid_utf8_bytes_do_not_crash_search():
                folder = make("n_bytes", {"old.txt": b"caf\xe9 notes\nmeeting at 10\n", "new.md": "meeting notes\n"})
                got = search(folder, "meeting")
                assert got == ["new.md:1: meeting notes", "old.txt:2: meeting at 10"], f"got {got!r}"
                got = search(folder, "caf")
                assert got == ["old.txt:1: caf� notes"], f"got {got!r}"

            def test_note_sizes_are_bytes_on_disk():
                folder = make("n_sizes", {"a.md": "café\n", "sub/b.txt": "", "c.json": "{}"})
                got = note_sizes(folder)
                assert got == {"a.md": 6, "sub/b.txt": 0}, f"got {got!r}"

            def test_save_results_creates_folders_and_writes_lines():
                results = ["a.md:1: one", "b.txt:3: two"]
                count = save_results(results, "reports/2026/hits.txt")
                assert count == 2, f"returned {count!r}"
                text = Path("reports/2026/hits.txt").read_text(encoding="utf-8")
                assert text == "a.md:1: one\nb.txt:3: two\n", f"file contains {text!r}"

            def test_save_results_empty_writes_no_matches():
                count = save_results([], "empty_hits.txt")
                assert count == 0, f"returned {count!r}"
                text = Path("empty_hits.txt").read_text(encoding="utf-8")
                assert text == "no matches\n", f"file contains {text!r}"

            def test_save_results_replaces_existing_file_and_keeps_unicode():
                Path("again.txt").write_text("old content\nold\nold\n", encoding="utf-8")
                save_results(["menu.md:1: crème brûlée"], "again.txt")
                text = Path("again.txt").read_text(encoding="utf-8")
                assert text == "menu.md:1: crème brûlée\n", f"file contains {text!r}"
        ''',
    },
    # ---------------------------------------------------------------------- env
    {
        "id": "mini-env",
        "chapter": "env",
        "title": "Config Doctor",
        "estimated_hours": 1,
        "main": "doctor.py",
        "files": ["doctor.py"],
        "brief": r'''
            "It works on my machine" is usually a config problem: a missing API key, a typo in
            `.env`, a variable set in one terminal but not another. Build a **config doctor**: it
            reads a `.env` file, works out where every setting comes from (real environment,
            `.env` or a default), hides secrets and prints a neat checkup report.

            ## What to build

            A file `doctor.py` with five functions:

            **`read_dotenv(path=".env")`**
            - **Returns:** a dict of the settings in the file, e.g. `{"LLM_MODEL": "gpt-4o"}`

            **`resolve(name, dotenv, default=None)`**
            - `name`: a variable name; `dotenv`: a dict from `read_dotenv`; `default`: a string or `None`
            - **Returns:** a tuple `(value, source)` where source is `"env"`, `".env"`, `"default"` or
              `"missing"` (then value is `None`)

            **`is_secret(name)`**
            - **Returns:** `True` if the name looks like a secret, else `False`

            **`mask(value)`**
            - **Returns:** a hidden version of a secret value, a string

            **`doctor(schema, path=".env")`**
            - `schema`: a dict name -> default value (a string), or `None` for "required, no default",
              e.g. `{"LLM_MODEL": "gpt-4o-mini", "OPENAI_API_KEY": None}`
            - **Returns:** a list of report lines, one per name, in the schema's order

            ## Rules
            - `read_dotenv`: if the file doesn't exist, return `{}`. Skip blank lines, lines starting
              with `#`, and lines without `=`. Remove an optional `export ` at the start. Split on the
              **first** `=`; strip the key and the value. If the value is wrapped in matching quotes
              (`"..."` or `'...'`), remove them. An empty value (`EMPTY=`) is kept as `""`.
            - `read_dotenv` also expands references to environment variables inside values:
              `DATA_DIR=$APP_HOME/data` or `${APP_HOME}/data` uses the real environment's `APP_HOME`.
              A reference to a variable that isn't set is left exactly as written.
            - `resolve` precedence: real environment (`os.environ`) first, then the `dotenv` dict, then
              `default`. A value that is empty or only spaces counts as **not set** (in both places).
            - `is_secret`: the name ends with `_KEY`, `_TOKEN`, `_SECRET` or `_PASSWORD`, ignoring
              upper/lower case.
            - `mask`: values longer than 8 characters become `****` + their last 4 characters; shorter
              ones (8 or fewer) become just `****`.
            - `doctor` line format, where the name is padded with spaces on the right to the length
              of the **longest name in the schema**:
              - found: `OK   NAME = value (source)` - secret values are masked
              - not found: `FAIL NAME = (missing)`
              (`OK` is followed by 3 spaces, `FAIL` by 1, so names line up.) An empty schema returns `[]`.
            - Never change `os.environ`.

            ## Examples

            With `APP_HOME=/srv/bot` and `LLM_MODEL=o3-mini` set in the environment, and this `.env`:
            ```
            # local settings
            export LLM_MODEL="gpt-4o"
            OPENAI_API_KEY='sk-test-1234567890abcd'
            DATA_DIR=$APP_HOME/data
            ```
            ```python
            read_dotenv()
            # {"LLM_MODEL": "gpt-4o", "OPENAI_API_KEY": "sk-test-1234567890abcd", "DATA_DIR": "/srv/bot/data"}
            read_dotenv("missing.env")                    # {}
            resolve("LLM_MODEL", read_dotenv())           # ("o3-mini", "env")
            resolve("MAX_TOKENS", {}, "256")              # ("256", "default")
            resolve("SLACK_TOKEN", {})                    # (None, "missing")
            is_secret("openai_api_key")                   # True
            mask("sk-test-1234567890abcd")                # "****abcd"
            mask("short")                                 # "****"

            doctor({"LLM_MODEL": "gpt-4o-mini", "OPENAI_API_KEY": None, "DATA_DIR": None,
                    "MAX_TOKENS": "256", "SLACK_TOKEN": None})
            # ["OK   LLM_MODEL      = o3-mini (env)",
            #  "OK   OPENAI_API_KEY = ****abcd (.env)",
            #  "OK   DATA_DIR       = /srv/bot/data (.env)",
            #  "OK   MAX_TOKENS     = 256 (default)",
            #  "FAIL SLACK_TOKEN    = (missing)"]
            ```

            ## You'll need to find out
            - how to expand `$NAME` / `${NAME}` references in a string using the environment (the
              `os` module has a helper for exactly this)
            - how to pad a string to a width that is stored in a **variable** inside an f-string

            ## Try it yourself
            ```python
            from doctor import doctor
            for line in doctor({"HOME": None, "EDITOR": "nano", "GITHUB_TOKEN": None}):
                print(line)
            ```
        ''',
        "explore": r'''
            - Add types to the schema (`int`, `bool`) and report `FAIL MAX_TOKENS = not a number`.
            - Warn when a secret is found in `.env` but `.env` is not listed in `.gitignore`.
            - After the scripts chapter: `python3 doctor.py` that exits with code 1 when anything FAILs.
        ''',
        "rubric": [
            "Precedence (env > .env > default) is implemented in exactly one place",
            "Secrets can never reach the report unmasked",
            "The .env parser handles comments, export and quotes without special-casing each example",
            "os.environ is only read, never written",
        ],
        "starter_files": {"doctor.py": r'''
            """Check where every config value comes from."""

            import os


            def read_dotenv(path=".env"):
                ...


            def resolve(name, dotenv, default=None):
                ...


            def is_secret(name):
                ...


            def mask(value):
                ...


            def doctor(schema, path=".env"):
                ...
        '''},
        "solution_files": {"doctor.py": r'''
            """Check where every config value comes from."""

            import os

            SECRET_ENDINGS = ("_KEY", "_TOKEN", "_SECRET", "_PASSWORD")


            def read_dotenv(path=".env"):
                try:
                    with open(path, encoding="utf-8") as fh:
                        lines = fh.read().splitlines()
                except FileNotFoundError:
                    return {}
                values = {}
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    if line.startswith("export "):
                        line = line[len("export "):]
                    key, value = line.split("=", 1)
                    value = value.strip()
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                        value = value[1:-1]
                    values[key.strip()] = os.path.expandvars(value)
                return values


            def resolve(name, dotenv, default=None):
                env_value = os.environ.get(name, "")
                if env_value.strip():
                    return env_value, "env"
                file_value = dotenv.get(name, "")
                if file_value.strip():
                    return file_value, ".env"
                if default is not None:
                    return default, "default"
                return None, "missing"


            def is_secret(name):
                return name.upper().endswith(SECRET_ENDINGS)


            def mask(value):
                return "****" + value[-4:] if len(value) > 8 else "****"


            def doctor(schema, path=".env"):
                if not schema:
                    return []
                dotenv = read_dotenv(path)
                width = max(len(name) for name in schema)
                lines = []
                for name, default in schema.items():
                    value, source = resolve(name, dotenv, default)
                    if source == "missing":
                        lines.append(f"FAIL {name:<{width}} = (missing)")
                    else:
                        shown = mask(value) if is_secret(name) else value
                        lines.append(f"OK   {name:<{width}} = {shown} ({source})")
                return lines
        '''},
        "tests": r'''
            import os
            from doctor import read_dotenv, resolve, is_secret, mask, doctor

            DOTENV = ("# local settings\n\nexport LLM_MODEL=\"gpt-4o\"\n"
                      "OPENAI_API_KEY='sk-test-1234567890abcd'\n"
                      "DATA_DIR=$APP_HOME/data\n"
                      "  CACHE = ${APP_HOME}/cache  \n"
                      "URL=https://x.io/?a=1&b=2\n"
                      "not a setting\n"
                      "EMPTY=\n")
            NAMES = ("APP_HOME", "LLM_MODEL", "OPENAI_API_KEY", "DATA_DIR", "MAX_TOKENS", "SLACK_TOKEN", "EMPTY")

            def write_env(path=".env", text=DOTENV):
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(text)
                return path

            def with_env(values, fn):
                saved = {n: os.environ.pop(n, None) for n in NAMES}
                try:
                    os.environ.update(values)
                    return fn()
                finally:
                    for n in NAMES:
                        os.environ.pop(n, None)
                        if saved[n] is not None:
                            os.environ[n] = saved[n]

            def test_read_dotenv_parses_comments_export_and_quotes():
                write_env("a.env")
                got = with_env({}, lambda: read_dotenv("a.env"))
                assert got["LLM_MODEL"] == "gpt-4o", f"got {got!r}"
                assert got["OPENAI_API_KEY"] == "sk-test-1234567890abcd", f"got {got!r}"
                assert got["URL"] == "https://x.io/?a=1&b=2", "split on the FIRST = only"
                assert got["EMPTY"] == "", f"got {got!r}"
                assert "not a setting" not in got and len(got) == 6, f"got keys {sorted(got)!r}"

            def test_read_dotenv_missing_file_returns_empty_dict():
                assert read_dotenv("nope.env") == {}, f"got {read_dotenv('nope.env')!r}"

            def test_read_dotenv_expands_environment_references():
                write_env("b.env")
                got = with_env({"APP_HOME": "/srv/bot"}, lambda: read_dotenv("b.env"))
                assert got["DATA_DIR"] == "/srv/bot/data", f"got {got['DATA_DIR']!r}"
                assert got["CACHE"] == "/srv/bot/cache", f"got {got['CACHE']!r}"

            def test_unknown_references_are_left_as_written():
                write_env("c.env")
                got = with_env({}, lambda: read_dotenv("c.env"))
                assert got["DATA_DIR"] == "$APP_HOME/data", f"got {got['DATA_DIR']!r}"

            def test_resolve_precedence_env_then_dotenv_then_default():
                dotenv = {"LLM_MODEL": "gpt-4o"}
                got = with_env({"LLM_MODEL": "o3-mini"}, lambda: resolve("LLM_MODEL", dotenv, "x"))
                assert got == ("o3-mini", "env"), f"got {got!r}"
                got = with_env({}, lambda: resolve("LLM_MODEL", dotenv, "x"))
                assert got == ("gpt-4o", ".env"), f"got {got!r}"
                got = with_env({}, lambda: resolve("MAX_TOKENS", dotenv, "256"))
                assert got == ("256", "default"), f"got {got!r}"
                got = with_env({}, lambda: resolve("SLACK_TOKEN", dotenv))
                assert got == (None, "missing"), f"got {got!r}"

            def test_resolve_blank_values_count_as_not_set():
                got = with_env({"LLM_MODEL": "   "}, lambda: resolve("LLM_MODEL", {"LLM_MODEL": "gpt-4o"}))
                assert got == ("gpt-4o", ".env"), f"blank env value: got {got!r}"
                got = with_env({}, lambda: resolve("EMPTY", {"EMPTY": ""}, "d"))
                assert got == ("d", "default"), f"blank .env value: got {got!r}"

            def test_is_secret_checks_name_endings_any_case():
                for name in ("OPENAI_API_KEY", "slack_token", "Db_Password", "JWT_SECRET"):
                    assert is_secret(name) is True, f"{name} should be a secret"
                for name in ("LLM_MODEL", "KEYBOARD", "TOKEN_LIMIT", "DATA_DIR"):
                    assert is_secret(name) is False, f"{name} should not be a secret"

            def test_mask_shows_only_last_four_characters():
                assert mask("sk-test-1234567890abcd") == "****abcd", f"got {mask('sk-test-1234567890abcd')!r}"
                assert mask("123456789") == "****6789", f"got {mask('123456789')!r}"
                assert mask("12345678") == "****", f"got {mask('12345678')!r}"
                assert mask("") == "****", f"got {mask('')!r}"

            def test_doctor_report_lines_align_and_mask_secrets():
                write_env(".env")
                schema = {"LLM_MODEL": "gpt-4o-mini", "OPENAI_API_KEY": None, "DATA_DIR": None,
                          "MAX_TOKENS": "256", "SLACK_TOKEN": None}
                got = with_env({"APP_HOME": "/srv/bot", "LLM_MODEL": "o3-mini"}, lambda: doctor(schema))
                want = ["OK   LLM_MODEL      = o3-mini (env)",
                        "OK   OPENAI_API_KEY = ****abcd (.env)",
                        "OK   DATA_DIR       = /srv/bot/data (.env)",
                        "OK   MAX_TOKENS     = 256 (default)",
                        "FAIL SLACK_TOKEN    = (missing)"]
                assert got == want, "got:\n" + "\n".join(got)

            def test_doctor_uses_given_path_and_never_leaks_full_secret():
                write_env("other.env", "GITHUB_TOKEN=ghp_abcdefghijklmnop\n")
                got = with_env({}, lambda: doctor({"GITHUB_TOKEN": None, "X": "1"}, "other.env"))
                assert got == ["OK   GITHUB_TOKEN = ****mnop (.env)", "OK   X            = 1 (default)"], f"got {got!r}"
                assert "abcdefgh" not in "".join(got)

            def test_doctor_empty_schema_and_missing_file():
                assert with_env({}, lambda: doctor({}, "none.env")) == []
                got = with_env({}, lambda: doctor({"A": None}, "none.env"))
                assert got == ["FAIL A = (missing)"], f"got {got!r}"

            def test_doctor_does_not_change_os_environ():
                write_env(".env")
                def run():
                    before = dict(os.environ)
                    doctor({"LLM_MODEL": None, "OPENAI_API_KEY": None})
                    return before == dict(os.environ)
                assert with_env({}, run), "doctor changed os.environ"
        ''',
    },
    # ------------------------------------------------------------------ scripts
    {
        "id": "mini-scripts",
        "chapter": "scripts",
        "title": "Terminal Todo List",
        "estimated_hours": 1.25,
        "main": "todo.py",
        "files": ["todo.py"],
        "brief": r'''
            A to-do list you drive from the terminal, git-style: `python3 todo.py add "Buy milk"`,
            `python3 todo.py list`, `python3 todo.py done 1`. Tasks are saved in a JSON file, so
            they survive between runs. It's the same shape as every real CLI tool: commands,
            options, a data file, error messages on stderr and honest exit codes.

            ## What to build

            A script `todo.py` with four commands:

            ```
            python3 todo.py add TEXT [--priority {low,normal,high}]
            python3 todo.py list [--all]
            python3 todo.py done ID
            python3 todo.py clear
            ```

            Tasks live in a JSON file: the path in the environment variable `TODO_FILE`, or
            `todo.json` (in the current folder) if it's not set. The file holds a JSON **list** of
            tasks, each a dict with exactly these keys:
            `{"id": 1, "text": "Buy milk", "priority": "normal", "done": false}`.

            ## Rules
            - A missing data file means "no tasks yet" (no error). Save the whole list back after
              every change, with `indent=2`.
            - `add TEXT`: strip the text; the new task's `id` is the biggest existing id + 1 (or `1`
              when there are none), `done` is `false`, `priority` defaults to `normal`.
              Prints `added #ID: TEXT`.
            - `--priority` only accepts `low`, `normal` or `high`; anything else is a usage error
              (exit code `2`, argparse does this for you).
            - `add` with a blank text: print `error: empty task` to **stderr**, exit code `1`, save nothing.
            - `list`: prints the tasks that are not done, in id order, one per line:
              `#ID [ ] TEXT`. With `--all` it prints every task, done ones as `#ID [x] TEXT`.
              A task with priority `high` gets ` (high)` at the end of its line.
              If there is nothing to print, print `nothing to do`.
            - `done ID`: `ID` must be a whole number (argparse `type`). Marks that task done and
              prints `done #ID: TEXT`. If no task has that id: print `error: no task #ID` to
              **stderr**, print nothing on stdout, exit code `1`, change nothing.
            - `clear`: removes all done tasks and prints `removed N done tasks` (always "tasks").
            - Running `todo.py` with no command is a usage error: exit code `2`.
            - Every successful command exits with code `0`.
            - Put the program in a `main()` function and run it only under
              `if __name__ == "__main__":` - importing `todo.py` must not run anything.

            ## Examples

            ```
            $ python3 todo.py add "  Buy milk "
            added #1: Buy milk
            $ python3 todo.py add "Ship the RAG demo" --priority high
            added #2: Ship the RAG demo
            $ python3 todo.py done 1
            done #1: Buy milk
            $ python3 todo.py list
            #2 [ ] Ship the RAG demo (high)
            $ python3 todo.py list --all
            #1 [x] Buy milk
            #2 [ ] Ship the RAG demo (high)
            $ python3 todo.py done 7          # stderr: error: no task #7   (exit code 1)
            $ python3 todo.py clear
            removed 1 done tasks
            $ python3 todo.py add "x" --priority urgent     # usage error, exit code 2
            $ TODO_FILE=work.json python3 todo.py list
            nothing to do
            ```

            After those commands `todo.json` contains:
            ```json
            [
              {
                "id": 2,
                "text": "Ship the RAG demo",
                "priority": "high",
                "done": false
              }
            ]
            ```

            ## You'll need to find out
            - how to make argparse understand **sub-commands** (like `git add` / `git commit`), each
              with its own arguments, and how to make choosing a sub-command required

            ## Try it yourself
            ```bash
            python3 todo.py add "Read the argparse tutorial" --priority high
            python3 todo.py list --all
            cat todo.json
            ```
        ''',
        "explore": r'''
            - Add `todo.py edit ID NEW_TEXT` and `todo.py undo ID`.
            - Sort `list` output by priority (high first) after the sorting chapter.
            - Add a `--json` flag to `list` that prints the tasks as JSON, so other scripts can use it.
        ''',
        "rubric": [
            "Loading and saving the task file each live in one small function",
            "Each sub-command is handled by its own small function (or a clear branch), not one giant block",
            "Errors go to stderr with a non-zero exit code; normal output goes to stdout",
            "The script is importable: all work happens inside main() under the main guard",
        ],
        "starter_files": {"todo.py": r'''
            """A tiny to-do list for the terminal."""

            import argparse
            import json
            import os
            import sys


            def main():
                ...


            if __name__ == "__main__":
                sys.exit(main())
        '''},
        "solution_files": {"todo.py": r'''
            """A tiny to-do list for the terminal."""

            import argparse
            import json
            import os
            import sys


            def data_path():
                return os.environ.get("TODO_FILE", "todo.json")


            def load_tasks():
                try:
                    with open(data_path(), encoding="utf-8") as fh:
                        return json.load(fh)
                except FileNotFoundError:
                    return []


            def save_tasks(tasks):
                with open(data_path(), "w", encoding="utf-8") as fh:
                    json.dump(tasks, fh, indent=2)


            def build_parser():
                parser = argparse.ArgumentParser(prog="todo", description="A tiny to-do list.")
                commands = parser.add_subparsers(dest="command", required=True)
                add = commands.add_parser("add", help="add a task")
                add.add_argument("text")
                add.add_argument("--priority", choices=["low", "normal", "high"], default="normal")
                show = commands.add_parser("list", help="show tasks")
                show.add_argument("--all", action="store_true")
                done = commands.add_parser("done", help="mark a task done")
                done.add_argument("id", type=int)
                commands.add_parser("clear", help="remove done tasks")
                return parser


            def cmd_add(tasks, args):
                text = args.text.strip()
                if not text:
                    print("error: empty task", file=sys.stderr)
                    return 1
                new_id = max([t["id"] for t in tasks], default=0) + 1
                tasks.append({"id": new_id, "text": text, "priority": args.priority, "done": False})
                save_tasks(tasks)
                print(f"added #{new_id}: {text}")
                return 0


            def cmd_list(tasks, args):
                shown = [t for t in tasks if args.all or not t["done"]]
                if not shown:
                    print("nothing to do")
                for t in shown:
                    mark = "x" if t["done"] else " "
                    extra = " (high)" if t["priority"] == "high" else ""
                    print(f"#{t['id']} [{mark}] {t['text']}{extra}")
                return 0


            def cmd_done(tasks, args):
                for t in tasks:
                    if t["id"] == args.id:
                        t["done"] = True
                        save_tasks(tasks)
                        print(f"done #{t['id']}: {t['text']}")
                        return 0
                print(f"error: no task #{args.id}", file=sys.stderr)
                return 1


            def cmd_clear(tasks, args):
                keep = [t for t in tasks if not t["done"]]
                save_tasks(keep)
                print(f"removed {len(tasks) - len(keep)} done tasks")
                return 0


            COMMANDS = {"add": cmd_add, "list": cmd_list, "done": cmd_done, "clear": cmd_clear}


            def main(argv=None):
                args = build_parser().parse_args(argv)
                return COMMANDS[args.command](load_tasks(), args)


            if __name__ == "__main__":
                sys.exit(main())
        '''},
        "tests": r'''
            import json
            import os

            def todo(file, *args):
                return run_script(args=list(args), env={"TODO_FILE": file})

            def saved(file):
                with open(file, encoding="utf-8") as fh:
                    return json.load(fh)

            def test_add_creates_the_file_and_prints_the_new_task():
                r = todo("t_add.json", "add", "  Buy milk ")
                assert r.returncode == 0, f"exit code {r.returncode}, stderr {r.stderr[-300:]!r}"
                assert r.stdout.strip() == "added #1: Buy milk", f"stdout {r.stdout!r}"
                assert saved("t_add.json") == [{"id": 1, "text": "Buy milk", "priority": "normal", "done": False}], \
                    f"file holds {saved('t_add.json')!r}"

            def test_ids_count_up_from_the_biggest_existing_id():
                with open("t_ids.json", "w", encoding="utf-8") as fh:
                    json.dump([{"id": 4, "text": "old", "priority": "low", "done": True}], fh)
                r = todo("t_ids.json", "add", "next one")
                assert r.stdout.strip() == "added #5: next one", f"stdout {r.stdout!r}"
                assert [t["id"] for t in saved("t_ids.json")] == [4, 5]

            def test_priority_is_saved_and_high_is_flagged_in_list():
                todo("t_prio.json", "add", "Ship the demo", "--priority", "high")
                todo("t_prio.json", "add", "Nap", "--priority", "low")
                assert [t["priority"] for t in saved("t_prio.json")] == ["high", "low"]
                r = todo("t_prio.json", "list")
                assert r.stdout.strip().splitlines() == ["#1 [ ] Ship the demo (high)", "#2 [ ] Nap"], f"stdout {r.stdout!r}"

            def test_invalid_priority_is_a_usage_error():
                r = todo("t_badprio.json", "add", "x", "--priority", "urgent")
                assert r.returncode == 2, f"exit code {r.returncode}"
                assert not os.path.exists("t_badprio.json"), "nothing should be saved"

            def test_blank_task_is_an_error_on_stderr():
                r = todo("t_blank.json", "add", "   ")
                assert r.returncode == 1, f"exit code {r.returncode}"
                assert "error: empty task" in r.stderr, f"stderr {r.stderr!r}"
                assert r.stdout == "", f"stdout {r.stdout!r}"
                assert not os.path.exists("t_blank.json"), "nothing should be saved"

            def test_list_with_no_tasks_says_nothing_to_do():
                r = todo("t_empty.json", "list")
                assert r.returncode == 0, f"exit code {r.returncode}, stderr {r.stderr[-300:]!r}"
                assert r.stdout.strip() == "nothing to do", f"stdout {r.stdout!r}"

            def test_done_marks_the_task_and_list_hides_it():
                todo("t_done.json", "add", "Buy milk")
                todo("t_done.json", "add", "Write tests")
                r = todo("t_done.json", "done", "1")
                assert r.returncode == 0, f"exit code {r.returncode}, stderr {r.stderr[-300:]!r}"
                assert r.stdout.strip() == "done #1: Buy milk", f"stdout {r.stdout!r}"
                assert [t["done"] for t in saved("t_done.json")] == [True, False]
                r = todo("t_done.json", "list")
                assert r.stdout.strip().splitlines() == ["#2 [ ] Write tests"], f"stdout {r.stdout!r}"

            def test_list_all_shows_done_tasks_with_x():
                todo("t_all.json", "add", "Buy milk")
                todo("t_all.json", "add", "Write tests")
                todo("t_all.json", "done", "1")
                r = todo("t_all.json", "list", "--all")
                assert r.stdout.strip().splitlines() == ["#1 [x] Buy milk", "#2 [ ] Write tests"], f"stdout {r.stdout!r}"
                todo("t_all.json", "done", "2")
                r = todo("t_all.json", "list")
                assert r.stdout.strip() == "nothing to do", f"stdout {r.stdout!r}"

            def test_done_unknown_id_is_an_error_and_changes_nothing():
                todo("t_unknown.json", "add", "Buy milk")
                before = saved("t_unknown.json")
                r = todo("t_unknown.json", "done", "7")
                assert r.returncode == 1, f"exit code {r.returncode}"
                assert "error: no task #7" in r.stderr, f"stderr {r.stderr!r}"
                assert r.stdout == "", f"stdout {r.stdout!r}"
                assert saved("t_unknown.json") == before, "the file changed"

            def test_done_needs_a_number():
                r = todo("t_nan.json", "done", "first")
                assert r.returncode == 2, f"exit code {r.returncode}"

            def test_clear_removes_done_tasks():
                for text in ("a", "b", "c"):
                    todo("t_clear.json", "add", text)
                todo("t_clear.json", "done", "1")
                todo("t_clear.json", "done", "3")
                r = todo("t_clear.json", "clear")
                assert r.stdout.strip() == "removed 2 done tasks", f"stdout {r.stdout!r}"
                assert saved("t_clear.json") == [{"id": 2, "text": "b", "priority": "normal", "done": False}]

            def test_no_command_is_a_usage_error():
                r = todo("t_nocmd.json")
                assert r.returncode == 2, f"exit code {r.returncode}"

            def test_default_file_is_todo_json():
                r = run_script(args=["add", "default file"])
                assert r.returncode == 0, f"exit code {r.returncode}, stderr {r.stderr[-300:]!r}"
                assert saved("todo.json")[0]["text"] == "default file", "expected the task in todo.json"

            def test_importing_does_not_run_the_program():
                with open("imp.py", "w") as fh:
                    fh.write("import todo\nprint('imported')\n")
                r = run_script(file="imp.py")
                assert r.returncode == 0 and r.stdout.strip() == "imported", f"importing ran the program: {r!r}"
        ''',
    },
    # ------------------------------------------------------------------ sorting
    {
        "id": "mini-sorting",
        "chapter": "sorting",
        "title": "Arcade Leaderboard",
        "estimated_hours": 0.75,
        "main": "leaderboard.py",
        "files": ["leaderboard.py"],
        "brief": r'''
            Every game needs a leaderboard, and every leaderboard has the same hard parts: tie
            breaks, shared places ("joint 2nd"), a nicely aligned table and a "most improved"
            award. Build the ranking engine for an arcade game.

            A **player** is a dict like `{"name": "ada", "score": 1200, "time": 31.5}` (time in
            seconds - faster is better).

            ## What to build

            A file `leaderboard.py` with five functions:

            **`rank(players)`**
            - `players`: a list of player dicts
            - **Returns:** a new list of new dicts, best first, each a copy of the player plus a
              `"rank"` key (an int)

            **`top(players, n=3)`**
            - **Returns:** a list of the names of the best `n` players, best first

            **`format_board(players, n=10)`**
            - **Returns:** a string: the table of the best `n` players, one line each

            **`most_improved(before, after)`**
            - `before`, `after`: two lists of player dicts (last week's and this week's scores)
            - **Returns:** the name of the player whose score went up the most, or `None`

            **`stats(players)`**
            - **Returns:** a dict `{"players": <count>, "top_score": <highest score>, "median_time": <median time>}`

            ## Rules
            - Order: higher `score` first; on equal scores, lower `time` first; if both are equal,
              by `name` A-Z **ignoring upper/lower case**.
            - Ranks use *competition ranking*: players with the same score **and** the same time
              share a rank, and the next rank skips (1, 2, 2, 4). Players with the same score but
              different times get different ranks.
            - Don't change the `players` list or its dicts.
            - `format_board` line format: rank right-aligned in 2 characters, `. `, the name
              left-aligned in 10 characters, one space, the score right-aligned in 7 characters
              **with a thousands separator**, two spaces, the time with 1 decimal and `s`. Lines are joined
              with `\n` (no newline at the end). No players: return `"no players yet"`.
            - `most_improved`: only names that appear in both lists count; the improvement is
              `after score - before score`. Only improvements above 0 count; if there are none (or
              no common names), return `None`. On a tie, the name that comes first A-Z (ignoring case).
            - `stats`: `median_time` is the middle time when sorted (the average of the two middle
              ones for an even count). With no players, return
              `{"players": 0, "top_score": None, "median_time": None}`.

            ## Examples
            ```python
            players = [
                {"name": "ada", "score": 1200, "time": 31.5},
                {"name": "Bob", "score": 950, "time": 28.0},
                {"name": "cy", "score": 1200, "time": 29.9},
                {"name": "amy", "score": 950, "time": 28.0},
                {"name": "eve", "score": 12500, "time": 60.4},
            ]
            [(p["rank"], p["name"]) for p in rank(players)]
            # [(1, "eve"), (2, "cy"), (3, "ada"), (4, "amy"), (4, "Bob")]
            top(players, 2)            # ["eve", "cy"]
            print(format_board(players, 3))
            #  1. eve         12,500  60.4s
            #  2. cy           1,200  29.9s
            #  3. ada          1,200  31.5s
            format_board([])           # "no players yet"

            last_week = [{"name": "ada", "score": 700, "time": 40.0},
                         {"name": "cy", "score": 1100, "time": 30.0},
                         {"name": "zed", "score": 50, "time": 99.0}]
            most_improved(last_week, players)   # "ada"   (+500, cy only +100, zed isn't in this week)
            most_improved(players, players)     # None    (nobody improved)
            stats(players)   # {"players": 5, "top_score": 12500, "median_time": 29.9}
            ```

            ## You'll need to find out
            - a standard-library function that computes the **median** of a list of numbers

            ## Try it yourself
            ```python
            from leaderboard import format_board
            print(format_board([{"name": "you", "score": 99999, "time": 12.3},
                                {"name": "me", "score": 99999, "time": 12.3}]))
            ```
        ''',
        "explore": r'''
            - Add a `--by time` mode for speed-runs: fastest first, score only breaks ties.
            - Show movement arrows by comparing this week's ranks with last week's (`▲2`, `▼1`, `=`).
            - Store the scores in a JSON file and make it a CLI: `python3 leaderboard.py add ada 1200 31.5`.
        ''',
        "rubric": [
            "Ordering is done with sorted() and a clear key function (tuple key), not a hand-written sort",
            "Ranking logic for ties is short and easy to follow",
            "min/max with key and default= (or equivalent) are used for the award and stats",
            "Input players are never mutated",
        ],
        "starter_files": {"leaderboard.py": r'''
            """Rank players for an arcade leaderboard."""


            def rank(players):
                ...


            def top(players, n=3):
                ...


            def format_board(players, n=10):
                ...


            def most_improved(before, after):
                ...


            def stats(players):
                ...
        '''},
        "solution_files": {"leaderboard.py": r'''
            """Rank players for an arcade leaderboard."""

            import statistics


            def sort_key(player):
                return (-player["score"], player["time"], player["name"].lower())


            def rank(players):
                ranked = []
                for position, player in enumerate(sorted(players, key=sort_key), start=1):
                    entry = dict(player)
                    prev = ranked[-1] if ranked else None
                    same = prev and (prev["score"], prev["time"]) == (player["score"], player["time"])
                    entry["rank"] = prev["rank"] if same else position
                    ranked.append(entry)
                return ranked


            def top(players, n=3):
                return [p["name"] for p in rank(players)[:n]]


            def format_board(players, n=10):
                if not players:
                    return "no players yet"
                return "\n".join(f"{p['rank']:>2}. {p['name']:<10} {p['score']:>7,}  {p['time']:.1f}s"
                                 for p in rank(players)[:n])


            def most_improved(before, after):
                old = {p["name"]: p["score"] for p in before}
                gains = {p["name"]: p["score"] - old[p["name"]] for p in after if p["name"] in old}
                improved = [name for name, gain in gains.items() if gain > 0]
                return min(improved, key=lambda name: (-gains[name], name.lower()), default=None)


            def stats(players):
                if not players:
                    return {"players": 0, "top_score": None, "median_time": None}
                return {"players": len(players),
                        "top_score": max(p["score"] for p in players),
                        "median_time": statistics.median(p["time"] for p in players)}
        '''},
        "tests": r'''
            import copy
            from leaderboard import rank, top, format_board, most_improved, stats

            PLAYERS = [
                {"name": "ada", "score": 1200, "time": 31.5},
                {"name": "Bob", "score": 950, "time": 28.0},
                {"name": "cy", "score": 1200, "time": 29.9},
                {"name": "amy", "score": 950, "time": 28.0},
                {"name": "eve", "score": 12500, "time": 60.4},
            ]

            def test_rank_orders_by_score_then_time_then_name():
                got = [p["name"] for p in rank(PLAYERS)]
                assert got == ["eve", "cy", "ada", "amy", "Bob"], f"got {got!r}"

            def test_name_tie_break_ignores_case():
                players = [{"name": "Zoe", "score": 5, "time": 1.0}, {"name": "bea", "score": 5, "time": 1.0},
                           {"name": "Al", "score": 5, "time": 1.0}]
                got = [p["name"] for p in rank(players)]
                assert got == ["Al", "bea", "Zoe"], f"got {got!r}"

            def test_competition_ranking_shares_places_and_skips():
                got = [(p["rank"], p["name"]) for p in rank(PLAYERS)]
                assert got == [(1, "eve"), (2, "cy"), (3, "ada"), (4, "amy"), (4, "Bob")], f"got {got!r}"
                more = PLAYERS + [{"name": "dan", "score": 100, "time": 5.0}]
                got = [p["rank"] for p in rank(more)]
                assert got == [1, 2, 3, 4, 4, 6], f"got {got!r}"

            def test_rank_returns_copies_and_does_not_change_input():
                before = copy.deepcopy(PLAYERS)
                got = rank(PLAYERS)
                assert PLAYERS == before, "rank changed the input list or its dicts"
                assert got[0] == {"name": "eve", "score": 12500, "time": 60.4, "rank": 1}, f"got {got[0]!r}"
                assert rank([]) == [], f"got {rank([])!r}"

            def test_top_returns_best_names():
                assert top(PLAYERS, 2) == ["eve", "cy"], f"got {top(PLAYERS, 2)!r}"
                assert top(PLAYERS) == ["eve", "cy", "ada"], f"got {top(PLAYERS)!r}"
                assert top(PLAYERS, 50) == ["eve", "cy", "ada", "amy", "Bob"], f"got {top(PLAYERS, 50)!r}"

            def test_format_board_aligns_columns():
                got = format_board(PLAYERS, 3)
                want = " 1. eve         12,500  60.4s\n 2. cy           1,200  29.9s\n 3. ada          1,200  31.5s"
                assert got == want, "got:\n" + got + "\nexpected:\n" + want

            def test_format_board_default_shows_up_to_ten_and_shared_ranks():
                got = format_board(PLAYERS).splitlines()
                assert len(got) == 5, f"got {got!r}"
                assert got[3] == " 4. amy            950  28.0s", f"got {got[3]!r}"
                assert got[4] == " 4. Bob            950  28.0s", f"got {got[4]!r}"

            def test_format_board_with_no_players():
                assert format_board([]) == "no players yet", f"got {format_board([])!r}"

            def test_most_improved_picks_biggest_gain_among_common_names():
                last_week = [{"name": "ada", "score": 700, "time": 40.0},
                             {"name": "cy", "score": 1100, "time": 30.0},
                             {"name": "zed", "score": 50, "time": 99.0}]
                got = most_improved(last_week, PLAYERS)
                assert got == "ada", f"got {got!r}"

            def test_most_improved_tie_goes_to_first_name_ignoring_case():
                before = [{"name": "Zed", "score": 1, "time": 1.0}, {"name": "bo", "score": 1, "time": 1.0}]
                after = [{"name": "Zed", "score": 11, "time": 1.0}, {"name": "bo", "score": 11, "time": 1.0}]
                got = most_improved(before, after)
                assert got == "bo", f"got {got!r}"

            def test_most_improved_none_when_nobody_improved():
                assert most_improved(PLAYERS, PLAYERS) is None
                assert most_improved([], PLAYERS) is None
                worse = [{"name": "ada", "score": 5, "time": 1.0}]
                assert most_improved(PLAYERS, worse) is None

            def test_stats_counts_top_score_and_median_time():
                got = stats(PLAYERS)
                assert got == {"players": 5, "top_score": 12500, "median_time": 29.9}, f"got {got!r}"
                got = stats(PLAYERS[:2])
                assert got == {"players": 2, "top_score": 1200, "median_time": 29.75}, f"even count: got {got!r}"

            def test_stats_with_no_players():
                got = stats([])
                assert got == {"players": 0, "top_score": None, "median_time": None}, f"got {got!r}"
        ''',
    },
]
