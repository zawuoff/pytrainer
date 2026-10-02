"""Personalisation: a get-to-know-you chat builds a learner profile, and lessons are
re-told through the learner's own interests (cricket, cooking, their job...).

The profile lives in settings["profile"]. Personalised lessons are cached per
(exercise, profile version) in the personal_lessons table and prefetched for the
next steps in the background, so the learner rarely waits.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor

from . import ai, content, db, runner

# --------------------------------------------------------------------------- profile

def get_profile() -> dict | None:
    return db.get_setting("profile")


def profile_hash(profile: dict | None = None) -> str:
    profile = profile if profile is not None else get_profile()
    if not profile:
        return ""
    key = json.dumps({k: profile.get(k) for k in ("primary_interest", "interests", "profession",
                                                  "analogy_style", "level")}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def enabled() -> bool:
    return bool(get_profile()) and db.get_setting("personalise", True) and ai.enabled()


def context_line(profile: dict | None = None) -> str:
    """A short description of the learner for any AI prompt (tutor, feedback...)."""
    p = profile if profile is not None else get_profile()
    if not p:
        return ""
    bits = [f"The learner's name is {p['name']}." if p.get("name") else "",
            f"Their favourite thing to relate ideas to: {p.get('primary_interest')}." if p.get("primary_interest") else "",
            f"Other interests: {', '.join(p.get('interests', []))}." if p.get("interests") else "",
            f"Work/background: {p.get('profession')}." if p.get("profession") else "",
            f"Goal: {p.get('goal')}." if p.get("goal") else "",
            f"How they like things explained: {p.get('analogy_style')}." if p.get("analogy_style") else ""]
    text = " ".join(b for b in bits if b)
    return ("\n\nAbout this learner (address them as 'you'; never assume their gender) (use it to make explanations personal - e.g. an analogy from their "
            f"favourite interest - but never at the cost of accuracy): {text}") if text else ""


# --------------------------------------------------------------------------- onboarding chat

INTERVIEW_SYSTEM = """You are the friendly guide of PyTrainer, a Python course for someone becoming an AI
engineer. You're having a short, warm get-to-know-you chat so the course can explain things through
what THIS person loves. Style: like a great modern AI assistant - curious, upbeat, concise, a little
playful, never cheesy. One or two short sentences, then ONE clear question at a time.

Find out, over roughly 6-9 turns (fewer if they give a lot at once):
1. hobbies/passions (sports, games, music, cooking, films...) - ask for specifics (which sport? team?)
2. what they do for work or study, and anything from it they know deeply
3. why they're learning Python / what they want to build
4. how much coding they've done before (and in which language)
5. how they like explanations: everyday analogies, straight technical, lots of examples, humour...
If they mention several interests, ask which one they'd most like lessons built around (offer the
choices as options). Acknowledge answers specifically ("Ooh, a Chelsea fan - noted.") so it feels
personal. Don't lecture about Python here.

Always respond with JSON only:
{"reply": "<markdown, your message>",
 "options": ["<2-5 short tappable answers for your question, or [] if free text fits better>"],
 "done": false}
When you have enough (or they ask to finish), respond with done=true, a reply that summarises what
you'll do with it in 2 sentences, and a "profile":
{"reply": "...", "options": [], "done": true,
 "profile": {"name": "<if known or null>", "interests": ["..."], "primary_interest": "<the one to use
 most, specific e.g. 'cricket (batting, Test matches)'>", "profession": "<or null>",
 "expertise": "<things they know deeply, or null>", "goal": "<what they want to build/achieve>",
 "experience": "<prior coding in a phrase>", "analogy_style": "<how to explain, in a phrase>",
 "summary": "<2-3 sentence friendly portrait of them as a learner, written in second person ('You ...')>"}}
Never assume the learner's gender: address them as "you" or by name, never he/she."""

FIRST_MESSAGE = {
    "reply": "Hey! I'm your PyTrainer guide. 👋\n\nBefore we dive in, I'd love to get to know you a bit, so "
             "I can explain Python through things **you** actually care about. Think variables as a "
             "cricket scorecard, or loops as a recipe method.\n\nSo, to start: **what do you love doing "
             "when you're not at a screen?**",
    "options": ["Sports", "Gaming", "Music", "Cooking", "Films & series", "Something else"],
    "done": False,
}


def interview_history() -> list[dict]:
    row = db.q1("SELECT messages FROM chats WHERE item_id='onboarding'")
    return json.loads(row["messages"]) if row else []


def _save_history(history: list[dict]) -> None:
    db.ex("INSERT INTO chats(item_id, messages, updated_at) VALUES('onboarding',?,?) ON CONFLICT(item_id) "
          "DO UPDATE SET messages=excluded.messages, updated_at=excluded.updated_at",
          (json.dumps(history), db.now()))


def interview_start(restart: bool = False) -> list[dict]:
    history = [] if restart else interview_history()
    if not history:
        history = [{"role": "guide", "content": FIRST_MESSAGE["reply"], "options": FIRST_MESSAGE["options"]}]
        _save_history(history)
    return history


def interview_turn(message: str, finish: bool = False) -> dict:
    history = interview_start()
    history.append({"role": "learner", "content": message})
    name = db.get_setting("name", "")
    convo = "\n".join(f"{'GUIDE' if m['role'] == 'guide' else 'LEARNER'}: {m['content']}" for m in history[-24:])
    prompt = ((f"The learner told the app their name is {name}.\n" if name else "") +
              f"Conversation so far:\n{convo}\n\n" +
              ("The learner wants to finish now: respond with done=true and the profile.\n" if finish else "") +
              "Your next message as JSON:")
    data = ai.complete_json(INTERVIEW_SYSTEM, prompt, timeout=180)
    reply = str(data.get("reply", "")).strip() or "Tell me a bit more?"
    options = [str(o)[:60] for o in (data.get("options") or [])][:5]
    history.append({"role": "guide", "content": reply, "options": options})
    _save_history(history)
    out = {"history": history, "done": bool(data.get("done"))}
    if out["done"] and isinstance(data.get("profile"), dict):
        prof = data["profile"]
        prof["interests"] = [str(i) for i in (prof.get("interests") or [])][:8]
        prof["name"] = prof.get("name") or name or None
        out["profile"] = prof
    return out


