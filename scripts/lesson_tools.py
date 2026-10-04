#!/usr/bin/env python3
"""Authoring helpers for lesson prose and the ```diagram blocks inside it.

    python3 scripts/lesson_tools.py trace FILE.py            # JSON for a "trace" diagram, from a real run
    python3 scripts/lesson_tools.py recursion FILE.py FUNC   # JSON for a "recursion" diagram, from a real run
    python3 scripts/lesson_tools.py check [tNN_file.py ...]  # prose + diagram checks for topic files
    python3 scripts/lesson_tools.py apply tNN_file.py PATCH  # write new lesson/prompt/hints text into a topic file
    python3 scripts/lesson_tools.py path                     # the chapters in course order, with what each teaches
    python3 scripts/lesson_tools.py show tNN_file.py [id ..] # what the learner reads in each step, plus solution and check names

`trace` and `recursion` execute the code and record what Python actually did, so the diagram
cannot disagree with the interpreter. `check` re-runs every trace diagram to confirm that, and
runs the code inside every interactive lesson block (quiz, predict, fill, order, try, match;
see "v6" in CONTENT_GUIDE.md) so a block can never claim something Python does not do.
"""

import ast
import contextlib
import importlib.util
import io
import json
import os
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



# --------------------------------------------------------------------------- interactive blocks

INTERACTIVE = ("quiz", "predict", "fill", "order", "try", "match")
KNOWN_FENCES = {"", "python", "py", "diagram", "text", "bash", "sh", "json", "sql", "http", "toml", "ini", "yaml",
                "jsonl", "markdown", "md", "csv", "console", "diff", "xml", "html", *INTERACTIVE}
OPTION = re.compile(r"^- \[( |x|X)\] (.*)$")
UNSTABLE = re.compile(r"\b(random|time\.time|datetime\.now|datetime\.today|uuid|input\(|id\(|os\.getpid|perf_counter)")


def sections(body: str) -> list[str]:
    """Split a block body on lines that are exactly `---`."""
    parts, cur = [], []
    for line in body.split("\n"):
        if line.strip() == "---":
            parts.append("\n".join(cur))
            cur = []
        else:
            cur.append(line)
    parts.append("\n".join(cur))
    return [part.strip("\n") for part in parts]


def options(text: str) -> tuple[str, list[dict]]:
    """(text before the first option, options). An option is `- [x] label :: feedback`; a line that
    follows an option and is not an option itself continues that option's feedback."""
    head, opts = [], []
    for line in text.split("\n"):
        m = OPTION.match(line.strip())
        if m:
            label, _, why = m.group(2).partition(" :: ")
            opts.append({"ok": m.group(1) != " ", "label": label.strip(), "why": why.strip()})
        elif opts:
            if line.strip():
                opts[-1]["why"] = (opts[-1]["why"] + " " + line.strip()).strip()
        else:
            head.append(line)
    return "\n".join(head).strip(), opts


def run_py(code: str) -> tuple[int, str, str]:
    """(exit code, stdout, last stderr line) of a snippet, run the way the lesson Run button runs it."""
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=15, cwd="/tmp")
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
    err = r.stderr.strip().splitlines()
    return r.returncode, r.stdout, err[-1] if err else ""


def _check_options(where, opts, problems, lo=2, hi=5):
    if not lo <= len(opts) <= hi:
        problems.append(f"{where}: needs {lo}-{hi} options written as `- [ ] text :: feedback`, has {len(opts)}")
    if sum(o["ok"] for o in opts) != 1:
        problems.append(f"{where}: exactly one option must be marked `[x]`")
    if any(not o["label"] for o in opts) or len({o["label"] for o in opts}) != len(opts):
        problems.append(f"{where}: options must be non-empty and different from each other")
    if any(len(o["why"]) < 12 for o in opts):
        problems.append(f"{where}: every option needs feedback after ` :: ` that says WHY it is right or wrong")


