"""Chapter projects for the APIs & Data module: http, api-data, regex, sql."""

# Local test server shared by the HTTP-based projects (no internet needed).
_SERVER = r'''
import json, threading
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

'''


# ---------------------------------------------------------------------------
# http: a caching weather client
# ---------------------------------------------------------------------------

_HTTP_TESTS = r'''
from urllib.error import HTTPError
from urllib.parse import unquote
from app import WeatherClient

WEATHER = {
    "Paris": ({"name": "Paris", "main": {"temp": 18.5, "humidity": 70},
               "weather": [{"description": "light rain"}, {"description": "mist"}]}, '"p1"'),
    "São Paulo": ({"name": "São Paulo", "main": {"temp": 24, "humidity": 60},
                   "weather": [{"description": "sunny"}]}, '"sp1"'),
    "Oslo": ({"name": "Oslo", "main": {"temp": -3, "humidity": 80},
              "weather": [{"description": "snow"}]}, None),
    "Boom": None,
}


def _handler(db=WEATHER):
    def handler(req):
        if req["headers"].get("authorization") != "Bearer key-123":
            return 401, {}, {"error": "bad key"}
        prefix = "/v1/weather/"
        if not req["path"].startswith(prefix):
            return 404, {}, {"error": "no route"}
        city = unquote(req["path"][len(prefix):])
        if city not in db:
            return 404, {}, {"error": "city not found"}
        if db[city] is None:
            return 500, {}, {"error": "server exploded"}
        data, etag = db[city]
        headers = {"ETag": etag} if etag else {}
        if etag and req["headers"].get("if-none-match") == etag:
            return 304, headers, b""
        return 200, headers, data
    return handler


def _clock(start=1000.0):
    now = [start]
    return now, (lambda: now[0])


def test_current_returns_city_temperature_and_summary():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        got = WeatherClient(srv.url, "key-123", clock=clock).current("Paris")
    assert got == {"city": "Paris", "temp_c": 18.5, "summary": "light rain"}, f"got {got!r}"


def test_sends_bearer_key_to_the_weather_path():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        WeatherClient(srv.url, "key-123", clock=clock).current("Paris")
        req = srv.requests[0]
    assert req["method"] == "GET", f"method was {req['method']}"
    assert req["path"] == "/v1/weather/Paris", f"path was {req['path']}"
    assert req["headers"].get("authorization") == "Bearer key-123", \
        f"Authorization header was {req['headers'].get('authorization')!r}"


def test_city_is_trimmed_and_percent_encoded_in_the_path():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        got = WeatherClient(srv.url, "key-123", clock=clock).current("  São Paulo ")
        path = srv.requests[0]["path"]
    assert path == "/v1/weather/S%C3%A3o%20Paulo", f"path was {path!r}"
    assert got["city"] == "São Paulo" and got["temp_c"] == 24, f"got {got!r}"


def test_report_shows_one_decimal_place():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", clock=clock)
        paris = client.report("Paris")
        oslo = client.report("Oslo")
    assert paris == "Paris: 18.5°C, light rain", f"got {paris!r}"
    assert oslo == "Oslo: -3.0°C, snow", f"got {oslo!r}"


def test_fresh_answer_comes_from_the_cache():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", ttl=600, clock=clock)
        first = client.current("Paris")
        now[0] += 599
        second = client.current("Paris")
        client.report("Paris")
        n = len(srv.requests)
    assert second == first, f"second call gave {second!r}"
    assert n == 1, f"server got {n} requests, expected 1 (the rest should come from the cache)"


def test_cache_ignores_case_and_surrounding_spaces():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", clock=clock)
        client.current("Paris")
        client.current("paris")
        client.current("  PARIS ")
        n = len(srv.requests)
    assert n == 1, f"server got {n} requests, expected 1"


def test_different_cities_are_cached_separately():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", clock=clock)
        a = client.current("Paris")
        b = client.current("Oslo")
        client.current("Paris")
        client.current("Oslo")
        n = len(srv.requests)
    assert a["city"] == "Paris" and b["city"] == "Oslo", f"got {a!r} and {b!r}"
    assert n == 2, f"server got {n} requests, expected 2"


def test_stale_entry_is_revalidated_with_if_none_match():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", ttl=600, clock=clock)
        first = client.current("Paris")
        now[0] += 600
        again = client.current("Paris")
        reqs = list(srv.requests)
    assert len(reqs) == 2, f"server got {len(reqs)} requests, expected 2 (entry is stale at exactly ttl)"
    assert "if-none-match" not in reqs[0]["headers"], "the very first request must not send If-None-Match"
    sent = reqs[1]["headers"].get("if-none-match")
    assert sent == '"p1"', f"If-None-Match was {sent!r}, expected the saved ETag '\"p1\"'"
    assert again == first, f"after a 304 you should return the cached data, got {again!r}"


def test_304_restarts_the_freshness_timer():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", ttl=600, clock=clock)
        client.current("Paris")
        now[0] += 700
        client.current("Paris")          # stale -> 304
        now[0] += 500
        client.current("Paris")          # fresh again (500 < 600 since the 304)
        n = len(srv.requests)
    assert n == 2, f"server got {n} requests, expected 2"


def test_changed_weather_replaces_cache_and_etag():
    db = dict(WEATHER)
    now, clock = _clock()
    with _Server(_handler(db)) as srv:
        client = WeatherClient(srv.url, "key-123", ttl=600, clock=clock)
        client.current("Paris")
        db["Paris"] = ({"name": "Paris", "main": {"temp": 21.25},
                        "weather": [{"description": "clear sky"}]}, '"p2"')
        now[0] += 601
        changed = client.current("Paris")
        now[0] += 601
        client.current("Paris")
        reqs = list(srv.requests)
    assert changed == {"city": "Paris", "temp_c": 21.25, "summary": "clear sky"}, f"got {changed!r}"
    sent = reqs[2]["headers"].get("if-none-match")
    assert sent == '"p2"', f"third request sent If-None-Match {sent!r}, expected the NEW ETag '\"p2\"'"


def test_no_etag_means_no_if_none_match():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", ttl=60, clock=clock)
        client.current("Oslo")
        now[0] += 61
        got = client.current("Oslo")
        reqs = list(srv.requests)
    assert len(reqs) == 2, f"server got {len(reqs)} requests, expected 2"
    assert "if-none-match" not in reqs[1]["headers"], "Oslo had no ETag, so don't send If-None-Match"
    assert got["temp_c"] == -3, f"got {got!r}"


def test_unknown_city_raises_value_error_and_is_not_cached():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        client = WeatherClient(srv.url, "key-123", clock=clock)
        for _ in range(2):
            try:
                client.current(" Atlantis ")
                assert False, "expected ValueError"
            except ValueError as err:
                assert str(err) == "unknown city: Atlantis", f"message was {str(err)!r}"
        n = len(srv.requests)
    assert n == 2, f"server got {n} requests - a 404 must not be cached"


def test_server_errors_raise_http_error():
    now, clock = _clock()
    with _Server(_handler()) as srv:
        try:
            WeatherClient(srv.url, "key-123", clock=clock).current("Boom")
            assert False, "expected urllib.error.HTTPError"
        except HTTPError as err:
            assert err.code == 500, f"code was {err.code}"


def test_passes_a_timeout():
    assert "timeout" in source("app.py"), "pass a timeout to urlopen so a stuck server can't hang the app"
'''

