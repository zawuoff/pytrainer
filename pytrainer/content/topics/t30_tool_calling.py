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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["tool", "tool calling", "function calling", "tool definition", "input_schema",
                 "tool_use", "tool_calls", "arguments", "registry", "dispatch", "tool_result",
                 "is_error", "stop_reason", "tool loop"],
    "cards": [
        {
            "syntax": '{"name": ..., "description": ..., "input_schema": {...}}',
            "explain": "An Anthropic tool definition. input_schema is a JSON schema for the arguments. OpenAI names that key parameters.",
            "example": r'''
                tool = {"name": "get_weather",
                        "description": "Current weather for a city.",
                        "input_schema": {"type": "object",
                                         "properties": {"city": {"type": "string"}},
                                         "required": ["city"]}}
                print(tool["name"], tool["input_schema"]["required"])
                # get_weather ['city']
            ''',
        },
        {
            "syntax": '[b for b in reply["content"] if b["type"] == "tool_use"]',
            "explain": "The tool calls of an Anthropic reply. Each block has an id, a name and an input dict of arguments.",
            "example": r'''
                reply = {"stop_reason": "tool_use", "content": [
                    {"type": "text", "text": "Checking."},
                    {"type": "tool_use", "id": "t1", "name": "add",
                     "input": {"a": 2, "b": 3}}]}
                calls = [b for b in reply["content"] if b["type"] == "tool_use"]
                print(calls[0]["name"], calls[0]["input"])
                # add {'a': 2, 'b': 3}
            ''',
        },
        {
            "syntax": 'json.loads(call["function"]["arguments"])',
            "explain": "The arguments of an OpenAI tool call. They arrive as a string of JSON text, so parse them into a dict first.",
            "example": r'''
                import json
                call = {"id": "call_1", "type": "function", "function": {
                    "name": "add", "arguments": '{"a": 2, "b": 3}'}}
                args = json.loads(call["function"]["arguments"])
                print(call["function"]["name"], args["a"] + args["b"])
                # add 5
            ''',
        },
        {
            "syntax": "registry[name](**args)",
            "explain": "Looks up the function for a tool name and calls it with each key of args as a keyword argument.",
            "example": r'''
                def add(a, b):
                    return a + b
                registry = {"add": add}
                name, args = "add", {"a": 2, "b": 3}
                if name in registry:
                    print(registry[name](**args))
                # 5
            ''',
        },
        {
            "syntax": '{"type": "tool_result", "tool_use_id": id, "content": text}',
            "explain": "An Anthropic tool result block. Send a list of them as the content of one user message. Add \"is_error\": True on failure.",
            "example": r'''
                import json
                block = {"type": "tool_result", "tool_use_id": "t1",
                         "content": json.dumps({"temp": 21})}
                message = {"role": "user", "content": [block]}
                print(message["content"][0]["content"])
                # {"temp": 21}
            ''',
        },
        {
            "syntax": '{"role": "tool", "tool_call_id": id, "content": text}',
            "explain": "An OpenAI tool result. Append one such message for every tool call in the reply, with the id of that call.",
            "example": r'''
                calls = [{"id": "call_a"}, {"id": "call_b"}]
                messages = []
                for call, out in zip(calls, ["sunny", "rainy"]):
                    messages.append({"role": "tool", "tool_call_id": call["id"],
                                     "content": out})
                print(messages[1])
                # {'role': 'tool', 'tool_call_id': 'call_b', 'content': 'rainy'}
            ''',
        },
    ],
}

