TOPIC = {
    "id": "vectors",
    "title": "Vectors & Similarity",
    "track": "rag",
    "order": 1,
    "requires": ["comprehensions", "functions"],
    "summary": """
        The pure-Python math behind embeddings and RAG: dot products, norms,
        normalisation, cosine similarity, nearest-neighbour search, bag-of-words
        vectors, mean pooling and TF-IDF keyword scoring.
    """,
    "concepts": ["dot product", "L2 norm", "normalisation", "cosine similarity", "top-k search",
                 "bag of words", "mean pooling", "TF-IDF"],
}

LESSON = r'''
## Vectors & similarity - chapter notes

An **embedding** turns text into a **vector** (a list of numbers) so that similar meaning
gives vectors pointing in similar directions. RAG = embed every chunk once, embed the
question, rank chunks by similarity, paste the best ones into the prompt.

| name | formula (pure Python) | notes |
| --- | --- | --- |
| element-wise add | `[x + y for x, y in zip(a, b)]` | same for `-`, `*` |
| scale | `[x * f for x in v]` | new list, input unchanged |
| dot product | `sum(x * y for x, y in zip(a, b))` | grows with length too |
| norm / length (L2) | `math.sqrt(sum(x * x for x in v))` | `[3, 4]` -> `5.0` |
| normalise | `[x / n for x in v]` with `n = norm(v)` | result has norm 1; zero vector -> error |
| cosine similarity | `dot(a, b) / (norm(a) * norm(b))` | -1..1, direction only |
| Euclidean distance | `math.dist(a, b)` | smaller = closer |
| mean pooling | average position by position | one vector for many chunks |
| top-k | `sorted(..., key=lambda p: (-p[1], p[0]))[:k]` | best first, ties by id |

```python
import math

cat, kitten, invoice = [0.9, 0.8, 0.0], [0.8, 0.9, 0.1], [0.0, 0.1, 0.9]
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.hypot(*a) * math.hypot(*b))
print(round(cosine(cat, kitten), 2), round(cosine(cat, invoice), 2))
```

**Keyword side:** *bag of words* = counts over a fixed vocabulary; *TF-IDF* = term
frequency x `log(N / df)`, rewarding words that are frequent in a doc but rare overall.

**Gotchas**
- `zip` silently stops at the shorter list - check `len(a) != len(b)` and raise `ValueError`.
- A zero vector has norm 0: guard before dividing.
- Rank by cosine, not raw dot product (long vectors win unfairly), unless vectors are normalised.
- Compare floats with `math.isclose`, never `==`.
'''

