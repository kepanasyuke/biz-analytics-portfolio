from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finance.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pnl (
    month TEXT PRIMARY KEY,
    revenue REAL NOT NULL,
    cogs REAL NOT NULL,
    marketing REAL NOT NULL,
    payroll REAL NOT NULL,
    rent REAL NOT NULL,
    other REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cash (month TEXT PRIMARY KEY, inflow REAL NOT NULL, outflow REAL NOT NULL);
CREATE TABLE IF NOT EXISTS channels (name TEXT PRIMARY KEY, spend REAL NOT NULL, customers INTEGER NOT NULL, revenue REAL NOT NULL);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return with_row_factory(sqlite3.connect(DB_PATH, check_same_thread=False))


def with_row_factory(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.row_factory = sqlite3.Row
    return conn


def rows_of(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(sql, params).fetchall()


def scalar(sql: str, params: tuple = ()) -> float:
    return rows_of(sql, params)[0][0] or 0.0


def init_schema() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def is_empty() -> bool:
    return scalar("SELECT COUNT(*) FROM pnl") == 0
