TOPIC = {
    "id": "json",
    "title": "JSON",
    "track": "working-python",
    "order": 3,
    "requires": ["dicts", "errors"],
    "summary": """
        Parsing and producing JSON: loads/dumps, files, JSONL, nested API responses,
        malformed input and pulling JSON out of chatty LLM replies.
    """,
    "concepts": ["json.loads", "json.dumps", "indent / sort_keys", "JSONDecodeError",
                 "nested navigation", "json.load / json.dump", "JSONL", "default=",
                 "round-tripping"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["json", "loads", "dumps", "parse", "serialize", "indent", "sort_keys",
                 "jsondecodeerror", "invalid json", "jsonl", "nested", "null", "true false",
                 "import"],
    "cards": [
        {
            "syntax": "data = json.loads(text)",
            "explain": "Parses JSON text and returns the Python value: object to dict, array to list, true/false/null to True/False/None.",
            "example": r'''
                import json
                data = json.loads('{"name": "Ada", "ok": true, "tags": []}')
                print(type(data).__name__, data["name"])
                # dict Ada
                print(data["ok"], data["tags"])
                # True []
            ''',
        },
        {
            "syntax": "text = json.dumps(value)",
            "explain": "Returns the value as JSON text, a string. Keys and strings get double quotes. True and None become true and null.",
            "example": r'''
                import json
                text = json.dumps({"lang": "fr", "beta": True, "limit": None})
                print(text)
                # {"lang": "fr", "beta": true, "limit": null}
                print(type(text).__name__)
                # str
            ''',
        },
        {
            "syntax": "json.dumps(value, indent=2, sort_keys=True)",
            "explain": "indent=2 puts each item on its own line, indented 2 spaces per level. sort_keys=True writes keys in alphabetical order.",
            "example": r'''
                import json
                print(json.dumps({"b": 1, "a": [2]}, indent=2, sort_keys=True))
                # {
                #   "a": [
                #     2
                #   ],
                #   "b": 1
                # }
            ''',
        },
        {
            "syntax": 'data["choices"][0]["message"]',
            "explain": "Reads nested data one level per pair of brackets: a key for a dict, an index for a list. .get(key, default) for a key that may be missing.",
            "example": r'''
                import json
                data = json.loads('{"choices": [{"message": "Hello!"}]}')
                print(data["choices"][0]["message"])
                # Hello!
                print(data.get("usage", {}).get("total_tokens", 0))
                # 0
            ''',
        },
        {
            "syntax": "except json.JSONDecodeError as exc:",
            "explain": "json.loads raises JSONDecodeError for text that is not valid JSON. exc.pos is the index where parsing failed.",
            "example": r'''
                import json
                try:
                    json.loads('{"city": Paris}')
                except json.JSONDecodeError as exc:
                    print("invalid JSON at index", exc.pos)
                # invalid JSON at index 9
            ''',
        },
        {
            "syntax": "for line in text.splitlines(): json.loads(line)",
            "explain": "JSONL is one JSON value per line. Parse each line on its own. To write it, add a newline after each json.dumps result.",
            "example": r'''
                import json
                text = '{"id": 1}\n{"id": 2}\n'
                for line in text.splitlines():
                    print(json.loads(line)["id"])
                # 1
                # 2
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: JSON

**JSON** is a text format for data. A JSON document is one string. It can describe
objects (written `{...}`, the same shape as a dict), arrays (written `[...]`, the same
shape as a list), strings, numbers, `true`, `false` and `null`. The APIs of language
models send and receive JSON, and files that hold settings often contain JSON.

### The four functions

A **module** is a file of Python code that you can use from your own program. The
`json` module comes with Python. The line `import json` loads it. After that line you
call its functions with the module name and a dot, as in `json.loads(...)`.

The `json` module converts between JSON text and Python values.

- `json.loads(text)` reads JSON text from a string and returns a Python value. This is called **parsing**.
- `json.dumps(value)` takes a Python value and returns JSON text as a string. This is called **serializing**.
- `json.load(fh)` parses JSON text read from an open file `fh`. `fh` is a file object.
  The next chapter covers files and file objects. Until then, use only `loads` and `dumps`.
- `json.dump(value, fh)` serializes `value` and writes the text to an open file `fh`.
  This is a preview. The next chapter shows `fh` in action.

The `s` at the end of `loads` and `dumps` stands for "string". The next chapter covers
files. This chapter uses `loads` and `dumps`.

```python
import json

message = {"role": "user", "content": "Hi"}
text = json.dumps(message)
print(text)
# {"role": "user", "content": "Hi"}
back = json.loads(text)
print(back)
# {'role': 'user', 'content': 'Hi'}
print(back == message)
# True
```

Step through the stages to see the value and its type at each one.

```diagram
{"type":"flow","title":"Round trip of message","steps":[
{"label":"Python dict","detail":"message is a dict in memory. You can read message[\"role\"].","code":"message = {'role': 'user', 'content': 'Hi'}\ntype: dict"},
{"label":"json.dumps","detail":"json.dumps(message) builds a new string. It writes each key and each string value in double quotes.","code":"text = json.dumps(message)"},
{"label":"JSON text","detail":"text is a str. You can send it or save it. You cannot read text[\"role\"], because a string has no keys.","code":"text = '{\"role\": \"user\", \"content\": \"Hi\"}'\ntype: str"},
{"label":"json.loads","detail":"json.loads(text) reads the string from left to right and builds new Python values from it.","code":"back = json.loads(text)"},
{"label":"Python dict","detail":"back is a new dict. It is equal to message, so back == message is True.","code":"back = {'role': 'user', 'content': 'Hi'}\ntype: dict"}
]}
```

### JSON values and Python values

`json.loads` and `json.dumps` convert these spellings in both directions.

| JSON | Python |
| --- | --- |
| object `{...}` | dict |
| array `[...]` | list |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

JSON strings always use double quotes.

```python
import json

print(json.dumps({"ok": True, "stop": None, "ids": [1, 2]}))
# {"ok": true, "stop": null, "ids": [1, 2]}
```

### json.dumps options

`indent=2` puts each item on its own line, indented 2 spaces per level.
`sort_keys=True` writes the keys in alphabetical order at every level.

```python
import json

cfg = {"zeta": 1, "alpha": {"y": 2, "b": 3}}
print(json.dumps(cfg, indent=2, sort_keys=True))
# {
#   "alpha": {
#     "b": 3,
#     "y": 2
#   },
#   "zeta": 1
# }
```

**ASCII** is a set of 128 characters: the plain English letters, the digits and common
punctuation. An accented letter such as the last letter of the word in the next example
is a **non-ASCII** character. By default `json.dumps` writes every non-ASCII character
as a `\uXXXX` code. `ensure_ascii=False` writes the character itself.

```python
import json

print(json.dumps({"reply": "café"}))
# {"reply": "caf\u00e9"}
print(json.dumps({"reply": "café"}, ensure_ascii=False))
# {"reply": "café"}
```

`default=fn` gives `json.dumps` a function to call for a value that JSON cannot
store, such as a set. The function returns a value that JSON can store. Here the
function is `sorted`, which returns the items of the set as a sorted list.

```python
import json

print(json.dumps({"ids": {3, 1, 2}}, default=sorted))
# {"ids": [1, 2, 3]}
```

### Nested data

Read nested data one level at a time, from left to right. Use a key for a dict and
an index for a list. Use `.get(key, default)` for a key that may be missing.

```python
import json

data = json.loads('{"choices": [{"message": {"content": "Hello!"}}]}')
print(data["choices"][0]["message"]["content"])
# Hello!
print(data.get("usage", {}).get("total_tokens", 0))
# 0
```

The key `"usage"` is missing, so the first `.get` returns its default, the empty dict
`{}`. The second `.get` runs on that empty dict and returns its own default, `0`.

### Invalid JSON

`json.loads` raises `json.JSONDecodeError` when the text is not valid JSON.
`JSONDecodeError` is a sub-type of `ValueError`, so `except ValueError` also catches it.
`except ... as exc` assigns the exception to the name `exc`. An **attribute** is a named
value that belongs to an object. You read it with a dot and no parentheses. The
attribute `exc.pos` is the index of the character where parsing failed.

```python
import json

try:
    json.loads('{"city": Paris}')
except json.JSONDecodeError as exc:
    print("broken at", exc.pos)
# broken at 9
```

### JSONL

**JSONL** (JSON Lines) is a text format with one JSON value per line. Files of saved records and
datasets often use it. You parse each line separately.

```python
import json

lines = '{"id": 1, "ok": true}\n{"id": 2, "ok": false}\n'
for line in lines.splitlines():
    print(json.loads(line))
# {'id': 1, 'ok': True}
# {'id': 2, 'ok': False}
```

### Common mistakes

- `json.dumps(text)` does not parse `text`. It returns a new string with `text` inside double quotes.
- `'{"ok": True}'` is not valid JSON. JSON spells it `true`.
- `"{'a': 1}"` is not valid JSON. JSON strings need double quotes.
- After parsing, index the result (`data["x"]`), not the original text.
- A model often puts sentences or a line of three backticks around its JSON. Find the JSON part before you parse.
'''

EXERCISES = [
    {
        "id": "json-s1",
        "lesson": r'''
            ## Parsing JSON with json.loads

            **JSON** is a text format for data. A JSON document is a string. You cannot read a
            key from it until you convert it to Python values. That conversion is called
            **parsing** (also *deserializing*).

            A **module** is a file of Python code that you can use from your own program.
            The `json` module comes with Python. The line `import json` loads it. After that
            line you call its functions with the module name and a dot.

            `json.loads(text)` parses a string and returns the Python value it describes. The
            `s` in `loads` stands for "string".

            ```python
            import json

            text = '{"name": "Ada", "active": true, "boss": null}'
            data = json.loads(text)
            print(type(text).__name__)
            # str
            print(type(data).__name__)
            # dict
            print(data["name"])
            # Ada
            ```

            JSON spells three values differently from Python. `json.loads` converts `true` to
            `True`, `false` to `False` and `null` to `None`. A JSON object `{...}` becomes a
            dict and a JSON array `[...]` becomes a list.

            ```python
            import json

            data = json.loads('{"name": "Ada", "active": true, "boss": null}')
            print(data["active"])
            # True
            print(data["boss"])
            # None
            ```

            Click a key to read its value from the parsed dict.

            ```diagram
            {"type":"dict","title":"Keys of the parsed dict data","name":"data","entries":[["name","Ada"],["active",true],["boss",null]]}
            ```

            The APIs of language models send their replies as JSON text, so parsing is the
            first step when you handle a reply.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            import json

            text = '{"model": "gpt-4o", "stream": false, "stop": null}'
            data = json.loads(text)
            print(data["model"])
            print(data["stream"])
            print(data["stop"])
            print(type(data).__name__)
        ''',
        "solution": r'''
            gpt-4o
            False
            None
            dict
        ''',
        "explanation": r'''
            `json.loads` parses the JSON text and returns a Python dict. It converts JSON
            `false` to Python `False` and `null` to `None`. `print` shows a string without
            its quotes, and the type of the result is `dict`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`json.loads` turns JSON text into Python values. Think about what each JSON value becomes.",
            "JSON `false` and `null` are not Python words: they get translated to Python's own spellings.",
            "Line 1 is the model string, line 2 is what `false` becomes (`False`), line 3 is what `null` becomes (`None`), line 4 is the type name of a parsed JSON object.",
        ],
    },
    {
        "id": "json-s2",
        "lesson": r'''
            ## Writing JSON with json.dumps

            `json.dumps(value)` takes a Python dict or list and returns JSON text as a string.
            The `s` in `dumps` stands for "string". Converting data to text is called
            **serializing**.

            ```python
            import json

            settings = {"lang": "fr", "beta": True, "limit": None}
            text = json.dumps(settings)
            print(text)
            # {"lang": "fr", "beta": true, "limit": null}
            print(type(text).__name__)
            # str
            ```

            `json.dumps` converts the Python spellings to the JSON ones: `True` becomes `true`
            and `None` becomes `null`. By default it writes the whole value on one line.

            ### The indent argument

            `json.dumps` accepts keyword arguments that change the layout of the text.
            `indent=4` puts each item on its own line and indents each level by 4 spaces.

            ```python
            import json

            settings = {"lang": "fr", "beta": True, "limit": None}
            print(json.dumps(settings, indent=4))
            # {
            #     "lang": "fr",
            #     "beta": true,
            #     "limit": null
            # }
            ```

            Indented JSON is easier to read when you print an API request to debug it. The
            data is the same in both layouts. Only the whitespace differs.
        ''',
        "title": "Pretty print",
        "difficulty": 0,
        "prompt": r'''
            Pretty JSON is easier to read when you debug an API request.

            **Write:** fill in the blank (`___`) in `pretty(data)`

            - `data`: a dict, e.g. `{"model": "gpt-4o", "n": 1}`
            - **Returns:** a string: the dict as JSON text

            **Rules**
            - Indent each level with **2 spaces**.
            - Keep the keys in their original order (don't sort them).

            **Examples**
            ```python
            print(pretty({"model": "gpt-4o", "n": 1}))
            ```
            prints exactly:
            ```
            {
              "model": "gpt-4o",
              "n": 1
            }
            ```
        ''',
        "starter": r'''
            import json


            def pretty(data):
                return json.dumps(data, ___)
        ''',
        "tests": r'''
            from solution import pretty

            def test_output_is_indented_with_2_spaces():
                got = pretty({"model": "gpt-4o", "n": 1})
                expected = '{\n  "model": "gpt-4o",\n  "n": 1\n}'
                assert got == expected, f"got {got!r}"

            def test_returns_a_string():
                got = pretty({"a": [1]})
                assert isinstance(got, str), f"got {type(got).__name__}"
        ''',
        "solution": r'''
            import json


            def pretty(data):
                return json.dumps(data, indent=2)
        ''',
        "hints": [
            "`json.dumps` accepts extra keyword arguments that change how the text is laid out.",
            "There is a keyword argument that says how many spaces to indent each level.",
            "Replace `___` with the keyword `indent` set to the number 2.",
        ],
    },
    {
        "id": "json-s3",
        "lesson": r'''
            ## loads or dumps

            The two function names differ by a few letters, so a common bug is calling the
            wrong one. Each function works in one direction only.

            - `json.loads` takes JSON text and returns a Python value.
            - `json.dumps` takes a Python value and returns JSON text.

            ```python
            import json

            text = '{"n": 1}'
            right = json.loads(text)
            print(type(right).__name__, right)
            # dict {'n': 1}
            ```

            A Python string is also a value that JSON can store. So `json.dumps(text)` does
            not raise an error. It returns a new string: the old text inside double quotes,
            with a backslash before each inner quote.

            ```python
            import json

            text = '{"n": 1}'
            wrong = json.dumps(text)
            print(type(wrong).__name__, wrong)
            # str "{\"n\": 1}"
            ```

            The result has the wrong type: `str` instead of `dict`. The error appears later,
            when `wrong["n"]` raises `TypeError`. When `data["key"]` fails on a value that
            prints as JSON text, check `type(data)` first.
        ''',
        "title": "Fix the parser",
        "difficulty": 0,
        "prompt": r'''
            A config arrives as JSON text and must become a Python dict. The function
            below returns the wrong thing: find the one bug and fix it.

            **Write:** fix `parse_config(text)`

            - `text`: a JSON string, e.g. `'{"temperature": 0.2}'`
            - **Returns:** a `dict` (not a string)

            **Rules**
            - JSON `true` becomes Python `True` (and `false` -> `False`, `null` -> `None`).

            **Examples**
            ```python
            parse_config('{"temperature": 0.2}')                  # returns {"temperature": 0.2}
            parse_config('{"model": "gpt-4o", "stream": true}')   # returns {"model": "gpt-4o", "stream": True}
            ```
        ''',
        "starter": r'''
            import json


            def parse_config(text):
                return json.dumps(text)
        ''',
        "tests": r'''
            from solution import parse_config

            def test_returns_a_dict_not_a_string():
                got = parse_config('{"temperature": 0.2}')
                assert isinstance(got, dict), f"got a {type(got).__name__}: {got!r}"

            def test_values_are_converted_to_python():
                got = parse_config('{"model": "gpt-4o", "stream": true}')
                assert got == {"model": "gpt-4o", "stream": True}, f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def parse_config(text):
                return json.loads(text)
        ''',
        "hints": [
            "There are two similar-looking functions in `json`. Which direction does each one go?",
            "`dumps` turns Python into text. Here you already have text and want Python.",
            "Change `json.dumps` to the function that loads from a string: `json.loads`.",
        ],
    },
    {
        "id": "json-s4",
        "lesson": r'''
            ## Nested data

            API replies are **nested**: a dict can hold another dict or a list as a value.
            After parsing, each pair of square brackets reads one level deeper.

            ```python
            import json

            raw = '{"user": {"profile": {"city": "Lyon"}}, "tags": ["a", "b"]}'
            data = json.loads(raw)
            print(data["user"])
            # {'profile': {'city': 'Lyon'}}
            print(data["user"]["profile"])
            # {'city': 'Lyon'}
            print(data["user"]["profile"]["city"])
            # Lyon
            ```

            Python evaluates `data["user"]["profile"]["city"]` from left to right.
            `data["user"]` returns a dict. `["profile"]` reads a key of that dict and returns
            another dict. `["city"]` reads a key of that one and returns the string `"Lyon"`.

            Use a key (a string) to read from a dict. Use an index (an int) to read from a list.

            ```python
            import json

            raw = '{"user": {"profile": {"city": "Lyon"}}, "tags": ["a", "b"]}'
            data = json.loads(raw)
            print(data["tags"][1])
            # b
            ```

            You can only read keys after parsing. `raw` is still a string, so `raw["user"]`
            raises `TypeError: string indices must be integers, not 'str'`.
        ''',
        "title": "Dig out the content",
        "difficulty": 0,
        "prompt": r'''
            A chat API answers with JSON text. The reply you want is nested inside it.

            **Write:** `get_content(raw)`

            - `raw`: a JSON **string** (not a dict yet) shaped like this:
              ```json
              {"message": {"role": "assistant", "content": "Hi there"}}
              ```
            - **Returns:** the string stored under `"content"` inside `"message"`

            **Rules**
            - The keys inside `"message"` may come in any order.

            **Examples**
            ```python
            get_content('{"message": {"role": "assistant", "content": "Hi there"}}')  # returns "Hi there"
            get_content('{"message": {"content": "42", "role": "assistant"}}')        # returns "42"
            ```
        ''',
        "starter": r'''
            import json


            def get_content(raw):
                ...
        ''',
        "tests": r'''
            from solution import get_content

            def test_returns_the_nested_content():
                got = get_content('{"message": {"role": "assistant", "content": "Hi there"}}')
                assert got == "Hi there", f"got {got!r}"

            def test_works_with_keys_in_another_order():
                got = get_content('{"message": {"content": "42", "role": "assistant"}}')
                assert got == "42", f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def get_content(raw):
                data = json.loads(raw)
                return data["message"]["content"]
        ''',
        "hints": [
            "`raw` is a string, so you cannot index it by key yet. Parse it first.",
            "Parse the text into a dict, then go one level down into `message`, then one more into `content`.",
            "Store `json.loads(raw)` in a variable, then return that variable indexed with `[\"message\"]` and then `[\"content\"]`.",
        ],
    },
    {
        "id": "json-s5",
        "lesson": r'''
            ## Invalid JSON

            A model sometimes sends text that is not valid JSON: a quote is missing, or the
            reply stops halfway. `json.loads` does not guess what the text meant. It raises
            an exception named `json.JSONDecodeError`.

            You catch it with `try` / `except`, the same way you caught `ValueError` and
            `KeyError` in the errors topic.

            ```python
            import json

            for text in ['{"ok": true}', "{'ok': true}", '{"ok": tru']:
                try:
                    print("parsed:", json.loads(text))
                except json.JSONDecodeError as exc:
                    print("rejected at position", exc.pos)
            # parsed: {'ok': True}
            # rejected at position 1
            # rejected at position 7
            ```

            `except ... as exc` assigns the exception to the name `exc`. An **attribute** is
            a named value that belongs to an object. You read it with a dot and no
            parentheses. The attribute `exc.pos` is the index of the character where parsing
            failed. You can put it in an error message.

            The second text fails at index 1 because of the single quote. JSON strings must
            use double quotes. The third text fails at index 7 because `tru` is not a JSON value.

            Catch `json.JSONDecodeError` and not every exception. A broad `except` also
            catches unrelated bugs, such as a misspelled variable name, and hides them.
        ''',
        "title": "Is it valid JSON?",
        "difficulty": 0,
        "prompt": r'''
            Before you trust a model's output, check that it is JSON at all.

            **Write:** `is_valid_json(text)`

            - `text`: a string that may or may not be JSON, e.g. `'{"a": 1}'`
            - **Returns:** the boolean `True` if `json.loads` can parse `text`, otherwise
              the boolean `False` (real `True`/`False`, not strings or `1`/`0`)

            **Rules**
            - Any valid JSON counts, not only objects: a list like `'[1, 2, 3]'` is valid too.
            - Single quotes are not valid JSON: `"{'a': 1}"` is invalid.
            - The empty string `""` is invalid.
            - Catch the specific error `json.JSONDecodeError` (a check looks for that name
              in your code).

            **Examples**
            ```python
            is_valid_json('{"a": 1}')    # returns True
            is_valid_json('[1, 2, 3]')   # returns True
            is_valid_json('{"a": }')     # returns False
            is_valid_json("")            # returns False
            ```

            Reminder:
            ```python
            try:
                ...                  # something that may fail
            except SomeError:
                ...                  # what to do if it fails
            ```
        ''',
        "starter": r'''
            import json


            def is_valid_json(text):
                ...
        ''',
        "tests": r'''
            from solution import is_valid_json

            def test_valid_object_returns_true():
                assert is_valid_json('{"a": 1}') is True

            def test_valid_list_returns_true():
                assert is_valid_json('[1, 2, 3]') is True

            def test_broken_or_single_quoted_json_returns_false():
                assert is_valid_json('{"a": }') is False
                assert is_valid_json("{'a': 1}") is False

            def test_empty_string_returns_false():
                assert is_valid_json("") is False

            def test_code_catches_json_decode_error():
                assert "JSONDecodeError" in source(), "catch json.JSONDecodeError"
        ''',
        "solution": r'''
            import json


            def is_valid_json(text):
                try:
                    json.loads(text)
                except json.JSONDecodeError:
                    return False
                return True
        ''',
        "hints": [
            "Use `try` / `except` around the parsing step.",
            "Try to parse the text. If parsing raises the JSON error, the answer is False; if it gets through, the answer is True.",
            "Inside `try`, call `json.loads(text)`. Add `except json.JSONDecodeError:` that returns `False`. After the try block, return `True`.",
        ],
    },
    {
        "id": "json-s6",
        "lesson": r'''
            ## Building a request body

            When you call the API of a language model, you send a **request body**: JSON
            text that holds, for example, the model name and a list of messages. Build the body
            as a Python dict first. Then convert it to text with `json.dumps`.

            ```python
            import json

            body = {"name": "search", "args": {"query": 'the "best" pizza', "limit": 3}}
            print(json.dumps(body))
            # {"name": "search", "args": {"query": "the \"best\" pizza", "limit": 3}}
            ```

            `json.dumps` writes every key and string in double quotes. It writes `, ` between
            items and `: ` after each key. Keys appear in the order you wrote them in the dict.

            The query contains double quotes. `json.dumps` writes each one as `\"`. This is
            called **escaping**: the backslash marks the quote as part of the string, not
            the end of it.

            ### Do not build JSON by joining strings

            Joining strings with `+` or an f-string copies the text in without escaping it.
            A quote inside the text then ends the JSON string too early.

            ```python
            import json

            query = 'the "best" pizza'
            glued = '{"query": "' + query + '"}'
            print(glued)
            # {"query": "the "best" pizza"}
            try:
                json.loads(glued)
            except json.JSONDecodeError as exc:
                print("invalid JSON at position", exc.pos)
            # invalid JSON at position 16
            ```

            A dict can hold a list of dicts. A chat request has that shape:
            `{"messages": [{"role": ..., "content": ...}]}`.
        ''',
        "title": "Build a request body",
        "difficulty": 0,
        "prompt": r'''
            Before calling a chat API you build its request body as JSON text.

            **Write:** `make_body(model, prompt)`

            - `model`: the model name, a string like `"gpt-4o"`
            - `prompt`: the user's message, a string like `"Hi"`
            - **Returns:** a string: the JSON text of this object (keys in this order):
              `{"model": <model>, "messages": [{"role": "user", "content": <prompt>}]}`

            **Rules**
            - Use the normal `json.dumps` spacing (one line, `", "` between items, `": "` after keys).
            - Quotes inside `prompt` must still give valid JSON (build a dict and let `json.dumps`
              write the text; don't glue strings together).

            **Examples**
            ```python
            make_body("gpt-4o", "Hi")
            # returns '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}'
            make_body("m", 'Say "yes"')
            # returns '{"model": "m", "messages": [{"role": "user", "content": "Say \\"yes\\""}]}'
            ```
        ''',
        "starter": r'''
            import json


            def make_body(model, prompt):
                ...
        ''',
        "tests": r'''
            import json
            from solution import make_body

            def test_returns_exact_json_text():
                got = make_body("gpt-4o", "Hi")
                expected = '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}'
                assert got == expected, f"got {got!r}"

            def test_returns_a_string():
                got = make_body("m", "x")
                assert isinstance(got, str), f"got a {type(got).__name__}"

            def test_quotes_in_prompt_still_give_valid_json():
                got = make_body("m", 'Say "yes"')
                data = json.loads(got)
                assert data["messages"][0]["content"] == 'Say "yes"', f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def make_body(model, prompt):
                body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
                return json.dumps(body)
        ''',
        "hints": [
            "Build the whole structure as a normal Python dict first, then turn it into text.",
            "The dict has two keys: the model, and a list holding one message dict with a role and a content.",
            "Create `body = {\"model\": ..., \"messages\": [ {...} ]}` with `\"role\": \"user\"` and `\"content\": prompt` inside the message, then return `json.dumps(body)`.",
        ],
    },
    {
        "id": "json-1",
        "lesson": r'''
            ## sort_keys and the round trip

            Two `json.dumps` arguments make a saved config file easier to read and compare.

            - `indent=2` puts each item on its own line, indented 2 spaces per level.
            - `sort_keys=True` writes the keys in alphabetical order, in nested dicts too.

            ```python
            import json

            cfg = {"zeta": 1, "alpha": {"y": 2, "b": 3}}
            print(json.dumps(cfg))
            # {"zeta": 1, "alpha": {"y": 2, "b": 3}}
            print(json.dumps(cfg, sort_keys=True))
            # {"alpha": {"b": 3, "y": 2}, "zeta": 1}
            ```

            With sorted keys, two dicts with the same keys and values always produce the same
            text. When you compare two saved versions of a file line by line, only the lines
            with changed values differ.

            ### Round trip

            A **round trip** converts a value to JSON text with `dumps` and back with `loads`.
            The result is a new dict that is equal to the original.

            ```python
            import json

            cfg = {"zeta": 1, "alpha": {"y": 2, "b": 3}}
            text = json.dumps(cfg, indent=2, sort_keys=True)
            back = json.loads(text)
            print(back == cfg)
            # True
            ```

            `indent` and `sort_keys` change the layout of the text. They do not change the
            data. Two dicts are equal when they have the same keys and values, in any order.
        ''',
        "hints": [
            "Both functions are one-liners with the `json` module: one goes dict -> text, the other text -> dict.",
            "`json.dumps` takes keyword arguments for indentation and for sorting keys; `json.loads` parses text.",
            "Import `json` at the top. In `to_pretty_json`, return the result of `json.dumps` on the config, passing an indent of 2 and asking it to sort the keys. In `from_json`, return the result of parsing the text with `json.loads`.",
        ],
        "title": "Pretty config",
        "difficulty": 1,
        "prompt": r'''
            Model configs are saved as readable JSON files and loaded back later. Write
            both directions.

            **Write:** `to_pretty_json(config)` and `from_json(text)`

            - `config`: a dict, e.g. `{"temperature": 0.2, "model": "gpt-4o"}` (values may
              be nested dicts and lists)
            - `text`: a JSON string, e.g. `'{"stream": false, "n": null}'`
            - **`to_pretty_json` returns:** a string of JSON text
            - **`from_json` returns:** the Python value the text describes (usually a dict)

            **Rules**
            - `to_pretty_json` indents with **2 spaces** per level.
            - Keys are **sorted alphabetically**, at every level (nested dicts too).
            - Use normal `json` spacing: `"key": value` with one space after the colon.
            - `from_json` turns JSON `true`/`false`/`null` into `True`/`False`/`None`.
            - Going there and back gives the original dict:
              `from_json(to_pretty_json(d)) == d`.

            **Examples**
            ```python
            print(to_pretty_json({"temperature": 0.2, "model": "gpt-4o"}))
            ```
            prints exactly:
            ```
            {
              "model": "gpt-4o",
              "temperature": 0.2
            }
            ```
            ```python
            from_json('{"stream": false, "n": null}')   # returns {"stream": False, "n": None}
            ```
        ''',
        "starter": r'''
            def to_pretty_json(config):
                ...


            def from_json(text):
                ...
        ''',
        "tests": r'''
            from solution import to_pretty_json, from_json

            def test_pretty_output_has_2_space_indent_and_sorted_keys():
                got = to_pretty_json({"temperature": 0.2, "model": "gpt-4o"})
                expected = '{\n  "model": "gpt-4o",\n  "temperature": 0.2\n}'
                assert got == expected, f"got {got!r}"

            def test_nested_keys_are_sorted_too():
                got = to_pretty_json({"b": {"z": 1, "a": None}, "a": [True]})
                assert got.index('"a": [') < got.index('"b"'), "top-level keys not sorted"
                assert got.index('"a": null') < got.index('"z"'), "nested keys not sorted"

            def test_from_json_parses_true_false_null():
                got = from_json('{"stop": ["\\n"], "stream": false, "n": null}')
                assert got == {"stop": ["\n"], "stream": False, "n": None}, f"got {got!r}"

            def test_round_trip_gives_back_the_same_dict():
                data = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}
                assert from_json(to_pretty_json(data)) == data
        ''',
        "solution": r'''
            import json


            def to_pretty_json(config):
                return json.dumps(config, indent=2, sort_keys=True)


            def from_json(text):
                return json.loads(text)
        ''',
    },
    {
        "id": "json-2",
        "lesson": r'''
            ## Lists and optional keys in a reply

            The reply of a chat API, once parsed, is a dict that holds a list of dicts:

            ```json
            {"choices": [{"message": {"role": "assistant", "content": "..."}}],
             "usage": {"total_tokens": 12}}
            ```

            `choices` is a list because you can ask the API for several answers. You usually
            read the item at index `0`. The next example has the same shape with other names.

            ```python
            import json

            data = json.loads('{"results": [{"title": "RAG"}, {"title": "Agents"}]}')
            print(data["results"][0]["title"])
            # RAG
            ```

            ### Optional keys

            Some keys are optional. `data["meta"]` raises `KeyError` when the key is missing.
            `data.get("meta", {})` returns the default, an empty dict, and raises nothing.

            Try `data["meta"]` and `data.get("meta")` on the parsed dict.

            ```diagram
            {"type":"dict","title":"Keys of the parsed dict data","name":"data","entries":[["results",[{"title":"RAG"},{"title":"Agents"}]]]}
            ```

            Because the first `.get` always returns a dict, you can call `.get` on its result.

            ```python
            import json

            data = json.loads('{"results": [{"title": "RAG"}, {"title": "Agents"}]}')
            meta = data.get("meta", {})
            print(meta)
            # {}
            print(meta.get("page", 1))
            # 1
            print(data.get("meta", {}).get("page", 1))
            # 1
            ```

            The key `"page"` is not in the empty dict, so the second `.get` returns its own
            default, `1`. This exercise returns two values from one function. Write
            `return a, b`. Python returns them as one tuple, a fixed group of values.
        ''',
        "hints": [
            "`raw` is text: parse it first, then walk down the nested dicts and lists one step at a time.",
            "The content lives at choices -> first item -> message -> content. The token count lives at usage -> total_tokens, but `usage` may be missing.",
            "Parse with `json.loads`. Index `[\"choices\"][0][\"message\"][\"content\"]`. For the tokens, use `.get(\"usage\", {})` and then `.get(\"total_tokens\", 0)` on that. Return both as a tuple.",
        ],
        "title": "Read a chat completion",
        "difficulty": 1,
        "prompt": r'''
            Every chat API call returns a JSON response. Your app needs two things from it:
            the reply text and how many tokens it cost.

            **Write:** `extract_reply(raw)`

            - `raw`: the **JSON text** (a string, not a dict) of an OpenAI-style chat
              completion, like this:

            ```json
            {
              "id": "chatcmpl-1",
              "choices": [
                {"index": 0,
                 "message": {"role": "assistant", "content": "Hello!"},
                 "finish_reason": "stop"}
              ],
              "usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12}
            }
            ```

            - **Returns:** a tuple `(content, total_tokens)`: the reply string and an int

            **Rules**
            - `content` is `message["content"]` of the **first** item in `"choices"`
              (there may be several choices).
            - `total_tokens` is `usage["total_tokens"]`.
            - If the `"usage"` key is missing, `total_tokens` is `0`.
            - Non-ASCII text (like `"café"`) must come back unchanged.

            **Examples**
            ```python
            extract_reply(raw)            # returns ("Hello!", 12)   (raw = the JSON above)
            extract_reply(raw_no_usage)   # returns ("Hello!", 0)    (same JSON without "usage")
            ```
        ''',
        "starter": r'''
            def extract_reply(raw):
                ...
        ''',
        "tests": r'''
            import json
            from solution import extract_reply

            def make(content, usage=True, extra_choice=False):
                choices = [{"index": 0, "message": {"role": "assistant", "content": content},
                            "finish_reason": "stop"}]
                if extra_choice:
                    choices.append({"index": 1, "message": {"role": "assistant",
                                    "content": "second"}, "finish_reason": "stop"})
                data = {"id": "chatcmpl-1", "choices": choices}
                if usage:
                    data["usage"] = {"prompt_tokens": 9, "completion_tokens": 3,
                                     "total_tokens": 12}
                return json.dumps(data)

            def test_returns_content_and_total_tokens():
                got = extract_reply(make("Hello!"))
                assert got == ("Hello!", 12), f"got {got!r}"

            def test_uses_the_first_choice():
                got = extract_reply(make("first", extra_choice=True))
                assert got[0] == "first", f"got {got!r}"

            def test_missing_usage_gives_0_tokens():
                got = extract_reply(make("x", usage=False))
                assert got == ("x", 0), f"got {got!r}"

            def test_parses_text_with_non_ascii_content():
                got = extract_reply(make("unicode café"))
                assert got[0] == "unicode café", f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def extract_reply(raw):
                data = json.loads(raw)
                content = data["choices"][0]["message"]["content"]
                total = data.get("usage", {}).get("total_tokens", 0)
                return content, total
        ''',
    },
    {
        "id": "json-7",
        "lesson": r'''
            ## Changing JSON text

            A string cannot be changed in place, and it has no keys or `append` method. To
            change JSON text, you parse it, change the Python value, and serialize it again.

            ```python
            import json

            raw = '{"tags": ["rag"]}'
            data = json.loads(raw)
            data["tags"].append("json")
            print(json.dumps(data))
            # {"tags": ["rag", "json"]}
            print(raw)
            # {"tags": ["rag"]}
            ```

            `json.dumps` returns a new string. The original `raw` string is unchanged.

            Step through the three stages to see the data at each one.

            ```diagram
            {"type":"flow","title":"Parse, change, serialize","steps":[
            {"label":"JSON text","detail":"raw is a str. It has no keys and no append method.","code":"raw = '{\"tags\": [\"rag\"]}'"},
            {"label":"json.loads","detail":"json.loads(raw) returns a dict. Its value for \"tags\" is a list.","code":"data = json.loads(raw)\ndata is {'tags': ['rag']}"},
            {"label":"Change the value","detail":"append adds one item to the list inside the dict. raw is not affected.","code":"data[\"tags\"].append(\"json\")\ndata is {'tags': ['rag', 'json']}"},
            {"label":"json.dumps","detail":"json.dumps(data) builds a new string from the changed dict.","code":"json.dumps(data)\nreturns '{\"tags\": [\"rag\", \"json\"]}'"}
            ]}
            ```

            AI apps use this pattern often. A chat history stored as JSON text is parsed, the
            new message is appended, and the whole list is serialized again. `json.dumps`
            writes the new text with its normal spacing: `, ` between items and `: ` after keys.

            `list.append` changes the list and returns `None`. If you write
            `data = data.append(...)`, the name `data` refers to `None` afterwards.
        ''',
        "title": "Append to a chat history",
        "difficulty": 1,
        "prompt": r'''
            A chat app stores the conversation as JSON text. Add a new message to it.

            **Write:** `add_message(history, role, content)`

            - `history`: JSON **text** of a list of message dicts, e.g.
              `'[{"role": "user", "content": "hi"}]'` (may be the empty list `'[]'`)
            - `role`: a string like `"assistant"`
            - `content`: a string like `"hello"`
            - **Returns:** a string: the JSON text of the list with
              `{"role": <role>, "content": <content>}` added at the **end**

            **Rules**
            - Keep all existing messages, in order.
            - The new message has exactly the keys `"role"` then `"content"`.
            - Use the normal `json.dumps` spacing (one line, no indent).

            **Examples**
            ```python
            add_message('[{"role": "user", "content": "hi"}]', "assistant", "hello")
            # returns '[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]'
            add_message("[]", "user", "first")
            # returns '[{"role": "user", "content": "first"}]'
            ```
        ''',
        "starter": r'''
            import json


            def add_message(history, role, content):
                ...
        ''',
        "tests": r'''
            import json
            from solution import add_message

            def test_appends_message_at_the_end():
                got = add_message('[{"role": "user", "content": "hi"}]', "assistant", "hello")
                expected = '[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]'
                assert got == expected, f"got {got!r}"

            def test_empty_history_gets_one_message():
                got = add_message("[]", "user", "first")
                assert got == '[{"role": "user", "content": "first"}]', f"got {got!r}"

            def test_returns_json_text_not_a_list():
                got = add_message("[]", "user", "x")
                assert isinstance(got, str), f"got a {type(got).__name__}"

            def test_keeps_order_of_existing_messages():
                hist = json.dumps([{"role": "system", "content": "s"}, {"role": "user", "content": "u"}])
                got = json.loads(add_message(hist, "assistant", "a"))
                assert [m["content"] for m in got] == ["s", "u", "a"], f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def add_message(history, role, content):
                messages = json.loads(history)
                messages.append({"role": role, "content": content})
                return json.dumps(messages)
        ''',
        "hints": [
            "You cannot append to text. Turn it into a Python list first, then back into text.",
            "Parse the history, add one new message dict to the end of the list, then serialise the whole list again.",
            "`messages = json.loads(history)`, then `messages.append({\"role\": role, \"content\": content})`, then return `json.dumps(messages)`.",
        ],
    },
    {
        "id": "json-8",
        "lesson": r'''
            ## Non-ASCII characters in JSON

            **ASCII** is a set of 128 characters: the plain English letters, the digits and
            common punctuation. Accented letters, emoji, Chinese and Arabic characters are
            outside it. They are called **non-ASCII** characters.

            By default `json.dumps` writes every non-ASCII character as an **escape code**:
            a backslash, the letter `u` and a four-character code.

            ```python
            import json

            text = json.dumps({"city": "Zürich"})
            print(text)
            # {"city": "Z\u00fcrich"}
            ```

            The u with two dots in the city name is written as `\u00fc`. The data is the
            same. `json.loads` converts the escape code back to the character. Some
            characters, such as most emoji, are written as two of these codes.

            ```python
            import json

            text = json.dumps({"city": "Zürich"})
            print(json.loads(text))
            # {'city': 'Zürich'}
            ```

            Model replies contain many non-ASCII characters. Printed output full of `\u00e9` codes is
            hard to read, and the text is longer: `\u00e9` takes 6 characters instead of 1.

            `json.dumps` has a keyword argument that turns this escaping off. This lesson
            does not name it. Finding it in the documentation is part of the exercise. The
            documentation of a function lists every argument it accepts, including ones you
            have not used yet.
        ''',
        "research": {"note": "Open the `json.dumps` documentation and find the parameter that controls whether non-ASCII characters are escaped. Then come back and use it.",
         "links": [{"title": "json.dumps - Python docs", "url": "https://docs.python.org/3/library/json.html#json.dumps"}]},
        "title": "Readable non-English JSON",
        "difficulty": 1,
        "prompt": r'''
            Your logs show model replies as JSON, but `"café"` appears as `"café"`. Make the
            JSON text keep non-English characters as they are.

            **Write:** `to_readable_json(data)`

            - `data`: a dict, e.g. `{"reply": "café"}`
            - **Returns:** a string: the JSON text of `data`

            **Rules**
            - Non-ASCII characters (accents, emoji, other alphabets) appear as themselves, never
              as `\u....` escape codes.
            - Use the normal `json.dumps` spacing (one line, no indent, keys in original order).
            - Loading the result with `json.loads` gives back `data`.

            **Examples**
            ```python
            to_readable_json({"reply": "café"})           # returns '{"reply": "café"}'
            to_readable_json({"a": "日本", "n": 1})        # returns '{"a": "日本", "n": 1}'
            to_readable_json({})                          # returns '{}'
            ```
        ''',
        "starter": r'''
            import json


            def to_readable_json(data):
                return json.dumps(data)
        ''',
        "tests": r'''
            import json
            from solution import to_readable_json

            def test_accented_text_stays_readable():
                got = to_readable_json({"reply": "café"})
                assert got == '{"reply": "café"}', f"got {got!r}"

            def test_no_unicode_escape_codes_for_other_alphabets_and_emoji():
                got = to_readable_json({"a": "日本", "e": "☕"})
                assert "\\u" not in got, f"got {got!r}"
                assert got == '{"a": "日本", "e": "☕"}', f"got {got!r}"

            def test_round_trip_gives_back_the_dict():
                data = {"q": "¿Qué?", "n": 1, "ok": True}
                assert json.loads(to_readable_json(data)) == data

            def test_empty_dict_gives_empty_object():
                assert to_readable_json({}) == "{}"
        ''',
        "solution": r'''
            import json


            def to_readable_json(data):
                return json.dumps(data, ensure_ascii=False)
        ''',
        "hints": [
            "The starter already produces valid JSON. The fix is one extra keyword argument to `json.dumps`.",
            "Look in the `json.dumps` docs for the parameter about ASCII: by default it is True, which escapes non-ASCII characters.",
            "Pass the ASCII-related keyword argument set to `False` in the `json.dumps` call.",
        ],
    },
    {
        "id": "json-3",
        "hints": [
            "Wrap the parse in `try` / `except json.JSONDecodeError`. The exception object knows where parsing failed.",
            "If parsing fails, build the error dict using the exception's position. If it succeeds, check the parsed value is a dict before returning it.",
            "`except json.JSONDecodeError as exc:` then return the dict with `exc.pos`. After the try block, use `isinstance(data, dict)`; if it is not a dict, `raise TypeError(...)`; otherwise return `data`.",
        ],
        "title": "Safe parse",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            When a model calls a tool, it sends the tool's arguments as a JSON string, and
            that string is often broken. Parse it safely.

            **Write:** `parse_tool_args(text)`

            - `text`: the tool call's `arguments` string, e.g. `'{"city": "Paris", "days": 3}'`
            - **Returns:** a dict (either the parsed arguments, or an error dict: see Rules)

            **Rules**
            - Valid JSON **object** (`{...}`) -> return the parsed dict.
            - Invalid JSON (including the empty string `""` and text cut off halfway) ->
              return `{"error": "invalid json", "position": <pos>}`, where `<pos>` is an
              `int`: the character index where parsing failed. The caught
              `json.JSONDecodeError` gives you this number as its `.pos` attribute.
            - Valid JSON that is **not** an object (a list like `[1, 2]`, a number like
              `42`, a string like `"hi"`) -> raise `TypeError` (any message).
            - Catch the specific `json.JSONDecodeError`. Your code must not contain
              `except Exception` or a bare `except:`.

            **Examples**
            ```python
            parse_tool_args('{"city": "Paris"}')   # returns {"city": "Paris"}
            parse_tool_args('{"city": Paris}')     # returns {"error": "invalid json", "position": 9}
            parse_tool_args("")                    # returns {"error": "invalid json", "position": 0}
            parse_tool_args('[1, 2]')              # raises TypeError
            ```
        ''',
        "starter": r'''
            def parse_tool_args(text):
                ...
        ''',
        "tests": r'''
            from solution import parse_tool_args

            def test_valid_object_returns_the_dict():
                got = parse_tool_args('{"city": "Paris", "days": 3}')
                assert got == {"city": "Paris", "days": 3}, f"got {got!r}"

            def test_invalid_json_returns_error_dict_with_position():
                got = parse_tool_args('{"city": Paris}')
                assert got == {"error": "invalid json", "position": 9}, f"got {got!r}"

            def test_cut_off_json_returns_error_dict_with_int_position():
                got = parse_tool_args('{"city": "Par')
                assert got.get("error") == "invalid json", f"got {got!r}"
                assert isinstance(got.get("position"), int), f"got {got!r}"

            def test_empty_string_returns_error_at_position_0():
                got = parse_tool_args("")
                assert got == {"error": "invalid json", "position": 0}, f"got {got!r}"

            def test_list_number_or_string_raises_type_error():
                for text in ("[1, 2]", "42", '"just a string"'):
                    try:
                        parse_tool_args(text)
                    except TypeError:
                        continue
                    assert False, f"expected TypeError for {text!r}"

            def test_code_has_no_except_exception_or_bare_except():
                src = source()
                assert "except Exception" not in src and "except:" not in src, \
                    "catch the specific JSON decoding error"
        ''',
        "solution": r'''
            import json


            def parse_tool_args(text):
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as exc:
                    return {"error": "invalid json", "position": exc.pos}
                if not isinstance(data, dict):
                    raise TypeError(f"expected a JSON object, got {type(data).__name__}")
                return data
        ''',
    },
    {
        "id": "json-4",
        "hints": [
            "Both directions work line by line: one `json.dumps` per record going out, one `json.loads` per non-blank line coming in.",
            "To build the text, turn each record into a compact JSON string (keeping non-ASCII characters readable) and add a newline after each. To read it, split the text into lines, skip blank ones, and parse the rest, turning a parse error into a `ValueError` that says which line broke.",
            "to_jsonl: start with an empty string (or list of parts) and, for each record, add `json.dumps(record, ensure_ascii=False)` plus `\"\\n\"`. from_jsonl: loop over `enumerate(text.splitlines(), start=1)`, skip lines whose `.strip()` is empty, `try` to `json.loads` the line and append it, `except json.JSONDecodeError` raise `ValueError` with an f-string containing `line {n}`.",
        ],
        "title": "JSONL eval log",
        "difficulty": 2,
        "prompt": r'''
            Eval runs are logged as **JSONL** (*JSON Lines*): one JSON object per line.
            Write the writer and the reader.

            **Write:** `to_jsonl(records)` and `from_jsonl(text)`

            - `records`: a list of dicts, e.g. `[{"q": "2+2?", "ok": True}]`
            - `text`: a JSONL string, e.g. `'{"a": 1}\n{"a": 2}\n'`
            - **`to_jsonl` returns:** one string holding all the records, one per line
            - **`from_jsonl` returns:** a list of dicts, one per non-blank line

            **Rules**
            - `to_jsonl`: each record is one line of JSON with the normal `json.dumps`
              spacing (`{"q": "2+2?", "ok": true}`), and **every** line ends with `\n`,
              including the last one.
            - `to_jsonl`: non-ASCII text stays as-is (`"café"`, not `"café"`).
            - `to_jsonl([])` returns `""`.
            - `from_jsonl`: skip blank lines, including lines that contain only spaces.
            - `from_jsonl`: if a line is not valid JSON, raise `ValueError` whose message
              contains `line N`, where N is that line's number in `text`, starting at 1 and
              counting blank lines too.
            - `from_jsonl(to_jsonl(records))` gives back `records`.

            **Examples**
            ```python
            to_jsonl([{"q": "2+2?", "ok": True}, {"q": "café?", "ok": False}])
            # returns '{"q": "2+2?", "ok": true}\n{"q": "café?", "ok": false}\n'
            to_jsonl([])                                   # returns ""
            from_jsonl('{"id": 1}\n\n   \n{"id": 2}\n')    # returns [{"id": 1}, {"id": 2}]
            from_jsonl('{"a": 1}\n\n{broken\n')            # raises ValueError, message contains "line 3"
            ```
        ''',
        "starter": r'''
            def to_jsonl(records):
                ...


            def from_jsonl(text):
                ...
        ''',
        "tests": r'''
            from solution import to_jsonl, from_jsonl

            def test_to_jsonl_writes_one_line_per_record_ending_in_newline():
                got = to_jsonl([{"q": "2+2?", "ok": True}, {"q": "x", "ok": False}])
                expected = '{"q": "2+2?", "ok": true}\n{"q": "x", "ok": false}\n'
                assert got == expected, f"got {got!r}"

            def test_to_jsonl_empty_list_gives_empty_string():
                assert to_jsonl([]) == "", f"got {to_jsonl([])!r}"

            def test_to_jsonl_keeps_non_ascii_text_unescaped():
                got = to_jsonl([{"q": "café"}])
                assert "café" in got, f"got {got!r}"

            def test_from_jsonl_skips_blank_lines():
                got = from_jsonl('{"id": 1, "score": 0.5}\n\n   \n{"id": 2, "score": 0.75}\n')
                assert got == [{"id": 1, "score": 0.5}, {"id": 2, "score": 0.75}], f"got {got!r}"

            def test_round_trip_gives_back_the_records():
                recs = [{"a": [1, 2]}, {"b": {"c": None}}, {"d": "café"}]
                assert from_jsonl(to_jsonl(recs)) == recs

            def test_broken_line_raises_value_error_with_line_number():
                try:
                    from_jsonl('{"a": 1}\n\n{broken\n')
                except ValueError as exc:
                    assert "line 3" in str(exc), f"message was {str(exc)!r}"
                else:
                    raise AssertionError("expected ValueError for a broken line")
        ''',
        "solution": r'''
            import json


            def to_jsonl(records):
                lines = []
                for record in records:
                    lines.append(json.dumps(record, ensure_ascii=False) + "\n")
                return "".join(lines)


            def from_jsonl(text):
                records = []
                for n, line in enumerate(text.splitlines(), start=1):
                    if not line.strip():
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        raise ValueError(f"invalid JSON on line {n}") from None
                return records
        ''',
    },
    {
        "id": "json-5",
        "hints": [
            "Split the job in two: first find the candidate text (fence block or braces), then parse and validate it.",
            "Look for three backticks with `.find()`. If there is a fenced block, take the text after the opening line up to the next fence. Otherwise take from the first `{` to the last `}`. Any parse failure or non-dict becomes `ValueError`.",
            "Use `reply.find(fence)` and `reply.find(\"\\n\", start)` to locate the block body, `reply.rfind(\"}\")` for the last brace. Parse with `json.loads` inside `try`, convert `json.JSONDecodeError` into `raise ValueError(...)`, and raise `ValueError` if the result is not a dict.",
        ],
        "title": "JSON from a chatty reply",
        "difficulty": 3,
        "prompt": r'''
            You asked the model for JSON, but it replied with prose around it and/or
            wrapped it in markdown *code fences* (a line of three backticks, optionally
            followed by `json`, then the code, then a closing line of three backticks).

            **Write:** `extract_json(reply)`

            - `reply`: the model's whole reply as a string
            - **Returns:** the parsed JSON **object**, as a dict

            **Rules**
            - If the reply contains a fenced block (opened by ` ```json ` or by a bare
              ` ``` ` line), parse the text between the opening line and the closing
              ` ``` ` of the **first** block. Ignore any later blocks.
            - Otherwise, parse the text from the **first** `{` to the **last** `}` (so a
              nested object like `{"meta": {"tags": ["y"]}}` stays whole).
            - Raise `ValueError` (any message) when: there is no JSON to find, the
              candidate text is not valid JSON, or it parses to something that is not a
              dict (e.g. a list).

            **Examples**
            ```python
            extract_json('Here you go:\n```json\n{"a": 1}\n```\nAnything else?')
            # returns {"a": 1}
            extract_json('```\n{"ok": true}\n```')
            # returns {"ok": True}
            extract_json('Result: {"name": "x", "meta": {"tags": ["y"]}} Hope that helps!')
            # returns {"name": "x", "meta": {"tags": ["y"]}}
            extract_json("I cannot do that.")          # raises ValueError
            extract_json("broken {not json}")          # raises ValueError
            extract_json('```json\n[1, 2]\n```')       # raises ValueError (a list, not a dict)
            ```
        ''',
        "starter": r'''
            def extract_json(reply):
                ...
        ''',
        "tests": r'''
            from solution import extract_json

            FENCE = "`" * 3

            def test_json_fence_surrounded_by_prose():
                reply = f"Here you go:\n{FENCE}json\n{{\"a\": 1}}\n{FENCE}\nAnything else?"
                got = extract_json(reply)
                assert got == {"a": 1}, f"got {got!r}"

            def test_bare_fence_without_json_label():
                reply = f"{FENCE}\n{{\"ok\": true}}\n{FENCE}"
                got = extract_json(reply)
                assert got == {"ok": True}, f"got {got!r}"

            def test_first_fenced_block_wins():
                reply = (f"{FENCE}json\n{{\"n\": 1}}\n{FENCE}\nor maybe\n"
                         f"{FENCE}json\n{{\"n\": 2}}\n{FENCE}")
                got = extract_json(reply)
                assert got == {"n": 1}, f"got {got!r}"

            def test_no_fence_uses_first_to_last_brace_keeping_nested_objects():
                reply = 'Result: {"name": "x", "meta": {"tags": ["y"]}} Hope that helps!'
                got = extract_json(reply)
                assert got == {"name": "x", "meta": {"tags": ["y"]}}, f"got {got!r}"

            def test_missing_broken_or_non_dict_json_raises_value_error():
                for reply in ("I cannot do that.", "broken {not json}",
                              f"{FENCE}json\n[1, 2]\n{FENCE}"):
                    try:
                        extract_json(reply)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for {reply!r}"
        ''',
        "solution": r'''
            import json

            FENCE = "`" * 3


            def _candidate(reply):
                start = reply.find(FENCE)
                if start != -1:
                    body_start = reply.find("\n", start)
                    end = reply.find(FENCE, body_start + 1) if body_start != -1 else -1
                    if end != -1:
                        return reply[body_start + 1:end]
                first, last = reply.find("{"), reply.rfind("}")
                if first == -1 or last < first:
                    raise ValueError("no JSON object found")
                return reply[first:last + 1]


            def extract_json(reply):
                try:
                    data = json.loads(_candidate(reply))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON: {exc}") from exc
                if not isinstance(data, dict):
                    raise ValueError("JSON is not an object")
                return data
        ''',
    },
    {
        "id": "json-6",
        "research": {"note": "JSON has no `set` type. Read what the `default` parameter of `json.dumps` does with values it cannot serialise, then come back.",
         "links": [{"title": "json.dumps - Python docs", "url": "https://docs.python.org/3/library/json.html#json.dumps"},
                   {"title": "json module: basic usage", "url": "https://docs.python.org/3/library/json.html#basic-usage"}]},
        "hints": [
            "Parse the input text, compute a few numbers, then produce text again with `json.dumps(..., default=...)`.",
            "Turn a parse error into `ValueError`. Build `failed_ids` as a set. Because JSON has no sets, write a small function that receives the set and returns a sorted list, and pass that function (without calling it) as `default=`.",
            "1) `try: run = json.loads(raw)` / `except json.JSONDecodeError: raise ValueError(...)`. 2) Loop over `run[\"results\"]` counting total, passed, summing latency and adding failed ids to a set. 3) Average = `round(total_latency / total, 1)` or `0.0` when there are no results. 4) Define `def encode(value)` that returns `sorted(value)` for a set. 5) Return `json.dumps(summary, indent=2, default=encode)`.",
        ],
        "title": "Serialise a run report",
        "difficulty": 3,
        "prompt": r'''
            After an eval run, you want a short JSON summary to save or post.

            **Write:** `summarize_run(raw)`

            - `raw`: the JSON **text** (a string) of an eval run, like this:

            ```json
            {"model": "gpt-4o",
             "results": [{"id": "q1", "passed": true, "latency_ms": 820},
                         {"id": "q2", "passed": false, "latency_ms": 1430}]}
            ```

            - **Returns:** a **string**: the JSON text of a summary object with
              **exactly** these five keys:
              - `"model"`: copied from the input
              - `"total"`: number of results (an int)
              - `"passed"`: number of results with `passed` true (an int)
              - `"failed_ids"`: the ids of the failed results, as a **sorted** list
              - `"avg_latency_ms"`: mean of `latency_ms`, rounded to 1 decimal (a float)

            **Rules**
            - Build `failed_ids` as a Python **set** first. JSON has no sets, so write your
              own small function that turns a set into a sorted list, and pass it to
              `json.dumps` as its `default=` argument (a check looks for `default=` in
              your code).
            - Produce the text with `indent=2`.
            - If `"results"` is empty: `total` and `passed` are `0`, `failed_ids` is `[]`,
              `avg_latency_ms` is `0.0`.
            - If `raw` is not valid JSON, raise `ValueError` whose message contains
              `cannot read run`.

            **Examples**
            ```python
            summarize_run('{"model": "m", "results": []}')
            # returns JSON text for {"model": "m", "total": 0, "passed": 0, "failed_ids": [], "avg_latency_ms": 0.0}
            summarize_run("{not json")    # raises ValueError("cannot read run")
            print(summarize_run(raw))     # raw = the JSON above
            # {
            #   "model": "gpt-4o",
            #   "total": 2,
            #   "passed": 1,
            #   "failed_ids": [
            #     "q2"
            #   ],
            #   "avg_latency_ms": 1125.0
            # }
            ```
        ''',
        "starter": r'''
            import json


            def summarize_run(raw):
                ...
        ''',
        "tests": r'''
            import json
            from solution import summarize_run

            RUN = json.dumps({"model": "gpt-4o",
                              "results": [{"id": "q3", "passed": False, "latency_ms": 900},
                                          {"id": "q1", "passed": True, "latency_ms": 820},
                                          {"id": "q2", "passed": False, "latency_ms": 1430}]})

            def test_summary_has_correct_values_and_sorted_failed_ids():
                got = json.loads(summarize_run(RUN))
                expected = {"model": "gpt-4o", "total": 3, "passed": 1,
                            "failed_ids": ["q2", "q3"], "avg_latency_ms": 1050.0}
                assert got == expected, f"summary is {got!r}"

            def test_returns_json_text_not_a_dict():
                assert isinstance(summarize_run(RUN), str), "return JSON text, not a dict"

            def test_text_is_indented_with_2_spaces():
                text = summarize_run(RUN)
                assert '\n  "model"' in text, "use indent=2"

            def test_code_uses_json_dumps_default_argument():
                assert "default=" in source(), "serialise the set via json.dumps(..., default=...)"

            def test_empty_results_give_zeros_and_empty_list():
                got = json.loads(summarize_run('{"model": "m", "results": []}'))
                assert got == {"model": "m", "total": 0, "passed": 0, "failed_ids": [],
                               "avg_latency_ms": 0.0}, f"got {got!r}"

            def test_invalid_json_raises_value_error_cannot_read_run():
                try:
                    summarize_run("{not json")
                except ValueError as exc:
                    assert "cannot read run" in str(exc), f"message was {str(exc)!r}"
                else:
                    raise AssertionError("expected ValueError for invalid JSON")
        ''',
        "solution": r'''
            import json


            def encode_extra(value):
                if isinstance(value, set):
                    return sorted(value)
                raise TypeError(f"cannot serialise {type(value).__name__}")


            def summarize_run(raw):
                try:
                    run = json.loads(raw)
                except json.JSONDecodeError:
                    raise ValueError("cannot read run") from None

                total = 0
                passed = 0
                latency_sum = 0
                failed = set()
                for result in run["results"]:
                    total += 1
                    latency_sum += result["latency_ms"]
                    if result["passed"]:
                        passed += 1
                    else:
                        failed.add(result["id"])
                avg = round(latency_sum / total, 1) if total else 0.0
                summary = {
                    "model": run["model"],
                    "total": total,
                    "passed": passed,
                    "failed_ids": failed,
                    "avg_latency_ms": avg,
                }
                return json.dumps(summary, indent=2, default=encode_extra)
        ''',
    },
]
