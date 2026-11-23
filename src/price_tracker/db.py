"""Database helpers for Price Tracker.

Database is SQLite, schema in db/schema.sql. init must be safe to run twice,
and must not delete observations.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(database_path: str | Path) -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    return sqlite3.connect(str(database_path))


def init_database(database_path: str | Path, schema_path: str | Path) -> None:
    """Create the database tables from schema.sql.

    Safe to run twice: every statement uses CREATE TABLE IF NOT EXISTS and
    CREATE INDEX IF NOT EXISTS, so existing tables and observations are never
    deleted or overwritten.
    """
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    conn = connect(database_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()
