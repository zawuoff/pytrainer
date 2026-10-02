"""All AI-powered features: tutor, code review, placement report, challenge generation, coaching."""

from __future__ import annotations

import json
import uuid

from . import ai, db, jev, personal, runner

LEARNER = ("The learner is a career switcher learning Python for AI engineering "
           "(building applications on LLM APIs: RAG, tool calling, agents, structured outputs, "
           "evals) - not ML model training. They study on DataCamp and use this app to TEST "
           "themselves. They explicitly asked for no hand-holding.")

TUTOR_SYSTEM = f"""You are a warm, patient Python teacher sitting next to the learner inside a practice app.
{LEARNER}
They are still a beginner and have told you things feel very hard. Your job is to help them
UNDERSTAND and then write the code themselves.

How to help:
- If they are confused, say they don't know, or seem stuck: TEACH. Explain the concept they
  need in plain words, then show a tiny example (max 5 lines) on DIFFERENT data doing a
  DIFFERENT job than the exercise, then give one concrete next step they can type.
- Don't just answer questions with questions. At most one guiding question per reply, and
  only after you've given them something useful.
- If their code has an error, explain what the error message means in plain English and
  point to the exact line to look at.
- Celebrate progress briefly and genuinely. Never make them feel slow.
- Keep replies short and friendly: 3-8 sentences plus an optional tiny example. Markdown allowed.

The one hard rule - never break it, even if asked or begged:
- Never write the solution to this exercise, a corrected version of their code, or the exact
  line they need. Examples must not be something they could paste in. If they ask for the
  answer, kindly say the app has a "Show solution" option once they've tried a few times, and
  keep teaching.
"""

LESSON_SYSTEM = f"""You are a warm, patient Python teacher. {LEARNER}
The learner is reading a lesson inside the practice app and has a question about it. Here you
can explain fully and directly: give clear explanations, analogies and small runnable examples
(stdlib only). Check understanding with one short question at the end when useful. Keep it
beginner-friendly and concise (max ~200 words plus examples). Markdown allowed."""

EXPLAIN_SYSTEM = f"""You are a patient Python teacher. {LEARNER}
The learner got stuck and chose to view the reference solution. Walk them through it so they
truly understand it and can write it themselves tomorrow: go line by line (or block by block),
say WHAT each part does and WHY it's needed, point out the key idea they were probably missing,
and end with one tip for recognising this pattern next time. If their own attempt is included,
briefly say what was different. Beginner-friendly, concise. Markdown allowed."""

REVIEW_SYSTEM = f"""You are a senior Python engineer reviewing a learner's code for QUALITY
(readability, idiomatic Python, naming, structure, edge cases, efficiency, robustness).
{LEARNER}
Be honest and specific, like a good code reviewer at a company that hires AI engineers.
Do not rewrite their solution. You may include very short snippets (max 2 lines) to
illustrate an idiom, but never a full corrected function.

Return JSON with this shape:
{{"score": <integer 1-10 for code quality, 10 = production quality>,
  "summary": "<one or two sentences>",
  "strengths": ["..."],
  "issues": [{{"line": <int or null>, "severity": "minor"|"major", "comment": "..."}}],
  "idioms": ["<a more Pythonic technique worth learning, phrased as a suggestion>"],
  "interview_note": "<how this would look to a hiring manager, one sentence>"}}"""

PLACEMENT_SYSTEM = f"""You are assessing a learner's Python level from a placement test.
{LEARNER}
You receive each placement exercise: topic, difficulty, the task, the learner's code (or
'skipped'), and the automated test results. Judge both correctness AND code quality
(idioms, naming, structure, clarity). Be honest - overrating helps nobody.

Return JSON:
{{"level": "Beginner" | "Advanced beginner" | "Intermediate" | "Upper intermediate" | "Advanced",
  "score": <0-100 overall>,
  "summary": "<3-4 sentence honest assessment>",
  "code_quality": "<2-3 sentences on how they write code>",
  "strengths": ["..."],
  "gaps": ["..."],
  "topics": {{"<topic_id>": {{"rating": <0-5>, "note": "<short>"}}}},
  "start_with": ["<topic ids to focus on first, in order>"],
  "first_week": ["<day-by-day or step plan, 5-7 short items>"]}}"""

