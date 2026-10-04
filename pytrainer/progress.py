"""Learning state: mastery, unlocking, spaced review, daily plan and stats."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from . import content, db, srs

WEIGHT = {0: 0, 1: 1, 2: 2, 3: 3}
CLEAR_THRESHOLD = 0.6


def all_exercises() -> dict:
    """Built-in exercises plus AI-generated ones."""
    data = content.load()
    out = dict(data["exercises"])
    for row in db.q("SELECT data FROM custom_exercises"):
        ex = json.loads(row["data"])
        out[ex["id"]] = ex
    return out


def passed_projects() -> set[str]:
    return {r["project_id"] for r in db.q("SELECT DISTINCT project_id FROM submissions "
                                           "WHERE json_extract(result, '$.status')='passed'")}


def exercise_states() -> dict[str, dict]:
    return {r["exercise_id"]: dict(r) for r in db.q("SELECT * FROM exercise_state")}


def placed_topics() -> set[str]:
    return {r["topic_id"] for r in db.q("SELECT topic_id FROM topic_state WHERE placed=1")}


def topic_progress(states: dict | None = None) -> dict[str, dict]:
    data = content.load()
    states = states if states is not None else exercise_states()
    placed = placed_topics()
    custom_by_topic: dict[str, list] = {}
    for row in db.q("SELECT id, topic, data FROM custom_exercises"):
        custom_by_topic.setdefault(row["topic"], []).append(json.loads(row["data"]))
    out = {}
    read = {r["topic_id"] for r in db.q("SELECT topic_id FROM lesson_state")}
    projects_passed = passed_projects()

    def earned(e):  # solved on your own (a revealed solution only counts after you redo it later)
        st = states.get(e["id"], {})
        return st.get("status") == "solved" and not st.get("revealed")

    for t in data["topics"]:
        all_exs = [data["exercises"][e] for e in t["exercise_ids"]]
        # Extra steps (test writing, bug hunts...) are practice on top of the path: they never
        # count toward mastery, so adding new ones can't un-clear a chapter.
        path = [e for e in all_exs if not e.get("extra")]
        starters = [e for e in path if e["difficulty"] == 0]
        exs = [e for e in path if e["difficulty"] >= 1]
        total_w = sum(WEIGHT[e["difficulty"]] for e in exs)
        solved = [e for e in exs if earned(e)]
        solved_w = sum(WEIGHT[e["difficulty"]] for e in solved)
        has_hard = any(e["difficulty"] == 3 for e in exs)
        hard_solved = any(e["difficulty"] == 3 for e in solved) or not has_hard
        mastery = solved_w / total_w if total_w else 0
        extra = sum(1 for e in custom_by_topic.get(t["id"], []) if earned(e))
        steps_done = mastery >= CLEAR_THRESHOLD and hard_solved
        mini = data["minis_by_chapter"].get(t["id"])
        project_done = mini is None or mini["id"] in projects_passed
        # A chapter is complete when its steps are mastered AND its chapter project passes
        # (or when the placement test / module test showed you already know it).
        earned_all = steps_done and project_done
        cleared = earned_all or t["id"] in placed
        out[t["id"]] = {
            "steps_done": steps_done,
            "project": ({"id": mini["id"], "title": mini["title"], "passed": mini["id"] in projects_passed}
                        if mini else None),
            "mastery": round(mastery, 3),
            "solved": len(solved),
            "total": len(exs),
            "starters_solved": sum(1 for e in starters if earned(e)),
            "starters_total": len(starters),
            "lesson_read": t["id"] in read,
            "has_lesson": bool(t.get("lesson")),
            "extra_solved": extra,
            "cleared": cleared,
            "earned": earned_all,
            "placed": t["id"] in placed,
            "attempted": any(states.get(e["id"], {}).get("attempts", 0) for e in all_exs),
            # The Library shows a chapter's reference card only once its lesson is finished:
            # the steps are mastered, or the chapter was tested out of, or it was marked read.
            "library_unlocked": steps_done or cleared or t["id"] in read,
        }
    for t in data["topics"]:
        out[t["id"]]["unlocked"] = all(out.get(r, {}).get("cleared") for r in t["requires"])
    return out


def combo_status(tp: dict, states: dict) -> list[dict]:
    data = content.load()
    res = []
    for c in data["combos"]:
        st = states.get(c["id"], {})
        res.append({"id": c["id"], "title": c["title"], "difficulty": c["difficulty"],
                    "topics": c.get("topics", []),
                    "unlocked": all(tp.get(t, {}).get("cleared") for t in c.get("topics", [])),
                    "status": st.get("status", "new")})
    return res


def record_attempt(ex: dict, files: dict, result: dict, kind: str, duration_s: int) -> dict:
    """Store an attempt and update exercise state + spaced repetition. Returns new state."""
    passed = result["status"] == "passed"
    db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, duration_s, result, created_at) "
          "VALUES(?,?,?,?,?,?,?,?,?)",
          (ex["id"], kind, json.dumps(files), result["status"], result["passed"], result["total"],
           int(duration_s), json.dumps(result), db.now()))
    st = get_state(ex["id"])
    was_solved = st["status"] == "solved"
    newly_solved = False
    st["attempts"] += 1
    st["best_passed"] = max(st["best_passed"], result["passed"])
    st["total"] = result["total"]
    st.setdefault("revealed", 0)
    st.setdefault("hints_used", 0)
    if kind == "review" and was_solved:
        rating = srs.on_review(st, passed, int(duration_s or 0))
        if rating:
            st["review_count"] += 1
        if rating == srs.AGAIN:
            st["lapses"] += 1
        if passed:
            st["revealed"] = 0  # rebuilt from memory: now it's genuinely yours
    elif passed and not was_solved:
        newly_solved = True
        st["status"] = "solved"
        st["solved_at"] = db.now()
        st["first_try"] = 1 if st["attempts"] == 1 else 0
        srs.on_first_solve(st)  # struggle (hints, retries, a revealed solution) means a sooner review
    elif not was_solved:
        st["status"] = "attempted"
    save_state(st)
    db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES(?, 0, ?, 1) ON CONFLICT(day) DO UPDATE SET "
          "solved = solved + excluded.solved, checks = checks + 1", (db.today(), 1 if newly_solved else 0))
    st["newly_solved"] = newly_solved
    return st


def save_state(st: dict) -> None:
    db.ex("INSERT OR REPLACE INTO exercise_state(exercise_id, status, attempts, first_try, solved_at, best_passed, "
          "total, next_review, interval_days, review_count, lapses, revealed, hints_used, stability, difficulty, "
          "last_review) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
          (st["exercise_id"], st["status"], st["attempts"], st["first_try"], st["solved_at"], st["best_passed"],
           st["total"], st["next_review"], st["interval_days"], st["review_count"], st["lapses"],
           st.get("revealed", 0), st.get("hints_used", 0), st.get("stability"), st.get("difficulty"),
           st.get("last_review")))


def get_state(ex_id: str) -> dict:
    row = db.q1("SELECT * FROM exercise_state WHERE exercise_id=?", (ex_id,))
    return dict(row) if row else {"exercise_id": ex_id, "status": "new", "attempts": 0, "first_try": 0,
                                  "solved_at": None, "best_passed": 0, "total": 0, "next_review": None,
                                  "interval_days": 0, "review_count": 0, "lapses": 0, "revealed": 0,
                                  "hints_used": 0, "stability": None, "difficulty": None, "last_review": None}


def due_reviews(limit: int | None = None) -> list[dict]:
    exs = all_exercises()
    rows = db.q("SELECT * FROM exercise_state WHERE status='solved' AND next_review IS NOT NULL "
                "AND next_review <= ? ORDER BY next_review, lapses DESC", (db.today(),))
    out = []
    for r in rows:
        ex = exs.get(r["exercise_id"])
        if ex:
            out.append({"id": ex["id"], "title": ex["title"], "topic": ex.get("topic"),
                        "difficulty": ex["difficulty"], "due": r["next_review"], "lapses": r["lapses"]})
    return out[:limit] if limit else out


def add_seconds(seconds: int) -> None:
    seconds = max(0, min(int(seconds), 120))
    db.ex("INSERT INTO activity(day, seconds) VALUES(?, ?) ON CONFLICT(day) DO UPDATE SET "
          "seconds = seconds + excluded.seconds", (db.today(), seconds))


def streak() -> dict:
    rows = {r["day"]: r for r in db.q("SELECT * FROM activity")}

    def active(d):
        r = rows.get(d.isoformat())
        return bool(r and (r["seconds"] >= 600 or r["solved"] > 0))

    day = date.today()
    current = 0
    if not active(day):
        day -= timedelta(days=1)
    while active(day):
        current += 1
        day -= timedelta(days=1)
    best = run = 0
    if rows:
        d = date.fromisoformat(min(rows))
        while d <= date.today():
            run = run + 1 if active(d) else 0
            best = max(best, run)
            d += timedelta(days=1)
    return {"current": current, "best": best, "today_active": active(date.today())}


def heatmap(days: int = 140) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows = {r["day"]: r for r in db.q("SELECT * FROM activity WHERE day >= ?", (start.isoformat(),))}
    out = []
    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        r = rows.get(d)
        out.append({"day": d, "minutes": round((r["seconds"] if r else 0) / 60),
                    "solved": r["solved"] if r else 0, "checks": r["checks"] if r else 0})
    return out


def today_plan(tp: dict, states: dict) -> list[dict]:
    """A focused 1-2h session: reviews first, then the frontier, then a combo, then a project."""
    data = content.load()
    plan = []
    for r in due_reviews(3):
        plan.append({"kind": "review", "id": r["id"], "title": r["title"], "topic": r["topic"],
                     "why": "Spaced review - rebuild it from memory"})
    # topics you tested out of come after genuinely new ones
    frontier = ([t for t in data["topics"] if tp[t["id"]]["unlocked"] and not tp[t["id"]]["cleared"]]
                + [t for t in data["topics"] if tp[t["id"]]["placed"] and not tp[t["id"]]["earned"]])
    picked = 0
    for t in frontier:
        if t.get("lesson") and not tp[t["id"]]["lesson_read"]:
            plan.append({"kind": "lesson", "id": t["id"], "title": f"Learn: {t['title']}", "topic": t["id"],
                         "why": "Read the lesson and run the examples (about 10 min)"})
            picked += 1
        for eid in t["exercise_ids"]:
            st = states.get(eid, {})
            if st.get("status") != "solved" or st.get("revealed"):
                ex = data["exercises"][eid]
                why = (f"Starter step in {t['title']}" if ex["difficulty"] == 0 else f"Next up in {t['title']}")
                plan.append({"kind": "exercise", "id": eid, "title": ex["title"], "topic": t["id"],
                             "difficulty": ex["difficulty"], "why": why})
                picked += 1
                if picked >= 5:
                    break
        if picked >= 5:
            break
    for c in combo_status(tp, states):
        if c["unlocked"] and c["status"] != "solved":
            plan.append({"kind": "exercise", "id": c["id"], "title": c["title"], "topic": "combo",
                         "difficulty": c["difficulty"], "why": "Combine what you know"})
            break
    done = {r["project_id"] for r in db.q("SELECT project_id, result FROM submissions")
            if json.loads(r["result"]).get("status") == "passed"}
    for p in data["projects"]:
        if p["id"] not in done and all(tp.get(t, {}).get("cleared") for t in p["requires"]):
            plan.append({"kind": "project", "id": p["id"], "title": p["title"],
                         "why": f"Build something real ({p['estimated_hours']}h)"})
            break
    return plan


def weak_spots(limit: int = 6) -> list[str]:
    exs = all_exercises()
    rows = db.q("SELECT item_id, result FROM attempts WHERE status != 'passed' "
                "ORDER BY id DESC LIMIT 60")
    notes = []
    for r in rows:
        ex = exs.get(r["item_id"])
        if not ex:
            continue
        res = json.loads(r["result"] or "{}")
        failed = [t["name"] for t in res.get("tests", []) if not t["passed"]][:2]
        notes.append(f"{ex['title']} ({ex.get('topic')}): " + (", ".join(failed) or res.get("status", "")))
    seen, out = set(), []
    for n in notes:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out[:limit]


def summary() -> dict:
    data = content.load()
    states = exercise_states()
    tp = topic_progress(states)
    rows = db.q("SELECT kind, status, COUNT(*) n FROM attempts GROUP BY kind, status")
    attempts_total = sum(r["n"] for r in rows)
    passes = sum(r["n"] for r in rows if r["status"] == "passed")
    solved = [s for s in states.values() if s["status"] == "solved"]
    first_try = sum(1 for s in solved if s["first_try"])
    today = db.q1("SELECT * FROM activity WHERE day=?", (db.today(),))
    week_start = (date.today() - timedelta(days=6)).isoformat()
    week = db.q1("SELECT COALESCE(SUM(seconds),0) s, COALESCE(SUM(solved),0) n FROM activity WHERE day >= ?",
                 (week_start,))
    cleared = [t for t in data["topics"] if tp[t["id"]]["cleared"]]
    qual = [r["q"] for r in db.q("SELECT json_extract(result, '$.quality.overall') q FROM attempts "
                                 "WHERE status='passed' AND q IS NOT NULL ORDER BY id DESC LIMIT 20")]
    return {
        "avg_quality": round(sum(qual) / len(qual), 1) if qual else None,
        "solved": len(solved),
        "total_exercises": len(data["exercises"]),
        "attempts": attempts_total,
        "pass_rate": round(passes / attempts_total, 3) if attempts_total else None,
        "first_try_rate": round(first_try / len(solved), 3) if solved else None,
        "today_minutes": round((today["seconds"] if today else 0) / 60),
        "today_solved": today["solved"] if today else 0,
        "week_minutes": round(week["s"] / 60),
        "week_solved": week["n"],
        "topics_cleared": len(cleared),
        "topics_total": len(data["topics"]),
        "reviews_due": len(due_reviews()),
        "streak": streak(),
    }


def coach_snapshot() -> dict:
    data = content.load()
    tp = topic_progress()
    placement = db.q1("SELECT report FROM placement WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1")
    return {
        "date": db.today(),
        "summary": summary(),
        "topics": {t["id"]: {k: tp[t["id"]][k] for k in ("mastery", "cleared", "solved", "total")}
                   for t in data["topics"]},
        "recent_failures": weak_spots(10),
        "projects_passed": [r["project_id"] for r in db.q("SELECT DISTINCT project_id FROM submissions "
                                                          "WHERE json_extract(result, '$.status')='passed'")],
        "labs_done": [r["lab_id"] for r in db.q("SELECT lab_id FROM lab_state WHERE done=1")],
        "placement": json.loads(placement["report"]) if placement and placement["report"] else None,
        "last_14_days": [{k: d[k] for k in ("day", "minutes", "solved")} for d in heatmap(14)],
    }


def level_label(tp: dict) -> str:
    data = content.load()
    by_track = {}
    for t in data["topics"]:
        by_track.setdefault(t["track"], []).append(tp[t["id"]]["cleared"])
    if all(by_track.get("ai-ready", [False])):
        return "AI-ready"
    if all(by_track.get("practical", [False])):
        return "Practical"
    if all(by_track.get("fundamentals", [False])):
        return "Fundamentals cleared"
    return "Building fundamentals"


def parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)
