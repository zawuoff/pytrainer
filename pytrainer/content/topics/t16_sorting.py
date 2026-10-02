TOPIC = {
    "id": "sorting",
    "title": "Sorting, Lambdas & Key Functions",
    "track": "working-python",
    "order": 7,
    "requires": ["functions", "lists"],
    "summary": """
        Ordering data the Pythonic way: sorted vs list.sort, key functions and lambdas,
        multi-key and mixed-direction sorts, min/max with key, map/filter and itemgetter.
    """,
    "concepts": ["sorted", "list.sort", "key functions", "lambda", "reverse", "tuple keys",
                 "stable sort", "min/max with key", "map", "filter", "operator.itemgetter",
                 "top-k"],
}

LESSON = r'''
## Chapter notes: sorting, keys and lambdas

| tool | what it does | returns |
| --- | --- | --- |
| `sorted(items)` | builds a **new** sorted list, original untouched | the new list |
| `items.sort()` | sorts the list **in place** | `None` |
| `reverse=True` | biggest / Z first (works on both) | - |
| `key=func` | sort by `func(item)` instead of the item | - |
| `min/max(items, key=..., default=...)` | the whole smallest/largest item | one item |
| `map(f, items)` / `filter(f, items)` | apply `f` to each / keep items where `f` is true | lazy - wrap in `list()` |
| `operator.itemgetter(1, 0)` | ready-made key picking positions/keys | a tuple of them |

```python
results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9}, {"id": "b", "score": 0.7}]
best = sorted(results, key=lambda r: (-r["score"], r["id"]))
print([r["id"] for r in best])
print(max(results, key=lambda r: r["score"])["id"])
print(max([], default=None))
```

**Key ideas**
- A *key function* takes one item and returns what to compare. Pass it **without** brackets:
  `key=len`, not `key=len()`.
- A *lambda* is a one-line, nameless function: `lambda r: r["score"]`.
- *Tuple keys* compare the first part, then the next on a tie: `(provider, price)`.
- A minus flips one numeric part: `(-score, name)` = score high to low, name A-Z.
- Python's sort is *stable*: items with equal keys keep their original order. So you can sort
  twice - least important rule first - to mix directions on strings.

**Gotchas**
- `items = items.sort()` turns `items` into `None`.
- `reverse=True` flips **every** part of a tuple key.
- `max([])` raises `ValueError` - use `default=`.
- `print(map(...))` shows `<map object ...>` - use `list(map(...))`.
'''


