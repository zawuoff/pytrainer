TOPIC = {
    "id": "lists",
    "title": "Lists",
    "track": "foundations",
    "order": 5,
    "requires": ["data-types"],
    "summary": """
        Ordered, mutable sequences: indexing and slicing, the core list methods,
        sorting, copying versus aliasing, and nested lists such as chat histories.
    """,
    "concepts": ["indexing", "negative indexing", "slicing", "append", "extend", "insert",
                 "pop", "remove", "in", "len", "sorted vs sort", "copying", "aliasing",
                 "nested lists"],
}

LESSON = r'''
## Chapter notes: Lists

A **list** is an ordered, changeable collection: `models = ["gpt-4o", "claude", "llama"]`.
`[]` is the empty list. Items can be anything, even other lists or tuples.

**Reading**
- `len(models)` - how many items (3).
- `models[0]` - first item (indexes start at **0**). `models[2]` - third.
- `models[-1]` - last item, `models[-2]` - second to last.
- `models[3]` on a 3-item list -> `IndexError`.

**Slicing** `items[start:stop]` - a **new** list from `start` up to but **not including**
`stop`. `items[:2]` first two, `items[-2:]` last two, `items[:]` a copy of everything.
Slices never raise errors: out-of-range bounds are simply clipped. Careful: `items[-0:]`
is the *whole* list (because `-0 == 0`).

**Changing in place** (these return `None`!)
- `items.append(x)` - add at the end. `items.extend(other)` - add every item of `other`.
- `items.insert(i, x)` - add at position `i`.
- `items.remove(x)` - delete the first `x` (`ValueError` if missing).
- `items.pop()` - remove and **return** the last item; `items.pop(0)` the first.
- `items.sort()` / `items.sort(reverse=True)` - sort the list itself.

**Asking questions**
- `x in items` / `x not in items` - `True` or `False`.
- `items.count(x)` - how many times `x` appears. `items.index(x)` - position of first `x`.

**New lists** - `sorted(items)` (and `reverse=True`), `a + b`, `items.copy()`, slices.

**Copy vs alias** - `b = a` gives the *same* list two names; changing one changes "both".
Use `b = a.copy()` (or `a[:]`) for an independent copy.

**Gotchas**
- `tools = tools.append("x")` sets `tools` to `None`. Call `tools.append("x")` on its own.
- `best = scores.sort()` is `None`; use `best = sorted(scores)`.
- Don't modify a list the caller gave you unless the spec says to - copy first.

Docs: [More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists).
'''

