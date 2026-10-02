TOPIC = {
    "id": "tool-calling",
    "title": "Tool Calling",
    "track": "llm-apps",
    "order": 4,
    "requires": ["structured-output"],
    "summary": """
        Letting a model use your Python functions: describing tools with JSON schema, reading
        tool calls (Anthropic and OpenAI shapes), dispatching and validating them, and sending
        the results back - one full request, tool, answer round with a fake model.
    """,
    "concepts": ["tool definition", "input_schema", "tool_use block", "stop_reason",
                 "OpenAI tool_calls", "JSON arguments", "tool registry", "dispatch",
                 "argument validation", "tool_result", "is_error", "tool loop"],
}

LESSON = r'''
## Tool calling in one picture

A model can only write text. **Tool calling** lets it *ask you* to run a function.
You describe your tools; the model answers "please call `get_weather` with
`{"city": "Paris"}`"; **your code** runs the function and sends the result back; the model
then writes the final answer. The model never runs anything itself.

## Describing a tool (Anthropic shape)

```python
tool = {"name": "get_weather",
        "description": "Current weather for a city.",
        "input_schema": {"type": "object",
                         "properties": {"city": {"type": "string", "description": "City name"}},
                         "required": ["city"]}}
print(tool["input_schema"]["required"])
```
OpenAI wraps the same thing: `{"type": "function", "function": {"name", "description", "parameters": <schema>}}`.

## Reading a tool call

| | Anthropic | OpenAI (chat completions) |
| --- | --- | --- |
| "I want a tool" | `stop_reason == "tool_use"` | `finish_reason == "tool_calls"` |
| where | `content` blocks with `type == "tool_use"` | `message["tool_calls"]` |
| args | `block["input"]` (a dict) | `call["function"]["arguments"]` (a JSON **string** - `json.loads` it) |
| id | `block["id"]` (`"toolu_..."`) | `call["id"]` (`"call_..."`) |

## Dispatching

Keep a **registry**: `{"get_weather": get_weather, ...}`. Look up the name, then call it
with the arguments unpacked: `tools[name](**args)`. Check the name exists and the
arguments match the schema **before** calling - the model can make mistakes.

## Sending results back

- Anthropic: a `user` message whose content is a list of
  `{"type": "tool_result", "tool_use_id": id, "content": "..."}` blocks
  (add `"is_error": True` when the tool failed).
- OpenAI: one `{"role": "tool", "tool_call_id": id, "content": "..."}` message per call.
- Content is text: `json.dumps` dicts/lists before sending.

## The loop

1. Send messages + tools. 2. If the model asks for tools: append its reply as an
`assistant` message, run every call, append the results. 3. Repeat until it stops asking,
then read the text. Always cap the number of rounds.

## Gotchas

- OpenAI arguments are a string, not a dict.
- Every tool call id must get exactly one result.
- Errors go back to the model as results (it can fix its call); don't crash the app.
- `True` is an `int` in Python: check `bool` before `int` when validating types.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "tool-calling-s1",
        "title": "Read a tool call",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The model asks, you act

            Think of the model as a manager who can't leave the office. It can't check
            the weather itself, but it can write you a note: *"please run `get_weather`
            with city = Paris"*. You do the errand and report back.

            With the Anthropic API that note arrives inside the reply's `content` list as a
            block with `"type": "tool_use"`, and the reply's `stop_reason` is `"tool_use"`:

            ```python
            reply = {
                "stop_reason": "tool_use",
                "content": [
                    {"type": "text", "text": "Let me check."},
                    {"type": "tool_use", "id": "toolu_01", "name": "get_weather",
                     "input": {"city": "Paris"}},
                ],
            }
            print(reply["content"][1]["name"])
            ```

            The proper name for this is a **tool call** (or *function call*). The block
            gives you three things: the tool's `name`, its arguments in `input` (already a
            dict), and an `id` you will need when you send the answer back.

            Watch out: the model never runs the function. Your code does.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            reply = {
                "stop_reason": "tool_use",
                "content": [
                    {"type": "text", "text": "Checking."},
                    {"type": "tool_use", "id": "toolu_7", "name": "get_weather",
                     "input": {"city": "Oslo", "unit": "celsius"}},
                ],
            }
            block = reply["content"][1]
            print(reply["stop_reason"])
            print(block["name"])
            print(block["input"]["city"])
            print(len(block["input"]))
        ''',
        "solution": r'''
            tool_use
            get_weather
            Oslo
            2
        ''',
        "explanation": r'''
            `stop_reason` says why the model stopped: it wants a tool. The second content
            block is the `tool_use` block: its `name` is `get_weather`, its `input` dict has
            `city` = `Oslo`, and that dict has 2 keys.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`block` is the second item of the content list (index 1).",
            "Each print reads one key: the reply's stop_reason, then the block's name, then a key inside input, then the size of input.",
            "Line 1: the stop_reason string. Line 2: the tool name. Line 3: the city value. Line 4: how many keys the input dict has.",
        ],
    },
    {
        "id": "tool-calling-s2",
        "title": "Describe a tool",
        "difficulty": 0,
        "lesson": r'''
            ## A tool is a menu item

            Before the model can ask for a tool, it must know the tool exists. You give it
            a menu: each item has a **name**, a **description** (when to use it) and the
            **ingredients** it needs (the arguments).

            The ingredients are described with **JSON schema**, the same idea as in the
            structured-output chapter: an object with `properties` and a `required` list.

            ```python
            tool = {
                "name": "search_docs",
                "description": "Search the help center.",
                "input_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            }
            print(tool["name"], tool["input_schema"]["required"])
            ```

            This dict is called a **tool definition**. Anthropic calls the schema part
            `input_schema`. You send a list of these with every request.

            Watch out: the description matters. The model decides *when* to call a tool
            mostly from its description.
        ''',
        "prompt": r'''
            Every tool starts from the same skeleton. Complete the function by replacing the `___`.

            **Write:** `make_tool(name, description)`

            - `name`: a string, e.g. `"get_time"`
            - `description`: a string, e.g. `"Current time."`
            - **Returns:** an Anthropic-style tool definition dict with no arguments:
              `{"name": name, "description": description, "input_schema": {"type": "object", "properties": {}, "required": []}}`

            **Rules**
            - Exactly the three keys `name`, `description`, `input_schema`.
            - Each call returns a new dict (two tools must not share the same `properties` dict).

            **Examples**
            ```python
            make_tool("get_time", "Current time.")
            # returns {"name": "get_time", "description": "Current time.",
            #          "input_schema": {"type": "object", "properties": {}, "required": []}}
            ```
        ''',
        "starter": r'''
            def make_tool(name, description):
                return {
                    "name": name,
                    "description": ___,
                    "input_schema": {"type": "object", "properties": {}, "required": []},
                }
        ''',
        "tests": r'''
            from solution import make_tool

            def test_builds_full_definition():
                got = make_tool("get_time", "Current time.")
                want = {"name": "get_time", "description": "Current time.",
                        "input_schema": {"type": "object", "properties": {}, "required": []}}
                assert got == want, f"got {got!r}"

            def test_uses_the_given_description():
                got = make_tool("ping", "Check the server.")
                assert got["description"] == "Check the server.", f"got {got!r}"

            def test_tools_do_not_share_properties():
                a = make_tool("a", "A")
                b = make_tool("b", "B")
                a["input_schema"]["properties"]["x"] = {"type": "string"}
                assert b["input_schema"]["properties"] == {}, "the two tools share one properties dict"
        ''',
        "solution": r'''
            def make_tool(name, description):
                return {
                    "name": name,
                    "description": description,
                    "input_schema": {"type": "object", "properties": {}, "required": []},
                }
        ''',
        "hints": [
            "Only one value is missing, and it arrives as a parameter.",
            "The `description` key should hold whatever the caller passed in.",
            "Replace ___ with the parameter named description (no quotes).",
        ],
    },
    {
        "id": "tool-calling-s3",
        "title": "Fix: does it want a tool?",
        "difficulty": 0,
        "lesson": r'''
            ## Why did the model stop?

            A waiter who walks back to the kitchen either has a finished order or a
            question for the chef. You check which one before doing anything.

            Every Anthropic reply has a `stop_reason` that says why the model stopped
            writing:

            ```python
            for reason in ["end_turn", "tool_use", "max_tokens"]:
                reply = {"stop_reason": reason}
                print(reason, reply["stop_reason"] == "tool_use")
            ```

            - `"end_turn"`: the answer is finished.
            - `"tool_use"`: it wants you to run one or more tools.
            - `"max_tokens"`: it ran out of room.

            OpenAI has the same idea with a different name and value: `finish_reason`
            is `"tool_calls"`. Each provider has its own spelling, so mixing them up is a
            classic bug.
        ''',
        "prompt": r'''
            The app must know when an Anthropic-style reply asks for a tool. The function
            below always returns `False`. Fix the bug.

            **Write:** `wants_tool(reply)`

            - `reply`: a dict with a `"stop_reason"` key, e.g. `{"stop_reason": "tool_use", "content": [...]}`
            - **Returns:** `True` if `stop_reason` is `"tool_use"`, otherwise `False`

            **Examples**
            ```python
            wants_tool({"stop_reason": "tool_use", "content": []})   # returns True
            wants_tool({"stop_reason": "end_turn", "content": []})   # returns False
            ```
        ''',
        "starter": r'''
            def wants_tool(reply):
                return reply["stop_reason"] == "tool_calls"
        ''',
        "tests": r'''
            from solution import wants_tool

            def test_tool_use_is_true():
                got = wants_tool({"stop_reason": "tool_use", "content": []})
                assert got is True, f"got {got!r}"

            def test_end_turn_is_false():
                got = wants_tool({"stop_reason": "end_turn", "content": []})
                assert got is False, f"got {got!r}"

            def test_max_tokens_is_false():
                got = wants_tool({"stop_reason": "max_tokens", "content": []})
                assert got is False, f"got {got!r}"
        ''',
        "solution": r'''
            def wants_tool(reply):
                return reply["stop_reason"] == "tool_use"
        ''',
        "hints": [
            "Compare the string in the starter with the one in the prompt.",
            "The starter uses the OpenAI spelling. Anthropic's stop_reason value is different.",
            "Change the compared string to exactly tool_use.",
        ],
    },
    {
        "id": "tool-calling-s4",
        "title": "Find the tool calls",
        "difficulty": 0,
        "lesson": r'''
            ## Sorting the mail

            A reply's `content` is like a pile of mail: some letters are plain text, some
            are tool requests. The model can ask for **several tools in one reply**, so
            you sort the pile and keep every tool request.

            ```python
            content = [
                {"type": "text", "text": "One moment."},
                {"type": "tool_use", "id": "t1", "name": "add", "input": {"a": 1, "b": 2}},
            ]
            for block in content:
                print(block["type"])
            ```

            You already know the pattern from loops: start an empty list, loop, `if`
            the block's `type` is what you want, `.append` it. (A list comprehension
            with an `if` works too.)

            These pieces are called **content blocks**. Every block has a `type` key,
            so that is what you check.
        ''',
        "prompt": r'''
            Pull out every tool request from an Anthropic-style reply.

            **Write:** `find_tool_calls(reply)`

            - `reply`: a dict whose `"content"` is a list of blocks; each block is a dict with a `"type"` key
            - **Returns:** a list of the blocks whose `type` is `"tool_use"`, in their original order

            **Rules**
            - Return the block dicts themselves (not just names).
            - If there are none, return `[]`.

            **Examples**
            ```python
            reply = {"content": [
                {"type": "text", "text": "Hi"},
                {"type": "tool_use", "id": "t1", "name": "add", "input": {}},
            ]}
            find_tool_calls(reply)   # returns [{"type": "tool_use", "id": "t1", "name": "add", "input": {}}]
            find_tool_calls({"content": [{"type": "text", "text": "Done"}]})   # returns []
            ```
        ''',
        "starter": r'''
            def find_tool_calls(reply):
                ...
        ''',
        "tests": r'''
            from solution import find_tool_calls

            A = {"type": "tool_use", "id": "t1", "name": "add", "input": {"a": 1}}
            B = {"type": "tool_use", "id": "t2", "name": "mul", "input": {"a": 2}}
            T = {"type": "text", "text": "hi"}

            def test_keeps_only_tool_use_blocks():
                got = find_tool_calls({"content": [T, A]})
                assert got == [A], f"got {got!r}"

            def test_keeps_several_in_order():
                got = find_tool_calls({"content": [A, T, B]})
                assert got == [A, B], f"got {got!r}"

            def test_no_tool_calls_gives_empty_list():
                got = find_tool_calls({"content": [T]})
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def find_tool_calls(reply):
                return [block for block in reply["content"] if block["type"] == "tool_use"]
        ''',
        "hints": [
            "Loop over reply[\"content\"] and look at each block's type.",
            "Keep a block only when its type equals \"tool_use\".",
            "Start with an empty list, loop over the content blocks, append those whose type is tool_use, return the list.",
        ],
    },
    {
        "id": "tool-calling-s5",
        "title": "Call a tool by name",
        "difficulty": 0,
        "lesson": r'''
            ## The switchboard

            The model hands you a **name** (a string) and **arguments** (a dict). You need
            to turn that into a real function call. A dict makes a perfect switchboard:
            the name is the key, the function is the value.

            ```python
            def add(a, b):
                return a + b

            tools = {"add": add}
            args = {"a": 2, "b": 3}
            func = tools["add"]
            print(func(**args))
            ```

            `**args` **unpacks** the dict into keyword arguments: `func(**{"a": 2, "b": 3})`
            is the same as `func(a=2, b=3)`. You saw `**kwargs` in the functions chapter;
            this is the same stars used on the calling side.

            The dict of tools is called a **tool registry**, and looking up and calling
            the right function is called **dispatching**.

            Watch out: `func(args)` passes the whole dict as ONE positional argument.
        ''',
        "prompt": r'''
            Run the tool the model asked for. Complete the function by replacing the `___`.

            **Write:** `run_tool(tools, name, args)`

            - `tools`: a dict mapping tool names to Python functions, e.g. `{"add": add}`
            - `name`: the tool name the model asked for, e.g. `"add"`
            - `args`: a dict of keyword arguments, e.g. `{"a": 2, "b": 3}`
            - **Returns:** whatever the tool function returns

            **Rules**
            - Pass the arguments as keyword arguments (unpack `args`).
            - You can assume `name` is in `tools` for this step.

            **Examples**
            ```python
            def add(a, b):
                return a + b
            run_tool({"add": add}, "add", {"a": 2, "b": 3})   # returns 5
            ```
        ''',
        "starter": r'''
            def run_tool(tools, name, args):
                func = tools[name]
                return func(___)
        ''',
        "tests": r'''
            from solution import run_tool

            def add(a, b):
                return a + b

            def greet(name, punct="!"):
                return "Hi " + name + punct

            def test_calls_add_with_keywords():
                got = run_tool({"add": add, "greet": greet}, "add", {"a": 2, "b": 3})
                assert got == 5, f"got {got!r}"

            def test_picks_the_named_tool():
                got = run_tool({"add": add, "greet": greet}, "greet", {"name": "Ada"})
                assert got == "Hi Ada!", f"got {got!r}"

            def test_arguments_go_by_name_not_position():
                got = run_tool({"greet": greet}, "greet", {"punct": "?", "name": "Bo"})
                assert got == "Hi Bo?", f"got {got!r}"
        ''',
        "solution": r'''
            def run_tool(tools, name, args):
                func = tools[name]
                return func(**args)
        ''',
        "hints": [
            "The arguments are in a dict, but the function wants separate named arguments.",
            "Two stars in front of a dict in a call spread it out as keyword arguments.",
            "Replace ___ with args preceded by two asterisks.",
        ],
    },
    {
        "id": "tool-calling-s6",
        "title": "OpenAI arguments are text",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Same letter, different envelope

            OpenAI delivers the same "please run this" note in a different envelope. The
            reply's message has a `tool_calls` list, and each call looks like:

            ```python
            import json

            call = {"id": "call_1", "type": "function",
                    "function": {"name": "add", "arguments": "{\"a\": 2, \"b\": 3}"}}
            raw = call["function"]["arguments"]
            print(type(raw).__name__)
            print(json.loads(raw)["a"])
            ```

            The big difference: `arguments` is a **JSON string**, not a dict. You have to
            parse it with `json.loads` (the JSON chapter) before you can use it. Anthropic's
            `input` is already a dict.

            When OpenAI wants tools, the choice's `finish_reason` is `"tool_calls"`.

            Watch out: the model writes that string, so it can be broken JSON. Real code
            catches `json.JSONDecodeError`.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            import json

            call = {"id": "call_9", "type": "function",
                    "function": {"name": "search", "arguments": "{\"query\": \"refunds\", \"k\": 3}"}}
            raw = call["function"]["arguments"]
            args = json.loads(raw)
            print(type(raw).__name__, type(args).__name__)
            print(call["function"]["name"], args["query"])
            print(args["k"] + 1)
        ''',
        "solution": r'''
            str dict
            search refunds
            4
        ''',
        "explanation": r'''
            `arguments` is a string of JSON text (`str`). `json.loads` turns it into a real
            `dict`. From the dict, `query` is `"refunds"` and `k` is the number `3`, so
            `k + 1` is `4`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`raw` is the value stored under arguments. Look at whether it has quotes around it.",
            "json.loads turns JSON text into Python objects; numbers become ints.",
            "Line 1: the type names of raw and args. Line 2: the tool name and the query. Line 3: k plus one.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "tool-calling-1",
        "title": "Parse an OpenAI tool call",
        "difficulty": 1,
        "lesson": r'''
            ## Unwrapping the envelope

            Remember the OpenAI envelope? The name is two levels deep and the arguments
            are JSON text. Most apps unwrap each call once, right away, into the three
            things they need: **id**, **name**, **arguments dict**.

            ```python
            import json

            call = {"id": "call_1", "type": "function",
                    "function": {"name": "ping", "arguments": "{}"}}
            fn = call["function"]
            print(call["id"], fn["name"], json.loads(fn["arguments"]))
            ```

            Returning several values from one function gives a **tuple**
            (`return a, b, c`), which the caller unpacks: `call_id, name, args = ...`.

            Watch out for empty arguments. A tool with no parameters may get `"{}"` or even
            an empty string `""`. `json.loads("")` raises an error, so treat an empty or
            whitespace-only string as "no arguments".
        ''',
        "prompt": r'''
            Turn one OpenAI-style tool call into plain values.

            **Write:** `parse_openai_call(call)`

            - `call`: a dict like `{"id": "call_1", "type": "function", "function": {"name": "add", "arguments": "{\"a\": 1}"}}`
            - **Returns:** a tuple `(call_id, name, args)`: the id string, the tool name string,
              and the arguments parsed into a dict

            **Rules**
            - `arguments` is JSON text; parse it with `json.loads`.
            - If `arguments` is an empty string or only whitespace, `args` is `{}`.
            - Don't change `call`.

            **Examples**
            ```python
            parse_openai_call({"id": "call_1", "type": "function",
                               "function": {"name": "add", "arguments": "{\"a\": 1, \"b\": 2}"}})
            # returns ("call_1", "add", {"a": 1, "b": 2})
            parse_openai_call({"id": "call_2", "type": "function",
                               "function": {"name": "now", "arguments": ""}})
            # returns ("call_2", "now", {})
            ```
        ''',
        "starter": r'''
            import json

            def parse_openai_call(call):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import parse_openai_call

            def make(cid, name, arguments):
                return {"id": cid, "type": "function", "function": {"name": name, "arguments": arguments}}

            def test_parses_id_name_and_args():
                got = parse_openai_call(make("call_1", "add", "{\"a\": 1, \"b\": 2}"))
                assert tuple(got) == ("call_1", "add", {"a": 1, "b": 2}), f"got {got!r}"

            def test_args_is_a_dict_not_a_string():
                _, _, args = parse_openai_call(make("c", "search", "{\"query\": \"x\"}"))
                assert isinstance(args, dict), f"args is a {type(args).__name__}"

            def test_empty_arguments_give_empty_dict():
                got = parse_openai_call(make("call_2", "now", ""))
                assert tuple(got) == ("call_2", "now", {}), f"got {got!r}"

            def test_whitespace_arguments_give_empty_dict():
                got = parse_openai_call(make("call_3", "now", "   "))
                assert tuple(got) == ("call_3", "now", {}), f"got {got!r}"

            def test_does_not_change_input():
                call = make("c", "add", "{\"a\": 1}")
                before = copy.deepcopy(call)
                parse_openai_call(call)
                assert call == before, "the call dict was changed"
        ''',
        "solution": r'''
            import json

            def parse_openai_call(call):
                fn = call["function"]
                raw = fn["arguments"]
                args = json.loads(raw) if raw.strip() else {}
                return call["id"], fn["name"], args
        ''',
        "hints": [
            "The name and the arguments live inside call[\"function\"]; the id is at the top level.",
            "Parse the arguments with json.loads, but only if the string has something other than spaces in it.",
            "Get fn = call[\"function\"]; if fn[\"arguments\"].strip() is empty use {}, else json.loads it; return the id, fn[\"name\"] and the dict as a tuple.",
        ],
    },
    {
        "id": "tool-calling-2",
        "title": "Build a tool schema",
        "difficulty": 1,
        "lesson": r'''
            ## Filling in the order form

            A tool with no ingredients is rare. Most tools need arguments, and each
            argument gets a line in the order form: its **type** and a short
            **description** so the model knows what to put there.

            ```python
            properties = {}
            params = {"city": ("string", "City name"), "days": ("integer", "1 to 7")}
            for name, (kind, text) in params.items():
                properties[name] = {"type": kind, "description": text}
            print(properties["days"])
            print(list(params))
            ```

            JSON schema type names are not Python names: `"string"`, `"integer"`,
            `"number"`, `"boolean"`, `"array"`, `"object"`.

            The `required` list names the arguments the model **must** provide. Its
            order doesn't matter to the model, but keeping the same order as the
            properties makes your definitions easy to read and to test.
        ''',
        "prompt": r'''
            Write a helper that builds a full Anthropic-style tool definition from a compact
            description of its parameters.

            **Write:** `tool_schema(name, description, params)`

            - `name`: a string, e.g. `"get_weather"`
            - `description`: a string
            - `params`: a dict mapping parameter name to a tuple `(json_type, param_description)`,
              e.g. `{"city": ("string", "City name")}`
            - **Returns:** a dict:
              `{"name": ..., "description": ..., "input_schema": {"type": "object", "properties": {...}, "required": [...]}}`

            **Rules**
            - Each property is `{"type": json_type, "description": param_description}`.
            - Every parameter is required; `required` lists the names in the same order as `params`.
            - With no parameters: `"properties": {}` and `"required": []`.

            **Examples**
            ```python
            tool_schema("get_weather", "Weather for a city.",
                        {"city": ("string", "City name"), "days": ("integer", "1 to 7")})
            # returns {"name": "get_weather", "description": "Weather for a city.",
            #          "input_schema": {"type": "object",
            #              "properties": {"city": {"type": "string", "description": "City name"},
            #                             "days": {"type": "integer", "description": "1 to 7"}},
            #              "required": ["city", "days"]}}
            tool_schema("now", "Current time.", {})["input_schema"]["required"]   # returns []
            ```
        ''',
        "starter": r'''
            def tool_schema(name, description, params):
                ...
        ''',
        "tests": r'''
            from solution import tool_schema

            def test_full_definition_for_two_params():
                got = tool_schema("get_weather", "Weather for a city.",
                                  {"city": ("string", "City name"), "days": ("integer", "1 to 7")})
                want = {"name": "get_weather", "description": "Weather for a city.",
                        "input_schema": {"type": "object",
                                         "properties": {"city": {"type": "string", "description": "City name"},
                                                        "days": {"type": "integer", "description": "1 to 7"}},
                                         "required": ["city", "days"]}}
                assert got == want, f"got {got!r}"

            def test_required_keeps_param_order():
                got = tool_schema("t", "d", {"z": ("string", "z"), "a": ("number", "a")})
                assert got["input_schema"]["required"] == ["z", "a"], f"got {got['input_schema']['required']!r}"

            def test_no_params():
                got = tool_schema("now", "Current time.", {})
                assert got["input_schema"] == {"type": "object", "properties": {}, "required": []}, f"got {got!r}"
        ''',
        "solution": r'''
            def tool_schema(name, description, params):
                properties = {}
                required = []
                for pname, (json_type, text) in params.items():
                    properties[pname] = {"type": json_type, "description": text}
                    required.append(pname)
                return {
                    "name": name,
                    "description": description,
                    "input_schema": {"type": "object", "properties": properties, "required": required},
                }
        ''',
        "hints": [
            "Loop over params.items(); each value is a (type, description) tuple you can unpack.",
            "Build the properties dict and the required list in the same loop, then place them in the result.",
            "Start properties = {} and required = []; for each name and (type, text) add properties[name] = {...} and append name; return the outer dict with input_schema holding both.",
        ],
    },
    {
        "id": "tool-calling-3",
        "title": "Check the arguments",
        "difficulty": 1,
        "lesson": r'''
            ## Check the order before cooking

            A good cook reads the order before starting. Models make mistakes: they
            forget an argument, or invent one that doesn't exist. Calling your function
            with bad arguments raises a `TypeError` deep inside your app. Better to check
            first and give a clear message.

            ```python
            schema = {"type": "object",
                      "properties": {"city": {"type": "string"}, "days": {"type": "integer"}},
                      "required": ["city"]}
            args = {"cty": "Paris"}
            print([n for n in schema["required"] if n not in args])
            print([n for n in args if n not in schema["properties"]])
            ```

            Two checks catch most mistakes:
            - **missing**: a name in `required` that is not in the arguments;
            - **unknown**: an argument name that is not in `properties`.

            This is called **argument validation**. The error messages go back to the
            model, which usually fixes its call on the next try.
        ''',
        "prompt": r'''
            Validate a tool call's arguments against the tool's `input_schema` before running it.

            **Write:** `check_args(schema, args)`

            - `schema`: an `input_schema` dict with `"properties"` (dict) and `"required"` (list)
            - `args`: the arguments dict the model sent
            - **Returns:** a list of error strings (empty list if everything is fine)

            **Rules**
            - For each name in `required` (in that order) that is missing from `args`: add `"missing: <name>"`.
            - Then, for each key in `args` (in its order) that is not in `properties`: add `"unknown: <name>"`.
            - All missing errors come before all unknown errors.
            - Types are not checked here.

            **Examples**
            ```python
            schema = {"type": "object",
                      "properties": {"city": {"type": "string"}, "days": {"type": "integer"}},
                      "required": ["city"]}
            check_args(schema, {"city": "Paris"})          # returns []
            check_args(schema, {"cty": "Paris"})           # returns ["missing: city", "unknown: cty"]
            check_args(schema, {"city": "Rome", "days": 2})   # returns []
            ```
        ''',
        "starter": r'''
            def check_args(schema, args):
                ...
        ''',
        "tests": r'''
            from solution import check_args

            SCHEMA = {"type": "object",
                      "properties": {"city": {"type": "string"}, "days": {"type": "integer"},
                                     "unit": {"type": "string"}},
                      "required": ["city", "days"]}

            def test_valid_args_give_no_errors():
                got = check_args(SCHEMA, {"city": "Rome", "days": 2})
                assert got == [], f"got {got!r}"

            def test_optional_argument_can_be_left_out_or_given():
                got = check_args(SCHEMA, {"city": "Rome", "days": 2, "unit": "c"})
                assert got == [], f"got {got!r}"

            def test_missing_in_required_order():
                got = check_args(SCHEMA, {})
                assert got == ["missing: city", "missing: days"], f"got {got!r}"

            def test_missing_before_unknown():
                got = check_args(SCHEMA, {"cty": "Paris", "days": 1, "zz": 0})
                assert got == ["missing: city", "unknown: cty", "unknown: zz"], f"got {got!r}"
        ''',
        "solution": r'''
            def check_args(schema, args):
                errors = []
                for name in schema["required"]:
                    if name not in args:
                        errors.append(f"missing: {name}")
                for name in args:
                    if name not in schema["properties"]:
                        errors.append(f"unknown: {name}")
                return errors
        ''',
        "hints": [
            "Two separate loops: one over schema[\"required\"], one over the keys of args.",
            "Use `in` / `not in` to test whether a name is a key of a dict.",
            "Start errors = []; loop required names, append \"missing: \" + name when absent from args; then loop args, append \"unknown: \" + name when not in properties; return errors.",
        ],
    },
    {
        "id": "tool-calling-4",
        "title": "Anthropic tool result",
        "difficulty": 1,
        "research": {
            "note": "Read how a tool result is sent back to Claude (the `tool_result` block, `tool_use_id`, "
                    "`content` and `is_error`), then come back.",
            "links": [{"title": "Tool use with Claude - Anthropic docs",
                       "url": "https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview"}],
        },
        "lesson": r'''
            ## Reporting back

            You ran the errand; now report back, and say **which** errand the report is
            for. Each `tool_use` block had an `id`. Your answer quotes it as
            `tool_use_id`, like writing the order number on a receipt.

            With Anthropic the report is a `user` message whose content is a list of
            `tool_result` blocks:

            ```python
            import json

            output = {"temp": 21}
            block = {"type": "tool_result", "tool_use_id": "toolu_01",
                     "content": json.dumps(output)}
            message = {"role": "user", "content": [block]}
            print(message)
            ```

            The result content should be **text**. A dict or list is turned into JSON
            text with `json.dumps`; a string is sent as it is.

            Watch out: `str({"temp": 21})` gives Python's `{'temp': 21}` with single
            quotes - that isn't JSON. Use `json.dumps`.
        ''',
        "prompt": r'''
            Build the message that returns one tool's output to an Anthropic model.

            **Write:** `tool_result_message(tool_use_id, output)`

            - `tool_use_id`: the id from the `tool_use` block, e.g. `"toolu_01"`
            - `output`: what the tool returned: a string, or any JSON-serialisable value (dict, list, number...)
            - **Returns:** `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": text}]}`

            **Rules**
            - If `output` is a string, `text` is that string unchanged.
            - Otherwise `text` is `json.dumps(output)` (default options).
            - Do not add an `is_error` key.

            **Examples**
            ```python
            tool_result_message("toolu_01", "21C and sunny")
            # returns {"role": "user", "content": [{"type": "tool_result",
            #          "tool_use_id": "toolu_01", "content": "21C and sunny"}]}
            tool_result_message("toolu_02", {"temp": 21})
            # content text is '{"temp": 21}'
            tool_result_message("toolu_03", 42)
            # content text is '42'
            ```
        ''',
        "starter": r'''
            import json

            def tool_result_message(tool_use_id, output):
                ...
        ''',
        "tests": r'''
            import json
            from solution import tool_result_message

            def test_string_output_is_sent_unchanged():
                got = tool_result_message("toolu_01", "21C and sunny")
                want = {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_01",
                                                     "content": "21C and sunny"}]}
                assert got == want, f"got {got!r}"

            def test_dict_output_becomes_json_text():
                got = tool_result_message("toolu_02", {"temp": 21, "sky": "clear"})
                text = got["content"][0]["content"]
                assert text == json.dumps({"temp": 21, "sky": "clear"}), f"content was {text!r}"

            def test_number_output_becomes_text():
                got = tool_result_message("toolu_03", 42)
                assert got["content"][0]["content"] == "42", f"got {got!r}"

            def test_no_is_error_key():
                got = tool_result_message("toolu_04", "ok")
                assert "is_error" not in got["content"][0], f"got {got!r}"
        ''',
        "solution": r'''
            import json

            def tool_result_message(tool_use_id, output):
                text = output if isinstance(output, str) else json.dumps(output)
                block = {"type": "tool_result", "tool_use_id": tool_use_id, "content": text}
                return {"role": "user", "content": [block]}
        ''',
        "hints": [
            "Two jobs: turn the output into text, then wrap it in the block and the message.",
            "isinstance(output, str) tells you whether to leave it alone or to call json.dumps.",
            "Compute text (the string itself, or json.dumps(output)); build the tool_result block with type, tool_use_id and content; return a user message whose content is a list holding that block.",
        ],
    },
    {
        "id": "tool-calling-5",
        "title": "OpenAI tool messages",
        "difficulty": 1,
        "research": {
            "note": "Read how OpenAI's function calling returns results: the `tool` role message and "
                    "its `tool_call_id`. Compare it with Anthropic's `tool_result` block.",
            "links": [{"title": "Function calling - OpenAI docs",
                       "url": "https://platform.openai.com/docs/guides/function-calling"}],
        },
        "lesson": r'''
            ## One receipt per errand

            OpenAI does the reporting differently. Instead of one `user` message holding
            a list of results, you add **one message per call**, with the special role
            `"tool"`:

            ```python
            calls = [{"id": "call_a"}, {"id": "call_b"}]
            outputs = ["sunny", "rainy"]
            messages = []
            for call, out in zip(calls, outputs):
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": out})
            print(len(messages), messages[1]["tool_call_id"])
            ```

            The key is `tool_call_id` (Anthropic says `tool_use_id`). The `content` is
            text here too.

            `zip` walks two lists side by side, like in the vectors chapter.

            Watch out: every call id in the model's reply must get a matching tool
            message, or the next request is rejected.
        ''',
        "prompt": r'''
            Build the OpenAI-style messages that answer a list of tool calls.

            **Write:** `openai_tool_messages(calls, outputs)`

            - `calls`: a list of OpenAI tool call dicts (each has an `"id"`), e.g. `[{"id": "call_a", ...}]`
            - `outputs`: a list of tool outputs, same length and order as `calls` (strings or JSON-serialisable values)
            - **Returns:** a list of dicts `{"role": "tool", "tool_call_id": <id>, "content": <text>}`, one per call, same order

            **Rules**
            - A string output is used unchanged; anything else becomes `json.dumps(output)`.
            - If `calls` and `outputs` have different lengths, raise `ValueError`.
            - Empty lists give `[]`.

            **Examples**
            ```python
            openai_tool_messages([{"id": "call_a"}, {"id": "call_b"}], ["sunny", {"t": 3}])
            # returns [{"role": "tool", "tool_call_id": "call_a", "content": "sunny"},
            #          {"role": "tool", "tool_call_id": "call_b", "content": "{\"t\": 3}"}]
            openai_tool_messages([{"id": "call_a"}], [])   # raises ValueError
            ```
        ''',
        "starter": r'''
            import json

            def openai_tool_messages(calls, outputs):
                ...
        ''',
        "tests": r'''
            from solution import openai_tool_messages

            def test_one_message_per_call_in_order():
                got = openai_tool_messages([{"id": "call_a"}, {"id": "call_b"}], ["sunny", "rainy"])
                want = [{"role": "tool", "tool_call_id": "call_a", "content": "sunny"},
                        {"role": "tool", "tool_call_id": "call_b", "content": "rainy"}]
                assert got == want, f"got {got!r}"

            def test_non_string_output_becomes_json():
                got = openai_tool_messages([{"id": "c"}], [{"t": 3}])
                assert got[0]["content"] == "{\"t\": 3}", f"got {got!r}"

            def test_empty_lists():
                got = openai_tool_messages([], [])
                assert got == [], f"got {got!r}"

            def test_length_mismatch_raises_value_error():
                try:
                    openai_tool_messages([{"id": "call_a"}], [])
                except ValueError:
                    return
                assert False, "expected ValueError"
        ''',
        "solution": r'''
            import json

            def openai_tool_messages(calls, outputs):
                if len(calls) != len(outputs):
                    raise ValueError("calls and outputs differ in length")
                messages = []
                for call, output in zip(calls, outputs):
                    text = output if isinstance(output, str) else json.dumps(output)
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": text})
                return messages
        ''',
        "hints": [
            "Check the lengths first, then walk both lists together with zip.",
            "Each pair (call, output) becomes one dict with role tool; convert non-strings with json.dumps.",
            "If len(calls) != len(outputs) raise ValueError; otherwise loop over zip(calls, outputs), build the text, append {\"role\": \"tool\", \"tool_call_id\": call[\"id\"], \"content\": text}; return the list.",
        ],
    },
    {
        "id": "tool-calling-6",
        "title": "Tools that fail safely",
        "difficulty": 1,
        "lesson": r'''
            ## A failed errand is still news

            If the shop is closed, you don't quit your job; you tell your manager "the
            shop was closed". The model can then try something else.

            Tools fail all the time: unknown name, bad arguments, a network error inside
            the tool. Catch the error and turn it into a **result that says what went
            wrong**:

            ```python
            def divide(a, b):
                return a / b

            try:
                print(divide(1, 0))
            except Exception as exc:
                print(f"Error: {exc}")
            ```

            Return two things: the content, and a flag saying whether it's an error. With
            Anthropic that flag becomes `"is_error": True` on the `tool_result` block.

            Catching the broad `Exception` is normally a smell, but at this boundary it's
            right: *any* tool failure should become a message, not a crash.
        ''',
        "prompt": r'''
            Run a tool without ever crashing the app.

            **Write:** `safe_run(tools, name, args)`

            - `tools`: a dict mapping tool names to functions
            - `name`: the requested tool name (string)
            - `args`: a dict of keyword arguments
            - **Returns:** a tuple `(result, is_error)`

            **Rules**
            - Unknown `name`: return `(f"Error: unknown tool {name}", True)`, e.g. `"Error: unknown tool fly"`.
            - If the tool raises any exception: return `(f"Error: {exc}", True)` where `exc` is the exception.
            - Otherwise return `(the tool's return value, False)` - the value unchanged.

            **Examples**
            ```python
            def divide(a, b):
                return a / b
            tools = {"divide": divide}
            safe_run(tools, "divide", {"a": 6, "b": 3})   # returns (2.0, False)
            safe_run(tools, "divide", {"a": 1, "b": 0})   # returns ("Error: division by zero", True)
            safe_run(tools, "fly", {})                    # returns ("Error: unknown tool fly", True)
            ```
        ''',
        "starter": r'''
            def safe_run(tools, name, args):
                ...
        ''',
        "tests": r'''
            from solution import safe_run

            def divide(a, b):
                return a / b

            def lookup(key):
                return {"k": [1, 2]}[key]

            TOOLS = {"divide": divide, "lookup": lookup}

            def test_success_returns_value_and_false():
                got = safe_run(TOOLS, "divide", {"a": 6, "b": 3})
                assert tuple(got) == (2.0, False), f"got {got!r}"

            def test_value_is_not_converted():
                got = safe_run(TOOLS, "lookup", {"key": "k"})
                assert tuple(got) == ([1, 2], False), f"got {got!r}"

            def test_exception_becomes_error_text():
                got = safe_run(TOOLS, "divide", {"a": 1, "b": 0})
                assert tuple(got) == ("Error: division by zero", True), f"got {got!r}"

            def test_bad_arguments_become_error():
                result, is_error = safe_run(TOOLS, "divide", {"x": 1})
                assert is_error is True and result.startswith("Error: "), f"got {(result, is_error)!r}"

            def test_unknown_tool():
                got = safe_run(TOOLS, "fly", {})
                assert tuple(got) == ("Error: unknown tool fly", True), f"got {got!r}"
        ''',
        "solution": r'''
            def safe_run(tools, name, args):
                if name not in tools:
                    return f"Error: unknown tool {name}", True
                try:
                    return tools[name](**args), False
                except Exception as exc:
                    return f"Error: {exc}", True
        ''',
        "hints": [
            "Two failure cases: the name isn't in the registry, or the call raises.",
            "Check the name with `in` first; wrap only the call itself in try/except Exception.",
            "If name not in tools return the unknown-tool text and True; try calling tools[name](**args) and return (value, False); in except Exception as exc return (f\"Error: {exc}\", True).",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "tool-calling-7",
        "title": "Answer every tool call",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## Putting it together

            One reply can hold several `tool_use` blocks. Run each (safely), and answer
            all of them in **one** `user` message with one `tool_result` block per call,
            in the same order. Failed calls get `"is_error": True`.
        ''',
        "prompt": r'''
            Handle all the tool calls in one Anthropic-style reply.

            **Write:** `handle_tool_calls(reply, tools)`

            - `reply`: a dict with `"content"`: a list of blocks (`"text"` and `"tool_use"` blocks;
              tool_use blocks have `"id"`, `"name"`, `"input"`)
            - `tools`: a dict mapping tool names to functions
            - **Returns:** one message `{"role": "user", "content": [<tool_result block>, ...]}`

            **Rules**
            - One `tool_result` block per `tool_use` block, in the same order; text blocks are ignored.
            - Each block: `{"type": "tool_result", "tool_use_id": <the call's id>, "content": <text>}`.
            - Call the tool with the `input` dict as keyword arguments.
            - Content text: a string result unchanged; any other result `json.dumps(result)`.
            - Unknown tool: content `"Error: unknown tool <name>"` and add `"is_error": True`.
            - Tool raises: content `"Error: <exception message>"` and add `"is_error": True`.
            - Successful blocks have no `is_error` key.
            - If there are no tool_use blocks, return `None`.

            **Examples**
            ```python
            def add(a, b):
                return a + b
            reply = {"stop_reason": "tool_use", "content": [
                {"type": "text", "text": "Adding."},
                {"type": "tool_use", "id": "t1", "name": "add", "input": {"a": 1, "b": 2}},
                {"type": "tool_use", "id": "t2", "name": "sub", "input": {}},
            ]}
            handle_tool_calls(reply, {"add": add})
            # returns {"role": "user", "content": [
            #   {"type": "tool_result", "tool_use_id": "t1", "content": "3"},
            #   {"type": "tool_result", "tool_use_id": "t2", "content": "Error: unknown tool sub", "is_error": True}]}
            handle_tool_calls({"content": [{"type": "text", "text": "Hi"}]}, {"add": add})   # returns None
            ```
        ''',
        "starter": r'''
            import json

            def handle_tool_calls(reply, tools):
                ...
        ''',
        "tests": r'''
            from solution import handle_tool_calls

            def add(a, b):
                return a + b

            def weather(city):
                if city == "Atlantis":
                    raise LookupError("no such city")
                return {"city": city, "temp": 20}

            def echo(text):
                return text

            TOOLS = {"add": add, "weather": weather, "echo": echo}

            def call(i, name, inp):
                return {"type": "tool_use", "id": i, "name": name, "input": inp}

            def test_single_call_result():
                got = handle_tool_calls({"content": [call("t1", "add", {"a": 1, "b": 2})]}, TOOLS)
                want = {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "3"}]}
                assert got == want, f"got {got!r}"

            def test_several_calls_in_order_text_ignored():
                reply = {"content": [{"type": "text", "text": "ok"}, call("a", "echo", {"text": "hi"}),
                                     call("b", "weather", {"city": "Oslo"})]}
                got = handle_tool_calls(reply, TOOLS)
                assert [b["tool_use_id"] for b in got["content"]] == ["a", "b"], f"got {got!r}"
                assert got["content"][0]["content"] == "hi", f"got {got!r}"
                assert got["content"][1]["content"] == "{\"city\": \"Oslo\", \"temp\": 20}", f"got {got!r}"

            def test_unknown_tool_is_error():
                got = handle_tool_calls({"content": [call("t2", "sub", {})]}, TOOLS)
                want = {"type": "tool_result", "tool_use_id": "t2", "content": "Error: unknown tool sub",
                        "is_error": True}
                assert got["content"] == [want], f"got {got!r}"

            def test_raising_tool_is_error_and_others_still_run():
                reply = {"content": [call("x", "weather", {"city": "Atlantis"}), call("y", "add", {"a": 2, "b": 2})]}
                got = handle_tool_calls(reply, TOOLS)
                first, second = got["content"]
                assert first["content"] == "Error: no such city" and first.get("is_error") is True, f"got {first!r}"
                assert second["content"] == "4" and "is_error" not in second, f"got {second!r}"

            def test_no_tool_calls_returns_none():
                got = handle_tool_calls({"content": [{"type": "text", "text": "Hi"}]}, TOOLS)
                assert got is None, f"got {got!r}"
        ''',
        "solution": r'''
            import json

            def handle_tool_calls(reply, tools):
                results = []
                for block in reply["content"]:
                    if block["type"] != "tool_use":
                        continue
                    name = block["name"]
                    item = {"type": "tool_result", "tool_use_id": block["id"]}
                    if name not in tools:
                        item["content"] = f"Error: unknown tool {name}"
                        item["is_error"] = True
                    else:
                        try:
                            value = tools[name](**block["input"])
                        except Exception as exc:
                            item["content"] = f"Error: {exc}"
                            item["is_error"] = True
                        else:
                            item["content"] = value if isinstance(value, str) else json.dumps(value)
                    results.append(item)
                if not results:
                    return None
                return {"role": "user", "content": results}
        ''',
        "hints": [
            "Combine three earlier steps: finding tool_use blocks, safe running, and building tool_result blocks.",
            "For each tool_use block build a result dict; set content and, only on failure, is_error. Collect them, then wrap in one user message.",
            "Loop over content, skip non tool_use blocks; start item with type and tool_use_id; handle unknown name, then try/except around tools[name](**input); convert non-strings with json.dumps; append; return None if the list is empty, else the user message.",
        ],
    },
    {
        "id": "tool-calling-8",
        "title": "Check argument types",
        "difficulty": 2,
        "prompt": r'''
            Models sometimes send `"3"` where you asked for a number. Check argument types
            against the schema before running a tool.

            **Write:** `type_errors(schema, args)`

            - `schema`: an `input_schema` dict; each property has a `"type"`:
              `"string"`, `"integer"`, `"number"`, `"boolean"`, `"array"` or `"object"`
            - `args`: the arguments dict
            - **Returns:** a list of error strings `"<name>: expected <type>"`, in the order of the keys in `args`

            **Rules**
            - Python types: string → `str`, integer → `int`, number → `int` or `float`,
              boolean → `bool`, array → `list`, object → `dict`.
            - `True`/`False` are **not** valid integers or numbers (even though `bool` is a kind of `int` in Python).
            - Arguments not in `properties` are skipped (another check handles them).
            - Missing arguments are not reported here.

            **Examples**
            ```python
            schema = {"type": "object", "properties": {
                "city": {"type": "string"}, "days": {"type": "integer"},
                "temp": {"type": "number"}, "exact": {"type": "boolean"}}, "required": []}
            type_errors(schema, {"city": "Oslo", "days": 3, "temp": 2})     # returns []
            type_errors(schema, {"days": "3", "temp": 1.5})                 # returns ["days: expected integer"]
            type_errors(schema, {"days": True, "exact": 1})
            # returns ["days: expected integer", "exact: expected boolean"]
            ```
        ''',
        "starter": r'''
            def type_errors(schema, args):
                ...
        ''',
        "tests": r'''
            from solution import type_errors

            SCHEMA = {"type": "object", "properties": {
                "city": {"type": "string"}, "days": {"type": "integer"}, "temp": {"type": "number"},
                "exact": {"type": "boolean"}, "tags": {"type": "array"}, "opts": {"type": "object"}},
                "required": []}

            def test_all_correct_types():
                args = {"city": "Oslo", "days": 3, "temp": 2.5, "exact": False, "tags": ["a"], "opts": {}}
                got = type_errors(SCHEMA, args)
                assert got == [], f"got {got!r}"

            def test_int_is_a_valid_number():
                got = type_errors(SCHEMA, {"temp": 2})
                assert got == [], f"got {got!r}"

            def test_string_digits_are_not_integer():
                got = type_errors(SCHEMA, {"days": "3", "temp": 1.5})
                assert got == ["days: expected integer"], f"got {got!r}"

            def test_bool_is_not_integer_or_number_and_int_is_not_bool():
                got = type_errors(SCHEMA, {"days": True, "temp": False, "exact": 1})
                assert got == ["days: expected integer", "temp: expected number", "exact: expected boolean"], f"got {got!r}"

            def test_float_is_not_integer_and_array_object_checked():
                got = type_errors(SCHEMA, {"days": 2.0, "tags": "a", "opts": []})
                assert got == ["days: expected integer", "tags: expected array", "opts: expected object"], f"got {got!r}"

            def test_unknown_args_skipped():
                got = type_errors(SCHEMA, {"zzz": 1, "city": 5})
                assert got == ["city: expected string"], f"got {got!r}"
        ''',
        "solution": r'''
            PY_TYPES = {"string": (str,), "integer": (int,), "number": (int, float),
                        "boolean": (bool,), "array": (list,), "object": (dict,)}

            def type_errors(schema, args):
                errors = []
                props = schema["properties"]
                for name, value in args.items():
                    if name not in props:
                        continue
                    expected = props[name]["type"]
                    ok = isinstance(value, PY_TYPES[expected])
                    if expected in ("integer", "number") and isinstance(value, bool):
                        ok = False
                    if not ok:
                        errors.append(f"{name}: expected {expected}")
                return errors
        ''',
        "hints": [
            "A dict mapping each JSON type name to Python type(s) keeps this short; isinstance accepts a tuple of types.",
            "isinstance(True, int) is True, so integers and numbers need an extra check that the value is not a bool.",
            "Loop over args.items(); skip names not in properties; look up the expected type; test isinstance with the mapped types; mark bools as wrong for integer/number; append \"name: expected type\" on failure.",
        ],
    },
    {
        "id": "tool-calling-9",
        "title": "Convert tools to OpenAI format",
        "difficulty": 2,
        "prompt": r'''
            Your app supports both providers. Keep one list of tool definitions (Anthropic
            shape) and convert it for OpenAI, and convert OpenAI's tool calls back into
            Anthropic-style `tool_use` blocks so the rest of your code handles one shape.

            **Write:** `to_openai_tools(tools)` and `from_openai_calls(tool_calls)`

            `to_openai_tools(tools)`
            - `tools`: a list of `{"name", "description", "input_schema"}` dicts
            - **Returns:** a list of `{"type": "function", "function": {"name": ..., "description": ..., "parameters": <input_schema>}}`, same order

            `from_openai_calls(tool_calls)`
            - `tool_calls`: a list of `{"id", "type": "function", "function": {"name", "arguments": <JSON text>}}`
            - **Returns:** a list of `{"type": "tool_use", "id": ..., "name": ..., "input": <parsed dict>}`, same order

            **Rules**
            - Empty or whitespace-only `arguments` parse to `{}`.
            - If `arguments` is not valid JSON, raise `ValueError` with the message `"bad arguments for <name>"`.
            - Don't change the input lists or dicts.

            **Examples**
            ```python
            to_openai_tools([{"name": "now", "description": "Time.", "input_schema": {"type": "object", "properties": {}, "required": []}}])
            # returns [{"type": "function", "function": {"name": "now", "description": "Time.",
            #           "parameters": {"type": "object", "properties": {}, "required": []}}}]
            from_openai_calls([{"id": "call_1", "type": "function", "function": {"name": "add", "arguments": "{\"a\": 1}"}}])
            # returns [{"type": "tool_use", "id": "call_1", "name": "add", "input": {"a": 1}}]
            from_openai_calls([{"id": "c", "type": "function", "function": {"name": "add", "arguments": "{a: 1"}}])
            # raises ValueError("bad arguments for add")
            ```
        ''',
        "starter": r'''
            import json

            def to_openai_tools(tools):
                ...

            def from_openai_calls(tool_calls):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import to_openai_tools, from_openai_calls

            SCHEMA = {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}
            TOOLS = [{"name": "search", "description": "Search.", "input_schema": SCHEMA},
                     {"name": "now", "description": "Time.", "input_schema": {"type": "object", "properties": {}, "required": []}}]

            def oc(cid, name, arguments):
                return {"id": cid, "type": "function", "function": {"name": name, "arguments": arguments}}

            def test_to_openai_wraps_each_tool():
                got = to_openai_tools(TOOLS)
                assert got[0] == {"type": "function", "function": {"name": "search", "description": "Search.",
                                                                   "parameters": SCHEMA}}, f"got {got[0]!r}"
                assert [t["function"]["name"] for t in got] == ["search", "now"], f"got {got!r}"

            def test_to_openai_does_not_change_input():
                before = copy.deepcopy(TOOLS)
                to_openai_tools(TOOLS)
                assert TOOLS == before, "input tools were changed"

            def test_from_openai_builds_tool_use_blocks():
                got = from_openai_calls([oc("call_1", "search", "{\"q\": \"hi\"}"), oc("call_2", "now", "")])
                want = [{"type": "tool_use", "id": "call_1", "name": "search", "input": {"q": "hi"}},
                        {"type": "tool_use", "id": "call_2", "name": "now", "input": {}}]
                assert got == want, f"got {got!r}"

            def test_from_openai_bad_json_raises_value_error():
                try:
                    from_openai_calls([oc("c", "add", "{a: 1")])
                except ValueError as exc:
                    assert str(exc) == "bad arguments for add", f"message was {str(exc)!r}"
                    return
                assert False, "expected ValueError"

            def test_empty_lists():
                assert to_openai_tools([]) == [] and from_openai_calls([]) == []
        ''',
        "solution": r'''
            import json

            def to_openai_tools(tools):
                return [{"type": "function",
                         "function": {"name": t["name"], "description": t["description"],
                                      "parameters": t["input_schema"]}}
                        for t in tools]

            def from_openai_calls(tool_calls):
                blocks = []
                for call in tool_calls:
                    fn = call["function"]
                    raw = fn["arguments"]
                    try:
                        args = json.loads(raw) if raw.strip() else {}
                    except json.JSONDecodeError:
                        raise ValueError(f"bad arguments for {fn['name']}")
                    blocks.append({"type": "tool_use", "id": call["id"], "name": fn["name"], "input": args})
                return blocks
        ''',
        "hints": [
            "Both functions are loops (or comprehensions) that build a new dict per item.",
            "For the calls, reuse the parsing from 'Parse an OpenAI tool call' and catch json.JSONDecodeError to raise your own ValueError.",
            "to_openai_tools: for each tool build {\"type\": \"function\", \"function\": {name, description, parameters=input_schema}}. from_openai_calls: for each call parse arguments ({} if blank) inside try/except json.JSONDecodeError, raise ValueError(f\"bad arguments for {name}\"), append the tool_use block.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "tool-calling-10",
        "title": "One full tool round",
        "difficulty": 3,
        "lesson": r'''
            ## Putting it together: the tool loop

            Send the conversation; if the model asks for tools, record its reply, run the
            tools, send the results, and ask again. Stop when it answers in text - or
            when you've gone round too many times.
        ''',
        "prompt": r'''
            Run a complete tool-calling conversation against a (fake) Anthropic-style model.

            **Write:** `chat_with_tools(model, tools, question, max_rounds=5)`

            - `model`: a function `model(messages)` that returns a reply dict
              `{"stop_reason": ..., "content": [blocks]}` (Anthropic shape)
            - `tools`: a dict mapping tool names to functions
            - `question`: the user's text
            - `max_rounds`: the maximum number of model calls
            - **Returns:** a tuple `(answer, messages)`: the final text and the full message list

            **Rules**
            - Start with `messages = [{"role": "user", "content": question}]`.
            - Each round: call `model(messages)`, then append `{"role": "assistant", "content": reply["content"]}`.
            - If `reply["stop_reason"] == "tool_use"`: run every `tool_use` block (in order) and append ONE
              `{"role": "user", "content": [tool_result blocks]}` message, then go to the next round.
              Tool result blocks follow the same rules as "Answer every tool call" (string unchanged,
              else `json.dumps`; unknown tool / exception → `"Error: ..."` content with `"is_error": True`).
            - Otherwise: `answer` is the `text` of all `"text"` blocks joined with `""`; return `(answer, messages)`.
            - If the model has been called `max_rounds` times and still wants a tool, raise
              `RuntimeError("too many tool rounds")` (do not call it again).
            - Pass the same list object to `model` each time (the model may look at it).

            **Examples**
            ```python
            def add(a, b):
                return a + b

            def fake_model(messages):
                if len(messages) == 1:
                    return {"stop_reason": "tool_use", "content": [
                        {"type": "tool_use", "id": "t1", "name": "add", "input": {"a": 2, "b": 3}}]}
                return {"stop_reason": "end_turn", "content": [{"type": "text", "text": "It is 5."}]}

            answer, messages = chat_with_tools(fake_model, {"add": add}, "What is 2+3?")
            answer          # "It is 5."
            len(messages)   # 4: user, assistant (tool_use), user (tool_result), assistant (text)
            messages[2]     # {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "5"}]}
            ```
        ''',
        "starter": r'''
            import json

            def chat_with_tools(model, tools, question, max_rounds=5):
                ...
        ''',
        "tests": r'''
            from solution import chat_with_tools

            def add(a, b):
                return a + b

            def boom():
                raise RuntimeError("tool broke")

            TOOLS = {"add": add, "boom": boom}

            def use(i, name, inp):
                return {"type": "tool_use", "id": i, "name": name, "input": inp}

            def scripted(replies):
                seen = []
                def model(messages):
                    seen.append(len(messages))
                    return replies[len(seen) - 1]
                model.seen = seen
                return model

            def test_no_tools_needed():
                model = scripted([{"stop_reason": "end_turn", "content": [{"type": "text", "text": "Hi!"}]}])
                answer, messages = chat_with_tools(model, TOOLS, "hello")
                assert answer == "Hi!", f"answer {answer!r}"
                assert messages == [{"role": "user", "content": "hello"},
                                    {"role": "assistant", "content": [{"type": "text", "text": "Hi!"}]}], f"got {messages!r}"

            def test_one_tool_round():
                model = scripted([
                    {"stop_reason": "tool_use", "content": [use("t1", "add", {"a": 2, "b": 3})]},
                    {"stop_reason": "end_turn", "content": [{"type": "text", "text": "It is "}, {"type": "text", "text": "5."}]},
                ])
                answer, messages = chat_with_tools(model, TOOLS, "What is 2+3?")
                assert answer == "It is 5.", f"answer {answer!r}"
                assert len(messages) == 4, f"got {len(messages)} messages"
                assert messages[2] == {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "5"}]}, f"got {messages[2]!r}"
                assert model.seen == [1, 3], f"model saw message counts {model.seen}"

            def test_errors_are_sent_back_not_raised():
                model = scripted([
                    {"stop_reason": "tool_use", "content": [use("a", "boom", {}), use("b", "nope", {})]},
                    {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Sorry."}]},
                ])
                answer, messages = chat_with_tools(model, TOOLS, "go")
                results = messages[2]["content"]
                assert results[0] == {"type": "tool_result", "tool_use_id": "a", "content": "Error: tool broke",
                                      "is_error": True}, f"got {results[0]!r}"
                assert results[1]["content"] == "Error: unknown tool nope" and results[1]["is_error"] is True
                assert answer == "Sorry."

            def test_two_tool_rounds():
                model = scripted([
                    {"stop_reason": "tool_use", "content": [use("t1", "add", {"a": 1, "b": 1})]},
                    {"stop_reason": "tool_use", "content": [{"type": "text", "text": "more"}, use("t2", "add", {"a": 2, "b": 2})]},
                    {"stop_reason": "end_turn", "content": [{"type": "text", "text": "4"}]},
                ])
                answer, messages = chat_with_tools(model, TOOLS, "q")
                assert answer == "4" and len(messages) == 6, f"got {answer!r}, {len(messages)} messages"
                assert messages[4]["content"][0]["content"] == "4"

            def test_too_many_rounds_raises():
                forever = {"stop_reason": "tool_use", "content": [use("t", "add", {"a": 0, "b": 0})]}
                model = scripted([forever] * 10)
                try:
                    chat_with_tools(model, TOOLS, "q", max_rounds=3)
                except RuntimeError as exc:
                    assert str(exc) == "too many tool rounds", f"message {str(exc)!r}"
                    assert len(model.seen) == 3, f"model was called {len(model.seen)} times"
                    return
                assert False, "expected RuntimeError"
        ''',
        "solution": r'''
            import json

            def run_block(block, tools):
                name = block["name"]
                item = {"type": "tool_result", "tool_use_id": block["id"]}
                if name not in tools:
                    item["content"] = f"Error: unknown tool {name}"
                    item["is_error"] = True
                    return item
                try:
                    value = tools[name](**block["input"])
                except Exception as exc:
                    item["content"] = f"Error: {exc}"
                    item["is_error"] = True
                    return item
                item["content"] = value if isinstance(value, str) else json.dumps(value)
                return item

            def chat_with_tools(model, tools, question, max_rounds=5):
                messages = [{"role": "user", "content": question}]
                for _ in range(max_rounds):
                    reply = model(messages)
                    messages.append({"role": "assistant", "content": reply["content"]})
                    if reply["stop_reason"] != "tool_use":
                        answer = "".join(b["text"] for b in reply["content"] if b["type"] == "text")
                        return answer, messages
                    results = [run_block(b, tools) for b in reply["content"] if b["type"] == "tool_use"]
                    messages.append({"role": "user", "content": results})
                raise RuntimeError("too many tool rounds")
        ''',
        "hints": [
            "A for loop over range(max_rounds) is the round counter; raising after the loop handles the limit.",
            "Inside each round: call the model, append its reply as an assistant message, then either return the joined text or append a user message of tool results. A helper that turns one tool_use block into one tool_result block keeps it tidy.",
            "messages = [user question]; for each round: reply = model(messages); append assistant content; if stop_reason is not tool_use, join text blocks and return (answer, messages); else build results for every tool_use block (unknown / exception / json.dumps rules) and append them as one user message. After the loop raise RuntimeError(\"too many tool rounds\").",
        ],
    },
]
