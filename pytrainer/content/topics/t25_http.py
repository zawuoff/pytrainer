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

LESSON = r'''
## Chapter notes: HTTP

**Request -> response.** The client (your code) sends a *request*; the server sends back a
*response*. Every LLM API call is one of these.

**A request has:** a **method** (`GET` read, `POST` create/send, `PUT`/`PATCH` update,
`DELETE` remove), a **URL**, **headers** (metadata) and, for POST/PUT, a **body**.

**A URL:** `https://api.example.com/v1/search?q=cats&limit=5`
= scheme `https` + host `api.example.com` + path `/v1/search` + query `q=cats&limit=5`.

```python
from urllib.parse import urlencode, urlparse, parse_qs
print(urlencode({"q": "hello world", "n": 2}))       # q=hello+world&n=2
print(parse_qs(urlparse("https://x.io/s?q=a&q=b").query))  # {'q': ['a', 'b']}
```

**Status codes:** 2xx success (200 OK, 201 Created, 204 No Content), 3xx redirect,
4xx *your* mistake (400 bad request, 401 no/bad key, 403 forbidden, 404 not found,
429 too many requests), 5xx *server* trouble (500, 502, 503).

**Headers:** `Authorization: Bearer <key>` (API key), `Content-Type: application/json`
(what the body is), `Accept`, `Retry-After` (seconds to wait). Header names are
case-insensitive.

**Sending with the stdlib:**
```python
import json
from urllib.request import Request
body = json.dumps({"model": "m", "messages": []}).encode("utf-8")
req = Request("https://api.example.com/v1/chat", data=body, method="POST",
              headers={"Authorization": "Bearer sk-...", "Content-Type": "application/json"})
print(req.get_method(), req.full_url)
# with urlopen(req, timeout=10) as resp: data = json.loads(resp.read())
```
- `urlopen` raises `urllib.error.HTTPError` for 4xx/5xx (it has `.code`, `.headers`,
  `.read()`), and `URLError` / `TimeoutError` when the server can't be reached in time.
- `HTTPError` is a subclass of `URLError`: catch it first.
- Bodies are **bytes**: `.encode("utf-8")` going out, `json.loads(resp.read())` coming back.

**Always set a timeout.** Without one, a stuck server hangs your app forever.

**Retries:** retry 429 and 5xx (temporary), never 400/401/404 (retrying won't fix them).
Wait between tries (*exponential backoff*: 0.5s, 1s, 2s...) and honour `Retry-After`.
Inject `sleep` so tests don't actually wait.

**Webhooks** are the reverse: a service calls YOUR URL. Verify it's genuine with an HMAC
signature: `hmac.new(secret, body, hashlib.sha256).hexdigest()` and compare with
`hmac.compare_digest` (constant time). Add a timestamp check to stop replays.

**Real projects** use `httpx` or `requests` (nicer API, same ideas), and LLM SDKs wrap
all of this for you - but when something breaks, it's HTTP underneath.
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
            ## Ordering food over the web

            HTTP works like ordering in a restaurant. You (the **client**) give the waiter an
            order - the **request**. The kitchen (the **server**) sends back a plate - the
            **response**. Every time your code calls an LLM API, that's one order and one plate.

            The order has to say *where* it goes. That's the **URL**, and it has parts:

            `https://api.example.com/v1/models?limit=2`
            - `https` - the *scheme* (how to talk; `s` = encrypted)
            - `api.example.com` - the *host* (which restaurant)
            - `/v1/models` - the *path* (which item on the menu)
            - `limit=2` - the *query string* (extra options: "no onions")

            Python's `urllib.parse` splits and builds URLs for you:

            ```python
            from urllib.parse import urlparse, urlencode

            parts = urlparse("https://example.com/docs?page=3")
            print(parts.netloc, parts.path, parts.query)
            print(urlencode({"lang": "en", "page": 3}))
            ```

            `urlencode` turns a dict into `key=value` pairs joined by `&`, and escapes
            characters that aren't allowed in URLs (a space becomes `+`). The host part is
            called `netloc` ("network location") in `urlparse`.
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
            ## Query strings: the "no onions, extra cheese" part

            Many API requests carry options in the URL, after a `?`. That's the
            **query string**: `?q=cats&limit=5`. Each option is a `key=value` pair, pairs are
            joined with `&`.

            Gluing these together by hand breaks as soon as a value contains a space, `&` or
            `=` (the server would think a new option started). So we let `urlencode` do it:

            ```python
            from urllib.parse import urlencode

            params = {"q": "fish & chips", "limit": 5}
            query = urlencode(params)
            print(query)
            print("https://api.example.com/search?" + query)
            ```

            `&` inside a value becomes `%26` - this is called *percent-encoding* (or URL
            encoding). The server decodes it back to `&`.

            **Watch out:** don't write `f"?q={text}"` with raw user text. Use `urlencode`.
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
            ## Status codes: the waiter's one-number summary

            Every response starts with a three-digit **status code**. Think of it as the
            waiter's quick summary before you even look at the plate. The first digit is
            the family:

            - **2xx - success.** `200 OK`, `201 Created`, `204 No Content`.
            - **3xx - go elsewhere.** The dish moved to another table (a *redirect*).
            - **4xx - your mistake.** `400` bad order, `401` no/bad API key, `404` no such
              dish, `429` you're ordering too fast.
            - **5xx - the kitchen's problem.** `500` error, `502`/`503` temporarily down.

            ```python
            for code in [200, 404, 503]:
                family = code // 100
                print(code, "family", family)
            ```

            `//` is whole-number division, so `404 // 100` is `4`. The difference between
            4xx and 5xx matters a lot later: a 4xx means *fix your request*, a 5xx often
            means *try again in a moment*.
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
            ## Headers: the notes stapled to your order

            Besides the URL, a request carries **headers**: little labelled notes stapled to
            the order. "I'm allergic to nuts" - or, for APIs, "here is my membership card".

            Headers are name/value pairs, so in Python they're a dict:

            ```python
            api_key = "sk-demo-123"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            for name, value in headers.items():
                print(f"{name}: {value}")
            ```

            - `Authorization: Bearer <key>` is how most LLM APIs (OpenAI and many others)
              receive your key. "Bearer" means "whoever carries this token is allowed in".
            - `Content-Type: application/json` tells the server the body is JSON.

            The format is strict: the word `Bearer`, **one space**, then the key. The server
            compares it character by character, and a missing space means `401 Unauthorized`.

            **Watch out:** never print or log a real API key.
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
            ## The body: what's actually in the envelope

            A `GET` request is like asking "what's on the menu?" - no package needed. A `POST`
            request sends something: a chat message, a document to embed. That something is
            the **body**, and for APIs it's almost always **JSON**.

            One catch: the network carries **bytes**, not Python strings. So sending is two
            steps - dict to JSON text, then text to bytes:

            ```python
            import json

            payload = {"model": "small", "messages": [{"role": "user", "content": "café?"}]}
            text = json.dumps(payload)
            body = text.encode("utf-8")
            print(type(text).__name__, type(body).__name__)
            print(json.loads(body) == payload)
            ```

            `.encode("utf-8")` turns text into bytes using the *UTF-8 encoding*, which can
            represent every character (é, 日本, emoji). Going back, `json.loads` accepts the
            bytes directly.

            **Watch out:** `str(payload)` is NOT JSON (it uses single quotes and `True`
            instead of `true`). Always use `json.dumps`.
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
            ## Reading the options back out

            Sometimes you're on the other side: you receive a URL (a callback link, a
            pagination "next" link) and need one option out of it. `urllib.parse` has the
            reverse tools:

            ```python
            from urllib.parse import urlparse, parse_qs

            url = "https://app.io/callback?code=abc123&tag=a&tag=b&q=hello+world"
            query = urlparse(url).query
            params = parse_qs(query)
            print(params)
            print(params["code"][0])
            print(params.get("missing"))
            ```

            `parse_qs` ("parse query string") returns a dict where **every value is a list**,
            because a key may appear more than once (`tag=a&tag=b`). It also decodes the
            percent-encoding for you (`+` becomes a space).

            **Watch out:** `params["code"]` is `["abc123"]`, a list. Take `[0]` to get the
            string. And use `.get()` for keys that might be missing.
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
            ## Writing the order slip

            Before the waiter goes to the kitchen, they write an order slip with everything
            on it: table, dishes, notes. In the standard library that slip is
            `urllib.request.Request`. It holds the URL, method, headers and body - but
            creating it doesn't send anything yet.

            ```python
            from urllib.request import Request

            req = Request("https://api.example.com/v1/chat",
                          data=b'{"q": "hi"}',
                          headers={"Content-Type": "application/json"},
                          method="POST")
            print(req.get_method())
            print(req.full_url)
            print(req.data)
            ```

            If you don't pass `method`, `Request` guesses: **GET** when there's no body, and
            **POST** when you pass `data`. The body (`data`) must be *bytes*.

            Sending it happens later with `urlopen(req, timeout=...)`, which returns the
            *response*. You'll do that next.
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
            ## Sending the order: urlopen

            Time to actually talk to a server. `urllib.request.urlopen` sends a request and
            hands you the **response**. The response is like a sealed container: you read
            its body once, as bytes.

            ```python
            import json
            from urllib.request import urlopen

            # (needs a real server - in the exercise the checks start one for you)
            def show_models(url):
                with urlopen(url, timeout=5) as resp:
                    print(resp.status)               # e.g. 200
                    data = json.loads(resp.read())   # bytes -> Python dict
                return data

            print(json.loads(b'{"models": ["a", "b"]}'))   # what the parsing step does
            ```

            - `with ... as resp:` closes the connection when you're done (a *context manager*).
            - `resp.read()` returns the body as bytes; `json.loads` accepts bytes.
            - `resp.status` is the status code.
            - `timeout=5` means "give up after 5 seconds". Always pass one.

            In this exercise the checks run a tiny web server on your own machine
            (`http://127.0.0.1:<port>`) and give your function its URL. No internet needed.
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
            ## A full API call: method + headers + body

            This is the shape of almost every LLM API call: **POST** a JSON body, with your
            key in an `Authorization` header. You fill in the order slip (`Request`) with all
            three, then hand it to `urlopen`.

            ```python
            import json
            from urllib.request import Request

            body = json.dumps({"prompt": "hi"}).encode("utf-8")
            req = Request("https://api.example.com/v1/complete",
                          data=body,
                          headers={"Authorization": "Bearer sk-demo",
                                   "Content-Type": "application/json"},
                          method="POST")
            print(req.get_method(), req.get_header("Content-type"))
            # then: with urlopen(req, timeout=5) as resp: ...
            ```

            `Request` stores header names with only the first letter capitalised
            (`Content-type`), which is fine: header names are *case-insensitive*.

            In real projects you'd write `httpx.post(url, json=payload, headers=...)` and it
            does the encoding for you - but it sends exactly the same bytes.
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
            ## Error responses arrive as exceptions

            When the kitchen sends back "sorry, we're out of that" (a 404) or "the oven broke"
            (a 500), `urlopen` doesn't return normally. It **raises** `urllib.error.HTTPError`.
            That error object is also a response: it has the status and the body, which
            usually explains what went wrong.

            ```python
            from urllib.error import HTTPError
            import io

            err = HTTPError("https://x.io/v1/nope", 404, "Not Found", {}, io.BytesIO(b"no such model"))
            try:
                raise err          # this is what urlopen does for a 404
            except HTTPError as e:
                print(e.code)
                print(e.read().decode("utf-8"))
            ```

            - `e.code` - the status code (404, 429, 500...)
            - `e.read()` - the error body, as bytes
            - `e.headers` - the response headers

            Catching it lets your code decide what to do: show the message, retry, or give up.

            **Watch out:** `HTTPError` lives in `urllib.error`, not `urllib.request`.
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
            ## Timeouts: how long you'll wait for your food

            If your order never comes, you don't sit in the restaurant for a week. You wait a
            reasonable time, then leave. A **timeout** is that limit for a request. Without
            one, a stuck server can freeze your whole app - forever.

            `urlopen(url, timeout=2)` gives up after about 2 seconds of silence. Giving up
            shows up as an exception:
            - `TimeoutError` - the server connected but didn't answer in time,
            - `urllib.error.URLError` - the server couldn't be reached (wrong port, down,
              or a timeout while connecting).

            ```python
            from urllib.request import urlopen
            from urllib.error import URLError

            try:
                urlopen("http://127.0.0.1:9/", timeout=0.5)   # port 9: nothing listening
            except (TimeoutError, URLError) as err:
                print("gave up:", type(err).__name__)
            ```

            You can catch several exception types at once with a tuple:
            `except (TimeoutError, URLError):`. LLM calls can legitimately take 30-60 s, so
            real timeouts are often generous - but they are always set.
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
            ## Retries and backoff: knocking again, politely

            Some failures are temporary. `429 Too Many Requests` means "you're going too fast,
            wait a bit". `500`/`502`/`503` often mean "the kitchen is swamped, try again".
            LLM APIs return these a LOT under load. Others are permanent: `400` (bad request),
            `401` (bad key), `404` - retrying just fails again.

            When you retry, wait a little longer each time, like knocking on a door: knock,
            wait 1 s, knock, wait 2 s, wait 4 s... That's **exponential backoff**: the delay
            doubles every attempt, up to a maximum (a *cap*).

            ```python
            base, cap = 0.5, 8
            for attempt in range(6):
                delay = min(base * 2 ** attempt, cap)
                print(attempt, delay)
            ```

            If the server sends a `Retry-After` header (a number of seconds), it's telling
            you exactly how long to wait - use that instead of your own guess. Header values
            are always text, so `"2"` needs `float()`.
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
            Putting it together: one helper that builds the request, sends it and turns both
            success and error responses into `(status, data)`.
        ''',
        "prompt": r'''
            Every API client ends up with one function that does the HTTP plumbing. Write it.

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
            Webhooks flip HTTP around: a service (a payment provider, GitHub, an LLM batch job)
            sends a POST to *your* server when something happens. Anyone can POST to your URL,
            so the sender signs the body with a shared secret. An **HMAC** is that signature:
            only someone with the secret can produce it, and changing one byte of the body
            changes it completely.

            ```python
            import hashlib, hmac
            sig = hmac.new(b"secret", b'{"event": "done"}', hashlib.sha256).hexdigest()
            print(sig[:16], len(sig))
            ```

            Compare signatures with `hmac.compare_digest`, never `==`: `==` stops at the first
            different character, and the time it takes leaks how much of a guess was right
            (a *timing attack*).
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
