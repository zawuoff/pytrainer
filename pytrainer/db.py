"""SQLite persistence. One file in the per-user data dir (~/.local/share/pytrainer on Linux),
with daily backups."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import threading
import time
from datetime import date, datetime
from pathlib import Path


def _default_data_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "PyTrainer"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/PyTrainer"
    return Path.home() / ".local/share/pytrainer"


DATA_DIR = Path(os.environ.get("PYTRAINER_DATA") or _default_data_dir())
DB_PATH = DATA_DIR / "pytrainer.db"
BACKUP_DIR = DATA_DIR / "backups"

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    kind TEXT NOT NULL,              -- practice | review | placement | project
    files TEXT NOT NULL,
    status TEXT NOT NULL,
    passed INTEGER NOT NULL,
    total INTEGER NOT NULL,
    duration_s INTEGER NOT NULL DEFAULT 0,
    result TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS attempts_item ON attempts(item_id);
CREATE INDEX IF NOT EXISTS attempts_created ON attempts(created_at);
CREATE TABLE IF NOT EXISTS exercise_state (
    exercise_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'new',   -- new | attempted | solved
    attempts INTEGER NOT NULL DEFAULT 0,
    first_try INTEGER NOT NULL DEFAULT 0,
    solved_at TEXT,
    best_passed INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL DEFAULT 0,
    next_review TEXT,
    interval_days REAL NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    lapses INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS drafts (
    item_id TEXT PRIMARY KEY,
    files TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS topic_state (
    topic_id TEXT PRIMARY KEY,
    placed INTEGER NOT NULL DEFAULT 0,
    placed_at TEXT
);
CREATE TABLE IF NOT EXISTS activity (
    day TEXT PRIMARY KEY,
    seconds INTEGER NOT NULL DEFAULT 0,
    solved INTEGER NOT NULL DEFAULT 0,
    checks INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS placement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    exercise_ids TEXT NOT NULL,
    answers TEXT NOT NULL DEFAULT '{}',
    report TEXT
);
CREATE TABLE IF NOT EXISTS custom_exercises (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    files TEXT NOT NULL,
    result TEXT NOT NULL,
    review TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chats (
    item_id TEXT PRIMARY KEY,
    messages TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    item_id TEXT NOT NULL,
    attempt_id INTEGER,
    review TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lesson_state (
    topic_id TEXT PRIMARY KEY,
    read_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lab_state (
    lab_id TEXT PRIMARY KEY,
    done INTEGER NOT NULL DEFAULT 0,
    last_result TEXT,
    done_at TEXT
);
"""

_local = threading.local()
_init_lock = threading.Lock()
_initialised = False


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today() -> str:
    return date.today().isoformat()


def conn() -> sqlite3.Connection:
    global _initialised
    c = getattr(_local, "conn", None)
    if c is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        with _init_lock:
            if not _initialised:
                c.executescript(SCHEMA)
                _migrate(c)
                _initialised = True
        _local.conn = c
    return c


MIGRATIONS = [
    "ALTER TABLE exercise_state ADD COLUMN revealed INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE exercise_state ADD COLUMN hints_used INTEGER NOT NULL DEFAULT 0",
    # FSRS memory model (see srs.py); NULL on rows scheduled before it, filled at their next review.
    "ALTER TABLE exercise_state ADD COLUMN stability REAL",
    "ALTER TABLE exercise_state ADD COLUMN difficulty REAL",
    "ALTER TABLE exercise_state ADD COLUMN last_review TEXT",
]


def _migrate(c: sqlite3.Connection) -> None:
    for sql in MIGRATIONS:
        try:
            c.execute(sql)
        except sqlite3.OperationalError:
            pass  # column already exists


def q(sql: str, params=()) -> list[sqlite3.Row]:
    return conn().execute(sql, params).fetchall()


def q1(sql: str, params=()) -> sqlite3.Row | None:
    return conn().execute(sql, params).fetchone()


def ex(sql: str, params=()) -> int:
    cur = conn().execute(sql, params)
    return cur.lastrowid


def get_setting(key: str, default=None):
    row = q1("SELECT value FROM settings WHERE key=?", (key,))
    return json.loads(row["value"]) if row else default


def set_setting(key: str, value) -> None:
    ex("INSERT INTO settings(key, value) VALUES(?, ?) "
       "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)))


def settings() -> dict:
    return {r["key"]: json.loads(r["value"]) for r in q("SELECT key, value FROM settings")}


def backup() -> None:
    """Keep one snapshot per day, last 14 days."""
    if not DB_PATH.exists():
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    target = BACKUP_DIR / f"pytrainer-{today()}.db"
    if not target.exists():
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(target)
        with dst:
            src.backup(dst)
        src.close()
        dst.close()
    snapshots = sorted(BACKUP_DIR.glob("pytrainer-*.db"))
    for old in snapshots[:-14]:
        old.unlink(missing_ok=True)


def export_all() -> dict:
    tables = ["settings", "attempts", "exercise_state", "drafts", "topic_state", "activity",
              "placement", "custom_exercises", "submissions", "chats", "reviews", "lab_state", "lesson_state"]
    return {"exported_at": now(), "version": 1,
            "tables": {t: [dict(r) for r in q(f"SELECT * FROM {t}")] for t in tables}}


def reset_all() -> None:
    if DB_PATH.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(DB_PATH, BACKUP_DIR / f"before-reset-{int(time.time())}.db")
    c = conn()
    for (name,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                             "AND name NOT LIKE 'sqlite_%'").fetchall():
        c.execute(f"DELETE FROM {name}")
