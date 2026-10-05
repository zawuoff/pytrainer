#!/usr/bin/env python3
"""Which steps caused the most trouble, from your own progress (the same data as the Insights page).

Usage: python3 scripts/content_report.py [--top N] [--csv]
Reads the PyTrainer database (PYTRAINER_DATA, or the default data folder); writes nothing.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pytrainer import db, insights  # noqa: E402

COLUMNS = ["id", "title", "chapter", "difficulty", "checks", "fails", "solved", "hints", "hint_count", "revealed",
           "tutor", "top_failure", "top_failure_n", "trouble"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--top", type=int, default=20, help="how many steps to list (default 20)")
    ap.add_argument("--csv", action="store_true", help="every step as CSV on stdout")
    args = ap.parse_args()
    rep = insights.report()
    if args.csv:
        w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rep["steps"])
        return 0
    t = rep["totals"]
    print(f"Data: {db.DB_PATH}")
    if not rep["steps"]:
        print("No practice checks yet.")
        return 0
    print(f"{t['tried']} steps tried, {t['solved']} solved, {t['checks']} checks. Per solve: "
          f"{t['fails_per_solve']} failing checks, {t['hints_per_solve']} hints. First try: "
          f"{round((t['first_try'] or 0) * 100)}%. Solutions shown: {t['revealed']}.\n")
    print(f"{'trouble':>7}  {'fails':>5}  {'hints':>5}  sol  {'step':<44} most failed check")
    for r in rep["steps"][:args.top]:
        fail = f"{r['top_failure']} (x{r['top_failure_n']})" if r["top_failure"] else ""
        print(f"{r['trouble']:>7}  {r['fails']:>5}  {r['hints']:>2}/{r['hint_count']:<2}  {'yes' if r['revealed'] else '   '}  "
              f"{(r['id'] + ' ' + ('' if r['solved'] else '[unsolved]'))[:44]:<44} {fail}")
    print("\nChapters (average trouble per step tried):")
    for c in rep["chapters"][:10]:
        print(f"{c['trouble']:>7}  {c['title']} ({c['solved']}/{c['tried']} solved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
