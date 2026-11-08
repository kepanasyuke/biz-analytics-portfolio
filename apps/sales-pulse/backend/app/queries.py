from __future__ import annotations

from .db import rows_of, scalar

REVENUE = "SELECT SUM(amount) FROM deals WHERE stage = 'Выиграна' AND month LIKE ?"
WON_COUNT = "SELECT COUNT(*) FROM deals WHERE stage = 'Выиграна' AND month LIKE ?"
DEAL_COUNT = "SELECT COUNT(*) FROM deals WHERE month LIKE ?"
CYCLE = "SELECT AVG(days_to_close) FROM deals WHERE stage = 'Выиграна' AND month LIKE ?"
PLAN = "SELECT SUM(amount) FROM targets WHERE month LIKE ?"

BY_MONTH = """
SELECT month, SUM(amount) AS revenue, COUNT(*) AS deals, AVG(amount) AS avg_deal
FROM deals WHERE stage = 'Выиграна' AND month LIKE ?
GROUP BY month ORDER BY month
"""

BY_CHANNEL = """
SELECT channel, SUM(amount) AS revenue
FROM deals WHERE stage = 'Выиграна' AND month LIKE ?
GROUP BY channel ORDER BY revenue DESC
"""

BY_TEAM = """
SELECT m.team, SUM(d.amount) AS revenue
FROM deals d JOIN managers m ON m.id = d.manager_id
WHERE d.stage = 'Выиграна' AND d.month LIKE ?
GROUP BY m.team ORDER BY revenue DESC
"""

FUNNEL = """
SELECT 'Все сделки' AS stage, COUNT(*) AS deals FROM deals WHERE month LIKE ?
UNION ALL
SELECT 'Дошли до предложения', COUNT(*) FROM deals WHERE month LIKE ? AND stage IN ('Предложение', 'Согласование', 'Выиграна')
UNION ALL
SELECT 'Дошли до согласования', COUNT(*) FROM deals WHERE month LIKE ? AND stage IN ('Согласование', 'Выиграна')
UNION ALL
SELECT 'Выиграны', COUNT(*) FROM deals WHERE month LIKE ? AND stage = 'Выиграна'
"""

MANAGERS = """
SELECT m.name, m.team, COUNT(d.id) AS deals,
       SUM(CASE WHEN d.stage = 'Выиграна' THEN 1 ELSE 0 END) AS won,
       ROUND(100.0 * SUM(CASE WHEN d.stage = 'Выиграна' THEN 1 ELSE 0 END) / COUNT(d.id), 1) AS win_rate,
       SUM(CASE WHEN d.stage = 'Выиграна' THEN d.amount ELSE 0 END) AS revenue,
       ROUND(AVG(CASE WHEN d.stage = 'Выиграна' THEN d.days_to_close END), 1) AS cycle
FROM deals d JOIN managers m ON m.id = d.manager_id
WHERE d.month LIKE ?
GROUP BY m.id ORDER BY revenue DESC
"""


def revenue(year: str) -> float:
    return scalar(REVENUE, (f"{year}-%",))


def won(year: str) -> float:
    return scalar(WON_COUNT, (f"{year}-%",))


def deals(year: str) -> float:
    return scalar(DEAL_COUNT, (f"{year}-%",))


def cycle(year: str) -> float:
    return scalar(CYCLE, (f"{year}-%",))


def plan(year: str) -> float:
    return scalar(PLAN, (f"{year}-%",))


def by_month(year: str) -> list:
    return rows_of(BY_MONTH, (f"{year}-%",))


def by_channel(year: str) -> list:
    return rows_of(BY_CHANNEL, (f"{year}-%",))


def by_team(year: str) -> list:
    return rows_of(BY_TEAM, (f"{year}-%",))


def funnel(year: str) -> list:
    return rows_of(FUNNEL, (f"{year}-%",) * 4)


def managers(year: str) -> list:
    return rows_of(MANAGERS, (f"{year}-%",))
