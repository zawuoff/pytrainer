PROJECT = {
    "id": "prompt-kit",
    "title": "Prompt Kit: templates, messages, transcripts",
    "order": 1,
    "level": "Beginner",
    "estimated_hours": 1.5,
    "requires": ["functions", "dicts", "strings", "errors"],
    "tags": ["prompts", "chat", "messages"],
    "main": "app.py",
    "files": ["app.py"],
    "brief": r'''
        # Prompt Kit

        Every LLM app builds prompts out of templates ("Summarise this {document} for a
        {audience}") and sends them as a list of chat messages
        (`[{"role": "system", ...}, {"role": "user", ...}]`). Bugs here are silent and
        expensive: a missing variable sends a literal `{document}` to the model, a
        misplaced system message gets ignored, a bad role makes the API reject the call.

        You will build a small, strict prompt toolkit in **`app.py`**.

        ## Interface

        ### `class MissingVariablesError(KeyError)`
        Raised by `render` when variables are missing. It must have an attribute
        **`missing`**: a list of the missing placeholder names, in order of first
        appearance in the template, without duplicates. `str(err)` must mention every
        missing name.

        ### `find_placeholders(template: str) -> list[str]`
        Return the placeholder names used in `template`, unique, in order of first
        appearance.

        - A placeholder is `{name}` where `name` is a valid Python identifier
          (letters, digits, underscore, not starting with a digit).
        - `{{` and `}}` are escaped literal braces, never placeholders.
        - Anything else in braces (e.g. `{ x }`, `{1abc}`, `{}`) is plain text.

        ### `render(template: str, **variables) -> str`
        Replace every placeholder with `str(value)` of the matching variable.

        - Missing variables: raise `MissingVariablesError` listing **all** of them
          (not just the first).
        - Extra variables are ignored.
        - `{{` renders as `{` and `}}` renders as `}`.
        - Values are inserted literally: a value containing `{other}` is **not**
          rendered again.

        ### `build_messages(user: str, system: str | None = None, history: list[dict] | None = None) -> list[dict]`
        Build the message list to send to a chat API:
        `[system (if given)] + history + [{"role": "user", "content": user}]`.

        - Every message is a dict with exactly the keys `"role"` and `"content"`.
        - `history` may only contain `"user"` and `"assistant"` messages.
        - The result must contain **new** dicts: mutating the result must not change
          the caller's `history`, and `history` itself must not be modified.
        - The result must pass `validate_messages`; raise `ValueError` for any
          invalid input (e.g. empty `user`, bad history entry, system role in history).

        ### `validate_messages(messages: list[dict]) -> None`
        Raise `ValueError` (with a helpful message) if any rule is broken, otherwise
        return `None`:

        1. `messages` is a non-empty list.
        2. Each message is a dict whose `"role"` is one of `"system"`, `"user"`,
           `"assistant"`, and whose `"content"` is a `str` that is not empty or
           whitespace-only.
        3. A `"system"` message may only appear at index 0.
        4. The last message has role `"user"`.

        ### `format_transcript(messages: list[dict], names: dict | None = None, include_system: bool = True) -> str`
        Format a conversation for logs or for pasting into a summarisation prompt.

        - One block per message: `"<Label>: <content>"`. The default label is the role
          capitalised (`System`, `User`, `Assistant`); `names` can override labels per
          role, e.g. `{"assistant": "Bot"}`.
        - Continuation lines of multi-line content are indented by **two spaces**.
        - Blocks are joined with `"\n"`. No trailing newline.
        - `include_system=False` leaves out system messages.
        - An empty list gives `""`.

        ## Examples

        ```python
        render("Hello {name}, you have {n} tokens", name="Ada", n=42)
        # 'Hello Ada, you have 42 tokens'

        render("Use JSON like {{\"k\": {value}}}", value=1)
        # 'Use JSON like {"k": 1}'

        render("{a} {b} {a} {c}", b=1)
        # raises MissingVariablesError; err.missing == ["a", "c"]

        build_messages("Hi", system="Be brief.")
        # [{'role': 'system', 'content': 'Be brief.'}, {'role': 'user', 'content': 'Hi'}]

        print(format_transcript([
            {"role": "user", "content": "Two lines?"},
            {"role": "assistant", "content": "Line one\nLine two"},
        ], names={"assistant": "Bot"}))
        # User: Two lines?
        # Bot: Line one
        #   Line two
        ```

        ## Running it locally

        Add a small `if __name__ == "__main__":` block that renders a template and
        prints a transcript, then run `python app.py`. Upload `app.py` when you are done.
    ''',
    "explore": r'''
        ## Things to research

        - **`string.Formatter().parse`** and **`string.Template`** in the standard
          library. How do they tokenise format strings? Why does `str.format` blow up
          with `KeyError` on the first missing name only, and why is that a problem
          when templates are written by non-programmers?
        - **Chat message roles**: read how the OpenAI *Chat Completions* API and the
          Anthropic *Messages* API differ (Anthropic takes `system` as a separate
          parameter, not a message; it also requires user/assistant turns to
          alternate). How would you adapt `build_messages` for each?
        - **Prompt injection**: why inserting user-supplied text into a template is
          risky, and what "delimiting untrusted input" means.

        ## Make it real (optional, ungraded)

        ```bash
        uv pip install openai     # or: pip install openai
        export OPENAI_API_KEY=sk-...
        ```

        ```python
        from openai import OpenAI
        from app import render, build_messages

        client = OpenAI()   # reads OPENAI_API_KEY
        prompt = render("Explain {topic} to a {audience} in 3 sentences.",
                        topic="embeddings", audience="product manager")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=build_messages(prompt, system="You are a concise teacher."),
        )
        print(resp.choices[0].message.content)
        ```
    ''',
    "rubric": [
        "Placeholder parsing is implemented once and reused by find_placeholders and render (no duplicated logic)",
        "Escaped braces and non-identifier braces are handled deliberately, not by accident of str.format",
        "Validation errors raise ValueError / MissingVariablesError with messages that say what is wrong and where",
        "build_messages never mutates its inputs and returns fresh dicts",
        "Functions are small, well named, with type hints and short docstrings",
        "No global mutable state; no print statements inside library functions",
    ],
    "starter_files": {
        "app.py": r'''
            """Prompt Kit: templates, chat messages and transcripts."""


            class MissingVariablesError(KeyError):
                ...


            def find_placeholders(template):
                ...


            def render(template, **variables):
                ...


            def build_messages(user, system=None, history=None):
                ...


            def validate_messages(messages):
                ...


            def format_transcript(messages, names=None, include_system=True):
                ...
        ''',
    },
    "solution_files": {
        "app.py": r'''
            """Prompt Kit: templates, chat messages and transcripts."""

            from __future__ import annotations

            import re

            ROLES = ("system", "user", "assistant")
            _TOKEN = re.compile(r"\{\{|\}\}|\{([A-Za-z_][A-Za-z0-9_]*)\}")


            class MissingVariablesError(KeyError):
                """Raised when a template references variables that were not supplied."""

                def __init__(self, missing: list[str]):
                    self.missing = list(missing)
                    super().__init__(f"missing template variables: {', '.join(self.missing)}")

                def __str__(self) -> str:
                    return self.args[0]


            def find_placeholders(template: str) -> list[str]:
                """Placeholder names in order of first appearance, without duplicates."""
                seen: dict[str, None] = {}
                for match in _TOKEN.finditer(template):
                    if match.group(1):
                        seen.setdefault(match.group(1))
                return list(seen)


            def render(template: str, **variables) -> str:
                """Fill {placeholders}; {{ and }} are literal braces."""
                missing = [name for name in find_placeholders(template) if name not in variables]
                if missing:
                    raise MissingVariablesError(missing)

                def substitute(match: re.Match) -> str:
                    token = match.group(0)
                    if token == "{{":
                        return "{"
                    if token == "}}":
                        return "}"
                    return str(variables[match.group(1)])

                return _TOKEN.sub(substitute, template)


            def _check_message(message: object, position: int) -> None:
                if not isinstance(message, dict):
                    raise ValueError(f"message {position} must be a dict")
                role = message.get("role")
                if role not in ROLES:
                    raise ValueError(f"message {position} has invalid role {role!r}")
                content = message.get("content")
                if not isinstance(content, str) or not content.strip():
                    raise ValueError(f"message {position} must have non-empty string content")


            def validate_messages(messages: list[dict]) -> None:
                """Raise ValueError if the message list is not a valid chat request."""
                if not isinstance(messages, list) or not messages:
                    raise ValueError("messages must be a non-empty list")
                for position, message in enumerate(messages):
                    _check_message(message, position)
                    if message["role"] == "system" and position != 0:
                        raise ValueError(f"system message only allowed first (found at {position})")
                if messages[-1]["role"] != "user":
                    raise ValueError("the last message must come from the user")


            def build_messages(user: str, system: str | None = None,
                               history: list[dict] | None = None) -> list[dict]:
                """system + history + new user turn, as fresh dicts."""
                messages = []
                if system is not None:
                    messages.append({"role": "system", "content": system})
                for position, message in enumerate(history or []):
                    _check_message(message, position)
                    if message["role"] == "system":
                        raise ValueError("history may not contain system messages")
                    messages.append({"role": message["role"], "content": message["content"]})
                messages.append({"role": "user", "content": user})
                validate_messages(messages)
                return messages


            def format_transcript(messages: list[dict], names: dict | None = None,
                                  include_system: bool = True) -> str:
                """Readable 'Label: content' transcript, continuation lines indented."""
                labels = {role: role.capitalize() for role in ROLES} | (names or {})
                blocks = []
                for message in messages:
                    role = message["role"]
                    if role == "system" and not include_system:
                        continue
                    first, *rest = message["content"].split("\n")
                    lines = [f"{labels.get(role, role.capitalize())}: {first}"]
                    lines += [f"  {line}" for line in rest]
                    blocks.append("\n".join(lines))
                return "\n".join(blocks)


            if __name__ == "__main__":
                prompt = render("Summarise {doc} for a {audience}.", doc="the report", audience="CEO")
                print(format_transcript(build_messages(prompt, system="Be brief.")))
        ''',
    },
    "tests": r'''
        from app import (MissingVariablesError, build_messages, find_placeholders,
                         format_transcript, render, validate_messages)

        def expect_value_error(fn, *args, **kwargs):
            try:
                fn(*args, **kwargs)
            except ValueError:
                return
            raise AssertionError(f"expected ValueError for args={args!r} kwargs={kwargs!r}")

        def test_render_fills_placeholders_with_str_values():
            got = render("Hello {name}, you have {n} tokens", name="Ada", n=42)
            assert got == "Hello Ada, you have 42 tokens", f"got {got!r}"

        def test_render_reports_all_missing_variables_in_order():
            try:
                render("{a} {b} {a} {c}", b=1)
            except MissingVariablesError as err:
                assert err.missing == ["a", "c"], f"missing={err.missing!r}"
                assert "a" in str(err) and "c" in str(err), f"str(err)={str(err)!r}"
                assert isinstance(err, KeyError)
                return
            raise AssertionError("expected MissingVariablesError")

        def test_escaped_braces_become_literal():
            got = render('Reply as JSON: {{"answer": {value}}}', value=7)
            assert got == 'Reply as JSON: {"answer": 7}', f"got {got!r}"

        def test_non_identifier_braces_are_plain_text():
            template = "set {} and { x } and {1abc} but {ok}"
            assert find_placeholders(template) == ["ok"], f"got {find_placeholders(template)!r}"
            got = render(template, ok="yes")
            assert got == "set {} and { x } and {1abc} but yes", f"got {got!r}"

        def test_values_are_not_rendered_twice_and_extras_ignored():
            got = render("Q: {question}", question="what is {secret}?", unused=1)
            assert got == "Q: what is {secret}?", f"got {got!r}"

        def test_find_placeholders_unique_in_order():
            got = find_placeholders("{b}{a}{{c}}{b}{d_1}")
            assert got == ["b", "a", "d_1"], f"got {got!r}"

        def test_build_messages_shape():
            got = build_messages("Hi", system="Be brief.",
                                 history=[{"role": "user", "content": "a"},
                                          {"role": "assistant", "content": "b"}])
            assert got == [
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "a"},
                {"role": "assistant", "content": "b"},
                {"role": "user", "content": "Hi"},
            ], f"got {got!r}"
            assert build_messages("Hi") == [{"role": "user", "content": "Hi"}]

        def test_build_messages_does_not_share_or_mutate_history():
            history = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
            got = build_messages("next", history=history)
            got[0]["content"] = "CHANGED"
            assert history == [{"role": "user", "content": "a"},
                               {"role": "assistant", "content": "b"}], "history was modified"

        def test_build_messages_rejects_bad_input():
            expect_value_error(build_messages, "   ")
            expect_value_error(build_messages, "hi", history=[{"role": "system", "content": "x"}])
            expect_value_error(build_messages, "hi", history=[{"role": "tool", "content": "x"}])
            expect_value_error(build_messages, "hi", history=[{"role": "user"}])

        def test_validate_messages_accepts_valid_list():
            assert validate_messages([{"role": "system", "content": "s"},
                                      {"role": "user", "content": "u"}]) is None

        def test_validate_messages_rejects_each_rule():
            expect_value_error(validate_messages, [])
            expect_value_error(validate_messages, ["hello"])
            expect_value_error(validate_messages, [{"role": "bot", "content": "x"}])
            expect_value_error(validate_messages, [{"role": "user", "content": ""}])
            expect_value_error(validate_messages, [{"role": "user", "content": 5}])
            expect_value_error(validate_messages, [{"role": "user", "content": "a"},
                                                   {"role": "system", "content": "s"},
                                                   {"role": "user", "content": "b"}])
            expect_value_error(validate_messages, [{"role": "user", "content": "a"},
                                                   {"role": "assistant", "content": "b"}])

        def test_format_transcript_labels_and_indentation():
            got = format_transcript([
                {"role": "system", "content": "Be nice"},
                {"role": "user", "content": "Two lines?"},
                {"role": "assistant", "content": "Line one\nLine two"},
            ], names={"assistant": "Bot"})
            want = "System: Be nice\nUser: Two lines?\nBot: Line one\n  Line two"
            assert got == want, f"got {got!r}"

        def test_format_transcript_can_skip_system_and_handles_empty():
            got = format_transcript([{"role": "system", "content": "s"},
                                     {"role": "user", "content": "u"}], include_system=False)
            assert got == "User: u", f"got {got!r}"
            assert format_transcript([]) == ""
    ''',
}
