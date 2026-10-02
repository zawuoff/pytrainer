PROJECT = {
    "id": "cli-chat",
    "title": "Terminal Chat App",
    "order": 6,
    "level": "Intermediate",
    "estimated_hours": 2,
    "requires": ["scripts", "env", "json", "files", "classes"],
    "tags": ["cli", "chat", "argparse", "providers"],
    "main": "chat.py",
    "files": ["chat.py"],
    "brief": r'''
        # Terminal Chat App

        Most AI engineers keep a little command-line chat tool around to poke at
        models, prompts and system messages. It is also the smallest complete LLM app:
        argument parsing, configuration from environment variables, a conversation
        loop, persistence, and a **provider abstraction** so the same app can talk to
        OpenAI, Anthropic, a local model, or a fake one in tests.

        Build **`chat.py`**, runnable as `python chat.py [options]`.

        ## Command line

        ```
        python chat.py [--model MODEL] [--system TEXT] [--history FILE]
        ```

        - `--model`: model name. If omitted, use the env var `CHAT_MODEL`, and if that
          is unset or empty, `"gpt-4o-mini"`.
        - `--system`: optional system prompt (sent to the provider as the first
          message, role `"system"`).
        - `--history`: optional path of a JSONL history file (see below).

        ## Provider

        The env var `PYTRAINER_PROVIDER` selects the provider (default `"openai"`):

        - `"echo"`: the built-in **`EchoProvider`**, no network. Its reply is
          `"echo: "` + the content of the **last user message**.
        - `"openai"`: a provider that uses the real OpenAI SDK (not tested; import
          `openai` lazily inside it so the file works without the package).
        - anything else: print `error: unknown provider '<name>'` to **stderr** and
          exit with status **2** (before printing anything to stdout).

        Every provider has the method `complete(messages: list[dict], model: str) -> str`,
        where `messages` is the full conversation in chat-API format.

        ## Session behaviour (exact output)

        1. On start, if the history file exists, load its messages into the
           conversation and print `(loaded N messages from FILE)`.
        2. Print `Chatting with MODEL (type /quit to exit)`.
        3. Read lines from **standard input** (`sys.stdin`) until `/quit` or end of
           input. Strip each line; ignore empty lines. Only print an input prompt
           such as `you> ` when stdin is a terminal (`sys.stdin.isatty()`).
        4. Commands:
           - `/quit`: stop reading.
           - `/reset`: forget the conversation (the system prompt stays), empty the
             history file if one is used, print `(conversation reset)`.
           - `/history`: print every non-system message as `ROLE: CONTENT`
             (e.g. `user: hi`), one per line, or `(empty)` if there are none.
           - any other line starting with `/`: print `unknown command: /word`
             (the first word of the line) and continue.
        5. Any other line is a user message: add it to the conversation, call the
           provider with the whole conversation, add the reply as an `"assistant"`
           message and print `assistant: REPLY`. If the provider raises, print
           `error: ...` to stderr, drop that user message and continue.
        6. With `--history FILE`, every user and assistant message is **appended** to
           FILE as one JSON object per line: `{"role": "user", "content": "hi"}`. The
           system prompt is never written to the file.
        7. Exit with status 0.

        Example session:

        ```
        $ printf 'hello\n/history\n/quit\nignored\n' | PYTRAINER_PROVIDER=echo python chat.py --model tiny
        Chatting with tiny (type /quit to exit)
        assistant: echo: hello
        user: hello
        assistant: echo: hello
        ```

        ## Importable interface

        The tests also import these from `chat.py`, so running the app must be guarded
        by `if __name__ == "__main__":`.

        | name | spec |
        | --- | --- |
        | `EchoProvider` | class with `complete(messages, model) -> str` as above |
        | `get_provider(name: str)` | return a provider instance for `"echo"` / `"openai"`; `ValueError` for any other name |
        | `parse_args(argv: list[str] \| None = None)` | return an `argparse.Namespace` with `model` (already resolved with the env/default rule), `system` and `history` (both `None` when not given) |
        | `main(argv: list[str] \| None = None) -> int` | run the app, return the exit status |

        ## Running it locally

        ```bash
        PYTRAINER_PROVIDER=echo python chat.py --history chat.jsonl
        ```

        Upload `chat.py`.
    ''',
    "explore": r'''
        ## Things to research

        - **Streaming responses**: with `stream=True` the API sends the reply as a
          series of chunks (server-sent events). Look up how to iterate them with the
          OpenAI SDK (`for chunk in stream: chunk.choices[0].delta.content`) and how to
          print them without newlines (`print(..., end="", flush=True)`). Why does
          streaming make a chat UI feel much faster even though the total time is the
          same?
        - **The OpenAI Python SDK**: `OpenAI()` client, `client.chat.completions.create`,
          error classes (`RateLimitError`, `APITimeoutError`), and built-in retries.
          Also have a look at the newer *Responses API*.
        - **`typing.Protocol`**: a clean way to describe "anything with a
          `complete(messages, model)` method" without inheritance.

        ## Make it real (optional, ungraded)

        ```bash
        pip install openai
        export OPENAI_API_KEY=sk-...
        PYTRAINER_PROVIDER=openai python chat.py --system "You are a pirate."
        ```

        ```python
        class OpenAIProvider:
            def __init__(self):
                from openai import OpenAI      # lazy import
                self.client = OpenAI()         # reads OPENAI_API_KEY

            def complete(self, messages, model):
                resp = self.client.chat.completions.create(model=model, messages=messages)
                return resp.choices[0].message.content
        ```

        Then add a `--stream` flag, and try an `AnthropicProvider` (remember the
        system prompt goes in the separate `system=` argument there).
    ''',
    "rubric": [
        "Providers share one small interface; the chat loop does not know which provider it is using",
        "argparse is used idiomatically; env-var defaults are resolved in one place",
        "Command handling is clean (a dispatch dict or small functions), not one giant if/elif block mixing I/O and state",
        "History file handling uses explicit UTF-8, JSONL append, and tolerates a missing file",
        "Errors go to stderr with proper exit codes; provider failures do not crash the session",
        "Top-level code is guarded by if __name__ == '__main__' and main() returns an exit status",
    ],
    "starter_files": {
        "chat.py": r'''
            """A small terminal chat app with pluggable LLM providers."""

            import argparse
            import os
            import sys


            class EchoProvider:
                def complete(self, messages, model):
                    ...


            def get_provider(name):
                ...


            def parse_args(argv=None):
                ...


            def main(argv=None):
                ...


            if __name__ == "__main__":
                sys.exit(main())
        ''',
    },
    "solution_files": {
        "chat.py": r'''
            """A small terminal chat app with pluggable LLM providers."""

            from __future__ import annotations

            import argparse
            import json
            import os
            import sys
            from pathlib import Path
            from typing import Protocol

            DEFAULT_MODEL = "gpt-4o-mini"


            class Provider(Protocol):
                def complete(self, messages: list[dict], model: str) -> str: ...


            class EchoProvider:
                """Offline provider for tests: repeats the last user message."""

                def complete(self, messages: list[dict], model: str) -> str:
                    last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
                    return f"echo: {last}"


            class OpenAIProvider:
                def __init__(self) -> None:
                    from openai import OpenAI  # imported lazily: optional dependency
                    self._client = OpenAI()

                def complete(self, messages: list[dict], model: str) -> str:
                    resp = self._client.chat.completions.create(model=model, messages=messages)
                    return resp.choices[0].message.content or ""


            PROVIDERS = {"echo": EchoProvider, "openai": OpenAIProvider}


            def get_provider(name: str) -> Provider:
                try:
                    factory = PROVIDERS[name]
                except KeyError:
                    raise ValueError(f"unknown provider '{name}'") from None
                return factory()


            def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
                parser = argparse.ArgumentParser(description="Chat with an LLM from the terminal.")
                parser.add_argument("--model", help="model name (default: $CHAT_MODEL or gpt-4o-mini)")
                parser.add_argument("--system", help="system prompt")
                parser.add_argument("--history", help="JSONL file to load and append the conversation to")
                args = parser.parse_args(argv)
                args.model = args.model or os.environ.get("CHAT_MODEL") or DEFAULT_MODEL
                return args


            class HistoryFile:
                """Append-only JSONL log of the conversation (optional)."""

                def __init__(self, path: str | None) -> None:
                    self.path = Path(path) if path else None

                def load(self) -> list[dict]:
                    if not self.path or not self.path.exists():
                        return []
                    lines = self.path.read_text(encoding="utf-8").splitlines()
                    return [json.loads(line) for line in lines if line.strip()]

                def append(self, message: dict) -> None:
                    if self.path:
                        with self.path.open("a", encoding="utf-8") as fh:
                            fh.write(json.dumps(message, ensure_ascii=False) + "\n")

                def clear(self) -> None:
                    if self.path:
                        self.path.write_text("", encoding="utf-8")


            class ChatSession:
                def __init__(self, provider: Provider, model: str, system: str | None,
                             history: HistoryFile) -> None:
                    self.provider = provider
                    self.model = model
                    self.system = [{"role": "system", "content": system}] if system else []
                    self.history = history
                    self.turns: list[dict] = []
                    self.commands = {"/reset": self.reset, "/history": self.show_history}

                def reset(self) -> None:
                    self.turns.clear()
                    self.history.clear()
                    print("(conversation reset)")

                def show_history(self) -> None:
                    if not self.turns:
                        print("(empty)")
                    for message in self.turns:
                        print(f"{message['role']}: {message['content']}")

                def ask(self, text: str) -> None:
                    user = {"role": "user", "content": text}
                    try:
                        reply = self.provider.complete(self.system + self.turns + [user], self.model)
                    except Exception as exc:
                        print(f"error: {exc}", file=sys.stderr)
                        return
                    assistant = {"role": "assistant", "content": reply}
                    for message in (user, assistant):
                        self.turns.append(message)
                        self.history.append(message)
                    print(f"assistant: {reply}")

                def handle(self, line: str) -> bool:
                    """Process one input line; return False to stop."""
                    if line == "/quit":
                        return False
                    if line.startswith("/"):
                        command = line.split()[0]
                        action = self.commands.get(command)
                        if action is None:
                            print(f"unknown command: {command}")
                        else:
                            action()
                    else:
                        self.ask(line)
                    return True


            def _lines(stream):
                interactive = stream.isatty()
                while True:
                    if interactive:
                        print("you> ", end="", flush=True)
                    line = stream.readline()
                    if not line:
                        return
                    yield line.strip()


            def main(argv: list[str] | None = None) -> int:
                args = parse_args(argv)
                name = os.environ.get("PYTRAINER_PROVIDER", "openai")
                try:
                    provider = get_provider(name)
                except ValueError as exc:
                    print(f"error: {exc}", file=sys.stderr)
                    return 2
                except ImportError:
                    print("error: the openai package is not installed", file=sys.stderr)
                    return 2
                history = HistoryFile(args.history)
                session = ChatSession(provider, args.model, args.system, history)
                session.turns = history.load()
                if session.turns:
                    print(f"(loaded {len(session.turns)} messages from {args.history})")
                print(f"Chatting with {args.model} (type /quit to exit)")
                for line in _lines(sys.stdin):
                    if line and not session.handle(line):
                        break
                return 0


            if __name__ == "__main__":
                sys.exit(main())
        ''',
    },
    "tests": r'''
        import json
        import os
        from chat import EchoProvider, get_provider, parse_args

        ECHO = {"PYTRAINER_PROVIDER": "echo"}

        def chat(stdin, args=(), env=None):
            full = dict(ECHO)
            full.update(env or {})
            result = run_script(list(args), stdin=stdin, env=full)
            assert result.returncode == 0, f"exit status {result.returncode}, stderr: {result.stderr[-300:]}"
            return result.stdout.splitlines()

        def read_jsonl(path):
            with open(path, encoding="utf-8") as fh:
                return [json.loads(line) for line in fh if line.strip()]

        def test_echo_provider_replies_to_last_user_message():
            p = EchoProvider()
            msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "first"},
                    {"role": "assistant", "content": "x"}, {"role": "user", "content": "second"}]
            assert p.complete(msgs, "m") == "echo: second", f"got {p.complete(msgs, 'm')!r}"

        def test_get_provider():
            assert isinstance(get_provider("echo"), EchoProvider)
            try:
                get_provider("nope")
            except ValueError:
                return
            raise AssertionError("get_provider('nope') should raise ValueError")

        def test_parse_args_model_resolution():
            old = os.environ.pop("CHAT_MODEL", None)
            try:
                a = parse_args([])
                assert a.model == "gpt-4o-mini", f"default model {a.model!r}"
                assert a.system is None and a.history is None
                os.environ["CHAT_MODEL"] = "env-model"
                assert parse_args([]).model == "env-model"
                b = parse_args(["--model", "cli-model", "--system", "Be nice", "--history", "h.jsonl"])
                assert (b.model, b.system, b.history) == ("cli-model", "Be nice", "h.jsonl")
            finally:
                os.environ.pop("CHAT_MODEL", None)
                if old is not None:
                    os.environ["CHAT_MODEL"] = old

        def test_banner_uses_model_from_flag_env_or_default():
            assert chat("/quit\n")[0] == "Chatting with gpt-4o-mini (type /quit to exit)"
            assert chat("/quit\n", env={"CHAT_MODEL": "from-env"})[0] == \
                "Chatting with from-env (type /quit to exit)"
            assert chat("/quit\n", ["--model", "flag"], env={"CHAT_MODEL": "from-env"})[0] == \
                "Chatting with flag (type /quit to exit)"

        def test_echo_conversation_and_quit():
            out = chat("hello\n\n   \nhow are you?\n/quit\nignored after quit\n", ["--model", "tiny"])
            assert out == ["Chatting with tiny (type /quit to exit)",
                           "assistant: echo: hello",
                           "assistant: echo: how are you?"], f"got {out!r}"

        def test_end_of_input_without_quit_exits_cleanly():
            out = chat("one\ntwo")
            assert out[-2:] == ["assistant: echo: one", "assistant: echo: two"], f"got {out!r}"

        def test_history_command_excludes_system():
            out = chat("/history\nhi\n/history\n", ["--system", "SECRET SYSTEM"])
            assert out[1] == "(empty)", f"got {out!r}"
            assert out[3:] == ["user: hi", "assistant: echo: hi"], f"got {out!r}"
            assert not any("SECRET SYSTEM" in line for line in out)

        def test_reset_and_unknown_command():
            out = chat("a\n/reset\n/history\n/frobnicate now\nb\n/history\n")
            assert out[1:] == ["assistant: echo: a", "(conversation reset)", "(empty)",
                               "unknown command: /frobnicate", "assistant: echo: b",
                               "user: b", "assistant: echo: b"], f"got {out!r}"

        def test_history_file_written_as_jsonl():
            chat("hi\nbye\n/quit\n", ["--history", "h.jsonl", "--system", "sys"])
            got = read_jsonl("h.jsonl")
            assert got == [{"role": "user", "content": "hi"},
                           {"role": "assistant", "content": "echo: hi"},
                           {"role": "user", "content": "bye"},
                           {"role": "assistant", "content": "echo: bye"}], f"got {got!r}"

        def test_history_file_is_resumed_and_appended():
            with open("resume.jsonl", "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"role": "user", "content": "old q"}) + "\n")
                fh.write(json.dumps({"role": "assistant", "content": "old a"}) + "\n")
            out = chat("/history\nnew\n", ["--history", "resume.jsonl", "--model", "m"])
            assert out[0] == "(loaded 2 messages from resume.jsonl)", f"got {out!r}"
            assert out[1] == "Chatting with m (type /quit to exit)"
            assert out[2:4] == ["user: old q", "assistant: old a"], f"got {out!r}"
            assert len(read_jsonl("resume.jsonl")) == 4, "new messages must be appended"

        def test_reset_empties_history_file():
            chat("hi\n/reset\nafter\n", ["--history", "r.jsonl"])
            got = read_jsonl("r.jsonl")
            assert got == [{"role": "user", "content": "after"},
                           {"role": "assistant", "content": "echo: after"}], f"got {got!r}"

        def test_unknown_provider_exits_with_status_2():
            result = run_script([], stdin="hi\n", env={"PYTRAINER_PROVIDER": "bogus"})
            assert result.returncode == 2, f"exit status {result.returncode}"
            assert "unknown provider" in result.stderr, f"stderr: {result.stderr!r}"
            assert result.stdout == "", f"nothing should go to stdout, got {result.stdout!r}"
    ''',
}
