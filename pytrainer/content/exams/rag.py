EXAM = {
    "module": "rag",
    "title": "RAG, Embeddings & Search: module test",
    "intro": r'''
        This is a **test**, not a lesson. It covers the whole *RAG* module: vectors and
        cosine similarity, chunking, keyword and semantic retrieval, and grounded answers
        with citations.

        - There are **no hints and no tutor** during the test. Every rule the checks test is
          written in the prompt, so read each one slowly.
        - Embedding functions and models are **fakes** passed into your code: no network, no
          API key, standard library only.
        - One task links to real documentation. Another asks you to find a well-known formula
          yourself, with no links. Looking things up is part of the job.
        - Pass at least **70%** of the exercises and you can skip the module.
    ''',
    "pass_ratio": 0.7,
}

EXERCISES = [
    {
        "id": "exam-rag-1",
        "title": "Overlapping chunks with metadata",
        "difficulty": 2,
        "prompt": r'''
            Before you can retrieve anything, documents are cut into overlapping chunks, and
            each chunk remembers where it came from.

            **Write:** `chunk_document(source, text, max_words=50, overlap=10)`

            - `source`: the document name, e.g. `"faq.md"`
            - `text`: the document text
            - `max_words`: the most words in one chunk
            - `overlap`: how many words each chunk repeats from the end of the previous one
            - **Returns:** a list of dicts `{"id": str, "source": str, "start": int, "text": str}`

            **Rules**
            - Words are what `text.split()` returns. A chunk's `text` is its words joined with one space.
            - Chunk `i` (counting from 0) starts at word `i * (max_words - overlap)`; `start` is that word index.
            - `id` is `"<source>#<i>"`, e.g. `"faq.md#0"`.
            - Stop after the first chunk that reaches the last word (no chunk that only repeats
              words already covered).
            - Text with no words returns `[]`.
            - If `max_words < 1`, or `overlap < 0`, or `overlap >= max_words`, raise
              `ValueError("invalid chunk settings")`.

            **Examples**
            ```python
            chunk_document("a.txt", "one two three four five six seven", max_words=3, overlap=1)
            # [{"id": "a.txt#0", "source": "a.txt", "start": 0, "text": "one two three"},
            #  {"id": "a.txt#1", "source": "a.txt", "start": 2, "text": "three four five"},
            #  {"id": "a.txt#2", "source": "a.txt", "start": 4, "text": "five six seven"}]

            chunk_document("a.txt", "one two", max_words=3, overlap=1)
            # [{"id": "a.txt#0", "source": "a.txt", "start": 0, "text": "one two"}]

            chunk_document("a.txt", "   ")       # []
            chunk_document("a.txt", "x", 3, 3)   # raises ValueError("invalid chunk settings")
            ```
        ''',
        "starter": r'''
            def chunk_document(source, text, max_words=50, overlap=10):
                ...
        ''',
        "tests": r'''
            from solution import chunk_document

            def texts(chunks):
                return [c["text"] for c in chunks]

            def test_example_with_overlap():
                got = chunk_document("a.txt", "one two three four five six seven", max_words=3, overlap=1)
                assert got == [
                    {"id": "a.txt#0", "source": "a.txt", "start": 0, "text": "one two three"},
                    {"id": "a.txt#1", "source": "a.txt", "start": 2, "text": "three four five"},
                    {"id": "a.txt#2", "source": "a.txt", "start": 4, "text": "five six seven"},
                ], f"got {got!r}"

            def test_last_chunk_can_be_short_and_no_duplicate_tail():
                got = chunk_document("d", "a b c d e f g h", max_words=4, overlap=2)
                assert texts(got) == ["a b c d", "c d e f", "e f g h"], f"got {texts(got)!r}"
                got = chunk_document("d", "a b c d e", max_words=4, overlap=0)
                assert texts(got) == ["a b c d", "e"], f"got {texts(got)!r}"
                assert [c["start"] for c in got] == [0, 4], f"got {got!r}"

            def test_short_text_is_one_chunk_and_whitespace_is_normalised():
                got = chunk_document("n.md", "  hello \n\n world\t ", max_words=5, overlap=2)
                assert got == [{"id": "n.md#0", "source": "n.md", "start": 0, "text": "hello world"}], f"got {got!r}"

            def test_empty_text_returns_empty_list():
                assert chunk_document("x", "") == []
                assert chunk_document("x", " \n ") == []

            def test_invalid_settings_raise():
                for mw, ov in [(3, 3), (3, 5), (0, 0), (4, -1)]:
                    try:
                        chunk_document("x", "a b c", max_words=mw, overlap=ov)
                    except ValueError as e:
                        assert str(e) == "invalid chunk settings", f"message was {str(e)!r}"
                    else:
                        assert False, f"expected ValueError for max_words={mw}, overlap={ov}"
        ''',
        "solution": r'''
            def chunk_document(source, text, max_words=50, overlap=10):
                if max_words < 1 or overlap < 0 or overlap >= max_words:
                    raise ValueError("invalid chunk settings")
                words = text.split()
                step = max_words - overlap
                chunks = []
                i = 0
                while True:
                    start = i * step
                    if start >= len(words):
                        break
                    part = words[start:start + max_words]
                    chunks.append({"id": f"{source}#{i}", "source": source, "start": start,
                                   "text": " ".join(part)})
                    if start + max_words >= len(words):
                        break
                    i += 1
                return chunks
        ''',
        "hints": [
            "Split into words once, then slide a window of `max_words` forward by `max_words - overlap` each time.",
            "Validate the settings first. Loop over chunk numbers; slice the words for each; stop as soon as a slice reaches the end of the list.",
            "step = max_words - overlap. For i = 0, 1, 2...: start = i * step; if start >= len(words) stop; take words[start:start+max_words]; append the dict; if start + max_words >= len(words) stop.",
        ],
    },
    {
        "id": "exam-rag-2",
        "title": "A tiny vector store",
        "difficulty": 2,
        "prompt": r'''
            Build the smallest useful vector store: it embeds texts when you add them and finds
            the most similar ones for a query, optionally filtered by metadata.

            **Write:** a class `VectorStore`

            - `VectorStore(embed)`: `embed(text) -> list[float]` is an embedding function (a fake in the tests)
            - `add(doc_id, text, **metadata)`: embed `text` once and store it with its metadata.
              Adding an id that already exists raises `ValueError("duplicate id: <doc_id>")`.
            - `search(query, k=3, **filters)` -> list of dicts `{"id": str, "score": float, "text": str}`
            - `len(store)` returns how many documents are stored.

            **Rules**
            - `score` is the cosine similarity between the query's vector and the document's
              vector, rounded with `round(value, 4)`. If either vector has length 0 (all zeros),
              the score is `0.0`.
            - Results are sorted by score, highest first; equal scores are ordered by id (A to Z).
              Sort on the **rounded** score.
            - Return at most `k` results.
            - `filters`: only documents whose metadata has **every** given key with an equal
              value are considered. E.g. `search("q", lang="en")`.
            - `embed` is called once per `add` and once per `search`, never more.

            **Examples**
            ```python
            vecs = {"cats": [1, 0], "dogs": [0, 1], "pets": [1, 1]}
            store = VectorStore(lambda t: vecs[t])
            store.add("d1", "cats", lang="en")
            store.add("d2", "dogs", lang="fr")
            len(store)                        # 2
            store.search("pets", k=1)
            # [{"id": "d1", "score": 0.7071, "text": "cats"}]      (d1 and d2 tie; d1 comes first)
            store.search("cats", lang="fr")
            # [{"id": "d2", "score": 0.0, "text": "dogs"}]
            ```
        ''',
        "starter": r'''
            import math


            class VectorStore:
                def __init__(self, embed):
                    ...
        ''',
        "tests": r'''
            from solution import VectorStore

            VECS = {"cats": [1, 0, 0], "dogs": [0, 1, 0], "pets": [1, 1, 0], "fish": [0, 0, 2],
                    "kitten": [3, 1, 0], "zero": [0, 0, 0]}

            def make():
                calls = []
                def embed(text):
                    calls.append(text)
                    return VECS[text]
                return VectorStore(embed), calls

            def test_add_and_len():
                s, _ = make()
                assert len(s) == 0
                s.add("d1", "cats")
                s.add("d2", "dogs", lang="en")
                assert len(s) == 2, f"len was {len(s)}"

            def test_search_scores_and_order():
                s, _ = make()
                s.add("b", "dogs")
                s.add("a", "cats")
                s.add("c", "kitten")
                s.add("d", "fish")
                got = s.search("pets", k=10)
                assert got == [
                    {"id": "c", "score": 0.8944, "text": "kitten"},
                    {"id": "a", "score": 0.7071, "text": "cats"},
                    {"id": "b", "score": 0.7071, "text": "dogs"},
                    {"id": "d", "score": 0.0, "text": "fish"},
                ], f"got {got!r}"

            def test_k_limits_results():
                s, _ = make()
                for i, t in enumerate(["cats", "dogs", "fish", "kitten"]):
                    s.add(f"d{i}", t)
                got = s.search("cats", k=2)
                assert [r["id"] for r in got] == ["d0", "d3"], f"got {got!r}"

            def test_metadata_filters():
                s, _ = make()
                s.add("en1", "cats", lang="en", year=2024)
                s.add("fr1", "kitten", lang="fr", year=2024)
                s.add("en2", "dogs", lang="en", year=2023)
                got = [r["id"] for r in s.search("cats", k=5, lang="en")]
                assert got == ["en1", "en2"], f"got {got!r}"
                got = [r["id"] for r in s.search("cats", k=5, lang="en", year=2023)]
                assert got == ["en2"], f"got {got!r}"
                assert s.search("cats", lang="de") == []

            def test_zero_vector_scores_zero():
                s, _ = make()
                s.add("z", "zero")
                got = s.search("cats")
                assert got == [{"id": "z", "score": 0.0, "text": "zero"}], f"got {got!r}"

            def test_duplicate_id_and_embed_call_count():
                s, calls = make()
                s.add("d1", "cats")
                try:
                    s.add("d1", "dogs")
                except ValueError as e:
                    assert str(e) == "duplicate id: d1", f"message was {str(e)!r}"
                else:
                    assert False, "expected ValueError"
                s.add("d2", "dogs")
                calls.clear()
                s.search("pets", k=2)
                assert calls == ["pets"], f"embed was called with {calls!r} during one search"
        ''',
        "solution": r'''
            import math


            def _cosine(a, b):
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(x * x for x in b))
                if na == 0 or nb == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (na * nb)


            class VectorStore:
                def __init__(self, embed):
                    self.embed = embed
                    self.docs = {}

                def __len__(self):
                    return len(self.docs)

                def add(self, doc_id, text, **metadata):
                    if doc_id in self.docs:
                        raise ValueError(f"duplicate id: {doc_id}")
                    self.docs[doc_id] = {"text": text, "vector": self.embed(text), "metadata": metadata}

                def search(self, query, k=3, **filters):
                    q = self.embed(query)
                    results = []
                    for doc_id, doc in self.docs.items():
                        if any(doc["metadata"].get(key) != value or key not in doc["metadata"]
                               for key, value in filters.items()):
                            continue
                        score = round(_cosine(q, doc["vector"]), 4)
                        results.append({"id": doc_id, "score": score, "text": doc["text"]})
                    results.sort(key=lambda r: (-r["score"], r["id"]))
                    return results[:k]
        ''',
        "hints": [
            "Store each document in a dict keyed by id, with its text, vector and metadata. Write a small cosine helper.",
            "In `search`, embed the query once, skip documents that fail a filter, score the rest, sort, slice to k.",
            "Cosine = dot product / (length of a * length of b), with `math.sqrt` for the lengths and a guard for 0. Sort with `key=lambda r: (-r['score'], r['id'])`. `__len__` returns `len(self.docs)`.",
        ],
    },
    {
        "id": "exam-rag-3",
        "title": "Keyword ranking the search-engine way",
        "difficulty": 3,
        "research": {
            "note": "Keyword search engines (Lucene, Elasticsearch, OpenSearch) don't use plain "
                    "TF-IDF by default. They use a classic probabilistic ranking function that adds "
                    "two ideas: term-frequency saturation (a word repeated 50 times is not 50x more "
                    "relevant) and document-length normalisation, tuned by two parameters usually "
                    "written k1 and b. Find that function and its per-term formula yourself.",
            "links": [],
        },
        "prompt": r'''
            Semantic search misses exact names and codes (`ERR_42`, `gpt-4o`), so good RAG systems
            also run a keyword ranker. Implement the standard one used by search engines.

            **Write:** `keyword_scores(query, docs, k1=1.5, b=0.75)`

            - `query`: the search text
            - `docs`: list of document strings
            - `k1`, `b`: the two tuning parameters of the ranking function
            - **Returns:** a list of floats, one score per document in the same order, each rounded with `round(value, 4)`

            **Rules**
            - Tokenise both query and documents with `re.findall(r"[a-z0-9]+", text.lower())`.
            - `N` = number of documents; `avgdl` = average document length in tokens;
              `n(t)` = number of documents containing term `t` at least once.
            - Use this IDF (a common smoothed variant, it is never negative):
              `idf(t) = math.log((N - n(t) + 0.5) / (n(t) + 0.5) + 1)`
            - A document's score is the sum over the **distinct** query terms of
              `idf(t)` times the standard per-term weight of the ranking function, which uses
              the term's count in the document, `k1`, `b`, the document length and `avgdl`.
              (Finding that per-term weight is the research part.)
            - A query term that appears in no document adds `0`.
            - `docs == []` returns `[]`. If every document is empty (`avgdl` is 0), every score is `0.0`.

            **Examples**
            ```python
            keyword_scores("error", ["error error code", "all good", "error"])
            # [0.5785, 0.0, 0.6065]      (the short doc with one match beats the longer one with two)

            keyword_scores("reset password", ["how to reset your password", "reset the router"])
            # [0.7869, 0.2054]

            keyword_scores("x", [])      # []
            ```
        ''',
        "starter": r'''
            import math
            import re


            def keyword_scores(query, docs, k1=1.5, b=0.75):
                ...
        ''',
        "tests": r'''
            from solution import keyword_scores

            def test_short_matching_doc_ranks_higher():
                got = keyword_scores("error", ["error error code", "all good", "error"])
                assert got == [0.5785, 0.0, 0.6065], f"got {got!r}"

            def test_two_term_query():
                got = keyword_scores("reset password", ["how to reset your password", "reset the router"])
                assert got == [0.7869, 0.2054], f"got {got!r}"

            def test_tokenising_is_case_insensitive_and_query_terms_are_distinct():
                a = keyword_scores("Reset RESET reset!", ["Reset the ROUTER.", "nothing here", "reset reset"])
                b = keyword_scores("reset", ["reset the router", "nothing here", "reset reset"])
                assert a == b, f"{a!r} != {b!r}"

            def test_repeated_terms_saturate():
                got = keyword_scores("cat", ["cat dog", "cat cat cat cat cat cat cat cat cat cat", "dog"])
                assert got == [0.6203, 0.9059, 0.0], f"got {got!r}"

            def test_parameters_change_the_scores():
                docs = ["alpha beta beta", "beta", "gamma gamma gamma gamma"]
                got = keyword_scores("beta", docs, k1=1.2, b=0.0)
                assert got == [0.6463, 0.47, 0.0], f"with k1=1.2, b=0.0 got {got!r}"
                got = keyword_scores("beta", docs, k1=2.0, b=1.0)
                assert got == [0.6635, 0.8057, 0.0], f"with k1=2.0, b=1.0 got {got!r}"

            def test_empty_inputs():
                assert keyword_scores("x", []) == []
                assert keyword_scores("x", ["", ""]) == [0.0, 0.0]
                assert keyword_scores("", ["a b"]) == [0.0]
        ''',
        "solution": r'''
            import math
            import re


            def _tokens(text):
                return re.findall(r"[a-z0-9]+", text.lower())


            def keyword_scores(query, docs, k1=1.5, b=0.75):
                if not docs:
                    return []
                toks = [_tokens(d) for d in docs]
                n_docs = len(docs)
                avgdl = sum(len(t) for t in toks) / n_docs
                if avgdl == 0:
                    return [0.0] * n_docs
                terms = set(_tokens(query))
                df = {t: sum(1 for d in toks if t in d) for t in terms}
                scores = []
                for d in toks:
                    score = 0.0
                    for t in terms:
                        tf = d.count(t)
                        if tf == 0:
                            continue
                        idf = math.log((n_docs - df[t] + 0.5) / (df[t] + 0.5) + 1)
                        score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(d) / avgdl))
                    scores.append(round(score, 4))
                return scores
        ''',
        "hints": [
            "The function you are looking for is called Okapi BM25. Its Wikipedia page and the Elasticsearch docs both show the per-term formula.",
            "Tokenise all docs once, compute N, avgdl and n(t) for each distinct query term, then score each doc by summing idf times the saturating tf weight.",
            "Per-term weight: tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avgdl)). Use `set()` for distinct query terms, `list.count` for tf, skip terms with tf 0, round each doc's total to 4 places.",
        ],
    },
    {
        "id": "exam-rag-4",
        "title": "A grounded prompt within budget",
        "difficulty": 2,
        "research": {
            "note": "Read how the providers recommend grounding answers in documents: put the "
                    "sources before the question, number or tag them, ask for citations, and give "
                    "the model explicit permission to say it doesn't know.",
            "links": [
                {"title": "Anthropic docs: reduce hallucinations",
                 "url": "https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations"},
                {"title": "Anthropic docs: citations", "url": "https://docs.anthropic.com/en/docs/build-with-claude/citations"},
                {"title": "Anthropic: contextual retrieval", "url": "https://www.anthropic.com/news/contextual-retrieval"},
            ],
        },
        "prompt": r'''
            Build the prompt for the answer step of a RAG pipeline: numbered sources, a clear
            instruction to cite them, and a hard budget on how much context you send.

            **Write:** `grounded_prompt(question, chunks, max_context_chars=1500)`

            - `question`: the user's question
            - `chunks`: retrieved chunks, best first, each `{"source": str, "text": str}`
            - `max_context_chars`: the most characters the sources section may use
            - **Returns:** a tuple `(prompt, used)` where `used` is the list of `source` names
              actually included, in order

            **Rules**
            - Source number `n` (starting at 1) is written as the block `"[n] (<source>) <text>"`.
            - Blocks are joined with `"\n\n"`. The **joined** sources text must be at most
              `max_context_chars` characters long.
            - Add chunks in the given order. Stop at the first chunk that would push the
              sources text over the budget (don't skip ahead to smaller chunks; numbering has no gaps).
            - The prompt is exactly:
              `"Answer using only the sources below. Cite sources like [1]. If the sources do not contain the answer, reply exactly: I don't know.\n\nSources:\n" + sources_text + "\n\nQuestion: " + question`
            - If there are no chunks, or not even the first one fits, raise `ValueError("no context fits the budget")`.

            **Examples**
            ```python
            chunks = [{"source": "faq.md", "text": "Refunds take 5 days."},
                      {"source": "terms.md", "text": "Refunds need a receipt."}]
            prompt, used = grounded_prompt("How long do refunds take?", chunks)
            used      # ["faq.md", "terms.md"]
            prompt.endswith("Sources:\n[1] (faq.md) Refunds take 5 days.\n\n[2] (terms.md) Refunds need a receipt.\n\nQuestion: How long do refunds take?")   # True

            grounded_prompt("q", chunks, max_context_chars=40)[1]   # ["faq.md"]   (the first block is 33 chars)
            grounded_prompt("q", [])                                # raises ValueError("no context fits the budget")
            ```
        ''',
        "starter": r'''
            def grounded_prompt(question, chunks, max_context_chars=1500):
                ...
        ''',
        "tests": r'''
            from solution import grounded_prompt

            HEAD = ("Answer using only the sources below. Cite sources like [1]. If the sources do not "
                    "contain the answer, reply exactly: I don't know.\n\nSources:\n")
            CHUNKS = [{"source": "faq.md", "text": "Refunds take 5 days."},
                      {"source": "terms.md", "text": "Refunds need a receipt."},
                      {"source": "blog.md", "text": "We love refunds."}]

            def test_full_prompt_text():
                prompt, used = grounded_prompt("How long?", CHUNKS[:2])
                assert prompt == (HEAD + "[1] (faq.md) Refunds take 5 days.\n\n[2] (terms.md) Refunds need a receipt."
                                  "\n\nQuestion: How long?"), f"got {prompt!r}"
                assert used == ["faq.md", "terms.md"], f"got {used!r}"

            def test_budget_counts_the_separators():
                # block 1 = 33 chars, block 2 = 38 chars: together 33 + 2 + 38 = 73
                _, used = grounded_prompt("q", CHUNKS, max_context_chars=73)
                assert used == ["faq.md", "terms.md"], f"got {used!r}"
                _, used = grounded_prompt("q", CHUNKS, max_context_chars=72)
                assert used == ["faq.md"], f"got {used!r}"

            def test_stops_at_first_chunk_that_does_not_fit():
                chunks = [{"source": "a", "text": "short"}, {"source": "b", "text": "x" * 100},
                          {"source": "c", "text": "tiny"}]
                prompt, used = grounded_prompt("q", chunks, max_context_chars=60)
                assert used == ["a"], f"got {used!r}"
                assert "[2]" not in prompt and "tiny" not in prompt

            def test_nothing_fits_raises():
                for chunks, budget in [([], 1500), (CHUNKS, 10)]:
                    try:
                        grounded_prompt("q", chunks, max_context_chars=budget)
                    except ValueError as e:
                        assert str(e) == "no context fits the budget", f"message was {str(e)!r}"
                    else:
                        assert False, "expected ValueError"
        ''',
        "solution": r'''
            HEAD = ("Answer using only the sources below. Cite sources like [1]. If the sources do not "
                    "contain the answer, reply exactly: I don't know.\n\nSources:\n")


            def grounded_prompt(question, chunks, max_context_chars=1500):
                blocks, used = [], []
                for n, chunk in enumerate(chunks, start=1):
                    block = f"[{n}] ({chunk['source']}) {chunk['text']}"
                    if len("\n\n".join(blocks + [block])) > max_context_chars:
                        break
                    blocks.append(block)
                    used.append(chunk["source"])
                if not blocks:
                    raise ValueError("no context fits the budget")
                return HEAD + "\n\n".join(blocks) + "\n\nQuestion: " + question, used
        ''',
        "hints": [
            "`enumerate(chunks, start=1)` gives you the source numbers.",
            "Build blocks one at a time; before keeping a block, check how long the joined text would be with it. Stop the loop the first time it's too long.",
            "For each chunk: make the block string; if `len('\\n\\n'.join(blocks + [block])) > max_context_chars`: break; else append the block and the source. If no blocks: raise. Return the head + joined blocks + question, and the used list.",
        ],
    },
    {
        "id": "exam-rag-5",
        "title": "Check the citations",
        "difficulty": 2,
        "prompt": r'''
            Models sometimes cite sources that don't exist (`[7]` when you sent 3) or cite nothing.
            Before showing an answer, check its citations.

            **Write:** `check_citations(answer, n_sources)`

            - `answer`: the model's reply text
            - `n_sources`: how many numbered sources were in the prompt (they are numbered `1..n_sources`)
            - **Returns:** `{"cited": list[int], "invalid": list[int], "grounded": bool}`

            **Rules**
            - A citation is a number in square brackets. One bracket may hold several numbers
              separated by commas and optional spaces: `[1]`, `[2,3]`, `[1, 4]` are all citations.
              Brackets that contain anything else (like `[a]` or `[1-3]`) are not citations.
            - `cited`: the valid numbers (between 1 and `n_sources`), each once, sorted ascending.
            - `invalid`: the out-of-range numbers (including `0`), each once, sorted ascending.
            - `grounded` is `True` only when there is at least one valid citation **and** no invalid one.
            - The exact reply `"I don't know"` (after stripping whitespace) is special: return
              `{"cited": [], "invalid": [], "grounded": True}`, an honest refusal is fine.

            **Examples**
            ```python
            check_citations("Refunds take 5 days [1]. You need a receipt [2, 1].", 3)
            # {"cited": [1, 2], "invalid": [], "grounded": True}

            check_citations("It is free [4][0].", 3)
            # {"cited": [], "invalid": [0, 4], "grounded": False}

            check_citations("No sources here [a].", 3)
            # {"cited": [], "invalid": [], "grounded": False}
            ```
        ''',
        "starter": r'''
            import re


            def check_citations(answer, n_sources):
                ...
        ''',
        "tests": r'''
            from solution import check_citations

            def test_valid_citations_deduplicated_and_sorted():
                got = check_citations("Refunds take 5 days [1]. You need a receipt [2, 1]. Also [3,2].", 3)
                assert got == {"cited": [1, 2, 3], "invalid": [], "grounded": True}, f"got {got!r}"

            def test_out_of_range_citations_are_invalid():
                got = check_citations("It is free [4][0].", 3)
                assert got == {"cited": [], "invalid": [0, 4], "grounded": False}, f"got {got!r}"
                got = check_citations("Mostly true [1] but also [12].", 3)
                assert got == {"cited": [1], "invalid": [12], "grounded": False}, f"got {got!r}"

            def test_brackets_that_are_not_citations_are_ignored():
                got = check_citations("See [a], [1-3] and [ ] and list[0 ,x].", 5)
                assert got == {"cited": [], "invalid": [], "grounded": False}, f"got {got!r}"

            def test_no_citations_is_not_grounded():
                got = check_citations("Refunds take 5 days.", 2)
                assert got == {"cited": [], "invalid": [], "grounded": False}, f"got {got!r}"

            def test_i_dont_know_is_accepted():
                got = check_citations("  I don't know\n", 3)
                assert got == {"cited": [], "invalid": [], "grounded": True}, f"got {got!r}"
        ''',
        "solution": r'''
            import re


            def check_citations(answer, n_sources):
                if answer.strip() == "I don't know":
                    return {"cited": [], "invalid": [], "grounded": True}
                numbers = set()
                for inside in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", answer):
                    numbers.update(int(x) for x in inside.split(","))
                cited = sorted(n for n in numbers if 1 <= n <= n_sources)
                invalid = sorted(n for n in numbers if not 1 <= n <= n_sources)
                return {"cited": cited, "invalid": invalid, "grounded": bool(cited) and not invalid}
        ''',
        "hints": [
            "A regular expression can find the bracket groups: digits, then optionally more `, digits` parts, between `\\[` and `\\]`.",
            "Collect every number from every matching bracket into a set, then split the set into valid and invalid by range.",
            "Handle the \"I don't know\" case first. Use `re.findall(r'\\[(\\d+(?:\\s*,\\s*\\d+)*)\\]', answer)`, split each match on ',', convert with `int()` (it ignores spaces), and sort the two groups.",
        ],
    },
    {
        "id": "exam-rag-6",
        "title": "End to end: answer or admit it",
        "difficulty": 3,
        "prompt": r'''
            Put the pipeline together: retrieve, refuse when retrieval is weak, ask the model,
            and keep only the sources the answer actually cites.

            **Write:** `rag_answer(question, chunks, embed, llm, k=2, threshold=0.5)`

            - `question`: the user's question
            - `chunks`: list of `{"source": str, "text": str}`
            - `embed`: fake embedding function, `embed(text) -> list[float]`
            - `llm`: fake model, `llm(prompt) -> str`
            - **Returns:** `{"answer": str, "sources": list[str]}`

            **Rules**
            - Score each chunk by cosine similarity between `embed(question)` and `embed(chunk["text"])`
              (zero-length vectors score `0.0`). Embed the question once.
            - Keep chunks with score `>= threshold`, best first (ties keep the original order),
              at most `k` of them.
            - If none are kept, return `{"answer": "I don't know", "sources": []}` **without calling `llm`**.
            - Otherwise call `llm` once with this prompt, numbering kept chunks from 1:
              `"Use only these sources and cite them like [1].\n" + lines + "\nQuestion: " + question`
              where `lines` is one line per chunk: `"[n] <text>\n"`.
            - Citations in the reply are `[n]` with a single number. `sources` = the `source` of
              each cited chunk, ordered by number, each once. Numbers outside `1..len(kept)` are ignored.
            - If the reply is exactly `"I don't know"` (after stripping) or cites no valid source, return
              `{"answer": "I don't know", "sources": []}`. Otherwise `answer` is the reply stripped of
              surrounding whitespace.

            **Examples**
            ```python
            # embed puts the question close to the faq chunk only
            rag_answer("How long do refunds take?", chunks, embed, llm)
            # llm got: "Use only these sources and cite them like [1].\n[1] Refunds take 5 days.\nQuestion: How long do refunds take?"
            # llm replied "5 days [1]."   ->  returns {"answer": "5 days [1].", "sources": ["faq.md"]}

            # nothing scores >= threshold  ->  {"answer": "I don't know", "sources": []}, llm never called
            ```
        ''',
        "starter": r'''
            import math
            import re


            def rag_answer(question, chunks, embed, llm, k=2, threshold=0.5):
                ...
        ''',
        "tests": r'''
            from solution import rag_answer

            VECS = {"How long do refunds take?": [1, 0, 0], "Refunds take 5 days.": [0.9, 0.1, 0],
                    "Refunds need a receipt.": [0.6, 0.8, 0], "Our office is in Paris.": [0, 0, 1],
                    "Weather?": [0, 0.1, 1], "Blank": [0, 0, 0]}
            CHUNKS = [{"source": "office.md", "text": "Our office is in Paris."},
                      {"source": "terms.md", "text": "Refunds need a receipt."},
                      {"source": "faq.md", "text": "Refunds take 5 days."}]

            def setup(reply):
                embeds, prompts = [], []
                def embed(t):
                    embeds.append(t)
                    return VECS[t]
                def llm(p):
                    prompts.append(p)
                    return reply
                return embed, llm, embeds, prompts

            def test_prompt_and_cited_sources():
                embed, llm, embeds, prompts = setup("5 days [1]. Receipt needed [2]. ")
                got = rag_answer("How long do refunds take?", CHUNKS, embed, llm)
                assert prompts == ["Use only these sources and cite them like [1].\n[1] Refunds take 5 days.\n"
                                   "[2] Refunds need a receipt.\nQuestion: How long do refunds take?"], f"prompt was {prompts!r}"
                assert got == {"answer": "5 days [1]. Receipt needed [2].", "sources": ["faq.md", "terms.md"]}, f"got {got!r}"
                assert embeds.count("How long do refunds take?") == 1, "embed the question only once"

            def test_threshold_and_k_limit_the_context():
                embed, llm, _, prompts = setup("[1]")
                rag_answer("How long do refunds take?", CHUNKS, embed, llm, k=5, threshold=0.7)
                assert "Receipt" not in prompts[0] and "[1] Refunds take 5 days." in prompts[0], f"prompt was {prompts[0]!r}"
                embed, llm, _, prompts = setup("[1]")
                rag_answer("How long do refunds take?", CHUNKS, embed, llm, k=1, threshold=0.0)
                assert "[2]" not in prompts[0], f"prompt was {prompts[0]!r}"

            def test_weak_retrieval_refuses_without_calling_llm():
                embed, llm, _, prompts = setup("should not be used")
                got = rag_answer("How long do refunds take?", CHUNKS[:1], embed, llm)
                assert got == {"answer": "I don't know", "sources": []}, f"got {got!r}"
                assert prompts == [], "llm must not be called when nothing passes the threshold"

            def test_uncited_or_invalid_citations_become_i_dont_know():
                for reply in ("5 days.", "5 days [7].", "  I don't know  "):
                    embed, llm, _, _ = setup(reply)
                    got = rag_answer("How long do refunds take?", CHUNKS, embed, llm)
                    assert got == {"answer": "I don't know", "sources": []}, f"reply {reply!r} gave {got!r}"

            def test_sources_ordered_by_number_and_deduplicated():
                embed, llm, _, _ = setup("A [2], B [1], again [2] and [9].")
                got = rag_answer("How long do refunds take?", CHUNKS, embed, llm)
                assert got["sources"] == ["faq.md", "terms.md"], f"got {got!r}"

            def test_zero_vectors_score_zero_and_ties_keep_order():
                chunks = [{"source": "blank", "text": "Blank"}] + CHUNKS
                embed, llm, _, prompts = setup("[1]")
                got = rag_answer("How long do refunds take?", chunks, embed, llm, k=4, threshold=0.0)
                lines = prompts[0].split("\n")[1:5]
                assert lines == ["[1] Refunds take 5 days.", "[2] Refunds need a receipt.", "[3] Blank",
                                 "[4] Our office is in Paris."], f"prompt was {prompts[0]!r}"
                assert got["sources"] == ["faq.md"], f"got {got!r}"
        ''',
        "solution": r'''
            import math
            import re


            def _cosine(a, b):
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(x * x for x in b))
                if na == 0 or nb == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (na * nb)


            def rag_answer(question, chunks, embed, llm, k=2, threshold=0.5):
                refuse = {"answer": "I don't know", "sources": []}
                q = embed(question)
                scored = [(_cosine(q, embed(c["text"])), c) for c in chunks]
                kept = [c for s, c in sorted(scored, key=lambda p: -p[0]) if s >= threshold][:k]
                if not kept:
                    return refuse
                lines = "".join(f"[{n}] {c['text']}\n" for n, c in enumerate(kept, start=1))
                reply = llm("Use only these sources and cite them like [1].\n" + lines + "Question: " + question)
                if reply.strip() == "I don't know":
                    return refuse
                nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", reply) if 1 <= int(n) <= len(kept)})
                if not nums:
                    return refuse
                return {"answer": reply.strip(), "sources": [kept[n - 1]["source"] for n in nums]}
        ''',
        "hints": [
            "Reuse ideas from the chapter: a cosine helper, a stable sort by score, `enumerate(..., start=1)` for numbering, and a regex for `[n]`.",
            "Score and filter first; return the refusal early if nothing is kept. Then build the prompt, call the model once, and map valid citation numbers back to chunks.",
            "Pairs (score, chunk) sorted with `key=lambda p: -p[0]` keep ties in order. Keep those with score >= threshold, slice [:k]. Lines: f'[{n}] {text}\\n'. Citations: `re.findall(r'\\[(\\d+)\\]', reply)` -> ints in range -> sorted set -> `kept[n-1]['source']`.",
        ],
    },
]
