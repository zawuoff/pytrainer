"""Refactor challenges: the code already works. Make it idiomatic without breaking it.

The starter passes every behaviour check. It fails only the style checks (tests named
``test_style_...``): a line budget for the whole file and one idiom the step is about. The
validator proves that split, so a learner never has to fix a bug here, only the shape.
"""

import textwrap

# Shared by every refactor's tests: counts real code lines and finds syntax nodes in the learner's file.
HELPERS = r'''
import ast


def code_lines():
    """Lines of code in solution.py: blank lines, comments and docstrings don't count."""
    text = source()
    docs = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docs.update(range(first.lineno, first.end_lineno + 1))
    return sum(1 for i, line in enumerate(text.splitlines(), 1)
               if line.strip() and not line.strip().startswith("#") and i not in docs)


def found(*kinds):
    return [n for n in ast.walk(ast.parse(source())) if isinstance(n, kinds)]
'''

LEAD = ("This code works and passes its behaviour checks, but it is longer and clunkier than it needs to be. "
        "**Your job:** refactor it without changing what it does.")


def make_tests(imports, body, budget):
    """Test source: the import, the helpers, the step's own tests, then the line-budget check."""
    return (imports + "\n" + HELPERS + textwrap.dedent(body) + f'''

def test_style_fits_in_{budget}_lines():
    lines = code_lines()
    assert lines <= {budget}, f"{{lines}} lines of code; the budget is {budget} (blank lines, comments and docstrings don't count)"
''')


