"""SQLite connection and schema. One file: data/vanlife.sqlite.

Destination-kind folder structures are never cached in here, they're
always read live via os.scandir (paths.py), so the DB can't drift from
what's actually on disk. This file only stores clips/markers/chat/canvas
state and the dynamic roots registry.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from . import config

DB_PATH = config.DATA_DIR / "vanlife.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_relative_path TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    size_bytes INTEGER,
    duration_seconds REAL,
    fps REAL,
    status TEXT NOT NULL DEFAULT 'new',
    dest_relative_path TEXT,
    sha256_source TEXT,
    sha256_dest TEXT,
    verified_at TEXT,
    metadata_doc_relative_path TEXT,
    first_seen_at TEXT NOT NULL,
    last_opened_at TEXT
);

CREATE TABLE IF NOT EXISTS markers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id INTEGER NOT NULL REFERENCES clips(id),
    timestamp_seconds REAL NOT NULL,
    tag TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id INTEGER REFERENCES clips(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    action_json TEXT,
    action_status TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS organize_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id INTEGER NOT NULL REFERENCES clips(id),
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    detail_json TEXT NOT NULL DEFAULT '{}',
    started_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS note_phrases (
    phrase TEXT PRIMARY KEY,
    use_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    absolute_path TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    is_default INTEGER NOT NULL DEFAULT 0,
    added_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS canvas_boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS canvas_regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL REFERENCES canvas_boards(id),
    name TEXT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    width REAL NOT NULL,
    height REAL NOT NULL,
    color TEXT,
    z_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS canvas_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL REFERENCES canvas_boards(id),
    clip_id INTEGER NOT NULL REFERENCES clips(id),
    x REAL NOT NULL,
    y REAL NOT NULL,
    width REAL NOT NULL,
    height REAL NOT NULL,
    region_id INTEGER REFERENCES canvas_regions(id),
    z_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ai_analysis (
    clip_id INTEGER NOT NULL UNIQUE REFERENCES clips(id),
    caption TEXT,
    tags_json TEXT,
    model TEXT,
    generated_at TEXT
);

CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id INTEGER NOT NULL REFERENCES clips(id),
    segment_start REAL NOT NULL,
    segment_end REAL NOT NULL,
    text TEXT NOT NULL,
    model TEXT,
    generated_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS footage_search USING fts5(
    filename,
    caption,
    tags,
    transcript,
    marker_notes,
    content='',
    tokenize='porter unicode61'
);
"""

_DEFAULT_ROOTS = [
    ("source", "Source", r"J:\Studio 25 films\vanlife clip sort", "readonly"),
    ("dest", "Destination", r"J:\Studio 25 films\Studio 25 Films", "dest"),
    ("project", "Project", r"D:\_Dev\AI-Setup\SEEKERS_GHOSTS", "readonly"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create every table if missing and seed the 3 default roots exactly
    once. Safe to call on every app start, idempotent by design."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _seed_default_roots(conn)
    finally:
        conn.close()


def _seed_default_roots(conn: sqlite3.Connection) -> None:
    existing = {
        row["key"] for row in conn.execute("SELECT key FROM roots WHERE is_default = 1")
    }
    for key, label, absolute_path, kind in _DEFAULT_ROOTS:
        if key in existing:
            continue
        conn.execute(
            "INSERT INTO roots (key, label, absolute_path, kind, is_default, added_at) "
            "VALUES (?, ?, ?, ?, 1, ?)",
            (key, label, absolute_path, kind, _now()),
        )
    conn.commit()
