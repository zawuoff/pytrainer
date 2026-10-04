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
            ## Reading a web address part by part

            When you type a question into a chat app, the answer is not worked out on your computer. Your
            program writes a message, sends it to another computer, and waits. A program on that computer
            does the work and sends a message back. Every call to an LLM happens this way, and so does
            every web page you open.

            Step through one round trip:

            ```diagram
            {"type":"flow","title":"One request and one response","steps":[
            {"label":"Write the message","detail":"Your program writes a message that says what it wants and which address the message is for."},
            {"label":"Send it and wait","detail":"The message travels over the internet to the computer that the address names. Your program does nothing else until an answer arrives."},
            {"label":"The other side works","detail":"A program on that computer has been waiting for messages. It reads yours and prepares an answer."},
            {"label":"The answer comes back","detail":"That program sends one message back. Your program stops waiting, reads the answer and carries on."}
            ]}
            ```

            Each piece has a name. The message that asks is a **request**, and the message that answers
            is a **response**. The program that asks is the **client**, and the program that answers is
            the **server**. The rules for writing the two messages are called **HTTP**. The set of
            requests that a server accepts from other programs is called its **API**.

            ### Where the request goes

            A request has to say where it is going, so it carries an address. Python can split an address
            into its parts:

            ```python
            from urllib.parse import urlparse

            parts = urlparse("https://docs.example.com/guide/install?lang=en")
            print(parts.scheme)
            # https
            print(parts.netloc)
            # docs.example.com
            print(parts.path)
            # /guide/install
            print(parts.query)
            # lang=en
            ```

            An address like this is called a **URL**. It has four parts:

            - The **scheme**, `https`, names the rules to use. `https` is HTTP with every message
              scrambled on the way, so that nobody in between can read it.
            - The **host**, `docs.example.com`, names the server. Python calls this part `netloc`, short
              for "network location".
            - The **path**, `/guide/install`, names one thing on that server. It keeps the `/` at its
              front.
            - The **query string**, `lang=en`, holds extra options. The `?` in front of it is only a
              separator and belongs to no part.

            Here is another URL: `https://api.weather.dev/v2/forecast?city=Oslo`. Match each piece of it
            with what it is.

            ```match
            `https` :: the scheme: which rules the two programs follow
            `api.weather.dev` :: the host: which server gets the request
            `/v2/forecast` :: the path: which thing on that server
            `city=Oslo` :: the query string: extra options
            ---
            The scheme ends at `://`, the host ends at the next `/`, and the path ends at the `?`.
            ```

            ### Writing the options

            `urlencode` works in the other direction, for the query string only. You give it a dict, and
            it writes each key and value as `key=value` and joins the pairs with `&`:

            ```python
            from urllib.parse import urlencode

            print(urlencode({"lang": "en", "page": 3}))
            # lang=en&page=3
            ```

            A URL may not contain a space. `urlencode` writes each space as `+`, and the server turns it
            back into a space. The next step looks at this more closely.

            ```predict
            from urllib.parse import urlencode

            print(urlencode({"city": "New York", "days": 3}))
            ---
            Each pair is written as `key=value` and the pairs are joined with `&`. The space in
            `New York` becomes `+`, so the line is `city=New+York&days=3`.
            ```

            **Watch out:** `urlparse` needs the scheme. Without `https://` at the front it cannot find the
            host: `urlparse("docs.example.com/guide")` puts the whole text into `path` and leaves `netloc`
            empty. There is no error to warn you.

            **In short:** a request goes to a URL, and `urlparse` splits a URL into its scheme, host
            (`netloc`), path and query.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
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
            `urlparse` splits the address into its parts. The scheme is everything before `://`, so the
            first line is `https`. `netloc` is the host, `api.example.com`. The path starts at the first
            `/` after the host and stops at the `?`, and it keeps its leading slash: `/v1/models`. The
            query is what comes after the `?`, without the `?` itself: `limit=2`.

            The last line comes from `urlencode`. It writes each pair of the dict as `key=value` and joins
            the pairs with `&`. The space in `hello world` becomes `+`, and the number 2 is written as
            text, so the line is `q=hello+world&page=2`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The first four lines are the four parts of the address inside the quotes. Before you type anything, find where each part starts and where it stops.",
            "The scheme stops before `://`. The host stops at the next `/`. The path stops at the `?`. For each of those separators, decide whether it is kept in a part or belongs to no part. The lesson says which.",
            "For the last line, write each pair of the dict as key, equals sign, value, and join the pairs with the character that separates options in a query string. Then think about what `urlencode` does to the space inside a value.",
        ],
    },
    {
        "id": "http-s2",
        "title": "Build a URL with a query string",
        "difficulty": 0,
        "lesson": r'''
            ## Sending options along in the address

            Your app lets people search a help centre, and it passes their words on to a search API. The
            words travel in the query string, the part of the URL after the `?`. Someone searches for
            `R&D`. Can you put those characters straight into the address?

            ```python
            words = "R&D"
            print(f"https://api.example.com/search?q={words}&limit=5")
            # https://api.example.com/search?q=R&D&limit=5
            ```

            It prints, but the address no longer says what you meant. In a query string, `&` means "the
            next option starts here" and `=` means "the value starts here". The server sees only
            characters. It cannot tell the `&` that the user typed from the `&` that you wrote as a
            separator.

            ```quiz
            The server receives the query string `q=R&D&limit=5`. What does it take as the value of `q`?
            - [x] `R` :: Right. To the server, the value of `q` ends at the first `&`. The search runs for the single letter R.
            - [ ] `R&D` :: That is what you meant. The server cannot know it, because to the server every `&` starts a new option.
            - [ ] `R&D&limit=5` :: The server does split the query string into options. It splits at every `&`, and that includes the one inside the user's text.
            ```

            The way out is to write such characters in a form that cannot be mistaken for a separator.
            `urlencode`, which you met in the last step, does this for every value in a dict:

            ```python
            from urllib.parse import urlencode

            options = {"q": "R&D", "limit": 5}
            print(urlencode(options))
            # q=R%26D&limit=5
            print(urlencode({"q": "cats and dogs"}))
            # q=cats+and+dogs
            ```

            The `&` inside the value became `%26`. The `&` between the two options stayed, because that
            one really is a separator. Each space became `+`, because a URL may not contain a space. The
            server first splits the options and then turns `%26` and `+` back, so it ends up with exactly
            the text the user typed.

            Writing a character as `%` and a code is called **percent-encoding**. The code is the number
            of the character, and you never have to work it out yourself.

            ```predict
            from urllib.parse import urlencode

            print(urlencode({"q": "AT&T news", "page": 2}))
            ---
            The `&` inside the value is written as `%26` and the space as `+`. The `&` in front of `page`
            separates two options, so it stays. The line is `q=AT%26T+news&page=2`.
            ```

            `urlencode` gives you the options and nothing else. The front of the URL and the `?` are
            yours to add. Put these lines in an order that prints
            `https://api.example.com/search?q=large+language+models&limit=3`:

            ```order
            from urllib.parse import urlencode
            options = {"q": "large language models", "limit": 3}
            query = urlencode(options)
            url = "https://api.example.com/search?" + query
            print(url)
            ---
            The dict has to exist before `urlencode` can read it, and the query has to exist before it can
            be joined to the front of the URL. The `?` is part of the front, because `urlencode` does not
            add it.
            ```

            **Watch out:** a query string built by hand with an f-string works in every test where the
            value is one plain word. It breaks, without any error, on the first value that contains a
            space, `&` or `=`. Use `urlencode` for every query string.

            **In short:** `urlencode(a_dict)` writes the options of a query string and makes every value
            safe, and you add the `?` in front yourself.
        ''',
        "prompt": r'''
            A search API takes its options in the query string of the URL. The text that people search for
            can contain spaces and characters such as `&`, so the options must be encoded before they go
            into the address.

            **Your job:** finish `build_url(base, path, params)` so that it gives back the full URL with
            the options at the end. The function is already written except for one gap, marked `___`.
            Replace the gap.

            **What goes in**
            - `base`: the scheme and host of the server, for example `"https://api.example.com"`
            - `path`: the path, starting with `/`, for example `"/v1/search"`
            - `params`: a dict with at least one option, for example `{"q": "hello world", "limit": 5}`

            **What comes out**
            - one string: `base`, then `path`, then `?`, then the options as a query string, for example
              `"https://api.example.com/v1/search?q=hello+world&limit=5"`

            **Rules**
            - The options come in the same order as in the dict.
            - Values are encoded the way the lesson showed: a space becomes `+`, and `&` becomes `%26`.
            - A value may be a number. It is written as text.

            **Examples**
            ```python
            build_url("https://api.example.com", "/v1/search", {"q": "hello world", "limit": 5})
            # returns "https://api.example.com/v1/search?q=hello+world&limit=5"
            build_url("https://x.io", "/s", {"q": "a&b"})
            # returns "https://x.io/s?q=a%26b"
            build_url("http://localhost:8000", "/health", {"verbose": "yes"})
            # returns "http://localhost:8000/health?verbose=yes"
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
            "The last line of the function already joins the base, the path, the `?` and the query. Only the query itself is missing. Which function in the lesson turns a dict into a query string?",
            "That function is already imported at the top of the file. It needs one thing handed to it: the dict that holds the options.",
            "Replace the gap with a call to the imported function, and hand it the parameter that holds the options. Do not add a `?` in the gap, because the last line already puts one in.",
        ],
    },
    {
        "id": "http-s3",
        "title": "What does this status code mean?",
        "difficulty": 0,
        "lesson": r'''
            ## Did it work? Reading the status code

            You sent a request, and a response came back. Before you read anything else in it, you want to
            know one thing: did the server do what you asked? Every response answers that question with a
            three-digit number at its very start. You have probably met one already: the `404` that a
            browser shows for a page that does not exist.

            A few numbers come up again and again:

            - `200`: it worked.
            - `201`: it worked, and the server created something new.
            - `401`: the server does not know who you are. The key is missing or wrong.
            - `404`: there is nothing at that address.
            - `429`: you are sending requests too fast.
            - `500`: the server hit an error of its own.
            - `503`: the server cannot answer right now, often because it is too busy.

            This number is called the **status code**. You do not have to learn every code, because the
            first digit already tells you the kind of answer:

            - 200 to 299, written **2xx**: success.
            - 300 to 399, **3xx**: what you asked for is at another address. This is called a
              **redirect**.
            - 400 to 499, **4xx**: the problem is on your side. Programmers call this a **client error**.
            - 500 to 599, **5xx**: the server failed. This is a **server error**.

            ```match
            `200` :: it worked
            `401` :: the key is missing or wrong
            `404` :: nothing exists at this address
            `429` :: too many requests, slow down
            `503` :: the server cannot answer right now
            ---
            The codes that start with 4 are about your side. The one that starts with 5 is about the
            server.
            ```

            The two kinds of error call for different reactions. After a 4xx code, the same request gets
            the same answer, so something on your side has to change. After a 5xx code your request may
            be perfectly fine, and the same request often works a moment later.

            ```quiz
            A request that worked yesterday comes back with `503` today. Your code has not changed. What is the sensible reaction?
            - [x] Wait a moment and send the same request again :: Right. A 5xx code says that the server failed, not your request. The same request often works a little later.
            - [ ] Look for the mistake in the request :: That is the reaction to a 4xx code. A 5xx code says that the failure is on the server's side.
            - [ ] Treat it as a success, because a response came back :: A response comes back whenever the server can be reached. Only a 2xx code means that it did what you asked.
            ```

            In code you test a whole group with a chained comparison, which you know from the
            Conditionals chapter:

            ```python
            for status in [201, 404, 503]:
                worked = 200 <= status <= 299
                print(status, worked)
            # 201 True
            # 404 False
            # 503 False
            ```

            Pick the test that makes this program print `fix the request`:

            ```fill
            status = 404
            if ___:
                print("fix the request")
            else:
                print("the request may be fine")
            ---
            - [x] 400 <= status <= 499 :: Right. 404 lies between 400 and 499, so it is a client error, and the fix is on your side.
            - [ ] 500 <= status <= 599 :: 404 is not in the 5xx group, so the test is false and the program prints `the request may be fine`.
            - [ ] status == 400 :: `400` is one code of the group, not the whole group. 404 is not equal to 400, so the test is false.
            ```

            **Watch out:** `200` is not the only success. An API that creates something answers `201`,
            and one that has nothing to send back answers `204`. Code that tests `status == 200` reports
            both as failures. Test the whole range from 200 to 299.

            **In short:** the first digit of the status code says how the request went: 2xx worked, 4xx
            is a problem on your side, 5xx is a problem on the server.
        ''',
        "prompt": r'''
            A log line that only says `429` or `502` means little to the person who reads it. A short
            label next to the number tells them at a glance which kind of answer it was.

            **Your job:** finish `status_kind(code)` so that it gives back the label for the group that a
            status code belongs to. The first group is already written in the editor.

            **What goes in**
            - `code`: a status code as a whole number, for example `200`

            **What comes out**
            - one of five strings:
              - `"success"` for 200 to 299
              - `"redirect"` for 300 to 399
              - `"client error"` for 400 to 499
              - `"server error"` for 500 to 599
              - `"unknown"` for every other number

            **Rules**
            - Both ends of a range belong to it: `299` is a success and `499` is a client error.
            - A number below 200 or above 599 is not a status code this function knows, so it gives
              `"unknown"`. The checks try `0`, `99` and `600`.
            - The labels must be spelled exactly as above, in lower case.

            **Examples**
            ```python
            status_kind(200)    # returns "success"
            status_kind(301)    # returns "redirect"
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
            "The code in the editor already handles one group. Read how it tests the range, and what it does when the test is true.",
            "Each of the other groups needs a test of the same shape, with its own two numbers and its own label. Something also has to happen for a number that fits no group.",
            "In place of the `...`, write three more tests like the first one, one for each remaining group, and hand back that group's label inside each. After the last test, on a line that is reached only when no group matched, hand back the fallback label.",
        ],
    },
    {
        "id": "http-s4",
        "title": "Fix: the API key header",
        "difficulty": 0,
        "lesson": r'''
            ## Tell the server how to interpret your request

            A URL says where to send a request, but it does not say what format you are sending or which credential you are using. Those details travel alongside the request as named pieces of text.

            ```python
            headers = {"Accept": "application/json", "X-Request-Id": "demo-7"}
            for name, value in headers.items():
                print(f"{name}: {value}")
            # Accept: application/json
            # X-Request-Id: demo-7
            ```

            These name-and-value pairs are **headers**. A dictionary is a convenient way to describe them in Python. Header names identify the detail; header values contain the detail itself. `Accept` describes the response formats the client wants, while `Content-Type` describes the format of a body being sent.

            ```match
            URL :: where the request is sent
            Accept :: which response format the client wants
            Content-Type :: which format the sent body uses
            Authorization :: which credential the request presents
            ```

            An `Authorization` header often uses the form `Bearer <credential>`. The word `Bearer` names the authentication scheme, and the space separates it from the credential. A **bearer token** can be used by whoever possesses it; the server must still check whether it is valid and permitted for the request.

            Whitespace in a value is not decorative. Concatenating two strings inserts nothing automatically. Inspect the resulting value carefully when a server reports an authentication failure.

            ```predict
            scheme = "Demo"
            credential = "sample"
            print(scheme + credential)
            print(scheme + " " + credential)
            ---
            Concatenation preserves only characters you explicitly supply. The first result has no separator; the second contains one space.
            ```

            **Watch out:** a malformed or invalid authorization value may produce a `401` response. Inspect formats with demonstration credentials, not real secrets in logs.

            **In short:** headers carry request details, and their values must follow the format the server expects.
        ''',
        "prompt": r'''
            The server rejects requests made with this helper. The starter already builds the two required headers, but one value has the wrong format.

            **Your job:** fix `auth_headers(api_key)` so its dictionary matches the required header values.

            **What goes in**
            - `api_key`: the credential string, such as `"sk-123"`.

            **What comes out**
            - A dictionary containing exactly `Authorization` and `Content-Type`.

            **Rules**
            - Authorization contains the word `Bearer`, one space, and the unchanged key.
            - Content-Type contains `application/json`.
            - Keep the supplied key unchanged, including any punctuation.

            **Examples**
            ```python
            auth_headers("sk-123")
            # {"Authorization": "Bearer sk-123", "Content-Type": "application/json"}
            auth_headers("")
            # {"Authorization": "Bearer ", "Content-Type": "application/json"}
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
            "Inspect the finished authorization value, not just its two ingredients.",
            "The authentication scheme and the credential are separate parts of the header value. Compare their boundary with the specified format.",
            "Check the required characters in order, including separators, and adjust only the malformed authorization construction while keeping both required headers.",
        ],
    },
    {
        "id": "http-s5",
        "title": "A JSON request body",
        "difficulty": 0,
        "lesson": r'''
            ## Turn a Python value into bytes for sending

            Your program holds a dictionary, but a network request cannot transmit a live Python dictionary. It needs a portable description of the data, then a sequence of bytes carrying that description.

            ```python
            import json
            payload = {"enabled": True, "label": "tea"}
            text = json.dumps(payload)
            raw = text.encode("utf-8")
            print(text)
            # {"enabled": true, "label": "tea"}
            print(type(raw).__name__)
            # bytes
            ```

            The data carried after the request's headers is its **body**. For a JSON body, `json.dumps` first produces JSON text. Encoding then translates the characters into bytes. **UTF-8** is the rule that describes this translation, including characters outside the English alphabet.

            ```predict
            import json
            value = {"missing": None, "active": False}
            print(str(value))
            print(json.dumps(value))
            ---
            Python's display uses None and False with single-quoted keys. JSON uses null and false with double-quoted keys. They are different text formats.
            ```

            A `bytes` value is a sequence of byte values rather than text characters. Python displays it with a `b` prefix. Going the other direction, decoding converts bytes into text, and JSON parsing reconstructs ordinary Python values. `json.loads` can also read JSON bytes directly.

            ```quiz
            Which property matters most when checking an encoded JSON body?
            - [x] Parsing it reconstructs the intended value :: Equivalent JSON may use different whitespace or escape forms.
            - [ ] It looks exactly like str of the dictionary :: Python's display syntax is not the JSON format.
            ```

            **Watch out:** `str` is not a JSON serializer. A body that looks plausible to a person may still be rejected with a JSON decoding error because its quotes or special values use Python syntax.

            **In short:** serialize the value as JSON, then encode the JSON text as UTF-8 bytes.
        ''',
        "prompt": r'''
            Before a chat request goes over the wire, its payload must become bytes.

            **Your job:** write `json_body(payload)`

            **What goes in**

            - `payload`: a dict, e.g. `{"model": "small", "stream": False}`

            **What comes out**
            - `bytes` containing the payload as JSON, encoded with UTF-8

            **Rules**
            - The result must be of type `bytes` (not `str`).
            - It must be valid JSON that `json.loads` turns back into an equal dict (including non-English text like `"caf\u00e9"`).

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
            "There are two distinct conversions before a dictionary can be sent.",
            "First create valid JSON text, then convert that text to bytes with the required character encoding.",
            "Use the JSON serializer, encode its result with UTF-8, and return the encoded value. Verify that parsing it recovers the original dictionary.",
        ],
    },
    {
        "id": "http-s6",
        "title": "Read a query parameter",
        "difficulty": 0,
        "lesson": r'''
            ## Read an option from a URL

            A link may contain a search term or a cursor pointing to another page. You need to read that option without confusing encoded punctuation with separators between options.

            ```python
            from urllib.parse import urlparse, parse_qs
            url = "https://example.test/search?topic=red+fox&tag=x&tag=y"
            params = parse_qs(urlparse(url).query)
            print(params)
            # {'topic': ['red fox'], 'tag': ['x', 'y']}
            ```

            `urlparse` separates the URL into its components. Its `.query` attribute contains only the query text after the question mark. `parse_qs` then parses that text, undoing the encoding used for spaces and special characters.

            Each dictionary value is a list because a query parameter can appear repeatedly. The list preserves those occurrences in order. Even a single value is wrapped in a list, so reading the dictionary alone does not yet give you the string your caller wants.

            ```predict
            from urllib.parse import parse_qs
            params = parse_qs("q=a%26b&q=c+d")
            print(params["q"])
            print(params["q"][0])
            ---
            The encoded ampersand belongs inside a value rather than separating parameters. The first occurrence decodes to a&b, and the second to c d.
            ```

            Decide what absence should mean before indexing. A missing key may use a supplied default rather than being an error. Also, `parse_qs` ignores empty values by default; retaining explicitly blank parameters requires its `keep_blank_values` option.

            ```quiz
            Why is splitting the whole URL at every ampersand insufficient?
            - [x] Parsing and decoding are separate concerns :: You first need the query component and then must interpret its encoded values correctly.
            - [ ] A query cannot repeat a name :: Repeated names are allowed and explain the lists in the result.
            ```

            **Watch out:** indexing a missing dictionary key raises `KeyError`. Read an optional key safely before choosing one of its values.

            **In short:** isolate the query, parse its lists of decoded values, and handle absence before selecting a value.
        ''',
        "prompt": r'''
            An OAuth-style callback URL carries values in its query string. Pull one out.

            **Your job:** write `get_param(url, name, default=None)`

            **What goes in**

            - `url`: a full URL string, e.g. `"https://x.io/s?q=hello+world&page=2"`
            - `name`: the parameter name, e.g. `"q"`
            - `default`: what to return if the parameter is missing

            **What comes out**
            - the parameter's value as a decoded string; if it appears several
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
            "Review the query parser's result shape: names map to lists.",
            "Separate the URL's query before parsing it, then look up the requested name safely.",
            "Obtain the decoded value list. If none is available, use the caller's default; otherwise select the earliest value without converting its type.",
        ],
    },
    {
        "id": "http-s7",
        "title": "Anatomy of a Request object",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Inspect a request before sending it

            Before contacting a service, you may want to check the destination, method, and body. Python lets you package those choices into an object without sending anything yet.

            ```python
            from urllib.request import Request
            request = Request("https://example.test/items/4", method="DELETE")
            print(request.get_method())
            # DELETE
            print(request.full_url)
            # https://example.test/items/4
            print(request.data)
            # None
            ```

            A `Request` object stores the request description. Its `full_url` attribute keeps the destination and its `data` attribute holds body bytes, if supplied. `get_method` reports the HTTP method. A later call to `urlopen` actually sends the request.

            ```predict
            from urllib.request import Request
            request = Request("https://example.test/notes", data=b"{}", method="PUT")
            print(request.get_method())
            print(request.data)
            ---
            The explicit method is PUT even though the object has a body. The data attribute holds the exact supplied bytes; constructing the object has made no network call.
            ```

            If you omit the method, a request with no body defaults to GET. Supplying body data changes that default to POST. An explicit method overrides the default. Reading code therefore requires checking both the method argument and whether data was supplied.

            Headers can be supplied as a dictionary. `get_header` reads a stored value. The object may normalize the spelling of header names, but their values remain the data you supplied.

            ```quiz
            Which operation actually contacts the server?
            - [x] Opening the request with urlopen :: Request construction and inspection only prepare data.
            - [ ] Reading full_url :: This only accesses a stored attribute.
            - [ ] Calling get_method :: This reports the selected method without sending it.
            ```

            **Watch out:** a dictionary is not an acceptable request body for sending. Convert structured data to encoded bytes before passing it as data.

            **In short:** a Request describes an HTTP operation; urlopen performs it.
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
            Neither object supplies an explicit method. The object without data therefore reports GET, while the object carrying body bytes reports POST. The third print reads the full_url stored on post_req, not get_req. The final print reads that same object's Authorization value, including the space separating Bearer from the demonstration key. Request construction only stores these choices; it does not send either request.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Neither request explicitly chooses its method. Look for the presence or absence of a body.",
            "Determine each default method independently, then inspect which stored object the remaining print calls read.",
            "Trace the printed method values first. For the remaining lines, read the POST object's destination and its supplied authorization value exactly, including spaces.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "http-1",
        "title": "GET some JSON",
        "difficulty": 1,
        "lesson": r'''
            ## Read and parse a response body

            The server has sent a JSON response. Your application needs Python values from that response, and it should release the response resource when reading is finished.

            ```python
            import json
            from urllib.request import urlopen
            url = 'data:application/json,{"count": 4}'
            with urlopen(url, timeout=3) as response:
                raw = response.read()
                remaining = response.read()
            print(json.loads(raw))
            # {'count': 4}
            print(remaining)
            # b''
            ```

            This example uses a `data:` URL, whose content is embedded directly in the URL. It makes no network request, but illustrates the reading interface. With an HTTP URL, `urlopen` sends the request and returns a response. Passing a URL string requests GET.

            The response body arrives as bytes. `read` consumes those bytes, so the second call finds nothing left. Store the first result if more than one operation needs it. `json.loads` parses those bytes into ordinary Python data.

            ```quiz
            You read the response once to print it, then read it again to parse JSON. Why might parsing fail?
            - [x] The second read may be empty :: A response is consumed as it is read, rather than replayed from the beginning.
            - [ ] JSON parsing changes the network response :: The problem occurs before parsing because the bytes were already consumed.
            ```

            The `with` statement closes the response when its block ends, including when an error interrupts the block. A timeout gives network operations a waiting limit instead of relying on an indefinite wait.

            The exercises provide a local server. Its address starts with `127.0.0.1`, meaning your own machine. A **port**, the number after the host, selects which listening program receives the connection.

            **Watch out:** parsed JSON is not always a dictionary; a response can contain a list or another JSON value. Return the parsed value your server actually supplied.

            **In short:** open with a timeout, read the body once, parse its bytes, and close the response.
        ''',
        "prompt": r'''
            List the models an API offers by calling its endpoint.

            **Your job:** write `get_json(url)`

            **What goes in**

            - `url`: a full URL string, e.g. `"http://127.0.0.1:8000/v1/models"`

            **What comes out**
            - the response body parsed from JSON (usually a dict)

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
            "Sending, reading, and parsing are separate stages.",
            "Open the supplied URL with a timeout and keep the response inside a with block.",
            "Read the response bytes once, parse them as JSON, and return that parsed value while allowing the context manager to close the response.",
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
            ## Assemble the parts of a JSON request

            You now know how to prepare headers, encode JSON, and read a response. Sending structured input brings those parts together: the server needs both the data and enough information to understand it.

            ```python
            import json
            from urllib.request import Request
            request = Request("https://example.test/jobs",
                              data=json.dumps({"label": "scan"}).encode("utf-8"),
                              headers={"Content-Type": "application/json", "Accept": "application/json"},
                              method="POST")
            print(request.get_method())
            # POST
            print(json.loads(request.data))
            # {'label': 'scan'}
            ```

            The method specifies the operation. The body carries the data. The content-type header identifies its format. Supplying JSON bytes without the format header may leave a server treating the body as something else, depending on that service's rules.

            ```match
            POST :: the chosen request method
            encoded JSON :: the request body bytes
            Content-Type :: describes the body's format
            Authorization :: presents the credential separately from the body
            ```

            This example stops after preparation. To send the request, pass the Request object to `urlopen` where earlier you passed a URL string. The response is then read and parsed using the same steps as a GET response.

            Header names are **case-insensitive**, meaning upper and lower case do not change their identity. Request may store `Content-Type` as `Content-type`. Header values do not share a universal case rule: preserve credential values and follow each header's required format.

            ```quiz
            The server returns different data from the data you sent. Which value should a request helper return?
            - [x] The parsed response body :: Sending a payload does not imply that the response repeats that payload.
            - [ ] The original payload :: That would hide the actual answer from the service.
            ```

            **Watch out:** putting an API key in the JSON body does not substitute for the required authorization header. The server reads authentication from the location its interface specifies.

            **In short:** assemble method, headers, and encoded body, then send and read the response independently.
        ''',
        "prompt": r'''
            Send a chat request the way LLM APIs expect it.

            **Your job:** write `post_json(url, payload, api_key)`

            **What goes in**

            - `url`: full endpoint URL, e.g. `"http://127.0.0.1:8000/v1/chat"`
            - `payload`: a dict to send as the JSON body
            - `api_key`: a string, e.g. `"sk-test"`

            **What comes out**
            - the response body parsed from JSON

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
            "A Request can carry all outgoing parts before urlopen sends it.",
            "Prepare the encoded payload and required header values, then choose the explicit method.",
            "Construct the POST request with its JSON bytes and headers. Open it with a timeout, read the response once, and return the parsed response rather than the original payload.",
        ],
    },
    {
        "id": "http-3",
        "title": "When the server says no",
        "difficulty": 1,
        "lesson": r'''
            ## Read the server's explanation of an error

            A failed HTTP status often carries useful text explaining what went wrong. You want that status and message for a report instead of losing them when the request raises an exception.

            ```python
            from urllib.error import HTTPError
            from io import BytesIO
            error = HTTPError("https://example.test/job", 409, "Conflict", {}, BytesIO(b"already exists"))
            try:
                raise error
            except HTTPError as failure:
                print(failure.code)
            # 409
                print(failure.read().decode("utf-8"))
            # already exists
            ```

            The example constructs an error locally instead of contacting a server. `BytesIO` supplies a readable sequence of bytes held in memory. For an HTTP error response, `urlopen` raises an `HTTPError` carrying similar response information.

            The exception's `.code` holds its status. Its `read` method supplies body bytes, and `.headers` carries response headers. Decoding bytes with UTF-8 gives ordinary text. A normal successful response instead exposes its status through `.status`.

            ```match
            successful response status :: read from status
            HTTPError response status :: read from code
            response body :: read as bytes
            UTF-8 decoding :: turns body bytes into text
            ```

            Catch the error around the operation that sends the request. You can then convert both the success path and error path into the same return shape. This gives callers one consistent interface even though urllib delivers the two cases differently.

            ```quiz
            Does an HTTPError mean the server sent no response body?
            - [x] No :: The error object can carry the server's explanation as readable bytes.
            - [ ] Yes :: Raising is urllib's way of reporting the status, not proof that no body exists.
            ```

            **Watch out:** HTTPError belongs to `urllib.error`, not `urllib.request`. Also, its body is consumed when read, so retain it if you need it again.

            **In short:** an HTTP error is also response data that you can inspect and return deliberately.
        ''',
        "prompt": r'''
            A health-check tool needs the status code and body of any URL - including errors.

            **Your job:** write `fetch_status(url)`

            **What goes in**

            - `url`: a full URL string

            **What comes out**
            - a tuple `(status, text)`: the status code (int) and the body decoded as UTF-8 text

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
            "An HTTPError still carries status and body information.",
            "Handle the successful response and HTTP error paths separately, but make both produce the same output shape.",
            "Open with a timeout inside try. Read the normal status and bytes on success; catch HTTPError to read its code and bytes instead. Decode either body as UTF-8 before returning.",
        ],
    },
    {
        "id": "http-4",
        "title": "Don't wait forever",
        "difficulty": 1,
        "lesson": r'''
            ## Put a limit on waiting for a response

            A status check is only useful if it eventually returns. A server may stop responding, or the connection may never be established. Your caller needs a defined result for these failures instead of waiting indefinitely.

            ```python
            from urllib.error import URLError
            failures = [TimeoutError("slow operation"), URLError("unreachable")]
            for failure in failures:
                try:
                    raise failure
                except (TimeoutError, URLError) as caught:
                    print(type(caught).__name__)
            # TimeoutError
            # URLError
            ```

            This local example shows exception handling without a network. `TimeoutError` can report an operation that waited too long. `URLError` wraps a broader range of connection failures, sometimes including a timeout during connection setup. Catching a tuple of exception types lets one handler accept either form.

            A **timeout** limits waiting during blocking network operations. With urllib it is not a strict wall-clock deadline for an entire multi-step download: separate operations may each wait, and a server that continually sends data can keep a download active.

            ```quiz
            What must you do with a timeout value supplied by your caller?
            - [x] Pass it to the operation that can block :: Merely accepting a parameter does not make the network operation use it.
            - [ ] Store it without changing the request :: A stored number cannot interrupt a wait by itself.
            ```

            Choose the fallback required by your interface. Returning `None` can distinguish failure from a successful empty body, which decodes to an empty string. Avoid converting all failures to empty text if those outcomes have different meanings.

            ```predict
            print("" is None)
            print(bool(""), bool(None))
            ---
            An empty successful result and a missing result are different values, even though both are false in a truth test.
            ```

            **Watch out:** HTTPError is also a kind of URLError. Catching URLError includes HTTP errors unless you handle them separately first.

            **In short:** pass an explicit waiting limit to the network operation and define how connection failures reach callers.
        ''',
        "prompt": r'''
            A status page pings a service. It must never hang.

            **Your job:** write `fetch_text(url, timeout)`

            **What goes in**

            - `url`: a full URL string
            - `timeout`: seconds to wait (a float, e.g. `0.1`)

            **What comes out**
            - the body decoded as UTF-8 text, or `None` if the server was too slow or unreachable

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
            "Accepting a timeout parameter is not enough; the network operation must receive it.",
            "Keep successful decoding inside try and let the two specified connection-failure types share one handler.",
            "Pass the supplied limit to urlopen, read and decode successful body bytes, and return the specified absent-result value when either permitted failure type is caught.",
        ],
    },
    {
        "id": "http-5",
        "title": "Should I retry?",
        "difficulty": 1,
        "lesson": r'''
            ## Decide whether another attempt is worthwhile

            A busy service may succeed if you try again later. A request with a bad credential usually needs correction instead. Before retrying, separate failures that your policy treats as temporary from those that should stop immediately.

            ```python
            initial_wait, maximum = 1.0, 10.0
            for retry_number in range(5):
                print(min(initial_wait * 2 ** retry_number, maximum))
            # 1.0
            # 2.0
            # 4.0
            # 8.0
            # 10.0
            ```

            A repeated request is a **retry**. Increasing the wait between attempts is **backoff**. Doubling it each time is **exponential backoff**. The maximum is a **cap**, preventing delays from growing without limit.

            The first retry uses exponent zero, so it starts at the initial wait. Count retries carefully: the original request is an attempt but is not itself a retry.

            ```predict
            base = 2.0
            print(base * 2 ** 0)
            print(base * 2 ** 2)
            ---
            The zero exponent gives the base wait unchanged. Two doublings give four times the base, or 8.0.
            ```

            A service may supply a `Retry-After` header. Under this exercise's policy, its numeric text overrides the calculated wait. Convert text to a number before using it. In general HTTP, that header can also contain a date; the exercise specifically accepts the numeric form.

            ```quiz
            A non-retryable status arrives with a suggested delay. Which decision comes first?
            - [x] Whether this request should be retried :: A delay does not turn a forbidden retry into an allowed one.
            - [ ] Always use the delay :: Timing is relevant only after retrying has been permitted.
            ```

            Real retry policies also consider whether repeating an operation could repeat a side effect. Here you are implementing a stated status policy, not deciding every production case.

            **Watch out:** sleeping after the final allowed attempt cannot lead to another request and only delays the error.

            **In short:** decide whether to retry first, then choose a server-supplied or bounded increasing delay.
        ''',
        "prompt": r'''
            Decide whether a failed request should be retried, and after how long.

            **Your job:** write `retry_delay(status, attempt, retry_after=None)`

            **What goes in**

            - `status`: the HTTP status code (int)
            - `attempt`: how many retries already happened (int, starts at `0`)
            - `retry_after`: the `Retry-After` header value as a string (e.g. `"3"`), or `None`

            **What comes out**
            - `None` if the status should NOT be retried; otherwise the number of
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
            "Decide eligibility before thinking about the length of the wait.",
            "A server-supplied delay overrides the calculated schedule only for retryable statuses.",
            "Reject statuses outside the allowed set. For eligible ones, convert a supplied delay to a float; otherwise calculate the doubling schedule and restrict it to the maximum.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "http-6",
        "title": "A reusable request helper",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## Give callers one consistent request interface

            Your app now needs several HTTP operations. Repeating header construction, encoding, and error handling in every method invites small inconsistencies. Put those boundary decisions in one helper with a predictable result shape.

            ```python
            import json
            bodies = [b'{"accepted": true}', b'[]', b'']
            for raw in bodies:
                result = json.loads(raw) if raw else None
                print(result)
            # {'accepted': True}
            # []
            # None
            ```

            Putting it together starts with separating outgoing data from incoming data. An absent outgoing payload means no body was supplied. An empty dictionary is still a real payload that can be encoded as JSON. Test absence with `is None`, rather than using truthiness to decide whether data exists.

            ```quiz
            The caller supplies an empty dictionary as the payload. Should the helper send no body?
            - [x] No :: An empty dictionary is a supplied JSON value, distinct from None.
            - [ ] Yes :: Treating every false value as absent would discard valid input.
            ```

            Next, normalize success and HTTP error responses to a status plus raw bytes. Their attribute names differ, but later parsing should not need to care which route supplied them. Read each body once and then inspect whether it is empty.

            An empty response body is not JSON text. It often accompanies a successful no-content response, so represent it using the value your interface promises instead of calling the JSON parser on it.

            ```match
            Accept header :: desired response format
            Content-Type header :: format of a supplied request body
            empty response bytes :: absence of a response value
            JSON empty list bytes :: a real response value with no items
            ```

            **Watch out:** `json.loads` on empty bytes raises `JSONDecodeError`. Check the raw body before parsing, not the truthiness of the parsed result afterwards.

            **In short:** prepare request parts conditionally, normalize response handling, and distinguish absent bodies from empty JSON values.
        ''',
        "prompt": r'''
            Every API client ends up with one function that does the HTTP work. Write it.

            **Your job:** write `request_json(url, method="GET", payload=None, api_key=None, timeout=5)`

            **What goes in**

            - `url`: full URL string
            - `method`: `"GET"`, `"POST"`, `"DELETE"`, ...
            - `payload`: a dict to send as JSON, or `None` for no body
            - `api_key`: a string, or `None`
            - `timeout`: seconds, passed to `urlopen`

            **What comes out**
            - a tuple `(status, data)`: the status code, and the response body parsed
              from JSON - or `None` if the body is empty

            **Rules**
            - Always send the header `Accept: application/json`.
            - When a payload other than `None` is supplied, send it as UTF-8 JSON and add `Content-Type: application/json`.
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
            "Treat request preparation and response interpretation as separate jobs.",
            "Prepare optional headers and payload by their presence. Both a response and HTTPError can supply a status plus raw body.",
            "Build the request using the requested method and timeout. Collect status and bytes from either response route, parse nonempty JSON, and use None for an empty body.",
        ],
    },
    {
        "id": "http-7",
        "title": "GET with retries",
        "difficulty": 2,
        "prompt": r'''
            Put retries into a real request loop. The `sleep` function is passed in, so the
            checks can record your waits instead of really waiting.

            **Your job:** write `get_with_retries(url, max_attempts=3, sleep=time.sleep)`

            **What goes in**

            - `url`: full URL string
            - `max_attempts`: the maximum number of requests in total (int >= 1)
            - `sleep`: a function taking seconds; call it to wait between attempts

            **What comes out**
            - the JSON body of the first successful response, parsed

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
            "Count total attempts, and remember that waiting makes sense only when another attempt will follow.",
            "An ordinary success returns immediately. In the error path, decide whether to stop before calculating any delay.",
            "Loop through the allowed attempts. Re-raise non-retryable errors and the final failed attempt. Otherwise choose the header delay or doubling schedule, call the supplied sleeper, and continue.",
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
            ## Check that the received bytes match a shared secret

            Another service notifies your server when a job finishes. Anyone could send a request to that address, so you need evidence that the sender knew your shared secret and signed the exact body you received.

            ```python
            import hashlib, hmac
            key = b"demonstration"
            first = hmac.new(key, b"ready", hashlib.sha256).hexdigest()
            second = hmac.new(key, b"READY", hashlib.sha256).hexdigest()
            print(len(first))
            # 64
            print(hmac.compare_digest(first, second))
            # False
            ```

            Such a notification request is a **webhook**. The keyed digest in this example is an **HMAC**, a message authentication code made from a secret key and message bytes. SHA-256 is the selected hashing algorithm. `hexdigest` represents the result as hexadecimal text.

            The verifier recomputes this value from its own secret and the received raw body. Matching values support authenticity and integrity: the expected key was used and the signed bytes have not changed. They do not hide the message contents or establish when it was sent.

            ```quiz
            You parse a JSON body and serialize it again with different spacing before checking its signature. Is that safe?
            - [x] No :: The signature covers exact bytes, including whitespace, not merely equivalent JSON values.
            - [ ] Yes :: Equivalent data can have different byte representations and therefore different signatures.
            ```

            Use `hmac.compare_digest` for the comparison. It is designed to avoid content-dependent short-circuit comparison behavior. A normal equality comparison is not the appropriate primitive for checking a secret-derived authentication value.

            ```match
            shared secret :: key known to sender and verifier
            raw body :: exact received bytes covered by the signature
            hex digest :: text representation of the keyed result
            ```

            **Watch out:** an absent or malformed signature header is a failed verification, not a reason to skip verification. Check the required header format before comparing it.

            **In short:** authenticate the exact received bytes with the shared key and compare the expected signature using compare_digest.
        ''',
        "prompt": r'''
            Your app receives webhooks. Each request has a header like
            `X-Signature: sha256=<hex>` where `<hex>` is the HMAC-SHA256 of the raw body using a shared secret.

            **Your job:** write two functions

            **What goes in**

            `sign(secret, body)`
            - `secret`: a string, e.g. `"whsec_123"`
            - `body`: the raw request body, `bytes`
            - **What comes out:** `"sha256="` followed by the hex HMAC-SHA256 of `body` with key `secret` (UTF-8 encoded)

            `verify_signature(secret, body, header)`
            - `header`: the received header value (a string) or `None`
            - **What comes out:** `True` if `header` is exactly the correct signature, else `False`

            **What comes out**
            - `sign` gives back the complete prefixed signature text. `verify_signature` gives back a Boolean indicating whether the supplied header matches.

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
            "Signing and verification should agree on the same exact byte sequence and header format.",
            "The signer needs an encoded secret, the raw body, the digest algorithm, and a hexadecimal result.",
            "Build the prefixed signature from the keyed digest. In verification, reject absent or malformed headers, compute the expected signature, and use the dedicated constant-time comparison helper.",
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

            **Your job:** write `verify_webhook(secret, body, headers, now, tolerance=300)`

            **What goes in**

            - `secret`: a string
            - `body`: the raw body, `bytes`
            - `headers`: a dict of received headers, e.g.
              `{"X-Timestamp": "1700000000", "X-Signature": "v1=<hex>"}` (names may come in any letter case)
            - `now`: the current time as an int (seconds since 1970)
            - `tolerance`: the maximum age/skew in seconds

            **What comes out**
            - `True` if the delivery is genuine and fresh, else `False`

            **Rules**
            - The signed message is the timestamp text, a dot, then the body: `b"1700000000." + body`.
            - The signature header is `"v1="` followed by the hex HMAC-SHA256 of that message with key `secret` (UTF-8).
            - Header names are case-insensitive (`x-signature`, `X-SIGNATURE`, ... all count).
            - The result is `False` when either header is missing, the timestamp isn't an integer,
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
            "Freshness and authenticity are separate conditions, and both must pass.",
            "Normalize header names, validate the timestamp, then authenticate the timestamp text together with the body.",
            "Read both required headers, safely convert the time, reject excessive past or future skew, and form the signed bytes from the original timestamp text and raw body. Compare the prefixed digest with the supplied signature.",
        ],
    },
    {
        "id": "http-10",
        "title": "Follow the pages",
        "difficulty": 3,
        "prompt": r'''
            List endpoints return results a page at a time, with a cursor pointing at the next
            page (this is how you list files, batches or fine-tuning jobs on LLM platforms).

            **Your job:** write `fetch_all(base_url, api_key, limit=2)`

            **What goes in**

            - `base_url`: e.g. `"http://127.0.0.1:8000"`
            - `api_key`: a string
            - `limit`: page size (int)

            **What comes out**
            - a list of every item from every page, in order

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
            "The server's returned cursor tells you whether another page exists.",
            "Keep a result list and current cursor across requests; encode query values rather than concatenating raw cursor characters.",
            "Start with only the limit parameter. On every authenticated timed request, parse the page, append its items in order, and read the next cursor. Stop when there is no next page, allowing HTTP errors to propagate.",
        ],
    },
    {
        "id": "http-11",
        "title": "A mini LLM API client",
        "difficulty": 3,
        "prompt": r'''
            Wrap everything into the kind of client class an LLM SDK gives you: auth, JSON,
            retries for temporary errors, clear exceptions, and token accounting.

            **Your job:** write a class `APIError(Exception)` and a class `LLMClient`

            **What goes in**

            `APIError(status, message)`
            - stores `.status` (int) and `.message` (str); `str(err)` is `"<status>: <message>"`

            `LLMClient(base_url, api_key, max_retries=2, sleep=time.sleep)`
            - `.total_tokens`: starts at `0`
            - `.chat(model, messages)`: sends `POST <base_url>/v1/chat` with JSON body
              `{"model": model, "messages": messages}` and headers `Authorization: Bearer <api_key>`
              and `Content-Type: application/json`
            - **What comes out:** the `"reply"` string from a response like
              `{"reply": "Hi!", "usage": {"total_tokens": 12}}`, and adds `usage.total_tokens` to `.total_tokens`

            **What comes out**
            - A client returns successful reply strings and accumulates reported token usage. Failed requests raise `APIError` with the specified status and message.

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
            "Combine a reusable request shape with per-instance token accounting and a bounded retry policy.",
            "Separate successful response handling from error-body interpretation. Retry counts describe extra attempts after the first.",
            "Store client settings and initialize its total. For each chat, send the required JSON request; on success add reported tokens and return the reply. On HTTP error extract a structured message or retain raw text, then retry only when allowed and attempts remain, otherwise raise the custom error.",
        ],
    },
]
