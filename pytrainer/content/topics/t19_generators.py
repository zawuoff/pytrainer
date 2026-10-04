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
            ## Handing out one value at a time

            A model writes its reply one small piece at a time. Suppose your function waits until the whole
            reply exists and then returns it as a list. The user looks at an empty screen for ten seconds.
            A log file with ten million lines has the same problem: a function that returns every line in
            one list must hold all of them in the computer's memory before your loop sees the first one.

            What you want is a function that hands over one value, waits until you ask for more, and then
            hands over the next one. Python has a keyword for that:

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

            There is no list here and no `return`. Each `yield` hands one value to the `for` loop, and the
            loop variable `model` receives it. Then the function stops at that line, but it is not over. It
            is paused. When the loop comes round for the next value, the function goes on from the line
            where it paused.

            Press Next and watch Python jump between the function and the loop:

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

            A function with `yield` in its body is called a **generator function**. The loop ends when the
            function reaches the end of its body.

            ```quiz
            The loop has printed `gpt-4o` and asks for the next value. Where does `three_models` go on?
            - [x] At the line after `yield "gpt-4o"` :: Yes. The function was paused at that `yield`, so it goes on with the line below it and reaches `yield "claude"`.
            - [ ] At the first line of its body :: A normal function starts at the top on every call. A generator function that is paused goes on from where it stopped. If it started again, the loop would get `gpt-4o` forever.
            - [ ] Nowhere, because it ended at the first `yield` :: That is what `return` would do. `yield` pauses the function without ending it, and that is why all three names are printed.
            ```

            ### `yield` inside a loop

            `yield` can also sit inside a loop. The function then hands out one value on every iteration,
            and its variables keep their values while it is paused:

            ```python
            def powers(limit):
                value = 1
                while value < limit:
                    yield value
                    value = value * 2

            for p in powers(5):
                print(p)
            # 1
            # 2
            # 4
            ```

            After each pause the function goes on with `value = value * 2` and then tests
            `value < limit` again. When the test is false, the body ends, and so does the `for` loop.

            ```predict
            def count_up(start, stop):
                n = start
                while n <= stop:
                    yield n
                    n += 2

            for x in count_up(1, 6):
                print(x)
            print("end")
            ---
            The function hands out 1 and pauses. Each time the loop asks again, it goes on with `n += 2` and tests `n <= stop` again, so it hands out 3 and then 5. When `n` is 7 the test is false and the body ends. That ends the `for` loop, and `end` is printed.
            ```

            **Watch out:** the values come out only when something loops over the call.
            `print(three_models())` does not show the three names. It shows a line such as
            `<generator object three_models at 0x7f3a5c1d2e40>`. The next step explains what that object is.

            **In short:** `yield` hands one value to the loop and pauses the function until the loop asks
            for the next one.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, with each printed line on a line of its own.
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
            The `for` loop asks `countdown(3)` for a value, so the body starts with `n` equal to 3. The test
            `3 > 0` is true, `yield n` hands 3 to the loop, and `print(x)` shows `3`. The loop asks again,
            and the function goes on at the line after the `yield`: `n -= 1` makes `n` 2, the `while` test
            is still true, and 2 is handed out. The same happens for 1. Then `n` becomes 0, the test `0 > 0`
            is false, and the body ends. That ends the `for` loop too, and the last line prints `liftoff`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Each `yield` hands one value to the `for` loop, and the loop prints it. Ask yourself where the function goes on when the loop wants the next value.",
            "After a `yield`, the function carries on with the line below it, so `n` gets smaller by 1 before the `while` test is tried again. When the test is false, the function ends, and so does the `for` loop.",
            "Write down the value of `n` each time the `yield` line is reached, one number per line, until the `while` test is false. The last line of your answer comes from the `print` after the loop.",
        ],
    },
    {
        "id": "generators-s2",
        "title": "Watch it pause",
        "lesson": r'''
            ## Nothing runs until you ask

            In the last step the body of a generator function ran when the loop asked for a value. So what
            happens on the line that calls the function, before anything has asked? Put a `print` in the
            body and find out:

            ```python
            def load_docs():
                print("opening a.txt")
                yield "a.txt"
                print("opening b.txt")
                yield "b.txt"

            docs = load_docs()
            print("nothing was opened")
            # nothing was opened
            ```

            `opening a.txt` is not printed. Calling a generator function does not run its body at all. The
            call hands you an object that is ready to run the body later, one piece at a time. That object
            is called a **generator**, and here it is stored under the name `docs`.

            You ask a generator for one value with the built-in function `next()`:

            ```python
            def load_docs():
                print("opening a.txt")
                yield "a.txt"
                print("opening b.txt")
                yield "b.txt"

            docs = load_docs()
            first = next(docs)
            # opening a.txt
            print("got", first)
            # got a.txt
            ```

            `next(docs)` ran the body up to the first `yield` and handed back the value of that `yield`.
            Then the generator paused again. A second `next(docs)` would go on from the line after that
            `yield`. The Python documentation says that the function is **suspended** at a `yield` and
            **resumed** by `next()`.

            ```predict
            def greet():
                print("one")
                yield "hello"
                print("two")
                yield "bye"

            g = greet()
            print("ready")
            print(next(g))
            print("end")
            ---
            `greet()` runs nothing, so `ready` comes first. `next(g)` runs the body up to the first `yield`: it prints `one` and hands back `"hello"`, which the outer `print` shows. Nobody asks for a second value, so the generator stays suspended and `two` is never printed.
            ```

            A `for` loop does the asking for you. It calls `next()` once per iteration. Press Next and
            watch the two `opening` lines appear between the `got` lines, not before them:

            ```diagram
            {"type": "trace", "title": "A for loop calls next() once per iteration", "code": ["def load_docs():", "    print(\"opening a.txt\")", "    yield \"a.txt\"", "    print(\"opening b.txt\")", "    yield \"b.txt\"", "", "for name in load_docs():", "    print(\"got\", name)", "print(\"done\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 7, "vars": {}, "out": "", "note": "load_docs() makes the generator. No line of the body has run yet."},
              {"line": 2, "vars": {}, "out": "", "note": "The loop asks for the first value, so the body starts."},
              {"line": 3, "vars": {}, "out": "opening a.txt\n", "note": "yield hands 'a.txt' to the loop. The function is suspended at this line."},
              {"line": 8, "vars": {"name": "'a.txt'"}, "out": "opening a.txt\n"},
              {"line": 7, "vars": {"name": "'a.txt'"}, "out": "opening a.txt\ngot a.txt\n", "note": "The loop asks for the next value."},
              {"line": 4, "vars": {}, "out": "opening a.txt\ngot a.txt\n", "note": "The function is resumed at the line after the first yield."},
              {"line": 5, "vars": {}, "out": "opening a.txt\ngot a.txt\nopening b.txt\n"},
              {"line": 8, "vars": {"name": "'b.txt'"}, "out": "opening a.txt\ngot a.txt\nopening b.txt\n"},
              {"line": 7, "vars": {"name": "'b.txt'"}, "out": "opening a.txt\ngot a.txt\nopening b.txt\ngot b.txt\n", "note": "The loop asks again. The body has no more lines, so the loop ends."},
              {"line": 9, "vars": {"name": "'b.txt'"}, "out": "opening a.txt\ngot a.txt\nopening b.txt\ngot b.txt\n"},
              {"line": null, "vars": {"name": "'b.txt'"}, "out": "opening a.txt\ngot a.txt\nopening b.txt\ngot b.txt\ndone\n"}
            ]}
            ```

            ```match
            `docs = load_docs()` :: makes a generator and runs no line of the body
            `next(docs)` :: runs the body up to the next `yield` and hands back one value
            `for name in docs:` :: asks for a value on every iteration until the body ends
            ```

            **Watch out:** a generator function that seems to do nothing is usually one that nobody asked.
            A call on a line of its own, such as `load_docs()`, runs no line of the body and raises no
            error.

            **In short:** calling a generator function only makes a generator, and each `next()` runs the
            body as far as the next `yield`.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, with each printed line on a line of its own. Think about when each line inside `steps` runs.
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
            `gen = steps()` makes the generator and runs no line of the body, so nothing is printed yet.
            The first `next(gen)` starts the body: `print("A")` runs, then `yield 1` hands back 1 and
            suspends the function. The outer `print` shows that `1`. Next, `print("C")` runs in the main
            program while the generator is still suspended. The second `next(gen)` resumes the body at the
            line after the first `yield`: it prints `B`, and `yield 2` hands back 2, which the outer `print`
            shows.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "The line `gen = steps()` prints nothing. Look again at the first example in the lesson.",
            "Each `next(gen)` runs the body from where it is suspended up to the next `yield`. A `print` on the way runs first. Then the value comes back, and the outer `print` shows it.",
            "Go through the last three lines of the program one at a time. For each `next(gen)`, write first what the body prints on its way to the `yield`, then the value that is handed back. The line that prints `C` runs between the two. Your answer has five lines.",
        ],
    },
    {
        "id": "generators-s6",
        "title": "Used up",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## A generator can be used only once

            You have a stream of chunks, and you loop over it twice: once to count the chunks and once to
            print them. The count is right. The second loop prints nothing, and there is no error.

            ```python
            def chunks():
                yield "intro"
                yield "body"
            stream = chunks()
            count = 0
            for c in stream:
                count += 1
            print(count)
            # 2
            for c in stream: print(c)
            print("second loop is over")
            # second loop is over
            ```

            A generator only moves forward. The first loop ran the body of `chunks` to its end. After that
            the generator has nothing more to hand out, and it cannot go back to the top. A generator in
            this state is called **exhausted**.

            To get the values a second time, call the generator function again. Every call makes a new
            generator that starts at the top of the body.

            The built-in `list()` shows what a generator still has: `list(gen)` asks for every remaining
            value and puts them in a list.

            ```try
            def chunks():
                yield "intro"
                yield "body"

            stream = chunks()
            print(list(stream))
            print(list(stream))
            ---
            Run it. The second line of output is `[]`, because the first `list()` exhausted `stream`. Change the last line so that the program prints `['intro', 'body']` twice.
            ---
            def chunks():
                yield "intro"
                yield "body"

            stream = chunks()
            print(list(stream))
            print(list(chunks()))
            ---
            `chunks()` made a second generator, and that one starts at the top of the body.
            ```

            `list()` collects what is left, not everything the generator ever had. A value that was taken
            earlier does not come back:

            ```python
            def letters():
                yield "a"
                yield "b"
                yield "c"

            gen = letters()
            print(next(gen))
            # a
            print(list(gen))
            # ['b', 'c']
            ```

            ### When nothing is left

            `next()` cannot hand back a value from an exhausted generator, so it raises an exception
            called `StopIteration`. A `for` loop and `list()` catch that exception for you and stop
            quietly. That is why the second loop above printed nothing. A `next()` call of your own does
            not catch it.

            ```quiz
            `gen` is a generator with two values, and both have been taken with `next(gen)`. What does a third `next(gen)` do?
            - [x] It raises `StopIteration` :: Right. The body has ended, so there is no value to hand back. Without a `try`, the program stops with a traceback whose last line is `StopIteration`.
            - [ ] It hands back `None` :: `None` can be a real value that a generator yields, so Python does not use it as the sign for "finished". It raises an exception instead.
            - [ ] It starts again and hands back the first value :: A generator never goes back to the top. Only a new call of the generator function gives you the first value again.
            ```

            **Watch out:** an exhausted generator is not an error. A `for` loop over it runs zero times,
            and `list()` of it is `[]`. When a loop over a generator does nothing, check whether an earlier
            line has already used the generator up.

            **In short:** a generator hands out each value once, and for a second round you call the
            generator function again.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`. For each line, ask yourself what is still left in the generator.
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
            `next(gen)` takes the first value, and `print` shows it as plain text: `Hel`. `list(gen)`
            collects what is left, which is only `"lo"`, so the second line is the list `['lo']`. Now the
            generator is exhausted, and the next `list(gen)` finds nothing: `[]`. The last line calls
            `tokens()` again. That makes a new generator, which starts at the top of the body, so `list`
            collects both values: `['Hel', 'lo']`. Python prints the strings inside a list with single
            quotes.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "A generator only moves forward. A value that has been taken is gone from that generator.",
            "After `next(gen)` took the first value, `list(gen)` collects only what is left. After that, nothing is left. The last line does not read from `gen` at all: it calls the function again.",
            "Write four lines. The first is one value as plain text. The other three are lists, written the way Python prints a list, with square brackets and with single quotes around each string: first the values that are still left, then what an exhausted generator gives, then the values of a brand-new generator.",
        ],
    },
    {
        "id": "generators-s3",
        "title": "Yield the even numbers",
        "lesson": r'''
            ## Hand out only the matches

            Your app keeps a record of what every request cost, and you care only about the expensive ones. A normal function would collect those costs in a list and return it, so every match has to exist before anyone sees the first. A generator can hand the matches out one at a time instead.

            Put the `yield` inside an `if`, and put the `if` inside a `for` loop:

            ```python
            def expensive(costs, limit):
                for cost in costs:
                    if cost > limit:
                        yield cost

            print(list(expensive([0.2, 1.5, 0.7, 3.0], 1.0)))
            # [1.5, 3.0]
            ```

            The loop looks at one cost after another. When the `if` condition is true, the `yield` hands that cost out and the function pauses, as in the earlier steps. When the condition is false, the `yield` line is skipped, nothing is handed out, and the loop moves on to the next cost. A generator that passes on only the values that pass a test is often called a **filter**.

            Skipped values cost no pause at all. Predict what this prints, and think about which lines run before the first `got`:

            ```predict
            def big(numbers):
                for n in numbers:
                    print("check", n)
                    if n > 10:
                        yield n

            for x in big([5, 20, 7]):
                print("got", x)
            ---
            The loop asks for a value, so the body starts. It checks 5, and the condition is false, so the body goes straight on to the next number without pausing. It checks 20, the condition is true, and `yield` hands 20 to the loop, which prints `got 20`. When the loop asks again, the body resumes after the `yield`, checks 7, finds nothing to hand out, and ends. That ends the `for` loop too.
            ```

            The condition decides which values come out. Fill the gap so that the generator hands out the words that have 3 letters or fewer:

            ```fill
            def short_words(words):
                for w in words:
                    if len(w) ___ 3:
                        yield w

            print(list(short_words(["a", "hello", "yes", "model"])))
            ---
            - [x] <= :: Yes. The words `a` (1 letter) and `yes` (3 letters) pass, so the list is `['a', 'yes']`.
            - [ ] < :: This keeps only the words with fewer than 3 letters. `yes` has exactly 3, so it is left out and only `['a']` comes out.
            - [ ] > :: This keeps the long words, `hello` and `model`. It is the opposite of what we want.
            - [ ] == :: This keeps only words of exactly 3 letters, so only `['yes']` comes out. `a` is shorter, and it should come out too.
            ```

            If no value passes the test, the generator hands out nothing. `list()` of it is `[]`, and a `for` loop over it runs zero times. That is not an error.

            **Watch out:** the `yield` must be inside the `if`. If it sits at the same indentation as the `if`, it runs for every item, and the generator hands out the matches and the other values too.

            **In short:** a `yield` inside an `if` hands out only the values that pass the test, and the loop goes on silently past the rest.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Your app has a list of whole numbers, and only some of them matter. The function `evens` should hand out the even numbers one at a time, as a generator. A whole number is even when it divides by 2 with nothing left over (2, 4, 6, 0, ...).

            **Your job:** the function is already in the editor except for one line, marked `___`. The `if` already finds the even numbers, but nothing is handed out yet. Replace `___` with the line that hands out each even number.

            **What goes in**
            - `numbers`: a list of whole numbers, for example `[1, 2, 3, 4]`

            **What comes out**
            - a generator that hands out each even number of `numbers`, one at a time

            **Rules**
            - `evens` must be a generator function, not a function that returns a list. A check tests this.
            - The even numbers come out in the same order as in `numbers`.
            - If there is no even number, nothing comes out: `list(evens([1, 3, 5]))` is `[]`.

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
            "Look at the first example of the lesson. Which keyword sits inside the `if` there, and what does it do with the value?",
            "The `if` already picks out the even numbers. The missing line only has to hand the current number to whoever is looping, and the function then carries on with the next number.",
            "Write one line inside the `if`: first the keyword that hands out a value, then the name of the loop variable that holds the current number.",
        ],
    },
    {
        "id": "generators-s4",
        "title": "Fix the bug: only one line",
        "lesson": r'''
            ## Why only one value came back

            You wrote a function that should give back every model name in a list. You run it and get one name, as plain text, and no error. Where did the other names go?

            Look at what happens to a loop when the function reaches `return`:

            ```python
            def first_model(models):
                for m in models:
                    print("looking at", m)
                    return m

            print(first_model(["gpt-4o", "claude", "llama"]))
            # looking at gpt-4o
            # gpt-4o
            ```

            The loop looked at one name only. `return` ends the whole function on the spot, even in the middle of a loop, so `claude` and `llama` were never visited.

            `yield` behaves differently. It hands a value out and pauses the function, and the loop is still alive when the function is asked again:

            ```python
            def every_model(models):
                for m in models:
                    print("looking at", m)
                    yield m

            print(list(every_model(["gpt-4o", "claude", "llama"])))
            # looking at gpt-4o
            # looking at claude
            # looking at llama
            # ['gpt-4o', 'claude', 'llama']
            ```

            Now check that you can tell where such a loop stops. Predict what this prints:

            ```predict
            def first_even(numbers):
                for n in numbers:
                    print("checking", n)
                    if n % 2 == 0:
                        return n

            print(first_even([3, 5, 8, 10]))
            print("done")
            ---
            The loop checks 3 and 5, and the condition is false for both. It checks 8, the condition is true, and `return n` ends the function and hands back 8. The number 10 is never checked, so there is no `checking 10` line. The outer `print` shows the returned 8, and the last line prints `done`.
            ```

            Match each statement to what it does inside a loop:

            ```match
            `return m` :: ends the whole function, so the loop never reaches the other items
            `yield m` :: hands out m and pauses, and the loop goes on at the next request
            `print(m)` :: shows m on the screen and the loop goes on at once, but nothing is handed to the caller
            ```

            **Watch out:** a function becomes a generator function only because it contains `yield`. After you change `return` to `yield`, the callers get a generator, not a single value, so they have to loop over it or call `list()` on it.

            **In short:** `return` inside a loop ends the function at the first pass, and `yield` hands out a value and lets the loop go on.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A document is a list of lines, and some of the lines are blank. Before the lines are processed, a helper should skip the blank ones and hand out all the others. The helper in the editor is supposed to be a generator, but it stops as soon as it finds the first good line, and it gives that line back as plain text.

            **Your job:** fix the bug in `non_empty(lines)` so that it is a generator function that hands out every line that is not blank. The code is already there. What is wrong is what the function does when it finds a good line.

            **What goes in**
            - `lines`: a list of strings, for example `["hi", "", "  ", "there"]`

            **What comes out**
            - a generator that hands out every line that is not blank, unchanged, one at a time, in the original order

            **Rules**
            - A line is blank when it is empty or contains only whitespace, so `""` and `"  "` are blank.
            - If every line is blank, nothing comes out.
            - `non_empty` must be a generator function. A check tests this.

            **Examples**
            ```python
            list(non_empty(["hi", "", "  ", "there"]))   # ["hi", "there"]
            list(non_empty(["", " "]))                   # []
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
            "Run the function by hand on `[\"hi\", \"\", \"there\"]`. At which line does it stop for the first time, and what happens to the items after it?",
            "A function that ends the moment it finds a good line can never find a second one. The lesson showed another keyword that hands a value out and lets the loop carry on afterwards.",
            "Only the line inside the `if` has to change. Replace the keyword that ends the function with the one that hands a value out and pauses. The loop and the test stay as they are.",
        ],
    },
    {
        "id": "generators-s5",
        "title": "Stream the words",
        "lesson": r'''
            ## Pieces that arrive one at a time

            When a chat app shows a reply, the words appear one after another while the model is still writing. The code that draws the reply cannot wait for the whole text. It has to handle each piece as soon as the piece exists. How can you try that code before a real model is connected?

            A generator is a good stand-in, because it hands out one value at a time. Here is one that hands out the letters of a word, and a loop that reacts to every letter:

            ```python
            def stream_letters(word):
                for letter in word:
                    yield letter

            for piece in stream_letters("hey"):
                print("got", piece)
            # got h
            # got e
            # got y
            ```

            The generator and the loop take turns. The loop gets `h` and prints it, then the generator goes on and hands out `e`, and so on. A series of values handed out one at a time like this is called a **stream**.

            ```quiz
            The loop has just printed `got h`. What has the generator done with the letters `e` and `y` so far?
            - [x] Nothing yet. It is paused at the `yield` that handed out `h` :: Right. The generator looks at the next letter only when the loop asks for it, so `e` and `y` have not been touched.
            - [ ] It has already collected all three letters in a list :: A generator does not build a list. Each letter is produced when it is asked for, which is why it works on a text that is still being written.
            - [ ] It has thrown them away :: Nothing is thrown away. The letters are still waiting in the string, and the generator will reach them on the next requests.
            ```

            The `for` loop inside a generator can go through any list. To make a stream of pieces from a text, cut the text into a list first. The `split(",")` method from the strings chapter cuts a string at every comma:

            ```python
            def stream_tags(text):
                for tag in text.split(","):
                    yield tag

            print(list(stream_tags("ai,python,rag")))
            # ['ai', 'python', 'rag']
            ```

            Put these lines in order to get a program that streams two model names and prints each name on a line of its own:

            ```order
            def stream_models(models):
                for model in models:
                    yield model
            for name in stream_models(["gpt-4o", "claude"]):
                print(name)
            ---
            The `def` comes first, because the function must exist before the loop calls it. The `for` loop sits inside the function, and the `yield` sits inside that loop. The loop that uses the stream comes last and prints `gpt-4o` and then `claude`.
            ```

            **Watch out:** do not `yield` the whole list. Writing `yield` followed by the list of tags hands out one value, the entire list, so the loop receives a single piece instead of three. Yield inside the loop, one item per pass.

            **In short:** to turn a list of pieces into a stream, loop over the list and `yield` each piece.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A chat app shows a model's reply one word at a time. To test the screen code before a real model is connected, you want a stand-in: a function that takes a finished text and hands it out word by word, the way a real model would.

            **Your job:** write the generator function `stream_words(text)`. Every time something asks it for a value, it hands out the next word of `text`.

            **What goes in**
            - `text`: a string, for example `"Hello from the model"`

            **What comes out**
            - a generator that hands out the words of `text` as strings, one at a time, in the order they appear in the text

            **Rules**
            - It must be a generator function, so calling it gives a generator and not a list. A check tests this.
            - Words are separated by whitespace. Several spaces in a row count as one gap, so `"a  b"` has the words `"a"` and `"b"` and never an empty word.
            - Empty text hands out nothing.

            **Examples**
            ```python
            gen = stream_words("Hello from the model")
            next(gen)                                      # "Hello"
            next(gen)                                      # "from"
            list(stream_words("RAG  needs   retrieval"))   # ["RAG", "needs", "retrieval"]
            list(stream_words(""))                         # []
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
            "The last example of the lesson turned a string into a list of pieces and then handed each piece out. What did its `for` loop go through?",
            "Cut `text` into its words with the string method that treats any run of whitespace as a single gap, then loop over those words and hand out each one.",
            "In order: cut the text into words with that method, start a `for` loop over the result, and inside the loop hand out the current word. There is no list to build and no `return`.",
        ],
    },
    {
        "id": "generators-1",
        "title": "Fake token stream",
        "lesson": r'''
            ## Send text a piece at a time

            A reply may arrive in small pieces instead of as one complete string. To practice that behavior without a network, you can walk along existing text and hand out a short slice whenever the caller asks for more.

            ```python
            text = "notebook"
            for offset in range(0, len(text), 3):
                print(text[offset:offset + 3])
            # not
            # ebo
            # ok
            ```

            The third argument to `range` is the **step**: the distance between successive numbers. Here the starting positions are zero, three, and six. Each slice ends three positions after its start, and the stop position itself is excluded.

            ```predict
            print(list(range(0, 7, 3)))
            print("notes"[3:6])
            ---
            range stops before seven, so it produces 0, 3, and 6. The slice reaches beyond the five-character string safely and gives the remaining text es.
            ```

            A slice can end beyond the available text; Python returns only the characters that exist. That makes a shorter final piece natural. The range must still stop before the text length, so it does not start an empty extra piece when the length divides exactly.

            You already know that `yield` pauses a function and hands out one value. Using it with these slices makes the production of pieces lazy: no later slice is produced until the caller requests it. A piece added to a streamed reply is often called a **delta**.

            ```quiz
            The input text is empty. How many starting positions should the stream visit?
            - [x] Zero :: There is no text to send, so an empty range should produce no pieces.
            - [ ] One :: Yielding an empty string would add a piece that contains no input characters.
            ```

            **Watch out:** a step of zero makes `range` raise `ValueError`. A piece size must move the position forward.

            **In short:** stepped starting positions and safe slices let a generator hand out consecutive pieces of text.
        ''',
        "hints": [
            "Revisit how a stepped range supplies starting positions.",
            "Each position identifies the beginning of one slice. Yield that slice rather than returning a list of slices.",
            "Visit starts separated by the requested size, stopping before the text length. Yield up to that many characters from each start; slicing handles the shorter remainder.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Simulate a model streaming its answer in small pieces (called *deltas*).

            **Your job:** write `stream_deltas(text, size)` - a **generator function** (it uses `yield`)

            **What goes in**

            - `text`: the full answer as a string, e.g. `"Hello world"`
            - `size`: how many characters per piece, an `int` of at least 1, e.g. `4`
            - **Yields:** consecutive pieces of `text` (strings), in order, one per `yield`

            **What comes out**
            - A generator handing out strings one at a time. Joining its pieces in order reconstructs the original text.

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
            ## Add values without storing an intermediate list

            You want one total from thousands of records. Building a list of every intermediate number wastes space when you will immediately add those numbers and discard the list. Python can calculate one value at a time instead.

            ```python
            lengths = (len(name) for name in ["oak", "birch", "elm"])
            print(sum(lengths))
            # 11
            print(list(lengths))
            # []
            ```

            The parentheses create a **generator expression**. Its shape resembles a list comprehension, but it computes each result only when requested. `sum` requests numbers one by one, adds them, and keeps a running total. The generator is exhausted afterwards, which explains the empty list on the second line.

            ```fill
            numbers = [2, 5, 8]
            print(___(n * 2 for n in numbers))
            ---
            - [x] sum :: Adding the three generated values gives 30.
            - [ ] max :: This keeps only the largest generated value, which is 16.
            - [ ] min :: This keeps only the smallest generated value, which is 4.
            ```

            When the expression is the only argument in a function call, its own parentheses may be left out. The parentheses of the call are enough. This saves punctuation without changing how the generator behaves.

            A generator expression can read a list or another generator. It does not need to index the input or know its length first. This is useful for inputs that permit only one pass, such as a stream of documents.

            ```quiz
            What does sum return when its generator produces no numbers?
            - [x] 0 :: Zero is the starting total, and no values are added.
            - [ ] None :: sum has a defined empty-input result rather than an absent answer.
            ```

            **Watch out:** changing the parentheses to square brackets eagerly builds a whole list. The numerical answer may match, but the memory behavior changes.

            **In short:** a generator expression supplies intermediate values only when the consumer asks for them.
        ''',
        "hints": [
            "Which consumer adds up a sequence of numbers?",
            "Generate one word count per document without making a list of those counts.",
            "Split each document on whitespace, measure how many pieces it has, and feed those measurements through a generator expression to the adding consumer.",
        ],
        "difficulty": 1,
        "prompt": r'''
            Count the words in a whole document collection without building a big list in
            memory.

            **Your job:** write `total_words(docs)`

            **What goes in**

            - `docs`: any iterable of document strings - a list like `["the cat", "sat"]`, or
              a generator that produces strings

            **What comes out**
            - an `int`, the total number of words across all documents

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
            ## Stop searching when you have an answer

            You want the first record that needs attention. Reading the rest of a large stream after finding it would waste work, and the stream might never end. Ask for one matching item, then stop.

            ```python
            scores = [4, 9, 2, 12]
            matches = (score for score in scores if score > 8)
            print(next(matches, None))
            # 9
            print(next(matches, None))
            # 12
            ```

            The condition in the generator expression filters out values that do not qualify. `next` asks that generator to keep reading until it can hand back one qualifying value. It does not collect all matches first.

            The second argument to `next` is a **default**. When nothing remains, Python gives back that value instead of raising `StopIteration`. Choose a default that your caller can distinguish from a real result, such as `None` when real results are strings.

            ```predict
            values = iter(["ready"])
            print(next(values, "missing"))
            print(next(values, "missing"))
            ---
            The first request consumes the only string. The second finds the iterator exhausted and returns the supplied fallback.
            ```

            `iter` turns an iterable, such as a list, into an object that remembers its current reading position. That object is an **iterator**. A generator already is an iterator, so it can be passed directly to `next`.

            ```quiz
            Why not build a list of all matches before selecting the first one?
            - [x] It would read beyond the answer :: The list construction consumes every input item before selection happens.
            - [ ] Lists change the matching values :: Building a list does not itself change those values.
            ```

            **Watch out:** when `next` has a default argument, put parentheses around a generator expression passed as its other argument. Without them, Python reports that the generator expression must be parenthesized.

            **In short:** a filtered generator and `next` find one result without reading the rest of the stream.
        ''',
        "research": {
            "note": "Read the docs for the built-in `next()` - especially what its second argument does - then come back.",
            "links": [{"title": "next() - Python built-in functions", "url": "https://docs.python.org/3/library/functions.html#next"}],
        },
        "prompt": r'''
            Before sending text chunks to a model, find the first one that is too long for the
            size limit.

            **Your job:** write `first_too_long(chunks, limit)`

            **What goes in**

            - `chunks`: any iterable of strings - a list, or a generator, e.g. `["short", "a much longer chunk"]`
            - `limit`: an `int`, the maximum allowed number of characters, e.g. `10`

            **What comes out**
            - the **first** chunk (a string) whose length is **greater than** `limit`,
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
            "You only need one qualifying item, so which operation asks for just the next result?",
            "Filter lazily with the strict length condition, and supply a default for no match.",
            "Describe the qualifying strings in a generator expression. Pass that iterator to next together with the absent-result default; keep the expression parenthesized because there are two arguments.",
        ],
    },
    {
        "id": "generators-8",
        "title": "Preview a stream",
        "difficulty": 1,
        "lesson": r'''
            ## Take a bounded preview of an endless stream

            A source may keep producing log entries indefinitely. To show a preview, you need to request a limited number of items before building a list. Reading the whole source first would never finish.

            ```python
            from itertools import count, islice
            source = count(10)
            print(list(islice(source, 3)))
            # [10, 11, 12]
            print(next(source))
            # 13
            ```

            `count` produces consecutive numbers without an end. `islice`, from the standard-library module `itertools`, makes a limited view of an iterable. Here it allows only three values through. The call to `list` then collects those three values, not the endless original source.

            ```predict
            from itertools import islice
            source = iter(["a", "b", "c"])
            print(list(islice(source, 0)))
            print(next(source))
            ---
            Taking zero items produces an empty list and leaves the source untouched. Its next value is still a.
            ```

            The limit is a maximum, not a promise that enough input exists. If the source ends early, `islice` ends with it. You do not need to catch an error to handle a short stream.

            Like a generator expression, `islice` is lazy. Creating it does not collect its values. A loop or another consumer asks for them later. This separation lets you put a safe bound around an expensive or infinite source before doing any collection.

            ```quiz
            The source has two values and the requested limit is five. What does list(islice(source, 5)) contain?
            - [x] The two available values :: It stops when the source ends.
            - [ ] Five values padded with None :: islice never invents missing input values.
            - [ ] No values :: A short source is still a valid source.
            ```

            **Watch out:** ordinary slicing on a generator raises `TypeError` because generators have no indexed storage. Converting an infinite source to a list first is worse: it never finishes.

            **In short:** limit the iterator before collecting a preview.
        ''',
        "research": {
            "note": "Skim the `itertools` docs: find `islice` and look at its example calls, then come back.",
            "links": [{"title": "itertools.islice - Python docs", "url": "https://docs.python.org/3/library/itertools.html#itertools.islice"},
                      {"title": "Generators - Functional Programming HOWTO", "url": "https://docs.python.org/3/howto/functional.html#generators"}],
        },
        "prompt": r'''
            Show a quick preview of a stream (for example the first log lines, or the first
            items of an endless feed) without reading the whole thing.

            **Your job:** write `preview(stream, n)`

            **What goes in**

            - `stream`: any iterable - a list, a generator, or an **infinite** iterator like
              `itertools.count()`
            - `n`: an `int` (0 or more), how many items to show, e.g. `3`

            **What comes out**
            - a **list** of the first `n` items, in order

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
            "Review the itertools tool that limits how much of a source can be read.",
            "Apply the limit before collecting values. Reversing those operations would consume an infinite input.",
            "Import the iterator-slicing tool, make a bounded view of the source using n, then collect only that view into the required result type.",
        ],
    },
    {
        "id": "generators-9",
        "title": "Prepend the system prompt",
        "difficulty": 1,
        "lesson": r'''
            ## Pass through another stream's items

            Your stream needs a marker before or after existing items. You could write a loop whose only job is to yield every incoming value. Python has a shorter form for that exact job.

            ```python
            def tagged(lines):
                yield "BEGIN"
                yield from lines
                yield "END"

            print(list(tagged(["one", "two"])))
            # ['BEGIN', 'one', 'two', 'END']
            ```

            `yield from lines` hands out the values of `lines` individually and in order. When that iterable finishes, your function continues with the next statement. Passing work to another iterable this way is called **delegation**.

            ```predict
            def tagged(lines):
                yield "BEGIN"
                yield from lines
                yield "END"
            print(list(tagged([])))
            ---
            The empty input contributes no values, but the statements before and after yield from still run. The result contains BEGIN and END.
            ```

            Delegation stays lazy. The outer generator asks the inner iterable for a value only when its own caller requests another value. It can therefore wrap a generator without converting the entire source into a list. That matters when the input is large, expensive, or still arriving.

            Contrast `yield lines` with `yield from lines`. The first hands out one value: the iterable itself. The second hands out its contents. Neither copies or edits the input items merely by passing them along.

            ```match
            `yield value` :: hands out one value
            `yield from values` :: hands out each value from the iterable
            `return` :: finishes the generator rather than sending another item
            ```

            **Watch out:** strings are iterable too. Delegating to a string sends one character at a time. If you want the entire string to be one item, use an ordinary yield for it.

            **In short:** use one yield for one item and yield from to pass along an existing stream.
        ''',
        "prompt": r'''
            Chat APIs expect the *system* message first, followed by the conversation. Build that
            message stream lazily.

            **Your job:** write `with_system(system, messages)` - a **generator function**

            **What goes in**

            - `system`: the system prompt, a string, e.g. `"Be brief."`
            - `messages`: any iterable of message dicts (a list or a generator), e.g.
              `[{"role": "user", "content": "Hi"}]`
            - **Yields:** first the dict `{"role": "system", "content": system}`, then every
              message from `messages`, unchanged and in order

            **What comes out**
            - A generator whose first item is the system-message dictionary and whose later items are the original messages in order.

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
            "There is one new message, followed by an existing sequence of messages.",
            "Use an ordinary yield for the new item and delegation for the existing stream.",
            "Construct and hand out the system message first. Afterwards delegate to the original messages iterable, without collecting or changing it.",
        ],
    },
    {
        "id": "generators-3",
        "title": "Batch for embeddings",
        "hints": [
            "A batch is a small bounded preview from one continuing iterator.",
            "Create the iterator once, then repeatedly read a limited group from that same position.",
            "Reject an invalid batch size. Take up to the size limit into a fresh list, stop if that list is empty, otherwise hand it out and repeat.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Embedding APIs accept a limited number of inputs per request, so texts are sent in
            *batches*.

            **Your job:** write `batched(iterable, n)` - a **generator function** (it uses `yield`)

            **What goes in**

            - `iterable`: anything you can loop over - a list, a string, a `range`, or another
              generator (possibly infinite, e.g. `itertools.count()`)
            - `n`: the maximum batch size, an `int`, e.g. `2`
            - **Yields:** **lists** of up to `n` consecutive items, in order

            **What comes out**
            - A generator handing out lists, with at most the requested number of consecutive input items per list.

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
            "Separate extracting useful text from displaying useful text.",
            "The extractor should safely skip missing or empty nested values. The display function must act on each piece before requesting the next.",
            "Read choices safely and examine the first delta when present. Yield only nonempty text. In render, print each arriving piece without a separator, retain it for the returned string, and print one final newline.",
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

            **Your job:** write `text_deltas(chunks)` and `render(chunks)`

            **What goes in**

            - `chunks`: any iterable of chunk dicts like the ones above (a list, or a generator
              that is still receiving data)
            - `text_deltas` **yields:** the `content` strings found at
              `chunk["choices"][0]["delta"]["content"]`, in order
            - `render` **returns:** the full reply text (a `str`), and also prints it

            **What comes out**
            - `text_deltas` yields useful text pieces. `render` prints them incrementally, adds a final newline, and gives back their combined string.

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
            ## Make an object remember the next position

            Sometimes the progress of a stream belongs in an object. You may want explicit attributes for its current position and whether it has finished. A class can support the same next-item behavior as a generator.

            ```python
            class Once:
                def __init__(self, value):
                    self.value, self.finished = value, False
                def __iter__(self):
                    return self
                def __next__(self):
                    if self.finished:
                        raise (StopIteration)
                    self.finished = True
                    return self.value
            print(list(Once("ready")))
            # ['ready']
            ```

            The two special methods form the **iterator protocol**: the agreement that lets `for`, `next`, and `list` read values. `__iter__` supplies the iterator. When an object is its own iterator, it returns itself. `__next__` supplies one value or raises `StopIteration` when finished.

            ```quiz
            After the Once object has produced its value, what should another next call do?
            - [x] Signal exhaustion again :: Exhaustion is a persistent state for this iterator.
            - [ ] Start over automatically :: Restarting would violate the promise that the same iterator is exhausted.
            - [ ] Return None :: None would be another ordinary item, not the signal that iteration has ended.
            ```

            Putting it together for moving windows requires two decisions: where the next window starts, and which window is the last. Keep those decisions distinct. A final window might reach the end before the next starting position would pass it. Mark completion at the moment the final window is produced.

            The class constructor should check impossible settings before iteration begins. An empty input should start already finished. That keeps later `__next__` calls focused on one task: either return a window and advance state, or report exhaustion.

            **Watch out:** returning a value without updating the stored position makes every request repeat the same window. The program runs but a consuming loop may never finish.

            **In short:** an iterator object stores progress between calls and uses StopIteration to signal a permanent end.
        ''',
        "hints": [
            "The protocol needs both a way to obtain the iterator and a way to request one value.",
            "Keep a current position and a persistent finished flag. The stopping rule is about the first window reaching the end.",
            "Validate settings in construction and mark empty input finished. Each request checks completion, takes the current window, records whether it reached the end, advances the position, and returns the window.",
        ],
        "difficulty": 3,
        "prompt": r'''
            RAG pipelines split documents into overlapping token *windows* before embedding
            them.

            **Your job:** write a class `SlidingWindow(tokens, size, stride)` that is an **iterator**

            **What goes in**

            - `tokens`: a list of tokens, e.g. `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` or `["a", "b"]`
            - `size`: the window length, an `int`, e.g. `4`
            - `stride`: how far each window moves forward, an `int`, e.g. `3`
            - **Each `next()` returns:** one window, a list `tokens[start:start + size]`, for
              `start = 0, stride, 2*stride, ...`

            **What comes out**
            - An iterator object. Each next-item request gives back one window list until the defined stopping point, then raises StopIteration.

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
            "Decide whether a value is a leaf before treating it as a container.",
            "Strings and bytes must stay whole; dictionaries contribute values; other iterables contribute their items.",
            "Handle those special cases first. For remaining values, try obtaining an iterator: failure means a leaf. Otherwise recursively delegate for each item, never collecting the entire source.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Tool results and message contents can be nested to any depth. Pull out every plain
            value (every *leaf*) so it can be indexed.

            **Your job:** write `flatten(obj)` - a recursive **generator function** (it calls itself for the nested parts)

            **What goes in**

            - `obj`: any value - a list, tuple, dict, generator, string, number, `None`, ... nested
              in any combination, e.g. `["a", ("b", ["c"]), {"k": "d"}]`
            - **Yields:** the leaves of `obj`, one per `yield`, in order

            **What comes out**
            - A generator handing out leaf values, preserving traversal order and treating complete strings and bytes as leaves.

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
