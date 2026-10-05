"""Achievements: milestones earned from what you actually did, kept once earned.

Every achievement reads one number from `stats()` and unlocks when it reaches its target. They are
checked after the actions that can earn them (see server.REWARDING), and an unlock is stored with
its date, so it stays even if the rules change later. Secret ones show as "???" until earned.
"""

from __future__ import annotations

from datetime import date, datetime

from . import content, db, progress

# (id, group, title, how to earn it, stat, target, secret)
ACHIEVEMENTS = [
    ("first-step", "Practice", "First steps", "Solve your first step.", "solved", 1, False),
    ("ten-steps", "Practice", "Warming up", "Solve 10 steps.", "solved", 10, False),
    ("fifty-steps", "Practice", "Half a century", "Solve 50 steps.", "solved", 50, False),
    ("hundred-steps", "Practice", "Centurion", "Solve 100 steps.", "solved", 100, False),
    ("three-hundred-steps", "Practice", "Unstoppable", "Solve 300 steps.", "solved", 300, False),
    ("clean-sheet", "Practice", "Clean sheet", "Solve 10 steps on the first try with no hints.", "clean", 10, False),
    ("deep-end", "Practice", "Deep end", "Solve 10 hard steps.", "hard", 10, False),
    ("first-chapter", "Course", "Chapter one", "Clear your first chapter.", "chapters", 1, False),
    ("ten-chapters", "Course", "Bookworm", "Clear 10 chapters.", "chapters", 10, False),
    ("first-module", "Course", "Module complete", "Clear every chapter in one module.", "modules", 1, False),
    ("all-chapters", "Course", "The whole course", "Clear every chapter.", "all_chapters", 1, False),
    ("ten-reviews", "Memory", "It stuck", "Pass 10 reviews.", "reviews", 10, False),
    ("hundred-reviews", "Memory", "Long memory", "Pass 100 reviews.", "reviews", 100, False),
    ("streak-3", "Habit", "Three in a row", "Practise 3 days in a row.", "best_streak", 3, False),
    ("streak-7", "Habit", "Week streak", "Practise 7 days in a row.", "best_streak", 7, False),
    ("streak-30", "Habit", "Month streak", "Practise 30 days in a row.", "best_streak", 30, False),
    ("ten-hours", "Habit", "Ten hours in", "Practise for 10 hours in total.", "hours", 10, False),
    ("night-owl", "Habit", "Night owl", "Solve a step between midnight and 5 am.", "night", 1, True),
    ("comeback", "Habit", "Welcome back", "Come back after a break of a week or more.", "comebacks", 1, True),
    ("bug-hunter", "Extra practice", "Bug hunter", "Fix 5 bug hunts.", "bughunt", 5, False),
    ("tidy", "Extra practice", "Tidy coder", "Finish 5 refactor challenges.", "refactor", 5, False),
    ("puzzler", "Extra practice", "Puzzler", "Solve 5 Parsons problems.", "parsons", 5, False),
    ("detective", "Extra practice", "Detective", "Solve 5 traceback drills.", "traceback", 5, False),
    ("test-pilot", "Extra practice", "Test pilot", "Solve 5 write-the-tests steps.", "tests", 5, False),
    ("speedster", "Extra practice", "Speedster", "Solve 10 problems in one speed drill.", "drill_best", 10, False),
    ("explainer", "Extra practice", "Explainer", "Get 4 or 5 out of 5 on 5 explain-it-back answers.", "explained", 5, False),
    ("first-project", "Building", "Shipped", "Pass your first project.", "projects", 1, False),
    ("five-projects", "Building", "Portfolio", "Pass 5 AI-app projects.", "portfolio", 5, False),
    ("capstone", "Building", "Docs Assistant", "Pass the capstone.", "capstone", 1, False),
    ("three-labs", "Building", "Terminal regular", "Finish 3 terminal labs.", "labs", 3, False),
    ("interview", "Building", "Hired (in practice)", "Pass every check in a practice interview.", "interviews_passed", 1, False),
    ("leaderboard", "Building", "Top of the board", "Score 80 or more on the eval leaderboard's held-out set.", "leaderboard", 80, False),
]

GROUPS = ["Practice", "Course", "Memory", "Habit", "Extra practice", "Building"]


def _count(sql: str, params: tuple = ()) -> int:
    row = db.q1(sql, params)
    return int(row[0] or 0) if row else 0


def _comebacks(days: list[str]) -> int:
    ordered = [date.fromisoformat(d) for d in sorted(days)]
    return sum(1 for a, b in zip(ordered, ordered[1:]) if (b - a).days >= 8)


