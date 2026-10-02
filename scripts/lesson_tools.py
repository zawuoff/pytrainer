#!/usr/bin/env python3
"""Authoring helpers for lesson prose and the ```diagram blocks inside it.

    python3 scripts/lesson_tools.py trace FILE.py            # JSON for a "trace" diagram, from a real run
    python3 scripts/lesson_tools.py recursion FILE.py FUNC   # JSON for a "recursion" diagram, from a real run
    python3 scripts/lesson_tools.py check [tNN_file.py ...]  # prose + diagram checks for topic files

`trace` and `recursion` execute the code and record what Python actually did, so the diagram
cannot disagree with the interpreter. `check` re-runs every trace diagram to confirm that.
"""

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import textwrap
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ROOT / "pytrainer" / "content" / "topics"
FILENAME = "<lesson>"
MAX_STEPS = 45
HIDDEN = (types.ModuleType, types.FunctionType, types.BuiltinFunctionType, type)

DIAGRAM_KEYS = {
    "list-index": ({"items"}, {"name", "index"}),
    "string-index": ({"value"}, {"name", "index"}),
    "slice": (set(), {"name", "items", "value", "start", "stop", "step"}),
    "alias-copy": (set(), {"a", "b", "items", "mode", "append"}),
    "dict": ({"entries"}, {"name"}),
    "stack-queue": (set(), {"mode", "name", "items", "push"}),
    "trace": ({"code", "steps"}, set()),
    "loop-trace": ({"code", "steps"}, set()),
    "recursion": ({"root"}, set()),
    "set-ops": ({"a", "b"}, {"op"}),
    "flow": ({"steps"}, {"loop"}),
    "vectors": (set(), {"a", "b"}),
    "chunks": ({"text"}, {"size", "overlap", "unit", "max_size"}),
}


class TooLong(Exception):
    pass


def _short(value):
    text = repr(value)
    return text if len(text) <= 70 else text[:67] + "..."


def _visible(scope):
    return {k: _short(v) for k, v in scope.items() if not k.startswith("__") and not isinstance(v, HIDDEN)}


def make_trace(code: str, max_steps: int = MAX_STEPS) -> dict:
    """Run `code`; one step per line event: the line about to run, the variables, the output so far."""
    out, steps = io.StringIO(), []

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FILENAME:
            return None
        if event == "line":
            if len(steps) >= max_steps:
                raise TooLong(f"more than {max_steps} steps; use a smaller example")
            scope = frame.f_globals if frame.f_code.co_name == "<module>" else frame.f_locals
            steps.append({"line": frame.f_lineno, "vars": _visible(scope), "out": out.getvalue()})
        return tracer

    env = {"__name__": "__main__"}
    compiled = compile(code, FILENAME, "exec")
    error = None
    with contextlib.redirect_stdout(out):
        sys.settrace(tracer)
        try:
            exec(compiled, env)
        except TooLong:
            raise
        except Exception as exc:  # the lesson may be about an error on purpose
            error = f"{type(exc).__name__}: {exc}"
        finally:
            sys.settrace(None)
    last = {"line": None, "vars": _visible(env), "out": out.getvalue()}
    if error:
        last["error"] = error
    steps.append(last)
    return {"type": "trace", "title": "", "code": code.rstrip("\n").split("\n"), "steps": steps}


def make_recursion(code: str, func: str) -> dict:
    """Run `code`; record every call of `func` made at any depth as a tree of calls and return values."""
    roots, stack = [], []

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FILENAME or frame.f_code.co_name != func:
            return None
        if event == "call":
            names = frame.f_code.co_varnames[:frame.f_code.co_argcount]
            node = {"call": f"{func}({', '.join(_short(frame.f_locals[n]) for n in names)})", "ret": "None", "children": []}
            (stack[-1]["children"] if stack else roots).append(node)
            stack.append(node)
        elif event == "return":
            stack.pop()["ret"] = _short(arg)
        return tracer

    with contextlib.redirect_stdout(io.StringIO()):
        sys.settrace(tracer)
        try:
            exec(compile(code, FILENAME, "exec"), {"__name__": "__main__"})
        finally:
            sys.settrace(None)
    if len(roots) != 1:
        raise SystemExit(f"expected exactly one top-level call of {func}(), found {len(roots)}")
    return {"type": "recursion", "title": "", "root": roots[0]}


