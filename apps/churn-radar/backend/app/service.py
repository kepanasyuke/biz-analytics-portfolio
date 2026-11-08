from __future__ import annotations

from datetime import date

from . import queries as q

MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
COHORT_STEPS = 6


def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f} млн ₽".replace(".", ",")


def thousands(value: float) -> str:
    return f"{value / 1_000:.0f} тыс ₽".replace(",", " ")


def percent(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def ratio(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def point(label: str, value: float) -> dict:
    return {"label": label, "value": round(float(value), 2)}


def kpi(label: str, value: str, hint: str | None = None) -> dict:
    return {"label": label, "value": value, "delta": None, "hint": hint}


def active() -> list:
    return [dict(row) for row in q.active_by_month()]


def churned() -> list:
    return [dict(row) for row in q.churned_by_month()]


def churn_rates() -> list:
    months = active()
    lookup = {row["month"]: row["churned"] for row in churned()}
    return [{"month": row["month"], "rate": 100 * lookup.get(row["month"], 0) / max(1, previous_active(months, index))} for index, row in enumerate(months)]


def previous_active(months: list, index: int) -> int:
    return months[index - 1]["active"] if index else months[0]["active"]


def average_churn() -> float:
    rates = [item["rate"] for item in churn_rates()]
    return sum(rates) / len(rates)


def title_text() -> str:
    return f"Отток {percent(average_churn())} в месяц: каждый клиент живёт в среднем {ratio(1 / (average_churn() / 100))} месяцев"


def meta() -> dict:
    return {
        "brand": "Churn Radar",
        "title": title_text(),
        "subtitle": "Когортный анализ оттока, MRR и причины потерь. Видно, на каком месяце жизни уходит клиент и сколько это стоит.",
        "period": "Январь — декабрь 2025",
        "updated": date.today().strftime("%d.%m.%Y"),
        "source": "SQLite · витрины customers, months",
    }


def arpu_of(row: dict) -> float:
    return row["mrr"] / max(1, row["active"])


def churn_rate() -> float:
    return average_churn() / 100


def kpis() -> list:
    last = active()[-1]
    return [
        kpi("MRR", millions(last["mrr"]), "последний месяц"),
        kpi("Отток", percent(average_churn()), "среднее за год"),
        kpi("Клиентов", f"{last['active']:,}".replace(",", " "), f"+{last['new_clients']} новых"),
        kpi("LTV", thousands(lifetime_ltv()), f"ARPU {thousands(arpu_of(last))}"),
        kpi("Срок жизни", f"{ratio(lifetime())} мес", "при текущем оттоке"),
    ]


def lifetime() -> float:
    return 1 / churn_rate() if churn_rate() else 0


def lifetime_ltv() -> float:
    return arpu_of(active()[-1]) * lifetime()


def series() -> list:
    rows = active()
    rates = churn_rates()
    return [
        {"key": "mrr", "title": "MRR по месяцам", "kind": "line", "unit": "млн ₽", "points": [point(MONTHS_SHORT[index], row["mrr"] / 1_000_000) for index, row in enumerate(rows)]},
        {"key": "churn", "title": "Отток по месяцам", "kind": "bar", "unit": "% от базы", "points": [point(MONTHS_SHORT[index], item["rate"]) for index, item in enumerate(rates)]},
        {"key": "new", "title": "Новые клиенты", "kind": "bar", "unit": "шт.", "points": [point(MONTHS_SHORT[index], row["new_clients"]) for index, row in enumerate(rows)]},
    ]


def blocks() -> list:
    reasons = q.reasons()
    risk = q.risk()
    return [
        {"kind": "heatmap", "title": "Удержание по когортам", "note": "% активных, M0–M5", "columns": [f"M{step}" for step in range(COHORT_STEPS)], "rows": cohort_rows()},
        {"kind": "donut", "title": "Причины оттока", "note": "по обращениям", "points": [point(row["reason"], row["cases"]) for row in reasons]},
        {"kind": "bars", "title": "Отток по тарифам", "note": "% клиентов", "points": [point(row["plan"], row["churn_rate"]) for row in q.plans()]},
        {"kind": "bars", "title": "Под риском", "note": "MRR, тыс ₽", "points": [point(f"ID {row['id']} · {row['plan']}", row["mrr"] / 1_000) for row in risk]},
    ]


def cohort_rows() -> list:
    rows = q.cohorts()
    cohorts = list(dict.fromkeys(row["cohort"] for row in rows))
    return [{"label": _month_label(cohort), "cells": [round(100 * cell["active"] / cell["total"]) for cell in rows if cell["cohort"] == cohort]} for cohort in cohorts]


def _month_label(month: str) -> str:
    return f"{MONTHS_SHORT[int(month[5:]) - 1]} {month[:4]}"


def plans_table() -> dict:
    return {
        "title": "Тарифы",
        "note": "клиенты и отток",
        "columns": [
            {"key": "plan", "title": "Тариф"},
            {"key": "clients", "title": "Клиенты", "kind": "int", "align": "right"},
            {"key": "mrr", "title": "MRR", "kind": "money", "align": "right"},
            {"key": "churned", "title": "Ушли", "kind": "int", "align": "right"},
            {"key": "churn_rate", "title": "Отток", "kind": "pct", "align": "right"},
        ],
        "rows": [dict(row) for row in q.plans()],
    }


def risk_table() -> dict:
    return {
        "title": "Клиенты с низким использованием",
        "note": "usage < 25%",
        "columns": [
            {"key": "id", "title": "ID", "kind": "int", "align": "right"},
            {"key": "plan", "title": "Тариф"},
            {"key": "mrr", "title": "MRR", "kind": "money", "align": "right"},
            {"key": "usage", "title": "Использование", "kind": "int", "align": "right"},
        ],
        "rows": [dict(row) for row in q.risk()],
    }


def reasons_table() -> dict:
    return {
        "title": "Причины ухода",
        "note": "за 2025 год",
        "columns": [{"key": "reason", "title": "Причина"}, {"key": "cases", "title": "Случаи", "kind": "int", "align": "right"}],
        "rows": [dict(row) for row in q.reasons()],
    }


def tables() -> list:
    return [plans_table(), risk_table(), reasons_table()]


def dashboard() -> dict:
    return {"meta": meta(), "kpis": kpis(), "series": series(), "blocks": blocks(), "tables": tables()}
