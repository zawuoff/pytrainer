TOPIC = {
    "id": "llm-basics",
    "title": "LLM API Basics",
    "track": "llm-apps",
    "order": 1,
    "requires": ["api-data", "classes"],
    "summary": """
        What an LLM API call really is: messages and roles, model parameters, reading
        OpenAI- and Anthropic-shaped responses, tokens and cost, stop reasons, streaming
        and handling rate limits - practised with fake clients, no network.
    """,
    "concepts": ["chat completion", "messages", "roles", "system prompt", "temperature",
                 "max_tokens", "response shapes", "usage and tokens", "cost math",
                 "stop reasons", "streaming deltas", "rate limits", "retries with backoff",
                 "dependency injection"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["llm", "model", "token", "messages", "role", "system prompt", "temperature",
                 "max_tokens", "response", "usage", "cost", "stop reason", "finish_reason",
                 "streaming", "rate limit", "retry"],
    "cards": [
        {
            "syntax": '{"role": "user", "content": text}',
            "explain": "One chat message. The role is \"system\", \"user\" or \"assistant\". A conversation is a list of these dicts.",
            "example": r'''
                messages = [{"role": "system", "content": "Be terse."}]
                messages.append({"role": "user", "content": "Hi"})
                print([m["role"] for m in messages])
                # ['system', 'user']
            ''',
        },
        {
            "syntax": 'r["choices"][0]["message"]["content"]',
            "explain": "The reply text of an OpenAI response. The stop reason is beside the message, under \"finish_reason\".",
            "example": r'''
                r = {"choices": [{"message": {"content": "Paris."},
                                  "finish_reason": "stop"}]}
                choice = r["choices"][0]
                print(choice["message"]["content"])
                # Paris.
                print(choice["finish_reason"])
                # stop
            ''',
        },
        {
            "syntax": '[b["text"] for b in r["content"] if b["type"] == "text"]',
            "explain": "The text blocks of an Anthropic response. Join them with \"\".join to get the reply text.",
            "example": r'''
                r = {"content": [{"type": "text", "text": "Hel"},
                                 {"type": "text", "text": "lo"}],
                     "stop_reason": "end_turn"}
                parts = [b["text"] for b in r["content"] if b["type"] == "text"]
                print("".join(parts), r["stop_reason"])
                # Hello end_turn
            ''',
        },
        {
            "syntax": "tokens * price / 1_000_000",
            "explain": "Cost in dollars of one side of a call. Prices are per million tokens. Add the input cost and the output cost.",
            "example": r'''
                usage = {"prompt_tokens": 2000, "completion_tokens": 400}
                cost_in = usage["prompt_tokens"] * 3.0 / 1_000_000
                cost_out = usage["completion_tokens"] * 15.0 / 1_000_000
                print(cost_in + cost_out)
                # 0.012
            ''',
        },
        {
            "syntax": 'chunk["choices"][0]["delta"].get("content") or ""',
            "explain": "The new text in one OpenAI stream chunk. Skip a chunk whose choices list is empty, then join the pieces.",
            "example": r'''
                chunks = [{"choices": [{"delta": {"role": "assistant"}}]},
                          {"choices": [{"delta": {"content": "Hi"}}]}]
                text = ""
                for chunk in chunks:
                    delta = chunk["choices"][0]["delta"]
                    text += delta.get("content") or ""
                print(text)
                # Hi
            ''',
        },
        {
            "syntax": 'getattr(err, "status_code", None)',
            "explain": "The status code of an error, or None if it has none. Retry 429 and 500 to 599. Raise every other error again.",
            "example": r'''
                class APIError(Exception):
                    status_code = 429
                try:
                    raise APIError("slow down")
                except Exception as err:
                    code = getattr(err, "status_code", None)
                    print(code, code == 429)
                # 429 True
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: calling an LLM

### What an LLM does

A **large language model (LLM)** is a program that takes a list of tokens and predicts the
next token. This course calls it the **model**. A **token** is a small piece of text: a
short word, part of a longer word or a punctuation mark. (It is not the Bearer token of the
HTTP chapter, which is a secret key.) The model appends the predicted token to the list and
predicts again. It repeats this until it reaches a stop condition.

### One API call

An LLM API call is an HTTP POST. You send a **request**: a model name, a list of messages
and a few parameters. You get back a JSON **response**: the reply text, the reason
generation stopped and the token counts. The **provider** is the company that runs the
model. It stores nothing between calls, so you send the whole conversation in every request.

The text you send is the **prompt**. The text the model generates is the **completion**.
A call that sends chat messages and gets one new message back is a **chat completion**.
The **client** is the code that sends the request.

Step through the stages of one call and read the data at each stage.

```diagram
{"type":"flow","title":"One chat completion call","steps":[{"label":"Build messages","detail":"You build a list of message dicts. Each dict has a role and the text content.","code":"messages = [\n    {\"role\": \"system\", \"content\": \"Be terse.\"},\n    {\"role\": \"user\", \"content\": \"Capital of France?\"},\n]"},{"label":"Send the request","detail":"The client puts the model name, the messages and the parameters into a JSON body. It sends that body with an HTTP POST.","code":"{\"model\": \"gpt-4o-mini\", \"messages\": [...], \"temperature\": 0, \"max_tokens\": 20}"},{"label":"Predict one token","detail":"The provider converts the messages to a list of tokens. The model predicts the next token and appends it to the list.","code":"reply after pass 1: 'Paris'\nreply after pass 2: 'Paris.'"},{"label":"Check the stop condition","detail":"Generation ends when the model predicts its end-of-reply token, or when the reply reaches max_tokens tokens. Otherwise the model predicts another token.","code":"end-of-reply token predicted: finish_reason is 'stop'\nmax_tokens reached: finish_reason is 'length'"},{"label":"Build the response","detail":"The provider converts the generated tokens to text. It returns JSON that holds the text, the stop reason and the token counts.","code":"{\"choices\": [{\"message\": {\"role\": \"assistant\", \"content\": \"Paris.\"},\n              \"finish_reason\": \"stop\"}],\n \"usage\": {\"prompt_tokens\": 14, \"completion_tokens\": 2}}"},{"label":"Read content and usage","detail":"Your code reads the reply text, the stop reason and the token counts from the response dict.","code":"response[\"choices\"][0][\"message\"][\"content\"]   # 'Paris.'\nresponse[\"choices\"][0][\"finish_reason\"]        # 'stop'\nresponse[\"usage\"][\"completion_tokens\"]         # 2"}],"loop":{"from":3,"to":2,"label":"while no stop condition is met"}}
```

### Messages

The conversation is a list of dicts in order. Each dict has a `"role"` and a `"content"`.
A `system` message holds instructions, a `user` message holds what the person typed and
an `assistant` message holds an earlier reply from the model.

```python
messages = [
    {"role": "system", "content": "Be terse."},
    {"role": "user", "content": "Capital of France?"},
]
messages.append({"role": "assistant", "content": "Paris."})
print([m["role"] for m in messages])
# ['system', 'user', 'assistant']
```

The text of the system message is the **system prompt**. OpenAI takes it as a message in
the list, as above. Anthropic takes it in a separate `"system"` key of the request body,
next to `"messages"`.

### Parameters

`model` names the model that runs. `max_tokens` is the maximum number of tokens in the
reply. `temperature` controls how the next token is picked: at `0` the model picks the
most likely token almost every time, and higher values pick less likely tokens more often.

### Reading responses

The two providers return different shapes. In an Anthropic response, `"content"` is a list
of **content blocks**: dicts with a `"type"` key. A text block is
`{"type": "text", "text": "..."}`.

| | OpenAI Chat Completions | Anthropic Messages |
| --- | --- | --- |
| text | `r["choices"][0]["message"]["content"]` | join `b["text"]` for blocks in `r["content"]` with `type == "text"` |
| stop | `choices[0]["finish_reason"]`: `stop`, `length` | `r["stop_reason"]`: `end_turn`, `max_tokens`, `stop_sequence` |
| usage | `usage.prompt_tokens`, `usage.completion_tokens` | `usage.input_tokens`, `usage.output_tokens` |

```python
openai_response = {
    "choices": [{"message": {"role": "assistant", "content": "Paris."}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 14, "completion_tokens": 2},
}
anthropic_response = {
    "content": [{"type": "text", "text": "Paris."}],
    "stop_reason": "end_turn",
    "usage": {"input_tokens": 14, "output_tokens": 2},
}
print(openai_response["choices"][0]["message"]["content"])
# Paris.
print("".join(b["text"] for b in anthropic_response["content"] if b["type"] == "text"))
# Paris.
print(openai_response["choices"][0]["finish_reason"], anthropic_response["stop_reason"])
# stop end_turn
```

A stop reason of `length` or `max_tokens` means the reply reached the token limit. The
text is **truncated**: it ends before the model finished. (Other stop reasons exist for
tool use. The Tool Calling chapter covers them. Ignore them here.)

### Cost

Prices are quoted per million tokens. Input tokens and output tokens have separate prices.

```python
usage = {"prompt_tokens": 2000, "completion_tokens": 400}
in_price, out_price = 3.0, 15.0
cost = usage["prompt_tokens"] * in_price / 1_000_000 + usage["completion_tokens"] * out_price / 1_000_000
print(cost)
# 0.012
```

### Streaming

With **streaming**, the provider sends the reply in small pieces while the model is still
generating it. Each piece is a dict called a **chunk**. The new text in a chunk is called its
**delta**. An OpenAI chunk holds the delta in `choices[0]["delta"]["content"]`. That key can be missing or `None`, and a final usage
chunk can have an empty `choices` list.

```python
chunks = [
    {"choices": [{"delta": {"role": "assistant"}}]},
    {"choices": [{"delta": {"content": "Par"}}]},
    {"choices": [{"delta": {"content": "is."}}]},
    {"choices": [], "usage": {"prompt_tokens": 14, "completion_tokens": 2}},
]
parts = []
for chunk in chunks:
    if chunk["choices"]:
        parts.append(chunk["choices"][0]["delta"].get("content") or "")
print("".join(parts))
# Paris.
```

Anthropic sends **events**: dicts with a `"type"` key. A `content_block_delta` event holds
text in `event["delta"]["text"]`. A `message_delta` event holds the `stop_reason` and the
output `usage`.

### Errors and retries

Status `429` means you are **rate limited**: you sent more requests or tokens per minute
than the provider allows. Statuses `500` to `599` mean the server failed.
Both are temporary, so you retry with **exponential backoff**: wait 1 second, then 2, then
4. Statuses `400`, `401`, `403` and `404` mean the request itself is wrong. A retry sends
the same wrong request, so you raise the error instead.

### Fake clients

**Dependency injection** means a function receives the client as an argument instead of
creating it. A test passes a fake function that returns a fixed response dict. The test
then uses no network, costs nothing and gives the same result on every run.

```python
def fake_client(model, messages):
    return {"choices": [{"message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}]}

def ask(client, question):
    response = client(model="demo", messages=[{"role": "user", "content": question}])
    return response["choices"][0]["message"]["content"]

print(ask(fake_client, "ping"))
# ok
```

## Common mistakes

- You do not append the assistant reply to the history. The next request then lacks that
  reply, so the model cannot use it.
- You call a string method on `content` when it is `None`. An OpenAI reply that only asks
  your code to run a function (finish reason `tool_calls`) has `"content": None`.
- You treat Anthropic `content` as a string. It is a **list** of blocks.
- You change the caller's `messages` list when the function was only asked to read it.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "llm-basics-s1",
        "title": "A conversation is a list",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Messages and roles

            A **large language model (LLM)** is a program that takes a list of tokens and
            predicts the next token. This course calls it the **model**. A **token** is a
            small piece of text, such as a word or part of a word. An LLM API takes your text, converts it to tokens and returns the
            predicted tokens as text. The reply is built one predicted token at a time.

            You send the text as a list of **messages**. Each message is a dict with two keys.
            `"role"` says who wrote the text. `"content"` holds the text.

            ```python
            messages = [
                {"role": "system", "content": "Be terse."},
                {"role": "user", "content": "Rome in May?"},
            ]
            messages.append({"role": "assistant", "content": "Yes."})
            for m in messages:
                print(m["role"], "->", m["content"])
            # system -> Be terse.
            # user -> Rome in May?
            # assistant -> Yes.
            ```

            There are three roles. A `system` message holds instructions for the model. A
            `user` message holds what the person typed. An `assistant` message holds a reply
            the model produced earlier. This layout is called the **chat messages format**, and
            nearly every LLM API uses it.

            Click a cell to read one message.

            ```diagram
            {"type":"list-index","title":"Indexes of messages","name":"messages","items":[{"role":"system","content":"Be terse."},{"role":"user","content":"Rome in May?"},{"role":"assistant","content":"Yes."}]}
            ```

            The API stores nothing between calls. The model's input is only the list you send.
            If you do not append the model's last reply, the next request does not contain it.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            messages = [
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "Hi"},
            ]
            messages.append({"role": "assistant", "content": "Hello!"})
            print(len(messages))
            print(messages[-1]["role"])
            print([m["role"] for m in messages])
        ''',
        "solution": r'''
            3
            assistant
            ['system', 'user', 'assistant']
        ''',
        "explanation": r'''
            The list starts with 2 messages and `append` adds a third, so `len(messages)` is 3.
            `messages[-1]` is the last message, the one with the role `assistant`. The
            comprehension builds a list of every role in order. `print` shows the strings in
            that list with single quotes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "append adds one item to the end of the list.",
            "messages[-1] is the last message; the comprehension collects the \"role\" of each message in order.",
            "Line 1: the new length. Line 2: the role of the appended message. Line 3: a Python list of the three role strings, printed with single quotes.",
        ],
    },
    {
        "id": "llm-basics-s2",
        "title": "Make a user message",
        "difficulty": 0,
        "lesson": r'''
            ## Message helper functions

            A message is a dict with two keys: `"role"` and `"content"`. If you write that
            dict by hand in many places, you will mistype a key or a role at some point, for
            example `"rol"` or `"User"`. A small function that builds the dict keeps the
            spelling in one place.

            ```python
            def system_message(text):
                return {"role": "system", "content": text}

            msg = system_message("Answer in French.")
            print(msg)
            # {'role': 'system', 'content': 'Answer in French.'}
            print(msg["role"])
            # system
            ```

            The function takes the text as its argument and returns a new dict. The role is
            fixed inside the function, so the caller cannot misspell it.

            The role strings are exact and lowercase: `"system"`, `"user"`, `"assistant"`.
            The API rejects a role it does not know, such as `"User"`, with a
            `400 Bad Request` error.

            For a plain text message, `content` is a string. It is not a list or another dict.
        ''',
        "prompt": r'''
            A tiny helper so the rest of the app never typos a message dict.

            **Write:** `user_message(text)`

            - `text`: a `str`, what the user typed, e.g. `"Summarise this"`
            - **Returns:** a `dict` with exactly two keys: `"role"` set to `"user"` and
              `"content"` set to `text`

            **Rules**
            - Keep `text` exactly as given (no stripping, no changes), even if it is empty.

            **Examples**
            ```python
            user_message("Summarise this")   # returns {"role": "user", "content": "Summarise this"}
            user_message("")                 # returns {"role": "user", "content": ""}
            ```
        ''',
        "starter": r'''
            def user_message(text):
                ...
        ''',
        "tests": r'''
            from solution import user_message

            def test_builds_user_message():
                got = user_message("Summarise this")
                assert got == {"role": "user", "content": "Summarise this"}, f"got {got!r}"

            def test_keeps_text_unchanged():
                got = user_message("  Hi!  ")
                assert got == {"role": "user", "content": "  Hi!  "}, f"got {got!r}"

            def test_empty_text():
                got = user_message("")
                assert got == {"role": "user", "content": ""}, f"got {got!r}"
        ''',
        "solution": r'''
            def user_message(text):
                return {"role": "user", "content": text}
        ''',
        "hints": [
            "Return a dict literal with two keys.",
            "One key is \"role\" with the fixed value \"user\"; the other is \"content\" with the parameter.",
            "Write one line: return a dict with \"role\": \"user\" and \"content\": text.",
        ],
    },
    {
        "id": "llm-basics-s3",
        "title": "Build the request body",
        "difficulty": 0,
        "lesson": r'''
            ## The request body

            A request to an LLM API holds the model name, the messages and a few
            **parameters**: named settings that control how the reply is generated.

            `max_tokens` is the maximum number of tokens in the reply. Generation stops when
            the reply reaches that count, even in the middle of a sentence.

            `temperature` controls how the model picks each next token. At `0` it picks the
            most likely token almost every time, so repeated calls give nearly the same
            reply. That suits data extraction. Around `1` it picks less likely tokens more
            often, so replies vary more. That suits generating ideas.

            ```python
            import json
            body = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Name a colour"}],
                "temperature": 0,
                "max_tokens": 20,
            }
            print(json.dumps(body))
            # {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Name a colour"}], "temperature": 0, "max_tokens": 20}
            ```

            This dict is the **request body**. The provider's Python package converts it to
            JSON text and sends it with an HTTP POST to the **provider**: the company that
            runs the model.

            Parameter names are exact. The API accepts `max_tokens`. It does not accept
            `maxTokens` or `max_token`.
        ''',
        "prompt": r'''
            Build the JSON body of a chat request.

            **Write:** `build_request(model, messages, temperature=0.7, max_tokens=256)`

            - `model`: a `str`, e.g. `"gpt-4o-mini"`
            - `messages`: a `list` of message dicts
            - `temperature`: a `float` (default `0.7`)
            - `max_tokens`: an `int` (default `256`)
            - **Returns:** a `dict` with exactly the keys `"model"`, `"messages"`, `"temperature"`,
              `"max_tokens"`, holding the matching arguments

            **Examples**
            ```python
            msgs = [{"role": "user", "content": "Hi"}]
            build_request("gpt-4o-mini", msgs)
            # returns {"model": "gpt-4o-mini", "messages": msgs, "temperature": 0.7, "max_tokens": 256}
            build_request("claude-haiku", msgs, temperature=0, max_tokens=50)
            # returns {"model": "claude-haiku", "messages": msgs, "temperature": 0, "max_tokens": 50}
            ```
        ''',
        "starter": r'''
            def build_request(model, messages, temperature=0.7, max_tokens=256):
                return {"model": ___, "messages": messages, "temperature": ___, "max_tokens": max_tokens}
        ''',
        "tests": r'''
            from solution import build_request

            MSGS = [{"role": "user", "content": "Hi"}]

            def test_defaults():
                got = build_request("gpt-4o-mini", MSGS)
                assert got == {"model": "gpt-4o-mini", "messages": MSGS, "temperature": 0.7,
                               "max_tokens": 256}, f"got {got!r}"

            def test_custom_values():
                got = build_request("claude-haiku", MSGS, temperature=0, max_tokens=50)
                assert got == {"model": "claude-haiku", "messages": MSGS, "temperature": 0,
                               "max_tokens": 50}, f"got {got!r}"

            def test_exact_keys():
                got = build_request("m", MSGS)
                assert set(got) == {"model", "messages", "temperature", "max_tokens"}, f"keys {sorted(got)}"
        ''',
        "solution": r'''
            def build_request(model, messages, temperature=0.7, max_tokens=256):
                return {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        ''',
        "hints": [
            "Each blank should be one of the function's parameters.",
            "The value for \"model\" is the model argument; the value for \"temperature\" is the temperature argument.",
            "Replace the first `___` with `model` and the second with `temperature` (no quotes: they are variables).",
        ],
    },
    {
        "id": "llm-basics-s4",
        "title": "Fix the OpenAI reply reader",
        "difficulty": 0,
        "lesson": r'''
            ## Reading an OpenAI response

            An OpenAI Chat Completions response is a dict that holds a list that holds more
            dicts. The reply text is several levels down. You read it one key or index at a
            time.

            ```python
            response = {
                "choices": [
                    {"index": 0,
                     "message": {"role": "assistant", "content": "Paris."},
                     "finish_reason": "stop"}
                ],
                "usage": {"prompt_tokens": 14, "completion_tokens": 2, "total_tokens": 16},
            }
            first = response["choices"][0]
            print(first["message"]["role"])
            # assistant
            print(first["message"]["content"])
            # Paris.
            ```

            `response["choices"]` is a **list**, because a request can ask for several
            alternative replies. `[0]` reads the first one. Each item in that list is a
            **choice**: a dict with the keys `"index"`, `"message"` and `"finish_reason"`.

            `first["message"]` is an assistant message. It has the same two keys as the
            messages you send: `"role"` and `"content"`. Reading a value through several keys
            and indexes in a row is called **nested access**.

            A choice has no `"content"` key. The text is one level deeper, inside
            `"message"`. Asking a dict for a key it does not have raises `KeyError`.
        ''',
        "prompt": r'''
            This function should pull the reply text out of an OpenAI-shaped chat response, but
            it crashes with a `KeyError`.

            **Write:** fix `openai_text(response)`

            - `response`: a dict shaped like
              `{"choices": [{"index": 0, "message": {"role": "assistant", "content": "Hi!"}, "finish_reason": "stop"}], "usage": {...}}`
            - **Returns:** a `str`, the `content` of the first choice's message

            **Examples**
            ```python
            openai_text({"choices": [{"index": 0, "message": {"role": "assistant", "content": "Paris."},
                                      "finish_reason": "stop"}]})   # returns "Paris."
            ```
        ''',
        "starter": r'''
            def openai_text(response):
                return response["choices"][0]["content"]
        ''',
        "tests": r'''
            from solution import openai_text

            def make(text):
                return {"choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                     "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7}}

            def test_reads_reply_text():
                got = openai_text(make("Paris."))
                assert got == "Paris.", f"got {got!r}"

            def test_reads_first_choice_only():
                resp = make("first")
                resp["choices"].append({"index": 1, "message": {"role": "assistant", "content": "second"},
                                        "finish_reason": "stop"})
                got = openai_text(resp)
                assert got == "first", f"got {got!r}"
        ''',
        "solution": r'''
            def openai_text(response):
                return response["choices"][0]["message"]["content"]
        ''',
        "hints": [
            "Compare the path in the code with the example shape: one key is missing.",
            "The choice holds a \"message\" dict, and the text is inside that.",
            "After `[0]`, go into `[\"message\"]` before asking for `[\"content\"]`.",
        ],
    },
    {
        "id": "llm-basics-s5",
        "title": "Read an Anthropic reply",
        "difficulty": 0,
        "lesson": r'''
            ## Reading an Anthropic response

            Anthropic's Messages API also returns an assistant reply, but the response has a
            different shape. `response["content"]` is a list of **content blocks**. A content
            block is a dict with a `"type"` key. A plain text block has the form
            `{"type": "text", "text": "..."}`. This lesson reads only the text blocks and
            skips the rest. (Blocks of other types exist for tool use. The Tool
            Calling chapter covers them.)

            ```python
            response = {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello"},
                            {"type": "text", "text": " world"}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": 3},
            }
            parts = []
            for block in response["content"]:
                if block["type"] == "text":
                    parts.append(block["text"])
            print(parts)
            # ['Hello', ' world']
            print("".join(parts))
            # Hello world
            ```

            One reply can hold text blocks and other blocks together. To get the reply text,
            you keep the blocks whose type is `"text"`, then join their `"text"` values in
            order. `"".join(parts)` builds one string from the strings in `parts` and puts
            nothing between them.

            `response["content"]` is a list, not a string. `response["content"][0]` is a
            dict, not text.
        ''',
        "prompt": r'''
            Get the full reply text out of an Anthropic-shaped response.

            **Write:** `anthropic_text(response)`

            - `response`: a dict like
              `{"role": "assistant", "content": [{"type": "text", "text": "Hi"}], "stop_reason": "end_turn", "usage": {...}}`
            - **Returns:** a `str`: the `"text"` of every block whose `"type"` is `"text"`,
              joined together in order with nothing in between

            **Rules**
            - Skip blocks of any other type (e.g. `"tool_use"`, which has no `"text"` key).
            - If there are no text blocks, return `""`.

            **Examples**
            ```python
            anthropic_text({"content": [{"type": "text", "text": "Hello"},
                                        {"type": "text", "text": " world"}]})   # returns "Hello world"
            anthropic_text({"content": [{"type": "tool_use", "id": "t1", "name": "search", "input": {}}]})
            # returns ""
            ```
        ''',
        "starter": r'''
            def anthropic_text(response):
                ...
        ''',
        "tests": r'''
            from solution import anthropic_text

            def test_joins_text_blocks():
                resp = {"role": "assistant", "stop_reason": "end_turn",
                        "content": [{"type": "text", "text": "Hello"}, {"type": "text", "text": " world"}]}
                got = anthropic_text(resp)
                assert got == "Hello world", f"got {got!r}"

            def test_skips_tool_use_blocks():
                resp = {"content": [{"type": "text", "text": "Let me check."},
                                    {"type": "tool_use", "id": "t1", "name": "search", "input": {"q": "x"}},
                                    {"type": "text", "text": " Done."}]}
                got = anthropic_text(resp)
                assert got == "Let me check. Done.", f"got {got!r}"

            def test_no_text_blocks_gives_empty_string():
                got = anthropic_text({"content": [{"type": "tool_use", "id": "t1", "name": "s", "input": {}}]})
                assert got == "", f"got {got!r}"
        ''',
        "solution": r'''
            def anthropic_text(response):
                return "".join(b["text"] for b in response["content"] if b["type"] == "text")
        ''',
        "hints": [
            "Loop over response[\"content\"] and look at each block's \"type\".",
            "Collect the text of the text blocks only, then join them together with an empty separator.",
            "Build a list of `block[\"text\"]` for blocks where `block[\"type\"] == \"text\"`, then return `\"\".join(...)` of it.",
        ],
    },
    {
        "id": "llm-basics-s6",
        "title": "What did that call cost?",
        "difficulty": 0,
        "lesson": r'''
            ## Tokens and cost

            Providers charge per **token**. A token is a small piece of text. In English, one
            token is about 3/4 of a word on average.

            **Input tokens** are the tokens in what you send. **Output tokens** are the tokens
            the model generates. Each kind has its own price, and the output price is usually
            several times higher.

            Prices are quoted **per million tokens**, for example "$3 input / $15 output per
            1M". To get the cost of one side, multiply its token count by its price and divide
            by one million.

            ```python
            input_tokens, output_tokens = 2_000, 400
            in_price, out_price = 3.0, 15.0        # dollars per million tokens (made-up prices)
            input_cost = input_tokens * in_price / 1_000_000
            output_cost = output_tokens * out_price / 1_000_000
            print(input_cost, output_cost)
            # 0.006 0.006
            cost = input_cost + output_cost
            print(cost)
            # 0.012
            print(f"${cost:.4f}")
            # $0.0120
            ```

            Every response has a **usage** section that holds both token counts. You can
            compute the exact cost of a call as soon as you have its response.

            Divide by one million (`1_000_000`), not one thousand. Some older price lists
            were per 1K tokens.
        ''',
        "prompt": r'''
            Compute the price of one API call in dollars.

            **Write:** `request_cost(input_tokens, output_tokens, input_price, output_price)`

            - `input_tokens`, `output_tokens`: `int` token counts from the response usage
            - `input_price`, `output_price`: `float` prices in **dollars per million tokens**
            - **Returns:** a `float`, the total cost in dollars (input cost + output cost)

            **Rules**
            - Don't round the result.
            - Zero tokens cost `0`.

            **Examples**
            ```python
            request_cost(1000, 500, 3.0, 15.0)        # returns 0.0105
            request_cost(1_000_000, 0, 0.15, 0.6)     # returns 0.15
            request_cost(0, 0, 3.0, 15.0)             # returns 0.0
            ```
        ''',
        "starter": r'''
            def request_cost(input_tokens, output_tokens, input_price, output_price):
                ...
        ''',
        "tests": r'''
            from solution import request_cost

            def close(a, b):
                return a is not None and abs(a - b) < 1e-12

            def test_input_and_output_are_both_priced():
                got = request_cost(1000, 500, 3.0, 15.0)
                assert close(got, 0.0105), f"got {got!r}"

            def test_one_million_input_tokens():
                got = request_cost(1_000_000, 0, 0.15, 0.6)
                assert close(got, 0.15), f"got {got!r}"

            def test_output_uses_output_price():
                got = request_cost(0, 2_000_000, 1.0, 4.0)
                assert close(got, 8.0), f"got {got!r}"

            def test_zero_tokens_cost_zero():
                got = request_cost(0, 0, 3.0, 15.0)
                assert close(got, 0.0), f"got {got!r}"
        ''',
        "solution": r'''
            def request_cost(input_tokens, output_tokens, input_price, output_price):
                return input_tokens * input_price / 1_000_000 + output_tokens * output_price / 1_000_000
        ''',
        "hints": [
            "Each side costs tokens times its price-per-million, divided by a million.",
            "Compute the input cost and the output cost separately, then add them.",
            "Return input_tokens * input_price / 1_000_000 plus output_tokens * output_price / 1_000_000.",
        ],
    },
    {
        "id": "llm-basics-s7",
        "title": "Streaming pieces",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Streaming and deltas

            A long reply can take 10 seconds to generate. With **streaming**, the server
            sends each part of the reply as soon as the model generates it. The app shows the
            text while the rest is still being generated.

            Each part is called a **delta**: the new text to add to what you already have. To
            get the full reply, you join the deltas in order.

            ```python
            deltas = ["The ", "sky ", "is ", "blue."]
            shown = ""
            for piece in deltas:
                shown += piece
                print(shown)
            # The
            # The sky
            # The sky is
            # The sky is blue.
            print("".join(deltas) == shown)
            # True
            ```

            Step through the loop and watch `shown` grow by one delta on each pass.

            ```diagram
            {"type": "trace", "title": "Joining deltas one at a time", "code": ["deltas = [\"The \", \"sky \", \"is \", \"blue.\"]", "shown = \"\"", "for piece in deltas:", "    shown += piece", "    print(shown)", "print(\"\".join(deltas) == shown)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']"}, "out": ""},
              {"line": 3, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "''"}, "out": ""},
              {"line": 4, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "''", "piece": "'The '"}, "out": ""},
              {"line": 5, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The '", "piece": "'The '"}, "out": ""},
              {"line": 3, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The '", "piece": "'The '"}, "out": "The \n"},
              {"line": 4, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The '", "piece": "'sky '"}, "out": "The \n"},
              {"line": 5, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky '", "piece": "'sky '"}, "out": "The \n"},
              {"line": 3, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky '", "piece": "'sky '"}, "out": "The \nThe sky \n"},
              {"line": 4, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky '", "piece": "'is '"}, "out": "The \nThe sky \n"},
              {"line": 5, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is '", "piece": "'is '"}, "out": "The \nThe sky \n"},
              {"line": 3, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is '", "piece": "'is '"}, "out": "The \nThe sky \nThe sky is \n"},
              {"line": 4, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is '", "piece": "'blue.'"}, "out": "The \nThe sky \nThe sky is \n"},
              {"line": 5, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is blue.'", "piece": "'blue.'"}, "out": "The \nThe sky \nThe sky is \n"},
              {"line": 3, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is blue.'", "piece": "'blue.'"}, "out": "The \nThe sky \nThe sky is \nThe sky is blue.\n"},
              {"line": 6, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is blue.'", "piece": "'blue.'"}, "out": "The \nThe sky \nThe sky is \nThe sky is blue.\n"},
              {"line": null, "vars": {"deltas": "['The ', 'sky ', 'is ', 'blue.']", "shown": "'The sky is blue.'", "piece": "'blue.'"}, "out": "The \nThe sky \nThe sky is \nThe sky is blue.\nTrue\n"}
            ]}
            ```

            `"".join(deltas)` builds one string from the strings in the list and puts nothing
            between them. It is the usual way to rebuild the reply.

            Each item the server sends in a stream is called an **event**. Some events hold
            no text. The first one may hold only the role, and the last one only the stop
            reason. Their delta can be missing or `None`. `"".join`
            raises `TypeError` when an item is `None`, so replace `None` with `""` first.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            deltas = ["Hel", "lo", "", " there", "!"]
            text = "".join(deltas)
            print(text)
            print(len(deltas))
            events = [{"delta": "Hi"}, {"delta": None}, {"delta": "!"}]
            print("".join(e["delta"] or "" for e in events))
        ''',
        "solution": r'''
            Hello there!
            5
            Hi!
        ''',
        "explanation": r'''
            Joining the five pieces (one of them empty) gives `Hello there!`. `len(deltas)` counts
            pieces, not characters: 5. In the events, `None or ""` becomes `""`, so the join gives
            `Hi!`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "\"\".join joins strings together with nothing between them.",
            "An empty string adds nothing. len of a list counts its items. `None or \"\"` is \"\".",
            "Line 1: the joined text. Line 2: how many items are in the deltas list. Line 3: the joined text of the events, where None became an empty string.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "llm-basics-8",
        "title": "Ask through an injected client",
        "difficulty": 1,
        "lesson": r'''
            ## Passing the client as an argument

            A **client** is the function or object that sends the request to the provider. A
            function that creates its own client can only ever call the real API. A function
            that receives the client as an argument works with any client you pass.

            In the real app you pass the real client. In a test you pass a **fake client**: a
            function that returns a fixed response dict. A fake uses no network, costs
            nothing and returns the same answer on every run.

            ```python
            def fake_client(model, messages, **kwargs):
                last = messages[-1]["content"]
                return {"choices": [{"index": 0, "finish_reason": "stop",
                                     "message": {"role": "assistant", "content": "You said: " + last}}]}

            def ask(client, question):
                response = client(model="demo", messages=[{"role": "user", "content": question}])
                return response["choices"][0]["message"]["content"]

            print(ask(fake_client, "ping"))
            # You said: ping
            ```

            `**kwargs` in a parameter list collects any extra keyword arguments into a dict. The fake
            accepts them and ignores them.

            `ask` calls whatever function `client` refers to. Here that is `fake_client`,
            which builds its reply from the last message it received.

            Passing a function the objects it depends on is called **dependency injection**.
            An **SDK** (software development kit) is the Python package a provider publishes
            for calling its API. The real OpenAI SDK call has almost the same form:
            `client.chat.completions.create(model=..., messages=...)`. It takes keyword
            arguments and returns a response.

            Call the client with **keyword arguments** (`model=...`), exactly as the task
            states. Real SDKs require them.
        ''',
        "prompt": r'''
            A helper that asks one question with a system prompt, using whatever client it is given.

            **Write:** `ask(client, question, system="You are a helpful assistant.", model="gpt-4o-mini")`

            - `client`: a function you call as `client(model=..., messages=...)`; it returns an
              OpenAI-shaped response dict (`{"choices": [{"message": {"role": "assistant", "content": ...}, ...}]}`)
            - `question`: a `str`
            - `system`: a `str`, the system prompt
            - `model`: a `str`
            - **Returns:** a `str`, the reply text (first choice's message content)

            **Rules**
            - Call `client` exactly once, with keyword arguments `model` and `messages` only.
            - `messages` must be exactly two messages: the system message, then the user message.

            **Examples**
            ```python
            ask(fake, "Capital of France?")
            # calls fake(model="gpt-4o-mini", messages=[
            #     {"role": "system", "content": "You are a helpful assistant."},
            #     {"role": "user", "content": "Capital of France?"}])
            # and returns the reply text, e.g. "Paris."
            ```
        ''',
        "starter": r'''
            def ask(client, question, system="You are a helpful assistant.", model="gpt-4o-mini"):
                ...
        ''',
        "tests": r'''
            from solution import ask

            def make_fake(reply):
                calls = []
                def fake(**kwargs):
                    calls.append(kwargs)
                    return {"choices": [{"index": 0, "finish_reason": "stop",
                                         "message": {"role": "assistant", "content": reply}}]}
                return fake, calls

            def test_returns_reply_text():
                fake, calls = make_fake("Paris.")
                got = ask(fake, "Capital of France?")
                assert got == "Paris.", f"got {got!r}"

            def test_sends_system_then_user_with_default_model():
                fake, calls = make_fake("ok")
                ask(fake, "Capital of France?")
                assert len(calls) == 1, f"client called {len(calls)} times"
                assert calls[0] == {"model": "gpt-4o-mini", "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Capital of France?"}]}, f"client got {calls[0]!r}"

            def test_custom_system_and_model():
                fake, calls = make_fake("ok")
                ask(fake, "Hi", system="Reply in French.", model="claude-haiku")
                assert calls[0]["model"] == "claude-haiku", f"model {calls[0].get('model')!r}"
                assert calls[0]["messages"][0] == {"role": "system", "content": "Reply in French."}
        ''',
        "solution": r'''
            def ask(client, question, system="You are a helpful assistant.", model="gpt-4o-mini"):
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": question},
                ]
                response = client(model=model, messages=messages)
                return response["choices"][0]["message"]["content"]
        ''',
        "hints": [
            "Build the two-message list, call the client with keywords, then read the reply like in the OpenAI step.",
            "messages = system message dict, then user message dict. Call client(model=model, messages=messages).",
            "Make the list of two dicts; call `client(model=model, messages=messages)`; return `response[\"choices\"][0][\"message\"][\"content\"]`.",
        ],
    },
    {
        "id": "llm-basics-9",
        "title": "Split out the system prompt",
        "difficulty": 1,
        "lesson": r'''
            ## The Anthropic system field

            The **system prompt** is the text of the system message: the instructions for the
            model. OpenAI takes it as a message with the role `"system"` inside the messages
            list. Anthropic's Messages API takes it in a separate top-level `"system"` field
            of the request body. Its `"messages"` list holds only `user` and `assistant`
            messages.

            ```python
            openai_style = [
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "Hi"},
            ]
            system = openai_style[0]["content"]
            rest = openai_style[1:]
            body = {"model": "claude-haiku", "system": system, "messages": rest, "max_tokens": 100}
            print(body["system"])
            # Be brief.
            print(body["messages"])
            # [{'role': 'user', 'content': 'Hi'}]
            ```

            The slice `openai_style[1:]` creates a new list. `openai_style` still has both
            messages afterwards.

            Code that supports several providers needs an **adapter**: a small function that
            converts one request shape into another.

            Build a new list for the non-system messages. Do not delete items from the
            caller's list while you loop over it, because the loop then skips items.
        ''',
        "prompt": r'''
            Convert an OpenAI-style message list for Anthropic, which wants the system prompt separately.

            **Write:** `split_system(messages)`

            - `messages`: a `list` of message dicts (roles `"system"`, `"user"`, `"assistant"`)
            - **Returns:** a tuple `(system_text, other_messages)`:
              - `system_text`: a `str`, the `content` of all system messages joined with `"\n\n"`
                (two newlines), in order; `""` if there are none
              - `other_messages`: a new `list` of all non-system messages, in their original order

            **Rules**
            - Don't modify the list you were given.

            **Examples**
            ```python
            split_system([{"role": "system", "content": "Be brief."},
                          {"role": "user", "content": "Hi"}])
            # returns ("Be brief.", [{"role": "user", "content": "Hi"}])
            split_system([{"role": "user", "content": "Hi"}])
            # returns ("", [{"role": "user", "content": "Hi"}])
            ```
        ''',
        "starter": r'''
            def split_system(messages):
                ...
        ''',
        "tests": r'''
            from solution import split_system

            def test_one_system_message():
                got = split_system([{"role": "system", "content": "Be brief."}, {"role": "user", "content": "Hi"}])
                assert got == ("Be brief.", [{"role": "user", "content": "Hi"}]), f"got {got!r}"

            def test_no_system_message():
                got = split_system([{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Yo"}])
                assert got == ("", [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Yo"}]), f"got {got!r}"

            def test_several_system_messages_joined_with_blank_line():
                msgs = [{"role": "system", "content": "A"}, {"role": "user", "content": "q"},
                        {"role": "system", "content": "B"}]
                got = split_system(msgs)
                assert got == ("A\n\nB", [{"role": "user", "content": "q"}]), f"got {got!r}"

            def test_input_not_modified():
                msgs = [{"role": "system", "content": "A"}, {"role": "user", "content": "q"}]
                split_system(msgs)
                assert len(msgs) == 2 and msgs[0]["role"] == "system", f"input changed to {msgs!r}"
        ''',
        "solution": r'''
            def split_system(messages):
                system_parts = [m["content"] for m in messages if m["role"] == "system"]
                others = [m for m in messages if m["role"] != "system"]
                return "\n\n".join(system_parts), others
        ''',
        "hints": [
            "Two passes over the list: one collecting system contents, one collecting the rest.",
            "Join the system contents with \"\\n\\n\" (joining an empty list gives \"\"), and return a tuple of the two results.",
            "system_parts = contents of messages whose role is \"system\"; others = messages whose role is not \"system\"; return (\"\\n\\n\".join(system_parts), others).",
        ],
    },
    {
        "id": "llm-basics-10",
        "title": "Was the reply cut off?",
        "difficulty": 1,
        "lesson": r'''
            ## Stop reasons

            The model generates tokens until a stop condition is met. One condition is that
            the model predicts its end-of-reply token, so the reply is complete. Another is
            that the reply reaches `max_tokens`, so the reply ends early. Every response
            holds a **stop reason**: a string that says which condition ended generation.

            ```python
            openai_reply = {"choices": [{"message": {"role": "assistant", "content": "The three steps are: 1."},
                                         "finish_reason": "length"}]}
            anthropic_reply = {"content": [{"type": "text", "text": "Done."}], "stop_reason": "end_turn"}
            print(openai_reply["choices"][0]["finish_reason"])
            # length
            print(anthropic_reply["stop_reason"])
            # end_turn
            ```

            OpenAI calls the field `finish_reason`. The values that matter here are `"stop"`
            (the reply is complete) and `"length"` (the reply reached `max_tokens`).
            Anthropic calls the field `stop_reason`. The values that matter here are
            `"end_turn"` (complete), `"max_tokens"` (limit reached) and `"stop_sequence"`
            (the model generated a string that your request listed as a
            place to stop). (Both providers have extra values for tool use. The Tool
            Calling chapter covers them.)

            A reply that reached the token limit is **truncated**: the text ends before the
            model finished. It can be half a JSON object, or a list that ends at item 3. Real
            apps detect this and retry with a larger `max_tokens`, or show a warning.

            The two providers put the stop reason in different places. Check which shape you
            have first, for example with `"choices" in response`.
        ''',
        "prompt": r'''
            Detect whether a reply was cut off by the token limit, for either provider.

            **Write:** `was_cut_off(response)`

            - `response`: either an OpenAI-shaped dict (has a `"choices"` list; the first choice has
              `"finish_reason"`) or an Anthropic-shaped dict (has a top-level `"stop_reason"`)
            - **Returns:** `True` if the reply stopped because it hit the token limit, else `False`

            **Rules**
            - OpenAI: cut off when the first choice's `finish_reason` is `"length"`.
            - Anthropic: cut off when `stop_reason` is `"max_tokens"`.
            - Every other stop reason (`"stop"`, `"end_turn"`, `"tool_calls"`, `"tool_use"`, ...) gives `False`.
            - Return real `True`/`False`.

            **Examples**
            ```python
            was_cut_off({"choices": [{"message": {...}, "finish_reason": "length"}]})   # returns True
            was_cut_off({"choices": [{"message": {...}, "finish_reason": "stop"}]})     # returns False
            was_cut_off({"content": [...], "stop_reason": "max_tokens"})               # returns True
            was_cut_off({"content": [...], "stop_reason": "end_turn"})                 # returns False
            ```
        ''',
        "research": {
            "note": "Look up the list of possible stop reasons in both API references "
                    "(`finish_reason` for OpenAI, `stop_reason` for Anthropic), then come back.",
            "links": [
                {"title": "Chat Completions: create - OpenAI API reference",
                 "url": "https://platform.openai.com/docs/api-reference/chat/create"},
                {"title": "Messages - Anthropic API reference",
                 "url": "https://docs.anthropic.com/en/api/messages"},
            ],
        },
        "starter": r'''
            def was_cut_off(response):
                ...
        ''',
        "tests": r'''
            from solution import was_cut_off

            def oa(reason):
                return {"choices": [{"index": 0, "message": {"role": "assistant", "content": "x"},
                                     "finish_reason": reason}]}

            def an(reason):
                return {"role": "assistant", "content": [{"type": "text", "text": "x"}], "stop_reason": reason}

            def test_openai_length_is_cut_off():
                assert was_cut_off(oa("length")) is True

            def test_openai_other_reasons_are_not():
                for reason in ("stop", "tool_calls", "content_filter"):
                    assert was_cut_off(oa(reason)) is False, f"{reason!r} is not a cut-off"

            def test_anthropic_max_tokens_is_cut_off():
                assert was_cut_off(an("max_tokens")) is True

            def test_anthropic_other_reasons_are_not():
                for reason in ("end_turn", "tool_use", "stop_sequence"):
                    assert was_cut_off(an(reason)) is False, f"{reason!r} is not a cut-off"
        ''',
        "solution": r'''
            def was_cut_off(response):
                if "choices" in response:
                    return response["choices"][0]["finish_reason"] == "length"
                return response.get("stop_reason") == "max_tokens"
        ''',
        "hints": [
            "First decide which provider's shape you have, then look at that shape's stop field.",
            "If the dict has a \"choices\" key it is OpenAI: compare the first choice's finish_reason. Otherwise compare stop_reason.",
            "`if \"choices\" in response:` return whether choices[0][\"finish_reason\"] == \"length\"; else return whether response[\"stop_reason\"] == \"max_tokens\". A comparison is already True/False.",
        ],
    },
    {
        "id": "llm-basics-11",
        "title": "Normalise token usage",
        "difficulty": 1,
        "lesson": r'''
            ## Token usage

            Every response has a `"usage"` dict. It holds the number of tokens you sent and
            the number of tokens the model generated. The two providers use different key
            names for the same two counts.

            OpenAI names them `prompt_tokens` and `completion_tokens`. The **prompt** is the
            text you send and the **completion** is the text the model generates. Anthropic
            names them `input_tokens` and `output_tokens`.

            ```python
            openai_usage = {"prompt_tokens": 120, "completion_tokens": 30, "total_tokens": 150}
            anthropic_usage = {"input_tokens": 120, "output_tokens": 30}
            for usage in (openai_usage, anthropic_usage):
                inp = usage.get("prompt_tokens", usage.get("input_tokens", 0))
                out = usage.get("completion_tokens", usage.get("output_tokens", 0))
                print(inp, out, inp + out)
            # 120 30 150
            # 120 30 150
            ```

            `usage.get("prompt_tokens", default)` returns the value for `"prompt_tokens"` if
            the key exists. Otherwise it returns the default. Here the default is a second
            `.get` call that reads the Anthropic key, and that call falls back to `0`.

            Try `get` with `input_tokens` on the OpenAI dict to see why the fallback is needed.

            ```diagram
            {"type":"dict","title":"Keys of an OpenAI usage dict","name":"openai_usage","entries":[["prompt_tokens",120],["completion_tokens",30],["total_tokens",150]]}
            ```

            Converting each provider's shape into one shape of your own is called
            **normalising** the data. Cost tracking code then handles one format only.

            A response may have no `"usage"` key, or `"usage": None`. Some fakes and some
            stream chunks are built that way. `response.get("usage") or {}` gives you an
            empty dict in both cases, so the later `.get` calls still work.
        ''',
        "prompt": r'''
            Turn either provider's usage block into one shape for your cost tracker.

            **Write:** `usage_of(response)`

            - `response`: an OpenAI-shaped dict (`"usage": {"prompt_tokens", "completion_tokens", ...}`)
              or an Anthropic-shaped dict (`"usage": {"input_tokens", "output_tokens"}`)
            - **Returns:** a `dict` `{"input": int, "output": int, "total": int}`

            **Rules**
            - OpenAI: `input` = `prompt_tokens`, `output` = `completion_tokens`.
            - Anthropic: `input` = `input_tokens`, `output` = `output_tokens`.
            - `total` = `input` + `output` (compute it; don't rely on a `total_tokens` field).
            - If `"usage"` is missing or `None`, return all zeros.

            **Examples**
            ```python
            usage_of({"choices": [...], "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15}})
            # returns {"input": 12, "output": 3, "total": 15}
            usage_of({"content": [...], "usage": {"input_tokens": 40, "output_tokens": 9}})
            # returns {"input": 40, "output": 9, "total": 49}
            usage_of({"choices": []})   # returns {"input": 0, "output": 0, "total": 0}
            ```
        ''',
        "starter": r'''
            def usage_of(response):
                ...
        ''',
        "tests": r'''
            from solution import usage_of

            def test_openai_usage():
                got = usage_of({"choices": [], "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15}})
                assert got == {"input": 12, "output": 3, "total": 15}, f"got {got!r}"

            def test_anthropic_usage():
                got = usage_of({"content": [], "usage": {"input_tokens": 40, "output_tokens": 9}})
                assert got == {"input": 40, "output": 9, "total": 49}, f"got {got!r}"

            def test_total_is_computed_not_copied():
                got = usage_of({"choices": [], "usage": {"prompt_tokens": 1, "completion_tokens": 2}})
                assert got == {"input": 1, "output": 2, "total": 3}, f"got {got!r}"

            def test_missing_or_none_usage_gives_zeros():
                for resp in ({"choices": []}, {"content": [], "usage": None}):
                    got = usage_of(resp)
                    assert got == {"input": 0, "output": 0, "total": 0}, f"{resp!r} gave {got!r}"
        ''',
        "solution": r'''
            def usage_of(response):
                usage = response.get("usage") or {}
                inp = usage.get("prompt_tokens", usage.get("input_tokens", 0))
                out = usage.get("completion_tokens", usage.get("output_tokens", 0))
                return {"input": inp, "output": out, "total": inp + out}
        ''',
        "hints": [
            "Get the usage dict safely first (it may be missing or None), then read whichever labels it uses.",
            "`.get()` with a default lets you try the OpenAI name and fall back to the Anthropic name, and then to 0.",
            "usage = response.get(\"usage\") or {}; input = the prompt_tokens value, else input_tokens, else 0; output likewise with completion_tokens/output_tokens; return the three-key dict with total = input + output.",
        ],
    },
    {
        "id": "llm-basics-12",
        "title": "Collect a stream",
        "difficulty": 1,
        "lesson": r'''
            ## OpenAI stream chunks

            A real OpenAI stream sends a sequence of **chunks**. A chunk is a dict with almost
            the same shape as a normal response. The difference is that each choice has a
            `"delta"` dict, which holds only the new text, instead of a full `"message"`.

            Not every chunk holds text. The first chunk often holds only the role. The last
            one holds only the `finish_reason`. When usage reporting is on, a final chunk has
            an **empty `choices` list**.

            ```python
            def fake_stream():
                yield {"choices": [{"delta": {"role": "assistant"}}]}
                yield {"choices": [{"delta": {"content": "Hel"}}]}
                yield {"choices": [{"delta": {"content": "lo"}, "finish_reason": None}]}
                yield {"choices": [{"delta": {}, "finish_reason": "stop"}]}
                yield {"choices": [], "usage": {"prompt_tokens": 5, "completion_tokens": 2}}

            for chunk in fake_stream():
                if chunk["choices"]:
                    print(repr(chunk["choices"][0]["delta"].get("content")))
            # None
            # 'Hel'
            # 'lo'
            # None
            ```

            The loop prints four lines for five chunks. The `if` skips the last chunk because
            an empty list counts as false. `.get("content")` returns `None` for the two
            deltas that have no `"content"` key.

            The stream is an **iterable**, often a generator such as `fake_stream()`. A
            generator produces each item once, so you can loop over the stream only one time.

            `delta.get("content")` can be `None`. `chunk["choices"][0]` raises `IndexError`
            on the chunk whose `choices` list is empty.
        ''',
        "prompt": r'''
            Rebuild the full reply text from an OpenAI-style stream of chunks.

            **Write:** `collect_stream(chunks)`

            - `chunks`: an iterable (e.g. a generator) of dicts like
              `{"choices": [{"delta": {"content": "Hel"}, "finish_reason": None}]}`
            - **Returns:** a `str`, all the `delta` `"content"` pieces of the first choice joined in order

            **Rules**
            - A delta may have no `"content"` key, or `"content": None` - treat both as nothing.
            - A chunk may have an empty `"choices"` list - skip it.
            - `chunks` may be a generator, so go through it only once.
            - No text at all gives `""`.

            **Examples**
            ```python
            collect_stream([
                {"choices": [{"delta": {"role": "assistant"}}]},
                {"choices": [{"delta": {"content": "Hel"}}]},
                {"choices": [{"delta": {"content": "lo"}}]},
                {"choices": [{"delta": {}, "finish_reason": "stop"}]},
                {"choices": [], "usage": {"prompt_tokens": 5, "completion_tokens": 2}},
            ])   # returns "Hello"
            ```
        ''',
        "starter": r'''
            def collect_stream(chunks):
                ...
        ''',
        "tests": r'''
            from solution import collect_stream

            def chunk(content=None, **delta_extra):
                delta = dict(delta_extra)
                if content is not None:
                    delta["content"] = content
                return {"choices": [{"index": 0, "delta": delta, "finish_reason": None}]}

            def test_joins_pieces_in_order():
                got = collect_stream([chunk("Hel"), chunk("lo"), chunk(" there")])
                assert got == "Hello there", f"got {got!r}"

            def test_skips_role_only_and_none_content():
                stream = [chunk(role="assistant"), {"choices": [{"delta": {"content": None}}]},
                          chunk("Hi"), {"choices": [{"delta": {}, "finish_reason": "stop"}]}]
                got = collect_stream(stream)
                assert got == "Hi", f"got {got!r}"

            def test_skips_chunks_with_no_choices():
                stream = [chunk("A"), {"choices": [], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}]
                got = collect_stream(stream)
                assert got == "A", f"got {got!r}"

            def test_works_with_a_generator():
                def gen():
                    yield chunk("x")
                    yield chunk("y")
                got = collect_stream(gen())
                assert got == "xy", f"got {got!r}"

            def test_empty_stream():
                got = collect_stream([])
                assert got == "", f"got {got!r}"
        ''',
        "solution": r'''
            def collect_stream(chunks):
                parts = []
                for chunk in chunks:
                    if not chunk.get("choices"):
                        continue
                    piece = chunk["choices"][0].get("delta", {}).get("content")
                    if piece:
                        parts.append(piece)
                return "".join(parts)
        ''',
        "hints": [
            "Loop over the chunks once, collecting text pieces into a list.",
            "Skip chunks whose choices list is empty; read the delta with `.get(\"content\")` so a missing key gives None; only keep real strings.",
            "parts = []; for each chunk: continue if no choices; piece = choices[0][\"delta\"].get(\"content\"); if piece: append it; finally return \"\".join(parts).",
        ],
    },
    {
        "id": "llm-basics-13",
        "title": "Survive a rate limit",
        "difficulty": 1,
        "lesson": r'''
            ## Rate limits and status 429

            A provider allows each account a fixed number of requests and tokens per minute.
            When you send more than that, the API responds with **HTTP 429 Too Many
            Requests**. You are **rate limited**. The condition is temporary: the same
            request can succeed a little later.

            Other errors are not temporary. `401` means the API key is wrong and `400` means
            the request body is invalid. The same request fails again until you change your code.

            SDKs raise exceptions that store the status code as an attribute.

            ```python
            class APIError(Exception):
                def __init__(self, status_code, message):
                    super().__init__(message)
                    self.status_code = status_code

            try:
                raise APIError(429, "Rate limit reached")
            except Exception as err:
                code = getattr(err, "status_code", None)
                print("status:", code, "-", err)
            # status: 429 - Rate limit reached
            ```

            `getattr(obj, "name", default)` reads the attribute called `name` from `obj`. If
            the object has no such attribute, it returns the default instead of raising
            `AttributeError`. That matters here because many exceptions, such as `KeyError`,
            have no `status_code`.

            Handle only the errors you have a response for. For every other error, write a
            bare `raise` inside the `except` block. It raises the same exception object again.
        ''',
        "prompt": r'''
            Show a friendly message when the model is rate limited, and let every other error through.

            **Write:** `safe_ask(client, messages)`

            - `client`: a function called as `client(messages=messages)`; returns an OpenAI-shaped
              response dict, or raises an exception
            - `messages`: a `list` of message dicts
            - **Returns:** a `str`: the reply text on success, or exactly
              `"The model is busy, please try again."` when rate limited

            **Rules**
            - Rate limited means: the exception has a `status_code` attribute equal to `429`.
            - Any other exception (other status codes, or no `status_code` at all) must be
              re-raised unchanged (same exception object).
            - Call `client` only once (no retries here).

            **Examples**
            ```python
            safe_ask(ok_client, msgs)        # returns "Hi!"
            safe_ask(limited_client, msgs)   # client raised an error with status_code 429
                                             # returns "The model is busy, please try again."
            safe_ask(bad_key_client, msgs)   # client raised an error with status_code 401 -> it propagates
            ```
        ''',
        "starter": r'''
            def safe_ask(client, messages):
                ...
        ''',
        "tests": r'''
            from solution import safe_ask

            class APIError(Exception):
                def __init__(self, status_code, message="error"):
                    super().__init__(message)
                    self.status_code = status_code

            MSGS = [{"role": "user", "content": "Hi"}]

            def raiser(err, calls):
                def client(**kwargs):
                    calls.append(kwargs)
                    raise err
                return client

            def test_returns_reply_on_success():
                def client(**kwargs):
                    assert kwargs == {"messages": MSGS}, f"client got {kwargs!r}"
                    return {"choices": [{"index": 0, "message": {"role": "assistant", "content": "Hi!"},
                                         "finish_reason": "stop"}]}
                got = safe_ask(client, MSGS)
                assert got == "Hi!", f"got {got!r}"

            def test_429_returns_friendly_message_after_one_call():
                calls = []
                got = safe_ask(raiser(APIError(429), calls), MSGS)
                assert got == "The model is busy, please try again.", f"got {got!r}"
                assert len(calls) == 1, f"client called {len(calls)} times"

            def test_other_status_codes_propagate():
                err = APIError(401, "bad key")
                try:
                    safe_ask(raiser(err, []), MSGS)
                except APIError as caught:
                    assert caught is err, "re-raise the same exception"
                    return
                assert False, "a 401 error should propagate"

            def test_errors_without_status_code_propagate():
                try:
                    safe_ask(raiser(KeyError("choices"), []), MSGS)
                except KeyError:
                    return
                assert False, "a KeyError should propagate"
        ''',
        "solution": r'''
            def safe_ask(client, messages):
                try:
                    response = client(messages=messages)
                except Exception as err:
                    if getattr(err, "status_code", None) == 429:
                        return "The model is busy, please try again."
                    raise
                return response["choices"][0]["message"]["content"]
        ''',
        "hints": [
            "Wrap the client call in try/except and inspect the exception's status_code attribute.",
            "In the except block, return the friendly text only when the status code is 429; otherwise re-raise. Read the reply outside the try.",
            "try: response = client(messages=messages); except Exception as err: if getattr(err, \"status_code\", None) == 429 return the message, else `raise`; then return the first choice's message content.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "llm-basics-14",
        "title": "One chat turn",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Run one turn of a multi-turn chat: add the user's message, call the model with the
            whole history, and record its reply.

            **Write:** `run_turn(client, messages, user_text, model="gpt-4o-mini")`

            - `client`: a function called as `client(model=..., messages=...)`; returns an
              OpenAI-shaped response dict
            - `messages`: the conversation so far, a `list` of message dicts (may be empty)
            - `user_text`: a `str`, the new user message
            - `model`: a `str`
            - **Returns:** a tuple `(reply_text, new_messages)`:
              - `reply_text`: the reply text (`str`)
              - `new_messages`: a **new** list = the old messages, then
                `{"role": "user", "content": user_text}`, then
                `{"role": "assistant", "content": reply_text}`

            **Rules**
            - The client must receive the full history **including** the new user message
              (but not the reply, which doesn't exist yet).
            - Don't modify the `messages` list you were given.
            - If the reply's `finish_reason` is `"length"`, add `" [truncated]"` to the end of
              `reply_text` (and to the stored assistant content).

            **Examples**
            ```python
            reply, history = run_turn(fake, [{"role": "system", "content": "Be brief."}], "Hi")
            # fake was called with messages=[{"role": "system", ...}, {"role": "user", "content": "Hi"}]
            # reply == "Hello!"
            # history == [{"role": "system", "content": "Be brief."},
            #             {"role": "user", "content": "Hi"},
            #             {"role": "assistant", "content": "Hello!"}]
            ```
        ''',
        "starter": r'''
            def run_turn(client, messages, user_text, model="gpt-4o-mini"):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import run_turn

            def make_fake(reply, finish="stop"):
                calls = []
                def fake(**kwargs):
                    calls.append(copy.deepcopy(kwargs))
                    return {"choices": [{"index": 0, "finish_reason": finish,
                                         "message": {"role": "assistant", "content": reply}}]}
                return fake, calls

            SYSTEM = {"role": "system", "content": "Be brief."}

            def test_returns_reply_and_new_history():
                fake, calls = make_fake("Hello!")
                reply, history = run_turn(fake, [SYSTEM], "Hi")
                assert reply == "Hello!", f"reply {reply!r}"
                assert history == [SYSTEM, {"role": "user", "content": "Hi"},
                                   {"role": "assistant", "content": "Hello!"}], f"history {history!r}"

            def test_client_gets_history_with_new_user_message():
                fake, calls = make_fake("ok")
                run_turn(fake, [SYSTEM], "Hi", model="claude-haiku")
                assert calls == [{"model": "claude-haiku",
                                  "messages": [SYSTEM, {"role": "user", "content": "Hi"}]}], f"client got {calls!r}"

            def test_input_list_not_modified():
                fake, _ = make_fake("ok")
                original = [SYSTEM]
                run_turn(fake, original, "Hi")
                assert original == [SYSTEM], f"input became {original!r}"

            def test_works_from_empty_history_and_chains():
                fake, calls = make_fake("one")
                _, history = run_turn(fake, [], "first")
                fake2, calls2 = make_fake("two")
                _, history = run_turn(fake2, history, "second")
                assert [m["content"] for m in history] == ["first", "one", "second", "two"], f"got {history!r}"
                assert len(calls2[0]["messages"]) == 3

            def test_truncated_reply_is_marked():
                fake, _ = make_fake("The steps are", finish="length")
                reply, history = run_turn(fake, [], "List steps")
                assert reply == "The steps are [truncated]", f"reply {reply!r}"
                assert history[-1] == {"role": "assistant", "content": "The steps are [truncated]"}
        ''',
        "solution": r'''
            def run_turn(client, messages, user_text, model="gpt-4o-mini"):
                history = messages + [{"role": "user", "content": user_text}]
                response = client(model=model, messages=history)
                choice = response["choices"][0]
                reply = choice["message"]["content"]
                if choice.get("finish_reason") == "length":
                    reply += " [truncated]"
                return reply, history + [{"role": "assistant", "content": reply}]
        ''',
        "hints": [
            "Build a new list with `+` (which copies) instead of calling append on the caller's list.",
            "history = old messages + the user message; call the client with it; read the reply and finish_reason; then return the reply and history + the assistant message.",
            "history = messages + [user dict]; response = client(model=model, messages=history); take choices[0]; add \" [truncated]\" if finish_reason == \"length\"; return (reply, history + [assistant dict]).",
        ],
    },
    {
        "id": "llm-basics-15",
        "title": "Retry with exponential backoff",
        "difficulty": 2,
        "prompt": r'''
            Retry calls that fail for temporary reasons, waiting longer each time
            (*exponential backoff*).

            **Write:** `call_with_retry(client, request, max_attempts=3, sleep=time.sleep)`

            - `client`: a function called as `client(request)`; returns a response dict or raises
            - `request`: a `dict` (pass it through unchanged)
            - `max_attempts`: an `int` >= 1, the total number of calls allowed
            - `sleep`: a function called as `sleep(seconds)` to wait (tests pass a fake that records the waits)
            - **Returns:** the first successful response dict

            **Rules**
            - Retry only when the exception has a `status_code` attribute that is `429` or `500`-`599`.
            - Any other exception is re-raised immediately (no waiting, no retry).
            - Before retry number 1, 2, 3... wait `1`, `2`, `4`... seconds (doubling), by calling `sleep`.
            - Never sleep after the last attempt: if the last allowed attempt fails, re-raise that error.
            - Never call `time.sleep` directly - use the `sleep` argument.

            **Examples**
            ```python
            # client fails with 429, 503, then succeeds:
            call_with_retry(client, req, sleep=waits.append)   # returns the response; waits == [1, 2]
            # client always fails with 429, max_attempts=3:
            # calls client 3 times, waits == [1, 2], then raises the last error
            # client fails with 400: raises it at once; waits == []
            ```
        ''',
        "research": {
            "note": "Read how the providers describe rate limits and which errors are worth retrying, then come back.",
            "links": [
                {"title": "Errors - Anthropic API docs", "url": "https://docs.anthropic.com/en/api/errors"},
                {"title": "Rate limits - OpenAI docs", "url": "https://platform.openai.com/docs/guides/rate-limits"},
            ],
        },
        "starter": r'''
            import time


            def call_with_retry(client, request, max_attempts=3, sleep=time.sleep):
                ...
        ''',
        "tests": r'''
            from solution import call_with_retry

            class APIError(Exception):
                def __init__(self, status_code):
                    super().__init__(f"HTTP {status_code}")
                    self.status_code = status_code

            OK = {"choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}]}
            REQ = {"model": "m", "messages": []}

            def scripted(outcomes):
                calls = []
                def client(request):
                    calls.append(request)
                    item = outcomes[len(calls) - 1]
                    if isinstance(item, Exception):
                        raise item
                    return item
                return client, calls

            def test_success_first_try_no_sleep():
                client, calls = scripted([OK])
                waits = []
                got = call_with_retry(client, REQ, sleep=waits.append)
                assert got == OK and waits == [] and calls == [REQ], f"waits {waits}, calls {len(calls)}"

            def test_retries_429_and_5xx_with_doubling_waits():
                client, calls = scripted([APIError(429), APIError(503), OK])
                waits = []
                got = call_with_retry(client, REQ, sleep=waits.append)
                assert got == OK, f"got {got!r}"
                assert waits == [1, 2], f"waits {waits}"
                assert len(calls) == 3

            def test_gives_up_after_max_attempts_and_raises_last_error():
                errors = [APIError(429), APIError(500), APIError(502), APIError(429)]
                client, calls = scripted(errors)
                waits = []
                try:
                    call_with_retry(client, REQ, max_attempts=3, sleep=waits.append)
                except APIError as err:
                    assert err is errors[2], f"raised {err!r}, expected the third error"
                else:
                    assert False, "expected the last error to be raised"
                assert len(calls) == 3, f"client called {len(calls)} times"
                assert waits == [1, 2], f"waits {waits}"

            def test_non_retryable_error_raises_immediately():
                client, calls = scripted([APIError(400), OK])
                waits = []
                try:
                    call_with_retry(client, REQ, sleep=waits.append)
                except APIError as err:
                    assert err.status_code == 400
                else:
                    assert False, "400 must not be retried"
                assert len(calls) == 1 and waits == [], f"calls {len(calls)}, waits {waits}"

            def test_errors_without_status_code_are_not_retried():
                client, calls = scripted([ValueError("bad"), OK])
                try:
                    call_with_retry(client, REQ, sleep=lambda s: None)
                except ValueError:
                    pass
                else:
                    assert False, "ValueError must propagate"
                assert len(calls) == 1

            def test_single_attempt_never_sleeps():
                client, calls = scripted([APIError(429)])
                waits = []
                try:
                    call_with_retry(client, REQ, max_attempts=1, sleep=waits.append)
                except APIError:
                    pass
                assert waits == [] and len(calls) == 1, f"waits {waits}"
        ''',
        "solution": r'''
            import time


            def _retryable(err):
                code = getattr(err, "status_code", None)
                return code == 429 or (code is not None and 500 <= code <= 599)


            def call_with_retry(client, request, max_attempts=3, sleep=time.sleep):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return client(request)
                    except Exception as err:
                        if not _retryable(err) or attempt == max_attempts:
                            raise
                        sleep(2 ** (attempt - 1))
        ''',
        "hints": [
            "A for loop over attempt numbers, with try/except inside, and `return` as soon as a call works.",
            "In the except: re-raise if the error is not retryable or this was the last attempt; otherwise sleep 2 ** (attempt - 1) seconds and loop again.",
            "for attempt in 1..max_attempts: try return client(request); except Exception as err: code = getattr(err, \"status_code\", None); if code is not 429/5xx or attempt == max_attempts: raise; else sleep(2 ** (attempt - 1)).",
        ],
    },
    {
        "id": "llm-basics-16",
        "title": "One response shape for both providers",
        "difficulty": 2,
        "prompt": r'''
            Your app talks to two providers. Convert either response into one internal shape.

            **Write:** `normalize_response(response)`

            - `response`: an OpenAI-shaped dict (has `"choices"`) or an Anthropic-shaped dict
              (has `"content"` list and `"stop_reason"`)
            - **Returns:** a `dict` with exactly these keys:
              `{"provider": str, "text": str, "stop": str, "input_tokens": int, "output_tokens": int}`

            **Rules**
            - `provider`: `"openai"` if the dict has `"choices"`, else `"anthropic"` if it has `"content"`.
              If it has neither, raise `ValueError`.
            - `text`: OpenAI - the first choice's message content (`None` becomes `""`);
              Anthropic - all `"text"` blocks joined with nothing between.
            - `stop`: map the provider's reason to one vocabulary:
              `"stop"`/`"end_turn"`/`"stop_sequence"` -> `"complete"`, `"length"`/`"max_tokens"` ->
              `"truncated"`, `"tool_calls"`/`"tool_use"` -> `"tool"`, anything else -> `"other"`.
            - Tokens: OpenAI `prompt_tokens`/`completion_tokens`, Anthropic `input_tokens`/`output_tokens`;
              missing usage gives `0`.

            **Examples**
            ```python
            normalize_response({"choices": [{"message": {"role": "assistant", "content": "Hi"}, "finish_reason": "stop"}],
                                "usage": {"prompt_tokens": 5, "completion_tokens": 1}})
            # returns {"provider": "openai", "text": "Hi", "stop": "complete", "input_tokens": 5, "output_tokens": 1}
            normalize_response({"content": [{"type": "text", "text": "Hey"}], "stop_reason": "max_tokens",
                                "usage": {"input_tokens": 9, "output_tokens": 50}})
            # returns {"provider": "anthropic", "text": "Hey", "stop": "truncated", "input_tokens": 9, "output_tokens": 50}
            normalize_response({"error": "oops"})   # raises ValueError
            ```
        ''',
        "starter": r'''
            def normalize_response(response):
                ...
        ''',
        "tests": r'''
            from solution import normalize_response

            def oa(content, reason, usage=None):
                r = {"choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                                  "finish_reason": reason}]}
                if usage is not None:
                    r["usage"] = usage
                return r

            def an(blocks, reason, usage=None):
                r = {"role": "assistant", "content": blocks, "stop_reason": reason}
                if usage is not None:
                    r["usage"] = usage
                return r

            def test_openai_response():
                got = normalize_response(oa("Hi", "stop", {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6}))
                assert got == {"provider": "openai", "text": "Hi", "stop": "complete",
                               "input_tokens": 5, "output_tokens": 1}, f"got {got!r}"

            def test_anthropic_response_joins_text_blocks():
                blocks = [{"type": "text", "text": "Hey"}, {"type": "tool_use", "id": "t", "name": "f", "input": {}},
                          {"type": "text", "text": "!"}]
                got = normalize_response(an(blocks, "max_tokens", {"input_tokens": 9, "output_tokens": 50}))
                assert got == {"provider": "anthropic", "text": "Hey!", "stop": "truncated",
                               "input_tokens": 9, "output_tokens": 50}, f"got {got!r}"

            def test_stop_reason_mapping():
                cases = {("oa", "length"): "truncated", ("oa", "tool_calls"): "tool", ("oa", "content_filter"): "other",
                         ("an", "end_turn"): "complete", ("an", "stop_sequence"): "complete", ("an", "tool_use"): "tool",
                         ("an", "refusal"): "other"}
                for (kind, reason), want in cases.items():
                    resp = oa("x", reason) if kind == "oa" else an([{"type": "text", "text": "x"}], reason)
                    got = normalize_response(resp)["stop"]
                    assert got == want, f"{kind} {reason!r} -> {got!r}, expected {want!r}"

            def test_none_content_and_missing_usage():
                got = normalize_response(oa(None, "tool_calls"))
                assert got["text"] == "" and got["input_tokens"] == 0 and got["output_tokens"] == 0, f"got {got!r}"

            def test_unknown_shape_raises_value_error():
                try:
                    normalize_response({"error": "oops"})
                except ValueError:
                    return
                assert False, "expected ValueError"
        ''',
        "solution": r'''
            STOP_MAP = {
                "stop": "complete", "end_turn": "complete", "stop_sequence": "complete",
                "length": "truncated", "max_tokens": "truncated",
                "tool_calls": "tool", "tool_use": "tool",
            }


            def normalize_response(response):
                usage = response.get("usage") or {}
                if "choices" in response:
                    choice = response["choices"][0]
                    return {
                        "provider": "openai",
                        "text": choice["message"].get("content") or "",
                        "stop": STOP_MAP.get(choice.get("finish_reason"), "other"),
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                    }
                if "content" in response:
                    return {
                        "provider": "anthropic",
                        "text": "".join(b["text"] for b in response["content"] if b.get("type") == "text"),
                        "stop": STOP_MAP.get(response.get("stop_reason"), "other"),
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                    }
                raise ValueError("unknown response shape")
        ''',
        "hints": [
            "Branch on the shape first, and use a lookup dict for the stop-reason mapping.",
            "One dict maps every known provider reason to your vocabulary; `.get(reason, \"other\")` covers the rest. Read usage with `.get(..., 0)` from `response.get(\"usage\") or {}`.",
            "usage = response.get(\"usage\") or {}; if \"choices\" in response build the OpenAI version; elif \"content\" in response build the Anthropic version (join text blocks); else raise ValueError. Use STOP_MAP.get(reason, \"other\") for stop.",
        ],
    },
    {
        "id": "llm-basics-17",
        "title": "Collect an Anthropic stream",
        "difficulty": 2,
        "prompt": r'''
            Anthropic streams a reply as a sequence of typed **events**. Rebuild the final result.

            **Write:** `collect_anthropic_stream(events)`

            - `events`: an iterable (maybe a generator) of event dicts, for example:
              ```python
              {"type": "message_start", "message": {"usage": {"input_tokens": 12, "output_tokens": 1}}}
              {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}
              {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hel"}}
              {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "lo"}}
              {"type": "content_block_stop", "index": 0}
              {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 6}}
              {"type": "message_stop"}
              ```
            - **Returns:** a `dict` `{"text": str, "stop_reason": str or None, "input_tokens": int, "output_tokens": int}`

            **Rules**
            - `text`: join, in order, the `delta["text"]` of `content_block_delta` events whose
              delta `"type"` is `"text_delta"` (ignore other delta types, e.g. `"input_json_delta"`).
            - `input_tokens`: from the `message_start` event's `message.usage.input_tokens`.
            - `stop_reason` and `output_tokens`: from the `message_delta` event
              (`delta.stop_reason`, `usage.output_tokens`).
            - Ignore all other event types (e.g. `"ping"`). Missing values: `None` for
              `stop_reason`, `0` for token counts.

            **Examples**
            ```python
            collect_anthropic_stream(events_above)
            # returns {"text": "Hello", "stop_reason": "end_turn", "input_tokens": 12, "output_tokens": 6}
            collect_anthropic_stream([])
            # returns {"text": "", "stop_reason": None, "input_tokens": 0, "output_tokens": 0}
            ```
        ''',
        "research": {
            "note": "Look at the full list of streaming event types and their shapes, then come back.",
            "links": [{"title": "Streaming Messages - Anthropic API docs",
                       "url": "https://docs.anthropic.com/en/api/messages-streaming"}],
        },
        "starter": r'''
            def collect_anthropic_stream(events):
                ...
        ''',
        "tests": r'''
            from solution import collect_anthropic_stream

            def standard():
                return [
                    {"type": "message_start", "message": {"id": "msg_1", "role": "assistant", "content": [],
                                                          "usage": {"input_tokens": 12, "output_tokens": 1}}},
                    {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
                    {"type": "ping"},
                    {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hel"}},
                    {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "lo"}},
                    {"type": "content_block_stop", "index": 0},
                    {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                     "usage": {"output_tokens": 6}},
                    {"type": "message_stop"},
                ]

            def test_standard_stream():
                got = collect_anthropic_stream(standard())
                assert got == {"text": "Hello", "stop_reason": "end_turn", "input_tokens": 12,
                               "output_tokens": 6}, f"got {got!r}"

            def test_ignores_non_text_deltas():
                events = standard()
                events.insert(5, {"type": "content_block_delta", "index": 1,
                                  "delta": {"type": "input_json_delta", "partial_json": "{\"q\":"}})
                got = collect_anthropic_stream(events)
                assert got["text"] == "Hello", f"got {got!r}"

            def test_works_with_generator():
                got = collect_anthropic_stream(e for e in standard())
                assert got["text"] == "Hello" and got["output_tokens"] == 6, f"got {got!r}"

            def test_max_tokens_stop_reason():
                events = standard()
                events[6] = {"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 2}}
                got = collect_anthropic_stream(events)
                assert got["stop_reason"] == "max_tokens" and got["output_tokens"] == 2, f"got {got!r}"

            def test_empty_stream_defaults():
                got = collect_anthropic_stream([])
                assert got == {"text": "", "stop_reason": None, "input_tokens": 0, "output_tokens": 0}, f"got {got!r}"
        ''',
        "solution": r'''
            def collect_anthropic_stream(events):
                parts = []
                result = {"text": "", "stop_reason": None, "input_tokens": 0, "output_tokens": 0}
                for event in events:
                    kind = event.get("type")
                    if kind == "message_start":
                        usage = event.get("message", {}).get("usage") or {}
                        result["input_tokens"] = usage.get("input_tokens", 0)
                    elif kind == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            parts.append(delta.get("text", ""))
                    elif kind == "message_delta":
                        result["stop_reason"] = event.get("delta", {}).get("stop_reason")
                        result["output_tokens"] = (event.get("usage") or {}).get("output_tokens", 0)
                result["text"] = "".join(parts)
                return result
        ''',
        "hints": [
            "Loop once over the events and branch on event[\"type\"].",
            "Keep a list of text pieces and a result dict with defaults; message_start gives input tokens, content_block_delta gives text, message_delta gives the stop reason and output tokens.",
            "Start with defaults; for each event: if type is message_start read message.usage.input_tokens; if content_block_delta and delta type is text_delta append delta text; if message_delta read delta.stop_reason and usage.output_tokens; at the end join the pieces into \"text\".",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "llm-basics-18",
        "title": "A budgeted client",
        "difficulty": 3,
        "prompt": r'''
            Wrap a raw client in a class that tracks spending and refuses to go over budget.

            **Write:** a class `BudgetExceeded(Exception)` and a class `BudgetedClient`

            - `BudgetedClient(client, model, budget, input_price, output_price)`:
              - `client`: a function called as `client(model=..., messages=..., max_tokens=...)`,
                returning an OpenAI-shaped response with a `"usage"` block
              - `model`: a `str`; `budget`: a `float` in dollars
              - `input_price`, `output_price`: `float` dollars **per million tokens**
            - Attributes: `spent` (a `float`, starts at `0.0`) and `calls` (an `int`, starts at `0`)
            - `ask(prompt, system=None, max_tokens=256)`: returns the reply text (`str`)

            **Rules**
            - `ask` sends `messages` = the system message (only if `system` is given) followed by
              the user message `prompt`, with the stored `model` and the given `max_tokens`.
            - After each successful call: add the call's cost (from `usage.prompt_tokens` and
              `usage.completion_tokens`) to `spent`, and add 1 to `calls`.
            - If `spent` is already **greater than or equal to** `budget` when `ask` is called,
              raise `BudgetExceeded` **without** calling the client.
            - A call may push `spent` past the budget; it is the *next* call that is refused.
            - If the client raises, let the error propagate and leave `spent`/`calls` unchanged.

            **Examples**
            ```python
            bc = BudgetedClient(fake, "gpt-4o-mini", budget=0.01, input_price=3.0, output_price=15.0)
            bc.ask("Hi")          # returns the reply; usage 1000 in / 500 out -> spent == 0.0105, calls == 1
            bc.ask("Again")       # raises BudgetExceeded (0.0105 >= 0.01); fake is not called
            ```
        ''',
        "starter": r'''
            class BudgetExceeded(Exception):
                pass


            class BudgetedClient:
                def __init__(self, client, model, budget, input_price, output_price):
                    ...
        ''',
        "tests": r'''
            from solution import BudgetExceeded, BudgetedClient

            def make_fake(inp=1000, out=500, reply="ok"):
                calls = []
                def fake(**kwargs):
                    calls.append(kwargs)
                    return {"choices": [{"index": 0, "finish_reason": "stop",
                                         "message": {"role": "assistant", "content": reply}}],
                            "usage": {"prompt_tokens": inp, "completion_tokens": out, "total_tokens": inp + out}}
                return fake, calls

            def test_starts_at_zero():
                fake, _ = make_fake()
                bc = BudgetedClient(fake, "m", 1.0, 3.0, 15.0)
                assert bc.spent == 0 and bc.calls == 0, f"spent {bc.spent!r}, calls {bc.calls!r}"

            def test_ask_returns_text_and_sends_messages():
                fake, calls = make_fake(reply="Paris.")
                bc = BudgetedClient(fake, "gpt-4o-mini", 1.0, 3.0, 15.0)
                assert bc.ask("Capital?", system="Be brief.", max_tokens=20) == "Paris."
                assert calls[0] == {"model": "gpt-4o-mini", "max_tokens": 20, "messages": [
                    {"role": "system", "content": "Be brief."}, {"role": "user", "content": "Capital?"}]}, f"got {calls[0]!r}"
                bc.ask("Again")
                assert calls[1]["messages"] == [{"role": "user", "content": "Again"}], f"got {calls[1]!r}"
                assert calls[1]["max_tokens"] == 256

            def test_tracks_spend_and_calls():
                fake, _ = make_fake(1000, 500)
                bc = BudgetedClient(fake, "m", 1.0, 3.0, 15.0)
                bc.ask("a")
                bc.ask("b")
                assert abs(bc.spent - 0.021) < 1e-12 and bc.calls == 2, f"spent {bc.spent!r}, calls {bc.calls!r}"

            def test_refuses_once_budget_reached_without_calling():
                fake, calls = make_fake(1000, 500)
                bc = BudgetedClient(fake, "m", 0.01, 3.0, 15.0)
                bc.ask("Hi")
                try:
                    bc.ask("Again")
                except BudgetExceeded:
                    pass
                else:
                    assert False, "expected BudgetExceeded"
                assert len(calls) == 1 and bc.calls == 1, f"client called {len(calls)} times"

            def test_exactly_at_budget_is_refused():
                fake, calls = make_fake(1_000_000, 0)
                bc = BudgetedClient(fake, "m", 3.0, 3.0, 15.0)
                bc.ask("Hi")
                try:
                    bc.ask("Again")
                except BudgetExceeded:
                    return
                assert False, "spent == budget must be refused"

            def test_client_error_leaves_counters_unchanged():
                def broken(**kwargs):
                    raise RuntimeError("down")
                bc = BudgetedClient(broken, "m", 1.0, 3.0, 15.0)
                try:
                    bc.ask("Hi")
                except RuntimeError:
                    pass
                else:
                    assert False, "the client's error should propagate"
                assert bc.spent == 0 and bc.calls == 0

            def test_budget_exceeded_is_an_exception_subclass():
                assert issubclass(BudgetExceeded, Exception)
        ''',
        "solution": r'''
            class BudgetExceeded(Exception):
                pass


            class BudgetedClient:
                def __init__(self, client, model, budget, input_price, output_price):
                    self.client = client
                    self.model = model
                    self.budget = budget
                    self.input_price = input_price
                    self.output_price = output_price
                    self.spent = 0.0
                    self.calls = 0

                def ask(self, prompt, system=None, max_tokens=256):
                    if self.spent >= self.budget:
                        raise BudgetExceeded(f"spent ${self.spent:.4f} of ${self.budget:.4f}")
                    messages = []
                    if system is not None:
                        messages.append({"role": "system", "content": system})
                    messages.append({"role": "user", "content": prompt})
                    response = self.client(model=self.model, messages=messages, max_tokens=max_tokens)
                    usage = response.get("usage") or {}
                    cost = (usage.get("prompt_tokens", 0) * self.input_price
                            + usage.get("completion_tokens", 0) * self.output_price) / 1_000_000
                    self.spent += cost
                    self.calls += 1
                    return response["choices"][0]["message"]["content"]
        ''',
        "hints": [
            "Store everything on self in __init__; do the budget check first thing in ask.",
            "ask: refuse if spent >= budget; build the messages list; call the client with keywords; only after it returns, compute the cost from usage and update spent and calls.",
            "In ask: `if self.spent >= self.budget: raise BudgetExceeded(...)`; messages = [system dict if system is not None] + [user dict]; response = self.client(model=..., messages=..., max_tokens=...); cost = (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000; add to spent, calls += 1; return the reply text.",
        ],
    },
]
