"""Wrap learner processes in an OS sandbox when the machine offers one.

Learner code and test code (including tests an AI wrote) run through ``wrap()``. The best
level that works on this machine is picked once and cached:

- ``bwrap``: bubblewrap. No network except loopback, the whole filesystem read-only except
  the run's own temp dir, ``/tmp`` private and PyTrainer's data dir hidden.
- ``netns``: util-linux ``unshare`` in a user + network namespace. No network except
  loopback; the filesystem is as usual.
- ``basic``: no OS sandbox, only the resource limits and temp HOME set by ``runner``.

``PYTRAINER_SANDBOX=bwrap|netns|basic`` forces a level (``basic`` turns sandboxing off).
A forced level that doesn't work on this machine falls back to the next one down.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

LEVELS = ("bwrap", "netns", "basic")

DETAIL = {
    "bwrap": "No network, read-only filesystem outside the run folder (bubblewrap).",
    "netns": "No network (user + network namespace). Install bubblewrap to also make the "
             "filesystem read-only.",
    "basic": "Resource limits only: code can reach the network and your files. Install "
             "bubblewrap (`bwrap`) for a real sandbox.",
}

# A new network namespace starts with loopback down. Local test servers on 127.0.0.1 need it,
# so the netns level brings it up (SIOCGIFFLAGS / SIOCSIFFLAGS) before exec'ing the real command.
_LO_UP = r"""
import fcntl, os, socket, struct, sys
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
flags = struct.unpack("16sH", fcntl.ioctl(s, 0x8913, struct.pack("16sH22x", b"lo", 0))[:18])[1]
fcntl.ioctl(s, 0x8914, struct.pack("16sH22x", b"lo", flags | 1))
s.close()
os.execvp(sys.argv[1], sys.argv[1:])
"""

# Passes when loopback works and the outside world is unreachable.
_PROBE = r"""
import socket
srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)
socket.create_connection(srv.getsockname(), timeout=2).close()
try:
    socket.create_connection(("1.1.1.1", 53), timeout=2).close()
    print("open")
except OSError:
    print("ok")
"""

_lock = threading.Lock()
_level: str | None = None


def _data_dir() -> Path:
    from . import db
    return db.DATA_DIR


def _python_dirs() -> set[str]:
    exe = Path(sys.executable or "python3").resolve()
    dirs = {sys.prefix, sys.base_prefix, str(exe.parent.parent)}
    return {d for d in dirs if (d == "/tmp" or d.startswith("/tmp/")) and Path(d).is_dir()}


def _command(level: str, cmd: list[str], workdir: Path) -> list[str]:
    if level == "bwrap":
        wrapped = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
                   "--tmpfs", "/tmp"]
        # /tmp is replaced by an empty one, so a Python (or venv) living under /tmp would vanish:
        # mount it back, read-only.
        for path in sorted(_python_dirs()):
            wrapped += ["--ro-bind", path, path]
        data = _data_dir()
        if data.is_dir():
            wrapped += ["--tmpfs", str(data)]
        wrapped += ["--bind", str(workdir), str(workdir), "--chdir", str(workdir),
                    "--unshare-net", "--unshare-pid", "--unshare-ipc", "--die-with-parent", "--"]
        return wrapped + cmd
    if level == "netns":
        return ["unshare", "--user", "--map-root-user", "--net", "--",
                sys.executable or "python3", "-c", _LO_UP] + cmd
    return list(cmd)


def _works(level: str) -> bool:
    if level == "basic":
        return True
    if not shutil.which("bwrap" if level == "bwrap" else "unshare"):
        return False
    tmp = Path(tempfile.mkdtemp(prefix="pytrainer-probe-"))
    try:
        cp = subprocess.run(_command(level, [sys.executable or "python3", "-c", _PROBE], tmp),
                            cwd=tmp, capture_output=True, text=True, timeout=15,
                            stdin=subprocess.DEVNULL)
        return cp.returncode == 0 and cp.stdout.strip() == "ok"
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def level() -> str:
    """The sandbox level in use, probed on first call."""
    global _level
    with _lock:
        if _level is None:
            forced = os.environ.get("PYTRAINER_SANDBOX", "").strip().lower()
            start = LEVELS.index(forced) if forced in LEVELS else 0
            _level = next(lv for lv in LEVELS[start:] if _works(lv))
        return _level


def in_container() -> bool:
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()


def status() -> dict:
    lv = level()
    detail = DETAIL[lv]
    if lv == "basic" and in_container():
        detail = ("Running in a container: resource limits only. Code can reach the network, but it only sees "
                  "the container's files, not your computer's.")
    return {"level": lv, "detail": detail}


def wrap(cmd: list[str], workdir: Path) -> list[str]:
    """Return ``cmd`` wrapped so it runs inside the sandbox, with ``workdir`` writable."""
    return _command(level(), cmd, workdir)
