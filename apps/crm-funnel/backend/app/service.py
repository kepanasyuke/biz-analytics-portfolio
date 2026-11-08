from __future__ import annotations

from datetime import date

from . import queries as q

MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
SLA_MINUTES = 30


def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f} млн ₽".replace(".", ",")


def count(value: float) -> str:
    return f"{int(value):,}".replace(",", " ")


def percent(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def point(label: str, value: float) -> dict:
    return {"label": label, "value": round(float(value), 2)}


def kpi(label: str, value: str, hint: str | None = None, delta: float | None = None) -> dict:
    return {"label": label, "value": value, "delta": delta, "hint": hint}


def conversion() -> float:
    return 100 * q.won() / q.total()


def title_text() -> str:
    return f"{round(conversion())}% лидов доходят до сделки — на этапе КП теряется каждый второй"


def meta() -> dict:
    return {
        "brand": "CRM Funnel",
        "title": title_text(),
        "subtitle": f"Воронка продаж за 2025 год: {count(q.total())} лидов, SLA первого ответа {SLA_MINUTES} минут, потери по этапам.",
        "period": "Январь — декабрь 2025",
        "updated": date.today().strftime("%d.%m.%Y"),
        "source": "SQLite · витрина leads",
    }


def kpis() -> list:
    return [
        kpi("Лидов за год", count(q.total()), "все источники"),
        kpi("Конверсия в сделку", percent(conversion()), f"{count(q.won())} сделок"),
        kpi("Медианный ответ", f"{q.median_response('2025-06'):.0f} мин", "первый контакт"),
        kpi("Ответ в SLA", percent(100 * q.in_sla(SLA_MINUTES) / q.total()), f"до {SLA_MINUTES} минут"),
        kpi("Выручка с лида", millions(q.revenue()), "сумма сделок"),
    ]


def series() -> list:
    rows = q.by_month()
    return [
        {"key": "leads", "title": "Лиды по месяцам", "kind": "line", "unit": "шт.", "points": [point(MONTHS_SHORT[index], row["leads"]) for index, row in enumerate(rows)]},
        {"key": "won", "title": "Закрытые сделки", "kind": "bar", "unit": "шт.", "points": [point(MONTHS_SHORT[index], row["won"]) for index, row in enumerate(rows)]},
        {"key": "revenue", "title": "Выручка по месяцам", "kind": "bar", "unit": "млн ₽", "points": [point(MONTHS_SHORT[index], row["revenue"] / 1_000_000) for index, row in enumerate(rows)]},
    ]


def funnel_points() -> list:
    data = q.funnel()
    return [point("Лиды", data["leads"]), point("Квалификация", data["qualified"]), point("Презентация", data["presented"]), point("КП", data["proposal"]), point("Сделка", data["won"])]


def blocks() -> list:
    return [
        {"kind": "funnel", "title": "Воронка от лида до сделки", "note": "абсолютные значения", "points": funnel_points()},
        {"kind": "donut", "title": "Лиды по источникам", "note": "доля канала", "points": [point(row["source"], row["leads"]) for row in q.by_source()]},
        {"kind": "bars", "title": "Конверсия по источникам", "note": "% в сделку", "points": [point(row["source"], 100 * row["won"] / row["leads"]) for row in q.by_source()]},
        {"kind": "bars", "title": "Средний первый ответ", "note": "минуты по менеджерам", "points": [point(row["owner"], row["response"]) for row in q.by_owner()]},
    ]


COLUMNS_COMMON = [
    {"key": "leads", "title": "Лиды", "kind": "int", "align": "right"},
    {"key": "won", "title": "Сделки", "kind": "int", "align": "right"},
    {"key": "conversion", "title": "Конверсия", "kind": "pct", "align": "right"},
    {"key": "revenue", "title": "Выручка", "kind": "money", "align": "right"},
    {"key": "response", "title": "Ответ, мин", "kind": "int", "align": "right"},
]


def conversion_row(row) -> dict:
    return {**dict(row), "conversion": round(100 * row["won"] / row["leads"], 1)}


def sources_table() -> dict:
    return {
        "title": "Источники",
        "note": "лиды и деньги",
        "columns": [{"key": "source", "title": "Источник"}, *COLUMNS_COMMON],
        "rows": [conversion_row(row) for row in q.by_source()],
    }


def owners_table() -> dict:
    return {
        "title": "Менеджеры",
        "note": "нагрузка и результат",
        "columns": [{"key": "owner", "title": "Менеджер"}, *COLUMNS_COMMON],
        "rows": [conversion_row(row) for row in q.by_owner()],
    }


def losses_table() -> dict:
    return {
        "title": "Потери по этапам",
        "note": "сколько лидов дошло",
        "columns": [
            {"key": "stage", "title": "Этап"},
            {"key": "reached", "title": "Дошло", "kind": "int", "align": "right"},
            {"key": "lost", "title": "Потеряно", "kind": "int", "align": "right"},
            {"key": "share", "title": "Доля потерь", "kind": "pct", "align": "right"},
        ],
        "rows": loss_rows(),
    }


def tables() -> list:
    return [sources_table(), owners_table(), losses_table()]


def loss_steps() -> list:
    stages = q.stage_losses()
    return [
        ("Квалификация", int(q.total()), stages["after_qualification"]),
        ("Презентация", stages["after_qualification"], stages["after_presentation"]),
        ("КП", stages["after_presentation"], stages["after_proposal"]),
        ("Сделка", stages["after_proposal"], stages["after_deal"]),
    ]


def loss_rows() -> list:
    return [{"stage": label, "reached": int(after), "lost": int(before) - int(after), "share": round(100 * (before - after) / before, 1) if before else 0} for label, before, after in loss_steps()]


def dashboard() -> dict:
    return {"meta": meta(), "kpis": kpis(), "series": series(), "blocks": blocks(), "tables": tables()}
