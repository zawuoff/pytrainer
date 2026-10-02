PROJECT = {
    "id": "doc-qa",
    "title": "Document Index & Search CLI",
    "order": 12,
    "level": "Intermediate",
    "estimated_hours": 3,
    "requires": ["files", "json", "scripts", "strings", "sorting", "regex"],
    "tags": ["rag", "ingestion", "chunking", "search", "cli"],
    "main": "search.py",
    "files": ["ingest.py", "search.py"],
    "brief": r'''
# Document index & search CLI

Before a RAG app can answer anything, somebody has to build the **ingestion pipeline**:
walk a folder of documents, split them into chunks small enough to fit in a prompt, and
store them in an index with their source so answers can cite where they came from. Then
a **retriever** finds the best chunks for a query. In production the retriever uses
embeddings and a vector database, often combined with good old keyword search (*hybrid
search*). Here you build the whole pipeline as two command-line tools with keyword
scoring, so every result is explainable.

## Files

You upload **two** files: `ingest.py` and `search.py`. Both must be importable without
side effects (put the CLI behind `if __name__ == "__main__":`).

## `ingest.py`

### `chunk_text(text, max_words=120) -> list[str]`

1. Split the text into paragraphs on blank lines (a line that is empty or contains only
   whitespace). Strip each paragraph; drop empty ones.
2. A paragraph with more than `max_words` words (`str.split()` words) is cut into
   consecutive pieces of exactly `max_words` words (the last piece may be shorter); each
   piece is its words joined by single spaces.
3. Greedily pack the paragraphs/pieces, in order, into chunks: append the next one to the
   current chunk (joined with `"\n\n"`) if the chunk's total word count stays
   `<= max_words`; otherwise start a new chunk.

```python
chunk_text("one two\n\nthree four five\n\nsix", max_words=5)
# ["one two\n\nthree four five", "six"]
chunk_text("a b c d e f g", max_words=3)
# ["a b c", "d e f", "g"]
```

### `build_index(folder, max_words=120) -> dict`

- Load every `.txt` and `.md` file under `folder`, **recursively**, read as UTF-8. Other
  extensions are ignored.
- Process files sorted by their path relative to `folder`, written with forward slashes
  (e.g. `"guides/setup.md"`); this relative path is the chunk's `source`.
- Return:

```python
{
    "version": 1,
    "chunks": [
        {"id": "guides/setup.md#0", "source": "guides/setup.md", "chunk": 0, "text": "..."},
        ...
    ],
}
```

  `chunk` is the chunk number within its file, starting at 0; `id` is `"<source>#<chunk>"`.

### CLI

```bash
python ingest.py <folder> [--out index.json] [--max-words 120]
```

- Writes the index as JSON to `--out` (default `index.json`).
- Prints exactly one line: `Indexed <C> chunks from <F> files` (F counts every loaded
  `.txt`/`.md` file, even if it produced no chunks).
- If `<folder>` is not an existing directory: print an error to **stderr**, write
  nothing, and exit with code 1.

## `search.py`

### Scoring (implement exactly)

- **Tokenize**: lowercase, take the runs of `[a-z0-9]` characters, drop stopwords:

```python
STOPWORDS = {"a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "for",
             "and", "or", "what", "how", "does", "do", "with", "it"}
```

- The query terms are the **distinct** tokens of the query.
- For each chunk: `score = (number of distinct query terms that appear among the chunk's
  tokens) / (number of query terms)`.
- Chunks with score 0 are excluded.
- Rank by score (high first); break ties by the total number of occurrences of query
  terms in the chunk (high first); then by position in the index (earlier first).

### `search(index_path, query, k=3) -> list[dict]`

Returns up to `k` results, best first, each
`{"id": ..., "source": ..., "text": ..., "score": float}`.
A query with no terms (e.g. only stopwords) returns `[]`. `k < 1` raises `ValueError`.
A missing index file raises `FileNotFoundError`.

### CLI

```bash
python search.py index.json "how does the event loop work" [-k 3]
```

For each result print two lines:

```text
1. guides/async.md#2 (score 0.67)
   The event loop runs coroutines one at a time and switches between them when ...
```

- First line: `<rank>. <id> (score <score with 2 decimals>)`.
- Second line: three spaces, then the chunk text with all whitespace runs collapsed to
  single spaces; if that is longer than 80 characters, keep the first 80 and add `...`.
- No results: print `No results.` (exit code 0).
- Missing index file: print an error to **stderr**, exit code 1.

## Running it locally

Point `ingest.py` at a folder of your own notes (markdown works great), then search it.
Standard library only (`argparse`, `json`, `pathlib`, `re`).
''',
    "explore": r'''
# Explore

- **Embeddings for retrieval**: keyword overlap misses synonyms ("car" vs "automobile").
  Look up how *dense retrieval* with embeddings fixes that, and what it gets wrong
  (exact IDs, product codes, rare names).
- **BM25**: the classic keyword ranking function behind Elasticsearch and most search
  engines. Compare it to your overlap score (term frequency saturation, inverse document
  frequency, length normalisation).
- **Vector databases & hybrid search**: skim the docs of Chroma (local, pip install),
  pgvector (Postgres extension) or Qdrant. Look up "hybrid search" and "reciprocal rank
  fusion" (RRF) for combining keyword and vector results.

## Make it real (optional, ungraded)

```bash
uv pip install chromadb   # or: pip install chromadb
```

```python
import json
import chromadb

index = json.load(open("index.json"))
client = chromadb.PersistentClient(path="chroma")
col = client.get_or_create_collection("docs")   # uses a small local embedding model
col.upsert(ids=[c["id"] for c in index["chunks"]],
           documents=[c["text"] for c in index["chunks"]],
           metadatas=[{"source": c["source"]} for c in index["chunks"]])
print(col.query(query_texts=["how does the event loop work"], n_results=3))
```

Compare its results with your keyword search on the same questions.
''',
    "rubric": [
        "Chunking, loading, indexing and searching are separate, testable functions; the CLI layer only parses arguments and formats output.",
        "Uses pathlib/argparse idiomatically; the recursive file walk is deterministic (sorted) and uses forward-slash relative paths.",
        "Scoring is implemented once, clearly, with the ranking expressed as a single sort key rather than manual comparison logic.",
        "Errors go to stderr with a non-zero exit code; no traceback for expected user errors (missing folder/index).",
        "Both modules are import-safe (main guard), well named, and free of duplicated code.",
    ],
    "starter_files": {
        "ingest.py": r'''
def chunk_text(text, max_words=120):
    ...


def build_index(folder, max_words=120):
    ...


def main():
    ...


if __name__ == "__main__":
    main()
''',
        "search.py": r'''
STOPWORDS = {"a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "for",
             "and", "or", "what", "how", "does", "do", "with", "it"}


def search(index_path, query, k=3):
    ...


def main():
    ...


if __name__ == "__main__":
    main()
''',
    },
    "solution_files": {
        "ingest.py": r'''
"""Build a JSON chunk index from a folder of .txt/.md documents."""

import argparse
import json
import re
import sys
from pathlib import Path

EXTENSIONS = {".txt", ".md"}
BLANK_LINE = re.compile(r"\n[ \t\r\f\v]*\n")


def _split_long(paragraph, max_words):
    words = paragraph.split()
    if len(words) <= max_words:
        return [paragraph]
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def chunk_text(text, max_words=120):
    pieces = []
    for para in BLANK_LINE.split(text):
        para = para.strip()
        if para:
            pieces.extend(_split_long(para, max_words))
    chunks, current, count = [], [], 0
    for piece in pieces:
        n = len(piece.split())
        if current and count + n > max_words:
            chunks.append("\n\n".join(current))
            current, count = [], 0
        current.append(piece)
        count += n
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def load_documents(folder):
    root = Path(folder)
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix in EXTENSIONS]
    docs = [(p.relative_to(root).as_posix(), p.read_text(encoding="utf-8")) for p in files]
    return sorted(docs)


def build_index(folder, max_words=120):
    chunks = []
    for source, text in load_documents(folder):
        for i, chunk in enumerate(chunk_text(text, max_words)):
            chunks.append({"id": f"{source}#{i}", "source": source, "chunk": i, "text": chunk})
    return {"version": 1, "chunks": chunks}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Index .txt/.md files into JSON chunks.")
    parser.add_argument("folder")
    parser.add_argument("--out", default="index.json")
    parser.add_argument("--max-words", type=int, default=120)
    args = parser.parse_args(argv)
    if not Path(args.folder).is_dir():
        print(f"error: {args.folder!r} is not a directory", file=sys.stderr)
        sys.exit(1)
    files = load_documents(args.folder)
    index = build_index(args.folder, args.max_words)
    Path(args.out).write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Indexed {len(index['chunks'])} chunks from {len(files)} files")


if __name__ == "__main__":
    main()
''',
        "search.py": r'''
"""Keyword-overlap search over a JSON chunk index."""

import argparse
import json
import re
import sys
from collections import Counter

STOPWORDS = {"a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "for",
             "and", "or", "what", "how", "does", "do", "with", "it"}
SNIPPET_CHARS = 80


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def search(index_path, query, k=3):
    if k < 1:
        raise ValueError("k must be at least 1")
    with open(index_path, encoding="utf-8") as fh:
        chunks = json.load(fh)["chunks"]
    terms = set(tokenize(query))
    if not terms:
        return []
    ranked = []
    for position, chunk in enumerate(chunks):
        counts = Counter(tokenize(chunk["text"]))
        matched = [t for t in terms if counts[t]]
        if not matched:
            continue
        score = len(matched) / len(terms)
        occurrences = sum(counts[t] for t in matched)
        ranked.append((-score, -occurrences, position, chunk, score))
    ranked.sort(key=lambda row: row[:3])
    return [{"id": c["id"], "source": c["source"], "text": c["text"], "score": score}
            for *_, c, score in ranked[:k]]


def snippet(text):
    flat = " ".join(text.split())
    return flat if len(flat) <= SNIPPET_CHARS else flat[:SNIPPET_CHARS] + "..."


def main(argv=None):
    parser = argparse.ArgumentParser(description="Search a chunk index.")
    parser.add_argument("index")
    parser.add_argument("query")
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        results = search(args.index, args.query, args.k)
    except FileNotFoundError:
        print(f"error: index file {args.index!r} not found", file=sys.stderr)
        sys.exit(1)
    if not results:
        print("No results.")
        return
    for rank, r in enumerate(results, start=1):
        print(f"{rank}. {r['id']} (score {r['score']:.2f})")
        print(f"   {snippet(r['text'])}")


if __name__ == "__main__":
    main()
''',
    },
    "tests": r'''
import json
import os
from search import search


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


CHUNKS = [
    ("a.md", "Python generators yield values lazily."),
    ("a.md", "Async python uses the event loop. Python python."),
    ("b.txt", "The event loop schedules coroutines."),
    ("b.txt", "Nothing relevant here."),
    ("c.md", "Event loop, event loop: the loop.\n\n  Spaces   everywhere " + "word " * 30),
]


def make_index(path="idx.json"):
    counters = {}
    chunks = []
    for source, text in CHUNKS:
        n = counters.get(source, 0)
        counters[source] = n + 1
        chunks.append({"id": f"{source}#{n}", "source": source, "chunk": n, "text": text})
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "chunks": chunks}, fh)
    return path


def test_chunk_text_packs_paragraphs():
    from ingest import chunk_text
    got = chunk_text("one two\n\nthree four five\n\nsix", max_words=5)
    assert got == ["one two\n\nthree four five", "six"], f"got {got!r}"
    got = chunk_text("  alpha beta \n   \t\n\n\ngamma\n", max_words=10)
    assert got == ["alpha beta\n\ngamma"], f"whitespace-only lines separate paragraphs; got {got!r}"
    assert chunk_text("", max_words=5) == [] and chunk_text("\n\n  \n") == []


def test_chunk_text_splits_long_paragraphs():
    from ingest import chunk_text
    got = chunk_text("a b c d e f g", max_words=3)
    assert got == ["a b c", "d e f", "g"], f"got {got!r}"
    got = chunk_text("x y\n\na b c d e", max_words=3)
    assert got == ["x y", "a b c", "d e"], f"got {got!r}"


def test_ingest_cli_builds_index():
    write("docs/guide.md", "# Guide\n\nInstall the package.\n\nRun the tests.")
    write("docs/sub/faq.txt", "Q: Is it free?\nA: Yes.")
    write("docs/empty.md", "\n\n")
    write("docs/notes.rst", "ignored")
    write("docs/data.json", "{}")
    r = run_script(["docs", "--out", "out.json"], file="ingest.py")
    assert r.returncode == 0, f"ingest failed: {r.stderr[-500:]}"
    assert r.stdout.strip() == "Indexed 2 chunks from 3 files", f"stdout: {r.stdout!r}"
    index = json.load(open("out.json", encoding="utf-8"))
    assert index["version"] == 1
    assert index["chunks"] == [
        {"id": "guide.md#0", "source": "guide.md", "chunk": 0,
         "text": "# Guide\n\nInstall the package.\n\nRun the tests."},
        {"id": "sub/faq.txt#0", "source": "sub/faq.txt", "chunk": 0,
         "text": "Q: Is it free?\nA: Yes."},
    ], f"chunks: {index['chunks']!r}"


def test_ingest_cli_max_words_and_default_out():
    write("corpus/z.txt", "one two three\n\nfour five six\n\nseven")
    write("corpus/a.md", "alpha")
    r = run_script(["corpus", "--max-words", "4"], file="ingest.py")
    assert r.returncode == 0, f"ingest failed: {r.stderr[-500:]}"
    index = json.load(open("index.json", encoding="utf-8"))
    ids = [c["id"] for c in index["chunks"]]
    assert ids == ["a.md#0", "z.txt#0", "z.txt#1"], f"ids: {ids}"
    assert index["chunks"][2]["text"] == "four five six\n\nseven"


def test_ingest_missing_folder_fails_cleanly():
    r = run_script(["no_such_dir", "--out", "never.json"], file="ingest.py")
    assert r.returncode == 1, f"exit code {r.returncode}"
    assert r.stderr.strip() and "Traceback" not in r.stderr, f"stderr: {r.stderr!r}"
    assert not os.path.exists("never.json"), "nothing should be written"


def test_search_scores_and_ranking():
    got = search(make_index(), "How does the Python event loop work?", k=10)
    assert [r["id"] for r in got] == ["a.md#1", "c.md#0", "b.txt#0", "a.md#0"], \
        f"ranking: {[(r['id'], r['score']) for r in got]}"
    assert [r["score"] for r in got] == [0.75, 0.5, 0.5, 0.25]
    assert set(got[0]) == {"id", "source", "text", "score"}, f"keys: {sorted(got[0])}"
    assert got[0]["source"] == "a.md" and got[0]["text"].startswith("Async python")


def test_search_ties_break_by_occurrences_then_position():
    got = search(make_index(), "event loop", k=3)
    assert [r["id"] for r in got] == ["c.md#0", "a.md#1", "b.txt#0"], f"got {[r['id'] for r in got]}"
    assert all(r["score"] == 1.0 for r in got)


def test_search_k_and_empty_queries():
    path = make_index()
    assert len(search(path, "python event loop", k=2)) == 2
    assert search(path, "the of and what", k=3) == [], "stopword-only queries have no terms"
    assert search(path, "quantum banana", k=3) == []
    try:
        search(path, "python", k=0)
    except ValueError:
        pass
    else:
        raise AssertionError("k=0 should raise ValueError")


def test_search_missing_index_raises():
    try:
        search("missing.json", "python")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("expected FileNotFoundError")


def test_search_cli_output_format():
    make_index("cli.json")
    r = run_script(["cli.json", "event loop", "-k", "2"], file="search.py")
    assert r.returncode == 0, f"search failed: {r.stderr[-500:]}"
    snippet = ("Event loop, event loop: the loop. Spaces everywhere " + "word " * 30)[:80] + "..."
    expected = [
        "1. c.md#0 (score 1.00)",
        "   " + snippet,
        "2. a.md#1 (score 1.00)",
        "   Async python uses the event loop. Python python.",
    ]
    assert r.stdout.rstrip("\n").split("\n") == expected, f"stdout was:\n{r.stdout}"


def test_search_cli_default_k_and_no_results():
    make_index("cli.json")
    r = run_script(["cli.json", "python event loop"], file="search.py")
    lines = [l for l in r.stdout.splitlines() if l and not l.startswith("   ")]
    assert len(lines) == 3, f"default k should be 3; stdout:\n{r.stdout}"
    r = run_script(["cli.json", "zebra"], file="search.py")
    assert r.returncode == 0 and r.stdout.strip() == "No results.", f"got {r!r}"


def test_search_cli_missing_index():
    r = run_script(["nope.json", "python"], file="search.py")
    assert r.returncode == 1, f"exit code {r.returncode}"
    assert r.stderr.strip() and "Traceback" not in r.stderr, f"stderr: {r.stderr!r}"


def test_end_to_end_pipeline():
    write("kb/rag.md", "Retrieval augmented generation grounds answers in documents.")
    write("kb/agents.md", "Agents call tools in a loop until they answer.")
    r = run_script(["kb", "--out", "kb.json"], file="ingest.py")
    assert r.returncode == 0, r.stderr[-500:]
    got = search("kb.json", "which tools do agents call?", k=1)
    assert [x["id"] for x in got] == ["agents.md#0"], f"got {got!r}"
''',
}
