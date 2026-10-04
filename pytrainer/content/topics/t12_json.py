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
            ## Turning text from another program into a dict

            Your program sends a question to a chat model. The model runs on another computer, behind a
            service that programs can send requests to (an API). Nothing but text can travel back over
            the network, so the answer arrives like this:

            ```python
            reply = '{"answer": "Paris", "tokens": 12}'
            print(reply)
            # {"answer": "Paris", "tokens": 12}
            print(type(reply).__name__)
            # str
            ```

            It looks like a dict. The type says otherwise: it is one string, and a string has no keys.

            Text written this way, with curly braces, keys in double quotes and colons, is called
            **JSON**. Programs in every language can read and write it, which is why almost every API
            uses it to send data.

            ### Borrowing a tool with import

            Python can turn JSON text into a real dict, but the tool for that is not loaded when your
            program starts. Python keeps many of its tools in separate files and loads one only when
            you ask for it.

            ```python
            import json

            reply = '{"answer": "Paris", "tokens": 12}'
            data = json.loads(reply)
            print(data["answer"])
            # Paris
            print(data["tokens"] + 1)
            # 13
            ```

            `import json` loads the file of tools named `json`. Such a file is called a **module**. The
            line goes at the top of your program, once. After it, you reach each function in the module
            with the module name, a dot and the function name.

            `json.loads(reply)` reads the string and builds the dict that the text describes. The `s` at
            the end of `loads` stands for "string": load from a string. Turning text into data is called
            **parsing**.

            ```quiz
            A program starts with `import json`, and `reply` holds JSON text. Which line parses it?
            - [x] `data = json.loads(reply)` :: Right. The function lives in the module, so you write the module name, a dot and then the function name.
            - [ ] `data = loads(reply)` :: `import json` makes one new name known, and that name is `json`. The name `loads` on its own is unknown, so Python stops with `NameError: name 'loads' is not defined`.
            - [ ] `data = reply.loads()` :: That asks the string for a method named `loads`, and a string has no such method. Python stops with `AttributeError: 'str' object has no attribute 'loads'`.
            ```

            ### Three words that JSON spells its own way

            JSON is not Python. It writes yes, no and "nothing here" as `true`, `false` and `null`, in
            small letters. `json.loads` turns them into Python's `True`, `False` and `None`.

            ```python
            import json

            reply = '{"name": "Ada", "active": true, "boss": null}'
            data = json.loads(reply)
            print(data["active"])
            # True
            print(data["boss"])
            # None
            ```

            Click a key to read its value from the parsed dict:

            ```diagram
            {"type":"dict","title":"Keys of the parsed dict data","name":"data","entries":[["name","Ada"],["active",true],["boss",null]]}
            ```

            JSON text can also hold a list, written in square brackets as in Python. Match each piece of
            JSON to what `json.loads` makes of it:

            ```match
            `true` :: `True`
            `false` :: `False`
            `null` :: `None`
            `{"a": 1}` :: a dict
            `[1, 2]` :: a list
            ```

            **Watch out:** `import json` has to run before the first line that uses the module. Without
            it, Python stops with `NameError: name 'json' is not defined`.

            **In short:** after `import json`, `json.loads(text)` turns JSON text into a dict, and `true`,
            `false` and `null` become `True`, `False` and `None`.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
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
            `json.loads` parses the JSON text and hands back a dict, which is stored under the name
            `data`. The value under `"model"` is a string, and `print` shows a string without its quotes:
            `gpt-4o`. JSON's `false` became Python's `False`, and JSON's `null` became Python's `None`, so
            those are what the second and third `print` show. The text started with a curly brace, so the
            parsed value is a dict, and the last line prints the name of that type: `dict`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Work out what `data` is after the line with `json.loads`. Every `print` below it reads from that value, not from the text.",
            "JSON's `false` and `null` are not Python words. `json.loads` replaces each of them with Python's own value, and `print` shows the Python value.",
            "Your first line is the value stored under `\"model\"`, shown the way `print` shows a string. Your second and third lines are the Python values that JSON's `false` and `null` turn into, with Python's capital letters. Your fourth line is the name of the type that JSON text in curly braces becomes.",
        ],
    },
    {
        "id": "json-s2",
        "lesson": r'''
            ## From a dict to JSON text that people can read

            The last step went from text to a dict. Your program needs the other direction as often. To
            send a request to a model API, or to save settings in a file, the dict in your program has
            to become text again.

            ```python
            import json

            settings = {"lang": "fr", "beta": True, "limit": None}
            text = json.dumps(settings)
            print(text)
            # {"lang": "fr", "beta": true, "limit": null}
            print(type(text).__name__)
            # str
            ```

            `json.dumps(settings)` builds a string that describes the dict in JSON. The `s` stands for
            "string" again: dump to a string. Look at the spelling in the output. `True` became `true`,
            `None` became `null`, and every key is in double quotes, because that is how JSON writes
            them. The dict itself is not changed.

            Turning data into text is called **serializing**. It is the opposite of parsing.

            ```predict
            import json

            message = {"role": "user", "pinned": False, "reply_to": None}
            print(json.dumps(message))
            ---
            The keys and the text `user` are in double quotes. `False` is written `false` and `None` is written `null`. `dumps` puts one space after each colon and one after each comma.
            ```

            ### One long line is hard to read

            A real request has many keys, and `dumps` writes them all on one line. When you print a
            request to find a mistake in it, you want one item per line. `dumps` has a keyword argument
            for that. A keyword argument is the named kind of argument you met in the Functions chapter.

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

            `indent=4` puts every item on its own line and moves each level 4 spaces to the right. The
            number is yours to choose. The data is the same as before. Only line breaks and spaces were
            added.

            ```try
            import json

            order = {"item": "pizza", "extras": ["olives", "ham"]}
            print(json.dumps(order))
            ---
            Add an argument to `json.dumps` so that the text is spread over several lines, with 3 spaces for each level.
            ---
            import json

            order = {"item": "pizza", "extras": ["olives", "ham"]}
            print(json.dumps(order, indent=3))
            ---
            The two extras sit one level deeper than the keys, so they are moved in by 6 spaces: 3 for each level.
            ```

            **Watch out:** the number alone is not enough. `json.dumps(settings, 4)` stops with
            `TypeError: dumps() takes 1 positional argument but 2 were given`. The layout options of
            `dumps` have to be given by name.

            **In short:** `json.dumps(value)` turns a dict into JSON text, and `indent=n` spreads that
            text over several lines with `n` spaces per level.
        ''',
        "title": "Pretty print",
        "difficulty": 0,
        "prompt": r'''
            When a request to a model API goes wrong, the first thing to do is print the request and
            read it. Printed as one long line it is hard to read, so you want it spread over several
            lines.

            **Your job:** finish `pretty(data)` so that it gives back `data` as JSON text with one item
            per line. The function is already written except for one gap, marked `___`. Replace the gap.

            **What goes in**
            - `data`: a dict, for example `{"model": "gpt-4o", "n": 1}`

            **What comes out**
            - a string: the dict as JSON text, spread over several lines

            **Rules**
            - Each level is moved in by exactly 2 spaces.
            - The keys stay in the order they have in the dict.

            **Examples**
            ```python
            print(pretty({"model": "gpt-4o", "n": 1}))
            ```
            prints exactly:
            ```text
            {
              "model": "gpt-4o",
              "n": 1
            }
            ```
            An empty dict has nothing to put on separate lines:
            ```python
            pretty({})    # returns "{}"
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
            "Look at the second example in the lesson. Which extra argument changed the layout of the text?",
            "`json.dumps` has a keyword argument that says how many spaces each level is moved in. The gap is the place for it.",
            "Write the name of that keyword argument, an equals sign and the number of spaces that the task asks for. The number alone does not work: this argument has to be given by name.",
        ],
    },
    {
        "id": "json-s3",
        "lesson": r'''
            ## loads or dumps: which way does it go?

            Two functions, two directions, and names that differ by a few letters. Sooner or later
            everyone calls the wrong one. One way to keep them apart: you load data into your program,
            and you dump it out as text.

            - `json.loads` takes JSON text and gives back a Python value.
            - `json.dumps` takes a Python value and gives back JSON text.

            What happens when you hand JSON text to the wrong one? You might expect an error. Make a
            guess, then read on:

            ```python
            import json

            reply = '{"n": 1}'
            wrong = json.dumps(reply)
            print(wrong)
            # "{\"n\": 1}"
            print(type(wrong).__name__)
            # str
            ```

            No error. A string is a value too, and JSON can store a string. So `dumps` did its normal
            job: it wrote the value it was given as JSON text. The result is the old text inside one
            more pair of double quotes. The backslash in front of each inner quote marks that quote as
            part of the text, not the end of it.

            You wanted a dict and got a longer string, and Python did not complain.

            ```predict
            import json

            reply = '{"score": 9}'
            right = json.loads(reply)
            wrong = json.dumps(reply)
            print(type(right).__name__)
            print(type(wrong).__name__)
            print(right["score"])
            ---
            `loads` parsed the text, so `right` is a dict and `right["score"]` is the number 9. `dumps` wrapped the text in more quotes, so `wrong` is still a string.
            ```

            ### The error shows up later

            The wrong call itself does not fail. What fails is the line that later uses the result as a
            dict:

            ```text
            TypeError: string indices must be integers, not 'str'
            ```

            Read it like this: the value is a string, a string can only be indexed with whole numbers,
            and it was given a key. The message does not point at the mistake. It points at the first
            line that needed a dict.

            ```quiz
            A function ends with `return json.dumps(reply)`, where `reply` is JSON text. The caller then reads `result["model"]`. What happens?
            - [x] `result["model"]` stops with a `TypeError` :: Right. `dumps` handed back a string, and a string cannot be read by key. The error appears where the result is used, not where the wrong function was called.
            - [ ] `json.dumps(reply)` stops with an error, because `reply` is JSON already :: `dumps` accepts a string like any other value. It wraps the text in one more pair of quotes and reports nothing.
            - [ ] `result["model"]` gives the name of the model :: Only a dict can be read by key. `result` is a string, because `dumps` always hands back text.
            ```

            **Watch out:** a value that prints like a dict is not always a dict. When `value["key"]`
            stops with the `TypeError` above, print `type(value).__name__`. If it says `str`, the text
            was never parsed.

            **In short:** `loads` goes from JSON text to a Python value, `dumps` goes from a Python value
            to JSON text, and `dumps` accepts a string without complaint.
        ''',
        "title": "Fix the parser",
        "difficulty": 0,
        "prompt": r'''
            The settings for a model arrive as JSON text, and the rest of the program wants to read them
            as a dict. Someone wrote `parse_config` for that. It runs without an error, but what it
            gives back is a string, not a dict.

            **Your job:** find the bug in `parse_config(text)` and fix it. The code is already in the
            editor, and only one line needs to change.

            **What goes in**
            - `text`: JSON text, for example `'{"temperature": 0.2}'`

            **What comes out**
            - a dict that holds the values from the text: `{"temperature": 0.2}` for the example value

            **Rules**
            - The result is a dict, not a string.
            - The values are Python values. JSON's `true` comes back as `True`.

            **Examples**
            ```python
            parse_config('{"temperature": 0.2}')                  # returns {"temperature": 0.2}
            parse_config('{"model": "gpt-4o", "stream": true}')   # returns {"model": "gpt-4o", "stream": True}
            parse_config('{}')                                    # returns {}
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
            "The two functions of the `json` module go in opposite directions. Which direction does this function need?",
            "The function receives text and should hand back a dict. The call in the editor goes from a Python value to text, which is the wrong way round.",
            "Keep the line as it is, and change only the name of the function that is called on `json`. Use the one that reads JSON text and builds a Python value from it.",
        ],
    },
    {
        "id": "json-s4",
        "lesson": r'''
            ## Reaching a value inside a reply

            A weather service answers your program with JSON text. The number you want, the
            temperature, is not at the top of the reply. It sits inside another part of it:

            ```python
            import json

            reply = '{"city": "Lyon", "now": {"temp": 21, "sky": "clear"}}'
            info = json.loads(reply)
            print(info["city"])
            # Lyon
            print(info["now"])
            # {'temp': 21, 'sky': 'clear'}
            ```

            The value under `"now"` is itself a dict, with keys of its own. (Python prints the text
            inside a dict in single quotes. They are still the same strings.) Data that holds one
            container inside another is called **nested**.

            To reach `temp`, go one level at a time. `info["now"]` gives the inner dict, and the inner
            dict can be asked for its key `"temp"`. You write the two reads one after the other:

            ```python
            import json

            reply = '{"city": "Lyon", "now": {"temp": 21, "sky": "clear"}}'
            info = json.loads(reply)
            print(info["now"]["temp"])
            # 21
            ```

            Python reads this from left to right. `info["now"]` becomes the inner dict, and `["temp"]`
            reads a key of that dict. Each pair of square brackets goes one level deeper. This only works
            after `json.loads`, because before it `reply` is still one string.

            The order of the keys in the text does not matter, because you ask for a key by its name.

            Fill the gap so that the program prints `clear`:

            ```fill
            import json

            reply = '{"city": "Lyon", "now": {"temp": 21, "sky": "clear"}}'
            info = json.loads(reply)
            print(info["now"][___])
            ---
            - [x] "sky" :: Right. `"sky"` is a key of the dict under `"now"`, and its value is `clear`.
            - [ ] "temp" :: `"temp"` is a key of the dict under `"now"`, so the program runs, but it prints `21`, not `clear`.
            - [ ] "city" :: `"city"` is a key of the outer dict, not of the one under `"now"`. Python stops with `KeyError: 'city'`.
            ```

            Three levels need three reads. Change the program so that it prints only `free`:

            ```try
            import json

            reply = '{"user": {"name": "Ada", "plan": {"tier": "free", "seats": 1}}}'
            account = json.loads(reply)
            print(account["user"]["plan"])
            ---
            The program prints a whole dict. Add one more read so that it prints only `free`.
            ---
            import json

            reply = '{"user": {"name": "Ada", "plan": {"tier": "free", "seats": 1}}}'
            account = json.loads(reply)
            print(account["user"]["plan"]["tier"])
            ---
            `account["user"]["plan"]` is the dict that holds `"tier"` and `"seats"`. One more pair of brackets reads the key `"tier"` from it.
            ```

            **Watch out:** every key belongs to one level. `info["temp"]` looks for `temp` at the top, where it
            does not exist, and Python stops with `KeyError: 'temp'`. When you get a `KeyError` for a key
            that you can see in the text, check which level that key is in.

            **In short:** after `json.loads`, use one pair of square brackets for each level, from the
            outside in.
        ''',
        "title": "Dig out the content",
        "difficulty": 0,
        "prompt": r'''
            A chat service sends its answer back as JSON text. The words you want to show the user are
            stored inside that text, one level down.

            **Your job:** write `get_content(raw)` so that it gives back the text of the assistant's reply.

            **What goes in**
            - `raw`: a string of JSON text shaped like
              `'{"message": {"role": "assistant", "content": "Hi there"}}'`. It is text, not a dict yet.

            **What comes out**
            - the string stored under `"content"` inside `"message"`: `"Hi there"` for the example above

            **Rules**
            - Inside `"message"`, the keys may come in either order. The checks try both.
            - The result is the string exactly as stored. If the content is `"42"`, you give back the
              string `"42"`, not the number.

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
            "`raw` is text, and text has no keys. Look at what the lesson does to the reply before it reads anything from it.",
            "First turn the text into a dict and keep the result under a name. Then read the `\"message\"` key of that dict, and read the `\"content\"` key of what you get.",
            "Three steps, in order. One: parse the text and store the result under a name. Two: read the key `\"message\"` from that result. Three: read the key `\"content\"` from the dict you just got, and hand it back with `return`. Steps two and three can be written as one expression with two pairs of square brackets.",
        ],
    },
    {
        "id": "json-s5",
        "lesson": r'''
            ## When the text is not JSON at all

            You asked a model for data as JSON, and it answered with a friendly sentence instead. What
            does `json.loads` do with text that is not JSON? It does not guess. It stops the program,
            and the last line of the traceback says:

            ```text
            json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
            ```

            That is an exception, like the `ValueError` from the Errors chapter. This one is called
            **`json.JSONDecodeError`**. It belongs to the `json` module, so you write its name with the
            module name and a dot, as you do for the functions. Your program can catch it with `try`
            and `except`:

            ```python
            import json
            def item_count(reply):
                try:
                    items = json.loads(reply)
                except json.JSONDecodeError as exc:
                    print("broken at position", exc.pos)
                    return -1
                return len(items)
            print(item_count('["a", "b"'))
            # broken at position 9
            # -1
            ```

            With good text, the `try` block finishes, the `except` block is skipped, and Python carries
            on with the line below the whole `try` statement. With bad text, `json.loads` raises, Python
            jumps into the `except` block, and that block returns `-1`. The last line never runs.

            The exception also knows where parsing gave up. `exc.pos` is the index of that character,
            counted from 0 like a list index. A named value that belongs to an object, read with a dot
            and no parentheses, is called an **attribute**.

            ### Valid JSON is more than curly braces

            JSON text does not have to start with `{`. A list, a number or a string alone is valid JSON
            too:

            ```python
            import json

            print(json.loads("[10, 20]"))
            # [10, 20]
            print(json.loads("7"))
            # 7
            ```

            ```quiz
            Which of these texts makes `json.loads` raise a `JSONDecodeError`?
            - [x] `"{'n': 1}"` :: Right. JSON needs double quotes around keys and strings. Single quotes are how Python prints a dict, but they are not valid JSON.
            - [ ] `'[10, 20]'` :: A list is valid JSON, and `json.loads` gives back the list `[10, 20]`.
            - [ ] `'7'` :: A lone number is valid JSON, and `json.loads` gives back the number 7.
            ```

            ```predict
            import json

            def first_item(reply):
                try:
                    items = json.loads(reply)
                except json.JSONDecodeError as exc:
                    return "bad at " + str(exc.pos)
                return items[0]

            print(first_item('["red", "green"]'))
            print(first_item("red, green"))
            print(first_item("{'n': 1}"))
            ---
            The first text is a valid JSON list, so the `except` block is skipped and the function returns the first item, `red`. The second text is not JSON at all, so parsing fails at index 0, the first character. In the third text, index 0 is the curly brace and index 1 is the single quote that JSON does not allow.
            ```

            **Watch out:** write the full name `json.JSONDecodeError` on the `except` line. With just
            `JSONDecodeError`, nothing seems wrong while the text is valid. The first bad text then stops
            the program with `NameError: name 'JSONDecodeError' is not defined`.

            **In short:** put `json.loads` in a `try` block and catch `json.JSONDecodeError`, and text that
            is not JSON no longer stops the program.
        ''',
        "title": "Is it valid JSON?",
        "difficulty": 0,
        "prompt": r'''
            A model was asked for JSON, but you cannot be sure that it obeyed. Before your program
            trusts an answer, it should check that the answer is JSON at all, without crashing when it is
            not.

            **Your job:** write `is_valid_json(text)` so that it gives back `True` when `json.loads` can
            read the text and `False` when it cannot. Whatever the text is, the function must not stop the
            program.

            **What goes in**
            - `text`: any string, for example `'{"a": 1}'`, `"hello"` or `""`

            **What comes out**
            - the boolean `True` when the text is valid JSON, and the boolean `False` when it is not. They
              must be real booleans, not the strings `"True"` and `"False"`, and not `1` and `0`.

            **Rules**
            - Any valid JSON counts, not only text in curly braces. A list such as `'[1, 2, 3]'` is valid.
            - Text with single quotes, such as `"{'a': 1}"`, is not valid JSON.
            - The empty string `""` is not valid JSON.
            - Catch the specific exception that belongs to the `json` module. A check looks for its name in
              your code.

            **Examples**
            ```python
            is_valid_json('{"a": 1}')    # returns True
            is_valid_json('[1, 2, 3]')   # returns True
            is_valid_json('{"a": }')     # returns False
            is_valid_json("{'a': 1}")    # returns False
            is_valid_json("")            # returns False
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
            "Which line of the function can stop the program when the text is not JSON? The lesson shows where such a line goes.",
            "Put the parsing line in the `try` block, and name the JSON exception on the `except` line. The `except` block hands back the answer for bad text. The answer for good text goes below the whole `try` statement, because Python only gets there when parsing did not fail.",
            "In order: a `try` line. Under it, indented, the line that parses the text. Its result is not needed, so you do not have to store it. Then an `except` line that names the exception type from the `json` module. Under it, indented, a line that hands back the boolean for bad text. Last, at the same indentation as `try`, a line that hands back the boolean for good text.",
        ],
    },
    {
        "id": "json-s6",
        "lesson": r'''
            ## Writing JSON text that never breaks

            To ask a chat model something, your program sends it text that describes the request,
            written in JSON. How would you write that text? A first idea is to glue the pieces together:

            ```python
            question = "Say hi"
            text = '{"prompt": "' + question + '"}'
            print(text)
            # {"prompt": "Say hi"}
            ```

            The text that your program sends to an API to ask for something is called a **request
            body**. This one works until the question contains a double quote:

            ```python
            import json

            question = 'Say "hi"'
            text = '{"prompt": "' + question + '"}'
            print(text)
            # {"prompt": "Say "hi""}
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                print("broken:", exc)
            # broken: Expecting ',' delimiter: line 1 column 18 (char 17)
            ```

            The quote inside the question ended the JSON string too early, and the API would reject the
            text. Your own code has to be right for every question a user can type.

            The way out is to build the request as a dict, the structure Python already understands, and
            let `json.dumps` write the text:

            ```python
            import json

            question = 'Say "hi"'
            text = json.dumps({"prompt": question})
            print(text)
            # {"prompt": "Say \"hi\""}
            print(json.loads(text)["prompt"])
            # Say "hi"
            ```

            `json.dumps` put a backslash in front of the quote that belongs to the text. This is called
            **escaping**: the backslash says "this quote is part of the string, not its end".
            `json.loads` removes the backslash again, so nothing is lost.

            Values can be nested, as in the replies you read in the Nested data step. A dict may hold a list, and that list may hold
            dicts. `json.dumps` writes all levels in one call:

            ```python
            import json

            team = {"name": "docs", "members": [{"who": "Ada", "role": "lead"}]}
            print(json.dumps(team))
            # {"name": "docs", "members": [{"who": "Ada", "role": "lead"}]}
            ```

            ```quiz
            `body` is a dict, and the text may contain double quotes. Which line always gives valid JSON text?
            - [x] `json.dumps(body)` :: Right. It writes every key and value the JSON way and escapes the quotes inside strings.
            - [ ] `str(body)` :: `str` writes the dict the way Python prints it, with single quotes: `{'prompt': 'Say "hi"'}`. That is not valid JSON.
            - [ ] `'{"prompt": "' + question + '"}'` :: Gluing breaks as soon as `question` holds a double quote, as in the example above.
            ```

            Put these lines in an order that builds the request as a dict, turns it into JSON text, and then prints the text and the question read back from it:

            ```order
            import json
            question = 'Say "hi"'
            body = {"prompt": question}
            text = json.dumps(body)
            print(text)
            print(json.loads(text)["prompt"])
            ---
            A name has to exist before a later line uses it. `body` needs `question`, `text` needs `body` and `json`, and both prints need `text`.
            ```

            **Watch out:** building the dict is only half of the job. Until you call `json.dumps`, you hold a
            dict, and an API only accepts text.

            **In short:** build the request as a dict and let `json.dumps` write the text, and the quotes
            inside it are escaped for you.
        ''',
        "title": "Build a request body",
        "difficulty": 0,
        "prompt": r'''
            Before your program can ask a chat model anything, it has to write the question as a request
            body: JSON text with the model name and the user's message in it.

            **Your job:** write `make_body(model, prompt)` so that it gives back the request body as a
            string of JSON text.

            **What goes in**
            - `model`: the model name, a string such as `"gpt-4o"`
            - `prompt`: what the user typed, a string such as `"Hi"`. It may contain double quotes.

            **What comes out**
            - a string of JSON text. It describes a dict with two keys, in this order: `"model"` holds the
              model name, and `"messages"` holds a list with exactly one dict. That dict has the key
              `"role"` with the value `"user"`, and the key `"content"` with the prompt as its value.

            **Rules**
            - The text uses the normal spacing of `json.dumps`: one line, a comma and a space between
              items, and a colon and a space after each key.
            - The text must stay valid JSON when the prompt contains double quotes. A check reads your
              text back with `json.loads` and expects the prompt to come out unchanged.
            - The result is a string, not a dict.

            **Examples**
            ```python
            make_body("gpt-4o", "Hi")
            # returns '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}'
            make_body("m", 'Say "yes"')
            # returns '{"model": "m", "messages": [{"role": "user", "content": "Say \\"yes\\""}]}'
            ```
            In the second example each backslash is written twice only because the result is shown as a
            Python string. The text itself has one backslash in front of each inner quote.
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
            "Look at the lesson again: which two steps turn a request into text that stays valid when the message contains quotes?",
            "First build the whole request as a Python dict, in the shape that \"What comes out\" describes. One of its values is a list that holds a dict. Then convert that dict into text with the function of the `json` module that goes from a Python value to a string, and hand the text back.",
            "In order: write the dict with a key for the model name and a key for the list of messages. The list holds one dict with a key for the role, whose value is the word `user`, and a key for the content, whose value is the `prompt` parameter. Keep the dict under a name. Then hand back what the text-making function gives for that dict.",
        ],
    },
    {
        "id": "json-1",
        "lesson": r'''
            ## Save readable data with a predictable layout

            Two teammates save the same settings with keys inserted in different orders. The data agrees, but the files look different when compared line by line. You can choose a consistent layout when converting the data to JSON.

            ```python
            import json
            settings = {"z": 2, "a": {"y": 4, "b": 1}}
            print(json.dumps(settings, sort_keys=True))
            # {"a": {"b": 1, "y": 4}, "z": 2}
            ```

            Sorting keys affects dictionaries inside the value as well as the outer dictionary. Adding indentation puts nested contents on separate, indented lines. These choices change the representation, not the information the JSON describes.

            ```python
            import json
            print(json.dumps({"enabled": True}, indent=2))
            # {
            #   "enabled": true
            # }
            ```

            Remember the difference between Python's boolean spelling and JSON's spelling. The serializer makes that conversion; you should not replace words manually. The parser reverses it when you load the text.

            ```predict
            import json
            original = {"enabled": True, "limit": None}
            encoded = json.dumps(original, indent=2, sort_keys=True)
            print(json.loads(encoded) == original)
            ---
            The formatting does not change the data, so parsing the saved representation gives an equal dictionary.
            ```

            Converting out and back is a **round trip**. For dictionaries built from JSON-compatible values, it is a useful way to check that formatting has preserved the intended information. Equality here checks the data, whereas comparing the serialized strings also checks spacing and key order.

            ```quiz
            What does indent change?
            - [x] The whitespace layout of the JSON text. :: Parsing ignores that formatting whitespace.
            - [ ] The values stored in nested dictionaries. :: Formatting does not recalculate values.
            ```

            **Watch out:** printing a Python dictionary is not JSON serialization. It may show single quotes, True, or None, which are not the required JSON spellings.

            Choose formatting while serializing, and verify meaning by parsing again.
        ''',
        "hints": [
            "Distinguish the layout of serialized text from the data recovered by parsing.",
            "Use the serializer's indentation and key-order options; let the parser handle JSON values.",
            "Serialize the config with the specified layout, and have the reading helper return the parsed value without extra transformations.",
        ],
        "title": "Pretty config",
        "difficulty": 1,
        "prompt": r'''
            Model configs are saved as readable JSON files and loaded back later. Write
            both directions.

            **Your job:** write `to_pretty_json(config)` and `from_json(text)`

            **What goes in**
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
            ## Read a value after crossing the text boundary

            A service sends a string containing several results and some optional metadata. Before you can use dictionary keys or list positions, turn that string into Python values. Then follow the same container-by-container path you learned in Dictionaries.

            ```python
            import json
            raw = '{"matches": [{"label": "Guide"}], "meta": {"page": 2}}'
            record = json.loads(raw)
            print(record["matches"][0]["label"])
            # Guide
            ```

            The first lookup selects a list, the numeric position selects one dictionary in it, and the last lookup selects its label. Parsing is a separate step from navigating: correct JSON syntax does not guarantee that every key your application wants exists.

            ```fill
            import json
            record = json.loads('{"matches": []}')
            metadata = record.get("meta", ___)
            print(metadata.get("page", 1))
            ---
            - [x] {} :: The fallback is a dictionary, so the next dictionary lookup works.
            - [ ] None :: None has no get method, so the following line would fail.
            - [ ] [] :: A list has no dictionary get method either.
            ```

            Choose a fallback of the right shape for the next operation. An absent optional dictionary can become an empty dictionary, then its absent numeric field can use a number. A default only covers a missing key: if the key exists with `None`, `get` returns `None`. Apply defaults according to the stated input contract.

            ```quiz
            Does successfully parsing JSON prove it contains the expected fields?
            - [x] No; syntax and application shape are separate checks. :: Valid JSON can describe many different values.
            - [ ] Yes; loads knows the response fields your app needs. :: The parser knows JSON syntax, not your application's contract.
            ```

            **Watch out:** indexing JSON text with a string key raises `TypeError`. Parse first, then navigate the resulting containers.

            Turn text into values, then handle required and optional fields deliberately.
        ''',
        "hints": [
            "The incoming value is text, so dictionary operations come after parsing.",
            "Read the first reply through its nested containers, and choose a numeric fallback for absent usage.",
            "Parse the response, follow the first choice to its content, obtain the usage total with the missing-data rule, and return both in a tuple.",
        ],
        "title": "Read a chat completion",
        "difficulty": 1,
        "prompt": r'''
            Every chat API call returns a JSON response. Your app needs two things from it:
            the reply text and how many tokens it cost.

            **Your job:** write `extract_reply(raw)`

            **What goes in**
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


            **What comes out**
            - a tuple `(content, total_tokens)`: the reply string and an int

            **Rules**
            - `content` is `message["content"]` of the **first** item in `"choices"`
              (there may be several choices).
            - `total_tokens` is `usage["total_tokens"]`.
            - If the `"usage"` key is missing, `total_tokens` is `0`.
            - Text containing accented letters or other writing systems must come back unchanged.

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
            ## Edit the data that JSON describes

            A saved record contains a list of document tags, and a new tag needs adding. The saved JSON is text, so it cannot receive a list operation directly. Work on the Python value it describes, then build new JSON text.

            ```python
            import json
            saved = '{"labels": ["draft"]}'
            record = json.loads(saved)
            record["labels"].append("reviewed")
            updated = json.dumps(record)
            print(updated)
            # {"labels": ["draft", "reviewed"]}
            print(saved)
            # {"labels": ["draft"]}
            ```

            The parser creates ordinary dictionaries and lists. You can modify those with the operations you already know. Serializing the edited value produces a new string; it does not rewrite the original string or save a file automatically.

            ```order
            import json
            items = json.loads('["draft"]')
            items.append("reviewed")
            print(json.dumps(items))
            ---
            The text must become a list before append can run. Serialization then describes the whole edited list.
            ```

            This three-stage pattern keeps responsibilities clear: parse the input representation, change the data, serialize the result. Existing list items keep their order unless your editing step explicitly changes it. Appending adds a new final item while leaving earlier items in place.

            ```predict
            items = ["draft"]
            result = items.append("reviewed")
            print(items)
            print(result)
            ---
            Append changes the existing list and returns None. The changed list is still available through items.
            ```

            That return value is an important difference from `json.dumps`, which returns newly created text. Assigning the result of append back to your list name loses access through that name to the list you just changed.

            **Watch out:** serializing the return value of append produces `null`, because that return value is None. Serialize the edited collection instead.

            Parse, edit the resulting value, and serialize the edited value.
        ''',
        "title": "Append to a chat history",
        "difficulty": 1,
        "prompt": r'''
            A chat app stores the conversation as JSON text. Add a new message to it.

            **Your job:** write `add_message(history, role, content)`

            **What goes in**
            - `history`: JSON **text** of a list of message dicts, e.g.
              `'[{"role": "user", "content": "hi"}]'` (may be the empty list `'[]'`)
            - `role`: a string like `"assistant"`
            - `content`: a string like `"hello"`

            **What comes out**
            - a string: the JSON text of the list with
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
            "The edit must happen to a list, not to its JSON representation.",
            "Convert the history into Python data before adding the new final message.",
            "Parse the list, append the required two-field message in the required key order, and serialize the complete updated list.",
        ],
    },
    {
        "id": "json-8",
        "lesson": r'''
            ## Keep human-readable characters in saved text

            A multilingual reply looks correct after loading, but its saved JSON contains sequences beginning with a backslash and `u`. Nothing has necessarily been lost. JSON can represent a character directly or describe it with an escape sequence.

            ```python
            import json
            place = {"city": "Z\u00fcrich"}
            encoded = json.dumps(place)
            print(encoded)
            # {"city": "Z\u00fcrich"}
            print(json.loads(encoded) == place)
            # True
            ```

            The Python string uses a Unicode escape to hold an accented character. Python's default serializer uses an escape for that character in the JSON representation too. **ASCII** is the basic set of 128 characters including English letters and digits; many writing systems need characters outside it.

            ```python
            import json
            name = "caf\u00e9"
            print(json.loads('"caf\\u00e9"') == name)
            # True
            ```

            Here the Python string contains the accented character, and the JSON text describes the same character with an escape. An **escape sequence** lets text formats spell characters using a backslash and a code. Loading interprets the code and recovers the character.

            ```quiz
            Two JSON strings encode an accented character differently but load to equal values. Is one necessarily corrupted?
            - [x] No; different representations can describe the same character. :: Parsing determines the represented value.
            - [ ] Yes; every visible backslash means data was lost. :: Escapes are part of the format, not evidence of corruption.
            ```

            The serializer documentation includes an option controlling whether non-ASCII characters must be escaped. Find that option, read its default, and choose the setting appropriate for a human-readable log. Other JSON escapes, such as those for newlines inside strings, are still required.

            **Watch out:** manually replacing backslashes can damage quotes and control characters. Let the serializer apply the format's rules.

            Choose a readable representation without changing the characters in the data.
        ''',
        "research": {"note": "Open the `json.dumps` documentation and find the parameter that controls whether non-ASCII characters are escaped. Then come back and use it.",
         "links": [{"title": "json.dumps - Python docs", "url": "https://docs.python.org/3/library/json.html#json.dumps"}]},
        "title": "Readable non-English JSON",
        "difficulty": 1,
        "prompt": r'''
            Your logs contain replies in several writing systems. Keep their characters directly readable in the saved JSON text.

            **Your job:** write `to_readable_json(data)`

            **What goes in**
            - `data`: a dictionary, for example one containing a reply with accented letters.

            **What comes out**
            - a string: the JSON text of `data`

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
            "Look in the serializer documentation for the option controlling ASCII-only output.",
            "Change the encoding option rather than manually replacing escaped text.",
            "Serialize with non-ASCII characters permitted directly, keep the default layout, and check that loading restores the original data.",
        ],
    },
    {
        "id": "json-3",
        "hints": [
            "Malformed JSON and valid JSON of the wrong shape are different failures.",
            "Recover from decoding errors using their reported position; separately reject parsed values that are not dictionaries.",
            "Protect the parse with the specific decoding exception, build the requested error record for syntax failures, then validate the successful result's type.",
        ],
        "title": "Safe parse",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            When a model calls a tool, it sends the tool's arguments as a JSON string, and
            that string is often broken. Parse it safely.

            **Your job:** write `parse_tool_args(text)`

            **What goes in**
            - `text`: the tool call's `arguments` string, e.g. `'{"city": "Paris", "days": 3}'`

            **What comes out**
            - a dict (either the parsed arguments, or an error dict: see Rules)

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
            "Each physical line is an independent JSON value, and blank lines still affect line numbers.",
            "Serialize each record separately with its newline, and number input lines before skipping blanks.",
            "Build the output from complete record lines; when reading, parse each nonblank line and translate a decoding failure into an error naming its original line number.",
        ],
        "title": "JSONL eval log",
        "difficulty": 2,
        "prompt": r'''
            Eval runs are logged as **JSONL** (*JSON Lines*): one JSON object per line.
            Write the writer and the reader.

            **Your job:** write `to_jsonl(records)` and `from_jsonl(text)`

            **What goes in**
            - `records`: a list of dicts, e.g. `[{"q": "2+2?", "ok": True}]`
            - `text`: a JSONL string, e.g. `'{"a": 1}\n{"a": 2}\n'`
            - **`to_jsonl` returns:** one string holding all the records, one per line
            - **`from_jsonl` returns:** a list of dicts, one per non-blank line

            **Rules**
            - `to_jsonl`: each record is one line of JSON with the normal `json.dumps`
              spacing (`{"q": "2+2?", "ok": true}`), and **every** line ends with `\n`,
              including the last one.
            - `to_jsonl`: non-ASCII text stays directly readable, without Unicode escape codes.
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
            "Finding the candidate text and validating its JSON are separate stages.",
            "Prefer the first complete fenced block; otherwise find the outermost requested brace span.",
            "Select the candidate using the specified boundaries, parse it, and reject missing text, malformed JSON, or a parsed value that is not a dictionary.",
        ],
        "title": "JSON from a chatty reply",
        "difficulty": 3,
        "prompt": r'''
            You asked the model for JSON, but it replied with prose around it and/or
            wrapped it in markdown *code fences* (a line of three backticks, optionally
            followed by `json`, then the code, then a closing line of three backticks).

            **Your job:** write `extract_json(reply)`

            **What goes in**
            - `reply`: the model's whole reply as a string

            **What comes out**
            - the parsed JSON **object**, as a dict

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
            "The parser, summary calculation, and serializer each have a different job.",
            "Keep failed identifiers in a set and give the serializer a helper for that unsupported type.",
            "Translate parsing failures, calculate counts and mean with an empty-run case, collect failures, and serialize the five-field summary with indentation and the custom conversion helper.",
        ],
        "title": "Serialise a run report",
        "difficulty": 3,
        "prompt": r'''
            After an eval run, you want a short JSON summary to save or post.

            **Your job:** write `summarize_run(raw)`

            **What goes in**
            - `raw`: the JSON **text** (a string) of an eval run, like this:

            ```json
            {"model": "gpt-4o",
             "results": [{"id": "q1", "passed": true, "latency_ms": 820},
                         {"id": "q2", "passed": false, "latency_ms": 1430}]}
            ```


            **What comes out**
            - a **string**: the JSON text of a summary object with
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
