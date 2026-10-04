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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["vector", "embedding", "dimension", "dot product", "norm", "length", "normalise",
                 "cosine similarity", "distance", "math.sqrt", "zip", "top-k", "mean pooling",
                 "bag of words", "tf-idf"],
    "cards": [
        {
            "syntax": "sum(x * y for x, y in zip(a, b))",
            "explain": "Dot product: multiplies the numbers at the same position and adds the products. Check len(a) == len(b) first.",
            "example": r'''
                a = [1, 2, 3]
                b = [4, 5, 6]
                print(sum(x * y for x, y in zip(a, b)))
                # 32
            ''',
        },
        {
            "syntax": "math.sqrt(sum(x * x for x in v))",
            "explain": "Norm (length) of a vector: the square root of the sum of its squares. Divide every number by it to normalise.",
            "example": r'''
                import math

                v = [3, 4]
                n = math.sqrt(sum(x * x for x in v))
                print(n)
                # 5.0
                print([x / n for x in v])
                # [0.6, 0.8]
            ''',
        },
        {
            "syntax": "dot / (norm_a * norm_b)",
            "explain": "Cosine similarity: the dot product divided by both norms. 1 is the same direction, 0 unrelated, -1 opposite.",
            "example": r'''
                import math

                a, b = [4, 0], [3, 4]
                dot = sum(x * y for x, y in zip(a, b))
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                print(dot / (norm_a * norm_b))
                # 0.6
            ''',
        },
        {
            "syntax": "[sum(col) / len(vs) for col in zip(*vs)]",
            "explain": "Mean pooling: averages several vectors position by position. zip(*vs) yields one tuple per position.",
            "example": r'''
                vs = [[4, 0], [0, 2], [2, 1]]
                print(list(zip(*vs)))
                # [(4, 0, 2), (0, 2, 1)]
                print([sum(col) / len(vs) for col in zip(*vs)])
                # [2.0, 1.0]
            ''',
        },
        {
            "syntax": "sorted(d.items(), key=lambda p: (-p[1], p[0]))[:k]",
            "explain": "Top-k: sorts (id, score) pairs by score from high to low, then by id for equal scores, and keeps the first k.",
            "example": r'''
                scores = {"c1": 0.2, "c2": 0.9, "c3": 0.9}
                ranked = sorted(scores.items(), key=lambda p: (-p[1], p[0]))
                print(ranked[:2])
                # [('c2', 0.9), ('c3', 0.9)]
            ''',
        },
        {
            "syntax": "tf * math.log(N / df)",
            "explain": "TF-IDF: a term's share of the document's words, times the log of (documents / documents containing the term).",
            "example": r'''
                import math

                docs = ["the cat sat", "the dog sat down", "cats and dogs"]
                words = docs[0].split()
                tf = words.count("cat") / len(words)
                df = sum(1 for d in docs if "cat" in d.split())
                print(round(tf * math.log(len(docs) / df), 3))
                # 0.366
            ''',
        },
    ],
}

