TOPIC = {
    "id": "dicts",
    "title": "Dictionaries",
    "track": "foundations",
    "order": 7,
    "requires": ["lists", "loops"],
    "summary": """
        Key-value mappings: safe access with defaults, merging, iterating over items,
        counting and grouping, nested API-response-like structures, and deleting keys.
    """,
    "concepts": ["key access", "get with default", "update", "merge operator |", "items()",
                 "counting", "grouping", "setdefault", "dict of lists", "nested dicts",
                 "del / pop", "copying nested data"],
}

LESSON = r'''
## Chapter notes: Dictionaries

A **dict** maps *keys* to *values*: `msg = {"role": "user", "content": "hi"}`.
`{}` is the empty dict. Keys are usually strings; values can be anything (lists, dicts...).
Dicts remember insertion order.

**Read / write**
- `msg["role"]` - the value, or `KeyError` if the key is missing.
- `msg.get("name")` - the value, or `None` if missing. `msg.get("name", "anon")` - your default.
- `msg["role"] = "assistant"` - change an existing key, or add a new one.
- `"role" in msg` - does the key exist? (checks keys, not values). `len(msg)` - number of pairs.

**Loop**
- `for key in d:` - keys. `for value in d.values():` - values.
- `for key, value in d.items():` - both (`for k, v in d:` does *not* work).

**Patterns**
- Count: `counts[x] = counts.get(x, 0) + 1`
- Group: `groups.setdefault(key, []).append(item)` (or `if key not in groups: groups[key] = []`)
- Nested data (API responses): chain lookups outside-in:
  `response["choices"][0]["message"]["content"]`

**Merge, copy, delete**
- `a | b` - new dict with both; on shared keys `b` wins. `a.update(b)` - same, in place.
- `d.copy()` - new dict (shallow: nested dicts/lists are still shared).
- `del d[key]` - remove (`KeyError` if missing). `d.pop(key)` - remove and return the value;
  `d.pop(key, None)` - no error when missing.

**Gotchas**
- `config[model]` looks up the *variable* `model`; you meant `config["model"]`.
- `.get(key) or default` replaces falsy values like `0`; `.get(key, default)` doesn't.
- `b = a` doesn't copy - it's the same dict with two names.
- Don't add or remove keys while looping over the same dict.

Docs: [Dictionaries tutorial](https://docs.python.org/3/tutorial/datastructures.html#dictionaries),
[dict methods](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict).
'''

