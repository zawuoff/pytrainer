TOPIC = {
    "id": "api-data",
    "title": "Working with API Data",
    "track": "apis-data",
    "order": 2,
    "requires": ["json", "errors"],
    "summary": """
        Handling API-shaped data offline: navigating nested responses safely,
        pagination, retries with exponential backoff, status codes, aggregating
        usage and building validated request payloads.
    """,
    "concepts": ["nested dict access", ".get() chains", "None handling", "pagination cursors",
                 "exponential backoff", "dependency injection", "status codes",
                 "custom exceptions", "aggregation", "payload validation"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["api", "response", "nested", "path", "get", "none", "missing key", "default",
                 "status code", "retry", "backoff", "pagination", "cursor", "apierror",
                 "tool call", "usage"],
    "cards": [
        {
            "syntax": 'response["choices"][0]["message"]["content"]',
            "explain": "A path: each pair of brackets does one lookup, left to right. A key reads a dict, an index reads a list.",
            "example": r'''
                response = {"choices": [{"message": {"content": "Hi"}}]}
                print(response["choices"][0])
                # {'message': {'content': 'Hi'}}
                print(response["choices"][0]["message"]["content"])
                # Hi
            ''',
        },
        {
            "syntax": "d.get(key) or default",
            "explain": "Gives the default when the key is missing and when it holds None. d.get(key, default) covers only a missing key.",
            "example": r'''
                reply = {"content": None}
                print(reply.get("content", "?"))
                # None
                print(reply.get("content") or "?")
                # ?
                print(reply.get("id") or "?")
                # ?
            ''',
        },
        {
            "syntax": "total += d.get(key) or 0",
            "explain": "Adds up a count that can be missing or None. Start the total at 0 before the loop.",
            "example": r'''
                responses = [{"tokens": 10}, {"tokens": None}, {}]
                total = 0
                for response in responses:
                    total += response.get("tokens") or 0
                print(total)
                # 10
            ''',
        },
        {
            "syntax": "status == 429 or 500 <= status <= 599",
            "explain": "True for the failures worth sending again. 200 <= status <= 299 is success. Other 4xx codes need a fixed request.",
            "example": r'''
                for status in (200, 401, 429, 503):
                    retry = status == 429 or 500 <= status <= 599
                    print(status, 200 <= status <= 299, retry)
                # 200 True False
                # 401 False False
                # 429 False True
                # 503 False True
            ''',
        },
        {
            "syntax": "class APIError(Exception):",
            "explain": "An exception class that stores the status code. An except block reads it as err.status.",
            "example": r'''
                class APIError(Exception):
                    def __init__(self, status, message):
                        super().__init__(message)
                        self.status = status
                err = APIError(429, "slow down")
                print(err.status, err)
                # 429 slow down
            ''',
        },
        {
            "syntax": 'while page.get("next_cursor"):',
            "explain": "Repeats while the page gives a cursor for a next page. Each round reads the page for that cursor.",
            "example": r'''
                pages = {None: {"data": [1], "next_cursor": "p2"}, "p2": {"data": [2]}}
                page = pages[None]
                items = page["data"]
                while page.get("next_cursor"):
                    page = pages[page["next_cursor"]]
                    items = items + page["data"]
                print(items)
                # [1, 2]
            ''',
        },
    ],
}

LESSON = r'''
## Working with API data: chapter notes

An **API** is a service your program sends requests to. An API response is JSON text.
After `json.loads` decodes (parses) it, it is a dict whose
values can be other dicts and lists. A dict or list stored inside another one is **nested**.

## Paths

A **path** is a sequence of lookups written one after another. Each pair of square brackets
does one lookup: a key reads from a dict, an index reads from a list. Python evaluates the
lookups from left to right.

```python
response = {
    "model": "gpt-4o",
    "choices": [{"message": {"role": "assistant", "content": "Hi"}}],
    "usage": None,
}
print(response["choices"][0]["message"]["content"])
# Hi
```

Step through the path to see the value that each lookup returns.

```diagram
{"type":"flow","title":"Reading response[\"choices\"][0][\"message\"][\"content\"]","steps":[
{"label":"response","detail":"The path starts at the whole response. It is a dict with the keys model, choices and usage.","code":"{'model': 'gpt-4o',\n 'choices': [{'message': {'role': 'assistant', 'content': 'Hi'}}],\n 'usage': None}"},
{"label":"[\"choices\"]","detail":"The key choices reads from the response dict. The value is a list with one item.","code":"[{'message': {'role': 'assistant', 'content': 'Hi'}}]"},
{"label":"[0]","detail":"The index 0 reads the first item of that list. The item is a dict with one key, message.","code":"{'message': {'role': 'assistant', 'content': 'Hi'}}"},
{"label":"[\"message\"]","detail":"The key message reads from that dict. The value is another dict with the keys role and content.","code":"{'role': 'assistant', 'content': 'Hi'}"},
{"label":"[\"content\"]","detail":"The key content reads from the message dict. The value is a string, and it is the result of the whole path.","code":"'Hi'"}
]}
```

## Missing keys and None values

A key can be **missing** (not in the dict), or it can be present and hold `None`. JSON
`null` decodes to `None`. The two cases behave differently.

| expression | key missing | key holds `None` |
| --- | --- | --- |
| `d["k"]` | raises `KeyError` | `None` |
| `d.get("k")` | `None` | `None` |
| `d.get("k", 0)` | `0` | `None` |
| `d.get("k") or 0` | `0` | `0` |

`.get(key, default)` returns the default only when the key is missing. `a or b` returns `b`
whenever `a` is falsy (counts as `False` in a condition), and `None` is falsy.

```python
response = {"choices": [], "usage": None}
usage = response.get("usage") or {}
print(usage.get("total_tokens", 0))
# 0
choices = response.get("choices") or []
print(choices[0]["message"]["content"] if choices else "no reply")
# no reply
```

Click a key, or type a key that is not in the dict, and compare `d[key]` with `d.get(key)`.

```diagram
{"type":"dict","title":"Keys of response","name":"response","entries":[["model","gpt-4o"],["choices",[{"message":{"role":"assistant","content":"Hi"}}]],["usage",null]]}
```

## Status codes

**HTTP** is the set of rules programs use to exchange messages over the web. Every HTTP
response has a three-digit **status code**. Codes `200` to `299` mean success.
Codes `400` to `499` mean the request was wrong: `400` is bad input, `401` is a bad API key,
`403` is forbidden, `404` is not found and `429` is rate limited: you sent too many requests
in a short time. Codes `500` to `599` mean the server failed.

Retry only `429`, the `5xx` codes and connection errors (the server could not be reached).
Sending the same request again after a `401` returns `401` again.

## Exponential backoff

**Exponential backoff** means that the wait doubles after each failed attempt. The wait
before retry number `attempt` is `base_delay * 2 ** attempt`, counting attempts from `0`.
When a `429` body gives a `retry_after` number, wait at least that long.

Pass the wait function in as a parameter, as in `sleep=time.sleep` (`time.sleep(n)` pauses
the program for `n` seconds). A test can then pass
`delays.append` and record the waits without waiting. Passing in the things a function
depends on is called **dependency injection**.

```python
base_delay = 1.0
for attempt in range(4):
    print(attempt, base_delay * 2 ** attempt)
# 0 1.0
# 1 2.0
# 2 4.0
# 3 8.0
```

## Errors as exceptions

A class that inherits from `Exception` can store the status code as an attribute. The
caller catches it with `except APIError as err:` and reads `err.status`.

```python
class APIError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status

try:
    raise APIError(429, "rate limited")
except APIError as err:
    print(err.status, err)
# 429 rate limited
```

## Pagination

**Pagination** means the API returns a long list one page at a time. Each page is a dict
with the items under `"data"` and a **cursor** under `"next_cursor"`: a value you send back
to request the next page. You loop until the cursor is `None`. A page limit stops the loop
if the API never returns `None`. In the example the dict `pages` stands in for the API:
`pages[cursor]` is the page that a request with that cursor would return.

```python
pages = {
    None: {"data": ["a", "b"], "next_cursor": "p2"},
    "p2": {"data": ["c"], "next_cursor": None},
}
items = []
cursor = None
for _ in range(10):
    page = pages[cursor]
    items.extend(page.get("data") or [])
    cursor = page.get("next_cursor")
    if cursor is None:
        break
print(items)
# ['a', 'b', 'c']
```

## Tool call arguments

An **LLM** (large language model) is a program that writes text. A **tool** is a function in your
program that an LLM can ask you to run. The request is a
**tool call**: a dict with the function's name and its arguments. The `"arguments"` of a
tool call are a JSON string, not a dict. `json.loads` decodes the string. Invalid JSON raises `json.JSONDecodeError`, which is a subclass of `ValueError`.

```python
import json

call = {"name": "get_weather", "arguments": '{"city": "Paris"}'}
print(type(call["arguments"]).__name__)
# str
args = json.loads(call["arguments"])
print(args["city"])
# Paris
print(issubclass(json.JSONDecodeError, ValueError))
# True
```

## Common mistakes

- `d.get(k, default)` returns `None` when the key holds `None`. Use `d.get(k) or default`.
- `choices[0]` raises `IndexError` when `choices` is `[]`. Check `if choices:` first.
- An API can omit `total_tokens`. Add `prompt_tokens` and `completion_tokens` yourself.
'''

EXERCISES = [
    {
        "id": "api-data-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            ## Finding one value inside a model's reply

            You send a question to a model. What comes back is more than the answer. The reply also says
            which model wrote it and how many tokens it used, because tokens are what you pay for. Once
            `json.loads` has turned the reply into Python data, all of that sits in one dict, and some of
            its values are dicts themselves.

            ```python
            reply = {
                "id": "msg_01",
                "model": "claude-sonnet",
                "usage": {"input_tokens": 25, "output_tokens": 110},
            }
            print(reply["model"])
            # claude-sonnet
            print(reply["usage"])
            # {'input_tokens': 25, 'output_tokens': 110}
            print(reply["usage"]["output_tokens"])
            # 110
            ```

            Read the last line from left to right. `reply["usage"]` hands back the inner dict. The second
            pair of brackets then reads the key `"output_tokens"` from that inner dict. A dict that is
            stored inside another dict is called **nested**, and a row of lookups like this one is called
            a **path**.

            ```predict
            job = {
                "id": "job_7",
                "status": "done",
                "result": {"chunks": 42, "failed": 3},
            }
            print(job["status"])
            print(job["result"]["failed"])
            ---
            `job["status"]` reads a key of the outer dict. `job["result"]` hands back the inner dict, and `["failed"]` reads `3` from it.
            ```

            ### When a key is not there

            A reply is not always complete. When a request fails, many APIs send a dict with an `"error"`
            key. When the request works, that key does not exist at all. Your code has to cope with both.

            Square brackets stop the program with `KeyError: 'error'` when the key is missing. The Dicts
            chapter showed the gentler way: `.get(key)` hands back `None` for a missing key, and
            `.get(key, default)` hands back a default that you choose.

            ```python
            reply = {"model": "claude-sonnet", "usage": {"input_tokens": 25}}
            print(reply.get("error"))
            # None
            print(reply.get("error", "no error"))
            # no error
            print(reply.get("error", {}).get("message", "all fine"))
            # all fine
            ```

            The last line has two `.get` calls in a row. The first finds no `"error"` key, so it hands
            back its default, the empty dict `{}`. The second `.get` then runs on that empty dict, finds
            no `"message"` in it, and hands back its own default.

            A default is used only when the key is missing. When the key is there, `.get` ignores the
            default and hands back the stored value.

            ```quiz
            `reply` is `{"usage": {"input_tokens": 25}}`. What does `reply.get("usage", {}).get("input_tokens", 0)` give?
            - [x] `25` :: Right. `"usage"` is a key of `reply`, so the first `.get` hands back the real inner dict. The second `.get` finds `"input_tokens"` in it.
            - [ ] `0` :: `0` is the default of the second `.get`, and a default is used only when the key is missing. `"input_tokens"` is in the inner dict.
            - [ ] `{}` :: `{}` is the default of the first `.get`. The key `"usage"` exists, so that default is never used, and the second `.get` still runs on the result.
            ```

            Click a row to read that key. Then type `error` into the key box and press `reply[key]` and
            `reply.get(key)` in turn:

            ```diagram
            {"type":"dict","title":"Keys of reply","name":"reply","entries":[["id","msg_01"],["model","claude-sonnet"],["usage",{"input_tokens":25,"output_tokens":110}]]}
            ```

            **Watch out:** `.get` protects one lookup, not the whole path. `reply.get("error")["message"]`
            stops with `TypeError: 'NoneType' object is not subscriptable`. That message means: the first
            lookup handed back `None`, and you then tried to read a key from `None`.

            **In short:** each lookup in a path reads from what the lookup before it handed back, and
            `.get` hands back `None` or your default when a key is missing.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            response = {"model": "gpt-4o", "usage": {"prompt_tokens": 12, "completion_tokens": 30}}
            print(response["usage"]["completion_tokens"])
            print(response.get("error"))
            print(response.get("usage", {}).get("total_tokens", 0))
        ''',
        "solution": r'''
            30
            None
            0
        ''',
        "explanation": r'''
            Line 1 is a path. `response["usage"]` hands back the inner dict, and `["completion_tokens"]`
            reads `30` from it.

            Line 2: `response` has no `"error"` key. `.get("error")` does not stop the program. It hands
            back `None`, and `print` shows that as `None`.

            Line 3: the key `"usage"` exists, so the first `.get` ignores its default `{}` and hands back
            the real inner dict. That inner dict has no `"total_tokens"` key, so the second `.get` hands
            back its own default, `0`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Take the three `print` lines one at a time. For every lookup, ask: is that key in the dict it is reading from?",
            "Square brackets and `.get` both go one level deeper. They only differ when the key is missing: `.get` then hands back `None`, or the default that was given to it.",
            "Line 1 walks into `usage` and reads a count that is there. Line 2 asks the outer dict for a key it does not have, and gives no default. Line 3 finds `usage`, and then asks that inner dict for a key it does not have, with a default.",
        ],
    },
    {
        "id": "api-data-s3",
        "title": "Fix the role lookup",
        "difficulty": 0,
        "lesson": r'''
            ## When the path goes through a list

            Ask an API which models you may use, and you do not get one model back. You get a list of
            them, wrapped in a dict. To reach the name of one model, your path has to step through that
            list.

            ```python
            listing = {
                "object": "list",
                "data": [
                    {"id": "gpt-4o", "owned_by": "openai"},
                    {"id": "gpt-4o-mini", "owned_by": "openai"},
                ],
            }
            print(listing["data"][0])
            # {'id': 'gpt-4o', 'owned_by': 'openai'}
            print(listing["data"][0]["id"])
            # gpt-4o
            ```

            `listing["data"]` hands back a list. `[0]` reads the first item of that list, and that item
            is a dict. `["id"]` reads a key from that dict.

            So there is one rule for every pair of brackets in a path. A key, in quotes, reads from a
            dict. A whole number reads from a list, and that number is the index you know from the Lists
            chapter. Press Next to see what each pair of brackets hands back:

            ```diagram
            {"type":"flow","title":"Reading listing[\"data\"][0][\"id\"]","steps":[
            {"label":"listing","detail":"The path starts at the whole response. It is a dict with the keys object and data.","code":"{'object': 'list',\n 'data': [{'id': 'gpt-4o', 'owned_by': 'openai'},\n          {'id': 'gpt-4o-mini', 'owned_by': 'openai'}]}"},
            {"label":"[\"data\"]","detail":"The key data reads from that dict. The value is a list with two items.","code":"[{'id': 'gpt-4o', 'owned_by': 'openai'},\n {'id': 'gpt-4o-mini', 'owned_by': 'openai'}]"},
            {"label":"[0]","detail":"The index 0 reads the first item of the list. The item is a dict with the keys id and owned_by.","code":"{'id': 'gpt-4o', 'owned_by': 'openai'}"},
            {"label":"[\"id\"]","detail":"The key id reads from that dict. The value is a string, and it is the result of the whole path.","code":"'gpt-4o'"}
            ]}
            ```

            Everything you know about lists still works in the middle of a path. `[-1]` reads the last
            item, and `len` counts the items:

            ```python
            listing = {"data": [{"id": "gpt-4o"}, {"id": "gpt-4o-mini"}]}
            print(listing["data"][-1]["id"])
            # gpt-4o-mini
            print(len(listing["data"]))
            # 2
            ```

            Match each expression to what it hands back for the `listing` above:

            ```match
            `listing["data"]` :: a list of two dicts
            `listing["data"][1]` :: one dict, the second item of the list
            `listing["data"][0]["id"]` :: the string `"gpt-4o"`
            `len(listing["data"])` :: the number `2`
            ```

            ```quiz
            A small account may use only one model, so `listing["data"]` has one item. What does `listing["data"][1]["id"]` do?
            - [x] It stops the program with an `IndexError` :: Right. One item sits at index 0 and nothing is at index 1. Python stops with `IndexError: list index out of range` before it ever looks for `"id"`.
            - [ ] It hands back the id of the only model :: The only item is at index 0. Index 1 would be a second item, and there is none.
            - [ ] It hands back `None` :: Only `.get` on a dict hands back `None` for something that is missing. A list index past the end is an error.
            ```

            **Watch out:** a `[1]` in a path reads the second item, not the first. When the list has two
            items you get the wrong one, with no error to warn you. When it has one item the program
            stops with `IndexError: list index out of range`.

            **In short:** in a path, a key reads from a dict and an index reads from a list, and the
            first item of a list is at index 0.
        ''',
        "prompt": r'''
            A chat request holds the conversation as a list of messages. Each message is a dict that
            says who is speaking (its `"role"`) and what was said (its `"content"`). Someone wrote a
            small function that reports who speaks first. It has a bug: it reports the role of the wrong
            message, and it stops with an error when the conversation has only one message.

            **Your job:** find the bug in `first_role(request)` and fix it, so that it gives back the
            role of the first message. The code is already in the editor, and one small change is enough.

            **What goes in**
            - `request`: a dict with a `"messages"` list that holds at least one message, for example
              `{"messages": [{"role": "system", "content": "Be brief"}, {"role": "user", "content": "Hi"}]}`

            **What comes out**
            - the `"role"` of the first message, a string: `"system"` for the example value

            **Rules**
            - It must also work when the list holds a single message.

            **Examples**
            ```python
            first_role({"messages": [{"role": "system", "content": "Be brief"},
                                     {"role": "user", "content": "Hi"}]})   # returns "system"
            first_role({"messages": [{"role": "user", "content": "Hi"}]})   # returns "user"
            ```
        ''',
        "starter": r'''
            def first_role(request):
                return request["messages"][1]["role"]
        ''',
        "tests": r'''
            from solution import first_role

            def test_returns_role_of_first_of_two_messages():
                req = {"messages": [{"role": "system", "content": "Be brief"},
                                    {"role": "user", "content": "Hi"}]}
                got = first_role(req)
                assert got == "system", f"got {got!r}"

            def test_works_with_a_single_message():
                got = first_role({"messages": [{"role": "user", "content": "Hi"}]})
                assert got == "user", f"got {got!r}"
        ''',
        "solution": r'''
            def first_role(request):
                return request["messages"][0]["role"]
        ''',
        "hints": [
            "Read the path in the function one pair of brackets at a time. Which pair picks the message?",
            "The quiz in the lesson shows what happens when a path asks a list of one item for a second item. Which item does the function ask for?",
            "Only the number in the path has to change. Make it the index of the first item of a list, and leave the two keys as they are.",
        ],
    },
    {
        "id": "api-data-s2",
        "title": "Model name with a default",
        "difficulty": 0,
        "lesson": r'''
            ## A stand-in for a key that is not always there

            A dashboard shows one line for every call to a model, and the line says why the model stopped
            writing. Most replies carry that reason under the key `"stop_reason"`. A reply that was cut
            off on the way does not. The dashboard should show something sensible in both cases.

            ```python
            reply = {"model": "claude-sonnet", "stop_reason": "end_turn"}
            cut_off = {"model": "claude-sonnet"}
            print(reply.get("stop_reason", "not given"))
            # end_turn
            print(cut_off.get("stop_reason", "not given"))
            # not given
            print(cut_off.get("stop_reason"))
            # None
            ```

            `.get` takes two values in its parentheses: the key to look for, and what to hand back when
            that key is missing. For `reply` the key is there, so the second value is ignored. For
            `cut_off` the key is missing, so the second value is the result. You met it in the Dicts
            chapter as the **default value**. Programmers also call it a **fallback**.

            With one value in the parentheses, the fallback is `None`. That is the last line.

            ```predict
            piece = {"index": 4, "text": "Hel"}
            print(piece.get("text", "?"))
            print(piece.get("role", "assistant"))
            print(piece.get("index", 0))
            ---
            `"text"` and `"index"` are keys of `piece`, so their stored values `Hel` and `4` come back and the defaults are ignored. There is no `"role"` key, so the default `assistant` comes back.
            ```

            ### Choose a fallback that the next line can use

            A fallback is not only there to avoid an error. The line after it will work with the result,
            so the fallback should be the same kind of value as the real one: text where text is
            expected, `0` for a count, an empty list where a list is expected.

            Some replies list the web pages they used under `"sources"`. Others have no such key. Pick
            the fallback that lets this program count the sources either way:

            ```fill
            piece = {"index": 4, "text": "Hel"}
            sources = piece.get("sources", ___)
            print(len(sources))
            ---
            - [x] [] :: Right. An empty list can be counted, so the program prints `0`.
            - [ ] None :: `len(None)` stops the program with `TypeError: object of type 'NoneType' has no len()`. `None` is what `.get` hands back anyway when you give it no fallback.
            - [ ] 0 :: `0` looks like the count you want, but `sources` should be the list, and a number cannot be counted: `TypeError: object of type 'int' has no len()`.
            ```

            **Watch out:** a fallback that is text needs quotes. `piece.get("role", assistant)` without
            them stops with `NameError: name 'assistant' is not defined`, because Python reads a bare
            word as the name of a variable.

            **In short:** `d.get(key, fallback)` hands back the stored value when the key is there and
            your fallback when it is not.
        ''',
        "prompt": r'''
            Your app writes one line to its log for every call, and the line names the model that
            answered. A normal response says which model that was. A response that reports an error may
            not say it.

            **Your job:** finish `get_model(response)` so that it gives back the name of the model, or a
            stand-in text when the response does not name one. The function is already written except
            for one gap, marked `___`. Replace the gap.

            **What goes in**
            - `response`: a dict, for example `{"model": "gpt-4o", "choices": []}`. It may have no
              `"model"` key, and it may be empty.

            **What comes out**
            - the value stored under `"model"`, for example `"gpt-4o"`
            - the string `"unknown"` when there is no `"model"` key

            **Rules**
            - An empty dict `{}` gives `"unknown"` as well. The function never stops with an error.

            **Examples**
            ```python
            get_model({"model": "gpt-4o", "choices": []})   # returns "gpt-4o"
            get_model({"error": "timeout"})                 # returns "unknown"
            get_model({})                                   # returns "unknown"
            ```
        ''',
        "starter": r'''
            def get_model(response):
                return response.get("model", ___)
        ''',
        "tests": r'''
            from solution import get_model

            def test_returns_model_when_present():
                got = get_model({"model": "gpt-4o", "choices": []})
                assert got == "gpt-4o", f"got {got!r}"

            def test_missing_model_returns_unknown():
                got = get_model({"error": "timeout"})
                assert got == "unknown", f"got {got!r}"

            def test_empty_response_returns_unknown():
                assert get_model({}) == "unknown"
        ''',
        "solution": r'''
            def get_model(response):
                return response.get("model", "unknown")
        ''',
        "hints": [
            "Look at the first example in the lesson. What does the second value in the parentheses of `.get` do?",
            "The gap is the value that comes back when the response has no `\"model\"` key. The task names that value.",
            "Put the stand-in text from the task into the gap. It is text, so write it as a string, with quotes around it.",
        ],
    },
    {
        "id": "api-data-s6",
        "title": "Missing or None?",
        "difficulty": 0,
        "lesson": r'''
            ## A key that is there, but holds nothing

            Remember the dashboard from the last step? A reply that was cut off had no `"stop_reason"`
            key, and a fallback filled the hole. Here is a third kind of reply: one that the model is
            still writing. Its JSON says `"stop_reason": null`, and `json.loads` turns `null` into
            `None`. The key is there. What it holds is nothing.

            ```python
            reply = {"model": "claude-sonnet", "stop_reason": None}
            print(reply.get("stop_reason", "not given"))
            # None
            print(reply.get("id", "not given"))
            # not given
            ```

            The fallback did not help on the first line. `.get` uses its fallback only when the key is
            **missing**. Here the key is there, so `.get` hands back what is stored under it, and that is
            `None`. On the second line the key really is missing, so the fallback comes back.

            Click the `stop_reason` row. Then type `id` into the key box and press `reply.get(key)`. Both
            answers are `None`. Press `key in reply` for each of them to see the difference:

            ```diagram
            {"type":"dict","title":"A key that holds None, and a key that is missing","name":"reply","entries":[["model","claude-sonnet"],["stop_reason",null]]}
            ```

            ```predict
            msg = {"text": None}
            print(msg.get("text", "nothing"))
            print(msg.get("label", "nothing"))
            print("text" in msg, "label" in msg)
            ---
            `"text"` is a key of `msg` and holds `None`, so the first line prints the stored `None` and ignores the fallback. `"label"` is missing, so the second line prints the fallback. `in` tells the two cases apart: `True` for the key that is there, `False` for the one that is not.
            ```

            ### One line that covers both

            Your code rarely cares which of the two it was. Either way there is no stop reason to show.

            With no fallback, `.get(key)` hands back `None` in both cases. And the Conditionals chapter
            gave you a tool that replaces a `None`: `a or b` hands back `a` when `a` is truthy, and `b`
            otherwise. `None` is falsy.

            ```python
            reply = {"model": "claude-sonnet", "stop_reason": None}
            print(reply.get("stop_reason") or "not given")
            # not given
            print(reply.get("id") or "not given")
            # not given
            print(reply.get("model") or "not given")
            # claude-sonnet
            ```

            The fallback now stands after `or`, outside the parentheses of `.get`. A real value such as
            `"claude-sonnet"` is truthy, so it passes through untouched.

            ```try
            answer = {"text": None, "tokens": 0}
            text = answer.get("text", "(no text)")
            print(text)
            ---
            The program prints `None`. Change the second line so that it prints `(no text)`.
            ---
            answer = {"text": None, "tokens": 0}
            text = answer.get("text") or "(no text)"
            print(text)
            ---
            The key `"text"` is there, so a fallback inside `.get` is never used. `or` looks at the value that came back, and replaces it when it is `None`.
            ```

            **Watch out:** `or` replaces every falsy value, not only `None`. A stored `0` or `""` is
            replaced too: for `answer` above, `answer.get("tokens") or 100` gives `100`. That does no
            harm when the fallback is itself the empty value, as in `or 0`, `or ""` and `or []`.

            **In short:** `d.get(key, fallback)` covers a missing key only, and `d.get(key) or fallback`
            covers a missing key and a stored `None`.
        ''',
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            message = {"role": "assistant", "content": None}
            print(message.get("content", "empty"))
            print(message.get("content") or "empty")
            print(message.get("name", "anon"))
            print(message.get("name") or "anon")
        ''',
        "solution": r'''
            None
            empty
            anon
            anon
        ''',
        "explanation": r'''
            Line 1: the key `"content"` is in the dict, and `None` is stored under it. `.get` uses its
            fallback only for a missing key, so it hands back the stored `None`.

            Line 2: `.get("content")` hands back the same `None`. `None` is falsy, so `or` hands back
            its right side, `empty`.

            Line 3: there is no `"name"` key at all. This time `.get` does use its fallback, `anon`.

            Line 4: for the missing key, `.get("name")` hands back `None`, and `or` again hands back its
            right side, `anon`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "For each line, ask two questions. Is the key in the dict at all? And if it is, what is stored under it?",
            "`.get(key, fallback)` uses the fallback only when the key is missing. `or` hands back its right side whenever its left side is falsy, and `None` is falsy.",
            "Lines 1 and 2 read a key that is there and holds `None`: one of them prints what is stored, and the other replaces it. Lines 3 and 4 read a key that is not there, and both ways of writing it end at the fallback.",
        ],
    },
    {
        "id": "api-data-s5",
        "title": "Count the results",
        "difficulty": 0,
        "lesson": r'''
            ## A list you can always count

            Under an answer, your app shows a line such as "2 sources". Some replies list the web pages
            they used under `"sources"`. Some have no such key. And some, like the reply in the last
            step, have the key with `None` under it. That makes three shapes, and your code wants one
            thing from all of them: a list that it can count.

            ```python
            replies = [{"sources": ["a.com", "b.org"]}, {"sources": None}, {}]
            for reply in replies:
                sources = reply.get("sources") or []
                print(len(sources), sources)
            # 2 ['a.com', 'b.org']
            # 0 []
            # 0 []
            ```

            `reply.get("sources")` hands back the list from the first reply, and `None` from the other
            two. `or []` turns that `None` into an empty list. After this one line, `sources` is a list
            whatever the reply looked like.

            An empty list is a comfortable value to hold. `len` gives 0 for it, and a `for` loop over it
            runs zero times. Neither of them needs a special case.

            ```predict
            reply = {"text": "Paris.", "sources": None}
            sources = reply.get("sources") or []
            for url in sources:
                print("source:", url)
            print(len(sources), "sources")
            ---
            `"sources"` holds `None`, so `or` hands back the empty list. A `for` loop over an empty list runs zero times, so the loop prints nothing. `len` of an empty list is 0, and the last line prints `0 sources`.
            ```

            Turning every shape of "nothing" into one known value, at the moment you read it, is called
            **normalising** the data. The lines after it then have a single case to deal with.

            The way you write the fallback matters, as the last step showed. Pick the line that makes
            this program print `0`:

            ```fill
            reply = {"text": "Paris.", "sources": None}
            sources = ___
            print(len(sources))
            ---
            - [x] reply.get("sources") or [] :: Right. `.get` hands back the stored `None`, and `or` replaces it with an empty list, which has a length of 0.
            - [ ] reply.get("sources", []) :: The key is there, so `.get` ignores the fallback and hands back the stored `None`. `len(None)` stops with `TypeError: object of type 'NoneType' has no len()`.
            - [ ] reply["sources"] :: Square brackets hand back the stored `None` as well, so `len` stops with the same `TypeError`. For a reply without the key they would stop with a `KeyError` instead.
            ```

            **Watch out:** `len` and `for` both need something they can walk through. `for url in None`
            stops with `TypeError: 'NoneType' object is not iterable`. When an error message mentions
            `NoneType`, look for a value that you read from the data and did not normalise.

            **In short:** `d.get(key) or []` always hands you a list, whether the key holds a list,
            holds `None` or is missing.
        ''',
        "prompt": r'''
            A search API sends its results one page at a time. Each page is a dict, and the results sit
            in a list under the key `"data"`. Your app shows how many results the current page holds.
            Pages are not always complete: on some of them `"data"` holds `None`, and on some the key is
            missing.

            **Your job:** write `count_results(page)` so that it gives back the number of results on the
            page.

            **What goes in**
            - `page`: a dict, for example `{"data": ["a", "b"], "next_cursor": "x"}`. Other keys, such
              as `"next_cursor"`, play no part here.

            **What comes out**
            - a whole number: how many items the list under `"data"` has, `2` for the example value

            **Rules**
            - An empty list under `"data"` gives `0`.
            - `None` under `"data"` gives `0`.
            - A page without a `"data"` key gives `0`. The function never stops with an error.

            **Examples**
            ```python
            count_results({"data": ["a", "b"], "next_cursor": "x"})   # returns 2
            count_results({"data": []})                               # returns 0
            count_results({"data": None})                             # returns 0
            count_results({})                                         # returns 0
            ```
        ''',
        "starter": r'''
            def count_results(page):
                ...
        ''',
        "tests": r'''
            from solution import count_results

            def test_counts_items_in_data():
                assert count_results({"data": ["a", "b"], "next_cursor": "x"}) == 2

            def test_empty_data_list_returns_zero():
                assert count_results({"data": []}) == 0

            def test_none_data_returns_zero():
                assert count_results({"data": None}) == 0, "None data should count as 0"

            def test_missing_data_key_returns_zero():
                assert count_results({}) == 0, "missing data should count as 0"
        ''',
        "solution": r'''
            def count_results(page):
                return len(page.get("data") or [])
        ''',
        "hints": [
            "The lesson turns three shapes of \"no sources\" into one list. A page has the same three shapes for `\"data\"`.",
            "First make sure that you hold a list, whatever the page looks like. Counting a list is then one call of a built-in function.",
            "Read `\"data\"` with the method that hands back `None` for a missing key. Replace a `None` with an empty list, the way the lesson does with `or`. Then hand back the length of that list.",
        ],
    },
    {
        "id": "api-data-s4",
        "title": "Was it a success?",
        "difficulty": 0,
        "lesson": r'''
            ## Did the request work?

            Before your code reads the body of a response, it should ask one question: did the request
            work at all? The body of a failed request has a different shape from the body of a
            successful one. A path written for one of them stops with an error on the other.

            Every response answers that question with a three-digit number. You met it in the HTTP
            chapter. It is the **status code**, and its first digit names the group it belongs to:

            - `2xx`, the codes 200 to 299: the request worked.
            - `4xx`, the codes 400 to 499: something was wrong with the request you sent.
            - `5xx`, the codes 500 to 599: the server failed.

            A group is a range of numbers, and the Conditionals chapter gave you the tool for a range,
            the chained comparison:

            ```python
            def is_client_error(status):
                return 400 <= status < 500

            for status in (399, 400, 429, 500):
                print(status, is_client_error(status))
            # 399 False
            # 400 True
            # 429 True
            # 500 False
            ```

            `400 <= status < 500` means "400 is at most `status`, and `status` is below 500". The `<=`
            lets 400 itself in. The `<` keeps 500 out. Writing `<= 499` on the right would do the same
            job, because a status code is a whole number.

            The two signs are easy to get wrong at the edges. This function leaves out one code that
            belongs to its group:

            ```try
            def is_server_error(status):
                return 500 < status < 600

            print(is_server_error(500), is_server_error(599), is_server_error(600))
            ---
            `500` is a server error, but the program prints `False True False`. Change one comparison sign so that it prints `True True False`.
            ---
            def is_server_error(status):
                return 500 <= status < 600

            print(is_server_error(500), is_server_error(599), is_server_error(600))
            ---
            `<` leaves its limit out and `<=` lets it in. The lowest code of a group belongs to the group, so that end needs `<=`.
            ```

            ### Hand the comparison straight back

            Neither function has an `if`. A comparison already produces `True` or `False`, and `return`
            can hand that bool back as it is. Wrapping it in an `if` invites a quiet bug:

            ```quiz
            What does `is_client_error(200)` hand back with this version of the function?

            ~~~python
            def is_client_error(status):
                if 400 <= status < 500:
                    return True
            ~~~
            - [x] `None` :: Right. The test is false, so `return True` is skipped and the function ends without reaching a `return`. Python then hands back `None`. `None` is falsy, but it is not `False`, and a check that expects `False` fails.
            - [ ] `False` :: Nothing in this function says `False`. A function that ends without reaching a `return` hands back `None`.
            - [ ] It stops with an error :: Ending without a `return` is not an error. Python quietly hands back `None`.
            ```

            **Watch out:** decide for each end of the range whether the limit itself counts. A group of
            status codes starts at a round number that belongs to it, and it ends just before the next
            round number.

            **In short:** `low <= status < high` is `True` for the codes of one group, and a function
            can return that comparison directly.
        ''',
        "prompt": r'''
            Every response from an API carries a status code. The codes from 200 to 299 mean that the
            request worked. Every other code means that it did not, for example `429` (too many
            requests) or `500` (the server failed). Your app asks this question before it reads the body
            of a response.

            **Your job:** write `is_success(status)` so that it says whether the request worked.

            **What goes in**
            - `status`: the status code, a whole number, for example `200`

            **What comes out**
            - a bool: `True` when `status` is one of the codes from 200 to 299, and `False` for every
              other code

            **Rules**
            - Both ends count: `200` and `299` give `True`.
            - Their neighbours do not: `199` and `300` give `False`.
            - The result is the real `True` or `False`. A result of `None`, `1` or `0` does not pass
              the checks.

            **Examples**
            ```python
            is_success(200)   # returns True
            is_success(299)   # returns True
            is_success(300)   # returns False
            is_success(429)   # returns False
            ```
        ''',
        "starter": r'''
            def is_success(status):
                ...
        ''',
        "tests": r'''
            from solution import is_success

            def test_200_to_299_return_true():
                for status in (200, 201, 204, 299):
                    assert is_success(status) is True, f"{status} is a success"

            def test_codes_outside_2xx_return_false():
                for status in (199, 300, 400, 401, 404, 429, 500, 503):
                    assert is_success(status) is False, f"{status} is not a success"
        ''',
        "solution": r'''
            def is_success(status):
                return 200 <= status < 300
        ''',
        "hints": [
            "A comparison already produces `True` or `False`. The functions in the lesson hand one straight back, without an `if`.",
            "One chained comparison can say that the status lies in the group of success codes. Decide for each end whether the limit itself belongs to the group.",
            "Write a single `return` line with `status` in the middle of two limits. The lower limit is the first success code, and it counts. The upper end has to let 299 in and keep 300 out.",
        ],
    },
    {
        "id": "api-data-1",
        "hints": [
            "The lesson takes a path apart: one lookup per line, each with a fallback. This path has the same stops as the one in the lesson: a list, its first item, a dict inside that item, and a string inside that dict.",
            "Work from the outside in. After each lookup, make sure that you hold the kind of value the next lookup needs: a list before you take its first item, a dict before you read a key from it. An empty list has no first item, so that case has to leave the function early.",
            "Read the choices so that a missing key and `None` both become an empty list. When that list is empty, hand back the empty string. Read the message from the first choice so that a missing key and `None` both become an empty dict. Read the content from that dict, and let `or` turn a missing or `None` content into the empty string.",
        ],
        "title": "Safe reply extraction",
        "difficulty": 1,
        "lesson": r'''
            ## A path that cannot break

            A search tool answers your app with a list of hits, the best one first. On a good day, the
            title of the best hit is four lookups away:

            ```python
            result = {"hits": [{"score": 0.91, "document": {"title": "Refund policy"}}]}
            print(result["hits"][0]["document"]["title"])
            # Refund policy
            ```

            That one line makes three promises. There is a `"hits"` key. The list under it is not empty.
            And the first hit has a `"document"` with a `"title"` in it. Real responses break every one
            of them: an error response has no `"hits"`, a search can find nothing, and a hit can arrive
            with `"document": null`.

            ```quiz
            The search finds nothing and answers `{"hits": []}`. What does `result["hits"][0]["document"]["title"]` do?
            - [x] It stops with `IndexError: list index out of range` :: Right. The key `"hits"` is there, so the first lookup works. The list is empty, so there is no item at index 0.
            - [ ] It stops with `KeyError: 'hits'` :: The key is there. What is stored under it is an empty list, and the trouble starts one lookup later.
            - [ ] It hands back an empty string :: Square brackets never make up a value. When a lookup cannot be done, they stop the program.
            ```

            ### One lookup per line

            The cure is to take the path apart. Do one lookup per line, and after each one make sure
            that you hold the kind of value the next lookup needs.

            ```python
            def top_title(result):
                hits = result.get("hits") or []
                if not hits:
                    return ""
                document = hits[0].get("document") or {}
                return document.get("title") or ""

            print(top_title({"hits": [{"document": {"title": "Refund policy"}}]}))
            # Refund policy
            print(top_title({"error": "index is rebuilding"}) == "")
            # True
            ```

            - `result.get("hits") or []` is the normalising line from "Count the results". After it,
              `hits` is a list in every case.
            - `if not hits` is true for an empty list, because an empty list is falsy. The function
              leaves early, before `hits[0]` can stop it with an `IndexError`.
            - `hits[0].get("document") or {}` turns a missing or `None` document into an empty dict, so
              the next `.get` has a dict to work on.
            - The last line hands back the title, or `""` when it is missing or `None`.

            Code that checks each value before it uses it is called **defensive** code. Write it at the
            place where outside data enters your program. Everything after that place can trust the
            values.

            Put the lines in order. The finished program should print `nobody here`:

            ```order
            team = {"members": []}
            members = team.get("members") or []
            if not members:
                print("nobody here")
            else:
                print(members[0].get("name") or "no name")
            ---
            `members` has to exist before the `if` can test it. The empty list goes to the first branch, so `members[0]` is only reached when there is a first item. With the two `print` lines swapped, the program would stop with an `IndexError`.
            ```

            **Watch out:** `or []` saves you from `None`, but not from an empty list. `[][0]` still stops
            with `IndexError: list index out of range`. Test for the empty list before you take item 0.

            **In short:** do one lookup per line, give each one a fallback of the kind the next line
            needs, and leave early when a list is empty.
        ''',
        "prompt": r'''
            A chat API wraps the answer of the model in several layers. A complete response looks like
            this:

            ```python
            {"choices": [{"message": {"role": "assistant", "content": "Hi"}}]}
            ```

            The text you want is the `"content"` of the `"message"` of the first item in `"choices"`.
            But responses are not always complete. An error response has no `"choices"` at all. The list
            of choices can be empty. And when the model has no text to give, `"content"` holds `None`.

            **Your job:** write `get_reply(response)` so that it gives back the text of the reply, or an
            empty string when there is no text to give back.

            **What goes in**
            - `response`: a dict. When it is complete, it has the shape shown above.

            **What comes out**
            - a string: the `"content"` of the `"message"` of the first choice, `"Hi"` for the response
              above
            - the empty string `""` whenever a part of that path is not there

            **Rules**
            - Only the first choice counts. Any other choices are ignored.
            - When `"choices"` is missing, is `None` or is an empty list, the result is `""`.
            - When the first choice has no `"message"` key, or `"message"` holds `None`, the result is
              `""`.
            - When `"content"` is missing or holds `None`, the result is `""`.
            - The function never stops with an error for any of these responses.

            **Examples**
            ```python
            get_reply({"choices": [{"message": {"role": "assistant", "content": "Hi"}},
                                   {"message": {"role": "assistant", "content": "Other"}}]})  # returns "Hi"
            get_reply({"choices": []})                                  # returns ""
            get_reply({"error": {"message": "rate limited"}})           # returns ""
            get_reply({"choices": [{"message": None}]})                 # returns ""
            get_reply({"choices": [{"message": {"content": None}}]})    # returns ""
            ```
        ''',
        "starter": r'''
            def get_reply(response):
                ...
        ''',
        "tests": r'''
            from solution import get_reply

            def test_returns_content_of_first_choice():
                r = {"id": "x", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hi"}},
                                            {"index": 1, "message": {"role": "assistant", "content": "Other"}}]}
                assert get_reply(r) == "Hi", f"got {get_reply(r)!r}"

            def test_empty_missing_or_none_choices_return_empty_string():
                for r in ({"choices": []}, {}, {"choices": None}, {"error": {"message": "rate limited"}}):
                    got = get_reply(r)
                    assert got == "", f"get_reply({r!r}) returned {got!r}"

            def test_missing_or_none_message_returns_empty_string():
                for r in ({"choices": [{}]}, {"choices": [{"message": None}]}):
                    got = get_reply(r)
                    assert got == "", f"get_reply({r!r}) returned {got!r}"

            def test_none_content_from_tool_call_returns_empty_string():
                r = {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": []}}]}
                got = get_reply(r)
                assert got == "", f"got {got!r}"
        ''',
        "solution": r'''
            def get_reply(response):
                choices = response.get("choices") or []
                if not choices:
                    return ""
                message = choices[0].get("message") or {}
                return message.get("content") or ""
        ''',
    },
    {
        "id": "api-data-2",
        "hints": [
            "The lesson adds up one count per log entry. Here you add up two counts per response, and both of them sit one level deeper, inside `\"usage\"`.",
            "Keep two running totals, one for each kind of count, and go through the responses once. For each response, first make sure that you hold a dict for its usage. Then add its two counts, where a count that is missing or `None` adds 0.",
            "Start both totals at 0 before the loop. In the loop, read the usage so that a missing key and `None` both become an empty dict. Add the prompt count to one total and the completion count to the other, each with a fallback of 0. After the loop, build the result dict with its three keys. The third value is the sum of your two totals.",
        ],
        "title": "Total token usage",
        "difficulty": 1,
        "lesson": r'''
            ## Adding up numbers that are not always there

            Your app keeps a log of every job it ran, and each entry says how often the job had to be
            tried again. At the end of the day you want the total. Some entries are incomplete: the
            count is `None`, or the key is missing.

            You know the accumulator from the Loops chapter: start a total at 0 and add to it in a loop.
            The only new part is the fallback inside the loop.

            ```python
            runs = [{"retries": 2}, {"retries": None}, {}, {"retries": 1}]
            total = 0
            for run in runs:
                total += run.get("retries") or 0
            print(total)
            # 3
            ```

            For the second and the third entry, `run.get("retries")` hands back `None`. Without the
            fallback, `total += None` would stop the program with
            `TypeError: unsupported operand type(s) for +=: 'int' and 'NoneType'`. `or 0` turns that
            `None` into `0`, and adding 0 changes nothing.

            Press Next and watch `total` in the rounds where the count is `None` or missing:

            ```diagram
            {"type": "trace", "title": "Adding counts that can be None or missing", "code": ["runs = [{\"retries\": 2}, {\"retries\": None}, {}, {\"retries\": 1}]", "total = 0", "for run in runs:", "    total += run.get(\"retries\") or 0", "print(total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]"}, "out": ""},
              {"line": 3, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "0"}, "out": ""},
              {"line": 4, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "0", "run": "{'retries': 2}"}, "out": ""},
              {"line": 3, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "2", "run": "{'retries': 2}"}, "out": ""},
              {"line": 4, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "2", "run": "{'retries': None}"}, "out": ""},
              {"line": 3, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "2", "run": "{'retries': None}"}, "out": ""},
              {"line": 4, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "2", "run": "{}"}, "out": ""},
              {"line": 3, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "2", "run": "{}"}, "out": ""},
              {"line": 4, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "2", "run": "{'retries': 1}"}, "out": ""},
              {"line": 3, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "3", "run": "{'retries': 1}"}, "out": ""},
              {"line": 5, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "3", "run": "{'retries': 1}"}, "out": ""},
              {"line": null, "vars": {"runs": "[{'retries': 2}, {'retries': None}, {}, {'retries': 1}]", "total": "3", "run": "{'retries': 1}"}, "out": "3\n"}
            ]}
            ```

            ### When the numbers sit one level deeper

            Often the count is not directly in the entry. It sits in a nested dict, and that dict can be
            `None` or missing as well. Then you need two safe steps: first get a dict, then get the
            number out of it. Pick the line that makes this program print `900`:

            ```fill
            jobs = [{"timing": {"run_ms": 900}}, {"timing": None}, {}]
            total = 0
            for job in jobs:
                timing = ___
                total += timing.get("run_ms") or 0
            print(total)
            ---
            - [x] job.get("timing") or {} :: Right. A missing or `None` timing becomes an empty dict. `.get` on an empty dict hands back `None`, and `or 0` turns that into 0.
            - [ ] job.get("timing") :: For the second job this is `None`, and `None` has no `.get` method. The next line stops with `AttributeError: 'NoneType' object has no attribute 'get'`.
            - [ ] job.get("timing", {}) :: This covers the job that has no `"timing"` key. The second job has the key with `None` under it, so the fallback is not used and the next line stops with the same `AttributeError`.
            ```

            ### Do the sum yourself

            Many responses carry a ready-made total next to the separate counts. Do not build your sum
            on it.

            ```quiz
            Two responses report `{"in": 10, "out": 5, "total": 15}` and `{"in": 3, "out": 4}`. You add up `usage.get("total") or 0` for both. What do you get?
            - [x] `15` :: Right, and it is 7 too low. The second response has no ready-made total, so it adds 0, although it used 3 + 4 tokens. Adding `"in"` and `"out"` yourself gives the true 22.
            - [ ] `22` :: That is the true number, but you only get it when you add the `"in"` and `"out"` counts yourself. The second response has no `"total"` to read.
            - [ ] A `TypeError` :: `or 0` turns the missing total into 0, so nothing stops the program. That is what makes this bug easy to miss.
            ```

            **Watch out:** a fallback hides a missing number, it does not find it. `or 0` is right for a
            count that really is absent. It is wrong for a number that you could have worked out from
            other fields.

            **In short:** start a total at 0, add `d.get(key) or 0` in a loop, and work out a grand
            total from the parts yourself.
        ''',
        "prompt": r'''
            You pay for a model by the token. A token is a small piece of text, such as a word or a part
            of a word. Every response reports its own counts in a `"usage"` dict: `"prompt_tokens"` for
            the text you sent, and `"completion_tokens"` for the text the model wrote. For the bill at
            the end of the day, you add up the counts of all the calls.

            **Your job:** write `total_usage(responses)` so that it gives back the totals for a list of
            responses.

            **What goes in**
            - `responses`: a list of response dicts, for example
              `[{"usage": {"prompt_tokens": 10, "completion_tokens": 5}}, {"usage": None}]`. The list
              may be empty.

            **What comes out**
            - a dict with exactly three keys, each with a whole number:
              `{"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}` for the example value

            **Rules**
            - `"prompt_tokens"` is the sum of the prompt counts of all the responses.
              `"completion_tokens"` is the sum of the completion counts.
            - `"total_tokens"` is your own sum of those two results. A usage dict may carry a
              `"total_tokens"` of its own. Ignore it, because it can be missing or wrong.
            - A response with no `"usage"` key, or with `None` under it, adds nothing.
            - A count that is missing from a usage dict, or that is `None`, adds nothing.
            - An empty list gives `0` for all three keys.

            **Examples**
            ```python
            total_usage([{"usage": {"prompt_tokens": 10, "completion_tokens": 5}},
                         {"usage": None},
                         {"usage": {"prompt_tokens": 3}}])
            # returns {"prompt_tokens": 13, "completion_tokens": 5, "total_tokens": 18}
            total_usage([{"id": "a"}, {"usage": {"completion_tokens": 7, "total_tokens": 999}}])
            # returns {"prompt_tokens": 0, "completion_tokens": 7, "total_tokens": 7}
            total_usage([])
            # returns {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            ```
        ''',
        "starter": r'''
            def total_usage(responses):
                ...
        ''',
        "tests": r'''
            from solution import total_usage

            def test_sums_usage_and_skips_none_usage():
                got = total_usage([{"usage": {"prompt_tokens": 10, "completion_tokens": 5}},
                                   {"usage": None},
                                   {"usage": {"prompt_tokens": 3}}])
                assert got == {"prompt_tokens": 13, "completion_tokens": 5, "total_tokens": 18}, f"got {got!r}"

            def test_empty_list_gives_all_zeros():
                got = total_usage([])
                assert got == {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, f"got {got!r}"

            def test_missing_usage_counts_zero_and_total_is_computed():
                got = total_usage([{"id": "a"}, {"usage": {"completion_tokens": 7, "total_tokens": 999}}])
                assert got == {"prompt_tokens": 0, "completion_tokens": 7, "total_tokens": 7}, \
                    f"got {got!r} - compute total_tokens yourself"

            def test_none_counts_count_as_zero():
                got = total_usage([{"usage": {"prompt_tokens": None, "completion_tokens": 2}}])
                assert got["prompt_tokens"] == 0 and got["total_tokens"] == 2, f"got {got!r}"
        ''',
        "solution": r'''
            def total_usage(responses):
                prompt = completion = 0
                for response in responses:
                    usage = response.get("usage") or {}
                    prompt += usage.get("prompt_tokens") or 0
                    completion += usage.get("completion_tokens") or 0
                return {"prompt_tokens": prompt, "completion_tokens": completion,
                        "total_tokens": prompt + completion}
        ''',
    },
    {
        "id": "api-data-7",
        "title": "Should we retry?",
        "difficulty": 1,
        "lesson": r'''
            ## What to do after a failed request

            A call to a model has failed. Should your code send it again? Sometimes that is exactly the
            right thing. Sometimes it only wastes time, because the same request will fail the same way
            a hundred times. The status code tells you which case you are in:

            - `429`: you sent too many requests in a short time. Wait a little, and the same request
              goes through.
            - `5xx`: the server had a problem. Such problems often pass within seconds, so the same
              request can work a moment later.
            - Every other `4xx`: the request itself is wrong. The API key is bad (`401`), the server
              cannot read what you sent (`400`), or the model you named does not exist (`404`). Nothing
              changes until you change the request.

            A failure that can go away by itself is called **transient**. A failure that stays until you
            change something is called **permanent**.

            ```match
            `200` :: nothing to do, because the request worked
            `401` :: fix the request, because the API key is wrong
            `429` :: wait and send it again, because you were too fast
            `503` :: wait and send it again, because the server is overloaded
            ```

            ### A special code inside a range

            Here is the trap. `429` begins with a 4, so it lies inside the `4xx` range, and yet it needs
            the opposite answer from the rest of that range. A function runs its tests from top to
            bottom and leaves at the first one that is true. So a special code has to be tested before
            the range that contains it. This example does it right for another special code, `404`:

            ```python
            def advice(code):
                if code == 404:
                    return "check the address"
                if 400 <= code <= 499:
                    return "check the request"
                return "nothing to check"

            print(advice(404), "|", advice(400), "|", advice(200))
            # check the address | check the request | nothing to check
            ```

            Now the same function with its first two tests in the other order:

            ```predict
            def advice(code):
                if 400 <= code <= 499:
                    return "check the request"
                if code == 404:
                    return "check the address"
                return "nothing to check"

            print(advice(404))
            print(advice(200))
            ---
            `404` lies between 400 and 499, so the first test is already true and the function hands back `check the request`. The test for `404` is never reached. Nothing warns you about it: the special code quietly gets the general answer.
            ```

            Two tests can also share one answer. Join them with `or`, and write each side as a complete
            comparison:

            ```quiz
            A function should hand back `"check your key"` for `401` and for `403`. Which test is true for exactly those two codes?
            - [x] `code == 401 or code == 403` :: Right. Each side is a complete comparison, and `or` is true when at least one of them is.
            - [ ] `code == 401 or 403` :: Python reads this as `(code == 401) or 403`. The number `403` is not zero, so it is truthy, and the test is true for every code.
            - [ ] `code == 401 and code == 403` :: No code is equal to both numbers at once, so this test is never true.
            ```

            **Watch out:** the order of the tests is part of the logic. A test for one special code goes
            above the test for the range that contains it.

            **In short:** send the request again after `429` and `5xx`, fix it after every other `4xx`,
            and test a special code before its range.
        ''',
        "prompt": r'''
            When a call to a model fails, your app has to decide what to do next. Some failures pass by
            themselves, so the same request can be sent again after a short wait. Others stay until the
            request is changed. The status code says which kind you have.

            **Your job:** write `classify_status(status)` so that it gives back a short label that says
            what to do.

            **What goes in**
            - `status`: the status code, a whole number, for example `429`

            **What comes out**
            - one of the strings `"ok"`, `"retry"`, `"fix request"` and `"unknown"`

            **Rules**

            | `status` | label |
            | --- | --- |
            | 200 to 299 | `"ok"` |
            | `429` | `"retry"` |
            | 500 to 599 | `"retry"` |
            | every other code from 400 to 499 | `"fix request"` |
            | anything else, such as `100`, `302` or `600` | `"unknown"` |

            - Every range includes both of its ends: `200`, `299`, `400`, `499`, `500` and `599` belong
              to their range.

            **Examples**
            ```python
            classify_status(200)   # returns "ok"
            classify_status(429)   # returns "retry"
            classify_status(503)   # returns "retry"
            classify_status(401)   # returns "fix request"
            classify_status(302)   # returns "unknown"
            ```
        ''',
        "starter": r'''
            def classify_status(status):
                ...
        ''',
        "tests": r'''
            from solution import classify_status

            def test_2xx_is_ok():
                for status in (200, 201, 299):
                    assert classify_status(status) == "ok", f"{status}: got {classify_status(status)!r}"

            def test_429_and_5xx_are_retry():
                for status in (429, 500, 502, 503, 599):
                    assert classify_status(status) == "retry", f"{status}: got {classify_status(status)!r}"

            def test_other_4xx_is_fix_request():
                for status in (400, 401, 403, 404, 422, 499):
                    assert classify_status(status) == "fix request", f"{status}: got {classify_status(status)!r}"

            def test_other_codes_are_unknown():
                for status in (100, 199, 302, 399, 600):
                    assert classify_status(status) == "unknown", f"{status}: got {classify_status(status)!r}"
        ''',
        "solution": r'''
            def classify_status(status):
                if 200 <= status <= 299:
                    return "ok"
                if status == 429 or 500 <= status <= 599:
                    return "retry"
                if 400 <= status <= 499:
                    return "fix request"
                return "unknown"
        ''',
        "hints": [
            "Each row of the table becomes a test that hands back a label. The predict box in the lesson shows what goes wrong when a special code is tested after the range it lies in.",
            "Test the ranges with chained comparisons, and hand back the label as soon as a test is true. `429` lies inside the range from 400 to 499, so it has to be dealt with before that range is.",
            "Write the tests in this order: the success range first, then `429` together with the server range (two tests that share a label can be joined with `or`), then the range from 400 to 499. A last line, below all the tests, hands back the label for everything else.",
        ],
    },
    {
        "id": "api-data-8",
        "title": "Raise an API error",
        "difficulty": 1,
        "lesson": r'''
            ## An exception that carries the status code

            A request to a model fails with status `429`. The function that sent it should not decide
            what happens next. The code that called that function should: wait and ask again after a
            `429`, give up after a `401`. So the failure has to reach that code together with its status
            code. A message such as `"slow down"` is not enough, because the caller would have to search
            the words of the message for a number. It is cleaner when the exception carries the number
            as a value of its own.

            You can build that. An exception is an object, and the Classes chapter showed that an object
            can hold values called attributes. Give your exception class an `__init__` that stores one:

            ```python
            class DiskFullError(Exception):
                def __init__(self, free_mb, reason):
                    super().__init__(reason)
                    self.free_mb = free_mb

            err = DiskFullError(3, "only 3 MB left")
            print(err)
            # only 3 MB left
            print(err.free_mb)
            # 3
            ```

            Three things happen:

            - `__init__` receives the two values written in the parentheses of `DiskFullError(...)`.
            - `super().__init__(reason)` hands the message to `Exception`, the parent class. That is why
              `print(err)` shows it.
            - `self.free_mb = free_mb` stores the number on the object. Anyone who catches the exception
              can read it as `err.free_mb`.

            Real client libraries work this way too: their errors carry the status code of the failed
            request.

            Fill in the line that stores the value:

            ```fill
            class SlowDownError(Exception):
                def __init__(self, wait, text):
                    super().__init__(text)
                    ___

            err = SlowDownError(30, "too many requests")
            print(err.wait)
            ---
            - [x] self.wait = wait :: Right. The value is stored on the object, so `err.wait` can read it.
            - [ ] wait = wait :: This gives the local name `wait` a value it already has. Nothing is stored on the object, so `err.wait` stops with `AttributeError: 'SlowDownError' object has no attribute 'wait'`.
            - [ ] self.text = text :: This stores the message under another name. There is still no `wait` on the object, so `err.wait` stops with an `AttributeError`.
            ```

            ### Both values must go to the right place

            The message and the extra value travel separately. Here the class forgets the `super()` line:

            ```quiz
            What does `print(err)` show for `err = DiskFullError(3, "only 3 MB left")`?

            ~~~python
            class DiskFullError(Exception):
                def __init__(self, free_mb, reason):
                    self.free_mb = free_mb
            ~~~
            - [x] `(3, 'only 3 MB left')` :: Right. The message never reached `Exception`, so Python shows every value that was passed in, as a tuple in parentheses.
            - [ ] `only 3 MB left` :: That needs the `super()` line. Without it, `Exception` does not know which of the two values is the message.
            - [ ] An `AttributeError` :: `print` works on every exception. The error would come from reading an attribute that was never stored, which is not the case here.
            ```

            Now the caller can use the number. Work out which message each round prints:

            ```predict
            class PauseError(Exception):
                def __init__(self, seconds):
                    super().__init__(f"server asks for {seconds} seconds")
                    self.seconds = seconds

            for seconds in (5, 90):
                try:
                    raise PauseError(seconds)
                except PauseError as err:
                    if err.seconds > 30:
                        print("give up:", err)
                    else:
                        print("wait:", err)
            ---
            In the first round `err.seconds` is 5, which is not above 30, so the `else` branch prints `wait:` and the message built by `__init__`. In the second round it is 90, so the `if` branch prints `give up:`. The decision used the number, not the words of the message.
            ```

            **Watch out:** creating the exception is not raising it. `DiskFullError(3, "full")` on a line
            by itself builds the object and throws it away. No error message appears, and the function
            carries on as if nothing had gone wrong. Put `raise` in front of it.

            **In short:** a custom exception stores extra values as attributes in `__init__`, and a call
            to the parent's `__init__` with the message keeps the message working.
        ''',
        "prompt": r'''
            A request to an API can fail, and the code that sent it often has to react in different ways: wait and try again after a `429`, give up after a `401`. For that, the failure should reach it as an exception that carries the status code as a number.

            **Your job:** write two things. A class `APIError`, which is a kind of `Exception` that holds a status code. And a function `check_response(status, body)` that hands the body back when the request worked, and raises an `APIError` when it did not.

            **What goes in**
            - `APIError(status, message)`: `status` is the status code, a whole number such as `429`. `message` is a text such as `"slow down"`.
            - `check_response(status, body)`: `status` is the status code of a response. `body` is the decoded JSON body of that response, a dict such as `{"error": {"message": "slow down"}}`.

            **What comes out**
            - An `APIError` object has an attribute `.status` with the number that was passed in, and `str(error)` gives the message that was passed in.
            - `check_response` gives back `body` itself when the request worked. When it did not, it raises an `APIError`.

            **Rules**
            - A status from 200 to 299 means the request worked. Both ends count. The function hands back the very same dict that it was given, unchanged.
            - Any other status raises an `APIError` whose `.status` is that status.
            - The message of the error is the text that the body keeps under `"error"` and then under `"message"`, when it is there.
            - When it is not there, the message is `"HTTP "` followed by the status number, for example `"HTTP 503"`. "Not there" covers all of these: the body has no `"error"` key, `"error"` holds `None`, the `"error"` dict has no `"message"` key, and the message is the empty string.

            **Examples**
            ```python
            check_response(200, {"ok": True})                          # returns {"ok": True}
            check_response(429, {"error": {"message": "slow down"}})   # raises APIError: .status is 429, str() is "slow down"
            check_response(503, {})                                    # raises APIError: .status is 503, str() is "HTTP 503"
            check_response(500, {"error": None})                       # raises APIError: .status is 500, str() is "HTTP 500"
            ```
        ''',
        "starter": r'''
            class APIError(Exception):
                ...


            def check_response(status, body):
                ...
        ''',
        "tests": r'''
            from solution import APIError, check_response

            def catch(status, body):
                try:
                    check_response(status, body)
                except APIError as err:
                    return err
                return None

            def test_success_returns_body_unchanged():
                body = {"ok": True}
                assert check_response(200, body) is body
                assert check_response(204, {}) == {}

            def test_api_error_is_an_exception_with_status():
                err = APIError(418, "teapot")
                assert isinstance(err, Exception), "APIError must inherit from Exception"
                assert err.status == 418, f"status was {getattr(err, 'status', None)!r}"
                assert str(err) == "teapot", f"str(err) was {str(err)!r}"

            def test_error_message_taken_from_body():
                err = catch(429, {"error": {"message": "slow down"}})
                assert err is not None, "a 429 should raise APIError"
                assert err.status == 429 and str(err) == "slow down", f"got status {err.status!r}, message {str(err)!r}"

            def test_missing_message_falls_back_to_http_status():
                for body in ({}, {"error": None}, {"error": {}}, {"error": {"message": ""}}):
                    err = catch(503, body)
                    assert err is not None, f"503 with {body!r} should raise APIError"
                    assert str(err) == "HTTP 503", f"body {body!r}: message was {str(err)!r}"
        ''',
        "solution": r'''
            class APIError(Exception):
                def __init__(self, status, message):
                    super().__init__(message)
                    self.status = status


            def check_response(status, body):
                if 200 <= status <= 299:
                    return body
                error = body.get("error") or {}
                message = error.get("message") or f"HTTP {status}"
                raise APIError(status, message)
        ''',
        "hints": [
            "Look again at the class in the lesson. Which line sends the message to `Exception`, and which line keeps the number? Your class needs one of each, with the names `status` and `message`.",
            "Do the class first, then the function. In the function, handle the success range first and hand the body back at once. For a failure, find the message with one lookup per line, the way the \"Safe reply extraction\" step did: after each lookup, make sure you hold a dict before you read from it. Then raise.",
            "In the class: pass the message to the parent class, then store the status on the object. In the function: if the status is in the success range, hand back the body. Otherwise read the `\"error\"` part of the body so that a missing key and `None` both give an empty dict. Read the `\"message\"` from that dict, so that a missing key and an empty string both give the text \"HTTP\" followed by the status, written as an f-string. Raise an `APIError` with the status and that message.",
        ],
    },
    {
        "id": "api-data-9",
        "title": "Decode tool arguments",
        "difficulty": 1,
        "lesson": r'''
            ## Turning the model's arguments into a dict

            You give a model a function that it may use, for example one that looks up the weather. The
            model never runs it. It answers with a request: "call `get_weather` with these values". Your
            code then runs the function. The request arrives as a dict, and the values for the function
            are inside it:

            ```python
            call = {"name": "get_weather", "arguments": '{"city": "Paris", "days": 3}'}
            print(call["arguments"]["city"])
            ```

            This stops with `TypeError: string indices must be integers, not 'str'`. Look at the quote
            marks around the value of `"arguments"`. It is not a dict. It is text that looks like one,
            because the model writes its arguments in JSON format. Such a value is a **JSON string**.
            Programmers call a function that a model may ask for a **tool**, and the request a **tool call**.

            You know the cure from the JSON chapter: `json.loads` turns the text into real Python data.

            ```python
            import json

            call = {"name": "get_weather", "arguments": '{"city": "Paris", "days": 3}'}
            args = json.loads(call["arguments"])
            print(args["city"], args["days"] + 1)
            # Paris 4
            ```

            ```quiz
            Which expression reads the city out of `call`?
            - [x] `json.loads(call["arguments"])["city"]` :: Right. `call["arguments"]` is the text, `json.loads` turns it into a dict, and `["city"]` reads from that dict.
            - [ ] `call["arguments"]["city"]` :: The value is a string, not a dict, so this stops with `TypeError: string indices must be integers, not 'str'`.
            - [ ] `json.loads(call)["arguments"]` :: `json.loads` needs text, and `call` is a dict, so this stops with `TypeError: the JSON object must be str, bytes or bytearray, not dict`.
            ```

            ### Text that the model got wrong

            The model writes that text itself, and sometimes it breaks off in the middle. Then `json.loads`
            raises `json.JSONDecodeError`, which is a kind of `ValueError`. (This step's research links
            show where the Python docs say so.) Both `except ValueError` and `except json.JSONDecodeError`
            catch it.

            The code that calls your function should not have to know about JSON. So catch the decoding
            error inside your function and raise a `ValueError` of your own, with a message that names
            what was wrong. The words `from problem` at the end keep the original error attached, so that a
            traceback shows both.

            ```try
            import json

            def read_options(text, label):
                return json.loads(text)

            try:
                read_options('{"size": ', "resize")
            except ValueError as err:
                print(err)
            ---
            The program prints the message of the decoding error. Change `read_options` so that the program prints `unreadable options for resize` instead.
            ---
            import json

            def read_options(text, label):
                try:
                    return json.loads(text)
                except json.JSONDecodeError as problem:
                    raise ValueError(f"unreadable options for {label}") from problem

            try:
                read_options('{"size": ', "resize")
            except ValueError as err:
                print(err)
            ---
            The `try` inside the function catches the decoding error. The function then raises its own `ValueError`, and the message uses `label` so that the caller can see which options were bad.
            ```

            ### Valid, but not a dict

            Arguments are named values, so they have to decode to a dict. But `json.loads` accepts any
            valid JSON, and not every JSON text describes a dict:

            ```python
            import json

            for text in ('{"n": 2}', "[1, 2]", "5"):
                value = json.loads(text)
                print(type(value).__name__, isinstance(value, dict))
            # dict True
            # list False
            # int False
            ```

            `isinstance(value, dict)` is `True` when `value` is a dict. When it is not, the arguments are
            no use to a tool, and your function should raise the same kind of `ValueError`.

            ```predict
            import json

            for text in ('{}', '"hi"', '[]', '{"a": [1]}'):
                print(isinstance(json.loads(text), dict))
            ---
            `{}` and `{"a": [1]}` are JSON objects, so they decode to dicts, and the dict that holds a list is still a dict. `"hi"` decodes to a string and `[]` to an empty list, so those two give `False`.
            ```

            **Watch out:** deal with empty arguments before you call `json.loads`. A tool that needs no
            input may send `""`, `None`, or no `"arguments"` key at all. `json.loads("")` raises a
            `JSONDecodeError`, and `json.loads(None)` raises `TypeError: the JSON object must be str,
            bytes or bytearray, not NoneType`. `except ValueError` does not catch that `TypeError`.

            **In short:** decode the text with `json.loads`, turn a decoding error and a result that is
            not a dict into your own `ValueError`, and settle empty arguments first.
        ''',
        "research": {
            "note": "Read what `json.loads` raises for invalid text, and how `json.JSONDecodeError` relates to `ValueError`, then come back.",
            "links": [
                {"title": "json.loads - Python docs", "url": "https://docs.python.org/3/library/json.html#json.loads"},
                {"title": "json.JSONDecodeError - Python docs", "url": "https://docs.python.org/3/library/json.html#json.JSONDecodeError"},
            ],
        },
        "prompt": r'''
            When a model asks for one of your tools, the request has the name of the tool and its arguments, and the arguments arrive as JSON text. Before your code can run the tool, it has to turn that text into a dict. It also has to refuse text that cannot be used, with an error that says which tool the problem belongs to.

            **Your job:** write `parse_arguments(call)` so that it gives back the arguments of a tool call as a dict, or raises a `ValueError` when they cannot be used.

            **What goes in**
            - `call`: a dict with the tool's `"name"` and its `"arguments"`, for example `{"name": "get_weather", "arguments": '{"city": "Paris"}'}`. The value of `"arguments"` is text in JSON format. The `"arguments"` key may also be missing, or hold `None` or `""`.

            **What comes out**
            - a dict: the decoded arguments, `{"city": "Paris"}` for the example value

            **Rules**
            - When `"arguments"` is missing, holds `None` or is the empty string `""`, the tool gets no arguments. The result is an empty dict `{}`.
            - When the text is not valid JSON, the function raises a `ValueError`. Its message is exactly `bad arguments for` followed by a space and the name of the tool, for example `bad arguments for calc`.
            - When the text is valid JSON but does not describe a dict, such as `[1, 2]`, `5` or `"text"`, the function raises the same `ValueError` with the same message.

            **Examples**
            ```python
            parse_arguments({"name": "get_weather", "arguments": '{"city": "Paris"}'})   # returns {"city": "Paris"}
            parse_arguments({"name": "now", "arguments": ""})                           # returns {}
            parse_arguments({"name": "now"})                                            # returns {}
            parse_arguments({"name": "calc", "arguments": '{"x": '})                    # raises ValueError("bad arguments for calc")
            parse_arguments({"name": "calc", "arguments": "[1, 2]"})                    # raises ValueError("bad arguments for calc")
            ```
        ''',
        "starter": r'''
            import json


            def parse_arguments(call):
                ...
        ''',
        "tests": r'''
            from solution import parse_arguments

            def error_message(call):
                try:
                    parse_arguments(call)
                except ValueError as err:
                    return str(err)
                return None

            def test_decodes_json_arguments_to_dict():
                got = parse_arguments({"name": "get_weather", "arguments": '{"city": "Paris", "days": 2}'})
                assert got == {"city": "Paris", "days": 2}, f"got {got!r}"

            def test_missing_none_or_empty_arguments_give_empty_dict():
                for call in ({"name": "now"}, {"name": "now", "arguments": None}, {"name": "now", "arguments": ""}):
                    got = parse_arguments(call)
                    assert got == {}, f"{call!r}: got {got!r}"

            def test_invalid_json_raises_value_error_with_tool_name():
                msg = error_message({"name": "calc", "arguments": '{"x": '})
                assert msg == "bad arguments for calc", f"message was {msg!r}"

            def test_json_that_is_not_an_object_raises_value_error():
                for raw in ("[1, 2]", "5", '"text"'):
                    msg = error_message({"name": "calc", "arguments": raw})
                    assert msg == "bad arguments for calc", f"{raw!r}: message was {msg!r}"
        ''',
        "solution": r'''
            import json


            def parse_arguments(call):
                raw = call.get("arguments")
                if not raw:
                    return {}
                message = f"bad arguments for {call.get('name')}"
                try:
                    args = json.loads(raw)
                except json.JSONDecodeError as err:
                    raise ValueError(message) from err
                if not isinstance(args, dict):
                    raise ValueError(message)
                return args
        ''',
        "hints": [
            "Write down the cases in the task. Three kinds of input need three different answers. Which case has to be settled before you call `json.loads` at all? The Watch out in the lesson tells you why.",
            "Settle the empty cases first and give back the empty dict. Then decode the text inside a `try`, and turn a decoding error into your own `ValueError`. After decoding, check that you really hold a dict, and raise the same `ValueError` if you do not. Both errors use the same message, so build that message once.",
            "Read the arguments from the call with the method that does not stop for a missing key. If what you got is empty, hand back an empty dict. Build the message from the tool's name with an f-string. Decode inside a `try`, catching the decoding error and raising a `ValueError` with the message. After the `try`, if the result is not a dict, raise a `ValueError` with the same message. Otherwise hand back the result.",
        ],
    },
    {
        "id": "api-data-3",
        "hints": [
            "Ask yourself two questions. What must your function remember from one request to the next? And what tells it that the list is complete? One variable changes in every round, and the loop depends on it.",
            "Keep a list for the results and a variable for the cursor, which starts as \"no cursor yet\". Repeat: ask for the page with the current cursor, add its items, take the cursor for the next page, and stop when there is none. Let the loop run at most `max_pages` times, and think about what has to happen when it ends without having stopped early.",
            "Start with an empty list and a cursor of `None`. Use a `for` loop over `range` of `max_pages`. In each round, call `fetch_page` with the current cursor. Add the items of that page to the list, treating a missing or `None` `\"data\"` as an empty list. Read the next cursor with the method that gives `None` for a missing key. If there is no cursor, hand back the list at once. After the loop, which only ends when no round handed anything back, raise the `RuntimeError`.",
        ],
        "title": "Follow the cursor",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A server that holds thousands of items does not send them all in one reply. It sends them one page at a time. Every page holds a small batch of items and, unless it is the last page, a marker called the **cursor**. You send the cursor back to say "continue from here", and the server answers with the next page. The last page carries no cursor. To get every item, you ask again and again until a page comes back without one.

            **Your job:** write `fetch_all(fetch_page, max_pages=100)` so that it collects the items of all the pages into one list.

            **What goes in**
            - `fetch_page`: a function that asks the server for one page. You call it as `fetch_page(cursor)`, and it gives back the page, a dict such as `{"data": [1, 2], "next_cursor": "p2"}`. The items are the list under `"data"`. The cursor for the next page is under `"next_cursor"`. Your function never talks to a real server: whoever calls it hands in the function that does, so that it can be tested with made-up pages.
            - `max_pages`: the most pages you may ask for, a whole number such as `5`. It protects your program from a server that never stops sending cursors.

            **What comes out**
            - a list of the items of all the pages, in the order of the pages, `[1, 2, 3]` for the example pages below

            **Rules**
            - The first page is asked for with `None`, because you have no cursor yet: `fetch_page(None)`. Every later request passes the `"next_cursor"` of the page before it, for example `fetch_page("p2")`.
            - The list is complete when a page's `"next_cursor"` is `None`, or when the page has no `"next_cursor"` key at all.
            - A page may hold an empty list under `"data"`. It adds no items, and you carry on with its cursor. A page whose `"data"` is missing or `None` adds no items either.
            - Asking for exactly `max_pages` pages is fine when the last of them ends the list.
            - When the list has still not ended after `max_pages` pages, raise a `RuntimeError`. The text of the message is up to you. `fetch_page` must never be called more than `max_pages` times.

            **Examples**
            ```python
            # `pages` is a made-up server. The lambda is the function that asks it.
            pages = {None: {"data": [1, 2], "next_cursor": "p2"},
                     "p2": {"data": [], "next_cursor": "p3"},
                     "p3": {"data": [3], "next_cursor": None}}
            fetch_all(lambda cursor: pages[cursor])        # returns [1, 2, 3]
                                                           # (fetch_page was called with None, "p2", "p3")
            fetch_all(lambda cursor: {"data": ["a"]})      # returns ["a"], the page has no "next_cursor" key
            fetch_all(lambda cursor: {"data": [0], "next_cursor": "again"}, max_pages=5)
            # raises RuntimeError, after at most 5 calls
            ```
        ''',
        "starter": r'''
            def fetch_all(fetch_page, max_pages=100):
                ...
        ''',
        "tests": r'''
            from solution import fetch_all

            def make_api(pages):
                calls = []
                def fetch_page(cursor):
                    calls.append(cursor)
                    return pages[cursor]
                return fetch_page, calls

            def test_follows_cursors_across_pages_in_order():
                fetch, calls = make_api({None: {"data": [1, 2], "next_cursor": "p2"},
                                         "p2": {"data": [], "next_cursor": "p3"},
                                         "p3": {"data": [3], "next_cursor": None}})
                got = fetch_all(fetch)
                assert got == [1, 2, 3], f"got {got!r}"
                assert calls == [None, "p2", "p3"], f"fetch_page was called with {calls}"

            def test_missing_next_cursor_key_stops():
                fetch, calls = make_api({None: {"data": ["a"]}})
                assert fetch_all(fetch) == ["a"]
                assert calls == [None]

            def test_exactly_max_pages_is_allowed():
                pages = {None: {"data": [0], "next_cursor": "1"}, "1": {"data": [1], "next_cursor": None}}
                fetch, calls = make_api(pages)
                assert fetch_all(fetch, max_pages=2) == [0, 1]

            def test_endless_api_raises_runtime_error_within_max_pages_calls():
                calls = []
                def fetch_page(cursor):
                    calls.append(cursor)
                    return {"data": [len(calls)], "next_cursor": f"c{len(calls)}"}
                try:
                    fetch_all(fetch_page, max_pages=5)
                except RuntimeError:
                    assert len(calls) <= 5, f"fetch_page was called {len(calls)} times with max_pages=5"
                    return
                assert False, "an API that never ends should raise RuntimeError"

            def test_single_empty_page_returns_empty_list():
                fetch, _ = make_api({None: {"data": [], "next_cursor": None}})
                assert fetch_all(fetch) == []
        ''',
        "solution": r'''
            def fetch_all(fetch_page, max_pages=100):
                items = []
                cursor = None
                for _ in range(max_pages):
                    page = fetch_page(cursor)
                    items.extend(page.get("data") or [])
                    cursor = page.get("next_cursor")
                    if cursor is None:
                        return items
                raise RuntimeError(f"more than {max_pages} pages")
        ''',
    },
    {
        "id": "api-data-4",
        "hints": [
            "Read the rules as a list of checks. Each one is a condition that, when it is true, ends the function with a `ValueError`. Go through the arguments in the order of the function's first line.",
            "Check every argument before you build anything. Ask the built-in that tells whether a value has a given type, and remember that a bool needs its own check, because `True` counts as a whole number. Decide \"was this option given\" by asking whether it is `None`, not whether it is truthy, because `0` is a valid temperature. For the copies, look back at the Dicts chapter: each message needs its own copy, not only the list around them.",
            "First `model`: raise unless it is a text that is not empty. Then `messages`: raise unless it is a non-empty list, and check each item in a loop: a dict, with a role from the allowed four and a text as content. Start the payload with the model and a list of copies of the messages. Then take each option in turn. If it is not `None`, check its type, whether it is a bool, and its range (for `stop`, the length of the list and a check that every item is text, using `all`), raise if it fails, and add its key to the payload. Last, hand back the payload.",
        ],
        "title": "Validated request payload",
        "difficulty": 2,
        "prompt": r'''
            Before an app sends a request to a model API, it is wise to check the request on your own machine. Then a typo, such as an empty model name or a temperature of 5, stops at once with a clear message, instead of coming back from the server as a vague `HTTP 400`.

            **Your job:** write `build_payload(model, messages, *, temperature=None, max_tokens=None, stop=None)`. It checks its arguments and gives back the request body as a dict, or raises a `ValueError` when something is wrong. The `*` in the list means that `temperature`, `max_tokens` and `stop` must be passed by name, for example `temperature=0`.

            **What goes in**
            - `model`: the name of the model, text such as `"gpt-4o"`
            - `messages`: the conversation, a list of dicts such as `{"role": "user", "content": "Hi"}`
            - `temperature`: how adventurous the answer may be, a number from 0 to 2, or `None` when it is not given
            - `max_tokens`: the most tokens the model may write, a whole number, or `None`
            - `stop`: a text, or a list of texts, at which the model must stop writing, or `None`

            **What comes out**
            - a dict `{"model": ..., "messages": [...]}`, plus one more key for each option that was given: `"temperature"`, `"max_tokens"` and `"stop"`. An option counts as given whenever it is not `None`, so `temperature=0` is given, and its key is in the result.

            **Rules**

            Every failure raises a `ValueError`. The text of the message is up to you.
            - `model` must be a text that is not empty. `""` and `None` are errors.
            - `messages` must be a list that is not empty. Every item must be a dict. Its `"role"` must be one of `"system"`, `"user"`, `"assistant"` or `"tool"`, and its `"content"` must be a text. An item that is not a dict, a message without `"content"` and a content of `5` are all errors.
            - `temperature`, when given, is a whole number or a decimal number from 0 to 2, both ends included. `2` is fine. `2.5`, `-0.1` and `"0.5"` are errors.
            - `max_tokens`, when given, is a whole number of at least 1. `0` and `1.5` are errors.
            - `stop`, when given, is a text, or a list of at most 4 items that are all texts. `5`, `["a", 1]` and a list of 5 items are errors.
            - In Python, `True` and `False` count as whole numbers (the Data Types chapter showed this). Here they must not: `True` is an error for `temperature` and for `max_tokens`.
            - The messages in the result are copies. Changing the list `payload["messages"]`, or a dict inside it, must leave the caller's list and dicts as they were.

            **Examples**
            ```python
            msgs = [{"role": "user", "content": "Hi"}]
            build_payload("gpt-4o", msgs)
            # returns {"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}
            build_payload("m", msgs, temperature=0, max_tokens=256, stop="END")
            # returns {"model": "m", "messages": [...], "temperature": 0, "max_tokens": 256, "stop": "END"}
            build_payload("m", msgs, temperature=2.5)                    # raises ValueError
            build_payload("m", [{"role": "robot", "content": "x"}])     # raises ValueError
            ```
        ''',
        "starter": r'''
            def build_payload(model, messages, *, temperature=None, max_tokens=None, stop=None):
                ...
        ''',
        "tests": r'''
            from solution import build_payload

            MSGS = [{"role": "system", "content": "Be brief"}, {"role": "user", "content": "Hi"}]

            def raises(**kwargs):
                args = {"model": "m", "messages": MSGS, **kwargs}
                try:
                    build_payload(args.pop("model"), args.pop("messages"), **args)
                except ValueError:
                    return True
                return False

            def test_minimal_payload_has_model_and_messages_only():
                got = build_payload("gpt-4o", MSGS)
                assert got == {"model": "gpt-4o", "messages": MSGS}, f"got {got!r}"

            def test_optional_keys_added_only_when_given():
                got = build_payload("m", MSGS, temperature=0, max_tokens=256, stop="END")
                assert got == {"model": "m", "messages": MSGS, "temperature": 0, "max_tokens": 256, "stop": "END"}, f"got {got!r}"
                assert "temperature" not in build_payload("m", MSGS, max_tokens=5)

            def test_payload_messages_are_copies_of_callers():
                msgs = [{"role": "user", "content": "Hi"}]
                p = build_payload("m", msgs)
                p["messages"][0]["content"] = "changed"
                p["messages"].append({"role": "user", "content": "x"})
                assert msgs == [{"role": "user", "content": "Hi"}], f"caller's messages became {msgs!r}"

            def test_invalid_model_or_messages_raise_value_error():
                assert raises(model=""), "empty model"
                assert raises(model=None), "model None"
                assert raises(messages=[]), "empty messages"
                assert raises(messages=[{"role": "robot", "content": "x"}]), "bad role"
                assert raises(messages=[{"role": "user"}]), "missing content"
                assert raises(messages=[{"role": "user", "content": 5}]), "non-string content"
                assert raises(messages=["hi"]), "message not a dict"

            def test_invalid_temperature_or_max_tokens_raise_value_error():
                for kwargs in ({"temperature": 2.5}, {"temperature": -0.1}, {"temperature": True},
                               {"temperature": "0.5"}, {"max_tokens": 0}, {"max_tokens": 1.5},
                               {"max_tokens": True}):
                    assert raises(**kwargs), f"{kwargs} should raise ValueError"
                assert not raises(temperature=2), "temperature=2 is allowed"

            def test_invalid_stop_raises_value_error():
                assert raises(stop=["a", "b", "c", "d", "e"]), "more than 4 stop sequences"
                assert raises(stop=["a", 1]), "non-string stop"
                assert raises(stop=5), "stop must be str or list"
                assert build_payload("m", MSGS, stop=["a", "b"])["stop"] == ["a", "b"]
        ''',
        "solution": r'''
            ROLES = {"system", "user", "assistant", "tool"}


            def _is_number(x):
                return isinstance(x, (int, float)) and not isinstance(x, bool)


            def build_payload(model, messages, *, temperature=None, max_tokens=None, stop=None):
                if not isinstance(model, str) or not model:
                    raise ValueError("model must be a non-empty string")
                if not isinstance(messages, list) or not messages:
                    raise ValueError("messages must be a non-empty list")
                for i, msg in enumerate(messages):
                    if not isinstance(msg, dict):
                        raise ValueError(f"message {i} is not a dict")
                    if msg.get("role") not in ROLES:
                        raise ValueError(f"message {i} has invalid role {msg.get('role')!r}")
                    if not isinstance(msg.get("content"), str):
                        raise ValueError(f"message {i} content must be a string")

                payload = {"model": model, "messages": [dict(m) for m in messages]}

                if temperature is not None:
                    if not _is_number(temperature) or not 0 <= temperature <= 2:
                        raise ValueError("temperature must be a number between 0 and 2")
                    payload["temperature"] = temperature
                if max_tokens is not None:
                    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens < 1:
                        raise ValueError("max_tokens must be a positive int")
                    payload["max_tokens"] = max_tokens
                if stop is not None:
                    ok = isinstance(stop, str) or (
                        isinstance(stop, list) and len(stop) <= 4 and all(isinstance(s, str) for s in stop))
                    if not ok:
                        raise ValueError("stop must be a string or a list of up to 4 strings")
                    payload["stop"] = stop
                return payload
        ''',
    },
    {
        "id": "api-data-5",
        "research": {
            "note": "Real providers document which errors are worth retrying and how to back off. Skim one of these pages (rate limits / error codes) before you write the retry loop.",
            "links": [
                {"title": "Rate limits - OpenAI docs", "url": "https://platform.openai.com/docs/guides/rate-limits"},
                {"title": "Errors - Anthropic API docs", "url": "https://docs.anthropic.com/en/api/errors"},
            ],
        },
        "hints": [
            "Separate successful, retryable, and permanent outcomes before deciding whether to wait.",
            "Remember the last failure and combine the exponential wait with any valid server-requested delay.",
            "Define the status-carrying exception, attempt at most the limit, return on success, reject permanent errors immediately, wait only before another attempt, and report the final failure when exhausted.",
        ],
        "title": "Retry with backoff",
        "difficulty": 3,
        "prompt": r'''
            LLM APIs fail now and then: rate limits (429), overloaded servers (5xx), dropped
                   connections. A robust client retries those, waiting longer each time (this is called
                   *exponential backoff*), but gives up at once on errors that retrying can't fix.

                   **Your job:** define these two pieces:
                   1. An exception class `APIError(Exception)` created as `APIError(status, message)`,
                      whose objects have a `.status` attribute (an `int`, or `None`).
                   2. `call_with_retry(request, *, max_attempts=4, base_delay=1.0, sleep=time.sleep)`
                      - `request`: a function with no arguments; `request()` returns a tuple
                        `(status, body)`, e.g. `(200, {"ok": True})`, or raises `ConnectionError`
                      - `max_attempts`: an `int`, the most times `request` may be called
                      - `base_delay`: a `float`, the first wait in seconds
                      - `sleep`: the function to call to wait (`time.sleep(n)` pauses for `n` seconds; tests
            pass their own function to record the delays instead)

            **What comes out**
            - the `body` of the first successful response

                   **Rules**
                   - A status from 200 to 299 is a success: return its `body` right away.
                   - Status `429`, any status from 500 to 599, or a raised `ConnectionError` is
                     *retryable*: wait, then call `request` again.
                   - The wait before retry number `k` (counting from 0) is `base_delay * 2 ** k`, so with
                     the defaults `1.0`, `2.0`, `4.0`. Always wait by calling `sleep(seconds)`.
                   - For a `429` whose body is a dict with a numeric `"retry_after"` (an int or float, excluding booleans), wait
                     `max(retry_after, base_delay * 2 ** k)` instead. A 429 with any other body uses the normal wait.
                   - Any other status (e.g. 400, 401, 404): raise `APIError` with that status immediately
                     (no retry, no sleep).
                   - Call `request` at most `max_attempts` times, and never sleep after the last attempt.
                   - If every attempt fails, raise `APIError` whose `.status` is the last status, or
                     `None` if the last failure was a `ConnectionError`.

                   **Examples**
                   ```python
                   responses = iter([(503, None), (429, {"retry_after": 5}), (200, {"ok": True})])
                   delays = []
                   call_with_retry(lambda: next(responses), sleep=delays.append)   # returns {"ok": True}
                   delays                                                          # [1.0, 5]

                   # always 500, max_attempts=4, base_delay=0.5:
                   # 4 calls, delays [0.5, 1.0, 2.0], then raises APIError with .status == 500

                   # first response (401, {...}): raises APIError with .status == 401 after 1 call, no sleep
                   APIError(418, "teapot").status                                  # 418
                   ```
        ''',
        "starter": r'''
            import time


            class APIError(Exception):
                ...


            def call_with_retry(request, *, max_attempts=4, base_delay=1.0, sleep=time.sleep):
                ...
        ''',
        "tests": r'''
            from solution import APIError, call_with_retry

            def scripted(*outcomes):
                it = iter(outcomes)
                calls = []
                def request():
                    calls.append(1)
                    out = next(it)
                    if isinstance(out, Exception):
                        raise out
                    return out
                return request, calls

            def test_succeeds_after_retries_using_retry_after():
                req, calls = scripted((503, None), (429, {"retry_after": 5}), (200, {"ok": True}))
                delays = []
                got = call_with_retry(req, sleep=delays.append)
                assert got == {"ok": True}, f"got {got!r}"
                assert delays == [1.0, 5], f"slept {delays}"

            def test_exponential_delays_then_api_error_after_max_attempts():
                req, calls = scripted(*[(500, "err")] * 10)
                delays = []
                try:
                    call_with_retry(req, max_attempts=4, base_delay=0.5, sleep=delays.append)
                except APIError as e:
                    assert e.status == 500, f"status was {e.status!r}"
                    assert len(calls) == 4, f"request called {len(calls)} times"
                    assert delays == [0.5, 1.0, 2.0], f"slept {delays} (no sleep after the last attempt)"
                    return
                assert False, "should raise APIError after max_attempts"

            def test_client_error_raises_immediately_without_retry():
                req, calls = scripted((401, {"error": "bad key"}), (200, "never"))
                delays = []
                try:
                    call_with_retry(req, sleep=delays.append)
                except APIError as e:
                    assert e.status == 401 and len(calls) == 1 and delays == [], \
                        f"status={e.status}, calls={len(calls)}, delays={delays}"
                    return
                assert False, "401 should raise APIError"

            def test_connection_error_is_retried():
                req, calls = scripted(ConnectionError("reset"), (201, "created"))
                delays = []
                assert call_with_retry(req, sleep=delays.append) == "created"
                assert delays == [1.0], f"slept {delays}"

            def test_only_connection_errors_raise_api_error_with_status_none():
                req, calls = scripted(*[ConnectionError("down")] * 3)
                delays = []
                try:
                    call_with_retry(req, max_attempts=3, sleep=delays.append)
                except APIError as e:
                    assert e.status is None, f"status should be None, got {e.status!r}"
                    assert delays == [1.0, 2.0], f"slept {delays}"
                    return
                assert False, "should raise APIError"

            def test_retry_after_smaller_than_backoff_uses_backoff():
                req, calls = scripted((500, None), (429, {"retry_after": 0.5}), (429, "text body"), (200, 1))
                delays = []
                assert call_with_retry(req, sleep=delays.append) == 1
                assert delays == [1.0, 2.0, 4.0], f"slept {delays}"

            def test_api_error_is_an_exception_with_status():
                e = APIError(418, "teapot")
                assert isinstance(e, Exception) and e.status == 418
        ''',
        "solution": r'''
            import time


            class APIError(Exception):
                def __init__(self, status, message=""):
                    super().__init__(message)
                    self.status = status


            def _retryable(status):
                return status == 429 or 500 <= status < 600


            def call_with_retry(request, *, max_attempts=4, base_delay=1.0, sleep=time.sleep):
                last_status = None
                for attempt in range(max_attempts):
                    delay = base_delay * 2 ** attempt
                    try:
                        status, body = request()
                    except ConnectionError:
                        last_status = None
                    else:
                        if 200 <= status < 300:
                            return body
                        if not _retryable(status):
                            raise APIError(status, f"request failed with {status}")
                        last_status = status
                        if status == 429 and isinstance(body, dict):
                            retry_after = body.get("retry_after")
                            if isinstance(retry_after, (int, float)) and not isinstance(retry_after, bool):
                                delay = max(retry_after, delay)
                    if attempt < max_attempts - 1:
                        sleep(delay)
                raise APIError(last_status, f"gave up after {max_attempts} attempts")
        ''',
    },
    {
        "id": "api-data-6",
        "hints": [
            "The outer response and each call's arguments cross different data-shape boundaries.",
            "Normalize missing collections, then use one argument-decoding helper for both modern and legacy calls.",
            "Visit choices and calls in order, skip other call types, validate decoded arguments as dictionaries with identifying errors, and append the legacy representation with an absent id.",
        ],
        "title": "Extract tool calls",
        "difficulty": 3,
        "prompt": r'''
            When a model wants to use a tool, the response lists *tool calls* instead of (or as
            well as) text. Your agent must pull them out and decode their arguments before it can
            run the tools.

            **Your job:** write `extract_tool_calls(response)`

            **What goes in**
            - `response`: a chat-completion dict, `{"choices": [{"message": {...}}, ...]}`

            **What comes out**
            - a `list` of dicts `{"id": ..., "name": ..., "arguments": {...}}`, one per
              tool call, where `"arguments"` is a decoded `dict`

            **Rules**
            - Tool calls live in `choice["message"]["tool_calls"]`, a list of
              `{"id": str, "type": "function", "function": {"name": str, "arguments": str}}`.
              `arguments` is a **JSON string** (decode it with `json.loads`). The list may be
              missing or `None`.
            - Order: go through the choices in order, and within each message its calls in order.
            - Skip a tool call whose `"type"` is present and not `"function"`
              (e.g. `"code_interpreter"`).
            - Older responses have `choice["message"]["function_call"]` =
              `{"name": str, "arguments": str}` instead; it becomes one call with `"id": None`.
            - `arguments` that are `None`, `""` or only whitespace decode to `{}`.
            - Invalid JSON raises `ValueError` whose message contains the call's `id`
              (or the function name when there is no id, as for `function_call`).
            - Valid JSON that is not an object (e.g. `"[1, 2]"`) also raises `ValueError` with the
              id / function name in its message.
            - A missing or empty `choices`, a choice without `message`, or `"message": None` means
              no calls; with no calls anywhere, return `[]`.

            **Examples**
            ```python
            r = {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [
                    {"id": "call_1", "type": "function",
                     "function": {"name": "get_weather", "arguments": "{\"city\": \"Paris\"}"}}]}}]}
            extract_tool_calls(r)
            # returns [{"id": "call_1", "name": "get_weather", "arguments": {"city": "Paris"}}]

            legacy = {"choices": [{"message": {"content": None,
                        "function_call": {"name": "lookup", "arguments": "{\"id\": 7}"}}}]}
            extract_tool_calls(legacy)
            # returns [{"id": None, "name": "lookup", "arguments": {"id": 7}}]

            extract_tool_calls({"choices": [{"message": {"role": "assistant", "content": "Hi"}}]})
            # returns []
            # a call with id "call_bad" and arguments "{\"city\": " -> raises ValueError mentioning "call_bad"
            ```
        ''',
        "starter": r'''
            import json


            def extract_tool_calls(response):
                ...
        ''',
        "tests": r'''
            import json
            from solution import extract_tool_calls

            def call(id_, name, args, type_="function"):
                return {"id": id_, "type": type_, "function": {"name": name, "arguments": args}}

            def resp(*messages):
                return {"id": "r", "choices": [{"index": i, "message": m} for i, m in enumerate(messages)]}

            def test_single_tool_call_with_decoded_arguments():
                r = resp({"role": "assistant", "content": None,
                          "tool_calls": [call("call_1", "get_weather", json.dumps({"city": "Paris"}))]})
                got = extract_tool_calls(r)
                assert got == [{"id": "call_1", "name": "get_weather", "arguments": {"city": "Paris"}}], f"got {got!r}"

            def test_multiple_choices_and_calls_in_order():
                r = resp({"tool_calls": [call("a", "search", '{"q": "x"}'), call("b", "calc", '{"e": "1+1"}')]},
                         {"content": "no tools", "tool_calls": None},
                         {"tool_calls": [call("c", "noop", "")]})
                got = [(c["id"], c["name"], c["arguments"]) for c in extract_tool_calls(r)]
                assert got == [("a", "search", {"q": "x"}), ("b", "calc", {"e": "1+1"}), ("c", "noop", {})], f"got {got!r}"

            def test_legacy_function_call_has_id_none():
                r = resp({"content": None, "function_call": {"name": "lookup", "arguments": '{"id": 7}'}})
                got = extract_tool_calls(r)
                assert got == [{"id": None, "name": "lookup", "arguments": {"id": 7}}], f"got {got!r}"

            def test_no_calls_returns_empty_list():
                for r in ({}, {"choices": []}, {"choices": [{}]}, {"choices": [{"message": None}]},
                          resp({"role": "assistant", "content": "Hi"})):
                    assert extract_tool_calls(r) == [], f"expected [] for {r!r}"

            def test_skips_non_function_and_blank_arguments():
                r = resp({"tool_calls": [call("x", "code", "{}", type_="code_interpreter"),
                                         call("y", "ping", None), call("z", "pong", "  ")]})
                got = [(c["id"], c["arguments"]) for c in extract_tool_calls(r)]
                assert got == [("y", {}), ("z", {})], f"got {got!r}"

            def test_invalid_json_raises_value_error_naming_the_call_id():
                r = resp({"tool_calls": [call("call_ok", "a", "{}"), call("call_bad", "b", '{"city": ')]})
                try:
                    extract_tool_calls(r)
                except ValueError as e:
                    assert "call_bad" in str(e), f"error message should contain the call id: {e}"
                else:
                    assert False, "invalid JSON arguments should raise ValueError"

            def test_non_object_json_raises_value_error_naming_the_function():
                r = resp({"function_call": {"name": "legacy_fn", "arguments": "[1, 2]"}})
                try:
                    extract_tool_calls(r)
                except ValueError as e:
                    assert "legacy_fn" in str(e), f"error message should contain the function name: {e}"
                else:
                    assert False, "arguments that are not a JSON object should raise ValueError"
        ''',
        "solution": r'''
            import json


            def _parse_args(raw, label):
                if raw is None or not raw.strip():
                    return {}
                try:
                    args = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON arguments for {label}: {exc}") from exc
                if not isinstance(args, dict):
                    raise ValueError(f"arguments for {label} must be a JSON object")
                return args


            def extract_tool_calls(response):
                calls = []
                for choice in response.get("choices") or []:
                    message = choice.get("message") or {}
                    for tc in message.get("tool_calls") or []:
                        if tc.get("type", "function") != "function":
                            continue
                        fn = tc.get("function") or {}
                        label = tc.get("id") or fn.get("name")
                        calls.append({"id": tc.get("id"), "name": fn.get("name"),
                                      "arguments": _parse_args(fn.get("arguments"), label)})
                    legacy = message.get("function_call")
                    if legacy:
                        calls.append({"id": None, "name": legacy.get("name"),
                                      "arguments": _parse_args(legacy.get("arguments"), legacy.get("name"))})
                return calls
        ''',
    },
]
