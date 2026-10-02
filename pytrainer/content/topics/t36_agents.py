TOPIC = {
    "id": "agents",
    "title": "Agents",
    "track": "agents",
    "order": 1,
    "requires": ["tool-calling", "observability"],
    "summary": """
        The agent loop (think, act, observe): stop conditions and max steps, a tool registry,
        memory, an audit log of every action, recovering from tool errors, budgets and human
        approval for risky tools - all driven by scripted fake models.
    """,
    "concepts": ["agent loop", "think-act-observe", "stop conditions", "max steps",
                 "tool registry", "observations", "memory", "audit log", "tool errors",
                 "budgets", "human approval", "scripted fake model", "workflows vs agents"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["agent", "agent loop", "tool", "registry", "max steps", "stop condition",
                 "observation", "memory", "audit log", "budget", "approval", "fake model",
                 "workflow", "stop_reason"],
    "cards": [
        {
            "syntax": "result = tools[name](**args)",
            "explain": "Runs a tool from the registry. tools[name] is the function and **args passes the dict as keyword arguments.",
            "example": r'''
                tools = {"add": lambda a, b: a + b}
                name, args = "add", {"a": 2, "b": 3}
                print(tools[name](**args))
                # 5
            ''',
        },
        {
            "syntax": "for step in range(1, max_steps + 1):",
            "explain": "The agent loop. It calls the model at most max_steps times and ends early on a final reply.",
            "example": r'''
                script = iter([{"type": "tool"}, {"type": "final", "text": "5"}])
                for step in range(1, 4):
                    reply = next(script)
                    if reply["type"] == "final":
                        print(step, reply["text"])
                        break
                # 2 5
            ''',
        },
        {
            "syntax": '{"role": "tool", "name": name, "content": str(result)}',
            "explain": "The observation message. Append it after a tool call so the next model call receives the result as text.",
            "example": r'''
                messages = [{"role": "user", "content": "2 + 3?"}]
                obs = {"role": "tool", "name": "add", "content": str(5)}
                messages.append(obs)
                print(len(messages), messages[-1])
                # 2 {'role': 'tool', 'name': 'add', 'content': '5'}
            ''',
        },
        {
            "syntax": 'f"error: {type(e).__name__}: {e}"',
            "explain": "Turns a tool exception into an error string for the model, so the loop keeps running.",
            "example": r'''
                try:
                    result = 1 / 0
                except Exception as e:
                    result = f"error: {type(e).__name__}: {e}"
                print(result)
                # error: ZeroDivisionError: division by zero
            ''',
        },
        {
            "syntax": "used.get(key, 0) >= limits[key]",
            "explain": "Budget check. A limit is reached when the amount used is greater than or equal to it.",
            "example": r'''
                used = {"steps": 4, "tokens": 900}
                limits = {"steps": 5, "tokens": 800}
                for key in limits:
                    print(key, used.get(key, 0) >= limits[key])
                # steps False
                # tokens True
            ''',
        },
        {
            "syntax": "if name in risky and not approve(name, args):",
            "explain": "Human approval. A risky tool runs only when approve returns True. approve is not called for other tools.",
            "example": r'''
                risky = {"send_email"}
                def approve(name, args):
                    return False
                name, args = "send_email", {"to": "ada@example.com"}
                if name in risky and not approve(name, args):
                    print("denied:", name)
                # denied: send_email
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: agents

### Agents

An **agent** is a loop in your code that calls a model and runs tools. On each pass the
model returns one of two things: a request to run a tool, or a final answer. Your code runs
the tool and adds the result to the messages, so the next model call receives it.

```python
script = iter([
    {"type": "tool", "tool": "add", "args": {"a": 2, "b": 3}},
    {"type": "final", "text": "2 + 3 is 5"},
])

def model(messages):
    return next(script)

tools = {"add": lambda a, b: a + b}
messages = [{"role": "user", "content": "What is 2 + 3?"}]
max_steps = 5
answer, stop_reason = None, "max_steps"
for step in range(1, max_steps + 1):
    reply = model(messages)
    if reply["type"] == "final":
        answer, stop_reason = reply["text"], "final"
        break
    name, args = reply["tool"], reply["args"]
    result = tools[name](**args)
    messages.append({"role": "assistant", "tool": name, "args": args})
    messages.append({"role": "tool", "name": name, "content": str(result)})
    print(step, name, args, "->", result)
    # 1 add {'a': 2, 'b': 3} -> 5
print(stop_reason, answer, step)
# final 2 + 3 is 5 2
print(len(messages))
# 3
```

`iter(...)` makes an iterator, which hands out the list items one at a time. Each
`next(script)` call returns the next reply. `tools[name]` is the function stored under the tool name. `(**args)` calls it with the dict
`args` unpacked into keyword arguments, so the call here is `add(a=2, b=3)`.

The first pass runs the tool and appends two messages, so the list ends with 3 messages. The
second pass gets the final reply, so `step` is 2 when `break` ends the loop.

The three parts of one pass are usually named think (call the model), act (run the tool)
and observe (append the result). Click each stage to see the code that runs there.

```diagram
{"type":"flow","title":"One pass of the agent loop","steps":[
  {"label":"Start the history","detail":"Before the loop, the message list holds one message: the user's task.","code":"messages = [{\"role\": \"user\", \"content\": \"What is 2 + 3?\"}]"},
  {"label":"Check the step limit","detail":"The for loop produces step numbers from 1 to max_steps. When they are used up, the loop ends and stop_reason stays \"max_steps\".","code":"for step in range(1, max_steps + 1):"},
  {"label":"Call the model","detail":"The model receives the whole message list and returns one reply dict.","code":"reply = model(messages)"},
  {"label":"Check the reply type","detail":"A reply with type \"final\" holds the answer, so break ends the loop. A reply with type \"tool\" continues to the next stage.","code":"if reply[\"type\"] == \"final\":\n    answer, stop_reason = reply[\"text\"], \"final\"\n    break"},
  {"label":"Run the tool","detail":"The tool name is the key into the tools dict. The args dict is unpacked into keyword arguments.","code":"name, args = reply[\"tool\"], reply[\"args\"]\nresult = tools[name](**args)"},
  {"label":"Append the observation","detail":"The request and the result are appended to the message list. The result is converted to a string. The next model call receives both.","code":"messages.append({\"role\": \"assistant\", \"tool\": name, \"args\": args})\nmessages.append({\"role\": \"tool\", \"name\": name, \"content\": str(result)})"}
],"loop":{"from":5,"to":1,"label":"while the reply is a tool request and steps remain"}}
```

### Reply and message shapes

This chapter uses two reply shapes. A **tool request** is
`{"type": "tool", "tool": "search", "args": {"q": "..."}}`. A **final answer** is
`{"type": "final", "text": "..."}`.

The message list starts with `{"role": "user", "content": task}`. Each tool call adds two
messages: `{"role": "assistant", "tool": name, "args": args}` and
`{"role": "tool", "name": name, "content": str(result)}`.

### Stop conditions

A **stop condition** is a test that ends the loop. The common ones are a final answer,
`max_steps` reached, a budget reached, and too many errors in a row. Return the reason
with the result, for example as `stop_reason`.

### Tool registry and tool errors

A **tool registry** is a dict that maps each tool name to a function. `tools[name](**args)`
gets the function and calls it with the dict `args` unpacked into keyword arguments.

An unknown name or an exception must not end the loop. Turn each one into an
**observation**: a string that goes back to the model in the next call.

```python
def divide(a, b):
    return a / b

tools = {"divide": divide}
requests = [("divide", {"a": 1, "b": 0}), ("fly", {}), ("divide", {"a": 6, "b": 3})]
for name, args in requests:
    if name not in tools:
        result = f"error: unknown tool {name}"
    else:
        try:
            result = tools[name](**args)
        except Exception as e:
            result = f"error: {type(e).__name__}: {e}"
    print(str(result))
# error: ZeroDivisionError: division by zero
# error: unknown tool fly
# 2.0
```

### Audit log

An **audit log** is a list with one dict per action: `step`, `tool`, `args` and `result` or
`status`. You read it to find out which tools the agent ran and what each one returned.

### Memory

An agent's **memory** is the data your code sends to the model on every call. The model keeps
nothing between calls. The message list is the first part of the memory. It must fit in the
context window (the most text a model accepts in one call), so old messages are dropped.
Values that must stay available are stored separately as **facts** and sent as a system
message on every call.

```python
messages = [
    {"role": "user", "content": "My name is Ada."},
    {"role": "assistant", "content": "Hello Ada."},
    {"role": "user", "content": "What is 2 + 3?"},
]
facts = {"name": "Ada"}
recent = messages[-2:]
system = {"role": "system", "content": "Facts: name=" + facts["name"]}
for m in [system] + recent:
    print(m["role"], "|", m["content"])
# system | Facts: name=Ada
# assistant | Hello Ada.
# user | What is 2 + 3?
```

### Budgets and human approval

A **budget** is a limit on steps, tokens or cost. A limit is reached when the amount used
is greater than or equal to it. Check budgets on every pass, before doing more work.

**Human approval** means a person must agree before a risky tool runs (send email, delete,
pay). The code calls an `approve(name, args)` function first. If it returns `False`, the
tool does not run, the observation is a "denied" string, and the loop continues.

```python
used = {"steps": 4, "tokens": 900}
limits = {"steps": 5, "tokens": 800}
for key in limits:
    print(key, used.get(key, 0) >= limits[key])
# steps False
# tokens True

risky = {"send_email"}

def approve(name, args):
    return False

name, args = "send_email", {"to": "ada@example.com"}
if name in risky and not approve(name, args):
    print(f"denied: {name}")
# denied: send_email
```

### Scripted fake model

A **scripted fake model** is a function that returns pre-written replies in order, one per
call. The `model` function in the first example is one. It lets you test agent code with
no network and no randomness.

### Workflows and agents

In a **workflow**, your code fixes the order of the steps. One example is a **prompt chain**:
each step is one model call that receives the previous step's output. A **gate** is a Python
check that runs after a step and stops the chain when it returns `False`. In an agent, the
model's reply selects the next step. Anthropic's advice is to use the simplest design that
works.

### Common mistakes

- A loop with no `max_steps` can run forever, and every model call costs money.
- If you do not append the observation, the model gets the same messages again and can
  return the same tool request on every pass.
- Message content is text. Convert the tool result with `str(result)`.
- Copy an input that you must not change before you modify it.
'''

EXERCISES = [
    {
        "id": "agents-s1",
        "title": "Trace the loop",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The agent loop

            An **agent** is a loop in your code that calls a model and runs tools. The model
            does not run anything itself. It returns data, and your code acts on that data.

            In this chapter every model reply is a dict with a `"type"` key. A **tool request**
            has the type `"tool"` and names a tool and its arguments. A **final answer** has
            the type `"final"` and holds the answer text.

            The program below uses two pre-written replies in place of real model calls. The
            loop reads one reply per pass. For a tool request it prints the tool name. For a
            final answer it prints the text, and `break` ends the loop.

            ```python
            tool_reply = {"type": "tool", "tool": "search", "args": {"q": "France"}}
            final_reply = {"type": "final", "text": "Paris"}
            for reply in [tool_reply, final_reply]:
                if reply["type"] == "final":
                    print("answer:", reply["text"])
                    break
                print("calling", reply["tool"])
            # calling search
            # answer: Paris
            ```

            Step through the program to see which lines run for each reply.

            ```diagram
            {"type": "trace", "title": "Two replies through the loop", "code": ["tool_reply = {\"type\": \"tool\", \"tool\": \"search\", \"args\": {\"q\": \"France\"}}", "final_reply = {\"type\": \"final\", \"text\": \"Paris\"}", "for reply in [tool_reply, final_reply]:", "    if reply[\"type\"] == \"final\":", "        print(\"answer:\", reply[\"text\"])", "        break", "    print(\"calling\", reply[\"tool\"])"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}"}, "out": ""},
              {"line": 3, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}"}, "out": ""},
              {"line": 4, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}"}, "out": ""},
              {"line": 7, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}"}, "out": ""},
              {"line": 3, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}"}, "out": "calling search\n"},
              {"line": 4, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'final', 'text': 'Paris'}"}, "out": "calling search\n"},
              {"line": 5, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'final', 'text': 'Paris'}"}, "out": "calling search\n"},
              {"line": 6, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'final', 'text': 'Paris'}"}, "out": "calling search\nanswer: Paris\n"},
              {"line": null, "vars": {"tool_reply": "{'type': 'tool', 'tool': 'search', 'args': {'q': 'France'}}", "final_reply": "{'type': 'final', 'text': 'Paris'}", "reply": "{'type': 'final', 'text': 'Paris'}"}, "out": "calling search\nanswer: Paris\n"}
            ]}
            ```

            This is the **agent loop**. Its three parts have standard names: *think* (call the
            model), *act* (run the tool) and *observe* (read the result). Then the loop repeats.

            `break` ends the loop at once. Any reply after the final answer is never read.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            replies = [
                {"type": "tool", "tool": "add", "args": {"a": 2, "b": 3}},
                {"type": "final", "text": "The answer is 5"},
                {"type": "tool", "tool": "add", "args": {"a": 1, "b": 1}},
            ]
            tools = {"add": lambda a, b: a + b}
            for step, reply in enumerate(replies, start=1):
                if reply["type"] == "final":
                    print(step, "final:", reply["text"])
                    break
                result = tools[reply["tool"]](**reply["args"])
                print(step, "tool", reply["tool"], "->", result)
        ''',
        "solution": r'''
            1 tool add -> 5
            2 final: The answer is 5
        ''',
        "explanation": r'''
            `enumerate(replies, start=1)` numbers the replies from 1. Reply 1 is a tool request:
            `tools["add"](a=2, b=3)` returns `5`, and the line `1 tool add -> 5` is printed.
            Reply 2 has the type `"final"`, so its text is printed and `break` ends the loop.
            The third reply is never read.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Walk the list one reply at a time and track the step number enumerate gives you.",
            "A tool reply runs the tool and prints a line; a final reply prints and then stops the loop.",
            "Step 1: run add with a=2 and b=3 and print the line. Step 2: print the final text, then break - nothing else runs.",
        ],
    },
    {
        "id": "agents-s2",
        "title": "Is the agent done?",
        "difficulty": 0,
        "lesson": r'''
            ## Stop conditions

            A **stop condition** is a test that tells the agent loop when to end. A loop with
            no stop condition calls the model forever.

            The first stop condition is the reply type. Each reply is a dict with a `"type"`
            key. The value `"tool"` means the loop must run a tool and continue. The value
            `"final"` means the model has returned its answer and the loop must end.

            ```python
            reply = {"type": "final", "text": "42"}
            print(reply["type"])
            # final
            print(reply["type"] == "final")
            # True
            print(reply["type"] == "tool")
            # False
            ```

            `==` compares two values and produces `True` or `False`. A function can return
            that result directly. No `if` statement is needed.

            ```python
            def is_tool(reply):
                return reply["type"] == "tool"

            print(is_tool({"type": "tool", "tool": "search", "args": {"q": "x"}}))
            # True
            ```
        ''',
        "prompt": r'''
            The loop needs to know when the model has finished. Replace the `___`.

            **Write:** `is_final(reply)`

            - `reply`: a dict like `{"type": "final", "text": "Paris"}` or
              `{"type": "tool", "tool": "search", "args": {"q": "x"}}`
            - **Returns:** `True` if the reply's `"type"` is `"final"`, otherwise `False`

            **Examples**
            ```python
            is_final({"type": "final", "text": "Paris"})                     # returns True
            is_final({"type": "tool", "tool": "search", "args": {"q": "x"}})  # returns False
            ```
        ''',
        "starter": r'''
            def is_final(reply):
                return reply["type"] == ___
        ''',
        "tests": r'''
            from solution import is_final

            def test_final_reply_is_final():
                assert is_final({"type": "final", "text": "Paris"}) is True

            def test_tool_reply_is_not_final():
                got = is_final({"type": "tool", "tool": "search", "args": {"q": "x"}})
                assert got is False, f"got {got!r}"

            def test_final_with_empty_text_is_still_final():
                assert is_final({"type": "final", "text": ""}) is True
        ''',
        "solution": r'''
            def is_final(reply):
                return reply["type"] == "final"
        ''',
        "hints": [
            "Look at the value stored under the \"type\" key of the reply.",
            "Compare that value with the text that means 'the model is done'.",
            "Replace ___ with the string \"final\" (in quotes) so the comparison is True only for final replies.",
        ],
    },
    {
        "id": "agents-s3",
        "title": "Fix: one step too many",
        "difficulty": 0,
        "lesson": r'''
            ## Max steps

            A model can return tool requests on every call and never return a final answer.
            Every model call costs money, so the loop needs a second stop condition.
            **Max steps** is a limit on the number of steps the loop may run.

            `step` counts the steps that have already run. The agent must stop when `step`
            equals the limit, not one step later.

            ```python
            max_steps = 3
            for step in [2, 3, 4]:
                print(step, step >= max_steps, step > max_steps)
            # 2 False False
            # 3 True False
            # 4 True True
            ```

            `step >= max_steps` is `True` when `step` has reached the limit or passed it.
            `step > max_steps` is `True` only after `step` has passed it. The two differ when
            `step` is `3`. Using the wrong one is an **off-by-one** bug: the loop runs one
            time too many or one time too few.

            The agent stops when it is done or when it is out of steps. `or` produces a true
            result when at least one side is true.

            ```python
            done = False
            out_of_steps = True
            print(done or out_of_steps)
            # True
            ```
        ''',
        "prompt": r'''
            The loop asks `should_stop` after every step. The agent is running one step too
            many. Find and fix the bug.

            **Write:** `should_stop(step, max_steps, reply)`

            - `step`: int, how many steps have already run (starts at 1), e.g. `3`
            - `max_steps`: int, the limit, e.g. `3`
            - `reply`: the latest model reply dict, e.g. `{"type": "tool", ...}`
            - **Returns:** `True` if the reply's `"type"` is `"final"` **or** `step` has reached
              `max_steps`; otherwise `False`

            **Examples**
            ```python
            should_stop(3, 3, {"type": "tool"})     # returns True  (limit reached)
            should_stop(2, 3, {"type": "tool"})     # returns False
            should_stop(1, 3, {"type": "final"})    # returns True  (done)
            ```
        ''',
        "starter": r'''
            def should_stop(step, max_steps, reply):
                return reply["type"] == "final" or step > max_steps
        ''',
        "tests": r'''
            from solution import should_stop

            def test_stops_when_limit_is_reached():
                assert should_stop(3, 3, {"type": "tool"}) is True

            def test_keeps_going_below_the_limit():
                assert should_stop(2, 3, {"type": "tool"}) is False

            def test_stops_on_final_reply_early():
                assert should_stop(1, 3, {"type": "final"}) is True

            def test_stops_past_the_limit_too():
                assert should_stop(5, 3, {"type": "tool"}) is True
        ''',
        "solution": r'''
            def should_stop(step, max_steps, reply):
                return reply["type"] == "final" or step >= max_steps
        ''',
        "hints": [
            "The final-reply part is fine. Look at how step is compared with max_steps.",
            "When step equals max_steps the agent has used all its steps, so it must stop.",
            "Change the > comparison to >= so reaching the limit counts as a reason to stop.",
        ],
    },
    {
        "id": "agents-s4",
        "title": "Call a tool by name",
        "difficulty": 0,
        "lesson": r'''
            ## Tool registry

            A **tool registry** is a dict that maps each tool name to a function. The model
            sends the tool name as a string. Your code uses that string as the key to get
            the function.

            ```python
            def weather(city, unit="C"):
                return f"18{unit} in {city}"

            tools = {"weather": weather}
            fn = tools["weather"]
            print(fn("Paris"))
            # 18C in Paris
            ```

            The model sends the arguments as a dict too. In a call, `**` unpacks a dict into
            keyword arguments. Each key becomes a parameter name.

            ```python
            def weather(city, unit="C"):
                return f"18{unit} in {city}"

            args = {"city": "Paris", "unit": "F"}
            print(weather(**args))
            # 18F in Paris
            print(weather(city="Paris", unit="F"))
            # 18F in Paris
            ```

            In the functions chapter, `**kwargs` in a `def` collected keyword arguments into
            a dict. `**args` in a call does the reverse. An empty dict unpacks to no
            arguments. A key that is not a parameter name raises `TypeError`.
        ''',
        "prompt": r'''
            The model asked for a tool by name, with its arguments as a dict. Run it.

            **Write:** `call_tool(tools, name, args)`

            - `tools`: a dict mapping tool names to functions, e.g. `{"add": add}`
            - `name`: str, the tool to run, e.g. `"add"`
            - `args`: dict of keyword arguments, e.g. `{"a": 2, "b": 3}`
            - **Returns:** whatever the tool function returns

            **Rules**
            - Pass the arguments by name (the dict keys are the parameter names).
            - An empty `args` dict means "call with no arguments".

            **Examples**
            ```python
            def add(a, b): return a + b
            def now(): return "12:00"
            call_tool({"add": add, "now": now}, "add", {"a": 2, "b": 3})   # returns 5
            call_tool({"add": add, "now": now}, "now", {})                 # returns "12:00"
            ```
        ''',
        "starter": r'''
            def call_tool(tools, name, args):
                ...
        ''',
        "tests": r'''
            from solution import call_tool

            def add(a, b):
                return a + b

            def now():
                return "12:00"

            def minus(a, b):
                return a - b

            def test_runs_add_with_args():
                assert call_tool({"add": add}, "add", {"a": 2, "b": 3}) == 5

            def test_runs_tool_with_no_args():
                assert call_tool({"add": add, "now": now}, "now", {}) == "12:00"

            def test_args_are_passed_by_name():
                got = call_tool({"minus": minus}, "minus", {"b": 1, "a": 10})
                assert got == 9, f"got {got!r} - were the arguments passed by name?"
        ''',
        "solution": r'''
            def call_tool(tools, name, args):
                return tools[name](**args)
        ''',
        "hints": [
            "First look the function up in the dict, then call it.",
            "The args dict must become keyword arguments - unpack it with ** when you call.",
            "Get tools[name], call it with **args, and return what it gives back.",
        ],
    },
    {
        "id": "agents-s5",
        "title": "Write it in the log",
        "difficulty": 0,
        "lesson": r'''
            ## Audit log

            An **audit log** is a record of every action the agent took, in order. An audit is
            an official check of records. When an agent gives a wrong answer, you read the log
            to see which tools it ran and what each one returned.

            In code, the log is a list of dicts. Each dict is one entry. `append` adds an
            entry to the end of the list.

            ```python
            log = []
            log.append({"step": 1, "tool": "search", "args": {"q": "tea"}, "result": "3 hits"})
            log.append({"step": 2, "tool": "read", "args": {"id": 7}, "result": "Tea is..."})
            for entry in log:
                print(entry["step"], entry["tool"], entry["result"])
            # 1 search 3 hits
            # 2 read Tea is...
            print(len(log), "actions")
            # 2 actions
            ```

            `append` changes the list in place and returns `None`.

            ```python
            log = []
            returned = log.append({"step": 1})
            print(returned)
            # None
            print(log)
            # [{'step': 1}]
            ```

            A function that must return the log returns the list, not the result of `append`.
        ''',
        "prompt": r'''
            Record one agent action in the audit log.

            **Write:** `record(log, step, tool, args, result)`

            - `log`: a list of earlier entries (may be empty)
            - `step`: int, e.g. `1`
            - `tool`: str, the tool name, e.g. `"search"`
            - `args`: dict, the tool arguments, e.g. `{"q": "tea"}`
            - `result`: whatever the tool returned, e.g. `"3 hits"`
            - **Returns:** the same `log` list, with one new entry added at the end

            **Rules**
            - The new entry is a dict with exactly the keys `"step"`, `"tool"`, `"args"`, `"result"`.
            - Add to the list you were given (don't build a new list); earlier entries stay.

            **Examples**
            ```python
            log = []
            record(log, 1, "search", {"q": "tea"}, "3 hits")
            # returns [{"step": 1, "tool": "search", "args": {"q": "tea"}, "result": "3 hits"}]
            # and log itself now holds that one entry
            ```
        ''',
        "starter": r'''
            def record(log, step, tool, args, result):
                ...
        ''',
        "tests": r'''
            from solution import record

            def test_adds_entry_with_exact_keys():
                got = record([], 1, "search", {"q": "tea"}, "3 hits")
                assert got == [{"step": 1, "tool": "search", "args": {"q": "tea"}, "result": "3 hits"}], f"got {got!r}"

            def test_returns_the_same_list_object():
                log = []
                got = record(log, 1, "search", {"q": "tea"}, "3 hits")
                assert got is log, "return the list you were given"
                assert len(log) == 1

            def test_keeps_earlier_entries_and_appends_at_end():
                log = [{"step": 1, "tool": "a", "args": {}, "result": 1}]
                record(log, 2, "b", {"x": 1}, 42)
                assert len(log) == 2 and log[0]["tool"] == "a" and log[1]["tool"] == "b"
                assert log[1]["result"] == 42
        ''',
        "solution": r'''
            def record(log, step, tool, args, result):
                log.append({"step": step, "tool": tool, "args": args, "result": result})
                return log
        ''',
        "hints": [
            "Build one dict for the new entry, then add it to the end of the list.",
            "Use the list method that adds an item at the end - it changes the list in place.",
            "Create a dict with keys step, tool, args, result; append it to log; then return log (not the result of append).",
        ],
    },
    {
        "id": "agents-s6",
        "title": "Errors don't stop the agent",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Tool errors

            Tools fail often: wrong arguments, missing data, a timeout. An exception that no
            code catches ends the program, and the agent loop ends with it. To keep the loop
            running, put the tool call inside `try` / `except`.

            ```python
            def divide(a, b):
                return a / b

            for b in [2, 0]:
                try:
                    print("ok:", divide(10, b))
                except ZeroDivisionError as e:
                    print("tool failed:", e)
            print("still running")
            # ok: 5.0
            # tool failed: division by zero
            # still running
            ```

            `divide(10, 0)` raises `ZeroDivisionError`. Python skips the rest of the `try`
            block and runs the `except` block. The loop and the last `print` still run.
            Step through the program to see the jump from line 2 to line 7.

            ```diagram
            {"type": "trace", "title": "A tool error caught inside the loop", "code": ["def divide(a, b):", "    return a / b", "", "for b in [2, 0]:", "    try:", "        print(\"ok:\", divide(10, b))", "    except ZeroDivisionError as e:", "        print(\"tool failed:\", e)", "print(\"still running\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 4, "vars": {}, "out": ""},
              {"line": 5, "vars": {"b": "2"}, "out": ""},
              {"line": 6, "vars": {"b": "2"}, "out": ""},
              {"line": 2, "vars": {"a": "10", "b": "2"}, "out": ""},
              {"line": 4, "vars": {"b": "2"}, "out": "ok: 5.0\n"},
              {"line": 5, "vars": {"b": "0"}, "out": "ok: 5.0\n"},
              {"line": 6, "vars": {"b": "0"}, "out": "ok: 5.0\n"},
              {"line": 2, "vars": {"a": "10", "b": "0"}, "out": "ok: 5.0\n"},
              {"line": 7, "vars": {"b": "0"}, "out": "ok: 5.0\n"},
              {"line": 8, "vars": {"b": "0", "e": "ZeroDivisionError('division by zero')"}, "out": "ok: 5.0\n"},
              {"line": 4, "vars": {"b": "0"}, "out": "ok: 5.0\ntool failed: division by zero\n"},
              {"line": 9, "vars": {"b": "0"}, "out": "ok: 5.0\ntool failed: division by zero\n"},
              {"line": null, "vars": {"b": "0"}, "out": "ok: 5.0\ntool failed: division by zero\nstill running\n"}
            ]}
            ```

            `type(e).__name__` is the name of the exception's class as a string. You use it
            when you report an error back to the model.

            ```python
            try:
                int("abc")
            except ValueError as e:
                print(type(e).__name__)
                # ValueError
                print(e)
                # invalid literal for int() with base 10: 'abc'
            ```
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            def lookup(city):
                temps = {"Paris": 18}
                return temps[city]

            for city in ["Paris", "Mars"]:
                try:
                    print(city, lookup(city))
                except KeyError as e:
                    print(city, "error:", type(e).__name__)
            print("agent keeps going")
        ''',
        "solution": r'''
            Paris 18
            Mars error: KeyError
            agent keeps going
        ''',
        "explanation": r'''
            `"Paris"` is in the dict, so it prints `Paris 18`. `"Mars"` is not, so `temps[city]`
            raises `KeyError`; the `except` catches it and prints the class name. Because the
            error was caught, the loop and the last `print` still run.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Check each city against the dict inside lookup.",
            "A missing key raises KeyError, which the except block catches - the program does not crash.",
            "Paris prints its temperature. Mars goes to the except line and prints the error class name. Then the final print runs.",
        ],
    },
    {
        "id": "agents-1",
        "title": "A scripted fake model",
        "difficulty": 1,
        "lesson": r'''
            ## Scripted fake model

            A real model is slow, costs money and can return a different reply on each call.
            A test needs the same replies on every run. A **scripted fake model** is a function
            that returns pre-written replies in order, one per call.

            The function must keep count of the replies it has already returned. A closure
            does this. A closure is a function defined inside another function that keeps
            access to the outer function's variables after the outer function has returned.

            ```python
            def make_counter():
                calls = [0]
                def count():
                    calls[0] += 1
                    return calls[0]
                return count

            c = make_counter()
            print(c(), c(), c())
            # 1 2 3
            d = make_counter()
            print(d(), c())
            # 1 4
            ```

            `calls` is a list with one item, and `count` changes that item on every call.
            Each call to `make_counter` creates a new `calls` list, so `d` starts at 1 while
            `c` continues from 3.

            An iterator also works. `iter(items)` creates an iterator over a list. `next(it)`
            returns the next item, and raises `StopIteration` when no items are left.

            ```python
            it = iter(["a", "b"])
            print(next(it))
            # a
            print(next(it))
            # b
            ```
        ''',
        "prompt": r'''
            Build the fake model every test in this chapter relies on.

            **Write:** `make_scripted_model(replies)`

            - `replies`: a list of reply dicts, e.g.
              `[{"type": "tool", "tool": "add", "args": {"a": 1, "b": 2}}, {"type": "final", "text": "3"}]`
            - **Returns:** a function `model(messages)` that returns the next reply from the list
              each time it is called (first call -> first reply, and so on)

            **Rules**
            - `model` accepts one argument, `messages`, and ignores it.
            - When all replies have been used, calling `model` again raises
              `RuntimeError("script exhausted")`.
            - Don't change the `replies` list.
            - Each call to `make_scripted_model` makes an independent model that starts at the first reply.

            **Examples**
            ```python
            model = make_scripted_model([{"type": "final", "text": "hi"}])
            model([])     # returns {"type": "final", "text": "hi"}
            model([])     # raises RuntimeError("script exhausted")
            ```
        ''',
        "starter": r'''
            def make_scripted_model(replies):
                def model(messages):
                    ...
                return model
        ''',
        "tests": r'''
            from solution import make_scripted_model

            R1 = {"type": "tool", "tool": "add", "args": {"a": 1, "b": 2}}
            R2 = {"type": "final", "text": "3"}

            def test_returns_replies_in_order():
                model = make_scripted_model([R1, R2])
                assert model([]) == R1
                assert model([{"role": "tool", "content": "3"}]) == R2

            def test_raises_runtime_error_when_exhausted():
                model = make_scripted_model([R2])
                model([])
                try:
                    model([])
                except RuntimeError as e:
                    assert str(e) == "script exhausted", f"message was {str(e)!r}"
                else:
                    raise AssertionError("expected RuntimeError after the last reply")

            def test_does_not_change_the_replies_list():
                replies = [R1, R2]
                model = make_scripted_model(replies)
                model([]); model([])
                assert replies == [R1, R2] and len(replies) == 2

            def test_two_models_are_independent():
                a = make_scripted_model([R1, R2])
                b = make_scripted_model([R1, R2])
                a([])
                assert b([]) == R1, "a new model must start at the first reply"
                assert a([]) == R2
        ''',
        "solution": r'''
            def make_scripted_model(replies):
                position = [0]

                def model(messages):
                    if position[0] >= len(replies):
                        raise RuntimeError("script exhausted")
                    reply = replies[position[0]]
                    position[0] += 1
                    return reply

                return model
        ''',
        "hints": [
            "The inner function must remember how many replies it has already given - a closure over a variable in the outer function.",
            "Keep a position counter (for example in a one-item list) or an iterator, created inside make_scripted_model so each model has its own.",
            "In make_scripted_model create position = [0]. In model: if position[0] >= len(replies) raise RuntimeError(\"script exhausted\"); otherwise take replies[position[0]], add 1 to the counter, and return the reply.",
        ],
    },
    {
        "id": "agents-2",
        "title": "Tool errors become observations",
        "difficulty": 1,
        "lesson": r'''
            ## Observations

            An **observation** is the text your code sends back to the model after a tool
            call. The model receives it in the next call. When a tool fails, the observation
            is an error message, and the model can then return a different request.

            Two things can go wrong. The model can ask for a name that is not in the registry.
            The tool can also raise an exception while it runs.

            ```python
            def half(n):
                return n / 2

            tools = {"half": half}
            for name, args in [("half", {"n": 8}), ("double", {"n": 2}), ("half", {"x": 1})]:
                if name not in tools:
                    print(f"error: unknown tool {name}")
                    continue
                try:
                    print(tools[name](**args))
                except Exception as e:
                    print(f"error: {type(e).__name__}: {e}")
            # 4.0
            # error: unknown tool double
            # error: TypeError: half() got an unexpected keyword argument 'x'
            ```

            The `not in` test runs first, so an unknown name is never looked up or called.
            The third request passes `x`, which is not a parameter of `half`, so the call
            raises `TypeError`.

            `except Exception` catches almost every exception a tool can raise. That is
            acceptable here because the error is not hidden. It is reported to the model.
        ''',
        "prompt": r'''
            Run a tool safely: never crash, always give the model something to read.

            **Write:** `safe_call_tool(tools, name, args)`

            - `tools`: dict of name -> function
            - `name`: str, the requested tool
            - `args`: dict of keyword arguments
            - **Returns:** the tool's return value, or an error string

            **Rules**
            - If `name` is not in `tools`, return `"error: unknown tool <name>"`
              (e.g. `"error: unknown tool fly"`) without calling anything.
            - If the tool raises any exception `e`, return
              `"error: <ExceptionClassName>: <str(e)>"`, e.g. `"error: ZeroDivisionError: division by zero"`.
            - Otherwise return the tool's result unchanged (not converted to a string).

            **Examples**
            ```python
            def div(a, b): return a / b
            safe_call_tool({"div": div}, "div", {"a": 6, "b": 3})   # returns 2.0
            safe_call_tool({"div": div}, "div", {"a": 1, "b": 0})   # returns "error: ZeroDivisionError: division by zero"
            safe_call_tool({"div": div}, "fly", {})                 # returns "error: unknown tool fly"
            ```
        ''',
        "starter": r'''
            def safe_call_tool(tools, name, args):
                return tools[name](**args)
        ''',
        "tests": r'''
            from solution import safe_call_tool

            def div(a, b):
                return a / b

            def test_success_returns_raw_result():
                got = safe_call_tool({"div": div}, "div", {"a": 6, "b": 3})
                assert got == 2.0 and not isinstance(got, str), f"got {got!r}"

            def test_exception_becomes_error_string():
                got = safe_call_tool({"div": div}, "div", {"a": 1, "b": 0})
                assert got == "error: ZeroDivisionError: division by zero", f"got {got!r}"

            def test_unknown_tool_is_reported():
                got = safe_call_tool({"div": div}, "fly", {})
                assert got == "error: unknown tool fly", f"got {got!r}"

            def test_bad_arguments_are_reported_as_type_error():
                got = safe_call_tool({"div": div}, "div", {"x": 1})
                assert isinstance(got, str) and got.startswith("error: TypeError: "), f"got {got!r}"
        ''',
        "solution": r'''
            def safe_call_tool(tools, name, args):
                if name not in tools:
                    return f"error: unknown tool {name}"
                try:
                    return tools[name](**args)
                except Exception as e:
                    return f"error: {type(e).__name__}: {e}"
        ''',
        "hints": [
            "Two separate problems: a name that is not in the dict, and a tool that raises while running.",
            "Check membership with `in` before calling; wrap the call itself in try/except Exception and build the message from the caught error.",
            "If name not in tools, return the unknown-tool f-string. Otherwise try: return tools[name](**args). except Exception as e: return f\"error: {type(e).__name__}: {e}\".",
        ],
    },
    {
        "id": "agents-3",
        "title": "One turn: think, act, observe",
        "difficulty": 1,
        "lesson": r'''
            ## One turn of the loop

            The **message list** is a list of dicts that holds the task and everything that
            has happened since. The whole list is passed to the model on every call.

            One turn of the loop has three parts:

            1. Think: call `model(messages)`.
            2. Act: if the reply is a tool request, run the tool.
            3. Observe: append the request and the result to `messages`.

            ```python
            messages = [{"role": "user", "content": "What is 2 + 3?"}]
            reply = {"type": "tool", "tool": "add", "args": {"a": 2, "b": 3}}
            result = 5
            messages.append({"role": "assistant", "tool": reply["tool"], "args": reply["args"]})
            messages.append({"role": "tool", "name": reply["tool"], "content": str(result)})
            for m in messages:
                print(m)
            # {'role': 'user', 'content': 'What is 2 + 3?'}
            # {'role': 'assistant', 'tool': 'add', 'args': {'a': 2, 'b': 3}}
            # {'role': 'tool', 'name': 'add', 'content': '5'}
            ```

            Message `content` is text. `str(result)` converts the result to a string, so the
            int `5` is stored as `'5'`.

            If you skip the two appends, the next call gets the same messages as before. The
            model has no information about the tool result and can return the same request again.
        ''',
        "prompt": r'''
            Run exactly one turn of the agent loop.

            **Write:** `agent_step(model, tools, messages)`

            - `model`: a function; `model(messages)` returns a reply dict (`"type"` is `"tool"` or `"final"`)
            - `tools`: dict of name -> function
            - `messages`: the conversation so far (a list of dicts); you will add to it
            - **Returns:** the final answer text (str) if the model finished, otherwise `None`

            **Rules**
            - Call `model(messages)` exactly once, passing the `messages` list.
            - If the reply is `{"type": "final", "text": ...}`: return the text and leave `messages` unchanged.
            - If the reply is `{"type": "tool", "tool": name, "args": args}`: run `tools[name](**args)`, then
              append these two dicts to `messages` (in this order) and return `None`:
              `{"role": "assistant", "tool": name, "args": args}` and
              `{"role": "tool", "name": name, "content": str(result)}`.

            **Examples**
            ```python
            messages = [{"role": "user", "content": "2+3?"}]
            # model returns {"type": "tool", "tool": "add", "args": {"a": 2, "b": 3}}
            agent_step(model, {"add": add}, messages)   # returns None
            # messages[1:] == [{"role": "assistant", "tool": "add", "args": {"a": 2, "b": 3}},
            #                  {"role": "tool", "name": "add", "content": "5"}]
            # model returns {"type": "final", "text": "5"}
            agent_step(model, {"add": add}, messages)   # returns "5"
            ```
        ''',
        "starter": r'''
            def agent_step(model, tools, messages):
                ...
        ''',
        "tests": r'''
            from solution import agent_step

            def add(a, b):
                return a + b

            def fixed(reply, seen):
                def model(messages):
                    seen.append(messages)
                    return reply
                return model

            def test_tool_reply_appends_request_and_observation():
                seen = []
                messages = [{"role": "user", "content": "2+3?"}]
                model = fixed({"type": "tool", "tool": "add", "args": {"a": 2, "b": 3}}, seen)
                got = agent_step(model, {"add": add}, messages)
                assert got is None, f"returned {got!r} for a tool reply"
                assert messages[1:] == [
                    {"role": "assistant", "tool": "add", "args": {"a": 2, "b": 3}},
                    {"role": "tool", "name": "add", "content": "5"},
                ], f"messages: {messages!r}"

            def test_observation_content_is_a_string():
                messages = []
                agent_step(fixed({"type": "tool", "tool": "add", "args": {"a": 1, "b": 1}}, []), {"add": add}, messages)
                assert messages[-1]["content"] == "2", f"got {messages[-1]['content']!r}"

            def test_final_reply_returns_text_and_leaves_messages():
                messages = [{"role": "user", "content": "hi"}]
                got = agent_step(fixed({"type": "final", "text": "hello"}, []), {}, messages)
                assert got == "hello", f"got {got!r}"
                assert messages == [{"role": "user", "content": "hi"}]

            def test_model_is_called_once_with_the_messages_list():
                seen = []
                messages = [{"role": "user", "content": "hi"}]
                agent_step(fixed({"type": "final", "text": "x"}, seen), {}, messages)
                assert len(seen) == 1 and seen[0] is messages
        ''',
        "solution": r'''
            def agent_step(model, tools, messages):
                reply = model(messages)
                if reply["type"] == "final":
                    return reply["text"]
                name, args = reply["tool"], reply["args"]
                result = tools[name](**args)
                messages.append({"role": "assistant", "tool": name, "args": args})
                messages.append({"role": "tool", "name": name, "content": str(result)})
                return None
        ''',
        "hints": [
            "Start by calling the model once with messages and looking at the reply's type.",
            "A final reply means return its text. A tool reply means run the tool, then record two messages: what was asked and what came back.",
            "reply = model(messages). If final, return reply[\"text\"]. Else read the name and args, compute result = tools[name](**args), append the assistant dict and the tool dict (content=str(result)), then return None.",
        ],
    },
    {
        "id": "agents-4",
        "title": "Check the budget",
        "difficulty": 1,
        "lesson": r'''
            ## Budgets

            A **budget** is a limit on something the agent uses: steps, tokens or cost. The
            loop compares what it has used with each limit and stops when a limit is reached.
            A run that never produces a final answer then still has a maximum cost.

            Store the amounts used and the limits in two dicts with the same keys. Then loop
            over the limits and compare.

            ```python
            used = {"steps": 4, "tokens": 900}
            limits = {"steps": 5, "tokens": 800}
            for key in limits:
                spent = used.get(key, 0)
                print(key, spent, "/", limits[key], "reached" if spent >= limits[key] else "ok")
            # steps 4 / 5 ok
            # tokens 900 / 800 reached
            ```

            A limit is **reached** when the amount used is greater than or equal to it. A
            `for` loop over a dict visits the keys in the order they were added.

            `used.get(key, 0)` returns `0` when the key is missing, so an amount that was
            never counted is treated as zero.

            ```python
            used = {"steps": 4}
            print(used.get("cost", 0))
            # 0
            ```
        ''',
        "prompt": r'''
            Before every turn, the agent checks whether any budget is used up.

            **Write:** `check_budget(used, limits)`

            - `used`: dict of what was spent so far, e.g. `{"steps": 3, "tokens": 1200, "cost": 0.02}`
            - `limits`: dict of maximums, e.g. `{"steps": 5, "tokens": 1000}`
            - **Returns:** the name (str) of the first limit that has been reached, or `None` if none has

            **Rules**
            - A limit is reached when `used[key] >= limits[key]`.
            - Check keys in the order they appear in `limits`; return the first one reached.
            - A key missing from `used` counts as `0`.
            - Keys in `used` that have no limit are ignored.

            **Examples**
            ```python
            check_budget({"steps": 3, "tokens": 1200}, {"steps": 5, "tokens": 1000})   # returns "tokens"
            check_budget({"steps": 5, "tokens": 1200}, {"steps": 5, "tokens": 1000})   # returns "steps"
            check_budget({"steps": 1}, {"steps": 5, "cost": 0.5})                      # returns None
            ```
        ''',
        "starter": r'''
            def check_budget(used, limits):
                ...
        ''',
        "tests": r'''
            from solution import check_budget

            def test_nothing_reached_returns_none():
                assert check_budget({"steps": 1, "tokens": 10}, {"steps": 5, "tokens": 1000}) is None

            def test_returns_the_reached_limit():
                got = check_budget({"steps": 3, "tokens": 1200}, {"steps": 5, "tokens": 1000})
                assert got == "tokens", f"got {got!r}"

            def test_equal_counts_as_reached():
                got = check_budget({"cost": 0.5}, {"cost": 0.5})
                assert got == "cost", f"got {got!r}"

            def test_first_in_limits_order_wins():
                got = check_budget({"steps": 5, "tokens": 1200}, {"steps": 5, "tokens": 1000})
                assert got == "steps", f"got {got!r}"
                got = check_budget({"steps": 5, "tokens": 1200}, {"tokens": 1000, "steps": 5})
                assert got == "tokens", f"got {got!r}"

            def test_missing_used_key_counts_as_zero():
                assert check_budget({"steps": 1}, {"steps": 5, "cost": 0.5}) is None
                assert check_budget({}, {"steps": 0}) == "steps"
        ''',
        "solution": r'''
            def check_budget(used, limits):
                for key, limit in limits.items():
                    if used.get(key, 0) >= limit:
                        return key
                return None
        ''',
        "hints": [
            "Loop over the limits dict - its order decides which limit is reported first.",
            "For each limit, look up how much was used (default 0) and compare with >=.",
            "for key, limit in limits.items(): if used.get(key, 0) >= limit: return key. After the loop, return None.",
        ],
    },
    {
        "id": "agents-5",
        "title": "Workflow: a gated chain",
        "difficulty": 1,
        "research": {
            "note": "Read Anthropic's \"Building effective agents\" - especially the difference between "
                    "*workflows* and *agents*, and the **prompt chaining** pattern with its \"gate\". "
                    "Then come back and build a tiny chain.",
            "links": [
                {"title": "Building effective agents - Anthropic",
                 "url": "https://www.anthropic.com/engineering/building-effective-agents"},
            ],
        },
        "lesson": r'''
            ## Workflows and prompt chaining

            A **workflow** is a fixed sequence of steps that you wrote in code. Your code
            decides which step runs next. In an agent, the model's reply decides that.

            **Prompt chaining** is a workflow where each step is one LLM call and each step
            receives the previous step's output: outline, then draft, then polish. A **gate**
            is a plain Python check that runs between steps and returns `True` or `False`.
            When it returns `False`, the chain stops.

            ```python
            steps = [str.strip, str.upper]
            gate = lambda text: len(text) > 0
            text = "  hello  "
            for i, step in enumerate(steps):
                text = step(text)
                print(i, repr(text), "pass" if gate(text) else "stop")
            # 0 'hello' pass
            # 1 'HELLO' pass
            ```

            `str.strip` and `str.upper` are used as functions here. `str.strip(text)` does the
            same as `text.strip()`. Click each stage to follow one step of the chain.

            ```diagram
            {"type":"flow","title":"A prompt chain with a gate","steps":[
              {"label":"Start with the input","detail":"The chain starts with the input text. The first step receives it.","code":"text = \"  hello  \""},
              {"label":"Run one step","detail":"The step is called with the current text. Its return value replaces the text.","code":"text = step(text)"},
              {"label":"Call the gate","detail":"The gate is called with the step's output. It returns True or False.","code":"gate(text)"},
              {"label":"Stop or continue","detail":"If the gate returned False, the chain stops and later steps do not run. If it returned True, the next step receives the output."},
              {"label":"Return the output","detail":"When every step has passed the gate, the last output is the result of the chain.","code":"'HELLO'"}
            ],"loop":{"from":3,"to":1,"label":"while the gate returns True and steps remain"}}
            ```

            Anthropic's advice is to start with the simplest workflow that works. Use an agent
            only when the sequence of steps cannot be planned in advance.
        ''',
        "prompt": r'''
            Build a prompt chain with a gate after every step. In tests, each step is a small
            fake "LLM call" function that takes a string and returns a string.

            **Write:** `run_chain(steps, text, gate)`

            - `steps`: a list of functions, each `step(text) -> str`
            - `text`: the starting string
            - `gate`: a function `gate(output) -> bool` (True = good, keep going)
            - **Returns:** a dict

            **Rules**
            - Run the steps in order; each step gets the previous step's output.
            - After **each** step, call `gate` on its output. If it returns `False`, stop at once and
              return `{"ok": False, "failed_at": <index of that step, starting at 0>, "output": <that output>}`.
              Later steps must not run.
            - If every step passes, return `{"ok": True, "output": <last output>}`.
            - With no steps, return `{"ok": True, "output": text}`.

            **Examples**
            ```python
            run_chain([str.strip, str.upper], "  hi ", lambda t: len(t) > 0)
            # returns {"ok": True, "output": "HI"}
            run_chain([str.strip, str.upper], "   ", lambda t: len(t) > 0)
            # returns {"ok": False, "failed_at": 0, "output": ""}
            run_chain([], "same", lambda t: False)
            # returns {"ok": True, "output": "same"}
            ```
        ''',
        "starter": r'''
            def run_chain(steps, text, gate):
                for step in steps:
                    text = step(text)
                return {"ok": True, "output": text}
        ''',
        "tests": r'''
            from solution import run_chain

            def not_empty(t):
                return len(t) > 0

            def test_all_steps_pass():
                got = run_chain([str.strip, str.upper], "  hi ", not_empty)
                assert got == {"ok": True, "output": "HI"}, f"got {got!r}"

            def test_gate_failure_reports_index_and_output():
                got = run_chain([str.strip, str.upper], "   ", not_empty)
                assert got == {"ok": False, "failed_at": 0, "output": ""}, f"got {got!r}"

            def test_later_steps_do_not_run_after_failure():
                ran = []
                def boom(t):
                    ran.append(t)
                    return t
                got = run_chain([str.upper, boom], "abc", lambda t: t != "ABC")
                assert ran == [], "a step ran after the gate failed"
                assert got["failed_at"] == 0 and got["ok"] is False

            def test_failure_in_second_step():
                got = run_chain([str.upper, lambda t: t + "!"], "ok", lambda t: not t.endswith("!"))
                assert got == {"ok": False, "failed_at": 1, "output": "OK!"}, f"got {got!r}"

            def test_no_steps_returns_input():
                assert run_chain([], "same", lambda t: False) == {"ok": True, "output": "same"}
        ''',
        "solution": r'''
            def run_chain(steps, text, gate):
                for i, step in enumerate(steps):
                    text = step(text)
                    if not gate(text):
                        return {"ok": False, "failed_at": i, "output": text}
                return {"ok": True, "output": text}
        ''',
        "hints": [
            "The starter already runs the steps. What's missing is the check after each one.",
            "Use enumerate to know each step's index, and return early as soon as the gate says no.",
            "for i, step in enumerate(steps): text = step(text); if not gate(text): return the failure dict with i and text. After the loop, return the ok dict.",
        ],
    },
    {
        "id": "agents-6",
        "title": "The full agent loop",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## The full agent loop

            This exercise combines the earlier parts into one function. The loop repeats
            think, act and observe. It ends on a final answer or when the step limit is
            reached, and it adds one audit log entry for every tool call.

            `range(1, max_steps + 1)` produces the step numbers from 1 to `max_steps`. A `for`
            loop over it runs its body at most `max_steps` times.

            ```python
            max_steps = 3
            calls = 0
            for step in range(1, max_steps + 1):
                calls += 1
                print("model call", step)
            # model call 1
            # model call 2
            # model call 3
            print("calls made:", calls)
            # calls made: 3
            ```

            A `while True` loop has no such limit. The returned dict states why the loop
            ended, in the key `stop_reason`.
        ''',
        "prompt": r'''
            Write a complete agent loop with a step limit and an audit log.

            **Write:** `run_agent(model, tools, task, max_steps=5)`

            - `model`: function, `model(messages)` returns `{"type": "tool", "tool": name, "args": {...}}`
              or `{"type": "final", "text": "..."}`
            - `tools`: dict of name -> function
            - `task`: str, the user's request, e.g. `"What is 2 + 3?"`
            - `max_steps`: int, the most model calls allowed
            - **Returns:** a dict `{"answer": ..., "stop_reason": ..., "steps": ..., "log": [...]}`

            **Rules**
            - Start with `messages = [{"role": "user", "content": task}]` and pass this list to every model call.
            - Each model call is one step (`steps` = number of model calls made).
            - Final reply: return `answer` = its text, `stop_reason` = `"final"`.
            - Tool reply: run `tools[name](**args)`, append
              `{"role": "assistant", "tool": name, "args": args}` then
              `{"role": "tool", "name": name, "content": str(result)}` to `messages`, and add
              `{"step": step, "tool": name, "args": args, "result": result}` to `log` (steps count from 1).
            - If `max_steps` model calls happen without a final reply: `answer` = `None`,
              `stop_reason` = `"max_steps"`, `steps` = `max_steps`. Never call the model more than `max_steps` times.

            **Examples**
            ```python
            # model script: tool add(a=2, b=3), then final "5"
            run_agent(model, {"add": add}, "What is 2 + 3?")
            # returns {"answer": "5", "stop_reason": "final", "steps": 2,
            #          "log": [{"step": 1, "tool": "add", "args": {"a": 2, "b": 3}, "result": 5}]}

            # model that always asks for a tool
            run_agent(looping_model, {"add": add}, "loop", max_steps=3)
            # returns {"answer": None, "stop_reason": "max_steps", "steps": 3, "log": [3 entries]}
            ```
        ''',
        "starter": r'''
            def run_agent(model, tools, task, max_steps=5):
                messages = [{"role": "user", "content": task}]
                while True:
                    reply = model(messages)
                    if reply["type"] == "final":
                        return reply["text"]
        ''',
        "tests": r'''
            from solution import run_agent

            def add(a, b):
                return a + b

            def scripted(replies):
                seen = []
                def model(messages):
                    seen.append([dict(m) for m in messages])
                    if len(seen) > len(replies):
                        raise AssertionError("model called too many times")
                    return replies[len(seen) - 1]
                model.seen = seen
                return model

            TOOL = {"type": "tool", "tool": "add", "args": {"a": 2, "b": 3}}
            FINAL = {"type": "final", "text": "5"}

            def test_tool_then_final_answer():
                got = run_agent(scripted([TOOL, FINAL]), {"add": add}, "What is 2 + 3?")
                assert got == {"answer": "5", "stop_reason": "final", "steps": 2,
                               "log": [{"step": 1, "tool": "add", "args": {"a": 2, "b": 3}, "result": 5}]}, f"got {got!r}"

            def test_model_sees_task_and_observation():
                model = scripted([TOOL, FINAL])
                run_agent(model, {"add": add}, "What is 2 + 3?")
                assert model.seen[0] == [{"role": "user", "content": "What is 2 + 3?"}]
                assert model.seen[1][1:] == [{"role": "assistant", "tool": "add", "args": {"a": 2, "b": 3}},
                                             {"role": "tool", "name": "add", "content": "5"}], f"second call saw {model.seen[1]!r}"

            def test_stops_at_max_steps():
                model = scripted([TOOL] * 10)
                got = run_agent(model, {"add": add}, "loop", max_steps=3)
                assert got["answer"] is None and got["stop_reason"] == "max_steps", f"got {got!r}"
                assert got["steps"] == 3 and len(got["log"]) == 3
                assert len(model.seen) == 3, f"model called {len(model.seen)} times"
                assert [e["step"] for e in got["log"]] == [1, 2, 3]

            def test_immediate_final_answer():
                got = run_agent(scripted([{"type": "final", "text": "hi"}]), {}, "say hi")
                assert got == {"answer": "hi", "stop_reason": "final", "steps": 1, "log": []}, f"got {got!r}"

            def test_final_on_the_last_allowed_step_counts():
                got = run_agent(scripted([TOOL, FINAL]), {"add": add}, "t", max_steps=2)
                assert got["stop_reason"] == "final" and got["answer"] == "5"
        ''',
        "solution": r'''
            def run_agent(model, tools, task, max_steps=5):
                messages = [{"role": "user", "content": task}]
                log = []
                for step in range(1, max_steps + 1):
                    reply = model(messages)
                    if reply["type"] == "final":
                        return {"answer": reply["text"], "stop_reason": "final", "steps": step, "log": log}
                    name, args = reply["tool"], reply["args"]
                    result = tools[name](**args)
                    messages.append({"role": "assistant", "tool": name, "args": args})
                    messages.append({"role": "tool", "name": name, "content": str(result)})
                    log.append({"step": step, "tool": name, "args": args, "result": result})
                return {"answer": None, "stop_reason": "max_steps", "steps": max_steps, "log": log}
        ''',
        "hints": [
            "Replace the endless while loop with a loop that runs at most max_steps times, counting steps from 1.",
            "Inside the loop: ask the model; on final, return the result dict; on a tool, run it, append the two messages and a log entry. After the loop, return the max_steps dict.",
            "Create messages and log = []. for step in range(1, max_steps + 1): reply = model(messages); if final return {answer, \"final\", step, log}. Else result = tools[name](**args); append assistant msg, tool msg with str(result), and the log dict. After the loop return {None, \"max_steps\", max_steps, log}.",
        ],
    },
    {
        "id": "agents-7",
        "title": "A registry with human approval",
        "difficulty": 2,
        "lesson": r'''
            ## Human approval

            Some tools are risky because their effects are hard to undo: sending an email,
            deleting files, paying. **Human approval** means a person must agree before such
            a tool runs. In code, the person is a function `approve(name, args)` that returns
            `True` or `False`. Risky tools stay in the registry, and every call is recorded.

            ```python
            risky = {"send_email"}

            def approve(name, args):
                print("asking about", name)
                return False

            for name in ["add", "send_email"]:
                if name in risky and not approve(name, {}):
                    print("denied:", name)
                else:
                    print("run:", name)
            # run: add
            # asking about send_email
            # denied: send_email
            ```

            `and` evaluates its right side only when the left side is true. `approve` is
            therefore called for `send_email` and not for `add`.
        ''',
        "prompt": r'''
            Build a tool registry class where risky tools need human approval.

            **Write:** class `ToolRegistry`

            - `ToolRegistry()` starts empty; attribute `history` is a list (starts `[]`).
            - `register(name, fn, risky=False)`: add a tool.
            - `names()`: returns a sorted list of registered tool names.
            - `call(name, args, approve=None)`: run a tool and return a result or a status string.
              `approve` is a function `approve(name, args) -> bool` (a human saying yes/no), or `None`.

            **Rules for `call`**
            - Unknown tool: return `"error: unknown tool <name>"` and add `(name, "unknown")` to `history`.
            - Risky tool: call `approve(name, args)`. If `approve` is `None` or returns a false value, do **not**
              run the tool; return `"denied: <name>"` and add `(name, "denied")` to `history`.
            - Otherwise (safe tool, or risky and approved): return `fn(**args)` and add `(name, "ok")` to `history`.
            - `approve` is only called for risky tools.

            **Examples**
            ```python
            reg = ToolRegistry()
            reg.register("add", lambda a, b: a + b)
            reg.register("send_email", send_email, risky=True)
            reg.names()                                            # ["add", "send_email"]
            reg.call("add", {"a": 1, "b": 2})                      # returns 3
            reg.call("send_email", {"to": "x@y.z"})                # returns "denied: send_email"
            reg.call("send_email", {"to": "x@y.z"}, lambda n, a: True)   # runs send_email
            reg.call("fly", {})                                    # returns "error: unknown tool fly"
            reg.history   # [("add", "ok"), ("send_email", "denied"), ("send_email", "ok"), ("fly", "unknown")]
            ```
        ''',
        "starter": r'''
            class ToolRegistry:
                def __init__(self):
                    self.tools = {}

                def register(self, name, fn, risky=False):
                    self.tools[name] = fn
        ''',
        "tests": r'''
            from solution import ToolRegistry

            def make():
                sent = []
                def send_email(to):
                    sent.append(to)
                    return f"sent to {to}"
                reg = ToolRegistry()
                reg.register("add", lambda a, b: a + b)
                reg.register("send_email", send_email, risky=True)
                return reg, sent

            def test_names_are_sorted():
                reg, _ = make()
                reg.register("abs", abs)
                assert reg.names() == ["abs", "add", "send_email"], f"got {reg.names()!r}"

            def test_safe_tool_runs_without_approval():
                reg, _ = make()
                assert reg.call("add", {"a": 1, "b": 2}) == 3
                assert reg.history == [("add", "ok")]

            def test_risky_tool_denied_without_approver():
                reg, sent = make()
                got = reg.call("send_email", {"to": "x@y.z"})
                assert got == "denied: send_email", f"got {got!r}"
                assert sent == [], "the risky tool ran without approval"

            def test_risky_tool_denied_when_human_says_no():
                reg, sent = make()
                asked = []
                got = reg.call("send_email", {"to": "x@y.z"}, lambda n, a: asked.append((n, a)) or False)
                assert got == "denied: send_email" and sent == []
                assert asked == [("send_email", {"to": "x@y.z"})], f"approve got {asked!r}"

            def test_risky_tool_runs_when_approved():
                reg, sent = make()
                got = reg.call("send_email", {"to": "x@y.z"}, lambda n, a: True)
                assert got == "sent to x@y.z" and sent == ["x@y.z"]

            def test_approve_not_called_for_safe_tools_and_history_tracks_all():
                reg, _ = make()
                def never(n, a):
                    raise AssertionError("approve was called for a safe tool")
                reg.call("add", {"a": 1, "b": 1}, never)
                reg.call("send_email", {"to": "a"})
                reg.call("send_email", {"to": "a"}, lambda n, a: True)
                assert reg.call("fly", {}) == "error: unknown tool fly"
                assert reg.history == [("add", "ok"), ("send_email", "denied"),
                                       ("send_email", "ok"), ("fly", "unknown")], f"got {reg.history!r}"
        ''',
        "solution": r'''
            class ToolRegistry:
                def __init__(self):
                    self.tools = {}
                    self.risky = set()
                    self.history = []

                def register(self, name, fn, risky=False):
                    self.tools[name] = fn
                    if risky:
                        self.risky.add(name)

                def names(self):
                    return sorted(self.tools)

                def call(self, name, args, approve=None):
                    if name not in self.tools:
                        self.history.append((name, "unknown"))
                        return f"error: unknown tool {name}"
                    if name in self.risky:
                        if approve is None or not approve(name, args):
                            self.history.append((name, "denied"))
                            return f"denied: {name}"
                    result = self.tools[name](**args)
                    self.history.append((name, "ok"))
                    return result
        ''',
        "hints": [
            "Besides the tools dict, the registry must remember which names are risky and keep a history list.",
            "In call, handle the three cases in order: unknown name, risky-and-not-approved, then run it. Record a tuple in history in each case.",
            "In __init__ add self.risky = set() and self.history = []. register adds the name to risky when risky=True. names returns sorted(self.tools). call: unknown -> append (name, \"unknown\") and return the error; if name in risky and (approve is None or not approve(name, args)) -> append (name, \"denied\") and return the denied string; else run fn(**args), append (name, \"ok\"), return the result.",
        ],
    },
    {
        "id": "agents-8",
        "title": "Agent memory",
        "difficulty": 2,
        "lesson": r'''
            ## Agent memory

            An agent's **memory** is the data your code sends to the model on every call.
            The model itself keeps nothing between calls.

            The context window (the most text a model accepts in one call) is limited, so an
            agent keeps only the most recent messages. A slice with a negative start keeps
            the last items of a list.

            ```python
            messages = ["m1", "m2", "m3", "m4"]
            print(messages[-2:])
            # ['m3', 'm4']
            ```

            Anything in a dropped message is no longer sent to the model. Values that must
            stay available are stored separately as **facts**, in a dict, and sent in a
            system message on every turn. Assigning to an existing key replaces the value
            and keeps the key's position.

            ```python
            facts = {"name": "Ada", "lang": "fr"}
            facts["lang"] = "en"
            print(", ".join(f"{k} is {v}" for k, v in facts.items()))
            # name is Ada, lang is en
            ```

            `dict(m)` creates a new dict with the same keys and values as `m`. Changing the
            new dict does not change `m`.

            ```python
            m = {"role": "user", "content": "hi"}
            c = dict(m)
            c["content"] = "changed"
            print(m["content"])
            # hi
            ```
        ''',
        "prompt": r'''
            Build a small memory for an agent: a rolling window of recent messages plus facts.

            **Write:** class `AgentMemory`

            - `AgentMemory(max_messages)`: `max_messages` is an int, the most messages to keep.
            - `add(role, content)`: store `{"role": role, "content": content}`. If there are now more than
              `max_messages` messages, drop the **oldest** ones so exactly `max_messages` remain.
            - `remember(key, value)`: store a fact (a later call with the same key replaces the value).
            - `context()`: returns a new list of message dicts to send to the model.

            **Rules for `context()`**
            - If there are facts, the first item is
              `{"role": "system", "content": "Facts: k1=v1; k2=v2"}` - facts in the order first remembered,
              each as `key=value`, joined by `"; "`.
            - Then the stored messages, oldest first.
            - With no facts, there's no system message.
            - Changing the returned list (or its dicts) must not change the memory.

            **Examples**
            ```python
            mem = AgentMemory(2)
            mem.add("user", "hi"); mem.add("assistant", "hello"); mem.add("user", "I'm Ada")
            mem.remember("name", "Ada")
            mem.context()
            # returns [{"role": "system", "content": "Facts: name=Ada"},
            #          {"role": "assistant", "content": "hello"},
            #          {"role": "user", "content": "I'm Ada"}]
            ```
        ''',
        "starter": r'''
            class AgentMemory:
                def __init__(self, max_messages):
                    self.max_messages = max_messages
                    self.messages = []

                def add(self, role, content):
                    self.messages.append({"role": role, "content": content})

                def context(self):
                    return self.messages
        ''',
        "tests": r'''
            from solution import AgentMemory

            def test_keeps_only_the_newest_messages():
                mem = AgentMemory(2)
                mem.add("user", "a"); mem.add("assistant", "b"); mem.add("user", "c")
                assert mem.context() == [{"role": "assistant", "content": "b"},
                                         {"role": "user", "content": "c"}], f"got {mem.context()!r}"

            def test_facts_come_first_as_system_message():
                mem = AgentMemory(5)
                mem.add("user", "hi")
                mem.remember("name", "Ada")
                mem.remember("lang", "fr")
                got = mem.context()
                assert got[0] == {"role": "system", "content": "Facts: name=Ada; lang=fr"}, f"got {got[0]!r}"
                assert got[1:] == [{"role": "user", "content": "hi"}]

            def test_remember_same_key_replaces_value():
                mem = AgentMemory(5)
                mem.remember("city", "Paris"); mem.remember("city", "Rome")
                assert mem.context() == [{"role": "system", "content": "Facts: city=Rome"}]

            def test_no_facts_no_system_message():
                mem = AgentMemory(3)
                mem.add("user", "x")
                assert mem.context() == [{"role": "user", "content": "x"}]

            def test_changing_context_does_not_change_memory():
                mem = AgentMemory(3)
                mem.add("user", "x")
                ctx = mem.context()
                ctx.append({"role": "user", "content": "extra"})
                ctx[0]["content"] = "changed"
                assert mem.context() == [{"role": "user", "content": "x"}], f"got {mem.context()!r}"
        ''',
        "solution": r'''
            class AgentMemory:
                def __init__(self, max_messages):
                    self.max_messages = max_messages
                    self.messages = []
                    self.facts = {}

                def add(self, role, content):
                    self.messages.append({"role": role, "content": content})
                    if len(self.messages) > self.max_messages:
                        self.messages = self.messages[-self.max_messages:]

                def remember(self, key, value):
                    self.facts[key] = value

                def context(self):
                    out = []
                    if self.facts:
                        text = "; ".join(f"{k}={v}" for k, v in self.facts.items())
                        out.append({"role": "system", "content": "Facts: " + text})
                    for m in self.messages:
                        out.append(dict(m))
                    return out
        ''',
        "hints": [
            "Three jobs: trim the message list in add, store facts in a dict, and build a fresh list in context.",
            "Slicing with a negative start keeps the last N items. Dicts keep insertion order, and assigning an existing key keeps its position. Copy each message dict when building the context.",
            "add: append, then if too long keep self.messages[-self.max_messages:]. remember: self.facts[key] = value. context: start an empty list; if facts, add the system dict built by joining \"k=v\" strings with \"; \"; then append dict(m) for each stored message; return the list.",
        ],
    },
    {
        "id": "agents-9",
        "title": "Budgets and error recovery",
        "difficulty": 3,
        "prompt": r'''
            A production agent must stop for many reasons and must keep running when tools fail.

            **Write:** `run_budgeted_agent(model, tools, task, max_steps, max_tokens, max_errors=2)`

            - `model(messages)` returns a reply dict that always has a `"tokens"` key (int, tokens used by that call):
              `{"type": "tool", "tool": name, "args": {...}, "tokens": 120}` or `{"type": "final", "text": "...", "tokens": 40}`
            - `tools`: dict name -> function; `task`: str; limits are ints
            - **Returns:** `{"answer": str or None, "stop_reason": str, "steps": int, "tokens": int}`

            **Rules** (each step, in this order)
            1. Call `model(messages)` (messages start as `[{"role": "user", "content": task}]`). Add the reply's
               `"tokens"` to the running total. `steps` = number of model calls so far.
            2. Final reply: stop with `stop_reason` `"final"` and its text as `answer` (even if the budget is now exceeded).
            3. Tool reply but total tokens `>= max_tokens`: stop with `"tokens"` **without** running the tool.
            4. Otherwise run the tool safely: unknown tool -> result `"error: unknown tool <name>"`;
               exception `e` -> result `"error: <ExceptionClassName>: <e>"`. Append
               `{"role": "assistant", "tool": name, "args": args}` and
               `{"role": "tool", "name": name, "content": str(result)}` to messages.
            5. Count errors **in a row**: an error result adds 1, a successful tool call resets the count to 0.
               When the count reaches `max_errors`, stop with `"errors"`.
            6. After `max_steps` model calls without stopping: stop with `"max_steps"`.
            - `answer` is `None` for every stop reason except `"final"`. `tokens` is the running total.

            **Examples**
            ```python
            # script: add(a=1,b=2) [100 tokens], final "3" [50 tokens]
            run_budgeted_agent(model, {"add": add}, "1+2?", max_steps=5, max_tokens=1000)
            # returns {"answer": "3", "stop_reason": "final", "steps": 2, "tokens": 150}

            # script: fly {} [10], fly {} [10], ...  (unknown tool twice)
            run_budgeted_agent(model, {}, "go", max_steps=5, max_tokens=1000, max_errors=2)
            # returns {"answer": None, "stop_reason": "errors", "steps": 2, "tokens": 20}
            ```
        ''',
        "starter": r'''
            def run_budgeted_agent(model, tools, task, max_steps, max_tokens, max_errors=2):
                ...
        ''',
        "tests": r'''
            from solution import run_budgeted_agent

            def add(a, b):
                return a + b

            def div(a, b):
                return a / b

            def scripted(replies):
                seen = []
                def model(messages):
                    seen.append([dict(m) for m in messages])
                    if len(seen) > len(replies):
                        raise AssertionError("model called too many times")
                    return replies[len(seen) - 1]
                model.seen = seen
                return model

            def tool(name, tokens, **args):
                return {"type": "tool", "tool": name, "args": args, "tokens": tokens}

            def final(text, tokens):
                return {"type": "final", "text": text, "tokens": tokens}

            def test_normal_run_counts_tokens():
                got = run_budgeted_agent(scripted([tool("add", 100, a=1, b=2), final("3", 50)]),
                                         {"add": add}, "1+2?", max_steps=5, max_tokens=1000)
                assert got == {"answer": "3", "stop_reason": "final", "steps": 2, "tokens": 150}, f"got {got!r}"

            def test_token_budget_stops_before_running_tool():
                ran = []
                def spy(**kw):
                    ran.append(kw)
                    return "x"
                got = run_budgeted_agent(scripted([tool("spy", 600), tool("spy", 600), final("done", 1)]),
                                         {"spy": spy}, "t", max_steps=5, max_tokens=1000)
                assert got == {"answer": None, "stop_reason": "tokens", "steps": 2, "tokens": 1200}, f"got {got!r}"
                assert len(ran) == 1, "the tool ran after the token budget was reached"

            def test_error_is_observed_and_agent_recovers():
                model = scripted([tool("div", 10, a=1, b=0), tool("div", 10, a=4, b=2), final("2.0", 10)])
                got = run_budgeted_agent(model, {"div": div}, "t", max_steps=5, max_tokens=1000)
                assert got["stop_reason"] == "final" and got["answer"] == "2.0", f"got {got!r}"
                assert model.seen[1][-1] == {"role": "tool", "name": "div",
                                             "content": "error: ZeroDivisionError: division by zero"}, f"saw {model.seen[1][-1]!r}"

            def test_consecutive_errors_stop_the_agent():
                got = run_budgeted_agent(scripted([tool("fly", 10), tool("fly", 10), final("x", 1)]),
                                         {}, "go", max_steps=5, max_tokens=1000, max_errors=2)
                assert got == {"answer": None, "stop_reason": "errors", "steps": 2, "tokens": 20}, f"got {got!r}"

            def test_success_resets_error_count():
                replies = [tool("fly", 1), tool("add", 1, a=1, b=1), tool("fly", 1), final("ok", 1)]
                got = run_budgeted_agent(scripted(replies), {"add": add}, "t", max_steps=5, max_tokens=100, max_errors=2)
                assert got["stop_reason"] == "final", f"got {got!r}"

            def test_max_steps():
                got = run_budgeted_agent(scripted([tool("add", 1, a=1, b=1)] * 5), {"add": add}, "t",
                                         max_steps=3, max_tokens=1000)
                assert got == {"answer": None, "stop_reason": "max_steps", "steps": 3, "tokens": 3}, f"got {got!r}"
        ''',
        "solution": r'''
            def run_budgeted_agent(model, tools, task, max_steps, max_tokens, max_errors=2):
                messages = [{"role": "user", "content": task}]
                tokens = 0
                errors = 0
                for step in range(1, max_steps + 1):
                    reply = model(messages)
                    tokens += reply["tokens"]
                    if reply["type"] == "final":
                        return {"answer": reply["text"], "stop_reason": "final", "steps": step, "tokens": tokens}
                    if tokens >= max_tokens:
                        return {"answer": None, "stop_reason": "tokens", "steps": step, "tokens": tokens}
                    name, args = reply["tool"], reply["args"]
                    failed = False
                    if name not in tools:
                        result, failed = f"error: unknown tool {name}", True
                    else:
                        try:
                            result = tools[name](**args)
                        except Exception as e:
                            result, failed = f"error: {type(e).__name__}: {e}", True
                    messages.append({"role": "assistant", "tool": name, "args": args})
                    messages.append({"role": "tool", "name": name, "content": str(result)})
                    errors = errors + 1 if failed else 0
                    if errors >= max_errors:
                        return {"answer": None, "stop_reason": "errors", "steps": step, "tokens": tokens}
                return {"answer": None, "stop_reason": "max_steps", "steps": max_steps, "tokens": tokens}
        ''',
        "hints": [
            "Start from your run_agent loop and add two counters: total tokens and errors in a row.",
            "Follow the numbered rules as a checklist inside the loop: add tokens, check final, check the token budget, run the tool safely, update the error counter and check it. Track 'did this call fail' with a boolean rather than by looking at the result text.",
            "for step in range(1, max_steps + 1): reply = model(messages); tokens += reply[\"tokens\"]; final -> return; tokens >= max_tokens -> return \"tokens\"; compute result and a failed flag (unknown name, or except Exception as e); append the two messages; errors = errors + 1 if failed else 0; if errors >= max_errors return \"errors\". After the loop return \"max_steps\".",
        ],
    },
    {
        "id": "agents-10",
        "title": "A supervised agent",
        "difficulty": 3,
        "prompt": r'''
            Combine the loop, risky-tool approval and a detailed audit log. Denials and errors don't
            stop the agent: they are reported back to the model so it can choose something else.

            **Write:** `run_supervised_agent(model, tools, task, risky, approve, max_steps=5)`

            - `model(messages)` returns `{"type": "tool", "tool": name, "args": {...}}` or `{"type": "final", "text": "..."}`
            - `tools`: dict name -> function; `task`: str
            - `risky`: a set of tool names that need approval, e.g. `{"delete_file"}`
            - `approve`: function `approve(name, args) -> bool`
            - **Returns:** `{"answer": str or None, "stop_reason": "final" or "max_steps", "audit": [...]}`

            **Rules** (messages start as `[{"role": "user", "content": task}]`; steps count model calls from 1)
            - Final reply: return its text with `"final"`. After `max_steps` calls without one: `None`, `"max_steps"`.
            - For each tool reply, decide a `status` and a `result`:
              - unknown tool: status `"error"`, result `"error: unknown tool <name>"`;
              - risky tool and `approve(name, args)` is false: status `"denied"`, result
                `"denied: user did not approve <name>"` (the tool does not run);
              - the tool raises `e`: status `"error"`, result `"error: <ExceptionClassName>: <e>"`;
              - otherwise status `"ok"`, result = the tool's return value.
            - Call `approve` only for known risky tools, once per request.
            - Every tool reply adds `{"step": step, "tool": name, "args": args, "status": status, "result": result}` to `audit`.
            - Every tool reply appends `{"role": "assistant", "tool": name, "args": args}` and
              `{"role": "tool", "name": name, "content": str(result)}` to messages.

            **Examples**
            ```python
            # script: delete_file(path="a.txt"), then final "I could not delete it."
            run_supervised_agent(model, {"delete_file": delete_file}, "clean up",
                                 risky={"delete_file"}, approve=lambda n, a: False)
            # returns {"answer": "I could not delete it.", "stop_reason": "final",
            #          "audit": [{"step": 1, "tool": "delete_file", "args": {"path": "a.txt"},
            #                     "status": "denied", "result": "denied: user did not approve delete_file"}]}
            ```
        ''',
        "starter": r'''
            def run_supervised_agent(model, tools, task, risky, approve, max_steps=5):
                ...
        ''',
        "tests": r'''
            from solution import run_supervised_agent

            def scripted(replies):
                seen = []
                def model(messages):
                    seen.append([dict(m) for m in messages])
                    if len(seen) > len(replies):
                        raise AssertionError("model called too many times")
                    return replies[len(seen) - 1]
                model.seen = seen
                return model

            def tool(name, **args):
                return {"type": "tool", "tool": name, "args": args}

            def final(text):
                return {"type": "final", "text": text}

            def make_tools():
                deleted = []
                def delete_file(path):
                    deleted.append(path)
                    return f"deleted {path}"
                def read_file(path):
                    if path == "missing":
                        raise FileNotFoundError("no such file")
                    return "contents"
                return {"delete_file": delete_file, "read_file": read_file}, deleted

            def test_denied_tool_does_not_run_and_is_audited():
                tools, deleted = make_tools()
                model = scripted([tool("delete_file", path="a.txt"), final("I could not delete it.")])
                got = run_supervised_agent(model, tools, "clean up", {"delete_file"}, lambda n, a: False)
                assert deleted == [], "a denied tool ran"
                assert got == {"answer": "I could not delete it.", "stop_reason": "final",
                               "audit": [{"step": 1, "tool": "delete_file", "args": {"path": "a.txt"},
                                          "status": "denied", "result": "denied: user did not approve delete_file"}]}, f"got {got!r}"
                assert model.seen[1][-1]["content"] == "denied: user did not approve delete_file"

            def test_approved_risky_tool_runs():
                tools, deleted = make_tools()
                asked = []
                def approve(n, a):
                    asked.append((n, a))
                    return True
                got = run_supervised_agent(scripted([tool("delete_file", path="b"), final("done")]),
                                           tools, "t", {"delete_file"}, approve)
                assert deleted == ["b"] and asked == [("delete_file", {"path": "b"})], f"asked {asked!r}"
                assert got["audit"][0]["status"] == "ok" and got["audit"][0]["result"] == "deleted b"

            def test_safe_tools_never_ask_for_approval():
                tools, _ = make_tools()
                def never(n, a):
                    raise AssertionError("approve called for a safe tool")
                got = run_supervised_agent(scripted([tool("read_file", path="x"), final("ok")]),
                                           tools, "t", {"delete_file"}, never)
                assert got["audit"][0]["status"] == "ok" and got["audit"][0]["result"] == "contents"

            def test_errors_are_audited_and_observed():
                tools, _ = make_tools()
                model = scripted([tool("read_file", path="missing"), tool("fly"), final("gave up")])
                got = run_supervised_agent(model, tools, "t", set(), lambda n, a: True)
                assert [e["status"] for e in got["audit"]] == ["error", "error"], f"got {got['audit']!r}"
                assert got["audit"][0]["result"] == "error: FileNotFoundError: no such file"
                assert got["audit"][1]["result"] == "error: unknown tool fly"
                assert model.seen[2][-1] == {"role": "tool", "name": "fly", "content": "error: unknown tool fly"}
                assert got["answer"] == "gave up"

            def test_max_steps_limit():
                tools, _ = make_tools()
                model = scripted([tool("read_file", path="x")] * 5)
                got = run_supervised_agent(model, tools, "t", set(), lambda n, a: True, max_steps=2)
                assert got["answer"] is None and got["stop_reason"] == "max_steps"
                assert [e["step"] for e in got["audit"]] == [1, 2] and len(model.seen) == 2
        ''',
        "solution": r'''
            def run_supervised_agent(model, tools, task, risky, approve, max_steps=5):
                messages = [{"role": "user", "content": task}]
                audit = []
                for step in range(1, max_steps + 1):
                    reply = model(messages)
                    if reply["type"] == "final":
                        return {"answer": reply["text"], "stop_reason": "final", "audit": audit}
                    name, args = reply["tool"], reply["args"]
                    if name not in tools:
                        status, result = "error", f"error: unknown tool {name}"
                    elif name in risky and not approve(name, args):
                        status, result = "denied", f"denied: user did not approve {name}"
                    else:
                        try:
                            status, result = "ok", tools[name](**args)
                        except Exception as e:
                            status, result = "error", f"error: {type(e).__name__}: {e}"
                    audit.append({"step": step, "tool": name, "args": args, "status": status, "result": result})
                    messages.append({"role": "assistant", "tool": name, "args": args})
                    messages.append({"role": "tool", "name": name, "content": str(result)})
                return {"answer": None, "stop_reason": "max_steps", "audit": audit}
        ''',
        "hints": [
            "This is your run_agent loop with a decision block in the middle that picks a status and a result for each tool request.",
            "Check the cases in order: unknown name, risky-and-not-approved, then try to run it (catching exceptions). Only after deciding, write the audit entry and the two messages.",
            "for step in range(1, max_steps + 1): reply = model(messages); final -> return. Then if/elif/else: unknown -> error; elif name in risky and not approve(name, args) -> denied; else try running -> ok, except Exception as e -> error. Append the audit dict, the assistant message and the tool message (str(result)). After the loop return the max_steps dict.",
        ],
    },
]
