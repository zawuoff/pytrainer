TOPIC = {
    "id": "retrieval",
    "title": "Retrieval",
    "track": "rag",
    "order": 3,
    "requires": ["chunking"],
    "summary": """
        Finding the right chunks for a question: ranking by score, keyword search,
        turning text into vectors with an injected `embed`, cosine top-k, hybrid scoring,
        metadata filters, re-ranking and a tiny in-memory vector store.
    """,
    "concepts": ["top-k", "tokenizing", "keyword overlap", "bag of words", "embed function",
                 "cosine search", "batching", "min-max normalisation", "hybrid search",
                 "metadata filtering", "TF-IDF", "re-ranking", "reciprocal rank fusion",
                 "vector store"],
}

LESSON = r'''
## Retrieval in one sentence

Give every chunk a **score** for the question, sort by score, keep the best `k`
(**top-k**). Everything else in this chapter is a different way to compute the score.

## Two kinds of score

| kind | how | good at | bad at |
| --- | --- | --- | --- |
| **keyword** (lexical) | count shared words; TF-IDF / BM25 weigh rare words higher | exact names, codes, error ids | synonyms ("refund" vs "money back") |
| **semantic** (vector) | `embed(text)` -> vector, cosine similarity with the question vector | meaning, paraphrases | exact rare tokens |

**Hybrid** search combines both: normalise each score to 0..1 (min-max), then
`alpha * semantic + (1 - alpha) * keyword`. **Reciprocal rank fusion** combines ranked lists
instead of scores: `sum(1 / (60 + rank))`.

## Key syntax

```python
import math, re
scores = {"a": 0.2, "b": 0.9, "c": 0.5}
print(sorted(scores, key=scores.get, reverse=True)[:2])   # top-k ids
q = re.findall(r"[a-z0-9]+", "Refund policy?".lower())    # simple tokenizer
d = re.findall(r"[a-z0-9]+", "Our REFUND rules".lower())
print(set(q) & set(d))                                    # keyword overlap
print(math.log(10 / 2))                                   # idf = log(n_docs / df)
```

- `cosine(a, b) = dot(a, b) / (norm(a) * norm(b))`; return `0.0` if a norm is 0.
- Pass the embedding model in as a function (`embed`) so tests can use a **fake** one.
- Embedding APIs take **batches** of texts: send slices of at most `batch_size`.
- **Metadata filters** (`{"source": "faq.md"}`) run **before** ranking: only matching chunks compete.
- **Re-ranking**: a cheap first stage finds ~20-50 candidates, a slower, smarter scorer
  re-orders them and you keep the top few.

## Gotchas

- `sorted(..., reverse=True)` is **stable**: ties keep their original order. Rely on it.
- Normalise before mixing scores: raw keyword counts (0..10) swamp cosine (-1..1).
- min-max with all-equal scores divides by zero: handle it.
- Lowercase **both** the query and the document before comparing words.
- A word that appears in every document has `idf = log(1) = 0`: it can't help rank.
'''

