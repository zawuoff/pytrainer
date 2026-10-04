#!/usr/bin/env python3
"""PyTrainer - local Python practice app for aspiring AI engineers.

Run:  python3 server.py [--port 8765] [--open]
Then open http://127.0.0.1:8765 (or use the installed desktop launcher). Needs Python 3.11+.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

if sys.version_info < (3, 11):
    sys.exit("PyTrainer needs Python 3.11 or newer (this is %d.%d)." % sys.version_info[:2])

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pytrainer import (achievements, ai, capstone, coach, content, course, db, drills, interview, jev, labs, leaderboard, lint,  # noqa: E402
                       mistakes, progress, radar, runner, sandbox, spans, tracer, variants, xp)

STATIC = ROOT / "static"
PROJECTS_DIR = labs.LAB_ROOT / "projects"
MAX_BODY = 8 * 1024 * 1024
VERSION = "1.0.0"


def _allowed_host(host: str) -> bool:
    """Localhost, or this machine reached through Tailscale (MagicDNS name or 100.64/10 IP)."""
    if host in ("127.0.0.1", "localhost", "[::1]") or host.endswith(".ts.net"):
        return True
    parts = host.split(".")
    return len(parts) == 4 and parts[0] == "100" and parts[1].isdigit() and 64 <= int(parts[1]) <= 127


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def _files(body: dict) -> dict[str, str]:
    files = body.get("files")
    if not isinstance(files, dict) or not files:
        raise ApiError("files required")
    clean = {}
    for name, code in files.items():
        if not isinstance(name, str) or not isinstance(code, str):
            raise ApiError("files must map names to text")
        if not re.fullmatch(r"[\w.\-/]{1,120}", name) or ".." in name or name.startswith("/"):
            raise ApiError(f"bad file name: {name}")
        if name.startswith("_"):
            raise ApiError("file names may not start with _")
        clean[name] = code
    return clean


def _exercise(ex_id: str) -> dict:
    ex = progress.all_exercises().get(ex_id)
    if not ex:
        raise ApiError("exercise not found", 404)
    return ex


def _task_text(ex: dict) -> str:
    return f"# {ex['title']}\n\n{ex['prompt']}"


QUALITY_TIPS = {
    "readability": "Readability: could someone skim this and know what it does? Clear steps, "
                   "one idea per line, and a blank line between the parts all help.",
    "naming": "Naming: good names say what a value holds (`total_tokens`, not `t` or `x`). "
              "Rename anything you had to think about.",
    "idiomatic": "Pythonic: look for a built-in or idiom that does this for you (`sum`, `enumerate`, "
                 "`zip`, `in`, comprehensions, `.get`), instead of doing it by hand.",
    "simplicity": "Simplicity: is there a step you could delete? Extra variables, flags and nested "
                  "ifs often disappear when you return early.",
    "robustness": "Edge cases: what happens with empty input, missing keys, zero or None? "
                  "Handle the cases the task mentions explicitly.",
}


def _quality_tips(q: dict | None) -> list[str]:
    if not q:
        return []
    weak = sorted(((v["score"], k) for k, v in q["dims"].items() if v["score"] < 6.5))
    return [QUALITY_TIPS[k] for _, k in weak[:3] if k in QUALITY_TIPS]


def _quality(ex: dict, code: str) -> dict | None:
    """Jev code-quality score, or None when Jev isn't set up / fails (never blocks grading)."""
    if not jev.enabled() or not code.strip():
        return None
    try:
        return jev.code_quality(_task_text(ex), code)
    except jev.JevError as exc:
        print(f"jev quality failed: {exc}", flush=True)
        return None


# --------------------------------------------------------------------------- state

def api_state(_body=None):
    if variants.enabled():
        variants.prepare(progress.all_exercises())
    data = content.load()
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    settings = db.settings()
    placement = db.q1("SELECT * FROM placement ORDER BY id DESC LIMIT 1")
    return {
        "version": VERSION,
        "settings": {
            "ai": settings.get("ai", {"provider": "none", "model": ""}),
            "daily_goal": settings.get("daily_goal", 90),
            "onboarded": settings.get("onboarded", False),
            "name": settings.get("name", ""),
            "jev": {"configured": bool(jev.key()), "enabled": jev.enabled(), "masked": jev.masked()},
            "review_variants": settings.get("review_variants", True),
        },
        "tracks": data["tracks"],
        "topics": [{"id": t["id"], "title": t["title"], "track": t["track"], "summary": t["summary"],
                    "requires": t["requires"], "concepts": t.get("concepts", []), **tp[t["id"]],
                    "strip": [[data["exercises"][e]["difficulty"], states.get(e, {}).get("status", "new")]
                              for e in t["exercise_ids"]]}
                   for t in data["topics"]],
        "combos": progress.combo_status(tp, states),
        "summary": progress.summary(),
        "level": progress.level_label(tp),
        "plan": course.today_plan(states, tp),
        "modules": course.overview(states, tp),
        "continue": course.continue_point(states, tp),
        "placement": {
            "status": ("none" if not placement else "done" if placement["finished_at"] else "in_progress"),
            "id": placement["id"] if placement else None,
        },
        "counts": {"projects": len(data["projects"]), "labs": len(data["labs"])},
        "library": {"unlocked": sum(p["library_unlocked"] for p in tp.values()), "total": len(tp)},
        "xp": xp.baseline(),
        "sandbox": sandbox.status(),
        "data_dir": str(db.DATA_DIR),
    }


def api_topic(topic_id: str):
    data = content.load()
    t = data["topics_by_id"].get(topic_id)
    if not t:
        raise ApiError("topic not found", 404)
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    exs = [data["exercises"][e] for e in t["exercise_ids"]]
    custom = [json.loads(r["data"]) for r in
              db.q("SELECT data FROM custom_exercises WHERE topic=? ORDER BY created_at", (topic_id,))]
    def row(e):
        st = states.get(e["id"], {})
        return {"id": e["id"], "title": e["title"], "difficulty": e["difficulty"],
                "status": st.get("status", "new"), "attempts": st.get("attempts", 0),
                "generated": e.get("generated", False), "mode": e.get("mode", "function"),
                "revealed": bool(st.get("revealed")), "extra": bool(e.get("extra")), "kind": e.get("kind")}
    requires = [{"id": r, "title": data["topics_by_id"][r]["title"], "cleared": tp[r]["cleared"]}
                for r in t["requires"]]
    return {"topic": {k: t[k] for k in ("id", "title", "track", "summary", "concepts", "lesson")},
            "progress": tp[topic_id], "requires": requires,
            "next": course.chapter_next(topic_id, states, tp),
            "next_chapter": course.next_chapter(topic_id, tp),
            "exercises": [row(e) for e in exs], "generated": [row(e) for e in custom]}