def check_block(where, kind, body, problems):
    parts = sections(body)
    where = f"{where}: {kind} block"
    for ch in sorted(set(c for c in body if ord(c) > 127)):
        problems.append(f"{where} has a non-ASCII character {ch!r}")
    if kind == "quiz":
        if len(parts) != 1:
            problems.append(f"{where} must not contain `---`")
        question, opts = options(body)
        if len(question) < 8:
            problems.append(f"{where} needs a question before the options")
        _check_options(where, opts, problems)
    elif kind == "match":
        pairs = [line.partition(" :: ") for line in parts[0].split("\n") if line.strip()]
        if len(parts) > 2:
            problems.append(f"{where} has too many `---` sections (pairs, then an optional explanation)")
        if not 3 <= len(pairs) <= 6 or any(not a.strip() or not sep or not b.strip() for a, sep, b in pairs):
            problems.append(f"{where} needs 3-6 lines written as `left :: right`")
        elif len({a.strip() for a, _, _ in pairs}) != len(pairs) or len({b.strip() for _, _, b in pairs}) != len(pairs):
            problems.append(f"{where}: every left side and every right side must be different")
    elif kind == "predict":
        if len(parts) != 2 or len(parts[1].strip()) < 20:
            problems.append(f"{where} needs the code, a `---` line, then an explanation of the output")
            return
        code = parts[0]
        if not 1 <= len(code.split("\n")) <= 14:
            problems.append(f"{where}: keep the code to 14 lines or fewer")
        if UNSTABLE.search(code):
            problems.append(f"{where}: the code must print the same thing on every run (no random, time or input)")
        rc, out, err = run_py(code)
        if rc != 0:
            problems.append(f"{where}: the code must run without an error ({err}); use a quiz for 'which error?' questions")
        elif not out.strip() or len(out.strip().split("\n")) > 8:
            problems.append(f"{where}: the code must print 1-8 lines")
        elif run_py(code)[1] != out:
            problems.append(f"{where}: the output changes between runs")
    elif kind == "fill":
        if len(parts) not in (2, 3):
            problems.append(f"{where} needs the code with one `___`, a `---` line, the options, and optionally `---` plus an explanation")
            return
        code, (_, opts) = parts[0], options(parts[1])
        if code.count("___") != 1:
            problems.append(f"{where}: the code needs exactly one `___` gap, has {code.count('___')}")
            return
        _check_options(where, opts, problems, 2, 4)
        right = [o for o in opts if o["ok"]]
        if len(right) != 1:
            return
        rc, out, err = run_py(code.replace("___", right[0]["label"]))
        if rc != 0 or not out.strip():
            problems.append(f"{where}: with the right option the code must run and print something ({err or 'no output'})")
        for o in opts:
            if not o["ok"] and run_py(code.replace("___", o["label"]))[:2] == (rc, out):
                problems.append(f"{where}: the wrong option {o['label']!r} prints the same as the right one, so it is not wrong")
    elif kind == "order":
        if len(parts) != 2 or len(parts[1].strip()) < 20:
            problems.append(f"{where} needs the lines in the CORRECT order, a `---` line, then an explanation")
            return
        lines = [line for line in parts[0].split("\n") if line.strip()]
        if not 3 <= len(lines) <= 8 or len(set(lines)) != len(lines):
            problems.append(f"{where} needs 3-8 different lines of code (no blank lines)")
            return
        rc, out, err = run_py("\n".join(lines))
        if rc != 0 or not out.strip():
            problems.append(f"{where}: in the order written, the code must run and print something ({err or 'no output'})")
        elif run_py("\n".join(reversed(lines)))[:2] == (rc, out):
            problems.append(f"{where}: the reversed order prints the same thing, so the order does not matter")
    elif kind == "try":
        if len(parts) not in (3, 4) or len(parts[1].strip()) < 15:
            problems.append(f"{where} needs: starter code, `---`, the goal in words, `---`, solution code, and optionally `---` plus an explanation")
            return
        starter, solution = parts[0], parts[2]
        if max(len(starter.split("\n")), len(solution.split("\n"))) > 16:
            problems.append(f"{where}: keep starter and solution to 16 lines or fewer")
        if UNSTABLE.search(solution):
            problems.append(f"{where}: the solution must print the same thing on every run (no random, time or input)")
        rc, out, err = run_py(solution)
        if rc != 0 or not out.strip():
            problems.append(f"{where}: the solution must run and print something ({err or 'no output'})")
        elif run_py(starter)[:2] == (rc, out):
            problems.append(f"{where}: the starter already prints the target output, so there is nothing to do")


# --------------------------------------------------------------------------- check

FENCE = re.compile(r"^[ \t]*```(\w*)\n(.*?)^[ \t]*```[ \t]*$", re.S | re.M)
FROZEN = ("id", "title", "difficulty", "mode", "code", "solution", "tests", "starter", "placement",
          "impl", "mutants", "setup_files", "research", "concepts")


def _load(source: str, name: str):
    env = {}
    exec(compile(source, name, "exec"), env)
    return env


def _prose(md: str) -> str:
    return FENCE.sub("", md)


