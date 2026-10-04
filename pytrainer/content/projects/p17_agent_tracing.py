PROJECT = {
    "id": "agent-tracing",
    "title": "Trace Your Agent: Spans and a Waterfall",
    "module": "evals",
    "order": 14.5,
    "level": "Advanced",
    "estimated_hours": 3,
    "requires": ["classes", "json", "async", "observability"],
    "tags": ["observability", "tracing", "spans", "opentelemetry", "agents", "contextvars"],
    "main": "traced_agent.py",
    "files": ["tracing.py", "traced_agent.py"],
    "brief": r'''
# Trace your agent

An agent that answers wrongly or slowly is a black box until you can see *what it did*: which model
calls it made, which tools ran, how long each took, how many tokens went where, and which step
failed. Production teams get that from **tracing**. Every unit of work is a **span** (a name, a
start, an end, a status and some attributes), and spans nest: one `agent.run` span holds a span per
step, which holds a span per model call and per tool call. Laid out on a time axis, the spans make a
**waterfall**, and the slow or broken part is visible at a glance.

OpenTelemetry, Langfuse, LangSmith and every APM tool are built on this idea. In this project you
write a small tracer yourself, then instrument an agent loop with it.

**Press Run** once your code works: `traced_agent.py` runs a demo agent and writes `traces.jsonl`,
and PyTrainer draws the spans as a waterfall under the output. Click a span to see its attributes.
(The trace viewer page, `#/traces`, opens any `traces.jsonl` you produce elsewhere.)

## Part 1: `tracing.py`

```python
class Span:
    name; trace_id; span_id; parent_id; start; end; status; attributes
    def set(self, key, value): ...
    def fail(self, message): ...
    def to_dict(self): ...

class Tracer:
    def __init__(self, clock=time.perf_counter, new_id=None): ...
    def span(self, name, **attributes): ...     # a context manager that yields the Span
    def current(self): ...
    def traced(self, name=None): ...            # a decorator
    @property
    def spans(self): ...                        # finished spans, as dicts
    def export(self, path): ...
```

### `Tracer(clock=time.perf_counter, new_id=None)`

`clock()` returns the current time in seconds. `new_id()` returns a fresh id string; when it's
`None`, use `secrets.token_hex(8)`. The tests inject both, so never call `time` or `secrets` directly
anywhere else.

### `with tracer.span(name, **attributes) as span:`

- On entry, create a `Span`: `span_id = new_id()`, `start = clock()`, `status = "ok"`, and the
  keyword arguments as its first attributes (stored with `set`).
- **Nesting:** the span that is open *in the current context* is its parent. A span opened with
  nothing open is a **root**: `parent_id` is `None` and its `trace_id` is its own `span_id`. A child
  has its parent's `span_id` as `parent_id` and inherits its `trace_id`.
- While the block runs, `tracer.current()` returns this span; afterwards it returns the parent again
  (or `None`).
- On exit, set `end = clock()` and record the span as finished. If an exception escapes the block,
  the span's status is `"error"` and its `"error"` attribute is `"<ExceptionType>: <message>"`, for
  example `"KeyError: 'B7'"` (use `str(exc)` for the message). The exception keeps propagating:
  tracing never swallows errors.
- **Async-safe:** keep the open span in a `contextvars.ContextVar` (one per `Tracer`), not in an
  attribute. Then two tasks running at once under `asyncio.gather` each see their own open span, and
  their children get the right parents.

### `Span`

- `set(key, value)`: store an attribute. `str`, `int`, `float`, `bool` and `None` are kept as they
  are; anything else is stored as `str(value)`. A string longer than 300 characters is cut to its
  first 300 (prompts and tool results can be huge, and traces are kept for a long time).
- `fail(message)`: mark the span as an error without an exception: `status = "error"` and
  `set("error", message)`.
- `to_dict()` returns:

```python
{"name": "llm.call", "trace_id": "a1", "span_id": "a3", "parent_id": "a2",
 "start": 10.0, "end": 10.25, "duration_ms": 250.0, "status": "ok",
 "attributes": {"step": 1, "input_tokens": 42}}
```

  `duration_ms` is `(end - start) * 1000` rounded to 3 decimals. `attributes` is a copy.

### `tracer.spans` and `tracer.export(path)`

`spans` is the list of finished spans as dicts, **in the order they finished** (so a child comes
before its parent). `export(path)` writes them to a JSON Lines file, one `to_dict()` per line, and
returns how many it wrote.

### `@tracer.traced()` / `@tracer.traced("name")`

A decorator that runs the function inside a span named `name`, or the function's `__qualname__`
when no name is given. It keeps the function's name and docstring (`functools.wraps`) and works for
**`async def` functions too**: their span must cover the awaited work, not just the creation of the
coroutine (check with `inspect.iscoroutinefunction`).

## Part 2: `traced_agent.py`

The starter has a working agent loop, `run_traced_agent(tracer, llm, tools, question, max_steps=5)`,
with no tracing. `llm(messages)` returns a final answer or tool calls, plus token usage:

```python
{"type": "final", "content": "...", "usage": {"input_tokens": 50, "output_tokens": 12}}
{"type": "tool_calls", "calls": [{"id": "c1", "name": "get_order", "arguments": {"order_id": "A1"}}],
 "usage": {...}}
```

`tools` maps a name to a Python function, called with the arguments as keyword arguments. Keep the
loop's behaviour exactly as it is and add these spans:

| Span | Parent | Attributes |
| --- | --- | --- |
| `agent.run` | none (a root) | `question`; on success also `steps` (model calls made), `answer`, and the totals `input_tokens` and `output_tokens` |
| `agent.step` | `agent.run` | `step` (1, 2, ...) |
| `llm.call` | its `agent.step` | `step`, `messages` (how many messages were sent), `reply` (`"final"` or `"tool_calls"`), and `input_tokens` / `output_tokens` from `usage` (0 when it's missing) |
| `tool.<name>` | its `agent.step` | `call_id`, `arguments` (as `json.dumps(arguments, sort_keys=True)`), and `result` (the string sent back to the model) |

- When a tool raises, the loop already sends `"Error: <Type>: <message>"` back to the model and goes
  on. Its span must say so: `fail(...)` it with that same text. An unknown tool name is handled the
  same way, and its span is still named `tool.<name>`.
- When the step limit is hit, the loop raises `RuntimeError`. Let it escape through `agent.run`,
  so the root span ends with status `"error"`.

## Running it

Press **Run**: the demo at the bottom of `traced_agent.py` runs a scripted agent (one tool fails on
purpose) and exports `traces.jsonl`. Look at the waterfall: which span is slowest, and where is the
red one? Standard library only (`contextvars`, `functools`, `inspect`, `json`, `secrets`, `time`).
''',
    "explore": r'''
# Explore

- **OpenTelemetry's model**: read the "Traces" concept page on opentelemetry.io. Map your fields onto
  theirs: span context (`trace_id`, `span_id`), parent, span kind, status, attributes, *events*. What
  are span events for, and how would you add `span.event("retry", attempt=2)`?
- **GenAI semantic conventions**: OpenTelemetry has agreed attribute names for model calls
  (`gen_ai.request.model`, `gen_ai.usage.input_tokens`, ...). Rename your attributes to match, and a
  real backend could read your traces.
- **Context propagation**: your tracer follows work across `await` thanks to `contextvars`. What
  happens with threads (`concurrent.futures`)? Look up `contextvars.copy_context().run` and how
  tracing libraries carry a trace id across an HTTP call (the W3C `traceparent` header).
- **Sampling**: tracing every request is expensive at scale. Look up head-based vs tail-based
  sampling, and why "keep every trace that has an error" needs the tail kind.

## Make it real (optional, ungraded)

```bash
uv pip install opentelemetry-sdk     # or: pip install opentelemetry-sdk
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("my-agent")

with tracer.start_as_current_span("agent.run") as span:
    span.set_attribute("question", "Where is order A1?")
    with tracer.start_as_current_span("llm.call"):
        ...
```

The API is almost the same as yours: `start_as_current_span` is your `span()`, and the "current span"
lives in a context variable for the same reason yours does.
''',
    "rubric": [
        "The open span lives in a contextvars.ContextVar owned by the tracer, so nesting is correct across await and concurrent tasks.",
        "Spans always end and are always recorded, including when the block raises (try/finally or a context manager that handles errors), and errors are never swallowed.",
        "The decorator handles sync and async functions separately, keeps metadata with functools.wraps, and the async span covers the awaited work.",
        "Instrumentation stays out of the agent's logic: the loop reads the same as before, with spans and attributes added around the existing steps.",
        "Attribute values are bounded and JSON-safe, and the clock and ids are injected so traces are testable.",
    ],
    "starter_files": {
        "tracing.py": r'''
import time


class Span:
    def __init__(self, name, trace_id, span_id, parent_id, start):
        ...

    def set(self, key, value):
        ...

    def fail(self, message):
        ...

    def to_dict(self):
        ...


class Tracer:
    def __init__(self, clock=time.perf_counter, new_id=None):
        ...

    def span(self, name, **attributes):
        ...

    def current(self):
        ...

    def traced(self, name=None):
        ...

    @property
    def spans(self):
        ...

    def export(self, path):
        ...
''',
        "traced_agent.py": r'''
"""An agent loop to instrument. Add spans; keep the behaviour the same."""

import json


def run_traced_agent(tracer, llm, tools, question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        reply = llm(messages)
        if reply["type"] == "final":
            return reply["content"]
        messages.append({"role": "assistant", "tool_calls": reply["calls"]})
        for call in reply["calls"]:
            func = tools.get(call["name"])
            if func is None:
                result = f"Error: unknown tool {call['name']}"
            else:
                try:
                    output = func(**call["arguments"])
                    result = output if isinstance(output, str) else json.dumps(output)
                except Exception as exc:  # the model sees tool errors and can recover
                    result = f"Error: {type(exc).__name__}: {exc}"
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    raise RuntimeError(f"no final answer after {max_steps} steps")


if __name__ == "__main__":
    import time

    from tracing import Tracer

    def search_docs(query):
        time.sleep(0.03)
        return "Refunds are paid within 5 business days."

    def get_order(order_id):
        time.sleep(0.02)
        orders = {"A1": {"id": "A1", "status": "shipped"}}
        return orders[order_id]

    script = [
        {"type": "tool_calls", "usage": {"input_tokens": 120, "output_tokens": 30}, "calls": [
            {"id": "c1", "name": "get_order", "arguments": {"order_id": "B7"}},
            {"id": "c2", "name": "search_docs", "arguments": {"query": "refund time"}}]},
        {"type": "tool_calls", "usage": {"input_tokens": 210, "output_tokens": 18}, "calls": [
            {"id": "c3", "name": "get_order", "arguments": {"order_id": "A1"}}]},
        {"type": "final", "usage": {"input_tokens": 260, "output_tokens": 40},
         "content": "Order A1 has shipped. Refunds are paid within 5 business days."},
    ]

    def fake_llm(messages):
        time.sleep(0.06)
        return script[sum(m["role"] == "assistant" for m in messages)]

    tracer = Tracer()
    answer = run_traced_agent(tracer, fake_llm, {"search_docs": search_docs, "get_order": get_order},
                              "Where is my order, and how long do refunds take?")
    print(answer)
    print(tracer.export("traces.jsonl"), "spans written to traces.jsonl")
''',
    },
    "solution_files": {
        "tracing.py": r'''
"""A small tracer: nested spans with timings, status and attributes, exported as JSON Lines."""

import contextlib
import contextvars
import functools
import inspect
import json
import secrets
import time

MAX_TEXT = 300
PLAIN = (str, int, float, bool, type(None))


class Span:
    """One unit of work: a name, a start and end time, a status and some attributes."""

    def __init__(self, name, trace_id, span_id, parent_id, start):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.start = start
        self.end = None
        self.status = "ok"
        self.attributes = {}

    def set(self, key, value):
        if not isinstance(value, PLAIN):
            value = str(value)
        if isinstance(value, str):
            value = value[:MAX_TEXT]
        self.attributes[key] = value

    def fail(self, message):
        self.status = "error"
        self.set("error", message)

    def to_dict(self):
        return {"name": self.name, "trace_id": self.trace_id, "span_id": self.span_id,
                "parent_id": self.parent_id, "start": self.start, "end": self.end,
                "duration_ms": round((self.end - self.start) * 1000, 3), "status": self.status,
                "attributes": dict(self.attributes)}


class Tracer:
    def __init__(self, clock=time.perf_counter, new_id=None):
        self._clock = clock
        self._new_id = new_id or (lambda: secrets.token_hex(8))
        self._open = contextvars.ContextVar(f"open_span_{id(self)}", default=None)
        self._finished = []

    @contextlib.contextmanager
    def span(self, name, **attributes):
        parent = self._open.get()
        span_id = self._new_id()
        span = Span(name, parent.trace_id if parent else span_id, span_id,
                    parent.span_id if parent else None, self._clock())
        for key, value in attributes.items():
            span.set(key, value)
        token = self._open.set(span)
        try:
            yield span
        except BaseException as exc:
            span.fail(f"{type(exc).__name__}: {exc}")
            raise
        finally:
            self._open.reset(token)
            span.end = self._clock()
            self._finished.append(span)

    def current(self):
        return self._open.get()

    def traced(self, name=None):
        def decorate(func):
            label = name or func.__qualname__
            if inspect.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.span(label):
                        return await func(*args, **kwargs)
                return async_wrapper

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.span(label):
                    return func(*args, **kwargs)
            return wrapper
        return decorate

    @property
    def spans(self):
        return [span.to_dict() for span in self._finished]

    def export(self, path):
        rows = self.spans
        with open(path, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        return len(rows)
''',
        "traced_agent.py": r'''
"""The agent loop, instrumented: one span per run, step, model call and tool call."""

import json


def _call_tool(tracer, tools, call):
    """Run one tool call inside its span and return the text sent back to the model."""
    with tracer.span(f"tool.{call['name']}", call_id=call["id"],
                     arguments=json.dumps(call["arguments"], sort_keys=True)) as span:
        func = tools.get(call["name"])
        if func is None:
            result = f"Error: unknown tool {call['name']}"
        else:
            try:
                output = func(**call["arguments"])
                result = output if isinstance(output, str) else json.dumps(output)
            except Exception as exc:  # the model sees tool errors and can recover
                result = f"Error: {type(exc).__name__}: {exc}"
        if result.startswith("Error: "):
            span.fail(result)
        span.set("result", result)
        return result


def run_traced_agent(tracer, llm, tools, question, max_steps=5):
    with tracer.span("agent.run", question=question) as run:
        messages = [{"role": "user", "content": question}]
        tokens = {"input_tokens": 0, "output_tokens": 0}
        for step in range(1, max_steps + 1):
            with tracer.span("agent.step", step=step):
                with tracer.span("llm.call", step=step, messages=len(messages)) as call_span:
                    reply = llm(messages)
                    call_span.set("reply", reply["type"])
                    usage = reply.get("usage") or {}
                    for key in tokens:
                        call_span.set(key, usage.get(key, 0))
                        tokens[key] += usage.get(key, 0)
                if reply["type"] == "final":
                    run.set("steps", step)
                    run.set("answer", reply["content"])
                    for key, total in tokens.items():
                        run.set(key, total)
                    return reply["content"]
                messages.append({"role": "assistant", "tool_calls": reply["calls"]})
                for call in reply["calls"]:
                    result = _call_tool(tracer, tools, call)
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        raise RuntimeError(f"no final answer after {max_steps} steps")


if __name__ == "__main__":
    import time

    from tracing import Tracer

    def search_docs(query):
        time.sleep(0.03)
        return "Refunds are paid within 5 business days."

    def get_order(order_id):
        time.sleep(0.02)
        orders = {"A1": {"id": "A1", "status": "shipped"}}
        return orders[order_id]

    script = [
        {"type": "tool_calls", "usage": {"input_tokens": 120, "output_tokens": 30}, "calls": [
            {"id": "c1", "name": "get_order", "arguments": {"order_id": "B7"}},
            {"id": "c2", "name": "search_docs", "arguments": {"query": "refund time"}}]},
        {"type": "tool_calls", "usage": {"input_tokens": 210, "output_tokens": 18}, "calls": [
            {"id": "c3", "name": "get_order", "arguments": {"order_id": "A1"}}]},
        {"type": "final", "usage": {"input_tokens": 260, "output_tokens": 40},
         "content": "Order A1 has shipped. Refunds are paid within 5 business days."},
    ]

    def fake_llm(messages):
        time.sleep(0.06)
        return script[sum(m["role"] == "assistant" for m in messages)]

    tracer = Tracer()
    answer = run_traced_agent(tracer, fake_llm, {"search_docs": search_docs, "get_order": get_order},
                              "Where is my order, and how long do refunds take?")
    print(answer)
    print(tracer.export("traces.jsonl"), "spans written to traces.jsonl")
''',
    },
    "tests": r'''
import asyncio
import json
import os
import tempfile

from tracing import Span, Tracer
from traced_agent import run_traced_agent


class Clock:
    """Each read advances time by `tick` seconds, so every span has a known length."""

    def __init__(self, tick=0.5):
        self.now, self.tick = 100.0, tick

    def __call__(self):
        self.now += self.tick
        return self.now


def ids():
    counter = iter(range(1, 10_000))
    return lambda: f"s{next(counter)}"


def make_tracer():
    return Tracer(clock=Clock(), new_id=ids())


def by_name(tracer):
    out = {}
    for s in tracer.spans:
        out.setdefault(s["name"], []).append(s)
    return out


def test_single_span_fields():
    tracer = make_tracer()
    with tracer.span("work", user="ana", size=3) as span:
        assert isinstance(span, Span), "span() should yield a Span"
        assert tracer.current() is span, "current() should return the open span"
        span.set("done", True)
    assert tracer.current() is None, "current() should be None once the span has closed"
    got = tracer.spans
    assert len(got) == 1, f"expected 1 finished span, got {got!r}"
    expected = {"name": "work", "trace_id": "s1", "span_id": "s1", "parent_id": None,
                "start": 100.5, "end": 101.0, "duration_ms": 500.0, "status": "ok",
                "attributes": {"user": "ana", "size": 3, "done": True}}
    assert got[0] == expected, f"got {got[0]!r}"


def test_nesting_parents_and_finish_order():
    tracer = make_tracer()
    with tracer.span("root") as root:
        with tracer.span("child") as child:
            with tracer.span("grandchild"):
                assert tracer.current().parent_id == child.span_id
            assert tracer.current() is child, "after a nested span closes, its parent is current again"
        with tracer.span("second"):
            pass
        assert tracer.current() is root
    names = [s["name"] for s in tracer.spans]
    assert names == ["grandchild", "child", "second", "root"], f"finish order: {names}"
    spans = {s["name"]: s for s in tracer.spans}
    assert spans["child"]["parent_id"] == spans["root"]["span_id"]
    assert spans["grandchild"]["parent_id"] == spans["child"]["span_id"]
    assert spans["second"]["parent_id"] == spans["root"]["span_id"]
    assert {s["trace_id"] for s in tracer.spans} == {spans["root"]["span_id"]}, "children inherit the root's trace_id"


def test_two_roots_are_two_traces():
    tracer = make_tracer()
    with tracer.span("first"):
        pass
    with tracer.span("second"):
        pass
    first, second = tracer.spans
    assert second["parent_id"] is None, "a span opened after the first one closed is a new root"
    assert first["trace_id"] != second["trace_id"]


def test_errors_are_recorded_and_re_raised():
    tracer = make_tracer()
    try:
        with tracer.span("outer"):
            with tracer.span("lookup"):
                {}["B7"]
    except KeyError:
        pass
    else:
        raise AssertionError("the KeyError must keep propagating out of the span")
    spans = {s["name"]: s for s in tracer.spans}
    assert len(spans) == 2, "both spans must still be recorded when the block raises"
    for name in ("lookup", "outer"):
        assert spans[name]["status"] == "error", f"{name}: {spans[name]!r}"
        assert spans[name]["attributes"]["error"] == "KeyError: 'B7'", f"{name}: {spans[name]['attributes']!r}"
    assert spans["lookup"]["end"] is not None and tracer.current() is None


def test_fail_and_attribute_values():
    tracer = make_tracer()
    with tracer.span("tool") as span:
        span.set("long", "x" * 1000)
        span.set("items", [1, 2])
        span.set("nothing", None)
        span.set("ratio", 0.5)
        span.fail("Error: timeout")
    s = tracer.spans[0]
    assert s["status"] == "error" and s["attributes"]["error"] == "Error: timeout", f"got {s!r}"
    assert s["attributes"]["long"] == "x" * 300, "strings are cut to 300 characters"
    assert s["attributes"]["items"] == "[1, 2]", "non-JSON values are stored as str(value)"
    assert s["attributes"]["nothing"] is None and s["attributes"]["ratio"] == 0.5
    s["attributes"]["changed"] = 1
    assert "changed" not in tracer.spans[0]["attributes"], "to_dict() should copy the attributes"


def test_traced_decorator_sync():
    tracer = make_tracer()

    @tracer.traced()
    def add(a, b):
        """Add two numbers."""
        return a + b

    @tracer.traced("custom")
    def boom():
        raise ValueError("bad")

    assert add(2, 3) == 5
    assert add.__name__ == "add" and add.__doc__ == "Add two numbers.", "use functools.wraps"
    try:
        boom()
    except ValueError:
        pass
    else:
        raise AssertionError("errors must propagate through the decorator")
    names = [s["name"] for s in tracer.spans]
    assert names[0].endswith("add") and names[1] == "custom", f"names: {names}"
    assert tracer.spans[1]["attributes"]["error"] == "ValueError: bad"


def test_traced_decorator_async_covers_awaited_work():
    tracer = make_tracer()

    @tracer.traced("fetch")
    async def fetch(x):
        with tracer.span("inner"):
            await asyncio.sleep(0)
        return x * 2

    assert asyncio.run(fetch(4)) == 8, "the decorated coroutine should still return its value"
    spans = {s["name"]: s for s in tracer.spans}
    assert set(spans) == {"inner", "fetch"}, f"got {list(spans)}"
    assert spans["inner"]["parent_id"] == spans["fetch"]["span_id"], \
        "the async span must be open while the coroutine runs, so 'inner' is its child"


def test_concurrent_tasks_get_their_own_parents():
    tracer = Tracer(new_id=ids())

    async def task(name):
        with tracer.span(name):
            await asyncio.sleep(0.01)
            with tracer.span(name + ".child"):
                await asyncio.sleep(0.01)

    async def main():
        with tracer.span("batch"):
            await asyncio.gather(task("a"), task("b"))

    asyncio.run(main())
    spans = {s["name"]: s for s in tracer.spans}
    assert spans["a"]["parent_id"] == spans["batch"]["span_id"]
    assert spans["b"]["parent_id"] == spans["batch"]["span_id"]
    assert spans["a.child"]["parent_id"] == spans["a"]["span_id"], "use a contextvars.ContextVar for the open span"
    assert spans["b.child"]["parent_id"] == spans["b"]["span_id"], "use a contextvars.ContextVar for the open span"


def test_export_jsonl():
    tracer = make_tracer()
    with tracer.span("a"):
        with tracer.span("b"):
            pass
    path = os.path.join(tempfile.mkdtemp(), "traces.jsonl")
    assert tracer.export(path) == 2, "export() returns how many spans it wrote"
    with open(path, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert rows == tracer.spans, f"got {rows!r}"


def test_default_ids_are_random_hex():
    tracer = Tracer()
    with tracer.span("x"):
        pass
    sid = tracer.spans[0]["span_id"]
    assert isinstance(sid, str) and len(sid) == 16 and int(sid, 16) >= 0, f"default ids are secrets.token_hex(8), got {sid!r}"


def scripted(replies):
    log = []

    def llm(messages):
        log.append(len(messages))
        return replies[len(log) - 1]
    return llm, log


def tools():
    def get_order(order_id):
        return {"A1": {"status": "shipped"}}[order_id]

    def search_docs(query):
        return "Refunds take 5 days."
    return {"get_order": get_order, "search_docs": search_docs}


REPLIES = [
    {"type": "tool_calls", "usage": {"input_tokens": 100, "output_tokens": 20}, "calls": [
        {"id": "c1", "name": "get_order", "arguments": {"order_id": "B7"}},
        {"id": "c2", "name": "search_docs", "arguments": {"query": "refunds"}}]},
    {"type": "tool_calls", "calls": [{"id": "c3", "name": "teleport", "arguments": {}}]},
    {"type": "final", "content": "Refunds take 5 days.", "usage": {"input_tokens": 150, "output_tokens": 10}},
]


def test_agent_behaviour_is_unchanged():
    llm, log = scripted(REPLIES)
    tracer = make_tracer()
    assert run_traced_agent(tracer, llm, tools(), "refunds?") == "Refunds take 5 days."
    assert log == [1, 4, 6], f"the model should see the same messages as before, got lengths {log}"


def test_agent_span_tree():
    llm, _ = scripted(REPLIES)
    tracer = make_tracer()
    run_traced_agent(tracer, llm, tools(), "refunds?")
    spans = by_name(tracer)
    assert set(spans) == {"agent.run", "agent.step", "llm.call", "tool.get_order", "tool.search_docs", "tool.teleport"}, \
        f"span names: {sorted(spans)}"
    run = spans["agent.run"][0]
    assert run["parent_id"] is None
    steps = spans["agent.step"]
    assert [s["attributes"]["step"] for s in steps] == [1, 2, 3], f"steps: {[s['attributes'] for s in steps]}"
    assert all(s["parent_id"] == run["span_id"] for s in steps), "agent.step spans are children of agent.run"
    step_ids = [s["span_id"] for s in steps]
    calls = spans["llm.call"]
    assert [c["parent_id"] for c in calls] == step_ids, "each llm.call is a child of its own agent.step"
    assert spans["tool.get_order"][0]["parent_id"] == step_ids[0]
    assert spans["tool.search_docs"][0]["parent_id"] == step_ids[0]
    assert spans["tool.teleport"][0]["parent_id"] == step_ids[1]
    assert len({s["trace_id"] for s in tracer.spans}) == 1, "one run is one trace"


def test_agent_attributes():
    llm, _ = scripted(REPLIES)
    tracer = make_tracer()
    run_traced_agent(tracer, llm, tools(), "refunds?")
    spans = by_name(tracer)
    run = spans["agent.run"][0]["attributes"]
    assert run == {"question": "refunds?", "steps": 3, "answer": "Refunds take 5 days.",
                   "input_tokens": 250, "output_tokens": 30}, f"agent.run attributes: {run!r}"
    calls = [c["attributes"] for c in spans["llm.call"]]
    assert calls[0] == {"step": 1, "messages": 1, "reply": "tool_calls", "input_tokens": 100, "output_tokens": 20}, \
        f"first llm.call: {calls[0]!r}"
    assert calls[1]["messages"] == 4 and calls[1]["input_tokens"] == 0 and calls[1]["output_tokens"] == 0, \
        f"missing usage counts as 0 tokens: {calls[1]!r}"
    assert calls[2]["reply"] == "final"
    search = spans["tool.search_docs"][0]
    assert search["status"] == "ok"
    assert search["attributes"] == {"call_id": "c2", "arguments": '{"query": "refunds"}',
                                    "result": "Refunds take 5 days."}, f"got {search['attributes']!r}"


def test_tool_failures_mark_the_span():
    llm, _ = scripted(REPLIES)
    tracer = make_tracer()
    run_traced_agent(tracer, llm, tools(), "refunds?")
    spans = by_name(tracer)
    order = spans["tool.get_order"][0]
    assert order["status"] == "error", f"a tool that raised should have an error span: {order!r}"
    assert order["attributes"]["error"] == "Error: KeyError: 'B7'" == order["attributes"]["result"], f"got {order['attributes']!r}"
    unknown = spans["tool.teleport"][0]
    assert unknown["status"] == "error" and unknown["attributes"]["error"] == "Error: unknown tool teleport", f"got {unknown!r}"
    assert spans["agent.run"][0]["status"] == "ok", "the run itself recovered, so its span is ok"


def test_step_limit_marks_the_root_as_failed():
    loop = {"type": "tool_calls", "calls": [{"id": "c", "name": "search_docs", "arguments": {"query": "q"}}]}
    llm, log = scripted([loop] * 5)
    tracer = make_tracer()
    try:
        run_traced_agent(tracer, llm, tools(), "loop", max_steps=2)
    except RuntimeError:
        pass
    else:
        raise AssertionError("hitting the step limit should still raise RuntimeError")
    assert len(log) == 2
    run = by_name(tracer)["agent.run"][0]
    assert run["status"] == "error" and run["attributes"]["error"].startswith("RuntimeError:"), f"got {run!r}"
    assert len(by_name(tracer)["agent.step"]) == 2
''',
}