EXERCISES = [
    {
        "id": "dicts-s1",
        "lesson": r'''
            ## A coat check

            At a coat check you hand over your coat and get a ticket. Later you give the
            ticket back and get *your* coat - nobody cares which hook it's on. A **dictionary**
            works the same way: you store a value under a *key* (the ticket), and look it up by
            that key - not by position like a list.

            ```python
            config = {"model": "gpt-4o", "temperature": 0.7}
            print(config["model"])
            config["max_tokens"] = 256
            print(len(config))
            print(config.get("stream"))
            print(config.get("stream", False))
            ```

            - Curly braces, `key: value` pairs, commas between pairs.
            - `config["model"]` reads the value stored under the key `"model"`.
            - Assigning to a new key adds a pair; `len` counts the pairs.
            - `.get(key)` is a polite lookup: a missing key gives `None` (or the default you
              pass) instead of crashing.

            Vocabulary: a *dict* (dictionary) holds *key-value pairs*. It is also called a
            *mapping*. Almost all AI API data - messages, configs, JSON responses - is dicts.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            config = {"model": "gpt-4o", "temperature": 0.7}
            print(config["model"])
            config["max_tokens"] = 256
            print(len(config))
            print(config.get("stream"))
            print(config.get("stream", False))
        ''',
        "solution": r'''
            gpt-4o
            3
            None
            False
        ''',
        "explanation": r'''
            `config["model"]` looks up the value for the key `"model"`. Assigning to a new
            key adds it, so the dict now has 3 pairs. `"stream"` is not a key: `.get()`
            returns `None`, or the default you pass (`False`).
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Square brackets with a key give that key's value; len counts key-value pairs.",
            "Track the dict: one key is added before len is called. .get on a missing key never crashes.",
            "Line 1 is the model value. Line 2 counts 3 keys. Line 3: .get with no default gives None. Line 4: it gives the default you passed.",
        ],
    },
    {
        "id": "dicts-s2",
        "lesson": r'''
            ## Looking up by key

            Remember the coat check: to get the coat back, you hand over the exact ticket.
            To read a value, put its key in square brackets after the dict:

            ```python
            config = {"temperature": 0, "model": "claude"}
            print(config["model"])
            key = "temperature"
            print(config[key])
            ```

            The order of the pairs doesn't matter for lookups: `"model"` is found wherever it
            sits. The key can be written directly (`config["model"]`) or come from a variable
            (`config[key]`).

            Vocabulary: this is *subscripting* the dict with a key, the same square-bracket
            syntax as list indexing, but with a key instead of a position.

            **Watch out:** a string key needs its quotes. `config[model]` (no quotes) looks up
            whatever is in the *variable* `model` - and fails with `NameError` if there is no
            such variable.
        ''',
        "title": "Read the model name",
        "difficulty": 0,
        "prompt": r'''
            Read one setting out of a model config. The function is almost done: replace
            the `___`.

            **Write:** `get_model(config)`

            - `config`: a dict that always has a `"model"` key, e.g.
              `{"model": "gpt-4o", "temperature": 0.7}`
            - **Returns:** the value stored under the key `"model"` (a string)

            **Rules**
            - The `"model"` key can be anywhere in the dict, not only first.

            **Examples**
            ```python
            get_model({"model": "gpt-4o", "temperature": 0.7})   # returns "gpt-4o"
            get_model({"temperature": 0, "model": "claude"})     # returns "claude"
            ```
        ''',
        "starter": r'''
            def get_model(config):
                return config[___]
        ''',
        "tests": r'''
            from solution import get_model

            def test_returns_model_value_gpt_4o():
                got = get_model({"model": "gpt-4o", "temperature": 0.7})
                assert got == "gpt-4o", f"got {got!r}"

            def test_returns_model_value_when_not_first_key():
                got = get_model({"temperature": 0, "model": "claude"})
                assert got == "claude", f"got {got!r}"
        ''',
        "solution": r'''
            def get_model(config):
                return config["model"]
        ''',
        "hints": [
            "A dict value is read with square brackets and its key.",
            "The key is a string, so it needs quotes.",
            "Replace ___ with \"model\" (including the quotes).",
        ],
    },
    {
        "id": "dicts-s4",
        "lesson": r'''
            ## Building a dict

            A dict literal is like a paper form with labelled fields: the labels are fixed
            (`role`, `content`), and you write a different answer in each field every time.

            ```python
            role = "user"
            text = "What is RAG?"
            message = {"role": role, "content": text}
            print(message)
            print(message["content"])
            ```

            On the left of each colon is the **key** - here a fixed string in quotes. On the
            right is the **value** - here the value of a variable, so no quotes. Python prints
            dicts with single quotes: `{'role': 'user', 'content': 'What is RAG?'}`.

            Vocabulary: writing `{...}` directly in code is a *dict literal*. The
            `{"role": ..., "content": ...}` shape is the standard *chat message* format used by
            OpenAI, Anthropic and most other LLM APIs.

            **Watch out:** `{"role": "role"}` stores the word `role`, not the variable's value.
        ''',
        "title": "Make a chat message",
        "difficulty": 0,
        "prompt": r'''
            Chat APIs take each message as a dict with a role and some content.

            **Write:** `make_message(role, content)`

            - `role`: a string, e.g. `"user"` or `"system"`
            - `content`: a string, the message text, e.g. `"hi"`
            - **Returns:** a dict with exactly two keys, `"role"` and `"content"`, holding
              the two arguments

            **Rules**
            - The keys are the strings `"role"` and `"content"` (no other keys).

            **Examples**
            ```python
            make_message("user", "hi")            # returns {"role": "user", "content": "hi"}
            make_message("system", "Be brief.")   # returns {"role": "system", "content": "Be brief."}
            ```
        ''',
        "starter": r'''
            def make_message(role, content):
                ...
        ''',
        "tests": r'''
            from solution import make_message

            def test_user_message_dict():
                got = make_message("user", "hi")
                assert got == {"role": "user", "content": "hi"}, f"got {got!r}"

            def test_system_message_dict():
                got = make_message("system", "Be brief.")
                assert got == {"role": "system", "content": "Be brief."}, f"got {got!r}"
        ''',
        "solution": r'''
            def make_message(role, content):
                return {"role": role, "content": content}
        ''',
        "hints": [
            "A dict literal is written with curly braces and key: value pairs.",
            "The keys are the fixed strings role and content; the values are the parameters.",
            "Return {\"role\": role, \"content\": content} - quoted keys, unquoted parameter names as values.",
        ],
    },
    {
        "id": "dicts-s6",
        "lesson": r'''
            ## Adding and changing a key

            A whiteboard with labelled boxes: writing in an empty box fills it; writing in a
            box that already has something erases the old value first. Dict assignment works
            the same - the same line either **adds** a new key or **replaces** an existing one.

            ```python
            config = {"model": "gpt-4o"}
            config["max_tokens"] = 256
            print(config)
            config["max_tokens"] = 1024
            print(config)
            print(len(config))
            ```

            After the second assignment there is still only one `"max_tokens"` key - keys are
            unique, so the value was replaced, not added twice.

            Like `list.append`, this changes the dict **in place**: anyone else holding that
            same dict sees the change.

            Vocabulary: dicts are *mutable*; keys are *unique*.

            **Watch out:** no method is needed - just `d[key] = value`.
        ''',
        "title": "Set the token limit",
        "difficulty": 0,
        "prompt": r'''
            Before sending a request, an app sets the maximum number of tokens the model may
            generate.

            **Write:** `set_max_tokens(config, limit)`

            - `config`: a request config dict, e.g. `{"model": "gpt-4o"}`
            - `limit`: an int, e.g. `256`
            - **Returns:** the **same** `config` dict, after storing `limit` under the key
              `"max_tokens"`

            **Rules**
            - If `"max_tokens"` is missing, it is added; if it exists, its value is replaced.
            - All other keys stay as they are.
            - Change the dict you were given (in place) and return that same dict.

            **Examples**
            ```python
            set_max_tokens({"model": "gpt-4o"}, 256)
            # returns {"model": "gpt-4o", "max_tokens": 256}
            set_max_tokens({"model": "m", "max_tokens": 100}, 1024)
            # returns {"model": "m", "max_tokens": 1024}
            ```
        ''',
        "starter": r'''
            def set_max_tokens(config, limit):
                ...
        ''',
        "tests": r'''
            from solution import set_max_tokens

            def test_adds_missing_key():
                got = set_max_tokens({"model": "gpt-4o"}, 256)
                assert got == {"model": "gpt-4o", "max_tokens": 256}, f"got {got!r}"

            def test_replaces_existing_value():
                got = set_max_tokens({"model": "m", "max_tokens": 100}, 1024)
                assert got == {"model": "m", "max_tokens": 1024}, f"got {got!r}"

            def test_changes_and_returns_the_same_dict():
                config = {"model": "m"}
                got = set_max_tokens(config, 5)
                assert config.get("max_tokens") == 5, f"the dict you were given is {config!r}"
                assert got is config, "return the same dict you were given"
        ''',
        "solution": r'''
            def set_max_tokens(config, limit):
                config["max_tokens"] = limit
                return config
        ''',
        "hints": [
            "Assigning to d[key] adds the key, or replaces its value if it already exists.",
            "One line stores limit under the key max_tokens in config; a second line returns config.",
            "Write config[\"max_tokens\"] = limit, then return config.",
        ],
    },
    {
        "id": "dicts-s3",
        "lesson": r'''
            ## When a key might be missing

            Ask the coat check for a ticket that doesn't exist and the attendant shouts - in
            Python, that's a `KeyError` crash. Real API data often has optional keys, so you
            need a calmer way to ask:

            ```python
            config = {"model": "gpt-4o", "temperature": 0}
            print(config.get("temperature", 1.0))
            print(config.get("top_p", 1.0))
            print(config.get("top_p"))
            print("top_p" in config)
            ```

            - `.get(key, default)` returns the value if the key exists, otherwise the default.
            - Without a default, a missing key gives `None`.
            - `key in config` asks "does this key exist?" and answers `True`/`False`.

            Notice line 1 prints `0`: the key exists, so its value is used - even though it is
            zero.

            Vocabulary: the second argument is the *default value* (or *fallback*).

            **Watch out:** `config.get("temperature") or 1.0` looks similar but turns a real
            `0` into `1.0`. Use the default argument instead.
        ''',
        "title": "Fix the missing key crash",
        "difficulty": 0,
        "prompt": r'''
            Read the temperature from a model config, with a fallback. The starter crashes
            with `KeyError` when the key is missing. Fix the bug.

            **Write:** `get_temperature(config)`

            - `config`: a dict, e.g. `{"temperature": 0.2}` or `{"model": "gpt-4o"}`
            - **Returns:** the value under `"temperature"`, or `1.0` if that key is missing

            **Rules**
            - If the key is present, return its value as is - even when it is `0`.
            - If the key is missing, return `1.0` (don't crash).

            **Examples**
            ```python
            get_temperature({"temperature": 0.2})   # returns 0.2
            get_temperature({"temperature": 0})     # returns 0
            get_temperature({"model": "gpt-4o"})    # returns 1.0
            ```
        ''',
        "starter": r'''
            def get_temperature(config):
                return config["temperature"]
        ''',
        "tests": r'''
            from solution import get_temperature

            def test_present_key_returns_its_value():
                got = get_temperature({"temperature": 0.2})
                assert got == 0.2, f"got {got!r}"

            def test_zero_temperature_is_kept():
                got = get_temperature({"temperature": 0})
                assert got == 0, f"got {got!r}"

            def test_missing_key_returns_1_0():
                got = get_temperature({"model": "gpt-4o"})
                assert got == 1.0, f"got {got!r}"
        ''',
        "solution": r'''
            def get_temperature(config):
                return config.get("temperature", 1.0)
        ''',
        "hints": [
            "Square brackets crash on a missing key. Dicts have a method that does not.",
            "Use the method that takes a key and a default value to return when the key is missing.",
            "Return config.get(\"temperature\", 1.0) instead of the square-bracket lookup.",
        ],
    },
    {
        "id": "dicts-s5",
        "lesson": r'''
            ## Looping over a dict

            Reading down a two-column table - label on the left, value on the right - you see
            both at once. `.items()` gives you each key **and** its value together, so a `for`
            loop can unpack them into two names (like `enumerate` did).

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            for key, value in usage.items():
                print(f"{key}: {value}")
            for key in usage:
                print(key)
            print(list(usage.values()))
            ```

            - `for key, value in d.items():` - both.
            - `for key in d:` - just the keys.
            - `d.values()` - just the values.

            The pairs come out in the order they were added to the dict.

            Vocabulary: `.items()`, `.keys()` and `.values()` return *views* of the dict you
            can loop over.

            **Watch out:** `for key, value in usage:` (without `.items()`) fails - looping over
            a dict directly gives only keys.
        ''',
        "title": "Config as lines",
        "difficulty": 0,
        "prompt": r'''
            Turn a model config into printable lines, e.g. for a log file.

            **Write:** `config_lines(config)`

            - `config`: a dict, e.g. `{"model": "gpt-4o", "temperature": 0.7}`
            - **Returns:** a list of strings, one `"key=value"` string per key-value pair

            **Rules**
            - Each string is the key, then `=`, then the value - no spaces.
            - The strings are in the same order as the keys in the dict.
            - An empty dict gives an empty list `[]`.
            - Tip: loop over `config.items()` to get each key and value together.

            **Examples**
            ```python
            config_lines({"model": "gpt-4o", "temperature": 0.7})
            # returns ["model=gpt-4o", "temperature=0.7"]
            config_lines({"b": 1, "a": 2})   # returns ["b=1", "a=2"]
            config_lines({})                 # returns []
            ```
        ''',
        "starter": r'''
            def config_lines(config):
                ...
        ''',
        "tests": r'''
            from solution import config_lines

            def test_two_keys_give_two_key_equals_value_lines():
                got = config_lines({"model": "gpt-4o", "temperature": 0.7})
                assert got == ["model=gpt-4o", "temperature=0.7"], f"got {got!r}"

            def test_empty_dict_returns_empty_list():
                assert config_lines({}) == []

            def test_lines_follow_dict_key_order():
                got = config_lines({"b": 1, "a": 2})
                assert got == ["b=1", "a=2"], f"got {got!r}"
        ''',
        "solution": r'''
            def config_lines(config):
                lines = []
                for key, value in config.items():
                    lines.append(f"{key}={value}")
                return lines
        ''',
        "hints": [
            ".items() gives you each key and its value together in a for loop.",
            "Start an empty list, and for every pair add one f-string made of the key, an equals sign and the value.",
            "Set lines = []. Loop for key, value in config.items(): append f\"{key}={value}\". Return lines after the loop.",
        ],
    },
    {
        "id": "dicts-7",
        "lesson": r'''
            ## Digging into nested data

            Russian dolls: to reach the smallest one you open them from the outside in, one at
            a time. API responses are nested the same way - dicts inside lists inside dicts -
            and you reach a value by chaining lookups, outermost first.

            ```python
            response = {
                "choices": [{"message": {"role": "assistant", "content": "Paris."}}],
            }
            choices = response["choices"]
            first = choices[0]
            print(first["message"]["content"])
            print(response["choices"][0]["message"]["role"])
            ```

            Read the last line left to right: the `"choices"` list, its item `0` (a dict), that
            dict's `"message"` (another dict), and finally its `"role"`. Each step gives you a
            value, and the next bracket looks inside that value.

            Vocabulary: this is *nested data*, and following it step by step is sometimes
            called *drilling down*.

            **Watch out:** `[0]` is for lists (positions), `["key"]` for dicts. When a chain
            fails, split it into steps with `print` to see which level is wrong.
        ''',
        "title": "Reply text from a response",
        "difficulty": 1,
        "prompt": r'''
            A chat-completion API returns nested data. You need the text of the reply.

            ```python
            response = {
                "id": "resp_1",
                "choices": [
                    {"message": {"role": "assistant", "content": "Paris."}, "finish_reason": "stop"},
                ],
            }
            ```

            **Write:** `reply_text(response)`

            - `response`: a dict shaped like the one above. It always has a `"choices"` list
              with at least one item, and each item has a `"message"` dict with a `"content"`.
            - **Returns:** the `"content"` string of the message in the **first** choice

            **Rules**
            - If there are several choices, use only the first one.
            - Don't change the response.

            **Examples**
            ```python
            reply_text(response)   # returns "Paris."
            reply_text({"choices": [{"message": {"content": "A"}}, {"message": {"content": "B"}}]})
            # returns "A"
            ```
        ''',
        "starter": r'''
            def reply_text(response):
                ...
        ''',
        "tests": r'''
            from solution import reply_text

            def resp(*texts):
                return {"id": "r", "choices": [{"message": {"role": "assistant", "content": t},
                                                "finish_reason": "stop"} for t in texts]}

            def test_returns_content_of_the_reply():
                got = reply_text(resp("Paris."))
                assert got == "Paris.", f"got {got!r}"

            def test_uses_only_the_first_choice():
                got = reply_text(resp("A", "B"))
                assert got == "A", f"got {got!r}"

            def test_empty_content_is_returned_as_is():
                got = reply_text(resp(""))
                assert got == "", f"got {got!r}"

            def test_response_not_modified():
                r = resp("x")
                reply_text(r)
                assert r == resp("x"), "the response was modified"
        ''',
        "solution": r'''
            def reply_text(response):
                return response["choices"][0]["message"]["content"]
        ''',
        "hints": [
            "Chain lookups from the outside in: a key, then a list position, then keys again.",
            "Get the choices list, take its first item, then that item's message, then the message's content.",
            "Return response[\"choices\"][0][\"message\"][\"content\"].",
        ],
    },
    {
        "id": "dicts-1",
        "lesson": r'''
            ## Merging two dicts

            A form comes pre-filled with sensible defaults; the user changes a couple of fields.
            The final form is "defaults, but with the user's answers on top". For dicts, the
            `|` operator does exactly that - and builds a **new** dict:

            ```python
            defaults = {"model": "gpt-4o-mini", "temperature": 0.7}
            user = {"temperature": 0, "stream": True}
            request = defaults | user
            print(request)
            print(defaults)
            ```

            - Keys only in one side are kept.
            - Keys in both sides take the value from the **right-hand** dict.
            - Neither `defaults` nor `user` is changed.

            Vocabulary: `|` is the *merge operator* (read it as "defaults, updated with user").
            Its in-place cousin is `d.update(other)`, which changes `d` itself.

            **Watch out:** if you call `defaults.update(...)`, you change the shared defaults
            for every later caller. Prefer `|` when you want a fresh dict.
        ''',
        "hints": [
            'There is an operator that merges two dicts into a brand-new one.',
            'Merge the defaults with the overrides so that the overrides win on shared keys, without changing either dict.',
            'Return DEFAULTS | overrides - the right-hand dict wins and a new dict is created. (A copy of DEFAULTS followed by .update(overrides) also works.)',
        ],
        "title": "Request defaults",
        "difficulty": 1,
        "prompt": r'''
            An API request starts from default settings, and the caller can override some
            of them. The starter already defines:

            ```python
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}
            ```

            **Write:** `build_request(overrides)`

            - `overrides`: a dict of settings to change or add, e.g. `{"temperature": 0}`
            - **Returns:** a **new** dict: all of `DEFAULTS`, with the `overrides` applied

            **Rules**
            - A key in `overrides` replaces the default value, even when the new value is
              `0`, `False` or another "empty" value.
            - Keys in `overrides` that are not in `DEFAULTS` are added to the result.
            - `overrides={}` returns a dict equal to `DEFAULTS`.
            - Don't modify `DEFAULTS`: a later call must still see the original defaults.
            - Don't modify the `overrides` dict you were given.

            **Examples**
            ```python
            build_request({"temperature": 0})
            # returns {"model": "gpt-4o-mini", "temperature": 0, "max_tokens": 256}
            build_request({"stream": True})
            # returns {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256, "stream": True}
            build_request({})
            # returns {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}
            ```
        ''',
        "starter": r'''
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}


            def build_request(overrides):
                ...
        ''',
        "tests": r'''
            from solution import build_request

            def test_empty_overrides_return_the_defaults():
                got = build_request({})
                assert got == {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}, f"got {got!r}"

            def test_override_wins_even_when_falsy():
                got = build_request({"temperature": 0})
                assert got["temperature"] == 0, f"got {got!r}"
                assert got["model"] == "gpt-4o-mini" and got["max_tokens"] == 256, f"got {got!r}"

            def test_extra_override_keys_are_added():
                got = build_request({"stream": True})
                assert got.get("stream") is True and len(got) == 4, f"got {got!r}"

            def test_defaults_not_modified_between_calls():
                build_request({"model": "gpt-4o", "stream": True})
                got = build_request({})
                assert got == {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}, (
                    f"an earlier call leaked into the defaults: {got!r}")

            def test_overrides_dict_not_modified():
                overrides = {"model": "gpt-4o"}
                build_request(overrides)
                assert overrides == {"model": "gpt-4o"}, f"overrides changed to {overrides!r}"
        ''',
        "solution": r'''
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}


            def build_request(overrides):
                return DEFAULTS | overrides
        ''',
    },
    {
        "id": "dicts-8",
        "lesson": r'''
            ## Removing a key (and reading the docs)

            Before logging a request, you strip out secrets like the API key - but on a
            **copy**, so the real request still has it. Remember the two name tags on one box
            from the lists chapter? Dicts work the same way: `b = a` is not a copy, `a.copy()`
            is.

            ```python
            config = {"model": "gpt-4o", "api_key": "sk-123"}
            safe = config.copy()
            del safe["api_key"]
            print(safe)
            print(config)
            ```

            `del d[key]` removes a key - but, like `d[key]`, it crashes with `KeyError` when the
            key isn't there.

            Dicts have a method that removes a key and can be told what to do when it's
            missing, **without crashing**. Open the dict methods in the Python docs (linked
            above), find it, and read what its second argument does.

            Vocabulary: `.copy()` makes a *shallow copy* - a new outer dict, while nested
            values are still shared. That's fine for flat configs like this one.
        ''',
        "title": "Strip a secret before logging",
        "difficulty": 1,
        "research": {
            "note": "Dicts have a method that removes a key and can return a default instead of raising `KeyError` when the key is missing. Find it in the dict methods list, read what its second argument does, then come back.",
            "links": [
                {"title": "Mapping types - dict (Python docs)",
                 "url": "https://docs.python.org/3/library/stdtypes.html#mapping-types-dict"},
            ],
        },
        "prompt": r'''
            Request configs are logged for debugging, but secrets such as API keys must never
            end up in the logs.

            **Write:** `without_key(config, key)`

            - `config`: a flat dict, e.g. `{"model": "gpt-4o", "api_key": "sk-123"}`
            - `key`: the key to leave out, a string, e.g. `"api_key"`
            - **Returns:** a **new** dict with every pair of `config` except `key`

            **Rules**
            - If `key` is not in `config`, return a copy equal to `config` (no error).
            - Don't change the dict you were given - the real request still needs its key.
            - Always return a new dict object, even when nothing was removed.

            **Examples**
            ```python
            without_key({"model": "gpt-4o", "api_key": "sk-123"}, "api_key")
            # returns {"model": "gpt-4o"}
            without_key({"model": "gpt-4o"}, "api_key")
            # returns {"model": "gpt-4o"}
            without_key({}, "api_key")   # returns {}
            ```
        ''',
        "starter": r'''
            def without_key(config, key):
                ...
        ''',
        "tests": r'''
            from solution import without_key

            def test_removes_the_key():
                got = without_key({"model": "gpt-4o", "api_key": "sk-123"}, "api_key")
                assert got == {"model": "gpt-4o"}, f"got {got!r}"

            def test_missing_key_is_not_an_error():
                got = without_key({"model": "gpt-4o"}, "api_key")
                assert got == {"model": "gpt-4o"}, f"got {got!r}"
                assert without_key({}, "api_key") == {}

            def test_original_dict_keeps_its_key():
                config = {"model": "m", "api_key": "sk-1"}
                without_key(config, "api_key")
                assert config == {"model": "m", "api_key": "sk-1"}, f"the input changed to {config!r}"

            def test_returns_a_new_dict():
                config = {"model": "m"}
                got = without_key(config, "api_key")
                assert got is not config, "return a new dict, not the one you were given"
        ''',
        "solution": r'''
            def without_key(config, key):
                clean = config.copy()
                clean.pop(key, None)
                return clean
        ''',
        "hints": [
            "Work on a copy of the dict, and look for a removing method that accepts a default.",
            "Copy config first. Then remove key from the copy in a way that does nothing when the key is missing. Return the copy.",
            "clean = config.copy(); call clean.pop(key, None) - the None default avoids the KeyError; return clean.",
        ],
    },
    {
        "id": "dicts-2",
        "lesson": r'''
            ## Counting with a dict

            A tally sheet: each time you see a name, you find its row and add a mark. If the
            name has no row yet, you start one at zero first. With a dict, `.get(key, 0)`
            handles the "no row yet" case in one step:

            ```python
            tools_called = ["search", "weather", "search"]
            counts = {}
            for tool in tools_called:
                counts[tool] = counts.get(tool, 0) + 1
            print(counts)
            ```

            Each round: read the current count (`0` if the tool is new), add 1, store it back.
            The first `"search"` creates the key with 1; the second makes it 2.

            Vocabulary: this is the *counting pattern* (a dict of *counters*). It's an
            accumulator, just like `total = 0` in the loops chapter - only now there is one
            accumulator per key.

            **Watch out:** `counts[tool] += 1` crashes the first time a tool is seen, because
            the key doesn't exist yet.
        ''',
        "hints": [
            'This is the counting pattern from the lesson: an empty dict plus .get(key, 0) + 1.',
            "Go through the messages; for each one, read its role and add 1 to that role's count.",
            'Set counts = {}. For each message: role = message["role"]; counts[role] = counts.get(role, 0) + 1. Return counts after the loop.',
        ],
        "title": "Count roles",
        "difficulty": 1,
        "prompt": r'''
            Count who said what in a chat history.

            **Write:** `count_roles(messages)`

            - `messages`: a list of message dicts like `{"role": "user", "content": "hi"}`
            - **Returns:** a dict mapping each role (string) to how many messages have that
              role (int), e.g. `{"system": 1, "user": 2}`

            **Rules**
            - Only roles that actually appear are keys - any role string counts (not only
              `"system"`, `"user"`, `"assistant"`).
            - An empty list returns `{}`.

            **Examples**
            ```python
            count_roles([
                {"role": "system", "content": "..."},
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
                {"role": "user", "content": "thanks"},
            ])
            # returns {"system": 1, "user": 2, "assistant": 1}
            count_roles([{"role": "tool", "content": "42"}])   # returns {"tool": 1}
            count_roles([])                                    # returns {}
            ```
        ''',
        "starter": r'''
            def count_roles(messages):
                ...
        ''',
        "tests": r'''
            from solution import count_roles

            def m(role):
                return {"role": role, "content": "x"}

            def test_counts_each_role_in_mixed_chat():
                got = count_roles([m("system"), m("user"), m("assistant"), m("user")])
                assert got == {"system": 1, "user": 2, "assistant": 1}, f"got {got!r}"

            def test_empty_list_returns_empty_dict():
                got = count_roles([])
                assert got == {}, f"got {got!r}"

            def test_five_user_messages_count_five():
                got = count_roles([m("user")] * 5)
                assert got == {"user": 5}, f"got {got!r}"

            def test_any_role_name_is_counted():
                got = count_roles([m("tool")])
                assert got == {"tool": 1}, f"got {got!r}"
        ''',
        "solution": r'''
            def count_roles(messages):
                counts = {}
                for message in messages:
                    role = message["role"]
                    counts[role] = counts.get(role, 0) + 1
                return counts
        ''',
    },
    {
        "id": "dicts-3",
        "hints": [
            'Use .get() with a default for every part that might be missing, and chain lookups for nested data.',
            'Get the choices list (empty if missing); if it has items, read text and finish_reason from the first. Get the usage dict (empty if missing) and add both counts with a default of 0.',
            'choices = response.get("choices") or []. Start text and finish_reason as None; if choices, read choices[0]["message"]["content"] and choices[0]["finish_reason"]. usage = response.get("usage", {}); total = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0). Return the three-key dict.',
        ],
        "title": "Read an API response",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A chat-completion API returns nested data like this:

            ```python
            response = {
                "id": "resp_123",
                "choices": [
                    {"message": {"role": "assistant", "content": "Paris."},
                     "finish_reason": "stop"},
                ],
                "usage": {"prompt_tokens": 12, "completion_tokens": 3},
            }
            ```

            **Write:** `summarize(response)`

            - `response`: a dict shaped like the one above (parts may be missing, see Rules)
            - **Returns:** a new dict with exactly three keys:
              `{"text": ..., "finish_reason": ..., "total_tokens": ...}`

            **Rules**
            - `"text"` is the `"content"` of the `"message"` of the **first** choice, and
              `"finish_reason"` is that first choice's `"finish_reason"`. Ignore any other
              choices.
            - If the `"choices"` key is missing, or the list is empty, both `"text"` and
              `"finish_reason"` are `None`.
            - `"total_tokens"` is `"prompt_tokens"` + `"completion_tokens"` from `"usage"`.
            - If the `"usage"` key is missing, `"total_tokens"` is `0`. If only one of the two
              counts is missing, count the missing one as `0`.
            - Don't modify the `response` dict you were given.

            **Examples**
            ```python
            summarize(response)
            # returns {"text": "Paris.", "finish_reason": "stop", "total_tokens": 15}
            summarize({"id": "x", "choices": []})
            # returns {"text": None, "finish_reason": None, "total_tokens": 0}
            summarize({"id": "x", "usage": {"prompt_tokens": 4, "completion_tokens": 0}})
            # returns {"text": None, "finish_reason": None, "total_tokens": 4}
            ```
        ''',
        "starter": r'''
            def summarize(response):
                ...
        ''',
        "tests": r'''
            from solution import summarize

            def full():
                return {
                    "id": "resp_123",
                    "choices": [
                        {"message": {"role": "assistant", "content": "Paris."}, "finish_reason": "stop"},
                        {"message": {"role": "assistant", "content": "Lyon."}, "finish_reason": "length"},
                    ],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 3},
                }

            def test_full_response_uses_first_choice_and_sums_tokens():
                got = summarize(full())
                assert got == {"text": "Paris.", "finish_reason": "stop", "total_tokens": 15}, f"got {got!r}"

            def test_empty_choices_and_no_usage_give_none_and_zero():
                got = summarize({"id": "x", "choices": []})
                assert got == {"text": None, "finish_reason": None, "total_tokens": 0}, f"got {got!r}"

            def test_missing_choices_key_gives_none():
                got = summarize({"id": "x", "usage": {"prompt_tokens": 4, "completion_tokens": 0}})
                assert got == {"text": None, "finish_reason": None, "total_tokens": 4}, f"got {got!r}"

            def test_missing_completion_tokens_counts_as_zero():
                r = full()
                del r["usage"]["completion_tokens"]
                got = summarize(r)
                assert got["total_tokens"] == 12, f"got {got!r}"

            def test_response_dict_not_modified():
                r = full()
                summarize(r)
                assert r == full(), "the response dict was modified"
        ''',
        "solution": r'''
            def summarize(response):
                choices = response.get("choices") or []
                text = finish_reason = None
                if choices:
                    first = choices[0]
                    text = first["message"]["content"]
                    finish_reason = first["finish_reason"]
                usage = response.get("usage", {})
                total = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                return {"text": text, "finish_reason": finish_reason, "total_tokens": total}
        ''',
    },
    {
        "id": "dicts-4",
        "hints": [
            'Build a dict of lists: one list per source, created the first time the source is seen.',
            "For each chunk, make sure its source has a list in the result, then append the chunk's text to that list.",
            'groups = {}. For each chunk: if the source is not in groups, set groups[source] = []. Then append chunk["text"] to groups[source]. (.setdefault(source, []) does both in one call.) Return groups.',
        ],
        "title": "Group chunks by source",
        "difficulty": 2,
        "prompt": r'''
            In a RAG app, retrieved chunks arrive as one flat list. Group them by the
            document they came from.

            **Write:** `group_by_source(chunks)`

            - `chunks`: a list of dicts like `{"source": "a.pdf", "text": "intro"}`
            - **Returns:** a dict mapping each source (string) to a **list of its texts**

            **Rules**
            - Inside each list, texts keep the order they had in `chunks`.
            - The keys are in order of first appearance in `chunks`.
            - Duplicate texts are kept (not removed).
            - Each source gets its own separate list: appending to one source's list must
              not change another's.
            - An empty list returns `{}`.

            **Examples**
            ```python
            group_by_source([
                {"source": "a.pdf", "text": "intro"},
                {"source": "b.md", "text": "setup"},
                {"source": "a.pdf", "text": "details"},
            ])
            # returns {"a.pdf": ["intro", "details"], "b.md": ["setup"]}
            group_by_source([
                {"source": "a", "text": "same"},
                {"source": "a", "text": "same"},
            ])
            # returns {"a": ["same", "same"]}
            group_by_source([])   # returns {}
            ```
        ''',
        "starter": r'''
            def group_by_source(chunks):
                ...
        ''',
        "tests": r'''
            from solution import group_by_source

            def c(source, text):
                return {"source": source, "text": text}

            def test_texts_grouped_by_source_in_order():
                got = group_by_source([c("a.pdf", "intro"), c("b.md", "setup"), c("a.pdf", "details")])
                assert got == {"a.pdf": ["intro", "details"], "b.md": ["setup"]}, f"got {got!r}"

            def test_key_order_is_first_appearance():
                got = group_by_source([c("z", "1"), c("a", "2"), c("z", "3")])
                assert list(got) == ["z", "a"], f"keys in order {list(got)!r}"

            def test_empty_list_returns_empty_dict():
                assert group_by_source([]) == {}

            def test_each_source_has_its_own_list():
                got = group_by_source([c("a", "1"), c("b", "2")])
                got["a"].append("x")
                assert got["b"] == ["2"], "the lists for different sources are the same object"

            def test_duplicate_texts_kept():
                got = group_by_source([c("a", "same"), c("a", "same")])
                assert got == {"a": ["same", "same"]}, f"got {got!r}"
        ''',
        "solution": r'''
            def group_by_source(chunks):
                groups = {}
                for chunk in chunks:
                    groups.setdefault(chunk["source"], []).append(chunk["text"])
                return groups
        ''',
    },
    {
        "id": "dicts-5",
        "hints": [
            "Loop over override.items(). isinstance(value, dict) tells you when a value is a nested section. Copy nested dicts with .copy() so the inputs are never shared.",
            "Start from a copy of base where every nested dict is copied too. Then for each override key: None removes; a dict merged into an existing dict updates that section key by key (None inside removes there too); anything else replaces.",
            "result = {}; copy each base value into it (use value.copy() for dicts). For key, value in override.items(): if value is None, result.pop(key, None). Elif value is a dict and result.get(key) is a dict: loop over value.items() and set or pop (for None) inside result[key]. Elif value is a dict: store a copy without its None values. Else result[key] = value. Return result.",
        ],
        "title": "Merge configs",
        "difficulty": 3,
        "prompt": r'''
            Combine a base model config with a user's overrides. Configs have **at most two
            levels**: each top-level value is either a plain value or a dict of plain values
            (called a "section", e.g. `"params"`).

            **Write:** `merge_config(base, override)`

            - `base`: a config dict, e.g. `{"model": "gpt-4o", "params": {"temperature": 0.7}}`
            - `override`: a config dict with changes, e.g. `{"params": {"temperature": 0.2}}`
            - **Returns:** a **new** merged config dict

            **Rules**
            - Keys that are only in `base` or only in `override` are kept.
            - If a key's value is a dict in **both**, merge the two sections key by key
              (the `override` section's values win; other section keys are kept).
            - Otherwise the `override` value replaces the `base` value - this includes a
              plain value replacing a section, and a section replacing a plain value.
            - An `override` value of `None` **removes** that key from the result, at the top
              level or inside a section. A `None` key that isn't in `base` is simply left out.
              `None` never appears in the result.
            - A section that exists only in `override` is copied without its `None` values.
            - Don't modify `base` or `override`.
            - The result must not share section dicts with the inputs: changing a section in
              the result must not change `base` or `override`.

            **Examples**
            ```python
            base = {"model": "gpt-4o", "params": {"temperature": 0.7, "top_p": 1.0},
                    "tools": ["search"]}
            override = {"params": {"temperature": 0.2, "top_p": None}, "stream": True}
            merge_config(base, override)
            # returns {"model": "gpt-4o", "params": {"temperature": 0.2},
            #          "tools": ["search"], "stream": True}
            merge_config({"a": 1, "b": 2}, {"a": None, "zzz": None})   # returns {"b": 2}
            merge_config({"a": {"x": 1}}, {"a": 5})                    # returns {"a": 5}
            merge_config({}, {"p": {"a": 1, "b": None}})               # returns {"p": {"a": 1}}
            ```
        ''',
        "starter": r'''
            def merge_config(base, override):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import merge_config

            def sample():
                base = {"model": "gpt-4o", "params": {"temperature": 0.7, "top_p": 1.0},
                        "tools": ["search"]}
                override = {"params": {"temperature": 0.2, "top_p": None}, "stream": True}
                return base, override

            def test_example_config_is_merged():
                got = merge_config(*sample())
                expected = {"model": "gpt-4o", "params": {"temperature": 0.2},
                            "tools": ["search"], "stream": True}
                assert got == expected, f"got {got!r}"

            def test_sections_merge_key_by_key():
                got = merge_config({"p": {"a": 1, "b": 2}, "x": 0}, {"p": {"b": 20, "c": 3}})
                assert got == {"p": {"a": 1, "b": 20, "c": 3}, "x": 0}, f"got {got!r}"

            def test_none_removes_top_level_key():
                got = merge_config({"a": 1, "b": 2}, {"a": None, "zzz": None})
                assert got == {"b": 2}, f"got {got!r}"

            def test_new_section_drops_none_values():
                got = merge_config({}, {"p": {"a": 1, "b": None}})
                assert got == {"p": {"a": 1}}, f"got {got!r}"

            def test_plain_value_and_section_replace_each_other():
                got = merge_config({"a": {"x": 1}}, {"a": 5})
                assert got == {"a": 5}, f"got {got!r}"
                got = merge_config({"a": 5}, {"a": {"x": 1}})
                assert got == {"a": {"x": 1}}, f"got {got!r}"

            def test_base_and_override_not_modified():
                base, override = sample()
                b0, o0 = copy.deepcopy(base), copy.deepcopy(override)
                merge_config(base, override)
                assert base == b0, f"base was modified: {base!r}"
                assert override == o0, f"override was modified: {override!r}"

            def test_changing_result_sections_leaves_inputs_alone():
                base = {"params": {"temperature": 0.7}, "meta": {"user": "a"}}
                override = {"extra": {"k": 1}}
                got = merge_config(base, override)
                got["params"]["temperature"] = 99
                got["meta"]["user"] = "changed"
                got["extra"]["k"] = 99
                assert base == {"params": {"temperature": 0.7}, "meta": {"user": "a"}}, (
                    f"mutating the result changed base: {base!r}")
                assert override == {"extra": {"k": 1}}, f"mutating the result changed override: {override!r}"
        ''',
        "solution": r'''
            def merge_config(base, override):
                result = {}
                for key, value in base.items():
                    if isinstance(value, dict):
                        result[key] = value.copy()
                    else:
                        result[key] = value
                for key, value in override.items():
                    if value is None:
                        result.pop(key, None)
                    elif isinstance(value, dict):
                        if isinstance(result.get(key), dict):
                            section = result[key]
                        else:
                            section = {}
                        for inner_key, inner_value in value.items():
                            if inner_value is None:
                                section.pop(inner_key, None)
                            else:
                                section[inner_key] = inner_value
                        result[key] = section
                    else:
                        result[key] = value
                return result
        ''',
    },
    {
        "id": "dicts-6",
        "hints": [
            'Nested dicts: one entry per user, each with a total and its own by_model dict. Pick top_model in a second pass.',
            'First loop over the records and accumulate tokens per user and per model (missing tokens = 0). Then, for each user, find the model with the most tokens, breaking ties by name.',
            'report = {}. For each record: tokens = record.get("tokens", 0); create the user\'s entry {"total": 0, "by_model": {}} if needed; add tokens to total and to by_model[model] with .get(model, 0). Then for each entry, loop over by_model.items() keeping the best model (higher tokens, or equal tokens and smaller name). Store it as top_model.',
        ],
        "title": "Per-user usage report",
        "difficulty": 3,
        "prompt": r'''
            Build a per-user token usage report from API usage records.

            **Write:** `usage_report(records)`

            - `records`: a list of dicts like `{"user": "ana", "model": "gpt-4o", "tokens": 120}`
            - **Returns:** a dict keyed by user name; each value is a dict with exactly three
              keys:

            ```python
            {
                "ana": {
                    "total": 450,
                    "by_model": {"gpt-4o": 120, "gpt-4o-mini": 330},
                    "top_model": "gpt-4o-mini",
                },
                ...
            }
            ```

            **Rules**
            - A record without a `"tokens"` key counts as `0` tokens (its model still appears
              in `by_model`, with `0`).
            - `"total"`: the sum of all that user's tokens.
            - `"by_model"`: for that user, model name -> sum of tokens (several records for
              the same model are added together).
            - Each user has their own `by_model` dict.
            - `"top_model"`: the model with the most tokens for that user. On a tie, pick
              the model name that comes first alphabetically (`"alpha"` before `"zeta"`).
            - An empty list returns `{}`.

            **Examples**
            ```python
            usage_report([
                {"user": "ana", "model": "gpt-4o", "tokens": 120},
                {"user": "ana", "model": "gpt-4o-mini", "tokens": 330},
                {"user": "bo", "model": "gpt-4o"},
            ])
            # returns {"ana": {"total": 450, "by_model": {"gpt-4o": 120, "gpt-4o-mini": 330},
            #                  "top_model": "gpt-4o-mini"},
            #          "bo": {"total": 0, "by_model": {"gpt-4o": 0}, "top_model": "gpt-4o"}}
            usage_report([
                {"user": "a", "model": "zeta", "tokens": 50},
                {"user": "a", "model": "alpha", "tokens": 50},
            ])
            # returns {"a": {"total": 100, "by_model": {"zeta": 50, "alpha": 50},
            #                "top_model": "alpha"}}
            usage_report([])   # returns {}
            ```
        ''',
        "starter": r'''
            def usage_report(records):
                ...
        ''',
        "tests": r'''
            from solution import usage_report

            def r(user, model, tokens=None):
                d = {"user": user, "model": model}
                if tokens is not None:
                    d["tokens"] = tokens
                return d

            def test_example_report_with_missing_tokens():
                got = usage_report([r("ana", "gpt-4o", 120), r("ana", "gpt-4o-mini", 330), r("bo", "gpt-4o")])
                expected = {
                    "ana": {"total": 450, "by_model": {"gpt-4o": 120, "gpt-4o-mini": 330},
                            "top_model": "gpt-4o-mini"},
                    "bo": {"total": 0, "by_model": {"gpt-4o": 0}, "top_model": "gpt-4o"},
                }
                assert got == expected, f"got {got!r}"

            def test_same_model_tokens_are_added_up():
                got = usage_report([r("ana", "m1", 10), r("ana", "m1", 15), r("ana", "m2", 20)])
                assert got["ana"]["by_model"] == {"m1": 25, "m2": 20}, f"got {got!r}"
                assert got["ana"]["top_model"] == "m1", f"got {got!r}"
                assert got["ana"]["total"] == 45

            def test_each_user_has_separate_by_model():
                got = usage_report([r("a", "m1", 5), r("b", "m1", 7)])
                assert got["a"]["by_model"] == {"m1": 5}, f"got {got!r}"
                assert got["b"]["by_model"] == {"m1": 7}, f"got {got!r}"
                assert got["a"]["by_model"] is not got["b"]["by_model"]

            def test_top_model_tie_picks_alphabetically_first():
                got = usage_report([r("a", "zeta", 50), r("a", "alpha", 50), r("a", "mid", 10)])
                assert got["a"]["top_model"] == "alpha", f"got {got['a']['top_model']!r}"
                got = usage_report([r("a", "beta", 0), r("a", "alpha", 0)])
                assert got["a"]["top_model"] == "alpha", f"got {got['a']['top_model']!r}"

            def test_empty_list_returns_empty_dict():
                assert usage_report([]) == {}
        ''',
        "solution": r'''
            def usage_report(records):
                report = {}
                for record in records:
                    tokens = record.get("tokens", 0)
                    entry = report.setdefault(record["user"], {"total": 0, "by_model": {}})
                    entry["total"] += tokens
                    by_model = entry["by_model"]
                    by_model[record["model"]] = by_model.get(record["model"], 0) + tokens
                for entry in report.values():
                    best = None
                    for model, tokens in entry["by_model"].items():
                        if best is None or tokens > entry["by_model"][best] or (
                                tokens == entry["by_model"][best] and model < best):
                            best = model
                    entry["top_model"] = best
                return report
        ''',
    },
]
