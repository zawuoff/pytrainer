# PyTrainer content authoring guide

PyTrainer is a local practice app for a learner moving into **AI engineering** (building
apps on top of LLM APIs: RAG, tool calling, agents, structured outputs) — not model
training. The learner studies elsewhere (DataCamp); this app **tests** them. Exercises
must check real understanding, never hand-hold, and feel relevant to AI-app work
(tokens, prompts, messages, model configs, API responses, documents, chunks, embeddings,
tool calls...) wherever that is natural, while still being fundamentally about the topic.

## Topic module format

One file per topic in `pytrainer/content/topics/tNN_<id>.py` (see `t01_variables.py` —
**read it first, it is the reference example**).

```python
TOPIC = {
    "id": "lists",             # kebab/lowercase id, unique
    "title": "Lists",
    "track": "fundamentals",   # fundamentals | practical | ai-ready
    "order": 4,                # order within the track
    "requires": ["data-types"],# prerequisite topic ids
    "summary": """one or two sentences""",
    "concepts": ["indexing", "slicing", ...],
}
EXERCISES = [ {...}, ... ]     # exactly 6, ordered easy -> hard
```

Exercise dict:

| key | meaning |
| --- | --- |
| `id` | `"<topic-id>-<n>"` |
| `title` | short |
| `difficulty` | 1 (easy), 2 (medium), 3 (hard). Aim for 2x1, 2x2, 2x3 |
| `placement` | `True` on **exactly one** exercise per topic (a medium one that proves competence) |
| `mode` | `"function"` (default: tests import from `solution`) or `"script"` (tests run the file as a program) |
| `prompt` | Markdown task. Precise spec with 1-3 examples. Say what to write, not how (unless the point is a specific feature, e.g. "use a dict comprehension"). No hints about the algorithm. |
| `starter` | Minimal: a signature with `...` body, or a comment. Must FAIL the tests. |
| `tests` | Python source with `test_*` functions (see below) |
| `solution` | Clean, idiomatic reference solution. Never shown to the learner. |
| `setup_files` | optional `{"name.txt": "content"}` placed in the working dir before tests run |

All multi-line strings use `r'''...'''` (raw, triple single quotes). Inside them **never
use `'''`** — use `"""` for docstrings. Indentation is dedented automatically.

## Writing tests

Tests run in a temp dir (cwd) containing `solution.py`. Available globals (no import needed):

- `run_script(args=None, stdin="", env=None, file=None, timeout=5)` -> object with
  `.stdout`, `.stderr`, `.returncode` — runs `python solution.py args...` as a real process.
- `capture(fn, *args, **kwargs)` -> `(return_value, printed_text)`
- `load(name=None)` -> freshly imported learner module (runs top-level code again)
- `source(file=None)` -> the learner's source text (for AST/feature checks)

Rules:
- `from solution import thing` at the top of tests for function mode.
- 3-6 tests per exercise, each named descriptively: `test_empty_list_returns_zero` is shown to
  the learner as "empty list returns zero".
- Use assert messages that show what went wrong **without giving the answer away**:
  `assert got == 42, f"got {got!r}"` is fine. Never reveal the implementation.
- Cover edge cases (empty input, missing keys, wrong types if spec says raise, etc).
- Feature checks via `source()`/`ast` are allowed when the exercise is about a specific
  feature (e.g. "use a comprehension"), but keep them robust.
- Tests must be deterministic and fast (< 1 s). No network. `input()` is disabled in
  function mode; script mode may read stdin via `run_script(stdin=...)`.
- Files: exercises may read/write files in the cwd. Use `setup_files` for fixtures.
- Environment variables: for env-var exercises, either use `run_script(env={...})`, or set
  `os.environ` inside the test and clean it up with try/finally.

## Validation (mandatory)

```
python3 scripts/validate_content.py <id-prefix> [<id-prefix> ...]
```
Every solution must pass all its tests, every starter must fail, each topic needs exactly one
placement exercise. Iterate until it reports 0 failing. Also, mentally check: would a
*wrong-but-plausible* solution be caught? Add a test for the common mistake.

