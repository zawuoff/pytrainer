"""Drills from your mistakes: the AI reads your last failed attempts and writes practice aimed at them.

One AI call gets up to ten recent failed attempts (the task, the learner's code and what failed)
and returns a short diagnosis plus a few new exercises. Each exercise is kept only when its
reference solution passes its own tests and its starter fails them, then it is saved like any
AI-generated step in the chapter it practises.
"""

from __future__ import annotations

import json
import uuid

from . import ai, coach, content, db, progress, runner

MAX_MISTAKES = 10
WANT = 3

SYSTEM = f"""You are a Python teacher who designs practice from a learner's real mistakes.
{coach.LEARNER}

You get the learner's most recent failed attempts: the task, their code, and which checks failed
and how. First find what the mistakes have in common: the misunderstanding or habit behind them,
not the surface topic. Then write {WANT} NEW short exercises that each make the learner confront
that misunderstanding directly, in a fresh context (do not repeat the original tasks).

Test harness rules:
- The learner's code is saved as solution.py. Tests are test_* functions with plain asserts and
  `from solution import ...` at the top. Standard library only, no network, no input(), fast.
- 3-5 tests per exercise, including the case the learner kept getting wrong. Assert messages show
  what went wrong (e.g. f"got {{got!r}}") without giving away the implementation.
- The starter is only the signature(s) with `...` bodies.

Return JSON:
{{"summary": "<2-3 plain sentences to the learner: what the mistakes have in common and what to watch for>",
 "exercises": [{{"title": "...", "topic": "<one topic id from the list given>", "difficulty": 1|2|3,
   "targets": "<which mistake this practises, one short sentence>",
   "prompt": "<markdown task with 1-3 examples>", "starter": "<python>", "tests": "<python>",
   "solution": "<python reference solution>"}}]}}"""


def recent_mistakes(limit: int = MAX_MISTAKES) -> list[dict]:
    """The newest failed attempt for each of the last `limit` distinct steps that failed."""
    exs = progress.all_exercises()
    out, seen = [], set()
    for r in db.q("SELECT item_id, files, result FROM attempts WHERE status != 'passed' "
                  "AND kind IN ('practice', 'review', 'placement') ORDER BY id DESC LIMIT 300"):
        ex = exs.get(r["item_id"])
        if not ex or ex["id"] in seen or ex.get("mode") in ("predict", "traceback"):
            continue
        seen.add(ex["id"])
        result = json.loads(r["result"] or "{}")
        files = json.loads(r["files"] or "{}")
        out.append({"id": ex["id"], "title": ex["title"], "topic": ex.get("topic"), "prompt": ex["prompt"][:900],
                    "code": "\n\n".join(files.values())[:1500], "result": coach._result_text(result)[:900]})
        if len(out) >= limit:
            break
    return out


def _validate(data: dict) -> str:
    missing = {"title", "prompt", "starter", "tests", "solution"} - data.keys()
    if missing:
        return f"missing {sorted(missing)}"
    good = runner.run_tests({"solution.py": data["solution"]}, data["tests"])
    if good["status"] != "passed" or good["total"] < 3:
        return "reference solution fails its own tests"
    if runner.run_tests({"solution.py": data["starter"]}, data["tests"])["status"] == "passed":
        return "starter already passes"
    return ""


def make_drill() -> dict:
    mistakes = recent_mistakes()
    if not mistakes:
        raise ValueError("No failed attempts yet: there's nothing to learn from. Come back after a few checks fail.")
    data = content.load()
    topics = {t["id"] for t in data["topics"]}
    prompt = ("Topic ids you may use: " + ", ".join(sorted(topics)) + "\n\n" + "\n\n".join(
        f"## Mistake {i + 1}: {m['title']} (topic {m['topic']})\n### Task\n{m['prompt']}\n### Their code\n"
        f"```python\n{m['code']}\n```\n### What failed\n{m['result']}" for i, m in enumerate(mistakes)))
    reply = ai.complete_json(SYSTEM, prompt, timeout=420)
    fallback = next((m["topic"] for m in mistakes if m["topic"] in topics), data["topics"][0]["id"])
    kept, rejected = [], []
    for raw in (reply.get("exercises") or [])[:WANT + 1]:
        if not isinstance(raw, dict):
            continue
        problem = _validate(raw)
        if problem:
            rejected.append(problem)
            continue
        topic = raw.get("topic") if raw.get("topic") in topics else fallback
        ex = {"id": f"ai-{topic}-{uuid.uuid4().hex[:6]}", "title": str(raw["title"])[:80],
              "difficulty": max(1, min(int(raw.get("difficulty") or 2), 3)), "prompt": raw["prompt"],
              "starter": raw["starter"], "tests": raw["tests"], "solution": raw["solution"], "mode": "function",
              "setup_files": {}, "topic": topic, "concepts": [], "generated": True, "from_mistakes": True,
              "targets": str(raw.get("targets") or "")[:200]}
        db.ex("INSERT INTO custom_exercises(id, topic, data, created_at) VALUES(?,?,?,?)",
              (ex["id"], topic, json.dumps(ex), db.now()))
        kept.append(ex)
    if not kept:
        raise ai.AIError("The AI's exercises didn't pass their own checks (" + "; ".join(rejected[:3]) + "). Try again.")
    drill = {"summary": str(reply.get("summary") or "")[:800], "created_at": db.now(),
             "based_on": [m["title"] for m in mistakes],
             "steps": [{"id": e["id"], "title": e["title"], "reason": e["targets"] or "Practice from your mistakes",
                        "href": f"#/step/{e['id']}", "status": "new"} for e in kept]}
    db.set_setting("mistake_drill", drill)
    return drill


def last_drill() -> dict | None:
    drill = db.get_setting("mistake_drill")
    if not drill:
        return None
    exs = progress.all_exercises()
    states = progress.exercise_states()
    drill["steps"] = [s | {"status": states.get(s["id"], {}).get("status", "new")} for s in drill["steps"] if s["id"] in exs]
    return drill
