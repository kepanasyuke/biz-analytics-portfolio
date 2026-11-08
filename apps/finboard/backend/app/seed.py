from __future__ import annotations

from random import Random

from .db import connect

MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]
CHANNELS = [
    ("Performance", 4_800_000, 312, 21_400_000),
    ("Партнёры", 2_100_000, 96, 15_800_000),
    ("Контент / SEO", 1_400_000, 148, 16_900_000),
    ("Outbound", 3_200_000, 74, 9_600_000),
    ("События", 2_600_000, 41, 7_200_000),
]
SEASON = [0.86, 0.92, 1.04, 1.0, 0.97, 1.02, 0.9, 0.95, 1.08, 1.12, 1.16, 1.28]
RESET = "DELETE FROM pnl; DELETE FROM cash; DELETE FROM channels;"
INSERT_PNL = "INSERT INTO pnl VALUES (?, ?, ?, ?, ?, ?, ?)"
INSERT_CASH = "INSERT INTO cash VALUES (?, ?, ?)"
INSERT_CHANNELS = "INSERT INTO channels VALUES (?, ?, ?, ?)"


def pnl_row(index: int, month: str, rnd: Random) -> tuple:
    revenue = 12_000_000 * SEASON[index] * (1 + 0.028 * index) * rnd.uniform(0.96, 1.04)
    return (
        month,
        round(revenue),
        round(revenue * rnd.uniform(0.46, 0.54)),
        round(revenue * rnd.uniform(0.10, 0.14)),
        round(2_600_000 + 42_000 * index),
        900_000,
        round(revenue * rnd.uniform(0.03, 0.05)),
    )


def cash_row(row: tuple, rnd: Random) -> tuple:
    month, revenue, *_costs, other = row
    spend = revenue * 0.52 + revenue * 0.12 + 2_600_000 + 900_000 + other
    return (month, round(revenue * rnd.uniform(0.96, 1.03)), round(spend * rnd.uniform(0.90, 0.98)))


def payload(rnd: Random) -> list[tuple[str, list]]:
    rows = [pnl_row(index, month, rnd) for index, month in enumerate(MONTHS)]
    return [(INSERT_PNL, rows), (INSERT_CASH, [cash_row(row, rnd) for row in rows]), (INSERT_CHANNELS, CHANNELS)]


def dump(conn, rnd: Random) -> None:
    for statement, rows in payload(rnd):
        conn.executemany(statement, rows)


def fill(conn, rnd: Random) -> None:
    conn.executescript(RESET)
    dump(conn, rnd)


def seed() -> None:
    with connect() as conn:
        fill(conn, Random(771))
