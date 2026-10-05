# PyTrainer

A local practice app that **tests** your Python for AI engineering. Learn on DataCamp;
come here to prove it by writing real code against hidden tests.

## Open it

**One line, no clone.** With [uv](https://docs.astral.sh/uv/) (it fetches Python 3.11+ if you need it):

```bash
uvx --from git+https://github.com/zawuoff/pytrainer pytrainer
```

It starts the server and opens http://127.0.0.1:8765 in your browser. The same with pipx:
`pipx run --spec git+https://github.com/zawuoff/pytrainer pytrainer`. To keep the command around,
`uv tool install git+https://github.com/zawuoff/pytrainer` (add `--with jedi` for type-aware
autocomplete), then just run `pytrainer`. Options: `--port`, `--no-open`, `--version`.

**Docker:**

```bash
docker run --rm -p 127.0.0.1:8765:8765 -v pytrainer-data:/data ghcr.io/zawuoff/pytrainer
```

Your progress lives in the `pytrainer-data` volume. The image is published from `master` by
`.github/workflows/docker.yml`; until then (or for a fork), build it straight from GitHub:
`docker build -t pytrainer https://github.com/zawuoff/pytrainer.git` and run `pytrainer` instead
of the `ghcr.io` name. Keep the `127.0.0.1:` in `-p`: the server only answers requests addressed to
localhost. Inside a container the code sandbox is the container itself (bubblewrap needs user
namespaces, which most container runtimes don't allow).

**From a clone.** Needs Python 3.11 or newer. Nothing else to install.

- **Linux:** run `./install.sh` once. Then search **PyTrainer** in your app launcher (Super + Space)
  or run `pytrainer` in a terminal. It runs as a user service (`systemctl --user status pytrainer`)
  at http://127.0.0.1:8765.
- **macOS:** run `./install.sh` once. It adds a launchd agent (`com.pytrainer.server`) that keeps the
  server running, and the `pytrainer` command in `~/.local/bin` that opens it.
- **Windows (or anywhere, without installing):** `python server.py --open`.
- Reinstall / move the folder: run `./install.sh` again.

**As an app, on a computer or a phone.** PyTrainer is installable (a PWA): your browser's
**Install app** (Chrome, Edge), **Add to Home Screen** (Safari on iPhone), or the button in
Settings → App. It gets its own window and icon, and it still opens when the server can't be
reached (then it says so, with a Try again button); progress always lives on the server. Browsers
only install from `https://` or `localhost`. To use it on your phone with the server on another
machine, put both on [Tailscale](https://tailscale.com) and run `tailscale serve --bg 8765` on the
server: open the `https://<machine>.<tailnet>.ts.net` address it prints on your phone and install
from there. (The API only answers requests addressed to `localhost`, a Tailscale name (`*.ts.net`)
or a Tailscale address (`100.64.0.0/10`).)

## What's inside

| Area | What it does |
| --- | --- |
| **Tonight** | A 1-2 hour session built for you: due reviews, then the next steps, then a combo or a project. Daily goal, streak, heatmap, AI coach. |
| **Course** | 38 chapters in 8 modules (Python Foundations up to Agents, Tools & Safety), 571 steps. Each step is a short lesson followed by a graded exercise. Lessons contain small activities you do while reading: quick checks, predict-the-output, fill the gap, put lines in order, try-it editors and matching pairs. |
| **Concept map** | All 38 chapters as a graph, one column per module, with every prerequisite drawn and each chapter coloured by status (cleared, in progress with a mastery bar, ready to start, not unlocked). Select one to light up what it builds on and what it unlocks. Lists what you're ready for and "weak foundations": chapters you've started on prerequisites you haven't cleared. From the Course page. |
| **Step through** | A debugger in every step: press **Debug** (Alt+D) to run your code one line at a time, back and forth, with the line highlighted, each frame's variables (changes light up) and the output so far. For a file that only defines functions it runs a call afterwards, picked from the step's own checks. |
| **"Why did it fail?"** | When a check like `assert result == expected` fails, the results show the expected value and what your code gave side by side, lines aligned and the differing characters highlighted (spaces and tabs drawn as · and →, so whitespace mistakes are visible), with a note for the usual surprises: different types (`"4"` vs `4`), only whitespace, only case, or only the final newline. The test harness records both sides of each `==` as it runs (each side is still evaluated once), so this works for every existing step without changing any tests. |
| **Help when you're stuck** | When the same check keeps failing (a few minutes and at least two checks, or longer after one), a small card in the corner of the editor offers a way forward: the next hint, a pointer from the tutor about where to look (with an AI connection), or stepping through your code. It never takes focus; "Not now" quiets it for five minutes, and it only counts time you're actually at it. Never in module tests or changed-form reviews. Turn it off in Settings. |
| **Extra practice** | Steps after a chapter's path that don't count toward clearing it. 13 "write the tests" steps across the AI chapters (JSON, regex, API data, prompts, structured output, tool calling, chunking, retrieval, RAG answers, evals, agents, AI safety): you test a real helper, and your tests must pass on it and catch every planted bug. 13 **bug hunts** (lists to vectors): working-looking code that passes every example shown but hides one small bug on an edge case the rules describe; find it (Debug helps) and fix it. 10 **refactors**: clunky but working code (`range(len(...))`, if/elif chains, `+=` strings, hand-written `__init__`/`__repr__`...) to make idiomatic; the checks keep testing behaviour and add a line budget and the idiom the step is about. 10 **Parsons problems**: a function's lines, shuffled and unindented, plus a couple of decoys; click or drag them into order and indent them (keyboard works too). Any arrangement that passes the checks counts. 12 **traceback drills**: a short program really crashes and you see its traceback; click the line you'd change. Often that isn't where the error surfaced (a typo two functions up, the wrong variable passed in, a library frame to look past), and a wrong pick gets a pointed nudge. |
| **Placement test** | One challenge per topic. Passing a topic unlocks everything after it; the AI writes an honest level + code-quality report. |
| **Reviews** | Spaced repetition with FSRS: solved exercises come back just before you'd forget them, and you rebuild them from a blank file. A quick rebuild pushes the next one far out, and a struggle brings it back soon. With an AI connected, due reviews come in a **changed form**: the same skill with new names, story and data, so you rebuild the idea rather than remember the text. Each variant is kept only if its reference passes its tests, its starter fails them, and your old answer fails them too. |
| **Interview mode** | A practice coding interview: one medium (20/30 min) or hard (45 min) problem from chapters you've reached, a countdown, Run as often as you like and one graded submit. With an AI connected it then plays the interviewer: three follow-up questions about your code, reacting to each answer, and a scored debrief (correctness, problem solving, communication, code quality, a verdict, strengths and what to work on). Without AI: standard questions and a self-review checklist. From the Projects page. |
| **Speed drill** | Timed rounds (3, 5 or 10 minutes) of easy steps you've already solved, back to back: Ctrl+Enter checks and moves on, Alt+S skips. Personal bests per round length. Drill checks never count as attempts or change your reviews. From the Reviews page. |
| **On the go** | Practice for a phone, where typing code is a pain but reading it isn't: predict what a short program prints, tap the line you'd change in a crashed program's traceback, flip flashcards made from your Library cards, or read the notes of the chapter you're on. One item at a time with big buttons; a mixed round interleaves the kinds, and cards you didn't know come back at the end. Everything comes from chapters you've reached, unsolved steps first, and steps go through the normal check, so they count toward your chapters and reviews. From the Reviews page, and on Home when the screen is narrow. |
| **Projects** | 17 AI-app builds (prompt kit, chat memory, chunker, search index, evals, terminal chat, mini RAG, structured outputs, tool-calling agent, resilient client, async batching, document index CLI, LLM feature with storage, RAG with evals and a release gate, tracing an agent, prompt-injection defences), plus a small project at the end of each of the 38 chapters. Write them in your own editor under `~/pytrainer-lab/projects/<id>`, then submit: hidden tests + AI rubric review. |
| **Budgets** | Some projects also have to stay within a budget, shown as "used of limit" bars in the results: the async batch processor must finish 20 slow calls in time (concurrency), mini RAG may embed each document and question only once, and the resilient client must serve repeated requests from its cache. Budget checks are hidden tests that print `BUDGET|label|used|limit|unit`. |
| **Capstone** | Five of the projects (chunker, search index, mini RAG, eval harness, tool agent) are the parts of one app. A final project, the Docs Assistant, wires your own passing code together, and the Capstone page exports it as a repository for your GitHub: the code, sample docs, a README with an architecture diagram and your scores, every part's tests with a stdlib runner, and a first git commit (`~/pytrainer-lab/portfolio/docs-assistant`). |
| **Observability** | The "Trace Your Agent" project: write a small tracer (nested spans kept in a `contextvars.ContextVar` so they work across `await`, error status, attributes, a sync/async decorator, JSON Lines export), then instrument an agent loop with run, step, model-call and tool-call spans. Any Run that writes `traces.jsonl` gets a **trace waterfall** under its output: spans nested under their parents on a time axis, failures marked, click one for its attributes. The `#/traces` page opens a `traces.jsonl` from anywhere, with a per-span-name summary. |
| **Eval leaderboard** | Your passing capstone answers questions about a made-up app's docs, with a fixed offline embedder and model so only your code and settings move the score: right when it cites the answering document, or refuses when the docs don't say. Tune `EVAL_SETTINGS` (chunk size, overlap, threshold, k) against 10 visible dev questions; the leaderboard ranks 10 held-out ones, so overfitting shows as a gap. Every run and your best are kept. |
| **Terminal labs** | Real terminal missions verified on disk: running scripts, venv + pip, installing uv, uv projects, `.env` & secrets, PEP 723 scripts, your first real LLM API call, a FastAPI service, Docker, CI, and "Ship it": package a CLI with uv, test it, build a wheel and install it as a command. |
| **Library** | A search engine over what you've learned. A chapter's reference cards (key syntax, a one-line explanation, a tiny example) join the Library as soon as you've solved its lesson steps, or tested out of the chapter or its module; chapters you haven't reached aren't shown at all. Search ranks single cards (the card about slicing for "slice", typos forgiven), lifting the ones you've opened lately, the chapters you're practising or failing in, and the chapters the current one builds on; anything else in your Library is still one search away. With an empty box it suggests cards "for you" and lists your chapters by module. Inside a step, a module test or a project it is part of the workspace: a tab next to Results and Output, or a panel docked on the left or right (the buttons in its header move it, Ctrl+K opens it). It also holds the notes of the chapter you are in. |
| **Progress** | Mastery per topic, pass rates, first-try rate, struggles, history. |
| **XP and levels** | XP worked out from your history, so there's nothing to farm and nothing lost: 10/20/30 per step by difficulty (+5 for a clean first try, half after seeing the solution), reviews, chapters, projects (the capstone most), labs, achievements, drills and interviews, and 10 for each day you practise. Level n takes 50·n·(n−1) XP, with a title every five levels; the whole course is about 25 levels. The sidebar shows your level, each action shows "+N XP", a level-up gets a card, and Progress breaks the total down by source. |
| **Themes and zen mode** | Seven themes in Settings > Appearance, picked from preview cards: follow the system, Dark, Light, Nord, Solarized Light, Sepia and High contrast (every text and syntax colour checked for at least 4.5:1 contrast, 7:1 in High contrast), plus a code font size from 12 to 20 px. Zen mode (Alt+Z or the Zen button on a step or project) leaves only the editor, Run and Check on screen; T slides the task in, XP pings are muted, it carries on to the next step, and Alt+Z or Esc ends it. |
| **Open in VS Code** | "Open in VS Code" on a step or project writes your code to `~/pytrainer-lab/steps/<id>` or `~/pytrainer-lab/projects/<id>` (with the brief, and any data files) and opens it in VS Code, Cursor or VSCodium, whichever is on your PATH (or through a `vscode://` link). Work already in the folder is never overwritten. While it's open, every save reloads in the browser within a second or so, and Run, Check and Submit use it; the page editor is read-only until you press Stop watching. |
| **REPL panel** | A REPL tab next to Output on every step and project: a live Python session in the sandbox that keeps your variables between commands, next to a copy of your files so you can import them. Expressions echo their value (and `_`), blocks continue with `...` until a blank line, pasted blocks run as one, ↑/↓ recall history. "Load my code" starts fresh with your file run first, like `python -i`. A command that runs past 10 s resets the session; idle sessions close after 20 minutes. |
| **Autocomplete and inline errors** | Every code editor underlines syntax errors (with the message on a line under it) and names that are never defined ("'heigth' is never defined. Did you mean 'height'?") as you type. Ctrl+Space, a dot, or two letters of a name opens suggestions: names in your file, builtins and keywords, attributes of imported stdlib modules (`json.du` → `dump`, `dumps`), of `self`, and of variables assigned a literal. Code is parsed, never run, and modules with import side effects are never imported. With [Jedi](https://github.com/davidhalter/jedi) installed, suggestions use real type inference; it stays optional. Turn it off in Settings. |
| **Streak freeze** | Every 7 days in a row earns a streak freeze (hold up to 2). Miss a day while holding one and it's used automatically: the streak carries on, the day shows as a snowflake on the heatmap, and Home tells you a freeze covered yesterday. It's replayed from your activity, so nothing is stored; turn it off in Settings for a strict streak. |
| **Weekly recap** | Each Monday-to-Sunday week as a card: minutes, steps solved, reviews passed and XP (each compared with the week before), a bar per day, best day, most practised chapter, toughest win (the step that took the most failed checks before you solved it), projects shipped, labs and achievements. Save it as a 1080×1350 image or copy it as text; browse back through earlier weeks. Home offers last week's recap early in the week. |
| **Achievements** | 32 milestones in six groups (practice, course, memory, habit, extra practice, building): solving on your own, clean first tries, clearing chapters and modules, passing reviews, streaks, bug hunts and refactors, speed drills, projects, labs, the capstone, a passed practice interview, 80+ on the leaderboard, plus two secret ones. They're earned from what you actually did, kept once earned, and announced with a toast right after the action that earned them; `#/achievements` shows progress toward the rest. |
| **Weakness radar** | Sorts your recent failed checks into patterns by what they say went wrong (empty input, boundaries, changing inputs by accident, wrong exceptions, order, missing keys, types, text details, code that doesn't run, endless loops), recent ones counting more. Shows the chapters where it happens and builds a 6-step targeted session (open steps, related extra practice, lapsed steps to rebuild) that the step page walks you through. From the Progress page. With an AI connected, **a drill from your mistakes**: your AI reads your last 10 failed attempts (task, your code, what failed), says what they have in common, and writes 3 new exercises aimed at it; each is kept only if its reference passes its tests and its starter fails. |

A chapter **clears** at 60% weighted mastery once you've solved at least one hard exercise and its chapter project passes (or you tested out of it).

## AI (optional)

Settings → AI connection. Uses the CLI you're already logged into — no API keys:
**Claude Code** (`claude -p`), **Codex** (`codex exec`) or **OpenCode** (`opencode run`).
AI powers the Socratic tutor (never gives solutions), explain-it-back grading (after a solve, explain why your code works and get a 1-5 understanding score with what's missing), code-quality reviews, the placement
report, AI-generated challenges (kept only if their reference solution passes their own
tests), project reviews and the coach. Everything test-based works without AI.

## Code sandbox

Your code, and the tests that grade it (including tests an AI wrote), run in a throwaway folder with
CPU, memory and time limits. On Linux they also run in an OS sandbox. Settings shows which level you have:

| Level | When | What it blocks |
| --- | --- | --- |
| `bwrap` | [bubblewrap](https://github.com/containers/bubblewrap) is installed (`apt install bubblewrap`, `dnf install bubblewrap`) | Network (loopback still works), writes anywhere outside the run folder, your PyTrainer data |
| `netns` | no bubblewrap, but unprivileged user namespaces work | Network |
| `basic` | macOS, Windows, or neither of the above | Nothing beyond the limits above |

Set `PYTRAINER_SANDBOX=netns` or `basic` to choose a lower level.

**Real model calls from Run (opt-in).** Tick "Real model calls" in the Output panel of a step or project and
your code can `from pytrainer_llm import llm, embed`: `llm(prompt)` reaches the AI you connected (at most 6
calls per run) and `embed()` is a small local stand-in for an embeddings API. The sandbox still has no
network: each call is written as a file in the run folder and answered by PyTrainer from outside, and every
call is listed under the output. Grading never uses it, so checks stay deterministic.

## Data

One SQLite file, `pytrainer.db`, with daily backups in `backups/` (14 kept):

- Linux: `~/.local/share/pytrainer/`
- macOS: `~/Library/Application Support/PyTrainer/`
- Windows: `%LOCALAPPDATA%\PyTrainer\`

Set `PYTRAINER_DATA` to use another folder. Export from Settings.

## Development

- Stdlib only: `python3 server.py --port 8765` (no dependencies). Python 3.11+. Optional: `pip install jedi` for type-aware autocomplete.
- The front-end is plain ES modules, with no build step: `static/js/main.js` (router, entry point),
  `core.js` (state, API client, helpers), `diagrams.js` / `blocks.js` (lesson widgets), `workspace.js`
  (editor and results), `library.js`, and one file per page in `static/js/views/`.
- `python3 -m unittest discover -s tests -t .` runs the app's own tests: the scheduler, the runner and
  sandbox, the HTTP API end to end, and the front-end module graph. They use a scratch data folder.
- Content lives in `pytrainer/content/` — see `CONTENT_GUIDE.md` ("v6" is the lesson and task style).
- `python3 scripts/lesson_tools.py check tNN_file.py` runs every example and every lesson activity of a
  chapter. `show` prints a chapter compactly and `apply` writes new lesson, task and hint text into it.
- `python3 scripts/validate_content.py` runs every reference solution against its tests
  and checks every starter fails. It also runs every Library card example (`REFERENCE` in each
  topic file) and checks its `#` output lines against what the example really prints.
- CI (`.github/workflows/ci.yml`) runs all of the above on every push: Linux on Python 3.11 to 3.14
  with bubblewrap installed, plus the unit tests on macOS and Windows.