MINI_HTTP = {
    "id": "mini-http",
    "chapter": "http",
    "title": "Weather Desk: a caching API client",
    "estimated_hours": 1.0,
    "main": "app.py",
    "files": ["app.py"],
    "brief": r'''
Your dashboard shows the weather for a dozen cities and refreshes every few seconds. Asking
the weather API every time is slow and burns your rate limit, so you'll build a small client
that **caches** answers and, once they get old, asks the server *"has this changed?"* instead
of downloading everything again. This is exactly how browsers and CDNs save bandwidth, and the
same caching idea saves real money in LLM apps.

## What to build

A file `app.py` with a class:

**`WeatherClient(base_url, api_key, ttl=600, clock=time.time)`**

- `base_url`: the API address, e.g. `"http://127.0.0.1:8000"` (no trailing slash)
- `api_key`: a string, e.g. `"key-123"`
- `ttl`: how many seconds a cached answer stays fresh (a number)
- `clock`: a function with no arguments that returns the current time in seconds. Always call
  `clock()` to get "now" (never `time.time()` directly) - the checks pass a fake clock.

Methods:

- **`current(city)`** returns a dict `{"city": str, "temp_c": number, "summary": str}`.
- **`report(city)`** returns a string like `"Paris: 18.5°C, light rain"` (uses `current`).

The server answers `GET /v1/weather/<city>` with JSON like:

```json
{"name": "Paris", "main": {"temp": 18.5, "humidity": 70},
 "weather": [{"description": "light rain"}, {"description": "mist"}]}
```

and usually an `ETag` response header such as `"p1"` (a version label for that answer,
quotes included).

## Rules

- Strip spaces from both ends of `city`. Request `GET <base_url>/v1/weather/<city>` with the
  city **percent-encoded as a URL path piece**: `"São Paulo"` -> `/v1/weather/S%C3%A3o%20Paulo`
  (spaces become `%20`, not `+`).
- Every request sends the header `Authorization: Bearer <api_key>`.
- Pass a `timeout` to `urlopen`.
- `current` returns `"city"` = the JSON `name`, `"temp_c"` = `main.temp` (unchanged),
  `"summary"` = the `description` of the **first** item in `weather`.
- `report` formats the temperature with exactly one decimal place: `"Oslo: -3.0°C, snow"`.
- **Cache** answers per city. The cache key is the stripped city in lowercase, so `"Paris"`,
  `"paris"` and `"  PARIS "` share one entry. Different cities have separate entries.
- An entry is **fresh** while `clock() - time_it_was_saved < ttl`. A fresh entry is returned
  with **no** request. (At exactly `ttl` seconds it is stale.)
- A **stale** entry makes a new request. If the saved answer came with an `ETag` header,
  send it back unchanged in an `If-None-Match` request header. If there was no ETag, don't
  send `If-None-Match`. A first request for a city never sends it.
- If the server answers **`304 Not Modified`**, return the cached dict and restart its
  freshness timer (treat it as saved "now").
- If the server answers `200`, replace the entry: new data, new ETag (or none), saved now.
- A `404` raises `ValueError("unknown city: <stripped city>")`, and nothing is cached.
- Any other error status (e.g. `500`) raises `urllib.error.HTTPError` (just let it through).

## Examples

```python
client = WeatherClient("http://127.0.0.1:8000", "key-123", ttl=600, clock=fake_clock)
client.current("Paris")      # {"city": "Paris", "temp_c": 18.5, "summary": "light rain"}  (1 request)
client.current(" paris ")    # same dict, no request (still fresh)
client.report("Paris")       # "Paris: 18.5°C, light rain", no request
# ... fake clock moves 600 seconds forward ...
client.current("Paris")      # request with If-None-Match: "p1" -> server says 304 -> same dict
client.current("Atlantis")   # raises ValueError("unknown city: Atlantis")
```

## You'll need to find out

- How to percent-encode text so it can go **inside a URL path** (the chapter only built
  query strings, which encode spaces differently).
- What `urlopen` does when a server answers `304 Not Modified` (is it a success or an
  error for urllib?), and how to read the status code when that happens.

## Try it yourself

No internet needed. In an empty folder, make a fake "API" out of plain files and serve it
with Python's built-in web server:

```bash
mkdir -p v1/weather
echo '{"name": "Paris", "main": {"temp": 18.5}, "weather": [{"description": "light rain"}]}' > v1/weather/Paris
python3 -m http.server 8000
```

Then, in another terminal next to `app.py`:

```bash
python3 -c "from app import WeatherClient; c = WeatherClient('http://127.0.0.1:8000', 'k'); print(c.report('Paris'))"
```
''',
    "explore": r'''
- Add a `max_entries` limit that evicts the least recently used city when the cache is full.
- Save the cache to a JSON file so it survives restarts (store the ETags too).
- Add retries with backoff for `429`/`503`, reusing the `Retry-After` header.
- Add a `forecast(city, days)` method that uses a query string on a different endpoint.
''',
    "rubric": [
        "The cache entry keeps data, ETag and saved time together in one clear structure",
        "Freshness uses the injected clock and the < ttl rule consistently",
        "HTTP errors are handled narrowly: 304 and 404 are special, everything else propagates",
        "The URL, headers and timeout are built in one place, not copy-pasted",
    ],
    "starter_files": {"app.py": r'''
import time


class WeatherClient:
    def __init__(self, base_url, api_key, ttl=600, clock=time.time):
        ...

    def current(self, city):
        ...

    def report(self, city):
        ...
'''},
    "solution_files": {"app.py": r'''
import json
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


class WeatherClient:
    def __init__(self, base_url, api_key, ttl=600, clock=time.time):
        self.base_url = base_url
        self.api_key = api_key
        self.ttl = ttl
        self.clock = clock
        self.cache = {}  # "paris" -> {"data": {...}, "etag": '"p1"' or None, "saved_at": 1000.0}

    def current(self, city):
        name = city.strip()
        entry = self.cache.get(name.lower())
        now = self.clock()
        if entry and now - entry["saved_at"] < self.ttl:
            return entry["data"]

        headers = {"Authorization": f"Bearer {self.api_key}"}
        if entry and entry["etag"]:
            headers["If-None-Match"] = entry["etag"]
        req = Request(f"{self.base_url}/v1/weather/{quote(name)}", headers=headers)
        try:
            with urlopen(req, timeout=5) as resp:
                raw = json.loads(resp.read())
                etag = resp.headers.get("ETag")
        except HTTPError as err:
            if err.code == 304 and entry:
                entry["saved_at"] = now
                return entry["data"]
            if err.code == 404:
                raise ValueError(f"unknown city: {name}")
            raise

        data = {
            "city": raw["name"],
            "temp_c": raw["main"]["temp"],
            "summary": raw["weather"][0]["description"],
        }
        self.cache[name.lower()] = {"data": data, "etag": etag, "saved_at": now}
        return data

    def report(self, city):
        w = self.current(city)
        return f"{w['city']}: {w['temp_c']:.1f}°C, {w['summary']}"
'''},
    "tests": _SERVER + _HTTP_TESTS,
}


