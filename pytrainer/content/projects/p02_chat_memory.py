PROJECT = {
    "id": "chat-memory",
    "title": "Chat Memory with a Token Budget",
    "order": 2,
    "level": "Beginner",
    "estimated_hours": 2,
    "requires": ["classes", "functions", "lists", "dicts"],
    "tags": ["chat", "tokens", "context-window", "memory"],
    "main": "memory.py",
    "files": ["memory.py"],
    "brief": r'''
        # Chat Memory with a Token Budget

        LLMs are stateless: every request must resend the conversation so far, and the
        whole thing must fit in the model's **context window** (and every token costs
        money). Real chat apps therefore keep a *memory* object that holds the history,
        always keeps the system prompt, drops the oldest turns when the budget is
        exceeded, and optionally replaces what it dropped with a short **summary**
        produced by the model itself.

        Build that memory in **`memory.py`**. The summariser is **injected**: your class
        receives a plain callable, so it can be a real LLM call in production and a
        fake in tests.

        ## Token counting (approximation)

        Use exactly this rule (it is close to what real tokenizers give for English):

        - `count_tokens(text: str) -> int` = `ceil(len(text) / 4)` (so `""` is `0`,
          `"abcde"` is `2`).
        - `message_tokens(message: dict) -> int` = `count_tokens(message["content"]) + 4`
          (4 tokens of per-message overhead for role/formatting).
        - `messages_tokens(messages: list[dict]) -> int` = sum of `message_tokens` of each.

        ## `class ChatMemory`

        ```python
        ChatMemory(max_tokens: int, system: str | None = None, summarize=None)
        ```

        - `max_tokens` must be a positive `int`, otherwise raise `ValueError`.
        - `system`: optional system prompt. It is **pinned**: always the first message,
          never trimmed.
        - `summarize`: optional callable `summarize(messages: list[dict]) -> str`.

        Methods:

        | method | behaviour |
        | --- | --- |
        | `add(role, content)` | Append a message. `role` must be `"user"` or `"assistant"` and `content` a `str`, else `ValueError`. Then trim (see below). |
        | `messages()` | The list to send to the API, as **new** dicts: system message (if any), then the summary message (if any), then the kept history, oldest first. |
        | `total_tokens()` | `messages_tokens(self.messages())`. |
        | `clear()` | Forget the history **and** the summary. The system prompt stays. |

        ### Trimming rules

        After each `add`, while `total_tokens() > max_tokens`:

        1. Drop the **oldest** history message. The system prompt and the summary are
           not history and are never dropped this way.
        2. The **newest** message is never dropped, even if it alone is over budget
           (stop trimming when only one history message is left).

        If `summarize` was given and any messages were dropped during this `add`:

        - Call `summarize(batch)` where `batch` is: the current summary message (if one
          exists), followed by the dropped messages oldest first (as `{"role", "content"}`
          dicts).
        - The result replaces the summary. The summary message is
          `{"role": "system", "content": "Summary of earlier conversation: " + result}`.
        - The summary costs tokens too. If the budget is still exceeded after
          summarising, keep trimming and summarising (each round folds the previous
          summary into the new one) until it fits or only one history message is left.

        Without `summarize`, dropped messages are simply forgotten.

        ## Example

        ```python
        mem = ChatMemory(max_tokens=30, system="Be brief.")   # system costs 3 + 4 = 7
        mem.add("user", "a" * 40)        # 10 + 4 = 14  -> total 21
        mem.add("assistant", "b" * 40)   # total 35 > 30 -> oldest user msg dropped
        [m["content"][:1] for m in mem.messages()]   # ['B', 'b']
        mem.total_tokens()               # 21
        ```

        ## Running it locally

        Write a quick loop in `if __name__ == "__main__":` that adds messages with a
        fake summariser (e.g. `lambda msgs: f"{len(msgs)} earlier messages"`) and prints
        `messages()` after each step. Upload `memory.py`.
    ''',
    "explore": r'''
        ## Things to research

        - **Tokenizers**: look up *byte-pair encoding (BPE)* and the `tiktoken` library.
          Compare `ceil(len/4)` with real counts for English, code and non-English
          text. Anthropic exposes a *count tokens* endpoint for the same purpose.
        - **Context window strategies**: sliding window vs. summary memory vs.
          retrieval-based memory. Search for "conversation summary buffer memory".
        - **Prompt caching**: why keeping the *prefix* of your messages stable (pinned
          system prompt!) makes requests cheaper and faster with OpenAI and Anthropic.

        ## Make it real (optional, ungraded)

        ```bash
        pip install anthropic          # or: uv add anthropic
        export ANTHROPIC_API_KEY=sk-ant-...
        ```

        ```python
        import anthropic
        from memory import ChatMemory

        client = anthropic.Anthropic()

        def summarize(messages):
            text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
            resp = client.messages.create(
                model="claude-haiku-4-5", max_tokens=200,
                messages=[{"role": "user", "content": "Summarise briefly:\n" + text}],
            )
            return resp.content[0].text

        mem = ChatMemory(max_tokens=2000, system="You are helpful.", summarize=summarize)
        ```

        Note that Anthropic takes the system prompt as a separate `system=` argument, so
        you will need to split `mem.messages()` before sending.
    ''',
    "rubric": [
        "Token counting follows the spec exactly and is defined once, reused by the class",
        "Trimming loop is clearly written, terminates, and never drops the system prompt or the newest message",
        "Summariser is dependency-injected and called only when something was dropped",
        "messages() returns fresh dicts so callers cannot corrupt internal state",
        "Input validation raises ValueError with clear messages",
        "Readable class design: private helpers, type hints, short docstrings",
    ],
    "starter_files": {
        "memory.py": r'''
            """Conversation memory with a token budget."""


            def count_tokens(text):
                ...


            def message_tokens(message):
                ...


            def messages_tokens(messages):
                ...


            class ChatMemory:
                def __init__(self, max_tokens, system=None, summarize=None):
                    ...

                def add(self, role, content):
                    ...

                def messages(self):
                    ...

                def total_tokens(self):
                    ...

                def clear(self):
                    ...
        ''',
    },
    "solution_files": {
        "memory.py": r'''
            """Conversation memory with a token budget."""

            from __future__ import annotations

            import math
            from typing import Callable

            MESSAGE_OVERHEAD = 4
            SUMMARY_PREFIX = "Summary of earlier conversation: "

            Summarizer = Callable[[list[dict]], str]


            def count_tokens(text: str) -> int:
                """Rough token estimate: one token per 4 characters."""
                return math.ceil(len(text) / 4)


            def message_tokens(message: dict) -> int:
                return count_tokens(message["content"]) + MESSAGE_OVERHEAD


            def messages_tokens(messages: list[dict]) -> int:
                return sum(message_tokens(m) for m in messages)


            class ChatMemory:
                """Keeps a pinned system prompt plus as much recent history as fits."""

                def __init__(self, max_tokens: int, system: str | None = None,
                             summarize: Summarizer | None = None):
                    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens <= 0:
                        raise ValueError("max_tokens must be a positive int")
                    self.max_tokens = max_tokens
                    self.system = system
                    self._summarize = summarize
                    self._summary: str | None = None
                    self._history: list[dict] = []

                def add(self, role: str, content: str) -> None:
                    if role not in ("user", "assistant"):
                        raise ValueError(f"role must be 'user' or 'assistant', not {role!r}")
                    if not isinstance(content, str):
                        raise ValueError("content must be a string")
                    self._history.append({"role": role, "content": content})
                    self._trim()

                def messages(self) -> list[dict]:
                    out = []
                    if self.system is not None:
                        out.append({"role": "system", "content": self.system})
                    summary = self._summary_message()
                    if summary:
                        out.append(summary)
                    out.extend(dict(m) for m in self._history)
                    return out

                def total_tokens(self) -> int:
                    return messages_tokens(self.messages())

                def clear(self) -> None:
                    self._history.clear()
                    self._summary = None

                def _summary_message(self) -> dict | None:
                    if self._summary is None:
                        return None
                    return {"role": "system", "content": SUMMARY_PREFIX + self._summary}

                def _over_budget(self) -> bool:
                    return self.total_tokens() > self.max_tokens and len(self._history) > 1

                def _trim(self) -> None:
                    while self._over_budget():
                        dropped = []
                        while self._over_budget():
                            dropped.append(self._history.pop(0))
                        if self._summarize is None:
                            return
                        previous = self._summary_message()
                        batch = ([previous] if previous else []) + dropped
                        self._summary = self._summarize(batch)


            if __name__ == "__main__":
                mem = ChatMemory(40, system="Be brief.", summarize=lambda ms: f"{len(ms)} msgs")
                for i in range(5):
                    mem.add("user", f"question number {i} " * 3)
                    print(mem.total_tokens(), mem.messages())
        ''',
    },
    "tests": r'''
        from memory import ChatMemory, count_tokens, message_tokens, messages_tokens

        def msg(role, content):
            return {"role": role, "content": content}

        def test_count_tokens_rule():
            got = [count_tokens(t) for t in ["", "a", "abcd", "abcde", "x" * 41]]
            assert got == [0, 1, 1, 2, 11], f"got {got!r}"

        def test_message_tokens_add_overhead():
            assert message_tokens(msg("user", "abcde")) == 6
            assert messages_tokens([msg("user", "abcd"), msg("assistant", "")]) == 9

        def test_invalid_budget_and_roles_raise_value_error():
            for bad in (0, -5, 2.5, "100"):
                try:
                    ChatMemory(bad)
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"ChatMemory({bad!r}) should raise ValueError")
            mem = ChatMemory(100)
            for role, content in (("system", "x"), ("tool", "x"), ("user", 42)):
                try:
                    mem.add(role, content)
                except ValueError:
                    continue
                raise AssertionError(f"add({role!r}, {content!r}) should raise ValueError")

        def test_messages_puts_system_first_and_returns_copies():
            mem = ChatMemory(1000, system="Be brief.")
            mem.add("user", "hi")
            mem.add("assistant", "hello")
            got = mem.messages()
            assert got == [msg("system", "Be brief."), msg("user", "hi"),
                           msg("assistant", "hello")], f"got {got!r}"
            got[1]["content"] = "HACKED"
            got.append(msg("user", "extra"))
            assert mem.messages()[1]["content"] == "hi", "messages() must return copies"
            assert len(mem.messages()) == 3

        def test_trims_oldest_to_fit_budget():
            mem = ChatMemory(30, system="Be brief.")
            mem.add("user", "a" * 40)
            mem.add("assistant", "b" * 40)
            got = [m["content"][:1] for m in mem.messages()]
            assert got == ["B", "b"], f"got {got!r}"
            assert mem.total_tokens() == 21, f"total={mem.total_tokens()}"

        def test_total_never_exceeds_budget_when_possible():
            mem = ChatMemory(60, system="sys")
            for i in range(20):
                mem.add("user" if i % 2 == 0 else "assistant", "word " * (i % 5 + 1))
                assert mem.total_tokens() <= 60, f"over budget after add #{i}: {mem.total_tokens()}"
            contents = [m["content"] for m in mem.messages()]
            assert contents[0] == "sys"
            assert contents[-1] == "word " * (19 % 5 + 1), "newest message must be kept"

        def test_newest_message_kept_even_if_too_big():
            mem = ChatMemory(20, system="s")
            mem.add("user", "short")
            mem.add("user", "z" * 400)
            got = mem.messages()
            assert got == [msg("system", "s"), msg("user", "z" * 400)], f"got {[m['content'][:5] for m in got]}"

        def test_summarize_not_called_when_everything_fits():
            calls = []
            mem = ChatMemory(1000, summarize=lambda ms: calls.append(ms) or "S")
            mem.add("user", "hi")
            mem.add("assistant", "hello")
            assert calls == [], "summarize was called although nothing was dropped"
            assert all(m["content"].find("Summary") == -1 for m in mem.messages())

        def test_summary_replaces_dropped_messages():
            calls = []
            def fake(ms):
                calls.append([dict(m) for m in ms])
                return "S"
            mem = ChatMemory(50, system="sys", summarize=fake)
            mem.add("user", "u" * 80)
            mem.add("assistant", "a" * 40)
            mem.add("user", "q" * 40)
            assert calls and calls[0] == [msg("user", "u" * 80)], f"summarize got {calls!r}"
            got = mem.messages()
            assert got[0] == msg("system", "sys")
            assert got[1] == msg("system", "Summary of earlier conversation: S"), f"got {got[1]!r}"
            assert [m["content"][:1] for m in got[2:]] == ["a", "q"]
            assert mem.total_tokens() <= 50

        def test_previous_summary_is_folded_into_next_one():
            calls = []
            def fake(ms):
                calls.append([dict(m) for m in ms])
                return f"n{len(calls)}"
            mem = ChatMemory(40, system="sys", summarize=fake)
            for ch in "abcdef":
                mem.add("user", ch * 40)
            assert len(calls) >= 2, f"summarize called {len(calls)} time(s)"
            last = calls[-1]
            assert last[0]["content"].startswith("Summary of earlier conversation: n"), \
                f"first item passed to summarize should be the previous summary, got {last[0]!r}"
            assert mem.messages()[1]["content"] == f"Summary of earlier conversation: n{len(calls)}"
            assert mem.messages()[-1]["content"] == "f" * 40
            assert mem.total_tokens() <= 40

        def test_clear_keeps_system_only():
            mem = ChatMemory(30, system="keep me", summarize=lambda ms: "S")
            for ch in "abc":
                mem.add("user", ch * 40)
            mem.clear()
            assert mem.messages() == [msg("system", "keep me")], f"got {mem.messages()!r}"
            mem.add("user", "again")
            assert mem.messages()[-1] == msg("user", "again")

        def test_works_without_system_prompt():
            mem = ChatMemory(15)
            mem.add("user", "a" * 20)       # 9
            mem.add("assistant", "b" * 20)  # 9 -> 18 > 15
            assert mem.messages() == [msg("assistant", "b" * 20)], f"got {mem.messages()!r}"
    ''',
}
