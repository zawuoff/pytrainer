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

LESSON = r'''
## Chapter notes: JSON

**JSON** is a text format for data. It looks like Python dicts and lists, but it is one
string. LLM APIs, tool calls, config files and structured outputs all speak JSON.

| direction | function | memory trick |
| --- | --- | --- |
| text -> Python | `json.loads(text)` | **load** from a **s**tring |
| Python -> text | `json.dumps(value)` | **dump** to a **s**tring |
| file -> Python | `json.load(fh)` | no "s": works on an open file |
| Python -> file | `json.dump(value, fh)` | no "s": works on an open file |

**Spellings** (translated for you): `true`/`false` <-> `True`/`False`, `null` <-> `None`,
array <-> list, object <-> dict. JSON strings always use **double quotes**.

**`json.dumps` options**
- `indent=2` - pretty, multi-line output
- `sort_keys=True` - keys in alphabetical order, at every level
- `ensure_ascii=False` - keep `é`, emoji etc. readable instead of `é`
- `default=fn` - called for values JSON cannot store (like a `set`); return something it can

**Nested data**: go one step at a time: `data["choices"][0]["message"]["content"]`.
Use `.get(key, default)` for keys that may be missing: `data.get("usage", {}).get("total_tokens", 0)`.

**Broken JSON** raises `json.JSONDecodeError` (a kind of `ValueError`); `.pos` is the index
where parsing failed.

```python
import json

try:
    json.loads('{"city": Paris}')
except json.JSONDecodeError as exc:
    print("broken at", exc.pos)
```

**Round trip**: `json.loads(json.dumps(d)) == d` - parse, change the Python value, dump again.

**JSONL** (JSON Lines): one JSON object per line - common for logs and eval datasets.

**Gotchas**
- `json.dumps(text)` does not parse - it wraps your string in quotes.
- `'{"ok": True}'` is not JSON (use `true`), `"{'a': 1}"` is not JSON (use double quotes).
- After parsing, index the result (`data["x"]`), not the original text.
- Models often wrap JSON in prose or code fences - find the JSON part before parsing.
'''

