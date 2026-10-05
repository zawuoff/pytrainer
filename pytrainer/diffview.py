"""The "Why did it fail?" view: expected and actual side by side, differences highlighted.

The test harness records both sides of a failed `assert actual == expected` (see runner.HARNESS).
`build()` turns them into rows for the results panel: lines are aligned with difflib, and within a
changed line the differing characters are marked, so a missing space or a wrong letter stands out.
Short values that the failure message already shows (3 vs 4) get no diff, unless their types differ,
which is the usual "3" vs 3 surprise.
"""

from __future__ import annotations

import difflib

MAX_ROWS = 120
CONTEXT = 1


def _chars(a: str, b: str) -> tuple[list, list]:
    """Segments [text, changed] for each side of a pair of differing lines."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    left, right = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if a[i1:i2]:
            left.append([a[i1:i2], tag != "equal"])
        if b[j1:j2]:
            right.append([b[j1:j2], tag != "equal"])
    return left, right


def _a(word: str) -> str:
    return ("an " if word[:1].lower() in "aeiou" else "a ") + word


def _note(expected: str, actual: str, kind: str, types: list[str]) -> str | None:
    if types and len(types) == 2 and types[0] != types[1]:
        return f"Different types: expected {_a(types[0])}, your code gave {_a(types[1])}."
    if kind == "text":
        if expected.rstrip("\n") == actual.rstrip("\n"):
            return "Only the newlines at the end differ."
        if "".join(expected.split()) == "".join(actual.split()):
            return "Only spaces, tabs or line breaks differ."
        if expected.lower() == actual.lower():
            return "Only upper and lower case differ."
    return None


def build(raw: dict | None, message: str = "") -> dict | None:
    """Rows for the results panel, or None when a diff wouldn't add anything to the message."""
    if not raw:
        return None
    expected, actual = str(raw.get("expected", "")), str(raw.get("actual", ""))
    kind, types = raw.get("kind", "repr"), raw.get("types") or []
    if expected == actual:
        return None
    note = _note(expected, actual, kind, types)
    short = "\n" not in expected + actual and len(expected) <= 24 and len(actual) <= 24
    if kind == "repr" and short and not note and expected in message and actual in message:
        return None
    exp_lines, act_lines = expected.split("\n"), actual.split("\n")
    rows: list[dict] = []
    sm = difflib.SequenceMatcher(None, exp_lines, act_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            rows += [{"t": "same", "e": [[line, False]], "a": [[line, False]]} for line in exp_lines[i1:i2]]
            continue
        n = max(i2 - i1, j2 - j1)
        for k in range(n):
            e = exp_lines[i1 + k] if i1 + k < i2 else None
            a = act_lines[j1 + k] if j1 + k < j2 else None
            if e is not None and a is not None:
                left, right = _chars(e, a)
                rows.append({"t": "change", "e": left or [["", False]], "a": right or [["", False]]})
            elif e is not None:
                rows.append({"t": "missing", "e": [[e, True]], "a": None})
            else:
                rows.append({"t": "extra", "e": None, "a": [[a, True]]})
    # Keep a line of context around each change; fold long unchanged stretches.
    keep = [any(rows[j]["t"] != "same" for j in range(max(0, i - CONTEXT), min(len(rows), i + CONTEXT + 1)))
            for i in range(len(rows))]
    folded: list[dict] = []
    for row, k in zip(rows, keep):
        if k:
            folded.append(row)
        elif folded and folded[-1]["t"] == "skip":
            folded[-1]["n"] += 1
        else:
            folded.append({"t": "skip", "n": 1})
    return {"kind": kind, "note": note, "rows": folded[:MAX_ROWS], "truncated": len(folded) > MAX_ROWS}