def dump(spec: dict) -> str:
    """Compact JSON with one step per line, so a diagram block stays readable in a lesson."""
    if spec["type"] != "trace":
        return json.dumps(spec, ensure_ascii=False)
    head = {k: v for k, v in spec.items() if k != "steps"}
    lines = [json.dumps(head, ensure_ascii=False)[:-1] + ', "steps": [']
    lines += ["  " + json.dumps(s, ensure_ascii=False) + ("," if i < len(spec["steps"]) - 1 else "")
              for i, s in enumerate(spec["steps"])]
    return "\n".join(lines + ["]}"])


# --------------------------------------------------------------------------- check

FENCE = re.compile(r"^[ \t]*```(\w*)\n(.*?)^[ \t]*```[ \t]*$", re.S | re.M)
FIGURES = re.compile(r"\b(think of|imagine|picture (a|an|the|it|this)|as if|just like|kind of like|sort of like|"
                     r"(is|are|acts?|works?|behaves?|looks?|feels?) (a bit |a lot |much |just |exactly )?like (a|an|the)\b|"
                     r"metaphor|analogy|under the hood|magic)", re.I)
FROZEN = ("id", "title", "difficulty", "mode", "code", "solution", "tests", "starter", "placement",
          "impl", "mutants", "setup_files", "research", "concepts")


def _load(source: str, name: str):
    env = {}
    exec(compile(source, name, "exec"), env)
    return env


def _prose(md: str) -> str:
    return FENCE.sub("", md)


