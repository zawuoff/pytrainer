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
            ## Choose which events belong in the log

            A request failed while nobody was watching the server. You need a record of what happened, but recording every small detail can bury the important events. Give each event a severity and choose how much detail to keep.

            ```python
            import logging, sys
            logging.basicConfig(stream=sys.stdout, level=logging.WARNING,
                                format="%(levelname)s %(message)s")
            report = logging.getLogger("worker")
            report.info("job started")
            report.warning("job is waiting")
            # WARNING job is waiting
            report.error("job failed")
            # ERROR job failed
            ```

            The information message is below the chosen threshold, so it produces no output. The warning and error are at or above it, and appear in the order the calls were made.

            A saved record of program events is a **log**. The object you send events to is a **logger**. Python's logging module provides named loggers, so records can identify which part of the application produced them. Messages have **levels**, ordered from debug through info, warning, error and critical. The configured level is the lowest severity you want to see.

            `basicConfig` sets up default output handling when the root logger has no handlers yet. The root logger is the top-level logger; messages from named loggers normally reach its handlers too. The format chooses which fields appear. Here the stream is standard output so you can see and predict the printed lines.

            ```match
            DEBUG :: detail used while investigating
            INFO :: an ordinary event
            ERROR :: an operation failed
            ---
            A level classifies the event; the configured threshold decides whether it is emitted.
            ```


            Try one more small check before moving to the task.

            ```predict
            import logging
            print(logging.ERROR >= logging.WARNING)
            ---
            An error is more serious than a warning, so it passes a warning-level threshold.
            ```

            **Watch out:** A filtered event does not print an empty line. It contributes no output at all. In an already-configured app, basicConfig may leave existing handlers in place.

            **In short:** Log levels let you keep important events while filtering less useful detail.
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

            Follow each printed line in execution order. Changes to a variable affect later lines; they do not change output that was already printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Find the configured threshold before following the logging calls.",
            "Compare each message severity with that threshold and preserve execution order.",
            "For each call decide whether it is emitted, then apply the format only to emitted messages.",
        ],
    },
    {
        "id": "observability-s2",
        "title": "Levels are numbers",
        "difficulty": 0,
        "lesson": r'''
            ## Use severity names instead of unexplained numbers

            You want HTTP failures to stand out in a log. Python compares severity using numbers, but a reader of your code should see the reason for the number. The logging module gives those values meaningful names.

            ```python
            import logging
            print(logging.INFO, logging.ERROR)
            # 20 40
            print(logging.WARNING < logging.ERROR)
            # True
            print(logging.getLevelName(logging.WARNING))
            # WARNING
            ```

            The values are ordinary integers. Their increasing order means more serious events pass a less serious threshold. The names make an intended category visible without requiring the reader to memorise the numbers.

            These names are **constants**: module attributes used as agreed fixed values. A function can return a logging constant exactly as it can return any integer. The caller then uses that value when deciding how to report an event.

            An HTTP status and a logging level are different kinds of numbers. The status describes a response, while the level describes how your application will report it. Mapping between them is an application policy, not a mathematical conversion. In this exercise, server errors get one severity, client errors another, and lower statuses the ordinary-event severity. Check the boundaries as well as typical statuses: a rule starting at 500 includes 500 itself.

            ```quiz
            Why return logging.WARNING rather than writing 30 directly?
            - [x] The name states the intended severity. :: Both values are the same integer, but the named constant explains its purpose.
            - [ ] The named constant has a different numeric value. :: logging.WARNING already refers to the integer 30.
            ```


            Try one more small check before moving to the task.

            ```predict
            import logging
            print(type(logging.INFO).__name__)
            ---
            A named severity constant is an integer value, rather than the text INFO.
            ```

            **Watch out:** Do not return the text "ERROR" when a logging level integer is required. Names, displayed labels and numeric values are distinct.

            **In short:** Named logging constants give numeric severity values a clear meaning.
        ''',
        "prompt": r'''
            Some HTTP responses deserve more attention in the logs. Complete the supplied gaps so each stated range gets the appropriate severity.

            **Your job:** `level_for_status(status)`

            **What goes in**
            - `status`: an int HTTP status code, e.g. `200`, `429`, `503`

            **What comes out**
            - a logging level constant (an int)

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
            "Look at which branch corresponds to an ordinary response and which to a server failure.",
            "Each branch must return a logging constant, not the HTTP code or a string.",
            "Match each stated status range to its required severity and check the boundary statuses against the completed branches.",
        ],
    },
    {
        "id": "observability-s3",
        "title": "A structured log line",
        "difficulty": 0,
        "lesson": r'''
            ## Write records a program can read

            You want to count how many requests waited more than a second. A sentence in a log makes that awkward. Named fields in JSON let another program read the delay without guessing where it appears in the sentence.

            ```python
            import json
            details = {"wait_ms": 450, "queue": "batch"}
            entry = {"kind": "queued", **details}
            encoded = json.dumps(entry, sort_keys=True)
            print(encoded)
            # {"kind": "queued", "queue": "batch", "wait_ms": 450}
            print(json.loads(encoded)["wait_ms"])
            # 450
            ```

            The dictionary holds separate values under stable names. Serialising it produces a single string, and parsing that string gives those values back. A tool can now filter by wait_ms without relying on the prose of a message.

            A log containing such named fields is called a **structured log**. JSON is a common format because many tools can parse it. Sorting its keys makes the displayed order predictable; it does not change what the keys mean.

            The double-star expression adds the fields into a new dictionary. The original details dictionary remains available for the rest of the application. That separation matters because logging should not alter the request it describes. Dictionary construction order also matters if two entries have the same key: the later value wins. The task's examples use distinct fields, so no collision needs to be resolved there.

            ```predict
            import json
            text = json.dumps({"z": 3, "a": 8}, sort_keys=True)
            print(text)
            print(json.loads(text)["z"])
            ---
            Sorted keys affect the JSON text order. Parsing still retrieves z by its name, with value 3.
            ```


            Try one more small check before moving to the task.

            ```predict
            import json
            print(json.loads('{"n": 7}')["n"])
            ---
            Parsing restores the named value as an integer, allowing a program to read it directly.
            ```

            **Watch out:** Changing the caller's dictionary to add a log field can change later application behaviour. Build a separate record instead.

            **In short:** Structured logs preserve named values in text that other programs can parse.
        ''',
        "prompt": r'''
            A monitoring tool needs named event fields. Encode a separate log record as one JSON string.

            **Your job:** `log_line(event, fields)`

            **What goes in**
            - `event`: a string, the event name, e.g. `"llm_call"`
            - `fields`: a dict of extra data, e.g. `{"model": "gpt-4o", "tokens": 120}`

            **What comes out**
            - a JSON string of one object holding `"event"` plus all of `fields`

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
            "Recall how a Python dictionary becomes JSON text.",
            "Create a separate record so adding the event name does not alter the input fields.",
            "Combine the event and extra fields in a fresh dictionary, serialise it with the required key ordering and spacing, and return the resulting string.",
        ],
    },
    {
        "id": "observability-s4",
        "title": "Fix: negative latency",
        "difficulty": 0,
        "lesson": r'''
            ## Measure elapsed time with two clock readings

            A request starts at one clock reading and ends at another. You want the time spent between them, not the clock's absolute value. A fake clock lets you practise that calculation without waiting or getting different answers on each run.

            ```python
            readings = iter([20.0, 20.125])
            clock = lambda: next(readings)
            first = clock()
            second = clock()
            print(second - first)
            # 0.125
            print((second - first) * 1000)
            # 125.0
            ```

            The later reading minus the earlier one is the elapsed time in seconds. Multiplying by a thousand converts seconds to milliseconds. Reversing the subtraction changes the sign and produces a negative duration.

            Passing the clock into a function is **dependency injection**. You already did this with fake models: the caller supplies a replaceable piece of behaviour. In production, `time.perf_counter` provides a clock suitable for elapsed-time measurements. Its starting point is unspecified, so a reading alone is not a calendar timestamp.

            In the example, an iterator hands out the two chosen readings. Each clock call advances to the next reading. This makes the order visible and testable. A timed operation belongs between the readings. Reading twice before the operation, or twice afterward, measures the wrong interval even if the subtraction is in the correct direction.

            ```quiz
            The readings are in seconds. How do you express their difference in milliseconds?
            - [x] Multiply the difference by 1000. :: A second contains one thousand milliseconds, so the numeric duration becomes larger.
            - [ ] Divide the difference by 1000. :: That conversion moves from milliseconds to seconds instead.
            ```


            Try one more small check before moving to the task.

            ```predict
            print((4.5 - 4.0) * 1000)
            ---
            Half a second becomes five hundred milliseconds after unit conversion.
            ```

            **Watch out:** A negative elapsed time often means the two readings were subtracted in the wrong order. Check the operation order too, not only the arithmetic.

            **In short:** Read the clock before and after the call, then convert the forward difference.
        ''',
        "prompt": r'''
            The supplied timing function reports a negative duration. Correct its timing behaviour while preserving the result of the wrapped call.

            **Your job:** `timed_call(fn, clock)`

            **What goes in**
            - `fn`: a function with no arguments; its return value is the result
            - `clock`: a function with no arguments returning the current time in seconds (float)

            **What comes out**
            - a tuple `(result, elapsed_ms)`: what `fn()` returned, and the time
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
            "Which reading represents the end, and which represents the start?",
            "The duration must measure the interval containing the function call.",
            "Preserve the clock-call and function-call order, subtract the earlier reading from the later one, and convert the seconds to milliseconds.",
        ],
    },
    {
        "id": "observability-s5",
        "title": "What did that call cost?",
        "difficulty": 0,
        "lesson": r'''
            ## Keep input and output costs separate

            Your bill counts the text you send and the text the model generates at different rates. A single total token count loses that distinction. Calculate each part using its own quoted rate before adding them.

            ```python
            sent, received = 2500, 500
            send_rate, receive_rate = 2.0, 8.0
            send_cost = sent * send_rate / 1_000_000
            receive_cost = received * receive_rate / 1_000_000
            print(round(send_cost + receive_cost, 6))
            # 0.009
            ```

            These are hypothetical rates in dollars per million tokens. They are data for the example, rather than current provider prices. The input part costs 0.005 dollars and the output part costs 0.004 dollars.

            A rate **per million** means that one token costs one millionth of the quoted amount. Multiplying a token count by that unit cost gives its contribution to the request. The underscore in `1_000_000` only improves readability; Python treats it as the same integer as 1000000.

            This calculation is **cost accounting**: translating recorded usage into spending. It is useful for identifying expensive requests and enforcing budgets. Keep full precision while calculating the separate parts, then round the combined amount at the reporting boundary. Zero tokens contribute zero cost, even when the associated rate is nonzero. A float is a numeric result; displaying trailing zeroes would be a separate formatting choice.

            ```fill
            tokens = 500_000
            price_per_million = 6
            print(tokens * price_per_million / ___)
            ---
            - [x] 1_000_000 :: Half a million tokens at six dollars per million costs three dollars.
            - [ ] 1000 :: A per-million rate must be scaled by a million, not a thousand.
            ```


            Try one more small check before moving to the task.

            ```predict
            print(500_000 * 4 / 1_000_000)
            ---
            Half a million tokens at a hypothetical four dollars per million cost two dollars.
            ```

            **Watch out:** Using the output rate for both counts, or omitting the per-million conversion, gives a plausible-looking but incorrect bill.

            **In short:** Price input and output separately, convert the quoted units, then add and round.
        ''',
        "prompt": r'''
            Calculate the cost of a request using the input and output prices supplied by the caller. These rates are dollars per million tokens.

            **Your job:** `request_cost(input_tokens, output_tokens, input_price, output_price)`

            **What goes in**
            - `input_tokens`, `output_tokens`: ints, e.g. `1200` and `300`
            - `input_price`, `output_price`: floats, dollars **per million** tokens, e.g. `2.5` and `10.0`

            **What comes out**
            - a float, the total cost in dollars, rounded to 6 decimals

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
            "Check what unit each quoted price uses.",
            "Input and output have separate rates, so each needs its own contribution.",
            "Calculate the two dollar contributions in per-token units, add them, and round the final total to the requested precision.",
        ],
    },
    {
        "id": "observability-s6",
        "title": "Redact API keys",
        "difficulty": 0,
        "lesson": r'''
            ## Remove matching secrets before writing text

            A diagnostic message includes an API key. Once the message reaches a log, other people and systems may copy it. Replace recognised secrets before writing the message, while leaving the useful surrounding text intact.

            ```python
            import re
            note = "session=tok-AB12CD34 ready"
            print(re.sub(r"tok-[A-Z0-9]{8,}", "[HIDDEN]", note))
            # session=[HIDDEN] ready
            print(re.sub(r"tok-[A-Z0-9]{8,}", "[HIDDEN]", "tok-A1 short"))
            # tok-A1 short
            ```

            The example pattern has a fixed prefix, a permitted character set and a minimum length. The first token matches the entire pattern, so the replacement covers it completely. The shorter text does not meet the length rule and remains visible.

            Replacing sensitive content with a placeholder is called **redaction**. `re.sub` returns a new string with all matching occurrences replaced. It does not change the original string or only stop at the first match.

            The real exercise supplies a different prefix and character set. Translate its stated pattern carefully rather than assuming every hyphenated word is a key. The length applies after the prefix, so count the suffix when checking a boundary example. This recognises one specified secret format. It cannot promise that every possible provider key or password has been removed. Avoid logging sensitive inputs where possible; use redaction as an additional control.

            ```quiz
            A message has three tokens matching the pattern. How many does re.sub replace by default?
            - [x] All three. :: Without a count limit, substitution replaces every non-overlapping match.
            - [ ] Only the first. :: Replacing one match would leave the other matching secrets visible.
            ```


            Try one more small check before moving to the task.

            ```predict
            import re
            print(re.sub(r"tok-[0-9]{3}", "X", "tok-123 tok-456"))
            ---
            Substitution replaces both matching tokens, not just the first.
            ```

            **Watch out:** Redacting after a message is written cannot remove copies already made. Sanitize the text before emitting it.

            **In short:** Replace every recognised secret before logging, and keep the pattern limits explicit.
        ''',
        "prompt": r'''
            A message may contain several API keys. Replace the specified key format before that text is logged.

            **Your job:** `redact_keys(text)`

            **What goes in**
            - `text`: a string that may contain API keys

            **What comes out**
            - the same text with every key replaced by `[REDACTED]`

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
            "Recall the regex operation that returns text with all matches replaced.",
            "The suffix has both a permitted character set and a minimum length.",
            "Build the stated whole-key pattern, replace every match with the required placeholder, and return the new text without changing nonmatches.",
        ],
    },
    {
        "id": "observability-s7",
        "title": "Context managers: enter and exit",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Run cleanup when a block ends

            You want to record the end of an operation even if its body raises an error. A pair of ordinary calls is easy to separate accidentally. Python's with statement groups the operation with its entry and exit behaviour.

            ```python
            class Marker:
                def __enter__(self):
                    print("begin")
                    return "work"
                def __exit__(self, kind, value, trace):
                    print("finish", kind is None)
                    return False
            with Marker() as label:
                print(label)
            # begin
            # work
            # finish True
            ```

            The with statement calls the entry method first and binds its returned value to label. Then it runs the indented body. After that, it calls the exit method. The example has no exception, so kind is None.

            An object supporting this pair of methods is a **context manager**. You have already used one when opening files. Its exit method receives the exception type, exception value and traceback if an error is leaving the body. A traceback records where the error came from. When there is no error, all three values are None.

            An exit method returning False allows an error to continue to the caller. Returning True suppresses it, which is a significant behaviour change. Timing and tracing helpers normally observe the outcome rather than hiding failures. Follow the method-call order when predicting output: entry, body, exit, and only then any following statement.

            ```match
            __enter__ :: starts the managed block
            value returned by __enter__ :: the value bound after as
            __exit__ :: runs when the managed block ends
            ---
            The with statement coordinates these parts even when the body exits with an exception.
            ```


            Try one more small check before moving to the task.

            ```predict
            print(None is None)
            print(ValueError is None)
            ---
            The exit method sees None for no exception and an exception class for an error.
            ```

            **Watch out:** The object after as is whatever the entry method returns. It is only the manager itself when the method explicitly returns self.

            **In short:** A context manager brackets a block with entry and exit behaviour.
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

            Follow each printed line in execution order. Changes to a variable affect later lines; they do not change output that was already printed.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "List the entry, body and exit phases before reading the print calls.",
            "Work out what __enter__ returns and whether an exception reaches __exit__.",
            "Follow the calls in execution order, bind the returned entry value, then evaluate the exit message before the final statement.",
        ],
    },
    {
        "id": "observability-1",
        "title": "Latency percentile",
        "difficulty": 1,
        "lesson": r'''
            ## Describe the slow end of your requests

            Most requests feel quick, but occasionally one waits a long time. The average alone can hide what users experience. You want a value that describes the typical request and another that describes the slow end of the list.

            ```python
            import math
            samples = [20, 40, 30, 800, 10]
            ordered = sorted(samples)
            position = math.ceil(80 * len(ordered) / 100)
            print(ordered)
            # [10, 20, 30, 40, 800]
            print(ordered[position - 1])
            # 40
            ```

            Four of the five observations are at or below 40. The example takes 80 percent of the list length, rounds the position upward, and reads that position in the sorted list. Positions start at one, while list indexes start at zero.

            A **percentile** names a point in an ordered set of measurements. **Latency** is the time a request takes. You will often see p50 for a typical latency and p95 for the slow end. Different percentile methods can differ on small datasets; this task uses the **nearest-rank** method, not interpolation between neighbouring values.

            Sort a copy so reporting does not reorder the caller's data. The endpoint at zero percent needs the smallest item rather than a zero position. An empty dataset has no observed value at any position, so the specified error is more honest than inventing a zero latency.

            ```quiz
            A computed rank is 4. Which list index reads that position?
            - [x] 3 :: Positions count from one, but indexes count from zero.
            - [ ] 4 :: That index reads the fifth item and would shift the percentile upward.
            ```


            Try one more small check before moving to the task.

            ```predict
            import math
            print(math.ceil(2.5))
            ---
            Nearest-rank positions use upward rounding, so a fractional position of 2.5 becomes three.
            ```

            **Watch out:** Subtracting one from a zero rank gives index -1, which selects the largest value. Enforce the specified minimum position before indexing.

            **In short:** A nearest-rank percentile selects a measured value at an agreed sorted position.
        ''',
        "prompt": r'''
            Users experience the distribution of request times, not only their average. Select a measured latency using the specified percentile method.

            **Your job:** `percentile(values, p)`

            **What goes in**
            - `values`: a list of numbers (latencies in ms), in any order, e.g. `[120, 80, 950, 100]`
            - `p`: a number from 0 to 100, e.g. `50` or `95`

            **What comes out**
            - one of the values: sort them, compute `rank = ceil(p * n / 100)`
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
            "Distinguish a one-based rank from a zero-based index.",
            "Work with a sorted copy and account for both the empty list and zero-percent endpoint.",
            "Reject empty data, compute the rounded-up position with the specified minimum, and read the corresponding index from the copy.",
        ],
    },
    {
        "id": "observability-2",
        "title": "A timing span",
        "difficulty": 1,
        "lesson": r'''
            ## Record one named operation and its outcome

            Your RAG request feels slow. You need to tell whether retrieval or answer generation used the time. Give each operation a name, measure its duration, and remember whether it completed or failed.

            ```python
            from contextlib import contextmanager
            @contextmanager
            def observed(label):
                print("begin", label)
                try:
                    yield
                finally: print("end", label)
            with observed("fetch"):
                print("working")
            # begin fetch
            # working
            # end fetch
            ```

            The decorator is a standard-library shortcut for building a context manager from a generator. Code before yield runs on entry; code after it resumes when the body exits. The finally branch runs even when the body raises. Your task builds a class using the entry and exit methods taught in the previous step instead.

            A record for one named operation is a **span**. It combines an operation name with timing and outcome. Entry stores the first clock reading; exit has the information needed to finish the record. Before exit, the completed duration and status are not known.

            When an exception leaves the body, record an error status while preserving the exception for the caller. Observability should tell you what failed without quietly changing whether the application failed. An injected clock keeps duration tests repeatable, just as it did for the earlier timing function.

            ```quiz
            An operation raises TimeoutError. What should an observing span do?
            - [x] Record failure and let the error continue. :: The record explains the outcome while the caller still receives the failure.
            - [ ] Mark success and suppress the error. :: That would hide the application failure and make the trace misleading.
            ```


            **Watch out:** Returning True from __exit__ suppresses an exception. A recorder that should preserve failures needs a false result instead.

            **In short:** A span records the duration and outcome of one named operation without hiding errors.
        ''',
        "prompt": r'''
            Measure one named operation and keep its success or error status available after the block ends.

            **Your job:** a class `Span` used as `with Span(name, clock) as span:`

            **What goes in**
            - `Span(name, clock)`: `name` is a string; `clock` is a function returning seconds (float)
            - Attributes: `name`; `duration_ms` and `status`, both `None` until the block ends
            - `__enter__` reads `clock()` once and returns the span itself
            - `__exit__` reads `clock()` once more, sets `duration_ms` = (end - start) * 1000
              rounded to 3 decimals, and sets `status` to `"ok"` or `"error"`

            **What comes out**
            - The context binds the `Span` object itself. Its `name` stays available. Before exit, `duration_ms` and `status` are `None`; afterward they describe the rounded milliseconds and `"ok"` or `"error"` outcome.

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
            "Use the context-manager lifecycle to decide when each attribute becomes known.",
            "The entry method starts measurement; the exit method sees both the end reading and any exception.",
            "Initialise pending attributes, store the start reading on entry, complete the rounded duration and status on exit, and preserve error propagation.",
        ],
    },
    {
        "id": "observability-3",
        "title": "JSON log formatter",
        "difficulty": 1,
        "lesson": r'''
            ## Separate the event from its displayed form

            Your application already uses Python logging, but another tool needs JSON records. You should be able to change how messages are displayed without rewriting every logging call. Put that conversion in the formatting stage.

            ```python
            import logging
            record = logging.LogRecord("queue", logging.WARNING, "demo", 1,
                                       "waiting for %s jobs", (4,), None)
            print(record.msg)
            # waiting for %s jobs
            print(record.getMessage())
            # waiting for 4 jobs
            ```

            The record stores a message template and its arguments separately. `getMessage` combines them into the finished text. Reading the template alone loses the arguments, as the first printed line shows.

            A **LogRecord** holds event data such as the level, logger name and message. A **handler** sends records to a destination. A **formatter** turns each record into text for that handler. These roles let the same event be written in different formats or sent to different destinations.

            To customise formatting, subclass logging.Formatter and implement its format method. The method returns text; it does not print that text itself. For structured logging, gather the requested fields and encode them with the JSON module. The handler handles writing the returned string. This keeps JSON generation separate from both the original event and the output stream.

            ```fill
            import logging
            r = logging.LogRecord("q", 20, "demo", 1, "items=%s", (6,), None)
            print(r.___())
            ---
            - [x] getMessage :: This method fills the stored argument into the template.
            - [ ] getName :: LogRecord has no getName method for formatting its message.
            ```


            **Watch out:** Using record.msg can leave placeholders in the log. Using print inside format can also duplicate output because the handler writes the returned result.

            **In short:** A formatter converts a completed log record into text for the handler to write.
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
            Keep ordinary logging calls while changing their displayed output to JSON. Implement the formatting stage.

            **Your job:** a class `JsonFormatter`, a subclass of `logging.Formatter`

            **What goes in**
            - A logging record supplied to `format(self, record)`, including its severity, logger name, message template and arguments.

            **What comes out**
            - `format(record)` returns one JSON string containing exactly `level`, `logger` and `message`, with the message arguments filled in.

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
            "Identify where logging turns a record into its output string.",
            "The three requested values already belong to the record, but the message must have its arguments filled.",
            "Subclass the formatter, obtain the level, logger and finished message, encode exactly those fields as JSON, and return the string.",
        ],
    },
    {
        "id": "observability-4",
        "title": "Usage summary",
        "difficulty": 1,
        "lesson": r'''
            ## Add up usage using each model's rates

            A day's requests used several models. Adding token counts is straightforward, but cost needs the price for each model used. Keep usage totals separate from the lookup that prices each record.

            ```python
            rates = {"basic": 2.0, "premium": 5.0}
            rows = [("basic", 2000), ("premium", 1000)]
            spent = 0.0
            for name, count in rows:
                spent += count * rates[name] / 1_000_000
            print(sum(count for name, count in rows))
            # 3000
            print(round(spent, 6))
            # 0.009
            ```

            The token total ignores the model name, but the dollar total cannot. The lookup makes a thousand premium tokens contribute more than a thousand basic tokens. These are illustrative rates, and the task will supply its own table.

            A **price table** maps model identifiers to rates. Your report combines this lookup with the request-cost calculation from earlier. Real records have separate input and output counts, so preserve both totals and use the appropriate rate for each contribution.

            A missing rate is incomplete accounting data. Counting that request as free would make the report look authoritative while understating spending. Raise the specified error so the caller can fix the table. Round the final combined cost rather than rounding every request first, because repeated early rounding can lose small amounts. For no requests, the natural counts are zero and the task defines the dollar total as zero too.

            ```predict
            rates = {"a": 1, "b": 4}
            print(1000 * rates["a"] / 1_000_000)
            print(1000 * rates["b"] / 1_000_000)
            ---
            Equal token counts can cost different amounts. Each request must use the rate associated with its model.
            ```


            **Watch out:** A missing model price must not silently become zero. The report needs a clear failure rather than a hidden underestimate.

            **In short:** Sum token counts directly, but price each record with its own model's rates.
        ''',
        "prompt": r'''
            A usage report must price each model correctly. Return combined counts and cost for the supplied requests.

            **Your job:** `summarize_usage(requests, prices)`

            **What goes in**
            - `requests`: a list of dicts like `{"model": "small", "input_tokens": 1000, "output_tokens": 500}`
            - `prices`: a dict like `{"small": {"input": 0.15, "output": 0.60}}`, dollars per million tokens

            **What comes out**
            - a dict
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
            "Which totals can be added directly, and which depend on the model?",
            "Check the price table before adding the request's dollar contribution.",
            "Start empty totals, validate and price each record, accumulate both token directions and request count, then round the combined cost.",
        ],
    },
    {
        "id": "observability-5",
        "title": "Redact secret fields",
        "difficulty": 1,
        "lesson": r'''
            ## Hide a secret field without breaking the request

            The same request dictionary will be used for an API call and a diagnostic record. You want the record to hide a password, but the API call still needs its original credentials. Build a sanitised copy for the log.

            ```python
            request = {"name": "batch", "Secret": "example"}
            hidden_names = {"secret"}
            copy = {}
            for field, value in request.items():
                copy[field] = "***" if field.lower() in hidden_names else value
            print(copy)
            # {'name': 'batch', 'Secret': '***'}
            print(request["Secret"])
            # example
            ```

            Each original key is preserved. Lowercasing is used only for deciding whether the key names a secret; the stored key keeps its spelling. Ordinary values pass through unchanged, and secret values become the placeholder.

            This is **field-based redaction**. Unlike the earlier text pattern, it recognises sensitive data from the field name. That works when you know which fields may contain secrets, even if their values do not resemble a particular provider's key format.

            The new dictionary avoids changing the caller's request. This is a shallow operation: if a non-secret field contains a nested object, it is not recursively inspected or copied. The task explicitly describes a flat dictionary, so do not infer a nested-data guarantee from it. A custom list of secret names lets the caller apply the same mechanism to another set of fields.

            ```quiz
            A sanitised record keeps a key named Password. What happens to the original key spelling?
            - [x] It stays Password. :: The lowercase form is used for classification, while the new dictionary preserves the original key.
            - [ ] It must become password. :: Changing spelling is not required for hiding the value and alters the record shape.
            ```


            **Watch out:** Assigning placeholders into the original dictionary changes the credentials used by later code. Keep the diagnostic copy separate.

            **In short:** Classify fields without regard to case and hide their values in a new dictionary.
        ''',
        "prompt": r'''
            Keep the usable request intact while producing a separate dictionary suitable for a diagnostic record.

            **Your job:** `redact_fields(data, secret_keys=("api_key", "authorization", "password"))`

            **What goes in**
            - `data`: a flat dict, e.g. `{"model": "gpt-4o", "Authorization": "Bearer sk-1"}`
            - `secret_keys`: a tuple of lowercase key names to hide

            **What comes out**
            - a **new** dict with the same keys; the value of every secret key is
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
            "Look at the field names rather than the shape of their values.",
            "Use a normalised name for the decision while preserving the original key in the result.",
            "Walk the input fields, choose the placeholder for secret names and the original value otherwise, and collect them in a fresh dictionary.",
        ],
    },
    {
        "id": "observability-6",
        "title": "Latency report",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A dashboard needs typical and slow-request latency values from the same batch. Return the specified summary.

            **Your job:** `latency_report(durations_ms)`

            **What goes in**
            - `durations_ms`: a list of numbers (milliseconds), any order

            **What comes out**
            - a dict `{"count": int, "p50": ..., "p95": ..., "max": ...}`

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
            "Percentiles need the ordered observations, not the average.",
            "Preserve the caller's list and calculate each requested position using the chapter's method.",
            "Reject the empty dataset, make an ordered copy, determine the bounded one-based positions for both percentiles, and return their values in the specified report.",
        ],
    },
    {
        "id": "observability-7",
        "title": "Deep redaction",
        "difficulty": 2,
        "prompt": r'''
            A diagnostic record can contain dictionaries and lists inside other records. Return a sanitised copy of the complete supported structure.

            **Your job:** `redact_deep(value)`

            **What goes in**
            - `value`: any JSON-like value: a dict, list, string, number, bool or `None`,
              possibly nested

            **What comes out**
            - a **new** value of the same shape with secrets hidden

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
            "Secret fields and secret-looking string contents need different checks.",
            "Decide how to treat dictionaries, lists, strings and all other values before recursing.",
            "Copy dictionaries and lists while sanitising their contents; replace whole secret fields, substitute matching keys in strings, and preserve other scalar values.",
        ],
    },
    {
        "id": "observability-8",
        "title": "A tracer with nested spans",
        "difficulty": 3,
        "lesson": r'''
            ## Remember which operation contains another

            One answer request retrieves documents and then calls a model. Retrieval may itself contain another operation. A flat duration list loses that relationship. Record which operation was active when each new operation began.

            ```python
            open_steps = ["answer"]
            print(open_steps[-1])
            # answer
            open_steps.append("lookup")
            print(open_steps[-1])
            # lookup
            open_steps.pop()
            print(open_steps[-1])
            # answer
            ```

            The end of the list represents the innermost active operation. Adding a name opens an operation; removing it closes that operation and restores the containing one. You have used this last-in-first-out structure before; it is a **stack**.

            A group of connected spans for one request is a **trace**. The containing span is the **parent** of a new span. Putting it together means combining the earlier context-manager timing with a stack maintained by the recorder. Capture a parent when the span opens, before pushing its own name.

            Finished spans belong in the report when their blocks end. A child therefore finishes before its parent. The report's completion order is different from its start order, and both can be useful. An error must still close the active span and restore the stack; otherwise a later unrelated operation could be incorrectly recorded as its child. Return control to the caller with the original error after recording it.

            ```predict
            active = ["request", "fetch"]
            active.pop()
            print(active[-1])
            ---
            Closing fetch restores request as the innermost active operation.
            ```


            **Watch out:** A stack entry left behind after an exception gives later spans the wrong parent. Exit processing must restore the active-operation stack on failures too.

            **In short:** A trace links timed spans by their parents and records them as they finish.
        ''',
        "prompt": r'''
            An operation can contain smaller operations. Record completed durations together with those parent relationships.

            **Your job:** a class `Tracer`

            **What goes in**
            - `Tracer(clock)`: `clock` is a function returning seconds (float)
            - `tracer.span(name)` returns a context manager for use in `with tracer.span("retrieve"):`
            - `tracer.spans`: a list of finished spans, each a dict
              `{"name": str, "parent": str or None, "duration_ms": float, "status": "ok" or "error"}`

            **What comes out**
            - `span(name)` returns a context manager. After blocks finish, `spans` holds records with `name`, `parent`, `duration_ms` and `status`, in completion order.

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
            "Separate the active-operation stack from the finished-span list.",
            "A span learns its parent when it opens, but its duration when it closes.",
            "On entry capture the current parent and start time before opening the new span; on exit restore the stack, record duration and outcome, and preserve the exception.",
        ],
    },
    {
        "id": "observability-9",
        "title": "An instrumented LLM call",
        "difficulty": 3,
        "lesson": r'''
            ## Give every model call the same reporting boundary

            Different parts of your app call the model. If each invents its own logging, some requests will have usage but no timing, or errors but no context. Route them through one function that records a consistent result on success and failure.

            ```python
            import json
            safe_prompt = "question with [HIDDEN]"
            entry = {"kind": "response", "elapsed_ms": 25.0,
                     "prompt": safe_prompt}
            print(json.dumps(entry, sort_keys=True))
            # {"elapsed_ms": 25.0, "kind": "response", "prompt": "question with [HIDDEN]"}
            ```

            This small record demonstrates the reporting boundary: structured data is converted to text after its sensitive field has been sanitised. The model's actual input and the diagnostic copy have different purposes, so do not accidentally send the sanitised copy when the contract promises the original input.

            Putting it together means coordinating the injected clock, price lookup, usage data, redaction and log level. Sketch two paths. The successful path has returned usage to price and answer text to return. The error path has an exception class to report, then must let that same exception continue to the caller.

            Both paths need a second clock reading and exactly one log event of their specified level. Avoid logging the raw prompt on either path. Also keep unavailable pricing distinct from a successful free call; the absence of a rate is a data problem. The supplied functions, logger and clock allow all of these effects to be checked without a network request.

            ```quiz
            The model raises an exception. Should the wrapper return an empty successful answer?
            - [x] No; it records the error and re-raises. :: The caller still needs to know that the model operation failed.
            - [ ] Yes; recording a log makes the failure handled. :: A diagnostic event does not turn a failed model call into a successful reply.
            ```


            **Watch out:** A broad success log in a finally block can report a failed call as successful. Keep success and error event construction separate.

            **In short:** One wrapper coordinates timing, safe logs and cost while preserving the model's outcome.
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
            Make model calls consistently observable. Wrap one call with timing, usage accounting and the specified success or error log.

            **Your job:** `traced_llm_call(llm, prompt, *, model, clock, logger, prices)`

            **What goes in**
            - `llm`: a function called as `llm(prompt)`; returns a dict
              `{"text": str, "input_tokens": int, "output_tokens": int}`
            - `prompt`: a string
            - `model`: a string, e.g. `"small"`
            - `clock`: a function returning seconds (float)
            - `logger`: a `logging.Logger`
            - `prices`: dict like `{"small": {"input": 0.15, "output": 0.60}}` (dollars per million tokens)

            **What comes out**
            - the reply's `"text"`

            **Rules**
            - Read `clock()` once right before calling `llm` and once right after it returns
              (or raises). `latency_ms` = (after - before) * 1000 rounded to 3 decimals.
            - On success, call `logger.info` once with a JSON string (one object) with keys:
              `event` equal to `"llm_call"`, `"model"`, `"latency_ms"`, `"input_tokens"`,
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
            # event=llm_call, model=small, "latency_ms": 500.0, "input_tokens": 1000,
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
            "List what is available on success and what is available when the call raises.",
            "Both paths measure latency, but they require different event fields and log levels.",
            "Measure around the one model call, record and re-raise failures, and otherwise price the usage, redact the diagnostic prompt, log success and return the answer.",
        ],
    },
]
