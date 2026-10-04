"""The REPL panel: a live Python session in the sandbox, kept between commands.

Each session is one sandboxed `python` process running AGENT below, in its own temp folder (with
the learner's files copied in when they ask to load their code). Commands and replies are JSON
lines on stdin/stdout. The agent behaves like the interactive interpreter: an expression shows its
repr, `_` holds the last result, and an unfinished block (`def f():`) asks for more lines.

A command that runs longer than COMMAND_TIMEOUT seconds gets the process killed (the next command
starts a fresh one), sessions idle for IDLE_SECONDS are closed, and at most MAX_SESSIONS live at once.
"""

from __future__ import annotations

import json
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

from . import runner, sandbox

COMMAND_TIMEOUT = 10
IDLE_SECONDS = 20 * 60
MAX_SESSIONS = 4
MAX_OUT = 20_000
SESSION_CPU = 600  # CPU seconds a whole session may use

AGENT = r'''
import ast, builtins, codeop, io, json, os, sys, traceback

chan = os.fdopen(os.dup(1), "w", encoding="utf-8", buffering=1)
commands = os.fdopen(os.dup(0), "r", encoding="utf-8")
# Output written straight to the file descriptors (os.write, subprocesses) lands in a file we read
# back after each command, so it can't corrupt the reply channel.
cap = open("_repl_fd_out.txt", "w+b")
os.dup2(cap.fileno(), 1)
os.dup2(cap.fileno(), 2)
devnull = os.open(os.devnull, os.O_RDONLY)
os.dup2(devnull, 0)
sys.stdin = io.StringIO("")

ns = {"__name__": "__main__", "__builtins__": builtins}
compiler = codeop.CommandCompiler()


def show_exc(skip_frames):
    etype, value, tb = sys.exc_info()
    for _ in range(skip_frames):
        tb = tb.tb_next if tb is not None else None
    sys.stderr.write("".join(traceback.format_exception(etype, value, tb)))


def run_block(src, filename):
    """Several statements at once (a paste, or a loaded file): run them; show the last expression."""
    tree = ast.parse(src, filename, "exec")
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    exec(compile(tree, filename, "exec"), ns)
    if last is not None:
        value = eval(compile(ast.Expression(last.value), filename, "eval"), ns)
        sys.displayhook(value)


def handle(msg):
    src = msg.get("code", "")
    if msg.get("file"):
        ns["__file__"] = msg["file"]
        try:
            run_block(src, msg["file"])
        except SystemExit:
            pass
        except BaseException:
            show_exc(2)  # skip handle() and run_block()
        return False
    block = False
    try:
        code = compiler(src, "<stdin>", "single")
    except (OverflowError, SyntaxError, ValueError) as exc:
        if not (isinstance(exc, SyntaxError) and "multiple statements" in str(exc)):
            sys.stderr.write("".join(traceback.format_exception_only(type(exc), exc)))
            return False
        block = True  # handled below, outside this except, so tracebacks don't chain onto it
    if block:
        try:
            run_block(src, "<stdin>")
        except SystemExit:
            pass
        except BaseException:
            show_exc(2)
        return False
    if code is None:
        return True
    try:
        exec(code, ns)
    except SystemExit:
        sys.stderr.write("(exit() doesn't close the REPL panel: use Restart.)\n")
    except BaseException:
        show_exc(1)
    return False


for line in commands:
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    out, err = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = out, err
    cap.seek(0); cap.truncate()
    more = handle(msg)
    sys.stdout.flush()
    sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    cap.seek(0)
    raw = cap.read().decode("utf-8", "replace")
    chan.write(json.dumps({"out": raw + out.getvalue(), "err": err.getvalue(), "more": more}) + "\n")
'''

_spawn_jobs: queue.Queue = queue.Queue()
_spawner_lock = threading.Lock()
_spawner: threading.Thread | None = None


def _spawn_loop() -> None:
    while True:
        make, box, done = _spawn_jobs.get()
        try:
            box["proc"] = make()
        except BaseException as exc:  # noqa: BLE001 - handed back to the caller
            box["error"] = exc
        done.set()


def _spawn(make) -> subprocess.Popen:
    """Start a process from one long-lived thread. The sandbox (bwrap --die-with-parent) kills a
    child when the *thread* that started it exits, and every HTTP request runs on its own thread,
    so a session started from a request thread would die as soon as that request finished."""
    global _spawner
    with _spawner_lock:
        if _spawner is None or not _spawner.is_alive():
            _spawner = threading.Thread(target=_spawn_loop, name="repl-spawner", daemon=True)
            _spawner.start()
    box: dict = {}
    done = threading.Event()
    _spawn_jobs.put((make, box, done))
    done.wait()
    if "error" in box:
        raise box["error"]
    return box["proc"]


