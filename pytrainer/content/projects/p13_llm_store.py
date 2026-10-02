PROJECT = {
    "id": "llm-store",
    "title": "LLM Feature with Storage & Usage Report",
    "module": "apis-data",
    "order": 13,
    "level": "Intermediate",
    "estimated_hours": 3,
    "requires": ["classes", "errors", "api-data", "dicts", "functions"],
    "tags": ["sqlite", "sql", "retries", "pagination", "token-usage", "cost"],
    "main": "service.py",
    "files": ["store.py", "service.py"],
    "brief": r'''
# LLM feature with storage & a usage report

A real LLM feature is more than one API call. The team wants to know **what was asked,
what came back, how many tokens it used and what it cost**, and they want the feature
to survive a flaky API. So you store every request in a database, retry the failures that
are worth retrying, page through the history and report token usage per model.
This is the "reliable API feature that calls an LLM and stores data" that job
postings ask for.

You build it in two files with the standard library `sqlite3` module. The LLM is
**injected** as a plain function, so the tests can use fakes. So can any real SDK.

## `store.py` (the data layer)

```python
class ChatStore:
    def __init__(self, path=":memory:"): ...
    def save(self, record): ...                                   # -> int (new id)
    def get(self, request_id): ...                                # -> dict | None
    def history(self, page=1, page_size=10, status=None): ...     # -> dict
    def usage_report(self, prices=None): ...                      # -> dict
    def close(self): ...
```

### The table

`__init__` opens (or creates) the sqlite database at `path` and creates this table if it
does not exist yet. Use exactly these names:

| column | type | meaning |
| --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | request id |
| `created_at` | `REAL` | timestamp from the injected clock |
| `model` | `TEXT` | model name |
| `prompt` | `TEXT` | the user prompt |
| `response` | `TEXT` | the model text, `NULL` if the request failed |
| `status` | `TEXT` | `"ok"` or `"error"` |
| `error` | `TEXT` | `"<ExceptionType>: <message>"` of the last failure, `NULL` if ok |
| `attempts` | `INTEGER` | how many times the LLM was called |
| `input_tokens` | `INTEGER` | `0` for failed requests |
| `output_tokens` | `INTEGER` | `0` for failed requests |
| `latency_ms` | `INTEGER` | total time including retries |

Data must survive: a new `ChatStore(path)` on the same file sees earlier rows.

### Methods

- `save(record)`: `record` is a dict with every column except `id`. Inserts one row,
  commits and returns the new `id`. Always use `?` placeholders: a prompt such as
  `x'); DROP TABLE requests; --` must be stored exactly as written.
- `get(request_id)`: returns the row as a dict with **all 11 columns** as keys, or
  `None` if there is no such id.
- `history(page=1, page_size=10, status=None)`: one page of rows, **newest first**
  (highest id first). `page` starts at 1. If `status` is given, only rows with that status
  are counted and returned. Returns:

  ```python
  {"items": [row_dict, ...], "page": 2, "page_size": 10, "total": 23, "has_more": True}
  ```
  `total` counts all matching rows. `has_more` is `True` if there are rows after this page.
  A page past the end returns `"items": []` and `"has_more": False`.
  Raise `ValueError` if `page < 1` or `page_size` is not between 1 and 100.
- `usage_report(prices=None)`: `prices` maps a model name to
  `{"input": usd_per_1M_tokens, "output": usd_per_1M_tokens}`. A missing or `None`
  `prices`, or a model not in it, costs `0.0`. Returns:

  ```python
  {
      "requests": 5, "errors": 1,
      "input_tokens": 400, "output_tokens": 120,
      "cost_usd": 0.000132,
      "by_model": {
          "fake-small": {"requests": 4, "errors": 1, "input_tokens": 300, "output_tokens": 100,
                         "cost_usd": 0.000105},
          ...
      },
  }
  ```
  Costs are rounded to 6 decimals. An empty store gives zeros and `"by_model": {}`.
- `close()`: closes the connection.

## `service.py` (the feature)

```python
RETRYABLE = (TimeoutError, ConnectionError)

class LLMServiceError(Exception): ...

class LLMService:
    def __init__(self, llm, store, model="fake-small", max_retries=2,
                 backoff=0.5, clock=time.time, sleep=time.sleep): ...
    def ask(self, prompt): ...     # -> dict (the stored row)
```

`llm(prompt, model)` returns
`{"text": "...", "usage": {"input_tokens": 12, "output_tokens": 5}}`, or raises.

`ask(prompt)`:

1. If `prompt` is not a string or is empty/whitespace, raise `ValueError`. Do not call the
   LLM and store nothing.
2. Call `clock()` once at the start. That value is `created_at`.
3. Call `llm(prompt, self.model)`. If it raises one of `RETRYABLE`, wait with
   `sleep(backoff * 2 ** n)` (n = 0 for the first retry, then 1, 2...) and try again,
   up to `max_retries` extra attempts. Any other exception is **not** retried.
4. Call `clock()` once more at the end. `latency_ms = round((end - start) * 1000)`.
5. Save exactly one row (success or failure) and return it as `store.get(new_id)`.
6. On final failure, save the row with `status="error"`, `response=None`, 0 tokens,
   and `error="TimeoutError: upstream timed out"` (type name + message of the last
   exception), then raise `LLMServiceError` **chained** from that exception
   (`raise ... from exc`).

## Example

```python
store = ChatStore("chat.db")
service = LLMService(my_llm, store)
row = service.ask("Summarise RAG in one line")
row["status"], row["attempts"], row["input_tokens"]    # ("ok", 1, 12)
store.history(page=1, page_size=2)["items"][0]["id"]   # the newest request
store.usage_report({"fake-small": {"input": 0.15, "output": 0.60}})
```

Standard library only (`sqlite3`, `time`).
''',
    "explore": r'''
# Explore

- **`sqlite3` rows as dicts**: look up `sqlite3.Row` and `connection.row_factory`. Also
  read why you must never build SQL with f-strings (search "SQL injection" and
  "parameterized queries").
- **Pagination styles**: `LIMIT/OFFSET` (what you built) vs **cursor / keyset pagination**
  (`WHERE id < ? ORDER BY id DESC LIMIT ?`). Why do large APIs such as Stripe's and
  GitHub's use cursors? What goes wrong with OFFSET when new rows arrive while someone
  is paging?
- **Retry etiquette**: read about *exponential backoff with jitter* and the
  `Retry-After` header on HTTP 429. Which errors should never be retried (for example 400
  or 401)?

## Make it real (optional, ungraded)

```bash
uv pip install anthropic     # or: pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
import anthropic
client = anthropic.Anthropic()

def llm(prompt, model):
    msg = client.messages.create(model=model, max_tokens=300,
                                 messages=[{"role": "user", "content": prompt}])
    return {"text": msg.content[0].text,
            "usage": {"input_tokens": msg.usage.input_tokens,
                      "output_tokens": msg.usage.output_tokens}}
```

Map `anthropic.APITimeoutError` / `anthropic.APIConnectionError` / `anthropic.RateLimitError`
to your retry logic. Then put a tiny HTTP endpoint in front of it (`http.server`, or
FastAPI if you know it) with `POST /ask` and `GET /history?page=2`.
''',
    "rubric": [
        "All SQL uses ? placeholders; the schema is created once and the store is a thin, well-named data layer with no LLM logic.",
        "Retry logic only retries transient errors, uses exponential backoff through the injected sleep, and never retries forever.",
        "Exactly one row is stored per request, success or failure, and errors are chained (raise ... from exc) so the cause is not lost.",
        "Pagination and the usage report push the work to SQL (ORDER BY/LIMIT/OFFSET, COUNT, SUM, GROUP BY) instead of loading every row into Python.",
        "Time and sleeping are injected (no real waiting in tests); code is small, typed or documented, and easy to read.",
    ],
    "starter_files": {
        "store.py": r'''
import sqlite3


class ChatStore:
    def __init__(self, path=":memory:"):
        ...

    def save(self, record):
        ...

    def get(self, request_id):
        ...

    def history(self, page=1, page_size=10, status=None):
        ...

    def usage_report(self, prices=None):
        ...

    def close(self):
        ...
''',
        "service.py": r'''
import time

RETRYABLE = (TimeoutError, ConnectionError)


class LLMServiceError(Exception):
    pass


class LLMService:
    def __init__(self, llm, store, model="fake-small", max_retries=2,
                 backoff=0.5, clock=time.time, sleep=time.sleep):
        ...

    def ask(self, prompt):
        ...
''',
    },
    "solution_files": {
        "store.py": r'''
"""sqlite3 storage for LLM requests, responses and token usage."""

import sqlite3

COLUMNS = ["id", "created_at", "model", "prompt", "response", "status", "error",
           "attempts", "input_tokens", "output_tokens", "latency_ms"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at REAL NOT NULL,
    model TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    status TEXT NOT NULL,
    error TEXT,
    attempts INTEGER NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL
)
"""


def _cost(prices, model, input_tokens, output_tokens):
    price = (prices or {}).get(model)
    if not price:
        return 0.0
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


class ChatStore:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def save(self, record):
        fields = COLUMNS[1:]
        sql = (f"INSERT INTO requests ({', '.join(fields)}) "
               f"VALUES ({', '.join('?' for _ in fields)})")
        cur = self.conn.execute(sql, [record[f] for f in fields])
        self.conn.commit()
        return cur.lastrowid

    def get(self, request_id):
        row = self.conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
        return dict(row) if row else None

    def history(self, page=1, page_size=10, status=None):
        if page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        where, params = ("WHERE status = ?", [status]) if status is not None else ("", [])
        total = self.conn.execute(f"SELECT COUNT(*) FROM requests {where}", params).fetchone()[0]
        rows = self.conn.execute(
            f"SELECT * FROM requests {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            params + [page_size, (page - 1) * page_size]).fetchall()
        return {"items": [dict(r) for r in rows], "page": page, "page_size": page_size,
                "total": total, "has_more": page * page_size < total}

    def usage_report(self, prices=None):
        rows = self.conn.execute(
            "SELECT model, COUNT(*) AS requests, "
            "SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS errors, "
            "SUM(input_tokens) AS input_tokens, SUM(output_tokens) AS output_tokens "
            "FROM requests GROUP BY model ORDER BY model").fetchall()
        report = {"requests": 0, "errors": 0, "input_tokens": 0, "output_tokens": 0,
                  "cost_usd": 0.0, "by_model": {}}
        total_cost = 0.0
        for r in rows:
            cost = _cost(prices, r["model"], r["input_tokens"], r["output_tokens"])
            total_cost += cost
            report["by_model"][r["model"]] = {
                "requests": r["requests"], "errors": r["errors"],
                "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"],
                "cost_usd": round(cost, 6)}
            for key in ("requests", "errors", "input_tokens", "output_tokens"):
                report[key] += r[key]
        report["cost_usd"] = round(total_cost, 6)
        return report

    def close(self):
        self.conn.close()
''',
        "service.py": r'''
"""An LLM-backed feature: validate, call with retries, store every request."""

import time

RETRYABLE = (TimeoutError, ConnectionError)


class LLMServiceError(Exception):
    """The LLM call failed for good (after any retries)."""


class LLMService:
    def __init__(self, llm, store, model="fake-small", max_retries=2,
                 backoff=0.5, clock=time.time, sleep=time.sleep):
        self.llm = llm
        self.store = store
        self.model = model
        self.max_retries = max_retries
        self.backoff = backoff
        self.clock = clock
        self.sleep = sleep

    def _call_with_retries(self, prompt):
        """Return (reply, attempts, last_exception); reply is None on failure."""
        attempts = 0
        while True:
            attempts += 1
            try:
                return self.llm(prompt, self.model), attempts, None
            except RETRYABLE as exc:
                if attempts > self.max_retries:
                    return None, attempts, exc
                self.sleep(self.backoff * 2 ** (attempts - 1))
            except Exception as exc:  # not worth retrying: record it and stop
                return None, attempts, exc

    def ask(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        start = self.clock()
        reply, attempts, exc = self._call_with_retries(prompt)
        end = self.clock()
        record = {"created_at": start, "model": self.model, "prompt": prompt,
                  "attempts": attempts, "latency_ms": round((end - start) * 1000)}
        if exc is None:
            usage = reply.get("usage", {})
            record.update(response=reply["text"], status="ok", error=None,
                          input_tokens=usage.get("input_tokens", 0),
                          output_tokens=usage.get("output_tokens", 0))
        else:
            record.update(response=None, status="error",
                          error=f"{type(exc).__name__}: {exc}",
                          input_tokens=0, output_tokens=0)
        row = self.store.get(self.store.save(record))
        if exc is not None:
            raise LLMServiceError(f"LLM call failed after {attempts} attempt(s)") from exc
        return row
''',
    },
    "tests": r'''
import sqlite3
from store import ChatStore
from service import LLMService, LLMServiceError

COLS = {"id", "created_at", "model", "prompt", "response", "status", "error",
        "attempts", "input_tokens", "output_tokens", "latency_ms"}


class FakeLLM:
    """Plays a script: each item is a reply dict or an exception to raise."""

    def __init__(self, script=None):
        self.script = list(script or [])
        self.calls = []

    def __call__(self, prompt, model):
        self.calls.append((prompt, model))
        if self.script:
            item = self.script.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        return {"text": f"echo: {prompt}",
                "usage": {"input_tokens": len(prompt.split()), "output_tokens": 2}}


class Clock:
    def __init__(self, start=1000.0, step=0.25):
        self.t = start - step
        self.step = step

    def __call__(self):
        self.t += self.step
        return self.t


def make(script=None, **kw):
    store = ChatStore()
    sleeps = []
    llm = FakeLLM(script)
    svc = LLMService(llm, store, clock=Clock(), sleep=sleeps.append, **kw)
    return svc, store, llm, sleeps


def ok(text="hi", i=10, o=3):
    return {"text": text, "usage": {"input_tokens": i, "output_tokens": o}}


def test_ask_stores_and_returns_the_row():
    svc, store, llm, _ = make([ok("Hello!", 12, 5)])
    row = svc.ask("Say hello")
    assert set(row) == COLS, f"row keys: {sorted(row)}"
    assert row["status"] == "ok" and row["response"] == "Hello!", f"got {row!r}"
    assert (row["input_tokens"], row["output_tokens"], row["attempts"]) == (12, 5, 1), f"got {row!r}"
    assert row["error"] is None and row["model"] == "fake-small"
    assert store.get(row["id"]) == row
    assert llm.calls == [("Say hello", "fake-small")], f"llm calls: {llm.calls!r}"
    assert store.get(999) is None


def test_table_has_the_specified_columns():
    ChatStore("cols.db").close()
    cols = {r[1] for r in sqlite3.connect("cols.db").execute("PRAGMA table_info(requests)")}
    assert cols == COLS, f"table 'requests' has columns {sorted(cols)}"


def test_data_persists_in_a_database_file():
    store = ChatStore("chat.db")
    svc = LLMService(FakeLLM(), store, clock=Clock(), sleep=lambda s: None)
    first = svc.ask("one")
    svc.ask("two")
    store.close()
    again = ChatStore("chat.db")
    assert again.history()["total"] == 2, "rows should survive reopening the file"
    assert again.get(first["id"])["prompt"] == "one"
    raw = sqlite3.connect("chat.db").execute("SELECT prompt FROM requests ORDER BY id").fetchall()
    assert [r[0] for r in raw] == ["one", "two"], f"got {raw!r}"


def test_prompts_with_sql_are_stored_verbatim():
    svc, store, _, _ = make()
    evil = "x'); DROP TABLE requests; --"
    row = svc.ask(evil)
    assert store.get(row["id"])["prompt"] == evil
    assert store.history()["total"] == 1, "the table must still exist and hold the row"


def test_invalid_prompt_is_rejected_before_calling_llm():
    svc, store, llm, _ = make()
    for bad in ["", "   ", None, 42]:
        try:
            svc.ask(bad)
        except ValueError:
            continue
        raise AssertionError(f"ask({bad!r}) should raise ValueError")
    assert llm.calls == [], "the LLM must not be called for invalid prompts"
    assert store.history()["total"] == 0, "nothing should be stored for invalid prompts"


def test_retries_transient_errors_with_backoff():
    svc, store, llm, sleeps = make([TimeoutError("slow"), ConnectionError("reset"), ok("finally")])
    row = svc.ask("hello")
    assert row["status"] == "ok" and row["response"] == "finally", f"got {row!r}"
    assert row["attempts"] == 3, f"attempts = {row['attempts']}"
    assert sleeps == [0.5, 1.0], f"sleep calls: {sleeps!r}"
    assert store.history()["total"] == 1, "exactly one row per request"


def test_gives_up_after_max_retries_and_stores_the_failure():
    errors = [TimeoutError("upstream timed out")] * 5
    svc, store, llm, sleeps = make(errors, max_retries=2, backoff=1)
    try:
        svc.ask("hello")
    except LLMServiceError as exc:
        assert isinstance(exc.__cause__, TimeoutError), "raise LLMServiceError from the last error"
    else:
        raise AssertionError("expected LLMServiceError")
    assert len(llm.calls) == 3, f"llm called {len(llm.calls)} times, expected 1 + 2 retries"
    assert sleeps == [1, 2], f"sleep calls: {sleeps!r}"
    items = store.history()["items"]
    assert len(items) == 1, f"expected one stored row, got {len(items)}"
    row = items[0]
    assert row["status"] == "error" and row["response"] is None, f"got {row!r}"
    assert row["error"] == "TimeoutError: upstream timed out", f"error = {row['error']!r}"
    assert (row["attempts"], row["input_tokens"], row["output_tokens"]) == (3, 0, 0), f"got {row!r}"


def test_non_retryable_errors_fail_immediately():
    svc, store, llm, sleeps = make([PermissionError("invalid api key"), ok()])
    try:
        svc.ask("hello")
    except LLMServiceError as exc:
        assert isinstance(exc.__cause__, PermissionError)
    else:
        raise AssertionError("expected LLMServiceError")
    assert len(llm.calls) == 1 and sleeps == [], "non-transient errors must not be retried"
    row = store.history(status="error")["items"][0]
    assert row["attempts"] == 1 and row["error"] == "PermissionError: invalid api key", f"got {row!r}"


def test_created_at_and_latency_come_from_the_injected_clock():
    ticks = iter([100.0, 100.8, 200.0, 200.0425])
    store = ChatStore()
    svc = LLMService(FakeLLM(), store, clock=lambda: next(ticks), sleep=lambda s: None)
    row = svc.ask("a")
    assert row["created_at"] == 100.0 and row["latency_ms"] == 800, f"got {row!r}"
    row = svc.ask("b")
    assert row["created_at"] == 200.0 and row["latency_ms"] == 42, f"got {row!r}"


def test_history_pages_newest_first():
    svc, store, _, _ = make()
    for i in range(1, 24):
        svc.ask(f"prompt {i}")
    p1 = store.history(page=1, page_size=10)
    assert [r["prompt"] for r in p1["items"]][:2] == ["prompt 23", "prompt 22"], "newest first"
    assert (p1["page"], p1["page_size"], p1["total"], p1["has_more"]) == (1, 10, 23, True), f"got {p1 | {'items': '...'}!r}"
    p3 = store.history(page=3, page_size=10)
    assert [r["prompt"] for r in p3["items"]] == ["prompt 3", "prompt 2", "prompt 1"]
    assert p3["has_more"] is False
    assert store.history(page=4, page_size=10)["items"] == []
    exact = store.history(page=1, page_size=23)
    assert exact["has_more"] is False and len(exact["items"]) == 23
    default = store.history()
    assert len(default["items"]) == 10 and default["page_size"] == 10


def test_history_status_filter_and_bad_arguments():
    svc, store, _, _ = make([ok(), ValueError("boom"), ok()])
    svc.ask("a")
    try:
        svc.ask("b")
    except LLMServiceError:
        pass
    svc.ask("c")
    errs = store.history(status="error")
    assert errs["total"] == 1 and errs["items"][0]["prompt"] == "b", f"got {errs!r}"
    oks = store.history(status="ok")
    assert [r["prompt"] for r in oks["items"]] == ["c", "a"] and oks["total"] == 2
    for kwargs in [{"page": 0}, {"page_size": 0}, {"page_size": 101}]:
        try:
            store.history(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"history(**{kwargs}) should raise ValueError")


def test_usage_report_totals_and_cost():
    store = ChatStore()
    small = LLMService(FakeLLM([ok(i=1000, o=200), ok(i=3000, o=800), TimeoutError("x")]),
                       store, model="fake-small", max_retries=0, clock=Clock(), sleep=lambda s: None)
    big = LLMService(FakeLLM([ok(i=500, o=100)]), store, model="fake-big",
                     clock=Clock(), sleep=lambda s: None)
    local = LLMService(FakeLLM([ok(i=10, o=10)]), store, model="local", clock=Clock(),
                       sleep=lambda s: None)
    small.ask("a")
    small.ask("b")
    try:
        small.ask("c")
    except LLMServiceError:
        pass
    big.ask("d")
    local.ask("e")
    prices = {"fake-small": {"input": 0.15, "output": 0.60}, "fake-big": {"input": 3.0, "output": 15.0}}
    rep = store.usage_report(prices)
    assert (rep["requests"], rep["errors"]) == (5, 1), f"got {rep!r}"
    assert (rep["input_tokens"], rep["output_tokens"]) == (4510, 1110), f"got {rep!r}"
    s = rep["by_model"]["fake-small"]
    assert s == {"requests": 3, "errors": 1, "input_tokens": 4000, "output_tokens": 1000,
                 "cost_usd": 0.0012}, f"fake-small: {s!r}"
    assert rep["by_model"]["fake-big"]["cost_usd"] == 0.003, f"got {rep['by_model']['fake-big']!r}"
    assert rep["by_model"]["local"]["cost_usd"] == 0.0, "models without a price cost 0.0"
    assert abs(rep["cost_usd"] - 0.0042) < 1e-9, f"total cost {rep['cost_usd']!r}"
    assert store.usage_report()["cost_usd"] == 0.0, "no prices means no cost"


def test_usage_report_on_empty_store():
    rep = ChatStore().usage_report({"fake-small": {"input": 1, "output": 1}})
    assert rep == {"requests": 0, "errors": 0, "input_tokens": 0, "output_tokens": 0,
                   "cost_usd": 0.0, "by_model": {}}, f"got {rep!r}"
''',
}
