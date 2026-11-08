from __future__ import annotations

import math
from datetime import date

from . import queries as q

MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]


def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f} млн ₽".replace(".", ",")


def thousands(value: float) -> str:
    return f"{value / 1_000:.0f} тыс ₽".replace(",", " ")


def percent(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def point(label: str, value: float) -> dict:
    return {"label": label, "value": round(float(value), 2)}


def kpi(label: str, value: str, hint: str | None = None) -> dict:
    return {"label": label, "value": value, "delta": None, "hint": hint}


def mean(values: list) -> float:
    return sum(values) / len(values)


def variance(values: list) -> float:
    return mean([(value - mean(values)) ** 2 for value in values])


def covariance(xs: list, ys: list) -> float:
    return mean([(x - mean(xs)) * (y - mean(ys)) for x, y in zip(xs, ys, strict=True)])


def slope_of(rows: list) -> float:
    xs, ys = [math.log(row["price"]) for row in rows], [math.log(row["units"]) for row in rows]
    return covariance(xs, ys) / variance(xs) if variance(xs) else 0.0


def class_of(cumulative: float) -> str:
    return "A" if cumulative <= 80 else "B" if cumulative <= 95 else "C"


def categories() -> list:
    return list(dict.fromkeys(row["category"] for row in q.points()))


def elasticities() -> list:
    rows = q.points()
    return [{"category": category, "slope": round(slope_of([row for row in rows if row["category"] == category]), 2)} for category in categories()]


def abc_rows() -> list:
    return [{**dict(row), "class": class_of(row["cumulative"])} for row in q.abc()]


def abc_groups() -> dict:
    rows = abc_rows()
    return {letter: sum(row["revenue"] for row in rows if row["class"] == letter) for letter in ("A", "B", "C")}


def title_text() -> str:
    most = max(elasticities(), key=lambda row: abs(row["slope"]))
    return f"Цена в «{most['category']}» эластична на {abs(most['slope']):.1f}: скидка 5% даёт около {abs(most['slope']) * 5:.0f}% к спросу"


def meta() -> dict:
    return {
        "brand": "Pricing Lab",
        "title": title_text(),
        "subtitle": "Ценовая аналитика портфеля: эластичность по категориям, маржа, эффект промо и ABC-разрез по выручке.",
        "period": "Январь — декабрь 2025",
        "updated": date.today().strftime("%d.%m.%Y"),
        "source": "SQLite · витрины products, prices",
    }


def kpis() -> list:
    totals = q.totals()
    revenue = totals["revenue"]
    return [
        kpi("Выручка", millions(revenue), "по прайсу продаж"),
        kpi("Маржа", percent(100 * (revenue - totals["cost"]) / revenue), millions(revenue - totals["cost"])),
        kpi("Эластичность", f"{slope_of(q.points()):.2f}", "лог-лог по портфелю"),
        kpi("Средняя скидка", percent(100 * (totals["discount"] or 0)), "по всем продажам"),
        kpi("Промо-выручка", percent(q.promo_share()), "продажи со скидкой"),
    ]


def series() -> list:
    rows = q.monthly()
    return [
        {"key": "price", "title": "Средняя цена", "kind": "line", "unit": "₽ за единицу", "points": [point(MONTHS_SHORT[index], row["avg_price"]) for index, row in enumerate(rows)]},
        {"key": "units", "title": "Отгрузки", "kind": "bar", "unit": "шт.", "points": [point(MONTHS_SHORT[index], row["units"]) for index, row in enumerate(rows)]},
        {"key": "margin", "title": "Маржа по месяцам", "kind": "bar", "unit": "%", "points": [point(MONTHS_SHORT[index], row["margin"]) for index, row in enumerate(rows)]},
    ]


def blocks() -> list:
    groups = abc_groups()
    return [
        {"kind": "bars", "title": "Маржа по категориям", "note": "% от выручки", "points": [point(row["category"], row["margin"]) for row in q.by_category()]},
        {"kind": "donut", "title": "Выручка по ABC-классам", "note": "A — 80% оборота", "points": [point(f"Класс {letter}", value) for letter, value in groups.items()]},
        {"kind": "bars", "title": "Эластичность спроса", "note": "наклон log–log", "points": [point(row["category"], abs(row["slope"])) for row in elasticities()]},
        {"kind": "heatmap", "title": "Маржа по кварталам", "note": "% · категория × квартал", "columns": QUARTERS, "rows": quarter_rows()},
    ]


def quarter_rows() -> list:
    return [{"label": row["category"], "cells": [row["q1"] or 0, row["q2"] or 0, row["q3"] or 0, row["q4"] or 0]} for row in q.quarter_margin()]


def product_classes() -> dict:
    return {row["id"]: class_of(row["cumulative"]) for row in q.abc()}


def product_rows() -> list:
    classes = product_classes()
    return [{**dict(row), "class": classes.get(row["id"], "C")} for row in q.products()]


def products_table() -> dict:
    return {
        "title": "Товары",
        "note": "цена, маржа, класс",
        "columns": [
            {"key": "name", "title": "Товар"},
            {"key": "category", "title": "Категория"},
            {"key": "avg_price", "title": "Средняя цена", "kind": "money", "align": "right"},
            {"key": "units", "title": "Продано", "kind": "int", "align": "right"},
            {"key": "revenue", "title": "Выручка", "kind": "money", "align": "right"},
            {"key": "margin", "title": "Маржа", "kind": "pct", "align": "right"},
            {"key": "discount", "title": "Скидка", "kind": "pct", "align": "right"},
            {"key": "class", "title": "ABC"},
        ],
        "rows": product_rows(),
    }


def promo_table() -> dict:
    return {
        "title": "Промо против обычных продаж",
        "note": "средние значения",
        "columns": [
            {"key": "mode", "title": "Режим"},
            {"key": "cases", "title": "Наблюдений", "kind": "int", "align": "right"},
            {"key": "avg_units", "title": "Единиц", "kind": "int", "align": "right"},
            {"key": "avg_revenue", "title": "Выручка", "kind": "money", "align": "right"},
            {"key": "margin", "title": "Маржа", "kind": "pct", "align": "right"},
        ],
        "rows": [dict(row) for row in q.promo()],
    }


def abc_table() -> dict:
    return {
        "title": "ABC-анализ",
        "note": "накопительная доля выручки",
        "columns": [
            {"key": "name", "title": "Товар"},
            {"key": "category", "title": "Категория"},
            {"key": "revenue", "title": "Выручка", "kind": "money", "align": "right"},
            {"key": "cumulative", "title": "Накопительно", "kind": "pct", "align": "right"},
            {"key": "class", "title": "Класс"},
        ],
        "rows": abc_rows(),
    }


def tables() -> list:
    return [products_table(), promo_table(), abc_table()]


def dashboard() -> dict:
    return {"meta": meta(), "kpis": kpis(), "series": series(), "blocks": blocks(), "tables": tables()}
