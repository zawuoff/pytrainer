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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["dict", "dictionary", "key", "value", "pair", "lookup", "keyerror", "curly braces",
                 "count", "group", "nested"],
    "cards": [
        {
            "syntax": 'd = {"key": value}',
            "explain": "Creates a dict. d[key] reads a value, d[key] = value adds or replaces a pair.",
            "example": r'''
                msg = {"role": "user"}
                msg["content"] = "hi"
                print(msg["role"], len(msg))
                # user 2
            ''',
        },
        {
            "syntax": "d.get(key, default)",
            "explain": "Reads a value without a KeyError. Returns default (or None) when the key is missing.",
            "example": r'''
                usage = {"input": 12}
                print(usage.get("input", 0))
                # 12
                print(usage.get("output", 0))
                # 0
            ''',
        },
        {
            "syntax": "key in d",
            "explain": "True when key is one of the dict's keys. It does not look at the values.",
            "example": r'''
                msg = {"role": "user"}
                print("role" in msg)
                # True
                print("user" in msg)
                # False
            ''',
        },
        {
            "syntax": "for key, value in d.items():",
            "explain": "Loops over the pairs in the order they were added. d.keys() and d.values() give one side.",
            "example": r'''
                prices = {"tea": 3, "cake": 4}
                for name, price in prices.items():
                    print(name, price)
                # tea 3
                # cake 4
            ''',
        },
        {
            "syntax": "counts[x] = counts.get(x, 0) + 1",
            "explain": "Counts how many times each value appears: start from 0 for a new key, then add 1.",
            "example": r'''
                counts = {}
                for word in ["a", "b", "a"]:
                    counts[word] = counts.get(word, 0) + 1
                print(counts)
                # {'a': 2, 'b': 1}
            ''',
        },
        {
            "syntax": "del d[key]  /  d.pop(key)",
            "explain": "del removes a pair. pop removes it and returns its value. Both raise KeyError if the key is missing.",
            "example": r'''
                msg = {"role": "user", "name": "bot"}
                print(msg.pop("name"))
                # bot
                del msg["role"]
                print(msg)
                # {}
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Dictionaries

A **dict** (dictionary) is a value that stores **key-value pairs**. Each **key** is paired
with one **value**, and you read a value by giving its key. You write a dict with curly
braces, a colon between each key and its value, and commas between the pairs. `{}` is the
empty dict.

```python
msg = {"role": "user", "content": "hi"}
print(msg)
# {'role': 'user', 'content': 'hi'}
print(len(msg))
# 2
```

Keys are usually strings. A value can be of any type, including a list or another dict.
A dict keeps its pairs in the order you added them. `len(msg)` returns the number of pairs.

### Reading and writing

`msg["role"]` returns the value stored under the key `"role"`. `msg["role"] = "assistant"`
replaces that value. Assigning to a key that does not exist adds a new pair.
`"role" in msg` is `True` when `"role"` is a key. It checks the keys, not the values.

```python
msg = {"role": "user", "content": "hi"}
print(msg["role"])
# user
msg["role"] = "assistant"
msg["name"] = "bot"
print(msg)
# {'role': 'assistant', 'content': 'hi', 'name': 'bot'}
print("role" in msg)
# True
print("hi" in msg)
# False
```

Click a key to read its value. Then type a key that does not exist and run `d[key]`.

```diagram
{"type":"dict","title":"Read, add and delete keys in msg","name":"msg","entries":[["role","user"],["content","hi"]]}
```

### Missing keys

`msg["name"]` raises `KeyError` when `"name"` is not a key, and the program stops.
`msg.get("name")` returns `None` in that case. `msg.get("name", "anon")` returns the
second value you pass, here `"anon"`.

```python
msg = {"role": "user", "content": "hi"}
print(msg.get("name"))
# None
print(msg.get("name", "anon"))
# anon
print(msg.get("role", "anon"))
# user
```

### Looping

`for key in d:` gives each key. `d.values()` gives each value. `d.items()` gives each key
together with its value, so the loop needs two names.

```python
usage = {"prompt_tokens": 12, "completion_tokens": 3}
for key in usage:
    print(key)
# prompt_tokens
# completion_tokens
for value in usage.values():
    print(value)
# 12
# 3
for key, value in usage.items():
    print(key, value)
# prompt_tokens 12
# completion_tokens 3
```

### Counting and grouping

To count, read the current count with a default of `0`, add 1, and store the result.
To group, store a list under each key and append to it. `groups.setdefault(source, [])`
returns the list stored under `source`. If `source` is not a key yet, it first stores `[]`
under that key.

```python
roles = ["user", "assistant", "user"]
counts = {}
for role in roles:
    counts[role] = counts.get(role, 0) + 1
print(counts)
# {'user': 2, 'assistant': 1}

chunks = [("a.pdf", "intro"), ("b.md", "setup"), ("a.pdf", "details")]
groups = {}
for source, text in chunks:
    groups.setdefault(source, []).append(text)
print(groups)
# {'a.pdf': ['intro', 'details'], 'b.md': ['setup']}
```

### Nested data

An **API** is a service that your program sends a request to and that sends data back.
API responses are dicts that contain lists and other dicts. Write one pair of square
brackets per level, starting with the outermost dict.

```python
response = {"choices": [{"message": {"role": "assistant", "content": "Paris."}}]}
print(response["choices"][0]["message"]["content"])
# Paris.
```

### Merging, copying and deleting

`a | b` builds a new dict with the pairs of both. When a key is in both, the value from
`b` is used. `a.update(b)` does the same merge but changes `a` itself. `a.copy()` returns a
new dict with the same pairs. The copy is **shallow**: a list or dict stored as a value is
not copied, so both dicts refer to the same inner object.

`del d[key]` removes a pair and raises `KeyError` when the key is missing. `d.pop(key)`
removes the pair and returns its value. `d.pop(key, None)` returns `None` when the key is
missing and raises no error.

```python
a = {"model": "gpt-4o-mini", "temperature": 0.7}
b = {"temperature": 0}
print(a | b)
# {'model': 'gpt-4o-mini', 'temperature': 0}
c = a.copy()
c.update(b)
del c["model"]
print(c)
# {'temperature': 0}
print(c.pop("temperature"))
# 0
print(c.pop("temperature", None))
# None
print(a)
# {'model': 'gpt-4o-mini', 'temperature': 0.7}
```

### Common mistakes

- `config[model]` uses the value of the variable `model` as the key. To look up the key
  `"model"`, write `config["model"]`.
- `d.get(key) or default` returns `default` when the stored value is `0`, `""` or `False`.
  `d.get(key, default)` returns `default` only when the key is missing.
- `b = a` does not copy. Both names refer to the same dict object. Use `a.copy()`.
- Do not add or remove keys inside a `for` loop over the same dict. When the number of
  pairs changes during the loop, Python stops with
  `RuntimeError: dictionary changed size during iteration`.

Docs: [Dictionaries tutorial](https://docs.python.org/3/tutorial/datastructures.html#dictionaries),
[dict methods](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict).
'''

EXERCISES = [
    {
        "id": "dicts-s1",
        "lesson": r'''
            ## Dictionaries

            A **dictionary**, or **dict**, is a value that stores **key-value pairs**. Each
            **key** is paired with one **value**. You read a value by giving its key, not a
            position as in a list. Write a dict with curly braces, a colon between each key
            and its value, and commas between the pairs.

            ```python
            settings = {"model": "claude", "stream": True}
            print(settings["model"])
            # claude
            print(len(settings))
            # 2
            ```

            `settings["model"]` returns the value stored under the key `"model"`. `len`
            returns the number of pairs.

            Assigning to a key that is not in the dict adds a new pair.

            ```python
            settings = {"model": "claude", "stream": True}
            settings["top_p"] = 0.9
            print(settings)
            # {'model': 'claude', 'stream': True, 'top_p': 0.9}
            ```

            `settings.get(key)` also reads a value. When the key is missing it returns `None`.
            If you pass a second value, `.get` returns that value for a missing key.

            ```python
            settings = {"model": "claude", "stream": True}
            print(settings.get("seed"))
            # None
            print(settings.get("seed", 42))
            # 42
            ```

            Click a key to read its value, then add a new key with `d[key] = value`.

            ```diagram
            {"type":"dict","title":"Keys and values of settings","name":"settings","entries":[["model","claude"],["stream",true]]}
            ```

            A dict is also called a **mapping**. An **API** is a service that your program
            sends a request to and that sends data back. The messages, settings and
            responses of AI APIs are dicts.
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

            To read a value from a dict, write the dict name followed by the key in square
            brackets. Python finds the pair with that key and returns its value.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            print(usage["completion_tokens"])
            # 3
            ```

            The position of the pair in the dict does not affect the lookup.
            `"completion_tokens"` is the second pair here and Python still finds it by its key.

            The key inside the brackets can be a string you write directly, or a variable
            that holds the key.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            key = "prompt_tokens"
            print(usage[key])
            # 12
            ```

            Reading with square brackets is called **subscripting**. It is the same syntax
            as a list index, with a key in place of the position.

            A string key needs its quotes. Without quotes, `usage[prompt_tokens]` tells
            Python to use the value of a variable named `prompt_tokens` as the key. This
            example raises an error on purpose, because no such variable exists.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            print(usage[prompt_tokens])
            # NameError: name 'prompt_tokens' is not defined
            ```
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

            A **dict literal** is a dict written directly in code with curly braces. The key
            goes on the left of each colon and the value goes on the right.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            print(usage)
            # {'prompt_tokens': 12, 'completion_tokens': 3}
            ```

            Python prints the string keys with single quotes. They are the same strings.

            The value on the right of a colon can be a variable. Python reads the variable
            when it builds the dict and stores what the variable holds.

            ```python
            name = "claude"
            limit = 256
            request = {"model": name, "max_tokens": limit}
            print(request)
            # {'model': 'claude', 'max_tokens': 256}
            print(request["model"])
            # claude
            ```

            The keys `"model"` and `"max_tokens"` are fixed strings, so they have quotes. The
            values `name` and `limit` are variables, so they have no quotes.

            The APIs of OpenAI, Anthropic and most other AI providers take each
            **chat message** as a dict with the two keys `"role"` and `"content"`.

            Quotes around a variable name turn it into a string. `{"model": "name"}` stores
            the text `name`, not the value of the variable.

            ```python
            name = "claude"
            request = {"model": "name"}
            print(request["model"])
            # name
            ```
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

            `d[key] = value` stores `value` under `key` in the dict `d`. If the key is not
            in the dict, Python adds a new pair. If the key is already there, Python replaces
            its value.

            ```python
            request = {"model": "claude"}
            request["temperature"] = 0.7
            print(request)
            # {'model': 'claude', 'temperature': 0.7}
            request["temperature"] = 0.2
            print(request)
            # {'model': 'claude', 'temperature': 0.2}
            print(len(request))
            # 2
            ```

            The first assignment adds the key `"temperature"`. The second one replaces its
            value. Keys in a dict are **unique**: a dict never holds the same key twice, so
            the length stays 2.

            A dict is **mutable**, which means you can change it after you create it.
            Assignment to a key changes the dict **in place**: no new dict is created. Every
            name that refers to that dict object shows the change, as with `list.append`.

            ```python
            request = {"model": "claude"}
            same = request
            same["stream"] = True
            print(request)
            # {'model': 'claude', 'stream': True}
            print(same is request)
            # True
            ```

            `same is request` is `True` when both names refer to the same object.

            You do not call anything to add a key. The assignment `d[key] = value` is the
            whole operation.
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

            Reading a key that is not in the dict with square brackets raises `KeyError`, and
            the program stops. This example raises the error on purpose.

            ```python
            request = {"model": "gpt-4o", "max_tokens": 0}
            print(request["top_p"])
            # KeyError: 'top_p'
            ```

            API data often has optional keys. `d.get(key, default)` reads a key without
            raising an error. It returns the stored value when the key exists. It returns
            `default` when the key is missing. The second value is called the
            **default value**.

            ```python
            request = {"model": "gpt-4o", "max_tokens": 0}
            print(request.get("max_tokens", 256))
            # 0
            print(request.get("top_p", 0.9))
            # 0.9
            print(request.get("top_p"))
            # None
            print("top_p" in request)
            # False
            ```

            The first line prints `0`. The key `"max_tokens"` exists, so `.get` returns its
            value and ignores the default. With no default, `.get` returns `None` for a
            missing key. `key in d` is `True` when the key exists and `False` when it does not.

            `d.get(key) or default` is not the same. `or` returns its right side whenever
            the left side is falsy, such as `0`, `""`, `False` or `None`, so a stored `0`
            is lost.

            ```python
            request = {"model": "gpt-4o", "max_tokens": 0}
            print(request.get("max_tokens") or 256)
            # 256
            ```
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

            `d.items()` gives each key together with its value. A `for` loop with two names
            assigns the key to the first name and the value to the second, as `enumerate` did
            with an index and an item.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            total = 0
            for key, value in usage.items():
                print(f"{key}: {value}")
                total = total + value
            print(total)
            # prompt_tokens: 12
            # completion_tokens: 3
            # 15
            ```

            The pairs come in the order they were added to the dict. Step through the loop
            and watch `key` and `value` change on each pass.

            ```diagram
            {"type": "trace", "title": "Looping over usage.items()", "code": ["usage = {\"prompt_tokens\": 12, \"completion_tokens\": 3}", "total = 0", "for key, value in usage.items():", "    print(f\"{key}: {value}\")", "    total = total + value", "print(total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}"}, "out": ""},
              {"line": 3, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "0"}, "out": ""},
              {"line": 4, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "0", "key": "'prompt_tokens'", "value": "12"}, "out": ""},
              {"line": 5, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "0", "key": "'prompt_tokens'", "value": "12"}, "out": "prompt_tokens: 12\n"},
              {"line": 3, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "12", "key": "'prompt_tokens'", "value": "12"}, "out": "prompt_tokens: 12\n"},
              {"line": 4, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "12", "key": "'completion_tokens'", "value": "3"}, "out": "prompt_tokens: 12\n"},
              {"line": 5, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "12", "key": "'completion_tokens'", "value": "3"}, "out": "prompt_tokens: 12\ncompletion_tokens: 3\n"},
              {"line": 3, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "15", "key": "'completion_tokens'", "value": "3"}, "out": "prompt_tokens: 12\ncompletion_tokens: 3\n"},
              {"line": 6, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "15", "key": "'completion_tokens'", "value": "3"}, "out": "prompt_tokens: 12\ncompletion_tokens: 3\n"},
              {"line": null, "vars": {"usage": "{'prompt_tokens': 12, 'completion_tokens': 3}", "total": "15", "key": "'completion_tokens'", "value": "3"}, "out": "prompt_tokens: 12\ncompletion_tokens: 3\n15\n"}
            ]}
            ```

            Looping over the dict itself gives only the keys. `d.values()` gives only the
            values.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            for key in usage:
                print(key)
            # prompt_tokens
            # completion_tokens
            print(list(usage.values()))
            # [12, 3]
            ```

            `.items()`, `.keys()` and `.values()` each return a **view**: an object that
            shows the current contents of the dict and that you can loop over.

            `for key, value in usage:` without `.items()` raises an error. Each item is then
            one key string, and Python tries to unpack the characters of that string into
            the two names. The key has more than two characters, so the unpacking fails.
            This example raises the error on purpose.

            ```python
            usage = {"prompt_tokens": 12, "completion_tokens": 3}
            for key, value in usage:
                print(key, value)
            # ValueError: too many values to unpack (expected 2)
            ```
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
            ## Nested data

            A dict value can be a list, and a list item can be another dict. Data with dicts
            and lists inside each other is called **nested data**. API responses have this
            shape.

            ```python
            result = {
                "model": "claude",
                "usage": {"input_tokens": 12, "output_tokens": 3},
                "tool_calls": [{"name": "search"}, {"name": "weather"}],
            }
            usage = result["usage"]
            print(usage)
            # {'input_tokens': 12, 'output_tokens': 3}
            print(usage["output_tokens"])
            # 3
            ```

            `result["usage"]` returns the inner dict. A second lookup on that dict returns
            the number. You can write both lookups in one expression. Python evaluates the
            brackets from left to right, and each bracket reads from the value the previous
            one returned.

            ```python
            result = {
                "model": "claude",
                "usage": {"input_tokens": 12, "output_tokens": 3},
                "tool_calls": [{"name": "search"}, {"name": "weather"}],
            }
            print(result["usage"]["output_tokens"])
            # 3
            print(result["tool_calls"][1]["name"])
            # weather
            ```

            In the last line, `result["tool_calls"]` returns a list, `[1]` returns its second
            item, which is a dict, and `["name"]` returns the value under that dict's key
            `"name"`.

            Use a whole number in the brackets for a list and a key for a dict. When a
            chained lookup raises an error, split it into separate lines and `print` each
            intermediate value to find the level that fails.
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

            The `|` operator between two dicts is the **merge operator**. `a | b` builds a
            new dict that contains the pairs of `a` and the pairs of `b`.

            ```python
            base = {"model": "claude", "top_p": 0.9}
            extra = {"top_p": 0.5, "seed": 42}
            merged = base | extra
            print(merged)
            # {'model': 'claude', 'top_p': 0.5, 'seed': 42}
            print(base)
            # {'model': 'claude', 'top_p': 0.9}
            print(extra)
            # {'top_p': 0.5, 'seed': 42}
            ```

            Python copies the pairs of the left dict into the new dict, then stores the
            pairs of the right dict in it. That gives three rules:

            - A key that is in only one of the dicts is kept.
            - A key that is in both dicts gets the value from the right-hand dict.
            - Neither `base` nor `extra` is changed.

            `d.update(other)` does the same merge **in place**: it stores the pairs of
            `other` in `d` itself and builds no new dict.

            ```python
            base = {"model": "claude", "top_p": 0.9}
            base.update({"top_p": 0.5})
            print(base)
            # {'model': 'claude', 'top_p': 0.5}
            ```

            After `base.update(...)`, the original values of `base` are gone for all code
            that uses `base` later. Use `|` when the original dict must stay as it is.
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

            `del d[key]` removes the pair with that key from the dict `d`. It changes the dict
            in place.

            To keep the original dict unchanged, remove the key from a copy. As with lists,
            `b = a` does not copy: both names refer to the same dict object. `a.copy()`
            returns a new dict with the same pairs.

            ```python
            headers = {"user": "ana", "token": "abc123"}
            safe = headers.copy()
            del safe["token"]
            print(safe)
            # {'user': 'ana'}
            print(headers)
            # {'user': 'ana', 'token': 'abc123'}
            ```

            `safe` lost the key and `headers` still has it, because they are two dict
            objects.

            `.copy()` makes a **shallow copy**: a new outer dict whose values are the same
            objects as in the original. A list or dict stored as a value is not copied. For
            a flat dict of strings and numbers, such as this one, that makes no difference.

            Like `d[key]`, `del d[key]` raises `KeyError` when the key is missing. This
            example raises the error on purpose.

            ```python
            headers = {"user": "ana"}
            del headers["token"]
            # KeyError: 'token'
            ```

            Dicts have a method that removes a key and lets you choose what it returns when
            the key is missing, so no error is raised. Open the dict methods in the Python
            docs (linked above), find it, and read what its second argument does.
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

            To count how often each value appears in a list, use a dict. Each key is one of
            the values, and the value stored under it is the count so far. This is the
            **counting pattern**.

            ```python
            tools_called = ["search", "weather", "search"]
            counts = {}
            for tool in tools_called:
                counts[tool] = counts.get(tool, 0) + 1
            print(counts)
            # {'search': 2, 'weather': 1}
            ```

            On each pass, Python evaluates the right side first. `counts.get(tool, 0)` returns
            the current count, or `0` when `tool` is not a key yet. Python adds 1 and stores
            the result under `tool`. The first `"search"` adds the key with the value 1. The
            second `"search"` replaces that value with 2.

            Step through the loop and watch `counts` change.

            ```diagram
            {"type": "trace", "title": "Counting tool calls with a dict", "code": ["tools_called = [\"search\", \"weather\", \"search\"]", "counts = {}", "for tool in tools_called:", "    counts[tool] = counts.get(tool, 0) + 1", "print(counts)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"tools_called": "['search', 'weather', 'search']"}, "out": ""},
              {"line": 3, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{}"}, "out": ""},
              {"line": 4, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{}", "tool": "'search'"}, "out": ""},
              {"line": 3, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 1}", "tool": "'search'"}, "out": ""},
              {"line": 4, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 1}", "tool": "'weather'"}, "out": ""},
              {"line": 3, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 1, 'weather': 1}", "tool": "'weather'"}, "out": ""},
              {"line": 4, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 1, 'weather': 1}", "tool": "'search'"}, "out": ""},
              {"line": 3, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 2, 'weather': 1}", "tool": "'search'"}, "out": ""},
              {"line": 5, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 2, 'weather': 1}", "tool": "'search'"}, "out": ""},
              {"line": null, "vars": {"tools_called": "['search', 'weather', 'search']", "counts": "{'search': 2, 'weather': 1}", "tool": "'search'"}, "out": "{'search': 2, 'weather': 1}\n"}
            ]}
            ```

            In the loops chapter, `total = 0` was one accumulator. Here the dict holds one
            accumulator per key.

            `counts[tool] += 1` without `.get` raises `KeyError` the first time a tool
            appears, because Python must read `counts[tool]` before the key exists. This
            example raises the error on purpose.

            ```python
            counts = {}
            counts["search"] += 1
            # KeyError: 'search'
            ```
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
