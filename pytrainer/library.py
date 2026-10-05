"""The Library as a search engine: reference cards from the chapters you've finished.

Only unlocked chapters are ever sent (a locked chapter isn't listed, not even by title). Alongside
the cards the browser gets personal signals, so search can rank like a smart search engine while
still finding anything you've unlocked:

- `boost`: per chapter, 0..1, from what you opened in the Library lately, the chapters you've been
  practising (and failing) in, and the chapters the one you're working on builds on;
- `recent`: the cards you opened most recently, newest first;
- `working_on`: the chapters of your latest attempts.

Search itself runs in the browser (static/js/library.js) over these few hundred cards, so results
appear as you type.
"""

from __future__ import annotations

import math
from datetime import datetime

from . import content, db, progress

HALF_LIFE_DAYS = 7
RECENT = 8


def _age_days(stamp: str, now: datetime) -> float:
    try:
        return max(0.0, (now - datetime.fromisoformat(stamp)).total_seconds() / 86400)
    except (TypeError, ValueError):
        return 365.0


def _decay(days: float) -> float:
    return math.pow(0.5, days / HALF_LIFE_DAYS)


def record_open(topic_id: str, card: int | None) -> None:
    db.ex("INSERT INTO library_opens(topic_id, card, opened_at) VALUES(?,?,?)", (topic_id, card, db.now()))


def signals(unlocked: set[str]) -> dict:
    data = content.load()
    exs = progress.all_exercises()
    now = datetime.now()
    score: dict[str, float] = {}

    def add(topic: str | None, amount: float) -> None:
        if topic in unlocked:
            score[topic] = score.get(topic, 0.0) + amount

    opens = db.q("SELECT topic_id, card, opened_at FROM library_opens ORDER BY id DESC LIMIT 400")
    for r in opens:
        add(r["topic_id"], 1.0 * _decay(_age_days(r["opened_at"], now)))
    attempts = db.q("SELECT item_id, status, created_at FROM attempts WHERE kind IN ('practice','review') "
                    "ORDER BY id DESC LIMIT 200")
    working: list[str] = []
    for r in attempts:
        topic = exs.get(r["item_id"], {}).get("topic")
        if topic not in data["topics_by_id"]:
            continue
        weight = (1.5 if r["status"] != "passed" else 0.6) * _decay(_age_days(r["created_at"], now))
        add(topic, weight)
        if topic not in working and len(working) < 3:
            working.append(topic)
    # What you're working on builds on its prerequisites: the cards you most likely need to look up.
    for topic in working:
        for req in data["topics_by_id"][topic]["requires"]:
            add(req, 1.0)
    top = max(score.values(), default=0.0)
    boost = {t: round(v / top, 3) for t, v in score.items()} if top else {}
    recent, seen = [], set()
    for r in opens:
        key = (r["topic_id"], r["card"])
        if r["topic_id"] in unlocked and key not in seen:
            seen.add(key)
            recent.append({"id": r["topic_id"], "card": r["card"], "at": r["opened_at"]})
        if len(recent) >= RECENT:
            break
    return {"boost": boost, "recent": recent, "working_on": working}
