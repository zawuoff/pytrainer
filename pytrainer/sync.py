"""Work in your own editor: write a step's or project's files to a folder, open it in VS Code (or
Cursor / VSCodium), and let the browser pick up every save.

`open_item` writes the browser's code into the folder without overwriting work already on disk (a
file that exists and has been changed from the starter is kept, and reported), then launches the
first editor found on PATH. When none is, it returns a ``vscode://`` link the browser can follow.
`changes` is polled by the browser: it returns the files whose modification time moved since the
stamps the browser last saw, so edits show up in the page within a second or two.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from .labs import LAB_ROOT

PROJECTS_DIR = LAB_ROOT / "projects"
STEPS_DIR = LAB_ROOT / "steps"
EDITORS = [("code", "VS Code"), ("cursor", "Cursor"), ("codium", "VSCodium"), ("code-insiders", "VS Code Insiders")]
MAX_FILE = 400_000


def display(folder: Path) -> str:
    """The folder as people write it: ~/pytrainer-lab/... rather than the full home path."""
    try:
        return "~/" + folder.relative_to(Path.home()).as_posix()
    except ValueError:
        return str(folder)


def find_editor() -> tuple[str, str] | None:
    for cmd, name in EDITORS:
        path = shutil.which(cmd)
        if path:
            return path, name
    return None


def _launch(path: str, args: list[str]) -> None:
    opts: dict = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        opts["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        # `code` on Windows is a .cmd script, which needs the shell to run.
        if path.lower().endswith((".cmd", ".bat")):
            subprocess.Popen(["cmd", "/c", path, *args], **opts)
            return
    else:
        opts["start_new_session"] = True
    subprocess.Popen([path, *args], **opts)


def folder_for(kind: str, item_id: str) -> Path:
    return (PROJECTS_DIR if kind == "project" else STEPS_DIR) / item_id


def _safe(folder: Path, name: str) -> Path:
    rel = Path(name)
    if rel.is_absolute() or ".." in rel.parts or not name:
        raise ValueError(f"bad file name: {name}")
    return folder / rel


def prepare(folder: Path, files: dict[str, str], starters: dict[str, str], extra: dict[str, str] | None = None) -> dict:
    """Put the browser's files on disk, keeping changed work that's already there.
    Returns the files as they are on disk afterwards, and the names that were kept from disk."""
    folder.mkdir(parents=True, exist_ok=True)
    kept = []
    for name, code in files.items():
        dest = _safe(folder, name)
        if dest.is_file():
            disk = dest.read_text(encoding="utf-8", errors="replace")
            if disk == code:
                continue
            if disk.strip() != (starters.get(name) or "").strip():
                kept.append(name)  # real work on disk: the folder wins
                continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code, encoding="utf-8")
    for name, text in (extra or {}).items():
        dest = _safe(folder, name)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
    current = {name: _safe(folder, name).read_text(encoding="utf-8", errors="replace") for name in files}
    return {"files": current, "kept": kept, "stamp": stamps(folder, list(files))}


def stamps(folder: Path, names: list[str]) -> dict[str, int]:
    out = {}
    for name in names:
        try:
            out[name] = _safe(folder, name).stat().st_mtime_ns
        except (OSError, ValueError):
            out[name] = 0
    return out


def changes(folder: Path, names: list[str], known: dict[str, int]) -> dict:
    """Files whose modification time differs from `known`, with their new contents."""
    now = stamps(folder, names)
    changed, missing = {}, []
    for name, stamp in now.items():
        if stamp == 0:
            missing.append(name)
            continue
        if stamp != known.get(name):
            path = _safe(folder, name)
            if path.stat().st_size > MAX_FILE:
                continue
            changed[name] = path.read_text(encoding="utf-8", errors="replace")
    return {"changed": changed, "stamp": now, "missing": missing}


def open_in_editor(folder: Path, file: str | None = None) -> dict:
    target = _safe(folder, file) if file else folder
    editor = find_editor()
    if editor:
        path, name = editor
        try:
            _launch(path, [str(folder), str(target)] if file else [str(folder)])
            return {"opened": name, "url": None}
        except OSError:
            pass
    # No editor command on PATH: VS Code registers vscode:// links, so the browser can open it.
    return {"opened": None, "url": "vscode://file/" + quote(str(target.resolve()).replace("\\", "/"))}
