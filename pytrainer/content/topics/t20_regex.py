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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["regex", "regular expression", "pattern", "re", "search", "findall", "fullmatch",
                 "sub", "match", "group", "named group", "flag", "multiline", "compile",
                 "validate", "raw string"],
    "cards": [
        {
            "syntax": 're.search(r"pattern", text)',
            "explain": "Returns a match object for the first match anywhere in text, or None. m.group() is the matched text.",
            "example": r'''
                import re
                m = re.search(r"\d+", "cost 30 usd")
                print(m.group(), m.start(), m.end())
                # 30 5 7
                print(re.search(r"\d+", "no digits"))
                # None
            ''',
        },
        {
            "syntax": 're.findall(r"pattern", text)',
            "explain": "Returns a list of every match as strings, in order. With one group it returns the group's text. No match gives [].",
            "example": r'''
                import re
                print(re.findall(r"\d+", "used 1200 tokens in 3 calls"))
                # ['1200', '3']
                print(re.findall(r"#(\w+)", "#ai and #ml"))
                # ['ai', 'ml']
            ''',
        },
        {
            "syntax": 're.fullmatch(r"pattern", text) is not None',
            "explain": "True only when the pattern matches the whole string. Use it to check the format of an input.",
            "example": r'''
                import re
                for text in ["ID-042", "my ID-042", "ID-42"]:
                    print(text, re.fullmatch(r"ID-\d{3}", text) is not None)
                # ID-042 True
                # my ID-042 False
                # ID-42 False
            ''',
        },
        {
            "syntax": 'm.group(1)  /  m.group("name")',
            "explain": "Parentheses make a group that stores part of the match. (?P<name>...) gives the group a name.",
            "example": r'''
                import re
                m = re.search(r"(?P<key>\w+)=(?P<value>\d+)", "set max_tokens=512")
                print(m.group(0))
                # max_tokens=512
                print(m.group(1), int(m.group("value")))
                # max_tokens 512
            ''',
        },
        {
            "syntax": 're.sub(r"pattern", replacement, text)',
            "explain": "Returns a new string with every match replaced. The original string does not change.",
            "example": r'''
                import re
                print(re.sub(r"\s+", " ", "too    many\n spaces"))
                # too many spaces
                print(re.sub(r"\d", "#", "call 555-1234"))
                # call ###-####
            ''',
        },
        {
            "syntax": "flags=re.MULTILINE | re.IGNORECASE",
            "explain": "MULTILINE makes ^ and $ match at the start and end of every line. IGNORECASE matches letters in either case.",
            "example": r'''
                import re
                log = "ERROR: a\nINFO: b\nerror: c"
                print(re.findall(r"^ERROR: (.*)$", log, flags=re.MULTILINE))
                # ['a']
                both = re.MULTILINE | re.IGNORECASE
                print(re.findall(r"^ERROR: (.*)$", log, flags=both))
                # ['a', 'c']
            ''',
        },
    ],
}