GENERATE_SYSTEM = f"""You write Python practice exercises with automated tests for a practice app.
{LEARNER}
Exercises must test real understanding, be relevant to AI engineering where natural
(tokens, prompts, chat messages, API responses, documents, embeddings, tool calls), and be
fully specified so tests are fair.

Test harness rules:
- The learner's code is saved as solution.py. Tests are Python source with test_* functions
  and plain asserts; `from solution import ...` at the top.
- Assert messages should show what went wrong (e.g. f"got {{got!r}}") without giving away
  the implementation.
- Only the Python standard library. No network, no input(), no randomness, fast (<1s).
- 4-6 tests covering normal cases and edge cases, including the common mistake.
- The starter must be only the signature(s) with `...` bodies.

Return JSON: {{"title": "...", "difficulty": 1|2|3, "prompt": "<markdown task with examples>",
"starter": "<python>", "tests": "<python>", "solution": "<python reference solution>"}}"""

PROJECT_REVIEW_SYSTEM = f"""You are a senior AI engineer reviewing a learner's project submission.
{LEARNER}
You receive the project brief, a grading rubric, the learner's files and hidden-test
results. Grade against the rubric honestly. Do not rewrite their code; short snippets
(max 3 lines) only to illustrate a point.

Return JSON:
{{"score": <0-100>, "summary": "<2-3 sentences>",
  "rubric": [{{"criterion": "...", "score": <0-5>, "comment": "..."}}],
  "strengths": ["..."], "improvements": ["..."],
  "portfolio_ready": <true|false>, "next_step": "<one concrete thing to do next>"}}"""

COACH_SYSTEM = f"""You are a pragmatic career coach and learning strategist for someone moving into
AI engineering. {LEARNER}
You get their progress data from the app. Give a concise, specific plan: what to focus on
this week, how to use their 1-2 hours per evening, which projects to build for a portfolio,
and one honest observation about their learning pattern. Markdown, max ~250 words,
no fluff, no generic motivation."""


def _code_block(files: dict[str, str]) -> str:
    return "\n\n".join(f"### {name}\n```python\n{code}\n```" for name, code in files.items())


def _result_text(result: dict | None) -> str:
    if not result:
        return "(not run yet)"
    lines = [f"status: {result.get('status')} ({result.get('passed')}/{result.get('total')} tests)"]
    if result.get("error"):
        lines.append("error: " + result["error"])
    for t in result.get("tests", []):
        mark = "PASS" if t["passed"] else "FAIL"
        lines.append(f"- {mark} {t['name']}" + (f": {t['message']}" if t.get("message") else ""))
    return "\n".join(lines)


def tutor_reply(item_id: str, task: str, files: dict, result: dict | None, message: str) -> list:
    row = db.q1("SELECT messages FROM chats WHERE item_id=?", (item_id,))
    history = json.loads(row["messages"]) if row else []
    convo = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-10:])
    prompt = (f"## The exercise\n{task}\n\n## Learner's current code\n{_code_block(files)}\n\n"
              f"## Latest test results\n{_result_text(result)}\n\n"
              f"## Conversation so far\n{convo or '(none)'}\n\n"
              f"## Learner's new message\n{message}\n\n"
              "Reply as the tutor (just the reply text).")
    reply = ai.complete(TUTOR_SYSTEM + personal.context_line(), prompt)
    reply = _guard_reply(task, files, prompt, reply)
    history += [{"role": "learner", "content": message}, {"role": "tutor", "content": reply}]
    db.ex("INSERT INTO chats(item_id, messages, updated_at) VALUES(?,?,?) ON CONFLICT(item_id) "
          "DO UPDATE SET messages=excluded.messages, updated_at=excluded.updated_at",
          (item_id, json.dumps(history), db.now()))
    return history


