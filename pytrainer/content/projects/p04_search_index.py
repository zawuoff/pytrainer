PROJECT = {
    "id": "search-index",
    "title": "Keyword Search Engine (TF-IDF)",
    "order": 4,
    "level": "Intermediate",
    "estimated_hours": 2.5,
    "requires": ["classes", "dicts", "json", "files", "regex", "vectors"],
    "tags": ["rag", "retrieval", "search", "tf-idf"],
    "main": "search.py",
    "files": ["search.py"],
    "brief": r'''
        # Keyword Search Engine (TF-IDF)

        The "R" in RAG is *retrieval*: given a question, find the most relevant chunks.
        Before embeddings, search engines used **TF-IDF** vectors and cosine similarity,
        and keyword search is still used today next to vector search ("hybrid search")
        because it nails exact terms such as product codes, error messages and names.
        Building it yourself teaches exactly the vector math that embedding search uses.

        Build it in **`search.py`**, using only the standard library.

        ## Interface

        ### `tokenize(text: str) -> list[str]`
        Lowercase the text and return every maximal run of `a-z` / `0-9` characters,
        in order (anything else is a separator).
        `tokenize("GPT-4o costs $5/1M tokens!")` -> `["gpt", "4o", "costs", "5", "1m", "tokens"]`.

        ### `class SearchIndex`

        | member | behaviour |
        | --- | --- |
        | `SearchIndex()` | empty index |
        | `add(doc_id: str, text: str)` | add a document. Raise `ValueError` if `doc_id` is already present. |
        | `len(index)` | number of documents |
        | `search(query: str, k: int = 5) -> list[tuple[str, float]]` | best `k` matches as `(doc_id, score)` |
        | `save(path: str)` | write the index to a **JSON** file |
        | `SearchIndex.load(path: str)` | classmethod: rebuild an index from a saved file. Missing file -> `FileNotFoundError`. |

        ## Scoring (use exactly this)

        With `N` documents, for term `t` and document `d`:

        - `tf(t, d) = count of t in tokenize(d) / len(tokenize(d))` (0 for an empty document)
        - `df(t)` = number of documents containing `t`
        - `idf(t) = ln((1 + N) / (1 + df(t))) + 1` (natural log)
        - document vector: `w(t, d) = tf(t, d) * idf(t)` for every term in `d`
        - query vector: the same formula applied to the query text, using the index's
          `idf` values; query terms not present in any document are ignored
        - `score = cosine(query_vector, doc_vector)` =
          `dot / (norm(query) * norm(doc))`, `0.0` if either norm is 0

        `idf` depends on the whole collection, so it must be correct after any
        sequence of `add` calls (including adds after a search or after `load`).

        ## `search` rules

        - `k` must be a positive `int`, otherwise `ValueError`.
        - Only documents with `score > 0` are returned.
        - Order by score descending; ties broken by `doc_id` ascending.
        - Return at most `k` results; an empty or unknown-word query returns `[]`.

        ## Example

        ```python
        idx = SearchIndex()
        idx.add("a", "The cat sat on the mat")
        idx.add("b", "Dogs and cats are pets")
        idx.add("c", "The stock market fell")
        idx.search("cat on a mat", k=2)
        # [('a', 0.689...)]          # 'b' has 'cats', not 'cat'
        idx.search("the", k=5)
        # [('a', 0.605...), ('c', 0.402...)]
        ```

        ## Running it locally

        Index a folder of text files (your chunker from the previous project is
        perfect), save the index, then query it from an `if __name__ == "__main__":`
        block. Upload `search.py`.
    ''',
    "explore": r'''
        ## Things to research

        - **Embeddings**: dense vectors produced by a model (e.g. OpenAI
          `text-embedding-3-small`) where *meaning*, not spelling, determines
          similarity. Why does "cat" vs "cats" or "car" vs "automobile" break TF-IDF but
          not embeddings? What are embedding *dimensions*?
        - **Vector databases**: look up Chroma, pgvector, Qdrant and FAISS. What is
          *approximate nearest neighbour* (ANN) search and why is brute-force cosine
          fine for a few thousand chunks but not for millions?
        - **BM25**: the ranking function most keyword engines (Elasticsearch, Lucene)
          use instead of plain TF-IDF. What problem do its `k1` and `b` parameters fix?
        - **Hybrid search / reciprocal rank fusion**: combining keyword and vector results.

        ## Make it real (optional, ungraded)

        Add a second index that uses real embeddings and compare the rankings:

        ```bash
        pip install openai
        export OPENAI_API_KEY=sk-...
        ```

        ```python
        from openai import OpenAI
        client = OpenAI()

        def embed(texts):
            resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
            return [d.embedding for d in resp.data]
        ```

        Store `embed([text])[0]` per document, embed the query, rank by cosine.
    ''',
    "rubric": [
        "TF-IDF and cosine are implemented exactly as specified, with the math isolated in small helper functions",
        "idf is never stale: recomputed or updated correctly whenever documents are added",
        "Sparse vectors are represented sensibly (dicts of term -> weight), not dense lists over the whole vocabulary",
        "save/load uses json with explicit UTF-8 and round-trips without losing information",
        "Clear class API with validation (duplicate ids, bad k) and helpful error messages",
    ],
    "starter_files": {
        "search.py": r'''
            """Keyword search with TF-IDF and cosine similarity."""


            def tokenize(text):
                ...


            class SearchIndex:
                def __init__(self):
                    ...

                def add(self, doc_id, text):
                    ...

                def __len__(self):
                    return 0

                def search(self, query, k=5):
                    ...

                def save(self, path):
                    ...

                @classmethod
                def load(cls, path):
                    ...
        ''',
    },
    "solution_files": {
        "search.py": r'''
            """Keyword search with TF-IDF and cosine similarity."""

            from __future__ import annotations

            import json
            import math
            import re
            from collections import Counter
            from pathlib import Path

            _TOKEN = re.compile(r"[a-z0-9]+")
            Vector = dict[str, float]


            def tokenize(text: str) -> list[str]:
                return _TOKEN.findall(text.lower())


            def term_frequencies(tokens: list[str]) -> Vector:
                if not tokens:
                    return {}
                total = len(tokens)
                return {term: count / total for term, count in Counter(tokens).items()}


            def norm(vector: Vector) -> float:
                return math.sqrt(sum(w * w for w in vector.values()))


            def cosine(a: Vector, b: Vector) -> float:
                if len(a) > len(b):
                    a, b = b, a
                dot = sum(w * b.get(term, 0.0) for term, w in a.items())
                denominator = norm(a) * norm(b)
                return dot / denominator if denominator else 0.0


            class SearchIndex:
                """In-memory TF-IDF index over string documents."""

                def __init__(self) -> None:
                    self._docs: dict[str, str] = {}
                    self._tf: dict[str, Vector] = {}
                    self._df: Counter[str] = Counter()

                def __len__(self) -> int:
                    return len(self._docs)

                def add(self, doc_id: str, text: str) -> None:
                    if doc_id in self._docs:
                        raise ValueError(f"duplicate document id: {doc_id!r}")
                    tf = term_frequencies(tokenize(text))
                    self._docs[doc_id] = text
                    self._tf[doc_id] = tf
                    self._df.update(tf.keys())

                def idf(self, term: str) -> float:
                    return math.log((1 + len(self._docs)) / (1 + self._df[term])) + 1

                def _weigh(self, tf: Vector) -> Vector:
                    return {term: w * self.idf(term) for term, w in tf.items()}

                def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
                    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
                        raise ValueError("k must be a positive int")
                    query_tf = {t: w for t, w in term_frequencies(tokenize(query)).items()
                                if self._df[t]}
                    if not query_tf:
                        return []
                    query_vec = self._weigh(query_tf)
                    scored = []
                    for doc_id, tf in self._tf.items():
                        score = cosine(query_vec, self._weigh(tf))
                        if score > 0:
                            scored.append((doc_id, score))
                    scored.sort(key=lambda item: (-item[1], item[0]))
                    return scored[:k]

                def save(self, path: str) -> None:
                    data = {"version": 1, "documents": self._docs}
                    Path(path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

                @classmethod
                def load(cls, path: str) -> "SearchIndex":
                    data = json.loads(Path(path).read_text(encoding="utf-8"))
                    index = cls()
                    for doc_id, text in data["documents"].items():
                        index.add(doc_id, text)
                    return index


            if __name__ == "__main__":
                idx = SearchIndex()
                idx.add("a", "The cat sat on the mat")
                idx.add("b", "Dogs and cats are pets")
                idx.add("c", "The stock market fell")
                print(idx.search("cat on a mat"))
        ''',
    },
    "tests": r'''
        import json
        import math
        from search import SearchIndex, tokenize

        def build():
            idx = SearchIndex()
            idx.add("a", "The cat sat on the mat")
            idx.add("b", "Dogs and cats are pets")
            idx.add("c", "The stock market fell")
            return idx

        def reference_scores(docs, query):
            toks = {d: tokenize(t) for d, t in docs.items()}
            n = len(docs)
            df = {}
            for ts in toks.values():
                for t in set(ts):
                    df[t] = df.get(t, 0) + 1
            idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
            def vec(ts):
                return {t: ts.count(t) / len(ts) * idf[t] for t in set(ts) if t in idf}
            q = vec(tokenize(query))
            out = {}
            for d, ts in toks.items():
                v = vec(ts) if ts else {}
                dot = sum(w * v.get(t, 0) for t, w in q.items())
                nq = math.sqrt(sum(w * w for w in q.values()))
                nv = math.sqrt(sum(w * w for w in v.values()))
                out[d] = dot / (nq * nv) if nq and nv else 0.0
            return out

        def close(a, b):
            return abs(a - b) < 1e-9

        def test_tokenize_lowercases_and_splits():
            got = tokenize("GPT-4o costs $5/1M tokens!")
            assert got == ["gpt", "4o", "costs", "5", "1m", "tokens"], f"got {got!r}"
            assert tokenize("  ...  ") == []

        def test_len_and_duplicate_ids():
            idx = build()
            assert len(idx) == 3
            try:
                idx.add("a", "again")
            except ValueError:
                return
            raise AssertionError("adding an existing doc_id should raise ValueError")

        def test_scores_match_tfidf_formula():
            docs = {"a": "The cat sat on the mat", "b": "Dogs and cats are pets",
                    "c": "The stock market fell"}
            idx = build()
            for query in ("cat on a mat", "the", "the market"):
                want = reference_scores(docs, query)
                got = dict(idx.search(query, k=10))
                for doc_id, score in got.items():
                    assert close(score, want[doc_id]), f"query {query!r}: {doc_id} scored {score}, expected {want[doc_id]}"
                expected_ids = {d for d, s in want.items() if s > 0}
                assert set(got) == expected_ids, f"query {query!r}: returned {sorted(got)}"

        def test_ranking_order_and_top_k():
            idx = build()
            got = idx.search("the", k=5)
            assert [d for d, _ in got] == ["a", "c"], f"got {got!r}"
            assert len(idx.search("the", k=1)) == 1
            assert idx.search("the", k=1)[0][0] == "a"

        def test_ties_broken_by_doc_id():
            idx = SearchIndex()
            idx.add("z", "llm agents")
            idx.add("m", "llm agents")
            idx.add("q", "other things")
            got = [d for d, _ in idx.search("agents")]
            assert got == ["m", "z"], f"got {got!r}"

        def test_no_match_and_empty_query_return_empty_list():
            idx = build()
            assert idx.search("quantum") == []
            assert idx.search("") == []
            assert idx.search("!!!") == []
            assert SearchIndex().search("cat") == []

        def test_invalid_k_raises():
            idx = build()
            for bad in (0, -1, 2.5, "3"):
                try:
                    idx.search("cat", k=bad)
                except ValueError:
                    continue
                raise AssertionError(f"k={bad!r} should raise ValueError")

        def test_idf_updates_after_more_adds():
            idx = build()
            idx.search("the")
            idx.add("d", "The the the end")
            docs = {"a": "The cat sat on the mat", "b": "Dogs and cats are pets",
                    "c": "The stock market fell", "d": "The the the end"}
            want = reference_scores(docs, "the cat")
            got = dict(idx.search("the cat", k=10))
            for doc_id, score in got.items():
                assert close(score, want[doc_id]), f"stale idf? {doc_id} scored {score}, expected {want[doc_id]}"

        def test_empty_document_is_allowed():
            idx = build()
            idx.add("empty", "")
            assert len(idx) == 4
            assert "empty" not in [d for d, _ in idx.search("cat mat")]

        def test_save_writes_json_and_load_round_trips():
            idx = build()
            idx.add("u", "Café résumé naïve")
            idx.save("index.json")
            with open("index.json", encoding="utf-8") as fh:
                json.load(fh)
            loaded = SearchIndex.load("index.json")
            assert isinstance(loaded, SearchIndex)
            assert len(loaded) == 4
            for q in ("the", "cat on a mat", "café"):
                assert loaded.search(q) == idx.search(q), f"results differ after load for {q!r}"
            loaded.add("new", "mat mat mat")
            assert loaded.search("mat")[0][0] == "new"

        def test_load_missing_file_raises():
            try:
                SearchIndex.load("nope.json")
            except FileNotFoundError:
                return
            raise AssertionError("expected FileNotFoundError")
    ''',
}
