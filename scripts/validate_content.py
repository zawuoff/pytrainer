#!/usr/bin/env python3
"""Validate the curriculum: every reference solution must pass, every starter must fail.

Usage: python3 scripts/validate_content.py [id-prefix ...]
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pytrainer import content, runner  # noqa: E402


def check_hints(ex, problems):
    hints = ex.get("hints", [])
    if len(hints) != 3 or not all(isinstance(h, str) and len(h) > 15 for h in hints):
        problems.append("needs exactly 3 non-trivial hints")


def check_prediction(ex):
    problems = []
    check_hints(ex, problems)
    check_common(ex, problems)
    if not ex.get("code", "").strip():
        problems.append("predict exercise needs `code`")
    if not ex.get("explanation", "").strip():
        problems.append("predict exercise needs `explanation`")
    if ex["difficulty"] != 0:
        problems.append("predict exercises must be difficulty 0 (starter)")
    r = runner.check_prediction(ex.get("code", ""), ex["solution"], setup_files=ex["setup_files"])
    if r["status"] != "passed":
        problems.append("solution is not the exact output of `code`. Actual output:\n" + r["_actual"])
    r2 = runner.check_prediction(ex.get("code", ""), ex["solution"], setup_files=ex["setup_files"])
    if r2["_actual"] != r["_actual"]:
        problems.append("output is not deterministic")
    return ex["id"], problems


def check_common(ex, problems):
    if ex["difficulty"] <= 1 and ex.get("topic") not in ("combo", "exam") and len(ex.get("lesson", "")) < 250:
        problems.append("difficulty 0-1 steps need a `lesson` (>= 250 chars) teaching the idea")
    r = ex.get("research")
    if r is not None:
        if not r.get("note"):
            problems.append("research needs a `note`")
        for link in r.get("links", []):
            if not str(link.get("url", "")).startswith("https://") or not link.get("title"):
                problems.append(f"bad research link {link}")


def check_test_writing(ex):
    problems = []
    check_hints(ex, problems)
    check_common(ex, problems)
    if not ex.get("impl") or len(ex.get("mutants", [])) < 2:
        problems.append("tests-mode needs `impl` and >= 2 `mutants`")
        return ex["id"], problems
    good = runner.grade_test_writing(ex["solution"], ex["impl"], ex["mutants"], setup_files=ex["setup_files"])
    if good["status"] != "passed":
        problems.append("reference tests don't pass/catch everything: " +
                        "; ".join(f"{t['name']}: {t['message']}" for t in good["tests"] if not t["passed"]))
    bad = runner.grade_test_writing(ex["starter"], ex["impl"], ex["mutants"], setup_files=ex["setup_files"])
    if bad["status"] == "passed":
        problems.append("starter already passes")
    return ex["id"], problems


def check_exercise(ex):
    if ex["mode"] == "predict":
        return check_prediction(ex)
    if ex["mode"] == "tests":
        return check_test_writing(ex)
    problems = []
    check_hints(ex, problems)
    check_common(ex, problems)
    main = "solution.py"
    good = runner.run_tests({main: ex["solution"]}, ex["tests"], mode=ex["mode"],
                            setup_files=ex["setup_files"])
    if good["status"] != "passed":
        detail = good["error"] or "; ".join(f"{t['name']}: {t['message']}" for t in good["tests"]
                                            if not t["passed"])
        problems.append(f"solution does not pass ({good['status']}): {detail}")
    if good["total"] < 2:
        problems.append("needs at least 2 tests")
    bad = runner.run_tests({main: ex["starter"]}, ex["tests"], mode=ex["mode"],
                           setup_files=ex["setup_files"])
    if bad["status"] == "passed":
        problems.append("starter code already passes all tests")
    if not 0 <= ex["difficulty"] <= 3:
        problems.append("difficulty must be 0..3")
    if ex.get("kind") == "parsons":
        lines = [line.strip() for line in ex["solution"].splitlines() if line.strip()]
        if any(line.startswith("#") or '"""' in line or "'''" in line for line in lines):
            problems.append("parsons: no comments or multi-line strings in the solution (each line is a tile)")
        if not 3 <= len(lines) <= 12:
            problems.append("parsons: the solution needs 3-12 lines")
        if not ex.get("distractors") or any(d.strip() in lines for d in ex["distractors"]):
            problems.append("parsons: needs distractors, and none may be a line of the solution")
    if ex.get("kind") == "refactor":
        # The starter already works: only the style checks may fail on it.
        broken = [t["name"] for t in bad["tests"] if not t["passed"] and not t["name"].startswith("style ")]
        if bad["error"] or broken:
            problems.append("refactor: the starter must pass every behaviour check, but fails: "
                            + (bad["error"] or ", ".join(broken)))
        if not any(t["name"].startswith("style ") for t in bad["tests"] if not t["passed"]):
            problems.append("refactor: the starter must fail at least one style check")
    if ex.get("kind") == "bughunt":
        # The bug must hide: the buggy starter passes every example shown in the prompt.
        if not ex.get("visible_tests"):
            problems.append("bug hunt needs `visible_tests` (the prompt's examples)")
        else:
            shown = runner.run_tests({main: ex["starter"]}, ex["visible_tests"], mode=ex["mode"],
                                     setup_files=ex["setup_files"])
            if shown["status"] != "passed":
                problems.append("bug hunt: the buggy starter must pass its visible examples: "
                                + (shown["error"] or "; ".join(t["message"] for t in shown["tests"] if not t["passed"])))
    return ex["id"], problems


