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
            ## Coroutines, await and asyncio.run

            A **server** is a remote computer that answers requests sent over a network. A call to a
            web API, such as an LLM (large language model) service that writes text, spends most of
            its time waiting for the server to answer. **Async** code lets a program do other work
            during that wait. This lesson covers the three things you need first.

            ```python
            import asyncio

            async def greet(name):
                return "hello " + name

            async def main():
                text = await greet("Ana")
                print(text)
                print("after")

            asyncio.run(main())
            # hello Ana
            # after
            ```

            `async def` defines a **coroutine function**. Calling it does not run its body. The call
            returns a **coroutine**: an object that holds the function body and its arguments, ready to
            run.

            `await greet("Ana")` runs that coroutine to its `return` and evaluates to the returned
            value, `"hello Ana"`. You can only write `await` inside an `async def` function.

            `asyncio.run(main())` starts the **event loop**: the object in the `asyncio` module that
            runs coroutines. It runs `main` from top to bottom and returns its result. You call
            `asyncio.run` from normal code, outside any `async def`.

            The lines after an `await` wait for it. `print(text)` runs only after `greet` has returned, and
            `print("after")` runs after that.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `asyncio.run(main())` runs `main`. It prints `start`, then `await greet("Ana")`
            runs `greet` to the end and evaluates to its return value, `"hi Ana"`, which is
            printed. `await` waits for the result. It does not skip ahead.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Follow the code from `asyncio.run(main())`: it runs the body of `main` from top to bottom.",
            "`await greet(...)` waits until `greet` returns, then gives you its return value.",
            "First `main` prints its own line. Then it gets the value returned by `greet` (text + name) and prints it.",
        ],
    },
    {
        "id": "async-s2",
        "title": "Wait politely",
        "difficulty": 0,
        "lesson": r'''
            ## asyncio.sleep

            The event loop runs one coroutine at a time. When a coroutine has to wait, the event loop
            can run another coroutine during that wait. This only works if the wait is done with
            `await`.

            `await asyncio.sleep(seconds)` pauses the current coroutine for that many seconds. Only
            this coroutine is paused. The event loop can run other coroutines in the meantime.

            ```python
            import asyncio

            async def think(seconds):
                print("thinking...")
                await asyncio.sleep(seconds)
                print("done after", seconds, "s")

            asyncio.run(think(0.1))
            # thinking...
            # done after 0.1 s
            ```

            `time.sleep(seconds)` also waits, but it stops the whole program, so the event loop cannot
            run anything else. Stopping the event loop is called **blocking** it. `asyncio.sleep` is
            **non-blocking**. Never use `time.sleep` inside async code.

            The fake LLMs in this chapter use `asyncio.sleep` to imitate a slow server.

            `asyncio.sleep` is itself a coroutine function, so you must `await` it.
            `asyncio.sleep(1)` without `await` creates a coroutine and waits for nothing.
        ''',
        "prompt": r'''
            `fetch_reply` pretends to call an LLM: it waits a moment, then returns a reply.
            One name is missing.

            **Write:** replace the `___` in `fetch_reply(prompt)`

            - `prompt`: a `str`, e.g. `"hi"`
            - **Returns:** a `str` like `"reply: hi"` (already written for you)

            **Rules**
            - Fill in the name of the `asyncio` function that waits `0.01` seconds **without
              blocking** the event loop.
            - `fetch_reply` must stay an `async def` function.

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
            "The `asyncio` module has its own version of a well-known waiting function.",
            "It has the same name as the function in the `time` module, but you `await` it.",
            "Replace `___` with `sleep`, so the line reads `await asyncio.sleep(0.01)`.",
        ],
    },
    {
        "id": "async-s3",
        "title": "Fix the missing await",
        "difficulty": 0,
        "lesson": r'''
            ## A missing await

            Calling a coroutine function only creates a coroutine object. The function body has not
            run yet, so there is no return value. `await` runs the body and gives you the value.

            ```python
            import asyncio

            async def get_score():
                return 7

            async def main():
                coro = get_score()
                print(type(coro).__name__)
                value = await coro
                print(value + 1)

            asyncio.run(main())
            # coroutine
            # 8
            ```

            The first `print` shows `coroutine`: the type of the object you have before awaiting.
            `await coro` runs `get_score` and evaluates to `7`, so the second `print` shows `8`.

            If you forget `await`, you use the coroutine object where you wanted the value. The next
            example raises on purpose.

            ```python
            import asyncio

            async def get_score():
                return 7

            async def main():
                score = get_score()
                print(score + 1)

            asyncio.run(main())
            # TypeError: unsupported operand type(s) for +: 'coroutine' and 'int'
            ```

            A number cannot be added to a coroutine, so Python raises `TypeError`. Python also prints
            `RuntimeWarning: coroutine 'get_score' was never awaited`. That warning always means an
            `await` is missing.

            This is the most common async bug. When a value in async code has an unexpected type,
            check for a missing `await` first.
        ''',
        "prompt": r'''
            `double_answer()` should use the number returned by the coroutine `get_answer()`
            (which is `42`), but it crashes with a `TypeError`. Read the error and fix the bug.

            **Write:** fix `double_answer()` (one small change on one line)

            - **Returns:** an `int`: twice what `get_answer()` returns, i.e. `84`

            **Rules**
            - Don't change `get_answer()`.
            - The result must be the number `84` (an `int`), not a coroutine object.

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
            "What does calling an `async def` function give you if you don't wait for it?",
            "`get_answer()` alone is a coroutine, not the number 42. You must wait for its result.",
            "Add the keyword `await` in front of `get_answer()` on the line that assigns `answer`.",
        ],
    },
    {
        "id": "async-s6",
        "title": "Who finishes first?",
        "difficulty": 0,
        "lesson": r'''
            ## asyncio.gather

            So far each `await` waited for one coroutine. `asyncio.gather(a, b, c)` takes several
            coroutines and runs them **concurrently**: their waiting periods overlap in time. `await`
            on it gives a list of their results.

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

            The event loop runs the first coroutine until its `await asyncio.sleep(0.2)`, then runs
            the second one until its `await asyncio.sleep(0.1)`. Both are now waiting at the same
            moment. The whole program takes about 0.2 seconds, the longest wait, not 0.3 seconds.

            Step through the stages to see which coroutine finishes first and where its result goes.

            ```diagram
            {"type":"flow","title":"Order of events in asyncio.gather(fake_llm(\"long\", 0.2), fake_llm(\"short\", 0.1))","steps":[{"label":"main awaits gather","detail":"gather schedules both coroutines on the event loop. main is paused at its await until both have finished.","code":"replies = await asyncio.gather(fake_llm(\"long\", 0.2), fake_llm(\"short\", 0.1))"},{"label":"long runs to its await","detail":"The event loop runs fake_llm(\"long\", 0.2) until await asyncio.sleep(0.2). That coroutine is paused for 0.2 seconds.","code":"await asyncio.sleep(0.2)   # long is paused"},{"label":"short runs to its await","detail":"The event loop switches to fake_llm(\"short\", 0.1) and runs it until await asyncio.sleep(0.1). Both coroutines are now paused.","code":"await asyncio.sleep(0.1)   # short is paused"},{"label":"short finishes first","detail":"After 0.1 seconds the event loop resumes short. It returns 'SHORT'. gather stores it in position 1 because short was the second argument.","code":"results so far: [not ready, 'SHORT']"},{"label":"long finishes","detail":"After 0.2 seconds the event loop resumes long. It returns 'LONG'. gather stores it in position 0.","code":"results so far: ['LONG', 'SHORT']"},{"label":"main resumes","detail":"Both coroutines are finished, so the await in main evaluates to the list, in argument order.","code":"print(replies)\n# ['LONG', 'SHORT']"}]}
            ```

            The result list is in the order you **passed** the coroutines, not the order they
            **finished**. `"short"` finished first, but `'LONG'` is still first in the list.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `gather` starts both jobs at the same time. `fast` only sleeps 0.01 s, so it prints
            first; `slow` prints 0.04 s later. But the returned list follows the order the
            coroutines were **passed** to `gather` (`slow`, then `fast`), not the order they
            finished.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Both jobs start together. Which `sleep` ends first?",
            "The `print` inside `job` happens when each job finishes, so the shorter sleep prints first. The final list follows a different rule.",
            "Line 1-2: the jobs' own prints, shortest delay first. Line 3: the list printed by `main`, in the order the jobs were written in the `gather` call (strings shown with quotes).",
        ],
    },
    {
        "id": "async-s5",
        "title": "Two calls at once",
        "difficulty": 0,
        "lesson": r'''
            ## Passing the call as a parameter

            In real apps the function that calls the LLM is usually passed in as a parameter, so
            tests can pass a fake one. A function is a value, as you saw in the functions chapter.

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

            `call` is the function `shout`. `call(prompt)` creates the coroutine. `await` runs it and
            gives its return value.

            ## Sequential awaits and gather

            Two `await` lines in a row are **sequential**: the second coroutine starts only after the
            first has returned. With `gather` you create both coroutines first, then pass them
            together. `await asyncio.gather(...)` returns a `list`.

            ```python
            import asyncio
            import time

            async def shout(text):
                await asyncio.sleep(0.1)
                return text.upper()

            async def main():
                start = time.perf_counter()
                one = await shout("a")
                two = await shout("b")
                print([one, two], round(time.perf_counter() - start, 1))

                start = time.perf_counter()
                both = await asyncio.gather(shout("a"), shout("b"))
                print(both, round(time.perf_counter() - start, 1))

            asyncio.run(main())
            # ['A', 'B'] 0.2
            # ['A', 'B'] 0.1
            ```

            `time.perf_counter()` returns the reading of a clock in seconds. Subtracting the
            reading at the start from a later reading gives the elapsed time. That is the second
            value on each line. Both versions are correct. The sequential one is slower.

            Step through the stages to compare the two versions.

            ```diagram
            {"type":"flow","title":"Sequential awaits compared with gather","steps":[{"label":"Sequential: first await","detail":"shout(\"a\") runs and pauses for 0.1 seconds. main is paused at this line too, so shout(\"b\") does not exist yet.","code":"one = await shout(\"a\")   # 0.0 s to 0.1 s"},{"label":"Sequential: second await","detail":"shout(\"a\") has returned 'A'. Only now is shout(\"b\") created and run. It pauses for another 0.1 seconds.","code":"two = await shout(\"b\")   # 0.1 s to 0.2 s"},{"label":"Sequential: total","detail":"The two waits happen one after the other, so the total is their sum.","code":"['A', 'B'] 0.2"},{"label":"gather: both start","detail":"Both coroutines are created before anything is awaited. The event loop runs shout(\"a\") to its sleep, then shout(\"b\") to its sleep.","code":"both = await asyncio.gather(shout(\"a\"), shout(\"b\"))"},{"label":"gather: waits overlap","detail":"Both coroutines are paused during the same 0.1 seconds. Each returns when its sleep ends.","code":"shout(\"a\")   # 0.0 s to 0.1 s\nshout(\"b\")   # 0.0 s to 0.1 s"},{"label":"gather: total","detail":"The total is the longest single wait. The list is in argument order.","code":"['A', 'B'] 0.1"}]}
            ```
        ''',
        "prompt": r'''
            Sending two prompts to an LLM one after the other wastes time. Send both at once
            and wait for both replies.

            **Write:** the coroutine `async def ask_two(call, first, second)`

            - `call`: an async function that takes one prompt; `await call("a")` gives its reply
            - `first`: a `str`, the first prompt, e.g. `"a"`
            - `second`: a `str`, the second prompt, e.g. `"b"`
            - **Returns:** a `list` of the two replies, `[reply_to_first, reply_to_second]`

            **Rules**
            - Run both calls **at the same time** (*concurrently*) with `asyncio.gather`, not one
              after the other: a check verifies that both calls are running together.
            - The result must be a `list` (not a tuple), in the order `first`, `second`.

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
            "`asyncio.gather(...)` takes several coroutines and runs them together.",
            "Create both coroutines by calling `call` twice, pass them to `gather`, and wait for it.",
            "1) Build `call(first)` and `call(second)`. 2) Pass both to `asyncio.gather`. 3) `await` it and return what it gives back (already a list).",
        ],
    },
    {
        "id": "async-s4",
        "title": "What gets streamed?",
        "difficulty": 0,
        "lesson": r'''
            ## Async generators and async for

            LLM APIs **stream**: the reply arrives in small pieces, so the user sees the first words
            before the whole reply is finished.

            You know generators from the generators chapter: a `def` function that uses `yield`. An
            `async def` function that uses `yield` is an **async generator**. It can `await` between
            items. You read it with `async for`, which you can only write inside an `async def`
            function.

            ```python
            import asyncio

            async def countdown():
                for n in (3, 2, 1):
                    await asyncio.sleep(0)
                    yield n

            async def main():
                async for number in countdown():
                    print(number)

            asyncio.run(main())
            # 3
            # 2
            # 1
            ```

            `await asyncio.sleep(0)` waits for zero seconds. It takes the place of waiting for the
            next piece from a server.

            `async for` asks the generator for its next item. The generator runs until its next
            `yield` and gives that value to the loop variable. The loop body runs. Then the generator
            continues from the line after the `yield`. When the generator's function body ends, the
            `async for` loop ends.

            A plain `for` loop cannot read an async generator. `for number in countdown():` raises
            `TypeError: 'async_generator' object is not iterable`. Write `async for`.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `stream` is an **async generator** (`async def` + `yield`). `async for` asks it for one
            token at a time and prints each on its own line, in order. When the generator runs
            out, the loop ends and `end` is printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`async for` works like a normal `for` loop, but over an async generator.",
            "Each `yield` hands one token to the loop, which prints it. After the last token, the loop is over.",
            "Print each of the three tokens on its own line in list order, then the line printed after the loop.",
        ],
    },
    {
        "id": "async-1",
        "hints": [
            'Use `await asyncio.sleep(delay)` in the coroutine, and `asyncio.run(...)` in the regular function.',
            'The coroutine waits then returns an f-string. The plain function creates the coroutine and hands it to `asyncio.run`, which runs it and returns its result.',
            '1) In `fake_complete`: `await asyncio.sleep(delay)`, then return the text with the prompt in square brackets followed by ` ok`. 2) In `complete_sync`: return `asyncio.run(fake_complete(prompt))`. Never use `time.sleep`.',
        ],
        "title": "Your first coroutine",
        "difficulty": 1,
        "lesson": r'''
            ## Calling async code from normal code

            Most of a program is normal code: scripts and plain `def` functions. Normal code cannot use
            `await`. It runs a coroutine with `asyncio.run(...)`. That call starts an event loop, runs
            the coroutine to the end, closes the event loop and returns the coroutine's return value.

            ```python
            import asyncio

            async def slow_add(a, b):
                await asyncio.sleep(0.05)
                return a + b

            def add_now(a, b):
                return asyncio.run(slow_add(a, b))

            print(add_now(2, 3))
            # 5
            ```

            `add_now` is a regular `def` function, so its callers do not need `await` or `asyncio`.
            Many libraries offer a regular function like this around their async code.

            Code inside `async def` is called **async code**. All other code is **sync code**. Sync
            code runs a coroutine with `asyncio.run`. Async code runs a coroutine with `await`.

            `asyncio.run` is only for sync code. Calling it inside a coroutine that is already running
            raises `RuntimeError: asyncio.run() cannot be called from a running event loop`. Inside a
            coroutine, use `await`.
        ''',
        "prompt": r'''
            Before calling a real LLM, build a fake one: a coroutine that "thinks" for a
            moment, plus a normal function so non-async code can use it too.

            **Write:** two functions

            1. `async def fake_complete(prompt, delay=0.01)` (a *coroutine function*)
               - `prompt`: a `str`, e.g. `"hi"`
               - `delay`: a `float`, seconds to wait, e.g. `0.05`; defaults to `0.01`
               - **Returns:** a `str` like `"[hi] ok"`: the prompt in square brackets, a
                 space, then `ok`
            2. `def complete_sync(prompt)` (a **regular** function, not `async`)
               - `prompt`: a `str`, e.g. `"summarise this"`
               - **Returns:** the result of `fake_complete(prompt)`, e.g. `"[summarise this] ok"`

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
            'An async generator is an `async def` that uses `yield`. To read any async iterable, use `async for`.',
            'In the generator, loop over the words of the text, sleep with `await`, then yield each word. In `collect`, loop with `async for` and gather the items into a list.',
            '1) `stream_tokens`: `for word in text.split():` then `await asyncio.sleep(delay)` then `yield word`. 2) `collect`: start an empty list, `async for item in stream:` append it, return the list (an async list comprehension also works).',
        ],
        "title": "Streaming tokens",
        "difficulty": 1,
        "lesson": r'''
            ## Writing an async generator

            In the previous step, "What gets streamed?", you read an async generator. Now you write one, plus a
            function that reads a whole stream into a list. That is useful in tests, where you want
            the complete reply as one value.

            ```python
            import asyncio

            async def letters(word):
                for ch in word:
                    await asyncio.sleep(0)
                    yield ch

            async def main():
                got = [ch async for ch in letters("abc")]
                print(got)

            asyncio.run(main())
            # ['a', 'b', 'c']
            ```

            `[ch async for ch in letters("abc")]` is an **async comprehension**: a list comprehension
            that uses `async for`. An `async for` loop that calls `.append()` builds the same list.

            Generators are **lazy**: they produce the next item only when it is requested. An async
            generator is lazy too.

            ```python
            import asyncio

            async def letters(word):
                for ch in word:
                    print("producing", ch)
                    yield ch

            async def main():
                async for ch in letters("abc"):
                    print("got", ch)
                    break

            asyncio.run(main())
            # producing a
            # got a
            ```

            The loop stops after one item, so the generator never produces `b` or `c`. This is why a
            stream can show the first word to the user before the rest of the reply exists.

            Any object you can loop over with `async for` is called an **async iterable**. Async
            generators are the most common kind, but not the only one. A function that reads a stream
            should accept any async iterable.
        ''',
        "prompt": r'''
            LLM APIs stream their replies piece by piece. Fake a stream, and write a helper
            that gathers a whole stream into a list.

            **Write:** two functions

            1. `async def stream_tokens(text, delay=0)`: an **async generator** (`async def`
               that uses `yield`)
               - `text`: a `str`, e.g. `"Hello  there world"` (may be empty)
               - `delay`: seconds to wait before each word; defaults to `0`
               - **Yields:** each word of `text` (split on any whitespace), one at a time, in order
            2. `async def collect(stream)`
               - `stream`: **any** async iterable (something you can loop over with `async for`),
                 not only `stream_tokens`
               - **Returns:** a `list` of all its items, in order

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
            ## Exceptions in coroutines

            An exception raised inside a coroutine is raised again at the `await` that runs it, the
            same way an exception raised inside a function is raised again at the line that called
            it. You catch it with `try` / `except` around the `await`.

            ```python
            import asyncio

            async def flaky(prompt):
                raise ValueError("model refused")

            async def main():
                try:
                    print(await flaky("hi"))
                except ValueError as err:
                    print("caught:", err)
                    print(type(err).__name__)

            asyncio.run(main())
            # caught: model refused
            # ValueError
            ```

            `flaky("hi")` raises `ValueError` when it is awaited. The `except` block catches it, so the
            program continues instead of stopping with a traceback.

            In an LLM app this is how you turn a failed request into a value that the rest of the
            program can handle.

            `type(err).__name__` gives the exception's class name as a string, here `"ValueError"`.
            You saw it in the errors chapter. It is useful in log messages.

            The `try` must wrap the `await`. A `try` that wraps only the line that creates the
            coroutine catches nothing, because the exception is raised while the coroutine runs.
        ''',
        "prompt": r'''
            A failed LLM request should become a clear message, not a crash.

            **Write:** the coroutine `async def safe_reply(call, prompt)`

            - `call`: an async function that takes one prompt; `await call("hi")` gives its
              reply, or raises an exception
            - `prompt`: a `str`, e.g. `"hi"`
            - **Returns:** the reply of `call(prompt)`; if the call raises any `Exception`,
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
            "Exceptions raised inside a coroutine come out of the `await`, so the familiar `try` / `except` works.",
            "Put the `await call(prompt)` inside `try`. In `except Exception as err`, build the message from the exception's class name.",
            "1) `try:` return the awaited reply. 2) `except Exception as err:` return `\"error: \"` plus `type(err).__name__`. 3) Don't call `call` a second time anywhere.",
        ],
    },
    {
        "id": "async-8",
        "title": "Count the failures",
        "difficulty": 1,
        "lesson": r'''
            ## Exceptions in gather

            By default, if one coroutine passed to `gather` raises, `await asyncio.gather(...)` raises
            that exception. You get no result list, so the replies of the other coroutines are not
            available. In a batch of 100 LLM calls, one failure should not make you lose 99 good replies.

            ```python
            import asyncio

            async def fake_llm(prompt):
                await asyncio.sleep(0.01)
                if prompt == "boom":
                    raise KeyError("choices")
                return prompt.upper()

            async def main():
                try:
                    replies = await asyncio.gather(fake_llm("a"), fake_llm("boom"), fake_llm("b"))
                    print(replies)
                except KeyError:
                    print("the whole gather raised")

            asyncio.run(main())
            # the whole gather raised
            ```

            `fake_llm("a")` and `fake_llm("b")` both succeed, but `replies` is never assigned and the
            first `print` never runs.

            `gather` has a keyword argument that changes this. With it, an exception is **returned**
            in the result list, at the position of the coroutine that raised it, instead of being
            raised. Finding that argument in the docs is this step's research task.

            You then check each item of the list with `isinstance(item, Exception)`.

            ```python
            print(isinstance(KeyError("choices"), Exception))
            print(isinstance("A", Exception))
            # True
            # False
            ```

            An exception object is a value like any other, so it can be stored in a list and counted.
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

            **Write:** the coroutine `async def count_outcomes(prompts, call)`

            - `prompts`: a `list` of `str`, e.g. `["a", "boom", "b"]` (may be empty)
            - `call`: an async function that takes one prompt; it returns a reply or raises
            - **Returns:** a `dict` `{"ok": <int>, "failed": <int>}`: how many calls returned
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
            "The research link shows a `gather` keyword that puts exceptions into the result list instead of raising them.",
            "Gather one `call(p)` per prompt with that keyword set to `True`, then count how many results are exception objects.",
            "1) `outcomes = await asyncio.gather(*(call(p) for p in prompts), return_exceptions=True)`. 2) Count items where `isinstance(item, Exception)`. 3) `ok` is the total minus that count. 4) Return the dict.",
        ],
    },
    {
        "id": "async-3",
        "hints": [
            '`asyncio.gather` runs many coroutines concurrently and returns results in the order given.',
            "Create one coroutine per prompt (don't await them one by one), pass them all to `gather` with `*`, and await the result.",
            '1) Build the coroutines: `call(p)` for each p in prompts. 2) Unpack them into `asyncio.gather(*...)`. 3) `await` it and return the result as a list.',
        ],
        "title": "Fan out with gather",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            You have a batch of prompts to send to an LLM. Send them all at once (this is
            called *fanning out*) instead of waiting for each reply before sending the next.

            **Write:** the coroutine `async def ask_all(prompts, call)`

            - `prompts`: a `list` of `str`, e.g. `["a", "b", "c"]` (may be empty)
            - `call`: an async function that takes one prompt; `await call("a")` gives its reply
            - **Returns:** a `list` with one reply per prompt, in the **same order as `prompts`**

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
            '`asyncio.wait_for(coroutine, timeout)` cancels the coroutine if it takes too long and raises a timeout error.',
            'Wrap the call in `wait_for` inside try/except. Only catch the timeout exception, so other errors still propagate.',
            "1) `try:` return `await asyncio.wait_for(call(prompt), timeout)`. 2) `except asyncio.TimeoutError:` return `fallback`. 3) Don't catch any other exception.",
        ],
        "title": "Timeout guard",
        "difficulty": 2,
        "prompt": r'''
            An LLM request can hang. Guard it: give up after a time limit and use a fallback
            answer instead.

            **Write:** the coroutine `async def with_timeout(call, prompt, timeout, fallback=None)`

            - `call`: an async function that takes one prompt; `await call("hi")` gives its reply
            - `prompt`: a `str`, e.g. `"hi"`
            - `timeout`: a `float`, the time limit in seconds, e.g. `0.03`
            - `fallback`: the value to return on timeout, e.g. `"timed out"`; defaults to `None`
            - **Returns:** the reply of `call(prompt)` if it finishes within `timeout` seconds,
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
            'An `asyncio.Semaphore(limit)` used with `async with` lets at most `limit` tasks inside at once.',
            'Validate `limit`, create one semaphore, wrap each call in a small inner coroutine that acquires the semaphore, then gather all the wrapped calls.',
            '1) If `limit < 1`, raise ValueError. 2) `sem = asyncio.Semaphore(limit)`. 3) Define `async def guarded(p):` with `async with sem: return await call(p)`. 4) `await asyncio.gather(*(guarded(p) for p in prompts))` and return it as a list.',
        ],
        "title": "Rate-limited fan out",
        "difficulty": 3,
        "prompt": r'''
            LLM providers rate-limit you, so you must cap how many requests are in flight
            at the same time.

            **Write:** the coroutine `async def ask_limited(prompts, call, limit)`

            - `prompts`: a `list` of `str`, e.g. `["a", "b", "c", "d"]`
            - `call`: an async function that takes one prompt; `await call("a")` gives its reply
            - `limit`: an `int`, the maximum number of calls running at once, e.g. `2`
            - **Returns:** a `list` with one reply per prompt, in the **same order as `prompts`**

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
            'Combine `asyncio.wait_for` (per-call timeout) with `asyncio.gather(..., return_exceptions=True)`.',
            'Gather one `wait_for(call(p), timeout)` per prompt. Afterwards, each outcome is either a result or an exception object; sort them into results and errors by index.',
            '1) Await a `gather` over one `wait_for(call(p), timeout)` per prompt, passing `return_exceptions=True`. 2) Loop with `enumerate`. 3) If `isinstance(outcome, BaseException)`: append None and store `type(outcome).__name__` under the index. 4) Else append the outcome. 5) Return the dict.',
        ],
        "title": "Resilient batch",
        "difficulty": 3,
        "prompt": r'''
            In a batch job, one failing or hanging LLM request must not stop the others.
            Run them all, and report which ones failed and why.

            **Write:** the coroutine `async def run_batch(prompts, call, timeout)`

            - `prompts`: a `list` of `str`, e.g. `["ok", "boom", "hang"]` (may be empty)
            - `call`: an async function that takes one prompt; it may return a reply, raise any
              exception, or hang
            - `timeout`: a `float`, the time limit in seconds for **each** call, e.g. `0.05`
            - **Returns:** a dict with exactly two keys:
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
