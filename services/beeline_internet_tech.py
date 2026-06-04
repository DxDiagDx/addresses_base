import json
import sqlite3
from collections import defaultdict
from tools import services as ts
from tools.db import Database
from address_base import normalize_house


def get_items_from_file(filename):
    items = ts.csv_open(filename)

    unigues = {}
    lines = defaultdict(list)
    for item in items:
        # TODO оставть - нет колонки подключения
        internet_tech = None
        if internet_tech:
            line = {
                'fias': item['Код ФИАС'],
                'locality': item['Город'],
                'street': item['Улица'],
                'street_prefix': item['Тип улицы'],
                'house': item['Дом/Строение'],
                'house_building': item['Корпус'],
                'full_address': item['Адрес подключенного дома']
            }
            print(line.keys())
            exit()
            unique = '~'.join([l.upper() for l in line.values()])
            unigues[unique] = line
            lines[unique].append(internet_tech)

    return lines


def get_variants(row, column_names, house_column_name):
    variants = []

    house_number = row[house_column_name]
    house_number_variants = None
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


def get_rows_from_db(database, lines, provider_name):
    column_names = ['region', 'locality', 'street', 'house', 'house_block', 'house_building']

    db = Database(database)

    updates = []

    rows = db.execute("""
        SELECT *
          FROM addresses
         WHERE provider == :provider_name
           AND internet_tech IS NULL
    """, {'provider_name': provider_name})
    for row in rows:
        variants = get_variants(row, column_names, 'house')
        for unique_variant in variants:
            print(unique_variant)
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


def main():
    filename = f'../files_csv/Билайн.csv'
    lines = get_items_from_file(filename)
    for key, values in lines.items():
        print(key)
        break

    database = '2026-05-15_addresses.db'
    # updates = get_rows_from_db(database, lines, 'beeline')

    # print(len(updates))
    # for update in updates:
    #     print(update)
    #     break

    # with sqlite3.connect(database) as conn:
    #     cur = conn.cursor()
    #     cur.executemany("""
    #         UPDATE addresses
    #            SET internet_tech = :internet_tech,
    #                house = :house
    #          WHERE id = :id
    #     """, updates)
    #
    # print('Данные в базе обновлены.')


if __name__ == '__main__':
    main()