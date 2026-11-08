from __future__ import annotations

from random import Random

from .db import connect

MONTHS = [f"{year}-{month:02d}" for year in (2024, 2025) for month in range(1, 13)]
MANAGERS = [
    (1, "Анна Ковалёва", "Москва"),
    (2, "Игорь Лебедев", "Москва"),
    (3, "Мария Соколова", "Санкт-Петербург"),
    (4, "Дмитрий Орлов", "Санкт-Петербург"),
    (5, "Елена Гусева", "Регионы"),
    (6, "Павел Зайцев", "Регионы"),
]
CHANNELS = {"Входящий": 180_000, "Партнёры": 260_000, "Тендеры": 540_000, "Outbound": 120_000}
STAGES = ["Квалификация", "Предложение", "Согласование", "Выиграна", "Проиграна"]
WEIGHTS = [22, 24, 16, 24, 14]
SEASON = {1: 0.82, 2: 0.9, 3: 1.08, 4: 1.02, 5: 0.98, 6: 1.05, 7: 0.9, 8: 0.94, 9: 1.12, 10: 1.16, 11: 1.1, 12: 1.35}
RESET = "DELETE FROM deals; DELETE FROM managers; DELETE FROM targets;"
INSERT_MANAGERS = "INSERT INTO managers VALUES (?, ?, ?)"
INSERT_DEALS = "INSERT INTO deals (month, manager_id, channel, stage, amount, days_to_close) VALUES (?, ?, ?, ?, ?, ?)"
INSERT_TARGETS = "INSERT INTO targets VALUES (?, ?)"


def deal_row(rnd: Random, month: str, manager_id: int, channel: str) -> tuple:
    base = CHANNELS[channel] * SEASON[int(month[5:])] * rnd.uniform(0.65, 1.6)
    return (month, manager_id, channel, rnd.choices(STAGES, weights=WEIGHTS)[0], round(base, 2), rnd.randint(3, 64))


def build_deals(rnd: Random) -> list[tuple]:
    return [deal_row(rnd, month, manager_id, channel) for month in MONTHS for manager_id, *_ in MANAGERS for channel in CHANNELS for _ in range(rnd.randint(5, 14))]


def targets(rows: list[tuple]) -> list[tuple]:
    months = sorted({row[0] for row in rows})
    return [(month, round(sum(row[4] for row in rows if row[0] == month and row[3] == "Выиграна") * 1.14, 2)) for month in months]


def payload() -> list[tuple[str, list]]:
    rows = build_deals(Random(1031))
    return [(INSERT_MANAGERS, MANAGERS), (INSERT_DEALS, rows), (INSERT_TARGETS, targets(rows))]


def dump(conn) -> None:
    for statement, rows in payload():
        conn.executemany(statement, rows)


def fill(conn) -> None:
    conn.executescript(RESET)
    dump(conn)


def seed() -> None:
    with connect() as conn:
        fill(conn)
