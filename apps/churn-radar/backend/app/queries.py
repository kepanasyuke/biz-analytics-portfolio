from __future__ import annotations

from .db import rows_of

ACTIVE_BY_MONTH = """
SELECT m.month,
       SUM(CASE WHEN c.cohort <= m.month AND (c.churn_month IS NULL OR c.churn_month > m.month) THEN 1 ELSE 0 END) AS active,
       SUM(CASE WHEN c.cohort <= m.month AND (c.churn_month IS NULL OR c.churn_month > m.month) THEN c.mrr ELSE 0 END) AS mrr,
       SUM(CASE WHEN c.cohort = m.month THEN 1 ELSE 0 END) AS new_clients
FROM months m CROSS JOIN customers c
GROUP BY m.month ORDER BY m.month
"""

CHURNED_BY_MONTH = """
SELECT churn_month AS month, COUNT(*) AS churned FROM customers
WHERE churn_month IS NOT NULL GROUP BY churn_month ORDER BY churn_month
"""

PLANS = """
SELECT plan, COUNT(*) AS clients, SUM(mrr) AS mrr,
       SUM(CASE WHEN churn_month IS NOT NULL THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn_month IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate
FROM customers GROUP BY plan ORDER BY mrr DESC
"""

REASONS = """
SELECT reason, COUNT(*) AS cases FROM customers
WHERE reason IS NOT NULL GROUP BY reason ORDER BY cases DESC
"""

COHORTS = """
WITH RECURSIVE mm(m) AS (SELECT 0 UNION ALL SELECT m + 1 FROM mm WHERE m < 5)
SELECT c.cohort, mm.m AS step, COUNT(*) AS total,
       SUM(CASE WHEN c.churn_month IS NULL OR c.churn_month > substr(date(c.cohort || '-01', '+' || mm.m || ' months'), 1, 7) THEN 1 ELSE 0 END) AS active
FROM customers c CROSS JOIN mm GROUP BY c.cohort, mm.m ORDER BY c.cohort, mm.m
"""

COHORT_SIZES = "SELECT cohort, COUNT(*) AS clients FROM customers GROUP BY cohort ORDER BY cohort"

RISK = """
SELECT id, plan, mrr, usage FROM customers
WHERE churn_month IS NULL AND usage < 25 ORDER BY mrr DESC LIMIT 8
"""


def active_by_month() -> list:
    return rows_of(ACTIVE_BY_MONTH)


def churned_by_month() -> list:
    return rows_of(CHURNED_BY_MONTH)


def plans() -> list:
    return rows_of(PLANS)


def reasons() -> list:
    return rows_of(REASONS)


def cohorts() -> list:
    return rows_of(COHORTS)


def cohort_sizes() -> list:
    return rows_of(COHORT_SIZES)


def risk() -> list:
    return rows_of(RISK)
