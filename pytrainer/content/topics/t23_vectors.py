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
            ## Vectors and zip

            A **vector** is a list of numbers. The count of numbers is its **dimension**: `[1, 0, 2]`
            has 3 dimensions. An **embedding** is a vector that a model computes from a text. It
            usually has hundreds of numbers. Texts with similar meaning get similar numbers, so you
            can compare meanings by comparing vectors.

            In Python a vector is a plain list. `zip(a, b)` pairs the items at the same position:
            item 0 with item 0, item 1 with item 1, and so on. Each pair is a tuple.

            ```python
            query = [1, 0, 2]
            doc = [3, 5, 1]
            print(list(zip(query, doc)))
            # [(1, 3), (0, 5), (2, 1)]
            print([x * y for x, y in zip(query, doc)])
            # [3, 0, 2]
            ```

            The **dot product** is the sum of those products: multiply each pair, then add the
            results. Here it is `3 + 0 + 2 = 5`. The dot product is the basic similarity score for
            two vectors. It is large when both vectors have large numbers at the same positions.

            Step through the loop to see `total` grow by one product per pair.

            ```diagram
            {"type": "trace", "title": "Dot product of query and doc with a loop", "code": ["query = [1, 0, 2]", "doc = [3, 5, 1]", "total = 0", "for x, y in zip(query, doc):", "    total += x * y", "print(total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"query": "[1, 0, 2]"}, "out": ""},
              {"line": 3, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]"}, "out": ""},
              {"line": 4, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "0"}, "out": ""},
              {"line": 5, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "0", "x": "1", "y": "3"}, "out": ""},
              {"line": 4, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "3", "x": "1", "y": "3"}, "out": ""},
              {"line": 5, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "3", "x": "0", "y": "5"}, "out": ""},
              {"line": 4, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "3", "x": "0", "y": "5"}, "out": ""},
              {"line": 5, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "3", "x": "2", "y": "1"}, "out": ""},
              {"line": 4, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "5", "x": "2", "y": "1"}, "out": ""},
              {"line": 6, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "5", "x": "2", "y": "1"}, "out": ""},
              {"line": null, "vars": {"query": "[1, 0, 2]", "doc": "[3, 5, 1]", "total": "5", "x": "2", "y": "1"}, "out": "5\n"}
            ]}
            ```
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
            ## Element-wise addition

            To add two vectors, add the numbers at the same position. The result is a new vector of
            the same length. This is called **element-wise** (or component-wise) addition.

            ```python
            chunk1 = [2, 0, 1]
            chunk2 = [1, 3, 0]
            total = [x + y for x, y in zip(chunk1, chunk2)]
            print(total)
            # [3, 3, 1]
            print(chunk1)
            # [2, 0, 1]
            ```

            The list comprehension loops over `zip(chunk1, chunk2)`. For every pair `(x, y)` it
            computes one number, `x + y`, and puts it in a new list. `chunk1` and `chunk2` are not
            changed.

            Subtraction and multiplication work the same way. Only the operator changes.

            ```python
            chunk1 = [2, 0, 1]
            chunk2 = [1, 3, 0]
            print([x - y for x, y in zip(chunk1, chunk2)])
            # [1, -3, 1]
            ```

            Embedding code uses element-wise addition to average several embeddings: add them
            position by position, then divide each sum by the number of embeddings.
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
            ## zip with different lengths

            When the two lists have **different lengths**, `zip` stops at the end of the **shorter**
            one. It raises no error and prints no warning. The extra items of the longer list are
            ignored.

            ```python
            names = ["ana", "bo", "cy"]
            scores = [0.9, 0.4]
            for name, score in zip(names, scores):
                print(name, score)
            # ana 0.9
            # bo 0.4
            print(len(names), len(scores))
            # 3 2
            ```

            Step through the loop and count how many times the loop body runs.

            ```diagram
            {"type": "trace", "title": "zip stops at the shorter list", "code": ["names = [\"ana\", \"bo\", \"cy\"]", "scores = [0.9, 0.4]", "for name, score in zip(names, scores):", "    print(name, score)", "print(len(names), len(scores))"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"names": "['ana', 'bo', 'cy']"}, "out": ""},
              {"line": 3, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]"}, "out": ""},
              {"line": 4, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]", "name": "'ana'", "score": "0.9"}, "out": ""},
              {"line": 3, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]", "name": "'ana'", "score": "0.9"}, "out": "ana 0.9\n"},
              {"line": 4, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]", "name": "'bo'", "score": "0.4"}, "out": "ana 0.9\n"},
              {"line": 3, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]", "name": "'bo'", "score": "0.4"}, "out": "ana 0.9\nbo 0.4\n"},
              {"line": 5, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]", "name": "'bo'", "score": "0.4"}, "out": "ana 0.9\nbo 0.4\n"},
              {"line": null, "vars": {"names": "['ana', 'bo', 'cy']", "scores": "[0.9, 0.4]", "name": "'bo'", "score": "0.4"}, "out": "ana 0.9\nbo 0.4\n3 2\n"}
            ]}
            ```

            `"cy"` is never printed because `scores` has only two items.

            For vectors this produces wrong results. Embeddings from **different models** often have
            different sizes, for example 768 and 1536 numbers. `zip` would pair the first 768
            numbers of each and the code would return a number that means nothing.

            Vector code therefore checks `len(a) != len(b)` first and raises `ValueError`. Stopping
            with an error as soon as the input is wrong is called **fail fast**. An error is easier
            to find than a wrong number.
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
            `zip` stops at the end of the **shorter** list, so the `3` in `a` is never paired:
            `zip` yields only `(1, 10)` and `(2, 20)`. The sum is then 1\*10 + 2\*20 = 50.
            Python raises no error, but 50 is not the dot product of a 3-item and a 2-item
            vector, which is not defined. Only `len(a) == len(b)`, which prints `False`, shows
            the problem.
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
            ## Scaling

            **Scaling** a vector means multiplying **every** number in it by the same factor. The
            number you multiply by is called a **scalar**.

            ```python
            v = [200, 3, 50]
            print([x * 3 for x in v])
            # [600, 9, 150]
            print([x * 0.5 for x in v])
            # [100.0, 1.5, 25.0]
            print([x * -1 for x in v])
            # [-200, -3, -50]
            print(v)
            # [200, 3, 50]
            ```

            The **direction** of a vector is the ratios between its numbers, not how large they
            are. In `[200, 3, 50]` and in `[600, 9, 150]` the first number is 4 times the last, so
            both have the same direction. Scaling by a positive factor keeps the direction and
            changes only how large the numbers are. A factor of `0.5` halves every number. A factor
            of `-1` flips every sign, which gives the opposite direction.

            Build a **new** list with a comprehension. An assignment such as `v[i] = ...` changes
            the list object that the caller passed in, and the caller may still need the original
            numbers.
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
            ## Vector length

            The **length** of a vector is one number that says how large the vector is. To compute
            it, square each number, add the squares, and take the square root of the sum. The
            **square root** of `49` is `7`, because `7 * 7` is `49`. `math.sqrt(x)` returns the
            square root of `x` as a float. The formula works for a vector with any number of items.

            ```python
            import math

            v = [2, 3, 6]
            squares = [x * x for x in v]
            print(squares, sum(squares))
            # [4, 9, 36] 49
            print(math.sqrt(sum(squares)))
            # 7.0
            ```

            This length is also called the vector's **norm** or **magnitude**. Its full name is the
            **L2 norm**. The square of a negative number is positive, so `[-2, -3, -6]` has the
            same length as `[2, 3, 6]`.

            Two embeddings can have the same direction and different lengths: `[2, 3, 6]` has
            length 7 and `[4, 6, 12]` has length 14. Dividing each vector by its own norm gives
            `[2 / 7, 3 / 7, 6 / 7]` for both, so you compare **direction only**. Cosine similarity,
            later in this chapter, is built on that division.
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
            ## max with a key function

            A **chunk** is a piece of a longer document. **Retrieval** means finding the chunks
            that are relevant to a question. The code gives every chunk a similarity score and
            returns the chunk with the highest score. A dict `{chunk_id: score}` holds the scores.
            `max` finds that chunk if you tell it **which values to compare**.

            ```python
            tokens = {"intro": 480, "setup": 310, "faq": 120}
            print(max(tokens))
            # setup
            print(max(tokens, key=tokens.get))
            # intro
            print(min(tokens, key=tokens.get))
            # faq
            ```

            Looping over a dict gives its **keys**, so `max(tokens)` compares the key strings
            alphabetically. With `key=tokens.get`, `max` calls `tokens.get` on each key and compares
            the returned values. It still returns the **key**. `key=` takes a function, as in the
            sorting chapter.

            With similarity scores, a larger number means more similar, so the best match is the
            maximum. That also holds when every score is negative: `-0.2` is larger than `-0.7`.

            ```python
            scores = {"c1": -0.7, "c2": -0.2}
            print(max(scores, key=scores.get))
            # c2
            ```
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
            ## Dot product

            The **dot product** of two vectors is one number. Multiply the numbers at the same
            position, then add all the products.

            The sign of each product shows whether the two vectors agree at that position. Two
            positive numbers, or two negative numbers, give a positive product and raise the total.
            One positive and one negative number give a negative product and lower the total.

            In this example two users rate the same three answers from `-1` (bad) to `1` (good).

            ```python
            ana = [1, -1, 0.5]
            bo = [1, -0.5, 1]
            products = [x * y for x, y in zip(ana, bo)]
            print(products)
            # [1, 0.5, 0.5]
            print(sum(products))
            # 2.0
            ```

            The two users agree on all three answers, so every product is positive and the total is
            high. Search tools use the same idea. A **vector database** is a program that stores
            embeddings and finds the stored ones most similar to a given vector. It scores the
            stored vectors against the given one with a measure such as the dot product.

            `sum` of an empty sequence is `0`, so two empty vectors give `0` with no special case.

            ```python
            print(sum([]))
            # 0
            ```

            `zip` stops at the end of the shorter list. Check the lengths first and raise
            `ValueError` if they differ.
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
            ## Norm and unit vectors

            A **unit vector** is a vector whose length is exactly 1. To get one, divide every number
            of a vector by the vector's norm. This is called **normalising** the vector. The result
            points in the same **direction** as the original. Only the length changes.

            ```python
            import math

            v = [6, 8]
            n = math.sqrt(sum(x * x for x in v))
            unit = [x / n for x in v]
            print(n, unit)
            # 10.0 [0.6, 0.8]
            print(math.sqrt(sum(x * x for x in unit)))
            # 1.0
            ```

            The squares of `[6, 8]` are `36` and `64`. Their sum is `100` and its square root is
            `10`, so each number is divided by `10`.

            Cosine similarity, a score taught later in this chapter, divides the dot product by
            both norms. For unit vectors both norms are 1, so the dot product **equals** the
            cosine similarity. A program that
            stores normalised vectors needs only the dot product to search. Many embedding APIs
            (services that compute embeddings for you) return vectors that are already normalised.

            A **zero vector** contains only zeros. Its norm is 0 and it has no direction. Dividing
            by that norm raises `ZeroDivisionError`. Check for a norm of 0 first and raise
            `ValueError` with a clear message.
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
            ## Euclidean distance

            Cosine similarity compares the directions of two vectors. **Distance** measures how far
            apart their numbers are. A small distance means the numbers are close, so the texts are
            similar. Some vector databases sort results by distance instead of cosine similarity.

            The distance is the norm of the **difference** of the two vectors. Subtract position by
            position, square each difference, add the squares, and take the square root.

            ```python
            import math

            query, chunk = [1, 1], [4, 5]
            diff = [x - y for x, y in zip(query, chunk)]
            print(diff)
            # [-3, -4]
            print(math.sqrt(sum(d * d for d in diff)))
            # 5.0
            ```

            The squares of `-3` and `-4` are `9` and `16`. Their sum is `25` and its square root
            is `5`.

            This is called the **Euclidean distance** or L2 distance. Identical vectors have
            distance `0`. The order of the arguments does not matter: squaring removes the sign of
            each difference, so the distance from `a` to `b` equals the distance from `b` to `a`.

            The standard library has a function that computes this in one call. Finding it is this
            step's research task. Open the docs of the `math` module and read the function's entry.
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
            ## Mean pooling

            A long document is split into chunks, and each chunk gets its own embedding. Sometimes
            you need **one** vector for the whole document. **Mean pooling** produces it: average
            the chunk vectors position by position.

            ```python
            chunks = [[10, 20], [14, 16], [12, 18]]
            firsts = [row[0] for row in chunks]
            print(firsts, sum(firsts) / len(firsts))
            # [10, 14, 12] 12.0
            columns = list(zip(*chunks))
            print(columns)
            # [(10, 14, 12), (20, 16, 18)]
            ```

            `firsts` holds the number at position 0 of every vector. Their average, `12.0`, is
            position 0 of the mean vector.

            In `zip(*chunks)` the `*` **unpacks** the list: Python passes each inner list as a
            separate argument. The call is the same as `zip([10, 20], [14, 16], [12, 18])`. `zip`
            then yields one tuple per **position**: all the first numbers, then all the second
            numbers. Each tuple is a **column**. The average of each column is one number of the
            mean vector.

            Two inputs go wrong. An empty list of vectors has length 0, so computing the average
            divides by zero. Vectors of different lengths are cut to the shortest one by `zip`.
            Both cases should raise `ValueError`.
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
            ## Top-k results

            A **retriever** is the code that finds the chunks for a question. It usually returns
            the best **k** chunks, where `k` is a number you choose, for example 3. The model then
            gets several sources. Sort the chunks by score, highest first, and keep the first k.
            This is called **top-k** retrieval.

            Two rules make the result predictable:
            - **Best first** means sorting by score in descending order.
            - **Ties** need a rule, so that equal scores always come out in the same order. A common
              rule: equal scores are ordered by id, A to Z.

            A key function can return a **tuple**. Python compares tuples item by item: it compares
            the first items, and looks at the second items only when the first are equal. Negating a
            number reverses its order, so the key `(-score, name)` sorts by score from high to low,
            then by name from A to Z.

            ```python
            ratings = {"cy": 9.5, "ana": 9.8, "bo": 9.5}
            ranked = sorted(ratings.items(), key=lambda item: (-item[1], item[0]))
            print(ranked)
            # [('ana', 9.8), ('bo', 9.5), ('cy', 9.5)]
            print(ranked[:2])
            # [('ana', 9.8), ('bo', 9.5)]
            print(ranked[:10])
            # [('ana', 9.8), ('bo', 9.5), ('cy', 9.5)]
            ```

            `ratings.items()` gives `(key, value)` tuples. The slice `[:k]` keeps the first k. A
            slice that goes past the end returns all the items there are and raises no error.
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
            ## Cosine similarity

            **Cosine similarity** is the dot product of two vectors divided by the product of their
            lengths. The division removes the lengths, so the score depends only on direction. It is
            always between `-1` (opposite directions) and `1` (same direction). The score is `0`
            when the dot product is `0`, as for `[1, 0]` and `[0, 5]`. Such vectors are called
            **perpendicular**, and for embeddings that means the texts are unrelated. Cosine
            similarity is the usual similarity measure for embeddings.

            ```python
            import math

            a = [4, 0]
            b = [3, 4]
            dot = sum(x * y for x, y in zip(a, b))
            len_a = math.sqrt(sum(x * x for x in a))
            len_b = math.sqrt(sum(x * x for x in b))
            print(dot, len_a, len_b)
            # 12 4.0 5.0
            print(dot / (len_a * len_b))
            # 0.6
            ```

            The dot product is `4 * 3 + 0 * 4 = 12`. The lengths are `4` and `5`, so the score is
            `12 / (4 * 5) = 0.6`.

            Drag the vectors until the cosine similarity is `1`, then `0`, then `-1`.

            ```diagram
            {"type":"vectors","title":"Cosine similarity of a and b","a":[4,0],"b":[3,4]}
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
            ## Bag of words

            Before embedding models existed, the vector of a text was a list of **word counts**. A
            **vocabulary** is a fixed list of words, and the vector has one count per vocabulary
            word. This is called a **bag of words**: it records how often each word occurs and
            ignores the order of the words. Here a **token** is one word of the text. Clean the
            tokens first (lowercase them and strip punctuation from both ends), then count.

            ```python
            words = "the cat and the hat".split()
            vocab = ["cat", "the", "dog"]
            print([words.count(w) for w in vocab])
            # [1, 2, 0]
            ```

            Position `i` of the result is the count of `vocab[i]`. `"dog"` does not occur in the
            text, so its count is `0`.
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
