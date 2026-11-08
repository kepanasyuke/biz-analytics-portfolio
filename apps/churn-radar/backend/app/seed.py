from __future__ import annotations

from random import Random

from .db import connect

MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]
PLANS = {"Старт": 2_900, "Бизнес": 9_900, "Про": 24_900}
CHURN_RISK = {"Старт": 0.085, "Бизнес": 0.05, "Про": 0.026}
REASONS = ["Дорого", "Не подошли функции", "Ушли к конкуренту", "Сократили штат", "Не пользуются"]
VOLUME = [72, 84, 96, 88, 102, 110, 94, 116, 124, 130, 126, 138]
RESET = "DELETE FROM customers; DELETE FROM months;"
INSERT_MONTH = "INSERT INTO months VALUES (?)"
INSERT_CUSTOMER = "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)"


def month_at(index: int) -> str:
    year, month = divmod(index, 12)
    return f"{2025 + year}-{month + 1:02d}"


def churn_part(rnd: Random, plan: str, cohort_index: int) -> tuple:
    churned = rnd.random() < CHURN_RISK[plan] * 6
    return (month_at(cohort_index + rnd.randint(1, 5)) if churned else None, rnd.choice(REASONS) if churned else None)


def customer_row(rnd: Random, ident: int, cohort_index: int) -> tuple:
    plan = rnd.choices(list(PLANS), weights=[46, 38, 16])[0]
    return (ident, MONTHS[cohort_index], plan, PLANS[plan] * rnd.uniform(0.9, 1.15), *churn_part(rnd, plan, cohort_index), rnd.randint(5, 100))


def build(rnd: Random) -> list[tuple]:
    return [customer_row(rnd, ident + 1, cohort_index) for cohort_index, volume in enumerate(VOLUME) for ident in range(sum(VOLUME[:cohort_index]), sum(VOLUME[: cohort_index + 1]))]


def payload(rnd: Random) -> list[tuple[str, list]]:
    return [(INSERT_MONTH, [(month,) for month in MONTHS]), (INSERT_CUSTOMER, build(rnd))]


def dump(conn, rnd: Random) -> None:
    for statement, rows in payload(rnd):
        conn.executemany(statement, rows)


def fill(conn, rnd: Random) -> None:
    conn.executescript(RESET)
    dump(conn, rnd)


def seed() -> None:
    with connect() as conn:
        fill(conn, Random(9182))
