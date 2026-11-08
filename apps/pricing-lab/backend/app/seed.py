from __future__ import annotations

from random import Random

from .db import connect

MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]
PRODUCTS = [
    (1, "Наушники Pro", "Электроника", 8_900, 4_300, 420, 1.7),
    (2, "Колонка Mini", "Электроника", 5_400, 2_600, 380, 1.8),
    (3, "Пауэрбанк 20K", "Электроника", 3_200, 1_500, 610, 2.0),
    (4, "Смарт-часы S2", "Электроника", 12_400, 6_100, 240, 1.5),
    (5, "Роутер AX", "Электроника", 6_100, 2_900, 330, 1.6),
    (6, "Чехол Ultra", "Аксессуары", 1_200, 380, 1_250, 2.4),
    (7, "Кабель USB-C 2м", "Аксессуары", 790, 220, 1_640, 2.7),
    (8, "Держатель авто", "Аксессуары", 1_450, 520, 880, 2.2),
    (9, "Стекло защитное", "Аксессуары", 590, 140, 2_100, 2.9),
    (10, "Сумка для ноутбука", "Аксессуары", 3_400, 1_400, 340, 1.9),
    (11, "Шуруповёрт 18V", "Инструмент", 9_800, 5_200, 190, 1.1),
    (12, "Набор бит 40шт", "Инструмент", 1_900, 760, 470, 1.7),
    (13, "Лобзик 600W", "Инструмент", 6_400, 3_400, 160, 1.2),
    (14, "Уровень лазерный", "Инструмент", 7_300, 3_900, 140, 1.3),
    (15, "Мультиметр", "Инструмент", 4_200, 1_900, 260, 1.5),
    (16, "Увлажнитель Air", "Бытовая техника", 4_900, 2_400, 350, 1.6),
    (17, "Весы кухонные", "Бытовая техника", 1_700, 640, 720, 2.1),
    (18, "Термокружка", "Бытовая техника", 2_100, 830, 560, 2.0),
    (19, "Очиститель воздуха", "Бытовая техника", 15_900, 8_200, 120, 1.2),
    (20, "Сушилка для белья", "Бытовая техника", 2_600, 1_100, 310, 1.8),
    (21, "Картридж X1", "Расходники", 2_400, 1_180, 520, 2.3),
    (22, "Фильтр HEPA", "Расходники", 1_800, 720, 640, 2.5),
    (23, "Батарейки AA 8шт", "Расходники", 480, 160, 2_400, 3.1),
    (24, "Плёнка упаковочная", "Расходники", 320, 95, 1_900, 3.4),
]
SEASON = [0.88, 0.94, 1.05, 1.0, 0.98, 1.03, 0.92, 0.96, 1.07, 1.1, 1.14, 1.3]
RESET = "DELETE FROM products; DELETE FROM prices;"
INSERT_PRODUCT = "INSERT INTO products VALUES (?, ?, ?, ?, ?)"
INSERT_PRICE = "INSERT INTO prices VALUES (?, ?, ?, ?, ?)"


def discount_of(rnd: Random, month: str) -> float:
    promo = month[5:] in {"03", "06", "11"} and rnd.random() < 0.35
    return round(rnd.choice([0.1, 0.15, 0.2, 0.25]), 2) if promo else 0.0


def row_of(rnd: Random, product: tuple, index: int, month: str, discount: float) -> tuple:
    price = round(product[3] * rnd.uniform(0.94, 1.06) * (1 - discount), 2)
    return (product[0], month, price, round(product[5] * (price / product[3]) ** (-product[6]) * rnd.uniform(0.9, 1.1) * SEASON[index]), discount)


def price_row(rnd: Random, product: tuple, index: int, month: str) -> tuple:
    discount = discount_of(rnd, month)
    return row_of(rnd, product, index, month, discount)


def build(rnd: Random) -> list[tuple]:
    return [price_row(rnd, product, index, month) for product in PRODUCTS for index, month in enumerate(MONTHS)]


def payload(rnd: Random) -> list[tuple[str, list]]:
    return [(INSERT_PRODUCT, [row[:5] for row in PRODUCTS]), (INSERT_PRICE, build(rnd))]


def dump(conn, rnd: Random) -> None:
    for statement, rows in payload(rnd):
        conn.executemany(statement, rows)


def fill(conn, rnd: Random) -> None:
    conn.executescript(RESET)
    dump(conn, rnd)


def seed() -> None:
    with connect() as conn:
        fill(conn, Random(6407))