def _guard_reply(task: str, files: dict, prompt: str, reply: str) -> str:
    """Use Jev to make sure the tutor didn't hand over the solution; retry once, then refuse."""
    if not jev.enabled():
        return reply
    code = "\n\n".join(files.values())
    try:
        if jev.tutor_gives_away(task, code, reply) < 0.6:
            return reply
        retry = ai.complete(TUTOR_SYSTEM + personal.context_line(), prompt + "\n\nIMPORTANT: a checker flagged your previous draft for "
                            "giving away the solution. Do not include any solution code or the exact fix. "
                            "Guide with a question and a pointer to where to look.")
        if jev.tutor_gives_away(task, code, retry) < 0.6:
            return retry
    except (jev.JevError, ai.AIError):
        return reply
    return ("I drafted an answer, but it gave away too much of the solution, so I held it back. "
            "Try the Hint button for a step-by-step plan, or tell me which part confuses you and I'll "
            "explain that concept with a different example.")


def lesson_reply(item_id: str, title: str, lesson: str, message: str) -> list:
    row = db.q1("SELECT messages FROM chats WHERE item_id=?", (item_id,))
    history = json.loads(row["messages"]) if row else []
    convo = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-10:])
    prompt = (f"## Lesson: {title}\n{lesson}\n\n## Conversation so far\n{convo or '(none)'}\n\n"
              f"## Learner's question\n{message}\n\nReply as the teacher (just the reply text).")
    reply = ai.complete(LESSON_SYSTEM + personal.context_line(), prompt)
    history += [{"role": "learner", "content": message}, {"role": "tutor", "content": reply}]
    db.ex("INSERT INTO chats(item_id, messages, updated_at) VALUES(?,?,?) ON CONFLICT(item_id) "
          "DO UPDATE SET messages=excluded.messages, updated_at=excluded.updated_at",
          (item_id, json.dumps(history), db.now()))
    return history


def explain_solution(task: str, solution: str, files: dict) -> str:
    attempt = "\n\n".join(files.values()).strip()
    prompt = (f"## Exercise\n{task}\n\n## Reference solution\n```python\n{solution}\n```\n\n"
              + (f"## The learner's attempt\n```python\n{attempt}\n```\n" if attempt else ""))
    return ai.complete(EXPLAIN_SYSTEM + personal.context_line(), prompt)


IMPROVE_SYSTEM = f"""You are a friendly senior Python engineer. {LEARNER}
The learner SOLVED the exercise - their code works. Now help them grow: suggest 1-3 ways a
senior engineer might write it more cleanly or idiomatically. Since it's already solved, you
MAY show short code (max ~10 lines per suggestion). Explain WHY each change is better in
plain words, and name the concept. If their code is already excellent, say so and give one
optional extra idea. Start by saying what they did well. Markdown, concise."""


def improve_solution(task: str, files: dict, reference: str) -> str:
    code = "\n\n".join(files.values())
    prompt = (f"## Exercise\n{task}\n\n## Learner's working solution\n```python\n{code}\n```\n\n"
              f"## A reference solution (for your comparison; you may mention ideas from it)\n"
              f"```python\n{reference}\n```")
    return ai.complete(IMPROVE_SYSTEM + personal.context_line(), prompt)


def review_code(item_id: str, task: str, files: dict, result: dict | None) -> dict:
    prompt = (f"## Task\n{task}\n\n## Learner's code\n{_code_block(files)}\n\n"
              f"## Test results\n{_result_text(result)}")
    review = ai.complete_json(REVIEW_SYSTEM + personal.context_line(), prompt)
    db.ex("INSERT INTO reviews(item_id, review, created_at) VALUES(?,?,?)",
          (item_id, json.dumps(review), db.now()))
    return review