# ---------------------------------------------------------------------------
# api-data: a GitHub-style issues exporter
# ---------------------------------------------------------------------------

_API_TESTS = r'''
import csv
from urllib.parse import urlparse, parse_qs
from app import export_issues, normalize_issue, ExportError

ISSUES = [
    {"number": 1, "title": "Crash on start", "state": "open", "user": {"login": "ada"},
     "labels": [{"name": "bug"}, {"name": "ui"}], "comments": 3},
    {"number": 2, "title": "Add dark mode", "state": "closed", "user": {"login": "grace"},
     "labels": [], "comments": 0, "pull_request": {"url": "https://x/pulls/2"}},
    {"number": 3, "title": 'Error: "token", limit reached', "state": "open", "user": None,
     "labels": [{"name": "bug"}], "comments": None},
    {"number": 4, "title": "Docs\nfor setup", "state": "closed", "user": {"login": "linus"},
     "labels": None},
    {"number": 5, "title": "Fix typo", "state": "closed", "user": {"login": "ada"},
     "labels": [{"name": "docs"}], "comments": 1, "pull_request": {"url": "https://x/pulls/5"}},
    {"number": 6, "title": "Slow search", "state": "open", "user": {"login": "grace"},
     "labels": [{"name": "perf"}, {"name": "bug"}], "comments": 12},
    {"number": 7, "title": "Ünïcode title ✓", "state": "open", "user": {"login": "ada"},
     "labels": [{"name": "i18n"}], "comments": 2},
]
PAGE = 3


def _pages(items=ISSUES, failures=None, endless=False):
    """failures: {page: [(status, headers), ...]} served before that page succeeds."""
    queue = {p: list(v) for p, v in (failures or {}).items()}
    def handler(req):
        if req["headers"].get("authorization") != "Bearer tok-1":
            return 401, {}, {"message": "Bad credentials"}
        parts = urlparse(req["path"])
        if parts.path != "/issues":
            return 404, {}, {"message": "Not Found"}
        page = int(parse_qs(parts.query)["page"][0])
        if queue.get(page):
            status, headers = queue[page].pop(0)
            return status, headers, {"message": "try later"}
        if endless:
            return 200, {}, items[:PAGE]
        return 200, {}, items[(page - 1) * PAGE: page * PAGE]
    return handler


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))


def test_normalize_issue_flattens_the_nested_data():
    got = normalize_issue(ISSUES[0])
    assert got == {"number": 1, "title": "Crash on start", "state": "open", "author": "ada",
                   "labels": "bug;ui", "comments": 3}, f"got {got!r}"


def test_missing_user_and_comments_get_defaults():
    got = normalize_issue(ISSUES[2])
    assert got["author"] == "ghost", f"author was {got['author']!r} (user is None)"
    assert got["comments"] == 0, f"comments was {got['comments']!r} (comments is None)"
    bare = normalize_issue({"number": 9, "state": "open"})
    assert bare == {"number": 9, "title": "", "state": "open", "author": "ghost",
                    "labels": "", "comments": 0}, f"got {bare!r} for an issue with most keys missing"


def test_null_or_empty_labels_become_an_empty_string():
    assert normalize_issue(ISSUES[3])["labels"] == "", "labels: None should give ''"
    assert normalize_issue(ISSUES[1])["labels"] == "", "labels: [] should give ''"
    assert normalize_issue(ISSUES[5])["labels"] == "perf;bug", "keep the labels in their original order"


def test_follows_pages_until_an_empty_page():
    with _Server(_pages()) as srv:
        export_issues(srv.url, "tok-1", "out.csv", sleep=lambda s: None)
        paths = [r["path"] for r in srv.requests]
    assert paths == ["/issues?page=1", "/issues?page=2", "/issues?page=3", "/issues?page=4"], \
        f"requested {paths}"


def test_sends_the_bearer_token():
    with _Server(_pages()) as srv:
        export_issues(srv.url, "tok-1", "out.csv", sleep=lambda s: None)
        auths = {r["headers"].get("authorization") for r in srv.requests}
    assert auths == {"Bearer tok-1"}, f"Authorization headers were {auths}"


def test_csv_has_header_and_one_row_per_issue_without_prs():
    with _Server(_pages()) as srv:
        export_issues(srv.url, "tok-1", "out.csv", sleep=lambda s: None)
    rows = _read("out.csv")
    assert rows[0] == ["number", "title", "state", "author", "labels", "comments"], f"header was {rows[0]}"
    assert [r[0] for r in rows[1:]] == ["1", "3", "4", "6", "7"], \
        f"issue numbers in the file: {[r[0] for r in rows[1:]]} (pull requests 2 and 5 must be skipped)"
    assert rows[1] == ["1", "Crash on start", "open", "ada", "bug;ui", "3"], f"first row was {rows[1]}"


def test_titles_with_commas_quotes_newlines_and_unicode_survive():
    with _Server(_pages()) as srv:
        export_issues(srv.url, "tok-1", "out.csv", sleep=lambda s: None)
    rows = _read("out.csv")
    titles = [r[1] for r in rows[1:]]
    assert titles == ["Crash on start", 'Error: "token", limit reached', "Docs\nfor setup",
                      "Slow search", "Ünïcode title ✓"], f"titles read back as {titles!r}"
    assert all(len(r) == 6 for r in rows), "every row must have exactly 6 columns when read back"


def test_returns_a_summary_with_label_counts():
    with _Server(_pages()) as srv:
        got = export_issues(srv.url, "tok-1", "out.csv", sleep=lambda s: None)
    assert got == {"exported": 5, "skipped_prs": 2,
                   "labels": {"bug": 3, "ui": 1, "perf": 1, "i18n": 1}}, f"got {got!r}"


def test_empty_repo_writes_only_the_header():
    with _Server(_pages(items=[])) as srv:
        got = export_issues(srv.url, "tok-1", "empty.csv", sleep=lambda s: None)
        n = len(srv.requests)
    assert got == {"exported": 0, "skipped_prs": 0, "labels": {}}, f"got {got!r}"
    assert _read("empty.csv") == [["number", "title", "state", "author", "labels", "comments"]]
    assert n == 1, f"made {n} requests, expected 1"


def test_retries_429_and_5xx_with_backoff():
    waits = []
    with _Server(_pages(failures={2: [(503, {}), (500, {})]})) as srv:
        got = export_issues(srv.url, "tok-1", "out.csv", sleep=waits.append)
        n = len(srv.requests)
    assert waits == [1, 2], f"waited {waits!r}, expected [1, 2]"
    assert got["exported"] == 5, f"got {got!r}"
    assert n == 6, f"made {n} requests, expected 6 (4 pages + 2 retries)"


def test_honours_the_retry_after_header():
    waits = []
    with _Server(_pages(failures={1: [(429, {"Retry-After": "3"})]})) as srv:
        export_issues(srv.url, "tok-1", "out.csv", sleep=waits.append)
    assert waits == [3.0], f"waited {waits!r}, expected [3.0]"


def test_gives_up_after_three_attempts_with_export_error():
    waits = []
    with _Server(_pages(failures={1: [(503, {})] * 5})) as srv:
        try:
            export_issues(srv.url, "tok-1", "out.csv", sleep=waits.append)
            assert False, "expected ExportError"
        except ExportError as err:
            assert err.status == 503, f"err.status was {err.status!r}"
            assert str(err) == "export failed: HTTP 503", f"message was {str(err)!r}"
        n = len(srv.requests)
    assert n == 3, f"made {n} requests, expected 3 attempts"
    assert waits == [1, 2], f"waited {waits!r} - don't wait after the last attempt"


def test_bad_token_fails_fast_without_retrying():
    waits = []
    with _Server(_pages()) as srv:
        try:
            export_issues(srv.url, "wrong", "out.csv", sleep=waits.append)
            assert False, "expected ExportError"
        except ExportError as err:
            assert err.status == 401, f"err.status was {err.status!r}"
        n = len(srv.requests)
    assert n == 1 and waits == [], f"made {n} requests and waited {waits!r} - never retry a 401"
    assert issubclass(ExportError, Exception)


def test_stops_after_max_pages():
    with _Server(_pages(endless=True)) as srv:
        got = export_issues(srv.url, "tok-1", "out.csv", max_pages=4, sleep=lambda s: None)
        n = len(srv.requests)
    assert n == 4, f"made {n} requests, expected 4 (max_pages)"
    assert got["exported"] == 8 and got["skipped_prs"] == 4, f"got {got!r}"
'''

