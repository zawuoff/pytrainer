TOPIC = {
    "id": "comprehensions",
    "title": "Comprehensions",
    "track": "working-python",
    "order": 2,
    "requires": ["lists", "dicts", "loops"],
    "summary": """
        List, dict and set comprehensions, filtering, nested comprehensions and
        generator expressions with sum/any/all.
    """,
    "concepts": ["list comprehension", "dict comprehension", "set comprehension",
                 "filtering", "conditional expression", "nested comprehension",
                 "generator expression", "sum / any / all"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["comprehension", "list comprehension", "dict comprehension", "set comprehension",
                 "filter", "generator expression", "sum", "any", "all", "flatten",
                 "conditional expression", "one line loop"],
    "cards": [
        {
            "syntax": "[expression for item in iterable]",
            "explain": "Builds a new list: one result of the expression per item, in the same order.",
            "example": r'''
                words = ["token", "prompt"]
                print([len(w) for w in words])
                # [5, 6]
                print([w.upper() for w in words])
                # ['TOKEN', 'PROMPT']
            ''',
        },
        {
            "syntax": "[expression for item in iterable if condition]",
            "explain": "The if at the end is a filter. Items where the condition is false are skipped.",
            "example": r'''
                scores = [0.9, 0.2, 0.7]
                print([s for s in scores if s >= 0.5])
                # [0.9, 0.7]
                print([s * 10 for s in scores if s < 0.5])
                # [2.0]
            ''',
        },
        {
            "syntax": "[a if condition else b for item in iterable]",
            "explain": "The if ... else at the front picks a value for every item. No item is skipped and the else is required.",
            "example": r'''
                scores = [0.9, 0.2, 0.7]
                print(["pass" if s >= 0.5 else "fail" for s in scores])
                # ['pass', 'fail', 'pass']
            ''',
        },
        {
            "syntax": "{key: value for item in iterable}",
            "explain": "Builds a dict. Left of the colon is the key, right of it is the value. A repeated key keeps the last value.",
            "example": r'''
                words = ["hi", "hello"]
                print({w: len(w) for w in words})
                # {'hi': 2, 'hello': 5}
                print({w[0]: w for w in words})
                # {'h': 'hello'}
            ''',
        },
        {
            "syntax": "{expression for item in iterable}",
            "explain": "Curly braces with no colon build a set: each value once, in no order. An empty set is set(), not {}.",
            "example": r'''
                tags = ["ai", "rag", "ai"]
                unique = {t.upper() for t in tags}
                print(len(tags), len(unique))
                # 3 2
                print("AI" in unique)
                # True
            ''',
        },
        {
            "syntax": "sum(expression for item in iterable)",
            "explain": "A generator expression has no brackets and builds no list. Pass it to sum, min, max, any or all.",
            "example": r'''
                lengths = [120, 800, 40]
                print(sum(n for n in lengths if n > 100))
                # 920
                print(any(n > 500 for n in lengths))
                # True
                print(all(n > 500 for n in lengths))
                # False
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Comprehensions

A **comprehension** is one expression that builds a new list, dict or set from the
items of an iterable. An **iterable** is any value a `for` loop can go through item
by item, such as a list, a string or a `range`. An expression is code that produces
a value.

### List comprehensions

The form is `[expression for item in iterable]`. Python takes each item in turn,
evaluates the expression and puts the result in a new list. The new list has the
same length and the same order as the iterable.

```python
words = ["token", "", "prompt"]
print([len(w) for w in words])
# [5, 0, 6]
```

Here `w` is the name for the current item, and `len(w)` is the expression. The empty
string has length `0`.

### Filters

An `if` after the `for` part is a **filter**. Python evaluates the expression only
for the items where the condition is true. The other items are skipped. In the next
example the condition is `w`. An empty string is falsy, so `""` is skipped.

```python
words = ["token", "", "prompt"]
print([len(w) for w in words if w])
# [5, 6]
```

That comprehension does the same work as this loop. Step through it to see which
items reach `append`.

```diagram
{"type": "trace", "title": "The for loop that [len(w) for w in words if w] replaces", "code": ["words = [\"token\", \"\", \"prompt\"]", "lengths = []", "for w in words:", "    if w:", "        lengths.append(len(w))", "print(lengths)"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {"words": "['token', '', 'prompt']"}, "out": ""},
  {"line": 3, "vars": {"words": "['token', '', 'prompt']", "lengths": "[]"}, "out": ""},
  {"line": 4, "vars": {"words": "['token', '', 'prompt']", "lengths": "[]", "w": "'token'"}, "out": ""},
  {"line": 5, "vars": {"words": "['token', '', 'prompt']", "lengths": "[]", "w": "'token'"}, "out": ""},
  {"line": 3, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5]", "w": "'token'"}, "out": ""},
  {"line": 4, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5]", "w": "''"}, "out": ""},
  {"line": 3, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5]", "w": "''"}, "out": ""},
  {"line": 4, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5]", "w": "'prompt'"}, "out": ""},
  {"line": 5, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5]", "w": "'prompt'"}, "out": ""},
  {"line": 3, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5, 6]", "w": "'prompt'"}, "out": ""},
  {"line": 6, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5, 6]", "w": "'prompt'"}, "out": ""},
  {"line": null, "vars": {"words": "['token', '', 'prompt']", "lengths": "[5, 6]", "w": "'prompt'"}, "out": "[5, 6]\n"}
]}
```

### Conditional expressions

A **conditional expression** has the form `a if condition else b`. Its value is `a`
when the condition is true and `b` when it is false. Written at the front of a
comprehension, it picks a value for every item. No item is skipped.

```python
xs = [3, -1, 2]
print([x if x > 0 else 0 for x in xs])
# [3, 0, 2]
print([x for x in xs if x > 0])
# [3, 2]
```

### Dict and set comprehensions

Curly braces with `key: value` build a dict. Curly braces with one expression and
no colon build a set, which holds each value once and has no order. In the example,
`"token"` has length 5, `""` has length 0 and `"prompt"` has length 6.

```python
words = ["token", "", "prompt"]
print({w: len(w) for w in words if w})
# {'token': 5, 'prompt': 6}
print({len(w) for w in words})
# {0, 5, 6}
```

### Generator expressions

A **generator expression** is a comprehension written without square brackets or
curly braces. It produces its values one at a time and builds no list. You pass it
directly to a function such as `sum`, `min`, `max`, `any` or `all`. The parentheses
of the call are the only brackets it needs.

```python
words = ["token", "", "prompt"]
print(sum(len(w) for w in words))
# 11
```

### any and all

`any(...)` returns `True` when at least one value is truthy (counts as `True` in an
`if`). `all(...)` returns `True` when every value is truthy. With no values, `any` returns `False` and `all` returns `True`.
In the example, `n > 500` produces `False`, `True`, `False`.

```python
lengths = [120, 800, 40]
print(any(n > 500 for n in lengths))
# True
print(all(n > 500 for n in lengths))
# False
print(any([]), all([]))
# False True
```

### Two for clauses

A comprehension can have two `for` parts. Python runs them left to right, the same
way it runs a loop inside a loop. This turns a list of lists into one list of the
inner items.

```python
docs = [["a", "b"], ["c"]]
print([c for doc in docs for c in doc])
# ['a', 'b', 'c']
```

The first `for` takes each inner list as `doc`. The second `for` takes each item of
that `doc` as `c`. The expression at the front, `c`, goes into the new list.

### Common mistakes

- The filter goes inside the brackets, after the `for` part: `[x for x in xs if x > 0]`.
  It has no `else`.
- An `if` with `else` goes at the front: `[x if x > 0 else 0 for x in xs]`. Leaving out
  the `else` there raises `SyntaxError`.
- Dict keys are unique. When two items produce the same key, the later value
  replaces the earlier one: `{len(w): w for w in ["cat", "dog"]}` is `{3: 'dog'}`.
- `{}` is an empty dict. An empty set is written `set()`.
- A comprehension builds a new list, dict or set. It does not change the original one.
- When the logic needs several conditions and nested loops, a normal `for` loop is
  easier to read.
'''

EXERCISES = [
    {
        "id": "comprehensions-s1",
        "title": "Read the comprehension",
        "difficulty": 0,
        "lesson": r'''
            ## A whole loop in one line

            You have the token counts of three messages, and you want a second list in which every count
            is doubled. You know how to build it from the Loops chapter: start with an empty list, go
            through the counts, and append one result for each item.

            ```python
            counts = [3, 5, 8]
            doubled = []
            for c in counts:
                doubled.append(c * 2)
            print(doubled)
            # [6, 10, 16]
            ```

            Press Next and watch the new list grow by one item on each iteration:

            ```diagram
            {"type": "trace", "title": "The loop that [c * 2 for c in counts] replaces", "code": ["counts = [3, 5, 8]", "doubled = []", "for c in counts:", "    doubled.append(c * 2)", "print(doubled)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"counts": "[3, 5, 8]"}, "out": ""},
              {"line": 3, "vars": {"counts": "[3, 5, 8]", "doubled": "[]"}, "out": ""},
              {"line": 4, "vars": {"counts": "[3, 5, 8]", "doubled": "[]", "c": "3"}, "out": ""},
              {"line": 3, "vars": {"counts": "[3, 5, 8]", "doubled": "[6]", "c": "3"}, "out": ""},
              {"line": 4, "vars": {"counts": "[3, 5, 8]", "doubled": "[6]", "c": "5"}, "out": ""},
              {"line": 3, "vars": {"counts": "[3, 5, 8]", "doubled": "[6, 10]", "c": "5"}, "out": ""},
              {"line": 4, "vars": {"counts": "[3, 5, 8]", "doubled": "[6, 10]", "c": "8"}, "out": ""},
              {"line": 3, "vars": {"counts": "[3, 5, 8]", "doubled": "[6, 10, 16]", "c": "8"}, "out": ""},
              {"line": 5, "vars": {"counts": "[3, 5, 8]", "doubled": "[6, 10, 16]", "c": "8"}, "out": ""},
              {"line": null, "vars": {"counts": "[3, 5, 8]", "doubled": "[6, 10, 16]", "c": "8"}, "out": "[6, 10, 16]\n"}
            ]}
            ```

            That is three lines for one small idea: "`c * 2` for each `c` in `counts`". Python lets you
            write the idea almost the way you say it:

            ```python
            counts = [3, 5, 8]
            print([c * 2 for c in counts])
            # [6, 10, 16]
            ```

            Start reading in the middle. `for c in counts` is the `for` line of the loop, without its
            colon. In front of it stands `c * 2`, which is what the loop appended. The square brackets
            around everything say that the results are gathered in a new list. Python creates that list
            and does the appending for you.

            This short form is called a **list comprehension**. It does the same work as the loop, one
            item after the other.

            ```match
            `for c in counts` :: goes through the items and calls each one `c`
            `c * 2` :: is worked out for each item and goes into the new list
            `[` and `]` :: gather all the results in a new list
            ```

            ### Leaving items out

            An `if` at the end is a test. Only the items that pass it are used:

            ```python
            counts = [3, 5, 8]
            print([c for c in counts if c > 4])
            # [5, 8]
            ```

            `3 > 4` is false, so 3 is left out. In front stands the plain `c`, so 5 and 8 go into the
            new list unchanged.

            ```predict
            sizes = [4, 10, 15, 7]
            print([s + 1 for s in sizes])
            print([s for s in sizes if s % 5 == 0])
            ---
            The first comprehension has no `if`, so every item is used, and each result is one more than the item. In the second, `s % 5` is the remainder when `s` is divided by 5. It is 0 for 10 and for 15, so those two pass the test, and they are kept as they are.
            ```

            ### The same idea builds a dict

            With curly braces and a colon in front, the result is a dict. Left of the colon is the key
            and right of it is the value, as in a dict that you write by hand:

            ```python
            counts = [3, 5, 8]
            print({c: c * 2 for c in counts})
            # {3: 6, 5: 10, 8: 16}
            ```

            ```quiz
            What does `{c: c + 1 for c in [1, 2, 3] if c > 1}` build?
            - [x] `{2: 3, 3: 4}` :: Right. The `if` leaves out 1. Each of the other two numbers becomes a key, and its value is one more.
            - [ ] `{1: 2, 2: 3, 3: 4}` :: This uses all three numbers. The `if` at the end lets only the numbers greater than 1 through.
            - [ ] `[3, 4]` :: Those are the values only. Curly braces with a colon build a dict, so each value is stored under its key.
            - [ ] `{2: 2, 3: 3}` :: The keys are right. The value is the part after the colon, `c + 1`, so it is one more than the key.
            ```

            **Watch out:** the `if` at the end only decides which items are used. It never changes them.
            What goes into the result is always the part in front of `for`.

            **In short:** `[c * 2 for c in counts]` builds a new list with one result for each item, an
            `if` at the end leaves items out, and curly braces with `key: value` build a dict in the
            same way.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            nums = [1, 2, 3, 4, 5]
            print([n * 10 for n in nums])
            print([n for n in nums if n % 2 == 0])
            print({n: n * n for n in nums if n > 3})
        ''',
        "solution": r'''
            [10, 20, 30, 40, 50]
            [2, 4]
            {4: 16, 5: 25}
        ''',
        "explanation": r'''
            The first comprehension has no `if`, so all five numbers are used, and each result is the
            number times 10. In the second one, `n % 2` is the remainder when `n` is divided by 2. It is
            0 for the even numbers, so only 2 and 4 pass the test. The part in front is the plain `n`, so
            they are kept unchanged. The third one has curly braces and a colon, so it builds a dict.
            Only 4 and 5 pass `n > 3`. Each of them becomes a key, and its value is `n * n`: 16 for 4,
            and 25 for 5.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Read each comprehension as the loop it stands for: take every `n` in turn, check the `if` when there is one, and then work out the part in front of `for`.",
            "The first line has no `if`, so all five numbers are used. The second line keeps the numbers that leave no remainder when they are divided by 2. The third line has a colon in front, so it builds a dict from the numbers that pass its test.",
            "Your first line is a list of five numbers, each ten times as big as the original. Your second line is a list of the even numbers, unchanged. Your third line is a dict, written the way Python prints one: curly braces, and for each number greater than 3 the number, a colon, a space and the number times itself, with a comma and a space between the two pairs.",
        ],
    },
    {
        "id": "comprehensions-s2",
        "title": "Shout every word",
        "difficulty": 0,
        "lesson": r'''
            ## The same change for every item

            People type the name of a model in all sorts of ways: `"GPT-4o"`, `"Claude"`, `"LLAMA"`.
            Before your app compares the names with its own list, it needs all of them in small letters.
            With a loop, the change happens inside `append(...)`:

            ```python
            typed = ["GPT-4o", "Claude", "LLAMA"]
            clean = []
            for name in typed:
                clean.append(name.lower())
            print(clean)
            # ['gpt-4o', 'claude', 'llama']
            ```

            In a list comprehension, whatever stood inside `append(...)` moves to the front:

            ```python
            typed = ["GPT-4o", "Claude", "LLAMA"]
            print([name.lower() for name in typed])
            # ['gpt-4o', 'claude', 'llama']
            ```

            The `for` part gives each item the name `name`. The part in front uses that name to say what
            goes into the new list. Python works it out once for each item, so three items give three
            results, in the same order.

            The part in front does not have to be a method call. It can be any piece of code that
            produces a value. You met the word for that in the Data Types chapter: an **expression**.

            ```python
            typed = ["GPT-4o", "Claude", "LLAMA"]
            print([len(name) for name in typed])
            # [6, 6, 5]
            print([f"model: {name}" for name in typed])
            # ['model: GPT-4o', 'model: Claude', 'model: LLAMA']
            ```

            ```try
            tools = ["search", "email", "weather"]
            print([t for t in tools])
            ---
            The program prints the list unchanged. Change the expression in front of `for` so that it prints the number of characters of each name: `[6, 5, 7]`.
            ---
            tools = ["search", "email", "weather"]
            print([len(t) for t in tools])
            ---
            The `for` part stayed as it was. Only the expression in front changed, and that alone decides what goes into the new list.
            ```

            ### No items, no results

            An empty list is no problem. The `for` part has nothing to go through, so the expression is
            never worked out, and the new list is empty too:

            ```python
            print([n * 2 for n in []])
            # []
            ```

            ### One name, in two places

            ```quiz
            What happens when this line runs?

            ~~~python
            print([t.lower() for w in ["AI", "Rag"]])
            ~~~
            - [x] Python stops with a `NameError` :: Right. The `for` part calls each item `w`, and the expression in front asks for `t`. No variable `t` exists, so Python reports `NameError: name 't' is not defined`.
            - [ ] It prints `['ai', 'rag']` :: It would with `w.lower()` in front. The expression asks for `t`, and the `for` part never created that name.
            - [ ] It prints `['AI', 'Rag']` :: Python does not skip an expression that it cannot work out. The name `t` does not exist, so the program stops with an error.
            ```

            **Watch out:** a `NameError` in a comprehension nearly always means that the name in the
            expression and the name after `for` are not the same. Pick one name and use it in both
            places.

            **In short:** the expression in front of `for` is worked out once for each item, and each
            result becomes one item of the new list.
        ''',
        "prompt": r'''
            A chat app has a "shout" mode that shows every word of a message in capital letters.

            **Your job:** finish `shout_all(words)` so that it gives back a new list with every word in
            upper case. The function is already written except for one gap, marked `___`. Replace the
            gap.

            **What goes in**
            - `words`: a list of strings, for example `["hi", "there"]`. It may be empty.

            **What comes out**
            - a new list with the same words in the same order, each one in capital letters:
              `["HI", "THERE"]` for the example value

            **Rules**
            - An empty list gives `[]`.

            **Examples**
            ```python
            shout_all(["hi", "there"])   # returns ["HI", "THERE"]
            shout_all(["ok"])            # returns ["OK"]
            shout_all([])                # returns []
            ```
        ''',
        "starter": r'''
            def shout_all(words):
                return [___ for w in words]
        ''',
        "tests": r'''
            from solution import shout_all

            def test_every_word_is_upper_cased():
                got = shout_all(["hi", "there"])
                assert got == ["HI", "THERE"], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert shout_all([]) == []
        ''',
        "solution": r'''
            def shout_all(words):
                return [w.upper() for w in words]
        ''',
        "hints": [
            "The gap is the expression in front of `for`. Ask yourself what one item of the new list should be.",
            "The `for` part calls each word `w`. The gap has to turn that one word into capital letters, with a string method from the Strings chapter.",
            "Write the loop variable, a dot, and the name of the method that gives back a string in upper case, followed by a pair of parentheses. That takes the place of the three underscores.",
        ],
    },
    {
        "id": "comprehensions-s3",
        "title": "Fix: backwards lookup",
        "difficulty": 0,
        "lesson": r'''
            ## A lookup table from a list

            An agent has three tools, and you want to count how often each one is called. Every count
            starts at 0, so you need a dict such as `{"search": 0, "email": 0, "weather": 0}`. Typing it
            by hand works for three tools. It does not work when the list of tools is read from a config
            file.

            A loop can build the dict, one key at a time:

            ```python
            tools = ["search", "email", "weather"]
            calls = {}
            for t in tools:
                calls[t] = 0
            print(calls)
            # {'search': 0, 'email': 0, 'weather': 0}
            ```

            The comprehension with curly braces from the first step of this chapter does it in one line:

            ```python
            tools = ["search", "email", "weather"]
            print({t: 0 for t in tools})
            # {'search': 0, 'email': 0, 'weather': 0}
            ```

            The line `calls[t] = 0` of the loop has become `t: 0`. Left of the colon is the key, and
            right of it is the value. That is the order you use when you write a dict by hand. A
            comprehension with curly braces and a colon is called a **dict comprehension**.

            Both sides of the colon may be expressions that use the loop variable. Which side is which
            decides what you can look up later. The program below should print
            `{'en': 'EN', 'fr': 'FR'}`:

            ```fill
            codes = ["en", "fr"]
            print({___ for c in codes})
            ---
            - [x] c: c.upper() :: Right. Each code is a key, and its value is the same code in capital letters.
            - [ ] c.upper(): c :: The two sides are the wrong way round. The capitals become the keys, and the program prints `{'EN': 'en', 'FR': 'fr'}`.
            - [ ] c, c.upper() :: A dict comprehension needs a colon between the key and the value. With a comma in its place, Python stops with a `SyntaxError`.
            ```

            ### Each key only once

            The two sides cannot be swapped freely, and the reason is a rule from the Dicts chapter: a
            dict holds each key only once. Storing a value under a key that is already there replaces
            the old value.

            In the next program, `m[0]` is the first character of the string `m`, in the same way that
            `[0]` reads the first item of a list.

            ```predict
            models = ["gpt", "claude", "gemini"]
            by_letter = {m[0]: m for m in models}
            print(len(by_letter))
            print(by_letter["g"])
            ---
            `"gpt"` and `"gemini"` both give the key `"g"`. The dict can hold that key only once, so `"gemini"` replaced `"gpt"`. Three items went in and two entries came out, without any error.
            ```

            **Watch out:** when a dict comprehension gives you fewer entries than the list had items,
            two items produced the same key. Python does not warn you. Put on the left of the colon the
            thing that is different for every item.

            **In short:** `{key: value for item in items}` builds a dict, with the key on the left of
            the colon and the value on the right.
        ''',
        "prompt": r'''
            A text tool needs to look up quickly how long each word of a text is. Someone wrote a
            function that builds the lookup table as a dict, with each word as a key and the length of
            that word as its value. It has a bug: the table comes out backwards, with the lengths as the
            keys. Because of that, two words of the same length cannot both be in it.

            **Your job:** find the bug in `word_lengths(words)` and fix it. The code is already in the
            editor.

            **What goes in**
            - `words`: a list of strings, for example `["hi", "hello"]`

            **What comes out**
            - a dict in which each key is a word and its value is the number of characters of that word:
              `{"hi": 2, "hello": 5}` for the example value

            **Rules**
            - Words of the same length must all be in the dict, each under its own key.

            **Examples**
            ```python
            word_lengths(["hi", "hello"])   # returns {"hi": 2, "hello": 5}
            word_lengths(["cat", "dog"])    # returns {"cat": 3, "dog": 3}
            word_lengths([])                # returns {}
            ```
        ''',
        "starter": r'''
            def word_lengths(words):
                return {len(w): w for w in words}
        ''',
        "tests": r'''
            from solution import word_lengths

            def test_maps_word_to_length():
                got = word_lengths(["hi", "hello"])
                assert got == {"hi": 2, "hello": 5}, f"got {got!r}"

            def test_words_with_same_length_are_both_kept():
                got = word_lengths(["cat", "dog"])
                assert got == {"cat": 3, "dog": 3}, f"got {got!r}"
        ''',
        "solution": r'''
            def word_lengths(words):
                return {w: len(w) for w in words}
        ''',
        "hints": [
            "In a dict comprehension, which side of the colon is the key? The lesson shows it with `tools`.",
            "The task wants the word as the key and its length as the value. Compare that with what the code has on each side of the colon.",
            "The two expressions around the colon are the wrong way round. Make the word the left side and its length the right side. The rest of the line can stay as it is.",
        ],
    },
    {
        "id": "comprehensions-s4",
        "title": "Keep the short names",
        "difficulty": 0,
        "lesson": r'''
            ## Keep only the items that pass a test

            A retriever has handed back four similarity scores, and only the scores of 0.5 or more are
            worth using. With a loop you put an `if` around the `append`, so that only the scores that pass
            are added:

            ```python
            scores = [0.9, 0.2, 0.7, 0.4]
            kept = []
            for s in scores:
                if s >= 0.5:
                    kept.append(s)
            print(kept)
            # [0.9, 0.7]
            ```

            Press Next and watch which scores reach `append`:

            ```diagram
            {"type": "trace", "title": "The for loop that [s for s in scores if s >= 0.5] replaces", "code": ["scores = [0.9, 0.2, 0.7, 0.4]", "kept = []", "for s in scores:", "    if s >= 0.5:", "        kept.append(s)", "print(kept)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]"}, "out": ""},
              {"line": 3, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[]"}, "out": ""},
              {"line": 4, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[]", "s": "0.9"}, "out": ""},
              {"line": 5, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[]", "s": "0.9"}, "out": ""},
              {"line": 3, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9]", "s": "0.9"}, "out": ""},
              {"line": 4, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9]", "s": "0.2"}, "out": ""},
              {"line": 3, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9]", "s": "0.2"}, "out": ""},
              {"line": 4, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9]", "s": "0.7"}, "out": ""},
              {"line": 5, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9]", "s": "0.7"}, "out": ""},
              {"line": 3, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9, 0.7]", "s": "0.7"}, "out": ""},
              {"line": 4, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9, 0.7]", "s": "0.4"}, "out": ""},
              {"line": 3, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9, 0.7]", "s": "0.4"}, "out": ""},
              {"line": 6, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9, 0.7]", "s": "0.4"}, "out": ""},
              {"line": null, "vars": {"scores": "[0.9, 0.2, 0.7, 0.4]", "kept": "[0.9, 0.7]", "s": "0.4"}, "out": "[0.9, 0.7]\n"}
            ]}
            ```

            The comprehension does the same work. The `if` line of the loop moves to the end, after the
            `for` part, and what the loop appended moves to the front:

            ```python
            scores = [0.9, 0.2, 0.7, 0.4]
            print([s for s in scores if s >= 0.5])
            # [0.9, 0.7]
            ```

            Python goes through the scores one by one and checks the test. When it is true, the score goes
            into the new list. When it is false, Python skips the score and moves on to the next one. The
            scores that stay keep their order. An `if` at the end of a comprehension is called a
            **filter**.

            ```quiz
            `scores = [0.9, 0.2, 0.7]`. Which line builds `[0.9, 0.7]`?
            - [x] `[s for s in scores if s > 0.5]` :: Right. The filter sits after the `for` part, and the plain `s` in front keeps each score that passes as it is.
            - [ ] `[s for s in scores if s < 0.5]` :: The comparison is the wrong way round. It keeps the scores that are below 0.5, so the result is `[0.2]`.
            - [ ] `[s if s > 0.5 for s in scores]` :: An `if` in front of `for` belongs to a conditional expression, and that needs an `else`. Python stops with `SyntaxError: expected 'else' after 'if' expression`.
            - [ ] `[s for s in scores if s > 0.5 else 0]` :: A filter has no `else`. Scores that fail are skipped, not replaced, and Python stops with a `SyntaxError`.
            ```

            ### The test can ask about the item

            The test does not have to compare the item itself. It can ask a question about it. Here the
            test looks at the length of each tag, while the new list holds the tags themselves:

            ```python
            tags = ["rag", "agents", "llm", "evals"]
            print([t for t in tags if len(t) > 3])
            # ['agents', 'evals']
            ```

            ```fill
            models = ["gpt", "claude", "gemini", "phi"]
            print([m for m in models if ___])
            ---
            - [x] len(m) > 3 :: Right. `claude` and `gemini` have more than 3 characters, so the program prints `['claude', 'gemini']`.
            - [ ] len(m) :: A length is a number, and every number except 0 counts as true in a test. Nothing is left out, so all four names are printed.
            - [ ] m > 3 :: This compares text with a number. Python stops with `TypeError: '>' not supported between instances of 'str' and 'int'`.
            ```

            **Watch out:** items that fail the filter are skipped, never replaced. The new list can be
            shorter than the old one, and it is `[]` when no item passes.

            **In short:** `[item for item in items if test]` keeps the items for which the test is true, in
            their original order.
        ''',
        "prompt": r'''
            A chat window has a narrow column, and a long model name does not fit into it. The app wants to
            show only the names that are short enough.

            **Your job:** write `short_names(names)` so that it gives back a new list with only the short
            names.

            **What goes in**
            - `names`: a list of model names (strings), for example `["gpt-4o", "claude", "llama", "phi"]`.
              It may be empty.

            **What comes out**
            - a new list with the names that have 5 characters or fewer, in the order they had before:
              `["llama", "phi"]` for the example value

            **Rules**
            - A name with exactly 5 characters is kept.
            - The names that are kept are not changed.
            - Write it as a list comprehension with an `if` at the end. A check looks for a list
              comprehension.

            **Examples**
            ```python
            short_names(["gpt-4o", "claude", "llama", "phi"])   # returns ["llama", "phi"]
            short_names(["abcde"])                              # returns ["abcde"]
            short_names(["abcdef"])                             # returns []
            ```
        ''',
        "starter": r'''
            def short_names(names):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import short_names

            def test_names_longer_than_five_are_dropped():
                got = short_names(["gpt-4o", "claude", "llama", "phi"])
                assert got == ["llama", "phi"], f"got {got!r}"

            def test_name_with_exactly_five_chars_is_kept():
                assert short_names(["abcde"]) == ["abcde"]

            def test_uses_list_comprehension():
                tree = ast.parse(source())
                assert any(isinstance(n, ast.ListComp) for n in ast.walk(tree)), \
                    "use a list comprehension"
        ''',
        "solution": r'''
            def short_names(names):
                return [name for name in names if len(name) <= 5]
        ''',
        "hints": [
            "Look at the example with `tags` in the lesson. Which part of a comprehension decides whether an item is used at all?",
            "The new list holds the names themselves, so the part in front of `for` is only the loop variable. The test goes at the end, and it asks how many characters the name has.",
            "Write one `return` line with square brackets. Inside them put the loop variable, then the `for` part over `names`, then an `if` and a comparison between the length of the name and 5. Choose the comparison that lets a length of exactly 5 through.",
        ],
    },
    {
        "id": "comprehensions-s5",
        "title": "Total characters",
        "difficulty": 0,
        "lesson": r'''
            ## One number from many items

            Every message that you send to a model costs its token count plus 2 tokens for formatting. You
            want the total cost of three messages. This is the accumulator pattern from the Loops chapter: a
            variable that starts at 0, and each message adds its cost to it.

            ```python
            counts = [3, 5, 8]
            total = 0
            for c in counts:
                total += c + 2
            print(total)
            # 22
            ```

            You also know `sum`, which adds up the numbers of a list. So there is a second way: build the
            list of costs with a comprehension, then hand that list to `sum`.

            ```python
            counts = [3, 5, 8]
            costs = [c + 2 for c in counts]
            print(costs)
            # [5, 7, 10]
            print(sum(costs))
            # 22
            ```

            The list `costs` exists only to be added up. You can drop its name and its square brackets and
            write the comprehension directly inside the parentheses of `sum`:

            ```python
            counts = [3, 5, 8]
            print(sum(c + 2 for c in counts))
            # 22
            ```

            Without brackets, Python does not build a list first. It works out one cost, hands it to `sum`,
            which adds it, and then works out the next one. A comprehension without brackets, written inside
            the parentheses of a call, is called a **generator expression**. Its `for` is part of one
            expression. It is not a `for` loop statement, which is a line that starts with `for`, ends with a
            colon and has an indented body.

            ```try
            prices = [4, 6, 10]
            print([p * 3 for p in prices])
            ---
            The program prints each price times 3, as a list. Change the `print` line so that it prints the total of those three numbers, `60`, as one number.
            ---
            prices = [4, 6, 10]
            print(sum(p * 3 for p in prices))
            ---
            The comprehension stayed the same. It moved inside `sum(...)` and lost its brackets, and `sum` added up the three results.
            ```

            ### A filter, and no items at all

            A generator expression can have a filter, like any comprehension:

            ```predict
            sizes = [10, 20, 30]
            print(sum(s - 5 for s in sizes))
            print(sum(s for s in sizes if s > 15))
            ---
            Without a filter, every size counts: 5 + 15 + 25 is 45. With the filter, only 20 and 30 pass, and they are added as they are, which gives 50.
            ```

            ```quiz
            `counts` is an empty list. What does `sum(c + 2 for c in counts)` give?
            - [x] `0` :: Right. The `for` part has nothing to go through, so there is nothing to add, and the sum of no numbers is 0.
            - [ ] `None` :: `sum` always gives back a number. With nothing to add, that number is 0.
            - [ ] An error :: An empty list is fine. The loop body in the comprehension never runs, and `sum` simply starts and ends at 0.
            ```

            **Watch out:** the `for` part has to stay inside the parentheses of `sum`. In `sum(c + 2)`,
            `sum` is given one number instead of a series of them, and Python stops with
            `TypeError: 'int' object is not iterable`.

            **In short:** `sum(expression for item in items)` adds up one value for each item, and it gives 0
            when there are no items.
        ''',
        "prompt": r'''
            A RAG app cuts every document into chunks, which are pieces of text. To judge how big a document
            is, you want to know the total number of characters in all of its chunks.

            **Your job:** write `total_chars(chunks)` so that it gives back the number of characters in all
            the chunks together.

            **What goes in**
            - `chunks`: a list of strings, for example `["abc", "de", ""]`. It may be empty.

            **What comes out**
            - a whole number: the lengths of all the strings added together, `5` for the example value

            **Rules**
            - An empty list gives `0`.
            - Write it with `sum` and a generator expression. A check fails if your code contains a `for`
              loop statement, which is a line that starts with `for` and ends with a colon. A `for` inside a
              comprehension is fine.

            **Examples**
            ```python
            total_chars(["abc", "de", ""])   # returns 5
            total_chars(["hello"])           # returns 5
            total_chars([])                  # returns 0
            ```
        ''',
        "starter": r'''
            def total_chars(chunks):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import total_chars

            def test_adds_up_the_lengths_of_all_chunks():
                got = total_chars(["abc", "de", ""])
                assert got == 5, f"got {got!r}"

            def test_empty_list_returns_zero():
                assert total_chars([]) == 0

            def test_uses_sum_without_a_for_loop_statement():
                tree = ast.parse(source())
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), \
                    "use sum() with a comprehension, not a for statement"
        ''',
        "solution": r'''
            def total_chars(chunks):
                return sum(len(c) for c in chunks)
        ''',
        "hints": [
            "You need one number from many strings. Which function adds numbers up, and what has to be added for each string?",
            "Work out the length of every chunk and hand all those lengths to the function that adds. Write the comprehension straight inside its parentheses, with no square brackets.",
            "Write one `return` line. Call the adding function, and inside its parentheses put what to work out for one chunk, followed by the `for` part over `chunks`. An empty list needs no special case, because the sum of nothing is 0.",
        ],
    },
    {
        "id": "comprehensions-s6",
        "title": "Which roles appear?",
        "difficulty": 0,
        "lesson": r'''
            ## Which different values appear?

            People typed the names of models in different ways: `"GPT-4o"`, `"gpt-4o"`, `"Claude"`,
            `"claude"`. You want to know which models there are, once each, whatever the capital letters. A
            set is made for this, because it keeps one copy of each value. You can fill a set in a loop. The
            method `add` does for a set what `append` does for a list: it puts a value in, and when the
            value is already there, nothing changes.

            ```python
            typed = ["GPT-4o", "gpt-4o", "Claude", "claude"]
            models = set()
            for t in typed:
                models.add(t.lower())
            print(sorted(models))
            # ['claude', 'gpt-4o']
            ```

            A set has no order, so the program prints `sorted(models)`, which puts the values in
            alphabetical order and shows the same thing on every run. Four names went in, and two values
            stayed.

            The comprehension keeps the same two pieces as before: what went into `add` moves to the front,
            and the `for` line follows it. The brackets are curly braces with no colon:

            ```python
            typed = ["GPT-4o", "gpt-4o", "Claude", "claude"]
            print(sorted({t.lower() for t in typed}))
            # ['claude', 'gpt-4o']
            ```

            A comprehension with curly braces and no colon builds a **set comprehension**. The brackets
            decide what a comprehension builds:

            ```match
            `[t.lower() for t in typed]` :: a list that keeps every item, repeats included
            `{t.lower() for t in typed}` :: a set that keeps each value once
            `{t: t.lower() for t in typed}` :: a dict, because of the colon between key and value
            ```

            ```predict
            words = ["Hi", "hi", "HELLO", "hello", "hey"]
            unique = {w.lower() for w in words}
            print(len(words))
            print(len(unique))
            print("hello" in unique)
            ---
            `words` has 5 items. In small letters, `"Hi"` and `"hi"` are the same value, and so are `"HELLO"` and `"hello"`, so the set holds three values: hi, hello and hey. The last line is `True` because `"hello"` is one of them.
            ```

            ### The empty set

            ```quiz
            You need an empty set to start from. Which line makes one?
            - [x] `set()` :: Right. The name of the type, with nothing inside the parentheses, gives an empty set.
            - [ ] `{}` :: Python keeps empty curly braces for an empty dict, so this is a dict, not a set.
            - [ ] `[]` :: This is an empty list. A list can hold repeats, so it is not a set.
            ```

            A set comprehension over an empty list gives an empty set without any extra work:

            ```python
            print({t.lower() for t in []})
            # set()
            ```

            **Watch out:** Python prints an empty set as `set()`, never as `{}`, because `{}` is an empty
            dict.

            **In short:** `{expression for item in items}` builds a set, which holds each value once and has no
            order.
        ''',
        "prompt": r'''
            A chat log is a list of messages, and every message says who wrote it: `"user"`, `"assistant"`,
            `"system"` or `"tool"`. Before sending the log to a model, your app wants to know which different
            roles appear in it. How often each role appears does not matter.

            **Your job:** write `roles_used(messages)` so that it gives back a set of the different roles.

            **What goes in**
            - `messages`: a list of dicts, each like `{"role": "user", "content": "hi"}`. It may be empty.

            **What comes out**
            - a set that holds each role that appears at least once: `{"user", "assistant"}` for a chat with
              messages from the user and the assistant

            **Rules**
            - Each role is in the set once, however many messages have it.
            - An empty list gives an empty set. Python prints it as `set()`, because `{}` is an empty dict.
            - Write it as a set comprehension. A check looks for one.

            **Examples**
            ```python
            roles_used([{"role": "user", "content": "hi"},
                        {"role": "assistant", "content": "hello"},
                        {"role": "user", "content": "thanks"}])
            # returns {"user", "assistant"}

            roles_used([{"role": "tool", "content": "42"}])   # returns {"tool"}
            roles_used([])                                    # returns set()
            ```
        ''',
        "starter": r'''
            def roles_used(messages):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import roles_used

            def test_repeated_roles_appear_once():
                got = roles_used([{"role": "user", "content": "hi"},
                                  {"role": "assistant", "content": "hello"},
                                  {"role": "user", "content": "thanks"}])
                assert got == {"user", "assistant"}, f"got {got!r}"

            def test_result_is_a_set():
                got = roles_used([{"role": "tool", "content": "42"}])
                assert isinstance(got, set), f"got a {type(got).__name__}"

            def test_empty_list_returns_empty_set():
                got = roles_used([])
                assert got == set() and isinstance(got, set), f"got {got!r}"

            def test_uses_set_comprehension():
                tree = ast.parse(source())
                assert any(isinstance(n, ast.SetComp) for n in ast.walk(tree)), \
                    "use a set comprehension"
        ''',
        "solution": r'''
            def roles_used(messages):
                return {m["role"] for m in messages}
        ''',
        "hints": [
            "You want each role once, however many messages carry it. Which kind of comprehension from the lessons keeps only one copy of each value?",
            "Go through the messages. For each message, the value that belongs in the set is the one stored under the key that names the role. Curly braces with no colon build the set.",
            "Write one `return` line inside curly braces. In front of `for`, read the role out of the message with its key. After `for`, name the loop variable and go through `messages`. No `if` and no special case for an empty list are needed.",
        ],
    },
    {
        "id": "comprehensions-1",
        "title": "Token lengths",
        "hints": [
            "The condition decides whether to keep a chunk; the expression decides what to measure.",
            "Test whether trimmed text exists, but measure the original chunk.",
            "Write one list comprehension with the character count at the front and the nonblank test at the end, preserving input order.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Choose items, then transform the survivors

            A document list contains real text and empty entries left by an earlier step. You want measurements of the useful entries, without letting the rule for selecting them change what you measure. A comprehension can express these two decisions separately.

            ```python
            labels = [" map ", "", "  ", "notes"]
            sizes = [len(label) for label in labels if label.strip()]
            print(sizes)
            # [5, 5]
            ```

            Read the `for` part first: it gives each input item a name. Next read the final `if`: it decides whether this item contributes anything. Finally read the expression at the front: it calculates the value to include. This combines **filtering**, deciding what stays, with **transformation**, deciding what each kept item becomes.

            ```predict
            labels = [" map ", "", "notes"]
            print([label.upper() for label in labels if label])
            ---
            The empty string is skipped. The two remaining strings become uppercase, with their original surrounding spaces preserved.
            ```

            The filter does not edit the original value. Calling `strip` only in the condition asks whether meaningful text exists; it does not force the output expression to use trimmed text. That distinction matters when the result must count all original characters.

            ```quiz
            A condition uses a trimmed copy. What does the expression at the front receive?
            - [x] The original item bound by the for clause. :: Evaluating a condition does not reassign the item.
            - [ ] Only the trimmed copy. :: You must explicitly use a trimmed value in the output expression if that is wanted.
            ```

            **Watch out:** a string containing spaces is nonempty and therefore true. Testing the original string alone will keep whitespace-only entries.

            Treat the keep-or-skip decision and the output calculation as separate questions.
        ''',
        "research": {
            "note": "Skim the Python tutorial's section on list comprehensions (it shows the same idea with a for loop next to it), then come back.",
            "links": [
                {"title": "List Comprehensions - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions"},
            ],
        },
        "prompt": r'''
            Before embedding text chunks you want their sizes, ignoring blank chunks.

            **Your job:** write `chunk_lengths(chunks)`

            **What goes in**
            - `chunks`: a list of strings, e.g. `["hello", "  ", "hi there", ""]`

            **What comes out**
            - a list of ints - the length (in characters) of each kept chunk,
              in the original order

            **Rules**
            - Skip chunks that are empty (`""`) or contain only whitespace (like `"  "`).
            - A kept chunk's length counts every character, including its spaces:
              `" a b "` has length `5`.
            - An empty list returns `[]`.
            - Use a **single list comprehension**. A check fails if your file has a `for`
              loop statement.

            **Examples**
            ```python
            chunk_lengths(["hello", "  ", "hi there", ""])   # returns [5, 8]
            chunk_lengths([" a b "])                         # returns [5]
            chunk_lengths([])                                # returns []
            ```
        ''',
        "starter": r'''
            def chunk_lengths(chunks):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import chunk_lengths

            def test_empty_and_whitespace_only_chunks_are_skipped():
                got = chunk_lengths(["hello", "  ", "hi there", ""])
                assert got == [5, 8], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert chunk_lengths([]) == []

            def test_spaces_inside_a_kept_chunk_are_counted():
                got = chunk_lengths([" a b "])
                assert got == [5], f"got {got!r}"

            def test_uses_list_comprehension_and_no_for_statement():
                tree = ast.parse(source())
                assert any(isinstance(n, ast.ListComp) for n in ast.walk(tree)), \
                    "use a list comprehension"
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), \
                    "no for-loop statements - use a comprehension"
        ''',
        "solution": r'''
            def chunk_lengths(chunks):
                return [len(chunk) for chunk in chunks if chunk.strip()]
        ''',
    },
    {
        "id": "comprehensions-2",
        "title": "Model lookup table",
        "hints": [
            "Choose the field that will become each lookup key.",
            "Each retained record supplies a name and its context size; the retired flag determines exclusion.",
            "Build a dictionary comprehension using the two required fields, and retain records only when their deprecated flag is false.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Turn records into a lookup by name

            A service returns a list of records, but your next step repeatedly asks for a value by name. Searching the entire list each time repeats work. Build a dictionary whose keys are the names you want to look up.

            ```python
            people = [{"name": "Mina", "active": True, "level": 3},
                      {"name": "Leo", "active": False, "level": 1}]
            levels = {p["name"]: p["level"] for p in people if p["active"]}
            print(levels)
            # {'Mina': 3}
            print(levels["Mina"])
            # 3
            ```

            The colon separates the key expression from the value expression. Each retained record supplies one pair. This **dictionary comprehension** follows the same iteration and filtering order as a list comprehension, but builds a keyed lookup instead of a sequence.

            ```fill
            records = [{"name": "Mina", "disabled": False}]
            print({r["name"]: 1 for r in records if ___ r["disabled"]})
            ---
            - [x] not :: Inverting the disabled flag keeps the enabled record.
            - [ ] + :: False behaves like zero here, so the record would be discarded.
            - [ ] - :: Negating False also gives zero and discards the record.
            ```

            Translate flags carefully. A field called `active` may be kept when true; a field called `disabled` usually means the opposite. Read the field's meaning rather than copying a condition from another example.

            ```quiz
            What happens if no records pass the condition?
            - [x] The result is an empty dictionary. :: No retained record contributes a key-value pair.
            - [ ] The result is None. :: A dictionary comprehension always produces a dictionary.
            ```

            **Watch out:** repeated keys replace earlier values, as with ordinary dictionary assignment. A lookup is not a way to keep multiple separate entries under the same key.

            Choose the lookup key, the stored value, and the inclusion rule independently.
        ''',
        "prompt": r'''
            Turn a list of model records into a quick lookup table of context windows.

            **Your job:** write `context_table(models)`

            **What goes in**
            - `models`: a list of dicts, each like
              `{"name": "gpt-4o", "context": 128000, "deprecated": False}`

            **What comes out**
            - a dict mapping each **non-deprecated** model's `"name"` to its
              `"context"` value

            **Rules**
            - Leave out every model whose `"deprecated"` is `True`.
            - An empty list, or a list where every model is deprecated, returns `{}`.
            - Use a **dict comprehension** (a check looks for one).

            **Examples**
            ```python
            context_table([
                {"name": "gpt-4o", "context": 128000, "deprecated": False},
                {"name": "gpt-3", "context": 2048, "deprecated": True},
                {"name": "claude", "context": 200000, "deprecated": False},
            ])
            # returns {"gpt-4o": 128000, "claude": 200000}

            context_table([])   # returns {}
            ```
        ''',
        "starter": r'''
            def context_table(models):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import context_table

            MODELS = [
                {"name": "gpt-4o", "context": 128000, "deprecated": False},
                {"name": "gpt-3", "context": 2048, "deprecated": True},
                {"name": "claude", "context": 200000, "deprecated": False},
            ]

            def test_deprecated_models_are_left_out():
                got = context_table(MODELS)
                assert got == {"gpt-4o": 128000, "claude": 200000}, f"got {got!r}"

            def test_empty_list_returns_empty_dict():
                assert context_table([]) == {}

            def test_all_deprecated_returns_empty_dict():
                assert context_table([MODELS[1]]) == {}

            def test_uses_dict_comprehension():
                tree = ast.parse(source())
                assert any(isinstance(n, ast.DictComp) for n in ast.walk(tree)), \
                    "use a dict comprehension"
        ''',
        "solution": r'''
            def context_table(models):
                return {m["name"]: m["context"] for m in models if not m["deprecated"]}
        ''',
    },
    {
        "id": "comprehensions-7",
        "title": "Label every result",
        "difficulty": 1,
        "lesson": r'''
            ## Choose a label without dropping an item

            A dashboard needs a status beside every result, including unsuccessful ones. Filtering out failures would make the dashboard shorter than the original result list. Instead, choose one of two labels for each item.

            ```python
            attempts = [1, 4, 2]
            labels = ["repeat" if count > 2 else "initial" for count in attempts]
            print(labels)
            # ['initial', 'repeat', 'initial']
            ```

            The choice appears at the front, where a comprehension normally calculates its output value. The form `a if condition else b` picks one value when the condition is true and the other when it is false. This is a **conditional expression**. It still produces one output per input.

            ```predict
            sizes = [2, 5, 8]
            print(["large" if size >= 5 else "small" for size in sizes])
            ---
            Every size gets a label. The comparison includes equality, so both five and eight receive large.
            ```

            Compare this with a final `if` after the `for` part. That final condition is a filter, so failed items disappear. A conditional expression has an `else` because it must supply an answer even when the condition fails. These two uses of `if` answer different questions.

            ```match
            condition at the end :: whether an item contributes a result
            choice at the front :: which result an item contributes
            `else` in a conditional expression :: the value for a false condition
            ```

            Boundary values need deliberate attention. A condition using greater-than excludes equality, while greater-than-or-equal includes it. Pick the comparison that matches the promised labels rather than whichever example you last saw.

            **Watch out:** moving the condition to the end changes a labeling task into filtering. The code can run successfully while returning too few items.

            Put the choice in the output expression when every input needs an answer.
        ''',
        "prompt": r'''
            A retriever returns similarity scores. Label each one so a dashboard can colour it,
            keeping **every** score (this uses a *conditional expression*, `a if cond else b`).

            **Your job:** write `label_scores(scores, threshold=0.5)`

            **What goes in**
            - `scores`: a list of floats, e.g. `[0.9, 0.2, 0.5]`
            - `threshold`: a float, default `0.5`

            **What comes out**
            - a list of strings, one per score in the same order: `"relevant"` if
              the score is **greater than or equal to** `threshold`, otherwise `"ignore"`

            **Rules**
            - The result always has the same length as `scores`.
            - A score exactly equal to `threshold` is `"relevant"`.
            - An empty list returns `[]`.
            - Use a **list comprehension** (a check looks for one) - no `for` loop statement.

            **Examples**
            ```python
            label_scores([0.9, 0.2, 0.5])        # returns ["relevant", "ignore", "relevant"]
            label_scores([0.6, 0.7], 0.65)       # returns ["ignore", "relevant"]
            label_scores([])                     # returns []
            ```
        ''',
        "starter": r'''
            def label_scores(scores, threshold=0.5):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import label_scores

            def test_labels_every_score_with_default_threshold():
                got = label_scores([0.9, 0.2, 0.5])
                assert got == ["relevant", "ignore", "relevant"], f"got {got!r}"

            def test_custom_threshold():
                got = label_scores([0.6, 0.7], 0.65)
                assert got == ["ignore", "relevant"], f"got {got!r}"

            def test_no_score_is_dropped():
                got = label_scores([0.1, 0.1, 0.1])
                assert got == ["ignore", "ignore", "ignore"], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert label_scores([]) == []

            def test_uses_list_comprehension_and_no_for_statement():
                tree = ast.parse(source())
                assert any(isinstance(n, ast.ListComp) for n in ast.walk(tree)), \
                    "use a list comprehension"
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), \
                    "no for-loop statements"
        ''',
        "solution": r'''
            def label_scores(scores, threshold=0.5):
                return ["relevant" if s >= threshold else "ignore" for s in scores]
        ''',
        "hints": [
            "Every input needs an output, so a final filter is the wrong shape.",
            "Make the expression choose between two labels while keeping every score.",
            "Use a conditional expression at the front of the list comprehension, including equality in the relevant case.",
        ],
    },
    {
        "id": "comprehensions-8",
        "title": "Any chunk too long?",
        "difficulty": 1,
        "lesson": r'''
            ## Ask one question about a whole collection

            A batch can contain many documents, but you may only need one yes-or-no answer: does anything exceed the size limit, or does everything satisfy a rule? Building a full list of labels would do more work than that answer needs.

            ```python
            sizes = [4, 12, 7]
            print(any(size > 10 for size in sizes))
            # True
            print(all(size > 10 for size in sizes))
            # False
            ```

            The expression supplies one condition result at a time. `any` succeeds when at least one is true; `all` succeeds when none is false. Both stop once later items cannot change the answer. Supplying those values without building a list uses the **generator expression** form introduced earlier in this chapter.

            ```predict
            print(any(number < 0 for number in []))
            print(all(number < 0 for number in []))
            ---
            With no items there is no successful example for any, so it is False. There is no counterexample for all, so it is True.
            ```

            Empty collections are not errors for these functions. Think of `all` as asking whether any item breaks the rule: an empty collection has no such item. Think of `any` as asking for at least one witness: an empty collection cannot supply one.

            ```quiz
            Does `any([2, 3])` check whether a number exceeds ten?
            - [x] No; it only tests whether those values count as true. :: Nonzero numbers are true, so you must supply the actual comparison.
            - [ ] Yes; any guesses the intended limit. :: The rule must be written explicitly in the expression.
            ```

            **Watch out:** a whitespace-only string counts as true until you trim it. Write the condition for meaningful text, not merely for a nonempty original string.

            Use any for at least one success and all for no failures.
        ''',
        "prompt": r'''
            Before embedding, check a batch of text chunks against the model's size limit.

            **Your job:** write `any_too_long(chunks, limit)` and `all_non_empty(chunks)`

            **What goes in**
            - `chunks`: a list of strings, e.g. `["short", "a much longer chunk"]`
            - `limit`: an int, the maximum allowed length in characters, e.g. `10`

            **What comes out**
            -
              - `any_too_long`: `True` if at least one chunk has **more than** `limit`
                characters, else `False`
              - `all_non_empty`: `True` if every chunk contains at least one non-whitespace
                character, else `False`

            **Rules**
            - A chunk of exactly `limit` characters is not too long.
            - `any_too_long([], 10)` returns `False`; `all_non_empty([])` returns `True`.
            - A chunk of only spaces (like `"  "`) counts as empty.
            - Both must return the real booleans `True`/`False`.
            - Use `any()` / `all()` with a generator expression; no `for` loop statements.

            **Examples**
            ```python
            any_too_long(["short", "a much longer chunk"], 10)   # returns True
            any_too_long(["exactly10!"], 10)                     # returns False
            all_non_empty(["a", "b c"])                          # returns True
            all_non_empty(["a", "  "])                           # returns False
            ```
        ''',
        "research": {
            "note": "Read the docs for the built-ins any() and all(), including what they return for an empty iterable, then come back.",
            "links": [
                {"title": "any() - Python built-in functions",
                 "url": "https://docs.python.org/3/library/functions.html#any"},
                {"title": "all() - Python built-in functions",
                 "url": "https://docs.python.org/3/library/functions.html#all"},
            ],
        },
        "starter": r'''
            def any_too_long(chunks, limit):
                ...


            def all_non_empty(chunks):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import any_too_long, all_non_empty

            def test_one_long_chunk_is_enough():
                got = any_too_long(["short", "a much longer chunk"], 10)
                assert got is True, f"got {got!r}"

            def test_chunk_of_exactly_limit_is_not_too_long():
                got = any_too_long(["exactly10!", "tiny"], 10)
                assert got is False, f"got {got!r}"

            def test_empty_batches():
                assert any_too_long([], 10) is False, "no chunks means none is too long"
                assert all_non_empty([]) is True, "no chunks means none is empty"

            def test_all_non_empty_true_and_false():
                assert all_non_empty(["a", "b c"]) is True
                assert all_non_empty(["a", "  "]) is False, "a whitespace-only chunk counts as empty"
                assert all_non_empty(["", "a"]) is False

            def test_no_for_statement():
                tree = ast.parse(source())
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), \
                    "use any()/all() with a generator expression, not a for statement"
        ''',
        "solution": r'''
            def any_too_long(chunks, limit):
                return any(len(c) > limit for c in chunks)


            def all_non_empty(chunks):
                return all(c.strip() != "" for c in chunks)
        ''',
        "hints": [
            "Ask whether one example is enough or whether every example must pass.",
            "One helper checks lengths against the limit; the other checks for meaningful text after trimming.",
            "Feed each built-in the corresponding per-chunk condition through a generator expression, keeping the specified empty-batch behavior.",
        ],
    },
    {
        "id": "comprehensions-3",
        "title": "Flatten chunked documents",
        "hints": [
            "Read the two for clauses in the order you would nest ordinary loops.",
            "Visit one document, then enumerate its chunks before moving to the next document.",
            "Build each output tuple from the current document and its current indexed chunk; put both for clauses in one comprehension.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A retriever returns documents, each with its own list of chunks. You want one
            flat list of every chunk, tagged with where it came from (this is called
            *flattening*).

            **Your job:** write `flatten_chunks(docs)`

            **What goes in**
            - `docs`: a list of dicts, each like `{"id": "a", "chunks": ["intro", "body"]}`
              (`"id"` is a string, `"chunks"` is a list of strings, possibly empty)

            **What comes out**
            - a list of tuples `(doc_id, index, chunk)`, where `index` is the
              chunk's position inside **its own** document (starting at `0`)

            **Rules**
            - Keep the order: documents in the order given, chunks in their order.
            - `index` restarts at `0` for each document.
            - A document with no chunks adds nothing.
            - An empty `docs` list returns `[]`.
            - Use **one list comprehension with two `for` clauses** (a *nested
              comprehension*). A check fails if your file has a `for` loop statement.

            **Examples**
            ```python
            docs = [
                {"id": "a", "chunks": ["intro", "body"]},
                {"id": "b", "chunks": []},
                {"id": "c", "chunks": ["only"]},
            ]
            flatten_chunks(docs)
            # returns [("a", 0, "intro"), ("a", 1, "body"), ("c", 0, "only")]

            flatten_chunks([{"id": "x", "chunks": ["p", "q"]},
                            {"id": "y", "chunks": ["r", "s"]}])
            # returns [("x", 0, "p"), ("x", 1, "q"), ("y", 0, "r"), ("y", 1, "s")]

            flatten_chunks([])   # returns []
            ```
        ''',
        "starter": r'''
            def flatten_chunks(docs):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import flatten_chunks

            DOCS = [
                {"id": "a", "chunks": ["intro", "body"]},
                {"id": "b", "chunks": []},
                {"id": "c", "chunks": ["only"]},
            ]

            def test_flattens_chunks_in_order_and_skips_empty_docs():
                got = flatten_chunks(DOCS)
                expected = [("a", 0, "intro"), ("a", 1, "body"), ("c", 0, "only")]
                assert got == expected, f"got {got!r}"

            def test_index_restarts_at_zero_for_each_document():
                got = flatten_chunks([{"id": "x", "chunks": ["p", "q"]},
                                      {"id": "y", "chunks": ["r", "s"]}])
                assert [t[1] for t in got] == [0, 1, 0, 1], f"got {got!r}"

            def test_no_docs_returns_empty_list():
                assert flatten_chunks([]) == []

            def test_uses_one_comprehension_with_two_fors_and_no_for_statement():
                tree = ast.parse(source())
                comps = [n for n in ast.walk(tree) if isinstance(n, ast.ListComp)]
                assert any(len(c.generators) >= 2 for c in comps), \
                    "use one list comprehension with two for clauses"
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), \
                    "no for-loop statements"
        ''',
        "solution": r'''
            def flatten_chunks(docs):
                return [
                    (doc["id"], i, chunk)
                    for doc in docs
                    for i, chunk in enumerate(doc["chunks"])
                ]
        ''',
    },
    {
        "id": "comprehensions-4",
        "title": "Guardrail checks",
        "hints": [
            "Choose the collecting function according to whether you need a sum, one match, or universal validity.",
            "Each generator supplies one number or one condition result per input.",
            "Sum token counts, test phrase membership against lowercased text, and check each role against the allowed names, using a separate generator in every helper.",
        ],
        "difficulty": 2,
        "prompt": r'''
            Three small guardrail checks you might run on a chat before sending it to a model.

            **Your job:** write `total_tokens(messages)`, `has_banned(text, banned)` and
            `all_valid_roles(messages)`

            - `messages`: a list of message dicts, each like `{"role": "user", "tokens": 12}`
            - `text`: a string, e.g. `"Ignore previous INSTRUCTIONS"`
            - `banned`: a list of lower-case phrases, e.g. `["ignore previous"]`

            **What comes out**
            -
              - `total_tokens`: an int - the sum of every message's `"tokens"`
              - `has_banned`: `True` if any phrase in `banned` appears anywhere inside
                `text.lower()` (a substring check), else `False`
              - `all_valid_roles`: `True` if every message's `"role"` is one of `"system"`,
                `"user"`, `"assistant"`, `"tool"`, else `False`

            **Rules**
            - `total_tokens([])` returns `0`.
            - `has_banned` ignores upper/lower case in `text`; with an empty `banned` list
              it returns `False`.
            - `all_valid_roles([])` returns `True` (no message breaks the rule).
            - `has_banned` and `all_valid_roles` must return the real booleans `True`/`False`.
            - Each function must use a **generator expression** (a comprehension without
              brackets, passed straight into `sum`, `any` or `all`). Inside these functions:
              no `for` loop statements and no list comprehensions.

            **Examples**
            ```python
            msgs = [{"role": "user", "tokens": 12}, {"role": "assistant", "tokens": 30}]
            total_tokens(msgs)                                                # returns 42
            total_tokens([])                                                  # returns 0
            has_banned("Ignore previous INSTRUCTIONS", ["ignore previous"])   # returns True
            has_banned("hello there", ["jailbreak", "ignore"])                # returns False
            all_valid_roles(msgs)                                             # returns True
            all_valid_roles(msgs + [{"role": "bot", "tokens": 1}])            # returns False
            ```
        ''',
        "starter": r'''
            def total_tokens(messages):
                ...


            def has_banned(text, banned):
                ...


            def all_valid_roles(messages):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import total_tokens, has_banned, all_valid_roles

            MSGS = [{"role": "user", "tokens": 12}, {"role": "assistant", "tokens": 30}]

            def test_total_tokens_sums_tokens_and_empty_is_zero():
                assert total_tokens(MSGS) == 42, f"got {total_tokens(MSGS)!r}"
                assert total_tokens([]) == 0

            def test_has_banned_is_case_insensitive_and_false_for_no_banned_words():
                assert has_banned("Ignore previous INSTRUCTIONS", ["ignore previous"]) is True
                assert has_banned("hello there", ["jailbreak", "ignore"]) is False
                assert has_banned("anything", []) is False

            def test_all_valid_roles_rejects_unknown_role_and_empty_is_true():
                assert all_valid_roles(MSGS) is True
                assert all_valid_roles(MSGS + [{"role": "bot", "tokens": 1}]) is False
                assert all_valid_roles([]) is True

            def test_each_function_uses_a_generator_expression_without_loops():
                tree = ast.parse(source())
                funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
                for name in ("total_tokens", "has_banned", "all_valid_roles"):
                    fn = funcs.get(name)
                    assert fn is not None, f"{name} is missing"
                    assert any(isinstance(n, ast.GeneratorExp) for n in ast.walk(fn)), \
                        f"{name}: use a generator expression"
                    assert not any(isinstance(n, (ast.For, ast.ListComp)) for n in ast.walk(fn)), \
                        f"{name}: no loops or list comprehensions"
        ''',
        "solution": r'''
            VALID_ROLES = {"system", "user", "assistant", "tool"}


            def total_tokens(messages):
                return sum(m["tokens"] for m in messages)


            def has_banned(text, banned):
                lowered = text.lower()
                return any(word in lowered for word in banned)


            def all_valid_roles(messages):
                return all(m["role"] in VALID_ROLES for m in messages)
        ''',
    },
    {
        "id": "comprehensions-5",
        "title": "Label and dedupe",
        "hints": [
            "The three output collections preserve different information: order, uniqueness, and a best value.",
            "Label every pair, collect qualifying identifiers, and calculate the maximum over all scores for each identifier.",
            "Build the required three comprehension kinds separately, ensure equality qualifies as a hit, and assemble them under the specified dictionary keys.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Summarise retriever results: label each hit or miss, list the documents that
            were hits, and find each document's best score.

            **Your job:** write `summarise_scores(results, threshold)`

            **What goes in**
            - `results`: a list of `(doc_id, score)` tuples, e.g. `[("a", 0.9), ("b", 0.2)]`
              (`doc_id` is a string, `score` a float; the same doc may appear more than once)
            - `threshold`: a float, e.g. `0.5`

            **What comes out**
            - a dict with exactly three keys:
              - `"labels"`: a list of strings, one per pair in input order:
                `"<doc_id>:hit"` if `score >= threshold`, else `"<doc_id>:miss"`
              - `"unique_hits"`: a **set** of the doc ids with at least one score `>= threshold`
              - `"best"`: a dict mapping each doc id to its **highest** score (not its last one)

            **Rules**
            - A score exactly equal to `threshold` counts as a hit.
            - With empty `results`, return `{"labels": [], "unique_hits": set(), "best": {}}`.
            - Build `"labels"` with a list comprehension containing a *conditional
              expression* (`x if condition else y`), `"unique_hits"` with a *set
              comprehension*, and `"best"` with a *dict comprehension* (checks look for all three).

            **Examples**
            ```python
            summarise_scores([("a", 0.9), ("b", 0.2), ("a", 0.4), ("c", 0.5)], 0.5)
            # returns {"labels": ["a:hit", "b:miss", "a:miss", "c:hit"],
            #          "unique_hits": {"a", "c"},
            #          "best": {"a": 0.9, "b": 0.2, "c": 0.5}}

            summarise_scores([("x", 0.1), ("x", 0.7)], 0.5)["best"]   # returns {"x": 0.7}

            summarise_scores([], 0.5)
            # returns {"labels": [], "unique_hits": set(), "best": {}}
            ```
        ''',
        "starter": r'''
            def summarise_scores(results, threshold):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import summarise_scores

            RESULTS = [("a", 0.9), ("b", 0.2), ("a", 0.4), ("c", 0.5)]

            def test_labels_mark_each_pair_hit_or_miss_in_order():
                got = summarise_scores(RESULTS, 0.5)["labels"]
                assert got == ["a:hit", "b:miss", "a:miss", "c:hit"], f"got {got!r}"

            def test_unique_hits_is_a_set_of_hit_doc_ids():
                got = summarise_scores(RESULTS, 0.5)["unique_hits"]
                assert isinstance(got, set), f"expected a set, got {type(got).__name__}"
                assert got == {"a", "c"}, f"got {got!r}"

            def test_best_keeps_highest_not_last():
                got = summarise_scores(RESULTS, 0.5)["best"]
                assert got == {"a": 0.9, "b": 0.2, "c": 0.5}, f"got {got!r}"

            def test_best_when_later_score_is_higher():
                got = summarise_scores([("x", 0.1), ("x", 0.7)], 0.5)["best"]
                assert got == {"x": 0.7}, f"got {got!r}"

            def test_empty_results_give_empty_collections():
                got = summarise_scores([], 0.5)
                assert got == {"labels": [], "unique_hits": set(), "best": {}}, f"got {got!r}"

            def test_uses_list_comp_with_conditional_set_comp_and_dict_comp():
                tree = ast.parse(source())
                nodes = list(ast.walk(tree))
                assert any(isinstance(n, ast.ListComp) and
                           any(isinstance(x, ast.IfExp) for x in ast.walk(n)) for n in nodes), \
                    "labels: list comprehension with a conditional expression"
                assert any(isinstance(n, ast.SetComp) for n in nodes), "use a set comprehension"
                assert any(isinstance(n, ast.DictComp) for n in nodes), "use a dict comprehension"
        ''',
        "solution": r'''
            def summarise_scores(results, threshold):
                labels = [f"{doc}:{'hit' if score >= threshold else 'miss'}"
                          for doc, score in results]
                unique_hits = {doc for doc, score in results if score >= threshold}
                best = {
                    doc: max(s for d, s in results if d == doc)
                    for doc, _ in results
                }
                return {"labels": labels, "unique_hits": unique_hits, "best": best}
        ''',
    },
    {
        "id": "comprehensions-6",
        "title": "Transpose embeddings",
        "hints": [
            "A column contains the same position from every input row.",
            "Build columns first; their averages become the entries of the mean vector.",
            "Handle empty inputs according to each function's contract, construct columns with nested comprehensions, then divide each column total by the number of vectors.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Embeddings are stored as a list of equal-length vectors (lists of numbers).
                      Averaging them gives a single "centre" vector for a group of documents.

                      **Your job:** write `transpose(matrix)` and `mean_vector(vectors)`

                      - `matrix` / `vectors`: a list of equal-length lists of numbers,
                        e.g. `[[1, 2, 3], [4, 5, 6]]`

            **What comes out**
            -
                        - `transpose`: a list of lists where row `i` holds item `i` of every input row
                          (rows become columns - this is called *transposing*)
                        - `mean_vector`: a list of floats - the *element-wise mean*: position `i` is the
                          average of item `i` across all the vectors

                      **Rules**
                      - `transpose` must return **lists**, not tuples, for each row.
                      - `transpose([])` returns `[]`.
                      - `mean_vector([])` raises `ValueError` (any message).
                      - Use comprehensions only: a check fails if your file has a `for` loop statement
                        or mentions `numpy` (a library for
            number arrays that you do not need here).

                      **Examples**
                      ```python
                      transpose([[1, 2, 3], [4, 5, 6]])   # returns [[1, 4], [2, 5], [3, 6]]
                      transpose([])                       # returns []
                      mean_vector([[1, 2], [3, 6]])       # returns [2.0, 4.0]
                      mean_vector([[0.5, 1.0, -1.0]])     # returns [0.5, 1.0, -1.0]
                      mean_vector([])                     # raises ValueError
                      ```
        ''',
        "starter": r'''
            def transpose(matrix):
                ...


            def mean_vector(vectors):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import transpose, mean_vector

            def test_transpose_turns_rows_into_columns():
                got = transpose([[1, 2, 3], [4, 5, 6]])
                assert got == [[1, 4], [2, 5], [3, 6]], f"got {got!r}"

            def test_transpose_returns_lists_not_tuples():
                got = transpose([[1, 2], [3, 4]])
                assert all(isinstance(row, list) for row in got), f"rows should be lists: {got!r}"

            def test_transpose_of_empty_matrix_is_empty_list():
                assert transpose([]) == []

            def test_mean_vector_averages_each_position():
                got = mean_vector([[1, 2], [3, 6]])
                assert got == [2.0, 4.0], f"got {got!r}"
                got = mean_vector([[0.5, 1.0, -1.0]])
                assert got == [0.5, 1.0, -1.0], f"got {got!r}"

            def test_mean_vector_of_no_vectors_raises_value_error():
                try:
                    mean_vector([])
                except ValueError:
                    return
                assert False, "expected ValueError for no vectors"

            def test_uses_comprehensions_no_for_statement_no_numpy():
                tree = ast.parse(source())
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), \
                    "use comprehensions, not for statements"
                assert "numpy" not in source(), "no numpy"
        ''',
        "solution": r'''
            def transpose(matrix):
                if not matrix:
                    return []
                return [[row[i] for row in matrix] for i in range(len(matrix[0]))]


            def mean_vector(vectors):
                if not vectors:
                    raise ValueError("need at least one vector")
                return [sum(column) / len(vectors) for column in transpose(vectors)]
        ''',
    },
]