def api_exercise(ex_id: str):
    ex = _exercise(ex_id)
    draft = db.q1("SELECT files FROM drafts WHERE item_id=?", (ex_id,))
    chat = db.q1("SELECT messages FROM chats WHERE item_id=?", (ex_id,))
    attempts = db.q("SELECT id, kind, status, passed, total, duration_s, created_at FROM attempts "
                    "WHERE item_id=? ORDER BY id DESC LIMIT 20", (ex_id,))
    last_pass = db.q1("SELECT files FROM attempts WHERE item_id=? AND status='passed' ORDER BY id DESC LIMIT 1",
                      (ex_id,))
    review = db.q1("SELECT review FROM reviews WHERE item_id=? ORDER BY rowid DESC LIMIT 1", (ex_id,))
    data = content.load()
    seq = _sequence(ex)
    state = progress.get_state(ex_id)
    path = course.path_info(ex)
    is_exam = ex.get("topic") == "exam"
    exam_open = is_exam and not (course.exam_status(ex.get("module")) or {}).get("passed")
    return {
        "path": path,
        "exam": is_exam, "exam_locked_help": exam_open,
        "reference": ex["solution"] if state["status"] == "solved" and ex.get("mode") != "predict" else None,
        "hints": ex.get("hints", [])[:state.get("hints_used", 0)],
        "can_reveal": _can_reveal(ex, state),
        "revealed": _revealed_payload(ex) if state.get("revealed") else None,
        "explanation": ex.get("explanation") if ex.get("mode") in READ_ONLY and state["status"] == "solved" else None,
        "traceback": _traceback(ex) if ex.get("mode") == "traceback" else None,
        "exercise": content.public_exercise(ex),
        "checks": _check_names(ex),
        "topic_title": ("Combination challenge" if ex.get("topic") == "combo" else
                        data["modules_by_id"].get(ex.get("module"), {}).get("title", "") + " test" if is_exam else
                        data["topics_by_id"].get(ex.get("topic"), {}).get("title")),
        "module": (data["topics_by_id"][ex["topic"]]["track"] if ex.get("topic") in data["topics_by_id"]
                   else ex.get("module")),
        "combo_topics": [data["topics_by_id"][t]["title"] for t in ex.get("topics", [])
                         if t in data["topics_by_id"]],
        "state": state,
        "draft": json.loads(draft["files"]) if draft else None,
        "last_passed_files": json.loads(last_pass["files"]) if last_pass else None,
        "chat": json.loads(chat["messages"]) if chat else [],
        "attempts": [dict(a) for a in attempts],
        "review": json.loads(review["review"]) if review else None,
        "explain_back": _last_explanation(ex_id),
        "next": seq["next"], "prev": seq["prev"],
        "debug_call": (tracer.suggest_call(ex["solution"], ex["tests"])
                       if ex.get("mode", "function") == "function" else ""),
    }


def _last_explanation(ex_id: str) -> dict | None:
    row = db.q1("SELECT text, result, created_at FROM explanations WHERE item_id=? ORDER BY id DESC LIMIT 1", (ex_id,))
    return {"text": row["text"], "result": json.loads(row["result"]), "created_at": row["created_at"]} if row else None


def _sequence(ex: dict) -> dict:
    data = content.load()
    if ex.get("topic") == "combo":
        ids = [c["id"] for c in data["combos"]]
    elif ex.get("topic") == "exam":
        ids = data["exams_by_module"][ex["module"]]["exercise_ids"]
    elif ex.get("topic") in data["topics_by_id"] and not ex.get("generated"):
        ids = data["topics_by_id"][ex["topic"]]["exercise_ids"]
    else:
        return {"next": None, "prev": None}
    i = ids.index(ex["id"])
    return {"next": ids[i + 1] if i + 1 < len(ids) else None, "prev": ids[i - 1] if i > 0 else None}


REVEAL_AFTER_ATTEMPTS = 3
REVEAL_AFTER_SECONDS = 600


READ_ONLY = ("predict", "traceback")  # steps where the learner reads a given program instead of writing one


def _traceback(ex: dict) -> str:
    """The real traceback of a read-the-traceback step's program, run once and remembered."""
    if ex["id"] not in _TRACEBACKS:
        run = runner.run_code({"solution.py": ex["code"]}, setup_files=ex.get("setup_files"))
        _TRACEBACKS[ex["id"]] = run["stderr"].strip()
    return _TRACEBACKS[ex["id"]]


_TRACEBACKS: dict[str, str] = {}


def _check_traceback(ex: dict, answer) -> dict:
    try:
        line = int(answer)
    except (TypeError, ValueError):
        raise ApiError("Click the line you would change first, then press Check.") from None
    ok = line == ex["answer_line"]
    frames = [int(n) for n in re.findall(r'File "solution\.py", line (\d+)', _traceback(ex))]
    if ok:
        msg = ""
    elif frames and line == frames[-1]:
        msg = (f"Line {line} is where the error surfaced, but nothing on it is wrong. "
               "Ask where the bad value or call came from: look at the frames above it.")
    elif line in frames:
        msg = f"Line {line} is part of the path to the error, but it isn't the line to change."
    else:
        msg = f"Not line {line}. Read the traceback from the bottom up: what went wrong, and on which lines?"
    return {"status": "passed" if ok else "failed", "error": None, "stdout": "", "passed": int(ok), "total": 1,
            "tests": [{"name": "the line to change", "passed": ok, "message": msg, "ms": None}]}


def _check_names(ex: dict) -> list[str]:
    """Readable names of the hidden tests - a checklist of what will be checked (not how)."""
    if ex.get("mode") in READ_ONLY:
        return []
    return [n.removeprefix("test_").replace("_", " ") for n in re.findall(r"^def (test_\w+)", ex["tests"], re.M)]


def _can_reveal(ex: dict, state: dict, duration_s: int = 0) -> bool:
    if state.get("status") == "solved" and not state.get("revealed"):
        return False
    need = 2 if ex.get("mode") in READ_ONLY else REVEAL_AFTER_ATTEMPTS
    return state.get("attempts", 0) >= need or duration_s >= REVEAL_AFTER_SECONDS or bool(state.get("revealed"))


def _revealed_payload(ex: dict) -> dict:
    if ex.get("mode") == "predict":
        out = runner.check_prediction(ex["code"], "", setup_files=ex.get("setup_files"))["_actual"]
        return {"output": out, "explanation": ex.get("explanation", "")}
    if ex.get("mode") == "traceback":
        return {"line": ex["answer_line"], "explanation": ex.get("explanation", ""), "solution": ex["solution"]}
    return {"solution": ex["solution"]}


def _no_help_in_tests(ex: dict) -> None:
    if ex.get("topic") == "exam" and not (course.exam_status(ex.get("module")) or {}).get("passed"):
        raise ApiError("This is a module test: no hints, solutions or tutor until you've passed it.")


def api_hint(ex_id: str, body: dict):
    ex = _exercise(ex_id)
    _no_help_in_tests(ex)
    hints = ex.get("hints", [])
    if not hints:
        raise ApiError("No hints for this one - ask the tutor instead.")
    state = progress.get_state(ex_id)
    state["hints_used"] = min(len(hints), state.get("hints_used", 0) + 1)
    progress.save_state(state)
    return {"hints": hints[:state["hints_used"]], "total": len(hints)}


def api_reveal(ex_id: str, body: dict):
    ex = _exercise(ex_id)
    _no_help_in_tests(ex)
    state = progress.get_state(ex_id)
    if not _can_reveal(ex, state, int(body.get("duration_s", 0))):
        need = 2 if ex.get("mode") in READ_ONLY else REVEAL_AFTER_ATTEMPTS
        raise ApiError(f"Keep going a bit longer: the solution unlocks after {need} checks "
                       f"or {REVEAL_AFTER_SECONDS // 60} minutes of trying.")
    state["revealed"] = 1
    progress.save_state(state)
    return {"revealed": _revealed_payload(ex)}


def api_run_snippet(body: dict):
    code = body.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ApiError("code required")
    return runner.run_code({"snippet.py": code[:20000]}, main="snippet.py", stdin=body.get("stdin", ""))


def api_lesson_read(topic_id: str, body: dict):
    if topic_id not in content.load()["topics_by_id"]:
        raise ApiError("topic not found", 404)
    if body.get("unread"):
        db.ex("DELETE FROM lesson_state WHERE topic_id=?", (topic_id,))
    else:
        db.ex("INSERT OR REPLACE INTO lesson_state(topic_id, read_at) VALUES(?,?)", (topic_id, db.now()))
    return {"ok": True}


# --------------------------------------------------------------------------- library

