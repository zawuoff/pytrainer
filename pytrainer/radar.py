"""Weakness radar: patterns in what keeps going wrong, and a short session aimed at them.

Every failed check names what failed ("empty list returns zero", "input not modified") or how
the code broke (a KeyError, a timeout, a SyntaxError). Each failure is sorted into one pattern by
those words. Recent failures weigh more (half-life of two weeks). The session then picks steps
for the top patterns: ones you tried and haven't solved, solved ones you lapsed on or needed the
solution for, and extra steps (bug hunts, test writing...) about the same thing.
"""

from __future__ import annotations

import json
from datetime import datetime

from . import content, db, progress

HALF_LIFE_DAYS = 14
LOOKBACK = 400
SESSION_SIZE = 6

# (id, label, what it means, words in failing check names/messages, error types). First match wins.
PATTERNS = [
    ("syntax", "Code that doesn't run", "Syntax and indentation errors, or names that don't exist yet.",
     [], ["SyntaxError", "IndentationError", "NameError", "ImportError", "ModuleNotFoundError"]),
    ("slow", "Loops that never end", "Checks that ran out of time: a loop that doesn't finish, or waits for input.",
     [], []),
    ("empty", "Empty and missing input", "Empty lists and strings, None, missing fields and zero.",
     ["empty", "blank", "missing", "none", "no ", "zero", "whitespace only", "nothing"], []),
    ("boundaries", "Boundaries and off-by-one", "Exact limits, first and last items, ranges that stop one short or one too far.",
     ["exactly", "limit", "bound", "last", "first", "edge", "equal", "at least", "at most", "longer", "shorter",
      "too long", "budget", "max", "min", "off by"], ["IndexError"]),
    ("mutation", "Changing inputs by accident", "Lists or dicts that were modified, shared or aliased when a copy was needed.",
     ["not modified", "modified", "copy", "new list", "same object", "independent", "separate",
      "mutat", "shared", "own list"], []),
    ("errors", "Raising the right errors", "Rejecting bad input with the right exception, and not swallowing errors.",
     ["raise", "raises", "error", "invalid", "bad ", "refus", "reject", "unknown"], []),
    ("order", "Order and sorting", "Results in the wrong order, ties broken the wrong way, sort keys.",
     ["order", "sort", "tie", "rank", "reverse", "first appearance", "best first", "highest"], []),
    ("keys", "Missing keys and attributes", "Looking up keys, indexes or attributes that aren't there.",
     ["key"], ["KeyError", "AttributeError"]),
    ("types", "Types and conversions", "Strings vs numbers, ints vs floats, None where a value was expected.",
     ["int", "float", "number", "string", "type", "convert", "bool", "round"], ["TypeError", "ValueError"]),
    ("text", "Text details", "Case, spaces, punctuation and exact output format.",
     ["case", "space", "strip", "format", "print", "output", "newline", "punctuation", "line", "join", "text"], []),
]
LABELS = {p[0]: p[1] for p in PATTERNS}

# Words in an extra step's concepts or title that make it practice for a pattern.
PRACTICE = {
    "syntax": ["def", "if / elif", "return", "while", "try / except"],
    "slow": ["while", "break", "for loops", "return inside a loop", "agent loop"],
    "mutation": ["copies", "mutation", "mutable", "class vs instance", "setdefault"],
    "empty": ["empty", "missing data", "truthiness", "dict.get", "division by zero"],
    "boundaries": ["boundar", "off-by-one", "range", "negative index", "slicing", "overlap", "string length"],
    "errors": ["testing exceptions", "try/except", "raise", "validation", "error handling", "eafp"],
    "order": ["sort", "tie", "max()"],
    "keys": ["dict.get", "missing", "a missing key", "attribute"],
    "types": ["truthiness", "validation", "json", "types"],
    "text": ["templates", "case-insensitive", "str.join", "f-strings", "regex", "string"],
}


def _classify(result: dict) -> list[tuple[str, str]]:
    """(pattern, what failed) for one failed check result."""
    if result.get("status") == "timeout":
        return [("slow", "ran out of time")]
    error = result.get("error") or ""
    if error:
        for pid, _label, _desc, _words, errors in PATTERNS:
            if any(e in error for e in errors):
                return [(pid, error.splitlines()[0][:80])]
    out = []
    for t in result.get("tests", []):
        if t.get("passed"):
            continue
        text = f"{t.get('name', '')} {t.get('message', '')}".lower()
        for pid, _label, _desc, words, errors in PATTERNS:
            if any(w in text for w in words) or any(e.lower() in text for e in errors):
                out.append((pid, t.get("name", "")))
                break
    return out


