TOPIC = {
    "id": "loops",
    "title": "Loops",
    "track": "foundations",
    "order": 6,
    "requires": ["lists", "conditionals"],
    "summary": """
        Repeating work with for and while: range, enumerate, zip, break/continue,
        for-else, nested loops and accumulating results.
    """,
    "concepts": ["for loop", "while loop", "range", "enumerate", "zip", "break", "continue",
                 "for-else", "nested loops", "accumulators"],
}

LESSON = r'''
## Chapter notes: Loops

**`for` loop** - run the indented block once per item; the *loop variable* holds the
current item. Code after the block (un-indented) runs once, when the loop is done.

```python
for text in ["hi", "bye"]:
    print(text)
print("done")
```

**Accumulator pattern** - create the result *before* the loop, update it *inside*,
use/return it *after*: `total = 0` then `total += n`; `found = 0` then `found += 1`
inside an `if`; `kept = []` then `kept.append(x)`.

**`range`** - numbers on demand. `range(3)` -> 0, 1, 2. `range(1, 4)` -> 1, 2, 3 (stop is
never included). `range(10, 0, -2)` -> 10, 8, 6, 4, 2 (third argument = *step*).
For 1..n: `range(1, n + 1)`. Indexes of a list backwards: `range(len(xs) - 1, -1, -1)`.

**`enumerate(items, start=1)`** - pairs of (position, item): `for i, text in enumerate(msgs, start=1):`

**`zip(a, b)`** - walk two lists side by side: `for role, n in zip(roles, tokens):`
(stops at the shorter list).

**`break`** - leave the loop now. **`continue`** - skip the rest of this round, go to the
next item. **`for ... else`** - the `else` block runs only if the loop did *not* `break`.

**`while condition:`** - repeat as long as the condition is true. Something inside must
change the condition, or the loop runs forever. Use it when you don't know the number of
rounds in advance (retries, backoff, following "next page" links).

**Gotchas**
- Resetting the accumulator inside the loop keeps only the last item.
- `return` inside the loop body stops after the first item.
- `range(n)` starts at 0 and stops before `n`.
- Don't add/remove items of the list you're looping over - build a new list.

Docs: [for statements](https://docs.python.org/3/tutorial/controlflow.html#for-statements),
[range()](https://docs.python.org/3/library/stdtypes.html#range).
'''

