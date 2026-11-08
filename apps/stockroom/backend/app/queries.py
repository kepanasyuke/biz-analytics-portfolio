from __future__ import annotations

from .db import rows_of, scalar

STOCK_VALUE = """
SELECT SUM(s.qty * k.cost) FROM stock s JOIN sku k ON k.id = s.sku_id
"""

BY_WAREHOUSE = """
SELECT s.warehouse, SUM(s.qty * k.cost) AS value, SUM(s.qty) AS units
FROM stock s JOIN sku k ON k.id = s.sku_id GROUP BY s.warehouse ORDER BY value DESC
"""

BY_CATEGORY = """
SELECT k.category, SUM(m.outbound * k.price) AS revenue, SUM(m.outbound) AS units
FROM movements m JOIN sku k ON k.id = m.sku_id WHERE m.month LIKE ? GROUP BY k.category ORDER BY revenue DESC
"""

MONTHLY = """
SELECT month, SUM(outbound) AS outbound, SUM(inbound) AS inbound
FROM movements GROUP BY month ORDER BY month
"""

ITEMS = """
SELECT k.id, k.name, k.category, k.price, k.cost,
       COALESCE(st.qty, 0) AS qty,
       COALESCE(mv.outbound, 0) AS outbound
FROM sku k
LEFT JOIN (SELECT sku_id, SUM(qty) AS qty FROM stock GROUP BY sku_id) st ON st.sku_id = k.id
LEFT JOIN (SELECT sku_id, SUM(outbound) AS outbound FROM movements WHERE month >= ? GROUP BY sku_id) mv ON mv.sku_id = k.id
ORDER BY mv.outbound * k.price DESC
"""

MATRIX = """
SELECT k.category, s.warehouse, SUM(s.qty) AS units
FROM stock s JOIN sku k ON k.id = s.sku_id GROUP BY k.category, s.warehouse
ORDER BY k.category, s.warehouse
"""


def stock_value() -> float:
    return scalar(STOCK_VALUE)


def by_warehouse() -> list:
    return rows_of(BY_WAREHOUSE)


def by_category(year: str) -> list:
    return rows_of(BY_CATEGORY, (f"{year}-%",))


def monthly() -> list:
    return rows_of(MONTHLY)


def items(since: str) -> list:
    return rows_of(ITEMS, (since,))


def matrix() -> list:
    return rows_of(MATRIX)
