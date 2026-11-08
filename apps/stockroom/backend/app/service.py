from __future__ import annotations

from datetime import date

from . import queries as q

MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
CAPACITY = {"Москва": 1600, "Санкт-Петербург": 1200, "Екатеринбург": 900}
WAREHOUSE_NAMES = ["Москва", "Санкт-Петербург", "Екатеринбург"]
STATUS_ORDER = {"дефицит": 0, "нет в наличии": 1, "мёртвый запас": 2, "норма": 3}


def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f} млн ₽".replace(".", ",")


def thousands(value: float) -> str:
    return f"{value / 1_000:.0f} тыс ₽"


def count(value: float) -> str:
    return f"{int(value):,}".replace(",", " ")


def percent(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def point(label: str, value: float) -> dict:
    return {"label": label, "value": round(float(value), 2)}


def kpi(label: str, value: str, hint: str | None = None, change: float | None = None) -> dict:
    return {"label": label, "value": value, "delta": change, "hint": hint}


def status_of(item: dict) -> str:
    short = item["days"] < 14
    return "нет в наличии" if item["qty"] == 0 else "мёртвый запас" if item["outbound"] == 0 else "дефицит" if short else "норма"


def metrics(row) -> dict:
    daily = row["outbound"] / 90
    days = 999 if daily == 0 else round(row["qty"] / daily)
    return {"id": row["id"], "name": row["name"], "category": row["category"], "qty": row["qty"], "value": round(row["qty"] * row["cost"]), "outbound": row["outbound"], "days": days}


def enriched(since: str) -> list:
    return [{**item, "status": status_of(item)} for item in (metrics(row) for row in q.items(since))]


def risky(items: list) -> list:
    return [item for item in items if item["status"] in ("дефицит", "нет в наличии")]


def dead(items: list) -> list:
    return [item for item in items if item["status"] == "мёртвый запас"]


def title_text() -> str:
    items = enriched("2025-09")
    return f"{len(dead(items))} SKU без движения, {len(risky(items))} в дефиците — закупка идёт вслепую"


def meta() -> dict:
    return {
        "brand": "Stockroom",
        "title": title_text(),
        "subtitle": "Остатки по трём складам, оборачиваемость и покрытие спроса. Решения по закупке — по дням запаса, а не по сумме остатка.",
        "period": "Январь — декабрь 2025",
        "updated": date.today().strftime("%d.%m.%Y"),
        "source": "SQLite · витрина stock",
    }


def load_share() -> float:
    return 100 * sum(row["units"] for row in q.by_warehouse()) / sum(CAPACITY.values())


def turnover_days() -> int:
    return round(365 * q.stock_value() / max(1.0, sale_cost()))


def kpis() -> list:
    items = enriched("2025-09")
    return [
        kpi("Стоимость запасов", millions(q.stock_value()), "по себестоимости"),
        kpi("Оборачиваемость", f"{turnover_days()} дн", "cost of goods sold"),
        kpi("SKU в дефиците", count(len(risky(items))), "покрытие < 14 дней"),
        kpi("Мёртвый запас", percent(100 * len(dead(items)) / len(items)), f"{len(dead(items))} SKU без продаж"),
        kpi("Заполненность складов", percent(load_share()), "к проектной ёмкости"),
    ]


def sale_cost() -> float:
    return sum(r["revenue"] for r in q.by_category("2025"))


def series() -> list:
    months = q.monthly()
    return [
        {"key": "outbound", "title": "Отгрузки по месяцам", "kind": "line", "unit": "шт.", "points": [point(MONTHS_SHORT[int(r["month"][5:]) - 1], r["outbound"]) for r in months]},
        {"key": "inbound", "title": "Поступления на склад", "kind": "bar", "unit": "шт.", "points": [point(MONTHS_SHORT[int(r["month"][5:]) - 1], r["inbound"]) for r in months]},
        {"key": "gap", "title": "Разрыв приход / расход", "kind": "bar", "unit": "шт.", "points": [point(MONTHS_SHORT[int(r["month"][5:]) - 1], r["inbound"] - r["outbound"]) for r in months]},
    ]


def blocks() -> list:
    items = sorted([item for item in enriched("2025-09") if item["status"] in ("дефицит", "нет в наличии")], key=lambda item: item["days"])[:7]
    return [
        {"kind": "donut", "title": "Стоимость запасов по складам", "note": "себестоимость", "points": [point(r["warehouse"], r["value"]) for r in q.by_warehouse()]},
        {"kind": "bars", "title": "Оборот по категориям", "note": "2025, млн ₽", "points": [point(r["category"], r["revenue"] / 1_000_000) for r in q.by_category("2025")]},
        {"kind": "heatmap", "title": "Остатки: категория × склад", "note": "шт.", "columns": ["Мск", "СПб", "Екб"], "rows": matrix_rows()},
        {"kind": "bars", "title": "Дефицит: дни запаса", "note": "ниже 14 дней", "points": [point(item["name"], item["days"]) for item in items]},
    ]


def categories_of(rows: list) -> list:
    return list(dict.fromkeys(row["category"] for row in rows))


def cells_of(rows: list, category: str) -> list:
    return [next((row["units"] for row in rows if row["category"] == category and row["warehouse"] == name), 0) for name in WAREHOUSE_NAMES]


def matrix_rows() -> list:
    rows = q.matrix()
    return [{"label": category, "cells": cells_of(rows, category)} for category in categories_of(rows)]


def tables() -> list:
    items = sorted(enriched("2025-09"), key=lambda item: STATUS_ORDER[item["status"]])
    return [
        {
            "title": "SKU под контролем",
            "note": "отсортировано по риску",
            "columns": [
                {"key": "name", "title": "Товар"},
                {"key": "category", "title": "Категория"},
                {"key": "qty", "title": "Остаток", "kind": "int", "align": "right"},
                {"key": "outbound", "title": "Отгрузки 90 дн", "kind": "int", "align": "right"},
                {"key": "days", "title": "Дней запаса", "kind": "int", "align": "right"},
                {"key": "value", "title": "Стоимость", "kind": "money", "align": "right"},
                {"key": "status", "title": "Статус"},
            ],
            "rows": items,
        }
    ]


def dashboard() -> dict:
    return {"meta": meta(), "kpis": kpis(), "series": series(), "blocks": blocks(), "tables": tables()}