MINI_API_DATA = {
    "id": "mini-api-data",
    "chapter": "api-data",
    "title": "Issue Exporter: from API pages to a spreadsheet",
    "estimated_hours": 1.0,
    "main": "app.py",
    "files": ["app.py"],
    "brief": r'''
Your team lead wants every open and closed issue from the project tracker in a spreadsheet
by this afternoon. The tracker has a GitHub-style API: issues come back a page at a time,
the data is messy (deleted users, missing labels, `null` everywhere), pull requests are mixed
in, and the server sometimes says "slow down". You'll write the exporter that survives all
of it and produces a clean CSV file.

## What to build

A file `app.py` with:

**`class ExportError(Exception)`** - created as `ExportError(status)` where `status` is an
HTTP status code (int). It stores it as `err.status`, and `str(err)` is
`"export failed: HTTP <status>"`, e.g. `"export failed: HTTP 503"`.

**`normalize_issue(issue)`** - turns one raw issue dict into a flat dict with exactly these
keys: `"number"`, `"title"`, `"state"`, `"author"`, `"labels"`, `"comments"`.

**`export_issues(base_url, token, out_path, max_pages=50, sleep=time.sleep)`**

- `base_url`: e.g. `"http://127.0.0.1:8000"`
- `token`: an API token string
- `out_path`: the CSV file to write, e.g. `"issues.csv"`
- `max_pages`: the most pages to fetch (a safety limit)
- `sleep`: a function taking seconds - call it to wait between retries (the checks record it)
- **Returns:** a summary dict `{"exported": int, "skipped_prs": int, "labels": {name: count}}`

A raw issue from the API looks like this (any key may be missing, and several may be `null`):

```python
{"number": 1, "title": "Crash on start", "state": "open", "user": {"login": "ada"},
 "labels": [{"name": "bug"}, {"name": "ui"}], "comments": 3}
```

## Rules

`normalize_issue`:
- `"number"` and `"state"` are copied as they are.
- `"title"`: the title, or `""` if it's missing or `None`.
- `"author"`: `user.login`, or `"ghost"` if `user` is missing or `None`.
- `"labels"`: the label `name`s in their original order joined with `";"` (`"bug;ui"`),
  or `""` if `labels` is missing, `None` or empty.
- `"comments"`: the number of comments, or `0` if missing or `None`.

`export_issues`:
- Request `GET <base_url>/issues?page=1`, then `page=2`, `page=3`, ... Each page is a JSON
  **list** of issues. Stop at the first page that is an empty list `[]`, or after
  `max_pages` pages, whichever comes first.
- Every request sends `Authorization: Bearer <token>`, and passes a `timeout` to `urlopen`.
- Skip every item that has a `"pull_request"` key (the API lists pull requests as issues
  too) and count them in `"skipped_prs"`.
- If a page answers `429` or any `5xx`, retry that page: at most **3 attempts** per page.
  Before each retry call `sleep(...)` with the `Retry-After` response header as a float if
  it's present, otherwise `2 ** n` where `n` is `0` for the first retry, `1` for the second
  (so `1`, then `2`). Don't sleep after the last attempt.
- If a page still fails after 3 attempts, raise `ExportError(<last status>)`.
- Any other error status (e.g. `401`, `404`) raises `ExportError(<status>)` immediately,
  with no retry and no sleep.
- Write `out_path` as a UTF-8 CSV file: a header row
  `number,title,state,author,labels,comments`, then one row per exported issue (from
  `normalize_issue`), in the order the API returned them. Titles can contain commas, double
  quotes, line breaks and non-English characters - the file must still read back correctly
  with a standard CSV reader, one row per issue. With no issues, the file holds just the header.
- `"exported"` is the number of rows written; `"labels"` counts how many exported issues
  have each label (`{}` if none).

## Examples

```python
normalize_issue({"number": 3, "title": None, "state": "open", "user": None, "labels": None})
# {"number": 3, "title": "", "state": "open", "author": "ghost", "labels": "", "comments": 0}

export_issues("http://127.0.0.1:8000", "tok-1", "issues.csv")
# requests page=1, page=2, page=3, page=4 (empty) and returns e.g.
# {"exported": 5, "skipped_prs": 2, "labels": {"bug": 3, "ui": 1, "perf": 1, "i18n": 1}}

# server answers page 2 with 503, then 500, then the data -> sleep(1), sleep(2), carries on
# server answers 429 with header Retry-After: 3 -> sleep(3.0)
export_issues("http://127.0.0.1:8000", "wrong", "issues.csv")
# raises ExportError; err.status == 401; str(err) == "export failed: HTTP 401"
```

## You'll need to find out

- How to write a proper CSV file with the standard library, so that commas, quotes and line
  breaks inside a value don't break the columns (and which argument to pass when opening the
  file so rows don't get blank lines between them on some systems).

## Try it yourself

Test `normalize_issue` directly with a few messy dicts first. For the full export, put a
JSON list of issues in a file called `issues` and serve the folder with
`python3 -m http.server 8000` (it ignores the query string, so every page is the same file):

```bash
python3 -c "from app import export_issues; print(export_issues('http://127.0.0.1:8000', 't', 'out.csv', max_pages=1))"
```

Then open `out.csv` in a spreadsheet app.
''',
    "explore": r'''
- Add a `state` filter (`"open"`, `"closed"`, `"all"`) sent as a query parameter.
- Also write a JSONL file next to the CSV, one normalized issue per line.
- Print a progress line per page to stderr ("page 3: 50 issues").
- Resume an interrupted export: remember the last finished page in a small state file.
''',
    "rubric": [
        "normalize_issue handles missing and None values with clear, consistent defaults",
        "Fetching one page (with retries) is its own small function, separate from writing the CSV",
        "Retry rules are easy to read: which statuses retry, how long to wait, when to give up",
        "The CSV is written with a real CSV writer, not by joining strings with commas",
    ],
    "starter_files": {"app.py": r'''
import time


class ExportError(Exception):
    ...


def normalize_issue(issue):
    ...


def export_issues(base_url, token, out_path, max_pages=50, sleep=time.sleep):
    ...
'''},
    "solution_files": {"app.py": r'''
import csv
import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

COLUMNS = ["number", "title", "state", "author", "labels", "comments"]
MAX_ATTEMPTS = 3


class ExportError(Exception):
    def __init__(self, status):
        super().__init__(f"export failed: HTTP {status}")
        self.status = status


def normalize_issue(issue):
    user = issue.get("user") or {}
    labels = issue.get("labels") or []
    return {
        "number": issue.get("number"),
        "title": issue.get("title") or "",
        "state": issue.get("state"),
        "author": user.get("login") or "ghost",
        "labels": ";".join(label["name"] for label in labels),
        "comments": issue.get("comments") or 0,
    }


def fetch_page(base_url, token, page, sleep):
    req = Request(f"{base_url}/issues?page={page}",
                  headers={"Authorization": f"Bearer {token}"})
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except HTTPError as err:
            retryable = err.code == 429 or 500 <= err.code <= 599
            if not retryable or attempt == MAX_ATTEMPTS - 1:
                raise ExportError(err.code)
            retry_after = err.headers.get("Retry-After")
            sleep(float(retry_after) if retry_after else 2 ** attempt)


def export_issues(base_url, token, out_path, max_pages=50, sleep=time.sleep):
    rows, skipped, label_counts = [], 0, {}
    for page in range(1, max_pages + 1):
        items = fetch_page(base_url, token, page, sleep)
        if not items:
            break
        for issue in items:
            if "pull_request" in issue:
                skipped += 1
                continue
            row = normalize_issue(issue)
            rows.append(row)
            for label in issue.get("labels") or []:
                label_counts[label["name"]] = label_counts.get(label["name"], 0) + 1

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return {"exported": len(rows), "skipped_prs": skipped, "labels": label_counts}
'''},
    "tests": _SERVER + _API_TESTS,
}