EXERCISES = [
    {
        "id": "json-s1",
        "lesson": r'''
            Think of JSON as a **parcel of data sent through the post**. On the outside it is just
            text (a string). To use what is inside, you unpack it. Python's `json` module does the
            unpacking with `json.loads` - read it as "**load** from a **s**tring".

            ```python
            import json

            text = '{"name": "Ada", "active": true, "boss": null}'
            data = json.loads(text)
            print(type(text).__name__, "->", type(data).__name__)
            print(data["name"], data["active"], data["boss"])
            ```

            JSON is not Python, so a few words are spelled differently. `json.loads` translates them:
            `true` -> `True`, `false` -> `False`, `null` -> `None`, and a JSON array `[...]` becomes a list.

            The proper name for turning text into data is **parsing** (you will also hear
            *deserializing*). The text coming back from every LLM API is JSON, so this is the first
            thing you do with a reply.
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
            `json.loads` turns the JSON text into a Python dict. On the way, JSON's `false`
            becomes Python's `False` and `null` becomes `None`. The strings print without
            quotes, and the type of the result is `dict`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`json.loads` turns JSON text into Python values. Think about what each JSON value becomes.",
            "JSON `false` and `null` are not Python words - they get translated to Python's own spellings.",
            "Line 1 is the model string, line 2 is what `false` becomes (`False`), line 3 is what `null` becomes (`None`), line 4 is the type name of a parsed JSON object.",
        ],
    },
    {
        "id": "json-s2",
        "lesson": r'''
            Unpacking has a mirror: **packing**. `json.dumps` ("**dump** to a **s**tring") takes a
            Python dict or list and writes it out as JSON text, ready to send or save.

            ```python
            import json

            settings = {"lang": "fr", "beta": True, "limit": None}
            print(json.dumps(settings))
            print(json.dumps(settings, indent=4))
            ```

            By default everything lands on one line. For humans that is hard to read, so `dumps`
            takes extra **keyword arguments** that change the layout. `indent=4` puts each item on
            its own line, indented 4 spaces per level. Notice the Python words were translated back:
            `True` -> `true`, `None` -> `null`.

            The proper name for turning data into text is **serializing**. Pretty-printed JSON is
            what you want when you log an API request to debug it.
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
            The two functions look alike, so the classic bug is using the wrong one. Picture a
            **one-way door** for each direction:

            - `loads`: text **in**, Python **out**
            - `dumps`: Python **in**, text **out**

            ```python
            import json

            text = '{"n": 1}'
            wrong = json.dumps(text)
            right = json.loads(text)
            print(type(wrong).__name__, wrong)
            print(type(right).__name__, right)
            ```

            `json.dumps` on a string does not fail - it happily wraps your text in *another* layer of
            quotes and gives you a string back. That is why this bug is sneaky: nothing crashes, you
            just get the wrong **type**. When a result looks right but `data["key"]` fails, check
            `type(data)` first.
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
            API replies are **Russian dolls**: a dict inside a dict inside a list. You open them one
            layer at a time, each `[...]` going one level deeper.

            ```python
            import json

            raw = '{"user": {"profile": {"city": "Lyon"}}, "tags": ["a", "b"]}'
            data = json.loads(raw)
            print(data["user"])
            print(data["user"]["profile"]["city"])
            print(data["tags"][1])
            ```

            Read a chain like `data["user"]["profile"]["city"]` from left to right: "in `data`, take
            `user`; in that, take `profile`; in that, take `city`". Use a **key** (a string) for a
            dict and a **position** (an int) for a list.

            Watch out: you can only index after parsing. `raw["user"]` fails, because `raw` is still a
            string - one flat parcel, not the dolls inside.
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
            Models are chatty and sometimes send **broken JSON**: a missing quote, a cut-off reply.
            `json.loads` then raises an error instead of guessing. Think of a strict **customs
            officer**: anything that is not perfectly valid gets stopped at the border.

            The error has a specific name: `json.JSONDecodeError`. You catch it with `try` / `except`,
            exactly like the errors you have caught before.

            ```python
            import json

            for text in ['{"ok": true}', "{'ok': true}"]:
                try:
                    print("parsed:", json.loads(text))
                except json.JSONDecodeError as exc:
                    print("rejected at position", exc.pos)
            ```

            `exc.pos` is the character index where parsing failed - handy for error messages.
            Single quotes are the most common reason for rejection: JSON strings **must** use double
            quotes. Catch the specific error, not every error, so real bugs are not hidden.
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
            When you call an LLM API, you send a **request body**: a JSON object with the model name
            and a list of messages. The easy, safe way to build it is to build a normal Python dict
            first, then pack it with `json.dumps`.

            ```python
            import json

            body = {"name": "search", "args": {"query": 'the "best" pizza', "limit": 3}}
            print(json.dumps(body))
            ```

            Look at the output: `dumps` added the double quotes, the `\"` escape for the quotes
            inside the text, and the standard spacing: `", "` between items and `": "` after each key.
            Keys come out in the order you wrote them.

            Watch out: never build JSON by gluing strings together with an f-string. As soon as the
            user's text contains a quote, your "JSON" breaks. Let `json.dumps` do the escaping.

            A dict inside a list inside a dict is completely normal - that is exactly the shape of a
            chat message list: `{"messages": [{"role": ..., "content": ...}]}`.
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
            Two more `dumps` options make saved config files pleasant to read and to compare:

            - `indent=2` - one item per line
            - `sort_keys=True` - keys in **alphabetical order**, inside nested dicts too

            ```python
            import json

            cfg = {"zeta": 1, "alpha": {"y": 2, "b": 3}}
            print(json.dumps(cfg, sort_keys=True))
            back = json.loads(json.dumps(cfg))
            print(back == cfg)
            ```

            Sorted keys mean the same config always produces the same text, so a `git diff` shows only
            real changes. Think of it as filing papers in alphabetical order.

            The second idea here is the **round trip**: pack a value with `dumps`, unpack it with
            `loads`, and you get an equal dict back. If a round trip changes your data, something is
            wrong. Remember: layout options change how the text *looks*, never what it *means*.
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
            A real chat completion reply is a set of Russian dolls with a **list** in the middle:

            ```json
            {"choices": [{"message": {"role": "assistant", "content": "..."}}],
             "usage": {"total_tokens": 12}}
            ```

            `choices` is a list because you can ask for several answers; you usually want item `0`.
            Some keys are optional. For those, use `.get(key, default)` so a missing key gives a
            default instead of a `KeyError`. You can even chain two `.get` calls by using an empty dict
            as the first default:

            ```python
            import json

            data = json.loads('{"results": [{"title": "RAG"}]}')
            print(data["results"][0]["title"])
            meta = data.get("meta", {})
            print(meta.get("page", 1))
            print(data.get("meta", {}).get("page", 1))
            ```

            The empty dict `{}` is a stand-in: "if there is no `meta`, pretend it is an empty one",
            and then the second `.get` falls back to its own default. Returning two values at once is
            done with a **tuple**: `return a, b`.
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
            Changing JSON text is like **editing a paper form**: you cannot write into the middle of
            the text safely, so you copy it into Python, edit it there, and print a fresh form.

            1. `loads` - text -> Python list/dict
            2. change the Python value (append, set a key, ...)
            3. `dumps` - Python -> new text

            ```python
            import json

            raw = '{"tags": ["rag"]}'
            data = json.loads(raw)
            data["tags"].append("json")
            print(json.dumps(data))
            ```

            This pattern is everywhere in AI apps: a chat history stored as JSON text is loaded,
            the new message is appended, and the whole list is saved or sent again. The new text is
            built by `dumps`, so its spacing is always the standard one: `", "` and `": "`.

            Watch out: `list.append` changes the list and returns `None`. Don't write
            `data = data.append(...)`.
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
            Try this and look closely at the output:

            ```python
            import json

            print(json.dumps({"city": "Zürich"}))
            print(json.loads(json.dumps({"city": "Zürich"})))
            ```

            By default `json.dumps` plays it safe and writes every non-English character as an
            **escape code**: `ü` becomes `ü`. It is still the same data (loading it gives `Zürich`
            back), but a log full of `é` and `😀` is hard for humans to read, and the
            text is longer.

            The ASCII table covers plain English letters, digits and punctuation. Anything outside it
            (accents, emoji, Chinese, Arabic...) is what gets escaped. Model replies are full of such
            characters.

            `json.dumps` has a keyword argument that switches this escaping off. We have not used it
            yet - finding it in the documentation is part of this step. Reading the docs for a function
            you already know is how you discover its extra powers.
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
            - **Returns:** a dict (either the parsed arguments, or an error dict - see Rules)

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
            "To build the text, turn each record into a compact JSON string (keeping non-ASCII characters readable) and add a newline after each. To read it, split the text into lines, skip blank ones, and parse the rest - turning a parse error into a `ValueError` that says which line broke.",
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
