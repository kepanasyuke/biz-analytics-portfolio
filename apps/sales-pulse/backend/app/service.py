from __future__ import annotations

from datetime import date

from . import queries as q

MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
YEAR = "2025"
PREV = "2024"


def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f} млн ₽".replace(".", ",")


def thousands(value: float) -> str:
    return f"{value / 1_000:.0f} тыс ₽"


def count(value: float) -> str:
    return f"{int(value):,}".replace(",", " ")


def percent(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def delta(current: float, previous: float) -> float:
    return 0.0 if previous == 0 else round(100 * (current - previous) / previous, 1)


def point(label: str, value: float) -> dict:
    return {"label": label, "value": round(float(value), 2)}


def kpi(label: str, value: str, change: float | None = None, hint: str | None = None) -> dict:
    return {"label": label, "value": value, "delta": change, "hint": hint}


def meta() -> dict:
    return {
        "brand": "Sales Pulse",
        "title": "Выручка выросла на четверть, но план закрывают три менеджера из шести",
        "subtitle": "B2B-дистрибуция: 4 212 сделок за два года. Отчёт по выручке, каналам и загрузке отдела продаж.",
        "period": "Январь — декабрь 2025",
        "updated": date.today().strftime("%d.%m.%Y"),
        "source": "SQLite · витрина deals",
    }


def kpis() -> list:
    fact, target = q.revenue(YEAR), q.plan(YEAR)
    return [
        kpi("Выручка 2025", millions(fact), delta(fact, q.revenue(PREV))),
        kpi("Выполнение плана", percent(100 * fact / target if target else 0), None, f"план {millions(target)}"),
        kpi("Средний чек", thousands(fact / q.won(YEAR) if q.won(YEAR) else 0), delta(fact / q.won(YEAR), q.revenue(PREV) / q.won(PREV))),
        kpi("Сделок закрыто", count(q.won(YEAR)), delta(q.won(YEAR), q.won(PREV))),
        kpi("Цикл сделки", f"{q.cycle(YEAR):.0f} дн", delta(q.cycle(YEAR), q.cycle(PREV))),
    ]


def series() -> list:
    months = q.by_month(YEAR)
    return [
        {"key": "revenue", "title": "Выручка по месяцам", "kind": "line", "unit": "млн ₽", "points": [point(MONTHS_SHORT[int(r["month"][5:]) - 1], r["revenue"] / 1_000_000) for r in months]},
        {"key": "deals", "title": "Закрытых сделок", "kind": "bar", "unit": "шт.", "points": [point(MONTHS_SHORT[int(r["month"][5:]) - 1], r["deals"]) for r in months]},
        {"key": "avg", "title": "Средний чек", "kind": "bar", "unit": "тыс ₽", "points": [point(MONTHS_SHORT[int(r["month"][5:]) - 1], r["avg_deal"] / 1_000) for r in months]},
    ]


def blocks() -> list:
    return [
        {"kind": "funnel", "title": "Воронка сделок", "note": "стадии из CRM", "points": [point(r["stage"], r["deals"]) for r in q.funnel(YEAR)]},
        {"kind": "donut", "title": "Выручка по каналам", "note": "доля в обороте", "points": [point(r["channel"], r["revenue"]) for r in q.by_channel(YEAR)]},
        {"kind": "bars", "title": "Выручка по командам", "note": "город присутствия", "points": [point(r["team"], r["revenue"] / 1_000_000) for r in q.by_team(YEAR)]},
        {"kind": "bars", "title": "Средний цикл сделки", "note": "дни до закрытия", "points": [point(r["name"].split()[0], r["cycle"] or 0) for r in q.managers(YEAR)]},
    ]


def tables() -> list:
    rows = q.managers(YEAR)
    return [
        {
            "title": "Менеджеры",
            "note": f"{len(rows)} человек · 2025",
            "columns": [
                {"key": "name", "title": "Менеджер"},
                {"key": "team", "title": "Команда"},
                {"key": "deals", "title": "Сделок", "kind": "int", "align": "right"},
                {"key": "won", "title": "Выиграно", "kind": "int", "align": "right"},
                {"key": "win_rate", "title": "Win rate", "kind": "pct", "align": "right"},
                {"key": "revenue", "title": "Выручка", "kind": "money", "align": "right"},
                {"key": "cycle", "title": "Цикл, дн", "kind": "ratio", "align": "right"},
            ],
            "rows": [dict(row) for row in rows],
        }
    ]


def dashboard() -> dict:
    return {"meta": meta(), "kpis": kpis(), "series": series(), "blocks": blocks(), "tables": tables()}
