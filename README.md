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
| **Tonight** | A 1–2 hour session built for you: due reviews → next exercises → a combo → a project. Daily goal, streak, heatmap, AI coach. |
| **Practice** | 23 topics in 3 tracks (Fundamentals → Practical → AI-Engineering Python), 6 graded exercises each (152 total), plus 14 combination challenges that unlock as you clear topics. |
| **Placement test** | One challenge per topic. Passing a topic unlocks everything after it; the AI writes an honest level + code-quality report. |
| **Reviews** | Spaced repetition: solved exercises come back (1, 3, 7, 16, 35… days) and you rebuild them from a blank file. |
| **Projects** | 12 AI-app builds (prompt kit, chat memory, chunker, search index, evals, CLI chat, mini RAG, structured outputs, tool-calling agent, resilient client, async batching, doc Q&A). Write them in your own editor under `~/pytrainer-lab/projects/<id>`, then submit: hidden tests + AI rubric review. |
| **Terminal labs** | Real terminal missions verified on disk: running scripts, venv + pip, installing uv, uv projects, `.env` & secrets, PEP 723 scripts, your first real LLM API call. |
| **Library** | A searchable reference that grows as you learn: each chapter you finish unlocks its card (key syntax, a one-line explanation, a tiny example). Press Ctrl+K inside an exercise to open it beside your code. |
| **Progress** | Mastery per topic, pass rates, first-try rate, struggles, history. |

A topic **clears** at 60% weighted mastery once you've solved at least one hard exercise (or you passed it in the placement test).

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
- Content lives in `pytrainer/content/` — see `CONTENT_GUIDE.md`.
- `python3 scripts/validate_content.py` runs every reference solution against its tests
  and checks every starter fails. It also runs every Library card example (`REFERENCE` in each
  topic file) and checks its `#` output lines against what the example really prints.
