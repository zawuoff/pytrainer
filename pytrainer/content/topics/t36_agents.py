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
# 1 add {'a': 2, 'b': 3} -> 5
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
            ## Let the reply choose the next action

            A user asks a question that needs information from a tool. You cannot plan the exact answer in advance, but you can write code that reads a model's request, runs the requested tool, and gives the result back.

            ```python
            script = [{"kind": "action", "name": "lookup"},
                      {"kind": "answer", "text": "Ready"}]
            for item in script:
                if item["kind"] == "answer":
                    print(item["text"])
                    break
                print("requested:", item["name"])
            # requested: lookup
            # Ready
            ```

            The first item describes an action. The second describes a completed answer and ends the loop. These items are prewritten data, so no model or network is needed to follow the control flow. The loop makes the decision; the data describes what decision to make.

            A program that repeatedly asks a model what to do, executes permitted actions and reports their results is an **agent**. You will see this described as **think, act, observe**: call the model, run a tool, and return its result to the conversation. A model reply does not itself execute Python or gain permission to act.

            This chapter uses a deliberately small reply format. It has tool requests and final answers. It is a teaching interface, rather than a universal provider response shape. Stop as soon as a final answer arrives; continuing could run actions after the task is complete.

            ```match
            think :: ask the model for the next reply
            act :: execute a permitted tool request
            observe :: include the result in later model context
            ---
            Your program coordinates all three phases and decides which actions are allowed.
            ```


            Try one more small check before moving to the task.

            ```predict
            for item in ["action", "done", "unused"]:
                print(item)
                if item == "done":
                    break
            ---
            The stop condition prevents the later unused item from being read or printed.
            ```

            **Watch out:** Reading a tool name does not execute that tool. Your code must explicitly dispatch it, and must stop dispatching after a final reply.

            **In short:** An agent loop reads requests, runs allowed actions, and feeds results into the next call.
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

            Follow each printed line in execution order. Changes to a variable affect later lines; they do not change output that was already printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Identify which reply branch runs on each pass through the loop.",
            "A final reply ends the loop, so later replies cannot produce output.",
            "Follow the step numbering, evaluate a tool call when requested, and trace each print until the branch that stops the loop.",
        ],
    },
    {
        "id": "agents-s2",
        "title": "Is the agent done?",
        "difficulty": 0,
        "lesson": r'''
            ## Recognise a completed answer

            Your loop needs a clear signal that the model has finished. Looking at the wording of its answer would be fragile. Give the reply a field that states whether it is asking for an action or delivering an answer.

            ```python
            event = {"kind": "complete", "message": ""}
            print(event["kind"] == "complete")
            # True
            print(event["kind"] == "action")
            # False
            ```

            The comparison reads the signal field and returns a boolean. The message is empty, but that does not alter the signal. A completed reply and a nonempty reply are different properties.

            A rule deciding when a loop should end is a **stop condition**. Here the rule inspects the reply's type. Your task uses the chapter's tool and final type names. Checking that field is more reliable than searching for a phrase such as done in free text.

            The starter already contains the lookup and comparison. Complete its missing value so it recognises the agreed final type. A comparison expression is itself a boolean, so the function can return it directly. You do not need to convert the entire dictionary to a boolean: a tool request is usually nonempty too. Keep the contract focused on the specific field rather than incidental contents such as answer length or tool name.

            ```fill
            state = {"kind": "working"}
            print(state["kind"] ___ "complete")
            ---
            - [x] == :: Equality asks whether the field has the agreed completion value.
            - [ ] != :: Inequality would report the opposite and treat working as complete.
            ```


            Try one more small check before moving to the task.

            ```predict
            print(bool({"kind": "working"}))
            ---
            A working reply can be truthy. Truthiness of the whole dictionary is not a completion signal.
            ```

            **Watch out:** A truthy dictionary does not establish that a task is finished. Both tool requests and final answers can contain data.

            **In short:** Use the agreed reply type as the completion signal, even when its text is empty.
        ''',
        "prompt": r'''
            The loop needs a completion signal. Fill the gap in the supplied comparison so it recognises final replies.

            **Your job:** `is_final(reply)`

            **What goes in**
            - `reply`: a dict like `{"type": "final", "text": "Paris"}` or
              `{"type": "tool", "tool": "search", "args": {"q": "x"}}`

            **What comes out**
            - `True` if the reply's `"type"` is `"final"`, otherwise `False`

            **Rules**
            - An empty answer string still counts as final when its type is final.

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
            "Which field carries the completion signal?",
            "The function must test the reply type rather than the answer contents.",
            "Read the expected type names in the task and complete the comparison so only a final reply makes it true.",
        ],
    },
    {
        "id": "agents-s3",
        "title": "Fix: one step too many",
        "difficulty": 0,
        "lesson": r'''
            ## Stop exactly when a limit is reached

            A model can keep requesting actions without ever answering. You need a second way to end the loop: a limit on the calls already made. The boundary itself matters, because one extra call can trigger another action or cost money.

            ```python
            limit = 4
            for used in [3, 4, 5]:
                print(used, used >= limit, used > limit)
            # 3 False False
            # 4 True False
            # 5 True True
            ```

            The comparisons differ when the count is exactly four. At that point all four allowed calls have already happened. Waiting until the count is greater would allow another call.

            A one-step mistake at a counting boundary is called an **off-by-one error**. You have met similar mistakes with indexes and ranges. Here the count represents completed calls, not the index of a future call, so reason from what has already happened.

            The loop also stops when a final reply arrives. These two reasons are independent: finishing early is allowed, and reaching the limit must stop a still-working model. The boolean operator or combines them because either reason is sufficient. Check a count below, equal to and above the limit. Those three examples reveal a boundary error much more reliably than testing only a typical count.

            ```quiz
            Four calls are allowed and four have happened. May the loop make a fifth?
            - [x] No, the allowance is used up. :: The maximum includes the calls already made, so reaching it is sufficient to stop.
            - [ ] Yes, because the count is not greater yet. :: That interpretation allows one call beyond the stated maximum.
            ```


            Try one more small check before moving to the task.

            ```predict
            print(4 >= 4)
            print(4 > 4)
            ---
            Equality reaches an inclusive maximum even though a strict greater-than comparison remains False.
            ```

            **Watch out:** Do not let the step limit replace the final-answer check. The loop must stop for either reason, including an early final reply.

            **In short:** A completed-call count reaches its limit at equality, and a final answer can stop earlier.
        ''',
        "prompt": r'''
            The supplied stop checker allows one call beyond the limit. Fix that boundary while retaining early completion.

            **Your job:** `should_stop(step, max_steps, reply)`

            **What goes in**
            - `step`: int, how many steps have already run (starts at 1), e.g. `3`
            - `max_steps`: int, the limit, e.g. `3`
            - `reply`: the latest model reply dict, e.g. `{"type": "tool", ...}`

            **What comes out**
            - `True` if the reply's `"type"` is `"final"` **or** `step` has reached
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
            "Examine the comparison at the exact limit, not only above it.",
            "The final-reply test is a separate valid reason to stop.",
            "Keep both stop reasons, make the budget boundary inclusive, and check below, equal and above the maximum.",
        ],
    },
    {
        "id": "agents-s4",
        "title": "Call a tool by name",
        "difficulty": 0,
        "lesson": r'''
            ## Connect a tool name to a callable function

            The model supplies a tool name as text and arguments as named values. Your program needs to connect that text to real code. A dictionary can hold functions, so looking up the name gives you the function to call.

            ```python
            def label(word, suffix="!"):
                return word + suffix
            registry = {"label": label}
            chosen = registry["label"]
            values = {"word": "Ready", "suffix": "?"}
            print(chosen(**values))
            # Ready?
            ```

            The dictionary value is the function itself, without parentheses. Parentheses would run it while constructing the registry. The later lookup selects the function, and the call actually runs it.

            This name-to-function mapping is a **tool registry**. The double star in a call turns a dictionary's entries into **keyword arguments**: each key names a parameter. It is the reverse of collecting extra keyword arguments in a function definition.

            The spelling of an argument key must agree with the callable's parameter name. A missing required parameter or an unexpected key can raise TypeError. An empty dictionary contributes no arguments, which is useful for a tool whose signature takes none. This step assumes the requested tool exists; later steps will handle unknown names and tool failures. Return the function's result as it is, because tools may return numbers, lists or other values.

            ```predict
            def greet(name):
                return "Hello " + name
            arguments = {"name": "Mira"}
            print(greet(**arguments))
            ---
            The name key becomes the name parameter, so the unpacked call behaves like passing name="Mira".
            ```


            Try one more small check before moving to the task.

            ```predict
            def ready():
                return "ready"
            print(ready(**{}))
            ---
            An empty argument dictionary contributes no keyword arguments, so the no-argument function runs.
            ```

            **Watch out:** Putting a function call in the registry stores its result rather than the callable. Store the function, then call it only after a request arrives.

            **In short:** Look up the callable by name and unpack the request's named arguments into its call.
        ''',
        "prompt": r'''
            A model request names a registered tool and supplies named arguments. Dispatch that one request.

            **Your job:** `call_tool(tools, name, args)`

            **What goes in**
            - `tools`: a dict mapping tool names to functions, e.g. `{"add": add}`
            - `name`: str, the tool to run, e.g. `"add"`
            - `args`: dict of keyword arguments, e.g. `{"a": 2, "b": 3}`

            **What comes out**
            - whatever the tool function returns

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
            "Remember that a dictionary can hold a function rather than only ordinary data.",
            "Selecting the callable and running it are two separate operations.",
            "Retrieve the requested function, pass the argument dictionary as named parameters, and return whatever that call produced.",
        ],
    },
    {
        "id": "agents-s5",
        "title": "Write it in the log",
        "difficulty": 0,
        "lesson": r'''
            ## Keep an ordered record of actions

            An agent gives an unexpected answer. You need to see which tools actually ran, with which inputs and results. Add a record after each action so you can inspect the run in the order it happened.

            ```python
            trail = [{"number": 1, "name": "find"}]
            returned = trail.append({"number": 2, "name": "read"})
            print(returned)
            # None
            print([entry["name"] for entry in trail])
            # ['find', 'read']
            ```

            Appending adds the new dictionary to the end of the existing list. Earlier entries stay in their original order. The append method returns None; it does not return the updated list.

            A record used to inspect past actions is an **audit log**. It should identify the step, action, arguments and result. Those fields help you distinguish a faulty tool result from a wrong request or a later reasoning mistake. The task gives the exact field names so other code can read the record consistently.

            This function deliberately changes the list supplied by the caller. That is different from a function required to return a new copy. The caller may already have a reference to the list and expects to see the new entry there. Return that same list after appending. Do not mistake the returned value of the method for the list whose contents it changed.

            ```quiz
            After entries.append(new_entry), what value does append return?
            - [x] None :: The method changes the existing list and has no updated-list return value.
            - [ ] The updated list :: The list itself changed, but the method result is a different value.
            ```


            Try one more small check before moving to the task.

            ```predict
            entries = ["old"]
            entries.append("new")
            print(entries)
            ---
            Appending preserves the old entry and places the new entry at the end.
            ```

            **Watch out:** Returning the result of append gives the caller None. Return the log object when the contract promises the updated log.

            **In short:** Append one action record and return the same log list, preserving its earlier entries.
        ''',
        "prompt": r'''
            Keep an ordered record of what the agent did. Add exactly one action record to the supplied log.

            **Your job:** `record(log, step, tool, args, result)`

            **What goes in**
            - `log`: a list of earlier entries (may be empty)
            - `step`: int, e.g. `1`
            - `tool`: str, the tool name, e.g. `"search"`
            - `args`: dict, the tool arguments, e.g. `{"q": "tea"}`
            - `result`: whatever the tool returned, e.g. `"3 hits"`

            **What comes out**
            - the same `log` list, with one new entry added at the end

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
            "Distinguish the list being changed from the value returned by its method.",
            "The task needs one new dictionary at the end of the original list.",
            "Build the specified record, append it without replacing the log, and then return the same list object.",
        ],
    },
    {
        "id": "agents-s6",
        "title": "Errors don't stop the agent",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Keep a tool failure visible without ending the loop

            A requested tool can fail because data is missing or an argument is invalid. If the exception escapes the loop, the agent cannot choose a recovery action. Catch the failure at the tool boundary and turn it into information the next call can use.

            ```python
            def read_item(items, index):
                return items[index]
            for position in [0, 3]:
                try:
                    print(read_item(["first"], position))
                except IndexError as problem:
                    print(type(problem).__name__)
            print("continue")
            # first
            # IndexError
            # continue
            ```

            The first call returns normally. The second raises while reading the list, so Python jumps to the except branch. After that branch finishes, the program continues. Catching the error changes control flow; it does not make the failed lookup succeed.

            An error object has a class, and `type(problem).__name__` exposes that class name as text. `str(problem)` gives its explanatory message. Those are distinct pieces: a name identifies the kind of error, while a message provides details about this occurrence.

            The next lesson uses this information as a tool **observation**, a result sent back to the model. Reporting errors makes recovery possible, but it does not guarantee that the next model request will recover correctly. Keep an independent step limit. In real applications, error messages may contain sensitive values, so decide what may be exposed rather than forwarding arbitrary details without review.

            ```match
            try :: attempt an operation that may fail
            except :: handle a matching raised error
            exception class name :: the kind of failure, such as IndexError
            ---
            A caught error remains a failed operation even though execution can continue.
            ```


            Try one more small check before moving to the task.

            ```predict
            try:
                int("not a number")
            except ValueError as fault:
                print(type(fault).__name__)
            ---
            The conversion error is caught and its class name becomes visible without ending the program.
            ```

            **Watch out:** Python skips the remaining try-body lines after an exception. Include that jump when predicting the print order.

            **In short:** Catch tool failures at their boundary and preserve useful information for recovery.
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

            Follow each printed line in execution order. Changes to a variable affect later lines; they do not change output that was already printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Locate the operation that raises and the handler that matches it.",
            "A caught exception skips the rest of the try body, then execution continues afterward.",
            "Follow each call in order, distinguish successful output from the handler's class name and message, and include the final print.",
        ],
    },
    {
        "id": "agents-1",
        "title": "A scripted fake model",
        "difficulty": 1,
        "lesson": r'''
            ## Make repeatable replies for an agent test

            A real model can choose a different reply on each call. That makes it hard to test your loop's exact behaviour. A test can supply a function that remembers its place in a prewritten sequence instead.

            ```python
            def make_reader(values):
                iterator = iter(values)
                def read():
                    return next(iterator)
                return read
            reader = make_reader(["north", "south"])
            print(reader())
            # north
            print(reader())
            # south
            ```

            The outer function creates the iterator once. The returned inner function keeps access to it and advances it on every call. Calling the outer function again creates a separate iterator, so separate readers do not share progress.

            An inner function retaining access to values from its enclosing function is a **closure**. A repeatable model made from a sequence of chosen replies is a **scripted fake**. You can use either an iterator or a stored position to track progress; the important part is that the state belongs to that particular fake.

            Your test interface still accepts the conversation argument, even though the scripted fake ignores its contents. That lets it stand in for the real model function without changing the loop. When the sequence ends, the task requires a specific error. Reaching that point should reveal an unexpected extra call rather than returning an invented reply. Reading must also leave the original list unchanged.

            ```quiz
            Two fake models are created from the same reply list. Should calling one advance the other?
            - [x] No; each model has its own position. :: Independent progress lets separate tests use the same script without interference.
            - [ ] Yes; the list must track their shared position. :: Changing shared progress would make the second model depend on calls to the first.
            ```


            Try one more small check before moving to the task.

            ```predict
            a = iter(["one", "two"])
            b = iter(["one", "two"])
            print(next(a), next(a), next(b))
            ---
            The two iterators have independent positions; advancing a does not advance b.
            ```

            **Watch out:** A counter stored outside the factory can be shared accidentally. Keep each fake's progress inside its own creation call.

            **In short:** A scripted fake returns chosen replies in order using state private to that instance.
        ''',
        "prompt": r'''
            Repeatable model replies let you test the loop without network calls. Build an independent scripted fake for each creation call.

            **Your job:** `make_scripted_model(replies)`

            **What goes in**
            - `replies`: a list of reply dicts, e.g.
              `[{"type": "tool", "tool": "add", "args": {"a": 1, "b": 2}}, {"type": "final", "text": "3"}]`

            **What comes out**
            - a function `model(messages)` that returns the next reply from the list
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
            "Where can the returned function keep progress between calls?",
            "Progress belongs to the created model, while the original replies stay intact.",
            "Create private progress, return a callable accepting messages, advance one reply per call, and raise the required exhaustion error when none remain.",
        ],
    },
    {
        "id": "agents-2",
        "title": "Tool errors become observations",
        "difficulty": 1,
        "lesson": r'''
            ## Turn failed requests into usable observations

            A model asks for an unavailable tool, or a registered tool raises while running. Neither case should look like a successful result. Report a clear failure while keeping the loop able to ask for a different action.

            ```python
            def lookup():
                raise LookupError("record unavailable")
            try:
                lookup()
            except LookupError as failure:
                print(type(failure).__name__, str(failure))
            # LookupError record unavailable
            ```

            The class name identifies the error category; the message explains this occurrence. They can be combined into the error format promised by the task. A successful tool result, on the other hand, should remain in its original type.

            A tool result supplied to a later model call is an **observation**. An observation can report success or failure. For an unknown name, check the registry before looking up or executing anything. For a known name, attempt the call and catch ordinary exceptions at that boundary.

            This small helper is safe in the specific sense that it converts the stated tool errors into return values. It is not a security sandbox and cannot undo side effects a failing tool already performed. Real applications should also decide which error details may be sent to a model or user. Catching Exception does not catch every possible process-level interruption, so avoid claiming the function can never fail under any circumstances.

            ```predict
            try:
                raise ValueError("bad choice")
            except Exception as issue:
                print(type(issue).__name__)
                print(str(issue))
            ---
            The error class name and explanatory text are two separate values. Both can be used to construct a failure observation.
            ```


            **Watch out:** An unknown tool should not be invoked. Keep its failure path separate from exceptions raised by an existing tool.

            **In short:** Return successful values unchanged and convert the specified failures to observations.
        ''',
        "prompt": r'''
            Give the next turn a useful observation even when a tool is unknown or raises an ordinary exception.

            **Your job:** `safe_call_tool(tools, name, args)`

            **What goes in**
            - `tools`: dict of name -> function
            - `name`: str, the requested tool
            - `args`: dict of keyword arguments

            **What comes out**
            - the tool's return value, or an error string

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
            "Consider an unknown name separately from a registered tool that raises.",
            "The registry check happens before the attempted call.",
            "Reject unknown names without execution; otherwise attempt the unpacked call, preserve its successful value, or report the caught class name and message.",
        ],
    },
    {
        "id": "agents-3",
        "title": "One turn: think, act, observe",
        "difficulty": 1,
        "lesson": r'''
            ## Give the next model call the tool result

            The agent has looked something up, but the next model call will not know that unless you include the result. Keep the request and its observation in the conversation so the next reply can use what happened.

            ```python
            history = [{"role": "user", "content": "Find the opening time"}]
            history.append({"role": "assistant", "action": "lookup"})
            history.append({"role": "tool", "content": str(9)})
            for message in history:
                print(message["role"])
            # user
            # assistant
            # tool
            ```

            The original user request remains first. The action request comes next, followed by the returned observation. Turning the numerical result into text makes it suitable for a content field that expects a string.

            The conversation is the agent's **message history**. Our teaching format records an assistant request and a tool result as two dictionary entries. Real provider formats may require additional identifiers, but the principle is the same: connect a returned result to the request that produced it.

            One step of the loop makes one model call. If that call returns a final answer, this helper returns the text without adding tool entries. If it requests a tool, the helper runs the tool, appends both entries in the agreed order, and signals that there is no final answer yet. The next step reuses the updated list. Passing the unchanged original history again would discard the new information.

            ```quiz
            The tool result was computed but never added to the conversation. What does the next call know?
            - [x] It receives no new observation from that tool. :: The model only receives the context your code supplies to that call.
            - [ ] It automatically remembers the Python result. :: A local Python value is not automatically part of a later model request.
            ```


            **Watch out:** A final answer and a tool observation are different kinds of result. Only the tool branch adds the request-and-result pair in this exercise.

            **In short:** One turn either returns a final answer or records a tool request and its observation.
        ''',
        "prompt": r'''
            Run one model turn. A tool turn must make its request and result available to the next call.

            **Your job:** `agent_step(model, tools, messages)`

            **What goes in**
            - `model`: a function; `model(messages)` returns a reply dict (`"type"` is `"tool"` or `"final"`)
            - `tools`: dict of name -> function
            - `messages`: the conversation so far (a list of dicts); you will add to it

            **What comes out**
            - the final answer text (str) if the model finished, otherwise `None`

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
            "Separate the final-answer branch from the tool-request branch.",
            "A tool turn adds two messages; a final turn leaves the conversation unchanged.",
            "Call the model once with the current list, return final text when present, otherwise execute and append the request then the stringified result.",
        ],
    },
    {
        "id": "agents-4",
        "title": "Check the budget",
        "difficulty": 1,
        "lesson": r'''
            ## Check the budgets in their agreed order

            An agent has used a few calls and many tokens. One allowance may still have room while another is exhausted. Check each configured limit before starting another turn, and give the caller a clear reason to stop.

            ```python
            consumed = {"calls": 2, "words": 600}
            allowance = {"calls": 3, "words": 500}
            for label, maximum in allowance.items():
                print(label, consumed.get(label, 0) >= maximum)
            # calls False
            # words True
            ```

            Each comparison asks about one resource. The second is already above its maximum, so more room in the first resource cannot justify continuing. Equality also means the allowance has been used up.

            An agreed maximum resource use is a **budget**. A checker can work with any named resources instead of hard-coding steps, tokens and dollars. The limits dictionary determines what needs checking. Entries present only in the usage dictionary are irrelevant to this particular decision.

            The task returns the first reached limit in the limits dictionary's order. That makes the result deterministic when several limits are reached together. A missing usage entry counts as zero under this contract. In a production system, missing measurements can also mean incomplete accounting, so the choice to treat them as zero needs to be deliberate. Here follow the supplied policy and keep the inclusive boundary consistent across all keys.

            ```quiz
            Both configured limits are reached. Which one should this checker return?
            - [x] The first in the limits dictionary. :: The contract uses limit order to make simultaneous failures deterministic.
            - [ ] Whichever has the largest numerical value. :: Different resources have different units, so comparing their raw maxima is not meaningful.
            ```


            Try one more small check before moving to the task.

            ```predict
            counts = {"calls": 2}
            print(counts.get("cost", 0))
            ---
            The stated missing-usage policy supplies zero for an absent resource key.
            ```

            **Watch out:** A token count and a dollar amount use different units. Compare each with its own limit rather than comparing resources with each other.

            **In short:** Check configured budgets inclusively and return the first exhausted one in limit order.
        ''',
        "prompt": r'''
            Check the configured resource allowances before another turn and report the first one already reached.

            **Your job:** `check_budget(used, limits)`

            **What goes in**
            - `used`: dict of what was spent so far, e.g. `{"steps": 3, "tokens": 1200, "cost": 0.02}`
            - `limits`: dict of maximums, e.g. `{"steps": 5, "tokens": 1000}`

            **What comes out**
            - the name (str) of the first limit that has been reached, or `None` if none has

            **Rules**
            - A limit is reached when the recorded amount is greater than or equal to its configured limit.
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
            "Let the limits dictionary define both the resource names and their checking order.",
            "Use the same inclusive reached-boundary for every resource.",
            "Visit configured limits in order, obtain each used amount with the stated default, and return immediately for the first reached allowance.",
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
            ## Stop a fixed sequence when a gate fails

            Your app always drafts an outline, writes text, then checks style. Those stages are known in advance, so you can connect them in a fixed sequence. A failed check should prevent later stages from using unsuitable input.

            ```python
            operations = [str.strip, str.upper]
            value = "  draft  "
            for number, operation in enumerate(operations):
                value = operation(value)
                print(number, repr(value))
            # 0 'draft'
            # 1 'DRAFT'
            ```

            Each operation receives the value returned by the preceding one. The first removes outer whitespace; the second changes case. The order is part of the program, rather than a choice supplied by a model on each turn.

            A predefined sequence is a **workflow**. When each stage is a model call using the previous output, it is often called **prompt chaining**. A yes-or-no check between stages is a **gate**. In this task, the steps are fake functions and the gate runs after every completed step.

            A gate failure returns both the failed stage's index and its output. That information helps the caller understand where the workflow stopped. Later operations must not run, because they would consume a rejected intermediate value. With no steps there is no intermediate output to check; the contract keeps the original input as a successful result. This differs from checking the starting input before the first step.

            ```fill
            text = "  "
            clean = text.strip()
            print(___(clean))
            ---
            - [x] bool :: An empty cleaned string is false, which can reject a blank intermediate output.
            - [ ] str :: Converting to text does not produce the promised yes-or-no gate result.
            ```


            **Watch out:** Run the gate on the step's returned value, not its input. The step may fix a problem or introduce one.

            **In short:** A workflow passes each output to the next stage and stops when its post-step gate fails.
        ''',
        "prompt": r'''
            Run a fixed sequence of fake model-call steps, rejecting unsuitable intermediate outputs before later steps run.

            **Your job:** `run_chain(steps, text, gate)`

            **What goes in**
            - `steps`: a list of functions, each `step(text) -> str`
            - `text`: the starting string
            - `gate`: a function `gate(output) -> bool` (True = good, keep going)

            **What comes out**
            - a dict

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
            "Distinguish the fixed step order from an agent choosing its next action.",
            "Each check belongs after its corresponding step and sees that step's output.",
            "Carry the latest output through the functions, check it after every step, return failure details immediately on rejection, and preserve the input for an empty chain.",
        ],
    },
    {
        "id": "agents-6",
        "title": "The full agent loop",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## Combine the loop with a strict call allowance

            You can now recognise final replies, dispatch tools and save observations. The complete runner must coordinate them while making no more than the allowed number of model calls. Plan the finish path and the still-working path separately.

            ```python
            allowed = 3
            for turn in range(allowed):
                print("attempt", turn + 1)
            # attempt 1
            # attempt 2
            # attempt 3
            ```

            The range contains three values, so the body has three opportunities to run. The displayed step numbers begin at one, even though the range begins at zero. A final-answer branch can stop before all opportunities are used.

            Putting it together means counting model calls as steps, including a call that immediately returns a final answer. Tool calls produce both conversation entries and audit records. The conversation lets the model use observations; the audit log lets a person inspect actions afterward. They have distinct interfaces even though they describe the same action.

            A final reply on the last allowed call still counts as completion. Only a run that uses its entire allowance without a final reply stops for the maximum-step reason. Never make an extra model call to see whether it would have finished. The reason, answer and step count in the returned report should agree with the branch that actually ended the run.

            ```quiz
            A final answer arrives on the last allowed model call. Which stop reason applies?
            - [x] Final answer. :: The permitted call produced completion, so the run finished within its allowance.
            - [ ] Maximum steps. :: The maximum-step reason applies when the allowance ends without a final reply.
            ```


            **Watch out:** Counting only tool requests undercounts model calls. A final response consumes a step too, and must appear in the reported count.

            **In short:** The complete loop counts every model call, records tools, and reports the reason it ended.
        ''',
        "prompt": r'''
            Coordinate model replies, tools, observations and an audit log within a strict model-call limit.

            **Your job:** `run_agent(model, tools, task, max_steps=5)`

            **What goes in**
            - `model`: function, `model(messages)` returns `{"type": "tool", "tool": name, "args": {...}}`
              or `{"type": "final", "text": "..."}`
            - `tools`: dict of name -> function
            - `task`: str, the user's request, e.g. `"What is 2 + 3?"`
            - `max_steps`: int, the most model calls allowed

            **What comes out**
            - a dict `{"answer": ..., "stop_reason": ..., "steps": ..., "log": [...]}`

            **Rules**
            - Start with a one-item conversation containing a user message whose content is `task` and pass this list to every model call.
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
            "Combine the earlier completion, dispatch, observation and logging ideas around one bounded loop.",
            "The model-call count is different from the number of tool actions.",
            "Begin with the task message, make at most the allowed calls, return final text when encountered, and otherwise execute and record each tool before reporting exhaustion.",
        ],
    },
    {
        "id": "agents-7",
        "title": "A registry with human approval",
        "difficulty": 2,
        "lesson": r'''
            ## Require approval before running a risky tool

            A search is usually reversible; sending a message or deleting a file may not be. The registry should know which tools need approval and refuse them when no approving person is available. A request alone is not permission.

            ```python
            marked_risky = {"publish"}
            requests = [("lookup", True), ("publish", False)]
            for label, approved in requests:
                may_run = label not in marked_risky or approved
                print(label, may_run)
            # lookup True
            # publish False
            ```

            The ordinary lookup needs no approval in this example. The risky publish request has a false approval result, so it cannot run. The real registry calls an approval function only when a known risky tool is requested.

            **Human approval** is a decision tied to a proposed action and its arguments. The approver must be able to see what would run; approval for one request does not authorise a different request. Tests supply a fake approval function so both permission paths can be checked without carrying out irreversible actions.

            Putting it together means recording three outcomes: an unknown name, a denied request or a successfully run tool. Unknown tools are rejected before asking anyone to approve them. A missing approval function counts as refusal for a risky tool. Safe tools bypass that function entirely. The history records requests in order, allowing a reviewer to see that a refused action was actually blocked.

            ```match
            unknown request :: reject before seeking approval
            ordinary tool :: run without an approval callback
            risky tool without approval :: deny without executing
            ---
            Lookup and approval both precede risky execution.
            ```


            **Watch out:** Calling the tool before requesting approval defeats the gate. The approval decision must precede every risky execution.

            **In short:** A registry runs risky tools only after approval and records unknown, denied and successful requests.
        ''',
        "prompt": r'''
            A registry must distinguish ordinary tools from tools requiring human approval. Keep an ordered history of outcomes.

            **Your job:** class `ToolRegistry`

            **What goes in**
            - `ToolRegistry()` starts empty; attribute `history` is a list (starts `[]`).
            - `register(name, fn, risky=False)`: add a tool.
            - `names()`: returns a sorted list of registered tool names.
            - `call(name, args, approve=None)`: run a tool and return a result or a status string.
              `approve` is a function `approve(name, args) -> bool` (a human saying yes/no), or `None`.

            **What comes out**
            - `names()` returns registered names in sorted order. `call()` returns the raw successful tool value or the specified unknown/denied text. `history` records the corresponding outcomes in request order.

            **Rules for `call`**
            - Unknown tool: return `"error: unknown tool <name>"` and add `(name, "unknown")` to `history`.
            - For a risky tool, call `approve(name, args)` once when an approver is supplied. If `approve` is `None` or returns a false value, do **not**
              run the tool; return `"denied: <name>"` and add `(name, "denied")` to `history`.
            - Otherwise (safe tool, or risky and approved): return `fn(**args)` and add `(name, "ok")` to `history`.
            - `approve` is only called for risky tools.



            **Examples**
            ```python
            def send_email(to):
                return "sent to " + to

            reg = ToolRegistry()
            reg.register("add", lambda a, b: a + b)
            reg.register("send_email", send_email, risky=True)
            reg.names()                                            # ["add", "send_email"]
            reg.call("add", {"a": 1, "b": 2})                      # returns 3
            reg.call("send_email", {"to": "x@y.z"})                # returns "denied: send_email"
            reg.call("send_email", {"to": "x@y.z"}, lambda n, a: True)   # returns "sent to x@y.z"
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
            "Store the callable and its risk flag as separate registry information.",
            "An unknown name and a known denied tool have different history outcomes.",
            "Resolve the tool, request approval only if it is risky, record refusals without execution, and otherwise run and record the successful call.",
        ],
    },
    {
        "id": "agents-8",
        "title": "Agent memory",
        "difficulty": 2,
        "lesson": r'''
            ## Keep recent messages and lasting facts separately

            A long conversation no longer fits into the next model request. You can drop old chat messages, but the user's preferred language may still matter. Keep a rolling message window and explicit facts as separate pieces of state.

            ```python
            conversation = ["old question", "old answer", "new question"]
            print(conversation[-2:])
            # ['old answer', 'new question']
            known = {"language": "Spanish", "city": "Madrid"}
            known["language"] = "English"
            print(list(known))
            # ['language', 'city']
            ```

            The slice retains the latest two items in their original order. The fact update replaces a value without moving its existing key to the end. These behaviours support a predictable context builder.

            The data your application retains and supplies to later model calls is its **memory**. A **rolling window** keeps only a bounded set of recent messages. Explicit facts survive independently of that window. This simplified exercise assumes each model call receives only the context your code constructs; it does not rely on a provider-managed conversation store.

            Building context is a read operation. Return a fresh list and fresh dictionaries for the stored messages so a caller changing that result cannot corrupt the memory. Copying only the outer list would still share its dictionary entries. The task's message values are strings, so a shallow copy of each message dictionary is sufficient for the specified isolation.

            ```quiz
            You return a new list containing the original message dictionaries. Can changing a returned dictionary affect memory?
            - [x] Yes, the inner dictionaries are still shared. :: Copying the outer container alone does not copy its contained dictionaries.
            - [ ] No, a new list isolates every level. :: Nested objects keep their identity unless they are copied too.
            ```


            **Watch out:** Recent-message trimming and fact retention are different policies. Dropping an old message must not silently erase an explicitly remembered fact.

            **In short:** Keep bounded recent messages and lasting facts, then build an isolated context view.
        ''',
        "prompt": r'''
            Retain recent chat messages without losing explicit facts. Return context that callers can modify without changing stored memory.

            **Your job:** class `AgentMemory`

            **What goes in**
            - `AgentMemory(max_messages)`: `max_messages` is an int, the most messages to keep.
            - `add(role, content)`: store `{"role": role, "content": content}`. If there are now more than
              `max_messages` messages, drop the **oldest** ones so exactly `max_messages` remain.
            - `remember(key, value)`: store a fact (a later call with the same key replaces the value).
            - `context()`: returns a new list of message dicts to send to the model.

            **What comes out**
            - `context()` returns a new list: an optional facts system message followed by retained messages oldest first. Both the returned list and its message dictionaries are independent of stored memory.

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
            "Separate message-window state from the facts that should survive it.",
            "The context result must isolate both its list and its message dictionaries.",
            "Trim oldest messages after additions, update facts by key, construct the required facts message when needed, then append copies of recent messages.",
        ],
    },
    {
        "id": "agents-9",
        "title": "Budgets and error recovery",
        "difficulty": 3,
        "prompt": r'''
            Combine call and token limits with recovery from tool failures. Report exactly why the run ended.

            **Your job:** `run_budgeted_agent(model, tools, task, max_steps, max_tokens, max_errors=2)`

            **What goes in**
            - `model(messages)` returns a reply dict that always has a `"tokens"` key (int, tokens used by that call):
              `{"type": "tool", "tool": name, "args": {...}, "tokens": 120}` or `{"type": "final", "text": "...", "tokens": 40}`
            - `tools`: dict name -> function; `task`: str; limits are ints

            **What comes out**
            - `{"answer": str or None, "stop_reason": str, "steps": int, "tokens": int}`

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
            "The stop reasons have a specified priority within each turn.",
            "Token usage is counted for every model call, while consecutive errors reset after a successful tool.",
            "Follow the ordered turn rules: count usage, honour final replies, check tokens before tool execution, observe tool outcomes, update the consecutive-error count, and report the applicable stopping reason.",
        ],
    },
    {
        "id": "agents-10",
        "title": "A supervised agent",
        "difficulty": 3,
        "prompt": r'''
            Run a supervised agent whose denied and failed tools are observed and audited while its call allowance remains bounded.

            **Your job:** `run_supervised_agent(model, tools, task, risky, approve, max_steps=5)`

            **What goes in**
            - `model(messages)` returns `{"type": "tool", "tool": name, "args": {...}}` or `{"type": "final", "text": "..."}`
            - `tools`: dict name -> function; `task`: str
            - `risky`: a set of tool names that need approval, e.g. `{"delete_file"}`
            - `approve`: function `approve(name, args) -> bool`

            **What comes out**
            - `{"answer": str or None, "stop_reason": "final" or "max_steps", "audit": [...]}`

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
            "Separate permission, tool execution and reporting for each request.",
            "A denial or tool error becomes an observation and audit entry, rather than automatically ending the loop.",
            "Resolve each requested name, seek approval only for known risky tools, run permitted calls safely, record every tool-request outcome, and keep looping until final completion or the call limit.",
        ],
    },
]