EXERCISES = [
    # ---------------------------------------------------------------- difficulty 0
    {
        "id": "retrieval-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The librarian

            Imagine asking a librarian: "How do refunds work?" They don't read you every book.
            They glance at each shelf, judge how *relevant* each book is, and hand you the best
            two or three. That is **retrieval**, the "R" in RAG.

            In code, "judging relevance" means giving every chunk a **score** (a number: bigger
            = more relevant). Then you sort the chunk ids by score, biggest first, and keep the
            first few.

            ```python
            scores = {"intro": 0.10, "pricing": 0.92, "faq": 0.55}
            ranked = sorted(scores, key=scores.get, reverse=True)
            print(ranked)
            print(ranked[:1])
            ```

            `sorted(scores, ...)` sorts the dict's **keys**. `key=scores.get` means "compare
            the keys by their value". `reverse=True` puts the biggest first.

            Keeping only the best `k` results is called **top-k** retrieval. `k` is usually
            small (3 to 10): the chosen chunks will be pasted into a prompt, and prompts
            have limited room.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            scores = {"refunds": 0.82, "shipping": 0.35, "returns": 0.77, "careers": 0.05}
            ranked = sorted(scores, key=scores.get, reverse=True)
            print(ranked[:2])
            print(len(ranked))
        ''',
        "solution": r'''
            ['refunds', 'returns']
            4
        ''',
        "explanation": r'''
            `sorted` orders the ids by their score, biggest first:
            `['refunds', 'returns', 'shipping', 'careers']`. The slice `[:2]` keeps the top 2.
            `ranked` itself still holds all 4 ids, so `len(ranked)` is `4`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`sorted` on a dict gives back a list of its keys; `key=scores.get` sorts them by their scores.",
            "`reverse=True` means the highest score comes first. Then `[:2]` keeps only two ids.",
            "Order the four ids by score from high to low, print the first two as a list, then print how many ids are in the full list.",
        ],
    },
    {
        "id": "retrieval-s2",
        "title": "Top-k ids",
        "difficulty": 0,
        "lesson": r'''
            ## Keep the best k

            Back to the librarian: you asked for "the best 3 books". If the library only has
            2 relevant ones, you get 2, not an error. If you ask for 0, you get nothing.

            A list slice behaves exactly like that. `items[:k]` gives *at most* `k` items and
            never complains:

            ```python
            ranked = ["pricing", "faq", "intro"]
            print(ranked[:2])
            print(ranked[:10])
            print(ranked[:0])
            ```

            One more useful fact: Python's `sorted` is **stable**. When two items tie, they
            keep the order they already had. For a dict, that's the order the keys were added.

            ```python
            scores = {"a": 0.5, "b": 0.9, "c": 0.5}
            print(sorted(scores, key=scores.get, reverse=True))
            ```

            `"a"` and `"c"` tie at 0.5, so `"a"` stays before `"c"`.
        ''',
        "prompt": r'''
            A retriever has scored every chunk. Return the ids of the best `k` chunks.

            **Write:** fill in the blank (`___`) in `top_k(scores, k)`

            - `scores`: a dict mapping chunk id (`str`) to score (`float`), e.g. `{"a": 0.2, "b": 0.9}`
            - `k`: how many ids to return (`int`, `0` or more)
            - **Returns:** a list of at most `k` ids, highest score first

            **Rules**
            - Change only the `___`.
            - If `k` is bigger than the number of chunks, return all of them.
            - Ties keep the order the ids have in the dict.

            **Examples**
            ```python
            top_k({"a": 0.2, "b": 0.9, "c": 0.5}, 2)    # returns ["b", "c"]
            top_k({"a": 0.2, "b": 0.9}, 5)              # returns ["b", "a"]
            top_k({"x": 0.5, "y": 0.7, "z": 0.5}, 3)    # returns ["y", "x", "z"]
            top_k({"a": 0.2}, 0)                        # returns []
            ```
        ''',
        "starter": r'''
            def top_k(scores, k):
                ranked = sorted(scores, key=scores.get, reverse=___)
                return ranked[:k]
        ''',
        "tests": r'''
            from solution import top_k

            def test_returns_best_two_highest_first():
                got = top_k({"a": 0.2, "b": 0.9, "c": 0.5}, 2)
                assert got == ["b", "c"], f"got {got!r}"

            def test_k_bigger_than_number_of_chunks_returns_all():
                got = top_k({"a": 0.2, "b": 0.9}, 5)
                assert got == ["b", "a"], f"got {got!r}"

            def test_ties_keep_dict_order():
                got = top_k({"x": 0.5, "y": 0.7, "z": 0.5}, 3)
                assert got == ["y", "x", "z"], f"got {got!r}"

            def test_k_zero_returns_empty_list():
                assert top_k({"a": 0.2}, 0) == []
        ''',
        "solution": r'''
            def top_k(scores, k):
                ranked = sorted(scores, key=scores.get, reverse=True)
                return ranked[:k]
        ''',
        "hints": [
            "The blank decides the direction of the sort.",
            "By default `sorted` puts the smallest first. You want the highest score first.",
            "Replace `___` with the boolean value that turns on reversed (descending) order.",
        ],
    },
    {
        "id": "retrieval-s3",
        "title": "Tokenize a query",
        "difficulty": 0,
        "lesson": r'''
            ## Cutting text into word tiles

            Before a computer can compare words, it has to cut the text into pieces, like
            tipping Scrabble tiles out of a bag: `"How do I get a REFUND?"` becomes
            `how`, `do`, `i`, `get`, `a`, `refund`. Punctuation and capital letters would only
            get in the way ("Refund" and "refund?" should match), so we drop them.

            Remember `re.findall` from the regex chapter? It returns every piece of text that
            matches a pattern. The pattern `[a-z0-9]+` means "one or more letters or digits in
            a row", so anything else (spaces, `?`, `-`, `$`) acts as a separator.

            ```python
            import re

            text = "Is GPT-4o cheaper?"
            print(text.lower())
            print(re.findall(r"[a-z0-9]+", text.lower()))
            ```

            Each piece is called a **token**, and this step is called **tokenizing**. (LLMs use
            a fancier tokenizer that cuts words into sub-word pieces, but the idea is the same.)

            Watch out: lowercase *first*. The pattern only matches lowercase letters, so
            capital letters would be treated as separators.
        ''',
        "prompt": r'''
            Keyword search starts by turning text into a list of lowercase words.

            **Write:** `tokenize(text)`

            - `text`: a string, e.g. `"How do I get a REFUND?"`
            - **Returns:** a list of tokens (strings): the runs of letters `a-z` and digits
              `0-9` in the **lowercased** text, in order

            **Rules**
            - Everything that is not a letter or digit (spaces, punctuation, `-`, `$`...) separates tokens.
            - Repeated words are kept (`"a a"` gives `["a", "a"]`).
            - An empty string returns `[]`.
            - `re` is already imported in the starter.

            **Examples**
            ```python
            tokenize("How do I get a REFUND?")   # returns ["how", "do", "i", "get", "a", "refund"]
            tokenize("GPT-4o costs $5")          # returns ["gpt", "4o", "costs", "5"]
            tokenize("")                         # returns []
            ```
        ''',
        "starter": r'''
            import re


            def tokenize(text):
                ...
        ''',
        "tests": r'''
            from solution import tokenize

            def test_lowercases_and_drops_punctuation():
                got = tokenize("How do I get a REFUND?")
                assert got == ["how", "do", "i", "get", "a", "refund"], f"got {got!r}"

            def test_digits_are_kept_and_symbols_split():
                got = tokenize("GPT-4o costs $5")
                assert got == ["gpt", "4o", "costs", "5"], f"got {got!r}"

            def test_repeated_words_are_kept():
                got = tokenize("a a, B")
                assert got == ["a", "a", "b"], f"got {got!r}"

            def test_empty_string_gives_empty_list():
                assert tokenize("") == []
        ''',
        "solution": r'''
            import re


            def tokenize(text):
                return re.findall(r"[a-z0-9]+", text.lower())
        ''',
        "hints": [
            "Use `re.findall` with a pattern for 'letters and digits', on the lowercased text.",
            "Lowercase the whole text first, then collect every run of one or more characters from a-z or 0-9.",
            "1) Call `.lower()` on the text. 2) Pass the pattern `r\"[a-z0-9]+\"` and the lowercased text to `re.findall`. 3) Return the list it gives you.",
        ],
    },
    {
        "id": "retrieval-s4",
        "title": "Fix the keyword score",
        "difficulty": 0,
        "lesson": r'''
            ## The highlighter test

            The simplest relevance score: take a highlighter, mark every word of the question
            that also appears in the document, and count the marked words. More shared words =
            more relevant. This is **keyword** (or *lexical*) search.

            A **set** is perfect for this. It keeps each word once, and `&` gives the words two
            sets have in common (the *intersection*):

            ```python
            question = {"refund", "policy", "refund"}
            document = {"our", "refund", "policy", "is", "simple"}
            print(question)
            print(question & document)
            print(len(question & document))
            ```

            Because a set keeps each word once, asking "refund refund?" doesn't count double.

            Watch out: `"Refund"` and `"refund"` are different strings. Both sides must be
            lowercased, or real matches get missed.
        ''',
        "prompt": r'''
            `overlap_score` should count how many **different** query words also appear in the
            document, ignoring upper/lower case. It misses obvious matches. Find and fix the bug.

            **Write:** fix `overlap_score(query, doc)`

            - `query`: the user's question (`str`), e.g. `"refund policy"`
            - `doc`: a chunk of text (`str`), e.g. `"Our Refund Policy is simple."`
            - **Returns:** an `int`: the number of distinct query words found in the document

            **Rules**
            - Matching ignores case on **both** sides.
            - A query word repeated twice still counts once.
            - No shared words returns `0`.

            **Examples**
            ```python
            overlap_score("refund policy", "Our Refund Policy is simple.")   # returns 2
            overlap_score("Refund refund", "refund in 5 days")               # returns 1
            overlap_score("shipping", "Our refund policy")                   # returns 0
            ```
        ''',
        "starter": r'''
            import re


            def overlap_score(query, doc):
                query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
                doc_words = set(re.findall(r"[a-z0-9]+", doc))
                return len(query_words & doc_words)
        ''',
        "tests": r'''
            from solution import overlap_score

            def test_matches_ignore_case_in_document():
                got = overlap_score("refund policy", "Our Refund Policy is simple.")
                assert got == 2, f"got {got!r}"

            def test_repeated_query_word_counts_once():
                got = overlap_score("Refund refund", "refund in 5 days")
                assert got == 1, f"got {got!r}"

            def test_no_shared_words_gives_zero():
                assert overlap_score("shipping", "Our refund policy") == 0

            def test_uppercase_document_word_matches():
                got = overlap_score("api key", "Set your API KEY first")
                assert got == 2, f"got {got!r}"
        ''',
        "solution": r'''
            import re


            def overlap_score(query, doc):
                query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
                doc_words = set(re.findall(r"[a-z0-9]+", doc.lower()))
                return len(query_words & doc_words)
        ''',
        "hints": [
            "Compare how the query and the document are each turned into words.",
            "The pattern only matches lowercase letters. One of the two texts is not lowercased first, so its capitalised words are lost.",
            "Add `.lower()` to the document text in the second `re.findall` call, just like the query line does.",
        ],
    },
    {
        "id": "retrieval-s5",
        "title": "Bag of words vector",
        "difficulty": 0,
        "lesson": r'''
            ## A tally sheet as a vector

            Cosine similarity needs vectors (lists of numbers), but we have text. Real
            embedding models are big neural networks. You can fake one with a **tally sheet**:
            write a fixed list of words down the side (the **vocabulary**), then for a text,
            count how often each word appears.

            ```python
            vocab = ["refund", "shipping", "days"]
            tokens = ["refund", "in", "5", "days", "refund"]
            vector = [tokens.count(word) for word in vocab]
            print(vector)
            ```

            Every text becomes a list of the same length (one number per vocabulary word), so
            any two texts can be compared with cosine. This is called a **bag of words**:
            the order of the words is thrown away, only the counts remain.

            In tests and prototypes, a function like this plays the role of `embed(text)`.
            It's a *fake embedding*: it matches exact words only, while a real one also
            understands synonyms.
        ''',
        "prompt": r'''
            Turn a text into a count vector over a fixed vocabulary (a fake embedding).

            **Write:** `bag_of_words(text, vocab)`

            - `text`: a string, e.g. `"The cat sat on the cat mat"`
            - `vocab`: a list of lowercase words, e.g. `["cat", "dog", "mat"]`
            - **Returns:** a list of `int`s, same length as `vocab`: how many times each
              vocabulary word appears in the text

            **Rules**
            - Split the text into tokens the same way as before: lowercase it, then take the
              runs of `a-z`/`0-9` (`re.findall(r"[a-z0-9]+", ...)`).
            - Whole tokens only: `"cats"` does not count as `"cat"`.
            - An empty `vocab` returns `[]`.

            **Examples**
            ```python
            bag_of_words("The cat sat on the cat mat", ["cat", "dog", "mat"])   # returns [2, 0, 1]
            bag_of_words("Cats! CAT.", ["cat"])                                  # returns [1]
            bag_of_words("hello", [])                                            # returns []
            ```
        ''',
        "starter": r'''
            import re


            def bag_of_words(text, vocab):
                ...
        ''',
        "tests": r'''
            from solution import bag_of_words

            def test_counts_each_vocab_word():
                got = bag_of_words("The cat sat on the cat mat", ["cat", "dog", "mat"])
                assert got == [2, 0, 1], f"got {got!r}"

            def test_case_insensitive_whole_tokens_only():
                got = bag_of_words("Cats! CAT.", ["cat"])
                assert got == [1], f"got {got!r}"

            def test_empty_vocab_gives_empty_vector():
                assert bag_of_words("hello", []) == []

            def test_vector_follows_vocab_order():
                got = bag_of_words("b b a", ["b", "a", "c"])
                assert got == [2, 1, 0], f"got {got!r}"
        ''',
        "solution": r'''
            import re


            def bag_of_words(text, vocab):
                tokens = re.findall(r"[a-z0-9]+", text.lower())
                return [tokens.count(word) for word in vocab]
        ''',
        "hints": [
            "First tokenize the text, then build one number per vocabulary word.",
            "A list of tokens has a `.count(x)` method. Walk through `vocab` in order and count each word in the tokens.",
            "1) tokens = re.findall on the lowercased text. 2) Return a list comprehension over `vocab` that calls `tokens.count(word)` for each word.",
        ],
    },
    {
        "id": "retrieval-s6",
        "title": "Filter by source",
        "difficulty": 0,
        "lesson": r'''
            ## Only search the right shelf

            If a user asks about the *billing* docs, the librarian doesn't search the cookbook
            shelf at all. Chunks usually carry **metadata**: extra facts about where they came
            from, stored next to the text.

            ```python
            chunk = {
                "id": "c7",
                "text": "Invoices are sent monthly.",
                "metadata": {"source": "billing.md", "year": 2026},
            }
            print(chunk["metadata"]["source"])
            print(chunk["metadata"]["year"] > 2025)
            ```

            **Metadata filtering** throws away the chunks that don't match *before* any scoring
            happens. It's cheap, and it stops a great-sounding chunk from the wrong document
            (an old policy, another customer's file) from sneaking into the answer.

            A list comprehension with an `if` is all it takes:
            `[c for c in chunks if <condition on c>]`.
        ''',
        "prompt": r'''
            Keep only the chunks that came from one source document.

            **Write:** fill in the blank (`___`) in `filter_by_source(chunks, source)`

            - `chunks`: a list of dicts like `{"id": "c1", "text": "...", "metadata": {"source": "faq.md"}}`
            - `source`: the source to keep (`str`), e.g. `"faq.md"`
            - **Returns:** a new list with only the chunks whose `metadata["source"]` equals `source`, in their original order

            **Rules**
            - Change only the `___`.
            - No match returns `[]`.

            **Examples**
            ```python
            chunks = [
                {"id": "c1", "text": "...", "metadata": {"source": "faq.md"}},
                {"id": "c2", "text": "...", "metadata": {"source": "blog.md"}},
                {"id": "c3", "text": "...", "metadata": {"source": "faq.md"}},
            ]
            [c["id"] for c in filter_by_source(chunks, "faq.md")]    # ["c1", "c3"]
            filter_by_source(chunks, "terms.md")                      # returns []
            ```
        ''',
        "starter": r'''
            def filter_by_source(chunks, source):
                return [c for c in chunks if ___]
        ''',
        "tests": r'''
            from solution import filter_by_source

            CHUNKS = [
                {"id": "c1", "text": "a", "metadata": {"source": "faq.md"}},
                {"id": "c2", "text": "b", "metadata": {"source": "blog.md"}},
                {"id": "c3", "text": "c", "metadata": {"source": "faq.md"}},
            ]

            def test_keeps_matching_chunks_in_order():
                got = [c["id"] for c in filter_by_source(CHUNKS, "faq.md")]
                assert got == ["c1", "c3"], f"got {got!r}"

            def test_other_source():
                got = [c["id"] for c in filter_by_source(CHUNKS, "blog.md")]
                assert got == ["c2"], f"got {got!r}"

            def test_no_match_gives_empty_list():
                assert filter_by_source(CHUNKS, "terms.md") == []
        ''',
        "solution": r'''
            def filter_by_source(chunks, source):
                return [c for c in chunks if c["metadata"]["source"] == source]
        ''',
        "hints": [
            "The blank is a condition that is True for chunks you want to keep.",
            "Reach into the chunk's `metadata` dict, read its `source`, and compare it with the `source` argument.",
            "Write: the chunk's `[\"metadata\"][\"source\"]` value `==` source.",
        ],
    },
    # ---------------------------------------------------------------- difficulty 1
    {
        "id": "retrieval-1",
        "title": "Safe cosine similarity",
        "difficulty": 1,
        "lesson": r'''
            ## Arrows pointing the same way

            Remember the vectors chapter: think of each vector as an arrow. **Cosine
            similarity** asks "how much do these two arrows point the same way?", ignoring how
            long they are. `1.0` = same direction, `0.0` = unrelated, `-1.0` = opposite.

            ```python
            import math

            a, b = [1, 2], [2, 4]
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            print(dot / (norm_a * norm_b))
            ```

            In a retriever this runs thousands of times, on real data. Two things go wrong:

            - A text with no known words gives an all-zero vector (a bag of words with no hits).
              Its length is 0, so you'd divide by zero. A retriever should not crash on that:
              the sensible score is `0.0` ("no similarity").
            - Vectors from two different embedding models have different lengths. Comparing
              them is a bug, so fail loudly with a `ValueError`.

            Watch out: `zip` silently stops at the shorter list, so check the lengths yourself.
        ''',
        "prompt": r'''
            A retriever-safe cosine similarity.

            **Write:** `cosine(a, b)`

            - `a`, `b`: lists of numbers (vectors)
            - **Returns:** a `float`: `dot(a, b) / (norm(a) * norm(b))`, where `norm(v)` is
              the square root of the sum of squares

            **Rules**
            - If the lists have different lengths, raise `ValueError`.
            - If either vector has norm `0` (e.g. `[0, 0]`, or empty lists), return `0.0`.
            - Results are compared with a small tolerance (`math.isclose`).

            **Examples**
            ```python
            cosine([1, 2], [2, 4])     # returns 1.0
            cosine([1, 0], [0, 1])     # returns 0.0
            cosine([1, 1], [-1, -1])   # returns -1.0
            cosine([0, 0], [3, 4])     # returns 0.0
            cosine([1, 2], [1, 2, 3])  # raises ValueError
            ```
        ''',
        "starter": r'''
            import math


            def cosine(a, b):
                ...
        ''',
        "tests": r'''
            import math
            from solution import cosine

            def test_same_direction_is_one():
                got = cosine([1, 2], [2, 4])
                assert math.isclose(got, 1.0), f"got {got!r}"

            def test_perpendicular_is_zero():
                got = cosine([1, 0], [0, 1])
                assert math.isclose(got, 0.0, abs_tol=1e-9), f"got {got!r}"

            def test_opposite_is_minus_one():
                got = cosine([1, 1], [-1, -1])
                assert math.isclose(got, -1.0), f"got {got!r}"

            def test_general_case():
                got = cosine([1, 2, 3], [4, 5, 6])
                assert math.isclose(got, 32 / (math.sqrt(14) * math.sqrt(77))), f"got {got!r}"

            def test_zero_vector_gives_zero():
                assert cosine([0, 0], [3, 4]) == 0
                assert cosine([], []) == 0

            def test_different_lengths_raise_value_error():
                try:
                    cosine([1, 2], [1, 2, 3])
                except ValueError:
                    return
                assert False, "expected ValueError"
        ''',
        "solution": r'''
            import math


            def cosine(a, b):
                if len(a) != len(b):
                    raise ValueError("vectors must have the same length")
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)
        ''',
        "hints": [
            "You need a length check, two norms, a zero check and a dot product.",
            "Check the lengths first and raise if they differ. Compute both norms; if either is 0 return 0.0 before dividing. Otherwise divide the dot product by the product of the norms.",
            "1) `if len(a) != len(b): raise ValueError(...)`. 2) norm = math.sqrt(sum of squares) for each. 3) If a norm is 0, return 0.0. 4) Return sum(x * y over zip(a, b)) divided by norm_a * norm_b.",
        ],
    },
    {
        "id": "retrieval-2",
        "title": "Semantic search",
        "difficulty": 1,
        "lesson": r'''
            ## Asking by meaning

            Semantic search is the librarian who understands what you *mean*. The recipe:

            1. Every chunk was embedded once, ahead of time, and stored with its vector.
            2. When a question comes in, embed the question too (the **query vector**).
            3. Score every chunk: `cosine(query_vector, chunk_vector)`.
            4. Sort by score, keep the top `k`.

            ```python
            chunks = [{"id": "a", "vector": [1, 0]}, {"id": "b", "vector": [0.6, 0.8]}]
            query_vec = [0.8, 0.6]
            for c in chunks:
                dot = sum(x * y for x, y in zip(query_vec, c["vector"]))
                print(c["id"], round(dot, 2))
            ```

            (Here every vector already has length 1, so the dot product *is* the cosine.)

            Returning `(id, score)` pairs instead of bare ids is common: the score is useful
            later, for example to refuse to answer when even the best match is weak.

            A **tuple** is a good fit for a pair: `("b", 0.96)`. Sorting a list of pairs by
            the score uses `key=lambda pair: pair[1]`, or a small named function.
        ''',
        "prompt": r'''
            Rank stored chunks by cosine similarity to a query vector.

            **Write:** `semantic_search(query_vec, chunks, k)`

            - `query_vec`: a list of numbers, e.g. `[1, 0]`
            - `chunks`: a list of dicts like `{"id": "c1", "vector": [0.6, 0.8]}`
            - `k`: maximum number of results (`int`)
            - **Returns:** a list of `(id, score)` tuples, highest cosine score first, at most `k` long

            **Rules**
            - Score = cosine similarity. A zero vector scores `0.0` (write your own `cosine`
              helper in the same file, like in the previous step).
            - Ties keep the order the chunks had in `chunks`.
            - Don't change `chunks`.
            - No chunks returns `[]`. Scores are checked with a small tolerance.

            **Examples**
            ```python
            chunks = [
                {"id": "a", "vector": [1, 0]},
                {"id": "b", "vector": [0, 1]},
                {"id": "c", "vector": [1, 1]},
            ]
            semantic_search([1, 0], chunks, 2)   # returns [("a", 1.0), ("c", 0.7071...)]
            semantic_search([0, 1], chunks, 1)   # returns [("b", 1.0)]
            semantic_search([1, 0], [], 3)       # returns []
            ```
        ''',
        "starter": r'''
            import math


            def semantic_search(query_vec, chunks, k):
                ...
        ''',
        "tests": r'''
            import math
            from solution import semantic_search

            CHUNKS = [
                {"id": "a", "vector": [1, 0]},
                {"id": "b", "vector": [0, 1]},
                {"id": "c", "vector": [1, 1]},
            ]

            def test_returns_top_two_pairs():
                got = semantic_search([1, 0], CHUNKS, 2)
                assert [g[0] for g in got] == ["a", "c"], f"got {got!r}"
                assert math.isclose(got[0][1], 1.0), f"got {got!r}"
                assert math.isclose(got[1][1], 1 / math.sqrt(2)), f"got {got!r}"

            def test_results_are_tuples():
                got = semantic_search([0, 1], CHUNKS, 1)
                assert len(got) == 1 and isinstance(got[0], tuple), f"got {got!r}"
                assert got[0][0] == "b", f"got {got!r}"

            def test_uses_cosine_not_raw_dot_product():
                chunks = [{"id": "long", "vector": [10, 10]}, {"id": "exact", "vector": [1, 0]}]
                got = semantic_search([1, 0], chunks, 1)
                assert got[0][0] == "exact", f"got {got!r} (a long vector should not win just by being long)"

            def test_ties_keep_input_order_and_zero_vector_scores_zero():
                chunks = [{"id": "z", "vector": [0, 0]}, {"id": "p", "vector": [2, 0]}, {"id": "q", "vector": [5, 0]}]
                got = semantic_search([1, 0], chunks, 3)
                assert [g[0] for g in got] == ["p", "q", "z"], f"got {got!r}"
                assert got[2][1] == 0, f"got {got!r}"

            def test_no_chunks_gives_empty_list():
                assert semantic_search([1, 0], [], 3) == []
        ''',
        "solution": r'''
            import math


            def cosine(a, b):
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


            def semantic_search(query_vec, chunks, k):
                scored = [(c["id"], cosine(query_vec, c["vector"])) for c in chunks]
                scored.sort(key=lambda pair: pair[1], reverse=True)
                return scored[:k]
        ''',
        "hints": [
            "Score every chunk with a cosine helper, then sort the (id, score) pairs by score.",
            "Build a list of tuples `(chunk id, cosine(query_vec, chunk vector))`, sort it descending by the second item of each tuple, and slice off the first `k`.",
            "1) Write `cosine(a, b)` that returns 0.0 for a zero norm. 2) scored = list comprehension of (c[\"id\"], cosine(...)) tuples. 3) Sort with key=lambda pair: pair[1] and reverse=True. 4) Return scored[:k].",
        ],
    },
    {
        "id": "retrieval-3",
        "title": "Embed in batches",
        "difficulty": 1,
        "lesson": r'''
            ## The stunt double and the grocery bags

            A real embedding model lives behind an API: it costs money, needs a network and
            an API key. So your code shouldn't create the client itself. It should **receive**
            the embed function as an argument. In production you pass the real one; in tests
            you pass a **fake** (a stunt double that looks the same from the outside).

            ```python
            def fake_embed(texts):
                return [[len(t), t.count("a")] for t in texts]

            def embed_all(texts, embed):
                return embed(texts)

            print(embed_all(["banana", "kiwi"], fake_embed))
            ```

            Embedding APIs take a **list** of texts per request (a *batch*), with a maximum
            batch size. With 1,000 chunks and a limit of 100, you carry the groceries in 10
            bags: slice the list into pieces of at most 100 and call the API once per piece.

            ```python
            items = ["a", "b", "c", "d", "e"]
            for start in range(0, len(items), 2):
                print(items[start:start + 2])
            ```

            Passing a function in like this is called **dependency injection**.
        ''',
        "research": {
            "note": "Skim the embeddings guide: see how an embeddings request takes a list of inputs and returns one vector per input, in the same order.",
            "links": [
                {"title": "Vector embeddings - OpenAI API docs", "url": "https://platform.openai.com/docs/guides/embeddings"},
            ],
        },
        "prompt": r'''
            Embed many texts with an API that accepts at most `batch_size` texts per call.

            **Write:** `embed_in_batches(texts, embed, batch_size)`

            - `texts`: a list of strings
            - `embed`: a function that takes a **list** of strings and returns a list of
              vectors (one per text, same order), like a real embeddings API
            - `batch_size`: maximum number of texts per `embed` call (`int`)
            - **Returns:** one list with all the vectors, in the same order as `texts`

            **Rules**
            - Call `embed` once per batch of consecutive texts: the first `batch_size` texts,
              then the next `batch_size`, and so on (the last batch may be smaller).
            - If `texts` is empty, return `[]` without calling `embed`.
            - If `batch_size` is less than `1`, raise `ValueError`.

            **Examples**
            ```python
            def fake_embed(batch):
                return [[len(t)] for t in batch]

            embed_in_batches(["a", "bb", "ccc"], fake_embed, 2)
            # calls fake_embed(["a", "bb"]) then fake_embed(["ccc"])
            # returns [[1], [2], [3]]
            embed_in_batches([], fake_embed, 2)       # returns [] (embed not called)
            embed_in_batches(["a"], fake_embed, 0)    # raises ValueError
            ```
        ''',
        "starter": r'''
            def embed_in_batches(texts, embed, batch_size):
                ...
        ''',
        "tests": r'''
            from solution import embed_in_batches

            def make_fake():
                calls = []
                def fake_embed(batch):
                    calls.append(list(batch))
                    return [[len(t)] for t in batch]
                return fake_embed, calls

            def test_returns_all_vectors_in_order():
                fake, calls = make_fake()
                got = embed_in_batches(["a", "bb", "ccc"], fake, 2)
                assert got == [[1], [2], [3]], f"got {got!r}"

            def test_calls_embed_once_per_batch():
                fake, calls = make_fake()
                embed_in_batches(["a", "bb", "ccc", "dddd", "e"], fake, 2)
                assert calls == [["a", "bb"], ["ccc", "dddd"], ["e"]], f"embed was called with {calls!r}"

            def test_batch_bigger_than_list_is_one_call():
                fake, calls = make_fake()
                embed_in_batches(["a", "bb"], fake, 10)
                assert calls == [["a", "bb"]], f"embed was called with {calls!r}"

            def test_empty_texts_do_not_call_embed():
                fake, calls = make_fake()
                assert embed_in_batches([], fake, 2) == []
                assert calls == [], f"embed was called with {calls!r}"

            def test_batch_size_below_one_raises_value_error():
                fake, calls = make_fake()
                try:
                    embed_in_batches(["a"], fake, 0)
                except ValueError:
                    return
                assert False, "expected ValueError"
        ''',
        "solution": r'''
            def embed_in_batches(texts, embed, batch_size):
                if batch_size < 1:
                    raise ValueError("batch_size must be at least 1")
                vectors = []
                for start in range(0, len(texts), batch_size):
                    vectors.extend(embed(texts[start:start + batch_size]))
                return vectors
        ''',
        "hints": [
            "Use `range(start, stop, step)` with a step of `batch_size` to walk through the list in slices.",
            "Check `batch_size` first. Then for each start position 0, batch_size, 2*batch_size..., slice out a batch, call `embed` on it, and add the returned vectors to a result list.",
            "1) If batch_size < 1: raise ValueError. 2) vectors = []. 3) for start in range(0, len(texts), batch_size): vectors.extend(embed(texts[start:start + batch_size])). 4) Return vectors.",
        ],
    },
    {
        "id": "retrieval-4",
        "title": "Min-max normalisation",
        "difficulty": 1,
        "lesson": r'''
            ## Apples and oranges

            Two judges score the same chunks. The keyword judge gives points from 0 to 12. The
            semantic judge gives cosine scores between -1 and 1. If you just add them, the
            keyword judge wins every time, simply because its numbers are bigger.

            The fix: put both on the same 0-to-1 ruler first. **Min-max normalisation** maps
            the lowest score to `0.0`, the highest to `1.0`, and everything else in between:

            `(score - lowest) / (highest - lowest)`

            ```python
            scores = {"a": 2, "b": 12, "c": 7}
            low, high = min(scores.values()), max(scores.values())
            for cid, s in scores.items():
                print(cid, (s - low) / (high - low))
            ```

            Watch out: if every score is the same, `highest - lowest` is `0` and you'd divide
            by zero. All chunks are equally good then, so give each one `1.0`.

            A **dict comprehension** (`{k: ... for k, v in d.items()}`) builds the new dict and
            leaves the original untouched.
        ''',
        "prompt": r'''
            Rescale scores to the range 0..1 so different scorers can be combined.

            **Write:** `min_max(scores)`

            - `scores`: a dict mapping chunk id (`str`) to a number, e.g. `{"a": 2, "b": 12, "c": 7}`
            - **Returns:** a **new** dict with the same keys, each value mapped to
              `(value - lowest) / (highest - lowest)` as a `float`

            **Rules**
            - If all scores are equal (including a single score), every value becomes `1.0`.
            - An empty dict returns `{}`.
            - Don't change the dict you were given.
            - Values are checked with a small tolerance.

            **Examples**
            ```python
            min_max({"a": 2, "b": 12, "c": 7})      # returns {"a": 0.0, "b": 1.0, "c": 0.5}
            min_max({"x": -0.5, "y": 0.5})          # returns {"x": 0.0, "y": 1.0}
            min_max({"a": 3, "b": 3})               # returns {"a": 1.0, "b": 1.0}
            min_max({})                             # returns {}
            ```
        ''',
        "starter": r'''
            def min_max(scores):
                ...
        ''',
        "tests": r'''
            import math
            from solution import min_max

            def close_dicts(got, want):
                return got.keys() == want.keys() and all(math.isclose(got[k], want[k], abs_tol=1e-9) for k in want)

            def test_maps_lowest_to_zero_and_highest_to_one():
                got = min_max({"a": 2, "b": 12, "c": 7})
                assert close_dicts(got, {"a": 0.0, "b": 1.0, "c": 0.5}), f"got {got!r}"

            def test_negative_scores():
                got = min_max({"x": -0.5, "y": 0.5, "z": 0.0})
                assert close_dicts(got, {"x": 0.0, "y": 1.0, "z": 0.5}), f"got {got!r}"

            def test_all_equal_scores_become_one():
                got = min_max({"a": 3, "b": 3})
                assert close_dicts(got, {"a": 1.0, "b": 1.0}), f"got {got!r}"
                got = min_max({"only": 0.2})
                assert close_dicts(got, {"only": 1.0}), f"got {got!r}"

            def test_empty_dict_gives_empty_dict():
                assert min_max({}) == {}

            def test_input_is_not_changed():
                scores = {"a": 2, "b": 12}
                min_max(scores)
                assert scores == {"a": 2, "b": 12}, f"input changed to {scores!r}"
        ''',
        "solution": r'''
            def min_max(scores):
                if not scores:
                    return {}
                low = min(scores.values())
                high = max(scores.values())
                if high == low:
                    return {cid: 1.0 for cid in scores}
                return {cid: (s - low) / (high - low) for cid, s in scores.items()}
        ''',
        "hints": [
            "You need the smallest and largest value (`min` and `max` on `scores.values()`), then a dict comprehension.",
            "Handle the empty dict first. Find low and high. If they're equal, every id gets 1.0. Otherwise map each score with (score - low) / (high - low).",
            "1) if not scores: return {}. 2) low, high = min(...), max(...) of the values. 3) if high == low: return {cid: 1.0 for cid in scores}. 4) return {cid: (s - low) / (high - low) for cid, s in scores.items()}.",
        ],
    },
    {
        "id": "retrieval-5",
        "title": "Hybrid score",
        "difficulty": 1,
        "lesson": r'''
            ## Two judges, one verdict

            Keyword search is great at exact things: product codes, error ids, names
            ("ERR_4012"). Semantic search is great at meaning ("money back" finds "refund").
            Each misses what the other catches, so good retrievers ask **both** judges and
            blend the verdicts. This is **hybrid search**.

            After min-max normalisation, both scores are on a 0-to-1 ruler, so you can take a
            weighted average. The weight `alpha` says how much you trust the semantic judge:

            `hybrid = alpha * semantic + (1 - alpha) * keyword`

            ```python
            alpha = 0.7
            keyword, semantic = 1.0, 0.2
            print(alpha * semantic + (1 - alpha) * keyword)
            print(0.5 * semantic + 0.5 * keyword)
            ```

            A chunk might be found by only one judge (it had zero shared words, or it wasn't
            in the semantic top list). Treat the missing score as `0`. `d.get(key, 0)`
            does exactly that.

            Watch out: `alpha` must stay between 0 and 1, or one judge gets a negative weight.
        ''',
        "prompt": r'''
            Blend already-normalised keyword and semantic scores into one hybrid score.

            **Write:** `hybrid(keyword, semantic, alpha=0.5)`

            - `keyword`: dict of chunk id -> keyword score (0..1)
            - `semantic`: dict of chunk id -> semantic score (0..1)
            - `alpha`: weight of the semantic score (`float`, default `0.5`)
            - **Returns:** a dict with **every id that appears in either dict**, mapped to
              `alpha * semantic + (1 - alpha) * keyword`

            **Rules**
            - An id missing from one of the dicts counts as score `0` there.
            - If `alpha` is below `0` or above `1`, raise `ValueError`.
            - Values are checked with a small tolerance; key order doesn't matter.

            **Examples**
            ```python
            hybrid({"a": 1.0, "b": 0.5}, {"a": 0.2, "c": 1.0})
            # returns {"a": 0.6, "b": 0.25, "c": 0.5}
            hybrid({"a": 1.0}, {"a": 0.0}, alpha=0.8)    # returns {"a": 0.2}
            hybrid({}, {})                               # returns {}
            hybrid({"a": 1.0}, {}, alpha=1.5)            # raises ValueError
            ```
        ''',
        "starter": r'''
            def hybrid(keyword, semantic, alpha=0.5):
                ...
        ''',
        "tests": r'''
            import math
            from solution import hybrid

            def close_dicts(got, want):
                return got.keys() == want.keys() and all(math.isclose(got[k], want[k], abs_tol=1e-9) for k in want)

            def test_blends_with_default_alpha_and_fills_missing_ids():
                got = hybrid({"a": 1.0, "b": 0.5}, {"a": 0.2, "c": 1.0})
                assert close_dicts(got, {"a": 0.6, "b": 0.25, "c": 0.5}), f"got {got!r}"

            def test_alpha_weights_the_semantic_score():
                got = hybrid({"a": 1.0}, {"a": 0.0}, alpha=0.8)
                assert close_dicts(got, {"a": 0.2}), f"got {got!r}"
                got = hybrid({"a": 1.0}, {"a": 0.0}, alpha=0.0)
                assert close_dicts(got, {"a": 1.0}), f"got {got!r}"

            def test_empty_inputs_give_empty_dict():
                assert hybrid({}, {}) == {}

            def test_alpha_out_of_range_raises_value_error():
                for bad in (1.5, -0.1):
                    try:
                        hybrid({"a": 1.0}, {}, alpha=bad)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for alpha={bad}"
        ''',
        "solution": r'''
            def hybrid(keyword, semantic, alpha=0.5):
                if not 0 <= alpha <= 1:
                    raise ValueError("alpha must be between 0 and 1")
                ids = set(keyword) | set(semantic)
                return {
                    cid: alpha * semantic.get(cid, 0) + (1 - alpha) * keyword.get(cid, 0)
                    for cid in ids
                }
        ''',
        "hints": [
            "Collect the ids from both dicts (a set union with `|` works), then use `.get(id, 0)` for each score.",
            "Validate alpha first. Then for every id found in either dict, compute alpha times its semantic score plus (1 - alpha) times its keyword score, using 0 when missing.",
            "1) if not 0 <= alpha <= 1: raise ValueError. 2) ids = set(keyword) | set(semantic). 3) Return a dict comprehension over ids with alpha * semantic.get(cid, 0) + (1 - alpha) * keyword.get(cid, 0).",
        ],
    },
    # ---------------------------------------------------------------- difficulty 2
    {
        "id": "retrieval-6",
        "title": "Filtered semantic search",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            Putting it together: filter by metadata first (only the right shelf), then rank the
            survivors by cosine similarity and keep the top `k`.
        ''',
        "prompt": r'''
            Search only the chunks whose metadata matches a filter, ranked by cosine similarity.

            **Write:** `filtered_search(query_vec, chunks, k, where=None)`

            - `query_vec`: a list of numbers
            - `chunks`: a list of dicts like `{"id": "c1", "vector": [1, 0], "metadata": {"source": "faq.md", "lang": "en"}}`
            - `k`: maximum number of results (`int`)
            - `where`: a dict of metadata requirements, e.g. `{"lang": "en"}`, or `None`
            - **Returns:** a list of chunk **ids**, best cosine score first, at most `k` long

            **Rules**
            - A chunk matches `where` only if **every** key in `where` is in its metadata with
              an **equal** value. A missing key means no match.
            - `where=None` or `{}` means every chunk matches.
            - Score = cosine similarity; a zero vector scores `0.0`.
            - Ties keep the order the chunks had in `chunks`.
            - No matching chunks returns `[]`.

            **Examples**
            ```python
            chunks = [
                {"id": "a", "vector": [1, 0], "metadata": {"lang": "en", "year": 2024}},
                {"id": "b", "vector": [1, 1], "metadata": {"lang": "fr", "year": 2026}},
                {"id": "c", "vector": [0, 1], "metadata": {"lang": "en", "year": 2026}},
            ]
            filtered_search([1, 0], chunks, 3)                                   # ["a", "b", "c"]
            filtered_search([1, 0], chunks, 3, where={"lang": "en"})             # ["a", "c"]
            filtered_search([1, 0], chunks, 3, where={"lang": "en", "year": 2026})  # ["c"]
            filtered_search([1, 0], chunks, 3, where={"team": "x"})              # []
            ```
        ''',
        "starter": r'''
            import math


            def filtered_search(query_vec, chunks, k, where=None):
                ...
        ''',
        "tests": r'''
            from solution import filtered_search

            CHUNKS = [
                {"id": "a", "vector": [1, 0], "metadata": {"lang": "en", "year": 2024}},
                {"id": "b", "vector": [1, 1], "metadata": {"lang": "fr", "year": 2026}},
                {"id": "c", "vector": [0, 1], "metadata": {"lang": "en", "year": 2026}},
            ]

            def test_no_filter_ranks_all_chunks():
                got = filtered_search([1, 0], CHUNKS, 3)
                assert got == ["a", "b", "c"], f"got {got!r}"

            def test_empty_filter_same_as_none():
                got = filtered_search([0, 1], CHUNKS, 2, where={})
                assert got == ["c", "b"], f"got {got!r}"

            def test_single_key_filter():
                got = filtered_search([1, 0], CHUNKS, 3, where={"lang": "en"})
                assert got == ["a", "c"], f"got {got!r}"

            def test_every_key_must_match():
                got = filtered_search([1, 0], CHUNKS, 3, where={"lang": "en", "year": 2026})
                assert got == ["c"], f"got {got!r}"

            def test_missing_metadata_key_means_no_match():
                assert filtered_search([1, 0], CHUNKS, 3, where={"team": "x"}) == []

            def test_k_limits_results_and_ties_keep_order():
                chunks = [
                    {"id": "p", "vector": [2, 0], "metadata": {}},
                    {"id": "z", "vector": [0, 0], "metadata": {}},
                    {"id": "q", "vector": [3, 0], "metadata": {}},
                ]
                got = filtered_search([1, 0], chunks, 2)
                assert got == ["p", "q"], f"got {got!r}"
        ''',
        "solution": r'''
            import math


            def cosine(a, b):
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


            def matches(metadata, where):
                return all(key in metadata and metadata[key] == value for key, value in where.items())


            def filtered_search(query_vec, chunks, k, where=None):
                where = where or {}
                kept = [c for c in chunks if matches(c["metadata"], where)]
                kept.sort(key=lambda c: cosine(query_vec, c["vector"]), reverse=True)
                return [c["id"] for c in kept[:k]]
        ''',
        "hints": [
            "Split it in two helpers: one that says whether a metadata dict matches `where`, and a cosine function.",
            "Treat `None` like an empty dict. Keep the chunks where every (key, value) of `where` is present and equal in the metadata. Sort those by cosine with the query, highest first, and return the first k ids.",
            "1) where = where or {}. 2) matches = all(key in md and md[key] == value for key, value in where.items()). 3) kept = [c for c in chunks if matches]. 4) Sort kept with key=cosine to query, reverse=True. 5) Return ids of kept[:k].",
        ],
    },
    {
        "id": "retrieval-7",
        "title": "TF-IDF keyword search",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: plain word overlap treats "the" and "invoice" as equally
            useful. **TF-IDF** weighs each query word by how rare it is across all documents:
            `idf = log(number_of_docs / docs_containing_word)`. A word in every document gets
            `log(1) = 0` and stops mattering; a rare word counts a lot. The score of a document
            adds up `count of the word in the doc * idf` over the query words.
        ''',
        "prompt": r'''
            Rank documents with a small TF-IDF keyword scorer.

            **Write:** `tfidf_search(query, docs, k)`

            - `query`: the question (`str`)
            - `docs`: a dict of doc id -> text, e.g. `{"d1": "refund in 5 days", ...}`
            - `k`: maximum number of results (`int`)
            - **Returns:** a list of doc ids, best score first, at most `k` long

            **Scoring**
            - Tokenize every text with `re.findall(r"[a-z0-9]+", text.lower())`.
            - Use each **distinct** query token once. For a query token `t`:
              `df` = number of docs whose tokens contain `t`; if `df` is `0`, skip `t`;
              otherwise `idf = math.log(len(docs) / df)`.
            - A doc's score is the sum over the query tokens of
              `(how many times t appears in the doc's tokens) * idf`.

            **Rules**
            - Only return docs with a score **greater than 0**.
            - Ties keep the order of `docs`.
            - Empty `docs` returns `[]`.

            **Examples**
            ```python
            docs = {
                "d1": "the refund takes 5 days",
                "d2": "the invoice is sent monthly, the invoice is a pdf",
                "d3": "the shipping takes 2 days",
            }
            tfidf_search("the invoice", docs, 3)       # returns ["d2"]   ("the" is in every doc: idf 0)
            tfidf_search("refund days", docs, 3)       # returns ["d1", "d3"]
            tfidf_search("warranty", docs, 3)          # returns []
            ```
        ''',
        "starter": r'''
            import math
            import re


            def tfidf_search(query, docs, k):
                ...
        ''',
        "tests": r'''
            from solution import tfidf_search

            DOCS = {
                "d1": "the refund takes 5 days",
                "d2": "the invoice is sent monthly, the invoice is a pdf",
                "d3": "the shipping takes 2 days",
            }

            def test_word_in_every_doc_does_not_count():
                got = tfidf_search("the invoice", DOCS, 3)
                assert got == ["d2"], f"got {got!r}"

            def test_rare_word_outweighs_common_word():
                got = tfidf_search("refund days", DOCS, 3)
                assert got == ["d1", "d3"], f"got {got!r}"

            def test_term_frequency_matters():
                docs = {"a": "invoice", "b": "invoice invoice", "c": "hello"}
                got = tfidf_search("invoice", docs, 2)
                assert got == ["b", "a"], f"got {got!r}"

            def test_query_words_counted_once_and_case_ignored():
                docs = {"a": "Refund policy", "b": "shipping policy", "c": "careers"}
                got = tfidf_search("REFUND refund", docs, 5)
                assert got == ["a"], f"got {got!r}"

            def test_no_matching_words_gives_empty_list():
                assert tfidf_search("warranty", DOCS, 3) == []
                assert tfidf_search("anything", {}, 3) == []

            def test_k_limits_results():
                got = tfidf_search("takes", DOCS, 1)
                assert got == ["d1"], f"got {got!r}"
        ''',
        "solution": r'''
            import math
            import re


            def tokenize(text):
                return re.findall(r"[a-z0-9]+", text.lower())


            def tfidf_search(query, docs, k):
                tokens = {doc_id: tokenize(text) for doc_id, text in docs.items()}
                scores = {doc_id: 0.0 for doc_id in docs}
                for term in set(tokenize(query)):
                    df = sum(1 for toks in tokens.values() if term in toks)
                    if df == 0:
                        continue
                    idf = math.log(len(docs) / df)
                    for doc_id, toks in tokens.items():
                        scores[doc_id] += toks.count(term) * idf
                ranked = sorted((d for d in docs if scores[d] > 0), key=scores.get, reverse=True)
                return ranked[:k]
        ''',
        "hints": [
            "Tokenize every doc once up front (a dict of id -> tokens), then loop over the distinct query tokens.",
            "Start every doc at score 0. For each distinct query token, count how many docs contain it (df); skip it if df is 0, else compute idf and add count * idf to each doc's score. Finally keep docs with score > 0 and sort them.",
            "1) tokens = {id: tokenize(text)}. 2) scores = {id: 0.0}. 3) for term in set(tokenize(query)): df = number of token lists containing term; skip if 0; idf = math.log(len(docs) / df); add toks.count(term) * idf to each score. 4) Sort the ids with score > 0 by score, reverse=True, return [:k].",
        ],
    },
    {
        "id": "retrieval-8",
        "title": "Re-rank candidates",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: the first retrieval stage is fast but rough, so it fetches a
            generous list of candidates. A **re-ranker** (a slower, smarter model that reads
            the question and a candidate together) scores only those candidates, and you keep
            the best few. The re-ranker is injected as a function, so tests can fake it.
        ''',
        "prompt": r'''
            Re-order first-stage candidates with a (slow) scoring function and keep the best.

            **Write:** `rerank(query, candidates, score_fn, k)`

            - `query`: the question (`str`)
            - `candidates`: a list of dicts like `{"id": "c1", "text": "..."}` (from a first search)
            - `score_fn`: a function `score_fn(query, text)` returning a number (bigger = more relevant)
            - `k`: how many ids to keep (`int`)
            - **Returns:** a list of at most `k` candidate ids, highest `score_fn` score first

            **Rules**
            - Call `score_fn` **exactly once per candidate** (it's slow and costs money).
            - Ties keep the candidates' original order.
            - Don't change `candidates`.
            - No candidates returns `[]` (and `score_fn` is never called).

            **Examples**
            ```python
            def fake_score(query, text):
                return text.count(query)

            cands = [{"id": "a", "text": "x"}, {"id": "b", "text": "x x x"}, {"id": "c", "text": "x x"}]
            rerank("x", cands, fake_score, 2)    # returns ["b", "c"]
            rerank("x", [], fake_score, 2)       # returns []
            ```
        ''',
        "starter": r'''
            def rerank(query, candidates, score_fn, k):
                ...
        ''',
        "tests": r'''
            from solution import rerank

            def make_scorer():
                calls = []
                def score(query, text):
                    calls.append(text)
                    return text.count(query)
                return score, calls

            CANDS = [{"id": "a", "text": "x"}, {"id": "b", "text": "x x x"}, {"id": "c", "text": "x x"}]

            def test_orders_by_score_and_keeps_k():
                score, calls = make_scorer()
                got = rerank("x", CANDS, score, 2)
                assert got == ["b", "c"], f"got {got!r}"

            def test_score_fn_called_once_per_candidate():
                score, calls = make_scorer()
                rerank("x", CANDS, score, 3)
                assert sorted(calls) == sorted(c["text"] for c in CANDS), f"score_fn was called for {calls!r}"

            def test_ties_keep_original_order():
                score, calls = make_scorer()
                cands = [{"id": "p", "text": "x"}, {"id": "q", "text": "none"}, {"id": "r", "text": "x"}]
                got = rerank("x", cands, score, 3)
                assert got == ["p", "r", "q"], f"got {got!r}"

            def test_candidates_not_changed():
                score, calls = make_scorer()
                cands = [dict(c) for c in CANDS]
                rerank("x", cands, score, 3)
                assert cands == CANDS, f"candidates changed to {cands!r}"

            def test_no_candidates():
                score, calls = make_scorer()
                assert rerank("x", [], score, 2) == []
                assert calls == []
        ''',
        "solution": r'''
            def rerank(query, candidates, score_fn, k):
                scored = [(score_fn(query, c["text"]), c["id"]) for c in candidates]
                scored.sort(key=lambda pair: pair[0], reverse=True)
                return [cid for _, cid in scored[:k]]
        ''',
        "hints": [
            "Compute every score once, store it next to the id, then sort those pairs.",
            "Build a list of (score, id) pairs with one `score_fn` call each. Sort by the score only (so ties stay in order), highest first, then take the ids of the first k.",
            "1) scored = [(score_fn(query, c[\"text\"]), c[\"id\"]) for c in candidates]. 2) scored.sort(key=lambda pair: pair[0], reverse=True). 3) Return the ids from scored[:k].",
        ],
    },
    {
        "id": "retrieval-9",
        "title": "Reciprocal rank fusion",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: instead of mixing *scores* (which live on different scales),
            **reciprocal rank fusion** (RRF) mixes *positions*. Each ranked list gives an id
            `1 / (k + rank)` points, where `rank` starts at 1 and `k` is a constant (60 is
            the usual choice). Ids near the top of several lists win.
        ''',
        "prompt": r'''
            Merge several ranked lists of ids (e.g. keyword results and semantic results) with RRF.

            **Write:** `rrf(rankings, k=60)`

            - `rankings`: a list of ranked lists of ids, best first, e.g. `[["a", "b"], ["b", "c"]]`
            - `k`: the smoothing constant (`int`, default `60`)
            - **Returns:** a list of every id that appears in any ranking, best fused score first

            **Rules**
            - An id at position `rank` (1 for the first item) in a list earns `1 / (k + rank)` points from that list.
            - An id's fused score is the sum of its points from every list it appears in.
            - Equal fused scores are ordered alphabetically by id.
            - Empty `rankings` (or only empty lists) returns `[]`.

            **Examples**
            ```python
            rrf([["a", "b"], ["b", "c"]])             # returns ["b", "a", "c"]
            rrf([["b", "a"], ["a", "b"]])             # returns ["a", "b"]   (a tie: alphabetical)
            rrf([["x", "y"]], k=0)                    # returns ["x", "y"]
            rrf([])                                   # returns []
            ```
        ''',
        "starter": r'''
            def rrf(rankings, k=60):
                ...
        ''',
        "tests": r'''
            from solution import rrf

            def test_id_high_in_both_lists_wins():
                got = rrf([["a", "b"], ["b", "c"]])
                assert got == ["b", "a", "c"], f"got {got!r}"

            def test_ties_are_alphabetical():
                got = rrf([["b", "a"], ["a", "b"]])
                assert got == ["a", "b"], f"got {got!r}"

            def test_uses_the_k_constant():
                lists = [["x", "y"], ["a", "y", "b", "c", "x"]]
                assert rrf(lists, k=0) == ["x", "a", "y", "b", "c"], f"got {rrf(lists, k=0)!r}"
                assert rrf(lists) == ["y", "x", "a", "b", "c"], f"got {rrf(lists)!r}"

            def test_ids_from_only_one_list_are_included():
                got = rrf([["a"], ["b", "c", "d"]])
                assert got == ["a", "b", "c", "d"], f"got {got!r}"

            def test_empty_rankings():
                assert rrf([]) == []
                assert rrf([[], []]) == []
        ''',
        "solution": r'''
            def rrf(rankings, k=60):
                scores = {}
                for ranking in rankings:
                    for rank, cid in enumerate(ranking, start=1):
                        scores[cid] = scores.get(cid, 0) + 1 / (k + rank)
                return sorted(scores, key=lambda cid: (-scores[cid], cid))
        ''',
        "hints": [
            "Accumulate points in a dict, using `enumerate(..., start=1)` to get each rank.",
            "Loop over every ranked list and every (rank, id) in it, adding 1 / (k + rank) to that id's total. Then sort the ids by total descending, breaking ties by the id itself.",
            "1) scores = {}. 2) Nested loops with enumerate(ranking, start=1): scores[cid] = scores.get(cid, 0) + 1 / (k + rank). 3) Return sorted(scores, key=lambda cid: (-scores[cid], cid)).",
        ],
    },
    # ---------------------------------------------------------------- difficulty 3
    {
        "id": "retrieval-10",
        "title": "In-memory vector store",
        "difficulty": 3,
        "lesson": r'''
            Putting it together: a **vector store** keeps chunks with their vectors and
            metadata, and answers "which chunks are closest to this text?". Real ones (pgvector,
            Chroma, provider-hosted stores) add indexes to stay fast with millions of chunks,
            but the interface is the same as the class you'll write here.
        ''',
        "research": {
            "note": "Look at how a hosted vector store is used for retrieval (adding files, searching with a query, filtering by attributes, reading scores). Your class is a tiny version of the same idea.",
            "links": [
                {"title": "Retrieval - OpenAI API docs", "url": "https://platform.openai.com/docs/guides/retrieval"},
            ],
        },
        "prompt": r'''
            Build a small in-memory vector store with an injected embedding function.

            **Write:** a class `VectorStore`

            - `VectorStore(embed)`: `embed` is a function `embed(text) -> list of numbers` (one text at a time)
            - `.add(chunk_id, text, metadata=None)`: embeds `text` (calls `embed` once) and stores the chunk
            - `.search(query, k=3, where=None)`: embeds `query` once and returns a list of at most
              `k` result dicts `{"id": ..., "text": ..., "score": ..., "metadata": {...}}`,
              highest score first
            - `len(store)`: the number of stored chunks

            **Rules**
            - `metadata=None` is stored as `{}`.
            - Adding an id that already exists raises `ValueError`.
            - `score` is the cosine similarity between the query vector and the chunk vector;
              a zero vector scores `0.0`.
            - `where` works like before: every key must be in the chunk's metadata with an equal
              value; `None` or `{}` matches everything.
            - Ties keep the order the chunks were added.
            - An empty store returns `[]`. Scores are checked with a small tolerance.

            **Examples**
            ```python
            def fake_embed(text):
                words = text.lower().split()
                return [words.count("cat"), words.count("dog")]

            store = VectorStore(fake_embed)
            store.add("c1", "cat cat", {"lang": "en"})
            store.add("c2", "dog", {"lang": "en"})
            store.add("c3", "cat dog", {"lang": "fr"})
            len(store)                              # 3
            [r["id"] for r in store.search("cat")]  # ["c1", "c3", "c2"]
            store.search("cat", k=1)[0]["score"]    # 1.0
            [r["id"] for r in store.search("dog", where={"lang": "en"})]   # ["c2", "c1"]
            store.add("c1", "again")                # raises ValueError
            ```
        ''',
        "starter": r'''
            import math


            class VectorStore:
                def __init__(self, embed):
                    ...
        ''',
        "tests": r'''
            import math
            from solution import VectorStore

            def make_embed():
                calls = []
                def fake_embed(text):
                    calls.append(text)
                    words = text.lower().split()
                    return [words.count("cat"), words.count("dog")]
                return fake_embed, calls

            def make_store():
                embed, calls = make_embed()
                store = VectorStore(embed)
                store.add("c1", "cat cat", {"lang": "en"})
                store.add("c2", "dog", {"lang": "en"})
                store.add("c3", "cat dog", {"lang": "fr"})
                return store, calls

            def test_len_counts_chunks():
                store, calls = make_store()
                assert len(store) == 3, f"got {len(store)!r}"
                assert len(VectorStore(make_embed()[0])) == 0

            def test_search_ranks_by_cosine():
                store, calls = make_store()
                got = [r["id"] for r in store.search("cat")]
                assert got == ["c1", "c3", "c2"], f"got {got!r}"

            def test_result_dicts_have_id_text_score_metadata():
                store, calls = make_store()
                top = store.search("cat", k=1)
                assert len(top) == 1, f"got {top!r}"
                r = top[0]
                assert r["id"] == "c1" and r["text"] == "cat cat" and r["metadata"] == {"lang": "en"}, f"got {r!r}"
                assert math.isclose(r["score"], 1.0), f"got {r!r}"
                second = store.search("cat", k=2)[1]
                assert math.isclose(second["score"], 1 / math.sqrt(2)), f"got {second!r}"

            def test_where_filters_before_ranking():
                store, calls = make_store()
                got = [r["id"] for r in store.search("dog", where={"lang": "en"})]
                assert got == ["c2", "c1"], f"got {got!r}"
                assert store.search("dog", where={"team": "x"}) == []

            def test_duplicate_id_raises_value_error():
                store, calls = make_store()
                try:
                    store.add("c1", "again")
                except ValueError:
                    assert len(store) == 3
                    return
                assert False, "expected ValueError"

            def test_metadata_defaults_to_empty_dict_and_zero_vector_scores_zero():
                embed, calls = make_embed()
                store = VectorStore(embed)
                store.add("n", "nothing here")
                store.add("d", "dog")
                got = store.search("dog")
                assert [r["id"] for r in got] == ["d", "n"], f"got {got!r}"
                assert got[1]["metadata"] == {} and got[1]["score"] == 0, f"got {got!r}"

            def test_embed_called_once_per_add_and_once_per_search():
                store, calls = make_store()
                assert calls == ["cat cat", "dog", "cat dog"], f"embed calls: {calls!r}"
                store.search("cat dog", k=2)
                assert calls[3:] == ["cat dog"], f"embed calls: {calls!r}"

            def test_empty_store_returns_empty_list():
                store = VectorStore(make_embed()[0])
                assert store.search("cat") == []
        ''',
        "solution": r'''
            import math


            def cosine(a, b):
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


            class VectorStore:
                def __init__(self, embed):
                    self.embed = embed
                    self.chunks = []
                    self.ids = set()

                def __len__(self):
                    return len(self.chunks)

                def add(self, chunk_id, text, metadata=None):
                    if chunk_id in self.ids:
                        raise ValueError(f"duplicate id {chunk_id!r}")
                    self.chunks.append({
                        "id": chunk_id,
                        "text": text,
                        "metadata": metadata or {},
                        "vector": self.embed(text),
                    })
                    self.ids.add(chunk_id)

                def search(self, query, k=3, where=None):
                    where = where or {}
                    query_vec = self.embed(query)
                    results = []
                    for c in self.chunks:
                        md = c["metadata"]
                        if all(key in md and md[key] == value for key, value in where.items()):
                            results.append({
                                "id": c["id"],
                                "text": c["text"],
                                "score": cosine(query_vec, c["vector"]),
                                "metadata": md,
                            })
                    results.sort(key=lambda r: r["score"], reverse=True)
                    return results[:k]
        ''',
        "hints": [
            "Store each chunk as a dict (id, text, metadata, vector) in a list on `self`, and keep the ids in a set to spot duplicates. `__len__` makes `len(store)` work.",
            "In `add`: reject duplicates, embed the text once, append. In `search`: embed the query once, filter chunks with the `where` rule, build result dicts with the cosine score, sort by score descending, slice to k.",
            "1) __init__: save embed, self.chunks = [], self.ids = set(). 2) __len__ returns len(self.chunks). 3) add: raise ValueError if id in self.ids; append {id, text, metadata or {}, vector: embed(text)}. 4) search: where = where or {}; q = embed(query); loop, filter, append result dicts; sort by score reverse=True; return [:k].",
        ],
    },
]
