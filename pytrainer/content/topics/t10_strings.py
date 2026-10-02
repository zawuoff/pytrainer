TOPIC = {
    "id": "strings",
    "title": "Strings & Text Processing",
    "track": "working-python",
    "order": 1,
    "requires": ["fstrings", "loops"],
    "summary": """
        Cleaning, splitting, joining, searching and slicing text - the daily work of
        preparing prompts and post-processing model output.
    """,
    "concepts": ["split", "join", "strip", "replace", "case methods", "startswith/endswith",
                 "find / in", "string slicing", "whitespace normalisation", "word counting",
                 "truncation"],
}

LESSON = r'''
## Chapter notes: Strings & Text Processing

**Basics**
- A string is a sequence of characters: `len(s)`, `s[0]`, `s[-1]`, `s[:5]`, `s[7:]`.
- Strings are *immutable*: methods return a **new** string. Store it:
  `text = text.strip()`.
- Methods are called with a dot and can be *chained*: `raw.strip().lower()`.

**Cleaning**
| call | result |
| --- | --- |
| `"  Hi \n".strip()` | `"Hi"` (whitespace removed at both ends only) |
| `"Hi".lower()` / `.upper()` | `"hi"` / `"HI"` |
| `"a-b-a".replace("a", "x")` | `"x-b-x"` (every occurrence) |

**Splitting and joining**
- `"a  b\tc".split()` gives `['a', 'b', 'c']`: any whitespace, no empty pieces.
- `"a,b,,c".split(",")` gives `['a', 'b', '', 'c']`: exact separator.
- `"hf/meta/llama".split("/", 1)` gives `['hf', 'meta/llama']` (*maxsplit*).
- `" ".join(words)`: the separator comes first and goes only between items.
- `" ".join(text.split())` collapses every run of whitespace to one space
  (*whitespace normalisation*).
- `text.splitlines()` gives the lines without `\n`; `"\n".join(lines)` rebuilds.

**Searching**
- `"key" in text`: anywhere? `text.startswith("Sure")`, `text.endswith(".md")`: edges.
- `text.find("42")`: position, or `-1` if missing. `text.count("e")`: occurrences.
- All checks are case-sensitive: compare `word.lower() in text.lower()`.

**Gotchas**
- `text.strip()` alone on a line does nothing useful - the result is thrown away.
- `words.join(" ")` is wrong; `" ".join(words)` is right.
- `"a  b".split(" ")` gives `['a', '', 'b']`; use `split()` for words.
- Unpacking `a, b = s.split("/", 1)` fails if there is no `/`: check with `in` first.
- An empty string is *falsy*: `if line.strip():` skips blank lines.
'''

