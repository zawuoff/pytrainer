"""Spaced repetition scheduling with FSRS-4.5 (Free Spaced Repetition Scheduler).

Each solved exercise carries a memory *stability* S (days until recall drops to 90%) and a
*difficulty* D (1 easy .. 10 hard). Every graded review updates both from a rating, and the
next review is set for when recall is predicted to fall to ``RETENTION``. Unlike a fixed
ladder of intervals, an exercise you rebuild quickly grows its gaps fast and one you keep
failing stays close.

Ratings come from what happened, not from a button:
  1 Again - failed the review (or needed the solution to solve it the first time)
  2 Hard  - got there with hints or after several tries
  3 Good  - solved it
  4 Easy  - rebuilt from memory in under a minute

Reference: https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm
"""

from __future__ import annotations

import math
import zlib
from datetime import date, timedelta

AGAIN, HARD, GOOD, EASY = 1, 2, 3, 4

# FSRS-4.5 default weights, fitted on a large public review dataset.
W = (0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031, 1.6474, 0.1367,
     1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755)
DECAY = -0.5
FACTOR = 19 / 81  # makes retrievability exactly 0.9 when elapsed days == stability
RETENTION = 0.9
MAX_INTERVAL = 365
EASY_SECONDS = 60


def _clamp_d(d: float) -> float:
    return min(10.0, max(1.0, d))


def initial_stability(rating: int) -> float:
    return W[rating - 1]


def initial_difficulty(rating: int) -> float:
    return _clamp_d(W[4] - (rating - 3) * W[5])


def retrievability(elapsed_days: float, stability: float) -> float:
    """Predicted chance of recalling it after ``elapsed_days``."""
    return (1 + FACTOR * max(elapsed_days, 0) / stability) ** DECAY


def next_difficulty(d: float, rating: int) -> float:
    d = d - W[6] * (rating - 3)
    return _clamp_d(W[7] * initial_difficulty(GOOD) + (1 - W[7]) * d)


def next_stability(d: float, s: float, r: float, rating: int) -> float:
    if rating == AGAIN:
        s_fail = W[11] * d ** -W[12] * ((s + 1) ** W[13] - 1) * math.exp(W[14] * (1 - r))
        return max(0.1, min(s_fail, s))
    hard = W[15] if rating == HARD else 1.0
    easy = W[16] if rating == EASY else 1.0
    growth = math.exp(W[8]) * (11 - d) * s ** -W[9] * (math.exp(W[10] * (1 - r)) - 1)
    return s * (growth * hard * easy + 1)


def interval(stability: float, key: str = "") -> int:
    """Days until recall falls to RETENTION, with a small stable per-item fuzz so exercises
    solved on the same day don't all come back on the same day."""
    days = stability / FACTOR * (RETENTION ** (1 / DECAY) - 1)
    if days > 2.5 and key:
        days *= 0.95 + 0.1 * (zlib.crc32(key.encode()) % 1000) / 1000
    return int(min(MAX_INTERVAL, max(1, round(days))))


def first_solve_rating(attempts: int, hints_used: int, revealed: bool) -> int:
    if revealed:
        return AGAIN
    if attempts == 1 and not hints_used:
        return GOOD
    return HARD


def review_rating(passed: bool, duration_s: int) -> int:
    if not passed:
        return AGAIN
    return EASY if 0 < duration_s < EASY_SECONDS else GOOD


def _memory(st: dict, today: date) -> tuple[float, float, float]:
    """Current (stability, difficulty, elapsed days), filling in rows scheduled before FSRS."""
    s, d = st.get("stability"), st.get("difficulty")
    last = st.get("last_review")
    if last:
        elapsed = (today - date.fromisoformat(last[:10])).days
    elif st.get("next_review"):  # pre-FSRS row: it was last seen interval_days before it fell due
        due = date.fromisoformat(st["next_review"][:10])
        elapsed = (today - due).days + int(st.get("interval_days") or 0)
    else:
        elapsed = 0
    if not s:
        s = max(float(st.get("interval_days") or 1), 0.5)
    if not d:
        d = _clamp_d(initial_difficulty(GOOD) + 0.5 * (st.get("lapses") or 0))
    return s, d, elapsed


def _schedule(st: dict, today: date, days: int) -> None:
    st["interval_days"] = days
    st["next_review"] = (today + timedelta(days=days)).isoformat()


def on_first_solve(st: dict, today: date | None = None) -> None:
    """Start the memory model for a freshly solved exercise (mutates ``st``)."""
    today = today or date.today()
    rating = first_solve_rating(st["attempts"], st.get("hints_used", 0), bool(st.get("revealed")))
    st["stability"] = initial_stability(rating)
    st["difficulty"] = initial_difficulty(rating)
    st["last_review"] = today.isoformat()
    _schedule(st, today, interval(st["stability"], st["exercise_id"]))


def on_review(st: dict, passed: bool, duration_s: int, today: date | None = None) -> int:
    """Update the memory model after a review check (mutates ``st``). Returns the rating used.

    Only the first check of a day is rated. A failure keeps the exercise due today until it is
    rebuilt; passing it later that day schedules it from the already-lowered stability.
    """
    today = today or date.today()
    if (st.get("last_review") or "")[:10] == today.isoformat():
        if passed:
            _schedule(st, today, interval(st["stability"], st["exercise_id"]))
        return 0
    s, d, elapsed = _memory(st, today)
    rating = review_rating(passed, duration_s)
    r = retrievability(elapsed, s)
    st["stability"] = next_stability(d, s, r, rating)
    st["difficulty"] = next_difficulty(d, rating)
    st["last_review"] = today.isoformat()
    if passed:
        _schedule(st, today, interval(st["stability"], st["exercise_id"]))
    else:
        st["interval_days"] = 0
        st["next_review"] = today.isoformat()
    return rating
