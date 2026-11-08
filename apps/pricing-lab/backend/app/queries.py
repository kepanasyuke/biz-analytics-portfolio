from __future__ import annotations

from .db import rows_of, scalar

TOTALS = """
SELECT SUM(pr.price * pr.units) AS revenue, SUM(pr.units * p.cost) AS cost,
       SUM(pr.units) AS units, AVG(pr.discount) AS discount
FROM prices pr JOIN products p ON p.id = pr.product_id
"""

BY_CATEGORY = """
SELECT p.category,
       SUM(pr.price * pr.units) AS revenue,
       SUM(pr.units * p.cost) AS cost,
       SUM(pr.units) AS units,
       ROUND(100.0 * (SUM(pr.price * pr.units) - SUM(pr.units * p.cost)) / SUM(pr.price * pr.units), 1) AS margin
FROM prices pr JOIN products p ON p.id = pr.product_id
GROUP BY p.category ORDER BY revenue DESC
"""

MONTHLY = """
SELECT pr.month, SUM(pr.price * pr.units) AS revenue, SUM(pr.units) AS units,
       ROUND(AVG(pr.price), 0) AS avg_price,
       ROUND(100.0 * (SUM(pr.price * pr.units) - SUM(pr.units * p.cost)) / SUM(pr.price * pr.units), 1) AS margin
FROM prices pr JOIN products p ON p.id = pr.product_id
GROUP BY pr.month ORDER BY pr.month
"""

PRODUCTS = """
SELECT p.id, p.name, p.category, p.base_price, p.cost,
       SUM(pr.units) AS units,
       ROUND(AVG(pr.price), 0) AS avg_price,
       ROUND(SUM(pr.price * pr.units)) AS revenue,
       ROUND(100.0 * (SUM(pr.price * pr.units) - SUM(pr.units * p.cost)) / SUM(pr.price * pr.units), 1) AS margin,
       ROUND(100.0 * AVG(pr.discount), 1) AS discount
FROM prices pr JOIN products p ON p.id = pr.product_id
GROUP BY p.id ORDER BY revenue DESC
"""

ABC = """
WITH r AS (
    SELECT p.id, p.name, p.category, SUM(pr.price * pr.units) AS revenue
    FROM prices pr JOIN products p ON p.id = pr.product_id GROUP BY p.id
)
SELECT id, name, category, revenue,
       ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC, name) / SUM(revenue) OVER (), 1) AS cumulative
FROM r ORDER BY revenue DESC
"""

POINTS = """
SELECT p.category, pr.price AS price, pr.units AS units
FROM prices pr JOIN products p ON p.id = pr.product_id
"""

PROMO = """
SELECT CASE WHEN pr.discount > 0 THEN 'С промо' ELSE 'Без промо' END AS mode,
       COUNT(*) AS cases, ROUND(AVG(pr.units)) AS avg_units,
       ROUND(AVG(pr.price * pr.units)) AS avg_revenue,
       ROUND(100.0 * AVG((pr.price - p.cost) / pr.price), 1) AS margin
FROM prices pr JOIN products p ON p.id = pr.product_id
GROUP BY mode ORDER BY mode DESC
"""

QUARTER_MARGIN = """
SELECT p.category,
       ROUND(100.0 * (SUM(CASE WHEN pr.month < '2025-04' THEN pr.price * pr.units - pr.units * p.cost END)) /
             NULLIF(SUM(CASE WHEN pr.month < '2025-04' THEN pr.price * pr.units END), 0), 1) AS q1,
       ROUND(100.0 * (SUM(CASE WHEN pr.month >= '2025-04' AND pr.month < '2025-07' THEN pr.price * pr.units - pr.units * p.cost END)) /
             NULLIF(SUM(CASE WHEN pr.month >= '2025-04' AND pr.month < '2025-07' THEN pr.price * pr.units END), 0), 1) AS q2,
       ROUND(100.0 * (SUM(CASE WHEN pr.month >= '2025-07' AND pr.month < '2025-10' THEN pr.price * pr.units - pr.units * p.cost END)) /
             NULLIF(SUM(CASE WHEN pr.month >= '2025-07' AND pr.month < '2025-10' THEN pr.price * pr.units END), 0), 1) AS q3,
       ROUND(100.0 * (SUM(CASE WHEN pr.month >= '2025-10' THEN pr.price * pr.units - pr.units * p.cost END)) /
             NULLIF(SUM(CASE WHEN pr.month >= '2025-10' THEN pr.price * pr.units END), 0), 1) AS q4
FROM prices pr JOIN products p ON p.id = pr.product_id
GROUP BY p.category ORDER BY q4 DESC
"""

LOW_MARGIN = """
SELECT COUNT(*) FROM (
    SELECT p.id FROM prices pr JOIN products p ON p.id = pr.product_id
    GROUP BY p.id
    HAVING 100.0 * (SUM(pr.price * pr.units) - SUM(pr.units * p.cost)) / SUM(pr.price * pr.units) < 25
)
"""

PROMO_SHARE = """
SELECT ROUND(100.0 * SUM(CASE WHEN discount > 0 THEN price * units ELSE 0 END) / SUM(price * units), 1)
FROM prices
"""


def totals() -> dict:
    return dict(rows_of(TOTALS)[0])


def by_category() -> list:
    return rows_of(BY_CATEGORY)


def monthly() -> list:
    return rows_of(MONTHLY)


def products() -> list:
    return rows_of(PRODUCTS)


def abc() -> list:
    return rows_of(ABC)


def points() -> list:
    return rows_of(POINTS)


def promo() -> list:
    return rows_of(PROMO)


def quarter_margin() -> list:
    return rows_of(QUARTER_MARGIN)


def low_margin() -> float:
    return scalar(LOW_MARGIN)


def promo_share() -> float:
    return scalar(PROMO_SHARE)