BANNER = "Python REPL in the sandbox. Variables stay until you restart. Shift+Enter for a new line, Up/Down for history."


class Session:
    def __init__(self, files: dict[str, str] | None = None):
        self.id = uuid.uuid4().hex[:12]
        self.files = dict(files or {})
        self.lock = threading.Lock()
        self.last_used = time.monotonic()
        self.proc: subprocess.Popen | None = None
        self.tmp: Path | None = None
        self.replies: queue.Queue = queue.Queue()

    def _start(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pytrainer-repl-"))
        runner._write_files(self.tmp, self.files)
        (self.tmp / "_repl_agent.py").write_text(AGENT, encoding="utf-8")
        tmp = self.tmp
        self.proc = _spawn(lambda: subprocess.Popen(
            sandbox.wrap([runner.PYTHON, "-X", "utf8", "-u", "_repl_agent.py"], tmp),
            cwd=tmp, env=runner._env(str(tmp)), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
            **runner._spawn_opts(SESSION_CPU)))
        self.replies = queue.Queue()
        threading.Thread(target=self._read, args=(self.proc, self.replies), daemon=True).start()

    @staticmethod
    def _read(proc: subprocess.Popen, replies: queue.Queue) -> None:
        try:
            for line in proc.stdout:
                replies.put(line)
        except (OSError, ValueError):
            pass
        finally:
            proc.stdout.close()
            replies.put(None)

    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def send(self, msg: dict) -> dict:
        with self.lock:
            self.last_used = time.monotonic()
            restarted = False
            if not self.alive():
                restarted = self.proc is not None
                self._cleanup()
                self._start()
            try:
                self.proc.stdin.write(json.dumps(msg) + "\n")
                self.proc.stdin.flush()
            except (BrokenPipeError, OSError):
                self._cleanup()
                return {"out": "", "err": "The session stopped. Run the command again to start a fresh one.\n",
                        "more": False, "restarted": True}
            try:
                line = self.replies.get(timeout=COMMAND_TIMEOUT)
            except queue.Empty:
                line = "timeout"
            if line is None or line == "timeout":
                why = (f"Stopped after {COMMAND_TIMEOUT} s (an infinite loop, or waiting on something?)."
                       if line == "timeout" else "The session crashed (out of memory or CPU?).")
                self._cleanup()
                return {"out": "", "err": why + " The session was reset, so earlier variables are gone.\n",
                        "more": False, "restarted": True}
            reply = json.loads(line)
            reply["out"], reply["err"] = reply["out"][-MAX_OUT:], reply["err"][-MAX_OUT:]
            reply["restarted"] = restarted
            return reply

    def _cleanup(self) -> None:
        if self.proc is not None:
            if self.proc.poll() is None:
                runner._kill(self.proc)
                try:
                    self.proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            try:
                self.proc.stdin.close()
            except OSError:
                pass
        self.proc = None
        if self.tmp is not None:
            shutil.rmtree(self.tmp, ignore_errors=True)
            self.tmp = None

    def close(self) -> None:
        with self.lock:
            self._cleanup()


_sessions: dict[str, Session] = {}
_lock = threading.Lock()


def _reap() -> None:
    now = time.monotonic()
    for sid, s in list(_sessions.items()):
        if now - s.last_used > IDLE_SECONDS:
            _sessions.pop(sid, None)
            s.close()


def start(files: dict[str, str] | None = None, run_file: str | None = None) -> dict:
    """A new session. With `run_file`, that file (one of `files`) runs first, like `python -i file.py`."""
    with _lock:
        _reap()
        while len(_sessions) >= MAX_SESSIONS:
            oldest = min(_sessions.values(), key=lambda s: s.last_used)
            _sessions.pop(oldest.id, None)
            oldest.close()
        s = Session(files)
        _sessions[s.id] = s
    out = {"id": s.id, "banner": BANNER, "out": "", "err": ""}
    if run_file:
        if run_file not in s.files:
            raise ValueError(f"{run_file} isn't one of your files")
        r = s.send({"code": s.files[run_file], "file": run_file})
        out.update(out=r["out"], err=r["err"])
    return out


def run(session_id: str, code: str) -> dict:
    s = _sessions.get(session_id)
    if s is None:
        raise KeyError("This REPL session has ended. Start a new one.")
    return s.send({"code": code[:50_000]})


def stop(session_id: str) -> None:
    s = _sessions.pop(session_id, None)
    if s:
        s.close()


def stop_all() -> None:
    for sid in list(_sessions):
        stop(sid)
