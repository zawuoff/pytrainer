TOPIC = {
    "id": "regex",
    "title": "Regular Expressions",
    "track": "apis-data",
    "order": 3,
    "requires": ["strings"],
    "summary": """
        Searching, extracting, validating and rewriting text with the re module:
        groups and named groups, flags, compiled patterns, and parsing or redacting
        LLM output and logs.
    """,
    "concepts": ["re.search", "re.match", "re.fullmatch", "re.findall", "re.sub", "re.split",
                 "groups", "named groups", "flags", "re.compile", "anchors", "quantifiers"],
}

LESSON = r'''
## Regular expressions - chapter notes

A **regex** is a pattern that describes the *shape* of text ("digits, then a dash, then 4
letters"). Python's tools live in `re`. Always write patterns as raw strings: `r"\d+"`.

| function | does | returns |
| --- | --- | --- |
| `re.search(p, s)` | first match anywhere | match object or `None` |
| `re.match(p, s)` | match at the **start** only | match object or `None` |
| `re.fullmatch(p, s)` | the **whole** string must match (validation) | match object or `None` |
| `re.findall(p, s)` | every match | list of strings (of the group, if the pattern has one) |
| `re.sub(p, repl, s)` | replace every match (`repl` may be a function) | new string |
| `re.compile(p, flags)` | build a pattern object once, reuse it | `Pattern` with the same methods |

**Building blocks:** `\d` digit, `\w` letter/digit/`_`, `\s` whitespace, `.` any character
(`\.` a real dot), `[a-z0-9_-]` one of a set, `[^...]` none of a set.
**Quantifiers:** `+` 1 or more, `*` 0 or more, `?` optional, `{4}` exactly 4, `{2,}` 2 or
more, `{20,48}` 20 to 48.
**Anchors:** `^` start, `$` end (of each line with `re.MULTILINE`).
**Groups:** `(...)` captures, `m.group(1)`; named: `(?P<name>...)`, `m.group("name")`;
`(?:...)` groups without capturing. **Flags:** `re.IGNORECASE`, `re.MULTILINE`, `re.VERBOSE`.

```python
import re

m = re.search(r"(?P<key>\w+)=(?P<value>\d+)", "set max_tokens=512 now")
print(m.group("key"), int(m.group("value")))
print(re.sub(r"\s+", " ", "too    many   spaces"))
print(re.findall(r"^ERROR: (.*)$", "ERROR: a\nINFO: b\nERROR: c", flags=re.MULTILINE))
```

**Gotchas**
- `"\b"` without `r` is a backspace character - always use `r"..."`.
- `.` matches anything; escape it for a literal dot.
- `re.match` only looks at the start; use `search` to look anywhere, `fullmatch` to validate.
- Groups change what `findall` returns; leave them out (or use `(?:...)`) for whole matches.
- Always check for `None` before calling `.group()`.
'''

