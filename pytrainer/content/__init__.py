"""Loads the built-in curriculum: topics + exercises, combo challenges, projects and labs.

Content lives in plain Python modules so it can be validated by actually running
every reference solution against its tests (see scripts/validate_content.py).
"""

from __future__ import annotations

import importlib
import pkgutil
import textwrap
from functools import lru_cache

from . import exams as _exams_pkg
from . import minis as _minis_pkg
from . import projects as _projects_pkg
from . import topics as _topics_pkg

from .modules import MODULES, PROJECT_MODULES

TRACKS = MODULES  # a "track" is a module of the course

EXERCISE_FIELDS = {"id", "title", "difficulty", "prompt", "starter", "tests", "solution"}


def _clean(text: str) -> str:
    return textwrap.dedent(text).strip("\n") + "\n" if text else ""


def _norm_exercise(ex: dict, topic_id: str | None = None) -> dict:
    missing = EXERCISE_FIELDS - ex.keys()
    if missing:
        raise ValueError(f"exercise {ex.get('id')} missing {missing}")
    out = dict(ex)
    for key in ("prompt", "starter", "tests", "solution", "code", "explanation", "lesson", "impl"):
        if key in out:
            out[key] = _clean(out[key])
    if "mutants" in out:
        out["mutants"] = [{"name": m["name"], "code": _clean(m["code"])} for m in out["mutants"]]
    if out.get("research"):
        r = out["research"]
        out["research"] = {"note": textwrap.dedent(r.get("note", "")).strip(), "links": r.get("links", [])}
    out.setdefault("mode", "function")
    out["hints"] = [textwrap.dedent(h).strip() for h in out.get("hints", [])]
    out.setdefault("setup_files", {})
    out["setup_files"] = {k: _clean(v) for k, v in out["setup_files"].items()}
    out.setdefault("placement", False)
    out.setdefault("concepts", [])
    if topic_id:
        out["topic"] = topic_id
    return out


def _norm_reference(ref: dict | None) -> dict:
    """A topic's Library entry: search keywords plus short syntax cards (see CONTENT_GUIDE.md)."""
    ref = ref or {}
    return {
        "keywords": [str(k).strip() for k in ref.get("keywords", [])],
        "cards": [{"syntax": str(c.get("syntax", "")).strip(), "explain": " ".join(str(c.get("explain", "")).split()),
                   "example": _clean(c.get("example", "")).rstrip("\n")} for c in ref.get("cards", [])],
    }


