"""Look back: code you wrote weeks ago, read again with what you know now.

A solved step whose passing code is at least MIN_DAYS old comes back as it was: you say what
you'd change, rewrite it if you like (checked by the step's own tests, but never recorded as an
attempt), and compare the two side by side. With an AI connection, a senior engineer's eye
compares them too. A step you've looked back on rests for COOLDOWN_DAYS.

Only practice passes count: a changed-form review's code solves a different task, and a review
rebuild is the same code written from memory, not the first version.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from . import content, db, diffview, lint, progress

MIN_DAYS = 14
COOLDOWN_DAYS = 60
MODES = ("function", "script", "tests")
MIN_LINES = 3


def _code(files: dict) -> str:
    return files.get("solution.py") or "\n\n".join(files.values())


def _lines(code: str) -> int:
    return sum(1 for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#"))


def candidates(now: datetime | None = None) -> list[dict]:
    """Old enough passing code, one per step (the last version from before the cutoff), best first."""
    now = now or datetime.now()
    cutoff = (now - timedelta(days=MIN_DAYS)).isoformat(timespec="seconds")
    resting = {r["item_id"] for r in db.q("SELECT item_id FROM retros WHERE created_at >= ?",
                                         ((now - timedelta(days=COOLDOWN_DAYS)).isoformat(timespec="seconds"),))}
    exs = progress.all_exercises()
    seen: dict[str, dict] = {}
    for r in db.q("SELECT id, item_id, files, created_at FROM attempts WHERE kind='practice' AND status='passed' "
                  "AND created_at <= ? ORDER BY id DESC", (cutoff,)):
        ex = exs.get(r["item_id"])
        if r["item_id"] in seen or r["item_id"] in resting or not ex or ex.get("mode", "function") not in MODES \
                or ex.get("generated") or ex.get("topic") == "exam":
            continue
        try:
            files = json.loads(r["files"])
        except (TypeError, ValueError):
            continue
        if _lines(_code(files)) < MIN_LINES:
            continue
        seen[r["item_id"]] = {"attempt": r["id"], "item": r["item_id"], "files": files, "at": r["created_at"]}
    out = list(seen.values())
    # Longer and older code has the most to gain from a second look.
    for c in out:
        days = (now - datetime.fromisoformat(c["at"])).days
        c["days"] = days
        c["score"] = _lines(_code(c["files"])) * (1 + days / 30) * (1 + exs[c["item"]].get("difficulty", 1) / 3)
    out.sort(key=lambda c: -c["score"])
    return out


def next_available(now: datetime | None = None) -> str | None:
    """The day the next solution becomes old enough to look back on, if one is on its way."""
    now = now or datetime.now()
    cutoff = (now - timedelta(days=MIN_DAYS)).isoformat(timespec="seconds")
    row = db.q1("SELECT MIN(created_at) AS m FROM attempts WHERE kind='practice' AND status='passed' "
                "AND created_at > ?", (cutoff,))
    if not row or not row["m"]:
        return None
    return (datetime.fromisoformat(row["m"]) + timedelta(days=MIN_DAYS)).date().isoformat()


def view(c: dict) -> dict:
    ex = progress.all_exercises()[c["item"]]
    data = content.load()
    topic = data["topics_by_id"].get(ex.get("topic"), {})
    code = _code(c["files"])
    return {"attempt": c["attempt"], "id": c["item"], "title": ex["title"], "prompt": ex["prompt"],
            "mode": ex.get("mode", "function"), "chapter": topic.get("title", ""), "module": topic.get("track"),
            "files": c["files"], "written_at": c["at"], "days_ago": c["days"], "style": lint.check(code)}


def pick(skip: list[str] | None = None) -> tuple[dict | None, int]:
    found = candidates()
    left = [c for c in found if c["item"] not in set(skip or [])]
    return (view(left[0]) if left else None), len(found)


def old_files(attempt_id: int, item_id: str) -> dict:
    row = db.q1("SELECT item_id, files FROM attempts WHERE id=? AND kind='practice' AND status='passed'", (attempt_id,))
    if not row or row["item_id"] != item_id:
        raise ValueError("That old solution wasn't found.")
    return json.loads(row["files"])


def compare(old: dict, new: dict) -> dict | None:
    """Then and now, side by side, through the same aligned diff the results use."""
    return diffview.build({"expected": _code(old), "actual": _code(new), "kind": "text", "types": ["str", "str"]})


def save(attempt_id: int, item_id: str, new: dict, notes: str, passed: bool | None) -> dict:
    old = old_files(attempt_id, item_id)
    rewritten = _code(new).strip() != _code(old).strip() if new else False
    rid = db.ex("INSERT INTO retros(item_id, attempt_id, notes, new_files, passed, created_at) VALUES(?,?,?,?,?,?)",
                (item_id, attempt_id, notes, json.dumps(new) if rewritten else None,
                 None if passed is None or not rewritten else int(bool(passed)), db.now()))
    return {"retro": rid, "rewritten": rewritten, "diff": compare(old, new) if rewritten else None,
            "style_then": lint.check(_code(old)), "style_now": lint.check(_code(new)) if rewritten else None}


def get(retro_id: int) -> dict:
    r = db.q1("SELECT * FROM retros WHERE id=?", (retro_id,))
    if not r:
        raise ValueError("Not found.")
    out = dict(r)
    out["old_files"] = old_files(r["attempt_id"], r["item_id"])
    then = db.q1("SELECT created_at FROM attempts WHERE id=?", (r["attempt_id"],))["created_at"]
    out["days"] = (datetime.now() - datetime.fromisoformat(then)).days
    out["new_files"] = json.loads(r["new_files"]) if r["new_files"] else None
    return out


def set_review(retro_id: int, review: str) -> None:
    db.ex("UPDATE retros SET review=? WHERE id=?", (review, retro_id))


def history(limit: int = 12) -> list[dict]:
    exs = progress.all_exercises()
    rows = db.q("SELECT id, item_id, notes, new_files IS NOT NULL AS rewritten, passed, review, created_at "
                "FROM retros ORDER BY id DESC LIMIT ?", (limit,))
    return [dict(r) | {"title": exs.get(r["item_id"], {}).get("title", r["item_id"]), "rewritten": bool(r["rewritten"])}
            for r in rows]