def _age_days(stamp: str) -> float:
    try:
        return max(0.0, (datetime.now() - datetime.fromisoformat(stamp)).total_seconds() / 86400)
    except ValueError:
        return 0.0


def analyse() -> dict:
    exs = progress.all_exercises()
    data = content.load()
    states = progress.exercise_states()
    rows = db.q("SELECT item_id, result, created_at FROM attempts WHERE status != 'passed' AND kind != 'project' "
                "ORDER BY id DESC LIMIT ?", (LOOKBACK,))
    scores: dict[str, float] = {}
    counts: dict[str, int] = {}
    examples: dict[str, list] = {}
    by_topic: dict[str, dict] = {}
    for r in rows:
        ex = exs.get(r["item_id"])
        if not ex:
            continue
        weight = 0.5 ** (_age_days(r["created_at"]) / HALF_LIFE_DAYS)
        for pid, what in _classify(json.loads(r["result"] or "{}")):
            scores[pid] = scores.get(pid, 0) + weight
            counts[pid] = counts.get(pid, 0) + 1
            ex_list = examples.setdefault(pid, [])
            if ex["id"] not in {e["id"] for e in ex_list} and len(ex_list) < 4:
                ex_list.append({"id": ex["id"], "title": ex["title"], "check": what})
            topic = ex.get("topic")
            if topic in data["topics_by_id"]:
                t = by_topic.setdefault(topic, {"id": topic, "title": data["topics_by_id"][topic]["title"],
                                                "failed": 0, "lapses": 0})
                t["failed"] += 1
    for eid, st in states.items():
        topic = exs.get(eid, {}).get("topic")
        if st.get("lapses") and topic in data["topics_by_id"]:
            t = by_topic.setdefault(topic, {"id": topic, "title": data["topics_by_id"][topic]["title"],
                                            "failed": 0, "lapses": 0})
            t["lapses"] += st["lapses"]
    patterns = sorted(({"id": pid, "label": label, "description": desc, "score": round(scores[pid], 2),
                        "count": counts[pid], "examples": examples[pid]}
                       for pid, label, desc, _w, _e in PATTERNS if pid in scores),
                      key=lambda p: -p["score"])
    chapters = sorted(by_topic.values(), key=lambda t: -(t["failed"] + 2 * t["lapses"]))[:5]
    return {"patterns": patterns, "chapters": chapters, "session": _session(patterns, chapters, exs, states),
            "attempts_considered": len(rows), "half_life_days": HALF_LIFE_DAYS}


def _session(patterns: list[dict], chapters: list[dict], exs: dict, states: dict) -> list[dict]:
    """Up to SESSION_SIZE steps aimed at the top patterns, each with the reason it was picked."""
    picked: list[dict] = []
    seen: set[str] = set()
    unlocked = {tid for tid, tp in progress.topic_progress(states).items() if tp["unlocked"] or tp["attempted"]}

    def add(ex_id: str, reason: str) -> None:
        if ex_id in seen or len(picked) >= SESSION_SIZE or ex_id not in exs:
            return
        seen.add(ex_id)
        st = states.get(ex_id, {})
        review = st.get("status") == "solved"
        picked.append({"id": ex_id, "title": exs[ex_id]["title"], "reason": reason,
                       "href": f"#/step/{ex_id}" + ("?review" if review else "")})

    for p in patterns[:3]:
        for e in p["examples"]:
            if states.get(e["id"], {}).get("status") != "solved":
                add(e["id"], f"Still open, failed on {LABELS[p['id']].lower()}")
    for p in patterns[:3]:
        words = PRACTICE.get(p["id"], [])
        for ex in exs.values():
            if not ex.get("extra") or ex.get("topic") not in unlocked or states.get(ex["id"], {}).get("status") == "solved":
                continue
            about = " ".join(ex.get("concepts", []) + [ex["title"]]).lower()
            if any(w in about for w in words):
                add(ex["id"], f"Practice for {LABELS[p['id']].lower()}")
                break
    weak_topics = {c["id"] for c in chapters}
    for eid, st in sorted(states.items(), key=lambda kv: -(kv[1].get("lapses") or 0)):
        if st.get("status") == "solved" and (st.get("lapses") or st.get("revealed")) and exs.get(eid, {}).get("topic") in weak_topics:
            add(eid, "Rebuild: you lapsed on it or needed the solution")
    return picked


def summary(limit: int = 3) -> list[dict]:
    return [{"id": p["id"], "label": p["label"], "count": p["count"]} for p in analyse()["patterns"][:limit]]

