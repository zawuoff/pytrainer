"""Interview mode: a timed problem, then an AI interviewer's follow-ups, then a debrief.

The problem is a medium or hard step from a chapter you have unlocked (unsolved ones first). The
submission is graded by the step's hidden tests but never recorded as a practice attempt. With an AI
connected, the interviewer asks FOLLOWUPS questions about your actual code, one at a time, then
writes a scored debrief. Without one, a fixed set of standard questions and a self-review checklist
stand in.
"""

from __future__ import annotations

import json
import random

from . import ai, coach, content, db, progress, runner

FOLLOWUPS = 3
LENGTHS = (20, 30, 45)

STANDARD_QUESTIONS = [
    "Walk me through your solution. Why this approach?",
    "What is the time complexity of your code, and where does the cost come from?",
    "Which inputs would you test first, and which edge case worried you most?",
    "What would change if the input were a million times bigger?",
]

INTERVIEWER = f"""You are a friendly but rigorous technical interviewer for a junior AI-engineering role.
{coach.LEARNER}
You are in the follow-up part of a coding interview. You see the problem, the candidate's code, the
test results, and the conversation so far. Ask ONE short follow-up question at a time about THEIR code:
its time/space complexity, an edge case it handles or misses, how it would scale or change for a
real system (large inputs, an LLM API call failing, streaming), or an alternative approach. Before the
question, react to their last answer in one sentence (what was right, or what was missing). Never write
code for them. Keep it under 70 words. Plain text, no markdown headings."""

DEBRIEF = f"""You are the interviewer writing the debrief after a coding interview for a junior AI-engineering role.
{coach.LEARNER}
Judge honestly from the evidence: the problem, the code, the hidden-test results, the time used, and the
follow-up conversation. Scores are 1-5 (3 = meets the bar for a junior role).

Return JSON: {{"scores": {{"correctness": n, "problem_solving": n, "communication": n, "code_quality": n}},
"verdict": "<one of: strong yes, yes, lean yes, lean no, no>", "summary": "<2-3 sentences>",
"strengths": ["...", "..."], "to_work_on": ["...", "..."], "practice": "<one concrete next step>"}}"""


def pick(minutes: int) -> dict:
    """A medium/hard function step from an unlocked chapter, unsolved ones first."""
    if minutes not in LENGTHS:
        raise ValueError("pick 20, 30 or 45 minutes")
    data = content.load()
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    open_topics = {tid for tid, t in tp.items() if t["unlocked"] or t["attempted"] or t["cleared"]}
    want = 3 if minutes >= 45 else 2
    pool = [e for e in data["exercises"].values()
            if e.get("topic") in open_topics and e.get("mode", "function") == "function" and not e.get("extra")
            and e["difficulty"] >= 2 and not e.get("setup_files")]
    if not pool:
        raise ValueError("Unlock a few chapters first: interviews use medium and hard steps from chapters you've reached.")
    fresh = [e for e in pool if states.get(e["id"], {}).get("status") != "solved"]
    choices = [e for e in (fresh or pool) if e["difficulty"] == want] or fresh or pool
    return random.choice(choices)


def start(minutes: int) -> dict:
    ex = pick(minutes)
    iid = db.ex("INSERT INTO interviews(exercise_id, minutes, transcript, created_at) VALUES(?,?,?,?)",
                (ex["id"], minutes, "[]", db.now()))
    return {"id": iid, "minutes": minutes, "exercise": content.public_exercise(ex),
            "questions": STANDARD_QUESTIONS, "followups": FOLLOWUPS}


def _row(iid: int) -> dict:
    row = db.q1("SELECT * FROM interviews WHERE id=?", (iid,))
    if not row:
        raise ValueError("interview not found")
    return dict(row)


def submit(iid: int, files: dict, seconds: int) -> dict:
    row = _row(iid)
    if row["result"]:
        raise ValueError("This interview's solution was already submitted.")
    ex = progress.all_exercises()[row["exercise_id"]]
    result = runner.run_tests(files, ex["tests"], mode="function")
    db.ex("UPDATE interviews SET files=?, result=?, seconds=? WHERE id=?",
          (json.dumps(files), json.dumps(result), max(0, int(seconds)), iid))
    return result


def _context(row: dict) -> str:
    ex = progress.all_exercises()[row["exercise_id"]]
    files = json.loads(row["files"] or "{}")
    result = json.loads(row["result"] or "null")
    used = f"{(row['seconds'] or 0) // 60} of {row['minutes']} minutes"
    return (f"## Problem\n# {ex['title']}\n{ex['prompt']}\n\n## Candidate's code\n{coach._code_block(files)}\n\n"
            f"## Hidden test results\n{coach._result_text(result)}\n\nTime used: {used}")


def followup(iid: int, answer: str | None) -> dict:
    """Record the candidate's answer (if any) and get the interviewer's next question."""
    row = _row(iid)
    if not row["result"]:
        raise ValueError("Submit your solution first.")
    transcript = json.loads(row["transcript"] or "[]")
    if answer is not None and answer.strip():
        if not transcript or transcript[-1]["role"] != "interviewer":
            raise ValueError("There is no question to answer yet.")
        transcript.append({"role": "candidate", "content": answer.strip()[:3000]})
    asked = sum(1 for m in transcript if m["role"] == "interviewer")
    done = asked >= FOLLOWUPS and transcript and transcript[-1]["role"] == "candidate"
    if not done and (not transcript or transcript[-1]["role"] == "candidate"):
        convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in transcript) or "(no questions yet)"
        question = ai.complete(INTERVIEWER, f"{_context(row)}\n\n## Conversation so far\n{convo}\n\n"
                                            f"This is follow-up {asked + 1} of {FOLLOWUPS}.")
        transcript.append({"role": "interviewer", "content": question.strip()})
    db.ex("UPDATE interviews SET transcript=? WHERE id=?", (json.dumps(transcript), iid))
    return {"transcript": transcript, "done": bool(done)}


def debrief(iid: int) -> dict:
    row = _row(iid)
    if not row["result"]:
        raise ValueError("Submit your solution first.")
    transcript = json.loads(row["transcript"] or "[]")
    convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in transcript) or "(no follow-up conversation)"
    report = ai.complete_json(DEBRIEF, f"{_context(row)}\n\n## Follow-up conversation\n{convo}", timeout=300)
    db.ex("UPDATE interviews SET debrief=? WHERE id=?", (json.dumps(report), iid))
    return report


def history(limit: int = 10) -> list[dict]:
    exs = progress.all_exercises()
    out = []
    for r in db.q("SELECT * FROM interviews WHERE result IS NOT NULL ORDER BY id DESC LIMIT ?", (limit,)):
        result = json.loads(r["result"])
        report = json.loads(r["debrief"]) if r["debrief"] else None
        out.append({"id": r["id"], "title": exs.get(r["exercise_id"], {}).get("title", r["exercise_id"]),
                    "minutes": r["minutes"], "seconds": r["seconds"], "created_at": r["created_at"],
                    "tests": f"{result['passed']}/{result['total']}", "verdict": report.get("verdict") if report else None})
    return out
