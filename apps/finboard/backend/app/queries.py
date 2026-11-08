from __future__ import annotations

from .db import rows_of

PNL = "SELECT * FROM pnl ORDER BY month"
CASH = "SELECT * FROM cash ORDER BY month"
CHANNELS = "SELECT * FROM channels ORDER BY spend DESC"

TOTALS = """
SELECT SUM(revenue) AS revenue, SUM(cogs) AS cogs, SUM(marketing) AS marketing,
       SUM(payroll) AS payroll, SUM(rent) AS rent, SUM(other) AS other
FROM pnl
"""

CASH_TOTAL = "SELECT SUM(inflow) AS inflow, SUM(outflow) AS outflow FROM cash"


def pnl() -> list:
    return rows_of(PNL)


def cash() -> list:
    return rows_of(CASH)


def channels() -> list:
    return rows_of(CHANNELS)


def totals() -> dict:
    return dict(rows_of(TOTALS)[0])


def cash_total() -> dict:
    return dict(rows_of(CASH_TOTAL)[0])