LESSON = r'''
## Vectors and similarity

### Vectors and embeddings

A **vector** is a list of numbers, such as `[3, 4]`. The count of numbers is the vector's
**dimension**: `[3, 4]` has 2 dimensions. An **embedding** is a vector that a model computes
from a piece of text. Texts with similar meaning get vectors with similar numbers. This
chapter shows how to measure how similar two vectors are.

**Retrieval** means finding the pieces of text that are relevant to a question. **RAG**
(retrieval-augmented generation) puts those pieces into the prompt, so the model can answer
from your own documents. It uses embeddings in four steps. You split documents into pieces
called **chunks** and **embed** every chunk once, which means computing its embedding. You
embed the question, which is also called the **query**. You sort the chunks by similarity to
the question. You put the best chunks into the prompt.

### Element-wise operations

An **element-wise** operation combines the numbers at the same position. `zip(a, b)` produces
the pairs and a list comprehension builds the result. **Scaling** multiplies every number by
the same factor.

```python
a = [3, 4]
b = [4, 3]
print([x + y for x, y in zip(a, b)])
# [7, 7]
print([x * 2 for x in a])
# [6, 8]
print(a)
# [3, 4]
```

Each comprehension builds a new list. `a` is not changed.

### Dot product, norm and cosine similarity

The **dot product** multiplies two vectors position by position and adds the products. For
`[3, 4]` and `[4, 3]` it is `3 * 4 + 4 * 3 = 24`.

The **norm** of a vector is the square root of the sum of its squares. For `[3, 4]` the
squares are `9` and `16` and their sum is `25`. The square root of `25` is `5`, because
`5 * 5` is `25`. `math.sqrt(x)` returns the square root of `x` as a float. The norm is also
called the length, the magnitude or the L2 norm.

**Cosine similarity** is the dot product divided by both norms. Here it is
`24 / (5 * 5) = 0.96`. It is between `-1` and `1`. It depends only on the **direction** of
each vector: the ratios between its numbers, not how large the numbers are. `[3, 4]` and
`[6, 8]` have the same direction, and their cosine similarity is `1`.

```python
import math

a = [3, 4]
b = [4, 3]
dot = sum(x * y for x, y in zip(a, b))
norm_a = math.sqrt(sum(x * x for x in a))
norm_b = math.sqrt(sum(x * x for x in b))
print(dot)
# 24
print(norm_a)
# 5.0
print(dot / (norm_a * norm_b))
# 0.96
```

Drag either vector and watch the dot product, the norms and the cosine similarity change.

```diagram
{"type":"vectors","title":"Dot product, norms and cosine similarity of a and b","a":[3,4],"b":[4,3]}
```

### Normalising and distance

To **normalise** a vector, divide every number by the norm. The result has norm 1 and the
same direction. `[3, 4]` has norm 5, so it becomes `[3 / 5, 4 / 5]`.

The **Euclidean distance** between two vectors is the norm of their difference.
`math.dist(a, b)` computes it. The difference of `[3, 4]` and `[4, 3]` is `[-1, 1]`. Its
squares add up to `2`, and the square root of `2` is about `1.41`. A smaller distance means
the numbers of the two vectors are closer.

```python
import math

a = [3, 4]
b = [4, 3]
n = math.sqrt(sum(x * x for x in a))
print([x / n for x in a])
# [0.6, 0.8]
print(math.dist(a, b))
# 1.4142135623730951
```

### Comparing embeddings

This example compares three small embeddings. `math.hypot` returns the norm of the numbers
you pass to it. The `*` in `math.hypot(*a)` passes each item of the list `a` as a separate
argument, so `math.hypot(*[3, 4])` is the same call as `math.hypot(3, 4)`.

```python
import math

cat, kitten, invoice = [0.9, 0.8, 0.0], [0.8, 0.9, 0.1], [0.0, 0.1, 0.9]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.hypot(*a) * math.hypot(*b))

print(round(cosine(cat, kitten), 2))
# 0.99
print(round(cosine(cat, invoice), 2))
# 0.07
```

`cat` and `kitten` have similar numbers at every position, so their score is close to `1`.
`cat` and `invoice` are large at different positions, so their score is close to `0`.

### Mean pooling and top-k

**Mean pooling** averages several vectors position by position. It gives one vector for many
chunks. `zip(*chunks)` yields one tuple per position, here `(4, 0, 2)` and `(0, 2, 1)`. The
averages are `6 / 3 = 2.0` and `3 / 3 = 1.0`.

**Top-k** keeps the `k` highest scores. The sort key `(-p[1], p[0])` orders the pairs by
score from high to low, then by id for equal scores.

```python
chunks = [[4, 0], [0, 2], [2, 1]]
print([sum(col) / len(chunks) for col in zip(*chunks)])
# [2.0, 1.0]

scores = {"c1": 0.2, "c2": 0.9, "c3": 0.9}
print(sorted(scores.items(), key=lambda p: (-p[1], p[0]))[:2])
# [('c2', 0.9), ('c3', 0.9)]
```

### Keyword vectors

A **vocabulary** is a fixed list of words. A **bag of words** vector holds one count per
vocabulary word: how many times that word occurs in the text.

```python
words = "the cat and the hat".split()
vocab = ["cat", "the", "dog"]
print([words.count(w) for w in vocab])
# [1, 2, 0]
```

**TF-IDF** is a score for how well a document matches one word. The word is called a
**term**. The score multiplies two numbers.

The **term frequency** (TF) is the number of times the term occurs in the document, divided
by the number of words in the document.

The **inverse document frequency** (IDF) is `math.log(N / df)`. `N` is the number of
documents and `df` is the number of documents that contain the term. `math.log(x)` returns
the natural logarithm of `x`. It is `0` when `x` is `1` and it grows slowly as `x` grows.

```python
import math

docs = ["the cat sat", "the dog sat down", "cats and dogs"]
words = docs[0].split()
tf = words.count("cat") / len(words)
df = sum(1 for d in docs if "cat" in d.split())
idf = math.log(len(docs) / df)
print(round(tf, 3), df, round(idf, 3))
# 0.333 1 1.099
print(round(tf * idf, 3))
# 0.366
print(math.log(3 / 3))
# 0.0
```

`"cat"` is 1 of the 3 words of the first document, so TF is `1 / 3`. Only 1 of the 3
documents contains `"cat"`, so IDF is `math.log(3 / 1)`. A term that all 3 documents contain
gets `math.log(3 / 3)`, which is `0`, so it adds nothing to any score. A word that is
frequent in one document and rare in the others gets a high score.

### Common mistakes

- `zip` stops at the end of the shorter list and raises no error. Check `len(a) != len(b)`
  first and raise `ValueError`.
- A vector of only zeros has norm 0. Check for that before you divide by the norm.
- Rank by cosine similarity, not by the raw dot product. A long vector can get a larger dot
  product than a short vector whose direction is closer to the query. The two rankings agree
  when every vector is normalised.
- Compare floats with `math.isclose(x, y)`, not with `==`. Float arithmetic has small
  rounding errors.

```python
import math

print(sum(x * y for x, y in zip([1, 2, 3], [10, 20])))
# 50
print(0.1 + 0.2 == 0.3)
# False
print(math.isclose(0.1 + 0.2, 0.3))
# True
```
'''

