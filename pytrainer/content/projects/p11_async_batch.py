PROJECT = {
    "id": "async-batch",
    "title": "Async Batch Processor",
    "order": 11,
    "level": "Advanced",
    "estimated_hours": 2.5,
    "requires": ["async", "errors", "functions", "dicts"],
    "tags": ["async", "concurrency", "batch", "reliability"],
    "main": "batch.py",
    "files": ["batch.py"],
    "brief": r'''
# Async batch processor

Real AI workloads are rarely one prompt: you classify 5,000 support tickets, summarise
800 documents, or run an eval set of 300 questions. Doing that sequentially is painfully
slow (each call waits ~1-10 s on the network); firing all of them at once gets you
rate-limited. The standard answer is **bounded concurrency** with `asyncio`: at most N
requests in flight, a timeout per request, a few retries, and results that line up with
the inputs - with a failure in one item never killing the whole batch.

## What to build

A file `batch.py` with one coroutine function:

```python
async def run_batch(prompts, call, *, concurrency=5, timeout=10.0, retries=0,
                    on_progress=None) -> list[dict]: ...
```

- `prompts`: a list of prompt strings.
- `call`: an **async** function `await call(prompt)` returning the model result (any value).
- `concurrency`: maximum number of `call`s running at the same time. `< 1` raises
  `ValueError`.
- `timeout`: seconds allowed for **each attempt** of each item.
- `retries`: extra attempts per item after a failure or timeout (so each item is tried
  at most `1 + retries` times). Retry immediately, no sleep.
- `on_progress`: optional plain (non-async) function `on_progress(done, total)`, called
  once each time an item **finishes** (success or final failure), with `done` counting
  1, 2, ..., `total`.

### Result format

Return one dict per prompt, **in the same order as `prompts`** (not completion order):

```python
{
    "index": 0,              # position in prompts
    "prompt": "...",
    "status": "ok",          # "ok" | "error" | "timeout" (status of the LAST attempt)
    "result": ...,           # return value of call on success, else None
    "error": None,           # on failure a non-empty str; for exceptions: "<ExcType>: <message>"
    "attempts": 1,           # how many times call was started for this item
}
```

- An exception raised by `call` for one item must not affect other items.
- An empty `prompts` list returns `[]` without calling `on_progress`.
- The whole batch must actually run concurrently: 10 items that each take 0.1 s with
  `concurrency=10` should finish in about 0.1 s, not 1 s.

```python
async def fake_call(prompt):
    await asyncio.sleep(0.05)
    return prompt.upper()

results = asyncio.run(run_batch(["a", "b"], fake_call, concurrency=2))
# [{"index": 0, "prompt": "a", "status": "ok", "result": "A", "error": None, "attempts": 1},
#  {"index": 1, "prompt": "b", "status": "ok", "result": "B", "error": None, "attempts": 1}]
```

## Running it locally

Add an `if __name__ == "__main__":` demo with a fake call that sleeps a random amount,
sometimes raises, and sometimes hangs; print a progress line from `on_progress`. Standard
library only (`asyncio`).
''',
    "explore": r'''
# Explore

- **`asyncio.TaskGroup` vs `asyncio.gather`** (Python 3.11+): how do they differ when one
  task raises? Why did you (probably) not want TaskGroup's behaviour here?
- **`asyncio.timeout()`** context manager vs `asyncio.wait_for`, and what *cancellation*
  means for the coroutine that timed out (`CancelledError`).
- **Batch APIs**: OpenAI and Anthropic both offer asynchronous *Batch* / *Message
  Batches* APIs at ~50% cost for non-urgent jobs. When would you use those instead of
  your own concurrent client?

## Make it real (optional, ungraded)

```bash
uv pip install openai     # or: pip install openai
export OPENAI_API_KEY=sk-...
```

```python
import asyncio
from openai import AsyncOpenAI
from batch import run_batch

client = AsyncOpenAI()

async def call(prompt):
    resp = await client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content

prompts = [f"Give one fun fact about the number {i}." for i in range(20)]
results = asyncio.run(run_batch(prompts, call, concurrency=5, timeout=30, retries=2,
                                on_progress=lambda d, t: print(f"{d}/{t}")))
```
''',
    "rubric": [
        "Concurrency is bounded with an asyncio.Semaphore (or equivalent) that wraps only the actual call, and all items are scheduled together (gather/TaskGroup), not awaited one by one.",
        "Per-attempt timeouts use asyncio.wait_for / asyncio.timeout correctly; failures are isolated per item and never cancel the batch.",
        "Retry logic is bounded and clear; the status/error/attempts bookkeeping is easy to follow.",
        "Results are returned in input order and built through a small helper rather than duplicated dict literals.",
        "Input validation, naming and structure are clean; no blocking calls (time.sleep) inside async code.",
    ],
    "starter_files": {
        "batch.py": r'''
import asyncio


async def run_batch(prompts, call, *, concurrency=5, timeout=10.0, retries=0,
                    on_progress=None):
    ...
''',
    },
    "solution_files": {
        "batch.py": r'''
"""Run many async LLM calls with bounded concurrency, timeouts and retries."""

import asyncio


def _result(index, prompt, status, attempts, result=None, error=None):
    return {"index": index, "prompt": prompt, "status": status, "result": result,
            "error": error, "attempts": attempts}


async def run_batch(prompts, call, *, concurrency=5, timeout=10.0, retries=0,
                    on_progress=None):
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    semaphore = asyncio.Semaphore(concurrency)
    total = len(prompts)
    done = 0

    async def attempt(prompt):
        async with semaphore:
            return await asyncio.wait_for(call(prompt), timeout)

    async def process(index, prompt):
        nonlocal done
        for attempts in range(1, retries + 2):
            try:
                value = await attempt(prompt)
            except asyncio.TimeoutError:
                outcome = _result(index, prompt, "timeout", attempts,
                                  error=f"timed out after {timeout}s")
            except Exception as exc:
                outcome = _result(index, prompt, "error", attempts,
                                  error=f"{type(exc).__name__}: {exc}")
            else:
                outcome = _result(index, prompt, "ok", attempts, result=value)
                break
        done += 1
        if on_progress is not None:
            on_progress(done, total)
        return outcome

    return list(await asyncio.gather(*(process(i, p) for i, p in enumerate(prompts))))


if __name__ == "__main__":
    import random

    async def flaky(prompt):
        await asyncio.sleep(random.uniform(0.01, 0.2))
        if random.random() < 0.2:
            raise RuntimeError("server hiccup")
        return prompt[::-1]

    results = asyncio.run(run_batch([f"prompt {i}" for i in range(10)], flaky, concurrency=3,
                                    timeout=0.15, retries=1,
                                    on_progress=lambda d, t: print(f"{d}/{t}")))
    for r in results:
        print(r)
''',
    },
    "tests": r'''
import asyncio
import time
from batch import run_batch


class Tracker:
    """Fake async LLM call that records how many calls run at once."""

    def __init__(self, delays=None, default=0.02):
        self.delays = delays or {}
        self.default = default
        self.active = 0
        self.peak = 0
        self.started = []

    async def __call__(self, prompt):
        self.started.append(prompt)
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(self.delays.get(prompt, self.default))
        finally:
            self.active -= 1
        if prompt.startswith("boom"):
            raise RuntimeError(f"failed on {prompt}")
        return prompt.upper()


def run(coro):
    return asyncio.run(coro)


def test_returns_results_in_input_order():
    call = Tracker(delays={"a": 0.06, "b": 0.01, "c": 0.03})
    got = run(run_batch(["a", "b", "c"], call, concurrency=3))
    assert [r["result"] for r in got] == ["A", "B", "C"], f"got {got!r}"
    assert [r["index"] for r in got] == [0, 1, 2]


def test_result_dict_shape():
    got = run(run_batch(["hi"], Tracker(), concurrency=1))
    assert got == [{"index": 0, "prompt": "hi", "status": "ok", "result": "HI",
                    "error": None, "attempts": 1}], f"got {got!r}"


def test_concurrency_limit_is_respected():
    call = Tracker(default=0.02)
    run(run_batch([f"p{i}" for i in range(12)], call, concurrency=3))
    assert call.peak == 3, f"peak concurrency was {call.peak}, expected exactly 3"


def test_actually_runs_concurrently():
    call = Tracker(default=0.1)
    start = time.perf_counter()
    got = run(run_batch([f"p{i}" for i in range(10)], call, concurrency=10))
    elapsed = time.perf_counter() - start
    assert all(r["status"] == "ok" for r in got)
    assert elapsed < 0.5, f"10 x 0.1s calls took {elapsed:.2f}s - they are not running concurrently"


def test_concurrency_one_is_sequential():
    call = Tracker(default=0.005)
    run(run_batch(["a", "b", "c", "d"], call, concurrency=1))
    assert call.peak == 1 and call.started == ["a", "b", "c", "d"], f"started {call.started}"


def test_errors_are_isolated_per_item():
    got = run(run_batch(["ok1", "boom", "ok2"], Tracker(), concurrency=3))
    assert [r["status"] for r in got] == ["ok", "error", "ok"], f"got {got!r}"
    bad = got[1]
    assert bad["result"] is None and bad["attempts"] == 1
    assert bad["error"] == "RuntimeError: failed on boom", f"error: {bad['error']!r}"


def test_timeout_per_item():
    call = Tracker(delays={"slow": 1.0}, default=0.01)
    start = time.perf_counter()
    got = run(run_batch(["fast", "slow"], call, concurrency=2, timeout=0.05))
    assert time.perf_counter() - start < 0.5, "a timed-out call must be abandoned"
    assert got[0]["status"] == "ok"
    slow = got[1]
    assert slow["status"] == "timeout" and slow["result"] is None, f"got {slow!r}"
    assert isinstance(slow["error"], str) and slow["error"], "timeout needs an error message"


def test_retries_until_success():
    attempts = {}

    async def flaky(prompt):
        attempts[prompt] = attempts.get(prompt, 0) + 1
        await asyncio.sleep(0.001)
        if attempts[prompt] < 3:
            raise ConnectionError("try again")
        return "done"

    got = run(run_batch(["x", "y"], flaky, retries=2))
    assert [r["status"] for r in got] == ["ok", "ok"], f"got {got!r}"
    assert [r["attempts"] for r in got] == [3, 3]
    assert got[0]["error"] is None


def test_retries_exhausted_reports_last_failure():
    calls = []

    async def always_fails(prompt):
        calls.append(prompt)
        await asyncio.sleep(0.001)
        raise ValueError("nope")

    got = run(run_batch(["q"], always_fails, retries=2))
    assert len(calls) == 3, f"call started {len(calls)} times, expected 3"
    assert got[0]["status"] == "error" and got[0]["attempts"] == 3, f"got {got!r}"


def test_timeouts_are_retried_too():
    seen = []

    async def slow_then_fast(prompt):
        seen.append(prompt)
        await asyncio.sleep(1.0 if len(seen) == 1 else 0.001)
        return "ok"

    got = run(run_batch(["p"], slow_then_fast, timeout=0.05, retries=1))
    assert got[0]["status"] == "ok" and got[0]["attempts"] == 2, f"got {got!r}"


def test_progress_callback():
    events = []
    run(run_batch(["a", "boom", "c"], Tracker(), concurrency=2,
                  on_progress=lambda done, total: events.append((done, total))))
    assert events == [(1, 3), (2, 3), (3, 3)], f"progress events: {events}"


def test_empty_and_invalid_concurrency():
    events = []
    assert run(run_batch([], Tracker(), on_progress=lambda d, t: events.append(d))) == []
    assert events == [], "no progress calls for an empty batch"
    try:
        run(run_batch(["a"], Tracker(), concurrency=0))
    except ValueError:
        pass
    else:
        raise AssertionError("concurrency=0 should raise ValueError")
''',
}
