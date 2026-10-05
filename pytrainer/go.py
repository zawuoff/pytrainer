"""On the go: practice for a phone, where typing code is a pain but reading it isn't.

A session mixes what works with a thumb, all from chapters you've reached:
- predict-the-output steps (type what a short program prints),
- read-the-traceback drills (tap the line you'd change),
- flashcards from your Library cards (syntax on the front, meaning and example on the back),
- the notes of the chapter you're on, to read.
Steps are graded by the normal check, so they count like anywhere else. Unsolved ones come first;
solved ones fill in as a refresher.
"""

from __future__ import annotations

import random

from . import content, course, library, progress

PREDICT = 6
TRACEBACK = 4
CARDS = 10


def _pick(exs: list[dict], states: dict, n: int, rng: random.Random) -> list[dict]:
    fresh = [e for e in exs if states.get(e["id"], {}).get("status") != "solved"]
    done = [e for e in exs if states.get(e["id"], {}).get("status") == "solved"]
    rng.shuffle(done)
    return (fresh + done)[:n]


def session(traceback_of, seed: int | None = None) -> dict:
    """`traceback_of(ex)` gives the real traceback of a drill's program (server caches it)."""
    rng = random.Random(seed)
    data = content.load()
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    reached = [t for t in data["topics"] if tp[t["id"]]["unlocked"] or tp[t["id"]]["attempted"] or tp[t["id"]]["cleared"]]
    reached_ids = {t["id"] for t in reached}
    in_order = [data["exercises"][e] for t in reached for e in t["exercise_ids"]]

    def item(ex: dict) -> dict:
        topic = data["topics_by_id"][ex["topic"]]
        out = content.public_exercise(ex) | {"status": states.get(ex["id"], {}).get("status", "new"),
                                             "chapter": topic["title"], "module": topic["track"]}
        if ex.get("mode") == "traceback":
            out["traceback"] = traceback_of(ex)
        return out

    predict = _pick([e for e in in_order if e.get("mode") == "predict"], states, PREDICT, rng)
    traceback = _pick([e for e in in_order if e.get("mode") == "traceback"], states, TRACEBACK, rng)

    unlocked = [t for t in data["topics"] if tp[t["id"]]["library_unlocked"]]
    boost = library.signals({t["id"] for t in unlocked})["boost"]
    pool = [(t, i, c) for t in unlocked for i, c in enumerate(t["reference"]["cards"])]
    rng.shuffle(pool)
    pool.sort(key=lambda x: -boost.get(x[0]["id"], 0) * rng.random())
    cards = [{"id": t["id"], "card": i, "chapter": t["title"], "module": t["track"], **c} for t, i, c in pool[:CARDS]]

    nxt = course.continue_point(states, tp)
    reading = None
    if nxt and nxt["topic"] in reached_ids:
        reading = {"id": nxt["topic"], "title": nxt["topic_title"], "read": tp[nxt["topic"]]["lesson_read"]}
    return {"predict": [item(e) for e in predict], "traceback": [item(e) for e in traceback], "cards": cards,
            "reading": reading, "reviews_due": len(progress.due_reviews())}
