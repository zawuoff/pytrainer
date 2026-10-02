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

LESSON = r'''
## Chapter notes: Comprehensions

A comprehension builds a new collection from an iterable in one expression -
the "empty list, loop, append" pattern folded into one line.

| shape | builds |
| --- | --- |
| `[expr for x in items]` | list (same length, same order) |
| `[expr for x in items if cond]` | list, *filtered* |
| `{k: v for x in items}` | dict |
| `{expr for x in items}` | set (unique values, no order) |
| `sum(expr for x in items)` | *generator expression*: no list is built |

```python
words = ["token", "", "prompt"]
print([len(w) for w in words if w])
print({w: len(w) for w in words if w})
print(sum(len(w) for w in words))
```

**Terms**
- *expression* (front): what each new item is. *filter* (`if` at the end): which items are kept.
- *conditional expression*: `a if cond else b` - at the front, chooses a value per item, keeps every item.
- *generator expression*: a comprehension without brackets, passed straight into
  `sum`, `min`, `max`, `any`, `all`.
- `any(...)` is `True` if at least one item is true (`any([])` is `False`);
  `all(...)` is `True` if every item is true (`all([])` is `True`).
- Two `for` clauses flatten nested lists, read left to right like nested loops:
  `[c for doc in docs for c in doc]`.

**Gotchas**
- Filter at the end: `[x for x in xs if x > 0]`, not `[x for x in xs] if x > 0`.
- `if` with `else` goes at the front: `[x if x > 0 else 0 for x in xs]`.
- Dict keys must be unique: a repeated key overwrites the earlier value.
- `{}` is an empty dict; an empty set is `set()`.
- A comprehension never changes the original list; it returns a new one.
- If it needs several conditions and nested loops, a normal `for` loop is clearer.
'''

