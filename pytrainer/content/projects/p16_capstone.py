PROJECT = {
    "id": "capstone",
    "title": "Capstone: Docs Assistant",
    "order": 16,
    "level": "Advanced",
    "estimated_hours": 4,
    "kind": "capstone",
    "module": "agents",
    "requires": ["classes", "files", "vectors", "agents"],
    # Your own passing code from these projects sits next to app.py when it runs and is graded.
    "requires_projects": ["chunker", "search-index", "mini-rag", "eval-harness", "tool-agent"],
    "tags": ["rag", "agents", "evals", "portfolio"],
    "main": "app.py",
    "files": ["app.py"],
    "setup_files": {
        "docs/faq.txt": r'''
            Refunds are processed within 5 business days.

            Our office is closed on public holidays.
        ''',
        "docs/guides/setup.md": r'''
            # Setup

            Install Python 3.11 or newer.

            Run the server with python server.py.
        ''',
        "docs/notes.bin": "not a text document\n",
    },
    "brief": r'''
# Capstone: Docs Assistant

Five of your projects are the parts of one real application. Your **chunker** splits documents,
your **search index** finds passages by keyword, your **RAG** pipeline answers from passages by
meaning, your **agent** lets a model pick tools, and your **eval harness** measures how well it
all works. In this project you wire them together into a Docs Assistant: point it at a folder of
notes and ask it questions.

Your own passing code from those five projects is placed next to your file, so you import it like
any module: `from chunker import chunk_folder`, `from search import SearchIndex`,
`from rag import RAG, NO_ANSWER`, `from agent import ToolRegistry, run_agent`,
`from evals import run_eval`. Write only the glue, in **`app.py`**. When it passes, the Capstone
page turns the whole thing into a repository you can push to GitHub.

## What to build

```python
SYSTEM = "..."   # a non-empty system prompt for the agent

class DocsAssistant:
    def __init__(self, folder, embed, llm, max_chars=500, overlap=50, threshold=0.2): ...
    def __len__(self): ...
    def search(self, query, k=5): ...
    def ask(self, question, k=3): ...
    def tools(self): ...
    def chat(self, agent_llm, message, max_steps=5): ...
    def evaluate(self, cases): ...

def main(argv=None): ...
```

`embed` and `llm` are the same injected callables as in your RAG project:
`embed(texts) -> list of vectors` and `llm(prompt) -> str`.

### Building it: `DocsAssistant(folder, embed, llm, max_chars=500, overlap=50, threshold=0.2)`

1. Chunk the folder with your `chunk_folder(folder, max_chars=max_chars, overlap=overlap)` and keep
   the list as `self.chunks`. A missing folder raises `FileNotFoundError` (your chunker already does).
2. Give every chunk an id: `"<source>#<index>"`, for example `"guides/setup.md#1"`.
3. Add every chunk's text to a `SearchIndex`, under its id.
4. Create a `RAG(embed, llm, threshold=threshold)` and add all chunk texts **in one
   `add_documents` call**, in chunk order. So `embed` is called exactly once while building
   (and not at all for an empty folder).

`len(assistant)` is the number of chunks.

### `search(query, k=5)`: keyword search with sources

Return your index's results in the same order, each as a dict:
`{"id": "faq.txt#0", "source": "faq.txt", "text": "<the chunk text>", "score": <float>}`.

### `ask(question, k=3)`: an answer with its sources

Use your RAG's `answer(question, k=k)`. Return
`{"answer": <its answer>, "sources": [{"source": ..., "text": ...}, ...]}`: one entry per source
passage, in the same order, where `source` is the document the passage came from. If the same text
appears in several chunks, use the first chunk. When RAG refuses, this is
`{"answer": NO_ANSWER, "sources": []}` and the model is never called.

### `tools()`: the assistant as agent tools

Return a new `ToolRegistry` with exactly two tools, registered in this order:

- `search_docs(query: str, k: int = 3)`: keyword search; returns a list of
  `{"source": ..., "text": ...}` dicts (the top `k` from `search`).
- `ask_docs(question: str)`: returns the dict from `ask(question)`.

Give each a one-line docstring: it becomes the tool description the model reads.

### `chat(agent_llm, message, max_steps=5)`

Run your agent: `run_agent(agent_llm, self.tools(), message, max_steps=max_steps, system=SYSTEM)`,
and return its answer.

### `evaluate(cases)`

Score the assistant with your eval harness: the model under test answers each case's `input` with
`ask(...)["answer"]`. Return the report from `run_eval`.

### `main(argv=None)`: a command line that works offline

`python app.py <folder> "<question>"` builds an assistant with **offline stand-ins** you write in
`app.py`: a simple embedder (a bag of words hashed into a fixed number of buckets is fine) and a model that quotes the first
source passage. Word counts give low similarity scores, so a lower `threshold` such as `0.1` suits them. Then it prints the answer, and if there are sources, a blank line, `Sources:` and
one `- <source>` line per source passage. `argv` defaults to `sys.argv[1:]`.

- Wrong number of arguments: print a line containing `usage` to stderr and return `2`.
- The folder does not exist: print a line containing `not found` to stderr and return `1`.
- Otherwise return `0`. End the file with `if __name__ == "__main__": sys.exit(main())`.

## Example

```python
assistant = DocsAssistant("docs", embed=my_embed, llm=my_llm, max_chars=60, overlap=10)
len(assistant)                      # 4
assistant.search("office", k=1)
# [{"id": "faq.txt#1", "source": "faq.txt", "text": "Our office is closed on public holidays.", "score": 0.378}]
assistant.ask("How long do refunds take?", k=1)
# {"answer": "Five business days [1].",
#  "sources": [{"source": "faq.txt", "text": "Refunds are processed within 5 business days."}]}
```

```text
$ python app.py docs "How do I install it?"
# Setup

Install Python 3.11 or newer.

Run the server with python server.py.

Sources:
- guides/setup.md
```

## Running it locally

Use **Set up folder** on this page: it writes your `app.py` starter, a copy of your five passing
modules and a sample `docs/` folder into the project folder. Then run the command above.
''',
    "explore": r'''
# Explore

- **Hybrid search**: production systems often run keyword search (like your TF-IDF index) and
  vector search side by side and merge the two rankings. Look up "reciprocal rank fusion". How
  would you add a `hybrid_search` that uses both?
- **Real models**: swap the offline stand-ins for a real embeddings API and a real LLM. Which parts
  of your code had to change? (If you injected them, none of the pipeline should.)
- **Evals as a release gate**: write 10 cases about your own notes and run `evaluate` before and
  after changing `max_chars`. Does a smaller chunk size answer better or worse?
''',
    "rubric": [
        "Glue only: chunking, search, retrieval, the agent loop and grading all come from the learner's own modules, not re-implemented.",
        "The assistant is built once (chunks, index and embeddings) and reused; embed is called a single time while building.",
        "Mapping a passage back to its source is done in one small, readable helper.",
        "Tools have clear names, typed parameters and one-line docstrings a model could use.",
        "The CLI is small and honest: usage and missing-folder errors go to stderr with the right exit codes.",
    ],
    "starter_files": {
        "app.py": r'''
            """Docs Assistant: ask questions about a folder of notes."""

            import sys

            from agent import ToolRegistry, run_agent
            from chunker import chunk_folder
            from evals import run_eval
            from rag import NO_ANSWER, RAG
            from search import SearchIndex

            SYSTEM = ""


            class DocsAssistant:
                def __init__(self, folder, embed, llm, max_chars=500, overlap=50, threshold=0.2):
                    ...

                def __len__(self):
                    ...

                def search(self, query, k=5):
                    ...

                def ask(self, question, k=3):
                    ...

                def tools(self):
                    ...

                def chat(self, agent_llm, message, max_steps=5):
                    ...

                def evaluate(self, cases):
                    ...


            def main(argv=None):
                ...


            if __name__ == "__main__":
                sys.exit(main())
        ''',
    },
    "solution_files": {
        "app.py": r'''
            """Docs Assistant: ask questions about a folder of notes.

            Built from five projects: chunker -> keyword search + RAG -> agent tools, measured by evals.
            """

            import re
            import sys
            import zlib

            from agent import ToolRegistry, run_agent
            from chunker import chunk_folder
            from evals import run_eval
            from rag import NO_ANSWER, RAG
            from search import SearchIndex

            SYSTEM = ("You answer questions about the user's documents. Use the tools to find passages, "
                      "answer only from what they return, and name the source documents.")


            def chunk_id(chunk):
                return f"{chunk.source}#{chunk.index}"


            class DocsAssistant:
                def __init__(self, folder, embed, llm, max_chars=500, overlap=50, threshold=0.2):
                    self.chunks = chunk_folder(folder, max_chars=max_chars, overlap=overlap)
                    self.index = SearchIndex()
                    for chunk in self.chunks:
                        self.index.add(chunk_id(chunk), chunk.text)
                    self.rag = RAG(embed, llm, threshold=threshold)
                    self.rag.add_documents([chunk.text for chunk in self.chunks])
                    self._by_id = {chunk_id(chunk): chunk for chunk in self.chunks}

                def __len__(self):
                    return len(self.chunks)

                def search(self, query, k=5):
                    hits = []
                    for cid, score in self.index.search(query, k=k):
                        chunk = self._by_id[cid]
                        hits.append({"id": cid, "source": chunk.source, "text": chunk.text, "score": score})
                    return hits

                def _source_of(self, text):
                    chunk = next((c for c in self.chunks if c.text == text), None)
                    return {"source": chunk.source if chunk else "", "text": text}

                def ask(self, question, k=3):
                    result = self.rag.answer(question, k=k)
                    return {"answer": result["answer"], "sources": [self._source_of(t) for t in result["sources"]]}

                def tools(self):
                    registry = ToolRegistry()

                    @registry.tool
                    def search_docs(query: str, k: int = 3):
                        """Keyword search over the documents; returns matching passages and their source."""
                        return [{"source": hit["source"], "text": hit["text"]} for hit in self.search(query, k)]

                    @registry.tool
                    def ask_docs(question: str):
                        """Answer a question from the documents, with the passages used as sources."""
                        return self.ask(question)

                    return registry

                def chat(self, agent_llm, message, max_steps=5):
                    return run_agent(agent_llm, self.tools(), message, max_steps=max_steps, system=SYSTEM)

                def evaluate(self, cases):
                    return run_eval(cases, model=lambda question: self.ask(question)["answer"])


            def word_embed(texts, dims=256):
                """Offline stand-in for an embeddings API: a bag of words (3+ letters), hashed into buckets."""
                vectors = []
                for text in texts:
                    vector = [0.0] * dims
                    for word in re.findall(r"[a-z0-9]{3,}", text.lower()):
                        vector[zlib.crc32(word.encode()) % dims] += 1.0
                    vectors.append(vector)
                return vectors


            def quoting_llm(prompt):
                """Offline stand-in for a model: quote the first source passage."""
                match = re.search(r"^\[1\] (.*?)(?=\n\[2\] |\n\nQuestion:)", prompt, re.S | re.M)
                return match.group(1) if match else NO_ANSWER


            def main(argv=None):
                argv = sys.argv[1:] if argv is None else argv
                if len(argv) != 2:
                    print('usage: python app.py <folder> "<question>"', file=sys.stderr)
                    return 2
                folder, question = argv
                try:
                    assistant = DocsAssistant(folder, word_embed, quoting_llm, threshold=0.1)
                except FileNotFoundError:
                    print(f"error: folder not found: {folder}", file=sys.stderr)
                    return 1
                result = assistant.ask(question)
                print(result["answer"])
                if result["sources"]:
                    print("\nSources:")
                    for source in result["sources"]:
                        print(f"- {source['source']}")
                return 0


            if __name__ == "__main__":
                sys.exit(main())
        ''',
    },
    "tests": r'''
        import json

        from app import SYSTEM, DocsAssistant
        from chunker import chunk_folder
        from rag import NO_ANSWER
        from search import SearchIndex

        WORDS = ["refund", "office", "install", "server", "python"]
        DOC_PATHS = {"faq.txt", "guides/setup.md"}


        class KeywordEmbed:
            """One dimension per keyword: deterministic, and zero for unrelated text."""

            def __init__(self):
                self.calls = []

            def __call__(self, texts):
                self.calls.append(list(texts))
                return [[float(t.lower().count(w)) for w in WORDS] for t in texts]


        class FakeLLM:
            def __init__(self, reply="  Five business days [1].  "):
                self.reply = reply
                self.prompts = []

            def __call__(self, prompt):
                self.prompts.append(prompt)
                return self.reply


        def build(**kw):
            emb, llm = KeywordEmbed(), FakeLLM(**kw)
            return DocsAssistant("docs", emb, llm, max_chars=60, overlap=10), emb, llm


        def test_chunks_come_from_your_chunker():
            assistant, _, _ = build()
            expected = chunk_folder("docs", max_chars=60, overlap=10)
            got = [(c.source, c.index, c.text) for c in assistant.chunks]
            assert got == [(c.source, c.index, c.text) for c in expected], f"chunks: {got!r}"
            assert len(assistant) == len(expected) == 4, f"len(assistant) is {len(assistant)}"


        def test_all_chunks_are_embedded_in_one_call():
            assistant, emb, _ = build()
            assert emb.calls == [[c.text for c in assistant.chunks]], f"embed calls while building: {emb.calls!r}"


        def test_search_returns_ids_sources_and_scores():
            assistant, _, _ = build()
            idx = SearchIndex()
            for c in chunk_folder("docs", max_chars=60, overlap=10):
                idx.add(f"{c.source}#{c.index}", c.text)
            want = idx.search("python server install", k=3)
            hits = assistant.search("python server install", k=3)
            assert [(h["id"], round(h["score"], 6)) for h in hits] == [(i, round(s, 6)) for i, s in want], \
                f"search gave {hits!r}"
            first = hits[0]
            assert set(first) == {"id", "source", "text", "score"}, f"keys: {sorted(first)}"
            assert first["source"] == first["id"].split("#")[0] == "guides/setup.md", f"first hit: {first!r}"
            assert "python" in first["text"].lower()


        def test_ask_answers_with_its_sources():
            assistant, _, llm = build()
            got = assistant.ask("How long does a refund take?", k=1)
            assert got["answer"] == "Five business days [1].", f"answer: {got['answer']!r}"
            assert got["sources"] == [{"source": "faq.txt", "text": "Refunds are processed within 5 business days."}], \
                f"sources: {got['sources']!r}"
            assert len(llm.prompts) == 1 and "Question: How long does a refund take?" in llm.prompts[0]


        def test_refuses_without_calling_the_model():
            assistant, _, llm = build()
            got = assistant.ask("Do zebras sleep standing up?")
            assert got == {"answer": NO_ANSWER, "sources": []}, f"got {got!r}"
            assert llm.prompts == [], "the model was called although nothing relevant was found"


        def test_tools_are_registered_for_the_agent():
            assistant, _, _ = build()
            schemas = assistant.tools().schemas()
            assert [s["name"] for s in schemas] == ["search_docs", "ask_docs"], f"tools: {[s['name'] for s in schemas]}"
            search, ask = schemas
            assert search["parameters"]["required"] == ["query"]
            assert search["parameters"]["properties"] == {"query": {"type": "string"}, "k": {"type": "integer"}}
            assert ask["parameters"]["required"] == ["question"]
            assert search["description"] and ask["description"], "give each tool a one-line docstring"


        def test_search_tool_returns_passages_as_json():
            assistant, _, _ = build()
            reply = assistant.tools().dispatch({"id": "c1", "name": "search_docs",
                                                "arguments": json.dumps({"query": "office", "k": 1})})
            assert json.loads(reply) == [{"source": "faq.txt", "text": "Our office is closed on public holidays."}], \
                f"dispatch returned {reply!r}"


        def test_chat_runs_your_agent_with_the_tools():
            assistant, _, _ = build()
            seen = []

            def agent_llm(messages, tools):
                seen.append((list(messages), tools))
                if len(seen) == 1:
                    return {"type": "tool_calls", "calls": [
                        {"id": "c1", "name": "ask_docs", "arguments": json.dumps({"question": "refund time?"})}]}
                answer = json.loads(messages[-1]["content"])["answer"]
                return {"type": "final", "content": "Done: " + answer}

            got = assistant.chat(agent_llm, "How long are refunds?")
            assert got == "Done: Five business days [1].", f"chat returned {got!r}"
            first_messages, tools = seen[0]
            assert first_messages[0] == {"role": "system", "content": SYSTEM} and SYSTEM.strip(), \
                "the agent should start with your SYSTEM prompt"
            assert [t["name"] for t in tools] == ["search_docs", "ask_docs"]


        def test_evaluate_scores_the_assistant():
            assistant, _, _ = build(reply="Refunds take 5 business days [1].")
            cases = [
                {"id": "refunds", "input": "refund timing?", "expected": "business days", "grader": "contains", "tags": ["faq"]},
                {"id": "unknown", "input": "zebras?", "expected": "don't know", "grader": "contains", "tags": []},
            ]
            report = assistant.evaluate(cases)
            assert report["summary"]["passed"] == 2, f"summary: {report['summary']!r}"
            assert [r["output"] for r in report["results"]] == ["Refunds take 5 business days [1].", NO_ANSWER]


        def test_cli_prints_the_answer_and_its_sources():
            r = run_script(["docs", "How do I install it?"])
            assert r.returncode == 0, f"exit code {r.returncode}: {r.stderr[-300:]}"
            lines = r.stdout.splitlines()
            assert lines and lines[0].strip(), "print the answer on the first line"
            assert "Sources:" in lines, f"no 'Sources:' line in:\n{r.stdout}"
            listed = [line[2:] for line in lines[lines.index("Sources:") + 1:] if line.startswith("- ")]
            assert listed and set(listed) <= DOC_PATHS, f"sources listed: {listed!r}"


        def test_cli_reports_usage_and_missing_folders():
            r = run_script([])
            assert r.returncode == 2 and "usage" in r.stderr.lower(), f"no arguments: exit {r.returncode}, stderr {r.stderr!r}"
            r = run_script(["no-such-folder", "hi"])
            assert r.returncode == 1 and "not found" in r.stderr.lower(), f"missing folder: exit {r.returncode}, stderr {r.stderr!r}"
    ''',
}
