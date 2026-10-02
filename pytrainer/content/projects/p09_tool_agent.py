PROJECT = {
    "id": "tool-agent",
    "title": "Tool-Calling Agent",
    "order": 9,
    "level": "Advanced",
    "estimated_hours": 3.5,
    "requires": ["classes", "dataclasses", "json", "errors", "dicts"],
    "tags": ["agents", "tool-calling", "function-calling", "introspection"],
    "main": "agent.py",
    "files": ["agent.py"],
    "brief": r'''
# Tool-calling agent

"Agents" are LLMs in a loop with tools. You describe your Python functions to the model as
JSON schemas; the model replies either with a final answer or with **tool calls** (a tool
name plus JSON-encoded arguments). Your code runs the tools, feeds the results back as
`tool` messages, and asks the model again - until it answers or a step limit is hit.
Every framework (OpenAI Agents SDK, Anthropic tool runner, LangGraph, MCP clients) is
this loop plus polish. Build it yourself once and the frameworks stop being magic.

## What to build

A file `agent.py` with:

```python
class AgentLoopError(RuntimeError): ...

class ToolRegistry:
    def tool(self, func): ...          # decorator
    def schemas(self): ...
    def dispatch(self, call): ...

def run_agent(llm, registry, user_message, max_steps=5, system=None): ...
```

### `ToolRegistry.tool` - a decorator

```python
registry = ToolRegistry()

@registry.tool
def get_weather(city: str, days: int = 1) -> dict:
    """Get the weather forecast for a city.

    More details that are not part of the description.
    """
    ...
```

- Registers the function under its `__name__` and **returns the function unchanged**
  (it must still be callable directly).
- Registering a second tool with the same name raises `ValueError`.
- Every parameter must have a type annotation from this table, otherwise raise
  `TypeError` at decoration time. `*args` / `**kwargs` are not allowed either (`TypeError`).

| Python | JSON schema type |
| --- | --- |
| `str` | `"string"` |
| `int` | `"integer"` |
| `float` | `"number"` |
| `bool` | `"boolean"` |
| `list` | `"array"` |
| `dict` | `"object"` |

### `schemas() -> list[dict]`

One description per tool, in registration order:

```python
{
    "name": "get_weather",
    "description": "Get the weather forecast for a city.",   # first line of the docstring, stripped; "" if none
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}, "days": {"type": "integer"}},
        "required": ["city"],        # parameters without a default, in signature order
    },
}
```

### `dispatch(call) -> str`

`call` is `{"id": "call_1", "name": "get_weather", "arguments": '{"city": "Paris"}'}` -
note `arguments` is a **JSON string**, exactly as LLM APIs send it.

- Parse the arguments, check them and call the tool with them as keyword arguments.
- If the tool returns a `str`, return it as is; otherwise return `json.dumps(result)`.
- **Never raise.** Models make mistakes, and the error must go back to the model so it
  can fix its call. Return a string starting with `"Error: "` when:
  - the tool name is unknown,
  - `arguments` is not valid JSON, or is not a JSON object,
  - a required argument is missing or an unknown argument is given,
  - an argument has the wrong JSON type (use the same table; a `bool` is not an `int`,
    an `int` is accepted for `float`),
  - the tool itself raises an exception (include the exception type name and message,
    e.g. `"Error: ZeroDivisionError: division by zero"`).

### `run_agent(llm, registry, user_message, max_steps=5, system=None) -> str`

`llm(messages, tools)` receives the conversation and `registry.schemas()` and returns
one of:

```python
{"type": "final", "content": "It is sunny in Paris."}
{"type": "tool_calls", "calls": [{"id": "c1", "name": "get_weather", "arguments": "{...}"}, ...]}
```

1. The conversation starts with `{"role": "system", "content": system}` (only if `system`
   is given) followed by `{"role": "user", "content": user_message}`.
2. Call `llm`. On `"final"`, return its `content`.
3. On `"tool_calls"`, append `{"role": "assistant", "tool_calls": calls}`, then for each
   call in order append
   `{"role": "tool", "tool_call_id": call["id"], "name": call["name"], "content": <dispatch result>}`,
   and loop.
4. Each `llm` call is one step. If `max_steps` calls have been made without a final
   answer, raise `AgentLoopError` with a message that mentions the step limit.
5. Any other reply `type` raises `ValueError`.

## Running it locally

Write a scripted fake `llm` that returns a tool call on the first step and a final answer
built from the last `tool` message on the second. Print the full `messages` list at the
end to see the transcript. Standard library only (`inspect`, `json`, `typing`).
''',
    "explore": r'''
# Explore

- **`inspect.signature` and `typing.get_type_hints`**: why does `get_type_hints` behave
  better than reading `param.annotation` when a module uses
  `from __future__ import annotations`? Also look up `inspect.getdoc` / `inspect.cleandoc`.
- **Function calling APIs**: read OpenAI's "Function calling" guide and Anthropic's
  "Tool use" docs. Compare the shapes: OpenAI's `tool_calls[].function.arguments` (a JSON
  string) vs Anthropic's `tool_use` content blocks with `input` (already a dict) and
  `tool_result` blocks. Also look up *parallel tool calls*.
- **MCP (Model Context Protocol)**: an open standard for exposing tools to any LLM client.
  Look up how an MCP server describes tools (`inputSchema`) - it is the same idea as your
  `schemas()`.

## Make it real (optional, ungraded)

```bash
uv pip install openai     # or: pip install openai
export OPENAI_API_KEY=sk-...
```

```python
import json
from openai import OpenAI
client = OpenAI()

def llm(messages, tools):
    api_messages = []
    for m in messages:
        if m["role"] == "assistant":
            api_messages.append({"role": "assistant", "tool_calls": [
                {"id": c["id"], "type": "function",
                 "function": {"name": c["name"], "arguments": c["arguments"]}}
                for c in m["tool_calls"]]})
        elif m["role"] == "tool":
            api_messages.append({"role": "tool", "tool_call_id": m["tool_call_id"],
                                 "content": m["content"]})
        else:
            api_messages.append(m)
    resp = client.chat.completions.create(
        model="gpt-4o-mini", messages=api_messages,
        tools=[{"type": "function", "function": s} for s in tools])
    msg = resp.choices[0].message
    if msg.tool_calls:
        return {"type": "tool_calls", "calls": [
            {"id": c.id, "name": c.function.name, "arguments": c.function.arguments}
            for c in msg.tool_calls]}
    return {"type": "final", "content": msg.content}
```
''',
    "rubric": [
        "Schema generation uses inspect/typing properly (signature, defaults, type hints, docstring) with a clear type mapping table.",
        "dispatch never raises: every failure mode (unknown tool, bad JSON, bad/missing args, tool exceptions) becomes a clear error string for the model.",
        "The agent loop is short and readable, bounds the number of steps, and builds the message transcript exactly as specified.",
        "Responsibilities are well separated (registration, validation, dispatch, loop) with small helpers instead of one large function.",
        "Custom exceptions and error messages are informative; no bare except that would hide programming errors in the loop itself.",
    ],
    "starter_files": {
        "agent.py": r'''
class AgentLoopError(RuntimeError):
    pass


class ToolRegistry:
    def __init__(self):
        ...

    def tool(self, func):
        ...

    def schemas(self):
        ...

    def dispatch(self, call):
        ...


def run_agent(llm, registry, user_message, max_steps=5, system=None):
    ...
''',
    },
    "solution_files": {
        "agent.py": r'''
"""A minimal tool registry and tool-calling agent loop."""

import inspect
import json
import typing

JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean",
              list: "array", dict: "object"}
PY_TYPES = {"string": (str,), "integer": (int,), "number": (int, float),
            "boolean": (bool,), "array": (list,), "object": (dict,)}


class AgentLoopError(RuntimeError):
    """The agent did not produce a final answer within its step budget."""


def _matches(value, json_type):
    if isinstance(value, bool) and json_type != "boolean":
        return False
    return isinstance(value, PY_TYPES[json_type])


def _describe(func):
    hints = typing.get_type_hints(func)
    properties, required = {}, []
    for name, param in inspect.signature(func).parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            raise TypeError(f"{func.__name__}: *args/**kwargs are not supported in tools")
        hint = hints.get(name)
        if hint not in JSON_TYPES:
            raise TypeError(f"{func.__name__}: parameter {name!r} needs a supported type hint")
        properties[name] = {"type": JSON_TYPES[hint]}
        if param.default is param.empty:
            required.append(name)
    doc = inspect.getdoc(func) or ""
    return {
        "name": func.__name__,
        "description": doc.splitlines()[0].strip() if doc else "",
        "parameters": {"type": "object", "properties": properties, "required": required},
    }


class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._schemas = {}

    def tool(self, func):
        name = func.__name__
        if name in self._tools:
            raise ValueError(f"tool {name!r} is already registered")
        self._schemas[name] = _describe(func)
        self._tools[name] = func
        return func

    def schemas(self):
        return list(self._schemas.values())

    def _check_arguments(self, name, raw):
        try:
            args = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return None, "arguments are not valid JSON"
        if not isinstance(args, dict):
            return None, "arguments must be a JSON object"
        params = self._schemas[name]["parameters"]
        missing = [p for p in params["required"] if p not in args]
        if missing:
            return None, f"missing required argument(s): {', '.join(missing)}"
        unknown = [a for a in args if a not in params["properties"]]
        if unknown:
            return None, f"unknown argument(s): {', '.join(unknown)}"
        for arg, value in args.items():
            expected = params["properties"][arg]["type"]
            if not _matches(value, expected):
                return None, f"argument {arg!r} must be of type {expected}"
        return args, None

    def dispatch(self, call):
        name = call.get("name")
        if name not in self._tools:
            return f"Error: unknown tool {name!r}"
        args, problem = self._check_arguments(name, call.get("arguments"))
        if problem:
            return f"Error: {problem}"
        try:
            result = self._tools[name](**args)
        except Exception as exc:  # the model must see tool failures, not crash the loop
            return f"Error: {type(exc).__name__}: {exc}"
        return result if isinstance(result, str) else json.dumps(result)


def run_agent(llm, registry, user_message, max_steps=5, system=None):
    messages = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_message})
    for _ in range(max_steps):
        reply = llm(messages, registry.schemas())
        if reply["type"] == "final":
            return reply["content"]
        if reply["type"] != "tool_calls":
            raise ValueError(f"unexpected reply type {reply['type']!r}")
        calls = reply["calls"]
        messages.append({"role": "assistant", "tool_calls": calls})
        for call in calls:
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "name": call["name"], "content": registry.dispatch(call)})
    raise AgentLoopError(f"no final answer after max_steps={max_steps} steps")
''',
    },
    "tests": r'''
import copy
import json
from agent import AgentLoopError, ToolRegistry, run_agent


def make_registry():
    reg = ToolRegistry()

    @reg.tool
    def get_weather(city: str, days: int = 1) -> dict:
        """Get the weather forecast for a city.

        Extra details that are not part of the description.
        """
        return {"city": city, "days": days, "sky": "sunny"}

    @reg.tool
    def divide(a: float, b: float) -> float:
        """  Divide a by b.  """
        return a / b

    @reg.tool
    def shout(text: str, loud: bool = True, tags: list = None, meta: dict = None):
        return text.upper() if loud else text

    return reg


class ScriptedLLM:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, messages, tools):
        self.calls.append((copy.deepcopy(messages), tools))
        return self.replies[len(self.calls) - 1]


def test_decorator_returns_function_unchanged():
    reg = ToolRegistry()

    def add(a: int, b: int) -> int:
        return a + b

    assert reg.tool(add) is add, "the decorator should return the original function"
    assert add(2, 3) == 5


def test_schema_from_signature_and_docstring():
    got = make_registry().schemas()[0]
    expected = {
        "name": "get_weather",
        "description": "Get the weather forecast for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}, "days": {"type": "integer"}},
            "required": ["city"],
        },
    }
    assert got == expected, f"got {got!r}"


def test_schemas_all_types_order_and_missing_docstring():
    schemas = make_registry().schemas()
    assert [s["name"] for s in schemas] == ["get_weather", "divide", "shout"]
    assert schemas[1]["description"] == "Divide a by b."
    shout = schemas[2]
    assert shout["description"] == "", f"got {shout['description']!r}"
    assert shout["parameters"]["properties"] == {
        "text": {"type": "string"}, "loud": {"type": "boolean"},
        "tags": {"type": "array"}, "meta": {"type": "object"}}, f"got {shout!r}"
    assert schemas[1]["parameters"]["properties"]["a"] == {"type": "number"}


def test_bad_tools_are_rejected():
    reg = ToolRegistry()

    @reg.tool
    def ping() -> str:
        return "pong"

    def ping2() -> str:
        return "pong"
    ping2.__name__ = "ping"
    for bad, exc_type in [(ping2, ValueError)]:
        try:
            reg.tool(bad)
        except exc_type:
            pass
        else:
            raise AssertionError("duplicate tool name should raise ValueError")

    def no_hint(x):
        return x

    def star(*items: str):
        return items

    for bad in (no_hint, star):
        try:
            reg.tool(bad)
        except TypeError:
            continue
        raise AssertionError(f"{bad.__name__} should be rejected with TypeError")


def test_dispatch_calls_tool_and_serialises_result():
    reg = make_registry()
    got = reg.dispatch({"id": "c1", "name": "get_weather", "arguments": '{"city": "Paris", "days": 2}'})
    assert isinstance(got, str), f"dispatch should return a string, got {type(got).__name__}"
    assert json.loads(got) == {"city": "Paris", "days": 2, "sky": "sunny"}
    got = reg.dispatch({"id": "c2", "name": "shout", "arguments": '{"text": "hi"}'})
    assert got == "HI", f"string results should be returned as is, got {got!r}"
    got = reg.dispatch({"id": "c3", "name": "divide", "arguments": '{"a": 1, "b": 4}'})
    assert json.loads(got) == 0.25


def test_dispatch_unknown_tool_and_bad_json():
    reg = make_registry()
    for call in [
        {"id": "x", "name": "launch_rockets", "arguments": "{}"},
        {"id": "x", "name": "get_weather", "arguments": "{city: Paris}"},
        {"id": "x", "name": "get_weather", "arguments": '["Paris"]'},
    ]:
        got = reg.dispatch(call)
        assert isinstance(got, str) and got.startswith("Error: "), f"{call!r} -> {got!r}"


def test_dispatch_argument_validation():
    reg = make_registry()
    bad_args = [
        "{}",                                   # missing city
        '{"city": "Paris", "units": "C"}',      # unknown argument
        '{"city": 42}',                         # wrong type
        '{"city": "Paris", "days": true}',      # bool is not an int
        '{"city": "Paris", "days": 1.5}',       # float is not an int
    ]
    for args in bad_args:
        got = reg.dispatch({"id": "x", "name": "get_weather", "arguments": args})
        assert isinstance(got, str) and got.startswith("Error: "), f"arguments {args} -> {got!r}"


def test_dispatch_reports_tool_exceptions():
    reg = make_registry()
    got = reg.dispatch({"id": "x", "name": "divide", "arguments": '{"a": 1, "b": 0}'})
    assert got.startswith("Error: ") and "ZeroDivisionError" in got, f"got {got!r}"


def test_agent_returns_final_answer_directly():
    llm = ScriptedLLM([{"type": "final", "content": "Hello!"}])
    reg = make_registry()
    assert run_agent(llm, reg, "hi") == "Hello!"
    messages, tools = llm.calls[0]
    assert messages == [{"role": "user", "content": "hi"}], f"messages: {messages!r}"
    assert tools == reg.schemas(), "llm should receive registry.schemas() as tools"


def test_agent_runs_tools_and_appends_messages():
    calls = [{"id": "c1", "name": "get_weather", "arguments": '{"city": "Oslo"}'},
             {"id": "c2", "name": "nope", "arguments": "{}"}]
    llm = ScriptedLLM([{"type": "tool_calls", "calls": calls},
                       {"type": "final", "content": "Sunny in Oslo."}])
    got = run_agent(llm, make_registry(), "weather in Oslo?", system="Be brief.")
    assert got == "Sunny in Oslo."
    messages = llm.calls[1][0]
    assert len(messages) == 5, f"expected 5 messages on step 2, got {len(messages)}: {messages!r}"
    assert messages[0] == {"role": "system", "content": "Be brief."}
    assert messages[1] == {"role": "user", "content": "weather in Oslo?"}
    assert messages[2] == {"role": "assistant", "tool_calls": calls}
    tool1, tool2 = messages[3], messages[4]
    assert tool1["role"] == "tool" and tool1["tool_call_id"] == "c1" and tool1["name"] == "get_weather"
    assert json.loads(tool1["content"])["city"] == "Oslo", f"tool message: {tool1!r}"
    assert tool2["tool_call_id"] == "c2" and tool2["content"].startswith("Error: "), f"got {tool2!r}"


def test_agent_multi_step():
    llm = ScriptedLLM([
        {"type": "tool_calls", "calls": [{"id": "a", "name": "divide", "arguments": '{"a": 9, "b": 3}'}]},
        {"type": "tool_calls", "calls": [{"id": "b", "name": "divide", "arguments": '{"a": 3, "b": 3}'}]},
        {"type": "final", "content": "done"},
    ])
    assert run_agent(llm, make_registry(), "compute") == "done"
    assert len(llm.calls) == 3
    assert len(llm.calls[2][0]) == 5, "each step should add an assistant and a tool message"


def test_agent_stops_at_max_steps():
    loop = {"type": "tool_calls", "calls": [{"id": "c", "name": "shout", "arguments": '{"text": "a"}'}]}
    llm = ScriptedLLM([loop] * 10)
    try:
        run_agent(llm, make_registry(), "go", max_steps=3)
    except AgentLoopError as exc:
        assert isinstance(exc, RuntimeError)
        assert "3" in str(exc), f"message should mention the limit: {exc}"
    else:
        raise AssertionError("expected AgentLoopError")
    assert len(llm.calls) == 3, f"llm called {len(llm.calls)} times, expected 3"


def test_agent_rejects_unknown_reply_type():
    llm = ScriptedLLM([{"type": "banana"}])
    try:
        run_agent(llm, make_registry(), "go")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown reply type should raise ValueError")
''',
}
