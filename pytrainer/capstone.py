"""Capstone: five projects become one application, exported as a repository to push to GitHub.

The capstone project (``content/projects/p16_capstone.py``) runs next to the learner's own latest
passing code from the projects it builds on. ``export`` then writes a self-contained repository:
the modules, app.py, sample docs, each stage's tests with a standard-library test runner, a README
with an architecture diagram and the learner's scores, and a first git commit.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

from . import content, db, labs

CAPSTONE_ID = "capstone"
REPO_DIR = labs.LAB_ROOT / "portfolio" / "docs-assistant"

STAGES = {
    "chunker": "Splits a folder of .md and .txt notes into overlapping chunks with exact character offsets.",
    "search-index": "TF-IDF keyword search with cosine similarity, saved to and loaded from JSON.",
    "mini-rag": "Embeds chunks, retrieves the closest ones and asks the model to answer only from them, with citations.",
    "eval-harness": "Runs a JSONL set of eval cases with exact, contains, regex, JSON and LLM-judge graders.",
    "tool-agent": "A tool registry that turns typed Python functions into JSON schemas, and an agent loop.",
}


def _latest_passing(project_id: str) -> dict | None:
    for row in db.q("SELECT id, files, result, review, created_at FROM submissions WHERE project_id=? "
                    "ORDER BY id DESC", (project_id,)):
        result = json.loads(row["result"])
        if result.get("status") == "passed":
            review = json.loads(row["review"]) if row["review"] else None
            return {"files": json.loads(row["files"]), "result": result, "created_at": row["created_at"],
                    "score": review.get("score") if review else None}
    return None


def provided_files(project: dict) -> tuple[dict, list[str]]:
    """The learner's passing files from the projects ``project`` builds on, and the ones still missing."""
    data = content.load()
    files, missing = {}, []
    for pid in project.get("requires_projects", []):
        best = _latest_passing(pid)
        if best is None:
            missing.append(data["projects_by_id"][pid]["title"])
            continue
        wanted = data["projects_by_id"][pid]["files"]
        files.update({name: code for name, code in best["files"].items() if name in wanted})
    return files, missing


def status() -> dict:
    data = content.load()
    stages = []
    for pid, what in STAGES.items():
        p = data["projects_by_id"][pid]
        best = _latest_passing(pid)
        stages.append({"id": pid, "title": p["title"], "file": p["files"][0], "what": what,
                       "passed": best is not None, "score": best["score"] if best else None,
                       "tests": f"{best['result']['passed']}/{best['result']['total']}" if best else None})
    app = _latest_passing(CAPSTONE_ID)
    return {"stages": stages,
            "app": {"id": CAPSTONE_ID, "title": data["projects_by_id"][CAPSTONE_ID]["title"],
                    "passed": app is not None, "score": app["score"] if app else None,
                    "tests": f"{app['result']['passed']}/{app['result']['total']}" if app else None},
            "ready": all(s["passed"] for s in stages),
            "repo": str(REPO_DIR), "repo_exists": (REPO_DIR / ".git").is_dir() or REPO_DIR.is_dir(),
            "git": bool(shutil.which("git"))}


RUN_TESTS = r'''"""Run the test suite with only the standard library:  python run_tests.py

Each tests/test_<name>.py checks <name>.py. Every file runs in a fresh temporary folder holding
the modules (and, for app.py, the sample docs), so tests can create files freely. A few helpers
the tests use are available as globals.
"""

import contextlib
import importlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = {"app.py": ["docs"]}  # folders a module's tests need next to it


def helpers(main):
    def run_script(args=None, stdin="", env=None, file=None, timeout=5):
        full_env = dict(os.environ, PYTHONIOENCODING="utf-8", **{str(k): str(v) for k, v in (env or {}).items()})
        cp = subprocess.run([sys.executable, file or main, *map(str, args or [])], input=stdin,
                            capture_output=True, text=True, timeout=timeout, env=full_env)
        cp.out = cp.stdout
        return cp

    def capture(fn, *args, **kwargs):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            value = fn(*args, **kwargs)
        return value, buf.getvalue()

    def load(name=None):
        name = name or main[:-3]
        sys.modules.pop(name, None)
        with contextlib.redirect_stdout(io.StringIO()):
            return importlib.import_module(name)

    def source(file=None):
        return Path(file or main).read_text(encoding="utf-8")

    return {"run_script": run_script, "capture": capture, "load": load, "source": source}


def run_file(test_file):
    main = test_file.stem.removeprefix("test_") + ".py"
    passed = failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for item in ROOT.glob("*.py"):
            shutil.copy(item, Path(tmp) / item.name)
        for folder in DATA.get(main, []):
            shutil.copytree(ROOT / folder, Path(tmp) / folder)
        old_cwd, old_path = os.getcwd(), list(sys.path)
        os.chdir(tmp)
        sys.path.insert(0, tmp)
        for path in ROOT.glob("*.py"):
            sys.modules.pop(path.stem, None)
        try:
            ns = {"__name__": "tests", **helpers(main)}
            exec(compile(test_file.read_text(encoding="utf-8"), str(test_file), "exec"), ns)
            for name, fn in ns.items():
                if name.startswith("test_") and callable(fn):
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            fn()
                        passed += 1
                    except Exception:
                        failed += 1
                        print(f"FAIL {test_file.name}::{name}")
                        print("    " + traceback.format_exc(limit=2).strip().replace("\n", "\n    "))
        finally:
            os.chdir(old_cwd)
            sys.path[:] = old_path
    print(f"{'ok  ' if not failed else 'FAIL'} {test_file.name}: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    files = sorted((ROOT / "tests").glob("test_*.py"))
    sys.exit(1 if sum(run_file(f) for f in files) else 0)
'''

