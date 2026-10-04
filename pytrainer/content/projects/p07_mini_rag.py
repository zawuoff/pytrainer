PROJECT = {
    "id": "mini-rag",
    "title": "Mini RAG Pipeline",
    "order": 7,
    "level": "Intermediate",
    "estimated_hours": 2.5,
    "requires": ["classes", "vectors", "fstrings", "sorting"],
    "tags": ["rag", "embeddings", "prompting"],
    "main": "rag.py",
    "files": ["rag.py"],
    "brief": r'''
# Mini RAG pipeline

Retrieval-Augmented Generation (RAG) is the most common pattern in production LLM apps:
instead of hoping the model "knows" your company handbook, you **retrieve** the most relevant
passages and put them in the prompt, then ask the model to answer **only** from those
passages and cite them. Every RAG system - from a weekend demo to an enterprise search
product - has the same skeleton: embed, store, retrieve by similarity, build a grounded
prompt, generate, and refuse when nothing relevant was found.

You will build that skeleton in pure Python. The embedding model and the LLM are
**injected** as plain callables, so your code works with any provider (and with the fakes
the tests use).

## What to build

A file `rag.py` containing a module constant and a class.

```python
NO_ANSWER = "I don't know based on the provided documents."

class RAG:
    def __init__(self, embed, llm, threshold=0.2): ...
    def add_documents(self, docs): ...
    def retrieve(self, query, k=3): ...
    def answer(self, query, k=3): ...
```

### Injected dependencies

- `embed(texts: list[str]) -> list[list[float]]` - returns one vector per input text,
  in the same order. Calls are "expensive": batch them.
- `llm(prompt: str) -> str` - returns the model's reply text.

### `add_documents(docs)`

- `docs` is a list of strings. Store them (keeping insertion order) together with their
  embeddings.
- Call `embed` **exactly once** per `add_documents` call, with the whole list. An empty
  list does nothing (no `embed` call).
- Can be called several times; documents accumulate.

### `retrieve(query, k=3)`

- Embed the query with a single `embed([query])` call.
- Score every stored document by **cosine similarity** between the query vector and the
  document vector. If either vector has zero magnitude, the similarity is `0.0`.
- Return a list of `(doc_text, score)` tuples, best first, at most `k` of them. Ties keep
  insertion order.
- No documents stored: return `[]` (and do not call `embed`).
- `k < 1` raises `ValueError`.

### `answer(query, k=3)`

Returns a dict `{"answer": str, "sources": list[str]}`.

1. Retrieve the top `k` documents. Keep only those whose score is `>= threshold`.
2. If none remain (including the empty-store case), return
   `{"answer": NO_ANSWER, "sources": []}` **without calling `llm`**.
3. Otherwise call `llm` exactly once with this prompt (numbered sources in rank order,
   one per line):

```text
Answer the question using only the sources below. Cite sources like [1].

Sources:
[1] <first document text>
[2] <second document text>

Question: <query>
```

4. Return `{"answer": <llm reply with surrounding whitespace stripped>, "sources": <the
   document texts that were in the prompt, in the same order>}`.

## Example

```python
rag = RAG(embed=my_embed, llm=my_llm, threshold=0.3)
rag.add_documents([
    "Refunds are processed within 5 business days.",
    "Our office is closed on public holidays.",
])
rag.retrieve("how long do refunds take?", k=1)
# [("Refunds are processed within 5 business days.", 0.83)]
rag.answer("how long do refunds take?")
# {"answer": "Refunds take up to 5 business days [1].",
#  "sources": ["Refunds are processed within 5 business days.", ...]}
```

## Running it locally

Write a tiny fake embedder to play with it, e.g. a 26-dimensional "bag of letters"
vector (count of each letter a-z), and a fake `llm` that just returns the first line of the
sources. Add an `if __name__ == "__main__":` block that runs a small demo. Only the standard
library is needed.
''',
    "explore": r'''
# Explore

- **Embeddings APIs**: look up OpenAI's `text-embedding-3-small` and Voyage AI embeddings
  (recommended by Anthropic). What is the vector dimension, and why are these vectors
  usually already *normalized* (which turns cosine similarity into a plain dot product)?
- **Chunking**: real documents are too long to embed whole. Research "chunk size and
  overlap" for RAG and why chunk boundaries matter for retrieval quality.
- **Re-ranking**: search for "cross-encoder re-ranking" (e.g. Cohere Rerank). Why do
  production systems retrieve 20-50 candidates cheaply and then re-rank them?

## Make it real (optional, ungraded)

```bash
uv pip install openai     # or: pip install openai
export OPENAI_API_KEY=sk-...
```

```python
from openai import OpenAI
client = OpenAI()

def embed(texts):
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]

def llm(prompt):
    resp = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content

rag = RAG(embed, llm, threshold=0.3)
```

Load a few paragraphs of your own notes and ask questions. Try questions that are *not*
covered and tune `threshold` until the refusal behaves sensibly.
''',
    "rubric": [
        "Embedding calls are batched: one call per add_documents, one per retrieve, none when unnecessary.",
        "Cosine similarity is implemented in a small, readable helper that handles zero vectors safely.",
        "Retrieval, prompt building and answering are separated into focused methods/helpers rather than one long method.",
        "The threshold/refusal path is explicit and avoids calling the LLM when there is no grounding.",
        "Clear names, no duplicated logic, no global mutable state; the class stores documents and vectors in a sensible structure.",
    ],
    "starter_files": {
        "rag.py": r'''
NO_ANSWER = "I don't know based on the provided documents."


class RAG:
    def __init__(self, embed, llm, threshold=0.2):
        ...

    def add_documents(self, docs):
        ...

    def retrieve(self, query, k=3):
        ...

    def answer(self, query, k=3):
        ...
''',
    },
    "solution_files": {
        "rag.py": r'''
"""A minimal retrieval-augmented generation pipeline with injected models."""

import math

NO_ANSWER = "I don't know based on the provided documents."

PROMPT_TEMPLATE = (
    "Answer the question using only the sources below. Cite sources like [1].\n"
    "\n"
    "Sources:\n"
    "{sources}\n"
    "\n"
    "Question: {query}"
)


def cosine(a, b):
    """Cosine similarity of two equal-length vectors; 0.0 if either is all zeros."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class RAG:
    def __init__(self, embed, llm, threshold=0.2):
        self._embed = embed
        self._llm = llm
        self.threshold = threshold
        self._docs = []
        self._vectors = []

    def add_documents(self, docs):
        docs = list(docs)
        if not docs:
            return
        vectors = self._embed(docs)
        self._docs.extend(docs)
        self._vectors.extend(vectors)

    def retrieve(self, query, k=3):
        if k < 1:
            raise ValueError("k must be at least 1")
        if not self._docs:
            return []
        query_vec = self._embed([query])[0]
        scored = [(doc, cosine(query_vec, vec)) for doc, vec in zip(self._docs, self._vectors)]
        scored.sort(key=lambda pair: pair[1], reverse=True)  # stable: ties keep order
        return scored[:k]

    def build_prompt(self, query, sources):
        numbered = "\n".join(f"[{i}] {doc}" for i, doc in enumerate(sources, start=1))
        return PROMPT_TEMPLATE.format(sources=numbered, query=query)

    def answer(self, query, k=3):
        sources = [doc for doc, score in self.retrieve(query, k) if score >= self.threshold]
        if not sources:
            return {"answer": NO_ANSWER, "sources": []}
        reply = self._llm(self.build_prompt(query, sources))
        return {"answer": reply.strip(), "sources": sources}


if __name__ == "__main__":
    def letters(texts):
        return [[t.lower().count(c) for c in "abcdefghijklmnopqrstuvwxyz"] for t in texts]

    rag = RAG(letters, lambda prompt: prompt.splitlines()[3], threshold=0.5)
    rag.add_documents(["Refunds take five days.", "The office is closed on holidays."])
    print(rag.answer("how long do refunds take?"))
''',
    },
    "tests": r'''
import math
from rag import RAG, NO_ANSWER


def letters(texts):
    return [[t.lower().count(c) for c in "abcdefghijklmnopqrstuvwxyz"] for t in texts]


class CountingEmbed:
    def __init__(self, table=None):
        self.calls = []
        self.table = table

    def __call__(self, texts):
        self.calls.append(list(texts))
        if self.table is not None:
            return [list(self.table[t]) for t in texts]
        return letters(texts)


class FakeLLM:
    def __init__(self, reply="  fake answer [1]  \n"):
        self.prompts = []
        self.reply = reply

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return self.reply


TABLE = {
    "cats": [1.0, 0.0, 0.0],
    "dogs": [0.0, 1.0, 0.0],
    "pets": [1.0, 1.0, 0.0],
    "void": [0.0, 0.0, 0.0],
    "q-cat": [2.0, 0.0, 0.0],
    "q-mix": [3.0, 1.0, 0.0],
    "q-far": [0.0, 0.0, 5.0],
}


def test_add_documents_batches_embed_calls():
    emb = CountingEmbed()
    rag = RAG(emb, FakeLLM())
    rag.add_documents(["alpha", "beta", "gamma"])
    assert emb.calls == [["alpha", "beta", "gamma"]], f"embed calls: {emb.calls!r}"
    rag.add_documents([])
    assert len(emb.calls) == 1, "adding an empty list should not call embed"


def test_retrieve_scores_are_cosine_similarity():
    rag = RAG(CountingEmbed(TABLE), FakeLLM())
    rag.add_documents(["cats", "dogs", "pets"])
    got = dict(rag.retrieve("q-mix", k=3))
    expected = {"cats": 3 / math.sqrt(10), "dogs": 1 / math.sqrt(10), "pets": 4 / math.sqrt(20)}
    for doc, score in expected.items():
        assert abs(got[doc] - score) < 1e-9, f"score for {doc!r}: {got.get(doc)!r}"


def test_retrieve_orders_best_first_and_returns_tuples():
    rag = RAG(CountingEmbed(TABLE), FakeLLM())
    rag.add_documents(["dogs", "pets", "cats"])
    got = rag.retrieve("q-cat", k=3)
    assert [d for d, _ in got] == ["cats", "pets", "dogs"], f"got {got!r}"
    assert all(isinstance(item, tuple) and len(item) == 2 for item in got), f"got {got!r}"


def test_retrieve_respects_k():
    rag = RAG(CountingEmbed(), FakeLLM())
    rag.add_documents(["one", "two", "three", "four"])
    assert len(rag.retrieve("one", k=2)) == 2
    assert len(rag.retrieve("one", k=10)) == 4, "k larger than the store should return everything"


def test_retrieve_embeds_query_once_as_list():
    emb = CountingEmbed()
    rag = RAG(emb, FakeLLM())
    rag.add_documents(["hello world"])
    rag.retrieve("hello", k=1)
    assert emb.calls[-1] == ["hello"], f"last embed call: {emb.calls[-1]!r}"
    assert len(emb.calls) == 2, f"expected 2 embed calls in total, got {len(emb.calls)}"


def test_ties_keep_insertion_order():
    rag = RAG(CountingEmbed(), FakeLLM())
    rag.add_documents(["abc", "cab", "bca"])
    got = [d for d, _ in rag.retrieve("abc", k=3)]
    assert got == ["abc", "cab", "bca"], f"got {got!r}"


def test_zero_vectors_score_zero():
    rag = RAG(CountingEmbed(TABLE), FakeLLM())
    rag.add_documents(["void", "cats"])
    got = dict(rag.retrieve("q-cat", k=2))
    assert got["void"] == 0.0, f"got {got!r}"


def test_invalid_k_raises_value_error():
    rag = RAG(CountingEmbed(), FakeLLM())
    rag.add_documents(["x"])
    for bad in (0, -1):
        try:
            rag.retrieve("x", k=bad)
        except ValueError:
            continue
        raise AssertionError(f"k={bad} should raise ValueError")


def test_empty_store_returns_nothing_without_calls():
    emb, llm = CountingEmbed(), FakeLLM()
    rag = RAG(emb, llm)
    assert rag.retrieve("anything") == []
    assert rag.answer("anything") == {"answer": NO_ANSWER, "sources": []}
    assert emb.calls == [] and llm.prompts == [], "nothing to search: embed/llm should not be called"


def test_answer_builds_numbered_grounded_prompt():
    llm = FakeLLM()
    rag = RAG(CountingEmbed(TABLE), llm, threshold=0.2)
    rag.add_documents(["dogs", "cats", "pets"])
    rag.answer("q-mix", k=2)
    assert len(llm.prompts) == 1, f"llm called {len(llm.prompts)} times"
    expected = (
        "Answer the question using only the sources below. Cite sources like [1].\n"
        "\n"
        "Sources:\n"
        "[1] cats\n"
        "[2] pets\n"
        "\n"
        "Question: q-mix"
    )
    assert llm.prompts[0].strip() == expected, f"prompt was:\n{llm.prompts[0]}"


def test_answer_returns_stripped_answer_and_sources():
    rag = RAG(CountingEmbed(TABLE), FakeLLM(), threshold=0.2)
    rag.add_documents(["dogs", "cats", "pets"])
    got = rag.answer("q-mix", k=2)
    assert got == {"answer": "fake answer [1]", "sources": ["cats", "pets"]}, f"got {got!r}"


def test_low_scores_are_filtered_from_sources():
    llm = FakeLLM()
    rag = RAG(CountingEmbed(TABLE), llm, threshold=0.5)
    rag.add_documents(["cats", "dogs", "pets"])
    got = rag.answer("q-cat", k=3)
    assert got["sources"] == ["cats", "pets"], f"got {got!r}"
    assert "dogs" not in llm.prompts[0], "documents below the threshold must not be in the prompt"


def test_below_threshold_refuses_without_calling_llm():
    llm = FakeLLM()
    rag = RAG(CountingEmbed(TABLE), llm, threshold=0.2)
    rag.add_documents(["cats", "dogs"])
    got = rag.answer("q-far")
    assert got == {"answer": NO_ANSWER, "sources": []}, f"got {got!r}"
    assert llm.prompts == [], "llm must not be called when nothing is relevant"

def test_budget_texts_embedded():
    emb = CountingEmbed()
    rag = RAG(emb, FakeLLM(), threshold=0.0)
    rag.add_documents([f"document number {i} about cats" for i in range(10)])
    for question in ["cats?", "dogs?", "numbers?", "about?"]:
        rag.answer(question)
    used = sum(len(texts) for texts in emb.calls)
    print(f"BUDGET|texts embedded for 10 documents and 4 questions|{used}|14|texts")
    assert used <= 14, f"embedded {used} texts; the budget is 14 (each document once, each question once)"
''',
}