LESSON = r'''
## Tool calling

A model produces text. It cannot run code. A **tool** is a Python function that you
allow the model to request. **Tool calling** is an exchange with three parts. The model's
reply names a tool and gives its arguments. Your code runs the function. Your code sends
the return value back in the next request. The model never runs anything.

Step through the stages to see the data that is sent or produced at each one.

```diagram
{"type": "flow", "title": "One tool-calling round for \"Weather in Paris?\"", "steps": [{"label": "Call the model", "detail": "Your code sends the message list and the list of tool definitions in one request.", "code": "messages = [{\"role\": \"user\", \"content\": \"Weather in Paris?\"}]\ntools = [{\"name\": \"get_weather\", \"description\": \"Current weather for a city.\", \"input_schema\": {...}}]"}, {"label": "Model returns a tool call", "detail": "The reply has stop_reason \"tool_use\". Its content list holds a tool_use block with an id, a name and an input dict. Your code appends the reply content as an assistant message.", "code": "{\"stop_reason\": \"tool_use\",\n \"content\": [{\"type\": \"tool_use\", \"id\": \"toolu_01\",\n              \"name\": \"get_weather\", \"input\": {\"city\": \"Paris\"}}]}"}, {"label": "Look up the function", "detail": "Your code uses the name from the block as a key in the registry dict. The value is the Python function. A name that is not a key becomes an error result.", "code": "name = \"get_weather\"\nfunc = registry[name]"}, {"label": "Run it with the arguments", "detail": "Your code calls the function and passes each key of the input dict as a keyword argument. The model does not run anything.", "code": "args = {\"city\": \"Paris\"}\nfunc(**args)\n# '21C in Paris'"}, {"label": "Append the tool result", "detail": "Your code appends a user message with one tool_result block. The block repeats the id of the tool call. Then the code calls the model again with the longer list.", "code": "{\"role\": \"user\",\n \"content\": [{\"type\": \"tool_result\", \"tool_use_id\": \"toolu_01\",\n              \"content\": \"21C in Paris\"}]}"}, {"label": "Model returns text", "detail": "When a reply has stop_reason \"end_turn\", the loop ends. Your code reads the text blocks of that reply.", "code": "{\"stop_reason\": \"end_turn\",\n \"content\": [{\"type\": \"text\", \"text\": \"It is 21C in Paris.\"}]}"}], "loop": {"from": 4, "to": 0, "label": "while stop_reason is \"tool_use\""}}
```

## Tool definitions

A **tool definition** is a dict that describes one tool to the model. It has a `name`, a
`description` and a JSON schema for the arguments. A JSON schema is the description of
the shape of data from the structured-output chapter. Anthropic names the schema key
`input_schema`.

```python
tool = {"name": "get_weather",
        "description": "Current weather for a city.",
        "input_schema": {"type": "object",
                         "properties": {"city": {"type": "string", "description": "City name"}},
                         "required": ["city"]}}
print(tool["input_schema"]["required"])
# ['city']
```

OpenAI nests the same three values in a second dict:
`{"type": "function", "function": {"name": ..., "description": ..., "parameters": <schema>}}`.

## Reading a tool call

A **tool call** is the part of a reply that names a tool and gives its arguments. The two
providers use different keys.

| | Anthropic | OpenAI (chat completions) |
| --- | --- | --- |
| The reply requests a tool | `stop_reason == "tool_use"` | `finish_reason == "tool_calls"` |
| Location of the calls | `content` blocks with `type == "tool_use"` | `message["tool_calls"]` |
| Arguments | `block["input"]`, a dict | `call["function"]["arguments"]`, a JSON string |
| Id | `block["id"]` (`"toolu_..."`) | `call["id"]` (`"call_..."`) |

Anthropic gives you the arguments as a dict. OpenAI gives you JSON text, so you parse it
with `json.loads`.

```python
import json

block = {"type": "tool_use", "id": "toolu_01", "name": "get_weather",
         "input": {"city": "Paris"}}
call = {"id": "call_1", "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Paris\"}"}}
print(block["input"]["city"])
# Paris
print(type(call["function"]["arguments"]).__name__)
# str
print(json.loads(call["function"]["arguments"])["city"])
# Paris
```

## Dispatching

A **tool registry** is a dict that maps each tool name to its function. **Dispatching**
means looking up the name in the registry and calling the function you get.
`registry[name](**args)` passes each key of `args` as a keyword argument.

```python
def get_weather(city):
    return f"21C in {city}"

def add(a, b):
    return a + b

registry = {"get_weather": get_weather, "add": add}
name = "get_weather"
args = {"city": "Paris"}
print(registry[name](**args))
# 21C in Paris
print("fly" in registry)
# False
```

Click a key to look up its function. Then type `fly` as the key and run `registry[key]` to
see what happens with an unknown tool name.

```diagram
{"type": "dict", "title": "Look up a tool by name in the registry", "name": "registry", "entries": [["get_weather", {"raw": "<function get_weather>"}], ["add", {"raw": "<function add>"}]]}
```

The model can request a name that is not in the registry, and `registry["fly"]` raises
`KeyError`. Check `name in registry` before the lookup. Check the arguments against the
schema before the call.

## Sending results back

A tool result goes back as a message that repeats the id of the tool call.

- Anthropic: one `user` message whose content is a list of
  `{"type": "tool_result", "tool_use_id": id, "content": "..."}` blocks. Add
  `"is_error": True` to a block when the tool failed.
- OpenAI: one `{"role": "tool", "tool_call_id": id, "content": "..."}` message per call.

The content is text. Convert a dict or a list with `json.dumps`. `str` gives Python
syntax with single quotes, which is not JSON.

```python
import json

output = {"temp": 21}
print(json.dumps(output))
# {"temp": 21}
print(str(output))
# {'temp': 21}
```

## The loop

1. Send the messages and the tool definitions.
2. If the reply requests tools, append the reply as an `assistant` message, run every
   call and append the results.
3. Repeat from step 1 until a reply requests no tool. Then read its text.

Always set a maximum number of rounds. Without one, a model that requests a tool in
every reply keeps the loop running forever.

## Common mistakes

- OpenAI `arguments` is a string. Indexing it with a key such as `["city"]` raises `TypeError`.
- Every tool call id must get exactly one result. A missing result makes the next request fail.
- A tool failure goes back to the model as a result with the error text. The model can
  then send a corrected call. Do not let the exception stop your program.
- `bool` is a subclass of `int`, so `isinstance(True, int)` is `True`. When you validate
  an integer argument, reject `bool` values first.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "tool-calling-s1",
        "title": "Read a tool call",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Read a request to run a function

            A chat app needs information that is not in the conversation. The model can ask your application to run a named function with particular inputs. Before anything happens, your code receives that request as data and decides how to handle it.

            A model produces text. It cannot run a Python function. Its reply can contain
            a **tool call** instead: data that names a function and gives the arguments
            for it. Your code reads the tool call and runs the function. A tool call is
            also called a function call.

            The Anthropic-shaped reply used here is a plain Python dict. Its `content` key holds a list of
            dicts called blocks. A tool call is a block whose `"type"` is `"tool_use"`.
            The reply's `stop_reason` is then `"tool_use"` as well.

            ```python
            reply = {"stop_reason": "tool_use", "content": [
                {"type": "text", "text": "Let me check."},
                {"type": "tool_use", "id": "toolu_01", "name": "get_weather",
                 "input": {"city": "Paris"}}]}
            block = reply["content"][1]
            print(block["name"])
            # get_weather
            print(block["input"])
            # {'city': 'Paris'}
            print(block["id"])
            # toolu_01
            ```

            ```quiz
            Which part actually executes the local function?
            - [x] Your application code :: The model supplies a request, not Python execution.
            - [ ] The name string :: A string naming a function does not call it.
            ```

            The block gives you three values. `name` is the name of the tool. `input`
            holds the arguments and is already a dict. `id` identifies this call. You
            need the id when you send the result back.

            The model never runs the function. Your code does.

            ```match
            name :: which function is requested
            input :: values requested for its arguments
            id :: identifier used to attach the result
            ```

            **Watch out:** A proposed tool call is not permission to run an arbitrary function. The examples below use a controlled local interface and no network.

            **In short:** The model proposes a tool call; your application controls execution and returns the result.
        ''',
        "prompt": r'''
            Read the program, then enter exactly what its print calls display, one output line per line.
        ''',
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
            Read the output from top to bottom. `stop_reason` says why the model stopped: it requested a tool call. The second content
            block is the `tool_use` block: its `name` is `get_weather`, its `input` dict has
            `city` = `Oslo`, and that dict has 2 keys.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Locate the selected block before reading its fields.",
            "Some printed values belong to the outer reply and others to the nested input.",
            "Follow each access in order and count only the keys of the dictionary passed to len.",
        ],
    },
    {
        "id": "tool-calling-s2",
        "title": "Describe a tool",
        "difficulty": 0,
        "lesson": r'''
            ## Describe what a callable tool is for

            You expose a document lookup function to the model. Its name alone may not explain when to use it or what input it expects. Send a description of the operation and a description of its arguments, keeping those distinct from the Python function itself.

            Your request describes the tools the model is meant to request. A
            **tool definition** is a dict that describes one tool. It has three keys.

            - `name`: the string the model uses to request the tool.
            - `description`: text that says what the tool does and when to use it.
            - `input_schema`: a JSON schema for the arguments.

            The schema has the form you used in the structured-output chapter: an
            object with `properties` and a `required` list.

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
            # search_docs ['query']
            ```

            ```quiz
            Does a tool definition execute the function?
            - [x] No :: It describes the interface available to request.
            - [ ] Yes :: Descriptive data has no execution effect by itself.
            ```

            `input_schema` is the key name that Anthropic uses. You send a list of tool
            definitions with every request.

            The model decides when to call a tool mostly from its description. A vague
            description leads to calls at the wrong time, or to no calls.

            ```order
            schema = {"type": "object", "properties": {}}
            definition = {"name": "ping", "input_schema": schema}
            print(definition["name"])
            ---
            Build the argument description before placing it inside the complete definition.
            ```

            **Watch out:** A description helps the model choose, but it does not enforce valid arguments or authorization. Your application still needs checks before execution.

            **In short:** A tool definition explains the operation and its expected inputs without running it.
        ''',
        "prompt": r'''
            Every tool definition has the same structure. Complete the function by replacing the `___`.

            **Your job:** write `make_tool(name, description)`

            **What goes in**
            - `name`: a string, e.g. `"get_time"`
            - `description`: a string, e.g. `"Current time."`

            **What comes out**
            - Return an Anthropic-style tool definition dict with no arguments:
              Its `name` and `description` come from the supplied arguments. Its `input_schema` is
              `{"type": "object", "properties": {}, "required": []}`.

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
            "The missing value describes what the tool does.",
            "Its value should come from the caller, like the completed entries beside it.",
            "Match the incomplete field to the relevant argument and preserve all the supplied wording.",
        ],
    },
    {
        "id": "tool-calling-s3",
        "title": "Fix: does it want a tool?",
        "difficulty": 0,
        "lesson": r'''
            ## Use the stopping reason for the right response shape

            Your application receives a reply but never enters its tool-handling branch. The comparison runs without an error, so inspect the exact status text it is testing. Two interfaces can describe the same event with different strings.

            The completed Anthropic-shaped replies in this exercise have a `stop_reason` key. Its value is a string that
            says why the model stopped writing. Read it before you read the content,
            because it tells you what your code must do next.

            ```python
            for reason in ["end_turn", "tool_use", "max_tokens"]:
                reply = {"stop_reason": reason}
                print(reason, reply["stop_reason"] == "tool_use")
            # end_turn False
            # tool_use True
            # max_tokens False
            ```

            ```quiz
            Why can a wrong status spelling be hard to notice?
            - [x] The comparison still runs and returns False :: No Python exception announces that the vocabulary is wrong.
            - [ ] Python automatically repairs it :: Equality compares the strings as written.
            ```

            - `"end_turn"`: the model finished its answer.
            - `"tool_use"`: the model requests one or more tools.
            - `"max_tokens"`: the reply reached the token limit of the request.

            OpenAI uses a different key and a different value: `finish_reason` is
            `"tool_calls"`. A comparison with the other provider's value raises no
            error. It is `False` for every reply, so the bug is easy to miss.

            ```predict
            reason = "finished"
            print(reason == "finish")
            print(reason == "finished")
            ---
            Equality uses the whole string, including its ending.
            ```

            **Watch out:** Keep response field names and status values from the same interface. Mixing vocabularies produces a logic bug even when all dictionary accesses work.

            **In short:** Compare the stopping reason with the exact value required by this response contract.
        ''',
        "prompt": r'''
            The app must know when an Anthropic-style reply asks for a tool. The function
            below always returns `False`. Fix the bug.

            **Your job:** write `wants_tool(reply)`

            **What goes in**
            - `reply`: a dict with a `"stop_reason"` key, e.g. `{"stop_reason": "tool_use", "content": [...]}`

            **What comes out**
            - Return `True` if `stop_reason` is `"tool_use"`, otherwise `False`

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
            "Check the exact status vocabulary used by this response shape.",
            "The starter compares against the spelling from a different interface.",
            "Correct the expected status value while preserving the boolean comparison and response lookup.",
        ],
    },
    {
        "id": "tool-calling-s4",
        "title": "Find the tool calls",
        "difficulty": 0,
        "lesson": r'''
            ## Select every requested operation

            A response includes a sentence explaining what the model plans to do and two requests for tools. The sentence is useful for display, but it is not a call. Inspect the label of each block and preserve all the blocks representing operations.

            A reply's `content` is a list of dicts. Each dict is a **content block**:
            one part of the reply. Every block has a `type` key. A `"text"` block
            holds text. A `"tool_use"` block holds a tool call.

            ```python
            content = [
                {"type": "text", "text": "One moment."},
                {"type": "tool_use", "id": "t1", "name": "add", "input": {"a": 1, "b": 2}},
            ]
            for block in content:
                print(block["type"])
            # text
            # tool_use
            ```

            ```quiz
            Why not assume the first content block is a tool call?
            - [x] Text may come first :: Block order does not determine block type.
            - [ ] Every reply begins with a tool :: Replies can contain text, tools, or mixtures in this simulated format.
            ```

            The model can request several tools in one reply, so the list can hold
            more than one `tool_use` block. You need all of them.

            To select blocks, use the pattern from the loops chapter that builds a list inside an `if`. Start
            with an empty list, loop over the blocks, test `block["type"]` with `if`
            and `.append` each block that matches. A list comprehension with an `if`
            does the same.

            ```predict
            blocks = [{"type": "text"}, {"type": "tool_use"}, {"type": "tool_use"}]
            print([b["type"] for b in blocks if b["type"] != "text"])
            ---
            Filtering removes text without losing either requested operation.
            ```

            **Watch out:** Do not stop after finding one matching block. A reply can request several operations, and each needs its own result tied to its own identifier.

            **In short:** Filter by the type label, preserving every matching block in its original order.
        ''',
        "prompt": r'''
            Pull out every tool request from an Anthropic-style reply.

            **Your job:** write `find_tool_calls(reply)`

            **What goes in**
            - `reply`: a dict whose `"content"` is a list of blocks; each block is a dict with a `"type"` key

            **What comes out**
            - Return a list of the blocks whose `type` is `"tool_use"`, in their original order

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
            "Inspect the type label of each block.",
            "Retain all matching blocks without changing their order.",
            "Visit the content list, collect tool-request blocks, and return an empty list if none qualify.",
        ],
    },
    {
        "id": "tool-calling-s5",
        "title": "Call a tool by name",
        "difficulty": 0,
        "lesson": r'''
            ## Connect a permitted name to its function

            You received a tool name and a dictionary of argument values. The name needs to select a function your application has already registered. Then each argument value needs to reach the parameter with the corresponding name.

            A tool call gives you a name, which is a string, and arguments, which are
            a dict. A **tool registry** is a dict that maps each tool name to its
            function. **Dispatching** means looking up the name and calling the
            function you get.

            ```python
            def add(a, b):
                return a + b

            def shout(text):
                return text.upper() + "!"

            tools = {"add": add, "shout": shout}
            name = "add"
            args = {"a": 2, "b": 3}
            func = tools[name]
            print(func(**args))
            # 5
            ```

            ```quiz
            What does unpacking a dictionary in a call do?
            - [x] Supplies its entries as named arguments :: Keys identify the function parameters.
            - [ ] Passes the dictionary as one unnamed value :: That is a different kind of call.
            ```

            `**args` **unpacks** the dict: each key becomes a keyword argument.
            `func(**{"a": 2, "b": 3})` is the same call as `func(a=2, b=3)`. In the
            functions chapter `**kwargs` collected keyword arguments into a dict.
            In a call, the two stars do the reverse.

            Click a key to look up its function. Then type `fly` as the key and run
            `tools[key]`.

            ```diagram
            {"type": "dict", "title": "The tools registry: name to function", "name": "tools", "entries": [["add", {"raw": "<function add>"}], ["shout", {"raw": "<function shout>"}]]}
            ```

            `func(args)` passes the whole dict as one positional argument. With `add`
            that raises `TypeError`, because `b` gets no value.

            ```fill
            def repeat(word, times): return word * times
            options = {"word": "ha", "times": 2}
            print(repeat(___))
            ---
            - [x] **options :: The entries fill the two named parameters.
            - [ ] options :: This provides one positional argument and leaves times missing.
            ```

            **Watch out:** A missing registry entry raises KeyError, while mismatched argument names can raise TypeError. These failures identify different parts of the requested call.

            **In short:** Look up the permitted callable, then pass its argument dictionary as named values.
        ''',
        "prompt": r'''
            Run the tool the model asked for. Complete the function by replacing the `___`.

            **Your job:** write `run_tool(tools, name, args)`

            **What goes in**
            - `tools`: a dict mapping tool names to Python functions, e.g. `{"add": add}`
            - `name`: the tool name the model asked for, e.g. `"add"`
            - `args`: a dict of keyword arguments, e.g. `{"a": 2, "b": 3}`

            **What comes out**
            - Return whatever the tool function returns

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
            "The callable expects named parameters, but the values are stored in a dictionary.",
            "Use the call syntax that expands a mapping into keyword arguments.",
            "Leave the registry lookup intact and pass each stored argument value under its corresponding key.",
        ],
    },
    {
        "id": "tool-calling-s6",
        "title": "OpenAI arguments are text",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Parse argument text before reading its fields

            One tool interface gives you an argument dictionary; another gives you a string describing that dictionary. The displayed values can look similar, but Python treats them differently. Check the representation and convert text before reading fields from it.

            OpenAI sends the same information with different keys. The reply's message
            has a `tool_calls` list. Each call is a dict with an `id` and a `function`
            dict. The `function` dict holds the `name` and the `arguments`.

            ```python
            import json

            call = {"id": "call_1", "type": "function",
                    "function": {"name": "add", "arguments": "{\"a\": 2, \"b\": 3}"}}
            raw = call["function"]["arguments"]
            print(type(raw).__name__)
            # str
            print(json.loads(raw)["a"])
            # 2
            ```

            ```quiz
            Can you unpack raw JSON text as keyword arguments?
            - [x] No :: Keyword unpacking needs a mapping, not the serialized string.
            - [ ] Yes :: Looking like a dictionary does not make a string a dictionary.
            ```

            `arguments` is a string of JSON text, not a dict. You parse it with
            `json.loads` from the JSON chapter, which returns a dict. Only then can
            you read a key. Anthropic's `input` is already a dict.

            When an OpenAI reply requests tools, its `finish_reason` is `"tool_calls"`.

            The model writes the `arguments` string, so the string can be invalid
            JSON. `json.loads` then raises `json.JSONDecodeError`. A real app
            catches that exception.

            ```predict
            import json
            raw = '{"limit": 6}'
            parsed = json.loads(raw)
            print(type(raw).__name__, type(parsed).__name__)
            ---
            The parser changes the representation from text to an actual dictionary.
            ```

            **Watch out:** Malformed argument text raises JSONDecodeError. Successfully parsing it is only the first check; the resulting value must also match the tool's expected shape.

            **In short:** Convert serialized arguments to Python values before inspecting or using them.
        ''',
        "prompt": r'''
            Read the program, then enter exactly what its print calls display, one output line per line.
        ''',
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
            Read the output from top to bottom. `arguments` is a string of JSON text (`str`). `json.loads` turns it into a real
            `dict`. From the dict, `query` is `"refunds"` and `k` is the number `3`, so
            `k + 1` is `4`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Track the arguments before and after JSON parsing.",
            "The raw value is text; the parsed object holds usable fields.",
            "Evaluate the type names, nested name and query accesses, then the arithmetic on the parsed number.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "tool-calling-1",
        "title": "Parse an OpenAI tool call",
        "difficulty": 1,
        "lesson": r'''
            ## Keep a call identifier beside its parsed arguments

            After adapting a response, later code should not need to know which fields were nested or encoded as JSON. Return the call identifier, operation name, and parsed arguments together. The identifier stays attached so a later result can answer the correct request.

            In an OpenAI tool call the `id` is a key of the call dict itself. The name and the
            arguments are one level down, inside `call["function"]`, and the
            arguments are JSON text. Most apps convert each call once into the three
            values they need: the id, the name and the arguments as a dict.

            ```python
            import json

            call = {"id": "call_1", "type": "function",
                    "function": {"name": "ping", "arguments": "{}"}}
            details = call["function"]
            print(call["id"], details["name"], json.loads(details["arguments"]))
            # call_1 ping {}
            ```

            ```quiz
            How does this task treat whitespace-only argument text?
            - [x] As no arguments :: That is an explicit adapter rule, separate from JSON parsing.
            - [ ] As valid JSON whitespace :: Whitespace alone is not a complete JSON value.
            ```

            A function that returns several values separated by commas
            (`return a, b, c`) returns one tuple. The caller can unpack it into
            names: `call_id, name, args = ...`.

            For a tool with no parameters the model may send `"{}"` or an empty
            string `""`. `json.loads("")` raises `json.JSONDecodeError`. This
            example catches the exception and prints its message.

            ```python
            import json

            try:
                json.loads("")
            except json.JSONDecodeError as exc:
                print(exc)
            # Expecting value: line 1 column 1 (char 0)
            ```

            Treat an empty string, or a string of only whitespace, as no arguments.

            ```predict
            text = "   "
            print(bool(text))
            print(bool(text.strip()))
            ---
            A whitespace string is nonempty until stripping removes its characters.
            ```

            **Watch out:** Do not treat every parsing failure as empty arguments. The contract allows blank text specially; malformed nonblank text is a different case.

            **In short:** Adapt the response into a useful group of values without losing the call identifier.
        ''',
        "prompt": r'''
            Turn one OpenAI-style tool call into plain values.

            **Your job:** write `parse_openai_call(call)`

            **What goes in**
            - `call`: a dict like `{"id": "call_1", "type": "function", "function": {"name": "add", "arguments": "{\"a\": 1}"}}`

            **What comes out**
            - Return a tuple `(call_id, name, args)`: the id string, the tool name string,
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
            "The identifier is outside the nested function information.",
            "Treat blank argument text separately from nonblank text that needs parsing.",
            "Read the identifier and name, choose empty arguments or parsed arguments as specified, and return the three values in order.",
        ],
    },
    {
        "id": "tool-calling-2",
        "title": "Build a tool schema",
        "difficulty": 1,
        "lesson": r'''
            ## Describe each parameter in the schema

            Your tool has several named inputs, each with a type and a description. Store those descriptions as data and build the tool definition from them. This keeps the list of required argument names aligned with the fields you describe.

            Most tools take arguments. In the `input_schema`, each argument is one
            entry in `fields`. The key is the argument name. The value is a dict
            with the argument's `type` and a short `description` that tells the model
            what value to send.

            ```python
            fields = {}
            params = {"city": ("string", "City name"), "days": ("integer", "1 to 7")}
            for name, (kind, text) in params.items():
                fields[name] = {"type": kind, "description": text}
            print(fields["days"])
            # {'type': 'integer', 'description': '1 to 7'}
            print(list(params))
            # ['city', 'days']
            ```

            ```quiz
            What identifies a parameter inside fields?
            - [x] Its dictionary key :: The value holds that parameter's description.
            - [ ] Its list position :: Properties are addressed by name, not position.
            ```

            `for name, (kind, text) in params.items()` unpacks each key into `name`
            and each 2-item tuple into `kind` and `text`. `list(params)` gives the
            keys in the order they were added.

            JSON schema type names differ from Python type names. They are
            `"string"`, `"integer"`, `"number"`, `"boolean"`, `"array"` and `"object"`.

            The `required` list names the arguments the model must send. The model
            ignores the order of that list. Keep the same order as `fields` so
            that the definition is easy to read and to test.

            ```predict
            parameters = {"count": ("integer", "Items to return")}
            for label, (kind, description) in parameters.items():
                print(label, kind)
            ---
            Nested unpacking separates the parameter name from both pieces of its description.
            ```

            **Watch out:** JSON type names are strings such as integer, not Python type objects such as int. This step builds a description; it does not validate a future call.

            **In short:** Keep each parameter name attached to its type and description when building the schema.
        ''',
        "prompt": r'''
            Write a helper that builds a full Anthropic-style tool definition from a compact
            description of its parameters.

            **Your job:** write `tool_schema(name, description, params)`

            **What goes in**
            - `name`: a string, e.g. `"get_weather"`
            - `description`: a string
            - `params`: a dict mapping parameter name to a tuple `(json_type, param_description)`,
              e.g. `{"city": ("string", "City name")}`

            **What comes out**
            - Return a dict:
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
            "Each parameter entry describes both a type and a purpose.",
            "The property names and required names must come from the same supplied parameters.",
            "Visit parameters in order, build their property descriptions, collect their required names, and wrap both in the tool definition.",
        ],
    },
    {
        "id": "tool-calling-3",
        "title": "Check the arguments",
        "difficulty": 1,
        "lesson": r'''
            ## Explain missing and unexpected argument names

            A call misspells an argument name. Python may later complain that one argument is missing and another is unexpected. You can catch both facts before execution by comparing the received names with the tool's declared requirements.

            A model can send wrong arguments. It can leave out a required argument,
            or send a name that the tool does not have. Calling a function with a
            keyword argument it does not accept raises `TypeError`.
            **Argument validation** means checking the arguments against the schema
            before you call the function, so that you can report a clear error.

            ```python
            schema = {"type": "object",
                      "properties": {"city": {"type": "string"}, "days": {"type": "integer"}},
                      "required": ["city"]}
            args = {"cty": "Paris"}
            print([n for n in schema["required"] if n not in args])
            # ['city']
            print([n for n in args if n not in schema["properties"]])
            # ['cty']
            ```

            ```quiz
            Can one misspelling create two validation problems?
            - [x] Yes :: The intended name is absent and the misspelled name is unknown.
            - [ ] No :: Missing and unknown checks examine different sides of the contract.
            ```

            This step checks two kinds of naming mistake.

            - **Missing**: a name in `required` that is not a key of the arguments.
            - **Unknown**: a key of the arguments that is not a key of `properties`.

            Here the model wrote `cty` for `city`. `city` is missing and `cty` is
            unknown. You send the error messages back to the model as the tool
            result. Those messages give the model information it can use when proposing another call; a correction is not guaranteed.

            ```predict
            required = ["term"]
            supplied = {"termm": "invoice"}
            print("term" in supplied)
            print("termm" in required)
            ---
            The typo fails both the presence check and the allowed-name check.
            ```

            **Watch out:** This step checks names, not value types or permission to use the tool. A clean list of name errors therefore does not prove the whole call is valid.

            **In short:** Check required names for omissions and supplied names for unexpected additions.
        ''',
        "prompt": r'''
            Validate a tool call's arguments against the tool's `input_schema` before running it.

            **Your job:** write `check_args(schema, args)`

            **What goes in**
            - `schema`: an `input_schema` dict with `"properties"` (dict) and `"required"` (list)
            - `args`: the arguments dict the model sent

            **What comes out**
            - Return a list of error strings (empty list if everything is fine)

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
            "Missing names and unknown names are different comparisons.",
            "Visit the declared required names before examining supplied names.",
            "Collect omissions in required order, then unexpected arguments in input order, and return the combined messages.",
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
            ## Attach the result to the call it answers

            Two tool requests can ask the same function different questions. Returning only the function name would not tell the model which answer belongs to which request. Carry the original call identifier into the result and put the output into the required text representation.

            After your code runs a tool, it sends the return value to the model. The
            model must know which tool call the value answers. Each `tool_use` block
            has an `id`. Your result repeats that id under the key `tool_use_id`.

            With Anthropic the result is a **`tool_result` block**: a dict with
            `"type": "tool_result"`, the `tool_use_id` and the `content`. You send
            it in a `user` message whose content is a list of these blocks.

            ```python
            import json

            output = {"temp": 21}
            block = {"type": "tool_result", "tool_use_id": "toolu_01",
                     "content": json.dumps(output)}
            message = {"role": "user", "content": [block]}
            print(message)
            # {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': 'toolu_01', 'content': '{"temp": 21}'}]}
            ```

            ```quiz
            Why preserve the call identifier?
            - [x] It ties this output to one particular request :: Function names need not be unique across calls.
            - [ ] It makes the output valid JSON :: Identification and serialization are separate concerns.
            ```

            The content of a result is text. You convert a dict or a list to JSON
            text with `json.dumps`. You send a string unchanged.

            `str` is the wrong function for the conversion. It returns Python syntax
            with single quotes, which is not JSON.

            ```python
            import json

            output = {"temp": 21}
            print(str(output))
            # {'temp': 21}
            print(json.dumps(output))
            # {"temp": 21}
            ```

            ```match
            original call id :: link back to the request
            string result :: preserve as text
            dictionary result :: serialize to JSON text
            ```

            **Watch out:** Do not JSON-encode an output that is already the required text. That would add a quoted representation rather than preserving the string itself.

            **In short:** Result content carries the answer, and the call identifier says which request it answers.
        ''',
        "prompt": r'''
            Build the message that returns one tool's output to an Anthropic model.

            **Your job:** write `tool_result_message(tool_use_id, output)`

            **What goes in**
            - `tool_use_id`: the id from the `tool_use` block, e.g. `"toolu_01"`
            - `output`: what the tool returned: a string, or any JSON-serialisable value (dict, list, number...)

            **What comes out**
            - Return `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": text}]}`

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
            "Separate text conversion from result-message construction.",
            "An existing string stays unchanged; another JSON-compatible value needs serialization.",
            "Prepare the content text, attach it to the original call identifier in a result block, and wrap that block in the required message.",
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
            ## Return one message for every requested result

            You have a list of calls and a list of outputs from running them. Each output must be paired with the matching call identifier. Check that both lists cover the same number of operations before combining them, because ordinary pairing stops at the shorter list.

            OpenAI takes tool results in a different form. You do not send one `user`
            message that holds a list of results. You append one message per tool
            call, and each message has the role `"tool"`.

            ```python
            calls = [{"id": "call_a"}, {"id": "call_b"}]
            outputs = ["sunny", "rainy"]
            outgoing = []
            for call, out in zip(calls, outputs):
                outgoing.append({"role": "tool", "tool_call_id": call["id"], "content": out})
            print(len(outgoing), outgoing[1]["tool_call_id"])
            # 2 call_b
            ```

            ```quiz
            What happens when zip receives lists of different lengths?
            - [x] It stops at the shorter list :: Unpaired items do not cause an exception by themselves.
            - [ ] It raises a length error :: You must check lengths explicitly if the contract requires equality.
            ```

            The id goes under the key `tool_call_id`. Anthropic names it
            `tool_use_id`. The `content` is text here as well.

            `zip(calls, outputs)` pairs the items of the two lists by position, as
            in the loops chapter. If one list is shorter, `zip` stops at its end
            and raises no error.

            The exercise requires one result message with the matching id for each call. That preserves the request-result pairing.

            ```predict
            calls = ["a", "b"]
            outputs = ["done"]
            print(list(zip(calls, outputs)))
            ---
            Only one pair exists; zip does not invent an output for the remaining call.
            ```

            **Watch out:** Silently losing the last call leaves the conversation incomplete. Validate the counts before building outgoing so every requested operation receives a result.

            **In short:** Check the counts, pair calls and outputs by position, and preserve every call identifier.
        ''',
        "prompt": r'''
            Build the OpenAI-style messages that answer a list of tool calls.

            **Your job:** write `openai_tool_messages(calls, outputs)`

            **What goes in**
            - `calls`: a list of OpenAI tool call dicts (each has an `"id"`), e.g. `[{"id": "call_a", ...}]`
            - `outputs`: a list of tool outputs, same length and order as `calls` (strings or JSON-serialisable values)

            **What comes out**
            - Return a list of dicts `{"role": "tool", "tool_call_id": <id>, "content": <text>}`, one per call, same order

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
            "Check that every call has an output before pairing the lists.",
            "Build one result message for each positional pair.",
            "Reject unequal lengths, visit matched calls and outputs in order, serialize only non-strings, and preserve the matching identifiers.",
        ],
    },
    {
        "id": "tool-calling-6",
        "title": "Tools that fail safely",
        "difficulty": 1,
        "lesson": r'''
            ## Turn a tool failure into a marked result

            A tool raises an exception while the surrounding conversation is still useful. You want the caller to know the operation failed without losing control of the whole loop. Return both the message and a separate signal that distinguishes failure from a successful textual answer.

            Tools fail often. The model requests a name that does not exist, it sends
            bad arguments, or the tool raises because of a network error. An
            uncaught exception stops your program. Catch the exception and send
            its text to the model as the result. The model can then send a
            different call.

            ```python
            def divide(a, b):
                return a / b

            try:
                print(divide(1, 0))
            except Exception as failure:
                print(f"Error: {failure}")
            # Error: division by zero
            ```

            ```quiz
            Why return an error flag as well as text?
            - [x] Successful output can also look like an error sentence :: The explicit flag identifies the outcome unambiguously.
            - [ ] All strings mean failure :: A successful tool may legitimately return text.
            ```

            `divide(1, 0)` raises `ZeroDivisionError`, so the first `print` never
            runs. The `except` block formats the exception. `{failure}` in an f-string
            gives the exception's message.

            Return two values: the content, and a boolean that says whether the
            content is an error. With Anthropic that boolean becomes
            `"is_error": True` on the `tool_result` block.

            In most code you catch one specific exception type. Here you catch
            `Exception`, because every kind of tool failure must become a result.

            ```predict
            result = ("not found", True)
            message, failed = result
            print(failed)
            print(message)
            ---
            The flag and the content are separate values with different purposes.
            ```

            **Watch out:** Exception messages in these exercises are safe fixtures. A production app should avoid forwarding credentials or private internal details when reporting tool failures.

            **In short:** Keep execution failures distinguishable from successful values while preserving a usable result.
        ''',
        "prompt": r'''
            Run a tool without ever crashing the app.

            **Your job:** write `safe_run(tools, name, args)`

            **What goes in**
            - `tools`: a dict mapping tool names to functions
            - `name`: the requested tool name (string)
            - `args`: a dict of keyword arguments

            **What comes out**
            - Return a tuple `(result, is_error)`

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
            "An unknown name and a failing known function need separate handling.",
            "Only the actual tool execution belongs inside the exception handler.",
            "Check the registry, try the call when known, and return the appropriate content paired with its success-or-failure flag.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "tool-calling-7",
        "title": "Answer every tool call",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## Handle a whole batch even when one call fails

            A reply requests several tools, and one of them fails. The other results still matter. Treat each operation independently, keep its identifier, and collect both successes and marked failures into the response format the next model call expects.

            One reply can hold several `tool_use` blocks. Run each call and catch
            its errors, as in the previous exercise. Answer all of the calls in one
            `user` message. That message holds one `tool_result` block per call, in
            the same order as the calls. A block for a failed call also has
            `"is_error": True`.

            ```python
            import json

            def add(a, b):
                return a + b

            ok = {"type": "tool_result", "tool_use_id": "t1", "content": str(add(a=1, b=2))}
            bad = {"type": "tool_result", "tool_use_id": "t2",
                   "content": "Error: unknown tool sub", "is_error": True}
            print(json.dumps({"role": "user", "content": [ok, bad]}))
            # {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "3"}, {"type": "tool_result", "tool_use_id": "t2", "content": "Error: unknown tool sub", "is_error": true}]}
            ```

            ```quiz
            Does one failed tool remove successful results from the batch?
            - [x] No :: Each operation keeps its own result and status.
            - [ ] Yes :: That would discard useful outcomes from unrelated calls.
            ```

            `content` is always text: keep a string result unchanged, and convert any
            other result with `json.dumps(...)`. Successful blocks have no `is_error`
            key. When the reply holds no `tool_use` blocks, there is nothing to answer.

            ```predict
            results = [{"id": "a", "failed": False}, {"id": "b", "failed": True}]
            print([r["id"] for r in results])
            print(sum(r["failed"] for r in results))
            ---
            Both results remain present, while only one contributes to the failure count.
            ```

            **Watch out:** Only failure blocks carry the error marker required here. Do not attach a failure flag to every block merely because a different operation failed.

            **In short:** Collect one correctly identified result per tool request, with failures marked individually.
        ''',
        "prompt": r'''
            Handle all the tool calls in one Anthropic-style reply.

            **Your job:** write `handle_tool_calls(reply, tools)`

            **What goes in**
            - `reply`: a dict with `"content"`: a list of blocks (`"text"` and `"tool_use"` blocks;
              tool_use blocks have `"id"`, `"name"`, `"input"`)
            - `tools`: a dict mapping tool names to functions

            **What comes out**
            - Return one message `{"role": "user", "content": [<tool_result block>, ...]}`

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
            "Combine selection, independent execution, and result formatting.",
            "One failed call should produce a marked block while the other calls still run.",
            "Select requests in order, handle each unknown name or exception, serialize its output, and return the collected blocks or the stated empty result.",
        ],
    },
    {
        "id": "tool-calling-8",
        "title": "Check argument types",
        "difficulty": 2,
        "prompt": r'''
            Models sometimes send `"3"` where you asked for a number. Check argument types
            against the schema before running a tool.

            **Your job:** write `type_errors(schema, args)`

            **What goes in**
            - `schema`: an `input_schema` dict; each property has a `"type"`:
              `"string"`, `"integer"`, `"number"`, `"boolean"`, `"array"` or `"object"`
            - `args`: the arguments dict

            **What comes out**
            - Return a list of error strings `"<name>: expected <type>"`, in the order of the keys in `args`

            **Rules**
            - Python types: string -> `str`, integer -> `int`, number -> `int` or `float`,
              boolean -> `bool`, array -> `list`, object -> `dict`.
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
            "Match JSON type names to Python value types.",
            "Integer and number checks must explicitly exclude booleans.",
            "Visit supplied arguments covered by the schema, check each supported type, and collect the required error messages in order.",
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

            **Your job:** write `to_openai_tools(tools)` and `from_openai_calls(tool_calls)`

            **What goes in**
            `to_openai_tools(tools)`
            - `tools`: a list of `{"name", "description", "input_schema"}` dicts

            **What comes out**
            - Return a list of `{"type": "function", "function": {"name": ..., "description": ..., "parameters": <input_schema>}}`, same order

            `from_openai_calls(tool_calls)`
            - `tool_calls`: a list of `{"id", "type": "function", "function": {"name", "arguments": <JSON text>}}`

            **What comes out**
            - Return a list of `{"type": "tool_use", "id": ..., "name": ..., "input": <parsed dict>}`, same order

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
            "Each adapter changes layout while preserving the information.",
            "Tool definitions and tool calls have different nested shapes.",
            "Build fresh definitions with renamed schema fields; parse each call's argument text, preserve its identifier, and translate malformed-argument errors as required.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "tool-calling-10",
        "title": "One full tool round",
        "difficulty": 3,
        "lesson": r'''
            ## Repeat the conversation with a bounded tool round

            One operation may provide enough information for a final answer, or the model may request another operation. Keep the conversation in order so the next call sees the request and its result. A fixed call limit makes the loop stop even if no final answer arrives.

            A **tool loop** repeats one round until the model stops requesting
            tools. In each round you call the model with the message list and
            append its reply. If the reply requests tools, you run them, append
            the results and start the next round. If it does not, you return its
            text. A maximum number of rounds stops a model that requests a tool
            in every reply.

            Step through the stages to see the `messages` list grow.

            ```diagram
            {"type": "flow", "title": "The messages list during one tool round", "steps": [{"label": "User question", "detail": "The list starts with one user message. Your code passes the list to the model.", "code": "messages = [\n  {\"role\": \"user\", \"content\": \"Weather in Oslo?\"},\n]"}, {"label": "Assistant reply with a tool call", "detail": "The reply has stop_reason \"tool_use\". Your code appends its content as an assistant message.", "code": "messages = [\n  {\"role\": \"user\", \"content\": \"Weather in Oslo?\"},\n  {\"role\": \"assistant\", \"content\": [{\"type\": \"tool_use\", \"id\": \"t1\", \"name\": \"get_weather\", \"input\": {\"city\": \"Oslo\"}}]},\n]"}, {"label": "Tool results", "detail": "Your code runs get_weather(city=\"Oslo\") and appends one user message that holds the tool_result block. Then it calls the model again with the same list.", "code": "messages = [\n  {\"role\": \"user\", \"content\": \"Weather in Oslo?\"},\n  {\"role\": \"assistant\", \"content\": [{\"type\": \"tool_use\", \"id\": \"t1\", ...}]},\n  {\"role\": \"user\", \"content\": [{\"type\": \"tool_result\", \"tool_use_id\": \"t1\", \"content\": \"4C in Oslo\"}]},\n]"}, {"label": "Assistant reply with text", "detail": "This reply has stop_reason \"end_turn\". Your code appends it, joins the text blocks and returns. The list now has 4 messages.", "code": "messages = [\n  {\"role\": \"user\", \"content\": \"Weather in Oslo?\"},\n  {\"role\": \"assistant\", \"content\": [{\"type\": \"tool_use\", \"id\": \"t1\", ...}]},\n  {\"role\": \"user\", \"content\": [{\"type\": \"tool_result\", \"tool_use_id\": \"t1\", \"content\": \"4C in Oslo\"}]},\n  {\"role\": \"assistant\", \"content\": [{\"type\": \"text\", \"text\": \"It is 4C in Oslo.\"}]},\n]"}], "loop": {"from": 2, "to": 1, "label": "while the reply asks for a tool"}}
            ```

            ```quiz
            What ends the loop without a final answer?
            - [x] The configured round limit :: The app must retain control over repeated model calls.
            - [ ] A tool result by itself :: A successful tool does not necessarily finish the conversation.
            ```

            ```order
            history = ["question"]
            history.append("tool request")
            history.append("tool result")
            print(history)
            ---
            The request precedes the result that answers it.
            ```

            **Watch out:** The fake model returns prepared data and does not think or execute functions. The loop tests your ordering and limits, not whether a real model will solve a task.

            **In short:** Preserve the conversation, answer requested tools, and bound how many model rounds can run.
        ''',
        "prompt": r'''
            Run a complete tool-calling conversation against a (fake) Anthropic-style model.

            **Your job:** write `chat_with_tools(model, tools, question, max_rounds=5)`

            **What goes in**
            - `model`: a function `model(messages)` that returns a reply dict
              `{"stop_reason": ..., "content": [blocks]}` (Anthropic shape)
            - `tools`: a dict mapping tool names to functions
            - `question`: the user's text
            - `max_rounds`: the maximum number of model calls

            **What comes out**
            - Return a tuple `(answer, messages)`: the final text and the full message list

            **Rules**
            - The starting conversation contains one user message whose content is the supplied question.
            - Each round: call `model(messages)`, then append `{"role": "assistant", "content": reply["content"]}`.
            - If `reply["stop_reason"] == "tool_use"`: run every `tool_use` block (in order) and append ONE
              `{"role": "user", "content": [tool_result blocks]}` message, then go to the next round.
              Tool result blocks follow the same rules as "Answer every tool call" (string unchanged,
              else `json.dumps`; unknown tool / exception -> `"Error: ..."` content with `"is_error": True`).
            - Otherwise: `answer` is the `text` of all `"text"` blocks joined with `""`; return `(answer, messages)`.
            - If the model has been called `max_rounds` times and still wants a tool, raise
              `RuntimeError` with the message `"too many tool rounds"` (do not call it again).
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
            "Keep the model reply in history before supplying its tool results.",
            "Each round either finishes with text or adds every requested result for another call.",
            "Call within the limit, append the reply, return final text when finished, otherwise run and append results, and raise if no final reply arrives in time.",
        ],
    },
]
