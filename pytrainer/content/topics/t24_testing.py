TOPIC = {
    "id": "testing",
    "title": "Testing Your Code",
    "track": "production-python",
    "order": 3,
    "requires": ["classes"],
    "summary": """
        Writing tests that catch real bugs: assert, test functions, arrange-act-assert,
        edge cases, testing exceptions, fixtures as helper functions, and faking an LLM
        so AI code can be tested without a network.
    """,
    "concepts": ["assert", "test functions", "arrange-act-assert", "edge cases",
                 "boundary values", "testing exceptions", "fixtures", "fakes and stubs",
                 "dependency injection", "pytest"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["test", "assert", "assertionerror", "test function", "test runner",
                 "arrange act assert", "edge case", "boundary value", "fixture", "fake", "stub",
                 "spy", "dependency injection", "pytest"],
    "cards": [
        {
            "syntax": 'assert condition, "message"',
            "explain": "Does nothing when the condition is true. Raises AssertionError with the message when it is false.",
            "example": r'''
                total = 2 + 2
                assert total == 4, "total should be 4"
                try:
                    assert total == 5, "total should be 5"
                except AssertionError as err:
                    print("failed:", err)
                # failed: total should be 5
            ''',
        },
        {
            "syntax": "def test_name():",
            "explain": "A test function: the name starts with test_, it takes no arguments, and it asserts on a result.",
            "example": r'''
                def shout(text):
                    return text.upper() + "!"
                def test_shout_adds_exclamation():
                    assert shout("hi") == "HI!"
                test_shout_adds_exclamation()
                print("passed")
                # passed
            ''',
        },
        {
            "syntax": 'assert False, "expected ValueError"',
            "explain": "Put it after a call inside try. It runs only if the call did not raise, and then the test fails.",
            "example": r'''
                def test_bad_number_raises():
                    try:
                        int("abc")
                        assert False, "expected ValueError"
                    except ValueError:
                        print("raised as expected")
                test_bad_number_raises()
                # raised as expected
            ''',
        },
        {
            "syntax": "def make_cart():",
            "explain": "A fixture: a helper function that builds new test data on every call, so tests do not share objects.",
            "example": r'''
                def make_cart():
                    return {"items": []}
                first = make_cart()
                first["items"].append("tea")
                print(first, make_cart())
                # {'items': ['tea']} {'items': []}
            ''',
        },
        {
            "syntax": "def answer(question, llm):",
            "explain": "Dependency injection: the model is a parameter, so a test passes a fake that records each prompt.",
            "example": r'''
                def answer(question, llm):
                    return llm("Q: " + question).strip()
                prompts = []
                def fake_llm(prompt):
                    prompts.append(prompt)
                    return " 4 "
                print(answer("2 + 2?", fake_llm), prompts)
                # 4 ['Q: 2 + 2?']
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: testing

### Tests

A **test** is code that calls your code and checks the result. You run the tests after
every change. If a change breaks a behaviour, a test fails and its name tells you which
behaviour broke. Programs whose behaviour changes often need tests. One example is an AI
app: a program that sends text to a model (a program that writes text) and parses the
answer. Its prompt (the text sent to the model) and parsing code change often, so it
needs tests.

### `assert`

`assert condition, "message"` evaluates the condition. If the condition is true, nothing
happens and the program continues. If it is false, Python raises `AssertionError` with
the message.

```python
assert 2 + 2 == 4
assert len([]) == 0, "empty list has length 0"
print("all good")
# all good
```

### Test functions and test runners

A **test function** is a function whose name starts with `test_`, takes no arguments and
contains `assert` statements. A **test runner** is a program that finds the test
functions, calls each one and reports which ones raised. pytest is a test runner, and so
is this app.

```python
def count_tokens(text):
    return len(text.split())

def test_counts_two_tokens():
    assert count_tokens("hello world") == 2

def test_empty_text_has_zero_tokens():
    assert count_tokens("") == 0

test_counts_two_tokens()
test_empty_text_has_zero_tokens()
print("2 tests passed")
# 2 tests passed
```

Name each test after the behaviour it checks, for example
`test_empty_text_has_zero_tokens`. Step through the stages to see what a runner does
with those two tests.

```diagram
{"type":"flow","title":"What a test runner does","steps":[
{"label":"Collect","detail":"The runner reads the test file and keeps every function whose name starts with test_. Other functions are not called as tests.","code":"test_counts_two_tokens\ntest_empty_text_has_zero_tokens"},
{"label":"Call one test","detail":"The runner calls the next test function with no arguments, inside a try block.","code":"try:\n    test_counts_two_tokens()"},
{"label":"Run the asserts","detail":"Each assert evaluates its condition. A true condition does nothing. A false condition raises AssertionError, and the rest of the test function does not run.","code":"assert count_tokens(\"hello world\") == 2"},
{"label":"Record pass or fail","detail":"If the call returned normally, the runner records a pass. If the call raised, the runner catches the exception and records a fail with the message. Then it continues with the next test.","code":"test_counts_two_tokens: passed"},
{"label":"Report","detail":"After the last test, the runner prints how many tests passed and the name and message of each test that failed.","code":"2 passed, 0 failed"}
],"loop":{"from":3,"to":1,"label":"while there are more test functions"}}
```

### Arrange, act, assert

The **code under test** is the code that a test checks. A test has three parts.
**Arrange** builds the inputs. **Act** calls the code under test once. **Assert** checks
the result.

### Edge cases

An **edge case** is an input at the limit of what the code accepts: empty input, one
item, the boundary value itself (exactly `limit` items), zero, negative numbers,
whitespace. The **spec** (short for specification) is the written description of what the
code must do. Write one test for each edge case the spec mentions.

### Testing that code raises

When the spec says a call raises an exception, the test passes only if it does.

```python
def fails():
    raise ValueError("bad")

try:
    fails()
    assert False, "expected ValueError"
except ValueError:
    print("raised as expected")
# raised as expected
```

If `fails()` does not raise, `assert False` runs and raises `AssertionError`.
`except ValueError` does not catch `AssertionError`, so the test fails.

### Fixtures

A **fixture** is a helper function that builds test data, such as `make_conversation()`.
Each test calls it and gets a new object, so one test cannot change the data of another.

### Fakes and dependency injection

A **fake** is a replacement object for something slow, random or paid, such as an LLM
(a large language model: a program that writes text). `llm` here is any function that
takes a prompt (text) and returns a reply.
**Dependency injection** means the function receives the model as a parameter. A test
then passes a fake that returns a fixed reply and records the prompts it was given.

```python
def answer(question, llm):
    return llm("Q: " + question).strip()

prompts = []
def fake_llm(prompt):
    prompts.append(prompt)
    return " 4 "

print(answer("2 + 2?", fake_llm))
# 4
print(prompts)
# ['Q: 2 + 2?']
```

### Good tests

A good test checks one behaviour, gives the same result on every run, runs fast, and
fails when the code has a plausible bug. A test that cannot fail checks nothing.

### pytest

Real projects use **pytest**. It is not part of the standard library. You install it by
typing `pip install pytest` in a terminal. The `pytest` command
finds files named `test_*.py` and runs every `test_*` function in them. When a plain
`assert` fails, pytest prints the values on both sides. It also provides
`pytest.raises(ValueError)`, `@pytest.fixture` and `@pytest.mark.parametrize`. The
`@` lines are decorators: a line above a function that changes how it is used. The
standard library module `unittest.mock` builds fakes.

### Common mistakes

- A test with no `assert` passes every time, unless the code under test raises.
- `0.1 + 0.2 == 0.3` is `False`. Compare computed floats with `abs(a - b) < 1e-9`.
  `1e-9` is `0.000000001`.
- A test that calls the real LLM service over the network is slow, costs money and can
  fail without a bug. Inject a fake.
- A wrong expected value makes a correct function fail its test. Work the expected
  value out by hand from the spec.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "testing-s1",
        "title": "What does assert do?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The assert statement

            An `assert` statement checks that a condition is true. You write `assert`
            followed by the condition. If the condition is true, nothing happens and the
            program continues with the next line. If it is false, Python raises an
            `AssertionError`.

            ```python
            total = 2 + 2
            assert total == 4
            print("check 1 passed")
            # check 1 passed
            ```

            You can add a comma and a string after the condition. That string is the
            **assertion message**: it becomes the message of the `AssertionError`.

            A **test** is code that calls your function and asserts that the result is
            correct. A failed `assert` raises an ordinary exception, so you can catch it
            with `try` / `except AssertionError`. A program that runs tests does this to
            continue after one test fails.

            ```python
            total = 2 + 2
            try:
                assert total == 5, "total should be 5"
                print("check 2 passed")
            except AssertionError as err:
                print("check 2 failed:", err)
            # check 2 failed: total should be 5
            ```

            Step through both checks to see which lines run.

            ```diagram
            {"type": "trace", "title": "A passing assert and a failing assert", "code": ["total = 2 + 2", "assert total == 4", "print(\"check 1 passed\")", "try:", "    assert total == 5, \"total should be 5\"", "    print(\"check 2 passed\")", "except AssertionError as err:", "    print(\"check 2 failed:\", err)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"total": "4"}, "out": ""},
              {"line": 3, "vars": {"total": "4"}, "out": "", "note": "4 == 4 is True, so the assert did nothing."},
              {"line": 4, "vars": {"total": "4"}, "out": "check 1 passed\n"},
              {"line": 5, "vars": {"total": "4"}, "out": "check 1 passed\n"},
              {"line": 7, "vars": {"total": "4"}, "out": "check 1 passed\n", "note": "4 == 5 is False, so the assert raised AssertionError. Line 6 is skipped."},
              {"line": 8, "vars": {"total": "4", "err": "AssertionError('total should be 5')"}, "out": "check 1 passed\n"},
              {"line": null, "vars": {"total": "4"}, "out": "check 1 passed\ncheck 2 failed: total should be 5\n"}
            ]}
            ```

            `assert` is a statement, not a function. Write `assert x == 1, "msg"`. With
            parentheses, `assert(x == 1, "msg")` checks a tuple of two items. A tuple that
            has items counts as true, so that assert never fails.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            def word_count(text):
                return len(text.split())

            assert word_count("hi there") == 2
            print("check 1 passed")
            try:
                assert word_count("") == 1, "empty text should have 1 word?"
                print("check 2 passed")
            except AssertionError as err:
                print("check 2 failed:", err)
        ''',
        "solution": r'''
            check 1 passed
            check 2 failed: empty text should have 1 word?
        ''',
        "explanation": r'''
            `word_count("hi there")` is `2`, so the first `assert` is silent and
            `check 1 passed` prints. `"".split()` is an empty list, so `word_count("")` is
            `0`, not `1`: the second `assert` raises `AssertionError` with the message, the
            `print("check 2 passed")` line is skipped, and the `except` block prints it.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "An assert whose condition is true does nothing. A false one raises AssertionError.",
            "Work out word_count(\"hi there\") and word_count(\"\") first. What does \"\".split() give?",
            "Line 1 comes from the first print. For line 2: the second assert is false, so jump straight to the except block and print its text followed by the message.",
        ],
    },
    {
        "id": "testing-s2",
        "title": "Your first test function",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Test functions

            A **test function** is a function that calls other code and asserts that the
            result is correct. It follows three rules:

            - Its name starts with `test_`.
            - It takes no arguments.
            - It calls the code and uses `assert` on the result.

            A **test runner** is a program that finds every function whose name starts
            with `test_` and calls it. If the call raises, the runner reports that test as
            failed.

            ```python
            def shout(text):
                return text.upper() + "!"

            def test_shout_adds_exclamation():
                assert shout("hi") == "HI!"

            test_shout_adds_exclamation()   # a runner makes this call for you
            print("test passed")
            # test passed
            ```

            The **code under test** is the code that your tests check. In the
            **test-writing** exercises, it is in a file named `target.py`. You import it
            with `from target import ...`. The **spec** (short for specification) is the
            written description of what that code must do: the exercise text. The app grades your
            tests in two ways. They must **pass** on the correct code. They must **fail**
            when the app replaces the correct code with a version that contains a bug. A
            test that cannot fail does not detect bugs.

            Work out the expected value by hand from the spec before you write it in the
            `assert`. A guessed value that is wrong makes the test fail on correct code.
        ''',
        "prompt": r'''
            `target.py` contains a word counter used to estimate prompt sizes. Finish the test
            by replacing `___` with the right expected value.

            **Write:** a test (a function named `test_...`) for `count_words(text)` from `target.py`

            - `text`: a string, e.g. `"the cat sat"`
            - **Returns:** the number of words, where words are separated by whitespace (an int)

            **Rules** (what `count_words` does - your test must check this)
            - `count_words("the cat sat")` is `3`.
            - Extra spaces between words don't create extra words.

            **Examples**
            ```python
            count_words("the cat sat")    # returns 3
            count_words("one")            # returns 1
            ```
        ''',
        "impl": r'''
            def count_words(text):
                return len(text.split())
        ''',
        "mutants": [
            {"name": "counts characters instead of words", "code": r'''
                def count_words(text):
                    return len(text)
            '''},
            {"name": "counts the spaces", "code": r'''
                def count_words(text):
                    return text.count(" ")
            '''},
            {"name": "always returns 0", "code": r'''
                def count_words(text):
                    return 0
            '''},
        ],
        "starter": r'''
            from target import count_words

            def test_counts_three_words():
                assert count_words("the cat sat") == ___
        ''',
        "solution": r'''
            from target import count_words

            def test_counts_three_words():
                assert count_words("the cat sat") == 3
        ''',
        "tests": "",
        "hints": [
            "The blank is the value count_words should return for that input, according to the spec.",
            "Count the words in \"the cat sat\" yourself. That number is what the function must give back.",
            "Replace ___ with the plain number of words (an int, no quotes).",
        ],
    },
    {
        "id": "testing-s3",
        "title": "One test per behaviour",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## One behaviour per test

            Write many small tests, and make each one check one behaviour. When a small
            test fails, its name tells you which behaviour is broken. When one large test
            fails, you have to read the whole test to find out.

            ```python
            def label(role):
                return role.upper() + ":"

            def test_user_label():
                assert label("user") == "USER:"

            def test_assistant_label():
                assert label("assistant") == "ASSISTANT:"

            test_user_label()
            test_assistant_label()
            print("2 tests passed")
            # 2 tests passed
            ```

            Give each test a **descriptive test name**: a name that states the behaviour
            it checks, such as `test_role_is_uppercased` or `test_content_is_kept_as_is`.
            The runner prints the name of a failed test, so the name is the first thing
            you read.

            Compare the **whole** result with `==` when you can. A check such as
            `"USER" in result` still passes when the space is missing or the parts are in
            the wrong order.

            Give every test function a different name. A second `def` with the same name
            makes the name refer to the new function, so the runner finds only the second
            one and the first test never runs.
        ''',
        "prompt": r'''
            A chat log printer formats each message on one line.

            **Write:** at least two test functions for `format_message(role, content)` from `target.py`

            - `role`: a string like `"user"` or `"assistant"`
            - `content`: the message text, e.g. `"hi"`
            - **Returns:** a string: the role in UPPERCASE, a colon, one space, then the content unchanged

            **Rules** (what `format_message` does - your tests must check this)
            - The role is uppercased; the content is NOT changed.
            - Exactly one space after the colon.

            **Examples**
            ```python
            format_message("user", "hi")              # returns "USER: hi"
            format_message("assistant", "Hello!")     # returns "ASSISTANT: Hello!"
            ```
        ''',
        "impl": r'''
            def format_message(role, content):
                return f"{role.upper()}: {content}"
        ''',
        "mutants": [
            {"name": "role not uppercased", "code": r'''
                def format_message(role, content):
                    return f"{role}: {content}"
            '''},
            {"name": "role and content swapped", "code": r'''
                def format_message(role, content):
                    return f"{content.upper()}: {role}"
            '''},
            {"name": "no space after the colon", "code": r'''
                def format_message(role, content):
                    return f"{role.upper()}:{content}"
            '''},
            {"name": "content uppercased too", "code": r'''
                def format_message(role, content):
                    return f"{role.upper()}: {content.upper()}"
            '''},
        ],
        "starter": r'''
            from target import format_message

            def test_user_message():
                ...

            def test_assistant_message():
                ...
        ''',
        "solution": r'''
            from target import format_message

            def test_user_message():
                assert format_message("user", "hi") == "USER: hi"

            def test_assistant_message_keeps_content_case():
                assert format_message("assistant", "Hello!") == "ASSISTANT: Hello!"
        ''',
        "tests": "",
        "hints": [
            "Replace each ... with an assert that calls format_message and compares the result to the exact expected string.",
            "Use the examples from the spec as your expected values. One of them has capital letters in the content - that catches a bug the other can't.",
            "In each test write: assert format_message(<role>, <content>) == <exact string>. Use \"user\"/\"hi\" in one and \"assistant\"/\"Hello!\" in the other.",
        ],
    },
    {
        "id": "testing-s4",
        "title": "Arrange, act, assert",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Arrange, act, assert

            Most tests have three parts, in this order. The pattern is named
            **arrange, act, assert**.

            1. **Arrange**: build the inputs.
            2. **Act**: call the code under test, once.
            3. **Assert**: check the result. Also check anything else that the call
               should or should not have changed.

            ```python
            def with_greeting(history):
                return history + ["hello"]

            # Arrange
            history = ["hi"]
            # Act
            result = with_greeting(history)
            # Assert
            assert result == ["hi", "hello"]
            assert history == ["hi"], "the original must not change"
            print("passed")
            # passed
            ```

            The second assert checks the input. `history + ["hello"]` builds a new list
            object, so `history` still holds one item. A function that used
            `history.append("hello")` instead would change the list the caller passed in.
            A change that a function makes to something outside itself is called a
            **side effect**. In a chat app, an unwanted side effect on a history list
            changes what every part of the program that uses that list reads.

            Check the exact contents of the result with `==`. A check of `len(result)`
            alone passes when the items are wrong or in the wrong order.
        ''',
        "prompt": r'''
            Chat history helpers must not change the history they are given.

            **Write:** tests for `add_message(history, role, content)` from `target.py`

            - `history`: a list of message dicts, e.g. `[{"role": "user", "content": "hi"}]`
            - `role`, `content`: strings
            - **Returns:** a NEW list: all the old messages, then `{"role": role, "content": content}` at the end

            **Rules** (what `add_message` does - your tests must check this)
            - The new message goes at the END.
            - The `history` list passed in is NOT modified.

            **Examples**
            ```python
            h = [{"role": "user", "content": "hi"}]
            add_message(h, "assistant", "hello!")
            # returns [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello!"}]
            # and h is still [{"role": "user", "content": "hi"}]
            ```
        ''',
        "impl": r'''
            def add_message(history, role, content):
                return history + [{"role": role, "content": content}]
        ''',
        "mutants": [
            {"name": "modifies the original list", "code": r'''
                def add_message(history, role, content):
                    history.append({"role": role, "content": content})
                    return history
            '''},
            {"name": "puts the new message first", "code": r'''
                def add_message(history, role, content):
                    return [{"role": role, "content": content}] + history
            '''},
            {"name": "drops the old messages", "code": r'''
                def add_message(history, role, content):
                    return [{"role": role, "content": content}]
            '''},
        ],
        "starter": r'''
            from target import add_message

            def test_add_message():
                # Arrange
                history = [{"role": "user", "content": "hi"}]
                # Act
                result = add_message(history, "assistant", "hello!")
                # Assert
                ...
        ''',
        "solution": r'''
            from target import add_message

            def test_add_message():
                # Arrange
                history = [{"role": "user", "content": "hi"}]
                # Act
                result = add_message(history, "assistant", "hello!")
                # Assert
                assert result == [{"role": "user", "content": "hi"},
                                  {"role": "assistant", "content": "hello!"}]
                assert history == [{"role": "user", "content": "hi"}]
        ''',
        "tests": "",
        "hints": [
            "Two things need checking: what comes back, and what happened to the list you passed in.",
            "Compare result with the full expected list (old message, then new one). Then check history still holds only the original message.",
            "Replace ... with two asserts: result == [old message dict, new message dict], and history == [old message dict].",
        ],
    },
    {
        "id": "testing-s5",
        "title": "Test the edge cases",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Edge cases

            An **edge case** (also called a **corner case**) is an input at the limit of
            what the code accepts. Code that works for a typical input often fails for an
            edge case, because the author did not think about it.

            Common edge cases:

            - Empty input: `""`, `[]`, `{}`.
            - Exactly one item.
            - The boundary value itself: a `limit` of 5 with exactly 5 items.
            - Zero and negative numbers.

            ```python
            def safe_max(numbers):
                if not numbers:
                    return None
                return max(numbers)

            print(safe_max([3, 9, 4]))   # typical input
            # 9
            print(safe_max([7]))         # one item
            # 7
            print(safe_max([]))          # empty: an edge case
            # None
            ```

            Without the `if not numbers` check, `max([])` raises `ValueError`. Only a test
            that passes an empty list finds that bug. When a spec has a sentence such as
            "for an empty list, return 0", write one test for that sentence.

            When the result is a float, choose inputs whose result you can write exactly.
            For example, the mean (the sum divided by the count) of `[2, 4]` is `3.0`.
        ''',
        "prompt": r'''
            Average tokens per message is a number shown on a usage dashboard.

            **Write:** tests for `average(numbers)` from `target.py`

            - `numbers`: a list of ints, e.g. `[2, 4, 6]`
            - **Returns:** the mean (sum divided by count) as a float

            **Rules** (what `average` does - your tests must check this)
            - An empty list returns `0.0` (it does not crash).
            - Every number counts, including the last one.

            **Examples**
            ```python
            average([2, 4, 6])    # returns 4.0
            average([5])          # returns 5.0
            average([])           # returns 0.0
            ```
        ''',
        "impl": r'''
            def average(numbers):
                if not numbers:
                    return 0.0
                return sum(numbers) / len(numbers)
        ''',
        "mutants": [
            {"name": "crashes on an empty list", "code": r'''
                def average(numbers):
                    return sum(numbers) / len(numbers)
            '''},
            {"name": "ignores the last number", "code": r'''
                def average(numbers):
                    if not numbers:
                        return 0.0
                    return sum(numbers[:-1]) / len(numbers)
            '''},
            {"name": "returns None for an empty list", "code": r'''
                def average(numbers):
                    if not numbers:
                        return None
                    return sum(numbers) / len(numbers)
            '''},
        ],
        "starter": r'''
            from target import average

            def test_normal_list():
                assert average([2, 4, 6]) == 4.0

            def test_empty_list():
                ...
        ''',
        "solution": r'''
            from target import average

            def test_normal_list():
                assert average([2, 4, 6]) == 4.0

            def test_empty_list():
                assert average([]) == 0.0

            def test_single_number():
                assert average([5]) == 5.0
        ''',
        "tests": "",
        "hints": [
            "One test is already done. The spec has a special rule for one kind of input - test it.",
            "Call average with an empty list and check the exact value the spec promises. A single-item list is another edge worth a test.",
            "Replace ... with: assert average([]) == 0.0. Optionally add test_single_number asserting average([5]) == 5.0.",
        ],
    },
    {
        "id": "testing-s6",
        "title": "Fix: the test is wrong",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Wrong expected values

            A test can contain a bug too. A test with a **wrong expected value** fails on
            code that is correct. A test that fails on correct code is called a
            **false positive**. People stop reading the results of tests that fail for no
            reason.

            When a test fails, there are two possible causes:

            1. The code is wrong.
            2. The expected value in the test is wrong.

            To decide, go back to the spec and work the expected value out by hand,
            character by character.

            ```python
            def initials(name):
                return "".join(part[0] for part in name.split()) + "."

            got = initials("Ada Lovelace")
            print(repr(got))
            # 'AL.'
            print(got == "AL")      # this expected value has no dot
            # False
            print(got == "AL.")
            # True
            ```

            `repr(got)` returns the string as you would type it in code, with its quotes.
            That makes leading spaces, trailing spaces and dots easy to see when you
            compare the actual value with the expected value.

            Do not fix a failing test by making it check less, for example by checking
            only the length. Correct the expected value, so the test still fails when the
            code has a bug.
        ''',
        "prompt": r'''
            A teammate wrote tests for `truncate`, but one fails on code that is correct. Fix
            the wrong test so all tests pass on the real code - and still catch real bugs.

            **Write:** tests for `truncate(text, limit)` from `target.py`

            - `text`: a string, e.g. `"hello world"`
            - `limit`: an int, the maximum number of characters to keep, e.g. `5`
            - **Returns:** `text` unchanged if it is at most `limit` characters long;
              otherwise the first `limit` characters followed by `"..."`

            **Rules** (what `truncate` does - your tests must check this)
            - Short text (length <= limit) comes back unchanged, with no dots.
            - Long text keeps exactly `limit` characters, then `"..."`.

            **Examples**
            ```python
            truncate("hello world", 5)    # returns "hello..."
            truncate("hi", 5)             # returns "hi"
            ```
        ''',
        "impl": r'''
            def truncate(text, limit):
                if len(text) <= limit:
                    return text
                return text[:limit] + "..."
        ''',
        "mutants": [
            {"name": "never adds the dots", "code": r'''
                def truncate(text, limit):
                    return text[:limit]
            '''},
            {"name": "keeps one character too few", "code": r'''
                def truncate(text, limit):
                    if len(text) <= limit:
                        return text
                    return text[:limit - 1] + "..."
            '''},
            {"name": "adds dots even to short text", "code": r'''
                def truncate(text, limit):
                    return text[:limit] + "..."
            '''},
        ],
        "starter": r'''
            from target import truncate

            def test_long_text_is_cut():
                assert truncate("hello world", 5) == "hello"

            def test_short_text_unchanged():
                assert truncate("hi", 5) == "hi"
        ''',
        "solution": r'''
            from target import truncate

            def test_long_text_is_cut():
                assert truncate("hello world", 5) == "hello..."

            def test_short_text_unchanged():
                assert truncate("hi", 5) == "hi"
        ''',
        "tests": "",
        "hints": [
            "Run the tests: one fails even though truncate is correct. Which one?",
            "Re-read what truncate returns for long text. The expected string in the failing test is missing something.",
            "In test_long_text_is_cut, change the expected value to the first 5 characters followed by three dots.",
        ],
    },
    {
        "id": "testing-s7",
        "title": "Catching the expected error",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Expected exceptions

            Some functions are specified to reject bad input by raising an exception. For
            those inputs, **raising is the correct behaviour**. A test for that rule
            passes when the call raises and fails when it returns normally.

            The test uses `try` / `except`, which you know from the Errors chapter.

            ```python
            def check_age(age):
                if age < 18:
                    raise ValueError("too young")
                return "welcome"

            try:
                check_age(15)
                print("no error: the test should fail")
            except ValueError as err:
                print("rejected as expected:", err)
            # rejected as expected: too young
            ```

            `check_age(15)` raises `ValueError`. Python skips the rest of the `try` block
            and runs the `except ValueError` block. With `check_age(30)` nothing is
            raised, so the next line of the `try` block runs and the `except` block is
            skipped. A real test puts `assert False, "expected ValueError"` on that next
            line.

            `except ValueError` catches only `ValueError` and its subclasses. If the call
            raised a `TypeError`, the `except ValueError` block would not run and the
            `TypeError` would stop the program.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            def check_temperature(t):
                if not 0 <= t <= 2:
                    raise ValueError("temperature must be 0-2")
                return t

            for value in [0.7, 5, 2]:
                try:
                    check_temperature(value)
                    print(value, "accepted")
                except ValueError as err:
                    print(value, "rejected:", err)
        ''',
        "solution": r'''
            0.7 accepted
            5 rejected: temperature must be 0-2
            2 accepted
        ''',
        "explanation": r'''
            `0.7` and `2` are inside `0 <= t <= 2` (the boundary `2` counts), so no error is
            raised and the `print` after the call runs. `5` is outside, so `ValueError` is
            raised, the `accepted` line is skipped, and the `except` block prints the message.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "For each value, decide whether check_temperature raises or returns normally.",
            "0 <= t <= 2 includes both ends. When it raises, the rest of the try block is skipped and except runs.",
            "Go through 0.7, 5, 2 in order: print 'VALUE accepted' if no error, else 'VALUE rejected: MESSAGE'.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "testing-1",
        "title": "Test that bad input raises",
        "difficulty": 1,
        "mode": "tests",
        "lesson": r'''
            ## Testing that a call raises

            To test that a call raises, put the call inside a `try` block and put
            `assert False` on the line after it, still inside the `try`.

            ```python
            def parse_age(text):
                age = int(text)
                if age < 0:
                    raise ValueError("negative age")
                return age

            def test_negative_age_raises():
                try:
                    parse_age("-3")
                    assert False, "expected ValueError"
                except ValueError:
                    pass    # good: it raised

            test_negative_age_raises()
            print("passed")
            # passed
            ```

            - If `parse_age` raises `ValueError`, Python skips `assert False` and runs the
              `except` block. The test function returns normally, so the test passes.
            - If `parse_age` does not raise, `assert False` runs and raises
              `AssertionError`. `except ValueError` does not catch it, so the test fails.

            Step through the body of that test to see which lines run when the call raises.

            ```diagram
            {"type": "trace", "title": "The call raises, so assert False is skipped", "code": ["def parse_age(text):", "    age = int(text)", "    if age < 0:", "        raise ValueError(\"negative age\")", "    return age", "", "try:", "    parse_age(\"-3\")", "    assert False, \"expected ValueError\"", "except ValueError:", "    print(\"raised as expected\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 7, "vars": {}, "out": ""},
              {"line": 8, "vars": {}, "out": ""},
              {"line": 2, "vars": {"text": "'-3'"}, "out": ""},
              {"line": 3, "vars": {"text": "'-3'", "age": "-3"}, "out": ""},
              {"line": 4, "vars": {"text": "'-3'", "age": "-3"}, "out": ""},
              {"line": 10, "vars": {}, "out": "", "note": "The ValueError leaves parse_age and the try block. Line 9 never runs."},
              {"line": 11, "vars": {}, "out": ""},
              {"line": null, "vars": {}, "out": "raised as expected\n"}
            ]}
            ```

            Test both sides of every rule. A value inside the allowed range must return a
            result, and a value outside it must raise. A **boundary value** is a value at
            the limit of the range, such as `0` for a rule that says "0 or more".

            Catch the specific exception type. `AssertionError` is a subclass of
            `Exception`, so `except Exception:` also catches the `AssertionError` from
            `assert False`. That test passes whether the call raises or not.
        ''',
        "prompt": r'''
            A settings form sends the model temperature as text. `parse_temperature` turns it
            into a number and rejects values outside the allowed range.

            **Write:** tests for `parse_temperature(value)` from `target.py`

            - `value`: a string like `"0.7"`
            - **Returns:** the temperature as a float

            **Rules** (what `parse_temperature` does - your tests must check this)
            - Valid range is `0.0` to `2.0`, **both ends included**.
            - Outside the range: raises `ValueError`.
            - Text that is not a number (e.g. `"hot"`): raises `ValueError`.
            - The return value is a float, not the original string.

            **Examples**
            ```python
            parse_temperature("0.7")    # returns 0.7
            parse_temperature("2")      # returns 2.0
            parse_temperature("3.5")    # raises ValueError
            parse_temperature("hot")    # raises ValueError
            ```
        ''',
        "impl": r'''
            def parse_temperature(value):
                t = float(value)
                if not 0.0 <= t <= 2.0:
                    raise ValueError(f"temperature out of range: {t}")
                return t
        ''',
        "mutants": [
            {"name": "accepts values above 2", "code": r'''
                def parse_temperature(value):
                    t = float(value)
                    if t < 0.0:
                        raise ValueError(f"temperature out of range: {t}")
                    return t
            '''},
            {"name": "rejects exactly 2.0", "code": r'''
                def parse_temperature(value):
                    t = float(value)
                    if not 0.0 <= t < 2.0:
                        raise ValueError(f"temperature out of range: {t}")
                    return t
            '''},
            {"name": "returns the text instead of a number", "code": r'''
                def parse_temperature(value):
                    t = float(value)
                    if not 0.0 <= t <= 2.0:
                        raise ValueError(f"temperature out of range: {t}")
                    return value
            '''},
            {"name": "returns None for non-numbers", "code": r'''
                def parse_temperature(value):
                    try:
                        t = float(value)
                    except ValueError:
                        return None
                    if not 0.0 <= t <= 2.0:
                        raise ValueError(f"temperature out of range: {t}")
                    return t
            '''},
        ],
        "starter": r'''
            from target import parse_temperature

            def test_valid_value():
                ...

            def test_too_high_raises():
                ...
        ''',
        "solution": r'''
            from target import parse_temperature

            def test_valid_value():
                assert parse_temperature("0.7") == 0.7

            def test_upper_boundary_allowed():
                assert parse_temperature("2") == 2.0

            def test_too_high_raises():
                try:
                    parse_temperature("3.5")
                    assert False, "expected ValueError"
                except ValueError:
                    pass

            def test_not_a_number_raises():
                try:
                    parse_temperature("hot")
                    assert False, "expected ValueError"
                except ValueError:
                    pass
        ''',
        "tests": "",
        "hints": [
            "You need tests for normal values, the boundary, and both kinds of bad input.",
            "For the error tests use try: call; assert False, 'expected ValueError' / except ValueError: pass. For the value tests compare to a float - \"0.7\" (a string) is not equal to 0.7.",
            "Write four tests: \"0.7\" returns 0.7; \"2\" returns 2.0; \"3.5\" raises ValueError; \"hot\" raises ValueError.",
        ],
    },
    {
        "id": "testing-2",
        "title": "A raises() helper",
        "difficulty": 1,
        "lesson": r'''
            ## A helper for error tests

            Every error test repeats the same `try` / `assert False` / `except` lines.
            Test tools put those lines in one helper function, and each test calls the
            helper.

            The helper has to make the call inside its own `try` block. So you pass it
            **the function itself**, without calling it, followed by the arguments.

            ```python
            def call_it(fn, *args):
                return fn(*args)       # the helper makes the call

            print(call_it(len, "hello"))
            # 5
            print(call_it(max, 3, 9, 4))
            # 9
            ```

            `len` without parentheses is a **function object**: the function itself as a
            value that you can pass to another function, not the result of calling it. In the
            parameter list, `*args` collects the extra arguments into a tuple. In the call `fn(*args)`, the `*` passes each
            item of the tuple as a separate argument.

            `except SomeError` also catches **subclasses** of that exception class.
            `KeyError` is a subclass of `LookupError`, so `except LookupError` catches it.

            ```python
            try:
                {}["missing"]
            except LookupError as err:
                print("caught", type(err).__name__)
            # caught KeyError
            ```

            `call_it(len("hello"))` is a mistake. Python evaluates `len("hello")` first,
            so the helper receives the integer `5` instead of a function. Calling `5()`
            raises `TypeError`.
        ''',
        "prompt": r'''
            Build the helper that error tests use, so they can be one line long.

            **Write:** `raises(exc_type, fn, *args)`

            - `exc_type`: an exception class, e.g. `ValueError`
            - `fn`: a function (not called yet), e.g. `int`
            - `*args`: the arguments to call `fn` with
            - **Returns:** `True` if `fn(*args)` raises `exc_type` (or a subclass of it),
              `False` if it returns normally

            **Rules**
            - Call `fn` exactly once, with the given arguments.
            - If `fn` raises a DIFFERENT exception type, let it propagate (don't catch it).

            **Examples**
            ```python
            raises(ValueError, int, "abc")      # True  (int("abc") raises ValueError)
            raises(ValueError, int, "42")       # False (no error)
            raises(LookupError, {}.__getitem__, "k")   # True (KeyError is a LookupError)
            raises(KeyError, int, "abc")        # ValueError propagates out of raises
            ```
        ''',
        "starter": r'''
            def raises(exc_type, fn, *args):
                ...
        ''',
        "tests": r'''
            from solution import raises

            def test_true_when_expected_error_raised():
                assert raises(ValueError, int, "abc") is True

            def test_false_when_no_error():
                assert raises(ValueError, int, "42") is False

            def test_subclass_counts():
                assert raises(LookupError, {}.__getitem__, "k") is True

            def test_other_errors_propagate():
                try:
                    raises(KeyError, int, "abc")
                except ValueError:
                    return
                assert False, "a different exception type should not be caught by raises()"

            def test_passes_all_arguments_and_calls_once():
                calls = []
                def boom(a, b):
                    calls.append((a, b))
                    raise ZeroDivisionError
                assert raises(ZeroDivisionError, boom, 1, 2) is True
                assert calls == [(1, 2)], f"fn was called like this: {calls!r}"
        ''',
        "solution": r'''
            def raises(exc_type, fn, *args):
                try:
                    fn(*args)
                except exc_type:
                    return True
                return False
        ''',
        "hints": [
            "Call fn(*args) inside a try block and catch only exc_type.",
            "except can take a variable holding an exception class: except exc_type:. If you land there, return True; if the call finished normally, return False.",
            "try: fn(*args) / except exc_type: return True / after the try, return False. Don't add a broad except - other errors must escape.",
        ],
    },
    {
        "id": "testing-3",
        "title": "Fixtures as functions",
        "difficulty": 1,
        "mode": "tests",
        "lesson": r'''
            ## Fixtures

            Each test should build its own data. If two tests use the same object, a
            change made by one test is visible in the other. Then the second test can
            fail because of the first test, not because of the code under test.

            A **fixture** is a helper function that builds the data a test needs. Each
            test calls the fixture and receives a new object.

            ```python
            def make_cart():            # the fixture
                return {"items": [], "total": 0}

            def test_add_item():
                cart = make_cart()
                cart["items"].append("tea")
                assert cart["items"] == ["tea"]

            def test_new_cart_is_empty():
                cart = make_cart()
                assert cart["items"] == []

            test_add_item()
            test_new_cart_is_empty()
            print("both passed")
            # both passed
            ```

            Each call to `make_cart()` builds a new dict with a new empty list. The item
            that `test_add_item` appends is not in the cart of `test_new_cart_is_empty`.
            The name `make_cart` does not start with `test_`, so the runner does not call
            it as a test.

            You can also test that **two objects do not share data**. Build two objects,
            change one, and assert that the other is unchanged. The Classes chapter
            covered class attributes: a list assigned in the class body is one list
            object that every instance uses. A test with two objects finds that bug.
        ''',
        "prompt": r'''
            `target.py` has a small `Conversation` class. Write tests for it, using a fixture
            function (e.g. `make_conversation()`) so each test starts fresh.

            **Write:** tests for the class `Conversation(system)` from `target.py`

            - `Conversation("Be brief")` starts with one message: `{"role": "system", "content": "Be brief"}`
              in its `.messages` list
            - `.add(role, content)`: appends `{"role": role, "content": content}`;
              `role` must be `"user"` or `"assistant"`, anything else raises `ValueError`
            - `.last()`: **returns** the content of the most recent message
            - `.count(role)`: **returns** how many messages have that role

            **Rules** (what `Conversation` does - your tests must check this)
            - Every conversation has its OWN messages list (two conversations never share messages).
            - `.add("system", ...)` or any other role raises `ValueError`.

            **Examples**
            ```python
            c = Conversation("Be brief")
            c.add("user", "hi")
            c.add("assistant", "hello")
            c.last()            # returns "hello"
            c.count("user")     # returns 1
            c.count("system")   # returns 1
            c.add("tool", "x")  # raises ValueError
            ```
        ''',
        "impl": r'''
            class Conversation:
                def __init__(self, system):
                    self.messages = [{"role": "system", "content": system}]

                def add(self, role, content):
                    if role not in ("user", "assistant"):
                        raise ValueError(f"bad role: {role}")
                    self.messages.append({"role": role, "content": content})

                def last(self):
                    return self.messages[-1]["content"]

                def count(self, role):
                    return sum(1 for m in self.messages if m["role"] == role)
        ''',
        "mutants": [
            {"name": "all conversations share one list", "code": r'''
                class Conversation:
                    messages = []

                    def __init__(self, system):
                        self.messages.append({"role": "system", "content": system})

                    def add(self, role, content):
                        if role not in ("user", "assistant"):
                            raise ValueError(f"bad role: {role}")
                        self.messages.append({"role": role, "content": content})

                    def last(self):
                        return self.messages[-1]["content"]

                    def count(self, role):
                        return sum(1 for m in self.messages if m["role"] == role)
            '''},
            {"name": "count ignores the role", "code": r'''
                class Conversation:
                    def __init__(self, system):
                        self.messages = [{"role": "system", "content": system}]

                    def add(self, role, content):
                        if role not in ("user", "assistant"):
                            raise ValueError(f"bad role: {role}")
                        self.messages.append({"role": role, "content": content})

                    def last(self):
                        return self.messages[-1]["content"]

                    def count(self, role):
                        return len(self.messages)
            '''},
            {"name": "last returns the first message", "code": r'''
                class Conversation:
                    def __init__(self, system):
                        self.messages = [{"role": "system", "content": system}]

                    def add(self, role, content):
                        if role not in ("user", "assistant"):
                            raise ValueError(f"bad role: {role}")
                        self.messages.append({"role": role, "content": content})

                    def last(self):
                        return self.messages[0]["content"]

                    def count(self, role):
                        return sum(1 for m in self.messages if m["role"] == role)
            '''},
            {"name": "add accepts any role", "code": r'''
                class Conversation:
                    def __init__(self, system):
                        self.messages = [{"role": "system", "content": system}]

                    def add(self, role, content):
                        self.messages.append({"role": role, "content": content})

                    def last(self):
                        return self.messages[-1]["content"]

                    def count(self, role):
                        return sum(1 for m in self.messages if m["role"] == role)
            '''},
        ],
        "starter": r'''
            from target import Conversation

            def make_conversation():
                ...

            def test_last_returns_newest_content():
                ...
        ''',
        "solution": r'''
            from target import Conversation

            def make_conversation():
                c = Conversation("Be brief")
                c.add("user", "hi")
                c.add("assistant", "hello")
                return c

            def test_last_returns_newest_content():
                assert make_conversation().last() == "hello"

            def test_count_by_role():
                c = make_conversation()
                assert c.count("user") == 1
                assert c.count("system") == 1

            def test_bad_role_raises():
                c = make_conversation()
                try:
                    c.add("tool", "x")
                    assert False, "expected ValueError"
                except ValueError:
                    pass

            def test_conversations_do_not_share_messages():
                a = make_conversation()
                b = Conversation("Other")
                assert len(b.messages) == 1
                assert len(a.messages) == 3
        ''',
        "tests": "",
        "hints": [
            "Start with the fixture: make_conversation() should build a Conversation, add a couple of messages and return it.",
            "Write one test per method (last, count, add with a bad role), and one test that builds two conversations and checks each has only its own messages.",
            "Fixture: create Conversation(\"Be brief\"), add a user and an assistant message, return it. Tests: last() is the assistant text; count(\"user\") == 1; add(\"tool\", ...) raises ValueError; a brand-new Conversation has exactly 1 message even after the fixture made another.",
        ],
    },
    {
        "id": "testing-4",
        "title": "Build a fake LLM",
        "difficulty": 1,
        "lesson": r'''
            ## Fakes

            An **LLM** (large language model) is a program that writes text. A real LLM call
            is slow, costs money, needs the network and returns a
            different answer each time. A test needs code that is fast and returns the
            same answer on every run. A **fake** is an object you write for tests that has
            the same methods as the real one and returns replies you chose in advance.

            A useful fake does two things:

            1. It **returns scripted replies**, in order.
            2. It **records what it was asked**, so a test can check the prompt.

            ```python
            class FakeWeather:
                def __init__(self, answers):
                    self.answers = list(answers)
                    self.cities = []

                def today(self, city):
                    self.cities.append(city)
                    return self.answers.pop(0)

            fake = FakeWeather(["sunny", "rain"])
            print(fake.today("Paris"), fake.today("Oslo"))
            # sunny rain
            print(fake.cities)
            # ['Paris', 'Oslo']
            ```

            `self.answers.pop(0)` removes the first remaining answer and returns it, so
            the answers come out in the order given. `list(answers)` builds a new list
            with the same items. `pop` changes that new list, and the list the caller
            passed in stays unchanged.

            Three terms are in common use. A **stub** returns fixed answers. A **spy**
            also records the calls it receives. **Fake** is the general word for both.
        ''',
        "prompt": r'''
            Every AI feature you test later will need a stand-in model. Build one.

            **Write:** a class `FakeLLM`

            - `FakeLLM(replies)`: `replies` is a list of strings to return, in order
            - `.complete(prompt)`: records `prompt`, then **returns** the next reply
            - `.prompts`: a list of every prompt received so far, in order (starts empty)

            **Rules**
            - Replies come out in the order given; each is used once.
            - When no replies are left, `.complete` raises `RuntimeError` (the prompt is still recorded).
            - Don't modify the `replies` list you were given.
            - Each `FakeLLM` has its own `.prompts` list.

            **Examples**
            ```python
            llm = FakeLLM(["Paris", "4"])
            llm.complete("Capital of France?")   # returns "Paris"
            llm.complete("2 + 2?")               # returns "4"
            llm.prompts                          # ["Capital of France?", "2 + 2?"]
            llm.complete("more?")                # raises RuntimeError
            ```
        ''',
        "starter": r'''
            class FakeLLM:
                def __init__(self, replies):
                    ...

                def complete(self, prompt):
                    ...
        ''',
        "tests": r'''
            from solution import FakeLLM

            def test_replies_in_order():
                llm = FakeLLM(["Paris", "4"])
                assert llm.complete("Capital of France?") == "Paris"
                assert llm.complete("2 + 2?") == "4"

            def test_records_prompts():
                llm = FakeLLM(["a", "b"])
                assert llm.prompts == [], f"a new fake should have no prompts, got {llm.prompts!r}"
                llm.complete("first")
                llm.complete("second")
                assert llm.prompts == ["first", "second"], f"got {llm.prompts!r}"

            def test_raises_runtime_error_when_out_of_replies():
                llm = FakeLLM(["only"])
                llm.complete("one")
                try:
                    llm.complete("two")
                    assert False, "expected RuntimeError"
                except RuntimeError:
                    pass
                assert llm.prompts == ["one", "two"], f"got {llm.prompts!r}"

            def test_does_not_modify_given_list():
                replies = ["x", "y"]
                llm = FakeLLM(replies)
                llm.complete("p")
                assert replies == ["x", "y"], f"your list became {replies!r}"

            def test_each_fake_has_its_own_prompts():
                a = FakeLLM(["1"])
                b = FakeLLM(["2"])
                a.complete("to a")
                assert b.prompts == [], f"b.prompts is {b.prompts!r}"
        ''',
        "solution": r'''
            class FakeLLM:
                def __init__(self, replies):
                    self.replies = list(replies)
                    self.prompts = []

                def complete(self, prompt):
                    self.prompts.append(prompt)
                    if not self.replies:
                        raise RuntimeError("FakeLLM: no replies left")
                    return self.replies.pop(0)
        ''',
        "hints": [
            "In __init__, store a copy of the replies and create an empty prompts list on self.",
            "complete() records the prompt first, then checks whether any replies are left, then hands out the first remaining one.",
            "__init__: self.replies = list(replies); self.prompts = []. complete: append prompt to self.prompts; if self.replies is empty raise RuntimeError(...); else return self.replies.pop(0).",
        ],
    },
    {
        "id": "testing-5",
        "title": "Inject a fake model",
        "difficulty": 1,
        "mode": "tests",
        "lesson": r'''
            ## Dependency injection

            A function that creates its own connection to the real model always calls the
            real model, in tests too. **Dependency injection** means the function receives
            the model as a parameter instead. The caller decides which model the function
            uses, so a test can pass a fake.

            ```python
            def translate(text, llm):
                return llm("Translate to French: " + text)

            seen = []
            def fake_llm(prompt):          # a fake, written in the test file
                seen.append(prompt)
                return "bonjour"

            print(translate("hello", fake_llm))
            # bonjour
            print(seen)
            # ['Translate to French: hello']
            ```

            The real app calls `translate(text, real_llm)`. A test calls
            `translate(text, fake_llm)`. With the fake, the test can check three things:

            - What the function **returned**, which is built from your scripted reply.
            - What **prompt** it sent, which is in `seen`.
            - **How many times** it called the model, which is `len(seen)`.

            Choose the scripted reply so that a bug changes the result. If the spec says
            the function removes surrounding whitespace from the reply, give the fake a
            reply that has surrounding whitespace. With a reply that is already clean, the
            test passes even if the function never removes anything.
        ''',
        "prompt": r'''
            `summarize` asks a model for a one-sentence summary. The model is injected, so you
            can test it with a fake function you write in your test file.

            **Write:** tests for `summarize(text, llm)` from `target.py`

            - `text`: the document to summarize, a string
            - `llm`: a function that takes a prompt string and returns a reply string
            - **Returns:** the model's reply with surrounding whitespace removed

            **Rules** (what `summarize` does - your tests must check this)
            - If `text` is empty or only whitespace, returns `""` **without calling** `llm`.
            - Otherwise calls `llm` **exactly once**, with a prompt that **contains `text`**.
            - The reply is returned with leading/trailing whitespace stripped.

            **Examples**
            ```python
            summarize("Cats sleep a lot.", fake)   # fake returns "  Cats nap.\n"  -> "Cats nap."
            summarize("   ", fake)                 # returns "" and fake is never called
            ```
        ''',
        "impl": r'''
            def summarize(text, llm):
                if not text.strip():
                    return ""
                prompt = f"Summarize in one sentence:\n\n{text}"
                reply = llm(prompt)
                return reply.strip()
        ''',
        "mutants": [
            {"name": "calls the model even for empty text", "code": r'''
                def summarize(text, llm):
                    prompt = f"Summarize in one sentence:\n\n{text}"
                    reply = llm(prompt)
                    if not text.strip():
                        return ""
                    return reply.strip()
            '''},
            {"name": "forgets to put the text in the prompt", "code": r'''
                def summarize(text, llm):
                    if not text.strip():
                        return ""
                    reply = llm("Summarize in one sentence:")
                    return reply.strip()
            '''},
            {"name": "does not strip the reply", "code": r'''
                def summarize(text, llm):
                    if not text.strip():
                        return ""
                    prompt = f"Summarize in one sentence:\n\n{text}"
                    return llm(prompt)
            '''},
            {"name": "calls the model twice", "code": r'''
                def summarize(text, llm):
                    if not text.strip():
                        return ""
                    prompt = f"Summarize in one sentence:\n\n{text}"
                    llm(prompt)
                    reply = llm(prompt)
                    return reply.strip()
            '''},
        ],
        "starter": r'''
            from target import summarize

            def make_fake(reply):
                calls = []
                def fake(prompt):
                    ...
                return fake, calls

            def test_returns_stripped_reply():
                ...
        ''',
        "solution": r'''
            from target import summarize

            def make_fake(reply):
                calls = []
                def fake(prompt):
                    calls.append(prompt)
                    return reply
                return fake, calls

            def test_returns_stripped_reply():
                fake, calls = make_fake("  Cats nap.\n")
                assert summarize("Cats sleep a lot.", fake) == "Cats nap."

            def test_calls_model_once_with_text_in_prompt():
                fake, calls = make_fake("ok")
                summarize("Cats sleep a lot.", fake)
                assert len(calls) == 1
                assert "Cats sleep a lot." in calls[0]

            def test_blank_text_skips_model():
                fake, calls = make_fake("should not be used")
                assert summarize("   ", fake) == ""
                assert calls == []
        ''',
        "tests": "",
        "hints": [
            "Finish the fake first: it should remember each prompt in calls and return the reply it was built with.",
            "Then write tests for each rule: stripped reply; exactly one call whose prompt contains the text; blank text returns \"\" with no calls.",
            "fake: calls.append(prompt); return reply. Tests: make_fake(\"  Cats nap.\\n\") and assert the result is \"Cats nap.\"; check len(calls) == 1 and the text is in calls[0]; with \"   \" assert result == \"\" and calls == [].",
        ],
    },
    {
        "id": "testing-6",
        "title": "Tests pytest would run",
        "difficulty": 1,
        "mode": "tests",
        "research": {
            "note": "Read pytest's getting-started page and the section on plain `assert`. Notice how it discovers tests by name and what a failure report looks like - the tests you write here run unchanged under pytest.",
            "links": [
                {"title": "pytest - Get started", "url": "https://docs.pytest.org/en/stable/getting-started.html"},
                {"title": "pytest - How to write and report assertions", "url": "https://docs.pytest.org/en/stable/how-to/assert.html"},
            ],
        },
        "lesson": r'''
            ## pytest

            So far this app has been your test runner. It finds every `test_` function,
            calls it and reports what failed. Real projects use **pytest**, the most
            widely used test runner for Python.

            What pytest provides:

            - The `pytest` command finds files named `test_*.py` and runs every `test_*`
              function in them.
            - When a plain `assert` fails, the report shows both values, for example
              `assert "a-b" == "a--b"`.
            - `pytest.raises(ValueError)` replaces the `try` / `assert False` / `except`
              pattern.
            - `@pytest.fixture` shares setup code between tests, and
              `@pytest.mark.parametrize` runs one test function with many inputs.

            You do not need pytest installed for this step. The tests you have written in
            this chapter are **already valid pytest tests**: functions named `test_...`
            that use plain `assert`.

            ```python
            def slug(title):
                return "-".join(title.lower().split())

            def test_slug():
                assert slug("Hello World") == "hello-world"

            test_slug()
            print(slug("  Many   spaces  here "))
            # many-spaces-here
            ```

            Choose test inputs that make every rule of the spec matter: capital letters,
            several spaces in a row, and spaces at the start and the end. An input such as
            `"Hello World"` alone does not detect a bug in how repeated spaces are handled.
        ''',
        "prompt": r'''
            Document ids in a RAG index are made from titles. Test the slug maker.

            **Write:** tests for `make_slug(title)` from `target.py`

            - `title`: a string, e.g. `"  Intro to  RAG "`
            - **Returns:** a string: the title in lowercase, with words joined by single dashes

            **Rules** (what `make_slug` does - your tests must check this)
            - All letters are lowercased.
            - Any run of whitespace between words becomes ONE dash.
            - Leading and trailing whitespace is dropped (no dash at the start or end).

            **Examples**
            ```python
            make_slug("Hello World")        # returns "hello-world"
            make_slug("  Intro to  RAG ")   # returns "intro-to-rag"
            make_slug("single")             # returns "single"
            ```
        ''',
        "impl": r'''
            def make_slug(title):
                return "-".join(title.lower().split())
        ''',
        "mutants": [
            {"name": "does not lowercase", "code": r'''
                def make_slug(title):
                    return "-".join(title.split())
            '''},
            {"name": "one dash per space (doubles up)", "code": r'''
                def make_slug(title):
                    return title.strip().lower().replace(" ", "-")
            '''},
            {"name": "keeps dashes for leading/trailing spaces", "code": r'''
                def make_slug(title):
                    words = [w for w in title.lower().split(" ")]
                    out = "-".join(words)
                    while "--" in out:
                        out = out.replace("--", "-")
                    return out
            '''},
        ],
        "starter": r'''
            from target import make_slug

            def test_simple_title():
                ...
        ''',
        "solution": r'''
            from target import make_slug

            def test_simple_title():
                assert make_slug("Hello World") == "hello-world"

            def test_messy_spaces():
                assert make_slug("  Intro to  RAG ") == "intro-to-rag"
        ''',
        "tests": "",
        "hints": [
            "One simple example won't catch every bug. Use an input that has capitals, double spaces and spaces at both ends.",
            "Write one test with a clean title and one with a messy one; compare each result to the exact expected slug.",
            "assert make_slug(\"Hello World\") == \"hello-world\" and assert make_slug(\"  Intro to  RAG \") == \"intro-to-rag\" in two test functions.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "testing-7",
        "title": "Test a chunker",
        "difficulty": 2,
        "mode": "tests",
        "placement": True,
        "lesson": r'''
            ## A full test suite

            A **test suite** is the set of all tests for one piece of code. To write one,
            read the spec rule by rule and write one test for each rule:

            - A typical input, compared with the whole expected result using `==`.
            - Each edge case the spec mentions, such as empty input.
            - Each boundary: an input that fits exactly, and one that leaves a remainder.
            - Each error rule, with the `try` / `assert False` / `except` pattern.

            When one rule covers several bad values, test more than one of them. Code that
            rejects one bad value can still accept another.
        ''',
        "prompt": r'''
            RAG pipelines split documents into chunks before embedding them. Write a test suite
            that would catch any plausible bug in this chunker.

            **Write:** tests for `chunk_words(text, size)` from `target.py`

            - `text`: a string of words separated by whitespace
            - `size`: an int, the maximum number of words per chunk
            - **Returns:** a list of strings; each chunk is up to `size` words joined by single spaces

            **Rules** (what `chunk_words` does - your tests must check this)
            - Chunks are taken in order; only the LAST chunk may be shorter than `size`.
            - Chunks don't overlap and no word is lost.
            - Empty (or whitespace-only) text returns `[]`.
            - `size` less than 1 raises `ValueError`.

            **Examples**
            ```python
            chunk_words("a b c d e", 2)   # returns ["a b", "c d", "e"]
            chunk_words("a b c d", 2)     # returns ["a b", "c d"]
            chunk_words("", 3)            # returns []
            chunk_words("a b", 0)         # raises ValueError
            chunk_words("a b", -1)        # raises ValueError
            ```
        ''',
        "impl": r'''
            def chunk_words(text, size):
                if size < 1:
                    raise ValueError("size must be >= 1")
                words = text.split()
                return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
        ''',
        "mutants": [
            {"name": "drops the last short chunk", "code": r'''
                def chunk_words(text, size):
                    if size < 1:
                        raise ValueError("size must be >= 1")
                    words = text.split()
                    return [" ".join(words[i:i + size]) for i in range(0, len(words) - size + 1, size)]
            '''},
            {"name": "returns [''] for empty text", "code": r'''
                def chunk_words(text, size):
                    if size < 1:
                        raise ValueError("size must be >= 1")
                    words = text.split()
                    if not words:
                        return [""]
                    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
            '''},
            {"name": "no error for a negative size", "code": r'''
                def chunk_words(text, size):
                    words = text.split()
                    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
            '''},
            {"name": "chunks are one word too long", "code": r'''
                def chunk_words(text, size):
                    if size < 1:
                        raise ValueError("size must be >= 1")
                    words = text.split()
                    return [" ".join(words[i:i + size + 1]) for i in range(0, len(words), size)]
            '''},
        ],
        "starter": r'''
            from target import chunk_words
        ''',
        "solution": r'''
            from target import chunk_words

            def test_last_chunk_may_be_short():
                assert chunk_words("a b c d e", 2) == ["a b", "c d", "e"]

            def test_even_split():
                assert chunk_words("a b c d", 2) == ["a b", "c d"]

            def test_empty_text():
                assert chunk_words("", 3) == []

            def test_bad_sizes_raise():
                for bad in (0, -1):
                    try:
                        chunk_words("a b", bad)
                        assert False, f"expected ValueError for size {bad}"
                    except ValueError:
                        pass
        ''',
        "tests": "",
        "hints": [
            "Go rule by rule through the spec and write one test for each: uneven split, even split, empty text, bad sizes.",
            "Compare whole lists with ==. For the error rule, test more than one bad size - 0 and a negative number can fail differently.",
            "Tests: \"a b c d e\" with 2 -> [\"a b\", \"c d\", \"e\"]; \"a b c d\" with 2 -> [\"a b\", \"c d\"]; \"\" -> []; sizes 0 and -1 each raise ValueError (try / assert False / except ValueError).",
        ],
    },
    {
        "id": "testing-8",
        "title": "A tiny test runner",
        "difficulty": 2,
        "lesson": r'''
            ## How a test runner works

            A test runner runs a loop over the test functions. It calls each function
            inside a `try` block and catches whatever the function raises. pytest does the
            same thing and adds more features.

            ```python
            def test_crash():
                return 1 / 0

            try:
                test_crash()
            except Exception as err:
                print(type(err).__name__, "|", str(err))
            else:
                print("passed")
            # ZeroDivisionError | division by zero
            ```

            `type(err).__name__` is the name of the exception class as a string, and
            `str(err)` is its message. The `else` block of a `try` runs only when the
            `try` block raised nothing. An `assert` without a message raises an
            `AssertionError` whose `str(err)` is the empty string `""`.
        ''',
        "prompt": r'''
            Build the core of a test runner: run test functions and report results.

            **Write:** `run_tests(tests)`

            - `tests`: a dict mapping names to functions, e.g. `{"test_ok": fn1, "helper": fn2}`
            - **Returns:** a dict `{"passed": [...names...], "failed": {name: message}}`

            **Rules**
            - Only run entries whose name starts with `"test_"`, in the dict's order. Other entries are ignored (not called).
            - A function that returns normally goes into `"passed"`.
            - If it raises `AssertionError`, the message is `str(err)`, or `"assertion failed"` if that is empty.
            - If it raises any other exception, the message is `"<TypeName>: <str(err)>"`, e.g. `"ZeroDivisionError: division by zero"`.
            - One failing test must not stop the others from running.

            **Examples**
            ```python
            def test_ok(): assert 1 + 1 == 2
            def test_bad(): assert 1 == 2, "one is not two"
            def test_crash(): 1 / 0
            def test_silent(): assert False
            run_tests({"test_ok": test_ok, "test_bad": test_bad, "test_crash": test_crash,
                       "test_silent": test_silent, "setup": print})
            # returns {"passed": ["test_ok"],
            #          "failed": {"test_bad": "one is not two",
            #                     "test_crash": "ZeroDivisionError: division by zero",
            #                     "test_silent": "assertion failed"}}
            ```
        ''',
        "starter": r'''
            def run_tests(tests):
                ...
        ''',
        "tests": r'''
            from solution import run_tests

            def _ok():
                assert 1 + 1 == 2

            def _bad():
                assert 1 == 2, "one is not two"

            def _crash():
                1 / 0

            def _silent():
                assert False

            def test_passed_and_failed_are_reported():
                got = run_tests({"test_ok": _ok, "test_bad": _bad})
                assert got == {"passed": ["test_ok"], "failed": {"test_bad": "one is not two"}}, f"got {got!r}"

            def test_other_exceptions_include_type_name():
                got = run_tests({"test_crash": _crash})
                assert got["failed"] == {"test_crash": "ZeroDivisionError: division by zero"}, f"got {got!r}"

            def test_empty_assert_message():
                got = run_tests({"test_silent": _silent})
                assert got["failed"] == {"test_silent": "assertion failed"}, f"got {got!r}"

            def test_non_test_entries_are_not_called():
                called = []
                got = run_tests({"setup": lambda: called.append("setup"), "test_ok": _ok})
                assert called == [], "a function not named test_... was called"
                assert got == {"passed": ["test_ok"], "failed": {}}, f"got {got!r}"

            def test_keeps_order_and_runs_all():
                order = []
                def a():
                    order.append("a"); 1 / 0
                def b():
                    order.append("b")
                def c():
                    order.append("c")
                got = run_tests({"test_c": c, "test_a": a, "test_b": b})
                assert order == ["c", "a", "b"], f"ran in this order: {order!r}"
                assert got["passed"] == ["test_c", "test_b"], f"got {got!r}"
        ''',
        "solution": r'''
            def run_tests(tests):
                passed, failed = [], {}
                for name, fn in tests.items():
                    if not name.startswith("test_"):
                        continue
                    try:
                        fn()
                    except AssertionError as err:
                        failed[name] = str(err) or "assertion failed"
                    except Exception as err:
                        failed[name] = f"{type(err).__name__}: {err}"
                    else:
                        passed.append(name)
                return {"passed": passed, "failed": failed}
        ''',
        "hints": [
            "Loop over tests.items(), skip names that don't start with test_, and call each function inside try/except.",
            "Catch AssertionError first (its message may be empty), then any other Exception. Only add to passed if nothing was raised.",
            "For each test name: try fn(); except AssertionError as err -> failed[name] = str(err) or \"assertion failed\"; except Exception as err -> f\"{type(err).__name__}: {err}\"; else append name to passed. Return both.",
        ],
    },
    {
        "id": "testing-9",
        "title": "Test a retry wrapper",
        "difficulty": 2,
        "mode": "tests",
        "prompt": r'''
            LLM APIs drop connections sometimes. `call_with_retry` tries again - but only for
            connection problems. Test it with a flaky fake model you write yourself.

            **Write:** tests for `call_with_retry(llm, prompt, attempts=3)` from `target.py`

            - `llm`: a function taking a prompt string and returning a reply string
            - `prompt`: the prompt string to send
            - `attempts`: the maximum number of calls in total (an int >= 1)
            - **Returns:** the first successful reply

            **Rules** (what `call_with_retry` does - your tests must check this)
            - If `llm` raises `ConnectionError`, it calls `llm` again, up to `attempts` calls in total.
            - As soon as a call succeeds it returns that reply and makes no more calls.
            - If all `attempts` calls raise `ConnectionError`, the last `ConnectionError` is raised.
            - Any other exception (e.g. `ValueError`) is raised immediately, with no retry.

            **Examples**
            ```python
            # flaky fake: fails twice with ConnectionError, then returns "ok"
            call_with_retry(flaky, "hi", attempts=3)   # returns "ok" after 3 calls
            call_with_retry(flaky2, "hi", attempts=2)  # a fresh fake failing twice: raises ConnectionError after 2 calls
            ```
        ''',
        "impl": r'''
            def call_with_retry(llm, prompt, attempts=3):
                last_error = None
                for _ in range(attempts):
                    try:
                        return llm(prompt)
                    except ConnectionError as err:
                        last_error = err
                raise last_error
        ''',
        "mutants": [
            {"name": "makes one call too few", "code": r'''
                def call_with_retry(llm, prompt, attempts=3):
                    last_error = ConnectionError("gave up")
                    for _ in range(attempts - 1):
                        try:
                            return llm(prompt)
                        except ConnectionError as err:
                            last_error = err
                    raise last_error
            '''},
            {"name": "retries every kind of error", "code": r'''
                def call_with_retry(llm, prompt, attempts=3):
                    last_error = None
                    for _ in range(attempts):
                        try:
                            return llm(prompt)
                        except Exception as err:
                            last_error = err
                    raise last_error
            '''},
            {"name": "returns None instead of raising at the end", "code": r'''
                def call_with_retry(llm, prompt, attempts=3):
                    for _ in range(attempts):
                        try:
                            return llm(prompt)
                        except ConnectionError:
                            pass
                    return None
            '''},
            {"name": "keeps calling after a success", "code": r'''
                def call_with_retry(llm, prompt, attempts=3):
                    reply, last_error = None, None
                    for _ in range(attempts):
                        try:
                            reply = llm(prompt)
                        except ConnectionError as err:
                            last_error = err
                    if reply is None:
                        raise last_error
                    return reply
            '''},
        ],
        "starter": r'''
            from target import call_with_retry

            def make_flaky(failures, reply="ok", error=ConnectionError):
                """Fake model: raises `error` for the first `failures` calls, then returns reply."""
                calls = []
                def llm(prompt):
                    ...
                return llm, calls
        ''',
        "solution": r'''
            from target import call_with_retry

            def make_flaky(failures, reply="ok", error=ConnectionError):
                """Fake model: raises `error` for the first `failures` calls, then returns reply."""
                calls = []
                def llm(prompt):
                    calls.append(prompt)
                    if len(calls) <= failures:
                        raise error("boom")
                    return reply
                return llm, calls

            def test_succeeds_after_retries():
                llm, calls = make_flaky(2)
                assert call_with_retry(llm, "hi", attempts=3) == "ok"
                assert len(calls) == 3

            def test_stops_after_first_success():
                llm, calls = make_flaky(0)
                assert call_with_retry(llm, "hi", attempts=3) == "ok"
                assert len(calls) == 1

            def test_gives_up_with_connection_error():
                llm, calls = make_flaky(5)
                try:
                    call_with_retry(llm, "hi", attempts=2)
                    assert False, "expected ConnectionError"
                except ConnectionError:
                    pass
                assert len(calls) == 2

            def test_other_errors_not_retried():
                llm, calls = make_flaky(5, error=ValueError)
                try:
                    call_with_retry(llm, "hi", attempts=3)
                    assert False, "expected ValueError"
                except ValueError:
                    pass
                assert len(calls) == 1
        ''',
        "tests": "",
        "hints": [
            "Finish the flaky fake first: it must count its calls and raise for the first few.",
            "Then check each rule with a call count: succeed-after-failures, no extra calls after success, give up after `attempts`, no retry for other errors.",
            "In llm: append the prompt to calls; if len(calls) <= failures raise error(\"boom\"); else return reply. Then write 4 tests using make_flaky(2), make_flaky(0), make_flaky(5) with attempts=2, and make_flaky(5, error=ValueError), asserting the result/exception and len(calls).",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "testing-10",
        "title": "Test a tool-call parser",
        "difficulty": 3,
        "mode": "tests",
        "prompt": r'''
            Models that use tools reply with JSON describing the call. Parsing it wrongly
            means running the wrong tool. Write a thorough test suite.

            **Write:** tests for `parse_tool_call(reply)` from `target.py`

            - `reply`: a string of JSON, e.g. `'{"name": "search", "args": {"q": "cats"}}'`
            - **Returns:** a tuple `(name, args)`, e.g. `("search", {"q": "cats"})`

            **Rules** (what `parse_tool_call` does - your tests must check this)
            - If `"args"` is missing, `args` is `{}`.
            - Raises `ValueError` if: the text is not valid JSON; the JSON is not an object (e.g. a list);
              `"name"` is missing, not a string, or an empty string; `"args"` is present but not an object.

            **Examples**
            ```python
            parse_tool_call('{"name": "search", "args": {"q": "cats"}}')  # ("search", {"q": "cats"})
            parse_tool_call('{"name": "now"}')                           # ("now", {})
            parse_tool_call('not json')                                  # raises ValueError
            parse_tool_call('["search"]')                                # raises ValueError
            parse_tool_call('{"name": ""}')                              # raises ValueError
            parse_tool_call('{"name": "x", "args": [1]}')                # raises ValueError
            ```
        ''',
        "impl": r'''
            import json

            def parse_tool_call(reply):
                data = json.loads(reply)
                if not isinstance(data, dict):
                    raise ValueError("tool call must be a JSON object")
                name = data.get("name")
                if not isinstance(name, str) or not name:
                    raise ValueError("tool call needs a non-empty name")
                args = data.get("args", {})
                if not isinstance(args, dict):
                    raise ValueError("args must be an object")
                return name, args
        ''',
        "mutants": [
            {"name": "crashes when args is missing", "code": r'''
                import json

                def parse_tool_call(reply):
                    data = json.loads(reply)
                    if not isinstance(data, dict):
                        raise ValueError("tool call must be a JSON object")
                    name = data.get("name")
                    if not isinstance(name, str) or not name:
                        raise ValueError("tool call needs a non-empty name")
                    args = data["args"]
                    if not isinstance(args, dict):
                        raise ValueError("args must be an object")
                    return name, args
            '''},
            {"name": "accepts an empty name", "code": r'''
                import json

                def parse_tool_call(reply):
                    data = json.loads(reply)
                    if not isinstance(data, dict):
                        raise ValueError("tool call must be a JSON object")
                    name = data.get("name")
                    if not isinstance(name, str):
                        raise ValueError("tool call needs a name")
                    args = data.get("args", {})
                    if not isinstance(args, dict):
                        raise ValueError("args must be an object")
                    return name, args
            '''},
            {"name": "accepts args that are not an object", "code": r'''
                import json

                def parse_tool_call(reply):
                    data = json.loads(reply)
                    if not isinstance(data, dict):
                        raise ValueError("tool call must be a JSON object")
                    name = data.get("name")
                    if not isinstance(name, str) or not name:
                        raise ValueError("tool call needs a non-empty name")
                    return name, data.get("args", {})
            '''},
            {"name": "returns (args, name)", "code": r'''
                import json

                def parse_tool_call(reply):
                    data = json.loads(reply)
                    if not isinstance(data, dict):
                        raise ValueError("tool call must be a JSON object")
                    name = data.get("name")
                    if not isinstance(name, str) or not name:
                        raise ValueError("tool call needs a non-empty name")
                    args = data.get("args", {})
                    if not isinstance(args, dict):
                        raise ValueError("args must be an object")
                    return args, name
            '''},
            {"name": "crashes with the wrong error on a JSON list", "code": r'''
                import json

                def parse_tool_call(reply):
                    data = json.loads(reply)
                    name = data.get("name")
                    if not isinstance(name, str) or not name:
                        raise ValueError("tool call needs a non-empty name")
                    args = data.get("args", {})
                    if not isinstance(args, dict):
                        raise ValueError("args must be an object")
                    return name, args
            '''},
            {"name": "accepts a number as the name", "code": r'''
                import json

                def parse_tool_call(reply):
                    data = json.loads(reply)
                    if not isinstance(data, dict):
                        raise ValueError("tool call must be a JSON object")
                    name = data.get("name")
                    if not name:
                        raise ValueError("tool call needs a non-empty name")
                    args = data.get("args", {})
                    if not isinstance(args, dict):
                        raise ValueError("args must be an object")
                    return name, args
            '''},
        ],
        "starter": r'''
            from target import parse_tool_call
        ''',
        "solution": r'''
            from target import parse_tool_call

            def assert_value_error(text):
                try:
                    parse_tool_call(text)
                except ValueError:
                    return
                assert False, f"expected ValueError for {text!r}"

            def test_name_and_args():
                assert parse_tool_call('{"name": "search", "args": {"q": "cats"}}') == ("search", {"q": "cats"})

            def test_missing_args_defaults_to_empty_dict():
                assert parse_tool_call('{"name": "now"}') == ("now", {})

            def test_invalid_json():
                assert_value_error("not json")

            def test_json_list():
                assert_value_error('["search"]')

            def test_bad_names():
                assert_value_error('{"name": ""}')
                assert_value_error('{"name": 42}')
                assert_value_error('{"args": {}}')

            def test_args_must_be_object():
                assert_value_error('{"name": "x", "args": [1]}')
        ''',
        "tests": "",
        "hints": [
            "Write a small helper that asserts a given text raises ValueError - you'll use it a lot.",
            "Cover both happy paths (with and without args) with == on the whole tuple, then one error test per bad-input rule. 'Not a string' and 'empty' are two different name bugs.",
            "Helper: try parse_tool_call(text) / except ValueError: return / then assert False. Use it for: \"not json\", '[\"search\"]', '{\"name\": \"\"}', '{\"name\": 42}', '{\"args\": {}}', '{\"name\": \"x\", \"args\": [1]}'. Plus two == tests for the valid examples.",
        ],
    },
    {
        "id": "testing-11",
        "title": "A scripted fake model",
        "difficulty": 3,
        "prompt": r'''
            A stricter fake for agent tests: it knows which prompt to expect at each step and
            fails loudly if the code under test goes off-script.

            **Write:** a class `ScriptedLLM`

            - `ScriptedLLM(script)`: `script` is a list of `(expected, reply)` pairs (tuples of two strings)
            - `.complete(prompt)`: handles the next step of the script:
              if `expected` is **contained in** `prompt`, **returns** `reply`
            - `.assert_done()`: checks that every step was used
            - `.calls`: the number of `.complete` calls so far (an int, starts at `0`)

            **Rules**
            - `.complete` raises `AssertionError` with a message containing the expected text if the prompt doesn't contain it.
            - `.complete` raises `AssertionError` with a message containing `"unexpected call"` when the script is used up.
            - `.calls` goes up by one on every `.complete` call, even ones that raise.
            - `.assert_done()` returns `None` when all steps were used; otherwise raises `AssertionError` with a message containing the number of unused steps.
            - Don't modify the `script` list you were given.

            **Examples**
            ```python
            llm = ScriptedLLM([("weather", "call get_weather"), ("sunny", "It is sunny.")])
            llm.complete("What's the weather in Paris?")   # returns "call get_weather"
            llm.assert_done()     # raises AssertionError: "1 unused step(s)"
            llm.complete("Tool said: sunny")               # returns "It is sunny."
            llm.assert_done()     # returns None
            llm.complete("more?") # raises AssertionError: "unexpected call ..."
            llm.calls             # 3
            ```
        ''',
        "starter": r'''
            class ScriptedLLM:
                def __init__(self, script):
                    ...
        ''',
        "tests": r'''
            from solution import ScriptedLLM

            def _expect_assertion(fn, *args):
                try:
                    fn(*args)
                except AssertionError as err:
                    return str(err)
                assert False, "expected an AssertionError"

            def test_follows_the_script():
                llm = ScriptedLLM([("weather", "call get_weather"), ("sunny", "It is sunny.")])
                assert llm.complete("What's the weather in Paris?") == "call get_weather"
                assert llm.complete("Tool said: sunny") == "It is sunny."
                assert llm.calls == 2, f"calls is {llm.calls!r}"

            def test_wrong_prompt_fails_with_expected_text():
                llm = ScriptedLLM([("weather", "x")])
                msg = _expect_assertion(llm.complete, "Tell me a joke")
                assert "weather" in msg, f"message was {msg!r}"

            def test_extra_call_fails():
                llm = ScriptedLLM([("a", "1")])
                llm.complete("a")
                msg = _expect_assertion(llm.complete, "a again")
                assert "unexpected call" in msg, f"message was {msg!r}"
                assert llm.calls == 2, f"calls is {llm.calls!r}"

            def test_assert_done():
                llm = ScriptedLLM([("a", "1"), ("b", "2"), ("c", "3")])
                llm.complete("a")
                msg = _expect_assertion(llm.assert_done)
                assert "2" in msg, f"message was {msg!r}"
                llm.complete("b")
                llm.complete("c")
                assert llm.assert_done() is None

            def test_does_not_modify_script_and_starts_at_zero():
                script = [("a", "1")]
                llm = ScriptedLLM(script)
                assert llm.calls == 0
                llm.complete("a")
                assert script == [("a", "1")], f"script became {script!r}"
        ''',
        "solution": r'''
            class ScriptedLLM:
                def __init__(self, script):
                    self.steps = list(script)
                    self.calls = 0

                def complete(self, prompt):
                    self.calls += 1
                    if not self.steps:
                        raise AssertionError(f"unexpected call #{self.calls}: {prompt!r}")
                    expected, reply = self.steps.pop(0)
                    if expected not in prompt:
                        raise AssertionError(f"expected a prompt containing {expected!r}, got {prompt!r}")
                    return reply

                def assert_done(self):
                    if self.steps:
                        raise AssertionError(f"{len(self.steps)} unused step(s)")
        ''',
        "hints": [
            "Keep a copy of the script as a list of remaining steps, plus a call counter.",
            "complete(): count the call first, then check whether steps remain, then take the next step and compare. assert_done(): complain if steps remain.",
            "__init__: self.steps = list(script); self.calls = 0. complete: self.calls += 1; if no steps raise AssertionError(\"unexpected call ...\"); expected, reply = self.steps.pop(0); if expected not in prompt raise AssertionError mentioning expected; return reply. assert_done: if self.steps raise AssertionError(f\"{len(self.steps)} unused step(s)\").",
        ],
    },
]
