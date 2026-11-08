from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "stock.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sku (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    cost REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS stock (sku_id INTEGER NOT NULL, warehouse TEXT NOT NULL, qty INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS movements (sku_id INTEGER NOT NULL, month TEXT NOT NULL, inbound INTEGER NOT NULL, outbound INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS movements_month ON movements(month);
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
    return scalar("SELECT COUNT(*) FROM sku") == 0