# ---------------------------------------------------------------------------
# regex: log detective (parse + redact LLM gateway logs)
# ---------------------------------------------------------------------------

_REGEX_TESTS = r'''
from app import redact, parse_line, summarize

LOG = """2026-09-28T10:15:02Z INFO req=a1 model=gpt-4o-mini tokens=512 latency_ms=830
2026-09-28T10:15:03Z ERROR req=b2 model=claude-haiku latency_ms=120 msg="rate limited, retry in 2s"
this line is not a log line

2026-09-28T10:15:04Z WARNING req=c3 model=gpt-4o-mini tokens=90 latency_ms=2400 msg="slow response"
2026-09-28T10:15:05Z INFO req=d4 model=claude-haiku tokens=300 latency_ms=2400
2026-09-28 10:15:06 INFO req=e5 model=gpt-4o-mini tokens=1000
"""


def test_redacts_email_addresses():
    got = redact("contact ada.lovelace+ai@example.co.uk or bob@mail.dev.")
    assert got == "contact [EMAIL] or [EMAIL].", f"got {got!r}"
    got = redact("user=grace_h@navy-labs.org logged in")
    assert got == "user=[EMAIL] logged in", f"got {got!r}"


def test_masks_api_keys_keeping_the_last_four_characters():
    got = redact("key=sk-proj-AbCdEf1234567890XyZ9 used")
    assert got == "key=sk-...XyZ9 used", f"got {got!r}"
    got = redact("sk-0123456789abcdef and sk-live_ABCDEFGHIJKLMNOP_q7Rt")
    assert got == "sk-...cdef and sk-...q7Rt", f"got {got!r}"


def test_short_or_embedded_sk_is_not_a_key():
    text = "sk-short, task-list and risk-assessment-for-2026-q3"
    got = redact(text)
    assert got == text, f"got {got!r} - only a word STARTING with sk- and 16+ characters after it is a key"


def test_redacts_ipv4_addresses():
    got = redact("from 192.168.0.12 to 10.0.0.1 (version 1.2.3)")
    assert got == "from [IP] to [IP] (version 1.2.3)", f"got {got!r}"


def test_redact_keeps_everything_else_across_lines():
    text = "line one: ada@x.io\nline two: nothing secret\nline three: 8.8.8.8\n"
    got = redact(text)
    assert got == "line one: [EMAIL]\nline two: nothing secret\nline three: [IP]\n", f"got {got!r}"


def test_parse_line_reads_time_level_and_plain_fields():
    got = parse_line("2026-09-28T10:15:02Z INFO req=a1 model=gpt-4o-mini tokens=512")
    assert got == {"time": "2026-09-28T10:15:02Z", "level": "INFO",
                   "fields": {"req": "a1", "model": "gpt-4o-mini", "tokens": "512"}}, f"got {got!r}"


def test_parse_line_handles_quoted_values():
    got = parse_line('2026-09-28T10:15:03Z ERROR req=b2 msg="rate limited, retry in 2s" note=""')
    assert got is not None, "this is a valid line"
    assert got["fields"] == {"req": "b2", "msg": "rate limited, retry in 2s", "note": ""}, \
        f"fields were {got['fields']!r}"


def test_parse_line_allows_a_trailing_newline_and_no_fields():
    got = parse_line("2026-09-28T10:15:02Z DEBUG\n")
    assert got == {"time": "2026-09-28T10:15:02Z", "level": "DEBUG", "fields": {}}, f"got {got!r}"


def test_parse_line_ignores_words_that_are_not_key_value():
    got = parse_line("2026-09-28T10:15:02Z WARNING retrying now attempt=2 of 3")
    assert got is not None and got["fields"] == {"attempt": "2"}, f"got {got!r}"


def test_parse_line_rejects_bad_timestamps_and_unknown_levels():
    bad = [
        "2026-09-28 10:15:06 INFO req=e5",
        "2026-9-28T10:15:02Z INFO req=1",
        "2026-09-28T10:15:02Z TRACE req=1",
        "2026-09-28T10:15:02Z info req=1",
        "2026-09-28T10:15:02Z INFORMATION req=1",
        "hello 2026-09-28T10:15:02Z INFO req=1",
        "",
    ]
    for line in bad:
        got = parse_line(line)
        assert got is None, f"parse_line({line!r}) returned {got!r}, expected None"


def test_summarize_counts_lines_parsed_and_levels():
    got = summarize(LOG)
    assert got["lines"] == 6, f"lines was {got['lines']!r} (blank lines don't count)"
    assert got["parsed"] == 4, f"parsed was {got['parsed']!r}"
    assert got["levels"] == {"INFO": 2, "ERROR": 1, "WARNING": 1}, f"levels was {got['levels']!r}"


def test_summarize_sums_tokens_per_model():
    got = summarize(LOG)
    assert got["tokens_by_model"] == {"gpt-4o-mini": 602, "claude-haiku": 300}, \
        f"tokens_by_model was {got['tokens_by_model']!r}"


def test_summarize_finds_the_slowest_request_first_wins_ties():
    got = summarize(LOG)
    assert got["slowest"] == "c3", f"slowest was {got['slowest']!r}"


def test_summarize_empty_text():
    got = summarize("\n\n")
    assert got == {"lines": 0, "parsed": 0, "levels": {}, "tokens_by_model": {}, "slowest": None}, \
        f"got {got!r}"
'''

