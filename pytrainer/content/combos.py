"""Combination challenges: mini real-world tasks that mix several topics.

Each challenge is unlocked once every topic listed in ``topics`` is cleared.
"""

CHALLENGES = [
    {
        "id": "combo-1",
        "title": "Conversation stats",
        "difficulty": 2,
        "topics": ["lists", "dicts", "loops", "functions"],
        "prompt": r'''
            A chat transcript is a list of message dicts with `"role"` and `"content"` keys.
            Tool-call messages may have `"content": None`.

            Write `conversation_stats(messages)` returning a dict that maps each role to
            `{"count": <messages with that role>, "chars": <total characters of content>}`.
            `None` content counts as 0 characters. Roles appear in the order they first
            occur in the transcript.

            ```python
            conversation_stats([
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": None},
                {"role": "user", "content": "Thanks"},
            ])
            # {"system": {"count": 1, "chars": 9},
            #  "user": {"count": 2, "chars": 8},
            #  "assistant": {"count": 1, "chars": 0}}
            ```
        ''',
        "starter": r'''
            def conversation_stats(messages):
                ...
        ''',
        "tests": r'''
            from solution import conversation_stats

            MSGS = [
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": None},
                {"role": "user", "content": "Thanks"},
            ]

            def test_example():
                got = conversation_stats(MSGS)
                assert got == {"system": {"count": 1, "chars": 9},
                               "user": {"count": 2, "chars": 8},
                               "assistant": {"count": 1, "chars": 0}}, f"got {got!r}"

            def test_role_order_is_first_appearance():
                msgs = [{"role": "user", "content": "a"}, {"role": "tool", "content": "b"},
                        {"role": "user", "content": "c"}, {"role": "assistant", "content": "d"}]
                got = list(conversation_stats(msgs))
                assert got == ["user", "tool", "assistant"], f"role order was {got!r}"

            def test_empty_transcript():
                assert conversation_stats([]) == {}

            def test_input_not_modified():
                msgs = [dict(m) for m in MSGS]
                conversation_stats(msgs)
                assert msgs == MSGS, "the input messages were modified"
        ''',
        "solution": r'''
            def conversation_stats(messages):
                stats = {}
                for message in messages:
                    entry = stats.setdefault(message["role"], {"count": 0, "chars": 0})
                    entry["count"] += 1
                    entry["chars"] += len(message["content"] or "")
                return stats
        ''',
        "hints": [
            'You need a loop over the messages and a dict whose values are small dicts. Start with an empty result dict before the loop.',
            "Stage 1: for each message, find (or create) the entry for its role. Stage 2: add 1 to that entry's count and add the content length to its chars. Remember `None` content counts as 0. Dicts remember insertion order, so first-appearance order comes for free.",
            '1) Create an empty dict `stats`. 2) Loop over `messages`. 3) Read the message\'s role; if the role is not in `stats` yet, add it with `{"count": 0, "chars": 0}` (`.setdefault()` does this in one step). 4) Increase that entry\'s count by 1. 5) Take the content, turn `None` into an empty string (e.g. `content or ""`), and add its `len()` to chars. 6) Only read from the input messages, never change them. 7) Return `stats` after the loop.',
        ],
    },
    {
        "id": "combo-2",
        "title": "Trim chat history",
        "difficulty": 2,
        "topics": ["lists", "conditionals", "loops", "functions"],
        "prompt": r'''
            Context windows are limited. Write `trim_history(messages, max_chars)` that
            returns a **new** list of messages that fits a character budget:

            - Every `"system"` message is always kept (even if it alone exceeds the budget).
            - Then keep the **most recent** non-system messages, walking backwards from the
              end, as long as the total content length (system messages included) stays
              `<= max_chars`. Stop at the first message that does not fit - never skip
              over it to keep an older one.
            - The result keeps the original order. The input list is not modified.

            ```python
            msgs = [
                {"role": "system", "content": "sys"},        # 3 chars
                {"role": "user", "content": "aaaaaaaaaa"},   # 10
                {"role": "assistant", "content": "bbbb"},    # 4
                {"role": "user", "content": "cc"},           # 2
            ]
            trim_history(msgs, 10)   # [system "sys", assistant "bbbb", user "cc"]
            ```
        ''',
        "starter": r'''
            def trim_history(messages, max_chars):
                ...
        ''',
        "tests": r'''
            from solution import trim_history

            def m(role, content):
                return {"role": role, "content": content}

            MSGS = [m("system", "sys"), m("user", "aaaaaaaaaa"), m("assistant", "bbbb"), m("user", "cc")]

            def contents(msgs):
                return [x["content"] for x in msgs]

            def test_example():
                got = trim_history(MSGS, 10)
                assert contents(got) == ["sys", "bbbb", "cc"], f"kept {contents(got)!r}"

            def test_everything_fits():
                got = trim_history(MSGS, 100)
                assert contents(got) == ["sys", "aaaaaaaaaa", "bbbb", "cc"], f"kept {contents(got)!r}"

            def test_stops_at_first_message_that_does_not_fit():
                msgs = [m("user", "x"), m("user", "yyyyyyyyyy"), m("user", "zz")]
                got = trim_history(msgs, 5)
                assert contents(got) == ["zz"], f"kept {contents(got)!r} - older messages must not skip ahead"

            def test_system_always_kept_even_over_budget():
                msgs = [m("system", "a very long system prompt"), m("user", "hi")]
                got = trim_history(msgs, 5)
                assert contents(got) == ["a very long system prompt"], f"kept {contents(got)!r}"

            def test_system_in_the_middle_keeps_order():
                msgs = [m("user", "old"), m("system", "S"), m("user", "new")]
                got = trim_history(msgs, 4)
                assert contents(got) == ["S", "new"], f"kept {contents(got)!r}"

            def test_input_not_modified():
                msgs = list(MSGS)
                trim_history(msgs, 5)
                assert msgs == MSGS, "the input list was modified"
        ''',
        "solution": r'''
            def trim_history(messages, max_chars):
                used = sum(len(msg["content"]) for msg in messages if msg["role"] == "system")
                keep = set()
                for i in range(len(messages) - 1, -1, -1):
                    msg = messages[i]
                    if msg["role"] == "system":
                        continue
                    if used + len(msg["content"]) > max_chars:
                        break
                    used += len(msg["content"])
                    keep.add(i)
                return [msg for i, msg in enumerate(messages)
                        if msg["role"] == "system" or i in keep]
        ''',
        "hints": [
            'This is about lists, a running total and walking a list backwards (`range()` with a negative step, or `reversed()`). Start by working out how many characters the system messages use.',
            'Stage 1: add up the length of all system messages - that budget is always spent. Stage 2: walk from the newest message to the oldest, skipping system messages, and keep each one while the running total still fits; stop (break) at the first one that does not fit. Stage 3: build a new list in the original order containing the system messages plus the ones you decided to keep.',
            '1) Compute `used` = sum of `len(content)` for messages whose role is "system". 2) Make an empty set to remember the indexes you keep. 3) Loop over indexes from `len(messages) - 1` down to 0. 4) Skip system messages with `continue`. 5) If `used` plus this message\'s length is more than `max_chars`, `break`. 6) Otherwise add the length to `used` and add the index to the set. 7) Finally loop forwards with `enumerate()` and collect each message that is a system message or whose index is in the set. Return that new list.',
        ],
    },
    {
        "id": "combo-3",
        "title": "API cost report",
        "difficulty": 2,
        "topics": ["dicts", "fstrings", "loops", "functions"],
        "prompt": r'''
            Write `cost_report(usage, prices)` that turns raw usage records into a text report.

            - `usage`: list of dicts `{"model": str, "input_tokens": int, "output_tokens": int}`
            - `prices`: dict `model -> (input_price_per_1k, output_price_per_1k)` in dollars
            - Aggregate per model. One line per model, **sorted by model name**:
              `"<model>: <total tokens with thousands separators> tokens, $<cost to 4 decimals>"`
            - Final line: `"TOTAL: <tokens> tokens, $<cost>"` in the same format.
            - Lines joined with `"\n"` (no trailing newline).
            - If a model has no price, raise `ValueError` naming the model.

            ```python
            usage = [
                {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
                {"model": "claude", "input_tokens": 2000, "output_tokens": 0},
                {"model": "gpt-4o", "input_tokens": 1500, "output_tokens": 300},
            ]
            prices = {"gpt-4o": (0.005, 0.015), "claude": (0.003, 0.015)}
            print(cost_report(usage, prices))
            # claude: 2,000 tokens, $0.0060
            # gpt-4o: 3,300 tokens, $0.0245
            # TOTAL: 5,300 tokens, $0.0305
            ```
        ''',
        "starter": r'''
            def cost_report(usage, prices):
                ...
        ''',
        "tests": r'''
            from solution import cost_report

            USAGE = [
                {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
                {"model": "claude", "input_tokens": 2000, "output_tokens": 0},
                {"model": "gpt-4o", "input_tokens": 1500, "output_tokens": 300},
            ]
            PRICES = {"gpt-4o": (0.005, 0.015), "claude": (0.003, 0.015)}

            def test_example():
                got = cost_report(USAGE, PRICES)
                expected = "claude: 2,000 tokens, $0.0060\ngpt-4o: 3,300 tokens, $0.0245\nTOTAL: 5,300 tokens, $0.0305"
                assert got == expected, f"got:\n{got}"

            def test_large_numbers_use_separators():
                usage = [{"model": "m", "input_tokens": 1_200_000, "output_tokens": 34_567}]
                got = cost_report(usage, {"m": (0.001, 0.002)})
                assert got.splitlines()[0] == "m: 1,234,567 tokens, $1.2691", f"got {got.splitlines()[0]!r}"

            def test_empty_usage():
                assert cost_report([], PRICES) == "TOTAL: 0 tokens, $0.0000"

            def test_unknown_model_raises():
                try:
                    cost_report([{"model": "mystery", "input_tokens": 1, "output_tokens": 1}], PRICES)
                except ValueError as exc:
                    assert "mystery" in str(exc), f"error message should name the model: {exc}"
                    return
                raise AssertionError("a model without a price should raise ValueError")
        ''',
        "solution": r'''
            def cost_report(usage, prices):
                totals = {}
                for record in usage:
                    model = record["model"]
                    if model not in prices:
                        raise ValueError(f"no price for model {model!r}")
                    in_price, out_price = prices[model]
                    tokens, cost = totals.get(model, (0, 0.0))
                    tokens += record["input_tokens"] + record["output_tokens"]
                    cost += (record["input_tokens"] * in_price + record["output_tokens"] * out_price) / 1000
                    totals[model] = (tokens, cost)
                lines = [f"{model}: {tokens:,} tokens, ${cost:.4f}"
                         for model, (tokens, cost) in sorted(totals.items())]
                all_tokens = sum(t for t, _ in totals.values())
                all_cost = sum(c for _, c in totals.values())
                lines.append(f"TOTAL: {all_tokens:,} tokens, ${all_cost:.4f}")
                return "\n".join(lines)
        ''',
        "hints": [
            'You need a dict to aggregate per model, a loop, and f-string format specs: `:,` for thousands separators and `:.4f` for 4 decimals. Start by grouping the records by model.',
            "Stage 1: loop over the usage records; check the model has a price (otherwise raise ValueError), then add its tokens and its cost to that model's running totals. Cost = (input_tokens * input_price + output_tokens * output_price) / 1000. Stage 2: build one formatted line per model in sorted order. Stage 3: add the TOTAL line and join everything with newlines.",
            '1) Create an empty dict `totals` mapping model -> (tokens, cost). 2) For each record: if the model is not in `prices`, raise `ValueError` with the model name in the message. 3) Unpack the two prices, fetch the current totals with `.get(model, (0, 0.0))`, add the record\'s tokens and cost, and store them back. 4) Loop over `sorted(totals.items())` and build lines like `model: tokens, $cost` using `{tokens:,}` and `{cost:.4f}`. 5) Use `sum()` to get the overall tokens and cost, and append the TOTAL line in the same format. 6) Return `"\\n".join(lines)` - an empty usage list still gives just the TOTAL line with zeros.',
        ],
    },
    {
        "id": "combo-4",
        "title": "Top keywords",
        "difficulty": 2,
        "topics": ["strings", "comprehensions", "sorting"],
        "prompt": r'''
            Extract keywords from a document to use as search tags. Write
            `top_keywords(text, stopwords, n)`:

            - Lowercase the text, split on whitespace, strip `.,!?;:"'()` from both ends of
              each token, drop empty tokens.
            - Drop tokens in `stopwords` (compare case-insensitively) and tokens shorter than
              3 characters.
            - Return the `n` most frequent as `(word, count)` tuples, sorted by count
              descending, then word alphabetically.

            ```python
            text = "The agent calls tools. Tools return JSON; the agent reads JSON, then answers!"
            top_keywords(text, {"the", "then"}, 3)
            # [("agent", 2), ("json", 2), ("tools", 2)]
            ```
        ''',
        "starter": r'''
            def top_keywords(text, stopwords, n):
                ...
        ''',
        "tests": r'''
            from solution import top_keywords

            TEXT = "The agent calls tools. Tools return JSON; the agent reads JSON, then answers!"

            def test_example():
                got = top_keywords(TEXT, {"the", "then"}, 3)
                assert got == [("agent", 2), ("json", 2), ("tools", 2)], f"got {got!r}"

            def test_ties_alphabetical_after_count():
                got = top_keywords(TEXT, {"the", "then"}, 6)
                assert got == [("agent", 2), ("json", 2), ("tools", 2), ("answers", 1),
                               ("calls", 1), ("reads", 1)], f"got {got!r}"

            def test_stopwords_case_insensitive_and_short_words_dropped():
                got = top_keywords("An LLM is an LLM. Is it? RAG rag", {"LLM"}, 5)
                assert got == [("rag", 2)], f"got {got!r}"

            def test_n_larger_than_vocabulary():
                got = top_keywords("vector vector search", set(), 10)
                assert got == [("vector", 2), ("search", 1)], f"got {got!r}"

            def test_empty_text():
                assert top_keywords("", set(), 3) == []
        ''',
        "solution": r'''
            def top_keywords(text, stopwords, n):
                stop = {w.lower() for w in stopwords}
                tokens = [t.strip(".,!?;:\"'()") for t in text.lower().split()]
                counts = {}
                for token in tokens:
                    if len(token) >= 3 and token not in stop:
                        counts[token] = counts.get(token, 0) + 1
                ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
                return ranked[:n]
        ''',
        "hints": [
            'Use string methods (`.lower()`, `.split()`, `.strip()`), a dict to count words, and `sorted()` with a `key`. Start by turning the text into a clean list of tokens.',
            'Stage 1: lowercase, split on whitespace, strip the punctuation characters from each token. Stage 2: count the tokens that are at least 3 characters long and not stopwords (lowercase the stopwords too). Stage 3: sort the (word, count) pairs by count high-to-low, then word A-to-Z, and take the first n.',
            '1) Build a lowercase set of stopwords with a set comprehension. 2) Make the token list: `text.lower().split()`, then `.strip()` each token with the string of punctuation `.,!?;:"\'()`. 3) Loop over the tokens; skip empty ones, ones shorter than 3 and stopwords; otherwise add 1 to the word\'s count using `.get(word, 0)`. 4) Call `sorted()` on `counts.items()` with a key that returns `(-count, word)` so bigger counts come first and ties go alphabetically. 5) Return the slice of the first `n` items (slicing is safe even if n is larger than the list).',
        ],
    },
    {
        "id": "combo-5",
        "title": "Load a model config",
        "difficulty": 2,
        "topics": ["json", "files", "errors"],
        "prompt": r'''
            Write `load_config(path)` that loads LLM settings from a JSON file and merges
            them over these defaults:

            ```python
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}
            ```

            - File does not exist -> return a copy of the defaults.
            - Invalid JSON -> raise `ValueError` whose message contains the path.
            - Top-level JSON value is not an object -> `ValueError`.
            - A key not in `DEFAULTS` -> `ValueError` whose message contains the key.
            - `temperature` must be a number between 0 and 2 inclusive -> otherwise `ValueError`.
            - Return the merged dict (never mutate `DEFAULTS`).

            ```python
            # config.json: {"model": "claude-sonnet", "temperature": 0}
            load_config("config.json")
            # {"model": "claude-sonnet", "temperature": 0, "max_tokens": 256}
            ```
        ''',
        "starter": r'''
            import json

            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}


            def load_config(path):
                ...
        ''',
        "setup_files": {
            "config.json": '{"model": "claude-sonnet", "temperature": 0}',
            "broken.json": '{"model": "gpt-4o",',
            "list.json": '["model", "gpt-4o"]',
            "extra.json": '{"model": "gpt-4o", "top_k": 5}',
            "hot.json": '{"temperature": 2.5}',
            "text_temp.json": '{"temperature": "high"}',
        },
        "tests": r'''
            import solution
            from solution import load_config

            def expect_value_error(path, must_contain=None):
                try:
                    load_config(path)
                except ValueError as exc:
                    if must_contain:
                        assert must_contain in str(exc), f"error message {str(exc)!r} should mention {must_contain!r}"
                    return
                raise AssertionError(f"load_config({path!r}) should raise ValueError")

            def test_merges_over_defaults():
                got = load_config("config.json")
                assert got == {"model": "claude-sonnet", "temperature": 0, "max_tokens": 256}, f"got {got!r}"

            def test_missing_file_gives_defaults_copy():
                got = load_config("nope.json")
                assert got == {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}, f"got {got!r}"
                got["model"] = "changed"
                assert solution.DEFAULTS["model"] == "gpt-4o-mini", "DEFAULTS was mutated"

            def test_invalid_json_mentions_path():
                expect_value_error("broken.json", "broken.json")

            def test_non_object_rejected():
                expect_value_error("list.json")

            def test_unknown_key_rejected():
                expect_value_error("extra.json", "top_k")

            def test_temperature_validated():
                expect_value_error("hot.json")
                expect_value_error("text_temp.json")
        ''',
        "solution": r'''
            import json

            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}


            def load_config(path):
                try:
                    with open(path, encoding="utf-8") as fh:
                        data = json.load(fh)
                except FileNotFoundError:
                    return dict(DEFAULTS)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON in {path}: {exc}") from exc
                if not isinstance(data, dict):
                    raise ValueError(f"{path} must contain a JSON object")
                for key in data:
                    if key not in DEFAULTS:
                        raise ValueError(f"unknown config key: {key}")
                config = {**DEFAULTS, **data}
                temp = config["temperature"]
                if isinstance(temp, bool) or not isinstance(temp, (int, float)) or not 0 <= temp <= 2:
                    raise ValueError(f"temperature must be a number between 0 and 2, got {temp!r}")
                return config
        ''',
        "hints": [
            'You need `open()` plus `json.load()`, and `try`/`except` for `FileNotFoundError` and `json.JSONDecodeError`. Start by reading the file inside a try block.',
            'Stage 1: try to open and parse the file; a missing file returns a copy of DEFAULTS, bad JSON becomes a ValueError mentioning the path. Stage 2: validate the data - it must be a dict and every key must be one of the DEFAULTS keys. Stage 3: merge the data over a copy of the defaults and check temperature is a real number from 0 to 2.',
            '1) In a `try`, open the path with a `with` block and `json.load()` it. 2) `except FileNotFoundError`: return `dict(DEFAULTS)` (a copy). 3) `except json.JSONDecodeError`: raise `ValueError` with the path in an f-string message. 4) If `isinstance(data, dict)` is false, raise ValueError. 5) Loop over the keys of data; if one is not in DEFAULTS, raise ValueError naming that key. 6) Build the merged dict with `{**DEFAULTS, **data}` so DEFAULTS is never changed. 7) Read the temperature: raise ValueError if it is a bool, is not an `int`/`float` (check with `isinstance()`), or is outside 0..2. 8) Return the merged dict.',
        ],
    },
    {
        "id": "combo-6",
        "title": "Token usage from JSONL logs",
        "difficulty": 3,
        "topics": ["files", "json", "dicts", "sorting"],
        "prompt": r'''
            Your app logs every LLM response as one JSON object per line (JSONL):

            ```
            {"model": "gpt-4o", "usage": {"prompt_tokens": 120, "completion_tokens": 30}}
            ```

            Write `usage_report(path)`:

            - Blank lines are ignored.
            - Lines that are invalid JSON, or lack `model`, `usage.prompt_tokens` or
              `usage.completion_tokens`, are **skipped and counted**.
            - Return:
              ```python
              {
                  "models": [
                      {"model": ..., "requests": ..., "prompt_tokens": ...,
                       "completion_tokens": ..., "total_tokens": ...},
                      ...
                  ],
                  "skipped": <number of skipped lines>,
              }
              ```
              with `"models"` sorted by `total_tokens` descending, then model name ascending.
        ''',
        "starter": r'''
            import json


            def usage_report(path):
                ...
        ''',
        "setup_files": {
            "logs.jsonl": r'''
                {"model": "gpt-4o", "usage": {"prompt_tokens": 120, "completion_tokens": 30}}
                {"model": "claude", "usage": {"prompt_tokens": 400, "completion_tokens": 100}}

                {"model": "gpt-4o", "usage": {"prompt_tokens": 80, "completion_tokens": 20}}
                not json at all
                {"model": "gpt-4o"}
                {"usage": {"prompt_tokens": 1, "completion_tokens": 1}}
                {"model": "mini", "usage": {"prompt_tokens": 250, "completion_tokens": 0}}
            ''',
        },
        "tests": r'''
            from solution import usage_report

            def test_log_file():
                got = usage_report("logs.jsonl")
                assert got["skipped"] == 3, f"skipped was {got['skipped']!r}"
                assert got["models"] == [
                    {"model": "claude", "requests": 1, "prompt_tokens": 400, "completion_tokens": 100, "total_tokens": 500},
                    {"model": "gpt-4o", "requests": 2, "prompt_tokens": 200, "completion_tokens": 50, "total_tokens": 250},
                    {"model": "mini", "requests": 1, "prompt_tokens": 250, "completion_tokens": 0, "total_tokens": 250},
                ], f"models were {got['models']!r}"

            def test_empty_file():
                with open("empty.jsonl", "w") as fh:
                    fh.write("\n\n")
                assert usage_report("empty.jsonl") == {"models": [], "skipped": 0}

            def test_usage_not_a_dict_is_skipped():
                with open("odd.jsonl", "w") as fh:
                    fh.write('{"model": "a", "usage": 5}\n[1, 2]\n{"model": "a", "usage": {"prompt_tokens": 1, "completion_tokens": 2}}\n')
                got = usage_report("odd.jsonl")
                assert got["skipped"] == 2, f"skipped was {got['skipped']!r}"
                assert got["models"] == [{"model": "a", "requests": 1, "prompt_tokens": 1,
                                          "completion_tokens": 2, "total_tokens": 3}], f"got {got['models']!r}"

            def test_whitespace_only_lines_ignored():
                with open("ws.jsonl", "w") as fh:
                    fh.write('   \n{"model": "b", "usage": {"prompt_tokens": 5, "completion_tokens": 5}}\n\t\n')
                got = usage_report("ws.jsonl")
                assert got["skipped"] == 0 and got["models"][0]["total_tokens"] == 10, f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def usage_report(path):
                totals = {}
                skipped = 0
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        if not line.strip():
                            continue
                        try:
                            record = json.loads(line)
                            model = record["model"]
                            prompt = record["usage"]["prompt_tokens"]
                            completion = record["usage"]["completion_tokens"]
                        except (json.JSONDecodeError, KeyError, TypeError):
                            skipped += 1
                            continue
                        entry = totals.setdefault(model, {
                            "model": model, "requests": 0, "prompt_tokens": 0,
                            "completion_tokens": 0, "total_tokens": 0,
                        })
                        entry["requests"] += 1
                        entry["prompt_tokens"] += prompt
                        entry["completion_tokens"] += completion
                        entry["total_tokens"] += prompt + completion
                models = sorted(totals.values(), key=lambda e: (-e["total_tokens"], e["model"]))
                return {"models": models, "skipped": skipped}
        ''',
        "hints": [
            'Read the file line by line with `open()`, parse each line with `json.loads()`, and use `try`/`except` to catch bad lines. A dict keyed by model will hold the running totals.',
            "Stage 1: for each line, skip it if it is blank or whitespace only. Stage 2: inside a try, parse the JSON and pull out the model, prompt_tokens and completion_tokens; if anything goes wrong (bad JSON, missing key, wrong type), count it as skipped and move on. Stage 3: add the numbers to that model's totals. Stage 4: sort the per-model dicts and return them with the skipped count.",
            '1) Set `totals = {}` and `skipped = 0`. 2) Open the file with `with` and loop over its lines. 3) If `line.strip()` is empty, `continue`. 4) In a `try`, call `json.loads(line)` and read `record["model"]`, `record["usage"]["prompt_tokens"]` and `record["usage"]["completion_tokens"]`. 5) `except (json.JSONDecodeError, KeyError, TypeError)`: add 1 to skipped and `continue` - TypeError covers things like a list line or `usage` being a number. 6) Use `.setdefault()` to get the model\'s entry dict with all five keys starting at 0, then add 1 request and the token counts (total = prompt + completion). 7) Sort `totals.values()` with a key of `(-total_tokens, model)`. 8) Return `{"models": ..., "skipped": skipped}`.',
        ],
    },
    {
        "id": "combo-7",
        "title": "Request builder CLI",
        "difficulty": 2,
        "mode": "script",
        "topics": ["env", "scripts", "errors", "json"],
        "prompt": r'''
            Write a **script** that builds a chat-completion request body from the command
            line and environment, and prints it as JSON.

            ```
            $ LLM_API_KEY=sk-123 LLM_MODEL=gpt-4o python solution.py Tell me a joke
            {"model": "gpt-4o", "max_tokens": 256, "messages": [{"role": "user", "content": "Tell me a joke"}]}
            ```

            - The prompt is all command-line arguments joined by single spaces. No arguments
              -> print `usage: solution.py PROMPT...` to **stderr**, exit code **2**.
            - `LLM_API_KEY` must be set and non-empty, otherwise print
              `error: LLM_API_KEY is not set` to stderr and exit **1**. Never print the key.
            - `LLM_MODEL` defaults to `gpt-4o-mini`.
            - `LLM_MAX_TOKENS` defaults to `256`; if set it must be a positive integer,
              otherwise print `error: LLM_MAX_TOKENS must be a positive integer` to stderr
              and exit **1**.
            - On success print the JSON object (keys `model`, `max_tokens`, `messages`) to
              stdout and exit 0.
        ''',
        "starter": r'''
            import json
            import os
            import sys

            # build and print the request body
        ''',
        "tests": r'''
            import json

            KEY = {"LLM_API_KEY": "sk-secret-123"}

            def test_builds_request():
                r = run_script(["Tell", "me", "a", "joke"], env={**KEY, "LLM_MODEL": "gpt-4o"})
                assert r.returncode == 0, r.stderr
                body = json.loads(r.stdout)
                assert body == {"model": "gpt-4o", "max_tokens": 256,
                                "messages": [{"role": "user", "content": "Tell me a joke"}]}, f"got {body!r}"

            def test_defaults_and_max_tokens():
                r = run_script(["hi"], env={**KEY, "LLM_MAX_TOKENS": "1024"})
                assert r.returncode == 0, r.stderr
                body = json.loads(r.stdout)
                assert body["model"] == "gpt-4o-mini" and body["max_tokens"] == 1024, f"got {body!r}"

            def test_key_never_printed():
                r = run_script(["hi"], env=KEY)
                assert "sk-secret-123" not in r.stdout + r.stderr, "the API key was printed"

            def test_no_prompt_is_usage_error():
                r = run_script([], env=KEY)
                assert r.returncode == 2, f"exit code {r.returncode}"
                assert "usage" in r.stderr.lower() and r.stdout == "", f"stdout={r.stdout!r} stderr={r.stderr!r}"

            def test_missing_key():
                r = run_script(["hi"], env={"LLM_API_KEY": ""})
                assert r.returncode == 1, f"exit code {r.returncode}"
                assert "LLM_API_KEY" in r.stderr and r.stdout == "", f"stdout={r.stdout!r} stderr={r.stderr!r}"

            def test_bad_max_tokens():
                for bad in ("abc", "0", "-5", "2.5"):
                    r = run_script(["hi"], env={**KEY, "LLM_MAX_TOKENS": bad})
                    assert r.returncode == 1, f"LLM_MAX_TOKENS={bad!r} gave exit code {r.returncode}"
                    assert "LLM_MAX_TOKENS" in r.stderr, f"stderr was {r.stderr!r}"
        ''',
        "solution": r'''
            import json
            import os
            import sys


            def fail(message, code):
                print(message, file=sys.stderr)
                sys.exit(code)


            def main():
                if len(sys.argv) < 2:
                    fail("usage: solution.py PROMPT...", 2)
                if not os.environ.get("LLM_API_KEY"):
                    fail("error: LLM_API_KEY is not set", 1)
                model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
                try:
                    max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "256"))
                    if max_tokens < 1:
                        raise ValueError
                except ValueError:
                    fail("error: LLM_MAX_TOKENS must be a positive integer", 1)
                body = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": " ".join(sys.argv[1:])}],
                }
                print(json.dumps(body))


            if __name__ == "__main__":
                main()
        ''',
        "hints": [
            'This is a script, not a function: use `sys.argv` for the arguments, `os.environ.get()` for environment variables, `print(..., file=sys.stderr)` for errors, `sys.exit()` for exit codes and `json.dumps()` for output.',
            'Stage 1: check there is at least one argument, else print the usage line to stderr and exit 2. Stage 2: check the API key is set and non-empty, else error and exit 1 (never print the key itself). Stage 3: read the model with its default, and read max tokens, converting it to an int and making sure it is positive - any failure is an error with exit 1. Stage 4: build the body dict and print it as JSON.',
            '1) Write a small helper that prints a message to stderr and calls `sys.exit(code)`. 2) If `len(sys.argv) < 2`, use it with the usage message and code 2. 3) If `os.environ.get("LLM_API_KEY")` is empty or missing, fail with code 1. 4) Get the model with `os.environ.get("LLM_MODEL", "gpt-4o-mini")`. 5) In a `try`, convert `os.environ.get("LLM_MAX_TOKENS", "256")` with `int()`; if the number is below 1, raise ValueError yourself. `except ValueError`: fail with the max-tokens message and code 1 (note `int("2.5")` already raises). 6) Join `sys.argv[1:]` with single spaces to get the prompt. 7) Build the dict with keys model, max_tokens and messages (one user message) and `print(json.dumps(body))`. 8) Put the steps in a `main()` guarded by `if __name__ == "__main__":`.',
        ],
    },
    {
        "id": "combo-8",
        "title": "Overlapping chunker",
        "difficulty": 3,
        "topics": ["strings", "comprehensions", "lists", "errors"],
        "prompt": r'''
            RAG pipelines split documents into overlapping chunks. Write
            `chunk_words(text, size, overlap)`:

            - Split `text` into words (whitespace). Each chunk has up to `size` words and
              starts `size - overlap` words after the previous one.
            - Stop after the first chunk that reaches the end of the text (no chunk may be
              made only of words already covered).
            - Return a list of dicts `{"id": <0-based>, "start": <index of first word>,
              "text": <words joined by single spaces>}`. Empty text -> `[]`.
            - Raise `ValueError` if `size < 1`, `overlap < 0` or `overlap >= size`.

            ```python
            chunk_words("a b c d e f g", 3, 1)
            # [{"id": 0, "start": 0, "text": "a b c"},
            #  {"id": 1, "start": 2, "text": "c d e"},
            #  {"id": 2, "start": 4, "text": "e f g"}]
            ```
        ''',
        "starter": r'''
            def chunk_words(text, size, overlap):
                ...
        ''',
        "tests": r'''
            from solution import chunk_words

            def test_example():
                got = chunk_words("a b c d e f g", 3, 1)
                assert got == [{"id": 0, "start": 0, "text": "a b c"},
                               {"id": 1, "start": 2, "text": "c d e"},
                               {"id": 2, "start": 4, "text": "e f g"}], f"got {got!r}"

            def test_last_chunk_may_be_short_but_not_redundant():
                got = chunk_words("w1 w2 w3 w4 w5", 3, 1)
                texts = [c["text"] for c in got]
                assert texts == ["w1 w2 w3", "w3 w4 w5"], f"got {texts!r}"
                got = chunk_words("w1 w2 w3 w4 w5 w6", 3, 1)
                texts = [c["text"] for c in got]
                assert texts == ["w1 w2 w3", "w3 w4 w5", "w5 w6"], f"got {texts!r}"

            def test_no_overlap_and_messy_whitespace():
                got = chunk_words("  one\ttwo\n three  four ", 2, 0)
                assert got == [{"id": 0, "start": 0, "text": "one two"},
                               {"id": 1, "start": 2, "text": "three four"}], f"got {got!r}"

            def test_text_shorter_than_size():
                assert chunk_words("just two", 5, 2) == [{"id": 0, "start": 0, "text": "just two"}]

            def test_empty_text():
                assert chunk_words("   ", 3, 1) == []

            def test_invalid_arguments():
                for args in ((0, 0), (3, 3), (3, 5), (3, -1)):
                    try:
                        chunk_words("a b c", *args)
                    except ValueError:
                        continue
                    raise AssertionError(f"size/overlap {args} should raise ValueError")
        ''',
        "solution": r'''
            def chunk_words(text, size, overlap):
                if size < 1 or overlap < 0 or overlap >= size:
                    raise ValueError("need size >= 1 and 0 <= overlap < size")
                words = text.split()
                step = size - overlap
                chunks = []
                start = 0
                while start < len(words):
                    chunks.append({"id": len(chunks), "start": start,
                                   "text": " ".join(words[start:start + size])})
                    if start + size >= len(words):
                        break
                    start += step
                return chunks
        ''',
        "hints": [
            'Use `.split()` to get the words, list slicing to take each chunk, `" ".join()` to glue it back, and a `while` loop that moves a start index forward. Check the arguments first and raise `ValueError`.',
            'Stage 1: validate size and overlap. Stage 2: split the text into words; the step between chunk starts is size - overlap. Stage 3: starting at 0, repeatedly take up to `size` words from the start index, record the chunk, and stop as soon as that chunk reached the last word; otherwise move start forward by the step.',
            '1) If `size < 1`, `overlap < 0` or `overlap >= size`, raise ValueError. 2) `words = text.split()` (this also handles tabs, newlines and extra spaces; empty text gives no words). 3) Compute `step = size - overlap`, make an empty `chunks` list and set `start = 0`. 4) `while start < len(words)`: append a dict with `id` = current length of `chunks`, `start`, and `text` = the slice `words[start:start + size]` joined with spaces. 5) If `start + size >= len(words)`, the chunk reached the end, so `break`. 6) Otherwise add `step` to `start`. 7) Return `chunks`.',
        ],
    },
    {
        "id": "combo-9",
        "title": "Serialisable conversation",
        "difficulty": 3,
        "topics": ["classes", "dataclasses", "json"],
        "prompt": r'''
            Model a chat session that can be saved and restored.

            1. A **dataclass** `Message` with fields `role: str`, `content: str`,
               `tokens: int = 0`. Creating one with a role outside
               `{"system", "user", "assistant", "tool"}` raises `ValueError`.
            2. A class `Conversation`:
               - `Conversation(model)` - stores `model` and an empty `messages` list
               - `add(role, content, tokens=0)` - appends a `Message` and returns it
               - `total_tokens` - a **property** with the sum of message tokens
               - `to_json()` - returns a JSON string of
                 `{"model": ..., "messages": [{"role": ..., "content": ..., "tokens": ...}, ...]}`
               - `Conversation.from_json(text)` - a **classmethod** rebuilding an equal
                 conversation (with `Message` instances)

            ```python
            conv = Conversation("gpt-4o")
            conv.add("user", "hi", tokens=3)
            conv.total_tokens                         # 3
            Conversation.from_json(conv.to_json()).messages[0]   # Message(role="user", content="hi", tokens=3)
            ```
        ''',
        "starter": r'''
            import json
            from dataclasses import dataclass


            class Message:
                ...


            class Conversation:
                ...
        ''',
        "tests": r'''
            import dataclasses
            import json
            from solution import Message, Conversation

            def build():
                conv = Conversation("gpt-4o")
                conv.add("system", "Be brief.", tokens=4)
                conv.add("user", "What is RAG?", tokens=6)
                conv.add("assistant", "Retrieval-augmented generation.")
                return conv

            def test_message_is_a_dataclass_with_default():
                assert dataclasses.is_dataclass(Message), "Message should be a @dataclass"
                m = Message("user", "hi")
                assert m.tokens == 0 and m == Message("user", "hi", 0)

            def test_invalid_role_rejected():
                try:
                    Message("robot", "beep")
                except ValueError:
                    return
                raise AssertionError("role 'robot' should raise ValueError")

            def test_add_and_total_tokens_property():
                conv = build()
                assert isinstance(conv.messages[1], Message)
                assert conv.add("tool", "{}", 2) == Message("tool", "{}", 2), "add should return the Message"
                assert conv.total_tokens == 12, f"total_tokens was {conv.total_tokens!r}"

            def test_to_json_shape():
                data = json.loads(build().to_json())
                assert data == {"model": "gpt-4o", "messages": [
                    {"role": "system", "content": "Be brief.", "tokens": 4},
                    {"role": "user", "content": "What is RAG?", "tokens": 6},
                    {"role": "assistant", "content": "Retrieval-augmented generation.", "tokens": 0},
                ]}, f"got {data!r}"

            def test_round_trip():
                original = build()
                restored = Conversation.from_json(original.to_json())
                assert isinstance(restored, Conversation)
                assert restored.model == "gpt-4o"
                assert restored.messages == original.messages, f"got {restored.messages!r}"
                assert all(isinstance(m, Message) for m in restored.messages)

            def test_from_json_validates_roles():
                bad = json.dumps({"model": "x", "messages": [{"role": "hacker", "content": "", "tokens": 0}]})
                try:
                    Conversation.from_json(bad)
                except ValueError:
                    return
                raise AssertionError("an invalid role in JSON should raise ValueError")
        ''',
        "solution": r'''
            import json
            from dataclasses import asdict, dataclass

            ROLES = {"system", "user", "assistant", "tool"}


            @dataclass
            class Message:
                role: str
                content: str
                tokens: int = 0

                def __post_init__(self):
                    if self.role not in ROLES:
                        raise ValueError(f"invalid role: {self.role!r}")


            class Conversation:
                def __init__(self, model):
                    self.model = model
                    self.messages = []

                def add(self, role, content, tokens=0):
                    message = Message(role, content, tokens)
                    self.messages.append(message)
                    return message

                @property
                def total_tokens(self):
                    return sum(m.tokens for m in self.messages)

                def to_json(self):
                    return json.dumps({"model": self.model,
                                       "messages": [asdict(m) for m in self.messages]})

                @classmethod
                def from_json(cls, text):
                    data = json.loads(text)
                    conv = cls(data["model"])
                    for m in data["messages"]:
                        conv.add(m["role"], m["content"], m.get("tokens", 0))
                    return conv
        ''',
        "hints": [
            'Use `@dataclass` for Message and put the role check in `__post_init__`. For Conversation you need `@property` and `@classmethod`, plus `json.dumps()`/`json.loads()` (and `dataclasses.asdict()` helps).',
            'Stage 1: define Message with three fields (tokens defaulting to 0) and validate the role right after creation. Stage 2: Conversation stores the model and a list; `add` creates a Message, appends it and returns it; `total_tokens` sums the tokens. Stage 3: `to_json` turns everything into plain dicts and dumps it; `from_json` loads the dict, creates a new conversation and re-adds each message (so roles get validated again).',
            '1) Make a set of the allowed roles. 2) Decorate `Message` with `@dataclass` and declare `role: str`, `content: str`, `tokens: int = 0`. 3) Add a `__post_init__(self)` method that raises ValueError if `self.role` is not in the allowed set. 4) In `Conversation.__init__`, store `model` and an empty `messages` list. 5) `add()` builds a `Message(role, content, tokens)`, appends it and returns it. 6) `total_tokens` is a method under `@property` that returns `sum()` of each message\'s tokens. 7) `to_json()` returns `json.dumps()` of a dict with the model and a list made with `asdict()` for each message. 8) `from_json(cls, text)` under `@classmethod`: `json.loads()` the text, create `cls(model)`, call `add()` for each message dict (use `.get("tokens", 0)`), and return it.',
        ],
    },
    {
        "id": "combo-10",
        "title": "Paginated API iterator",
        "difficulty": 3,
        "topics": ["generators", "api-data", "errors"],
        "prompt": r'''
            A list endpoint returns results one page at a time. Write a **generator**
            `iter_records(fetch_page)`:

            - `fetch_page(cursor)` returns a page dict. Call it first with `None`.
            - A normal page looks like `{"data": [...], "next_cursor": "abc"}`. Yield every
              item of `"data"`, then fetch the next page with that cursor. Stop when
              `"next_cursor"` is `None` or missing. A missing `"data"` means no items.
            - An error page looks like `{"error": {"message": "rate limited"}}` -> raise
              `RuntimeError` with that message (items from earlier pages were already yielded).
            - Be **lazy**: fetch a page only when its items are actually needed.

            ```python
            pages = {None: {"data": [1, 2], "next_cursor": "p2"},
                     "p2": {"data": [3], "next_cursor": None}}
            list(iter_records(pages.get))   # [1, 2, 3]
            ```
        ''',
        "starter": r'''
            def iter_records(fetch_page):
                ...
        ''',
        "tests": r'''
            import inspect
            from solution import iter_records

            def make_api(pages):
                calls = []
                def fetch(cursor):
                    calls.append(cursor)
                    return pages[cursor]
                return fetch, calls

            PAGES = {
                None: {"data": [{"id": 1}, {"id": 2}], "next_cursor": "c2"},
                "c2": {"data": [], "next_cursor": "c3"},
                "c3": {"data": [{"id": 3}]},
            }

            def test_is_a_generator():
                assert inspect.isgeneratorfunction(iter_records), "iter_records must be a generator function"

            def test_yields_all_pages_in_order():
                fetch, calls = make_api(PAGES)
                got = list(iter_records(fetch))
                assert got == [{"id": 1}, {"id": 2}, {"id": 3}], f"got {got!r}"
                assert calls == [None, "c2", "c3"], f"fetched cursors {calls!r}"

            def test_is_lazy():
                fetch, calls = make_api(PAGES)
                gen = iter_records(fetch)
                assert calls == [], "nothing should be fetched before iteration starts"
                next(gen); next(gen)
                assert calls == [None], f"after 2 items, fetched {calls!r}"

            def test_error_page_raises_after_earlier_items():
                pages = {None: {"data": ["a"], "next_cursor": "x"},
                         "x": {"error": {"message": "rate limited"}}}
                fetch, _ = make_api(pages)
                seen = []
                try:
                    for item in iter_records(fetch):
                        seen.append(item)
                except RuntimeError as exc:
                    assert "rate limited" in str(exc), f"message was {str(exc)!r}"
                    assert seen == ["a"], f"items before the error: {seen!r}"
                    return
                raise AssertionError("an error page should raise RuntimeError")

            def test_page_without_data():
                fetch, _ = make_api({None: {"next_cursor": None}})
                assert list(iter_records(fetch)) == []
        ''',
        "solution": r'''
            def iter_records(fetch_page):
                cursor = None
                while True:
                    page = fetch_page(cursor)
                    if "error" in page:
                        raise RuntimeError(page["error"].get("message", "API error"))
                    yield from page.get("data", [])
                    cursor = page.get("next_cursor")
                    if cursor is None:
                        return
        ''',
        "hints": [
            'Use a generator function: `yield` (or `yield from`) inside a `while True` loop. Keep a `cursor` variable that starts as `None`.',
            'Stage 1: fetch the page for the current cursor (only inside the loop, so nothing runs until someone iterates). Stage 2: if the page has an "error" key, raise RuntimeError with its message. Stage 3: yield each item of "data" (treating a missing "data" as empty). Stage 4: read the next cursor; if it is None or missing, stop, otherwise loop again.',
            '1) Set `cursor = None`. 2) Start `while True:`. 3) Call `fetch_page(cursor)` to get the page. 4) If `"error" in page`, raise `RuntimeError` with the message from `page["error"]` (use `.get("message", ...)` to be safe). 5) `yield from page.get("data", [])` - this hands out the items one at a time. 6) Set `cursor = page.get("next_cursor")`. 7) If the cursor is `None`, `return` to end the generator. Because the fetch happens inside the generator body, the next page is only requested after the previous page\'s items have been consumed.',
        ],
    },
    {
        "id": "combo-11",
        "title": "Async retry with backoff",
        "difficulty": 3,
        "topics": ["async", "errors", "functions"],
        "prompt": r'''
            LLM APIs fail transiently. Write two coroutines:

            1. `call_with_retry(call, prompt, retries=3, base_delay=0.01)`
               - Returns `await call(prompt)`.
               - On `ConnectionError` or `TimeoutError`, wait
                 `base_delay * 2 ** attempt` seconds (attempt = 0, 1, 2, ...) with
                 `asyncio.sleep`, then try again - at most `retries` retries
                 (so `retries + 1` attempts in total). If every attempt fails, re-raise the
                 last error.
               - Any other exception propagates immediately, without retrying.
            2. `ask_many(prompts, call, retries=3, base_delay=0.01)` - runs
               `call_with_retry` for all prompts **concurrently** and returns a list aligned
               with `prompts`: the result, or `None` if that prompt ultimately failed with
               any exception.
        ''',
        "starter": r'''
            import asyncio


            async def call_with_retry(call, prompt, retries=3, base_delay=0.01):
                ...


            async def ask_many(prompts, call, retries=3, base_delay=0.01):
                ...
        ''',
        "tests": r'''
            import asyncio
            import time
            from solution import call_with_retry, ask_many

            def flaky(fail_times, exc=ConnectionError):
                state = {"attempts": 0}
                async def call(p):
                    state["attempts"] += 1
                    await asyncio.sleep(0)
                    if state["attempts"] <= fail_times:
                        raise exc("transient")
                    return f"ok:{p}"
                return call, state

            def test_succeeds_after_transient_failures():
                call, state = flaky(2)
                got = asyncio.run(call_with_retry(call, "q", retries=3, base_delay=0.001))
                assert got == "ok:q", f"got {got!r}"
                assert state["attempts"] == 3, f"made {state['attempts']} attempts"

            def test_timeout_error_is_retried_too():
                call, state = flaky(1, TimeoutError)
                got = asyncio.run(call_with_retry(call, "q", retries=1, base_delay=0.001))
                assert got == "ok:q" and state["attempts"] == 2

            def test_gives_up_and_reraises():
                call, state = flaky(99)
                try:
                    asyncio.run(call_with_retry(call, "q", retries=2, base_delay=0.001))
                except ConnectionError:
                    assert state["attempts"] == 3, f"made {state['attempts']} attempts, expected retries + 1"
                    return
                raise AssertionError("should re-raise ConnectionError after the last attempt")

            def test_other_errors_not_retried():
                call, state = flaky(99, ValueError)
                try:
                    asyncio.run(call_with_retry(call, "q", retries=3, base_delay=0.001))
                except ValueError:
                    assert state["attempts"] == 1, f"ValueError was retried ({state['attempts']} attempts)"
                    return
                raise AssertionError("ValueError should propagate")

            def test_exponential_backoff():
                call, _ = flaky(99)
                start = time.perf_counter()
                try:
                    asyncio.run(call_with_retry(call, "q", retries=2, base_delay=0.03))
                except ConnectionError:
                    pass
                elapsed = time.perf_counter() - start
                assert 0.085 <= elapsed < 0.3, f"total wait was {elapsed:.3f}s, expected ~0.03 + 0.06"

            def test_ask_many_concurrent_with_failures():
                attempts = {}
                async def call(p):
                    attempts[p] = attempts.get(p, 0) + 1
                    await asyncio.sleep(0.03)
                    if p == "down":
                        raise ConnectionError("503")
                    if p == "bad":
                        raise ValueError("invalid")
                    if p == "blip" and attempts[p] == 1:
                        raise TimeoutError("slow")
                    return p.upper()
                start = time.perf_counter()
                got = asyncio.run(ask_many(["a", "down", "bad", "blip", "b"], call, retries=1, base_delay=0.001))
                elapsed = time.perf_counter() - start
                assert got == ["A", None, None, "BLIP", "B"], f"got {got!r}"
                assert elapsed < 0.3, f"took {elapsed:.2f}s - prompts should run concurrently"
        ''',
        "solution": r'''
            import asyncio

            TRANSIENT = (ConnectionError, TimeoutError)


            async def call_with_retry(call, prompt, retries=3, base_delay=0.01):
                for attempt in range(retries + 1):
                    try:
                        return await call(prompt)
                    except TRANSIENT:
                        if attempt == retries:
                            raise
                        await asyncio.sleep(base_delay * 2 ** attempt)


            async def ask_many(prompts, call, retries=3, base_delay=0.01):
                outcomes = await asyncio.gather(
                    *(call_with_retry(call, p, retries, base_delay) for p in prompts),
                    return_exceptions=True,
                )
                return [None if isinstance(o, Exception) else o for o in outcomes]
        ''',
        "hints": [
            'You need `async def`, `await`, `asyncio.sleep()` for the wait, `try`/`except (ConnectionError, TimeoutError)` for retries, and `asyncio.gather()` to run many calls at once.',
            'call_with_retry: loop over attempt numbers 0..retries; try to return `await call(prompt)`; on a transient error, if it was the last attempt re-raise it, otherwise sleep base_delay * 2 ** attempt and try again. Other errors are simply not caught, so they escape immediately. ask_many: start one call_with_retry per prompt, run them all together with gather, and turn any exception result into None.',
            '1) In `call_with_retry`, loop `for attempt in range(retries + 1)`. 2) Inside, `try: return await call(prompt)`. 3) `except` only the tuple `(ConnectionError, TimeoutError)`. 4) In that except block, if `attempt == retries`, use a bare `raise` to re-raise the last error. 5) Otherwise `await asyncio.sleep(base_delay * 2 ** attempt)`. 6) In `ask_many`, create one `call_with_retry(call, p, retries, base_delay)` coroutine per prompt and pass them all to `asyncio.gather()` with `return_exceptions=True` (unpack them with `*`). 7) `await` the gather - results come back in the same order as the prompts. 8) Return a list that replaces each result that `isinstance(..., Exception)` with `None`.',
        ],
    },
    {
        "id": "combo-12",
        "title": "Parse JSON from an LLM reply",
        "difficulty": 3,
        "topics": ["regex", "json", "errors"],
        "prompt": r'''
            Models asked for JSON often wrap it in prose or Markdown fences and leave
            trailing commas. Write `extract_json(text)` that returns the parsed **dict**:

            1. If the text contains a fenced code block (three backticks, optionally
               followed by a language tag such as `json`, a newline, the content, then
               three closing backticks), use the content of the **first** such block.
            2. Otherwise use the substring from the first `{` to the last `}`.
            3. Remove trailing commas that directly precede a `}` or `]` (whitespace
               allowed between them).
            4. Parse it. If no candidate is found, parsing fails, or the result is not a
               dict, raise `ValueError`.

            ````python
            extract_json('Sure! Here it is:\n```json\n{"tool": "search", "args": {"q": "rag",},}\n```')
            # {"tool": "search", "args": {"q": "rag"}}
            extract_json('The answer is {"score": 7} - hope that helps.')
            # {"score": 7}
            ````
        ''',
        "starter": r'''
            import json
            import re


            def extract_json(text):
                ...
        ''',
        "tests": r'''
            from solution import extract_json

            FENCE = "`" * 3

            def expect_value_error(text):
                try:
                    extract_json(text)
                except ValueError:
                    return
                raise AssertionError(f"extract_json({text!r}) should raise ValueError")

            def test_fenced_json_with_trailing_commas():
                text = f'Sure! Here it is:\n{FENCE}json\n{{"tool": "search", "args": {{"q": "rag",}},}}\n{FENCE}'
                got = extract_json(text)
                assert got == {"tool": "search", "args": {"q": "rag"}}, f"got {got!r}"

            def test_fence_without_language_tag_and_list_comma():
                text = f'{FENCE}\n{{"tags": ["a", "b" ,\n ],\n "n": 2}}\n{FENCE}\nDone.'
                got = extract_json(text)
                assert got == {"tags": ["a", "b"], "n": 2}, f"got {got!r}"

            def test_braces_in_prose():
                got = extract_json('The answer is {"score": 7, "why": {"ok": true}} - hope that helps.')
                assert got == {"score": 7, "why": {"ok": True}}, f"got {got!r}"

            def test_first_fence_wins():
                text = f'{FENCE}json\n{{"n": 1}}\n{FENCE}\nand\n{FENCE}json\n{{"n": 2}}\n{FENCE}'
                got = extract_json(text)
                assert got == {"n": 1}, f"got {got!r}"

            def test_commas_inside_strings_untouched():
                got = extract_json('{"text": "a, b, c", "x": 1,}')
                assert got == {"text": "a, b, c", "x": 1}, f"got {got!r}"

            def test_failures_raise_value_error():
                expect_value_error("no json here")
                expect_value_error('{"broken": }')
                expect_value_error(f"{FENCE}json\n[1, 2, 3]\n{FENCE}")
        ''',
        "solution": r'''
            import json
            import re

            FENCE_RE = re.compile(r"```[\w-]*[ \t]*\n(.*?)```", re.DOTALL)
            TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


            def extract_json(text):
                match = FENCE_RE.search(text)
                if match:
                    candidate = match.group(1)
                else:
                    start, end = text.find("{"), text.rfind("}")
                    if start == -1 or end < start:
                        raise ValueError("no JSON object found")
                    candidate = text[start:end + 1]
                candidate = TRAILING_COMMA_RE.sub(r"\1", candidate)
                try:
                    data = json.loads(candidate)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"could not parse JSON: {exc}") from exc
                if not isinstance(data, dict):
                    raise ValueError("expected a JSON object")
                return data
        ''',
        "hints": [
            'Use `re.search()` with the `re.DOTALL` flag to find a fenced block, `str.find()`/`str.rfind()` for the brace fallback, `re.sub()` to remove trailing commas and `json.loads()` to parse.',
            'Stage 1: look for the first code fence (three backticks, an optional tag, a newline, then content up to the next three backticks) and take its content. Stage 2: if there is no fence, take everything from the first `{` to the last `}`, and raise ValueError if there is none. Stage 3: delete any comma that is followed only by whitespace and then `}` or `]`. Stage 4: parse; turn parse errors and non-dict results into ValueError.',
            '1) Write a regex for the fence: three backticks, then `[\\w-]*` for the optional language tag, a newline, then a lazy group `(.*?)` for the content, then three backticks; compile or search it with `re.DOTALL` so `.` also matches newlines. 2) If it matches, the candidate is `match.group(1)`. 3) Otherwise find the first `{` with `.find()` and the last `}` with `.rfind()`; if either is missing (-1) or they are in the wrong order, raise ValueError; else slice from start to end inclusive. 4) Use `re.sub()` with a pattern like comma, optional whitespace, then a captured `}` or `]`, replacing it with just the captured bracket (`\\1`). 5) `try` `json.loads()` and turn `json.JSONDecodeError` into ValueError. 6) If the result is not a dict (check with `isinstance()`), raise ValueError. 7) Return the dict.',
        ],
    },
    {
        "id": "combo-13",
        "title": "Tool-call dispatcher",
        "difficulty": 3,
        "topics": ["regex", "dataclasses", "dicts", "functions"],
        "prompt": r'''
            A simple agent asks the model to emit tool calls, one per line, like:

            ```
            I'll check the weather first.
            CALL get_weather(city="Paris", days=3)
            CALL get_time()
            ```

            1. A **dataclass** `ToolCall` with fields `name: str` and `args: dict`.
            2. `parse_calls(text)` -> list of `ToolCall`, in order. A call line starts with
               `CALL` (after optional leading whitespace), then a name (letters, digits,
               underscores), then `(...)` ending the line (trailing whitespace allowed).
               Arguments are `key=value` pairs separated by commas where each value is a
               double-quoted string (no escapes) or an integer (possibly negative, becomes
               an `int`). Other lines are ignored.
            3. `dispatch(text, tools)` - `tools` maps names to functions. For each parsed call,
               in order, append to the result list:
               - `tools[name](**args)` if the tool exists
               - `{"error": "unknown tool: <name>"}` if it does not
               - `{"error": "bad arguments for <name>"}` if calling it raises `TypeError`
        ''',
        "starter": r'''
            import re
            from dataclasses import dataclass


            def parse_calls(text):
                ...


            def dispatch(text, tools):
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import ToolCall, parse_calls, dispatch

            TEXT = """I'll check the weather first.
            CALL get_weather(city="Paris, FR", days=3)
              CALL get_time()
            Then maybe CALL fake(x=1) mid-sentence.
            CALL add(a=-2, b=5)
            """

            def test_toolcall_is_a_dataclass():
                assert dataclasses.is_dataclass(ToolCall)
                assert ToolCall("x", {"a": 1}) == ToolCall(name="x", args={"a": 1})

            def test_parse_calls():
                got = parse_calls(TEXT)
                assert got == [
                    ToolCall("get_weather", {"city": "Paris, FR", "days": 3}),
                    ToolCall("get_time", {}),
                    ToolCall("add", {"a": -2, "b": 5}),
                ], f"got {got!r}"

            def test_integer_values_are_ints():
                (call,) = parse_calls('CALL f(n=42, s="42")')
                assert call.args == {"n": 42, "s": "42"}, f"got {call.args!r}"
                assert isinstance(call.args["n"], int)

            def test_no_calls():
                assert parse_calls("Just chatting, no tools needed.") == []

            def test_dispatch_results_and_errors():
                tools = {
                    "get_weather": lambda city, days: f"{city}: sunny for {days}d",
                    "add": lambda a, b: a + b,
                }
                text = TEXT + 'CALL add(a=1)\nCALL send_email(to="x")\n'
                got = dispatch(text, tools)
                assert got == [
                    "Paris, FR: sunny for 3d",
                    {"error": "unknown tool: get_time"},
                    3,
                    {"error": "bad arguments for add"},
                    {"error": "unknown tool: send_email"},
                ], f"got {got!r}"
        ''',
        "solution": r'''
            import re
            from dataclasses import dataclass

            CALL_RE = re.compile(r"^\s*CALL\s+(\w+)\((.*)\)\s*$", re.MULTILINE)
            ARG_RE = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|(-?\d+))')


            @dataclass
            class ToolCall:
                name: str
                args: dict


            def parse_calls(text):
                calls = []
                for match in CALL_RE.finditer(text):
                    args = {}
                    for key, string_value, int_value in ARG_RE.findall(match.group(2)):
                        args[key] = string_value if int_value == "" else int(int_value)
                    calls.append(ToolCall(match.group(1), args))
                return calls


            def dispatch(text, tools):
                results = []
                for call in parse_calls(text):
                    tool = tools.get(call.name)
                    if tool is None:
                        results.append({"error": f"unknown tool: {call.name}"})
                        continue
                    try:
                        results.append(tool(**call.args))
                    except TypeError:
                        results.append({"error": f"bad arguments for {call.name}"})
                return results
        ''',
        "hints": [
            'Use `@dataclass` for ToolCall, `re.finditer()` with the `re.MULTILINE` flag to find call lines, a second regex with `re.findall()` for the key=value arguments, and a dict lookup plus `try`/`except TypeError` for dispatch.',
            'Stage 1: a line regex that matches start of line, optional spaces, CALL, the name, and the text inside the parentheses at the end of the line. Stage 2: for each match, scan the inside text with an argument regex that captures the key and either a quoted string or an integer, converting integers with int(). Stage 3: dispatch loops over the parsed calls, looks the tool up, and calls it with the args as keyword arguments, recording an error dict when the tool is missing or the call raises TypeError.',
            '1) Define `ToolCall` with `name: str` and `args: dict`. 2) Line pattern: `^`, `\\s*`, `CALL`, `\\s+`, a captured `\\w+` name, a literal `(`, a captured `.*` body, a literal `)`, `\\s*`, `$` - use `re.MULTILINE` so `^` and `$` work per line (a call in the middle of a sentence will not match). 3) Argument pattern: captured `\\w+` key, `=` with optional spaces, then either a quoted `"([^"]*)"` or `(-?\\d+)`. 4) `findall()` gives (key, string, integer) tuples; if the integer part is not empty use `int()` on it, otherwise use the string. 5) Append a `ToolCall(name, args)` for each line and return the list. 6) In `dispatch`, loop over `parse_calls(text)`; get the tool with `tools.get(name)`; if it is `None`, append the unknown-tool error dict and `continue`. 7) Otherwise `try` calling `tool(**call.args)` and append the result; `except TypeError` append the bad-arguments error dict. 8) Return the results list.',
        ],
    },
    {
        "id": "combo-14",
        "title": "Tiny search index",
        "difficulty": 3,
        "topics": ["vectors", "files", "json", "classes"],
        "prompt": r'''
            Build a tiny keyword search engine. Write a class `TinyIndex`:

            - `TinyIndex()` - empty index.
            - `add(doc_id, text)` - add or replace a document.
            - `vocab` - a **property**: sorted list of unique tokens across all documents.
              Tokens: lowercase, split on whitespace, strip `.,!?;:"'()` from both ends,
              drop empty tokens.
            - `search(query, k=3)` - build bag-of-words count vectors over the current
              `vocab` for every document and for the query; score by cosine similarity
              (a zero vector scores `0.0`). Return up to `k` `(doc_id, score)` tuples with
              score > 0, highest first, ties by `doc_id` ascending.
            - `save(path)` - write `{"docs": {doc_id: text, ...}}` as JSON.
            - `TinyIndex.load(path)` - **classmethod** that rebuilds an index from such a file.
            - `TinyIndex.from_folder(folder)` - **classmethod** that indexes every `.txt` file
              in `folder`; the doc id is the file name without `.txt`.

            ```python
            index = TinyIndex.from_folder("docs")
            index.search("reset password", k=2)
            # [("account", 0.5669...)]
            ```
        ''',
        "starter": r'''
            import json
            import math
            import os


            class TinyIndex:
                ...
        ''',
        "setup_files": {
            "docs/account.txt": "To reset your password, open Settings and choose Account. Password resets expire.",
            "docs/billing.txt": "Billing questions: invoices are emailed monthly. Update your card in Settings.",
            "docs/api.txt": "Use your API key in the Authorization header. Rotate the key if leaked.",
            "docs/notes.md": "password password password - not a txt file",
        },
        "tests": r'''
            import json
            import math
            from solution import TinyIndex

            def test_vocab_property():
                idx = TinyIndex()
                idx.add("a", "Hello, World! hello")
                idx.add("b", "(world) peace.")
                assert idx.vocab == ["hello", "peace", "world"], f"vocab was {idx.vocab!r}"

            def test_search_scores():
                idx = TinyIndex()
                idx.add("a", "cat cat dog")
                idx.add("b", "dog bird")
                idx.add("c", "fish")
                got = idx.search("cat dog", k=5)
                assert [d for d, _ in got] == ["a", "b"], f"got {got!r} (zero scores must be excluded)"
                assert math.isclose(got[0][1], 3 / math.sqrt(10)), f"score for a was {got[0][1]!r}"
                assert math.isclose(got[1][1], 0.5), f"score for b was {got[1][1]!r}"

            def test_k_limit_ties_and_unknown_query():
                idx = TinyIndex()
                idx.add("z", "rag")
                idx.add("y", "rag")
                idx.add("x", "other")
                got = idx.search("RAG!", k=1)
                assert [d for d, _ in got] == ["y"], f"got {got!r}"
                assert idx.search("unicorn") == []

            def test_add_replaces_document():
                idx = TinyIndex()
                idx.add("a", "old words")
                idx.add("a", "new text")
                assert idx.vocab == ["new", "text"], f"vocab was {idx.vocab!r}"

            def test_from_folder_only_txt():
                idx = TinyIndex.from_folder("docs")
                got = idx.search("reset password", k=3)
                assert got and got[0][0] == "account", f"got {got!r}"
                assert all(d in {"account", "billing", "api"} for d, _ in idx.search("password settings key", k=10))

            def test_save_and_load(tmp="index.json"):
                idx = TinyIndex.from_folder("docs")
                idx.save(tmp)
                with open(tmp) as fh:
                    data = json.load(fh)
                assert set(data["docs"]) == {"account", "billing", "api"}, f"saved {data!r}"
                restored = TinyIndex.load(tmp)
                assert isinstance(restored, TinyIndex)
                assert restored.search("api key", k=2) == idx.search("api key", k=2)
        ''',
        "solution": r'''
            import json
            import math
            import os

            PUNCT = ".,!?;:\"'()"


            def tokenize(text):
                tokens = (t.strip(PUNCT) for t in text.lower().split())
                return [t for t in tokens if t]


            def cosine(a, b):
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(y * y for y in b))
                if na == 0 or nb == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (na * nb)


            class TinyIndex:
                def __init__(self):
                    self.docs = {}

                def add(self, doc_id, text):
                    self.docs[doc_id] = text

                @property
                def vocab(self):
                    return sorted({t for text in self.docs.values() for t in tokenize(text)})

                def _vector(self, text, vocab):
                    tokens = tokenize(text)
                    return [tokens.count(word) for word in vocab]

                def search(self, query, k=3):
                    vocab = self.vocab
                    q = self._vector(query, vocab)
                    scored = []
                    for doc_id, text in self.docs.items():
                        score = cosine(q, self._vector(text, vocab))
                        if score > 0:
                            scored.append((doc_id, score))
                    scored.sort(key=lambda item: (-item[1], item[0]))
                    return scored[:k]

                def save(self, path):
                    with open(path, "w", encoding="utf-8") as fh:
                        json.dump({"docs": self.docs}, fh)

                @classmethod
                def load(cls, path):
                    with open(path, encoding="utf-8") as fh:
                        data = json.load(fh)
                    index = cls()
                    for doc_id, text in data["docs"].items():
                        index.add(doc_id, text)
                    return index

                @classmethod
                def from_folder(cls, folder):
                    index = cls()
                    for name in sorted(os.listdir(folder)):
                        if name.endswith(".txt"):
                            with open(os.path.join(folder, name), encoding="utf-8") as fh:
                                index.add(name[:-4], fh.read())
                    return index
        ''',
        "hints": [
            'Write two small helpers first: a tokenizer (lowercase, split, strip punctuation, drop empties) and a cosine similarity function using `math.sqrt()`. The class just stores a dict of doc_id -> text; use `@property` and `@classmethod`, plus `json` and `os.listdir()`.',
            'Stage 1: `add` stores the text in a dict (same id replaces it); `vocab` collects all tokens from all docs into a sorted list. Stage 2: `search` turns the query and every document into count vectors over the vocab, scores each with cosine, keeps scores above 0, sorts and takes k. Stage 3: `save`/`load` write and read `{"docs": ...}` as JSON. Stage 4: `from_folder` reads each `.txt` file in the folder and adds it with the file name minus `.txt` as id.',
            '1) tokenizer: `text.lower().split()`, `.strip()` each token with the punctuation string, keep non-empty tokens. 2) cosine(a, b): compute each vector\'s length as the square root of the sum of squares; if either is 0 return 0.0; otherwise return the dot product (use `zip()`) divided by the product of the lengths. 3) `__init__` makes `self.docs = {}`; `add` sets `self.docs[doc_id] = text`. 4) `vocab` property: a set of every token from every doc, passed to `sorted()`. 5) A vector for some text is, for each word in the vocab, how many times it appears in the text\'s tokens (`.count()`). 6) `search`: build the query vector, loop over the docs, score each, keep `(doc_id, score)` when score > 0, sort with key `(-score, doc_id)`, return the first k. 7) `save`: `json.dump({"docs": self.docs}, fh)` inside a `with open(path, "w")`. 8) `load` classmethod: `json.load()` the file, make `cls()`, `add()` each doc, return it. 9) `from_folder` classmethod: loop over `os.listdir(folder)`, keep names ending in `.txt`, read each with `open(os.path.join(folder, name))`, and add it under `name[:-4]`.',
        ],
    },
]
