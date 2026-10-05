"""Execute learner code in an isolated subprocess and grade it against tests.

Tests are plain Python source containing ``test_*`` functions. They run inside
``_harness.py`` next to the learner's files, in a throwaway temp directory, with
CPU / memory / file-size limits and a wall-clock timeout, inside the OS sandbox that
``sandbox`` picks (no network, read-only filesystem) when the machine has one.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

try:
    import resource
except ImportError:  # Windows: no rlimits, only the wall-clock timeout applies
    resource = None

from . import sandbox

PYTHON = sys.executable or "python3"
MAX_OUTPUT = 20_000

HARNESS = r'''
import sys, os, io, json, types, traceback, contextlib, subprocess, importlib, time, builtins

RESULTS = sys.argv[1]
TESTS_FILE = sys.argv[2]
MODE = sys.argv[3]
MAIN = sys.argv[4]
sys.path.insert(0, os.getcwd())
os.environ.pop("PYTHONSTARTUP", None)

state = {"tests": [], "load_error": None, "stdout": "", "running": None}

def dump():
    with open(RESULTS, "w") as fh:
        json.dump(state, fh)

_out = io.StringIO()

def _user_frames(tb):
    """Return (file, line, source) for frames that belong to learner files."""
    frames = []
    for fs in traceback.extract_tb(tb):
        name = os.path.basename(fs.filename)
        if fs.filename.startswith(os.getcwd()) and not name.startswith("_"):
            frames.append((name, fs.lineno, (fs.line or "").strip()))
    return frames

def _test_line(tb):
    for fs in reversed(traceback.extract_tb(tb)):
        if os.path.basename(fs.filename) == "_tests.py":
            return (fs.line or "").strip()
    return ""

def describe(exc, tb):
    if isinstance(exc, AssertionError):
        msg = str(exc).strip()
        line = _test_line(tb)
        if msg:
            return msg
        return "Check failed: " + line if line else "Assertion failed"
    text = f"{type(exc).__name__}: {exc}"
    frames = _user_frames(tb)
    if frames:
        f, ln, src = frames[-1]
        text += f"\n  raised at {f} line {ln}: {src}"
    else:
        line = _test_line(tb)
        if line:
            text += f"\n  while running: {line}"
    return text

class ScriptResult:
    def __init__(self, cp):
        self.stdout = cp.stdout
        self.stderr = cp.stderr
        self.returncode = cp.returncode
        self.out = cp.stdout
    def __repr__(self):
        return f"ScriptResult(returncode={self.returncode}, stdout={self.stdout!r}, stderr={self.stderr[-300:]!r})"

def run_script(args=None, stdin="", env=None, file=None, timeout=5):
    """Run a learner file as a real script (``python file args``)."""
    full_env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "TMPDIR", "SYSTEMROOT")}
    full_env["PYTHONIOENCODING"] = "utf-8"
    full_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        full_env.update({str(k): str(v) for k, v in env.items()})
    cp = subprocess.run([sys.executable, file or MAIN, *[str(a) for a in (args or [])]],
                        input=stdin, capture_output=True, text=True, timeout=timeout, env=full_env)
    return ScriptResult(cp)

def capture(fn, *args, **kwargs):
    """Call fn and return (return_value, printed_text)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        value = fn(*args, **kwargs)
    return value, buf.getvalue()

def load(name=None):
    """(Re)import a learner module freshly and return it."""
    name = name or MAIN[:-3]
    sys.modules.pop(name, None)
    with contextlib.redirect_stdout(_out), contextlib.redirect_stderr(_out):
        return importlib.import_module(name)

def source(file=None):
    with open(file or MAIN, encoding="utf-8") as fh:
        return fh.read()