def _library_entry(t: dict, number: int, unlocked: bool) -> dict:
    """One Library row. A locked chapter gives away nothing but its title."""
    entry = {"id": t["id"], "title": t["title"], "module": t["track"], "number": number, "unlocked": unlocked}
    if unlocked:
        entry |= {"summary": " ".join(t["summary"].replace("`", "").split()), "concepts": t.get("concepts", []),
                  "keywords": t["reference"]["keywords"], "cards": t["reference"]["cards"]}
    return entry


def api_library(_=None):
    """Reference cards for the chapters whose lesson is finished, plus locked placeholders."""
    data = content.load()
    tp = progress.topic_progress()
    entries = [_library_entry(t, i + 1, tp[t["id"]]["library_unlocked"]) for i, t in enumerate(data["topics"])]
    return {"unlocked": sum(e["unlocked"] for e in entries), "total": len(entries), "entries": entries,
            "modules": [{"id": m["id"], "title": m["title"]} for m in data["modules"]]}


def api_library_entry(topic_id: str):
    data = content.load()
    t = data["topics_by_id"].get(topic_id)
    if not t:
        raise ApiError("topic not found", 404)
    if not progress.topic_progress()[topic_id]["library_unlocked"]:
        raise ApiError("This Library entry is locked. Finish the chapter to unlock it.", 403)
    return {"entry": _library_entry(t, data["topics"].index(t) + 1, True)}


def api_explain_solution(body: dict):
    ex = _exercise(body.get("item_id", ""))
    if not progress.get_state(ex["id"]).get("revealed"):
        raise ApiError("reveal the solution first")
    return {"explanation": coach.explain_solution(_task_text(ex), ex["solution"],
                                                  _files(body) if body.get("files") else {})}


def api_exam(module_id: str):
    data = content.load()
    exam = data["exams_by_module"].get(module_id)
    if not exam:
        raise ApiError("module test not found", 404)
    states = progress.exercise_states()
    m = data["modules_by_id"][module_id]
    return {"exam": {k: exam[k] for k in ("module", "title", "intro")} | {"pass_ratio": exam.get("pass_ratio", 0.7)},
            "module": {k: m[k] for k in ("id", "title", "summary")},
            "status": course.exam_status(module_id, states),
            "exercises": [{"id": e, "title": data["exercises"][e]["title"],
                           "difficulty": data["exercises"][e]["difficulty"],
                           "research": bool(data["exercises"][e].get("research")),
                           "status": states.get(e, {}).get("status", "new")} for e in exam["exercise_ids"]]}


def api_explain_back(body: dict):
    """Grade the learner's own explanation of a step they solved."""
    ex = _exercise(body.get("item_id", ""))
    if progress.get_state(ex["id"])["status"] != "solved":
        raise ApiError("Solve it first, then explain why your solution works.")
    text = str(body.get("text", "")).strip()
    if len(text) < 40:
        raise ApiError("Write at least a couple of sentences: what your code does, and why that gives the right answer.")
    return {"result": coach.explain_back(ex["id"], _task_text(ex), _files(body), text[:4000])}


def api_improve(body: dict):
    ex = _exercise(body.get("item_id", ""))
    if progress.get_state(ex["id"])["status"] != "solved":
        raise ApiError("Solve it first. Then I'll show you ways to make it even better.")
    files = _files(body)
    return {"advice": coach.improve_solution(_task_text(ex), files, ex["solution"])}


def _real_llm(body: dict):
    """The model callable for Run when the learner ticked "Real model calls", else None."""
    if not body.get("real_llm"):
        return None
    if ai.current().get("provider", "none") == "none":
        raise ApiError("Real model calls need an AI connection: connect one in Settings.")
    return lambda prompt, system: ai.complete(system, prompt, timeout=120)


def api_run(ex_id: str, body: dict):
    ex = _exercise(ex_id)
    if ex.get("mode") in READ_ONLY:
        st = progress.get_state(ex_id)
        if st["status"] != "solved" and not st.get("revealed"):
            raise ApiError("Running is unlocked once you've answered (that's the exercise!).")
        return runner.run_code({"solution.py": ex["code"]}, setup_files=ex.get("setup_files"))
    files = _files(body)
    if ex.get("mode") == "tests":
        files = {**files, "target.py": ex["impl"]}
    return runner.run_code(files, stdin=body.get("stdin", ""), setup_files=ex.get("setup_files"),
                           args=[str(a) for a in body.get("args", [])][:20], llm=_real_llm(body))


def _variant_test_names(tests: str) -> list[str]:
    return [n.removeprefix("test_").replace("_", " ") for n in re.findall(r"^def (test_\w+)", tests, re.M)]


def api_variant(ex_id: str):
    """The changed-form version of a review, if one is ready (never its solution or tests)."""
    ex = _exercise(ex_id)
    v = variants.get(ex_id) if variants.eligible(ex) else None
    if not v:
        return {"variant": None, "enabled": variants.enabled()}
    return {"variant": {"title": v["title"], "prompt": v["prompt"], "starter": v["starter"]},
            "checks": _variant_test_names(v["tests"]),
            "debug_call": tracer.suggest_call(v["solution"], v["tests"]) if ex.get("mode", "function") == "function" else "",
            "enabled": variants.enabled()}


def api_trace(ex_id: str, body: dict):
    """Step through the learner's file (or, for read-and-predict steps, the program once it's unlocked)."""
    ex = _exercise(ex_id)
    call = str(body.get("call") or "")[:2000]
    if ex.get("mode") in READ_ONLY:
        st = progress.get_state(ex_id)
        if st["status"] != "solved" and not st.get("revealed"):
            raise ApiError("Stepping through is unlocked once you've answered.")
        return tracer.trace_code({"solution.py": ex["code"]}, setup_files=ex.get("setup_files"))
    files = _files(body)
    if ex.get("mode") == "tests":
        files = {**files, "target.py": ex["impl"]}
    return tracer.trace_code(files, call=call, stdin=str(body.get("stdin", ""))[:20000],
                             setup_files=ex.get("setup_files"))


def _grade(ex: dict, body: dict) -> tuple[dict, dict]:
    """Run the right kind of check; returns (files_to_store, result)."""
    if ex.get("mode") == "predict":
        answer = str(body.get("answer", ""))[:5000]
        result = runner.check_prediction(ex["code"], answer, setup_files=ex.get("setup_files"))
        result.pop("_actual", None)
        return {"answer.txt": answer}, result
    if ex.get("mode") == "traceback":
        result = _check_traceback(ex, body.get("answer"))
        return {"answer.txt": str(body.get("answer"))}, result
    files = _files(body)
    if ex.get("mode") == "tests":
        return files, runner.grade_test_writing(files.get("solution.py", ""), ex["impl"], ex["mutants"],
                                                setup_files=ex.get("setup_files"))
    return files, runner.run_tests(files, ex["tests"], mode=ex.get("mode", "function"),
                                   setup_files=ex.get("setup_files"))