## Tone of prompts

Direct, concise, professional. Like a good take-home test. Show example calls with
expected results in a ```python block. Specify exact output formats and error behaviour
(which exception type to raise). Do not explain the concept — the learner is being tested.

## v2: learning layer (lessons, starter steps, hints) — REQUIRED

The learner is a **real beginner**. They found "return the type name of a value" and a basic
f-string exercise impossible, because those assumed concepts not yet taught. The app must
now TEACH before it tests, and ramp gently. Every topic module needs:

### 1. `LESSON = r'''...'''` (markdown, module-level, 1500-5000 chars)
A friendly, clear mini-lesson for a beginner. Structure:
- `## The idea` - what it is and why it matters (1 short paragraph, relate to AI apps if natural).
- `## How it works` - the core syntax, each piece shown with a tiny ```python example that
  **prints something** (the app adds a Run button to every ```python block, so every block
  must be a complete runnable snippet using only the stdlib, printing its result, < 15 lines).
- `## Common mistakes` - 2-4 bullets, each with the wrong vs right version.
- `## Check yourself` - 2-3 quick questions, answers inside `<details><summary>Answer</summary>...</details>`.
Only use concepts from this topic and earlier topics (see order below). Write like a patient
senior dev teaching a friend: plain words, short sentences, no fluff.

### 2. Five starter steps (difficulty `0`)
Put them FIRST in EXERCISES, ids `<topic>-s1` .. `<topic>-s5`, gentle ramp, each 2-5 minutes:
- at least one **predict** exercise (see below) - reading code is how beginners learn;
- **fill in the blank**: starter is almost complete, with `___` marking what to write
  (a `___` placeholder makes the starter fail, which is required);
- **fix the bug**: starter has one small bug to find;
- **write a tiny thing**: 1-3 lines in the body.
Starters use ONLY concepts from this topic + earlier topics. Their prompts may briefly
remind of the syntax. None of them is the placement exercise. Starters that are not
predict mode are normal function/script exercises (tests + solution + starter).

### 3. `hints`: exactly 3 progressive hints on EVERY exercise (starters AND existing ones)
`"hints": ["...", "...", "..."]`
1. Which concept/tool to use, or where to look (a nudge).
2. The approach in plain words.
3. A step-by-step plan in plain English (may name built-ins/methods, e.g. "use `.get()`"),
   but never the full code solution.

### 4. Predict mode (`"mode": "predict"`, difficulty 0 only)
```python
{
    "id": "lists-s1", "title": "What gets printed?", "difficulty": 0, "mode": "predict",
    "prompt": r'''Read the code and type exactly what it prints.''',
    "code": r'''
        items = ["a", "b", "c"]
        print(items[0])
        print(len(items))
    ''',
    "solution": r'''
        a
        3
    ''',   # must be EXACTLY the program's output (the validator runs the code)
    "explanation": r'''`items[0]` is the first item ...''',   # shown after they get it right
    "starter": "", "tests": "",
    "hints": ["...", "...", "..."],
}
```
Keep predict code short (3-10 lines, 1-5 output lines), deterministic, one or two concepts.

### 5. Existing exercises
Keep all existing ids. Review the existing difficulty-1 exercises of your topics: if one needs
a concept from a LATER topic in the new order below (e.g. an `if` inside the data-types topic,
which now comes before conditionals), rewrite it (prompt/starter/tests/solution/hints) so it
only needs this + earlier topics. Difficulty 2-3 exercises may use earlier topics freely.
Keep placement on the same exercise unless it breaks the rule.

### Validate
`python3 scripts/validate_content.py <topic-id> ...` must print 0 failing, 0 structural for
your topics. It checks hints on every exercise, 5 starters with >= 1 predict, lesson length,
that predict solutions equal the real output, that solutions pass and that starters fail.

## Full topic map (ids are fixed — use exactly these)

