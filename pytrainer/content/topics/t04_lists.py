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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["list", "square brackets", "index", "negative index", "slice", "append", "pop",
                 "insert", "remove", "sort", "sorted", "copy", "alias", "len", "indexerror",
                 "nested"],
    "cards": [
        {
            "syntax": "items[i]  /  items[-1]",
            "explain": "Reads the item at index i. The first index is 0. A negative index counts from the end, so -1 is the last item.",
            "example": r'''
                models = ["gpt-4o", "claude", "llama"]
                print(models[0], models[-1])
                # gpt-4o llama
                print(len(models))
                # 3
            ''',
        },
        {
            "syntax": "items[start:stop]",
            "explain": "A new list with the items from index start up to, but not including, stop. Both parts are optional.",
            "example": r'''
                chunks = ["a", "b", "c", "d", "e"]
                print(chunks[1:3])
                # ['b', 'c']
                print(chunks[:2], chunks[-2:])
                # ['a', 'b'] ['d', 'e']
            ''',
        },
        {
            "syntax": "items.append(x)  /  items.pop()",
            "explain": "append adds x at the end and returns None. pop removes the last item and returns it. Both change the list.",
            "example": r'''
                tools = ["search"]
                tools.append("email")
                print(tools)
                # ['search', 'email']
                print(tools.pop())
                # email
            ''',
        },
        {
            "syntax": "items.insert(i, x)  /  items.remove(x)",
            "explain": "insert puts x at index i. remove deletes the first item equal to x and raises ValueError if there is none.",
            "example": r'''
                models = ["gpt-4o", "claude", "llama"]
                models.remove("claude")
                models.insert(0, "mistral")
                print(models)
                # ['mistral', 'gpt-4o', 'llama']
            ''',
        },
        {
            "syntax": "x in items",
            "explain": "True when some item of the list equals x. x not in items gives the opposite result.",
            "example": r'''
                tools = ["search", "calculator"]
                print("search" in tools)
                # True
                print("email" not in tools)
                # True
            ''',
        },
        {
            "syntax": "sorted(items)  /  items.sort()",
            "explain": "sorted returns a new sorted list. sort reorders the existing list and returns None. Both accept reverse=True.",
            "example": r'''
                scores = [0.2, 0.9, 0.5]
                print(sorted(scores, reverse=True))
                # [0.9, 0.5, 0.2]
                scores.sort()
                print(scores)
                # [0.2, 0.5, 0.9]
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Lists

A **list** is a value that holds other values in a fixed order. You write a list with
square brackets and separate the items with commas. `[]` is the empty list. An item can
be any value, including another list or a tuple.

```python
models = ["gpt-4o", "claude", "llama"]
print(models)
# ['gpt-4o', 'claude', 'llama']
print(len(models))
# 3
```

`len(models)` returns the number of items in the list.

### Indexes

An **index** is a whole number that gives the position of an item. The first item has
index `0`. A negative index counts from the end, so `-1` is the last item.

```python
models = ["gpt-4o", "claude", "llama"]
print(models[0])
# gpt-4o
print(models[2])
# llama
print(models[-1])
# llama
print(models[-2])
# claude
```

A list with 3 items has the indexes 0, 1 and 2. `models[3]` stops
the program with `IndexError: list index out of range`. (The proper verb for this is
**raises**: the index lookup raises an `IndexError`.)

A list inside a list is a **nested list**. Use one index after the other: the first index
picks the inner list (or tuple) and the second picks an item of it.

```python
history = [("user", "hi"), ("assistant", "hello")]
print(history[0])
# ('user', 'hi')
print(history[0][0])
# user
```

### Slices

A **slice** `items[start:stop]` builds a new list. It holds the items from index `start`
up to, but not including, index `stop`. If you leave out `start`, the slice begins at
index 0. If you leave out `stop`, the slice runs to the end of the list.

```python
chunks = ["a", "b", "c", "d", "e"]
print(chunks[1:3])
# ['b', 'c']
print(chunks[:2])
# ['a', 'b']
print(chunks[-2:])
# ['d', 'e']
print(chunks[:10])
# ['a', 'b', 'c', 'd', 'e']
```

A slice never raises `IndexError`. When `start` or `stop` is past the end of the list,
Python uses the end of the list instead. `chunks[:]` is a copy of the whole list.

Drag the start and stop handles to see which items the slice takes.

```diagram
{"type":"slice","title":"Slicing chunks","name":"chunks","items":["a","b","c","d","e"],"start":1,"stop":3}
```

### Methods that change the list

A **method** is a function that you call on a value with a dot, as in
`tools.append("email")`. The methods below change the list **in place**: they modify the
existing list, do not create a new one and return `None`. Only `pop` returns something else.

```python
tools = ["search"]
tools.append("calculator")
tools.extend(["weather", "email"])
tools.insert(0, "browser")
tools.remove("weather")
print(tools)
# ['browser', 'search', 'calculator', 'email']
print(tools.pop())
# email
print(tools.pop(0))
# browser
print(tools)
# ['search', 'calculator']
```

- `append(x)` adds `x` at the end.
- `extend(other)` adds every item of the list `other` at the end.
- `insert(i, x)` puts `x` at index `i` and moves the later items one position right.
- `remove(x)` deletes the first item equal to `x`. It raises `ValueError` if no item is equal to `x`.
- `pop()` removes the last item and returns it. `pop(0)` removes and returns the first item.

### Sorting

`sorted(items)` returns a new sorted list and leaves `items` unchanged. `items.sort()`
sorts the list in place and returns `None`. Both accept `reverse=True` to put the
largest value first. `reverse=True` is a **keyword argument**: you pass it by name.

```python
scores = [0.2, 0.9, 0.5]
print(sorted(scores, reverse=True))
# [0.9, 0.5, 0.2]
print(scores)
# [0.2, 0.9, 0.5]
scores.sort()
print(scores)
# [0.2, 0.5, 0.9]
```

### Questions about a list

`x in items` is `True` when some item equals `x`, and `x not in items` is the opposite.
`items.count(x)` returns how many items equal `x`. `items.index(x)` returns the index of
the first item equal to `x`.

```python
calls = ["search", "search", "weather"]
print("search" in calls)
# True
print("email" not in calls)
# True
print(calls.count("search"))
# 2
print(calls.index("weather"))
# 2
```

### New lists

An **object** is one value stored in the computer's memory. These expressions create a new
list object and leave the original unchanged:
`sorted(items)`, `a + b`, `items.copy()` and any slice.

```python
calls = ["search", "search", "weather"]
print(calls + ["email"])
# ['search', 'search', 'weather', 'email']
print(calls)
# ['search', 'search', 'weather']
```

### Copy and alias

`backup = history` does not create a list. It makes the name `backup` refer to the same
list object that `history` refers to. Two names for one object are called **aliases**.
`history.copy()` creates a second list object with the same items. `a is b` is `True` when
both names refer to the same object.

```python
history = [12, 40, 7]
backup = history
backup.append(99)
print(history)
# [12, 40, 7, 99]
print(history is backup)
# True
saved = history.copy()
saved.append(5)
print(history)
# [12, 40, 7, 99]
print(saved)
# [12, 40, 7, 99, 5]
```

Switch between `backup = history` and `backup = history.copy()`, then run the statements.

```diagram
{"type":"alias-copy","title":"Alias or copy of history","a":"history","b":"backup","items":[12,40,7],"append":99}
```

### Common mistakes

`append` returns `None`, so assigning its result replaces your list with `None`.

```python
tools = ["search"]
tools = tools.append("email")
print(tools)
# None
```

- Call `tools.append("email")` as its own statement, without `tools =` in front.
- `best = scores.sort()` sets `best` to `None`. Write `best = sorted(scores)`.
- `items[-0:]` is the whole list, because `-0` equals `0`.
- A function that receives a list receives the caller's list object. Copy it first unless the task says to change it.

Docs: [More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists).
'''

EXERCISES = [
    {
        "id": "lists-s1",
        "lesson": r'''
            ## Keeping several things in order

            A chat app does not hold one message. It holds a whole conversation. A search tool does not
            return one result. It returns ten. Sooner or later every program needs to keep several values
            together, in order, under one name.

            In Python you write them between square brackets, with commas in between:

            ```python
            models = ["gpt-4o", "claude", "llama"]
            print(models)
            # ['gpt-4o', 'claude', 'llama']
            print(len(models))
            # 3
            ```

            This is called a **list**, and each value inside it is an **item**. `len(models)` counts the
            items, the same way `len` counted the characters of a string in the Basics chapter. (Python
            prints the text items of a list in single quotes. They are still the same strings.)

            ### Reading one item

            Every item has a position number. To read an item, write its position in square brackets after
            the name of the list. The surprise is that Python starts counting at 0, not at 1.

            ```python
            models = ["gpt-4o", "claude", "llama"]
            print(models[0])
            # gpt-4o
            print(models[1])
            # claude
            print(models[-1])
            # llama
            ```

            The position number is called an **index**. Index `0` is the first item. A minus sign counts
            from the other end, so index `-1` is the last item. Click a cell to see both numbers for it:

            ```diagram
            {"type":"list-index","title":"Indexes of models","name":"models","items":["gpt-4o","claude","llama"]}
            ```

            ```quiz
            `models` has 3 items. What does `models[3]` do?
            - [ ] It reads the third item, `llama` :: The third item is at index 2, because counting starts at 0.
            - [x] It stops the program with an error :: Right. Three items use the indexes 0, 1 and 2. Nothing is at index 3, so Python stops with `IndexError: list index out of range`.
            - [ ] It goes back to the first item :: Python does not wrap around. An index past the end is an error.
            ```

            ### Adding an item, and reading several at once

            Two more things appear in this step. `models.append("mistral")` adds one item to the end of the
            list. And a colon between two indexes reads several items in one go: `models[0:2]` means "start
            at index 0 and stop before index 2".

            ```python
            models = ["gpt-4o", "claude", "llama"]
            models.append("mistral")
            print(len(models))
            # 4
            print(models[0:2])
            # ['gpt-4o', 'claude']
            ```

            Reading a range such as `[0:2]` is called a **slice**. The item at the stop index is left out.
            Later steps in this chapter come back to `append` and to slices, so a first look is enough here.

            ```predict
            tools = ["search", "email"]
            tools.append("weather")
            print(tools[-1])
            print(tools[0:2])
            ---
            `append` put `"weather"` at the end, so `-1` reads it. The slice `[0:2]` takes index 0 and
            index 1 and stops before index 2, so `"weather"` is not in it.
            ```

            **Watch out:** the first item is `[0]`, not `[1]`. Reading `[1]` and getting the second item
            happens to everyone at least once.

            **In short:** a list holds items in order, `items[0]` is the first, `items[-1]` is the last,
            and counting starts at 0.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
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
            Index `0` is the first item, `gpt-4o`. Index `-1` is the last of the three, `llama`. Then
            `append` adds `mistral`, so `len` counts 4 items. The slice `[1:3]` takes index 1 and index 2
            and stops before index 3. Python prints the result as a list, with the text in single quotes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Go through the program one line at a time, and keep track of what is in the list after each line.",
            "Counting starts at 0, a minus sign counts from the end, and `append` makes the list one item longer before `len` counts it.",
            "Your first line is the first item. Your second line is the last of the original three items. Your third line is how many items there are after one was added. Your fourth line is a list: the items at index 1 and index 2, written the way Python prints a list.",
        ],
    },
    {
        "id": "lists-s2",
        "lesson": r'''
            ## The last item, without counting

            Your chat app keeps every message in a list, oldest first. The newest message is the one at the
            end. How do you ask Python for it?

            You could count. This list has 3 messages and counting starts at 0, so the last one is at
            index 2:

            ```python
            messages = ["hi", "hello", "how are you?"]
            print(messages[2])
            # how are you?
            ```

            That works until someone sends a fourth message. Index 2 is then no longer the end, and your
            code shows an old message without any error to warn you.

            Python has a way to say "the end" directly. Put a minus sign in front of the number, and Python
            counts from the end instead of from the start:

            ```python
            messages = ["hi", "hello", "how are you?"]
            print(messages[-1])
            # how are you?
            print(messages[-2])
            # hello
            ```

            `-1` is the last item, `-2` is the one before it, and so on. The list can grow as much as it
            likes, and `-1` still lands on the end.

            ```predict
            messages = ["hi", "hello", "how are you?"]
            messages.append("fine, thanks")
            print(messages[-1])
            print(messages[-3])
            ---
            `append` added a fourth message, so `-1` now reads `"fine, thanks"`. Counting back three from
            the end lands on `"hello"`.
            ```

            An index with a minus sign is called a **negative index**. Python works it out as the length
            of the list minus the number, so in a list of 4 items, `-1` is the same position as `4 - 1`,
            which is index 3.

            ```quiz
            A list has 5 items. Which index reads the same item as `[-1]`?
            - [ ] `[5]` :: Counting starts at 0, so 5 items use the indexes 0 to 4. `[5]` is past the end and stops the program with an `IndexError`.
            - [x] `[4]` :: Yes. Five items sit at indexes 0, 1, 2, 3 and 4, so the last one is at 4, which is `5 - 1`.
            - [ ] `[0]` :: `[0]` is the first item. It is the same as `[-1]` only when the list has exactly one item.
            ```

            **Watch out:** `-0` is the same number as `0`, so `messages[-0]` is the first message, not the
            last one.

            **In short:** `items[-1]` is the last item of a list, however long the list is.
        ''',
        "title": "Latest message",
        "difficulty": 0,
        "prompt": r'''
            A chat screen shows a preview of the newest message. The messages are kept in a list, oldest
            first, so the newest one is always at the end.

            **Your job:** finish `latest(messages)` so that it gives back the last message in the list. The
            function is already written except for one gap, marked `___`. Replace the gap.

            **What goes in**
            - `messages`: a list of messages (strings) with at least one message in it, for example
              `["hi", "hello"]`

            **What comes out**
            - the last message in the list, for example `"hello"`

            **Rules**
            - It must work for a list of any length. The checks try lists of 1, 3 and 5 messages.

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
            "Which kind of index counts from the end of the list instead of from the start?",
            "A fixed position such as 2 is only right for one length of list. You need a single index that means \"the last item\" for every length.",
            "Look at the second example in the lesson. The index it uses to read the newest message is what belongs in the gap.",
        ],
    },
    {
        "id": "lists-s3",
        "lesson": r'''
            ## Changing a list that already exists

            An agent starts with one tool, and you want to give it another. You do not need a new list for
            that. You can tell the list you already have to take one more item:

            ```python
            tools = ["search"]
            tools.append("calculator")
            print(tools)
            # ['search', 'calculator']
            ```

            Read `tools.append("calculator")` as "tools, add `calculator` to your end". The dot aims the
            instruction at that one list. An instruction that you give to a value with a dot is called a
            **method**, and `append` is one of the methods that every list has.

            Look at what is missing from that line: there is no `=`. `append` does not build a second list
            and hand it to you. It changes the list that is already there. Programmers say it changes the
            list **in place**.

            So what does `append` hand back? Make a guess, then find out:

            ```predict
            tools = ["search"]
            result = tools.append("weather")
            print(result)
            print(tools)
            ---
            `append` did its work on `tools`, which now has two items. It hands nothing back, and Python's
            value for "nothing" is `None`. So `result` is `None`.
            ```

            That `None` causes one of the most common list bugs. Here is what happens when someone writes
            `tools =` in front out of habit:

            ```python
            tools = ["search"]
            tools = tools.append("weather")
            print(tools)
            # None
            ```

            `append` did add the item. Then the `=` took what `append` handed back, which is `None`, and
            stored it under the name `tools`. The list can no longer be reached under that name.

            ```quiz
            Which line adds `"email"` to `tools` and leaves `tools` a list?
            - [x] `tools.append("email")` :: Yes. The method changes the list itself, so there is nothing to store.
            - [ ] `tools = tools.append("email")` :: The item is added, but then `tools` is set to what `append` hands back, and that is `None`.
            - [ ] `append(tools, "email")` :: `append` is a method, so it is written after the list and a dot. Written on its own, Python does not know the name `append`.
            ```

            The opposite of `append` is `pop()`. It removes the last item and, unlike `append`, it does hand
            that item back. Add and remove a few items to see the order:

            ```diagram
            {"type":"stack-queue","title":"append and pop on tools","mode":"stack","name":"tools","items":["search","calculator","weather"],"push":["email","browser"]}
            ```

            **Watch out:** when a check says your function returned `None`, look for an `=` in front of
            `append`.

            **In short:** `items.append(x)` changes the list itself and hands back `None`, so write it on a
            line of its own.
        ''',
        "title": "Fix add_tool",
        "difficulty": 0,
        "prompt": r'''
            An agent keeps a list of the tools it is allowed to use. Someone wrote a small function that
            adds one more tool to that list and hands the list back. It has a bug: whatever you pass in, it
            gives back `None` instead of the list.

            **Your job:** find the bug in `add_tool(tools, name)` and fix it. The code is already in the
            editor, and only one line needs to change.

            **What goes in**
            - `tools`: a list of tool names (strings), for example `["search"]`. It may be empty.
            - `name`: the name of the tool to add, for example `"calculator"`

            **What comes out**
            - the list, now with `name` as its last item

            **Rules**
            - An empty list works too. It comes back as a list that holds only `name`.

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
            "What does `append` hand back? The predict box in the lesson shows it.",
            "The item really is added to the list. The trouble is what the first line then stores under the name `tools`.",
            "On the first line of the function, keep the part that adds the item and remove the part that stores a result. The `return` line can stay as it is.",
        ],
    },
    {
        "id": "lists-s6",
        "lesson": r'''
            ## Checking whether something is in a list

            An agent is a program in which a model can ask for tools, such as a web search or a calculator.
            You decide which tools it may use, and you keep their names in a list. When the model asks for a
            tool, your program has a question to answer before anything runs: is that name in my list?

            Python lets you ask almost in plain English:

            ```python
            tools = ["search", "calculator"]
            print("search" in tools)
            # True
            print("email" in tools)
            # False
            ```

            Read `"search" in tools` as "is `"search"` one of the items of `tools`?". Python compares your
            value with the items one after another. When it finds an item that is equal, the answer is
            `True`. When it reaches the end without finding one, the answer is `False`. An empty list has
            nothing to compare with, so its answer is always `False`. That is not an error.

            The word `in` is called the **membership operator**, because it tests whether a value is a
            member of the list.

            "Equal" here means exactly equal, the same test that `==` makes. Pick the value that makes this
            program print `True`:

            ```fill
            models = ["gpt-4o", "claude", "llama"]
            print(___ in models)
            ---
            - [x] "claude" :: Right. This string is exactly equal to the second item of the list.
            - [ ] "Claude" :: A capital `C` makes this a different string from `"claude"`. No item is equal to it, so the program prints `False`.
            - [ ] "clau" :: The value must be equal to a whole item. Part of an item does not count, so the program prints `False`.
            ```

            ### Using the answer

            The `True` or `False` that `in` gives is a value like any other. You can store it under a name,
            hand it back from a function with `return`, or use it as the condition of an `if`:

            ```python
            tools = ["search", "calculator"]
            found = "calculator" in tools
            print(found)
            # True
            if "email" in tools:
                print("send the email")
            else:
                print("email is not allowed")
            # email is not allowed
            ```

            Now change one thing and watch the answer flip:

            ```try
            allowed = ["search", "calculator"]
            wanted = "Calculator"
            if wanted in allowed:
                print("run the tool")
            else:
                print("blocked")
            ---
            This prints `blocked` because of one capital letter. Change the value of `wanted` so that the
            program prints `run the tool`.
            ---
            allowed = ["search", "calculator"]
            wanted = "calculator"
            if wanted in allowed:
                print("run the tool")
            else:
                print("blocked")
            ---
            `in` says `True` only for an exact match, so the fix was in the value, not in the `if`.
            ```

            **Watch out:** the value goes on the left of `in` and the list goes on the right. Written the
            other way round, as in `tools in "search"`, Python stops with
            `TypeError: 'in <string>' requires string as left operand, not list`. The message is saying that
            the thing on the right of `in` was a string, not your list.

            **In short:** `x in items` is `True` when one of the items is exactly equal to `x`, and `False`
            when none is.
        ''',
        "title": "Is this tool allowed?",
        "difficulty": 0,
        "prompt": r'''
            An agent may only use the tools that you have approved. The names of the approved tools are kept
            in a list. Such a list is called an allow-list: the list of things that are allowed. Before the
            agent runs a tool, your code looks the tool's name up in that list.

            **Your job:** write `is_allowed(tools, name)`. It gives back `True` when `name` is one of the
            approved tools, and `False` when it is not.

            **What goes in**
            - `tools`: the allow-list, a list of tool names (strings), for example
              `["search", "calculator"]`. It may be empty.
            - `name`: the name of the tool that the agent wants to run (a string), for example `"search"`

            **What comes out**
            - `True` or `False`

            **Rules**
            - The name must match an item exactly. Capital letters count, so `"Search"` does not match
              `"search"`.
            - An empty list allows nothing, so the answer is `False`.
            - Give back the values `True` and `False` themselves, not the words in quotes. The checks tell
              the difference.

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
            "The lesson asks a list a yes-or-no question with one short word. Which word is it?",
            "That question already gives `True` or `False` as its answer. Your function does not need an `if` to turn the answer into `True` or `False`. It can hand the answer straight back.",
            "The body is one line. Start it with `return`, then write the question \"is this name one of the items of this list?\" with the membership operator. The name goes on the left of the operator and the list goes on the right.",
        ],
    },
    {
        "id": "lists-s4",
        "lesson": r'''
            ## Taking part of a list

            A search over your documents comes back with five results, the best match first. The model you
            pass them to has room for only two. You could read them one at a time with `results[0]` and
            `results[1]`, but then you hold two separate strings instead of a list, and you have to rewrite
            the code as soon as there is room for three.

            In the first step of this chapter you saw a colon between two indexes. It reads a whole run of
            items in one go:

            ```python
            results = ["A", "B", "C", "D", "E"]
            print(results[1:3])
            # ['B', 'C']
            print(results)
            # ['A', 'B', 'C', 'D', 'E']
            ```

            `results[1:3]` is a slice. It begins at index 1 and ends before index 3, so it takes the items
            at index 1 and index 2. The result is a new list, and `results` itself is left as it was.

            The first number is called the **start** and the second the **stop**. The item at the stop is
            not taken. There is a reason for that rule: stop minus start is the number of items you get.
            Here that is `3 - 1`, so 2 items.

            Drag the start and stop handles and watch which items are taken. (Leave the step buttons alone
            for now.)

            ```diagram
            {"type":"slice","title":"A slice of results","name":"results","items":["A","B","C","D","E"],"start":1,"stop":3}
            ```

            Pick the slice that prints `['C', 'D']`:

            ```fill
            results = ["A", "B", "C", "D", "E"]
            print(results[___])
            ---
            - [x] 2:4 :: Right. `C` is at index 2 and `D` is at index 3. The stop is one past the last item you want, so it is 4.
            - [ ] 2:3 :: The item at the stop is not taken, so this slice holds only index 2 and prints `['C']`.
            - [ ] 3:4 :: Counting starts at 0, so index 3 is `D`, not `C`. This prints `['D']`.
            ```

            ### Leaving a number out

            You may leave out either number. Without a start, the slice begins at the first item. Without a
            stop, it runs to the end of the list.

            ```python
            results = ["A", "B", "C", "D", "E"]
            print(results[:2])
            # ['A', 'B']
            print(results[3:])
            # ['D', 'E']
            print(results[-2:])
            # ['D', 'E']
            ```

            `results[:2]` is "the first 2 items". `results[3:]` is "everything from index 3 on". The last
            line uses the minus sign from the step "Latest message": a start of `-2` counts from the end, so
            `results[-2:]` is "the last 2 items".

            What if you ask for more items than the list has? An index past the end stopped the program in
            the first step. Make a guess for a slice, then find out:

            ```predict
            names = ["Ada", "Grace", "Alan"]
            print(names[:10])
            print(names[:0])
            ---
            A slice takes what is there and never stops the program. `names[:10]` asks for ten items, finds
            three, and gives all three. `names[:0]` stops before index 0, so it takes nothing and gives the
            empty list, `[]`.
            ```

            **Watch out:** the item at the stop index is not included, so `results[0:2]` gives two items,
            not three. When a slice comes back one item short, look at the stop.

            **In short:** `items[start:stop]` is a new list that runs from `start` up to, but not
            including, `stop`, and a number you leave out means "from the beginning" or "to the end".
        ''',
        "title": "First n chunks",
        "difficulty": 0,
        "prompt": r'''
            A model can read only a limited amount of text at once. An app that answers questions about
            your documents therefore does not send whole documents. It cuts them into pieces called chunks,
            puts the most useful chunks first, and sends only the first few.

            **Your job:** write `first_n(chunks, n)`. It gives back a new list with the first `n` items of
            `chunks`.

            **What goes in**
            - `chunks`: a list of pieces of text (strings), for example `["a", "b", "c", "d"]`
            - `n`: how many items to keep, a whole number that is 0 or more, for example `2`

            **What comes out**
            - a new list with the first `n` items, in their original order, for example `["a", "b"]`

            **Rules**
            - When the list has fewer than `n` items, give back all of them. That is not an error.
            - When `n` is 0, give back the empty list, `[]`.

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
            "Which tool from the lesson reads several items in one go and gives them to you as a new list?",
            "You want a slice that begins at the first item and stops before index `n`. The numbers in a slice do not have to be digits that you type. A name that holds a number works as well.",
            "The body is one line. Start it with `return`, then write `chunks` followed by a slice in square brackets. Leave the start out, so that the slice begins at the first item, and use the parameter `n` as the stop. You need no special case for a large `n` or for 0, because a slice copes with both.",
        ],
    },
    {
        "id": "lists-s5",
        "lesson": r'''
            ## Putting a list in order

            Three models answered the same question, and you wrote down how long each one took, in
            milliseconds: 340, 120 and 560. Which was the fastest? With three numbers you can see it at a
            glance. With three hundred you want Python to put them in order for you.

            ```python
            times = [340, 120, 560]
            ordered = sorted(times)
            print(ordered)
            # [120, 340, 560]
            print(times)
            # [340, 120, 560]
            ```

            `sorted(times)` builds a new list with the same items, arranged from smallest to largest, and
            hands it back. Look at the last line: `times` still has its old order. There are now two lists.

            ### Largest first

            To turn the order around, add `reverse=True` inside the brackets, after a comma:

            ```python
            times = [340, 120, 560]
            print(sorted(times, reverse=True))
            # [560, 340, 120]
            ```

            `reverse=True` is an argument that you pass by its name. The name says which setting you are
            switching on. An argument written as `name=value` is called a **keyword argument**.

            ```try
            lengths = [12, 40, 7]
            print(sorted(lengths))
            ---
            This prints the lengths from shortest to longest. Change the `sorted` call so that the longest
            comes first: `[40, 12, 7]`.
            ---
            lengths = [12, 40, 7]
            print(sorted(lengths, reverse=True))
            ---
            The keyword argument goes after the list, with a comma between the two.
            ```

            ### The other way: reorder the list itself

            Lists also have a method named `sort`. In the step "Fix add_tool" you met a method that changes
            its list in place. So what do you think `sort` hands back? Make a guess, then find out:

            ```predict
            times = [340, 120, 560]
            result = times.sort()
            print(result)
            print(times)
            ---
            `sort` behaves like `append`: it changes the list in place and hands back `None`. So `result`
            is `None`, and `times` itself is now in order. Its old order is gone.
            ```

            So you have two tools. `sorted(times)` gives you a new list and leaves the original alone.
            `times.sort()` reorders the original and gives you nothing. When another part of the program
            still needs the list in its old order, `sorted` is the one to use.

            **Watch out:** `best = times.sort()` stores `None` under the name `best`, because `sort` hands
            nothing back. In a function, a check then reports that you returned `None`. Write
            `best = sorted(times)` instead.

            **In short:** `sorted(items)` hands back a new list in order and leaves `items` alone, and
            `reverse=True` puts the largest first.
        ''',
        "title": "Best scores first",
        "difficulty": 0,
        "prompt": r'''
            A search tool gives every document a score that says how well it matches the question. A higher
            score means a better match. The scores arrive in no particular order, and you want to show the
            best ones first.

            **Your job:** write `best_first(scores)`. It gives back a new list with the same scores,
            ordered from highest to lowest.

            **What goes in**
            - `scores`: a list of numbers, for example `[0.2, 0.9, 0.5]`. It may be empty.

            **What comes out**
            - a new list with the same numbers, the highest first, for example `[0.9, 0.5, 0.2]`

            **Rules**
            - An empty list gives back an empty list, `[]`.
            - The list you were given must not change. After the call it still holds its items in their
              original order, because the code that called your function may still need them that way.

            **Examples**
            ```python
            best_first([0.2, 0.9, 0.5])   # returns [0.9, 0.5, 0.2]
            best_first([0.7])             # returns [0.7]
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
            "The lesson shows two ways to put a list in order. One changes the list it is given and one builds a new list. Which one does the second rule of the task ask for?",
            "Use the built-in function that hands back a new list in order. On its own it puts the smallest first, so it also needs the setting that turns the order around.",
            "The body is one line. Start it with `return`, then call the sorting function with two things inside its brackets: the list, and the keyword argument from the lesson that puts the largest first.",
        ],
    },
    {
        "id": "lists-7",
        "lesson": r'''
            ## Two names, one list

            Before you change a chat history, you make a backup: `backup = history`. Then you change the
            backup, and find that the original has changed as well.

            ```python
            history = [12, 40, 7]
            backup = history
            backup.append(99)
            print(history)
            # [12, 40, 7, 99]
            ```

            Remember that a variable is a label stuck on a value. `backup = history` does not make a
            second list. It sticks a second label on the list that is already there. Two names for one
            list are called **aliases**. A value that lives in the computer's memory is called an
            **object**, so here there is one list object with two names.

            You have asked `is None` before. In general, `a is b` is `True` when both names stand for the
            same object:

            ```python
            history = [12, 40, 7]
            backup = history
            print(backup is history)
            # True
            ```

            ### A real copy

            `history.copy()` makes a second list object with the same items. A change to the copy leaves
            the original alone:

            ```python
            history = [12, 40, 7]
            saved = history.copy()
            saved.append(5)
            print(history)
            # [12, 40, 7]
            print(saved)
            # [12, 40, 7, 5]
            ```

            `history + [5]` builds a new list too. Switch between the two ways of creating `backup`
            below, then run the statements and watch which list changes:

            ```diagram
            {"type":"alias-copy","title":"backup = history or backup = history.copy()","a":"history","b":"backup","items":[12,40,7],"append":99}
            ```

            ```predict
            a = [1, 2]
            b = a
            c = a.copy()
            b.append(3)
            c.append(4)
            print(a)
            print(c)
            print(a is b, a is c)
            ---
            `b` is a second name for the list `a`, so the 3 shows up in `a`. `c` is a separate list, so the 4 goes only into `c`. `a is b` is `True` because they are one object, and `a is c` is `False`.
            ```

            ### A parameter is an alias too

            When you pass a list to a function, the parameter becomes a second name for the caller's
            list. The function does not get a copy.

            ```quiz
            What does this program print?

            ~~~python
            def add_zero(numbers):
                numbers.append(0)

            mine = [5, 6]
            add_zero(mine)
            print(mine)
            ~~~
            - [x] `[5, 6, 0]` :: Right. Inside the function, `numbers` is a second name for the list that `mine` names. `append` changed that one list.
            - [ ] `[5, 6]` :: That would be the output if the function had received a copy. It receives the list itself.
            - [ ] `None` :: `add_zero` hands back `None`, but the program prints `mine`, not the result of the call.
            ```

            **Watch out:** a function that should hand back a changed list and leave the caller's list
            alone has to copy first, or build a new list with `+`.

            **In short:** `b = a` gives one list a second name, and `b = a.copy()` makes a second list.
        ''',
        "title": "Don't touch the caller's list",
        "difficulty": 1,
        "prompt": r'''
            An agent has a basic list of tools. For one request it needs one extra tool, and only for
            that request. The helper below returns the longer list, and that part works. But it also
            changes the list it was given, so the extra tool stays in the basic list and turns up in
            every later request.

            **Your job:** fix `with_tool(tools, name)` so that the list it is given stays as it was. The
            code is already in the editor.

            **What goes in**
            - `tools`: a list of tool names (strings), for example `["search"]`. It may be empty.
            - `name`: the name of the extra tool, a string, for example `"weather"`

            **What comes out**
            - a new list: every item of `tools`, in the same order, and then `name` at the end

            **Rules**
            - The list that was passed in is exactly the same after the call as before it.
            - The list that comes back is a different list object from `tools`.

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
            "Look at the first line of the body. Does it make a second list, or a second name for the same list?",
            "The function should add the tool to a real copy, so that the list it was given never changes.",
            "Change the first line so that `new_tools` gets a copy of the list, made with the list method from the lesson. The other two lines can stay as they are.",
        ],
    },
    {
        "id": "lists-8",
        "lesson": r'''
            ## Finding the method you need

            You have used `append`, `pop`, `sort` and `copy`. Lists have about a dozen methods, and you do
            not need to learn them by heart. When you need one, you look it up. The Python tutorial has a
            short section, "More on Lists", that describes every list method in a sentence or two.

            Here are two of them, to show what you will find there:

            ```python
            calls = ["search", "search", "weather"]
            print(calls.index("weather"))
            # 2
            calls.extend(["email", "search"])
            print(calls)
            # ['search', 'search', 'weather', 'email', 'search']
            ```

            `calls.index(x)` hands back the index of the first item that is equal to `x`.
            `calls.extend(other)` adds every item of another list to the end.

            A good way to read such a section: skim the names first, read the description of each method
            that sounds useful, then try it out.

            As you read, sort each method into one of two kinds. Some methods change the list and hand
            back `None`. Others answer a question: they hand back a value and leave the list alone.

            ```match
            `calls.append("x")` :: changes the list and hands back `None`
            `calls.index("x")` :: hands back a position and changes nothing
            `calls.pop()` :: changes the list and hands back the item it removed
            ```

            ```quiz
            `tools` is `["a", "b"]`. What is it after `tools.extend(["c", "d"])`?
            - [x] `["a", "b", "c", "d"]` :: Right. `extend` adds each item of the other list, one by one.
            - [ ] `["a", "b", ["c", "d"]]` :: That is what `append` would do: it adds its argument as one single item, here a whole list.
            - [ ] `["c", "d"]` :: `extend` adds to the end. The items that were there stay.
            ```

            For this step, open the section that is linked in the task. Find the method that tells you
            how many times a value appears in a list. It is one of the methods that answer a question.

            **Watch out:** `index` stops with `ValueError: list.index(x): x not in list` when no item is
            equal to `x`.

            **In short:** the tutorial lists every list method, and for each one it matters whether it
            changes the list or hands back an answer.
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
            An agent writes down the name of every tool it calls, in order. From that log you want to
            know how often one tool was used.

            **Your job:** write `call_count(calls, name)` so that it gives back the number of times the
            tool appears in the log.

            **What goes in**
            - `calls`: a list of tool names (strings), for example `["search", "weather", "search"]`. It
              may be empty.
            - `name`: the tool to count, a string

            **What comes out**
            - a whole number: how many items of `calls` are exactly equal to `name`

            **Rules**
            - A tool that never appears gives `0`.
            - The comparison is exact, and capital letters matter.
            - The list stays as it was.
            - Lists have a method that does the counting. It is in the tutorial section linked above, and
              no loop is needed.

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
            "Read the list methods in the linked tutorial section. One of them counts.",
            "The method is called on the list with a dot, takes the value to look for, and hands back a number.",
            "Write one `return` line: the list, a dot, the counting method from the tutorial, and `name` as its argument.",
        ],
    },
    {
        "id": "lists-1",
        "lesson": r'''
            ## One step straight after another

            A search hands back a list of scores, and you want the best two. That is two steps you
            already know: sort the scores with the highest first, then take the first two.

            ```python
            scores = [0.2, 0.9, 0.5, 0.7]
            ranked = sorted(scores, reverse=True)
            print(ranked)
            # [0.9, 0.7, 0.5, 0.2]
            print(ranked[:2])
            # [0.9, 0.7]
            ```

            The name `ranked` exists only to carry the list from the first step to the second. You can
            leave it out and apply the second step straight to the result of the first:

            ```python
            scores = [0.2, 0.9, 0.5, 0.7]
            print(sorted(scores)[:1])
            # [0.2]
            ```

            Python works out `sorted(scores)` first, gets a list, and applies `[:1]` to that list.
            Writing one operation directly after another is called **chaining**. You did it before with
            string methods, as in `text.strip().lower()`.

            ```predict
            words = ["pear", "fig", "apple"]
            print(sorted(words)[0])
            print(sorted(words)[-1])
            print(words)
            ---
            Sorted by the alphabet, the list is apple, fig, pear. Index 0 of that is `apple` and index -1 is `pear`. `sorted` built a new list each time, so `words` is still in its original order.
            ```

            Two facts make this pattern safe. `sorted` builds a new list and a slice builds a new list,
            so the original never changes. And a slice that asks for more items than there are gives
            back all of them, without an error.

            ```quiz
            `nums` is `[3, 1, 2]`. What is `sorted(nums)[:5]`?
            - [x] `[1, 2, 3]` :: Right. The slice asks for up to 5 items, the list has 3, so all 3 come back in sorted order.
            - [ ] An `IndexError` :: A single index past the end raises an error. A slice never does. It stops at the end of the list.
            - [ ] `[3, 1, 2]` :: The slice is applied to the result of `sorted`, which is a new list in sorted order.
            ```

            **Watch out:** this works with `sorted()`, not with `.sort()`. The method `sort` hands back
            `None`, so `scores.sort()[:2]` stops with
            `TypeError: 'NoneType' object is not subscriptable`.

            **In short:** an operation can be applied directly to the result of the one before it, as in
            `sorted(items)[:n]`.
        ''',
        "hints": [
            "Two list tools from this chapter are needed: one that sorts into a new list, and one that takes the first few items.",
            "Sort the scores from the highest to the lowest without touching the original, then keep only the first `k` of them.",
            "Write one `return` line. Call the built-in that hands back a new sorted list, with the keyword argument that puts the largest value first. Directly after the call, add a slice that takes the first `k` items.",
        ],
        "title": "Top k scores",
        "difficulty": 1,
        "prompt": r'''
            A retriever is the part of a RAG app that looks up documents. For each document it hands back
            a similarity score, a number that says how well the document fits the question. You only want
            the best few scores.

            **Your job:** write `top_k(scores, k)` so that it gives back the `k` highest scores.

            **What goes in**
            - `scores`: a list of numbers, for example `[0.2, 0.9, 0.5, 0.7]`
            - `k`: the number of scores to keep, a whole number that is 0 or more, for example `2`

            **What comes out**
            - a new list with the `k` highest scores, the highest first: `[0.9, 0.7]` for the example
              values

            **Rules**
            - When `k` is larger than the number of scores, all of them come back, the highest first.
            - When `k` is `0`, the result is `[]`.
            - Equal scores are all kept. Each one counts as a score of its own.
            - The list that was passed in stays as it was.

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
            ## Take it out, put it in somewhere else

            A model picker shows the models that were used most recently at the top. When a model is
            used, it should jump to the front of the list. That takes two moves: take the model out of
            the place where it is, and put it in at the front.

            `remove(x)` deletes the first item that is equal to `x`. The items after it move one place to
            the left.

            ```python
            models = ["gpt-4o", "claude", "llama"]
            models.remove("claude")
            print(models)
            # ['gpt-4o', 'llama']
            ```

            `insert(i, x)` puts `x` at index `i`. The items from that index on move one place to the
            right, so `insert(0, x)` puts `x` at the front.

            ```python
            models = ["gpt-4o", "llama"]
            models.insert(0, "claude")
            print(models)
            # ['claude', 'gpt-4o', 'llama']
            ```

            Both methods change the list in place, and both hand back `None`.

            ```order
            queue = ["a", "b", "c"]
            queue.remove("c")
            queue.insert(0, "c")
            print(queue)
            ---
            `remove` takes `"c"` out of the end, and `insert` puts it in at the front, which gives `['c', 'a', 'b']`. The other way round does not work: after the insert the list has two `"c"` items, and `remove` deletes the first of them, which is the one that was just put in.
            ```

            ### When the value may not be there

            `remove(x)` stops with `ValueError: list.remove(x): x not in list` when no item is equal to
            `x`. When the value may be missing, ask with `in` first:

            ```python
            models = ["claude", "gpt-4o"]
            if "gemini" in models:
                models.remove("gemini")
            print(models)
            # ['claude', 'gpt-4o']
            ```

            A function that changes a list it was given has a **side effect**: after the call, the
            caller's list is different. Sometimes that is exactly what a task wants. "Change the list in
            place and return `None`" asks for a side effect and for no `return` line.

            ```quiz
            What does `print(models.insert(0, "x"))` show?
            - [x] `None` :: Right. `insert` changes the list and hands back `None`, and `print` shows what was handed back.
            - [ ] The list with `"x"` at the front :: The list was changed, but the call does not hand it back. To see it, print `models` on a line of its own.
            - [ ] `0` :: The index is an argument of the call. It is not what the call hands back.
            ```

            **Watch out:** `remove` only deletes the first item that matches. Later copies of the same
            value stay in the list.

            **In short:** `items.remove(x)` takes the first `x` out and `items.insert(i, x)` puts `x` in
            at index `i`. Both change the list itself.
        ''',
        "hints": [
            "Three tools are needed: the `in` operator, the method that takes an item out, and the method that puts an item in at a position.",
            "When the name is already in the list, take it out first. In both cases it then goes in at index 0. Change the list itself, and hand nothing back.",
            "Write an `if` that asks whether the name is in the list, and take the name out inside that block. After the `if`, at its indentation, put the name in at index 0. The function needs no `return` line.",
        ],
        "title": "Move to front",
        "difficulty": 1,
        "prompt": r'''
            A model picker keeps the models that were used most recently at the top of its list. When a
            model is used, it moves to the front.

            **Your job:** write `move_to_front(models, name)`. It changes the list that it is given, and
            it hands nothing back.

            **What goes in**
            - `models`: a list of model names (strings), for example `["gpt-4o", "claude", "llama"]`
            - `name`: the model that was just used, a string

            **What comes out**
            - nothing. The function has no `return` value, so a call gives `None`. Its result is the
              changed list. (This is called modifying the list in place.)

            **Rules**
            - When `name` is already in the list, it moves to index 0. Only its first occurrence moves.
              Later copies of the same name stay where they are.
            - When `name` is already first, the list ends up unchanged.
            - When `name` is not in the list, it is put in at index 0.
            - The other items keep their order.

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
            "Slices do the work here, together with a look at the role of the first message, which is the first item of the first tuple.",
            "Split the history into a head, which is the system message or nothing, and the rest. Take the last `n` messages of the rest, and join the head and that tail with `+`.",
            "When the list is not empty and its first message has the role `\"system\"`, the head is a slice that holds that one message, and the rest is everything after it. Otherwise the head is an empty list and the rest is the whole list. Take the last `n` items of the rest with a negative slice. Be careful when `n` is 0: a slice from `-0` is the whole list, so in that case the tail has to be an empty list. Hand back the head joined to the tail.",
        ],
        "title": "Trim chat history",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A model can only read a limited number of tokens, so a chat app sends only the most recent
            messages of a long conversation. There is one exception. A conversation often starts with a
            system message, which holds the instructions for the model, and that message must never be
            dropped.

            Each message is a tuple of two strings, the role and the text, for example `("user", "hi")`.

            **Your job:** write `trim_history(messages, n)` so that it gives back the trimmed history.

            **What goes in**
            - `messages`: a list of `(role, text)` tuples, the oldest first. It may be empty.
            - `n`: the number of recent messages to keep, a whole number that is 0 or more

            **What comes out**
            - a new list of messages: the same tuples, in the same order

            **Rules**
            - When the first message has the role `"system"`, it is always kept, at the front. After it
              come the last `n` of the other messages.
            - A `"system"` message that is not the first message is treated like any other message.
            - In every other case, the result is the last `n` messages.
            - When there are fewer than `n` messages to choose from, all of them are kept.
            - With `n` equal to `0`, no ordinary message is kept. Only a system message at the front
              stays.
            - An empty list gives `[]`.
            - The list that was passed in stays as it was, and the result is always a new list, even when
              every message is kept.

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
            "A slice gives you a window on the list. Be careful: a negative start in a slice counts from the end of the list.",
            "The window runs from `center` minus `radius` to `center` plus `radius`, both included. When the start would be below 0, use 0. The stop may go past the end of the list without harm.",
            "Work out the start as the center minus the radius, and raise it to 0 when it is negative. The stop of the slice is one more than the center plus the radius, because a slice leaves its stop out. Hand back that slice of `words`.",
        ],
        "title": "Context around a hit",
        "difficulty": 2,
        "prompt": r'''
            A search has found a matching word inside a document. To show the match in its context, you
            display a few words on each side of it.

            **Your job:** write `around(words, center, radius)` so that it gives back the matching word
            together with its neighbours.

            **What goes in**
            - `words`: a list of strings, for example `["a", "b", "c", "d", "e", "f"]`
            - `center`: the index of the matching word. It is always a valid index.
            - `radius`: the number of words to show on each side, a whole number that is 0 or more

            **What comes out**
            - a new list: the word at `center`, with up to `radius` words before it and up to `radius`
              words after it, in their original order

            **Rules**
            - Near the start or the end of the list the window is shorter. It never wraps round to the
              other end of the list.
            - A `radius` of `0` gives only the word at `center`.
            - When the radius covers the whole list, all the words come back.
            - The list that was passed in stays as it was, and the result is a new list.

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
            "There are two parts: a slice for the page, and a division that rounds up for the number of pages.",
            "The number of pages is the number of items divided by `per_page`, rounded up. Page `p`, counted from 1, starts at the index `(p - 1)` times `per_page`. A page outside the range from 1 to `total_pages` is empty.",
            "For the page count, add one less than `per_page` to the number of items, and floor-divide the sum by `per_page`. When the page is below 1 or above that count, hand back an empty list and the count. Otherwise work out the start index of the page, slice `per_page` items from there, and hand back that slice and the count.",
        ],
        "title": "Paginate results",
        "difficulty": 3,
        "prompt": r'''
            A search API does not send all its results at once. It shows them page by page, which is
            called pagination. To show one page, you need the items on that page and the total number of
            pages.

            **Your job:** write `get_page(items, page, per_page)` so that it gives back both.

            **What goes in**
            - `items`: the full list of results, for example `["r1", "r2", "r3", "r4", "r5"]`
            - `page`: the page to show, a whole number. The first page is number 1.
            - `per_page`: the number of items on one page, a whole number that is 1 or more

            **What comes out**
            - a tuple `(page_items, total_pages)`:
              - `page_items`: a new list with the items on that page, in order
              - `total_pages`: a whole number, the number of pages needed to show every item

            **Rules**
            - A last page that is only partly filled still counts as a page: 5 items at 2 per page are
              3 pages.
            - When the items fit exactly, there is no extra empty page: 4 items at 2 per page are 2 pages.
            - No items means `0` pages.
            - For a `page` outside the range from 1 to `total_pages`, for example `0`, `-1` or a number
              that is too big, `page_items` is `[]`. `total_pages` is still the real count.
            - The list that was passed in stays as it was.

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
            "You need slices for the two ends, `len` for the count, an f-string for the marker, and `+` to join lists.",
            "When the list is short enough, at most `2 * keep` items, hand back a copy. Otherwise hand back the first `keep` items, one marker that says how many were left out, and the last `keep` items.",
            "Start with the short case: compare the length with twice `keep`, and hand back a copy of the list. Then count the hidden messages, which is the length minus twice `keep`. The head is a slice of the first `keep` items. The tail is the last `keep` items, except when `keep` is 0: a slice from `-0` is the whole list, so then the tail is an empty list. Hand back the head, a list that holds only the marker, and the tail, joined with `+`.",
        ],
        "title": "Compact a long conversation",
        "difficulty": 3,
        "prompt": r'''
            A long chat does not fit into a small panel. To show it there, you keep only the start and
            the end of the conversation and replace the middle with a short marker that says how many
            messages are hidden.

            **Your job:** write `compact(messages, keep)` so that it gives back the shortened list.

            **What goes in**
            - `messages`: a list of strings, for example `["m1", "m2", "m3"]`. It may be empty.
            - `keep`: the number of messages to keep at each end, a whole number that is 0 or more

            **What comes out**
            - a new list of strings

            **Rules**
            - When there are at most `2 * keep` messages, nothing would be hidden. The result is then a
              copy of the whole list: the same contents in a new list object.
            - Otherwise the result is the first `keep` messages, then one marker string
              `"[<hidden> messages hidden]"`, then the last `keep` messages. `<hidden>` is the number of
              messages that were left out.
            - The marker always says `messages`, even for one: `"[1 messages hidden]"`.
            - With `keep` equal to `0` and a list that is not empty, the result is only the marker.
            - An empty list gives `[]`.
            - The list that was passed in stays as it was.

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