def stats() -> dict:
    data = content.load()
    exs = progress.all_exercises()
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    solved = [s for s in states.values() if s["status"] == "solved" and s["exercise_id"] in exs]
    kinds: dict[str, int] = {}
    for s in solved:
        ex = exs[s["exercise_id"]]
        if ex.get("extra"):
            k = ex.get("kind") or ex.get("mode")
            kinds[k] = kinds.get(k, 0) + 1
    by_module: dict[str, list[bool]] = {}
    for t in data["topics"]:
        by_module.setdefault(t["track"], []).append(tp[t["id"]]["cleared"])
    passed_projects = {r["project_id"] for r in db.q(
        "SELECT DISTINCT project_id FROM submissions WHERE json_extract(result, '$.status')='passed'")}
    portfolio = {p["id"] for p in data["projects"]}
    active_days = [r["day"] for r in db.q("SELECT day FROM activity WHERE seconds >= 600 OR solved > 0")]
    night = 0
    for r in db.q("SELECT created_at FROM attempts WHERE status='passed' AND kind IN ('practice','review')"):
        try:
            night += datetime.fromisoformat(r["created_at"]).hour < 5
        except ValueError:
            pass
    return {
        "solved": len(solved),
        "clean": sum(1 for s in solved if s["first_try"] and not s.get("hints_used") and not s.get("revealed")),
        "hard": sum(1 for s in solved if exs[s["exercise_id"]]["difficulty"] >= 3),
        "chapters": sum(1 for t in tp.values() if t["cleared"]),
        "all_chapters": int(all(t["cleared"] for t in tp.values())),
        "modules": sum(1 for v in by_module.values() if v and all(v)),
        "reviews": _count("SELECT COUNT(*) FROM attempts WHERE kind='review' AND status='passed'"),
        "best_streak": progress.streak()["best"],
        "hours": _count("SELECT COALESCE(SUM(seconds), 0) FROM activity") // 3600,
        "night": night,
        "comebacks": _comebacks(active_days),
        "bughunt": kinds.get("bughunt", 0),
        "refactor": kinds.get("refactor", 0),
        "parsons": kinds.get("parsons", 0),
        "traceback": kinds.get("traceback", 0),
        "tests": kinds.get("tests", 0),
        "drill_best": _count("SELECT COALESCE(MAX(solved), 0) FROM drills"),
        "explained": _count("SELECT COUNT(*) FROM explanations WHERE json_extract(result, '$.score') >= 4"),
        "projects": len(passed_projects),
        "portfolio": len(passed_projects & portfolio),
        "capstone": int("capstone" in passed_projects),
        "labs": _count("SELECT COUNT(*) FROM lab_state WHERE done=1"),
        "interviews_passed": _count("SELECT COUNT(*) FROM interviews WHERE json_extract(result, '$.status')='passed'"),
        "leaderboard": _count("SELECT COALESCE(MAX(test), 0) FROM leaderboard_runs"),
    }


def _public(a: tuple, unlocked_at: str | None, value: int | None = None) -> dict:
    aid, group, title, text, _stat, target, secret = a
    hide = secret and not unlocked_at
    out = {"id": aid, "group": group, "title": "???" if hide else title,
           "text": "A secret achievement. Keep practising." if hide else text,
           "target": target, "unlocked_at": unlocked_at, "secret": secret}
    if value is not None and not hide:
        out["value"] = min(value, target)
    return out


def unlocked() -> dict[str, str]:
    return {r["id"]: r["unlocked_at"] for r in db.q("SELECT id, unlocked_at FROM achievements")}


def check() -> list[dict]:
    """Unlock everything newly earned. Returns the new ones (usually none)."""
    have = unlocked()
    if len(have) == len(ACHIEVEMENTS):
        return []
    values = stats()
    new = []
    for a in ACHIEVEMENTS:
        if a[0] not in have and values.get(a[4], 0) >= a[5]:
            when = db.now()
            db.ex("INSERT OR IGNORE INTO achievements(id, unlocked_at) VALUES(?, ?)", (a[0], when))
            new.append(_public(a, when))
    return new


def overview() -> dict:
    have = unlocked()
    values = stats()
    items = [_public(a, have.get(a[0]), values.get(a[4], 0)) for a in ACHIEVEMENTS]
    recent = sorted((i for i in items if i["unlocked_at"]), key=lambda i: i["unlocked_at"], reverse=True)
    return {"groups": GROUPS, "items": items, "unlocked": len(have), "total": len(ACHIEVEMENTS),
            "recent": recent[:3]}


def unlocked_between(start: str, end: str) -> list[dict]:
    """Achievements unlocked in [start, end) (ISO dates), for the weekly recap."""
    by_id = {a[0]: a for a in ACHIEVEMENTS}
    rows = db.q("SELECT id, unlocked_at FROM achievements WHERE unlocked_at >= ? AND unlocked_at < ? "
                "ORDER BY unlocked_at", (start, end))
    return [_public(by_id[r["id"]], r["unlocked_at"]) for r in rows if r["id"] in by_id]

