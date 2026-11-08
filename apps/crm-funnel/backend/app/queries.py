from __future__ import annotations

from .db import rows_of, scalar

TOTAL = "SELECT COUNT(*) FROM leads"
WON = "SELECT COUNT(*) FROM leads WHERE won = 1"
REVENUE = "SELECT SUM(amount) FROM leads"
MEDIAN = "SELECT response_min FROM leads WHERE month LIKE ? ORDER BY response_min LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM leads WHERE month LIKE ?)"
IN_SLA = "SELECT COUNT(*) FROM leads WHERE response_min <= ?"

FUNNEL = """
SELECT COUNT(*) AS leads, SUM(qualified) AS qualified, SUM(presented) AS presented,
       SUM(proposal) AS proposal, SUM(won) AS won
FROM leads
"""

BY_SOURCE = """
SELECT source, COUNT(*) AS leads, SUM(won) AS won, SUM(amount) AS revenue, AVG(response_min) AS response
FROM leads GROUP BY source ORDER BY leads DESC
"""

BY_OWNER = """
SELECT owner, COUNT(*) AS leads, SUM(won) AS won, SUM(amount) AS revenue,
       ROUND(100.0 * SUM(won) / COUNT(*), 1) AS conversion, ROUND(AVG(response_min)) AS response
FROM leads GROUP BY owner ORDER BY revenue DESC
"""

BY_MONTH = """
SELECT month, COUNT(*) AS leads, SUM(won) AS won, SUM(amount) AS revenue
FROM leads GROUP BY month ORDER BY month
"""

STAGE_LOSSES = """
SELECT SUM(qualified) AS after_qualification, SUM(presented) AS after_presentation,
       SUM(proposal) AS after_proposal, SUM(won) AS after_deal
FROM leads
"""


def total() -> float:
    return scalar(TOTAL)


def won() -> float:
    return scalar(WON)


def revenue() -> float:
    return scalar(REVENUE)


def median_response(month: str) -> float:
    return scalar(MEDIAN, (month, month))


def in_sla(minutes: int) -> float:
    return scalar(IN_SLA, (minutes,))


def funnel() -> dict:
    return dict(rows_of(FUNNEL)[0])


def by_source() -> list:
    return rows_of(BY_SOURCE)


def by_owner() -> list:
    return rows_of(BY_OWNER)


def by_month() -> list:
    return rows_of(BY_MONTH)


def stage_losses() -> dict:
    return dict(rows_of(STAGE_LOSSES)[0])
