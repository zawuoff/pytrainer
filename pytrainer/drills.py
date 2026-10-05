"""Speed drills: timed rounds of easy steps you've already solved, for fluency.

Drill checks are graded like any check but never recorded as attempts and never touch the
review schedule: speed practice shouldn't change what your stats or reviews say you know.
Only the round's totals are kept, to show personal bests.
"""

from __future__ import annotations

import random

from . import content, db, progress

LENGTHS = (180, 300, 600)
MODES = ("function", "script")
MIN_POOL = 5


def pool(limit: int = 60) -> list[dict]:
    """Solved steps that are quick to rebuild (difficulty 0-1, code steps), shuffled."""
    states = progress.exercise_states()
    exs = progress.all_exercises()
    ids = [i for i, st in states.items() if st["status"] == "solved" and i in exs
           and exs[i].get("difficulty", 9) <= 1 and exs[i].get("mode", "function") in MODES
           and not exs[i].get("generated")]
    random.shuffle(ids)
    return [content.public_exercise(exs[i]) for i in ids[:limit]]


def finish(seconds: int, solved: int, skipped: int, best_streak: int) -> dict:
    if seconds not in LENGTHS:
        raise ValueError("unknown round length")
    best_before = best(seconds)
    db.ex("INSERT INTO drills(seconds, solved, skipped, best_streak, created_at) VALUES(?,?,?,?,?)",
          (seconds, max(0, int(solved)), max(0, int(skipped)), max(0, int(best_streak)), db.now()))
    return {"new_best": solved > best_before, "previous_best": best_before} | stats()


def best(seconds: int) -> int:
    row = db.q1("SELECT MAX(solved) AS m FROM drills WHERE seconds=?", (seconds,))
    return row["m"] or 0


def stats() -> dict:
    recent = [dict(r) for r in db.q("SELECT seconds, solved, skipped, best_streak, created_at FROM drills "
                                    "ORDER BY id DESC LIMIT 8")]
    return {"best": {str(s): best(s) for s in LENGTHS}, "recent": recent, "lengths": list(LENGTHS)}
