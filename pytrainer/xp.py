"""XP and levels, worked out from your history (nothing to farm, nothing lost on a reinstall).

XP rewards the work that teaches: solving steps (more for harder ones, a bonus for a clean first
try, half when you'd looked at the solution), passing reviews, clearing chapters, shipping projects
and labs, earning achievements, and showing up on a day. Reaching level n takes 50·n·(n−1) XP, so
early levels come quickly and later ones take a while; the whole course is worth about 25 levels.
"""

from __future__ import annotations

import math

from . import achievements, content, db, progress

STEP = {1: 10, 2: 20, 3: 30}
CLEAN_BONUS = 5
REVIEW = 5
CHAPTER = 50
PROJECT = 150
CHAPTER_PROJECT = 60
CAPSTONE = 300
LAB = 80
ACHIEVEMENT = 25
ACTIVE_DAY = 10
DRILL_SOLVE = 2
INTERVIEW = 30
EXPLAINED = 10

TITLES = [(1, "Beginner"), (5, "Apprentice"), (10, "Practitioner"), (15, "Engineer"), (20, "Senior engineer"),
          (25, "Staff engineer")]


def _n(sql: str) -> int:
    row = db.q1(sql)
    return int(row[0] or 0) if row else 0


def breakdown() -> dict[str, int]:
    """XP per source. The total is their sum."""
    data = content.load()
    exs = progress.all_exercises()
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    steps = 0
    for s in states.values():
        ex = exs.get(s["exercise_id"])
        if s["status"] != "solved" or not ex:
            continue
        base = STEP.get(ex["difficulty"], 10)
        if s.get("revealed"):
            base //= 2
        elif s["first_try"] and not s.get("hints_used"):
            base += CLEAN_BONUS
        steps += base
    passed = {r["project_id"] for r in db.q(
        "SELECT DISTINCT project_id FROM submissions WHERE json_extract(result, '$.status')='passed'")}
    portfolio = {p["id"] for p in data["projects"]}
    minis = {m["id"] for m in data["minis"]}
    projects = sum(CAPSTONE if pid == "capstone" else PROJECT if pid in portfolio else
                   CHAPTER_PROJECT if pid in minis else 0 for pid in passed)
    return {
        "steps": steps,
        "reviews": REVIEW * _n("SELECT COUNT(*) FROM attempts WHERE kind='review' AND status='passed'"),
        "chapters": CHAPTER * sum(1 for t in tp.values() if t["cleared"]),
        "projects": projects,
        "labs": LAB * _n("SELECT COUNT(*) FROM lab_state WHERE done=1"),
        "achievements": ACHIEVEMENT * len(achievements.unlocked()),
        "days": ACTIVE_DAY * _n("SELECT COUNT(*) FROM activity WHERE seconds >= 600 OR solved > 0"),
        "practice": (DRILL_SOLVE * _n("SELECT COALESCE(SUM(solved), 0) FROM drills")
                     + INTERVIEW * _n("SELECT COUNT(*) FROM interviews WHERE result IS NOT NULL")
                     + EXPLAINED * _n("SELECT COUNT(*) FROM explanations WHERE json_extract(result, '$.score') >= 4")),
    }


def threshold(level: int) -> int:
    """Total XP needed to reach `level` (level 1 needs 0)."""
    return 50 * level * (level - 1)


def level_for(total: int) -> int:
    # Solve 50·n·(n−1) <= total for the largest n, then guard against float rounding.
    n = max(1, int((1 + math.sqrt(1 + total / 12.5)) / 2))
    while threshold(n + 1) <= total:
        n += 1
    while n > 1 and threshold(n) > total:
        n -= 1
    return n


def title(level: int) -> str:
    return [t for lv, t in TITLES if level >= lv][-1]


def summary(total: int | None = None) -> dict:
    total = sum(breakdown().values()) if total is None else total
    lv = level_for(total)
    lo, hi = threshold(lv), threshold(lv + 1)
    return {"total": total, "level": lv, "title": title(lv), "into_level": total - lo, "level_size": hi - lo,
            "next_title": next((t for need, t in TITLES if need > lv), None)}


def baseline() -> dict:
    """The summary for the app's state, starting the "gained" count on a learner's first visit."""
    info = summary()
    if "xp_seen" not in db.settings():
        db.set_setting("xp_seen", info["total"])
    return info


def gained() -> dict | None:
    """XP earned since the last time this was asked. The very first call only sets the baseline, so an
    existing learner isn't greeted with their whole history as one gain."""
    total = sum(breakdown().values())
    seen = db.settings().get("xp_seen")
    if seen != total:
        db.set_setting("xp_seen", total)
    if seen is None or total <= seen:
        return None
    before, after = level_for(seen), level_for(total)
    return {"gained": total - seen, **summary(total), "level_up": after > before}
