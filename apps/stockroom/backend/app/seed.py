from __future__ import annotations

from random import Random

from .db import connect

MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]
WAREHOUSES = ["Москва", "Санкт-Петербург", "Екатеринбург"]
CATALOG = {
    "Электроника": [("Наушники Pro", 8900, 4300), ("Колонка Mini", 5400, 2600), ("Пауэрбанк 20K", 3200, 1500), ("Роутер AX", 6100, 2900), ("Смарт-часы S2", 12400, 6100)],
    "Аксессуары": [("Чехол Ultra", 1200, 380), ("Кабель USB-C 2м", 790, 220), ("Держатель авто", 1450, 520), ("Стекло защитное", 590, 140), ("Сумка для ноутбука", 3400, 1400)],
    "Инструмент": [("Шуруповёрт 18V", 9800, 5200), ("Набор бит 40шт", 1900, 760), ("Лобзик 600W", 6400, 3400), ("Уровень лазерный", 7300, 3900), ("Мультиметр", 4200, 1900)],
    "Бытовое": [("Увлажнитель Air", 4900, 2400), ("Весы кухонные", 1700, 640), ("Термокружка", 2100, 830), ("Сушилка для белья", 2600, 1100), ("Очиститель воздуха", 15900, 8200)],
    "Расходники": [("Картридж X1", 2400, 1180), ("Фильтр HEPA", 1800, 720), ("Мешок для пылесоса", 640, 180), ("Батарейки AA 8шт", 480, 160), ("Плёнка упаковочная", 320, 95)],
}
RESET = "DELETE FROM sku; DELETE FROM stock; DELETE FROM movements;"
INSERT_SKU = "INSERT INTO sku VALUES (?, ?, ?, ?, ?)"
INSERT_STOCK = "INSERT INTO stock VALUES (?, ?, ?)"
INSERT_MOVEMENTS = "INSERT INTO movements VALUES (?, ?, ?, ?)"


def sku_rows() -> list[tuple]:
    items = [(name, category, price, cost) for category, goods in CATALOG.items() for name, price, cost in goods]
    return [(index + 1, *item) for index, item in enumerate(items)]


def movement_rows(rnd: Random) -> list[tuple]:
    dead = {sku_id for sku_id, *_ in sku_rows() if rnd.random() < 0.16}
    return [(sku_id, month, rnd.randint(20, 180), 0 if sku_id in dead else rnd.randint(15, 220)) for sku_id, *_ in sku_rows() for month in MONTHS]


def stock_rows(rnd: Random) -> list[tuple]:
    return [(sku_id, warehouse, rnd.randint(0, 80)) for sku_id, *_ in sku_rows() for warehouse in WAREHOUSES]


def payload(rnd: Random) -> list[tuple[str, list]]:
    return [(INSERT_SKU, sku_rows()), (INSERT_STOCK, stock_rows(rnd)), (INSERT_MOVEMENTS, movement_rows(rnd))]


def dump(conn, rnd: Random) -> None:
    for statement, rows in payload(rnd):
        conn.executemany(statement, rows)


def fill(conn, rnd: Random) -> None:
    conn.executescript(RESET)
    dump(conn, rnd)


def seed() -> None:
    with connect() as conn:
        fill(conn, Random(4821))