| file | id | track | order | requires |
| --- | --- | --- | --- | --- |
| t00_basics.py | basics | fundamentals | 0 | - |
| t01_variables.py | variables | fundamentals | 1 | basics |
| t02_data_types.py | data-types | fundamentals | 2 | variables |
| t06_conditionals.py | conditionals | fundamentals | 3 | data-types |
| t03_fstrings.py | fstrings | fundamentals | 4 | data-types |
| t04_lists.py | lists | fundamentals | 5 | data-types |
| t07_loops.py | loops | fundamentals | 6 | lists, conditionals |
| t05_dicts.py | dicts | fundamentals | 7 | lists, loops |
| t08_functions.py | functions | fundamentals | 8 | loops |
| t09_errors.py | errors | fundamentals | 9 | functions |
| t10_strings.py | strings | practical | 1 | fstrings, loops |
| t11_comprehensions.py | comprehensions | practical | 2 | lists, dicts, loops |
| t12_json.py | json | practical | 3 | dicts, errors |
| t13_files.py | files | practical | 4 | errors, loops |
| t14_env.py | env | practical | 5 | functions, errors |
| t15_scripts.py | scripts | practical | 6 | functions |
| t16_sorting.py | sorting | practical | 7 | functions, lists |
| t17_classes.py | classes | ai-ready | 1 | functions, dicts |
| t18_dataclasses.py | dataclasses | ai-ready | 2 | classes |
| t19_generators.py | generators | ai-ready | 3 | loops, functions |
| t20_regex.py | regex | ai-ready | 4 | strings |
| t21_api_data.py | api-data | ai-ready | 5 | json, errors |
| t22_async.py | async | ai-ready | 6 | functions, errors |
| t23_vectors.py | vectors | ai-ready | 7 | comprehensions, functions |

Titles: Python Basics, Data Types, F-Strings & Formatting, Lists, Dictionaries, Conditionals, Loops, Functions,
Error Handling, Strings & Text Processing, Comprehensions, JSON, Reading & Writing Files,
Environment & Env Variables, Running Scripts & CLIs, Sorting, Lambdas & Key Functions,
Classes & Objects, Dataclasses & Type Hints, Iterators & Generators, Regular Expressions,
Working with API Data, Async Python, Vectors & Similarity (pure Python math behind embeddings/RAG).

NOTE the new fundamentals ORDER (the `order` field): basics, variables, data-types,
conditionals, fstrings, lists, loops, dicts, functions, errors. Set `order` and `requires`
exactly as in the table. "Earlier topics" means earlier in this order (then practical, then ai-ready).

Special case `basics` (new file t00_basics.py, id `basics`, title "Python Basics"): print(),
comments, running code, calling a function, `def` + `return` + indentation as "the answer
format of every exercise", reading an error message and a failing test. 5 starters + 3
regular exercises (difficulty 1, 1, 2; the difficulty-2 one is the placement). Everything
must be doable by someone on day one.

## v3: precise prompts (REQUIRED for every non-predict exercise)

The learner is still learning the vocabulary. They often fail not because they can't code
it but because the prompt left something implicit. A prompt must let a careful beginner
pass ALL checks on the first try if they can code it. Rewrite prompts to this template:

```markdown
<one or two sentences of context: what this is for>

**Write:** `function_name(param1, param2)`   (or: **Write a script** that ...)

- `param1`: what it is, its type, an example value
- `param2`: ...
- **Returns:** exactly what (type + shape), e.g. "a string like `"gpt-4o (128000 tokens)"`"

**Rules** (every rule the checks test, one bullet each - no hidden requirements):
- If the list is empty, return `0`.
- Don't change the list you were given.
- Use a `for` loop (only if a check enforces it).

**Examples**
```python
function_name("a", 2)    # returns "..."
function_name("", 0)     # returns 0
```
```

Rules for the rewrite:
- Every behaviour a test checks must be stated in Rules or visible in Examples (edge cases,
  exact formatting, spaces/punctuation, rounding, exception type AND message when checked,
  "must not modify input", "must use X" feature checks). Read each test and tick it off.
- Examples show calls and their exact expected result/output (as comments, or for scripts a
  "Running `python3 solution.py Ada` prints:" block). 2-4 examples, including one edge case.
  Examples show WHAT, never HOW (no code of the solution itself).
