"""Chapter projects for the llm-apps module: llm-basics, prompts, structured-output, tool-calling."""

MINIS = [
    # ------------------------------------------------------------------ llm-basics
    {
        "id": "mini-llm-basics",
        "chapter": "llm-basics",
        "title": "Penny-Pincher Router",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Real AI products rarely talk to just one model. They try the **cheap** model first,
            fall back to another provider when one is rate limited or down, and keep a close eye
            on what every call costs. You'll build that router: one `ask()` that speaks both the
            OpenAI and the Anthropic dialect, bills each call to the cent (including prompt
            caching discounts), and never gives up while there is still a provider to try.

            ## What to build

            A file `app.py` with two functions.

            **`ask(providers, prompt, system=None, max_tokens=256)`**

            - `providers`: a `list` of provider dicts, **in the order to try them**, e.g.
              ```python
              {"name": "cheap", "api": "openai", "model": "gpt-4o-mini",
               "client": fake_openai, "input_price": 0.15, "output_price": 0.60}
              ```
              - `api` is `"openai"` or `"anthropic"` (which request/response shape to use)
              - `client` is a function you call with **keyword arguments only**; it returns a
                response dict or raises an exception
              - `input_price` / `output_price` are `float` dollars **per million tokens**
            - `prompt`: a `str`, the user's question
            - `system`: a `str` system prompt, or `None` for no system prompt
            - `max_tokens`: an `int`, passed through to the client
            - **Returns:** a `dict` with exactly these keys:
              `{"provider": str, "model": str, "text": str, "input_tokens": int,
              "output_tokens": int, "cached_tokens": int, "cost": float, "truncated": bool,
              "attempts": int}`

            **`spend_by_provider(results)`**

            - `results`: a `list` of dicts returned by `ask`
            - **Returns:** a `dict` provider name -> total `cost` of that provider's results,
              each total rounded to 6 decimal places; names appear in the order they are first
              seen; `{}` for an empty list

            ## Rules

            **Calling a provider**
            - `"openai"`: call `client(model=..., messages=..., max_tokens=...)`. `messages` is
              `[{"role": "system", "content": system}, {"role": "user", "content": prompt}]`,
              or just the user message when `system` is `None`.
            - `"anthropic"`: call `client(model=..., messages=..., max_tokens=...)` plus
              `system=system` **only when `system` is not `None`** (never send `system=None`).
              `messages` is only `[{"role": "user", "content": prompt}]`.

            **Reading the response**
            - OpenAI: `text` is the first choice's `message` `content` (`None` becomes `""`);
              `truncated` is `True` when its `finish_reason` is `"length"`;
              `input_tokens` = `usage["prompt_tokens"]`, `output_tokens` = `usage["completion_tokens"]`.
            - Anthropic: `text` is the `"text"` of every block with `"type": "text"`, joined with
              nothing in between (other block types are skipped); `truncated` is `True` when
              `stop_reason` is `"max_tokens"`; `input_tokens` = `usage["input_tokens"]`,
              `output_tokens` = `usage["output_tokens"]`.
            - `provider` and `model` come from the provider dict that answered.

            **Prompt caching and cost** (the cache counters may be missing - treat missing as `0`)
            - OpenAI: `cached_tokens` = the cached-token count from OpenAI's usage block. Those
              tokens are **already included** in `prompt_tokens`: bill them at **50%** of the
              input price and the remaining `prompt_tokens - cached_tokens` at the full input price.
            - Anthropic: the usage block has two separate cache counters (not included in
              `input_tokens`): tokens **read** from the cache cost **10%** of the input price and
              tokens **written** to the cache cost **125%** of the input price.
              `cached_tokens` = the cache **read** count.
            - Output tokens always cost `output_tokens * output_price / 1_000_000`.
            - `cost` is the total in dollars, rounded to 6 decimal places.

            **Falling back**
            - If a client raises an exception with a `status_code` attribute of `429` or
              `500`-`599`, move on to the next provider.
            - Any other exception (other status codes, or no `status_code` at all) is re-raised
              unchanged, immediately - no more providers are tried.
            - `attempts` = how many providers were called, including the one that answered.
            - If every provider failed, raise `RuntimeError` with the message
              `"all providers failed: "` + the failures as `name=status_code` joined with `", "`,
              e.g. `"all providers failed: cheap=429, backup=503"`, chained from the last
              provider's exception (so its `__cause__` is that exception).
            - An empty `providers` list raises `ValueError("no providers given")`.
            - Each provider is called at most once per `ask` (no retries on the same provider).

            ## Examples

            ```python
            def fake_openai(**kwargs):
                return {"choices": [{"message": {"role": "assistant", "content": "Paris."},
                                     "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 1000, "completion_tokens": 500}}

            cheap = {"name": "cheap", "api": "openai", "model": "gpt-4o-mini",
                     "client": fake_openai, "input_price": 3.0, "output_price": 15.0}
            ask([cheap], "Capital of France?")
            # returns {"provider": "cheap", "model": "gpt-4o-mini", "text": "Paris.",
            #          "input_tokens": 1000, "output_tokens": 500, "cached_tokens": 0,
            #          "cost": 0.0105, "truncated": False, "attempts": 1}

            # If cheap's client raised an error with status_code 429 and a second provider
            # answered, the result would come from the second one with "attempts": 2.

            spend_by_provider([{"provider": "cheap", "cost": 0.0105},
                               {"provider": "big", "cost": 0.2},
                               {"provider": "cheap", "cost": 0.0005}])
            # returns {"cheap": 0.011, "big": 0.2}
            ```

            Anthropic caching example: `input_tokens` 200, cache reads 10000, cache writes 0,
            `output_tokens` 100, prices 3.0 / 15.0 ->
            `(200*3 + 10000*3*0.10 + 100*15) / 1_000_000` = `0.0051`, `cached_tokens` = `10000`.

            ## You'll need to find out

            - Where each provider reports **cached input tokens** in the `usage` block of a
              response: the key path in OpenAI's Chat Completions response, and the names of the
              two cache counters in Anthropic's Messages response (look at each provider's API
              reference or prompt-caching guide).

            ## Try it yourself

            Put a couple of fake clients at the bottom of `app.py` under
            `if __name__ == "__main__":` (one that raises an exception with `status_code = 429`,
            one that answers), call `ask` with both, and print the result. Then try a fake that
            raises a `401` and check it is *not* swallowed.
        ''',
        "explore": r'''
            - Skip a provider automatically when the estimated cost of the prompt (4 characters
              per token) would exceed a per-call budget.
            - Add a "retry the same provider once with exponential backoff" option before falling back.
            - Turn it into a class that remembers which provider failed recently and skips it for
              the next N calls (a tiny *circuit breaker*).
        ''',
        "rubric": [
            "Request building and response reading are split into small helpers per provider shape",
            "Only temporary errors (429/5xx) trigger fallback; everything else surfaces unchanged",
            "Cost math is written once, clearly, with per-million prices and caching multipliers",
            "No global state; the caller's inputs are not modified",
        ],
        "starter_files": {"app.py": r'''
            # Penny-Pincher Router: a cost-aware, multi-provider ask().


            def ask(providers, prompt, system=None, max_tokens=256):
                ...


            def spend_by_provider(results):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Penny-Pincher Router: a cost-aware, multi-provider ask().


            def _is_temporary(exc):
                code = getattr(exc, "status_code", None)
                return code == 429 or (isinstance(code, int) and 500 <= code <= 599)


            def _call(provider, prompt, system, max_tokens):
                client = provider["client"]
                if provider["api"] == "openai":
                    messages = []
                    if system is not None:
                        messages.append({"role": "system", "content": system})
                    messages.append({"role": "user", "content": prompt})
                    return client(model=provider["model"], messages=messages, max_tokens=max_tokens)
                kwargs = {"model": provider["model"],
                          "messages": [{"role": "user", "content": prompt}],
                          "max_tokens": max_tokens}
                if system is not None:
                    kwargs["system"] = system
                return client(**kwargs)


            def _read_openai(response, provider):
                choice = response["choices"][0]
                usage = response.get("usage") or {}
                details = usage.get("prompt_tokens_details") or {}
                inp = usage.get("prompt_tokens", 0)
                out = usage.get("completion_tokens", 0)
                cached = details.get("cached_tokens", 0) or 0
                price_in = provider["input_price"]
                cost = ((inp - cached) * price_in + cached * price_in * 0.5
                        + out * provider["output_price"]) / 1_000_000
                text = choice["message"].get("content") or ""
                return text, choice.get("finish_reason") == "length", inp, out, cached, cost


            def _read_anthropic(response, provider):
                usage = response.get("usage") or {}
                inp = usage.get("input_tokens", 0)
                out = usage.get("output_tokens", 0)
                reads = usage.get("cache_read_input_tokens", 0) or 0
                writes = usage.get("cache_creation_input_tokens", 0) or 0
                price_in = provider["input_price"]
                cost = (inp * price_in + reads * price_in * 0.10 + writes * price_in * 1.25
                        + out * provider["output_price"]) / 1_000_000
                text = "".join(b["text"] for b in response["content"] if b.get("type") == "text")
                return text, response.get("stop_reason") == "max_tokens", inp, out, reads, cost


            def ask(providers, prompt, system=None, max_tokens=256):
                if not providers:
                    raise ValueError("no providers given")
                failures = []
                last_error = None
                for provider in providers:
                    try:
                        response = _call(provider, prompt, system, max_tokens)
                    except Exception as exc:
                        if not _is_temporary(exc):
                            raise
                        failures.append(f"{provider['name']}={exc.status_code}")
                        last_error = exc
                        continue
                    reader = _read_openai if provider["api"] == "openai" else _read_anthropic
                    text, truncated, inp, out, cached, cost = reader(response, provider)
                    return {"provider": provider["name"], "model": provider["model"], "text": text,
                            "input_tokens": inp, "output_tokens": out, "cached_tokens": cached,
                            "cost": round(cost, 6), "truncated": truncated,
                            "attempts": len(failures) + 1}
                raise RuntimeError("all providers failed: " + ", ".join(failures)) from last_error


            def spend_by_provider(results):
                totals = {}
                for result in results:
                    name = result["provider"]
                    totals[name] = totals.get(name, 0) + result["cost"]
                return {name: round(total, 6) for name, total in totals.items()}
        '''},
        "tests": r'''
            from app import ask, spend_by_provider


            class ApiError(Exception):
                def __init__(self, status_code):
                    super().__init__(f"HTTP {status_code}")
                    self.status_code = status_code


            class FakeClient:
                def __init__(self, outcome):
                    self.outcome = outcome
                    self.calls = []

                def __call__(self, **kwargs):
                    self.calls.append(kwargs)
                    if isinstance(self.outcome, BaseException):
                        raise self.outcome
                    return self.outcome


            def openai_reply(text="Hi", prompt_tokens=10, completion_tokens=5, finish="stop", cached=None):
                usage = {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                         "total_tokens": prompt_tokens + completion_tokens}
                if cached is not None:
                    usage["prompt_tokens_details"] = {"cached_tokens": cached}
                return {"id": "chatcmpl-1", "object": "chat.completion",
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                     "finish_reason": finish}],
                        "usage": usage}


            def anthropic_reply(blocks, input_tokens=10, output_tokens=5, stop="end_turn", **cache):
                usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
                usage.update(cache)
                return {"id": "msg_1", "type": "message", "role": "assistant", "content": blocks,
                        "stop_reason": stop, "usage": usage}


            def provider(name, api, client, model="m-1", input_price=1.0, output_price=2.0):
                return {"name": name, "api": api, "model": model, "client": client,
                        "input_price": input_price, "output_price": output_price}


            def close(a, b):
                return abs(a - b) < 1e-9


            def test_openai_answer_is_returned_with_usage_and_cost():
                client = FakeClient(openai_reply("Paris.", 1000, 500))
                result = ask([provider("cheap", "openai", client, "gpt-4o-mini", 3.0, 15.0)], "Capital?")
                assert result == {"provider": "cheap", "model": "gpt-4o-mini", "text": "Paris.",
                                  "input_tokens": 1000, "output_tokens": 500, "cached_tokens": 0,
                                  "cost": 0.0105, "truncated": False, "attempts": 1}, result


            def test_openai_request_sends_system_then_user_message():
                client = FakeClient(openai_reply())
                ask([provider("a", "openai", client, "gpt-4o-mini")], "Hi", system="Be brief.", max_tokens=50)
                assert client.calls == [{"model": "gpt-4o-mini",
                                         "messages": [{"role": "system", "content": "Be brief."},
                                                      {"role": "user", "content": "Hi"}],
                                         "max_tokens": 50}], client.calls


            def test_openai_without_system_sends_only_the_user_message():
                client = FakeClient(openai_reply())
                ask([provider("a", "openai", client)], "Hi")
                assert client.calls[0]["messages"] == [{"role": "user", "content": "Hi"}]
                assert client.calls[0]["max_tokens"] == 256


            def test_anthropic_gets_system_as_a_separate_argument():
                client = FakeClient(anthropic_reply([{"type": "text", "text": "Hey"}]))
                ask([provider("claude", "anthropic", client, "claude-haiku")], "Hi", system="Be brief.", max_tokens=99)
                assert client.calls == [{"model": "claude-haiku", "system": "Be brief.",
                                         "messages": [{"role": "user", "content": "Hi"}],
                                         "max_tokens": 99}], client.calls


            def test_anthropic_without_system_does_not_send_a_system_argument():
                client = FakeClient(anthropic_reply([{"type": "text", "text": "Hey"}]))
                ask([provider("claude", "anthropic", client)], "Hi")
                assert "system" not in client.calls[0], "don't pass system=None to Anthropic"


            def test_anthropic_text_blocks_are_joined_and_other_blocks_skipped():
                blocks = [{"type": "text", "text": "Hello"},
                          {"type": "tool_use", "id": "toolu_1", "name": "x", "input": {}},
                          {"type": "text", "text": " world"}]
                client = FakeClient(anthropic_reply(blocks, 40, 8))
                result = ask([provider("claude", "anthropic", client, "claude-haiku", 1.0, 5.0)], "Hi")
                assert result["text"] == "Hello world"
                assert (result["input_tokens"], result["output_tokens"]) == (40, 8)
                assert close(result["cost"], 0.00008), result["cost"]


            def test_openai_cached_tokens_are_billed_at_half_price():
                client = FakeClient(openai_reply("ok", prompt_tokens=10000, completion_tokens=100, cached=8000))
                result = ask([provider("a", "openai", client, "gpt-4o", 2.0, 8.0)], "Hi")
                assert result["cached_tokens"] == 8000
                # 2000 * 2.0 + 8000 * 1.0 + 100 * 8.0 = 12800 -> 0.0128
                assert close(result["cost"], 0.0128), result["cost"]


            def test_anthropic_cache_reads_and_writes_are_priced():
                reads = FakeClient(anthropic_reply([{"type": "text", "text": "ok"}], 200, 100,
                                                   cache_read_input_tokens=10000,
                                                   cache_creation_input_tokens=0))
                result = ask([provider("c", "anthropic", reads, "claude", 3.0, 15.0)], "Hi")
                assert result["cached_tokens"] == 10000
                assert close(result["cost"], 0.0051), result["cost"]
                writes = FakeClient(anthropic_reply([{"type": "text", "text": "ok"}], 200, 100,
                                                    cache_creation_input_tokens=2000))
                result = ask([provider("c", "anthropic", writes, "claude", 3.0, 15.0)], "Hi")
                assert result["cached_tokens"] == 0
                # 200*3 + 2000*3*1.25 + 100*15 = 9600 -> 0.0096
                assert close(result["cost"], 0.0096), result["cost"]


            def test_truncated_replies_are_flagged_for_both_providers():
                a = FakeClient(openai_reply("cut", finish="length"))
                b = FakeClient(anthropic_reply([{"type": "text", "text": "cut"}], stop="max_tokens"))
                c = FakeClient(openai_reply(None, finish="tool_calls"))
                assert ask([provider("a", "openai", a)], "x")["truncated"] is True
                assert ask([provider("b", "anthropic", b)], "x")["truncated"] is True
                result = ask([provider("c", "openai", c)], "x")
                assert result["truncated"] is False and result["text"] == ""


            def test_rate_limited_and_down_providers_fall_back_to_the_next():
                first = FakeClient(ApiError(429))
                second = FakeClient(ApiError(503))
                third = FakeClient(anthropic_reply([{"type": "text", "text": "Backup here"}]))
                result = ask([provider("cheap", "openai", first), provider("mid", "openai", second),
                              provider("big", "anthropic", third, "claude-big")], "Hi")
                assert result["provider"] == "big" and result["model"] == "claude-big"
                assert result["text"] == "Backup here"
                assert result["attempts"] == 3
                assert len(first.calls) == 1 and len(second.calls) == 1, "call each provider once"


            def test_other_errors_are_reraised_without_trying_other_providers():
                err = ApiError(401)
                first = FakeClient(err)
                second = FakeClient(openai_reply())
                try:
                    ask([provider("a", "openai", first), provider("b", "openai", second)], "Hi")
                except ApiError as caught:
                    assert caught is err, "re-raise the same exception object"
                else:
                    raise AssertionError("a 401 must be raised, not swallowed")
                assert second.calls == [], "don't fall back on a 401"
                boom = FakeClient(KeyError("no status code"))
                try:
                    ask([provider("a", "openai", boom), provider("b", "openai", second)], "Hi")
                except KeyError:
                    pass
                else:
                    raise AssertionError("exceptions without status_code must be re-raised")


            def test_all_providers_failing_raises_runtime_error_chained_to_last():
                last = ApiError(503)
                try:
                    ask([provider("cheap", "openai", FakeClient(ApiError(429))),
                         provider("backup", "anthropic", FakeClient(last))], "Hi")
                except RuntimeError as err:
                    assert str(err) == "all providers failed: cheap=429, backup=503", str(err)
                    assert err.__cause__ is last, "chain it from the last provider's exception"
                else:
                    raise AssertionError("expected RuntimeError")


            def test_empty_provider_list_raises_value_error():
                try:
                    ask([], "Hi")
                except ValueError as err:
                    assert str(err) == "no providers given", str(err)
                else:
                    raise AssertionError("expected ValueError")


            def test_spend_by_provider_totals_in_first_seen_order():
                results = [{"provider": "cheap", "cost": 0.0105}, {"provider": "big", "cost": 0.2},
                           {"provider": "cheap", "cost": 0.0005}]
                totals = spend_by_provider(results)
                assert totals == {"cheap": 0.011, "big": 0.2}, totals
                assert list(totals) == ["cheap", "big"]
                assert spend_by_provider([]) == {}
        ''',
    },
    # ------------------------------------------------------------------ prompts
    {
        "id": "mini-prompts",
        "chapter": "prompts",
        "title": "Prompt Shelf: versioned prompts",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Once a team ships an AI feature, prompts change every week - and "which prompt
            produced that weird answer?" becomes a real question. You'll build a small
            **prompt library**: every edit becomes a new numbered version, you can render any
            version with variables (safely wrapping untrusted input), check it fits a token
            budget, and see exactly what changed between two versions, `git diff` style.

            ## What to build

            A file `app.py` with a class `PromptLibrary` (no arguments to create it) and these
            methods:

            - `add(name, system, user)` -> `int`: store a new version of the prompt `name`
              (`system` and `user` are template strings with `{placeholders}`) and return its
              version number.
            - `versions(name)` -> `list[int]`: all version numbers of `name`, ascending.
            - `variables(name, version=None)` -> `list[str]`: the unique placeholder names used
              in that version's `system` **or** `user` template, sorted alphabetically.
            - `render(name, values, version=None, max_tokens=None)` -> `list[dict]`:
              `[{"role": "system", "content": ...}, {"role": "user", "content": ...}]` with both
              templates filled in from the dict `values`.
            - `diff(name, old, new)` -> `list[str]`: a unified diff between two versions.

            ## Rules

            **Versions**
            - The first `add` of a name returns `1`; each later `add` returns the previous
              highest version + 1.
            - If `system` **and** `user` are both identical to the latest version, don't create
              a new version: return the latest version number.
            - `version=None` means the latest (highest) version.
            - Unknown name (in any method): raise `ValueError("unknown prompt: <name>")`.
            - Known name but unknown version: raise `ValueError("unknown version <version> of <name>")`.

            **Variables & rendering**
            - A placeholder is `{` + one or more letters, digits or underscores + `}`, e.g. `{text}`.
              Templates never contain literal braces.
            - Every placeholder must have a value in `values`. Otherwise raise `ValueError` with
              `"missing variables: "` + **all** missing names, sorted, joined with `", "`, e.g.
              `"missing variables: n, text"`.
            - Extra keys in `values` are ignored. Values are converted with `str()`.
            - **Untrusted input:** a variable whose name ends with `_input` is wrapped in tags
              named after the variable, with every `<` in the value replaced by `&lt;`:
              `"<" + name + ">\n" + escaped value + "\n</" + name + ">"`.
            - Don't modify `values`.

            **Budget**
            - Estimated tokens of the rendered prompt = for each of the two messages,
              `(len(content) + 3) // 4 + 4`, summed.
            - If `max_tokens` is given and the estimate is **greater** than it, raise
              `ValueError("prompt too long: <estimate> tokens (limit <max_tokens>)")`.

            **Diff**
            - Compare the lines of `old` against `new`, where a version's lines are its `system`
              template's lines followed by its `user` template's lines (split on newlines).
            - Return the standard **unified diff** lines (3 lines of context, the default), with
              the file labels `"<name>@v<old>"` and `"<name>@v<new>"`, and **no** newline
              characters at the end of any line.
            - Two identical versions give `[]`.

            ## Examples

            ```python
            lib = PromptLibrary()
            lib.add("summarize", "You are a concise assistant.", "Summarize: {text}")   # returns 1
            lib.add("summarize", "You are a concise assistant.", "Summarize in {n} words: {text}")  # returns 2
            lib.add("summarize", "You are a concise assistant.", "Summarize in {n} words: {text}")  # returns 2 (no change)
            lib.versions("summarize")      # returns [1, 2]
            lib.variables("summarize")     # returns ["n", "text"]

            lib.render("summarize", {"n": 5, "text": "Long story..."})
            # returns [{"role": "system", "content": "You are a concise assistant."},
            #          {"role": "user", "content": "Summarize in 5 words: Long story..."}]
            lib.render("summarize", {"text": "x"})     # raises ValueError("missing variables: n")

            lib.add("qa", "Answer from the document only.", "{doc_input}\nQuestion: {question}")
            lib.render("qa", {"doc_input": "a<b", "question": "Why?"})[1]["content"]
            # returns "<doc_input>\na&lt;b\n</doc_input>\nQuestion: Why?"

            lib.render("summarize", {"n": 5, "text": "Long story..."}, max_tokens=10)
            # raises ValueError("prompt too long: 24 tokens (limit 10)")

            lib.diff("summarize", 1, 2)
            # returns ["--- summarize@v1", "+++ summarize@v2", "@@ -1,2 +1,2 @@",
            #          " You are a concise assistant.", "-Summarize: {text}",
            #          "+Summarize in {n} words: {text}"]
            ```

            ## You'll need to find out

            - The standard-library tool that compares two lists of lines and produces a
              **unified diff** (the `---` / `+++` / `@@` format you see in `git diff`) - and how
              to give it the two file labels and stop it adding a line ending to each line.

            ## Try it yourself

            At the bottom of `app.py`, under `if __name__ == "__main__":`, add two versions of a
            prompt, `print(lib.render(...))` and print each line of `lib.diff(...)`. Tweak a
            template and watch the diff change.
        ''',
        "explore": r'''
            - Save the whole library to a JSON file and load it back (careful: JSON object keys
              are always strings, so versions come back as `"1"`, not `1`).
            - Add `rollback(name, version)` that re-adds an old version as the newest one.
            - Support few-shot examples: `render(..., examples=[(input, output), ...])` inserting
              user/assistant pairs between the system and user messages.
        ''',
        "rubric": [
            "Version lookup and the unknown-name/unknown-version errors live in one helper",
            "Placeholder detection is done once (e.g. a regex), not duplicated per method",
            "Untrusted-input wrapping and escaping is clearly separated from ordinary values",
            "The caller's values dict is never mutated",
        ],
        "starter_files": {"app.py": r'''
            # Prompt Shelf: a versioned prompt library.


            class PromptLibrary:
                def __init__(self):
                    ...

                def add(self, name, system, user):
                    ...

                def versions(self, name):
                    ...

                def variables(self, name, version=None):
                    ...

                def render(self, name, values, version=None, max_tokens=None):
                    ...

                def diff(self, name, old, new):
                    ...
        '''},
        "solution_files": {"app.py": r'''
            # Prompt Shelf: a versioned prompt library.
            import difflib
            import re

            PLACEHOLDER = re.compile(r"\{(\w+)\}")


            def estimate_tokens(text):
                return (len(text) + 3) // 4


            class PromptLibrary:
                def __init__(self):
                    self._prompts = {}

                def add(self, name, system, user):
                    versions = self._prompts.setdefault(name, {})
                    if versions:
                        latest = max(versions)
                        if versions[latest] == (system, user):
                            return latest
                        number = latest + 1
                    else:
                        number = 1
                    versions[number] = (system, user)
                    return number

                def _versions_of(self, name):
                    if name not in self._prompts:
                        raise ValueError(f"unknown prompt: {name}")
                    return self._prompts[name]

                def _get(self, name, version):
                    versions = self._versions_of(name)
                    if version is None:
                        version = max(versions)
                    if version not in versions:
                        raise ValueError(f"unknown version {version} of {name}")
                    return versions[version]

                def versions(self, name):
                    return sorted(self._versions_of(name))

                def variables(self, name, version=None):
                    system, user = self._get(name, version)
                    return sorted(set(PLACEHOLDER.findall(system)) | set(PLACEHOLDER.findall(user)))

                def render(self, name, values, version=None, max_tokens=None):
                    system, user = self._get(name, version)
                    needed = self.variables(name, version)
                    missing = [var for var in needed if var not in values]
                    if missing:
                        raise ValueError("missing variables: " + ", ".join(missing))
                    filled = {}
                    for var in needed:
                        text = str(values[var])
                        if var.endswith("_input"):
                            text = f"<{var}>\n" + text.replace("<", "&lt;") + f"\n</{var}>"
                        filled[var] = text
                    messages = [{"role": "system", "content": system.format(**filled)},
                                {"role": "user", "content": user.format(**filled)}]
                    if max_tokens is not None:
                        total = sum(estimate_tokens(m["content"]) + 4 for m in messages)
                        if total > max_tokens:
                            raise ValueError(f"prompt too long: {total} tokens (limit {max_tokens})")
                    return messages

                def diff(self, name, old, new):
                    a_system, a_user = self._get(name, old)
                    b_system, b_user = self._get(name, new)
                    a = a_system.splitlines() + a_user.splitlines()
                    b = b_system.splitlines() + b_user.splitlines()
                    return list(difflib.unified_diff(a, b, fromfile=f"{name}@v{old}",
                                                     tofile=f"{name}@v{new}", lineterm=""))
        '''},
        "tests": r'''
            from app import PromptLibrary

            SYS = "You are a concise assistant."


            def make_lib():
                lib = PromptLibrary()
                lib.add("summarize", SYS, "Summarize: {text}")
                lib.add("summarize", SYS, "Summarize in {n} words: {text}")
                return lib


            def raises(fn, message):
                try:
                    fn()
                except ValueError as err:
                    assert str(err) == message, f"expected message {message!r}, got {str(err)!r}"
                else:
                    raise AssertionError(f"expected ValueError({message!r})")


            def test_versions_count_up_from_one():
                lib = PromptLibrary()
                assert lib.add("summarize", SYS, "Summarize: {text}") == 1
                assert lib.add("summarize", SYS, "Summarize in {n} words: {text}") == 2
                assert lib.add("other", "S", "U") == 1, "each name has its own version numbers"
                assert lib.versions("summarize") == [1, 2]


            def test_adding_an_identical_prompt_does_not_create_a_version():
                lib = make_lib()
                assert lib.add("summarize", SYS, "Summarize in {n} words: {text}") == 2
                assert lib.versions("summarize") == [1, 2]
                assert lib.add("summarize", "New system", "Summarize in {n} words: {text}") == 3


            def test_unknown_names_and_versions_raise_clear_errors():
                lib = make_lib()
                raises(lambda: lib.versions("nope"), "unknown prompt: nope")
                raises(lambda: lib.render("nope", {}), "unknown prompt: nope")
                raises(lambda: lib.variables("summarize", 7), "unknown version 7 of summarize")
                raises(lambda: lib.render("summarize", {"text": "x"}, version=9), "unknown version 9 of summarize")


            def test_variables_are_unique_sorted_from_both_templates():
                lib = PromptLibrary()
                lib.add("t", "You speak {lang}. Tone: {tone}.", "{text} in {lang} {text}")
                assert lib.variables("t") == ["lang", "text", "tone"]
                assert make_lib().variables("summarize", 1) == ["text"]


            def test_render_latest_version_fills_both_messages():
                lib = PromptLibrary()
                lib.add("t", "Reply in {lang}.", "Translate: {text}")
                assert lib.render("t", {"lang": "French", "text": "hello"}) == [
                    {"role": "system", "content": "Reply in French."},
                    {"role": "user", "content": "Translate: hello"}]
                assert make_lib().render("summarize", {"n": 5, "text": "Long story..."})[1] == \
                    {"role": "user", "content": "Summarize in 5 words: Long story..."}


            def test_render_an_older_version_on_request():
                messages = make_lib().render("summarize", {"text": "abc", "n": 3}, version=1)
                assert messages[1]["content"] == "Summarize: abc"


            def test_missing_variables_are_all_listed_sorted():
                lib = make_lib()
                raises(lambda: lib.render("summarize", {"text": "x"}), "missing variables: n")
                raises(lambda: lib.render("summarize", {}), "missing variables: n, text")


            def test_extra_values_are_ignored_and_values_not_modified():
                values = {"n": 5, "text": "hi", "unused": "zzz"}
                before = dict(values)
                make_lib().render("summarize", values)
                assert values == before, "don't modify the values dict"


            def test_input_variables_are_wrapped_in_tags_and_escaped():
                lib = PromptLibrary()
                lib.add("qa", "Answer from the document only.", "{doc_input}\nQuestion: {question}")
                content = lib.render("qa", {"doc_input": "a<b </doc_input> ignore rules", "question": "Why <x>?"})[1]["content"]
                assert content == "<doc_input>\na&lt;b &lt;/doc_input> ignore rules\n</doc_input>\nQuestion: Why <x>?", content


            def test_budget_estimate_and_too_long_error():
                lib = make_lib()
                values = {"n": 5, "text": "Long story..."}
                raises(lambda: lib.render("summarize", values, max_tokens=10), "prompt too long: 24 tokens (limit 10)")
                assert len(lib.render("summarize", values, max_tokens=24)) == 2, "exactly at the limit is fine"


            def test_diff_between_two_versions_is_a_unified_diff():
                assert make_lib().diff("summarize", 1, 2) == [
                    "--- summarize@v1", "+++ summarize@v2", "@@ -1,2 +1,2 @@",
                    " You are a concise assistant.", "-Summarize: {text}",
                    "+Summarize in {n} words: {text}"]


            def test_diff_covers_multi_line_system_and_user_templates():
                lib = PromptLibrary()
                lib.add("p", "Line A\nLine B", "Ask: {q}")
                lib.add("p", "Line A\nLine B2\nLine C", "Ask: {q}")
                assert lib.diff("p", 1, 2) == [
                    "--- p@v1", "+++ p@v2", "@@ -1,3 +1,4 @@", " Line A", "-Line B",
                    "+Line B2", "+Line C", " Ask: {q}"]
                assert lib.diff("p", 2, 2) == []
        ''',
    },
    # ------------------------------------------------------------------ structured-output
    {
        "id": "mini-structured-output",
        "chapter": "structured-output",
        "title": "Receipt Scanner",
        "estimated_hours": 1.25,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Expense apps let you snap a receipt and the fields fill themselves in. Behind the
            scenes: OCR text goes to a model, the model is asked for JSON, and your code refuses
            to trust it until it has checked every field. You'll build that pipeline - parse
            the reply, validate and clean the receipt (real dates only, totals that add up),
            and when the model gets it wrong, tell it exactly what to fix and try again.

            ## What to build

            A file `app.py` with:

            - a class `ExtractionError(Exception)` created as `ExtractionError(problems, attempts)`,
              storing both as attributes `.problems` (a `list` of strings) and `.attempts` (an `int`)
            - `parse_reply(text)` -> a tuple `(data, error)`
            - `validate_receipt(data)` -> a tuple `(receipt, problems)`
            - `extract_receipt(llm, receipt_text, max_attempts=3)` -> a clean receipt `dict`

            ## Rules

            **`parse_reply(text)`** - `text` is the model's reply (a `str`)
            - If the reply contains a Markdown code fence (three backticks, optionally followed
              by `json`), parse only the text inside the **first** fence.
            - Otherwise, if it contains a `{` and a later `}`, parse from the first `{` to the
              last `}` (both included). Otherwise parse the whole text.
            - Success: `(the dict, None)`.
            - Invalid JSON: `(None, "invalid JSON: " + the error's .msg)`, e.g.
              `"invalid JSON: Expecting value"`.
            - Valid JSON that is not an object: `(None, "expected a JSON object")`.

            **`validate_receipt(data)`** - `data` is a dict. Returns `(receipt, [])` when valid,
            or `(None, problems)` with **every** problem found, in this order:
            1. Missing required keys, in the order `merchant`, `date`, `total`, `items`:
               `"missing field: <key>"`. If any are missing, stop and return just these.
            2. `"merchant must be a non-empty string"` - unless it is a `str` that is not blank.
            3. `"date must be a real date in YYYY-MM-DD format"` - unless it is a `str` of exactly
               4 digits, `-`, 2 digits, `-`, 2 digits **and** a real calendar date
               (`"2026-02-30"` and `"2026-1-05"` are rejected; `"2024-02-29"` is fine).
            4. `"currency must be one of USD, EUR, GBP"` - `currency` is optional (missing or
               `null` means `"USD"`); a string is stripped and uppercased before checking.
            5. `"total must be a number"` - see *numbers* below.
            6. `"items must be a non-empty list"` - if `items` is not a list or is empty.
               Otherwise, for each item (numbered from 1) that is not a dict with a non-blank
               string `name` and a number `price`: `"item <n> needs a name and a numeric price"`.
            7. Only if there are no problems so far: if the item prices add up to more than
               `0.01` away from `total`: `"total <total> does not match items sum <sum>"`, both
               numbers with exactly 2 decimals, e.g. `"total 12.00 does not match items sum 11.50"`.

            *Numbers:* an `int` or `float` (but **not** a `bool`), or a string that `float()` can
            convert after stripping spaces (`" 3.50"` is fine, `"$3.50"` is not). Clean numbers
            are always `float`.

            The clean receipt is a new dict with exactly:
            `{"merchant": stripped str, "date": str, "currency": str, "items": [{"name": stripped str, "price": float}, ...], "total": float}`.
            Extra keys in `data` (or in items) are dropped. Don't modify `data`.

            **`extract_receipt(llm, receipt_text, max_attempts=3)`**
            - `llm` is a function called as `llm(messages)` with a list of message dicts; it
              returns the reply text.
            - The first call gets exactly two messages: a `system` message (your wording, but it
              must contain the word `JSON`), then a `user` message whose content is
              `"<receipt>\n" + receipt_text + "\n</receipt>"`.
            - Parse the reply with `parse_reply`, then validate with `validate_receipt`.
              If both succeed, return the clean receipt.
            - Otherwise the problems are `[the parse error]` or the validation problems. Append the
              model's reply as an `assistant` message, then a `user` message:
              `"Your reply had these problems:\n- <problem 1>\n- <problem 2>\nReply with only the corrected JSON object."`
              (one `- ` line per problem), and call `llm` again with the whole list.
            - Call `llm` at most `max_attempts` times. If no attempt succeeds, raise
              `ExtractionError(last problems, max_attempts)`.

            ## Examples

            ```python
            parse_reply('Sure!\n```json\n{"merchant": "Cafe"}\n```')   # returns ({"merchant": "Cafe"}, None)
            parse_reply("Sorry, I can't read that.")   # returns (None, "invalid JSON: Expecting value")
            parse_reply("[1, 2]")                      # returns (None, "expected a JSON object")

            validate_receipt({"merchant": " Blue Cafe ", "date": "2026-03-14", "total": "7.50",
                              "items": [{"name": "Latte", "price": 4.5}, {"name": "Bagel", "price": "3"}]})
            # returns ({"merchant": "Blue Cafe", "date": "2026-03-14", "currency": "USD",
            #           "items": [{"name": "Latte", "price": 4.5}, {"name": "Bagel", "price": 3.0}],
            #           "total": 7.5}, [])

            validate_receipt({"merchant": "", "date": "2026-02-30", "total": 1, "items": []})
            # returns (None, ["merchant must be a non-empty string",
            #                 "date must be a real date in YYYY-MM-DD format",
            #                 "items must be a non-empty list"])
            ```

            ## You'll need to find out

            - How to check, with the standard library, whether a string like `"2026-02-30"` is a
              **real calendar date** (turn it into a date object and see whether that fails).
              Careful: some ways of doing this also accept other formats, so check the exact
              `YYYY-MM-DD` shape yourself too.

            ## Try it yourself

            Write a fake model at the bottom of `app.py` that returns a bad reply first and a
            good one second:

            ```python
            if __name__ == "__main__":
                replies = iter(["Here you go: {\"merchant\": \"Cafe\"}",
                                '{"merchant": "Cafe", "date": "2026-03-14", "total": 4.5, "items": [{"name": "Tea", "price": 4.5}]}'])
                print(extract_receipt(lambda messages: next(replies), "CAFE ... TEA 4.50"))
            ```
        ''',
        "explore": r'''
            - Read about your provider's native structured outputs / JSON mode and JSON Schema,
              and write the receipt schema as real JSON Schema.
            - Accept dates like `"14/03/2026"` and normalise them instead of rejecting them.
            - Add a `tax` field and check `sum(items) + tax == total`.
        ''',
        "rubric": [
            "Parsing, validation and the retry loop are separate functions with clear jobs",
            "Number handling (bool exclusion, string coercion) is written once and reused",
            "The retry loop is bounded and the feedback message tells the model exactly what to fix",
            "Inputs (data, messages) are never mutated in surprising ways",
        ],
        "starter_files": {"app.py": r'''
            # Receipt Scanner: model reply -> validated receipt data.


            class ExtractionError(Exception):
                ...


            def parse_reply(text):
                ...


            def validate_receipt(data):
                ...


            def extract_receipt(llm, receipt_text, max_attempts=3):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Receipt Scanner: model reply -> validated receipt data.
            import json
            import re
            from datetime import date

            CURRENCIES = ["USD", "EUR", "GBP"]
            SYSTEM_PROMPT = ("You extract data from receipts. Reply with only a JSON object with the "
                             "keys: merchant, date (YYYY-MM-DD), currency, items (name, price), total.")


            class ExtractionError(Exception):
                def __init__(self, problems, attempts):
                    super().__init__(f"could not extract the receipt after {attempts} attempts")
                    self.problems = problems
                    self.attempts = attempts


            def parse_reply(text):
                fence = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
                if fence:
                    candidate = fence.group(1)
                else:
                    start, end = text.find("{"), text.rfind("}")
                    candidate = text[start:end + 1] if start != -1 and end > start else text
                try:
                    data = json.loads(candidate)
                except json.JSONDecodeError as err:
                    return None, f"invalid JSON: {err.msg}"
                if not isinstance(data, dict):
                    return None, "expected a JSON object"
                return data, None


            def to_number(value):
                if isinstance(value, bool):
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    try:
                        return float(value.strip())
                    except ValueError:
                        return None
                return None


            def is_real_date(value):
                if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    return False
                try:
                    date.fromisoformat(value)
                except ValueError:
                    return False
                return True


            def validate_receipt(data):
                missing = [f"missing field: {key}" for key in ["merchant", "date", "total", "items"]
                           if key not in data]
                if missing:
                    return None, missing
                problems = []
                merchant = data["merchant"]
                if not isinstance(merchant, str) or not merchant.strip():
                    problems.append("merchant must be a non-empty string")
                if not is_real_date(data["date"]):
                    problems.append("date must be a real date in YYYY-MM-DD format")
                currency = data.get("currency")
                if currency is None:
                    currency = "USD"
                elif isinstance(currency, str):
                    currency = currency.strip().upper()
                if currency not in CURRENCIES:
                    problems.append("currency must be one of USD, EUR, GBP")
                total = to_number(data["total"])
                if total is None:
                    problems.append("total must be a number")
                items = []
                if not isinstance(data["items"], list) or not data["items"]:
                    problems.append("items must be a non-empty list")
                else:
                    for n, item in enumerate(data["items"], 1):
                        name = item.get("name") if isinstance(item, dict) else None
                        price = to_number(item.get("price")) if isinstance(item, dict) else None
                        if not isinstance(name, str) or not name.strip() or price is None:
                            problems.append(f"item {n} needs a name and a numeric price")
                        else:
                            items.append({"name": name.strip(), "price": price})
                if not problems:
                    items_sum = sum(item["price"] for item in items)
                    if abs(items_sum - total) > 0.01:
                        problems.append(f"total {total:.2f} does not match items sum {items_sum:.2f}")
                if problems:
                    return None, problems
                return {"merchant": merchant.strip(), "date": data["date"], "currency": currency,
                        "items": items, "total": total}, []


            def extract_receipt(llm, receipt_text, max_attempts=3):
                messages = [{"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": "<receipt>\n" + receipt_text + "\n</receipt>"}]
                problems = []
                for _ in range(max_attempts):
                    reply = llm(messages)
                    data, error = parse_reply(reply)
                    if error:
                        problems = [error]
                    else:
                        receipt, problems = validate_receipt(data)
                        if receipt is not None:
                            return receipt
                    feedback = ("Your reply had these problems:\n"
                                + "\n".join("- " + p for p in problems)
                                + "\nReply with only the corrected JSON object.")
                    messages = messages + [{"role": "assistant", "content": reply},
                                           {"role": "user", "content": feedback}]
                raise ExtractionError(problems, max_attempts)
        '''},
        "tests": r'''
            import copy
            import json
            from app import ExtractionError, parse_reply, validate_receipt, extract_receipt

            GOOD = {"merchant": " Blue Cafe ", "date": "2026-03-14", "total": "7.50",
                    "items": [{"name": "Latte", "price": 4.5}, {"name": "Bagel", "price": "3"}]}
            CLEAN = {"merchant": "Blue Cafe", "date": "2026-03-14", "currency": "USD",
                     "items": [{"name": "Latte", "price": 4.5}, {"name": "Bagel", "price": 3.0}],
                     "total": 7.5}


            class FakeLLM:
                def __init__(self, replies):
                    self.replies = list(replies)
                    self.seen = []

                def __call__(self, messages):
                    self.seen.append(copy.deepcopy(messages))
                    return self.replies.pop(0)


            def receipt(**changes):
                data = copy.deepcopy(GOOD)
                data.update(changes)
                return data


            def test_parse_reply_reads_plain_json():
                assert parse_reply('{"merchant": "Cafe", "ok": true}') == ({"merchant": "Cafe", "ok": True}, None)


            def test_parse_reply_uses_only_the_first_code_fence():
                text = 'Sure! {not this}\n```json\n{"merchant": "Cafe"}\n```\nand ```{"x": 1}```'
                assert parse_reply(text) == ({"merchant": "Cafe"}, None)
                assert parse_reply('```\n{"a": 1}\n```') == ({"a": 1}, None)


            def test_parse_reply_finds_json_inside_prose():
                assert parse_reply('Here it is: {"a": {"b": 2}} Hope that helps!') == ({"a": {"b": 2}}, None)


            def test_parse_reply_reports_invalid_json_and_non_objects():
                assert parse_reply("Sorry, I can't read that.") == (None, "invalid JSON: Expecting value")
                data, error = parse_reply('{"a": 1,}')
                assert data is None and error.startswith("invalid JSON: "), error
                assert parse_reply("[1, 2]") == (None, "expected a JSON object")


            def test_valid_receipt_is_cleaned_with_defaults_and_numbers():
                data = receipt(extra="dropped")
                before = copy.deepcopy(data)
                assert validate_receipt(data) == (CLEAN, [])
                assert data == before, "don't modify data"
                result, _ = validate_receipt(receipt(total=7.5, currency=None))
                assert result["currency"] == "USD" and isinstance(result["total"], float)


            def test_missing_fields_are_reported_in_order_and_stop_there():
                assert validate_receipt({"date": "nope", "merchant": ""}) == (
                    None, ["missing field: total", "missing field: items"])
                assert validate_receipt({}) == (None, ["missing field: merchant", "missing field: date",
                                                        "missing field: total", "missing field: items"])


            def test_dates_must_be_real_and_exactly_yyyy_mm_dd():
                msg = "date must be a real date in YYYY-MM-DD format"
                for bad in ["2026-02-30", "2026-1-05", "14/03/2026", "20260314", 20260314, "2026-13-01"]:
                    assert validate_receipt(receipt(date=bad)) == (None, [msg]), bad
                result, problems = validate_receipt(receipt(date="2024-02-29"))
                assert problems == [] and result["date"] == "2024-02-29"


            def test_currency_is_normalised_then_checked():
                result, _ = validate_receipt(receipt(currency=" eur "))
                assert result["currency"] == "EUR"
                assert validate_receipt(receipt(currency="bitcoin")) == (None, ["currency must be one of USD, EUR, GBP"])


            def test_bad_numbers_and_items_are_all_reported():
                data = receipt(merchant="  ", total=True,
                               items=[{"name": "Tea", "price": "$3"}, {"price": 2}, "x", {"name": "Ok", "price": " 1.5"}])
                assert validate_receipt(data) == (None, [
                    "merchant must be a non-empty string", "total must be a number",
                    "item 1 needs a name and a numeric price", "item 2 needs a name and a numeric price",
                    "item 3 needs a name and a numeric price"])
                assert validate_receipt(receipt(items={"name": "Tea"})) == (None, ["items must be a non-empty list"])
                assert validate_receipt(receipt(items=[{"name": "Tea", "price": False}])) == (
                    None, ["item 1 needs a name and a numeric price"])


            def test_total_must_match_the_items():
                assert validate_receipt(receipt(total=12)) == (None, ["total 12.00 does not match items sum 7.50"])
                result, problems = validate_receipt(receipt(total=7.505))
                assert problems == [], "within 0.01 is fine"


            def test_extract_succeeds_first_try_with_system_and_wrapped_receipt():
                llm = FakeLLM(["```json\n" + json.dumps(GOOD) + "\n```"])
                assert extract_receipt(llm, "BLUE CAFE\nLATTE 4.50") == CLEAN
                assert len(llm.seen) == 1
                first = llm.seen[0]
                assert [m["role"] for m in first] == ["system", "user"], first
                assert "JSON" in first[0]["content"]
                assert first[1]["content"] == "<receipt>\nBLUE CAFE\nLATTE 4.50\n</receipt>"


            def test_extract_retries_with_the_problems_as_feedback():
                bad = json.dumps(receipt(date="2026-02-30", total=12))
                llm = FakeLLM(["Sorry, no idea", bad, json.dumps(GOOD)])
                assert extract_receipt(llm, "r") == CLEAN
                assert len(llm.seen) == 3
                second = llm.seen[1]
                assert len(second) == 4
                assert second[2] == {"role": "assistant", "content": "Sorry, no idea"}
                assert second[3] == {"role": "user", "content": "Your reply had these problems:\n"
                                     "- invalid JSON: Expecting value\nReply with only the corrected JSON object."}
                third = llm.seen[2]
                assert len(third) == 6 and third[4] == {"role": "assistant", "content": bad}
                assert third[5]["content"] == ("Your reply had these problems:\n"
                                               "- date must be a real date in YYYY-MM-DD format\n"
                                               "Reply with only the corrected JSON object.")


            def test_extract_gives_up_after_max_attempts():
                llm = FakeLLM(["nope", "[1]", json.dumps({"merchant": "x"}), json.dumps(GOOD)])
                try:
                    extract_receipt(llm, "r", max_attempts=3)
                except ExtractionError as err:
                    assert err.attempts == 3
                    assert err.problems == ["missing field: date", "missing field: total", "missing field: items"]
                else:
                    raise AssertionError("expected ExtractionError")
                assert len(llm.seen) == 3, "never call the model more than max_attempts times"
        ''',
    },
    # ------------------------------------------------------------------ tool-calling
    {
        "id": "mini-tool-calling",
        "chapter": "tool-calling",
        "title": "Pocket Assistant: calculator and unit converter",
        "estimated_hours": 1.25,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Language models are famously bad at arithmetic and unit conversions - so good
            assistants don't let them guess, they hand them **tools**. You'll build a tiny
            assistant with two real tools (a calculator and a unit converter), describe them so
            a model can use them, check every call the model makes, and run the full
            request -> tool -> answer loop against a (fake) Anthropic-style model.

            ## What to build

            A file `app.py` with:

            - `TOOLS`: a list of two Anthropic-style tool definitions (`name`, `description`,
              `input_schema`), `calculate` first, then `convert_units`
            - `calculate(a, op, b)` -> the result (number)
            - `convert_units(value, from_unit, to_unit)` -> a `float`
            - `check_args(name, args)` -> a list of problem strings
            - `run_tool(name, args)` -> a tuple `(content, is_error)`
            - `run_assistant(model, question, max_rounds=5)` -> a `dict`

            ## Rules

            **`TOOLS`**
            - `calculate`: properties `a` (`"number"`), `op` (`"string"` with
              `"enum": ["+", "-", "*", "/"]`), `b` (`"number"`); `required` is `["a", "op", "b"]`.
            - `convert_units`: properties `value` (`"number"`), `from_unit` and `to_unit`
              (`"string"`); `required` is `["value", "from_unit", "to_unit"]`.
            - Every tool and every property has a non-empty `description`; each
              `input_schema` has `"type": "object"`.

            **`calculate(a, op, b)`**
            - `op` is `"+"`, `"-"`, `"*"` or `"/"`. Return the result rounded to 6 decimal places
              (use `round`, so `2 + 3` stays `5`).
            - Dividing by zero raises `ValueError("division by zero")`; any other `op` raises
              `ValueError("unknown operator: <op>")`.

            **`convert_units(value, from_unit, to_unit)`**
            - Units (case-insensitive): length `m`, `km`, `ft`, `mi`; mass `kg`, `g`, `lb`;
              temperature `c`, `f`.
            - Use the **exact** official definitions of the foot, mile and pound in metric
              units, and the exact Celsius/Fahrenheit formula. Return the result rounded to 4
              decimal places.
            - A unit that isn't in the list raises `ValueError("unknown unit: <unit as given>")`
              (check `from_unit` first).
            - Units of different kinds raise `ValueError("cannot convert <from_unit> to <to_unit>")`
              (as given).

            **`check_args(name, args)`** - checks against the matching tool's `input_schema` in `TOOLS`
            - Unknown tool name: return `["unknown tool: <name>"]`.
            - First, for each `required` name (in order) missing from `args`: `"missing: <name>"`.
            - Then for each key in `args` (in its order):
              - not a property: `"unknown: <key>"`
              - `"number"` property whose value isn't an `int`/`float` (a `bool` doesn't count):
                `"<key>: expected number"`
              - `"string"` property whose value isn't a `str`: `"<key>: expected string"`
              - property with an `enum` whose value isn't in it:
                `"<key>: expected one of <values joined with ', '>"`, e.g. `"op: expected one of +, -, *, /"`
            - All good: `[]`.

            **`run_tool(name, args)`**
            - If `check_args` finds problems: `("Error: " + problems joined with "; ", True)`.
            - Otherwise call the matching Python function with the arguments unpacked. If it raises,
              return `("Error: " + str(the exception), True)`.
            - On success return `(json.dumps(result), False)`, e.g. `("5", False)`.

            **`run_assistant(model, question, max_rounds=5)`**
            - `model` is called as `model(messages=messages, tools=TOOLS)` and returns an
              Anthropic-style reply: `{"stop_reason": ..., "content": [blocks]}`.
            - Start with `messages = [{"role": "user", "content": question}]`.
            - After every model call, append `{"role": "assistant", "content": reply["content"]}`.
            - If `stop_reason` is `"tool_use"`: run every `tool_use` block in order with `run_tool`,
              and append **one** `user` message whose content is a list of `tool_result` blocks, one per
              call, in order: `{"type": "tool_result", "tool_use_id": <block id>, "content": <content>}`,
              plus `"is_error": True` **only** for failed calls. Then call the model again.
            - Any other `stop_reason`: return
              `{"answer": <all text blocks joined with nothing between>, "messages": messages, "tool_log": log}`.
            - `tool_log` has one dict per tool call, in order:
              `{"tool": name, "input": args, "output": content, "is_error": bool}`.
            - If the model is still asking for tools after `max_rounds` calls, raise
              `RuntimeError("no final answer after <max_rounds> rounds")`.

            ## Examples

            ```python
            calculate(2, "+", 3)              # returns 5
            calculate(1, "/", 3)              # returns 0.333333
            convert_units(10, "mi", "km")     # returns 16.0934
            convert_units(100, "C", "F")      # returns 212.0
            convert_units(3, "kg", "km")      # raises ValueError("cannot convert kg to km")
            check_args("calculate", {"a": 2, "b": "3", "op": "%", "x": 1})
            # returns ["b: expected number", "op: expected one of +, -, *, /", "unknown: x"]
            run_tool("calculate", {"a": 1, "op": "/", "b": 0})   # returns ("Error: division by zero", True)
            ```

            A round trip: the model first replies
            `{"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "toolu_1", "name": "calculate", "input": {"a": 6, "op": "*", "b": 7}}]}`;
            you append that as an assistant message, then
            `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "42"}]}`;
            the model then replies `{"stop_reason": "end_turn", "content": [{"type": "text", "text": "It's 42."}]}`
            and `run_assistant` returns `{"answer": "It's 42.", "messages": [...4 messages...], "tool_log": [{"tool": "calculate", "input": {"a": 6, "op": "*", "b": 7}, "output": "42", "is_error": False}]}`.

            ## You'll need to find out

            - The exact internationally agreed lengths of a foot and a mile in metres, the exact
              mass of a pound in kilograms, and the formula between Celsius and Fahrenheit
              (the tests check 1 mile is exactly `5280.0` feet).

            ## Try it yourself

            Script a fake model with a list of replies and a function that returns the next one
            each call (it can also `print(messages)` so you can watch the conversation grow),
            then `print(run_assistant(fake, "How many km is 26.2 miles?"))`.
        ''',
        "explore": r'''
            - Add an OpenAI adapter: convert `TOOLS` to OpenAI's `{"type": "function", ...}` shape
              and handle `tool_calls` with JSON-string arguments.
            - Add a `today()` tool and a tool allow-list per user.
            - Cap total tool calls (not just rounds) and return a polite "I gave up" answer.
        ''',
        "rubric": [
            "Tool schemas and the name -> function registry are defined once and used for dispatch",
            "Arguments are validated before any tool function runs",
            "Tool errors become is_error results for the model instead of crashing the loop",
            "The loop is bounded and the message history follows the provider's shape exactly",
        ],
        "starter_files": {"app.py": r'''
            # Pocket Assistant: a calculator + unit converter the model can call.
            import json

            TOOLS = []


            def calculate(a, op, b):
                ...


            def convert_units(value, from_unit, to_unit):
                ...


            def check_args(name, args):
                ...


            def run_tool(name, args):
                ...


            def run_assistant(model, question, max_rounds=5):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Pocket Assistant: a calculator + unit converter the model can call.
            import json

            TOOLS = [
                {"name": "calculate",
                 "description": "Do one arithmetic operation on two numbers.",
                 "input_schema": {
                     "type": "object",
                     "properties": {
                         "a": {"type": "number", "description": "The first number"},
                         "op": {"type": "string", "enum": ["+", "-", "*", "/"],
                                "description": "The operator"},
                         "b": {"type": "number", "description": "The second number"},
                     },
                     "required": ["a", "op", "b"]}},
                {"name": "convert_units",
                 "description": "Convert a value between units of length, mass or temperature.",
                 "input_schema": {
                     "type": "object",
                     "properties": {
                         "value": {"type": "number", "description": "The amount to convert"},
                         "from_unit": {"type": "string", "description": "Unit to convert from, e.g. mi"},
                         "to_unit": {"type": "string", "description": "Unit to convert to, e.g. km"},
                     },
                     "required": ["value", "from_unit", "to_unit"]}},
            ]

            LENGTH = {"m": 1.0, "km": 1000.0, "ft": 0.3048, "mi": 1609.344}
            MASS = {"kg": 1.0, "g": 0.001, "lb": 0.45359237}
            TEMPERATURE = {"c", "f"}


            def calculate(a, op, b):
                if op == "+":
                    result = a + b
                elif op == "-":
                    result = a - b
                elif op == "*":
                    result = a * b
                elif op == "/":
                    if b == 0:
                        raise ValueError("division by zero")
                    result = a / b
                else:
                    raise ValueError(f"unknown operator: {op}")
                return round(result, 6)


            def convert_units(value, from_unit, to_unit):
                f, t = from_unit.lower(), to_unit.lower()
                for given, unit in ((from_unit, f), (to_unit, t)):
                    if unit not in LENGTH and unit not in MASS and unit not in TEMPERATURE:
                        raise ValueError(f"unknown unit: {given}")
                if f in LENGTH and t in LENGTH:
                    result = value * LENGTH[f] / LENGTH[t]
                elif f in MASS and t in MASS:
                    result = value * MASS[f] / MASS[t]
                elif f in TEMPERATURE and t in TEMPERATURE:
                    if f == t:
                        result = value
                    elif f == "c":
                        result = value * 9 / 5 + 32
                    else:
                        result = (value - 32) * 5 / 9
                else:
                    raise ValueError(f"cannot convert {from_unit} to {to_unit}")
                return round(float(result), 4)


            FUNCTIONS = {"calculate": calculate, "convert_units": convert_units}
            SCHEMAS = {tool["name"]: tool["input_schema"] for tool in TOOLS}


            def check_args(name, args):
                if name not in SCHEMAS:
                    return [f"unknown tool: {name}"]
                schema = SCHEMAS[name]
                problems = [f"missing: {key}" for key in schema["required"] if key not in args]
                for key, value in args.items():
                    prop = schema["properties"].get(key)
                    if prop is None:
                        problems.append(f"unknown: {key}")
                    elif prop["type"] == "number" and (isinstance(value, bool)
                                                       or not isinstance(value, (int, float))):
                        problems.append(f"{key}: expected number")
                    elif prop["type"] == "string" and not isinstance(value, str):
                        problems.append(f"{key}: expected string")
                    elif "enum" in prop and value not in prop["enum"]:
                        problems.append(f"{key}: expected one of " + ", ".join(prop["enum"]))
                return problems


            def run_tool(name, args):
                problems = check_args(name, args)
                if problems:
                    return "Error: " + "; ".join(problems), True
                try:
                    result = FUNCTIONS[name](**args)
                except Exception as exc:
                    return f"Error: {exc}", True
                return json.dumps(result), False


            def run_assistant(model, question, max_rounds=5):
                messages = [{"role": "user", "content": question}]
                log = []
                for _ in range(max_rounds):
                    reply = model(messages=messages, tools=TOOLS)
                    messages.append({"role": "assistant", "content": reply["content"]})
                    if reply["stop_reason"] != "tool_use":
                        answer = "".join(b["text"] for b in reply["content"] if b["type"] == "text")
                        return {"answer": answer, "messages": messages, "tool_log": log}
                    results = []
                    for block in reply["content"]:
                        if block["type"] != "tool_use":
                            continue
                        content, is_error = run_tool(block["name"], block["input"])
                        result = {"type": "tool_result", "tool_use_id": block["id"], "content": content}
                        if is_error:
                            result["is_error"] = True
                        results.append(result)
                        log.append({"tool": block["name"], "input": block["input"],
                                    "output": content, "is_error": is_error})
                    messages.append({"role": "user", "content": results})
                raise RuntimeError(f"no final answer after {max_rounds} rounds")
        '''},
        "tests": r'''
            import copy
            from app import TOOLS, calculate, convert_units, check_args, run_tool, run_assistant


            class FakeModel:
                def __init__(self, replies):
                    self.replies = list(replies)
                    self.calls = []

                def __call__(self, messages, tools):
                    self.calls.append({"messages": copy.deepcopy(messages), "tools": tools})
                    return self.replies.pop(0)


            def tool_use(*calls, text=None):
                blocks = [{"type": "text", "text": text}] if text else []
                for call_id, name, args in calls:
                    blocks.append({"type": "tool_use", "id": call_id, "name": name, "input": args})
                return {"stop_reason": "tool_use", "content": blocks}


            def final(text):
                return {"stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}


            def value_error(fn, message):
                try:
                    fn()
                except ValueError as err:
                    assert str(err) == message, f"expected {message!r}, got {str(err)!r}"
                else:
                    raise AssertionError(f"expected ValueError({message!r})")


            def test_tools_describe_calculate_and_convert_units():
                assert [t["name"] for t in TOOLS] == ["calculate", "convert_units"]
                calc, conv = TOOLS
                assert calc["input_schema"]["required"] == ["a", "op", "b"]
                assert conv["input_schema"]["required"] == ["value", "from_unit", "to_unit"]
                for tool in TOOLS:
                    assert tool["description"], "every tool needs a description"
                    assert tool["input_schema"]["type"] == "object"
                    for name, prop in tool["input_schema"]["properties"].items():
                        assert prop.get("description"), f"property {name} needs a description"


            def test_tool_properties_have_the_right_types_and_enum():
                calc, conv = TOOLS
                props = calc["input_schema"]["properties"]
                assert (props["a"]["type"], props["op"]["type"], props["b"]["type"]) == ("number", "string", "number")
                assert props["op"]["enum"] == ["+", "-", "*", "/"]
                props = conv["input_schema"]["properties"]
                assert set(props) == {"value", "from_unit", "to_unit"}
                assert (props["value"]["type"], props["from_unit"]["type"], props["to_unit"]["type"]) == ("number", "string", "string")


            def test_calculate_does_arithmetic_and_rounds():
                assert calculate(2, "+", 3) == 5 and isinstance(calculate(2, "+", 3), int)
                assert calculate(10, "-", 12.5) == -2.5
                assert calculate(6, "*", 7) == 42
                assert calculate(1, "/", 3) == 0.333333
                assert calculate(0.1, "+", 0.2) == 0.3


            def test_calculate_rejects_division_by_zero_and_unknown_operators():
                value_error(lambda: calculate(1, "/", 0), "division by zero")
                value_error(lambda: calculate(2, "%", 3), "unknown operator: %")


            def test_convert_lengths_with_exact_definitions():
                assert convert_units(10, "mi", "km") == 16.0934
                assert convert_units(1, "mi", "ft") == 5280.0
                assert convert_units(5, "ft", "m") == 1.524
                assert convert_units(2500, "m", "km") == 2.5


            def test_convert_mass_and_temperature_case_insensitively():
                assert convert_units(1, "kg", "lb") == 2.2046
                assert convert_units(1, "LB", "g") == 453.5924
                assert convert_units(100, "C", "F") == 212.0
                assert convert_units(98.6, "f", "c") == 37.0
                assert convert_units(-40, "c", "f") == -40.0
                assert isinstance(convert_units(3, "km", "km"), float)


            def test_convert_rejects_unknown_and_mismatched_units():
                value_error(lambda: convert_units(1, "parsec", "km"), "unknown unit: parsec")
                value_error(lambda: convert_units(1, "km", "Furlong"), "unknown unit: Furlong")
                value_error(lambda: convert_units(3, "kg", "km"), "cannot convert kg to km")
                value_error(lambda: convert_units(3, "C", "lb"), "cannot convert C to lb")


            def test_check_args_reports_every_problem_in_order():
                assert check_args("calculate", {"a": 2, "op": "+", "b": 3}) == []
                assert check_args("calculate", {"a": 2, "b": "3", "op": "%", "x": 1}) == [
                    "b: expected number", "op: expected one of +, -, *, /", "unknown: x"]
                assert check_args("convert_units", {"to_unit": 5, "value": True}) == [
                    "missing: from_unit", "to_unit: expected string", "value: expected number"]
                assert check_args("fly", {"to": "moon"}) == ["unknown tool: fly"]


            def test_run_tool_returns_json_text_or_error_results():
                assert run_tool("calculate", {"a": 6, "op": "*", "b": 7}) == ("42", False)
                assert run_tool("convert_units", {"value": 10, "from_unit": "mi", "to_unit": "km"}) == ("16.0934", False)
                assert run_tool("calculate", {"a": 1, "op": "/", "b": 0}) == ("Error: division by zero", True)
                assert run_tool("calculate", {"a": 1}) == ("Error: missing: op; missing: b", True)
                assert run_tool("fly", {}) == ("Error: unknown tool: fly", True)


            def test_assistant_answers_directly_without_tools():
                model = FakeModel([final("Hello!")])
                result = run_assistant(model, "Hi")
                assert result["answer"] == "Hello!"
                assert result["tool_log"] == []
                assert model.calls[0]["messages"] == [{"role": "user", "content": "Hi"}]
                assert model.calls[0]["tools"] is TOOLS or model.calls[0]["tools"] == TOOLS
                assert result["messages"] == [{"role": "user", "content": "Hi"},
                                              {"role": "assistant", "content": final("Hello!")["content"]}]


            def test_assistant_runs_a_tool_and_sends_the_result_back():
                first = tool_use(("toolu_1", "calculate", {"a": 6, "op": "*", "b": 7}), text="Let me compute.")
                model = FakeModel([first, final("It's 42.")])
                result = run_assistant(model, "What is 6 times 7?")
                assert result["answer"] == "It's 42."
                second_call = model.calls[1]["messages"]
                assert second_call == [
                    {"role": "user", "content": "What is 6 times 7?"},
                    {"role": "assistant", "content": first["content"]},
                    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "42"}]},
                ], second_call
                assert len(result["messages"]) == 4
                assert result["tool_log"] == [{"tool": "calculate", "input": {"a": 6, "op": "*", "b": 7},
                                               "output": "42", "is_error": False}]


            def test_two_tool_calls_in_one_reply_get_one_message_with_two_results():
                first = tool_use(("t1", "convert_units", {"value": 26.2, "from_unit": "mi", "to_unit": "km"}),
                                 ("t2", "calculate", {"a": 2, "op": "+", "b": 2}))
                model = FakeModel([first, final("Done")])
                run_assistant(model, "q")
                results = model.calls[1]["messages"][2]
                assert results["role"] == "user"
                assert [r["tool_use_id"] for r in results["content"]] == ["t1", "t2"]
                assert [r["content"] for r in results["content"]] == ["42.1648", "4"]
                assert all("is_error" not in r for r in results["content"]), "no is_error key on success"


            def test_tool_errors_go_back_to_the_model_with_is_error():
                first = tool_use(("t1", "calculate", {"a": 1, "op": "/", "b": 0}),
                                 ("t2", "teleport", {"to": "Mars"}))
                model = FakeModel([first, tool_use(("t3", "calculate", {"a": 1, "op": "+", "b": 1})), final("2")])
                result = run_assistant(model, "q")
                assert result["answer"] == "2"
                assert model.calls[1]["messages"][2]["content"] == [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "Error: division by zero", "is_error": True},
                    {"type": "tool_result", "tool_use_id": "t2", "content": "Error: unknown tool: teleport", "is_error": True}]
                assert [e["is_error"] for e in result["tool_log"]] == [True, True, False]
                assert len(result["messages"]) == 6


            def test_assistant_gives_up_after_max_rounds():
                loop = tool_use(("t", "calculate", {"a": 1, "op": "+", "b": 1}))
                model = FakeModel([loop] * 10)
                try:
                    run_assistant(model, "q", max_rounds=3)
                except RuntimeError as err:
                    assert str(err) == "no final answer after 3 rounds", str(err)
                else:
                    raise AssertionError("expected RuntimeError")
                assert len(model.calls) == 3, "call the model at most max_rounds times"
        ''',
    },
]
