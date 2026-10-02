TOPIC = {
    "id": "observability",
    "title": "Observability: Logs, Traces & Costs",
    "track": "evals",
    "order": 2,
    "requires": ["evals"],
    "summary": """
        Seeing what your AI app does in production: the logging module and levels, structured
        JSON logs, timing with an injected clock, spans and traces, latency percentiles, token
        cost accounting and redacting secrets.
    """,
    "concepts": ["logging module", "log levels", "structured logs", "logging.Formatter",
                 "time.perf_counter", "injected clock", "context manager", "__enter__/__exit__",
                 "span", "trace", "p50/p95 latency", "token cost", "redaction"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["logging", "log", "level", "getlogger", "basicconfig", "structured log",
                 "perf_counter", "clock", "latency", "span", "trace", "percentile", "p95",
                 "cost", "redact", "context manager"],
    "cards": [
        {
            "syntax": "log = logging.getLogger(name)  /  log.info(msg)",
            "explain": "Writes log messages. A message is written only when its level is at or above the configured level.",
            "example": r'''
                import logging, sys

                logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                    format="%(levelname)s %(name)s %(message)s")
                log = logging.getLogger("rag")
                log.debug("query embedded")
                log.info("retrieved %s chunks", 3)
                # INFO rag retrieved 3 chunks
            ''',
        },
        {
            "syntax": 'json.dumps({"event": event, **fields}, sort_keys=True)',
            "explain": "A structured log line: one JSON object with a key for every value, keys in alphabetical order.",
            "example": r'''
                import json

                fields = {"model": "small", "latency_ms": 250.0}
                print(json.dumps({"event": "llm_call", **fields}, sort_keys=True))
                # {"event": "llm_call", "latency_ms": 250.0, "model": "small"}
            ''',
        },
        {
            "syntax": "elapsed_ms = (clock() - start) * 1000",
            "explain": "Elapsed time: the later clock reading minus the earlier one. Pass the clock in so a test can use a fake one.",
            "example": r'''
                readings = iter([10.0, 10.25])

                def clock():
                    return next(readings)

                start = clock()
                print((clock() - start) * 1000)
                # 250.0
            ''',
        },
        {
            "syntax": "def __exit__(self, exc_type, exc, tb):",
            "explain": "A context manager has __enter__ and __exit__. with calls __exit__ when its block ends. exc_type is None when no exception was raised.",
            "example": r'''
                class Step:
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        print("exit", exc_type is None)
                with Step():
                    pass
                # exit True
            ''',
        },
        {
            "syntax": "ordered[max(1, math.ceil(p * n / 100)) - 1]",
            "explain": "Nearest-rank percentile of n sorted values. p50 is the median. p95 measures the slow requests.",
            "example": r'''
                import math

                ordered = sorted([120, 80, 950, 100, 110])
                for p in (50, 95):
                    rank = max(1, math.ceil(p * len(ordered) / 100))
                    print(p, rank, ordered[rank - 1])
                # 50 3 110
                # 95 5 950
            ''',
        },
        {
            "syntax": "tokens * price / 1_000_000",
            "explain": "Token cost. Prices are in dollars per million tokens, with one price for input and one for output.",
            "example": r'''
                cost = 1200 * 2.50 / 1_000_000 + 300 * 10.00 / 1_000_000
                print(round(cost, 6))
                # 0.006
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: observability

**Observability** is the ability to find out what a running program did from the data it
recorded: what happened, how long it took and what it cost.

### Logging and levels

The `logging` module writes messages called **log records**. Each record has a **level**: an
integer that says how serious the message is. The levels are `DEBUG` 10, `INFO` 20,
`WARNING` 30, `ERROR` 40 and `CRITICAL` 50.

```python
import logging, sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("rag")
log.debug("query embedded")
log.info("retrieved %s chunks", 3)
# INFO rag retrieved 3 chunks
log.error("model call failed")
# ERROR rag model call failed
```

A **logger** is an object whose methods (`debug`, `info`, `warning`, `error`, `critical`)
create log records. `getLogger("rag")` returns a logger named `rag`. The **root logger** is
the one logger that receives the records of every other logger and writes them.
`basicConfig` configures the root logger once: where the output goes, the level and the
line format.

In the `format` string, `%(levelname)s` is replaced by the level name, `%(name)s` by the
logger name and `%(message)s` by the message. In a message, `%s` is replaced by the next
argument, so `"retrieved %s chunks"` with `3` becomes `retrieved 3 chunks`.

A record is written only when its level is at or above the configured level, so the
`debug` call prints nothing.

### Structured logs

A **structured log** is one JSON object per line. A tool can then filter the lines by
`event`, `model` or `latency_ms`. **Latency** is the time one request takes. `latency_ms` is
that time in milliseconds (thousandths of a second).

```python
import json

record = {"event": "llm_call", "model": "gpt-4o", "latency_ms": 812, "cost_usd": 0.006}
line = json.dumps(record, sort_keys=True)
print(line)
# {"cost_usd": 0.006, "event": "llm_call", "latency_ms": 812, "model": "gpt-4o"}
print(json.loads(line)["latency_ms"])
# 812
```

To make `logging` write JSON, subclass `logging.Formatter` and define `format(self, record)`,
which returns the text for one record. `record.getMessage()` is the finished message,
`record.levelname` the level name and `record.name` the logger name.

### Timing with an injected clock

`time.perf_counter()` returns a float number of seconds. Only the difference between two
readings has a meaning: `elapsed = end - start`. Real readings differ on every run, so code
you want to test takes the clock as a parameter. Passing the clock in as an argument is
called **injecting** it. A test injects a fake clock that returns fixed numbers.

```python
def timed(fn, clock):
    start = clock()
    result = fn()
    return result, (clock() - start) * 1000

readings = iter([10.0, 10.25])
print(timed(lambda: "hi", lambda: next(readings)))
# ('hi', 250.0)
```

`iter(list)` creates an iterator, which hands out the list items one at a time. Each
`next(readings)` call returns the next item, so the fake clock returns `10.0` and then `10.25`.

### Context managers

A **context manager** is an object with `__enter__` and `__exit__` methods. `with X as y:`
calls `X.__enter__()` and assigns its return value to `y`. Then the block runs. Then Python
calls `X.__exit__(exc_type, exc, tb)`, also when the block raised an exception. The three
arguments are the exception's type, the exception itself and its traceback (the record of
the lines that were running). They are all `None` when there was no exception. Returning `False` lets an exception continue.

```python
class Step:
    def __enter__(self):
        print("enter")
        return "value"
    def __exit__(self, exc_type, exc, tb):
        print("exit", exc_type)
        return False

with Step() as s:
    print(s)
# enter
# value
# exit None
```

### Spans and traces

A **span** is one timed step of a request, such as `retrieve` or `llm_call`. It has a name,
a duration and a status. A span opened inside another span is its child, and the outer span
is its **parent**. All the spans of one request form a **trace**. OpenTelemetry is a
widely used open standard and library for spans.

### Latency percentiles

A **percentile** is a value that a given percentage of the values are at or below. The
**p95** latency is a value that 95% of requests were at or below. The **p50** latency is
the **median**: half of the requests were at or below it.

The nearest-rank method sorts the values and computes `rank = ceil(p * n / 100)`, where `n`
is the number of values. `math.ceil` rounds a number up to the next whole number. The rank is
at least 1. The answer is `ordered[rank - 1]`, because rank 1 is index 0.

```python
import math

latencies = [120, 80, 950, 100, 110]
ordered = sorted(latencies)
for p in (50, 95):
    rank = max(1, math.ceil(p * len(ordered) / 100))
    print(p, rank, ordered[rank - 1])
# 50 3 110
# 95 5 950
print(sum(latencies) / len(latencies))
# 272.0
```

There are 5 values. For p50, `50 * 5 / 100` is 2.5, which rounds up to rank 3, and the third
sorted value is 110. For p95, `95 * 5 / 100` is 4.75, which rounds up to rank 5, and the
fifth sorted value is 950.

The **mean** is the sum divided by the count: `1360 / 5`, which is 272.0. Four of the five
requests took 120 ms or less, so the mean describes none of them. Report p50 and p95.

### One traced request

Prices are quoted per million tokens, with separate prices for input and output tokens.
This program times one call, computes its cost and prints one structured log line.

```python
import json

readings = iter([10.0, 10.25])

def clock():
    return next(readings)

def fake_llm(prompt):
    return {"text": "Hi!", "input_tokens": 1200, "output_tokens": 300}

start = clock()
reply = fake_llm("hello")
latency_ms = (clock() - start) * 1000
cost = reply["input_tokens"] * 2.50 / 1_000_000 + reply["output_tokens"] * 10.00 / 1_000_000
record = {"event": "llm_call", "model": "gpt-4o", "latency_ms": latency_ms,
          "input_tokens": reply["input_tokens"],
          "output_tokens": reply["output_tokens"], "cost_usd": round(cost, 6)}
print(json.dumps(record, sort_keys=True))
# {"cost_usd": 0.006, "event": "llm_call", "input_tokens": 1200, "latency_ms": 250.0, "model": "gpt-4o", "output_tokens": 300}
```

Step through the stages to see the data each one produces.

```diagram
{"type":"flow","title":"One traced LLM request","steps":[
{"label":"Start timer","detail":"The program reads the clock before the call and stores the reading in start.","code":"start = clock()\nstart: 10.0"},
{"label":"Call the model","detail":"The program calls the model. The reply is a dict with the text and the token counts.","code":"reply = fake_llm(\"hello\")\nreply: {'text': 'Hi!', 'input_tokens': 1200, 'output_tokens': 300}"},
{"label":"Record latency","detail":"The program reads the clock again. The difference between the two readings, times 1000, is the latency in milliseconds.","code":"latency_ms = (clock() - start) * 1000\n(10.25 - 10.0) * 1000 = 250.0"},
{"label":"Compute cost","detail":"Each token count is multiplied by its price and divided by one million. The two parts are added.","code":"1200 * 2.50 / 1_000_000 = 0.003\n300 * 10.00 / 1_000_000 = 0.003\ncost: 0.006"},
{"label":"Build the record","detail":"The program puts every measurement into one dict. Each value has a key.","code":"record = {'event': 'llm_call', 'model': 'gpt-4o', 'latency_ms': 250.0,\n          'input_tokens': 1200, 'output_tokens': 300, 'cost_usd': 0.006}"},
{"label":"Write the log line","detail":"json.dumps turns the dict into one line of JSON text with sorted keys.","code":"{\"cost_usd\": 0.006, \"event\": \"llm_call\", \"input_tokens\": 1200, \"latency_ms\": 250.0, \"model\": \"gpt-4o\", \"output_tokens\": 300}"}
]}
```

### Redaction

To **redact** a value is to replace it with a placeholder before it is logged. Logs are
copied to dashboards and bug reports, so an API key in a log is a leaked key.

```python
import re

prompt = "summarise this, key sk-abc123XYZ789"
print(re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", prompt))
# summarise this, key [REDACTED]
headers = {"Authorization": "Bearer sk-abc123XYZ789", "model": "gpt-4o"}
safe = {k: ("***" if k.lower() == "authorization" else v) for k, v in headers.items()}
print(safe)
# {'Authorization': '***', 'model': 'gpt-4o'}
```

The comprehension builds a new dict. `headers` still holds the real key for the request.

### Common mistakes

- `(start - end) * 1000` gives a negative latency. Subtract the earlier reading from the later one.
- Forgetting `/ 1_000_000` makes every cost a million times too high.
- Returning `True` from `__exit__` makes Python discard the exception, so the failure is hidden.
- A rank of 0 gives `ordered[-1]`, which is the largest value. Use `max(1, rank)`.
- `record.msg` is the template with `%s` still in it. Use `record.getMessage()`.
- `data[key] = "***"` changes the caller's dict. Build a new dict for the log.
'''

EXERCISES = [
    {
        "id": "observability-s1",
        "title": "Which log lines show up?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Logging and levels

            An app on a server runs with nobody reading its output. A **log** is a record of
            what the program did, which you read later to find out what went wrong. Python
            writes logs with the `logging` module.

            ```python
            import logging, sys

            logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                format="%(levelname)s %(message)s")
            log = logging.getLogger("chat")
            log.debug("prompt has 42 tokens")
            log.info("request received")
            # INFO request received
            log.warning("retrying after 429")
            # WARNING retrying after 429
            ```

            A **logger** is an object whose methods write log messages. `getLogger("chat")`
            returns a logger named `chat`. The **root logger** is the one logger that
            receives the messages of every other logger and writes them. `basicConfig`
            configures the root logger once: where the output goes, the level and the line
            format.

            `stream=sys.stdout` sends the lines to the normal program output. In the
            `format` string, `%(levelname)s` is replaced by the level name and
            `%(message)s` by the message.

            Every message has a **level** that says how serious it is. From least to most
            serious the levels are `debug` (details for developers), `info` (normal events),
            `warning` (something unexpected), `error` (something failed) and `critical`.

            The configured level is a threshold. A message is written only when its level is
            the configured level or a more serious one. The example sets `logging.INFO`, so
            the `debug` call prints nothing.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            import logging
            import sys

            logging.basicConfig(stream=sys.stdout, level=logging.WARNING,
                                format="%(levelname)s %(message)s")
            log = logging.getLogger("rag")
            log.debug("query embedded")
            log.info("3 chunks retrieved")
            log.warning("slow response: 2.4s")
            log.error("model call failed")
        ''',
        "solution": r'''
            WARNING slow response: 2.4s
            ERROR model call failed
        ''',
        "explanation": r'''
            The level is `WARNING`, so only records at WARNING or above are shown. `debug` and
            `info` are below the threshold and silently dropped. The format string prints the
            level name, a space, then the message.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The configured level is a threshold: only messages at that level or more serious appear.",
            "The order from least to most serious is debug, info, warning, error, critical.",
            "Drop the debug and info lines; print the other two as 'LEVELNAME message'.",
        ],
    },
    {
        "id": "observability-s2",
        "title": "Levels are numbers",
        "difficulty": 0,
        "lesson": r'''
            ## Levels are integers

            Each log level is an integer. The `logging` module stores them in named constants.

            ```python
            import logging

            print(logging.DEBUG, logging.INFO, logging.WARNING)
            # 10 20 30
            print(logging.ERROR, logging.CRITICAL)
            # 40 50
            print(logging.ERROR > logging.WARNING)
            # True
            print(logging.getLevelName(30))
            # WARNING
            ```

            A larger number means a more serious message. To decide whether to write a
            message, `logging` compares its level number with the configured level number.

            A function can return a level. This one picks a level from a token count.

            ```python
            import logging

            def level_for_tokens(tokens, limit):
                if tokens > limit:
                    return logging.WARNING
                return logging.DEBUG

            print(level_for_tokens(9000, 8000))
            # 30
            print(level_for_tokens(500, 8000))
            # 10
            ```

            A common rule for API calls: a status of 500 or above is a server error and gets
            `ERROR`. A status from 400 to 499 gets `WARNING`. Everything else gets `INFO`.

            Write the constant `logging.ERROR`, not the number `40`. The name states the
            meaning.
        ''',
        "prompt": r'''
            Pick the log level for an HTTP response from a model provider. Replace each `___`.

            **Write:** `level_for_status(status)`

            - `status`: an int HTTP status code, e.g. `200`, `429`, `503`
            - **Returns:** a logging level constant (an int)

            **Rules**
            - `500` and above: `logging.ERROR`
            - `400` to `499`: `logging.WARNING`
            - anything below `400`: `logging.INFO`

            **Examples**
            ```python
            level_for_status(503)   # returns logging.ERROR (40)
            level_for_status(429)   # returns logging.WARNING (30)
            level_for_status(200)   # returns logging.INFO (20)
            ```
        ''',
        "starter": r'''
            import logging

            def level_for_status(status):
                if status >= 500:
                    return ___
                if status >= 400:
                    return logging.WARNING
                return ___
        ''',
        "tests": r'''
            import logging
            from solution import level_for_status

            def test_server_errors_are_error():
                assert level_for_status(503) == logging.ERROR, f"got {level_for_status(503)!r}"
                assert level_for_status(500) == logging.ERROR, f"got {level_for_status(500)!r}"

            def test_client_errors_are_warning():
                assert level_for_status(429) == logging.WARNING, f"got {level_for_status(429)!r}"

            def test_success_is_info():
                assert level_for_status(200) == logging.INFO, f"got {level_for_status(200)!r}"
                assert level_for_status(399) == logging.INFO, f"got {level_for_status(399)!r}"
        ''',
        "solution": r'''
            import logging

            def level_for_status(status):
                if status >= 500:
                    return logging.ERROR
                if status >= 400:
                    return logging.WARNING
                return logging.INFO
        ''',
        "hints": [
            "The middle branch already shows the pattern: return a constant from the logging module.",
            "The first blank is the level for broken servers; the last one is for normal events.",
            "Replace the first ___ with logging.ERROR and the second with logging.INFO.",
        ],
    },
    {
        "id": "observability-s3",
        "title": "A structured log line",
        "difficulty": 0,
        "lesson": r'''
            ## Structured logs

            A log line such as `"Called gpt-4o, took 812ms"` is free text. To find every slow
            call, a program would have to parse each sentence with a regex.

            A **structured log** is one JSON object per line. Every value has a key, so a
            tool can filter and chart the lines by key.

            ```python
            import json

            fields = {"model": "gpt-4o", "latency_ms": 812}
            record = {"event": "llm_call", **fields}
            line = json.dumps(record, sort_keys=True)
            print(line)
            # {"event": "llm_call", "latency_ms": 812, "model": "gpt-4o"}
            print(json.loads(line)["latency_ms"])
            # 812
            print(fields)
            # {'model': 'gpt-4o', 'latency_ms': 812}
            ```

            `{"event": "llm_call", **fields}` creates a new dict. It holds the `event` key
            and a copy of every key and value in `fields`. `fields` itself is unchanged, as
            the last line shows.

            `sort_keys=True` writes the keys in alphabetical order. The same data then
            always produces the same line.

            Click a key to read its value from `record`.

            ```diagram
            {"type":"dict","title":"The record dict before json.dumps","name":"record","entries":[["event","llm_call"],["model","gpt-4o"],["latency_ms",812]]}
            ```

            `fields["event"] = "llm_call"` would add the key to the caller's dict. Build a
            new dict.
        ''',
        "prompt": r'''
            Build one structured (JSON) log line.

            **Write:** `log_line(event, fields)`

            - `event`: a string, the event name, e.g. `"llm_call"`
            - `fields`: a dict of extra data, e.g. `{"model": "gpt-4o", "tokens": 120}`
            - **Returns:** a JSON string of one object holding `"event"` plus all of `fields`

            **Rules**
            - Keys are sorted (`json.dumps(..., sort_keys=True)`), default spacing.
            - Don't modify `fields`.

            **Examples**
            ```python
            log_line("llm_call", {"model": "gpt-4o", "tokens": 120})
            # returns '{"event": "llm_call", "model": "gpt-4o", "tokens": 120}'
            log_line("start", {})
            # returns '{"event": "start"}'
            ```
        ''',
        "starter": r'''
            import json

            def log_line(event, fields):
                ...
        ''',
        "tests": r'''
            from solution import log_line

            def test_event_and_fields_sorted():
                got = log_line("llm_call", {"tokens": 120, "model": "gpt-4o"})
                assert got == '{"event": "llm_call", "model": "gpt-4o", "tokens": 120}', f"got {got!r}"

            def test_no_fields():
                got = log_line("start", {})
                assert got == '{"event": "start"}', f"got {got!r}"

            def test_fields_not_modified():
                fields = {"model": "claude"}
                log_line("x", fields)
                assert fields == {"model": "claude"}, f"fields became {fields!r}"
        ''',
        "solution": r'''
            import json

            def log_line(event, fields):
                return json.dumps({"event": event, **fields}, sort_keys=True)
        ''',
        "hints": [
            "Make a new dict with the event plus the fields, then turn it into JSON text.",
            "Dict unpacking {**fields} copies fields into a new dict; json.dumps has a sort_keys option.",
            "Return json.dumps({'event': event, **fields}, sort_keys=True).",
        ],
    },
    {
        "id": "observability-s4",
        "title": "Fix: negative latency",
        "difficulty": 0,
        "lesson": r'''
            ## Timing with an injected clock

            To time a piece of code, read a clock before it and after it.
            `time.perf_counter()` returns a float number of seconds from a clock that can
            measure very short times. One reading on its own has no meaning. The **difference** between two
            readings is the elapsed time in seconds.

            ```python
            import time

            start = time.perf_counter()
            total = sum(range(100_000))
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(elapsed_ms > 0)
            # True
            ```

            A real clock gives different numbers on every run, so a test cannot check an
            exact value. The fix is to take the clock as a **parameter**. Production code
            passes `time.perf_counter`. A test passes a fake clock: a function that returns
            numbers you chose. Passing the clock in as an argument is called **injecting**
            it. You injected a fake model the same way in the RAG chapter.

            ```python
            readings = iter([10.0, 10.25])

            def fake_clock():
                return next(readings)

            a = fake_clock()
            b = fake_clock()
            print((b - a) * 1000)
            # 250.0
            print((a - b) * 1000)
            # -250.0
            ```

            `iter(list)` creates an iterator: an object that hands out the items of the list one
            at a time. `next(iterator)` returns the next item. Each call to `fake_clock()` therefore
            returns the next number from `readings`. The later
            reading minus the earlier reading is positive. The other order gives a negative
            number.
        ''',
        "prompt": r'''
            `timed_call` should run a function and report how long it took, but the latency
            comes out negative. Fix the bug.

            **Write:** `timed_call(fn, clock)`

            - `fn`: a function with no arguments; its return value is the result
            - `clock`: a function with no arguments returning the current time in seconds (float)
            - **Returns:** a tuple `(result, elapsed_ms)`: what `fn()` returned, and the time
              between the clock reading before and after the call, in milliseconds

            **Rules**
            - Read `clock()` exactly once before calling `fn`, and once after.
            - `elapsed_ms` = (after - before) * 1000.

            **Examples**
            ```python
            readings = iter([10.0, 10.25])
            timed_call(lambda: "hi", lambda: next(readings))   # returns ("hi", 250.0)
            ```
        ''',
        "starter": r'''
            def timed_call(fn, clock):
                start = clock()
                result = fn()
                end = clock()
                return result, (start - end) * 1000
        ''',
        "tests": r'''
            from solution import timed_call

            def fake_clock(*values):
                it = iter(values)
                return lambda: next(it)

            def test_quarter_second_is_250_ms():
                got = timed_call(lambda: "hi", fake_clock(10.0, 10.25))
                assert tuple(got) == ("hi", 250.0), f"got {got!r}"

            def test_result_is_passed_through():
                got = timed_call(lambda: [1, 2], fake_clock(0.0, 2.0))
                assert tuple(got) == ([1, 2], 2000.0), f"got {got!r}"

            def test_clock_read_before_and_after_call():
                events = []
                values = iter([1.0, 1.5])
                def clock():
                    events.append("clock")
                    return next(values)
                def fn():
                    events.append("fn")
                timed_call(fn, clock)
                assert events == ["clock", "fn", "clock"], f"order was {events!r}"
        ''',
        "solution": r'''
            def timed_call(fn, clock):
                start = clock()
                result = fn()
                end = clock()
                return result, (end - start) * 1000
        ''',
        "hints": [
            "Look at the subtraction on the last line. Which reading is the bigger number?",
            "Elapsed time is the later reading minus the earlier one.",
            "Swap the two names in the subtraction: (end - start) * 1000.",
        ],
    },
    {
        "id": "observability-s5",
        "title": "What did that call cost?",
        "difficulty": 0,
        "lesson": r'''
            ## Token cost

            An LLM API charges for two token counts. **Input tokens** are the tokens you
            send. **Output tokens** are the tokens the model writes. Output tokens usually
            cost more.

            Providers quote prices **per million tokens**, for example $2.50 per million
            input tokens and $10 per million output tokens. One token costs
            `price / 1_000_000`.

            ```python
            input_tokens, output_tokens = 1200, 300
            in_price, out_price = 2.50, 10.00   # dollars per million tokens
            cost = input_tokens * in_price / 1_000_000 + output_tokens * out_price / 1_000_000
            print(cost)
            # 0.006
            print(round(cost, 6))
            # 0.006
            ```

            The input part is `1200 * 2.50 / 1_000_000`, which is 0.003. The output part is
            `300 * 10.00 / 1_000_000`, also 0.003. `round(cost, 6)` keeps 6 decimals. Float
            sums can be off by a tiny amount, and rounding removes that error.

            The cost of one request is small. At a million requests a day it is 6000 dollars
            a day, so production apps log the cost of **every** call.

            `1_000_000` is the integer `1000000`. Python ignores underscores between digits.
            Without the division, every cost is a million times too high.
        ''',
        "prompt": r'''
            Compute the dollar cost of one LLM request.

            **Write:** `request_cost(input_tokens, output_tokens, input_price, output_price)`

            - `input_tokens`, `output_tokens`: ints, e.g. `1200` and `300`
            - `input_price`, `output_price`: floats, dollars **per million** tokens, e.g. `2.5` and `10.0`
            - **Returns:** a float, the total cost in dollars, rounded to 6 decimals

            **Rules**
            - cost = input_tokens * input_price / 1,000,000 + output_tokens * output_price / 1,000,000
            - Round the total with `round(total, 6)`.

            **Examples**
            ```python
            request_cost(1200, 300, 2.5, 10.0)       # returns 0.006
            request_cost(1_000_000, 0, 3.0, 15.0)    # returns 3.0
            request_cost(0, 0, 2.5, 10.0)            # returns 0.0
            ```
        ''',
        "starter": r'''
            def request_cost(input_tokens, output_tokens, input_price, output_price):
                ...
        ''',
        "tests": r'''
            from solution import request_cost

            def test_typical_request():
                got = request_cost(1200, 300, 2.5, 10.0)
                assert got == 0.006, f"got {got!r}"

            def test_one_million_input_tokens():
                got = request_cost(1_000_000, 0, 3.0, 15.0)
                assert got == 3.0, f"got {got!r}"

            def test_output_priced_separately_and_rounded():
                got = request_cost(1, 7, 0.15, 0.6)
                assert got == 0.000004, f"got {got!r}"

            def test_zero_tokens():
                assert request_cost(0, 0, 2.5, 10.0) == 0.0
        ''',
        "solution": r'''
            def request_cost(input_tokens, output_tokens, input_price, output_price):
                total = input_tokens * input_price / 1_000_000 + output_tokens * output_price / 1_000_000
                return round(total, 6)
        ''',
        "hints": [
            "Each kind of token has its own price per million. Compute the two parts and add them.",
            "Multiply tokens by price and divide by one million, for input and for output, then round.",
            "total = input_tokens * input_price / 1_000_000 + output_tokens * output_price / 1_000_000; return round(total, 6).",
        ],
    },
    {
        "id": "observability-s6",
        "title": "Redact API keys",
        "difficulty": 0,
        "lesson": r'''
            ## Redacting API keys

            Many people and tools read logs. Logs are copied to dashboards, pasted into bug
            reports and kept for months. An API key that appears in a log is a leaked key.

            To **redact** a secret is to replace it with a placeholder before the text is
            logged. `re.sub(pattern, replacement, text)` from the regex chapter returns a
            new string with every match of the pattern replaced.

            ```python
            import re

            text = "calling with key sk-abc123XYZ789 now"
            print(re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", text))
            # calling with key [REDACTED] now
            print(re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", "sk-short stays"))
            # sk-short stays
            ```

            Many providers start their keys with a fixed prefix such as `sk-`, so a pattern
            can find them. `[A-Za-z0-9_-]` matches one letter, digit, `_` or `-`. `{8,}`
            repeats that 8 or more times. `sk-short` has only 5 such characters after the
            prefix, so it does not match and stays in the text.

            Redact **before** you log. Once a line is written, the key is already in the log.
        ''',
        "prompt": r'''
            Hide API keys in text before it is logged.

            **Write:** `redact_keys(text)`

            - `text`: a string that may contain API keys
            - **Returns:** the same text with every key replaced by `[REDACTED]`

            **Rules**
            - A key is `sk-` followed by **8 or more** characters that are letters, digits,
              `_` or `-`. The whole key (including `sk-`) is replaced.
            - Replace every key, not just the first.
            - `sk-` followed by fewer than 8 such characters is not a key: leave it.

            **Examples**
            ```python
            redact_keys("key=sk-abc123XYZ789 ok")        # returns "key=[REDACTED] ok"
            redact_keys("a sk-AAAAAAAA b sk-proj_12-34ab")   # returns "a [REDACTED] b [REDACTED]"
            redact_keys("sk-short is fine")              # returns "sk-short is fine"
            ```
        ''',
        "starter": r'''
            import re

            def redact_keys(text):
                ...
        ''',
        "tests": r'''
            from solution import redact_keys

            def test_single_key_is_replaced():
                got = redact_keys("key=sk-abc123XYZ789 ok")
                assert got == "key=[REDACTED] ok", f"got {got!r}"

            def test_every_key_is_replaced():
                got = redact_keys("a sk-AAAAAAAA b sk-proj_12-34ab")
                assert got == "a [REDACTED] b [REDACTED]", f"got {got!r}"

            def test_short_values_are_left_alone():
                got = redact_keys("sk-short is fine")
                assert got == "sk-short is fine", f"got {got!r}"

            def test_text_without_keys_unchanged():
                assert redact_keys("hello world") == "hello world"
        ''',
        "solution": r'''
            import re

            def redact_keys(text):
                return re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", text)
        ''',
        "hints": [
            "re.sub replaces every match of a pattern with a replacement string.",
            "The pattern is the literal sk- followed by a character class of letters, digits, _ and -, repeated at least 8 times.",
            "Return re.sub(r'sk-[A-Za-z0-9_-]{8,}', '[REDACTED]', text).",
        ],
    },
    {
        "id": "observability-s7",
        "title": "Context managers: enter and exit",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Context managers

            You have used `with open(...) as f:`. Python closes the file when the block
            ends. The object after `with` is a **context manager**: an object with an
            `__enter__` method and an `__exit__` method. Python calls them at the start and
            at the end of the `with` block.

            You can write your own class with these two methods:
            - `__enter__(self)` runs when the `with` block starts. Its return value is
              assigned to the name after `as`.
            - `__exit__(self, exc_type, exc, tb)` runs when the block ends. It runs
              **always**, also when the block raised an exception. The three arguments
              are the exception's type, the exception itself and its traceback (the record
              of the lines that were running). All three are `None` when there was none. Returning
              `False` tells Python to let the exception continue.

            ```python
            class Step:
                def __enter__(self):
                    print("enter")
                    return "embed"
                def __exit__(self, exc_type, exc, tb):
                    print("exit", exc_type)
                    return False

            with Step() as name:
                print(name)
            print("after")
            # enter
            # embed
            # exit None
            # after
            ```

            `Step()` creates the object. `with` calls its `__enter__`, which prints `enter`
            and returns `"embed"`. That string is assigned to `name`. The block prints it.
            Then `__exit__` prints `exit None`, because no exception was raised.

            This order suits timing: read the clock in `__enter__` and again in `__exit__`.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            class Span:
                def __init__(self, name):
                    self.name = name
                def __enter__(self):
                    print("start", self.name)
                    return self
                def __exit__(self, exc_type, exc, tb):
                    print("end", self.name, exc_type is None)
                    return False

            with Span("retrieve") as s:
                print("working in", s.name)
            print("done")
        ''',
        "solution": r'''
            start retrieve
            working in retrieve
            end retrieve True
            done
        ''',
        "explanation": r'''
            `with` calls `__enter__` first, which prints `start retrieve` and returns the `Span`
            object itself. That object is assigned to `s`. The block runs and prints
            `working in retrieve`. Then `__exit__` runs. No exception was raised, so `exc_type`
            is `None` and `exc_type is None` is `True`. Last, the line after the `with` block
            prints `done`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "A with block runs __enter__ first, then the indented body, then __exit__.",
            "__enter__ returns self, so s.name is the span's name. Without an error, exc_type is None.",
            "Four lines: start line from __enter__, the body line, the end line with True, then done.",
        ],
    },
    {
        "id": "observability-1",
        "title": "Latency percentile",
        "difficulty": 1,
        "lesson": r'''
            ## Latency percentiles

            **Latency** is the time one request takes. Most requests are fast and a few are
            very slow. The **mean** is the sum of the latencies divided by their count. One
            very slow request raises the mean a lot, so the mean describes neither the fast
            requests nor the slow ones.

            A **percentile** is a value that a given percentage of the requests were at or
            below. **p50**, also called the **median**, is the value that half of the
            requests were at or below. It is the latency of a typical request. **p95** is the
            latency that 95% of requests were at or below. It measures the slow requests.

            The **nearest-rank** method sorts the values and computes
            `rank = ceil(p * n / 100)`, where `n` is the number of values. `math.ceil` rounds
            a number up to the next whole number. The answer is the value at position
            `rank`, counting from 1.

            ```python
            import math

            latencies = [120, 80, 950, 100, 110]
            ordered = sorted(latencies)
            rank = math.ceil(95 * len(ordered) / 100)
            print(ordered, rank)
            # [80, 100, 110, 120, 950] 5
            print("p95:", ordered[rank - 1])
            # p95: 950
            print("mean:", sum(latencies) / len(latencies))
            # mean: 272.0
            ```

            `95 * 5 / 100` is 4.75 and `math.ceil` rounds it up to 5. Position 5 is index 4,
            so the code reads `ordered[rank - 1]`. For p50, `50 * 5 / 100` is 2.5, which
            rounds up to rank 3, and `ordered[2]` is 110. The mean is 272.0, which is
            larger than four of the five values.

            `sorted()` returns a new list. `latencies.sort()` would reorder the caller's
            list. For `p = 0` the rank is 0, and `ordered[0 - 1]` is `ordered[-1]`, the
            largest value. Raise the rank to at least 1.
        ''',
        "prompt": r'''
            Compute a latency percentile using the nearest-rank method.

            **Write:** `percentile(values, p)`

            - `values`: a list of numbers (latencies in ms), in any order, e.g. `[120, 80, 950, 100]`
            - `p`: a number from 0 to 100, e.g. `50` or `95`
            - **Returns:** one of the values: sort them, compute `rank = ceil(p * n / 100)`
              (where `n` is the number of values), use at least `1`, and return the value at
              position `rank` counting from 1

            **Rules**
            - An empty `values` list raises `ValueError`.
            - `p = 0` returns the smallest value; `p = 100` returns the largest.
            - Don't modify `values`.

            **Examples**
            ```python
            percentile([400, 100, 300, 200], 50)   # returns 200
            percentile([400, 100, 300, 200], 95)   # returns 400
            percentile([400, 100, 300, 200], 0)    # returns 100
            percentile([], 50)                     # raises ValueError
            ```
        ''',
        "starter": r'''
            import math

            def percentile(values, p):
                ...
        ''',
        "tests": r'''
            from solution import percentile

            V = [400, 100, 300, 200]

            def test_median():
                assert percentile(V, 50) == 200, f"got {percentile(V, 50)!r}"

            def test_p95_of_twenty_values():
                values = list(range(20, 0, -1))
                got = percentile(values, 95)
                assert got == 19, f"got {got!r}"

            def test_p0_and_p100():
                assert percentile(V, 0) == 100, f"p0 gave {percentile(V, 0)!r}"
                assert percentile(V, 100) == 400, f"p100 gave {percentile(V, 100)!r}"

            def test_input_not_modified():
                values = [3, 1, 2]
                percentile(values, 50)
                assert values == [3, 1, 2], f"values became {values!r}"

            def test_empty_raises_value_error():
                try:
                    percentile([], 50)
                except ValueError:
                    return
                raise AssertionError("percentile([], 50) should raise ValueError")
        ''',
        "solution": r'''
            import math

            def percentile(values, p):
                if not values:
                    raise ValueError("no values")
                ordered = sorted(values)
                rank = max(1, math.ceil(p * len(ordered) / 100))
                return ordered[rank - 1]
        ''',
        "hints": [
            "Sort a copy of the values with sorted(), then find the right position with math.ceil.",
            "rank = ceil(p * n / 100), but never below 1. Positions count from 1, list indexes from 0.",
            "1) Raise ValueError if values is empty. 2) ordered = sorted(values). 3) rank = max(1, math.ceil(p * len(ordered) / 100)). 4) Return ordered[rank - 1].",
        ],
    },
    {
        "id": "observability-2",
        "title": "A timing span",
        "difficulty": 1,
        "lesson": r'''
            ## Spans

            A RAG request has several steps: embed the question, retrieve chunks, call the
            model. To see which step is slow, you time each one. A **span** is a record of
            one named step and how long it took.

            A context manager fits this job. `__enter__` reads the clock when the step
            starts. `__exit__` reads it again when the step ends and stores the difference.

            ```python
            readings = iter([1.0, 1.2])
            clock = lambda: next(readings)

            class Stopwatch:
                def __enter__(self):
                    self.start = clock()
                    return self
                def __exit__(self, exc_type, exc, tb):
                    self.ms = (clock() - self.start) * 1000
                    return False

            with Stopwatch() as sw:
                pass
            print(round(sw.ms, 1))
            # 200.0
            ```

            `__enter__` returns `self`, so `sw` is the `Stopwatch` object. Its `ms`
            attribute is set in `__exit__`, so you read it after the block.

            A span also has a **status**: `"ok"` when the block finished normally and
            `"error"` when the block raised an exception. `__exit__` can tell which one
            happened: `exc_type` is `None` when no exception was raised.

            Return `False` from `__exit__`. Returning `True` makes Python discard the
            exception, and the caller never learns that the step failed.
        ''',
        "prompt": r'''
            Build a span class to time one step of a request.

            **Write:** a class `Span` used as `with Span(name, clock) as span:`

            - `Span(name, clock)`: `name` is a string; `clock` is a function returning seconds (float)
            - Attributes: `name`; `duration_ms` and `status`, both `None` until the block ends
            - `__enter__` reads `clock()` once and returns the span itself
            - `__exit__` reads `clock()` once more, sets `duration_ms` = (end - start) * 1000
              rounded to 3 decimals, and sets `status` to `"ok"` or `"error"`

            **Rules**
            - `status` is `"error"` when an exception is raised inside the block, else `"ok"`.
            - The exception must still propagate (don't swallow it).

            **Examples**
            ```python
            readings = iter([2.0, 2.5])
            with Span("retrieve", lambda: next(readings)) as span:
                print(span.duration_ms)   # prints None
            span.duration_ms              # 500.0
            span.status                   # "ok"
            ```
        ''',
        "starter": r'''
            class Span:
                def __init__(self, name, clock):
                    ...
        ''',
        "tests": r'''
            from solution import Span

            def fake_clock(*values):
                it = iter(values)
                return lambda: next(it)

            def test_duration_and_ok_status():
                with Span("retrieve", fake_clock(2.0, 2.5)) as span:
                    assert span.duration_ms is None and span.status is None, "should be None inside the block"
                assert span.name == "retrieve"
                assert span.duration_ms == 500.0, f"duration_ms = {span.duration_ms!r}"
                assert span.status == "ok", f"status = {span.status!r}"

            def test_duration_is_rounded():
                with Span("x", fake_clock(0.0, 0.0123456)) as span:
                    pass
                assert span.duration_ms == 12.346, f"duration_ms = {span.duration_ms!r}"

            def test_error_status_and_exception_propagates():
                span = Span("llm", fake_clock(1.0, 1.25))
                try:
                    with span:
                        raise TimeoutError("slow")
                except TimeoutError:
                    pass
                else:
                    raise AssertionError("the exception was swallowed")
                assert span.status == "error", f"status = {span.status!r}"
                assert span.duration_ms == 250.0, f"duration_ms = {span.duration_ms!r}"
        ''',
        "solution": r'''
            class Span:
                def __init__(self, name, clock):
                    self.name = name
                    self.clock = clock
                    self.start = None
                    self.duration_ms = None
                    self.status = None

                def __enter__(self):
                    self.start = self.clock()
                    return self

                def __exit__(self, exc_type, exc, tb):
                    end = self.clock()
                    self.duration_ms = round((end - self.start) * 1000, 3)
                    self.status = "ok" if exc_type is None else "error"
                    return False
        ''',
        "hints": [
            "You need __init__, __enter__ and __exit__. Store the clock on self so both methods can use it.",
            "__enter__ saves the start reading and returns self. __exit__ reads the clock again, computes the duration, and checks whether exc_type is None.",
            "1) __init__: save name and clock, set duration_ms and status to None. 2) __enter__: self.start = self.clock(); return self. 3) __exit__: duration = round((self.clock() - self.start) * 1000, 3); status 'ok' if exc_type is None else 'error'; return False.",
        ],
    },
    {
        "id": "observability-3",
        "title": "JSON log formatter",
        "difficulty": 1,
        "lesson": r'''
            ## Formatters

            The `logging` module handles a message in three stages. A **logger** creates a
            **LogRecord**: an object that holds the message, the level, the logger name and
            the time. A **handler** sends the record to a destination such as the screen or
            a file. A **formatter** converts the record to the text that is written.

            To get structured logs, you give the handler your own formatter. It is a
            subclass of `logging.Formatter` with a `format(self, record)` method that
            returns a string.

            ```python
            import logging, sys

            class Shout(logging.Formatter):
                def format(self, record):
                    return record.levelname + "! " + record.getMessage().upper()

            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(Shout())
            log = logging.getLogger("demo")
            log.addHandler(handler)
            log.warning("disk at %s%%", 91)
            # WARNING! DISK AT 91%
            ```

            The handler calls `format` once for each record and writes the string it
            returns. `record.levelname` is the level name, here `"WARNING"`. `record.name`
            is the logger name, here `"demo"`.

            `record.getMessage()` returns the finished message. It puts the argument `91`
            in place of `%s` and turns `%%` into `%`.

            `record.msg` is the template `"disk at %s%%"` with nothing filled in. Use
            `record.getMessage()` for the text.
        ''',
        "research": {
            "note": "Skim the logging HOWTO (loggers, handlers, formatters), then find the table of "
                    "LogRecord attributes to see which fields a record carries.",
            "links": [
                {"title": "Logging HOWTO - Python docs",
                 "url": "https://docs.python.org/3/howto/logging.html"},
                {"title": "LogRecord attributes - Python docs",
                 "url": "https://docs.python.org/3/library/logging.html#logrecord-attributes"},
            ],
        },
        "prompt": r'''
            Make the logging module output one JSON object per line.

            **Write:** a class `JsonFormatter`, a subclass of `logging.Formatter`

            - Its `format(self, record)` method **returns** a JSON string of a dict with
              exactly three keys:
              - `"level"`: the level name, e.g. `"INFO"`
              - `"logger"`: the logger's name, e.g. `"rag"`
              - `"message"`: the finished message, with `%s`-style arguments filled in

            **Rules**
            - Use `json.dumps` (tests parse your output with `json.loads`).
            - `log.info("found %s chunks", 3)` must produce the message `"found 3 chunks"`.

            **Examples**
            ```python
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JsonFormatter())
            log = logging.getLogger("rag")
            log.addHandler(handler)
            log.warning("found %s chunks", 3)
            # prints {"level": "WARNING", "logger": "rag", "message": "found 3 chunks"}
            ```
        ''',
        "starter": r'''
            import json
            import logging

            class JsonFormatter(logging.Formatter):
                ...
        ''',
        "tests": r'''
            import io
            import json
            import logging
            from solution import JsonFormatter

            def emit(name, level, msg, *args):
                stream = io.StringIO()
                handler = logging.StreamHandler(stream)
                handler.setFormatter(JsonFormatter())
                log = logging.getLogger(name)
                log.handlers = [handler]
                log.propagate = False
                log.setLevel(logging.DEBUG)
                log.log(level, msg, *args)
                return stream.getvalue().strip()

            def test_is_a_formatter_subclass():
                assert issubclass(JsonFormatter, logging.Formatter)

            def test_outputs_json_with_three_keys():
                line = emit("rag", logging.INFO, "ready")
                data = json.loads(line)
                assert data == {"level": "INFO", "logger": "rag", "message": "ready"}, f"got {data!r}"

            def test_arguments_are_filled_in():
                data = json.loads(emit("rag.retrieve", logging.WARNING, "found %s chunks", 3))
                assert data["message"] == "found 3 chunks", f"message was {data['message']!r}"
                assert data["level"] == "WARNING" and data["logger"] == "rag.retrieve", f"got {data!r}"
        ''',
        "solution": r'''
            import json
            import logging

            class JsonFormatter(logging.Formatter):
                def format(self, record):
                    return json.dumps({
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                    })
        ''',
        "hints": [
            "Override the format method; the record has attributes for the level name, logger name and finished message.",
            "record.levelname, record.name and record.getMessage() give the three values. Put them in a dict and dump it.",
            "Inside the class: def format(self, record): return json.dumps({'level': record.levelname, 'logger': record.name, 'message': record.getMessage()}).",
        ],
    },
    {
        "id": "observability-4",
        "title": "Usage summary",
        "difficulty": 1,
        "lesson": r'''
            ## Usage totals

            A log holds one usage record per request. To get totals for a day, you loop over
            the records and add each number to a running total.

            ```python
            usage = [{"model": "small", "input_tokens": 1000},
                     {"model": "small", "input_tokens": 2000}]
            total = 0
            for u in usage:
                total += u["input_tokens"]
            print(total)
            # 3000
            ```

            Step through the loop and watch `total` grow.

            ```diagram
            {"type": "trace", "title": "Adding up input tokens", "code": ["usage = [{\"model\": \"small\", \"input_tokens\": 1000},", "         {\"model\": \"small\", \"input_tokens\": 2000}]", "total = 0", "for u in usage:", "    total += u[\"input_tokens\"]", "print(total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {}, "out": ""},
              {"line": 1, "vars": {}, "out": ""},
              {"line": 3, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu..."}, "out": ""},
              {"line": 4, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "0"}, "out": ""},
              {"line": 5, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "0", "u": "{'model': 'small', 'input_tokens': 1000}"}, "out": ""},
              {"line": 4, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "1000", "u": "{'model': 'small', 'input_tokens': 1000}"}, "out": ""},
              {"line": 5, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "1000", "u": "{'model': 'small', 'input_tokens': 2000}"}, "out": ""},
              {"line": 4, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "3000", "u": "{'model': 'small', 'input_tokens': 2000}"}, "out": ""},
              {"line": 6, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "3000", "u": "{'model': 'small', 'input_tokens': 2000}"}, "out": ""},
              {"line": null, "vars": {"usage": "[{'model': 'small', 'input_tokens': 1000}, {'model': 'small', 'inpu...", "total": "3000", "u": "{'model': 'small', 'input_tokens': 2000}"}, "out": "3000\n"}
            ]}
            ```

            Models have different prices, so you keep a **price table**: a dict that maps
            each model name to its prices per million tokens. The loop looks up the prices
            of each record's model and adds that record's cost to the total.

            ```python
            prices = {"small": {"input": 0.15, "output": 0.60}}
            usage = [{"model": "small", "input_tokens": 1000, "output_tokens": 500},
                     {"model": "small", "input_tokens": 2000, "output_tokens": 0}]
            dollars = 0.0
            for u in usage:
                p = prices[u["model"]]
                dollars += u["input_tokens"] * p["input"] / 1_000_000
                dollars += u["output_tokens"] * p["output"] / 1_000_000
            print(round(dollars, 6))
            # 0.00075
            ```

            This is **cost accounting**: recording what each request cost and adding the
            costs up. Teams use the totals to set budgets and alerts.

            A model that is missing from the price table must raise an exception with a
            clear message. Counting it as free would hide real spending.
        ''',
        "prompt": r'''
            Summarise token usage and cost for a batch of requests.

            **Write:** `summarize_usage(requests, prices)`

            - `requests`: a list of dicts like `{"model": "small", "input_tokens": 1000, "output_tokens": 500}`
            - `prices`: a dict like `{"small": {"input": 0.15, "output": 0.60}}`, dollars per million tokens
            - **Returns:** a dict
              `{"requests": int, "input_tokens": int, "output_tokens": int, "cost_usd": float}`

            **Rules**
            - Cost per request = input_tokens * input price / 1,000,000 + output_tokens * output price / 1,000,000.
            - `cost_usd` is the total rounded to 6 decimals.
            - A model not in `prices` raises `ValueError` with the message `no price for model: <model>`.
            - No requests returns `{"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}`.

            **Examples**
            ```python
            prices = {"small": {"input": 0.15, "output": 0.60}, "big": {"input": 2.5, "output": 10.0}}
            summarize_usage([{"model": "small", "input_tokens": 1000, "output_tokens": 500},
                             {"model": "big", "input_tokens": 2000, "output_tokens": 100}], prices)
            # returns {"requests": 2, "input_tokens": 3000, "output_tokens": 600, "cost_usd": 0.00645}
            ```
        ''',
        "starter": r'''
            def summarize_usage(requests, prices):
                ...
        ''',
        "tests": r'''
            from solution import summarize_usage

            PRICES = {"small": {"input": 0.15, "output": 0.60}, "big": {"input": 2.5, "output": 10.0}}

            def test_two_models():
                got = summarize_usage([{"model": "small", "input_tokens": 1000, "output_tokens": 500},
                                       {"model": "big", "input_tokens": 2000, "output_tokens": 100}], PRICES)
                assert got == {"requests": 2, "input_tokens": 3000, "output_tokens": 600,
                               "cost_usd": 0.00645}, f"got {got!r}"

            def test_no_requests():
                got = summarize_usage([], PRICES)
                assert got == {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}, f"got {got!r}"

            def test_unknown_model_raises_value_error_with_name():
                try:
                    summarize_usage([{"model": "mystery", "input_tokens": 1, "output_tokens": 1}], PRICES)
                except ValueError as exc:
                    assert "no price for model: mystery" in str(exc), f"message was {str(exc)!r}"
                    return
                raise AssertionError("an unknown model should raise ValueError")
        ''',
        "solution": r'''
            def summarize_usage(requests, prices):
                summary = {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
                total = 0.0
                for req in requests:
                    if req["model"] not in prices:
                        raise ValueError(f"no price for model: {req['model']}")
                    price = prices[req["model"]]
                    summary["requests"] += 1
                    summary["input_tokens"] += req["input_tokens"]
                    summary["output_tokens"] += req["output_tokens"]
                    total += req["input_tokens"] * price["input"] / 1_000_000
                    total += req["output_tokens"] * price["output"] / 1_000_000
                summary["cost_usd"] = round(total, 6)
                return summary
        ''',
        "hints": [
            "Loop over the requests, look up each model's prices, and keep running totals.",
            "Check the model is in the price table before using it; add tokens to the counters and each request's cost to a total, then round at the end.",
            "Start a summary dict with zeros. For each request: raise ValueError if model not in prices; add 1 to requests; add the tokens; add the cost. Finally set cost_usd = round(total, 6).",
        ],
    },
    {
        "id": "observability-5",
        "title": "Redact secret fields",
        "difficulty": 1,
        "lesson": r'''
            ## Redacting dict fields

            A whole request dict is useful in a log because it holds everything you need to
            debug. It also holds the `Authorization` header and sometimes an `api_key`.
            Before you log the dict, build a copy in which the value of every secret key is
            replaced by a placeholder.

            ```python
            SECRET = {"api_key", "authorization", "password"}
            request = {"model": "gpt-4o", "Authorization": "Bearer sk-123"}
            safe = {}
            for key, value in request.items():
                safe[key] = "***" if key.lower() in SECRET else value
            print(safe)
            # {'model': 'gpt-4o', 'Authorization': '***'}
            print(request["Authorization"])
            # Bearer sk-123
            ```

            The loop copies each key into `safe`. The value is `"***"` when the key is a
            secret key, and the original value otherwise.

            Header names appear in any letter case, such as `Authorization` or
            `authorization`. `key.lower()` returns the key in lowercase, so one lowercase
            name in `SECRET` matches both. The key stored in `safe` keeps its original
            spelling.

            `safe` is a **new** dict. `request` still holds the real key, as the last line
            shows. `request[key] = "***"` inside the loop would change the caller's dict,
            and the API call that uses it would then send `"***"` as the key.
        ''',
        "prompt": r'''
            Hide secret values in a dict before logging it.

            **Write:** `redact_fields(data, secret_keys=("api_key", "authorization", "password"))`

            - `data`: a flat dict, e.g. `{"model": "gpt-4o", "Authorization": "Bearer sk-1"}`
            - `secret_keys`: a tuple of lowercase key names to hide
            - **Returns:** a **new** dict with the same keys; the value of every secret key is
              replaced by the string `"***"`, other values unchanged

            **Rules**
            - Keys match ignoring case: `"API_KEY"` and `"Authorization"` count.
            - Don't modify `data`.

            **Examples**
            ```python
            redact_fields({"model": "gpt-4o", "Authorization": "Bearer sk-1"})
            # returns {"model": "gpt-4o", "Authorization": "***"}
            redact_fields({"user": "ada", "token": "t1"}, secret_keys=("token",))
            # returns {"user": "ada", "token": "***"}
            ```
        ''',
        "starter": r'''
            def redact_fields(data, secret_keys=("api_key", "authorization", "password")):
                ...
        ''',
        "tests": r'''
            from solution import redact_fields

            def test_default_secret_keys_any_case():
                got = redact_fields({"model": "gpt-4o", "Authorization": "Bearer sk-1", "API_KEY": "k", "password": "p"})
                assert got == {"model": "gpt-4o", "Authorization": "***", "API_KEY": "***", "password": "***"}, f"got {got!r}"

            def test_custom_secret_keys():
                got = redact_fields({"user": "ada", "token": "t1", "api_key": "k"}, secret_keys=("token",))
                assert got == {"user": "ada", "token": "***", "api_key": "k"}, f"got {got!r}"

            def test_input_not_modified():
                data = {"api_key": "sk-real"}
                redact_fields(data)
                assert data == {"api_key": "sk-real"}, f"data became {data!r}"

            def test_empty_dict():
                assert redact_fields({}) == {}
        ''',
        "solution": r'''
            def redact_fields(data, secret_keys=("api_key", "authorization", "password")):
                return {key: ("***" if key.lower() in secret_keys else value)
                        for key, value in data.items()}
        ''',
        "hints": [
            "Build a new dict from data.items(), deciding each value based on the key.",
            "Lowercase each key before checking whether it is in secret_keys; use '***' for secrets and the original value otherwise.",
            "Use a dict comprehension: {key: '***' if key.lower() in secret_keys else value for key, value in data.items()}.",
        ],
    },
    {
        "id": "observability-6",
        "title": "Latency report",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Summarise the latencies of many requests for a dashboard.

            **Write:** `latency_report(durations_ms)`

            - `durations_ms`: a list of numbers (milliseconds), any order
            - **Returns:** a dict `{"count": int, "p50": ..., "p95": ..., "max": ...}`

            **Rules**
            - `p50` and `p95` use the nearest-rank method: sort, `rank = ceil(p * n / 100)`
              (at least 1), take the value at position `rank` counting from 1.
            - `max` is the largest value.
            - An empty list returns `{"count": 0, "p50": None, "p95": None, "max": None}`.
            - Don't modify the input list.

            **Examples**
            ```python
            latency_report([120, 80, 950, 100, 110])
            # returns {"count": 5, "p50": 110, "p95": 950, "max": 950}
            latency_report(list(range(1, 21)))
            # returns {"count": 20, "p50": 10, "p95": 19, "max": 20}
            latency_report([])
            # returns {"count": 0, "p50": None, "p95": None, "max": None}
            ```
        ''',
        "starter": r'''
            import math

            def latency_report(durations_ms):
                ...
        ''',
        "tests": r'''
            from solution import latency_report

            def test_five_requests():
                got = latency_report([120, 80, 950, 100, 110])
                assert got == {"count": 5, "p50": 110, "p95": 950, "max": 950}, f"got {got!r}"

            def test_twenty_requests():
                got = latency_report(list(range(20, 0, -1)))
                assert got == {"count": 20, "p50": 10, "p95": 19, "max": 20}, f"got {got!r}"

            def test_single_request():
                got = latency_report([42.5])
                assert got == {"count": 1, "p50": 42.5, "p95": 42.5, "max": 42.5}, f"got {got!r}"

            def test_empty():
                got = latency_report([])
                assert got == {"count": 0, "p50": None, "p95": None, "max": None}, f"got {got!r}"

            def test_input_not_modified():
                data = [3, 1, 2]
                latency_report(data)
                assert data == [3, 1, 2], f"input became {data!r}"
        ''',
        "solution": r'''
            import math

            def _nearest_rank(ordered, p):
                rank = max(1, math.ceil(p * len(ordered) / 100))
                return ordered[rank - 1]

            def latency_report(durations_ms):
                if not durations_ms:
                    return {"count": 0, "p50": None, "p95": None, "max": None}
                ordered = sorted(durations_ms)
                return {
                    "count": len(ordered),
                    "p50": _nearest_rank(ordered, 50),
                    "p95": _nearest_rank(ordered, 95),
                    "max": ordered[-1],
                }
        ''',
        "hints": [
            "Reuse the nearest-rank percentile idea from earlier: sort once, then pick positions.",
            "Handle the empty list first. Otherwise sort a copy, compute the p50 and p95 positions with math.ceil, and take the last item as max.",
            "1) Empty -> the dict of Nones. 2) ordered = sorted(durations_ms). 3) Helper: rank = max(1, ceil(p * n / 100)); return ordered[rank - 1]. 4) Return count, p50, p95 and ordered[-1].",
        ],
    },
    {
        "id": "observability-7",
        "title": "Deep redaction",
        "difficulty": 2,
        "prompt": r'''
            Real log payloads are nested: messages inside a request, headers inside a config.
            Redact secrets at any depth before logging.

            **Write:** `redact_deep(value)`

            - `value`: any JSON-like value: a dict, list, string, number, bool or `None`,
              possibly nested
            - **Returns:** a **new** value of the same shape with secrets hidden

            **Rules**
            - In every dict (at any depth), a key whose lowercase form is `"api_key"`,
              `"authorization"` or `"password"` gets the value `"***"` (whatever it was).
            - Every other string (at any depth, including list items) has API keys replaced
              by `[REDACTED]`: `sk-` followed by 8 or more letters, digits, `_` or `-`.
            - Numbers, bools and `None` are returned unchanged. Dict keys stay the same.
            - Don't modify the input.

            **Examples**
            ```python
            redact_deep({"headers": {"Authorization": "Bearer x"},
                         "messages": [{"role": "user", "content": "my key is sk-abcdefgh123"}],
                         "max_tokens": 50})
            # returns {"headers": {"Authorization": "***"},
            #          "messages": [{"role": "user", "content": "my key is [REDACTED]"}],
            #          "max_tokens": 50}
            redact_deep("sk-12345678")   # returns "[REDACTED]"
            redact_deep(None)            # returns None
            ```
        ''',
        "starter": r'''
            import re

            def redact_deep(value):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import redact_deep

            PAYLOAD = {"headers": {"Authorization": "Bearer x"},
                       "messages": [{"role": "user", "content": "my key is sk-abcdefgh123"}],
                       "max_tokens": 50}

            def test_nested_payload():
                got = redact_deep(PAYLOAD)
                assert got == {"headers": {"Authorization": "***"},
                               "messages": [{"role": "user", "content": "my key is [REDACTED]"}],
                               "max_tokens": 50}, f"got {got!r}"

            def test_secret_key_value_hidden_even_if_not_string():
                got = redact_deep({"PASSWORD": 1234, "api_key": {"nested": "x"}})
                assert got == {"PASSWORD": "***", "api_key": "***"}, f"got {got!r}"

            def test_strings_in_lists_and_top_level():
                got = redact_deep(["ok", "sk-12345678", [None, True, 3.5]])
                assert got == ["ok", "[REDACTED]", [None, True, 3.5]], f"got {got!r}"
                assert redact_deep("sk-12345678") == "[REDACTED]"
                assert redact_deep(None) is None

            def test_input_not_modified():
                original = copy.deepcopy(PAYLOAD)
                redact_deep(PAYLOAD)
                assert PAYLOAD == original, "the input was changed"
        ''',
        "solution": r'''
            import re

            SECRET_KEYS = {"api_key", "authorization", "password"}
            KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_-]{8,}")

            def redact_deep(value):
                if isinstance(value, dict):
                    return {k: ("***" if k.lower() in SECRET_KEYS else redact_deep(v))
                            for k, v in value.items()}
                if isinstance(value, list):
                    return [redact_deep(item) for item in value]
                if isinstance(value, str):
                    return KEY_PATTERN.sub("[REDACTED]", value)
                return value
        ''',
        "hints": [
            "This is a recursive function: it calls itself on the values inside dicts and lists.",
            "Check the type with isinstance: dicts get a new dict (secret keys -> '***', others recurse), lists get a new list of recursed items, strings get re.sub, everything else comes back as is.",
            "1) dict: comprehension with '***' if k.lower() is secret else redact_deep(v). 2) list: [redact_deep(x) for x in value]. 3) str: re.sub(pattern, '[REDACTED]', value). 4) otherwise return value.",
        ],
    },
    {
        "id": "observability-8",
        "title": "A tracer with nested spans",
        "difficulty": 3,
        "lesson": r'''
            ## Putting it together: traces

            The steps of one request are nested: the `answer` span contains the `retrieve`
            span and the `llm_call` span. The containing span is the **parent**. All the
            spans of one request form a **trace**.

            A **tracer** records every span with the name of its parent, so you can see
            which step took the time. OpenTelemetry, a widely used tracing library, does the
            same. The tracer keeps a **stack** of the open spans: a list where items are
            added and removed only at the end. `append` adds a span name when its block
            starts and `pop()` removes it when the block ends. A new span's parent is the
            last item of the stack at the moment the span starts.
        ''',
        "prompt": r'''
            Record nested spans for one request.

            **Write:** a class `Tracer`

            - `Tracer(clock)`: `clock` is a function returning seconds (float)
            - `tracer.span(name)` returns a context manager for use in `with tracer.span("retrieve"):`
            - `tracer.spans`: a list of finished spans, each a dict
              `{"name": str, "parent": str or None, "duration_ms": float, "status": "ok" or "error"}`

            **Rules**
            - Each span reads `clock()` once when its block starts and once when it ends;
              `duration_ms` = (end - start) * 1000 rounded to 3 decimals.
            - `parent` is the name of the span that was open (innermost) when this one started,
              or `None` at the top level.
            - Spans are appended to `tracer.spans` when they **finish**, so children come before
              their parent.
            - `status` is `"error"` if an exception escaped the block (it must still propagate),
              else `"ok"`. After an error, the next span's parent is correct again.

            **Examples**
            ```python
            readings = iter([0.0, 0.1, 0.3, 0.4, 0.9, 1.0])
            tracer = Tracer(lambda: next(readings))
            with tracer.span("answer"):
                with tracer.span("retrieve"):
                    pass
                with tracer.span("llm_call"):
                    pass
            tracer.spans
            # [{"name": "retrieve", "parent": "answer", "duration_ms": 200.0, "status": "ok"},
            #  {"name": "llm_call", "parent": "answer", "duration_ms": 500.0, "status": "ok"},
            #  {"name": "answer", "parent": None, "duration_ms": 1000.0, "status": "ok"}]
            ```
        ''',
        "starter": r'''
            class Tracer:
                def __init__(self, clock):
                    ...
        ''',
        "tests": r'''
            from solution import Tracer

            def fake_clock(*values):
                it = iter(values)
                return lambda: next(it)

            def test_nested_spans_with_parents():
                tracer = Tracer(fake_clock(0.0, 0.1, 0.3, 0.4, 0.9, 1.0))
                with tracer.span("answer"):
                    with tracer.span("retrieve"):
                        pass
                    with tracer.span("llm_call"):
                        pass
                assert tracer.spans == [
                    {"name": "retrieve", "parent": "answer", "duration_ms": 200.0, "status": "ok"},
                    {"name": "llm_call", "parent": "answer", "duration_ms": 500.0, "status": "ok"},
                    {"name": "answer", "parent": None, "duration_ms": 1000.0, "status": "ok"},
                ], f"got {tracer.spans!r}"

            def test_three_levels_deep():
                tracer = Tracer(fake_clock(0.0, 1.0, 2.0, 3.0, 4.0, 5.0))
                with tracer.span("a"):
                    with tracer.span("b"):
                        with tracer.span("c"):
                            pass
                parents = [(s["name"], s["parent"]) for s in tracer.spans]
                assert parents == [("c", "b"), ("b", "a"), ("a", None)], f"got {parents!r}"

            def test_error_status_propagates_and_stack_recovers():
                tracer = Tracer(fake_clock(0.0, 0.5, 0.75, 1.0, 1.5, 2.0))
                try:
                    with tracer.span("request"):
                        with tracer.span("tool"):
                            raise KeyError("missing")
                except KeyError:
                    pass
                else:
                    raise AssertionError("the exception was swallowed")
                with tracer.span("next"):
                    pass
                assert tracer.spans[0] == {"name": "tool", "parent": "request", "duration_ms": 250.0, "status": "error"}, f"got {tracer.spans[0]!r}"
                assert tracer.spans[1]["status"] == "error", f"got {tracer.spans[1]!r}"
                assert tracer.spans[2]["parent"] is None, f"got {tracer.spans[2]!r}"

            def test_sequential_top_level_spans():
                tracer = Tracer(fake_clock(0.0, 0.002, 1.0, 1.0035))
                with tracer.span("x"):
                    pass
                with tracer.span("y"):
                    pass
                got = [(s["name"], s["parent"], s["duration_ms"]) for s in tracer.spans]
                assert got == [("x", None, 2.0), ("y", None, 3.5)], f"got {got!r}"
        ''',
        "solution": r'''
            class _ActiveSpan:
                def __init__(self, tracer, name):
                    self.tracer = tracer
                    self.name = name

                def __enter__(self):
                    stack = self.tracer._stack
                    self.parent = stack[-1] if stack else None
                    stack.append(self.name)
                    self.start = self.tracer.clock()
                    return self

                def __exit__(self, exc_type, exc, tb):
                    end = self.tracer.clock()
                    self.tracer._stack.pop()
                    self.tracer.spans.append({
                        "name": self.name,
                        "parent": self.parent,
                        "duration_ms": round((end - self.start) * 1000, 3),
                        "status": "ok" if exc_type is None else "error",
                    })
                    return False


            class Tracer:
                def __init__(self, clock):
                    self.clock = clock
                    self.spans = []
                    self._stack = []

                def span(self, name):
                    return _ActiveSpan(self, name)
        ''',
        "hints": [
            "You need two classes: the Tracer, and a small context-manager class that span() returns. The tracer keeps a stack (a list) of open span names.",
            "On enter: the parent is the last name on the stack (or None), push this name, read the clock. On exit: read the clock, pop the stack, append the finished span dict.",
            "1) Tracer.__init__: save clock, spans = [], stack = []. 2) span(name) returns a helper object holding the tracer and name. 3) helper __enter__: parent = stack[-1] if stack else None; stack.append(name); start = clock(). 4) helper __exit__: end = clock(); stack.pop(); append the dict with rounded duration and status; return False.",
        ],
    },
    {
        "id": "observability-9",
        "title": "An instrumented LLM call",
        "difficulty": 3,
        "lesson": r'''
            ## Putting it together: one observable call

            In production every model call goes through the same steps. You time it, record
            its token counts and cost, and log one structured line with secrets redacted.
            When the call raises an exception, you log it at the `ERROR` level and raise it
            again. Put these steps in one function that makes the model call. When all code
            calls the model through that function, every call is logged.
        ''',
        "research": {
            "note": "See how OpenTelemetry names the same ideas (tracer, span, attributes, exporter). "
                    "The function you write here is a hand-made version of an instrumented span.",
            "links": [
                {"title": "OpenTelemetry Python: getting started",
                 "url": "https://opentelemetry.io/docs/languages/python/getting-started/"},
            ],
        },
        "prompt": r'''
            Wrap a (fake) LLM call with timing, cost accounting and structured logging.

            **Write:** `traced_llm_call(llm, prompt, *, model, clock, logger, prices)`

            - `llm`: a function called as `llm(prompt)`; returns a dict
              `{"text": str, "input_tokens": int, "output_tokens": int}`
            - `prompt`: a string
            - `model`: a string, e.g. `"small"`
            - `clock`: a function returning seconds (float)
            - `logger`: a `logging.Logger`
            - `prices`: dict like `{"small": {"input": 0.15, "output": 0.60}}` (dollars per million tokens)
            - **Returns:** the reply's `"text"`

            **Rules**
            - Read `clock()` once right before calling `llm` and once right after it returns
              (or raises). `latency_ms` = (after - before) * 1000 rounded to 3 decimals.
            - On success, call `logger.info` once with a JSON string (one object) with keys:
              `"event": "llm_call"`, `"model"`, `"latency_ms"`, `"input_tokens"`,
              `"output_tokens"`, `"cost_usd"` (rounded to 6 decimals) and `"prompt"`: the prompt
              with API keys (`sk-` + 8 or more letters, digits, `_` or `-`) replaced by `[REDACTED]`.
            - If `llm` raises, call `logger.error` once with a JSON string with keys
              `"event": "llm_error"`, `"model"`, `"latency_ms"`, `"error"` (the exception's class
              name, e.g. `"TimeoutError"`), then re-raise the same exception.
            - Never log the raw prompt (but send the original prompt to `llm`).
            - If `model` is not in `prices`, raise `KeyError` or `ValueError` (never treat it as free).

            **Examples**
            ```python
            readings = iter([5.0, 5.5])
            reply = traced_llm_call(
                lambda p: {"text": "Hi!", "input_tokens": 1000, "output_tokens": 500},
                "hello, key sk-abcdefgh99", model="small", clock=lambda: next(readings),
                logger=logging.getLogger("app"), prices={"small": {"input": 0.15, "output": 0.60}})
            # reply is "Hi!"; the INFO message parses to
            # {"event": "llm_call", "model": "small", "latency_ms": 500.0, "input_tokens": 1000,
            #  "output_tokens": 500, "cost_usd": 0.00045, "prompt": "hello, key [REDACTED]"}
            ```
        ''',
        "starter": r'''
            import json
            import re

            def traced_llm_call(llm, prompt, *, model, clock, logger, prices):
                ...
        ''',
        "tests": r'''
            import json
            import logging
            from solution import traced_llm_call

            PRICES = {"small": {"input": 0.15, "output": 0.60}}

            class ListHandler(logging.Handler):
                def __init__(self):
                    super().__init__()
                    self.records = []
                def emit(self, record):
                    self.records.append(record)

            def make_logger(name):
                log = logging.getLogger(name)
                handler = ListHandler()
                log.handlers = [handler]
                log.propagate = False
                log.setLevel(logging.DEBUG)
                return log, handler

            def fake_clock(*values):
                it = iter(values)
                return lambda: next(it)

            def test_success_returns_text_and_logs_one_info_line():
                log, h = make_logger("t.success")
                reply = traced_llm_call(
                    lambda p: {"text": "Hi!", "input_tokens": 1000, "output_tokens": 500},
                    "hello, key sk-abcdefgh99", model="small", clock=fake_clock(5.0, 5.5),
                    logger=log, prices=PRICES)
                assert reply == "Hi!", f"returned {reply!r}"
                assert len(h.records) == 1, f"logged {len(h.records)} records"
                rec = h.records[0]
                assert rec.levelno == logging.INFO, f"level was {rec.levelname}"
                data = json.loads(rec.getMessage())
                assert data == {"event": "llm_call", "model": "small", "latency_ms": 500.0,
                                "input_tokens": 1000, "output_tokens": 500, "cost_usd": 0.00045,
                                "prompt": "hello, key [REDACTED]"}, f"got {data!r}"

            def test_raw_key_never_logged_but_sent_to_model():
                log, h = make_logger("t.secret")
                seen = []
                def llm(p):
                    seen.append(p)
                    return {"text": "ok", "input_tokens": 1, "output_tokens": 1}
                traced_llm_call(llm, "use sk-SECRETSECRET", model="small", clock=fake_clock(0.0, 0.1),
                                logger=log, prices=PRICES)
                assert seen == ["use sk-SECRETSECRET"], "the model must receive the original prompt"
                assert "SECRETSECRET" not in h.records[0].getMessage(), "the key leaked into the log"

            def test_error_is_logged_and_reraised():
                log, h = make_logger("t.error")
                def llm(p):
                    raise TimeoutError("took too long")
                try:
                    traced_llm_call(llm, "hi", model="small", clock=fake_clock(1.0, 3.0),
                                    logger=log, prices=PRICES)
                except TimeoutError:
                    pass
                else:
                    raise AssertionError("the TimeoutError should be re-raised")
                assert len(h.records) == 1, f"logged {len(h.records)} records"
                rec = h.records[0]
                assert rec.levelno == logging.ERROR, f"level was {rec.levelname}"
                data = json.loads(rec.getMessage())
                assert data == {"event": "llm_error", "model": "small", "latency_ms": 2000.0,
                                "error": "TimeoutError"}, f"got {data!r}"

            def test_unknown_model_price_is_an_error_not_free():
                log, h = make_logger("t.price")
                try:
                    traced_llm_call(lambda p: {"text": "x", "input_tokens": 1, "output_tokens": 1},
                                    "hi", model="huge", clock=fake_clock(0.0, 1.0), logger=log, prices=PRICES)
                except KeyError:
                    return
                except ValueError:
                    return
                raise AssertionError("a model missing from prices should raise (KeyError or ValueError)")
        ''',
        "solution": r'''
            import json
            import re

            KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_-]{8,}")

            def traced_llm_call(llm, prompt, *, model, clock, logger, prices):
                start = clock()
                try:
                    reply = llm(prompt)
                except Exception as exc:
                    latency = round((clock() - start) * 1000, 3)
                    logger.error(json.dumps({"event": "llm_error", "model": model,
                                             "latency_ms": latency, "error": type(exc).__name__}))
                    raise
                latency = round((clock() - start) * 1000, 3)
                price = prices[model]
                cost = (reply["input_tokens"] * price["input"] / 1_000_000
                        + reply["output_tokens"] * price["output"] / 1_000_000)
                logger.info(json.dumps({
                    "event": "llm_call",
                    "model": model,
                    "latency_ms": latency,
                    "input_tokens": reply["input_tokens"],
                    "output_tokens": reply["output_tokens"],
                    "cost_usd": round(cost, 6),
                    "prompt": KEY_PATTERN.sub("[REDACTED]", prompt),
                }))
                return reply["text"]
        ''',
        "hints": [
            "Combine earlier steps: the injected clock, the cost formula, key redaction with re.sub, and json.dumps for the log line.",
            "Read the clock, call llm inside try/except. In except: read the clock, log the error JSON with logger.error, and use a bare raise. Otherwise read the clock, compute cost, log the info JSON, return the text.",
            "1) start = clock(). 2) try: reply = llm(prompt) / except Exception as exc: latency, logger.error(json.dumps({...,'error': type(exc).__name__})), raise. 3) latency, cost from prices[model]. 4) logger.info(json.dumps({... 'prompt': redacted})). 5) return reply['text'].",
        ],
    },
]
