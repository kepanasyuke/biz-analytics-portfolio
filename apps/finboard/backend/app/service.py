from __future__ import annotations

from datetime import date

from . import queries as q

MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
COST_KEYS = ["cogs", "marketing", "payroll", "rent", "other"]
COST_TITLES = {"cogs": "Себестоимость", "marketing": "Маркетинг", "payroll": "ФОТ", "rent": "Аренда", "other": "Прочее"}
QUARTERS = [("Q1", 0, 3), ("Q2", 3, 6), ("Q3", 6, 9), ("Q4", 9, 12)]


def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f} млн ₽".replace(".", ",")


def percent(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def ratio(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def point(label: str, value: float) -> dict:
    return {"label": label, "value": round(float(value), 2)}


def kpi(label: str, value: str, hint: str | None = None) -> dict:
    return {"label": label, "value": value, "delta": None, "hint": hint}


def ebitda(row: dict) -> float:
    return row["revenue"] - sum(row[key] for key in COST_KEYS)


def margin(row: dict) -> float:
    return 100 * ebitda(row) / row["revenue"]


def balance() -> float:
    cash = q.cash_total()
    return cash["inflow"] - cash["outflow"]


def flow() -> float:
    totals = q.totals()
    return totals["revenue"] - sum(totals[key] for key in COST_KEYS)


def monthly_rows() -> list:
    return [dict(row) for row in q.pnl()]


def cash_rows() -> list:
    return [dict(row) for row in q.cash()]


def channels() -> list:
    return [{**dict(row), "cac": row["spend"] / row["customers"], "ltv": 1.6 * row["revenue"] / row["customers"]} for row in q.channels()]


def title_text() -> str:
    kopecks = round(100 * flow() / q.totals()["revenue"])
    return f"Рост есть, но каждый рубль выручки приносит {kopecks} копеек EBITDA"


def meta() -> dict:
    return {
        "brand": "FinBoard",
        "title": title_text(),
        "subtitle": "P&L, денежный поток и unit-экономика каналов за 2025 год. Показывает, где рост съедается себестоимостью и маркетингом.",
        "period": "Январь — декабрь 2025",
        "updated": date.today().strftime("%d.%m.%Y"),
        "source": "SQLite · витрины pnl, cash, channels",
    }


def kpis() -> list:
    totals = q.totals()
    return [
        kpi("Выручка 2025", millions(totals["revenue"]), "начислением"),
        kpi("EBITDA", percent(100 * flow() / totals["revenue"]), millions(flow())),
        kpi("Свободный поток", millions(balance()), "касса за год"),
        kpi("Поток в месяц", millions(balance() / len(MONTHS_SHORT)), "средний"),
        kpi("LTV / CAC", ratio(sum(item["ltv"] for item in channels()) / sum(item["cac"] for item in channels())), "по всем каналам"),
    ]


def revenue_points() -> list:
    return [point(MONTHS_SHORT[index], row["revenue"] / 1_000_000) for index, row in enumerate(monthly_rows())]


def ebitda_points() -> list:
    return [point(MONTHS_SHORT[index], ebitda(row) / 1_000_000) for index, row in enumerate(monthly_rows())]


def cash_points() -> list:
    return [point(MONTHS_SHORT[index], (row["inflow"] - row["outflow"]) / 1_000_000) for index, row in enumerate(cash_rows())]


def series() -> list:
    return [
        {"key": "revenue", "title": "Выручка по месяцам", "kind": "line", "unit": "млн ₽", "points": revenue_points()},
        {"key": "ebitda", "title": "EBITDA по месяцам", "kind": "bar", "unit": "млн ₽", "points": ebitda_points()},
        {"key": "cash", "title": "Денежный поток", "kind": "bar", "unit": "млн ₽", "points": cash_points()},
    ]


def blocks() -> list:
    totals = q.totals()
    return [
        {"kind": "donut", "title": "Структура расходов", "note": "за год", "points": [point(COST_TITLES[key], totals[key]) for key in COST_KEYS]},
        {"kind": "bars", "title": "CAC по каналам", "note": "тыс ₽ за клиента", "points": [point(row["name"], row["cac"] / 1_000) for row in channels()]},
        {"kind": "bars", "title": "Маржа канала", "note": "% от выручки", "points": [point(row["name"], 100 * (row["revenue"] - row["spend"]) / row["revenue"]) for row in channels()]},
        {"kind": "heatmap", "title": "Затраты по кварталам", "note": "млн ₽", "columns": [label for label, *_ in QUARTERS], "rows": quarter_rows()},
    ]


def quarter_rows() -> list:
    rows = monthly_rows()
    return [{"label": COST_TITLES[key], "cells": [round(sum(row[key] for row in rows[start:end]) / 1_000_000) for _, start, end in QUARTERS]} for key in COST_KEYS]


def pnl_row(index: int, row: dict) -> dict:
    return {
        "month": MONTHS_SHORT[index],
        "revenue": row["revenue"],
        "cogs": row["cogs"],
        "gross": row["revenue"] - row["cogs"],
        "opex": sum(row[key] for key in COST_KEYS[1:]),
        "ebitda": ebitda(row),
        "margin": round(margin(row), 1),
    }


def pnl_table() -> dict:
    return {
        "title": "P&L по месяцам",
        "note": "2025, ₽",
        "columns": [
            {"key": "month", "title": "Месяц"},
            {"key": "revenue", "title": "Выручка", "kind": "money", "align": "right"},
            {"key": "cogs", "title": "COGS", "kind": "money", "align": "right"},
            {"key": "gross", "title": "Валовая", "kind": "money", "align": "right"},
            {"key": "opex", "title": "OPEX", "kind": "money", "align": "right"},
            {"key": "ebitda", "title": "EBITDA", "kind": "money", "align": "right"},
            {"key": "margin", "title": "Маржа", "kind": "pct", "align": "right"},
        ],
        "rows": [pnl_row(index, row) for index, row in enumerate(monthly_rows())],
    }


def channels_table() -> dict:
    return {
        "title": "Каналы привлечения",
        "note": "unit-экономика",
        "columns": [
            {"key": "name", "title": "Канал"},
            {"key": "spend", "title": "Расход", "kind": "money", "align": "right"},
            {"key": "customers", "title": "Клиенты", "kind": "int", "align": "right"},
            {"key": "cac", "title": "CAC", "kind": "money", "align": "right"},
            {"key": "ltv", "title": "LTV", "kind": "money", "align": "right"},
            {"key": "ratio", "title": "LTV/CAC", "kind": "ratio", "align": "right"},
        ],
        "rows": [{**item, "ratio": round(item["ltv"] / item["cac"], 2)} for item in channels()],
    }


def cash_table() -> dict:
    return {
        "title": "Денежный поток",
        "note": "кассовый метод",
        "columns": [
            {"key": "month", "title": "Месяц"},
            {"key": "inflow", "title": "Приход", "kind": "money", "align": "right"},
            {"key": "outflow", "title": "Расход", "kind": "money", "align": "right"},
            {"key": "net", "title": "Сальдо", "kind": "money", "align": "right"},
        ],
        "rows": [{"month": MONTHS_SHORT[index], "inflow": row["inflow"], "outflow": row["outflow"], "net": row["inflow"] - row["outflow"]} for index, row in enumerate(cash_rows())],
    }


def tables() -> list:
    return [pnl_table(), channels_table(), cash_table()]


def dashboard() -> dict:
    return {"meta": meta(), "kpis": kpis(), "series": series(), "blocks": blocks(), "tables": tables()}