EXERCISES = [
    {
        "id": "regex-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            Think of a regex as a **wanted poster** for text. It doesn't say "find the word `66`", it
            describes a *shape*: "a run of digits". Python then searches the text for anything that fits
            the description.

            ```python
            import re

            text = "Model v4 costs 30 dollars"
            m = re.search(r"\d+", text)
            print(m.group())
            print(re.findall(r"\d+", text))
            ```

            The pieces:
            - `\d` means "one digit"; `+` means "one or more of the thing before me". So `\d+` is a
              whole run of digits.
            - `re.search(pattern, text)` finds the **first** match. It returns a *match object*;
              `.group()` gives the matched text.
            - `re.findall(pattern, text)` returns **every** match as a list of strings.

            The pattern is written `r"..."` - a *raw string*, so the backslashes reach `re` untouched.
            Python's regex tools all live in the `re` module.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            import re

            text = "Order 66 shipped in 3 boxes"
            print(re.findall(r"\d+", text))
            m = re.search(r"\d+", text)
            print(m.group())
        ''',
        "solution": r'''
            ['66', '3']
            66
        ''',
        "explanation": r'''
            `\d+` means "one or more digits". `re.findall` returns **every** match as a list of
            strings (not ints), so you get `['66', '3']`. `re.search` stops at the **first**
            match, and `.group()` gives its text: `66`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            r"`\d` is one digit and `+` means 'one or more', so `\d+` matches a whole run of digits.",
            "`findall` collects every match into a list of strings; `search` only finds the first one.",
            "Line 1: list every digit run in the text, printed as a Python list with quotes. Line 2: just the first run, printed without quotes.",
        ],
    },
    {
        "id": "regex-s2",
        "title": "Find all numbers",
        "difficulty": 0,
        "lesson": r'''
            `re.findall` is a highlighter pen: it runs over the whole text and marks **every** piece that
            fits the pattern, then hands you the marked pieces as a list, left to right.

            ```python
            import re

            log = "latency 120ms, 85ms, 240ms"
            print(re.findall(r"\d+", log))
            print(re.findall(r"\d+", "no numbers"))
            ```

            Things to notice:
            - The results are **strings** (`"120"`), even when they look like numbers. Convert with
              `int(...)` if you need maths.
            - Nothing found? You get an empty list `[]`, never `None` - so a `for` loop over the result
              is always safe.
            - Matches never overlap: after one match, the search continues right after it.

            Compare with `re.search`, which stops at the first match and gives a match object. When the
            task says "all of them", reach for `findall`.
        ''',
        "prompt": r'''
            Logs mix numbers into text (`"used 1200 tokens"`). Pull out all of them.

            **Write:** replace the `___` in `find_numbers(text)` with the right `re` function name.

            - `text`: a `str`, e.g. `"gpt-4o used 1200 tokens"`
            - **Returns:** a `list` of strings: **every** run of digits, in order, e.g. `["4", "1200"]`

            **Rules**
            - Keep the pattern as it is; only fill in the blank.
            - The numbers stay strings (`"1200"`, not `1200`).
            - No digits: return `[]`.

            **Examples**
            ```python
            find_numbers("gpt-4o used 1200 tokens")   # returns ["4", "1200"]
            find_numbers("1, 22, 333")                # returns ["1", "22", "333"]
            find_numbers("no digits")                 # returns []
            ```
        ''',
        "starter": r'''
            import re


            def find_numbers(text):
                return re.___(r"\d+", text)
        ''',
        "tests": r'''
            from solution import find_numbers

            def test_finds_each_run_of_digits_as_a_string():
                got = find_numbers("gpt-4o used 1200 tokens")
                assert got == ["4", "1200"], f"got {got!r}"

            def test_no_digits_returns_empty_list():
                got = find_numbers("no digits")
                assert got == [], f"got {got!r}"

            def test_three_numbers_in_order():
                got = find_numbers("1, 22, 333")
                assert got == ["1", "22", "333"], f"got {got!r}"
        ''',
        "solution": r'''
            import re


            def find_numbers(text):
                return re.findall(r"\d+", text)
        ''',
        "hints": [
            "You need the `re` function that returns ALL matches, not just the first.",
            "`re.search` gives one match object; the other function gives a list of every matching string.",
            "Replace `___` with the name of the function from the lesson that returns a list of all matches (it starts with 'find').",
        ],
    },
    {
        "id": "regex-s3",
        "title": "Fix the version finder",
        "difficulty": 0,
        "lesson": r'''
            Three functions, three places a pattern may match. Picture looking for a cat in a house:
            - `re.match` checks only the **front door** (the start of the string).
            - `re.search` walks through **every room** and stops at the first cat.
            - `re.fullmatch` says the **whole house** must be exactly one cat - nothing else allowed.

            ```python
            import re

            text = "use model v2 today"
            print(re.match(r"v\d", text))
            print(re.search(r"v\d", text).group())
            print(re.fullmatch(r"v\d", "v2") is not None)
            ```

            All three return a match object when they succeed and `None` when they don't. That's why
            you often see `... is not None` - it turns the result into a clean `True`/`False`.

            Watch out: `re.match` is the classic trap - its name sounds like "find a match", but it only
            ever looks at the very beginning.
        ''',
        "prompt": r'''
            Release notes mention model versions like `v1.2`. `has_version` should spot one
            anywhere in the text, but right now it only finds a version at the very start.

            **Write:** fix `has_version(text)`

            - `text`: a `str`, e.g. `"release v10.04 now"`
            - **Returns:** `True` if the text contains a version **anywhere**, else `False`
              (a real `bool`)

            **Rules**
            - A version is `v`, one or more digits, `.`, one or more digits (e.g. `v1.2`, `v10.04`).
              The pattern is already correct; the bug is elsewhere.
            - `v1` alone (no `.` and minor number) is not a version.

            **Examples**
            ```python
            has_version("v1.2 is out")          # returns True
            has_version("release v10.04 now")   # returns True
            has_version("no version here")      # returns False
            has_version("v1 without minor")     # returns False
            ```
        ''',
        "starter": r'''
            import re


            def has_version(text):
                return re.match(r"v\d+\.\d+", text) is not None
        ''',
        "tests": r'''
            from solution import has_version

            def test_version_at_start_is_found():
                assert has_version("v1.2 is out") is True

            def test_version_in_the_middle():
                assert has_version("release v10.04 now") is True, "a version in the middle was not found"

            def test_no_full_version_returns_false():
                assert has_version("no version here") is False
                assert has_version("v1 without minor") is False
        ''',
        "solution": r'''
            import re


            def has_version(text):
                return re.search(r"v\d+\.\d+", text) is not None
        ''',
        "hints": [
            "The pattern is fine. Look at which `re` function is used.",
            "`re.match` only checks the beginning of the string. You need a function that looks anywhere.",
            "Swap `re.match` for the function that scans the whole text for the first match (see 'Where must it match?' in the lesson).",
        ],
    },
    {
        "id": "regex-s4",
        "title": "Validate a ticket id",
        "difficulty": 0,
        "lesson": r'''
            Validation is like a **stencil**: the input must fit it exactly, edge to edge. That's
            `re.fullmatch`. Combine it with an exact count and you can check formats like codes, ids or
            dates.

            ```python
            import re

            print(re.fullmatch(r"\d{3}", "123") is not None)
            print(re.fullmatch(r"\d{3}", "1234") is not None)
            print(re.fullmatch(r"ID-\d{3}", "ID-042") is not None)
            print(re.fullmatch(r"ID-\d{3}", "my ID-042") is not None)
            ```

            The vocabulary:
            - `{3}` is a *quantifier* meaning "exactly 3 of the thing before me".
            - Plain letters and `-` in a pattern are *literals*: they match themselves, case included.

            Watch out: `re.search(r"\d{3}", "1234")` succeeds (it finds `123` inside), which is why
            validation needs `fullmatch`, not `search`.
        ''',
        "prompt": r'''
            A support bot should only look up a ticket when the user typed a valid ticket id.

            **Write:** `is_ticket_id(text)`

            - `text`: a `str`, e.g. `"TICKET-1234"`
            - **Returns:** `True` if the **whole** string is a ticket id, else `False` (a real `bool`)

            **Rules**
            - A ticket id is exactly `TICKET-` (upper case) followed by **exactly 4 digits**.
            - Nothing may come before or after it: `"see TICKET-1234"` and `"TICKET-1234!"` are `False`.
            - 3 or 5 digits, lower case `ticket-`, or a letter among the digits: `False`.

            Reminder: `re.fullmatch(pattern, text)` returns a match object or `None`, and `\d{4}`
            means exactly four digits.

            **Examples**
            ```python
            is_ticket_id("TICKET-1234")      # returns True
            is_ticket_id("TICKET-0000")      # returns True
            is_ticket_id("TICKET-123")       # returns False
            is_ticket_id("see TICKET-1234")  # returns False
            is_ticket_id("ticket-1234")      # returns False
            ```
        ''',
        "starter": r'''
            import re


            def is_ticket_id(text):
                ...
        ''',
        "tests": r'''
            from solution import is_ticket_id

            def test_ticket_with_four_digits_is_valid():
                assert is_ticket_id("TICKET-1234") is True
                assert is_ticket_id("TICKET-0000") is True

            def test_three_or_five_digits_rejected():
                assert is_ticket_id("TICKET-123") is False, "3 digits is not enough"
                assert is_ticket_id("TICKET-12345") is False, "5 digits is too many"

            def test_extra_text_wrong_case_or_letters_rejected():
                for text in ("see TICKET-1234", "TICKET-1234!", "ticket-1234", "TICKET-12a4"):
                    assert is_ticket_id(text) is False, f"{text!r} should be False"
        ''',
        "solution": r'''
            import re


            def is_ticket_id(text):
                return re.fullmatch(r"TICKET-\d{4}", text) is not None
        ''',
        "hints": [
            "Whole-string checks are the job of `re.fullmatch`.",
            "Write a pattern with the literal text `TICKET-` followed by a digit class with an exact count, then turn the result into True/False.",
            r"1) Pattern: the literal `TICKET-` then `\d{4}`. 2) Call `re.fullmatch(pattern, text)`. 3) Return whether the result `is not None`.",
        ],
    },
    {
        "id": "regex-s5",
        "title": "Collect hashtags",
        "difficulty": 0,
        "lesson": r'''
            Sometimes one position can hold **several** allowed characters. A *character class* `[...]`
            is a menu: "any ONE of these". Ranges save typing: `[a-z]`, `[A-Z]`, `[0-9]`.

            ```python
            import re

            text = "tags: #ai, #ML_ops, #2024!"
            print(re.findall(r"[a-z]+", "abc DEF ghi"))
            print(re.findall(r"#[A-Za-z]+", text))
            print(re.findall(r"#\w+", text))
            ```

            Shortcuts you'll use constantly:
            - `\d` = `[0-9]` (a digit)
            - `\w` = letters, digits and `_` (a "word" character)
            - `\s` = any whitespace (space, tab, newline)

            Put a quantifier after the class to repeat it: `[A-Za-z]+` is "one or more letters". The
            match stops at the first character that is not on the menu - here `,` and `!`.
        ''',
        "prompt": r'''
            You want to tag social posts by topic before sending them to a classifier. Pull
            out the hashtags.

            **Write:** `find_hashtags(text)`

            - `text`: a `str`, e.g. `"Loving #RAG and #llm_ops!"`
            - **Returns:** a `list` of strings, every hashtag in the order it appears, each
              including its `#`, e.g. `["#RAG", "#llm_ops"]`

            **Rules**
            - A hashtag is `#` followed by **one or more** letters, digits or `_`.
            - The hashtag ends at the first other character (`!`, `,`, `-`, space...), so
              `"#gpt-4"` gives `"#gpt"`.
            - A `#` with nothing valid after it is not a hashtag.
            - No hashtags: return `[]`.

            Reminder: a *character class* like `[A-Za-z]` matches one character from the set.

            **Examples**
            ```python
            find_hashtags("Loving #RAG and #llm_ops! #")   # returns ["#RAG", "#llm_ops"]
            find_hashtags("#ai2024, #gpt-4 #x")            # returns ["#ai2024", "#gpt", "#x"]
            find_hashtags("nothing here")                  # returns []
            ```
        ''',
        "starter": r'''
            import re


            def find_hashtags(text):
                ...
        ''',
        "tests": r'''
            from solution import find_hashtags

            def test_finds_hashtags_in_order():
                got = find_hashtags("Loving #RAG and #llm_ops! #")
                assert got == ["#RAG", "#llm_ops"], f"got {got!r}"

            def test_no_hashtags_returns_empty_list():
                assert find_hashtags("nothing here") == []

            def test_hashtag_includes_digits_and_stops_at_punctuation():
                got = find_hashtags("#ai2024, #gpt-4 #x")
                assert got == ["#ai2024", "#gpt", "#x"], f"got {got!r}"
        ''',
        "solution": r'''
            import re


            def find_hashtags(text):
                return re.findall(r"#[A-Za-z0-9_]+", text)
        ''',
        "hints": [
            "Use `re.findall` with a pattern that starts with a literal `#`.",
            "After the `#`, put a character class containing letters, digits and underscore, and repeat it one or more times.",
            r"1) Start the pattern with `#`. 2) Add a class like `[A-Za-z0-9_]` (or the shortcut `\w`). 3) Add `+` after it. 4) Return `re.findall(pattern, text)`.",
        ],
    },
    {
        "id": "regex-s6",
        "title": "Capture the pieces",
        "difficulty": 0,
        "lesson": r'''
            Finding a match is nice; usually you want **pieces** of it. Parentheses `( )` in a pattern
            are labelled bags: whatever that part of the pattern matched goes in the bag, and you can
            take it out afterwards. They're called *capturing groups*.

            ```python
            import re

            m = re.search(r"(\d+)x(\d+)", "image size 1024x768 px")
            print(m.group(0))
            print(m.group(1))
            print(m.group(2))
            ```

            - `m.group(0)` (or just `m.group()`) is the **whole** match.
            - `m.group(1)` is the first bag, counting opening parentheses from the left, `m.group(2)`
              the second, and so on.
            - Groups are always strings: use `int(...)` for numbers.

            The parentheses don't change *what* matches - only what you can pull out afterwards.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            import re

            m = re.search(r"(\w+)=(\d+)", "set max_tokens=512 now")
            print(m.group(0))
            print(m.group(1))
            print(int(m.group(2)) * 2)
        ''',
        "solution": r'''
            max_tokens=512
            max_tokens
            1024
        ''',
        "explanation": r'''
            The pattern matches `max_tokens=512` (a run of word characters, `=`, a run of digits).
            `group(0)` is that whole match, `group(1)` is the first parenthesised part
            (`max_tokens`), and `group(2)` is the text `"512"`, which `int` turns into a number
            before doubling it.
        ''',
        "starter": "", "tests": "",
        "hints": [
            r"`\w+` stops at the first character that is not a letter, digit or `_` - the `=` here. `set` is not followed by `=`.",
            "Group 0 is the whole match; groups 1 and 2 are the parts inside each pair of parentheses.",
            "Line 1: the whole `name=number` text. Line 2: only the name. Line 3: the number converted to int and doubled.",
        ],
    },
    {
        "id": "regex-1",
        "hints": [
            'Use `re.findall` with one pattern built from character classes `[...]` and quantifiers like `+` and `{2,}`.',
            'Describe an email left to right: allowed name characters, `@`, domain characters, a literal dot, then 2+ letters. Use no capturing groups so findall returns whole addresses.',
            '1) Name part: a class holding `\\w` plus the symbols `. % + -`, repeated with `+`. 2) A literal `@`. 3) Domain: a class of letters, digits, `.` and `-`, repeated. 4) An escaped dot `\\.` then letters repeated `{2,}`. 5) Return `re.findall(pattern, text)`.',
        ],
        "title": "Extract emails",
        "difficulty": 1,
        "lesson": r'''
            Real patterns are just the small pieces chained left to right, like describing a postal
            address: "a name, then `@`, then a domain, then a dot, then 2+ letters".

            ```python
            import re

            PRICE = re.compile(r"\$\d+\.\d{2}")
            print(PRICE.findall("was $19.99, now $9.50 (or 9.50?)"))
            print(re.findall(r"v\d+\.\d+", "v1.2 and v10x3"))
            ```

            New pieces here:
            - **Escaping.** `.` means "any character" and `$` has a special meaning too. To match the
              real symbol, put a backslash in front: `\.`, `\$`. This is called *escaping*.
            - **`{2,}`** means "2 or more".
            - **`re.compile(pattern)`** builds a *pattern object* once; it has the same methods
              (`.findall`, `.search`, ...). Handy for a pattern you reuse, usually stored in a
              CAPITALS constant at the top of the file.

            Inside a class, most symbols are literal already: `[.%+]` is simply "a dot, a percent or a
            plus". Watch out: an unescaped `.` outside a class quietly matches anything, so `a.b`
            also matches `axb`.
        ''',
        "prompt": r'''
            Before sending support tickets to an LLM you want to know which contacts they
            mention. Extract the email addresses.

            **Write:** `find_emails(text)`

            - `text`: a `str`, e.g. `"Contact ops@x.io today"`
            - **Returns:** a `list` of strings: every whole email address, in the order they
              appear, e.g. `["ops@x.io"]`

            **Rules** (what counts as an email here, left to right):
            - a name part: one or more letters, digits, `.`, `_`, `%`, `+` or `-`
            - then `@`
            - then a domain made of letters, digits, `-` and `.`
            - ending in a `.` followed by **at least 2 letters** (so `a@b.c` is not an email, and
              `bob@localhost` is not either)
            - Punctuation around an address (brackets, a final `.` or `,`) is not part of it.
            - Return whole addresses, not pieces of them. No emails: return `[]`.

            **Examples**
            ```python
            find_emails("Contact ana.b+ai@lab.example.com or ops@x.io, not bob@localhost.")
            # returns ["ana.b+ai@lab.example.com", "ops@x.io"]
            find_emails("Mail me (dev_team@corp.co.uk).")   # returns ["dev_team@corp.co.uk"]
            find_emails("a@b.c and real@site.ai")           # returns ["real@site.ai"]
            find_emails("no addresses here @ all")          # returns []
            ```
        ''',
        "starter": r'''
            import re


            def find_emails(text):
                ...
        ''',
        "tests": r'''
            from solution import find_emails

            def test_finds_emails_in_order():
                got = find_emails("Contact ana.b+ai@lab.example.com or ops@x.io, not bob@localhost.")
                assert got == ["ana.b+ai@lab.example.com", "ops@x.io"], f"got {got!r}"

            def test_no_emails_returns_empty_list():
                assert find_emails("no addresses here @ all") == []

            def test_surrounding_punctuation_not_included():
                got = find_emails("Mail me (dev_team@corp.co.uk).")
                assert got == ["dev_team@corp.co.uk"], f"got {got!r}"

            def test_one_letter_ending_is_not_an_email():
                got = find_emails("a@b.c and real@site.ai")
                assert got == ["real@site.ai"], f"got {got!r}"

            def test_returns_whole_addresses_as_strings():
                got = find_emails("x@y.com")
                assert got == ["x@y.com"], f"got {got!r} - return whole addresses, not groups"
        ''',
        "solution": r'''
            import re

            EMAIL = re.compile(r"[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


            def find_emails(text):
                return EMAIL.findall(text)
        ''',
    },
    {
        "id": "regex-2",
        "hints": [
            'Checking a WHOLE string is the job of `re.fullmatch`.',
            'The pattern is the literal prefix `sk-` followed by one character class repeated between 20 and 48 times. Convert the match result to a bool.',
            '1) Build a class with letters, digits, `_` and `-` (put `-` last inside the brackets). 2) Add the quantifier `{20,48}`. 3) Put `sk-` in front. 4) Return `re.fullmatch(pattern, key) is not None`.',
        ],
        "title": "Validate an API key",
        "difficulty": 1,
        "lesson": r'''
            A form field that says "8 to 12 characters" is a range quantifier: `{m,n}` means "between
            m and n times", both ends included. Combined with `fullmatch`, it's the standard way to
            check a token or key *looks* right before you send it to an API.

            ```python
            import re

            CODE = re.compile(r"ab-[a-z0-9_-]{3,5}")
            for text in ["ab-x1", "ab-x1_-z", "ab-x", "ab-x1y2z9"]:
                print(text, CODE.fullmatch(text) is not None)
            ```

            Details worth knowing:
            - A `-` inside a class means a range (`a-z`). To include a real hyphen, put it **last**:
              `[a-z_-]`.
            - `fullmatch` rejects anything extra, even a trailing newline `"\n"` - the typical leftover
              when a key is read from a file.

            The name for this kind of check is *format validation*: it catches typos early, but it can't
            tell you the key actually works - only the API can.
        ''',
        "prompt": r'''
            Before calling an LLM API, check that the configured key at least looks right, so
            a typo fails fast with a clear message.

            **Write:** `is_valid_key(key)`

            - `key`: a `str`, e.g. `"sk-proj_Ab3-xxxxxxxxxxxx"`
            - **Returns:** `True` if the **whole** string is a valid key, else `False` (a real `bool`)

            **Rules**
            - It starts with lower-case `sk-` (`pk-` or `SK-` are invalid).
            - Then **20 to 48** characters (both included), each a letter, digit, `_` or `-`.
              19 or 49 characters are invalid; a space or `!` makes it invalid.
            - Nothing else may appear before or after it - not a space, not `"key="`, not even a
              trailing newline `"\n"`.

            **Examples**
            ```python
            is_valid_key("sk-" + "a" * 20)       # returns True
            is_valid_key("sk-" + "a" * 49)       # returns False (too long)
            is_valid_key("sk-short")             # returns False
            is_valid_key(" sk-" + "a" * 20)      # returns False
            is_valid_key("sk-" + "a" * 20 + "\n")   # returns False
            ```
        ''',
        "starter": r'''
            import re


            def is_valid_key(key):
                ...
        ''',
        "tests": r'''
            from solution import is_valid_key

            GOOD = "sk-proj_Ab3-" + "x" * 12

            def test_valid_keys_return_true():
                for key in ("sk-" + "a" * 20, "sk-" + "Z9_-" * 12, GOOD):
                    assert is_valid_key(key) is True, f"{key!r} should be valid"

            def test_19_or_49_characters_rejected():
                assert is_valid_key("sk-" + "a" * 19) is False, "19 chars is too short"
                assert is_valid_key("sk-" + "a" * 49) is False, "49 chars is too long"

            def test_wrong_prefix_case_or_characters_rejected():
                for key in ("pk-" + "a" * 20, "SK-" + "a" * 20, "sk-" + "a" * 19 + "!", "sk-" + "a b" * 8):
                    assert is_valid_key(key) is False, f"{key!r} should be invalid"

            def test_extra_text_or_newline_around_key_rejected():
                for key in (" " + GOOD, GOOD + " ", "key=" + GOOD, GOOD + "\n"):
                    assert is_valid_key(key) is False, f"{key!r} should be invalid"
        ''',
        "solution": r'''
            import re

            KEY = re.compile(r"sk-[A-Za-z0-9_-]{20,48}")


            def is_valid_key(key):
                return KEY.fullmatch(key) is not None
        ''',
    },
    {
        "id": "regex-7",
        "title": "Tidy the whitespace",
        "difficulty": 1,
        "lesson": r'''
            `re.sub` is **find and replace** from a word processor - but the "find" box takes a pattern.
            Every piece of text that fits the pattern is swapped for the replacement, and you get a new
            string back (the original is never changed; strings are immutable).

            ```python
            import re

            phone = "call 555-1234 or 555-9876"
            print(re.sub(r"\d", "#", phone))
            print(re.sub(r"-+", "-", "a---b--c"))
            print(re.sub(r"x", "y", "no match here"))
            ```

            The order of arguments is `re.sub(pattern, replacement, text)` - pattern first, text last.
            If nothing matches, you simply get the same text back.

            In AI apps this is everyday cleanup: collapsing messy spacing before counting tokens,
            masking numbers or ids before logging, normalising user input before it goes in a prompt.

            Remember the shortcut `\s`: any whitespace character - space, tab `\t` or newline `\n`.
        ''',
        "prompt": r'''
            Text pasted by users (or scraped from PDFs) is full of messy spacing. Normalise it
            before putting it in a prompt.

            **Write:** `tidy_spaces(text)`

            - `text`: a `str`, e.g. `"  Summarise\tthis\n\n  please "`
            - **Returns:** a `str`: every run of whitespace (spaces, tabs, newlines, in any mix)
              replaced by **one** space, with no whitespace at the start or end

            **Rules**
            - Use `re.sub` (a check looks for it in your code).
            - Text that is empty or only whitespace returns `""`.
            - Other characters are kept exactly as they are.

            **Examples**
            ```python
            tidy_spaces("  Summarise\tthis\n\n  please ")   # returns "Summarise this please"
            tidy_spaces("already tidy")                    # returns "already tidy"
            tidy_spaces(" \n\t ")                          # returns ""
            ```
        ''',
        "starter": r'''
            import re


            def tidy_spaces(text):
                ...
        ''',
        "tests": r'''
            from solution import tidy_spaces

            def test_mixed_whitespace_becomes_single_spaces():
                got = tidy_spaces("  Summarise\tthis\n\n  please ")
                assert got == "Summarise this please", f"got {got!r}"

            def test_tidy_text_is_unchanged():
                got = tidy_spaces("already tidy, ok?")
                assert got == "already tidy, ok?", f"got {got!r}"

            def test_only_whitespace_returns_empty_string():
                assert tidy_spaces(" \n\t ") == ""
                assert tidy_spaces("") == ""

            def test_uses_re_sub():
                assert "sub(" in source(), "use re.sub for this exercise"
        ''',
        "solution": r'''
            import re


            def tidy_spaces(text):
                return re.sub(r"\s+", " ", text).strip()
        ''',
        "hints": [
            r"`re.sub` replaces every match of a pattern; `\s` matches any whitespace character.",
            "Replace each run of one-or-more whitespace characters with a single space, then remove what's left at both ends.",
            r"1) Call `re.sub` with the pattern `\s+`, the replacement `\" \"` and the text. 2) Call `.strip()` on the result. 3) Return it.",
        ],
    },
    {
        "id": "regex-8",
        "title": "Named groups",
        "difficulty": 1,
        "lesson": r'''
            Numbered groups work, but `m.group(3)` tells a reader nothing. **Named groups** stick a
            label on each bag: `(?P<model>...)` captures like `(...)`, and you get it back with
            `m.group("model")`. Change the pattern later and your code still reads the right piece.

            ```python
            import re

            m = re.search(r"(?P<w>\d+)x(?P<h>\d+)", "size 1024x768")
            print(m.group("w"), m.group("h"))
            print(m.groupdict())
            print(re.search(r"(?P<w>\d+)x", "no size"))
            ```

            - `(?P<name>pattern)` is the syntax - the `P` is upper case.
            - `m.groupdict()` returns all named groups as a dict, values as strings.
            - As always, when nothing matches you get `None`, so check before calling `.group(...)`.

            This step's research task: read the official syntax description of named groups so you
            recognise it in other people's code.
        ''',
        "research": {
            "note": "Read how named groups `(?P<name>...)` are written and how you get their text back from a match object, then come back.",
            "links": [
                {"title": "Regular expression syntax - Python docs", "url": "https://docs.python.org/3/library/re.html#regular-expression-syntax"},
                {"title": "Match.group - Python docs", "url": "https://docs.python.org/3/library/re.html#re.Match.group"},
            ],
        },
        "prompt": r'''
            Usage logs contain lines like `"model=gpt-4o tokens=512 status=ok"`. Pull out the
            model and the token count.

            **Write:** `parse_usage(line)`

            - `line`: a `str`, e.g. `"ts=17:02 model=gpt-4o tokens=512 status=ok"`
            - **Returns:** a `dict` `{"model": <str>, "tokens": <int>}`, e.g.
              `{"model": "gpt-4o", "tokens": 512}`, or `None` if the line has no usage info

            **Rules**
            - Usage info is `model=`, the model name (one or more letters, digits, `.`, `_` or
              `-`), one or more spaces, `tokens=`, then one or more digits. It may appear
              anywhere in the line.
            - `"tokens"` is an `int`, not a string.
            - Use **named groups** `(?P<name>...)` in your pattern (a check looks for `(?P<`).
            - No match (e.g. `tokens` missing or not a number): return `None`.

            **Examples**
            ```python
            parse_usage("ts=17:02 model=gpt-4o tokens=512 status=ok")
            # returns {"model": "gpt-4o", "tokens": 512}
            parse_usage("model=claude-3.5_x  tokens=7")   # returns {"model": "claude-3.5_x", "tokens": 7}
            parse_usage("model=gpt-4o tokens=many")       # returns None
            ```
        ''',
        "starter": r'''
            import re


            def parse_usage(line):
                ...
        ''',
        "tests": r'''
            from solution import parse_usage

            def test_parses_model_and_tokens_anywhere_in_line():
                got = parse_usage("ts=17:02 model=gpt-4o tokens=512 status=ok")
                assert got == {"model": "gpt-4o", "tokens": 512}, f"got {got!r}"

            def test_tokens_is_an_int():
                got = parse_usage("model=m tokens=42")
                assert got is not None and isinstance(got["tokens"], int), f"got {got!r}"

            def test_dots_underscores_and_several_spaces():
                got = parse_usage("model=claude-3.5_x  tokens=7")
                assert got == {"model": "claude-3.5_x", "tokens": 7}, f"got {got!r}"

            def test_no_usage_info_returns_none():
                assert parse_usage("model=gpt-4o tokens=many") is None
                assert parse_usage("status=ok") is None

            def test_uses_named_groups():
                assert "(?P<" in source(), "use named groups (?P<name>...)"
        ''',
        "solution": r'''
            import re

            USAGE = re.compile(r"model=(?P<model>[\w.-]+) +tokens=(?P<tokens>\d+)")


            def parse_usage(line):
                m = USAGE.search(line)
                if m is None:
                    return None
                return {"model": m.group("model"), "tokens": int(m.group("tokens"))}
        ''',
        "hints": [
            "Use `re.search` with a pattern that has two named groups, one for the model and one for the number.",
            "Describe it left to right: literal `model=`, a named group for the name characters, spaces, literal `tokens=`, a named group of digits. Return None when search fails.",
            r"1) Pattern: `model=(?P<model>[\w.-]+) +tokens=(?P<tokens>\d+)`-style. 2) `m = re.search(pattern, line)`. 3) If `m is None`, return None. 4) Return a dict with `m.group(\"model\")` and `int(m.group(\"tokens\"))`.",
        ],
    },
    {
        "id": "regex-9",
        "title": "Errors at the start of a line",
        "difficulty": 1,
        "lesson": r'''
            *Anchors* match a **position**, not a character: `^` is "the start", `$` is "the end".
            By default that means the start and end of the **whole** string. A *flag* changes how the
            pattern engine behaves - think of it as a settings switch. Two you'll use a lot:

            - `re.MULTILINE`: `^` and `$` now also match at the start/end of **every line**.
            - `re.IGNORECASE`: letters match in any case.

            ```python
            import re

            log = "INFO: start\nWARN: slow\nINFO: done"
            print(re.findall(r"^INFO: (\w+)$", log))
            print(re.findall(r"^INFO: (\w+)$", log, flags=re.MULTILINE))
            print(re.findall(r"warn", log, flags=re.IGNORECASE))
            ```

            Without the flag, `^INFO` can only match the very first characters of the text. With it,
            every line gets its own start and end - perfect for logs and multi-line model output.

            Also notice: with **one** group in the pattern, `findall` returns just that group's text for
            each match, not the whole line. Combine several flags with `|`, e.g.
            `re.MULTILINE | re.IGNORECASE`.
        ''',
        "prompt": r'''
            An agent's log has one event per line. Collect the error messages.

            **Write:** `error_messages(log)`

            - `log`: a `str`, lines separated by `"\n"`, e.g. `"INFO: ok\nERROR: disk full"`
            - **Returns:** a `list` of strings: for each line that **starts** with `ERROR:`,
              the rest of that line after `ERROR:` and any spaces following it, in order

            **Rules**
            - `ERROR:` must be at the very start of the line (upper case). Lines like
              `"  ERROR: x"` (indented) or `"see ERROR: x"` don't count.
            - The message may be empty: `"ERROR:"` alone gives `""`.
            - Use `re.findall` with the `re.MULTILINE` flag (a check looks for `MULTILINE`).
            - No error lines: return `[]`.

            **Examples**
            ```python
            error_messages("INFO: ok\nERROR: disk full\nERROR:timeout")   # returns ["disk full", "timeout"]
            error_messages("see ERROR: x\n  ERROR: y")                    # returns []
            error_messages("ERROR:\nINFO: ok")                            # returns [""]
            ```
        ''',
        "starter": r'''
            import re


            def error_messages(log):
                ...
        ''',
        "tests": r'''
            from solution import error_messages

            def test_collects_messages_from_error_lines():
                got = error_messages("INFO: ok\nERROR: disk full\nWARN: slow\nERROR:timeout")
                assert got == ["disk full", "timeout"], f"got {got!r}"

            def test_error_must_start_the_line():
                got = error_messages("see ERROR: x\n  ERROR: y\nINFO: ERROR: z")
                assert got == [], f"got {got!r}"

            def test_empty_message_and_no_errors():
                assert error_messages("ERROR:\nINFO: ok") == [""]
                assert error_messages("INFO: all good") == []

            def test_messages_do_not_run_into_the_next_line():
                got = error_messages("ERROR: first\nsecond line")
                assert got == ["first"], f"got {got!r}"

            def test_uses_multiline_flag():
                assert "MULTILINE" in source(), "use the re.MULTILINE flag"
        ''',
        "solution": r'''
            import re


            def error_messages(log):
                return re.findall(r"^ERROR:[ \t]*(.*)$", log, flags=re.MULTILINE)
        ''',
        "hints": [
            r"`^` anchors to the start of a line only when you pass `re.MULTILINE`; one group makes `findall` return just the captured part.",
            "Pattern: start-of-line anchor, the literal `ERROR:`, optional spaces, then capture the rest of the line up to the end-of-line anchor.",
            r"1) Pattern `^ERROR:[ \t]*(.*)$` (`.` never crosses a newline). 2) `re.findall(pattern, log, flags=re.MULTILINE)`. 3) Return the list.",
        ],
    },
    {
        "id": "regex-3",
        "hints": [
            'You need named or numbered groups, the `^`/`$` anchors and the `re.MULTILINE` flag so they work per line.',
            'Match a whole line: optional spaces, `Action:`, optional spaces, an identifier group, `[`, a greedy group for the input, `]`, optional trailing spaces, end of line. Use `re.search` to get the first one.',
            '1) Compile with `re.MULTILINE`. 2) Use `[ \\t]*` for spaces (not `\\s`, which crosses lines). 3) Identifier: `[A-Za-z_]\\w*`. 4) Input: `.*` between `\\[` and `\\]` (greedy, so it reaches the last `]`). 5) Return `None` if no match, else the two groups with the input `.strip()`ed.',
        ],
        "title": "Parse a ReAct action",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A ReAct-style agent writes its tool calls as lines like
            `Action: search[weather in Paris]`. Your code must find that line in the model's
            multi-line output and pull out which tool to call and with what input.

            **Write:** `parse_action(text)`

            - `text`: a `str`, the model output, possibly several lines separated by `"\n"`
            - **Returns:** a tuple `(tool_name, tool_input)` of two strings, e.g.
              `("search", "weather in Paris")`, or `None` if there is no valid action line

            **Rules**
            - An action line is: optional spaces at the start of the line, `Action:`, optional
              spaces, the tool name, `[`, the input, `]`, optional spaces, end of the line.
            - `Action:` in the middle of a line (after other text) does **not** count.
            - The tool name is an identifier: letters, digits and `_`, not starting with a digit,
              no spaces. `9tool` or `web search` make the line invalid.
            - The input is everything between the `[` right after the name and the **last** `]`
              on that same line (it may contain brackets itself), with surrounding whitespace stripped.
            - If there are several action lines, use the **first** one. The match must stay on
              one line.
            - Empty text or no action line: return `None`.

            **Examples**
            ```python
            out = "Thought: I need the weather.\nAction: search[weather in Paris]\nObservation: sunny"
            parse_action(out)                              # returns ("search", "weather in Paris")
            parse_action("Action: calc[ (2+3)*[4] ]")       # returns ("calc", "(2+3)*[4]")
            parse_action("  Action:lookup_user[id=7]\nAction: other[x]")   # returns ("lookup_user", "id=7")
            parse_action("I will use Action: search[x] later")             # returns None
            parse_action("Final Answer: 42")               # returns None
            ```
        ''',
        "starter": r'''
            import re


            def parse_action(text):
                ...
        ''',
        "tests": r'''
            from solution import parse_action

            def test_finds_action_line_in_multiline_output():
                out = "Thought: I need the weather.\nAction: search[weather in Paris]\nObservation: sunny"
                got = parse_action(out)
                assert got == ("search", "weather in Paris"), f"got {got!r}"

            def test_input_runs_to_last_bracket_and_is_stripped():
                got = parse_action("Action: calc[ (2+3)*[4] ]")
                assert got == ("calc", "(2+3)*[4]"), f"got {got!r}"

            def test_no_action_line_returns_none():
                assert parse_action("Final Answer: 42") is None
                assert parse_action("") is None

            def test_first_action_wins_and_leading_spaces_allowed():
                out = "  Action:lookup_user[id=7]\nAction: other[x]"
                got = parse_action(out)
                assert got == ("lookup_user", "id=7"), f"got {got!r}"

            def test_action_in_middle_of_line_does_not_count():
                out = "I will use Action: search[x] later\nThought: done"
                assert parse_action(out) is None, "Action: must start the line"

            def test_invalid_tool_name_returns_none():
                assert parse_action("Action: 9tool[x]") is None
                assert parse_action("Action: web search[x]") is None
        ''',
        "solution": r'''
            import re

            ACTION = re.compile(r"^[ \t]*Action:[ \t]*(?P<tool>[A-Za-z_]\w*)\[(?P<input>.*)\][ \t]*$", re.MULTILINE)


            def parse_action(text):
                m = ACTION.search(text)
                if m is None:
                    return None
                return m["tool"], m["input"].strip()
        ''',
    },
    {
        "id": "regex-4",
        "research": {
            "note": "Two things here go beyond the lessons: passing a *function* as the replacement to `re.sub`, and a lookbehind `(?<!...)` that checks what comes before a match. Read about both, then come back.",
            "links": [
                {"title": "re.sub - Python docs", "url": "https://docs.python.org/3/library/re.html#re.sub"},
                {"title": "Regular expression syntax (lookbehind) - Python docs", "url": "https://docs.python.org/3/library/re.html#regular-expression-syntax"},
            ],
        },
        "hints": [
            'Use two `re.sub` calls; for the API key, pass a function as the replacement so you can use the matched text.',
            'For keys, use a negative lookbehind `(?<!...)` so `sk-` inside words like `task-` is not matched. For bearer tokens, capture the `Authorization: Bearer ` part in a group and keep it in the replacement.',
            "1) Key pattern: a lookbehind saying 'not preceded by a letter, digit or underscore', then the literal `sk-`, then the allowed characters repeated at least 16 times. 2) Replacement function: build the masked text from the matched string's last 4 characters. 3) Bearer pattern: capture the header words and the spaces after them in a group (any case), then match the token as a run of non-whitespace. 4) In the replacement, refer back to that group and add `[REDACTED]`.",
        ],
        "title": "Redact secrets from logs",
        "difficulty": 2,
        "prompt": r'''
            Request logs of an LLM app must never store API keys or auth tokens. Mask them
            before the log is written.

            **Write:** `redact(log)`

            - `log`: a `str`, possibly several lines, e.g. `"key=sk-abcdefghijklmnop1234 ok"`
            - **Returns:** a `str`: the same text with every secret masked and everything else unchanged

            **Rules**
            - **API key:** `sk-` followed by **16 or more** characters that are letters, digits,
              `_` or `-`. Replace the whole key with `sk-****` plus the key's **last 4 characters**.
            - It only counts as a key if the `sk-` is **not** directly preceded by a letter, digit
              or `_` - so `task-...` and `risk-...` are left alone. Fewer than 16 characters
              (`sk-short`) is left alone.
            - Mask **every** key in the log, not just the first.
            - **Bearer token:** `Authorization:` then spaces then `Bearer` then spaces then a token
              (a run of non-whitespace characters). The words may be in any letter case
              (`authorization:  bearer ...`). Keep the header text exactly as written (same case,
              same spaces) and replace only the token with `[REDACTED]`.
            - Works on every line of a multi-line log.

            **Examples**
            ```python
            redact("key=sk-abcdefghijklmnop1234 ok")         # returns "key=sk-****1234 ok"
            redact("a sk-proj-AAAAAAAAAAAAAAAA_zz9 b")       # returns "a sk-****_zz9 b"
            redact("authorization:  bearer eyJhbGciOi.xyz rest")
            # returns "authorization:  bearer [REDACTED] rest"
            redact("run task-list-abcdefghijklmnopqr")       # returned unchanged
            ```
        ''',
        "starter": r'''
            import re


            def redact(log):
                ...
        ''',
        "tests": r'''
            from solution import redact

            def test_api_key_masked_keeping_last_4():
                got = redact("key=sk-abcdefghijklmnop1234 ok")
                assert got == "key=sk-****1234 ok", f"got {got!r}"

            def test_multiple_keys_each_masked():
                log = "a sk-proj-AAAAAAAAAAAAAAAA_zz9 b sk-BBBBBBBBBBBBBBBBqrst"
                got = redact(log)
                assert got == "a sk-****_zz9 b sk-****qrst", f"got {got!r}"

            def test_short_keys_and_sk_inside_words_unchanged():
                for log in ("sk-short", "run task-list-abcdefghijklmnopqr", "risk-abcdefghijklmnopqrstu"):
                    assert redact(log) == log, f"{log!r} was changed to {redact(log)!r}"

            def test_bearer_token_redacted_in_any_case():
                got = redact("authorization:  bearer eyJhbGciOi.xyz rest")
                assert got == "authorization:  bearer [REDACTED] rest", f"got {got!r}"
                got = redact("Authorization: Bearer abc123")
                assert got == "Authorization: Bearer [REDACTED]", f"got {got!r}"

            def test_multiline_log_redacts_every_line():
                log = "GET /v1 200\nAuthorization: Bearer tok_1\nkey sk-1234567890abcdefWXYZ\ndone"
                got = redact(log)
                assert got == "GET /v1 200\nAuthorization: Bearer [REDACTED]\nkey sk-****WXYZ\ndone", f"got {got!r}"
        ''',
        "solution": r'''
            import re

            API_KEY = re.compile(r"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_-]{16,}")
            BEARER = re.compile(r"(authorization:\s*bearer\s+)\S+", re.IGNORECASE)


            def redact(log):
                log = API_KEY.sub(lambda m: "sk-****" + m.group()[-4:], log)
                return BEARER.sub(r"\1[REDACTED]", log)
        ''',
    },
    {
        "id": "regex-5",
        "hints": [
            "Split the job: one pattern that validates a line's prefix (timestamp + level), then a second pattern that finds `key=value` pairs.",
            'Use `finditer` with `re.MULTILINE` to go line by line, turn the pairs into a dict, check the required keys, then validate latency and tokens with `fullmatch`.',
            "1) Line pattern: a timestamp group, whitespace, a level group (case-insensitive), then the rest of the line as a repeated 'whitespace + key=value' part, anchored to the line end. 2) Pull the pairs out of the rest with `findall` and turn them into a dict. 3) Skip the line if `model` or `latency` is missing. 4) Check latency with `fullmatch` (a number with optional decimals, then a unit) and convert it to whole milliseconds with `round`. 5) If tokens is present it must be all digits. 6) Build the result dict with the level in upper case.",
        ],
        "title": "Parse usage logs",
        "difficulty": 3,
        "prompt": r'''
            To track cost and speed you parse the request logs of your LLM gateway. A log line
            looks like:

            ```
            2024-05-01T12:00:03Z info model=gpt-4o latency=532ms tokens=1234 status=200
            ```

            **Write:** `parse_log(text)`

            - `text`: a `str` with zero or more log lines separated by `"\n"`
            - **Returns:** a `list` of dicts, one per **valid** line, in order. Each dict has exactly
              these keys: `{"timestamp": str, "level": str, "model": str, "latency_ms": int, "tokens": int | None}`

            **Rules**
            - A valid line starts with a UTC timestamp in exactly the form `YYYY-MM-DDTHH:MM:SSZ`
              (e.g. `2024-05-01T12:00:03Z`; `2024-05-01 12:00:08` is invalid), then whitespace,
              then a level: `debug`, `info`, `warn` or `error` in any letter case (`trace` is invalid).
            - After the level come zero or more `key=value` pairs separated by whitespace, in
              **any order**. Values contain no whitespace.
            - `model` and `latency` are required; a line missing either is skipped.
            - `latency` is a number (optionally with a decimal part) followed by `ms` or `s`,
              e.g. `532ms`, `1.2s`. Convert it to **whole milliseconds** with `round()`
              (`1.2s` -> `1200`, `0.0004s` -> `0`). Any other form (e.g. `fast`) skips the line.
            - `tokens` is optional: all digits -> an `int`; absent -> `None`; anything else
              (e.g. `many`) skips the line.
            - `"level"` in the result is upper case (`"info"` -> `"INFO"`).
            - Other keys (`status`, `user`, ...) are ignored and do not appear in the result.
            - Empty text: return `[]`.

            **Examples**
            ```python
            parse_log("2024-05-01T12:00:03Z info model=gpt-4o latency=532ms tokens=1234 status=200")
            # returns [{"timestamp": "2024-05-01T12:00:03Z", "level": "INFO", "model": "gpt-4o",
            #           "latency_ms": 532, "tokens": 1234}]
            parse_log("2024-05-01T12:00:03Z INFO latency=1.2s model=claude")
            # returns [{"timestamp": "2024-05-01T12:00:03Z", "level": "INFO", "model": "claude",
            #           "latency_ms": 1200, "tokens": None}]
            parse_log("2024-05-01T12:00:05Z Warn model=gpt-4o-mini status=429")
            # returns []  (no latency)
            ```
        ''',
        "starter": r'''
            import re


            def parse_log(text):
                ...
        ''',
        "tests": r'''
            from solution import parse_log

            LOG = """2024-05-01T12:00:03Z info model=gpt-4o latency=532ms tokens=1234 status=200
            2024-05-01T12:00:04Z INFO latency=1.2s model=claude
            garbage line model=x latency=1ms
            2024-05-01T12:00:05Z Warn model=gpt-4o-mini status=429
            2024-05-01T12:00:06Z error model=m latency=fast
            2024-05-01T12:00:07Z debug user=ana tokens=7 model=llama-3.1 latency=0.0004s
            2024-05-01 12:00:08 INFO model=m latency=3ms
            2024-05-01T12:00:09Z trace model=m latency=3ms
            2024-05-01T12:00:10Z info model=m latency=3ms tokens=many
            """

            def test_full_line_parsed_into_dict():
                got = parse_log(LOG)[0]
                assert got == {"timestamp": "2024-05-01T12:00:03Z", "level": "INFO", "model": "gpt-4o",
                               "latency_ms": 532, "tokens": 1234}, f"got {got!r}"

            def test_keys_in_any_order_seconds_converted_tokens_none():
                got = parse_log(LOG)[1]
                assert got == {"timestamp": "2024-05-01T12:00:04Z", "level": "INFO", "model": "claude",
                               "latency_ms": 1200, "tokens": None}, f"got {got!r}"

            def test_invalid_lines_are_skipped():
                got = [r["timestamp"] for r in parse_log(LOG)]
                assert got == ["2024-05-01T12:00:03Z", "2024-05-01T12:00:04Z", "2024-05-01T12:00:07Z"], \
                    f"parsed lines with timestamps {got}"

            def test_latency_rounded_and_unknown_keys_ignored():
                got = parse_log(LOG)[2]
                assert got["latency_ms"] == 0 and got["tokens"] == 7 and got["model"] == "llama-3.1", f"got {got!r}"
                assert got["level"] == "DEBUG"
                assert set(got) == {"timestamp", "level", "model", "latency_ms", "tokens"}, f"keys: {sorted(got)}"

            def test_empty_text_returns_empty_list():
                assert parse_log("") == []
        ''',
        "solution": r'''
            import re

            LINE = re.compile(r"""
                ^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)
                \s+(?P<level>debug|info|warn|error)
                (?P<rest>(?:\s+\S+=\S+)*)\s*$
            """, re.VERBOSE | re.IGNORECASE | re.MULTILINE)
            PAIR = re.compile(r"(\S+?)=(\S+)")
            LATENCY = re.compile(r"(?P<num>\d+(?:\.\d+)?)(?P<unit>ms|s)")


            def parse_log(text):
                records = []
                for m in LINE.finditer(text):
                    pairs = dict(PAIR.findall(m["rest"]))
                    if "model" not in pairs or "latency" not in pairs:
                        continue
                    lat = LATENCY.fullmatch(pairs["latency"])
                    tokens = pairs.get("tokens")
                    if lat is None or (tokens is not None and not re.fullmatch(r"\d+", tokens)):
                        continue
                    factor = 1 if lat["unit"] == "ms" else 1000
                    records.append({
                        "timestamp": m["timestamp"],
                        "level": m["level"].upper(),
                        "model": pairs["model"],
                        "latency_ms": round(float(lat["num"]) * factor),
                        "tokens": int(tokens) if tokens is not None else None,
                    })
                return records
        ''',
    },
    {
        "id": "regex-6",
        "hints": [
            '`re.sub` with a replacement FUNCTION processes each placeholder once and never re-scans the replaced text.',
            'Write one pattern with named groups for the variable name and an optional filter; inside the replacement function, look the value up, apply the filter, and raise on unknown filters.',
            '1) Pattern: escaped double braces on each side; inside them optional spaces/tabs, a name group (letter or underscore first, then word characters), and an optional non-capturing part with a pipe and a named filter group. Use `[ \\t]` rather than `\\s` so it stays on one line. 2) In the replacement function, look the name up in `variables` and convert it with `str` (a missing name raises KeyError by itself). 3) Keep a dict from filter names to string methods and raise ValueError for unknown ones. 4) Return the result of `sub` with that function.',
        ],
        "title": "Prompt template engine",
        "difficulty": 3,
        "prompt": r'''
            Prompt templates keep your prompts out of your code. Build a tiny template engine
            that fills in placeholders like `{{ name }}` or `{{name|upper}}`.

            **Write:** `render(template, variables)`

            - `template`: a `str`, e.g. `"Hi {{ name }}! Topic: {{topic|upper}}"`
            - `variables`: a `dict` from names to values, e.g. `{"name": "Ana", "topic": "rag"}`
            - **Returns:** a `str`: the template with every valid placeholder replaced

            **Rules**
            - A valid placeholder is `{{`, optional spaces/tabs, a name, optionally `|` and a filter
              name (spaces allowed around the `|`), optional spaces/tabs, `}}` - all on **one line**.
            - A name starts with a letter or `_`, followed by letters, digits or `_`.
            - The replacement is `str(variables[name])`, so numbers work too (`3` -> `"3"`,
              `0.2` -> `"0.2"`). The value itself is inserted as-is (its own spaces are kept).
            - Filters: `upper`, `lower`, `strip` (the string methods of the same name) are applied
              to the value. Any other filter name raises `ValueError`.
            - A name missing from `variables` raises `KeyError`.
            - Anything that is not a valid placeholder is left untouched: `{{ 1x }}`, `{ x }`,
              `{{ a b }}`, or braces split over two lines.
            - Inserted values are never scanned again for placeholders.

            **Examples**
            ```python
            render("Hi {{ name }}! Topic: {{topic|upper}}", {"name": "Ana", "topic": "rag"})
            # returns "Hi Ana! Topic: RAG"
            render("[{{ x | lower }}][{{x|strip}}]", {"x": "  AbC "})   # returns "[  abc ][AbC]"
            render("{{ 1x }} {{x}}", {"x": "ok"})                        # returns "{{ 1x }} ok"
            render("{{ q }}", {"q": "{{ name }}", "name": "X"})          # returns "{{ name }}"
            render("{{ x | title }}", {"x": "a"})                        # raises ValueError
            ```
        ''',
        "starter": r'''
            import re


            def render(template, variables):
                ...
        ''',
        "tests": r'''
            from solution import render

            def test_replaces_placeholders_and_applies_filter():
                got = render("Hi {{ name }}! Topic: {{topic|upper}}", {"name": "Ana", "topic": "rag"})
                assert got == "Hi Ana! Topic: RAG", f"got {got!r}"

            def test_spaces_inside_braces_and_all_three_filters():
                t = "[{{x}}][{{  x  }}][{{ x | lower }}][{{x|strip}}]"
                got = render(t, {"x": "  AbC "})
                assert got == "[  AbC ][  AbC ][  abc ][AbC]", f"got {got!r}"

            def test_non_string_values_converted_with_str():
                got = render("n={{ n }}, t={{ t }}", {"n": 3, "t": 0.2})
                assert got == "n=3, t=0.2", f"got {got!r}"

            def test_invalid_placeholders_left_untouched():
                t = "{{ 1x }} { x } {{ a b }} {{\nx }} {{x}}"
                got = render(t, {"x": "ok", "a": "A"})
                assert got == "{{ 1x }} { x } {{ a b }} {{\nx }} ok", f"got {got!r}"

            def test_inserted_values_not_rescanned():
                got = render("{{ q }}", {"q": "{{ name }}", "name": "X"})
                assert got == "{{ name }}", f"got {got!r}"

            def test_missing_variable_key_error_unknown_filter_value_error():
                try:
                    render("{{ missing }}", {})
                    assert False, "missing variable should raise KeyError"
                except KeyError:
                    pass
                try:
                    render("{{ x | title }}", {"x": "a"})
                    assert False, "unknown filter should raise ValueError"
                except ValueError:
                    pass
        ''',
        "solution": r'''
            import re

            PLACEHOLDER = re.compile(
                r"\{\{[ \t]*(?P<name>[A-Za-z_]\w*)[ \t]*(?:\|[ \t]*(?P<filter>\w+)[ \t]*)?\}\}"
            )
            FILTERS = {"upper": str.upper, "lower": str.lower, "strip": str.strip}


            def render(template, variables):
                def replace(m):
                    value = str(variables[m["name"]])
                    flt = m["filter"]
                    if flt is None:
                        return value
                    if flt not in FILTERS:
                        raise ValueError(f"unknown filter: {flt}")
                    return FILTERS[flt](value)

                return PLACEHOLDER.sub(replace, template)
        ''',
    },
]
