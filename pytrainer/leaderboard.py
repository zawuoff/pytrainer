"""Eval leaderboard: score your capstone Docs Assistant on fixed questions and beat your best.

Your passing capstone (app.py plus your five modules) runs in the sandbox against the corpus in
content/leaderboard.py, with a fixed offline embedder and a model that quotes its first source, so
scores only change when your code or settings do. A question counts as right when ask() cites the
document that answers it, or refuses when the docs don't say. Tune with an optional
``EVAL_SETTINGS = {"max_chars": ..., "overlap": ..., "threshold": ..., "k": ...}`` in app.py.

Two sets: DEV is shown for tuning; TEST is held out, and the leaderboard ranks on it. A big gap
between them means the settings fit the dev questions rather than the problem.
"""

from __future__ import annotations

import json

from . import capstone, content, db, runner
from .content import leaderboard as data

DEFAULTS = {"max_chars": 500, "overlap": 50, "threshold": 0.2, "k": 3}

HARNESS = r'''
import json
import re
import zlib

import app
from rag import NO_ANSWER

SETTINGS = DEFAULTS_PLACEHOLDER
custom = getattr(app, "EVAL_SETTINGS", None)
if isinstance(custom, dict):
    SETTINGS.update({k: custom[k] for k in SETTINGS if k in custom})


def embed(texts, dims=256):
    vectors = []
    for text in texts:
        vector = [0.0] * dims
        for word in re.findall(r"[a-z0-9]{3,}", str(text).lower()):
            vector[zlib.crc32(word.encode()) % dims] += 1.0
        vectors.append(vector)
    return vectors


def llm(prompt):
    match = re.search(r"^\[1\] (.*?)(?=\n\[2\] |\n\nQuestion:)", prompt, re.S | re.M)
    return match.group(1) if match else NO_ANSWER


def score(questions):
    assistant = app.DocsAssistant("docs", embed, llm, max_chars=SETTINGS["max_chars"],
                                  overlap=SETTINGS["overlap"], threshold=SETTINGS["threshold"])
    rows = []
    for q in questions:
        result = assistant.ask(q["q"], k=SETTINGS["k"])
        sources = [s.get("source") for s in result.get("sources", [])]
        refused = result.get("answer") == NO_ANSWER or not sources
        if q["source"] is None:
            ok, outcome = refused, "refused correctly" if refused else "answered without support"
        elif q["source"] in sources:
            ok, outcome = True, "found the right document"
        else:
            ok, outcome = False, "wrongly refused" if refused else "cited the wrong document"
        rows.append({"q": q["q"], "ok": ok, "outcome": outcome, "sources": sources, "expected": q["source"]})
    return rows, len(assistant)


with open("_questions.json", encoding="utf-8") as fh:
    questions = json.load(fh)
dev, chunks = score(questions["dev"])
test, _ = score(questions["test"])
print("@@RESULT@@" + json.dumps({"settings": SETTINGS, "dev": dev, "test": test, "chunks": chunks}))
'''


def _relative(questions: list[dict]) -> list[dict]:
    """Sources as the assistant reports them: relative to the docs folder it was built on."""
    return [q | {"source": q["source"].removeprefix("docs/") if q["source"] else None} for q in questions]


def _pct(rows: list[dict]) -> int:
    return round(100 * sum(r["ok"] for r in rows) / len(rows)) if rows else 0


def run() -> dict:
    """Score the latest passing capstone. Raises ValueError when there is none yet."""
    app = capstone._latest_passing(capstone.CAPSTONE_ID)
    if not app:
        raise ValueError("Pass the Capstone: Docs Assistant project first. The leaderboard scores your app.py.")
    project = content.load()["projects_by_id"][capstone.CAPSTONE_ID]
    modules, missing = capstone.provided_files(project)
    if missing:
        raise ValueError("Pass these projects first: " + ", ".join(missing))
    files = {**modules, "app.py": app["files"]["app.py"],
             "_leaderboard.py": HARNESS.replace("DEFAULTS_PLACEHOLDER", repr(DEFAULTS)),
             "_questions.json": json.dumps({"dev": _relative(data.DEV), "test": _relative(data.TEST)})}
    out = runner.run_code(files, main="_leaderboard.py", setup_files=data.CORPUS, timeout=60)
    line = next((ln for ln in reversed(out["stdout"].splitlines()) if ln.startswith("@@RESULT@@")), None)
    if not line:
        detail = (out["stderr"] or out["stdout"]).strip()[-800:] or "no output"
        raise ValueError("Your Docs Assistant crashed during the eval:\n" + detail)
    result = json.loads(line[len("@@RESULT@@"):])
    best_before = best()
    dev_score, test_score = _pct(result["dev"]), _pct(result["test"])
    db.ex("INSERT INTO leaderboard_runs(settings, dev, test, details, created_at) VALUES(?,?,?,?,?)",
          (json.dumps(result["settings"]), dev_score, test_score,
           json.dumps({"dev": result["dev"], "chunks": result["chunks"],
                       "test_outcomes": [r["outcome"] for r in result["test"]]}), db.now()))
    return {"settings": result["settings"], "dev": dev_score, "test": test_score, "chunks": result["chunks"],
            "dev_rows": result["dev"], "test_outcomes": _outcomes(result["test"]),
            "new_best": test_score > best_before, "previous_best": best_before}


def _outcomes(rows: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    return counts


def best() -> int:
    row = db.q1("SELECT MAX(test) AS m FROM leaderboard_runs")
    return row["m"] or 0


def overview() -> dict:
    runs = [dict(r) | {"settings": json.loads(r["settings"])} for r in
            db.q("SELECT id, settings, dev, test, created_at FROM leaderboard_runs ORDER BY id DESC LIMIT 20")]
    last = db.q1("SELECT details FROM leaderboard_runs ORDER BY id DESC LIMIT 1")
    return {"runs": runs, "best": best(), "defaults": DEFAULTS, "ready": capstone._latest_passing(capstone.CAPSTONE_ID) is not None,
            "dev_questions": data.DEV, "test_count": len(data.TEST), "docs": sorted(data.CORPUS),
            "last": json.loads(last["details"]) if last else None}
