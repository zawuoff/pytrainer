"""Bug hunts: code that looks right and passes its examples, but has one small bug.

The starter is the buggy code. It passes ``visible_tests`` (the examples in the prompt) and fails
the hidden ``tests``, which cover the edge case the rules describe. The fix is small: the learner
reads the rules, finds the input that breaks it (Run or Debug helps), and changes a line or two.
"""

LEAD = ("A teammate wrote this and it passes every example below, but users have hit a bug. "
        "**Your job:** find the bug and fix it. It's small: change the code, don't rewrite it.")

EXTRAS = [
    {
        "id": "lists-bh1", "topic": "lists", "kind": "bughunt", "title": "Bug hunt: keep the last n messages",
        "difficulty": 2, "concepts": ["negative indexes", "slicing"],
        "prompt": r'''
            A chat app keeps only the most recent messages so the prompt stays short. ''' + LEAD + r'''

            **What goes in**

            - `messages`: a list of strings, oldest first
            - `n`: how many of the newest messages to keep (0 or more)

            **What comes out**
            - a new list with the last `n` messages, oldest first

            **Rules**
            - `n` larger than the list keeps everything.
            - `n` of 0 keeps nothing.

            **Examples**
            ```python
            last_n(["a", "b", "c", "d"], 2)   # returns ["c", "d"]
            last_n(["a", "b"], 5)             # returns ["a", "b"]
            ```
        ''',
        "starter": r'''
            def last_n(messages, n):
                return messages[-n:]
        ''',
        "solution": r'''
            def last_n(messages, n):
                return messages[len(messages) - n:] if n < len(messages) else messages[:]
        ''',
        "visible_tests": r'''
            from solution import last_n

            def test_examples():
                assert last_n(["a", "b", "c", "d"], 2) == ["c", "d"]
                assert last_n(["a", "b"], 5) == ["a", "b"]
        ''',
        "tests": r'''
            from solution import last_n

            def test_keeps_the_newest():
                assert last_n(["a", "b", "c", "d"], 2) == ["c", "d"]

            def test_n_larger_than_the_list():
                assert last_n(["a", "b"], 5) == ["a", "b"]

            def test_n_zero_keeps_nothing():
                got = last_n(["a", "b", "c"], 0)
                assert got == [], f"last_n(['a', 'b', 'c'], 0) returned {got!r}"

            def test_returns_a_new_list():
                msgs = ["a", "b"]
                assert last_n(msgs, 5) is not msgs, "return a new list, not the same object"
        ''',
        "hints": [
            "Read the rules again and try each one that the examples don't show.",
            "Run it with n set to 0. Think about what a slice starting at -0 means.",
            "Negative zero is just zero, so that slice starts at the beginning. Compute the start position from the "
            "length instead, and make sure a new list comes back in every case.",
        ],
    },
    {
        "id": "loops-bh1", "topic": "loops", "kind": "bughunt", "title": "Bug hunt: find the first long message",
        "difficulty": 2, "concepts": ["for loops", "return inside a loop"],
        "prompt": r'''
            Before sending a conversation, an app looks for the first message that is too long. ''' + LEAD + r'''

            **What goes in**

            - `messages`: a list of strings
            - `limit`: the most characters a message may have

            **What comes out**
            - the first message longer than `limit`, or `None` if there is none

            **Examples**
            ```python
            first_too_long(["a very long message", "ok"], 5)   # returns "a very long message"
            first_too_long(["ok", "fine"], 10)                 # returns None
            ```
        ''',
        "starter": r'''
            def first_too_long(messages, limit):
                for message in messages:
                    if len(message) > limit:
                        return message
                    else:
                        return None
        ''',
        "solution": r'''
            def first_too_long(messages, limit):
                for message in messages:
                    if len(message) > limit:
                        return message
                return None
        ''',
        "visible_tests": r'''
            from solution import first_too_long

            def test_examples():
                assert first_too_long(["a very long message", "ok"], 5) == "a very long message"
                assert first_too_long(["ok", "fine"], 10) is None
        ''',
        "tests": r'''
            from solution import first_too_long

            def test_first_message_too_long():
                assert first_too_long(["a very long message", "ok"], 5) == "a very long message"

            def test_none_too_long():
                assert first_too_long(["ok", "fine"], 10) is None

            def test_long_message_later_in_the_list():
                got = first_too_long(["ok", "fine", "this one is far too long"], 10)
                assert got == "this one is far too long", f"got {got!r}"

            def test_empty_list():
                assert first_too_long([], 3) is None
        ''',
        "hints": [
            "The examples only ever have the long message first. What if it comes later?",
            "Step through it with the debugger on a list where the long message is third, and watch when it returns.",
            "Returning None belongs after the loop has looked at every message, not inside it.",
        ],
    },
    {
        "id": "dicts-bh1", "topic": "dicts", "kind": "bughunt", "title": "Bug hunt: merge model settings",
        "difficulty": 2, "concepts": ["dict copies", "mutation"],
        "prompt": r'''
            Every request starts from default model settings, with per-request overrides on top. ''' + LEAD + r'''

            **What goes in**

            - `defaults`: a dict of default settings
            - `overrides`: a dict of settings for this request

            **What comes out**
            - a new dict: the defaults, with the overrides replacing or adding keys

            **Rules**
            - Neither input dict is changed. The defaults are shared by every request.

            **Examples**
            ```python
            merge({"model": "small", "temperature": 0.7}, {"temperature": 0})
            # returns {"model": "small", "temperature": 0}
            merge({"model": "small"}, {"max_tokens": 50})
            # returns {"model": "small", "max_tokens": 50}
            ```
        ''',
        "starter": r'''
            def merge(defaults, overrides):
                settings = defaults
                settings.update(overrides)
                return settings
        ''',
        "solution": r'''
            def merge(defaults, overrides):
                settings = dict(defaults)
                settings.update(overrides)
                return settings
        ''',
        "visible_tests": r'''
            from solution import merge

            def test_examples():
                assert merge({"model": "small", "temperature": 0.7}, {"temperature": 0}) == {"model": "small", "temperature": 0}
                assert merge({"model": "small"}, {"max_tokens": 50}) == {"model": "small", "max_tokens": 50}
        ''',
        "tests": r'''
            from solution import merge

            def test_override_replaces():
                assert merge({"model": "small", "temperature": 0.7}, {"temperature": 0}) == {"model": "small", "temperature": 0}

            def test_override_adds():
                assert merge({"model": "small"}, {"max_tokens": 50}) == {"model": "small", "max_tokens": 50}

            def test_defaults_are_not_changed():
                defaults = {"model": "small", "temperature": 0.7}
                merge(defaults, {"temperature": 0})
                assert defaults == {"model": "small", "temperature": 0.7}, f"defaults became {defaults!r}"

            def test_second_request_starts_from_clean_defaults():
                defaults = {"model": "small"}
                merge(defaults, {"max_tokens": 50})
                assert merge(defaults, {}) == {"model": "small"}
        ''',
        "hints": [
            "The rules say something the examples never check: what happens to `defaults` afterwards?",
            "Call it twice with the same defaults dict and print the defaults between the calls.",
            "`settings = defaults` gives the same dict a second name. Start from a copy instead.",
        ],
    },
    {
        "id": "functions-bh1", "topic": "functions", "kind": "bughunt", "title": "Bug hunt: start a conversation",
        "difficulty": 2, "concepts": ["default arguments", "mutable defaults"],
        "prompt": r'''
            A helper starts a new conversation with a system message, optionally after some earlier
            messages. ''' + LEAD + r'''

            **What goes in**

            - `system`: the system prompt text
            - `history`: an optional list of earlier message dicts (default: no history)

            **What comes out**
            - a new list: the history, then `{"role": "system", "content": system}`

            **Rules**
            - Every call returns its own list; calls never affect each other.
            - The `history` list passed in is not changed.

            **Examples**
            ```python
            start("Be brief.")   # returns [{"role": "system", "content": "Be brief."}]
            start("Hi", [{"role": "user", "content": "yo"}])
            # returns [{"role": "user", "content": "yo"}, {"role": "system", "content": "Hi"}]
            ```
        ''',
        "starter": r'''
            def start(system, history=[]):
                history.append({"role": "system", "content": system})
                return history
        ''',
        "solution": r'''
            def start(system, history=None):
                return list(history or []) + [{"role": "system", "content": system}]
        ''',
        "visible_tests": r'''
            from solution import start

            def test_examples():
                assert start("Hi", [{"role": "user", "content": "yo"}]) == [
                    {"role": "user", "content": "yo"}, {"role": "system", "content": "Hi"}]
                assert start("Be brief.") == [{"role": "system", "content": "Be brief."}]
        ''',
        "tests": r'''
            from solution import start

            def test_without_history():
                assert start("Be brief.") == [{"role": "system", "content": "Be brief."}]

            def test_two_calls_without_history_are_independent():
                start("first")
                got = start("second")
                assert got == [{"role": "system", "content": "second"}], f"second call returned {got!r}"

            def test_history_is_not_changed():
                history = [{"role": "user", "content": "yo"}]
                got = start("Hi", history)
                assert got == [{"role": "user", "content": "yo"}, {"role": "system", "content": "Hi"}]
                assert history == [{"role": "user", "content": "yo"}], f"history became {history!r}"
        ''',
        "hints": [
            "Call it twice in a row without a history and look at the second result.",
            "A default value is created once, when the function is defined, not on every call.",
            "Use None as the default and build a fresh list inside the function, copying the history instead of "
            "appending to it.",
        ],
    },
    {
        "id": "strings-bh1", "topic": "strings", "kind": "bughunt", "title": "Bug hunt: truncate for a preview",
        "difficulty": 2, "concepts": ["string length", "boundaries"],
        "prompt": r'''
            A dashboard shows model replies cut to a fixed width, ending in `...` when they were cut. ''' + LEAD + r'''

            **What goes in**

            - `text`: a string
            - `limit`: the most characters the preview may have (at least 4)

            **What comes out**
            - `text` unchanged if it fits in `limit` characters, otherwise the first `limit - 3` characters
              followed by `...` (so the result is exactly `limit` long)

            **Examples**
            ```python
            preview("hello", 10)          # returns "hello"
            preview("hello world", 8)     # returns "hello..."
            ```
        ''',
        "starter": r'''
            def preview(text, limit):
                if len(text) < limit:
                    return text
                return text[:limit - 3] + "..."
        ''',
        "solution": r'''
            def preview(text, limit):
                if len(text) <= limit:
                    return text
                return text[:limit - 3] + "..."
        ''',
        "visible_tests": r'''
            from solution import preview

            def test_examples():
                assert preview("hello", 10) == "hello"
                assert preview("hello world", 8) == "hello..."
        ''',
        "tests": r'''
            from solution import preview

            def test_short_text_unchanged():
                assert preview("hello", 10) == "hello"

            def test_long_text_cut():
                assert preview("hello world", 8) == "hello..."

            def test_text_exactly_at_the_limit_is_unchanged():
                got = preview("exactly10!", 10)
                assert got == "exactly10!", f"preview('exactly10!', 10) returned {got!r}"
        ''',
        "hints": [
            "The examples test a text that is shorter and one that is longer. What about a text of exactly `limit` characters?",
            "Try a 10-character text with a limit of 10. Does it fit?",
            "Check the comparison that decides whether the text fits.",
        ],
    },
    {
        "id": "errors-bh1", "topic": "errors", "kind": "bughunt", "title": "Bug hunt: parse a temperature",
        "difficulty": 2, "concepts": ["try/except scope", "raise"],
        "prompt": r'''
            A settings form reads the model temperature as text. ''' + LEAD + r'''

            **What goes in**

            - `text`: what the user typed

            **What comes out**
            - the temperature as a float

            **Rules**
            - Text that isn't a number gives the default, `1.0`.
            - A number outside 0 to 2 (inclusive) raises `ValueError`, so the form can show an error.

            **Examples**
            ```python
            parse_temperature("0.7")   # returns 0.7
            parse_temperature("hot")   # returns 1.0
            ```
        ''',
        "starter": r'''
            def parse_temperature(text):
                try:
                    value = float(text)
                    if not 0 <= value <= 2:
                        raise ValueError(f"temperature {value} is outside 0-2")
                    return value
                except ValueError:
                    return 1.0
        ''',
        "solution": r'''
            def parse_temperature(text):
                try:
                    value = float(text)
                except ValueError:
                    return 1.0
                if not 0 <= value <= 2:
                    raise ValueError(f"temperature {value} is outside 0-2")
                return value
        ''',
        "visible_tests": r'''
            from solution import parse_temperature

            def test_examples():
                assert parse_temperature("0.7") == 0.7
                assert parse_temperature("hot") == 1.0
        ''',
        "tests": r'''
            from solution import parse_temperature

            def test_number():
                assert parse_temperature("0.7") == 0.7

            def test_not_a_number_gives_the_default():
                assert parse_temperature("hot") == 1.0

            def test_edges_are_allowed():
                assert parse_temperature("0") == 0.0 and parse_temperature("2") == 2.0

            def test_out_of_range_raises():
                for text in ("5", "-0.1"):
                    try:
                        got = parse_temperature(text)
                    except ValueError:
                        continue
                    assert False, f"parse_temperature({text!r}) returned {got!r} instead of raising ValueError"
        ''',
        "hints": [
            "Try a number that is too big, like \"5\". What should happen, and what does?",
            "The ValueError raised for the range check is caught by the same `except` meant for bad text.",
            "Make the `try` cover only the conversion to float, and do the range check after it.",
        ],
    },
    {
        "id": "comprehensions-bh1", "topic": "comprehensions", "kind": "bughunt", "title": "Bug hunt: passing eval cases",
        "difficulty": 2, "concepts": ["comprehension filters", "comparisons"],
        "prompt": r'''
            An eval report lists the cases whose score reached the passing threshold. ''' + LEAD + r'''

            **What goes in**

            - `results`: a list of `(case_id, score)` tuples
            - `threshold`: the passing score

            **What comes out**
            - the ids of the cases that pass, in the same order

            **Rules**
            - A case passes when its score is at least the threshold.

            **Examples**
            ```python
            passing([("a", 0.9), ("b", 0.4), ("c", 0.75)], 0.7)   # returns ["a", "c"]
            passing([("a", 0.1)], 0.5)                            # returns []
            ```
        ''',
        "starter": r'''
            def passing(results, threshold):
                return [case_id for case_id, score in results if score > threshold]
        ''',
        "solution": r'''
            def passing(results, threshold):
                return [case_id for case_id, score in results if score >= threshold]
        ''',
        "visible_tests": r'''
            from solution import passing

            def test_examples():
                assert passing([("a", 0.9), ("b", 0.4), ("c", 0.75)], 0.7) == ["a", "c"]
                assert passing([("a", 0.1)], 0.5) == []
        ''',
        "tests": r'''
            from solution import passing

            def test_keeps_scores_above():
                assert passing([("a", 0.9), ("b", 0.4), ("c", 0.75)], 0.7) == ["a", "c"]

            def test_none_pass():
                assert passing([("a", 0.1)], 0.5) == []

            def test_score_equal_to_threshold_passes():
                got = passing([("a", 0.5), ("b", 0.49)], 0.5)
                assert got == ["a"], f"got {got!r}"
        ''',
        "hints": [
            "\"At least the threshold\" includes one score the examples never use.",
            "Try a case whose score is exactly the threshold.",
            "Check the comparison in the filter part of the comprehension.",
        ],
    },
    {
        "id": "sorting-bh1", "topic": "sorting", "kind": "bughunt", "title": "Bug hunt: rank search results",
        "difficulty": 2, "concepts": ["sort keys", "reverse"],
        "prompt": r'''
            Search results are shown best first; results with the same score are listed by title so the order
            never changes between runs. ''' + LEAD + r'''

            **What goes in**

            - `results`: a list of dicts with `"title"` and `"score"`

            **What comes out**
            - a new list: highest score first, and equal scores in alphabetical title order

            **Examples**
            ```python
            rank([{"title": "B", "score": 0.2}, {"title": "A", "score": 0.9}])
            # returns [{"title": "A", "score": 0.9}, {"title": "B", "score": 0.2}]
            ```
        ''',
        "starter": r'''
            def rank(results):
                return sorted(results, key=lambda r: (r["score"], r["title"]), reverse=True)
        ''',
        "solution": r'''
            def rank(results):
                return sorted(results, key=lambda r: (-r["score"], r["title"]))
        ''',
        "visible_tests": r'''
            from solution import rank

            def test_examples():
                got = rank([{"title": "B", "score": 0.2}, {"title": "A", "score": 0.9}])
                assert got == [{"title": "A", "score": 0.9}, {"title": "B", "score": 0.2}]
        ''',
        "tests": r'''
            from solution import rank

            def test_best_first():
                got = rank([{"title": "B", "score": 0.2}, {"title": "A", "score": 0.9}])
                assert [r["title"] for r in got] == ["A", "B"]

            def test_ties_in_title_order():
                got = rank([{"title": "Alpha", "score": 0.5}, {"title": "Zulu", "score": 0.5}, {"title": "Mid", "score": 0.8}])
                assert [r["title"] for r in got] == ["Mid", "Alpha", "Zulu"], f"order: {[r['title'] for r in got]}"
        ''',
        "hints": [
            "The example has no ties. Try two results with the same score.",
            "`reverse=True` reverses the whole key, the title part included.",
            "Sort by the negative score, then the title, without reversing.",
        ],
    },
    {
        "id": "classes-bh1", "topic": "classes", "kind": "bughunt", "title": "Bug hunt: one history per chat",
        "difficulty": 2, "concepts": ["class vs instance attributes"],
        "prompt": r'''
            Each `Chat` object keeps its own message history. ''' + LEAD + r'''

            **What goes in**

            - `Chat()` creates an empty chat; `chat.add(role, content)` appends a message dict

            **What comes out**
            - `chat.messages`: that chat's list of `{"role": ..., "content": ...}` dicts

            **Rules**
            - Two chats never share messages.

            **Examples**
            ```python
            chat = Chat()
            chat.add("user", "hi")
            chat.messages   # [{"role": "user", "content": "hi"}]
            ```
        ''',
        "starter": r'''
            class Chat:
                messages = []

                def add(self, role, content):
                    self.messages.append({"role": role, "content": content})
        ''',
        "solution": r'''
            class Chat:
                def __init__(self):
                    self.messages = []

                def add(self, role, content):
                    self.messages.append({"role": role, "content": content})
        ''',
        "visible_tests": r'''
            from solution import Chat

            def test_examples():
                chat = Chat()
                chat.add("user", "hi")
                assert chat.messages == [{"role": "user", "content": "hi"}]
        ''',
        "tests": r'''
            from solution import Chat

            def test_add_one_message():
                chat = Chat()
                chat.add("user", "hi")
                assert chat.messages == [{"role": "user", "content": "hi"}]

            def test_two_chats_are_separate():
                a, b = Chat(), Chat()
                a.add("user", "only in a")
                assert b.messages == [], f"a new chat already has {b.messages!r}"
        ''',
        "hints": [
            "Make two chats and add a message to just one of them.",
            "A list written in the class body belongs to the class, so every instance sees the same one.",
            "Give each instance its own list when it is created.",
        ],
    },
    {
        "id": "regex-bh1", "topic": "regex", "kind": "bughunt", "title": "Bug hunt: find email addresses",
        "difficulty": 2, "concepts": ["character classes", "quantifiers"],
        "prompt": r'''
            Before a support ticket goes to a model, the app finds the email addresses in it. ''' + LEAD + r'''

            **What goes in**

            - `text`: the ticket text

            **What comes out**
            - every full email address in the text, in order

            **Rules**
            - The part before `@` may contain letters, digits, `.`, `_`, `+` and `-`.
            - The domain is one or more dot-separated parts, like `example.com` or `mail.example.co.uk`.

            **Examples**
            ```python
            find_emails("Write to ada@example.com today")   # returns ["ada@example.com"]
            find_emails("no address here")                  # returns []
            ```
        ''',
        "starter": r'''
            import re


            def find_emails(text):
                return re.findall(r"\w+@\w+\.\w+", text)
        ''',
        "solution": r'''
            import re


            def find_emails(text):
                return re.findall(r"[\w.+-]+@\w[\w-]*(?:\.[\w-]+)+", text)
        ''',
        "visible_tests": r'''
            from solution import find_emails

            def test_examples():
                assert find_emails("Write to ada@example.com today") == ["ada@example.com"]
                assert find_emails("no address here") == []
        ''',
        "tests": r'''
            from solution import find_emails

            def test_simple_address():
                assert find_emails("Write to ada@example.com today") == ["ada@example.com"]

            def test_none():
                assert find_emails("no address here") == []

            def test_dots_and_plus_before_the_at():
                got = find_emails("cc ada.lovelace+ai@example.com")
                assert got == ["ada.lovelace+ai@example.com"], f"got {got!r}"

            def test_domain_with_several_parts():
                got = find_emails("from bob@mail.example.co.uk, thanks")
                assert got == ["bob@mail.example.co.uk"], f"got {got!r}"
        ''',
        "hints": [
            "Try the kinds of address the rules mention but the examples don't: a dot or + before the @, and a "
            "domain with more than one dot.",
            "`\\w` matches letters, digits and underscores only, and the pattern allows exactly one dot after the @.",
            "Widen the character class before the @, and let the domain repeat \"a dot and a part\" one or more times.",
        ],
    },
    {
        "id": "json-bh1", "topic": "json", "kind": "bughunt", "title": "Bug hunt: read the temperature setting",
        "difficulty": 2, "concepts": ["truthiness", "dict.get"],
        "prompt": r'''
            An app reads model settings from a JSON string; a missing temperature means 0.7. ''' + LEAD + r'''

            **What goes in**

            - `text`: a JSON object as a string

            **What comes out**
            - the temperature as a number

            **Rules**
            - A missing `"temperature"` key gives `0.7`.
            - Any temperature that is there is used as is, including `0`.

            **Examples**
            ```python
            read_temperature('{"temperature": 0.2}')   # returns 0.2
            read_temperature('{"model": "small"}')     # returns 0.7
            ```
        ''',
        "starter": r'''
            import json


            def read_temperature(text):
                settings = json.loads(text)
                return settings.get("temperature") or 0.7
        ''',
        "solution": r'''
            import json


            def read_temperature(text):
                settings = json.loads(text)
                return settings.get("temperature", 0.7)
        ''',
        "visible_tests": r'''
            from solution import read_temperature

            def test_examples():
                assert read_temperature('{"temperature": 0.2}') == 0.2
                assert read_temperature('{"model": "small"}') == 0.7
        ''',
        "tests": r'''
            from solution import read_temperature

            def test_value_is_used():
                assert read_temperature('{"temperature": 0.2}') == 0.2

            def test_missing_gives_default():
                assert read_temperature('{"model": "small"}') == 0.7

            def test_zero_is_kept():
                got = read_temperature('{"temperature": 0}')
                assert got == 0, f"a temperature of 0 came back as {got!r}"
        ''',
        "hints": [
            "The rules mention one temperature value specially. Try it.",
            "`x or default` uses the default whenever x is falsy, and 0 is falsy.",
            "Give the default to the lookup itself, so it is only used when the key is missing.",
        ],
    },
    {
        "id": "chunking-bh1", "topic": "chunking", "kind": "bughunt", "title": "Bug hunt: fixed-size chunks",
        "difficulty": 2, "concepts": ["range", "off-by-one"],
        "prompt": r'''
            A simple chunker cuts a text into pieces of `size` characters for embedding. ''' + LEAD + r'''

            **What goes in**

            - `text`: a string
            - `size`: the chunk length (at least 1)

            **What comes out**
            - a list of chunks, in order; joined together they give back the whole text

            **Rules**
            - Every chunk is `size` long except possibly the last, which holds what's left.
            - An empty text gives `[]`.

            **Examples**
            ```python
            chunks("abcdefghij", 5)   # returns ["abcde", "fghij"]
            chunks("abcd", 2)         # returns ["ab", "cd"]
            ```
        ''',
        "starter": r'''
            def chunks(text, size):
                return [text[i:i + size] for i in range(0, len(text) - size + 1, size)]
        ''',
        "solution": r'''
            def chunks(text, size):
                return [text[i:i + size] for i in range(0, len(text), size)]
        ''',
        "visible_tests": r'''
            from solution import chunks

            def test_examples():
                assert chunks("abcdefghij", 5) == ["abcde", "fghij"]
                assert chunks("abcd", 2) == ["ab", "cd"]
        ''',
        "tests": r'''
            from solution import chunks

            def test_even_split():
                assert chunks("abcdefghij", 5) == ["abcde", "fghij"]

            def test_leftover_becomes_the_last_chunk():
                got = chunks("abcdefg", 3)
                assert got == ["abc", "def", "g"], f"got {got!r}"

            def test_text_shorter_than_size():
                assert chunks("ab", 5) == ["ab"]

            def test_empty_text():
                assert chunks("", 3) == []
        ''',
        "hints": [
            "Both examples divide evenly. Try a length that doesn't.",
            "Look at where the range stops: which start positions does it never reach?",
            "Every start position from 0 up to the end of the text, in steps of size, should get a chunk.",
        ],
    },
    {
        "id": "vectors-bh1", "topic": "vectors", "kind": "bughunt", "title": "Bug hunt: cosine similarity",
        "difficulty": 2, "concepts": ["division by zero", "vector norms"],
        "prompt": r'''
            Retrieval scores documents by the cosine similarity of their embedding to the query's. ''' + LEAD + r'''

            **What goes in**

            - `a`, `b`: two lists of numbers of the same length

            **What comes out**
            - their cosine similarity, a float

            **Rules**
            - If either vector is all zeros (length 0), the similarity is `0.0`.

            **Examples**
            ```python
            cosine([1, 0], [1, 0])   # returns 1.0
            cosine([1, 0], [0, 1])   # returns 0.0
            ```
        ''',
        "starter": r'''
            import math


            def cosine(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
        ''',
        "solution": r'''
            import math


            def cosine(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                norms = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
                return dot / norms if norms else 0.0
        ''',
        "visible_tests": r'''
            from solution import cosine

            def test_examples():
                assert cosine([1, 0], [1, 0]) == 1.0
                assert cosine([1, 0], [0, 1]) == 0.0
        ''',
        "tests": r'''
            import math
            from solution import cosine

            def test_same_direction():
                assert math.isclose(cosine([1, 0], [1, 0]), 1.0)

            def test_perpendicular():
                assert math.isclose(cosine([1, 0], [0, 1]), 0.0, abs_tol=1e-12)

            def test_general_case():
                assert math.isclose(cosine([1, 2], [2, 1]), 0.8)

            def test_zero_vector_gives_zero():
                got = cosine([0, 0], [1, 2])
                assert got == 0.0, f"got {got!r}"
        ''',
        "hints": [
            "The rules mention one input the examples never use.",
            "Run it with a vector of zeros. What does Python do when you divide by 0?",
            "Compute the product of the two lengths first, and return 0.0 when it is zero.",
        ],
    },
]
