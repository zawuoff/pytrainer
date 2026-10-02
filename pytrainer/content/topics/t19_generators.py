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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["generator", "yield", "yield from", "next", "iter", "iterator", "iterable", "lazy",
                 "stopiteration", "generator expression", "islice", "itertools", "stream",
                 "exhausted"],
    "cards": [
        {
            "syntax": "yield value",
            "explain": "Makes a function a generator function. Each yield gives one value to the loop and suspends the body.",
            "example": r'''
                def count_up_to(n):
                    i = 1
                    while i <= n:
                        yield i
                        i += 1
                print(list(count_up_to(3)))
                # [1, 2, 3]
            ''',
        },
        {
            "syntax": "next(gen, default)",
            "explain": "Asks for one value. With no values left it returns default, or raises StopIteration if you gave none.",
            "example": r'''
                def two_tokens():
                    yield "Hel"
                    yield "lo"
                gen = two_tokens()
                print(next(gen), next(gen), next(gen, "done"))
                # Hel lo done
            ''',
        },
        {
            "syntax": "(expr for x in items if cond)",
            "explain": "A generator expression. It computes each value only when asked, and its values can be read once.",
            "example": r'''
                nums = [3, 8, 11, 20]
                print(sum(n * n for n in nums))
                # 594
                print(next((n for n in nums if n > 10), None))
                # 11
            ''',
        },
        {
            "syntax": "yield from iterable",
            "explain": "Yields every value of another iterable in order, then continues with the next line.",
            "example": r'''
                def framed(lines):
                    yield "start"
                    yield from lines
                    yield "end"
                print(list(framed(["a", "b"])))
                # ['start', 'a', 'b', 'end']
            ''',
        },
        {
            "syntax": "itertools.islice(iterable, n)",
            "explain": "Returns an iterator over at most n items. It reads no more items than it needs.",
            "example": r'''
                from itertools import count, islice
                print(list(islice(count(), 5)))
                # [0, 1, 2, 3, 4]
                print(list(islice(["a", "b"], 5)))
                # ['a', 'b']
            ''',
        },
        {
            "syntax": "def __iter__(self):  /  def __next__(self):",
            "explain": "A class with both methods is an iterator. __next__ returns a value or raises StopIteration.",
            "example": r'''
                class Once:
                    def __iter__(self):
                        return self
                    def __next__(self):
                        raise StopIteration
                print(list(Once()))
                # []
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: iterators and generators

### Generator functions

A **generator function** is a function whose body contains the keyword `yield`. Calling it
does not run the body. The call returns a **generator**: an object that runs the body in
steps and produces one value per step.

```python
def count_up_to(n):
    i = 1
    while i <= n:
        yield i
        i += 1

for x in count_up_to(2):
    print(x)
print("done")
# 1
# 2
# done
```

The `for` loop asks the generator for a value. The body runs until it reaches `yield i`.
That statement gives the value of `i` to the loop and suspends the function at that line.
The local variables keep their values. On the next request, the body resumes at the line
after the `yield`. When the body ends, the loop ends.

Step through the code and watch execution move between the loop and the function body.

```diagram
{"type": "trace", "title": "A for loop consuming count_up_to(2)", "code": ["def count_up_to(n):", "    i = 1", "    while i <= n:", "        yield i", "        i += 1", "", "for x in count_up_to(2):", "    print(x)", "print(\"done\")"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 7, "vars": {}, "out": "", "note": "count_up_to(2) creates a generator. No line of the body has run yet."},
  {"line": 2, "vars": {"n": "2"}, "out": "", "note": "The loop asks for the first value, so the body starts."},
  {"line": 3, "vars": {"n": "2", "i": "1"}, "out": ""},
  {"line": 4, "vars": {"n": "2", "i": "1"}, "out": "", "note": "yield i gives 1 to the loop and suspends the function here."},
  {"line": 8, "vars": {"x": "1"}, "out": ""},
  {"line": 7, "vars": {"x": "1"}, "out": "1\n"},
  {"line": 5, "vars": {"n": "2", "i": "1"}, "out": "1\n", "note": "The body resumes after the yield. n and i still have their values."},
  {"line": 3, "vars": {"n": "2", "i": "2"}, "out": "1\n"},
  {"line": 4, "vars": {"n": "2", "i": "2"}, "out": "1\n"},
  {"line": 8, "vars": {"x": "2"}, "out": "1\n"},
  {"line": 7, "vars": {"x": "2"}, "out": "1\n2\n"},
  {"line": 5, "vars": {"n": "2", "i": "2"}, "out": "1\n2\n"},
  {"line": 3, "vars": {"n": "2", "i": "3"}, "out": "1\n2\n", "note": "i <= n is False. The body ends, so the generator is finished and the loop stops."},
  {"line": 9, "vars": {"x": "2"}, "out": "1\n2\n"},
  {"line": null, "vars": {"x": "2"}, "out": "1\n2\ndone\n"}
]}
```

### `next()` and `StopIteration`

The built-in function `next(gen)` asks a generator for one value. When the body has ended,
or has reached a `return`, the generator is finished. `next()` on a finished generator
raises the exception `StopIteration`. If you pass a second argument, `next()` returns that
value instead of raising.

```python
def two_tokens():
    yield "Hel"
    yield "lo"

gen = two_tokens()
print(next(gen))
# Hel
print(next(gen))
# lo
print(next(gen, "nothing left"))
# nothing left
try:
    next(gen)
except StopIteration:
    print("StopIteration was raised")
# StopIteration was raised
```

A `for` loop and `list()` call `next()` repeatedly. They catch `StopIteration` and stop.

### Generator expressions

A **generator expression** is a list comprehension written with round brackets. It
returns a generator. A generator is **lazy**: it computes each value only when that value
is requested.

```python
nums = [1, 2, 3, 4]
squares = [n * n for n in nums]
lazy = (n * n for n in nums)
print(squares)
# [1, 4, 9, 16]
print(list(lazy))
# [1, 4, 9, 16]
print(list(lazy))
# []
print(sum(n * n for n in nums))
# 30
```

The list comprehension builds all four values at once. The generator expression computes
nothing until `list()` or `sum()` requests values. The second `list(lazy)` returns `[]`
because the first one already used every value. Lazy evaluation is useful for text
that arrives piece by piece, for large files, and for series that never end.

### Iterables and iterators

An **iterable** is any object a `for` loop can loop over, such as a list, a string, a dict
or a generator. An **iterator** is an object that returns its values one at a time through
`next()`. `iter(items)` returns an iterator for an iterable. A generator is an iterator.

```python
it = iter(["gpt-4o", "claude"])
print(next(it))
# gpt-4o
print(next(it))
# claude
print(next(it, None))
# None
```

The **iterator protocol** is the pair of methods a `for` loop uses. `__iter__` returns the
iterator itself. `__next__` returns the next value or raises `StopIteration`. A class that
defines both methods is an iterator.

### `itertools.islice` and `yield from`

`itertools.islice(iterable, n)` returns an iterator over at most `n` items and reads no
more than it needs. `yield from iterable` yields every value of another iterable in order.
`itertools.count()` yields 0, 1, 2 and so on without end, so `list()` on it never
finishes. `islice(count(), 5)` stops after 5 items.

```python
from itertools import count, islice

def framed(lines):
    yield "start"
    yield from lines
    yield "end"

print(list(framed(["a", "b"])))
# ['start', 'a', 'b', 'end']
print(list(islice(count(), 5)))
# [0, 1, 2, 3, 4]
```

## Common mistakes

- A generator produces its values once. A second `list(gen)` returns `[]`. Call the
  generator function again to get a new generator.
- `return x` inside a loop ends the function at the first item. Use `yield x` to produce
  every item.
- `print(gen)` prints text such as `<generator object count_up_to at 0x...>`. It does not
  print the values. Use `print(list(gen))`.
- `[x for x in xs]` builds a list immediately. `(x for x in xs)` computes nothing until a
  value is requested.
- `next()` on an empty iterator raises `StopIteration`, and `max()` on one raises
  `ValueError`. Pass a second argument to `next()` or `default=` to `max()`.
'''


EXERCISES = [
    {
        "id": "generators-s1",
        "title": "Countdown",
        "lesson": r'''
            ## Generator functions and `yield`

            A normal function runs its whole body and returns one value with `return`. A
            **generator function** is a function whose body contains the keyword `yield`. It
            produces a series of values, one at a time.

            ```python
            def three_models():
                yield "gpt-4o"
                yield "claude"
                yield "llama"

            for model in three_models():
                print(model)
            # gpt-4o
            # claude
            # llama
            ```

            Calling `three_models()` returns a **generator**: an object that runs the function
            body in steps. The `for` loop asks the generator for a value. The body runs until it
            reaches a `yield`, and the value after `yield` is assigned to `model`. The function
            is suspended at that line. On the next pass of the loop, the body continues from the
            line after that `yield`. When the body ends, the loop ends.

            Step through the code to see each `yield` give one value to the loop.

            ```diagram
            {"type": "trace", "title": "Each yield gives one value to the for loop", "code": ["def three_models():", "    yield \"gpt-4o\"", "    yield \"claude\"", "    yield \"llama\"", "", "for model in three_models():", "    print(model)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 6, "vars": {}, "out": ""},
              {"line": 2, "vars": {}, "out": "", "note": "The loop asks for a value, so the body runs up to the first yield."},
              {"line": 7, "vars": {"model": "'gpt-4o'"}, "out": ""},
              {"line": 6, "vars": {"model": "'gpt-4o'"}, "out": "gpt-4o\n"},
              {"line": 3, "vars": {}, "out": "gpt-4o\n", "note": "The body continues after the first yield and reaches the second one."},
              {"line": 7, "vars": {"model": "'claude'"}, "out": "gpt-4o\n"},
              {"line": 6, "vars": {"model": "'claude'"}, "out": "gpt-4o\nclaude\n"},
              {"line": 4, "vars": {}, "out": "gpt-4o\nclaude\n"},
              {"line": 7, "vars": {"model": "'llama'"}, "out": "gpt-4o\nclaude\n"},
              {"line": 6, "vars": {"model": "'llama'"}, "out": "gpt-4o\nclaude\nllama\n", "note": "The loop asks again. The body has no more lines, so the loop ends."},
              {"line": null, "vars": {"model": "'llama'"}, "out": "gpt-4o\nclaude\nllama\n"}
            ]}
            ```

            `yield` also works inside a loop. This generator function yields once per pass of
            its `while` loop.

            ```python
            def count_up_to(n):
                i = 1
                while i <= n:
                    yield i
                    i += 1

            for x in count_up_to(3):
                print(x)
            # 1
            # 2
            # 3
            ```

            Each value that a generator produces is said to be **yielded**.
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

            Calling a generator function does not run any line of its body. The call only creates
            a generator object and returns it.

            The built-in function `next()` asks a generator for one value. Each `next(gen)` call
            runs the body from the line where it stopped, up to the next `yield`. The call
            returns the yielded value. The generator is then **suspended**: it stops at that
            `yield` and keeps the values of its local variables. The following `next(gen)`
            **resumes** it at the line after that `yield`.

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
            # nothing ran yet
            # start
            # first
            # resumed
            # second
            ```

            `start` is printed after `nothing ran yet`. The line `print("start")` runs during
            the first `next(gen)`, not during `steps()`.

            A `for` loop calls `next()` for you once per pass. Step through the same generator in
            a `for` loop and watch the two `print` calls inside the body run between the passes.

            ```diagram
            {"type": "trace", "title": "steps() is suspended at each yield and resumed by the loop", "code": ["def steps():", "    print(\"start\")", "    yield \"first\"", "    print(\"resumed\")", "    yield \"second\"", "", "for value in steps():", "    print(\"got\", value)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 7, "vars": {}, "out": "", "note": "steps() creates the generator. Nothing is printed yet."},
              {"line": 2, "vars": {}, "out": "", "note": "The loop calls next(), so the body starts running."},
              {"line": 3, "vars": {}, "out": "start\n", "note": "The generator yields 'first' and is suspended at this line."},
              {"line": 8, "vars": {"value": "'first'"}, "out": "start\n"},
              {"line": 7, "vars": {"value": "'first'"}, "out": "start\ngot first\n"},
              {"line": 4, "vars": {}, "out": "start\ngot first\n", "note": "The loop calls next() again. The body resumes at the line after the first yield."},
              {"line": 5, "vars": {}, "out": "start\ngot first\nresumed\n"},
              {"line": 8, "vars": {"value": "'second'"}, "out": "start\ngot first\nresumed\n"},
              {"line": 7, "vars": {"value": "'second'"}, "out": "start\ngot first\nresumed\ngot second\n", "note": "The next call to next() reaches the end of the body. StopIteration is raised and the loop ends."},
              {"line": null, "vars": {"value": "'second'"}, "out": "start\ngot first\nresumed\ngot second\n"}
            ]}
            ```
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
            `yield`: it prints `A`, then yields `1`, which gets printed. Then `C` is
            printed outside. The second `next(gen)` resumes right after the first `yield`:
            it prints `B` and yields `2`.
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
            ## Exhausted generators

            A generator yields each of its values once. After the last value it is
            **exhausted**: it has no more values and it cannot start again. To get the values a
            second time, call the generator function again. That call creates a new generator.

            `list(gen)` calls `next()` repeatedly and puts every remaining value into a list.

            ```python
            def two():
                yield 1
                yield 2

            gen = two()
            print(list(gen))
            # [1, 2]
            print(list(gen))
            # []
            print(list(two()))
            # [1, 2]
            ```

            The second `list(gen)` returns `[]` because the first one exhausted `gen`. The last
            line calls `two()` again, so it reads from a new generator.

            `next()` on an exhausted generator raises the exception `StopIteration`. It means
            that there are no more values. A `for` loop and `list()` catch `StopIteration` for
            you and stop.

            ```python
            def two():
                yield 1
                yield 2

            gen = two()
            print(next(gen), next(gen))
            # 1 2
            try:
                next(gen)
            except StopIteration:
                print("no more values")
            # no more values
            ```

            `print(gen)` does not print the values. It prints a description of the object, such
            as `<generator object two at 0x7f3a5c1d2e40>`. Use `print(list(gen))` to see the
            values.
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
            "A generator keeps its position: values already taken are gone.",
            "After `next(gen)` took the first value, `list(gen)` only gets the rest; then nothing is left. `tokens()` makes a fresh generator.",
            "Write four lines: the first value as plain text, then a one-item list, then an empty list, then a two-item list - lists printed with quotes like `['a']`.",
        ],
    },
    {
        "id": "generators-s3",
        "title": "Yield the even numbers",
        "lesson": r'''
            ## Yield only some items

            A generator function can yield some items of a list and skip the others. Put the
            `yield` inside an `if` inside a `for` loop. The `yield` runs only for the items where
            the condition is `True`.

            ```python
            def long_words(words):
                for w in words:
                    if len(w) > 3:
                        yield w

            print(list(long_words(["hi", "hello", "yo", "model"])))
            # ['hello', 'model']
            print(list(long_words(["hi", "yo"])))
            # []
            ```

            When the condition is `False`, the `yield` line does not run and the loop moves to
            the next item. If no item meets the condition, the generator yields nothing and
            `list()` returns `[]`.

            This function does not create a result list and does not call `.append()`. It yields
            each matching item as soon as the loop reaches it. A generator that yields only the
            items that meet a condition is called a **filtering generator**.

            A generator is **lazy**: it does work only when a value is requested. `long_words`
            checks the next word only when the caller asks for the next value.
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

            `return` and `yield` both give a value to the code that called the function. They
            differ in what happens to the function afterwards.

            - `return x` ends the function. A loop inside the function stops, and the remaining
              items are never visited.
            - `yield x` produces `x` and suspends the function. On the next request, the
              function continues from the same line, so the loop goes on.

            ```python
            def first_only(items):
                for x in items:
                    return x

            def every_one(items):
                for x in items:
                    yield x

            print(first_only(["a", "b", "c"]))
            # a
            print(list(every_one(["a", "b", "c"])))
            # ['a', 'b', 'c']
            ```

            `first_only` ends during the first pass of its loop, so it returns only `"a"`.

            This is a common bug. If a function should produce every matching item and you get
            only one, look for a `return` inside the loop.

            Inside a generator function, a `return` with no value is allowed. It ends the
            generator, and no more values are yielded.

            ```python
            def until_stop(items):
                for x in items:
                    if x == "STOP":
                        return
                    yield x

            print(list(until_stop(["a", "b", "STOP", "c"])))
            # ['a', 'b']
            ```
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
            ## Streaming with a generator

            A chat application shows a reply piece by piece while the language model that writes the
            reply is still writing it. The program talks to the model through its **API**: the set
            of requests that the model's service accepts. The API **streams** the reply: it sends
            each piece as soon as the model produces it, instead of sending the whole text at the end.

            A generator works the same way. The code that loops over the generator receives each
            piece as soon as it is yielded, before the next piece exists.

            ```python
            def stream_letters(word):
                for letter in word:
                    yield letter

            for piece in stream_letters("hey"):
                print(piece, end="|")
            print()
            # h|e|y|
            ```

            `print(piece, end="|")` writes `|` after the piece instead of a newline, so all the
            pieces appear on one line. The final `print()` writes the newline.

            A `for` loop works on a list and on a generator in the same way. An **iterable** is
            any object that a `for` loop can loop over. Lists, strings and generators are all
            iterables. A generator differs from a list in one way: it computes each item when
            the loop asks for it.

            In the next example the outer loop runs twice: first `source` is a list, then it is
            a generator. The inner loop is the same code for both and prints the same line.

            ```python
            def stream_letters(word):
                for letter in word:
                    yield letter

            for source in (["h", "i"], stream_letters("hi")):
                for piece in source:
                    print(piece, end="|")
                print()
            # h|i|
            # h|i|
            ```
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
            ## `range` with a step

            To cut a string into pieces of equal size, you need the start index of each piece:
            `0`, then `size`, then `2 * size`, and so on.

            `range` takes an optional third argument, the **step**: the amount added to get
            each next number.

            ```python
            print(list(range(0, 10, 4)))
            # [0, 4, 8]

            text = "streaming"
            for start in range(0, len(text), 4):
                print(start, text[start:start + 4])
            # 0 stre
            # 4 amin
            # 8 g
            ```

            Two rules make this work for any text length:

            - `range(0, len(text), size)` stops before `len(text)`, so no piece starts past the
              end. For an empty string the range is empty and the loop body never runs.
            - A slice that goes past the end of a string does not raise an error. It stops at
              the last character.

            ```python
            print(list(range(0, 0, 4)))
            # []
            print("ing"[0:4])
            # ing
            ```

            In the APIs of language models, each small piece of a streamed reply is called a **delta**: the text
            added since the previous piece. Joining all the deltas gives the full text.

            ```python
            print("".join(["stre", "amin", "g"]))
            # streaming
            ```
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

            The list comprehension `[n * n for n in nums]` builds a complete list immediately.
            A **generator expression** has the same syntax with round brackets instead of square
            ones. It returns a generator, and it computes each value only when that value is
            requested.

            ```python
            nums = [1, 2, 3, 4]
            squares = [n * n for n in nums]
            lazy = (n * n for n in nums)
            print(squares)
            # [1, 4, 9, 16]
            print(type(lazy))
            # <class 'generator'>
            print(list(lazy))
            # [1, 4, 9, 16]
            ```

            `squares` is a list that already holds four numbers. `lazy` is a generator that has
            computed nothing yet. `list(lazy)` requests every value, so the squares are computed
            at that point.

            Generator expressions are useful as arguments to functions that read values one by
            one, such as `sum()`, `max()`, `min()` and `"".join()`. When a generator expression
            is the only argument of a call, you can leave out its own brackets.

            ```python
            prompts = ["Summarize this", "Translate to French"]
            print(sum(len(p) for p in prompts))
            # 33
            print(max(len(p) for p in prompts))
            # 19
            ```

            `sum()` requests one length, adds it to the total and requests the next one. No list
            of lengths is ever stored. With millions of prompts, a list of lengths would take a
            lot of the computer's memory, and the generator expression takes almost none.
            Computing a value only when it is requested is called **lazy evaluation**.
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
            ## `next()` with a default

            `next()` on an exhausted generator raises `StopIteration`. `next()` also accepts a
            second argument, the **default**: a value that `next()` returns instead of raising
            when there are no more values.

            ```python
            gen = (w for w in ["hi", "hello"] if len(w) > 3)
            print(next(gen, "none"))
            # hello
            print(next(gen, "none"))
            # none
            ```

            `next()` with a generator expression finds the first item that matches a condition.
            The generator expression tests the items one by one. `next()` takes the first value
            it yields, and the remaining items are never tested.

            ```python
            nums = [3, 8, 11, 20]
            print(next((n for n in nums if n > 10), None))
            # 11
            print(next((n for n in nums if n > 99), None))
            # None
            ```

            The call needs two pairs of brackets: one pair for `next(...)` and one pair around
            the generator expression. A generator expression can drop its own brackets only when
            it is the only argument.

            `next()` does not accept a list directly. First call `iter(items)`. It returns an
            **iterator**: an object that returns the values of a collection one at a time and
            keeps its current position. Then pass that iterator to `next()`. A generator is an
            iterator too.

            ```python
            it = iter(["a", "b"])
            print(next(it))
            # a
            print(next(it))
            # b
            print(next(it, "done"))
            # done
            ```
        ''',
        "research": {
            "note": "Read the docs for the built-in `next()` - especially what its second argument does - then come back.",
            "links": [{"title": "next() - Python built-in functions", "url": "https://docs.python.org/3/library/functions.html#next"}],
        },
        "prompt": r'''
            Before sending text chunks to a model, find the first one that is too long for the
            size limit.

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
            ## The first `n` items of a stream

            A list can be sliced: `items[:3]`. A generator cannot. It has no indexes, and it can
            only produce its next value. Some iterators are **infinite**: they never run out of
            values. `itertools.count()` yields 0, 1, 2 and so on without end, so `list()` on it
            never finishes.

            The `itertools` module is part of the standard library. `itertools.islice(iterable, n)`
            returns an iterator over at most `n` items. It reads no more items than it needs.
            The name is short for "iterator slice".

            ```python
            from itertools import count, islice

            print(list(islice(count(), 5)))
            # [0, 1, 2, 3, 4]
            print(list(islice(["a", "b"], 5)))
            # ['a', 'b']
            ```

            The second call asks for 5 items, but the list has 2. `islice` returns the items
            that exist and raises no error.

            `islice` is lazy. It returns an iterator, not a list. Pass it to `list(...)` or loop
            over it to get the values.

            `itertools` has other functions that you will see in real code. `chain(a, b)` yields
            every item of `a` and then every item of `b`. `groupby` groups consecutive
            items that have the same key, and `batched` (Python 3.12 and newer) splits an iterable
            into tuples of a fixed size.

            ```python
            from itertools import chain

            print(list(chain(["a"], ["b", "c"])))
            # ['a', 'b', 'c']
            ```
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
            ## `yield from`

            A generator function often needs to yield every value of another iterable. You can
            write a loop that yields the values one by one.

            ```python
            def with_header(lines):
                yield "HEADER"
                for line in lines:
                    yield line

            print(list(with_header(["a", "b"])))
            # ['HEADER', 'a', 'b']
            ```

            `yield from iterable` does the same as that loop in one statement. It yields each
            value of the iterable in order. When the iterable has no more values, the function
            continues with the next line.

            ```python
            def with_footer(lines):
                yield from lines
                yield "FOOTER"

            print(list(with_footer(["a", "b"])))
            # ['a', 'b', 'FOOTER']
            print(list(with_footer(x * 2 for x in [1, 2])))
            # [2, 4, 'FOOTER']
            ```

            `yield from` accepts any iterable: a list, a string, a generator expression or a
            call to another generator function. `yield from` stays lazy. It reads one value
            from the iterable each time a value is requested.

            Using `yield from` on a call to another generator function is called **delegating**
            to a sub-generator. You can write a large generator function as several small ones
            and combine them this way.
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
            ## The iterator protocol

            A `for` loop uses two methods of an object. Together they are called the
            **iterator protocol**.

            - `__iter__` returns an iterator. In a class that is its own iterator, it returns `self`.
            - `__next__` returns the next value, or raises `StopIteration` when no values are
              left.

            `iter(obj)` calls `obj.__iter__()` and `next(obj)` calls `obj.__next__()`. A
            generator has both methods already. A class can define them itself and store its
            position in attributes.

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
            # [3, 2, 1]
            ```

            Click through the stages to see what a `for` loop over `Countdown(3)` does.

            ```diagram
            {"type": "flow", "title": "What for value in Countdown(3) does", "steps": [
              {"label": "iter()", "detail": "The for loop calls iter() on the object once. iter() calls the __iter__ method, which returns self. The object is its own iterator.", "code": "it = iter(Countdown(3))\n# it.n is 3"},
              {"label": "next()", "detail": "The loop calls next(it) at the start of each pass. next() calls the __next__ method.", "code": "value = next(it)"},
              {"label": "Value returned", "detail": "__next__ subtracts 1 from self.n and returns the old number. The loop assigns it to value and runs the loop body.", "code": "pass 1: value = 3, it.n is 2\npass 2: value = 2, it.n is 1\npass 3: value = 1, it.n is 0"},
              {"label": "StopIteration", "detail": "When self.n is 0, __next__ raises StopIteration. The for loop catches the exception and ends. Every later next(it) raises StopIteration again.", "code": "next(it)\n# StopIteration"}
            ], "loop": {"from": 2, "to": 1, "label": "while __next__ returns a value"}}
            ```

            After the loop ends, the iterator is exhausted. `self.n` stays at `0`, so every
            later `next()` call raises `StopIteration` again.
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

            **Write:** `flatten(obj)` - a recursive **generator function** (it calls itself for the nested parts)

            - `obj`: any value - a list, tuple, dict, generator, string, number, `None`, ... nested
              in any combination, e.g. `["a", ("b", ["c"]), {"k": "d"}]`
            - **Yields:** the leaves of `obj`, one per `yield`, in order

            **Rules**
            - Lists, tuples and any other iterables (including generators) are descended into.
            - For a dict, descend into its **values** (in insertion order); keys are not yielded.
            - Strings and bytes (raw binary data, written like `b"ab"`) are leaves: yield them whole, never split into characters.
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
