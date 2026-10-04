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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["sort", "sorted", "order", "key", "lambda", "reverse", "ascending", "descending",
                 "min", "max", "map", "filter", "itemgetter", "stable", "tie", "top-k"],
    "cards": [
        {
            "syntax": "sorted(items, reverse=True)",
            "explain": "Returns a new sorted list and leaves items unchanged. Without reverse=True, the smallest item is first.",
            "example": r'''
                scores = [0.7, 0.9, 0.2]
                print(sorted(scores))
                # [0.2, 0.7, 0.9]
                print(sorted(scores, reverse=True))
                # [0.9, 0.7, 0.2]
                print(scores)
                # [0.7, 0.9, 0.2]
            ''',
        },
        {
            "syntax": "items.sort()",
            "explain": "Sorts the list itself and returns None. It accepts key= and reverse= in the same way as sorted().",
            "example": r'''
                queue = [3, 1, 2]
                answer = queue.sort()
                print(queue)
                # [1, 2, 3]
                print(answer)
                # None
            ''',
        },
        {
            "syntax": "sorted(items, key=function)",
            "explain": "Calls function on every item and orders the items by the returned values. Pass the name, with no ().",
            "example": r'''
                words = ["ccc", "a", "bb"]
                print(sorted(words, key=len))
                # ['a', 'bb', 'ccc']
                print(sorted(["bob", "Al"], key=str.lower))
                # ['Al', 'bob']
            ''',
        },
        {
            "syntax": "lambda item: expression",
            "explain": "A function with no name, written as one expression. Its return value is the value of the expression.",
            "example": r'''
                models = [{"name": "big", "price": 5.0},
                          {"name": "tiny", "price": 0.2}]
                ordered = sorted(models, key=lambda m: m["price"])
                print(ordered[0]["name"])
                # tiny
            ''',
        },
        {
            "syntax": 'key=lambda r: (-r["score"], r["id"])',
            "explain": "A tuple key sorts by several rules: first part first, later parts for ties. A minus sign reverses a number.",
            "example": r'''
                results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9},
                           {"id": "b", "score": 0.7}]
                best = sorted(results, key=lambda r: (-r["score"], r["id"]))
                print([r["id"] for r in best])
                # ['a', 'b', 'c']
            ''',
        },
        {
            "syntax": "max(items, key=function, default=None)",
            "explain": "Returns the whole item with the largest key value, or default for an empty list. min works the same way.",
            "example": r'''
                words = ["ab", "abcd", "abc"]
                print(max(words, key=len))
                # abcd
                print(min(words, key=len))
                # ab
                print(max([], key=len, default=None))
                # None
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: sorting, keys and lambdas

### `sorted()` and `.sort()`

`sorted(items)` returns a new list with the items in **ascending** order: smallest first. The
original list is not changed. `items.sort()` reorders the list itself and returns `None`. Both
accept `reverse=True`, which gives **descending** order: largest first.

```python
scores = [0.7, 0.9, 0.2]
print(sorted(scores))
# [0.2, 0.7, 0.9]
print(scores)
# [0.7, 0.9, 0.2]
scores.sort(reverse=True)
print(scores)
# [0.9, 0.7, 0.2]
```

### Key functions and lambdas

A **key function** takes one item and returns the value that Python compares. You pass it as
`key=`. A **lambda** is a function written as one expression, with no name:
`lambda r: r["score"]` takes `r` and returns `r["score"]`.

```python
results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9}, {"id": "b", "score": 0.7}]
ordered = sorted(results, key=lambda r: r["score"])
print([r["id"] for r in ordered])
# ['c', 'b', 'a']
```

Step through the stages to see the data that `sorted()` works with at each one.

```diagram
{"type":"flow","title":"How sorted(results, key=...) works","steps":[
{"label":"Input list","detail":"sorted() receives the list and the key function. It does not change this list.","code":"results = [\n  {'id': 'c', 'score': 0.7},\n  {'id': 'a', 'score': 0.9},\n  {'id': 'b', 'score': 0.7},\n]\nkey = lambda r: r['score']"},
{"label":"Call key on each item","detail":"Python calls the key function once for every item, in list order. Each call returns one key value.","code":"key({'id': 'c', 'score': 0.7})  returns 0.7\nkey({'id': 'a', 'score': 0.9})  returns 0.9\nkey({'id': 'b', 'score': 0.7})  returns 0.7"},
{"label":"Compare the key values","detail":"Python compares the key values with <, not the dicts. 0.7 is less than 0.9, so 'c' and 'b' go before 'a'. The two 0.7 values are equal, so 'c' and 'b' keep their original order.","code":"0.7 ('c')\n0.7 ('b')\n0.9 ('a')"},
{"label":"Return the items","detail":"sorted() returns a new list that holds the original items in that order. The key values are discarded.","code":"[\n  {'id': 'c', 'score': 0.7},\n  {'id': 'b', 'score': 0.7},\n  {'id': 'a', 'score': 0.9},\n]"}
]}
```

### Tuple keys

A key can return a tuple. Python compares the first parts, and compares the next parts only when
the first parts are equal. A minus sign in front of a number reverses the order of that part.

```python
results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9}, {"id": "b", "score": 0.7}]
best = sorted(results, key=lambda r: (-r["score"], r["id"]))
print([r["id"] for r in best])
# ['a', 'b', 'c']
```

### Stable sort

Python's sort is **stable**: items with equal keys keep their original order. A minus sign
does not work on a string, so a tuple key cannot put a string part in descending order. Sort
twice instead. Sort by the least important rule first, then by the more important rules.

### `min()` and `max()` with a key

`min` and `max` accept the same `key=`. They return the whole item, not the key value.
`default=` is the value they return for an empty list.

```python
results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9}, {"id": "b", "score": 0.7}]
print(max(results, key=lambda r: r["score"])["id"])
# a
print(max([], default=None))
# None
```

### `map`, `filter` and `itemgetter`

`map(f, items)` calls `f` on each item. `filter(f, items)` keeps the items for which `f` returns
a truthy value (a value that counts as `True` in a condition). Both produce their results one at a time, so pass them to `list()` to get a list.
`operator` is a standard library module, and `from operator import itemgetter` loads only
`itemgetter` from it. `operator.itemgetter("score", "id")` returns a key
function that takes one item and returns `(item["score"], item["id"])`.

```python
from operator import itemgetter

scores = [0.7, 0.9, 0.2]
print(list(map(lambda s: s * 10, scores)))
# [7.0, 9.0, 2.0]
print(list(filter(lambda s: s > 0.5, scores)))
# [0.7, 0.9]
results = [{"id": "c", "score": 0.7}, {"id": "a", "score": 0.9}, {"id": "b", "score": 0.7}]
print(sorted(results, key=itemgetter("score", "id"))[0])
# {'id': 'b', 'score': 0.7}
```

### Common mistakes

- `items = items.sort()` stores `None` in `items`, because `.sort()` returns `None`.
- `key=len()` calls `len` with no argument and raises `TypeError`. Write `key=len`.
- `reverse=True` reverses every part of a tuple key, not one part.
- `max([])` raises `ValueError`. Pass `default=` to get a value back.
- `print(map(len, words))` prints `<map object at 0x...>`. Write `list(map(len, words))`.
'''


EXERCISES = [
    {
        "id": "sorting-s1",
        "lesson": r'''
            ## Smallest first, or largest first

            A search tool hands you ten results, each with a score. A price list holds every model you
            could call. Before you show either one to a person, you have to decide what comes first. This
            chapter is about putting things in order: numbers, words, and later whole records such as a
            model together with its price.

            You met the basic tool in the Lists chapter. Here it is again:

            ```python
            prices = [5.0, 0.5, 2.0]
            cheap_first = sorted(prices)
            print(cheap_first)
            # [0.5, 2.0, 5.0]
            print(prices)
            # [5.0, 0.5, 2.0]
            ```

            `sorted(prices)` builds a new list with the same items, arranged from the smallest to the
            largest, and returns it. The last line shows that `prices` still has its old order. `sorted`
            only reads the list you give it.

            Smallest-to-largest has a name: **ascending** order, because the values climb as you read
            along the list.

            ```quiz
            After these two lines, what does `print(waits)` show?

            ~~~python
            waits = [340, 120, 560]
            fastest_first = sorted(waits)
            ~~~
            - [x] `[340, 120, 560]` :: Right. `sorted` built a second list, and that list is stored under `fastest_first`. `waits` was only read.
            - [ ] `[120, 340, 560]` :: That is what `fastest_first` holds. `sorted` does not reorder the list it is given.
            - [ ] `None` :: `None` is what the list method `waits.sort()` returns. Here nothing was assigned to `waits` a second time, so it still names the original list.
            ```

            ### Text, and the other direction

            Strings can be sorted too. Python puts them in alphabetical order:

            ```python
            names = ["llama", "claude", "gemini"]
            print(sorted(names))
            # ['claude', 'gemini', 'llama']
            print(sorted(names, reverse=True))
            # ['llama', 'gemini', 'claude']
            ```

            The second call adds the keyword argument `reverse=True`, which turns the order around. The
            largest number, or the word that is last in the alphabet, now comes first. That is called
            **descending** order.

            Pick the argument that makes this program print the highest score first:

            ```fill
            scores = [0.4, 0.9, 0.7]
            print(sorted(scores, ___))
            ---
            - [x] reverse=True :: Right. The program prints `[0.9, 0.7, 0.4]`.
            - [ ] True :: Without its name, Python cannot tell which setting you mean. It stops with `TypeError: sorted expected 1 argument, got 2`.
            - [ ] reverse=true :: Python's value is `True`, with a capital T. The lowercase word is read as a name that nobody has defined, so Python stops with `NameError: name 'true' is not defined. Did you mean: 'True'?`.
            ```

            **Watch out:** `sorted(prices)` on a line of its own does nothing that you can see. It builds
            the ordered list, nothing stores it, and the list is thrown away. No error warns you. Store
            the result under a name, or use it straight away.

            **In short:** `sorted(items)` returns a new list in ascending order, `reverse=True` makes it
            descending, and `items` stays as it was.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
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
            `sorted(nums)` builds a new list in ascending order, so the first line is `[1, 2, 3]`. It did
            not change `nums`, so the second line shows the original order, `[3, 1, 2]`. The last call
            adds `reverse=True`, which gives descending order: `[3, 2, 1]`. Python prints a list with
            square brackets, and with a comma and a space between the items.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Go through the three `print` lines one at a time. For each one, ask which list is being printed: a new one, or the original?",
            "`sorted` returns a new list and leaves `nums` alone. Without `reverse=True` the smallest number comes first, and with it the largest comes first.",
            "Your first line is the numbers from the smallest to the largest. Your second line is `nums` exactly as the program created it. Your third line is the numbers from the largest to the smallest. Write each line the way Python prints a list: square brackets, and a comma and a space between the items.",
        ],
    },
    {
        "id": "sorting-s2",
        "lesson": r'''
            ## Telling sorted what to compare

            A model gives every customer review a mood score between -1 and 1. A score of -0.9 means very
            unhappy, 0.6 means quite happy, and a score near 0 means the review has hardly any mood at
            all. You want the mildest reviews first and the strongest feelings last, whichever way they
            point.

            `sorted` on its own cannot do that. It compares the numbers themselves, so -0.9 comes first:

            ```python
            moods = [-0.9, 0.2, -0.1, 0.6]
            print(sorted(moods))
            # [-0.9, -0.1, 0.2, 0.6]
            ```

            What you want to compare is how far each score is from zero. So write a function that works
            that out for one score, and hand the function to `sorted`:

            ```python
            def strength(score):
                return abs(score)

            moods = [-0.9, 0.2, -0.1, 0.6]
            print(sorted(moods, key=strength))
            # [-0.1, 0.2, 0.6, -0.9]
            ```

            The built-in `abs` drops the minus sign of a number, so `abs(-0.9)` is `0.9`. `sorted` calls
            `strength` once for every item and gets 0.9, 0.2, 0.1 and 0.6. Then it arranges the items in
            the order of those answers. The new list still holds the original scores. The answers were
            only used to decide which item goes where.

            A function that is used this way is called a **key function**, and `key=` is the keyword
            argument that takes it.

            Here is the same idea with temperatures. Step through the program and watch line 2 run once
            for every item:

            ```diagram
            {"type": "trace", "title": "sorted() calls distance once per item", "code": ["def distance(n):", "    return abs(n)", "", "temps = [-5, 2, -1, 4]", "ordered = sorted(temps, key=distance)", "print(ordered)", "print(temps)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 4, "vars": {}, "out": ""},
              {"line": 5, "vars": {"temps": "[-5, 2, -1, 4]"}, "out": ""},
              {"line": 2, "vars": {"n": "-5"}, "out": ""},
              {"line": 2, "vars": {"n": "2"}, "out": ""},
              {"line": 2, "vars": {"n": "-1"}, "out": ""},
              {"line": 2, "vars": {"n": "4"}, "out": ""},
              {"line": 6, "vars": {"temps": "[-5, 2, -1, 4]", "ordered": "[-1, 2, 4, -5]"}, "out": ""},
              {"line": 7, "vars": {"temps": "[-5, 2, -1, 4]", "ordered": "[-1, 2, 4, -5]"}, "out": "[-1, 2, 4, -5]\n"},
              {"line": null, "vars": {"temps": "[-5, 2, -1, 4]", "ordered": "[-1, 2, 4, -5]"}, "out": "[-1, 2, 4, -5]\n[-5, 2, -1, 4]\n"}
            ]}
            ```

            A key function can look at any part of an item:

            ```predict
            def last_letter(word):
                return word[-1]

            names = ["gemini", "claude", "llama"]
            print(sorted(names, key=last_letter))
            print(names)
            ---
            The key function gives `"i"` for gemini, `"e"` for claude and `"a"` for llama. In alphabetical order those answers are a, e, i, so the names come out as llama, claude, gemini. `names` is unchanged, because `sorted` builds a new list.
            ```

            ### No brackets after the name

            Look at `key=strength` once more. There are no brackets after `strength`. With brackets you
            would call the function yourself, right there on that line. Without them you hand over the
            function itself, and `sorted` does the calling, one item at a time.

            A built-in function can be a key function too. `strength` does nothing except call `abs`, so
            you can pass `abs` directly:

            ```python
            moods = [-0.9, 0.2, -0.1, 0.6]
            print(sorted(moods, key=abs))
            # [-0.1, 0.2, 0.6, -0.9]
            ```

            ```quiz
            `temps` is `[-5, 2, -1, 4]`. Which call sorts it by distance from zero?
            - [x] `sorted(temps, key=abs)` :: Right. `sorted` receives the function `abs` and calls it on each number.
            - [ ] `sorted(temps, key=abs())` :: The brackets call `abs` straight away, with nothing inside them. Python stops with `TypeError: abs() takes exactly one argument (0 given)` before `sorted` has started.
            - [ ] `sorted(temps, abs)` :: The function has to be passed by name, as `key=`. Without the name, Python stops with `TypeError: sorted expected 1 argument, got 2`.
            - [ ] `sorted(abs(temps))` :: This calls `abs` once on the whole list, not on each number. Python stops with `TypeError: bad operand type for abs(): 'list'`.
            ```

            **Watch out:** `key=` wants a function, not the result of calling one. When an error on a line
            with `key=` says `takes exactly one argument (0 given)`, look for a pair of brackets that
            should not be there.

            **In short:** `sorted(items, key=f)` calls `f` on every item and orders the items by what `f`
            returns.
        ''',
        "title": "Sort by length",
        "difficulty": 0,
        "prompt": r'''
            A search box suggests words while you type, and the short words should come first because they
            are the quickest to read. Later in this course the same ordering is used for pieces of text of
            different sizes.

            **Your job:** finish `by_length(words)` so that it gives back the words ordered from the
            shortest to the longest. The function is already written except for one gap, marked `___`.
            Replace the gap.

            **What goes in**
            - `words`: a list of strings, for example `["ccc", "a", "bb"]`. It may be empty.

            **What comes out**
            - a new list with the same words, the shortest first, for example `["a", "bb", "ccc"]`

            **Rules**
            - Only the number of characters decides the order. The alphabet plays no part: `"zz"` comes
              before `"aaa"`, because it is shorter.
            - An empty list gives `[]`.

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
            "The gap is where the key function goes. What does `sorted` have to find out about each word before it can compare two of them?",
            "You do not have to write a function of your own. A built-in that you have used since the first chapter already gives the number of characters in a string.",
            "Put the name of that built-in in the gap, and nothing else. Leave out the brackets, because `sorted` does the calling.",
        ],
    },
    {
        "id": "sorting-s3",
        "lesson": r'''
            ## Reordering the list you already have

            `sorted` gives you a second list. Sometimes a second list is not what you want. You have a
            queue of waiting times, nobody needs the old order, and the queue itself should be put in
            order.

            Lists have a method for that. You met it briefly in the Lists chapter:

            ```python
            waits = [340, 120, 560]
            waits.sort()
            print(waits)
            # [120, 340, 560]
            ```

            `waits.sort()` moves the items around inside the list that is already there. You know the
            phrase for that from `append`: the method changes the list **in place**. It accepts the same
            settings as `sorted`, so `waits.sort(reverse=True)` and `waits.sort(key=abs)` both work.

            So what does `sort` return? Make a guess, then find out:

            ```predict
            waits = [340, 120, 560]
            result = waits.sort(reverse=True)
            print(waits)
            print(result)
            ---
            `sort` did its work on `waits`, which is now in descending order. Like `append`, it returns nothing, and Python's value for "nothing" is `None`. So `result` is `None`.
            ```

            That `None` is behind a very common bug. Someone stores the result of `.sort()` under a name,
            or returns it from a function, and finds `None` where they expected a list.

            ### Inside a function

            There is a second thing to know before you use `.sort()` inside a function. A parameter is
            another name for the caller's list, not a copy of it. Sorting the parameter in place therefore
            reorders the caller's list:

            ```python
            def slowest(waits):
                waits.sort()
                return waits[-1]

            mine = [340, 120, 560]
            print(slowest(mine))
            # 560
            print(mine)
            # [120, 340, 560]
            ```

            The caller asked one question and had their list rearranged as well. Repair that function:

            ```try
            def slowest(waits):
                waits.sort()
                return waits[-1]

            mine = [340, 120, 560]
            print(slowest(mine))
            print(mine)
            ---
            The second line printed is `[120, 340, 560]`: the caller's list was reordered. Change the body
            of the function so that the program prints `560` and then `[340, 120, 560]`.
            ---
            def slowest(waits):
                ordered = sorted(waits)
                return ordered[-1]

            mine = [340, 120, 560]
            print(slowest(mine))
            print(mine)
            ---
            A new list from `sorted` gave the function everything it needed, and the caller's list was only read.
            ```

            **Watch out:** when a check says that your function returned `None`, look for a `.sort()`
            whose result is being stored or returned.

            **In short:** `items.sort()` reorders `items` itself and returns `None`, and `sorted(items)`
            returns a new list and leaves `items` alone.
        ''',
        "title": "Fix the bug: newest first",
        "difficulty": 0,
        "prompt": r'''
            An activity feed shows the most recent events first. Every event has a timestamp, a number
            that grows as time passes, so a bigger number means a newer event. Someone wrote a function
            that should give back the timestamps from the newest to the oldest. It has a bug: whatever
            list you pass in, it gives back `None`.

            **Your job:** fix `newest_first(timestamps)` so that it gives back a new list with the same
            numbers, ordered from the biggest to the smallest. The code is already in the editor.

            **What goes in**
            - `timestamps`: a list of numbers, for example `[10, 30, 20]`. It may be empty.

            **What comes out**
            - a new list with the same numbers, the biggest first, for example `[30, 20, 10]`

            **Rules**
            - The list that was passed in must not change. After the call it still holds its numbers in
              their original order, because the code that called your function may still need them that
              way. A fix that gets rid of the `None` but reorders the caller's list fails a check.
            - An empty list gives `[]`.

            **Examples**
            ```python
            newest_first([10, 30, 20])   # returns [30, 20, 10]
            newest_first([5])            # returns [5]
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
            "What does the list method `sort` return? The predict box in the lesson shows it.",
            "The method does its work on the list it is called on, which here is the caller's list, and it returns nothing. You need the tool that builds a new list in order and leaves the original alone.",
            "Replace the method call with a call to the built-in function that returns a new sorted list. Give it the timestamps, keep the setting that puts the biggest number first, and return what it gives you.",
        ],
    },
    {
        "id": "sorting-s4",
        "lesson": r'''
            ## Tell a sort which field matters

            A list of document records contains names, sizes, and dates. You want the smallest size first, but comparing entire dictionaries does not tell Python that. Give the sort a small function that extracts the comparison value from one record.

            ```python
            records = [{"name": "guide", "pages": 12}, {"name": "note", "pages": 2}]
            ordered = sorted(records, key=lambda record: record["pages"])
            print([record["name"] for record in ordered])
            # ['note', 'guide']
            ```

            The expression after `key=` is a **lambda**, a small function written without a separate `def` statement. Its parameter receives one item, and the expression after the colon supplies the returned comparison value. The result still contains the original records, not just those values.

            ```predict
            triple = lambda number: number * 3
            print(triple(5))
            ---
            The lambda receives five and evaluates its expression, returning fifteen without needing a return statement.
            ```

            Use a lambda when the job is one short expression. A named function is often clearer when extracting the key requires several steps. Both forms give sorting the same kind of tool: a function to call for each input item.

            ```quiz
            What does reverse=True change in a sort with a key?
            - [x] The direction of comparison, putting larger keys first. :: The items remain whole; their ordering changes.
            - [ ] It reverses the characters inside every string. :: Sorting rearranges items rather than editing their contents.
            ```

            **Watch out:** a lambda uses its expression as its answer. Writing a return statement inside it causes a syntax error. Use def when you need statements.

            Extract a comparison key while keeping the original records as the sorted result.
        ''',
        "title": "Best results first",
        "difficulty": 0,
        "prompt": r'''
            Search results should be shown best match first. Each result is a dict like
            `{"id": "doc1", "score": 0.8}`.

            **Your job:** write `by_score(results)`

            **What goes in**
            - `results`: a list of dicts, each with an `"id"` (str) and a `"score"` (float)

            **What comes out**
            - a **new** list of the same dicts, sorted by `"score"`, highest first

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
            "A sort key receives one complete result and supplies its comparison value.",
            "Use the score for comparison and choose descending order without changing the supplied list.",
            "Return a copying sort, giving it a lambda that extracts the score and the option for highest values first.",
        ],
    },
    {
        "id": "sorting-s5",
        "lesson": r'''
            ## Pick one record by its comparison value

            You need the document with the most pages, not a complete ordering of the whole collection. Selecting one winner directly expresses that intention. Python's minimum and maximum functions accept the same key idea as sorting.

            ```python
            records = [{"name": "guide", "pages": 12}, {"name": "note", "pages": 2}]
            winner = max(records, key=lambda record: record["pages"])
            print(winner)
            # {'name': 'guide', 'pages': 12}
            print(winner["name"])
            # guide
            ```

            The key tells `max` which values to compare, but the returned answer is the entire winning item. You can then read whichever field the caller actually needs. `min` behaves the same way when you want the smallest comparison value instead.

            ```predict
            words = ["a", "longest", "mid"]
            print(max(words, key=len))
            print(min(words, key=len))
            ---
            The comparison uses lengths, but the returned values are the original strings: longest and a.
            ```

            An empty collection has no winner. Either check for it before selecting or pass the built-in's `default` argument. That default applies only when no items exist; it does not replace a real winner whose value happens to be zero or an empty string.

            ```fill
            print(repr(max([], default=___)))
            ---
            - [x] None :: This represents the absence of a winning item.
            - [ ] 0 :: This would report a number instead of the requested absent value.
            - [ ] "None" :: This is text, not Python's absent-value object.
            ```

            **Watch out:** `min([])` and `max([])` raise `ValueError` without a default. Also distinguish the selected item from the numeric key used to select it.

            Choose the winning item first, then extract the part promised to the caller.
        ''',
        "title": "Cheapest model",
        "difficulty": 0,
        "prompt": r'''
            Pick the cheapest model from a price list. Each model is a dict like
            `{"name": "gpt-4o", "price": 5.0}`.

            **Your job:** write `cheapest(models)`

            **What goes in**
            - `models`: a list of dicts, each with a `"name"` (str) and a `"price"` (float)

            **What comes out**
            - the **name** (a string, not the whole dict) of the model with the
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
            "The selection returns a whole model record before you choose the output field.",
            "Handle no available model separately, then compare models by price.",
            "Use the required minimum operation with a price key, then give back the selected record's name rather than its price or the entire record.",
        ],
    },
    {
        "id": "sorting-s6",
        "lesson": r'''
            ## Break a tie with a second rule

            A queue should group jobs by priority, then order equal-priority jobs by name. One comparison value is not enough to express both rules. Return an ordered pair of comparison values and let Python compare them in sequence.

            ```python
            jobs = [("write", 2), ("check", 1), ("build", 2)]
            print(sorted(jobs, key=lambda job: (job[1], job[0])))
            # [('check', 1), ('build', 2), ('write', 2)]
            ```

            Python compares tuples from left to right. The first unequal part decides the order; later parts matter only when earlier parts tie. This is a **tuple key**. Here the numeric priority dominates, and the name breaks ties between equal priorities.

            ```predict
            print((3, "a") < (2, "z"))
            print((2, "a") < (2, "z"))
            ---
            The first comparison is False because three exceeds two. The second is True because equal first parts make the names decide.
            ```

            Sometimes only the numeric rule should run backwards. Negating that number in the key makes larger original numbers produce smaller keys. Leave the text part unchanged to keep its normal alphabetical direction.

            ```python
            jobs = [("write", 2), ("check", 1), ("build", 2)]
            print(sorted(jobs, key=lambda job: (-job[1], job[0])))
            # [('build', 2), ('write', 2), ('check', 1)]
            ```

            ```quiz
            Would reverse=True reverse only the first part of a tuple key?
            - [x] No; it reverses the whole comparison order. :: Tied numeric values would also use the opposite name ordering.
            - [ ] Yes; later tuple parts ignore reverse. :: Reverse applies to the complete key comparison.
            ```

            **Watch out:** the key changes how items are compared, not the original tuple contents. The output still contains the original positive numbers.

            List comparison rules from most important to least important in the key.
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
            The first key puts the numeric value first and the name second. The smallest number therefore leads, and names decide the tied larger values alphabetically. The second key negates only the number, moving larger original numbers ahead while preserving the same alphabetical rule within a tie. The key controls comparison; Python still prints the original pairs.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Tuple comparisons follow the key parts from left to right.",
            "The names matter only for equal numeric keys, and negation changes only the numeric priority.",
            "Determine each key order, keep the original pairs as output items, and format both resulting lists exactly as Python prints them.",
        ],
    },
    {
        "id": "sorting-1",
        "lesson": r'''
            ## Decide whether the original list should change

            One screen needs a ranked view of scores, while another still needs their arrival order. Changing the shared list to create the first view would surprise the second screen. Choose a copying or changing operation according to the function's promise.

            ```python
            arrival = [8, 2, 5]
            ordered = sorted(arrival)
            print(arrival)
            # [8, 2, 5]
            print(ordered)
            # [2, 5, 8]
            ```

            `sorted` builds a new list, leaving the supplied list in its original order. The list method `sort` instead rearranges the list itself. Changing an existing object is called **mutation**; a caller holding that object sees the change too.

            ```predict
            values = [8, 2, 5]
            result = values.sort()
            print(values)
            print(result)
            ---
            The original list is now ordered, while the method's return value is None.
            ```

            The return value and the changed object are two different results of a call. Python's mutating list methods usually return None to make that distinction clear. A helper that only calls such a method can finish without an explicit return; it also returns None.

            ```quiz
            A caller passes a list into a function. Does Python automatically copy it first?
            - [x] No; the function receives that same list object. :: Mutating it is visible to the caller.
            - [ ] Yes; every argument is copied. :: Passing an argument does not automatically duplicate its data.
            ```

            A sorted copy is a new outer list, but it still contains the same item objects. This preserves input order without promising deep copies of nested records. Keep the contract precise about which kind of independence is required.

            **Watch out:** returning the result of the sort method returns None, not the ordered list. Use the operation that matches the promised return behavior.

            Choose whether to return a new ordering or change the existing list before implementing the sort.
        ''',
        "title": "Copy or in place",
        "hints": [
            "Decide which helper promises a new list and which promises a visible change.",
            "Use copying behavior for the descending result and mutation for the ascending operation.",
            "Have the first helper give back a new ordered list; have the second rearrange the supplied list and finish with no list return value.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Two ways to order a list of relevance scores: make a sorted **copy**, or sort the
            original list **in place** (change the list itself).

            **Your job:** write `ranked(scores)` and `sort_in_place(scores)`

            **What goes in**
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
            ## Preserve the order of equal items

            Two search results have equal scores. Their original order may already express a useful preference, such as arrival order. You can sort by the intended key alone and let equal-key items keep their earlier relationship.

            ```python
            words = ["zz", "a", "bb", "c"]
            print(sorted(words, key=len))
            # ['a', 'c', 'zz', 'bb']
            ```

            The two one-character strings retain their order, and so do the two two-character strings. This property is **stability**: items with equal comparison keys stay in their original relative order. Both `sorted` and the list's `sort` method provide it.

            ```predict
            words = ["zz", "bb", "a"]
            print(max(words, key=len))
            print(min(words, key=len))
            ---
            The maximum is zz because it is the first of the two longest strings. The minimum is a.
            ```

            Minimum and maximum selection also choose the first item when several share the winning key. This lets you satisfy a first-on-ties contract without building a separate tie-breaking rule. Adding the word itself to the key would change the contract by making alphabetic order decide ties.

            ```quiz
            A task says equal-length strings keep input order. Should you add the string as a second key?
            - [x] No; that would introduce an alphabetical tie-breaker. :: Length alone plus stability preserves the required order.
            - [ ] Yes; every sort needs a unique key. :: Equal keys are valid, and Python handles them stably.
            ```

            For empty input, a sort returns an empty list naturally. A maximum needs an explicit fallback or a preceding empty check because there is no item to select.

            **Watch out:** sorting text without a key compares the text itself, not its length. A plausible-looking order can still answer the wrong question.

            Use only the promised comparison rules and let stability preserve full ties.
        ''',
        "title": "Shortest and longest chunks",
        "hints": [
            "Length is the only ranking rule; equal lengths retain input order.",
            "Use the length function as the key for both ordering and selecting.",
            "Create the sorted view, then implement maximum selection with its empty fallback; do not add an alphabetical tie-breaker.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A RAG pipeline splits documents into text chunks. Order them by size and find the
            biggest one.

            **Your job:** write `by_length(chunks)` and `longest(chunks)`

            **What goes in**
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
            ## Translate a display policy into an ordered key

            A task list should group work by team and put shorter jobs first inside each team. A short job from a later team must not jump ahead of every job from an earlier team. Write the policy in priority order before writing the key.

            ```python
            tasks = [{"name": "ship", "team": "ops", "hours": 1},
                     {"name": "review", "team": "dev", "hours": 4},
                     {"name": "edit", "team": "dev", "hours": 2}]
            ordered = sorted(tasks, key=lambda task: (task["team"], task["hours"]))
            print([task["name"] for task in ordered])
            # ['edit', 'review', 'ship']
            ```

            Team is the primary rule because it is first in the tuple. Hours decide only within a shared team. This is the same tuple comparison you predicted earlier, now applied to fields in dictionaries rather than positions in pairs.

            ```quiz
            Why is the one-hour ops job last?
            - [x] The team rule is more important than the hours rule. :: Dev comes before ops regardless of the hours in different teams.
            - [ ] Tuple keys add their parts together. :: They compare parts in order instead of combining them arithmetically.
            ```

            After sorting, you may need only a list of names for display. Keep sorting and selecting output fields as separate steps: the sort needs records with all comparison fields, while the caller may want a simpler result.

            ```predict
            items = [{"name": "z", "group": 1}, {"name": "a", "group": 1}]
            print([item["name"] for item in sorted(items, key=lambda item: item["group"])])
            ---
            Both keys are equal, so stability keeps z before a. No alphabetical rule was requested.
            ```

            The linked Sorting HOWTO gives further examples of these priorities. Read the explanation of key functions and stability while the concrete example is fresh.

            **Watch out:** sorting names before extracting their associated fields loses the information needed for the primary rule.

            Order complete records by the policy, then return the requested fields.
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

            **Your job:** write `catalog_order(models)`

            **What goes in**
            - `models`: a list of dicts `{"name": str, "provider": str, "price": float}`,
              e.g. `{"name": "haiku", "provider": "anthropic", "price": 0.8}`

            **What comes out**
            - a **new** list of the model **names** (strings) in display order

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
            "Translate the two priorities into a tuple with the most important field first.",
            "Sort the records before reducing them to display names.",
            "Use a copying sort on provider then price, rely on stability for complete ties, and collect the names from the ordered records.",
        ],
    },
    {
        "id": "sorting-8",
        "lesson": r'''
            ## Keep some items, then transform each survivor

            A document-processing step must discard unusable entries and measure the rest. You already expressed that with a comprehension. Other codebases may spell the same two responsibilities with functions named map and filter, so it helps to read those forms too.

            ```python
            words = ["map", "", "  ", " note "]
            kept = filter(lambda word: word.strip(), words)
            uppercased = map(str.upper, kept)
            print(list(uppercased))
            # ['MAP', ' NOTE ']
            ```

            `filter` calls a function to decide which original items stay. `map` calls a function to produce a new value from every kept item. Neither builds the complete output list immediately: they are **lazy**, supplying values as another operation asks for them. `list` requests and collects all those results.

            ```match
            filter :: decide which original items survive
            map :: calculate one result for each incoming item
            list :: collect the produced values into a list
            ```

            Notice that using `strip` as the filter test does not trim the retained original string. The last entry still has its spaces when passed to the uppercase operation. Choosing what survives and choosing how to transform it remain separate decisions.

            ```predict
            words = ["a", "long"]
            lengths = map(len, words)
            print(list(lengths))
            print(list(lengths))
            ---
            The first list call consumes both lengths. The same map object has no remaining values for the second call.
            ```

            Pass the function itself to map, not the result of calling it without an item. Map supplies each item when it needs a result. The same rule applies to the function passed into filter.

            **Watch out:** returning a map object does not satisfy a promise to return a list. Collect its values explicitly when the output contract requires that concrete container.

            Filter chooses survivors; map transforms them; list collects the answers.
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

            **Your job:** write `chunk_lengths(chunks)`

            **What goes in**
            - `chunks`: a list of strings, e.g. `["hello", "", "  ", "ab c"]`

            **What comes out**
            - a list of ints - the length (`len`) of each **non-blank** chunk, in
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
            "The blank test and the length measurement use the input for different purposes.",
            "Keep original nonblank chunks with filter, then measure those unchanged values with map.",
            "Use a trimming-based filter condition, map the length function over its survivors, and collect the produced lengths into a real list.",
        ],
    },
    {
        "id": "sorting-3",
        "title": "Top-k results",
        "hints": [
            "Descending scores and ascending identifiers require separate directions within the key.",
            "Handle nonpositive limits before taking a prefix of the ranked results.",
            "Sort a copy by score priority and alphabetical tie-break, keep at most the requested count, and extract only the identifiers.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A vector search returns many results; a RAG app keeps only the best `k` of them
            (this is called *top-k*).

            **Your job:** write `top_k(results, k)`

            **What goes in**
            - `results`: a list of dicts `{"id": str, "score": float}`
            - `k`: an int, how many results to keep, e.g. `3`

            **What comes out**
            - a list of the **ids** (strings) of the `k` best results, best first

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
            ## Put pair fields into comparison order

            You have named measurements in a dictionary and want a ranked table. Its items are pairs with the name first and the measurement second, but the measurement should decide the order. A small standard-library helper can select pair positions for your key.

            ```python
            from operator import itemgetter
            measurements = [("north", 7), ("west", 3), ("east", 3)]
            pick = itemgetter(1, 0)
            print(pick(("north", 7)))
            # (7, 'north')
            print(sorted(measurements, key=pick))
            # [('east', 3), ('west', 3), ('north', 7)]
            ```

            `itemgetter` builds a function that reads the requested items. With several positions, that function returns a tuple in the supplied order. This combines field extraction with the tuple-key rules from earlier steps: measurement first, name only when measurements tie.

            ```fill
            from operator import itemgetter
            pick = itemgetter(___)
            print(pick(("north", 7)))
            ---
            - [x] 1 :: Position one holds the measurement, seven.
            - [ ] 0 :: Position zero holds the name instead.
            - [ ] 2 :: The pair has no position two, so the lookup fails.
            ```

            When planning the practice task, distinguish the full ranked table from selecting a single best name. A dictionary's items provide pairs; iterating the dictionary itself provides keys. Decide which kind of item the key function will receive before choosing how to read the measurement.

            ```quiz
            Does passing itemgetter into sorted replace each original pair with its key?
            - [x] No; keys control comparison while original items remain in the result. :: The displayed pair order stays name then measurement.
            - [ ] Yes; the result always contains only comparison tuples. :: Extraction for comparison does not transform output items.
            ```

            **Watch out:** an empty mapping has no smallest item to select. Plan the task's fallback independently from the ordering logic.

            Choose the incoming item shape, then extract comparison fields in priority order.
        ''',
        "title": "Rank models by latency",
        "hints": [
            "Dictionary items supply name-measurement pairs, while iterating keys supplies names.",
            "For the table, extract the numeric position before the name position in the key.",
            "Use itemgetter for ranking pairs, use minimum selection with both latency and name priorities for the winner, and handle empty mappings for both outputs.",
        ],
        "difficulty": 2,
        "prompt": r'''
            Compare LLMs by speed using a dict of measured latencies.

            **Your job:** write `rank_models(latencies)` and `fastest(latencies)`

            **What goes in**
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
            ## Combine opposite text ordering directions

            A report groups people by team from A to Z, but lists names within each team from Z to A. Negating a number can reverse one numeric key; it cannot reverse text. Use the stable-sort behavior from earlier steps to combine the two policies.

            ```python
            people = [("Ana", "red"), ("Zed", "red"), ("Bo", "blue")]
            by_name = sorted(people, key=lambda person: person[0], reverse=True)
            result = sorted(by_name, key=lambda person: person[1])
            print(result)
            # [('Bo', 'blue'), ('Zed', 'red'), ('Ana', 'red')]
            ```

            The first pass establishes the less important name order. The second pass groups by the more important team rule. Because that second sort is stable, names with equal team keys keep the order established by the first pass. This is **multi-pass sorting**.

            ```quiz
            Which rule should be applied first in separate stable sorting passes?
            - [x] The least important rule. :: Later passes establish higher-priority groups while preserving lower-priority order within ties.
            - [ ] The most important rule. :: A later sort on another key could rearrange those primary groups.
            ```

            For the practice task, write all priorities in order before choosing the passes. A final pass may use a tuple for several compatible rules. Numeric keys can still be negated to reverse only their direction, while a separate text pass handles descending alphabetical order.

            ```predict
            records = [("z", 2), ("a", 2), ("m", 1)]
            print(sorted(records, key=lambda record: record[1]))
            ---
            The smaller numeric key comes first. The tied pair retains z before a because the sort is stable.
            ```

            Keep using copying sorts when the original list must remain unchanged. Each pass should operate on the preceding pass's result, not restart from the unsorted input and discard the ordering you just established.

            **Watch out:** reverse=True on the final tuple key reverses every component, not just a chosen field.

            Establish lower-priority order first and preserve it inside higher-priority ties.
        ''',
        "title": "Mixed-direction catalog",
        "hints": [
            "Text cannot be reversed by numeric negation, but stable passes preserve earlier tie order.",
            "Apply the least important text rule first, then establish the remaining priorities.",
            "Build a name-descending copy, sort that result by provider, descending context, and price, then return the final list.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Order a model catalog for display, where some rules go up and others go down.

            **Your job:** write `sort_catalog(models)`

            **What goes in**
            - `models`: a list of dicts `{"name": str, "provider": str, "context": int, "price": float}`

            **What comes out**
            - a **new** list of the same dicts in this order:
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
            "Distinct terms require sets so repeated words cannot inflate a score.",
            "Keep each original document beside its score through mapping, filtering, and ranking.",
            "Normalize query and document words for overlap counting, map to scored records, filter zero scores, sort by score and length while preserving full ties, and return the original texts.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A tiny keyword *reranker*: after a search has found documents, put the ones that best match the
            user's query first.

            **Your job:** write `rerank(docs, query)`

            **What goes in**
            - `docs`: a list of strings, e.g. `["Python sorting guide", "Cooking pasta"]`
            - `query`: a string, e.g. `"python sorting"`

            **What comes out**
            - a new list of the matching documents (the original strings,
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
