PROJECT = {
    "id": "chunker",
    "title": "Document Chunker for RAG",
    "order": 3,
    "level": "Intermediate",
    "estimated_hours": 2.5,
    "requires": ["strings", "files", "dataclasses", "regex"],
    "tags": ["rag", "chunking", "documents"],
    "main": "chunker.py",
    "files": ["chunker.py"],
    "brief": r'''
        # Document Chunker for RAG

        Retrieval-Augmented Generation (RAG) answers questions from your own documents:
        documents are split into **chunks**, the chunks are indexed, the best ones are
        retrieved and pasted into the prompt. Chunking quality decides answer quality:
        chunks cut mid-sentence lose meaning, chunks that are too big waste context,
        and without exact **offsets** you cannot highlight or cite the source passage.

        Build a chunker in **`chunker.py`**.

        ## Interface

        ### `Chunk`
        A dataclass (or any class with these attributes, compared by value):

        | field | type | meaning |
        | --- | --- | --- |
        | `text` | `str` | the chunk text |
        | `source` | `str` | where it came from (file path or any label) |
        | `index` | `int` | position of the chunk within its source, starting at 0 |
        | `start` | `int` | start offset in the original text |
        | `end` | `int` | end offset (exclusive) |

        Invariant: **`original_text[chunk.start:chunk.end] == chunk.text`**, always.

        ### `split_text(text: str, max_chars: int = 500, overlap: int = 50, source: str = "") -> list[Chunk]`

        Validation: `max_chars` must be `> 0` and `0 <= overlap < max_chars`, otherwise
        raise `ValueError`.

        Rules:

        1. **Paragraphs** are separated by one or more blank lines (lines that are empty
           or only whitespace). Leading/trailing whitespace of a paragraph is not part
           of it.
        2. **Pack paragraphs**: consecutive paragraphs go into the same chunk as long as
           the chunk's span (from the first paragraph's start to the last one's end,
           including the blank lines between them) is at most `max_chars`. Otherwise
           start a new chunk. A paragraph that fits is never split across chunks.
        3. A paragraph longer than `max_chars` is split into **sentences**. A sentence
           ends after `.`, `!` or `?` followed by whitespace (or at the end of the
           paragraph). Sentences are packed greedily into chunks the same way
           (span <= `max_chars`).
        4. **Overlap** (sentence level): when a long paragraph continues into a new
           chunk, the new chunk starts by repeating trailing whole sentences of the
           previous chunk, as many as fit in `overlap` characters, but only if the
           chunk still fits in `max_chars` and still includes at least one new
           sentence. With `overlap=0` nothing is repeated.
        5. A single sentence longer than `max_chars` is **hard-cut** into windows of
           `max_chars` characters with a step of `max_chars - overlap`
           (`start = s, s + step, s + 2*step, ...`) until the sentence end is reached.
           The last window ends at the sentence end.
        6. Chunks never start or end with whitespace, are never empty, and are in
           document order. `index` counts from 0. Text with no non-whitespace
           characters gives `[]`.

        ### `load_documents(folder: str) -> dict[str, str]`
        Read every `.txt` and `.md` file (extension matched case-insensitively) in
        `folder` **and its sub-folders**. Keys are paths relative to `folder` using
        forward slashes (e.g. `"guides/setup.md"`), values are the file contents (read
        as UTF-8). Other files are ignored. Return the dict with keys sorted. Raise
        `FileNotFoundError` if `folder` does not exist.

        ### `chunk_folder(folder: str, max_chars: int = 500, overlap: int = 50) -> list[Chunk]`
        Chunk every loaded document, documents in sorted-path order, `source` set to the
        relative path, `index` restarting at 0 for each document.

        ## Example

        ```python
        text = "Intro para.\n\nSecond para is here.\n\n" + "Long sentence number one. " * 10
        for c in split_text(text, max_chars=60, overlap=30, source="doc"):
            print(c.index, c.start, c.end, repr(c.text))
        # 0 0 33 'Intro para.\n\nSecond para is here.'
        # 1 35 86 'Long sentence number one. Long sentence number one.'
        # 2 61 112 'Long sentence number one. Long sentence number one.'
        # ...
        ```

        ## Running it locally

        Point `chunk_folder` at a folder of your own notes and print the chunks with
        their offsets. Upload `chunker.py`.
    ''',
    "explore": r'''
        ## Things to research

        - **Chunking strategies**: fixed-size vs. recursive character splitting (look up
          LangChain's `RecursiveCharacterTextSplitter`) vs. semantic chunking. Why do
          most RAG systems use some overlap?
        - **Chunk size vs. embedding model limits**: embedding models have a max input
          length in *tokens*; what happens when you exceed it?
        - **`pathlib.Path.rglob`** and **`Path.relative_to`**, and why
          `Path.as_posix()` matters for cross-platform keys.
        - **Citations**: how start/end offsets let an app highlight the exact passage
          the model used (search "RAG citations grounding").

        ## Make it real (optional, ungraded)

        Embed your chunks with a real embedding model and store them:

        ```bash
        pip install openai
        export OPENAI_API_KEY=sk-...
        ```

        ```python
        from openai import OpenAI
        from chunker import chunk_folder

        client = OpenAI()
        chunks = chunk_folder("my_notes", max_chars=800, overlap=100)
        resp = client.embeddings.create(model="text-embedding-3-small",
                                        input=[c.text for c in chunks])
        vectors = [d.embedding for d in resp.data]
        print(len(vectors), len(vectors[0]))
        ```
    ''',
    "rubric": [
        "Offsets are tracked from the original text (not recomputed with str.find), so text[start:end] == chunk.text holds by construction",
        "Paragraph -> sentence -> hard-cut fallback is structured as clear, separately testable steps",
        "Overlap logic is correct and cannot loop forever",
        "Argument validation with ValueError; file loading uses pathlib and explicit UTF-8",
        "Chunk is a clean dataclass; functions have type hints and docstrings",
    ],
    "starter_files": {
        "chunker.py": r'''
            """Split documents into overlapping chunks with exact offsets."""

            from dataclasses import dataclass


            @dataclass
            class Chunk:
                text: str
                source: str
                index: int
                start: int
                end: int


            def split_text(text, max_chars=500, overlap=50, source=""):
                ...


            def load_documents(folder):
                ...


            def chunk_folder(folder, max_chars=500, overlap=50):
                ...
        ''',
    },
    "solution_files": {
        "chunker.py": r'''
            """Split documents into overlapping chunks with exact offsets."""

            from __future__ import annotations

            import re
            from dataclasses import dataclass
            from pathlib import Path

            EXTENSIONS = {".txt", ".md"}
            _PARAGRAPH_BREAK = re.compile(r"\n[ \t\r\f\v]*\n\s*")
            _SENTENCE_END = re.compile(r"[.!?](?=\s)")

            Span = tuple[int, int]


            @dataclass
            class Chunk:
                text: str
                source: str
                index: int
                start: int
                end: int


            def _strip_span(text: str, start: int, end: int) -> Span | None:
                """Shrink [start, end) to exclude surrounding whitespace; None if empty."""
                while start < end and text[start].isspace():
                    start += 1
                while end > start and text[end - 1].isspace():
                    end -= 1
                return (start, end) if start < end else None


            def _split_spans(text: str, start: int, end: int, pattern: re.Pattern,
                             keep_separator: bool) -> list[Span]:
                spans, pos = [], start
                for match in pattern.finditer(text, start, end):
                    cut = match.end() if keep_separator else match.start()
                    span = _strip_span(text, pos, cut)
                    if span:
                        spans.append(span)
                    pos = match.end()
                span = _strip_span(text, pos, end)
                if span:
                    spans.append(span)
                return spans


            def _paragraphs(text: str) -> list[Span]:
                return _split_spans(text, 0, len(text), _PARAGRAPH_BREAK, keep_separator=False)


            def _sentences(text: str, span: Span) -> list[Span]:
                return _split_spans(text, span[0], span[1], _SENTENCE_END, keep_separator=True)


            def _pack(spans: list[Span], max_chars: int) -> list[list[Span]]:
                """Greedily group consecutive spans whose total extent fits max_chars."""
                groups: list[list[Span]] = []
                for span in spans:
                    if groups and span[1] - groups[-1][0][0] <= max_chars:
                        groups[-1].append(span)
                    else:
                        groups.append([span])
                return groups


            def _hard_cut(text: str, span: Span, max_chars: int, overlap: int) -> list[Span]:
                start, end = span
                step = max_chars - overlap
                pieces = []
                while True:
                    piece = _strip_span(text, start, min(start + max_chars, end))
                    if piece:
                        pieces.append(piece)
                    if start + max_chars >= end:
                        return pieces
                    start += step


            def _split_long_paragraph(text: str, span: Span, max_chars: int,
                                      overlap: int) -> list[Span]:
                out: list[Span] = []
                current: list[Span] = []
                for sentence in _sentences(text, span):
                    if sentence[1] - sentence[0] > max_chars:
                        if current:
                            out.append((current[0][0], current[-1][1]))
                        out.extend(_hard_cut(text, sentence, max_chars, overlap))
                        current = []
                        continue
                    if current and sentence[1] - current[0][0] > max_chars:
                        out.append((current[0][0], current[-1][1]))
                        current = _carry_over(current, sentence, max_chars, overlap)
                    current.append(sentence)
                if current:
                    out.append((current[0][0], current[-1][1]))
                return out


            def _carry_over(previous: list[Span], nxt: Span, max_chars: int,
                            overlap: int) -> list[Span]:
                """Trailing sentences of the previous chunk to repeat in the next one."""
                carried: list[Span] = []
                for sentence in reversed(previous):
                    if previous[-1][1] - sentence[0] > overlap or nxt[1] - sentence[0] > max_chars:
                        break
                    carried.insert(0, sentence)
                return carried


            def split_text(text: str, max_chars: int = 500, overlap: int = 50,
                           source: str = "") -> list[Chunk]:
                """Split text into chunks of at most max_chars with exact offsets."""
                if max_chars <= 0:
                    raise ValueError("max_chars must be positive")
                if not 0 <= overlap < max_chars:
                    raise ValueError("overlap must be >= 0 and smaller than max_chars")
                spans: list[Span] = []
                for group in _pack(_paragraphs(text), max_chars):
                    start, end = group[0][0], group[-1][1]
                    if end - start <= max_chars:
                        spans.append((start, end))
                    else:
                        spans.extend(_split_long_paragraph(text, group[0], max_chars, overlap))
                return [Chunk(text[s:e], source, i, s, e) for i, (s, e) in enumerate(spans)]


            def load_documents(folder: str) -> dict[str, str]:
                """All .txt/.md files under folder, keyed by relative POSIX path."""
                root = Path(folder)
                if not root.is_dir():
                    raise FileNotFoundError(f"no such folder: {folder}")
                docs = {
                    path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
                    for path in root.rglob("*")
                    if path.is_file() and path.suffix.lower() in EXTENSIONS
                }
                return dict(sorted(docs.items()))


            def chunk_folder(folder: str, max_chars: int = 500, overlap: int = 50) -> list[Chunk]:
                chunks: list[Chunk] = []
                for name, text in load_documents(folder).items():
                    chunks.extend(split_text(text, max_chars, overlap, source=name))
                return chunks


            if __name__ == "__main__":
                import sys
                for chunk in chunk_folder(sys.argv[1] if len(sys.argv) > 1 else "."):
                    print(chunk.source, chunk.index, chunk.start, chunk.end, repr(chunk.text[:60]))
        ''',
    },
    "tests": r'''
        import os
        from chunker import Chunk, chunk_folder, load_documents, split_text

        LONG = " ".join(f"Sentence number {i} talks about topic {i % 3}." for i in range(30))
        DOC = ("Title line\n\nFirst short paragraph.\n  \nSecond short paragraph here.\n\n"
               + LONG + "\n\n\nClosing words.\n")

        def check_invariants(text, chunks, max_chars):
            assert chunks, "no chunks returned"
            for i, c in enumerate(chunks):
                assert c.index == i, f"chunk {i} has index {c.index}"
                assert text[c.start:c.end] == c.text, f"chunk {i}: text[start:end] != text ({c.start}, {c.end})"
                assert 0 < len(c.text) <= max_chars, f"chunk {i} has length {len(c.text)}"
                assert c.text == c.text.strip(), f"chunk {i} starts/ends with whitespace: {c.text!r}"
            starts = [c.start for c in chunks]
            assert starts == sorted(starts), "chunks are not in document order"

        def coverage_ok(text, chunks):
            covered = set()
            for c in chunks:
                covered.update(range(c.start, c.end))
            return all(i in covered for i, ch in enumerate(text) if not ch.isspace())

        def test_invalid_arguments_raise_value_error():
            for kwargs in ({"max_chars": 0}, {"max_chars": 10, "overlap": 10},
                           {"max_chars": 10, "overlap": -1}):
                try:
                    split_text("hello", **kwargs)
                except ValueError:
                    continue
                raise AssertionError(f"split_text(..., **{kwargs}) should raise ValueError")

        def test_blank_text_gives_no_chunks():
            assert split_text("") == []
            assert split_text("  \n\n \t ") == []

        def test_small_paragraphs_are_packed_together():
            text = "Alpha one.\n\nBeta two.\n\nGamma three."
            chunks = split_text(text, max_chars=30, overlap=0, source="s")
            got = [(c.text, c.start, c.end) for c in chunks]
            assert got == [("Alpha one.\n\nBeta two.", 0, 21), ("Gamma three.", 23, 35)], f"got {got!r}"
            assert all(c.source == "s" for c in chunks)

        def test_short_paragraph_never_split():
            text = "A" * 10 + "\n\n" + "word " * 8 + "end."
            chunks = split_text(text.strip(), max_chars=50, overlap=0)
            assert [c.text for c in chunks] == ["A" * 10, "word " * 8 + "end."], \
                f"got {[c.text for c in chunks]!r}"

        def test_invariants_on_mixed_document():
            for max_chars, overlap in ((80, 0), (80, 40), (200, 50), (1000, 100)):
                chunks = split_text(DOC, max_chars=max_chars, overlap=overlap, source="d")
                check_invariants(DOC, chunks, max_chars)
                assert coverage_ok(DOC, chunks), f"some text is missing (max_chars={max_chars})"

        def test_long_paragraph_split_on_sentence_boundaries():
            chunks = split_text(LONG, max_chars=120, overlap=0)
            check_invariants(LONG, chunks, 120)
            for c in chunks:
                assert c.text.startswith("Sentence") and c.text.endswith("."), \
                    f"chunk cut mid-sentence: {c.text!r}"
            for a, b in zip(chunks, chunks[1:]):
                assert b.start > a.end, "overlap=0 must not repeat text"
            assert len(chunks) >= 10

        def test_overlap_repeats_trailing_sentences():
            chunks = split_text(LONG, max_chars=120, overlap=50)
            check_invariants(LONG, chunks, 120)
            assert coverage_ok(LONG, chunks)
            overlapping = [b.start < a.end for a, b in zip(chunks, chunks[1:])]
            assert all(overlapping), f"consecutive chunks should overlap: {overlapping}"
            for c in chunks:
                assert c.text.startswith("Sentence"), f"overlap must use whole sentences: {c.text!r}"
            for a, b in zip(chunks, chunks[1:]):
                assert a.end - b.start <= 50, "overlap longer than the overlap setting"
                assert b.end > a.end, "each chunk must add new text"

        def test_hard_cut_windows():
            text = "x" * 250
            got = [(c.start, c.end) for c in split_text(text, max_chars=100, overlap=20)]
            assert got == [(0, 100), (80, 180), (160, 250)], f"got {got!r}"
            got = [(c.start, c.end) for c in split_text(text, max_chars=100, overlap=0)]
            assert got == [(0, 100), (100, 200), (200, 250)], f"got {got!r}"

        def test_chunk_equality_and_fields():
            chunks = split_text("  Hello world.  ", max_chars=50, overlap=0, source="a.txt")
            assert chunks == [Chunk("Hello world.", "a.txt", 0, 2, 14)], f"got {chunks!r}"

        def make_tree():
            os.makedirs("docs/guides", exist_ok=True)
            with open("docs/b.txt", "w", encoding="utf-8") as fh:
                fh.write("Bee file.\n\nSecond para.")
            with open("docs/guides/A.MD", "w", encoding="utf-8") as fh:
                fh.write("# Guide\n\nCafé instructions.")
            with open("docs/image.png", "w") as fh:
                fh.write("not text")
            with open("docs/notes.py", "w") as fh:
                fh.write("print(1)")

        def test_load_documents_recursive_filtered_sorted():
            make_tree()
            docs = load_documents("docs")
            assert list(docs) == ["b.txt", "guides/A.MD"], f"got keys {list(docs)!r}"
            assert docs["guides/A.MD"] == "# Guide\n\nCafé instructions."

        def test_load_documents_missing_folder():
            try:
                load_documents("does_not_exist")
            except FileNotFoundError:
                return
            raise AssertionError("expected FileNotFoundError")

        def test_chunk_folder_sources_and_indexes():
            make_tree()
            chunks = chunk_folder("docs", max_chars=12, overlap=0)
            got = [(c.source, c.index, c.text) for c in chunks]
            assert got[0] == ("b.txt", 0, "Bee file."), f"got {got!r}"
            assert ("b.txt", 1, "Second para.") in got, f"got {got!r}"
            guide = [g for g in got if g[0] == "guides/A.MD"]
            assert guide and guide[0][1] == 0, "index must restart at 0 for each document"
            assert [g[1] for g in guide] == list(range(len(guide)))
    ''',
}