def _claimed_output(code: str):
    """The lines an example claims to print: its full-line `# ` comments, when it has any."""
    lines = [line[2:] if line.startswith("# ") else "" for line in code.split("\n") if line.startswith("#")]
    return lines or None


def check_text(where, text, problems, warnings, need_diagram=False, prose_only=False, need_check=False):
    text = textwrap.dedent(text)
    prose = _prose(text)
    for ch in sorted(set(c for c in prose if ord(c) > 127)):
        banned = ch in "–—―" or 0x2600 <= ord(ch) <= 0x27BF or ord(ch) >= 0x1F000
        (problems if banned else warnings).append(
            f"{where}: non-ASCII character {ch!r} (U+{ord(ch):04X}) in prose" + ("; no em dashes or emojis" if banned else ""))
    if prose_only:
        return
    diagrams = checks = 0
    for lang, body in FENCE.findall(text):
        body = textwrap.dedent(body).strip("\n")
        if lang == "diagram":
            diagrams += 1
            check_diagram(where, body, problems)
        elif lang in INTERACTIVE:
            checks += 1
            check_block(where, lang, body, problems)
        elif lang in ("python", "py"):
            rc, out, err = run_py(body)
            claimed = _claimed_output(body)
            if rc != 0:
                warnings.append(f"{where}: python example exits with an error (fine only if the lesson says so): {err or rc}")
            elif claimed is not None and [x.rstrip() for x in claimed] != [x.rstrip() for x in out.rstrip("\n").split("\n")]:
                warnings.append(f"{where}: the `# ` lines of an example are not what it prints. In lesson examples, keep "
                                f"full-line `# ` comments for output only. claimed {claimed} actual {out.rstrip().split(chr(10))}")
        elif lang not in KNOWN_FENCES:
            problems.append(f"{where}: unknown block type ```{lang}")
    if need_diagram and not diagrams:
        problems.append(f"{where}: no ```diagram block")
    if need_check:
        if not checks:
            problems.append(f"{where}: no interactive block (add at least one quiz, predict, fill, order, try or match)")
        lines = [line for line in text.strip().split("\n") if line.strip()]
        if not lines or not lines[0].startswith("## "):
            problems.append(f"{where}: must start with a `## ` heading")
        words = len(prose.split())
        if not 110 <= words <= 480:
            warnings.append(f"{where}: {words} words of prose (aim for 150-400)")
        first = next((p for p in re.split(r"\n\s*\n", prose.strip()) if p.strip() and not p.strip().startswith("#")), "")
        if "**" in first:
            warnings.append(f"{where}: the opening paragraph already introduces a bold term. Open with a situation, "
                            "a question or a tiny example, and name the term after the idea has landed.")


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


def _norm(code: str) -> str:
    return " ".join(code.replace("`", "").split()).lower()


def _solution_lines(ex) -> list[str]:
    """Lines of the reference solution that would give the answer away if quoted to the learner."""
    if ex.get("mode") in ("predict", "tests"):
        return []
    given = {_norm(line) for line in ex.get("starter", "").splitlines()}
    out = []
    for line in ex.get("solution", "").splitlines():
        n = _norm(line)
        if len(n) >= 12 and n not in given and not n.startswith(("def ", "class ", "import ", "from ", "#", "@", "print(")):
            out.append(n)
    return out


