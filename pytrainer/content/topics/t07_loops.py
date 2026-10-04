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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["loop", "for", "while", "repeat", "iterate", "iteration", "range", "enumerate",
                 "zip", "break", "continue", "accumulator", "counter", "infinite loop"],
    "cards": [
        {
            "syntax": "for item in items:",
            "explain": "Runs the indented lines once for each item of the list. The loop variable refers to the current item.",
            "example": r'''
                total = 0
                for n in [120, 80, 45]:
                    total += n
                print(total)
                # 245
            ''',
        },
        {
            "syntax": "for i in range(start, stop, step):",
            "explain": "Loops over whole numbers. The stop value is never included. range(n) starts at 0 and adds 1 each time.",
            "example": r'''
                for i in range(1, 4):
                    print(i)
                # 1
                # 2
                # 3
                print(list(range(6, 0, -2)))
                # [6, 4, 2]
            ''',
        },
        {
            "syntax": "for i, item in enumerate(items, start=1):",
            "explain": "Gives a number and the item on each iteration. Without start=1 the numbers begin at 0.",
            "example": r'''
                for i, role in enumerate(["user", "assistant"], start=1):
                    print(i, role)
                # 1 user
                # 2 assistant
            ''',
        },
        {
            "syntax": "for a, b in zip(list_a, list_b):",
            "explain": "Gives the items at the same index of two lists on each iteration. Stops when the shorter list ends.",
            "example": r'''
                roles = ["user", "assistant"]
                tokens = [12, 30]
                for role, n in zip(roles, tokens):
                    print(role, n)
                # user 12
                # assistant 30
            ''',
        },
        {
            "syntax": "break  /  continue",
            "explain": "continue ends the current iteration and goes on with the next item. break ends the whole loop.",
            "example": r'''
                for name in ["tmp", "mini", "std", "long"]:
                    if name == "tmp":
                        continue
                    if name == "std":
                        break
                    print(name)
                # mini
            ''',
        },
        {
            "syntax": "while condition:",
            "explain": "Checks the condition before each iteration and runs the indented lines while it is true.",
            "example": r'''
                wait = 1
                while wait <= 4:
                    print(wait)
                    wait *= 2
                # 1
                # 2
                # 4
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Loops

A **loop** runs the same block of code more than once.

### for loops

A **`for` loop** runs its indented block once for each item of a list. The **loop
variable** (here `text`) refers to the current item. The indented block is the loop
**body**. One run of the body is an **iteration**.

```python
for text in ["hi", "bye"]:
    print(text)
print("done")
# hi
# bye
# done
```

The last line is not indented, so it is not part of the body. It runs once, after the
loop ends.

### Accumulators

An **accumulator** is a variable that collects a result across iterations. You create it
before the loop, update it in the body and use it after the loop.

```python
counts = [120, 80, 45]
total = 0
for n in counts:
    total += n
print(total)
# 245
```

Step through the code and watch `n` and `total` change on each iteration.

```diagram
{"type": "trace", "title": "A for loop with an accumulator", "code": ["counts = [120, 80, 45]", "total = 0", "for n in counts:", "    total += n", "print(total)"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {"counts": "[120, 80, 45]"}, "out": ""},
  {"line": 3, "vars": {"counts": "[120, 80, 45]", "total": "0"}, "out": ""},
  {"line": 4, "vars": {"counts": "[120, 80, 45]", "total": "0", "n": "120"}, "out": ""},
  {"line": 3, "vars": {"counts": "[120, 80, 45]", "total": "120", "n": "120"}, "out": ""},
  {"line": 4, "vars": {"counts": "[120, 80, 45]", "total": "120", "n": "80"}, "out": ""},
  {"line": 3, "vars": {"counts": "[120, 80, 45]", "total": "200", "n": "80"}, "out": ""},
  {"line": 4, "vars": {"counts": "[120, 80, 45]", "total": "200", "n": "45"}, "out": ""},
  {"line": 3, "vars": {"counts": "[120, 80, 45]", "total": "245", "n": "45"}, "out": ""},
  {"line": 5, "vars": {"counts": "[120, 80, 45]", "total": "245", "n": "45"}, "out": ""},
  {"line": null, "vars": {"counts": "[120, 80, 45]", "total": "245", "n": "45"}, "out": "245\n"}
]}
```

The same pattern counts items and builds lists. To count, add `1` inside an `if`. To
build a list, start with `[]` and call `append`.

```python
counts = [120, 80, 45]
found = 0
kept = []
for n in counts:
    if n > 100:
        found += 1
        kept.append(n)
print(found, kept)
# 1 [120]
```

### range

`range` produces whole numbers one at a time. `list(range(...))` puts them in a list so
you can print them.

```python
print(list(range(3)))
# [0, 1, 2]
print(list(range(1, 4)))
# [1, 2, 3]
print(list(range(10, 0, -2)))
# [10, 8, 6, 4, 2]
```

`range(stop)` starts at `0`. `range(start, stop)` starts at `start`. The stop value is
never included. The third value is the **step**: the amount added to get the next number.

For the numbers 1 to `n`, write `range(1, n + 1)`. For the indexes of a list from last to
first, write `range(len(xs) - 1, -1, -1)`.

```python
xs = ["a", "b", "c"]
for i in range(len(xs) - 1, -1, -1):
    print(i, xs[i])
# 2 c
# 1 b
# 0 a
```

### enumerate and zip

`enumerate(items, start=1)` produces one pair per item: a tuple that holds a number and the
item. The loop assigns the two values of each pair to two loop variables.

```python
msgs = ["hi", "bye"]
for i, text in enumerate(msgs, start=1):
    print(i, text)
# 1 hi
# 2 bye
```

`zip(a, b)` produces one pair per position: the item of `a` and the item of `b` at that
position. It stops when the shorter list ends.

```python
roles = ["user", "assistant"]
tokens = [12, 30, 99]
for role, n in zip(roles, tokens):
    print(role, n)
# user 12
# assistant 30
```

### break and continue

`continue` ends the current iteration. The loop goes on with the next item. `break` ends
the whole loop. Python then runs the first line after the loop.

```python
for name in ["tmp", "mini", "std", "long"]:
    if name == "tmp":
        continue
    if name == "std":
        break
    print(name)
# mini
```

### for-else

A `for` loop can have an `else` block. The `else` block runs only if the loop ended
without a `break`. In the example no value is at least `100000`, so `break` never runs and
the `else` block prints its line.

```python
windows = [8000, 32000]
for w in windows:
    if w >= 100000:
        print("found", w)
        break
else:
    print("no model fits")
# no model fits
```

### while loops

A **`while` loop** checks its condition before each iteration. It runs the body if the
condition is true and ends when the condition is false. Use it when you do not know the
number of iterations in advance: repeating a failed step until it succeeds, or reading
batches of data until none are left.

```python
wait = 1
while wait <= 4:
    print(wait)
    wait *= 2
# 1
# 2
# 4
```

After the third iteration `wait` is `8`. `8 <= 4` is false, so the loop ends.

The body must change something the condition uses. If it does not, the condition stays
true and the loop never ends.

### Nested loops

The body of a loop can contain another loop. This is called a **nested loop**. For each
iteration of the outer loop, the inner loop runs from start to finish. The inner body is
indented twice.

```python
for model in ["mini", "std"]:
    for size in [1, 2]:
        print(model, size)
# mini 1
# mini 2
# std 1
# std 2
```

The outer loop has 2 items and the inner loop has 2 items, so the inner body runs
2 * 2 = 4 times. A `break` in the inner loop ends only the inner loop.

### Common mistakes

- If you set the accumulator to its starting value inside the body, it is reset on every
  iteration. The result then contains only the last item.
- A `return` placed directly in the loop body ends the function during the first iteration.
- `range(n)` starts at `0` and stops before `n`. It never produces `n`.
- Do not add or remove items of the list you are looping over. Build a new list instead.

Docs: [for statements](https://docs.python.org/3/tutorial/controlflow.html#for-statements),
[range()](https://docs.python.org/3/library/stdtypes.html#range).
'''

EXERCISES = [
    {
        "id": "loops-s1",
        "lesson": r'''
            ## Do it again for every item

            A chat has three messages, and you want to greet each of the three senders. You could write
            three `print` lines. That works for three people. It does not work for three thousand. What
            you want to say is: do this for each item of the list.

            ```python
            for name in ["Ada", "Linus", "Grace"]:
                print("Hello", name)
            # Hello Ada
            # Hello Linus
            # Hello Grace
            ```

            Read the first line as "for each name in this list, run the indented lines". Python gives the
            first item the name `name` and runs the block. Then it gives the second item that name and
            runs the block again, and so on. When no items are left, the loop is over. The shape is the
            one you know from `if` and `def`: a line that ends with a colon, and an indented block.

            This is called a **`for` loop**. The name after `for` is the **loop variable**, and the
            indented lines are the **body** of the loop. One run of the body is an **iteration**, and
            going through items one at a time is called **iterating** over them.

            ```quiz
            How many times does this loop print `hi`?

            ~~~python
            for x in [7, 7, 7, 7]:
                print("hi")
            ~~~
            - [x] 4 times :: Right. The body runs once for each item, and the list has four items. What the items are makes no difference.
            - [ ] Once :: Equal items are still separate items. The loop visits every one of them.
            - [ ] 7 times :: The loop counts items, and there are four of them. Their value, 7, is only what `x` stands for.
            ```

            ### A loop that adds things up

            The body may use the loop variable in any way, for example to build a total:

            ```python
            total = 0
            for n in [120, 80, 45]:
                total += n
                print("running total:", total)
            print("done:", total)
            # running total: 120
            # running total: 200
            # running total: 245
            # done: 245
            ```

            Press Next and watch `n` and `total` change on each iteration:

            ```diagram
            {"type": "trace", "title": "A for loop over three numbers", "code": ["total = 0", "for n in [120, 80, 45]:", "    total += n", "    print(\"running total:\", total)", "print(\"done:\", total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"total": "0"}, "out": ""},
              {"line": 3, "vars": {"total": "0", "n": "120"}, "out": ""},
              {"line": 4, "vars": {"total": "120", "n": "120"}, "out": ""},
              {"line": 2, "vars": {"total": "120", "n": "120"}, "out": "running total: 120\n"},
              {"line": 3, "vars": {"total": "120", "n": "80"}, "out": "running total: 120\n"},
              {"line": 4, "vars": {"total": "200", "n": "80"}, "out": "running total: 120\n"},
              {"line": 2, "vars": {"total": "200", "n": "80"}, "out": "running total: 120\nrunning total: 200\n"},
              {"line": 3, "vars": {"total": "200", "n": "45"}, "out": "running total: 120\nrunning total: 200\n"},
              {"line": 4, "vars": {"total": "245", "n": "45"}, "out": "running total: 120\nrunning total: 200\n"},
              {"line": 2, "vars": {"total": "245", "n": "45"}, "out": "running total: 120\nrunning total: 200\nrunning total: 245\n"},
              {"line": 5, "vars": {"total": "245", "n": "45"}, "out": "running total: 120\nrunning total: 200\nrunning total: 245\n"},
              {"line": null, "vars": {"total": "245", "n": "45"}, "out": "running total: 120\nrunning total: 200\nrunning total: 245\ndone: 245\n"}
            ]}
            ```

            The last line of that program is not indented. It is not part of the loop, so it runs once,
            after the loop has finished.

            ```try
            for word in ["red", "green"]:
                print(word)
            print("end")
            ---
            Add a third item to the list so that the program prints `red`, `green`, `blue` and then `end`.
            ---
            for word in ["red", "green", "blue"]:
                print(word)
            print("end")
            ---
            The body ran one more time, because the list has one more item. The line after the loop still ran once.
            ```

            **Watch out:** only the indented lines repeat. If you indent the last line too, it becomes
            part of the body and runs on every iteration.

            **In short:** `for item in items:` runs its indented body once for each item, with `item`
            standing for that item.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line.
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
            The two indented lines run once for each of the three numbers. `total` goes from 0 to 3, then
            to 8, then to 10, and it is printed on every iteration. `print("done")` is not indented, so it
            runs once, after the loop has finished.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The indented lines repeat for each number. The last line is not indented.",
            "Keep a running total: add each number to it, and write down the total after each addition.",
            "Your first three lines are the total after each of the three numbers was added to it, starting from 0. Your fourth line is the text that is printed once, after the loop.",
        ],
    },
    {
        "id": "loops-s3",
        "lesson": r'''
            ## A variable that collects the result

            The loop in the last step added numbers into `total`. A variable that gathers a result over
            the iterations of a loop is the most useful pattern there is for loops. It has three parts,
            and each part has its place.

            ```python
            latencies = [300, 150, 250]
            total_ms = 0
            for ms in latencies:
                total_ms += ms
            print(total_ms)
            # 700
            ```

            1. Before the loop, the variable is created with a starting value.
            2. In the body, it is updated.
            3. After the loop, it is used: printed, or handed back.

            A variable that is used like this is called an **accumulator**.

            ```order
            prices = [4, 6]
            total = 0
            for p in prices:
                total += p
            print(total)
            ---
            The list and the starting value have to exist before the loop, the update belongs in the body, and the result is printed after the loop. The program prints 10.
            ```

            ### The starting value runs once

            See what happens when part 1 slips into the body:

            ```predict
            latencies = [300, 150, 250]
            for ms in latencies:
                total_ms = 0
                total_ms += ms
            print(total_ms)
            ---
            The line `total_ms = 0` now runs on every iteration, so the total is thrown away each time. Only the last item survives, and the program prints 250.
            ```

            There is a second reason to create the accumulator before the loop. With an empty list the
            body never runs, so the starting value is the final result. It has to be the right answer for
            "no items at all". For a sum, that is 0.

            ```quiz
            `counts` is an empty list. What does this program print?

            ~~~python
            total = 0
            for n in counts:
                total += n
            print(total)
            ~~~
            - [x] `0` :: Right. The body never runs, so `total` still has its starting value.
            - [ ] `None` :: `total` was given the value 0 before the loop, and nothing changed it.
            - [ ] Nothing, because of an error :: Looping over an empty list is fine. The body is skipped, and the program carries on.
            ```

            **Watch out:** an accumulator that is created only inside the body does not exist at all when
            the list is empty. Using it after the loop then stops the program with an error.

            **In short:** create the accumulator before the loop, update it in the body, and use it after
            the loop.
        ''',
        "title": "Fix the token total",
        "difficulty": 0,
        "prompt": r'''
            A conversation is made of several messages, and each message has a token count. The function
            below should add the counts up. Instead it gives back only the last one, and it stops with an
            error when the list is empty.

            **Your job:** find the bug in `total_tokens(counts)` and fix it. The code is already in the
            editor.

            **What goes in**
            - `counts`: a list of whole numbers, for example `[120, 80, 45]`

            **What comes out**
            - a whole number, the sum of all the numbers in `counts`: `245` for the example value

            **Rules**
            - An empty list gives `0`.

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
            "Look at the line that sets `total` to 0. How many times does it run?",
            "The accumulator is set back to 0 on every iteration, so the earlier numbers are lost. It has to be created only once.",
            "Move the line that creates `total` up, so that it stands before the `for` line and at the same indentation as the `for`. The line that adds stays inside the loop.",
        ],
    },
    {
        "id": "loops-s4",
        "lesson": r'''
            ## Counting the ones that pass a test

            How many answers scored above 0.5? This question does not ask for a sum. It asks for the
            number of items that pass a test. The accumulator pattern still works, with two changes: add
            1 in place of the item, and do it only when the test is true.

            ```python
            scores = [0.9, 0.4, 0.75, 0.2]
            good = 0
            for s in scores:
                if s > 0.5:
                    good += 1
            print(good)
            # 2
            ```

            An accumulator that counts is called a **counter**.

            Look at the two levels of indentation. The `if` is in the body of the loop, so Python checks
            it for every item. The line `good += 1` is indented under the `if`, so it runs only for the
            items that pass. Here those are `0.9` and `0.75`.

            ```fill
            words = ["hi", "hello", "hey", "howdy"]
            long_words = 0
            for w in words:
                if len(w) > 3:
                    ___
            print(long_words)
            ---
            - [x] long_words += 1 :: Right. Two words have more than 3 characters, `hello` and `howdy`, and each adds 1. The program prints 2.
            - [ ] long_words += len(w) :: This adds the length of each long word, not 1. The program prints 10, which is a sum of lengths and not a count.
            - [ ] long_words = 1 :: This sets the counter to 1 each time and never adds to it. The program prints 1 however many words pass.
            ```

            ### The boundary matters here too

            `>` is true only when the left value is really greater. An item that is equal to the limit
            does not pass. `>=` lets equal values through as well.

            ```predict
            scores = [0.5, 0.9, 0.5]
            strict = 0
            loose = 0
            for s in scores:
                if s > 0.5:
                    strict += 1
                if s >= 0.5:
                    loose += 1
            print(strict, loose)
            ---
            Only `0.9` is greater than 0.5, so `strict` is 1. All three scores are at least 0.5, so `loose` is 3.
            ```

            **Watch out:** check the indentation of the line that adds 1. At the level of the `if`, it
            would run for every item and count the whole list.

            **In short:** to count the matching items, start a counter at 0 and add 1 inside an `if` in
            the loop body.
        ''',
        "title": "Count long messages",
        "difficulty": 0,
        "prompt": r'''
            Some messages in a conversation are too long for a model. Before sending anything, your app
            wants to know how many messages are over the token limit.

            **Your job:** write `count_over(counts, limit)` so that it gives back that number.

            **What goes in**
            - `counts`: a list of whole numbers, the token count of each message, for example
              `[120, 80, 45, 300]`
            - `limit`: a whole number, for example `100`

            **What comes out**
            - a whole number: how many numbers in `counts` are greater than `limit`

            **Rules**
            - A number that is equal to `limit` does not count. It is not greater.
            - An empty list gives `0`.

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
            "You need a counter that starts at 0, a `for` loop, and an `if` inside the loop.",
            "Go through every number. Each time a number is greater than the limit, add 1 to the counter.",
            "Create the counter before the loop. In the body, test whether the number is greater than `limit`, and add 1 under that test. After the loop, hand the counter back.",
        ],
    },
    {
        "id": "loops-s2",
        "lesson": r'''
            ## Looping over numbers

            "Try three times." "Number the lines from 1 to 10." Sometimes there is no list to loop over,
            only a count. For that, `range` produces whole numbers one after another:

            ```python
            for i in range(3):
                print("round", i)
            # round 0
            # round 1
            # round 2
            ```

            `range(3)` gives three numbers, and it starts at 0: they are 0, 1 and 2. The 3 itself never
            appears.

            With two arguments, the first is the **start** and the second is the **stop**. The numbers
            begin at the start and end before the stop. It is the rule you know from slices: the start is
            included and the stop is left out.

            ```python
            print(list(range(1, 5)))
            # [1, 2, 3, 4]
            print(list(range(1, 1)))
            # []
            ```

            `list(...)` gathers the numbers into a list, so that you can see them. The second line shows
            that a range can be empty: when the start equals the stop, there are no numbers, and a loop
            over it never runs its body.

            ```predict
            print(list(range(4)))
            print(list(range(2, 6)))
            print(len(list(range(10))))
            ---
            `range(4)` starts at 0 and stops before 4. `range(2, 6)` starts at 2 and stops before 6. `range(10)` gives the ten numbers from 0 to 9.
            ```

            ```quiz
            Which call produces the numbers 1, 2, 3, 4, 5?
            - [x] `range(1, 6)` :: Right. The stop is left out, so to end at 5 the stop has to be 6.
            - [ ] `range(1, 5)` :: This stops before 5, so it gives 1, 2, 3, 4.
            - [ ] `range(5)` :: With one argument the numbers start at 0: 0, 1, 2, 3, 4.
            ```

            ### Building a list in a loop

            An accumulator does not have to be a number. It can be a list that starts empty and grows
            with `append`:

            ```python
            squares = []
            for i in range(1, 4):
                squares.append(i * i)
            print(squares)
            # [1, 4, 9]
            ```

            **Watch out:** the stop is never produced. To end at a certain number, the stop has to lie
            one past it.

            **In short:** `range(start, stop)` gives the whole numbers from `start` up to, but not
            including, `stop`.
        ''',
        "title": "Count up to n",
        "difficulty": 0,
        "prompt": r'''
            A numbered list needs the numbers 1, 2, 3 and so on, up to some number `n`. The function
            below builds them with a loop, and it is finished except for one detail.

            **Your job:** finish `count_up(n)`. It is written except for one gap, marked `___`. The gap is
            the stop of the `range`.

            **What goes in**
            - `n`: a whole number, for example `3`

            **What comes out**
            - a list of whole numbers that counts from `1` up to `n`, with `n` included: `[1, 2, 3]` for
              the example value

            **Rules**
            - `n` itself is in the list.
            - When `n` is `0`, the result is the empty list `[]`.

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
            "`range(start, stop)` never produces the stop value itself.",
            "For `n` to be in the list, the stop has to lie one past `n`.",
            "Replace the three underscores with an expression that is one more than the parameter.",
        ],
    },
    {
        "id": "loops-s6",
        "lesson": r'''
            ## Skip this one, carry on with the next

            A list of tokens contains filler items, `"<pad>"`, that carry no meaning. You want to keep
            everything else. Inside the loop, you need a way to say: not this one, next.

            ```python
            tokens = ["Hello", "<pad>", "world", "<pad>"]
            kept = []
            for tok in tokens:
                if tok == "<pad>":
                    continue
                kept.append(tok)
            print(kept)
            # ['Hello', 'world']
            ```

            `continue` ends the current iteration at once. Python goes back to the `for` line and takes
            the next item. The lines below `continue` in the body do not run for the current item.

            So for `"<pad>"` the test is true, `continue` runs, and the `append` line is skipped. For
            every other token the test is false, and the `append` line runs.

            Press Next and watch which line comes after `continue`:

            ```diagram
            {"type": "trace", "title": "continue skips the rest of one iteration", "code": ["tokens = [\"Hello\", \"<pad>\", \"world\", \"<pad>\"]", "kept = []", "for tok in tokens:", "    if tok == \"<pad>\":", "        continue", "    kept.append(tok)", "print(kept)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "[]"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "[]", "tok": "'Hello'"}, "out": ""},
              {"line": 6, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "[]", "tok": "'Hello'"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello']", "tok": "'Hello'"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello']", "tok": "'<pad>'"}, "out": ""},
              {"line": 5, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello']", "tok": "'<pad>'"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello']", "tok": "'<pad>'"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello']", "tok": "'world'"}, "out": ""},
              {"line": 6, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello']", "tok": "'world'"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello', 'world']", "tok": "'world'"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello', 'world']", "tok": "'<pad>'"}, "out": ""},
              {"line": 5, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello', 'world']", "tok": "'<pad>'"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello', 'world']", "tok": "'<pad>'"}, "out": ""},
              {"line": 7, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello', 'world']", "tok": "'<pad>'"}, "out": ""},
              {"line": null, "vars": {"tokens": "['Hello', '<pad>', 'world', '<pad>']", "kept": "['Hello', 'world']", "tok": "'<pad>'"}, "out": "['Hello', 'world']\n"}
            ]}
            ```

            ```predict
            for n in [1, 2, 3, 4]:
                if n % 2 == 0:
                    continue
                print(n)
            print("end")
            ---
            `n % 2 == 0` is true for the even numbers 2 and 4, so `continue` skips the `print` for them. The odd numbers 1 and 3 are printed, and `end` is printed once after the loop.
            ```

            An `if` with `continue` at the top of a loop body is called a **guard**. It keeps unwanted
            items away from the rest of the body.

            ```quiz
            What does `continue` do?
            - [x] It skips the rest of this iteration, and the loop goes on with the next item :: Right. Only the current item is affected. The loop itself keeps running.
            - [ ] It ends the whole loop :: That is the job of another keyword, `break`, which a later step covers. `continue` ends one iteration only.
            - [ ] It skips the next item :: The item that is skipped is the current one. The lines below `continue` do not run for it.
            ```

            **Watch out:** `continue` belongs under an `if`. Without a condition it would skip the rest
            of the body for every item.

            **In short:** `continue` ends the current iteration, and the loop carries on with the next
            item.
        ''',
        "title": "Skip empty messages",
        "difficulty": 0,
        "prompt": r'''
            A chat log sometimes contains empty messages. They should be dropped before the history is
            sent to a model. The function below does that with a guard at the top of its loop, and one
            word of it is missing.

            **Your job:** finish `non_empty(messages)`. It is written except for one gap, marked `___`.

            **What goes in**
            - `messages`: a list of strings, for example `["hi", "", "bye"]`. It may be empty.

            **What comes out**
            - a new list with every message except the empty strings `""`, in the original order

            **Rules**
            - Only the exact empty string `""` is dropped. A message `" "` that holds a space is kept.
            - An empty list, or a list of nothing but `""`, gives `[]`.
            - Keep the structure of the code as it is. A check looks for the keyword that belongs in the
              gap.

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
            "One keyword skips the rest of the current iteration and moves on to the next item.",
            "When the message is empty, the `append` line below must not run for it. Python should go straight to the next message.",
            "The gap is a single keyword, the one this lesson is about. Write it in place of the three underscores.",
        ],
    },
    {
        "id": "loops-s5",
        "lesson": r'''
            ## Repeat until something changes

            A `for` loop knows in advance how often it will run: once for each item. Some jobs do not
            know that. Keep retrying until the call succeeds. Keep cutting a text until it fits. For those
            jobs there is a loop that repeats for as long as a condition is true:

            ```python
            length = 900
            while length > 250:
                print("too long:", length)
                length -= 250
            print("fits:", length)
            # too long: 900
            # too long: 650
            # too long: 400
            # fits: 150
            ```

            After `while` comes a condition, like the one in an `if`. Python checks it. When it is true,
            Python runs the body and then checks the condition again. When it is false, Python carries on
            with the first line after the loop. The test is called the **loop condition**, and the whole
            thing is a **`while` loop**.

            Press Next and watch the condition being checked before every iteration:

            ```diagram
            {"type": "trace", "title": "A while loop", "code": ["length = 900", "while length > 250:", "    print(\"too long:\", length)", "    length -= 250", "print(\"fits:\", length)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"length": "900"}, "out": ""},
              {"line": 3, "vars": {"length": "900"}, "out": ""},
              {"line": 4, "vars": {"length": "900"}, "out": "too long: 900\n"},
              {"line": 2, "vars": {"length": "650"}, "out": "too long: 900\n"},
              {"line": 3, "vars": {"length": "650"}, "out": "too long: 900\n"},
              {"line": 4, "vars": {"length": "650"}, "out": "too long: 900\ntoo long: 650\n"},
              {"line": 2, "vars": {"length": "400"}, "out": "too long: 900\ntoo long: 650\n"},
              {"line": 3, "vars": {"length": "400"}, "out": "too long: 900\ntoo long: 650\n"},
              {"line": 4, "vars": {"length": "400"}, "out": "too long: 900\ntoo long: 650\ntoo long: 400\n"},
              {"line": 2, "vars": {"length": "150"}, "out": "too long: 900\ntoo long: 650\ntoo long: 400\n"},
              {"line": 5, "vars": {"length": "150"}, "out": "too long: 900\ntoo long: 650\ntoo long: 400\n"},
              {"line": null, "vars": {"length": "150"}, "out": "too long: 900\ntoo long: 650\ntoo long: 400\nfits: 150\n"}
            ]}
            ```

            ```predict
            n = 1
            while n < 20:
                n *= 3
            print(n)
            ---
            `n` goes from 1 to 3 to 9 to 27. After 9 the condition `9 < 20` is still true, so the body runs once more. `27 < 20` is false, so the loop ends, and the program prints 27.
            ```

            ### The body has to change something

            The body must change a value that the condition uses. If it does not, the condition stays
            true and the loop never ends. That is called an **infinite loop**. In this app, a program that
            runs for too long is stopped with a time limit message.

            ```quiz
            Why does this loop never end?

            ~~~python
            count = 0
            while count < 3:
                print(count)
            ~~~
            - [x] Nothing in the body changes `count` :: Right. `count` stays 0, so `count < 3` stays true for ever. A line such as `count += 1` in the body would fix it.
            - [ ] `0 < 3` is false :: It is true, which is why the body runs at all. The trouble is that it never becomes false.
            - [ ] A `while` loop needs a list :: A `while` loop needs only a condition. Lists are for `for` loops.
            ```

            **Watch out:** the condition is checked before each iteration, not in the middle of the body.
            The body always runs to its end.

            **In short:** `while condition:` repeats its body for as long as the condition is true, so the
            body has to change something that the condition looks at.
        ''',
        "title": "Retry waits",
        "difficulty": 0,
        "prompt": r'''
            When a call to an API fails, a client waits a moment and tries again. If the call fails
            again, it waits twice as long before the next try. This pattern is called exponential
            backoff. You want the list of waiting times, in seconds.

            **Your job:** write `retry_waits(max_wait)` so that it gives back that list.

            **What goes in**
            - `max_wait`: a whole number, the longest wait that is allowed, for example `10`

            **What comes out**
            - a list of whole numbers: the waits `1, 2, 4, 8, ...`, starting at `1` and doubling each
              time, for as long as the wait is not more than `max_wait`: `[1, 2, 4, 8]` for the example
              value

            **Rules**
            - A wait that is exactly equal to `max_wait` is in the list.
            - When `max_wait` is less than `1`, the result is `[]`.
            - Use a `while` loop. A check looks for it.

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
            "You need a list that collects the waits, a variable for the current wait that starts at 1, and a `while` loop.",
            "As long as the current wait is not above the maximum, add it to the list, and then double it.",
            "Create an empty list and a wait of 1. The loop condition compares the wait with `max_wait` and lets equal values through. In the body, append the wait, and then double it with an augmented assignment. After the loop, hand back the list.",
        ],
    },
    {
        "id": "loops-1",
        "lesson": r'''
            ## The position and the item together

            You want to number the lines of a transcript: `1. hi`, `2. hello`. Inside a `for` loop you
            have each item, but not its position. You could keep a counter of your own, with `i = 0`
            before the loop and `i += 1` in the body. That is two extra lines, and when you forget the
            second one, every number is wrong.

            Python does the counting for you:

            ```python
            roles = ["system", "user", "assistant"]
            for i, role in enumerate(roles):
                print(i, role)
            # 0 system
            # 1 user
            # 2 assistant
            ```

            `enumerate(roles)` hands the loop a pair for each item: a number, and the item. With two
            loop variables and a comma between them, the pair is unpacked, as you learned in the
            Variables chapter. The first variable gets the number and the second gets the item.

            The numbers start at 0, so they are the indexes of the items. Counting from 0 is called
            **0-based**. People count from 1, which is called **1-based**, and for that `enumerate`
            takes the keyword argument `start=1`:

            ```python
            for i, role in enumerate(["system", "user"], start=1):
                print(f"#{i} {role}")
            # #1 system
            # #2 user
            ```

            ```quiz
            In `for i, x in enumerate(["a", "b", "c"]):`, what is `i` during the last iteration?
            - [x] `2` :: Right. Without `start`, the numbers begin at 0, so three items are numbered 0, 1 and 2.
            - [ ] `3` :: That would be the last number with `start=1`. By default the count starts at 0.
            - [ ] `"c"` :: That is `x`, the item. `i` is the number that comes with it.
            ```

            ```fill
            steps = ["open", "read", "close"]
            for ___ in enumerate(steps, start=1):
                print(n, step)
            ---
            - [x] n, step :: Right. The number goes to the first name and the item to the second, so the program prints `1 open`, `2 read` and `3 close`.
            - [ ] step, n :: The names are the wrong way round. `step` gets the number and `n` gets the item, so the program prints `open 1` and so on.
            - [ ] n :: With a single name, `n` is the whole pair, and the name `step` does not exist. Python stops with a `NameError`.
            ```

            **Watch out:** the number comes first and the item second. With the two loop variables the
            other way round, nothing fails, and every use of them is wrong.

            **In short:** `for i, item in enumerate(items, start=1):` gives you each item together with
            its number.
        ''',
        "hints": [
            "`enumerate` gives you the position and the item together, and it can start counting at 1.",
            "Build a new list. For each message, add a string made of its number, a dot, a space and the text.",
            "Start with an empty list. Loop over `enumerate` of the messages, with the keyword argument that starts the count at 1, and with two loop variables. In the body, append an f-string made of the number, a dot, a space and the text. After the loop, hand back the list.",
        ],
        "title": "Numbered transcript",
        "difficulty": 1,
        "prompt": r'''
            A chat transcript is shown as a numbered list, so that people can refer to "message 3".

            **Your job:** write `number_lines(messages)` so that it gives back the messages with their
            numbers in front.

            **What goes in**
            - `messages`: a list of strings, for example `["hi", "hello!"]`

            **What comes out**
            - a new list of strings, each of the form `"<position>. <text>"`: `["1. hi", "2. hello!"]` for
              the example value

            **Rules**
            - The positions start at `1`, not at `0`.
            - The format is the number, a dot, one space, and then the text.
            - An empty list gives `[]`.
            - Use `enumerate`. A check looks for it.

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
            ## Two lists side by side

            One list holds the roles of a conversation, and another holds the token counts. Item 0 of the
            first belongs with item 0 of the second, item 1 with item 1, and so on. You need to walk through both without losing those pairings.

            ```python
            roles = ["user", "assistant"]
            tokens = [12, 30]
            for role, n in zip(roles, tokens):
                print(f"{role}: {n}")
            # user: 12
            # assistant: 30
            ```

            Lists whose same-position items belong together are called **parallel lists**.

            `zip(roles, tokens)` pairs the items up: the first with the first, the second with the
            second. On each iteration it hands the loop one pair, and the two loop variables unpack it,
            the same way as with `enumerate`.

            ```order
            items = ["pen", "ink"]
            prices = [2, 7]
            for item, price in zip(items, prices):
                print(f"{item}: {price}")
            ---
            Both lists have to exist before `zip` can pair them up. The body then runs once for each pair, and the program prints `pen: 2` and `ink: 7`.
            ```

            The body of such a loop is an ordinary body. An accumulator, an `if` or a `continue` works in
            it as before.

            ### When the lists are not the same length

            ```predict
            names = ["a", "b", "c"]
            sizes = [1, 2]
            for name, size in zip(names, sizes):
                print(name, size)
            print("end")
            ---
            `zip` stops as soon as the shorter list has no more items. There is no error, and `"c"` is never used. The program prints `a 1`, `b 2` and `end`.
            ```

            **Watch out:** because `zip` stops quietly at the shorter list, a missing item does not show
            up as an error. It shows up as a result that is too small. Make sure the two lists have the
            same length.

            **In short:** `for a, b in zip(list_a, list_b):` walks through two lists together, one pair
            at a time.
        ''',
        "title": "Cost per request",
        "difficulty": 1,
        "prompt": r'''
            Two parallel lists describe a batch of API calls. Call number `i` used `tokens[i]` tokens, and
            the model it went to costs `prices[i]` dollars for every 1000 tokens. You want the cost of the
            whole batch.

            **Your job:** write `total_cost(tokens, prices)` so that it gives back the total cost in
            dollars.

            **What goes in**
            - `tokens`: a list of whole numbers, for example `[2000, 1000]`
            - `prices`: a list of floats of the same length, the price in dollars for 1000 tokens, for
              example `[0.15, 2.5]`

            **What comes out**
            - a number (a float): the cost of all the calls together: `2.8` for the example values

            **Rules**
            - The cost of one call is its tokens divided by 1000, times its price.
            - When both lists are empty, the result is `0` (or `0.0`).
            - Walk through the two lists together with `zip`. A check looks for it.

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
            "`zip(a, b)` gives you one item from each list on every iteration, as a pair.",
            "Keep a running total. For each pair of a token count and a price, add the cost of that call.",
            "Start a total at 0.0. Loop over `zip` of the two lists, with two loop variables. In the body, add the tokens divided by 1000 and multiplied by the price. After the loop, hand back the total.",
        ],
    },
    {
        "id": "loops-7",
        "lesson": r'''
            ## Stop as soon as you have enough

            The output of a model is a list of tokens, and it ends with a special end marker, `"<eos>"`,
            short for "end of sequence". Anything after the marker is junk. Once you have seen the
            marker, there is no reason to look at the rest of the list.

            ```python
            tokens = ["The", "answer", "<eos>", "junk"]
            shown = []
            for tok in tokens:
                if tok == "<eos>":
                    break
                shown.append(tok)
            print(shown)
            # ['The', 'answer']
            ```

            `break` ends the whole loop at once. The remaining items are never visited, and Python
            carries on with the first line after the loop. A value that marks the end of the data, as
            `"<eos>"` does here, is called a **sentinel**.

            Press Next and watch which line comes after `break`:

            ```diagram
            {"type": "trace", "title": "break ends the loop", "code": ["tokens = [\"The\", \"answer\", \"<eos>\", \"junk\"]", "shown = []", "for tok in tokens:", "    if tok == \"<eos>\":", "        break", "    shown.append(tok)", "print(shown)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "[]"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "[]", "tok": "'The'"}, "out": ""},
              {"line": 6, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "[]", "tok": "'The'"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The']", "tok": "'The'"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The']", "tok": "'answer'"}, "out": ""},
              {"line": 6, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The']", "tok": "'answer'"}, "out": ""},
              {"line": 3, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The', 'answer']", "tok": "'answer'"}, "out": ""},
              {"line": 4, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The', 'answer']", "tok": "'<eos>'"}, "out": ""},
              {"line": 5, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The', 'answer']", "tok": "'<eos>'"}, "out": ""},
              {"line": 7, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The', 'answer']", "tok": "'<eos>'"}, "out": ""},
              {"line": null, "vars": {"tokens": "['The', 'answer', '<eos>', 'junk']", "shown": "['The', 'answer']", "tok": "'<eos>'"}, "out": "['The', 'answer']\n"}
            ]}
            ```

            ```predict
            for n in [4, 8, 15, 16]:
                if n > 10:
                    break
                print(n)
            print("after", n)
            ---
            4 and 8 are printed. At 15 the test is true, so `break` ends the loop before the `print`, and 16 is never visited. After a loop, the loop variable still holds the last item it was given, which is 15.
            ```

            You now know three ways to cut something short. Keep them apart:

            ```match
            `continue` :: ends this iteration, and the loop goes on with the next item
            `break` :: ends the whole loop, and the remaining items are never visited
            `return` :: ends the whole function, and hands a value back
            ```

            ### Adding to a string

            One more tool for this step. An accumulator can be a string as well. `text += part` builds a
            longer string, with the part joined on at the end:

            ```python
            text = ""
            text += "to"
            text += "ken"
            print(text)
            # token
            ```

            **Watch out:** when the sentinel is not in the list, `break` never runs. The loop then ends
            in the normal way, after the last item, and that is not an error.

            **In short:** `break` ends a loop at once, and Python carries on with the first line after
            the loop.
        ''',
        "title": "Read a stream until done",
        "difficulty": 1,
        "prompt": r'''
            A model API that streams its answer sends the text in small pieces, one after another. The
            piece `"[DONE]"` marks the end of the answer, and anything that comes after it must be
            ignored.

            **Your job:** write `read_stream(pieces)` so that it gives back the answer as one string.

            **What goes in**
            - `pieces`: a list of strings, for example `["Par", "is", ".", "[DONE]"]`

            **What comes out**
            - one string: all the pieces before the first `"[DONE]"`, joined in order with nothing
              between them: `"Paris."` for the example value

            **Rules**
            - The answer stops at the first `"[DONE]"`. Pieces after it are not included.
            - When there is no `"[DONE]"`, all the pieces are joined.
            - An empty list, or a list that starts with `"[DONE]"`, gives `""`.
            - Use `break`. A check looks for it.

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
            "Use a string accumulator that starts as an empty string, and `break` when you see the marker.",
            "Go through the pieces in order. When a piece is the marker, leave the loop. Otherwise add the piece to the end of your text.",
            "Start with an empty string. In the loop, first test whether the piece is equal to the marker, and `break` under that test. Below the test, add the piece to the text with `+=`. After the loop, hand back the text.",
        ],
    },
    {
        "id": "loops-8",
        "lesson": r'''
            ## The third number of range

            You know `range(stop)` and `range(start, stop)`. There is a third form. The documentation of
            a built-in lists every form that it accepts, so reading it is quicker than guessing.

            ```python
            print(list(range(0, 10, 3)))
            # [0, 3, 6, 9]
            ```

            With a third argument of 3, each number is 3 more than the one before it. The stop is still
            left out.

            In the Basics chapter you met the signature, the line in the docs that shows the parameters
            of a function. For `range` the docs write `range(start, stop[, step])`. The square brackets
            mean that the third argument may be left out, and when it is left out it is 1.

            ```predict
            print(list(range(0, 10, 5)))
            print(list(range(1, 8, 2)))
            print(list(range(10, 20, 4)))
            ---
            From 0 in steps of 5, stopping before 10: 0 and 5. From 1 in steps of 2, stopping before 8: 1, 3, 5, 7. From 10 in steps of 4, stopping before 20: 10, 14, 18.
            ```

            ```quiz
            Which numbers does `range(2, 11, 3)` produce?
            - [x] 2, 5, 8 :: Right. It starts at 2 and adds 3 each time. The next number would be 11, and the stop is left out.
            - [ ] 2, 5, 8, 11 :: The stop value is never produced, with a step as well as without one.
            - [ ] 3, 6, 9 :: The first number is always the start, which is 2 here. The step only decides how far apart the numbers are.
            ```

            For this step, read the `range` entry that is linked in the task. Find out what `range`
            produces when the third argument is negative, and how the rule about the stop reads in that
            case.

            **Watch out:** a step never changes the rule that the stop is left out. Check the last number
            you expect against the stop.

            **In short:** `range(start, stop, step)` moves from `start` towards `stop` in steps of `step`
            and never produces `stop` itself.
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
            Before a command-line tool retries a failed API call, it shows a countdown: 3, 2, 1. You need
            the numbers for that countdown as a list.

            **Your job:** write `countdown(n)` so that it gives back the numbers from `n` down to `1`.

            **What goes in**
            - `n`: a whole number that is 0 or more, for example `3`

            **What comes out**
            - a list of whole numbers from `n` down to `1`: `[3, 2, 1]` for the example value

            **Rules**
            - `1` is the last number. `0` is never in the list.
            - `countdown(0)` gives `[]`.
            - Produce the numbers with one `range` call that has three arguments. A check looks for it.
              Do not sort or reverse a list.

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
            "The third argument of `range` is the step, and the docs say what happens when it is negative.",
            "Start at `n` and go down by 1 each time. Choose the stop so that 1 is the last number that is produced: the stop itself is left out.",
            "Build an empty list. Loop over one `range` call with three arguments: the start, a stop that lies just past the last number you want, and a negative step. Append each number, and hand back the list after the loop.",
        ],
    },
    {
        "id": "loops-3",
        "hints": [
            "Walk through the indexes backwards, with a `range` that has a negative step, and keep a running total.",
            "Add messages from the newest one for as long as the total stays within the budget. The first message that would go over the budget ends the loop for good.",
            "Start with an empty list and a total of 0. Loop over the indexes from the last one down to 0. When the total plus the count of that message is over the budget, `break`. Otherwise add the count to the total and append the index. After the loop, reverse the list of indexes and hand it back.",
        ],
        "title": "Fit messages in a budget",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A model can only read a limited number of tokens, so a chat app sends only the most recent
            messages that fit into a token budget. It walks backwards from the newest message and keeps
            messages until one does not fit.

            **Your job:** write `fit_history(token_counts, budget)` so that it gives back the positions
            of the messages that are kept.

            **What goes in**
            - `token_counts`: a list of whole numbers, the token count of each message, the oldest first,
              for example `[50, 10, 30, 20]`
            - `budget`: a whole number, the most tokens that may be kept in total, for example `60`

            **What comes out**
            - a list of whole numbers: the indexes of the kept messages, in ascending order: `[1, 2, 3]`
              for the example values

            **Rules**
            - Start at the newest message, which is the last one, and go backwards.
            - A message is kept when the running total of kept tokens, with this message added, is not
              more than `budget`.
            - Stop at the first message that does not fit. All older messages are dropped too, even
              those that would be small enough.
            - When nothing fits, or when the list is empty, the result is `[]`.

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
            "You do not know in advance how many pages you will visit, so this is a job for a `while` loop.",
            "Keep three things: the position of the current page, starting at 0, a count of the pages read, and a list of all the items. Each iteration reads one page, adds its items, and moves to the position that the page names as next.",
            "The loop runs while the position is not `None` and the count is below `max_pages`. In the body, unpack the page at the current position into its items and its next position, add the items to your list with `extend`, add 1 to the count, and make the next position the current one. After the loop, hand back the list.",
        ],
        "title": "Follow the cursors",
        "difficulty": 2,
        "prompt": r'''
            An API with many results sends them one page at a time, and each page says where the next
            page is. This is called cursor pagination. To get everything, you start at the first page and
            keep following the links.

            **Your job:** write `collect(pages, max_pages)` so that it gives back the items of all the
            pages that were read.

            **What goes in**
            - `pages`: a list of `(items, next)` tuples, with at least one tuple. `items` is a list.
              `next` is the position in `pages` of the page that follows, or `None` on the last page. For
              example: `[(["a", "b"], 2), (["z"], None), (["c"], 1)]`
            - `max_pages`: a whole number, the most pages that may be read, for example `10`

            **What comes out**
            - one flat list with all the items of the pages that were read, in the order in which the
              pages were visited

            **Rules**
            - Start at position `0`, and follow the `next` links. The order of the list `pages` does not
              matter.
            - Stop when `next` is `None`, or after `max_pages` pages have been read, whichever comes
              first.
            - A page whose `items` list is empty is not the end. Keep following its `next`.
            - The links may run in a circle, with a page that points back to an earlier one. `max_pages`
              is what stops the reading then.
            - Use a `while` loop. A check looks for it.

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
            "A `for` loop can have an `else` block. It runs only when the loop ended without a `break`.",
            "Skip banned models with `continue`, and `break` as soon as a model has a window that is big enough. The `else` block handles the case where nothing was found.",
            "Loop over the models with two loop variables, the name and the window. A banned name gets `continue`. A window that is at least the required size gets `break`. Under the loop, at the indentation of the `for`, an `else` block hands back `None`. After that, hand back the name.",
        ],
        "title": "First model that fits",
        "difficulty": 3,
        "prompt": r'''
            Your app has several models, listed in order of preference. For each request it picks the
            first model that is allowed and whose context window is big enough for the request.

            **Your job:** write `choose(models, required_tokens, banned)` so that it gives back the name
            of that model.

            **What goes in**
            - `models`: a list of `(name, context_window)` tuples in order of preference, for example
              `[("mini", 8000), ("std", 32000)]`
            - `required_tokens`: a whole number, for example `10000`
            - `banned`: a set of model names that must not be chosen, for example `{"std"}`. It may be
              the empty set, `set()`.

            **What comes out**
            - the name (a string) of the first model whose context window is at least `required_tokens`
              and whose name is not in `banned`, or `None` when there is no such model

            **Rules**
            - A window that is exactly equal to `required_tokens` is big enough.
            - A banned model is skipped, even when it would fit.
            - The result is `None` when nothing fits, when every model is banned, and when `models` is
              empty.
            - Use a `for` loop with an `else` block. A `for` loop may have an `else`, and that block runs
              only when the loop ended without a `break`. It handles the case "nothing found". A check
              looks for it.

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
            "Check the arguments first. Then use a `while` loop with a start position that moves forward by `size - overlap`.",
            "Each iteration slices one chunk from the start position. When that chunk reaches the end of the list, stop. Otherwise move the start forward.",
            "Hand back an empty list for settings that make no sense. Work out the step as the size minus the overlap. While the start is inside the list: slice `size` items from the start, append the slice to the chunks, `break` when the end of that slice has reached the end of the list, and otherwise move the start forward by the step. After the loop, hand back the chunks.",
        ],
        "title": "Chunk with overlap",
        "difficulty": 3,
        "prompt": r'''
            Before the documents of a RAG app are turned into embeddings, they are split into pieces
            called chunks. The chunks overlap a little, so that an idea that is cut at the border of one
            chunk still appears whole in the next one.

            **Your job:** write `chunk(words, size, overlap)` so that it gives back the list of chunks.

            **What goes in**
            - `words`: a list of words, or of any other items, for example `["a", "b", "c", "d", "e"]`
            - `size`: a whole number, the number of words in a chunk, for example `3`
            - `overlap`: a whole number, the number of words that a chunk shares with the chunk before
              it, for example `1`

            **What comes out**
            - a list of lists: the chunks, in order

            **Rules**
            - The first chunk starts at position `0`. Each following chunk starts `size - overlap` words
              after the one before it.
            - Stop as soon as a chunk reaches the end of the list. Never add a last chunk that lies
              completely inside the chunk before it.
            - The last chunk may be shorter than `size`.
            - Settings that make no sense give `[]`: a `size` of 0 or less, a negative `overlap`, and an
              `overlap` that is equal to `size` or greater.
            - An empty `words` list gives `[]`.

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