EXERCISES = [
    {
        "id": "lists-s1",
        "lesson": r'''
            ## A numbered shelf

            So far each variable held one value. A **list** holds many values, in order, in
            one variable - like a shelf with numbered slots. You write it with square brackets
            and commas. To take something off the shelf, give its slot number in square
            brackets. The first slot is number **0**, not 1.

            ```python
            models = ["gpt-4o", "claude", "llama"]
            print(models[0])
            print(models[1])
            print(len(models))
            models.append("mistral")
            print(len(models))
            print(models[1:3])
            ```

            - `models[0]` is the first item, `models[1]` the second.
            - `len(models)` counts the items.
            - `.append(...)` puts a new item at the end of the shelf.
            - `models[1:3]` takes the items from slot 1 up to (not including) slot 3.

            Vocabulary: a slot number is an *index* (plural *indexes* or *indices*); reading
            `models[0]` is *indexing*; `[1:3]` is a *slice*. Python prints a list of strings
            with single quotes: `['claude', 'llama']`.

            **Watch out:** a 3-item list has indexes 0, 1, 2. `models[3]` is an `IndexError`.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            models = ["gpt-4o", "claude", "llama"]
            print(models[0])
            print(models[-1])
            models.append("mistral")
            print(len(models))
            print(models[1:3])
        ''',
        "solution": r'''
            gpt-4o
            llama
            4
            ['claude', 'llama']
        ''',
        "explanation": r'''
            Index `0` is the first item and `-1` the last. After `append` the list has 4
            items. The slice `[1:3]` takes indexes 1 and 2 (3 is excluded), and Python
            prints a list of strings with single quotes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Indexes start at 0, and negative indexes count from the end.",
            "Work line by line and keep track of the list: append adds one item at the end before len is called.",
            "Line 1 is the item at index 0, line 2 the last item, line 3 the length after append, line 4 the items at index 1 and 2 printed as a list.",
        ],
    },
    {
        "id": "lists-s2",
        "lesson": r'''
            ## Counting from the back

            In a queue you can say "the first person" or "the last person" without knowing how
            long the queue is. Lists work the same way: **negative indexes** count from the
            end. `-1` is the last item, `-2` the one before it.

            ```python
            messages = ["hi", "hello", "how are you?"]
            print(messages[-1])
            print(messages[-2])
            messages.append("fine, thanks")
            print(messages[-1])
            ```

            Notice that `messages[-1]` always means "the newest one", however many messages
            were added. That's why chat apps use it constantly: the latest message, the most
            recent tool result, the last chunk.

            Vocabulary: this is *negative indexing*. `items[-1]` is the same item as
            `items[len(items) - 1]`, just shorter and harder to get wrong.

            **Watch out:** there is no `-0` for the last item - `items[-0]` is `items[0]`,
            the **first** item.
        ''',
        "title": "Latest message",
        "difficulty": 0,
        "prompt": r'''
            A chat app often needs the most recent message.

            **Write:** `latest(messages)` by replacing the `___` in the starter.

            - `messages`: a non-empty list of strings, oldest first, e.g. `["hi", "hello"]`
            - **Returns:** the **last** string in the list

            **Rules**
            - It must work for any length of list, including a list with just one message.

            **Examples**
            ```python
            latest(["hi", "hello", "how are you?"])   # returns "how are you?"
            latest(["a", "b", "c", "d", "e"])         # returns "e"
            latest(["only"])                          # returns "only"
            ```
        ''',
        "starter": r'''
            def latest(messages):
                return messages[___]
        ''',
        "tests": r'''
            from solution import latest

            def test_returns_last_of_three_messages():
                got = latest(["hi", "hello", "how are you?"])
                assert got == "how are you?", f"got {got!r}"

            def test_single_message_list_returns_that_message():
                got = latest(["only"])
                assert got == "only", f"got {got!r}"

            def test_returns_last_of_five_messages():
                got = latest(["a", "b", "c", "d", "e"])
                assert got == "e", f"got {got!r}"
        ''',
        "solution": r'''
            def latest(messages):
                return messages[-1]
        ''',
        "hints": [
            "Negative indexes count from the end of a list.",
            "You need one index that means 'the last item' no matter how long the list is.",
            "Replace ___ with -1.",
        ],
    },
    {
        "id": "lists-s3",
        "lesson": r'''
            ## Methods that change the list

            Adding a page to a ring binder changes *the binder*. You don't get a new binder
            back - you get nothing back. `.append()` works the same way: it changes the list
            you call it on, and returns `None` ("nothing").

            ```python
            tools = ["search"]
            tools.append("calculator")
            print(tools)
            result = tools.append("weather")
            print(result)
            print(tools)
            ```

            The second `print` shows `None`: that's what `append` gives back. The list itself
            has all three tools.

            Vocabulary: a function attached to a value, called with a dot (`tools.append(...)`),
            is a *method*. A method that changes the object itself works *in place*; the
            list is *mutable* (changeable).

            **Watch out:** `tools = tools.append("x")` replaces your list with `None`. Call
            in-place methods on their own line.
        ''',
        "title": "Fix add_tool",
        "difficulty": 0,
        "prompt": r'''
            An agent keeps a list of the tools it may call. This function has one bug:
            right now it returns `None`. Find and fix it.

            **Fix:** `add_tool(tools, name)`

            - `tools`: a list of tool names (strings), possibly empty, e.g. `["search"]`
            - `name`: the tool name to add, a string, e.g. `"calculator"`
            - **Returns:** the list, with `name` added at the **end**

            **Rules**
            - An empty list works too: it becomes a list with just `name`.

            **Examples**
            ```python
            add_tool(["search"], "calculator")   # returns ["search", "calculator"]
            add_tool([], "weather")              # returns ["weather"]
            ```
        ''',
        "starter": r'''
            def add_tool(tools, name):
                tools = tools.append(name)
                return tools
        ''',
        "tests": r'''
            from solution import add_tool

            def test_adds_name_to_end_and_returns_list():
                got = add_tool(["search"], "calculator")
                assert got == ["search", "calculator"], f"got {got!r}"

            def test_adding_to_empty_list():
                got = add_tool([], "weather")
                assert got == ["weather"], f"got {got!r}"
        ''',
        "solution": r'''
            def add_tool(tools, name):
                tools.append(name)
                return tools
        ''',
        "hints": [
            "What does .append() return? Try print([1].append(2)).",
            "append changes the list in place and returns None, so saving its result into tools throws the list away.",
            "Call tools.append(name) on its own line (without tools = in front), then return tools.",
        ],
    },
    {
        "id": "lists-s6",
        "lesson": r'''
            ## Is it on the list?

            A bouncer with a guest list doesn't care *where* your name is on the list - only
            whether it is there. The `in` operator asks exactly that question and answers
            `True` or `False`.

            ```python
            tools = ["search", "calculator"]
            print("search" in tools)
            print("email" in tools)
            print("Search" in tools)
            print("email" not in tools)
            ```

            `in` compares each item for **equality**, so `"Search"` (capital S) is not the
            same as `"search"`. `not in` is the opposite question.

            Vocabulary: `in` is the *membership* operator, and its result is a *boolean*
            (`True`/`False`) - so you can return it directly, or use it in an `if`.

            **Watch out:** no need for `if ... : return True else: return False` - the
            expression `name in tools` already *is* `True` or `False`.
        ''',
        "title": "Is this tool allowed?",
        "difficulty": 0,
        "prompt": r'''
            An agent may only call tools from an allow-list.

            **Write:** `is_allowed(tools, name)`

            - `tools`: a list of allowed tool names (strings), possibly empty, e.g.
              `["search", "calculator"]`
            - `name`: a tool name, a string, e.g. `"search"`
            - **Returns:** `True` if `name` is in `tools`, otherwise `False`

            **Rules**
            - The comparison is exact and case-sensitive (`"Search"` is not `"search"`).
            - An empty list allows nothing.
            - Return the booleans `True` / `False`, not strings.

            **Examples**
            ```python
            is_allowed(["search", "calculator"], "search")   # returns True
            is_allowed(["search", "calculator"], "email")    # returns False
            is_allowed(["search"], "Search")                 # returns False
            is_allowed([], "search")                         # returns False
            ```
        ''',
        "starter": r'''
            def is_allowed(tools, name):
                ...
        ''',
        "tests": r'''
            from solution import is_allowed

            def test_listed_tool_is_allowed():
                got = is_allowed(["search", "calculator"], "search")
                assert got is True, f"got {got!r}"

            def test_unlisted_tool_is_not_allowed():
                got = is_allowed(["search", "calculator"], "email")
                assert got is False, f"got {got!r}"

            def test_comparison_is_case_sensitive():
                got = is_allowed(["search"], "Search")
                assert got is False, f"got {got!r}"

            def test_empty_list_allows_nothing():
                got = is_allowed([], "search")
                assert got is False, f"got {got!r}"
        ''',
        "solution": r'''
            def is_allowed(tools, name):
                return name in tools
        ''',
        "hints": [
            "There is an operator that checks whether a value is in a list.",
            "The expression 'value in some_list' already evaluates to True or False, so you can return it directly.",
            "Return name in tools - one line, no if needed.",
        ],
    },
    {
        "id": "lists-s4",
        "lesson": r'''
            ## Cutting a slice

            Think of a loaf of bread with numbered slices. "Give me slices 1 up to 3" means
            slices 1 and 2 - you stop *before* 3. A list **slice** `items[start:stop]` works
            the same way, and gives you a **new** list.

            ```python
            chunks = ["a", "b", "c", "d", "e"]
            print(chunks[1:3])
            print(chunks[:2])
            print(chunks[3:])
            print(chunks[:10])
            print(chunks[:0])
            ```

            - Leave out `start` to begin at the start; leave out `stop` to go to the end.
            - `chunks[:2]` means "the first 2 items".
            - A slice **never** raises an error: `[:10]` on 5 items just gives all 5.
            - `[:0]` is an empty list `[]`.

            Vocabulary: `start` is *inclusive*, `stop` is *exclusive*. The original list is
            not changed - a slice is a copy of that part.
        ''',
        "title": "First n chunks",
        "difficulty": 0,
        "prompt": r'''
            A RAG app sends only the first few document chunks to the model.

            **Write:** `first_n(chunks, n)`

            - `chunks`: a list of strings, e.g. `["a", "b", "c", "d"]`
            - `n`: how many to keep, an int `>= 0`
            - **Returns:** a new list with the first `n` items, in their original order

            **Rules**
            - If there are fewer than `n` items, return all of them.
            - If `n` is `0`, return `[]`.
            - Tip: a *slice* does this in one step.

            **Examples**
            ```python
            first_n(["a", "b", "c", "d"], 2)   # returns ["a", "b"]
            first_n(["a"], 5)                  # returns ["a"]
            first_n(["a", "b"], 0)             # returns []
            ```
        ''',
        "starter": r'''
            def first_n(chunks, n):
                ...
        ''',
        "tests": r'''
            from solution import first_n

            def test_first_two_of_four():
                got = first_n(["a", "b", "c", "d"], 2)
                assert got == ["a", "b"], f"got {got!r}"

            def test_n_bigger_than_list_returns_all():
                got = first_n(["a"], 5)
                assert got == ["a"], f"got {got!r}"

            def test_n_zero_returns_empty_list():
                got = first_n(["a", "b"], 0)
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def first_n(chunks, n):
                return chunks[:n]
        ''',
        "hints": [
            "A slice items[start:stop] returns a new list.",
            "Start from the beginning (leave start empty) and stop at n. Slices never fail when n is too big.",
            "Return chunks with the slice [:n].",
        ],
    },
    {
        "id": "lists-s5",
        "lesson": r'''
            ## Sorted copy vs sorting in place

            Imagine a stack of exam papers. You can photocopy them in sorted order (the
            original pile stays as it was), or shuffle the original pile itself into order.
            Python gives you both:

            ```python
            scores = [0.2, 0.9, 0.5]
            print(sorted(scores))
            print(sorted(scores, reverse=True))
            print(scores)
            scores.sort()
            print(scores)
            ```

            - `sorted(scores)` is a built-in function that **returns a new** sorted list.
              The original is untouched.
            - `scores.sort()` is a method that sorts the list **in place** and returns `None`.
            - Both take `reverse=True` to put the biggest first.

            Vocabulary: `reverse=True` is a *keyword argument* - an argument passed by name.

            **Watch out:** when you are given a list, prefer `sorted(...)`, so you don't
            reorder the caller's data behind their back.
        ''',
        "title": "Best scores first",
        "difficulty": 0,
        "prompt": r'''
            A retriever gives similarity scores; you want to see the best ones first.

            **Write:** `best_first(scores)`

            - `scores`: a list of numbers, e.g. `[0.2, 0.9, 0.5]`
            - **Returns:** a **new** list with the same scores sorted from highest to lowest

            **Rules**
            - An empty list gives back an empty list `[]`.
            - Don't change the list you were given (the caller's `scores` must stay in its
              original order).

            **Examples**
            ```python
            best_first([0.2, 0.9, 0.5])   # returns [0.9, 0.5, 0.2]
            best_first([])                # returns []
            ```
        ''',
        "starter": r'''
            def best_first(scores):
                ...
        ''',
        "tests": r'''
            from solution import best_first

            def test_scores_sorted_highest_first():
                got = best_first([0.2, 0.9, 0.5])
                assert got == [0.9, 0.5, 0.2], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert best_first([]) == []

            def test_original_list_is_not_changed():
                scores = [0.2, 0.9, 0.5]
                best_first(scores)
                assert scores == [0.2, 0.9, 0.5], f"the input changed to {scores!r}"
        ''',
        "solution": r'''
            def best_first(scores):
                return sorted(scores, reverse=True)
        ''',
        "hints": [
            "There is a built-in function that returns a new sorted list, unlike the .sort() method.",
            "Use sorted() and ask it for the reverse order so the biggest comes first.",
            "Return sorted(scores, reverse=True).",
        ],
    },
    {
        "id": "lists-7",
        "lesson": r'''
            ## Two name tags, one box

            `b = a` does **not** copy a list. It sticks a second name tag on the *same* box.
            Put something in through one name and you'll see it through the other.

            ```python
            a = ["search"]
            b = a
            b.append("weather")
            print(a)
            c = a.copy()
            c.append("email")
            print(a)
            print(c)
            print(a + ["x"])
            ```

            After `b.append(...)`, `a` has changed too - there is only one list. `a.copy()`
            makes a real second box, so changing `c` leaves `a` alone. `a + [...]` also builds
            a brand-new list.

            Vocabulary: two names for one object is called *aliasing*. A parameter works the
            same way: inside a function, `tools` is an alias for the caller's list, so
            `tools.append(...)` changes **their** list.

            **Watch out:** to give back "the list plus one item" without side effects, work
            on a copy (or use `+`).
        ''',
        "title": "Don't touch the caller's list",
        "difficulty": 1,
        "prompt": r'''
            A helper should return a tool list with one extra tool, for a single request only.
            The starter works, but it has a hidden side effect: it also changes the caller's
            list, so the extra tool "leaks" into every later request. Fix it.

            **Fix:** `with_tool(tools, name)`

            - `tools`: a list of tool names (strings), possibly empty, e.g. `["search"]`
            - `name`: the extra tool name, a string, e.g. `"weather"`
            - **Returns:** a **new** list: all of `tools`, in order, then `name` at the end

            **Rules**
            - The list you were given must stay exactly as it was.
            - The returned list must be a different list object from `tools`.

            **Examples**
            ```python
            base = ["search"]
            with_tool(base, "weather")   # returns ["search", "weather"]
            base                         # still ["search"]
            with_tool([], "email")       # returns ["email"]
            ```
        ''',
        "starter": r'''
            def with_tool(tools, name):
                new_tools = tools
                new_tools.append(name)
                return new_tools
        ''',
        "tests": r'''
            from solution import with_tool

            def test_returns_tools_plus_new_name():
                got = with_tool(["search"], "weather")
                assert got == ["search", "weather"], f"got {got!r}"

            def test_empty_list_gives_just_the_name():
                got = with_tool([], "email")
                assert got == ["email"], f"got {got!r}"

            def test_callers_list_is_not_changed():
                base = ["search", "calculator"]
                with_tool(base, "weather")
                assert base == ["search", "calculator"], f"the caller's list changed to {base!r}"

            def test_returns_a_different_list_object():
                base = ["search"]
                got = with_tool(base, "weather")
                assert got is not base, "return a new list, not the one you were given"
        ''',
        "solution": r'''
            def with_tool(tools, name):
                new_tools = tools.copy()
                new_tools.append(name)
                return new_tools
        ''',
        "hints": [
            "new_tools = tools does not make a copy - both names point at the same list.",
            "Make a real copy before appending, so the append only changes the copy.",
            "Change the first line to new_tools = tools.copy() (or build the result with tools + [name]). Keep the append and the return.",
        ],
    },
    {
        "id": "lists-8",
        "lesson": r'''
            ## Reading the docs for more methods

            You've met `append`, `insert`, `remove`, `pop` and `sort`. Lists have a few more
            methods, and part of being an engineer is knowing *where to look* rather than
            memorising. The Python tutorial has a short section listing every list method,
            one line each.

            ```python
            calls = ["search", "search", "weather"]
            print(len(calls))
            print(calls.index("weather"))
            calls.extend(["email", "search"])
            print(calls)
            ```

            Here `index` tells you where an item first appears, and `extend` adds all items
            of another list.

            A good way to read that page: skim the method names, read the one-line
            description of any that sound useful, then try it in the editor.

            For this step, find the method that tells you **how many times** a value
            appears in a list. Vocabulary: this is a method that *returns* a value (unlike
            `append`, which returns `None`).
        ''',
        "title": "How often was a tool called?",
        "difficulty": 1,
        "research": {
            "note": "Lists have a built-in method that counts how many times a value appears. Skim the list methods in the tutorial section below, find it, then come back.",
            "links": [
                {"title": "More on Lists - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/datastructures.html#more-on-lists"},
            ],
        },
        "prompt": r'''
            An agent logs the name of every tool it calls, in order. You want to know how many
            times one tool was used.

            **Write:** `call_count(calls, name)`

            - `calls`: a list of tool names (strings), possibly empty, e.g.
              `["search", "weather", "search"]`
            - `name`: the tool to count, a string
            - **Returns:** an int, how many items of `calls` are exactly equal to `name`

            **Rules**
            - A tool that never appears counts `0`.
            - The comparison is exact and case-sensitive.
            - Don't change the list you were given.
            - Use the list method you found in the docs (no loop needed).

            **Examples**
            ```python
            call_count(["search", "weather", "search"], "search")   # returns 2
            call_count(["search", "weather"], "email")              # returns 0
            call_count(["Search", "search"], "search")              # returns 1
            call_count([], "search")                                # returns 0
            ```
        ''',
        "starter": r'''
            def call_count(calls, name):
                ...
        ''',
        "tests": r'''
            from solution import call_count

            def test_counts_repeated_tool():
                got = call_count(["search", "weather", "search"], "search")
                assert got == 2, f"got {got!r}"

            def test_missing_tool_counts_zero():
                got = call_count(["search", "weather"], "email")
                assert got == 0, f"got {got!r}"

            def test_count_is_case_sensitive():
                got = call_count(["Search", "search"], "search")
                assert got == 1, f"got {got!r}"

            def test_empty_list_counts_zero():
                assert call_count([], "search") == 0

            def test_input_list_is_not_modified():
                calls = ["a", "b", "a"]
                call_count(calls, "a")
                assert calls == ["a", "b", "a"], f"the input changed to {calls!r}"
        ''',
        "solution": r'''
            def call_count(calls, name):
                return calls.count(name)
        ''',
        "hints": [
            "Look at the list methods in the linked tutorial section: one of them counts.",
            "The method is called on the list, takes the value to look for, and returns a number.",
            "Return calls.count(name).",
        ],
    },
    {
        "id": "lists-1",
        "lesson": r'''
            ## Chaining steps

            An assembly line passes the product from one station to the next. You can do the
            same with list operations: the result of one step is a list, so you can slice it,
            sort it or pass it on straight away.

            ```python
            scores = [0.2, 0.9, 0.5, 0.7]
            ranked = sorted(scores, reverse=True)
            print(ranked)
            print(ranked[:2])
            print(sorted(scores)[:1])
            print(scores)
            ```

            The two-line version (a named `ranked` variable, then a slice) and the one-line
            version (`sorted(...)[:1]`) do the same thing. Choose whichever reads better.

            Remember: `sorted` builds a new list and slices build new lists, so the original
            `scores` never changes. And a slice is safe when it asks for more items than exist.

            Vocabulary: writing one operation right after another like this is called
            *chaining*.
        ''',
        "hints": [
            'You need two list tools from the lesson: one that sorts into a new list and one that takes the first few items.',
            'Sort the scores from highest to lowest without touching the original, then keep only the first k of them.',
            'Call sorted() with reverse=True to get a new list, then slice it with [:k] and return that. A slice never fails if k is bigger than the list.',
        ],
        "title": "Top k scores",
        "difficulty": 1,
        "prompt": r'''
            A retriever returns similarity scores and you only want the best few.

            **Write:** `top_k(scores, k)`

            - `scores`: a list of numbers, e.g. `[0.2, 0.9, 0.5, 0.7]`
            - `k`: how many scores to keep, an int `>= 0`, e.g. `2`
            - **Returns:** a **new** list with the `k` highest scores, highest first

            **Rules**
            - If `k` is larger than the number of scores, return all of them, highest first.
            - If `k` is `0`, return `[]`.
            - Equal scores are all kept (duplicates count as separate scores).
            - Don't change the list you were given.

            **Examples**
            ```python
            top_k([0.2, 0.9, 0.5, 0.7], 2)   # returns [0.9, 0.7]
            top_k([0.3, 0.8], 5)             # returns [0.8, 0.3]
            top_k([0.5, 0.9, 0.9, 0.1], 3)   # returns [0.9, 0.9, 0.5]
            top_k([0.3, 0.8], 0)             # returns []
            ```
        ''',
        "starter": r'''
            def top_k(scores, k):
                ...
        ''',
        "tests": r'''
            from solution import top_k

            def test_returns_two_highest_scores_highest_first():
                got = top_k([0.2, 0.9, 0.5, 0.7], 2)
                assert got == [0.9, 0.7], f"got {got!r}"

            def test_k_larger_than_list_returns_all_sorted():
                got = top_k([0.3, 0.8], 5)
                assert got == [0.8, 0.3], f"got {got!r}"

            def test_k_zero_returns_empty_list():
                got = top_k([0.3, 0.8], 0)
                assert got == [], f"got {got!r}"

            def test_duplicate_scores_are_kept():
                got = top_k([0.5, 0.9, 0.9, 0.1], 3)
                assert got == [0.9, 0.9, 0.5], f"got {got!r}"

            def test_input_list_is_not_modified():
                scores = [0.2, 0.9, 0.5]
                top_k(scores, 2)
                assert scores == [0.2, 0.9, 0.5], f"the input list was changed to {scores!r}"
        ''',
        "solution": r'''
            def top_k(scores, k):
                return sorted(scores, reverse=True)[:k]
        ''',
    },
    {
        "id": "lists-2",
        "lesson": r'''
            ## Moving items around

            Picture a stack of recently used apps: when you open one, it jumps to the top and
            everything else shifts down. Lists have two in-place methods for that:

            ```python
            models = ["gpt-4o", "claude", "llama"]
            models.remove("claude")
            print(models)
            models.insert(0, "claude")
            print(models)
            models.insert(1, "mistral")
            print(models)
            print(models.remove("mistral"))
            ```

            - `remove(x)` deletes the **first** item equal to `x`. If `x` isn't there, it
              raises a `ValueError` - so check with `in` first when it might be missing.
            - `insert(i, x)` puts `x` at index `i` and shifts the rest to the right.
              `insert(0, x)` puts it at the front.
            - Both return `None`: they change the list in place.

            Vocabulary: a function that changes its argument instead of returning a new value
            is said to have a *side effect*. When a spec says "modify the list in place and
            return `None`", this is what it means.
        ''',
        "hints": [
            'Use the in operator plus the list methods that remove an item and insert at a position.',
            'If the name is already present, take it out first. Either way, it then goes in at index 0. Change the list itself and return nothing.',
            'Check if name in models: if so, call models.remove(name) (it removes only the first match). Then call models.insert(0, name). No return statement is needed.',
        ],
        "title": "Move to front",
        "difficulty": 1,
        "prompt": r'''
            A model picker keeps the most recently used models at the top.

            **Write:** `move_to_front(models, name)`

            - `models`: a list of model names (strings), e.g. `["gpt-4o", "claude", "llama"]`
            - `name`: the model that was just used, a string
            - **Returns:** `None` (no `return` value). Instead, it changes the list it was
              given (this is called modifying the list *in place*).

            **Rules**
            - If `name` is already in the list, move it to index 0. Only its **first**
              occurrence moves; any later copies stay where they are.
            - If `name` is already first, the list ends up unchanged.
            - If `name` is not in the list, insert it at index 0.
            - The other items keep their relative order.

            **Examples**
            ```python
            models = ["gpt-4o", "claude", "llama"]
            move_to_front(models, "llama")      # returns None
            models   # now ["llama", "gpt-4o", "claude"]

            models = ["gpt-4o"]
            move_to_front(models, "mistral")
            models   # now ["mistral", "gpt-4o"]

            models = ["a", "b", "c", "b"]
            move_to_front(models, "b")
            models   # now ["b", "a", "c", "b"]
            ```
        ''',
        "starter": r'''
            def move_to_front(models, name):
                ...
        ''',
        "tests": r'''
            from solution import move_to_front

            def test_existing_name_moves_to_front():
                models = ["gpt-4o", "claude", "llama"]
                move_to_front(models, "llama")
                assert models == ["llama", "gpt-4o", "claude"], f"list is {models!r}"

            def test_new_name_is_inserted_at_front():
                models = ["gpt-4o"]
                move_to_front(models, "mistral")
                assert models == ["mistral", "gpt-4o"], f"list is {models!r}"

            def test_name_already_first_leaves_list_unchanged():
                models = ["a", "b"]
                move_to_front(models, "a")
                assert models == ["a", "b"], f"list is {models!r}"

            def test_only_first_occurrence_moves():
                models = ["a", "b", "c", "b"]
                move_to_front(models, "b")
                assert models == ["b", "a", "c", "b"], f"list is {models!r}"

            def test_returns_none_and_mutates_same_list():
                models = ["x", "y"]
                result = move_to_front(models, "y")
                assert result is None, "modify the list in place and return None"
                assert models == ["y", "x"], f"list is {models!r}"
        ''',
        "solution": r'''
            def move_to_front(models, name):
                if name in models:
                    models.remove(name)
                models.insert(0, name)
        ''',
    },
    {
        "id": "lists-3",
        "hints": [
            "Slicing is the key tool, plus checking the first message's role with messages[0][0].",
            "Split the history into a head (the system message, or nothing) and the rest. Take the last n items of the rest, then join head and tail with +.",
            "If messages is not empty and messages[0][0] == \"system\": head = messages[:1], rest = messages[1:]; else head = [] and rest = messages. Watch out: rest[-0:] is the WHOLE list, so when n is 0 the tail must be []. Return head + tail.",
        ],
        "title": "Trim chat history",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            To fit a model's context window, a chat app keeps only the most recent messages.

            **Write:** `trim_history(messages, n)`

            - `messages`: a list of messages, oldest first. Each message is a
              `(role, text)` tuple, e.g. `("user", "hi")`. The list may be empty.
            - `n`: how many recent messages to keep, an int `>= 0`
            - **Returns:** a **new** list of messages (the same tuples, in the same order)

            **Rules**
            - If the **first** message has role `"system"`, it is always kept, at the front,
              followed by the last `n` of the *other* messages.
            - A `"system"` message that is not first is treated like any other message.
            - Otherwise, return just the last `n` messages.
            - If there are fewer than `n` messages to choose from, keep all of them.
            - `n = 0` keeps no normal messages (only the leading system message, if any).
            - An empty `messages` list returns `[]`.
            - Don't change the list you were given, and always return a new list (even when
              everything is kept).

            **Examples**
            ```python
            sys_msg = ("system", "Be brief.")
            u1, a1, u2 = ("user", "hi"), ("assistant", "hello"), ("user", "bye")

            trim_history([sys_msg, u1, a1, u2], 2)   # returns [sys_msg, a1, u2]
            trim_history([u1, a1, u2], 1)            # returns [u2]
            trim_history([u1, sys_msg, a1], 1)       # returns [a1]
            trim_history([sys_msg, u1], 0)           # returns [sys_msg]
            trim_history([u1, a1], 0)                # returns []
            trim_history([sys_msg, u1], 10)          # returns [sys_msg, u1]
            ```
        ''',
        "starter": r'''
            def trim_history(messages, n):
                ...
        ''',
        "tests": r'''
            from solution import trim_history

            SYS = ("system", "Be brief.")
            U1 = ("user", "hi")
            A1 = ("assistant", "hello")
            U2 = ("user", "bye")

            def test_keeps_system_message_plus_last_n():
                got = trim_history([SYS, U1, A1, U2], 2)
                assert got == [SYS, A1, U2], f"got {got!r}"

            def test_without_system_message_keeps_last_n():
                got = trim_history([U1, A1, U2], 1)
                assert got == [U2], f"got {got!r}"

            def test_system_message_not_first_is_not_special():
                got = trim_history([U1, SYS, A1], 1)
                assert got == [A1], f"got {got!r}"

            def test_n_zero_keeps_nothing_but_system():
                got = trim_history([SYS, U1, A1], 0)
                assert got == [SYS], f"got {got!r}"
                got = trim_history([U1, A1], 0)
                assert got == [], f"with n=0 and no system message, got {got!r}"

            def test_n_larger_than_history_keeps_everything():
                got = trim_history([SYS, U1], 10)
                assert got == [SYS, U1], f"got {got!r}"

            def test_empty_history_returns_empty_list():
                assert trim_history([], 3) == []

            def test_input_not_modified_and_new_list_returned():
                history = [SYS, U1, A1, U2]
                got = trim_history(history, 10)
                assert history == [SYS, U1, A1, U2], "the input list was modified"
                assert got is not history, "return a new list, not the same object"
        ''',
        "solution": r'''
            def trim_history(messages, n):
                if messages and messages[0][0] == "system":
                    head, rest = messages[:1], messages[1:]
                else:
                    head, rest = [], messages
                if n == 0:
                    tail = []
                else:
                    tail = rest[-n:]
                return head + tail
        ''',
    },
    {
        "id": "lists-4",
        "hints": [
            "A slice gives you a window of the list. Be careful: a negative start in a slice counts from the END.",
            "The window goes from center - radius to center + radius (inclusive). If the start would be below 0, use 0 instead. The end can safely go past the list.",
            "Compute start = center - radius; if start < 0, set start = 0. The stop of the slice is center + radius + 1 (stop is excluded). Return words[start:stop].",
        ],
        "title": "Context around a hit",
        "difficulty": 2,
        "prompt": r'''
            A search found a match inside a document. To show the match in context, you
            display a few words on each side of it.

            **Write:** `around(words, center, radius)`

            - `words`: a list of strings, e.g. `["a", "b", "c", "d", "e", "f"]`
            - `center`: the index of the matching word, always a valid index
            - `radius`: how many words to show on each side, an int `>= 0`
            - **Returns:** a **new** list: the word at `center` plus up to `radius` words
              before it and up to `radius` words after it, in their original order

            **Rules**
            - Near the start or end of the list the window is simply shorter. It never
              wraps around to the other end of the list.
            - `radius` `0` returns just the word at `center`.
            - If the radius covers the whole list, return all the words.
            - Don't change the list you were given, and return a new list.

            **Examples**
            ```python
            words = ["a", "b", "c", "d", "e", "f"]
            around(words, 3, 1)     # returns ["c", "d", "e"]
            around(words, 1, 2)     # returns ["a", "b", "c", "d"]
            around(words, 0, 3)     # returns ["a", "b", "c", "d"]
            around(words, 5, 2)     # returns ["d", "e", "f"]
            around(words, 2, 0)     # returns ["c"]
            ```
        ''',
        "starter": r'''
            def around(words, center, radius):
                ...
        ''',
        "tests": r'''
            from solution import around

            W = ["a", "b", "c", "d", "e", "f"]

            def test_window_in_the_middle():
                got = around(W, 3, 1)
                assert got == ["c", "d", "e"], f"got {got!r}"

            def test_near_start_is_cut_not_wrapped():
                got = around(W, 1, 2)
                assert got == ["a", "b", "c", "d"], f"got {got!r}"
                got = around(W, 0, 3)
                assert got == ["a", "b", "c", "d"], f"got {got!r}"

            def test_near_end_is_cut():
                got = around(W, 5, 2)
                assert got == ["d", "e", "f"], f"got {got!r}"

            def test_radius_zero_returns_only_center_word():
                got = around(W, 2, 0)
                assert got == ["c"], f"got {got!r}"

            def test_huge_radius_returns_all_words():
                got = around(W, 2, 100)
                assert got == W, f"got {got!r}"

            def test_input_not_modified_and_new_list_returned():
                words = list(W)
                got = around(words, 2, 100)
                assert words == W, "the input list was modified"
                assert got is not words, "return a new list"
        ''',
        "solution": r'''
            def around(words, center, radius):
                start = center - radius
                if start < 0:
                    start = 0
                return words[start:center + radius + 1]
        ''',
    },
    {
        "id": "lists-5",
        "hints": [
            "Two pieces: a slice for the page, and a rounding-up division for the page count.",
            "The number of pages is len(items) divided by per_page, rounded UP. Page p (1-based) starts at index (p - 1) * per_page. Pages outside 1..total_pages are empty.",
            "total_pages = (len(items) + per_page - 1) // per_page. If page < 1 or page > total_pages, return ([], total_pages). Otherwise start = (page - 1) * per_page and return (items[start:start + per_page], total_pages).",
        ],
        "title": "Paginate results",
        "difficulty": 3,
        "prompt": r'''
            A search API shows its results page by page (this is called *pagination*).

            **Write:** `get_page(items, page, per_page)`

            - `items`: the full list of results, e.g. `["r1", "r2", "r3", "r4", "r5"]`
            - `page`: which page to show, an int. Pages are numbered from **1** (1-based).
            - `per_page`: how many items fit on one page, an int, always `>= 1`
            - **Returns:** a tuple `(page_items, total_pages)`
              - `page_items`: a new list with the items on that page, in order
              - `total_pages`: an int, how many pages are needed to show every item

            **Rules**
            - A partly filled last page still counts as a page (5 items, 2 per page = 3 pages).
            - If the items fit exactly, there is no extra empty page (4 items, 2 per page = 2 pages).
            - No items means `0` pages.
            - For a `page` outside `1..total_pages` (for example `0`, `-1`, or too big),
              `page_items` is `[]`; `total_pages` is still the real count.
            - Don't change the list you were given.

            **Examples**
            ```python
            results = ["r1", "r2", "r3", "r4", "r5"]
            get_page(results, 1, 2)     # returns (["r1", "r2"], 3)
            get_page(results, 3, 2)     # returns (["r5"], 3)
            get_page(results, 4, 2)     # returns ([], 3)
            get_page(results, 0, 2)     # returns ([], 3)
            get_page(results, 1, 100)   # returns (["r1", "r2", "r3", "r4", "r5"], 1)
            get_page([], 1, 10)         # returns ([], 0)
            ```
        ''',
        "starter": r'''
            def get_page(items, page, per_page):
                ...
        ''',
        "tests": r'''
            from solution import get_page

            R = ["r1", "r2", "r3", "r4", "r5"]

            def check(items, page, per_page, expected):
                got = get_page(items, page, per_page)
                assert got == expected, f"get_page({items}, {page}, {per_page}) returned {got!r}"

            def test_first_and_middle_pages():
                check(R, 1, 2, (["r1", "r2"], 3))
                check(R, 2, 2, (["r3", "r4"], 3))

            def test_partial_last_page():
                check(R, 3, 2, (["r5"], 3))

            def test_exact_fit_has_no_extra_page():
                check(R[:4], 2, 2, (["r3", "r4"], 2))
                check(R[:4], 3, 2, ([], 2))

            def test_out_of_range_pages_are_empty():
                check(R, 0, 2, ([], 3))
                check(R, -1, 2, ([], 3))
                check(R, 4, 2, ([], 3))

            def test_no_items_means_zero_pages():
                check([], 1, 10, ([], 0))

            def test_everything_fits_on_one_big_page():
                check(R, 1, 100, (R, 1))

            def test_input_list_is_not_modified():
                items = list(R)
                get_page(items, 2, 2)
                assert items == R, "the input list was modified"
        ''',
        "solution": r'''
            def get_page(items, page, per_page):
                total_pages = (len(items) + per_page - 1) // per_page
                if page < 1 or page > total_pages:
                    return [], total_pages
                start = (page - 1) * per_page
                return items[start:start + per_page], total_pages
        ''',
    },
    {
        "id": "lists-6",
        "hints": [
            "Slices for the first and last parts, len() for the count, an f-string for the marker, and + to join lists.",
            "If the list is short enough (at most 2 * keep items), just return a copy. Otherwise keep the first keep items, a marker saying how many were hidden, then the last keep items.",
            "If len(messages) <= 2 * keep, return messages[:] (a copy). Else hidden = len(messages) - 2 * keep; head = messages[:keep]; tail = [] when keep is 0 (because [-0:] is the whole list!), otherwise messages[-keep:]. Return head + [f\"[{hidden} messages hidden]\"] + tail.",
        ],
        "title": "Compact a long conversation",
        "difficulty": 3,
        "prompt": r'''
            To show a long chat in a small panel, keep only the start and the end and
            replace the middle with a short marker.

            **Write:** `compact(messages, keep)`

            - `messages`: a list of strings, possibly empty, e.g. `["m1", "m2", "m3"]`
            - `keep`: how many messages to keep at **each** end, an int `>= 0`
            - **Returns:** a **new** list of strings

            **Rules**
            - If there are at most `2 * keep` messages (nothing would be hidden), return a
              **copy** of the whole list: equal contents, but a new list object.
            - Otherwise return: the first `keep` messages, then **one** marker string
              `"[<hidden> messages hidden]"`, then the last `keep` messages. `<hidden>` is
              the number of messages left out.
            - The marker always says `messages`, even for 1 (`"[1 messages hidden]"`).
            - With `keep` `0` and a non-empty list, the result is only the marker.
            - An empty list returns `[]`.
            - Don't change the list you were given.

            **Examples**
            ```python
            msgs = ["m1", "m2", "m3", "m4", "m5", "m6", "m7"]
            compact(msgs, 2)       # returns ["m1", "m2", "[3 messages hidden]", "m6", "m7"]
            compact(msgs[:5], 2)   # returns ["m1", "m2", "[1 messages hidden]", "m4", "m5"]
            compact(msgs, 4)       # returns a new list equal to msgs (7 <= 8)
            compact(msgs, 0)       # returns ["[7 messages hidden]"]
            compact([], 3)         # returns []
            ```
        ''',
        "starter": r'''
            def compact(messages, keep):
                ...
        ''',
        "tests": r'''
            from solution import compact

            M = ["m1", "m2", "m3", "m4", "m5", "m6", "m7"]

            def test_keeps_both_ends_with_hidden_marker():
                got = compact(M, 2)
                assert got == ["m1", "m2", "[3 messages hidden]", "m6", "m7"], f"got {got!r}"

            def test_short_list_is_returned_as_a_copy():
                got = compact(M, 4)
                assert got == M, f"got {got!r}"
                assert got is not M, "return a new list, not the same object"

            def test_exactly_two_keep_is_not_compacted():
                got = compact(M[:6], 3)
                assert got == M[:6], f"got {got!r}"

            def test_one_hidden_message_marker():
                got = compact(M[:5], 2)
                assert got == ["m1", "m2", "[1 messages hidden]", "m4", "m5"], f"got {got!r}"

            def test_keep_zero_returns_only_the_marker():
                got = compact(M, 0)
                assert got == ["[7 messages hidden]"], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert compact([], 0) == [], f"got {compact([], 0)!r}"
                assert compact([], 3) == [], f"got {compact([], 3)!r}"

            def test_input_list_is_not_modified():
                msgs = list(M)
                compact(msgs, 1)
                assert msgs == M, f"the input changed to {msgs!r}"
        ''',
        "solution": r'''
            def compact(messages, keep):
                if len(messages) <= 2 * keep:
                    return messages[:]
                hidden = len(messages) - 2 * keep
                head = messages[:keep]
                if keep == 0:
                    tail = []
                else:
                    tail = messages[-keep:]
                return head + [f"[{hidden} messages hidden]"] + tail
        ''',
    },
]