def check_text(where, text, problems, warnings, need_diagram=False, prose_only=False):
    text = textwrap.dedent(text)
    prose = _prose(text)
    for ch in sorted(set(c for c in prose if ord(c) > 127)):
        banned = ch in "\u2013\u2014\u2015" or 0x2600 <= ord(ch) <= 0x27BF or ord(ch) >= 0x1F000
        (problems if banned else warnings).append(
            f"{where}: non-ASCII character {ch!r} (U+{ord(ch):04X}) in prose" + ("; no em dashes or emojis" if banned else ""))
    if prose_only:
        return
    for m in FIGURES.finditer(prose):
        warnings.append(f"{where}: possible metaphor or figure of speech: ...{prose[max(0, m.start() - 30):m.end() + 30]!r}...")
    diagrams = 0
    for lang, body in FENCE.findall(text):
        body = textwrap.dedent(body)
        if lang == "diagram":
            diagrams += 1
            check_diagram(where, body, problems)
        elif lang in ("python", "py"):
            r = subprocess.run([sys.executable, "-c", body], capture_output=True, text=True, timeout=20, cwd="/tmp")
            if r.returncode != 0:
                warnings.append(f"{where}: python example exits with an error (fine only if the lesson says so): "
                                f"{r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
    if need_diagram and not diagrams:
        problems.append(f"{where}: no ```diagram block")


def check_diagram(where, body, problems):
    try:
        spec = json.loads(body)
    except json.JSONDecodeError as exc:
        problems.append(f"{where}: diagram is not valid JSON ({exc})")
        return
    kind = spec.get("type")
    if kind not in DIAGRAM_KEYS:
        problems.append(f"{where}: unknown diagram type {kind!r}")
        return
    required, optional = DIAGRAM_KEYS[kind]
    keys = set(spec) - {"type", "title"}
    if required - keys:
        problems.append(f"{where}: {kind} diagram is missing {sorted(required - keys)}")
    if keys - required - optional:
        problems.append(f"{where}: {kind} diagram has unknown keys {sorted(keys - required - optional)}")
    if not spec.get("title"):
        problems.append(f"{where}: {kind} diagram needs a non-empty title")
    for ch in sorted(set(c for c in body if ord(c) > 127)):
        problems.append(f"{where}: non-ASCII character {ch!r} in diagram")
    if kind in ("trace", "loop-trace") and required <= keys:
        code = spec["code"] if isinstance(spec["code"], str) else "\n".join(spec["code"])
        try:
            real = make_trace(code)["steps"]
        except Exception as exc:
            problems.append(f"{where}: trace code cannot be traced ({exc})")
            return
        got = [{k: s.get(k) for k in ("line", "vars", "out", "error") if k in s} for s in spec["steps"]]
        if got != real:
            problems.append(f"{where}: trace steps differ from what Python really does; regenerate with `lesson_tools.py trace`")
    if kind == "flow":
        for s in spec.get("steps", []):
            if not (isinstance(s, dict) and s.get("label") and s.get("detail")) or set(s) - {"label", "detail", "code"}:
                problems.append(f"{where}: each flow step needs label and detail (optional code)")
                break
        if len(spec.get("steps", [])) < 3:
            problems.append(f"{where}: a flow diagram needs at least 3 steps")
    if kind == "dict" and not all(isinstance(e, list) and len(e) == 2 for e in spec.get("entries", [])):
        problems.append(f"{where}: dict entries must be [key, value] pairs")
    if kind == "set-ops" and not all(isinstance(spec.get(k), dict) and isinstance(spec[k].get("items"), list) for k in "ab"):
        problems.append(f"{where}: set-ops needs a and b as {{name, items}}")


def check_file(path: Path):
    problems, warnings = [], []
    rel = path.relative_to(ROOT).as_posix()
    new = _load(path.read_text(), rel)
    old_src = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=ROOT)
    old = _load(old_src.stdout, rel) if old_src.returncode == 0 else None
    if old:
        if old["TOPIC"] != new["TOPIC"]:
            problems.append("TOPIC changed")
        if [e["id"] for e in old["EXERCISES"]] != [e["id"] for e in new["EXERCISES"]]:
            problems.append("exercise ids or order changed")
        for o, n in zip(old["EXERCISES"], new["EXERCISES"]):
            if list(o) != list(n):
                problems.append(f"{o['id']}: keys changed or reordered: {list(o)} -> {list(n)}")
            for key in FROZEN:
                if o.get(key) != n.get(key):
                    problems.append(f"{o['id']}: `{key}` changed (it must stay byte-identical)")
            for key in ("prompt", "hints"):
                if o.get(key) != n.get(key):
                    warnings.append(f"{o['id']}: `{key}` changed (allowed only to remove a metaphor, emoji or em dash)")
            if len(n.get("hints", [])) != 3:
                problems.append(f"{o['id']}: needs exactly 3 hints")
            if o.get("lesson") and n.get("lesson") == o.get("lesson"):
                problems.append(f"{o['id']}: lesson was not rewritten")
    if old and old.get("LESSON") == new.get("LESSON"):
        problems.append("LESSON was not rewritten")
    check_text("LESSON", new.get("LESSON", ""), problems, warnings, need_diagram=True)
    for ex in new["EXERCISES"]:
        for key in ("lesson", "explanation"):
            if ex.get(key):
                check_text(f"{ex['id']}.{key}", ex[key], problems, warnings)
        check_text(f"{ex['id']}.prompt", ex.get("prompt", ""), problems, warnings, prose_only=True)
        for i, hint in enumerate(ex.get("hints", [])):
            check_text(f"{ex['id']}.hints[{i}]", hint, problems, warnings, prose_only=True)
    return problems, warnings


def main(argv):
    if len(argv) >= 2 and argv[0] == "trace":
        print(dump(make_trace(Path(argv[1]).read_text())))
    elif len(argv) >= 3 and argv[0] == "recursion":
        print(dump(make_recursion(Path(argv[1]).read_text(), argv[2])))
    elif argv and argv[0] == "check":
        paths = [TOPICS / Path(a).name for a in argv[1:]] or sorted(TOPICS.glob("t*.py"))
        bad = 0
        for path in paths:
            problems, warnings = check_file(path)
            bad += len(problems)
            print(f"{path.name}: {len(problems)} problems, {len(warnings)} warnings")
            for p in problems:
                print("  PROBLEM", p)
            for w in warnings:
                print("  warning", w)
        return 1 if bad else 0
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
