"""Course-level view: modules, chapter paths, module tests and "continue where you left off"."""

from __future__ import annotations

from . import content, db, progress


def _earned(st: dict) -> bool:
    return st.get("status") == "solved" and not st.get("revealed")


def exam_status(module_id: str, states: dict | None = None) -> dict | None:
    data = content.load()
    exam = data["exams_by_module"].get(module_id)
    if not exam:
        return None
    states = states if states is not None else progress.exercise_states()
    solved = sum(1 for e in exam["exercise_ids"] if _earned(states.get(e, {})))
    attempted = any(states.get(e, {}).get("attempts") for e in exam["exercise_ids"])
    total = len(exam["exercise_ids"])
    ratio = exam.get("pass_ratio", 0.7)
    return {"module": module_id, "title": exam["title"], "solved": solved, "total": total,
            "pass_ratio": ratio, "passed": total > 0 and solved / total >= ratio - 1e-9,
            "attempted": attempted, "first": exam["exercise_ids"][0] if exam["exercise_ids"] else None}


def place_module_if_exam_passed(module_id: str) -> bool:
    """Passing a module test proves the module: place all its chapters (they unlock what follows)."""
    st = exam_status(module_id)
    if not st or not st["passed"]:
        return False
    data = content.load()
    newly = False
    for t in data["topics"]:
        if t["track"] == module_id:
            row = db.q1("SELECT placed FROM topic_state WHERE topic_id=?", (t["id"],))
            if not row or not row["placed"]:
                newly = True
            db.ex("INSERT INTO topic_state(topic_id, placed, placed_at) VALUES(?,1,?) ON CONFLICT(topic_id) "
                  "DO UPDATE SET placed=1", (t["id"], db.now()))
    return newly


def overview(states: dict | None = None, tp: dict | None = None) -> list[dict]:
    data = content.load()
    states = states if states is not None else progress.exercise_states()
    tp = tp if tp is not None else progress.topic_progress(states)
    out = []
    for i, m in enumerate(data["modules"]):
        chapters = []
        for t in data["topics"]:
            if t["track"] != m["id"]:
                continue
            steps = t["exercise_ids"]
            done = sum(1 for e in steps if _earned(states.get(e, {})))
            chapters.append({"id": t["id"], "title": t["title"], "summary": t["summary"],
                             "steps": len(steps), "done": done, **tp[t["id"]],
                             "strip": [[data["exercises"][e]["difficulty"], states.get(e, {}).get("status", "new")]
                                       for e in steps]})
        exam = exam_status(m["id"], states)
        cleared = sum(c["cleared"] for c in chapters)
        out.append({**m, "number": i + 1, "chapters": chapters, "exam": exam,
                    "cleared": cleared, "complete": bool(chapters) and (cleared == len(chapters)
                                                                        or bool(exam and exam["passed"])),
                    "steps_total": sum(c["steps"] for c in chapters),
                    "steps_done": sum(c["done"] for c in chapters),
                    "projects": [p["id"] for p in data["projects"] if p.get("module") == m["id"]]})
    return out


def chapter_next(topic_id: str, states: dict | None = None, tp: dict | None = None) -> dict | None:
    """What to do next inside one chapter: the first unsolved step, then its chapter project."""
    data = content.load()
    states = states if states is not None else progress.exercise_states()
    tp = tp if tp is not None else progress.topic_progress(states)
    t = data["topics_by_id"][topic_id]
    for idx, eid in enumerate(t["exercise_ids"]):
        if not _earned(states.get(eid, {})):
            ex = data["exercises"][eid]
            return {"type": "step", "id": eid, "title": ex["title"], "topic": t["id"], "topic_title": t["title"],
                    "module": t["track"], "step": idx + 1, "steps": len(t["exercise_ids"]),
                    "kind": "learn" if ex.get("lesson") and ex["difficulty"] <= 1 else "practice"}
    proj = tp[topic_id]["project"]
    if proj and not proj["passed"]:
        return {"type": "project", "id": proj["id"], "title": proj["title"], "topic": t["id"],
                "topic_title": t["title"], "module": t["track"], "step": len(t["exercise_ids"]),
                "steps": len(t["exercise_ids"]), "kind": "project"}
    return None


def next_chapter(topic_id: str, tp: dict | None = None) -> dict | None:
    """The next chapter in course order that you haven't completed."""
    data = content.load()
    tp = tp if tp is not None else progress.topic_progress()
    ids = [t["id"] for t in data["topics"]]
    for t in data["topics"][ids.index(topic_id) + 1:]:
        if not tp[t["id"]]["cleared"]:
            return {"id": t["id"], "title": t["title"], "module": t["track"]}
    return None


