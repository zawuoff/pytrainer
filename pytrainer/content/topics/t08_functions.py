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

LESSON = r'''
## Chapter notes: Functions

**Define and call**
```python
def greet(name):              # name is a *parameter*
    return f"Hello, {name}!"  # the body is indented

print(greet("Ada"))           # "Ada" is an *argument*
```

**Terms**
- *parameter*: the name in the `def` line. *argument*: the value you pass in the call.
- *return value*: what `return` hands back. No `return` means the function returns `None`.
- `return` ends the function immediately; code after it never runs.
- *default value*: `def f(x, role="user")` makes `role` optional.
- *keyword argument*: naming the parameter in the call, `f("hi", role="system")`.
- Several return values: `return low, high` gives a tuple; unpack with `a, b = f(...)`.
- *scope*: variables made inside a function only exist inside it.
- *type hints*: `def cost(tokens: int) -> float:` (documentation, not enforced).
- *docstring*: a string on the first line of the body; read it with `f.__doc__`.
- `*args` collects extra positional arguments into a tuple; `**kwargs` collects
  extra keyword arguments into a dict. Parameters after `*args` are keyword-only.
- Functions are values: pass them around, store them, return them. An inner
  function that remembers the outer function's variables is a *closure*.

**Gotchas**
- `print` is not `return`: tests check the returned value.
- `result = greet` stores the function itself; call it with brackets: `greet("Ada")`.
- Never use a list/dict as a default (`items=[]`): it is shared by all calls.
  Use `items=None`, then `if items is None: items = []`.
- Handle the edge case (empty list...) first with an early `return`.
'''