EXERCISES = [
    {
        "id": "vectors-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            Imagine describing foods with three scores: *sweet*, *salty*, *spicy*. A cookie is
            `[0.9, 0.1, 0.0]`, a pretzel `[0.1, 0.9, 0.0]`. Foods that taste alike get similar lists.
            An **embedding** does the same for text: a model turns each sentence into a list of numbers
            (hundreds of them) so that sentences with similar *meaning* get similar numbers.

            A list of numbers like this is called a **vector**. In Python it's a plain list, and the
            tool for comparing two of them position by position is `zip`:

            ```python
            cookie = [0.9, 0.1, 0.0]
            cake = [0.8, 0.2, 0.1]
            print(list(zip(cookie, cake)))
            print([round(x * y, 2) for x, y in zip(cookie, cake)])
            ```

            `zip(a, b)` pairs item 0 with item 0, item 1 with item 1, and so on, giving tuples.

            Multiply each pair and add the results and you get the **dot product** - the most basic
            "how alike are these?" score. Bigger means the two vectors agree more.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            a = [1, 2, 3]
            b = [4, 5, 6]
            pairs = list(zip(a, b))
            print(pairs[0])
            print(sum(x * y for x, y in zip(a, b)))
        ''',
        "solution": r'''
            (1, 4)
            32
        ''',
        "explanation": r'''
            `zip(a, b)` pairs the numbers position by position: `(1, 4)`, `(2, 5)`, `(3, 6)`.
            The first pair is `(1, 4)`. The second line is the **dot product**: multiply each
            pair and add: 1\*4 + 2\*5 + 3\*6 = 4 + 10 + 18 = 32.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`zip` pairs up items at the same position from both lists, as tuples.",
            "The first line prints the first tuple. The second multiplies each pair and adds all the products.",
            "Line 1: the first item of `a` with the first item of `b`, in parentheses. Line 2: compute 1*4, 2*5 and 3*6, then add them.",
        ],
    },
    {
        "id": "vectors-s2",
        "title": "Add two vectors",
        "difficulty": 0,
        "lesson": r'''
            Vectors are added **position by position**, like adding up two shopping receipts line by
            line: apples with apples, bread with bread. The result is a new vector of the same length.

            ```python
            monday = [2, 0, 1]
            tuesday = [1, 3, 0]
            total = [x + y for x, y in zip(monday, tuesday)]
            print(total)
            print(monday)
            ```

            This is a list comprehension over `zip`: for every pair `(x, y)`, compute one new number.
            The originals are untouched - you build a new list.

            The proper name is *element-wise* (or *component-wise*) addition. Subtraction and
            multiplication work the same way; only the operator changes. In RAG code you'll see this in
            averaging embeddings or moving a query vector towards a topic.
        ''',
        "prompt": r'''
            Adding two vectors means adding the numbers at the same position.

            **Write:** fill in the blank (`___`) in `add_vectors(a, b)`

            - `a`: a list of numbers, e.g. `[1, 2, 3]`
            - `b`: a list of numbers of the same length, e.g. `[10, 20, 30]`
            - **Returns:** a new list where each number is `a[i] + b[i]`, e.g. `[11, 22, 33]`

            **Rules**
            - Change only the `___`.
            - Works for floats and negative numbers too; two empty lists give `[]`.

            **Examples**
            ```python
            add_vectors([1, 2, 3], [10, 20, 30])   # returns [11, 22, 33]
            add_vectors([0.5, -1], [0.5, 1])       # returns [1.0, 0]
            add_vectors([], [])                    # returns []
            ```
        ''',
        "starter": r'''
            def add_vectors(a, b):
                return [x ___ y for x, y in zip(a, b)]
        ''',
        "tests": r'''
            from solution import add_vectors

            def test_adds_integers_position_by_position():
                got = add_vectors([1, 2, 3], [10, 20, 30])
                assert got == [11, 22, 33], f"got {got!r}"

            def test_negatives_and_floats():
                got = add_vectors([0.5, -1], [0.5, 1])
                assert got == [1.0, 0], f"got {got!r}"

            def test_empty_vectors_give_empty_list():
                assert add_vectors([], []) == []
        ''',
        "solution": r'''
            def add_vectors(a, b):
                return [x + y for x, y in zip(a, b)]
        ''',
        "hints": [
            "The blank sits between the two numbers of each pair.",
            "`zip` hands you one number from `a` (`x`) and one from `b` (`y`); you want their sum.",
            "Replace `___` with the addition operator.",
        ],
    },
    {
        "id": "vectors-s6",
        "title": "When lengths don't match",
        "difficulty": 0,
        "lesson": r'''
            `zip` has a quiet habit you must know about: when the two lists have **different lengths**,
            it stops at the end of the **shorter** one - no error, no warning. Like pairing dancers:
            if there are 3 on one side and 2 on the other, one person just sits out.

            ```python
            names = ["ana", "bo", "cy"]
            scores = [0.9, 0.4]
            for name, score in zip(names, scores):
                print(name, score)
            print(len(names), len(scores))
            ```

            For vectors this is dangerous. Two embeddings from **different models** often have different
            sizes (e.g. 768 vs 1536 numbers). `zip` would happily compute a meaningless result.

            That's why vector code checks `len(a) != len(b)` first and raises a `ValueError`. Failing
            loudly is better than a silent wrong answer - a principle called *fail fast*.
        ''',
        "mode": "predict",
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            a = [1, 2, 3]
            b = [10, 20]
            print(list(zip(a, b)))
            print(sum(x * y for x, y in zip(a, b)))
            print(len(a) == len(b))
        ''',
        "solution": r'''
            [(1, 10), (2, 20)]
            50
            False
        ''',
        "explanation": r'''
            `zip` stops when the **shorter** list runs out, so the `3` in `a` is silently
            dropped: only two pairs. The "dot product" then adds 1\*10 + 2\*20 = 50 - a number
            that looks fine but is meaningless. Only the explicit length check reveals the
            problem.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "How many pairs can `zip` make when one list has 3 items and the other has 2?",
            "`zip` stops at the end of the shorter list; the extra item is ignored without any error.",
            "Line 1: the two pairs as a list of tuples. Line 2: multiply each of those two pairs and add. Line 3: compare the two lengths.",
        ],
    },
    {
        "id": "vectors-s4",
        "title": "Scale a vector",
        "difficulty": 0,
        "lesson": r'''
            *Scaling* stretches or shrinks a vector: multiply **every** number by the same factor. Think of
            a recipe for 2 people scaled to 6: every ingredient times 3. The proportions - the vector's
            **direction** - stay the same; only its size changes.

            ```python
            recipe = [200, 3, 50]
            print([x * 3 for x in recipe])
            print([x * 0.5 for x in recipe])
            print(recipe)
            ```

            A number that multiplies a vector is called a *scalar* (it "scales" it). Multiplying by
            `0.5` halves the vector; by `-1` flips it to point the opposite way.

            Watch out: build a **new** list with a comprehension. Changing the numbers inside the list
            you were given (`v[i] = ...`) would surprise the caller, who may still need the original.
        ''',
        "prompt": r'''
            *Scaling* a vector multiplies every number in it by the same factor.

            **Write:** `scale(v, factor)`

            - `v`: a list of numbers, e.g. `[1, 2, 3]`
            - `factor`: a number, e.g. `2` or `0.5`
            - **Returns:** a **new** list with every number of `v` multiplied by `factor`

            **Rules**
            - Don't change the list `v` you were given.
            - An empty list returns `[]`.
            - Reminder: a list comprehension `[... for x in v]` builds a new list.

            **Examples**
            ```python
            scale([1, 2, 3], 2)     # returns [2, 4, 6]
            scale([4, -2], 0.5)     # returns [2.0, -1.0]
            scale([], 3)            # returns []
            ```
        ''',
        "starter": r'''
            def scale(v, factor):
                ...
        ''',
        "tests": r'''
            from solution import scale

            def test_factor_two_doubles_each_number():
                got = scale([1, 2, 3], 2)
                assert got == [2, 4, 6], f"got {got!r}"

            def test_factor_half_with_negatives():
                got = scale([4, -2], 0.5)
                assert got == [2.0, -1.0], f"got {got!r}"

            def test_empty_vector_gives_empty_list():
                assert scale([], 3) == []

            def test_input_list_is_not_changed():
                v = [1, 2]
                scale(v, 10)
                assert v == [1, 2], f"the input list was changed to {v}"
        ''',
        "solution": r'''
            def scale(v, factor):
                return [x * factor for x in v]
        ''',
        "hints": [
            "A list comprehension builds a new list from each item of `v`.",
            "For each number `x` in `v`, the new list should contain `x` times `factor`.",
            "Return a comprehension of the form [expression for x in v] where the expression multiplies `x` by `factor`.",
        ],
    },
    {
        "id": "vectors-s5",
        "title": "Vector length",
        "difficulty": 0,
        "lesson": r'''
            How long is a vector? For `[3, 4]`, picture walking 3 blocks east and 4 blocks north: the
            straight-line distance back home is 5 - Pythagoras. The same rule works in any number of
            dimensions: square each number, add the squares, take the square root.

            ```python
            import math

            v = [2, 3, 6]
            squares = [x * x for x in v]
            print(squares, sum(squares))
            print(math.sqrt(sum(squares)))
            ```

            This length is called the vector's **norm** or **magnitude** (precisely, the *L2 norm*).
            Squaring makes negative numbers count the same as positive ones.

            Why care? Two texts can point the same way but have very different lengths. Dividing by the
            norm later lets us compare **direction only** - that's where cosine similarity comes from.
        ''',
        "prompt": r'''
            An embedding is a vector (a list of numbers). Its *length* (also called its
            *norm* or *magnitude*) tells you how big it is.

            **Write:** `length(v)`

            - `v`: a list of numbers, e.g. `[3, 4]`
            - **Returns:** a float: the **square root of the sum of the squares** of the numbers in `v`

            **Rules**
            - Negative numbers count the same as positive ones (they are squared).
            - An empty list returns `0` (`0.0` is fine).
            - `math` is already imported; `math.sqrt(x)` gives a square root.
            - Results are compared with a small float tolerance (`math.isclose`), so tiny
              rounding differences are fine.

            **Examples**
            ```python
            length([3, 4])       # returns 5.0
            length([1, 2, 2])    # returns 3.0
            length([-3, -4])     # returns 5.0
            length([])           # returns 0.0
            ```
        ''',
        "starter": r'''
            import math


            def length(v):
                ...
        ''',
        "tests": r'''
            import math
            from solution import length

            def test_length_of_3_4_is_5():
                got = length([3, 4])
                assert math.isclose(got, 5.0), f"got {got!r}"

            def test_three_dimensional_vector():
                got = length([1, 2, 2])
                assert math.isclose(got, 3.0), f"got {got!r}"

            def test_negatives_are_squared():
                got = length([-3, -4])
                assert math.isclose(got, 5.0), f"got {got!r}"

            def test_empty_vector_has_length_zero():
                assert length([]) == 0
        ''',
        "solution": r'''
            import math


            def length(v):
                return math.sqrt(sum(x * x for x in v))
        ''',
        "hints": [
            "You need three things: squaring each number, `sum(...)`, and `math.sqrt(...)`.",
            "First square every number and add the squares up, then take the square root of that total.",
            "1) Build the squares with a comprehension (`x * x` for each x). 2) Wrap it in `sum(...)`. 3) Wrap that in `math.sqrt(...)` and return it.",
        ],
    },
    {
        "id": "vectors-s3",
        "title": "Fix the best-chunk picker",
        "difficulty": 0,
        "lesson": r'''
            Once every chunk has a similarity score, retrieval is simply "highest score wins". A dict
            `{chunk_id: score}` holds the scores, and `max` can pick the winner - if you tell it **what to
            compare**.

            ```python
            prices = {"apple": 0.5, "melon": 2.0, "grape": 1.2}
            print(max(prices))
            print(max(prices, key=prices.get))
            print(min(prices, key=prices.get))
            ```

            Looping over a dict gives its **keys**, so `max(prices)` compares the names alphabetically.
            With `key=prices.get`, `max` looks up each key's value and compares those instead, but still
            returns the **key**. `key=` takes a function - you met it in the sorting chapter.

            With similarity scores, bigger means more similar, so the best match is the maximum - even
            when every score is negative.
        ''',
        "prompt": r'''
            A retriever scored some chunks by similarity to the question. `best_chunk` should
            pick the best match, but it returns the worst one. Fix the bug.

            **Write:** fix `best_chunk(scores)`

            - `scores`: a dict mapping chunk id (`str`) to score (`float`), e.g. `{"c1": 0.12, "c2": 0.91}`
            - **Returns:** the id (`str`) of the chunk with the **highest** score

            **Rules**
            - Scores can be negative: the highest is still the one closest to `+infinity`
              (e.g. `-0.1` beats `-0.5`).
            - With a single chunk, return its id.

            **Examples**
            ```python
            best_chunk({"c1": 0.12, "c2": 0.91, "c3": 0.45})   # returns "c2"
            best_chunk({"a": -0.5, "b": -0.1, "c": -0.9})      # returns "b"
            best_chunk({"only": 0.3})                          # returns "only"
            ```
        ''',
        "starter": r'''
            def best_chunk(scores):
                return min(scores, key=scores.get)
        ''',
        "tests": r'''
            from solution import best_chunk

            def test_returns_id_with_highest_score():
                got = best_chunk({"c1": 0.12, "c2": 0.91, "c3": 0.45})
                assert got == "c2", f"got {got!r}"

            def test_negative_scores_highest_wins():
                got = best_chunk({"a": -0.5, "b": -0.1, "c": -0.9})
                assert got == "b", f"got {got!r}"

            def test_single_chunk_returns_its_id():
                assert best_chunk({"only": 0.3}) == "only"
        ''',
        "solution": r'''
            def best_chunk(scores):
                return max(scores, key=scores.get)
        ''',
        "hints": [
            "The `key=scores.get` part is right: it compares chunks by their score.",
            "The function picks the smallest score. You want the largest.",
            "Swap the built-in `min` for its opposite, keeping the same `key=` argument.",
        ],
    },
    {
        "id": "vectors-1",
        "hints": [
            'Pair the numbers with `zip`, multiply each pair and `sum` the products. Check the lengths first.',
            'If the two lengths differ, raise ValueError before doing any math. Otherwise add up x * y for every pair; `sum` of nothing is already 0.',
            '1) `if len(a) != len(b): raise ValueError(...)`. 2) Return `sum(...)` over a generator that multiplies each `x, y` from `zip(a, b)`.',
        ],
        "title": "Dot product",
        "difficulty": 1,
        "lesson": r'''
            Time to write the dot product yourself. Picture two people rating the same films from -1
            (hate) to 1 (love). Multiply their ratings film by film and add up: where both love or both
            hate a film, the product is positive and pushes the total up; where they disagree, it's
            negative and pulls it down. A high total means similar taste.

            ```python
            ana = [1, -1, 0.5]
            bo = [1, -0.5, 1]
            products = [x * y for x, y in zip(ana, bo)]
            print(products)
            print(sum(products))
            ```

            That total is the **dot product**, written `a · b`. It's the core operation of every vector
            database; GPUs compute billions of them per second.

            `sum` of an empty sequence is `0`, so two empty vectors give `0` without any special case.
            And remember the `zip` trap: check the lengths first and raise `ValueError` if they differ.
        ''',
        "prompt": r'''
            The *dot product* is the basic building block of embedding similarity: it
            multiplies two vectors position by position and adds up the results.

            **Write:** `dot(a, b)`

            - `a`: a list of numbers, e.g. `[1, 2, 3]`
            - `b`: a list of numbers, e.g. `[4, 5, 6]`
            - **Returns:** a number: `a[0]*b[0] + a[1]*b[1] + ...` (for the example, `4 + 10 + 18 = 32`)

            **Rules**
            - If `a` and `b` have different lengths (either one longer), raise `ValueError`.
            - Two empty lists give `0`.
            - Float results are compared with a small tolerance (`math.isclose`).

            **Examples**
            ```python
            dot([1, 2, 3], [4, 5, 6])   # returns 32
            dot([0.5, -1], [2, 3])      # returns -2.0
            dot([], [])                 # returns 0
            dot([1, 2], [1])            # raises ValueError
            ```
        ''',
        "starter": r'''
            def dot(a, b):
                ...
        ''',
        "tests": r'''
            import math
            from solution import dot

            def test_integer_vectors():
                assert dot([1, 2, 3], [4, 5, 6]) == 32, f"got {dot([1, 2, 3], [4, 5, 6])!r}"

            def test_floats_and_negatives():
                got = dot([0.5, -1], [2, 3])
                assert math.isclose(got, -2.0), f"got {got!r}"

            def test_empty_vectors_give_zero():
                assert dot([], []) == 0, f"got {dot([], [])!r}"

            def test_different_lengths_raise_value_error():
                for a, b in (([1, 2], [1]), ([1], [1, 2])):
                    try:
                        dot(a, b)
                    except ValueError:
                        continue
                    raise AssertionError(f"dot({a}, {b}) should raise ValueError")
        ''',
        "solution": r'''
            def dot(a, b):
                if len(a) != len(b):
                    raise ValueError("vectors must have the same length")
                return sum(x * y for x, y in zip(a, b))
        ''',
    },
    {
        "id": "vectors-2",
        "hints": [
            'Norm: square root of the sum of squares (`math.sqrt`). Normalise: divide every number by the norm.',
            'Write `norm` first, then reuse it in `normalize`. Raise ValueError when the norm is 0 instead of dividing by zero, and build a new list with a comprehension.',
            '1) `norm`: `math.sqrt(sum(x * x for x in v))` (the empty sum is 0, so `norm([])` is 0.0). 2) `normalize`: compute `n = norm(v)`; if `n == 0` raise ValueError; return `[x / n for x in v]`.',
        ],
        "title": "Norm and unit vectors",
        "difficulty": 1,
        "lesson": r'''
            A *unit vector* has length exactly 1 - like shrinking every arrow on a map to the same size so
            only the **direction** is left. To get it, divide every number by the vector's norm. This is
            called *normalising* the vector.

            ```python
            import math

            v = [6, 8]
            n = math.sqrt(sum(x * x for x in v))
            unit = [x / n for x in v]
            print(n, unit)
            print(math.sqrt(sum(x * x for x in unit)))
            ```

            Why vector databases love this: for unit vectors, the plain dot product **equals** cosine
            similarity, so search only needs the cheap dot product. Many embedding APIs return vectors
            that are already normalised.

            Watch out: a *zero vector* (all zeros) has norm 0 and no direction at all - dividing would
            raise `ZeroDivisionError`. Check first and raise a clear `ValueError` instead.
        ''',
        "prompt": r'''
            Many vector databases store embeddings *normalised* to length 1, so that a plain
            dot product equals cosine similarity.

            **Write:** two functions, `norm(v)` and `normalize(v)`

            - `v`: a list of numbers, e.g. `[3, 4]`
            - `norm(v)` **returns:** a float, the *L2 norm* (magnitude) of `v`: the square root
              of the sum of the squares of its numbers
            - `normalize(v)` **returns:** a **new** list: every number of `v` divided by `norm(v)`,
              so the result points the same way and has norm `1.0`

            **Rules**
            - `norm([])` returns `0.0`.
            - `normalize` of a *zero vector* (norm 0, e.g. `[0, 0]` or `[]`) raises `ValueError`.
            - `normalize` must not change the list it was given.
            - Results are compared with a small float tolerance (`math.isclose`); do not round.

            **Examples**
            ```python
            norm([3, 4])             # returns 5.0
            norm([-1, -2, 2])        # returns 3.0
            norm([])                 # returns 0.0
            normalize([3, 4])        # returns [0.6, 0.8]
            normalize([0, -2, 0])    # returns [0.0, -1.0, 0.0]
            normalize([0, 0])        # raises ValueError
            ```
        ''',
        "starter": r'''
            import math


            def norm(v):
                ...


            def normalize(v):
                ...
        ''',
        "tests": r'''
            import math
            from solution import norm, normalize

            def close_lists(a, b):
                return len(a) == len(b) and all(math.isclose(x, y, abs_tol=1e-9) for x, y in zip(a, b))

            def test_norm_of_3_4_is_5():
                assert math.isclose(norm([3, 4]), 5.0), f"got {norm([3, 4])!r}"

            def test_norm_with_negatives():
                got = norm([-1, -2, 2])
                assert math.isclose(got, 3.0), f"got {got!r}"

            def test_norm_of_empty_vector_is_zero():
                assert norm([]) == 0.0, f"got {norm([])!r}"

            def test_normalize_divides_each_number_by_norm():
                got = normalize([3, 4])
                assert close_lists(got, [0.6, 0.8]), f"got {got!r}"
                got = normalize([0, -2, 0])
                assert close_lists(got, [0.0, -1.0, 0.0]), f"got {got!r}"

            def test_normalized_has_unit_norm_and_input_untouched():
                v = [1.5, -2.0, 7.25, 0.1]
                got = normalize(v)
                assert math.isclose(math.sqrt(sum(x * x for x in got)), 1.0), "result does not have norm 1"
                assert v == [1.5, -2.0, 7.25, 0.1], "the input list was modified"

            def test_normalize_zero_or_empty_vector_raises_value_error():
                for v in ([0, 0], []):
                    try:
                        normalize(v)
                    except ValueError:
                        continue
                    raise AssertionError(f"normalize({v}) should raise ValueError")
        ''',
        "solution": r'''
            import math


            def norm(v):
                return math.sqrt(sum(x * x for x in v))


            def normalize(v):
                n = norm(v)
                if n == 0:
                    raise ValueError("cannot normalise a zero vector")
                return [x / n for x in v]
        ''',
    },
    {
        "id": "vectors-7",
        "title": "Euclidean distance",
        "difficulty": 1,
        "lesson": r'''
            Similarity asks "do they point the same way?". **Distance** asks "how far apart are the two
            points?" - like measuring with a ruler between two pins on a map. Small distance = close =
            similar. Some vector databases rank by distance instead of cosine.

            It's the norm from before, applied to the **difference** of the two vectors: subtract
            position by position, square, add, square root.

            ```python
            import math

            home, shop = [1, 1], [4, 5]
            diff = [x - y for x, y in zip(home, shop)]
            print(diff)
            print(math.sqrt(sum(d * d for d in diff)))
            ```

            This is called the *Euclidean* (or *L2*) distance. Identical vectors have distance `0`;
            order doesn't matter (`a` to `b` is as far as `b` to `a`).

            The standard library can already do this in one call. Finding which function is this step's
            research task - reading the docs of the `math` module is a habit worth building.
        ''',
        "research": {
            "note": "The `math` module has a function that computes the Euclidean distance between two points in one call. Read its entry (and what it does when the points have different lengths), then come back.",
            "links": [
                {"title": "math.dist - Python docs", "url": "https://docs.python.org/3/library/math.html#math.dist"},
            ],
        },
        "prompt": r'''
            Some vector stores rank results by distance instead of similarity. Compute the
            straight-line distance between two embeddings.

            **Write:** `distance(a, b)`

            - `a`: a list of numbers, e.g. `[0, 0]`
            - `b`: a list of numbers, e.g. `[3, 4]`
            - **Returns:** a `float`, the *Euclidean distance*: the square root of the sum of
              `(a[i] - b[i]) ** 2` over every position, e.g. `5.0`

            **Rules**
            - If `a` and `b` have different lengths, raise `ValueError`.
            - Two empty lists give `0.0`.
            - Results are compared with a small float tolerance (`math.isclose`).

            **Examples**
            ```python
            distance([0, 0], [3, 4])         # returns 5.0
            distance([1, 2, 3], [1, 2, 3])   # returns 0.0
            distance([-1, -1], [2, 3])       # returns 5.0
            distance([1, 2], [1])            # raises ValueError
            ```
        ''',
        "starter": r'''
            import math


            def distance(a, b):
                ...
        ''',
        "tests": r'''
            import math
            from solution import distance

            def test_distance_3_4_5():
                got = distance([0, 0], [3, 4])
                assert math.isclose(got, 5.0), f"got {got!r}"

            def test_identical_vectors_have_distance_zero():
                got = distance([1, 2, 3], [1, 2, 3])
                assert math.isclose(got, 0.0, abs_tol=1e-12), f"got {got!r}"

            def test_negatives_and_order_does_not_matter():
                assert math.isclose(distance([-1, -1], [2, 3]), 5.0), f"got {distance([-1, -1], [2, 3])!r}"
                assert math.isclose(distance([2, 3], [-1, -1]), 5.0), "distance must be the same both ways"

            def test_empty_vectors_give_zero():
                assert distance([], []) == 0.0

            def test_different_lengths_raise_value_error():
                for a, b in (([1, 2], [1]), ([1], [1, 2])):
                    try:
                        distance(a, b)
                    except ValueError:
                        continue
                    raise AssertionError(f"distance({a}, {b}) should raise ValueError")
        ''',
        "solution": r'''
            import math


            def distance(a, b):
                if len(a) != len(b):
                    raise ValueError("vectors must have the same length")
                return math.dist(a, b)
        ''',
        "hints": [
            "Either use the `math` function from the research link, or build it from subtraction, squares, `sum` and `math.sqrt`.",
            "Check the lengths first and raise `ValueError` if they differ. Then compute the length of the difference vector.",
            "1) `if len(a) != len(b): raise ValueError(...)`. 2) Return `math.dist(a, b)` - or `math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))`.",
        ],
    },
    {
        "id": "vectors-8",
        "title": "Mean pooling",
        "difficulty": 1,
        "lesson": r'''
            A long document is split into chunks, and each chunk gets its own embedding. Sometimes you
            want **one** vector for the whole document. The simplest way: average the chunk vectors
            position by position - like averaging a class's test scores subject by subject to get the
            "typical student".

            ```python
            scores = [[10, 20], [14, 16], [12, 18]]
            firsts = [row[0] for row in scores]
            print(firsts, sum(firsts) / len(firsts))
            columns = list(zip(*scores))
            print(columns)
            ```

            `zip(*scores)` is a neat trick: the `*` *unpacks* the list, so it's the same as
            `zip([10, 20], [14, 16], [12, 18])`, which walks all rows together and gives you one tuple
            per **position** (a *column*). Averaging each column gives the mean vector.

            In embedding jargon this is called **mean pooling**. Watch out: averaging zero vectors is
            dividing by zero, and rows of different lengths would be cut short by `zip` - both deserve
            a `ValueError`.
        ''',
        "prompt": r'''
            Turn a document's chunk embeddings into one document embedding by averaging them.

            **Write:** `mean_vector(vectors)`

            - `vectors`: a `list` of vectors (lists of numbers), all the same length, e.g.
              `[[4, 0], [0, 1]]`
            - **Returns:** a **new** list of floats: position `i` is the average of `v[i]` over
              all the vectors, e.g. `[2.0, 0.5]`

            **Rules**
            - An empty `vectors` list raises `ValueError`.
            - If the vectors don't all have the same length, raise `ValueError`.
            - Don't change the input lists.
            - Results are compared with a small float tolerance (`math.isclose`).

            **Examples**
            ```python
            mean_vector([[4, 0], [0, 1]])            # returns [2.0, 0.5]
            mean_vector([[1, 2, 3]])                 # returns [1.0, 2.0, 3.0]
            mean_vector([[1, -1], [3, 1], [2, 3]])   # returns [2.0, 1.0]
            mean_vector([])                          # raises ValueError
            mean_vector([[1, 2], [1]])               # raises ValueError
            ```
        ''',
        "starter": r'''
            def mean_vector(vectors):
                ...
        ''',
        "tests": r'''
            import math
            from solution import mean_vector

            def close_lists(a, b):
                return len(a) == len(b) and all(math.isclose(x, y, abs_tol=1e-9) for x, y in zip(a, b))

            def test_average_of_two_vectors():
                got = mean_vector([[4, 0], [0, 1]])
                assert close_lists(got, [2.0, 0.5]), f"got {got!r}"

            def test_single_vector_is_its_own_mean():
                got = mean_vector([[1, 2, 3]])
                assert close_lists(got, [1.0, 2.0, 3.0]), f"got {got!r}"

            def test_three_vectors_with_negatives():
                got = mean_vector([[1, -1], [3, 1], [2, 3]])
                assert close_lists(got, [2.0, 1.0]), f"got {got!r}"

            def test_empty_or_uneven_input_raises_value_error():
                for bad in ([], [[1, 2], [1]], [[1], [1, 2]]):
                    try:
                        mean_vector(bad)
                    except ValueError:
                        continue
                    raise AssertionError(f"mean_vector({bad}) should raise ValueError")

            def test_input_is_not_changed():
                data = [[4, 0], [0, 1]]
                mean_vector(data)
                assert data == [[4, 0], [0, 1]], f"input changed to {data}"
        ''',
        "solution": r'''
            def mean_vector(vectors):
                if not vectors:
                    raise ValueError("need at least one vector")
                size = len(vectors[0])
                if any(len(v) != size for v in vectors):
                    raise ValueError("vectors must have the same length")
                return [sum(column) / len(vectors) for column in zip(*vectors)]
        ''',
        "hints": [
            "Validate first (empty list, uneven lengths), then average each position across all vectors.",
            "Compare every vector's length with the first one's. For the averages, walk the positions (columns) with `zip(*vectors)` or with an index loop.",
            "1) If `not vectors`, raise ValueError. 2) If any `len(v)` differs from `len(vectors[0])`, raise ValueError. 3) Return `[sum(col) / len(vectors) for col in zip(*vectors)]`.",
        ],
    },
    {
        "id": "vectors-9",
        "title": "Top-k results",
        "difficulty": 1,
        "lesson": r'''
            A retriever rarely wants just **the** best chunk - it wants the best **k** (say 3), to give
            the model a few sources. That's a podium: sort everyone by score, best first, and keep the
            first k places.

            Two details make it reliable:
            - **Best first** means sorting by score descending.
            - **Ties** need a rule, or results could come out in a different order each run. A common
              rule: equal scores are ordered by id, A to Z.

            A key function can return a **tuple**; Python compares tuples item by item. Negating a
            number flips its order, so `(-score, name)` means "score high to low, then name A to Z":

            ```python
            runners = {"cy": 9.5, "ana": 9.8, "bo": 9.5}
            podium = sorted(runners.items(), key=lambda item: (-item[1], item[0]))
            print(podium)
            print(podium[:2])
            ```

            `dict.items()` gives `(key, value)` pairs, and slicing `[:k]` keeps the first k (a slice past
            the end simply returns everything). This pattern is called **top-k** retrieval.
        ''',
        "prompt": r'''
            A retriever has scored every chunk. Return the best `k` for the prompt.

            **Write:** `top_k(scores, k)`

            - `scores`: a dict mapping chunk id (`str`) to score (`float`), e.g.
              `{"c1": 0.2, "c2": 0.9, "c3": 0.5}`
            - `k`: an `int`, how many results to keep, e.g. `2`
            - **Returns:** a `list` of `(chunk_id, score)` tuples, highest score first, e.g.
              `[("c2", 0.9), ("c3", 0.5)]`

            **Rules**
            - Equal scores are ordered by chunk id A->Z.
            - If `k` is larger than the number of chunks, return them all.
            - `k <= 0` or an empty dict returns `[]`.
            - Don't change `scores`.

            **Examples**
            ```python
            top_k({"c1": 0.2, "c2": 0.9, "c3": 0.5}, 2)   # returns [("c2", 0.9), ("c3", 0.5)]
            top_k({"b": 0.5, "a": 0.5, "c": 0.1}, 2)      # returns [("a", 0.5), ("b", 0.5)]
            top_k({"x": 0.3}, 5)                          # returns [("x", 0.3)]
            top_k({"x": 0.3}, 0)                          # returns []
            ```
        ''',
        "starter": r'''
            def top_k(scores, k):
                ...
        ''',
        "tests": r'''
            from solution import top_k

            def test_best_k_highest_first():
                got = top_k({"c1": 0.2, "c2": 0.9, "c3": 0.5}, 2)
                assert got == [("c2", 0.9), ("c3", 0.5)], f"got {got!r}"

            def test_ties_ordered_by_id():
                got = top_k({"b": 0.5, "a": 0.5, "c": 0.1, "d": 0.5}, 3)
                assert got == [("a", 0.5), ("b", 0.5), ("d", 0.5)], f"got {got!r}"

            def test_k_larger_than_chunks_returns_all():
                got = top_k({"x": 0.3, "y": -0.2}, 5)
                assert got == [("x", 0.3), ("y", -0.2)], f"got {got!r}"

            def test_zero_or_negative_k_and_empty_dict_return_empty_list():
                assert top_k({"x": 0.3}, 0) == []
                assert top_k({"x": 0.3}, -1) == []
                assert top_k({}, 3) == []

            def test_scores_dict_not_changed():
                scores = {"a": 0.1, "b": 0.2}
                top_k(scores, 1)
                assert scores == {"a": 0.1, "b": 0.2}, f"scores changed to {scores}"
        ''',
        "solution": r'''
            def top_k(scores, k):
                if k <= 0:
                    return []
                ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
                return ranked[:k]
        ''',
        "hints": [
            "Sort the `(id, score)` pairs from `.items()` with a key function, then slice.",
            "Use a tuple key: the negated score first (so high scores come first), then the id for ties. Handle `k <= 0` before slicing - a negative slice would mean something else.",
            "1) If `k <= 0`, return `[]`. 2) `ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))`. 3) Return `ranked[:k]`.",
        ],
    },
    {
        "id": "vectors-3",
        "hints": [
            'Cosine similarity = dot product / (norm of a * norm of b).',
            'Check the lengths first. Compute both norms; if either is 0, return 0.0 early. Otherwise divide the dot product by the product of the norms.',
            "1) Raise ValueError if `len(a) != len(b)`. 2) `na` and `nb` = square root of each vector's sum of squares. 3) If `na == 0 or nb == 0`, return 0.0. 4) Return `sum(x * y for x, y in zip(a, b)) / (na * nb)`.",
        ],
        "title": "Cosine similarity",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: **cosine similarity** is the dot product of two vectors divided by both
            their lengths. The division removes "how long" and keeps "which direction", so the score is
            always between `-1` (opposite) and `1` (same direction), with `0` meaning unrelated. It's the
            default similarity for embeddings.

            ```python
            import math

            a, b = [1, 2], [2, 4]
            dot = sum(x * y for x, y in zip(a, b))
            print(dot / (math.sqrt(5) * math.sqrt(20)))
            ```
        ''',
        "placement": True,
        "prompt": r'''
            RAG retrievers compare a question's embedding with chunk embeddings using
            *cosine similarity*: how closely two vectors point in the same direction,
            ignoring how long they are.

            **Write:** `cosine_similarity(a, b)`

            - `a`: a list of numbers, e.g. `[1, 0]`
            - `b`: a list of numbers of the same length, e.g. `[1, 1]`
            - **Returns:** a float between `-1.0` and `1.0`: the dot product of `a` and `b`
              divided by (length of `a` × length of `b`), where a vector's length is the square
              root of the sum of its squares

            **Rules**
            - If `a` and `b` have different lengths, raise `ValueError`.
            - If either vector is a *zero vector* (all zeros, or empty), return exactly `0.0`
              (don't divide by zero).
            - Same direction gives `1.0`, opposite gives `-1.0`, perpendicular gives `0.0`.
            - Results are compared with a small float tolerance (`math.isclose`); do not round.

            **Examples**
            ```python
            cosine_similarity([1, 0], [1, 1])     # returns 0.7071067811865475  (1 / sqrt(2))
            cosine_similarity([1, 2], [2, 4])     # returns 1.0 (same direction)
            cosine_similarity([1, 0], [-1, 0])    # returns -1.0
            cosine_similarity([0, 0], [1, 1])     # returns 0.0 (zero vector)
            cosine_similarity([], [])             # returns 0.0
            cosine_similarity([1, 2, 3], [1, 2])  # raises ValueError
            ```
        ''',
        "starter": r'''
            import math


            def cosine_similarity(a, b):
                ...
        ''',
        "tests": r'''
            import math
            from solution import cosine_similarity as cos

            def test_forty_five_degrees_gives_0_707():
                got = cos([1, 0], [1, 1])
                assert math.isclose(got, 1 / math.sqrt(2)), f"got {got!r}"

            def test_same_direction_different_length_gives_one():
                got = cos([1, 2], [2, 4])
                assert math.isclose(got, 1.0), f"got {got!r}"

            def test_opposite_gives_minus_one_and_perpendicular_gives_zero():
                assert math.isclose(cos([1, 0], [-1, 0]), -1.0), f"got {cos([1, 0], [-1, 0])!r}"
                assert math.isclose(cos([1, 0], [0, 5]), 0.0, abs_tol=1e-12), f"got {cos([1, 0], [0, 5])!r}"

            def test_three_dimensional_float_vectors():
                got = cos([0.2, 0.9, -0.4], [0.5, 0.1, 0.3])
                assert math.isclose(got, 0.07 / math.sqrt(1.01 * 0.35), rel_tol=1e-9), f"got {got!r}"

            def test_zero_vectors_give_zero():
                assert cos([0, 0], [1, 1]) == 0.0
                assert cos([3, 4], [0, 0]) == 0.0
                assert cos([], []) == 0.0

            def test_different_lengths_raise_value_error():
                try:
                    cos([1, 2, 3], [1, 2])
                except ValueError:
                    return
                raise AssertionError("different lengths should raise ValueError")
        ''',
        "solution": r'''
            import math


            def cosine_similarity(a, b):
                if len(a) != len(b):
                    raise ValueError("vectors must have the same length")
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(y * y for y in b))
                if na == 0 or nb == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (na * nb)
        ''',
    },
    {
        "id": "vectors-4",
        "hints": [
            'Tokenise with `.lower()`, `.split()` and `.strip(chars)`, count with a dict, then read the counts in vocab order.',
            'Build a word -> count dict from the cleaned tokens (skipping empty ones). Then make a list with one count per vocab word, 0 if it never appeared.',
            '1) Loop over `text.lower().split()`. 2) `token = raw.strip(".,!?;:\\"\'()")`; skip if empty. 3) `counts[token] = counts.get(token, 0) + 1`. 4) Return `[counts.get(word, 0) for word in vocab]`.',
        ],
        "title": "Bag of words",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: before neural embeddings, a text's vector was simply **word counts** over
            a fixed vocabulary - a *bag of words* (order is thrown away, like tipping words into a bag).
            Clean the tokens first (lowercase, strip punctuation), then count.

            ```python
            words = "the cat and the hat".split()
            vocab = ["cat", "the", "dog"]
            print([words.count(w) for w in vocab])
            ```
        ''',
        "prompt": r'''
            Before neural embeddings, text was turned into *count vectors* over a fixed
            vocabulary (a *bag of words*): one number per vocabulary word.

            **Write:** `bag_of_words(text, vocab)`

            - `text`: a string, e.g. `"The cat saw the DOG. Cat!"`
            - `vocab`: a list of lowercase words, e.g. `["cat", "dog", "the"]`
            - **Returns:** a list of ints, the same length as `vocab`, where position `i` is how
              many times `vocab[i]` occurs in `text`, e.g. `[2, 1, 2]`

            **Rules**
            - Tokenise like this: lowercase `text`, split it on whitespace, then remove these
              characters from **both ends** of every token: `.` `,` `!` `?` `;` `:` `"` `'` `(` `)`.
              Drop tokens that become empty.
            - Only whole tokens count: `"category"` does not count as `"cat"`.
            - Words not in `vocab` are ignored.
            - The result follows the order of `vocab`; a vocab word that never appears gets `0`.
            - Empty `text` gives all zeros; an empty `vocab` gives `[]`.

            **Examples**
            ```python
            vocab = ["cat", "dog", "the"]
            bag_of_words("The cat saw the DOG. Cat!", vocab)   # returns [2, 1, 2]
            bag_of_words('("dog") dog? "cat", cat;', vocab)    # returns [2, 2, 0]
            bag_of_words("category dogma theme", vocab)        # returns [0, 0, 0]
            bag_of_words("dog dog cat", ["dog", "llm", "cat"]) # returns [2, 0, 1]
            bag_of_words("", vocab)                            # returns [0, 0, 0]
            ```
        ''',
        "starter": r'''
            def bag_of_words(text, vocab):
                ...
        ''',
        "tests": r'''
            from solution import bag_of_words

            VOCAB = ["cat", "dog", "the"]

            def test_counts_are_case_insensitive():
                got = bag_of_words("The cat saw the DOG. Cat!", VOCAB)
                assert got == [2, 1, 2], f"got {got!r}"

            def test_empty_text_gives_all_zeros():
                assert bag_of_words("", VOCAB) == [0, 0, 0]

            def test_punctuation_stripped_both_ends():
                got = bag_of_words('("dog") dog? "cat", cat;', VOCAB)
                assert got == [2, 2, 0], f"got {got!r}"

            def test_only_whole_tokens_count():
                got = bag_of_words("category dogma theme", VOCAB)
                assert got == [0, 0, 0], f"got {got!r} - only whole tokens count"

            def test_vector_follows_vocab_order():
                got = bag_of_words("dog dog cat", ["dog", "llm", "cat"])
                assert got == [2, 0, 1], f"got {got!r}"

            def test_empty_vocab_gives_empty_list():
                assert bag_of_words("some text", []) == []
        ''',
        "solution": r'''
            def bag_of_words(text, vocab):
                counts = {}
                for raw in text.lower().split():
                    token = raw.strip(".,!?;:\"'()")
                    if token:
                        counts[token] = counts.get(token, 0) + 1
                return [counts.get(word, 0) for word in vocab]
        ''',
    },
    {
        "id": "vectors-5",
        "research": {
            "note": "This is how real RAG search works. Skim how an embeddings API is used for search (what comes back, and which similarity it recommends), then build the pure-Python version.",
            "links": [
                {"title": "Embeddings guide - OpenAI docs", "url": "https://platform.openai.com/docs/guides/embeddings"},
            ],
        },
        "hints": [
            'Break it into helpers: mean pooling of a list of vectors, cosine similarity, then sort and slice.',
            'Mean pooling: `zip(*chunks)` gives you each column; average each column. Score every non-empty document, sort by score descending then id ascending, and keep the first k.',
            '1) Return [] if k <= 0. 2) For each doc with chunks: pooled = `[sum(col) / len(chunks) for col in zip(*chunks)]`. 3) Score = cosine(query, pooled), 0.0 for zero vectors. 4) Sort with `key=lambda item: (-item[1], item[0])`. 5) Return `scored[:k]`.',
        ],
        "title": "Top-k document search",
        "difficulty": 3,
        "prompt": r'''
            In a RAG index each document is stored as several **chunk embeddings**. Find the
            documents that best match a query embedding.

            **Write:** `search(query, docs, k)`

            - `query`: a vector (list of numbers), e.g. `[1, 0]`
            - `docs`: a dict mapping `doc_id` (`str`) to a **list of chunk vectors**, all with the
              same length as `query`, e.g. `{"a": [[1, 0], [1, 0]], "c": [[0, 1]]}`
            - `k`: an `int`, how many results to return, e.g. `2`
            - **Returns:** a list of `(doc_id, score)` tuples, best first, e.g. `[("a", 1.0), ("b", 0.447...)]`

            **Rules**
            - A document's vector is the **mean pooling** of its chunks: the average of the
              chunks position by position (e.g. `[[4, 0], [0, 1]]` pools to `[2.0, 0.5]`).
            - A document's score is the cosine similarity between `query` and its pooled vector
              (dot product / (length × length)). If either vector is all zeros, the score is `0.0`.
            - Documents with an empty chunk list are skipped (not in the result at all).
            - Sort by score, highest first; equal scores are ordered by `doc_id` A→Z.
            - Return only the first `k`; if `k` is larger than the number of documents, return
              them all. `k <= 0` returns `[]`.
            - Scores are compared with a tolerance of `1e-9`; do not round them.

            **Examples**
            ```python
            docs = {
                "a": [[1, 0], [1, 0]],     # pooled -> [1.0, 0.0]
                "b": [[0, 1], [1, 1]],     # pooled -> [0.5, 1.0]
                "c": [[0, 1]],
            }
            search([1, 0], docs, 2)    # returns [("a", 1.0), ("b", 0.4472135954999579)]
            search([0, 1], docs, 10)   # returns [("c", 1.0), ("b", 0.8944271909999159), ("a", 0.0)]
            search([1, 0], {"m": [[5, 0]], "z": [[2, 0]]}, 2)   # returns [("m", 1.0), ("z", 1.0)]
            search([1, 0], {"empty": [], "zero": [[0, 0]]}, 5)  # returns [("zero", 0.0)]
            search([1, 0], docs, 0)    # returns []
            ```
        ''',
        "starter": r'''
            import math


            def search(query, docs, k):
                ...
        ''',
        "tests": r'''
            import math
            from solution import search

            DOCS = {
                "a": [[1, 0], [1, 0]],
                "b": [[0, 1], [1, 1]],
                "c": [[0, 1]],
            }

            def check(got, expected):
                assert [d for d, _ in got] == [d for d, _ in expected], f"got ids {[d for d, _ in got]!r}"
                for (d, s), (_, e) in zip(got, expected):
                    assert math.isclose(s, e, abs_tol=1e-9), f"score for {d} was {s!r}"

            def test_top_two_documents_with_cosine_scores():
                got = search([1, 0], DOCS, 2)
                check(got, [("a", 1.0), ("b", 0.5 / math.sqrt(1.25))])

            def test_chunks_are_mean_pooled():
                # mean of [4,0] and [0,1] is [2, 0.5]; summing/only-first-chunk would score differently
                docs = {"x": [[4, 0], [0, 1]], "y": [[1, 1]]}
                got = search([1, 0], docs, 2)
                check(got, [("x", 2 / math.sqrt(4.25)), ("y", 1 / math.sqrt(2))])

            def test_k_larger_than_docs_returns_all_sorted():
                got = search([0, 1], DOCS, 10)
                check(got, [("c", 1.0), ("b", 1.0 / math.sqrt(1.25)), ("a", 0.0)])

            def test_equal_scores_ordered_by_doc_id():
                docs = {"z": [[2, 0]], "m": [[5, 0]], "q": [[3, 4]]}
                got = search([1, 0], docs, 3)
                check(got, [("m", 1.0), ("z", 1.0), ("q", 0.6)])

            def test_empty_docs_skipped_and_zero_vectors_score_zero():
                docs = {"empty": [], "zero": [[0, 0]], "one": [[3, 1]]}
                got = search([1, 0], docs, 5)
                assert [d for d, _ in got] == ["one", "zero"], f"got {got!r}"
                assert got[1][1] == 0.0

            def test_k_zero_returns_empty_list():
                assert search([1, 0], DOCS, 0) == []
        ''',
        "solution": r'''
            import math


            def _mean_pool(vectors):
                n = len(vectors)
                return [sum(column) / n for column in zip(*vectors)]


            def _cosine(a, b):
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(y * y for y in b))
                if na == 0 or nb == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (na * nb)


            def search(query, docs, k):
                if k <= 0:
                    return []
                scored = [
                    (doc_id, _cosine(query, _mean_pool(chunks)))
                    for doc_id, chunks in docs.items()
                    if chunks
                ]
                scored.sort(key=lambda item: (-item[1], item[0]))
                return scored[:k]
        ''',
    },
    {
        "id": "vectors-6",
        "hints": [
            'Tokenise every document once, compute an idf per unique query term, then a score per document.',
            "`df` is how many documents contain the term; `idf = math.log(N / df)` (0 if df is 0). A document's score sums `count / length * idf` over the unique query terms. Keep only positive scores.",
            '1) `tokenised = {id: text.lower().split()}`. 2) `terms = set(query.lower().split())`. 3) For each term, count docs containing it and compute idf. 4) For each non-empty doc: score = sum of `tokens.count(t) / len(tokens) * idf[t]`. 5) Keep score > 0, sort by (-score, id).',
        ],
        "title": "TF-IDF keyword scoring",
        "difficulty": 3,
        "prompt": r'''
            Hybrid RAG systems combine embeddings with keyword scores. *TF-IDF* rewards
            documents that use the query's words often (*term frequency*) and prefers words that
            are rare across all documents (*inverse document frequency*).

            **Write:** `tfidf_rank(query, docs)`

            - `query`: a string, e.g. `"the cat"`
            - `docs`: a dict mapping `doc_id` (`str`) to its text (`str`), e.g. `{"d1": "the cat sat"}`
            - **Returns:** a list of `(doc_id, score)` tuples (score is a float), best first

            **Rules**
            - Tokens are the lowercased text split on whitespace (same for the query), so
              `"Dog"` and `"dog"` are the same term. No punctuation stripping.
            - Duplicate query terms count **once** (`"dog dog"` is just `dog`).
            - For a term `t` and document `d`:
              - `tf(t, d)` = number of times `t` occurs in `d` / number of tokens in `d`
                (an empty document scores 0)
              - `idf(t)` = `math.log(N / df)` (natural log), where `N` = number of documents
                in `docs` (empty ones included) and `df` = number of documents containing `t`.
                A term that is in no document contributes `0`.
            - A document's score is the sum of `tf(t, d) * idf(t)` over the unique query terms.
            - Only include documents whose score is **greater than 0** (so a term found in every
              document, whose idf is 0, adds nothing).
            - Sort by score, highest first; equal scores are ordered by `doc_id` A→Z.
            - Scores are compared with a relative tolerance of `1e-9`; do not round them.

            **Examples**
            ```python
            docs = {
                "d1": "the cat sat",
                "d2": "the dog sat down",
                "d3": "cats and dogs",
            }
            tfidf_rank("the cat", docs)
            # [("d1", 0.5014...), ("d2", 0.1013...)]
            # d1: 1/3*log(3/2) + 1/3*log(3/1);  d2: 1/4*log(3/2);  d3 scores 0 -> left out
            tfidf_rank("Dog DOG dog", docs)    # [("d2", 0.2746...)]   (1/4 * log(3/1))
            tfidf_rank("llm", {"a": "llm agent", "b": "llm tools"})   # []  (idf = log(2/2) = 0)
            tfidf_rank("rag", {"z": "rag rag", "y": "rag", "w": "nothing"})
            # [("y", 0.4054...), ("z", 0.4054...)]   equal scores -> ordered by id
            ```
        ''',
        "starter": r'''
            import math


            def tfidf_rank(query, docs):
                ...
        ''',
        "tests": r'''
            import math
            from solution import tfidf_rank

            DOCS = {
                "d1": "the cat sat",
                "d2": "the dog sat down",
                "d3": "cats and dogs",
            }

            def check(got, expected):
                assert [d for d, _ in got] == [d for d, _ in expected], f"got {got!r}"
                for (d, s), (_, e) in zip(got, expected):
                    assert math.isclose(s, e, rel_tol=1e-9), f"score for {d} was {s!r}"

            def test_two_term_query_scores_and_order():
                got = tfidf_rank("the cat", DOCS)
                check(got, [("d1", math.log(1.5) / 3 + math.log(3) / 3), ("d2", math.log(1.5) / 4)])

            def test_term_in_every_doc_gives_no_results():
                docs = {"a": "llm agent", "b": "llm tools", "c": "llm rag"}
                assert tfidf_rank("llm", docs) == [], "a term in every document has idf 0"

            def test_case_insensitive_and_duplicate_query_terms_count_once():
                got = tfidf_rank("Dog DOG dog", DOCS)
                check(got, [("d2", math.log(3) / 4)])

            def test_unknown_terms_and_empty_docs_add_nothing():
                docs = {"a": "", "b": "vector search", "c": "keyword search"}
                got = tfidf_rank("vector unicorn", docs)
                check(got, [("b", math.log(3) / 2)])

            def test_equal_scores_ordered_by_id_and_tf_divided_by_doc_length():
                docs = {"z": "rag rag", "y": "rag", "x": "rag rag other words", "w": "nothing"}
                got = tfidf_rank("rag", docs)
                idf = math.log(4 / 3)
                check(got, [("y", idf), ("z", idf), ("x", idf / 2)])
        ''',
        "solution": r'''
            import math


            def tfidf_rank(query, docs):
                tokenised = {doc_id: text.lower().split() for doc_id, text in docs.items()}
                n = len(tokenised)
                terms = set(query.lower().split())
                idf = {}
                for term in terms:
                    df = sum(1 for tokens in tokenised.values() if term in tokens)
                    idf[term] = math.log(n / df) if df else 0.0
                results = []
                for doc_id, tokens in tokenised.items():
                    if not tokens:
                        continue
                    score = sum(tokens.count(t) / len(tokens) * idf[t] for t in terms)
                    if score > 0:
                        results.append((doc_id, score))
                results.sort(key=lambda item: (-item[1], item[0]))
                return results
        ''',
    },
]