def check_mini(m):
    ident, problems = check_project(m)
    if "## You'll need to find out" not in m["brief"]:
        problems.append("brief needs a '## You'll need to find out' section (things to look up, described not named)")
    if not 0.25 <= float(m.get("estimated_hours", 0)) <= 1.5:
        problems.append("estimated_hours should be 0.25-1.5 for a chapter project")
    if len(m["rubric"]) < 3:
        problems.append("rubric needs >= 3 items")
    return "mini:" + m["chapter"], problems


def check_project(p):
    problems = []
    # A capstone runs next to the code of the projects it builds on: use their reference solutions.
    data = content.load()
    base = {}
    for pid in p.get("requires_projects", []):
        base.update(data["projects_by_id"][pid]["solution_files"])
    setup = p.get("setup_files") or None
    good = runner.run_tests({**base, **p["solution_files"]}, p["tests"], mode="function",
                            main=p.get("main", "app.py"), timeout=60, setup_files=setup)
    if good["status"] != "passed":
        detail = good["error"] or "; ".join(f"{t['name']}: {t['message']}" for t in good["tests"]
                                            if not t["passed"])
        problems.append(f"solution does not pass ({good['status']}): {detail}")
    bad = runner.run_tests({**base, **p["starter_files"]}, p["tests"], mode="function",
                           main=p.get("main", "app.py"), timeout=60, setup_files=setup)
    if bad["status"] == "passed":
        problems.append("starter already passes")
    return "project:" + p["id"], problems


def check_reference(t):
    """The Library card for a topic: structured, short, and every example really prints what it claims."""
    problems = []
    ref = t.get("reference") or {}
    keywords, cards = ref.get("keywords", []), ref.get("cards", [])
    if not 3 <= len(keywords) <= 16 or any(not k or k != k.lower() or len(k) > 30 for k in keywords):
        problems.append("REFERENCE needs 3-16 lowercase `keywords` (search words, each <= 30 chars)")
    if not 3 <= len(cards) <= 6:
        problems.append(f"REFERENCE needs 3-6 `cards`, has {len(cards)}")
    for i, c in enumerate(cards):
        where = f"card {i + 1} ({c['syntax'][:30]!r})"
        if not c["syntax"] or "\n" in c["syntax"] or len(c["syntax"]) > 60:
            problems.append(f"{where}: `syntax` must be one line, 1-60 chars")
        if not 15 <= len(c["explain"]) <= 160:
            problems.append(f"{where}: `explain` must be one sentence or two, 15-160 chars")
        lines = c["example"].splitlines()
        if not 2 <= len(lines) <= 8 or any(len(line) > 72 for line in lines):
            problems.append(f"{where}: `example` must be 2-8 lines of at most 72 chars")
            continue
        if any(ord(ch) > 127 for ch in c["syntax"] + c["explain"] + c["example"]):
            problems.append(f"{where}: ASCII only")
        r = runner.run_code({"snippet.py": c["example"] + "\n"}, main="snippet.py")
        claimed = [line[2:] if line.startswith("# ") else "" for line in lines if line.startswith("#")]
        actual = r["stdout"].rstrip("\n").split("\n") if r["stdout"].strip() else []
        if r["returncode"] != 0 or r.get("timed_out"):
            last = r["stderr"].strip().splitlines()[-1] if r["stderr"].strip() else r["returncode"]
            problems.append(f"{where}: example does not run cleanly: {last}")
        elif [a.rstrip() for a in actual] != [x.rstrip() for x in claimed]:
            problems.append(f"{where}: the `# ` comment lines must be exactly what the example prints.\n"
                            f"claimed: {claimed}\nactual:  {actual}")
        elif not actual:
            problems.append(f"{where}: example must print something (show it on `# ` lines)")
    return "reference:" + t["id"], problems