def check_file(path: Path):
    problems, warnings = [], []
    rel = path.relative_to(ROOT).as_posix()
    new = _load(path.read_text(), rel)
    old_src = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=ROOT)
    old = _load(old_src.stdout, rel) if old_src.returncode == 0 else None
    if old:
        if old["TOPIC"] != new["TOPIC"]:
            problems.append("TOPIC changed")
        if old.get("REFERENCE") != new.get("REFERENCE"):
            problems.append("REFERENCE changed (leave the Library cards alone)")
        if [e["id"] for e in old["EXERCISES"]] != [e["id"] for e in new["EXERCISES"]]:
            problems.append("exercise ids or order changed")
        for o, n in zip(old["EXERCISES"], new["EXERCISES"]):
            if list(o) != list(n):
                problems.append(f"{o['id']}: keys changed or reordered: {list(o)} -> {list(n)}")
            for key in FROZEN:
                if o.get(key) != n.get(key):
                    problems.append(f"{o['id']}: `{key}` changed (it must stay byte-identical)")
            if len(n.get("hints", [])) != 3:
                problems.append(f"{o['id']}: needs exactly 3 hints")
            if o.get("lesson") and n.get("lesson") == o.get("lesson"):
                problems.append(f"{o['id']}: lesson was not rewritten")
            if o.get("prompt") == n.get("prompt") and n.get("mode") != "predict":
                warnings.append(f"{o['id']}: prompt is unchanged. Fine only if a first-week learner would already "
                                "find it clear (see 'The task' in CONTENT_GUIDE.md v6)")
    check_text("LESSON", new.get("LESSON", ""), problems, warnings, need_diagram=True)
    for ex in new["EXERCISES"]:
        for key in ("lesson", "explanation"):
            if ex.get(key):
                check_text(f"{ex['id']}.{key}", ex[key], problems, warnings, need_check=key == "lesson")
        check_text(f"{ex['id']}.prompt", ex.get("prompt", ""), problems, warnings, prose_only=True)
        for i, hint in enumerate(ex.get("hints", [])):
            check_text(f"{ex['id']}.hints[{i}]", hint, problems, warnings, prose_only=True)
        # nothing shown to the learner may contain the answer
        for line in _solution_lines(ex):
            for i, hint in enumerate(ex.get("hints", [])):
                if line in _norm(hint):
                    problems.append(f"{ex['id']}.hints[{i}]: quotes a line of the solution ({line!r}). Describe the step in words.")
            if line in _norm(ex.get("prompt", "")):
                problems.append(f"{ex['id']}.prompt: contains a line of the solution ({line!r})")
            if line in _norm(ex.get("lesson", "")):
                warnings.append(f"{ex['id']}.lesson: contains a line of this step's solution ({line!r}). "
                                "Teach the idea with different names and data.")
        if ex.get("mode") == "predict" and ex.get("lesson") and _norm(ex.get("code", "")) in _norm(ex["lesson"]):
            problems.append(f"{ex['id']}.lesson: contains the exact program the learner must predict")
    return problems, warnings


# --------------------------------------------------------------------------- apply

PATCH_HEAD = re.compile(r"^@@ +([\w-]+)(?: +(\w+))? *$")
TEXT_FIELDS = ("lesson", "prompt", "explanation")


def parse_patch(text: str) -> list[tuple[str, str, str]]:
    """A patch is plain text. `@@ <exercise-id> <field>` (or `@@ LESSON`) starts a section and the lines
    after it are the new value. For `hints`, write the three hints separated by `---` lines."""
    out, cur = [], None
    for line in text.split("\n"):
        m = PATCH_HEAD.match(line)
        if m:
            cur = [m.group(1), m.group(2) or "", []]
            out.append(cur)
        elif cur is not None:
            cur[2].append(line)
        elif line.strip():
            raise SystemExit(f"patch must start with an `@@ <exercise-id> <field>` line, found: {line!r}")
    return [(a, b, "\n".join(lines).strip("\n")) for a, b, lines in out]


def apply_patch(path: Path, patch: str) -> list[str]:
    """Replace only the named fields, in place. Refuses anything that would leave the file broken."""
    src = path.read_text()
    tree = ast.parse(src)
    starts = [0]
    for line in src.split("\n"):
        starts.append(starts[-1] + len(line) + 1)
    at = lambda line, col: starts[line - 1] + col
    targets = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "LESSON":
            targets[("LESSON", "")] = (node.value, node.col_offset)
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "EXERCISES":
            for d in node.value.elts:
                keys = {k.value: (k, v) for k, v in zip(d.keys, d.values)}
                for name, (k, v) in keys.items():
                    targets[(keys["id"][1].value, name)] = (v, k.col_offset)
    edits, done = [], []
    diagrams = None
    for ex_id, field, text in parse_patch(patch):
        if "%%diagram" in text:
            # `%%diagram <exercise-id> <n>%%` on a line of its own stands for the n-th (0-based) diagram
            # block of that exercise's lesson in the last commit, so existing diagrams need no retyping.
            if diagrams is None:
                rel = path.relative_to(ROOT).as_posix()
                old_src = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=ROOT)
                old_env = _load(old_src.stdout, rel) if old_src.returncode == 0 else {"EXERCISES": []}
                diagrams = {e["id"]: [m.group(0) for m in re.finditer(r"^```diagram\n.*?^```[ \t]*$", textwrap.dedent(e.get("lesson", "")), re.S | re.M)]
                            for e in old_env["EXERCISES"]}
            def _fill(m):
                found = diagrams.get(m.group(1), [])
                if int(m.group(2)) >= len(found):
                    raise SystemExit(f"@@ {ex_id} {field}: no diagram {m.group(2)} in the old lesson of {m.group(1)} (it has {len(found)})")
                return found[int(m.group(2))]
            text = re.sub(r"^%%diagram ([\w-]+) (\d+)%%[ \t]*$", _fill, text, flags=re.M)
        if (ex_id, field) not in targets:
            raise SystemExit(f"@@ {ex_id} {field}: no such field in {path.name} (a field can be replaced, not added)")
        if ex_id != "LESSON" and field not in (*TEXT_FIELDS, "hints"):
            raise SystemExit(f"@@ {ex_id} {field}: only lesson, prompt, explanation and hints may be rewritten")
        if "\'\'\'" in text or not text.strip():
            raise SystemExit(f"@@ {ex_id} {field}: text is empty or contains three single quotes in a row")
        node, col = targets[(ex_id, field)]
        pad = " " * col
        if field == "hints":
            hints = [" ".join(h.split()) for h in sections(text)]
            if len(hints) != 3 or not all(hints):
                raise SystemExit(f"@@ {ex_id} hints: write exactly 3 hints separated by `---` lines")
            literal = "[\n" + "".join(f"{pad}    {json.dumps(h)},\n" for h in hints) + pad + "]"
        else:
            body = "\n".join((pad + "    " + line).rstrip() if ex_id != "LESSON" else line for line in text.split("\n"))
            literal = "r\'\'\'\n" + body + "\n" + (pad if ex_id != "LESSON" else "") + "\'\'\'"
        edits.append((at(node.lineno, node.col_offset), at(node.end_lineno, node.end_col_offset), literal))
        done.append(f"{ex_id} {field}".strip())
    for start, end, literal in sorted(edits, reverse=True):
        src = src[:start] + literal + src[end:]
    compile(src, path.name, "exec")
    tmp = path.with_suffix(".py.tmp")
    tmp.write_text(src)
    os.replace(tmp, path)
    return done


