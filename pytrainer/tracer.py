"""Step-through debugger: run learner code under ``sys.settrace`` and record every step.

The program runs in the same sandbox, temp dir and limits as ``runner.run_code``. Each step
records the line about to run (or a call / return / exception), the call stack with each
frame's variables, and how much had been printed so far. Only the learner's own code is
traced: library code runs at full speed and never shows up as steps.

Function-only exercises print nothing when run, so a "call" can be added: one expression or a
few statements run after the file (``count_tokens("hi there")``). ``suggest_call`` picks one
from the exercise's own tests.
"""

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import runner, sandbox

MAX_STEPS = 800

TRACER = r'''
import builtins, io, json, os, sys, types

RESULTS, MAIN, MAX_STEPS = sys.argv[1], os.path.abspath(sys.argv[2]), int(sys.argv[3])
CALL_NAME = "<your call>"
FILES = {MAIN: "main", CALL_NAME: "call"}
REPR_LEN, MAX_VARS, MAX_FRAMES, DUMP_EVERY = 120, 40, 12, 100

with open("_call.py", encoding="utf-8") as fh:
    CALL = fh.read()
with open("_stdin.txt", encoding="utf-8") as fh:
    sys.stdin = io.StringIO(fh.read())
out = io.StringIO()
real_stdout = sys.stdout
state = {"steps": [], "stdout": "", "error": None, "truncated": False, "result": None}


def dump():
    state["stdout"] = out.getvalue()[-20000:]
    with open(RESULTS, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def show(value):
    try:
        text = repr(value)
    except Exception as exc:  # a learner class with a broken __repr__
        text = "<repr failed: %s>" % type(exc).__name__
    return text if len(text) <= REPR_LEN else text[:REPR_LEN - 1] + "…"


def variables(names, is_module):
    rows = []
    for name, value in names.items():
        if name.startswith("__") or isinstance(value, types.ModuleType):
            continue
        if is_module and name in ("In", "Out"):
            continue
        if isinstance(value, types.FunctionType):
            rows.append([name, "function", "function %s()" % value.__name__])
        elif isinstance(value, type):
            rows.append([name, "class", "class %s" % value.__name__])
        else:
            rows.append([name, type(value).__name__, show(value)])
        if len(rows) >= MAX_VARS:
            break
    return rows


def stack(frame):
    frames = []
    while frame is not None:
        where = FILES.get(frame.f_code.co_filename)
        if where:
            is_module = frame.f_code.co_name == "<module>"
            frames.append({"name": "Global" if is_module else frame.f_code.co_name + "()", "file": where,
                           "line": frame.f_lineno, "vars": variables(frame.f_locals, is_module)})
        frame = frame.f_back
    frames.reverse()
    return frames[-MAX_FRAMES:]


seen_exc = set()


def record(frame, event, arg):
    if event == "call" and frame.f_code.co_name == "<module>":
        return  # "the file starts" is not a step anyone needs to see
    step = {"event": event, "file": FILES[frame.f_code.co_filename], "line": frame.f_lineno,
            "func": frame.f_code.co_name, "stack": stack(frame), "out": len(out.getvalue())}
    if event == "return":
        step["value"] = show(arg)
    elif event == "exception":
        exc = arg[1]
        if id(exc) in seen_exc:
            return
        seen_exc.add(id(exc))
        step["value"] = "%s: %s" % (type(exc).__name__, exc)
    state["steps"].append(step)
    if len(state["steps"]) >= MAX_STEPS:
        sys.settrace(None)
        state["truncated"] = True
        dump()
        os._exit(0)
    if len(state["steps"]) % DUMP_EVERY == 0:
        dump()


def tracer(frame, event, arg):
    if frame.f_code.co_filename not in FILES:
        return None
    record(frame, event, arg)
    return tracer


def describe(exc):
    tb, line = exc.__traceback__, None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename in FILES:
            line = (FILES[tb.tb_frame.f_code.co_filename], tb.tb_lineno)
        tb = tb.tb_next
    text = "%s: %s" % (type(exc).__name__, exc)
    if line:
        text += " (in your call, line %d)" % line[1] if line[0] == "call" else " (line %d)" % line[1]
    return text


def main():
    ns = {"__name__": "__main__", "__file__": MAIN, "__builtins__": builtins}
    with open(MAIN, encoding="utf-8") as fh:
        source = fh.read()
    try:
        code = compile(source, MAIN, "exec")
        call_code, call_is_expr = None, False
        if CALL.strip():
            try:
                call_code, call_is_expr = compile(CALL, CALL_NAME, "eval"), True
            except SyntaxError:
                call_code = compile(CALL, CALL_NAME, "exec")
    except SyntaxError as exc:
        where = "your call" if exc.filename == CALL_NAME else "line %s" % exc.lineno
        state["error"] = "SyntaxError (%s): %s" % (where, exc.msg)
        dump()
        return
    sys.stdout = out
    sys.settrace(tracer)
    try:
        exec(code, ns)
        if call_code is not None:
            if call_is_expr:
                value = eval(call_code, ns)
                state["result"] = show(value)
            else:
                exec(call_code, ns)
    except SystemExit:
        pass
    except BaseException as exc:
        state["error"] = describe(exc)
    finally:
        sys.settrace(None)
        sys.stdout = real_stdout
    dump()


main()
'''


