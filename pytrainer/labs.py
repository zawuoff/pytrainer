"""Terminal labs: real-world tasks done in the learner's own terminal, verified by checks."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from . import ai

LAB_ROOT = Path.home() / "pytrainer-lab"


def _path(p: str) -> Path:
    return Path(os.path.expanduser(p))


def _run(cmd: list[str], cwd: str | None, env: dict | None, timeout: int = 120):
    full_env = ai._env()
    for key in ("VIRTUAL_ENV", "PYTHONHOME", "PYTHONPATH", "UV_PROJECT_ENVIRONMENT"):
        full_env.pop(key, None)
    if env:
        full_env.update(env)
    cwd_path = _path(cwd) if cwd else None
    if cwd_path and not cwd_path.is_dir():
        return None, f"folder {cwd} does not exist"
    exe = ai.which(cmd[0]) if not cmd[0].startswith((".", "/", "~")) else str(_path(cmd[0]) if cmd[0].startswith("~") else cmd[0])
    if not exe:
        return None, f"`{cmd[0]}` not found on PATH"
    try:
        cp = subprocess.run([exe, *cmd[1:]], cwd=cwd_path, env=full_env, capture_output=True,
                            text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, "command timed out"
    except OSError as exc:
        return None, str(exc)
    return cp, None


def run_check(check: dict) -> tuple[bool, str]:
    kind = check["type"]
    if kind == "command":
        path = ai.which(check["cmd"])
        return bool(path), (f"found at {path}" if path else f"`{check['cmd']}` is not on your PATH")
    if kind == "path":
        p = _path(check["path"])
        ok = p.exists() and (not check.get("dir") or p.is_dir())
        return ok, ("exists" if ok else f"{check['path']} not found")
    if kind == "absent":
        p = _path(check["path"])
        return not p.exists(), ("not present (good)" if not p.exists() else f"{check['path']} should not exist")
    if kind == "contains":
        p = _path(check["path"])
        if not p.is_file():
            return False, f"{check['path']} not found"
        text = p.read_text(errors="replace")
        ok = re.search(check["pattern"], text, re.M) is not None
        if check.get("negate"):
            ok = not ok
        return ok, ("ok" if ok else check.get("hint", "content doesn't match what is expected"))
    if kind == "run":
        cp, err = _run(check["cmd"], check.get("cwd"), check.get("env"), check.get("timeout", 120))
        if err:
            return False, err
        want_rc = check.get("returncode", 0)
        if want_rc is not None and cp.returncode != want_rc:
            tail = (cp.stderr or cp.stdout).strip()[-400:]
            return False, f"exit code {cp.returncode} (expected {want_rc}). {tail}"
        if "stdout" in check and not re.search(check["stdout"], cp.stdout, re.M):
            return False, f"output was: {cp.stdout.strip()[-300:]!r}"
        if "stderr" in check and not re.search(check["stderr"], cp.stderr, re.M):
            return False, f"stderr was: {cp.stderr.strip()[-300:]!r}"
        return True, "ok"
    return False, f"unknown check type {kind}"


def check_lab(lab: dict) -> dict:
    results = []
    for check in lab["checks"]:
        ok, detail = run_check(check)
        results.append({"label": check["label"], "passed": ok, "detail": detail})
    return {"passed": all(r["passed"] for r in results), "checks": results}
