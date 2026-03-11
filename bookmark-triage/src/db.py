"""SQLite database setup and helpers."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bookmarks.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            normalized_url TEXT NOT NULL UNIQUE,
            title TEXT DEFAULT '',
            domain TEXT DEFAULT '',
            site_bucket TEXT DEFAULT '',
            status TEXT DEFAULT 'imported',
            is_build_candidate INTEGER DEFAULT 0,
            candidate_reason TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_bookmark(conn, original_url, normalized_url, title=""):
    """Insert a bookmark. Returns (id, was_inserted). Skips duplicates."""
    now = datetime.now().isoformat()
    try:
        cur = conn.execute(
            """INSERT INTO bookmarks (original_url, normalized_url, title, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (original_url, normalized_url, title, now, now),
        )
        return cur.lastrowid, True
    except sqlite3.IntegrityError:
        return None, False


def update_bookmark(conn, bookmark_id, **fields):
    """Update arbitrary fields on a bookmark by id."""
    fields["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [bookmark_id]
    conn.execute(f"UPDATE bookmarks SET {set_clause} WHERE id = ?", values)


def get_bookmarks(conn, where="1=1", params=()):
    return conn.execute(f"SELECT * FROM bookmarks WHERE {where}", params).fetchall()


def count_bookmarks(conn, where="1=1", params=()):
    row = conn.execute(f"SELECT COUNT(*) FROM bookmarks WHERE {where}", params).fetchone()
    return row[0]
