PROJECT = {
    "id": "structured-output",
    "title": "Structured Output with Retries",
    "order": 8,
    "level": "Intermediate",
    "estimated_hours": 2.5,
    "requires": ["json", "errors", "dicts", "regex", "classes"],
    "tags": ["structured-output", "validation", "json", "prompting"],
    "main": "structured.py",
    "files": ["structured.py"],
    "brief": r'''
# Structured output with validation and retries

LLM apps constantly need **data**, not prose: "classify this ticket", "extract the invoice
fields", "return a list of search queries". You ask the model for JSON, and it *mostly*
complies - but sometimes it wraps the JSON in a markdown code fence, adds "Sure! Here is the
result:" in front, forgets a field, or invents an enum value. Robust apps handle this with a
loop: **extract -> validate -> if invalid, tell the model exactly what was wrong and ask
again**, giving up after a few attempts with a clear error.

## What to build

A file `structured.py` with:

```python
class ExtractionError(ValueError): ...
class StructuredOutputError(Exception): ...   # has .errors and .attempts

def extract_json(text): ...
def validate(data, schema): ...
def ask_structured(llm, prompt, schema, max_retries=2): ...
```

### `extract_json(text) -> dict | list`

Find and parse JSON in messy model output:

1. If the text contains fenced code blocks (three backticks, with or without a language
   tag such as `json`), return the parsed content of the **first fenced block that is valid
   JSON**.
2. Otherwise, return the **first** JSON object or array that appears in the text: scan for
   a `{` or `[` that starts a complete, valid JSON value (anything after it is ignored).
   Brackets that don't start valid JSON (e.g. `[see below]`) are skipped.
3. If nothing parses, raise `ExtractionError` (a `ValueError` subclass) with a helpful
   message.

```python
extract_json('{"a": 1}')                                   # {"a": 1}
extract_json('Sure! Here you go:\n```json\n{"a": 1}\n```')  # {"a": 1}
extract_json('Result [draft]: {"a": [1, 2]} hope it helps') # {"a": [1, 2]}
extract_json("no json here")                               # raises ExtractionError
```

### Schema format

A schema is a dict mapping field name to a field spec:

```python
SCHEMA = {
    "title":     {"type": "str"},
    "priority":  {"type": "str", "enum": ["low", "medium", "high"]},
    "estimate":  {"type": "float", "required": False},
    "tags":      {"type": "list", "items": "str"},
}
```

- `type` is one of `"str"`, `"int"`, `"float"`, `"bool"`, `"list"`, `"dict"`.
  `bool` values are **not** valid `int`/`float`. An `int` value **is** a valid `float`.
- `required` defaults to `True`.
- `enum` (optional): the value must be one of the listed values.
- `items` (optional, for lists): every element must have this type.

### `validate(data, schema) -> list[str]`

Return a list of error messages (empty list = valid). Never raise for bad data.

- If `data` is not a dict: return `["expected a JSON object"]`.
- Check fields in schema order, then report unexpected keys in the order they appear in
  `data`. Report **all** problems, at most one per field (a missing, wrongly-typed or
  enum-violating field) plus one per bad list item. Message formats:

| problem | message |
| --- | --- |
| missing required field | `"<field>: missing required field"` |
| wrong type | `"<field>: expected <type>, got <python type name>"` e.g. `"estimate: expected float, got str"` |
| not in enum | `"<field>: <value repr> is not one of <enum list repr>"` |
| bad list item | `"<field>[<index>]: expected <type>, got <python type name>"` |
| key not in schema | `"<field>: unexpected field"` |

### `ask_structured(llm, prompt, schema, max_retries=2) -> dict`

`llm(messages) -> str` takes a chat message list (`[{"role": ..., "content": ...}]`).

1. Start with `messages = [{"role": "user", "content": prompt}]` and call `llm(messages)`.
2. Extract and validate the reply. If extraction fails, the error list is
   `[str(the ExtractionError)]`.
3. If valid, return the parsed dict.
4. If not, and retries remain, append the model's reply as
   `{"role": "assistant", "content": reply}` and then a user message containing **every
   error message** (plus an instruction to reply with corrected JSON only), and call `llm`
   again with the whole conversation.
5. `llm` is called at most `1 + max_retries` times. When all attempts fail, raise
   `StructuredOutputError`; the exception must have `.errors` (the error list from the
   last attempt) and `.attempts` (how many times `llm` was called).
6. `max_retries < 0` raises `ValueError`.

## Running it locally

Write a fake `llm` that returns a list of canned replies in turn (first a broken one, then
a correct one) and print the conversation it receives. Standard library only (`json`, `re`).
''',
    "explore": r'''
# Explore

- **JSON mode vs. Structured Outputs**: look up OpenAI's `response_format` with
  `{"type": "json_schema", ...}` ("Structured Outputs") and how it differs from plain JSON
  mode. Anthropic achieves the same via *tool use* with an `input_schema`. Why does
  constrained decoding make the retry loop you wrote less necessary, but not useless?
- **JSON Schema**: your mini schema is a toy version of the real standard. Skim
  json-schema.org ("type", "enum", "required", "items", "additionalProperties").
- **Pydantic**: research `BaseModel`, `model_validate_json` and `ValidationError`.
  Pydantic models are how most Python AI apps define output schemas (and the OpenAI SDK's
  `client.beta.chat.completions.parse(response_format=MyModel)` accepts them directly).

## Make it real (optional, ungraded)

```bash
uv pip install anthropic   # or: pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
import anthropic
client = anthropic.Anthropic()

def llm(messages):
    resp = client.messages.create(model="claude-haiku-4-5", max_tokens=500, messages=messages)
    return resp.content[0].text

ticket = ask_structured(llm, "Turn this into a ticket as JSON with title, priority "
                        "(low/medium/high) and tags: 'checkout page crashes on Safari'", SCHEMA)
```
''',
    "rubric": [
        "extract_json is robust (fences, prose, stray brackets) without fragile ad-hoc string slicing; uses json.JSONDecoder.raw_decode or equivalent sensibly.",
        "Type checking handles the bool-vs-int subtlety and int-as-float explicitly, via a clear type table rather than a long if/elif chain.",
        "validate collects all errors instead of stopping at the first, and never raises for bad input data.",
        "The retry loop is easy to follow: bounded attempts, conversation built correctly, custom exceptions carry useful context.",
        "Custom exceptions are defined with sensible base classes; names and helpers are clear, with no duplicated logic.",
    ],
    "starter_files": {
        "structured.py": r'''
class ExtractionError(ValueError):
    pass


class StructuredOutputError(Exception):
    pass


def extract_json(text):
    ...


def validate(data, schema):
    ...


def ask_structured(llm, prompt, schema, max_retries=2):
    ...
''',
    },
    "solution_files": {
        "structured.py": r'''
"""Extract, validate and retry structured JSON output from an LLM."""

import json
import re

FENCE_RE = re.compile(r"```[\w-]*[ \t]*\n?(.*?)```", re.DOTALL)
_decoder = json.JSONDecoder()

TYPES = {
    "str": (str,),
    "int": (int,),
    "float": (int, float),
    "bool": (bool,),
    "list": (list,),
    "dict": (dict,),
}


class ExtractionError(ValueError):
    """No valid JSON could be found in a piece of text."""


class StructuredOutputError(Exception):
    """The model never produced output matching the schema."""

    def __init__(self, errors, attempts):
        super().__init__(f"no valid output after {attempts} attempts: {'; '.join(errors)}")
        self.errors = errors
        self.attempts = attempts


def _first_json_value(text):
    for match in re.finditer(r"[\[{]", text):
        try:
            value, _ = _decoder.raw_decode(text, match.start())
        except json.JSONDecodeError:
            continue
        return value
    raise ExtractionError("could not find a valid JSON object or array in the reply")


def extract_json(text):
    for block in FENCE_RE.findall(text):
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    return _first_json_value(text)


def _is_type(value, type_name):
    if isinstance(value, bool) and type_name != "bool":
        return False
    return isinstance(value, TYPES[type_name])


def _check_field(name, value, spec):
    expected = spec["type"]
    if not _is_type(value, expected):
        return [f"{name}: expected {expected}, got {type(value).__name__}"]
    if "enum" in spec and value not in spec["enum"]:
        return [f"{name}: {value!r} is not one of {spec['enum']!r}"]
    errors = []
    if expected == "list" and "items" in spec:
        for i, item in enumerate(value):
            if not _is_type(item, spec["items"]):
                errors.append(f"{name}[{i}]: expected {spec['items']}, got {type(item).__name__}")
    return errors


def validate(data, schema):
    if not isinstance(data, dict):
        return ["expected a JSON object"]
    errors = []
    for name, spec in schema.items():
        if name not in data:
            if spec.get("required", True):
                errors.append(f"{name}: missing required field")
            continue
        errors.extend(_check_field(name, data[name], spec))
    errors.extend(f"{key}: unexpected field" for key in data if key not in schema)
    return errors


def _feedback(errors):
    lines = "\n".join(f"- {e}" for e in errors)
    return ("Your previous reply was not valid. Problems:\n"
            f"{lines}\n"
            "Reply with the corrected JSON object only.")


def ask_structured(llm, prompt, schema, max_retries=2):
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    messages = [{"role": "user", "content": prompt}]
    errors = []
    for attempt in range(1, max_retries + 2):
        reply = llm(messages)
        try:
            data = extract_json(reply)
        except ExtractionError as exc:
            errors = [str(exc)]
        else:
            errors = validate(data, schema)
            if not errors:
                return data
        if attempt <= max_retries:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": _feedback(errors)})
    raise StructuredOutputError(errors, max_retries + 1)
''',
    },
    "tests": r'''
from structured import (ExtractionError, StructuredOutputError, ask_structured,
                        extract_json, validate)

SCHEMA = {
    "title": {"type": "str"},
    "priority": {"type": "str", "enum": ["low", "medium", "high"]},
    "estimate": {"type": "float", "required": False},
    "tags": {"type": "list", "items": "str"},
}

GOOD = {"title": "Fix login", "priority": "high", "tags": ["auth"]}


class ScriptedLLM:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, messages):
        self.calls.append([dict(m) for m in messages])
        return self.replies[len(self.calls) - 1]


def test_extract_plain_json():
    assert extract_json('{"a": 1, "b": [true, null]}') == {"a": 1, "b": [True, None]}
    assert extract_json("  [1, 2, 3]\n") == [1, 2, 3]


def test_extract_from_code_fences():
    text = 'Sure! Here is the result:\n```json\n{"a": 1}\n```\nLet me know!'
    assert extract_json(text) == {"a": 1}, f"got {extract_json(text)!r}"
    text = 'Output:\n```\n[{"x": 2}]\n```'
    assert extract_json(text) == [{"x": 2}]


def test_extract_skips_invalid_fence_for_valid_one():
    text = "```python\nprint({1: 2})\n```\nand the data:\n```json\n{\"ok\": true}\n```"
    assert extract_json(text) == {"ok": True}, f"got {extract_json(text)!r}"


def test_extract_from_prose_skips_stray_brackets():
    text = 'Result [draft]: {"a": [1, 2]} hope it {helps}'
    got = extract_json(text)
    assert got == {"a": [1, 2]}, f"got {got!r}"


def test_extract_raises_extraction_error():
    for text in ["no json here", "{broken: json", ""]:
        try:
            extract_json(text)
        except ExtractionError as exc:
            assert isinstance(exc, ValueError)
            continue
        raise AssertionError(f"expected ExtractionError for {text!r}")


def test_validate_accepts_valid_data():
    assert validate(GOOD, SCHEMA) == []
    assert validate(dict(GOOD, estimate=3), SCHEMA) == [], "an int is a valid float"
    assert validate(dict(GOOD, estimate=2.5), SCHEMA) == []


def test_validate_reports_missing_and_unexpected():
    got = validate({"title": "x", "tags": [], "owner": "bob"}, SCHEMA)
    assert got == ["priority: missing required field", "owner: unexpected field"], f"got {got!r}"


def test_validate_type_and_bool_subtlety():
    schema = {"n": {"type": "int"}, "f": {"type": "float"}, "b": {"type": "bool"}}
    got = validate({"n": True, "f": False, "b": 1}, schema)
    assert got == ["n: expected int, got bool", "f: expected float, got bool",
                   "b: expected bool, got int"], f"got {got!r}"


def test_validate_enum_and_list_items():
    got = validate({"title": "x", "priority": "urgent", "tags": ["a", 3, None]}, SCHEMA)
    assert got == [
        "priority: 'urgent' is not one of ['low', 'medium', 'high']",
        "tags[1]: expected str, got int",
        "tags[2]: expected str, got NoneType",
    ], f"got {got!r}"


def test_validate_non_object():
    assert validate([1, 2], SCHEMA) == ["expected a JSON object"]
    assert validate("text", SCHEMA) == ["expected a JSON object"]


def test_ask_structured_first_try():
    llm = ScriptedLLM(['```json\n{"title": "Fix login", "priority": "high", "tags": ["auth"]}\n```'])
    assert ask_structured(llm, "make a ticket", SCHEMA) == GOOD
    assert llm.calls == [[{"role": "user", "content": "make a ticket"}]], f"calls: {llm.calls!r}"


def test_ask_structured_retries_with_error_feedback():
    bad = '{"title": "Fix login", "priority": "urgent", "tags": ["auth"]}'
    good = '{"title": "Fix login", "priority": "high", "tags": ["auth"]}'
    llm = ScriptedLLM([bad, good])
    assert ask_structured(llm, "make a ticket", SCHEMA) == GOOD
    assert len(llm.calls) == 2, f"llm called {len(llm.calls)} times"
    second = llm.calls[1]
    assert len(second) == 3, f"second call should get 3 messages, got {second!r}"
    assert second[0] == {"role": "user", "content": "make a ticket"}
    assert second[1] == {"role": "assistant", "content": bad}
    assert second[2]["role"] == "user"
    assert "priority: 'urgent' is not one of ['low', 'medium', 'high']" in second[2]["content"], \
        f"feedback message: {second[2]['content']!r}"


def test_ask_structured_feedback_for_unparseable_reply():
    llm = ScriptedLLM(["I cannot do that.", '{"title": "t", "priority": "low", "tags": []}'])
    got = ask_structured(llm, "p", SCHEMA)
    assert got == {"title": "t", "priority": "low", "tags": []}
    assert llm.calls[1][1] == {"role": "assistant", "content": "I cannot do that."}


def test_ask_structured_gives_up_with_custom_error():
    llm = ScriptedLLM(['{"title": 1}'] * 10)
    try:
        ask_structured(llm, "p", SCHEMA, max_retries=2)
    except StructuredOutputError as exc:
        assert exc.attempts == 3, f"attempts={exc.attempts!r}"
        assert "title: expected str, got int" in exc.errors, f"errors={exc.errors!r}"
        assert "priority: missing required field" in exc.errors
    else:
        raise AssertionError("expected StructuredOutputError")
    assert len(llm.calls) == 3, f"llm called {len(llm.calls)} times, expected 3"


def test_ask_structured_zero_retries_and_negative():
    llm = ScriptedLLM(["nope", "nope"])
    try:
        ask_structured(llm, "p", SCHEMA, max_retries=0)
    except StructuredOutputError as exc:
        assert exc.attempts == 1
    else:
        raise AssertionError("expected StructuredOutputError")
    assert len(llm.calls) == 1
    try:
        ask_structured(ScriptedLLM([]), "p", SCHEMA, max_retries=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("max_retries=-1 should raise ValueError")
''',
}