- Name the concept when it helps vocabulary: "(this is called *unpacking*)".
- Keep the test names descriptive (they're shown to the learner as the checklist before
  they start): rename `test_x` style names to what they check, e.g.
  `test_empty_list_returns_zero`. Don't change what tests check unless a test enforces
  something unreasonable for the exercise's level.
- Don't change ids, difficulty, placement flags, solutions (unless a test changed), hints
  (update them if the prompt changes meaning).

# v4: THE COURSE (supersedes earlier counts; v2 hints + v3 precise prompts still apply)

The app is now a proper course, Boot.dev-style: every chapter is a **path of steps**. Each
step = a short **lesson** (left side of the screen, text-heavy, teaches ONE idea) followed
by an **exercise** on exactly that idea (right side: editor; below: output/checks).

## Modules and path order (defines "earlier topics")

| module (TOPIC["track"]) | chapters in order (TOPIC["order"]) |
| --- | --- |
| foundations | basics 0, variables 1, data-types 2, conditionals 3, fstrings 4, lists 5, loops 6, dicts 7, functions 8, errors 9 |
| working-python | strings 1, comprehensions 2, json 3, files 4, env 5, scripts 6, sorting 7 |
| production-python | classes 1, dataclasses 2, **testing 3 (new)**, generators 4, async 5 |
| apis-data | **http 1 (new)**, api-data 2, regex 3, **sql 4 (new)** |
| llm-apps | **llm-basics 1, prompts 2, structured-output 3, tool-calling 4** (all new) |
| rag | vectors 1, **chunking 2, retrieval 3, rag-answers 4** (new) |
| evals | **evals 1, observability 2** (new) |
| agents | **agents 1, ai-safety 2** (new) |

A step may only use concepts from its own chapter (taught in earlier steps) and chapters
earlier in this order. Stdlib only (Python 3.14). No network.

## Chapter file

```python
TOPIC = {"id", "title", "track": <module id>, "order", "requires": [...], "summary", "concepts"}
LESSON = r'''Chapter notes: a compact cheat-sheet of the whole chapter (800-3000 chars) -
             the terms, the syntax, the gotchas. Shown as "Chapter notes" for revision.'''
EXERCISES = [ ...the path, ORDERED BY DIFFICULTY (0s, then 1s, then 2s, then 3s)... ]
```

Per chapter: **at least 14 exercises**: **>= 6 difficulty-0 steps** (at least one `predict`),
**>= 4 difficulty-1 steps**, and the difficulty 2-3 "practice/checkpoint" exercises
(keep the existing ones). Exactly one `placement: True` (a difficulty-2 exercise).
Every difficulty 0-1 step has a `lesson`; difficulty 2-3 may have a short `lesson`
("Putting it together: ...") but it's optional. All exercises: 3 hints, v3 precise prompt.

## The `lesson` field (the heart of it)

Markdown, 250-1800 chars, teaching exactly what this step's exercise needs. Voice:

1. **Plain words and a metaphor first.** "A variable is a labelled box...", "A dict is like a
   coat check: you hand over a ticket (the key) and get your coat (the value) back."
