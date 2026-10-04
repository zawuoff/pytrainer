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
            ## Find text when you only know its shape

            A log line says `Model v4 costs 30 dollars`, and your program needs the numbers in it. The
            string methods you know can look for a text you already have: `text.find("30")` works when
            you know that the number is 30. Here you do not know the number. You only know what a number
            looks like: digits.

            Python has a small language for describing what a piece of text looks like. It lives in the
            `re` module, which comes with Python. Here is the first sign of that language:

            ```python
            import re

            text = "Model v4 costs 30 dollars"
            print(re.findall(r"\d", text))
            # ['4', '3', '0']
            ```

            `\d` stands for "one digit, whichever digit it is". `re.findall` reads the text from left to
            right and collects every place where that description fits. Each digit fits on its own, so
            you get three pieces. (The `r` in front of the quote is explained at the end.)

            Three loose digits are not the numbers you wanted. Add one more sign:

            ```python
            import re

            text = "Model v4 costs 30 dollars"
            print(re.findall(r"\d+", text))
            # ['4', '30']
            ```

            `+` means "one or more of the thing in front of me, as many as stand in a row". So `\d+` is
            a whole run of digits.

            A description such as `\d+` is called a **pattern**. The language of patterns is called
            **regular expressions**, or **regex** for short. When a piece of text fits a pattern, the
            pattern **matches** it.

            ```match
            `re.findall(r"\d", "room 12")` :: `['1', '2']`
            `re.findall(r"\d+", "room 12")` :: `['12']`
            `re.findall(r"\d+", "3 rooms, 12 beds")` :: `['3', '12']`
            `re.findall(r"\d+", "room twelve")` :: `[]`
            ---
            Without the `+`, every digit is a match of its own. With it, a run of digits is one match. A text without digits gives an empty list. The quotes show that the pieces are strings, not numbers.
            ```

            ### Only the first match

            `re.search` takes the same pattern and text, and stops at the first place where the pattern
            matches:

            ```python
            import re

            m = re.search(r"\d+", "Model v4 costs 30 dollars")
            print(m)
            # <re.Match object; span=(7, 8), match='4'>
            print(m.group())
            # 4
            ```

            `re.search` hands back a **match object**: a value that remembers what matched and where.
            `m.group()` asks it for the matched text. Step through the stages to see why the `30` is
            never reached:

            ```diagram
            {"type":"flow","title":"How re.search scans the text","steps":[
            {"label":"Start at index 0","detail":"re.search receives the pattern and the text. It begins at index 0 of the text.","code":"re.search(r\"\\d+\", \"Model v4 costs 30 dollars\")"},
            {"label":"Try the pattern","detail":"It checks whether the pattern matches starting at the current index. \\d needs a digit at that index.","code":"index 0: 'M' is not a digit"},
            {"label":"No match: advance","detail":"The attempt fails, so re.search moves to the next index and tries again. Indexes 0 to 6 all fail. If no index is left, it returns None.","code":"index 1: 'o'\nindex 2: 'd'\n...\nindex 6: 'v'"},
            {"label":"Match at index 7","detail":"The character at index 7 is the digit 4, so \\d matches. The + tries to match more digits. Index 8 holds a space, so the match ends there.","code":"index 7: '4' is a digit\nindex 8: ' ' is not a digit"},
            {"label":"Return a match object","detail":"re.search stops and returns a match object for the span from index 7 to index 8. It never reaches the 30.","code":"<re.Match object; span=(7, 8), match='4'>"}
            ],"loop":{"from":2,"to":1,"label":"until the pattern matches or the text ends"}}
            ```

            ```quiz
            What does this program print?

            ~~~python
            import re

            m = re.search(r"\d+", "call 911 or 112")
            print(m.group())
            ~~~
            - [x] `911` :: Right. `re.search` stops at the first run of digits, and `.group()` gives its text.
            - [ ] `['911', '112']` :: That is the answer of `re.findall`, which collects every match. `re.search` stops at the first one.
            - [ ] `9` :: `\d` alone would stop after one digit. The `+` takes the whole run, `911`.
            - [ ] `<re.Match object; span=(5, 8), match='911'>` :: That is what `print(m)` shows. `.group()` takes the text out of the match object.
            ```

            ### The `r` in front of the quote

            In a normal string, a backslash starts an escape sequence: `"\n"` is one newline character.
            A pattern needs its backslashes to reach `re` exactly as you wrote them. An `r` in front of
            the opening quote switches escape sequences off, so in `r"\d+"` the backslash stays a
            backslash. This is called a **raw string**. Write every pattern as one.

            **Watch out:** `re.search` gives you a match object, not the text. If your program prints
            something like `<re.Match object; span=(7, 8), match='4'>`, the `.group()` is missing.

            **In short:** `\d+` matches a run of digits, `re.findall` gives every match as a list of
            strings, and `re.search` gives a match object for the first match, which `.group()` turns
            into text.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
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
            `\d+` matches a run of one or more digits, and this text has two runs: `66` and `3`.
            `re.findall` collects every match in a list. The matches are strings, so Python prints them
            in quotes: `['66', '3']`. `re.search` stops at the first match, which is `66`, and hands back
            a match object. `m.group()` reads the matched text out of it, and `print` shows a string
            without quotes: `66`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Work out first which pieces of the text `\\d+` matches. A piece ends at the first character that is not a digit.",
            "The first `print` shows what `re.findall` hands back, and the second shows what `m.group()` hands back. One of the two is a list, and the other is a single string.",
            "Your first line is a list of every run of digits in the text, written the way Python prints a list of strings: square brackets, a comma between the items, and single quotes around each item. Your second line is only the first run of digits, without quotes.",
        ],
    },
    {
        "id": "regex-s2",
        "title": "Find all numbers",
        "difficulty": 0,
        "lesson": r'''
            ## Collect every match in one list

            One line of a log reads `latency 120ms, 85ms, 240ms`. You want all three numbers, perhaps to
            find the slowest call. `re.search` stops at the first match, so it would give you `120` and
            nothing more.

            In the last step you met the function that keeps going. `re.findall` moves through the text
            from left to right, collects every match, and hands them back as a list, in the order in
            which they stand in the text:

            ```python
            import re

            log = "latency 120ms, 85ms, 240ms"
            print(re.findall(r"\d+", log))
            # ['120', '85', '240']
            ```

            A match may sit in the middle of a word. `\d+` asks for digits, and it does not care what
            stands around them:

            ```predict
            import re

            line = "gpt-4 retried 3 times in 20s"
            found = re.findall(r"\d+", line)
            print(found)
            print(len(found))
            ---
            The `4` in `gpt-4` and the `20` in `20s` are runs of digits like any other, so the list has three items. The letters and the `-` around them are not part of the matches.
            ```

            ### The items are strings

            Every item in that list is a piece of the text. So it is a string, even when it holds
            nothing but digits. To calculate with an item, turn it into a number with `int()` first, as
            you did in the Data types chapter.

            ```try
            import re

            sizes = re.findall(r"\d+", "chunks of 200 and 350 words")
            print(sizes[0] + sizes[1])
            ---
            The program glues two strings together and prints `200350`. Change the last line so that it adds the two numbers and prints `550`.
            ---
            import re

            sizes = re.findall(r"\d+", "chunks of 200 and 350 words")
            print(int(sizes[0]) + int(sizes[1]))
            ---
            `findall` hands back strings, and `+` between two strings joins them. `int()` around each item turns it into a number first.
            ```

            ### When nothing matches

            ```python
            import re

            print(re.findall(r"\d+", "no numbers here"))
            # []
            ```

            Finding nothing is not an error. You get an empty list. A `for` loop over an empty list
            runs zero times, so code that loops over the result needs no extra check.

            ```quiz
            How many items are in the list that `re.findall(r"\d+", "v2.5 has 10 tools")` hands back?
            - [x] 3 :: Right: `'2'`, `'5'` and `'10'`. The dot is not a digit, so it ends the first run, and the `5` starts a new one.
            - [ ] 2 :: `2.5` is one number to you, but `\d+` only knows digits. The dot ends one run, and the `5` starts another.
            - [ ] 4 :: `10` is two digits in a row, and the `+` keeps a run together as one match.
            - [ ] 1 :: `re.search` stops after one match. `re.findall` carries on to the end of the text.
            ```

            **Watch out:** the items are strings, and strings are compared character by character, like
            words in a dictionary. So `max(['120', '85', '240'])` is `'85'`, with no error to warn you.
            Turn the items into numbers before you compare them or add them up.

            **In short:** `re.findall(pattern, text)` hands back a list of every match, as strings, in
            the order of the text, and an empty list when nothing matches.
        ''',
        "prompt": r'''
            The logs of an AI app mix numbers into plain text, as in `"gpt-4o used 1200 tokens"`. Before
            you can add the numbers up or chart them, you have to get them out of the text.

            **Your job:** finish `find_numbers(text)` so that it gives back every number in the text. The
            function is already written except for one gap, marked `___`. The name of a function of the
            `re` module belongs there. Replace the gap.

            **What goes in**
            - `text`: a string, for example `"gpt-4o used 1200 tokens"`

            **What comes out**
            - a list of strings: every run of digits in the text, in the order in which they stand
              there. For the example value that is `["4", "1200"]`.

            **Rules**
            - The pattern in the editor is right. Only the gap changes.
            - The numbers stay strings: `"1200"`, not `1200`.
            - A text without any digit gives the empty list, `[]`.

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
            "The lesson compares two functions of the `re` module. One of them stops at the first match. Which one keeps going?",
            "Look at what must come out: a list with every run of digits in it, and an empty list when there is none. Only one of the two functions hands back a list.",
            "The gap takes one word: the name of the function that the first example of the lesson calls. The pattern and the text after the gap stay as they are.",
        ],
    },
    {
        "id": "regex-s3",
        "title": "Fix the version finder",
        "difficulty": 0,
        "lesson": r'''
            ## Is it anywhere in the text?

            Release notes mention model versions: `now using v2 for chat`. Your program has a yes-or-no
            question about such a text: does it mention a version at all?

            First the pattern. A plain letter in a pattern stands for itself, so `v\d` reads: the
            letter `v`, and then one digit.

            ```python
            import re

            print(re.findall(r"v\d", "version v2, later v3"))
            # ['v2', 'v3']
            ```

            The `v` of `version` is not in the list. The whole pattern has to fit, and after that `v`
            comes an `e`, which is not a digit.

            ```match
            `v\d` :: fits `v2`, but not `vx`
            `\d\d` :: fits `42`, but not `4`
            `id\d+` :: fits `id7` and `id123`, but not `id`
            `\d+%` :: fits `50%`, but not `50`
            ---
            Read a pattern from left to right, one piece at a time. Every piece has to find its character in the text, or there is no match.
            ```

            ### Yes or no

            You know that `re.search` hands back a match object. When the pattern fits nowhere, there
            is no match object to hand back, and you get `None` instead:

            ```python
            import re

            print(re.search(r"v\d", "now using v2 for chat"))
            # <re.Match object; span=(10, 12), match='v2'>
            print(re.search(r"v\d", "no version here"))
            # None
            ```

            For a yes-or-no answer, compare the result with `None`, as you did in the Data types
            chapter. `re.search(...) is not None` is `True` when there is a match and `False` when there
            is none.

            ### The function with the misleading name

            The `re` module also has a function called `re.match`. The name sounds like "find a match".
            But `re.match` tries the pattern at the very start of the text only, at index 0, and gives
            up when it does not fit there.

            ```python
            import re

            print(re.match(r"v\d", "v2 is out") is not None)
            # True
            print(re.match(r"v\d", "now using v2 for chat") is not None)
            # False
            ```

            The second text does contain `v2`. It starts with `n`, though, so `re.match` says no.

            The program below should print `True`, because the note mentions `v7`. Pick the function:

            ```fill
            import re

            note = "we moved to v7 last week"
            print(re.___(r"v\d", note) is not None)
            ---
            - [x] search :: Right. `re.search` tries every position, so it finds `v7` in the middle of the text.
            - [ ] match :: `re.match` only tries index 0. This text starts with `w`, so it hands back `None`, and the program prints `False`.
            - [ ] find :: `find` is a string method, as in `note.find("v7")`. The `re` module has no function of that name, so Python stops with `AttributeError: module 're' has no attribute 'find'`.
            ```

            **Watch out:** `re.match` raises no error when you meant `re.search`. It quietly hands back
            `None` for every text that does not start with the pattern, so the bug shows only on some
            inputs.

            **In short:** `re.search` looks for the pattern anywhere in the text, `re.match` looks only
            at the very start, and `is not None` turns either result into `True` or `False`.
        ''',
        "prompt": r'''
            Release notes mention model versions such as `v1.2`. The function `has_version` is meant to
            say whether a text mentions a version anywhere. It has a bug: it says yes only when the
            version stands at the very start of the text.

            **Your job:** find the bug in `has_version(text)` and fix it. The code is already in the
            editor.

            **What goes in**
            - `text`: a string, for example `"release v10.04 now"`

            **What comes out**
            - `True` when the text contains a version anywhere, and `False` when it does not

            **Rules**
            - A version is the letter `v`, one or more digits, a dot, and one or more digits again, as
              in `v1.2` and `v10.04`.
            - The pattern in the editor already says exactly that, so leave it alone. (`\.` stands for
              a real dot. A later step explains why it needs the backslash.) The bug is somewhere else.
            - `v1` on its own, with no dot and no second number, is not a version.

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
            "The pattern is right. Look at the name of the function that is called with it, and read the last part of the lesson again.",
            "The function in the editor tries the pattern at one position only. Which position is that? And which function of the `re` module tries every position?",
            "Change one word on the `return` line: the name of the `re` function. Use the one that looks for the pattern anywhere in the text. Everything else on that line stays.",
        ],
    },
    {
        "id": "regex-s4",
        "title": "Validate a ticket id",
        "difficulty": 0,
        "lesson": r'''
            ## Is the whole text a valid code?

            A form asks for an order code such as `ORD-042`. Your program must accept `ORD-042` and refuse
            `please send ORD-042 now`. You already know a function that answers yes or no, `re.search`.
            Try it on both texts:

            ```python
            import re

            print(re.search(r"ORD-\d+", "ORD-042") is not None)
            # True
            print(re.search(r"ORD-\d+", "please send ORD-042 now") is not None)
            # True
            ```

            Both say yes, because `re.search` looks for the pattern anywhere, and a code does sit inside
            the second text. A form needs a different question: does the whole text fit the pattern, from
            the first character to the last? `re.fullmatch` asks exactly that. It hands back a match
            object when the whole text fits, and `None` when it does not.

            ```python
            import re

            print(re.fullmatch(r"ORD-\d+", "ORD-042") is not None)
            # True
            print(re.fullmatch(r"ORD-\d+", "please send ORD-042 now") is not None)
            # False
            ```

            Checking that a text has the right format, like this, is called **validation**.

            ### Exactly this many

            `\d+` accepts any number of digits. A code with exactly three digits needs a stricter sign:
            a number in curly braces, written after a piece of the pattern, says how many times that piece
            must appear. `\d{3}` is three digits, no more and no fewer.

            ```python
            import re

            print(re.fullmatch(r"ORD-\d{3}", "ORD-042") is not None)
            # True
            print(re.fullmatch(r"ORD-\d{3}", "ORD-0421") is not None)
            # False
            ```

            `+` and `{3}` are both **quantifiers**: signs that say how many times the piece in front of
            them repeats. Letters and the hyphen in a pattern match themselves, and a capital letter is
            not the same as a lower-case one, so `ORD` does not match `ord`.

            ```predict
            import re

            for text in ["A-7", "A-77", "A-777"]:
                print(text, re.fullmatch(r"A-\d{2}", text) is not None)
            ---
            `\d{2}` wants exactly two digits. `A-7` has one, so it fails. `A-77` has two, so it passes. `A-777` has three, and the third digit is left over, so `re.fullmatch` says no.
            ```

            ```quiz
            Which text does `re.fullmatch(r"ORD-\d{3}", text)` accept?
            - [x] `ORD-042` :: Right. `ORD-` matches itself, the three digits fill `\d{3}`, and nothing is left over.
            - [ ] `ORD-0421` :: The pattern takes three digits and stops, but this text has a fourth digit left over. The whole text has to fit.
            - [ ] `my ORD-042` :: Text before the code is not allowed either. `re.fullmatch` starts at the first character of the text.
            - [ ] `ord-042` :: Letters match themselves exactly, capital letters included. `ord` is not `ORD`.
            ```

            **Watch out:** `re.match` is no replacement. It only insists on the start of the text, so
            `re.match(r"ORD-\d{3}", "ORD-0421")` still hands back a match object for `ORD-042`. For a
            yes-or-no check of the whole text, use `re.fullmatch`.

            **In short:** `re.fullmatch(pattern, text)` gives a match object only when the whole text fits
            the pattern, `{3}` means exactly three times, and `is not None` turns the result into `True`
            or `False`.
        ''',
        "prompt": r'''
            A support bot should only look up a ticket when the user typed a valid ticket id, and nothing
            else around it.

            **Your job:** write `is_ticket_id(text)` so that it says whether the whole text is a valid
            ticket id.

            **What goes in**
            - `text`: a string, for example `"TICKET-1234"`

            **What comes out**
            - `True` when the whole text is a ticket id, and `False` when it is not. It must be a real
              `True` or `False`, not a match object.

            **Rules**
            - A ticket id is the word `TICKET` in capital letters, a hyphen, and exactly 4 digits.
            - Nothing may stand before it or after it. `"see TICKET-1234"` and `"TICKET-1234!"` are
              `False`.
            - 3 digits or 5 digits, a lower-case `ticket`, and a letter among the digits are all `False`.

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
            "The text must fit as a whole, with nothing before it and nothing after it. Which function of the lesson asks exactly that?",
            "The pattern is the fixed letters and the hyphen, followed by a digit that must appear an exact number of times. The function you picked hands back a match object or `None`, and the result you return must be `True` or `False`.",
            "Write the pattern as a raw string: the capital letters and the hyphen as they are, then the sign for one digit and the sign for an exact count. Call the whole-text function with the pattern and the text. Compare what it hands back with `None`, and return that comparison.",
        ],
    },
    {
        "id": "regex-s5",
        "title": "Collect hashtags",
        "difficulty": 0,
        "lesson": r'''
            ## A set of allowed characters

            `\d` matches one digit. But how do you match the words in `gpt4 and llama3`? There is no short
            sign for "any letter", so you describe the characters you allow yourself. Put them in square
            brackets, and the pattern matches one character that is any of them.

            ```python
            import re

            print(re.findall(r"[aeiou]", "prompt tokens"))
            # ['o', 'o', 'e']
            ```

            `[aeiou]` matches one vowel. Every vowel in the text is a match of its own, just as every
            digit was a match of its own for `\d` in the first step. The part in square brackets is called
            a **character class**.

            Listing every letter would be long, so a class can contain a **range**: a hyphen between two
            characters stands for all the characters from the first to the last. `[a-z]` is any lower-case
            letter, `[A-Z]` any capital letter and `[0-9]` any digit. Put several in one class to combine
            them, as in `[A-Za-z]` for any letter. A `+` after a class repeats it, just as it repeated
            `\d`.

            ```python
            import re

            print(re.findall(r"[A-Z][a-z]+", "Ada met Grace in Paris"))
            # ['Ada', 'Grace', 'Paris']
            ```

            Here one capital letter is followed by a run of lower-case letters. A run ends at the first
            character that is not in the class.

            ```match
            `re.findall(r"[a-z]+", "Ada-7 ok_2")` :: `['da', 'ok']`
            `re.findall(r"[A-Za-z]+", "Ada-7 ok_2")` :: `['Ada', 'ok']`
            `re.findall(r"[0-9]+", "Ada-7 ok_2")` :: `['7', '2']`
            `re.findall(r"\w+", "Ada-7 ok_2")` :: `['Ada', '7', 'ok_2']`
            ---
            The first class has no capital letters, so the `A` is skipped and the run of `Ada` starts at the `d`. The hyphen and the space are in none of these classes, so they end every run. The last pattern, `\w`, is explained next.
            ```

            ### A short sign for letters, digits and underscore

            Letters, digits and `_` are what names in code are made of, so they have a short sign of their
            own: `\w`. Then `\w+` is a run of them:

            ```python
            import re

            print(re.findall(r"\w+", "user_id=42, ok"))
            # ['user_id', '42', 'ok']
            ```

            The `=`, the comma and the space are none of the three, so they end each run.

            ```try
            import re

            print(re.findall(r"[a-z]+", "gpt4 and llama3"))
            ---
            The program prints `['gpt', 'and', 'llama']`: the digits are cut off. Change the class so that the digits stay in the words and the program prints `['gpt4', 'and', 'llama3']`.
            ---
            import re

            print(re.findall(r"[a-z0-9]+", "gpt4 and llama3"))
            ---
            A class can hold several ranges. `[a-z0-9]` accepts a lower-case letter or a digit at each position, so the run no longer ends at the digit.
            ```

            ```quiz
            What does `re.findall(r"[a-z]+", "model_v2")` give?
            - [x] `['model', 'v']` :: Right. The `_` is not in the class, so it ends the first run. The `v` starts a new run, which ends at the `2`, and the `2` is not in the class either.
            - [ ] `['model_v']` :: The underscore is not between `a` and `z`, so `[a-z]` cannot match it. Only `\w` includes `_`.
            - [ ] `['model', 'v2']` :: `[a-z]` has no digits in it, so the `2` is not part of any match.
            - [ ] `['m', 'o', 'd', 'e', 'l', 'v']` :: The `+` keeps a run of letters together as one match, so `model` is a single item.
            ```

            **Watch out:** a class matches one single character. `[a-z]` alone finds letters one at a
            time, and you need the `+` after it to get whole words. A word that has a digit or an
            underscore in it is cut at that place unless the class contains them.

            **In short:** `[...]` matches one character out of those listed, `a-z` is a range, `+` repeats
            the class, and `\w` is the short sign for a letter, a digit or an underscore.
        ''',
        "prompt": r'''
            You want to tag social posts by topic before sending them to a classifier, so you need the
            hashtags out of each post.

            **Your job:** write `find_hashtags(text)` so that it gives back every hashtag in the text.

            **What goes in**
            - `text`: a string, for example `"Loving #RAG and #llm_ops!"`

            **What comes out**
            - a list of strings: every hashtag, in the order in which it stands in the text, each one with
              its `#` in front. For the example value that is `["#RAG", "#llm_ops"]`.

            **Rules**
            - A hashtag is a `#` followed by one or more letters, digits or underscores.
            - A hashtag ends at the first other character (a `!`, a comma, a hyphen, a space), so
              `"#gpt-4"` gives `"#gpt"`.
            - A `#` with nothing valid after it is not a hashtag.
            - A text without any hashtag gives the empty list, `[]`.

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
            "You need every match, in a list: which function of the lesson gives that? And which part of the lesson describes a set of allowed characters?",
            "The pattern starts with the `#`, written as it is. Then comes a class that allows letters, digits and underscore, repeated for one or more characters. The match ends by itself at the first other character.",
            "Write the pattern as a raw string: the `#` first, then a class of the allowed characters (written with ranges, or with the short sign for letter, digit or underscore), then the sign for one or more. Hand back what the find-every function returns for that pattern and the text.",
        ],
    },
    {
        "id": "regex-s6",
        "title": "Capture the pieces",
        "difficulty": 0,
        "lesson": r'''
            ## Pull one match apart

            The text `size 1024x768` holds a width and a height. `re.findall` with `\d+` would give you both
            numbers, but in a list that does not say which is which. A match object can do better. If you
            mark parts of the pattern with parentheses, it remembers the text of each part separately.

            ```python
            import re

            m = re.search(r"(\d+)x(\d+)", "size 1024x768")
            print(m.group(0))
            # 1024x768
            print(m.group(1))
            # 1024
            print(m.group(2))
            # 768
            ```

            Each pair of parentheses marks a part of the pattern whose text the match object keeps. Such a
            part is called a **group**.

            - `m.group(1)` is the text of the first group, and `m.group(2)` the text of the second.
              Groups are numbered from 1, in the order of their opening parentheses.
            - `m.group(0)` is the whole match. `m.group()` with no number gives the same text.

            The parentheses do not change which text matches: `\d+x\d+` matches the same `1024x768`. They
            only mark what to remember.

            A group is a stretch of the text, so it has a start and an end, like a slice. `m.start(1)` is
            the index where group 1 begins, and `m.end(1)` is the index just after it ends. Move the
            handles to `10` and `13` to see the stretch that group 2 covers.

            ```diagram
            {"type":"slice","title":"The span of group 1 in text","name":"text","value":"size 1024x768","start":5,"stop":9}
            ```

            ```fill
            import re

            m = re.search(r"(\w+)@(\w+)", "mail ana@lab now")
            print(m.group(___))
            ---
            - [x] 2 :: Right. The second pair of parentheses matched `lab`, the part after the `@`.
            - [ ] 1 :: That is the first group, the part before the `@`, which is `ana`.
            - [ ] 0 :: That is the whole match, `ana@lab`, with both parts and the `@`.
            ```

            The program above should print `lab`, the text after the `@`. Pick the number for the gap.

            ### A group is text

            A group holds a piece of the text, so it is a string, even when it holds only digits. To do
            arithmetic with it, turn it into a number with `int()` first.

            ```quiz
            `m.group(1)` holds the text `1024`. What does `print(m.group(1) * 2)` print?
            - [x] `10241024` :: Right. A group is a string, and `*` on a string repeats it. There is no arithmetic yet.
            - [ ] `2048` :: That is what you get after `int(m.group(1)) * 2`. Without `int`, the group is still text.
            - [ ] `TypeError` :: A string times a whole number is allowed. It repeats the string.
            ```

            **Watch out:** only the numbers from 0 up to the number of groups exist. With two groups,
            `m.group(3)` stops with `IndexError: no such group`.

            **In short:** a pair of parentheses makes a group, `m.group(1)`, `m.group(2)` and so on give
            the text of each one as a string, and `m.group(0)` gives the whole match.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
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
            `re.search` tries the pattern from the left. At `set` the `\w+` finds letters, but no `=` follows,
            so the attempt fails and `re.search` moves on. The match starts at `max_tokens`: a run of
            letters, digits and underscores, then `=`, then the digits `512`.

            - `m.group(0)` is the whole match: `max_tokens=512`.
            - `m.group(1)` is the text of the first pair of parentheses: `max_tokens`.
            - `m.group(2)` is the text of the second pair, the string `"512"`. `int` turns it into the
              number 512, and `* 2` makes it 1024. `print` shows a number without quotes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Find the piece of the text that the pattern matches first. It is a run of letters, digits and underscores, then an `=`, then digits. `re.search` skips the words that are not followed by an `=`.",
            "Group 0 is the whole match. Group 1 is the text matched by the first pair of parentheses, and group 2 by the second. A group is a string until `int` turns it into a number.",
            "Your first line is the whole matched text, with the `=` in it. Your second line is only the part in front of the `=`. Your third line is the number after the `=`, doubled, printed without quotes.",
        ],
    },
    {
        "id": "regex-1",
        "hints": [
            "Describe the address as consecutive pieces rather than trying to match arbitrary text around it.",
            "Use character classes for the name and domain, then require a literal separator and a sufficiently long letter ending.",
            "Build the pattern left to right using the allowed characters and repetition rules. Avoid capturing groups so all matches are returned as complete strings, and test punctuation and absent-address cases.",
        ],
        "title": "Extract emails",
        "difficulty": 1,
        "lesson": r'''
            ## Match punctuation without giving it special meaning

            You want to find a price such as `$8.25` inside a sentence. A pattern needs to describe both the digits and the punctuation, but some punctuation already tells the pattern engine what to do. You need to distinguish those instructions from actual characters.

            ```python
            import re
            price = re.compile(r"\$\d+\.\d{2}")
            print(price.findall("pay $8.25 or $12.50"))
            # ['$8.25', '$12.50']
            ```

            Read the pattern from left to right: a dollar sign, one or more digits, a dot, and exactly two digits. A backslash before a special character requests the real character. This is **escaping**. The raw-string prefix keeps those backslashes intact for the pattern engine.

            ```predict
            import re
            print(re.findall(r"x.y", "x.y x-y"))
            print(re.findall(r"x\.y", "x.y x-y"))
            ---
            The unescaped dot matches either punctuation character. The escaped dot matches only the literal dot, so only x.y remains in the second list.
            ```

            `re.compile` produces a **pattern object**. It has methods such as `findall` and `fullmatch`, with the pattern already attached. Keeping one named pattern can make repeated use clearer. Compilation is optional for a one-off operation.

            Remember character classes? Most punctuation inside square brackets is already literal. A class such as `[.%+]` accepts one of those three characters. Repetition belongs after the class. `{2,}` means at least two occurrences, with no stated maximum.

            ```fill
            import re
            print(re.findall(r"[A-Z]___", "A BB CCC"))
            ---
            - [x] {2,} :: Each match needs at least two capitals, so BB and CCC qualify.
            - [ ] {2} :: This takes only two characters from CCC instead of the whole run.
            - [ ] ? :: This allows zero or one capital, including empty matches.
            ```

            **Watch out:** an unescaped dot usually causes no Python error. It quietly accepts unwanted characters, so test a near-match as well as a valid example.

            **In short:** escape literal punctuation and combine small pattern parts in the order the text must follow.
        ''',
        "prompt": r'''
            Before sending support tickets to an LLM you want to know which contacts they
            mention. Extract the email addresses.

            **Your job:** write `find_emails(text)`

            **What goes in**

            - `text`: a `str`, e.g. `"Contact ops@x.io today"`

            **What comes out**
            - a `list` of strings: every whole email address, in the order they
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
            "You are validating a whole string, not searching for a fragment.",
            "Use a literal case-sensitive prefix followed by an allowed-character class with inclusive length bounds.",
            "Describe the suffix alphabet with a literal hyphen, apply the required repetition range, and convert the full-match result to a Boolean without trimming input.",
        ],
        "title": "Validate an API key",
        "difficulty": 1,
        "lesson": r'''
            ## Check the whole value, including its boundaries

            An identifier has a fixed prefix and a limited number of characters after it. Finding a valid-looking fragment inside a longer string is not enough: the complete input must obey the format, with nothing extra attached.

            ```python
            import re
            pattern = r"job-[a-z0-9_-]{3,5}"
            for value in ["job-ab3", "job-a", "job-ab3!"]:
                print(re.fullmatch(pattern, value) is not None)
            # True
            # False
            # False
            ```

            `{3,5}` permits three, four, or five repetitions of the preceding part. These are inclusive boundaries. Here the repeated part is a character class, so each character must belong to the allowed set.

            The hyphen inside a class needs care. Between letters, it describes a range, as in `a-z`. At the end of the class it represents a real hyphen. That lets an identifier contain hyphens without accidentally inventing another range.

            ```predict
            import re
            pattern = r"job-[a-z]{3,5}"
            print(re.fullmatch(pattern, "job-abc\n") is not None)
            print(re.search(pattern, "job-abc\n") is not None)
            ---
            fullmatch rejects the extra newline. search can find a valid fragment before that newline, so it succeeds despite the extra character.
            ```

            A match result is an object or `None`, rather than necessarily the Boolean your caller expects. Comparing it with `None` produces an actual `True` or `False`.

            Checking shape is **format validation**. It can catch a pasted space or missing character, but it cannot establish that a credential exists, belongs to you, or is accepted by a remote service.

            ```quiz
            Which input belongs in a boundary test for a suffix length of three through five?
            - [x] A suffix with two characters :: It sits just outside the permitted range and should fail.
            - [ ] Only a suffix with four characters :: An interior value cannot reveal an incorrect minimum or maximum.
            ```

            **Watch out:** trimming input before validation changes the rule. If extra whitespace is forbidden, reject it rather than silently removing it.

            **In short:** use full-string matching and explicit inclusive repetition limits for exact formats.
        ''',
        "prompt": r'''
            Before calling an LLM API, check that the configured key at least looks right, so
            a typo fails fast with a clear message.

            **Your job:** write `is_valid_key(key)`

            **What goes in**

            - `key`: a `str`, e.g. `"sk-proj_Ab3-xxxxxxxxxxxx"`

            **What comes out**
            - `True` if the **whole** string is a valid key, else `False` (a real `bool`)

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
            ## Replace each matching run once

            Copied text often contains repeated separators. You want to clean those parts while keeping letters and punctuation unchanged. Instead of finding positions and rebuilding the string yourself, let a pattern identify each part to replace.

            ```python
            import re
            original = "first---second--third"
            cleaned = re.sub(r"-+", "/", original)
            print(cleaned)
            # first/second/third
            print(original)
            # first---second--third
            ```

            `re.sub` takes the pattern, replacement, and original text in that order. Each entire match is replaced once. Because the plus sign matches a run of one or more hyphens, three adjacent hyphens become one slash, not three slashes.

            ```predict
            import re
            print(re.sub(r"\d", "#", "room 204"))
            print(re.sub(r"\d+", "#", "room 204"))
            ---
            The first pattern makes three separate digit matches, producing three replacement characters. The second treats the entire run of digits as one match.
            ```

            The result is a new string. Python strings cannot have their characters changed in place, so calling a string-cleaning operation without storing or returning its result leaves the caller's original value unchanged.

            The pattern `\s` matches whitespace, including spaces, tabs, and line breaks. Adding a repetition marker lets one match cover a mixed run of those characters. Decide whether line breaks are allowed to disappear before choosing this broad category.

            ```fill
            import re
            print(re.sub(r"\s", "_", "a\tb\nc"))
            print("  done  ".___())
            ---
            - [x] strip :: This removes whitespace at the two ends and prints done.
            - [ ] upper :: This changes letters and preserves the surrounding whitespace.
            - [ ] split :: This returns a list rather than the cleaned string.
            ```

            **Watch out:** matching one whitespace character at a time preserves the count of gaps through repeated replacements. Match the whole run when you need one replacement per run.

            **In short:** substitution replaces each match once, so the pattern determines how much text becomes one replacement.
        ''',
        "prompt": r'''
            Text pasted by users (or scraped from PDFs) is full of messy spacing. Normalise it
            before putting it in a prompt.

            **Your job:** write `tidy_spaces(text)`

            **What goes in**

            - `text`: a `str`, e.g. `"  Summarise\tthis\n\n  please "`

            **What comes out**
            - a `str`: every run of whitespace (spaces, tabs, newlines, in any mix)
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
            "Think about how much text one substitution match should consume.",
            "A mixed run of whitespace should become one space; the two ends need no spaces at all.",
            "Substitute each nonempty whitespace run with one ordinary space, remove remaining boundary whitespace, and return the new text.",
        ],
    },
    {
        "id": "regex-8",
        "title": "Named groups",
        "difficulty": 1,
        "lesson": r'''
            ## Give extracted pieces meaningful names

            A log entry contains several useful values. If your code reads group one and group two, a future change to the pattern can make those numbers hard to follow. You can name each captured piece according to what it represents.

            ```python
            import re
            match = re.search(r"(?P<width>\d+)x(?P<height>\d+)", "image 640x480")
            print(match.group("width"))
            # 640
            print(match.groupdict())
            # {'width': '640', 'height': '480'}
            ```

            The form `(?P<width>...)` creates a **named group**. It captures the text matched inside it, just as ordinary parentheses do, and also associates that text with a name. The capital `P` is part of the syntax.

            ```predict
            import re
            match = re.search(r"page=(?P<number>\d+)", "page=08")
            print(match.group("number"))
            print(int(match.group("number")) + 1)
            ---
            The group contains text, including its leading zero. Converting that text with int creates the number eight, so the later addition produces nine.
            ```

            Captured digits are still strings. Convert them when your caller expects numbers. `groupdict` is convenient when you need all named pieces, but it does not perform type conversion for you.

            The search itself can fail. `re.search` returns `None` when no match exists, so check that result before reading a group. This keeps an absent record distinct from malformed extraction code.

            ```quiz
            Your pattern searches a line without the expected fields. What should you check before calling group?
            - [x] Whether the search result is None :: There is no match object to inspect in that case.
            - [ ] Whether the first captured number is zero :: You cannot read any captured value until a match exists.
            ```

            **Watch out:** calling `.group(...)` on `None` raises `AttributeError`. A missing match is often normal input, so handle it deliberately rather than letting attribute access crash.

            **In short:** name captured pieces, check that a match exists, and convert their text to the required output types.
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

            **Your job:** write `parse_usage(line)`

            **What goes in**

            - `line`: a `str`, e.g. `"ts=17:02 model=gpt-4o tokens=512 status=ok"`

            **What comes out**
            - a `dict` `{"model": <str>, "tokens": <int>}`, e.g.
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
            "The output needs two named pieces and one type conversion.",
            "Search anywhere in the line for the literal labels with named captures around their values.",
            "Describe model characters and the digit count in separate named groups. Return the absent-result value if search fails; otherwise build the required dictionary and convert the captured count to an integer.",
        ],
    },
    {
        "id": "regex-9",
        "title": "Errors at the start of a line",
        "difficulty": 1,
        "lesson": r'''
            ## Restrict matches to the start of each line

            A log message may mention a warning without actually being a warning entry. You need to distinguish a label at the start of a line from the same text buried inside its message.

            ```python
            import re
            log = "INFO: ready\nNOTE: mentions INFO: later\nINFO: done"
            print(re.findall(r"^INFO: (.*)$", log, flags=re.MULTILINE))
            # ['ready', 'done']
            ```

            The `^` and `$` parts match positions rather than consuming characters. Such position checks are called **anchors**. Normally they refer to the whole string's boundaries. `re.MULTILINE` makes them also recognize each line's start and end.

            An option that changes pattern behavior is a **flag**. Another flag, `re.IGNORECASE`, makes letter case irrelevant. Combine flags with `|` only when both behaviors belong in your specification.

            ```predict
            import re
            text = "Note: one\nNOTE: two"
            print(re.findall(r"^NOTE", text, flags=re.MULTILINE))
            print(re.findall(r"^NOTE", text, flags=re.MULTILINE | re.IGNORECASE))
            ---
            MULTILINE changes positions, not letter case. The first search finds only NOTE. Adding IGNORECASE also accepts the mixed-case label Note.
            ```

            With one capturing group, `findall` returns the text inside that group for every match. This lets you recognize a line's label while returning only its message. `.*` accepts zero or more characters other than a newline, so it can capture an empty message too.

            Be precise about whitespace near line boundaries. `\s` includes newlines; a class containing only space and tab does not. Accidentally consuming a newline can make an empty message borrow text from the next line.

            ```quiz
            Which repetition allows a message to be empty?
            - [x] The star quantifier :: It permits zero characters as well as longer runs.
            - [ ] The plus quantifier :: It requires at least one character.
            ```

            **Watch out:** multiline mode does not make the dot match newlines. Those are separate pattern behaviors, and keeping them separate helps prevent cross-line matches.

            **In short:** anchors choose positions, flags adjust their behavior, and a capture group selects the text you return.
        ''',
        "prompt": r'''
            An agent's log has one event per line. Collect the error messages.

            **Your job:** write `error_messages(log)`

            **What goes in**

            - `log`: a `str`, lines separated by `"\n"`, e.g. `"INFO: ok\nERROR: disk full"`

            **What comes out**
            - a `list` of strings: for each line that **starts** with `ERROR:`,
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
            "The label must match a position at a line boundary, not merely occur in the text.",
            "Use multiline anchors and one group for the message. Restrict optional spacing so it cannot consume a newline.",
            "Match the exact uppercase label at the line start, skip horizontal whitespace, and capture the possibly empty remainder of that line. Return all captured messages in order.",
        ],
    },
    {
        "id": "regex-3",
        "hints": [
            "Think about line boundaries and the two pieces that the caller needs.",
            "Capture a valid identifier and the input on the same line, allowing only horizontal spacing around the fixed punctuation.",
            "Search for the first anchored action line with multiline behavior. Let the input capture extend to the final closing bracket, then trim its surrounding whitespace and return both captures, or None when no line qualifies.",
        ],
        "title": "Parse a ReAct action",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            An *agent* is a program that lets a model call tools. A ReAct-style agent writes its tool
            calls as lines like
            `Action: search[weather in Paris]`. Your code must find that line in the model's
            multi-line output and pull out which tool to call and with what input.

            **Your job:** write `parse_action(text)`

            **What goes in**

            - `text`: a `str`, the model output, possibly several lines separated by `"\n"`

            **What comes out**
            - a tuple `(tool_name, tool_input)` of two strings, e.g.
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
            "Separate key masking from authorization-header masking because their replacement rules differ.",
            "A replacement function can inspect matched text. A captured header prefix can be reused unchanged in the replacement.",
            "Reject keys embedded in words with a lookbehind condition, mask each qualifying key while retaining its suffix, then match authorization headers without case sensitivity and replace only their token portions.",
        ],
        "title": "Redact secrets from logs",
        "difficulty": 2,
        "prompt": r'''
            Request logs of an LLM app must never store API keys or auth tokens (secret strings that
            prove who you are). Mask them
            before the log is written.

            **Your job:** write `redact(log)`

            **What goes in**

            - `log`: a `str`, possibly several lines, e.g. `"key=sk-abcdefghijklmnop1234 ok"`

            **What comes out**
            - a `str`: the same text with every secret masked and everything else unchanged

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
            "Break validation into the line prefix, named pairs, and each pair's allowed value.",
            "Read pairs independently of their order. A line is usable only after required fields and numeric formats have passed their checks.",
            "Extract the timestamp and level, collect pairs, reject missing or malformed required values, convert seconds or milliseconds with the specified rounding, and build only the requested output fields.",
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

            **Your job:** write `parse_log(text)`

            **What goes in**

            - `text`: a `str` with zero or more log lines separated by `"\n"`

            **What comes out**
            - a `list` of dicts, one per **valid** line, in order. Each dict has exactly
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
            "A substitution function can calculate a different replacement for each match.",
            "Capture the variable name and optional filter while keeping all whitespace matching on one line.",
            "Find only valid placeholder forms. In the replacement callback, look up the value, convert it to text, apply an allowed filter when present, and raise for an unknown filter. Let one substitution pass leave inserted values unscanned.",
        ],
        "title": "Prompt template engine",
        "difficulty": 3,
        "prompt": r'''
            Prompt templates keep your prompts out of your code. Build a tiny template engine
            that fills in placeholders like `{{ name }}` or `{{name|upper}}`.

            **Your job:** write `render(template, variables)`

            **What goes in**

            - `template`: a `str`, e.g. `"Hi {{ name }}! Topic: {{topic|upper}}"`
            - `variables`: a `dict` from names to values, e.g. `{"name": "Ana", "topic": "rag"}`

            **What comes out**
            - a `str`: the template with every valid placeholder replaced

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