def save_profile(profile: dict) -> dict:
    clean = {k: profile.get(k) for k in ("name", "interests", "primary_interest", "profession", "expertise",
                                         "goal", "experience", "analogy_style", "summary")}
    clean["interests"] = [str(i)[:60] for i in (clean.get("interests") or []) if str(i).strip()][:8]
    for k in ("primary_interest", "profession", "expertise", "goal", "experience", "analogy_style", "summary", "name"):
        if clean.get(k) is not None:
            clean[k] = str(clean[k])[:400]
    clean["updated_at"] = db.now()
    db.set_setting("profile", clean)
    if clean.get("name") and not db.get_setting("name"):
        db.set_setting("name", clean["name"])
    return clean


# --------------------------------------------------------------------------- personalised lessons

PERSONALISE_SYSTEM = """You rewrite one short lesson of a beginner Python course so it clicks for ONE
specific learner, by explaining the idea through their own world (their favourite interest, their job).

Hard rules:
- Teach EXACTLY the same concept, to the same depth, and keep EVERY technical term / piece of
  vocabulary the original introduces (introduce them the same gentle way: plain words first, then
  "the proper name for this is ...").
- Build the metaphor and the example data from the learner's interest (e.g. cricket: runs, overs,
  batters; cooking: ingredients, recipes). Keep it natural - one clear analogy, not a pile of puns.
- Include 1-2 tiny ```python examples that use that theme. Each must be a complete, runnable,
  standard-library-only snippet (<= 12 lines) that PRINTS its result, uses no input(), no files,
  no network, no randomness.
- NEVER solve or hint at the solution of the exercise described below; examples must use different
  names/data and must not be copy-pasteable into it.
- Similar length to the original (a bit shorter is fine). Beginner-friendly, warm, short sentences.
- Output ONLY the lesson markdown (no preamble, no heading with the exercise title)."""


def _python_blocks(md: str) -> list[str]:
    return re.findall(r"```python\n(.*?)```", md, re.S)


def _check_examples(md: str) -> list[str]:
    errors = []
    for i, code in enumerate(_python_blocks(md), 1):
        r = runner.run_code({"snippet.py": code}, main="snippet.py", timeout=5)
        if r["timed_out"] or r["returncode"] != 0:
            errors.append(f"example {i} failed: {(r['stderr'] or 'timed out').strip()[-300:]}")
        elif not r["stdout"].strip():
            errors.append(f"example {i} prints nothing")
    return errors


def _generate(ex: dict, profile: dict) -> str:
    data = content.load()
    topic = data["topics_by_id"].get(ex.get("topic"), {})
    base = (f"## The learner\n{json.dumps(profile, indent=1)}\n\n"
            f"## Chapter: {topic.get('title', '')}\n\n## Original lesson\n{ex['lesson']}\n\n"
            f"## The exercise that follows (do NOT solve it)\n{ex['prompt']}\n")
    last_err = ""
    for _ in range(2):
        prompt = base + (f"\nYour previous version had broken examples, fix them: {last_err}\n" if last_err else "")
        text = ai.complete(PERSONALISE_SYSTEM, prompt, timeout=240).strip()
        text = re.sub(r"^```(?:markdown)?\n(.*)\n```$", r"\1", text, flags=re.S).strip()
        errors = _check_examples(text)
        if not errors and len(text) > 150:
            return text
        last_err = "; ".join(errors) or "too short"
    raise ai.AIError("Couldn't produce a personalised version with working examples.")


_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()
_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="personalise")


def _lock_for(key: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(key, threading.Lock())


def cached(ex_id: str) -> str | None:
    row = db.q1("SELECT content FROM personal_lessons WHERE exercise_id=? AND profile_hash=?",
                (ex_id, profile_hash()))
    return row["content"] if row else None


def personal_lesson(ex_id: str) -> str:
    """Return the personalised lesson for a step, generating (once) if needed."""
    profile = get_profile()
    if not profile:
        raise ai.AIError("No profile yet: do the get-to-know-you chat first.")
    ex = content.load()["exercises"].get(ex_id)
    if not ex or not ex.get("lesson"):
        raise ai.AIError("This step has no lesson to personalise.")
    h = profile_hash(profile)
    with _lock_for(f"{ex_id}:{h}"):
        hit = cached(ex_id)
        if hit:
            return hit
        text = _generate(ex, profile)
        db.ex("INSERT OR REPLACE INTO personal_lessons(exercise_id, profile_hash, content, created_at) "
              "VALUES(?,?,?,?)", (ex_id, h, text, db.now()))
        return text


def prefetch(ex_ids: list[str]) -> None:
    """Warm the cache for the next steps in the background."""
    if not enabled():
        return
    exercises = content.load()["exercises"]
    for ex_id in ex_ids:
        ex = exercises.get(ex_id)
        if ex and ex.get("lesson") and not cached(ex_id):
            _pool.submit(_safe_generate, ex_id)


def _safe_generate(ex_id: str) -> None:
    try:
        personal_lesson(ex_id)
    except Exception as exc:  # noqa: BLE001 - background best effort
        print(f"prefetch {ex_id} failed: {exc}", flush=True)
