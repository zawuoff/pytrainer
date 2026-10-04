TOPIC = {
    "id": "functions",
    "title": "Functions",
    "track": "foundations",
    "order": 8,
    "requires": ["loops"],
    "summary": """
        Defining and calling functions: parameters, defaults, keyword-only arguments,
        *args/**kwargs, multiple return values, scope, higher-order functions and closures.
    """,
    "concepts": ["parameters", "default arguments", "keyword-only arguments", "*args",
                 "**kwargs", "return values", "mutable default trap", "scope",
                 "higher-order functions", "closures", "type hints", "docstrings"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["function", "def", "return", "parameter", "argument", "default value",
                 "keyword argument", "args", "kwargs", "scope", "local", "type hint", "docstring",
                 "closure", "none"],
    "cards": [
        {
            "syntax": "def name(parameter):  ...  return value",
            "explain": "Defines a function. A call runs the body and evaluates to the value after return, or None when no return runs.",
            "example": r'''
                def shout(word):
                    return word + "!"

                print(shout("hi"))
                # hi!
            ''',
        },
        {
            "syntax": "def name(a, b=default):",
            "explain": "b gets the default value when the call leaves it out. A call can also pass an argument by name: b=value.",
            "example": r'''
                def label(text, role="user"):
                    return f"{role}: {text}"

                print(label("hi"))
                # user: hi
                print(label("be brief", role="system"))
                # system: be brief
            ''',
        },
        {
            "syntax": "return a, b   /   x, y = f()",
            "explain": "Returns one tuple that holds both values. The call can unpack it into one name per item.",
            "example": r'''
                def low_high(numbers):
                    return min(numbers), max(numbers)

                low, high = low_high([3, 9, 5])
                print(low, high)
                # 3 9
            ''',
        },
        {
            "syntax": "def name(*args, **kwargs):",
            "explain": "*args collects the extra positional arguments into a tuple. **kwargs collects the extra keyword arguments into a dict.",
            "example": r'''
                def describe(model, *prompts, **options):
                    print(model, prompts, options)

                describe("gpt-4o", "hi", "bye", max_tokens=50)
                # gpt-4o ('hi', 'bye') {'max_tokens': 50}
            ''',
        },
        {
            "syntax": 'def name(x: int) -> float:  """Docstring."""',
            "explain": "Type hints state the expected types. Python does not check them. The docstring describes the function.",
            "example": r'''
                def cost(tokens: int, price: float = 0.002) -> float:
                    """Return the dollar cost of a request."""
                    return tokens * price

                print(cost(1000))
                # 2.0
                print(cost.__doc__)
                # Return the dollar cost of a request.
            ''',
        },
        {
            "syntax": "def outer(x):  def inner(y): ...  return inner",
            "explain": "A closure: outer returns the function inner, and inner can still read x after outer has returned.",
            "example": r'''
                def make_prefixer(prefix):
                    def add_prefix(text):
                        return prefix + text
                    return add_prefix

                tag = make_prefixer("user: ")
                print(tag("hi"))
                # user: hi
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Functions

### Define and call

A **function** is a named block of code that runs when you call it. `def` creates the
function. The indented lines under `def` are the **body**. A **call** is the function
name followed by parentheses, and it runs the body.

```python
def greet(name):
    text = f"Hello, {name}!"
    return text

first = greet("Ada")
second = greet("Bob")
print(first)
# Hello, Ada!
print(second)
# Hello, Bob!
```

A **parameter** is a name in the `def` line, here `name`. An **argument** is the value
you pass in the call, here `"Ada"`. Each call assigns the argument to the parameter and
then runs the body.

Step through the program to see `name` and `text` exist only while the body runs.

```diagram
{"type": "trace", "title": "Two calls to greet", "code": ["def greet(name):", "    text = f\"Hello, {name}!\"", "    return text", "", "first = greet(\"Ada\")", "second = greet(\"Bob\")", "print(first)", "print(second)"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 5, "vars": {}, "out": ""},
  {"line": 2, "vars": {"name": "'Ada'"}, "out": ""},
  {"line": 3, "vars": {"name": "'Ada'", "text": "'Hello, Ada!'"}, "out": ""},
  {"line": 6, "vars": {"first": "'Hello, Ada!'"}, "out": ""},
  {"line": 2, "vars": {"name": "'Bob'"}, "out": ""},
  {"line": 3, "vars": {"name": "'Bob'", "text": "'Hello, Bob!'"}, "out": ""},
  {"line": 7, "vars": {"first": "'Hello, Ada!'", "second": "'Hello, Bob!'"}, "out": ""},
  {"line": 8, "vars": {"first": "'Hello, Ada!'", "second": "'Hello, Bob!'"}, "out": "Hello, Ada!\n"},
  {"line": null, "vars": {"first": "'Hello, Ada!'", "second": "'Hello, Bob!'"}, "out": "Hello, Ada!\nHello, Bob!\n"}
]}
```

### Return values

`return` ends the function immediately and sends a value to the caller, which is the
line that called the function. That value is the **return value**. Code after `return`
in the body does not run. A function that ends without running `return` returns `None`,
the value Python uses for "no value".

```python
def log(text):
    print(text)

result = log("sent")
# sent
print(result)
# None
```

`return low, high` returns one **tuple**: an ordered group of values that cannot be
changed after it is created. Python prints a tuple in parentheses. You can assign its items
to two names in one statement, which is called **unpacking**.

```python
def low_high(numbers):
    return min(numbers), max(numbers)

low, high = low_high([3, 9, 5])
print(low, high)
# 3 9
```

### Default values and keyword arguments

A **default value** is written as `name=value` in the `def` line. Python uses it when
the call leaves that argument out. A **keyword argument** names the parameter in the call.

```python
def label(text, role="user"):
    return f"{role}: {text}"

print(label("hi"))
# user: hi
print(label("be brief", role="system"))
# system: be brief
```

### Scope

**Scope** is the part of the program where a name can be used. A variable assigned
inside a function is **local**: it exists only while that call runs. Assigning to a
name inside a function does not change a variable with the same name outside it.

### Type hints and docstrings

A **type hint** states the expected type: `tokens: int` for a parameter, `-> float` for
the return value. Python does not check hints when the program runs. A **docstring** is
a string on the first line of the body that describes the function. Python stores it,
and you read it by writing `.__doc__` after the function name.

```python
def cost(tokens: int, price: float = 0.002) -> float:
    """Return the dollar cost of a request."""
    return tokens * price

print(cost(1000))
# 2.0
print(cost.__doc__)
# Return the dollar cost of a request.
```

### `*args` and `**kwargs`

A **positional argument** is an argument passed without a name. A parameter with one
star collects the extra positional arguments into a tuple. A parameter with two stars
collects the extra keyword arguments into a dict. A parameter written after the starred
one is **keyword-only**: the call must pass it by name. Programmers usually name the two
starred parameters `*args` (arguments) and `**kwargs` (keyword arguments). Any names work.

```python
def describe(model, *prompts, temperature=1.0, **options):
    print(model, prompts, temperature, options)

describe("gpt-4o", "hi", "bye", max_tokens=50)
# gpt-4o ('hi', 'bye') 1.0 {'max_tokens': 50}
```

`"gpt-4o"` goes to `model`. The two other positional arguments go into the tuple
`prompts`. The call does not pass `temperature`, so it keeps its default. `max_tokens`
is not a parameter name, so it goes into the dict `options`.

### Functions as values

A function is a value. You can assign it to a variable, pass it as an argument and
return it. A **higher-order function** takes a function as an argument or returns one.
A **closure** is a function defined inside another function that keeps access to the
outer function's variables after the outer function has returned.

```python
def make_prefixer(prefix):
    def add_prefix(text):
        return prefix + text
    return add_prefix

tag = make_prefixer("user: ")
print(tag("hi"))
# user: hi
```

`make_prefixer("user: ")` returns the inner function `add_prefix`, and the assignment
stores it in `tag`. `tag("hi")` calls that function. It still reads `prefix`, which is
`"user: "`, although `make_prefixer` has already returned.

### Common mistakes

- `print` does not return a value. The tests in this app check the return value.
- `result = greet` assigns the function itself. `result = greet("Ada")` calls it.
- A default value is created once, when the `def` line runs. A list or dict default
  such as `items=[]` is the same object in every call. Use `items=None`, then
  `if items is None: items = []`.
- `min([])` and a division by `len([])` both raise an error. Check for the empty list
  first and return early.
'''

EXERCISES = [
    {
        "id": "functions-s1",
        "title": "Return vs print",
        "difficulty": 0,
        "lesson": r'''
            ## Give a result back to the next line

            You have calculated a price and want to add it to a bill. Seeing the price on the screen is useful, but the next calculation needs the actual number. This is why functions can give values back as well as display them.

            ```python
            def delivery_cost():
                return 4

            fee = delivery_cost()
            print(fee + 2)
            # 6
            ```

            The `def` line creates a named piece of reusable code, a **function**. Writing its name with parentheses calls it: Python runs the indented lines. `return` ends that run and gives its value to the calling line. Here the **return value** becomes the value of `fee`.

            ```predict
            def show_fee():
                print(4)

            fee = show_fee()
            print(fee)
            ---
            The function prints 4 itself. Because it reaches the end without return, the calling line receives None, which the last line prints.
            ```

            Printing sends text to the output area. It does not supply that displayed value to the calling line. A function that reaches its end without returning a value gives back `None`, Python's value for an absent result. Assigning the call to a variable stores this returned value, not whatever appeared on screen.

            ```quiz
            A function returns 9 but never prints. What appears when you only call it in a script?
            - [x] Nothing. :: Returning gives the caller a value; displaying it is a separate action.
            - [ ] 9 :: A script needs a print call to display the returned number.
            ```

            **Watch out:** correct-looking output can hide a wrong return value. Check what the calling line actually receives.

            Use return when another part of the program needs your answer.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            def shout(word):
                return word + "!"

            def whisper(word):
                print(word + "...")

            print(shout("hi"))
            result = whisper("HEY")
            print(result)
        ''',
        "solution": r'''
            hi!
            HEY...
            None
        ''',
        "explanation": r'''
            The first outer print displays the text returned by shout. Next, calling whisper runs its own print, producing the second line. That helper never returns a value explicitly, so result receives None, which the final print displays. Reading visible output and return values separately explains all three lines.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Track displayed output separately from returned values.",
            "The first helper returns text; the second displays text during its own call.",
            "Follow each print in execution order, then consider the default return value of a function without return.",
        ],
    },
    {
        "id": "functions-s2",
        "title": "Fill in the greeting",
        "difficulty": 0,
        "lesson": r'''
            ## Reuse the same code with different values

            A report needs a label for whichever document is being processed. Writing a separate function for every document would repeat the same work. Let the caller supply the changing part instead.

            ```python
            def document_label(title):
                return f"Reading: {title}"

            print(document_label("Guide"))
            # Reading: Guide
            print(document_label("Notes"))
            # Reading: Notes
            ```

            The name `title` in the definition stands for the incoming value. That name is a **parameter**. The actual value supplied in a call, such as `"Guide"`, is an **argument**. Python assigns that value to the parameter for this call, then runs the function's indented **body**. The next call runs the same body with a different value.

            ```fill
            def document_label(title):
                return f"Reading: {___}"
            print(document_label("Manual"))
            ---
            - [x] title :: The parameter holds this call's document title.
            - [ ] "Guide" :: A fixed string would ignore the caller's title.
            - [ ] missing :: No value has been assigned to this name, so it raises NameError.
            ```

            Remember the f-strings chapter: braces insert the value of an expression into text. Here the expression can be the parameter name. You do not need to assign the example title inside the function, because calling the function already supplies it.

            ```match
            parameter :: name written in the definition
            argument :: value supplied in a call
            body :: indented code run by the call
            ```

            **Watch out:** a hard-coded example may pass one check and fail another. Use the supplied value wherever the text must vary.

            One definition can handle many inputs because each call supplies its own values.
        ''',
        "prompt": r'''
            A chat app greets each user by name. Complete the function by replacing the `___`.

            **Your job:** write `greet(name)`

            **What goes in**
            - `name`: a string, e.g. `"Ada"`

            **What comes out**
            - a string like `"Hello, Ada!"`

            **Rules**
            - Return the text (don't print it): `Hello`, a comma, one space, the name, then `!`.
            - It must work for any name, not just `"Ada"`.

            **Examples**
            ```python
            greet("Ada")    # returns "Hello, Ada!"
            greet("Bob")    # returns "Hello, Bob!"
            ```

            For an empty name, `greet("")` returns `"Hello, !"`.
        ''',
        "starter": r'''
            def greet(name):
                return ___
        ''',
        "tests": r'''
            from solution import greet

            def test_returns_hello_ada():
                got = greet("Ada")
                assert got == "Hello, Ada!", f"got {got!r}"

            def test_works_for_another_name():
                got = greet("Bob")
                assert got == "Hello, Bob!", f"got {got!r}"
        ''',
        "solution": r'''
            def greet(name):
                return f"Hello, {name}!"
        ''',
        "hints": [
            "Use the incoming name rather than one fixed example name.",
            "Build the greeting as text, preserving the punctuation and spacing shown.",
            "Replace the gap with a string expression that incorporates this call's name, and let the existing return give it back.",
        ],
    },
    {
        "id": "functions-s3",
        "title": "Fix: nothing comes back",
        "difficulty": 0,
        "lesson": r'''
            ## Make a calculation available to its caller

            A helper displays a number, yet the next calculation fails. The displayed answer might be correct while the helper still gives back no usable number. Trace the result from the function to the line that called it.

            ```python
            def square(value):
                return value * value

            answer = square(3)
            print(answer + 1)
            # 10
            ```

            The calculation runs inside `square`. Its return value becomes `answer`, so adding one works. If the helper only printed the square, `answer` would receive `None`. The visible number and the value stored by an assignment are separate things.

            ```try
            def next_page(page):
                print(page + 1)

            result = next_page(4)
            print(result)
            ---
            Change the function so this whole program prints just one line: `5`.
            ---
            def next_page(page):
                return page + 1

            result = next_page(4)
            print(result)
            ---
            The function gives back the number. Only the outer print displays it.
            ```

            Returning also stops the current call immediately. Any later statements in that body are skipped. This matters when you add debug prints: a print after an unconditional return will never run, even though the function was called correctly.

            ```predict
            def answer():
                return 7
                print("later")

            print(answer())
            ---
            Only 7 appears. Returning finishes the call before the inner print can run.
            ```

            **Watch out:** `TypeError` involving `NoneType` in a later calculation often means an earlier helper forgot to return its result. Look at the producing function, not only the failing line.

            A reusable calculation needs to hand its result back.
        ''',
        "prompt": r'''
            `double(n)` should give back twice `n`, but the checks receive `None`. Fix the bug.

            **Your job:** write `double(n)`

            **What goes in**
            - `n`: a number (int), e.g. `4` or `-3`

            **What comes out**
            - `n` times 2, as a number

            **Rules**
            - The value must be **returned** to the caller; printing it is not enough.
            - Negative numbers work the same way.

            **Examples**
            ```python
            double(4)     # returns 8
            double(-3)    # returns -6
            ```

            For zero, `double(0)` returns `0`.
        ''',
        "starter": r'''
            def double(n):
                print(n * 2)
        ''',
        "tests": r'''
            from solution import double

            def test_returns_eight_for_four():
                got = double(4)
                assert got == 8, f"double(4) gave back {got!r}"

            def test_returns_minus_six_for_minus_three():
                got = double(-3)
                assert got == -6, f"double(-3) gave back {got!r}"
        ''',
        "solution": r'''
            def double(n):
                return n * 2
        ''',
        "hints": [
            "Compare displaying a result with giving a result back.",
            "The calculation is already correct; inspect how it leaves the function.",
            "Keep the arithmetic, but make its answer become the call's return value.",
        ],
    },
    {
        "id": "functions-s4",
        "title": "Default price",
        "difficulty": 0,
        "lesson": r'''
            ## Choose a value when the caller leaves one out

            Most reports show ten rows, but sometimes a caller wants fewer. Requiring every caller to write the usual number adds noise. You can put that usual value in the function definition and still let individual calls replace it.

            ```python
            def page_size(rows=10):
                return rows

            print(page_size())
            # 10
            print(page_size(4))
            # 4
            print(page_size(rows=0))
            # 0
            ```

            The value after the equals sign is the parameter's **default value**. It is used only when that argument is omitted. Zero does not mean missing: the third call deliberately supplies zero, so zero wins.

            An argument written with its parameter name, such as `rows=0`, is a **keyword argument**. An argument written without its name is matched by position. Naming arguments helps readers understand what a number means without looking up the definition.

            ```predict
            def area(width, height=3):
                return width * height

            print(area(2))
            print(area(2, height=5))
            ---
            The first call uses height 3. The named height in the second call replaces the default with 5.
            ```

            Required parameters come before parameters with defaults. That keeps the ordinary positional call unambiguous: Python knows which supplied value belongs to which required name before it fills omissions.

            ```quiz
            When is a default used?
            - [x] When the caller omits that argument. :: Supplying any value replaces the default.
            - [ ] Whenever the caller supplies zero. :: Zero is an explicit value, not an omission.
            ```

            **Watch out:** putting a required parameter after one with a default raises `SyntaxError`. Arrange the definition before debugging its body.

            Defaults describe what happens when a caller leaves a choice unspecified.
        ''',
        "prompt": r'''
            An API bills per token. Compute the cost of a request.

            **Your job:** write `request_cost(tokens, price=0.002)`

            **What goes in**
            - `tokens`: an int, the number of tokens used, e.g. `1000`
            - `price`: a float, the price of one token; it has the **default value** `0.002`
              (used when the caller leaves it out)

            **What comes out**
            - `tokens` multiplied by `price` (a float)

            **Rules**
            - Calling with only `tokens` uses the price `0.002`.
            - `price` can be passed by position or by name (`price=...`).

            **Examples**
            ```python
            request_cost(1000)               # returns 2.0
            request_cost(1000, 0.01)         # returns 10.0
            request_cost(500, price=0.004)   # returns 2.0
            ```

            With no tokens, `request_cost(0)` returns `0.0`.
        ''',
        "starter": r'''
            def request_cost(tokens):
                ...
        ''',
        "tests": r'''
            from solution import request_cost

            def test_default_price_is_used_when_omitted():
                got = request_cost(1000)
                assert got == 2.0, f"got {got!r}"

            def test_price_passed_by_position():
                got = request_cost(1000, 0.01)
                assert got == 10.0, f"got {got!r}"

            def test_price_passed_by_name():
                got = request_cost(500, price=0.004)
                assert got == 2.0, f"got {got!r}"
        ''',
        "solution": r'''
            def request_cost(tokens, price=0.002):
                return tokens * price
        ''',
        "hints": [
            "The definition needs to describe what happens when price is omitted.",
            "Allow both positional and named price arguments, with the stated default.",
            "Add the optional parameter after the required one, then give back the cost calculated using the received values.",
        ],
    },
    {
        "id": "functions-s5",
        "title": "Two answers at once",
        "difficulty": 0,
        "lesson": r'''
            ## Give back a pair of related answers

            A report needs both the first and last document name. Making two calls would repeat the same lookup work. You can group the answers and return that group in one call.

            ```python
            def endpoints(items):
                return items[0], items[-1]

            pair = endpoints(["Guide", "FAQ", "Notes"])
            print(pair)
            # ('Guide', 'Notes')
            ```

            The comma groups the two values into a tuple, which you met in the variables chapter. The function still returns one object, but that object holds two ordered answers. The order you choose becomes part of the function's promise to its callers.

            ```predict
            def endpoints(items):
                return items[0], items[-1]

            start, finish = endpoints([8, 3, 5])
            print(finish)
            ---
            Unpacking assigns the first returned item to start and the second to finish, so finish is 5.
            ```

            You can keep the tuple whole or unpack it into two names. For numeric summaries, `min` finds the smallest number and `max` the largest. If your input contains words but you need sizes, first think about the numeric measurements you will compare, rather than comparing the words themselves.

            ```python
            sizes = [6, 2, 9]
            print(min(sizes), max(sizes))
            # 2 9
            ```

            ```quiz
            What does changing the order of the returned pair change?
            - [x] Which answer the caller receives first. :: Tuples preserve positions, so callers depend on that order.
            - [ ] Nothing; Python sorts tuples automatically. :: Creating a tuple never sorts its values.
            ```

            **Watch out:** unpacking two values into three names raises `ValueError`. Match the names to the shape the function promises.

            Return related answers together, in an order the caller can rely on.
        ''',
        "prompt": r'''
            Before sending text to a model you often want quick stats about it. Find the
            shortest and longest word lengths in one call.

            **Your job:** write `shortest_longest(words)`

            **What goes in**
            - `words`: a list of strings, never empty, e.g. `["hi", "hello", "hey"]`

            **What comes out**
            - **two values** separated by a comma (a tuple): the length of the
              shortest word, then the length of the longest word

            **Rules**
            - Order matters: shortest length first, longest length second.
            - With a single word, both values are that word's length.

            **Examples**
            ```python
            shortest_longest(["hi", "hello", "hey"])   # returns (2, 5)
            shortest_longest(["abcdef", "a"])          # returns (1, 6)
            shortest_longest(["token"])                # returns (5, 5)

            low, high = shortest_longest(["hi", "hello"])   # low is 2, high is 5 (unpacking)
            ```
        ''',
        "starter": r'''
            def shortest_longest(words):
                ...
        ''',
        "tests": r'''
            from solution import shortest_longest

            def test_three_words_give_two_and_five():
                got = shortest_longest(["hi", "hello", "hey"])
                assert tuple(got) == (2, 5), f"got {got!r}"

            def test_single_word_gives_same_length_twice():
                got = shortest_longest(["token"])
                assert tuple(got) == (5, 5), f"got {got!r}"

            def test_order_is_shortest_then_longest():
                got = shortest_longest(["abcdef", "a"])
                assert tuple(got) == (1, 6), f"got {got!r}"
        ''',
        "solution": r'''
            def shortest_longest(words):
                lengths = []
                for word in words:
                    lengths.append(len(word))
                return min(lengths), max(lengths)
        ''',
        "hints": [
            "The answers are numeric lengths, not the words themselves.",
            "Measure each word, then find the smallest and largest measurements.",
            "Collect the lengths, select their two endpoints, and return them together with the shortest first.",
        ],
    },
    {
        "id": "functions-s6",
        "title": "Inside stays inside",
        "difficulty": 0,
        "lesson": r'''
            ## Keep a function's working names separate

            Two helpers both use a name like `result`. You would not want running one helper to overwrite every other result in the program. Python gives each function call its own working names.

            ```python
            status = "waiting"

            def check():
                status = "ready"
                return status

            print(check())
            # ready
            print(status)
            # waiting
            ```

            The assignment inside `check` creates a name for that call. It does not reassign the name outside. Where a name can be used is its **scope**; a name belonging to a function call has **local scope**. Identical spelling does not mean two names refer to the same variable.

            ```predict
            size = 12

            def measure():
                size = 4
                return size + 1

            measured = measure()
            print(measured, size)
            ---
            The local size supplies 4 to the calculation. The outside size is untouched and remains 12.
            ```

            Returning a local value lets the caller keep that value under its own name. You are passing a result out, not making the function's local names available everywhere. This separation lets you understand a small function without reading all the names used by the rest of the program.

            ```quiz
            A helper creates `temporary` only inside its body. Can unrelated code use that name afterwards?
            - [x] No; the helper should return any value the caller needs. :: Local names belong to the function call.
            - [ ] Yes; calling a function exposes all its names. :: Calls do not add their local names to the surrounding program.
            ```

            **Watch out:** using an unavailable local name outside its function raises `NameError`. Save the function's return value instead.

            Pass values in through arguments and values out through return.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            count = 10

            def reset():
                count = 0
                return count

            print(reset())
            print(count)
        ''',
        "solution": r'''
            0
            10
        ''',
        "explanation": r'''
            The assignment inside reset belongs to that function call. Its return value supplies the first printed number. The outside count was assigned before the function ran and was never reassigned afterwards, so the final print still uses its original value.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Separate names inside the call from names outside it.",
            "An assignment in the helper creates a local value without reassigning the outside name.",
            "Follow the returned local value for the first print, then read the untouched outside value for the next print.",
        ],
    },
    {
        "id": "functions-1",
        "title": "Build a message",
        "hints": [
            "Review defaults, type hints, and where a docstring belongs.",
            "Describe both input types and the returned dictionary, while making the speaker optional.",
            "Update the definition, put a description first in the body, and give back the two required fields using the supplied values.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Tell readers what a helper expects

            A teammate finds your helper and wants to know what to pass and what comes back. Good names help, but a short description and notes about types make the promise clearer without reading the implementation.

            ```python
            def heading(text: str, level: int = 1) -> str:
                """Build a heading label for a report."""
                return f"{level}: {text}"

            print(heading("Overview"))
            # 1: Overview
            print(heading.__doc__)
            # Build a heading label for a report.
            ```

            The annotations after parameter names describe expected types. The arrow describes the returned type. These are **type hints**: information for readers and checking tools. The default still follows the type note, so the definition can document both the expected kind of value and the usual value.

            The first string inside the body describes the function. It is a **docstring**, and Python keeps it in the function's `__doc__` attribute, the stored information accessed with that dotted name.

            ```match
            `text: str` :: input is expected to be text
            `-> str` :: return value is expected to be text
            `__doc__` :: stored description of the function
            ```

            Hints do not enforce types while Python runs. If an operation accepts a different type, the annotation does not block it. Validation requires real checks in the body. Likewise, a docstring describes behavior but does not implement it.

            ```quiz
            Where does Python recognize a function's docstring?
            - [x] As the first statement in its body. :: Python saves that leading string as the description.
            - [ ] Anywhere after the return statement. :: That text is neither reached nor stored as the function's docstring.
            ```

            **Watch out:** a helpful comment is not a docstring. Use a leading string when the function must carry its description.

            Document the input, output, and purpose alongside the function definition.
        ''',
        "prompt": r'''
            Chat APIs take a list of message dicts. Write a helper that builds one message.

            **Your job:** write `make_message(content, role="user")`

            **What goes in**
            - `content`: a string, the message text, e.g. `"hi"`
            - `role`: a string, who is speaking, e.g. `"system"`; **default value** `"user"`

            **What comes out**
            - a dict with exactly two keys, like `{"role": "user", "content": "hi"}`

            **Rules**
            - If `role` is left out, it is `"user"`.
            - `role` can be passed by position or by name (`role="assistant"`).
            - Add **type hints** to both parameters AND the return value
              (e.g. `content: str`, and `-> dict` after the parentheses).
            - Add a **docstring**: a string on the first line of the body describing the function.

            **Examples**
            ```python
            make_message("hi")                    # returns {"role": "user", "content": "hi"}
            make_message("be terse", "system")    # returns {"role": "system", "content": "be terse"}
            make_message("ok", role="assistant")  # returns {"role": "assistant", "content": "ok"}
            ```

            An empty message is kept: `make_message("")` returns `{"role": "user", "content": ""}`.
        ''',
        "starter": r'''
            def make_message(content, role):
                ...
        ''',
        "tests": r'''
            from solution import make_message
            import inspect

            def test_role_defaults_to_user():
                got = make_message("hi")
                assert got == {"role": "user", "content": "hi"}, f"got {got!r}"

            def test_role_can_be_passed_by_position_or_name():
                assert make_message("be terse", "system") == {"role": "system", "content": "be terse"}
                assert make_message("ok", role="assistant") == {"role": "assistant", "content": "ok"}

            def test_parameters_and_return_have_type_hints():
                sig = inspect.signature(make_message)
                for name, p in sig.parameters.items():
                    assert p.annotation is not inspect.Parameter.empty, f"parameter {name!r} has no type hint"
                assert sig.return_annotation is not inspect.Signature.empty, "add a return type hint"

            def test_function_has_a_docstring():
                assert (make_message.__doc__ or "").strip(), "add a docstring"
        ''',
        "solution": r'''
            def make_message(content: str, role: str = "user") -> dict:
                """Return a chat message dict with the given role and content."""
                return {"role": role, "content": content}
        ''',
    },
    {
        "id": "functions-2",
        "title": "Token stats",
        "hints": [
            "Decide the empty-list answer before selecting extrema or dividing.",
            "For nonempty data, minimum, maximum, and mean are separate calculations.",
            "Return the specified empty tuple immediately when needed; otherwise calculate all three summaries and return them in the promised order.",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Handle an empty input before calculating

            A usage dashboard must still show something before any requests arrive. An average calculation that works for every nonempty list can fail when the list is empty. Decide what that case should mean before doing the ordinary work.

            ```python
            def average(values):
                if not values:
                    return 0.0
                return sum(values) / len(values)

            print(average([3, 9]))
            # 6.0
            print(average([]))
            # 0.0
            ```

            An empty list is false in a condition, so `not values` selects the special case. Returning there ends the call immediately. The final calculation therefore only runs when there are values. This arrangement is an **early return**, also called a **guard clause**: it handles a case before the main calculation.

            ```predict
            def average(values):
                if not values:
                    return 0.0
                return sum(values) / len(values)

            print(average([5]))
            ---
            The list is nonempty. Its sum and length are 5 and 1, and division gives the float 5.0.
            ```

            `sum` adds the numbers, `len` counts them, and `/` divides to produce a float. For a broader summary, `min` and `max` supply the endpoints. Empty inputs need attention for those operations too: there is no smallest or largest item to select.

            ```quiz
            Why put the empty-input check before the average calculation?
            - [x] Division by a zero item count would otherwise fail. :: The guard prevents the invalid calculation from running.
            - [ ] Empty lists automatically have an average of zero. :: Python does not choose a statistical convention for your application.
            ```

            **Watch out:** `min([])` raises `ValueError`, and dividing by zero raises `ZeroDivisionError`. Decide the empty result first.

            Handle exceptional input shapes before calculations that assume ordinary data.
        ''',
        "prompt": r'''
            You log how many tokens each request used and want a quick summary.

            **Your job:** write `token_stats(counts)`

            **What goes in**
            - `counts`: a list of ints (token counts), e.g. `[10, 30, 20]`; may be empty

            **What comes out**
            - **three values** (a tuple): the minimum, the maximum, and the
              average of the counts

            **Rules**
            - Order: minimum, maximum, average.
            - The average is always a `float` (e.g. `20.0`, not `20`).
            - If the list is empty, return `(0, 0, 0.0)`.

            **Examples**
            ```python
            token_stats([10, 30, 20])   # returns (10, 30, 20.0)
            token_stats([1, 2])         # returns (1, 2, 1.5)
            token_stats([7])            # returns (7, 7, 7.0)
            token_stats([])             # returns (0, 0, 0.0)
            ```
        ''',
        "starter": r'''
            def token_stats(counts):
                ...
        ''',
        "tests": r'''
            from solution import token_stats

            def test_returns_min_max_and_average():
                got = token_stats([10, 30, 20])
                assert tuple(got) == (10, 30, 20.0), f"got {got!r}"

            def test_average_is_a_float():
                lo, hi, avg = token_stats([1, 2])
                assert avg == 1.5 and isinstance(avg, float), f"avg was {avg!r}"

            def test_single_count():
                assert tuple(token_stats([7])) == (7, 7, 7.0)

            def test_empty_list_returns_zeros():
                got = token_stats([])
                assert tuple(got) == (0, 0, 0.0), f"got {got!r}"
        ''',
        "solution": r'''
            def token_stats(counts):
                if not counts:
                    return 0, 0, 0.0
                return min(counts), max(counts), sum(counts) / len(counts)
        ''',
    },
    {
        "id": "functions-7",
        "title": "Reuse your helper",
        "difficulty": 1,
        "lesson": r'''
            ## Build one helper from another

            A report already has a helper that calculates a document's size. Another helper needs that same answer to decide whether the document is large. Calling the first helper keeps the calculation in one place, so a later correction benefits both uses.

            ```python
            def combined_size(parts):
                total_size = 0
                for part in parts:
                    total_size += len(part)
                return total_size

            def fits(parts, limit):
                return combined_size(parts) <= limit

            print(fits(["red", "blue"], 8))
            # True
            ```

            When `fits` reaches the call, Python runs `combined_size` and waits for its return value. That value then participates in the comparison. Building a larger operation from smaller ones is called **composition**; using an existing helper again is **reuse**.

            ```order
            def plus_three(number):
                return number + 3
            answer = plus_three(4)
            print(answer)
            ---
            The definition must run before the call. The call supplies the value that the final line prints.
            ```

            A helper can return a number that the caller uses several times. Save that answer once when it does not change during a loop. Recalculating the same answer for every item makes the work harder to follow and often repeats unnecessary effort.

            ```quiz
            Why call an existing helper instead of copying its calculation?
            - [x] A correction to the helper benefits every caller. :: There is one implementation to maintain.
            - [ ] Calling a helper always prints its result. :: Display and return remain separate; calling does not imply printing.
            ```

            **Watch out:** a function name without parentheses refers to the function itself. Add a call when you need its computed result, or a comparison may fail with `TypeError`.

            Give each helper one clear job, then connect them through return values.
        ''',
        "prompt": r'''
            A chat app wants to know which messages are longer than average. Write two small
            functions, where the second one **reuses** the first.

            **Your job:** write `average_length(texts)`

            **What goes in**
            - `texts`: a list of strings, never empty, e.g. `["hi", "hello"]`

            **What comes out**
            - the average number of characters per string, as a float
              (e.g. `3.5`)

            **Your job:** write `longer_than_average(texts)`

            **What goes in**
            - `texts`: a list of strings, never empty

            **What comes out**
            - a new list with the strings whose length is **strictly greater**
              than the average length, in their original order

            **Rules**
            - `longer_than_average` must call `average_length` (a check reads your code for this).
            - If every string has the same length, `longer_than_average` returns `[]`.
            - Don't change the list you were given.

            **Examples**
            ```python
            average_length(["hi", "hello"])             # returns 3.5
            average_length(["abc"])                     # returns 3.0
            longer_than_average(["hi", "hello", "hey"]) # returns ["hello"]   (average is 3.33...)
            longer_than_average(["ab", "cd"])           # returns []
            ```
        ''',
        "starter": r'''
            def average_length(texts):
                ...


            def longer_than_average(texts):
                ...
        ''',
        "tests": r'''
            from solution import average_length, longer_than_average

            def test_average_length_of_two_strings():
                got = average_length(["hi", "hello"])
                assert got == 3.5, f"got {got!r}"

            def test_average_length_of_one_string_is_a_float():
                got = average_length(["abc"])
                assert got == 3.0 and isinstance(got, float), f"got {got!r}"

            def test_keeps_only_strictly_longer_strings_in_order():
                got = longer_than_average(["hello", "hi", "hey", "greetings"])
                assert got == ["hello", "greetings"], f"got {got!r}"

            def test_same_lengths_give_empty_list():
                got = longer_than_average(["ab", "cd"])
                assert got == [], f"got {got!r}"

            def test_input_list_is_not_changed():
                texts = ["hi", "hello", "hey"]
                longer_than_average(texts)
                assert texts == ["hi", "hello", "hey"], f"list became {texts!r}"

            def test_longer_than_average_calls_average_length():
                import ast
                tree = ast.parse(source())
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "longer_than_average":
                        names = [n.func.id for n in ast.walk(node)
                                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
                        assert "average_length" in names, "longer_than_average should call average_length"
                        return
                assert False, "longer_than_average not found"
        ''',
        "solution": r'''
            def average_length(texts):
                total = 0
                for text in texts:
                    total += len(text)
                return total / len(texts)


            def longer_than_average(texts):
                average = average_length(texts)
                result = []
                for text in texts:
                    if len(text) > average:
                        result.append(text)
                return result
        ''',
        "hints": [
            "Finish and check the average helper before the filtering helper.",
            "Call the average helper once, then compare each original string's length with that result.",
            "Calculate the average, create a new list, add only strings strictly above it in input order, and give the list back.",
        ],
    },
    {
        "id": "functions-8",
        "title": "Any number of counts",
        "difficulty": 1,
        "lesson": r'''
            ## Accept a changing number of inputs

            One report contains two documents and another contains seven. You want one helper that accepts either set of names without requiring a different definition for every count. Python can gather separate incoming values for you.

            ```python
            def collect(*titles):
                return titles

            print(collect("Guide", "Notes"))
            # ('Guide', 'Notes')
            print(collect())
            # ()
            ```

            The star in the definition gathers positional arguments into a tuple. Inside the body, `titles` is an ordinary tuple, so you can loop over it or count its items. With no arguments, it is empty. The conventional name `*args` means the same thing; the star supplies the behavior, not the spelling of the name.

            ```predict
            def how_many(*items):
                return len(items)

            print(how_many("a", "b", "c"))
            print(how_many())
            ---
            Three separate arguments produce a tuple of length three. An omitted collection of arguments produces an empty tuple.
            ```

            Keyword arguments can be gathered too. A parameter with two stars collects extra named arguments into a dictionary. You will meet this as `**kwargs` in documentation, short for keyword arguments. A function can therefore accept both an unknown number of unnamed values and additional named choices.

            ```python
            def options(**settings):
                return settings

            print(options(limit=3))
            # {'limit': 3}
            ```

            ```match
            `*items` in a definition :: collects positional arguments into a tuple
            `**settings` in a definition :: collects keyword arguments into a dictionary
            `items` inside the body :: the collected tuple itself
            ```

            **Watch out:** receiving one list is different from receiving several separate arguments. Match the definition to the required calling style.

            Use a starred parameter when the number of incoming values can vary.
        ''',
        "prompt": r'''
            A conversation has several messages and you want the total token count, however
            many messages there are. Accept the counts as separate arguments.

            **Your job:** write `total_tokens(*counts)`

            **What goes in**
            - `*counts`: any number of ints passed by position (collected into a tuple),
              e.g. `total_tokens(10, 20, 5)`

            **What comes out**
            - the sum of all the counts, as an int

            **Rules**
            - Called with no arguments, return `0`.
            - The function must accept any number of arguments (use `*` in the `def` line).

            **Examples**
            ```python
            total_tokens(10, 20, 5)   # returns 35
            total_tokens(7)           # returns 7
            total_tokens()            # returns 0
            ```
        ''',
        "research": {
            "note": "Read the Python tutorial's section on arbitrary argument lists to see how a starred parameter collects arguments into a tuple, then come back.",
            "links": [
                {"title": "Arbitrary Argument Lists - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists"},
            ],
        },
        "starter": r'''
            def total_tokens(counts):
                ...
        ''',
        "tests": r'''
            from solution import total_tokens

            def test_three_counts_are_added():
                got = total_tokens(10, 20, 5)
                assert got == 35, f"got {got!r}"

            def test_a_single_count():
                got = total_tokens(7)
                assert got == 7, f"got {got!r}"

            def test_no_arguments_gives_zero():
                got = total_tokens()
                assert got == 0, f"got {got!r}"

            def test_many_counts():
                got = total_tokens(*range(1, 11))
                assert got == 55, f"got {got!r}"
        ''',
        "solution": r'''
            def total_tokens(*counts):
                total = 0
                for count in counts:
                    total += count
                return total
        ''',
        "hints": [
            "Separate arguments can be collected by a starred parameter.",
            "Add the values in the resulting tuple, allowing it to be empty.",
            "Adjust the definition to accept any number of counts, begin the total at zero, include every count, and return the total.",
        ],
    },
    {
        "id": "functions-3",
        "title": "Request builder",
        "hints": [
            "The definition separates required input, extra positional input, and named options.",
            "Collect message text and extra settings separately, then create the requested output shape.",
            "Build fresh message dictionaries and a fresh list for each call, add model and temperature, copy extra named settings, and return the request.",
        ],
        "difficulty": 2,
        "placement": True,
        "research": {
            "note": "Read about keyword arguments, *args/**kwargs and keyword-only parameters in the Python tutorial, then come back.",
            "links": [
                {"title": "Keyword Arguments - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/controlflow.html#keyword-arguments"},
                {"title": "Special parameters - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/controlflow.html#special-parameters"},
            ],
        },
        "prompt": r'''
            LLM client libraries let you pass any number of messages and extra options.
            Build the request dict that would be sent to the API.

            **Your job:** write `build_request(model, *messages, temperature=1.0, **extra)`

            **What goes in**
            - `model`: a string, required, e.g. `"gpt-4o"`
            - `*messages`: any number of message **strings** passed by position after `model`
              (`*messages` collects them into a tuple), e.g. `"hi", "how are you?"`
            - `temperature`: a float, default `1.0`, **keyword-only** (it comes after
              `*messages`, so it can only be passed as `temperature=...`)
            - `**extra`: any other keyword arguments (collected into a dict), e.g. `max_tokens=50`

            **What comes out**
            - a dict with the keys `"model"`, `"messages"`, `"temperature"`, plus
              one key per extra keyword argument

            **Rules**
            - Each message string becomes `{"role": "user", "content": <the string>}`, in the
              order given, inside the `"messages"` list.
            - Every positional argument after `model` is a message (never the temperature):
              `build_request("m", "a", "b")` has 2 messages and temperature `1.0`.
            - Extra keyword arguments are copied into the dict as-is (same key, same value).
            - If no messages are given, `"messages"` is an empty list `[]`.
            - Each call returns a new dict with its own new list (nothing is shared between calls).

            **Examples**
            ```python
            build_request("gpt-4o", "hi", "how are you?", max_tokens=50)
            # returns {"model": "gpt-4o",
            #          "messages": [{"role": "user", "content": "hi"},
            #                       {"role": "user", "content": "how are you?"}],
            #          "temperature": 1.0,
            #          "max_tokens": 50}

            build_request("m", "x", temperature=0.2, stream=True)
            # returns {"model": "m", "messages": [{"role": "user", "content": "x"}],
            #          "temperature": 0.2, "stream": True}

            build_request("m", temperature=0.5)
            # returns {"model": "m", "messages": [], "temperature": 0.5}
            ```
        ''',
        "starter": r'''
            def build_request(model, messages, temperature=1.0):
                ...
        ''',
        "tests": r'''
            from solution import build_request

            def test_messages_become_user_dicts_and_extras_are_copied():
                got = build_request("gpt-4o", "hi", "how are you?", max_tokens=50)
                want = {"model": "gpt-4o",
                        "messages": [{"role": "user", "content": "hi"},
                                     {"role": "user", "content": "how are you?"}],
                        "temperature": 1.0, "max_tokens": 50}
                assert got == want, f"got {got!r}"

            def test_custom_temperature_and_several_extras():
                got = build_request("m", "x", temperature=0.2, top_p=0.9, stream=True)
                assert got["temperature"] == 0.2
                assert got["top_p"] == 0.9 and got["stream"] is True, f"got {got!r}"

            def test_positional_args_are_messages_not_temperature():
                got = build_request("m", "a", "b")
                assert len(got["messages"]) == 2, "a positional arg must become a message"
                assert got["temperature"] == 1.0

            def test_no_messages_gives_empty_list():
                got = build_request("m", temperature=0.5)
                assert got == {"model": "m", "messages": [], "temperature": 0.5}, f"got {got!r}"

            def test_calls_do_not_share_messages():
                a = build_request("m", "one")
                b = build_request("m", "two")
                assert len(a["messages"]) == 1 and len(b["messages"]) == 1
        ''',
        "solution": r'''
            def build_request(model, *messages, temperature=1.0, **extra):
                message_list = []
                for m in messages:
                    message_list.append({"role": "user", "content": m})
                request = {"model": model, "messages": message_list, "temperature": temperature}
                for key, value in extra.items():
                    request[key] = value
                return request
        ''',
    },
    {
        "id": "functions-4",
        "title": "Mutable default trap",
        "hints": [
            "Default objects are created when the definition runs, not anew for each call.",
            "Represent an omitted history with a value that cannot be confused with an explicitly supplied empty list.",
            "Use a missing-value marker as the default, create a list only for that marker, then append to and return the chosen history.",
        ],
        "difficulty": 2,
        "prompt": r'''
            This helper appends a message to a conversation history and returns it. When
            called without a `history`, each call should start a **fresh** conversation,
            but right now conversations leak into each other (the *mutable default* trap).
            Fix it.

            **Your job:** write `add_message(text, history=...)`

            **What goes in**
            - `text`: a string, the message to add, e.g. `"hello"`
            - `history`: optional list of strings, the conversation so far, e.g. `["sys"]`;
              it must still have a default value so it can be left out

            **What comes out**
            - the history list, with `text` appended at the end

            **Rules**
            - Without `history`, every call starts from a brand-new empty list: two calls
              must return two **different** list objects.
            - With `history`, append to **that same list** (modify it) and return that same
              list object, not a copy.
            - This also applies when the caller passes an **empty** list `[]`: use it,
              don't replace it with a new one.

            **Examples**
            ```python
            add_message("hello")    # returns ["hello"]
            add_message("bye")      # returns ["bye"]   (not ["hello", "bye"])

            h = ["sys"]
            add_message("hi", h)    # returns h, and h is now ["sys", "hi"]

            h = []
            add_message("hi", h)    # returns h, and h is now ["hi"]
            ```
        ''',
        "starter": r'''
            def add_message(text, history=[]):
                history.append(text)
                return history
        ''',
        "tests": r'''
            from solution import add_message

            def test_fresh_history_each_call():
                a = add_message("hello")
                b = add_message("bye")
                assert a == ["hello"], f"first call returned {a!r}"
                assert b == ["bye"], f"second call returned {b!r} - state leaked between calls"

            def test_each_call_without_history_returns_a_new_list():
                assert add_message("x") is not add_message("y")

            def test_appends_to_and_returns_callers_list():
                h = ["sys"]
                got = add_message("hi", h)
                assert got is h, "should return the list that was passed in"
                assert h == ["sys", "hi"], f"caller list is {h!r}"

            def test_empty_list_passed_in_is_used():
                h = []
                got = add_message("hi", h)
                assert got is h and h == ["hi"], "an empty list passed in must still be used"
        ''',
        "solution": r'''
            def add_message(text, history=None):
                if history is None:
                    history = []
                history.append(text)
                return history
        ''',
    },
    {
        "id": "functions-5",
        "title": "Apply a pipeline",
        "hints": [
            "A function can return another function that remembers values from the enclosing call.",
            "For composition, pass each result onward. For counting, keep shared call records for the wrapper and the count reader.",
            "Define the returned helpers inside their factories; forward both argument kinds, record each wrapper call, and keep each factory call's state separate.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Text preprocessing is often a pipeline of small functions, and you often want to
            count how many times a function (like an API call) was used. Write two helpers
            that take functions and return new functions.

            **Your job:** write `compose(*funcs)`

            **What goes in**
            - `*funcs`: any number of one-argument functions (possibly none)

            **What comes out**
            - a **new function** that takes one value and passes it through each
              function in `funcs`, **left to right** (the output of one is the input of the next)

            **Your job:** write `count_calls(func)`

            **What goes in**
            - `func`: any function, e.g. the built-in `max`

            **What comes out**
            - **two functions** as a tuple `(wrapper, count)`:
              - `wrapper` behaves exactly like `func`: it accepts the same positional AND
                keyword arguments and returns the same value
              - `count()` takes no arguments and returns how many times `wrapper` has been called

            **Rules**
            - `compose`: order matters, the first function in `funcs` runs first.
            - `compose()` with no functions returns a function that gives back its input
              unchanged (the very same object).
            - `count_calls`: `count()` is `0` before any call.
            - Each call to `count_calls` has its own independent counter.

            **Examples**
            ```python
            def add_one(x):
                return x + 1

            def double(x):
                return x * 2

            compose(add_one, double)(3)            # returns 8   (3 + 1, then * 2)
            compose(double, add_one)(3)            # returns 7   (3 * 2, then + 1)
            compose(add_one, add_one, double)(0)   # returns 4
            compose()(5)                           # returns 5

            wrapped_max, count = count_calls(max)
            count()                        # returns 0
            wrapped_max(1, 5)              # returns 5
            wrapped_max([3, 2])            # returns 3
            wrapped_max([1, -9], key=abs)  # returns -9
            count()                        # returns 3
            ```
        ''',
        "starter": r'''
            def compose(*funcs):
                ...


            def count_calls(func):
                ...
        ''',
        "tests": r'''
            from solution import compose, count_calls

            def add_one(x):
                return x + 1

            def double(x):
                return x * 2

            def shout(text):
                return f"{text}!"

            def test_compose_applies_left_to_right():
                assert compose(add_one, double)(3) == 8, f"got {compose(add_one, double)(3)!r}"
                assert compose(double, add_one)(3) == 7, f"got {compose(double, add_one)(3)!r} (order matters)"

            def test_compose_three_functions():
                got = compose(add_one, add_one, double)(0)
                assert got == 4, f"got {got!r}"

            def test_compose_with_no_functions_returns_input_unchanged():
                f = compose()
                obj = [1]
                assert f(obj) is obj

            def test_wrapper_passes_positional_and_keyword_args_and_counts():
                wrapped, count = count_calls(max)
                assert wrapped(1, 5) == 5
                assert wrapped([3, 2]) == 3
                assert wrapped([1, 9], key=abs) == 9
                assert count() == 3, f"count() was {count()!r}"

            def test_each_count_calls_has_its_own_counter():
                a, count_a = count_calls(shout)
                b, count_b = count_calls(shout)
                assert a("x") == "x!"
                a("y"); b("z")
                assert count_a() == 2 and count_b() == 1, f"counts were {count_a()} and {count_b()}"

            def test_count_starts_at_zero():
                wrapped, count = count_calls(abs)
                assert count() == 0
        ''',
        "solution": r'''
            def compose(*funcs):
                def pipeline(value):
                    for func in funcs:
                        value = func(value)
                    return value
                return pipeline


            def count_calls(func):
                calls = []

                def wrapper(*args, **kwargs):
                    calls.append(1)
                    return func(*args, **kwargs)

                def count():
                    return len(calls)

                return wrapper, count
        ''',
    },
    {
        "id": "functions-6",
        "title": "Rate limiter closure",
        "hints": [
            "The returned function needs to remember previously allowed timestamps.",
            "Discard expired requests before comparing the remaining count with the limit.",
            "Create private state for each limiter, remove timestamps at or before the boundary, record only accepted requests, and return the decision.",
        ],
        "difficulty": 3,
        "prompt": r'''
            LLM APIs limit how many requests you may send per minute. Build a client-side
            rate limiter that stores past requests (this is a *closure*).

            **Your job:** write `make_limiter(max_requests)`

            **What goes in**
            - `max_requests`: an int, how many requests are allowed per 60 seconds, e.g. `2`

            **What comes out**
            - a function `allow(now)`:
              - `now`: a timestamp in seconds (int or float), never decreasing between calls
              - returns `True` (the request is allowed) or `False` (it is rejected)

            **Rules**
            - `allow(now)` returns `True` if fewer than `max_requests` requests were
              **allowed** in the 60-second window `(now - 60, now]`, and records this request.
            - Otherwise it returns `False` and records nothing: a rejected request never
              counts against later calls.
            - The window excludes `now - 60` itself: a request exactly 60 seconds old no
              longer counts.
            - Each limiter returned by `make_limiter` has its own independent state.
            - Don't use `global` or classes: keep the state inside `make_limiter` (a check
              reads your code for this).

            **Examples**
            ```python
            allow = make_limiter(2)
            allow(0)     # returns True
            allow(10)    # returns True
            allow(20)    # returns False  (2 already allowed in the window)
            allow(60)    # returns True   (the request at 0 is now outside (0, 60])
            allow(61)    # returns False  (10 and 60 are in the window)

            one = make_limiter(1)
            one(100)     # returns True
            one(159.9)   # returns False
            one(160)     # returns True   (exactly 60 seconds later)
            ```
        ''',
        "starter": r'''
            def make_limiter(max_requests):
                ...
        ''',
        "tests": r'''
            from solution import make_limiter

            def test_example_sequence_with_limit_two():
                allow = make_limiter(2)
                got = [allow(t) for t in (0, 10, 20, 60, 61)]
                assert got == [True, True, False, True, False], f"got {got!r}"

            def test_rejected_requests_do_not_count():
                allow = make_limiter(1)
                assert allow(0) is True
                assert allow(30) is False
                assert allow(60) is True, "a rejected request must not occupy the window"

            def test_request_exactly_60_seconds_old_no_longer_counts():
                allow = make_limiter(1)
                assert allow(100) is True
                assert allow(159.9) is False
                assert allow(160) is True, "request exactly 60s later should be allowed"

            def test_limiters_are_independent():
                a = make_limiter(1)
                b = make_limiter(1)
                assert a(0) is True
                assert b(0) is True, "a second limiter must have its own state"
                assert a(1) is False

            def test_twenty_requests_every_ten_seconds():
                allow = make_limiter(3)
                got = [allow(t) for t in range(0, 200, 10)]
                assert got.count(True) == 11, f"allowed {got.count(True)} of 20"

            def test_no_global_or_class_used():
                import ast
                tree = ast.parse(source())
                assert not any(isinstance(n, (ast.Global, ast.ClassDef)) for n in ast.walk(tree)), \
                    "keep state in the closure (no global, no class)"
        ''',
        "solution": r'''
            def make_limiter(max_requests):
                allowed = []

                def allow(now):
                    while allowed and allowed[0] <= now - 60:
                        allowed.pop(0)
                    if len(allowed) < max_requests:
                        allowed.append(now)
                        return True
                    return False

                return allow
        ''',
    },
]
