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

LESSON = r'''
## Chapter notes: observability

**Why**: once an app is live you can't watch it. Logs, traces and metrics are its flight
recorder: what happened, how long it took, what it cost.

**logging basics**
```python
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("rag")      # one named logger per module/component
log.info("retrieved %s chunks", 3)  # args are filled in lazily
```
Levels are numbers: DEBUG 10, INFO 20, WARNING 30, ERROR 40, CRITICAL 50. A logger/handler
shows records **at or above** its level. `record.getMessage()` gives the finished text
(`msg % args`); `record.levelname`, `record.name` are the level and logger names.

**Structured logs**: one JSON object per line (`json.dumps(..., sort_keys=True)`), so a
machine can filter by `event`, `model`, `latency_ms`. A custom `logging.Formatter` subclass
with a `format(self, record)` method turns records into JSON.

**Timing**: `time.perf_counter()` is a stopwatch (seconds, float). `elapsed = end - start`.
In code you want to test, take the clock as a parameter (`clock=time.perf_counter`) and pass
a fake clock in tests: deterministic numbers, no sleeping.

**Context managers**: `with X as y:` calls `X.__enter__()` (its return value becomes `y`),
runs the block, then always calls `X.__exit__(exc_type, exc, tb)` - even on an exception.
Returning `False` from `__exit__` lets the exception continue.

**Spans and traces**: a *span* is one timed step (`retrieve`, `llm_call`) with a name,
duration and status. Spans nest: the enclosing span is the *parent*. All spans of one request
form a *trace*. OpenTelemetry is the standard library/format for this.

**Latency percentiles** (nearest-rank): sort values, `rank = ceil(p * n / 100)` (at least 1),
answer `sorted_values[rank - 1]`. p50 = typical request, p95 = the slow tail users feel.
Averages hide the tail.

**Cost**: prices are per million tokens:
`cost = input_tokens * in_price / 1_000_000 + output_tokens * out_price / 1_000_000`.

**Redaction**: logs are read by many people and tools. Never log API keys, passwords or
auth headers: replace them (`sk-...` -> `[REDACTED]`, secret fields -> `"***"`) before logging,
and build a new structure instead of mutating the caller's data.
'''

