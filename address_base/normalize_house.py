import re
import json
import sqlite3
from datetime import datetime
from collections import defaultdict
from tools.db import Database
from tools import services as ts


def get_variants_months(text):
    month_nums = {
        'янв': 1,
        'фев': 2,
        'мар': 3,
        "апр": 4,
        "май": 5,
        "июн": 6,
        "июл": 7,
        "авг": 8,
        "сен": 9,
        "окт": 10,
        "ноя": 11,
        "дек": 12,
    }
    months = list(month_nums)
    elements = []
    for m in months:
        if str(text).startswith(m):
            hs = text.split('.')
            house_block = int(hs[1])
            house_number = month_nums[hs[0]]
            elements.append(str(house_number))
            elements.append(str(house_block))
            break
        if str(text).endswith(m):
            hs = text.split('.')
            house_number = int(hs[0])
            house_block = month_nums[hs[1]]
            elements.append(str(house_number))
            elements.append(str(house_block))
            break
    variants = {
        'dot': '.'.join(elements),
        'defis': '-'.join(elements),
        'slash': '/'.join(elements)
    }
    return variants


def get_variants_date(text):
    items = text.split('.')
    elements = []
    for item in items:
        elements.append(str(int(item[-2:])))

    variants = {
        'dot': '.'.join(elements),
        'defis': '-'.join(elements),
        'slash': '/'.join(elements)
    }
    return variants


def replace_date_xlsx(text):
    if text.count('.') == 1:
        return get_variants_months(text)
    if text.count('.') == 2:
        return get_variants_date(text)
    return text


def split_house_building(house_str):
    """
    Разделяет номер дома и корпус, если:
    - слева от дроби: 1 или 2 цифры
    - справа от дроби: 1 или 2 цифры
    - ничего кроме цифр и дроби
    """
    # ^ - начало строки
    # \d{1,2} - одна или две цифры
    # / - дробь
    # \d{1,2} - одна или две цифры
    # $ - конец строки
    pattern = r'^(\d{1,2})/(\d{1,2})$'
    match = re.match(pattern, house_str.strip())
    if match:
        return match.group(1), match.group(2)
    return house_str, None


def main():
    database = "addresses.db"
    db = Database(database)

    rows = db.execute("""
        SELECT id,
               house_number
          FROM addresses
         WHERE house_number LIKE "%.%"
         ORDER BY house_number;
    """)

    count_rows = len(rows)
    print(count_rows)

    updates = []
    for i, row in enumerate(rows, start=1):
        house_number = row['house_number']
        variants = get_variants_months(house_number)
        if variants.get('slash'):
            print(f"{house_number:10} -> {variants['slash']}")
            updates.append({
                "id": row["id"],
                "house_number": variants['slash']
            })

        house, building = split_house_building(house_number)
        print(f"{house_number:30} -> {house:10} {building}")

    # with sqlite3.connect(database) as conn:
    #     cur = conn.cursor()
    #     cur.executemany("""
    #         UPDATE addresses
    #            SET house_number = :house_number
    #          WHERE id = :id
    #     """, updates)


if __name__ == '__main__':
    main()