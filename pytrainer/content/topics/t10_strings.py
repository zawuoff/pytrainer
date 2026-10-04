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
            ## Looking inside a piece of text

            A prompt, a document, a reply from a model: almost everything an AI app handles is text. And
            text rarely arrives in the shape you need. A reply has spaces around it. A file name has
            capital letters where you expected none. This chapter is about the tools that deal with that.
            It starts with a question: what is a string made of?

            ```python
            word = "prompt"
            print(len(word))
            # 6
            print(word[0], word[-1])
            # p t
            print(word[:3])
            # pro
            ```

            A string is a row of characters, and Python treats that row much like a list. `len` counts the
            characters. Index `0` is the first character and index `-1` is the last. The slice `word[:3]`
            takes the characters at indexes 0, 1 and 2 and hands them back as a new string.

            Values that keep their contents in a row like this are called **sequences**. A list is a
            sequence of items, and a string is a sequence of characters. Click a character to see both of
            its indexes:

            ```diagram
            {"type":"string-index","title":"Indexes of word","name":"word","value":"prompt"}
            ```

            Pick the gap that makes this program print `de`:

            ```fill
            name = "claude"
            print(name[___])
            ---
            - [x] -2: :: Right. A start of `-2` counts from the end, and with no stop the slice runs to the end of the string. That is the last two characters.
            - [ ] -2 :: Without the colon this is one index, not a slice. It reads the single character `d`.
            - [ ] :2 :: With no start, the slice begins at the first character. It takes the first two characters and prints `cl`.
            ```

            ### Tools that come with every string

            In the Data Types chapter you met `strip()`, `lower()` and `upper()`. They are methods: you
            write them after a string and a dot, and each one hands back a new string. Two more methods
            appear in this step. Later steps come back to both, so a first look is enough here.

            ```python
            text = "  Ask me anything  "
            clean = text.strip()
            print(clean.upper())
            # ASK ME ANYTHING
            print(clean.split())
            # ['Ask', 'me', 'anything']
            print(clean.startswith("Ask"))
            # True
            ```

            `split()` cuts the string at its spaces and hands back a list of the words.
            `startswith("Ask")` answers a yes-or-no question: does the string begin with exactly this
            text? The answer is `True` or `False`.

            Every one of those lines used `clean`. What about `text` itself, now that `text.strip()` has
            run?

            ```predict
            text = "  Ask me anything  "
            clean = text.strip()
            print(len(text), len(clean))
            print(text.startswith("Ask"))
            ---
            Strings are immutable, so no method can change one. `text.strip()` built a new string of 15 characters, and `clean` is the name for it. `text` still has all 19 characters. It begins with a space, not with `Ask`, so the answer is `False`.
            ```

            **Watch out:** a method works on the string in front of its dot, and on no other. When you ask
            the wrong string, there is no error message. The program runs and gives a correct answer about
            a string you did not mean. So before you read a line such as `text.startswith("Ask")`, look at
            which name stands in front of the dot, and at what that name holds.

            **In short:** a string is a sequence of characters that you can index and slice like a list,
            and its methods hand back new values and leave the string itself as it was.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
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
            `strip()` takes the two spaces off each end, so `clean` is `"Hello World"`. The first `print`
            shows it in small letters. `len(clean)` counts 11 characters: five letters, the space in the
            middle, and five more letters. `split()` cuts at that space and hands back a list of the two
            words, which Python prints in square brackets with the words in single quotes. The last line
            asks about `text`, not about `clean`. No method changed `text`, so it still begins with two
            spaces, and the answer is `False`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Start by working out what `clean` holds. Three of the four `print` lines use it.",
            "`strip()` takes whitespace off the two ends only, and the space between the two words is a character that `len` counts. Before you answer the last line, look at which name stands in front of the dot.",
            "Your first line is `clean` in small letters. Your second line is the number of characters in `clean`, with the space in the middle counted. Your third line is a list of two words, written the way Python prints a list. Your fourth line is `True` or `False`: does the string that still has its spaces begin with `Hello`?",
        ],
    },
    {
        "id": "strings-s2",
        "title": "Tidy a user message",
        "difficulty": 0,
        "lesson": r'''
            ## Trimming the ends of a string

            A user types a message, taps the space bar a few times and presses Enter. Your program receives
            `"  Hello \n"`. On the screen it looks like a clean `Hello`, because spaces and newlines are
            invisible. To Python it is a different string from `"Hello"`, and a comparison of the two says
            `False`.

            So the first job is to see what is really there:

            ```python
            raw = "\t Summarise this. \n"
            print(repr(raw))
            # '\t Summarise this. \n'
            print(repr(raw.strip()))
            # 'Summarise this.'
            ```

            `repr(raw)` hands back the string written the way you would type it in code: inside quotes,
            with `\t` for a tab and `\n` for a newline. Printing that shows exactly where the string
            starts and ends. The checks in this app show your results in the same form.

            Spaces, tabs and newlines have one name together: **whitespace**. `strip()`, which you know
            from the Data Types chapter, removes all the whitespace at both ends, however much there is. It
            stops at the first character that is not whitespace, so it never reaches the middle.

            ```predict
            line = "  a  b \n"
            print(repr(line.strip()))
            print(len(line.strip()))
            ---
            The two spaces in front are gone, and so are the space and the newline at the end. The two spaces between `a` and `b` are in the middle, so they stay. `'a  b'` has 4 characters.
            ```

            ### Other characters at the ends

            Put a string in the parentheses, and `strip` removes those characters instead of whitespace:

            ```python
            word = "...wait!?"
            print(word.strip(".!?"))
            # wait
            print("(a.b)".strip("()."))
            # a.b
            ```

            The argument is not a word to look for. Python reads it as single characters, and each one is
            a character to remove. The order in which you write them does not matter. At each end, Python
            removes characters for as long as they are among the ones you named, and stops at the first
            one that is not. The dot between `a` and `b` is in the middle, so it stays. You will need this
            later in the chapter, to take the punctuation off words.

            Pick the argument that makes this program print `'Setup'`:

            ```fill
            tag = "## Setup ##"
            print(repr(tag.strip(___)))
            ---
            - [x] "# " :: Right. Both `#` and the space are named, so Python keeps removing until it reaches the `S` on one side and the `p` on the other.
            - [ ] "#" :: Only `#` is named, so Python stops at the spaces. This prints `' Setup '`, with a space on each side.
            - [ ] " " :: Only the space is named, and the string begins and ends with `#`. Nothing is removed.
            ```

            ### One method after another

            `strip()` hands back a string, so the next method can follow it directly, as in
            `raw.strip().upper()`. Python works from left to right: it strips first, and then makes
            capitals of the result. In the Lists chapter this was called chaining.

            **Watch out:** `strip("the")` does not remove the word `the`. It removes the characters `t`,
            `h` and `e` from both ends. `"the theme".strip("the")` gives `" them"`: the `the` in front is
            gone, and so is the `e` at the end. There is no error to warn you.

            **In short:** `text.strip()` removes the whitespace at both ends of a string,
            `text.strip(chars)` removes the characters you name instead, and neither touches the middle.
        ''',
        "prompt": r'''
            People type messages with stray spaces at the ends and with capital letters in odd places.
            Before a chat app compares a message with anything or stores it, it tidies the message up.

            **Your job:** finish `tidy(text)` so that it gives back the tidied message. The function is
            already written except for one gap, marked `___`. The part that makes the letters small is
            there. The part that trims the two ends is missing.

            **What goes in**
            - `text`: a string, for example `"  Hello THERE \n"`

            **What comes out**
            - a string: `text` without the whitespace (spaces, tabs, newlines) at both ends, and with
              every letter small: `"hello there"` for the example value

            **Rules**
            - Whitespace in the middle stays as it is.
            - A text that is already tidy comes back unchanged.

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
            "Which method takes the whitespace off both ends of a string? You met it in the Data Types chapter, and the lesson takes a closer look at it.",
            "The gap sits where the name of a method belongs: after the dot and before the parentheses. That method has to hand back a string, because `.lower()` is then called on its result.",
            "Read the finished line from left to right: start with `text`, trim its two ends, then make the letters small. The gap is the name of the method that does the trimming. Write the name only, because its parentheses are already there.",
        ],
    },
    {
        "id": "strings-s3",
        "title": "Fix: the redaction does nothing",
        "difficulty": 0,
        "lesson": r'''
            ## Swapping one piece of text for another

            You wrote a prompt with a placeholder in it: `"Dear NAME, your order has shipped."`. For each
            customer, `NAME` has to become a real name. The same need turns up when a secret must be
            hidden before a text is saved. One piece of text comes out, and another goes in its place.

            ```python
            msg = "hello world, hello again"
            fixed = msg.replace("hello", "hi")
            print(fixed)
            # hi world, hi again
            print(msg)
            # hello world, hello again
            ```

            `replace` takes two arguments: the text to look for, and the text to put in its place. It
            finds every place where the first one appears, not only the first place, and hands back a new
            string with the swap made in all of them.

            Three details. Capital letters count: to `replace`, `A` and `a` are different characters. When
            the text to look for is not in the string at all, you get back a string equal to the original,
            and that is not an error. And the second argument may be the empty string `""`, which deletes
            what was found.

            ```match
            `"a-b-a".replace("a", "x")` :: `"x-b-x"`
            `"a-b-a".replace("-", "")` :: `"aba"`
            `"a-b-a".replace("A", "x")` :: `"a-b-a"`
            `"a-b-a".replace("a-b", "c")` :: `"c-a"`
            ---
            Every `a` is swapped, not only the first one. Swapping the dashes for the empty string deletes them. A capital `A` is not in the string, so it comes back as it was. And the text to look for can be several characters long: `a-b` is found once, at the start.
            ```

            ### Where did the new string go?

            Look at the last line of the first example: `msg` still says `hello`. Strings are immutable,
            so `replace` cannot change `msg`. It builds a new string and hands it back, the same way
            `strip()` does. So what happens when nobody takes that new string?

            ```quiz
            What does this program print?

            ~~~python
            setting = "temperature=0.7"
            setting.replace("0.7", "0.2")
            print(setting)
            ~~~
            - [x] `temperature=0.7` :: Right. The second line builds the string `"temperature=0.2"`, and then nothing stores it, so it is lost. `setting` still stands for the original.
            - [ ] `temperature=0.2` :: That needs an assignment: `setting = setting.replace("0.7", "0.2")`. The method alone cannot change what `setting` stands for.
            - [ ] Nothing, because of an error :: Calling a method and ignoring what it hands back is allowed. It only has no effect.
            ```

            A method call on a line of its own makes sense for `append`, which changes its list in place.
            A string method never changes its string. What it hands back has to go somewhere: under a
            name, into `print`, or after `return`.

            **Watch out:** a `replace` whose result is not stored does nothing, and Python gives no
            warning. When a text comes out of your function unchanged, look for a method call that stands
            on a line of its own.

            **In short:** `text.replace(old, new)` hands back a new string with every `old` swapped for
            `new`, and you have to store that string to keep it.
        ''',
        "prompt": r'''
            A program that writes its prompts to a log file must never write an API key there. An API key
            is the secret password for a paid service, and anyone who can read the log could use it. So
            before a prompt is logged, the key in it is swapped for the placeholder `[KEY]`. Hiding a
            secret in this way is called redacting it.

            **Your job:** find the bug in `redact(text)` and fix it. The code is already in the editor. At
            the moment the function gives back the text exactly as it came in, with the key still in it.

            **What goes in**
            - `text`: a string, for example `"my key is sk-secret"`

            **What comes out**
            - a string: `text` with `"sk-secret"` swapped for `"[KEY]"`: `"my key is [KEY]"` for the
              example value

            **Rules**
            - Every `"sk-secret"` in the text is swapped, not only the first one.
            - A text without `"sk-secret"` comes back unchanged.

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
            "What does `replace` do with the new string it builds? The quiz in the lesson shows what happens when nobody takes it.",
            "The first line of the function does build the redacted string. Then nothing stores it, and the `return` line hands back the old `text`.",
            "Make sure that the string which `replace` hands back is the one that reaches `return`. You can store it under a name and return that name, or you can return what `replace` hands back directly.",
        ],
    },
    {
        "id": "strings-s4",
        "title": "Count the words",
        "difficulty": 0,
        "lesson": r'''
            ## Splitting text into words

            How long is this prompt? Before anything more exact, programmers often answer with a rough count of its words. To count words you first have to get them apart, and real text does not make that easy: some words have two spaces after them, some have a tab, some end a line.

            You met `split()` in the first step of this chapter. Here is what it does with that mess:

            ```python
            line = "the  quick\tbrown\nfox"
            words = line.split()
            print(words)
            # ['the', 'quick', 'brown', 'fox']
            ```

            Between `the` and `quick` there are two spaces, and a tab and a newline sit further on. `split()` coped with all of it. A stretch of one or more whitespace characters in a row is called a **run** of whitespace. With nothing in the parentheses, `split()` makes one cut at each run, however long it is, and throws the whitespace away. What you get is a list, so everything you know about lists works on it.

            Try it before you read on:

            ```predict
            note = "  tokens\t\tand   costs\n"
            print(note.split())
            print(note.split()[-1])
            ---
            The whitespace at the two ends and between the words is cut away, and no empty strings are left behind. The list holds three words, and `[-1]` reads the last one, `costs`.
            ```

            A text with no words in it gives a list with no items:

            ```python
            print("     ".split())
            # []
            ```

            `split()` never puts an empty string in its list. A list with no items has a `len` of `0`.

            ### Cutting at a piece of text you choose

            Sometimes you want to cut at one particular piece of text, such as a comma. Put it in the parentheses. Programmers call it the **separator**, and Python cuts at every single copy of it:

            ```python
            print("gpt,claude,llama".split(","))
            # ['gpt', 'claude', 'llama']
            ```

            So what happens when the separator is a space and two spaces sit side by side?

            ```quiz
            What does `"a  b".split(" ")` return? (There are two spaces between the letters.)
            - [x] `['a', '', 'b']` :: Right. Python cuts at each space on its own. The two cuts sit next to each other, so an empty string is left between them.
            - [ ] `['a', 'b']` :: That is what `split()` with nothing in the parentheses returns. A separator that you name is taken literally, so the double space is two cuts, not one.
            - [ ] `['a b']` :: The string does contain spaces, and Python cuts at every one it finds. It does not stay in one piece.
            ```

            That is why splitting text into words uses `split()` with the parentheses empty. Make this program print `['gpt', 'claude', 'llama']`:

            ```try
            text = "gpt  claude\tllama"
            print(text.split(" "))
            ---
            The program prints an empty piece and two names stuck together. Change one thing so that it prints `['gpt', 'claude', 'llama']`.
            ---
            text = "gpt  claude\tllama"
            print(text.split())
            ---
            A tab is whitespace but it is not a space, so `split(" ")` did not cut there. With nothing in the parentheses, every run of whitespace is one cut.
            ```

            **Watch out:** `text.split(" ")` looks like `text.split()` but behaves differently. A double space leaves an empty string in the list, and a tab or a newline is not cut at all. No error warns you. The list is simply wrong, and so is anything you count from it.

            **In short:** `text.split()` cuts at every run of whitespace and hands back the list of words, which is empty when there are none.
        ''',
        "prompt": r'''
            A rough word count is a quick way to estimate how long a document is, for example before you decide whether it fits into a prompt.

            **Your job:** write `word_count(text)` so that it gives back how many words `text` contains.

            **What goes in**
            - `text`: a string, for example `"the quick  brown\nfox"`

            **What comes out**
            - an int: the number of words, `4` for the example value

            **Rules**
            - Words are separated by whitespace: spaces, tabs or newlines, in any amount. Extra whitespace between two words never adds a word.
            - A text that is empty, or holds only whitespace, has `0` words.

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
            "The job has two steps: get the words apart, then count them. The lesson shows the first step, and you used `len` on lists in the Lists chapter.",
            "Cutting a string with nothing in the parentheses ignores extra whitespace, and a text without words gives an empty list. A list with no items has a length of 0, so the blank case needs no code of its own.",
            "One `return` line is enough. Cut `text` into words with that method, and put the result inside the built-in function that counts how many items a list has.",
        ],
    },
    {
        "id": "strings-s5",
        "title": "Make a slug",
        "difficulty": 0,
        "lesson": r'''
            ## Joining a list into one string

            You are saving a prompt to a file, and its title is `My First Prompt`. File names and web addresses are happier without spaces, so you want `my-first-prompt`. The last step cut text apart into a list of words. Now you need the way back: take a list of words and glue them into one string, with a dash between them.

            ```python
            parts = ["gpt", "4o", "mini"]
            name = "-".join(parts)
            print(name)
            # gpt-4o-mini
            print(", ".join(["red", "green", "blue"]))
            # red, green, blue
            ```

            Read `"-".join(parts)` as "use the dash to join the items of `parts`". The string in front of the dot is the glue, and the list goes inside the parentheses. The method is called `join`. Python puts the glue **between** the items. It never adds any at the start or at the end.

            Work out where the glue goes before you run this:

            ```predict
            print("+".join(["a", "b", "c"]))
            print("+".join(["solo"]))
            print(repr("+".join([])))
            ---
            Glue goes between neighbours. Three items have two gaps, so two plus signs. One item has no neighbour, so no glue appears. An empty list has no items at all, so the result is the empty string, which `repr` shows as two quote marks with nothing between them.
            ```

            ### Split, then join

            Cutting a text into words and gluing them back with something else takes two steps, one after the other:

            ```python
            phrase = "hello   big world"
            words = phrase.split()
            print(words)
            # ['hello', 'big', 'world']
            print("_".join(words))
            # hello_big_world
            ```

            `split()` takes the extra spaces away and `join` puts exactly one piece of glue in each gap. Put these four lines in the order that makes the program print `hello_big_world`:

            ```order
            phrase = "hello   big world"
            words = phrase.split()
            joined = "_".join(words)
            print(joined)
            ---
            A name has to exist before a line can use it. `phrase` comes first, then `words` is made from it, then `joined` is made from `words`, and `print` shows the result last.
            ```

            The glue comes first in `join` and the list goes inside the parentheses. It is easy to turn that around:

            ```quiz
            You have `parts = ["gpt", "4o"]` and you want the text `gpt-4o`. Which line makes it?
            - [x] `"-".join(parts)` :: Right. `join` is called on the glue, and the list goes inside the parentheses.
            - [ ] `parts.join("-")` :: A list has no `join` method. Python stops with `AttributeError: 'list' object has no attribute 'join'`.
            - [ ] `join("-", parts)` :: `join` only exists as a method, written after a string and a dot. On its own the name is unknown, and Python stops with `NameError: name 'join' is not defined`.
            ```

            **Watch out:** every item must be a string. `"-".join(["gpt", 4])` stops with `TypeError: sequence item 1: expected str instance, int found`, because `4` is a number. Turn it into text first with `str(4)`, as you learned in the Data Types chapter.

            **In short:** `glue.join(items)` makes one string from a list of strings, with the glue between the items and nowhere else.
        ''',
        "prompt": r'''
            A slug is a short name made only of small letters and dashes, safe to use in a file name or a web address. An app can use one to save the prompt titled `My First Prompt` as `my-first-prompt`.

            **Your job:** write `slugify(title)` so that it gives back the slug for a title.

            **What goes in**
            - `title`: a string of words, for example `"My First  Prompt"`

            **What comes out**
            - a string: the words of the title in small letters, with a single `-` between neighbouring words: `"my-first-prompt"` for the example value

            **Rules**
            - Words are separated by whitespace in any amount. Extra spaces, in the middle or at either end of the title, never produce an empty piece or an extra dash.
            - There is no dash at the start or at the end.
            - A title with one word gives just that word, in small letters.

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
            "Three small jobs, each with a tool from this chapter or the one before: make the letters small, get the words apart, and put the words back together with a dash.",
            "Cutting with nothing in the parentheses already removes the extra spaces, so no dash can come out doubled or at an end. The glue goes in front of the dot of the joining method, and the list of words goes inside its parentheses.",
            "Write one `return` line and read it from the inside out. Make the title small, cut that result into words, and join the words with a dash as the glue. The first two steps are two methods chained one after the other, and the joining wraps around them.",
        ],
    },
    {
        "id": "strings-s6",
        "title": "Is it Markdown?",
        "difficulty": 0,
        "lesson": r'''
            ## Does it start or end with this?

            A document loader receives file names, and it can only open the ones that end in `.md`. How does it ask? In the first step you met `startswith`, which answers a yes-or-no question about the beginning of a string. It has a partner, `endswith`, that asks about the end.

            ```python
            name = "report.pdf"
            print(name.endswith(".pdf"))
            # True
            print(name.endswith(".md"))
            # False
            print("/help".startswith("/"))
            # True
            ```

            Each of them answers `True` or `False`. That is a **boolean**, the type you met in the Data Types chapter. You can put the answer straight after `return`, or use it in an `if`.

            Both methods compare the text exactly, capital letters included, the same way `replace` did. Work out what that means here:

            ```predict
            upload = "Photo.PNG"
            print(upload.endswith(".png"))
            print(upload.lower().endswith(".png"))
            print(upload.endswith(".PNG"))
            ---
            The first check compares exactly, and `.PNG` is not `.png`. Making the string small first turns `Photo.PNG` into `photo.png`, so the second check finds the ending. The third check asks for the capitals that are really there, so it also gives `True`.
            ```

            When capitals should not matter, make the string small first and ask afterwards, as the second line of that program did.

            ### Anywhere in the text

            `startswith` and `endswith` look at one end only. To ask whether a piece of text appears anywhere inside a string, use `in`. You used it on lists in the Lists chapter, and on strings it works the same way:

            ```python
            print("key" in "my api key")
            # True
            print("Key" in "my api key")
            # False
            ```

            It is exact about capitals too. Match each question with the line that asks it:

            ```match
            Does `name` begin with `data`? :: `name.startswith("data")`
            Does `name` end with `.json`? :: `name.endswith(".json")`
            Does `json` appear anywhere in `name`? :: `"json" in name`
            Does `json` appear in `name`, whatever the capitals? :: `"json" in name.lower()`
            ---
            `startswith` and `endswith` look at one end only, and `in` looks everywhere. The last line makes `name` small first, so `JSON` and `Json` count too.
            ```

            **Watch out:** a name in capitals gets a quiet `False`. `"README.MD".endswith(".md")` is `False`, and Python does not warn you that the only difference is the capital letters.

            **In short:** `text.startswith(x)` and `text.endswith(x)` ask about the two ends and `x in text` asks about anywhere, all three answer `True` or `False`, and all three care about capital letters.
        ''',
        "prompt": r'''
            A document loader reads only Markdown files, which are text files whose names end in `.md`. Before it opens a file, it checks the file's name.

            **Your job:** finish `is_markdown(filename)` so that it tells whether a file name belongs to a Markdown file. The function is already written except for one gap, marked `___`. The part that makes the letters small is there. The part that asks how the name finishes is missing.

            **What goes in**
            - `filename`: a string, for example `"README.md"`

            **What comes out**
            - `True` when the name ends with `.md`, and `False` when it does not

            **Rules**
            - Capital letters do not matter: `"NOTES.MD"` is a Markdown file.
            - Only the end of the name counts. A name that has `md` somewhere else, such as `"md_notes.txt"`, is not Markdown.

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
            "Which two string methods answer a yes-or-no question about one end of a string? You met the first one in the first step of this chapter, and this lesson adds its partner.",
            "One of the two looks at the beginning and the other at the end. This task is about how the name finishes. The gap holds a method name and nothing else, because the dot before it and the parentheses with the text after it are already written.",
            "Say the finished line aloud: \"the file name, made small, finishes with `.md`\". The gap is the word that stands for \"finishes with\". Type the name of that method only, with no dot and no parentheses.",
        ],
    },
    {
        "id": "strings-1",
        "title": "Normalise whitespace",
        "hints": [
            "Think about the difference between words and their whitespace boundaries.",
            "Separate on any whitespace, then rebuild with one consistent separator.",
            "Split without a literal separator, join the resulting words with one space, and return the rebuilt string.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Make inconsistent spacing predictable

            Text copied from a document may put three spaces between words, a tab after a heading, and a newline in the middle of a sentence. You want the words without letting those layout choices change the text you compare or count.

            ```python
            copied = "  red\t green\nblue  "
            words = copied.split()
            print(words)
            # ['red', 'green', 'blue']
            print(" / ".join(words))
            # red / green / blue
            ```

            Calling `split` without a separator treats a run of whitespace as one boundary. It also drops whitespace at either end, so it does not invent empty words there. Then `join` places your chosen separator between the words, without adding it before the first or after the last.

            ```predict
            pieces = " \t\n ".split()
            print(pieces)
            print("-".join(pieces) == "")
            ---
            Whitespace alone contains no words, so splitting produces an empty list. Joining that list produces an empty string.
            ```

            Giving different-looking inputs one consistent representation is **normalisation**. Here you are normalising whitespace, which is useful when accidental spacing should not matter. It does discard line breaks and indentation, so do not apply it when those carry meaning, such as Python source code.

            ```quiz
            Why does replacing one double space with one space miss some cases?
            - [x] Tabs, newlines, and longer runs still need handling. :: Splitting on whitespace recognizes all those boundaries together.
            - [ ] Python cannot replace spaces inside strings. :: Replacement works; the issue is covering all permitted whitespace.
            ```

            **Watch out:** `split(" ")` behaves differently from `split()`: repeated literal spaces can produce empty pieces, and tabs are not treated as the chosen separator.

            Separate the words first, then choose how their boundaries should look.
        ''',
        "prompt": r'''
            Text pasted from PDFs is full of stray spaces, tabs and newlines. Clean it up
            before sending it to a model.

            **Your job:** write `normalize_ws(text)`

            **What goes in**
            - `text`: a string, e.g. `"  Hello \t\n  world  "`

            **What comes out**
            - a string where every run of whitespace (spaces, tabs, newlines)
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
            "Clean the outside and case before deciding whether a provider was supplied.",
            "A single cut preserves any later slashes as part of the model name.",
            "Normalize the string, handle the missing-slash case with the default provider, otherwise split once and return the two parts as a tuple.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Split the first boundary and keep the rest

            A stored name contains a category followed by a longer path. You need to separate the category without breaking up all the later path components. A limit on the number of cuts gives you exactly that control.

            ```python
            location = "archive/2025/notes.txt"
            print(location.split("/"))
            # ['archive', '2025', 'notes.txt']
            print(location.split("/", 1))
            # ['archive', '2025/notes.txt']
            ```

            The second argument limits the number of splits, not the number of pieces. It is called **maxsplit** in the documentation. One split can produce two pieces. Everything after that first boundary remains together, including later copies of the separator.

            ```fill
            location = "archive/2025/notes.txt"
            print(location.split("/", ___))
            ---
            - [x] 1 :: One cut leaves the remaining path together as the second piece.
            - [ ] 2 :: Two cuts break the year away from the filename too.
            - [ ] 0 :: Zero cuts leave the complete string in one piece.
            ```

            Remember unpacking from the variables chapter: two names can receive a two-item result. But a split limit is a maximum, not a guarantee. If the separator is absent, the result contains the original string as its only item. Decide what that missing boundary means before attempting to unpack two pieces.

            ```predict
            print("readme".split("/", 1))
            print("/" in "readme")
            ---
            No separator is present, so there is one unchanged piece and the membership check is False.
            ```

            **Watch out:** unpacking that one-item list into two names raises `ValueError: not enough values to unpack`. A missing separator needs its own behavior.

            Limit the number of cuts when the remainder belongs together.
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

            **Your job:** write `parse_model_id(model_id)`

            **What goes in**
            - `model_id`: a string, e.g. `"Anthropic/Claude-3"`

            **What comes out**
            - a **tuple** of two strings `(provider, model)`, e.g.
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
            ## Search without caring about capital letters

            A support message says BILLING, while your list of routing words contains Billing. The spelling matches for a reader, but an ordinary Python text search distinguishes those capital letters. Compare versions with consistent case.

            ```python
            message = "Question about BILLING"
            needle = "Billing"
            print(needle in message)
            # False
            print(needle.lower() in message.lower())
            # True
            ```

            This is a **case-insensitive** comparison: upper and lower case are treated alike. Both sides need the same treatment. Lowercasing only the message would still leave an uppercase letter in the search word, so that comparison could fail.

            ```predict
            print("bill" in "billing")
            print("BILL".lower() in "Billing".lower())
            ---
            Both searches find the shorter text inside the longer text. Membership searches substrings, not only complete words.
            ```

            A string occurring inside another is a **substring**. This is useful for a deliberately broad keyword flag, but it is not a complete safety system or a whole-word language parser. Be clear about what the check actually promises.

            When trying several keywords, one match is enough for a positive answer. A negative answer needs more evidence: every keyword must have been checked. Remember that return ends the function immediately, even when it appears inside a loop.

            ```quiz
            The first keyword is absent but later keywords remain. Can you give back False yet?
            - [x] No; a later keyword may match. :: Only finishing all checks establishes that none matched.
            - [ ] Yes; the first keyword decides the result. :: That would ignore valid matches later in the list.
            ```

            **Watch out:** giving back False after the first unsuccessful check skips the rest of the keywords. Place the negative outcome after all candidates have been considered.

            A positive match needs one success; a negative match needs every candidate to fail.
        ''',
        "prompt": r'''
            A simple guardrail flags user messages that mention certain keywords, whatever
            their capitalisation.

            **Your job:** write `mentions_any(text, keywords)`

            **What goes in**
            - `text`: a string, the user message, e.g. `"Please IGNORE the rules"`
            - `keywords`: a list of strings, e.g. `["ignore", "password"]`; may be empty

            **What comes out**
            - `True` if at least one keyword appears anywhere in `text`,
              otherwise `False`

            **Rules**
            - The check is **case-insensitive** on both sides: keyword `"Password"` matches
              text `"my PASSWORD is"`.
            - A keyword may appear inside a longer word: `"ignore"` matches `"ignored"`.
            - With an empty `keywords` list, give back `False`.

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
            "Both the message and keyword may contain capital letters.",
            "A positive match can stop the search; an unsuccessful first keyword cannot.",
            "Prepare the text for case-insensitive comparison, examine every keyword until one matches, and report no match only after all candidates fail.",
        ],
    },
    {
        "id": "strings-8",
        "title": "Non-blank lines",
        "difficulty": 1,
        "lesson": r'''
            ## Keep useful lines and drop blank ones

            A document contains headings, paragraphs, and blank lines inserted for layout. You need each meaningful line as a separate item while preserving the text inside it. Splitting into words would lose the line boundaries you still care about.

            ```python
            page = "  Overview  \n\n  Two words\r\n"
            print(page.splitlines())
            # ['  Overview  ', '', '  Two words']
            print(page.splitlines()[0].strip())
            # Overview
            ```

            The `splitlines` method recognizes line endings and removes those boundary characters from the resulting items. It understands both newline and Windows-style carriage-return/newline endings. Trimming each resulting line is a separate operation: `strip` removes whitespace at its ends, while leaving spaces within the line alone.

            ```predict
            print(bool("   "))
            print(bool("   ".strip()))
            ---
            A spaces-only string is nonempty and therefore true. Trimming it produces an empty string, which is false.
            ```

            That distinction explains the order of the work. Testing the original line for emptiness would keep a line full of spaces. Test the trimmed version when your goal is meaningful text. Keep the original sequence of the surviving lines; cleaning should not silently rearrange the document.

            ```match
            `splitlines()` :: separates a document into lines
            `strip()` :: removes whitespace at both ends of one string
            an empty cleaned line :: contains no text to keep
            ```

            An empty document naturally produces no lines. A final line ending does not invent an extra useful line either, so the same process works when a saved file ends with a newline.

            **Watch out:** splitting on whitespace would also cut a line such as `Two words` into two items. Choose boundaries that match the structure you need.

            Find the lines first, then decide which cleaned lines contain text.
        ''',
        "prompt": r'''
            Before chunking a document you want its real lines: trimmed, with blank lines
            dropped.

            **Your job:** write `clean_lines(text)`

            **What goes in**
            - `text`: a string with newlines, e.g. `"  intro \n\n body\n"`

            **What comes out**
            - a list of strings: each line of `text` with whitespace removed
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

            Both `\n` and Windows-style `\r\n` line endings count as line boundaries.
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
            "Line boundaries and word boundaries are different.",
            "Trim a line before checking whether it has any content left.",
            "Split into lines, trim each one, append only nonempty results in order, and return that list.",
        ],
    },
    {
        "id": "strings-3",
        "title": "Truncate to N words",
        "hints": [
            "Compare the full word count with the requested preview size.",
            "The ellipsis means words were omitted, not merely that the limit was reached.",
            "Separate words on whitespace, keep the permitted prefix, join with spaces, and append the ellipsis only when some original words were left out.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Search results show a short preview of each long document. Build that preview.

            **Your job:** write `truncate_words(text, n)`

            **What goes in**
            - `text`: a string, e.g. `"The quick brown fox jumps"` (may contain newlines)
            - `n`: an `int` >= 0, the maximum number of words to keep, e.g. `3`

            **What comes out**
            - a string: the kept words joined by single spaces, plus `"..."`
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
            "Combine the dictionary counting pattern with per-word cleaning.",
            "Strip only the listed punctuation at word boundaries, preserving internal characters.",
            "Split words, clean and lowercase each one, skip empty results, then increase the stored count under that cleaned word.",
        ],
        "difficulty": 2,
        "prompt": r'''
            Word frequencies are a first step in keyword search over documents.

            **Your job:** write `word_counts(text)`

            **What goes in**
            - `text`: a string, e.g. `"The cat. THE dog!"`

            **What comes out**
            - a `dict` mapping each word (a lower-case string) to how many
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
            "Each wrapping layer has its own position and removal rule.",
            "Compare prefixes using lowercase text, but preserve the case of the actual answer.",
            "Follow the stated stages in order: outside whitespace, at most one prefix, complete outer fence, then paired outer quotes; keep internal text intact.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Models often wrap an answer in chatter, code fences or quotes. Strip that
            wrapping so only the answer is left.

            **Your job:** write `clean_reply(reply)`

            **What goes in**
            - `reply`: a string, the raw model output, e.g. `"  Sure! Here it is  "`

            **What comes out**
            - the cleaned string.

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
            "Build the instruction and context separately before assembling their headings.",
            "Preserve the instruction's existing case except for its first letter, and number only nonblank snippets.",
            "Clean the instruction, prepare snippets in order, build the required section lines with the specified blank lines, then join them and include the final newline.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A RAG app turns a task plus retrieved chunks into one prompt for the model.
            Build that prompt from a block of text.

            **Your job:** write `build_prompt(raw)`

            **What goes in**
            - `raw`: a string with one item per line, e.g.
              `"summarise the docs\nFirst chunk\n\n  Second chunk \n"`
              - line 1 is the task instruction
              - every following line is a context snippet

            **What comes out**
            - one string in exactly this format, where every line (including
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
