TOPIC = {
    "id": "generators",
    "title": "Iterators & Generators",
    "track": "production-python",
    "order": 4,
    "requires": ["loops", "functions"],
    "summary": """
        Producing values lazily with yield and generator expressions, batching and
        streaming data (like LLM token streams), itertools, the iterator protocol
        and yield from.
    """,
    "concepts": ["yield", "generator functions", "lazy evaluation", "generator expressions",
                 "itertools.islice", "itertools.chain", "itertools.groupby",
                 "__iter__ / __next__", "StopIteration", "yield from"],
}

LESSON = r'''
## Chapter notes: iterators & generators

**Generator function** = a function with `yield` in it. Calling it runs **nothing**; it
returns a *generator object*. Each `next(gen)` runs the body up to the next `yield`, hands
out that value and **pauses** (all local variables are remembered).

```python
def count_up_to(n):
    i = 1
    while i <= n:
        yield i
        i += 1

print(list(count_up_to(3)))
```

| thing | meaning |
| --- | --- |
| `yield x` | hand out `x`, pause here |
| `return` in a generator | stop (no more values) |
| `next(gen)` | get the next value; raises `StopIteration` when done |
| `next(gen, default)` | same, but returns `default` instead of raising |
| `for x in gen` / `list(gen)` | pull every value; stop quietly at the end |
| `(expr for x in items)` | *generator expression*: lazy, round brackets |
| `iter(items)` | turn a list/str/dict into an *iterator* you can `next()` |
| `itertools.islice(it, n)` | take at most `n` items, lazily |
| `yield from other()` | pass along everything another generator yields |

**Lazy** = values are computed only when someone asks. Good for streams (LLM token
deltas), huge files and infinite sequences (`itertools.count()`).

**Iterator protocol** (what `for` really uses): a class with `__iter__` returning `self`
and `__next__` returning the next value or raising `StopIteration`.

## Gotchas

- A generator is **one-shot**: the second `list(gen)` is `[]`. Call the function again.
- `return` instead of `yield` in a loop stops after the first item.
- `print(gen)` shows `<generator object ...>`, not the values.
- `[x for x in xs]` builds a list now; `(x for x in xs)` builds nothing until asked.
- `max()`/`next()` on an empty iterator raise; pass `default=` / a second argument.
'''


