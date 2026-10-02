PROJECT = {
    "id": "resilient-client",
    "title": "Resilient LLM Client",
    "order": 10,
    "level": "Advanced",
    "estimated_hours": 3.5,
    "requires": ["classes", "errors", "json", "files", "dicts"],
    "tags": ["reliability", "retries", "caching", "cost-tracking", "rate-limiting"],
    "main": "client.py",
    "files": ["client.py"],
    "brief": r'''
# Resilient LLM client

LLM APIs fail in production all the time: `429 Too Many Requests`, `500`/`529 overloaded`,
timeouts. They are also slow and cost money per token. Every serious LLM app wraps the
raw SDK in a thin client that **retries the right errors with exponential backoff and
jitter**, **caches** deterministic requests, **tracks token usage and cost** per model and
**rate-limits** itself before the provider does it for you.

You will build these pieces separately (so each can be tested) and then compose them.
Time, sleeping and randomness are **injected** so that tests are instant and deterministic.

## What to build

A file `client.py` with the following public API.

### Errors

```python
class LLMError(Exception): ...
class RateLimitError(LLMError):      # retryable; __init__(self, message="", retry_after=None)
class ServerError(LLMError): ...     # retryable
class BadRequestError(LLMError): ... # NOT retryable
```

`RateLimitError` stores `retry_after` (seconds or `None`) as an attribute.

### `backoff_delay(attempt, base_delay=0.5, max_delay=8.0, rand=random.random) -> float`

`attempt` is 0 for the first retry, 1 for the second, ... The delay is
`min(max_delay, base_delay * 2 ** attempt)` multiplied by a jitter factor
`0.5 + 0.5 * rand()` (so it lies between half and all of the capped value).

### `call_with_retries(fn, *, max_retries=3, base_delay=0.5, max_delay=8.0, sleep=time.sleep, rand=random.random)`

- Call `fn()` (no arguments) and return its result.
- On `RateLimitError` or `ServerError`: if retries remain, `sleep(...)` and try again.
  The sleep is `err.retry_after` when the error is a `RateLimitError` with a
  `retry_after` that is not `None`, otherwise `backoff_delay(attempt, ...)`.
- Any other exception (including `BadRequestError`) propagates immediately, no retry.
- `fn` is called at most `1 + max_retries` times; after the last failure, re-raise that
  last error.

### `request_key(model, messages, temperature) -> str`

A stable cache key: the SHA-256 hex digest of the JSON encoding of
`{"model": ..., "messages": ..., "temperature": ...}` with sorted keys. The same request
must always give the same key, regardless of dict key order inside messages.

### `ResponseCache(path)`

- `get(key)` returns the cached value or `None`; `set(key, value)` stores it and
  **immediately writes** the whole cache to `path` as JSON.
- On creation, load the file if it exists. A missing **or corrupted** file means an empty
  cache (do not crash).

### `UsageTracker(prices)`

`prices` maps model name to USD per **million** tokens:
`{"small": {"input": 0.15, "output": 0.60}}`.

- `record(model, input_tokens, output_tokens)` - unknown model raises `ValueError`.
- `summary()` returns `{model: {"calls": int, "input_tokens": int, "output_tokens": int, "cost": float}}`
  for models that were used.
- `total_cost()` returns the sum of all costs (`0.0` if nothing recorded).

### `RateLimiter(max_calls, window, clock=time.monotonic, sleep=time.sleep)`

Sliding window: at most `max_calls` calls to `acquire()` in any `window` seconds.
`acquire()` returns immediately if a slot is free; otherwise it sleeps exactly until the
oldest call in the window expires (a call made at time `t` stops counting at `t + window`),
then records the call.

### `ResilientClient`

```python
ResilientClient(call, *, prices, cache_path=None, limiter=None, max_retries=3,
                base_delay=0.5, max_delay=8.0, sleep=time.sleep, rand=random.random)
client.complete(model, messages, temperature=0.0) -> str
client.usage          # the UsageTracker instance
```

`call(model=..., messages=..., temperature=...)` is the raw provider call. It returns
`{"text": str, "usage": {"input_tokens": int, "output_tokens": int}}` or raises the
errors above.

`complete` does, in order:

1. If a cache is configured **and `temperature == 0`**, return the cached text on a hit
   (no call, no usage recorded).
2. Otherwise call the provider through `call_with_retries`, calling
   `limiter.acquire()` (if a limiter is given) **before every attempt**.
3. Record usage for the successful response, store the text in the cache (only when
   caching applies, see 1.) and return the text.

## Running it locally

Write a fake `call` that raises `ServerError` twice then succeeds, and pass
`sleep=print` to watch the backoff delays. Standard library only.
''',
    "explore": r'''
# Explore

- **Retry libraries**: look at `tenacity` (`@retry`, `stop_after_attempt`,
  `wait_random_exponential`). Also note that the official OpenAI and Anthropic SDKs
  already retry some errors (`max_retries=` on the client) - read which ones.
- **Jitter strategies**: search "AWS exponential backoff and jitter" (full vs equal vs
  decorrelated jitter) and why jitter prevents a *thundering herd*.
- **Token bucket** rate limiting, and the difference between requests-per-minute and
  tokens-per-minute limits (the `x-ratelimit-*` response headers).
- **Idempotency**: why is retrying a *read* safe but retrying a non-idempotent write
  dangerous? Look up idempotency keys (Stripe popularised them).

## Make it real (optional, ungraded)

```bash
uv pip install anthropic   # or: pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
import anthropic
from client import ResilientClient, RateLimitError, ServerError, BadRequestError

sdk = anthropic.Anthropic(max_retries=0)   # we do the retrying ourselves

def call(model, messages, temperature):
    try:
        r = sdk.messages.create(model=model, max_tokens=300, messages=messages,
                                temperature=temperature)
    except anthropic.RateLimitError as e:
        raise RateLimitError(str(e)) from e
    except anthropic.InternalServerError as e:
        raise ServerError(str(e)) from e
    except anthropic.BadRequestError as e:
        raise BadRequestError(str(e)) from e
    return {"text": r.content[0].text,
            "usage": {"input_tokens": r.usage.input_tokens,
                      "output_tokens": r.usage.output_tokens}}
```

Look up current per-million-token prices for the model you use to fill in `prices`.
''',
    "rubric": [
        "Retry logic distinguishes retryable from non-retryable errors via the exception hierarchy, is bounded, and re-raises the original error.",
        "Each concern (backoff, cache, usage, rate limit) lives in its own small class/function; ResilientClient composes them instead of re-implementing them.",
        "All time/randomness is injected and never read from globals inside logic, making the code deterministic to test.",
        "Cache persistence is robust (atomic-ish writes or at least safe loading of missing/corrupted files) and keys are stable.",
        "Clear naming, docstrings for the public API, no magic numbers scattered around.",
    ],
    "starter_files": {
        "client.py": r'''
import random
import time


class LLMError(Exception):
    pass


class RateLimitError(LLMError):
    pass


class ServerError(LLMError):
    pass


class BadRequestError(LLMError):
    pass


def backoff_delay(attempt, base_delay=0.5, max_delay=8.0, rand=random.random):
    ...


def call_with_retries(fn, *, max_retries=3, base_delay=0.5, max_delay=8.0,
                      sleep=time.sleep, rand=random.random):
    ...


def request_key(model, messages, temperature):
    ...


class ResponseCache:
    def __init__(self, path):
        ...


class UsageTracker:
    def __init__(self, prices):
        ...


class RateLimiter:
    def __init__(self, max_calls, window, clock=time.monotonic, sleep=time.sleep):
        ...


class ResilientClient:
    def __init__(self, call, *, prices, cache_path=None, limiter=None, max_retries=3,
                 base_delay=0.5, max_delay=8.0, sleep=time.sleep, rand=random.random):
        ...

    def complete(self, model, messages, temperature=0.0):
        ...
''',
    },
    "solution_files": {
        "client.py": r'''
"""A resilient wrapper around a raw LLM call: retries, cache, usage and rate limiting."""

import hashlib
import json
import os
import random
import time
from collections import deque

TOKENS_PER_PRICE_UNIT = 1_000_000


class LLMError(Exception):
    """Base class for provider errors."""


class RateLimitError(LLMError):
    """HTTP 429: retry later, optionally after `retry_after` seconds."""

    def __init__(self, message="", retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class ServerError(LLMError):
    """HTTP 5xx: transient, safe to retry."""


class BadRequestError(LLMError):
    """HTTP 400: the request itself is wrong; retrying will not help."""


RETRYABLE = (RateLimitError, ServerError)


def backoff_delay(attempt, base_delay=0.5, max_delay=8.0, rand=random.random):
    """Capped exponential backoff with equal jitter."""
    capped = min(max_delay, base_delay * 2 ** attempt)
    return capped * (0.5 + 0.5 * rand())


def call_with_retries(fn, *, max_retries=3, base_delay=0.5, max_delay=8.0,
                      sleep=time.sleep, rand=random.random):
    """Call fn(), retrying retryable errors up to max_retries times."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except RETRYABLE as exc:
            if attempt == max_retries:
                raise
            retry_after = getattr(exc, "retry_after", None)
            if retry_after is not None:
                sleep(retry_after)
            else:
                sleep(backoff_delay(attempt, base_delay, max_delay, rand))


def request_key(model, messages, temperature):
    """Stable SHA-256 key for a request."""
    payload = {"model": model, "messages": messages, "temperature": temperature}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class ResponseCache:
    """A dict persisted to a JSON file after every write."""

    def __init__(self, path):
        self.path = path
        self._data = self._load()

    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value
        tmp = f"{self.path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh)
        os.replace(tmp, self.path)


class UsageTracker:
    """Token and cost accounting per model."""

    def __init__(self, prices):
        self.prices = prices
        self._stats = {}

    def record(self, model, input_tokens, output_tokens):
        if model not in self.prices:
            raise ValueError(f"no price configured for model {model!r}")
        price = self.prices[model]
        cost = (input_tokens * price["input"] + output_tokens * price["output"]) / TOKENS_PER_PRICE_UNIT
        stats = self._stats.setdefault(
            model, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0})
        stats["calls"] += 1
        stats["input_tokens"] += input_tokens
        stats["output_tokens"] += output_tokens
        stats["cost"] += cost

    def summary(self):
        return {model: dict(stats) for model, stats in self._stats.items()}

    def total_cost(self):
        return sum(stats["cost"] for stats in self._stats.values())


class RateLimiter:
    """Sliding-window limiter: at most max_calls per window seconds."""

    def __init__(self, max_calls, window, clock=time.monotonic, sleep=time.sleep):
        self.max_calls = max_calls
        self.window = window
        self._clock = clock
        self._sleep = sleep
        self._calls = deque()

    def _evict(self, now):
        while self._calls and self._calls[0] + self.window <= now:
            self._calls.popleft()

    def acquire(self):
        now = self._clock()
        self._evict(now)
        if len(self._calls) >= self.max_calls:
            self._sleep(self._calls[0] + self.window - now)
            now = self._clock()
            self._evict(now)
        self._calls.append(now)


class ResilientClient:
    """Composes retries, caching, rate limiting and usage tracking around `call`."""

    def __init__(self, call, *, prices, cache_path=None, limiter=None, max_retries=3,
                 base_delay=0.5, max_delay=8.0, sleep=time.sleep, rand=random.random):
        self._call = call
        self.usage = UsageTracker(prices)
        self.cache = ResponseCache(cache_path) if cache_path else None
        self.limiter = limiter
        self._retry_options = {"max_retries": max_retries, "base_delay": base_delay,
                               "max_delay": max_delay, "sleep": sleep, "rand": rand}

    def complete(self, model, messages, temperature=0.0):
        use_cache = self.cache is not None and temperature == 0
        key = request_key(model, messages, temperature) if use_cache else None
        if use_cache:
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        def attempt():
            if self.limiter is not None:
                self.limiter.acquire()
            return self._call(model=model, messages=messages, temperature=temperature)

        response = call_with_retries(attempt, **self._retry_options)
        usage = response["usage"]
        self.usage.record(model, usage["input_tokens"], usage["output_tokens"])
        if use_cache:
            self.cache.set(key, response["text"])
        return response["text"]
''',
    },
    "tests": r'''
import json
import os
from client import (BadRequestError, LLMError, RateLimitError, RateLimiter, ResilientClient,
                    ResponseCache, ServerError, UsageTracker, backoff_delay, call_with_retries,
                    request_key)

PRICES = {"small": {"input": 0.15, "output": 0.60}, "big": {"input": 3.0, "output": 15.0}}
MSGS = [{"role": "user", "content": "hi"}]


def close(a, b):
    return abs(a - b) < 1e-9


class Flaky:
    def __init__(self, errors, result="ok"):
        self.errors = list(errors)
        self.calls = 0
        self.result = result

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return self.result


class FakeProvider:
    def __init__(self, errors=()):
        self.errors = list(errors)
        self.calls = []

    def __call__(self, model, messages, temperature):
        self.calls.append((model, messages, temperature))
        if self.errors:
            raise self.errors.pop(0)
        return {"text": f"reply {len(self.calls)}", "usage": {"input_tokens": 1000, "output_tokens": 500}}


class FakeTime:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def test_error_hierarchy():
    for cls in (RateLimitError, ServerError, BadRequestError):
        assert issubclass(cls, LLMError)
    assert RateLimitError("slow down", retry_after=2).retry_after == 2
    assert RateLimitError("slow down").retry_after is None


def test_backoff_delay_exponential_capped_with_jitter():
    assert close(backoff_delay(0, 0.5, 8.0, rand=lambda: 1.0), 0.5)
    assert close(backoff_delay(2, 0.5, 8.0, rand=lambda: 1.0), 2.0)
    assert close(backoff_delay(2, 0.5, 8.0, rand=lambda: 0.0), 1.0), "jitter factor lies in [0.5, 1]"
    assert close(backoff_delay(10, 0.5, 8.0, rand=lambda: 0.5), 6.0), "delay must be capped by max_delay"


def test_retries_retryable_errors_with_backoff():
    fn = Flaky([ServerError("500"), RateLimitError("429"), ServerError("503")])
    sleeps = []
    got = call_with_retries(fn, max_retries=3, base_delay=1.0, max_delay=100,
                            sleep=sleeps.append, rand=lambda: 1.0)
    assert got == "ok" and fn.calls == 4, f"result={got!r}, calls={fn.calls}"
    assert [round(s, 6) for s in sleeps] == [1.0, 2.0, 4.0], f"sleeps: {sleeps!r}"


def test_retry_after_is_respected():
    fn = Flaky([RateLimitError("429", retry_after=7)])
    sleeps = []
    call_with_retries(fn, sleep=sleeps.append, rand=lambda: 1.0)
    assert sleeps == [7], f"sleeps: {sleeps!r}"


def test_non_retryable_errors_propagate_immediately():
    for err in (BadRequestError("400"), KeyError("oops")):
        fn = Flaky([err])
        sleeps = []
        try:
            call_with_retries(fn, sleep=sleeps.append, rand=lambda: 0.5)
        except type(err):
            pass
        else:
            raise AssertionError(f"{type(err).__name__} should propagate")
        assert fn.calls == 1 and sleeps == [], f"{type(err).__name__}: calls={fn.calls}, sleeps={sleeps}"


def test_gives_up_after_max_retries_with_last_error():
    errors = [ServerError("a"), ServerError("b"), ServerError("c")]
    fn = Flaky(errors)
    sleeps = []
    try:
        call_with_retries(fn, max_retries=2, sleep=sleeps.append, rand=lambda: 0.5)
    except ServerError as exc:
        assert str(exc) == "c", f"should re-raise the last error, got {exc!r}"
    else:
        raise AssertionError("expected ServerError")
    assert fn.calls == 3 and len(sleeps) == 2, f"calls={fn.calls}, sleeps={sleeps}"


def test_request_key_is_stable():
    k1 = request_key("small", [{"role": "user", "content": "hi"}], 0.0)
    k2 = request_key("small", [{"content": "hi", "role": "user"}], 0.0)
    assert k1 == k2, "key must not depend on dict key order"
    assert len(k1) == 64 and all(c in "0123456789abcdef" for c in k1), f"not a sha256 hex: {k1!r}"
    assert request_key("small", MSGS, 0.7) != k1
    assert request_key("big", MSGS, 0.0) != request_key("small", MSGS, 0.0)


def test_response_cache_persists_and_survives_corruption():
    cache = ResponseCache("cache.json")
    assert cache.get("k") is None
    cache.set("k", "value")
    assert json.load(open("cache.json")) == {"k": "value"}, "cache must be written to disk on set"
    assert ResponseCache("cache.json").get("k") == "value", "a new cache should load the file"
    with open("broken.json", "w") as fh:
        fh.write("{not json")
    assert ResponseCache("broken.json").get("k") is None


def test_usage_tracker_costs():
    usage = UsageTracker(PRICES)
    assert usage.total_cost() == 0.0
    usage.record("small", 1_000_000, 0)
    usage.record("small", 2000, 1000)
    usage.record("big", 100, 10)
    s = usage.summary()
    assert s["small"]["calls"] == 2 and s["small"]["input_tokens"] == 1_002_000
    assert s["small"]["output_tokens"] == 1000
    assert close(s["small"]["cost"], 0.15 + 0.0003 + 0.0006), f"small cost: {s['small']['cost']!r}"
    assert close(s["big"]["cost"], 0.0003 + 0.00015), f"big cost: {s['big']['cost']!r}"
    assert close(usage.total_cost(), 0.15 + 0.0009 + 0.00045)
    try:
        usage.record("mystery", 1, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown model should raise ValueError")


def test_rate_limiter_sliding_window():
    t = FakeTime()
    limiter = RateLimiter(3, 10, clock=t.clock, sleep=t.sleep)
    for _ in range(3):
        limiter.acquire()
    assert t.sleeps == [], f"first 3 calls should not wait, slept {t.sleeps}"
    t.now = 4.0
    limiter.acquire()
    assert t.sleeps == [6.0], f"4th call should wait until t=10, slept {t.sleeps}"
    t.now = 30.0
    limiter.acquire()
    assert t.sleeps == [6.0], "old calls should have expired"


def test_client_retries_tracks_usage_and_rate_limits():
    t = FakeTime()
    provider = FakeProvider([ServerError("503")])
    limiter = RateLimiter(10, 60, clock=t.clock, sleep=t.sleep)
    acquired = []
    original = limiter.acquire
    limiter.acquire = lambda: (acquired.append(1), original())[1]
    client = ResilientClient(provider, prices=PRICES, limiter=limiter, sleep=t.sleep,
                             rand=lambda: 1.0, base_delay=0.5)
    got = client.complete("small", MSGS, temperature=0.3)
    assert got == "reply 2", f"got {got!r}"
    assert len(provider.calls) == 2 and len(acquired) == 2, "acquire() before every attempt"
    assert provider.calls[0] == ("small", MSGS, 0.3)
    assert t.sleeps == [0.5], f"sleeps: {t.sleeps}"
    assert client.usage.summary()["small"]["calls"] == 1, "only successful responses are recorded"


def test_client_caches_only_deterministic_requests():
    provider = FakeProvider()
    client = ResilientClient(provider, prices=PRICES, cache_path="c.json", sleep=lambda s: None)
    assert client.complete("small", MSGS) == "reply 1"
    assert client.complete("small", MSGS) == "reply 1"
    assert len(provider.calls) == 1, "second identical temperature=0 request should hit the cache"
    assert client.usage.summary()["small"]["calls"] == 1, "cache hits cost nothing"
    client.complete("small", MSGS, temperature=0.9)
    client.complete("small", MSGS, temperature=0.9)
    assert len(provider.calls) == 3, "temperature > 0 requests must not be cached"
    fresh = ResilientClient(FakeProvider(), prices=PRICES, cache_path="c.json")
    assert fresh.complete("small", MSGS) == "reply 1", "cache should persist across instances"


def test_client_without_cache_and_bad_request():
    before = set(os.listdir("."))
    provider = FakeProvider([BadRequestError("bad")])
    client = ResilientClient(provider, prices=PRICES, sleep=lambda s: None)
    try:
        client.complete("small", MSGS)
    except BadRequestError:
        pass
    else:
        raise AssertionError("BadRequestError should propagate")
    assert len(provider.calls) == 1
    assert client.complete("small", MSGS) == "reply 2"
    assert client.complete("small", MSGS) == "reply 3", "no cache_path means no caching"
    assert set(os.listdir(".")) == before, "no cache file should be written without cache_path"
''',
}
