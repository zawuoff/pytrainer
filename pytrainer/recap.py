"""The weekly recap: one card per Monday-to-Sunday week, compared with the week before.

Everything comes from what's already recorded (activity, attempts, solves, submissions, labs,
achievements), so any past week can be recapped, not just the last one.
"""

from __future__ import annotations

from datetime import date, timedelta

from . import achievements, content, course, db, progress, xp

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _numbers(start: date) -> dict:
    lo, hi = start.isoformat(), (start + timedelta(days=7)).isoformat()
    act = {r["day"]: r for r in db.q("SELECT * FROM activity WHERE day >= ? AND day < ?", (lo, hi))}
    days = []
    for i in range(7):
        d = (start + timedelta(days=i)).isoformat()
        r = act.get(d)
        days.append({"day": d, "name": DAY_NAMES[i], "minutes": round((r["seconds"] if r else 0) / 60),
                     "solved": r["solved"] if r else 0,
                     "active": bool(r and (r["seconds"] >= 600 or r["solved"] > 0))})
    attempts = db.q("SELECT item_id, kind, status FROM attempts WHERE created_at >= ? AND created_at < ?", (lo, hi))
    solved = db.q("SELECT exercise_id, first_try, hints_used, revealed FROM exercise_state "
                  "WHERE status='solved' AND solved_at >= ? AND solved_at < ?", (lo, hi))
    return {
        "lo": lo, "hi": hi, "days": days,
        "minutes": sum(d["minutes"] for d in days),
        "active_days": sum(d["active"] for d in days),
        "solved": len(solved),
        "clean": sum(1 for s in solved if s["first_try"] and not s["hints_used"] and not s["revealed"]),
        "solved_ids": [s["exercise_id"] for s in solved],
        "checks": sum(1 for a in attempts if a["kind"] in ("practice", "review")),
        "reviews": sum(1 for a in attempts if a["kind"] == "review" and a["status"] == "passed"),
        "attempts": attempts,
        "xp": xp.between(lo, hi),
    }


def _toughest(attempts: list, solved_ids: list, exs: dict) -> dict | None:
    """The step that took the most failed checks this week before you solved it."""
    fails: dict[str, int] = {}
    for a in attempts:
        if a["kind"] == "practice" and a["status"] != "passed":
            fails[a["item_id"]] = fails.get(a["item_id"], 0) + 1
    beaten = [(n, i) for i, n in fails.items() if i in solved_ids and i in exs and n >= 2]
    if not beaten:
        return None
    n, ex_id = max(beaten)
    return {"id": ex_id, "title": exs[ex_id]["title"], "fails": n}


def week(start: date | None = None) -> dict:
    """The recap for the week starting on `start` (a Monday; default: last week)."""
    today = date.today()
    start = week_start(start or (today - timedelta(days=7)))
    if start > week_start(today):
        raise ValueError("That week hasn't happened yet.")
    data = content.load()
    exs = progress.all_exercises()
    now, before = _numbers(start), _numbers(start - timedelta(days=7))
    chapters: dict[str, int] = {}
    for ex_id in now["solved_ids"]:
        topic = exs.get(ex_id, {}).get("topic")
        if topic in data["topics_by_id"]:
            chapters[topic] = chapters.get(topic, 0) + 1
    top = max(chapters.items(), key=lambda kv: kv[1]) if chapters else None
    projects = [r["project_id"] for r in db.q(
        "SELECT project_id, MIN(created_at) AS first FROM submissions WHERE json_extract(result, '$.status')='passed' "
        "GROUP BY project_id HAVING first >= ? AND first < ?", (now["lo"], now["hi"]))]
    labs = [r["lab_id"] for r in db.q("SELECT lab_id FROM lab_state WHERE done=1 AND done_at >= ? AND done_at < ?",
                                      (now["lo"], now["hi"]))]
    best_day = max(now["days"], key=lambda d: (d["minutes"], d["solved"]))
    titles = data["projects_by_id"]
    latest = start >= week_start(today - timedelta(days=7))
    return {
        "start": now["lo"], "end": (start + timedelta(days=6)).isoformat(),
        "is_current": start == week_start(today),
        "has_previous": bool(db.q1("SELECT 1 FROM activity WHERE day < ? LIMIT 1", (now["lo"],))),
        "empty": not (now["minutes"] or now["solved"] or now["checks"] or projects or labs),
        "days": now["days"],
        "minutes": now["minutes"], "active_days": now["active_days"], "solved": now["solved"],
        "clean": now["clean"], "reviews": now["reviews"], "checks": now["checks"], "xp": now["xp"],
        "previous": {k: before[k] for k in ("minutes", "solved", "reviews", "active_days", "xp")},
        "best_day": best_day if best_day["minutes"] or best_day["solved"] else None,
        "top_chapter": {"id": top[0], "title": data["topics_by_id"][top[0]]["title"], "solved": top[1]} if top else None,
        "toughest": _toughest(now["attempts"], now["solved_ids"], exs),
        "projects": [{"id": p, "title": titles[p]["title"]} for p in projects if p in titles],
        "labs": [{"id": lab, "title": data["labs_by_id"][lab]["title"]} for lab in labs if lab in data["labs_by_id"]],
        "achievements": achievements.unlocked_between(now["lo"], now["hi"]),
        "streak": progress.streak(),
        "level": xp.summary(),
        "next": {"reviews_due": len(progress.due_reviews()), "continue": course.continue_point()} if latest else None,
    }


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def banner() -> dict:
    """For Home: last week's recap is worth showing early in the week when there was something in it."""
    today = date.today()
    start = week_start(today - timedelta(days=7))
    end = start + timedelta(days=7)
    busy = db.q1("SELECT 1 FROM activity WHERE day >= ? AND day < ? AND (seconds > 0 OR solved > 0 OR checks > 0) "
                 "LIMIT 1", (start.isoformat(), end.isoformat()))
    return {"week": start.isoformat(), "ready": bool(busy) and today.weekday() <= 2}


def text(r: dict) -> str:
    """The recap as plain text, for pasting into a chat or a journal."""
    lines = [f"PyTrainer, week of {r['start']}",
             f"{r['minutes']} min over {_plural(r['active_days'], 'day')} · {_plural(r['solved'], 'step')} solved"
             f" ({r['clean']} on a clean first try) · {_plural(r['reviews'], 'review')} · +{r['xp']} XP",
             f"Level {r['level']['level']} ({r['level']['title']}) · {r['streak']['current']}-day streak"]
    if r["top_chapter"]:
        lines.append(f"Most practised: {r['top_chapter']['title']} ({_plural(r['top_chapter']['solved'], 'step')})")
    if r["toughest"]:
        lines.append(f"Toughest win: {r['toughest']['title']} (after {r['toughest']['fails']} failed checks)")
    for p in r["projects"]:
        lines.append(f"Shipped: {p['title']}")
    for lab in r["labs"]:
        lines.append(f"Lab done: {lab['title']}")
    if r["achievements"]:
        lines.append("Achievements: " + ", ".join(a["title"] for a in r["achievements"]))
    return "\n".join(lines)