def main():
    dump()
    builtins.input = lambda *a: (_ for _ in ()).throw(EOFError("input() is not available here - write a function instead"))
    if MODE == "function":
        try:
            with contextlib.redirect_stdout(_out), contextlib.redirect_stderr(_out):
                importlib.import_module(MAIN[:-3])
        except SyntaxError as exc:
            state["load_error"] = f"SyntaxError in {os.path.basename(exc.filename or MAIN)} line {exc.lineno}: {exc.msg}\n    {(exc.text or '').rstrip()}"
        except BaseException as exc:
            state["load_error"] = "Your file crashed while loading:\n" + describe(exc, exc.__traceback__)
        if state["load_error"]:
            state["stdout"] = _out.getvalue()[-4000:]
            dump()
            return
    ns = {"__name__": "_tests", "run_script": run_script, "capture": capture,
          "load": load, "source": source}
    with open(TESTS_FILE, encoding="utf-8") as fh:
        code = compile(fh.read(), "_tests.py", "exec")
    with contextlib.redirect_stdout(_out):
        exec(code, ns)
    tests = [(k, v) for k, v in ns.items() if k.startswith("test_") and callable(v)]
    for name, fn in tests:
        state["running"] = name
        dump()
        start = time.perf_counter()
        entry = {"name": name, "passed": False, "message": ""}
        try:
            with contextlib.redirect_stdout(_out), contextlib.redirect_stderr(_out):
                fn()
            entry["passed"] = True
        except subprocess.TimeoutExpired:
            entry["message"] = "Your script took too long (possible infinite loop or waiting for input)."
        except BaseException as exc:
            entry["message"] = describe(exc, exc.__traceback__)[:1500]
        entry["ms"] = round((time.perf_counter() - start) * 1000, 1)
        state["tests"].append(entry)
    state["running"] = None
    state["stdout"] = _out.getvalue()[-4000:]
    dump()

