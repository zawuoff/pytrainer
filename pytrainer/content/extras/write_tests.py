"""Write-the-tests steps for the chapters after Testing: you test real AI-engineering helpers.

The code under test is saved as target.py. Your tests must pass on the real implementation and
at least one of them must fail on each planted bug (the mutants).
"""

INTRO = "The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it."

EXTRAS = [
    {
        "id": "json-wt1", "topic": "json", "title": "Test a tool-argument parser", "difficulty": 2, "mode": "tests",
        "concepts": ["json.loads", "testing exceptions"],
        "prompt": r'''
            Models send tool arguments as a JSON **string**. Before calling a tool, an app parses it and
            refuses anything that isn't a JSON object. Write tests that would catch a broken parser.

            **Your job:** write tests for `parse_tool_args(text)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `text`: the arguments string a model sent

            **What comes out**
            - a dict: the parsed JSON object, nested values included

            **Rules** (what `parse_tool_args` does - your tests must check this)
            - A JSON object gives back the same dict, nested lists and objects included.
            - Text that isn't valid JSON raises `ValueError`.
            - Valid JSON that isn't an object (a list, a number, a string) raises `ValueError`.

            **Examples**
            ```python
            parse_tool_args('{"city": "Paris", "days": 2}')   # returns {"city": "Paris", "days": 2}
            parse_tool_args('{"filters": {"tags": ["a"]}}')     # returns {"filters": {"tags": ["a"]}}
            parse_tool_args("{city: Paris}")                    # raises ValueError
            parse_tool_args("[1, 2]")                           # raises ValueError
            ```
        ''',
        "impl": r'''
            import json


            def parse_tool_args(text):
                try:
                    value = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"arguments are not valid JSON: {exc}") from None
                if not isinstance(value, dict):
                    raise ValueError("arguments must be a JSON object")
                return value
        ''',
        "mutants": [
            {"name": "accepts any JSON value, not just objects", "code": r'''
                import json


                def parse_tool_args(text):
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as exc:
                        raise ValueError(str(exc)) from None
            '''},
            {"name": "returns {} for invalid JSON", "code": r'''
                import json


                def parse_tool_args(text):
                    try:
                        value = json.loads(text)
                    except json.JSONDecodeError:
                        return {}
                    if not isinstance(value, dict):
                        raise ValueError("arguments must be a JSON object")
                    return value
            '''},
            {"name": "drops nested values", "code": r'''
                import json


                def parse_tool_args(text):
                    try:
                        value = json.loads(text)
                    except json.JSONDecodeError as exc:
                        raise ValueError(str(exc)) from None
                    if not isinstance(value, dict):
                        raise ValueError("arguments must be a JSON object")
                    return {k: v for k, v in value.items() if not isinstance(v, (dict, list))}
            '''},
        ],
        "starter": r'''
            from target import parse_tool_args

        ''',
        "solution": r'''
            from target import parse_tool_args


            def raises_value_error(text):
                try:
                    parse_tool_args(text)
                except ValueError:
                    return True
                return False


            def test_object_is_parsed():
                assert parse_tool_args('{"city": "Paris", "days": 2}') == {"city": "Paris", "days": 2}


            def test_nested_values_are_kept():
                assert parse_tool_args('{"filters": {"tags": ["a"]}}') == {"filters": {"tags": ["a"]}}


            def test_invalid_json_raises():
                assert raises_value_error("{city: Paris}")


            def test_non_objects_raise():
                for text in ("[1, 2]", "3", '"hi"'):
                    assert raises_value_error(text), text
        ''',
        "tests": "",
        "hints": [
            "Each rule is one behaviour to pin down: the happy path, a nested value, and the two kinds of bad input.",
            "Compare whole dicts for the good cases, and for the bad cases check that a ValueError really happens.",
            "Write one test with a nested object, one with text that is not JSON at all, and one that loops over a few "
            "JSON values that are not objects. Make the error tests fail when no exception is raised.",
        ],
    },
    {
        "id": "regex-wt1", "topic": "regex", "title": "Test a citation extractor", "difficulty": 2, "mode": "tests",
        "concepts": ["re.findall", "edge cases"],
        "prompt": r'''
            A RAG answer cites its sources with markers like `[1]` or `[12]`. The app pulls out which sources
            were cited so it can show them. Write tests that would catch a broken extractor.

            **Your job:** write tests for `extract_citations(answer)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `answer`: the model's reply text

            **What comes out**
            - a list of ints: the cited source numbers

            **Rules** (what `extract_citations` does - your tests must check this)
            - A marker is a whole number in square brackets, with any number of digits.
            - Numbers come back as ints, in the order they first appear.
            - A source cited twice is listed once.
            - Brackets without a number, like `[a]` or `[]`, are ignored. No markers gives `[]`.

            **Examples**
            ```python
            extract_citations("Paris [2], founded early [1].")   # returns [2, 1]
            extract_citations("See [12] and again [12].")        # returns [12]
            extract_citations("No sources [a] here []")          # returns []
            ```
        ''',
        "impl": r'''
            import re


            def extract_citations(answer):
                seen = []
                for number in re.findall(r"\[(\d+)\]", answer):
                    n = int(number)
                    if n not in seen:
                        seen.append(n)
                return seen
        ''',
        "mutants": [
            {"name": "only finds one-digit markers", "code": r'''
                import re


                def extract_citations(answer):
                    seen = []
                    for number in re.findall(r"\[(\d)\]", answer):
                        if int(number) not in seen:
                            seen.append(int(number))
                    return seen
            '''},
            {"name": "returns the numbers as strings", "code": r'''
                import re


                def extract_citations(answer):
                    seen = []
                    for number in re.findall(r"\[(\d+)\]", answer):
                        if number not in seen:
                            seen.append(number)
                    return seen
            '''},
            {"name": "keeps duplicates", "code": r'''
                import re


                def extract_citations(answer):
                    return [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
            '''},
            {"name": "sorts instead of keeping the order", "code": r'''
                import re


                def extract_citations(answer):
                    return sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})
            '''},
        ],
        "starter": r'''
            from target import extract_citations

        ''',
        "solution": r'''
            from target import extract_citations


            def test_order_of_first_appearance():
                assert extract_citations("Paris [2], founded early [1].") == [2, 1]


            def test_multi_digit_and_duplicates():
                assert extract_citations("See [12] and again [12].") == [12]


            def test_ignores_brackets_without_numbers():
                assert extract_citations("No sources [a] here []") == []
        ''',
        "tests": "",
        "hints": [
            "Think about what could go wrong with digits, types, repeats and order: each rule hides one bug.",
            "Use inputs whose expected list only comes out right if every rule is followed, and compare whole lists.",
            "Write one test where the citations are out of numeric order, one with a two-digit number cited twice, and "
            "one with brackets that hold no number.",
        ],
    },
    {
        "id": "api-data-wt1", "topic": "api-data", "title": "Test a token counter", "difficulty": 2, "mode": "tests",
        "concepts": ["dict.get", "missing data"],
        "prompt": r'''
            To track spending, an app adds up the tokens reported by every API response. Some responses have no
            usage data. Write tests that would catch a broken counter.

            **Your job:** write tests for `total_tokens(responses)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `responses`: a list of response dicts. Each may have a `"usage"` dict with `"prompt_tokens"` and
              `"completion_tokens"`.

            **What comes out**
            - an int: all prompt and completion tokens added together

            **Rules** (what `total_tokens` does - your tests must check this)
            - Both prompt and completion tokens count, for every response.
            - A missing `"usage"` key, or `"usage": None`, counts as 0.
            - A usage dict missing one of the two numbers counts that one as 0.
            - An empty list gives 0.

            **Examples**
            ```python
            total_tokens([{"usage": {"prompt_tokens": 10, "completion_tokens": 5}},
                          {"usage": {"prompt_tokens": 3, "completion_tokens": 1}}])   # returns 19
            total_tokens([{"usage": None}, {"id": "x"}])                            # returns 0
            total_tokens([{"usage": {"prompt_tokens": 7}}])                         # returns 7
            ```
        ''',
        "impl": r'''
            def total_tokens(responses):
                total = 0
                for response in responses:
                    usage = response.get("usage") or {}
                    total += usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                return total
        ''',
        "mutants": [
            {"name": "ignores completion tokens", "code": r'''
                def total_tokens(responses):
                    return sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in responses)
            '''},
            {"name": "crashes when usage is None", "code": r'''
                def total_tokens(responses):
                    total = 0
                    for response in responses:
                        usage = response.get("usage", {})
                        total += usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                    return total
            '''},
            {"name": "only counts the first response", "code": r'''
                def total_tokens(responses):
                    for response in responses:
                        usage = response.get("usage") or {}
                        return usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                    return 0
            '''},
        ],
        "starter": r'''
            from target import total_tokens

        ''',
        "solution": r'''
            from target import total_tokens


            def test_adds_prompt_and_completion_for_every_response():
                responses = [{"usage": {"prompt_tokens": 10, "completion_tokens": 5}},
                             {"usage": {"prompt_tokens": 3, "completion_tokens": 1}}]
                assert total_tokens(responses) == 19


            def test_missing_or_none_usage_counts_zero():
                assert total_tokens([{"usage": None}, {"id": "x"}]) == 0


            def test_missing_field_counts_zero():
                assert total_tokens([{"usage": {"prompt_tokens": 7}}]) == 7


            def test_empty_list():
                assert total_tokens([]) == 0
        ''',
        "tests": "",
        "hints": [
            "Each rule names a shape of response data: full, missing, None, and partly filled.",
            "Use more than one response, and numbers where leaving any part out gives a different total.",
            "Test two full responses together, a None and a missing usage, a usage with only one number, and an empty list.",
        ],
    },
    {
        "id": "prompts-wt1", "topic": "prompts", "title": "Test a prompt template filler", "difficulty": 2, "mode": "tests",
        "concepts": ["templates", "KeyError"],
        "prompt": r'''
            Prompts are kept as templates with `{placeholders}` and filled in at run time. A silent mistake here
            sends the model a broken prompt. Write tests that would catch a broken filler.

            **Your job:** write tests for `fill(template, values)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `template`: a string with placeholders like `{name}` (letters, digits and underscores)
            - `values`: a dict from placeholder names to values

            **What comes out**
            - the filled-in string

            **Rules** (what `fill` does - your tests must check this)
            - Every occurrence of a placeholder is replaced, not just the first.
            - Values that aren't strings are converted with `str()`.
            - A placeholder with no value raises `KeyError`.
            - Values that no placeholder uses are ignored.

            **Examples**
            ```python
            fill("Hi {name}, bye {name}", {"name": "Ada"})   # returns "Hi Ada, bye Ada"
            fill("{n} tokens left", {"n": 5})                # returns "5 tokens left"
            fill("Hi {name}", {"name": "Ada", "x": 1})       # returns "Hi Ada"
            fill("Hi {name}", {})                            # raises KeyError
            ```
        ''',
        "impl": r'''
            import re


            def fill(template, values):
                return re.sub(r"\{(\w+)\}", lambda m: str(values[m.group(1)]), template)
        ''',
        "mutants": [
            {"name": "only replaces the first occurrence", "code": r'''
                import re


                def fill(template, values):
                    return re.sub(r"\{(\w+)\}", lambda m: str(values[m.group(1)]), template, count=1)
            '''},
            {"name": "leaves missing placeholders in the text", "code": r'''
                import re


                def fill(template, values):
                    return re.sub(r"\{(\w+)\}", lambda m: str(values.get(m.group(1), m.group(0))), template)
            '''},
            {"name": "fails on values that aren't strings", "code": r'''
                import re


                def fill(template, values):
                    return re.sub(r"\{(\w+)\}", lambda m: values[m.group(1)], template)
            '''},
        ],
        "starter": r'''
            from target import fill

        ''',
        "solution": r'''
            from target import fill


            def test_every_occurrence_is_replaced():
                assert fill("Hi {name}, bye {name}", {"name": "Ada"}) == "Hi Ada, bye Ada"


            def test_numbers_are_converted():
                assert fill("{n} tokens left", {"n": 5}) == "5 tokens left"


            def test_unused_values_are_ignored():
                assert fill("Hi {name}", {"name": "Ada", "x": 1}) == "Hi Ada"


            def test_missing_value_raises_key_error():
                try:
                    fill("Hi {name}", {})
                except KeyError:
                    return
                assert False, "expected KeyError"
        ''',
        "tests": "",
        "hints": [
            "Look at each rule and ask which wrong version of fill would still pass a simple one-placeholder test.",
            "Use a template that repeats a placeholder, a value that is a number, and an empty dict.",
            "Write a test per rule and compare complete strings. For the missing value, make the test fail when no "
            "KeyError happens.",
        ],
    },
    {
        "id": "structured-output-wt1", "topic": "structured-output", "title": "Test a score parser", "difficulty": 2,
        "mode": "tests", "concepts": ["validation", "code fences"],
        "prompt": r'''
            An LLM judge replies with JSON like `{"score": 4}`, sometimes wrapped in a Markdown code fence. The app
            must accept only a whole number from 1 to 5. Write tests that would catch a broken parser.

            **Your job:** write tests for `parse_score(reply)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `reply`: the model's reply text

            **What comes out**
            - an int from 1 to 5

            **Rules** (what `parse_score` does - your tests must check this)
            - The reply is a JSON object, possibly inside a code fence that starts with three backticks
              (optionally followed by `json`) and ends with three backticks.
            - `"score"` must be an int from 1 to 5. `true`/`false`, strings like `"4"` and other numbers are refused.
            - Anything refused, including text that isn't JSON or has no `"score"`, raises `ValueError`.

            **Examples**
            ```python
            parse_score('{"score": 4}')                          # returns 4
            parse_score('```json\n{"score": 5}\n```')            # returns 5
            parse_score('{"score": 0}')                          # raises ValueError
            parse_score('{"score": "4"}')                        # raises ValueError
            parse_score('{"score": true}')                       # raises ValueError
            ```
        ''',
        "impl": r'''
            import json
            import re


            def parse_score(reply):
                text = reply.strip()
                fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
                if fence:
                    text = fence.group(1)
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise ValueError("reply is not JSON") from None
                score = data.get("score") if isinstance(data, dict) else None
                if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                    raise ValueError(f"bad score: {score!r}")
                return score
        ''',
        "mutants": [
            {"name": "doesn't handle code fences", "code": r'''
                import json


                def parse_score(reply):
                    try:
                        data = json.loads(reply)
                    except json.JSONDecodeError:
                        raise ValueError("reply is not JSON") from None
                    score = data.get("score") if isinstance(data, dict) else None
                    if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                        raise ValueError(f"bad score: {score!r}")
                    return score
            '''},
            {"name": "accepts 0", "code": r'''
                import json
                import re


                def parse_score(reply):
                    text = reply.strip()
                    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
                    if fence:
                        text = fence.group(1)
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        raise ValueError("reply is not JSON") from None
                    score = data.get("score") if isinstance(data, dict) else None
                    if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 5:
                        raise ValueError(f"bad score: {score!r}")
                    return score
            '''},
            {"name": "converts strings like \"4\"", "code": r'''
                import json
                import re


                def parse_score(reply):
                    text = reply.strip()
                    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
                    if fence:
                        text = fence.group(1)
                    try:
                        score = int(json.loads(text)["score"])
                    except (json.JSONDecodeError, KeyError, TypeError):
                        raise ValueError("bad reply") from None
                    if not 1 <= score <= 5:
                        raise ValueError(f"bad score: {score!r}")
                    return score
            '''},
            {"name": "accepts true as 1", "code": r'''
                import json
                import re


                def parse_score(reply):
                    text = reply.strip()
                    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
                    if fence:
                        text = fence.group(1)
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        raise ValueError("reply is not JSON") from None
                    score = data.get("score") if isinstance(data, dict) else None
                    if not isinstance(score, int) or not 1 <= score <= 5:
                        raise ValueError(f"bad score: {score!r}")
                    return score
            '''},
        ],
        "starter": r'''
            from target import parse_score

        ''',
        "solution": r'''
            from target import parse_score


            def refused(reply):
                try:
                    parse_score(reply)
                except ValueError:
                    return True
                return False


            def test_plain_json():
                assert parse_score('{"score": 4}') == 4


            def test_fenced_json():
                assert parse_score('```json\n{"score": 5}\n```') == 5


            def test_out_of_range_is_refused():
                assert refused('{"score": 0}') and refused('{"score": 6}')


            def test_wrong_types_are_refused():
                assert refused('{"score": "4"}')
                assert refused('{"score": true}')


            def test_not_json_or_no_score_is_refused():
                assert refused("four") and refused('{"rating": 4}')
        ''',
        "tests": "",
        "hints": [
            "Go through the rules for good replies (plain and fenced) and for each way a reply can be refused.",
            "The edges matter most: the lowest and highest allowed scores, the numbers just outside them, and values of "
            "the wrong type.",
            "Test a plain reply, a fenced one, 0 and 6, a string score, a boolean score, and a reply with no score. "
            "A small helper that reports whether ValueError was raised keeps each test short.",
        ],
    },
    {
        "id": "tool-calling-wt1", "topic": "tool-calling", "title": "Test a tool dispatcher", "difficulty": 2,
        "mode": "tests", "concepts": ["error handling", "tool calls"],
        "prompt": r'''
            When a model calls a tool, the app must never crash: every problem goes back to the model as an
            `"Error: ..."` message so it can try again. Write tests that would catch a broken dispatcher.

            **Your job:** write tests for `dispatch(tools, call)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `tools`: a dict from tool names to Python functions
            - `call`: `{"name": <tool name>, "arguments": <JSON object as a string>}`

            **What comes out**
            - a string to send back to the model

            **Rules** (what `dispatch` does - your tests must check this)
            - The arguments are passed to the tool as keyword arguments.
            - A string result comes back as is; any other result comes back as JSON text (`json.dumps`).
            - It never raises. An unknown tool, arguments that aren't valid JSON, or a tool that raises an exception
              all give back a string that starts with `"Error: "`.

            **Examples**
            ```python
            tools = {"add": lambda a, b: a + b, "hello": lambda name: "hi " + name}
            dispatch(tools, {"name": "add", "arguments": '{"a": 2, "b": 3}'})     # returns "5"
            dispatch(tools, {"name": "hello", "arguments": '{"name": "Ada"}'})    # returns "hi Ada"
            dispatch(tools, {"name": "nope", "arguments": "{}"})                  # returns "Error: unknown tool 'nope'"
            dispatch(tools, {"name": "add", "arguments": '{"a": 1, "b": "x"}'})   # returns "Error: TypeError: ..."
            ```
        ''',
        "impl": r'''
            import json


            def dispatch(tools, call):
                name = call["name"]
                if name not in tools:
                    return f"Error: unknown tool {name!r}"
                try:
                    args = json.loads(call["arguments"])
                except json.JSONDecodeError as exc:
                    return f"Error: arguments are not valid JSON ({exc.msg})"
                try:
                    result = tools[name](**args)
                except Exception as exc:
                    return f"Error: {type(exc).__name__}: {exc}"
                return result if isinstance(result, str) else json.dumps(result)
        ''',
        "mutants": [
            {"name": "raises KeyError for an unknown tool", "code": r'''
                import json


                def dispatch(tools, call):
                    tool = tools[call["name"]]
                    try:
                        args = json.loads(call["arguments"])
                    except json.JSONDecodeError as exc:
                        return f"Error: arguments are not valid JSON ({exc.msg})"
                    try:
                        result = tool(**args)
                    except Exception as exc:
                        return f"Error: {type(exc).__name__}: {exc}"
                    return result if isinstance(result, str) else json.dumps(result)
            '''},
            {"name": "lets the tool's exceptions escape", "code": r'''
                import json


                def dispatch(tools, call):
                    name = call["name"]
                    if name not in tools:
                        return f"Error: unknown tool {name!r}"
                    try:
                        args = json.loads(call["arguments"])
                    except json.JSONDecodeError as exc:
                        return f"Error: arguments are not valid JSON ({exc.msg})"
                    result = tools[name](**args)
                    return result if isinstance(result, str) else json.dumps(result)
            '''},
            {"name": "returns results that aren't strings unchanged", "code": r'''
                import json


                def dispatch(tools, call):
                    name = call["name"]
                    if name not in tools:
                        return f"Error: unknown tool {name!r}"
                    try:
                        args = json.loads(call["arguments"])
                    except json.JSONDecodeError as exc:
                        return f"Error: arguments are not valid JSON ({exc.msg})"
                    try:
                        return tools[name](**args)
                    except Exception as exc:
                        return f"Error: {type(exc).__name__}: {exc}"
            '''},
            {"name": "crashes on invalid JSON", "code": r'''
                import json


                def dispatch(tools, call):
                    name = call["name"]
                    if name not in tools:
                        return f"Error: unknown tool {name!r}"
                    args = json.loads(call["arguments"])
                    try:
                        result = tools[name](**args)
                    except Exception as exc:
                        return f"Error: {type(exc).__name__}: {exc}"
                    return result if isinstance(result, str) else json.dumps(result)
            '''},
        ],
        "starter": r'''
            from target import dispatch

            TOOLS = {"add": lambda a, b: a + b, "hello": lambda name: "hi " + name}

        ''',
        "solution": r'''
            from target import dispatch

            TOOLS = {"add": lambda a, b: a + b, "hello": lambda name: "hi " + name}


            def call(name, arguments):
                return dispatch(TOOLS, {"name": name, "arguments": arguments})


            def test_number_result_comes_back_as_json_text():
                assert call("add", '{"a": 2, "b": 3}') == "5"


            def test_string_result_comes_back_as_is():
                assert call("hello", '{"name": "Ada"}') == "hi Ada"


            def test_unknown_tool_is_an_error_message():
                assert call("nope", "{}").startswith("Error: ")


            def test_bad_json_is_an_error_message():
                assert call("add", "{a: 2}").startswith("Error: ")


            def test_tool_exception_is_an_error_message():
                assert call("add", '{"a": 1, "b": "x"}').startswith("Error: ")
        ''',
        "tests": "",
        "hints": [
            "The rule \"it never raises\" covers three different situations. Each needs its own test.",
            "Check exact strings for the good results, and only the \"Error: \" start for the problems.",
            "Write tests for a number result, a string result, an unknown tool name, arguments that are not JSON, and a "
            "tool that fails on its input. If any of them raises, the test should fail.",
        ],
    },
    {
        "id": "chunking-wt1", "topic": "chunking", "title": "Test an overlapping window splitter", "difficulty": 2,
        "mode": "tests", "concepts": ["overlap", "boundaries"],
        "prompt": r'''
            Chunkers often split a list of words into overlapping windows, so a sentence cut at a boundary still
            appears whole in one chunk. Off-by-one bugs hide easily here. Write tests that would catch them.

            **Your job:** write tests for `windows(words, size, overlap)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `words`: a list of strings
            - `size`: the most words in one window
            - `overlap`: how many words each window repeats from the previous one

            **What comes out**
            - a list of windows (lists of words)

            **Rules** (what `windows` does - your tests must check this)
            - Windows start at position 0, then every `size - overlap` words.
            - It stops at the first window that reaches the end of the list, so the last window may be shorter, and
              there is never a window that only repeats words already covered.
            - An empty list gives `[]`.
            - `size` of 0 or less, a negative `overlap`, or an `overlap` of `size` or more raises `ValueError`.

            **Examples**
            ```python
            windows(["a", "b", "c", "d", "e", "f"], 3, 1)   # returns [["a","b","c"], ["c","d","e"], ["e","f"]]
            windows(["a", "b", "c", "d", "e"], 3, 1)        # returns [["a","b","c"], ["c","d","e"]]
            windows(["a", "b", "c", "d"], 2, 0)             # returns [["a","b"], ["c","d"]]
            windows(["a", "b"], 2, 3)                       # raises ValueError
            ```
        ''',
        "impl": r'''
            def windows(words, size, overlap):
                if size <= 0 or not 0 <= overlap < size:
                    raise ValueError("need size > 0 and 0 <= overlap < size")
                out, step = [], size - overlap
                for start in range(0, len(words), step):
                    out.append(words[start:start + size])
                    if start + size >= len(words):
                        break
                return out
        ''',
        "mutants": [
            {"name": "ignores the overlap", "code": r'''
                def windows(words, size, overlap):
                    if size <= 0 or not 0 <= overlap < size:
                        raise ValueError("bad sizes")
                    return [words[i:i + size] for i in range(0, len(words), size)]
            '''},
            {"name": "adds a window that only repeats covered words", "code": r'''
                def windows(words, size, overlap):
                    if size <= 0 or not 0 <= overlap < size:
                        raise ValueError("bad sizes")
                    return [words[i:i + size] for i in range(0, len(words), size - overlap)]
            '''},
            {"name": "accepts an overlap bigger than the window", "code": r'''
                def windows(words, size, overlap):
                    if size <= 0:
                        raise ValueError("bad size")
                    out, step = [], size - overlap
                    if step <= 0:
                        return []
                    for start in range(0, len(words), step):
                        out.append(words[start:start + size])
                        if start + size >= len(words):
                            break
                    return out
            '''},
            {"name": "steps one word too far", "code": r'''
                def windows(words, size, overlap):
                    if size <= 0 or not 0 <= overlap < size:
                        raise ValueError("bad sizes")
                    out = []
                    for start in range(0, len(words), size - overlap + 1):
                        out.append(words[start:start + size])
                        if start + size >= len(words):
                            break
                    return out
            '''},
        ],
        "starter": r'''
            from target import windows

        ''',
        "solution": r'''
            from target import windows

            WORDS = ["a", "b", "c", "d", "e", "f"]


            def test_overlapping_windows_with_a_short_last_one():
                assert windows(WORDS, 3, 1) == [["a", "b", "c"], ["c", "d", "e"], ["e", "f"]]


            def test_no_window_only_repeats_covered_words():
                assert windows(WORDS[:5], 3, 1) == [["a", "b", "c"], ["c", "d", "e"]]


            def test_no_overlap():
                assert windows(WORDS[:4], 2, 0) == [["a", "b"], ["c", "d"]]


            def test_empty_list():
                assert windows([], 3, 1) == []


            def test_bad_sizes_raise():
                for size, overlap in ((0, 0), (2, -1), (2, 2), (2, 3)):
                    try:
                        windows(WORDS, size, overlap)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for size={size}, overlap={overlap}"
        ''',
        "tests": "",
        "hints": [
            "Windows are about boundaries: where each one starts, and when the splitting stops.",
            "Pick list lengths where the last window ends exactly at the end, and where it would run past the end.",
            "Test six words with size 3 and overlap 1, five words with the same settings, a case without overlap, an "
            "empty list, and several bad size/overlap pairs that must raise.",
        ],
    },
    {
        "id": "retrieval-wt1", "topic": "retrieval", "title": "Test a top-k ranker", "difficulty": 2, "mode": "tests",
        "concepts": ["sorting", "tie-breaks"],
        "prompt": r'''
            After scoring every document, retrieval keeps the best `k`. Results must be stable: the same scores must
            always give the same order. Write tests that would catch a broken ranker.

            **Your job:** write tests for `top_k(scores, k)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `scores`: a dict from document ids to similarity scores
            - `k`: how many ids to keep

            **What comes out**
            - a list of document ids

            **Rules** (what `top_k` does - your tests must check this)
            - Highest score first.
            - Equal scores are ordered by id, alphabetically.
            - `k` larger than the number of documents returns them all; `k` of 0 or less returns `[]`.

            **Examples**
            ```python
            top_k({"a": 0.2, "b": 0.9, "c": 0.5}, 2)    # returns ["b", "c"]
            top_k({"z": 0.5, "m": 0.5, "a": 0.1}, 2)    # returns ["m", "z"]
            top_k({"a": 0.2}, 5)                        # returns ["a"]
            top_k({"a": 0.2, "b": 0.3}, -1)             # returns []
            ```
        ''',
        "impl": r'''
            def top_k(scores, k):
                ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
                return [doc_id for doc_id, _ in ranked[:max(k, 0)]]
        ''',
        "mutants": [
            {"name": "lowest score first", "code": r'''
                def top_k(scores, k):
                    ranked = sorted(scores.items(), key=lambda item: (item[1], item[0]))
                    return [doc_id for doc_id, _ in ranked[:max(k, 0)]]
            '''},
            {"name": "keeps ties in insertion order", "code": r'''
                def top_k(scores, k):
                    ranked = sorted(scores.items(), key=lambda item: -item[1])
                    return [doc_id for doc_id, _ in ranked[:max(k, 0)]]
            '''},
            {"name": "negative k drops the last result", "code": r'''
                def top_k(scores, k):
                    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
                    return [doc_id for doc_id, _ in ranked[:k]]
            '''},
            {"name": "returns (id, score) pairs", "code": r'''
                def top_k(scores, k):
                    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:max(k, 0)]
            '''},
        ],
        "starter": r'''
            from target import top_k

        ''',
        "solution": r'''
            from target import top_k


            def test_highest_first():
                assert top_k({"a": 0.2, "b": 0.9, "c": 0.5}, 2) == ["b", "c"]


            def test_ties_by_id():
                assert top_k({"z": 0.5, "m": 0.5, "a": 0.1}, 2) == ["m", "z"]


            def test_k_bigger_than_documents():
                assert top_k({"a": 0.2}, 5) == ["a"]


            def test_k_zero_or_negative():
                assert top_k({"a": 0.2, "b": 0.3}, 0) == []
                assert top_k({"a": 0.2, "b": 0.3, "c": 0.4}, -1) == []
        ''',
        "tests": "",
        "hints": [
            "Order, ties, and unusual values of k: each needs a test where a wrong version gives a different list.",
            "For ties, insert the dict keys in reverse alphabetical order so keeping insertion order would be visible.",
            "Test a normal case, a tie, a k larger than the dict, and k values of 0 and below. Compare whole lists of ids.",
        ],
    },
    {
        "id": "rag-answers-wt1", "topic": "rag-answers", "title": "Test a grounded prompt builder", "difficulty": 2,
        "mode": "tests", "concepts": ["prompt layout", "citations"],
        "prompt": r'''
            A RAG app numbers its sources in the prompt so the model can cite them as `[1]`, `[2]`... If the
            numbering or the order is wrong, every citation points at the wrong passage. Write tests that would
            catch a broken builder.

            **Your job:** write tests for `build_prompt(question, passages)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `question`: the user's question
            - `passages`: the retrieved passages, best first

            **What comes out**
            - the prompt text, exactly in this layout:

            ```text
            Answer using only the sources below. Cite them like [1].

            Sources:
            [1] <first passage>
            [2] <second passage>

            Question: <question>
            ```

            **Rules** (what `build_prompt` does - your tests must check this)
            - Sources are numbered from 1, in the order given.
            - An empty list of passages raises `ValueError`.

            **Examples**
            ```python
            build_prompt("Refund time?", ["Refunds take 5 days."])
            # returns "Answer using only the sources below. Cite them like [1].\n\nSources:\n[1] Refunds take 5 days.\n\nQuestion: Refund time?"
            build_prompt("Hi?", [])   # raises ValueError
            ```
        ''',
        "impl": r'''
            HEADER = "Answer using only the sources below. Cite them like [1]."


            def build_prompt(question, passages):
                if not passages:
                    raise ValueError("no passages to answer from")
                sources = "\n".join(f"[{i}] {text}" for i, text in enumerate(passages, start=1))
                return f"{HEADER}\n\nSources:\n{sources}\n\nQuestion: {question}"
        ''',
        "mutants": [
            {"name": "numbers sources from 0", "code": r'''
                HEADER = "Answer using only the sources below. Cite them like [1]."


                def build_prompt(question, passages):
                    if not passages:
                        raise ValueError("no passages")
                    sources = "\n".join(f"[{i}] {text}" for i, text in enumerate(passages))
                    return f"{HEADER}\n\nSources:\n{sources}\n\nQuestion: {question}"
            '''},
            {"name": "lists the passages in reverse", "code": r'''
                HEADER = "Answer using only the sources below. Cite them like [1]."


                def build_prompt(question, passages):
                    if not passages:
                        raise ValueError("no passages")
                    sources = "\n".join(f"[{i}] {text}" for i, text in enumerate(reversed(passages), start=1))
                    return f"{HEADER}\n\nSources:\n{sources}\n\nQuestion: {question}"
            '''},
            {"name": "builds a prompt with no sources", "code": r'''
                HEADER = "Answer using only the sources below. Cite them like [1]."


                def build_prompt(question, passages):
                    sources = "\n".join(f"[{i}] {text}" for i, text in enumerate(passages, start=1))
                    return f"{HEADER}\n\nSources:\n{sources}\n\nQuestion: {question}"
            '''},
            {"name": "forgets the question", "code": r'''
                HEADER = "Answer using only the sources below. Cite them like [1]."


                def build_prompt(question, passages):
                    if not passages:
                        raise ValueError("no passages")
                    sources = "\n".join(f"[{i}] {text}" for i, text in enumerate(passages, start=1))
                    return f"{HEADER}\n\nSources:\n{sources}\n"
            '''},
        ],
        "starter": r'''
            from target import build_prompt

        ''',
        "solution": r'''
            from target import build_prompt


            def test_exact_layout_with_two_sources():
                got = build_prompt("Refund time?", ["Refunds take 5 days.", "Office closed on holidays."])
                assert got == ("Answer using only the sources below. Cite them like [1].\n\nSources:\n"
                               "[1] Refunds take 5 days.\n[2] Office closed on holidays.\n\nQuestion: Refund time?")


            def test_no_passages_raises():
                try:
                    build_prompt("Hi?", [])
                except ValueError:
                    return
                assert False, "expected ValueError"
        ''',
        "tests": "",
        "hints": [
            "With an exact layout, one comparison of the whole string can catch several bugs at once, if the input is rich enough.",
            "Use at least two different passages, so numbering and order both show, and check the question is there too.",
            "Compare the full prompt for a question with two passages against the layout written out by hand, and add a "
            "test that an empty list raises ValueError.",
        ],
    },
    {
        "id": "evals-wt1", "topic": "evals", "title": "Test a contains grader", "difficulty": 2, "mode": "tests",
        "concepts": ["graders", "case-insensitive"],
        "prompt": r'''
            Eval graders decide whether a model's output passes. A grader that is too strict or too lenient makes
            every number in the eval report wrong. Write tests that would catch a broken one.

            **Your job:** write tests for `grade_contains(output, expected)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `output`: the model's output text
            - `expected`: a string, or a list of strings

            **What comes out**
            - `True` if the output passes, else `False`

            **Rules** (what `grade_contains` does - your tests must check this)
            - A string passes when it appears in the output, ignoring upper and lower case.
            - A list passes only when **every** string in it appears (again ignoring case).
            - An empty list passes.

            **Examples**
            ```python
            grade_contains("The capital is PARIS.", "paris")          # returns True
            grade_contains("Paris and Lyon", ["paris", "lyon"])       # returns True
            grade_contains("Paris only", ["paris", "lyon"])           # returns False
            grade_contains("anything", [])                            # returns True
            ```
        ''',
        "impl": r'''
            def grade_contains(output, expected):
                text = output.lower()
                if isinstance(expected, str):
                    return expected.lower() in text
                return all(item.lower() in text for item in expected)
        ''',
        "mutants": [
            {"name": "case-sensitive", "code": r'''
                def grade_contains(output, expected):
                    if isinstance(expected, str):
                        return expected in output
                    return all(item in output for item in expected)
            '''},
            {"name": "any string from the list is enough", "code": r'''
                def grade_contains(output, expected):
                    text = output.lower()
                    if isinstance(expected, str):
                        return expected.lower() in text
                    return any(item.lower() in text for item in expected)
            '''},
            {"name": "fails an empty list", "code": r'''
                def grade_contains(output, expected):
                    text = output.lower()
                    if isinstance(expected, str):
                        return expected.lower() in text
                    return bool(expected) and all(item.lower() in text for item in expected)
            '''},
        ],
        "starter": r'''
            from target import grade_contains

        ''',
        "solution": r'''
            from target import grade_contains


            def test_string_ignores_case():
                assert grade_contains("The capital is PARIS.", "paris") is True


            def test_list_needs_every_item():
                assert grade_contains("Paris and Lyon", ["paris", "LYON"]) is True
                assert grade_contains("Paris only", ["paris", "lyon"]) is False


            def test_missing_string_fails():
                assert grade_contains("Berlin", "paris") is False


            def test_empty_list_passes():
                assert grade_contains("anything", []) is True
        ''',
        "tests": "",
        "hints": [
            "A grader can be wrong in two directions: passing what should fail, and failing what should pass.",
            "Mix upper and lower case between output and expected, and use a list where only some items appear.",
            "Test a string that matches with different case, a list that fully matches, a list that partly matches, a "
            "string that is missing, and an empty list.",
        ],
    },
    {
        "id": "evals-wt2", "topic": "evals", "title": "Test an eval summary", "difficulty": 2, "mode": "tests",
        "concepts": ["pass rate", "division by zero"],
        "prompt": r'''
            After an eval run, a summary turns the list of pass/fail results into the numbers people compare
            between prompt versions. Write tests that would catch a broken summary.

            **Your job:** write tests for `summarize(results)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `results`: a list of booleans, `True` for each case that passed

            **What comes out**
            - `{"total": <int>, "passed": <int>, "pass_rate": <float>}`

            **Rules** (what `summarize` does - your tests must check this)
            - `pass_rate` is `passed / total`, rounded to 2 decimals.
            - No results gives `{"total": 0, "passed": 0, "pass_rate": 0.0}`.

            **Examples**
            ```python
            summarize([True, False, True])   # returns {"total": 3, "passed": 2, "pass_rate": 0.67}
            summarize([True, True])          # returns {"total": 2, "passed": 2, "pass_rate": 1.0}
            summarize([])                    # returns {"total": 0, "passed": 0, "pass_rate": 0.0}
            ```
        ''',
        "impl": r'''
            def summarize(results):
                total, passed = len(results), sum(1 for r in results if r)
                return {"total": total, "passed": passed, "pass_rate": round(passed / total, 2) if total else 0.0}
        ''',
        "mutants": [
            {"name": "crashes when there are no results", "code": r'''
                def summarize(results):
                    total, passed = len(results), sum(1 for r in results if r)
                    return {"total": total, "passed": passed, "pass_rate": round(passed / total, 2)}
            '''},
            {"name": "doesn't round", "code": r'''
                def summarize(results):
                    total, passed = len(results), sum(1 for r in results if r)
                    return {"total": total, "passed": passed, "pass_rate": passed / total if total else 0.0}
            '''},
            {"name": "gives a percentage", "code": r'''
                def summarize(results):
                    total, passed = len(results), sum(1 for r in results if r)
                    return {"total": total, "passed": passed, "pass_rate": round(100 * passed / total, 2) if total else 0.0}
            '''},
            {"name": "counts the failures as passed", "code": r'''
                def summarize(results):
                    total, passed = len(results), results.count(False)
                    return {"total": total, "passed": passed, "pass_rate": round(passed / total, 2) if total else 0.0}
            '''},
        ],
        "starter": r'''
            from target import summarize

        ''',
        "solution": r'''
            from target import summarize


            def test_rounds_to_two_decimals():
                assert summarize([True, False, True]) == {"total": 3, "passed": 2, "pass_rate": 0.67}


            def test_all_passed():
                assert summarize([True, True]) == {"total": 2, "passed": 2, "pass_rate": 1.0}


            def test_no_results():
                assert summarize([]) == {"total": 0, "passed": 0, "pass_rate": 0.0}
        ''',
        "tests": "",
        "hints": [
            "The interesting inputs are the ones where a fraction doesn't come out even, and the empty list.",
            "Compare the whole returned dict, so a wrong count, a wrong scale or missing rounding all show up.",
            "Test a list with a repeating-decimal pass rate, a list where everything passed, and an empty list.",
        ],
    },
    {
        "id": "agents-wt1", "topic": "agents", "title": "Test an action parser", "difficulty": 2, "mode": "tests",
        "concepts": ["parsing", "agent loop"],
        "prompt": r'''
            A simple agent asks the model to reply with either `FINAL: <answer>` or `TOOL: <name> | <input>`. The
            loop parses each reply to decide what to do next. Write tests that would catch a broken parser.

            **Your job:** write tests for `parse_action(text)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `text`: the model's reply

            **What comes out**
            - `("final", answer)` or `("tool", name, tool_input)`

            **Rules** (what `parse_action` does - your tests must check this)
            - The `FINAL` / `TOOL` word may be in any case.
            - Spaces around the answer, the name and the input are removed.
            - A tool input may contain spaces; only the first `|` separates it from the name.
            - Anything else, including a `TOOL:` reply without a `|`, raises `ValueError`.

            **Examples**
            ```python
            parse_action("FINAL: It is sunny.")             # returns ("final", "It is sunny.")
            parse_action("tool:  search | rag eval tips ")  # returns ("tool", "search", "rag eval tips")
            parse_action("TOOL: search rag")                # raises ValueError
            parse_action("Let me think...")                 # raises ValueError
            ```
        ''',
        "impl": r'''
            def parse_action(text):
                text = text.strip()
                head, sep, rest = text.partition(":")
                kind = head.strip().upper()
                if sep and kind == "FINAL":
                    return ("final", rest.strip())
                if sep and kind == "TOOL":
                    name, bar, tool_input = rest.partition("|")
                    if bar and name.strip():
                        return ("tool", name.strip(), tool_input.strip())
                raise ValueError(f"cannot parse action: {text[:60]!r}")
        ''',
        "mutants": [
            {"name": "only understands upper case", "code": r'''
                def parse_action(text):
                    text = text.strip()
                    if text.startswith("FINAL:"):
                        return ("final", text[6:].strip())
                    if text.startswith("TOOL:"):
                        name, bar, tool_input = text[5:].partition("|")
                        if bar and name.strip():
                            return ("tool", name.strip(), tool_input.strip())
                    raise ValueError("cannot parse action")
            '''},
            {"name": "keeps the spaces", "code": r'''
                def parse_action(text):
                    head, sep, rest = text.strip().partition(":")
                    kind = head.strip().upper()
                    if sep and kind == "FINAL":
                        return ("final", rest)
                    if sep and kind == "TOOL":
                        name, bar, tool_input = rest.partition("|")
                        if bar and name.strip():
                            return ("tool", name, tool_input)
                    raise ValueError("cannot parse action")
            '''},
            {"name": "splits the tool input at a space", "code": r'''
                def parse_action(text):
                    head, sep, rest = text.strip().partition(":")
                    kind = head.strip().upper()
                    if sep and kind == "FINAL":
                        return ("final", rest.strip())
                    if sep and kind == "TOOL":
                        parts = rest.replace("|", " ").split()
                        if len(parts) >= 2:
                            return ("tool", parts[0], parts[1])
                    raise ValueError("cannot parse action")
            '''},
            {"name": "accepts a tool call without a |", "code": r'''
                def parse_action(text):
                    head, sep, rest = text.strip().partition(":")
                    kind = head.strip().upper()
                    if sep and kind == "FINAL":
                        return ("final", rest.strip())
                    if sep and kind == "TOOL":
                        name, _, tool_input = rest.partition("|")
                        return ("tool", name.strip(), tool_input.strip())
                    raise ValueError("cannot parse action")
            '''},
        ],
        "starter": r'''
            from target import parse_action

        ''',
        "solution": r'''
            from target import parse_action


            def raises(text):
                try:
                    parse_action(text)
                except ValueError:
                    return True
                return False


            def test_final_answer():
                assert parse_action("FINAL: It is sunny.") == ("final", "It is sunny.")


            def test_tool_call_any_case_spaces_trimmed():
                assert parse_action("tool:  search | rag eval tips ") == ("tool", "search", "rag eval tips")


            def test_tool_without_bar_raises():
                assert raises("TOOL: search rag")


            def test_other_text_raises():
                assert raises("Let me think...")
        ''',
        "hints": [
            "Each rule hides a common slip: case, extra spaces, spaces inside the input, and a missing separator.",
            "One carefully chosen tool reply can check case, trimming and spaces inside the input all at once.",
            "Test a FINAL reply, a lower-case tool reply with extra spaces and a multi-word input, a tool reply with no "
            "bar, and a reply that is neither.",
        ],
        "tests": "",
    },
    {
        "id": "ai-safety-wt1", "topic": "ai-safety", "title": "Test a secret redactor", "difficulty": 2, "mode": "tests",
        "concepts": ["regex", "privacy"],
        "prompt": r'''
            Before logs or prompts leave the app, API keys and email addresses are replaced with placeholders.
            Missing one leaks a secret; redacting too much breaks normal text. Write tests that would catch both.

            **Your job:** write tests for `redact(text)` from `target.py`

            ''' + INTRO + r'''

            **What goes in**

            - `text`: any text

            **What comes out**
            - the same text with secrets replaced

            **Rules** (what `redact` does - your tests must check this)
            - An API key is `sk-` followed by **20 or more** letters, digits, `-` or `_`. It becomes `[KEY]`.
            - An email address becomes `[EMAIL]`.
            - Every occurrence is replaced; everything else is left exactly as it was, including short words that
              start with `sk-`.

            **Examples**
            ```python
            redact("key sk-abcdefghijklmnopqrstu1 ok")    # returns "key [KEY] ok"
            redact("a sk-proj_ABCDEFGHIJ-0123456789 b")   # returns "a [KEY] b"
            redact("mail ada@example.com now")           # returns "mail [EMAIL] now"
            redact("I use sk-learn")                     # returns "I use sk-learn"
            ```
        ''',
        "impl": r'''
            import re

            KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")
            EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")


            def redact(text):
                return EMAIL.sub("[EMAIL]", KEY.sub("[KEY]", text))
        ''',
        "mutants": [
            {"name": "only replaces the first key", "code": r'''
                import re

                KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")
                EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")


                def redact(text):
                    return EMAIL.sub("[EMAIL]", KEY.sub("[KEY]", text, count=1))
            '''},
            {"name": "redacts short words that start with sk-", "code": r'''
                import re

                KEY = re.compile(r"\bsk-[A-Za-z0-9_-]+")
                EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")


                def redact(text):
                    return EMAIL.sub("[EMAIL]", KEY.sub("[KEY]", text))
            '''},
            {"name": "misses keys with - or _", "code": r'''
                import re

                KEY = re.compile(r"\bsk-[A-Za-z0-9]{20,}")
                EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")


                def redact(text):
                    return EMAIL.sub("[EMAIL]", KEY.sub("[KEY]", text))
            '''},
            {"name": "leaves emails alone", "code": r'''
                import re

                KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")


                def redact(text):
                    return KEY.sub("[KEY]", text)
            '''},
        ],
        "starter": r'''
            from target import redact

        ''',
        "solution": r'''
            from target import redact


            def test_every_key_is_replaced():
                text = "k1 sk-abcdefghijklmnopqrstu1 k2 sk-ZYXWVUTSRQPONMLKJIHG99"
                assert redact(text) == "k1 [KEY] k2 [KEY]"


            def test_keys_with_dashes_and_underscores():
                assert redact("a sk-proj_ABCDEFGHIJ-0123456789 b") == "a [KEY] b"


            def test_emails_are_replaced():
                assert redact("mail ada@example.com now") == "mail [EMAIL] now"


            def test_short_sk_words_are_left_alone():
                assert redact("I use sk-learn") == "I use sk-learn"
        ''',
        "tests": "",
        "hints": [
            "There are two kinds of failure here: missing a secret, and changing text that was never secret.",
            "Use a text with two keys, a key containing - and _, an email, and a short word starting with sk-.",
            "Write one test per rule and compare complete strings, so a single leaked or wrongly replaced word shows up.",
        ],
    },
]
