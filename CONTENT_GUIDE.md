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

1. **Plain, literal words first. No metaphors or analogies.** "A variable is a name that points
   to a value.", "A dict stores values under keys. You give it a key and get the value back."
2. **Then a tiny runnable example** (```python block, prints something, < 12 lines; the app
   adds Run / Edit & run buttons).
3. **Then the real vocabulary**, introduced gently: "The proper name for this is a
   *return value*." / "You'll see people call this *unpacking*."
4. Optionally one "Watch out" line with the common mistake.
Short sentences. No jargon without explanation. Never contains the exercise solution.
Steps build on each other - the lesson can refer back ("Remember how a dict looks up a key?").

## Library card (`REFERENCE`, module-level, one per chapter)

The Library (`#/library`, or Ctrl+K inside an exercise) shows one entry per chapter, and only
after the learner has finished that chapter. An entry is the chapter title and summary plus
the cards in the chapter file's `REFERENCE` dict, placed between `TOPIC` and `LESSON`:

```python
REFERENCE = {
    "keywords": ["dict", "dictionary", "key", "keyerror"],   # 3-16 lowercase search words
    "cards": [                                               # 3-6 cards, basic to advanced
        {
            "syntax": "d.get(key, default)",                 # one line, <= 60 chars
            "explain": "Reads a value without a KeyError. Returns default when the key is missing.",
            "example": r'''
                usage = {"input": 12}
                print(usage.get("output", 0))
                # 0
            ''',
        },
    ],
}
```

- `explain` is 15-160 characters, literal, and uses no term the chapter has not defined.
- `example` is a complete program of 2-8 lines (<= 72 chars each): standard library only, no
  network, deterministic, and it prints something.
- Every line that starts with `#` in an example is an output line. The `#` lines, in order,
  must be exactly what the example prints, so examples carry no explanatory comments.
- Check one chapter with `python3 scripts/validate_content.py reference:<topic-id>`.

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

## Extra steps (`pytrainer/content/extras/`)

Practice that sits on top of a chapter's learning path: test writing, bug hunts and the like.
Each module there defines `EXTRAS`, a list of normal exercise dicts with one more key, `topic`.
The loader appends them to the end of that chapter and marks them `extra`:

- they are difficulty 1-3 and never the placement step;
- they get reviews like any step, and show as "Extra · ..." in the chapter;
- they never count toward chapter mastery, so adding one can't un-clear a chapter someone finished.

`validate_content.py` checks them like any other step (`python3 scripts/validate_content.py json-wt`).

Two extra kinds have their own rules, which the validator enforces:

- `"kind": "bughunt"`: the starter is the buggy code. Add `visible_tests` (the prompt's examples): the
  starter must pass them and fail the hidden `tests`.
- `"kind": "refactor"`: the starter is working but clunky code. Style checks are tests named
  `test_style_...` (a line budget, the idiom the step is about); the starter must fail only those.
- `"kind": "parsons"`: every non-blank line of `solution` becomes a tile (so no comments or multi-line
  strings, 3-12 lines), plus `distractors` that must not be lines of the solution. `starter` is `""`.

## New chapters: what to cover (fake/injected clients - no network, stdlib only)

- **testing**: why tests; `assert`; test functions; arrange-act-assert; edge cases; testing
  exceptions (try/except + assert, or a helper); fixtures-as-functions; mocking by injecting a fake
  (e.g. a fake LLM function); what pytest adds (lesson only, + link). Mostly `mode: "tests"`.
- **http**: what an HTTP request/response is (request in, response out), methods, URLs & query
  strings (`urllib.parse`), status codes, headers, JSON bodies, auth headers (Bearer), building a
  request with `urllib.request.Request`, timeouts, retries on 429/5xx, webhooks (verifying an
  HMAC signature with `hmac`/`hashlib`). Tests may start a local `http.server` in a thread
  on port 0 and pass its URL to the learner's function - keep it fast and reliable. Mention
  `httpx`/`requests` as what real projects use (research link).
- **sql**: tables/rows (rows and columns), `sqlite3` in-memory, CREATE/INSERT with `?`
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
- **ai-safety**: prompt injection (instructions hidden inside retrieved text), treating
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

# v6: THE TEACHER REWRITE (supersedes the voice rules above for `lesson`, `prompt` and `hints`)

The v4 lessons are accurate but read like a reference manual: a definition, a bold term, the next
definition. A beginner needs a teacher. Everything a learner reads in a step (`lesson`, `prompt`,
`hints`, and `explanation` on predict steps) is rewritten to the rules below. Nothing else in an
exercise changes.

## Who you are writing for

Someone smart who has never programmed, studying alone in the evening, a little nervous. They do
not know what "argument", "iterate" or "in place" mean until you tell them. They will read every
word, so every word must help. Write the way the best teacher you ever had would explain it across
a table: one idea at a time, a reason for each idea, and a chance to try it before moving on.

## The lesson (`lesson` field)

A lesson teaches the ONE idea that this step's exercise needs. Use this shape:

1. **`## ` heading** in plain words that says what the learner will be able to do
   ("The last item, without counting"), not the name of a feature ("Negative indexes").
2. **Start with a situation or a question**, never a definition. Two or three sentences that make
   the learner want the idea: a small problem they can picture, ideally from an AI app (a chat
   history, a list of model names, a bill for tokens) and always explained in everyday words.
3. **Show the smallest example that works** in a ```python block, then say in plain words what
   each part did. Build up in small steps. If an idea has two parts, teach one, let them try it,
   then teach the other.
4. **Idea first, name second.** Describe the thing in everyday words and let it work in an example.
   Only then give it its real name in bold: "Programmers call this number an **index**." Every
   technical term gets this treatment the first time the chapter uses it. From then on, use the
   real term, because the learner needs it for docs, error messages and job interviews.
   One short, accurate everyday comparison is welcome when it truly helps ("a variable is a label
   stuck on a value"). No extended metaphors, no themed stories, no jokes that need explaining.
5. **Make them do something every screenful.** At least one interactive block (next section), and
   two or three in most lessons, each placed directly after the idea it exercises.
6. **`**Watch out:**`** the one mistake beginners really make here, what the error message looks
   like, and what it means.
7. **`**In short:**`** one sentence they can repeat from memory.

Rules:

- 150-400 words of prose, plus examples and blocks. Short sentences. Short paragraphs.
- Say "you". Use contractions sparingly. No hype ("awesome", "super easy", "simply", "just").
  Never tell the learner something is easy or obvious.
- Explain *why*, not only *what*: "Python counts from 0, so the third item is at position 2."
- Never use a word or a Python feature that neither this chapter (in an earlier step) nor an
  earlier chapter has taught. If you need one, explain it in a sentence where you use it.
- Later steps refer back: "Remember the `-1` trick from two steps ago?"
- ASCII only. No em dashes, no emojis, no curly quotes.
- Every ```python block is a complete program that runs with the standard library, prints
  something, and is 12 lines or fewer. Show what it prints as `# ` comment lines directly under
  the `print` that printed them. Full-line `#` comments in lesson examples are output only.
- **Never give away this step's exercise.** Teach the idea with different names and different
  data. The lesson for a predict step must not contain the program the learner has to predict.
- A lesson on a difficulty 2-3 step is a short "Putting it together" (which ideas from the chapter
  combine here and how to plan the work), still with at least one interactive block.

## Interactive blocks

Fenced blocks that the app turns into small activities inside the lesson. They are plain text, so
they are easy to write and `lesson_tools.py check` can run the code in them. A section break is a
line that contains only `---`. Use a mix across a chapter; never the same type three steps in a row.

**quiz**: one question, 2-5 options, exactly one marked `[x]`. Every option carries feedback
after ` :: ` that says *why* it is right or wrong (the wrong options are the mistakes beginners
really make). The question is markdown; for a code sample inside it use a `~~~python` fence.
The app shuffles the options of a quiz and of a fill block, so never refer to an option by its
position ("the first one") and do not write "all of the above".

    ```quiz
    A list has 5 items. Which index reads the same item as `[-1]`?
    - [ ] `[5]` :: Counting starts at 0, so 5 items use positions 0 to 4. `[5]` is past the end.
    - [x] `[4]` :: Yes. Five items sit at positions 0, 1, 2, 3 and 4, so the last one is at 4.
    - [ ] `[0]` :: `[0]` is the first item, not the last.
    ```

**predict**: the learner types what the code prints, then the app runs it and compares. Code,
`---`, then the explanation shown afterwards. The code must run cleanly, print 1-8 lines and
print the same thing every time.

    ```predict
    messages = ["hi", "hello", "how are you?"]
    messages.append("fine, thanks")
    print(messages[-1])
    ---
    `append` put a fourth message at the end, so `-1` now reads `"fine, thanks"`.
    ```

**fill**: code with exactly one `___` gap and 2-4 options (raw code, exactly one `[x]`), each
with feedback. Optional third section: an explanation. With the right option the code must run
and print something; each wrong option must fail or print something else.

    ```fill
    models = ["small", "medium", "large"]
    print(models[___])
    ---
    - [x] -1 :: Right. `-1` is the last item however long the list is.
    - [ ] 3 :: A list of 3 items has positions 0, 1 and 2. Position 3 raises an IndexError.
    - [ ] 0 :: That is the first item.
    ```

**order**: 3-8 lines of code written in the CORRECT order (the app shuffles them), `---`, then
an explanation. The learner arranges them; any order that prints the same output counts.

    ```order
    name = "Ada"
    greeting = "Hello, " + name
    print(greeting)
    ---
    Python runs lines from top to bottom, so `name` must exist before the line that uses it.
    ```

**try**: a small editor in the lesson. Starter code, `---`, the goal in words, `---`, solution
code (never shown; its output is the target), and optionally `---` plus an explanation shown on
success. The starter may contain a bug to fix. Use it for "change one thing and see".

    ```try
    temperature = 0.7
    print("temperature is", temperature)
    ---
    Change one number so the program prints `temperature is 0.2`.
    ---
    temperature = 0.2
    print("temperature is", temperature)
    ---
    The name stayed the same. Only the value stored under it changed.
    ```

**match**: 3-6 `left :: right` pairs (the app shuffles the right side). Good for vocabulary and
for "what does each line print". Optional `---` plus an explanation.

    ```match
    `"hello"` :: text
    `42` :: a whole number
    `3.5` :: a number with a decimal point
    ```

**diagram**: the JSON widgets that already exist (`list-index`, `slice`, `alias-copy`, `dict`,
`stack-queue`, `trace`, `recursion`, `set-ops`, `flow`, `vectors`, `chunks`). Keep the ones that
help, move them next to the idea they show, and introduce each with a sentence that tells the
learner what to try. Make a trace with `python3 scripts/lesson_tools.py trace FILE.py`; never
write trace steps by hand. A diagram is extra: a lesson still needs at least one of the six
blocks above.

Blocks may only use what the lesson has taught up to that point. A block is practice for the idea,
not a second exercise: it should take under a minute.

## The task (`prompt` field)

The learner must be able to tell exactly what to make and how they will know it is right, without
being told how to write it. Use this shape (predict steps keep a one-line prompt):

```markdown
<The situation in 1-3 plain sentences: what this is for and why anyone would want it.>

**Your job:** <one sentence in plain words. Name the function and say what it gives back.
For a fill-the-gap or fix-the-bug step, say that the code is already there and what is missing
or wrong in terms of behaviour, not the fix.>

**What goes in**
- `param`: what it is in plain words, with an example value

**What comes out**
- what is returned (or printed), in plain words, with an example

**Rules**
- one bullet for every behaviour a check tests: edge cases, exact text, rounding, error type

**Examples**
```python
function_name("a", 2)    # returns "..."
```
```

- Read every test and make sure the prompt states that behaviour, in Rules or in Examples. A
  careful beginner who can write the code must pass every check on the first try.
- Use words the chapter has taught. Explain the task's own words ("an allow-list is the list of
  things that are permitted"). Give the reason for an odd rule when there is one.
- Say what, never how: no solution code, no "use `x[-1]`", no algorithm. If a check enforces a
  feature ("uses a `for` loop"), say that the check exists.
- 2-4 examples with exact results, one of them an edge case.
- A script step uses "**Your job:** write a script that ..." and shows the exact output of a run.

## Hints (`hints`, exactly 3)

A hint moves the learner one step, then stops. None of them may contain the answer or a line of it.

1. Point at the idea: which part of the lesson to look at again, or a question to ask themselves.
2. The approach in plain words.
3. The steps in order, in words. Name a tool if needed ("the method that adds one item to the
   end"), but do not write the expression. "Replace `___` with `-1`" is an answer, not a hint.

## What you may and may not change

- Rewrite: `lesson`, `prompt`, `hints`, and `explanation` (predict steps).
- Frozen, byte for byte: `id`, `title`, `difficulty`, `mode`, `code`, `solution`, `tests`,
  `starter`, `placement`, `impl`, `mutants`, `setup_files`, `research`, `concepts`, the order of
  the exercises, `TOPIC` and `REFERENCE`.
- `LESSON` (the chapter notes) stays a compact cheat-sheet. Touch it only to fix a mistake.

## Check your work

```
python3 scripts/lesson_tools.py check tNN_<file>.py     # 0 problems; read every warning
python3 scripts/validate_content.py <topic-id>          # 0 failing, 0 structural issues
```

`check` runs every example and every block, compares frozen fields with the last commit, and
refuses a hint or prompt that quotes a line of the solution.
