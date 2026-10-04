"""Reviews in a changed form: the AI rewrites a due review with new names, story and data.

A variant tests the same skill at the same difficulty, so recalling the *idea* is what passes
it, not remembering the text. It is only kept when it is proven sound and actually different:

- its reference solution passes its own tests (at least 3 of them),
- its starter fails them,
- the original reference solution fails them (otherwise the old answer could be pasted back).

Variants are made ahead of time by one background worker, for reviews that are due now or
tomorrow, so opening a review never waits on the AI. Passing a variant counts as a review of
the original exercise, and the variant is then dropped so the next review gets a fresh one.
"""

from __future__ import annotations

import json
import threading
from datetime import date, timedelta

from . import ai, coach, db, runner

MODES = ("function", "script")
PER_RUN = 3

VARIANT_SYSTEM = f"""You write practice exercises with automated tests for a Python practice app.
{coach.LEARNER}

You get an exercise the learner already solved. Write a VARIANT of it for a spaced-repetition
review. It must test exactly the same skill at the same difficulty, but look different, so the
learner has to recall the idea rather than the text.

Change: the function and parameter names, the story (pick another realistic AI-engineering
setting: tokens, prompts, chat messages, model configs, API responses, documents, chunks,
embeddings, tool calls, eval results, logs...), every literal value and example, and so every
expected output.
Keep: the concept, the Python features a good solution uses, the difficulty, the mode (function:
tests do `from solution import ...`; script: tests call `run_script(...)` and check its output),
and any files it reads (the same file names will be next to the code).

Test harness: the learner's file is solution.py. Tests are test_* functions with plain asserts.
Available without import: run_script(args=None, stdin="", env=None, file=None, timeout=5) returning
an object with .stdout/.stderr/.returncode, capture(fn, *args) returning (value, printed),
load(), source(). Standard library only, no network, no input(), no randomness, fast.
Write 4-6 tests covering normal and edge cases; assert messages show what went wrong
(e.g. f"got {{got!r}}") without giving the implementation away.

Return JSON: {{"title": "...", "prompt": "<markdown: what goes in, what comes out, rules, 1-2
examples; same structure as the original>", "starter": "<signature(s) with ... bodies, or a
comment for scripts>", "tests": "<python>", "solution": "<clean reference solution>"}}"""

_lock = threading.Lock()
_worker: threading.Thread | None = None


def enabled() -> bool:
    return ai.current().get("provider", "none") != "none" and db.get_setting("review_variants", True)


def eligible(ex: dict) -> bool:
    return ex.get("mode", "function") in MODES and not ex.get("generated")


def get(ex_id: str) -> dict | None:
    row = db.q1("SELECT data FROM review_variants WHERE exercise_id=?", (ex_id,))
    return json.loads(row["data"]) if row else None


def ready_ids() -> set[str]:
    return {r["exercise_id"] for r in db.q("SELECT exercise_id FROM review_variants")}


def drop(ex_id: str) -> None:
    db.ex("DELETE FROM review_variants WHERE exercise_id=?", (ex_id,))


def save(ex_id: str, variant: dict) -> None:
    db.ex("INSERT INTO review_variants(exercise_id, data, created_at) VALUES(?,?,?) "
          "ON CONFLICT(exercise_id) DO UPDATE SET data=excluded.data, created_at=excluded.created_at",
          (ex_id, json.dumps(variant), db.now()))


def _grade(ex: dict, code: str, tests: str) -> dict:
    return runner.run_tests({"solution.py": code}, tests, mode=ex.get("mode", "function"),
                            setup_files=ex.get("setup_files"))


def validate(ex: dict, data: dict) -> str:
    """Empty string when the variant is usable, else what is wrong with it."""
    missing = {"title", "prompt", "starter", "tests", "solution"} - data.keys()
    if missing:
        return f"missing keys {sorted(missing)}"
    if not all(isinstance(data[k], str) and data[k].strip() for k in ("title", "prompt", "tests", "solution")):
        return "title, prompt, tests and solution must be non-empty text"
    good = _grade(ex, data["solution"], data["tests"])
    if good["status"] != "passed" or good["total"] < 3:
        return f"the reference solution must pass at least 3 tests: {coach._result_text(good)}"
    if _grade(ex, data["starter"], data["tests"])["status"] == "passed":
        return "the starter already passes the tests"
    if _grade(ex, ex["solution"], data["tests"])["status"] == "passed":
        return "the original solution passes these tests unchanged, so nothing really changed"
    return ""


def generate(ex: dict, tries: int = 2) -> dict:
    """Ask the AI for a variant of ``ex`` and return it once it validates. Raises ai.AIError."""
    last = ""
    for _ in range(tries):
        prompt = (f"## Original exercise ({ex.get('mode', 'function')} mode, difficulty {ex.get('difficulty')})\n"
                  f"# {ex['title']}\n\n{ex['prompt']}\n\n## Its reference solution\n```python\n{ex['solution']}\n```\n\n"
                  f"## Its tests\n```python\n{ex['tests']}\n```\n"
                  + (f"\nFiles next to the code: {', '.join(ex.get('setup_files') or {})}\n" if ex.get("setup_files") else "")
                  + (f"\nYour previous variant was rejected: {last}\nFix that.\n" if last else ""))
        data = ai.complete_json(VARIANT_SYSTEM, prompt, timeout=300)
        last = validate(ex, data)
        if not last:
            return {"title": data["title"].strip(), "prompt": data["prompt"], "starter": data["starter"],
                    "tests": data["tests"], "solution": data["solution"], "based_on": ex["id"]}
    raise ai.AIError(f"Could not make a valid variant: {last[:300]}")


def _due_soon() -> list[str]:
    horizon = (date.today() + timedelta(days=1)).isoformat()
    return [r["exercise_id"] for r in db.q(
        "SELECT exercise_id FROM exercise_state WHERE status='solved' AND next_review IS NOT NULL "
        "AND next_review <= ? ORDER BY next_review", (horizon,))]


def _work(exercises: dict) -> None:
    global _worker
    try:
        have = ready_ids()
        todo = [i for i in _due_soon() if i not in have and i in exercises and eligible(exercises[i])]
        for ex_id in todo[:PER_RUN]:
            try:
                save(ex_id, generate(exercises[ex_id]))
            except (ai.AIError, OSError) as exc:
                print(f"review variant for {ex_id} failed: {exc}", flush=True)
    finally:
        with _lock:
            _worker = None


def prepare(exercises: dict) -> bool:
    """Start the background worker if there is work and it isn't already running."""
    global _worker
    if not enabled():
        return False
    with _lock:
        if _worker is not None:
            return False
        _worker = threading.Thread(target=_work, args=(exercises,), daemon=True, name="review-variants")
        _worker.start()
    return True
