TOPIC = {
    "id": "async",
    "title": "Async Python",
    "track": "production-python",
    "order": 5,
    "requires": ["functions", "errors"],
    "summary": """
        Coroutines with async def / await, running them with asyncio.run, firing many
        LLM calls concurrently with gather, limiting concurrency, timeouts, error
        handling and async generators for streaming.
    """,
    "concepts": ["async def", "await", "asyncio.run", "asyncio.gather", "asyncio.Semaphore",
                 "asyncio.wait_for", "return_exceptions", "async generators", "async for"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["async", "await", "asyncio", "coroutine", "event loop", "gather", "concurrent",
                 "asyncio.run", "asyncio.sleep", "timeout", "timeouterror", "wait_for", "semaphore",
                 "async for", "async generator", "return_exceptions"],
    "cards": [
        {
            "syntax": "async def name():  /  await coro",
            "explain": "Calling an async def function returns a coroutine. await runs it and evaluates to its return value.",
            "example": r'''
                import asyncio
                async def greet(name):
                    return "hello " + name
                async def main():
                    print(await greet("Ana"))
                asyncio.run(main())
                # hello Ana
            ''',
        },
        {
            "syntax": "asyncio.run(coro)",
            "explain": "Runs a coroutine from normal code and returns its result. Inside async def, use await instead.",
            "example": r'''
                import asyncio
                async def slow_add(a, b):
                    await asyncio.sleep(0.01)
                    return a + b
                print(asyncio.run(slow_add(2, 3)))
                # 5
            ''',
        },
        {
            "syntax": "await asyncio.gather(a, b)",
            "explain": "Runs several coroutines so that their waits overlap. Gives a list of results in argument order.",
            "example": r'''
                import asyncio
                async def up(text, delay):
                    await asyncio.sleep(delay)
                    return text.upper()
                async def main():
                    print(await asyncio.gather(up("a", 0.02), up("b", 0.01)))
                asyncio.run(main())
                # ['A', 'B']
            ''',
        },
        {
            "syntax": "asyncio.gather(a, b, return_exceptions=True)",
            "explain": "An exception from one coroutine is put in the result list instead of being raised.",
            "example": r'''
                import asyncio
                async def half(n):
                    return 10 // n
                async def main():
                    a, b = half(5), half(0)
                    print(await asyncio.gather(a, b, return_exceptions=True))
                asyncio.run(main())
                # [2, ZeroDivisionError('division by zero')]
            ''',
        },
        {
            "syntax": "await asyncio.wait_for(coro, seconds)",
            "explain": "Runs coro. If it has not finished after that many seconds, stops it and raises TimeoutError.",
            "example": r'''
                import asyncio
                async def main():
                    try:
                        await asyncio.wait_for(asyncio.sleep(1), 0.01)
                    except TimeoutError:
                        print("timed out")
                asyncio.run(main())
                # timed out
            ''',
        },
        {
            "syntax": "async for item in agen():",
            "explain": "Reads an async generator: an async def function that uses yield. Only allowed inside async def.",
            "example": r'''
                import asyncio
                async def stream():
                    yield "Hel"
                    yield "lo"
                async def main():
                    print([token async for token in stream()])
                asyncio.run(main())
                # ['Hel', 'lo']
            ''',
        },
    ],
}

LESSON = r'''
## Async Python: chapter notes

A **server** is a remote computer that answers requests sent over a network. A call to a web API
(an API is a service your program sends requests to), such as an LLM (large language model)
service that writes text, spends most of its time waiting
for the server to answer. **Async** code lets one program start a second call while
the first one is still waiting.

### Coroutines and await

`async def` defines a **coroutine function**. Calling it does not run its body. The call returns a
**coroutine**: an object that holds the function body and its arguments, ready to run.

`await coro` runs the coroutine and evaluates to its return value. You can only write `await`
inside an `async def` function.

`asyncio.run(coro)` starts the **event loop**: the object in the `asyncio` module that runs
coroutines. It runs `coro` to the end and returns its result. You call it from normal code.

```python
import asyncio

async def fake_llm(prompt):
    await asyncio.sleep(0.01)
    return prompt.upper()

async def main():
    coro = fake_llm("hi")
    print(type(coro).__name__)
    reply = await coro
    print(reply)

asyncio.run(main())
# coroutine
# HI
```

### The event loop and asyncio.sleep

The event loop runs one coroutine at a time. When that coroutine reaches an `await` that has to
wait, the event loop pauses it there and runs another coroutine that is ready.

`await asyncio.sleep(s)` pauses only the current coroutine for `s` seconds. `time.sleep(s)` stops
the whole program, so the event loop cannot run anything else. Preventing the event loop
from running other coroutines this way is called **blocking** it. Never use `time.sleep`
in async code.

### asyncio.gather

`asyncio.gather(a, b, ...)` takes several coroutines and runs them **concurrently**: their waiting
periods overlap. `await` on it gives a list of their results. The list follows the order of the
arguments, not the order in which the coroutines finished.

```python
import asyncio

async def fake_llm(prompt, delay):
    await asyncio.sleep(delay)
    print("done", prompt)
    return prompt.upper()

async def main():
    replies = await asyncio.gather(fake_llm("a", 0.02), fake_llm("b", 0.01))
    print(replies)

asyncio.run(main())
# done b
# done a
# ['A', 'B']
```

Step through the stages to see when each coroutine runs and when it is paused.

```diagram
{"type":"flow","title":"Order of events in asyncio.gather(fake_llm(\"a\", 0.02), fake_llm(\"b\", 0.01))","steps":[{"label":"main awaits gather","detail":"gather schedules both coroutines on the event loop. main is paused at its await until both have finished.","code":"replies = await asyncio.gather(fake_llm(\"a\", 0.02), fake_llm(\"b\", 0.01))"},{"label":"a runs to its await","detail":"The event loop runs fake_llm(\"a\", 0.02) until it reaches await asyncio.sleep(0.02). That coroutine is now paused for 0.02 seconds.","code":"await asyncio.sleep(0.02)   # a is paused"},{"label":"b runs to its await","detail":"The event loop switches to fake_llm(\"b\", 0.01) and runs it until await asyncio.sleep(0.01). Both coroutines are now paused at the same moment.","code":"await asyncio.sleep(0.01)   # b is paused"},{"label":"b finishes first","detail":"After 0.01 seconds the event loop resumes b. It prints and returns 'B'. gather stores 'B' in position 1 because b was the second argument.","code":"done b\nresults so far: [not ready, 'B']"},{"label":"a finishes","detail":"After 0.02 seconds the event loop resumes a. It prints and returns 'A'. gather stores 'A' in position 0.","code":"done a\nresults so far: ['A', 'B']"},{"label":"main resumes","detail":"Both coroutines are finished, so the await in main evaluates to the list. The order is the argument order.","code":"print(replies)\n# ['A', 'B']"}]}
```

A loop that awaits each call in turn is sequential: `for p in prompts: reply = await call(p)`
starts each call only after the previous one has returned. To run them concurrently, write
`await asyncio.gather(*(call(p) for p in prompts))`. The generator expression creates one
coroutine per prompt, and the `*` passes each one to `gather` as a separate argument.

### Exceptions and timeouts

An exception raised inside a coroutine is raised again at the `await` that runs it. Catch it with
`try` / `except` around the `await`.

If one coroutine in a `gather` raises, `await asyncio.gather(...)` raises that exception. With
`return_exceptions=True`, the exception object is put in the result list instead.

```python
import asyncio

async def fake_llm(prompt):
    await asyncio.sleep(0.01)
    if prompt == "boom":
        raise ValueError("model refused")
    return prompt.upper()

async def main():
    outcomes = await asyncio.gather(
        fake_llm("a"), fake_llm("boom"), return_exceptions=True
    )
    print(outcomes)

asyncio.run(main())
# ['A', ValueError('model refused')]
```

`asyncio.wait_for(coro, t)` runs `coro`. If it has not finished after `t` seconds, `wait_for`
stops it and raises `TimeoutError`. Since Python 3.11, `asyncio.TimeoutError` is the same class as the built-in `TimeoutError`.

```python
import asyncio

async def slow_llm(prompt):
    await asyncio.sleep(1)
    return prompt.upper()

async def main():
    try:
        print(await asyncio.wait_for(slow_llm("hi"), 0.01))
    except TimeoutError:
        print("timed out")
    print(asyncio.TimeoutError is TimeoutError)

asyncio.run(main())
# timed out
# True
```

### Limiting concurrency

`asyncio.Semaphore(n)` is an object that lets at most `n` coroutines be inside its `async with`
block at once. The others pause at `async with` until one leaves the block. `async with` is the
form of `with` that async code uses. A **rate limit** is the maximum number of requests an API
accepts in a period of time. Use a semaphore to stay under it.

```python
import asyncio

active = []

async def fake_llm(prompt, sem):
    async with sem:
        active.append(prompt)
        print(prompt, "started, active:", active)
        await asyncio.sleep(0.01)
        active.remove(prompt)
    return prompt.upper()

async def main():
    sem = asyncio.Semaphore(2)
    replies = await asyncio.gather(
        fake_llm("a", sem), fake_llm("b", sem), fake_llm("c", sem)
    )
    print(replies)

asyncio.run(main())
# a started, active: ['a']
# b started, active: ['a', 'b']
# c started, active: ['c']
# ['A', 'B', 'C']
```

The list `active` holds the prompts that are inside the block. `c` pauses at `async with` until
`a` and `b` have left the block. Here both have left before `c` starts, so `active` holds only
`'c'`. `active` never holds more than 2 prompts.

### Async generators

An `async def` function that contains `yield` is an **async generator**. It can `await` between
items. You read it with `async for`, inside an `async def` function. In the example,
`await asyncio.sleep(0)` waits for zero seconds. It takes the place of waiting for a server.

```python
import asyncio

async def stream_reply():
    for token in ["Hel", "lo"]:
        await asyncio.sleep(0)
        yield token

async def main():
    async for token in stream_reply():
        print(token)

asyncio.run(main())
# Hel
# lo
```

### Common mistakes

- `reply = call("hi")` without `await` assigns a coroutine object, not the reply.
- `await` inside a plain `def` function is a `SyntaxError`. From normal code, use `asyncio.run(...)`.
- `asyncio.sleep(1)` without `await` creates a coroutine and never waits.
- A plain `for` loop over an async generator raises `TypeError`. Use `async for`.
- A `try` that wraps only the line that creates a coroutine catches nothing. The exception is raised at the `await`.

Docs: [asyncio tasks and coroutines](https://docs.python.org/3/library/asyncio-task.html)
'''

EXERCISES = [
    {
        "id": "async-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            ## A function that is allowed to wait

            Your program has ten questions for an LLM. It sends the first one, and then nothing happens
            for two seconds. The answer is being written on a computer far away, and your program can only
            wait for it. Ten questions, asked one after the other, add up to twenty seconds, and for
            almost all of that time your program does nothing at all.

            You would not stand next to a kettle until it boils. You would switch it on and do something
            else in the meantime. This chapter teaches your program the same habit: start a slow call, and
            use the waiting time to start the next one. That takes a new kind of function, one that can
            pause in the middle and carry on later. Here is the smallest one:

            ```python
            import asyncio

            async def shout(text):
                return text.upper() + "!"

            async def main():
                loud = await shout("hello")
                print(loud)

            asyncio.run(main())
            # HELLO!
            ```

            Three things are new, and nothing runs unless all three are there.

            - `async def` in place of `def`. The word `async` marks a function that is allowed to pause.
              Nothing pauses yet. That comes in the next step.
            - `await shout("hello")`. Read it as "run `shout`, wait until it has finished, and give me
              what it returned". The line below it runs only after that. You may write `await` only
              inside an `async def` function.
            - `asyncio.run(main())`. The first line of the file, `import asyncio`, loads the part of
              Python that knows how to run these functions. `asyncio.run(...)` is the way in from
              ordinary code: it runs `main` from top to bottom and comes back when `main` has finished.

            A function written with `async def` is called a **coroutine function**, or a **coroutine**
            for short. Code that is built from `async` and `await` is called **async** code.

            ```predict
            import asyncio

            async def add(a, b):
                return a + b

            async def main():
                first = await add(2, 3)
                second = await add(first, 10)
                print(first)
                print(second)

            asyncio.run(main())
            ---
            The first `await` runs `add(2, 3)` and hands back 5. Only then does the next line run, so `first` is already 5 when `add(first, 10)` is called, and that gives 15.
            ```

            ```quiz
            You write `x = await shout("hi")` at the bottom of a file, outside every function. What happens?
            - [x] Python refuses to start the program :: Right. `await` is only allowed inside an `async def` function. Python stops before it runs a single line, with `SyntaxError: 'await' outside function`.
            - [ ] `x` becomes `"HI!"` :: It would inside an `async def` function. Outside one, `await` is not allowed, and Python stops with `SyntaxError: 'await' outside function`.
            - [ ] The program waits for ever :: Nothing runs at all. Python reads the whole file first, finds the `await` in a place where it is not allowed, and stops with a `SyntaxError`.
            ```

            The program of this step has one more line that you have not met: `await asyncio.sleep(0)`. It
            stands for the waiting. It prints nothing and changes no value. The next step is about it.

            **Watch out:** an async function does not start when you call it the ordinary way. If the last
            line says `main()` where it should say `asyncio.run(main())`, nothing is printed, and Python
            shows `RuntimeWarning: coroutine 'main' was never awaited`.

            **In short:** `async def` makes a function that can pause, `await` runs one and gives you its
            result, and `asyncio.run(main())` starts the first one from ordinary code.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            import asyncio

            async def greet(name):
                await asyncio.sleep(0)
                return "hi " + name

            async def main():
                print("start")
                reply = await greet("Ana")
                print(reply)

            asyncio.run(main())
        ''',
        "solution": r'''
            start
            hi Ana
        ''',
        "explanation": r'''
            The last line, `asyncio.run(main())`, runs `main` from top to bottom. `main` first prints
            `start`. Then `await greet("Ana")` runs `greet`: its line `await asyncio.sleep(0)` is a wait of
            zero seconds and prints nothing, and its `return` builds `"hi Ana"`. The `await` hands that
            text back, it is stored under `reply`, and the last line of `main` prints it. Printed text has
            no quotes around it.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Start at the last line. `asyncio.run(main())` runs the body of `main` from top to bottom, so follow `main` one line at a time.",
            "`await greet(\"Ana\")` runs `greet` to its `return` and hands back what it returned. The line with `asyncio.sleep(0)` prints nothing.",
            "Your first line is what `main` prints before it awaits anything. Your second line is the text that `greet` builds from its two parts, printed by the last line of `main`. Printed text has no quotes around it.",
        ],
    },
    {
        "id": "async-s2",
        "title": "Wait politely",
        "difficulty": 0,
        "lesson": r'''
            ## Waiting without stopping everything

            To practise, you need a function that is slow in the same way as a call to an LLM: it does
            nothing for a moment, and then it has an answer. Calling a real LLM in every exercise would
            cost money, so this chapter fakes the wait.

            Python has an ordinary way to do nothing for a while. `time.sleep(2)` waits two seconds. The
            trouble is that it stops the whole program. Until the two seconds are over, no other line
            anywhere can run. That is standing next to the kettle.

            The `asyncio` module has its own version, made for async functions:

            ```python
            import asyncio

            async def fake_llm(question):
                print("asking:", question)
                await asyncio.sleep(0.05)
                return "answer to " + question

            print(asyncio.run(fake_llm("why?")))
            # asking: why?
            # answer to why?
            ```

            `await asyncio.sleep(0.05)` pauses this one function for 0.05 seconds. The rest of the program
            is not stopped. While `fake_llm` is paused, Python is free to run other async functions. This
            small program has no others, so all you notice is a short wait. Two steps from now there will
            be several, and the difference will show.

            The last line shows one more thing. `asyncio.run(...)` hands back whatever the function
            returned, so you can print it or store it under a name.

            Now the names. A wait that stops everything, as `time.sleep` does, is called **blocking**.
            `asyncio.sleep` is **non-blocking**. The part of `asyncio` that keeps track of the paused
            functions and decides which one runs next is called the **event loop**. `asyncio.run` starts
            it.

            Put these lines in order so that the program prints `kettle on` and then `kettle off`:

            ```order
            import asyncio
            async def boil():
                print("kettle on")
                await asyncio.sleep(0.05)
                print("kettle off")
            asyncio.run(boil())
            ---
            The function has to exist before the last line can run it. Inside the function the lines run from top to bottom: the first `print`, then the pause, then the second `print`.
            ```

            ```quiz
            Which line pauses one async function for a second and leaves the rest of the program free to run?
            - [x] `await asyncio.sleep(1)` :: Right. The function is paused at this line, and the event loop can run other async functions until the second is over.
            - [ ] `time.sleep(1)` :: This does wait, but it blocks. The event loop cannot run anything else until the second is over.
            - [ ] `asyncio.sleep(1)` :: Without `await`, nothing waits at all. The pause is prepared and never run, and Python shows `RuntimeWarning: coroutine 'sleep' was never awaited`.
            ```

            **Watch out:** `time.sleep` inside an async function gives no error. The program still works,
            only slower, because every other async function stands still during the wait. That makes this
            mistake hard to see, so check the module name: in async code it is `asyncio.sleep`, with
            `await` in front.

            **In short:** `await asyncio.sleep(seconds)` pauses one async function and lets the event loop
            run others in the meantime.
        ''',
        "prompt": r'''
            `fetch_reply` is a stand-in for a call to an LLM. It waits a moment, the way a real call waits
            for the computer that runs the model, and then it gives back a reply. The function is already
            written, except for one name.

            **Your job:** replace the gap `___` in `fetch_reply(prompt)` so that the function waits 0.01
            seconds without blocking, and then gives back the reply.

            **What goes in**
            - `prompt`: a string, for example `"hi"`

            **What comes out**
            - the text `reply: ` followed by the prompt, for example `"reply: hi"`. This part is already
              written.

            **Rules**
            - The gap is the name of a function in the `asyncio` module. It must be the kind of wait that
              does not block the event loop.
            - `fetch_reply` stays an `async def` function. A check tests this.

            **Examples**
            ```python
            asyncio.run(fetch_reply("hi"))          # returns "reply: hi"
            asyncio.run(fetch_reply("summarise"))   # returns "reply: summarise"
            ```
        ''',
        "starter": r'''
            import asyncio


            async def fetch_reply(prompt):
                await asyncio.___(0.01)
                return "reply: " + prompt
        ''',
        "tests": r'''
            import asyncio
            import inspect
            from solution import fetch_reply

            def test_fetch_reply_is_async_def():
                assert inspect.iscoroutinefunction(fetch_reply), "fetch_reply must be async def"

            def test_returns_reply_for_hi():
                got = asyncio.run(fetch_reply("hi"))
                assert got == "reply: hi", f"got {got!r}"

            def test_returns_reply_for_another_prompt():
                got = asyncio.run(fetch_reply("summarise"))
                assert got == "reply: summarise", f"got {got!r}"
        ''',
        "solution": r'''
            import asyncio


            async def fetch_reply(prompt):
                await asyncio.sleep(0.01)
                return "reply: " + prompt
        ''',
        "hints": [
            "Which function made `fake_llm` slow in the lesson?",
            "The `asyncio` module has its own version of the ordinary waiting function from the `time` module. The two have the same name. Only the `asyncio` one is awaited, and only that one leaves the event loop free.",
            "Look at the line with `await` in the first example of the lesson. The word between `asyncio.` and the opening bracket is what belongs in the gap.",
        ],
    },
    {
        "id": "async-s3",
        "title": "Fix the missing await",
        "difficulty": 0,
        "lesson": r'''
            ## What you get when you forget await

            You call your fake LLM, and what comes back is not a reply. It is some object you never asked
            for, and the next line stops with a `TypeError`. This is the most common mistake in async
            code. After this step you will recognise it at once.

            It starts with a fact that is easy to miss: calling an async function does not run it.

            ```python
            import asyncio
            async def get_score():
                return 7
            async def main():
                waiting = get_score()
                print(type(waiting).__name__)
                print(await waiting)
            asyncio.run(main())
            # coroutine
            # 7
            ```

            `type(x).__name__` gives the name of a value's type as text. For `waiting` it is `coroutine`,
            not `int`. The call `get_score()` did not produce 7. It produced a package: the function
            together with its arguments, ready to run but not started. This package is called a
            **coroutine object**.

            `await` is what runs it. `await waiting` runs the body of `get_score` and hands you the 7.

            ```match
            `get_score` :: the function itself
            `get_score()` :: a coroutine object, and nothing has run yet
            `await get_score()` :: the number 7
            ```

            Most of the time you write the call and the `await` together, as in `await get_score()`. When
            the `await` is left out, the name on the left holds the package and not the value:

            ```python
            import asyncio
            async def get_score():
                return 7
            async def main():
                score = get_score()
                try:
                    print(score + 1)
                except TypeError as error:
                    print("TypeError:", error)
                await score
            asyncio.run(main())
            # TypeError: unsupported operand type(s) for +: 'coroutine' and 'int'
            ```

            The example catches the error and then awaits the coroutine so it is not left unused. Python cannot add 1 to a package. The message names the two types it was asked to add: a
            `coroutine` and an `int`.

            ```predict
            import asyncio

            async def get_price():
                return 20

            async def main():
                a = await get_price()
                b = get_price()
                print(type(a).__name__)
                print(type(b).__name__)
                print(await b)

            asyncio.run(main())
            ---
            `a` got an `await`, so it holds the number 20, and its type is `int`. `b` holds only the coroutine object. The last line awaits `b`, which runs `get_price` and gives 20.
            ```

            **Watch out:** if a coroutine is left unused, Python can also print `RuntimeWarning: coroutine 'get_score'
            was never awaited`. Whenever you read "was never awaited", an `await` is missing in front of
            the call that the warning names.

            **In short:** calling an async function only prepares it, and `await` runs it and gives you
            the value.
        ''',
        "prompt": r'''
            `get_answer()` is an async function that gives back the number 42. `double_answer()` is meant
            to fetch that number and give back twice as much. It stops with a `TypeError` every time.

            **Your job:** find the bug in `double_answer()` and fix it. The code is already in the editor,
            and one line needs a small change.

            **What goes in**
            - nothing. `double_answer()` takes no arguments.

            **What comes out**
            - the number `84`, an `int`

            **Rules**
            - Leave `get_answer()` as it is.
            - The result is the number itself, not a coroutine object.

            **Examples**
            ```python
            asyncio.run(double_answer())   # returns 84
            ```
        ''',
        "starter": r'''
            import asyncio


            async def get_answer():
                await asyncio.sleep(0)
                return 42


            async def double_answer():
                answer = get_answer()
                return answer * 2
        ''',
        "tests": r'''
            import asyncio
            from solution import double_answer

            def test_returns_84():
                got = asyncio.run(double_answer())
                assert got == 84, f"got {got!r}"

            def test_result_is_an_int():
                got = asyncio.run(double_answer())
                assert isinstance(got, int), f"got a {type(got).__name__}"
        ''',
        "solution": r'''
            import asyncio


            async def get_answer():
                await asyncio.sleep(0)
                return 42


            async def double_answer():
                answer = await get_answer()
                return answer * 2
        ''',
        "hints": [
            "What do you hold after you call an async function without waiting for it? The first example in the lesson prints its type.",
            "The name `answer` holds a coroutine object, not 42, and a coroutine object cannot be multiplied. The function `get_answer` was prepared but never run.",
            "Look at the line that gives `answer` its value. One keyword is missing between the `=` and the call. The `return` line can stay as it is.",
        ],
    },
    {
        "id": "async-s6",
        "title": "Who finishes first?",
        "difficulty": 0,
        "lesson": r'''
            ## Start every call first, then wait for all of them

            Your app has ten questions for an LLM, and each answer takes two seconds. If you `await` the
            questions one after the other, the program waits twenty seconds. But no question depends on
            another one. You could send all ten at once and then wait until all ten answers are in. That
            takes about two seconds.

            Python has a function for this: `asyncio.gather`. Remember the previous step: calling an async
            function does not run it, it gives a coroutine object. `gather` takes several of those, starts
            all of them, and waits until every one has finished.

            ```python
            import asyncio

            async def fake_llm(prompt, seconds):
                await asyncio.sleep(seconds)
                return prompt.upper()

            async def main():
                replies = await asyncio.gather(fake_llm("long", 0.2), fake_llm("short", 0.1))
                print(replies)

            asyncio.run(main())
            # ['LONG', 'SHORT']
            ```

            `await asyncio.gather(...)` gives back a list with one reply for each call. In time, this is what
            happened. `gather` started `fake_llm("long", 0.2)`, and it paused at its `sleep`. Without waiting
            for it, `gather` started `fake_llm("short", 0.1)`, and that one paused too. Now both were waiting
            at the same moment, so the whole program took about 0.2 seconds, the longest single wait, and
            not 0.3. Programmers say the two calls ran **concurrently**.

            Look at the list. `"short"` finished first, but its reply is second. The list follows the order
            in which you passed the calls, not the order in which they finished. That is what lets you match
            replies to questions: the reply at position 0 belongs to the first call.

            Step through the stages to watch the two calls overlap.

            ```diagram
            {"type":"flow","title":"Order of events in asyncio.gather(fake_llm(\"long\", 0.2), fake_llm(\"short\", 0.1))","steps":[{"label":"main awaits gather","detail":"gather schedules both coroutines on the event loop. main is paused at its await until both have finished.","code":"replies = await asyncio.gather(fake_llm(\"long\", 0.2), fake_llm(\"short\", 0.1))"},{"label":"long runs to its await","detail":"The event loop runs fake_llm(\"long\", 0.2) until await asyncio.sleep(0.2). That coroutine is paused for 0.2 seconds.","code":"await asyncio.sleep(0.2)   # long is paused"},{"label":"short runs to its await","detail":"The event loop switches to fake_llm(\"short\", 0.1) and runs it until await asyncio.sleep(0.1). Both coroutines are now paused.","code":"await asyncio.sleep(0.1)   # short is paused"},{"label":"short finishes first","detail":"After 0.1 seconds the event loop resumes short. It returns 'SHORT'. gather stores it in position 1 because short was the second argument.","code":"results so far: [not ready, 'SHORT']"},{"label":"long finishes","detail":"After 0.2 seconds the event loop resumes long. It returns 'LONG'. gather stores it in position 0.","code":"results so far: ['LONG', 'SHORT']"},{"label":"main resumes","detail":"Both coroutines are finished, so the await in main evaluates to the list, in argument order.","code":"print(replies)\n# ['LONG', 'SHORT']"}]}
            ```

            ```quiz
            You pass three calls to `gather` in the order A, B, C. They finish in the order C, A, B. In which order are the replies in the list?
            - [x] A, B, C :: Right. The list follows the order in which the calls were passed, whatever the order of finishing.
            - [ ] C, A, B :: That is the order of finishing. `gather` does not use it for the list. It puts each reply in the position of its call.
            - [ ] Only the reply of C, the first one to finish :: `gather` waits for every call and gives back all the replies, in one list.
            ```

            A `print` inside a coroutine runs at the moment that coroutine reaches it. So lines printed by
            the calls come out in the order the calls finish, while the list that `gather` returns keeps the
            order you passed them in. Work out both orders for this program:

            ```predict
            import asyncio

            async def ask(model, seconds):
                await asyncio.sleep(seconds)
                print("reply from", model)
                return len(model)

            async def main():
                sizes = await asyncio.gather(ask("medium", 0.06), ask("tiny", 0.01), ask("large", 0.03))
                print(sizes)

            asyncio.run(main())
            ---
            The three calls start together and wait 0.06, 0.01 and 0.03 seconds. The `print` inside `ask` runs when each wait is over, so the lines come in the order `tiny`, `large`, `medium`. `gather` then gives the results in the order the calls were passed: `medium` (6 letters), `tiny` (4) and `large` (5).
            ```

            **Watch out:** do not put `await` in front of the calls inside the brackets of `gather`. With
            `gather(await fake_llm("a", 0.1), await fake_llm("b", 0.1))`, each call is finished before the
            next one starts, so nothing runs together. Then `gather` receives plain text instead of calls
            and stops with `TypeError: An asyncio.Future, a coroutine or an awaitable is required`. Pass
            the calls as they are, and write one `await` in front of `gather`.

            **In short:** `await asyncio.gather(a, b)` starts the calls together, waits for all of them, and
            gives back their replies in the order you passed them.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, line by line, in the order the lines appear.
        ''',
        "code": r'''
            import asyncio

            async def job(name, delay):
                await asyncio.sleep(delay)
                print("done", name)
                return name

            async def main():
                results = await asyncio.gather(job("slow", 0.05), job("fast", 0.01))
                print(results)

            asyncio.run(main())
        ''',
        "solution": r'''
            done fast
            done slow
            ['slow', 'fast']
        ''',
        "explanation": r'''
            `gather` starts both jobs together. Both are now waiting: `slow` for 0.05 seconds and `fast` for 0.01 seconds. The `print` inside `job` runs when its wait is over, so `done fast` comes first and `done slow` follows a little later. Only when both jobs have finished does `await asyncio.gather(...)` give back its list. The list follows the order in which the jobs were passed, `slow` and then `fast`, and `print(results)` shows the strings with quotes inside square brackets.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Both jobs start together. Which wait ends first, and what does a job do right after its wait?",
            "The `print` inside `job` runs at the moment that job finishes its wait, so those lines come in the order of finishing. The list at the end follows a different rule: look at the order in which the jobs were passed to `gather`.",
            "The first two lines are the prints of the two jobs, the one with the shorter wait first. The third line is the list printed by `main`: both names, in the order they were written in the `gather` call, as text in quotes inside square brackets.",
        ],
    },
    {
        "id": "async-s5",
        "title": "Two calls at once",
        "difficulty": 0,
        "lesson": r'''
            ## Two questions at once, with the function passed in

            A function that asks an LLM two questions has to know how to ask. If the real network call were
            written inside it, the function would be slow, cost money and be hard to test. So real programs
            pass the asking function in as a parameter, and a test can hand over a fake one that answers at
            once. This works because a function is a value, as you saw in the functions chapter. Write its
            name without brackets and you pass the function itself.

            ```python
            import asyncio

            async def shout(text):
                await asyncio.sleep(0.01)
                return text.upper()

            async def ask(call, prompt):
                return await call(prompt)

            print(asyncio.run(ask(shout, "hi")))
            # HI
            ```

            Inside `ask`, `call` is another name for `shout`. `call(prompt)` is a call like any other, so it
            gives a coroutine object, and `await` runs it and hands back the reply.

            ```quiz
            Which line hands the function `shout` itself to `ask`?
            - [x] `ask(shout, "hi")` :: Right. A name without brackets is the function itself, and `ask` can call it later.
            - [ ] `ask(shout(), "hi")` :: The brackets call `shout` right here, with no text. Python stops with `TypeError: shout() missing 1 required positional argument: 'text'`.
            - [ ] `ask("shout", "hi")` :: That is the text `"shout"`, not the function. When `ask` tries to call it, Python raises `TypeError: 'str' object is not callable`.
            ```

            Now two questions. Two `await` lines in a row are **sequential**: the second call does not start
            until the first has finished. The prints show the order:

            ```python
            import asyncio
            async def step(name, seconds):
                print("start", name)
                await asyncio.sleep(seconds)
                print("end", name)
            async def main():
                for name in ("a", "b"): await step(name, 0.01)
            asyncio.run(main())
            # start a
            # end a
            # start b
            # end b
            ```

            You met the cure in the previous step. Change `main` so that both calls run together. Both
            `start` lines should then print before any `end` line, because both calls are already running
            when the first wait begins.

            ```try
            import asyncio

            async def step(name, seconds):
                print("start", name)
                await asyncio.sleep(seconds)
                print("end", name)

            async def main():
                for name in ("a", "b"):
                    await step(name, 0.01)

            asyncio.run(main())
            ---
            Replace the two `await` lines in `main` with one line, so that both `start` lines print before the first `end`.
            ---
            import asyncio

            async def step(name, seconds):
                print("start", name)
                await asyncio.sleep(seconds)
                print("end", name)

            async def main():
                await asyncio.gather(step("a", 0.03), step("b", 0.01))

            asyncio.run(main())
            ---
            Both calls started before either wait was over. `b` only waits 0.01 seconds, so it ends before `a`. The whole run takes about 0.03 seconds, not 0.04.
            ```

            **Watch out:** two `await` lines in a row give no error and the right answer, only slowly,
            because the waits add up. That makes the mistake easy to miss. When two calls do not depend on
            each other, ask yourself whether they should run together.

            **In short:** pass a function in by its name without brackets, and use `asyncio.gather` rather
            than two `await` lines in a row when the calls do not depend on each other.
        ''',
        "prompt": r'''
            A chat app has to ask an LLM two separate questions. The questions do not depend on each other, so waiting for the first reply before sending the second one wastes time. The function that does the asking is handed to your function as a parameter.

            **Your job:** write the coroutine `ask_two(call, first, second)` so that it sends both questions at the same time and gives back both replies.

            **What goes in**
            - `call`: an async function that takes one prompt and gives back its reply, for example a fake LLM. `await call("a")` gives the reply to `"a"`.
            - `first`: a string, the first prompt, for example `"a"`
            - `second`: a string, the second prompt, for example `"b"`

            **What comes out**
            - a list with two replies: the reply to `first`, then the reply to `second`, for example `["A", "B"]`

            **Rules**
            - The two calls must run at the same time, not one after the other. A check watches how many calls are running at once.
            - The result is a list (not a tuple), with the reply to `first` at position 0.

            **Examples**
            ```python
            async def call(p):          # a fake LLM used in the examples
                await asyncio.sleep(0.01)
                return p.upper()

            asyncio.run(ask_two(call, "a", "b"))   # returns ["A", "B"]
            asyncio.run(ask_two(call, "x", "y"))   # returns ["X", "Y"]
            ```
        ''',
        "starter": r'''
            import asyncio


            async def ask_two(call, first, second):
                ...
        ''',
        "tests": r'''
            import asyncio
            from solution import ask_two

            async def upper(p):
                await asyncio.sleep(0.01)
                return p.upper()

            def test_results_in_first_second_order():
                got = asyncio.run(ask_two(upper, "a", "b"))
                assert list(got) == ["A", "B"], f"got {got!r}"

            def test_returns_a_list():
                got = asyncio.run(ask_two(upper, "x", "y"))
                assert isinstance(got, list), f"got a {type(got).__name__}"

            def test_calls_run_at_the_same_time():
                stats = {"active": 0, "max": 0}
                async def tracked(p):
                    stats["active"] += 1
                    stats["max"] = max(stats["max"], stats["active"])
                    await asyncio.sleep(0.01)
                    stats["active"] -= 1
                    return p
                asyncio.run(ask_two(tracked, "a", "b"))
                assert stats["max"] == 2, "the two calls ran one after another, not at the same time"
        ''',
        "solution": r'''
            import asyncio


            async def ask_two(call, first, second):
                return await asyncio.gather(call(first), call(second))
        ''',
        "hints": [
            "Look at the previous example again: what did you change so that both `start` lines came before the first `end`?",
            "Make a coroutine object for each question by calling `call` twice, hand both to the function that runs them together, and wait for it once. The function that runs them together already returns a list, so you do not need to build one.",
            "In order: call `call` with `first` and call it with `second`, without awaiting either of them yet. Pass both results to `asyncio.gather`. Put a single `await` in front of `gather` and return what you get.",
        ],
    },
    {
        "id": "async-s4",
        "title": "What gets streamed?",
        "difficulty": 0,
        "lesson": r'''
            ## Reading a reply as it arrives

            A chat window shows an answer word by word while the model is still writing it. The program
            does not wait for the whole answer. The pieces arrive one at a time, each after a short wait,
            and the program handles every piece as it comes.

            Programmers call this **streaming**. You already know a tool that hands out items one at a time: a generator, a `def` function with
            `yield`. A stream needs one more thing. Between two pieces the function has to wait for the
            server, and waiting needs `await`, which only an `async def` function may use. Put `async def`
            and `yield` together and you get what a stream needs:

            ```python
            import asyncio
            async def progress():
                for percent in (25, 50, 100):
                    await asyncio.sleep(0)
                    yield percent
            async def main():
                async for value in progress():
                    print(value, "percent")
            asyncio.run(main())
            # 25 percent
            # 50 percent
            # 100 percent
            ```

            `progress` is an **async generator**: an `async def` function that contains `yield`. Its
            `await asyncio.sleep(0)` stands for the wait for the server, as in the earlier steps.

            The loop in `main` is new. `async for` is the loop that reads an async generator. It asks for
            the next piece, and the generator runs until its next `yield` and hands the value over. The
            loop body runs. Then the generator carries on from the line after the `yield`. When the
            function body ends, the loop ends. Like `await`, `async for` is allowed only inside an
            `async def` function.

            Fill in the gap so that the loop can read the generator:

            ```fill
            import asyncio

            async def pieces():
                for word in ["a", "b"]:
                    await asyncio.sleep(0)
                    yield word

            async def main():
                ___ word in pieces():
                    print(word)

            asyncio.run(main())
            ---
            - [x] async for :: Right. `async for` is the loop that reads an async generator.
            - [ ] for :: A plain `for` cannot read an async generator. Python stops with `TypeError: 'async_generator' object is not iterable`.
            - [ ] await for :: There is no `await for` in Python. It is a `SyntaxError`.
            ```

            The generator and the loop take turns. Work out which line comes when:

            ```predict
            import asyncio

            async def pieces():
                print("start")
                yield "A"
                print("middle")
                yield "B"
                print("finish")

            async def main():
                async for p in pieces():
                    print("got", p)

            asyncio.run(main())
            ---
            The generator runs only when the loop asks for a piece. It prints `start` and hands over `"A"`, the loop body prints `got A`, and the generator carries on from the line after the first `yield`. It prints `middle` and hands over `"B"`, and the loop prints `got B`. At the next request the generator prints `finish` and ends, and that ends the loop.
            ```

            **Watch out:** a plain `for` loop cannot read an async generator. `for value in progress():`
            stops with `TypeError: 'async_generator' object is not iterable`. Whenever you see that
            message, change `for` to `async for`.

            **In short:** an `async def` function with `yield` is an async generator, and `async for`
            reads it one piece at a time.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, line by line.
        ''',
        "code": r'''
            import asyncio

            async def stream():
                for token in ["Hel", "lo", "!"]:
                    await asyncio.sleep(0)
                    yield token

            async def main():
                async for token in stream():
                    print(token)
                print("end")

            asyncio.run(main())
        ''',
        "solution": r'''
            Hel
            lo
            !
            end
        ''',
        "explanation": r'''
            `stream` is an async generator, so the loop in `main` gets its pieces one at a time. Each trip of the loop receives one token and the body prints it on its own line: `Hel`, then `lo`, then `!`. Printed text has no quotes. After the third token the generator has nothing left, its function body ends, and the loop ends with it. Only then does the last `print` of `main` run, and it prints `end`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The loop body runs once for every piece that the generator hands over. How many pieces does `stream` hand over, and what are they?",
            "Each trip of the loop prints one piece on its own line, in the order of the list. The `print` after the loop runs only when the generator has no more pieces.",
            "Three lines for the three pieces, in list order, without quotes. After them one last line from the `print` that comes after the loop.",
        ],
    },
    {
        "id": "async-1",
        "hints": [
            "Where is the boundary between the ordinary caller and the async operation?",
            "The coroutine cooperatively waits and returns formatted text. The ordinary wrapper must run it to completion.",
            "In the coroutine, await the async delay before constructing the specified reply. In the sync wrapper, hand a newly created coroutine to the loop-running function and give back its completed result.",
        ],
        "title": "Your first coroutine",
        "difficulty": 1,
        "lesson": r'''
            ## Run async work from an ordinary function

            Your script needs a result from an async operation, but the rest of the script uses ordinary functions. Its caller should receive the finished result, not an object representing work that has not run yet.

            ```python
            import asyncio
            async def double_later(number):
                await asyncio.sleep(0)
                return number * 2

            def double_now(number):
                return asyncio.run(double_later(number))

            print(double_now(6))
            # 12
            ```

            `asyncio.run` starts an event loop, runs the supplied coroutine to completion, closes the loop, and gives back its result. The event loop coordinates async work while operations wait. Here the outer function is ordinary code, so its caller does not need to use `await`.

            ```quiz
            What does calling double_later(6) without await or asyncio.run give you?
            - [x] A coroutine object representing the work :: Calling an async function prepares the coroutine; it does not obtain its finished result.
            - [ ] The integer 12 immediately :: The body has not been run to completion yet.
            ```

            Code using ordinary `def` is often called **synchronous**, or **sync**, code. A function defined with `async def` is async code. At a sync boundary you can start the loop with `asyncio.run`; inside an already running coroutine, you await other async operations.

            A delay should also cooperate with that loop. Awaiting `asyncio.sleep` suspends the current coroutine while other ready work can proceed. A blocking sleep prevents the loop from progressing during the wait.

            ```match
            ordinary function :: may start async work with asyncio.run
            running coroutine :: awaits other async operations
            asyncio.sleep :: waits without blocking the event loop
            ```

            **Watch out:** starting `asyncio.run` inside an already running loop raises `RuntimeError`. It is a boundary tool, not a replacement for await everywhere.

            **In short:** start async work from sync code with asyncio.run, and await it from async code.
        ''',
        "prompt": r'''
            Before calling a real LLM, build a fake one: a coroutine that "thinks" for a
            moment, plus a normal function so non-async code can use it too.

            **Your job:** write two functions

            **What goes in**

            1. `async def fake_complete(prompt, delay=0.01)` (a *coroutine function*)
               - `prompt`: a `str`, e.g. `"hi"`
               - `delay`: a `float`, seconds to wait, e.g. `0.05`; defaults to `0.01`
               - **What comes out:** a `str` like `"[hi] ok"`: the prompt in square brackets, a
                 space, then `ok`
            2. `def complete_sync(prompt)` (a **regular** function, not `async`)
               - `prompt`: a `str`, e.g. `"summarise this"`
               - **What comes out:** the result of `fake_complete(prompt)`, e.g. `"[summarise this] ok"`

            **What comes out**
            - Awaiting `fake_complete` gives back the formatted reply after the cooperative delay. Calling `complete_sync` normally gives back the same completed string.

            **Rules**
            - `fake_complete` must be defined with `async def`.
            - `fake_complete` must really wait about `delay` seconds before returning.
            - Wait **without blocking the event loop**: the text `time.sleep` must not appear
              anywhere in your file.
            - `complete_sync` must be a plain `def` that runs the coroutine itself and returns
              its result (the caller does not use `await` or `asyncio.run`).

            **Examples**
            ```python
            asyncio.run(fake_complete("hi"))              # returns "[hi] ok"
            asyncio.run(fake_complete("x", delay=0.05))   # returns "[x] ok" after ~0.05 s
            complete_sync("summarise this")               # returns "[summarise this] ok"
            ```
        ''',
        "starter": r'''
            import asyncio


            async def fake_complete(prompt, delay=0.01):
                ...


            def complete_sync(prompt):
                ...
        ''',
        "tests": r'''
            import asyncio
            import inspect
            import time
            from solution import fake_complete, complete_sync

            def test_fake_complete_is_a_coroutine_function():
                assert inspect.iscoroutinefunction(fake_complete), "fake_complete must be defined with async def"

            def test_fake_complete_returns_prompt_in_brackets_then_ok():
                got = asyncio.run(fake_complete("hi"))
                assert got == "[hi] ok", f"got {got!r}"

            def test_fake_complete_waits_for_delay_seconds():
                start = time.perf_counter()
                asyncio.run(fake_complete("x", delay=0.05))
                elapsed = time.perf_counter() - start
                assert elapsed >= 0.045, f"returned after {elapsed:.3f}s, expected to wait ~0.05s"

            def test_does_not_use_time_sleep():
                assert "time.sleep" not in source(), "time.sleep blocks the event loop"

            def test_complete_sync_is_a_plain_function_returning_the_result():
                assert not inspect.iscoroutinefunction(complete_sync), "complete_sync must be a regular def"
                got = complete_sync("summarise this")
                assert got == "[summarise this] ok", f"got {got!r}"
        ''',
        "solution": r'''
            import asyncio


            async def fake_complete(prompt, delay=0.01):
                await asyncio.sleep(delay)
                return f"[{prompt}] ok"


            def complete_sync(prompt):
                return asyncio.run(fake_complete(prompt))
        ''',
    },
    {
        "id": "async-2",
        "hints": [
            "The producer gives many values; the collector gives one final list.",
            "Use async generation for delayed pieces and async iteration to read any compatible producer.",
            "Split the text on whitespace, cooperatively wait before each word, and yield it. Collect the incoming stream with async iteration, preserving item order.",
        ],
        "title": "Streaming tokens",
        "difficulty": 1,
        "lesson": r'''
            ## Produce and collect a reply incrementally

            A streaming reply can show its first piece before later pieces exist. You need a producer that can wait between pieces and a reader that can request each next piece without blocking the event loop.

            ```python
            import asyncio
            async def letters():
                for letter in "sun":
                    await asyncio.sleep(0)
                    yield letter

            async def main():
                print([letter async for letter in letters()])

            asyncio.run(main())
            # ['s', 'u', 'n']
            ```

            Combining `async def` and `yield` makes an **async generator**. Its body can await work before yielding a value. Its consumer uses `async for`, which can wait for each next item. The example collects these items with an **async comprehension**, the familiar list-comprehension form with an async loop.

            ```quiz
            Why does the reader use async for rather than ordinary for?
            - [x] Obtaining the next item may require waiting :: The async iteration operation can suspend until that item is ready.
            - [ ] The values are special async strings :: Ordinary strings can be carried by an async stream.
            ```

            The generator stays lazy: after yielding a piece it pauses until another piece is requested. Stopping the reader early prevents later pieces from being produced. Collecting the whole stream is useful in a test, but a user interface may choose to display pieces immediately instead.

            ```predict
            import asyncio
            async def letters():
                for letter in "sun":
                    print("made", letter)
                    yield letter
            async def main():
                async for letter in letters():
                    print("read", letter)
                    break
            asyncio.run(main())
            ---
            Only s is produced and read. The reader breaks before requesting u, so the generator never advances to that letter.
            ```

            Any object supporting this reading operation is an **async iterable**. A collection helper should rely on that behavior, not the name of one particular producer.

            **Watch out:** awaiting an async generator itself raises `TypeError`; it provides many items through async iteration, rather than one final awaited result.

            **In short:** async generators yield incremental values, and async for lets a consumer wait for each one.
        ''',
        "prompt": r'''
            LLM APIs stream their replies piece by piece. Fake a stream, and write a helper
            that gathers a whole stream into a list.

            **Your job:** write two functions

            **What goes in**

            1. `async def stream_tokens(text, delay=0)`: an **async generator** (`async def`
               that uses `yield`)
               - `text`: a `str`, e.g. `"Hello  there world"` (may be empty)
               - `delay`: seconds to wait before each word; defaults to `0`
               - **Yields:** each word of `text` (split on any whitespace), one at a time, in order
            2. `async def collect(stream)`
               - `stream`: **any** async iterable (something you can loop over with `async for`),
                 not only `stream_tokens`
               - **What comes out:** a `list` of all its items, in order

            **What comes out**
            - `stream_tokens` supplies words through async iteration. Awaiting `collect` gives back an ordered list of all items from the supplied async iterable.

            **Rules**
            - `stream_tokens` must be an async generator (a check verifies this).
            - Wait `delay` seconds with `asyncio.sleep` before yielding each word.
            - Several spaces in a row count as one separator; empty text yields nothing.
            - `stream_tokens` must be *lazy*: it yields words one by one as they are asked for,
              so reading just the first item of `stream_tokens("a b c")` gives `"a"`.

            **Examples**
            ```python
            asyncio.run(collect(stream_tokens("Hello  there world")))   # returns ["Hello", "there", "world"]
            asyncio.run(collect(stream_tokens("")))                     # returns []

            async def numbers():        # any other async generator
                for i in range(3):
                    yield i * 10
            asyncio.run(collect(numbers()))                             # returns [0, 10, 20]
            ```
        ''',
        "starter": r'''
            import asyncio


            async def stream_tokens(text, delay=0):
                ...


            async def collect(stream):
                ...
        ''',
        "tests": r'''
            import asyncio
            import inspect
            from solution import stream_tokens, collect

            def test_stream_tokens_is_an_async_generator():
                assert inspect.isasyncgenfunction(stream_tokens), "stream_tokens must be an async generator (async def + yield)"

            def test_streams_each_word_in_order():
                got = asyncio.run(collect(stream_tokens("Hello  there world")))
                assert got == ["Hello", "there", "world"], f"got {got!r}"

            def test_empty_text_streams_nothing():
                got = asyncio.run(collect(stream_tokens("")))
                assert got == [], f"got {got!r}"

            def test_collect_works_on_any_async_iterable():
                async def numbers():
                    for i in range(3):
                        await asyncio.sleep(0)
                        yield i * 10
                got = asyncio.run(collect(numbers()))
                assert got == [0, 10, 20], f"got {got!r}"

            def test_stream_yields_first_word_on_demand():
                async def first_only():
                    agen = stream_tokens("a b c")
                    first = await agen.__anext__()
                    await agen.aclose()
                    return first
                got = asyncio.run(first_only())
                assert got == "a", f"first streamed item was {got!r}"
        ''',
        "solution": r'''
            import asyncio


            async def stream_tokens(text, delay=0):
                for word in text.split():
                    await asyncio.sleep(delay)
                    yield word


            async def collect(stream):
                return [item async for item in stream]
        ''',
    },
    {
        "id": "async-7",
        "title": "Catch a failed call",
        "difficulty": 1,
        "lesson": r'''
            ## Catch errors where async work actually runs

            A request can fail after waiting for a response. You want to turn that failure into a useful value while leaving successful results unchanged. The familiar try/except structure still works, but it must surround the operation that actually runs the coroutine.

            ```python
            import asyncio
            async def fetch():
                raise LookupError("missing record")
            async def main():
                try:
                    await fetch()
                except LookupError as error:
                    print(type(error).__name__)
            asyncio.run(main())
            # LookupError
            ```

            The exception raised inside `fetch` comes out at the `await` in `main`. That is where the `except` block catches it. Creating a coroutine object without awaiting it does not run the body, so a try block around creation alone cannot catch the later failure.

            ```quiz
            A coroutine object was created successfully. Does that prove the request succeeded?
            - [x] No :: The body may not have run yet, and failures can occur while it is awaited.
            - [ ] Yes :: Creating a coroutine is not the same as obtaining its result.
            ```

            The variable after `as` refers to the actual exception object. `type(error).__name__` gives its class name, such as `LookupError`. `str(error)` gives its message, such as `missing record`. These answer different questions: what kind of failure occurred, and what detail did it carry?

            ```predict
            error = ValueError("bad setting")
            print(type(error).__name__)
            print(str(error))
            ---
            The first line identifies the exception class. The second reports the message stored in that exception instance.
            ```

            Catch only the family of failures your contract says to handle. `Exception` covers ordinary application errors. Cancellation is a separate control signal and should not be swallowed by an unnecessarily broad catch.

            **Watch out:** calling the async function again in the handler retries the operation. If the requirement is one call, keep the original awaited call as the only call site.

            **In short:** wrap the awaited operation in try/except and distinguish an exception's class name from its message.
        ''',
        "prompt": r'''
            A failed LLM request should become a clear message, not a crash.

            **Your job:** write the coroutine `async def safe_reply(call, prompt)`

            **What goes in**

            - `call`: an async function that takes one prompt; `await call("hi")` gives its
              reply, or raises an exception
            - `prompt`: a `str`, e.g. `"hi"`

            **What comes out**
            - the reply of `call(prompt)`; if the call raises any `Exception`,
              return the string `"error: "` followed by the exception's class name, e.g.
              `"error: ValueError"`

            **Rules**
            - `safe_reply` must be defined with `async def`.
            - Call `call` exactly once.
            - Any exception type counts (`ValueError`, `KeyError`, `TimeoutError`, ...).

            **Examples**
            ```python
            async def good(p):
                return "reply to " + p

            async def broken(p):
                raise KeyError("choices")

            asyncio.run(safe_reply(good, "hi"))     # returns "reply to hi"
            asyncio.run(safe_reply(broken, "hi"))   # returns "error: KeyError"
            ```
        ''',
        "starter": r'''
            import asyncio


            async def safe_reply(call, prompt):
                ...
        ''',
        "tests": r'''
            import asyncio
            import inspect
            from solution import safe_reply

            async def good(p):
                await asyncio.sleep(0)
                return "reply to " + p

            def test_safe_reply_is_async_def():
                assert inspect.iscoroutinefunction(safe_reply), "safe_reply must be defined with async def"

            def test_successful_call_returns_the_reply():
                got = asyncio.run(safe_reply(good, "hi"))
                assert got == "reply to hi", f"got {got!r}"

            def test_value_error_becomes_error_message():
                async def broken(p):
                    await asyncio.sleep(0)
                    raise ValueError("model refused")
                got = asyncio.run(safe_reply(broken, "x"))
                assert got == "error: ValueError", f"got {got!r}"

            def test_other_exception_types_use_their_class_name():
                async def broken(p):
                    raise KeyError("choices")
                got = asyncio.run(safe_reply(broken, "x"))
                assert got == "error: KeyError", f"got {got!r}"

            def test_call_is_made_exactly_once():
                seen = []
                async def call(p):
                    seen.append(p)
                    return "ok"
                asyncio.run(safe_reply(call, "hello"))
                assert seen == ["hello"], f"call received {seen!r}"
        ''',
        "solution": r'''
            import asyncio


            async def safe_reply(call, prompt):
                try:
                    return await call(prompt)
                except Exception as err:
                    return "error: " + type(err).__name__
        ''',
        "hints": [
            "The error appears when the coroutine runs, not when it is created.",
            "Place the awaited call inside try/except and turn ordinary exceptions into the required class-name message.",
            "Make the call once and await it. Return a successful reply unchanged; for a caught Exception, obtain its type name and attach the specified prefix.",
        ],
    },
    {
        "id": "async-8",
        "title": "Count the failures",
        "difficulty": 1,
        "lesson": r'''
            ## Keep successful results when another call fails

            A batch contains several independent requests. One failure should not hide the successful replies. You need a result for each position, even if some positions contain information about failures instead of ordinary answers.

            ```python
            import asyncio
            async def checked(number):
                if number < 0:
                    raise ValueError("negative")
                return number * 2
            async def main():
                results = await asyncio.gather(checked(3), checked(-1), return_exceptions=True)
                print([type(value).__name__ for value in results])
            asyncio.run(main())
            # ['int', 'ValueError']
            ```

            By default, awaiting `gather` raises when a child operation raises. The option shown above instead places exceptions in the result list. They occupy the same positions as their input operations, just as successful results do. An exception object can be stored and inspected like another value.

            ```predict
            results = ["done", KeyError("record"), "ready"]
            print([isinstance(value, Exception) for value in results])
            ---
            Only the middle item is an exception object. The result is False, True, False in the same input order.
            ```

            This is useful when the batch report matters more than stopping at the first error. You can count failures or associate each failure with its original input. Do not use whether a value is truthy as a success test: an empty string may be a perfectly successful reply.

            ```quiz
            A request successfully returns an empty string. Should a health report count it as a failure?
            - [x] No :: An empty result is different from a raised exception.
            - [ ] Yes :: Truthiness does not tell you whether the operation raised.
            ```

            Create all the coroutine objects before awaiting the gather. Awaiting each call inside the creation loop would run the batch sequentially and lose the concurrency you wanted.

            **Watch out:** an exception collected as data is no longer automatically raised at this boundary. Your code must deliberately inspect and report it rather than treating every item as a reply.

            **In short:** gather can preserve every outcome, and exception objects let you distinguish failures from valid results.
        ''',
        "research": {
            "note": "`asyncio.gather` has a keyword argument that returns exceptions as results instead of raising the first one. Read the `gather` docs, find it, then come back.",
            "links": [
                {"title": "asyncio.gather - Python docs", "url": "https://docs.python.org/3/library/asyncio-task.html#asyncio.gather"},
            ],
        },
        "prompt": r'''
            A batch job wants a quick health report: how many LLM calls worked and how many
            failed - without one failure hiding the others.

            **Your job:** write the coroutine `async def count_outcomes(prompts, call)`

            **What goes in**

            - `prompts`: a `list` of `str`, e.g. `["a", "boom", "b"]` (may be empty)
            - `call`: an async function that takes one prompt; it returns a reply or raises

            **What comes out**
            - a `dict` `{"ok": <int>, "failed": <int>}`: how many calls returned
              and how many raised an exception

            **Rules**
            - Run all calls **concurrently** with one `asyncio.gather` (a check verifies they
              all run at the same time).
            - Use the `gather` option that returns exceptions instead of raising them (a check
              looks for `return_exceptions` in your code).
            - An empty list returns `{"ok": 0, "failed": 0}`.

            **Examples**
            ```python
            # call("boom") raises ValueError, any other prompt returns p.upper()
            asyncio.run(count_outcomes(["a", "boom", "b"], call))   # returns {"ok": 2, "failed": 1}
            asyncio.run(count_outcomes(["boom", "boom"], call))     # returns {"ok": 0, "failed": 2}
            asyncio.run(count_outcomes([], call))                   # returns {"ok": 0, "failed": 0}
            ```
        ''',
        "starter": r'''
            import asyncio


            async def count_outcomes(prompts, call):
                ...
        ''',
        "tests": r'''
            import asyncio
            from solution import count_outcomes

            async def call(p):
                await asyncio.sleep(0.005)
                if p == "boom":
                    raise ValueError("model refused")
                return p.upper()

            def test_counts_successes_and_failures():
                got = asyncio.run(count_outcomes(["a", "boom", "b"], call))
                assert got == {"ok": 2, "failed": 1}, f"got {got!r}"

            def test_all_failing():
                got = asyncio.run(count_outcomes(["boom", "boom"], call))
                assert got == {"ok": 0, "failed": 2}, f"got {got!r}"

            def test_empty_list_counts_zero():
                got = asyncio.run(count_outcomes([], call))
                assert got == {"ok": 0, "failed": 0}, f"got {got!r}"

            def test_calls_run_at_the_same_time():
                stats = {"active": 0, "max": 0}
                async def tracked(p):
                    stats["active"] += 1
                    stats["max"] = max(stats["max"], stats["active"])
                    await asyncio.sleep(0.01)
                    stats["active"] -= 1
                    return p
                asyncio.run(count_outcomes(["a", "b", "c", "d"], tracked))
                assert stats["max"] == 4, f"only {stats['max']} call(s) ran at once - they should all run together"

            def test_uses_return_exceptions():
                assert "return_exceptions" in source(), "use asyncio.gather(..., return_exceptions=True)"
        ''',
        "solution": r'''
            import asyncio


            async def count_outcomes(prompts, call):
                outcomes = await asyncio.gather(*(call(p) for p in prompts), return_exceptions=True)
                failed = sum(1 for o in outcomes if isinstance(o, Exception))
                return {"ok": len(outcomes) - failed, "failed": failed}
        ''',
        "hints": [
            "Review how gather can represent a failed operation inside its result list.",
            "Collect outcomes concurrently and classify them by whether they are exception objects, not by their truthiness.",
            "Gather one coroutine for each prompt using exception collection. Count exception outcomes and successful outcomes, then return the two counts under the required keys.",
        ],
    },
    {
        "id": "async-3",
        "hints": [
            "Which operation starts many coroutines and preserves their input order in its results?",
            "Create one coroutine per input occurrence, including duplicates, without awaiting them individually.",
            "Pass the created coroutines as separate arguments to gather, await the gathered result once, and return the ordered replies as a list.",
        ],
        "title": "Fan out with gather",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            You have a batch of prompts to send to an LLM. Send them all at once (this is
            called *fanning out*) instead of waiting for each reply before sending the next.

            **Your job:** write the coroutine `async def ask_all(prompts, call)`

            **What goes in**

            - `prompts`: a `list` of `str`, e.g. `["a", "b", "c"]` (may be empty)
            - `call`: an async function that takes one prompt; `await call("a")` gives its reply

            **What comes out**
            - a `list` with one reply per prompt, in the **same order as `prompts`**

            **Rules**
            - Call `call` exactly **once per prompt** (duplicates included: `["x", "y", "x"]`
              means three calls).
            - Run all the calls **concurrently**: 6 calls that each take 0.05 s must finish in
              well under 0.2 s in total (a check times it).
            - Keep the order of `prompts` even when a later prompt finishes first.
            - An empty `prompts` list returns `[]`.

            **Examples**
            ```python
            async def call(p):          # a fake LLM used in the examples
                await asyncio.sleep(0.05)
                return p.upper()

            asyncio.run(ask_all(["a", "b", "c"], call))   # returns ["A", "B", "C"] in ~0.05 s, not 0.15 s
            asyncio.run(ask_all([], call))                # returns []
            ```
        ''',
        "starter": r'''
            import asyncio


            async def ask_all(prompts, call):
                ...
        ''',
        "tests": r'''
            import asyncio
            import time
            from solution import ask_all

            async def upper_call(p):
                await asyncio.sleep(0.01)
                return p.upper()

            def test_returns_one_reply_per_prompt():
                got = asyncio.run(ask_all(["a", "b", "c"], upper_call))
                assert got == ["A", "B", "C"], f"got {got!r}"

            def test_order_preserved_when_finishing_out_of_order():
                delays = {"slow": 0.05, "mid": 0.03, "fast": 0.0}
                async def call(p):
                    await asyncio.sleep(delays[p])
                    return p + "!"
                got = asyncio.run(ask_all(["slow", "mid", "fast"], call))
                assert got == ["slow!", "mid!", "fast!"], f"got {got!r}"

            def test_calls_run_concurrently():
                async def call(p):
                    await asyncio.sleep(0.05)
                    return p
                start = time.perf_counter()
                asyncio.run(ask_all([str(i) for i in range(6)], call))
                elapsed = time.perf_counter() - start
                assert elapsed < 0.2, f"6 calls of 0.05s took {elapsed:.2f}s - they ran one after another"

            def test_empty_prompts_returns_empty_list():
                got = asyncio.run(ask_all([], upper_call))
                assert got == [], f"got {got!r}"

            def test_each_prompt_called_exactly_once():
                seen = []
                async def call(p):
                    seen.append(p)
                    await asyncio.sleep(0)
                    return p
                asyncio.run(ask_all(["x", "y", "x"], call))
                assert sorted(seen) == ["x", "x", "y"], f"call received {seen!r}"
        ''',
        "solution": r'''
            import asyncio


            async def ask_all(prompts, call):
                return list(await asyncio.gather(*(call(p) for p in prompts)))
        ''',
    },
    {
        "id": "async-4",
        "research": {
            "note": "This exercise needs a way to put a time limit on one awaited call. Read how `asyncio.wait_for` works - what it raises and what happens to the slow call - then come back.",
            "links": [
                {"title": "asyncio.wait_for - Python docs", "url": "https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for"},
            ],
        },
        "hints": [
            "The timeout must cancel the ongoing work rather than only stop your own waiting.",
            "Use the asyncio timeout wrapper around the single call. Handle only the timeout error so other failures retain their meaning.",
            "Await the protected operation with its time limit. Return its result on success and the supplied fallback on timeout, leaving other exceptions uncaught.",
        ],
        "title": "Timeout guard",
        "difficulty": 2,
        "prompt": r'''
            An LLM request can hang. Guard it: give up after a time limit and use a fallback
            answer instead.

            **Your job:** write the coroutine `async def with_timeout(call, prompt, timeout, fallback=None)`

            **What goes in**

            - `call`: an async function that takes one prompt; `await call("hi")` gives its reply
            - `prompt`: a `str`, e.g. `"hi"`
            - `timeout`: a `float`, the time limit in seconds, e.g. `0.03`
            - `fallback`: the value to return on timeout, e.g. `"timed out"`; defaults to `None`

            **What comes out**
            - the reply of `call(prompt)` if it finishes within `timeout` seconds,
              otherwise `fallback`

            **Rules**
            - On timeout, **stop waiting right away**: a call that would take 2 s with a
              `timeout` of 0.03 must return in well under 0.5 s.
            - The slow call must be **cancelled** (not left running in the background).
            - Only a timeout gives `fallback`. Any other exception raised by `call` (e.g. a
              `ValueError`) must propagate unchanged - don't catch it.

            **Examples**
            ```python
            async def fast(p):
                await asyncio.sleep(0.01)
                return f"reply to {p}"

            async def slow(p):
                await asyncio.sleep(2)
                return "too late"

            asyncio.run(with_timeout(fast, "hi", 1.0))                 # returns "reply to hi"
            asyncio.run(with_timeout(slow, "hi", 0.03, "timed out"))   # returns "timed out" after ~0.03 s
            asyncio.run(with_timeout(slow, "hi", 0.02))                # returns None
            ```
        ''',
        "starter": r'''
            import asyncio


            async def with_timeout(call, prompt, timeout, fallback=None):
                return await call(prompt)
        ''',
        "tests": r'''
            import asyncio
            import time
            from solution import with_timeout

            async def fast(p):
                await asyncio.sleep(0.01)
                return f"reply to {p}"

            async def slow(p):
                await asyncio.sleep(2)
                return "too late"

            def test_fast_call_returns_result():
                got = asyncio.run(with_timeout(fast, "hi", 1.0))
                assert got == "reply to hi", f"got {got!r}"

            def test_slow_call_returns_fallback_quickly():
                start = time.perf_counter()
                got = asyncio.run(with_timeout(slow, "hi", 0.03, "timed out"))
                elapsed = time.perf_counter() - start
                assert got == "timed out", f"got {got!r}"
                assert elapsed < 0.5, f"waited {elapsed:.2f}s - did not stop at the timeout"

            def test_default_fallback_is_none():
                got = asyncio.run(with_timeout(slow, "hi", 0.02))
                assert got is None, f"got {got!r}"

            def test_slow_call_is_cancelled():
                state = {"cancelled": False}
                async def tracked(p):
                    try:
                        await asyncio.sleep(2)
                    except asyncio.CancelledError:
                        state["cancelled"] = True
                        raise
                asyncio.run(with_timeout(tracked, "x", 0.02))
                assert state["cancelled"], "the slow call was left running instead of being cancelled"

            def test_other_errors_propagate_unchanged():
                async def broken(p):
                    await asyncio.sleep(0)
                    raise ValueError("bad prompt")
                try:
                    asyncio.run(with_timeout(broken, "x", 1.0, "fallback"))
                except ValueError:
                    return
                raise AssertionError("a ValueError from call should propagate")
        ''',
        "solution": r'''
            import asyncio


            async def with_timeout(call, prompt, timeout, fallback=None):
                try:
                    return await asyncio.wait_for(call(prompt), timeout)
                except asyncio.TimeoutError:
                    return fallback
        ''',
    },
    {
        "id": "async-5",
        "hints": [
            "A shared semaphore controls how many tasks can enter a protected section.",
            "Create one semaphore for the batch, not one per request. Each wrapper holds a slot while its call is awaited.",
            "Reject an invalid limit, create the shared semaphore, and wrap each call in its async context. Gather all wrappers together so available slots are filled while result order remains stable.",
        ],
        "title": "Rate-limited fan out",
        "difficulty": 3,
        "prompt": r'''
            LLM providers rate-limit you, so you must cap how many requests are in flight
            at the same time.

            **Your job:** write the coroutine `async def ask_limited(prompts, call, limit)`

            **What goes in**

            - `prompts`: a `list` of `str`, e.g. `["a", "b", "c", "d"]`
            - `call`: an async function that takes one prompt; `await call("a")` gives its reply
            - `limit`: an `int`, the maximum number of calls running at once, e.g. `2`

            **What comes out**
            - a `list` with one reply per prompt, in the **same order as `prompts`**

            **Rules**
            - Never have more than `limit` calls running at the same time (use an
              `asyncio.Semaphore`).
            - But do use the limit fully: with 10 prompts and `limit=3`, exactly 3 calls must
              run together at some point (not just 1 at a time).
            - `limit=1` runs the calls one after another.
            - A `limit` larger than the number of prompts simply runs them all at once.
            - If `limit < 1`, raise `ValueError`.

            **Examples**
            ```python
            async def call(p):          # a fake LLM used in the examples
                await asyncio.sleep(0.01)
                return p * 2

            asyncio.run(ask_limited(["a", "b", "c", "d", "e"], call, 2))
            # returns ["aa", "bb", "cc", "dd", "ee"]; at most 2 calls active at once
            asyncio.run(ask_limited(["p", "q"], call, 50))   # returns ["pp", "qq"]
            asyncio.run(ask_limited(["a"], call, 0))         # raises ValueError
            ```
        ''',
        "starter": r'''
            import asyncio


            async def ask_limited(prompts, call, limit):
                ...
        ''',
        "tests": r'''
            import asyncio
            from solution import ask_limited

            def make_tracker(delay=0.01):
                stats = {"active": 0, "max": 0}
                async def call(p):
                    stats["active"] += 1
                    stats["max"] = max(stats["max"], stats["active"])
                    try:
                        await asyncio.sleep(delay)
                        return p * 2
                    finally:
                        stats["active"] -= 1
                return call, stats

            def test_results_in_prompt_order():
                call, _ = make_tracker()
                got = asyncio.run(ask_limited(["a", "b", "c", "d", "e"], call, 2))
                assert got == ["aa", "bb", "cc", "dd", "ee"], f"got {got!r}"

            def test_never_exceeds_limit():
                call, stats = make_tracker()
                asyncio.run(ask_limited([str(i) for i in range(10)], call, 3))
                assert stats["max"] <= 3, f"{stats['max']} calls were running at once (limit 3)"

            def test_runs_limit_calls_at_once():
                call, stats = make_tracker()
                asyncio.run(ask_limited([str(i) for i in range(10)], call, 3))
                assert stats["max"] == 3, f"only {stats['max']} call(s) ran at once - should run 3 concurrently"

            def test_limit_one_is_sequential():
                call, stats = make_tracker()
                got = asyncio.run(ask_limited(["x", "y", "z"], call, 1))
                assert stats["max"] == 1, f"max concurrency was {stats['max']}"
                assert got == ["xx", "yy", "zz"], f"got {got!r}"

            def test_limit_bigger_than_prompts_runs_all_at_once():
                call, stats = make_tracker()
                got = asyncio.run(ask_limited(["p", "q"], call, 50))
                assert got == ["pp", "qq"], f"got {got!r}"
                assert stats["max"] == 2

            def test_limit_below_one_raises_value_error():
                call, _ = make_tracker()
                try:
                    asyncio.run(ask_limited(["a"], call, 0))
                except ValueError:
                    return
                raise AssertionError("limit=0 should raise ValueError")
        ''',
        "solution": r'''
            import asyncio


            async def ask_limited(prompts, call, limit):
                if limit < 1:
                    raise ValueError("limit must be at least 1")
                sem = asyncio.Semaphore(limit)

                async def guarded(prompt):
                    async with sem:
                        return await call(prompt)

                return list(await asyncio.gather(*(guarded(p) for p in prompts)))
        ''',
    },
    {
        "id": "async-6",
        "hints": [
            "Combine a timeout around each operation with exception collection around the batch.",
            "The timeout belongs to each call; gather keeps their outcomes in prompt order.",
            "Gather timed operations with exceptions returned as data. Visit outcomes alongside their indices, keeping successful values and placing None for failures while recording each failure's class name.",
        ],
        "title": "Resilient batch",
        "difficulty": 3,
        "prompt": r'''
            In a batch job, one failing or hanging LLM request must not stop the others.
            Run them all, and report which ones failed and why.

            **Your job:** write the coroutine `async def run_batch(prompts, call, timeout)`

            **What goes in**

            - `prompts`: a `list` of `str`, e.g. `["ok", "boom", "hang"]` (may be empty)
            - `call`: an async function that takes one prompt; it may return a reply, raise any
              exception, or hang
            - `timeout`: a `float`, the time limit in seconds for **each** call, e.g. `0.05`

            **What comes out**
            - a dict with exactly two keys:
              - `"results"`: a `list` with one entry per prompt, in order - the call's reply,
                or `None` if that call failed or timed out
              - `"errors"`: a dict mapping the **index** (an `int`) of each failed prompt to the
                exception's **class name** as a string, e.g. `"ValueError"`, `"KeyError"`;
                a timed-out call is reported as `"TimeoutError"`

            **Rules**
            - Run all calls **concurrently**: several hanging calls must time out together, so
              the whole batch finishes in well under 0.5 s with `timeout=0.05`.
            - Use `asyncio.gather(..., return_exceptions=True)` (a check looks for
              `return_exceptions` in your code), so failures are collected, not raised.
            - If every call succeeds, `"errors"` is `{}`.
            - An empty batch returns `{"results": [], "errors": {}}`.

            **Examples**
            ```python
            # call("ok") returns "OK", call("boom") raises ValueError,
            # call("key") raises KeyError, call("hang") sleeps for 2 s
            asyncio.run(run_batch(["ok", "boom", "hang"], call, 0.05))
            # returns {"results": ["OK", None, None], "errors": {1: "ValueError", 2: "TimeoutError"}}
            asyncio.run(run_batch(["key", "fine"], call, 0.5))
            # returns {"results": [None, "FINE"], "errors": {0: "KeyError"}}
            asyncio.run(run_batch([], call, 0.1))
            # returns {"results": [], "errors": {}}
            ```
        ''',
        "starter": r'''
            import asyncio


            async def run_batch(prompts, call, timeout):
                ...
        ''',
        "tests": r'''
            import asyncio
            import time
            from solution import run_batch

            async def call(p):
                if p.startswith("boom"):
                    await asyncio.sleep(0.005)
                    raise ValueError("model refused")
                if p.startswith("hang"):
                    await asyncio.sleep(2)
                if p.startswith("key"):
                    raise KeyError("choices")
                await asyncio.sleep(0.01)
                return p.upper()

            def test_all_succeed_gives_empty_errors():
                got = asyncio.run(run_batch(["a", "b"], call, 0.5))
                assert got == {"results": ["A", "B"], "errors": {}}, f"got {got!r}"

            def test_failure_and_timeout_reported_by_index():
                got = asyncio.run(run_batch(["ok", "boom", "hang"], call, 0.05))
                assert got["results"] == ["OK", None, None], f"results were {got['results']!r}"
                assert got["errors"] == {1: "ValueError", 2: "TimeoutError"}, f"errors were {got['errors']!r}"

            def test_other_exception_class_names_reported():
                got = asyncio.run(run_batch(["key", "fine"], call, 0.5))
                assert got["errors"] == {0: "KeyError"}, f"errors were {got['errors']!r}"
                assert got["results"] == [None, "FINE"], f"results were {got['results']!r}"

            def test_runs_concurrently_and_respects_timeout():
                start = time.perf_counter()
                asyncio.run(run_batch(["hang1", "hang2", "hang3", "x"], call, 0.05))
                elapsed = time.perf_counter() - start
                assert elapsed < 0.5, f"batch took {elapsed:.2f}s - timeouts should run in parallel"

            def test_empty_batch_returns_empty_results_and_errors():
                got = asyncio.run(run_batch([], call, 0.1))
                assert got == {"results": [], "errors": {}}, f"got {got!r}"

            def test_uses_gather_with_return_exceptions():
                assert "return_exceptions" in source(), "use asyncio.gather(..., return_exceptions=True)"
        ''',
        "solution": r'''
            import asyncio


            async def run_batch(prompts, call, timeout):
                outcomes = await asyncio.gather(
                    *(asyncio.wait_for(call(p), timeout) for p in prompts),
                    return_exceptions=True,
                )
                results, errors = [], {}
                for i, outcome in enumerate(outcomes):
                    if isinstance(outcome, BaseException):
                        results.append(None)
                        errors[i] = type(outcome).__name__
                    else:
                        results.append(outcome)
                return {"results": results, "errors": errors}
        ''',
    },
]
