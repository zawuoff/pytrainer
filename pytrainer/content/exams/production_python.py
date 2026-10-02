"""Module test: Production Python (classes -> async)."""

EXAM = {
    "module": "production-python",
    "title": "Production Python: module test",
    "intro": r'''
        This is a **test**, not a lesson. It checks the whole Production Python module:
        classes, dataclasses and type hints, writing tests, generators and async code -
        the things that turn "code that runs" into "code a team can ship".

        **How it works**

        - There are **no hints and no tutor** while you take it. You get the prompt, the
          checks and your own knowledge.
        - Every rule the checks test is in the prompt or its examples. One exercise asks
          *you* to write the tests: they must pass on correct code and catch planted bugs.
        - Two exercises are *research* tasks: one links to the official docs, the other asks
          you to find the right standard-library tool yourself. Reading docs under time
          pressure is a real engineering skill.

        **Passing**

        Pass at least **70%** of the exercises and the module counts as done: you can skip
        its chapters and move on. Not there yet? The chapters will show you what to practise.
    ''',
    "pass_ratio": 0.7,
}

EXERCISES = [
    {
        "id": "exam-production-python-1",
        "title": "Versioned prompt template",
        "difficulty": 2,
        "prompt": r'''
            Teams keep prompts as versioned objects instead of loose strings, so a change to a
            prompt is a new version, never an edit in place.

            **Write:** a **frozen dataclass** `PromptTemplate` with fields
            `name: str`, `text: str`, `version: int = 1`, and two methods:

            - `render(**values)` → the `text` with its `{placeholders}` filled in from `values`
              (a string). If a placeholder has no value, raise `ValueError` with the message
              `"missing value for '<field>'"`, e.g. `"missing value for 'topic'"`.
            - `new_version(text)` → a **new** `PromptTemplate` with the same `name`, the new
              `text`, and `version` one higher. The original is unchanged.

            **Rules**
            - It must be a dataclass created with `frozen=True`, so assigning to a field
              raises `dataclasses.FrozenInstanceError`.
            - Extra values that the text doesn't use are ignored.
            - Two templates with the same name, text and version are equal (`==`).

            **Examples**
            ```python
            t = PromptTemplate("summarize", "Summarize {doc} in {n} bullet points.")
            t.render(doc="the report", n=3)    # returns "Summarize the report in 3 bullet points."
            t.render(doc="x")                  # raises ValueError("missing value for 'n'")
            t2 = t.new_version("Summarize {doc}.")
            t2.version                         # 2
            t.version                          # still 1
            t.version = 5                      # raises dataclasses.FrozenInstanceError
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass


            class PromptTemplate:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import PromptTemplate

            def test_render_fills_placeholders():
                t = PromptTemplate("summarize", "Summarize {doc} in {n} bullet points.")
                got = t.render(doc="the report", n=3)
                assert got == "Summarize the report in 3 bullet points.", f"got {got!r}"

            def test_default_version_is_1_and_extra_values_ignored():
                t = PromptTemplate("greet", "Hi {name}")
                assert t.version == 1, f"version was {t.version!r}"
                assert t.render(name="Ada", unused="x") == "Hi Ada"

            def test_missing_value_raises_value_error_naming_the_field():
                t = PromptTemplate("summarize", "Summarize {doc} in {n} bullet points.")
                try:
                    t.render(doc="x")
                except ValueError as e:
                    assert str(e) == "missing value for 'n'", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for a missing placeholder")

            def test_new_version_returns_new_object_and_keeps_original():
                t = PromptTemplate("summarize", "old {doc}")
                t2 = t.new_version("new {doc}")
                assert (t2.name, t2.text, t2.version) == ("summarize", "new {doc}", 2), f"got {t2!r}"
                assert (t.text, t.version) == ("old {doc}", 1), "the original template changed"
                assert t2.new_version("v3").version == 3

            def test_is_a_frozen_dataclass():
                t = PromptTemplate("a", "b")
                assert dataclasses.is_dataclass(t), "PromptTemplate is not a dataclass"
                try:
                    t.version = 5
                except dataclasses.FrozenInstanceError:
                    pass
                else:
                    raise AssertionError("assigning a field did not raise FrozenInstanceError")

            def test_equal_templates_compare_equal():
                assert PromptTemplate("a", "b", 2) == PromptTemplate("a", "b", 2)
                assert PromptTemplate("a", "b", 2) != PromptTemplate("a", "b", 3)
        ''',
        "solution": r'''
            from dataclasses import dataclass


            @dataclass(frozen=True)
            class PromptTemplate:
                name: str
                text: str
                version: int = 1

                def render(self, **values) -> str:
                    try:
                        return self.text.format(**values)
                    except KeyError as e:
                        raise ValueError(f"missing value for '{e.args[0]}'")

                def new_version(self, text: str) -> "PromptTemplate":
                    return PromptTemplate(self.name, text, self.version + 1)
        ''',
        "hints": [
            "@dataclass(frozen=True) gives you __init__, __eq__ and the frozen behaviour. str.format(**values) fills placeholders.",
            "When format() can't find a placeholder it raises KeyError, and the missing name is the error's first argument. Catch it and raise ValueError. new_version just builds a fresh instance.",
            "1) Decorate the class with @dataclass(frozen=True) and declare the three fields. 2) render: try return self.text.format(**values) except KeyError as e: raise ValueError(f\"missing value for '{e.args[0]}'\"). 3) new_version: return PromptTemplate(self.name, text, self.version + 1).",
        ],
    },
    {
        "id": "exam-production-python-2",
        "title": "Validated conversation",
        "difficulty": 3,
        "research": {
            "note": "Two dataclass features make this clean: a hook that runs right after the "
                    "generated `__init__` (for validation), and a safe way to give a field a "
                    "mutable default like an empty list. Read both sections before you start.",
            "links": [
                {"title": "dataclasses: post-init processing - Python docs",
                 "url": "https://docs.python.org/3/library/dataclasses.html#post-init-processing"},
                {"title": "dataclasses: mutable default values - Python docs",
                 "url": "https://docs.python.org/3/library/dataclasses.html#mutable-default-values"},
            ],
        },
        "prompt": r'''
            A chat app keeps its history in typed objects that refuse bad data.

            **Write:** two dataclasses.

            `Message` with fields `role: str`, `content: str`, `tokens: int = 0`
            - `role` must be one of `"system"`, `"user"`, `"assistant"`, `"tool"`; otherwise
              creating the message raises `ValueError` with the message `"invalid role: <role>"`.
            - `tokens` below `0` raises `ValueError` with the message `"tokens must be >= 0"`.

            `Conversation` with fields `max_tokens: int = 4000` and `messages: list[Message]`
            (defaults to a new empty list for **each** conversation), and methods:
            - `add(role, content, tokens=0)` → creates a `Message`, appends it and returns it.
              If adding it would make the total tokens greater than `max_tokens`, raise
              `ValueError` with the message `"token budget exceeded"` and don't append.
            - `total_tokens()` → the sum of `tokens` over all messages (an `int`).
            - `to_api()` → a list of `{"role": ..., "content": ...}` dicts, in order.

            **Examples**
            ```python
            c = Conversation(max_tokens=100)
            c.add("system", "Be brief.", 5)
            c.add("user", "Hi", 2)
            c.total_tokens()   # 7
            c.to_api()         # [{"role": "system", "content": "Be brief."}, {"role": "user", "content": "Hi"}]
            c.add("assistant", "long...", 94)   # raises ValueError("token budget exceeded")
            Message("bot", "hi")                # raises ValueError("invalid role: bot")
            Conversation().messages             # [] - and never shared with another Conversation
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass, field


            class Message:
                ...


            class Conversation:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import Conversation, Message

            def expect_value_error(fn, message):
                try:
                    fn()
                except ValueError as e:
                    assert str(e) == message, f"message was {str(e)!r}"
                else:
                    raise AssertionError(f"no ValueError (expected {message!r})")

            def test_message_is_dataclass_with_default_tokens():
                m = Message("user", "Hi")
                assert dataclasses.is_dataclass(m), "Message is not a dataclass"
                assert (m.role, m.content, m.tokens) == ("user", "Hi", 0), f"got {m!r}"

            def test_message_validates_role_and_tokens():
                expect_value_error(lambda: Message("bot", "hi"), "invalid role: bot")
                expect_value_error(lambda: Message("user", "hi", -1), "tokens must be >= 0")

            def test_add_total_and_to_api():
                c = Conversation(max_tokens=100)
                m = c.add("system", "Be brief.", 5)
                assert isinstance(m, Message), f"add returned {m!r}"
                c.add("user", "Hi", 2)
                assert c.total_tokens() == 7, f"total was {c.total_tokens()!r}"
                assert c.to_api() == [{"role": "system", "content": "Be brief."},
                                      {"role": "user", "content": "Hi"}], f"got {c.to_api()!r}"

            def test_budget_exceeded_raises_and_does_not_append():
                c = Conversation(max_tokens=10)
                c.add("user", "a", 4)
                expect_value_error(lambda: c.add("assistant", "b", 7), "token budget exceeded")
                assert len(c.messages) == 1, "the message was appended anyway"
                c.add("assistant", "c", 6)
                assert c.total_tokens() == 10, "reaching the budget exactly should be allowed"

            def test_conversations_do_not_share_messages():
                a, b = Conversation(), Conversation()
                a.add("user", "only in a")
                assert b.messages == [], "two conversations share the same list"
                assert a.max_tokens == 4000, f"default max_tokens was {a.max_tokens!r}"

            def test_invalid_role_via_add_is_rejected():
                c = Conversation()
                expect_value_error(lambda: c.add("robot", "x"), "invalid role: robot")
                assert c.messages == []
        ''',
        "solution": r'''
            from dataclasses import dataclass, field

            ROLES = ("system", "user", "assistant", "tool")


            @dataclass
            class Message:
                role: str
                content: str
                tokens: int = 0

                def __post_init__(self) -> None:
                    if self.role not in ROLES:
                        raise ValueError(f"invalid role: {self.role}")
                    if self.tokens < 0:
                        raise ValueError("tokens must be >= 0")


            @dataclass
            class Conversation:
                max_tokens: int = 4000
                messages: list[Message] = field(default_factory=list)

                def total_tokens(self) -> int:
                    return sum(m.tokens for m in self.messages)

                def add(self, role: str, content: str, tokens: int = 0) -> Message:
                    message = Message(role, content, tokens)
                    if self.total_tokens() + tokens > self.max_tokens:
                        raise ValueError("token budget exceeded")
                    self.messages.append(message)
                    return message

                def to_api(self) -> list[dict]:
                    return [{"role": m.role, "content": m.content} for m in self.messages]
        ''',
        "hints": [
            "Validation goes in __post_init__; the list default needs field(default_factory=list).",
            "Message checks its own role and tokens after init. Conversation.add builds the Message first (so bad roles fail), then checks the budget before appending. to_api is a list comprehension.",
            "1) @dataclass class Message with a __post_init__ that raises the two ValueErrors. 2) @dataclass class Conversation: max_tokens: int = 4000; messages: list[Message] = field(default_factory=list). 3) total_tokens: sum(m.tokens for m in self.messages). 4) add: m = Message(...); if total + tokens > max_tokens raise; append; return m. 5) to_api: [{'role': m.role, 'content': m.content} for m in self.messages].",
        ],
    },
    {
        "id": "exam-production-python-3",
        "title": "Test the token budget",
        "difficulty": 2,
        "mode": "tests",
        "prompt": r'''
            A teammate wrote a `TokenBudget` dataclass (saved as `target.py`). Your job is to
            **write the tests** for it.

            **Behaviour of `target.py`**

            - `TokenBudget(limit)` starts with `used == 0`.
            - `spend(n)` adds `n` to `used`.
              - If `n` is negative, it raises `ValueError` and nothing changes.
              - If `used + n` would be **greater than** `limit`, it raises `ValueError` and
                nothing changes. Spending up to exactly the limit is allowed.
            - `remaining()` returns `limit - used`.

            **Write:** test functions (names starting with `test_`) that import
            `TokenBudget` from `target`.

            **Rules**
            - Your tests must all pass on the correct code.
            - Several buggy versions will be swapped in; for each one, at least one of your
              tests must fail. Think about every rule above, including the edges.

            **Example test**
            ```python
            from target import TokenBudget

            def test_new_budget_has_everything_remaining():
                assert TokenBudget(100).remaining() == 100
            ```
        ''',
        "impl": r'''
            from dataclasses import dataclass


            @dataclass
            class TokenBudget:
                limit: int
                used: int = 0

                def spend(self, n: int) -> None:
                    if n < 0:
                        raise ValueError("cannot spend a negative amount")
                    if self.used + n > self.limit:
                        raise ValueError("budget exceeded")
                    self.used += n

                def remaining(self) -> int:
                    return self.limit - self.used
        ''',
        "mutants": [
            {"name": "refuses to spend up to exactly the limit", "code": r'''
                from dataclasses import dataclass


                @dataclass
                class TokenBudget:
                    limit: int
                    used: int = 0

                    def spend(self, n: int) -> None:
                        if n < 0:
                            raise ValueError("cannot spend a negative amount")
                        if self.used + n >= self.limit:
                            raise ValueError("budget exceeded")
                        self.used += n

                    def remaining(self) -> int:
                        return self.limit - self.used
            '''},
            {"name": "overspending is silently capped instead of raising", "code": r'''
                from dataclasses import dataclass


                @dataclass
                class TokenBudget:
                    limit: int
                    used: int = 0

                    def spend(self, n: int) -> None:
                        if n < 0:
                            raise ValueError("cannot spend a negative amount")
                        self.used = min(self.limit, self.used + n)

                    def remaining(self) -> int:
                        return self.limit - self.used
            '''},
            {"name": "negative amounts are accepted", "code": r'''
                from dataclasses import dataclass


                @dataclass
                class TokenBudget:
                    limit: int
                    used: int = 0

                    def spend(self, n: int) -> None:
                        if self.used + n > self.limit:
                            raise ValueError("budget exceeded")
                        self.used += n

                    def remaining(self) -> int:
                        return self.limit - self.used
            '''},
            {"name": "a refused spend is still counted", "code": r'''
                from dataclasses import dataclass


                @dataclass
                class TokenBudget:
                    limit: int
                    used: int = 0

                    def spend(self, n: int) -> None:
                        if n < 0:
                            raise ValueError("cannot spend a negative amount")
                        self.used += n
                        if self.used > self.limit:
                            raise ValueError("budget exceeded")

                    def remaining(self) -> int:
                        return self.limit - self.used
            '''},
        ],
        "starter": r'''
            from target import TokenBudget


            def test_new_budget_has_everything_remaining():
                ...
        ''',
        "solution": r'''
            from target import TokenBudget


            def raises_value_error(fn):
                try:
                    fn()
                except ValueError:
                    return True
                return False


            def test_new_budget_has_everything_remaining():
                assert TokenBudget(100).remaining() == 100


            def test_spend_reduces_remaining():
                b = TokenBudget(100)
                b.spend(30)
                assert b.used == 30
                assert b.remaining() == 70


            def test_can_spend_exactly_the_limit():
                b = TokenBudget(100)
                b.spend(100)
                assert b.remaining() == 0


            def test_overspending_raises_and_changes_nothing():
                b = TokenBudget(100)
                b.spend(60)
                assert raises_value_error(lambda: b.spend(50))
                assert b.used == 60


            def test_negative_spend_raises_and_changes_nothing():
                b = TokenBudget(100)
                assert raises_value_error(lambda: b.spend(-5))
                assert b.used == 0
        ''',
        "tests": "",
        "hints": [
            "Write one small test per rule in the spec: normal spending, spending exactly the limit, overspending, negative amounts.",
            "For the error rules, check two things: that ValueError is raised, AND that `used` is unchanged afterwards. The edge case 'exactly the limit is allowed' needs its own test.",
            "1) Test a fresh budget's remaining(). 2) Spend some and check used/remaining. 3) Spend exactly the limit and check it doesn't raise. 4) Spend too much inside try/except ValueError, then assert used didn't change. 5) Same for a negative amount.",
        ],
    },
    {
        "id": "exam-production-python-4",
        "title": "Lines from a streamed reply",
        "difficulty": 3,
        "prompt": r'''
            A streaming LLM reply arrives in chunks that don't line up with line breaks. The UI
            wants whole lines as soon as each one is complete.

            **Write:**
            - a dataclass `Line` with fields `index: int` and `text: str`
            - a **generator function** `stream_lines(chunks)`

            - `chunks`: any iterable of strings (it may be a generator that produces chunks slowly)
            - **Yields:** a `Line` for every complete line, in order

            **Rules**
            - A line is complete when a `"\n"` arrives. The yielded `text` doesn't include the `"\n"`.
            - Empty lines (`""`) are skipped and don't use up an index. `index` counts yielded
              lines from `0`.
            - When the chunks run out, any leftover text (not ending in `"\n"`) is yielded as a
              last line if it's not empty.
            - Be lazy: yield each line as soon as it is complete, **before** reading the next chunk.
            - It must be a generator function (it uses `yield`).

            **Examples**
            ```python
            list(stream_lines(["Hel", "lo\nWor", "ld\n\nBye"]))
            # [Line(index=0, text="Hello"), Line(index=1, text="World"), Line(index=2, text="Bye")]
            list(stream_lines([]))           # []
            list(stream_lines(["a\n", "\n"]))  # [Line(index=0, text="a")]
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass


            def stream_lines(chunks):
                ...
        ''',
        "tests": r'''
            import dataclasses
            import inspect
            from solution import Line, stream_lines

            def test_example_stream():
                got = list(stream_lines(["Hel", "lo\nWor", "ld\n\nBye"]))
                assert got == [Line(0, "Hello"), Line(1, "World"), Line(2, "Bye")], f"got {got!r}"

            def test_line_is_a_dataclass():
                assert dataclasses.is_dataclass(Line), "Line is not a dataclass"
                assert Line(index=1, text="x").text == "x"

            def test_is_a_generator_function():
                assert inspect.isgeneratorfunction(stream_lines), "stream_lines does not use yield"

            def test_empty_lines_skipped_and_no_leftover():
                got = list(stream_lines(["a\n", "\n"]))
                assert got == [Line(0, "a")], f"got {got!r}"
                assert list(stream_lines([])) == []

            def test_several_lines_in_one_chunk():
                got = [l.text for l in stream_lines(["x\ny\nz\n"])]
                assert got == ["x", "y", "z"], f"got {got!r}"

            def test_yields_before_reading_the_next_chunk():
                def slow_chunks():
                    yield "first line\nsec"
                    raise RuntimeError("read the next chunk too early")
                gen = stream_lines(slow_chunks())
                got = next(gen)
                assert got == Line(0, "first line"), f"got {got!r}"
        ''',
        "solution": r'''
            from dataclasses import dataclass


            @dataclass
            class Line:
                index: int
                text: str


            def stream_lines(chunks):
                buffer = ""
                index = 0
                for chunk in chunks:
                    buffer += chunk
                    while "\n" in buffer:
                        text, buffer = buffer.split("\n", 1)
                        if text:
                            yield Line(index, text)
                            index += 1
                if buffer:
                    yield Line(index, buffer)
        ''',
        "hints": [
            "Keep a text buffer between chunks. A while loop inside the for loop can pull out every finished line.",
            "Add each chunk to the buffer. While the buffer has a newline, split off the part before it and yield it (unless empty). After the loop, yield whatever is left if it isn't empty.",
            "1) @dataclass class Line: index: int; text: str. 2) buffer = ''; index = 0. 3) for chunk in chunks: buffer += chunk. 4) while '\\n' in buffer: text, buffer = buffer.split('\\n', 1); if text: yield Line(index, text); index += 1. 5) After the loop: if buffer: yield Line(index, buffer).",
        ],
    },
    {
        "id": "exam-production-python-5",
        "title": "Concurrent calls with a limit",
        "difficulty": 3,
        "prompt": r'''
            You need answers for many prompts. Calls should run concurrently, but the provider
            allows only a few at a time.

            **Write:**
            - a dataclass `Result` with fields `prompt: str`, `ok: bool`, `text: str`
            - an **async** function `run_all(prompts, call, limit)`

            - `prompts`: a list of strings
            - `call`: an async function; `await call(prompt)` returns the reply string or raises
            - `limit`: the most calls allowed to run at the same time, an `int`
            - **Returns:** a list of `Result`, one per prompt, **in the same order as `prompts`**

            **Rules**
            - Never have more than `limit` calls running at once, but do run up to `limit` at once.
            - If a call raises an exception, that prompt's result is
              `Result(prompt, False, str(exception))`; other prompts still run.
              A successful call gives `Result(prompt, True, reply)`.
            - If `limit` is less than `1`, raise `ValueError` with the message
              `"limit must be at least 1"`.
            - An empty `prompts` list returns `[]`.

            **Examples**
            ```python
            async def fake_llm(prompt):
                await asyncio.sleep(0.01)
                if prompt == "bad":
                    raise RuntimeError("rate limited")
                return prompt.upper()

            asyncio.run(run_all(["hi", "bad", "yo"], fake_llm, 2))
            # [Result(prompt="hi", ok=True, text="HI"),
            #  Result(prompt="bad", ok=False, text="rate limited"),
            #  Result(prompt="yo", ok=True, text="YO")]
            ```
        ''',
        "starter": r'''
            import asyncio
            from dataclasses import dataclass


            async def run_all(prompts, call, limit):
                ...
        ''',
        "tests": r'''
            import asyncio
            import time
            from solution import Result, run_all

            async def fake_llm(prompt):
                await asyncio.sleep(0.01)
                if prompt == "bad":
                    raise RuntimeError("rate limited")
                return prompt.upper()

            def test_results_in_order_with_errors_captured():
                got = asyncio.run(run_all(["hi", "bad", "yo"], fake_llm, 2))
                assert got == [Result("hi", True, "HI"), Result("bad", False, "rate limited"),
                               Result("yo", True, "YO")], f"got {got!r}"

            def test_order_kept_even_when_later_calls_finish_first():
                async def varied(prompt):
                    await asyncio.sleep(0.05 if prompt == "slow" else 0.001)
                    return prompt
                got = asyncio.run(run_all(["slow", "fast1", "fast2"], varied, 3))
                assert [r.text for r in got] == ["slow", "fast1", "fast2"], f"got {got!r}"

            def test_never_more_than_limit_but_uses_the_limit():
                state = {"active": 0, "peak": 0}
                async def tracked(prompt):
                    state["active"] += 1
                    state["peak"] = max(state["peak"], state["active"])
                    await asyncio.sleep(0.03)
                    state["active"] -= 1
                    return prompt
                asyncio.run(run_all([str(i) for i in range(9)], tracked, 3))
                assert state["peak"] == 3, f"at most {state['peak']} calls ran at once (limit was 3)"

            def test_runs_concurrently_not_one_by_one():
                async def slow(prompt):
                    await asyncio.sleep(0.1)
                    return prompt
                start = time.perf_counter()
                asyncio.run(run_all(["a", "b", "c", "d"], slow, 4))
                took = time.perf_counter() - start
                assert took < 0.3, f"4 calls of 0.1s took {took:.2f}s - they are not concurrent"

            def test_empty_prompts_and_bad_limit():
                assert asyncio.run(run_all([], fake_llm, 2)) == []
                try:
                    asyncio.run(run_all(["x"], fake_llm, 0))
                except ValueError as e:
                    assert str(e) == "limit must be at least 1", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for limit=0")
        ''',
        "solution": r'''
            import asyncio
            from dataclasses import dataclass


            @dataclass
            class Result:
                prompt: str
                ok: bool
                text: str


            async def run_all(prompts, call, limit):
                if limit < 1:
                    raise ValueError("limit must be at least 1")
                semaphore = asyncio.Semaphore(limit)

                async def one(prompt):
                    async with semaphore:
                        try:
                            return Result(prompt, True, await call(prompt))
                        except Exception as e:
                            return Result(prompt, False, str(e))

                return list(await asyncio.gather(*(one(p) for p in prompts)))
        ''',
        "hints": [
            "asyncio.gather runs coroutines concurrently and keeps their order; asyncio.Semaphore limits how many run at once.",
            "Write a small inner async function that handles one prompt: it waits for the semaphore, calls, and turns success or an exception into a Result. Gather one of those per prompt.",
            "1) Raise ValueError if limit < 1. 2) sem = asyncio.Semaphore(limit). 3) async def one(p): async with sem: try: return Result(p, True, await call(p)) except Exception as e: return Result(p, False, str(e)). 4) return list(await asyncio.gather(*(one(p) for p in prompts))).",
        ],
    },
    {
        "id": "exam-production-python-6",
        "title": "Client with a timeout",
        "difficulty": 3,
        "research": {
            "note": "An LLM call can hang. `asyncio` has a built-in way to give up on an awaitable "
                    "after a number of seconds - and cancel it so it doesn't keep running in the "
                    "background. Find it in the asyncio docs (look at what it raises when time runs "
                    "out) instead of building your own timer.",
            "links": [],
        },
        "prompt": r'''
            Wrap a slow async LLM call in a small client that gives up after a time limit.

            **Write:** a class `TimeoutClient`

            - `TimeoutClient(call, seconds)`: `call` is an async function (`await call(prompt)`
              returns a string); `seconds` is the time limit, a number like `0.5`.
            - `timeouts`: an attribute counting how many calls have timed out (starts at `0`).
            - `async ask(prompt)` → the reply string, or `None` if the call took longer than
              `seconds`.

            **Rules**
            - When a call times out it must be **cancelled** (it must not keep running and
              finish later), `ask` returns `None` and `timeouts` goes up by 1.
            - Fast calls return their reply unchanged and don't touch `timeouts`.
            - Errors raised by `call` itself are not caught - they reach the caller.

            **Examples**
            ```python
            async def slow(prompt):
                await asyncio.sleep(1)
                return "late"

            async def fast(prompt):
                return "hi " + prompt

            client = TimeoutClient(fast, 0.5)
            asyncio.run(client.ask("Ada"))    # returns "hi Ada"
            client = TimeoutClient(slow, 0.05)
            asyncio.run(client.ask("x"))      # returns None (after about 0.05 s)
            client.timeouts                   # 1
            ```
        ''',
        "starter": r'''
            import asyncio


            class TimeoutClient:
                ...
        ''',
        "tests": r'''
            import asyncio
            import time
            from solution import TimeoutClient

            async def fast(prompt):
                await asyncio.sleep(0)
                return "hi " + prompt

            def test_fast_call_returns_reply():
                client = TimeoutClient(fast, 0.5)
                got = asyncio.run(client.ask("Ada"))
                assert got == "hi Ada", f"got {got!r}"
                assert client.timeouts == 0, f"timeouts was {client.timeouts!r}"

            def test_slow_call_returns_none_quickly_and_counts():
                async def slow(prompt):
                    await asyncio.sleep(1)
                    return "late"
                client = TimeoutClient(slow, 0.05)
                start = time.perf_counter()
                got = asyncio.run(client.ask("x"))
                took = time.perf_counter() - start
                assert got is None, f"got {got!r}"
                assert took < 0.5, f"ask took {took:.2f}s - it did not give up in time"
                assert client.timeouts == 1, f"timeouts was {client.timeouts!r}"

            def test_timed_out_call_is_cancelled():
                state = {"finished": False}
                async def slow(prompt):
                    await asyncio.sleep(0.2)
                    state["finished"] = True
                    return "late"
                async def scenario():
                    client = TimeoutClient(slow, 0.02)
                    result = await client.ask("x")
                    await asyncio.sleep(0.3)
                    return result
                assert asyncio.run(scenario()) is None
                assert not state["finished"], "the slow call kept running after the timeout"

            def test_timeouts_accumulate_across_calls():
                async def slow(prompt):
                    await asyncio.sleep(1)
                async def scenario():
                    client = TimeoutClient(slow, 0.01)
                    await client.ask("a")
                    await client.ask("b")
                    return client.timeouts
                assert asyncio.run(scenario()) == 2

            def test_errors_from_the_call_are_not_swallowed():
                async def broken(prompt):
                    raise KeyError("boom")
                client = TimeoutClient(broken, 0.5)
                try:
                    asyncio.run(client.ask("x"))
                except KeyError:
                    pass
                else:
                    raise AssertionError("the KeyError from the call was swallowed")
                assert client.timeouts == 0
        ''',
        "solution": r'''
            import asyncio


            class TimeoutClient:
                def __init__(self, call, seconds):
                    self.call = call
                    self.seconds = seconds
                    self.timeouts = 0

                async def ask(self, prompt):
                    try:
                        return await asyncio.wait_for(self.call(prompt), timeout=self.seconds)
                    except TimeoutError:
                        self.timeouts += 1
                        return None
        ''',
        "hints": [
            "Look through the asyncio docs sections on coroutines and tasks for anything about timeouts.",
            "asyncio can wrap an awaitable with a time limit; when time runs out it cancels the awaitable and raises TimeoutError. Catch that error, count it, return None.",
            "1) __init__ stores call and seconds and sets self.timeouts = 0. 2) In async ask: try: return await asyncio.wait_for(self.call(prompt), timeout=self.seconds). 3) except TimeoutError: self.timeouts += 1; return None. (asyncio.timeout() as an async context manager works too.)",
        ],
    },
]
