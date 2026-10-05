"""Whole-function Parsons problems: put shuffled lines in order and indent them.

The lines are the reference solution's, stripped of indentation and shuffled, plus a few
``distractors`` that don't belong. The arrangement is graded by the normal hidden tests, so any
order that works passes. Solutions here avoid blank-line-sensitive constructs, comments and
multi-line strings, since every non-blank line becomes one tile.
"""

LEAD = ("**Your job:** put the lines in order and indent them to build the function. "
        "Not every line belongs: leave the extra ones out.")

EXTRAS = [
    {
        "id": "functions-pz1", "topic": "functions", "kind": "parsons", "title": "Put it in order: count words",
        "difficulty": 2, "concepts": ["def", "return"],
        "prompt": r'''
            Build `count_words(text, min_length)`: how many whitespace-separated words in `text` have at least
            `min_length` characters.

            ''' + LEAD + r'''

            **Examples**
            ```python
            count_words("a big model", 3)   # returns 2
            count_words("", 1)              # returns 0
            ```
        ''',
        "solution": r'''
            def count_words(text, min_length):
                count = 0
                for word in text.split():
                    if len(word) >= min_length:
                        count += 1
                return count
        ''',
        "distractors": ["return count + 1", "for word in text:"],
        "starter": "",
        "tests": r'''
            from solution import count_words

            def test_counts_long_enough_words():
                assert count_words("a big model", 3) == 2

            def test_empty_text():
                assert count_words("", 1) == 0

            def test_every_word():
                assert count_words("one two three", 1) == 3
        ''',
        "hints": [
            "Start with the def line, then think about what has to exist before the loop.",
            "A counter starts at 0, a loop looks at each word, a condition decides whether to count it, and the result comes back after the loop.",
            "The return line is at the same indentation as the loop, not inside it. The loop goes over the split text, not the text itself.",
        ],
    },
    {
        "id": "loops-pz1", "topic": "loops", "kind": "parsons", "title": "Put it in order: retry until success",
        "difficulty": 2, "concepts": ["while", "break"],
        "prompt": r'''
            Build `first_success(results)`: given a list of attempt results (strings), return the index of the
            first `"ok"`, or `-1` if none of them is.

            ''' + LEAD + r'''

            **Examples**
            ```python
            first_success(["timeout", "error", "ok", "ok"])   # returns 2
            first_success(["error"])                          # returns -1
            ```
        ''',
        "solution": r'''
            def first_success(results):
                for index, result in enumerate(results):
                    if result == "ok":
                        return index
                return -1
        ''',
        "distractors": ["return result", "for index in results:"],
        "starter": "",
        "tests": r'''
            from solution import first_success

            def test_finds_first_ok():
                assert first_success(["timeout", "error", "ok", "ok"]) == 2

            def test_none():
                assert first_success(["error"]) == -1
                assert first_success([]) == -1

            def test_ok_first():
                assert first_success(["ok"]) == 0
        ''',
        "hints": [
            "You need both the position and the value of each result.",
            "Loop with positions, return as soon as you find a success, and only give up after the loop.",
            "The \"not found\" return belongs at function level, after the loop has finished.",
        ],
    },
    {
        "id": "conditionals-pz1", "topic": "conditionals", "kind": "parsons", "title": "Put it in order: pick a model",
        "difficulty": 2, "concepts": ["if / elif / else"],
        "prompt": r'''
            Build `pick_model(tokens)`: prompts under 1,000 tokens use `"small"`, under 10,000 use `"medium"`,
            anything bigger uses `"large"`.

            ''' + LEAD + r'''

            **Examples**
            ```python
            pick_model(200)      # returns "small"
            pick_model(5000)     # returns "medium"
            pick_model(50000)    # returns "large"
            ```
        ''',
        "solution": r'''
            def pick_model(tokens):
                if tokens < 1000:
                    return "small"
                elif tokens < 10000:
                    return "medium"
                else:
                    return "large"
        ''',
        "distractors": ["elif tokens > 1000:", "if tokens < 10000:"],
        "starter": "",
        "tests": r'''
            from solution import pick_model

            def test_small():
                assert pick_model(200) == "small"
                assert pick_model(999) == "small"

            def test_medium():
                assert pick_model(1000) == "medium"
                assert pick_model(5000) == "medium"

            def test_large():
                assert pick_model(10000) == "large"
                assert pick_model(50000) == "large"
        ''',
        "hints": [
            "Check the smallest limit first: the first true branch wins.",
            "One if, one elif, one else, each followed by an indented return.",
            "The conditions use \"less than\", from the 1,000 limit up to the 10,000 one, with else catching the rest.",
        ],
    },
    {
        "id": "dicts-pz1", "topic": "dicts", "kind": "parsons", "title": "Put it in order: group by role", "difficulty": 2,
        "concepts": ["setdefault", "grouping"],
        "prompt": r'''
            Build `group_by_role(messages)`: given `(role, text)` pairs, return a dict from each role to the list of
            its texts, in order.

            ''' + LEAD + r'''

            **Examples**
            ```python
            group_by_role([("user", "hi"), ("assistant", "hello"), ("user", "bye")])
            # returns {"user": ["hi", "bye"], "assistant": ["hello"]}
            ```
        ''',
        "solution": r'''
            def group_by_role(messages):
                groups = {}
                for role, text in messages:
                    groups.setdefault(role, []).append(text)
                return groups
        ''',
        "distractors": ["groups[role] = text", "groups = []"],
        "starter": "",
        "tests": r'''
            from solution import group_by_role

            def test_groups_in_order():
                got = group_by_role([("user", "hi"), ("assistant", "hello"), ("user", "bye")])
                assert got == {"user": ["hi", "bye"], "assistant": ["hello"]}

            def test_empty():
                assert group_by_role([]) == {}
        ''',
        "hints": [
            "The result is a dict whose values are lists.",
            "Start with an empty dict, loop over the pairs, and add each text to its role's list.",
            "One line both creates a missing list and appends to it. Assigning the text directly would replace the list.",
        ],
    },
    {
        "id": "errors-pz1", "topic": "errors", "kind": "parsons", "title": "Put it in order: safe division", "difficulty": 2,
        "concepts": ["try / except / else"],
        "prompt": r'''
            Build `cost_per_token(cost, tokens)`: `cost / tokens`, but `0.0` when `tokens` is 0.

            ''' + LEAD + r'''

            **Examples**
            ```python
            cost_per_token(2.0, 4)   # returns 0.5
            cost_per_token(2.0, 0)   # returns 0.0
            ```
        ''',
        "solution": r'''
            def cost_per_token(cost, tokens):
                try:
                    return cost / tokens
                except ZeroDivisionError:
                    return 0.0
        ''',
        "distractors": ["except ValueError:", "finally:"],
        "starter": "",
        "tests": r'''
            from solution import cost_per_token

            def test_divides():
                assert cost_per_token(2.0, 4) == 0.5

            def test_zero_tokens():
                assert cost_per_token(2.0, 0) == 0.0
        ''',
        "hints": [
            "Which error does Python raise when you divide by zero?",
            "Try the division, and catch exactly that error to return the fallback.",
            "try and except sit at the same indentation, each with one indented return under it.",
        ],
    },
    {
        "id": "comprehensions-pz1", "topic": "comprehensions", "kind": "parsons", "title": "Put it in order: clean a batch",
        "difficulty": 2, "concepts": ["list comprehensions"],
        "prompt": r'''
            Build `clean_batch(texts)`: strip each text and drop the ones that are empty after stripping, keeping
            the order.

            ''' + LEAD + r'''

            **Examples**
            ```python
            clean_batch(["  hi ", "", "   ", "ok"])   # returns ["hi", "ok"]
            ```
        ''',
        "solution": r'''
            def clean_batch(texts):
                stripped = [text.strip() for text in texts]
                return [text for text in stripped if text]
        ''',
        "distractors": ["return [text for text in texts if text]", "stripped = texts.strip()"],
        "starter": "",
        "tests": r'''
            from solution import clean_batch

            def test_strips_and_drops_empty():
                assert clean_batch(["  hi ", "", "   ", "ok"]) == ["hi", "ok"]

            def test_all_empty():
                assert clean_batch([" ", ""]) == []
        ''',
        "hints": [
            "Two steps: strip everything, then filter.",
            "The filter must look at the stripped texts, not the originals.",
            "A list has no strip method; each string does.",
        ],
    },
    {
        "id": "classes-pz1", "topic": "classes", "kind": "parsons", "title": "Put it in order: a token budget",
        "difficulty": 2, "concepts": ["__init__", "methods", "self"],
        "prompt": r'''
            Build a `Budget` class: `Budget(limit)` starts with nothing spent, `spend(n)` adds `n` tokens, and
            `left()` returns how many tokens remain (never below 0).

            ''' + LEAD + r'''

            **Examples**
            ```python
            b = Budget(100)
            b.spend(30)
            b.left()      # returns 70
            b.spend(500)
            b.left()      # returns 0
            ```
        ''',
        "solution": r'''
            class Budget:
                def __init__(self, limit):
                    self.limit = limit
                    self.spent = 0
                def spend(self, n):
                    self.spent += n
                def left(self):
                    return max(self.limit - self.spent, 0)
        ''',
        "distractors": ["spent = 0", "return self.limit - n"],
        "starter": "",
        "tests": r'''
            from solution import Budget

            def test_spending():
                b = Budget(100)
                b.spend(30)
                assert b.left() == 70

            def test_never_below_zero():
                b = Budget(100)
                b.spend(500)
                assert b.left() == 0

            def test_starts_full():
                assert Budget(5).left() == 5
        ''',
        "hints": [
            "Three methods, each indented one level inside the class.",
            "The constructor stores the limit and starts the spent count; the other two methods read and update them through self.",
            "Every attribute is written with self. in front, and each method's body is indented one more level than its def.",
        ],
    },
    {
        "id": "files-pz1", "topic": "files", "kind": "parsons", "title": "Put it in order: count lines in a log",
        "difficulty": 2, "concepts": ["with open", "iterating a file"],
        "setup_files": {"log.txt": "INFO start\nERROR timeout\nINFO retry\nERROR rate limit\n"},
        "prompt": r'''
            Build `count_errors(path)`: how many lines of the text file at `path` start with `"ERROR"`.

            ''' + LEAD + r'''

            **Examples**
            ```python
            count_errors("log.txt")   # returns 2 for the sample log next to your code
            ```
        ''',
        "solution": r'''
            def count_errors(path):
                errors = 0
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("ERROR"):
                            errors += 1
                return errors
        ''',
        "distractors": ["f.close()", "for line in path:"],
        "starter": "",
        "tests": r'''
            from solution import count_errors

            def test_counts_error_lines():
                assert count_errors("log.txt") == 2

            def test_file_without_errors(tmp_name="clean.txt"):
                with open(tmp_name, "w", encoding="utf-8") as f:
                    f.write("INFO a\nINFO b\n")
                assert count_errors(tmp_name) == 0
        ''',
        "hints": [
            "The file is opened in a with block, and the loop reads it line by line inside that block.",
            "Counter first, then the with block, then the loop, then the check.",
            "The with block closes the file itself. The loop goes over the open file, not the path string.",
        ],
    },
    {
        "id": "generators-pz1", "topic": "generators", "kind": "parsons", "title": "Put it in order: stream in batches",
        "difficulty": 2, "concepts": ["yield", "batching"],
        "prompt": r'''
            Build the generator `batches(items, size)`: yield lists of up to `size` items, in order, so an app can
            send work to an API a batch at a time.

            ''' + LEAD + r'''

            **Examples**
            ```python
            list(batches([1, 2, 3, 4, 5], 2))   # returns [[1, 2], [3, 4], [5]]
            list(batches([], 3))                # returns []
            ```
        ''',
        "solution": r'''
            def batches(items, size):
                batch = []
                for item in items:
                    batch.append(item)
                    if len(batch) == size:
                        yield batch
                        batch = []
                if batch:
                    yield batch
        ''',
        "distractors": ["return batch", "batch.clear()"],
        "starter": "",
        "tests": r'''
            from solution import batches

            def test_batches_with_remainder():
                assert list(batches([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]

            def test_even():
                assert list(batches([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]

            def test_empty():
                assert list(batches([], 3)) == []

            def test_is_a_generator():
                import types
                assert isinstance(batches([1], 1), types.GeneratorType)
        ''',
        "hints": [
            "Collect items into a list and hand it out each time it is full.",
            "After yielding a full batch, start a new list. After the loop, hand out whatever is left over.",
            "Clearing the yielded list instead of making a new one would empty the batch you already gave out. "
            "The leftover check sits at function level, after the loop.",
        ],
    },
    {
        "id": "agents-pz1", "topic": "agents", "kind": "parsons", "title": "Put it in order: a tiny agent loop",
        "difficulty": 3, "concepts": ["agent loop", "max steps"],
        "prompt": r'''
            Build `run(llm, tools, task, max_steps)`. `llm(history)` returns either `("final", answer)` or
            `("tool", name, arg)`. Start the history with the task, then on each step call `llm`: return the answer
            when it's final, otherwise call `tools[name](arg)` and add `(name, result)` to the history. After
            `max_steps` calls without an answer, raise `RuntimeError`.

            ''' + LEAD + r'''

            **Examples**
            ```python
            replies = iter([("tool", "upper", "hi"), ("final", "done")])
            run(lambda h: next(replies), {"upper": str.upper}, "shout", 3)   # returns "done"
            ```
        ''',
        "solution": r'''
            def run(llm, tools, task, max_steps):
                history = [task]
                for _ in range(max_steps):
                    reply = llm(history)
                    if reply[0] == "final":
                        return reply[1]
                    name, arg = reply[1], reply[2]
                    history.append((name, tools[name](arg)))
                raise RuntimeError("no answer within max_steps")
        ''',
        "distractors": ["while True:", "return history"],
        "starter": "",
        "tests": r'''
            from solution import run

            def test_tool_then_final():
                seen = []
                replies = iter([("tool", "upper", "hi"), ("final", "done")])
                def llm(history):
                    seen.append(list(history))
                    return next(replies)
                assert run(llm, {"upper": str.upper}, "shout", 3) == "done"
                assert seen[1] == ["shout", ("upper", "HI")]

            def test_gives_up_after_max_steps():
                try:
                    run(lambda h: ("tool", "upper", "x"), {"upper": str.upper}, "loop", 2)
                except RuntimeError:
                    return
                assert False, "expected RuntimeError"
        ''',
        "hints": [
            "The loop runs at most max_steps times, so it is a for loop over a range, not a while True.",
            "Inside the loop: ask the model, return if it's final, otherwise run the tool and record the result.",
            "The raise sits after the loop, at function level, so it only happens when every step was used up.",
        ],
    },
]