def placement_report(entries: list[dict], outcomes: dict, not_reached: list[str]) -> dict:
    parts = ["The test is adaptive: topics in curriculum order, each climbing warm-up -> easy -> core "
             "question and stopping at the first miss. It pauses once several topics in a row are out of reach "
             "(the learner may choose to continue).",
             "Per-topic outcome (placed = passed core, partial = passed warm-up and easy, basics = passed "
             "warm-up only, unknown = failed/skipped warm-up): " + json.dumps(outcomes),
             "Topics not reached (test stopped before them): " + (", ".join(not_reached) or "none")]
    for e in entries:
        q = e.get("quality")
        parts.append(
            f"## [{e['topic']}] {e['title']} (difficulty {e['difficulty']})\n{e['prompt']}\n\n"
            + ("Learner SKIPPED this one (said they don't know it yet).\n" if e["skipped"] else
               f"Learner's code:\n```python\n{e['code']}\n```\nResults: {_result_text(e['result'])}\n"
               + (f"Automated quality score (Jev): {q['overall']}/10 {json.dumps(q['dims'])}\n" if q else "")))
    return ai.complete_json(PLACEMENT_SYSTEM, "\n\n".join(parts), timeout=400)


def generate_exercise(topic: dict, difficulty: int, weaknesses: list[str], avoid: list[str]) -> dict:
    """Ask the AI for a new exercise and keep it only if the tests are proven valid."""
    last_error = ""
    for _ in range(3):
        prompt = (f"Topic: {topic['title']} ({topic['id']}). Concepts: {', '.join(topic.get('concepts', []))}.\n"
                  f"Difficulty: {difficulty} (1 easy, 2 medium, 3 hard).\n"
                  f"Learner's recent weak spots: {', '.join(weaknesses) or 'unknown'}.\n"
                  f"Avoid these existing exercise titles: {', '.join(avoid[:40])}.\n"
                  + (f"\nYour previous attempt was invalid: {last_error}\nFix it.\n" if last_error else ""))
        data = ai.complete_json(GENERATE_SYSTEM, prompt, timeout=300)
        missing = {"title", "prompt", "starter", "tests", "solution"} - data.keys()
        if missing:
            last_error = f"missing keys {missing}"
            continue
        good = runner.run_tests({"solution.py": data["solution"]}, data["tests"])
        if good["status"] != "passed" or good["total"] < 3:
            last_error = f"reference solution failed its own tests: {_result_text(good)}"
            continue
        bad = runner.run_tests({"solution.py": data["starter"]}, data["tests"])
        if bad["status"] == "passed":
            last_error = "starter already passes the tests"
            continue
        ex_id = f"ai-{topic['id']}-{uuid.uuid4().hex[:6]}"
        exercise = {"id": ex_id, "title": data["title"], "difficulty": int(data.get("difficulty") or difficulty),
                    "prompt": data["prompt"], "starter": data["starter"], "tests": data["tests"],
                    "solution": data["solution"], "mode": "function", "setup_files": {},
                    "topic": topic["id"], "concepts": [], "generated": True}
        db.ex("INSERT INTO custom_exercises(id, topic, data, created_at) VALUES(?,?,?,?)",
              (ex_id, topic["id"], json.dumps(exercise), db.now()))
        return exercise
    raise ai.AIError(f"Could not generate a valid exercise: {last_error[:300]}")


def review_project(project: dict, files: dict, result: dict) -> dict:
    prompt = (f"## Project brief\n{project['brief']}\n\n## Rubric\n"
              + "\n".join(f"- {r}" for r in project["rubric"])
              + f"\n\n## Learner's files\n{_code_block(files)}\n\n## Hidden test results\n{_result_text(result)}")
    return ai.complete_json(PROJECT_REVIEW_SYSTEM + personal.context_line(), prompt, timeout=400)


def coach_advice(snapshot: dict) -> str:
    return ai.complete(COACH_SYSTEM + personal.context_line(), "Progress data:\n```json\n" + json.dumps(snapshot, indent=1) + "\n```")