EXERCISES = [
    {
        "id": "vectors-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "lesson": r'''
            ## Pair corresponding numbers before comparing them

            Suppose two documents are represented by lists of numbers. Before comparing them, you need to align the first number with the first, the second with the second, and so on. Comparing different positions would mix unrelated measurements.

            ```python
            left = [2, 0, -1]
            right = [5, 3, 4]
            print(list(zip(left, right)))
            # [(2, 5), (0, 3), (-1, 4)]
            print([a * b for a, b in zip(left, right)])
            # [10, 0, -4]
            ```

            A numerical list used this way is a **vector**. Its number of positions is its **dimension**. A model-generated vector representing input such as text is an **embedding**. Its coordinates are learned numerical features, not usually a list of human-readable properties.

            `zip` pairs corresponding positions into tuples. Unpacking each tuple as `a, b` lets an expression use its two numbers. Multiplying each pair and adding the products gives one combined number called the **dot product**.

            ```predict
            pairs = [(2, 3), (-1, 4)]
            print([x * y for x, y in pairs])
            print(sum(x * y for x, y in pairs))
            ---
            The products are six and negative four. Keeping them in a list shows both contributions; summing them produces the single score two.
            ```

            This score is a building block for comparisons, not a complete guarantee that two texts mean the same thing. The embedding model and scoring method determine how useful the comparison is. You will add length-aware comparisons later.

            ```quiz
            What does zip pair with the second number in the left vector?
            - [x] The second number in the right vector :: Pairing is positional, preserving corresponding coordinates.
            - [ ] Every number in the right vector :: That would produce all combinations, which is a different operation.
            ```

            **Watch out:** a list of pairs and a sum are different output shapes. Trace each print separately rather than expecting every vector operation to return another vector.

            **In short:** pair matching positions, calculate each pair's contribution, then combine those contributions if you need one score.
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
            Zip aligns the first numbers as (1, 4), the second as (2, 5), and the third as (3, 6). The first print selects the first tuple from that list. The second print performs a separate calculation: each pair is multiplied, giving 4, 10, and 18, and their sum is 32. The tuple output and the scalar output therefore have different shapes.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Track the two printed values separately: a pair and a numerical total.",
            "Zip aligns corresponding positions. The product expression multiplies within each pair before the sum combines results.",
            "Write down the paired coordinates, identify the first tuple, and separately total the coordinate products. Preserve Python's tuple punctuation in the first output line.",
        ],
    },
    {
        "id": "vectors-s2",
        "title": "Add two vectors",
        "difficulty": 0,
        "lesson": r'''
            ## Combine two vectors one position at a time

            Two records measure the same quantities in the same order. You want a combined record while keeping both originals available. Each output position should combine only the corresponding positions of the inputs.

            ```python
            morning = [4, 1, 2]
            evening = [3, 5, 0]
            combined = [a + b for a, b in zip(morning, evening)]
            print(combined)
            # [7, 6, 2]
            print(morning)
            # [4, 1, 2]
            ```

            This is **element-wise addition**: one addition per pair of elements. The result is another vector with the same dimension. The list comprehension creates a new list, so assigning the result does not replace any item inside an input list.

            ```predict
            print([3, 1] + [2, 4])
            print([a - b for a, b in zip([3, 1], [2, 4])])
            ---
            Adding the lists directly concatenates them into four items. The comprehension instead operates on corresponding numbers and produces two differences.
            ```

            The distinction matters because Python's plus operator works differently for lists and numbers. A list plus another list joins sequences. Two numbers joined with plus produce their sum. Use the surrounding structure to tell which kind of value the operation receives.

            Negative values and decimal values follow the same arithmetic rules. You do not need a separate operation for them. If both input lists are empty, there are no pairs to process and the new list is empty too.

            ```quiz
            Where should the combining arithmetic happen?
            - [x] On each pair of numbers :: This preserves one output coordinate per input coordinate.
            - [ ] On the two whole lists with list concatenation :: That doubles the sequence rather than combining corresponding coordinates.
            ```

            **Watch out:** changing an input item through its index also changes the list the caller owns. Construct a new result when preservation is required.

            **In short:** element-wise operations combine matching numbers into a new vector, not a longer concatenated list.
        ''',
        "prompt": r'''
            Adding two vectors means adding the numbers at the same position.

            **Your job:** fill in the blank (`___`) in `add_vectors(a, b)`

            **What goes in**

            - `a`: a list of numbers, e.g. `[1, 2, 3]`
            - `b`: a list of numbers of the same length, e.g. `[10, 20, 30]`

            **What comes out**
            - a new list where each number is `a[i] + b[i]`, e.g. `[11, 22, 33]`

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
            "The surrounding comprehension already pairs the coordinates and builds the result list.",
            "The gap controls the arithmetic between the two numbers, not the traversal.",
            "Take one pair from the example and ask which arithmetic operation produces its required combined coordinate. Check the same choice against a negative-number pair.",
        ],
    },
    {
        "id": "vectors-s6",
        "title": "When lengths don't match",
        "difficulty": 0,
        "lesson": r'''
            ## Notice when pairing silently drops data

            One list contains three names, but another contains only two scores. Pairing them can still run successfully while leaving one name out. A numerical result is not proof that every input value was used.

            ```python
            names = ["oak", "elm", "pine"]
            values = [7, 9]
            print(list(zip(names, values)))
            # [('oak', 7), ('elm', 9)]
            print(len(names), len(values))
            # 3 2
            ```

            By default, `zip` stops when the shortest input ends. It does not insert a missing value or raise an exception. That behavior is convenient when shorter pairing is intended, but dangerous when all coordinates are required.

            ```predict
            left = [8, 2, 5, 1]
            right = [3]
            print(list(zip(left, right)))
            print(list(zip([], right)))
            ---
            Only the first pair can be formed in the first call. In the second, one input is already exhausted, so there are no pairs at all.
            ```

            Vector calculations usually require equal dimensions. Checking before arithmetic makes an incompatible pair fail clearly instead of returning a plausible but incomplete score. Rejecting invalid input early is often called **failing fast**.

            Equal length is necessary but not sufficient for meaningful embedding comparisons. The vectors also need compatible coordinate meanings, usually from the same embedding model and configuration. Two unrelated models may produce equal-length vectors that should not be compared directly.

            ```quiz
            The calculation returned a number after zip paired unequal-length vectors. What does that establish?
            - [x] Only that the operations ran :: Some coordinates may have been ignored, invalidating the intended calculation.
            - [ ] That the vectors were compatible :: Python did not validate their dimensions or meanings for you.
            ```

            **Watch out:** there may be no error message for this bug. Count input lengths and resulting pairs when a score seems reasonable but wrong.

            **In short:** default zip stops at the shortest input, so validate vector dimensions before relying on its pairs.
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
            The shorter list has only two values, so zip creates (1, 10) and (2, 20), then stops without pairing the remaining 3. The sum uses only those pairs and becomes 10 plus 40, or 50. The final comparison uses the original lengths, three and two, so it prints False. Python completed the arithmetic, but it did not validate the vector dimensions.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Count how many complete pairs can exist before either input runs out.",
            "Only those complete pairs contribute to both the displayed pair list and the later numerical total.",
            "Trace the available pairs in order, add their products, then compare the original list lengths for the final Boolean line.",
        ],
    },
    {
        "id": "vectors-s4",
        "title": "Scale a vector",
        "difficulty": 0,
        "lesson": r'''
            ## Change every coordinate by the same factor

            You want a measurement vector expressed at half its current scale. Each coordinate must change by the same proportion while the original measurements remain available.

            ```python
            measurements = [6, -4, 2]
            adjusted = [number * 0.5 for number in measurements]
            print(adjusted)
            # [3.0, -2.0, 1.0]
            print(measurements)
            # [6, -4, 2]
            ```

            Multiplying every coordinate by one number is **scaling**. That one number is a **scalar**. A positive scalar changes the vector's size while preserving its direction. A negative scalar reverses direction as well. Multiplying by zero produces the zero vector, which has no direction.

            ```predict
            values = [2, -3]
            print(values * 2)
            print([value * -1 for value in values])
            ---
            Multiplying a list repeats the list, producing four items. Multiplying each number by negative one flips the two coordinate signs without changing the dimension.
            ```

            A vector's direction describes its orientation, rather than how far it extends. You can picture that in two dimensions: increasing both coordinates by the same positive proportion keeps the same line from the origin. Later comparisons can ignore the size and compare orientation alone.

            A fresh list comprehension preserves the input. An empty vector has no coordinates to scale, so it naturally produces an empty output list. There is no need to invent a coordinate for it.

            ```quiz
            Which factor reverses a nonzero vector's direction without changing its magnitude?
            - [x] Negative one :: Every sign flips while absolute coordinate sizes stay the same.
            - [ ] Zero :: All coordinates become zero, removing any direction.
            - [ ] One :: This preserves both the original direction and size.
            ```

            **Watch out:** whole-list multiplication repeats a sequence. It does not perform vector arithmetic on its elements.

            **In short:** scale by multiplying each coordinate, creating a new list when the original must remain intact.
        ''',
        "prompt": r'''
            *Scaling* a vector multiplies every number in it by the same factor.

            **Your job:** write `scale(v, factor)`

            **What goes in**

            - `v`: a list of numbers, e.g. `[1, 2, 3]`
            - `factor`: a number, e.g. `2` or `0.5`

            **What comes out**
            - a **new** list with every number of `v` multiplied by `factor`

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
            "Distinguish multiplying a whole list from multiplying each number it contains.",
            "Build a new result so the original coordinates remain available to the caller.",
            "Visit every coordinate, multiply it by the supplied factor, and collect the products in order. With no coordinates, collect nothing.",
        ],
    },
    {
        "id": "vectors-s5",
        "title": "Vector length",
        "difficulty": 0,
        "lesson": r'''
            ## Measure the size of a vector

            Two vectors can contain the same number of coordinates while extending different distances from zero. Counting their items will not tell you that distance. You need to combine the sizes of their coordinates.

            ```python
            import math
            values = [2, 6, 3]
            squared = [number * number for number in values]
            print(squared)
            # [4, 36, 9]
            print(math.sqrt(sum(squared)))
            # 7.0
            ```

            Square each coordinate, add those squares, then take the square root. The **square root** of 49 is 7 because seven multiplied by itself is 49. This calculation gives the vector's **magnitude**, also called its **L2 norm** or geometric length.

            The dimension counts coordinates. The norm measures magnitude. A three-coordinate vector can have norm seven; these are different quantities despite both sometimes being described informally as length.

            ```predict
            import math
            print(math.sqrt((-5) * (-5)))
            print(len([-5]))
            ---
            Squaring removes the negative sign and the square root gives a magnitude of 5.0. The dimension is only one because the list has one coordinate.
            ```

            Squaring ensures positive and negative coordinates cannot cancel each other when measuring size. Adding coordinates directly would make `[5, -5]` appear to have size zero even though both coordinates are nonzero.

            ```quiz
            Why must the square root come after adding the squares?
            - [x] The norm combines all squared contributions before returning to the original scale :: Taking roots separately would instead add absolute coordinate sizes, a different measure.
            - [ ] Square roots only accept lists :: math.sqrt accepts one numerical value, not a list.
            ```

            **Watch out:** `len` answers the dimension question, not the magnitude question. Also, floating-point answers can differ by tiny rounding amounts, so numeric comparisons often use a tolerance.

            **In short:** a norm is the square root of the total squared coordinates, not the count of coordinates.
        ''',
        "prompt": r'''
            An embedding is a vector (a list of numbers). Its *length* (also called its
            *norm* or *magnitude*) tells you how big it is.

            **Your job:** write `length(v)`

            **What goes in**

            - `v`: a list of numbers, e.g. `[3, 4]`

            **What comes out**
            - a float: the **square root of the sum of the squares** of the numbers in `v`

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
            "The geometric length is not the number of list items.",
            "Square each coordinate so opposite signs cannot cancel, then combine their contributions.",
            "Add the coordinate squares and take one square root of that total. Return the number, including the zero result for empty input.",
        ],
    },
    {
        "id": "vectors-s3",
        "title": "Fix the best-chunk picker",
        "difficulty": 0,
        "lesson": r'''
            ## Select an identifier by its score

            A search step assigns each document a numerical score. You need the identifier of the best-scoring document, rather than the identifier that happens to sort last alphabetically.

            ```python
            ratings = {"zebra": 0.3, "apple": 0.8, "maple": 0.5}
            print(max(ratings))
            # zebra
            print(max(ratings, key=ratings.get))
            # apple
            ```

            Iterating over a dictionary supplies its keys. Without a key function, `max` therefore compares the identifier strings. The `key` argument tells it how to obtain a comparison value for each identifier. Here, the dictionary's `get` method supplies the score.

            The returned item remains the identifier. The comparison value helps choose the item; it does not replace the item in the output. You saw the same separation when sorting records with key functions.

            ```fill
            costs = {"fast": 9, "cheap": 2}
            print(min(costs, key=___))
            ---
            - [x] costs.get :: This compares the stored costs and returns cheap.
            - [ ] len :: This compares identifier lengths and returns fast instead.
            ```

            Whether bigger or smaller is better depends on the metric. Similarity usually ranks higher scores first. Distance usually ranks lower values first. Read the promised meaning of a score instead of choosing a function from the word "best" alone.

            ```predict
            print(max([-0.8, -0.3, -0.6]))
            ---
            Negative 0.3 is the largest number, even though its absolute value is the smallest. Similarity ranking still uses ordinary numerical order.
            ```

            **Watch out:** a function can compare the correct stored values but choose the wrong end of that ordering. Test two unequal scores, including negative ones, to expose that mistake.

            **In short:** compare identifiers using their scores, then choose the high or low end required by the metric.
        ''',
        "prompt": r'''
            A retriever scored some chunks by similarity to the question. `best_chunk` should
            pick the best match, but it returns the worst one. Fix the bug.

            **Your job:** fix `best_chunk(scores)`

            **What goes in**

            - `scores`: a dict mapping chunk id (`str`) to score (`float`), e.g. `{"c1": 0.12, "c2": 0.91}`

            **What comes out**
            - the id (`str`) of the chunk with the **highest** score

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
            "The existing key function chooses what to compare; inspect which end of the ordering is selected.",
            "Larger similarity scores are better, including when every score is negative.",
            "Trace the current selection with two unequal scores, then choose the built-in that selects the required extreme while retaining the score lookup.",
        ],
    },
    {
        "id": "vectors-1",
        "hints": [
            "A dot product reduces coordinate-wise multiplication to one scalar.",
            "Validate equal dimensions before pairing; otherwise zip could silently ignore unmatched coordinates.",
            "Reject either kind of dimension mismatch. Multiply every corresponding pair and sum those products, allowing the empty sum to produce zero.",
        ],
        "title": "Dot product",
        "difficulty": 1,
        "lesson": r'''
            ## Reduce matching coordinate products to one score

            You have aligned two vectors and now need one number describing how their coordinates contribute together. Positive and negative contributions should combine rather than being kept as a new vector.

            ```python
            one = [2, -3, 1]
            two = [4, -1, -2]
            products = [left * right for left, right in zip(one, two)]
            print(products)
            # [8, 3, -2]
            print(sum(products))
            # 9
            ```

            This is the dot product introduced at the start of the chapter. Matching signs create a positive contribution: two negative numbers multiply to a positive number too. Opposite signs contribute negatively. Adding the products combines their effects into one scalar.

            ```predict
            print(sum(a * b for a, b in zip([2, 0], [3, 9])))
            print(sum(a * b for a, b in zip([2, 0], [-3, 9])))
            ---
            The second coordinate contributes zero in both cases. Reversing the sign of the other contribution changes the totals from six to negative six.
            ```

            Remember that default `zip` will silently truncate unequal inputs. A public vector function should validate matching dimensions before computing the score. Checking only one mismatch direction is insufficient: either input can be longer.

            A large dot product can come from large magnitudes as well as similar directions. Do not interpret it as a pure direction score until you account for those magnitudes. That distinction is why normalization and cosine similarity follow this step.

            ```quiz
            What is the sum of the products for two empty vectors under this exercise's convention?
            - [x] Zero :: There are no contributions to add, and sum starts from zero.
            - [ ] An empty list :: The dot product returns one number, not another vector.
            ```

            **Watch out:** adding paired coordinates instead of multiplying them performs a different operation. Inspect intermediate products when the final number is wrong.

            **In short:** validate dimensions, multiply corresponding coordinates, and add the products into one score.
        ''',
        "prompt": r'''
            The *dot product* is the basic building block of embedding similarity: it
            multiplies two vectors position by position and adds up the results.

            **Your job:** write `dot(a, b)`

            **What goes in**

            - `a`: a list of numbers, e.g. `[1, 2, 3]`
            - `b`: a list of numbers, e.g. `[4, 5, 6]`

            **What comes out**
            - a number: `a[0]*b[0] + a[1]*b[1] + ...` (for the example, `4 + 10 + 18 = 32`)

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
            "Normalization needs the magnitude calculation from the previous norm exercise.",
            "Compute that magnitude once and reuse it as the divisor for every coordinate.",
            "Implement the norm helper, reject zero magnitude before dividing, and produce a fresh list of divided coordinates without rounding or modifying the input.",
        ],
        "title": "Norm and unit vectors",
        "difficulty": 1,
        "lesson": r'''
            ## Keep direction while giving every vector unit size

            A longer vector can dominate a dot-product score even when its direction is no better. You want vectors on a common size scale so comparisons emphasize their orientation.

            ```python
            import math
            values = [5, 12]
            magnitude = math.sqrt(sum(item * item for item in values))
            unit = [item / magnitude for item in values]
            print(magnitude)
            # 13.0
            print(math.isclose(sum(item * item for item in unit), 1.0))
            # True
            ```

            Dividing every coordinate by the vector's norm is **normalization**. The result has norm one and is called a **unit vector**. Because the same positive divisor is applied to each coordinate, a nonzero vector keeps its direction.

            ```predict
            values = [0, -6]
            print([item / 6 for item in values])
            ---
            The new coordinates are 0.0 and -1.0. The direction remains along the negative second axis, while the magnitude becomes one.
            ```

            Normalization should return a new vector if callers still need the original magnitude. Reusing a norm helper keeps the calculation consistent: first obtain the magnitude, then use it as the shared divisor.

            A zero vector contains only zero coordinates. It has no direction and its norm is zero. The empty vector also has norm zero under the convention used here. Neither can be turned into a direction-preserving unit vector.

            ```quiz
            Why should normalization reject a zero norm before the division?
            - [x] There is no direction to preserve and the divisor is zero :: The function should raise its promised validation error instead of accidentally dividing by zero.
            - [ ] Zero coordinates are individually forbidden :: A nonzero vector can contain zero coordinates and still be normalized.
            ```

            **Watch out:** rounding each normalized coordinate can change its norm and later rankings. Keep the floating-point precision and use tolerant comparisons for checks.

            **In short:** divide a nonzero vector by its own norm to preserve direction at unit magnitude.
        ''',
        "prompt": r'''
            Many vector databases store embeddings *normalised* to length 1, so that a plain
            dot product equals cosine similarity.

            **Your job:** write two functions, `norm(v)` and `normalize(v)`

            **What goes in**

            - `v`: a list of numbers, e.g. `[3, 4]`
            - `norm(v)` **returns:** a float, the *L2 norm* (magnitude) of `v`: the square root
              of the sum of the squares of its numbers
            - `normalize(v)` **returns:** a **new** list: every number of `v` divided by `norm(v)`,
              so the result points the same way and has norm `1.0`

            **What comes out**
            - `norm` gives back the magnitude as a float. `normalize` gives back a fresh unit-length vector for nonzero input and raises for a zero norm.

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
            ## Measure how far apart two vectors are

            Sometimes the useful question is how close the coordinates are, rather than whether the vectors point in the same direction. Two points on the same ray can still lie far apart.

            ```python
            import math
            start = [2, 1]
            finish = [8, 9]
            difference = [a - b for a, b in zip(start, finish)]
            print(difference)
            # [-6, -8]
            print(math.sqrt(sum(value * value for value in difference)))
            # 10.0
            ```

            Take the difference at each coordinate, then measure that difference vector's norm. This is **Euclidean distance**, the ordinary straight-line distance generalized to any number of dimensions. Identical vectors have distance zero.

            ```predict
            import math
            print(math.sqrt((2 - 5) ** 2))
            print(math.sqrt((5 - 2) ** 2))
            ---
            The differences have opposite signs, but squaring makes both nine. The distance is 3.0 in either direction.
            ```

            Distance is symmetric: swapping the two inputs does not change the result. It is also nonnegative. Those properties give you useful checks before testing complicated vectors.

            Smaller distance means closer coordinates. Whether that also means more relevant text depends on the embedding model and preprocessing. Do not assume that every metric produces interchangeable scores or that larger always means better.

            The standard library includes a function for this calculation. The research link asks you to identify it in the math documentation and confirm its behavior on dimension mismatches and empty inputs.

            ```quiz
            A search ranks by Euclidean distance. Which result is closer, distance two or distance seven?
            - [x] Distance two :: Less separation means a closer vector under this metric.
            - [ ] Distance seven :: Higher-is-better applies to many similarities, not to distance.
            ```

            **Watch out:** unequal coordinate counts do not describe points in the same space. Reject them rather than using truncated pairs.

            **In short:** subtract corresponding coordinates and take the norm; smaller distances indicate closer points.
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

            **Your job:** write `distance(a, b)`

            **What goes in**

            - `a`: a list of numbers, e.g. `[0, 0]`
            - `b`: a list of numbers, e.g. `[3, 4]`

            **What comes out**
            - a `float`, the *Euclidean distance*: the square root of the sum of
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
            "Distance is the magnitude of the difference between corresponding coordinates.",
            "The math documentation offers a function for this measure; confirm how it handles dimensions.",
            "Validate matching lengths and calculate the straight-line distance using the documented helper or the sum-of-squared-differences formula. Preserve full precision.",
        ],
    },
    {
        "id": "vectors-8",
        "title": "Mean pooling",
        "difficulty": 1,
        "lesson": r'''
            ## Average several vectors without mixing their positions

            A document contains several chunks, each with its own vector. You want one summary vector whose first coordinate averages the first coordinates, whose second averages the second coordinates, and so on.

            ```python
            rows = [[2, 8], [6, 4], [4, 6]]
            columns = list(zip(*rows))
            print(columns)
            # [(2, 6, 4), (8, 4, 6)]
            print([sum(column) / len(rows) for column in columns])
            # [4.0, 6.0]
            ```

            Averaging vectors position by position is **mean pooling**. Here `*rows` unpacks the outer list into separate arguments to `zip`. Instead of pairing two vectors, zip gathers one coordinate from every vector for each position.

            Each resulting tuple is a column of the original rows. Dividing its sum by the number of vectors gives one coordinate of the result. The divisor is the number of input vectors, not their dimension.

            ```quiz
            You average four vectors, each with three coordinates. How many numbers are averaged for one result coordinate?
            - [x] Four :: Each of the four vectors contributes its value at that position.
            - [ ] Three :: Three is the number of result coordinates, not the number contributing to each average.
            ```

            Validate before rearranging coordinates. An empty outer list provides no observations to average. Unequal dimensions would let zip quietly discard coordinates. By contrast, a nonempty list of empty vectors has matching zero dimensions and can yield an empty mean vector under this exercise's rules.

            ```predict
            print(list(zip(*[[3, 7]])))
            print(list(zip(*[[], []])))
            ---
            A single vector creates one-item columns. Two empty vectors have no coordinate columns at all.
            ```

            **Watch out:** averaging each row gives one number per chunk and destroys the coordinate layout. Pool across rows at each position instead.

            **In short:** mean pooling averages each coordinate across equally shaped vectors into a fresh summary vector.
        ''',
        "prompt": r'''
            Turn a document's chunk embeddings into one document embedding by averaging them.

            **Your job:** write `mean_vector(vectors)`

            **What goes in**

            - `vectors`: a `list` of vectors (lists of numbers), all the same length, e.g.
              `[[4, 0], [0, 1]]`

            **What comes out**
            - a **new** list of floats: position `i` is the average of `v[i]` over
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
            "Think in columns across vectors rather than totals within each vector.",
            "Ensure there is at least one vector and all dimensions agree before collecting corresponding coordinates.",
            "For each coordinate position, add contributions from every vector and divide by the number of vectors. Collect those means into a new list.",
        ],
    },
    {
        "id": "vectors-9",
        "title": "Top-k results",
        "difficulty": 1,
        "lesson": r'''
            ## Return several best matches in a predictable order

            A question may need evidence from more than one document. You want a chosen number of high-scoring results, and equal scores should always appear in a predictable order.

            ```python
            ratings = {"pine": 7, "birch": 9, "ash": 7}
            ranked = sorted(ratings.items(), key=lambda pair: (-pair[1], pair[0]))
            print(ranked)
            # [('birch', 9), ('ash', 7), ('pine', 7)]
            print(ranked[:2])
            # [('birch', 9), ('ash', 7)]
            ```

            Keeping the best chosen number of results is called **top-k** selection, where `k` is that number. A tuple-valued sort key expresses two priorities. Python compares its first values, then uses the second only when the first values tie.

            Negating a score makes a larger score sort earlier in ascending order. Leaving the identifier unchanged makes tied identifiers sort alphabetically. Reversing the entire sort would reverse both priorities, which is not always what the task promises.

            ```quiz
            Two records tie on score and identifiers must be alphabetical. What is wrong with reversing an ascending sort of (score, identifier)?
            - [x] It reverses the identifier order too :: You need opposite directions for the two priorities.
            - [ ] It changes the stored scores :: Sorting reorders items; it does not change numerical values.
            ```

            Slicing a sorted list keeps the requested prefix. Asking for more items than exist gives all available items, without an error. But a negative slice stop has its own Python meaning, so handle nonpositive requested counts explicitly when they mean no results.

            ```predict
            items = ["a", "b", "c"]
            print(items[:8])
            print(items[:-1])
            ---
            The large stop keeps every item. A negative stop removes the last item rather than requesting zero items.
            ```

            **Watch out:** sorting the dictionary alone sorts keys. Use its item pairs when the result must preserve both identifiers and scores.

            **In short:** express score and tie priorities separately, then take a bounded prefix with an explicit nonpositive-count rule.
        ''',
        "prompt": r'''
            A retriever has scored every chunk. Return the best `k` for the prompt.

            **Your job:** write `top_k(scores, k)`

            **What goes in**

            - `scores`: a dict mapping chunk id (`str`) to score (`float`), e.g.
              `{"c1": 0.2, "c2": 0.9, "c3": 0.5}`
            - `k`: an `int`, how many results to keep, e.g. `2`

            **What comes out**
            - a `list` of `(chunk_id, score)` tuples, highest score first, e.g.
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
            "You need two ordering priorities followed by a result-count boundary.",
            "Use a sort key with score descending and identifier ascending; reversing everything would break ties.",
            "Handle nonpositive counts first. Sort fresh identifier-score pairs using the two priorities and take the requested prefix without changing the input dictionary.",
        ],
    },
    {
        "id": "vectors-3",
        "hints": [
            "Combine the dot product and the two norm calculations.",
            "The denominator removes both magnitudes, but a zero magnitude needs its own defined result.",
            "Check dimensions, calculate both norms, handle the directionless case, then divide the dot product by the product of norms without rounding.",
        ],
        "title": "Cosine similarity",
        "difficulty": 2,
        "lesson": r'''
            ## Compare direction without rewarding extra size

            Two vectors may point the same way even though one is twice as large. A direction-based comparison should give them the same agreement as two identical vectors. You already have the ingredients: the dot product and each vector's norm.

            ```python
            import math
            first, second = [3, 0], [4, 3]
            product = sum(a * b for a, b in zip(first, second))
            size_a = math.sqrt(sum(a * a for a in first))
            size_b = math.sqrt(sum(b * b for b in second))
            print(product / (size_a * size_b))
            # 0.8
            ```

            Dividing the dot product by the product of the two norms gives **cosine similarity**. For nonzero vectors, its mathematical range is negative one through one. One means the same direction, negative one means opposite directions, and zero means perpendicular directions.

            Try moving the endpoints in this diagram while keeping one vector longer than the other. Notice how matching direction can still give a score of one.

            ```diagram
            {"type":"vectors","title":"Direction and cosine similarity","a":[3,0],"b":[4,3]}
            ```

            ```quiz
            One nonzero vector is multiplied by a positive factor. What happens to its cosine similarity with another fixed nonzero vector?
            - [x] It stays the same :: The factor affects the dot product and norm equally, so it cancels.
            - [ ] It must increase :: That can happen to a raw dot product, not this normalized comparison.
            ```

            Putting it together also requires a zero-vector policy. A zero vector has no direction, so the mathematical formula is undefined. This exercise chooses a score of zero for that case. Check dimensions first so unequal vectors are still rejected even if one has zero norm.

            A geometric score is not a calibrated probability of relevance. Its practical interpretation depends on the embedding model and your application.

            **Watch out:** do not divide before checking norms. A zero norm causes `ZeroDivisionError`, and premature rounding can distort close scores.

            **In short:** cosine similarity divides out magnitudes, with explicit handling for incompatible dimensions and directionless vectors.
        ''',
        "placement": True,
        "prompt": r'''
            RAG retrievers compare a question's embedding with chunk embeddings using
            *cosine similarity*: how closely two vectors point in the same direction,
            ignoring how long they are.

            **Your job:** write `cosine_similarity(a, b)`

            **What goes in**

            - `a`: a list of numbers, e.g. `[1, 0]`
            - `b`: a list of numbers of the same length, e.g. `[1, 1]`

            **What comes out**
            - a float between `-1.0` and `1.0`: the dot product of `a` and `b`
              divided by (length of `a` times length of `b`), where a vector's length is the square
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
            "Counting and output ordering are separate parts of the task.",
            "Normalize each whole token exactly as specified, then count nonempty results.",
            "Lowercase and split text, remove permitted punctuation from token boundaries, count the remaining tokens, and read each vocabulary word's count in vocabulary order with zero for absence.",
        ],
        "title": "Bag of words",
        "difficulty": 2,
        "lesson": r'''
            ## Represent text with counts in a fixed word order

            You want a numerical representation you can inspect without a model. Choose a fixed list of words, then count how often each appears in the text. Every position must keep the same meaning across documents.

            ```python
            words = "blue boat blue sky".split()
            vocabulary = ["sky", "blue", "tree"]
            print([words.count(word) for word in vocabulary])
            # [1, 2, 0]
            ```

            The fixed word list is a **vocabulary**. A vector of counts in that order is a **bag-of-words** representation. It preserves frequency but discards word order. In this exercise, each whitespace-separated piece is initially a **token**, which you then clean according to the specified punctuation rules.

            ```predict
            pieces = ["Hello!", "(sky)", "..."]
            print([piece.lower().strip(".!()") for piece in pieces])
            ---
            Lowercasing makes case consistent. Stripping the listed boundary characters gives hello, sky, and an empty string. A punctuation-only token may disappear during cleaning.
            ```

            Putting it together has two stages: count cleaned whole tokens, then read those counts in vocabulary order. Iterating over the count dictionary instead would order the vector by what appeared in the document, breaking positional consistency between documents.

            ```quiz
            The vocabulary contains tree, but the document contains only treetop. How many occurrences of tree should be counted?
            - [x] Zero :: Whole-token counting does not count substrings inside a different token.
            - [ ] One :: That would be substring search, which is a different rule.
            ```

            A vocabulary word absent from the document receives zero. An empty document therefore produces a vector of zeros with the vocabulary's dimension. An empty vocabulary has no positions and produces an empty list.

            **Watch out:** `strip(chars)` removes permitted characters only from the ends, not from the middle. Follow the given token-cleaning rule rather than adding broader normalization.

            **In short:** clean and count whole tokens, then emit counts in the shared vocabulary's fixed order.
        ''',
        "prompt": r'''
            Before neural embeddings, text was turned into *count vectors* over a fixed
            vocabulary (a *bag of words*): one number per vocabulary word.

            **Your job:** write `bag_of_words(text, vocab)`

            **What goes in**

            - `text`: a string, e.g. `"The cat saw the DOG. Cat!"`
            - `vocab`: a list of lowercase words, e.g. `["cat", "dog", "the"]`

            **What comes out**
            - a list of ints, the same length as `vocab`, where position `i` is how
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
            "Separate document pooling, vector scoring, and result ranking.",
            "Skip documents with no chunks, but retain a real zero-vector document with the defined zero score.",
            "Handle a nonpositive count, average each eligible document's coordinates, compare its pooled vector with the query, then rank by descending score and ascending identifier before limiting results.",
        ],
        "title": "Top-k document search",
        "difficulty": 3,
        "prompt": r'''
            In a RAG index each document is stored as several **chunk embeddings**. Find the
            documents that best match a query embedding.

            **Your job:** write `search(query, docs, k)`

            **What goes in**

            - `query`: a vector (list of numbers), e.g. `[1, 0]`
            - `docs`: a dict mapping `doc_id` (`str`) to a **list of chunk vectors**, all with the
              same length as `query`, e.g. `{"a": [[1, 0], [1, 0]], "c": [[0, 1]]}`
            - `k`: an `int`, how many results to return, e.g. `2`

            **What comes out**
            - a list of `(doc_id, score)` tuples, best first, e.g. `[("a", 1.0), ("b", 0.447...)]`

            **Rules**
            - A document's vector is the **mean pooling** of its chunks: the average of the
              chunks position by position (e.g. `[[4, 0], [0, 1]]` pools to `[2.0, 0.5]`).
            - A document's score is the cosine similarity between `query` and its pooled vector
              (dot product / (length times length)). If either vector is all zeros, the score is `0.0`.
            - Documents with an empty chunk list are skipped (not in the result at all).
            - Sort by score, highest first; equal scores are ordered by `doc_id` A to Z.
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
            "Document frequency counts documents containing a term, while term frequency counts occurrences inside one document.",
            "Deduplicate query terms and normalize document counts by each document's token length.",
            "Tokenize all inputs, calculate rarity for each unique query term, sum its normalized contribution per nonempty document, retain positive scores, and apply the required score and identifier ordering.",
        ],
        "title": "TF-IDF keyword scoring",
        "difficulty": 3,
        "prompt": r'''
            Hybrid RAG systems combine embeddings with keyword scores. *TF-IDF* rewards
            documents that use the query's words often (*term frequency*) and prefers words that
            are rare across all documents (*inverse document frequency*).

            **Your job:** write `tfidf_rank(query, docs)`

            **What goes in**

            - `query`: a string, e.g. `"the cat"`
            - `docs`: a dict mapping `doc_id` (`str`) to its text (`str`), e.g. `{"d1": "the cat sat"}`

            **What comes out**
            - a list of `(doc_id, score)` tuples (score is a float), best first

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
            - Sort by score, highest first; equal scores are ordered by `doc_id` A to Z.
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