def continue_point(states: dict | None = None, tp: dict | None = None) -> dict | None:
    """The next thing in the course: in the first chapter you haven't completed, the next unsolved
    step, or its chapter project once the steps are done."""
    data = content.load()
    states = states if states is not None else progress.exercise_states()
    tp = tp if tp is not None else progress.topic_progress(states)
    for t in data["topics"]:
        if tp[t["id"]]["cleared"]:
            continue
        nxt = chapter_next(t["id"], states, tp)
        if nxt:
            return nxt
    return None


def path_info(ex: dict, states: dict | None = None) -> dict | None:
    """Where an exercise sits in its chapter (or module test) path, for the step bar."""
    data = content.load()
    states = states if states is not None else progress.exercise_states()
    mini = None
    if ex.get("topic") == "exam":
        exam = data["exams_by_module"].get(ex.get("module"))
        ids, title, kind = (exam["exercise_ids"], exam["title"], "exam") if exam else ([], "", "exam")
    elif ex.get("topic") in data["topics_by_id"] and not ex.get("generated"):
        t = data["topics_by_id"][ex["topic"]]
        ids, title, kind = t["exercise_ids"], t["title"], "chapter"
        mini = data["minis_by_chapter"].get(t["id"])
    elif ex.get("topic") == "combo":
        ids, title, kind = [c["id"] for c in data["combos"]], "Combination challenges", "combo"
    else:
        return None
    passed = progress.passed_projects() if mini else set()
    return {"kind": kind, "title": title, "index": ids.index(ex["id"]), "total": len(ids),
            "project": {"id": mini["id"], "title": mini["title"], "passed": mini["id"] in passed} if mini else None,
            "steps": [{"id": e, "title": data["exercises"][e]["title"],
                       "difficulty": data["exercises"][e]["difficulty"],
                       "status": ("revealed" if states.get(e, {}).get("revealed")
                                  else states.get(e, {}).get("status", "new"))} for e in ids]}


def today_plan(states: dict | None = None, tp: dict | None = None) -> list[dict]:
    """Tonight: due reviews, then the next steps on your path, then a module test or project."""
    data = content.load()
    states = states if states is not None else progress.exercise_states()
    tp = tp if tp is not None else progress.topic_progress(states)
    plan = [{"kind": "review", "id": r["id"], "title": r["title"], "topic": r["topic"],
             "why": "Spaced review: rebuild it from memory"} for r in progress.due_reviews(3)]
    picked = 0
    for t in data["topics"]:
        if tp[t["id"]]["cleared"] or picked >= 5:
            continue
        for idx, eid in enumerate(t["exercise_ids"]):
            if picked >= 5:
                break
            if not _earned(states.get(eid, {})):
                ex = data["exercises"][eid]
                plan.append({"kind": "exercise", "id": eid, "title": ex["title"], "topic": t["id"],
                             "difficulty": ex["difficulty"],
                             "why": f"{t['title']} · step {idx + 1} of {len(t['exercise_ids'])}"})
                picked += 1
        proj = tp[t["id"]]["project"]
        if picked < 5 and proj and not proj["passed"] and all(_earned(states.get(e, {})) for e in t["exercise_ids"]):
            plan.append({"kind": "project", "id": proj["id"], "title": proj["title"],
                         "why": f"Chapter project: build it on your own to finish {t['title']}"})
            picked += 1
        if picked:
            break  # stay within one chapter per evening
    for m in overview(states, tp):
        chapters_done = m["chapters"] and all(c["cleared"] for c in m["chapters"])
        if chapters_done and m["exam"] and not m["exam"]["passed"]:
            plan.append({"kind": "exam", "id": m["id"], "title": m["exam"]["title"],
                         "why": "You've finished the chapters. Prove the module."})
            break
        if not m["complete"]:
            done = {r["project_id"] for r in db.q("SELECT project_id FROM submissions "
                                                   "WHERE json_extract(result,'$.status')='passed'")}
            for pid in m["projects"]:
                p = data["projects_by_id"][pid]
                if pid not in done and all(tp.get(r, {}).get("cleared") for r in p["requires"]):
                    plan.append({"kind": "project", "id": pid, "title": p["title"],
                                 "why": f"Portfolio project (~{p['estimated_hours']}h)"})
                    break
            break
    return plan