EXERCISES = [
    {
        "id": "loops-s1",
        "lesson": r'''
            ## Doing something for every item

            A dealer doesn't write new instructions for each card - they repeat the same
            move for every card in the deck. A **`for` loop** does that: it takes each item of
            a list in turn, and runs the indented block once per item.

            ```python
            total = 0
            for n in [120, 80, 45]:
                total += n
                print("running total:", total)
            print("done:", total)
            ```

            Read it like this: *for each `n` in the list, do the indented lines*. Round 1 `n`
            is 120, round 2 it's 80, round 3 it's 45. The last line is **not** indented, so it
            is not part of the loop: it runs once, after the loop ends.

            `total += n` is shorthand for `total = total + n`.

            Vocabulary: `n` is the *loop variable*; each round is an *iteration*; the
            indented lines are the loop *body*. Walking through a list like this is called
            *iterating* over it.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            total = 0
            for n in [3, 5, 2]:
                total += n
                print(total)
            print("done")
        ''',
        "solution": r'''
            3
            8
            10
            done
        ''',
        "explanation": r'''
            The indented lines run once per item. `total` grows 0 -> 3 -> 8 -> 10 and is
            printed each round. `print("done")` is not indented, so it runs once, after
            the loop finishes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The indented lines repeat for each number; the last line is not indented.",
            "Keep a running total: add each number, then print the total so far.",
            "Round 1: 0 + 3. Round 2: add 5. Round 3: add 2. Each round prints the new total, then done is printed once.",
        ],
    },
    {
        "id": "loops-s3",
        "lesson": r'''
            ## The accumulator

            A tally counter at a door is set to zero **once**, in the morning. Then it clicks
            up for each visitor. If someone reset it to zero before every click, the evening
            total would always be 1. Loops that add things up work the same way:

            ```python
            counts = [120, 80, 45]
            total = 0            # set once, before the loop
            for n in counts:
                total += n       # grows every round
            print(total)
            ```

            Three places, three jobs: **before** the loop you create the starting value,
            **inside** you update it, **after** the loop you use it (print or return it).

            Vocabulary: a variable that collects a result across iterations is an
            *accumulator*.

            **Watch out:** if `total = 0` is inside the loop body, it is reset every round and
            only the last number survives. With an empty list, the body never runs at all - so
            the starting value must already be the right answer for "nothing" (`0`).
        ''',
        "title": "Fix the token total",
        "difficulty": 0,
        "prompt": r'''
            Fix the bug: `total_tokens` should add up the token counts of several messages,
            but right now it only returns the last one (and crashes on an empty list).

            **Write:** `total_tokens(counts)` (fix the starter)

            - `counts`: a list of ints, e.g. `[120, 80, 45]`
            - **Returns:** an int, the sum of all numbers in `counts`

            **Rules**
            - If `counts` is empty, return `0`.

            **Examples**
            ```python
            total_tokens([120, 80, 45])   # returns 245
            total_tokens([7])             # returns 7
            total_tokens([])              # returns 0
            ```
        ''',
        "starter": r'''
            def total_tokens(counts):
                for n in counts:
                    total = 0
                    total += n
                return total
        ''',
        "tests": r'''
            from solution import total_tokens

            def test_adds_all_three_counts():
                got = total_tokens([120, 80, 45])
                assert got == 245, f"got {got!r}"

            def test_single_count_returns_it():
                assert total_tokens([7]) == 7

            def test_empty_list_returns_zero():
                got = total_tokens([])
                assert got == 0, f"got {got!r}"
        ''',
        "solution": r'''
            def total_tokens(counts):
                total = 0
                for n in counts:
                    total += n
                return total
        ''',
        "hints": [
            "Look at where total is set to 0. How many times does that line run?",
            "The accumulator is reset on every round, so earlier numbers are lost. It must be set only once.",
            "Move the line total = 0 above the for line (same indentation as for). Keep total += n inside the loop.",
        ],
    },
    {
        "id": "loops-s4",
        "lesson": r'''
            ## Counting what matches

            Counting is the accumulator pattern with a twist: you don't add the item itself,
            you add **1** - but only when the item passes a test. Like a teacher counting the
            hands raised: look at each student, and click only for the raised hands.

            ```python
            scores = [0.9, 0.4, 0.75, 0.2]
            good = 0
            for s in scores:
                if s > 0.5:
                    good += 1
            print(good)
            ```

            The `if` is **inside** the loop (indented once more), so it runs for every item.
            The `good += 1` is inside the `if`, so it only runs when the test is true.

            Vocabulary: this is often called a *counter*, and the `if` is a *filter*.

            **Watch out:** `>` means "strictly greater" - a value equal to the limit does not
            pass. Use `>=` when equal should count.
        ''',
        "title": "Count long messages",
        "difficulty": 0,
        "prompt": r'''
            Find how many messages are longer than a token limit.

            **Write:** `count_over(counts, limit)`

            - `counts`: a list of ints (token counts), e.g. `[120, 80, 45, 300]`
            - `limit`: an int, e.g. `100`
            - **Returns:** an int, how many numbers in `counts` are **strictly greater than** `limit`

            **Rules**
            - A number **equal** to `limit` does not count (it is not greater).
            - If `counts` is empty, return `0`.

            **Examples**
            ```python
            count_over([120, 80, 45, 300], 100)   # returns 2
            count_over([100, 100, 101], 100)      # returns 1
            count_over([], 10)                    # returns 0
            ```
        ''',
        "starter": r'''
            def count_over(counts, limit):
                ...
        ''',
        "tests": r'''
            from solution import count_over

            def test_counts_numbers_above_limit():
                got = count_over([120, 80, 45, 300], 100)
                assert got == 2, f"got {got!r}"

            def test_number_equal_to_limit_is_not_counted():
                got = count_over([100, 100, 101], 100)
                assert got == 1, f"got {got!r}"

            def test_empty_list_returns_zero():
                assert count_over([], 10) == 0
        ''',
        "solution": r'''
            def count_over(counts, limit):
                found = 0
                for n in counts:
                    if n > limit:
                        found += 1
                return found
        ''',
        "hints": [
            "Use an accumulator that starts at 0, a for loop and an if inside it.",
            "Go through every number; each time one is bigger than limit, add 1 to your counter.",
            "Set found = 0. For each n in counts: if n > limit, do found += 1. After the loop, return found.",
        ],
    },
    {
        "id": "loops-s2",
        "lesson": r'''
            ## Numbers on demand: `range`

            Sometimes you don't have a list to loop over - you just need numbers: "try 3
            times", "number the pages 1 to 10". `range` produces numbers, like a ticket
            machine handing out 0, 1, 2, ...

            ```python
            for i in range(3):
                print("round", i)
            nums = []
            for i in range(1, 5):
                nums.append(i)
            print(nums)
            ```

            - `range(3)` gives 0, 1, 2 - three numbers, starting at 0.
            - `range(1, 5)` gives 1, 2, 3, 4 - it starts at the first number and stops
              **before** the second.
            - The loop builds a list by appending each number: an accumulator that is a list.

            Vocabulary: the two arguments are *start* and *stop*; like slices, start is
            included and stop is excluded.

            **Watch out:** to include `n` itself, the stop must be `n + 1`. And
            `range(1, 1)` is empty - the loop body doesn't run at all.
        ''',
        "title": "Count up to n",
        "difficulty": 0,
        "prompt": r'''
            Fill in the blank: the function is almost done, only the `___` is missing.

            **Write:** `count_up(n)` (replace the `___` in the starter)

            - `n`: an int, e.g. `3`
            - **Returns:** a list of ints counting from `1` up to **and including** `n`, e.g. `[1, 2, 3]`

            **Rules**
            - `n` itself must be in the list (remember: `range` stops *before* its stop value).
            - If `n` is `0`, return an empty list `[]`.

            **Examples**
            ```python
            count_up(3)   # returns [1, 2, 3]
            count_up(1)   # returns [1]
            count_up(0)   # returns []
            ```
        ''',
        "starter": r'''
            def count_up(n):
                numbers = []
                for i in range(1, ___):
                    numbers.append(i)
                return numbers
        ''',
        "tests": r'''
            from solution import count_up

            def test_count_up_to_three_includes_three():
                got = count_up(3)
                assert got == [1, 2, 3], f"got {got!r}"

            def test_count_up_to_one_is_just_one():
                assert count_up(1) == [1], f"got {count_up(1)!r}"

            def test_zero_returns_empty_list():
                assert count_up(0) == [], f"got {count_up(0)!r}"
        ''',
        "solution": r'''
            def count_up(n):
                numbers = []
                for i in range(1, n + 1):
                    numbers.append(i)
                return numbers
        ''',
        "hints": [
            "range(start, stop) never includes the stop value.",
            "To include n itself, the stop value must be one more than n.",
            "Replace ___ with n + 1.",
        ],
    },
    {
        "id": "loops-s6",
        "lesson": r'''
            ## Skipping an item: `continue`

            Sorting mail, you toss the junk aside and move straight on to the next letter -
            you don't do the rest of the steps for it. Inside a loop, `continue` means
            exactly that: *skip the rest of this round, go to the next item*.

            ```python
            messages = ["hi", "", "how are you?", ""]
            kept = []
            for text in messages:
                if text == "":
                    continue
                kept.append(text)
            print(kept)
            ```

            When `text` is empty, `continue` jumps back to the `for` line, so the `append`
            below it never runs for that item. Every other item goes through normally.

            Vocabulary: this is an *early skip*; the `if` + `continue` at the top of a loop
            body is often called a *guard*.

            **Watch out:** `continue` only skips the current item - the loop keeps going.
            (Its sibling `break`, coming soon, stops the whole loop.)
        ''',
        "title": "Skip empty messages",
        "difficulty": 0,
        "prompt": r'''
            Fill in the blank: a chat log sometimes contains empty messages, and they should be
            dropped before sending the history to a model.

            **Write:** `non_empty(messages)` (replace the `___` in the starter)

            - `messages`: a list of strings, possibly empty, e.g. `["hi", "", "bye"]`
            - **Returns:** a **new** list with every message except the empty strings `""`,
              in the original order

            **Rules**
            - Only the exact empty string `""` is dropped (a message `" "` with a space is kept).
            - An empty list, or a list of only `""`, returns `[]`.
            - Keep the `continue` structure of the starter (a check looks for `continue`).

            **Examples**
            ```python
            non_empty(["hi", "", "bye"])   # returns ["hi", "bye"]
            non_empty(["", ""])            # returns []
            non_empty(["a", " "])          # returns ["a", " "]
            ```
        ''',
        "starter": r'''
            def non_empty(messages):
                kept = []
                for text in messages:
                    if text == "":
                        ___
                    kept.append(text)
                return kept
        ''',
        "tests": r'''
            from solution import non_empty

            def test_drops_empty_messages():
                got = non_empty(["hi", "", "bye"])
                assert got == ["hi", "bye"], f"got {got!r}"

            def test_only_empty_messages_gives_empty_list():
                got = non_empty(["", ""])
                assert got == [], f"got {got!r}"

            def test_space_only_message_is_kept():
                got = non_empty(["a", " "])
                assert got == ["a", " "], f"got {got!r}"

            def test_empty_input_gives_empty_list():
                assert non_empty([]) == []

            def test_uses_continue():
                import ast
                ok = any(isinstance(n, ast.Continue) for n in ast.walk(ast.parse(source())))
                assert ok, "use continue to skip the empty messages"
        ''',
        "solution": r'''
            def non_empty(messages):
                kept = []
                for text in messages:
                    if text == "":
                        continue
                    kept.append(text)
                return kept
        ''',
        "hints": [
            "One keyword skips the rest of the current round and moves on to the next item.",
            "When the message is empty, the append below must not run for it - jump straight to the next message.",
            "Replace ___ with the keyword continue.",
        ],
    },
    {
        "id": "loops-s5",
        "lesson": r'''
            ## Repeat while something is true

            A `for` loop is for "every item of this list". But sometimes you don't know how
            many rounds you need: *keep retrying while it fails*, *keep doubling while it's
            small enough*. That's a **`while` loop** - like a kid asking "are we there yet?"
            until the answer changes.

            ```python
            wait = 1
            while wait <= 8:
                print("retry after", wait)
                wait *= 2
            print("stopped at", wait)
            ```

            Before each round Python checks the condition. True: run the body, then check
            again. False: skip past the loop. Here `wait` goes 1, 2, 4, 8, then 16 fails the
            test.

            Vocabulary: the test after `while` is the *loop condition*; `wait *= 2` is
            shorthand for `wait = wait * 2`.

            **Watch out:** something in the body must change the condition. If `wait` never
            changed, the loop would run forever (an *infinite loop*).
        ''',
        "title": "Retry waits",
        "difficulty": 0,
        "prompt": r'''
            When an API call fails, clients retry and **double** the wait each time
            (this is called *exponential backoff*).

            **Write:** `retry_waits(max_wait)`

            - `max_wait`: an int, the largest wait allowed, e.g. `10`
            - **Returns:** a list of ints: the waits `1, 2, 4, 8, ...` (start at `1`, double each time)
              for as long as the wait is `<= max_wait`

            **Rules**
            - A wait exactly equal to `max_wait` is included.
            - If `max_wait` is less than `1`, return `[]`.
            - Use a `while` loop (a check looks for `while`).

            **Examples**
            ```python
            retry_waits(10)   # returns [1, 2, 4, 8]
            retry_waits(16)   # returns [1, 2, 4, 8, 16]
            retry_waits(1)    # returns [1]
            retry_waits(0)    # returns []
            ```
        ''',
        "starter": r'''
            def retry_waits(max_wait):
                ...
        ''',
        "tests": r'''
            from solution import retry_waits

            def test_waits_up_to_ten():
                got = retry_waits(10)
                assert got == [1, 2, 4, 8], f"got {got!r}"

            def test_wait_equal_to_max_is_included():
                got = retry_waits(16)
                assert got == [1, 2, 4, 8, 16], f"got {got!r}"

            def test_zero_max_returns_empty_list():
                assert retry_waits(0) == []

            def test_uses_a_while_loop():
                assert "while " in source(), "use a while loop"
        ''',
        "solution": r'''
            def retry_waits(max_wait):
                waits = []
                wait = 1
                while wait <= max_wait:
                    waits.append(wait)
                    wait *= 2
                return waits
        ''',
        "hints": [
            "You need a list to collect waits, a wait variable that starts at 1, and a while loop.",
            "While the current wait is small enough, add it to the list and then double it.",
            "Set waits = [] and wait = 1. While wait <= max_wait: append wait, then wait *= 2. Return waits after the loop.",
        ],
    },
    {
        "id": "loops-1",
        "lesson": r'''
            ## Position and item together: `enumerate`

            A cloakroom attendant hands you the coat **and** its ticket number. `enumerate`
            does the same for a list: each round gives you a pair - the position and the item -
            and you unpack both into two loop variables.

            ```python
            roles = ["system", "user", "assistant"]
            for i, role in enumerate(roles):
                print(i, role)
            for i, role in enumerate(roles, start=1):
                print(f"{i}. {role}")
            ```

            By default counting starts at 0 (like indexes). `start=1` makes it count from 1,
            which is what humans expect in numbered lists.

            Vocabulary: `for i, role in ...` is *unpacking* each pair into two names. The
            numbering from 1 is called *1-based* (indexes are *0-based*).

            **Watch out:** without `enumerate` you might write a separate counter
            (`i = 0` ... `i += 1`). It works, but `enumerate` is shorter and harder to get
            wrong.
        ''',
        "hints": [
            'enumerate gives you a position and the item together; it can start counting at 1.',
            'Build a new list: for each message, add a string made of its number, a dot, a space and the text.',
            'Set lines = []. Loop with for i, text in enumerate(messages, start=1): append the f-string with i, then a dot and a space, then text. Return lines.',
        ],
        "title": "Numbered transcript",
        "difficulty": 1,
        "prompt": r'''
            Number the messages of a chat transcript so they can be displayed.

            **Write:** `number_lines(messages)`

            - `messages`: a list of strings, e.g. `["hi", "hello!"]`
            - **Returns:** a **new** list of strings, each one shaped `"<position>. <text>"`,
              e.g. `["1. hi", "2. hello!"]`

            **Rules**
            - Positions start at `1`, not `0` (*1-based*).
            - The format is the number, a dot, one space, then the text.
            - If `messages` is empty, return `[]`.
            - Use `enumerate` (a check looks for it).

            **Examples**
            ```python
            number_lines(["hi", "hello!"])      # returns ["1. hi", "2. hello!"]
            number_lines(list("abcdefghij"))    # last item is "10. j"
            number_lines([])                    # returns []
            ```
        ''',
        "starter": r'''
            def number_lines(messages):
                ...
        ''',
        "tests": r'''
            from solution import number_lines

            def test_two_messages_numbered_from_one():
                got = number_lines(["hi", "hello!"])
                assert got == ["1. hi", "2. hello!"], f"got {got!r}"

            def test_empty_list_returns_empty_list():
                assert number_lines([]) == []

            def test_tenth_line_is_numbered_ten():
                got = number_lines(list("abcdefghij"))
                assert got[-1] == "10. j", f"last line was {got[-1]!r}"

            def test_uses_enumerate():
                assert "enumerate(" in source(), "use enumerate"
        ''',
        "solution": r'''
            def number_lines(messages):
                lines = []
                for i, text in enumerate(messages, start=1):
                    lines.append(f"{i}. {text}")
                return lines
        ''',
    },
    {
        "id": "loops-2",
        "lesson": r'''
            ## Two lists side by side: `zip`

            A zipper joins two sides tooth by tooth: first with first, second with second.
            `zip(a, b)` walks two lists together and gives you one item from each per round.

            ```python
            roles = ["user", "assistant"]
            tokens = [12, 30]
            total = 0
            for role, n in zip(roles, tokens):
                print(f"{role}: {n}")
                total += n
            print(total)
            ```

            Round 1: `role` is `"user"` and `n` is 12. Round 2: `"assistant"` and 30. Each
            pair is unpacked into two loop variables, just like with `enumerate`.

            Vocabulary: lists where item `i` of one belongs with item `i` of the other are
            called *parallel lists*.

            **Watch out:** `zip` stops at the end of the **shorter** list, silently. Make sure
            your lists really have the same length.
        ''',
        "title": "Cost per request",
        "difficulty": 1,
        "prompt": r'''
            Two parallel lists describe a batch of API calls: call number `i` used
            `tokens[i]` tokens, and its model costs `prices[i]` dollars **per 1000 tokens**.

            **Write:** `total_cost(tokens, prices)`

            - `tokens`: a list of ints, e.g. `[2000, 1000]`
            - `prices`: a list of floats (dollars per 1000 tokens), same length, e.g. `[0.15, 2.5]`
            - **Returns:** a number (float), the total cost of all calls in dollars

            **Rules**
            - The cost of one call is its tokens divided by 1000, times its price.
            - If both lists are empty, return `0` (or `0.0`).
            - Walk the two lists together with `zip` (a check looks for it).

            **Examples**
            ```python
            total_cost([2000, 1000], [0.15, 2.5])              # returns 2.8   (0.3 + 2.5)
            total_cost([1000, 1000, 500], [0.15, 0.15, 0.15])  # returns 0.375
            total_cost([10], [1.0])                            # returns 0.01
            total_cost([], [])                                 # returns 0
            ```
        ''',
        "starter": r'''
            def total_cost(tokens, prices):
                ...
        ''',
        "tests": r'''
            from solution import total_cost
            import math

            def test_two_calls_with_different_prices():
                got = total_cost([2000, 1000], [0.15, 2.5])
                assert math.isclose(got, 2.8), f"got {got!r}"

            def test_empty_batch_costs_zero():
                assert total_cost([], []) == 0

            def test_three_calls_same_price():
                got = total_cost([1000, 1000, 500], [0.15, 0.15, 0.15])
                assert math.isclose(got, 0.375), f"got {got!r}"

            def test_price_is_per_thousand_tokens():
                got = total_cost([10], [1.0])
                assert math.isclose(got, 0.01), f"got {got!r}"

            def test_uses_zip_to_walk_both_lists():
                assert "zip(" in source(), "iterate with zip"
        ''',
        "solution": r'''
            def total_cost(tokens, prices):
                total = 0.0
                for count, price in zip(tokens, prices):
                    total += count / 1000 * price
                return total
        ''',
        "hints": [
            "zip(a, b) gives you one item from each list per round, as a pair.",
            "Keep a running total. For each pair of token count and price, add the cost of that call.",
            "Set total = 0.0. Loop with for count, price in zip(tokens, prices): add count / 1000 * price to total. Return total after the loop.",
        ],
    },
    {
        "id": "loops-7",
        "lesson": r'''
            ## Stopping early: `break`

            Streaming APIs send a reply in small pieces, and a special marker says "that's
            all". You read pieces until you see the marker, then you stop - even if more
            data follows. Inside a loop, `break` means *leave the loop right now*.

            ```python
            pieces = ["Par", "is", ".", "[DONE]", "junk"]
            text = ""
            for p in pieces:
                if p == "[DONE]":
                    break
                text += p
            print(text)
            ```

            When `p` is the marker, `break` jumps out of the loop entirely: `"junk"` is never
            looked at, and the code after the loop runs next. If the marker never appears,
            the loop simply finishes normally.

            Vocabulary: a special value that signals the end is a *sentinel*.

            **Watch out:** `break` ends the whole loop; `continue` only skips one item.
            And `text += p` works for strings too: it glues `p` onto the end
            (*concatenation*).
        ''',
        "title": "Read a stream until done",
        "difficulty": 1,
        "prompt": r'''
            A streaming model API sends its answer in small text pieces. The piece `"[DONE]"`
            marks the end; anything after it must be ignored.

            **Write:** `read_stream(pieces)`

            - `pieces`: a list of strings, e.g. `["Par", "is", ".", "[DONE]"]`
            - **Returns:** one string: all pieces **before** the first `"[DONE]"`, glued
              together in order with nothing between them

            **Rules**
            - Stop at the first `"[DONE]"`; pieces after it are not included.
            - If there is no `"[DONE]"`, glue all the pieces.
            - An empty list, or a list that starts with `"[DONE]"`, returns `""`.
            - Use `break` (a check looks for it).

            **Examples**
            ```python
            read_stream(["Par", "is", ".", "[DONE]"])        # returns "Paris."
            read_stream(["Hi", "[DONE]", "junk", "[DONE]"])  # returns "Hi"
            read_stream(["no ", "marker"])                   # returns "no marker"
            read_stream([])                                  # returns ""
            ```
        ''',
        "starter": r'''
            def read_stream(pieces):
                ...
        ''',
        "tests": r'''
            from solution import read_stream

            def test_joins_pieces_before_done():
                got = read_stream(["Par", "is", ".", "[DONE]"])
                assert got == "Paris.", f"got {got!r}"

            def test_ignores_everything_after_first_done():
                got = read_stream(["Hi", "[DONE]", "junk", "[DONE]"])
                assert got == "Hi", f"got {got!r}"

            def test_without_marker_joins_everything():
                got = read_stream(["no ", "marker"])
                assert got == "no marker", f"got {got!r}"

            def test_empty_or_immediate_done_gives_empty_string():
                assert read_stream([]) == "", f"got {read_stream([])!r}"
                assert read_stream(["[DONE]", "x"]) == "", f"got {read_stream(['[DONE]', 'x'])!r}"

            def test_uses_break():
                import ast
                ok = any(isinstance(n, ast.Break) for n in ast.walk(ast.parse(source())))
                assert ok, "use break to stop at the marker"
        ''',
        "solution": r'''
            def read_stream(pieces):
                text = ""
                for piece in pieces:
                    if piece == "[DONE]":
                        break
                    text += piece
                return text
        ''',
        "hints": [
            "Use a string accumulator that starts as an empty string, and break when you see the marker.",
            "Go through the pieces in order. If a piece is the marker, leave the loop; otherwise add it to the end of your text.",
            "Set text = \"\". For each piece: if piece == \"[DONE]\", break; otherwise text += piece. Return text after the loop.",
        ],
    },
    {
        "id": "loops-8",
        "lesson": r'''
            ## What else can `range` do?

            You know `range(stop)` and `range(start, stop)`. The official docs list
            **every** form a built-in accepts - reading the signature is often faster than
            guessing.

            ```python
            print(list(range(4)))
            print(list(range(2, 6)))
            print(list(range(0, 10, 3)))
            ```

            `list(range(...))` turns the numbers into a list so you can see them. The last
            line uses a third argument: the numbers now go up in jumps of 3.

            For this step, read the `range` documentation linked above and find out what that
            third argument is called, and what happens when it is **negative**. Pay attention
            to the rule for `stop` in that case: is it still excluded?

            Vocabulary: in the docs, a signature like `range(start, stop[, step])` means the
            part in square brackets is *optional*.
        ''',
        "title": "Countdown with range",
        "difficulty": 1,
        "research": {
            "note": "`range` accepts a third argument. Read the `range` docs (and the short tutorial section) to find what it does, especially when it is negative, then come back.",
            "links": [
                {"title": "range - Python docs",
                 "url": "https://docs.python.org/3/library/stdtypes.html#range"},
                {"title": "The range() function - Python tutorial",
                 "url": "https://docs.python.org/3/tutorial/controlflow.html#the-range-function"},
            ],
        },
        "prompt": r'''
            Before retrying a failed API call, a CLI shows a countdown: `3... 2... 1...`.

            **Write:** `countdown(n)`

            - `n`: a non-negative int, e.g. `3`
            - **Returns:** a list of ints from `n` down to `1`, e.g. `[3, 2, 1]`

            **Rules**
            - `1` is the last number; `0` is never included.
            - `countdown(0)` returns `[]`.
            - Produce the numbers with a **single `range` call with three arguments**
              (a check looks for it). Don't sort or reverse a list.

            **Examples**
            ```python
            countdown(3)   # returns [3, 2, 1]
            countdown(1)   # returns [1]
            countdown(0)   # returns []
            ```
        ''',
        "starter": r'''
            def countdown(n):
                ...
        ''',
        "tests": r'''
            from solution import countdown

            def test_counts_down_from_three():
                got = countdown(3)
                assert got == [3, 2, 1], f"got {got!r}"

            def test_one_gives_just_one():
                assert countdown(1) == [1], f"got {countdown(1)!r}"

            def test_zero_gives_empty_list():
                assert countdown(0) == [], f"got {countdown(0)!r}"

            def test_ten_ends_at_one():
                got = countdown(10)
                assert got == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1], f"got {got!r}"

            def test_uses_range_with_three_arguments():
                import ast
                ok = any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "range" and len(n.args) == 3
                         for n in ast.walk(ast.parse(source())))
                assert ok, "use range(start, stop, step)"
        ''',
        "solution": r'''
            def countdown(n):
                numbers = []
                for i in range(n, 0, -1):
                    numbers.append(i)
                return numbers
        ''',
        "hints": [
            "The third argument of range is the step, and it may be negative.",
            "Start at n, go down by 1 each time, and choose a stop value so that 1 is the last number (stop is excluded).",
            "Loop with for i in range(n, 0, -1) and append each i to a list; return the list. (list(range(n, 0, -1)) also works.)",
        ],
    },
    {
        "id": "loops-3",
        "hints": [
            'Walk the indexes backwards with range(len(token_counts) - 1, -1, -1) and keep a running total.',
            'Add messages from the newest one while the total stays within budget. The first message that would go over ends the loop for good.',
            'Set kept = [] and total = 0. For each index from the last down to 0: if total + that count > budget, break; otherwise add it to total and append the index. Reverse kept before returning it.',
        ],
        "title": "Fit messages in a budget",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A chat model has a limited context window, so an app keeps only the most recent
            messages that fit in a token budget.

            **Write:** `fit_history(token_counts, budget)`

            - `token_counts`: a list of ints, the token count of each message, **oldest first**,
              e.g. `[50, 10, 30, 20]`
            - `budget`: an int, the maximum total tokens to keep, e.g. `60`
            - **Returns:** a list of ints: the **indices** (positions) of the kept messages,
              in ascending order, e.g. `[1, 2, 3]`

            **Rules**
            - Start from the **newest** message (the last one) and go backwards.
            - Keep a message if the running total of kept tokens stays `<= budget`.
            - Stop at the **first** message that does not fit: older messages are dropped too,
              even if they are small enough to fit.
            - If nothing fits, or the list is empty, return `[]`.

            **Examples**
            ```python
            fit_history([50, 10, 30, 20], 60)   # returns [1, 2, 3]   (20 + 30 + 10 = 60)
            fit_history([5, 100, 5], 50)        # returns [2]         (100 doesn't fit, stop)
            fit_history([1, 2, 3], 100)         # returns [0, 1, 2]
            fit_history([10, 200], 50)          # returns []
            fit_history([], 100)                # returns []
            ```
        ''',
        "starter": r'''
            def fit_history(token_counts, budget):
                ...
        ''',
        "tests": r'''
            from solution import fit_history

            def test_keeps_newest_messages_within_budget():
                got = fit_history([50, 10, 30, 20], 60)
                assert got == [1, 2, 3], f"got {got!r}"

            def test_stops_at_first_message_that_does_not_fit():
                got = fit_history([5, 100, 5], 50)
                assert got == [2], f"older small messages must not be kept past a gap, got {got!r}"

            def test_everything_fits_returns_all_indices():
                got = fit_history([1, 2, 3], 100)
                assert got == [0, 1, 2], f"got {got!r}"

            def test_newest_too_big_returns_empty_list():
                assert fit_history([10, 200], 50) == [], f"got {fit_history([10, 200], 50)!r}"

            def test_empty_history_returns_empty_list():
                assert fit_history([], 100) == []
        ''',
        "solution": r'''
            def fit_history(token_counts, budget):
                kept = []
                total = 0
                for i in range(len(token_counts) - 1, -1, -1):
                    if total + token_counts[i] > budget:
                        break
                    total += token_counts[i]
                    kept.append(i)
                kept.reverse()
                return kept
        ''',
    },
    {
        "id": "loops-4",
        "hints": [
            "You don't know in advance how many pages you will visit, so this is a job for a while loop.",
            "Keep the current page position (starting at 0), a counter of pages read and a list of all items. Each round reads one page, adds its items and jumps to its next position.",
            "Set items = [], pos = 0, count = 0. While pos is not None and count < max_pages: unpack page_items, nxt = pages[pos]; add page_items to items (items.extend(page_items) or items += page_items); add 1 to count; set pos = nxt. Return items.",
        ],
        "title": "Follow the cursors",
        "difficulty": 2,
        "prompt": r'''
            A paginated API returns results one page at a time, and each page says where
            the next one is (this is called *cursor pagination*).

            **Write:** `collect(pages, max_pages)`

            - `pages`: a list of `(items, next)` tuples, always at least one. `items` is a list;
              `next` is the **position in `pages`** of the following page, or `None` on the last
              page. E.g. `[(["a", "b"], 2), (["z"], None), (["c"], 1)]`
            - `max_pages`: an int, the most pages you may read, e.g. `10`
            - **Returns:** one flat list with **all** the items of the pages you read, in the
              order you visited them

            **Rules**
            - Start at position `0` and follow the `next` links (not the order of the list).
            - Stop when `next` is `None` **or** after reading `max_pages` pages, whichever comes first.
            - A page with an empty `items` list is not the end: keep following its `next`.
            - Links may form a loop (a page pointing back to an earlier one); `max_pages` stops it.
            - Use a `while` loop (a check looks for `while`).

            **Examples**
            ```python
            pages = [(["a", "b"], 2), (["z"], None), (["c"], 1)]
            collect(pages, 10)                        # returns ["a", "b", "c", "z"]  (0 -> 2 -> 1)
            collect(pages, 2)                         # returns ["a", "b", "c"]
            collect(pages, 1)                         # returns ["a", "b"]
            collect([([], 1), (["x"], None)], 10)     # returns ["x"]
            collect([([1], 1), ([2], 0)], 5)          # returns [1, 2, 1, 2, 1]
            ```
        ''',
        "starter": r'''
            def collect(pages, max_pages):
                ...
        ''',
        "tests": r'''
            from solution import collect

            PAGES = [(["a", "b"], 2), (["z"], None), (["c"], 1)]

            def test_follows_links_not_list_order():
                got = collect(PAGES, 10)
                assert got == ["a", "b", "c", "z"], f"got {got!r}"

            def test_single_page_returns_its_items():
                got = collect([([1, 2], None)], 10)
                assert got == [1, 2], f"got {got!r}"

            def test_stops_after_max_pages():
                got = collect(PAGES, 2)
                assert got == ["a", "b", "c"], f"got {got!r}"
                got = collect(PAGES, 1)
                assert got == ["a", "b"], f"got {got!r}"

            def test_empty_page_is_not_the_end():
                got = collect([([], 1), (["x"], None)], 10)
                assert got == ["x"], f"got {got!r}"

            def test_looping_links_stop_at_max_pages():
                got = collect([([1], 1), ([2], 0)], 5)
                assert got == [1, 2, 1, 2, 1], f"got {got!r}"

            def test_uses_a_while_loop():
                assert "while " in source(), "use a while loop"
        ''',
        "solution": r'''
            def collect(pages, max_pages):
                items = []
                pos = 0
                count = 0
                while pos is not None and count < max_pages:
                    page_items, nxt = pages[pos]
                    items.extend(page_items)
                    count += 1
                    pos = nxt
                return items
        ''',
    },
    {
        "id": "loops-5",
        "hints": [
            'A for loop can have an else block that runs only if the loop did NOT break.',
            "Skip banned models with continue; break as soon as a model has a big enough window. The else block handles 'nothing found'.",
            'Loop for name, window in models: if name in banned, continue; if window >= required_tokens, break. Put else: return None under the for (same indentation). After the loop, return name.',
        ],
        "title": "First model that fits",
        "difficulty": 3,
        "prompt": r'''
            Pick which model to send a request to: the first one (in order of preference)
            that is allowed and has a big enough context window.

            **Write:** `choose(models, required_tokens, banned)`

            - `models`: a list of `(name, context_window)` tuples in preference order,
              e.g. `[("mini", 8000), ("std", 32000)]`
            - `required_tokens`: an int, e.g. `10000`
            - `banned`: a set of model names that must not be chosen, e.g. `{"std"}` (may be `set()`)
            - **Returns:** the **name** (a string) of the first model whose context window is
              `>= required_tokens` and whose name is not in `banned`, or `None` if there is none

            **Rules**
            - A window exactly equal to `required_tokens` is big enough.
            - Skip banned models even if they fit.
            - Return `None` when nothing fits, when every model is banned, or when `models` is empty.
            - Use a **`for ... else`** loop: the `else` clause handles the "not found" case
              (a check looks for a `for` loop with an `else`).

            **Examples**
            ```python
            models = [("mini", 8000), ("std", 32000), ("long", 200000)]
            choose(models, 10000, set())      # returns "std"
            choose(models, 8000, set())       # returns "mini"
            choose(models, 10000, {"std"})    # returns "long"
            choose(models, 500000, set())     # returns None
            choose([], 1, set())              # returns None
            ```
        ''',
        "starter": r'''
            def choose(models, required_tokens, banned):
                ...
        ''',
        "tests": r'''
            from solution import choose

            MODELS = [("mini", 8000), ("std", 32000), ("long", 200000)]

            def test_returns_first_model_that_fits():
                assert choose(MODELS, 10000, set()) == "std", f"got {choose(MODELS, 10000, set())!r}"

            def test_window_equal_to_required_fits():
                assert choose(MODELS, 8000, set()) == "mini"

            def test_skips_banned_models():
                got = choose(MODELS, 10000, {"std"})
                assert got == "long", f"got {got!r}"

            def test_returns_none_when_nothing_fits():
                assert choose(MODELS, 500000, set()) is None
                assert choose(MODELS, 1, {"mini", "std", "long"}) is None
                assert choose([], 1, set()) is None

            def test_uses_a_for_else_loop():
                import ast
                ok = any(isinstance(n, ast.For) and n.orelse for n in ast.walk(ast.parse(source())))
                assert ok, "use a for ... else loop"
        ''',
        "solution": r'''
            def choose(models, required_tokens, banned):
                for name, window in models:
                    if name in banned:
                        continue
                    if window >= required_tokens:
                        break
                else:
                    return None
                return name
        ''',
    },
    {
        "id": "loops-6",
        "hints": [
            "Check the arguments first, then use a while loop with a start position that moves by size - overlap.",
            "Slice size words from each start. Stop right after the chunk whose end reaches the end of the list.",
            "If size <= 0 or overlap < 0 or overlap >= size, return []. step = size - overlap, start = 0, chunks = []. While start < len(words): end = start + size; append words[start:end]; if end >= len(words) break; start += step. Return chunks.",
        ],
        "title": "Chunk with overlap",
        "difficulty": 3,
        "prompt": r'''
            RAG pipelines split documents into overlapping chunks before embedding them,
            so that an idea cut at a chunk border still appears whole in one chunk.

            **Write:** `chunk(words, size, overlap)`

            - `words`: a list (of words, or any items), e.g. `["a", "b", "c", "d", "e"]`
            - `size`: an int, the number of words per chunk, e.g. `3`
            - `overlap`: an int, how many words a chunk shares with the previous one, e.g. `1`
            - **Returns:** a list of lists (the chunks), in order

            **Rules**
            - The first chunk starts at position `0`; each next chunk starts `size - overlap`
              words after the previous one.
            - Stop as soon as a chunk reaches the end of the list: never add a trailing chunk
              that is entirely contained in the previous one.
            - The last chunk may be shorter than `size`.
            - Invalid settings return `[]`: `size <= 0`, or `overlap < 0`, or `overlap >= size`.
            - An empty `words` list returns `[]`.

            **Examples**
            ```python
            w = ["a", "b", "c", "d", "e"]
            chunk(w, 2, 0)                 # returns [["a", "b"], ["c", "d"], ["e"]]
            chunk(w, 3, 1)                 # returns [["a", "b", "c"], ["c", "d", "e"]]
            chunk(w, 4, 2)                 # returns [["a", "b", "c", "d"], ["c", "d", "e"]]
            chunk(w, 5, 3)                 # returns [["a", "b", "c", "d", "e"]]
            chunk(list(range(10)), 4, 1)   # returns [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]]
            chunk(["x"], 10, 2)            # returns [["x"]]
            chunk(w, 3, 3)                 # returns []   (invalid: overlap >= size)
            ```
        ''',
        "starter": r'''
            def chunk(words, size, overlap):
                ...
        ''',
        "tests": r'''
            from solution import chunk

            W = ["a", "b", "c", "d", "e"]

            def test_no_overlap_splits_into_pairs():
                got = chunk(W, 2, 0)
                assert got == [["a", "b"], ["c", "d"], ["e"]], f"got {got!r}"

            def test_overlap_of_one_ends_exactly_at_end():
                got = chunk(W, 3, 1)
                assert got == [["a", "b", "c"], ["c", "d", "e"]], f"got {got!r}"

            def test_no_redundant_trailing_chunk():
                got = chunk(W, 4, 2)
                assert got == [["a", "b", "c", "d"], ["c", "d", "e"]], f"got {got!r}"
                got = chunk(W, 5, 3)
                assert got == [W], f"a chunk covering everything should be the only one, got {got!r}"

            def test_short_or_empty_list():
                assert chunk(["x"], 10, 2) == [["x"]]
                assert chunk([], 3, 1) == []

            def test_ten_words_make_three_chunks():
                words = list(range(10))
                got = chunk(words, 4, 1)
                assert got == [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]], f"got {got!r}"

            def test_invalid_settings_return_empty():
                for size, overlap in ((0, 0), (-1, 0), (3, 3), (3, 5), (3, -1)):
                    got = chunk(W, size, overlap)
                    assert got == [], f"chunk(w, {size}, {overlap}) returned {got!r}"
        ''',
        "solution": r'''
            def chunk(words, size, overlap):
                if size <= 0 or overlap < 0 or overlap >= size:
                    return []
                step = size - overlap
                chunks = []
                start = 0
                while start < len(words):
                    end = start + size
                    chunks.append(words[start:end])
                    if end >= len(words):
                        break
                    start += step
                return chunks
        ''',
    },
]
