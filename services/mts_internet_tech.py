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
        internet_tech = None
        if item['Id'] == 'Интернет':
            internet_tech = item['ConnectionType']
        if internet_tech:
            line = {
                'region_name': item['RegionName'],
                'region_prefix': item['RegionPrefix'],
                'city_name': item['CityName'],
                'city_prefix': item['CityPrefix'],
                'district_name': item['DistrictName'],
                'district_prefix': item['DistrictPrefix'],
                'locality_name': item['LocalityName'],
                'locality_prefix': item['LocalityPrefix'],
                'street_name': item['StreetName'],
                'street_prefix': item['StreetPrefix'],
                'house_number': item['HouseNumber'],
                'house_block': item['HouseBlock'],
                'house_building': item['HouseBuilding'],
                'fias': item['FiasCode']
            }
            unique = '~'.join([l.upper() for l in line.values()])
            unigues[unique] = line
            lines[unique].append(internet_tech)

    return lines


def get_variants(row, column_names):
    variants = []

    house_number = row['house_number']
    house_number_variants = None
    if house_number.count('.') == 1:
        house_number_variants = normalize_house.get_variants_months(house_number)
    if house_number.count('.') == 2:
        house_number_variants = normalize_house.get_variants_date(house_number)

    if house_number_variants:
        for splitter_name in ['dot', 'defis', 'slash']:
            elements = []
            for column_name in column_names:
                if column_name == "house_number":
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
    column_names = [
        'region_name', 'region_prefix',
        'city_name', 'city_prefix',
        'district_name', 'district_prefix',
        'locality_name', 'locality_prefix',
        'street_name', 'street_prefix',
        'house_number', 'house_block', 'house_building',
        'fias'
    ]

    db = Database(database)

    updates = []

    rows = db.execute("""
        SELECT *
          FROM addresses
         WHERE provider == :provider_name
           AND internet_tech IS NULL
    """, {'provider_name': provider_name})
    for row in rows:
        variants = get_variants(row, column_names)
        for unique_variant in variants:
            print(unique_variant)
            values = lines.get(unique_variant)
            if values:
                us = unique_variant.split('~')
                internet_tech = []
                for value in values:
                    if value not in internet_tech:
                        internet_tech.append(value)
                updates.append({
                    'id': row['id'],
                    'internet_tech': json.dumps(internet_tech, ensure_ascii=False),
                    'house_number': us[-4],
                    'house_block': us[-3],
                    'house_building': us[-2]
                })

    return updates


def main():
    filename = f'../files_csv/МТС.csv'
    lines = get_items_from_file(filename)

    database = '2026-05-15_addresses.db'
    updates = get_rows_from_db(database, lines, 'mts')

    print(updates)

    # with sqlite3.connect(database) as conn:
    #     cur = conn.cursor()
    #     cur.executemany("""
    #         UPDATE addresses
    #            SET internet_tech = :internet_tech,
    #                house_number = :house_number,
    #                house_block = :house_block,
    #                house_building = :house_building
    #          WHERE id = :id
    #     """, updates)

    print('Данные в базе обновлены.')


if __name__ == '__main__':
    main()