def trace_code(files: dict[str, str], *, main: str = "solution.py", call: str = "", stdin: str = "",
               setup_files: dict | None = None, timeout: float = 10, max_steps: int = MAX_STEPS) -> dict:
    """Run ``main`` (then ``call``, if given) step by step. Never raises for learner errors."""
    tmp = Path(tempfile.mkdtemp(prefix="pytrainer-trace-"))
    try:
        runner._write_files(tmp, setup_files or {})
        runner._write_files(tmp, files)
        (tmp / "_tracer.py").write_text(TRACER, encoding="utf-8")
        (tmp / "_call.py").write_text(call or "", encoding="utf-8")
        (tmp / "_stdin.txt").write_text(stdin or "", encoding="utf-8")
        results = tmp / "_trace.json"
        proc = subprocess.Popen(
            sandbox.wrap([runner.PYTHON, "-X", "utf8", "_tracer.py", str(results), main, str(max_steps)], tmp),
            cwd=tmp, env=runner._env(str(tmp)), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", **runner._spawn_opts(timeout),
        )
        timed_out = False
        try:
            _, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            runner._kill(proc)
            _, stderr = proc.communicate()
        try:
            state = json.loads(results.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {"steps": [], "stdout": "", "error": None, "truncated": False, "result": None}
        if timed_out:
            state["error"] = (state.get("error") or
                              "Time limit reached. Showing the steps recorded before it stopped.")
            state["truncated"] = True
        elif proc.returncode and not state["steps"] and not state.get("error"):
            state["error"] = ("The debugger crashed.\n" + (stderr or "")[-1500:]).strip()
        state["max_steps"] = max_steps
        return state
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _defined_functions(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    return names


def _calls_anything(source: str) -> bool:
    """True if running the file does something visible: calls at top level, loops, a main guard.

    Definitions, imports and assignments (constants, compiled regexes) don't count."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return True
    quiet = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom,
             ast.Assign, ast.AnnAssign, ast.Pass)
    for node in tree.body:
        if isinstance(node, quiet):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):  # docstring
            continue
        return True
    return False


def _literal(node: ast.AST) -> bool:
    try:
        ast.literal_eval(node)
        return True
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return False


class _Inline(ast.NodeTransformer):
    """Replace names bound to literals earlier in the test, and ``solution.f`` with ``f``."""

    def __init__(self, env: dict):
        self.env = env

    def visit_Name(self, node):
        return self.env.get(node.id, node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "solution":
            return ast.Name(id=node.attr, ctx=ast.Load())
        return self.generic_visit(node)


def _bind_literal(stmt: ast.AST, env: dict) -> None:
    """Record ``name = <literal>``, inlining names already known (``[SYS, U1]``)."""
    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
        value = _Inline(env).visit(ast.parse(ast.unparse(stmt.value), mode="eval").body)
        if _literal(value):
            env[stmt.targets[0].id] = value


def _calls_in(func: ast.FunctionDef, names: set[str], module_env: dict):
    env = dict(module_env)
    for stmt in func.body:
        _bind_literal(stmt, env)
        for node in ast.walk(stmt):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name)
                and fn.value.id == "solution" else None)
            if name not in names or not (node.args or node.keywords):
                continue
            call = _Inline(env).visit(ast.parse(ast.unparse(node), mode="eval").body)
            if all(_literal(a) for a in call.args) and all(k.arg and _literal(k.value) for k in call.keywords):
                yield ast.unparse(call)


def suggest_call(solution: str, tests: str) -> str:
    """A call to try in the debugger: the first call in the tests to a function the solution
    defines whose arguments are (or are set earlier in that test to) plain literals."""
    if _calls_anything(solution):
        return ""
    names = _defined_functions(solution)
    if not names:
        return ""
    try:
        tree = ast.parse(tests or "")
    except SyntaxError:
        return ""
    module_env: dict[str, ast.AST] = {}
    for stmt in tree.body:
        _bind_literal(stmt, module_env)
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    found = [text for func in funcs for text in _calls_in(func, names, module_env)]
    # The richest call that still reads at a glance: empty inputs make dull walk-throughs.
    short = [t for t in found if len(t) <= 90]
    return max(short, key=len) if short else min(found, key=len, default="")