EXTRAS = [
    {
        "id": "loops-rf1", "topic": "loops", "kind": "refactor", "title": "Refactor: total characters", "difficulty": 2,
        "concepts": ["iterating directly", "sum()"],
        "prompt": r'''
            ''' + LEAD + r'''

            `total_chars(messages)` returns the total number of characters in a list of message strings.

            **Style checks**
            - No `range(len(...))`: loop over the messages themselves.
            - The whole file fits in **2 lines** of code.

            **Examples**
            ```python
            total_chars(["hi", "there"])   # returns 7
            total_chars([])                # returns 0
            ```
        ''',
        "starter": r'''
            def total_chars(messages):
                total = 0
                for i in range(len(messages)):
                    message = messages[i]
                    total = total + len(message)
                return total
        ''',
        "solution": r'''
            def total_chars(messages):
                return sum(len(message) for message in messages)
        ''',
        "tests": make_tests("from solution import total_chars", r'''

            def test_adds_up_lengths():
                assert total_chars(["hi", "there"]) == 7

            def test_empty():
                assert total_chars([]) == 0

            def test_style_no_range_len():
                calls = [n for n in found(ast.Call) if getattr(n.func, "id", None) == "range"
                         and n.args and isinstance(n.args[0], ast.Call) and getattr(n.args[0].func, "id", None) == "len"]
                assert not calls, "loop over the list itself instead of range(len(...))"
        ''', 2),
        "hints": [
            "What you really want is the length of each message, added up.",
            "Python can loop over a list's items directly, and has a built-in that adds up numbers.",
            "Feed the built-in that sums numbers a generator expression that gives each message's length.",
        ],
    },
    {
        "id": "comprehensions-rf1", "topic": "comprehensions", "kind": "refactor", "title": "Refactor: user messages",
        "difficulty": 2, "concepts": ["list comprehensions"],
        "prompt": r'''
            ''' + LEAD + r'''

            `user_texts(messages)` returns the `"content"` of every message whose `"role"` is `"user"`, in order.

            **Style checks**
            - No `.append(...)`: build the list with a comprehension.
            - The whole file fits in **2 lines** of code.

            **Examples**
            ```python
            user_texts([{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"},
                        {"role": "user", "content": "bye"}])   # returns ["hi", "bye"]
            ```
        ''',
        "starter": r'''
            def user_texts(messages):
                result = []
                for message in messages:
                    if message["role"] == "user":
                        result.append(message["content"])
                return result
        ''',
        "solution": r'''
            def user_texts(messages):
                return [m["content"] for m in messages if m["role"] == "user"]
        ''',
        "tests": make_tests("from solution import user_texts", r'''

            MSGS = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"},
                    {"role": "user", "content": "bye"}]

            def test_keeps_user_messages_in_order():
                assert user_texts(MSGS) == ["hi", "bye"]

            def test_no_user_messages():
                assert user_texts([{"role": "system", "content": "x"}]) == []

            def test_style_no_append():
                calls = [n for n in found(ast.Call) if isinstance(n.func, ast.Attribute) and n.func.attr == "append"]
                assert not calls, "build the list in one comprehension instead of appending"
        ''', 2),
        "hints": [
            "This is the exact shape a list comprehension was made for: a loop, a filter and one value per item.",
            "A comprehension has three parts: the value to keep, the loop, and an optional condition.",
            "Return a comprehension whose value is the content, looping over the messages, with the role check as its condition.",
        ],
    },
    {
        "id": "dicts-rf1", "topic": "dicts", "kind": "refactor", "title": "Refactor: count tool calls", "difficulty": 2,
        "concepts": ["dict.get", "counting"],
        "prompt": r'''
            ''' + LEAD + r'''

            `count_tools(calls)` takes a list of tool names and returns a dict from each name to how many times
            it appears.

            **Style checks**
            - No `if` statements: let a dict method (or `collections.Counter`) handle missing keys.
            - The whole file fits in **5 lines** of code.

            **Examples**
            ```python
            count_tools(["search", "calc", "search"])   # returns {"search": 2, "calc": 1}
            count_tools([])                             # returns {}
            ```
        ''',
        "starter": r'''
            def count_tools(calls):
                counts = {}
                for name in calls:
                    if name in counts:
                        counts[name] = counts[name] + 1
                    else:
                        counts[name] = 1
                return counts
        ''',
        "solution": r'''
            def count_tools(calls):
                counts = {}
                for name in calls:
                    counts[name] = counts.get(name, 0) + 1
                return counts
        ''',
        "tests": make_tests("from solution import count_tools", r'''

            def test_counts():
                assert dict(count_tools(["search", "calc", "search"])) == {"search": 2, "calc": 1}

            def test_empty():
                assert dict(count_tools([])) == {}

            def test_style_no_if():
                assert not found(ast.If), "no if statements: a dict method can supply a starting count"
        ''', 5),
        "hints": [
            "The if/else only exists to handle a name you haven't seen yet.",
            "There's a dict method that looks up a key and gives back a default when it's missing.",
            "Inside the loop, set the count to the current count (with a default of 0) plus one, in a single line.",
        ],
    },
    {
        "id": "strings-rf1", "topic": "strings", "kind": "refactor", "title": "Refactor: format a transcript", "difficulty": 2,
        "concepts": ["str.join", "f-strings"],
        "prompt": r'''
            ''' + LEAD + r'''

            `transcript(messages)` turns `(role, text)` pairs into lines like `user: hi`, one per message, joined
            with newlines (no newline at the end).

            **Style checks**
            - No `+=`: join the lines instead of growing a string.
            - The whole file fits in **2 lines** of code.

            **Examples**
            ```python
            transcript([("user", "hi"), ("assistant", "hello")])   # returns "user: hi\nassistant: hello"
            transcript([])                                         # returns ""
            ```
        ''',
        "starter": r'''
            def transcript(messages):
                text = ""
                for role, content in messages:
                    if text != "":
                        text += "\n"
                    text += role + ": " + content
                return text
        ''',
        "solution": r'''
            def transcript(messages):
                return "\n".join(f"{role}: {content}" for role, content in messages)
        ''',
        "tests": make_tests("from solution import transcript", r'''

            def test_lines_joined():
                assert transcript([("user", "hi"), ("assistant", "hello")]) == "user: hi\nassistant: hello"

            def test_empty():
                assert transcript([]) == ""

            def test_style_no_augmented_assignment():
                assert not found(ast.AugAssign), "join the lines instead of growing a string with +="
        ''', 2),
        "hints": [
            "The awkward part is putting newlines between lines but not after the last one.",
            "A string method takes many strings and puts a separator only between them.",
            "Call that method on the newline character, with a generator that formats each pair using an f-string.",
        ],
    },
    {
        "id": "conditionals-rf1", "topic": "conditionals", "kind": "refactor", "title": "Refactor: name a finish reason",
        "difficulty": 2, "concepts": ["dict lookup instead of if/elif"],
        "prompt": r'''
            ''' + LEAD + r'''

            `describe(reason)` turns an API `finish_reason` into words for the user: `"stop"` gives
            `"Finished normally"`, `"length"` gives `"Cut off: hit the token limit"`, `"tool_calls"` gives
            `"Wants to call a tool"`, `"content_filter"` gives `"Blocked by the content filter"`, and anything else
            gives `"Unknown reason"`.

            **Style checks**
            - At most **one** `if`: replace the chain with a lookup table.
            - The whole file fits in **8 lines** of code.

            **Examples**
            ```python
            describe("length")   # returns "Cut off: hit the token limit"
            describe("weird")    # returns "Unknown reason"
            ```
        ''',
        "starter": r'''
            def describe(reason):
                if reason == "stop":
                    return "Finished normally"
                elif reason == "length":
                    return "Cut off: hit the token limit"
                elif reason == "tool_calls":
                    return "Wants to call a tool"
                elif reason == "content_filter":
                    return "Blocked by the content filter"
                else:
                    return "Unknown reason"
        ''',
        "solution": r'''
            REASONS = {
                "stop": "Finished normally",
                "length": "Cut off: hit the token limit",
                "tool_calls": "Wants to call a tool",
                "content_filter": "Blocked by the content filter",
            }


            def describe(reason):
                return REASONS.get(reason, "Unknown reason")
        ''',
        "tests": make_tests("from solution import describe", r'''

            def test_known_reasons():
                assert describe("stop") == "Finished normally"
                assert describe("length") == "Cut off: hit the token limit"
                assert describe("tool_calls") == "Wants to call a tool"
                assert describe("content_filter") == "Blocked by the content filter"

            def test_unknown_reason():
                assert describe("weird") == "Unknown reason"

            def test_style_at_most_one_if():
                count = len(found(ast.If))
                assert count <= 1, f"{count} if/elif branches; a dict can map each reason to its words"
        ''', 8),
        "hints": [
            "Each branch maps one fixed string to another. That's what a dict is for.",
            "Put the four known reasons in a dict, and use a lookup that has a fallback for anything else.",
            "Define the dict once at module level, then return a lookup on it with \"Unknown reason\" as the default.",
        ],
    },
    {
        "id": "functions-rf1", "topic": "functions", "kind": "refactor", "title": "Refactor: is the reply usable?",
        "difficulty": 2, "concepts": ["returning booleans"],
        "prompt": r'''
            ''' + LEAD + r'''

            `usable(reply, max_chars)` is `True` when the reply has some non-space text and is at most `max_chars`
            long, else `False`.

            **Style checks**
            - No `if` statements: return the condition itself.
            - The whole file fits in **2 lines** of code.

            **Examples**
            ```python
            usable("Paris", 10)     # returns True
            usable("   ", 10)       # returns False
            usable("x" * 20, 10)    # returns False
            ```
        ''',
        "starter": r'''
            def usable(reply, max_chars):
                if reply.strip() != "":
                    if len(reply) <= max_chars:
                        return True
                    else:
                        return False
                else:
                    return False
        ''',
        "solution": r'''
            def usable(reply, max_chars):
                return bool(reply.strip()) and len(reply) <= max_chars
        ''',
        "tests": make_tests("from solution import usable", r'''

            def test_good_reply():
                assert usable("Paris", 10) is True

            def test_blank_reply():
                assert usable("   ", 10) is False
                assert usable("", 10) is False

            def test_too_long():
                assert usable("x" * 20, 10) is False

            def test_exactly_at_the_limit():
                assert usable("x" * 10, 10) is True

            def test_style_no_if():
                assert not found(ast.If), "return the condition itself instead of if ...: return True"
        ''', 2),
        "hints": [
            "`if condition: return True else: return False` is just a long way to write the condition.",
            "Both checks must hold, so combine them with the boolean operator for \"both\".",
            "Return one expression: the stripped reply turned into a bool, combined with the length comparison.",
        ],
    },
    {
        "id": "sorting-rf1", "topic": "sorting", "kind": "refactor", "title": "Refactor: the best match", "difficulty": 2,
        "concepts": ["max() with key"],
        "prompt": r'''
            ''' + LEAD + r'''

            `best(results)` returns the result dict with the highest `"score"`; if several share it, the first one
            in the list. An empty list returns `None`.

            **Style checks**
            - No `for` loops: use a built-in that finds the largest item by a key.
            - The whole file fits in **2 lines** of code.

            **Examples**
            ```python
            best([{"id": "a", "score": 0.2}, {"id": "b", "score": 0.9}])   # returns {"id": "b", "score": 0.9}
            best([])                                                    # returns None
            ```
        ''',
        "starter": r'''
            def best(results):
                if not results:
                    return None
                top = results[0]
                for result in results:
                    if result["score"] > top["score"]:
                        top = result
                return top
        ''',
        "solution": r'''
            def best(results):
                return max(results, key=lambda r: r["score"], default=None)
        ''',
        "tests": make_tests("from solution import best", r'''

            def test_highest_score():
                assert best([{"id": "a", "score": 0.2}, {"id": "b", "score": 0.9}])["id"] == "b"

            def test_first_of_a_tie():
                assert best([{"id": "a", "score": 0.5}, {"id": "b", "score": 0.5}])["id"] == "a"

            def test_empty():
                assert best([]) is None

            def test_style_no_for_loop():
                assert not found(ast.For), "a built-in can find the largest item by a key, no loop needed"
        ''', 2),
        "hints": [
            "Finding the biggest thing by some measure is common enough to have a built-in.",
            "That built-in takes a `key` function, and a `default` for an empty input.",
            "Return the built-in applied to the results, with a key that reads the score and None as the default.",
        ],
    },
    {
        "id": "files-rf1", "topic": "files", "kind": "refactor", "title": "Refactor: read a prompt file", "difficulty": 2,
        "concepts": ["with", "pathlib"],
        "setup_files": {"prompt.txt": "You are a helpful assistant.\n"},
        "prompt": r'''
            ''' + LEAD + r'''

            `read_prompt(path)` returns the text of a UTF-8 file with surrounding whitespace removed.

            **Style checks**
            - No `.close()` calls: let a `with` block (or `pathlib`) close the file for you.
            - The whole file fits in **3 lines** of code.

            **Examples**
            ```python
            read_prompt("prompt.txt")   # returns "You are a helpful assistant."
            ```
        ''',
        "starter": r'''
            def read_prompt(path):
                f = open(path, encoding="utf-8")
                text = f.read()
                f.close()
                text = text.strip()
                return text
        ''',
        "solution": r'''
            def read_prompt(path):
                with open(path, encoding="utf-8") as f:
                    return f.read().strip()
        ''',
        "tests": make_tests("from solution import read_prompt", r'''

            def test_reads_and_strips():
                assert read_prompt("prompt.txt") == "You are a helpful assistant."

            def test_style_no_close():
                calls = [n for n in found(ast.Call) if isinstance(n.func, ast.Attribute) and n.func.attr == "close"]
                assert not calls, "let a with block close the file instead of calling .close()"
        ''', 3),
        "hints": [
            "If `read()` raised an error, this version would never close the file.",
            "A `with` block closes the file for you when the block ends, even after an error.",
            "Open the file in a with statement and return the stripped contents from inside it.",
        ],
    },
    {
        "id": "errors-rf1", "topic": "errors", "kind": "refactor", "title": "Refactor: get the reply text", "difficulty": 2,
        "concepts": ["EAFP", "try/except"],
        "prompt": r'''
            ''' + LEAD + r'''

            `reply_text(response)` returns `response["choices"][0]["message"]["content"]`, or `None` when any part
            of that path is missing (no `"choices"`, an empty list, no `"message"`, no `"content"`).

            **Style checks**
            - No `if` statements: try the lookup and handle the errors it can raise.
            - The whole file fits in **5 lines** of code.

            **Examples**
            ```python
            reply_text({"choices": [{"message": {"content": "Hi"}}]})   # returns "Hi"
            reply_text({"choices": []})                                 # returns None
            ```
        ''',
        "starter": r'''
            def reply_text(response):
                if "choices" in response:
                    choices = response["choices"]
                    if len(choices) > 0:
                        first = choices[0]
                        if "message" in first:
                            message = first["message"]
                            if "content" in message:
                                return message["content"]
                return None
        ''',
        "solution": r'''
            def reply_text(response):
                try:
                    return response["choices"][0]["message"]["content"]
                except (KeyError, IndexError):
                    return None
        ''',
        "tests": make_tests("from solution import reply_text", r'''

            def test_full_path():
                assert reply_text({"choices": [{"message": {"content": "Hi"}}]}) == "Hi"

            def test_missing_parts():
                for response in ({}, {"choices": []}, {"choices": [{}]}, {"choices": [{"message": {}}]}):
                    assert reply_text(response) is None, f"expected None for {response!r}"

            def test_style_no_if():
                assert not found(ast.If), "try the whole lookup once and catch what it can raise"
        ''', 5),
        "hints": [
            "Each if guards against one way the lookup could fail. Python has a tidier way: ask forgiveness, not permission.",
            "Do the whole lookup in one expression, and catch the two exceptions a missing key or an empty list raise.",
            "Put the chained lookup in a try block and return None from an except that catches the missing-key and "
            "bad-index errors.",
        ],
    },
    {
        "id": "dataclasses-rf1", "topic": "dataclasses", "kind": "refactor", "title": "Refactor: a usage record", "difficulty": 2,
        "concepts": ["@dataclass"],
        "prompt": r'''
            ''' + LEAD + r'''

            `Usage(model, prompt_tokens, completion_tokens)` stores one API call's token usage. Two records with the
            same values are equal, the repr looks like
            `Usage(model='small', prompt_tokens=10, completion_tokens=5)`, and `.total()` returns the two counts added.

            **Style checks**
            - Use `@dataclass`: no hand-written `__init__`, `__repr__` or `__eq__`.
            - The whole file fits in **9 lines** of code.

            **Examples**
            ```python
            u = Usage("small", 10, 5)
            u.total()                     # returns 15
            u == Usage("small", 10, 5)    # True
            ```
        ''',
        "starter": r'''
            class Usage:
                def __init__(self, model, prompt_tokens, completion_tokens):
                    self.model = model
                    self.prompt_tokens = prompt_tokens
                    self.completion_tokens = completion_tokens

                def __repr__(self):
                    return (f"Usage(model={self.model!r}, prompt_tokens={self.prompt_tokens!r}, "
                            f"completion_tokens={self.completion_tokens!r})")

                def __eq__(self, other):
                    if not isinstance(other, Usage):
                        return NotImplemented
                    return (self.model, self.prompt_tokens, self.completion_tokens) == (
                        other.model, other.prompt_tokens, other.completion_tokens)

                def total(self):
                    return self.prompt_tokens + self.completion_tokens
        ''',
        "solution": r'''
            from dataclasses import dataclass


            @dataclass
            class Usage:
                model: str
                prompt_tokens: int
                completion_tokens: int

                def total(self):
                    return self.prompt_tokens + self.completion_tokens
        ''',
        "tests": make_tests("from solution import Usage", r'''

            def test_fields_and_total():
                u = Usage("small", 10, 5)
                assert (u.model, u.prompt_tokens, u.completion_tokens, u.total()) == ("small", 10, 5, 15)

            def test_equality_and_repr():
                assert Usage("small", 10, 5) == Usage("small", 10, 5)
                assert Usage("small", 10, 5) != Usage("small", 10, 6)
                assert repr(Usage("small", 10, 5)) == "Usage(model='small', prompt_tokens=10, completion_tokens=5)"

            def test_style_uses_dataclass():
                names = {f.name for f in found(ast.FunctionDef)}
                assert not names & {"__init__", "__repr__", "__eq__"}, "let @dataclass write __init__, __repr__ and __eq__"
                assert "dataclass" in source(), "decorate the class with @dataclass"
        ''', 9),
        "hints": [
            "Three of these four methods are exactly what a dataclass writes for you.",
            "Declare the three fields with type annotations in the class body, and keep only the method that is really yours.",
            "Import the dataclass decorator, put it above the class, list the fields with their types, and keep total().",
        ],
    },
]