2. **Then a tiny runnable example** (```python block, prints something, < 12 lines; the app
   adds Run / Edit & run buttons).
3. **Then the real vocabulary**, introduced gently: "The proper name for this is a
   *return value*." / "You'll see people call this *unpacking*."
4. Optionally one "Watch out" line with the common mistake.
Short sentences. No jargon without explanation. Never contains the exercise solution.
Steps build on each other - the lesson can refer back ("Remember the coat check?").

## Research steps (`research` field)

Some exercises should push the learner to read real docs (a real AI-engineer skill):
```python
"research": {"note": "Read how `json.dumps` handles the `default` argument, then come back.",
             "links": [{"title": "json.dumps - Python docs", "url": "https://docs.python.org/3/library/json.html#json.dumps"}]}
```
Or with **no links** (module tests only): `{"note": "You'll need a standard-library function we
haven't covered. Search the Python docs for how to compare two dates.", "links": []}` -
say WHAT kind of thing is needed, never the exact name to search. Links must be real,
stable official docs (docs.python.org, developer.mozilla.org, sqlite.org, docs.anthropic.com,
platform.openai.com/docs, etc). Aim for 1-2 research steps per chapter (difficulty 1-3).

## Test-writing exercises (`"mode": "tests"`, used in the testing chapter, allowed elsewhere)

The learner WRITES tests. The code under test is saved as `target.py`.
```python
{"id": "testing-s4", "difficulty": 0, "mode": "tests", "title": "...", "lesson": ..., "prompt": ...,
 "impl": r'''def add(a, b):\n    return a + b''',             # correct implementation
 "mutants": [{"name": "subtracts instead of adding", "code": r'''def add(a, b):\n    return a - b'''},
             {"name": "ignores b", "code": r'''...'''}],         # >= 2 plausible bugs
 "starter": r'''from target import add\n\ndef test_add():\n    ...''',
 "solution": r'''from target import add\n\ndef test_add():\n    assert add(2, 3) == 5''',
 "tests": "", "hints": [...]}
```
Graded: learner's tests must all pass on `impl` and at least one must fail for each mutant.
The prompt describes what `target.py` does (its behaviour spec), not the bugs.

## New chapters: what to cover (fake/injected clients - no network, stdlib only)

- **testing**: why tests; `assert`; test functions; arrange-act-assert; edge cases; testing
  exceptions (try/except + assert, or a helper); fixtures-as-functions; mocking by injecting a fake
  (e.g. a fake LLM function); what pytest adds (lesson only, + link). Mostly `mode: "tests"`.
- **http**: what an HTTP request/response is (restaurant order metaphor), methods, URLs & query
  strings (`urllib.parse`), status codes, headers, JSON bodies, auth headers (Bearer), building a
  request with `urllib.request.Request`, timeouts, retries on 429/5xx, webhooks (verifying an
  HMAC signature with `hmac`/`hashlib`). Tests may start a local `http.server` in a thread
  on port 0 and pass its URL to the learner's function - keep it fast and reliable. Mention
  `httpx`/`requests` as what real projects use (research link).
- **sql**: tables/rows (spreadsheet metaphor), `sqlite3` in-memory, CREATE/INSERT with `?`
  params (and why: SQL injection), SELECT/WHERE/ORDER BY/LIMIT, aggregates & GROUP BY, JOIN,
  transactions/commit, storing chat logs & token usage, pagination with LIMIT/OFFSET.
- **llm-basics**: what an LLM API call is, messages & roles, model params (temperature,
  max_tokens), reading a response dict (OpenAI & Anthropic shapes), tokens & cost math, stop
  reasons, streaming chunks (join deltas), handling errors/rate limits - all with fake clients.
- **prompts**: prompts as code: templates, system vs user, few-shot examples, delimiting user input,
  versioned prompt registry, prompt length budgeting, output format instructions.
- **structured-output**: why (code needs data, not prose), JSON extraction from replies, validating
  shape/types, a tiny schema checker, retry with error feedback (fake LLM), enums/defaults,
  (lesson + link: JSON schema / Pydantic / provider structured outputs).
- **tool-calling**: what a tool is, describing tools as JSON schema, parsing a tool call,
  dispatching to Python functions, validating arguments, returning tool results as messages,
  handling unknown tools/errors, one full request→tool→answer round with a fake model.
- **chunking**: why chunk (context limits, retrieval precision), fixed-size by chars/words, overlap,
  paragraph/sentence-aware splitting, keeping metadata (source, position), token-budget chunks.
- **retrieval**: turning text into vectors (bag-of-words & a fake `embed`), cosine top-k,
  keyword (TF-IDF/BM25-lite) vs semantic, hybrid scoring, metadata filtering, re-ranking,
  a tiny in-memory vector store class.
- **rag-answers**: building the grounded prompt with numbered sources, citations `[1]`,
  "I don't know" when retrieval is weak (threshold), extracting/validating citations from the
  answer, context budget - end-to-end with fake `embed`/`llm`.
- **evals**: why evals (vibes don't scale), test cases/datasets (JSONL), graders: exact, contains,
  regex, numeric tolerance, LLM-as-judge with a fake judge, pass rate & per-tag metrics,
  retrieval metrics (precision@k, recall@k, MRR), comparing two runs, a release gate.
- **observability**: logging module basics & levels, structured (JSON) logs, timing with
  `time.perf_counter` (injected clock in tests), a span/trace recorder (context manager),
  token & cost accounting per request, p50/p95 latency, redacting secrets in logs.
- **agents**: the loop (think → act → observe), stop conditions & max steps, tool registry,
  state/memory, recording every action (audit log), recovering from tool errors, budgets
  (steps/tokens/cost), human approval for risky tools - with scripted fake models.
- **ai-safety**: prompt injection (the "sticky note in the document" metaphor), treating
  retrieved text as untrusted data, delimiting/escaping, detecting suspicious instructions
  (heuristics), least-privilege tool allow-lists, confirming dangerous actions, PII/secret
  redaction in inputs/outputs, output validation before acting. Link OWASP LLM Top 10.

## Module tests (exams)

File `pytrainer/content/exams/<module>.py`:
```python
EXAM = {"module": "foundations", "title": "Python Foundations: module test",
        "intro": r'''What this tests, how to approach it (no hints/tutor in tests).''', "pass_ratio": 0.7}
EXERCISES = [ 5-8 exercises, ids "exam-<module>-1".., difficulty 2-3, mixing chapters,
              realistic AI-app flavoured tasks, v3 precise prompts, 3 hints (hidden during the test) ]
```
Each exam must include **>= 1 research step with doc links** and **>= 1 research step with no
links** (they must look something up themselves; the note says what kind of thing, not the name).

# v5: CHAPTER PROJECTS (one small independent build per chapter)

After finishing a chapter's steps, the learner builds a small project ON THEIR OWN, submits
the files, and hidden tests grade it. Passing it completes the chapter. There are no
solutions shown, ever; the tutor won't write it either. It should feel like a mini real
thing, be genuinely interesting/fun, take 20-80 minutes, and require **a little googling**:
1-2 small things (stdlib only) that the chapter didn't teach, described by WHAT is needed,
never by the exact function name.

File: `pytrainer/content/minis/<module>.py` containing `MINIS = [ {...}, ... ]`, one per chapter:

```python
{
    "id": "mini-<chapter id>",            # unique
    "chapter": "<chapter id>",
    "title": "Short, fun title",
    "estimated_hours": 0.5,               # 0.25 - 1.5
    "main": "app.py",                     # module the tests import (or a script they run)
    "files": ["app.py"],                  # files the learner must submit (1-2 files)
    "brief": r'''
        <2-4 sentences: the story / why it's fun or useful>

        ## What to build
        <precise interface: names, parameters, return values or printed output, file names>

        ## Rules
        - <every behaviour the hidden tests check, one bullet each - no hidden requirements>

        ## Examples
        ```python
        ...calls with their exact expected results / or "Running `python3 app.py Ada` prints:" blocks
        ```

        ## You'll need to find out
        - <1-2 things to look up, described by what they do, e.g. "how to make a string a fixed
          width by padding it on the right" - NOT the method name>

        ## Try it yourself
        <how to run it locally, e.g. python3 app.py, or a tiny snippet to call it>
    ''',
    "explore": r'''Optional extra ideas (ungraded) to push it further.''',
    "rubric": ["3-4 short quality criteria for the optional AI review"],
    "starter_files": {"app.py": r'''# minimal: a comment, or signatures with ... bodies (must FAIL the tests)'''},
    "solution_files": {"app.py": r'''clean reference solution'''},
    "tests": r'''8-14 descriptive test_* functions (names are shown to the learner as results),
                 `from app import ...` or run_script(file="app.py", ...). Fast, deterministic, stdlib.''',
}
```

Rules: use only concepts from this chapter and earlier chapters in the path, PLUS the 1-2
things to find out. Keep scope small enough for the level. Vary the themes across chapters
(tiny games, text tools, trackers, AI-app bits, data crunching, simulations...). Validate:
`python3 scripts/validate_content.py mini:<chapter> ...` → 0 failing.
