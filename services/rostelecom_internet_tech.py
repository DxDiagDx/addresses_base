import json
import sqlite3
from pathlib import Path
from glob import glob
from collections import defaultdict
from tools import services as ts
from tools.db import Database
from address_base import normalize_house


KEYS = {
    'Ростелеком__03': {
        'region': 'Область',
        'locality': 'Населенный пункт',
        'street': 'Улица',
        'house': 'Дом',
        'house_building': 'Корпус',
        'internet_tech': 'Вид оборудования'
    },
    'Ростелеком__АБ МиМО': {
        'region': 'регион',
        'locality': 'населенный пункт',
        'street': 'улица',
        'house': 'дом',
        'house_building': 'корп./стр./лит.',
        'fias': 'ФИАС',
        'internet_tech': 'технология'
    },
    'Ростелеком__АБ СЗ': {
        'region': 'Наименование региона',
        'locality': 'Наименование населенного пункта',
        'street': 'Наименование улицы',
        'house': 'дом',
        'house_building': 'корпус/литера',
        'fias': 'ФИАС',
        'internet_tech': 'Доступные технологии'
    },
    'Ростелеком__АБ Центр оптика': {
        'region': 'Область',
        'locality': 'Населенный пункт',
        'street': 'Улица',
        'house': 'Дом',
        'house_building': 'Корп.',
        'fias': 'ФИАС ',
        'full_address': 'Адрес ОРПОН',
        'internet_tech': 'Технология работы'
    }
}


def get_items_from_file(file_path, namespace):
    items = ts.csv_open(file_path)

    unigues = {}
    lines = defaultdict(list)
    for item in items:
        row = dict.fromkeys(namespace.keys())
        for name in namespace:
            row[name] = item[namespace[name]]
        internet_tech = row['internet_tech']
        if internet_tech:
            line = {}
            for key, value in row.items():
                if key != 'internet_tech':
                    line[key] = value.strip()

            unique = '~'.join([l.upper() for l in line.values()])
            unigues[unique] = line
            lines[unique].append(internet_tech)

    return lines


def get_variants(row, column_names, house_column_name):
    variants = []

    house_number_variants = None
    house_number = row[house_column_name]
    if house_number:
        if house_number.count('.') == 1:
            house_number_variants = normalize_house.get_variants_months(house_number)
        if house_number.count('.') == 2:
            house_number_variants = normalize_house.get_variants_date(house_number)

    if house_number_variants:
        for splitter_name in ['dot', 'defis', 'slash']:
            elements = []
            for column_name in column_names:
                if column_name == house_column_name:
                    value = house_number_variants[splitter_name]
                else:
                    value = row[column_name]

                if value:
                    elements.append(value)
                else:
                    elements.append('')
            unique_variant = '~'.join([e.upper() for e in elements])
            variants.append(unique_variant)

    else:
        elements = []
        for column_name in column_names:
            value = row[column_name]
            if value:
                elements.append(value)
            else:
                elements.append('')
        unique_variant = '~'.join([e.upper() for e in elements])
        variants.append(unique_variant)

    return variants


def get_rows_from_db(rows, lines, column_names):
    updates = []
    for row in rows:
        variants = get_variants(row, column_names, 'house')
        for unique_variant in variants:
            # print(unique_variant)
            values = lines.get(unique_variant)
            if values:
                us = unique_variant.split('~')

                file_address = dict.fromkeys(column_names)
                for i, u in enumerate(us):
                    file_address[column_names[i]] = u

                internet_tech = []
                for value in values:
                    if value not in internet_tech:
                        internet_tech.append(value)
                updates.append({
                    'id': row['id'],
                    'internet_tech': json.dumps(internet_tech, ensure_ascii=False),
                    'house': file_address['house'],
                    # 'house_block': file_address['house_block'],
                    # 'house_building': file_address['house_building']
                })

    return updates



def update_db(database, file_path, namespace):
    lines = get_items_from_file(file_path, namespace)
    print("Строк в файле:", len(lines))
    # for key, values in lines.items():
    #     print(key)
    #     break

    db = Database(database)
    rows = db.execute("""
        SELECT *
          FROM addresses
         WHERE filename == :filename
           AND internet_tech IS NULL

    """, {'filename': Path(file_path).name})

    column_names = list(namespace)[:-1]  # исключаем internet_tech
    updates = get_rows_from_db(rows, lines, column_names)

    print("Доступно для обновления в базе:", len(updates))
    # for update in updates:
    #     print(update)
    #     break

    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.executemany("""
                UPDATE addresses
                   SET internet_tech = :internet_tech,
                       house = :house
                 WHERE id = :id
            """, updates)

    print('Данные в базе обновлены.')


def main():
    database = '../address_base/2026-05-15_addresses.db'
    for file_path in glob('../files_csv/Ростелеком__*'):
        filename = Path(file_path).name
        # if 'Ростелеком__АБ Центр оптика 01.12.2025 фиас ПОН стройка нояб.csv' == filename:
        print(filename)
        for key, namespace in KEYS.items():
            if filename.startswith(key):
                # print(namespace)
                update_db(database, file_path, namespace)
        print()


if __name__ == '__main__':
    main()