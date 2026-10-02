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

LESSON = r'''
## Working with API data - chapter notes

An API response is JSON turned into **nested dicts and lists**. The job: dig out what you
need, survive missing pieces, react properly to failures.

**Paths.** Each `[...]` goes one level down: key for a dict, index for a list.
`r["choices"][0]["message"]["content"]` = key, index, key, key. Lists start at index `0`.

**Missing vs `None`**

| expression | key missing | key holds `None` |
| --- | --- | --- |
| `d["k"]` | `KeyError` | `None` |
| `d.get("k")` | `None` | `None` |
| `d.get("k", 0)` | `0` | `None` (!) |
| `d.get("k") or 0` | `0` | `0` |

```python
response = {"choices": [], "usage": None}
usage = response.get("usage") or {}
print(usage.get("total_tokens", 0))
choices = response.get("choices") or []
print(choices[0]["message"]["content"] if choices else "")
```

**Status codes:** `2xx` success - `400` bad input, `401` bad key, `403` forbidden,
`404` not found, `429` rate limited - `5xx` server broke. Retry only `429`, `5xx` and
connection errors, with *exponential backoff* (`base * 2 ** attempt`), honouring
`retry_after` when given. Never retry a `401`.

**Errors as exceptions:** a small `class APIError(Exception)` that stores `status` lets
callers `except APIError as err:` and read `err.status`.

**Pagination:** each page has `data` + `next_cursor`; loop until the cursor is `None`, with
a `max_pages` safety limit.

**Tool calls:** `arguments` arrive as a JSON **string** - `json.loads` it, and remember
`json.JSONDecodeError` is a subclass of `ValueError`.

**Gotchas**
- `d.get(k, default)` doesn't replace a `None` value - use `or`.
- `choices[0]` on `[]` is an `IndexError` - check `if choices:` first.
- Compute totals yourself instead of trusting one field the API might omit.
'''

