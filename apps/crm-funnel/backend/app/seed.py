from __future__ import annotations

from random import Random

from .db import connect

MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]
SOURCES = ["Сайт", "Реклама", "Партнёры", "Звонки", "Рекомендации"]
SOURCE_POWER = {"Сайт": 0.44, "Реклама": 0.3, "Партнёры": 0.5, "Звонки": 0.26, "Рекомендации": 0.62}
OWNERS = ["Анна К.", "Игорь Л.", "Мария С.", "Дмитрий О.", "Павел З."]
VOLUME = [96, 104, 118, 121, 110, 124, 102, 108, 132, 141, 138, 156]
RESET = "DELETE FROM leads;"
INSERT_LEAD = "INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


def chain_of(qualified: int, presented: int, proposal: int, won: int) -> tuple:
    return (qualified, qualified * presented, qualified * presented * proposal, qualified * presented * proposal * won)


def stages_of(rnd: Random, source: str) -> tuple:
    power = SOURCE_POWER[source] * rnd.uniform(0.75, 1.25)
    return chain_of(int(rnd.random() < power), int(rnd.random() < power * 1.15), int(rnd.random() < power * 1.2), int(rnd.random() < power * 1.35))


def amount_of(rnd: Random, source: str, won: int) -> float:
    return round(rnd.uniform(80_000, 900_000) * (1.4 if source == "Партнёры" else 1.0)) if won else 0


def lead_row(rnd: Random, index: int, month: str) -> tuple:
    source = rnd.choices(SOURCES, weights=[32, 24, 18, 16, 10])[0]
    return row_of(rnd, index, month, source, stages_of(rnd, source))


def row_of(rnd: Random, index: int, month: str, source: str, stages: tuple) -> tuple:
    return (index, month, source, OWNERS[index % len(OWNERS)], rnd.randint(2, 240), *stages, amount_of(rnd, source, stages[3]))


def build(rnd: Random) -> list[tuple]:
    months = [month for month, volume in zip(MONTHS, VOLUME, strict=True) for _ in range(volume)]
    return [lead_row(rnd, index + 1, month) for index, month in enumerate(months)]


def payload(rnd: Random) -> list[tuple[str, list]]:
    return [(INSERT_LEAD, build(rnd))]


def dump(conn, rnd: Random) -> None:
    for statement, rows in payload(rnd):
        conn.executemany(statement, rows)


def fill(conn, rnd: Random) -> None:
    conn.executescript(RESET)
    dump(conn, rnd)


def seed() -> None:
    with connect() as conn:
        fill(conn, Random(5519))