EXERCISES = [
    {
        "id": "observability-s1",
        "title": "Which log lines show up?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The flight recorder

            Once your app runs on a server, you can't watch it. `print` goes nowhere useful.
            You need a **flight recorder**: a record of what happened, which you read after
            something goes wrong. In Python that's the `logging` module.

            ```python
            import logging, sys

            logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                format="%(levelname)s %(message)s")
            log = logging.getLogger("chat")
            log.info("request received")
            log.warning("retrying after 429")
            ```

            Every message has a **level**: `debug` (details for developers), `info` (normal
            events), `warning` (something odd), `error` (something failed), `critical`.

            The level you configure is a volume knob: set it to `WARNING` and only warnings
            and worse get through. `basicConfig` sets up the root logger once;
            `getLogger(name)` gives you a named logger to write with.
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
            ## A volume knob with numbers on it

            Behind the names, log levels are plain integers:

            ```python
            import logging

            print(logging.DEBUG, logging.INFO, logging.WARNING)
            print(logging.ERROR, logging.CRITICAL)
            print(logging.ERROR > logging.WARNING)
            print(logging.getLevelName(30))
            ```

            Bigger number = more serious. That's how "show WARNING and above" works: Python
            just compares numbers.

            It also means your code can **choose** a level. A common rule for API calls:
            server errors (status 500 and up) are `ERROR` - something is broken. Client
            errors like 404 or 429 (400-499) are `WARNING`. Everything else is `INFO`.

            Watch out: use the named constants (`logging.ERROR`), not magic numbers like `40`.
            They read better and can't be mistyped.
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
            ## Fill in a form, don't write a diary

            A diary entry: `"Called gpt-4o, took 812ms, used 1200 tokens"`. Easy for a human,
            painful for a computer: to find every slow call you'd need a regex.

            A form: `{"event": "llm_call", "model": "gpt-4o", "latency_ms": 812}`. Every field
            has a name, so tools can filter and chart them. Logs written as one JSON object per
            line are called **structured logs**.

            ```python
            import json

            fields = {"model": "gpt-4o", "latency_ms": 812}
            line = json.dumps({"event": "llm_call", **fields}, sort_keys=True)
            print(line)
            print(json.loads(line)["latency_ms"])
            ```

            `{"event": ..., **fields}` builds a **new** dict: the `event` key plus everything
            from `fields`. `sort_keys=True` makes the key order stable, so the same data always
            gives the same line.

            Watch out: `fields["event"] = ...` would change the caller's dict. Build a new one.
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
            ## A stopwatch you can control

            To time something, read a stopwatch before and after: `time.perf_counter()` returns
            seconds as a float from a high-precision clock. Its absolute value means nothing;
            only the **difference** between two readings matters.

            ```python
            import time

            start = time.perf_counter()
            total = sum(range(100_000))
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(elapsed_ms > 0)
            ```

            Real clocks give different numbers every run, which makes tests flaky. The fix:
            take the clock as a **parameter**. In production pass `time.perf_counter`; in tests
            pass a fake that returns the numbers you choose. This is called **injecting** the
            clock (the same trick as injecting a fake model).

            ```python
            readings = iter([10.0, 10.25])
            fake_clock = lambda: next(readings)
            a, b = fake_clock(), fake_clock()
            print((b - a) * 1000)
            ```
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
            ## The taxi meter

            An LLM API is a taxi with two meters: one for tokens you send (**input**) and one
            for tokens it writes (**output**). Output tokens usually cost more.

            Providers quote prices **per million tokens**, e.g. "$2.50 / 1M input, $10 / 1M
            output". So one token costs `price / 1_000_000`.

            ```python
            input_tokens, output_tokens = 1200, 300
            in_price, out_price = 2.50, 10.00   # dollars per million tokens
            cost = input_tokens * in_price / 1_000_000 + output_tokens * out_price / 1_000_000
            print(cost)
            print(round(cost, 6))
            ```

            Cost per request is tiny, but multiply by a million requests a day and it's the
            biggest line on the bill. That's why production apps log it on **every** call.

            Watch out: `1_000_000` is just `1000000` with underscores for readability.
            Forgetting to divide gives you costs a million times too high.
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
            ## Logs are postcards

            A log line is like a postcard: the mail carrier, the neighbours, anyone who handles
            it can read it. Logs get copied to dashboards, shared in bug reports and kept for
            months. If an API key ends up in a log, consider it leaked.

            So before logging text that might contain secrets, **redact** them: replace the
            secret with a placeholder. Remember `re.sub` from the regex chapter?

            ```python
            import re

            text = "calling with key sk-abc123XYZ789 now"
            print(re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", text))
            print(re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", "sk-short stays"))
            ```

            Many providers use a recognisable prefix for keys (like `sk-`), which makes them
            easy to match. The `{8,}` part means "at least 8 more characters", so ordinary
            words that start with `sk-` are left alone.

            Watch out: redact **before** logging. Once the line is written, it's too late.
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
        "title": "The automatic door",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Things that clean up after themselves

            You've used `with open(...) as f:` - the file closes itself when the block ends.
            That's a **context manager**: like an automatic door that opens when you walk up
            and closes behind you, even if you leave in a hurry.

            You can make your own with a class that has two special methods:
            - `__enter__(self)`: runs when the `with` block starts. What it returns is what
              you get after `as`.
            - `__exit__(self, exc_type, exc, tb)`: runs when the block ends - **always**, even
              if an exception was raised. The three arguments describe the exception (all
              `None` if there wasn't one). Returning `False` means "don't hide the exception".

            ```python
            class Door:
                def __enter__(self):
                    print("open")
                    return "inside"
                def __exit__(self, exc_type, exc, tb):
                    print("close")
                    return False

            with Door() as where:
                print(where)
            ```

            This is perfect for timing: start the stopwatch in `__enter__`, stop it in
            `__exit__`.
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
            `with` calls `__enter__` first (prints `start retrieve`) and binds its return value -
            the Span itself - to `s`. The block runs, then `__exit__` runs. No exception
            happened, so `exc_type` is `None` and `exc_type is None` is `True`. Finally the code
            after the `with` block prints `done`.
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
            ## The slowest buses matter

            If your bus is usually 5 minutes late but one day in twenty it's an hour late, the
            **average** delay looks fine and you still miss meetings. Users feel the slow tail.

            So we report **percentiles**. p50 (the median) is the typical request. p95 means
            "95% of requests were at least this fast" - it shows the slow tail.

            A simple method is **nearest-rank**: sort the values, and take the one at position
            `ceil(p * n / 100)` (counting from 1).

            ```python
            import math

            latencies = [120, 80, 950, 100, 110]
            ordered = sorted(latencies)
            rank = math.ceil(95 * len(ordered) / 100)
            print(ordered, rank)
            print("p95:", ordered[rank - 1])
            print("mean:", sum(latencies) / len(latencies))
            ```

            Watch out: `sorted()` returns a new list; `.sort()` would reorder the caller's data.
            And a rank of 0 (for `p=0`) must become 1, or `[rank - 1]` is `[-1]`: the maximum!
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
            ## Wrap a step in a stopwatch

            In a RAG request there are several steps: embed, retrieve, call the model. To see
            which one is slow, wrap each in a **span**: a named, timed piece of work.

            A context manager is a perfect span. `__enter__` starts the stopwatch, `__exit__`
            stops it and notes whether the step ended with an exception.

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
            ```

            A span also has a **status**: `"ok"` if the block finished normally, `"error"` if
            an exception escaped. `exc_type` tells you which: it is `None` when all went well.

            Watch out: return `False` from `__exit__`. Returning `True` would swallow the
            exception and hide the failure.
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
            ## Teaching the logger to fill in forms

            The logging module has a pipeline: a **logger** creates a **LogRecord** (an object
            holding the message, level, logger name, time...), a **handler** decides where it
            goes (screen, file), and a **formatter** turns the record into text.

            To get structured logs, you swap in your own formatter: a subclass of
            `logging.Formatter` with a `format(self, record)` method that returns a string.

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
            ```

            `record.getMessage()` fills in the `%s` placeholders with the arguments. That's
            the finished message.

            Watch out: `record.msg` is the raw template (`"disk at %s%%"`), not the final text.
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
            ## Adding up the receipts

            One request's cost is a receipt. At the end of the day you want the totals: how many
            requests, how many tokens, how many dollars. Different models have different
            prices, so you keep a **price table**: a dict from model name to its prices.

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
            ```

            This is **cost accounting**. Teams use it to set budgets and alerts, and to see
            which feature eats the bill.

            Watch out: a model missing from the price table should fail **loudly** with a
            clear message. Silently counting it as free hides real spending.
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
            ## Black marker on the form

            Logging a whole request dict is tempting: it has everything you need to debug. It
            also has the `Authorization` header and maybe an `api_key`. Before logging, run the
            dict past someone with a **black marker** who blacks out the secret fields.

            ```python
            SECRET = {"api_key", "authorization", "password"}
            request = {"model": "gpt-4o", "Authorization": "Bearer sk-123"}
            safe = {}
            for key, value in request.items():
                safe[key] = "***" if key.lower() in SECRET else value
            print(safe)
            print(request["Authorization"])
            ```

            Two details: header names come in any case (`Authorization`, `authorization`), so
            compare with `key.lower()`. And build a **new** dict: the real request still needs
            the real key to be sent.

            Watch out: `request[key] = "***"` inside the loop would change the caller's dict
            and break the actual API call.
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

            One request is a tree of steps: `answer` contains `retrieve` and `llm_call`. A
            **tracer** records every span and who its parent is, so you can draw that tree and
            see where time went. This is what OpenTelemetry does, in miniature: keep a stack of
            open spans - the top of the stack is the parent of any new span.
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

            In production every model call gets the same treatment: time it, count tokens and
            cost, log one structured line with secrets removed, and log errors loudly before
            re-raising them. Wrapping that in one function means no call slips through
            unobserved.
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
