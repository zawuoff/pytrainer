"""Where it got hard: steps and chapters ranked by how much trouble they caused.

For the learner, the steps worth another go. For whoever writes the content, the prompts, hints and
checks that may need work: a step that many tries fail on the same check, or that is mostly solved
after a hint or the solution, is often unclear rather than hard.

Only practice checks count (reviews and drills are re-solving, not first contact). Per step:
- fails: failing checks before the first solve (all of them while unsolved),
- hints and whether the solution was shown, tutor questions asked,
- the check that failed most often, by name (or the kind of error),
- trouble: one number to rank by, fails + 2 per hint + 4 for the solution + 1 per tutor question,
  plus 3 while still unsolved.
"""

from __future__ import annotations

import json
import re
from collections import Counter

from . import content, db, progress

TROUBLE = {"fail": 1, "hint": 2, "revealed": 4, "tutor": 1, "unsolved": 3}


def _failure(result_json: str | None, status: str) -> str | None:
    try:
        r = json.loads(result_json or "{}")
    except ValueError:
        return None
    if status == "timeout":
        return "time limit"
    if r.get("error"):
        last = r["error"].strip().splitlines()[-1] if r["error"].strip() else ""
        m = re.match(r"(\w+(?:Error|Exception))\b", last)
        return m.group(1) if m else "error"
    failing = [t["name"] for t in r.get("tests", []) if not t.get("passed")]
    return failing[0] if failing else None


def _tutor_questions() -> dict[str, int]:
    out = {}
    for r in db.q("SELECT item_id, messages FROM chats"):
        try:
            out[r["item_id"]] = sum(1 for m in json.loads(r["messages"]) if m.get("role") == "learner")
        except (TypeError, ValueError):
            continue
    return out


def steps() -> list[dict]:
    data = content.load()
    exs = progress.all_exercises()
    states = progress.exercise_states()
    tutor = _tutor_questions()
    per: dict[str, dict] = {}
    for r in db.q("SELECT item_id, status, result, duration_s FROM attempts WHERE kind='practice' ORDER BY id"):
        s = per.setdefault(r["item_id"], {"checks": 0, "fails": 0, "solved_after": None, "seconds": None,
                                          "failures": Counter()})
        s["checks"] += 1
        if r["status"] == "passed":
            if s["solved_after"] is None:
                s["solved_after"] = s["fails"]
                s["seconds"] = r["duration_s"] or None
        else:
            s["fails"] += 1
            name = _failure(r["result"], r["status"])
            if name and s["solved_after"] is None:
                s["failures"][name] += 1
    out = []
    for item, s in per.items():
        ex = exs.get(item)
        if not ex or ex.get("generated"):
            continue
        st = states.get(item, {})
        solved = s["solved_after"] is not None
        fails = s["solved_after"] if solved else s["fails"]
        hints, revealed, asked = st.get("hints_used", 0) or 0, bool(st.get("revealed")), tutor.get(item, 0)
        topic = data["topics_by_id"].get(ex.get("topic"))
        top = s["failures"].most_common(1)
        top_name = top[0][0] if top else None
        if top_name and ex.get("mode") == "predict" and top_name.startswith("line "):
            top_name = "output " + top_name    # predict steps check the output line by line
        out.append({
            "id": item, "title": ex["title"], "difficulty": ex.get("difficulty", 1), "mode": ex.get("mode", "function"),
            "topic": ex.get("topic"), "chapter": topic["title"] if topic else "Module test",
            "module": topic["track"] if topic else ex.get("module"),
            "checks": s["checks"], "fails": fails, "solved": solved, "first_try": solved and fails == 0,
            "hints": hints, "hint_count": len(ex.get("hints", [])), "revealed": revealed, "tutor": asked,
            "seconds": s["seconds"], "top_failure": top_name, "top_failure_n": top[0][1] if top else 0,
            "trouble": fails * TROUBLE["fail"] + hints * TROUBLE["hint"] + revealed * TROUBLE["revealed"]
                       + asked * TROUBLE["tutor"] + (0 if solved else TROUBLE["unsolved"]),
        })
    out.sort(key=lambda x: (-x["trouble"], -x["fails"], x["title"]))
    return out


def chapters(rows: list[dict]) -> list[dict]:
    data = content.load()
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["topic"] or "exam", []).append(r)
    out = []
    for t in data["topics"]:
        rs = by.get(t["id"])
        if not rs:
            continue
        solved = [r for r in rs if r["solved"]]
        n = max(1, len(solved))
        out.append({"id": t["id"], "title": t["title"], "module": t["track"], "tried": len(rs), "solved": len(solved),
                    "first_try": round(sum(r["first_try"] for r in solved) / n, 2) if solved else None,
                    "fails_per_solve": round(sum(r["fails"] for r in solved) / n, 2) if solved else None,
                    "hints_per_solve": round(sum(r["hints"] for r in solved) / n, 2) if solved else None,
                    "revealed": sum(r["revealed"] for r in rs),
                    "trouble": round(sum(r["trouble"] for r in rs) / len(rs), 2)})
    out.sort(key=lambda c: -c["trouble"])
    return out


def report() -> dict:
    rows = steps()
    solved = [r for r in rows if r["solved"]]
    n = max(1, len(solved))
    totals = {"tried": len(rows), "solved": len(solved), "checks": sum(r["checks"] for r in rows),
              "fails_per_solve": round(sum(r["fails"] for r in solved) / n, 2) if solved else None,
              "hints_per_solve": round(sum(r["hints"] for r in solved) / n, 2) if solved else None,
              "first_try": round(sum(r["first_try"] for r in solved) / n, 2) if solved else None,
              "revealed": sum(r["revealed"] for r in rows)}
    return {"steps": rows, "chapters": chapters(rows), "totals": totals, "weights": TROUBLE}