EXERCISES = [
    {
        "id": "sorting-s1",
        "lesson": r'''
            ## `sorted()` makes a sorted copy

            Picture a pile of exam papers on your desk. `sorted()` photocopies the pile and puts the
            **copies** in order. The original pile doesn't move at all.

            ```python
            prices = [5.0, 0.5, 2.0]
            cheap_first = sorted(prices)
            print(cheap_first)
            print(prices)
            print(sorted(["b", "c", "a"], reverse=True))
            ```

            Numbers go smallest to largest, strings go A to Z. Add `reverse=True` and the order flips:
            biggest (or Z) first.

            The real words: `sorted` is a *built-in function* that **returns a new list**. `reverse=True`
            is a *keyword argument* - an option you pass by name.

            Watch out: `sorted()` never changes the list you give it. If you print the original, you see
            it exactly as it was.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            nums = [3, 1, 2]
            print(sorted(nums))
            print(nums)
            print(sorted(nums, reverse=True))
        ''',
        "solution": r'''
            [1, 2, 3]
            [3, 1, 2]
            [3, 2, 1]
        ''',
        "explanation": r'''
            `sorted(nums)` builds a **new** sorted list and leaves `nums` alone - that is why
            the second line still shows `[3, 1, 2]`. `reverse=True` flips the order so the
            biggest number comes first.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "`sorted()` never changes the list you give it - it builds a new one.",
            "Line 1 is the numbers smallest to largest, line 2 is the untouched original, line 3 is largest to smallest.",
            "Write three lines, each a list in Python's print format with square brackets and commas, e.g. `[1, 2, 3]`.",
        ],
    },
    {
        "id": "sorting-s2",
        "lesson": r'''
            ## Sorting by something else: `key=`

            Imagine lining up a class. By default Python lines people up by name. But you can say
            "line them up by **height**" - you tell it *what to measure* on each person.

            That is what `key=` does. You give `sorted` a function. Python calls it on every item and
            sorts by the answers, not by the items themselves.

            ```python
            temps = [-5, 2, -1, 4]
            print(sorted(temps))            # plain numbers
            print(sorted(temps, key=abs))   # by distance from zero

            names = ["bob", "Alice", "carol"]
            print(sorted(names, key=str.lower))  # ignore upper/lower case
            ```

            `abs(-5)` is `5`, so `-5` ends up last in the second line. The list still holds the original
            items - only the order was decided by the key.

            The real name: a *key function*. It takes **one item** and returns the thing to compare.

            Watch out: pass the function itself, **without brackets**: `key=abs`, not `key=abs()`.
            With brackets you'd be calling it right away, with nothing to measure.
        ''',
        "title": "Sort by length",
        "difficulty": 0,
        "prompt": r'''
            Order words by how long they are - the same idea you'd use to order text chunks by size.

            **Write:** `by_length(words)` - fill in the blank (`___`) in the starter.

            - `words`: a list of strings, e.g. `["ccc", "a", "bb"]`
            - **Returns:** a new list with the same words, shortest first

            **Rules**
            - Replace `___` with a **key function** (the function `sorted` calls on each item).
            - Order by length only, not alphabetically.
            - An empty list returns `[]`.

            Reminder: `sorted(items, key=some_function)` calls the function on each item and
            sorts by the results.

            **Examples**
            ```python
            by_length(["ccc", "a", "bb"])   # returns ["a", "bb", "ccc"]
            by_length(["zz", "b", "aaa"])   # returns ["b", "zz", "aaa"]
            by_length([])                   # returns []
            ```
        ''',
        "starter": r'''
            def by_length(words):
                return sorted(words, key=___)
        ''',
        "tests": r'''
            from solution import by_length

            def test_shortest_word_comes_first():
                got = by_length(["ccc", "a", "bb"])
                assert got == ["a", "bb", "ccc"], f"got {got!r}"

            def test_sorted_by_length_not_alphabetically():
                got = by_length(["zz", "b", "aaa"])
                assert got == ["b", "zz", "aaa"], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert by_length([]) == []
        ''',
        "solution": r'''
            def by_length(words):
                return sorted(words, key=len)
        ''',
        "hints": [
            "Which built-in function tells you how long a string is?",
            "The key is that function's name, passed without brackets - Python will call it on each word for you.",
            "Replace `___` with `len` (not `len()`).",
        ],
    },
    {
        "id": "sorting-s3",
        "lesson": r'''
            ## `.sort()` changes the list itself

            Back to the pile of papers. `sorted()` made copies. The list **method** `.sort()` instead
            rearranges the **original** papers - and hands you nothing back.

            ```python
            queue = [3, 1, 2]
            queue.sort()
            print(queue)

            answer = queue.sort(reverse=True)
            print(queue)
            print(answer)
            ```

            The list is now in order, but `answer` is `None`: `.sort()` did its work on the list and
            returned nothing.

            The real words: `.sort()` sorts *in place* (it changes the object you call it on). Methods
            that change something in place usually return `None`.

            Watch out for the classic bug: `items = items.sort()`. The list gets sorted... and then you
            throw it away by storing `None` in `items`. If you want a sorted list **back**, use
            `sorted(items)`.
        ''',
        "title": "Fix the bug: newest first",
        "difficulty": 0,
        "prompt": r'''
            Show the most recent events first. The starter has one bug: it returns `None`.
            Find and fix it.

            **Write:** `newest_first(timestamps)` (fix the starter)

            - `timestamps`: a list of numbers, e.g. `[10, 30, 20]`
            - **Returns:** a **new** list of the same numbers, biggest first

            **Rules**
            - Don't change the list you were given (the caller's list must stay `[10, 30, 20]`).
            - An empty list returns `[]`.

            **Examples**
            ```python
            newest_first([10, 30, 20])   # returns [30, 20, 10]
            newest_first([])             # returns []
            ```
        ''',
        "starter": r'''
            def newest_first(timestamps):
                result = timestamps.sort(reverse=True)
                return result
        ''',
        "tests": r'''
            from solution import newest_first

            def test_biggest_timestamp_comes_first():
                got = newest_first([10, 30, 20])
                assert got == [30, 20, 10], f"got {got!r}"

            def test_callers_list_is_not_changed():
                data = [10, 30, 20]
                newest_first(data)
                assert data == [10, 30, 20], f"the caller's list changed to {data!r}"

            def test_empty_list_returns_empty_list():
                assert newest_first([]) == []
        ''',
        "solution": r'''
            def newest_first(timestamps):
                return sorted(timestamps, reverse=True)
        ''',
        "hints": [
            "What does the list method `.sort()` return?",
            "`.sort()` changes the list in place and returns `None`. You need the function that builds a new sorted list instead.",
            "Use `sorted(...)` on `timestamps` with `reverse=True` and return its result directly.",
        ],
    },
    {
        "id": "sorting-s4",
        "lesson": r'''
            ## `lambda`: a tiny throwaway function

            Sometimes the key you need doesn't exist yet - "sort these dicts by their `price`". You could
            write a whole `def` for that, but it's like printing a business card just to write down one
            phone number. A `lambda` is a **sticky note**: a one-line function written right where you
            need it.

            ```python
            models = [{"name": "big", "price": 5.0}, {"name": "tiny", "price": 0.2}]

            def get_price(m):
                return m["price"]

            print(sorted(models, key=get_price)[0]["name"])
            print(sorted(models, key=lambda m: m["price"])[0]["name"])
            ```

            Both lines print the same thing. `lambda m: m["price"]` means "take `m`, give back
            `m["price"]`".

            The real words: a *lambda* (or *anonymous function*) is `lambda parameters: expression`.
            There is no `return` keyword - the expression after the colon **is** the return value.

            Watch out: a lambda can only hold one expression. Anything bigger deserves a normal `def`.
        ''',
        "title": "Best results first",
        "difficulty": 0,
        "prompt": r'''
            Search results should be shown best match first. Each result is a dict like
            `{"id": "doc1", "score": 0.8}`.

            **Write:** `by_score(results)`

            - `results`: a list of dicts, each with an `"id"` (str) and a `"score"` (float)
            - **Returns:** a **new** list of the same dicts, sorted by `"score"`, highest first

            **Rules**
            - Use a `lambda` as the sort key (a *lambda* is a tiny one-line function).
            - Don't change the list you were given.
            - An empty list returns `[]`.

            **Examples**
            ```python
            by_score([{"id": "a", "score": 0.2}, {"id": "b", "score": 0.9}, {"id": "c", "score": 0.5}])
            # returns [{"id": "b", "score": 0.9}, {"id": "c", "score": 0.5}, {"id": "a", "score": 0.2}]
            by_score([])   # returns []
            ```
        ''',
        "starter": r'''
            def by_score(results):
                ...
        ''',
        "tests": r'''
            from solution import by_score

            def ids(results):
                return [r["id"] for r in results]

            def test_highest_score_comes_first():
                got = ids(by_score([{"id": "a", "score": 0.2}, {"id": "b", "score": 0.9},
                                    {"id": "c", "score": 0.5}]))
                assert got == ["b", "c", "a"], f"order of ids: {got!r}"

            def test_callers_list_is_not_changed():
                data = [{"id": "a", "score": 0.2}, {"id": "b", "score": 0.9}]
                by_score(data)
                assert ids(data) == ["a", "b"], "the caller's list was changed"

            def test_empty_list_returns_empty_list():
                assert by_score([]) == []
        ''',
        "solution": r'''
            def by_score(results):
                return sorted(results, key=lambda r: r["score"], reverse=True)
        ''',
        "hints": [
            "Use `sorted()` with a `key=` and `reverse=True`.",
            "The key must turn one result dict into the number to sort by - its `\"score\"` value. A `lambda` does that in one line.",
            "Return `sorted(results, key=..., reverse=True)` where the key is a lambda that takes one result `r` and gives back `r[\"score\"]`.",
        ],
    },
    {
        "id": "sorting-s5",
        "lesson": r'''
            ## `min()` and `max()` with a key

            To find the tallest person in a room you don't line everyone up - you just look for the
            tallest. `min()` and `max()` do exactly that, and they take the same `key=` as `sorted`.

            ```python
            models = [{"name": "a", "context": 8000}, {"name": "b", "context": 200000}]
            biggest = max(models, key=lambda m: m["context"])
            print(biggest)
            print(biggest["name"])
            ```

            Notice: `max` returns the **whole item** (the full dict), not the number the key produced.
            Take what you need from it afterwards.

            An empty list has no biggest item, so `max([])` raises a `ValueError`. Either check first
            (`if not items:`), or pass `default=`, which is returned instead of an error:

            ```python
            print(max([], default=None))
            print(min([3, 1, 2], default=None))
            ```

            The real words: `key=` works the same everywhere it appears - `sorted`, `.sort`, `min`,
            `max`.
        ''',
        "title": "Cheapest model",
        "difficulty": 0,
        "prompt": r'''
            Pick the cheapest model from a price list. Each model is a dict like
            `{"name": "gpt-4o", "price": 5.0}`.

            **Write:** `cheapest(models)`

            - `models`: a list of dicts, each with a `"name"` (str) and a `"price"` (float)
            - **Returns:** the **name** (a string, not the whole dict) of the model with the
              lowest price, or `None`

            **Rules**
            - Use `min` with a `key`.
            - If the list is empty, return `None`.

            **Examples**
            ```python
            cheapest([{"name": "big", "price": 5.0}, {"name": "small", "price": 0.5}])  # returns "small"
            cheapest([{"name": "only", "price": 2.0}])                                 # returns "only"
            cheapest([])                                                               # returns None
            ```
        ''',
        "starter": r'''
            def cheapest(models):
                ...
        ''',
        "tests": r'''
            from solution import cheapest

            def test_returns_name_of_cheapest_model():
                got = cheapest([{"name": "big", "price": 5.0}, {"name": "small", "price": 0.5},
                                {"name": "mid", "price": 1.0}])
                assert got == "small", f"got {got!r}"

            def test_returns_a_name_not_a_dict():
                got = cheapest([{"name": "only", "price": 2.0}])
                assert got == "only", f"got {got!r} - return just the name"

            def test_empty_list_returns_none():
                assert cheapest([]) is None
        ''',
        "solution": r'''
            def cheapest(models):
                if not models:
                    return None
                best = min(models, key=lambda m: m["price"])
                return best["name"]
        ''',
        "hints": [
            "`min(items, key=...)` returns the whole item whose key is smallest - here, a whole dict.",
            "First handle the empty list, then find the cheapest dict with `min` and a lambda key on `\"price\"`, then take its `\"name\"`.",
            "1) If `models` is empty, return None. 2) Call `min` on models with a lambda that returns `m[\"price\"]`. 3) Return the `\"name\"` of the dict you got back.",
        ],
    },
    {
        "id": "sorting-s6",
        "lesson": r'''
            ## Sorting by two things: tuple keys

            A phone book is sorted by last name, and **only when two last names are equal** does the
            first name decide. Tuples compare the same way: first part first, and the next part only
            breaks ties.

            ```python
            print((1, "b") < (1, "c"))   # tie on 1, so "b" vs "c" decides
            print((2, "a") < (1, "z"))   # 2 vs 1 already decides

            people = [("kim", 30), ("ada", 25), ("bo", 30)]
            print(sorted(people, key=lambda p: (p[1], p[0])))
            ```

            So a key that returns a **tuple** sorts by several rules at once.

            Need one rule to go the other way? For numbers, put a minus in front: `-p[1]` turns "small
            to big" into "big to small" for just that part.

            ```python
            people = [("kim", 30), ("ada", 25), ("bo", 30)]
            print(sorted(people, key=lambda p: (-p[1], p[0])))
            ```

            The real words: this is a *tuple key* (or *multi-key sort*). Watch out: `reverse=True`
            flips **every** part of the tuple, not just one.
        ''',
        "title": "Predict: two-part keys",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            models = [("sonnet", 3), ("haiku", 1), ("opus", 3)]
            print(sorted(models, key=lambda m: (m[1], m[0])))
            print(sorted(models, key=lambda m: (-m[1], m[0])))
        ''',
        "solution": r'''
            [('haiku', 1), ('opus', 3), ('sonnet', 3)]
            [('opus', 3), ('sonnet', 3), ('haiku', 1)]
        ''',
        "explanation": r'''
            The key returns a tuple, so Python compares the number first and only looks at the
            name when the numbers tie. `opus` and `sonnet` both have `3`, so the name decides:
            `opus` comes first (A-Z). In the second line the minus flips just the number part
            (big first), while names still go A-Z. Python prints tuples with round brackets and
            strings inside them with single quotes.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "The key turns each pair into a tuple `(number, name)` - sort by that tuple, then print the original pairs.",
            "Tuples compare their first parts; the second part only matters on a tie. `-m[1]` makes bigger numbers come first.",
            "Line 1: numbers small to big, ties by name A-Z. Line 2: numbers big to small, ties still A-Z. Write each list like `[('a', 1), ...]` with single quotes.",
        ],
    },
    {
        "id": "sorting-1",
        "lesson": r'''
            ## Copy or in place: choosing the right tool

            You now know two ways to order a list. Which to pick?

            - `sorted(items)` - the **photocopier**. Use it when the caller's list must stay as it was,
              or when you want the sorted list as a result.
            - `items.sort()` - **rearranging the originals**. Use it when you *own* the list and want to
              change it; it saves making a copy.

            A function that has no `return` line still returns something: `None`.

            ```python
            def add_default(tags):
                tags.append("general")

            my_tags = ["rag", "llm"]
            result = add_default(my_tags)
            print(my_tags)   # changed by the function!
            print(result)
            ```

            The real words: changing an object that the caller passed in is called *mutating* it (or a
            *side effect*). A function that does this should say so - usually by returning `None`, just
            like `.sort()` does.

            Watch out: a function that sorts *in place* and also returns the list confuses readers. Pick
            one style.
        ''',
        "title": "Copy or in place",
        "hints": [
            "Look at `sorted()` and the list method `.sort()`: one builds a new list, the other changes the list you call it on.",
            "`ranked` needs a new list in reverse order. `sort_in_place` must change the caller's list and not return anything.",
            "1) In `ranked`, call `sorted` on the scores with `reverse=True` and return the result. 2) In `sort_in_place`, call `.sort()` on `scores` and write no `return` - a function without one returns `None`.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Two ways to order a list of relevance scores: make a sorted **copy**, or sort the
            original list **in place** (change the list itself).

            **Write:** `ranked(scores)` and `sort_in_place(scores)`

            - `scores`: a list of numbers, e.g. `[0.2, 0.9, 0.5]`
            - **`ranked` returns:** a **new** list of the scores, highest to lowest
            - **`sort_in_place` returns:** `None` - it changes the list it was given instead

            **Rules**
            - `ranked` must not change the caller's list.
            - `sort_in_place` sorts the caller's list lowest to highest and returns `None`.
            - Both work on an empty list (`ranked([])` returns `[]`).

            **Examples**
            ```python
            s = [0.2, 0.9, 0.5]
            ranked(s)          # returns [0.9, 0.5, 0.2]; s is still [0.2, 0.9, 0.5]
            sort_in_place(s)   # returns None; s is now [0.2, 0.5, 0.9]
            ranked([])         # returns []
            ```
        ''',
        "starter": r'''
            def ranked(scores):
                ...


            def sort_in_place(scores):
                ...
        ''',
        "tests": r'''
            from solution import ranked, sort_in_place

            def test_ranked_returns_highest_first():
                got = ranked([0.2, 0.9, 0.5])
                assert got == [0.9, 0.5, 0.2], f"got {got!r}"

            def test_ranked_does_not_change_callers_list():
                s = [3, 1, 2]
                ranked(s)
                assert s == [3, 1, 2], f"caller's list changed to {s!r}"

            def test_sort_in_place_sorts_the_list_and_returns_none():
                s = [0.2, 0.9, 0.5]
                result = sort_in_place(s)
                assert s == [0.2, 0.5, 0.9], f"list is {s!r}"
                assert result is None, f"returned {result!r}"

            def test_both_handle_an_empty_list():
                assert ranked([]) == []
                s = []
                sort_in_place(s)
                assert s == []
        ''',
        "solution": r'''
            def ranked(scores):
                return sorted(scores, reverse=True)


            def sort_in_place(scores):
                scores.sort()
        ''',
    },
    {
        "id": "sorting-2",
        "lesson": r'''
            ## Stable sorting and ties

            Think of a queue at a bakery where the baker serves **VIPs first**. Two VIPs don't fight -
            they keep the order they arrived in. Python's sort works the same way: items whose keys are
            **equal** keep their original order.

            ```python
            tickets = [{"who": "ann", "vip": 0}, {"who": "bo", "vip": 1},
                       {"who": "cy", "vip": 0}, {"who": "di", "vip": 1}]
            served = sorted(tickets, key=lambda t: -t["vip"])
            print([t["who"] for t in served])
            ```

            `bo` still comes before `di`, and `ann` before `cy`. The real word: Python's sort is *stable*.

            `max` and `min` have a similar tie rule: when several items tie, they return the **first**
            one they met.

            ```python
            print(max([-3, 3, 1], key=abs))
            print(max([], key=abs, default=None))
            ```

            Remember `default=` from before - it is what `max` returns for an empty list.
        ''',
        "title": "Shortest and longest chunks",
        "hints": [
            "Both functions need `key=len`: `sorted` for the first, `max` for the second.",
            "`sorted` is stable, so sorting by length alone keeps equal-length chunks in their original order. `max` returns the first of several equal maximums.",
            "1) `by_length`: return `sorted` with `key=len`. 2) `longest`: return `max` over the chunks with `key=len` and `default=None`, so an empty list gives `None` instead of an error.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A RAG pipeline splits documents into text chunks. Order them by size and find the
            biggest one.

            **Write:** `by_length(chunks)` and `longest(chunks)`

            - `chunks`: a list of strings, e.g. `["ccc", "a", "bb"]`
            - **`by_length` returns:** a new list of the chunks, shortest first
            - **`longest` returns:** the longest chunk (a string), or `None`

            **Rules**
            - `by_length` orders by length only, not alphabetically. Chunks of equal length
              keep their original order.
            - `longest` returns the **first** one if several chunks tie for longest.
            - `longest([])` returns `None` (no error).
            - `longest` must use `max(..., key=...)` (a check looks for it).

            **Examples**
            ```python
            by_length(["ccc", "a", "bb", "x"])   # returns ["a", "x", "bb", "ccc"]
            by_length(["zz", "b", "aaa"])        # returns ["b", "zz", "aaa"]
            longest(["ab", "cd", "e"])           # returns "ab"
            longest([])                          # returns None
            ```
        ''',
        "starter": r'''
            def by_length(chunks):
                ...


            def longest(chunks):
                ...
        ''',
        "tests": r'''
            from solution import by_length, longest

            def test_by_length_shortest_first_ties_keep_order():
                got = by_length(["ccc", "a", "bb", "x"])
                assert got == ["a", "x", "bb", "ccc"], f"got {got!r}"

            def test_by_length_is_not_alphabetical():
                got = by_length(["zz", "b", "aaa"])
                assert got == ["b", "zz", "aaa"], f"got {got!r}"

            def test_longest_returns_first_on_tie():
                got = longest(["ab", "cd", "e"])
                assert got == "ab", f"got {got!r}"

            def test_longest_of_empty_list_is_none():
                assert longest([]) is None

            def test_uses_max_with_a_key():
                import ast
                tree = ast.parse(source())
                ok = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "max"
                         and any(k.arg == "key" for k in n.keywords) for n in ast.walk(tree))
                assert ok, "use max(..., key=...)"
        ''',
        "solution": r'''
            def by_length(chunks):
                return sorted(chunks, key=len)


            def longest(chunks):
                return max(chunks, key=len, default=None)
        ''',
    },
    {
        "id": "sorting-7",
        "lesson": r'''
            ## Writing your own tuple key

            You predicted tuple keys earlier - now you write one. The recipe:

            1. List your rules from most important to least important.
            2. Return them, in that order, as a tuple from the key.

            ```python
            tasks = [{"title": "deploy", "team": "ops", "hours": 3},
                     {"title": "docs", "team": "dev", "hours": 1},
                     {"title": "fix", "team": "ops", "hours": 1}]
            ordered = sorted(tasks, key=lambda t: (t["team"], t["hours"]))
            print([t["title"] for t in ordered])
            ```

            Team first (A-Z), and only inside the same team do hours decide.

            Real engineers keep the official docs open while they work. Python has a short, friendly
            guide to sorting (the *Sorting HOWTO*) - it covers key functions, tuple keys and stability,
            everything in this chapter. Reading it now is part of this step.

            Watch out: if every part of your key ties, the stable sort keeps the original order - so
            you don't need to add a rule for that.
        ''',
        "title": "Catalog order: provider, then price",
        "difficulty": 1,
        "research": {
            "note": "Skim the *Sorting HOWTO* (the \"Key Functions\" and \"Sort Stability and Complex Sorts\" sections), then come back and write the key.",
            "links": [
                {"title": "Sorting Techniques - Python HOWTO", "url": "https://docs.python.org/3/howto/sorting.html"},
            ],
        },
        "prompt": r'''
            A model picker lists models grouped by provider, cheapest first inside each group.

            **Write:** `catalog_order(models)`

            - `models`: a list of dicts `{"name": str, "provider": str, "price": float}`,
              e.g. `{"name": "haiku", "provider": "anthropic", "price": 0.8}`
            - **Returns:** a **new** list of the model **names** (strings) in display order

            **Rules**
            - Order by `provider` A-Z first.
            - Inside the same provider, order by `price`, lowest first.
            - Models with the same provider **and** price keep their original order.
            - Don't change the list you were given. An empty list returns `[]`.

            **Examples**
            ```python
            catalog_order([
                {"name": "gpt-4o", "provider": "openai", "price": 5.0},
                {"name": "sonnet", "provider": "anthropic", "price": 3.0},
                {"name": "mini", "provider": "openai", "price": 0.15},
                {"name": "haiku", "provider": "anthropic", "price": 0.8},
            ])
            # returns ["haiku", "sonnet", "mini", "gpt-4o"]
            catalog_order([])   # returns []
            ```
        ''',
        "starter": r'''
            def catalog_order(models):
                ...
        ''',
        "tests": r'''
            from solution import catalog_order

            def m(name, provider, price):
                return {"name": name, "provider": provider, "price": price}

            DATA = [m("gpt-4o", "openai", 5.0), m("sonnet", "anthropic", 3.0),
                    m("mini", "openai", 0.15), m("haiku", "anthropic", 0.8)]

            def test_grouped_by_provider_then_cheapest_first():
                got = catalog_order(DATA)
                assert got == ["haiku", "sonnet", "mini", "gpt-4o"], f"got {got!r}"

            def test_provider_decides_before_price():
                got = catalog_order([m("cheap", "zeta", 0.1), m("pricey", "alpha", 9.0)])
                assert got == ["pricey", "cheap"], f"got {got!r}"

            def test_full_ties_keep_original_order():
                got = catalog_order([m("b", "x", 1.0), m("c", "x", 1.0), m("a", "x", 1.0)])
                assert got == ["b", "c", "a"], f"got {got!r}"

            def test_input_list_is_not_changed():
                data = list(DATA)
                catalog_order(data)
                assert data == DATA, "the input list was changed"

            def test_empty_list_returns_empty_list():
                assert catalog_order([]) == []
        ''',
        "solution": r'''
            def catalog_order(models):
                ordered = sorted(models, key=lambda m: (m["provider"], m["price"]))
                return [m["name"] for m in ordered]
        ''',
        "hints": [
            "One `sorted` call is enough if the key returns a tuple with both rules in it.",
            "The key should give back `(provider, price)` for each model - most important rule first. Then turn the sorted dicts into a list of names.",
            "1) `sorted(models, key=lambda m: (m[\"provider\"], m[\"price\"]))`-style call. 2) Loop over the result (or use a comprehension) collecting each `\"name\"`. 3) Return that list.",
        ],
    },
    {
        "id": "sorting-8",
        "lesson": r'''
            ## `map` and `filter`: assembly line and sieve

            Picture a factory line. `map` is a machine that does **the same thing to every item** that
            passes by. `filter` is a sieve: it lets through only the items that pass a test.

            ```python
            words = ["hi", "", "llm", "  "]
            print(list(map(len, words)))
            print(list(filter(lambda w: w.strip(), words)))
            print(list(map(str.upper, filter(lambda w: w.strip(), words))))
            ```

            - `map(f, items)` calls `f(item)` for each item.
            - `filter(f, items)` keeps each item where `f(item)` is *truthy* (an empty string is falsy).

            The real words: both are *built-in functions* that take a function as an argument (like
            `key=`). They are *lazy*: they don't build a list, they hand out results one at a time. Wrap
            them in `list(...)` to see or keep the results.

            Watch out: `print(map(len, words))` prints something like `<map object at 0x...>`, not the
            numbers. You'll usually write a comprehension instead in everyday code - but you'll read
            `map`/`filter` in other people's code all the time.
        ''',
        "title": "Lengths of non-blank chunks",
        "difficulty": 1,
        "research": {
            "note": "Read the official entries for the built-ins `map()` and `filter()` - what they take and what they return - then come back.",
            "links": [
                {"title": "map() - Built-in Functions", "url": "https://docs.python.org/3/library/functions.html#map"},
                {"title": "filter() - Built-in Functions", "url": "https://docs.python.org/3/library/functions.html#filter"},
            ],
        },
        "prompt": r'''
            Before embedding text chunks, a pipeline drops blank ones and records how long the
            rest are.

            **Write:** `chunk_lengths(chunks)`

            - `chunks`: a list of strings, e.g. `["hello", "", "  ", "ab c"]`
            - **Returns:** a list of ints - the length (`len`) of each **non-blank** chunk, in
              the original order

            **Rules**
            - A chunk is *blank* if it is empty or contains only whitespace; skip it.
            - Measure the chunk exactly as given (spaces inside or around it count).
            - Return a real list (not a `map`/`filter` object). An empty list returns `[]`.
            - Your code must call the built-in `map` and `filter` functions (a check looks for
              both).

            **Examples**
            ```python
            chunk_lengths(["hello", "", "  ", "ab c"])   # returns [5, 4]
            chunk_lengths([" hi "])                      # returns [4]
            chunk_lengths([])                            # returns []
            ```
        ''',
        "starter": r'''
            def chunk_lengths(chunks):
                ...
        ''',
        "tests": r'''
            from solution import chunk_lengths

            def test_blank_chunks_are_skipped():
                got = chunk_lengths(["hello", "", "  ", "ab c"])
                assert got == [5, 4], f"got {got!r}"

            def test_surrounding_spaces_are_counted():
                got = chunk_lengths([" hi "])
                assert got == [4], f"got {got!r}"

            def test_returns_a_real_list():
                got = chunk_lengths(["abc", "\n\t"])
                assert isinstance(got, list), f"returned a {type(got).__name__}, expected a list"
                assert got == [3], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert chunk_lengths([]) == []

            def test_uses_map_and_filter():
                import ast
                called = {n.func.id for n in ast.walk(ast.parse(source()))
                          if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
                assert {"map", "filter"} <= called, "use the built-in map and filter functions"
        ''',
        "solution": r'''
            def chunk_lengths(chunks):
                kept = filter(lambda c: c.strip(), chunks)
                return list(map(len, kept))
        ''',
        "hints": [
            "`filter` can drop the blank chunks, and `map` can turn each remaining chunk into its length.",
            "A chunk is blank when `.strip()` leaves an empty string - and an empty string is falsy, so it works as a filter test. Filter first, then map, then make a list.",
            "1) `filter` the chunks with a lambda that returns `c.strip()`. 2) `map` `len` over what's left. 3) Wrap it in `list(...)` and return it.",
        ],
    },
    {
        "id": "sorting-3",
        "title": "Top-k results",
        "hints": [
            "A key function can return a tuple to sort by several things; putting a minus in front of a number flips its direction.",
            "Sort by (negative score, id): highest score first, ties alphabetical by id. Then keep the first `k` and take their ids.",
            "1) If `k <= 0`, return `[]`. 2) Use `sorted()` (it makes a new list) with a lambda key returning `(-r[\"score\"], r[\"id\"])`. 3) Slice off the first `k`. 4) Build a list of their `\"id\"` values.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A vector search returns many results; a RAG app keeps only the best `k` of them
            (this is called *top-k*).

            **Write:** `top_k(results, k)`

            - `results`: a list of dicts `{"id": str, "score": float}`
            - `k`: an int, how many results to keep, e.g. `3`
            - **Returns:** a list of the **ids** (strings) of the `k` best results, best first

            **Rules**
            - Highest score first.
            - Equal scores are ordered by id A-Z (ascending) - even though scores go high to low.
            - If `k` is larger than the number of results, return all of their ids.
            - If `k` is `0` or negative, return `[]`.
            - Don't change the list you were given.

            **Examples**
            ```python
            results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9},
                       {"id": "b", "score": 0.7}, {"id": "d", "score": 0.1}]
            top_k(results, 3)    # returns ["a", "b", "c"]
            top_k(results, 10)   # returns ["a", "b", "c", "d"]
            top_k(results, 0)    # returns []
            top_k([{"id": "x", "score": 1.0}, {"id": "m", "score": 1.0}], 2)   # returns ["m", "x"]
            ```
        ''',
        "starter": r'''
            def top_k(results, k):
                ...
        ''',
        "tests": r'''
            from solution import top_k

            RESULTS = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9},
                       {"id": "b", "score": 0.7}, {"id": "d", "score": 0.1}]

            def test_top_3_with_a_score_tie():
                got = top_k(RESULTS, 3)
                assert got == ["a", "b", "c"], f"got {got!r}"

            def test_top_1_returns_single_best_id():
                assert top_k(RESULTS, 1) == ["a"]

            def test_k_larger_than_results_returns_all():
                got = top_k(RESULTS, 10)
                assert got == ["a", "b", "c", "d"], f"got {got!r}"

            def test_k_zero_or_negative_returns_empty_list():
                assert top_k(RESULTS, 0) == [], f"k=0 -> {top_k(RESULTS, 0)!r}"
                assert top_k(RESULTS, -1) == [], f"k=-1 -> {top_k(RESULTS, -1)!r}"

            def test_input_list_is_not_changed():
                data = [dict(r) for r in RESULTS]
                top_k(data, 2)
                assert data == RESULTS, "the input list was modified"

            def test_ties_ordered_by_id_ascending():
                got = top_k([{"id": "x", "score": 1.0}, {"id": "m", "score": 1.0}], 2)
                assert got == ["m", "x"], f"got {got!r}"
        ''',
        "solution": r'''
            def top_k(results, k):
                if k <= 0:
                    return []
                ordered = sorted(results, key=lambda r: (-r["score"], r["id"]))
                return [r["id"] for r in ordered[:k]]
        ''',
    },
    {
        "id": "sorting-4",
        "lesson": r'''
            ## Putting it together: `operator.itemgetter`

            Writing `lambda pair: pair[1]` gets repetitive. The `operator` module has a ready-made key
            maker: `itemgetter(1)` builds a function that picks index `1` from whatever it's given.
            Give it several indexes and it returns a tuple - a tuple key without a lambda.

            ```python
            from operator import itemgetter

            pick = itemgetter(1, 0)
            print(pick(("gpt", 820)))
            print(sorted([("b", 2), ("a", 2), ("c", 1)], key=itemgetter(1, 0)))
            ```

            It works with dict keys too: `itemgetter("score")`.
        ''',
        "title": "Rank models by latency",
        "hints": [
            "`latencies.items()` gives `(model, ms)` pairs, and `operator.itemgetter` builds a key that picks positions out of each pair.",
            "Sort the pairs by latency first and name second - `itemgetter` can take two indexes and return both as a tuple. For the fastest, call `min` over the model names with a key that also breaks ties by name.",
            "1) `from operator import itemgetter`. 2) `rank_models`: sort `latencies.items()` with `itemgetter` picking index 1, then index 0. 3) `fastest`: return `None` for an empty dict; otherwise `min` over the dict with a lambda key returning `(latency, name)`.",
        ],
        "difficulty": 2,
        "prompt": r'''
            Compare LLMs by speed using a dict of measured latencies.

            **Write:** `rank_models(latencies)` and `fastest(latencies)`

            - `latencies`: a dict mapping model name (str) -> average latency in ms (int),
              e.g. `{"gpt-4o": 820, "haiku": 310}`
            - **`rank_models` returns:** a list of `(model, ms)` tuples, fastest first
            - **`fastest` returns:** the **name** (str) of the fastest model, or `None`

            **Rules**
            - `rank_models`: equal latencies are ordered by model name A-Z. An empty dict
              returns `[]`.
            - `fastest`: on a tie, return the alphabetically first name. An empty dict
              returns `None`.
            - Your code must use `operator.itemgetter` (for the sort key) and `min(`
              (a check looks for both).

            **Examples**
            ```python
            lat = {"o3": 2400, "llama": 310, "gpt-4o": 820, "haiku": 310}
            rank_models(lat)   # returns [("haiku", 310), ("llama", 310), ("gpt-4o", 820), ("o3", 2400)]
            fastest(lat)       # returns "haiku"
            fastest({"a": 5, "b": 1})   # returns "b"
            fastest({})        # returns None
            ```
        ''',
        "starter": r'''
            def rank_models(latencies):
                ...


            def fastest(latencies):
                ...
        ''',
        "tests": r'''
            from solution import rank_models, fastest

            LAT = {"o3": 2400, "llama": 310, "gpt-4o": 820, "haiku": 310}

            def test_rank_models_fastest_first_ties_by_name():
                got = rank_models(LAT)
                assert got == [("haiku", 310), ("llama", 310), ("gpt-4o", 820), ("o3", 2400)], f"got {got!r}"

            def test_rank_models_empty_dict_returns_empty_list():
                assert rank_models({}) == []

            def test_fastest_tie_returns_alphabetically_first():
                got = fastest(LAT)
                assert got == "haiku", f"got {got!r}"

            def test_fastest_returns_name_not_latency():
                got = fastest({"a": 5, "b": 1})
                assert got == "b", f"got {got!r}"

            def test_fastest_empty_dict_returns_none():
                assert fastest({}) is None

            def test_uses_itemgetter_and_min():
                src = source()
                assert "itemgetter" in src, "use operator.itemgetter"
                assert "min(" in src, "use min"
        ''',
        "solution": r'''
            from operator import itemgetter


            def rank_models(latencies):
                return sorted(latencies.items(), key=itemgetter(1, 0))


            def fastest(latencies):
                if not latencies:
                    return None
                return min(latencies, key=lambda m: (latencies[m], m))
        ''',
    },
    {
        "id": "sorting-5",
        "lesson": r'''
            ## Putting it together: sorting in two passes

            A minus sign can flip a number, but not a string - `-"abc"` is an error. The trick uses
            *stability*: sort by the **least** important rule first, then sort again by the more
            important rules. Ties in the second sort keep the order from the first.

            ```python
            names = ["ann", "zed", "bo"]
            teams = {"ann": "x", "zed": "x", "bo": "a"}
            step1 = sorted(names, reverse=True)
            print(sorted(step1, key=lambda n: teams[n]))
            ```
        ''',
        "title": "Mixed-direction catalog",
        "hints": [
            "You can't put a minus in front of a string, so one tuple key can't do 'name Z-A'. But Python's sort is stable - you can sort more than once.",
            "Sort by the least important rule first (name, Z-A), then sort that result by the other three rules. Ties in the second sort keep the order from the first sort.",
            "1) `sorted` by `\"name\"` with `reverse=True`. 2) `sorted` that result with a tuple key `(provider, -context, price)`. 3) Return the second result.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Order a model catalog for display, where some rules go up and others go down.

            **Write:** `sort_catalog(models)`

            - `models`: a list of dicts `{"name": str, "provider": str, "context": int, "price": float}`
            - **Returns:** a **new** list of the same dicts in this order:
              1. `provider` ascending (A-Z)
              2. then `context` **descending** (biggest window first)
              3. then `price` ascending (cheapest first)
              4. then `name` **descending** (Z-A)

            **Rules**
            - Each rule only decides between models that tie on all the rules above it.
            - Return a new list; don't change the list you were given.

            **Examples** (showing only the names of the result)
            ```python
            sort_catalog([
                {"name": "a", "provider": "openai", "context": 128000, "price": 5.0},
                {"name": "b", "provider": "anthropic", "context": 200000, "price": 3.0},
                {"name": "c", "provider": "openai", "context": 200000, "price": 2.0},
            ])
            # names in order: "b", "c", "a"

            sort_catalog([
                {"name": "alpha", "provider": "x", "context": 1000, "price": 2.0},
                {"name": "beta",  "provider": "x", "context": 1000, "price": 1.0},
                {"name": "zeta",  "provider": "x", "context": 1000, "price": 2.0},
            ])
            # names in order: "beta", "zeta", "alpha"
            ```
        ''',
        "starter": r'''
            def sort_catalog(models):
                ...
        ''',
        "tests": r'''
            from solution import sort_catalog

            def m(name, provider, context, price):
                return {"name": name, "provider": provider, "context": context, "price": price}

            def names(models):
                return [x["name"] for x in models]

            def test_provider_a_to_z_then_context():
                got = names(sort_catalog([m("a", "openai", 128000, 5.0), m("b", "anthropic", 200000, 3.0),
                                          m("c", "openai", 200000, 2.0)]))
                assert got == ["b", "c", "a"], f"got {got!r}"

            def test_bigger_context_first_within_provider():
                got = names(sort_catalog([m("small", "x", 8000, 1.0), m("big", "x", 32000, 9.0)]))
                assert got == ["big", "small"], f"got {got!r}"

            def test_cheaper_first_then_name_z_to_a():
                got = names(sort_catalog([m("alpha", "x", 1000, 2.0), m("beta", "x", 1000, 1.0),
                                          m("zeta", "x", 1000, 2.0)]))
                assert got == ["beta", "zeta", "alpha"], f"got {got!r}"

            def test_all_four_rules_together():
                data = [m("q", "b", 10, 1.0), m("r", "a", 10, 1.0), m("s", "a", 20, 5.0),
                        m("t", "a", 20, 1.0), m("u", "a", 20, 1.0)]
                got = names(sort_catalog(data))
                assert got == ["u", "t", "s", "r", "q"], f"got {got!r}"

            def test_returns_new_list_and_input_unchanged():
                data = [m("b", "p", 1, 1.0), m("a", "p", 2, 1.0)]
                snapshot = list(data)
                result = sort_catalog(data)
                assert data == snapshot and result is not data, "return a new list, leave the input alone"
        ''',
        "solution": r'''
            def sort_catalog(models):
                ordered = sorted(models, key=lambda x: x["name"], reverse=True)
                return sorted(ordered, key=lambda x: (x["provider"], -x["context"], x["price"]))
        ''',
    },
    {
        "id": "sorting-6",
        "title": "Keyword rerank",
        "hints": [
            "Break it into steps: score every doc, drop the zeros, sort. `map` can do the scoring and `filter` the dropping.",
            "Turn the query into a set of lowercase words; a doc's score is the size of the overlap (`&`) with the set of its own lowercase words. A stable sort on `(-score, len(doc))` keeps full ties in input order.",
            "1) `terms` = set of the lowercased query words. 2) `map` each doc to a `(score, doc)` pair. 3) `filter` out pairs with score 0. 4) `sorted` with key `(-score, len(doc))`. 5) Return just the docs.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A tiny keyword *reranker*: after retrieval, put the documents that best match the
            user's query first.

            **Write:** `rerank(docs, query)`

            - `docs`: a list of strings, e.g. `["Python sorting guide", "Cooking pasta"]`
            - `query`: a string, e.g. `"python sorting"`
            - **Returns:** a new list of the matching documents (the original strings,
              unchanged), best first

            **Rules**
            - The query's *terms* are its words (split on whitespace), lowercased. Matching
              ignores case: `"LLM"` matches `"llm"`.
            - A document's score is how many **distinct** query terms appear among its own
              lowercased whitespace-separated words. Repeating a word doesn't add points.
            - Drop documents with score 0. If none match, return `[]`.
            - Order by score, highest first; on equal score, the shorter document (fewer
              characters) first; on a full tie, keep the original order.
            - Your code must call the built-in `map` and `filter` functions (a check looks
              for both).

            **Examples**
            ```python
            docs = ["Python sorting guide", "Sorting in Python with key functions",
                    "Cooking pasta", "python"]
            rerank(docs, "python sorting")
            # returns ["Python sorting guide", "Sorting in Python with key functions", "python"]
            rerank(["rag rag rag rag", "rag agents"], "rag agents")
            # returns ["rag agents", "rag rag rag rag"]
            rerank(["b llm", "a llm", "c llm"], "LLM")   # returns ["b llm", "a llm", "c llm"]
            rerank(["alpha", "beta"], "gamma")           # returns []
            ```
        ''',
        "starter": r'''
            def rerank(docs, query):
                ...
        ''',
        "tests": r'''
            from solution import rerank

            def test_best_match_first_and_non_matches_dropped():
                docs = ["Python sorting guide", "Sorting in Python with key functions", "Cooking pasta", "python"]
                got = rerank(docs, "python sorting")
                assert got == ["Python sorting guide", "Sorting in Python with key functions", "python"], f"got {got!r}"

            def test_no_matches_returns_empty_list():
                assert rerank(["alpha", "beta"], "gamma") == []

            def test_repeated_words_count_once():
                docs = ["rag rag rag rag", "rag agents"]
                got = rerank(docs, "rag agents")
                assert got == ["rag agents", "rag rag rag rag"], f"got {got!r}"

            def test_full_tie_keeps_original_order():
                docs = ["b llm", "a llm", "c llm"]
                got = rerank(docs, "LLM")
                assert got == ["b llm", "a llm", "c llm"], f"got {got!r}"

            def test_shorter_doc_first_on_equal_score():
                docs = ["tool calling explained in depth", "tool calling"]
                got = rerank(docs, "tool")
                assert got == ["tool calling", "tool calling explained in depth"], f"got {got!r}"

            def test_uses_map_and_filter():
                import ast
                called = {n.func.id for n in ast.walk(ast.parse(source()))
                          if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
                assert {"map", "filter"} <= called, "use the built-in map and filter functions"
        ''',
        "solution": r'''
            def rerank(docs, query):
                terms = set(query.lower().split())

                def score(doc):
                    return len(terms & set(doc.lower().split()))

                scored = map(lambda d: (score(d), d), docs)
                kept = filter(lambda pair: pair[0] > 0, scored)
                ordered = sorted(kept, key=lambda pair: (-pair[0], len(pair[1])))
                return [doc for _, doc in ordered]
        ''',
    },
]
