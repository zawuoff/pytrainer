"""Module test: APIs, Data & Integrations (http, api-data, regex, sql)."""

EXAM = {
    "module": "apis-data",
    "title": "APIs, Data & Integrations: module test",
    "intro": r'''
        This is a **test**, not a lesson. It checks the whole APIs & Data module: HTTP
        requests and responses, working with API data (pagination, retries, errors),
        regular expressions and SQL - the integration work every AI product runs on.

        **How it works**

        - There are **no hints and no tutor** while you take it. You get the prompt, the
          checks and your own knowledge.
        - Nothing here touches the network: requests are built but not sent, and "APIs" are
          fake functions passed in by the checks. Databases are in-memory `sqlite3`.
        - Every rule the checks test is in the prompt or its examples.
        - Two exercises are *research* tasks: some link to official docs, and one asks you
          to find a standard-library module on your own.

        **Passing**

        Pass at least **70%** of the exercises and the module counts as done: you can skip
        its chapters and move on. If not, the chapters will show you exactly where to focus.
    ''',
    "pass_ratio": 0.7,
}

EXERCISES = [
    {
        "id": "exam-apis-data-1",
        "title": "Build an authenticated request",
        "difficulty": 2,
        "research": {
            "note": "Read how `urllib.request.Request` stores its URL, headers and method, and how "
                    "`urllib.parse.urlencode` turns a dict into a query string.",
            "links": [
                {"title": "urllib.request.Request - Python docs",
                 "url": "https://docs.python.org/3/library/urllib.request.html#urllib.request.Request"},
                {"title": "urllib.parse.urlencode - Python docs",
                 "url": "https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode"},
                {"title": "Authorization header - MDN",
                 "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization"},
            ],
        },
        "prompt": r'''
            Before calling a search API you build the request object (sending it is another step).

            **Write:** `build_request(base_url, api_key, params)`

            - `base_url`: e.g. `"https://api.example.com/v1/search"`
            - `api_key`: the secret key, a string like `"sk-123"`
            - `params`: a dict of query parameters, e.g. `{"q": "vector db", "limit": 5}`
            - **Returns:** a `urllib.request.Request` (not sent)

            **Rules**
            - Parameters whose value is `None` are left out.
            - The query string is made with `urllib.parse.urlencode` (so spaces become `+`),
              keeping the dict's order, and added after a `?`. With no parameters left, the
              URL is just `base_url` (no `?`).
            - Headers: `Authorization: Bearer <api_key>` and `Accept: application/json`.
            - The method is `GET`.
            - If `api_key` is empty, raise `ValueError` with the message `"missing API key"`.

            **Examples**
            ```python
            req = build_request("https://api.example.com/v1/search", "sk-123",
                                {"q": "vector db", "limit": 5, "cursor": None})
            req.full_url                      # "https://api.example.com/v1/search?q=vector+db&limit=5"
            req.get_header("Authorization")   # "Bearer sk-123"
            req.get_method()                  # "GET"
            build_request("https://x.dev", "", {})   # raises ValueError("missing API key")
            ```
        ''',
        "starter": r'''
            import urllib.parse
            import urllib.request


            def build_request(base_url, api_key, params):
                ...
        ''',
        "tests": r'''
            import urllib.request
            from solution import build_request

            BASE = "https://api.example.com/v1/search"

            def test_builds_url_with_query_string():
                req = build_request(BASE, "sk-123", {"q": "vector db", "limit": 5, "cursor": None})
                assert isinstance(req, urllib.request.Request), f"got {type(req).__name__}"
                assert req.full_url == BASE + "?q=vector+db&limit=5", f"url was {req.full_url!r}"

            def test_headers_are_set():
                req = build_request(BASE, "sk-123", {"q": "x"})
                assert req.get_header("Authorization") == "Bearer sk-123", \
                    f"Authorization was {req.get_header('Authorization')!r}"
                assert req.get_header("Accept") == "application/json", \
                    f"Accept was {req.get_header('Accept')!r}"

            def test_method_is_get():
                assert build_request(BASE, "k", {}).get_method() == "GET"

            def test_no_params_means_no_question_mark():
                assert build_request(BASE, "k", {}).full_url == BASE
                assert build_request(BASE, "k", {"cursor": None}).full_url == BASE

            def test_special_characters_are_encoded():
                req = build_request(BASE, "k", {"q": "a&b=c"})
                assert req.full_url == BASE + "?q=a%26b%3Dc", f"url was {req.full_url!r}"

            def test_empty_key_raises_value_error():
                try:
                    build_request(BASE, "", {})
                except ValueError as e:
                    assert str(e) == "missing API key", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for an empty key")
        ''',
        "solution": r'''
            import urllib.parse
            import urllib.request


            def build_request(base_url, api_key, params):
                if not api_key:
                    raise ValueError("missing API key")
                kept = {k: v for k, v in params.items() if v is not None}
                url = base_url
                if kept:
                    url += "?" + urllib.parse.urlencode(kept)
                headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
                return urllib.request.Request(url, headers=headers, method="GET")
        ''',
        "hints": [
            "urllib.parse.urlencode for the query string, urllib.request.Request(url, headers=..., method=...) for the object.",
            "Check the key first. Filter out None values with a dict comprehension. Only add '?' plus the encoded query when something is left. Pass the two headers as a dict.",
            "1) if not api_key: raise ValueError('missing API key'). 2) kept = {k: v for k, v in params.items() if v is not None}. 3) url = base_url, plus '?' + urlencode(kept) if kept. 4) return Request(url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}, method='GET').",
        ],
    },
    {
        "id": "exam-apis-data-2",
        "title": "Decide what to do with a response",
        "difficulty": 3,
        "prompt": r'''
            A resilient API client looks at every response and decides: use it, retry, or give up.

            **Write:** `next_action(response, attempt, max_attempts)`

            - `response`: a dict `{"status": int, "headers": dict, "body": str}`
            - `attempt`: which attempt this was, counting from `1`
            - `max_attempts`: the most attempts allowed, an `int`
            - **Returns:** a tuple, one of
              `("ok", <parsed JSON body>)`, `("retry", <seconds to wait>)`, `("fail", <reason string>)`

            **Rules**
            - Status 200-299: parse `body` as JSON and return `("ok", data)`. If the body isn't
              valid JSON, return `("fail", "invalid JSON body")`.
            - Status 429 or 500-599 (retryable):
              - if `attempt >= max_attempts`, return `("fail", "gave up after <attempt> attempts")`;
              - otherwise wait `int(<Retry-After header>)` seconds if that header is present,
                else `2 ** attempt` seconds, and return `("retry", seconds)`.
              - Header names are case-insensitive: `"retry-after"` counts too.
            - Any other status: return `("fail", "HTTP <status>")`.

            **Examples**
            ```python
            next_action({"status": 200, "headers": {}, "body": '{"id": 1}'}, 1, 3)
            # ("ok", {"id": 1})
            next_action({"status": 429, "headers": {"Retry-After": "7"}, "body": ""}, 1, 3)
            # ("retry", 7)
            next_action({"status": 503, "headers": {}, "body": ""}, 2, 3)
            # ("retry", 4)
            next_action({"status": 503, "headers": {}, "body": ""}, 3, 3)
            # ("fail", "gave up after 3 attempts")
            next_action({"status": 404, "headers": {}, "body": "not found"}, 1, 3)
            # ("fail", "HTTP 404")
            ```
        ''',
        "starter": r'''
            import json


            def next_action(response, attempt, max_attempts):
                ...
        ''',
        "tests": r'''
            from solution import next_action

            def resp(status, body="", headers=None):
                return {"status": status, "headers": headers or {}, "body": body}

            def test_success_parses_json():
                got = next_action(resp(200, '{"id": 1}'), 1, 3)
                assert got == ("ok", {"id": 1}), f"got {got!r}"
                got = next_action(resp(201, "[1, 2]"), 1, 3)
                assert got == ("ok", [1, 2]), f"got {got!r}"

            def test_success_with_bad_json_fails():
                got = next_action(resp(200, "<html>oops</html>"), 1, 3)
                assert got == ("fail", "invalid JSON body"), f"got {got!r}"

            def test_retry_after_header_is_used_case_insensitively():
                got = next_action(resp(429, headers={"Retry-After": "7"}), 1, 3)
                assert got == ("retry", 7), f"got {got!r}"
                got = next_action(resp(429, headers={"retry-after": "3"}), 1, 3)
                assert got == ("retry", 3), f"got {got!r}"

            def test_server_errors_back_off_exponentially():
                assert next_action(resp(500), 1, 5) == ("retry", 2)
                got = next_action(resp(503), 2, 5)
                assert got == ("retry", 4), f"got {got!r}"

            def test_gives_up_at_max_attempts():
                got = next_action(resp(503), 3, 3)
                assert got == ("fail", "gave up after 3 attempts"), f"got {got!r}"

            def test_other_statuses_fail_without_retry():
                assert next_action(resp(404, "not found"), 1, 3) == ("fail", "HTTP 404")
                got = next_action(resp(401), 1, 3)
                assert got == ("fail", "HTTP 401"), f"got {got!r}"
        ''',
        "solution": r'''
            import json


            def next_action(response, attempt, max_attempts):
                status = response["status"]
                if 200 <= status <= 299:
                    try:
                        return ("ok", json.loads(response["body"]))
                    except json.JSONDecodeError:
                        return ("fail", "invalid JSON body")
                if status == 429 or 500 <= status <= 599:
                    if attempt >= max_attempts:
                        return ("fail", f"gave up after {attempt} attempts")
                    headers = {k.lower(): v for k, v in response["headers"].items()}
                    if "retry-after" in headers:
                        return ("retry", int(headers["retry-after"]))
                    return ("retry", 2 ** attempt)
                return ("fail", f"HTTP {status}")
        ''',
        "hints": [
            "Branch on the status code ranges; json.loads in a try/except; lower-case the header names to look one up.",
            "Handle success first, then the retryable statuses (check the attempt count before anything else), then everything else. For headers, build a copy of the dict with lower-case keys.",
            "1) If 200 <= status <= 299: try json.loads(body) -> ('ok', data), except JSONDecodeError -> ('fail', 'invalid JSON body'). 2) If status == 429 or 500 <= status <= 599: if attempt >= max_attempts return the give-up tuple; lower = {k.lower(): v ...}; return ('retry', int(lower['retry-after'])) if present else ('retry', 2 ** attempt). 3) Else ('fail', f'HTTP {status}').",
        ],
    },
    {
        "id": "exam-apis-data-3",
        "title": "Follow cursor pagination",
        "difficulty": 2,
        "prompt": r'''
            A documents API returns results one page at a time. Each page tells you the cursor
            for the next page, or `None` when there are no more.

            **Write:** `fetch_all(get_page, max_pages=10)`

            - `get_page`: a function; `get_page(cursor)` returns a dict like
              `{"data": [...items...], "next_cursor": "abc"}` (or `"next_cursor": None` on the last page)
            - `max_pages`: the most pages you may fetch, an `int`
            - **Returns:** a list of all items from all pages, in order

            **Rules**
            - The first call is `get_page(None)`. Each following call passes the previous
              page's `next_cursor`.
            - Stop when `next_cursor` is `None`.
            - Never call `get_page` more than `max_pages` times. If you've fetched `max_pages`
              pages and there is still a `next_cursor`, raise `RuntimeError` with the message
              `"too many pages"`.
            - A page with `"data": []` is fine.

            **Examples**
            ```python
            pages = {None: {"data": [1, 2], "next_cursor": "p2"},
                     "p2": {"data": [3], "next_cursor": None}}
            fetch_all(lambda cursor: pages[cursor])                # returns [1, 2, 3]
            fetch_all(lambda cursor: pages[cursor], max_pages=1)   # raises RuntimeError("too many pages")
            ```
        ''',
        "starter": r'''
            def fetch_all(get_page, max_pages=10):
                ...
        ''',
        "tests": r'''
            from solution import fetch_all

            PAGES = {None: {"data": [1, 2], "next_cursor": "p2"},
                     "p2": {"data": [], "next_cursor": "p3"},
                     "p3": {"data": [3], "next_cursor": None}}

            def recorder(pages):
                calls = []
                def get_page(cursor):
                    calls.append(cursor)
                    return pages[cursor]
                return get_page, calls

            def test_collects_items_from_all_pages():
                get_page, calls = recorder(PAGES)
                got = fetch_all(get_page)
                assert got == [1, 2, 3], f"got {got!r}"

            def test_passes_cursors_in_order_starting_with_none():
                get_page, calls = recorder(PAGES)
                fetch_all(get_page)
                assert calls == [None, "p2", "p3"], f"cursors passed: {calls!r}"

            def test_single_page():
                get_page, calls = recorder({None: {"data": ["a"], "next_cursor": None}})
                assert fetch_all(get_page) == ["a"]
                assert calls == [None], f"cursors passed: {calls!r}"

            def test_exactly_max_pages_is_fine():
                get_page, calls = recorder(PAGES)
                assert fetch_all(get_page, max_pages=3) == [1, 2, 3]

            def test_too_many_pages_raises_without_extra_calls():
                get_page, calls = recorder(PAGES)
                try:
                    fetch_all(get_page, max_pages=2)
                except RuntimeError as e:
                    assert str(e) == "too many pages", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no RuntimeError when pages ran out")
                assert len(calls) == 2, f"get_page was called {len(calls)} times (max_pages=2)"
        ''',
        "solution": r'''
            def fetch_all(get_page, max_pages=10):
                items = []
                cursor = None
                for _ in range(max_pages):
                    page = get_page(cursor)
                    items.extend(page["data"])
                    cursor = page["next_cursor"]
                    if cursor is None:
                        return items
                raise RuntimeError("too many pages")
        ''',
        "hints": [
            "A loop that runs at most max_pages times, carrying the cursor from one page to the next.",
            "Start with cursor None. Each round: fetch, add the page's items, take its next_cursor, and return if it's None. If the loop finishes without returning, you ran out of pages.",
            "1) items = []; cursor = None. 2) for _ in range(max_pages): page = get_page(cursor); items.extend(page['data']); cursor = page['next_cursor']; if cursor is None: return items. 3) After the loop: raise RuntimeError('too many pages').",
        ],
    },
    {
        "id": "exam-apis-data-4",
        "title": "Redact secrets from logs",
        "difficulty": 3,
        "prompt": r'''
            Before request logs are stored, secrets and emails must be masked.

            **Write:** `redact(text)`

            - `text`: a log line or any string
            - **Returns:** a tuple `(redacted_text, count)` where `count` is the total number of
              replacements made

            **Rules** (applied in this order)
            1. `Bearer ` followed by a token (one or more non-whitespace characters) becomes
               `Bearer ***`.
            2. `sk-` followed by **at least 8** characters that are letters, digits, `-` or `_`
               becomes `sk-***`.
            3. An email address becomes `[email]`. An email is: one or more letters, digits,
               `.`, `_`, `+` or `-`; then `@`; then a domain made of letters, digits and `-`,
               with one or more `.part` sections (e.g. `ada@example.co.uk`).

            Text that has already been replaced (like `sk-***`) must not be counted again.

            **Examples**
            ```python
            redact("auth=Bearer abc.def key=sk-live_12345678 user=ada@example.com")
            # returns ("auth=Bearer *** key=sk-*** user=[email]", 3)
            redact("Authorization: Bearer sk-abcdefghij")
            # returns ("Authorization: Bearer ***", 1)
            redact("sk-short is fine")   # returns ("sk-short is fine", 0)
            ```
        ''',
        "starter": r'''
            import re


            def redact(text):
                ...
        ''',
        "tests": r'''
            from solution import redact

            def test_all_three_kinds():
                got = redact("auth=Bearer abc.def key=sk-live_12345678 user=ada@example.com")
                assert got == ("auth=Bearer *** key=sk-*** user=[email]", 3), f"got {got!r}"

            def test_bearer_rule_runs_first_so_key_inside_counts_once():
                got = redact("Authorization: Bearer sk-abcdefghij")
                assert got == ("Authorization: Bearer ***", 1), f"got {got!r}"

            def test_short_sk_strings_are_not_keys():
                got = redact("sk-short is fine")
                assert got == ("sk-short is fine", 0), f"got {got!r}"

            def test_multi_part_domains_and_several_emails():
                got = redact("from a.b+tag@mail.example.co.uk to x-y@z.io")
                assert got == ("from [email] to [email]", 2), f"got {got!r}"

            def test_not_an_email_without_a_dot_in_domain():
                got = redact("ping admin@localhost")
                assert got == ("ping admin@localhost", 0), f"got {got!r}"

            def test_key_is_masked_but_following_text_kept():
                got = redact("sk-ABCdef_123-xyz, then more")
                assert got == ("sk-***, then more", 1), f"got {got!r}"
        ''',
        "solution": r'''
            import re

            RULES = [
                (re.compile(r"Bearer \S+"), "Bearer ***"),
                (re.compile(r"sk-[A-Za-z0-9_-]{8,}"), "sk-***"),
                (re.compile(r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"), "[email]"),
            ]


            def redact(text):
                total = 0
                for pattern, replacement in RULES:
                    text, n = pattern.subn(replacement, text)
                    total += n
                return text, total
        ''',
        "hints": [
            "The re module can replace AND count in one call. Character classes and {8,} quantifiers describe the patterns.",
            "Write three patterns and apply them one after the other to the updated text, adding up how many replacements each one made. Because `***` isn't a valid key or token character sequence of 8+, replaced text won't match again.",
            "1) Patterns: r'Bearer \\S+', r'sk-[A-Za-z0-9_-]{8,}', and an email pattern: r'[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)+'. 2) total = 0. 3) For each (pattern, replacement): text, n = re.subn(pattern, replacement, text); total += n. 4) return (text, total).",
        ],
    },
    {
        "id": "exam-apis-data-5",
        "title": "Store API usage in SQL",
        "difficulty": 3,
        "research": {
            "note": "Read how `sqlite3` uses `?` placeholders to pass values safely, and how SQLite's "
                    "`INSERT OR IGNORE` handles a row that would break a PRIMARY KEY.",
            "links": [
                {"title": "sqlite3: how to use placeholders - Python docs",
                 "url": "https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders"},
                {"title": "SQLite: ON CONFLICT clause",
                 "url": "https://www.sqlite.org/lang_conflict.html"},
                {"title": "SQLite: aggregate functions",
                 "url": "https://www.sqlite.org/lang_aggfunc.html"},
            ],
        },
        "prompt": r'''
            Record the token usage of every LLM response in a database, then report per model.

            **Write:** two functions that take an open `sqlite3.Connection` `conn`.

            `store_usage(conn, response)`
            - `response`: an API response dict like
              `{"id": "msg_1", "model": "claude-x", "usage": {"input_tokens": 10, "output_tokens": 20}}`
            - Creates the table if it doesn't exist:
              `usage(id TEXT PRIMARY KEY, model TEXT, input_tokens INTEGER, output_tokens INTEGER)`
            - Inserts one row and commits. Returns `True` if a row was inserted, `False` if a row
              with that `id` already existed (the old row is kept, no error).
            - If the response has no `"usage"` key, raise `ValueError` with the message
              `"response has no usage"` (and insert nothing).
            - Pass values with `?` placeholders (model names may contain quotes).

            `usage_by_model(conn)`
            - **Returns:** a list of `(model, total_tokens)` tuples, where `total_tokens` is the
              sum of input + output tokens for that model, ordered by `total_tokens` high to low,
              then by model name A-Z.

            **Examples**
            ```python
            conn = sqlite3.connect(":memory:")
            store_usage(conn, {"id": "a", "model": "big", "usage": {"input_tokens": 10, "output_tokens": 20}})   # True
            store_usage(conn, {"id": "a", "model": "big", "usage": {"input_tokens": 99, "output_tokens": 99}})   # False
            store_usage(conn, {"id": "b", "model": "small", "usage": {"input_tokens": 5, "output_tokens": 5}})   # True
            usage_by_model(conn)   # [("big", 30), ("small", 10)]
            store_usage(conn, {"id": "c", "model": "big"})   # raises ValueError("response has no usage")
            ```
        ''',
        "starter": r'''
            import sqlite3


            def store_usage(conn, response):
                ...


            def usage_by_model(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import store_usage, usage_by_model

            def resp(id_, model, i, o):
                return {"id": id_, "model": model, "usage": {"input_tokens": i, "output_tokens": o}}

            def test_insert_returns_true_and_row_exists():
                conn = sqlite3.connect(":memory:")
                assert store_usage(conn, resp("a", "big", 10, 20)) is True
                rows = conn.execute("SELECT id, model, input_tokens, output_tokens FROM usage").fetchall()
                assert rows == [("a", "big", 10, 20)], f"rows were {rows!r}"

            def test_duplicate_id_returns_false_and_keeps_old_row():
                conn = sqlite3.connect(":memory:")
                store_usage(conn, resp("a", "big", 10, 20))
                assert store_usage(conn, resp("a", "big", 99, 99)) is False
                rows = conn.execute("SELECT input_tokens FROM usage").fetchall()
                assert rows == [(10,)], f"rows were {rows!r}"

            def test_totals_ordered_by_tokens_then_name():
                conn = sqlite3.connect(":memory:")
                store_usage(conn, resp("1", "small", 5, 5))
                store_usage(conn, resp("2", "big", 10, 20))
                store_usage(conn, resp("3", "mid", 4, 6))
                store_usage(conn, resp("4", "big", 1, 1))
                got = usage_by_model(conn)
                assert got == [("big", 32), ("mid", 10), ("small", 10)], f"got {got!r}"

            def test_model_names_with_quotes_are_safe():
                conn = sqlite3.connect(":memory:")
                store_usage(conn, resp("q", "o'brien-7b", 1, 2))
                assert usage_by_model(conn) == [("o'brien-7b", 3)]

            def test_missing_usage_raises_and_inserts_nothing():
                conn = sqlite3.connect(":memory:")
                store_usage(conn, resp("a", "big", 1, 1))
                try:
                    store_usage(conn, {"id": "c", "model": "big"})
                except ValueError as e:
                    assert str(e) == "response has no usage", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for a response without usage")
                count = conn.execute("SELECT COUNT(*) FROM usage").fetchone()[0]
                assert count == 1, f"table has {count} rows"

            def test_changes_are_committed(tmp_name="usage.db"):
                conn = sqlite3.connect(tmp_name)
                store_usage(conn, resp("a", "big", 1, 1))
                other = sqlite3.connect(tmp_name)
                rows = other.execute("SELECT COUNT(*) FROM usage").fetchone()[0]
                assert rows == 1, "another connection can't see the row - did you commit?"
        ''',
        "solution": r'''
            import sqlite3

            SCHEMA = """
                CREATE TABLE IF NOT EXISTS usage (
                    id TEXT PRIMARY KEY,
                    model TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER
                )
            """


            def store_usage(conn, response):
                if "usage" not in response:
                    raise ValueError("response has no usage")
                conn.execute(SCHEMA)
                usage = response["usage"]
                cur = conn.execute(
                    "INSERT OR IGNORE INTO usage VALUES (?, ?, ?, ?)",
                    (response["id"], response["model"], usage["input_tokens"], usage["output_tokens"]),
                )
                conn.commit()
                return cur.rowcount == 1


            def usage_by_model(conn):
                rows = conn.execute(
                    """
                    SELECT model, SUM(input_tokens + output_tokens) AS total
                    FROM usage
                    GROUP BY model
                    ORDER BY total DESC, model ASC
                    """
                ).fetchall()
                return [(model, total) for model, total in rows]
        ''',
        "hints": [
            "CREATE TABLE IF NOT EXISTS, INSERT OR IGNORE with ? placeholders, then SUM + GROUP BY + ORDER BY.",
            "Validate the response first. After an INSERT OR IGNORE, the cursor's rowcount tells you whether a row went in (1) or was ignored (0). Remember conn.commit(). For the report, let SQL do the summing and sorting.",
            "1) If 'usage' not in response: raise ValueError. 2) conn.execute(CREATE TABLE IF NOT EXISTS ...). 3) cur = conn.execute('INSERT OR IGNORE INTO usage VALUES (?, ?, ?, ?)', (...)). 4) conn.commit(); return cur.rowcount == 1. 5) usage_by_model: SELECT model, SUM(input_tokens + output_tokens) AS total FROM usage GROUP BY model ORDER BY total DESC, model ASC; return the rows as tuples.",
        ],
    },
    {
        "id": "exam-apis-data-6",
        "title": "HTTP Basic auth header",
        "difficulty": 3,
        "research": {
            "note": "HTTP Basic authentication sends `user:password` converted with a standard "
                    "binary-to-text encoding. Find out which encoding the HTTP spec uses, and which "
                    "standard-library module implements it (it works on bytes, not str).",
            "links": [],
        },
        "prompt": r'''
            Some internal APIs and webhooks still use HTTP *Basic* authentication.

            **Write:** two functions.

            `basic_auth(user, password)`
            - **Returns:** the header value `"Basic <token>"`, where `<token>` is the standard
              Basic-auth encoding of the UTF-8 text `"<user>:<password>"`.

            `parse_basic(header)`
            - `header`: an `Authorization` header value, e.g. `"Basic YWRhOnMzY3JldA=="`
            - **Returns:** a tuple `(user, password)`

            **Rules for `parse_basic`**
            - Use a regular expression to check the shape: exactly `Basic`, one space, then a
              token of letters, digits, `+`, `/`, ending in at most two `=`. Nothing before or after.
            - The decoded text is split at the **first** `:` (passwords may contain `:`).
            - Raise `ValueError` with the message `"invalid Basic auth header"` if the shape is
              wrong, the token can't be decoded as UTF-8 text, or there is no `:`.

            **Examples**
            ```python
            basic_auth("ada", "s3cret")               # returns "Basic YWRhOnMzY3JldA=="
            parse_basic("Basic YWRhOnMzY3JldA==")     # returns ("ada", "s3cret")
            parse_basic("Bearer abc")                 # raises ValueError("invalid Basic auth header")
            ```
        ''',
        "starter": r'''
            import re


            def basic_auth(user, password):
                ...


            def parse_basic(header):
                ...
        ''',
        "tests": r'''
            from solution import basic_auth, parse_basic

            def expect_invalid(header):
                try:
                    parse_basic(header)
                except ValueError as e:
                    assert str(e) == "invalid Basic auth header", f"message was {str(e)!r}"
                else:
                    raise AssertionError(f"no ValueError for {header!r}")

            def test_builds_header():
                got = basic_auth("ada", "s3cret")
                assert got == "Basic YWRhOnMzY3JldA==", f"got {got!r}"

            def test_non_ascii_is_encoded_as_utf8():
                got = basic_auth("zoë", "pw")
                assert got == "Basic em/Dqzpwdw==", f"got {got!r}"

            def test_parses_header():
                got = parse_basic("Basic YWRhOnMzY3JldA==")
                assert got == ("ada", "s3cret"), f"got {got!r}"

            def test_round_trip_with_colon_in_password():
                got = parse_basic(basic_auth("svc", "a:b:c"))
                assert got == ("svc", "a:b:c"), f"got {got!r}"

            def test_wrong_scheme_or_shape_is_rejected():
                expect_invalid("Bearer abc")
                expect_invalid("Basic")
                expect_invalid("basic YWRhOnMzY3JldA==")
                expect_invalid("Basic YWRh OnMz")
                expect_invalid(" Basic YWRhOnMzY3JldA==")

            def test_undecodable_or_missing_colon_is_rejected():
                expect_invalid("Basic bm9jb2xvbg==")   # decodes to text without ':'
                expect_invalid("Basic //79")           # not valid UTF-8 text
        ''',
        "solution": r'''
            import base64
            import re

            HEADER = re.compile(r"Basic ([A-Za-z0-9+/]+={0,2})")


            def basic_auth(user, password):
                raw = f"{user}:{password}".encode("utf-8")
                return "Basic " + base64.b64encode(raw).decode("ascii")


            def parse_basic(header):
                match = HEADER.fullmatch(header)
                if not match:
                    raise ValueError("invalid Basic auth header")
                try:
                    text = base64.b64decode(match.group(1), validate=True).decode("utf-8")
                except ValueError:
                    raise ValueError("invalid Basic auth header")
                if ":" not in text:
                    raise ValueError("invalid Basic auth header")
                user, password = text.split(":", 1)
                return user, password
        ''',
        "hints": [
            "Search the HTTP docs (e.g. MDN's page on the Authorization header) for the encoding Basic auth uses, then look for a stdlib module with that name.",
            "Encoding: text -> UTF-8 bytes -> encode -> bytes -> back to an ASCII str. Parsing: regex fullmatch to pull out the token, decode it back to bytes and then to text (both steps can raise ValueError subclasses), then split once on ':'.",
            "1) basic_auth: 'Basic ' + base64.b64encode(f'{user}:{password}'.encode()).decode(). 2) parse_basic: m = re.fullmatch(r'Basic ([A-Za-z0-9+/]+={0,2})', header); raise if no match. 3) try: text = base64.b64decode(m.group(1), validate=True).decode('utf-8') except ValueError: raise the error. 4) If ':' not in text raise; else return tuple(text.split(':', 1)).",
        ],
    },
    {
        "id": "exam-apis-data-7",
        "title": "Ingest request logs into SQL",
        "difficulty": 3,
        "prompt": r'''
            Your LLM gateway writes one log line per request. Load the good lines into SQL and
            compute error rates per model.

            A valid line looks exactly like this (single spaces, this field order):
            ```text
            2026-09-25T10:00:01Z model=gpt-4o status=200 latency_ms=812
            ```
            - timestamp: `YYYY-MM-DDTHH:MM:SSZ`
            - model: one or more letters, digits, `.`, `-` or `_`
            - status: exactly 3 digits; latency_ms: one or more digits

            **Write:** two functions that take an open `sqlite3.Connection` `conn`.

            `ingest_logs(conn, lines)`
            - `lines`: a list of strings (they may have a trailing `"\n"` or spaces; strip them first)
            - Creates the table if it doesn't exist:
              `requests(ts TEXT, model TEXT, status INTEGER, latency_ms INTEGER)`
            - Inserts every valid line (status and latency as integers), skips invalid ones, commits.
            - **Returns:** the number of rows inserted.

            `error_rates(conn)`
            - **Returns:** a dict `{model: rate}` where `rate` is the fraction of that model's
              requests with `status >= 400`, rounded to 2 decimal places, models in A-Z order.

            **Examples**
            ```python
            conn = sqlite3.connect(":memory:")
            ingest_logs(conn, [
                "2026-09-25T10:00:01Z model=gpt-4o status=200 latency_ms=812\n",
                "2026-09-25T10:00:02Z model=gpt-4o status=429 latency_ms=90",
                "garbage line",
                "2026-09-25T10:00:03Z model=claude-x status=200 latency_ms=640",
            ])
            # returns 3
            error_rates(conn)   # {"claude-x": 0.0, "gpt-4o": 0.5}
            ```
        ''',
        "starter": r'''
            import re
            import sqlite3


            def ingest_logs(conn, lines):
                ...


            def error_rates(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import error_rates, ingest_logs

            GOOD = [
                "2026-09-25T10:00:01Z model=gpt-4o status=200 latency_ms=812\n",
                "2026-09-25T10:00:02Z model=gpt-4o status=429 latency_ms=90",
                "garbage line",
                "2026-09-25T10:00:03Z model=claude-x status=200 latency_ms=640",
            ]

            def test_inserts_valid_lines_and_returns_count():
                conn = sqlite3.connect(":memory:")
                assert ingest_logs(conn, GOOD) == 3
                rows = conn.execute("SELECT ts, model, status, latency_ms FROM requests ORDER BY ts").fetchall()
                assert rows[0] == ("2026-09-25T10:00:01Z", "gpt-4o", 200, 812), f"first row was {rows[0]!r}"
                assert len(rows) == 3, f"{len(rows)} rows stored"

            def test_malformed_lines_are_skipped():
                conn = sqlite3.connect(":memory:")
                bad = [
                    "2026-09-25T10:00:01Z model=gpt-4o status=20 latency_ms=812",
                    "2026-09-25 10:00:01 model=gpt-4o status=200 latency_ms=812",
                    "2026-09-25T10:00:01Z model=gpt-4o status=200",
                    "2026-09-25T10:00:01Z model=gpt 4o status=200 latency_ms=812",
                    "2026-09-25T10:00:01Z model=gpt-4o status=200 latency_ms=812 extra",
                    "",
                ]
                assert ingest_logs(conn, bad) == 0

            def test_error_rates_per_model():
                conn = sqlite3.connect(":memory:")
                ingest_logs(conn, GOOD)
                got = error_rates(conn)
                assert got == {"claude-x": 0.0, "gpt-4o": 0.5}, f"got {got!r}"
                assert list(got) == ["claude-x", "gpt-4o"], f"model order was {list(got)!r}"

            def test_rates_are_rounded_and_ingest_can_run_twice():
                conn = sqlite3.connect(":memory:")
                ingest_logs(conn, ["2026-09-25T10:00:01Z model=m.1 status=500 latency_ms=1"])
                ingest_logs(conn, ["2026-09-25T10:00:02Z model=m.1 status=200 latency_ms=1",
                                   "2026-09-25T10:00:03Z model=m.1 status=201 latency_ms=1"])
                got = error_rates(conn)
                assert got == {"m.1": 0.33}, f"got {got!r}"

            def test_changes_are_committed():
                conn = sqlite3.connect("logs.db")
                ingest_logs(conn, GOOD)
                other = sqlite3.connect("logs.db")
                n = other.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
                assert n == 3, "another connection can't see the rows - did you commit?"
        ''',
        "solution": r'''
            import re
            import sqlite3

            LINE = re.compile(
                r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) model=([A-Za-z0-9._-]+) "
                r"status=(\d{3}) latency_ms=(\d+)"
            )


            def ingest_logs(conn, lines):
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS requests "
                    "(ts TEXT, model TEXT, status INTEGER, latency_ms INTEGER)"
                )
                rows = []
                for line in lines:
                    match = LINE.fullmatch(line.strip())
                    if match:
                        ts, model, status, latency = match.groups()
                        rows.append((ts, model, int(status), int(latency)))
                conn.executemany("INSERT INTO requests VALUES (?, ?, ?, ?)", rows)
                conn.commit()
                return len(rows)


            def error_rates(conn):
                rows = conn.execute(
                    """
                    SELECT model, AVG(CASE WHEN status >= 400 THEN 1.0 ELSE 0.0 END)
                    FROM requests
                    GROUP BY model
                    ORDER BY model
                    """
                ).fetchall()
                return {model: round(rate, 2) for model, rate in rows}
        ''',
        "hints": [
            "One compiled regex with groups and fullmatch per line; executemany with ? placeholders; GROUP BY for the rates.",
            "Strip each line, fullmatch it, and collect tuples of the groups (converting status and latency to int). Insert them all and commit. For rates, count errors per model divided by all rows per model - SQL can do that with a CASE expression inside AVG, or you can count in Python.",
            "1) Pattern: r'(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z) model=([A-Za-z0-9._-]+) status=(\\d{3}) latency_ms=(\\d+)'. 2) CREATE TABLE IF NOT EXISTS requests(...). 3) For each line: m = pattern.fullmatch(line.strip()); if m, append (ts, model, int(status), int(latency)). 4) executemany INSERT ... VALUES (?, ?, ?, ?); commit; return len(rows). 5) error_rates: SELECT model, AVG(CASE WHEN status >= 400 THEN 1.0 ELSE 0.0 END) FROM requests GROUP BY model ORDER BY model; build {model: round(rate, 2)}.",
        ],
    },
]
