import textwrap

TOPIC = {
    "id": "http",
    "title": "HTTP & Web APIs",
    "track": "apis-data",
    "order": 1,
    "requires": ["json", "errors"],
    "summary": """
        How programs talk over the web: requests and responses, methods, URLs and query
        strings, status codes, headers and Bearer auth, JSON bodies, timeouts, retries on
        429/5xx, and verifying signed webhooks - with the standard library.
    """,
    "concepts": ["request", "response", "HTTP methods", "URL", "query string", "urllib.parse",
                 "status codes", "headers", "Bearer token", "JSON body", "urllib.request.Request",
                 "HTTPError", "timeouts", "retries", "backoff", "Retry-After", "webhooks", "HMAC"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["http", "request", "response", "url", "query string", "urlencode", "urlparse",
                 "status code", "header", "bearer", "urlopen", "httperror", "timeout", "retry",
                 "webhook", "hmac"],
    "cards": [
        {
            "syntax": "urlparse(url)",
            "explain": "Splits a URL string into parts: .scheme, .netloc (the host), .path and .query.",
            "example": r'''
                from urllib.parse import urlparse
                parts = urlparse("https://api.example.com/v1/models?limit=2")
                print(parts.scheme, parts.netloc)
                # https api.example.com
                print(parts.path, parts.query)
                # /v1/models limit=2
            ''',
        },
        {
            "syntax": "urlencode(params)  /  parse_qs(query)",
            "explain": "urlencode builds a query string from a dict. parse_qs turns one back into a dict of lists.",
            "example": r'''
                from urllib.parse import urlencode, parse_qs
                query = urlencode({"q": "fish & chips", "limit": 5})
                print(query)
                # q=fish+%26+chips&limit=5
                print(parse_qs(query)["q"][0])
                # fish & chips
            ''',
        },
        {
            "syntax": "200 <= status <= 299",
            "explain": "Tests the group of a status code. 2xx is success, 4xx a wrong request, 5xx a server failure.",
            "example": r'''
                for status in [200, 404, 503]:
                    ok = 200 <= status <= 299
                    retry = status == 429 or 500 <= status <= 599
                    print(status, ok, retry)
                # 200 True False
                # 404 False False
                # 503 False True
            ''',
        },
        {
            "syntax": "Request(url, data=body, headers={...}, method=\"POST\")",
            "explain": "Stores one request without sending it. data must be bytes. urlopen(req, timeout=5) sends it.",
            "example": r'''
                import json
                from urllib.request import Request
                body = json.dumps({"prompt": "hi"}).encode("utf-8")
                req = Request("https://api.example.com/v1/chat", data=body,
                              headers={"Authorization": "Bearer sk-demo"},
                              method="POST")
                print(req.get_method(), req.get_header("Authorization"), req.data)
                # POST Bearer sk-demo b'{"prompt": "hi"}'
            ''',
        },
        {
            "syntax": "except HTTPError as err:",
            "explain": "urlopen raises HTTPError for a 4xx or 5xx response. err.code is the status, err.read() the body.",
            "example": r'''
                import io
                from urllib.error import HTTPError
                body = io.BytesIO(b"slow down")
                try:
                    raise HTTPError("https://x.io/v1", 429, "Too Many", {}, body)
                except HTTPError as err:
                    print(err.code, err.read().decode("utf-8"))
                # 429 slow down
            ''',
        },
        {
            "syntax": "hmac.new(key, body, hashlib.sha256).hexdigest()",
            "explain": "Computes the signature of a body with a secret key. Compare two signatures with hmac.compare_digest.",
            "example": r'''
                import hashlib
                import hmac
                sig = hmac.new(b"secret", b"{}", hashlib.sha256).hexdigest()
                other = hmac.new(b"secret", b"{ }", hashlib.sha256).hexdigest()
                print(len(sig), hmac.compare_digest(sig, sig))
                # 64 True
                print(hmac.compare_digest(sig, other))
                # False
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: HTTP

### Requests and responses

**HTTP** is the set of rules that programs use to exchange messages over the web. The
**client** is the program that sends a message, called a **request**. The **server** is
the program that receives it and sends back a **response**. An **API** is the set of
requests that a server accepts from other programs. Every LLM API call is one request and
one response.

A request has four parts:

- The **method** names the action. `GET` reads data, `POST` sends data, `PUT` and `PATCH`
  update data, `DELETE` removes data.
- The **URL** is the address the request goes to.
- The **headers** are name and value pairs that describe the request. One of them carries
  your API key, the secret string that tells the server who you are.
- The **body** is the data you send. `GET` requests usually have no body.

Step through one chat request to see the exact data at each stage.

```diagram
{"type":"flow","title":"One HTTP request and its response","steps":[
{"label":"Encode the body","detail":"json.dumps turns the dict into JSON text. .encode(\"utf-8\") turns that text into bytes.","code":"payload = {\"model\": \"small\", \"messages\": [{\"role\": \"user\", \"content\": \"hi\"}]}\nbody = json.dumps(payload).encode(\"utf-8\")\n# b'{\"model\": \"small\", \"messages\": [{\"role\": \"user\", \"content\": \"hi\"}]}'"},
{"label":"Build the Request","detail":"Request stores the URL, the method, the headers and the body. Nothing is sent yet.","code":"req = Request(\"https://api.example.com/v1/chat\", data=body, method=\"POST\",\n              headers={\"Authorization\": \"Bearer sk-demo\", \"Content-Type\": \"application/json\"})"},
{"label":"Send the request","detail":"urlopen(req, timeout=10) connects to the host and sends the request line, the header lines, an empty line and the body.","code":"POST /v1/chat HTTP/1.1\nHost: api.example.com\nAuthorization: Bearer sk-demo\nContent-Type: application/json\nContent-Length: 67\n\n{\"model\": \"small\", \"messages\": [{\"role\": \"user\", \"content\": \"hi\"}]}"},
{"label":"Receive the response","detail":"The server answers with a status line, header lines, an empty line and a body. The status code here is 200.","code":"HTTP/1.1 200 OK\nContent-Type: application/json\nContent-Length: 47\n\n{\"reply\": \"Hi!\", \"usage\": {\"total_tokens\": 12}}"},
{"label":"Parse the JSON","detail":"resp.status is 200. resp.read() returns the body as bytes. json.loads turns those bytes into a dict.","code":"data = json.loads(resp.read())\n# {'reply': 'Hi!', 'usage': {'total_tokens': 12}}\nprint(data[\"reply\"])\n# Hi!"}
]}
```

### URLs and query strings

A URL has a **scheme** (`https`), a **host** (`api.example.com`), a **path**
(`/v1/search`) and an optional **query string**: `key=value` pairs after a `?`, joined
by `&`. `urlparse` splits a URL. `urlencode` builds a query string from a dict.
`parse_qs` turns a query string into a dict of lists.

```python
from urllib.parse import urlparse, urlencode, parse_qs

parts = urlparse("https://api.example.com/v1/search?q=cats&limit=5")
print(parts.scheme, parts.netloc, parts.path, parts.query)
# https api.example.com /v1/search q=cats&limit=5
print(urlencode({"q": "hello world", "n": 2}))
# q=hello+world&n=2
print(parse_qs("q=a&q=b&n=2"))
# {'q': ['a', 'b'], 'n': ['2']}
```

### Status codes

Every response has a three-digit **status code**. The first digit gives the kind of result.

- 2xx means success: `200` OK, `201` Created, `204` No Content.
- 3xx means a redirect: the data is at another URL.
- 4xx means the request is wrong: `400` bad request, `401` missing or bad key, `403`
  forbidden, `404` not found, `429` too many requests.
- 5xx means the server failed: `500`, `502`, `503`.

### Headers and bodies

`Authorization: Bearer <key>` carries your API key. `Bearer` is a fixed word that tells the server the text after it is an access key. `Content-Type: application/json`
says the body is JSON. `Retry-After` is a response header that gives a number of seconds
to wait. Header names are case-insensitive.

A body is **bytes**: a sequence of raw byte values, not a `str`. Call
`.encode("utf-8")` on JSON text before you send it. `json.loads` accepts the bytes that
come back.

```python
import json
from urllib.request import Request

payload = {"model": "small", "messages": [{"role": "user", "content": "hi"}]}
body = json.dumps(payload).encode("utf-8")
req = Request(
    "https://api.example.com/v1/chat",
    data=body,
    headers={"Authorization": "Bearer sk-demo", "Content-Type": "application/json"},
    method="POST",
)
print(req.get_method(), req.full_url)
# POST https://api.example.com/v1/chat
print(req.data)
# b'{"model": "small", "messages": [{"role": "user", "content": "hi"}]}'
```

`Request` only stores the data. `urlopen(req, timeout=10)` sends it and returns the
response. Use it in a `with` block, read `resp.status`, and parse the body with
`json.loads(resp.read())`.

### Errors and timeouts

For a 4xx or 5xx response, `urlopen` raises `urllib.error.HTTPError`. The exception has
`.code`, `.headers` and `.read()`. When the server cannot be reached, `urlopen` raises
`urllib.error.URLError`. When the server accepts the connection but does not answer within
`timeout` seconds, it raises `TimeoutError`. When the connection itself takes longer than
`timeout`, you get a `URLError`.

The example builds an `HTTPError` by hand, so it runs without a server. The arguments are
the URL, the status code, the status text, the headers and the body. `io.BytesIO(b"...")`
makes an object whose `.read()` method returns those bytes. `issubclass(A, B)` is `True`
when class `A` is a subclass of class `B`.

```python
import io
import json
from urllib.error import HTTPError, URLError

err = HTTPError("https://api.example.com/v1/chat", 429, "Too Many Requests",
                {"Retry-After": "2"}, io.BytesIO(b'{"error": "slow down"}'))
try:
    raise err
except HTTPError as e:
    print(e.code)
    # 429
    print(e.headers.get("Retry-After"))
    # 2
    print(json.loads(e.read()))
    # {'error': 'slow down'}
print(issubclass(HTTPError, URLError))
# True
```

### Retries

Retry `429` and 5xx responses, because those failures are often temporary. Do not retry
`400`, `401` or `404`: the same request fails again. Wait between attempts.
**Exponential backoff** doubles the wait after each failed attempt. If the response has
a `Retry-After` header, wait that many seconds instead. Pass `sleep` in as a parameter so
tests can replace it and finish without waiting.

```python
def retry_wait(status, attempt, retry_after=None):
    if status != 429 and not 500 <= status <= 599:
        return None
    if retry_after is not None:
        return float(retry_after)
    return 0.5 * 2 ** attempt

print(retry_wait(503, 0), retry_wait(503, 1), retry_wait(503, 2))
# 0.5 1.0 2.0
print(retry_wait(429, 0, "2"))
# 2.0
print(retry_wait(404, 0))
# None
```

### Webhooks

A **webhook** is a request that a service sends to your server when an event happens.
Anyone can send a request to your URL, so the sender adds a signature that proves who
sent the body. The signature is an **HMAC**: a value computed from a secret key and the
body. `hmac.new(key, body, hashlib.sha256).hexdigest()` returns it as a string of 64
characters. You compute it again and compare with `hmac.compare_digest`. A body with one
extra byte gives a different value. Check a signed timestamp as well, so an old request
cannot be sent again.

```python
import hashlib
import hmac

secret = b"whsec_demo"
body = b'{"event": "batch.completed"}'
signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
print(len(signature))
# 64
changed = hmac.new(secret, body + b" ", hashlib.sha256).hexdigest()
print(hmac.compare_digest(signature, changed))
# False
```

### Common mistakes

- `urlopen(url)` without `timeout` can wait forever when the server stops answering.
  Always pass `timeout`.
- `except URLError` placed before `except HTTPError` catches both, because `HTTPError`
  is a subclass of `URLError`. Put `except HTTPError` first.
- `Request(url, data="text")` fails when it is sent, because `data` must be bytes.
- `"Bearer" + key` has no space after `Bearer`, so the server answers `401`.
- A query string built with an f-string breaks when a value contains a space or `&`.
  Use `urlencode`.

Real projects often use `httpx` or `requests` (ready-made libraries for HTTP).
An LLM **SDK** (a ready-made library from the company that runs the LLM service) makes
these HTTP calls for you.
'''

# Shared by every check that talks to a real (local) server.
_SERVER = r'''
import json, socket, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class _Server:
    """Local test server on a random free port. handler(req) -> (status, headers, body)."""

    def __init__(self, handler):
        self.handler = handler
        self.requests = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def _serve(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                req = {"method": self.command, "path": self.path, "body": body,
                       "headers": {k.lower(): v for k, v in self.headers.items()}}
                outer.requests.append(req)
                status, headers, payload = outer.handler(req)
                if not isinstance(payload, (bytes, str)):
                    payload = json.dumps(payload)
                    headers = {"Content-Type": "application/json", **headers}
                if isinstance(payload, str):
                    payload = payload.encode("utf-8")
                try:
                    self.send_response(status)
                    for key, value in headers.items():
                        self.send_header(key, str(value))
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except OSError:
                    pass

            do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _serve

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.httpd.daemon_threads = True
        self.url = "http://127.0.0.1:%d" % self.httpd.server_address[1]

    def __enter__(self):
        threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.01},
                         daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port

'''


def _t(src):
    return _SERVER + textwrap.dedent(src)


EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "http-s1",
        "title": "Taking a URL apart",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Requests, responses and URLs

            **HTTP** is the set of rules that programs use to exchange messages over the web.
            The **client** is the program that sends a message. That message is a **request**.
            The **server** is the program that receives the request and sends back a
            **response**. An **API** is the set of requests that a server accepts from other
            programs. When your code calls an LLM API, your code is the client. Each call
            is one request and one response.

            A request names the address it goes to. That address is the **URL**. The URL
            `https://example.com/docs?page=3` has four parts:

            - The **scheme** is `https`. It names the rules used for the exchange. `https` is
              HTTP with encryption: only the client and the server can read the messages.
            - The **host** is `example.com`. It names the server.
            - The **path** is `/docs`. It names one thing on that server, such as a page.
            - The **query string** is `page=3`. It holds extra options, written after a `?`.

            `urlparse` from the `urllib.parse` module splits a URL string into these parts.
            It names the host part `netloc`, short for network location.

            ```python
            from urllib.parse import urlparse

            parts = urlparse("https://example.com/docs?page=3")
            print(parts.scheme)
            # https
            print(parts.netloc)
            # example.com
            print(parts.path)
            # /docs
            print(parts.query)
            # page=3
            ```

            The path keeps its leading `/`. The query does not include the `?`.

            `urlencode` does the opposite job for the query string. It takes a dict and
            returns `key=value` pairs joined by `&`. A space is not allowed in a URL, so
            `urlencode` replaces each space with `+`.

            ```python
            from urllib.parse import urlencode

            print(urlencode({"lang": "en", "page": 3}))
            # lang=en&page=3
            print(urlencode({"prompt": "count tokens"}))
            # prompt=count+tokens
            ```
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            from urllib.parse import urlparse, urlencode

            url = urlparse("https://api.example.com/v1/models?limit=2")
            print(url.scheme)
            print(url.netloc)
            print(url.path)
            print(url.query)
            print(urlencode({"q": "hello world", "page": 2}))
        ''',
        "solution": r'''
            https
            api.example.com
            /v1/models
            limit=2
            q=hello+world&page=2
        ''',
        "explanation": r'''
            `urlparse` splits the URL: scheme `https`, netloc (host) `api.example.com`, path
            `/v1/models` (with its leading slash), query `limit=2` (without the `?`).
            `urlencode` joins `key=value` pairs with `&` and encodes the space as `+`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "urlparse splits a URL into named parts: scheme, netloc, path, query.",
            "The scheme is before ://, the netloc is the host, the path starts with / and stops at ?, the query is after ?.",
            "Print each part in order, then remember urlencode writes key=value pairs joined by & with spaces turned into +.",
        ],
    },
    {
        "id": "http-s2",
        "title": "Build a URL with a query string",
        "difficulty": 0,
        "lesson": r'''
            ## Query strings

            Many API requests carry options in the URL, after a `?`. That part is the
            **query string**, for example `?q=cats&limit=5`. Each option is a `key=value`
            pair. The pairs are joined with `&`.

            The characters `&` and `=` separate the pairs, so a value must not contain them
            as they are. A value must not contain a space either. `urlencode` takes a dict
            and returns a query string with those characters replaced.

            ```python
            from urllib.parse import urlencode

            params = {"q": "fish & chips", "limit": 5}
            query = urlencode(params)
            print(query)
            # q=fish+%26+chips&limit=5
            print("https://api.example.com/search?" + query)
            # https://api.example.com/search?q=fish+%26+chips&limit=5
            ```

            Each space became `+`. The `&` inside the value became `%26`. This replacement
            is called **percent-encoding**: a `%` followed by the character's code number
            written in **hexadecimal** (base 16, with the digits 0-9 and A-F). The code
            number of `&` is 38, which is `26` in hexadecimal. The server decodes `%26`
            back to `&`. `urlencode` does not add the `?`, so you add it yourself.

            Do not build the query with an f-string such as `f"?q={text}"`. With the text
            `fish & chips` the server reads the `&` as the start of a new pair, so `q` is
            cut short. Use `urlencode` for every query string.
        ''',
        "prompt": r'''
            A search API takes its options in the query string. Replace the `___`.

            **Write:** `build_url(base, path, params)`

            - `base`: the server address, e.g. `"https://api.example.com"`
            - `path`: e.g. `"/v1/search"`
            - `params`: a non-empty dict of options, e.g. `{"q": "hello world", "limit": 5}`
            - **Returns:** a string: `base` + `path` + `"?"` + the URL-encoded params (in the dict's order)

            **Rules**
            - Encode the params with `urllib.parse.urlencode` (spaces become `+`, `&` becomes `%26`).

            **Examples**
            ```python
            build_url("https://api.example.com", "/v1/search", {"q": "hello world", "limit": 5})
            # returns "https://api.example.com/v1/search?q=hello+world&limit=5"
            build_url("https://x.io", "/s", {"q": "a&b"})
            # returns "https://x.io/s?q=a%26b"
            ```
        ''',
        "starter": r'''
            from urllib.parse import urlencode

            def build_url(base, path, params):
                query = ___
                return f"{base}{path}?{query}"
        ''',
        "tests": r'''
            from solution import build_url

            def test_spaces_and_numbers():
                got = build_url("https://api.example.com", "/v1/search", {"q": "hello world", "limit": 5})
                assert got == "https://api.example.com/v1/search?q=hello+world&limit=5", f"got {got!r}"

            def test_ampersand_is_encoded():
                got = build_url("https://x.io", "/s", {"q": "a&b"})
                assert got == "https://x.io/s?q=a%26b", f"got {got!r}"

            def test_single_param():
                got = build_url("http://localhost:8000", "/health", {"verbose": "yes"})
                assert got == "http://localhost:8000/health?verbose=yes", f"got {got!r}"
        ''',
        "solution": r'''
            from urllib.parse import urlencode

            def build_url(base, path, params):
                query = urlencode(params)
                return f"{base}{path}?{query}"
        ''',
        "hints": [
            "urlencode is already imported. It turns a dict into a query string.",
            "The blank should be the encoded version of the params dict.",
            "Replace ___ with a call to urlencode, passing params.",
        ],
    },
    {
        "id": "http-s3",
        "title": "What does this status code mean?",
        "difficulty": 0,
        "lesson": r'''
            ## Status codes

            Every response starts with a **status code**: a three-digit number that says how
            the request went. The first digit gives the group of the code.

            - 2xx means success. Examples: `200` OK, `201` Created, `204` No Content.
            - 3xx means a **redirect**: the data is at another URL.
            - 4xx means the request is wrong. Examples: `400` bad request, `401` missing or
              bad API key, `404` not found, `429` too many requests.
            - 5xx means the server failed. Examples: `500` internal error, `502` and `503`
              temporarily unavailable.

            Here `2xx` stands for every code from 200 to 299.

            The `//` operator divides and drops the remainder. `code // 100` gives the first
            digit of a three-digit code.

            ```python
            for code in [200, 404, 503]:
                family = code // 100
                print(code, "family", family)
            # 200 family 2
            # 404 family 4
            # 503 family 5
            ```

            Step through the loop to see `family` change for each code.

            ```diagram
            {"type": "trace", "title": "First digit of each status code", "code": ["for code in [200, 404, 503]:", "    family = code // 100", "    print(code, \"family\", family)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"code": "200"}, "out": ""},
              {"line": 3, "vars": {"code": "200", "family": "2"}, "out": ""},
              {"line": 1, "vars": {"code": "200", "family": "2"}, "out": "200 family 2\n"},
              {"line": 2, "vars": {"code": "404", "family": "2"}, "out": "200 family 2\n"},
              {"line": 3, "vars": {"code": "404", "family": "4"}, "out": "200 family 2\n"},
              {"line": 1, "vars": {"code": "404", "family": "4"}, "out": "200 family 2\n404 family 4\n"},
              {"line": 2, "vars": {"code": "503", "family": "4"}, "out": "200 family 2\n404 family 4\n"},
              {"line": 3, "vars": {"code": "503", "family": "5"}, "out": "200 family 2\n404 family 4\n"},
              {"line": 1, "vars": {"code": "503", "family": "5"}, "out": "200 family 2\n404 family 4\n503 family 5\n"},
              {"line": null, "vars": {"code": "503", "family": "5"}, "out": "200 family 2\n404 family 4\n503 family 5\n"}
            ]}
            ```

            You can also test a group with a chained comparison. `400 <= code <= 499` is
            `True` when `code` is between 400 and 499, with both ends included.

            ```python
            code = 429
            print(400 <= code <= 499)
            # True
            print(500 <= code <= 599)
            # False
            ```

            The two error groups need different reactions. After a 4xx you fix the request.
            After a 5xx the same request often works a moment later.
        ''',
        "prompt": r'''
            Your logs should show a readable label next to each status code. Finish the function.

            **Write:** `status_kind(code)`

            - `code`: an int, e.g. `200`
            - **Returns:** one of these strings:
              `"success"` for 200-299, `"redirect"` for 300-399, `"client error"` for 400-499,
              `"server error"` for 500-599, `"unknown"` for anything else

            **Examples**
            ```python
            status_kind(200)    # returns "success"
            status_kind(429)    # returns "client error"
            status_kind(503)    # returns "server error"
            status_kind(99)     # returns "unknown"
            ```
        ''',
        "starter": r'''
            def status_kind(code):
                if 200 <= code <= 299:
                    return "success"
                ...
        ''',
        "tests": r'''
            from solution import status_kind

            def test_success_codes():
                for code in (200, 201, 204, 299):
                    assert status_kind(code) == "success", f"{code} -> {status_kind(code)!r}"

            def test_redirect():
                assert status_kind(301) == "redirect", f"got {status_kind(301)!r}"

            def test_client_errors():
                for code in (400, 401, 404, 429, 499):
                    assert status_kind(code) == "client error", f"{code} -> {status_kind(code)!r}"

            def test_server_errors():
                for code in (500, 502, 503, 599):
                    assert status_kind(code) == "server error", f"{code} -> {status_kind(code)!r}"

            def test_unknown():
                for code in (99, 600, 0):
                    assert status_kind(code) == "unknown", f"{code} -> {status_kind(code)!r}"
        ''',
        "solution": r'''
            def status_kind(code):
                if 200 <= code <= 299:
                    return "success"
                if 300 <= code <= 399:
                    return "redirect"
                if 400 <= code <= 499:
                    return "client error"
                if 500 <= code <= 599:
                    return "server error"
                return "unknown"
        ''',
        "hints": [
            "The first branch is done. Add one range check per family, the same way.",
            "Check 300-399, 400-499 and 500-599 in turn, each returning its label. If nothing matched, return the fallback.",
            "Replace ... with three more `if low <= code <= high: return \"label\"` checks and a final `return \"unknown\"`.",
        ],
    },
    {
        "id": "http-s4",
        "title": "Fix: the API key header",
        "difficulty": 0,
        "lesson": r'''
            ## Headers

            Besides the URL, a request carries **headers**: name and value pairs that give
            the server extra information about the request. Each header is sent as one line
            of text in the form `Name: value`.

            Headers are name and value pairs, so in Python you write them as a dict. Both the
            names and the values are strings.

            ```python
            api_key = "sk-demo-123"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            for name, value in headers.items():
                print(f"{name}: {value}")
            # Authorization: Bearer sk-demo-123
            # Content-Type: application/json
            ```

            Click a key to read the value stored for that header.

            ```diagram
            {"type":"dict","title":"The headers dict","name":"headers","entries":[["Authorization","Bearer sk-demo-123"],["Content-Type","application/json"]]}
            ```

            The `Authorization` header carries your API key. Most LLM APIs expect the value
            `Bearer <key>`. The word `Bearer` tells the server that the text after it is a
            secret key, and that the server accepts any request that carries this key. A key
            sent this way is called a **Bearer token**.

            The `Content-Type` header names the format of the request body.
            `application/json` means the body is JSON.

            The format of the `Authorization` value is exact: the word `Bearer`, one space,
            then the key. The server checks the whole value. Without the space the value is
            wrong and the server answers `401 Unauthorized`.

            Do not print or log a real API key. Anyone who reads the log can use it.
        ''',
        "prompt": r'''
            This helper builds the headers for every API call, but the server keeps answering
            `401 Unauthorized`. Find and fix the bug.

            **Write:** `auth_headers(api_key)`

            - `api_key`: a string, e.g. `"sk-123"`
            - **Returns:** a dict with exactly two headers:
              `"Authorization"` -> `"Bearer "` followed by the key, and
              `"Content-Type"` -> `"application/json"`

            **Examples**
            ```python
            auth_headers("sk-123")
            # returns {"Authorization": "Bearer sk-123", "Content-Type": "application/json"}
            ```
        ''',
        "starter": r'''
            def auth_headers(api_key):
                return {
                    "Authorization": "Bearer" + api_key,
                    "Content-Type": "application/json",
                }
        ''',
        "tests": r'''
            from solution import auth_headers

            def test_bearer_format():
                got = auth_headers("sk-123")
                assert got.get("Authorization") == "Bearer sk-123", f"Authorization is {got.get('Authorization')!r}"

            def test_exact_headers():
                got = auth_headers("abc")
                assert got == {"Authorization": "Bearer abc", "Content-Type": "application/json"}, f"got {got!r}"
        ''',
        "solution": r'''
            def auth_headers(api_key):
                return {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
        ''',
        "hints": [
            "Print auth_headers(\"sk-123\") and look very closely at the Authorization value.",
            "Compare it with the required format: the word Bearer, a space, then the key.",
            "Add the missing space between \"Bearer\" and the key (for example with an f-string: f\"Bearer {api_key}\").",
        ],
    },
    {
        "id": "http-s5",
        "title": "A JSON request body",
        "difficulty": 0,
        "lesson": r'''
            ## The request body

            The **method** of a request names the action. A `GET` request asks the server for
            data and usually has no body. A `POST` request sends data, such as a chat
            message or a document to embed. That data is the **body** of the request. For
            APIs the body is almost always JSON.

            A network connection transfers **bytes**: a sequence of numbers from 0 to 255.
            It does not transfer Python strings. Python has a separate type for this, also
            called `bytes`. A bytes value prints with a `b` in front of the quotes.

            Sending a dict takes two steps. `json.dumps` turns the dict into JSON text.
            The string method `.encode("utf-8")` turns that text into bytes.

            ```python
            import json

            payload = {"model": "small", "messages": [{"role": "user", "content": "café?"}]}
            text = json.dumps(payload)
            body = text.encode("utf-8")
            print(type(text).__name__, type(body).__name__)
            # str bytes
            print(json.loads(body) == payload)
            # True
            ```

            **UTF-8** is an encoding: a rule for turning characters into bytes. It covers
            every character, including accented letters. `json.loads` accepts bytes as well
            as a string.

            `str(payload)` does not produce JSON. It produces Python syntax, with single
            quotes, `True` and `None`. A server that expects JSON rejects that text.

            ```python
            import json

            payload = {"stream": True, "stop": None}
            print(str(payload))
            # {'stream': True, 'stop': None}
            print(json.dumps(payload))
            # {"stream": true, "stop": null}
            ```
        ''',
        "prompt": r'''
            Before a chat request goes over the wire, its payload must become bytes.

            **Write:** `json_body(payload)`

            - `payload`: a dict, e.g. `{"model": "small", "stream": False}`
            - **Returns:** `bytes` containing the payload as JSON, encoded with UTF-8

            **Rules**
            - The result must be of type `bytes` (not `str`).
            - It must be valid JSON that `json.loads` turns back into an equal dict (including non-English text like `"café"`).

            **Examples**
            ```python
            json_body({"stream": False})        # returns b'{"stream": false}'
            json.loads(json_body({"q": "café"})) == {"q": "café"}   # True
            ```
        ''',
        "starter": r'''
            import json

            def json_body(payload):
                ...
        ''',
        "tests": r'''
            import json
            from solution import json_body

            def test_returns_bytes():
                got = json_body({"stream": False})
                assert isinstance(got, bytes), f"expected bytes, got {type(got).__name__}"

            def test_is_valid_json():
                payload = {"model": "small", "stream": False, "messages": [{"role": "user", "content": "hi"}]}
                got = json.loads(json_body(payload))
                assert got == payload, f"decoded back to {got!r}"

            def test_non_english_text_survives():
                got = json.loads(json_body({"q": "café 日本"}).decode("utf-8"))
                assert got == {"q": "café 日本"}, f"decoded back to {got!r}"
        ''',
        "solution": r'''
            import json

            def json_body(payload):
                return json.dumps(payload).encode("utf-8")
        ''',
        "hints": [
            "Two conversions: dict to JSON text, then text to bytes.",
            "json.dumps gives you a JSON string; strings have a method that turns them into bytes.",
            "Return json.dumps(payload) followed by .encode(\"utf-8\").",
        ],
    },
    {
        "id": "http-s6",
        "title": "Read a query parameter",
        "difficulty": 0,
        "lesson": r'''
            ## Reading a query string

            Sometimes your code receives a URL and needs one option from it. Examples are the
            link a login service sends the user back to, or a link to the next page of
            results. `urllib.parse` has functions for this direction too.

            `urlparse(url).query` gives the query string. `parse_qs`, short for "parse query
            string", turns that string into a dict.

            ```python
            from urllib.parse import urlparse, parse_qs

            url = "https://app.io/callback?code=abc123&tag=a&tag=b&q=hello+world"
            query = urlparse(url).query
            print(query)
            # code=abc123&tag=a&tag=b&q=hello+world
            params = parse_qs(query)
            print(params)
            # {'code': ['abc123'], 'tag': ['a', 'b'], 'q': ['hello world']}
            print(params["code"][0])
            # abc123
            print(params.get("missing"))
            # None
            ```

            Every value in the dict is a list. A key can appear more than once in a query
            string, as `tag` does here, and the list holds each value in order. `parse_qs`
            also decodes each value: `hello+world` became `hello world`, and `%26` would
            become `&`.

            `params["code"]` is the list `['abc123']`, not the string. Index it with `[0]`
            to get the string. `params["missing"]` raises `KeyError` because the key is not
            in the dict. Use `.get()` for a key that may be missing.
        ''',
        "prompt": r'''
            An OAuth-style callback URL carries values in its query string. Pull one out.

            **Write:** `get_param(url, name, default=None)`

            - `url`: a full URL string, e.g. `"https://x.io/s?q=hello+world&page=2"`
            - `name`: the parameter name, e.g. `"q"`
            - `default`: what to return if the parameter is missing
            - **Returns:** the parameter's value as a decoded string; if it appears several
              times, the FIRST value; if it's missing, `default`

            **Examples**
            ```python
            get_param("https://x.io/s?q=hello+world&page=2", "q")      # returns "hello world"
            get_param("https://x.io/s?q=hello+world&page=2", "page")   # returns "2"  (a string)
            get_param("https://x.io/s?tag=a&tag=b", "tag")             # returns "a"
            get_param("https://x.io/s?q=x", "page", "1")               # returns "1"
            ```
        ''',
        "starter": r'''
            from urllib.parse import urlparse, parse_qs

            def get_param(url, name, default=None):
                ...
        ''',
        "tests": r'''
            from solution import get_param

            URL = "https://x.io/s?q=hello+world&page=2"

            def test_decodes_value():
                got = get_param(URL, "q")
                assert got == "hello world", f"got {got!r}"

            def test_value_is_a_string():
                got = get_param(URL, "page")
                assert got == "2", f"got {got!r}"

            def test_first_of_repeated():
                got = get_param("https://x.io/s?tag=a&tag=b", "tag")
                assert got == "a", f"got {got!r}"

            def test_missing_uses_default():
                assert get_param("https://x.io/s?q=x", "page", "1") == "1"
                assert get_param("https://x.io/s", "q") is None
        ''',
        "solution": r'''
            from urllib.parse import urlparse, parse_qs

            def get_param(url, name, default=None):
                values = parse_qs(urlparse(url).query).get(name)
                if not values:
                    return default
                return values[0]
        ''',
        "hints": [
            "urlparse gets you the query part; parse_qs turns it into a dict.",
            "The dict's values are lists. Look the name up with .get() and handle the missing case.",
            "values = parse_qs(urlparse(url).query).get(name); if values is None (or empty) return default; otherwise return values[0].",
        ],
    },
    {
        "id": "http-s7",
        "title": "Anatomy of a Request object",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The Request object

            `urllib.request.Request` is a standard library class that holds everything about
            one request: the URL, the method, the headers and the body. Creating a `Request`
            object sends nothing. It only stores the data.

            ```python
            from urllib.request import Request

            req = Request("https://api.example.com/v1/embed",
                          data=b'{"input": "hi"}',
                          headers={"Content-Type": "application/json"},
                          method="POST")
            print(req.get_method())
            # POST
            print(req.full_url)
            # https://api.example.com/v1/embed
            print(req.data)
            # b'{"input": "hi"}'
            ```

            `data` is the body and it must be bytes. `get_method()` returns the method the
            request will use. `full_url` is the URL you passed. `get_header(name)` returns
            the value of one header.

            If you leave out `method`, `get_method()` picks one from the body. It returns
            `"GET"` when `data` is `None` and `"POST"` when you passed `data`.

            ```python
            from urllib.request import Request

            print(Request("https://api.example.com/v1/files").get_method())
            # GET
            print(Request("https://api.example.com/v1/files", data=b"{}").get_method())
            # POST
            print(Request("https://api.example.com/v1/files/7", method="DELETE").get_method())
            # DELETE
            ```

            You send a request with `urlopen(req, timeout=...)`, which returns the response.
            A later exercise covers that step.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            from urllib.request import Request

            get_req = Request("https://api.example.com/v1/models")
            post_req = Request("https://api.example.com/v1/chat", data=b'{"x": 1}',
                               headers={"Authorization": "Bearer sk-123"})
            print(get_req.get_method())
            print(post_req.get_method())
            print(post_req.full_url)
            print(post_req.get_header("Authorization"))
        ''',
        "solution": r'''
            GET
            POST
            https://api.example.com/v1/chat
            Bearer sk-123
        ''',
        "explanation": r'''
            No `method` was given, so `Request` decides: no body means `GET`, a `data` body
            means `POST`. `full_url` is the URL you passed, and `get_header` returns the
            header value you set.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Neither request passes method=..., so Request picks the method itself.",
            "The rule: a request with data (a body) is a POST, one without is a GET.",
            "Line 1 and 2 are the two methods; line 3 is the URL of post_req; line 4 is the Authorization value exactly as given.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "http-1",
        "title": "GET some JSON",
        "difficulty": 1,
        "lesson": r'''
            ## Sending a request with urlopen

            `urllib.request.urlopen` sends a request and returns a response object. You can
            pass it a URL string. It then sends a `GET` request to that URL.

            The response object has the status code in `resp.status` and the body in
            `resp.read()`. The body is bytes. `json.loads` accepts bytes and returns the
            parsed value.

            The example below uses a `data:` URL. A `data:` URL holds its content inside the
            URL itself, so `urlopen` returns that content without contacting a server. The
            reading and parsing steps are the same as for an `http:` URL.

            ```python
            import json
            from urllib.request import urlopen

            url = 'data:application/json,{"reply": "Hi!", "tokens": 12}'
            with urlopen(url, timeout=5) as resp:
                raw = resp.read()
                again = resp.read()
            print(raw)
            # b'{"reply": "Hi!", "tokens": 12}'
            print(again)
            # b''
            data = json.loads(raw)
            print(data["reply"], data["tokens"])
            # Hi! 12
            ```

            - `with urlopen(...) as resp:` closes the connection when the block ends.
            - `resp.read()` returns the whole body the first time. The second call returns
              `b''` because the body has already been read. Store the result in a variable.
            - `resp.status` is the status code of an HTTP response, for example `200`.
            - `timeout=5` makes `urlopen` stop waiting after 5 seconds. Always pass a timeout.

            In this exercise the checks start a small web server on your own machine at
            `http://127.0.0.1:<port>` and pass its URL to your function. The address
            `127.0.0.1` always means your own machine, so no internet connection is needed.
            A **port** is a number after the host that selects one program on that machine.
        ''',
        "prompt": r'''
            List the models an API offers by calling its endpoint.

            **Write:** `get_json(url)`

            - `url`: a full URL string, e.g. `"http://127.0.0.1:8000/v1/models"`
            - **Returns:** the response body parsed from JSON (usually a dict)

            **Rules**
            - Send a `GET` request with `urllib.request.urlopen`, passing a `timeout` (e.g. `5`).
            - Parse the body with `json.loads`.

            **Examples**
            ```python
            get_json(server + "/v1/models")
            # returns {"models": ["small", "large"]}  (whatever JSON the server sent)
            ```
        ''',
        "starter": r'''
            import json
            from urllib.request import urlopen

            def get_json(url):
                ...
        ''',
        "tests": _t(r'''
            from solution import get_json

            def test_returns_parsed_json():
                with _Server(lambda req: (200, {}, {"models": ["small", "large"]})) as srv:
                    got = get_json(srv.url + "/v1/models")
                assert got == {"models": ["small", "large"]}, f"got {got!r}"

            def test_sends_get_to_the_right_path():
                with _Server(lambda req: (200, {}, {"ok": True})) as srv:
                    get_json(srv.url + "/v1/models?limit=2")
                    reqs = srv.requests
                assert len(reqs) == 1, f"server got {len(reqs)} requests"
                assert reqs[0]["method"] == "GET", f"method was {reqs[0]['method']}"
                assert reqs[0]["path"] == "/v1/models?limit=2", f"path was {reqs[0]['path']}"

            def test_non_english_text():
                with _Server(lambda req: (200, {}, {"text": "café 日本"})) as srv:
                    got = get_json(srv.url + "/t")
                assert got == {"text": "café 日本"}, f"got {got!r}"

            def test_uses_a_timeout():
                assert "timeout" in source(), "pass a timeout to urlopen"
        '''),
        "solution": r'''
            import json
            from urllib.request import urlopen

            def get_json(url):
                with urlopen(url, timeout=5) as resp:
                    return json.loads(resp.read())
        ''',
        "hints": [
            "urlopen(url, timeout=5) sends the request; use it in a with block.",
            "Inside the with block, read the body and turn the JSON into a Python value.",
            "with urlopen(url, timeout=5) as resp: return json.loads(resp.read())",
        ],
    },
    {
        "id": "http-2",
        "title": "POST JSON with an API key",
        "difficulty": 1,
        "research": {
            "note": "Skim the `urllib.request.Request` docs (the `data`, `headers` and `method` arguments), then look at how httpx does the same POST in one line - that's what most real projects use.",
            "links": [
                {"title": "urllib.request.Request - Python docs", "url": "https://docs.python.org/3/library/urllib.request.html#urllib.request.Request"},
                {"title": "httpx - QuickStart", "url": "https://www.python-httpx.org/quickstart/"},
                {"title": "Requests - Quickstart", "url": "https://requests.readthedocs.io/en/latest/user/quickstart/"},
            ],
        },
        "lesson": r'''
            ## A full API call: method, headers and body

            Almost every LLM API call has the same three parts. The method is `POST`. The
            body is JSON. The API key goes in an `Authorization` header. You put all three
            into one `Request` object and pass that object to `urlopen`.

            ```python
            import json
            from urllib.request import Request

            body = json.dumps({"prompt": "hi"}).encode("utf-8")
            req = Request("https://api.example.com/v1/complete",
                          data=body,
                          headers={"Authorization": "Bearer sk-demo",
                                   "Content-Type": "application/json"},
                          method="POST")
            print(req.get_method())
            # POST
            print(req.data)
            # b'{"prompt": "hi"}'
            print(req.header_items())
            # [('Authorization', 'Bearer sk-demo'), ('Content-type', 'application/json')]
            ```

            `urlopen` accepts a `Request` object in place of a URL string. Sending and
            reading work the same way as for a `GET`: open it in a `with` block, pass a
            `timeout`, and parse `resp.read()` with `json.loads`.

            `Request` stores each header name with only its first letter in upper case, so
            `Content-Type` is stored as `Content-type`. The server accepts both spellings
            because HTTP header names are **case-insensitive**: upper and lower case letters
            count as the same.

            Many projects use the `httpx` library instead. `httpx.post(url, json=payload,
            headers=...)` encodes the payload for you. The request it sends has the same
            method, headers and JSON body.
        ''',
        "prompt": r'''
            Send a chat request the way LLM APIs expect it.

            **Write:** `post_json(url, payload, api_key)`

            - `url`: full endpoint URL, e.g. `"http://127.0.0.1:8000/v1/chat"`
            - `payload`: a dict to send as the JSON body
            - `api_key`: a string, e.g. `"sk-test"`
            - **Returns:** the response body parsed from JSON

            **Rules**
            - Method `POST`.
            - Body: `payload` as UTF-8 JSON bytes.
            - Headers: `Authorization: Bearer <api_key>` and `Content-Type: application/json`.
            - Pass a `timeout` to `urlopen`.

            **Examples**
            ```python
            post_json(server + "/v1/chat", {"model": "small", "messages": []}, "sk-test")
            # server receives POST /v1/chat with those headers and body
            # returns the JSON it answered, e.g. {"id": "resp_1", ...}
            ```
        ''',
        "starter": r'''
            import json
            from urllib.request import Request, urlopen

            def post_json(url, payload, api_key):
                ...
        ''',
        "tests": _t(r'''
            from solution import post_json

            def _echo(req):
                return 200, {}, {"id": "resp_1", "echo": json.loads(req["body"] or b"null")}

            PAYLOAD = {"model": "small", "messages": [{"role": "user", "content": "héllo"}]}

            def test_returns_parsed_response():
                with _Server(_echo) as srv:
                    got = post_json(srv.url + "/v1/chat", PAYLOAD, "sk-test")
                assert got == {"id": "resp_1", "echo": PAYLOAD}, f"got {got!r}"

            def test_method_and_path():
                with _Server(_echo) as srv:
                    post_json(srv.url + "/v1/chat", PAYLOAD, "sk-test")
                    req = srv.requests[0]
                assert req["method"] == "POST", f"method was {req['method']}"
                assert req["path"] == "/v1/chat", f"path was {req['path']}"

            def test_headers():
                with _Server(_echo) as srv:
                    post_json(srv.url + "/v1/chat", PAYLOAD, "sk-test")
                    h = srv.requests[0]["headers"]
                assert h.get("authorization") == "Bearer sk-test", f"Authorization was {h.get('authorization')!r}"
                assert h.get("content-type") == "application/json", f"Content-Type was {h.get('content-type')!r}"

            def test_body_is_the_json_payload():
                with _Server(_echo) as srv:
                    post_json(srv.url + "/v1/chat", PAYLOAD, "sk-test")
                    body = srv.requests[0]["body"]
                assert json.loads(body) == PAYLOAD, f"server received {body!r}"
        '''),
        "solution": r'''
            import json
            from urllib.request import Request, urlopen

            def post_json(url, payload, api_key):
                req = Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Authorization": f"Bearer {api_key}",
                             "Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(req, timeout=5) as resp:
                    return json.loads(resp.read())
        ''',
        "hints": [
            "Build a Request with the url, a bytes body, a headers dict and method=\"POST\", then open it with urlopen.",
            "The body is json.dumps(payload) encoded to UTF-8 bytes. The headers dict has the Bearer token and the JSON content type.",
            "req = Request(url, data=<bytes>, headers={...}, method=\"POST\"); with urlopen(req, timeout=5) as resp: return json.loads(resp.read()).",
        ],
    },
    {
        "id": "http-3",
        "title": "When the server says no",
        "difficulty": 1,
        "lesson": r'''
            ## Error responses are raised as exceptions

            When the server answers with a 4xx or 5xx status, `urlopen` does not return a
            response. It raises `urllib.error.HTTPError`. The exception object holds the
            response data: the status code, the headers and the body. The body usually
            explains what went wrong.

            The example builds an `HTTPError` by hand and raises it, so it runs without a
            server. `urlopen` raises the same kind of object for a real 404.
            `io.BytesIO(b"...")` makes an object with a `.read()` method that returns those
            bytes.

            ```python
            import io
            from urllib.error import HTTPError

            err = HTTPError("https://x.io/v1/nope", 404, "Not Found", {}, io.BytesIO(b"no such model"))
            try:
                raise err
            except HTTPError as e:
                print(e.code)
                # 404
                print(e.read().decode("utf-8"))
                # no such model
            ```

            - `e.code` is the status code, such as 404, 429 or 500.
            - `e.read()` returns the error body as bytes.
            - `.decode("utf-8")` turns bytes into a string. It is the reverse of `.encode("utf-8")`.
            - `e.headers` holds the response headers.

            Catching the exception lets your code choose what to do next: show the message,
            try again, or stop.

            If nothing catches it, the program stops with a traceback whose last line is
            `urllib.error.HTTPError: HTTP Error 404: Not Found`.

            `HTTPError` is defined in `urllib.error`, not in `urllib.request`. Import it
            with `from urllib.error import HTTPError`.
        ''',
        "prompt": r'''
            A health-check tool needs the status code and body of any URL - including errors.

            **Write:** `fetch_status(url)`

            - `url`: a full URL string
            - **Returns:** a tuple `(status, text)`: the status code (int) and the body decoded as UTF-8 text

            **Rules**
            - Works for success codes AND for error codes (4xx/5xx): catch `urllib.error.HTTPError`
              and return its code and body instead of crashing.
            - Pass a `timeout` to `urlopen`.

            **Examples**
            ```python
            fetch_status(server + "/ok")        # returns (200, "fine")
            fetch_status(server + "/missing")   # returns (404, "no such page")
            fetch_status(server + "/boom")      # returns (500, "oven broke")
            ```
        ''',
        "starter": r'''
            from urllib.request import urlopen
            from urllib.error import HTTPError

            def fetch_status(url):
                ...
        ''',
        "tests": _t(r'''
            from solution import fetch_status

            ROUTES = {"/ok": (200, "fine"), "/missing": (404, "no such page"),
                      "/boom": (500, "oven broke"), "/limit": (429, "slow down")}

            def _handler(req):
                status, text = ROUTES[req["path"]]
                return status, {}, text

            def test_success():
                with _Server(_handler) as srv:
                    got = fetch_status(srv.url + "/ok")
                assert got == (200, "fine"), f"got {got!r}"

            def test_not_found():
                with _Server(_handler) as srv:
                    got = fetch_status(srv.url + "/missing")
                assert got == (404, "no such page"), f"got {got!r}"

            def test_server_error():
                with _Server(_handler) as srv:
                    got = fetch_status(srv.url + "/boom")
                assert got == (500, "oven broke"), f"got {got!r}"

            def test_rate_limited():
                with _Server(_handler) as srv:
                    got = fetch_status(srv.url + "/limit")
                assert got == (429, "slow down"), f"got {got!r}"
        '''),
        "solution": r'''
            from urllib.request import urlopen
            from urllib.error import HTTPError

            def fetch_status(url):
                try:
                    with urlopen(url, timeout=5) as resp:
                        return resp.status, resp.read().decode("utf-8")
                except HTTPError as err:
                    return err.code, err.read().decode("utf-8")
        ''',
        "hints": [
            "Put the urlopen call in a try block and catch HTTPError.",
            "On success use resp.status and resp.read(); on HTTPError use err.code and err.read(). Decode both bodies from bytes to text.",
            "try: with urlopen(url, timeout=5) as resp: return resp.status, resp.read().decode(\"utf-8\") / except HTTPError as err: return err.code, err.read().decode(\"utf-8\").",
        ],
    },
    {
        "id": "http-4",
        "title": "Don't wait forever",
        "difficulty": 1,
        "lesson": r'''
            ## Timeouts

            A **timeout** is the longest time, in seconds, that your code waits for the
            server. Without a timeout, `urlopen` keeps waiting for as long as the server
            stays silent, and your program does nothing else during that time.

            `urlopen(url, timeout=2)` stops waiting after about 2 seconds without an answer.
            It then raises an exception. Two exception types can occur:

            - `TimeoutError`: the connection was made, but the server did not answer in time.
            - `urllib.error.URLError`: the server could not be reached. The port is wrong,
              the server is down, or the timeout ran out while connecting.

            You can catch several exception types in one `except` clause. Put them in a
            tuple: `except (TimeoutError, URLError):`.

            This example raises the two exceptions itself, so it runs without a server.

            ```python
            from urllib.error import URLError

            def call(kind):
                if kind == "slow":
                    raise TimeoutError("timed out")
                if kind == "down":
                    raise URLError("connection refused")
                return "pong"

            for kind in ["ok", "slow", "down"]:
                try:
                    print(call(kind))
                except (TimeoutError, URLError) as err:
                    print("gave up:", type(err).__name__)
            # pong
            # gave up: TimeoutError
            # gave up: URLError
            ```

            An LLM call can take 30 to 60 seconds to answer, so real timeouts are often
            long. Set one on every request anyway.
        ''',
        "prompt": r'''
            A status page pings a service. It must never hang.

            **Write:** `fetch_text(url, timeout)`

            - `url`: a full URL string
            - `timeout`: seconds to wait (a float, e.g. `0.1`)
            - **Returns:** the body decoded as UTF-8 text, or `None` if the server was too slow or unreachable

            **Rules**
            - Pass `timeout` to `urlopen`.
            - Catch `TimeoutError` and `urllib.error.URLError` and return `None`.

            **Examples**
            ```python
            fetch_text(server + "/fast", 1)    # returns "pong"
            fetch_text(server + "/slow", 0.1)  # server takes 0.5 s -> returns None after ~0.1 s
            fetch_text("http://127.0.0.1:1/", 0.5)   # nothing listening -> returns None
            ```
        ''',
        "starter": r'''
            from urllib.request import urlopen
            from urllib.error import URLError

            def fetch_text(url, timeout):
                ...
        ''',
        "tests": _t(r'''
            from solution import fetch_text

            def _handler(req):
                if req["path"] == "/slow":
                    time.sleep(0.5)
                return 200, {}, "pong"

            def test_fast_response():
                with _Server(_handler) as srv:
                    got = fetch_text(srv.url + "/fast", 1)
                assert got == "pong", f"got {got!r}"

            def test_slow_server_returns_none_quickly():
                with _Server(_handler) as srv:
                    start = time.perf_counter()
                    got = fetch_text(srv.url + "/slow", 0.1)
                    took = time.perf_counter() - start
                assert got is None, f"got {got!r}"
                assert took < 0.4, f"waited {took:.2f}s - is the timeout passed to urlopen?"

            def test_unreachable_returns_none():
                got = fetch_text("http://127.0.0.1:%d/" % _free_port(), 0.5)
                assert got is None, f"got {got!r}"
        '''),
        "solution": r'''
            from urllib.request import urlopen
            from urllib.error import URLError

            def fetch_text(url, timeout):
                try:
                    with urlopen(url, timeout=timeout) as resp:
                        return resp.read().decode("utf-8")
                except (TimeoutError, URLError):
                    return None
        ''',
        "hints": [
            "urlopen takes a timeout argument. Giving up raises an exception you can catch.",
            "Wrap the request in try/except and catch both TimeoutError and URLError together with a tuple.",
            "try: with urlopen(url, timeout=timeout) as resp: return resp.read().decode(\"utf-8\") / except (TimeoutError, URLError): return None.",
        ],
    },
    {
        "id": "http-5",
        "title": "Should I retry?",
        "difficulty": 1,
        "lesson": r'''
            ## Retries and backoff

            Some failures are temporary. `429 Too Many Requests` means you sent requests too
            fast. `500`, `502` and `503` often mean the server is overloaded. LLM APIs return
            these codes often when they are busy. A **retry** sends the same request again,
            and it can succeed.

            Other failures are permanent. `400` is a bad request, `401` is a bad key and
            `404` is a missing resource. The same request fails again, so you do not retry.

            Wait before each retry, and wait longer each time. **Exponential backoff** is a
            schedule where the wait doubles after every failed attempt. A **cap** is the
            maximum wait. `min(a, b)` returns the smaller value, so it applies the cap.

            ```python
            base, cap = 1.0, 20.0
            for attempt in range(6):
                delay = min(base * 2 ** attempt, cap)
                print(attempt, delay)
            # 0 1.0
            # 1 2.0
            # 2 4.0
            # 3 8.0
            # 4 16.0
            # 5 20.0
            ```

            `2 ** attempt` is 1, 2, 4, 8, 16, 32. The last wait would be 32.0, and the cap
            reduces it to 20.0.

            Step through the stages to see where the loop goes back to the request.

            ```diagram
            {"type":"flow","title":"Retry with exponential backoff","steps":[
            {"label":"Send the request","detail":"The first request uses attempt = 0.","code":"attempt = 0\nbase, cap = 1.0, 20.0"},
            {"label":"Read the status","detail":"A 2xx status means success and the loop ends. Any other status goes to the next stage.","code":"status = 503"},
            {"label":"Check the status","detail":"429 and 500 to 599 are temporary, so a retry can work. 400, 401 and 404 are permanent, so the loop ends with an error.","code":"status == 429 or 500 <= status <= 599\n# True"},
            {"label":"Compute the wait","detail":"If the response has a Retry-After header, the wait is that number of seconds. Otherwise the wait doubles with each attempt, up to the cap.","code":"delay = min(base * 2 ** attempt, cap)\n# attempt 0: 1.0\n# attempt 1: 2.0\n# attempt 2: 4.0"},
            {"label":"Wait","detail":"The program sleeps for delay seconds. Then attempt goes up by 1.","code":"time.sleep(delay)\nattempt += 1"}
            ],"loop":{"from":4,"to":0,"label":"while the status is 429 or 5xx and attempts remain"}}
            ```

            A server can send a `Retry-After` header with a number of seconds. That is the
            wait the server asks for, so use it in place of your computed delay. A header
            value is always a string. Convert `"2"` with `float()` before you use it as a
            number.
        ''',
        "prompt": r'''
            Decide whether a failed request should be retried, and after how long.

            **Write:** `retry_delay(status, attempt, retry_after=None)`

            - `status`: the HTTP status code (int)
            - `attempt`: how many retries already happened (int, starts at `0`)
            - `retry_after`: the `Retry-After` header value as a string (e.g. `"3"`), or `None`
            - **Returns:** `None` if the status should NOT be retried; otherwise the number of
              seconds to wait, as a float

            **Rules**
            - Retry only `429` and `500`-`599`. Everything else returns `None`.
            - If `retry_after` is given, return it as a float.
            - Otherwise return `0.5 * 2 ** attempt`, but never more than `8.0`.

            **Examples**
            ```python
            retry_delay(503, 0)          # returns 0.5
            retry_delay(503, 2)          # returns 2.0
            retry_delay(429, 10)         # returns 8.0  (capped)
            retry_delay(429, 0, "3")     # returns 3.0
            retry_delay(404, 0)          # returns None
            ```
        ''',
        "starter": r'''
            def retry_delay(status, attempt, retry_after=None):
                ...
        ''',
        "tests": r'''
            from solution import retry_delay

            def test_backoff_doubles():
                got = [retry_delay(503, a) for a in range(4)]
                assert got == [0.5, 1.0, 2.0, 4.0], f"got {got!r}"

            def test_capped_at_eight():
                assert retry_delay(429, 10) == 8.0, f"got {retry_delay(429, 10)!r}"
                assert retry_delay(500, 4) == 8.0, f"got {retry_delay(500, 4)!r}"

            def test_retry_after_wins():
                got = retry_delay(429, 0, "3")
                assert got == 3.0 and isinstance(got, float), f"got {got!r}"

            def test_permanent_errors_not_retried():
                for code in (400, 401, 404, 200, 302):
                    assert retry_delay(code, 0) is None, f"{code} -> {retry_delay(code, 0)!r}"

            def test_all_5xx_retried():
                for code in (500, 502, 599):
                    assert retry_delay(code, 1) == 1.0, f"{code} -> {retry_delay(code, 1)!r}"
        ''',
        "solution": r'''
            def retry_delay(status, attempt, retry_after=None):
                if status != 429 and not 500 <= status <= 599:
                    return None
                if retry_after is not None:
                    return float(retry_after)
                return min(0.5 * 2 ** attempt, 8.0)
        ''',
        "hints": [
            "Three decisions in order: is this status retryable at all? did the server say how long? otherwise compute backoff.",
            "Return None unless the status is 429 or between 500 and 599. Then prefer retry_after (converted to float). Otherwise use the doubling formula with min() for the cap.",
            "if status != 429 and not 500 <= status <= 599: return None; if retry_after is not None: return float(retry_after); return min(0.5 * 2 ** attempt, 8.0).",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "http-6",
        "title": "A reusable request helper",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## One helper for every request

            This exercise combines the earlier steps in one function. The function builds
            the headers and the body, sends the request, and returns `(status, data)` for
            success responses and for error responses.

            A successful response and an `HTTPError` both give you a status code and body
            bytes. Some responses, such as `204 No Content`, have an empty body. Empty bytes
            are `b""`, and `bool(b"")` is `False`. `json.loads(b"")` raises
            `JSONDecodeError`, so check for an empty body before you parse.

            ```python
            import json

            for raw in [b'{"ok": true}', b""]:
                print(raw, bool(raw))
            # b'{"ok": true}' True
            # b'' False
            try:
                json.loads(b"")
            except json.JSONDecodeError as err:
                print("JSONDecodeError:", err)
            # JSONDecodeError: Expecting value: line 1 column 1 (char 0)
            ```
        ''',
        "prompt": r'''
            Every API client ends up with one function that does the HTTP work. Write it.

            **Write:** `request_json(url, method="GET", payload=None, api_key=None, timeout=5)`

            - `url`: full URL string
            - `method`: `"GET"`, `"POST"`, `"DELETE"`, ...
            - `payload`: a dict to send as JSON, or `None` for no body
            - `api_key`: a string, or `None`
            - `timeout`: seconds, passed to `urlopen`
            - **Returns:** a tuple `(status, data)`: the status code, and the response body parsed
              from JSON - or `None` if the body is empty

            **Rules**
            - Always send the header `Accept: application/json`.
            - Only if `payload` is not `None`: send it as UTF-8 JSON and add `Content-Type: application/json`.
            - Only if `api_key` is given: add `Authorization: Bearer <api_key>`.
            - Use the given `method`.
            - Error statuses (4xx/5xx) are returned as `(status, data)` too - don't raise.

            **Examples**
            ```python
            request_json(server + "/v1/models")                 # (200, {"models": [...]})
            request_json(server + "/v1/chat", "POST", {"q": 1}, "sk-1")   # (201, {...})
            request_json(server + "/v1/nope")                   # (404, {"error": "not found"})
            request_json(server + "/v1/files/7", "DELETE", api_key="sk-1")  # (204, None)
            ```
        ''',
        "starter": r'''
            import json
            from urllib.request import Request, urlopen
            from urllib.error import HTTPError

            def request_json(url, method="GET", payload=None, api_key=None, timeout=5):
                ...
        ''',
        "tests": _t(r'''
            from solution import request_json

            def _handler(req):
                if req["path"] == "/v1/models":
                    return 200, {}, {"models": ["small"]}
                if req["path"] == "/v1/chat":
                    return 201, {}, {"got": json.loads(req["body"])}
                if req["path"].startswith("/v1/files/"):
                    return 204, {}, b""
                return 404, {}, {"error": "not found"}

            def test_simple_get():
                with _Server(_handler) as srv:
                    got = request_json(srv.url + "/v1/models")
                    h = srv.requests[0]["headers"]
                    method = srv.requests[0]["method"]
                assert got == (200, {"models": ["small"]}), f"got {got!r}"
                assert method == "GET"
                assert h.get("accept") == "application/json", f"Accept was {h.get('accept')!r}"
                assert "authorization" not in h, "no api_key was given, so no Authorization header"
                assert "content-type" not in h, "no payload, so no Content-Type header"

            def test_post_with_payload_and_key():
                with _Server(_handler) as srv:
                    got = request_json(srv.url + "/v1/chat", "POST", {"q": "hé"}, "sk-1")
                    req = srv.requests[0]
                assert got == (201, {"got": {"q": "hé"}}), f"got {got!r}"
                assert req["method"] == "POST"
                assert req["headers"].get("authorization") == "Bearer sk-1"
                assert req["headers"].get("content-type") == "application/json"

            def test_error_status_is_returned():
                with _Server(_handler) as srv:
                    got = request_json(srv.url + "/v1/nope")
                assert got == (404, {"error": "not found"}), f"got {got!r}"

            def test_delete_with_empty_body():
                with _Server(_handler) as srv:
                    got = request_json(srv.url + "/v1/files/7", "DELETE", api_key="sk-1")
                    method = srv.requests[0]["method"]
                assert got == (204, None), f"got {got!r}"
                assert method == "DELETE", f"method was {method}"
        '''),
        "solution": r'''
            import json
            from urllib.request import Request, urlopen
            from urllib.error import HTTPError

            def request_json(url, method="GET", payload=None, api_key=None, timeout=5):
                headers = {"Accept": "application/json"}
                data = None
                if payload is not None:
                    data = json.dumps(payload).encode("utf-8")
                    headers["Content-Type"] = "application/json"
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                req = Request(url, data=data, headers=headers, method=method)
                try:
                    with urlopen(req, timeout=timeout) as resp:
                        status, raw = resp.status, resp.read()
                except HTTPError as err:
                    status, raw = err.code, err.read()
                return status, (json.loads(raw) if raw else None)
        ''',
        "hints": [
            "Build the headers dict and the body step by step with if-statements, then make one Request with method=method.",
            "Get (status, raw bytes) from either the response or the HTTPError, then parse the bytes only if they're not empty.",
            "headers = {\"Accept\": ...}; if payload is not None: data = JSON bytes and add Content-Type; if api_key: add Authorization. try: urlopen -> resp.status, resp.read() / except HTTPError as err: err.code, err.read(). Return (status, json.loads(raw) if raw else None).",
        ],
    },
    {
        "id": "http-7",
        "title": "GET with retries",
        "difficulty": 2,
        "prompt": r'''
            Put retries into a real request loop. The `sleep` function is passed in, so the
            checks can record your waits instead of really waiting.

            **Write:** `get_with_retries(url, max_attempts=3, sleep=time.sleep)`

            - `url`: full URL string
            - `max_attempts`: the maximum number of requests in total (int >= 1)
            - `sleep`: a function taking seconds; call it to wait between attempts
            - **Returns:** the JSON body of the first successful response, parsed

            **Rules**
            - On `HTTPError` with status `429` or `500`-`599`: wait, then try again.
            - The wait is the `Retry-After` response header as a float if present, otherwise
              `0.5 * 2 ** n` where `n` is `0` for the first retry, `1` for the second, ...
            - Any other `HTTPError` status (e.g. `404`) is re-raised immediately, with no wait.
            - After `max_attempts` failed requests, re-raise the last `HTTPError` (don't sleep after the last attempt).
            - Pass a `timeout` to `urlopen`.

            **Examples**
            ```python
            # server: 503, 503, then 200 {"ok": true}
            get_with_retries(url, 3, fake_sleep)   # returns {"ok": True}; waits 0.5 then 1.0
            # server: 429 with header Retry-After: 2, then 200
            get_with_retries(url, 3, fake_sleep)   # waits 2.0
            # server: always 404
            get_with_retries(url, 3, fake_sleep)   # raises HTTPError (code 404) after 1 request
            ```
        ''',
        "starter": r'''
            import json
            import time
            from urllib.request import urlopen
            from urllib.error import HTTPError

            def get_with_retries(url, max_attempts=3, sleep=time.sleep):
                ...
        ''',
        "tests": _t(r'''
            from urllib.error import HTTPError
            from solution import get_with_retries

            def _script(*responses):
                """Serve the given (status, headers) in order; after that, 200 {"ok": true}."""
                queue = list(responses)
                def handler(req):
                    if queue:
                        status, headers = queue.pop(0)
                        return status, headers, {"error": "try later"}
                    return 200, {}, {"ok": True}
                return handler

            def test_retries_5xx_with_backoff():
                waits = []
                with _Server(_script((503, {}), (500, {}))) as srv:
                    got = get_with_retries(srv.url + "/x", 3, waits.append)
                    n = len(srv.requests)
                assert got == {"ok": True}, f"got {got!r}"
                assert n == 3, f"server got {n} requests"
                assert waits == [0.5, 1.0], f"waited {waits!r}"

            def test_honours_retry_after():
                waits = []
                with _Server(_script((429, {"Retry-After": "2"}))) as srv:
                    got = get_with_retries(srv.url + "/x", 3, waits.append)
                assert got == {"ok": True}, f"got {got!r}"
                assert waits == [2.0], f"waited {waits!r}"

            def test_404_not_retried():
                waits = []
                with _Server(lambda req: (404, {}, {"error": "nope"})) as srv:
                    try:
                        get_with_retries(srv.url + "/x", 3, waits.append)
                        assert False, "expected HTTPError"
                    except HTTPError as err:
                        assert err.code == 404, f"code was {err.code}"
                    n = len(srv.requests)
                assert n == 1, f"server got {n} requests"
                assert waits == [], f"waited {waits!r}"

            def test_gives_up_after_max_attempts():
                waits = []
                with _Server(lambda req: (500, {}, {"error": "down"})) as srv:
                    try:
                        get_with_retries(srv.url + "/x", 2, waits.append)
                        assert False, "expected HTTPError"
                    except HTTPError as err:
                        assert err.code == 500, f"code was {err.code}"
                    n = len(srv.requests)
                assert n == 2, f"server got {n} requests"
                assert waits == [0.5], f"waited {waits!r}"
        '''),
        "solution": r'''
            import json
            import time
            from urllib.request import urlopen
            from urllib.error import HTTPError

            def get_with_retries(url, max_attempts=3, sleep=time.sleep):
                for attempt in range(max_attempts):
                    try:
                        with urlopen(url, timeout=5) as resp:
                            return json.loads(resp.read())
                    except HTTPError as err:
                        retryable = err.code == 429 or 500 <= err.code <= 599
                        if not retryable or attempt == max_attempts - 1:
                            raise
                        retry_after = err.headers.get("Retry-After")
                        sleep(float(retry_after) if retry_after else 0.5 * 2 ** attempt)
        ''',
        "hints": [
            "Loop over range(max_attempts). Inside, try the request; in the except HTTPError branch decide between re-raising and sleeping.",
            "Re-raise (plain `raise`) if the status isn't retryable or this was the last attempt. Otherwise read err.headers.get(\"Retry-After\") to pick the wait.",
            "for attempt in range(max_attempts): try: return parsed JSON / except HTTPError as err: if not (429 or 5xx) or attempt == max_attempts - 1: raise; wait = float(header) if header else 0.5 * 2 ** attempt; sleep(wait).",
        ],
    },
    {
        "id": "http-8",
        "title": "Verify a webhook signature",
        "difficulty": 2,
        "research": {
            "note": "Read how `hmac.new` and `hmac.compare_digest` work, then see how GitHub signs its webhooks with an `X-Hub-Signature-256: sha256=...` header - the exact scheme you'll implement.",
            "links": [
                {"title": "hmac - Python docs", "url": "https://docs.python.org/3/library/hmac.html"},
                {"title": "Validating webhook deliveries - GitHub Docs", "url": "https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries"},
            ],
        },
        "lesson": r'''
            ## Webhooks and HMAC signatures

            A **webhook** is an HTTP request that a service sends to your server when an
            event happens. Here your code is the server and the service is the client.

            Anyone can send a `POST` to your URL, so the sender adds a **signature**: a value
            that only someone with the secret key can compute. Only you and the sender have
            that key. The signature is an **HMAC**: a
            fixed-length value computed from a key and a message. Changing one byte of the
            message gives a different value.

            `hmac.new(key, message, hashlib.sha256)` takes the key and the message as bytes.
            `hashlib.sha256` names the algorithm that computes the value. `.hexdigest()`
            returns the HMAC as a string of 64 hexadecimal characters (`0`-`9` and `a`-`f`).

            ```python
            import hashlib
            import hmac

            secret = b"secret"
            sig = hmac.new(secret, b'{"event": "done"}', hashlib.sha256).hexdigest()
            print(sig[:16], len(sig))
            # e8e14181494d07f1 64
            changed = hmac.new(secret, b'{"event": "DONE"}', hashlib.sha256).hexdigest()
            print(changed[:16])
            # e0ff41802135617f
            print(hmac.compare_digest(sig, changed))
            # False
            ```

            To verify a webhook, compute the signature of the received body and compare it
            with the header value. Use `hmac.compare_digest(a, b)`, not `==`. `==` can stop
            at the first character that differs, so its running time shows how many leading
            characters of a guess were right. An attacker who measures that time can find
            the signature one character at a time. This is called a **timing attack**.
            `compare_digest` takes the same time wherever the first difference is.
        ''',
        "prompt": r'''
            Your app receives webhooks. Each request has a header like
            `X-Signature: sha256=<hex>` where `<hex>` is the HMAC-SHA256 of the raw body using a shared secret.

            **Write:** two functions

            `sign(secret, body)`
            - `secret`: a string, e.g. `"whsec_123"`
            - `body`: the raw request body, `bytes`
            - **Returns:** `"sha256="` followed by the hex HMAC-SHA256 of `body` with key `secret` (UTF-8 encoded)

            `verify_signature(secret, body, header)`
            - `header`: the received header value (a string) or `None`
            - **Returns:** `True` if `header` is exactly the correct signature, else `False`

            **Rules**
            - Missing header (`None`), a header without the `sha256=` prefix, a changed body or
              the wrong secret all give `False` (never an exception).
            - Compare with `hmac.compare_digest` (the checks look for it in your code).

            **Examples**
            ```python
            sign("whsec_123", b'{"event": "done"}')     # "sha256=" + 64 hex characters
            verify_signature("whsec_123", b'{"event": "done"}', sign("whsec_123", b'{"event": "done"}'))  # True
            verify_signature("whsec_123", b'{"event": "HACKED"}', <that same header>)   # False
            verify_signature("whsec_123", b"{}", None)                                   # False
            ```
        ''',
        "starter": r'''
            import hashlib
            import hmac

            def sign(secret, body):
                ...

            def verify_signature(secret, body, header):
                ...
        ''',
        "tests": r'''
            import hashlib, hmac
            from solution import sign, verify_signature

            BODY = b'{"event": "batch.completed", "id": "b_1"}'
            SECRET = "whsec_123"
            GOOD = "sha256=" + hmac.new(SECRET.encode(), BODY, hashlib.sha256).hexdigest()

            def test_sign_matches_hmac_sha256():
                got = sign(SECRET, BODY)
                assert got == GOOD, f"got {got!r}"

            def test_valid_signature_accepted():
                assert verify_signature(SECRET, BODY, GOOD) is True

            def test_tampered_body_rejected():
                assert verify_signature(SECRET, BODY.replace(b"b_1", b"b_2"), GOOD) is False

            def test_wrong_secret_rejected():
                assert verify_signature("whsec_other", BODY, GOOD) is False

            def test_missing_or_malformed_header_rejected():
                assert verify_signature(SECRET, BODY, None) is False
                assert verify_signature(SECRET, BODY, GOOD.removeprefix("sha256=")) is False
                assert verify_signature(SECRET, BODY, "") is False

            def test_uses_compare_digest():
                assert "compare_digest" in source(), "compare signatures with hmac.compare_digest"
        ''',
        "solution": r'''
            import hashlib
            import hmac

            def sign(secret, body):
                digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
                return "sha256=" + digest

            def verify_signature(secret, body, header):
                if not header or not header.startswith("sha256="):
                    return False
                return hmac.compare_digest(sign(secret, body), header)
        ''',
        "hints": [
            "hmac.new(key_bytes, body, hashlib.sha256).hexdigest() gives the hex signature; the key must be bytes.",
            "verify_signature can reuse sign(): compute the expected header, reject missing/bad headers first, then compare the two strings safely.",
            "sign: return \"sha256=\" + hmac.new(secret.encode(\"utf-8\"), body, hashlib.sha256).hexdigest(). verify: if not header or not header.startswith(\"sha256=\"): return False; return hmac.compare_digest(sign(secret, body), header).",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "http-9",
        "title": "Webhooks: stop replays",
        "difficulty": 3,
        "prompt": r'''
            A valid signed webhook can be captured and re-sent later (a *replay attack*). Many
            providers sign a timestamp together with the body and reject old deliveries.

            **Write:** `verify_webhook(secret, body, headers, now, tolerance=300)`

            - `secret`: a string
            - `body`: the raw body, `bytes`
            - `headers`: a dict of received headers, e.g.
              `{"X-Timestamp": "1700000000", "X-Signature": "v1=<hex>"}` (names may come in any letter case)
            - `now`: the current time as an int (seconds since 1970)
            - `tolerance`: the maximum age/skew in seconds
            - **Returns:** `True` if the delivery is genuine and fresh, else `False`

            **Rules**
            - The signed message is the timestamp text, a dot, then the body: `b"1700000000." + body`.
            - The signature header is `"v1="` followed by the hex HMAC-SHA256 of that message with key `secret` (UTF-8).
            - Header names are case-insensitive (`x-signature`, `X-SIGNATURE`, ... all count).
            - Return `False` if either header is missing, the timestamp isn't an integer,
              `abs(now - timestamp) > tolerance`, or the signature doesn't match.
            - Compare signatures with `hmac.compare_digest`. Never raise.

            **Examples**
            ```python
            ts = "1700000000"
            sig = "v1=" + hmac.new(b"whsec", ts.encode() + b"." + body, hashlib.sha256).hexdigest()
            verify_webhook("whsec", body, {"X-Timestamp": ts, "X-Signature": sig}, now=1700000100)  # True
            verify_webhook("whsec", body, {"X-Timestamp": ts, "X-Signature": sig}, now=1700000400)  # False (too old)
            verify_webhook("whsec", body, {"x-timestamp": ts, "x-signature": sig}, now=1700000000)  # True
            verify_webhook("whsec", body, {"X-Signature": sig}, now=1700000000)                     # False
            ```
        ''',
        "starter": r'''
            import hashlib
            import hmac

            def verify_webhook(secret, body, headers, now, tolerance=300):
                ...
        ''',
        "tests": r'''
            import hashlib, hmac
            from solution import verify_webhook

            BODY = b'{"type": "batch.completed"}'
            TS = "1700000000"

            def _sig(ts=TS, body=BODY, secret="whsec"):
                return "v1=" + hmac.new(secret.encode(), ts.encode() + b"." + body, hashlib.sha256).hexdigest()

            def _h(ts=TS, sig=None):
                return {"X-Timestamp": ts, "X-Signature": sig or _sig(ts)}

            def test_fresh_valid_delivery():
                assert verify_webhook("whsec", BODY, _h(), now=1700000100) is True

            def test_too_old_or_from_the_future():
                assert verify_webhook("whsec", BODY, _h(), now=1700000301) is False
                assert verify_webhook("whsec", BODY, _h(), now=1699999699) is False
                assert verify_webhook("whsec", BODY, _h(), now=1700000300) is True

            def test_custom_tolerance():
                assert verify_webhook("whsec", BODY, _h(), now=1700000010, tolerance=5) is False

            def test_header_names_any_case():
                headers = {"x-timestamp": TS, "X-SIGNATURE": _sig()}
                assert verify_webhook("whsec", BODY, headers, now=1700000000) is True

            def test_timestamp_is_part_of_signature():
                forged = {"X-Timestamp": "1700000500", "X-Signature": _sig()}
                assert verify_webhook("whsec", BODY, forged, now=1700000500) is False

            def test_bad_inputs_return_false():
                assert verify_webhook("whsec", BODY, {"X-Signature": _sig()}, now=1700000000) is False
                assert verify_webhook("whsec", BODY, {"X-Timestamp": TS}, now=1700000000) is False
                assert verify_webhook("whsec", BODY, _h(ts="soon", sig=_sig("soon")), now=1700000000) is False
                assert verify_webhook("whsec", BODY + b" ", _h(), now=1700000000) is False
                assert verify_webhook("other", BODY, _h(), now=1700000000) is False

            def test_uses_compare_digest():
                assert "compare_digest" in source(), "compare signatures with hmac.compare_digest"
        ''',
        "solution": r'''
            import hashlib
            import hmac

            def verify_webhook(secret, body, headers, now, tolerance=300):
                lower = {name.lower(): value for name, value in headers.items()}
                ts = lower.get("x-timestamp")
                sig = lower.get("x-signature")
                if ts is None or sig is None:
                    return False
                try:
                    ts_int = int(ts)
                except ValueError:
                    return False
                if abs(now - ts_int) > tolerance:
                    return False
                message = ts.encode("utf-8") + b"." + body
                expected = "v1=" + hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
                return hmac.compare_digest(expected, sig)
        ''',
        "hints": [
            "Normalise the header names first (a dict comprehension with .lower()), then check each rule in order and return False as soon as one fails.",
            "Parse the timestamp with int() inside try/except ValueError, check the age with abs(), then compute the expected signature over timestamp + b\".\" + body.",
            "lower = {k.lower(): v ...}; get x-timestamp and x-signature (False if missing); int(ts) or False; False if abs(now - ts) > tolerance; expected = \"v1=\" + hmac.new(secret.encode(), ts.encode() + b\".\" + body, hashlib.sha256).hexdigest(); return hmac.compare_digest(expected, sig).",
        ],
    },
    {
        "id": "http-10",
        "title": "Follow the pages",
        "difficulty": 3,
        "prompt": r'''
            List endpoints return results a page at a time, with a cursor pointing at the next
            page (this is how you list files, batches or fine-tuning jobs on LLM platforms).

            **Write:** `fetch_all(base_url, api_key, limit=2)`

            - `base_url`: e.g. `"http://127.0.0.1:8000"`
            - `api_key`: a string
            - `limit`: page size (int)
            - **Returns:** a list of every item from every page, in order

            **Rules**
            - Request `GET <base_url>/items?limit=<limit>` first; for later pages add
              `&cursor=<cursor>`. Build the query with `urlencode` (cursors may contain `=`, `&` or `/`).
            - Every request sends `Authorization: Bearer <api_key>`.
            - Each response is JSON like `{"data": [...items...], "next_cursor": "abc"}`.
              Add the `data` items; stop when `next_cursor` is `null`/missing.
            - Don't catch `HTTPError`: a `401` must propagate to the caller.
            - Pass a `timeout` to `urlopen`.

            **Examples**
            ```python
            fetch_all(server, "sk-1")           # 5 items over 3 pages -> [item1, ..., item5]
            fetch_all(server, "sk-1", limit=10) # 1 page -> same 5 items
            fetch_all(server, "wrong-key")      # raises urllib.error.HTTPError (401)
            ```
        ''',
        "starter": r'''
            import json
            from urllib.parse import urlencode
            from urllib.request import Request, urlopen

            def fetch_all(base_url, api_key, limit=2):
                ...
        ''',
        "tests": _t(r'''
            from urllib.error import HTTPError
            from urllib.parse import urlparse, parse_qs
            from solution import fetch_all

            ITEMS = [{"id": i, "name": f"file-{i}"} for i in range(1, 6)]

            def _cursor(i):
                return f"pos={i}&x/y" if i else None

            def _handler(req):
                if req["headers"].get("authorization") != "Bearer sk-1":
                    return 401, {}, {"error": "bad key"}
                parts = urlparse(req["path"])
                if parts.path != "/items":
                    return 404, {}, {"error": "no route"}
                q = parse_qs(parts.query)
                limit = int(q["limit"][0])
                start = 0
                if "cursor" in q:
                    start = int(q["cursor"][0].split("&")[0].removeprefix("pos="))
                    if q["cursor"][0] != _cursor(start):
                        return 400, {}, {"error": "mangled cursor"}
                end = start + limit
                nxt = _cursor(end) if end < len(ITEMS) else None
                return 200, {}, {"data": ITEMS[start:end], "next_cursor": nxt}

            def test_collects_all_pages():
                with _Server(_handler) as srv:
                    got = fetch_all(srv.url, "sk-1")
                    n = len(srv.requests)
                assert got == ITEMS, f"got {got!r}"
                assert n == 3, f"made {n} requests, expected 3 pages"

            def test_first_request_has_no_cursor():
                with _Server(_handler) as srv:
                    fetch_all(srv.url, "sk-1")
                    first = srv.requests[0]["path"]
                assert first == "/items?limit=2", f"first request was {first}"

            def test_bigger_page_size():
                with _Server(_handler) as srv:
                    got = fetch_all(srv.url, "sk-1", limit=10)
                    n = len(srv.requests)
                assert got == ITEMS and n == 1, f"got {len(got)} items in {n} requests"

            def test_bad_key_raises_http_error():
                with _Server(_handler) as srv:
                    try:
                        fetch_all(srv.url, "wrong-key")
                        assert False, "expected HTTPError"
                    except HTTPError as err:
                        assert err.code == 401, f"code was {err.code}"
        '''),
        "solution": r'''
            import json
            from urllib.parse import urlencode
            from urllib.request import Request, urlopen

            def fetch_all(base_url, api_key, limit=2):
                items, cursor = [], None
                while True:
                    params = {"limit": limit}
                    if cursor:
                        params["cursor"] = cursor
                    req = Request(f"{base_url}/items?{urlencode(params)}",
                                  headers={"Authorization": f"Bearer {api_key}"})
                    with urlopen(req, timeout=5) as resp:
                        page = json.loads(resp.read())
                    items.extend(page["data"])
                    cursor = page.get("next_cursor")
                    if not cursor:
                        return items
        ''',
        "hints": [
            "Use a while True loop that keeps track of the cursor (None at the start) and an items list.",
            "Each round: build params (limit, plus cursor when you have one), urlencode them, send a Request with the Authorization header, extend items with page[\"data\"], then read next_cursor.",
            "items, cursor = [], None; loop: params = {\"limit\": limit}; if cursor: params[\"cursor\"] = cursor; Request(f\"{base_url}/items?{urlencode(params)}\", headers=...); parse the JSON; items.extend(page[\"data\"]); cursor = page.get(\"next_cursor\"); if not cursor: return items.",
        ],
    },
    {
        "id": "http-11",
        "title": "A mini LLM API client",
        "difficulty": 3,
        "prompt": r'''
            Wrap everything into the kind of client class an LLM SDK gives you: auth, JSON,
            retries for temporary errors, clear exceptions, and token accounting.

            **Write:** a class `APIError(Exception)` and a class `LLMClient`

            `APIError(status, message)`
            - stores `.status` (int) and `.message` (str); `str(err)` is `"<status>: <message>"`

            `LLMClient(base_url, api_key, max_retries=2, sleep=time.sleep)`
            - `.total_tokens`: starts at `0`
            - `.chat(model, messages)`: sends `POST <base_url>/v1/chat` with JSON body
              `{"model": model, "messages": messages}` and headers `Authorization: Bearer <api_key>`
              and `Content-Type: application/json`
            - **Returns:** the `"reply"` string from a response like
              `{"reply": "Hi!", "usage": {"total_tokens": 12}}`, and adds `usage.total_tokens` to `.total_tokens`

            **Rules**
            - Status `429` or `500`-`599`: retry, up to `max_retries` extra attempts, calling
              `sleep(0.5 * 2 ** n)` before retry `n` (`n` = 0, 1, ...).
            - Any other error status, or still failing after the retries: raise `APIError`.
            - `APIError.message` is `error.message` from a JSON error body like
              `{"error": {"message": "bad model"}}`; if the body isn't in that shape, it's the raw body text.
            - Pass a `timeout` to `urlopen`.

            **Examples**
            ```python
            client = LLMClient(server, "sk-1", sleep=fake_sleep)
            client.chat("small", [{"role": "user", "content": "hi"}])   # returns "Hi!"
            client.total_tokens                                         # 12
            # server answers 400 {"error": {"message": "bad model"}}
            client.chat("nope", [])   # raises APIError; err.status == 400, err.message == "bad model"
            # server answers 502 "Bad Gateway" every time, max_retries=1
            # -> 2 requests, sleeps [0.5], raises APIError(502, "Bad Gateway")
            ```
        ''',
        "starter": r'''
            import json
            import time
            from urllib.request import Request, urlopen
            from urllib.error import HTTPError

            class APIError(Exception):
                ...

            class LLMClient:
                ...
        ''',
        "tests": _t(r'''
            from solution import APIError, LLMClient

            def _ok(req):
                body = json.loads(req["body"])
                words = sum(len(m["content"].split()) for m in body["messages"])
                return 200, {}, {"reply": f"echo:{body['model']}", "usage": {"total_tokens": 10 + words}}

            def test_chat_returns_reply_and_counts_tokens():
                with _Server(_ok) as srv:
                    c = LLMClient(srv.url, "sk-1", sleep=lambda s: None)
                    assert c.total_tokens == 0
                    got = c.chat("small", [{"role": "user", "content": "hi there"}])
                    c.chat("small", [{"role": "user", "content": "one"}])
                assert got == "echo:small", f"got {got!r}"
                assert c.total_tokens == 23, f"total_tokens is {c.total_tokens!r}"

            def test_request_shape():
                msgs = [{"role": "user", "content": "hi"}]
                with _Server(_ok) as srv:
                    LLMClient(srv.url, "sk-1", sleep=lambda s: None).chat("small", msgs)
                    req = srv.requests[0]
                assert req["method"] == "POST" and req["path"] == "/v1/chat", f"{req['method']} {req['path']}"
                assert req["headers"].get("authorization") == "Bearer sk-1"
                assert req["headers"].get("content-type") == "application/json"
                assert json.loads(req["body"]) == {"model": "small", "messages": msgs}

            def test_client_error_raises_api_error_without_retry():
                waits = []
                with _Server(lambda r: (400, {}, {"error": {"message": "bad model"}})) as srv:
                    c = LLMClient(srv.url, "sk-1", sleep=waits.append)
                    try:
                        c.chat("nope", [])
                        assert False, "expected APIError"
                    except APIError as err:
                        assert (err.status, err.message) == (400, "bad model"), f"got {(err.status, err.message)!r}"
                        assert str(err) == "400: bad model", f"str(err) is {str(err)!r}"
                    n = len(srv.requests)
                assert n == 1 and waits == [], f"{n} requests, waits {waits!r}"

            def test_retries_then_succeeds():
                state = {"n": 0}
                def handler(req):
                    state["n"] += 1
                    if state["n"] <= 2:
                        return 503, {}, {"error": {"message": "busy"}}
                    return _ok(req)
                waits = []
                with _Server(handler) as srv:
                    got = LLMClient(srv.url, "sk-1", sleep=waits.append).chat("m", [])
                assert got == "echo:m", f"got {got!r}"
                assert waits == [0.5, 1.0], f"waited {waits!r}"

            def test_gives_up_with_raw_text_message():
                waits = []
                with _Server(lambda r: (502, {}, "Bad Gateway")) as srv:
                    c = LLMClient(srv.url, "sk-1", max_retries=1, sleep=waits.append)
                    try:
                        c.chat("m", [])
                        assert False, "expected APIError"
                    except APIError as err:
                        assert (err.status, err.message) == (502, "Bad Gateway"), f"got {(err.status, err.message)!r}"
                    n = len(srv.requests)
                assert n == 2, f"server got {n} requests"
                assert waits == [0.5], f"waited {waits!r}"
        '''),
        "solution": r'''
            import json
            import time
            from urllib.request import Request, urlopen
            from urllib.error import HTTPError


            class APIError(Exception):
                def __init__(self, status, message):
                    super().__init__(f"{status}: {message}")
                    self.status = status
                    self.message = message


            class LLMClient:
                def __init__(self, base_url, api_key, max_retries=2, sleep=time.sleep):
                    self.base_url = base_url
                    self.api_key = api_key
                    self.max_retries = max_retries
                    self.sleep = sleep
                    self.total_tokens = 0

                def chat(self, model, messages):
                    body = json.dumps({"model": model, "messages": messages}).encode("utf-8")
                    headers = {"Authorization": f"Bearer {self.api_key}",
                               "Content-Type": "application/json"}
                    for attempt in range(self.max_retries + 1):
                        req = Request(self.base_url + "/v1/chat", data=body, headers=headers, method="POST")
                        try:
                            with urlopen(req, timeout=5) as resp:
                                data = json.loads(resp.read())
                        except HTTPError as err:
                            raw = err.read().decode("utf-8", errors="replace")
                            try:
                                message = json.loads(raw)["error"]["message"]
                            except (ValueError, KeyError, TypeError):
                                message = raw
                            retryable = err.code == 429 or 500 <= err.code <= 599
                            if retryable and attempt < self.max_retries:
                                self.sleep(0.5 * 2 ** attempt)
                                continue
                            raise APIError(err.code, message) from None
                        self.total_tokens += data["usage"]["total_tokens"]
                        return data["reply"]
        ''',
        "hints": [
            "APIError: call super().__init__ with the formatted text, then store status and message. LLMClient: store the settings in __init__ and set total_tokens = 0.",
            "chat() loops over range(max_retries + 1). On HTTPError, read the body once, try to pull error.message out of the JSON (fall back to the raw text), then either sleep and continue, or raise APIError.",
            "In the loop: build the Request (POST, JSON body, two headers); try urlopen -> data; except HTTPError as err: raw = err.read().decode(); message = json.loads(raw)[\"error\"][\"message\"] inside try/except (ValueError, KeyError, TypeError); if retryable and attempt < max_retries: sleep(0.5 * 2 ** attempt); continue; else raise APIError(err.code, message). On success add data[\"usage\"][\"total_tokens\"] and return data[\"reply\"].",
        ],
    },
]