MINI_REGEX = {
    "id": "mini-regex",
    "chapter": "regex",
    "title": "Gateway Log Scrubber",
    "estimated_hours": 0.75,
    "main": "app.py",
    "files": ["app.py"],
    "brief": r'''
Your LLM gateway writes a log line for every model call. You need two things from those logs:
numbers for the weekly report (who's slow, which model eats the tokens) and a *clean* copy you
can paste into a bug ticket without leaking customer emails, API keys or IP addresses.
Regular expressions are the perfect tool for both.

## What to build

A file `app.py` with three functions:

- **`redact(text)`** returns `text` with secrets replaced (see Rules).
- **`parse_line(line)`** returns a dict `{"time": str, "level": str, "fields": {str: str}}`,
  or `None` if the line isn't a valid log line.
- **`summarize(text)`** takes a whole log (many lines) and returns a dict
  `{"lines": int, "parsed": int, "levels": {level: count}, "tokens_by_model": {model: int}, "slowest": str or None}`.

A log line looks like this:

```
2026-09-28T10:15:03Z ERROR req=b2 model=claude-haiku latency_ms=120 msg="rate limited, retry in 2s"
```

## Rules

`redact`:
- An **email** (letters, digits, `.`, `_`, `+` or `-` before the `@`; a domain of letters,
  digits, `-` and dots, ending in a dot and 2+ letters) becomes `[EMAIL]`.
- An **API key** is `sk-` at the **start of a word** followed by 16 or more letters, digits,
  `_` or `-`. It becomes `sk-...` plus its last 4 characters: `sk-proj-AbCdEf1234567890XyZ9`
  -> `sk-...XyZ9`. `sk-short` and `risk-assessment-for-2026-q3` are left alone.
- An **IPv4 address** (four numbers of 1-3 digits joined by dots) becomes `[IP]`.
  `1.2.3` is not an address.
- Everything else, including line breaks, stays exactly as it was.

`parse_line`:
- Ignore whitespace (like a trailing `\n`) at both ends of the line.
- A valid line is: a timestamp shaped exactly `YYYY-MM-DDTHH:MM:SSZ` at the very start, one
  space, a level that is exactly `DEBUG`, `INFO`, `WARNING` or `ERROR`, then optionally one
  space and the rest. Anything else -> `None` (lowercase levels, `TRACE`, `INFORMATION`, a
  space instead of `T`, text before the timestamp, an empty line).
- In the rest, every `key=value` becomes an entry in `"fields"`. A key is letters, digits
  and `_`. A value is either `"in double quotes"` (may contain spaces and commas, stored
  **without** the quotes; `""` gives `""`) or a run of non-space characters.
- Words in the rest that aren't `key=value` are ignored. All values stay strings.

`summarize`:
- `"lines"`: number of non-blank lines. `"parsed"`: how many of them `parse_line` accepts.
- `"levels"`: count of parsed lines per level (only levels that appear).
- `"tokens_by_model"`: for parsed lines that have both `model` and `tokens`, the sum of
  `tokens` (as an int) per model.
- `"slowest"`: the `req` of the parsed line with the biggest `latency_ms` (as an int); if
  several tie, the first one in the log wins; `None` if no line has `latency_ms`.

## Examples

```python
redact("mail ada@example.com from 10.0.0.1 with sk-0123456789abcdef")
# "mail [EMAIL] from [IP] with sk-...cdef"

parse_line('2026-09-28T10:15:03Z ERROR req=b2 msg="rate limited, retry in 2s" retrying')
# {"time": "2026-09-28T10:15:03Z", "level": "ERROR",
#  "fields": {"req": "b2", "msg": "rate limited, retry in 2s"}}
parse_line("2026-09-28 10:15:06 INFO req=e5")     # None

summarize(log_text)
# {"lines": 6, "parsed": 4, "levels": {"INFO": 2, "ERROR": 1, "WARNING": 1},
#  "tokens_by_model": {"gpt-4o-mini": 602, "claude-haiku": 300}, "slowest": "c3"}
summarize("")    # {"lines": 0, "parsed": 0, "levels": {}, "tokens_by_model": {}, "slowest": None}
```

## You'll need to find out

- How to say **"this OR that"** inside one regex pattern (for the list of levels, and for
  "a quoted value or a plain value").
- How to say **"at the start of a word"** in a regex, so `risk-...` doesn't look like a key.

## Try it yourself

Save a few lines like the example into `gateway.log`, then:

```bash
python3 -c "from app import redact, summarize; t = open('gateway.log').read(); print(summarize(t)); print(redact(t))"
```
''',
    "explore": r'''
- Add `--redact` / `--summary` command-line flags so it works as `python3 app.py gateway.log --summary`.
- Report p50 and p95 latency per model.
- Redact `Bearer <token>` headers and phone numbers too, with tests for each new pattern.
- Use `re.VERBOSE` to write the line pattern over several commented lines.
''',
    "rubric": [
        "Patterns are compiled once at module level with clear names",
        "Patterns are raw strings and readable (named groups where they help)",
        "summarize reuses parse_line instead of re-parsing the text differently",
        "Edge cases (no latency, empty text, ties) are handled without special-case clutter",
    ],
    "starter_files": {"app.py": r'''
import re


def redact(text):
    ...


def parse_line(line):
    ...


def summarize(text):
    ...
'''},
    "solution_files": {"app.py": r'''
import re

EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
API_KEY = re.compile(r"\bsk-[\w-]{16,}")
IPV4 = re.compile(r"\d{1,3}(?:\.\d{1,3}){3}")
LINE = re.compile(
    r"(?P<time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) "
    r"(?P<level>DEBUG|INFO|WARNING|ERROR)"
    r"(?: (?P<rest>.*))?"
)
FIELD = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')


def redact(text):
    text = EMAIL.sub("[EMAIL]", text)
    text = API_KEY.sub(lambda m: "sk-..." + m.group()[-4:], text)
    return IPV4.sub("[IP]", text)


def parse_line(line):
    m = LINE.fullmatch(line.strip())
    if m is None:
        return None
    fields = {}
    for key, quoted, plain in FIELD.findall(m.group("rest") or ""):
        fields[key] = quoted if plain == "" else plain
    return {"time": m.group("time"), "level": m.group("level"), "fields": fields}


def summarize(text):
    lines = [line for line in text.splitlines() if line.strip()]
    parsed = [p for p in (parse_line(line) for line in lines) if p]
    levels, tokens = {}, {}
    slowest, slowest_ms = None, -1
    for entry in parsed:
        f = entry["fields"]
        levels[entry["level"]] = levels.get(entry["level"], 0) + 1
        if "model" in f and "tokens" in f:
            tokens[f["model"]] = tokens.get(f["model"], 0) + int(f["tokens"])
        if "latency_ms" in f and int(f["latency_ms"]) > slowest_ms:
            slowest, slowest_ms = f.get("req"), int(f["latency_ms"])
    return {"lines": len(lines), "parsed": len(parsed), "levels": levels,
            "tokens_by_model": tokens, "slowest": slowest}
'''},
    "tests": _REGEX_TESTS,
}