LESSON = r'''
## Regular expressions: chapter notes

A **regular expression** (or **regex**) is a string that describes which characters to look
for in a text. That string is called the **pattern**. The `re` module searches text with
patterns. Write every pattern as a **raw string**: put `r` before the opening quote, as in `r"..."`.
A raw string keeps each backslash as written, so `re` receives it unchanged.

## A match is a span of indexes

In a pattern, `\d` matches one digit and `+` means one or more of the item before it. So
`\d+` matches one or more digits in a row.

`re.search(pattern, text)` tries the pattern at index 0, then index 1, and so on. At the
first index where the pattern matches, it returns a **match object**. If no index matches,
it returns `None`. A **span** is the range of indexes that a match covers.

```python
import re

text = "cost 30 usd"
m = re.search(r"\d+", text)
print(m.start(), m.end())
# 5 7
print(text[m.start():m.end()])
# 30
print(m.group())
# 30
```

`m.start()` is the index of the first matched character. `m.end()` is the index after the
last one. `m.group()` returns the same string as `text[m.start():m.end()]`.

Drag the handles to other indexes to see which characters a span covers.

```diagram
{"type":"slice","title":"The span matched by \\d+ in text","name":"text","value":"cost 30 usd","start":5,"stop":7}
```

## Functions

- `re.search(p, s)` returns a match object for the first match anywhere in `s`, or `None`.
- `re.match(p, s)` tries the pattern at index 0 only. It returns a match object or `None`.
- `re.fullmatch(p, s)` succeeds only when the pattern matches all of `s`. Use it to validate input.
- `re.findall(p, s)` returns a list of every match. Each item is a string.
- `re.sub(p, repl, s)` returns a new string with every match replaced by `repl`. `repl` can be a string or a function.
- `re.split(p, s)` returns a list of the pieces of `s` between the matches.
- `re.compile(p, flags)` returns a pattern object with the same methods, so you can reuse one pattern.

```python
import re

print(re.findall(r"\d+", "used 1200 tokens in 3 calls"))
# ['1200', '3']
print(re.sub(r"\s+", " ", "too    many   spaces"))
# too many spaces
print(re.split(r",\s*", "gpt-4o, claude,llama"))
# ['gpt-4o', 'claude', 'llama']
print(re.fullmatch(r"\d{4}", "2024") is not None)
# True
```

## Pattern syntax

- `\d` matches one digit. `\w` matches one letter, digit or `_`. `\s` matches one whitespace character.
- `.` matches any character except a newline. `\.` matches a real dot.
- `[a-z0-9_-]` matches one character from the set. `[^0-9]` matches one character that is not in the set.
- A **quantifier** says how many times the item before it repeats. `+` is 1 or more, `*` is 0 or more, `?` is 0 or 1, `{4}` is exactly 4, `{2,}` is 2 or more, `{20,48}` is 20 to 48.
- An **anchor** matches a position instead of a character. `^` is the start of the string and `$` is the end.

## Groups

Parentheses create a **capturing group**: the match object stores the text that this part
of the pattern matched. `m.group(1)` returns the first group. `(?P<name>...)` gives a group
a name, and `m.group("name")` returns it. `(?:...)` groups items without capturing.

```python
import re

m = re.search(r"(?P<key>\w+)=(?P<value>\d+)", "set max_tokens=512 now")
print(m.group(0))
# max_tokens=512
print(m.group("key"), int(m.group("value")))
# max_tokens 512
```

## Flags

A **flag** is an extra argument that changes how the pattern is applied. `re.IGNORECASE`
makes letters match in either case. `re.MULTILINE` makes `^` and `$` also match at the start
and end of every line. (`re.VERBOSE` lets you put spaces and comments inside the
pattern. This chapter does not use it.)

```python
import re

log = "ERROR: a\nINFO: b\nERROR: c"
print(re.findall(r"^ERROR: (.*)$", log, flags=re.MULTILINE))
# ['a', 'c']
```

The pattern has one group, so `findall` returns the group's text for each match. `.*` is
any run of characters up to the end of the line.

## Common mistakes

- In a pattern, `\b` matches the position at the edge of a word. `"\b"` without the `r` prefix is one backspace character instead. Always write `r"..."`.
- `.` matches any character, so `a.b` also matches `axb`. Write `\.` for a real dot.
- `re.match` only tries index 0. Use `re.search` to look anywhere and `re.fullmatch` to validate.
- A group changes what `findall` returns: you get the group's text, not the whole match. Leave the group out, or use `(?:...)`, to get whole matches.
- `m.group()` raises `AttributeError` when `m` is `None`. Check `m is not None` first.
'''

