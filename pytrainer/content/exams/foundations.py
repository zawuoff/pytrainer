"""Module test: Python Foundations (basics -> errors)."""

EXAM = {
    "module": "foundations",
    "title": "Python Foundations: module test",
    "intro": r'''
        This is a **test**, not a lesson. It checks the whole Foundations module at once:
        variables, data types, conditionals, f-strings, lists, loops, dicts, functions and
        error handling, mixed together the way real code mixes them.

        **How it works**

        - There are **no hints and no tutor** while you take it. You get the prompt, the
          checks and your own knowledge.
        - Read each prompt slowly. Every rule the checks test is written in the prompt or
          visible in the examples.
        - Two exercises are *research* tasks: one gives you official doc links to read, the
          other asks you to find a standard-library tool yourself. Looking things up is
          allowed and expected - it's what working engineers do all day.

        **Passing**

        Pass at least **70%** of the exercises and the module counts as done: you can skip
        its chapters and move on. If you don't pass, nothing is lost - the chapters will
        show you exactly what to practise.
    ''',
    "pass_ratio": 0.7,
}

EXERCISES = [
    {
        "id": "exam-foundations-1",
        "title": "Token budget status",
        "difficulty": 2,
        "prompt": r'''
            An AI app shows the user how much of their monthly token budget they have used.

            **Write:** `budget_status(used, limit)`

            - `used`: tokens used so far, an `int`, e.g. `300`
            - `limit`: the monthly token limit, an `int`, e.g. `1000`
            - **Returns:** a string like `"ok: 300/1000 tokens (30%)"`

            **Rules**
            - The percentage is `used / limit * 100`, rounded with `round()` to a whole number.
            - The label is `"ok"` when the percentage (before rounding) is below 80,
              `"warning"` when it is 80 or more but `used` is not above `limit`,
              and `"over"` when `used` is greater than `limit`.
            - Format: `"<label>: <used>/<limit> tokens (<percent>%)"`.
            - If `limit` is `0` or negative, raise `ValueError` with the message
              `"limit must be positive"`.

            **Examples**
            ```python
            budget_status(300, 1000)    # returns "ok: 300/1000 tokens (30%)"
            budget_status(800, 1000)    # returns "warning: 800/1000 tokens (80%)"
            budget_status(1000, 1000)   # returns "warning: 1000/1000 tokens (100%)"
            budget_status(1500, 1000)   # returns "over: 1500/1000 tokens (150%)"
            budget_status(5, 0)         # raises ValueError("limit must be positive")
            ```
        ''',
        "starter": r'''
            def budget_status(used, limit):
                ...
        ''',
        "tests": r'''
            from solution import budget_status

            def test_low_usage_is_ok():
                got = budget_status(300, 1000)
                assert got == "ok: 300/1000 tokens (30%)", f"got {got!r}"

            def test_exactly_eighty_percent_is_warning():
                got = budget_status(800, 1000)
                assert got == "warning: 800/1000 tokens (80%)", f"got {got!r}"

            def test_just_below_eighty_percent_is_ok_even_if_it_rounds_to_80():
                got = budget_status(799, 1000)
                assert got == "ok: 799/1000 tokens (80%)", f"got {got!r}"

            def test_at_the_limit_is_warning_not_over():
                got = budget_status(1000, 1000)
                assert got == "warning: 1000/1000 tokens (100%)", f"got {got!r}"

            def test_above_limit_is_over():
                got = budget_status(1500, 1000)
                assert got == "over: 1500/1000 tokens (150%)", f"got {got!r}"

            def test_zero_or_negative_limit_raises_value_error():
                for bad in (0, -10):
                    try:
                        budget_status(5, bad)
                    except ValueError as e:
                        assert str(e) == "limit must be positive", f"message was {str(e)!r}"
                    else:
                        raise AssertionError(f"no ValueError for limit={bad}")
        ''',
        "solution": r'''
            def budget_status(used, limit):
                if limit <= 0:
                    raise ValueError("limit must be positive")
                percent = used / limit * 100
                if used > limit:
                    label = "over"
                elif percent >= 80:
                    label = "warning"
                else:
                    label = "ok"
                return f"{label}: {used}/{limit} tokens ({round(percent)}%)"
        ''',
        "hints": [
            "This combines an early error check, an if/elif/else chain and an f-string.",
            "Check the limit first and raise. Then compute the raw percentage, pick the label by testing the most specific case ('over') first, and only round when you build the string.",
            "1) If limit <= 0, raise ValueError with the exact message. 2) percent = used / limit * 100. 3) if used > limit: 'over'; elif percent >= 80: 'warning'; else 'ok'. 4) Return an f-string using round(percent) for the number.",
        ],
    },
    {
        "id": "exam-foundations-2",
        "title": "Words per role",
        "difficulty": 2,
        "prompt": r'''
            To see who is "talking" most in a chat, count the words each role wrote.

            **Write:** `words_by_role(messages)`

            - `messages`: a list of dicts, each with `"role"` (a string) and `"content"`
              (a string, or `None` for tool-call messages)
            - **Returns:** a dict mapping each role to the total number of words in its
              messages, e.g. `{"user": 5, "assistant": 12}`

            **Rules**
            - Words are what `.split()` gives you (split on any whitespace).
            - `None` content counts as 0 words, but its role still appears in the result.
            - Roles appear in the order they first occur in `messages`.
            - An empty list returns `{}`.
            - Don't change the list or the dicts you were given.

            **Examples**
            ```python
            words_by_role([
                {"role": "user", "content": "What is RAG?"},
                {"role": "assistant", "content": None},
                {"role": "assistant", "content": "Retrieval augmented generation."},
                {"role": "user", "content": "Thanks"},
            ])
            # returns {"user": 4, "assistant": 3}
            words_by_role([])   # returns {}
            ```
        ''',
        "starter": r'''
            def words_by_role(messages):
                ...
        ''',
        "tests": r'''
            from solution import words_by_role

            MSGS = [
                {"role": "user", "content": "What is RAG?"},
                {"role": "assistant", "content": None},
                {"role": "assistant", "content": "Retrieval augmented generation."},
                {"role": "user", "content": "Thanks"},
            ]

            def test_example_counts():
                got = words_by_role(MSGS)
                assert got == {"user": 4, "assistant": 3}, f"got {got!r}"

            def test_none_content_role_still_appears_with_zero():
                got = words_by_role([{"role": "tool", "content": None}])
                assert got == {"tool": 0}, f"got {got!r}"

            def test_roles_in_first_appearance_order():
                msgs = [{"role": "system", "content": "a"}, {"role": "user", "content": "b"},
                        {"role": "system", "content": "c"}, {"role": "assistant", "content": "d"}]
                got = list(words_by_role(msgs))
                assert got == ["system", "user", "assistant"], f"order was {got!r}"

            def test_extra_whitespace_does_not_create_words():
                got = words_by_role([{"role": "user", "content": "  hello \n  world  "}])
                assert got == {"user": 2}, f"got {got!r}"

            def test_empty_list():
                assert words_by_role([]) == {}

            def test_input_not_modified():
                msgs = [dict(m) for m in MSGS]
                words_by_role(msgs)
                assert msgs == MSGS, "the input was modified"
        ''',
        "solution": r'''
            def words_by_role(messages):
                counts = {}
                for message in messages:
                    role = message["role"]
                    content = message["content"]
                    words = 0 if content is None else len(content.split())
                    counts[role] = counts.get(role, 0) + words
                return counts
        ''',
        "hints": [
            "You need a loop, a dict that starts empty, and a way to count words in a string.",
            "For each message, work out how many words it has (0 for None), then add that to the running total for its role, creating the role's entry the first time you see it.",
            "1) counts = {}. 2) Loop over messages. 3) words = 0 if content is None, else len(content.split()). 4) counts[role] = counts.get(role, 0) + words. 5) Return counts.",
        ],
    },
    {
        "id": "exam-foundations-3",
        "title": "Total API cost",
        "difficulty": 3,
        "prompt": r'''
            Every LLM call reports its token usage. Prices are quoted **per million tokens**,
            with different prices for input and output.

            **Write:** `total_cost(usage, prices)`

            - `usage`: a list of dicts like `{"model": "small", "input_tokens": 1000, "output_tokens": 600}`
            - `prices`: a dict mapping model name to `{"input": <USD per 1M>, "output": <USD per 1M>}`,
              e.g. `{"small": {"input": 0.5, "output": 1.5}}`
            - **Returns:** the total cost in dollars as a `float`, rounded to 4 decimal places

            **Rules**
            - Cost of one call = `input_tokens * input_price / 1_000_000 + output_tokens * output_price / 1_000_000`.
            - Round only the final total (use `round(total, 4)`).
            - An empty `usage` list returns `0.0`.
            - If a call uses a model that is not in `prices`, raise `ValueError` with the
              message `"unknown model: <name>"`, e.g. `"unknown model: huge"`.

            **Examples**
            ```python
            prices = {"small": {"input": 0.5, "output": 1.5}, "big": {"input": 3, "output": 15}}
            total_cost([{"model": "small", "input_tokens": 1000, "output_tokens": 600}], prices)
            # returns 0.0014
            total_cost([
                {"model": "small", "input_tokens": 1000, "output_tokens": 600},
                {"model": "big", "input_tokens": 2000, "output_tokens": 1000},
            ], prices)
            # returns 0.0224
            total_cost([], prices)   # returns 0.0
            total_cost([{"model": "huge", "input_tokens": 1, "output_tokens": 1}], prices)
            # raises ValueError("unknown model: huge")
            ```
        ''',
        "starter": r'''
            def total_cost(usage, prices):
                ...
        ''',
        "tests": r'''
            from solution import total_cost

            PRICES = {"small": {"input": 0.5, "output": 1.5}, "big": {"input": 3, "output": 15}}

            def test_single_call():
                got = total_cost([{"model": "small", "input_tokens": 1000, "output_tokens": 600}], PRICES)
                assert got == 0.0014, f"got {got!r}"

            def test_two_models_added_together():
                got = total_cost([
                    {"model": "small", "input_tokens": 1000, "output_tokens": 600},
                    {"model": "big", "input_tokens": 2000, "output_tokens": 1000},
                ], PRICES)
                assert got == 0.0224, f"got {got!r}"

            def test_output_tokens_use_output_price():
                got = total_cost([{"model": "big", "input_tokens": 0, "output_tokens": 1_000_000}], PRICES)
                assert got == 15.0, f"got {got!r}"

            def test_rounds_only_the_total():
                usage = [{"model": "small", "input_tokens": 40, "output_tokens": 0}] * 3
                got = total_cost(usage, PRICES)
                assert got == 0.0001, f"got {got!r}"

            def test_empty_usage_is_zero():
                got = total_cost([], PRICES)
                assert got == 0.0 and isinstance(got, float), f"got {got!r}"

            def test_unknown_model_raises_value_error_with_name():
                try:
                    total_cost([{"model": "huge", "input_tokens": 1, "output_tokens": 1}], PRICES)
                except ValueError as e:
                    assert str(e) == "unknown model: huge", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for an unknown model")
        ''',
        "solution": r'''
            def total_cost(usage, prices):
                total = 0.0
                for call in usage:
                    model = call["model"]
                    if model not in prices:
                        raise ValueError(f"unknown model: {model}")
                    price = prices[model]
                    total += call["input_tokens"] * price["input"] / 1_000_000
                    total += call["output_tokens"] * price["output"] / 1_000_000
                return round(total, 4)
        ''',
        "hints": [
            "A loop with a running total, a dict lookup for the price, and an early raise for unknown models.",
            "Start total at 0.0. For every call, check the model is known, look up its prices, add both the input and the output cost. Round once at the very end.",
            "1) total = 0.0. 2) For each call: if call['model'] not in prices, raise ValueError(f'unknown model: ...'). 3) price = prices[model]. 4) total += input_tokens * price['input'] / 1_000_000, and the same for output. 5) return round(total, 4).",
        ],
    },
    {
        "id": "exam-foundations-4",
        "title": "Parse a temperature setting",
        "difficulty": 2,
        "research": {
            "note": "Before you start, read how the built-in `float()` turns strings into numbers "
                    "(including what it does with surrounding spaces and what it raises on bad input), "
                    "and how `try`/`except` lets you catch an error and raise your own instead.",
            "links": [
                {"title": "float() - Python built-in functions",
                 "url": "https://docs.python.org/3/library/functions.html#float"},
                {"title": "Handling exceptions - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/errors.html#handling-exceptions"},
            ],
        },
        "prompt": r'''
            A model's `temperature` often arrives as text from a form or config file, and it
            must be a number from 0 to 2.

            **Write:** `parse_temperature(value)`

            - `value`: a string like `"0.7"` or `" 1 "`, or already a number like `0.2` or `1`
            - **Returns:** the temperature as a `float`

            **Rules**
            - Surrounding spaces in a string are fine: `" 1.5 "` gives `1.5`.
            - If the value can't be turned into a number, raise `ValueError` with the message
              `"temperature must be a number"`.
            - If the number is below `0` or above `2`, raise `ValueError` with the message
              `"temperature must be between 0 and 2"`. `0` and `2` themselves are allowed.

            **Examples**
            ```python
            parse_temperature("0.7")     # returns 0.7
            parse_temperature(" 1 ")     # returns 1.0
            parse_temperature(2)         # returns 2.0
            parse_temperature("hot")     # raises ValueError("temperature must be a number")
            parse_temperature("2.5")     # raises ValueError("temperature must be between 0 and 2")
            ```
        ''',
        "starter": r'''
            def parse_temperature(value):
                ...
        ''',
        "tests": r'''
            from solution import parse_temperature

            def expect_error(value, message):
                try:
                    parse_temperature(value)
                except ValueError as e:
                    assert str(e) == message, f"for {value!r} the message was {str(e)!r}"
                else:
                    raise AssertionError(f"no ValueError for {value!r}")

            def test_string_numbers_become_floats():
                got = parse_temperature("0.7")
                assert got == 0.7 and isinstance(got, float), f"got {got!r}"

            def test_surrounding_spaces_are_fine():
                got = parse_temperature(" 1 ")
                assert got == 1.0 and isinstance(got, float), f"got {got!r}"

            def test_numbers_are_accepted_and_returned_as_float():
                got = parse_temperature(2)
                assert got == 2.0 and isinstance(got, float), f"got {got!r}"
                assert parse_temperature(0) == 0.0

            def test_non_numbers_raise_value_error():
                expect_error("hot", "temperature must be a number")
                expect_error("", "temperature must be a number")

            def test_out_of_range_raises_value_error():
                expect_error("2.5", "temperature must be between 0 and 2")
                expect_error(-0.1, "temperature must be between 0 and 2")
        ''',
        "solution": r'''
            def parse_temperature(value):
                try:
                    temperature = float(value)
                except ValueError:
                    raise ValueError("temperature must be a number")
                if temperature < 0 or temperature > 2:
                    raise ValueError("temperature must be between 0 and 2")
                return temperature
        ''',
        "hints": [
            "float() already handles strings, ints and surrounding spaces. The work is in catching its error and checking the range.",
            "Wrap the conversion in try/except and raise your own ValueError with the exact message. After that, compare the number with 0 and 2.",
            "1) try: t = float(value). 2) except ValueError: raise ValueError('temperature must be a number'). 3) If t < 0 or t > 2, raise the range error. 4) Return t.",
        ],
    },
    {
        "id": "exam-foundations-5",
        "title": "Plan request batches",
        "difficulty": 2,
        "research": {
            "note": "This one needs a standard-library function we haven't covered: one that rounds "
                    "a number *up* to the next whole number. Search the Python docs for it (it lives "
                    "in a module, so you'll need an import). Doing it with integer tricks also passes, "
                    "but finding the function is the point.",
            "links": [],
        },
        "prompt": r'''
            An embeddings API accepts at most `batch_size` texts per request. Before sending,
            you want to know how many requests you need and how big the last one will be.

            **Write:** `plan_batches(n_items, batch_size)`

            - `n_items`: how many texts you have, an `int` (`0` or more), e.g. `250`
            - `batch_size`: the most texts per request, an `int`, e.g. `100`
            - **Returns:** a dict `{"batches": <number of requests>, "last_batch": <texts in the last request>}`

            **Rules**
            - Every text must be sent, so a partly filled batch still counts as a batch.
            - If `n_items` is `0`, return `{"batches": 0, "last_batch": 0}`.
            - If `batch_size` is less than `1`, raise `ValueError` with the message
              `"batch_size must be at least 1"`.

            **Examples**
            ```python
            plan_batches(250, 100)   # returns {"batches": 3, "last_batch": 50}
            plan_batches(200, 100)   # returns {"batches": 2, "last_batch": 100}
            plan_batches(0, 100)     # returns {"batches": 0, "last_batch": 0}
            plan_batches(10, 0)      # raises ValueError("batch_size must be at least 1")
            ```
        ''',
        "starter": r'''
            def plan_batches(n_items, batch_size):
                ...
        ''',
        "tests": r'''
            from solution import plan_batches

            def test_partial_last_batch():
                got = plan_batches(250, 100)
                assert got == {"batches": 3, "last_batch": 50}, f"got {got!r}"

            def test_exact_multiple_has_full_last_batch():
                got = plan_batches(200, 100)
                assert got == {"batches": 2, "last_batch": 100}, f"got {got!r}"

            def test_fewer_items_than_batch_size():
                got = plan_batches(7, 100)
                assert got == {"batches": 1, "last_batch": 7}, f"got {got!r}"

            def test_zero_items():
                got = plan_batches(0, 100)
                assert got == {"batches": 0, "last_batch": 0}, f"got {got!r}"

            def test_bad_batch_size_raises_value_error():
                for bad in (0, -5):
                    try:
                        plan_batches(10, bad)
                    except ValueError as e:
                        assert str(e) == "batch_size must be at least 1", f"message was {str(e)!r}"
                    else:
                        raise AssertionError(f"no ValueError for batch_size={bad}")
        ''',
        "solution": r'''
            import math


            def plan_batches(n_items, batch_size):
                if batch_size < 1:
                    raise ValueError("batch_size must be at least 1")
                if n_items == 0:
                    return {"batches": 0, "last_batch": 0}
                batches = math.ceil(n_items / batch_size)
                last = n_items - (batches - 1) * batch_size
                return {"batches": batches, "last_batch": last}
        ''',
        "hints": [
            "Look in the standard library's maths module for a function that rounds up ('ceiling').",
            "Number of batches = n_items / batch_size rounded up. The last batch holds whatever is left after all the full batches before it.",
            "1) Raise if batch_size < 1. 2) Handle n_items == 0. 3) import math; batches = math.ceil(n_items / batch_size). 4) last = n_items - (batches - 1) * batch_size. 5) Return the dict.",
        ],
    },
    {
        "id": "exam-foundations-6",
        "title": "Retry backoff schedule",
        "difficulty": 2,
        "prompt": r'''
            When an API says "slow down", clients retry with *exponential backoff*: each wait is
            double the previous one, up to a maximum.

            **Write:** `backoff_delays(base, retries, cap)`

            - `base`: the first delay in seconds, a number, e.g. `1` or `0.5`
            - `retries`: how many retries to plan, an `int` (`0` or more)
            - `cap`: the largest allowed delay, a number, e.g. `10`
            - **Returns:** a list with one delay per retry

            **Rules**
            - Delay number `i` (counting from 0) is `base * 2 ** i`, but never more than `cap`.
            - `retries` of `0` returns `[]`.

            **Examples**
            ```python
            backoff_delays(1, 5, 10)      # returns [1, 2, 4, 8, 10]
            backoff_delays(0.5, 3, 30)    # returns [0.5, 1.0, 2.0]
            backoff_delays(1, 0, 10)      # returns []
            ```
        ''',
        "starter": r'''
            def backoff_delays(base, retries, cap):
                ...
        ''',
        "tests": r'''
            from solution import backoff_delays

            def test_doubles_then_caps():
                got = backoff_delays(1, 5, 10)
                assert got == [1, 2, 4, 8, 10], f"got {got!r}"

            def test_fractional_base():
                got = backoff_delays(0.5, 3, 30)
                assert got == [0.5, 1.0, 2.0], f"got {got!r}"

            def test_cap_applies_to_every_later_delay():
                got = backoff_delays(3, 6, 20)
                assert got == [3, 6, 12, 20, 20, 20], f"got {got!r}"

            def test_one_retry():
                assert backoff_delays(2, 1, 10) == [2]

            def test_zero_retries_is_empty():
                assert backoff_delays(1, 0, 10) == []
        ''',
        "solution": r'''
            def backoff_delays(base, retries, cap):
                delays = []
                for i in range(retries):
                    delays.append(min(base * 2 ** i, cap))
                return delays
        ''',
        "hints": [
            "A for loop over range(retries) that appends to a list.",
            "For each retry number, compute base times 2 to the power of that number, then keep whichever is smaller: that value or the cap.",
            "1) delays = []. 2) for i in range(retries): 3) delay = base * 2 ** i. 4) Append min(delay, cap). 5) Return delays.",
        ],
    },
    {
        "id": "exam-foundations-7",
        "title": "Readable transcript",
        "difficulty": 3,
        "prompt": r'''
            For a debug view, turn a chat history into short readable lines.

            **Write:** `transcript_lines(messages, max_len)`

            - `messages`: a list of dicts with `"role"` and `"content"` (a string or `None`)
            - `max_len`: the most characters of content to show per line, an `int`, e.g. `20`
            - **Returns:** a list of strings, one per shown message, like `"User: What is RAG?"`

            **Rules**
            - Labels: `"user"` → `"User"`, `"assistant"` → `"AI"`, `"tool"` → `"Tool"`.
            - Messages with role `"system"` are skipped (no line).
            - Any other role raises `ValueError` with the message `"unknown role: <role>"`.
            - `None` content is shown as `"(no content)"`.
            - Content longer than `max_len` characters is cut to its first `max_len`
              characters followed by `"..."`. Content of exactly `max_len` characters is not cut.
            - Each line is `"<label>: <content>"`.

            **Examples**
            ```python
            transcript_lines([
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "What is RAG?"},
                {"role": "assistant", "content": None},
                {"role": "tool", "content": "Retrieved 3 documents about RAG"},
            ], 20)
            # returns ["User: What is RAG?", "AI: (no content)", "Tool: Retrieved 3 document..."]
            transcript_lines([], 20)                                   # returns []
            transcript_lines([{"role": "bot", "content": "hi"}], 20)   # raises ValueError("unknown role: bot")
            ```
        ''',
        "starter": r'''
            def transcript_lines(messages, max_len):
                ...
        ''',
        "tests": r'''
            from solution import transcript_lines

            def test_example_transcript():
                got = transcript_lines([
                    {"role": "system", "content": "Be brief."},
                    {"role": "user", "content": "What is RAG?"},
                    {"role": "assistant", "content": None},
                    {"role": "tool", "content": "Retrieved 3 documents about RAG"},
                ], 20)
                assert got == ["User: What is RAG?", "AI: (no content)",
                               "Tool: Retrieved 3 document..."], f"got {got!r}"

            def test_content_of_exactly_max_len_is_not_cut():
                got = transcript_lines([{"role": "user", "content": "abcde"}], 5)
                assert got == ["User: abcde"], f"got {got!r}"

            def test_long_content_is_cut_with_dots():
                got = transcript_lines([{"role": "assistant", "content": "abcdef"}], 5)
                assert got == ["AI: abcde..."], f"got {got!r}"

            def test_system_messages_are_skipped():
                got = transcript_lines([{"role": "system", "content": "x"}], 5)
                assert got == [], f"got {got!r}"

            def test_empty_history():
                assert transcript_lines([], 20) == []

            def test_unknown_role_raises_value_error():
                try:
                    transcript_lines([{"role": "bot", "content": "hi"}], 20)
                except ValueError as e:
                    assert str(e) == "unknown role: bot", f"message was {str(e)!r}"
                else:
                    raise AssertionError("no ValueError for an unknown role")
        ''',
        "solution": r'''
            LABELS = {"user": "User", "assistant": "AI", "tool": "Tool"}


            def transcript_lines(messages, max_len):
                lines = []
                for message in messages:
                    role = message["role"]
                    if role == "system":
                        continue
                    if role not in LABELS:
                        raise ValueError(f"unknown role: {role}")
                    content = message["content"]
                    if content is None:
                        content = "(no content)"
                    elif len(content) > max_len:
                        content = content[:max_len] + "..."
                    lines.append(f"{LABELS[role]}: {content}")
                return lines
        ''',
        "hints": [
            "A dict of labels, a loop with `continue` for system messages, slicing to cut text, and an f-string per line.",
            "For each message: skip system, fail on unknown roles, replace None with the placeholder, cut long content with a slice plus '...', then build the line from the label and content.",
            "1) LABELS = {'user': 'User', ...}. 2) Loop; if role == 'system': continue. 3) If role not in LABELS, raise ValueError. 4) If content is None use '(no content)'; elif len(content) > max_len use content[:max_len] + '...'. 5) Append f'{label}: {content}'. 6) Return the list.",
        ],
    },
]