GITIGNORE = "__pycache__/\n*.pyc\n.venv/\n.env\nout/\n*.egg-info/\n"


def _pyproject() -> str:
    return ('[project]\nname = "docs-assistant"\nversion = "0.1.0"\n'
            'description = "Ask questions about a folder of notes: chunking, keyword search, RAG, an agent and evals, '
            'in pure Python."\nreadme = "README.md"\nrequires-python = ">=3.11"\ndependencies = []\n')


def _readme(st: dict, have_app: bool, today: str) -> str:
    rows = []
    for s in st["stages"]:
        score = f"{s['score']}/100" if s["score"] is not None else "not reviewed"
        rows.append(f"| `{s['file']}` | {s['what']} | {s['tests']} | {score} |")
    app = st["app"]
    if have_app:
        score = f"{app['score']}/100" if app["score"] is not None else "not reviewed"
        rows.append(f"| `app.py` | `DocsAssistant`: wires the parts together, exposes them as agent tools, "
                    f"scores itself with the eval harness, and a command line. | {app['tests']} | {score} |")
    run = ('```bash\npython app.py docs "How do I install it?"\npython run_tests.py\n```' if have_app else
           "```bash\npython run_tests.py\n```\n\nNext step: the `app.py` that wires these parts together.")
    return f"""# Docs Assistant

Ask questions about a folder of notes. A retrieval-augmented generation (RAG) toolkit and agent, built
from scratch in pure Python with no dependencies: chunking with exact offsets, TF-IDF keyword search,
embedding retrieval with grounded, cited answers, an agent with typed tools, and an evaluation harness
to measure it all.

The embedding model and the LLM are injected as plain functions, so any provider plugs in. The command
line uses small offline stand-ins and runs anywhere.

## How it fits together

```mermaid
flowchart LR
    D[docs folder] --> C[chunker.py<br/>chunks + offsets]
    C --> S[search.py<br/>TF-IDF keyword search]
    C --> R[rag.py<br/>embeddings + cited answers]
    S --> T[agent.py<br/>tools + agent loop]
    R --> T
    T --> A[app.py<br/>DocsAssistant + CLI]
    E[evals.py<br/>eval harness] --> A
```

## Parts

| File | What it does | Tests | Code review |
| --- | --- | --- | --- |
{chr(10).join(rows)}

Each part was written to a spec and graded by hidden tests and an AI code review against a rubric.

## Run it

Python 3.11 or newer, standard library only.

{run}

## What I practised

Python classes and dataclasses, files and JSON, regular expressions, vector math (cosine similarity, TF-IDF),
retrieval-augmented generation, tool calling with JSON schemas, agent loops with step limits, and
evaluating LLM output with automatic graders and an LLM judge.

<sub>Built with PyTrainer, {today}.</sub>
"""


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=60)


def export(dest: Path | None = None) -> dict:
    """Write (or refresh) the portfolio repository and commit it. Needs all five stages passed."""
    st = status()
    if not st["ready"]:
        missing = [s["title"] for s in st["stages"] if not s["passed"]]
        raise ValueError("Pass these projects first: " + ", ".join(missing))
    data = content.load()
    dest = Path(dest or REPO_DIR)
    dest.mkdir(parents=True, exist_ok=True)
    written = []

    def write(rel: str, text: str) -> None:
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        written.append(rel)

    for pid in STAGES:
        best = _latest_passing(pid)
        p = data["projects_by_id"][pid]
        for name in p["files"]:
            write(name, best["files"][name])
        write(f"tests/test_{p['files'][0][:-3]}.py", p["tests"])
    cap = data["projects_by_id"][CAPSTONE_ID]
    app = _latest_passing(CAPSTONE_ID)
    for name, text in cap["setup_files"].items():
        if name.endswith((".md", ".txt")):
            write(name, text)
    if app:
        write("app.py", app["files"]["app.py"])
        write("tests/test_app.py", cap["tests"])
    write("run_tests.py", RUN_TESTS)
    write("README.md", _readme(st, bool(app), date.today().strftime("%B %Y")))
    write("pyproject.toml", _pyproject())
    write(".gitignore", GITIGNORE)

    git = {"available": bool(shutil.which("git")), "committed": False, "message": ""}
    if git["available"]:
        if not (dest / ".git").is_dir():
            _git(["init", "-q", "-b", "main"], dest)
        _git(["add", "-A"], dest)
        if _git(["diff", "--cached", "--quiet"], dest).returncode == 0:
            git["message"] = "Nothing changed since the last export."
        else:
            msg = "Docs Assistant: chunker, search, RAG, evals and agent" + (" wired together in app.py" if app else "")
            cp = _git(["commit", "-q", "-m", msg], dest)
            git["committed"] = cp.returncode == 0
            git["message"] = "Committed." if git["committed"] else (
                "Files are written, but git could not commit: " + (cp.stderr or cp.stdout).strip()[-300:]
                + " Set your name and email with `git config --global user.name` / `user.email`, then commit.")
    return {"path": str(dest), "files": sorted(written), "git": git, "has_app": bool(app)}