def course_path() -> str:
    sys.path.insert(0, str(ROOT))
    from pytrainer import content
    data = content.load()
    lines = []
    for n, t in enumerate(data["topics"], 1):
        mod = data["modules_by_id"][t["track"]]["title"]
        steps = [data["exercises"][e] for e in t["exercise_ids"]]
        lines.append(f"{n:2}. {t['id']} ({mod}): {', '.join(t.get('concepts', []))}")
        lines.append("      steps: " + " | ".join(f"{e['id']} {e['title']!r}" for e in steps if e.get("lesson")))
    return "\n".join(lines)


def show(path: Path, ids: list[str]) -> str:
    """A compact view of a chapter for rewriting: everything the learner reads, the starter, the solution
    and the names of the checks (the test bodies are left out)."""
    env = _load(path.read_text(), path.name)
    out = []
    for ex in env["EXERCISES"]:
        if ids and ex["id"] not in ids:
            continue
        out.append(f"\n{'=' * 100}\n{ex['id']} | {ex['title']!r} | difficulty {ex['difficulty']} | mode {ex.get('mode', 'function')}"
                   + (" | PLACEMENT" if ex.get("placement") else "") + (" | has research note" if ex.get("research") else ""))
        for key in ("lesson", "prompt", "code", "explanation", "starter", "solution", "impl"):
            if ex.get(key, "").strip():
                out.append(f"--- {key}\n" + textwrap.dedent(ex[key]).strip("\n"))
        if ex.get("setup_files"):
            out.append("--- setup_files: " + ", ".join(ex["setup_files"]))
        names = re.findall(r"^\s*def (test_\w+)", ex.get("tests", ""), re.M)
        if names:
            out.append("--- checks: " + "; ".join(n.removeprefix("test_").replace("_", " ") for n in names))
        if ex.get("mutants"):
            out.append("--- mutants: " + "; ".join(m["name"] for m in ex["mutants"]))
        out.append("--- hints\n" + "\n".join(f"{i + 1}. {' '.join(h.split())}" for i, h in enumerate(ex.get("hints", []))))
    return "\n".join(out)


def main(argv):
    if len(argv) >= 2 and argv[0] == "trace":
        print(dump(make_trace(Path(argv[1]).read_text())))
    elif len(argv) >= 3 and argv[0] == "recursion":
        print(dump(make_recursion(Path(argv[1]).read_text(), argv[2])))
    elif len(argv) >= 3 and argv[0] == "apply":
        path = TOPICS / Path(argv[1]).name
        done = []
        for patch in argv[2:]:
            done += apply_patch(path, Path(patch).read_text())
        print(f"{path.name}: replaced {len(done)} fields: {', '.join(done)}")
    elif len(argv) >= 2 and argv[0] == "show":
        print(show(TOPICS / Path(argv[1]).name, argv[2:]))
    elif argv and argv[0] == "path":
        print(course_path())
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
