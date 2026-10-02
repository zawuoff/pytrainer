TOPIC = {
    "id": "structured-output",
    "title": "Structured Output",
    "track": "llm-apps",
    "order": 3,
    "requires": ["prompts"],
    "summary": """
        Getting data, not prose, out of a model: parsing JSON from replies, stripping code
        fences, checking keys and types, defaults and enums, a tiny JSON Schema checker,
        and retrying with error feedback.
    """,
    "concepts": ["structured output", "json.loads", "JSONDecodeError", "code fences",
                 "required keys", "type checks", "bool is an int", "defaults", "enums",
                 "type coercion", "JSON Schema", "retry with feedback"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["structured output", "json", "json.loads", "jsondecodeerror", "parse",
                 "code fence", "validate", "isinstance", "bool", "default", "enum", "coercion",
                 "json schema", "schema", "retry"],
    "cards": [
        {
            "syntax": "json.loads(text)",
            "explain": "Parses a JSON string into Python data. Raises json.JSONDecodeError for invalid JSON. Its .msg is a short reason.",
            "example": r'''
                import json
                for text in ['{"n": 2}', "Sure!"]:
                    try:
                        print(json.loads(text))
                    except json.JSONDecodeError as error:
                        print("invalid JSON:", error.msg)
                # {'n': 2}
                # invalid JSON: Expecting value
            ''',
        },
        {
            "syntax": 'reply[reply.find("{"):reply.rfind("}") + 1]',
            "explain": "The text from the first { to the last }, both included. Removes sentences around a JSON object.",
            "example": r'''
                reply = 'Sure! {"a": 1} Hope that helps.'
                start = reply.find("{")
                end = reply.rfind("}") + 1
                print(reply[start:end])
                # {"a": 1}
            ''',
        },
        {
            "syntax": "isinstance(value, int) and not isinstance(value, bool)",
            "explain": "True for an int, False for True and False. bool is a subclass of int, so isinstance(True, int) is True.",
            "example": r'''
                for value in [3, True, "3"]:
                    is_int = isinstance(value, int) and not isinstance(value, bool)
                    print(repr(value), is_int)
                # 3 True
                # True False
                # '3' False
            ''',
        },
        {
            "syntax": "{**defaults, **data}",
            "explain": "A new dict with the keys of both. For a key in both, the value from data replaces the default.",
            "example": r'''
                defaults = {"priority": "medium", "tags": []}
                data = {"title": "Bug", "priority": "high"}
                print({**defaults, **data})
                # {'priority': 'high', 'tags': [], 'title': 'Bug'}
            ''',
        },
        {
            "syntax": "value.strip().lower() in allowed",
            "explain": "An enum check: remove spaces at both ends, lowercase, then test against the list of allowed values.",
            "example": r'''
                allowed = ["low", "medium", "high"]
                for value in [" HIGH ", "urgent"]:
                    print(value.strip().lower() in allowed)
                # True
                # False
            ''',
        },
        {
            "syntax": '{"type": "object", "properties": {...}, "required": [...]}',
            "explain": "A JSON Schema. properties maps each key to a schema for its value. required lists the keys that must be present.",
            "example": r'''
                schema = {"type": "object",
                          "properties": {"age": {"type": "integer"}},
                          "required": ["age"]}
                data = {"name": "Ada"}
                print([key for key in schema["required"] if key not in data])
                # ['age']
            ''',
        },
    ],
}

LESSON = r'''
## Structured output: chapter notes

A model's reply is a string. Your code cannot branch on a sentence such as
`Sure! The customer seems unhappy.` It can branch on
`{"sentiment": "negative", "urgent": true}`. **Structured output** means that you ask the
model for data in a fixed format, usually JSON, and you check that data before you use it.

Models often write replies in **Markdown**, a plain-text format in which symbols mark
headings, lists and code. In Markdown, a line of three backticks before a block of code and
another after it is a code fence. A backtick is the slanted quote character on the key
left of `1` on a US keyboard.

Step through the stages a reply passes through before your code uses it.

```diagram
{"type":"flow","title":"From reply text to checked data","steps":[
{"label":"Call the model","detail":"llm(messages) returns the reply as one string. The string can contain extra sentences or a Markdown code fence around the JSON.","code":"reply = 'Sure! {\"sentiment\": \"negative\", \"urgent\": true}'"},
{"label":"Extract the JSON text","detail":"Take the text inside the code fence if there is one. Otherwise slice from the first { to the last }.","code":"text = '{\"sentiment\": \"negative\", \"urgent\": true}'"},
{"label":"Parse","detail":"json.loads(text) builds a Python value from the JSON text. It raises json.JSONDecodeError when the text is not valid JSON.","code":"data = {'sentiment': 'negative', 'urgent': True}"},
{"label":"Validate","detail":"Check that the value is a dict, that every required key is present and that each value has the expected type. Collect each problem as a string.","code":"problems = []"},
{"label":"Use the data","detail":"When the list of problems is empty, fill in defaults for missing optional keys and return the dict.","code":"result = {'sentiment': 'negative', 'urgent': True, 'tags': []}"}
],"loop":{"from":3,"to":0,"label":"problems found and attempts remain: send the problems back"}}
```

### Parsing

`json.loads(text)` parses a JSON string and returns the Python value it describes: a
`dict`, `list`, `str`, `int`, `float`, `bool` or `None`.

```python
import json

data = json.loads('{"ok": true, "n": 2}')
print(data)
# {'ok': True, 'n': 2}
```

Invalid JSON raises `json.JSONDecodeError`, which is a subclass of `ValueError`. Its `.msg`
attribute is a short reason.

```python
import json

try:
    json.loads("Sure!")
except json.JSONDecodeError as error:
    print(error.msg)
# Expecting value
```

### Extracting the JSON

Models often surround the JSON with sentences or put it in a Markdown **code fence**: three
backticks, optionally followed by `json`, then the content, then three backticks. With a
fence, parse only the text inside it. Without one, slice from the first `{` to the last `}`.

```python
reply = 'Sure! {"a": 1} Hope that helps.'
start = reply.find("{")
end = reply.rfind("}") + 1
print(reply[start:end])
# {"a": 1}
```

### Checking keys and types

`key in data` tests whether a dict has a key. `isinstance(value, kind)` tests the type of
a value.

```python
data = {"count": 3, "ok": True}
print("count" in data)
# True
print(isinstance(data["count"], int))
# True
print(isinstance(data["ok"], int))
# True
```

The last line prints `True` because `bool` is a subclass of `int`. When a field must be a
number, reject `bool` values with a separate check.

### Defaults and enums

`{**defaults, **data}` builds a new dict. A key that is in both dicts gets the value from
`data`. An **enum** is a fixed list of allowed values for a field. Clean the value with
`.strip().lower()`, then test it with `in`.

```python
defaults = {"priority": "medium", "tags": []}
data = {"title": "Bug", "priority": " HIGH "}
merged = {**defaults, **data}
priority = merged["priority"].strip().lower()
print(priority, priority in ["low", "medium", "high"])
# high True
```

### Coercion

**Type coercion** is converting a value from one type to another. Models sometimes send
`"42"` where you expect `42`. Try `int` first, then `float`, and raise if both fail.

```python
print(int("42"))
# 42
print(float("3.5"))
# 3.5
```

### JSON Schema

A **schema** is a description of the shape of data: which keys it has and what type each
value has. **JSON Schema** is a standard format for writing a schema for JSON data. A
schema in that format is itself a JSON object. `"properties"` maps each key of the data to
a schema for its value. `"required"` lists the keys that must be present.

```python
schema = {"type": "object",
          "properties": {"age": {"type": "integer"}},
          "required": ["age"]}
print(schema["properties"]["age"]["type"])
# integer
```

The type names are `string`, `integer`, `number`, `boolean`, `array` and `object`. The
`jsonschema` and Pydantic libraries (third-party packages that check data against a
schema) use JSON Schema, and so do the structured output
features of model providers.

### Retry with feedback

When a reply is invalid, append two messages to the conversation: an `assistant` message
that holds the invalid reply, and a `user` message that states what was wrong. Then call
the model again. Stop after a maximum number of attempts and raise an exception.

## Common mistakes

- `text[start:end]` with `end = text.rfind("}")` leaves out the closing brace. Use `end + 1`.
- Valid JSON is not always an object. `[1, 2]` and `"hi"` are valid JSON, and `json.loads`
  returns a list and a string for them.
- `isinstance(True, int)` is `True`, so a number check that uses only `isinstance` accepts
  `true` from the model.
- Changing the caller's dict or message list in place affects the caller's later code.
  Build a new dict or list.
- A retry loop with no attempt limit keeps calling the API for as long as the replies stay
  invalid, and every call costs money.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "structured-output-s1",
        "title": "From text to data",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Structured output

            A model's reply is always a string. Your code cannot read a field out of a
            sentence such as `Paris has about 2 million people.` It can read a field out of
            JSON.

            **JSON** is a text format for data. A JSON object has keys and values inside curly
            braces, written much as a Python dict is written. **Structured output** means that
            you ask the model to reply with data in a fixed format, usually JSON, instead of
            sentences.

            To **parse** a string is to read it and build the Python value it describes.
            `json.loads(text)` parses a JSON string. The name is short for "load from string".
            A JSON object becomes a `dict`, and a JSON number becomes an `int` or a `float`.

            ```python
            import json

            reply = '{"city": "Paris", "population": 2100000}'
            data = json.loads(reply)
            print(data["city"])
            # Paris
            print(data["population"] > 1000000)
            # True
            print(type(data).__name__)
            # dict
            ```

            `type(x).__name__` is the name of the type of `x` as a string. `reply` is a `str`,
            so `reply["city"]` raises `TypeError`. `data` is a `dict`, and
            `data["population"]` is an `int` that you can compare with another number.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            import json

            reply = '{"name": "Ada", "age": 36, "tags": ["math"]}'
            data = json.loads(reply)
            print(data["name"])
            print(data["age"] + 1)
            print(type(reply).__name__, type(data).__name__)
        ''',
        "solution": r'''
            Ada
            37
            str dict
        ''',
        "explanation": r'''
            `json.loads` turns the JSON text into a dict. `data["name"]` is the string `Ada`,
            and `data["age"]` is a real int, so `+ 1` gives `37`. The original `reply` is still
            a `str`; the parsed `data` is a `dict`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "json.loads turns the text into Python values: objects become dicts, numbers become ints.",
            "After parsing, data[\"age\"] is the number 36, so you can do maths with it.",
            "Line 1: the name. Line 2: 36 + 1. Line 3: the type names of the original text and the parsed result.",
        ],
    },
    {
        "id": "structured-output-s2",
        "title": "Parse a reply",
        "difficulty": 0,
        "lesson": r'''
            ## json.loads and json.dumps

            A JSON reply from a model is a string. Your code needs the dict that the string
            describes. The `json` module in the standard library converts in both directions.

            `json.loads(text)` takes a JSON string and returns Python data. `json.dumps(data)`
            takes Python data and returns a JSON string. The "s" at the end of both names
            stands for "string".

            ```python
            import json

            text = '{"label": "spam", "score": 0.93}'
            result = json.loads(text)
            print(result["label"], result["score"])
            # spam 0.93
            print(json.dumps(result))
            # {"label": "spam", "score": 0.93}
            ```

            JSON writes three values differently from Python: `true`, `false` and `null`.
            `json.loads` converts them to `True`, `False` and `None`.

            ```python
            import json

            flags = json.loads('{"cached": true, "error": null}')
            print(flags)
            # {'cached': True, 'error': None}
            ```

            Writing `true` or `null` in Python code raises `NameError`. Those spellings are
            only valid inside a JSON string.
        ''',
        "prompt": r'''
            A model was told to reply with JSON. Turn its reply into a Python dict. Replace the `___`.

            **Write:** `parse_reply(text)`

            - `text`: a string containing a JSON object, e.g. `'{"label": "spam"}'`
            - **Returns:** the parsed dict

            **Rules**
            - JSON `true`/`false`/`null` come back as `True`/`False`/`None`.

            **Examples**
            ```python
            parse_reply('{"label": "spam", "score": 0.93}')   # returns {"label": "spam", "score": 0.93}
            parse_reply('{"urgent": true, "owner": null}')    # returns {"urgent": True, "owner": None}
            ```
        ''',
        "starter": r'''
            import json


            def parse_reply(text):
                return json.___(text)
        ''',
        "tests": r'''
            from solution import parse_reply

            def test_parses_object_into_dict():
                got = parse_reply('{"label": "spam", "score": 0.93}')
                assert got == {"label": "spam", "score": 0.93}, f"got {got!r}"

            def test_json_literals_become_python_values():
                got = parse_reply('{"urgent": true, "owner": null}')
                assert got == {"urgent": True, "owner": None}, f"got {got!r}"

            def test_result_is_a_dict_not_a_string():
                got = parse_reply('{"a": 1}')
                assert isinstance(got, dict), f"got a {type(got).__name__}"
        ''',
        "solution": r'''
            import json


            def parse_reply(text):
                return json.loads(text)
        ''',
        "hints": [
            "You want the json function that goes from a string to Python data.",
            "It's the one whose name ends in s for 'string' and starts with 'load'.",
            "Replace ___ with loads.",
        ],
    },
    {
        "id": "structured-output-s3",
        "title": "Fix: the missing brace",
        "difficulty": 0,
        "lesson": r'''
            ## Extracting the JSON object from a reply

            A model that is told to reply with JSON only often adds words around it, as in
            `OK: {"a": 1}.` Passing that whole string to `json.loads` raises an error. You
            first have to take out the part that is JSON.

            A JSON object starts at the first `{` and ends at the last `}`.
            `reply.find("{")` searches from the left and returns the index of the first `{`.
            `reply.rfind("}")` searches from the right and returns the index of the last `}`.

            ```python
            reply = 'OK: {"a": 1}.'
            start = reply.find("{")
            end = reply.rfind("}")
            print(start, end)
            # 4 11
            print(reply[start:end])
            # {"a": 1
            print(reply[start:end + 1])
            # {"a": 1}
            ```

            A slice `reply[a:b]` stops before index `b`. The character at index `b` is not
            part of the result. To include the character at `end`, slice up to `end + 1`.

            Drag the stop handle from 11 to 12 and watch the closing brace join the result.

            ```diagram
            {"type":"slice","title":"Slicing the JSON object out of reply","name":"reply","value":"OK: {\"a\": 1}.","start":4,"stop":11}
            ```

            A result that is one position too short or too long is called an **off-by-one
            error**. Here it produces `{"a": 1`, which is not valid JSON.
        ''',
        "prompt": r'''
            This helper should cut the JSON object out of a chatty reply, but the result is
            always broken. Fix the bug.

            **Write:** `extract_object(reply)`

            - `reply`: a string that contains exactly one JSON object somewhere inside, e.g.
              `'Sure! {"a": 1} Hope that helps.'`
            - **Returns:** the substring from the first `{` to the last `}`, **both included**

            **Rules**
            - Return a string (don't parse it).

            **Examples**
            ```python
            extract_object('Sure! {"a": 1} Hope that helps.')   # returns '{"a": 1}'
            extract_object('{"x": {"y": 2}}')                   # returns '{"x": {"y": 2}}'
            ```
        ''',
        "starter": r'''
            def extract_object(reply):
                start = reply.find("{")
                end = reply.rfind("}")
                return reply[start:end]
        ''',
        "tests": r'''
            from solution import extract_object

            def test_cuts_object_out_of_prose():
                got = extract_object('Sure! {"a": 1} Hope that helps.')
                assert got == '{"a": 1}', f"got {got!r}"

            def test_nested_object_kept_whole():
                got = extract_object('{"x": {"y": 2}}')
                assert got == '{"x": {"y": 2}}', f"got {got!r}"

            def test_result_ends_with_closing_brace():
                got = extract_object('Result: {"ok": true}.')
                assert got.endswith("}"), f"got {got!r}"
        ''',
        "solution": r'''
            def extract_object(reply):
                start = reply.find("{")
                end = reply.rfind("}")
                return reply[start:end + 1]
        ''',
        "hints": [
            "Print what the function returns for the first example. Which character is missing?",
            "A slice stops just before its end index, so the character at `end` is left out.",
            "Change the slice to reply[start:end + 1].",
        ],
    },
    {
        "id": "structured-output-s4",
        "title": "Is a bool a number?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Type checks with isinstance

            A parsed reply is a dict, but its values can have any type. The model can send the
            string `"3"` where you expected the number `3`. Check the type of a value before
            you use it.

            `isinstance(value, kind)` returns `True` when `value` has the type `kind`. The
            second argument can also be a tuple of types. Then the result is `True` when the
            value has any one of them.

            ```python
            print(isinstance(3, int))
            # True
            print(isinstance("3", int))
            # False
            print(isinstance(2.5, (int, float)))
            # True
            ```

            `isinstance` also returns `True` for a subclass of `kind`. `type(x) is kind` is
            stricter: it is `True` only when the type of `x` is exactly `kind`.

            ```python
            print(type(2.5) is float)
            # True
            print(type(2.5) is int)
            # False
            ```

            In Python, `bool` is a subclass of `int`. `True` equals `1` and `False` equals `0`,
            so `False + 1` is `1`. This affects what `isinstance` returns for `True` and
            `False`, which the code below asks you to predict.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            data = {"count": 3, "ok": True, "score": 0.5, "name": "x"}
            print(isinstance(data["count"], int))
            print(isinstance(data["ok"], int))
            print(isinstance(data["score"], int))
            print(type(data["ok"]) is bool)
        ''',
        "solution": r'''
            True
            True
            False
            True
        ''',
        "explanation": r'''
            `3` is an int, so the first line prints `True`. `True` is a `bool`, and `bool` is a
            subclass of `int`, so `isinstance(True, int)` is also `True`. `0.5` is a float,
            not an int, so the third line prints `False`. `type(True) is bool` compares the
            exact type, so it is `True`. When you validate a number field, reject `bool`
            values with a separate check.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "isinstance also says True for related (sub-) types.",
            "In Python, bool is built on top of int: True acts like 1.",
            "count -> True; ok (a bool) -> also counts as an int; score is a float -> False; exact type of ok is bool -> True.",
        ],
    },
    {
        "id": "structured-output-s5",
        "title": "All keys present?",
        "difficulty": 0,
        "lesson": r'''
            ## Checking required keys

            A model can leave out a key that your code needs. Reading a missing key with
            `reply["owner"]` raises `KeyError`. If that happens many lines after the reply was
            parsed, the traceback points at the line that read the key, not at the reply that
            lacked it. Check for the keys right after parsing.

            The `in` operator tests whether a dict has a key.

            ```python
            reply = {"title": "Bug in login", "priority": "high"}
            print("title" in reply)
            # True
            print("owner" in reply)
            # False
            ```

            Click a key, or type `owner` and run `key in d` and `d[key]`.

            ```diagram
            {"type":"dict","title":"Keys of reply","name":"reply","entries":[["title","Bug in login"],["priority","high"]]}
            ```

            `all(...)` takes a series of values and returns `True` only when every one of them
            is true. Give it one `in` test per required key.

            ```python
            reply = {"title": "Bug in login", "priority": "high"}
            print(all(key in reply for key in ["title", "priority"]))
            # True
            print(all(key in reply for key in ["title", "owner"]))
            # False
            ```

            To **validate** data is to check that it has the form your code expects. Checking
            the keys is the first part of validating structured output.

            `all([])` returns `True`. With no values to test, none of them is false.
        ''',
        "prompt": r'''
            Check that a parsed reply has every key your code needs.

            **Write:** `has_keys(data, keys)`

            - `data`: a dict, e.g. `{"title": "Bug", "priority": "high"}`
            - `keys`: a list of key strings, e.g. `["title", "priority"]`; may be empty
            - **Returns:** `True` if every key in `keys` is in `data`, otherwise `False`

            **Rules**
            - Extra keys in `data` don't matter.
            - An empty `keys` list returns `True`.

            **Examples**
            ```python
            has_keys({"title": "Bug", "priority": "high"}, ["title", "priority"])   # returns True
            has_keys({"title": "Bug"}, ["title", "owner"])                         # returns False
            has_keys({}, [])                                                       # returns True
            ```
        ''',
        "starter": r'''
            def has_keys(data, keys):
                ...
        ''',
        "tests": r'''
            from solution import has_keys

            def test_all_keys_present():
                assert has_keys({"title": "Bug", "priority": "high"}, ["title", "priority"]) is True

            def test_one_key_missing():
                assert has_keys({"title": "Bug"}, ["title", "owner"]) is False

            def test_extra_keys_do_not_matter():
                assert has_keys({"a": 1, "b": 2, "c": 3}, ["b"]) is True

            def test_no_keys_required():
                assert has_keys({}, []) is True
        ''',
        "solution": r'''
            def has_keys(data, keys):
                return all(key in data for key in keys)
        ''',
        "hints": [
            "Use `in` to test if one key is in the dict; you need that for every key.",
            "all(...) with a generator expression checks a condition for every item.",
            "Return all(key in data for key in keys).",
        ],
    },
    {
        "id": "structured-output-s6",
        "title": "Fill in defaults",
        "difficulty": 0,
        "lesson": r'''
            ## Defaults

            A **default** is the value your code uses for a field when the reply does not
            contain that field. Models often leave out optional fields. Filling in defaults
            lets the rest of your code read every key without a `KeyError`.

            Inside a dict literal, `**other` copies every key and value of `other` into the
            new dict. When the same key is copied twice, the value copied later replaces the
            earlier one.

            ```python
            defaults = {"priority": "medium", "tags": []}
            reply = {"title": "Bug", "priority": "high"}
            merged = {**defaults, **reply}
            print(merged)
            # {'priority': 'high', 'tags': [], 'title': 'Bug'}
            print(defaults)
            # {'priority': 'medium', 'tags': []}
            ```

            `defaults` is copied first and `reply` second. `"priority"` is in both, so `merged`
            gets `"high"` from `reply`. `"tags"` is only in `defaults`, so `merged` gets the
            default. The braces build a new dict, so `defaults` and `reply` are unchanged.

            `defaults.update(reply)` gives the same keys and values, but it changes `defaults`
            itself. Every later use of `defaults` would then contain `"priority": "high"` and
            `"title": "Bug"`.
        ''',
        "prompt": r'''
            Fill in missing optional fields of a parsed reply with default values.

            **Write:** `with_defaults(data, defaults)`

            - `data`: a dict from the model, e.g. `{"title": "Bug"}`
            - `defaults`: a dict of default values, e.g. `{"priority": "medium"}`
            - **Returns:** a **new** dict with every key from both; values from `data` win

            **Rules**
            - If a key is in both, keep the value from `data`.
            - Don't modify `data` or `defaults`.

            **Examples**
            ```python
            with_defaults({"title": "Bug"}, {"priority": "medium"})
            # returns {"priority": "medium", "title": "Bug"}
            with_defaults({"priority": "high"}, {"priority": "medium"})
            # returns {"priority": "high"}
            ```
        ''',
        "starter": r'''
            def with_defaults(data, defaults):
                ...
        ''',
        "tests": r'''
            from solution import with_defaults

            def test_missing_keys_get_defaults():
                got = with_defaults({"title": "Bug"}, {"priority": "medium"})
                assert got == {"priority": "medium", "title": "Bug"}, f"got {got!r}"

            def test_data_values_win_over_defaults():
                got = with_defaults({"priority": "high"}, {"priority": "medium"})
                assert got == {"priority": "high"}, f"got {got!r}"

            def test_inputs_are_not_modified():
                data = {"title": "Bug"}
                defaults = {"priority": "medium"}
                got = with_defaults(data, defaults)
                assert data == {"title": "Bug"} and defaults == {"priority": "medium"}, "an input dict was changed"
                assert got is not data and got is not defaults, "return a new dict"
        ''',
        "solution": r'''
            def with_defaults(data, defaults):
                return {**defaults, **data}
        ''',
        "hints": [
            "Two dicts can be unpacked into a new dict literal with **.",
            "When the same key appears twice, the later one wins - so put the defaults first.",
            "Return {**defaults, **data}.",
        ],
    },
    {
        "id": "structured-output-s7",
        "title": "Only allowed values",
        "difficulty": 0,
        "lesson": r'''
            ## Allowed values

            When your code branches on a field such as `sentiment`, it handles a fixed set of
            values: `"positive"`, `"negative"` and `"neutral"`. A model can reply with any
            string, for example `"kinda good"`, and no branch of your code handles that.

            A fixed list of allowed values is called an **enum**, short for "enumeration".
            `value in allowed` is `True` when the list `allowed` contains `value`.

            ```python
            allowed = ["positive", "negative", "neutral"]
            for value in ["negative", "kinda good", "Positive"]:
                if value in allowed:
                    print("ok:", value)
                else:
                    print("rejected:", value)
            # ok: negative
            # rejected: kinda good
            # rejected: Positive
            ```

            A function that checks a value raises `ValueError` instead of printing. The
            caller can then catch the exception and, for example, call the model again.

            String comparison is case-sensitive. `"Positive"` and `"positive"` are different
            strings, so `"Positive" in allowed` is `False`.
        ''',
        "prompt": r'''
            Make sure a field from the model is one of the allowed values.

            **Write:** `check_choice(value, allowed)`

            - `value`: a string from the model, e.g. `"negative"`
            - `allowed`: a list of allowed strings, e.g. `["positive", "negative", "neutral"]`
            - **Returns:** `value` unchanged if it is allowed

            **Rules**
            - If `value` is not in `allowed`, raise `ValueError` with the message
              `"invalid choice: <value>"`.
            - The check is case-sensitive: `"Positive"` is not allowed if only `"positive"` is.

            **Examples**
            ```python
            check_choice("negative", ["positive", "negative"])   # returns "negative"
            check_choice("meh", ["positive", "negative"])        # raises ValueError("invalid choice: meh")
            ```
        ''',
        "starter": r'''
            def check_choice(value, allowed):
                ...
        ''',
        "tests": r'''
            from solution import check_choice

            def test_allowed_value_is_returned():
                assert check_choice("negative", ["positive", "negative"]) == "negative"

            def test_unknown_value_raises_value_error():
                try:
                    check_choice("meh", ["positive", "negative"])
                except ValueError as e:
                    assert str(e) == "invalid choice: meh", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"

            def test_check_is_case_sensitive():
                try:
                    check_choice("Positive", ["positive"])
                except ValueError:
                    pass
                else:
                    assert False, "'Positive' is not in the allowed list"
        ''',
        "solution": r'''
            def check_choice(value, allowed):
                if value not in allowed:
                    raise ValueError(f"invalid choice: {value}")
                return value
        ''',
        "hints": [
            "Use `in` (or `not in`) to test the value against the list.",
            "If it's not allowed, raise; otherwise hand the value back.",
            "if value not in allowed: raise ValueError(f\"invalid choice: {value}\"). Then return value.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "structured-output-1",
        "title": "Parse without crashing",
        "difficulty": 1,
        "lesson": r'''
            ## Handling invalid JSON

            An invalid reply from a model is an expected event, not a reason to stop the
            program. Your code should report what was wrong, so that the next step can retry,
            log the problem or use a default value.

            `json.loads` raises `json.JSONDecodeError` when the text is not valid JSON. The
            `.msg` attribute of the exception is a short reason. Valid JSON is not always an
            object: `"[1, 2]"` parses to a list.

            ```python
            import json

            for text in ['{"a": 1}', "Sure!", "[1, 2]"]:
                try:
                    value = json.loads(text)
                    print("parsed a", type(value).__name__)
                except json.JSONDecodeError as error:
                    print("bad JSON:", error.msg)
            # parsed a dict
            # bad JSON: Expecting value
            # parsed a list
            ```

            Step through the loop and watch which lines run for each `text`.

            ```diagram
            {"type": "trace", "title": "try and except around json.loads", "code": ["import json", "", "for text in ['{\"a\": 1}', \"Sure!\", \"[1, 2]\"]:", "    try:", "        value = json.loads(text)", "        print(\"parsed a\", type(value).__name__)", "    except json.JSONDecodeError as error:", "        print(\"bad JSON:\", error.msg)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 3, "vars": {}, "out": ""},
              {"line": 4, "vars": {"text": "'{\"a\": 1}'"}, "out": ""},
              {"line": 5, "vars": {"text": "'{\"a\": 1}'"}, "out": ""},
              {"line": 6, "vars": {"text": "'{\"a\": 1}'", "value": "{'a': 1}"}, "out": ""},
              {"line": 3, "vars": {"text": "'{\"a\": 1}'", "value": "{'a': 1}"}, "out": "parsed a dict\n"},
              {"line": 4, "vars": {"text": "'Sure!'", "value": "{'a': 1}"}, "out": "parsed a dict\n"},
              {"line": 5, "vars": {"text": "'Sure!'", "value": "{'a': 1}"}, "out": "parsed a dict\n", "note": "json.loads raises JSONDecodeError here, so line 6 is skipped."},
              {"line": 7, "vars": {"text": "'Sure!'", "value": "{'a': 1}"}, "out": "parsed a dict\n"},
              {"line": 8, "vars": {"text": "'Sure!'", "value": "{'a': 1}", "error": "JSONDecodeError('Expecting value: line 1 column 1 (char 0)')"}, "out": "parsed a dict\n"},
              {"line": 3, "vars": {"text": "'Sure!'", "value": "{'a': 1}"}, "out": "parsed a dict\nbad JSON: Expecting value\n"},
              {"line": 4, "vars": {"text": "'[1, 2]'", "value": "{'a': 1}"}, "out": "parsed a dict\nbad JSON: Expecting value\n"},
              {"line": 5, "vars": {"text": "'[1, 2]'", "value": "{'a': 1}"}, "out": "parsed a dict\nbad JSON: Expecting value\n"},
              {"line": 6, "vars": {"text": "'[1, 2]'", "value": "[1, 2]"}, "out": "parsed a dict\nbad JSON: Expecting value\n"},
              {"line": 3, "vars": {"text": "'[1, 2]'", "value": "[1, 2]"}, "out": "parsed a dict\nbad JSON: Expecting value\nparsed a list\n"},
              {"line": null, "vars": {"text": "'[1, 2]'", "value": "[1, 2]"}, "out": "parsed a dict\nbad JSON: Expecting value\nparsed a list\n"}
            ]}
            ```

            A function can report a failure without raising. It returns a tuple of two
            values, `(result, error)`, and exactly one of the two is `None`. The caller
            unpacks the tuple into two names.

            ```python
            def to_int(text):
                try:
                    return int(text), None
                except ValueError:
                    return None, f"not an integer: {text}"

            number, error = to_int("12")
            print(number, error)
            # 12 None
            number, error = to_int("twelve")
            print(number, error)
            # None not an integer: twelve
            ```
        ''',
        "prompt": r'''
            Parse a model reply into a dict, returning an error message instead of raising.

            **Write:** `safe_parse(text)`

            - `text`: the model's reply string
            - **Returns:** a tuple `(data, error)`:
              - success: `(the dict, None)`
              - failure: `(None, an error message string)`

            **Rules**
            - Invalid JSON: the error is `"invalid JSON: "` followed by the exception's `.msg`,
              e.g. `"invalid JSON: Expecting value"`.
            - Valid JSON that is not an object (dict): the error is
              `"expected a JSON object, got <type name>"`, e.g. `"expected a JSON object, got list"`.
            - Never raise for bad input.

            **Examples**
            ```python
            safe_parse('{"a": 1}')    # returns ({"a": 1}, None)
            safe_parse("Sure!")       # returns (None, "invalid JSON: Expecting value")
            safe_parse("[1, 2]")      # returns (None, "expected a JSON object, got list")
            safe_parse('"hi"')        # returns (None, "expected a JSON object, got str")
            ```
        ''',
        "starter": r'''
            import json


            def safe_parse(text):
                ...
        ''',
        "tests": r'''
            from solution import safe_parse

            def test_valid_object():
                got = safe_parse('{"a": 1}')
                assert tuple(got) == ({"a": 1}, None), f"got {got!r}"

            def test_invalid_json_gives_reason():
                got = safe_parse("Sure!")
                assert tuple(got) == (None, "invalid JSON: Expecting value"), f"got {got!r}"

            def test_empty_reply_is_invalid_json():
                data, error = safe_parse("")
                assert data is None and error.startswith("invalid JSON: "), f"got {(data, error)!r}"

            def test_list_is_not_an_object():
                got = safe_parse("[1, 2]")
                assert tuple(got) == (None, "expected a JSON object, got list"), f"got {got!r}"

            def test_string_is_not_an_object():
                got = safe_parse('"hi"')
                assert tuple(got) == (None, "expected a JSON object, got str"), f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def safe_parse(text):
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as error:
                    return None, f"invalid JSON: {error.msg}"
                if not isinstance(data, dict):
                    return None, f"expected a JSON object, got {type(data).__name__}"
                return data, None
        ''',
        "hints": [
            "Two different failures: the text isn't JSON at all (an exception), or it is JSON but not a dict (a type check).",
            "Wrap json.loads in try/except json.JSONDecodeError and use the error's .msg. After parsing, check isinstance(data, dict).",
            "try: data = json.loads(text) / except json.JSONDecodeError as error: return None, f\"invalid JSON: {error.msg}\". If not a dict: return None with the type name from type(data).__name__. Else return data, None.",
        ],
    },
    {
        "id": "structured-output-2",
        "title": "Unwrap a code fence",
        "difficulty": 1,
        "lesson": r'''
            ## Code fences

            Models often format replies as **Markdown**: a plain-text format in which symbols
            mark headings, lists and code. A backtick is the slanted quote character on the
            key left of `1` on a US keyboard. A Markdown **code fence** is three
            backticks, optionally followed by a word such as `json`, then the content, then
            three backticks again. A model asked for JSON often puts it inside a code fence
            and writes sentences around the fence.

            Those sentences can contain braces, as in `Here is {your} data`. Slicing from the
            first `{` to the last `}` then returns text that is not valid JSON. When the reply
            has a fence, the JSON is the text inside the fence.

            A regular expression with a capture group extracts that text. In the example,
            `tick` is a string of three backticks.

            ```python
            import re

            tick = "`" * 3
            reply = f"Here is {{your}} data:\n{tick}json\n{{\"a\": 1}}\n{tick}\nEnjoy!"
            match = re.search(tick + r"(?:json)?\s*(.*?)" + tick, reply, re.DOTALL)
            print(repr(match.group(1)))
            # '{"a": 1}\n'
            ```

            `(?:json)?` matches the word `json` if it is there and does not capture it. `\s*`
            matches the whitespace after it. `(.*?)` is the capture group: it matches as few
            characters as possible, so it stops at the next three backticks. `re.DOTALL` makes
            `.` match newline characters as well.

            `match.group(1)` still ends with a newline. Call `.strip()` on it before parsing.

            When the reply has no fence, `re.search` returns `None`. In that case parse the
            whole reply.
        ''',
        "prompt": r'''
            Parse the JSON in a model reply that may be wrapped in a Markdown code fence.

            **Write:** `extract_json(reply)`

            - `reply`: the model's reply string
            - **Returns:** the parsed JSON value (usually a dict)

            **Rules**
            - A code fence is three backticks, optionally followed by `json`, then the content,
              then three backticks.
            - If the reply contains a code fence, parse **only the text inside the first fence**
              (ignore everything outside it, even if it contains braces).
            - Otherwise parse the whole reply, ignoring leading/trailing whitespace.
            - If the JSON is invalid, let `json.JSONDecodeError` propagate (don't catch it).

            **Examples**
            ```python
            extract_json('  {"a": 1}\n')                                  # returns {"a": 1}
            extract_json('Here is {your} data:\n```json\n{"a": 1}\n```')  # returns {"a": 1}
            extract_json('```\n{"b": [1, 2]}\n```')                       # returns {"b": [1, 2]}
            extract_json("no json here")                                  # raises json.JSONDecodeError
            ```
        ''',
        "starter": r'''
            import json


            def extract_json(reply):
                return json.loads(reply)
        ''',
        "tests": r'''
            import json
            from solution import extract_json

            T = "`" * 3

            def test_plain_json_with_whitespace():
                assert extract_json('  {"a": 1}\n') == {"a": 1}

            def test_fenced_json_with_braces_in_prose():
                reply = "Here is {your} data:\n" + T + 'json\n{"a": 1}\n' + T + "\nEnjoy {it}!"
                got = extract_json(reply)
                assert got == {"a": 1}, f"got {got!r}"

            def test_fence_without_language_tag():
                got = extract_json(T + '\n{"b": [1, 2]}\n' + T)
                assert got == {"b": [1, 2]}, f"got {got!r}"

            def test_uses_the_first_fence():
                reply = T + 'json\n{"n": 1}\n' + T + " and " + T + 'json\n{"n": 2}\n' + T
                assert extract_json(reply) == {"n": 1}

            def test_invalid_json_raises_decode_error():
                try:
                    extract_json("no json here")
                except json.JSONDecodeError:
                    pass
                else:
                    assert False, "expected json.JSONDecodeError"
        ''',
        "solution": r'''
            import json
            import re

            FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


            def extract_json(reply):
                match = FENCE.search(reply)
                text = match.group(1) if match else reply
                return json.loads(text.strip())
        ''',
        "hints": [
            "First decide which text to parse: the inside of the fence if there is one, else the whole reply.",
            "re.search with a capture group finds the first fence; it returns None when there is no fence. Use re.DOTALL so the content can span lines.",
            "match = re.search(r\"```(?:json)?\\s*(.*?)```\", reply, re.DOTALL); text = match.group(1) if match else reply; return json.loads(text.strip()).",
        ],
    },
    {
        "id": "structured-output-3",
        "title": "Check keys and types",
        "difficulty": 1,
        "lesson": r'''
            ## Checking keys and types

            A validator that stops at the first problem reports one problem per run. A
            validator that collects every problem in a list reports all of them at once, so
            they can all be fixed in one step.

            You can describe the data you expect as a dict that maps each key to a Python
            type. Types such as `str` and `int` are values, so you can store them in a dict
            and pass them to `isinstance`. Loop over the dict and append one string for each
            problem.

            ```python
            expected = {"name": str, "age": int}
            data = {"name": "Ada", "age": "36"}
            problems = []
            for key, kind in expected.items():
                value = data[key]
                if not isinstance(value, kind):
                    problems.append(f"{key} should be {kind.__name__}, got {type(value).__name__}")
            print(problems)
            # ['age should be int, got str']
            ```

            `kind.__name__` is the name of a type as a string: `int.__name__` is `"int"`.
            `type(value).__name__` is the name of the type of `value`. An empty `problems`
            list means the data is valid.

            This example reads `data[key]` without testing `key in data` first, so a missing
            key raises `KeyError`. A complete check tests for the key before it reads the
            value.

            `isinstance(True, int)` is `True` because `bool` is a subclass of `int`. A check
            for a number has to reject `bool` values with its own test.
        ''',
        "prompt": r'''
            Validate a parsed reply against a dict of expected Python types, collecting every problem.

            **Write:** `check_types(data, expected)`

            - `data`: a dict, e.g. `{"name": "Ada", "age": "36"}`
            - `expected`: a dict of key -> Python type, e.g. `{"name": str, "age": int}`
            - **Returns:** a list of problem strings, in the order of `expected`; `[]` if valid

            **Rules**
            - Missing key: `"missing key: <key>"`.
            - Wrong type: `"<key> should be <expected type name>, got <actual type name>"`,
              e.g. `"age should be int, got str"`.
            - Use `isinstance`, except that a `bool` value **never** passes an `int` or `float`
              check (it gives `"... got bool"`).
            - Extra keys in `data` are ignored.

            **Examples**
            ```python
            check_types({"name": "Ada", "age": 36}, {"name": str, "age": int})     # returns []
            check_types({"name": "Ada", "age": "36"}, {"name": str, "age": int})   # returns ["age should be int, got str"]
            check_types({"ok": True}, {"ok": bool, "n": int})                      # returns ["missing key: n"]
            check_types({"n": True}, {"n": int})                                   # returns ["n should be int, got bool"]
            ```
        ''',
        "starter": r'''
            def check_types(data, expected):
                ...
        ''',
        "tests": r'''
            from solution import check_types

            def test_valid_data_gives_empty_list():
                assert check_types({"name": "Ada", "age": 36}, {"name": str, "age": int}) == []

            def test_wrong_type_is_reported():
                got = check_types({"name": "Ada", "age": "36"}, {"name": str, "age": int})
                assert got == ["age should be int, got str"], f"got {got!r}"

            def test_missing_key_is_reported():
                got = check_types({"ok": True}, {"ok": bool, "n": int})
                assert got == ["missing key: n"], f"got {got!r}"

            def test_bool_is_not_a_number():
                got = check_types({"n": True, "x": False}, {"n": int, "x": float})
                assert got == ["n should be int, got bool", "x should be float, got bool"], f"got {got!r}"

            def test_all_problems_in_expected_order_and_extras_ignored():
                got = check_types({"b": 1, "extra": 0}, {"a": str, "b": str, "c": list})
                assert got == ["missing key: a", "b should be str, got int", "missing key: c"], f"got {got!r}"
        ''',
        "solution": r'''
            def check_types(data, expected):
                problems = []
                for key, kind in expected.items():
                    if key not in data:
                        problems.append(f"missing key: {key}")
                        continue
                    value = data[key]
                    is_bad_bool = isinstance(value, bool) and kind in (int, float)
                    if is_bad_bool or not isinstance(value, kind):
                        problems.append(f"{key} should be {kind.__name__}, got {type(value).__name__}")
                return problems
        ''',
        "hints": [
            "Loop over expected.items() and collect problem strings in a list; check 'missing' before checking the type.",
            "For each key: if it's missing, add the missing message and move on. Otherwise, it's wrong if it's a bool while an int/float is expected, or if isinstance fails.",
            "problems = []; for key, kind in expected.items(): if key not in data: append + continue; value = data[key]; if (isinstance(value, bool) and kind in (int, float)) or not isinstance(value, kind): append the message using kind.__name__ and type(value).__name__; return problems.",
        ],
    },
    {
        "id": "structured-output-4",
        "title": "Normalize a ticket",
        "difficulty": 1,
        "lesson": r'''
            ## Normalizing a reply

            A reply can be usable without being exact. `"  HIGH "` means `"high"`, and a
            missing optional field can take its default. To **normalize** a value is to
            convert it to one standard form, for example by removing spaces and lowercasing.
            Normalize first, and reject only the values that are still not allowed afterwards.

            This step combines three things you have already used: defaults, normalizing and
            an enum check.

            ```python
            ALLOWED = ["low", "medium", "high"]
            raw = {"title": "Login broken", "priority": "  HIGH ", "mood": "sad"}
            priority = raw.get("priority", "medium").strip().lower()
            print(repr(priority), priority in ALLOWED)
            # 'high' True
            clean = {"title": raw["title"], "priority": priority}
            print(clean)
            # {'title': 'Login broken', 'priority': 'high'}
            ```

            `raw.get(key, default)` returns `raw[key]` when the key is present and `default`
            when it is missing. `.strip()` removes the spaces at both ends and `.lower()`
            lowercases the result.

            `clean` is a new dict that contains only the keys you list. The extra key
            `"mood"` that the model added is not copied, and `raw` is unchanged.

            A default that is a list must be a new list on every call. `raw.get("tags", [])`
            evaluates `[]` each time it runs, so each call creates its own list. If you store
            one list in a constant and use it as the default, every ticket refers to the same
            list object, and appending a tag to one ticket changes all of them.
        ''',
        "prompt": r'''
            Turn a parsed model reply into a clean support ticket.

            **Write:** `normalize_ticket(data)`

            - `data`: a dict from the model, e.g. `{"title": "Login broken", "priority": " HIGH "}`
            - **Returns:** a new dict with exactly the keys `"title"`, `"priority"`, `"tags"`

            **Rules**
            - `"title"` is required: if missing, raise `ValueError("missing field: title")`.
            - `"priority"` defaults to `"medium"`. Strip spaces and lowercase it; it must then be
              one of `"low"`, `"medium"`, `"high"`, else raise `ValueError` with the message
              `"invalid priority: <original value>"`.
            - `"tags"` defaults to a **new** empty list `[]` each call.
            - Any other keys are dropped. Don't modify `data`.

            **Examples**
            ```python
            normalize_ticket({"title": "Login broken", "priority": " HIGH "})
            # returns {"title": "Login broken", "priority": "high", "tags": []}
            normalize_ticket({"title": "Typo", "tags": ["docs"], "mood": "sad"})
            # returns {"title": "Typo", "priority": "medium", "tags": ["docs"]}
            normalize_ticket({"title": "X", "priority": "urgent"})   # raises ValueError("invalid priority: urgent")
            normalize_ticket({"priority": "low"})                    # raises ValueError("missing field: title")
            ```
        ''',
        "starter": r'''
            def normalize_ticket(data):
                ...
        ''',
        "tests": r'''
            from solution import normalize_ticket

            def test_priority_is_cleaned_and_tags_defaulted():
                got = normalize_ticket({"title": "Login broken", "priority": " HIGH "})
                assert got == {"title": "Login broken", "priority": "high", "tags": []}, f"got {got!r}"

            def test_priority_default_and_extra_keys_dropped():
                got = normalize_ticket({"title": "Typo", "tags": ["docs"], "mood": "sad"})
                assert got == {"title": "Typo", "priority": "medium", "tags": ["docs"]}, f"got {got!r}"

            def test_invalid_priority_raises_with_original_value():
                try:
                    normalize_ticket({"title": "X", "priority": "Urgent"})
                except ValueError as e:
                    assert str(e) == "invalid priority: Urgent", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"

            def test_missing_title_raises():
                try:
                    normalize_ticket({"priority": "low"})
                except ValueError as e:
                    assert str(e) == "missing field: title", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"

            def test_default_tags_not_shared_and_input_unchanged():
                data = {"title": "A"}
                a = normalize_ticket(data)
                b = normalize_ticket({"title": "B"})
                a["tags"].append("x")
                assert b["tags"] == [], "the default tags list is shared between calls"
                assert data == {"title": "A"}, "the input dict was changed"
        ''',
        "solution": r'''
            ALLOWED = ["low", "medium", "high"]


            def normalize_ticket(data):
                if "title" not in data:
                    raise ValueError("missing field: title")
                raw_priority = data.get("priority", "medium")
                priority = raw_priority.strip().lower()
                if priority not in ALLOWED:
                    raise ValueError(f"invalid priority: {raw_priority}")
                return {"title": data["title"], "priority": priority, "tags": data.get("tags", [])}
        ''',
        "hints": [
            "Handle it in order: required field, then priority (default, clean, check), then tags; build a brand-new dict at the end.",
            "Use data.get(key, default) for the optional fields. Keep the original priority value around for the error message.",
            "If \"title\" not in data: raise. raw = data.get(\"priority\", \"medium\"); p = raw.strip().lower(); if p not in the allowed list: raise with raw. Return {\"title\": ..., \"priority\": p, \"tags\": data.get(\"tags\", [])}.",
        ],
    },
    {
        "id": "structured-output-5",
        "title": "Numbers sent as text",
        "difficulty": 1,
        "lesson": r'''
            ## Type coercion

            Models sometimes put a number in quotes: `"42"` or `"3.5"` instead of `42` or
            `3.5`. The value is a string, so arithmetic on it fails or gives the wrong result.
            You can reject such a reply, or you can convert the string to the number it
            contains. Converting a value from one type to another is called **type coercion**.

            `int("42")` returns `42`. `int("3.5")` raises `ValueError`, because `int` only
            parses whole numbers. `float("3.5")` returns `3.5`. Try `int` first, then `float`,
            and report a failure only when both raise.

            ```python
            for text in ["42", "3.5", "lots"]:
                try:
                    print(int(text))
                except ValueError:
                    try:
                        print(float(text))
                    except ValueError:
                        print("not a number:", text)
            # 42
            # 3.5
            # not a number: lots
            ```

            The order matters. `float("42")` returns `42.0`, so trying `float` first would
            turn every whole number into a float.

            Coerce only the fields that should hold numbers, and only when the value is a
            string. `isinstance(value, str)` tests that. A value that is already an `int`, a
            `float` or a `bool` stays as it is.
        ''',
        "prompt": r'''
            Convert number fields that the model sent as strings into real numbers.

            **Write:** `coerce_numbers(data, fields)`

            - `data`: a dict, e.g. `{"qty": "3", "price": "9.5", "name": "pen"}`
            - `fields`: a list of keys that should hold numbers, e.g. `["qty", "price"]`
            - **Returns:** a **new** dict with those fields converted

            **Rules**
            - Only convert values that are strings. Convert with `int` if possible, otherwise
              `float`.
            - If a string can't be converted by either, raise `ValueError` with the message
              `"not a number: <field>"`.
            - Values that are not strings (ints, floats, bools, ...) are left unchanged.
            - Fields listed in `fields` but missing from `data` are skipped.
            - Other keys are copied unchanged. Don't modify `data`.

            **Examples**
            ```python
            coerce_numbers({"qty": "3", "price": "9.5", "name": "pen"}, ["qty", "price"])
            # returns {"qty": 3, "price": 9.5, "name": "pen"}
            coerce_numbers({"qty": 2}, ["qty", "price"])        # returns {"qty": 2}
            coerce_numbers({"qty": "a few"}, ["qty"])           # raises ValueError("not a number: qty")
            ```
        ''',
        "starter": r'''
            def coerce_numbers(data, fields):
                ...
        ''',
        "tests": r'''
            from solution import coerce_numbers

            def test_converts_int_and_float_strings():
                got = coerce_numbers({"qty": "3", "price": "9.5", "name": "pen"}, ["qty", "price"])
                assert got == {"qty": 3, "price": 9.5, "name": "pen"}, f"got {got!r}"
                assert isinstance(got["qty"], int), "\"3\" should become an int, not a float"

            def test_non_strings_and_missing_fields_untouched():
                got = coerce_numbers({"qty": 2, "flag": True}, ["qty", "flag", "price"])
                assert got == {"qty": 2, "flag": True}, f"got {got!r}"
                assert got["flag"] is True

            def test_unconvertible_string_raises():
                try:
                    coerce_numbers({"qty": "a few"}, ["qty"])
                except ValueError as e:
                    assert str(e) == "not a number: qty", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"

            def test_input_not_modified():
                data = {"qty": "3"}
                got = coerce_numbers(data, ["qty"])
                assert data == {"qty": "3"}, "the input dict was changed"
                assert got == {"qty": 3}
        ''',
        "solution": r'''
            def coerce_numbers(data, fields):
                result = dict(data)
                for field in fields:
                    value = result.get(field)
                    if not isinstance(value, str):
                        continue
                    try:
                        result[field] = int(value)
                    except ValueError:
                        try:
                            result[field] = float(value)
                        except ValueError:
                            raise ValueError(f"not a number: {field}")
                return result
        ''',
        "hints": [
            "Copy the dict first, then loop over the fields and only touch values that are strings.",
            "Try int(value); if that raises ValueError, try float(value); if that also fails, raise your own ValueError.",
            "result = dict(data); for field in fields: value = result.get(field); skip if not isinstance(value, str); nested try/except: int, then float, else raise ValueError(f\"not a number: {field}\"); return result.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "structured-output-6",
        "title": "A tiny JSON Schema checker",
        "difficulty": 2,
        "placement": True,
        "research": {
            "note": "Read how JSON Schema describes types (`string`, `integer`, `number`, ...), "
                    "`properties`, `required` and `enum`. Real projects use the `jsonschema` package "
                    "or Pydantic for this - here you build a tiny version.",
            "links": [
                {"title": "JSON Schema: type-specific keywords",
                 "url": "https://json-schema.org/understanding-json-schema/reference/type"},
                {"title": "JSON Schema: getting started step by step",
                 "url": "https://json-schema.org/learn/getting-started-step-by-step"},
            ],
        },
        "lesson": r'''
            ## JSON Schema

            A dict such as `{"age": int}` describes expected data in a format that only your
            own code understands. A **schema** is a description of the shape of data.
            **JSON Schema** is the standard format for writing one. A schema is a JSON
            object. `"type"` names the type of the data. `"properties"` maps each key of
            the data to a schema for its value. `"required"` lists the keys that must be
            present. `"enum"` lists the allowed values. Model providers accept JSON Schema
            for structured outputs.

            In this exercise you check a small part of JSON Schema: `type`, `properties`,
            `required` and `enum`. One trap: in Python `isinstance(True, int)` is `True`,
            because `bool` is a subclass of `int`. JSON Schema still treats them as
            different types, so your checks for `"integer"` and `"number"` must reject
            `True` and `False` explicitly (check for `bool` first).
        ''',
        "prompt": r'''
            Validate data against a small subset of JSON Schema and return every problem found.

            **Write:** `validate(data, schema)`

            - `data`: any parsed JSON value, e.g. `{"name": "Ada", "age": 36}`
            - `schema`: a dict like
              `{"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name"]}`
              (`properties` and `required` may be missing)
            - **Returns:** a list of error strings; `[]` means valid

            **Rules**
            - If `data` is not a dict, return `["expected object"]` (nothing else is checked).
            - First, for each key in `required` (in order) that is missing from `data`:
              `"missing required property: <key>"`.
            - Then, for each property in `properties` (in order) that **is** present in `data`:
              - if it has a `"type"` and the value doesn't match: `"<key>: expected <type>"`
              - else if it has an `"enum"` list and the value is not in it:
                `"<key>: must be one of <enum values joined with ', '>"`
            - Type names: `"string"` = str, `"integer"` = int, `"number"` = int or float,
              `"boolean"` = bool, `"array"` = list, `"object"` = dict. A bool is **never** an
              `"integer"` or `"number"`.
            - Keys in `data` that are not in `properties` are ignored.

            **Examples**
            ```python
            schema = {"type": "object",
                      "properties": {"name": {"type": "string"},
                                     "age": {"type": "integer"},
                                     "mood": {"type": "string", "enum": ["happy", "sad"]}},
                      "required": ["name", "age"]}
            validate({"name": "Ada", "age": 36}, schema)                   # returns []
            validate({"name": 5, "mood": "meh"}, schema)
            # returns ["missing required property: age", "name: expected string",
            #          "mood: must be one of happy, sad"]
            validate({"name": "A", "age": True}, schema)                   # returns ["age: expected integer"]
            validate([1, 2], schema)                                       # returns ["expected object"]
            ```
        ''',
        "starter": r'''
            def validate(data, schema):
                ...
        ''',
        "tests": r'''
            from solution import validate

            SCHEMA = {"type": "object",
                      "properties": {"name": {"type": "string"},
                                     "age": {"type": "integer"},
                                     "mood": {"type": "string", "enum": ["happy", "sad"]}},
                      "required": ["name", "age"]}

            def test_valid_data():
                assert validate({"name": "Ada", "age": 36}, SCHEMA) == []
                assert validate({"name": "Ada", "age": 36, "mood": "sad", "extra": 1}, SCHEMA) == []

            def test_missing_then_type_then_enum_errors_in_order():
                got = validate({"name": 5, "mood": "meh"}, SCHEMA)
                want = ["missing required property: age", "name: expected string", "mood: must be one of happy, sad"]
                assert got == want, f"got {got!r}"

            def test_bool_is_not_integer_or_number():
                assert validate({"name": "A", "age": True}, SCHEMA) == ["age: expected integer"]
                s = {"properties": {"x": {"type": "number"}}}
                assert validate({"x": False}, s) == ["x: expected number"]

            def test_number_accepts_int_and_float():
                s = {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}}}
                assert validate({"x": 1, "y": 2.5}, s) == []

            def test_other_types():
                s = {"properties": {"a": {"type": "array"}, "o": {"type": "object"}, "b": {"type": "boolean"}}}
                assert validate({"a": [], "o": {}, "b": False}, s) == []
                got = validate({"a": "x", "o": [], "b": 1}, s)
                assert got == ["a: expected array", "o: expected object", "b: expected boolean"], f"got {got!r}"

            def test_non_object_data():
                assert validate([1, 2], SCHEMA) == ["expected object"]
                assert validate("hi", {}) == ["expected object"]

            def test_schema_without_properties_or_required():
                assert validate({"anything": 1}, {"type": "object"}) == []
        ''',
        "solution": r'''
            TYPES = {"string": str, "integer": int, "number": (int, float),
                     "boolean": bool, "array": list, "object": dict}


            def matches(value, type_name):
                if isinstance(value, bool) and type_name in ("integer", "number"):
                    return False
                return isinstance(value, TYPES[type_name])


            def validate(data, schema):
                if not isinstance(data, dict):
                    return ["expected object"]
                errors = []
                for key in schema.get("required", []):
                    if key not in data:
                        errors.append(f"missing required property: {key}")
                for key, rule in schema.get("properties", {}).items():
                    if key not in data:
                        continue
                    value = data[key]
                    if "type" in rule and not matches(value, rule["type"]):
                        errors.append(f"{key}: expected {rule['type']}")
                    elif "enum" in rule and value not in rule["enum"]:
                        errors.append(f"{key}: must be one of " + ", ".join(str(v) for v in rule["enum"]))
                return errors
        ''',
        "hints": [
            "A dict mapping JSON Schema type names to Python types (a tuple for 'number') does most of the type work. Remember the bool gotcha.",
            "Check the data is a dict first. Then loop over required for missing keys, then over properties for the present keys: type check first, enum check only if the type was fine.",
            "TYPES = {...}; a helper matches(value, name) that returns False for bools when name is integer/number, else isinstance. validate: non-dict -> [\"expected object\"]; loop schema.get(\"required\", []); loop schema.get(\"properties\", {}).items(), skipping missing keys, with if/elif for type then enum; return the list.",
        ],
    },
    {
        "id": "structured-output-7",
        "title": "Retry with error feedback",
        "difficulty": 2,
        "research": {
            "note": "Skim how providers enforce structured outputs natively (you pass a JSON "
                    "Schema and the API guarantees the shape). Even then, apps keep a validation "
                    "and retry layer like the one you're about to write.",
            "links": [
                {"title": "OpenAI docs: structured outputs",
                 "url": "https://platform.openai.com/docs/guides/structured-outputs"},
                {"title": "Anthropic docs: structured outputs",
                 "url": "https://docs.claude.com/en/docs/build-with-claude/structured-outputs"},
            ],
        },
        "lesson": r'''
            ## Retry with error feedback

            When a reply is not valid, calling the model again with the same messages often
            produces the same mistake. Tell the model what was wrong. Add the invalid reply
            as an `assistant` message and the reason as a `user` message, then call the model
            again with the longer list.

            Step through one failed attempt and see which messages the next call receives.

            ```diagram
            {"type":"flow","title":"Retry loop with feedback","steps":[
            {"label":"Call the model","detail":"llm(conversation) returns the reply text. The first call receives a copy of the starting messages.","code":"conversation = [\n  {'role': 'user', 'content': 'Sentiment of \"slow app\" as JSON'}\n]\nreply = 'It is negative.'"},
            {"label":"Parse and check","detail":"json.loads(reply) raises JSONDecodeError for this reply, and its .msg is the reason. A reply that parses to a dict is valid and is returned at this stage.","code":"reason = 'Expecting value'"},
            {"label":"Add feedback","detail":"Build a new list: the earlier messages, the invalid reply as an assistant message and the reason as a user message.","code":"conversation = [\n  {'role': 'user', 'content': 'Sentiment of \"slow app\" as JSON'},\n  {'role': 'assistant', 'content': 'It is negative.'},\n  {'role': 'user', 'content': 'Not valid JSON: Expecting value.'}\n]"},
            {"label":"Stop","detail":"The loop ends in one of two ways. A valid reply is returned as a dict. After the maximum number of calls without a valid reply, the function raises ValueError.","code":"{'sentiment': 'negative'}"}
            ],"loop":{"from":2,"to":0,"label":"while attempts remain"}}
            ```

            Always limit the number of attempts. In the tests, `llm` is a plain Python function
            that returns prepared replies in order. No real model is called.
        ''',
        "prompt": r'''
            Call a model until it returns a JSON object, feeding the parse error back each time.

            **Write:** `ask_json(llm, messages, max_attempts=3)`

            - `llm`: a function; `llm(messages)` takes a list of message dicts and returns the
              reply text (a string)
            - `messages`: the starting list of message dicts
            - `max_attempts`: an int, the most times `llm` may be called
            - **Returns:** the parsed dict from the first valid reply

            **Rules**
            - Parse each reply with `json.loads` (surrounding whitespace is fine).
            - A reply is valid only if it parses **and** is a dict.
            - After an invalid reply, add two messages to the conversation before the next call:
              - `{"role": "assistant", "content": <the bad reply>}`
              - `{"role": "user", "content": "Invalid reply: <reason>. Reply with only a JSON object."}`
                where `<reason>` is the `JSONDecodeError`'s `.msg` (e.g. `Expecting value`), or
                `expected a JSON object` when it parsed but isn't a dict.
            - Call `llm` at most `max_attempts` times. If none is valid, raise `ValueError` with
              the message `"no valid JSON after <max_attempts> attempts"`.
            - Don't modify the caller's `messages` list (work on a copy).

            **Examples**
            ```python
            replies = iter(["Sure! Here you go", '{"city": "Paris"}'])
            def fake_llm(msgs):
                return next(replies)

            ask_json(fake_llm, [{"role": "user", "content": "Capital of France as JSON"}])
            # returns {"city": "Paris"}
            # the 2nd call received 3 messages; the last one was:
            # {"role": "user", "content": "Invalid reply: Expecting value. Reply with only a JSON object."}
            ```
        ''',
        "starter": r'''
            import json


            def ask_json(llm, messages, max_attempts=3):
                ...
        ''',
        "tests": r'''
            from solution import ask_json

            def scripted(*replies):
                calls = []
                def llm(messages):
                    calls.append([dict(m) for m in messages])
                    return replies[min(len(calls), len(replies)) - 1]
                return llm, calls

            START = [{"role": "user", "content": "Capital of France as JSON"}]

            def test_first_valid_reply_is_returned():
                llm, calls = scripted(' {"city": "Paris"}\n')
                assert ask_json(llm, START) == {"city": "Paris"}
                assert len(calls) == 1 and calls[0] == START

            def test_bad_reply_and_feedback_are_sent_on_retry():
                llm, calls = scripted("Sure! Here you go", '{"city": "Paris"}')
                assert ask_json(llm, START) == {"city": "Paris"}
                assert len(calls) == 2, f"llm was called {len(calls)} times"
                assert calls[1] == START + [
                    {"role": "assistant", "content": "Sure! Here you go"},
                    {"role": "user", "content": "Invalid reply: Expecting value. Reply with only a JSON object."},
                ], f"second call got {calls[1]!r}"

            def test_non_object_json_is_rejected():
                llm, calls = scripted("[1, 2]", '{"ok": true}')
                assert ask_json(llm, START) == {"ok": True}
                assert calls[1][-1]["content"] == "Invalid reply: expected a JSON object. Reply with only a JSON object."

            def test_feedback_accumulates_over_attempts():
                llm, calls = scripted("a", "b", '{"n": 3}')
                assert ask_json(llm, START) == {"n": 3}
                assert len(calls[2]) == 5, f"third call got {len(calls[2])} messages"

            def test_gives_up_after_max_attempts():
                llm, calls = scripted("nope")
                try:
                    ask_json(llm, START, max_attempts=2)
                except ValueError as e:
                    assert str(e) == "no valid JSON after 2 attempts", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
                assert len(calls) == 2, f"llm was called {len(calls)} times"

            def test_callers_messages_not_modified():
                start = [{"role": "user", "content": "q"}]
                llm, calls = scripted("x", '{"a": 1}')
                ask_json(llm, start)
                assert start == [{"role": "user", "content": "q"}], "the caller's list was changed"
        ''',
        "solution": r'''
            import json


            def ask_json(llm, messages, max_attempts=3):
                conversation = list(messages)
                for _ in range(max_attempts):
                    reply = llm(conversation)
                    try:
                        data = json.loads(reply)
                    except json.JSONDecodeError as error:
                        reason = error.msg
                    else:
                        if isinstance(data, dict):
                            return data
                        reason = "expected a JSON object"
                    conversation = conversation + [
                        {"role": "assistant", "content": reply},
                        {"role": "user", "content": f"Invalid reply: {reason}. Reply with only a JSON object."},
                    ]
                raise ValueError(f"no valid JSON after {max_attempts} attempts")
        ''',
        "hints": [
            "A for loop over range(max_attempts) gives you the attempt limit for free; raise after the loop.",
            "Inside the loop: call llm on your copy of the conversation, try to parse, return on a dict, otherwise work out the reason and append the assistant + user feedback messages.",
            "conversation = list(messages). for _ in range(max_attempts): reply = llm(conversation); try json.loads -> except JSONDecodeError as e: reason = e.msg; else: return if dict, reason = \"expected a JSON object\"; append the two messages. After the loop: raise ValueError(f\"no valid JSON after {max_attempts} attempts\").",
        ],
    },
    {
        "id": "structured-output-8",
        "title": "Schema-guided extraction",
        "difficulty": 3,
        "prompt": r'''
            The full structured-output loop: ask for JSON matching a schema, extract it from the
            reply, validate it, feed problems back, and fill in defaults.

            **Write:** `extract_with_schema(llm, text, schema, max_attempts=3)`

            - `llm`: a function; `llm(messages)` returns the reply text
            - `text`: the input text to extract data from
            - `schema`: a JSON-Schema-like dict with `"properties"` (each may have `"type"` and
              `"default"`) and optional `"required"`
            - `max_attempts`: the most times `llm` may be called
            - **Returns:** the validated dict, with defaults filled in

            **Conversation**
            - Start with two messages:
              `{"role": "system", "content": "Extract the data as a JSON object matching this JSON Schema:\n" + json.dumps(schema)}`
              and `{"role": "user", "content": text}`.
            - After an invalid reply, append `{"role": "assistant", "content": <reply>}` and
              `{"role": "user", "content": "Fix these problems and reply with only the JSON object: " + <problems joined with "; ">}`.

            **Checking a reply** (produces a list of problems; empty = valid)
            - If the reply contains a code fence (three backticks, optional `json`), use only
              the text inside the first fence; otherwise the whole reply. Strip whitespace.
            - Invalid JSON: the only problem is `"invalid JSON: <error .msg>"`.
            - Parsed but not a dict: the only problem is `"expected a JSON object"`.
            - Otherwise: `"missing required property: <key>"` for each missing `required` key (in
              order), then `"<key>: expected <type>"` for each present property whose value
              doesn't match its `"type"` (in `properties` order). Types as in JSON Schema:
              string, integer, number, boolean, array, object; a bool is never an integer/number.

            **Rules**
            - On a valid reply, add `"default"` values for properties that are missing, then return.
            - If no reply is valid after `max_attempts` calls, raise `ValueError` with
              `"extraction failed: "` + the last reply's problems joined with `"; "`.

            **Examples**
            ```python
            schema = {"type": "object",
                      "properties": {"name": {"type": "string"},
                                     "age": {"type": "integer"},
                                     "country": {"type": "string", "default": "unknown"}},
                      "required": ["name", "age"]}
            # replies: '{"name": "Ada", "age": "36"}', then '```json\n{"name": "Ada", "age": 36}\n```'
            extract_with_schema(llm, "Ada is 36.", schema)
            # returns {"name": "Ada", "age": 36, "country": "unknown"}
            # the 2nd call's last message content:
            # "Fix these problems and reply with only the JSON object: age: expected integer"
            ```
        ''',
        "starter": r'''
            import json


            def extract_with_schema(llm, text, schema, max_attempts=3):
                ...
        ''',
        "tests": r'''
            import json
            from solution import extract_with_schema

            T = "`" * 3
            FIX = "Fix these problems and reply with only the JSON object: "
            SCHEMA = {"type": "object",
                      "properties": {"name": {"type": "string"},
                                     "age": {"type": "integer"},
                                     "country": {"type": "string", "default": "unknown"}},
                      "required": ["name", "age"]}

            def scripted(*replies):
                calls = []
                def llm(messages):
                    calls.append([dict(m) for m in messages])
                    return replies[min(len(calls), len(replies)) - 1]
                return llm, calls

            def test_first_call_messages():
                llm, calls = scripted('{"name": "Ada", "age": 36, "country": "UK"}')
                got = extract_with_schema(llm, "Ada is 36.", SCHEMA)
                assert got == {"name": "Ada", "age": 36, "country": "UK"}, f"got {got!r}"
                system = "Extract the data as a JSON object matching this JSON Schema:\n" + json.dumps(SCHEMA)
                assert calls[0] == [{"role": "system", "content": system},
                                    {"role": "user", "content": "Ada is 36."}], f"first call got {calls[0]!r}"

            def test_type_problem_fed_back_then_fenced_reply_accepted_with_default():
                llm, calls = scripted('{"name": "Ada", "age": "36"}', T + 'json\n{"name": "Ada", "age": 36}\n' + T)
                got = extract_with_schema(llm, "Ada is 36.", SCHEMA)
                assert got == {"name": "Ada", "age": 36, "country": "unknown"}, f"got {got!r}"
                assert calls[1][-2] == {"role": "assistant", "content": '{"name": "Ada", "age": "36"}'}
                assert calls[1][-1] == {"role": "user", "content": FIX + "age: expected integer"}, f"got {calls[1][-1]!r}"

            def test_missing_and_type_problems_joined_in_order():
                llm, calls = scripted('{"age": true}', '{"name": "A", "age": 1}')
                extract_with_schema(llm, "x", SCHEMA)
                want = FIX + "missing required property: name; age: expected integer"
                assert calls[1][-1]["content"] == want, f"got {calls[1][-1]['content']!r}"

            def test_invalid_json_and_non_object_problems():
                llm, calls = scripted("sorry", "[1]", '{"name": "A", "age": 1}')
                extract_with_schema(llm, "x", SCHEMA)
                assert calls[1][-1]["content"] == FIX + "invalid JSON: Expecting value"
                assert calls[2][-1]["content"] == FIX + "expected a JSON object"
                assert len(calls[2]) == 6

            def test_gives_up_with_last_problems():
                llm, calls = scripted('{"name": 1}')
                try:
                    extract_with_schema(llm, "x", SCHEMA, max_attempts=2)
                except ValueError as e:
                    want = "extraction failed: missing required property: age; name: expected string"
                    assert str(e) == want, f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
                assert len(calls) == 2, f"llm was called {len(calls)} times"
        ''',
        "solution": r'''
            import json
            import re

            FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
            TYPES = {"string": str, "integer": int, "number": (int, float),
                     "boolean": bool, "array": list, "object": dict}


            def matches(value, type_name):
                if isinstance(value, bool) and type_name in ("integer", "number"):
                    return False
                return isinstance(value, TYPES[type_name])


            def check(reply, schema):
                match = FENCE.search(reply)
                raw = (match.group(1) if match else reply).strip()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError as error:
                    return None, [f"invalid JSON: {error.msg}"]
                if not isinstance(data, dict):
                    return None, ["expected a JSON object"]
                problems = []
                for key in schema.get("required", []):
                    if key not in data:
                        problems.append(f"missing required property: {key}")
                for key, rule in schema.get("properties", {}).items():
                    if key in data and "type" in rule and not matches(data[key], rule["type"]):
                        problems.append(f"{key}: expected {rule['type']}")
                return data, problems


            def extract_with_schema(llm, text, schema, max_attempts=3):
                messages = [
                    {"role": "system",
                     "content": "Extract the data as a JSON object matching this JSON Schema:\n" + json.dumps(schema)},
                    {"role": "user", "content": text},
                ]
                problems = []
                for _ in range(max_attempts):
                    reply = llm(messages)
                    data, problems = check(reply, schema)
                    if not problems:
                        for key, rule in schema.get("properties", {}).items():
                            if key not in data and "default" in rule:
                                data[key] = rule["default"]
                        return data
                    messages = messages + [
                        {"role": "assistant", "content": reply},
                        {"role": "user", "content": "Fix these problems and reply with only the JSON object: "
                                                    + "; ".join(problems)},
                    ]
                raise ValueError("extraction failed: " + "; ".join(problems))
        ''',
        "hints": [
            "Reuse what you built: fence extraction (structured-output-2), the schema checks (structured-output-6) and the retry loop (structured-output-7). Put the checking in its own helper that returns (data, problems).",
            "The helper: pick the text (fence or whole), parse (return a single problem on failure), check it's a dict, then collect missing-required and wrong-type problems. The main loop: call, check, return with defaults if there are no problems, else append the two feedback messages.",
            "messages = [system, user]; for _ in range(max_attempts): reply = llm(messages); data, problems = check(reply, schema); if not problems: fill defaults from properties and return data; else append assistant reply + the 'Fix these problems...' message. After the loop raise ValueError(\"extraction failed: \" + \"; \".join(problems)).",
        ],
    },
]