@lru_cache(maxsize=1)
def load() -> dict:
    topics, exercises = [], {}
    for mod_info in pkgutil.iter_modules(_topics_pkg.__path__):
        mod = importlib.import_module(f"{_topics_pkg.__name__}.{mod_info.name}")
        if not hasattr(mod, "TOPIC"):
            continue
        topic = dict(mod.TOPIC)
        topic.setdefault("requires", [])
        topic["summary"] = _clean(topic.get("summary", "")).strip()
        topic["lesson"] = _clean(getattr(mod, "LESSON", ""))
        topic["reference"] = _norm_reference(getattr(mod, "REFERENCE", None))
        topic["exercise_ids"] = []
        for ex in mod.EXERCISES:
            ex = _norm_exercise(ex, topic["id"])
            if ex["id"] in exercises:
                raise ValueError(f"duplicate exercise id {ex['id']}")
            exercises[ex["id"]] = ex
            topic["exercise_ids"].append(ex["id"])
        topics.append(topic)
    track_order = {t["id"]: i for i, t in enumerate(TRACKS)}
    topics.sort(key=lambda t: (track_order.get(t["track"], 99), t["order"]))

    from .combos import CHALLENGES
    combos = []
    for ch in CHALLENGES:
        ch = _norm_exercise(ch)
        ch["topic"] = "combo"
        if ch["id"] in exercises:
            raise ValueError(f"duplicate exercise id {ch['id']}")
        exercises[ch["id"]] = ch
        combos.append(ch)

    projects = []
    for mod_info in pkgutil.iter_modules(_projects_pkg.__path__):
        mod = importlib.import_module(f"{_projects_pkg.__name__}.{mod_info.name}")
        if not hasattr(mod, "PROJECT"):
            continue
        projects.append(_norm_project(mod.PROJECT))
    projects.sort(key=lambda p: (p["order"]))

    exams = []
    for mod_info in pkgutil.iter_modules(_exams_pkg.__path__):
        mod = importlib.import_module(f"{_exams_pkg.__name__}.{mod_info.name}")
        if not hasattr(mod, "EXAM"):
            continue
        exam = dict(mod.EXAM)
        exam["intro"] = _clean(exam.get("intro", ""))
        exam["exercise_ids"] = []
        for ex in mod.EXERCISES:
            ex = _norm_exercise(ex)
            ex["topic"] = "exam"
            ex["module"] = exam["module"]
            if ex["id"] in exercises:
                raise ValueError(f"duplicate exercise id {ex['id']}")
            exercises[ex["id"]] = ex
            exam["exercise_ids"].append(ex["id"])
        exams.append(exam)
    module_order = {m["id"]: i for i, m in enumerate(MODULES)}
    exams.sort(key=lambda e: module_order.get(e["module"], 99))
    for p in projects:
        p.setdefault("module", PROJECT_MODULES.get(p["id"], "llm-apps"))

    # Chapter projects: one small independent build at the end of each chapter.
    topics_by_id = {t["id"]: t for t in topics}
    minis = []
    for mod_info in pkgutil.iter_modules(_minis_pkg.__path__):
        mod = importlib.import_module(f"{_minis_pkg.__name__}.{mod_info.name}")
        for raw in getattr(mod, "MINIS", []):
            m = _norm_project(raw)
            chapter = topics_by_id.get(m["chapter"])
            if not chapter:
                raise ValueError(f"chapter project {m['id']} has unknown chapter {m['chapter']}")
            m["kind"] = "mini"
            m["module"] = chapter["track"]
            m["requires"] = [m["chapter"]]
            m.setdefault("order", 0)
            minis.append(m)
    topic_order = {t["id"]: i for i, t in enumerate(topics)}
    minis.sort(key=lambda m: topic_order[m["chapter"]])
    for m in minis:
        if m["id"] in {p["id"] for p in projects}:
            raise ValueError(f"duplicate project id {m['id']}")

    from .labs import LABS
    labs = []
    for lab in LABS:
        lab = dict(lab)
        lab["brief"] = _clean(lab["brief"])
        labs.append(lab)

    return {
        "tracks": TRACKS,
        "topics": topics,
        "topics_by_id": {t["id"]: t for t in topics},
        "exercises": exercises,
        "combos": combos,
        "projects": projects,
        "projects_by_id": {p["id"]: p for p in projects + minis},
        "minis": minis,
        "minis_by_chapter": {m["chapter"]: m for m in minis},
        "labs": labs,
        "labs_by_id": {lab["id"]: lab for lab in labs},
        "exams": exams,
        "exams_by_module": {e["module"]: e for e in exams},
        "modules": MODULES,
        "modules_by_id": {m["id"]: m for m in MODULES},
    }


def _norm_project(raw: dict) -> dict:
    p = dict(raw)
    for key in ("brief", "explore", "tests"):
        p[key] = _clean(p.get(key, ""))
    p["starter_files"] = {k: _clean(v) for k, v in p.get("starter_files", {}).items()}
    p["solution_files"] = {k: _clean(v) for k, v in p.get("solution_files", {}).items()}
    p.setdefault("rubric", [])
    p.setdefault("requires", [])
    p.setdefault("kind", "portfolio")
    return p


def public_exercise(ex: dict) -> dict:
    """What the browser is allowed to see (never the solution, hints or test source)."""
    return {k: ex[k] for k in ("id", "title", "difficulty", "prompt", "starter", "mode",
                               "topic", "concepts", "code", "lesson", "research", "module")
            if k in ex} | {
        "topics": ex.get("topics", []),
        "setup_files": list(ex.get("setup_files", {}).keys()),
        "hint_count": len(ex.get("hints", [])),
    }
