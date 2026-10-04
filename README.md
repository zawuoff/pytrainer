# PyTrainer

A local practice app that **tests** your Python for AI engineering. Learn on DataCamp;
come here to prove it by writing real code against hidden tests.

## Open it

Needs Python 3.11 or newer. Nothing else to install.

- **Linux:** run `./install.sh` once. Then search **PyTrainer** in your app launcher (Super + Space)
  or run `pytrainer` in a terminal. It runs as a user service (`systemctl --user status pytrainer`)
  at http://127.0.0.1:8765.
- **macOS:** run `./install.sh` once. It adds a launchd agent (`com.pytrainer.server`) that keeps the
  server running, and the `pytrainer` command in `~/.local/bin` that opens it.
- **Windows (or anywhere, without installing):** `python server.py --open`.
- Reinstall / move the folder: run `./install.sh` again.

## What's inside

| Area | What it does |
| --- | --- |
| **Tonight** | A 1-2 hour session built for you: due reviews, then the next steps, then a combo or a project. Daily goal, streak, heatmap, AI coach. |
| **Course** | 38 chapters in 8 modules (Python Foundations up to Agents, Tools & Safety), 571 steps. Each step is a short lesson followed by a graded exercise. Lessons contain small activities you do while reading: quick checks, predict-the-output, fill the gap, put lines in order, try-it editors and matching pairs. |
| **Step through** | A debugger in every step: press **Debug** (Alt+D) to run your code one line at a time, back and forth, with the line highlighted, each frame's variables (changes light up) and the output so far. For a file that only defines functions it runs a call afterwards, picked from the step's own checks. |
| **Extra practice** | Steps after a chapter's path that don't count toward clearing it. 13 "write the tests" steps across the AI chapters (JSON, regex, API data, prompts, structured output, tool calling, chunking, retrieval, RAG answers, evals, agents, AI safety): you test a real helper, and your tests must pass on it and catch every planted bug. 13 **bug hunts** (lists to vectors): working-looking code that passes every example shown but hides one small bug on an edge case the rules describe; find it (Debug helps) and fix it. 10 **refactors**: clunky but working code (`range(len(...))`, if/elif chains, `+=` strings, hand-written `__init__`/`__repr__`...) to make idiomatic; the checks keep testing behaviour and add a line budget and the idiom the step is about. |
| **Placement test** | One challenge per topic. Passing a topic unlocks everything after it; the AI writes an honest level + code-quality report. |
| **Reviews** | Spaced repetition with FSRS: solved exercises come back just before you'd forget them, and you rebuild them from a blank file. A quick rebuild pushes the next one far out, and a struggle brings it back soon. With an AI connected, due reviews come in a **changed form**: the same skill with new names, story and data, so you rebuild the idea rather than remember the text. Each variant is kept only if its reference passes its tests, its starter fails them, and your old answer fails them too. |
| **Projects** | 16 AI-app builds (prompt kit, chat memory, chunker, search index, evals, terminal chat, mini RAG, structured outputs, tool-calling agent, resilient client, async batching, document index CLI, LLM feature with storage, RAG with evals and a release gate, prompt-injection defences), plus a small project at the end of each of the 38 chapters. Write them in your own editor under `~/pytrainer-lab/projects/<id>`, then submit: hidden tests + AI rubric review. |
| **Capstone** | Five of the projects (chunker, search index, mini RAG, eval harness, tool agent) are the parts of one app. A final project, the Docs Assistant, wires your own passing code together, and the Capstone page exports it as a repository for your GitHub: the code, sample docs, a README with an architecture diagram and your scores, every part's tests with a stdlib runner, and a first git commit (`~/pytrainer-lab/portfolio/docs-assistant`). |
| **Terminal labs** | Real terminal missions verified on disk: running scripts, venv + pip, installing uv, uv projects, `.env` & secrets, PEP 723 scripts, your first real LLM API call. |
| **Library** | A searchable reference that grows as you learn: each chapter you finish unlocks its card (key syntax, a one-line explanation, a tiny example). Inside a step, a module test or a project it is part of the workspace: a tab next to Results and Output, or a panel docked on the left or right (the buttons in its header move it, Ctrl+K opens it). It also holds the notes of the chapter you are in. |
| **Progress** | Mastery per topic, pass rates, first-try rate, struggles, history. |

A chapter **clears** at 60% weighted mastery once you've solved at least one hard exercise and its chapter project passes (or you tested out of it).

## AI (optional)

Settings → AI connection. Uses the CLI you're already logged into — no API keys:
**Claude Code** (`claude -p`), **Codex** (`codex exec`) or **OpenCode** (`opencode run`).
AI powers the Socratic tutor (never gives solutions), code-quality reviews, the placement
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

## Data

One SQLite file, `pytrainer.db`, with daily backups in `backups/` (14 kept):

- Linux: `~/.local/share/pytrainer/`
- macOS: `~/Library/Application Support/PyTrainer/`
- Windows: `%LOCALAPPDATA%\PyTrainer\`

Set `PYTRAINER_DATA` to use another folder. Export from Settings.

## Development

- Stdlib only: `python3 server.py --port 8765` (no dependencies). Python 3.11+.
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