def api_check(ex_id: str, body: dict):
    ex = _exercise(ex_id)
    kind = body.get("kind", "practice")
    if kind not in ("practice", "review"):
        kind = "practice"
    variant = variants.get(ex_id) if body.get("variant") and kind == "review" else None
    if body.get("variant") and kind == "review" and not variant:
        raise ApiError("This changed-form review is no longer available. Reload the page to review the original.")
    if variant:
        # Graded against the variant's own tests; it still counts as a review of the original step.
        files = _files(body)
        result = runner.run_tests(files, variant["tests"], mode=ex.get("mode", "function"),
                                  setup_files=ex.get("setup_files"))
        ex_view = {**ex, "title": variant["title"], "prompt": variant["prompt"], "solution": variant["solution"]}
    else:
        files, result = _grade(ex, body)
        ex_view = ex
    if result["status"] == "passed" and ex.get("mode") not in READ_ONLY:
        result["quality"] = _quality(ex_view, files.get("solution.py", ""))
    state = progress.record_attempt(ex, files, result, kind, body.get("duration_s", 0))
    if variant and result["status"] == "passed":
        variants.drop(ex_id)  # the next review gets a fresh one
    if result["status"] == "passed" and ex.get("mode") in READ_ONLY:
        result["explanation"] = ex.get("explanation", "")
    tp = progress.topic_progress()
    topic = ex.get("topic")
    style = lint.check(files.get("solution.py", "")) if result["status"] == "passed" else []
    passed = result["status"] == "passed"
    exam = None
    if ex.get("topic") == "exam":
        placed_now = passed and course.place_module_if_exam_passed(ex["module"])
        exam = course.exam_status(ex["module"]) | {"placed_now": placed_now}
    return {"result": result, "state": state, "style": style, "exam": exam,
            "reference": ex_view["solution"] if passed and ex.get("mode") != "predict" else None,
            "tips": _quality_tips(result.get("quality")) if passed else [],
            "can_reveal": _can_reveal(ex, state, int(body.get("duration_s", 0))),
            "topic_progress": tp.get(topic) if topic in tp else None}


def api_draft(body: dict):
    item = body.get("item_id")
    if not item:
        raise ApiError("item_id required")
    files = _files(body)
    db.ex("INSERT INTO drafts(item_id, files, updated_at) VALUES(?,?,?) ON CONFLICT(item_id) DO UPDATE SET "
          "files=excluded.files, updated_at=excluded.updated_at", (item, json.dumps(files), db.now()))
    return {"ok": True}


def api_reset_draft(body: dict):
    db.ex("DELETE FROM drafts WHERE item_id=?", (body.get("item_id"),))
    return {"ok": True}


def api_heartbeat(body: dict):
    progress.add_seconds(body.get("seconds", 0))
    return {"ok": True}


def api_reviews(_=None):
    exs = progress.all_exercises()
    if variants.enabled():
        variants.prepare(exs)
    ready = variants.ready_ids()
    return {"due": [r | {"variant": r["id"] in ready} for r in progress.due_reviews()],
            "variants_on": variants.enabled(),
            "upcoming": [dict(r) | {"title": exs.get(r["exercise_id"], {}).get("title", r["exercise_id"])} for r in db.q(
                "SELECT exercise_id, next_review FROM exercise_state WHERE status='solved' AND next_review > ? "
                "ORDER BY next_review LIMIT 15", (db.today(),))]}


def api_stats(_=None):
    data = content.load()
    states = progress.exercise_states()
    tp = progress.topic_progress(states)
    recent = db.q("SELECT id, item_id, kind, status, passed, total, duration_s, created_at FROM attempts "
                  "ORDER BY id DESC LIMIT 40")
    exs = progress.all_exercises()
    per_day = db.q("SELECT substr(created_at,1,10) d, COUNT(*) n, SUM(status='passed') p FROM attempts "
                   "GROUP BY d ORDER BY d DESC LIMIT 30")
    placement = db.q1("SELECT * FROM placement WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1")
    awards = _rewards()
    ach = achievements.overview()
    parts = xp.breakdown()
    return {
        **awards,
        "xp": {**xp.summary(sum(parts.values())), "breakdown": parts},
        "summary": progress.summary(),
        "achievements": {k: ach[k] for k in ("unlocked", "total", "recent")},
        "heatmap": progress.heatmap(140),
        "topics": [{"id": t["id"], "title": t["title"], "track": t["track"], **tp[t["id"]]} for t in data["topics"]],
        "recent": [dict(r) | {"title": exs.get(r["item_id"], {}).get("title", r["item_id"])} for r in recent],
        "per_day": [dict(r) for r in per_day][::-1],
        "weak_spots": progress.weak_spots(8),
        "placement": ({"finished_at": placement["finished_at"],
                       "report": json.loads(placement["report"]) if placement["report"] else None}
                      if placement else None),
        "projects": [dict(r) | {"result": json.loads(r["result"]).get("status")} for r in
                     db.q("SELECT id, project_id, result, created_at FROM submissions ORDER BY id DESC LIMIT 20")],
    }


# --------------------------------------------------------------------------- placement

# Adaptive placement: topics are visited in curriculum order, and each topic climbs a
# three-step ladder: a warm-up (a starter step), an easy exercise, then the core question
# (a medium one). A topic's climb stops at the first miss. Passing the core question places
# the topic. The test pauses once several topics in a row are clearly out of reach - you can
# choose to keep going anyway, since later topics don't always depend on the ones you missed.
PLACEMENT_STOP_AT = 3.0
STAGES = ["warm-up", "easy", "core"]
OUTCOMES = ["unknown", "basics", "partial", "placed"]
MISS_COST = {"unknown": 1.0, "basics": 0.5, "partial": 0.25, "placed": 0.0}