# ---------------------------------------------------------------------------
# sql: a SQLite reading list
# ---------------------------------------------------------------------------

_SQL_TESTS = r'''
from app import ReadingList


def _sample():
    rl = ReadingList()
    rl.add("https://arxiv.org/abs/1706.03762", "Attention Is All You Need", ["AI", "papers"])
    rl.add("https://docs.python.org/3/library/sqlite3.html", "sqlite3 docs", ["python", "docs"])
    rl.add("https://example.com/rag-guide", "A practical RAG guide", ["ai", "rag"])
    rl.add("https://example.com/cooking", "Weeknight pasta", [])
    rl.add("https://example.com/evals", "Writing LLM evals", ["AI", "evals"])
    return rl


def test_add_returns_increasing_ids():
    rl = ReadingList()
    a = rl.add("https://a.io", "A")
    b = rl.add("https://b.io", "B", ["x"])
    assert (a, b) == (1, 2), f"ids were {(a, b)!r}"


def test_get_returns_a_dict_with_clean_sorted_tags():
    rl = ReadingList()
    item_id = rl.add("https://a.io", "Alpha", ["  Python ", "ai", "AI", "  "])
    got = rl.get(item_id)
    assert got == {"id": 1, "url": "https://a.io", "title": "Alpha", "read": False,
                   "tags": ["ai", "python"]}, f"got {got!r}"


def test_get_unknown_id_returns_none():
    rl = _sample()
    assert rl.get(99) is None, "get() of a missing id should return None"


def test_duplicate_url_raises_value_error_and_changes_nothing():
    rl = _sample()
    try:
        rl.add("https://example.com/cooking", "Pasta again", ["food"])
        assert False, "expected ValueError"
    except ValueError as err:
        assert str(err) == "already saved: https://example.com/cooking", f"message was {str(err)!r}"
    assert rl.get(4)["title"] == "Weeknight pasta", "the original item must be unchanged"
    assert all(tag != "food" for tag, _ in rl.tag_counts()), "the failed add must not leave tags behind"
    assert rl.add("https://new.io", "New") == 6, "the next add should still work"


def test_search_matches_title_or_url_ignoring_case():
    rl = _sample()
    got = [item["id"] for item in rl.search("RAG")]
    assert got == [3], f"search('RAG') gave ids {got}"
    got = [item["id"] for item in rl.search("example.com")]
    assert got == [3, 4, 5], f"search('example.com') gave ids {got}"
    assert rl.search("attention")[0]["tags"] == ["ai", "papers"], "search results are full item dicts"
    assert rl.search("quantum") == [], "no match -> []"


def test_search_is_safe_from_sql_injection():
    rl = _sample()
    got = rl.search("' OR 1=1 --")
    assert got == [], f"got {len(got)} results - pass the search text as a ? parameter"
    rl.search("'); DROP TABLE items; --")
    assert len(rl.search("")) == 5, "the data should still be there"


def test_with_tag_finds_items_in_id_order():
    rl = _sample()
    got = [item["id"] for item in rl.with_tag("ai")]
    assert got == [1, 3, 5], f"with_tag('ai') gave ids {got}"
    assert [i["id"] for i in rl.with_tag(" AI ")] == [1, 3, 5], "tag lookups ignore case and spaces"
    assert rl.with_tag("nope") == [], "unknown tag -> []"


def test_mark_read_returns_whether_the_item_exists():
    rl = _sample()
    assert rl.mark_read(2) is True, "mark_read of an existing id returns True"
    assert rl.get(2)["read"] is True, "read should now be True (a real bool)"
    assert rl.mark_read(2) is True, "marking it again still returns True (the item exists)"
    assert rl.mark_read(42) is False, "mark_read of a missing id returns False"


def test_unread_pages_skip_read_items():
    rl = _sample()
    rl.mark_read(1)
    rl.mark_read(4)
    first = [i["id"] for i in rl.unread(page=1, per_page=2)]
    second = [i["id"] for i in rl.unread(page=2, per_page=2)]
    third = rl.unread(page=3, per_page=2)
    assert first == [2, 3], f"page 1 gave {first}"
    assert second == [5], f"page 2 gave {second}"
    assert third == [], f"page 3 gave {third!r}"
    assert [i["id"] for i in rl.unread()] == [2, 3, 5], "defaults: page=1, per_page=5"


def test_tag_counts_most_used_first_then_alphabetical():
    rl = _sample()
    got = rl.tag_counts()
    assert got == [("ai", 3), ("docs", 1), ("evals", 1), ("papers", 1), ("python", 1), ("rag", 1)], \
        f"got {got!r}"


def test_data_survives_reopening_the_file():
    rl = ReadingList("reading.db")
    rl.add("https://a.io", "Alpha", ["x"])
    rl.mark_read(1)
    rl.close()
    again = ReadingList("reading.db")
    got = again.get(1)
    again.close()
    assert got == {"id": 1, "url": "https://a.io", "title": "Alpha", "read": True, "tags": ["x"]}, \
        f"after reopening, get(1) gave {got!r} - commit every change"


def test_empty_list_edge_cases():
    rl = ReadingList()
    assert rl.search("a") == [] and rl.unread() == [] and rl.tag_counts() == [] \
        and rl.with_tag("ai") == [], "an empty reading list should give [] everywhere"
'''

