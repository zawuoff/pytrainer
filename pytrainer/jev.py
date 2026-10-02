"""Jev (TypeSafe System One) client: fast, calibrated, structured judgments.

Docs: https://docs.typesafe.ai - POST /v1/systemone with a `state` and typed questions
(score / choice / noul). Used here for instant code-quality scoring and to check that
tutor replies never give away the solution. Optional: everything works without a key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from . import db

API = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"


class JevError(Exception):
    pass


def key() -> str:
    return db.get_setting("jev_key") or os.environ.get("TYPESAFE_API_KEY", "")


def enabled() -> bool:
    return bool(key()) and db.get_setting("jev_enabled", True)


def masked() -> str:
    k = key()
    return f"{k[:4]}...{k[-4:]}" if len(k) > 12 else ("set" if k else "")


def ask(state, questions: dict, *, timeout: float = 20, api_key: str | None = None) -> dict:
    """Send one state + questions; return the `answers` dict."""
    api_key = api_key or key()
    if not api_key:
        raise JevError("No Jev API key configured.")
    body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
        "User-Agent": "pytrainer/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        if exc.code in (401, 403):
            raise JevError("Jev rejected the API key.") from None
        if exc.code == 429:
            raise JevError("Jev rate limit hit; try again in a moment.") from None
        raise JevError(f"Jev error {exc.code}: {detail}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise JevError(f"Could not reach Jev: {exc}") from None
    return data.get("answers", {})


# --------------------------------------------------------------------------- code quality

QUALITY_DIMENSIONS = {
    "readability": {
        "instructions": "How easy is this Python code to read and follow?",
        "criteria": ["Very hard to follow: tangled logic, no clear flow",
                     "Readable with effort: some confusing parts",
                     "Clear: straightforward flow with minor rough spots",
                     "Very clear: reads like well-written prose, obvious intent"],
    },
    "naming": {
        "instructions": "How well are variables, functions and parameters named?",
        "criteria": ["Poor: single letters or misleading names for important values",
                     "Mixed: some vague or generic names",
                     "Good: names mostly describe what values hold",
                     "Excellent: every name is precise and conventional (snake_case)"],
    },
    "idiomatic": {
        "instructions": "How idiomatic (Pythonic) is this code?",
        "criteria": ["Not Pythonic: written like another language (index loops, manual flags, reinvented built-ins)",
                     "Somewhat Pythonic: works but misses obvious idioms",
                     "Pythonic: uses common idioms and built-ins appropriately",
                     "Very Pythonic: elegant use of the language, nothing a senior dev would rewrite"],
    },
    "simplicity": {
        "instructions": "Is the solution as simple as the task allows, without unnecessary steps or complexity?",
        "criteria": ["Far more complex than needed: redundant steps, convoluted logic",
                     "Somewhat over-complicated",
                     "Reasonably simple",
                     "As simple as possible while still correct"],
    },
    "robustness": {
        "instructions": "How well does the code handle edge cases and invalid input that the task mentions?",
        "criteria": ["Ignores edge cases the task mentions",
                     "Handles some edge cases, misses others",
                     "Handles the edge cases the task mentions",
                     "Handles edge cases thoughtfully and explicitly"],
    },
}


def code_quality(task: str, code: str) -> dict:
    """Score code on five dimensions in one call. Returns overall 0-10 plus per-dimension 0-10."""
    questions = {name: {"type": "score", **spec} for name, spec in QUALITY_DIMENSIONS.items()}
    state = {"task": task[:6000], "python_code": code[:12000]}
    answers = ask(state, questions)
    dims = {}
    for name in QUALITY_DIMENSIONS:
        a = answers.get(name) or {}
        top = len(QUALITY_DIMENSIONS[name]["criteria"]) - 1
        if "score" in a:
            dims[name] = {"score": round(10 * a["score"] / top, 1), "confidence": round(a.get("confidence", 0), 2)}
    if not dims:
        raise JevError("Jev returned no scores.")
    weights = {"readability": 0.25, "naming": 0.15, "idiomatic": 0.25, "simplicity": 0.2, "robustness": 0.15}
    total_w = sum(weights[d] for d in dims)
    overall = round(sum(dims[d]["score"] * weights[d] for d in dims) / total_w, 1)
    return {"overall": overall, "dims": dims, "by": "jev"}


# --------------------------------------------------------------------------- tutor guard

def tutor_gives_away(task: str, learner_code: str, reply: str) -> float:
    """Probability (0-1) that a tutor reply hands over the solution instead of guiding."""
    answers = ask(
        {"exercise": task[:5000], "learner_code": learner_code[:6000], "tutor_reply": reply[:4000]},
        {"gives_away": {
            "type": "noul",
            "instructions": "Does the tutor reply give away the solution to the exercise?",
            "criteria": {
                "true": "The reply contains code that solves the exercise or part of it, shows a corrected "
                        "version of the learner's code, or states the exact code change to make.",
                "false": "The reply only explains concepts, error messages or unrelated tiny examples, points "
                         "to where to look, or asks guiding questions.",
            },
        }},
        timeout=15,
    )
    return float((answers.get("gives_away") or {}).get("noul", 0.0))