EXERCISES = [
    {
        "id": "functions-s1",
        "title": "Return vs print",
        "difficulty": 0,
        "lesson": r'''
            ## A machine that hands something back

            Think of a function as a small machine. You drop something in, it does its job,
            and it **hands a result back out** of a slot. Every AI app is built from little
            machines like this: one builds a prompt, one counts tokens, one cleans a reply.

            ```python
            def add_bang(word):
                return word + "!"

            loud = add_bang("hi")
            print(loud)
            ```

            `return` pushes the result out of the slot, and the caller catches it in `loud`.

            `print` is different: it only **shows** text on the screen. The caller gets
            nothing back. A function that never runs `return` hands back a special value
            called `None` ("nothing here").

            ```python
            def show(word):
                print(word)

            got = show("hey")   # prints hey
            print(got)          # None
            ```

            The proper names: the thing handed back is the *return value*; using the machine
            is *calling* the function.

            **Watch out:** only lines that call `print` put text on the screen.
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
            `shout` **returns** `"hi!"`, and the outer `print` shows it. `whisper` prints
            `HEY...` itself but has no `return`, so it gives back `None` - which is what
            `result` holds and what the last line prints.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Follow the code top to bottom. Only lines that call print() produce output.",
            "shout gives back a value; whisper prints something itself but gives nothing back.",
            "Line 1: the returned value of shout. Line 2: what whisper prints. Line 3: what a function with no return gives back.",
        ],
    },
    {
        "id": "functions-s2",
        "title": "Fill in the greeting",
        "difficulty": 0,
        "lesson": r'''
            ## A recipe card with blanks

            A function definition is like a recipe card with a blank on it: "Bake a cake
            for ____". The blank gets filled in each time someone uses the recipe.

            ```python
            def welcome(city):
                return f"Welcome to {city}"

            print(welcome("Paris"))
            print(welcome("Tokyo"))
            ```

            Piece by piece:
            - `def` starts the definition, then the name, then brackets, then a colon.
            - `city` is the blank. Its proper name is a *parameter*.
            - The indented lines below are the *body*.
            - `"Paris"` is the value that fills the blank in one call. That is an *argument*.

            Inside the body the parameter is just a normal variable, so you can use it in
            an f-string, in maths, anywhere.

            **Watch out:** don't write a real value like `"Paris"` inside the body - then
            the function would ignore what the caller gave it.
        ''',
        "prompt": r'''
            A chat app greets each user by name. Complete the function by replacing the `___`.

            **Write:** `greet(name)`

            - `name`: a string, e.g. `"Ada"`
            - **Returns:** a string like `"Hello, Ada!"`

            **Rules**
            - Return the text (don't print it): `Hello`, a comma, one space, the name, then `!`.
            - It must work for any name, not just `"Ada"`.

            **Examples**
            ```python
            greet("Ada")    # returns "Hello, Ada!"
            greet("Bob")    # returns "Hello, Bob!"
            ```
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
            "The function receives the name in the parameter `name`. Build a string that uses it.",
            "An f-string lets you put a variable inside a string with curly braces.",
            "Replace ___ with an f-string: the text Hello, then a comma and space, then {name}, then an exclamation mark.",
        ],
    },
    {
        "id": "functions-s3",
        "title": "Fix: nothing comes back",
        "difficulty": 0,
        "lesson": r'''
            ## Showing is not giving

            Imagine asking a colleague to calculate a total. They shout the number across the
            room (that's `print`), but never write it on your sheet (that's `return`). You
            heard it, but you can't use it.

            ```python
            def triple_show(n):
                print(n * 3)

            def triple_give(n):
                return n * 3

            x = triple_show(2)   # screen shows 6, x is None
            y = triple_give(2)   # nothing shown, y is 6
            print(x, y + 1)
            ```

            The checks in this app always look at the *return value*, so a function that
            only prints looks like it "returned `None`".

            You'll hear people say a function "returns" a value or "gives back" a value.
            Same thing.

            **Watch out:** `return` also ends the function right away. Anything after it in
            the body never runs.
        ''',
        "prompt": r'''
            `double(n)` should give back twice `n`, but the checks receive `None`. Fix the bug.

            **Write:** `double(n)`

            - `n`: a number (int), e.g. `4` or `-3`
            - **Returns:** `n` times 2, as a number

            **Rules**
            - The value must be **returned** to the caller; printing it is not enough.
            - Negative numbers work the same way.

            **Examples**
            ```python
            double(4)     # returns 8
            double(-3)    # returns -6
            ```
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
            "Look at how the result leaves the function. Showing a value is not the same as giving it back.",
            "print only displays text. The caller needs the value handed back to them.",
            "Change the print(...) line into a return statement that returns n * 2.",
        ],
    },
    {
        "id": "functions-s4",
        "title": "Default price",
        "difficulty": 0,
        "lesson": r'''
            ## Defaults: the usual order

            At a coffee shop, "a coffee" means a medium coffee unless you say otherwise.
            Medium is the *default*. Functions can do the same.

            ```python
            def make_tea(sugar=1):
                return f"tea with {sugar} sugar"

            print(make_tea())          # uses the default
            print(make_tea(3))         # by position
            print(make_tea(sugar=0))   # by name
            ```

            Write the default in the `def` line as `name=value`. If the caller leaves that
            argument out, the default is used.

            The last call names the parameter: `sugar=0`. That is a *keyword argument*. It
            makes calls easier to read, especially with numbers: `cost(500, price=0.004)`
            says much more than `cost(500, 0.004)`.

            **Watch out:** parameters with defaults go after the ones without:
            `def f(tokens, price=0.002)` works, `def f(price=0.002, tokens)` is a SyntaxError.
        ''',
        "prompt": r'''
            An API bills per token. Compute the cost of a request.

            **Write:** `request_cost(tokens, price=0.002)`

            - `tokens`: an int, the number of tokens used, e.g. `1000`
            - `price`: a float, the price of one token; it has the **default value** `0.002`
              (used when the caller leaves it out)
            - **Returns:** `tokens` multiplied by `price` (a float)

            **Rules**
            - Calling with only `tokens` uses the price `0.002`.
            - `price` can be passed by position or by name (`price=...`).

            **Examples**
            ```python
            request_cost(1000)               # returns 2.0
            request_cost(1000, 0.01)         # returns 10.0
            request_cost(500, price=0.004)   # returns 2.0
            ```
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
            "You need a second parameter called price that has a default value.",
            "A default is written in the def line as name=value. Then the body just multiplies.",
            "Change the def line to take tokens and price=0.002, then return tokens multiplied by price.",
        ],
    },
    {
        "id": "functions-s5",
        "title": "Two answers at once",
        "difficulty": 0,
        "lesson": r'''
            ## Two answers in one bag

            Sometimes one question has two answers: "what are the cheapest and the most
            expensive models?". A function can hand back both at once. Python puts them in
            one bag, a *tuple*, and you can unpack the bag straight into two variables.

            ```python
            def first_last(items):
                return items[0], items[-1]

            pair = first_last(["a", "b", "c"])
            print(pair)

            start, end = first_last([10, 20, 30])
            print(start, end)
            ```

            `return a, b` returns the tuple `(a, b)`. Writing `x, y = ...` to split it again
            is called *unpacking*. The number of names on the left must match the number of
            values.

            Useful built-ins for this step: `min(numbers)` and `max(numbers)` give the
            smallest and largest number of a list.

            **Watch out:** order matters. `return high, low` hands them back the other way round.
        ''',
        "prompt": r'''
            Before sending text to a model you often want quick stats about it. Find the
            shortest and longest word lengths in one call.

            **Write:** `shortest_longest(words)`

            - `words`: a list of strings, never empty, e.g. `["hi", "hello", "hey"]`
            - **Returns:** **two values** separated by a comma (a tuple): the length of the
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
            "First get the length of every word, then find the smallest and largest of those numbers.",
            "Build a list of lengths with a loop, then use min() and max() on it. Return both separated by a comma.",
            "Make an empty list; loop over words and append len(word); finally return min of the list, max of the list.",
        ],
    },
    {
        "id": "functions-s6",
        "title": "Inside stays inside",
        "difficulty": 0,
        "lesson": r'''
            ## What happens in the function stays in the function

            A function is like a hotel room. You can make a mess inside it (create
            variables, change them), but when you check out, the room is cleaned. Nothing
            you made inside is visible in the lobby.

            ```python
            def make_total():
                total = 99
                return total

            print(make_total())
            # print(total) here would crash: NameError, total only lived inside
            ```

            If a variable inside the function has the **same name** as one outside, they are
            still two different boxes. Setting it inside does not touch the outside one.

            ```python
            level = "outside"

            def change():
                level = "inside"
                return level

            print(change(), level)
            ```

            The proper name is *scope*: a variable created inside a function has *local
            scope*. To get a value out, `return` it. To get a value in, pass it as an argument.
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
            Inside `reset`, `count = 0` creates a **new local variable** that only lives
            inside the function, so `reset()` returns `0`. The `count` outside the
            function is a different variable and still holds `10`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "There are two variables called count here: one outside the function and one created inside it.",
            "Assigning a variable inside a function creates a local one; it does not change the one outside.",
            "Line 1 is what reset() returns (its own local count). Line 2 is the outside count, which nobody changed.",
        ],
    },
    {
        "id": "functions-1",
        "title": "Build a message",
        "hints": [
            "You need a default parameter value, a dict as the return value, type hints and a docstring.",
            "Give role a default of \"user\" in the def line. Add `: str` after each parameter and `-> dict` before the colon. The first line of the body is a string describing the function.",
            "Write the def line with content: str and role: str = \"user\" and a -> dict return hint; add a triple-quoted docstring line; return a dict with keys \"role\" and \"content\".",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Labels on the jar

            A jar of homemade jam is much nicer with a label: what's inside and when it was
            made. Functions get labels too, so other people (and your editor) know how to use them.

            ```python
            def tokens_to_cost(tokens: int, price: float = 0.002) -> float:
                """Return the dollar cost of a request."""
                return tokens * price

            print(tokens_to_cost(1000))
            print(tokens_to_cost.__doc__)
            ```

            - `tokens: int` is a *type hint*: "I expect an int here". With a default, write
              the hint first: `price: float = 0.002`.
            - `-> float` before the colon hints at the type of the return value.
            - The string on the first line of the body is the *docstring*. Triple quotes let
              it span several lines. Python stores it in `function.__doc__`.

            Python does **not** check hints at runtime: they are documentation for humans
            and tools. Real AI codebases use them everywhere.

            **Watch out:** the docstring must be the very first line of the body, before any code.
        ''',
        "prompt": r'''
            Chat APIs take a list of message dicts. Write a helper that builds one message.

            **Write:** `make_message(content, role="user")`

            - `content`: a string, the message text, e.g. `"hi"`
            - `role`: a string, who is speaking, e.g. `"system"`; **default value** `"user"`
            - **Returns:** a dict with exactly two keys, like `{"role": "user", "content": "hi"}`

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
            "Python has built-ins for the smallest, largest and total of a list: min(), max(), sum(). len() gives the count.",
            "Handle the empty list first with an if, then return the three values separated by commas.",
            "If the list is empty return 0, 0, 0.0. Otherwise return min(counts), max(counts), and sum(counts) divided by len(counts) (the / operator always gives a float).",
        ],
        "difficulty": 1,
        "lesson": r'''
            ## Check the doorway first

            A bouncer checks your ID at the door, before you get inside. Functions often do
            the same: deal with the awkward case (an empty list, a missing value) first,
            and leave early.

            ```python
            def average(numbers):
                if not numbers:
                    return 0.0
                return sum(numbers) / len(numbers)

            print(average([2, 4]))
            print(average([]))
            ```

            Because `return` ends the function immediately, the second `return` only runs
            when the list is not empty. Without the check, `average([])` would divide by
            zero and crash.

            This pattern is called a *guard clause* or an *early return*. It keeps the main
            logic flat and readable.

            Handy built-ins: `sum(numbers)`, `len(numbers)`, `min(numbers)`, `max(numbers)`.
            `/` always gives a float (`4 / 2` is `2.0`).

            **Watch out:** `min([])` and `max([])` crash with a ValueError. Guard first.
        ''',
        "prompt": r'''
            You log how many tokens each request used and want a quick summary.

            **Write:** `token_stats(counts)`

            - `counts`: a list of ints (token counts), e.g. `[10, 30, 20]`; may be empty
            - **Returns:** **three values** (a tuple): the minimum, the maximum, and the
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
            ## Build with your own bricks

            Once you've written a function, it becomes a new brick you can build with - just
            like `len` or `max`. Bigger functions are usually a few smaller ones snapped together.

            ```python
            def total(counts):
                result = 0
                for c in counts:
                    result += c
                return result

            def is_over_budget(counts, budget):
                return total(counts) > budget

            print(total([100, 250]))
            print(is_over_budget([100, 250], 300))
            ```

            `is_over_budget` doesn't repeat the adding logic: it *calls* `total`. If you ever
            fix a bug in `total`, every function that uses it gets the fix for free.

            Programmers call this *reuse* or *composition*: small functions that each do one
            job, combined into bigger ones.

            **Watch out:** call the helper with brackets and arguments, `total(counts)`.
            Writing just `total` gives you the function itself, not its answer.
        ''',
        "prompt": r'''
            A chat app wants to know which messages are longer than average. Write two small
            functions, where the second one **reuses** the first.

            **Write:** `average_length(texts)`

            - `texts`: a list of strings, never empty, e.g. `["hi", "hello"]`
            - **Returns:** the average number of characters per string, as a float
              (e.g. `3.5`)

            **Write:** `longer_than_average(texts)`

            - `texts`: a list of strings, never empty
            - **Returns:** a new list with the strings whose length is **strictly greater**
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
            "Write average_length first and test it on its own. Then use it as a building block inside the second function.",
            "average_length: add up len() of every string and divide by how many strings there are. longer_than_average: compute the average once, then keep the strings whose length is bigger.",
            "In longer_than_average: store average_length(texts) in a variable; make an empty list; loop over texts and append each text whose len() is greater than the average; return the list.",
        ],
    },
    {
        "id": "functions-8",
        "title": "Any number of counts",
        "difficulty": 1,
        "lesson": r'''
            ## A bag that takes any number of items

            Some functions don't know in advance how many things you'll give them. `print`
            is one: `print("a")`, `print("a", "b", "c")`. You can write functions like that
            with a star.

            ```python
            def show_all(*names):
                print(names)
                for n in names:
                    print("-", n)

            show_all("gpt", "claude")
            show_all()
            ```

            `*names` means: "put every positional argument into one tuple called `names`".
            With no arguments, it's an empty tuple `()`. You loop over it like a list.

            People call this parameter `*args` (short for "arguments"); the name after the
            star can be anything.

            Its sibling `**kwargs` does the same for keyword arguments and collects them into
            a dict - you'll meet it in the next practice exercise.

            **Watch out:** the star goes in the `def` line only. Inside the body, use the plain
            name: `names`, not `*names`.
        ''',
        "prompt": r'''
            A conversation has several messages and you want the total token count, however
            many messages there are. Accept the counts as separate arguments.

            **Write:** `total_tokens(*counts)`

            - `*counts`: any number of ints passed by position (collected into a tuple),
              e.g. `total_tokens(10, 20, 5)`
            - **Returns:** the sum of all the counts, as an int

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
            "A parameter written with a star in front, like *counts, collects all the positional arguments into one tuple.",
            "Change the def line to use *counts, then add up the items of the tuple (a loop or sum() both work).",
            "def total_tokens(*counts): start a total at 0, loop over counts adding each one, return the total. With no arguments the tuple is empty, so the total stays 0.",
        ],
    },
    {
        "id": "functions-3",
        "title": "Request builder",
        "hints": [
            "Look at *args (collects extra positional arguments into a tuple) and **kwargs (collects extra keyword arguments into a dict). Any parameter after *args is keyword-only.",
            "The signature does most of the work: model, *messages, temperature=1.0, **extra. Then turn each message string into a dict, build the request dict and merge the extras in.",
            "Start with an empty list and loop over messages, appending {\"role\": \"user\", \"content\": m} for each m. Create the dict with model, messages, temperature. Then loop over extra.items() and copy each key/value into the dict (or call .update(extra)). Return it.",
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

            **Write:** `build_request(model, *messages, temperature=1.0, **extra)`

            - `model`: a string, required, e.g. `"gpt-4o"`
            - `*messages`: any number of message **strings** passed by position after `model`
              (`*messages` collects them into a tuple), e.g. `"hi", "how are you?"`
            - `temperature`: a float, default `1.0`, **keyword-only** (it comes after
              `*messages`, so it can only be passed as `temperature=...`)
            - `**extra`: any other keyword arguments (collected into a dict), e.g. `max_tokens=50`
            - **Returns:** a dict with the keys `"model"`, `"messages"`, `"temperature"`, plus
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
            "A default value is created once, when the def line runs - not on every call. A list default is shared by all calls.",
            "Use None as the default, and create a new empty list inside the function when history is None.",
            "Change the default to history=None. At the start of the body: if history is None, set history to []. Use `is None`, not `not history`, so an empty list passed in is still used. Then append and return.",
        ],
        "difficulty": 2,
        "prompt": r'''
            This helper appends a message to a conversation history and returns it. When
            called without a `history`, each call should start a **fresh** conversation,
            but right now conversations leak into each other (the *mutable default* trap).
            Fix it.

            **Write:** `add_message(text, history=...)`

            - `text`: a string, the message to add, e.g. `"hello"`
            - `history`: optional list of strings, the conversation so far, e.g. `["sys"]`;
              it must still have a default value so it can be left out
            - **Returns:** the history list, with `text` appended at the end

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
            "Functions are values: you can define a function inside another function and return it. The inner function can still see the outer function's variables (a closure).",
            "compose: the inner function loops over funcs, feeding each result into the next. count_calls: the inner wrapper forwards *args and **kwargs to func and records the call in a list (or dict) created in count_calls; a second inner function reports how many calls were recorded.",
            "compose: def pipeline(value), loop over funcs doing value = f(value), return value; then return pipeline. count_calls: calls = []; def wrapper(*args, **kwargs): append something to calls, return func(*args, **kwargs); def count(): return len(calls); return wrapper, count.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Text preprocessing is often a pipeline of small functions, and you often want to
            count how many times a function (like an API call) was used. Write two helpers
            that take functions and return new functions.

            **Write:** `compose(*funcs)`

            - `*funcs`: any number of one-argument functions (possibly none)
            - **Returns:** a **new function** that takes one value and passes it through each
              function in `funcs`, **left to right** (the output of one is the input of the next)

            **Write:** `count_calls(func)`

            - `func`: any function, e.g. the built-in `max`
            - **Returns:** **two functions** as a tuple `(wrapper, count)`:
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
            "This is a closure: make_limiter creates a variable (e.g. a list of timestamps) that the inner allow function keeps using between calls.",
            "Keep a list of the timestamps of allowed requests. On each call, first drop timestamps that are outside the 60-second window, then decide based on how many are left.",
            "Create an empty list in make_limiter. In allow(now): remove items <= now - 60 from the front; if len(list) < max_requests, append now and return True; otherwise return False. Return allow from make_limiter.",
        ],
        "difficulty": 3,
        "prompt": r'''
            LLM APIs limit how many requests you may send per minute. Build a client-side
            rate limiter that remembers past requests (this is a *closure*).

            **Write:** `make_limiter(max_requests)`

            - `max_requests`: an int, how many requests are allowed per 60 seconds, e.g. `2`
            - **Returns:** a function `allow(now)`:
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