EXERCISES = [
    {
        "id": "strings-s1",
        "title": "Method chain",
        "difficulty": 0,
        "lesson": r'''
            ## Text is a row of letter tiles

            Picture a string as a row of Scrabble tiles: `"Hello"` is five tiles side by side.
            Prompts, documents, model replies - they are all rows of tiles. Like a list, you
            can count the tiles, pick one, or take a slice.

            ```python
            word = "Hello"
            print(len(word))     # 5 tiles
            print(word[0], word[-1])
            print(word[:3])
            ```

            Strings also come with built-in tools you call with a dot: `text.lower()`,
            `text.strip()`, `text.split()`. Those tools are called *methods*: functions that
            belong to a value.

            ```python
            text = "  Hi There  "
            print(text.lower())
            print(text.startswith("Hi"))
            ```

            One big rule: a string **never changes**. A method always hands back a **new**
            string and leaves the original alone. The proper word is *immutable*.

            **Watch out:** in the second example, `text` still starts with two spaces, so
            `startswith("Hi")` is `False`.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            text = "  Hello World  "
            clean = text.strip()
            print(clean.lower())
            print(len(clean))
            print(clean.split())
            print(text.startswith("Hello"))
        ''',
        "solution": r'''
            hello world
            11
            ['Hello', 'World']
            False
        ''',
        "explanation": r'''
            `strip()` removes the outer spaces, giving `"Hello World"` (11 characters).
            `lower()` returns a lower-case copy. `split()` breaks it into a list of words.
            The last line checks the **original** `text`, which still starts with spaces,
            so `startswith("Hello")` is `False`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Work out what `clean` holds first. Then evaluate each print one at a time.",
            "strip only removes spaces at the ends, not the one in the middle. The last line uses text, not clean.",
            "clean is \"Hello World\". Line 1: lower-case version. Line 2: count its characters including the middle space. Line 3: a list of two words. Line 4: does the unstripped text begin with Hello?",
        ],
    },
    {
        "id": "strings-s2",
        "title": "Tidy a user message",
        "difficulty": 0,
        "lesson": r'''
            ## Trimming the edges

            Text from users is like a photo with a messy border: stray spaces, a newline at the
            end, a tab at the start. `strip()` crops that border off. The middle of the
            picture is left alone.

            ```python
            raw = "\t  Summarise this document.  \n"
            print(repr(raw.strip()))
            print("  a  b  ".strip())
            ```

            (`repr` shows the string with its quotes, so you can see the spaces.)

            Case methods make every letter the same size:

            ```python
            title = "Hello World"
            print(title.lower())
            print(title.upper())
            ```

            You can *chain* methods: each one works on the result of the previous one,
            left to right: `raw.strip().lower()`.

            The spaces, tabs (`\t`) and newlines (`\n`) together are called *whitespace*.
            `strip()` removes all kinds of whitespace from both ends.

            **Watch out:** `strip()` never touches the space between two words.
        ''',
        "prompt": r'''
            User messages arrive with stray spaces and random capitals. Tidy them up.

            **Write:** `tidy(text)` - fill in the `___` in the starter.

            - `text`: a string, e.g. `"  Hello THERE \n"`
            - **Returns:** a new string with the whitespace (spaces, tabs, newlines) at
              both ends removed **and** every letter lower-case.

            **Rules**
            - Whitespace in the middle stays as it is.
            - Text that is already clean comes back unchanged.

            **Examples**
            ```python
            tidy("  Hello THERE \n")   # returns "hello there"
            tidy("ok")                 # returns "ok"
            ```
        ''',
        "starter": r'''
            def tidy(text):
                return text.___().lower()
        ''',
        "tests": r'''
            from solution import tidy

            def test_strips_outer_whitespace_and_lower_cases():
                got = tidy("  Hello THERE \n")
                assert got == "hello there", f"got {got!r}"

            def test_already_clean_text_unchanged():
                assert tidy("ok") == "ok"
        ''',
        "solution": r'''
            def tidy(text):
                return text.strip().lower()
        ''',
        "hints": [
            "You need the string method that removes whitespace from both ends.",
            "The lower-casing is already there. Only the whitespace-removing method name is missing.",
            "Replace ___ with strip.",
        ],
    },
    {
        "id": "strings-s3",
        "title": "Fix: the redaction does nothing",
        "difficulty": 0,
        "lesson": r'''
            ## Find and replace makes a new copy

            Imagine a printed page. You can't change the ink - but you can photocopy it with
            a correction. That's `replace`: it gives you a corrected **copy**; the original
            page stays as it was.

            ```python
            msg = "hello world, hello again"
            fixed = msg.replace("hello", "hi")
            print(fixed)
            print(msg)
            ```

            `replace(old, new)` swaps **every** occurrence of `old` for `new`. If `old` isn't
            there, you get back the same text.

            Because strings are *immutable* (they can't change), a line like
            `msg.replace("a", "b")` on its own does nothing useful: the new copy is thrown
            away. You have to keep it: `msg = msg.replace("a", "b")`.

            **Watch out:** this "forgot to store the result" bug is one of the most common
            string mistakes. It applies to `strip()`, `lower()` and every other string method too.
        ''',
        "prompt": r'''
            Before logging a prompt we hide API keys. The starter's `redact` has one bug:
            it returns the text unchanged.

            **Write:** fix `redact(text)`

            - `text`: a string, e.g. `"my key is sk-secret"`
            - **Returns:** a new string where every `"sk-secret"` is replaced by `"[KEY]"`.

            **Rules**
            - Replace **every** occurrence, not just the first.
            - Text without `"sk-secret"` comes back unchanged.

            **Examples**
            ```python
            redact("my key is sk-secret")       # returns "my key is [KEY]"
            redact("sk-secret and sk-secret")   # returns "[KEY] and [KEY]"
            redact("nothing here")              # returns "nothing here"
            ```
        ''',
        "starter": r'''
            def redact(text):
                text.replace("sk-secret", "[KEY]")
                return text
        ''',
        "tests": r'''
            from solution import redact

            def test_key_is_replaced_with_placeholder():
                got = redact("my key is sk-secret")
                assert got == "my key is [KEY]", f"got {got!r}"

            def test_every_occurrence_is_replaced():
                got = redact("sk-secret and sk-secret")
                assert got == "[KEY] and [KEY]", f"got {got!r}"

            def test_text_without_key_unchanged():
                assert redact("nothing here") == "nothing here"
        ''',
        "solution": r'''
            def redact(text):
                text = text.replace("sk-secret", "[KEY]")
                return text
        ''',
        "hints": [
            "Strings never change in place. What does replace() do with its result?",
            "replace returns a NEW string. The code throws that new string away and returns the old one.",
            "Store the result: assign text.replace(...) back to text (or return it directly).",
        ],
    },
    {
        "id": "strings-s4",
        "title": "Count the words",
        "difficulty": 0,
        "lesson": r'''
            ## Cutting text into words

            `split()` is a pair of scissors that cuts a string wherever there is whitespace,
            and hands you a **list** of the pieces.

            ```python
            line = "the  quick\tbrown\nfox"
            words = line.split()
            print(words)
            print(len(words))
            print("   ".split())
            ```

            With no argument, `split()` treats any run of spaces, tabs and newlines as one
            cut, and never gives you empty pieces. Blank text gives an empty list `[]`.

            You can also split on a specific separator, like a comma:

            ```python
            print("a,b,c".split(","))
            ```

            The pieces are often called *tokens* in everyday code (not quite the same as an
            LLM's tokens, but a rough word count is a common quick estimate).

            **Watch out:** `split(" ")` (with a space) cuts at every single space, so double
            spaces create empty strings: `"a  b".split(" ")` is `['a', '', 'b']`.
        ''',
        "prompt": r'''
            A rough word count is a quick way to estimate how long a document is.

            **Write:** `word_count(text)`

            - `text`: a string, e.g. `"the quick  brown\nfox"`
            - **Returns:** an `int`, the number of words in `text`.

            **Rules**
            - Words are separated by any amount of whitespace (spaces, tabs, newlines).
            - Extra spaces never count as words.
            - Text that is empty or only whitespace has `0` words.

            **Examples**
            ```python
            word_count("the quick  brown\nfox")   # returns 4
            word_count("hello")                   # returns 1
            word_count("   ")                     # returns 0
            ```
        ''',
        "starter": r'''
            def word_count(text):
                ...
        ''',
        "tests": r'''
            from solution import word_count

            def test_counts_words_across_spaces_and_newlines():
                got = word_count("the quick  brown\nfox")
                assert got == 4, f"got {got!r}"

            def test_blank_text_has_zero_words():
                got = word_count("   ")
                assert got == 0, f"got {got!r}"

            def test_single_word_counts_one():
                assert word_count("hello") == 1
        ''',
        "solution": r'''
            def word_count(text):
                return len(text.split())
        ''',
        "hints": [
            "One string method turns text into a list of words. Then count the list.",
            "split() with no argument splits on any whitespace and ignores extra spaces.",
            "Return len() of text.split().",
        ],
    },
    {
        "id": "strings-s5",
        "title": "Make a slug",
        "difficulty": 0,
        "lesson": r'''
            ## Gluing pieces back together

            `join` is the opposite of `split`. Think of it as a string of beads: you choose
            the thread (the separator), and it threads all the pieces onto it.

            ```python
            parts = ["gpt", "4o", "mini"]
            print("-".join(parts))
            print(" ".join(["hello", "there"]))
            print(", ".join(["a", "b", "c"]))
            ```

            The separator comes **first**, and `join` is called on it: `"-".join(parts)`.
            The separator only goes **between** the pieces, never at the start or end.

            A very common pair: split text into words, change them, join them again.

            ```python
            words = "Big  Cat".split()
            print("_".join(words))
            ```

            **Watch out:** `parts.join("-")` is an error - lists don't have `join`. The
            separator string does. And every item must be a string.
        ''',
        "prompt": r'''
            A *slug* is a URL-friendly name, e.g. for saving a prompt as `my-first-prompt`.

            **Write:** `slugify(title)`

            - `title`: a string, e.g. `"My First  Prompt"`
            - **Returns:** a string: the words of the title, lower-cased, joined by `-`.

            **Rules**
            - Words are separated by any amount of whitespace; extra spaces (in the
              middle or at the ends) must not produce empty pieces or extra dashes.
            - No dash at the start or end.
            - A single word gives just that word, lower-cased.

            **Examples**
            ```python
            slugify("My First  Prompt")   # returns "my-first-prompt"
            slugify("  vector store ")    # returns "vector-store"
            slugify("RAG")                # returns "rag"
            ```
        ''',
        "starter": r'''
            def slugify(title):
                ...
        ''',
        "tests": r'''
            from solution import slugify

            def test_words_lower_cased_and_joined_with_dashes():
                got = slugify("My First  Prompt")
                assert got == "my-first-prompt", f"got {got!r}"

            def test_single_word_is_just_lower_cased():
                assert slugify("RAG") == "rag"

            def test_outer_spaces_add_no_extra_dashes():
                got = slugify("  vector store ")
                assert got == "vector-store", f"got {got!r}"
        ''',
        "solution": r'''
            def slugify(title):
                return "-".join(title.lower().split())
        ''',
        "hints": [
            "Three steps: lower-case, split into words, join them back with a dash.",
            "split() gives a list of words without empty pieces. join is called on the separator string.",
            "Lower-case the title, split it with split(), then call \"-\".join(...) on that list and return the result.",
        ],
    },
    {
        "id": "strings-s6",
        "title": "Is it Markdown?",
        "difficulty": 0,
        "lesson": r'''
            ## Checking the ends

            Before opening a file, you glance at its name: does it end in `.txt`? Before
            trusting a reply, you check: does it start with `"Error"`? Strings have two
            methods for exactly this.

            ```python
            name = "notes.TXT"
            print(name.endswith(".txt"))
            print(name.lower().endswith(".txt"))
            print("/help".startswith("/"))
            ```

            `startswith(x)` and `endswith(x)` return `True` or `False` (a *boolean*), so
            they fit straight into an `if` or a `return`.

            To check whether some text appears **anywhere**, use `in`:

            ```python
            print("key" in "my api key")
            ```

            **Watch out:** all these checks are case-sensitive. `"A.MD".endswith(".md")` is
            `False`. Lower-case first when case shouldn't matter.
        ''',
        "prompt": r'''
            A document loader only handles Markdown files. Check a file name. Fill in
            the `___` in the starter.

            **Write:** `is_markdown(filename)`

            - `filename`: a string, e.g. `"README.md"`
            - **Returns:** `True` if the name ends with `.md`, otherwise `False`

            **Rules**
            - Upper or lower case doesn't matter: `"NOTES.MD"` is Markdown.
            - Only the **end** counts: `"md_notes.txt"` is not Markdown.

            **Examples**
            ```python
            is_markdown("README.md")      # returns True
            is_markdown("NOTES.MD")       # returns True
            is_markdown("md_notes.txt")   # returns False
            ```
        ''',
        "starter": r'''
            def is_markdown(filename):
                return filename.lower().___(".md")
        ''',
        "tests": r'''
            from solution import is_markdown

            def test_lower_case_md_is_markdown():
                assert is_markdown("README.md") is True

            def test_upper_case_md_is_markdown():
                assert is_markdown("NOTES.MD") is True, "case should not matter"

            def test_md_at_the_start_does_not_count():
                assert is_markdown("md_notes.txt") is False

            def test_other_extension_is_not_markdown():
                assert is_markdown("data.json") is False
        ''',
        "solution": r'''
            def is_markdown(filename):
                return filename.lower().endswith(".md")
        ''',
        "hints": [
            "You need the string method that checks how a string finishes.",
            "The lower-casing is already done, so only the method name is missing. It returns True or False.",
            "Replace ___ with endswith.",
        ],
    },
    {
        "id": "strings-1",
        "title": "Normalise whitespace",
        "hints": [
            "Two string methods together solve this: one breaks text into words, the other glues words back together.",
            "split() with no argument splits on ANY run of whitespace and drops empty pieces. Join the pieces with a single space.",
            "Call text.split() to get the words, then return \" \".join(...) of that list. Empty or whitespace-only text gives an empty list, which joins to \"\".",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Squash the gaps

            Text copied out of a PDF looks like a badly packed suitcase: clothes (words)
            with random empty gaps between them. The trick to repack it neatly is to take
            everything out, then put it back in with the same small gap every time.

            ```python
            messy = "one   two\n\nthree"
            pieces = messy.split()
            print(pieces)
            print("|".join(pieces))
            ```

            `split()` (no argument) already throws away every gap of any size, including tabs
            and newlines. `join` then puts back exactly the separator you choose.

            This clean-up has a name: *whitespace normalisation*. It's a standard step
            before counting, comparing or sending text to a model - it saves tokens and
            makes two versions of the same text compare equal.

            **Watch out:** empty or blank text splits into `[]`, and joining an empty list
            gives `""` - no special case needed.
        ''',
        "prompt": r'''
            Text pasted from PDFs is full of stray spaces, tabs and newlines. Clean it up
            before sending it to a model.

            **Write:** `normalize_ws(text)`

            - `text`: a string, e.g. `"  Hello \t\n  world  "`
            - **Returns:** a string where every run of whitespace (spaces, tabs, newlines)
              is replaced by a **single space**, with no whitespace at the start or end.

            **Rules**
            - Text that is empty or only whitespace returns `""`.
            - Text that is already clean comes back unchanged.
            - Don't use the `re` module (a check looks for `import re`): use string methods.

            **Examples**
            ```python
            normalize_ws("  Hello \t\n  world  ")   # returns "Hello world"
            normalize_ws("a\n\nb   c")              # returns "a b c"
            normalize_ws("one two")                 # returns "one two"
            normalize_ws("   \n\t ")                # returns ""
            ```
        ''',
        "starter": r'''
            def normalize_ws(text):
                ...
        ''',
        "tests": r'''
            from solution import normalize_ws

            def test_mixed_whitespace_becomes_single_spaces():
                got = normalize_ws("  Hello \t\n  world  ")
                assert got == "Hello world", f"got {got!r}"

            def test_blank_lines_collapse_to_one_space():
                got = normalize_ws("a\n\nb   c")
                assert got == "a b c", f"got {got!r}"

            def test_only_whitespace_gives_empty():
                got = normalize_ws("   \n\t ")
                assert got == "", f"got {got!r}"

            def test_already_clean_unchanged():
                assert normalize_ws("one two") == "one two"

            def test_does_not_import_re():
                assert "import re" not in source(), "solve it with string methods, not re"
        ''',
        "solution": r'''
            def normalize_ws(text):
                return " ".join(text.split())
        ''',
    },
    {
        "id": "strings-2",
        "title": "Model name parts",
        "hints": [
            "Clean the string first (strip, lower), then check whether it contains a slash with `in`.",
            "If there is no slash, return the default provider with the whole string. Otherwise split only once so the rest of the name stays together.",
            "cleaned = model_id.strip().lower(). If \"/\" not in cleaned, return (\"openai\", cleaned). Otherwise provider, model = cleaned.split(\"/\", 1) and return them as a tuple.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Split only once

            Sometimes you only want to cut at the **first** separator. Think of an address
            like `"hf/meta-llama/llama-3"`: the part before the first `/` is the provider,
            and everything after it - slashes included - is the name.

            ```python
            path = "docs/2024/report.txt"
            print(path.split("/"))
            print(path.split("/", 1))
            first, rest = path.split("/", 1)
            print(first, "|", rest)
            ```

            The second argument of `split` is the maximum number of cuts (*maxsplit*).
            With `1` you always get at most two pieces, which you can *unpack* straight into
            two variables.

            Before splitting, check the separator is there with `in`:

            ```python
            print("/" in "gpt-4o")
            ```

            **Watch out:** unpacking into two names fails with a ValueError if the split
            gave only one piece. Check with `in` first.
        ''',
        "research": {
            "note": "Read the docs for `str.split`, especially what the `maxsplit` argument does and how splitting with no separator differs, then come back.",
            "links": [
                {"title": "str.split - Python docs",
                 "url": "https://docs.python.org/3/library/stdtypes.html#str.split"},
            ],
        },
        "prompt": r'''
            Model identifiers look like `"provider/model-name"`, sometimes with extra
            whitespace and inconsistent case. Split one into its two parts.

            **Write:** `parse_model_id(model_id)`

            - `model_id`: a string, e.g. `"Anthropic/Claude-3"`
            - **Returns:** a **tuple** of two strings `(provider, model)`, e.g.
              `("anthropic", "claude-3")`

            **Rules**
            - Remove whitespace at both ends and lower-case everything first.
            - Split on the **first** `/` only: anything after it (including more `/`) is
              the model.
            - If there is no `/`, the provider is `"openai"` and the whole cleaned string
              is the model.
            - Return a `tuple`, not a list.

            **Examples**
            ```python
            parse_model_id("Anthropic/Claude-3")        # returns ("anthropic", "claude-3")
            parse_model_id(" gpt-4o ")                  # returns ("openai", "gpt-4o")
            parse_model_id("hf/meta-llama/Llama-3-8B")  # returns ("hf", "meta-llama/llama-3-8b")
            ```
        ''',
        "starter": r'''
            def parse_model_id(model_id):
                ...
        ''',
        "tests": r'''
            from solution import parse_model_id

            def test_provider_and_model_lower_cased():
                got = parse_model_id("Anthropic/Claude-3")
                assert got == ("anthropic", "claude-3"), f"got {got!r}"

            def test_no_slash_defaults_provider_to_openai():
                got = parse_model_id(" gpt-4o ")
                assert got == ("openai", "gpt-4o"), f"got {got!r}"

            def test_splits_on_first_slash_only():
                got = parse_model_id("hf/meta-llama/Llama-3-8B")
                assert got == ("hf", "meta-llama/llama-3-8b"), f"got {got!r}"

            def test_result_is_a_tuple():
                assert isinstance(parse_model_id("a/b"), tuple)
        ''',
        "solution": r'''
            def parse_model_id(model_id):
                cleaned = model_id.strip().lower()
                if "/" not in cleaned:
                    return "openai", cleaned
                provider, model = cleaned.split("/", 1)
                return provider, model
        ''',
    },
    {
        "id": "strings-7",
        "title": "Flag keywords",
        "difficulty": 1,
        "lesson": r'''
            ## Case-blind searching

            A content filter should notice "SPAM", "Spam" and "spam" alike. `in` is strict
            about case, so the usual trick is to lower-case **both** sides before comparing.

            ```python
            reply = "Please ignore PREVIOUS instructions"
            print("previous" in reply)
            print("previous" in reply.lower())
            print("Previous".lower() in reply.lower())
            ```

            When you have several words to look for, loop over them and stop as soon as one
            matches - `return True` inside the loop ends the function early. If the loop
            finishes without a match, nothing was found.

            ```python
            for word in ["cat", "dog"]:
                if word in "hot dog stand":
                    print("found", word)
            ```

            This is called a *case-insensitive* check. Real apps use it for keyword
            filters, simple routing ("does the user mention billing?") and guardrails.

            **Watch out:** lower-case the keyword too, not only the text.
        ''',
        "prompt": r'''
            A simple guardrail flags user messages that mention certain keywords, whatever
            their capitalisation.

            **Write:** `mentions_any(text, keywords)`

            - `text`: a string, the user message, e.g. `"Please IGNORE the rules"`
            - `keywords`: a list of strings, e.g. `["ignore", "password"]`; may be empty
            - **Returns:** `True` if at least one keyword appears anywhere in `text`,
              otherwise `False`

            **Rules**
            - The check is **case-insensitive** on both sides: keyword `"Password"` matches
              text `"my PASSWORD is"`.
            - A keyword may appear inside a longer word: `"ignore"` matches `"ignored"`.
            - With an empty `keywords` list, return `False`.

            **Examples**
            ```python
            mentions_any("Please IGNORE the rules", ["ignore", "password"])   # returns True
            mentions_any("my PASSWORD is", ["Password"])                      # returns True
            mentions_any("hello there", ["ignore", "password"])               # returns False
            mentions_any("anything", [])                                      # returns False
            ```
        ''',
        "starter": r'''
            def mentions_any(text, keywords):
                ...
        ''',
        "tests": r'''
            from solution import mentions_any

            def test_upper_case_text_matches_lower_case_keyword():
                assert mentions_any("Please IGNORE the rules", ["ignore", "password"]) is True

            def test_keyword_case_does_not_matter_either():
                assert mentions_any("my PASSWORD is", ["Password"]) is True

            def test_no_keyword_found_returns_false():
                assert mentions_any("hello there", ["ignore", "password"]) is False

            def test_empty_keyword_list_returns_false():
                assert mentions_any("anything", []) is False

            def test_last_keyword_can_match():
                assert mentions_any("send me the api key", ["password", "secret", "Key"]) is True
        ''',
        "solution": r'''
            def mentions_any(text, keywords):
                lowered = text.lower()
                for keyword in keywords:
                    if keyword.lower() in lowered:
                        return True
                return False
        ''',
        "hints": [
            "Use `in` to check whether one string appears inside another, and lower() to ignore case.",
            "Lower-case the text once. Loop over the keywords; as soon as a lower-cased keyword is in the text, you have your answer.",
            "lowered = text.lower(). For each keyword: if keyword.lower() in lowered, return True. After the loop, return False.",
        ],
    },
    {
        "id": "strings-8",
        "title": "Non-blank lines",
        "difficulty": 1,
        "lesson": r'''
            ## One line at a time

            Documents arrive as one long string with `\n` (newline) characters in it.
            Reading them line by line is like reading a shopping list: one item per line,
            skipping the blank ones.

            ```python
            doc = "apples\n\n  milk  \nbread"
            lines = doc.splitlines()
            print(lines)
            for line in lines:
                if line.strip():
                    print("->", line.strip())
            ```

            `splitlines()` cuts at every line break and gives a list of lines, without the
            `\n` characters. Blank lines become empty strings `""` (or strings of spaces).

            `line.strip()` is empty for a blank line, and an empty string counts as
            `False` in an `if`. That makes "skip blank lines" a one-liner.

            An empty string being false is called being *falsy*.

            **Watch out:** `split("\n")` is similar but leaves an extra `""` at the end when
            the text ends with a newline. `splitlines()` doesn't.
        ''',
        "prompt": r'''
            Before chunking a document you want its real lines: trimmed, with blank lines
            dropped.

            **Write:** `clean_lines(text)`

            - `text`: a string with newlines, e.g. `"  intro \n\n body\n"`
            - **Returns:** a list of strings: each line of `text` with whitespace removed
              from both ends, skipping lines that are empty or only whitespace

            **Rules**
            - Keep the original order of the lines.
            - Text that is empty or only blank lines returns `[]`.
            - A trailing newline at the end of the text must not add an empty item.

            **Examples**
            ```python
            clean_lines("  intro \n\n body\n")   # returns ["intro", "body"]
            clean_lines("one\ntwo")              # returns ["one", "two"]
            clean_lines("\n  \n")                # returns []
            ```
        ''',
        "research": {
            "note": "Look up `str.splitlines` in the Python docs: see which characters count as line boundaries and how it differs from `split(\"\\n\")`, then come back.",
            "links": [
                {"title": "str.splitlines - Python docs",
                 "url": "https://docs.python.org/3/library/stdtypes.html#str.splitlines"},
            ],
        },
        "starter": r'''
            def clean_lines(text):
                ...
        ''',
        "tests": r'''
            from solution import clean_lines

            def test_lines_are_trimmed_and_blank_ones_dropped():
                got = clean_lines("  intro \n\n body\n")
                assert got == ["intro", "body"], f"got {got!r}"

            def test_simple_lines_kept_in_order():
                got = clean_lines("one\ntwo\nthree")
                assert got == ["one", "two", "three"], f"got {got!r}"

            def test_only_blank_lines_gives_empty_list():
                got = clean_lines("\n  \n\t\n")
                assert got == [], f"got {got!r}"

            def test_empty_text_gives_empty_list():
                assert clean_lines("") == []

            def test_windows_line_endings():
                got = clean_lines("a\r\nb\r\n")
                assert got == ["a", "b"], f"got {got!r}"
        ''',
        "solution": r'''
            def clean_lines(text):
                result = []
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        result.append(line)
                return result
        ''',
        "hints": [
            "There is a string method that cuts text into a list of lines. Then look at each line on its own.",
            "Loop over the lines, strip each one, and keep it only if something is left after stripping.",
            "Make an empty list. For each line in text.splitlines(): strip it; if the stripped line is not empty, append it. Return the list.",
        ],
    },
    {
        "id": "strings-3",
        "title": "Truncate to N words",
        "hints": [
            "Get the words with split(), then compare how many there are with n.",
            "If there are more than n words, keep only the first n (slicing) and add \"...\". Otherwise just rejoin all the words.",
            "words = text.split(). If len(words) > n, return \" \".join(words[:n]) + \"...\". Else return \" \".join(words).",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Search results show a short preview of each long document. Build that preview.

            **Write:** `truncate_words(text, n)`

            - `text`: a string, e.g. `"The quick brown fox jumps"` (may contain newlines)
            - `n`: an `int` >= 0, the maximum number of words to keep, e.g. `3`
            - **Returns:** a string: the kept words joined by single spaces, plus `"..."`
              if words were cut off.

            **Rules**
            - Words are separated by any whitespace (spaces, tabs, newlines).
            - If the text has **more than** `n` words: return the first `n` words joined by
              single spaces, followed directly by `"..."` (no space before it).
            - Otherwise (`n` words or fewer): return all the words joined by single spaces,
              with no `"..."`.
            - `n` of `0` with non-empty text returns `"..."`.
            - Empty text returns `""`.

            **Examples**
            ```python
            truncate_words("The quick brown fox jumps", 3)       # returns "The quick brown..."
            truncate_words("line one\nline two\nline three", 4)  # returns "line one line two..."
            truncate_words("exactly three words", 3)             # returns "exactly three words"
            truncate_words("Short  text", 5)                     # returns "Short text"
            truncate_words("anything here", 0)                   # returns "..."
            truncate_words("", 3)                                # returns ""
            ```
        ''',
        "starter": r'''
            def truncate_words(text, n):
                ...
        ''',
        "tests": r'''
            from solution import truncate_words

            def test_long_text_cut_to_n_words_with_ellipsis():
                got = truncate_words("The quick brown fox jumps", 3)
                assert got == "The quick brown...", f"got {got!r}"

            def test_short_text_has_no_ellipsis_and_single_spaces():
                got = truncate_words("Short  text", 5)
                assert got == "Short text", f"got {got!r}"

            def test_exactly_n_words_has_no_ellipsis():
                got = truncate_words("exactly three words", 3)
                assert got == "exactly three words", f"got {got!r}"

            def test_newlines_count_as_word_separators():
                got = truncate_words("line one\nline two\nline three", 4)
                assert got == "line one line two...", f"got {got!r}"

            def test_zero_words_gives_only_ellipsis():
                got = truncate_words("anything here", 0)
                assert got == "...", f"got {got!r}"

            def test_empty_text_returns_empty_string():
                got = truncate_words("", 3)
                assert got == "", f"got {got!r}"
        ''',
        "solution": r'''
            def truncate_words(text, n):
                words = text.split()
                if len(words) > n:
                    return " ".join(words[:n]) + "..."
                return " ".join(words)
        ''',
    },
    {
        "id": "strings-4",
        "title": "Word frequencies",
        "hints": [
            "Split into words, clean each word with strip() given a string of punctuation characters, and count with a dict.",
            "strip(chars) removes any of those characters from both ends only. Lower-case each word, skip empty results, and increase its count in the dict.",
            "Store the punctuation characters in a string. Loop over text.split(): word = raw.strip(PUNCT).lower(); if word is not empty, set counts[word] = counts.get(word, 0) + 1. Return counts.",
        ],
        "difficulty": 2,
        "prompt": r'''
            Word frequencies are a first step in keyword search over documents.

            **Write:** `word_counts(text)`

            - `text`: a string, e.g. `"The cat. THE dog!"`
            - **Returns:** a `dict` mapping each word (a lower-case string) to how many
              times it appears (an `int`), e.g. `{"the": 2, "cat": 1, "dog": 1}`

            **Rules**
            - Words are separated by any whitespace.
            - Counting is case-insensitive; keys are lower-case.
            - Remove these punctuation characters from the **start and end** of each word
              only: `.` `,` `!` `?` `;` `:` `"` `'` `(` `)`
            - Punctuation inside a word stays (`"don't"`, `"gpt-4o"`). Other characters
              such as `-` are not stripped, so `"--"` counts as a word.
            - A word that becomes empty after stripping (e.g. `"..."`, `"?!"`) is ignored.
            - Empty text returns `{}`.
            - Don't use `collections` or `re` (a check looks for them in your code): use a
              plain dict and string methods.

            **Examples**
            ```python
            word_counts("The cat. THE dog!")               # returns {"the": 2, "cat": 1, "dog": 1}
            word_counts("Don't stop -- don't!")            # returns {"don't": 2, "stop": 1, "--": 1}
            word_counts('"Hello" (hello) gpt-4o, GPT-4o?')  # returns {"hello": 2, "gpt-4o": 2}
            word_counts("wait ... what ?!")                # returns {"wait": 1, "what": 1}
            word_counts("")                                # returns {}
            ```
        ''',
        "starter": r'''
            def word_counts(text):
                ...
        ''',
        "tests": r'''
            from solution import word_counts

            def test_counts_case_insensitively_with_lower_case_keys():
                got = word_counts("The cat. THE dog!")
                assert got == {"the": 2, "cat": 1, "dog": 1}, f"got {got!r}"

            def test_punctuation_inside_words_is_kept():
                got = word_counts("Don't stop -- don't!")
                assert got == {"don't": 2, "stop": 1, "--": 1}, f"got {got!r}"

            def test_quotes_and_brackets_stripped_from_ends():
                got = word_counts('"Hello" (hello) gpt-4o, GPT-4o?')
                assert got == {"hello": 2, "gpt-4o": 2}, f"got {got!r}"

            def test_words_that_are_only_punctuation_ignored():
                got = word_counts("wait ... what ?!")
                assert got == {"wait": 1, "what": 1}, f"got {got!r}"

            def test_empty_text_returns_empty_dict():
                assert word_counts("") == {}

            def test_does_not_use_collections_or_re():
                src = source()
                assert "collections" not in src and "import re" not in src, \
                    "use plain dicts and string methods"
        ''',
        "solution": r'''
            PUNCT = ".,!?;:\"'()"

            def word_counts(text):
                counts = {}
                for raw in text.split():
                    word = raw.strip(PUNCT).lower()
                    if word:
                        counts[word] = counts.get(word, 0) + 1
                return counts
        ''',
    },
    {
        "id": "strings-5",
        "title": "Clean LLM output",
        "hints": [
            "Work in stages, each one a small check with startswith/endswith followed by slicing, and strip() between stages.",
            "Compare prefixes against a lower-cased copy but cut from the original text. For the fence, drop the closing fence and then everything up to and including the first newline. For quotes, check both ends and slice off one character each side.",
            "text = reply.strip(). Loop over the lower-case prefixes; if text.lower() starts with one, text = text[len(prefix):].strip() and break. If text starts and ends with three backticks: remove the last three chars, find the first \"\\n\" and keep what is after it, strip. If it starts and ends with a double quote (and is at least 2 long), use text[1:-1].",
        ],
        "difficulty": 3,
        "prompt": r'''
            Models often wrap an answer in chatter, code fences or quotes. Strip that
            wrapping so only the answer is left.

            **Write:** `clean_reply(reply)`

            - `reply`: a string, the raw model output, e.g. `"  Sure! Here it is  "`
            - **Returns:** the cleaned string.

            **Rules** (apply these steps in this order)
            1. Remove whitespace (spaces, newlines) at both ends.
            2. If the text **starts with** one of these prefixes, compared
               case-insensitively, remove it and then remove whitespace at both ends again:
               `"Sure!"`, `"Sure,"`, `"Certainly!"`, `"Of course!"`.
               - Remove **at most one** prefix (`"Sure, Sure! ok"` becomes `"Sure! ok"`).
               - A prefix word later in the text is not a prefix: leave it alone.
            3. If the text now starts **and** ends with a triple-backtick fence, remove the
               whole first line (the opening fence, which may carry a language tag such
               as `python`) and the closing fence, then remove whitespace at both ends
               again. Lines inside the fence keep their `\n` between them.
            4. If the text now starts **and** ends with a double quote `"`, remove those
               two quote characters. Quotes elsewhere in the text are left alone.

            **Examples**
            ```python
            clean_reply("  Sure! Here it is  ")                    # returns "Here it is"
            clean_reply('CERTAINLY! "Paris"')                      # returns "Paris"
            clean_reply("```python\nprint(1)\nprint(2)\n```")      # returns "print(1)\nprint(2)"
            clean_reply("Of course!\n```\nSELECT 1;\n```\n")       # returns "SELECT 1;"
            clean_reply('The answer is "yes"')                     # returns 'The answer is "yes"' (unchanged)
            clean_reply("I am not sure! Maybe.")                   # returns "I am not sure! Maybe." (unchanged)
            clean_reply("Sure, Sure! ok")                          # returns "Sure! ok"
            ```
        ''',
        "starter": r'''
            def clean_reply(reply):
                ...
        ''',
        "tests": r'''
            from solution import clean_reply

            def test_prefix_and_outer_whitespace_removed():
                got = clean_reply("  Sure! Here it is  ")
                assert got == "Here it is", f"got {got!r}"

            def test_prefix_is_case_insensitive_and_wrapping_quotes_removed():
                got = clean_reply('CERTAINLY! "Paris"')
                assert got == "Paris", f"got {got!r}"

            def test_code_fence_with_language_tag_removed():
                got = clean_reply("```python\nprint(1)\nprint(2)\n```")
                assert got == "print(1)\nprint(2)", f"got {got!r}"

            def test_prefix_then_code_fence_both_removed():
                got = clean_reply("Of course!\n```\nSELECT 1;\n```\n")
                assert got == "SELECT 1;", f"got {got!r}"

            def test_quotes_inside_text_untouched():
                text = 'The answer is "yes"'
                got = clean_reply(text)
                assert got == text, f"got {got!r}"

            def test_prefix_word_later_in_text_untouched():
                got = clean_reply("I am not sure! Maybe.")
                assert got == "I am not sure! Maybe.", f"got {got!r}"

            def test_only_one_prefix_removed():
                got = clean_reply("Sure, Sure! ok")
                assert got == "Sure! ok", f"got {got!r}"
        ''',
        "solution": r'''
            PREFIXES = ("sure!", "sure,", "certainly!", "of course!")
            FENCE = "`" * 3

            def clean_reply(reply):
                text = reply.strip()
                lowered = text.lower()
                for prefix in PREFIXES:
                    if lowered.startswith(prefix):
                        text = text[len(prefix):].strip()
                        break
                if text.startswith(FENCE) and text.endswith(FENCE) and len(text) > 6:
                    body = text[: -len(FENCE)]
                    first_newline = body.find("\n")
                    body = "" if first_newline == -1 else body[first_newline + 1:]
                    text = body.strip()
                if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
                    text = text[1:-1]
                return text
        ''',
    },
    {
        "id": "strings-6",
        "title": "Prompt builder",
        "hints": [
            "Split the raw text into lines with splitlines(). The first line is the instruction, the rest are snippets. Build the output as a list of lines and join them with \"\\n\" at the end.",
            "Clean the instruction (strip, upper-case only the first letter, add a period if needed). Keep only non-blank stripped snippets. Then add the section lines in order, numbering snippets from 1.",
            "lines = raw.splitlines(). instruction = lines[0].strip() if there are lines; instruction = instruction[:1].upper() + instruction[1:]; if not instruction.endswith((\"?\", \".\")) add \".\". snippets = stripped non-empty lines[1:]. Build a list: \"### Instruction\", instruction, \"\", \"### Context\", then [i] lines (enumerate(snippets, start=1)) or \"(none)\", then \"\", \"### Answer\". Return \"\\n\".join(that list) + \"\\n\".",
        ],
        "difficulty": 3,
        "prompt": r'''
            A RAG app turns a task plus retrieved chunks into one prompt for the model.
            Build that prompt from a block of text.

            **Write:** `build_prompt(raw)`

            - `raw`: a string with one item per line, e.g.
              `"summarise the docs\nFirst chunk\n\n  Second chunk \n"`
              - line 1 is the task instruction
              - every following line is a context snippet
            - **Returns:** one string in exactly this format, where every line (including
              the last, `### Answer`) ends with `\n`:

            ```
            ### Instruction
            <instruction>

            ### Context
            [1] <snippet 1>
            [2] <snippet 2>

            ### Answer
            ```

            **Rules**
            - Instruction: remove whitespace at both ends, upper-case **only its first
              letter** (the rest keeps its case, e.g. `GPU` stays `GPU`).
            - If the instruction ends with `?` or `.`, keep it as is; otherwise add a `.`.
            - Snippets: remove whitespace at both ends of each one; skip blank lines.
            - Snippets are numbered from `[1]`, in order, one per line.
            - If there are no snippets, the Context section is the single line `(none)`.
            - There is exactly one empty line before `### Context` and before `### Answer`.

            **Examples**
            ```python
            build_prompt("summarise the docs\nFirst chunk\n\n   Second chunk  \n")
            # returns "### Instruction\nSummarise the docs.\n\n### Context\n[1] First chunk\n[2] Second chunk\n\n### Answer\n"

            build_prompt("Explain tokens.\n\n\n")
            # returns "### Instruction\nExplain tokens.\n\n### Context\n(none)\n\n### Answer\n"

            build_prompt("what is RAG?\nRAG means retrieval.\n")     # instruction line: "What is RAG?"
            build_prompt("  list GPU types  \nA\n")                  # instruction line: "List GPU types."
            ```
        ''',
        "starter": r'''
            def build_prompt(raw):
                ...
        ''',
        "tests": r'''
            from solution import build_prompt

            def test_full_prompt_has_exact_format():
                got = build_prompt("summarise the docs\nFirst chunk\n\n   Second chunk  \n")
                expected = ("### Instruction\nSummarise the docs.\n\n### Context\n"
                            "[1] First chunk\n[2] Second chunk\n\n### Answer\n")
                assert got == expected, f"got {got!r}"

            def test_question_keeps_its_question_mark():
                lines = build_prompt("what is RAG?\nRAG means retrieval.\n").splitlines()
                assert lines[1] == "What is RAG?", f"instruction line was {lines[1]!r}"

            def test_no_snippets_shows_none():
                got = build_prompt("Explain tokens.\n\n\n")
                expected = ("### Instruction\nExplain tokens.\n\n### Context\n(none)\n\n"
                            "### Answer\n")
                assert got == expected, f"got {got!r}"

            def test_only_first_letter_upper_cased_and_period_added():
                lines = build_prompt("  list GPU types  \nA\n").splitlines()
                assert lines[1] == "List GPU types.", f"instruction line was {lines[1]!r}"
        ''',
        "solution": r'''
            def build_prompt(raw):
                lines = raw.splitlines()
                instruction = lines[0].strip() if lines else ""
                instruction = instruction[:1].upper() + instruction[1:]
                if not instruction.endswith(("?", ".")):
                    instruction += "."
                snippets = []
                for line in lines[1:]:
                    if line.strip():
                        snippets.append(line.strip())

                out = ["### Instruction", instruction, "", "### Context"]
                if snippets:
                    for i, snippet in enumerate(snippets, start=1):
                        out.append(f"[{i}] {snippet}")
                else:
                    out.append("(none)")
                out += ["", "### Answer"]
                return "\n".join(out) + "\n"
        ''',
    },
]