EXERCISES = [
    {
        "id": "generators-s1",
        "title": "Countdown",
        "lesson": r'''
            ## A function that hands things out one at a time

            Picture a vending machine. A normal function is a machine that dumps **everything** on
            the floor at once and switches off (`return`). A **generator** is a machine that hands
            you **one** item each time you press the button, then waits for the next press.

            The keyword that hands out one item is `yield`.

            ```python
            def three_colours():
                yield "red"
                yield "green"
                yield "blue"

            for colour in three_colours():
                print(colour)
            ```

            A `for` loop keeps "pressing the button" until the machine is empty.

            `yield` works inside loops too - that's where it shines:

            ```python
            def count_up_to(n):
                i = 1
                while i <= n:
                    yield i
                    i += 1

            for x in count_up_to(3):
                print(x)
            ```

            The real names: a function that contains `yield` is a **generator function**. Calling it
            gives you a **generator**, and each value it hands out is *yielded*.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            def countdown(n):
                while n > 0:
                    yield n
                    n -= 1

            for x in countdown(3):
                print(x)
            print("liftoff")
        ''',
        "solution": r'''
            3
            2
            1
            liftoff
        ''',
        "explanation": r'''
            Each time the loop asks for a value, `countdown` runs until it hits `yield`, hands
            out `n`, and pauses. On the next request it continues with `n -= 1`. When `n`
            reaches `0` the `while` ends, the generator is finished, and the `for` loop stops.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Every `yield` hands one value to the `for` loop, which prints it.",
            "`n` starts at 3 and goes down by 1 after each yield; the loop inside stops when `n` is no longer above 0.",
            "Write the yielded values one per line in order, then the line printed after the loop.",
        ],
    },
    {
        "id": "generators-s2",
        "title": "Watch it pause",
        "lesson": r'''
            ## Pause and resume

            Remember the vending machine? Here is the surprising part: when you **call** a generator
            function, the machine is only switched on - no code inside runs yet. You get a
            *generator object* back and nothing else happens.

            To press the button by hand, use the built-in `next()`. Each `next()` runs the body from
            where it last stopped, up to the next `yield`, hands out that value, and **pauses** there.
            All the local variables are remembered while it waits.

            ```python
            def steps():
                print("start")
                yield "first"
                print("resumed")
                yield "second"

            gen = steps()
            print("nothing ran yet")
            print(next(gen))
            print(next(gen))
            ```

            Run it and follow the order of the lines carefully: `start` only appears after the first
            `next(gen)`.

            Vocabulary: the generator is **suspended** at a `yield` and **resumed** by `next()`.
            A `for` loop is really just calling `next()` for you, over and over.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints. Careful: think about **when**
            each line inside `steps` actually runs.
        ''',
        "code": r'''
            def steps():
                print("A")
                yield 1
                print("B")
                yield 2

            gen = steps()
            print(next(gen))
            print("C")
            print(next(gen))
        ''',
        "solution": r'''
            A
            1
            C
            B
            2
        ''',
        "explanation": r'''
            `gen = steps()` runs nothing. The first `next(gen)` runs the body until the first
            `yield`: it prints `A`, then hands out `1`, which gets printed. Then `C` is
            printed outside. The second `next(gen)` resumes right after the first `yield`:
            it prints `B` and hands out `2`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Creating the generator with `steps()` does not run any of its lines.",
            "Each `next(gen)` runs from where it paused up to the next `yield`, including any prints on the way, and then returns the yielded value.",
            "Go line by line: first `next` -> prints inside, then the value; then `C`; second `next` -> prints inside, then the value. Five lines in total.",
        ],
    },
    {
        "id": "generators-s6",
        "title": "Used up",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Used up for good

            A generator is like a tube of toothpaste: once you have squeezed it all out, it is empty.
            There is no refill - you need a **new** tube (call the function again).

            `list(gen)` squeezes out every remaining value into a list. After that, the generator is
            *exhausted*.

            ```python
            def two():
                yield 1
                yield 2

            gen = two()
            print(list(gen))
            print(list(gen))      # already empty
            print(list(two()))    # a fresh generator
            ```

            What happens if you call `next()` on an empty generator? Python raises an error called
            `StopIteration` - that is the signal "no more values". A `for` loop and `list()` catch
            that signal for you and just stop quietly.

            ```python
            def two():
                yield 1
                yield 2

            gen = two()
            print(next(gen), next(gen))
            try:
                next(gen)
            except StopIteration:
                print("no more values")
            ```

            Watch out: `print(gen)` does **not** show the values - it shows something like
            `<generator object two at 0x...>`.
        ''',
        "prompt": r'''
            Read the code and type exactly what it prints. Think about what is **left** in the
            generator after each line.
        ''',
        "code": r'''
            def tokens():
                yield "Hel"
                yield "lo"

            gen = tokens()
            print(next(gen))
            print(list(gen))
            print(list(gen))
            print(list(tokens()))
        ''',
        "solution": r'''
            Hel
            ['lo']
            []
            ['Hel', 'lo']
        ''',
        "explanation": r'''
            `next(gen)` takes the first value, `"Hel"`. `list(gen)` then collects only what is
            **left**: `['lo']`. After that the generator is exhausted, so the next `list(gen)` is
            `[]`. Calling `tokens()` again creates a brand-new generator that starts from the top.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "A generator remembers how far it got - values already taken are gone.",
            "After `next(gen)` took the first value, `list(gen)` only gets the rest; then nothing is left. `tokens()` makes a fresh generator.",
            "Write four lines: the first value as plain text, then a one-item list, then an empty list, then a two-item list - lists printed with quotes like `['a']`.",
        ],
    },
    {
        "id": "generators-s3",
        "title": "Yield the even numbers",
        "lesson": r'''
            ## Yield only some items

            A generator can sit on a conveyor belt with a quality checker: items roll past, and it
            hands out only the ones that pass. You combine three things you already know - a `for`
            loop, an `if`, and the new `yield`.

            ```python
            def long_words(words):
                for w in words:
                    if len(w) > 3:
                        yield w

            print(list(long_words(["hi", "hello", "yo", "model"])))
            ```

            Items that fail the `if` are simply skipped - the loop moves on, nothing is handed out.
            If nothing passes, the generator yields nothing at all and `list()` gives `[]`.

            Unlike building a result list with `.append()`, there is no list to create or return:
            each matching item is handed out the moment it is found. This is called a
            **filtering generator**, and it is *lazy* - it only checks the next item when someone
            asks for one.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Filter a list of numbers lazily, handing out the matching ones one at a time.

            **Write:** complete the generator `evens(numbers)` by replacing the `___`

            - `numbers`: a list of `int`s, e.g. `[1, 2, 3, 4]`
            - **Yields:** each even number from `numbers`, in their original order

            **Rules**
            - The function must use `yield` (it is a *generator function*).
            - If there are no even numbers, it yields nothing.

            **Examples**
            ```python
            list(evens([1, 2, 3, 4, 6]))   # [2, 4, 6]
            list(evens([1, 3, 5]))         # []
            ```
        ''',
        "starter": r'''
            def evens(numbers):
                for n in numbers:
                    if n % 2 == 0:
                        ___
        ''',
        "tests": r'''
            import inspect
            from solution import evens

            def test_is_a_generator_function_using_yield():
                assert inspect.isgeneratorfunction(evens), "evens must use yield"

            def test_yields_only_even_numbers_in_order():
                got = list(evens([1, 2, 3, 4, 6]))
                assert got == [2, 4, 6], f"got {got!r}"

            def test_no_even_numbers_yields_nothing():
                assert list(evens([1, 3, 5])) == []
        ''',
        "solution": r'''
            def evens(numbers):
                for n in numbers:
                    if n % 2 == 0:
                        yield n
        ''',
        "hints": [
            "A generator hands out values with a special keyword instead of `return`.",
            "Inside the `if`, hand out the current number `n` and let the loop continue.",
            "Replace `___` with `yield n`.",
        ],
    },
    {
        "id": "generators-s4",
        "title": "Fix the bug: only one line",
        "lesson": r'''
            ## `return` vs `yield`

            Two different doors out of a function:

            - `return` is the **exit** door. The function is over, for good. Any loop inside it stops.
            - `yield` is a **serving hatch**. A value goes out, but the function stays alive and
              continues from the same spot next time.

            ```python
            def first_only(items):
                for x in items:
                    return x          # leaves on the first item

            def every_one(items):
                for x in items:
                    yield x           # hands out each item

            print(first_only(["a", "b", "c"]))
            print(list(every_one(["a", "b", "c"])))
            ```

            Watch out: this is one of the most common generator bugs. If a function is supposed to
            hand out *every* matching item but you only ever get one, look for a `return` sitting
            inside the loop.

            (Inside a generator, a bare `return` is allowed - it just means "stop now, no more
            values".)
        ''',
        "difficulty": 0,
        "prompt": r'''
            Skip blank lines in a document before it is processed. Right now this function only
            ever gives you the first non-blank line.

            **Write:** fix the bug in `non_empty(lines)`

            - `lines`: a list of strings, e.g. `["hi", "", "  ", "there"]`
            - **Yields:** **every** line that is not blank, unchanged, in order

            **Rules**
            - It must be a *generator function* (it uses `yield`).
            - A line is blank if it is empty or contains only whitespace (`""`, `"  "`).
            - If all lines are blank, it yields nothing.

            **Examples**
            ```python
            list(non_empty(["hi", "", "  ", "there"]))   # ["hi", "there"]
            list(non_empty(["", " "]))                  # []
            ```
        ''',
        "starter": r'''
            def non_empty(lines):
                for line in lines:
                    if line.strip():
                        return line
        ''',
        "tests": r'''
            import inspect
            from solution import non_empty

            def test_is_a_generator_function_using_yield():
                assert inspect.isgeneratorfunction(non_empty), "non_empty must be a generator"

            def test_yields_every_non_blank_line():
                got = list(non_empty(["hi", "", "  ", "there"]))
                assert got == ["hi", "there"], f"got {got!r}"

            def test_all_blank_lines_yield_nothing():
                assert list(non_empty(["", " "])) == []
        ''',
        "solution": r'''
            def non_empty(lines):
                for line in lines:
                    if line.strip():
                        yield line
        ''',
        "hints": [
            "What happens to a function the moment it reaches `return`?",
            "`return` ends the function for good. You need the keyword that hands out a value and then keeps going.",
            "Change `return line` to `yield line`.",
        ],
    },
    {
        "id": "generators-s5",
        "title": "Stream the words",
        "lesson": r'''
            ## Streaming, the way chat apps do it

            When you use a chatbot, the answer appears word by word instead of all at the end. The
            server *streams* the reply: it sends each piece as soon as the model produces it. A
            generator is the natural Python shape for a stream - the consumer handles each piece the
            moment it is yielded.

            ```python
            def stream_letters(word):
                for letter in word:
                    yield letter

            for piece in stream_letters("hey"):
                print(piece, end="|")
            print()
            ```

            `print(..., end="|")` prints without a newline, so the pieces land on one line like a
            streaming reply.

            The consumer doesn't care whether it gets a list or a generator - a `for` loop works on
            both. Things you can loop over are called **iterables**; a generator is one kind of
            iterable that computes its items on demand.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Simulate a model streaming its reply, one word at a time.

            **Write:** `stream_words(text)` - a **generator function** (it uses `yield`)

            - `text`: a string, e.g. `"Hello from the model"`
            - **Yields:** the words of `text`, one string per `yield`, in order

            **Rules**
            - The function must use `yield` (calling it gives a generator, not a list).
            - Words are separated by whitespace; several spaces in a row count as one gap.
            - Empty text yields nothing.

            **Examples**
            ```python
            gen = stream_words("Hello from the model")
            next(gen)                                  # "Hello"
            next(gen)                                  # "from"
            list(stream_words("RAG  needs   retrieval"))  # ["RAG", "needs", "retrieval"]
            list(stream_words(""))                     # []
            ```
        ''',
        "starter": r'''
            def stream_words(text):
                ...
        ''',
        "tests": r'''
            import inspect
            from solution import stream_words

            def test_is_a_generator_function_using_yield():
                assert inspect.isgeneratorfunction(stream_words), "use yield"

            def test_next_gives_words_in_order():
                gen = stream_words("Hello from the model")
                assert next(gen) == "Hello"
                assert next(gen) == "from"

            def test_multiple_spaces_count_as_one_gap():
                got = list(stream_words("RAG  needs   retrieval"))
                assert got == ["RAG", "needs", "retrieval"], f"got {got!r}"

            def test_empty_text_yields_nothing():
                assert list(stream_words("")) == []
        ''',
        "solution": r'''
            def stream_words(text):
                for word in text.split():
                    yield word
        ''',
        "hints": [
            "Loop over the words and hand each one out with `yield`.",
            "`text.split()` gives you the list of words; a `for` loop visits them one by one.",
            "1) Write a `for` loop over `text.split()`. 2) Inside it, `yield` the current word.",
        ],
    },
    {
        "id": "generators-1",
        "title": "Fake token stream",
        "lesson": r'''
            ## Walking in steps

            To cut a long string into equal pieces, you need the start of each piece: `0`, then
            `size`, then `2 * size`... Like cutting a ribbon every 4 cm with a ruler.

            `range` takes an optional third argument, the **step**: how far to jump each time.

            ```python
            print(list(range(0, 10, 4)))

            text = "streaming"
            for start in range(0, len(text), 4):
                print(start, text[start:start + 4])
            ```

            Two things make this safe:

            - `range(0, len(text), size)` stops **before** `len(text)`, so you never start a piece
              past the end, and for an empty string the range is empty.
            - Slicing past the end of a string is fine: `"ing"[0:4]` just gives `"ing"`.

            In LLM APIs the small pieces a streaming reply arrives in are called **deltas** (the
            "difference" since the last piece). Joining all deltas gives back the full text.
        ''',
        "hints": [
            "A function with `yield` in it is a generator function; each `yield` hands out one piece.",
            "Walk through the start positions 0, size, 2*size, ... and yield a slice of `size` characters starting at each one.",
            "1) Use `range` with three arguments (start, stop, step) to get the start positions up to `len(text)`. 2) For each start, yield the slice from `start` to `start + size`. Slicing past the end is safe, and for empty text the range is empty.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Simulate a model streaming its answer in small pieces (called *deltas*).

            **Write:** `stream_deltas(text, size)` - a **generator function** (it uses `yield`)

            - `text`: the full answer as a string, e.g. `"Hello world"`
            - `size`: how many characters per piece, an `int` of at least 1, e.g. `4`
            - **Yields:** consecutive pieces of `text` (strings), in order, one per `yield`

            **Rules**
            - The function must use `yield`.
            - Every piece is exactly `size` characters long, except the last one, which may be
              shorter (whatever is left).
            - If the length of `text` is an exact multiple of `size`, there is no extra empty piece.
            - Empty text yields nothing.

            **Examples**
            ```python
            list(stream_deltas("Hello world", 4))   # ["Hell", "o wo", "rld"]
            list(stream_deltas("abcdef", 3))        # ["abc", "def"]
            list(stream_deltas("", 3))              # []
            gen = stream_deltas("abc", 2)
            next(gen)                               # "ab"
            next(gen)                               # "c"
            ```
        ''',
        "starter": r'''
            def stream_deltas(text, size):
                ...
        ''',
        "tests": r'''
            import inspect
            from solution import stream_deltas

            def test_is_a_generator_function_using_yield():
                assert inspect.isgeneratorfunction(stream_deltas), "use yield - stream_deltas must be a generator function"

            def test_pieces_of_size_with_shorter_last_piece():
                got = list(stream_deltas("Hello world", 4))
                assert got == ["Hell", "o wo", "rld"], f"got {got!r}"

            def test_exact_multiple_has_no_empty_piece():
                got = list(stream_deltas("abcdef", 3))
                assert got == ["abc", "def"], f"got {got!r}"

            def test_empty_text_yields_nothing():
                assert list(stream_deltas("", 3)) == []

            def test_next_gives_pieces_one_at_a_time():
                gen = stream_deltas("abc", 2)
                assert next(gen) == "ab" and next(gen) == "c"
        ''',
        "solution": r'''
            def stream_deltas(text, size):
                for start in range(0, len(text), size):
                    yield text[start:start + size]
        ''',
    },
    {
        "id": "generators-2",
        "title": "Count without a list",
        "lesson": r'''
            ## Generator expressions

            You know list comprehensions: `[n * n for n in nums]` builds a whole list right away.
            Swap the square brackets for round ones and you get a **generator expression**: the
            same recipe, but cooked one portion at a time, only when someone asks.

            ```python
            nums = [1, 2, 3, 4]
            squares = [n * n for n in nums]    # a list, built now
            lazy = (n * n for n in nums)       # a generator, nothing computed yet
            print(squares)
            print(lazy)
            print(list(lazy))
            ```

            They shine inside functions that consume values one by one, like `sum()`, `max()`,
            `min()` or `"".join()`. When a generator expression is the only argument, you can even
            drop the extra brackets:

            ```python
            docs = ["the cat", "sat on the mat"]
            print(sum(len(d.split()) for d in docs))
            print(max(len(d) for d in docs))
            ```

            No list of word counts is ever stored: each count is made, added, and thrown away. With
            millions of documents, that saves a lot of memory. The idea is called **lazy evaluation**.
        ''',
        "hints": [
            "A generator expression looks like a list comprehension with round brackets instead of square ones - and it can go straight inside `sum(...)`.",
            "The number of words in one document is `len(doc.split())`. Add that up over all the docs.",
            "Return `sum(...)` where the inside is a generator expression producing `len(doc.split())` for each `doc` in `docs`. No square brackets and no `for` statement block.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Count the words in a whole document collection without building a big list in
            memory.

            **Write:** `total_words(docs)`

            - `docs`: any iterable of document strings - a list like `["the cat", "sat"]`, or
              a generator that produces strings
            - **Returns:** an `int`, the total number of words across all documents

            **Rules**
            - Words are separated by whitespace (several spaces count as one gap); an empty
              string has 0 words.
            - An empty `docs` gives `0`.
            - Use a **generator expression** (round brackets, e.g. inside `sum(...)`).
              A list comprehension (`[... for ...]`) and a `for` loop statement are not allowed.
            - It must also work when `docs` is a generator (which can only be looped over once).

            **Examples**
            ```python
            total_words(["the cat", "sat on the mat", ""])   # 6
            total_words([])                                  # 0
            total_words(("word " * i for i in range(4)))     # 6
            ```
        ''',
        "starter": r'''
            def total_words(docs):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import total_words

            def test_counts_words_across_documents():
                got = total_words(["the cat", "sat on the mat", ""])
                assert got == 6, f"got {got!r}"

            def test_no_documents_gives_zero():
                assert total_words([]) == 0

            def test_works_on_a_generator():
                docs = ("word " * i for i in range(4))
                got = total_words(docs)
                assert got == 6, f"got {got!r}"

            def test_uses_generator_expression_not_list_comp_or_for_loop():
                tree = ast.parse(source())
                kinds = {type(n).__name__ for n in ast.walk(tree)}
                assert "GeneratorExp" in kinds, "use a generator expression"
                assert "ListComp" not in kinds, "no list comprehension"
                assert "For" not in kinds, "no explicit for loop"
        ''',
        "solution": r'''
            def total_words(docs):
                return sum(len(doc.split()) for doc in docs)
        ''',
    },
    {
        "id": "generators-7",
        "title": "First chunk over the limit",
        "difficulty": 1,
        "lesson": r'''
            ## `next()` with a safety net

            Remember that `next()` on an empty generator raises `StopIteration`? `next()` accepts a
            second argument: a **default** to return instead of raising. Think of it as asking the
            vending machine "one more, please - or give me this if you're empty".

            ```python
            gen = (w for w in ["hi", "hello"] if len(w) > 3)
            print(next(gen, "none"))
            print(next(gen, "none"))
            ```

            Combine that with a generator expression and you get a neat pattern: **find the first
            item that matches**, and stop looking as soon as it is found.

            ```python
            nums = [3, 8, 11, 20]
            print(next((n for n in nums if n > 10), None))
            print(next((n for n in nums if n > 99), None))
            ```

            Note the double brackets: one pair for the call to `next(...)`, one pair around the
            generator expression, because it is not the only argument any more.

            You can also get an **iterator** from any list with `iter(items)` and pull from it with
            `next()`. Iterators remember their position, exactly like generators.
        ''',
        "research": {
            "note": "Read the docs for the built-in `next()` - especially what its second argument does - then come back.",
            "links": [{"title": "next() - Python built-in functions", "url": "https://docs.python.org/3/library/functions.html#next"}],
        },
        "prompt": r'''
            Before sending text chunks to a model, find the first one that is too long for the
            context budget.

            **Write:** `first_too_long(chunks, limit)`

            - `chunks`: any iterable of strings - a list, or a generator, e.g. `["short", "a much longer chunk"]`
            - `limit`: an `int`, the maximum allowed number of characters, e.g. `10`
            - **Returns:** the **first** chunk (a string) whose length is **greater than** `limit`,
              or `None` if there is none

            **Rules**
            - A chunk of exactly `limit` characters is fine (not too long).
            - Stop reading `chunks` as soon as the answer is found (it may be a generator that
              must not be read further).
            - Use the built-in `next()` (a check looks for it); no `for` loop statement.

            **Examples**
            ```python
            first_too_long(["short", "a much longer chunk", "another long chunk"], 10)
            # returns "a much longer chunk"
            first_too_long(["abc", "de"], 3)   # returns None
            first_too_long([], 5)              # returns None
            ```
        ''',
        "starter": r'''
            def first_too_long(chunks, limit):
                ...
        ''',
        "tests": r'''
            import ast
            from solution import first_too_long

            def test_returns_first_chunk_over_the_limit():
                got = first_too_long(["short", "a much longer chunk", "another long chunk"], 10)
                assert got == "a much longer chunk", f"got {got!r}"

            def test_exactly_limit_is_not_too_long():
                got = first_too_long(["abc", "de"], 3)
                assert got is None, f"got {got!r}"

            def test_empty_input_returns_none():
                assert first_too_long([], 5) is None

            def test_stops_reading_once_found():
                read = []
                def stream():
                    for c in ["ok", "way too long", "x", "y"]:
                        read.append(c)
                        yield c
                got = first_too_long(stream(), 5)
                assert got == "way too long", f"got {got!r}"
                assert len(read) == 2, f"read {len(read)} chunks, the answer was the 2nd"

            def test_uses_next_and_no_for_statement():
                tree = ast.parse(source())
                calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
                assert "next" in calls, "use the built-in next()"
                assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), "no for loop statement"
        ''',
        "solution": r'''
            def first_too_long(chunks, limit):
                return next((c for c in chunks if len(c) > limit), None)
        ''',
        "hints": [
            "A generator expression can describe 'the chunks that are too long'; `next()` takes the first thing out of it.",
            "Build a generator expression over `chunks` with an `if` that keeps only chunks longer than `limit`, and give `next()` a default for when it is empty.",
            "Return `next(` + a generator expression `(c for c in chunks if len(c) > limit)` + `, None)`. Mind the brackets: the generator expression needs its own pair.",
        ],
    },
    {
        "id": "generators-8",
        "title": "Preview a stream",
        "difficulty": 1,
        "lesson": r'''
            ## Taking just a slice of a stream

            Lists can be sliced: `items[:3]`. Generators can't - they have no positions, only "the
            next one". Some are even **infinite**: `itertools.count()` counts 0, 1, 2, ... forever,
            so `list()` on it would never finish.

            The `itertools` module (part of the standard library) has a tool for this:
            `itertools.islice(iterable, n)` gives back an iterator over **at most** `n` items, and
            reads no more than it needs.

            ```python
            from itertools import count, islice

            print(list(islice(count(), 5)))
            print(list(islice(["a", "b"], 5)))   # fewer items: you just get what exists
            ```

            Because `islice` itself is lazy, you wrap it in `list(...)` (or loop over it) to actually
            get the values.

            Think of it as a tap you open for exactly `n` cups. The name means "iterator slice".
            Other `itertools` helpers you'll see in real code: `chain` (one stream after another),
            `groupby` and `batched`.
        ''',
        "research": {
            "note": "Skim the `itertools` docs: find `islice` and look at its example calls, then come back.",
            "links": [{"title": "itertools.islice - Python docs", "url": "https://docs.python.org/3/library/itertools.html#itertools.islice"},
                      {"title": "Generators - Functional Programming HOWTO", "url": "https://docs.python.org/3/howto/functional.html#generators"}],
        },
        "prompt": r'''
            Show a quick preview of a stream (for example the first log lines, or the first
            items of an endless feed) without reading the whole thing.

            **Write:** `preview(stream, n)`

            - `stream`: any iterable - a list, a generator, or an **infinite** iterator like
              `itertools.count()`
            - `n`: an `int` (0 or more), how many items to show, e.g. `3`
            - **Returns:** a **list** of the first `n` items, in order

            **Rules**
            - If `stream` has fewer than `n` items, return all of them.
            - `n` = `0` returns `[]`.
            - It must work on an infinite iterator, and read no more than `n` items.
            - Use `itertools.islice` (a check looks for `islice`).

            **Examples**
            ```python
            preview(["a", "b", "c", "d"], 2)        # returns ["a", "b"]
            preview(["a"], 5)                       # returns ["a"]
            preview(itertools.count(), 3)           # returns [0, 1, 2]
            preview([1, 2], 0)                      # returns []
            ```
        ''',
        "starter": r'''
            def preview(stream, n):
                ...
        ''',
        "tests": r'''
            import itertools
            from solution import preview

            def test_returns_first_n_items_as_list():
                got = preview(["a", "b", "c", "d"], 2)
                assert got == ["a", "b"], f"got {got!r}"

            def test_short_stream_returns_everything():
                assert preview(["a"], 5) == ["a"]

            def test_works_on_infinite_iterator():
                got = preview(itertools.count(), 3)
                assert got == [0, 1, 2], f"got {got!r}"

            def test_zero_returns_empty_list():
                assert preview([1, 2], 0) == []

            def test_reads_no_more_than_n_items():
                read = []
                def stream():
                    for i in range(10):
                        read.append(i)
                        yield i
                preview(stream(), 3)
                assert len(read) == 3, f"read {len(read)} items to preview 3"

            def test_uses_islice():
                assert "islice" in source(), "use itertools.islice"
        ''',
        "solution": r'''
            from itertools import islice


            def preview(stream, n):
                return list(islice(stream, n))
        ''',
        "hints": [
            "You can't slice a generator with `[:n]`, but the `itertools` module has a slicing tool that works on any iterable.",
            "`islice(stream, n)` gives a lazy iterator over at most `n` items; turn it into a list.",
            "1) `from itertools import islice` at the top. 2) Return `list(islice(stream, n))`.",
        ],
    },
    {
        "id": "generators-9",
        "title": "Prepend the system prompt",
        "difficulty": 1,
        "lesson": r'''
            ## Passing a whole stream along: `yield from`

            Sometimes a generator wants to hand out **everything** another iterable produces. You
            could write a loop:

            ```python
            def with_header(lines):
                yield "HEADER"
                for line in lines:
                    yield line

            print(list(with_header(["a", "b"])))
            ```

            `yield from` does that loop in one line. It's like a relay: "for this part, just pass on
            everything that comes from over there".

            ```python
            def with_footer(lines):
                yield from lines
                yield "FOOTER"

            print(list(with_footer(["a", "b"])))
            print(list(with_footer(x * 2 for x in [1, 2])))
            ```

            `yield from` works with any iterable: a list, a string, a generator expression, or a call
            to another generator function. That last case is how bigger generators are built from
            smaller ones - this is called **delegating** to a sub-generator.
        ''',
        "prompt": r'''
            Chat APIs expect the *system* message first, followed by the conversation. Build that
            message stream lazily.

            **Write:** `with_system(system, messages)` - a **generator function**

            - `system`: the system prompt, a string, e.g. `"Be brief."`
            - `messages`: any iterable of message dicts (a list or a generator), e.g.
              `[{"role": "user", "content": "Hi"}]`
            - **Yields:** first the dict `{"role": "system", "content": system}`, then every
              message from `messages`, unchanged and in order

            **Rules**
            - It must be a generator function, and use **`yield from`** (a check looks for it).
            - With no messages, it yields only the system message.
            - It must be lazy: nothing from `messages` is read until it is needed.

            **Examples**
            ```python
            list(with_system("Be brief.", [{"role": "user", "content": "Hi"}]))
            # [{"role": "system", "content": "Be brief."}, {"role": "user", "content": "Hi"}]
            list(with_system("x", []))
            # [{"role": "system", "content": "x"}]
            ```
        ''',
        "starter": r'''
            def with_system(system, messages):
                ...
        ''',
        "tests": r'''
            import ast
            import inspect
            from solution import with_system

            USER = {"role": "user", "content": "Hi"}
            BOT = {"role": "assistant", "content": "Hello!"}

            def test_system_message_comes_first_then_messages():
                got = list(with_system("Be brief.", [USER, BOT]))
                assert got == [{"role": "system", "content": "Be brief."}, USER, BOT], f"got {got!r}"

            def test_no_messages_yields_only_system():
                got = list(with_system("x", []))
                assert got == [{"role": "system", "content": "x"}], f"got {got!r}"

            def test_is_lazy_generator():
                assert inspect.isgeneratorfunction(with_system), "with_system must be a generator function"
                read = []
                def stream():
                    for m in [USER, BOT]:
                        read.append(m)
                        yield m
                gen = with_system("s", stream())
                next(gen)
                assert read == [], "the system message should not need any of the messages"

            def test_uses_yield_from():
                tree = ast.parse(source())
                assert any(isinstance(n, ast.YieldFrom) for n in ast.walk(tree)), "use yield from"
        ''',
        "solution": r'''
            def with_system(system, messages):
                yield {"role": "system", "content": system}
                yield from messages
        ''',
        "hints": [
            "Two things are handed out in order: one dict you build yourself, then everything in `messages`.",
            "`yield` the system dict first; then pass along every message with a single `yield from` line.",
            "1) `yield {\"role\": \"system\", \"content\": system}`. 2) `yield from messages`.",
        ],
    },
    {
        "id": "generators-3",
        "title": "Batch for embeddings",
        "hints": [
            "Turn the input into one iterator with `iter()`, then keep taking up to `n` items from that same iterator. `itertools.islice(it, n)` takes up to `n` items.",
            "Loop: grab a list of up to `n` items; if it is empty you are done, otherwise yield it. Taking only `n` at a time is what makes it work on infinite inputs.",
            "1) If `n < 1`, raise `ValueError`. 2) `it = iter(iterable)`. 3) Repeat forever: batch = `list(islice(it, n))`; if the batch is empty, stop; else yield it.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Embedding APIs accept a limited number of inputs per request, so texts are sent in
            *batches*.

            **Write:** `batched(iterable, n)` - a **generator function** (it uses `yield`)

            - `iterable`: anything you can loop over - a list, a string, a `range`, or another
              generator (possibly infinite, e.g. `itertools.count()`)
            - `n`: the maximum batch size, an `int`, e.g. `2`
            - **Yields:** **lists** of up to `n` consecutive items, in order

            **Rules**
            - Every batch has exactly `n` items except the last, which may be smaller.
            - Never yield an empty batch: an empty input yields nothing, and an input whose
              length is a multiple of `n` has no extra empty batch at the end.
            - It must be *lazy*: it must work on an infinite iterator, and to produce one batch
              it must not read more than `n + 1` items from the input.
            - If `n < 1`, raise `ValueError` (raising it when iteration starts is fine).
            - Do not use `itertools.batched` (write it yourself; other tools such as
              `itertools.islice` are allowed).

            **Examples**
            ```python
            list(batched("abcde", 2))       # [["a", "b"], ["c", "d"], ["e"]]
            list(batched(range(6), 3))      # [[0, 1, 2], [3, 4, 5]]
            list(batched([], 3))            # []
            gen = batched(itertools.count(), 4)
            next(gen)                       # [0, 1, 2, 3]
            list(batched([1, 2], 0))        # ValueError
            ```
        ''',
        "starter": r'''
            def batched(iterable, n):
                ...
        ''',
        "tests": r'''
            import itertools
            from solution import batched

            def test_batches_of_n_with_smaller_last_batch():
                got = list(batched("abcde", 2))
                assert got == [["a", "b"], ["c", "d"], ["e"]], f"got {got!r}"

            def test_exact_multiple_and_empty_input_give_no_empty_batch():
                assert list(batched(range(6), 3)) == [[0, 1, 2], [3, 4, 5]]
                assert list(batched([], 3)) == []

            def test_works_on_infinite_input():
                got = list(itertools.islice(batched(itertools.count(), 4), 2))
                assert got == [[0, 1, 2, 3], [4, 5, 6, 7]], f"got {got!r}"

            def test_reads_only_what_it_needs():
                consumed = []
                def source_items():
                    for i in range(100):
                        consumed.append(i)
                        yield i
                gen = batched(source_items(), 3)
                first = next(gen)
                assert first == [0, 1, 2], f"got {first!r}"
                assert len(consumed) <= 4, f"read {len(consumed)} items to produce one batch of 3"

            def test_n_below_one_raises_value_error():
                try:
                    list(batched([1, 2], 0))
                except ValueError:
                    return
                assert False, "n=0 should raise ValueError"

            def test_does_not_use_itertools_batched():
                src = source().replace(" ", "")
                assert "itertools.batched" not in src and "importbatched" not in src.replace(",", ""), \
                    "write it yourself, without itertools.batched"
        ''',
        "solution": r'''
            from itertools import islice


            def batched(iterable, n):
                if n < 1:
                    raise ValueError("n must be at least 1")
                it = iter(iterable)
                while batch := list(islice(it, n)):
                    yield batch
        ''',
    },
    {
        "id": "generators-4",
        "title": "Render a streamed reply",
        "hints": [
            "Split the job in two: a generator that filters chunks, and a normal function that loops over that generator and prints.",
            "In `text_deltas`, dig into `chunk[\"choices\"][0][\"delta\"][\"content\"]` safely with `.get()` and skip chunks where any part is missing, None or empty. In `render`, print each piece right away with `end=\"\"` and collect the pieces.",
            "1) `text_deltas`: for each chunk, get `\"choices\"` (default `[]`) and skip if empty; get the first choice's `\"delta\"` (default `{}`), then its `\"content\"`; yield it if truthy. 2) `render`: for each delta, `print(delta, end=\"\", flush=True)` and append it to a list. 3) Call `print()` once at the end and return the joined text.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A streaming chat API sends its reply as a series of *chunk* dicts. Only some of them
            carry text:

            ```python
            {"choices": [{"delta": {"content": "Hel"}}]}      # text "Hel"
            {"choices": [{"delta": {"role": "assistant"}}]}   # no "content" key
            {"choices": [{"delta": {"content": None}}]}       # content is None
            {"choices": [{"delta": {"content": ""}}]}         # content is empty
            {"choices": []}                                   # no choices (e.g. a usage chunk)
            {"id": "x"}                                       # no "choices" key at all
            ```

            **Write:** `text_deltas(chunks)` and `render(chunks)`

            - `chunks`: any iterable of chunk dicts like the ones above (a list, or a generator
              that is still receiving data)
            - `text_deltas` **yields:** the `content` strings found at
              `chunk["choices"][0]["delta"]["content"]`, in order
            - `render` **returns:** the full reply text (a `str`), and also prints it

            **Rules**
            - `text_deltas` must be a *generator function* (it uses `yield`).
            - `text_deltas` skips every chunk that has no text: missing `"choices"` key, empty
              choices list, no `"content"` key, content `None`, or content `""`. It never crashes
              on them.
            - `text_deltas` must be lazy: it reads nothing before iteration starts, and reads
              chunks only as far as needed for the next piece of text.
            - `render` uses `text_deltas`. It prints each piece **as soon as it arrives**, all on
              one line with nothing added between pieces, then prints one newline at the very end.
            - An empty stream: `render` prints just `"\n"` and returns `""`.

            **Examples**
            ```python
            chunks = [{"choices": [{"delta": {"role": "assistant"}}]},
                      {"choices": [{"delta": {"content": "Hel"}}]},
                      {"choices": [{"delta": {"content": None}}]},
                      {"choices": [{"delta": {"content": "lo"}}]},
                      {"choices": []}]
            list(text_deltas(chunks))   # ["Hel", "lo"]
            render(chunks)              # prints "Hello" then a newline, returns "Hello"
            render([])                  # prints only a newline, returns ""
            ```
        ''',
        "starter": r'''
            def text_deltas(chunks):
                ...


            def render(chunks):
                ...
        ''',
        "tests": r'''
            import inspect
            from solution import text_deltas, render

            def chunk(content=None, role=None):
                delta = {}
                if role:
                    delta["role"] = role
                if content is not None or role is None:
                    delta["content"] = content
                return {"choices": [{"delta": delta}]}

            CHUNKS = [chunk(role="assistant"), chunk("Hel"), chunk(None), chunk(""),
                      {"choices": []}, chunk("lo"), {"id": "x"}, chunk(" world")]

            def test_text_deltas_skips_chunks_without_text():
                got = list(text_deltas(CHUNKS))
                assert got == ["Hel", "lo", " world"], f"got {got!r}"

            def test_text_deltas_is_a_lazy_generator():
                assert inspect.isgeneratorfunction(text_deltas), "text_deltas must be a generator function"
                seen = []
                def stream():
                    for c in CHUNKS:
                        seen.append(c)
                        yield c
                gen = text_deltas(stream())
                assert seen == [], "nothing should be read before iteration starts"
                next(gen)
                assert len(seen) == 2, f"read {len(seen)} chunks to get the first delta"

            def test_render_prints_text_and_newline_and_returns_text():
                value, out = capture(render, CHUNKS)
                assert value == "Hello world", f"returned {value!r}"
                assert out == "Hello world\n", f"printed {out!r}"

            def test_render_prints_each_piece_as_it_arrives():
                printed_before = []
                import sys
                def stream():
                    for c in CHUNKS:
                        printed_before.append(sys.stdout.getvalue())
                        yield c
                value, out = capture(render, stream())
                assert "Hel" in printed_before[-1], "each delta must be printed as soon as it arrives, not at the end"

            def test_render_empty_stream_prints_newline_returns_empty():
                value, out = capture(render, [])
                assert value == "" and out == "\n", f"returned {value!r}, printed {out!r}"
        ''',
        "solution": r'''
            def text_deltas(chunks):
                for chunk in chunks:
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    content = (choices[0].get("delta") or {}).get("content")
                    if content:
                        yield content


            def render(chunks):
                parts = []
                for delta in text_deltas(chunks):
                    print(delta, end="", flush=True)
                    parts.append(delta)
                print()
                return "".join(parts)
        ''',
    },
    {
        "id": "generators-5",
        "title": "Sliding window iterator",
        "lesson": r'''
            ## Putting it together: the iterator protocol

            A `for` loop only needs two methods from an object: `__iter__` (give me an iterator -
            an iterator just returns `self`) and `__next__` (give me the next value, or raise
            `StopIteration` when you're done). Generators get both for free; a class can write them
            by hand and keep its position in attributes.

            ```python
            class Countdown:
                def __init__(self, n):
                    self.n = n
                def __iter__(self):
                    return self
                def __next__(self):
                    if self.n <= 0:
                        raise StopIteration
                    self.n -= 1
                    return self.n + 1

            print(list(Countdown(3)))
            ```
        ''',
        "hints": [
            "The iterator protocol: `__iter__` returns `self`, and `__next__` returns the next value or raises `StopIteration` when there are no more.",
            "Keep the current start position and a 'done' flag on `self`. Each `__next__` returns `tokens[start:start + size]`, marks itself done if that window reached the end, and moves `start` forward by `stride`.",
            "1) `__init__`: validate (ValueError), store tokens/size/stride, `start = 0`, `done = True` if tokens is empty. 2) `__iter__`: return self. 3) `__next__`: if done, raise `StopIteration`; take the window; if `start + size >= len(tokens)`, set done; add `stride` to start; return the window.",
        ],
        "difficulty": 3,
        "prompt": r'''
            RAG pipelines split documents into overlapping token *windows* before embedding
            them.

            **Write:** a class `SlidingWindow(tokens, size, stride)` that is an **iterator**

            - `tokens`: a list of tokens, e.g. `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` or `["a", "b"]`
            - `size`: the window length, an `int`, e.g. `4`
            - `stride`: how far each window moves forward, an `int`, e.g. `3`
            - **Each `next()` returns:** one window, a list `tokens[start:start + size]`, for
              `start = 0, stride, 2*stride, ...`

            **Rules**
            - Implement the *iterator protocol* yourself: `__iter__` returns the object itself,
              and `__next__` returns the next window or raises `StopIteration` when there are
              none left. The word `yield` must not appear anywhere in your file.
            - The last window is the first one that reaches the end of `tokens` (it may be
              shorter than `size`); no window comes after it.
            - Empty `tokens` gives no windows.
            - Once exhausted, every further `next()` keeps raising `StopIteration`.
            - The constructor raises `ValueError` if `size < 1`, `stride < 1`, or `stride > size`.

            **Examples**
            ```python
            list(SlidingWindow(list(range(10)), 4, 3))
            # [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]]
            list(SlidingWindow(list(range(10)), 4, 4))
            # [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
            list(SlidingWindow(["a", "b", "c", "d", "e"], 3, 1))
            # [["a", "b", "c"], ["b", "c", "d"], ["c", "d", "e"]]   (nothing after "cde")
            list(SlidingWindow(["a", "b"], 5, 2))    # [["a", "b"]]
            list(SlidingWindow([], 3, 2))            # []
            SlidingWindow([1, 2, 3], 2, 3)           # ValueError (stride > size)
            ```
        ''',
        "starter": r'''
            class SlidingWindow:
                def __init__(self, tokens, size, stride):
                    ...
        ''',
        "tests": r'''
            from solution import SlidingWindow

            def test_overlapping_windows():
                got = list(SlidingWindow(list(range(10)), 4, 3))
                assert got == [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]], f"got {got!r}"

            def test_last_window_may_be_shorter():
                got = list(SlidingWindow(list(range(10)), 4, 4))
                assert got == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]], f"got {got!r}"

            def test_stops_after_first_window_reaching_the_end():
                got = list(SlidingWindow(list("abcde"), 3, 1))
                assert got == [list("abc"), list("bcd"), list("cde")], f"got {got!r}"
                got = list(SlidingWindow(list("ab"), 5, 2))
                assert got == [["a", "b"]], f"got {got!r}"

            def test_empty_tokens_give_no_windows():
                assert list(SlidingWindow([], 3, 2)) == []

            def test_iterator_protocol_without_yield_stays_exhausted():
                w = SlidingWindow([1, 2, 3], 2, 1)
                assert iter(w) is w, "__iter__ should return the iterator itself"
                assert next(w) == [1, 2] and next(w) == [2, 3]
                for _ in range(2):
                    try:
                        next(w)
                    except StopIteration:
                        continue
                    assert False, "an exhausted iterator must keep raising StopIteration"
                assert "yield" not in source(), "implement __next__ yourself, without yield"

            def test_invalid_size_or_stride_raises_value_error():
                for args in ((0, 1), (3, 0), (2, 3)):
                    try:
                        SlidingWindow([1, 2, 3], *args)
                    except ValueError:
                        continue
                    assert False, f"size, stride = {args} should raise ValueError"
        ''',
        "solution": r'''
            class SlidingWindow:
                def __init__(self, tokens, size, stride):
                    if size < 1 or stride < 1 or stride > size:
                        raise ValueError("need 1 <= stride <= size")
                    self.tokens = tokens
                    self.size = size
                    self.stride = stride
                    self.start = 0
                    self.done = not tokens

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.done:
                        raise StopIteration
                    end = self.start + self.size
                    window = self.tokens[self.start:end]
                    if end >= len(self.tokens):
                        self.done = True
                    self.start += self.stride
                    return window
        ''',
    },
    {
        "id": "generators-6",
        "title": "Flatten nested content",
        "hints": [
            "This is recursion with generators: `yield from flatten(child)` passes along everything the inner call yields.",
            "Decide per value: strings/bytes -> yield as a leaf; dict -> recurse into its values; otherwise try `iter(obj)` - if that raises `TypeError` it's a leaf, if it works recurse into each item.",
            "1) If it's a `str` or `bytes`, yield it. 2) Elif it's a dict, `yield from flatten(value)` for each value. 3) Else `try: items = iter(obj)` / `except TypeError:` yield obj and return. 4) For each item, `yield from flatten(item)`. Never turn anything into a list, so infinite generators stay lazy.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Tool results and message contents can be nested to any depth. Pull out every plain
            value (every *leaf*) so it can be indexed.

            **Write:** `flatten(obj)` - a recursive **generator function**

            - `obj`: any value - a list, tuple, dict, generator, string, number, `None`, ... nested
              in any combination, e.g. `["a", ("b", ["c"]), {"k": "d"}]`
            - **Yields:** the leaves of `obj`, one per `yield`, in order

            **Rules**
            - Lists, tuples and any other iterables (including generators) are descended into.
            - For a dict, descend into its **values** (in insertion order); keys are not yielded.
            - Strings and bytes are leaves: yield them whole, never split into characters.
            - Every non-iterable value (numbers, `None`, ...) is a leaf, including when `obj`
              itself is one: `flatten(5)` yields `5`.
            - Empty containers yield nothing.
            - Use **`yield from`** for the recursive calls.
            - It must stay lazy: it must work with `itertools.islice` on input that contains an
              infinite generator (never convert things to a list first).

            **Examples**
            ```python
            list(flatten(["a", ("b", ["c"]), {"k": "d", "n": [1, 2]}, 3]))
            # ["a", "b", "c", "d", 1, 2, 3]
            list(flatten("text"))           # ["text"]
            list(flatten([b"ab", ["cd"]]))  # [b"ab", "cd"]
            list(flatten(None))             # [None]
            list(flatten([[], {}, ()]))     # []
            list(itertools.islice(flatten(["start", itertools.count(), "never"]), 3))
            # ["start", 0, 1]
            ```
        ''',
        "starter": r'''
            def flatten(obj):
                ...
        ''',
        "tests": r'''
            import itertools
            from solution import flatten

            def test_mixed_nesting():
                got = list(flatten(["a", ("b", ["c"]), {"k": "d", "n": [1, 2]}, 3]))
                assert got == ["a", "b", "c", "d", 1, 2, 3], f"got {got!r}"

            def test_strings_and_bytes_are_leaves():
                assert list(flatten("text")) == ["text"]
                assert list(flatten([b"ab", ["cd"]])) == [b"ab", "cd"]

            def test_scalars_are_leaves_and_empty_containers_yield_nothing():
                assert list(flatten(5)) == [5]
                assert list(flatten(None)) == [None]
                assert list(flatten([[], {}, ()])) == []

            def test_generators_descended_lazily():
                nested = ["start", (x * 2 for x in itertools.count()), "never"]
                got = list(itertools.islice(flatten(nested), 4))
                assert got == ["start", 0, 2, 4], f"got {got!r}"

            def test_deep_dicts_yield_values_not_keys():
                data = {"messages": [{"role": "tool", "content": [{"type": "text", "text": "hi"}]}]}
                got = list(flatten(data))
                assert got == ["tool", "text", "hi"], f"got {got!r}"

            def test_uses_yield_from():
                import ast
                tree = ast.parse(source())
                assert any(isinstance(n, ast.YieldFrom) for n in ast.walk(tree)), "use yield from"
        ''',
        "solution": r'''
            def flatten(obj):
                if isinstance(obj, (str, bytes)):
                    yield obj
                elif isinstance(obj, dict):
                    for value in obj.values():
                        yield from flatten(value)
                else:
                    try:
                        items = iter(obj)
                    except TypeError:
                        yield obj
                        return
                    for item in items:
                        yield from flatten(item)
        ''',
    },
]