EXERCISES = [
    {
        "id": "regex-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            ## Patterns and `re.search`

            A **regular expression** (or **regex**) is a string that describes which characters to look
            for in a text. That string is called the **pattern**. The `re` module in the standard
            library searches text with patterns.

            In a pattern, `\d` matches one digit. A `+` after an item means "one or more of that item".
            So `\d+` matches one or more digits in a row. The example writes the pattern as
            `r"\d+"`. The `r` before the quote is explained at the end of this step.

            ```python
            import re

            text = "Model v4 costs 30 dollars"
            m = re.search(r"\d+", text)
            print(m.group())
            # 4
            print(re.findall(r"\d+", text))
            # ['4', '30']
            ```

            `re.search(pattern, text)` finds the **first** match. It returns a **match object**: a value
            that records which part of the text matched. `m.group()` returns the matched text as a string.

            `re.findall(pattern, text)` returns **every** match as a list of strings.

            Step through the stages to see how `re.search` finds the `4`.

            ```diagram
            {"type":"flow","title":"How re.search scans the text","steps":[
            {"label":"Start at index 0","detail":"re.search receives the pattern and the text. It begins at index 0 of the text.","code":"re.search(r\"\\d+\", \"Model v4 costs 30 dollars\")"},
            {"label":"Try the pattern","detail":"It checks whether the pattern matches starting at the current index. \\d needs a digit at that index.","code":"index 0: 'M' is not a digit"},
            {"label":"No match: advance","detail":"The attempt fails, so re.search moves to the next index and tries again. Indexes 0 to 6 all fail. If no index is left, it returns None.","code":"index 1: 'o'\nindex 2: 'd'\n...\nindex 6: 'v'"},
            {"label":"Match at index 7","detail":"The character at index 7 is the digit 4, so \\d matches. The + tries to match more digits. Index 8 holds a space, so the match ends there.","code":"index 7: '4' is a digit\nindex 8: ' ' is not a digit"},
            {"label":"Return a match object","detail":"re.search stops and returns a match object for the span from index 7 to index 8. It never reaches the 30.","code":"<re.Match object; span=(7, 8), match='4'>"}
            ],"loop":{"from":2,"to":1,"label":"until the pattern matches or the text ends"}}
            ```

            Write the pattern as a **raw string**: put `r` before the opening quote. In a normal
            string Python reads a backslash and the next character as one special character:
            `"\n"` is a newline. In a raw string Python keeps every backslash as written, so `re`
            receives `\d` unchanged.
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
            ## `re.findall`

            `re.findall(pattern, text)` scans the text from left to right. It returns a list of every
            part of the text that matches the pattern, in the order the matches appear.

            ```python
            import re

            log = "latency 120ms, 85ms, 240ms"
            print(re.findall(r"\d+", log))
            # ['120', '85', '240']
            ```

            Each item in the list is a string, even when it contains only digits. Call `int()` on an
            item when you need a number.

            ```python
            import re

            numbers = re.findall(r"\d+", "latency 120ms, 85ms, 240ms")
            print(int(numbers[0]) + int(numbers[1]))
            # 205
            ```

            When nothing matches, `findall` returns an empty list, not `None`. A `for` loop over an
            empty list runs zero times, so you can loop over the result without a check.

            ```python
            import re

            print(re.findall(r"\d+", "no numbers"))
            # []
            ```

            Matches do not overlap. After a match ends, the scan continues at the index where that
            match ended.

            `re.search` stops at the first match and returns a match object. Use `findall` when you
            need all the matches.
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
            ## Where the pattern must match

            Three functions take the same arguments, a pattern and a text. They differ in where the
            pattern is allowed to match.

            - `re.match` tries the pattern at index 0 only.
            - `re.search` tries every index and stops at the first match.
            - `re.fullmatch` succeeds only when the pattern matches the whole string, from index 0 to the end.

            ```python
            import re

            text = "use model v2 today"
            print(re.match(r"v\d", text))
            # None
            print(re.search(r"v\d", text).group())
            # v2
            print(re.fullmatch(r"v\d", text))
            # None
            print(re.fullmatch(r"v\d", "v2").group())
            # v2
            ```

            Each function returns a match object when it succeeds and `None` when it fails. The
            comparison `result is not None` turns that result into `True` or `False`.

            ```python
            import re

            text = "use model v2 today"
            print(re.search(r"v\d", text) is not None)
            # True
            print(re.match(r"v\d", text) is not None)
            # False
            ```

            The name `re.match` does not mean "find a match anywhere". `re.match(r"v\d", text)` returns
            `None` here because the text starts with `u`, not `v`.
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
            ## Validation with `re.fullmatch`

            To **validate** a string is to check that the whole string has an expected format.
            `re.fullmatch(pattern, text)` does this. It returns a match object only when the pattern
            matches every character of the text, from the first to the last.

            ```python
            import re

            print(re.fullmatch(r"\d{3}", "123") is not None)
            # True
            print(re.fullmatch(r"\d{3}", "1234") is not None)
            # False
            print(re.fullmatch(r"ID-\d{3}", "ID-042") is not None)
            # True
            print(re.fullmatch(r"ID-\d{3}", "my ID-042") is not None)
            # False
            print(re.fullmatch(r"ID-\d{3}", "id-042") is not None)
            # False
            ```

            A **quantifier** is a part of a pattern that says how many times the item before it
            repeats. `{3}` means exactly 3 times, so `\d{3}` matches exactly 3 digits.

            A **literal** is a character in a pattern that matches itself. The letters `I` and `D` and
            the `-` are literals here. Literals are case-sensitive, so `ID` does not match `id`.

            `re.search` is the wrong function for validation. It accepts a string that has extra
            characters around the match.

            ```python
            import re

            print(re.search(r"\d{3}", "1234").group())
            # 123
            ```
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
            ## Character classes

            A **character class** is a set of characters in square brackets. It matches exactly one
            character, and that character must be in the set. `[aeiou]` matches one lower-case vowel.

            A `-` between two characters makes a range. `[a-z]` is any lower-case letter, `[A-Z]` any
            upper-case letter and `[0-9]` any digit. You can combine them: `[A-Za-z]` is any letter.

            ```python
            import re

            print(re.findall(r"[aeiou]", "prompt tokens"))
            # ['o', 'o', 'e']
            print(re.findall(r"[a-z]+", "abc DEF ghi"))
            # ['abc', 'ghi']
            ```

            Put a quantifier after the class to repeat it. `[A-Za-z]+` matches one or more letters in a
            row. The match ends at the first character that is not in the set.

            ```python
            import re

            text = "tags: #ai, #ML_ops, #2024!"
            print(re.findall(r"#[A-Za-z]+", text))
            # ['#ai', '#ML']
            print(re.findall(r"#\w+", text))
            # ['#ai', '#ML_ops', '#2024']
            ```

            Three classes have a short form:

            - `\d` matches one digit, the same as `[0-9]`.
            - `\w` matches one letter, digit or `_`.
            - `\s` matches one whitespace character: a space, a tab or a newline.

            `#[A-Za-z]+` stops at the `_` in `#ML_ops` and finds nothing in `#2024`, because `_` and
            digits are not in that set. `\w` includes them.
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
            ## Capturing groups

            A pair of parentheses in a pattern creates a **capturing group**. The match object stores
            the text that this part of the pattern matched, and you read it with `m.group(number)`.

            ```python
            import re

            text = "size 1024x768"
            m = re.search(r"(\d+)x(\d+)", text)
            print(m.group(0))
            # 1024x768
            print(m.group(1))
            # 1024
            print(m.group(2))
            # 768
            ```

            - `m.group(0)` is the whole match. `m.group()` with no argument returns the same string.
            - `m.group(1)` is the first group and `m.group(2)` is the second. Groups are numbered by
              their opening parenthesis, from left to right.

            Each group is a span of indexes in the text. `m.start(1)` is `5` and `m.end(1)` is `9`, so
            `m.group(1)` equals `text[5:9]`. Move the handles to `10` and `13` to see the span of group 2.

            ```diagram
            {"type":"slice","title":"The span of group 1 in text","name":"text","value":"size 1024x768","start":5,"stop":9}
            ```

            A group is always a string. Call `int()` on it before you do arithmetic.

            ```python
            import re

            m = re.search(r"(\d+)x(\d+)", "size 1024x768")
            print(int(m.group(1)) * int(m.group(2)))
            # 786432
            ```

            The parentheses do not change which text matches. `\d+x\d+` matches the same `1024x768`.
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
            ## Escaping and compiled patterns

            You build a longer pattern by writing the small parts one after another, left to right. The
            pattern below reads: a dollar sign, one or more digits, a dot, exactly 2 digits.

            ```python
            import re

            PRICE = re.compile(r"\$\d+\.\d{2}")
            print(PRICE.findall("was $19.99, now $9.50 (or 9.50?)"))
            # ['$19.99', '$9.50']
            ```

            ### Escaping

            Some characters have a special meaning in a pattern. `.` matches any character except a
            newline, and `$` matches the end of the text. To match the real character, put a backslash in front of it: `\.` and `\$`.
            This is called **escaping**.

            ```python
            import re

            print(re.findall(r"a.b", "a.b axb a-b"))
            # ['a.b', 'axb', 'a-b']
            print(re.findall(r"a\.b", "a.b axb a-b"))
            # ['a.b']
            ```

            Inside a character class most special characters are literals already. `[.%+]` matches one
            dot, one percent sign or one plus sign.

            ### `{2,}`

            The quantifier `{2,}` means 2 or more times.

            ```python
            import re

            print(re.findall(r"\d{2,}", "7 42 1200"))
            # ['42', '1200']
            ```

            ### `re.compile`

            `re.compile(pattern)` builds a **pattern object** once. The object has the same methods as
            the module: `.findall(text)`, `.search(text)`, `.fullmatch(text)`. Use it for a pattern that
            you apply many times. The usual place is a constant with an upper-case name at the top of
            the file.

            An unescaped `.` outside a class raises no error. It matches more than you intended:
            `v\d+.\d+` matches `v10x3` as well as `v1.2`.
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
            ## Range quantifiers

            The quantifier `{m,n}` means "between m and n times", with both ends included. `{3,5}`
            accepts 3, 4 or 5 repeats of the item before it.

            Combine it with `fullmatch` to check that a key or an id has the right format
            before you send it to an API (an API is a service your program sends requests to).

            ```python
            import re

            CODE = re.compile(r"ab-[a-z0-9_-]{3,5}")
            for text in ["ab-x1y", "ab-x1_-z", "ab-x1", "ab-x1y2z9"]:
                print(text, CODE.fullmatch(text) is not None)
            # ab-x1y True
            # ab-x1_-z True
            # ab-x1 False
            # ab-x1y2z9 False
            ```

            `ab-x1` has 2 characters after `ab-` and `ab-x1y2z9` has 6, so both fail.

            ### A hyphen inside a class

            Between two characters in a class, `-` makes a range such as `a-z`. To include a real
            hyphen in the set, put it last: `[a-z_-]`.

            ### Extra characters

            `fullmatch` rejects any extra character, including a newline `"\n"` at the end. A key that
            you read from a file often ends with that newline.

            ```python
            import re

            CODE = re.compile(r"ab-[a-z0-9_-]{3,5}")
            print(CODE.fullmatch("ab-x1y\n") is not None)
            # False
            ```

            This check is called **format validation**. It catches typing mistakes early. It cannot
            tell you that the key is accepted: only the API can do that.
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
            ## `re.sub`

            `re.sub(pattern, replacement, text)` returns a new string in which every match of the
            pattern is replaced by the replacement string. The arguments come in that order: pattern
            first, text last.

            ```python
            import re

            phone = "call 555-1234 or 555-9876"
            print(re.sub(r"\d", "#", phone))
            # call ###-#### or ###-####
            print(phone)
            # call 555-1234 or 555-9876
            ```

            `\d` has no quantifier, so each digit is one match and each is replaced by one `#`.
            `re.sub` does not change `phone`. A string cannot be changed after it is created, so
            `re.sub` builds and returns a new one.

            A quantifier makes one match cover several characters in a row. The whole match is replaced
            by one copy of the replacement.

            ```python
            import re

            print(re.sub(r"-+", "-", "a---b--c"))
            # a-b-c
            ```

            When the pattern matches nothing, `re.sub` returns the text unchanged.

            ```python
            import re

            print(re.sub(r"x", "y", "no match here"))
            # no match here
            ```

            `\s` matches one whitespace character: a space, a tab `\t` or a newline `\n`.

            ```python
            import re

            print(re.sub(r"\s", "_", "a b\tc\nd"))
            # a_b_c_d
            ```

            Programs use `re.sub` to clean text: to normalise spacing before counting words, to mask
            numbers or ids before writing them to a log, and to clean user input before using it.
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
            ## Named groups

            A numbered group such as `m.group(3)` does not say what it contains. A **named group** is a
            capturing group that also has a name. Write it as `(?P<name>pattern)` and read it with
            `m.group("name")`.

            ```python
            import re

            m = re.search(r"(?P<w>\d+)x(?P<h>\d+)", "size 1024x768")
            print(m.group("w"), m.group("h"))
            # 1024 768
            print(m.groupdict())
            # {'w': '1024', 'h': '768'}
            ```

            - The `P` in `(?P<name>...)` is upper case.
            - `m.groupdict()` returns a dict with every named group. The keys are the group names and
              the values are strings.
            - A named group still has a number, so `m.group(1)` also returns `'1024'` here.

            If you add another group to the pattern later, the numbers of the groups after it change.
            The names stay the same, so code that reads groups by name still gets the right text.

            When nothing matches, `re.search` returns `None`. Check for `None` before you call `.group(...)`.

            ```python
            import re

            m = re.search(r"(?P<w>\d+)x", "no size")
            print(m)
            # None
            ```

            Calling `m.group("w")` on that `None` raises `AttributeError`.

            This step has a research task: read the official description of named groups, so that you
            recognise the syntax in code written by other people.
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
            ## Anchors and flags

            An **anchor** matches a position in the text, not a character. `^` matches at the start and
            `$` matches at the end. By default these are the start and the end of the **whole** string.

            A **flag** is an extra argument that changes how `re` applies the pattern. You pass it as
            `flags=...`.

            - `re.MULTILINE` makes `^` and `$` also match at the start and end of **every line**.
            - `re.IGNORECASE` makes letters match in upper or lower case.

            ```python
            import re

            log = "INFO: start\nWARN: slow\nINFO: done"
            print(re.findall(r"^INFO: (\w+)$", log))
            # []
            print(re.findall(r"^INFO: (\w+)$", log, flags=re.MULTILINE))
            # ['start', 'done']
            print(re.findall(r"warn", log, flags=re.IGNORECASE))
            # ['WARN']
            ```

            Without the flag, `^` matches only at index 0 and `$` only at the end of the text. No single
            line of `log` covers the whole text, so the first call returns `[]`. With `re.MULTILINE`
            each of the three lines has its own start and end.

            ### `findall` with a group

            When the pattern has **one** capturing group, `findall` returns the text of that group for
            each match, not the whole match. That is why the result above is `['start', 'done']` and
            not `['INFO: start', 'INFO: done']`.

            ### `*` and `.*`

            The quantifier `*` means zero or more times, so the item before it can be absent.
            `.` matches any character except a newline, so `.*` matches the rest of the line,
            and it can match an empty string.

            ```python
            import re

            print(re.findall(r"ab*", "a ab abbb"))
            # ['a', 'ab', 'abbb']
            print(re.search(r"id: *(.*)", "id:   42 ok\nnext").group(1))
            # 42 ok
            ```

            ### Several flags

            Combine flags by writing `|` between them.

            ```python
            import re

            log = "INFO: start\nWARN: slow\nINFO: done"
            print(re.findall(r"^info", log, flags=re.MULTILINE | re.IGNORECASE))
            # ['INFO', 'INFO']
            ```
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
            An *agent* is a program that lets a model call tools. A ReAct-style agent writes its tool
            calls as lines like
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
            Request logs of an LLM app must never store API keys or auth tokens (secret strings that
            prove who you are). Mask them
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
            To track cost and speed you parse the request logs of your LLM gateway (the service that sits between your
            app and the model). A log line
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