EXERCISES = [
    {
        "id": "api-data-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            When you call an LLM API, the answer comes back as JSON, which Python turns into **nested
            dicts and lists** - boxes inside boxes. To reach the reply text you open one box at a time.

            ```python
            response = {
                "model": "gpt-4o",
                "usage": {"prompt_tokens": 12, "completion_tokens": 30},
            }
            print(response["model"])
            print(response["usage"]["prompt_tokens"])
            print(response.get("error"))
            ```

            - `response["usage"]` opens the outer box and gives you the inner dict;
              `["prompt_tokens"]` then reads from that inner dict. Reading left to right, this chain is
              called a *path*.
            - `.get(key)` is the careful version: if the key is missing you get `None` instead of a
              `KeyError` crash, and `.get(key, default)` gives your default instead.

            Watch out: `.get()` only protects **one** level. `response.get("usage")["x"]` still crashes if
            `usage` is missing, because you'd be indexing `None`.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `response["usage"]` is the inner dict, and `["completion_tokens"]` reads `30` from it.
            There is no `"error"` key, so `.get("error")` returns `None` instead of crashing.
            On the last line `"usage"` exists, but it has no `"total_tokens"`, so the default `0`
            is used.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Each `[...]` or `.get(...)` goes one level deeper into the nested dict.",
            "`.get(key)` returns `None` when the key is missing; `.get(key, default)` returns the default instead.",
            "Line 1: open `usage`, then read `completion_tokens`. Line 2: is there an `error` key? Line 3: `usage` exists, but does it contain `total_tokens`?",
        ],
    },
    {
        "id": "api-data-s3",
        "title": "Fix the role lookup",
        "difficulty": 0,
        "lesson": r'''
            Chat APIs send and receive **lists of messages**. A path into a response mixes dict keys and
            list indexes: key to open a dict, number to pick from a list - like "building B, floor 0,
            room 3".

            ```python
            request = {"messages": [
                {"role": "system", "content": "Be brief"},
                {"role": "user", "content": "Hi"},
            ]}
            print(request["messages"][0]["content"])
            print(request["messages"][-1]["role"])
            print(len(request["messages"]))
            ```

            Each message is a dict with a `"role"` (`"system"`, `"user"`, `"assistant"`) and its
            `"content"`. The first message lives at index `0`, the last at `-1`.

            Watch out: counting from 1 is the classic slip. `[1]` is the **second** item - and on a
            one-item list it raises `IndexError: list index out of range`.
        ''',
        "prompt": r'''
            A chat request holds a list of messages. This function should tell you who sent the
            first one, but it returns the wrong role (and crashes when there is only one message).

            **Write:** fix `first_role(request)`

            - `request`: a dict like `{"messages": [{"role": "system", "content": "Be brief"}, ...]}`
              with at least one message
            - **Returns:** a `str`, the `"role"` of the **first** message in `request["messages"]`

            **Rules**
            - Must also work when the list has only one message.

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
            "Look closely at the list index in the path.",
            "Python lists start counting at 0, so the first item is not at index 1.",
            "Change the index after `[\"messages\"]` so it points to the first message, then keep reading its `\"role\"`.",
        ],
    },
    {
        "id": "api-data-s2",
        "title": "Model name with a default",
        "difficulty": 0,
        "lesson": r'''
            A coat check hands your coat back when you show the ticket. If the ticket is lost, a nice
            coat check gives you a spare umbrella instead of shouting. That's `.get(key, default)`: the
            value if the key exists, otherwise the default you chose.

            ```python
            config = {"model": "gpt-4o", "temperature": 0.2}
            print(config.get("model", "default-model"))
            print(config.get("max_tokens", 256))
            print(config.get("stream"))
            ```

            API responses often skip keys - an error response has no `"model"`, a streaming chunk has no
            `"usage"`. Reading them with `d["key"]` would raise `KeyError`. With `.get` and a sensible
            default, your code keeps going.

            The vocabulary: this is a *fallback* or *default value*. Pick one of the type the caller
            expects - `""` for text, `0` for counts, `[]` for lists - so the next line of code still works.
        ''',
        "prompt": r'''
            An API response usually says which model answered, but an error response may not.

            **Write:** fill in the blank (`___`) in `get_model(response)`

            - `response`: a dict, e.g. `{"model": "gpt-4o", "choices": []}`
            - **Returns:** a `str`: `response["model"]`, or `"unknown"` when that key is missing

            **Rules**
            - A missing `"model"` key (including an empty dict `{}`) gives `"unknown"`; don't crash.

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
            "The second argument of `.get()` is what you get back when the key is missing.",
            "Put the fallback value the prompt asks for in the blank.",
            "Replace `___` with the string `\"unknown\"` (with quotes, since it is text).",
        ],
    },
    {
        "id": "api-data-s6",
        "title": "Missing or None?",
        "difficulty": 0,
        "lesson": r'''
            Here's a trap every API programmer hits. The coat check has your ticket, but the hook is
            **empty**. The key exists - it just holds `None` (JSON's `null`). APIs do this a lot:
            `"content": null` when the model calls a tool, `"usage": null` on some errors.

            `.get(key, default)` only uses the default when the key is **missing**, so it won't help.
            The fix is `or`: `a or b` gives `a` if it's "truthy", otherwise `b`. `None`, `0`, `""`, `[]`
            and `{}` are all "falsy".

            ```python
            reply = {"content": None}
            print(reply.get("content", "?"))
            print(reply.get("content") or "?")
            print([] or "empty list")
            print("hi" or "?")
            ```

            The pattern `d.get("key") or default` handles **both** cases - missing key *and* `None` - in
            one go. Programmers call this *coalescing* a value.

            Watch out: `or` also replaces legit falsy values - a real count of `0` would become the
            default. That's fine when the default is `0` too.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `"content"` **exists** but holds `None`, so `.get("content", "empty")` returns that
            `None` - the default is only for missing keys. `None or "empty"` gives `"empty"`
            because `None` is falsy. `"name"` is **missing**, so both styles give `"anon"`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Ask two questions for each line: is the key there at all, and what value does it hold?",
            "`.get(key, default)` uses the default only when the key is missing. `x or y` gives `y` whenever `x` is falsy, and `None` is falsy.",
            "Line 1: the key exists, so its stored value is printed. Line 2: that value is falsy, so the right side of `or` wins. Lines 3-4: the key is missing, so both give the fallback.",
        ],
    },
    {
        "id": "api-data-s5",
        "title": "Count the results",
        "difficulty": 0,
        "lesson": r'''
            Big lists come back in **pages**, like a search engine showing 10 results at a time. A page
            is a dict with the items (often under `"data"`) plus a pointer to the next page. Before you
            loop over the items, make sure you really have a list.

            ```python
            pages = [{"data": ["a", "b"]}, {"data": None}, {}]
            for page in pages:
                items = page.get("data") or []
                print(len(items), items)
            ```

            The line `page.get("data") or []` is the coalescing trick from the last step: whether
            `"data"` is missing or `None`, you end up with an empty list, and `len`, `for` and `if` all
            work on it.

            This habit - turn "nothing" into an empty container as early as possible - is sometimes
            called *normalising* the input. It keeps the rest of your code free of special cases.
        ''',
        "prompt": r'''
            A search API returns results one page at a time. Count how many results one page holds.

            **Write:** `count_results(page)`

            - `page`: a dict like `{"data": ["a", "b"], "next_cursor": "x"}`; `"data"` is a list
              of results, but it may be missing or `None`
            - **Returns:** an `int`, the number of items in `page["data"]`

            **Rules**
            - If `"data"` is an empty list, return `0`.
            - If `"data"` is `None`, return `0`.
            - If the `"data"` key is missing, return `0` (don't crash).
            - Reminder: `value or []` gives `[]` when `value` is `None`.

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
            "Use `.get()` so a missing key does not crash, and `len()` to count.",
            "`.get(\"data\")` may give `None`; turn that into an empty list before counting.",
            "1) Read `page.get(\"data\")`. 2) Add `or []` so None becomes an empty list. 3) Return `len(...)` of that.",
        ],
    },
    {
        "id": "api-data-s4",
        "title": "Was it a success?",
        "difficulty": 0,
        "lesson": r'''
            Every HTTP response carries a three-digit **status code** - like the little light on a
            parcel tracker: green, orange or red. The first digit tells you the family:

            - `2xx` success (`200` OK, `201` created)
            - `4xx` **you** made a mistake (`400` bad input, `401` bad key, `404` not found,
              `429` too many requests)
            - `5xx` the **server** broke (`500`, `502`, `503`)

            ```python
            for status in (200, 204, 404, 503):
                family = status // 100
                print(status, "family", family, "success:", 200 <= status < 300)
            ```

            Python lets you *chain* comparisons: `200 <= status < 300` reads like maths and is already a
            `bool` - no `if` needed to return it.

            Watch out for the edges: `200` is in the range and `300` is not, hence `<=` on the left and
            `<` on the right.
        ''',
        "prompt": r'''
            Every HTTP response has a status code. Codes from 200 to 299 (the "2xx" range) mean
            the request worked; anything else (e.g. `429` rate limited, `500` server error) did not.

            **Write:** `is_success(status)`

            - `status`: an `int` HTTP status code, e.g. `200`
            - **Returns:** the `bool` `True` if `status` is between 200 and 299 inclusive, else `False`

            **Rules**
            - Return the actual `True` / `False` values (not `1`/`0` or `None`).
            - `200` and `299` are successes; `199` and `300` are not.

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
            "A comparison like `a <= x < b` already evaluates to True or False.",
            "Check that the status is at least 200 and below 300, and return the result of that check.",
            "Return a chained comparison: 200 is allowed, 300 is not. No `if` is needed.",
        ],
    },
    {
        "id": "api-data-1",
        "hints": [
            'Walk the path one level at a time with `.get()`, and guard against `None` and an empty list.',
            'At each step, replace a missing or `None` value with an empty container (`or []` / `or {}`), and check the choices list is not empty before taking item 0.',
            '1) `choices = response.get("choices") or []`. 2) If it is empty, return `""`. 3) Take the first choice\'s `"message"` with `.get(...) or {}`. 4) Return its `"content"` with `or ""` so None becomes an empty string.',
        ],
        "title": "Safe reply extraction",
        "difficulty": 1,
        "lesson": r'''
            Now combine the guards into one safe path. Picture walking down a dark staircase: at every
            step you check the next step exists before putting your weight on it.

            ```python
            def first_city(data):
                users = data.get("users") or []
                if not users:
                    return ""
                address = users[0].get("address") or {}
                return address.get("city") or ""

            print(first_city({"users": [{"address": {"city": "Lyon"}}]}))
            print(repr(first_city({"users": [{"address": None}]})))
            print(repr(first_city({})))
            ```

            Each line does one step: coalesce a missing or `None` value into an empty container, check
            the list isn't empty before indexing `[0]`, and coalesce the final value into the type you
            promise to return.

            This style is called *defensive* code. It's exactly what you want at the edge of your
            program, where untrusted API data comes in - once it's been cleaned up, the rest of your code
            can stay simple.
        ''',
        "prompt": r'''
            A chat-completion API answers with a nested dict. Pull out the reply text without
            ever crashing on an unusual response (an error, an empty result, a tool call).

            **Write:** `get_reply(response)`

            - `response`: a dict like
              `{"choices": [{"message": {"role": "assistant", "content": "Hi"}}]}`
            - **Returns:** a `str`: the `"content"` of the `"message"` of the **first** choice,
              i.e. `response["choices"][0]["message"]["content"]`

            **Rules**
            - Only the first choice counts; ignore any others.
            - If `"choices"` is missing, `None` or an empty list, return `""`.
            - If the first choice has no `"message"`, or it is `None`, return `""`.
            - If `"content"` is missing or `None` (this happens when the model calls a tool), return `""`.
            - Never raise an exception for these cases.

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
            'Keep two running totals and loop over the responses, reading usage safely with `.get()`.',
            'For each response, get its usage dict (or an empty dict if missing/None), then add its prompt and completion counts, treating missing/None as 0. Compute the total yourself at the end.',
            '1) Start `prompt = 0` and `completion = 0`. 2) For each response: `usage = response.get("usage") or {}`. 3) Add `usage.get("prompt_tokens") or 0` and the same for completion. 4) Return the dict with `total_tokens = prompt + completion`.',
        ],
        "title": "Total token usage",
        "difficulty": 1,
        "lesson": r'''
            You pay for LLM calls **per token**, so apps keep a running total - like a taxi meter adding
            each trip's fare. Each response's `"usage"` dict holds that call's counts.

            ```python
            trips = [{"fare": 12}, {"fare": None}, {}, {"fare": 5}]
            total = 0
            for trip in trips:
                total += trip.get("fare") or 0
            print(total)
            ```

            The loop is the *accumulator* pattern from the loops chapter; the `or 0` from this chapter
            makes missing or `None` values count as zero instead of crashing with `TypeError`.

            A typical usage dict looks like `{"prompt_tokens": 10, "completion_tokens": 5,
            "total_tokens": 15}`. *Prompt* tokens are what you sent, *completion* tokens what the model
            wrote (usually priced higher).

            Watch out: don't trust one field for everything - if a response is missing `total_tokens`
            you'd undercount. Summing the parts yourself is safer.
        ''',
        "prompt": r'''
            You pay per token. Add up how many tokens a batch of API calls used.

            **Write:** `total_usage(responses)`

            - `responses`: a `list` of response dicts; each may have a `"usage"` dict like
              `{"prompt_tokens": 10, "completion_tokens": 5}`
            - **Returns:** a dict with exactly three `int` values:
              `{"prompt_tokens": ..., "completion_tokens": ..., "total_tokens": ...}`

            **Rules**
            - `"prompt_tokens"` is the sum of all prompt counts; `"completion_tokens"` likewise.
            - `"total_tokens"` is **your own** sum of those two results. Ignore any
              `"total_tokens"` the API put inside a usage dict.
            - A missing `"usage"` key, or `"usage": None`, counts as 0 tokens.
            - A missing count inside usage, or a count of `None`, counts as 0.
            - An empty list gives all three values `0`.

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
            When a request fails, the status code tells you **what to do next** - like a shop sign:
            "Closed, back in 5 minutes" (wait and come back) is very different from "Wrong address"
            (coming back won't help).

            - `2xx`: it worked, use the body.
            - `429` *Too Many Requests*: you're going too fast - wait, then try again.
            - `5xx`: the server had a problem - often temporary, worth another try.
            - other `4xx`: **your** request is wrong (bad key, bad JSON, unknown model). Sending the same
              request again gives the same error; fix the request instead.

            ```python
            def is_server_error(status):
                return 500 <= status <= 599

            for status in (200, 404, 500, 503):
                print(status, is_server_error(status))
            ```

            Errors worth retrying are called *transient* (they go away on their own); the others are
            *permanent*. Deciding which is which is the first step of every retry strategy.
        ''',
        "prompt": r'''
            Before retrying a failed LLM request, decide what kind of result you got.

            **Write:** `classify_status(status)`

            - `status`: an `int` HTTP status code, e.g. `429`
            - **Returns:** one of these `str` values:
              - `"ok"` for 200-299
              - `"retry"` for `429` and for 500-599
              - `"fix request"` for any other code from 400 to 499
              - `"unknown"` for anything else (e.g. `100`, `302`, `600`)

            **Rules**
            - Ranges include both ends: `200`, `299`, `500` and `599` are inside their range.

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
            "A chain of `if` checks with range comparisons, each returning a label.",
            "Order matters: check `429` before the general 4xx range, otherwise it would be labelled \"fix request\".",
            "1) 200-299 -> \"ok\". 2) 429, or 500-599 -> \"retry\". 3) 400-499 -> \"fix request\". 4) Anything left -> \"unknown\".",
        ],
    },
    {
        "id": "api-data-8",
        "title": "Raise an API error",
        "difficulty": 1,
        "lesson": r'''
            Returning `"retry"` or `None` from deep inside your code is like whispering a problem - the
            caller can easily miss it. Raising an exception is pulling the fire alarm: nobody can ignore
            it, and whoever knows how to handle it catches it. A **custom exception class** makes the
            alarm specific: "the API failed, with status 429".

            ```python
            class QuotaError(Exception):
                def __init__(self, used, limit):
                    super().__init__(f"used {used} of {limit}")
                    self.used = used

            try:
                raise QuotaError(120, 100)
            except QuotaError as err:
                print("caught:", err, "| used =", err.used)
            ```

            - Inheriting from `Exception` makes it a real exception you can `raise` and `except`.
            - `super().__init__(message)` sets the text shown by `str(err)` and in tracebacks.
            - Extra attributes like `err.used` let the handler make decisions (retry? give up?).

            This is how real SDKs work: the OpenAI and Anthropic clients raise their own error classes
            carrying the HTTP status.
        ''',
        "prompt": r'''
            Turn a failed HTTP response into an exception that carries its status code, so the
            caller can decide what to do.

            **Write:** two things

            1. A class `APIError(Exception)`, created as `APIError(status, message)`:
               - `status`: an `int`, stored as the attribute `.status`
               - `message`: a `str`, which is also what `str(error)` returns
            2. A function `check_response(status, body)`
               - `status`: an `int` HTTP status code, e.g. `200`
               - `body`: a `dict` (the decoded JSON body), e.g. `{"error": {"message": "slow down"}}`
               - **Returns:** `body` unchanged if `status` is 200-299

            **Rules**
            - For any other status, raise `APIError(status, message)`.
            - The message is `body["error"]["message"]` when it exists and is a non-empty string.
            - Otherwise (no `"error"`, `"error": None`, no `"message"`, ...) the message is
              `"HTTP "` followed by the status, e.g. `"HTTP 503"`.

            **Examples**
            ```python
            check_response(200, {"ok": True})                          # returns {"ok": True}
            check_response(429, {"error": {"message": "slow down"}})   # raises APIError: .status 429, str() "slow down"
            check_response(503, {})                                    # raises APIError: .status 503, str() "HTTP 503"
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
            "Subclass `Exception`, pass the message up with `super().__init__(message)`, and store the status on `self`.",
            "In `check_response`, return early on 2xx. Otherwise dig the message out with the safe `.get(...) or ...` pattern and raise.",
            "1) `APIError.__init__(self, status, message)`: call `super().__init__(message)`, set `self.status = status`. 2) If 200 <= status <= 299, return body. 3) `error = body.get(\"error\") or {}`. 4) `message = error.get(\"message\") or f\"HTTP {status}\"`. 5) `raise APIError(status, message)`.",
        ],
    },
    {
        "id": "api-data-9",
        "title": "Decode tool arguments",
        "difficulty": 1,
        "lesson": r'''
            When a model asks to use a tool, it sends the tool's arguments as a **JSON string**, not a
            dict - like a letter still in its envelope. You have to open it with `json.loads` before
            you can read it. And sometimes the letter is torn: models occasionally produce broken JSON.

            ```python
            import json

            raw = '{"city": "Paris", "days": 3}'
            args = json.loads(raw)
            print(args["city"], args["days"] + 1)
            try:
                json.loads('{"city": "Par')
            except ValueError as err:
                print("broken:", type(err).__name__)
            ```

            Things to know:
            - `json.loads` on valid JSON can still give a **list** or a number, not a dict - check with
              `isinstance(args, dict)` when you need a dict.
            - Broken JSON raises `json.JSONDecodeError`. How that class relates to `ValueError` is this
              step's research task.
            - Re-raising with a clearer message (`raise ValueError(...) from err`) keeps the original
              error attached for debugging - this is called *exception chaining*.
        ''',
        "research": {
            "note": "Read what `json.loads` raises for invalid text, and how `json.JSONDecodeError` relates to `ValueError`, then come back.",
            "links": [
                {"title": "json.loads - Python docs", "url": "https://docs.python.org/3/library/json.html#json.loads"},
                {"title": "json.JSONDecodeError - Python docs", "url": "https://docs.python.org/3/library/json.html#json.JSONDecodeError"},
            ],
        },
        "prompt": r'''
            A model asked to call a tool. Decode the arguments it sent so you can call your
            Python function with them.

            **Write:** `parse_arguments(call)`

            - `call`: a dict like `{"name": "get_weather", "arguments": '{"city": "Paris"}'}`;
              `"arguments"` is a JSON **string**
            - **Returns:** a `dict`, the decoded arguments, e.g. `{"city": "Paris"}`

            **Rules**
            - If `"arguments"` is missing, `None` or an empty string `""`, return `{}`.
            - If it is not valid JSON, raise `ValueError` with the message
              `"bad arguments for <name>"`, e.g. `"bad arguments for get_weather"`.
            - If it is valid JSON but not an object (e.g. `"[1, 2]"` or `"5"`), raise the same
              `ValueError` with the same message.

            **Examples**
            ```python
            parse_arguments({"name": "get_weather", "arguments": '{"city": "Paris"}'})   # returns {"city": "Paris"}
            parse_arguments({"name": "now", "arguments": ""})                           # returns {}
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
            "`json.loads` turns the string into Python data; wrap it in `try` / `except` to catch broken JSON.",
            "Handle the empty cases first, then decode inside try/except and re-raise with your own message. After decoding, check the result really is a dict.",
            "1) `raw = call.get(\"arguments\")`; if it's falsy, return `{}`. 2) `try: args = json.loads(raw)` / `except json.JSONDecodeError: raise ValueError(f\"bad arguments for {name}\")`. 3) If `not isinstance(args, dict)`, raise the same error. 4) Return `args`.",
        ],
    },
    {
        "id": "api-data-3",
        "hints": [
            'This is a loop that keeps a `cursor` variable and stops when it becomes `None`.',
            'Start with cursor `None`, fetch a page, add its items, read the next cursor. Limit the loop to `max_pages` iterations and raise if you run out without finishing.',
            '1) `items = []`, `cursor = None`. 2) `for _ in range(max_pages):` fetch the page, `extend` items with `page.get("data") or []`, set `cursor = page.get("next_cursor")`, return items if it is None. 3) After the loop, `raise RuntimeError(...)`.',
        ],
        "title": "Follow the cursor",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Many APIs return long lists one page at a time. Each page tells you the *cursor*
            (a bookmark) to ask for the next page, until there is none left. This is called
            *cursor pagination*.

            **Write:** `fetch_all(fetch_page, max_pages=100)`

            - `fetch_page`: a function you call as `fetch_page(cursor)`; it returns one page, a
              dict like `{"data": [1, 2], "next_cursor": "p2"}`
            - `max_pages`: an `int`, the most pages you may fetch, e.g. `5`
            - **Returns:** a `list` of all items from all pages, in order, e.g. `[1, 2, 3]`

            **Rules**
            - The first call is `fetch_page(None)`. Each following call passes the previous page's
              `"next_cursor"` (e.g. `fetch_page("p2")`).
            - Stop when `"next_cursor"` is `None` **or** missing from the page.
            - A page's `"data"` may be an empty list; just add nothing and keep going.
            - Fetching exactly `max_pages` pages is fine if the last one ends the list.
            - If the list has still not ended after `max_pages` pages, raise `RuntimeError`
              (a guard against APIs that never stop). Never call `fetch_page` more than
              `max_pages` times.

            **Examples**
            ```python
            pages = {None: {"data": [1, 2], "next_cursor": "p2"},
                     "p2": {"data": [], "next_cursor": "p3"},
                     "p3": {"data": [3], "next_cursor": None}}
            fetch_all(lambda cursor: pages[cursor])        # returns [1, 2, 3]
                                                           # (called with None, "p2", "p3")
            fetch_all(lambda cursor: {"data": ["a"]})      # returns ["a"] (no next_cursor key)
            fetch_all(lambda cursor: {"data": [0], "next_cursor": "again"}, max_pages=5)
            # raises RuntimeError after at most 5 calls
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
            'Validate each argument in turn and `raise ValueError(...)` as soon as something is wrong; build the payload only from valid pieces.',
            'Check types with `isinstance` (remember `bool` is a subclass of `int`, so exclude it explicitly). Copy each message dict with `dict(m)` and add optional keys only when they are not None.',
            '1) Check `model` is a non-empty str. 2) Check `messages` is a non-empty list of dicts with a valid role and str content. 3) Start the payload with `model` and a list of copied messages. 4) For temperature / max_tokens / stop: if not None, validate the range/type and add the key.',
        ],
        "title": "Validated request payload",
        "difficulty": 2,
        "prompt": r'''
            Before sending a request to an LLM API, check it locally so a typo fails fast with a
            clear message instead of a vague HTTP 400.

            **Write:** `build_payload(model, messages, *, temperature=None, max_tokens=None, stop=None)`
            (the `*` means the last three must be passed by keyword, e.g. `temperature=0`)

            - `model`: a `str`, e.g. `"gpt-4o"`
            - `messages`: a `list` of dicts like `{"role": "user", "content": "Hi"}`
            - `temperature`: a number, or `None` (not given)
            - `max_tokens`: an `int`, or `None`
            - `stop`: a `str` or a `list` of strings, or `None`
            - **Returns:** the request body dict: `{"model": ..., "messages": [...]}` plus a
              `"temperature"`, `"max_tokens"` and/or `"stop"` key only for the options that are not `None`

            **Rules** (every failure raises `ValueError`; the message is up to you):
            - `model` must be a non-empty `str` (`""` and `None` are errors).
            - `messages` must be a non-empty `list`. Each item must be a `dict`, its `"role"` one of
              `"system"`, `"user"`, `"assistant"`, `"tool"`, and its `"content"` a `str`
              (a missing content, or content `5`, is an error).
            - `temperature`, if given, is an `int` or `float` from 0 to 2 inclusive (`2` is fine;
              `2.5`, `-0.1`, `"0.5"` and `True` are errors).
            - `max_tokens`, if given, is an `int` of at least 1 (`0`, `1.5` and `True` are errors).
            - `stop`, if given, is a `str`, or a `list` of at most 4 items that are all `str`
              (`5`, `["a", 1]` and a 5-item list are errors).
            - Note: `True` and `False` count as ints in Python, so reject bools explicitly.
            - The payload's messages must be **copies**: changing `payload["messages"]` or the dicts
              inside it must not change the caller's list or dicts.

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
            'Define `__init__(self, status, message)` on the exception (call `super().__init__(message)`), then write a `for attempt in range(max_attempts)` loop with try/except.',
            'Each attempt: call `request()`; on success return the body; on a non-retryable status raise immediately; otherwise remember the status and sleep with an exponentially growing delay - but not after the last attempt.',
            '1) delay = `base_delay * 2 ** attempt`. 2) `except ConnectionError`: last_status = None. 3) 2xx: return body. 4) Not 429 and not 5xx: raise APIError(status). 5) For 429 with a numeric `retry_after` in a dict body, delay = max(retry_after, delay). 6) If this is not the last attempt, `sleep(delay)`. 7) After the loop, raise APIError(last_status).',
        ],
        "title": "Retry with backoff",
        "difficulty": 3,
        "prompt": r'''
            LLM APIs fail now and then: rate limits (429), overloaded servers (5xx), dropped
            connections. A robust client retries those, waiting longer each time (this is called
            *exponential backoff*), but gives up at once on errors that retrying can't fix.

            **Write:**
            1. An exception class `APIError(Exception)` created as `APIError(status, message)`,
               whose objects have a `.status` attribute (an `int`, or `None`).
            2. `call_with_retry(request, *, max_attempts=4, base_delay=1.0, sleep=time.sleep)`
               - `request`: a function with no arguments; `request()` returns a tuple
                 `(status, body)`, e.g. `(200, {"ok": True})`, or raises `ConnectionError`
               - `max_attempts`: an `int`, the most times `request` may be called
               - `base_delay`: a `float`, the first wait in seconds
               - `sleep`: the function to call to wait (tests pass their own to record the delays)
               - **Returns:** the `body` of the first successful response

            **Rules**
            - A status from 200 to 299 is a success: return its `body` right away.
            - Status `429`, any status from 500 to 599, or a raised `ConnectionError` is
              *retryable*: wait, then call `request` again.
            - The wait before retry number `k` (counting from 0) is `base_delay * 2 ** k`, so with
              the defaults `1.0`, `2.0`, `4.0`. Always wait by calling `sleep(seconds)`.
            - For a `429` whose body is a dict with a numeric `"retry_after"`, wait
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
            "Loop over every choice, then over its message's `tool_calls`, using `.get(...) or []` / `or {}` everywhere; use `json.loads` for the arguments.",
            'Write a small helper that turns an arguments string into a dict: blank/None gives `{}`, invalid JSON or a non-dict raises ValueError mentioning a label. Also handle the legacy `function_call` key per message.',
            '1) For each choice: `message = choice.get("message") or {}`. 2) For each tool call: skip if its `type` (default "function") is not "function"; read `function.name` and `function.arguments`. 3) Parse args with the helper, catching `json.JSONDecodeError` and re-raising ValueError with the id (or name). 4) If `message.get("function_call")`, append one call with id None.',
        ],
        "title": "Extract tool calls",
        "difficulty": 3,
        "prompt": r'''
            When a model wants to use a tool, the response lists *tool calls* instead of (or as
            well as) text. Your agent must pull them out and decode their arguments before it can
            run the tools.

            **Write:** `extract_tool_calls(response)`

            - `response`: a chat-completion dict, `{"choices": [{"message": {...}}, ...]}`
            - **Returns:** a `list` of dicts `{"id": ..., "name": ..., "arguments": {...}}`, one per
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