main()
'''


def _limits(cpu: int = 30):
    os.setsid()
    for name, value in (("RLIMIT_CPU", (cpu, cpu + 5)), ("RLIMIT_AS", (2 * 1024**3, 2 * 1024**3)),
                        ("RLIMIT_FSIZE", (20 * 1024**2, 20 * 1024**2))):
        try:
            resource.setrlimit(getattr(resource, name), value)
        except (AttributeError, ValueError, OSError):
            pass  # e.g. macOS refuses RLIMIT_AS; the other limits and the timeout still apply


def _spawn_opts(timeout: float) -> dict:
    """Popen options that put the child in its own process group with resource limits."""
    if os.name == "posix":
        return {"preexec_fn": lambda: _limits(int(timeout) + 10)}
    return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}


def _env(home: str) -> dict:
    env = {
        "PATH": os.environ.get("PATH", os.defpath),
        "HOME": home,
        "LANG": "C.UTF-8",
        "TMPDIR": home,
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if os.name == "nt":  # Python can't start on Windows without these
        env.update({k: os.environ[k] for k in ("SYSTEMROOT", "COMSPEC", "PATHEXT") if k in os.environ})
        env.update(TEMP=home, TMP=home, USERPROFILE=home)
    return env


def _write_files(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"Bad file name: {name}")
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            dest.write_bytes(content)
        else:
            dest.write_text(content, encoding="utf-8")


def _kill(proc: subprocess.Popen) -> None:
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError):
        pass


def _nice_name(name: str) -> str:
    return name.removeprefix("test_").replace("_", " ").strip()


def run_tests(files: dict[str, str], tests: str, *, mode: str = "function",
              main: str = "solution.py", setup_files: dict | None = None,
              timeout: float = 12) -> dict:
    """Grade learner files against test source. Never raises for learner errors."""
    tmp = Path(tempfile.mkdtemp(prefix="pytrainer-"))
    try:
        _write_files(tmp, setup_files or {})
        _write_files(tmp, files)
        (tmp / "_harness.py").write_text(HARNESS, encoding="utf-8")
        (tmp / "_tests.py").write_text(tests, encoding="utf-8")
        results = tmp / "_results.json"
        proc = subprocess.Popen(
            sandbox.wrap([PYTHON, "-X", "utf8", "_harness.py", str(results), "_tests.py", mode, main], tmp),
            cwd=tmp, env=_env(str(tmp)), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
            errors="replace", **_spawn_opts(timeout),
        )
        timed_out = False
        try:
            _, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill(proc)
            _, stderr = proc.communicate()
        try:
            state = json.loads(results.read_text())
        except (OSError, json.JSONDecodeError):
            state = {"tests": [], "load_error": None, "stdout": "", "running": None}
        return _summarise(state, timed_out, proc.returncode, stderr or "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _budgets(stdout: str) -> tuple[str, list[dict]]:
    """Pull `BUDGET|label|used|limit|unit` lines (printed by budget tests) out of the output."""
    keep, budgets = [], []
    for line in stdout.splitlines(keepends=True):
        parts = line.strip().split("|")
        if len(parts) == 5 and parts[0] == "BUDGET":
            try:
                used, limit = float(parts[2]), float(parts[3])
            except ValueError:
                keep.append(line)
                continue
            budgets.append({"label": parts[1], "used": used, "limit": limit, "unit": parts[4], "ok": used <= limit})
        else:
            keep.append(line)
    return "".join(keep), budgets


def _summarise(state: dict, timed_out: bool, returncode: int, stderr: str) -> dict:
    tests = [
        {"name": _nice_name(t["name"]), "passed": t["passed"], "message": t.get("message", ""),
         "ms": t.get("ms")}
        for t in state.get("tests", [])
    ]
    stdout, budgets = _budgets(state.get("stdout") or "")
    out = {
        "status": "passed",
        "tests": tests,
        "passed": sum(t["passed"] for t in tests),
        "total": len(tests),
        "error": None,
        "stdout": stdout[-MAX_OUTPUT:],
    }
    if budgets:
        out["budgets"] = budgets
    if state.get("load_error"):
        out.update(status="error", error=state["load_error"])
    elif timed_out:
        running = state.get("running")
        where = f" during '{_nice_name(running)}'" if running else ""
        out.update(status="timeout",
                   error=f"Time limit exceeded{where}. Look for an infinite loop or very slow code.")
    elif returncode is not None and returncode < 0 and not tests:
        out.update(status="error", error="Your code was killed (CPU, memory or time limit). "
                                         "Look for an infinite loop or huge data structures.")
    elif returncode not in (0, None) and not tests:
        out.update(status="error", error=("The test run crashed.\n" + stderr[-2000:]).strip())
    elif returncode and returncode < 0:
        out.update(status="error", error="Your code was killed (memory or CPU limit hit).")
    if out["status"] == "passed" and (not tests or out["passed"] < len(tests)):
        out["status"] = "failed"
    if out["status"] == "timeout" and tests and state.get("running") is None:
        out["status"] = "failed" if out["passed"] < len(tests) else "passed"
    return out


def run_code(files: dict[str, str], *, main: str = "solution.py", stdin: str = "",
             args: list[str] | None = None, setup_files: dict | None = None,
             timeout: float = 10, llm=None) -> dict:
    """Run a file as a script (the 'Run' button) and return its output.

    With `llm` (a callable taking a prompt and a system prompt), the code can make real model calls
    through `pytrainer_llm` (see llm_bridge); time spent waiting on the model doesn't count against
    `timeout`, and the calls are listed in the result. A `traces.jsonl` the code writes comes back
    as `result["spans"]` for the waterfall viewer (see spans)."""
    from . import llm_bridge, spans

    tmp = Path(tempfile.mkdtemp(prefix="pytrainer-run-"))
    try:
        _write_files(tmp, setup_files or {})
        _write_files(tmp, files)
        if llm is not None:
            llm_bridge.install(tmp)
        proc = subprocess.Popen(
            sandbox.wrap([PYTHON, "-X", "utf8", main, *(args or [])], tmp), cwd=tmp, env=_env(str(tmp)),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", **_spawn_opts(timeout + (300 if llm else 0)),
        )
        timed_out, calls = False, []
        if llm is None:
            try:
                stdout, stderr = proc.communicate(stdin, timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                _kill(proc)
                stdout, stderr = proc.communicate()
        else:
            out: dict = {}
            reader = threading.Thread(target=lambda: out.update(zip(("stdout", "stderr"), proc.communicate(stdin))),
                                      daemon=True)
            reader.start()
            deadline = time.monotonic() + timeout
            while reader.is_alive():
                deadline += llm_bridge.serve(tmp, llm, calls)
                if time.monotonic() > deadline:
                    timed_out = True
                    _kill(proc)
                    break
                reader.join(0.05)
            reader.join()
            stdout, stderr = out.get("stdout", ""), out.get("stderr", "")
        # Show paths relative to the run folder. Strip the resolved path first: on macOS the temp dir
        # is reached through a symlink (/var -> /private/var) and tracebacks report the real path.
        for prefix in (str(tmp.resolve()) + os.sep, str(tmp) + os.sep):
            stderr = stderr.replace(prefix, "")
        result = {
            "stdout": stdout[-MAX_OUTPUT:],
            "stderr": stderr[-MAX_OUTPUT:],
            "returncode": proc.returncode,
            "timed_out": timed_out,
        }
        if llm is not None:
            result["llm_calls"] = calls
        traced = spans.collect(tmp)
        if traced:
            result["spans"] = traced
        return result
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def normalize_output(text: str) -> list[str]:
    lines = [line.rstrip() for line in (text or "").replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def check_prediction(code: str, answer: str, *, setup_files: dict | None = None) -> dict:
    """Grade a 'what does this print?' answer line by line against the real output."""
    run = run_code({"solution.py": code}, setup_files=setup_files)
    actual = normalize_output(run["stdout"] + (run["stderr"] if run["returncode"] else ""))
    guess = normalize_output(answer)
    tests = []
    for i in range(max(len(actual), len(guess))):
        want = actual[i] if i < len(actual) else None
        got = guess[i] if i < len(guess) else None
        ok = want == got
        if ok:
            msg = ""
        elif got is None:
            msg = "missing: the program prints more lines than this"
        elif want is None:
            msg = f"extra line: {got!r} - the program doesn't print this many lines"
        else:
            msg = f"you wrote {got!r} - not what this line prints"
        tests.append({"name": f"line {i + 1}", "passed": ok, "message": msg, "ms": None})
    passed = sum(t["passed"] for t in tests)
    return {"status": "passed" if tests and passed == len(tests) else "failed", "tests": tests,
            "passed": passed, "total": len(tests), "error": None, "stdout": "",
            "_actual": "\n".join(actual)}


def grade_test_writing(test_code: str, impl: str, mutants: list[dict], *,
                       setup_files: dict | None = None) -> dict:
    """Grade learner-written tests: they must pass on the real code and fail on each planted bug.

    The code under test is saved as target.py; the learner's file holds test_* functions.
    """
    from concurrent.futures import ThreadPoolExecutor

    def run(code: str) -> dict:
        return run_tests({"target.py": code}, test_code, mode="script", main="target.py",
                         setup_files=setup_files)

    with ThreadPoolExecutor(max_workers=4) as pool:
        base_future = pool.submit(run, impl)
        mutant_results = list(pool.map(lambda m: run(m["code"]), mutants))
        base = base_future.result()

    tests = []
    if base["total"] == 0 and not base["error"]:
        tests.append({"name": "you wrote at least one test_ function", "passed": False,
                      "message": "No test functions found. Name them test_something.", "ms": None})
    ok = base["status"] == "passed" and base["total"] > 0
    failing = [t for t in base["tests"] if not t["passed"]]
    msg = base["error"] or "; ".join(f"{t['name']}: {t['message']}" for t in failing)[:1500]
    tests.append({"name": f"your {base['total']} test(s) pass on the correct code", "passed": ok,
                  "message": "" if ok else ("A test fails on code that is actually correct - "
                                            "check your expected values. " + msg), "ms": None})
    for m, r in zip(mutants, mutant_results):
        caught = ok and r["status"] != "passed"
        tests.append({"name": f"catches the bug: {m['name']}", "passed": caught,
                      "message": "" if caught else (
                          "All your tests still pass with this bug planted. Add a test that would notice it."
                          if ok else "Fix your tests so they pass on the correct code first."), "ms": None})
    passed = sum(t["passed"] for t in tests)
    return {"status": "passed" if passed == len(tests) else "failed", "tests": tests, "passed": passed,
            "total": len(tests), "error": None, "stdout": base.get("stdout", "")}