MINI_SQL = {
    "id": "mini-sql",
    "chapter": "sql",
    "title": "Shelf: a SQLite reading list",
    "estimated_hours": 1.25,
    "main": "app.py",
    "files": ["app.py"],
    "brief": r'''
You collect links to papers, docs and blog posts faster than you read them. Time for a proper
reading list: saved in a real database file, taggable, searchable, with an "up next" queue.
It's the same shape as the storage layer behind every bookmarking app - and behind the
document store of a RAG system.

## What to build

A file `app.py` with a class **`ReadingList(path=":memory:")`** backed by `sqlite3`
(`path` is a database file name like `"reading.db"`, or `":memory:"`). You design the tables.

Items are returned as dicts shaped like this ("an item dict"):

```python
{"id": 1, "url": "https://a.io", "title": "Alpha", "read": False, "tags": ["ai", "python"]}
```

Methods:

- **`add(url, title, tags=())`** saves a new, unread item and returns its id (int).
- **`get(item_id)`** returns the item dict, or `None` if there's no such id.
- **`search(text)`** returns a list of item dicts whose title **or** url contains `text`.
- **`with_tag(tag)`** returns a list of item dicts that have that tag.
- **`mark_read(item_id)`** marks the item as read; returns `True` if it exists, else `False`.
- **`unread(page=1, per_page=5)`** returns one page (a list) of unread item dicts.
- **`tag_counts()`** returns a list of `(tag, count)` tuples.
- **`close()`** closes the database connection.

## Rules

- Ids start at `1` and go up by one per added item.
- Tags are stripped of surrounding spaces and lowercased; blank tags are ignored; duplicates
  are kept once. In an item dict, `"tags"` is sorted alphabetically (`[]` if none).
- `"read"` is a real `bool` (`False` for new items).
- Adding a url that is already saved raises `ValueError("already saved: <url>")` and changes
  **nothing** (no new item, no stray tags).
- `search` ignores upper/lower case, and `search("")` matches everything. Results are
  ordered by id; no match gives `[]`.
- Search text is user input: pass it with `?` parameters, never paste it into the SQL.
  Text like `' OR 1=1 --` must simply find nothing.
- `with_tag` cleans the tag the same way as `add` (so `" AI "` finds `"ai"`), results
  ordered by id; unknown tag gives `[]`.
- `mark_read` on an item that is already read still returns `True`.
- `unread` returns unread items ordered by id; `page=1` is the first `per_page` items,
  `page=2` the next ones, and so on. A page past the end gives `[]`.
- `tag_counts` includes only tags used by at least one item, most used first; ties sorted
  alphabetically by tag.
- Commit every change straight away. Creating a `ReadingList` on a file that already holds
  one must keep its data (don't fail because the tables already exist).

## Examples

```python
rl = ReadingList()
rl.add("https://arxiv.org/abs/1706.03762", "Attention Is All You Need", ["AI", "papers"])  # 1
rl.add("https://example.com/rag-guide", "A practical RAG guide", ["ai", " rag "])          # 2
rl.add("https://example.com/cooking", "Weeknight pasta")                                   # 3
rl.get(2)          # {"id": 2, "url": "https://example.com/rag-guide", "title": "A practical RAG guide",
                   #  "read": False, "tags": ["ai", "rag"]}
[i["id"] for i in rl.search("example.COM")]   # [2, 3]
rl.mark_read(1)    # True
rl.mark_read(99)   # False
[i["id"] for i in rl.unread(page=1, per_page=1)]   # [2]
rl.tag_counts()    # [("ai", 2), ("papers", 1), ("rag", 1)]
rl.add("https://example.com/cooking", "Again")    # raises ValueError("already saved: https://example.com/cooking")
```

## You'll need to find out

- How to make the database itself **refuse a duplicate value** in a column, and which
  `sqlite3` exception you get when an insert breaks that rule.
- How to find out **how many rows** an `UPDATE` statement actually changed.

## Try it yourself

```bash
python3 -c "
from app import ReadingList
rl = ReadingList('reading.db')
rl.add('https://docs.python.org/3/library/sqlite3.html', 'sqlite3 docs', ['python'])
print(rl.search('sqlite'))
"
```

Run it twice: the second time you should get the duplicate-url `ValueError` - proof the data
was saved to `reading.db`.
''',
    "explore": r'''
- Add a tiny command-line interface: `python3 app.py add <url> <title> --tag ai`, `python3 app.py next`.
- Add `remove(item_id)` that also deletes the item's tags (in one transaction).
- Record `added_at` and `read_at` timestamps and report "read this week".
- Rank search results: title matches before url matches.
''',
    "rubric": [
        "Every query uses ? parameters; no SQL is built from user input",
        "Multi-step writes (item + its tags) happen in a single transaction",
        "Turning a row into an item dict happens in one helper, not repeated in each method",
        "The table design is simple and fits the queries (e.g. a separate table for tags)",
    ],
    "starter_files": {"app.py": r'''
import sqlite3


class ReadingList:
    def __init__(self, path=":memory:"):
        ...

    def add(self, url, title, tags=()):
        ...

    def get(self, item_id):
        ...

    def search(self, text):
        ...

    def with_tag(self, tag):
        ...

    def mark_read(self, item_id):
        ...

    def unread(self, page=1, per_page=5):
        ...

    def tag_counts(self):
        ...

    def close(self):
        ...
'''},
    "solution_files": {"app.py": r'''
import sqlite3


def clean_tag(tag):
    return tag.strip().lower()


class ReadingList:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS items ("
                " id INTEGER PRIMARY KEY,"
                " url TEXT NOT NULL UNIQUE,"
                " title TEXT NOT NULL,"
                " read INTEGER NOT NULL DEFAULT 0)"
            )
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS tags ("
                " item_id INTEGER NOT NULL REFERENCES items(id),"
                " name TEXT NOT NULL)"
            )

    def _item(self, row):
        item_id, url, title, read = row
        names = self.conn.execute(
            "SELECT name FROM tags WHERE item_id = ? ORDER BY name", (item_id,)
        ).fetchall()
        return {"id": item_id, "url": url, "title": title, "read": bool(read),
                "tags": [name for (name,) in names]}

    def _items(self, sql, params=()):
        return [self._item(row) for row in self.conn.execute(sql, params).fetchall()]

    def add(self, url, title, tags=()):
        names = sorted({clean_tag(t) for t in tags if clean_tag(t)})
        try:
            with self.conn:
                cur = self.conn.execute("INSERT INTO items (url, title) VALUES (?, ?)", (url, title))
                item_id = cur.lastrowid
                for name in names:
                    self.conn.execute("INSERT INTO tags (item_id, name) VALUES (?, ?)",
                                      (item_id, name))
        except sqlite3.IntegrityError:
            raise ValueError(f"already saved: {url}")
        return item_id

    def get(self, item_id):
        row = self.conn.execute(
            "SELECT id, url, title, read FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        return self._item(row) if row else None

    def search(self, text):
        pattern = f"%{text}%"
        return self._items(
            "SELECT id, url, title, read FROM items WHERE title LIKE ? OR url LIKE ? ORDER BY id",
            (pattern, pattern),
        )

    def with_tag(self, tag):
        return self._items(
            "SELECT i.id, i.url, i.title, i.read FROM items i"
            " JOIN tags t ON t.item_id = i.id WHERE t.name = ? ORDER BY i.id",
            (clean_tag(tag),),
        )

    def mark_read(self, item_id):
        with self.conn:
            cur = self.conn.execute("UPDATE items SET read = 1 WHERE id = ?", (item_id,))
        return cur.rowcount > 0

    def unread(self, page=1, per_page=5):
        return self._items(
            "SELECT id, url, title, read FROM items WHERE read = 0 ORDER BY id LIMIT ? OFFSET ?",
            (per_page, (page - 1) * per_page),
        )

    def tag_counts(self):
        return self.conn.execute(
            "SELECT name, COUNT(*) FROM tags GROUP BY name ORDER BY COUNT(*) DESC, name"
        ).fetchall()

    def close(self):
        self.conn.close()
'''},
    "tests": _SQL_TESTS,
}


MINIS = [MINI_HTTP, MINI_API_DATA, MINI_REGEX, MINI_SQL]
