# PyTrainer

A local practice app that **tests** your Python for AI engineering. Learn on DataCamp;
come here to prove it by writing real code against hidden tests.

## Open it

- App launcher: search **PyTrainer** (Super + Space), or run `pytrainer` in a terminal.
- It runs as a user service (`systemctl --user status pytrainer`) at http://127.0.0.1:8765.
- Reinstall / move the folder: run `./install.sh` again.

## What's inside

| Area | What it does |
| --- | --- |
| **Tonight** | A 1-2 hour session built for you: due reviews, then the next steps, then a combo or a project. Daily goal, streak, heatmap, AI coach. |
| **Course** | 38 chapters in 8 modules (Python Foundations up to Agents, Tools & Safety), 571 steps. Each step is a short lesson followed by a graded exercise. Lessons contain small activities you do while reading: quick checks, predict-the-output, fill the gap, put lines in order, try-it editors and matching pairs. |
| **Placement test** | One challenge per topic. Passing a topic unlocks everything after it; the AI writes an honest level + code-quality report. |
| **Reviews** | Spaced repetition: solved exercises come back (1, 3, 7, 16, 35… days) and you rebuild them from a blank file. |
| **Projects** | 12 AI-app builds (prompt kit, chat memory, chunker, search index, evals, CLI chat, mini RAG, structured outputs, tool-calling agent, resilient client, async batching, doc Q&A). Write them in your own editor under `~/pytrainer-lab/projects/<id>`, then submit: hidden tests + AI rubric review. |
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

## Data

`~/.local/share/pytrainer/pytrainer.db` (SQLite) with daily backups in `backups/` (14 kept).
Export from Settings.

## Development

- Stdlib only: `python3 server.py --port 8765` (no dependencies).
- Content lives in `pytrainer/content/` — see `CONTENT_GUIDE.md` ("v6" is the lesson and task style).
- `python3 scripts/lesson_tools.py check tNN_file.py` runs every example and every lesson activity of a
  chapter. `show` prints a chapter compactly and `apply` writes new lesson, task and hint text into it.
- `python3 scripts/validate_content.py` runs every reference solution against its tests
  and checks every starter fails. It also runs every Library card example (`REFERENCE` in each
  topic file) and checks its `#` output lines against what the example really prints.
