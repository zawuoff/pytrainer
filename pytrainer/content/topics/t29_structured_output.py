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

LESSON = r'''
## Structured output - chapter notes

Your code can't use "Sure! The customer seems unhappy." It needs
`{"sentiment": "negative", "urgent": true}`. **Structured output** means asking the model
for data in a fixed shape (usually JSON) and *checking* it before you trust it.

**Parse.** `json.loads(text)` turns a JSON string into Python (`dict`, `list`, `str`,
`int`, `float`, `bool`, `None`). Bad JSON raises `json.JSONDecodeError` (a subclass of
`ValueError`); its `.msg` is a short reason like `"Expecting value"`.

```python
import json
print(json.loads('{"ok": true, "n": 2}'))
```

**Extract.** Models wrap JSON in prose or a Markdown code fence (three backticks, often
followed by `json`). Take the text inside the fence, or from the first `{` to the last
`}` (slice end is `rfind("}") + 1`).

**Check the shape.** Required keys present? Right types? Watch out:
`isinstance(True, int)` is `True` - exclude bools when you want a number.

**Defaults & enums.** Fill optional keys with defaults (`{**defaults, **data}`).
Restrict fields to allowed values (an *enum*): normalise (`.strip().lower()`), then check
`in allowed`.

**Coerce.** Models sometimes send `"42"` for `42`. Convert carefully: `int`, then `float`,
else raise.

**JSON Schema** is the standard way to describe a shape:
`{"type": "object", "properties": {"age": {"type": "integer"}}, "required": ["age"]}`.
Type names: `string`, `integer`, `number`, `boolean`, `array`, `object`.
Libraries (`jsonschema`, Pydantic) and provider "structured outputs" features use it.

**Retry with feedback.** On a bad reply, append the model's reply (`assistant`) and a
`user` message that says what was wrong, then call again - up to a max number of
attempts, then raise. Never loop forever.

## Gotchas

- Slicing `text[start:end]` with `end = rfind("}")` cuts off the closing brace.
- Valid JSON is not always a dict - `[1, 2]` and `"hi"` are valid JSON too.
- Don't mutate the caller's dicts or message lists; build new ones.
- A retry loop without a limit can burn your whole API budget.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "structured-output-s1",
        "title": "From text to data",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## A form, not a letter

            Imagine asking a hundred people for their name and age. If each writes you a
            letter, a human must read every one. If each fills in a **form** with a "Name" box
            and an "Age" box, a computer can sort them in a second.

            A model's reply is always text. When you ask for **JSON**, that text is a form your
            code can read. `json.loads` ("load from string") turns it into Python data:

            ```python
            import json

            reply = '{"city": "Paris", "population": 2100000}'
            data = json.loads(reply)
            print(data["city"])
            print(data["population"] > 1000000)
            print(type(data).__name__)
            ```

            Before `loads`, `reply` is just a `str` - `reply["city"]` would fail. After it,
            `data` is a real `dict` with a real `int` inside. Getting data back instead of prose
            is called **structured output**.
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
            ## Opening the envelope

            When a parcel arrives you don't use the box - you open it and use what's inside.
            A JSON reply is the box: a string. Your code wants the dict inside.

            The `json` module from the standard library does the unpacking:

            ```python
            import json

            text = '{"label": "spam", "score": 0.93}'
            result = json.loads(text)
            print(result["label"], result["score"])
            print(json.dumps(result))
            ```

            `json.loads` goes from **text to data**. Its twin `json.dumps` goes from **data to
            text** ("dump to string"). The "s" at the end of both means *string*.

            Watch out: JSON uses `true`, `false` and `null`; after `loads` they become Python's
            `True`, `False` and `None`.
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
            ## Cutting the JSON out of the chatter

            Even when told "reply with JSON only", models often add polite words:
            `Sure! {"a": 1} Hope that helps.` It's like a parcel wrapped in newspaper - you cut
            the newspaper away and keep the parcel.

            The JSON object starts at the **first** `{` and ends at the **last** `}`:

            ```python
            reply = 'Sure! {"a": 1} Hope that helps.'
            start = reply.find("{")
            end = reply.rfind("}")
            print(start, end)
            print(reply[start:end])
            print(reply[start:end + 1])
            ```

            `find` searches from the left, `rfind` from the right, and both return a position
            (an *index*). A slice `text[a:b]` stops **before** index `b` - so to include the
            character at `end`, you slice up to `end + 1`.

            Watch out: this is the classic *off-by-one* error.
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
            ## Checking what's in the box

            A parsed reply is a dict, but the *values* could be anything. The model might send
            `"3"` (text) where you wanted `3` (a number). Before using a value you check its
            type, like a cashier checking a banknote.

            `isinstance(value, type)` answers "is this value of this type?":

            ```python
            print(isinstance(3, int))
            print(isinstance("3", int))
            print(isinstance(2.5, (int, float)))
            print(type(2.5) is float)
            ```

            You can pass a tuple of types to accept any of them. `type(x) is T` is the strict
            version: exactly that type, nothing related.

            Watch out: in Python, `bool` is a special kind of `int` (`True` behaves like `1`).
            That surprises everyone once - this step is where it surprises you.
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
            `3` is an int. `True` is a `bool`, and `bool` is a subclass of `int`, so
            `isinstance(True, int)` is **True** - the gotcha. `0.5` is a float, not an int.
            `type(True) is bool` checks the exact type, so it is `True`. When you validate a
            number field, exclude bools explicitly.
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
            ## The checklist at the door

            A pilot doesn't take off because the plane "looks fine" - they tick a checklist.
            Before your code uses a parsed reply, tick off the keys it needs. A missing key
            later becomes a `KeyError` deep inside your app, far from the real cause.

            The `in` operator checks whether a dict has a key. `all(...)` is `True` only if
            every check inside is `True`:

            ```python
            reply = {"title": "Bug in login", "priority": "high"}
            print("title" in reply)
            print("owner" in reply)
            print(all(key in reply for key in ["title", "priority"]))
            print(all(key in reply for key in ["title", "owner"]))
            ```

            Checking that the right keys exist is the first part of **validating the shape**
            of structured output.

            Watch out: `all([])` is `True` - with nothing to check, nothing failed.
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
            ## Pre-printed answers on a form

            Some forms come with answers already filled in: "Country: France" unless you cross
            it out. Those are **defaults**. Models often skip optional fields, so your code fills
            them in rather than crashing.

            Unpacking two dicts into a new one with `**` merges them. When a key appears in
            both, the **later** one wins:

            ```python
            defaults = {"priority": "medium", "tags": []}
            reply = {"title": "Bug", "priority": "high"}
            merged = {**defaults, **reply}
            print(merged)
            print(defaults)
            ```

            Putting the defaults first and the reply second means: use the model's value when
            there is one, the default otherwise. And because this builds a **new** dict,
            neither original changes.

            Watch out: `defaults.update(reply)` would change your defaults dict for every
            later call.
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
            ## A multiple-choice question

            A free-text answer can say anything. A multiple-choice question only accepts A, B
            or C. When your code branches on a field like `sentiment`, it needs multiple-choice:
            `"positive"`, `"negative"` or `"neutral"` - not `"kinda good"`.

            A fixed list of allowed values is called an **enum** (short for *enumeration*).
            Checking a value is one `in` test, and a bad value should stop the program loudly:

            ```python
            allowed = ["positive", "negative", "neutral"]
            for value in ["negative", "kinda good"]:
                if value in allowed:
                    print("ok:", value)
                else:
                    print("rejected:", value)
            ```

            In a function you'd `raise ValueError(...)` instead of printing, so the caller can
            catch it (and maybe ask the model again).

            Watch out: `"Positive"` is not `"positive"` - comparisons are case-sensitive.
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
            ## A result slip instead of an alarm

            When a lab test fails, the lab doesn't set off the fire alarm - it sends a slip:
            "sample unreadable, reason: too small". Your app should treat a bad model reply the
            same way: report *what* went wrong so the next step (retry, log, fallback) can act.

            `json.loads` raises `json.JSONDecodeError` on bad text. Its `.msg` attribute is a
            short reason. And valid JSON isn't always a dict:

            ```python
            import json

            for text in ['{"a": 1}', "Sure!", "[1, 2]"]:
                try:
                    value = json.loads(text)
                    print("parsed a", type(value).__name__)
                except json.JSONDecodeError as error:
                    print("bad JSON:", error.msg)
            ```

            Returning a pair `(result, error)` - where exactly one of them is `None` - is a
            common pattern for "this might fail and that's normal". The caller unpacks it:
            `data, error = safe_parse(text)`.
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
            ## When the parcel comes in a gift box

            Models love Markdown. Ask for JSON and you often get it inside a **code fence**:
            a line of three backticks (maybe followed by `json`), the JSON, then three
            backticks again - with chatter around it. The chatter can even contain braces,
            like "Here is {your} data", which breaks the first-`{` trick.

            If there *is* a fence, the JSON is exactly what's inside it. A regular expression
            with a capture group grabs it:

            ```python
            import re

            tick = "`" * 3
            reply = f"Here is {{your}} data:\n{tick}json\n{{\"a\": 1}}\n{tick}\nEnjoy!"
            match = re.search(tick + r"(?:json)?\s*(.*?)" + tick, reply, re.DOTALL)
            print(match.group(1))
            ```

            `(?:json)?` means "optionally the word json" (without capturing it), `.*?` takes as
            little as possible, and `re.DOTALL` lets `.` match newlines too. No fence? Then
            `re.search` returns `None`, and you parse the whole (stripped) reply.
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
            ## The customs officer

            A customs officer checks a list: is every required item declared, and is each item
            what it claims to be? They don't stop at the first problem - they write down
            everything wrong, so you can fix it all at once.

            You can describe the shape you expect as a dict of **key -> Python type**, then
            walk it and collect problems in a list:

            ```python
            expected = {"name": str, "age": int}
            data = {"name": "Ada", "age": "36"}
            problems = []
            for key, kind in expected.items():
                value = data[key]
                if not isinstance(value, kind):
                    problems.append(f"{key} should be {kind.__name__}, got {type(value).__name__}")
            print(problems)
            ```

            Types are values too: `int.__name__` is the string `"int"`. An empty problem list
            means "valid". Remember the bool gotcha from earlier: `isinstance(True, int)` is
            `True`, so number checks must reject bools on purpose.
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
            ## Tidying the form before filing it

            A clerk receiving forms fixes the small stuff before filing: "HIGH" becomes "high",
            stray spaces go, a blank optional box gets the standard answer. Only truly broken
            forms are sent back.

            Structured output needs the same tidy-up step, combining what you've learned:
            defaults, a light clean-up (**normalising**), then an enum check.

            ```python
            ALLOWED = ["low", "medium", "high"]
            raw = {"title": "Login broken", "priority": "  HIGH "}
            priority = raw.get("priority", "medium").strip().lower()
            print(repr(priority), priority in ALLOWED)
            clean = {"title": raw["title"], "priority": priority}
            print(clean)
            ```

            `dict.get(key, default)` returns the default when the key is missing - a neat way
            to apply one default. Building a fresh dict with only the keys you want also drops
            anything extra the model invented.

            Watch out: a list default like `[]` must be a **new** list each time, or two
            tickets end up sharing one tags list.
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
            ## Reading a price tag written by hand

            A handwritten price tag says "12" - to add it up you read it as the number 12.
            Models do the same thing to you: they sometimes put numbers in quotes, `"42"` or
            `"3.5"`. Rejecting those outright is harsh; converting them carefully is kinder.

            `int("42")` works, `int("3.5")` raises `ValueError`, and `float("3.5")` works.
            So try `int` first, then `float`, and give up only if both fail:

            ```python
            for text in ["42", "3.5", "lots"]:
                try:
                    print(int(text))
                except ValueError:
                    try:
                        print(float(text))
                    except ValueError:
                        print("not a number:", text)
            ```

            Changing a value from one type to another is called **type coercion**. Only coerce
            the fields you expect to be numbers, and only when the value is a string - a real
            number or `True` should be left alone.
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
            ## Putting it together: the standard form description

            Instead of a home-made `{"age": int}`, the industry describes shapes with **JSON
            Schema** - the same format providers accept for structured outputs and tool
            definitions. You'll check a small part of it: `type`, `properties`, `required`, `enum`.
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
            ## Putting it together: "try again, and here's what was wrong"

            When a reply isn't valid, don't just ask again - tell the model *why*. Append its bad
            reply as an `assistant` message and your complaint as a `user` message, then call it
            again. Always cap the number of attempts. In tests, `llm` is a fake function that
            returns scripted replies.
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