def _placement_ladder() -> list[tuple[dict, list[str]]]:
    data = content.load()
    ladder = []
    for t in data["topics"]:
        exs = [data["exercises"][e] for e in t["exercise_ids"]]
        core = next((e for e in exs if e["placement"]), exs[len(exs) // 2])
        starters = [e for e in exs if e["difficulty"] == 0 and e.get("mode") != "predict"]
        easy = next((e for e in exs if e["difficulty"] == 1 and e["id"] != core["id"]), None)
        steps = [e["id"] for e in (starters[-1] if starters else None, easy, core) if e]
        ladder.append((t, list(dict.fromkeys(steps))))
    return ladder


def _answer_passed(a: dict | None) -> bool:
    return bool(a and not a.get("skipped") and (a.get("result") or {}).get("status") == "passed")


def _placement_walk(answers: dict) -> dict:
    """Replay the answers through the ladder. Returns the next question + per-topic outcome."""
    outcomes, misses = {}, 0.0
    resets = set((answers.get("_meta") or {}).get("resets", []))
    ladder = _placement_ladder()
    for i, (t, steps) in enumerate(ladder):
        if i in resets:
            misses = 0.0
        level = 0
        for step, eid in enumerate(steps):
            if eid not in answers:
                stage = STAGES[step + (3 - len(steps))] if len(steps) < 3 else STAGES[step]
                return {"next": eid, "stage": stage, "step": step + 1, "steps": len(steps),
                        "topic_index": i, "outcomes": outcomes, "done": False}
            if not _answer_passed(answers[eid]):
                break
            level = step + 1
        outcome = "placed" if level == len(steps) else OUTCOMES[min(level, 2)]
        outcomes[t["id"]] = outcome
        misses = 0.0 if outcome == "placed" else misses + MISS_COST[outcome]
        if misses >= PLACEMENT_STOP_AT and i + 1 < len(ladder) and (i + 1) not in resets:
            return {"next": None, "stage": None, "topic_index": i, "outcomes": outcomes, "done": True,
                    "stopped_early": True, "stopped_at": i}
    return {"next": None, "stage": None, "topic_index": len(ladder), "outcomes": outcomes, "done": True,
            "stopped_early": False}


def api_placement_continue(_body=None):
    row = db.q1("SELECT * FROM placement WHERE finished_at IS NULL ORDER BY id DESC LIMIT 1")
    if not row:
        raise ApiError("no placement test in progress")
    answers = json.loads(row["answers"])
    walk = _placement_walk(answers)
    if not walk.get("stopped_early"):
        raise ApiError("the test hasn't paused")
    meta = answers.setdefault("_meta", {})
    meta.setdefault("resets", []).append(walk["stopped_at"] + 1)
    db.ex("UPDATE placement SET answers=? WHERE id=?", (json.dumps(answers), row["id"]))
    return api_placement()


def api_placement(_=None):
    row = db.q1("SELECT * FROM placement ORDER BY id DESC LIMIT 1")
    data = content.load()
    if not row:
        return {"status": "none", "topics": len(data["topics"])}
    asked = json.loads(row["exercise_ids"])
    answers = json.loads(row["answers"])
    walk = _placement_walk(answers)
    items = []
    for eid in asked:
        ex = data["exercises"].get(eid)
        if not ex:
            continue
        a = answers.get(eid)
        result = (a or {}).get("result") or {}
        items.append({"id": eid, "title": ex["title"], "topic": ex["topic"],
                      "topic_title": data["topics_by_id"][ex["topic"]]["title"],
                      "difficulty": ex["difficulty"], "answered": a is not None,
                      "skipped": bool(a and a.get("skipped")), "passed": _answer_passed(a),
                      "score": f"{result['passed']}/{result['total']}" if result else None,
                      "quality": (a or {}).get("quality")})
    nxt = walk["next"]
    return {"status": "done" if row["finished_at"] else "in_progress", "id": row["id"],
            "started_at": row["started_at"], "finished_at": row["finished_at"], "items": items,
            "topics_total": len(data["topics"]), "topic_index": walk["topic_index"],
            "next": nxt, "next_stage": walk["stage"], "next_step": walk.get("step"),
            "next_steps": walk.get("steps"),
            "next_topic": data["topics_by_id"][data["exercises"][nxt]["topic"]]["title"] if nxt else None,
            "ready_to_finish": walk["done"], "stopped_early": walk.get("stopped_early", False),
            "outcomes": walk["outcomes"],
            "report": json.loads(row["report"]) if row["report"] else None}


def api_placement_start(_=None):
    db.ex("DELETE FROM placement WHERE finished_at IS NULL")
    db.ex("INSERT INTO placement(started_at, exercise_ids) VALUES(?,?)", (db.now(), "[]"))
    return api_placement()


def api_placement_answer(body: dict):
    row = db.q1("SELECT * FROM placement WHERE finished_at IS NULL ORDER BY id DESC LIMIT 1")
    if not row:
        raise ApiError("no placement test in progress")
    answers = json.loads(row["answers"])
    walk = _placement_walk(answers)
    eid = body.get("exercise_id")
    if eid != walk["next"]:
        raise ApiError("that isn't the current placement question - reload the page")
    ex = _exercise(eid)
    if body.get("skipped"):
        answers[eid] = {"skipped": True, "files": {}, "result": None}
        result = None
    else:
        files, result = _grade(ex, body)
        answers[eid] = {"skipped": False, "files": files, "result": result,
                        "duration_s": body.get("duration_s", 0),
                        "quality": _quality(ex, files.get("solution.py", ""))}
        progress.record_attempt(ex, files, result, "placement", body.get("duration_s", 0))
    asked = json.loads(row["exercise_ids"])
    if eid not in asked:
        asked.append(eid)
    db.ex("UPDATE placement SET answers=?, exercise_ids=? WHERE id=?",
          (json.dumps(answers), json.dumps(asked), row["id"]))
    return {"result": result, "quality": answers[eid].get("quality"), "placement": api_placement()}


def api_placement_finish(body: dict):
    row = db.q1("SELECT * FROM placement WHERE finished_at IS NULL ORDER BY id DESC LIMIT 1")
    if not row:
        raise ApiError("no placement test in progress")
    data = content.load()
    answers = json.loads(row["answers"])
    walk = _placement_walk(answers)
    entries = []
    for eid in json.loads(row["exercise_ids"]):
        ex = data["exercises"][eid]
        a = answers.get(eid) or {"skipped": True, "files": {}, "result": None}
        entries.append({"id": eid, "topic": ex["topic"], "title": ex["title"], "difficulty": ex["difficulty"],
                        "prompt": ex["prompt"], "skipped": a.get("skipped", True),
                        "code": (a.get("files") or {}).get("solution.py", ""), "result": a.get("result"),
                        "quality": a.get("quality")})
    for topic_id, outcome in walk["outcomes"].items():
        if outcome == "placed":
            db.ex("INSERT INTO topic_state(topic_id, placed, placed_at) VALUES(?,1,?) ON CONFLICT(topic_id) "
                  "DO UPDATE SET placed=1, placed_at=excluded.placed_at", (topic_id, db.now()))
    not_reached = [t["id"] for t in data["topics"] if t["id"] not in walk["outcomes"]]
    report = _offline_placement_report(entries, walk["outcomes"], not_reached)
    report["ai"] = False
    if ai.enabled() and body.get("use_ai", True) and any(not e["skipped"] for e in entries):
        try:
            report = coach.placement_report(entries, walk["outcomes"], not_reached) | {"ai": True, "offline": report}
        except ai.AIError as exc:
            report["ai_error"] = str(exc)
    report["outcomes"] = walk["outcomes"]
    report["not_reached"] = not_reached
    db.ex("UPDATE placement SET finished_at=?, report=? WHERE id=?", (db.now(), json.dumps(report), row["id"]))
    db.set_setting("onboarded", True)
    return api_placement()


def _offline_placement_report(entries: list[dict], outcomes: dict, not_reached: list[str]) -> dict:
    data = content.load()
    title = lambda t: data["topics_by_id"][t]["title"]  # noqa: E731
    placed = [t for t, o in outcomes.items() if o == "placed"]
    basics = [t for t, o in outcomes.items() if o in ("basics", "partial")]
    unknown = [t for t, o in outcomes.items() if o == "unknown"]
    by_track = {}
    for t in data["topics"]:
        by_track.setdefault(t["track"], []).append(outcomes.get(t["id"]) == "placed")
    frac = {k: sum(v) / len(v) for k, v in by_track.items()}
    if frac.get("fundamentals", 0) < 0.4:
        level = "Beginner"
    elif frac.get("fundamentals", 0) < 0.9:
        level = "Advanced beginner"
    elif frac.get("practical", 0) < 0.7:
        level = "Intermediate"
    elif frac.get("ai-ready", 0) < 0.7:
        level = "Upper intermediate"
    else:
        level = "Advanced"
    total = len(data["topics"])
    score = round(100 * (len(placed) + sum(0.6 if outcomes[t] == "partial" else 0.3 for t in basics)) / total)
    qualities = [e["quality"]["overall"] for e in entries if e.get("quality")]
    report = {
        "level": level, "score": score,
        "summary": (f"You placed out of {len(placed)} of {total} topics"
                    + (f", know the basics of {len(basics)} more" if basics else "")
                    + (f", and the test stopped after {len(outcomes)} topics once questions got consistently "
                       "out of reach" if not_reached else "") + "."),
        "strengths": [title(t) for t in placed],
        "gaps": [title(t) + (" (basics only)" if t in basics else "") for t in basics + unknown],
        "start_with": (basics + unknown + not_reached)[:3],
    }
    if qualities:
        avg = round(sum(qualities) / len(qualities), 1)
        report["code_quality"] = f"Average code quality across your answers: {avg}/10 (scored by Jev)."
    return report


# --------------------------------------------------------------------------- AI

def api_ai_providers(_=None):
    return {"providers": ai.detect(), "current": ai.current()}


def api_settings(body: dict):
    if "ai" in body:
        cfg = body["ai"]
        if cfg.get("provider") not in ("none", *ai.PROVIDERS):
            raise ApiError("unknown provider")
        db.set_setting("ai", {"provider": cfg["provider"], "model": str(cfg.get("model") or "")[:120]})
    if "daily_goal" in body:
        db.set_setting("daily_goal", max(15, min(int(body["daily_goal"]), 480)))
    if "name" in body:
        db.set_setting("name", str(body["name"])[:40])
    if "onboarded" in body:
        db.set_setting("onboarded", bool(body["onboarded"]))
    if "jev_enabled" in body:
        db.set_setting("jev_enabled", bool(body["jev_enabled"]))
    if "review_variants" in body:
        db.set_setting("review_variants", bool(body["review_variants"]))
    return api_state()


def api_jev_key(body: dict):
    new_key = (body.get("key") or "").strip()
    if body.get("remove"):
        db.ex("DELETE FROM settings WHERE key='jev_key'")
        return api_state()
    if not new_key:
        raise ApiError("paste your Jev API key")
    try:
        answers = jev.ask("def add(a, b):\n    return a + b",
                          {"is_python": {"type": "noul", "instructions": "Is this Python code?"}},
                          api_key=new_key, timeout=20)
    except jev.JevError as exc:
        raise ApiError(str(exc)) from None
    if "is_python" not in answers:
        raise ApiError("Jev answered, but not in the expected format.")
    db.set_setting("jev_key", new_key)
    db.set_setting("jev_enabled", True)
    return api_state()


def api_ai_test(body: dict):
    provider = body.get("provider")
    model = body.get("model", "")
    text = ai.complete("You are a connectivity check.", "Reply with exactly the word: ready",
                       provider=provider, model=model, timeout=120)
    return {"ok": "ready" in text.lower(), "reply": text[:200]}


def api_tutor(body: dict):
    item = body.get("item_id", "")
    message = (body.get("message") or "").strip()
    if not message:
        raise ApiError("message required")
    if item.startswith("lesson:"):
        t = content.load()["topics_by_id"].get(item.split(":", 1)[1])
        if not t:
            raise ApiError("topic not found", 404)
        history = coach.lesson_reply(item, t["title"], t.get("lesson", ""), message[:4000])
        return {"chat": history}
    if item.startswith("project:"):
        p = content.load()["projects_by_id"].get(item.split(":", 1)[1])
        if not p:
            raise ApiError("project not found", 404)
        task = f"# Project: {p['title']}\n\n{p['brief']}"
    else:
        ex = _exercise(item)
        _no_help_in_tests(ex)
        task = _task_text(ex)
    history = coach.tutor_reply(item, task, body.get("files") or {}, body.get("result"), message[:4000])
    return {"chat": history}


def api_clear_chat(body: dict):
    db.ex("DELETE FROM chats WHERE item_id=?", (body.get("item_id"),))
    return {"ok": True}


def api_review(body: dict):
    ex = _exercise(body.get("item_id", ""))
    files = _files(body)
    return {"review": coach.review_code(ex["id"], _task_text(ex), files, body.get("result"))}


def api_generate(body: dict):
    data = content.load()
    topic = data["topics_by_id"].get(body.get("topic"))
    if not topic:
        raise ApiError("unknown topic")
    difficulty = max(1, min(int(body.get("difficulty", 2)), 3))
    avoid = [e["title"] for e in progress.all_exercises().values() if e.get("topic") == topic["id"]]
    ex = coach.generate_exercise(topic, difficulty, progress.weak_spots(), avoid)
    return {"id": ex["id"]}


def api_coach(_=None):
    return {"advice": coach.coach_advice(progress.coach_snapshot())}


# --------------------------------------------------------------------------- projects

def _project(pid: str) -> dict:
    p = content.load()["projects_by_id"].get(pid)
    if not p:
        raise ApiError("project not found", 404)
    return p


def api_projects(_=None):
    data = content.load()
    tp = progress.topic_progress()
    subs = {}
    for r in db.q("SELECT project_id, result, review FROM submissions ORDER BY id"):
        res = json.loads(r["result"])
        s = subs.setdefault(r["project_id"], {"submissions": 0, "passed": False, "best": 0, "score": None})
        s["submissions"] += 1
        s["passed"] = s["passed"] or res.get("status") == "passed"
        s["best"] = max(s["best"], res.get("passed", 0))
        if r["review"]:
            s["score"] = json.loads(r["review"]).get("score")
    return {"projects": [{
        "id": p["id"], "title": p["title"], "level": p["level"], "order": p["order"], "module": p.get("module"),
        "estimated_hours": p["estimated_hours"], "tags": p.get("tags", []),
        "requires": [{"id": r, "title": data["topics_by_id"][r]["title"], "cleared": tp[r]["cleared"]}
                     for r in p["requires"] if r in data["topics_by_id"]],
        "ready": all(tp.get(r, {}).get("cleared") for r in p["requires"]),
        **subs.get(p["id"], {"submissions": 0, "passed": False, "best": 0, "score": None}),
    } for p in data["projects"]],
        "chapter_projects": [{"id": m["id"], "title": m["title"], "chapter": m["chapter"],
                              "chapter_title": data["topics_by_id"][m["chapter"]]["title"], "module": m["module"],
                              "estimated_hours": m.get("estimated_hours"),
                              **subs.get(m["id"], {"submissions": 0, "passed": False, "best": 0, "score": None})}
                             for m in data["minis"]]}


def api_project(pid: str):
    p = _project(pid)
    subs = db.q("SELECT id, result, review, created_at FROM submissions WHERE project_id=? ORDER BY id DESC",
                (pid,))
    draft = db.q1("SELECT files FROM drafts WHERE item_id=?", ("project:" + pid,))
    chat = db.q1("SELECT messages FROM chats WHERE item_id=?", ("project:" + pid,))
    folder = PROJECTS_DIR / pid
    return {
        "project": {k: p.get(k) for k in ("id", "title", "level", "estimated_hours", "tags", "brief", "explore",
                                          "rubric", "files", "main", "starter_files", "module", "kind", "chapter")},
        "chapter_title": (content.load()["topics_by_id"][p["chapter"]]["title"] if p.get("chapter") else None),
        "next_chapter": course.next_chapter(p["chapter"]) if p.get("chapter") else None,
        "submissions": [{"id": s["id"], "created_at": s["created_at"], "result": json.loads(s["result"]),
                         "review": json.loads(s["review"]) if s["review"] else None} for s in subs],
        "draft": json.loads(draft["files"]) if draft else None,
        "chat": json.loads(chat["messages"]) if chat else [],
        "folder": str(folder), "folder_exists": folder.is_dir(),
        "builds_on": _builds_on(p),
    }


def _builds_on(p: dict) -> list[dict] | None:
    """For a capstone: the projects whose passing code runs next to it, and whether each has passed."""
    if not p.get("requires_projects"):
        return None
    data = content.load()
    passed = progress.passed_projects()
    return [{"id": pid, "title": data["projects_by_id"][pid]["title"], "files": data["projects_by_id"][pid]["files"],
             "passed": pid in passed} for pid in p["requires_projects"]]


def _with_provided(p: dict, files: dict) -> dict:
    """Add the learner's passing code from the projects a capstone builds on (their own files win)."""
    if not p.get("requires_projects"):
        return files
    provided, missing = capstone.provided_files(p)
    if missing:
        raise ApiError("This project runs on your own code from earlier projects. Pass these first: "
                       + ", ".join(missing))
    return {**provided, **files}


def api_project_scaffold(pid: str, _body=None):
    p = _project(pid)
    folder = PROJECTS_DIR / pid
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for name, code in p["starter_files"].items():
        dest = folder / name
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(code)
            written.append(name)
    if p.get("requires_projects"):
        provided, _missing = capstone.provided_files(p)
        for name, code in {**provided, **p.get("setup_files", {})}.items():
            dest = folder / name
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(code)
                written.append(name)
    readme = folder / "BRIEF.md"
    readme.write_text(f"# {p['title']}\n\n{p['brief']}\n\n---\n\n## Explore\n\n{p['explore']}")
    return {"folder": str(folder), "written": written}


def api_project_load_folder(pid: str, _body=None):
    p = _project(pid)
    folder = PROJECTS_DIR / pid
    if not folder.is_dir():
        raise ApiError(f"{folder} does not exist yet")
    files = {}
    for name in p["files"]:
        f = folder / name
        if f.is_file():
            files[name] = f.read_text(errors="replace")
    if not files:
        raise ApiError("none of the required files were found in the folder")
    return {"files": files}


def api_project_run(pid: str, body: dict):
    p = _project(pid)
    files = _files(body)
    main = body.get("file") or p.get("main", "app.py")
    if main not in files:
        raise ApiError(f"{main} isn't one of your files")
    return runner.run_code(_with_provided(p, files), main=main, stdin=str(body.get("stdin", ""))[:20000],
                           args=[str(a) for a in body.get("args", [])][:20], timeout=15,
                           setup_files=p.get("setup_files") or None, llm=_real_llm(body))


def api_project_submit(pid: str, body: dict):
    p = _project(pid)
    files = _files(body)
    missing = [f for f in p["files"] if f not in files]
    if missing:
        raise ApiError("missing required files: " + ", ".join(missing))
    total = sum(len(c) for c in files.values())
    if total > 400_000:
        raise ApiError("submission too large")
    result = runner.run_tests(_with_provided(p, files), p["tests"], mode="function", main=p.get("main", "app.py"),
                              timeout=90, setup_files=p.get("setup_files") or None)
    result["style"] = {name: lint.check(code) for name, code in files.items() if name.endswith(".py")}
    sid = db.ex("INSERT INTO submissions(project_id, files, result, created_at) VALUES(?,?,?,?)",
                (pid, json.dumps(files), json.dumps(result), db.now()))
    db.ex("INSERT INTO attempts(item_id, kind, files, status, passed, total, duration_s, result, created_at) "
          "VALUES(?,?,?,?,?,?,?,?,?)", ("project:" + pid, "project", json.dumps(files), result["status"],
                                         result["passed"], result["total"], 0, json.dumps(result), db.now()))
    db.ex("INSERT INTO activity(day, seconds, solved, checks) VALUES(?,0,0,1) ON CONFLICT(day) DO UPDATE SET "
          "checks = checks + 1", (db.today(),))
    return {"submission_id": sid, "result": result,
            "next_chapter": course.next_chapter(p["chapter"]) if p.get("chapter") else None}


def api_project_review(pid: str, body: dict):
    p = _project(pid)
    row = db.q1("SELECT * FROM submissions WHERE id=? AND project_id=?", (body.get("submission_id"), pid))
    if not row:
        raise ApiError("submission not found", 404)
    review = coach.review_project(p, json.loads(row["files"]), json.loads(row["result"]))
    db.ex("UPDATE submissions SET review=? WHERE id=?", (json.dumps(review), row["id"]))
    return {"review": review}


# --------------------------------------------------------------------------- labs

def _interview(fn, *args):
    try:
        return fn(*args)
    except ValueError as exc:
        raise ApiError(str(exc)) from None


def api_interviews(_=None):
    return {"history": interview.history(), "lengths": list(interview.LENGTHS)}


def api_interview_start(body: dict):
    return _interview(interview.start, int(body.get("minutes", 30)))


def api_interview_submit(iid: str, body: dict):
    return {"result": _interview(interview.submit, int(iid), _files(body), int(body.get("seconds", 0)))}


def api_interview_followup(iid: str, body: dict):
    answer = body.get("answer")
    return _interview(interview.followup, int(iid), str(answer) if answer is not None else None)


def api_interview_debrief(iid: str, _body=None):
    return {"debrief": _interview(interview.debrief, int(iid))}


def api_radar(_=None):
    return radar.analyse() | {"mistake_drill": mistakes.last_drill(), "mistakes": len(mistakes.recent_mistakes())}


def api_mistake_drill(_body=None):
    try:
        return mistakes.make_drill()
    except ValueError as exc:
        raise ApiError(str(exc)) from None


def api_drill(_=None):
    exercises = drills.pool()
    return {"pool": exercises, "enough": len(exercises) >= drills.MIN_POOL, "min": drills.MIN_POOL} | drills.stats()


def api_drill_check(body: dict):
    """Grade a drill answer. Not recorded: drills never change stats or the review schedule."""
    ex = _exercise(str(body.get("id", "")))
    if ex.get("mode", "function") not in drills.MODES:
        raise ApiError("This step can't be drilled.")
    files, result = _grade(ex, body)
    return {"result": result}


def api_drill_finish(body: dict):
    try:
        return drills.finish(int(body.get("seconds", 0)), int(body.get("solved", 0)), int(body.get("skipped", 0)),
                             int(body.get("best_streak", 0)))
    except ValueError as exc:
        raise ApiError(str(exc)) from None


def api_leaderboard(_=None):
    return leaderboard.overview()


def api_traces_parse(body: dict):
    """The trace viewer page: spans from a JSON Lines file the learner opened or pasted."""
    text = str(body.get("text") or "")
    if len(text) > spans.MAX_BYTES:
        raise ApiError("That file is too big for the viewer (2 MB at most).")
    found = spans.parse(text)
    if not found:
        raise ApiError("No spans found. Each line should be a JSON object with a name, start and end.")
    return {"spans": found}


def api_traces_sample(_=None):
    return {"spans": spans.parse(spans.SAMPLE)}


def api_achievements(_=None):
    awards = _rewards()
    return {**achievements.overview(), **awards}


def _rewards() -> dict:
    """What an action just earned, merged into its response: new achievements (`awards`) and XP
    gained (`xp_gain`, with `level_up`). The browser celebrates both."""
    out = {}
    new = achievements.check()
    if new:
        out["awards"] = new
    gain = xp.gained()
    if gain:
        out["xp_gain"] = gain
    return out


def api_leaderboard_run(_body=None):
    try:
        return leaderboard.run()
    except ValueError as exc:
        raise ApiError(str(exc)) from None


def api_capstone(_=None):
    return capstone.status()


def api_capstone_export(_body=None):
    try:
        return capstone.export()
    except ValueError as exc:
        raise ApiError(str(exc)) from None


def api_labs(_=None):
    data = content.load()
    states = {r["lab_id"]: dict(r) for r in db.q("SELECT * FROM lab_state")}
    return {"root": str(labs.LAB_ROOT), "labs": [{
        "id": lab["id"], "title": lab["title"], "brief": lab["brief"], "order": lab["order"],
        "checks": [c["label"] for c in lab["checks"]],
        "done": bool(states.get(lab["id"], {}).get("done")),
        "last_result": json.loads(states[lab["id"]]["last_result"]) if states.get(lab["id"], {}).get("last_result") else None,
    } for lab in sorted(data["labs"], key=lambda x: x["order"])]}


def api_lab_check(lab_id: str, _body=None):
    lab = content.load()["labs_by_id"].get(lab_id)
    if not lab:
        raise ApiError("lab not found", 404)
    res = labs.check_lab(lab)
    prev = db.q1("SELECT done FROM lab_state WHERE lab_id=?", (lab_id,))
    done = res["passed"] or bool(prev and prev["done"])
    db.ex("INSERT INTO lab_state(lab_id, done, last_result, done_at) VALUES(?,?,?,?) ON CONFLICT(lab_id) DO UPDATE "
          "SET done=excluded.done, last_result=excluded.last_result, done_at=COALESCE(lab_state.done_at, excluded.done_at)",
          (lab_id, int(done), json.dumps(res), db.now() if res["passed"] else None))
    return res


# --------------------------------------------------------------------------- misc

def api_export(_=None):
    return db.export_all()


def api_reset(body: dict):
    if body.get("confirm") != "RESET":
        raise ApiError("type RESET to confirm")
    db.reset_all()
    return {"ok": True}


def api_unplace(body: dict):
    db.ex("UPDATE topic_state SET placed=0 WHERE topic_id=?", (body.get("topic_id"),))
    return {"ok": True}


ROUTES = [
    ("GET", r"/api/state", api_state),
    ("GET", r"/api/topic/([\w-]+)", api_topic),
    ("GET", r"/api/exercise/([\w-]+)", api_exercise),
    ("POST", r"/api/exercise/([\w-]+)/run", api_run),
    ("POST", r"/api/exercise/([\w-]+)/check", api_check),
    ("POST", r"/api/exercise/([\w-]+)/trace", api_trace),
    ("GET", r"/api/exercise/([\w-]+)/variant", api_variant),
    ("POST", r"/api/exercise/([\w-]+)/hint", api_hint),
    ("POST", r"/api/exercise/([\w-]+)/reveal", api_reveal),
    ("POST", r"/api/run", api_run_snippet),
    ("GET", r"/api/exam/([\w-]+)", api_exam),
    ("POST", r"/api/ai/improve", api_improve),
    ("POST", r"/api/ai/explain-back", api_explain_back),
    ("POST", r"/api/lesson/([\w-]+)/read", api_lesson_read),
    ("GET", r"/api/library", api_library),
    ("GET", r"/api/library/([\w-]+)", api_library_entry),
    ("POST", r"/api/ai/explain", api_explain_solution),
    ("POST", r"/api/draft", api_draft),
    ("POST", r"/api/draft/reset", api_reset_draft),
    ("POST", r"/api/heartbeat", api_heartbeat),
    ("GET", r"/api/reviews", api_reviews),
    ("GET", r"/api/stats", api_stats),
    ("GET", r"/api/placement", api_placement),
    ("POST", r"/api/placement/start", api_placement_start),
    ("POST", r"/api/placement/answer", api_placement_answer),
    ("POST", r"/api/placement/finish", api_placement_finish),
    ("POST", r"/api/placement/continue", api_placement_continue),
    ("GET", r"/api/ai/providers", api_ai_providers),
    ("POST", r"/api/settings", api_settings),
    ("POST", r"/api/ai/test", api_ai_test),
    ("POST", r"/api/jev/key", api_jev_key),
    ("POST", r"/api/ai/tutor", api_tutor),
    ("POST", r"/api/ai/tutor/clear", api_clear_chat),
    ("POST", r"/api/ai/review", api_review),
    ("POST", r"/api/ai/generate", api_generate),
    ("POST", r"/api/ai/coach", api_coach),
    ("GET", r"/api/projects", api_projects),
    ("GET", r"/api/project/([\w-]+)", api_project),
    ("POST", r"/api/project/([\w-]+)/scaffold", api_project_scaffold),
    ("POST", r"/api/project/([\w-]+)/load-folder", api_project_load_folder),
    ("POST", r"/api/project/([\w-]+)/run", api_project_run),
    ("POST", r"/api/project/([\w-]+)/submit", api_project_submit),
    ("POST", r"/api/project/([\w-]+)/review", api_project_review),
    ("GET", r"/api/interviews", api_interviews),
    ("POST", r"/api/interview/start", api_interview_start),
    ("POST", r"/api/interview/(\d+)/submit", api_interview_submit),
    ("POST", r"/api/interview/(\d+)/followup", api_interview_followup),
    ("POST", r"/api/interview/(\d+)/debrief", api_interview_debrief),
    ("GET", r"/api/radar", api_radar),
    ("POST", r"/api/ai/mistakes", api_mistake_drill),
    ("GET", r"/api/drill", api_drill),
    ("POST", r"/api/drill/check", api_drill_check),
    ("POST", r"/api/drill/finish", api_drill_finish),
    ("GET", r"/api/leaderboard", api_leaderboard),
    ("POST", r"/api/leaderboard/run", api_leaderboard_run),
    ("POST", r"/api/traces/parse", api_traces_parse),
    ("GET", r"/api/traces/sample", api_traces_sample),
    ("GET", r"/api/achievements", api_achievements),
    ("GET", r"/api/capstone", api_capstone),
    ("POST", r"/api/capstone/export", api_capstone_export),
    ("GET", r"/api/labs", api_labs),
    ("POST", r"/api/lab/([\w-]+)/check", api_lab_check),
    ("GET", r"/api/export", api_export),
    ("POST", r"/api/reset", api_reset),
    ("POST", r"/api/unplace", api_unplace),
]
COMPILED = [(m, re.compile(p + r"$"), fn) for m, p, fn in ROUTES]
# Actions that can earn an achievement: their responses carry anything newly earned.
REWARDING = {api_check, api_project_submit, api_lab_check, api_drill_finish, api_interview_submit,
             api_leaderboard_run, api_explain_back, api_heartbeat, api_placement_finish}


class Handler(BaseHTTPRequestHandler):
    server_version = "PyTrainer/" + VERSION

    def log_message(self, fmt, *args):
        if "--verbose" in sys.argv:
            super().log_message(fmt, *args)

    def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj):
        self._send(status, json.dumps(obj).encode(), "application/json; charset=utf-8")

    def _dispatch(self, method: str):
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            return self._static(path) if method == "GET" else self._json(404, {"error": "not found"})
        # Only accept same-origin requests: blocks other websites from driving the local API.
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "")
        if not _allowed_host(host.rsplit(":", 1)[0].lower()):
            return self._json(403, {"error": "unexpected Host header"})
        if origin and urlparse(origin).netloc != host:
            return self._json(403, {"error": "cross-origin request refused"})
        if method == "POST" and self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self._json(415, {"error": "expected application/json"})
        for m, rx, fn in COMPILED:
            match = rx.match(path)
            if m == method and match:
                try:
                    body = None
                    if method == "POST":
                        length = int(self.headers.get("Content-Length") or 0)
                        if length > MAX_BODY:
                            raise ApiError("request too large", 413)
                        raw = self.rfile.read(length) if length else b"{}"
                        body = json.loads(raw or b"{}")
                        if not isinstance(body, dict):
                            raise ApiError("expected a JSON object")
                    args = list(match.groups())
                    if method == "POST":
                        args.append(body)
                    result = fn(*args) if args else fn()
                    if fn in REWARDING and isinstance(result, dict):
                        result = {**result, **_rewards()}
                    return self._json(200, result)
                except ApiError as exc:
                    return self._json(exc.status, {"error": str(exc)})
                except ai.AIError as exc:
                    return self._json(502, {"error": str(exc)})
                except json.JSONDecodeError:
                    return self._json(400, {"error": "invalid JSON"})
                except Exception as exc:  # noqa: BLE001 - report, keep serving
                    traceback.print_exc()
                    return self._json(500, {"error": f"{type(exc).__name__}: {exc}"})
        return self._json(404, {"error": "not found"})

    def _static(self, path: str):
        if path in ("/", "") or not Path(path).suffix:
            path = "/index.html"
        target = (STATIC / path.lstrip("/")).resolve()
        if not str(target).startswith(str(STATIC.resolve())) or not target.is_file():
            return self._json(404, {"error": "not found"})
        # .js is pinned: Windows registry settings can map it to text/plain, which browsers refuse
        # to run as a module.
        ctype = "text/javascript" if target.suffix == ".js" else (
            mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
            ctype += "; charset=utf-8"
        self._send(200, target.read_bytes(), ctype)

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")


def main():
    ap = argparse.ArgumentParser(description="PyTrainer local server")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--open", action="store_true", help="open the app in your browser once it is up")
    args = ap.parse_args()
    db.conn()
    db.backup()
    content.load()
    print(f"Code sandbox: {sandbox.level()}", flush=True)
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    httpd.daemon_threads = True
    url = f"http://{args.host}:{args.port}/"
    print(f"PyTrainer running on {url}", flush=True)
    print(f"Data: {db.DATA_DIR}", flush=True)
    if args.open:
        threading.Timer(0.5, webbrowser.open, (url,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