def main():
    data = content.load()
    prefixes = sys.argv[1:]
    jobs = []
    for t in data["topics"]:
        if not prefixes or any(("reference:" + t["id"]).startswith(p) or p == "references" for p in prefixes):
            jobs.append((check_reference, t))
    for ex in data["exercises"].values():
        if not prefixes or any(ex["id"].startswith(p) for p in prefixes):
            jobs.append((check_exercise, ex))
    for p in data["projects"]:
        if not prefixes or any(("project:" + p["id"]).startswith(x) or x == "projects"
                               for x in prefixes):
            jobs.append((check_project, p))
    for m in data["minis"]:
        if not prefixes or any(("mini:" + m["chapter"]).startswith(x) or x == "minis" for x in prefixes):
            jobs.append((check_mini, m))
    topic_ids = {t["id"] for t in data["topics"]}
    structural = []
    for t in data["topics"]:
        if prefixes and not any(t["id"].startswith(p) for p in prefixes):
            continue
        for req in t["requires"]:
            if req not in topic_ids:
                structural.append(f"topic {t['id']} requires unknown topic {req}")
        everything = [data["exercises"][e] for e in t["exercise_ids"]]
        exs = [e for e in everything if not e.get("extra")]
        extras = [e for e in everything if e.get("extra")]
        if everything[len(exs):] != extras:
            structural.append(f"topic {t['id']} extra steps must come after the learning path")
        if any(e["placement"] or e["difficulty"] < 1 for e in extras):
            structural.append(f"topic {t['id']} extra steps are difficulty 1-3 and never the placement step")
        placements = [e for e in exs if e["placement"]]
        if len(placements) != 1:
            structural.append(f"topic {t['id']} needs exactly one placement exercise (has {len(placements)})")
        starters = [e for e in exs if e["difficulty"] == 0]
        learn = [e for e in exs if e["difficulty"] <= 1]
        if len(starters) < 6:
            structural.append(f"topic {t['id']} needs >= 6 starter (difficulty 0) steps, has {len(starters)}")
        if len(learn) < 10:
            structural.append(f"topic {t['id']} needs >= 10 learning steps (difficulty 0-1), has {len(learn)}")
        if len(exs) < 14:
            structural.append(f"topic {t['id']} needs >= 14 exercises in total, has {len(exs)}")
        if not any(e["mode"] == "predict" for e in starters):
            structural.append(f"topic {t['id']} needs at least one predict starter")
        if [e["difficulty"] for e in exs] != sorted(e["difficulty"] for e in exs):
            structural.append(f"topic {t['id']} exercises must be ordered by difficulty (the learning path)")
        if len(t["lesson"]) < 800:
            structural.append(f"topic {t['id']} chapter notes (LESSON) missing or too short ({len(t['lesson'])} chars)")
    mini_count = {}
    for m in data["minis"]:
        mini_count[m["chapter"]] = mini_count.get(m["chapter"], 0) + 1
    if not prefixes or "minis" in prefixes:
        for t in data["topics"]:
            if mini_count.get(t["id"], 0) != 1:
                structural.append(f"chapter {t['id']} needs exactly one chapter project (has {mini_count.get(t['id'], 0)})")
    module_ids = {m["id"] for m in data["modules"]}
    for t in data["topics"]:
        if t["track"] not in module_ids:
            structural.append(f"topic {t['id']} has unknown module {t['track']}")
    for exam in data["exams"]:
        if prefixes and not any(("exam-" + exam["module"]).startswith(p) or p == "exams" for p in prefixes):
            continue
        exs = [data["exercises"][e] for e in exam["exercise_ids"]]
        if not 5 <= len(exs) <= 8:
            structural.append(f"exam {exam['module']} needs 5-8 exercises")
        if not any(e.get("research") and e["research"]["links"] for e in exs):
            structural.append(f"exam {exam['module']} needs a research exercise with doc links")
        if not any(e.get("research") and not e["research"]["links"] for e in exs):
            structural.append(f"exam {exam['module']} needs a look-it-up-yourself exercise (research without links)")
    if not prefixes or "exams" in prefixes:
        for m in module_ids - {e["module"] for e in data["exams"]}:
            structural.append(f"module {m} has no exam")
    for c in data["combos"]:
        for req in c.get("topics", []):
            if req not in topic_ids:
                structural.append(f"combo {c['id']} requires unknown topic {req}")
    for p in data["projects"]:
        for req in p["requires"]:
            if req not in topic_ids:
                structural.append(f"project {p['id']} requires unknown topic {req}")

    failures = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for ident, problems in pool.map(lambda j: j[0](j[1]), jobs):
            if problems:
                failures += 1
                print(f"FAIL {ident}")
                for pr in problems:
                    print("     " + pr.replace("\n", "\n     "))
    for s in structural:
        print("STRUCTURE " + s)
    print(f"\n{len(jobs)} checked, {failures} failing, {len(structural)} structural issues")
    print(f"{len(data['topics'])} topics, {len(data['exercises'])} exercises, "
          f"{len(data['combos'])} combos, {len(data['projects'])} projects, {len(data['labs'])} labs")
    sys.exit(1 if failures or structural else 0)


if __name__ == "__main__":
    main()
