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
            ## Make a wrong result stop the program

            You change a helper and want to know whether it still gives the promised answer. Printing the result makes you inspect it yourself every time. You can instead write a condition that must remain true and let Python report when it is false.

            ```python
            total = 3 * 4
            assert total == 12
            print("first check passed")
            # first check passed
            try:
                assert total == 10, "unexpected total"
            except AssertionError as error:
                print("failed:", error)
            # failed: unexpected total
            ```

            An **assertion** expresses an expectation. When its condition is true, the `assert` statement continues silently. When false, it raises `AssertionError`. The optional text after the comma becomes the error's message.

            ```predict
            try:
                assert 4 > 7, "wrong order"
                print("after assertion")
            except AssertionError:
                print("caught failure")
            print("finished")
            ---
            The assertion is false, so control jumps to the handler and skips the next print inside try. After the handler, execution continues with finished.
            ```

            A **test** runs code and checks expectations about its behavior. A test runner can catch an assertion failure, report it, and continue with other tests. The failure is useful evidence, not something to hide by weakening the expectation.

            ```quiz
            A true assertion produces no output. Does that mean it was skipped?
            - [x] No :: Success is silent; the next line runs normally.
            - [ ] Yes :: An assertion does not print a success message automatically.
            ```

            **Watch out:** `assert(condition, message)` checks a nonempty tuple, which is truthy even when condition is false. Use the statement's comma form. Assertions are for tests and internal checks, not security checks that must survive Python's optimization mode.

            **In short:** assert stays silent when an expectation holds and raises when it does not.
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
            The first word count is two, matching its expectation, so execution continues to the success print. Empty text splits into no words, giving zero rather than the second assertion's expected one. That failed assertion raises with the supplied message, skips the following success print, and reaches the AssertionError handler. The handler prints its prefix and the error message separated by the space that print inserts.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "A true assertion is silent; a false assertion changes control flow by raising.",
            "Calculate both word counts before tracing which print statements can be reached.",
            "Follow the first assertion to its next line, then trace the second assertion through either normal continuation or its matching handler. Include the assertion message only where it is actually printed.",
        ],
    },
    {
        "id": "testing-s2",
        "title": "Your first test function",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Put an expectation in a discoverable test function

            You have a useful assertion, but you do not want to remember which checks to run by hand. Put it in a named function so a runner can discover and call it consistently.

            ```python
            def double(number):
                return number * 2

            def test_double_keeps_zero():
                assert double(0) == 0

            test_double_keeps_zero()
            print("test passed")
            # test passed
            ```

            A **test function** calls the code being checked and asserts its expected behavior. For this app, its name begins with `test_` and it takes no arguments. A **test runner** finds these functions and calls each one. Defining a function alone does not run its assertions.

            ```order
            def triple(number): return number * 3
            def test_triple(): assert triple(4) == 12
            test_triple()
            print("passed")
            ---
            The implementation and test must be defined before the test is called. The final message is reached only if the assertion succeeds.
            ```

            In test-writing exercises, the implementation is supplied in `target.py`. Import the function from there rather than redefining it. That implementation is the **code under test**. The written requirements are its **specification**, often shortened to spec.

            Your tests must accept correct behavior and reject buggy behavior. The app checks both by running them against a correct implementation and altered versions. Calculate expected answers independently from the spec; copying the implementation's answer into the expectation cannot reveal its mistakes.

            ```quiz
            Why is assert actual == actual not a useful result check?
            - [x] It does not compare against the promised answer :: A wrong result still equals itself.
            - [ ] Assertions cannot compare variables :: Variables are valid; the missing independent expectation is the problem.
            ```

            **Watch out:** a function with a different name may be a helper rather than a discovered test. Keep the required naming convention.

            **In short:** a test function gives the runner a repeatable, independently calculated expectation to check.
        ''',
        "prompt": r'''
            `target.py` contains a word counter used to estimate prompt sizes. Finish the test
            by replacing `___` with the right expected value.

            **Your job:** write a test (a function named `test_...`) for `count_words(text)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `text`: a string, e.g. `"the cat sat"`

            **What comes out**
            - the number of words, where words are separated by whitespace (an int)

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
            "Expected values come from the function's written behavior, independently of its implementation.",
            "Count whitespace-separated words in the supplied input, rather than characters or gaps.",
            "Replace the placeholder with a numerical expectation you can justify from that count. The comparison should fail if the implementation counts a different thing.",
        ],
    },
    {
        "id": "testing-s3",
        "title": "One test per behaviour",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Make failures describe the broken behavior

            A large test checks many things, but its first failure stops the rest of its body. Several focused tests give clearer reports and let other behaviors be checked even when one fails.

            ```python
            def bracket(text):
                return "[" + text + "]"
            def test_nonempty_text():
                assert bracket("sun") == "[sun]"
            def test_empty_text():
                assert bracket("") == "[]"
            test_nonempty_text()
            test_empty_text()
            print("two checks passed")
            # two checks passed
            ```

            A descriptive name tells you which expectation failed before you read the test body. Name the behavior, such as preserving text or handling empty input, rather than calling every check `test_one` or `test_two`.

            ```quiz
            A formatter must preserve punctuation exactly. Which assertion is stronger?
            - [x] Compare the entire returned string with the required string :: This catches missing punctuation, unwanted spaces, and wrong order together.
            - [ ] Check that one expected word occurs somewhere :: The word could be present while the rest of the formatting is wrong.
            ```

            Choose inputs that make the behavior visible. If a function must preserve letter case, all-lowercase or already-uppercase data may fail to distinguish two plausible implementations. A mixture gives the comparison something useful to detect.

            Focused tests can share the same implementation call shape while using different data. They should remain independent: one must not depend on another having run first or stored its result globally.

            ```predict
            def test_example():
                return "old"
            def test_example():
                return "new"
            print(test_example())
            ---
            The second definition replaces the first under the same name. A runner looking up that name can see only the newer function.
            ```

            **Watch out:** reusing a test function name silently removes the earlier test from discovery. Give each behavior its own distinct name.

            **In short:** focused, uniquely named tests with whole-result comparisons make failures informative.
        ''',
        "prompt": r'''
            A chat log printer formats each message on one line.

            **Your job:** write at least two test functions for `format_message(role, content)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `role`: a string like `"user"` or `"assistant"`
            - `content`: the message text, e.g. `"hi"`

            **What comes out**
            - a string: the role in UPPERCASE, a colon, one space, then the content unchanged

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
            "Each test should compare a complete returned line with its required formatting.",
            "Use distinct roles and content whose letter case makes accidental content conversion visible.",
            "Write at least two uniquely named tests. For each, derive the uppercase role, exact separator, and unchanged content from the specification, then compare the whole output.",
        ],
    },
    {
        "id": "testing-s4",
        "title": "Arrange, act, assert",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Check both the result and the original input

            A helper can return the right-looking answer while secretly changing a list another part of your app still uses. Testing only the return value misses that unwanted change.

            ```python
            def with_marker(values):
                return values + ["done"]
            original = ["ready"]
            result = with_marker(original)
            assert result == ["ready", "done"]
            assert original == ["ready"]
            print("result and input checked")
            # result and input checked
            ```

            The test follows **arrange, act, assert**. Arrange the starting data, act by calling the function, then assert what happened. The final stage may include the returned value and the state of objects after the call.

            A change outside a function's local work is a **side effect**. Mutating an input list is one example. Whether a side effect is correct depends on the specification: some operations promise to change an object, while others promise a fresh result.

            ```quiz
            A returned list contains the correct items, but the original list also gained the new item. Did the helper satisfy a promise to leave input unchanged?
            - [x] No :: Output correctness and input preservation are separate requirements.
            - [ ] Yes :: A correct returned value does not excuse an unwanted side effect.
            ```

            Keep your expected data independent. If `expected = original` refers to the same list, a mutation changes both names' view and may make a broken test pass. A separately written expected list or an appropriate snapshot avoids that shared-reference trap.

            ```predict
            original = ["first"]
            same = original
            original.append("second")
            print(same == original)
            ---
            The comparison is True because both names refer to the same changed list. This cannot establish that the original contents were preserved.
            ```

            **Watch out:** checking only the result length misses wrong content and wrong ordering. Compare the full expected structure as well as the preserved input.

            **In short:** arrange independent expectations, make the call, then check both its answer and its promised effects.
        ''',
        "prompt": r'''
            Chat history helpers must not change the history they are given.

            **Your job:** write tests for `add_message(history, role, content)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `history`: a list of message dicts, e.g. `[{"role": "user", "content": "hi"}]`
            - `role`, `content`: strings

            **What comes out**
            - a NEW list: all the old messages, then `{"role": role, "content": content}` at the end

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
            "There are two obligations: the new returned list and the original list after the call.",
            "Keep independent expected data for each so an accidental mutation cannot alter your expectation too.",
            "Compare the returned list with the complete ordered old-and-new messages, then compare the original history with its unchanged starting contents.",
        ],
    },
    {
        "id": "testing-s5",
        "title": "Test the edge cases",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Test the cases where the usual path changes

            A helper works for a typical list, but what happens when there is nothing to process? Empty input, one item, and values exactly at a limit often take different paths through the code.

            ```python
            def first_or_none(values):
                return values[0] if values else None
            print(first_or_none(["a", "b"]))
            # a
            print(first_or_none(["only"]))
            # only
            print(first_or_none([]))
            # None
            ```

            An input near the boundary of expected behavior is an **edge case**. Its importance comes from the specification, not from being unusual for its own sake. If a rule explicitly promises a value for empty input, test that promise directly.

            ```quiz
            A list-size rule accepts at most four items. Which inputs best distinguish an inclusive boundary from an exclusive one?
            - [x] Lists with three, four, and five items :: These check just below, exactly at, and just above the boundary.
            - [ ] Only a list with one item :: Both boundary implementations would likely accept it.
            ```

            One-item inputs can expose code that accidentally skips the last value or assumes there is a second item. Empty inputs expose missing fallback behavior, including division by zero in averaging code.

            Choose numbers whose expected result you can calculate independently. A mean divides the sum by the number of observations. When testing floating-point results, exact binary fractions such as halves can simplify examples; other values may need a tolerance.

            ```predict
            numbers = [1, 4]
            print(sum(numbers) / len(numbers))
            print(sum([]))
            ---
            The mean is 2.5. An empty sum is zero, but computing an average still needs a policy for its zero item count.
            ```

            **Watch out:** a test should check the promised empty result, not merely that the call does not crash. Returning None instead of zero can still break the caller.

            **In short:** test the normal case, the boundary itself, and the empty or single-item cases that change control flow.
        ''',
        "prompt": r'''
            Average tokens per message is a number shown on a usage dashboard.

            **Your job:** write tests for `average(numbers)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `numbers`: a list of ints, e.g. `[2, 4, 6]`

            **What comes out**
            - the mean (sum divided by count) as a float

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
            "Which behavior changes when there are no observations to average?",
            "The existing normal case does not check the special empty-input promise. A one-item case also makes an omitted final value visible.",
            "Add an exact empty-result assertion, then a separate single-observation test if needed. Derive every expected value from the stated mean and empty-input rules.",
        ],
    },
    {
        "id": "testing-s6",
        "title": "Fix: the test is wrong",
        "difficulty": 0,
        "mode": "tests",
        "lesson": r'''
            ## Check the expectation before changing the implementation

            A test fails after you write it. The implementation might be wrong, but your expected value might also misread the requirement. Fixing the wrong side can turn correct behavior into a bug.

            ```python
            def label(text):
                return "(" + text + ")"
            actual = label("note")
            print(repr(actual))
            # '(note)'
            print(actual == "note")
            # False
            print(actual == "(note)")
            # True
            ```

            A failing test that incorrectly accuses correct code is a **false positive**. To investigate, derive the expected result from the specification independently. Count separators, punctuation, and spaces as actual output characters, not visual decoration.

            `repr` makes invisible details easier to see. Quotes expose leading and trailing spaces, while escapes make newlines visible. Use that view to compare exact strings before deciding what should change.

            ```predict
            actual = "ready\n"
            print(repr(actual))
            print(actual == "ready")
            ---
            The representation exposes the final newline. The equality comparison is False because that newline is part of the string.
            ```

            Do not repair a false positive by weakening the test until it passes. Replacing a whole-result comparison with a length check or substring check may discard requirements that matter. Correct the expectation while keeping its ability to reject plausible wrong behavior.

            ```quiz
            The specification requires brackets, but your expected string omits them. What should change?
            - [x] The expected value in the test :: The specification is the source of the contract being checked.
            - [ ] Remove brackets from the implementation :: That would make the implementation violate the contract to satisfy a mistaken test.
            ```

            **Watch out:** copying the latest actual output into every failing expectation is not verification. First explain why that output follows the requirement; otherwise you may approve a regression.

            **In short:** a failure asks you to compare both code and expectation with the specification.
        ''',
        "prompt": r'''
            A teammate wrote tests for `truncate`, but one fails on code that is correct. Fix
            the wrong test so all tests pass on the real code - and still catch real bugs.

            **Your job:** write tests for `truncate(text, limit)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `text`: a string, e.g. `"hello world"`
            - `limit`: an int, the maximum number of characters to keep, e.g. `5`

            **What comes out**
            - `text` unchanged if it is at most `limit` characters long;
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
            "A failing expected value should be checked against the contract before the implementation is changed.",
            "For long text, the returned value includes both kept characters and the required ending marker.",
            "Work out the complete long-text result character by character and correct that expectation. Retain the short-text test so a fix cannot add the marker everywhere.",
        ],
    },
    {
        "id": "testing-s7",
        "title": "Catching the expected error",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Recognize when an exception is the correct result

            An input validator is supposed to refuse bad data. For that case, returning normally is the failure, and raising the promised error is success. Trace where execution moves after the call.

            ```python
            def require_nonnegative(number):
                if number < 0:
                    raise ValueError("negative input")
            for number in [1, -2, 0]:
                try:
                    require_nonnegative(number)
                    print(number, "accepted")
                except ValueError:
                    print(number, "rejected")
            # 1 accepted
            # -2 rejected
            # 0 accepted
            ```

            An **expected exception** is an exception that belongs to the specification for a particular input. The error's presence is not automatically a bug. What matters is whether it is the correct type and occurs for the correct inputs.

            When the call raises, Python skips the rest of that try block and looks for a matching handler. When it returns normally, the following statements run and the handler is skipped.

            ```quiz
            The contract says ValueError, but the call raises TypeError. Should an exception test pass?
            - [x] No :: Rejecting input with the wrong error type violates the specified behavior.
            - [ ] Yes, because any crash is enough :: An accidental crash can hide a broken validation path.
            ```

            Boundaries need particular attention. If zero is allowed, rejecting negative input does not establish that zero works. Test the endpoint separately from values clearly inside and outside the range.

            ```predict
            try:
                int("not-a-number")
                print("normal return")
            except ValueError:
                print("expected error")
            ---
            Conversion raises ValueError, so the normal-return print is skipped and only the handler's message appears.
            ```

            **Watch out:** a handler that accepts every exception may hide an unrelated programming error. Catch the specific promised type when testing validation.

            **In short:** trace normal returns and expected exceptions as different successful behaviors for different inputs.
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
            The loop checks each value independently. The interior value 0.7 returns normally, so its accepted line runs. Five violates the range and raises ValueError, skipping the accepted line and printing the handler's rejection message. Two equals the upper endpoint, which is included, so it also reaches the accepted line. Handling the failure allows the loop to continue to that final input.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "For each input, determine whether the validator returns or raises.",
            "The range includes its endpoints; an exception skips the remaining lines of the try block.",
            "Process inputs in order and choose the reached print statement for each. Include the stored exception message only on the rejection path.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "testing-1",
        "title": "Test that bad input raises",
        "difficulty": 1,
        "mode": "tests",
        "lesson": r'''
            ## Make the no-error path fail an error test

            You wrote a test that catches a required error, but the test also passes when the function raises nothing. Catching alone is insufficient: the normal-return path must explicitly fail.

            ```python
            def reject_blank(text):
                if not text:
                    raise ValueError("blank")
            def test_blank_rejected():
                try:
                    reject_blank("")
                    assert False, "expected an error"
                except ValueError:
                    pass
            test_blank_rejected()
            print("passed")
            # passed
            ```

            The call raises before the failing assertion, so the handler runs and the test finishes normally. If a buggy implementation returns instead, execution reaches `assert False` and the test fails. The assertion's error must not be caught by the same handler.

            ```quiz
            Why is except Exception dangerous around this pattern?
            - [x] It can catch the test's own AssertionError :: That makes the missing-error case look like a successful expected-error case.
            - [ ] It cannot catch ValueError :: Exception does include ValueError; that breadth is the problem here.
            ```

            Check both sides of a validation rule. Invalid inputs should raise the required type, while valid inputs should return the right value. Otherwise a function that rejects everything might satisfy your entire test file.

            Treat each kind of invalid input separately. An out-of-range number and text that cannot be converted into a number are different paths, even when both promise ValueError.

            ```match
            valid input test :: checks the returned value
            expected-error test :: checks rejection with the promised type
            boundary test :: checks whether the endpoint is accepted
            ```

            **Watch out:** comparing a numeric result with the original text can hide a misunderstood output contract. Write the expected value with its intended type and check type explicitly when the specification requires it.

            **In short:** an exception test needs a passing expected-error path and a failing normal-return path.
        ''',
        "prompt": r'''
            A settings form sends the model temperature as text. `parse_temperature` turns it
            into a number and rejects values outside the allowed range.

            **Your job:** write tests for `parse_temperature(value)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `value`: a string like `"0.7"`

            **What comes out**
            - the temperature as a float

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
            "Test accepted numeric conversion separately from each kind of rejection.",
            "Use boundary inputs to distinguish inclusive from exclusive limits, and let error tests fail when a call returns normally.",
            "Check a valid float result and both allowed endpoints. For out-of-range and nonnumeric text, catch the required exception specifically and assert failure if it never occurs.",
        ],
    },
    {
        "id": "testing-2",
        "title": "A raises() helper",
        "difficulty": 1,
        "lesson": r'''
            ## Let a helper make the call inside its error handler

            Several tests repeat the same error-catching structure. A helper can centralize it, but only if it receives the function before the function runs. Otherwise the error happens outside the helper's protection.

            ```python
            def invoke(function, *arguments):
                return function(*arguments)
            print(invoke(len, "chapter"))
            # 7
            print(invoke(max, 2, 8, 5))
            # 8
            ```

            A function without call parentheses is a **function object**, which you can pass like other values. The parameter `*arguments` collects the remaining positional arguments into a tuple. Using a star in the later call unpacks that tuple into separate arguments again.

            ```quiz
            Which value should a helper receive so it can control when integer conversion runs?
            - [x] The int function and its input separately :: The helper can perform the conversion inside its own try block.
            - [ ] The result of int on the input :: Python performs that conversion before the helper is called.
            ```

            An except clause can use a variable holding an exception class. It catches instances of that class and its subclasses. This lets a reusable helper apply the particular exception contract requested by each test.

            ```predict
            try:
                {}["absent"]
            except LookupError as error:
                print(type(error).__name__)
            ---
            KeyError inherits from LookupError, so a handler for LookupError catches it and the printed concrete class name is KeyError.
            ```

            Call the supplied function once. A preliminary call to see whether it works would consume side effects or scripted fake responses before the real check. Let unrelated exception types propagate so callers can tell a wrong error from the expected one.

            **Watch out:** passing `int("bad")` evaluates immediately and raises before your helper starts. Pass the function and arguments separately.

            **In short:** receive an uncalled function, invoke it inside the handler, and catch only the requested exception family.
        ''',
        "prompt": r'''
            Build the helper that error tests use, so they can be one line long.

            **Your job:** write `raises(exc_type, fn, *args)`

            **What goes in**

            - `exc_type`: an exception class, e.g. `ValueError`
            - `fn`: a function (not called yet), e.g. `int`
            - `*args`: the arguments to call `fn` with

            **What comes out**
            - `True` if `fn(*args)` raises `exc_type` (or a subclass of it),
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
            "The helper must receive a callable before that callable executes.",
            "Perform exactly one forwarded call inside a handler for the requested exception class.",
            "If that class or its subclass is caught, give the success Boolean. If the call completes, give the no-error Boolean. Leave other error types uncaught.",
        ],
    },
    {
        "id": "testing-3",
        "title": "Fixtures as functions",
        "difficulty": 1,
        "mode": "tests",
        "lesson": r'''
            ## Start each test with independent data

            One test adds an item to a shared list, and a later test unexpectedly starts with that item already present. The second failure is caused by test setup leaking across cases rather than the behavior you meant to inspect.

            ```python
            def make_folder():
                return {"files": []}
            a = make_folder()
            b = make_folder()
            a["files"].append("draft")
            print(a["files"])
            # ['draft']
            print(b["files"])
            # []
            ```

            Reusable setup data is often called a **fixture**. Here a plain helper function creates the fixture, returning a new object for each call. Its name does not begin with `test_`, because it supports tests rather than being independently discovered as a test.

            ```predict
            shared = []
            def bad_fixture():
                return {"files": shared}
            a = bad_fixture()
            b = bad_fixture()
            a["files"].append("draft")
            print(b["files"])
            ---
            The dictionaries are separate but their nested file lists are the same object. A fresh outer container alone does not guarantee independent nested state.
            ```

            Choose fixture contents that make several behaviors observable. For a sequence, distinct values make first-versus-last mistakes visible. For categories, unequal or mixed counts make counting the wrong category detectable.

            You can also test independence in the application itself. Create two instances, change one, and assert the other retains its original state. This finds accidental class-level collections shared by every instance.

            ```quiz
            Should a test rely on another test creating its fixture first?
            - [x] No :: Each test should work when run independently and in a different order.
            - [ ] Yes, if the names sort correctly :: Ordering conventions do not replace independent setup.
            ```

            **Watch out:** storing a mutable fixture globally can make failures depend on test order. Build fresh state for each test unless sharing is intentional and controlled.

            **In short:** fixture helpers reuse setup instructions while creating independent objects for each test.
        ''',
        "prompt": r'''
            `target.py` has a small `Conversation` class. Write tests for it, using a fixture
            function (e.g. `make_conversation()`) so each test starts fresh.

            **Your job:** write tests for the class `Conversation(system)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `Conversation("Be brief")` starts with one message: `{"role": "system", "content": "Be brief"}`
              in its `.messages` list
            - `.add(role, content)`: appends `{"role": role, "content": content}`;
              `role` must be `"user"` or `"assistant"`, anything else raises `ValueError`
            - `.last()`: **returns** the content of the most recent message
            - `.count(role)`: **returns** how many messages have that role

            **What comes out**
            - Your test functions pass for the described behavior and fail when that behavior is broken.

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
            "A setup helper should create new state on every call.",
            "Choose messages that make newest content and per-role counts distinguishable, then add a separate independence check.",
            "Build the fixture, test each stated method and role rejection, and create two conversations to verify that changes to one do not appear in the other.",
        ],
    },
    {
        "id": "testing-4",
        "title": "Build a fake LLM",
        "difficulty": 1,
        "lesson": r'''
            ## Replace an external service with predictable replies

            Your test needs to check what happens after a model answers. A live service adds waiting, network failures, cost, and responses you do not fully control. A local stand-in can supply exactly the replies needed to exercise your code.

            ```python
            class FakeLookup:
                def __init__(self, replies):
                    self.remaining = list(replies)
                    self.requests = []
                def lookup(self, name):
                    self.requests.append(name)
                    return self.remaining.pop(0)
            fake = FakeLookup(["found", "missing"])
            print(fake.lookup("guide"), fake.lookup("notes"))
            # found missing
            print(fake.requests)
            # ['guide', 'notes']
            ```

            This is a **test double**, a replacement dependency used during tests. We call this local stand-in a **fake**. A double returning predetermined answers is often called a **stub**; one recording calls is a **spy**. Terminology varies, but the behavior you need is concrete.

            ```quiz
            Why copy the supplied reply list before consuming it?
            - [x] Consuming internal replies should not change the caller's list :: The fake owns its progress independently of the script provided by the test.
            - [ ] Lists cannot be stored on objects :: Lists are valid attributes; shared mutation is the concern.
            ```

            A scripted fake has state: which replies remain and which requests have arrived. Decide the order of those changes carefully. Even a call that runs out of scripted replies may need to be recorded so a test can diagnose an unexpected extra request.

            ```match
            scripted replies :: determine what the dependency returns
            recorded calls :: show how the dependency was used
            fresh instance state :: prevents one test from affecting another
            ```

            **Watch out:** silently returning a default forever can hide repeated calls. A clear exhaustion error makes extra calls visible when the script is meant to be finite.

            **In short:** a predictable fake supplies controlled replies and records enough interaction to check your code's behavior.
        ''',
        "prompt": r'''
            Every AI feature you test later will need a stand-in model. Build one.

            **Your job:** write a class `FakeLLM`

            **What goes in**

            - `FakeLLM(replies)`: `replies` is a list of strings to return, in order
            - `.complete(prompt)`: records `prompt`, then **returns** the next reply
            - `.prompts`: a list of every prompt received so far, in order (starts empty)

            **What comes out**
            - The public methods behave as described above, with independent state for every instance.

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
            "Your fake needs independent records of remaining answers and received prompts.",
            "Copy the reply script and create per-instance call history. Recording must happen even when no reply remains.",
            "On construction, prepare the two collections. On each call, record the prompt, reject exhaustion with the promised error, otherwise consume and return the earliest unused reply.",
        ],
    },
    {
        "id": "testing-5",
        "title": "Inject a fake model",
        "difficulty": 1,
        "mode": "tests",
        "lesson": r'''
            ## Pass a fake into the code you want to test

            A function that creates its own remote client is hard to isolate. If it receives that dependency from its caller, a test can substitute a local function and observe how it is used.

            ```python
            def title_for(text, model):
                return model("Title: " + text).strip()
            calls = []
            def fake(prompt):
                calls.append(prompt)
                return "  Notes  "
            print(title_for("gardening", fake))
            # Notes
            print(calls)
            # ['Title: gardening']
            ```

            Passing the dependency in from outside is **dependency injection**. The application can provide the real callable, while a test provides a fake with the same calling shape. The function under test should not need to know which it received.

            ```quiz
            The contract says to remove surrounding whitespace from replies. Which fake response tests that requirement?
            - [x] A reply with spaces or newlines at its ends :: Leaving the reply untrimmed would now change the asserted output.
            - [ ] A reply already free of surrounding whitespace :: Both trimming and doing nothing would give the same result.
            ```

            Check interactions as well as returned text. The recorded calls can prove how often the dependency ran and whether the original input reached it. For a blank input that should skip work, an empty call record proves the absence of a call.

            Avoid specifying more than the contract promises. If a prompt must contain the document, do not insist on a particular instruction prefix unless that exact prefix is required. A test should reject wrong behavior while allowing different correct implementations.

            ```match
            return assertion :: checks how the reply is processed
            call-count assertion :: checks how often the dependency runs
            prompt assertion :: checks what input reaches the dependency
            ```

            **Watch out:** a fake that returns the right answer without recording calls cannot reveal unnecessary extra requests by itself.

            **In short:** inject a controlled dependency and test its output, inputs, and call count according to the contract.
        ''',
        "prompt": r'''
            `summarize` asks a model for a one-sentence summary. The model is injected, so you
            can test it with a fake function you write in your test file.

            **Your job:** write tests for `summarize(text, llm)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `text`: the document to summarize, a string
            - `llm`: a function that takes a prompt string and returns a reply string

            **What comes out**
            - the model's reply with surrounding whitespace removed

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
            "A fake can both supply a reply and record how summarize used it.",
            "Pick a reply with surrounding whitespace, and test blank input separately from a normal document.",
            "Complete the recording fake. Check processed output, one call containing the original text, and no calls for blank input. Avoid asserting prompt wording beyond the documented containment rule.",
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
            ## Write ordinary tests a larger runner can discover

            Your tests are useful beyond this app. A project runner can discover the same named functions, execute them, and report assertion failures without requiring you to call each test manually.

            ```python
            def initials(text):
                return "".join(word[0] for word in text.split())
            def test_initials_ignore_extra_gaps():
                assert initials("  red   green blue ") == "rgb"
            test_initials_ignore_extra_gaps()
            print("passed")
            # passed
            ```

            **pytest** is a third-party Python test runner. Under its usual conventions, it discovers test files and functions named with `test_`. Ordinary assertions work, and its reports help display the actual and expected values when a comparison fails.

            The test above needs no pytest installation to run directly. In a project you would place the test in a discovered file and let the runner make the call. Discovery replaces manual invocation, not the need for good expectations.

            ```quiz
            A runner discovers your tests successfully. Does that prove the tests cover every stated behavior?
            - [x] No :: Discovery only proves the checks ran; their inputs and assertions determine what bugs they can reveal.
            - [ ] Yes :: A runner cannot infer every missing scenario from a passing assertion.
            ```

            Pytest adds tools for expected exceptions, reusable setup, and running one test with many input sets. `pytest.raises` expresses an expected-error check; fixtures organize setup; parameterization repeats a test over cases. The research link introduces these tools, but this exercise uses plain functions and asserts.

            Choose data that distinguishes plausible errors. A normalization function needs messy spacing to test spacing rules, and mixed case to test case conversion. A clean example may leave those branches untested.

            ```predict
            print("a  b".split(" "))
            print("a  b".split())
            ---
            Splitting on one literal space preserves an empty piece between adjacent spaces. Splitting on arbitrary whitespace collapses that gap instead.
            ```

            **Watch out:** a framework cannot rescue a test that checks only an already-clean input.

            **In short:** keep writing focused plain assertions; a runner automates discovery and reporting around them.
        ''',
        "prompt": r'''
            Document ids in a RAG index are made from titles. Test the slug maker.

            **Your job:** write tests for `make_slug(title)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `title`: a string, e.g. `"  Intro to  RAG "`

            **What comes out**
            - a string: the title in lowercase, with words joined by single dashes

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
            "Choose inputs where case conversion and whitespace normalization visibly change the result.",
            "A clean example alone cannot reveal repeated-gap or boundary-gap mistakes.",
            "Write independent tests for an ordinary title and one with mixed case and messy whitespace, comparing each whole expected slug rather than just its words or length.",
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
            ## Turn each behavior rule into evidence

            A function has several requirements, and one successful example cannot establish them all. Read the contract as a list of behaviors and choose cases that distinguish each behavior from a plausible mistake.

            ```python
            def groups(values, size):
                return [values[start:start + size] for start in range(0, len(values), size)]
            print(groups([1, 2, 3, 4], 2))
            # [[1, 2], [3, 4]]
            print(groups([1, 2, 3], 2))
            # [[1, 2], [3]]
            ```

            The first example checks an exact split. The second checks a leftover group. A buggy function that discards leftovers could pass the first and fail the second. These are related but distinct cases.

            A collection of tests for a piece of code is a **test suite**. Putting a suite together means covering normal values, edges, boundaries, and promised errors without inventing requirements the function never agreed to meet.

            ```quiz
            An invalid-size rule rejects every value below one. Is testing only zero enough to distinguish all likely mistakes?
            - [x] No :: Code may explicitly reject zero while accidentally allowing negative values.
            - [ ] Yes :: Zero and negative values can follow different branches or library behavior.
            ```

            Compare the whole result to catch loss, duplication, order changes, and wrong item sizes. Checking only how many groups came back leaves their contents unverified. Use distinct items so a misplaced or repeated item is visible.

            An exception check should fail if no exception occurs and should accept only the promised exception family. Pair rejection tests with successful cases so an implementation that rejects everything cannot pass.

            ```match
            exact split :: checks boundaries without a remainder
            uneven split :: checks the final partial group
            empty input :: checks the absence of output items
            invalid size :: checks deliberate rejection
            ```

            **Watch out:** the phrase "thorough tests" does not mean random inputs alone. Small chosen cases often expose specific faults more clearly.

            **In short:** build a suite from distinct contract behaviors and exact expected outcomes.
        ''',
        "prompt": r'''
            RAG pipelines split documents into chunks before embedding them. Write a test suite
            that would catch any plausible bug in this chunker.

            **Your job:** write tests for `chunk_words(text, size)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `text`: a string of words separated by whitespace
            - `size`: an int, the maximum number of words per chunk

            **What comes out**
            - a list of strings; each chunk is up to `size` words joined by single spaces

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
            "Map normal results, leftover handling, empty input, and invalid sizes to separate tests.",
            "Use distinct words and compare complete chunk lists so loss, overlap, and wrong sizes are visible.",
            "Test exact and uneven splits, empty or whitespace-only input, and more than one invalid size. Make each error test fail when the call returns normally.",
        ],
    },
    {
        "id": "testing-8",
        "title": "A tiny test runner",
        "difficulty": 2,
        "lesson": r'''
            ## Keep running after one test fails

            A test report should include all results, not stop at the first failure. You need a loop that isolates each test call and records whether it returned normally, failed an assertion, or raised an unexpected error.

            ```python
            def test_good(): assert 3 > 1
            def test_bad():
                raise ValueError("broken setup")
            for check in [test_good, test_bad]:
                try:
                    check()
                except Exception as error:
                    print(type(error).__name__)
                else:
                    print("passed")
            # passed
            # ValueError
            ```

            Putting it together requires exception handling inside the per-test loop. A try block around the whole loop would leave later tests unrun after the first failure. The `else` block runs only when the protected call raises nothing, making it a natural place to record success.

            ```quiz
            Where should the runner catch an individual test's failure?
            - [x] Around that one call inside the loop :: After recording it, the loop can continue to the next test.
            - [ ] Only outside the entire loop :: An escaping exception exits the loop before the handler runs.
            ```

            An assertion failure and an unexpected crash may need different report formats. Catch the more specific exception first, because `AssertionError` is itself a kind of `Exception`. If the broad handler comes first, it consumes the specific case too.

            ```predict
            error = AssertionError()
            print(repr(str(error)))
            print(type(ValueError("bad")).__name__)
            ---
            An assertion without a message has empty message text. An exception's class name is available independently from its message.
            ```

            Filter discovered names before calling functions. A helper stored alongside tests must remain uncalled unless its name meets the runner's contract. Preserve input order so the report is predictable.

            **Watch out:** a test that returns False has still returned normally. This runner judges exceptions, not return-value truthiness.

            **In short:** select tests, isolate each call, classify its outcome, and continue collecting the report.
        ''',
        "prompt": r'''
            Build the core of a test runner: run test functions and report results.

            **Your job:** write `run_tests(tests)`

            **What goes in**

            - `tests`: a dict mapping names to functions, e.g. `{"test_ok": fn1, "helper": fn2}`

            **What comes out**
            - a dict `{"passed": [...names...], "failed": {name: message}}`

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
            "Each discovered test needs its own protected call so one failure cannot end the loop.",
            "Catch assertion failures before the general exception handler and reserve the normal-return path for passed names.",
            "Filter names, call eligible functions in order, record the specified assertion fallback or typed error message, and collect successful names. Return both collections after all calls finish.",
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

            **Your job:** write tests for `call_with_retry(llm, prompt, attempts=3)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `llm`: a function taking a prompt string and returning a reply string
            - `prompt`: the prompt string to send
            - `attempts`: the maximum number of calls in total (an int >= 1)

            **What comes out**
            - the first successful reply

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
            "A retry test needs control over both the sequence of failures and the count of calls.",
            "Make the fake record prompts and fail a chosen number of times before succeeding. Use another error type to test the no-retry branch.",
            "Check eventual success, immediate success with no extra calls, exhaustion at the total attempt limit, and immediate propagation of an unrelated error. Assert call counts as well as returned values or exceptions.",
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

            **Your job:** write tests for `parse_tool_call(reply)` from `target.py`

            The following inputs and outputs describe the supplied implementation. Your job is to test it, not replace it.

            **What goes in**

            - `reply`: a string of JSON, e.g. `'{"name": "search", "args": {"q": "cats"}}'`

            **What comes out**
            - a tuple `(name, args)`, e.g. `("search", {"q": "cats"})`

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
            "Separate valid output shape, optional defaults, and each invalid-input rule.",
            "Missing, empty, and wrong-type values are different cases even when the error type is the same.",
            "Compare complete tuples for normal and missing-args inputs. Use a specific ValueError helper for invalid JSON, non-object JSON, every bad-name form, and non-object arguments.",
        ],
    },
    {
        "id": "testing-11",
        "title": "A scripted fake model",
        "difficulty": 3,
        "prompt": r'''
            A stricter fake for agent tests: it knows which prompt to expect at each step and
            fails loudly if the code under test goes off-script.

            **Your job:** write a class `ScriptedLLM`

            **What goes in**

            - `ScriptedLLM(script)`: `script` is a list of `(expected, reply)` pairs (tuples of two strings)
            - `.complete(prompt)`: handles the next step of the script:
              if `expected` is **contained in** `prompt`, **returns** `reply`
            - `.assert_done()`: checks that every step was used
            - `.calls`: the number of `.complete` calls so far (an int, starts at `0`)

            **What comes out**
            - The public methods behave as described above, with independent state for every instance.

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
            "Track remaining script steps separately from the total call count.",
            "Count a call before any validation, consume the next expected step, and make error messages identify the violated expectation.",
            "Copy the script, initialize the counter, and on each call record progress before checking exhaustion and expected-text containment. Return the scripted reply on success; the completion assertion checks how many steps remain.",
        ],
    },
]