EXERCISES = [
    {
        "id": "comprehensions-s1",
        "title": "Read the comprehension",
        "difficulty": 0,
        "lesson": r'''
            ## A loop folded into one line

            You've written this shape many times: make an empty list, loop, append. It's
            like a factory conveyor belt: items come in one end, each gets worked on, and
            the results land in a new box. Python lets you write the whole belt in one line.

            ```python
            nums = [1, 2, 3]

            doubled = []
            for n in nums:
                doubled.append(n * 2)
            print(doubled)

            print([n * 2 for n in nums])
            ```

            Both print `[2, 4, 6]`. The second form is a *list comprehension*. Read it out
            loud: "`n * 2`, for every `n` in `nums`".

            It can also end with an `if` to skip some items, and with curly braces and a
            colon (`{key: value for ...}`) it builds a dict instead of a list.

            **Watch out:** read the `for` part first to know what the variable is, then look
            at the front to see what gets produced.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            The first comprehension transforms every item. The second keeps only the items
            where the `if` is true (the even numbers). The third is a dict comprehension:
            for each `n` greater than 3 it makes the key `n` with the value `n * n`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Read each comprehension as a small loop: for every n, (maybe) check the if, then produce the expression.",
            "Line 1 changes every number. Line 2 only keeps numbers with remainder 0 when divided by 2. Line 3 builds key: value pairs.",
            "Line 1: multiply each number by 10. Line 2: keep 2 and 4. Line 3: only 4 and 5 pass the filter; write them as a dict mapping each to its square.",
        ],
    },
    {
        "id": "comprehensions-s2",
        "title": "Shout every word",
        "difficulty": 0,
        "lesson": r'''
            ## The front part is the work station

            On the conveyor belt, the front of the comprehension is the work station: what
            happens to each item before it lands in the new box.

            ```python
            names = ["ada", "grace"]
            print([n.title() for n in names])
            print([len(n) for n in names])
            print([n + "!" for n in names])
            ```

            The shape is always `[expression for item in iterable]`:
            - `item` is a new variable that holds each element in turn.
            - `expression` is what goes into the new list; it usually uses `item`.
            - `iterable` is what you loop over (a list, a string, a `range`...).

            The result is a **new** list with the same number of items, in the same order.
            The original list is not changed.

            **Watch out:** the expression must use the loop variable. `[x.upper() for w in words]`
            fails because `x` doesn't exist - the variable is called `w`.
        ''',
        "prompt": r'''
            Upper-case every word in a list (fill in the blank).

            **Write:** `shout_all(words)` - replace the `___` in the starter.

            - `words`: a list of strings, e.g. `["hi", "there"]`
            - **Returns:** a new list with every word in upper case, in the same order

            **Rules**
            - An empty list returns `[]`.

            **Examples**
            ```python
            shout_all(["hi", "there"])   # returns ["HI", "THERE"]
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
            "The blank is the expression: what each item of the new list should be.",
            "Each item is the word w, upper-cased with a string method.",
            "Replace ___ with w.upper().",
        ],
    },
    {
        "id": "comprehensions-s3",
        "title": "Fix: backwards lookup",
        "difficulty": 0,
        "lesson": r'''
            ## Building a phone book in one line

            A dict is like a phone book: name (the key) points to number (the value). A
            *dict comprehension* builds one from a list in a single line, using curly braces
            and a colon.

            ```python
            models = ["gpt", "claude"]
            print({m: m.upper() for m in models})
            print({m: 0 for m in models})
            ```

            The shape is `{key: value for item in iterable}`. Left of the colon is the key,
            right of the colon is the value - exactly like writing a dict by hand.

            **Watch out:** which side is which matters a lot. Keys must be unique: if two
            items produce the same key, the later one overwrites the earlier one and you
            silently lose data. That's why a word makes a better key than its length:
            many words share a length.
        ''',
        "prompt": r'''
            Build a lookup of word lengths. The starter has one bug - find and fix it.

            **Write:** `word_lengths(words)` (fix the starter)

            - `words`: a list of strings, e.g. `["hi", "hello"]`
            - **Returns:** a dict where each **key is a word** and its **value is that word's length**

            **Rules**
            - Words with the same length must all be kept (each word is its own key).

            **Examples**
            ```python
            word_lengths(["hi", "hello"])   # returns {"hi": 2, "hello": 5}
            word_lengths(["cat", "dog"])    # returns {"cat": 3, "dog": 3}
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
            "In a dict comprehension the part before the colon is the key and the part after is the value.",
            "The spec says the word is the key and its length is the value. Check which is which in the code.",
            "Swap the two sides of the colon so it reads w: len(w).",
        ],
    },
    {
        "id": "comprehensions-s4",
        "title": "Keep the short names",
        "difficulty": 0,
        "lesson": r'''
            ## A sieve at the end

            Add a sieve to the end of the belt: only items that pass the test get through.
            In a comprehension the sieve is an `if` at the **end**.

            ```python
            scores = [0.9, 0.2, 0.7, 0.4]
            print([s for s in scores if s >= 0.5])
            print([s * 100 for s in scores if s < 0.5])
            ```

            Shape: `[expression for item in iterable if condition]`. For each item, Python
            checks the condition first; only when it's `True` does the expression go into
            the new list. Items keep their original order.

            This is called *filtering*. The expression can be just the item itself
            (`[s for s in ...]`) when you only want to keep some items unchanged.

            **Watch out:** the filter `if` goes after the `for`, never before it, and it has
            no `else`.
        ''',
        "prompt": r'''
            Keep only the short model names from a list (this is called *filtering*).

            **Write:** `short_names(names)`

            - `names`: a list of strings, e.g. `["gpt-4o", "claude", "llama", "phi"]`
            - **Returns:** a new list with only the names that have **5 characters or fewer**,
              in their original order

            **Rules**
            - A name with exactly 5 characters is kept.
            - Use a list comprehension with an `if` (a check looks for a list comprehension).

            **Examples**
            ```python
            short_names(["gpt-4o", "claude", "llama", "phi"])   # returns ["llama", "phi"]
            short_names(["abcde"])                              # returns ["abcde"]
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
            "A list comprehension with a filter: [item for item in list if condition].",
            "The item itself is kept unchanged; the condition compares its length with 5.",
            "Return [name for name in names if len(name) <= 5].",
        ],
    },
    {
        "id": "comprehensions-s5",
        "title": "Total characters",
        "difficulty": 0,
        "lesson": r'''
            ## Feeding the belt straight into a machine

            Sometimes you don't want the list at all - you only want a total. You can feed
            the conveyor belt straight into a machine like `sum()`, without a box in between.

            ```python
            prices = [0.5, 1.25, 2.0]
            print(sum([p * 2 for p in prices]))
            print(sum(p * 2 for p in prices))
            print(max(len(w) for w in ["hi", "hello"]))
            ```

            The second line has no square brackets. That's a *generator expression*: it
            produces the values one at a time for `sum` to add up, without building a list
            first. Use it whenever you pass a comprehension directly into `sum`, `min`,
            `max`, `any` or `all`.

            `sum` of nothing is `0`, so an empty list just gives `0`.

            **Watch out:** `max` and `min` of an empty sequence crash; `sum` doesn't.
        ''',
        "prompt": r'''
            Count how many characters a set of text chunks contains in total.

            **Write:** `total_chars(chunks)`

            - `chunks`: a list of strings, e.g. `["abc", "de", ""]`
            - **Returns:** an int - the sum of the lengths of all the strings

            **Rules**
            - An empty list returns `0`.
            - Use `sum()` with a comprehension or *generator expression* (a comprehension
              without the square brackets). A check fails if your file has a `for` loop
              statement (a `for` inside a comprehension is fine).

            **Examples**
            ```python
            total_chars(["abc", "de", ""])   # returns 5
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
            "sum() adds up numbers. You need one number per chunk: its length.",
            "Produce the length of each chunk with a comprehension and pass that straight to sum().",
            "Return sum(len(c) for c in chunks).",
        ],
    },
    {
        "id": "comprehensions-s6",
        "title": "Which roles appear?",
        "difficulty": 0,
        "lesson": r'''
            ## A guest list: no duplicates

            A guest list at a party only needs each name once, however many times people
            RSVP. Python's *set* works like that: it keeps unique values only, with no order.
            Curly braces **without** a colon build a set comprehension.

            ```python
            tags = ["ai", "python", "ai", "rag"]
            unique = {t.upper() for t in tags}
            print(len(unique))
            print("AI" in unique)
            print(len(tags))
            ```

            Compare the three brackets:
            - `[x for ...]` - list (keeps duplicates, keeps order)
            - `{x for ...}` - set (unique values, no order)
            - `{k: v for ...}` - dict (key: value pairs)

            Sets are great for "which different values appear?" and for fast `in` checks.

            **Watch out:** `{}` on its own is an empty **dict**, not a set. An empty set is
            written `set()`.
        ''',
        "prompt": r'''
            A chat log has many messages; you want to know which different roles appear in it.

            **Write:** `roles_used(messages)`

            - `messages`: a list of message dicts, each like `{"role": "user", "content": "hi"}`
            - **Returns:** a **set** of the different `"role"` values

            **Rules**
            - Each role appears once in the result, however many messages have it.
            - An empty list returns an empty set, `set()`.
            - Use a **set comprehension** (a check looks for one).

            **Examples**
            ```python
            roles_used([{"role": "user", "content": "hi"},
                        {"role": "assistant", "content": "hello"},
                        {"role": "user", "content": "thanks"}])
            # returns {"user", "assistant"}

            roles_used([])   # returns set()
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
            "A set comprehension uses curly braces without a colon: {expression for item in list}.",
            "Each item is a message dict; the expression is that message's role, looked up with its key.",
            "Return a set comprehension that produces m[\"role\"] for every m in messages.",
        ],
    },
    {
        "id": "comprehensions-1",
        "title": "Token lengths",
        "hints": [
            "A list comprehension with a filter: [expression for item in list if condition].",
            "The expression is the chunk's length. The condition must be false for empty and whitespace-only chunks - strip() the chunk and check whether anything is left.",
            "Return [len(chunk) for chunk in chunks if chunk.strip()]. An empty string is falsy, so chunk.strip() works directly as the condition.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Work station and sieve together

            You can use both parts at once: a filter at the end decides which items get
            through, and the expression at the front says what to produce from each one.

            ```python
            words = ["cat", "", "horse", "  "]
            print([w.upper() for w in words if w])
            print([len(w) for w in words if len(w) > 3])
            ```

            Python runs it in this order for each item: check the `if`; if it passes,
            compute the expression and add it to the list.

            A handy trick: strings are *truthy* when they contain something and *falsy*
            when they are empty. So `if w` keeps non-empty strings. `"  "` is not empty
            (it has spaces) - `strip()` it first if blank text should count as empty.

            **Watch out:** the filter tests the original item, not the result of the
            expression.
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

            **Write:** `chunk_lengths(chunks)`

            - `chunks`: a list of strings, e.g. `["hello", "  ", "hi there", ""]`
            - **Returns:** a list of ints - the length (in characters) of each kept chunk,
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
            "A dict comprehension looks like {key: value for item in list if condition}.",
            "For each model dict, the key is its \"name\" and the value is its \"context\". Keep only the ones whose \"deprecated\" is False.",
            "Return {m[\"name\"]: m[\"context\"] for m in models if not m[\"deprecated\"]}.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## A lookup table from records

            API responses often give you a list of records (dicts). To answer "what is X
            for this name?" quickly, turn the list into a lookup table with a dict
            comprehension - and filter out the records you don't want.

            ```python
            users = [{"name": "ada", "age": 36, "active": True},
                     {"name": "bob", "age": 20, "active": False}]
            ages = {u["name"]: u["age"] for u in users if u["active"]}
            print(ages)
            print(ages["ada"])
            ```

            Shape: `{key: value for item in iterable if condition}`. Here each item is a
            dict, so the key and value are pulled out with square-bracket lookups.

            `not` flips a boolean: `if not u["active"]` keeps only the inactive ones.

            **Watch out:** the filter works the same as in a list comprehension: at the
            end, after the `for`.
        ''',
        "prompt": r'''
            Turn a list of model records into a quick lookup table of context windows.

            **Write:** `context_table(models)`

            - `models`: a list of dicts, each like
              `{"name": "gpt-4o", "context": 128000, "deprecated": False}`
            - **Returns:** a dict mapping each **non-deprecated** model's `"name"` to its
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
            ## Choosing a label for every item

            A filter throws items away. Sometimes you want to keep **every** item but give
            each one a different value depending on a test - like a teacher writing "pass"
            or "fail" next to every name, without removing anyone.

            ```python
            scores = [0.9, 0.2, 0.6]
            print(["pass" if s >= 0.5 else "fail" for s in scores])
            print("big" if 10 > 3 else "small")
            ```

            `a if condition else b` is a *conditional expression* (some call it the
            *ternary*). It is one value: `a` when the condition is true, `b` otherwise. It
            works anywhere, not just in comprehensions.

            Inside a comprehension it goes at the **front**, as the expression:
            `[a if cond else b for x in items]` - the list keeps its length.

            **Watch out:** the `if` at the end filters and has no `else`; the `if ... else`
            at the front chooses and always needs the `else`.
        ''',
        "prompt": r'''
            A retriever returns similarity scores. Label each one so a dashboard can colour it,
            keeping **every** score (this uses a *conditional expression*, `a if cond else b`).

            **Write:** `label_scores(scores, threshold=0.5)`

            - `scores`: a list of floats, e.g. `[0.9, 0.2, 0.5]`
            - `threshold`: a float, default `0.5`
            - **Returns:** a list of strings, one per score in the same order: `"relevant"` if
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
            "Every score stays, so there is no filter at the end. The choice happens in the expression at the front.",
            "The expression is a conditional expression: one string if the score is at least the threshold, the other string otherwise.",
            "Return a list comprehension whose expression is \"relevant\" if s >= threshold else \"ignore\", for s in scores.",
        ],
    },
    {
        "id": "comprehensions-8",
        "title": "Any chunk too long?",
        "difficulty": 1,
        "lesson": r'''
            ## Asking a yes/no question about a whole list

            "Is **any** chunk too long?" "Are **all** replies non-empty?" Python has two
            built-ins for these questions. `any` is the friend who says yes as soon as one
            item matches. `all` is the strict inspector who only says yes if every item passes.

            ```python
            lengths = [120, 800, 40]
            print(any(n > 500 for n in lengths))
            print(all(n > 500 for n in lengths))
            print(any(n > 5 for n in []), all(n > 5 for n in []))
            ```

            Feed them a generator expression of `True`/`False` values. They stop early as
            soon as the answer is known, and they return real booleans.

            Empty input: `any([])` is `False` (nothing matched), `all([])` is `True`
            (nothing failed).

            **Watch out:** `any(lengths)` without a condition only checks whether the items
            are truthy (non-zero), which is almost never what you mean.
        ''',
        "prompt": r'''
            Before embedding, check a batch of text chunks against the model's size limit.

            **Write:** `any_too_long(chunks, limit)` and `all_non_empty(chunks)`

            - `chunks`: a list of strings, e.g. `["short", "a much longer chunk"]`
            - `limit`: an int, the maximum allowed length in characters, e.g. `10`
            - **Returns:**
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
            "any() answers 'is at least one true?', all() answers 'is every one true?'. Feed each a generator expression of True/False values.",
            "any_too_long: one comparison per chunk, its length against the limit. all_non_empty: one check per chunk, whether anything is left after removing whitespace.",
            "Return any(len(c) > limit for c in chunks). For the other, return all(...) over a comparison that is True when c.strip() is not the empty string.",
        ],
    },
    {
        "id": "comprehensions-3",
        "title": "Flatten chunked documents",
        "hints": [
            "A comprehension can have two for clauses, read left to right like nested loops. enumerate() gives (index, item) pairs.",
            "The outer for goes over the docs; the inner for goes over enumerate(doc[\"chunks\"]). The expression builds the tuple.",
            "Return [(doc[\"id\"], i, chunk) for doc in docs for i, chunk in enumerate(doc[\"chunks\"])]. A doc with no chunks simply produces nothing.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A retriever returns documents, each with its own list of chunks. You want one
            flat list of every chunk, tagged with where it came from (this is called
            *flattening*).

            **Write:** `flatten_chunks(docs)`

            - `docs`: a list of dicts, each like `{"id": "a", "chunks": ["intro", "body"]}`
              (`"id"` is a string, `"chunks"` is a list of strings, possibly empty)
            - **Returns:** a list of tuples `(doc_id, index, chunk)`, where `index` is the
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
            "A generator expression is a comprehension without square brackets, passed straight into sum(), any() or all().",
            "sum adds numbers from each message; any is True if at least one check passes; all is True if every check passes (and for an empty list).",
            "total_tokens: sum(m[\"tokens\"] for m in messages). has_banned: lower-case the text once, then any(word in lowered for word in banned). all_valid_roles: keep a set of valid roles and use all(m[\"role\"] in that_set for m in messages).",
        ],
        "difficulty": 2,
        "prompt": r'''
            Three small guardrail checks you might run on a chat before sending it to a model.

            **Write:** `total_tokens(messages)`, `has_banned(text, banned)` and
            `all_valid_roles(messages)`

            - `messages`: a list of message dicts, each like `{"role": "user", "tokens": 12}`
            - `text`: a string, e.g. `"Ignore previous INSTRUCTIONS"`
            - `banned`: a list of lower-case phrases, e.g. `["ignore previous"]`
            - **Returns:**
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
            "Three different comprehensions: a list comp with `a if cond else b`, a set comp with {...} and no colon, and a dict comp.",
            "For labels, put the conditional expression inside an f-string or next to the doc id. For best, for every doc id compute the max of all scores belonging to that id.",
            "labels: [f\"{doc}:\" + (\"hit\" if score >= threshold else \"miss\") for doc, score in results]. unique_hits: {doc for doc, score in results if score >= threshold}. best: {doc: max(s for d, s in results if d == doc) for doc, _ in results}. Return the three in a dict.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Summarise retriever results: label each hit or miss, list the documents that
            were hits, and find each document's best score.

            **Write:** `summarise_scores(results, threshold)`

            - `results`: a list of `(doc_id, score)` tuples, e.g. `[("a", 0.9), ("b", 0.2)]`
              (`doc_id` is a string, `score` a float; the same doc may appear more than once)
            - `threshold`: a float, e.g. `0.5`
            - **Returns:** a dict with exactly three keys:
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
            "Nested list comprehensions: the outer one goes over column positions, the inner one over rows.",
            "Column i of the result is [row[i] for row in matrix]. There are len(matrix[0]) columns. The mean vector is the average of each column of the transposed matrix.",
            "transpose: return [] for an empty matrix, else [[row[i] for row in matrix] for i in range(len(matrix[0]))]. mean_vector: raise ValueError if empty, else [sum(col) / len(vectors) for col in transpose(vectors)].",
        ],
        "difficulty": 3,
        "prompt": r'''
            Embeddings are stored as a list of equal-length vectors (lists of numbers).
            Averaging them gives a single "centre" vector for a group of documents.

            **Write:** `transpose(matrix)` and `mean_vector(vectors)`

            - `matrix` / `vectors`: a list of equal-length lists of numbers,
              e.g. `[[1, 2, 3], [4, 5, 6]]`
            - **Returns:**
              - `transpose`: a list of lists where row `i` holds item `i` of every input row
                (rows become columns - this is called *transposing*)
              - `mean_vector`: a list of floats - the *element-wise mean*: position `i` is the
                average of item `i` across all the vectors

            **Rules**
            - `transpose` must return **lists**, not tuples, for each row.
            - `transpose([])` returns `[]`.
            - `mean_vector([])` raises `ValueError` (any message).
            - Use comprehensions only: a check fails if your file has a `for` loop statement
              or mentions `numpy`.

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
