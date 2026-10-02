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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["string", "text", "strip", "split", "join", "replace", "lower", "upper",
                 "startswith", "endswith", "find", "slice", "whitespace", "words", "lines"],
    "cards": [
        {
            "syntax": "s.strip()  /  s.lower()  /  s.upper()",
            "explain": "Each returns a new string: without whitespace at both ends, in lower case, in upper case. s itself does not change.",
            "example": r'''
                raw = "  Hello World \n"
                clean = raw.strip()
                print(clean)
                # Hello World
                print(clean.lower(), clean.upper())
                # hello world HELLO WORLD
            ''',
        },
        {
            "syntax": "s.replace(old, new)",
            "explain": "Returns a new string with every occurrence of old replaced by new. Assign the result to keep it.",
            "example": r'''
                text = "a-b-a"
                text.replace("a", "x")
                print(text)
                # a-b-a
                text = text.replace("a", "x")
                print(text)
                # x-b-x
            ''',
        },
        {
            "syntax": "s.split()  /  s.split(sep)  /  s.splitlines()",
            "explain": "Return a list of pieces: cut at whitespace, cut at each sep, or cut at each line break.",
            "example": r'''
                print("the  quick\tfox".split())
                # ['the', 'quick', 'fox']
                print("a,b,,c".split(","))
                # ['a', 'b', '', 'c']
                print("one\ntwo\n".splitlines())
                # ['one', 'two']
            ''',
        },
        {
            "syntax": "sep.join(items)",
            "explain": "Returns one string with sep between the items. You call it on the separator. Every item must be a string.",
            "example": r'''
                words = "Big   Cat".split()
                print("-".join(words))
                # Big-Cat
                print(" ".join(words))
                # Big Cat
            ''',
        },
        {
            "syntax": "x in s  /  s.startswith(x)  /  s.endswith(x)",
            "explain": "Each is True or False: x appears anywhere in s, at the start, at the end. All three are case-sensitive.",
            "example": r'''
                name = "Notes.MD"
                print("otes" in name, name.startswith("notes"))
                # True False
                print(name.lower().endswith(".md"))
                # True
                print(name.find("."), name.find("?"))
                # 5 -1
            ''',
        },
        {
            "syntax": "s[start:stop]",
            "explain": "Returns the characters from index start up to, but not including, stop. Leave one out to go from the start or to the end.",
            "example": r'''
                s = "Hello, model"
                print(len(s), s[0], s[-1])
                # 12 H l
                print(s[:5])
                # Hello
                print(s[7:])
                # model
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Strings & Text Processing

### Strings are sequences

A **string** is a sequence of characters. Each character has an **index**: a whole
number that gives its position, starting at `0`. `len(s)` returns the number of
characters. A **slice** `s[start:stop]` returns a new string with the characters from
index `start` up to, but not including, index `stop`. Indexes and slices work the same
way as they do on a list: `s[-1]` is the last character, `s[:5]` starts at index `0`
and `s[7:]` goes to the end.

```python
s = "Hello, model"
print(len(s))
# 12
print(s[0], s[-1])
# H l
print(s[:5])
# Hello
print(s[7:])
# model
```

Drag the start and stop handles to see which characters a slice returns.

```diagram
{"type":"slice","title":"Slicing the string s","name":"s","value":"Hello, model","start":7,"stop":12}
```

### Methods and immutability

A **method** is a function that belongs to a value. You call it with a dot:
`s.lower()`. A string is **immutable**: its characters cannot change after it is
created. No string method changes the string. A method such as `strip()` returns a
new string, so you must store the result.

`repr(text)` returns the string the way you would type it in code: with its quotes,
and with a newline shown as `\n`. Printing it shows where the string starts and ends.

```python
text = "  Hi \n"
text.strip()
print(repr(text))
# '  Hi \n'
text = text.strip()
print(repr(text))
# 'Hi'
```

### Cleaning

**Whitespace** means spaces, tabs (`\t`) and newlines (`\n`). `strip()` returns the
string without the whitespace at both ends. `lower()` and `upper()` return the string
with every letter in lower case or upper case. `replace(old, new)` returns the string
with every occurrence of `old` replaced by `new`. You can **chain** methods: write one
call directly after another, and each call runs on the result of the call before it.

```python
raw = "  GPT-4o Mini \n"
print(raw.strip().lower())
# gpt-4o mini
print("a-b-a".replace("a", "x"))
# x-b-x
```

### Splitting and joining

A **run** of whitespace is one or more whitespace characters in a row. `split()` with
no argument cuts at every run of whitespace and returns a list with no empty strings.
`split(",")` cuts at every `","`. The text you cut at is called the **separator**. A
second argument, **maxsplit**, limits the number of cuts. `splitlines()` returns a list
of the lines without their `\n` characters.

```python
print("a  b\tc".split())
# ['a', 'b', 'c']
print("a,b,,c".split(","))
# ['a', 'b', '', 'c']
print("hf/meta/llama".split("/", 1))
# ['hf', 'meta/llama']
print("one\ntwo\n".splitlines())
# ['one', 'two']
```

`sep.join(items)` returns one string with `sep` between the items. You call it on
the separator, and `items` is a list of strings. Splitting and then joining with one
space replaces every run of whitespace with a single space. This is called **whitespace normalisation**.

```python
words = "the   quick\n\nfox".split()
print(" ".join(words))
# the quick fox
print("\n".join(["one", "two"]))
# one
# two
```

### Searching

`in` checks whether one string appears anywhere in another. `startswith` and
`endswith` check the two ends. `find` returns the index of the first match, or `-1`
when there is none. `count` returns the number of occurrences.

```python
text = "the model replied"
print("model" in text)
# True
print(text.startswith("the"), text.endswith(".md"))
# True False
print(text.find("model"), text.find("42"))
# 4 -1
print(text.count("e"))
# 4
```

All of these checks are case-sensitive: `"M"` and `"m"` are different characters.
Lower-case both sides when case should not matter: `word.lower() in text.lower()`.

### Common mistakes

- `text.strip()` on a line by itself changes nothing. The new string is discarded.
  Write `text = text.strip()`.
- `words.join(" ")` raises `AttributeError` (the value has no method with that name),
  because lists have no `join` method.
  Write `" ".join(words)`.
- `"a  b".split(" ")` returns `['a', '', 'b']`. Use `split()` with no argument to get words.
- `a, b = s.split("/", 1)` raises `ValueError` when `s` has no `/`. Check `"/" in s` first.
- An empty string is **falsy**: it counts as `False` in an `if`. `if line.strip():`
  skips blank lines.
'''

EXERCISES = [
    {
        "id": "strings-s1",
        "title": "Method chain",
        "difficulty": 0,
        "lesson": r'''
            ## Strings and string methods

            A **string** is a sequence of characters. Prompts, documents and model replies
            are all strings. Each character has an index that starts at `0`, the same way
            list items do. A negative index counts from the end, so `word[-1]` is the last
            character. `len` returns the number of characters, and a slice such as
            `word[:3]` returns part of the string: here the characters at indexes 0, 1 and 2.

            ```python
            word = "prompt"
            print(len(word))
            # 6
            print(word[0], word[-1])
            # p t
            print(word[:3])
            # pro
            ```

            Click a character to see both of its indexes.

            ```diagram
            {"type":"string-index","title":"Indexes of word","name":"word","value":"prompt"}
            ```

            A **method** is a function that belongs to a value. You call it with a dot
            after the value. `strip()` returns the text without the spaces at both ends,
            `upper()` returns it with every letter in upper case, and `split()` returns a
            list of the words. `startswith("Hi")` returns `True` when the string begins
            with `Hi`, and `False` when it does not.

            ```python
            text = "  Hi There  "
            clean = text.strip()
            print(clean)
            # Hi There
            print(clean.upper())
            # HI THERE
            print(clean.split())
            # ['Hi', 'There']
            print(text.startswith("Hi"))
            # False
            ```

            A string is **immutable**: its characters cannot change after it is created.
            No method changes the original string. `strip()` and `upper()` each return a
            new string.

            `text.strip()` did not change `text`. `text` still starts with two spaces, so
            `text.startswith("Hi")` is `False`.
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
            ## strip, lower and upper

            **Whitespace** is the name for spaces, tabs (`\t`) and newlines (`\n`). Text
            typed by users often has whitespace at the start or at the end.

            `strip()` returns a new string with all whitespace removed from both ends.

            ```python
            raw = "\t  Summarise this document.  \n"
            print(repr(raw.strip()))
            # 'Summarise this document.'
            print(repr("  a  b  ".strip()))
            # 'a  b'
            ```

            `repr` returns the string the way you would type it in code, with its quotes,
            so you can see where it starts and ends.

            `lower()` returns a copy with every letter in lower case. `upper()` returns a
            copy with every letter in upper case.

            ```python
            title = "Hello World"
            print(title.lower())
            # hello world
            print(title.upper())
            # HELLO WORLD
            ```

            You can **chain** methods: write one call directly after another. Python runs
            them left to right, and each method runs on the result of the one before it.

            ```python
            raw = "  GPT-4o Mini \n"
            print(raw.strip().upper())
            # GPT-4O MINI
            ```

            `strip()` only removes whitespace at the two ends. The two spaces between `a`
            and `b` in the first example are still there.
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
            ## replace returns a new string

            `replace(old, new)` returns a new string in which every occurrence of `old` is
            replaced by `new`. The original string stays as it was.

            ```python
            msg = "hello world, hello again"
            fixed = msg.replace("hello", "hi")
            print(fixed)
            # hi world, hi again
            print(msg)
            # hello world, hello again
            ```

            If `old` does not appear in the string, `replace` returns the same text.

            Strings are **immutable**: their characters cannot change after they are
            created. So a call to `replace` on a line by itself has no effect. Python
            builds the new string and then discards it, because no name refers to it.

            ```python
            setting = "temperature=0.7"
            setting.replace("0.7", "0.2")
            print(setting)
            # temperature=0.7
            setting = setting.replace("0.7", "0.2")
            print(setting)
            # temperature=0.2
            ```

            To keep the result, assign it to a name: `setting = setting.replace(...)`.

            The same mistake happens with `strip()`, `lower()` and every other string
            method. None of them changes the original string.
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
            ## Splitting text into words

            `split()` cuts a string at its whitespace and returns a **list** of the pieces.

            ```python
            line = "the  quick\tbrown\nfox"
            words = line.split()
            print(words)
            # ['the', 'quick', 'brown', 'fox']
            print(len(words))
            # 4
            print("   ".split())
            # []
            ```

            A **run** of whitespace is one or more spaces, tabs or newlines in a row. With
            no argument, `split()` makes one cut at each run, whatever its length. The
            list never contains empty strings. Text that is empty or only
            whitespace gives the empty list `[]`.

            You can also pass a **separator**: the exact text to cut at.

            ```python
            print("a,b,c".split(","))
            # ['a', 'b', 'c']
            ```

            The number of words is a quick estimate of how long a text is.

            `split(" ")` with a space as the separator cuts at every single space. Two
            spaces in a row produce an empty string.

            ```python
            print("a  b".split(" "))
            # ['a', '', 'b']
            print("a  b".split())
            # ['a', 'b']
            ```
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
            ## Joining a list into one string

            `join` does the reverse of `split`. It takes a list of strings and returns one
            string, with a separator between the items.

            ```python
            parts = ["gpt", "4o", "mini"]
            print("-".join(parts))
            # gpt-4o-mini
            print(" ".join(["hello", "there"]))
            # hello there
            print(", ".join(["a", "b", "c"]))
            # a, b, c
            ```

            `join` is a method of the separator string, so the separator comes first:
            `"-".join(parts)`. Python puts the separator only **between** the items. It
            never adds one at the start or at the end.

            A common sequence is to split text into words and then join the words with a
            different separator.

            ```python
            words = "Big  Cat".split()
            print(words)
            # ['Big', 'Cat']
            print("_".join(words))
            # Big_Cat
            ```

            `parts.join("-")` raises `AttributeError: 'list' object has no attribute 'join'`.
            Lists have no `join` method. Every item in the list must also be a string:
            `"-".join(["gpt", 4])` raises `TypeError`, because `4` is an int.
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
            ## startswith and endswith

            Programs often check one end of a string. A file name that ends with `.txt` is
            a text file. A reply that starts with `"Error"` is a failed request.

            `startswith(x)` returns `True` if the string begins with `x`. `endswith(x)`
            returns `True` if the string finishes with `x`. Otherwise they return `False`.

            ```python
            name = "notes.TXT"
            print(name.endswith(".txt"))
            # False
            print(name.lower().endswith(".txt"))
            # True
            print("/help".startswith("/"))
            # True
            ```

            Both methods return a **boolean**: the value `True` or `False`. You can use
            the result directly in an `if` or after `return`.

            To check whether some text appears **anywhere** in a string, use `in`.

            ```python
            print("key" in "my api key")
            # True
            print("Key" in "my api key")
            # False
            ```

            All of these checks are case-sensitive: `"T"` and `"t"` are different
            characters. `"notes.TXT".endswith(".txt")` is `False`. Call `lower()` first
            when upper and lower case should count as the same.
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
            "Two string methods together solve this: one breaks text into words, the other joins words back together.",
            "split() with no argument splits on ANY run of whitespace and drops empty pieces. Join the pieces with a single space.",
            "Call text.split() to get the words, then return \" \".join(...) of that list. Empty or whitespace-only text gives an empty list, which joins to \"\".",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Whitespace normalisation

            Text copied out of a PDF has runs of spaces, tabs and newlines between its
            words. You can replace every run with one separator in two steps: split the
            text into words, then join the words.

            ```python
            messy = "one   two\n\nthree"
            pieces = messy.split()
            print(pieces)
            # ['one', 'two', 'three']
            print("|".join(pieces))
            # one|two|three
            ```

            `split()` with no argument cuts at every run of whitespace, whatever its
            length, and drops the whitespace. `join` then puts exactly one separator
            between each pair of words.

            Step through the stages to see the value at each one.

            ```diagram
            {"type":"flow","title":"From messy to one separator","steps":[{"label":"messy","detail":"The string has three spaces between one and two, and two newlines between two and three.","code":"'one   two\\n\\nthree'"},{"label":"split()","detail":"split() cuts at each run of whitespace. It returns a list of the words and discards the whitespace.","code":"['one', 'two', 'three']"},{"label":"\"|\".join(pieces)","detail":"join builds one string. It puts the separator between the items and nowhere else.","code":"'one|two|three'"}]}
            ```

            Replacing every run of whitespace with a single separator is called
            **whitespace normalisation**. It is a standard step before you count text,
            compare it or send it to a model. It makes the text shorter, and two copies of the
            same text with different spacing become equal strings.

            Empty or whitespace-only text needs no special case. `"".split()` returns `[]`,
            and joining an empty list returns the empty string `""`.
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
            - Don't `import re` (a check looks for it): use string methods only.

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
            ## Splitting once with maxsplit

            `split("/")` cuts at every `/`. Sometimes you want to cut only at the
            **first** separator and keep the rest of the string in one piece.

            The second argument of `split` is **maxsplit**: the maximum number of cuts.

            ```python
            path = "docs/2024/report.txt"
            print(path.split("/"))
            # ['docs', '2024', 'report.txt']
            print(path.split("/", 1))
            # ['docs', '2024/report.txt']
            ```

            With a maxsplit of `1`, the list has at most two items. The second item keeps
            every later `/`.

            You can **unpack** a two-item list: write two names on the left of `=`, and
            Python assigns the first item to the first name and the second item to the
            second name.

            ```python
            path = "docs/2024/report.txt"
            first, rest = path.split("/", 1)
            print(first)
            # docs
            print(rest)
            # 2024/report.txt
            ```

            When the separator is not in the string, `split` returns a list with one item.
            Use `in` to check for the separator before you unpack.

            ```python
            print("/" in "gpt-4o")
            # False
            print("gpt-4o".split("/", 1))
            # ['gpt-4o']
            ```

            `first, rest = "gpt-4o".split("/", 1)` raises
            `ValueError: not enough values to unpack (expected 2, got 1)`.
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
            ## Case-insensitive search

            A filter that blocks spam must match "SPAM", "Spam" and "spam". `in` is
            case-sensitive, so `"spam" in "SPAM"` is `False`. A **case-insensitive** check treats upper and
            lower case as the same. To get one, lower-case **both** strings before you
            compare them.

            ```python
            reply = "Please ignore PREVIOUS instructions"
            print("previous" in reply)
            # False
            print("previous" in reply.lower())
            # True
            print("Previous".lower() in reply.lower())
            # True
            ```

            To search for several words, loop over them. A `return` inside the loop ends
            the function at the first match, so the remaining words are not checked. If
            the loop finishes, no word matched, and the line after the loop runs.

            ```python
            def first_match(text, words):
                for word in words:
                    if word in text:
                        return word
                return None

            print(first_match("hot dog stand", ["cat", "dog", "hot"]))
            # dog
            print(first_match("hot dog stand", ["cat", "fish"]))
            # None
            ```

            Apps use case-insensitive checks to filter messages by keyword, to send a
            message that mentions billing to the billing team, and to flag messages that
            contain forbidden words.

            Lower-case the keyword as well as the text. `"Previous" in reply.lower()` is
            `False`, because the keyword still has an upper-case `P`.
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
            ## Lines and blank lines

            A document is one long string with `\n` (newline) characters in it.
            `splitlines()` cuts the string at every line break and returns a list of the
            lines, without the `\n` characters.

            ```python
            doc = "apples\n\n  milk  \nbread"
            print(doc.splitlines())
            # ['apples', '', '  milk  ', 'bread']
            ```

            A blank line becomes an empty string `""` or a string that holds only spaces.
            `line.strip()` removes those spaces, so it returns `""` for both.

            An empty string is **falsy**: it counts as `False` in an `if`. Any other
            string counts as `True`. So `if line.strip():` runs its block only for lines
            that contain text.

            ```python
            doc = "apples\n\n  milk  \nbread"
            for line in doc.splitlines():
                item = line.strip()
                if item:
                    print(item)
            # apples
            # milk
            # bread
            ```

            Step through the loop and watch `item` on the blank line.

            ```diagram
            {"type": "trace", "title": "Skipping the blank line", "code": ["doc = \"apples\\n\\n  milk  \\nbread\"", "for line in doc.splitlines():", "    item = line.strip()", "    if item:", "        print(item)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'"}, "out": ""},
              {"line": 3, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'apples'"}, "out": ""},
              {"line": 4, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'apples'", "item": "'apples'"}, "out": ""},
              {"line": 5, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'apples'", "item": "'apples'"}, "out": ""},
              {"line": 2, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'apples'", "item": "'apples'"}, "out": "apples\n"},
              {"line": 3, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "''", "item": "'apples'"}, "out": "apples\n"},
              {"line": 4, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "''", "item": "''"}, "out": "apples\n", "note": "item is the empty string, which is falsy, so line 5 is skipped."},
              {"line": 2, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "''", "item": "''"}, "out": "apples\n"},
              {"line": 3, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'  milk  '", "item": "''"}, "out": "apples\n"},
              {"line": 4, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'  milk  '", "item": "'milk'"}, "out": "apples\n"},
              {"line": 5, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'  milk  '", "item": "'milk'"}, "out": "apples\n"},
              {"line": 2, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'  milk  '", "item": "'milk'"}, "out": "apples\nmilk\n"},
              {"line": 3, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'bread'", "item": "'milk'"}, "out": "apples\nmilk\n"},
              {"line": 4, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'bread'", "item": "'bread'"}, "out": "apples\nmilk\n"},
              {"line": 5, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'bread'", "item": "'bread'"}, "out": "apples\nmilk\n"},
              {"line": 2, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'bread'", "item": "'bread'"}, "out": "apples\nmilk\nbread\n"},
              {"line": null, "vars": {"doc": "'apples\\n\\n  milk  \\nbread'", "line": "'bread'", "item": "'bread'"}, "out": "apples\nmilk\nbread\n"}
            ]}
            ```

            `split("\n")` also cuts at newlines, but it returns an extra `""` at the end
            when the text ends with a newline. `splitlines()` does not.

            ```python
            print("a\nb\n".split("\n"))
            # ['a', 'b', '']
            print("a\nb\n".splitlines())
            # ['a', 'b']
            ```
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
