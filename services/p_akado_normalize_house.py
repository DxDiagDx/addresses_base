import csv
import sqlite3
from tools.db import Database


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
    return None


keys = {
    'АКАДО': {
        'fias': None,
        'region': 'Округ',
        'locality': 'Город',
        'street': 'Улица',
        'house': 'Дом',
        'building': 'Корпус',
        'building_block': 'Строение',
        'full_address': None,
        'internet_tech': 'Тип сети'
    }
}


def get_key(row, fields):
    items = []
    for field_name in fields:
        if row[field_name]:
            items.append(row[field_name])
    return ''.join(items)


def internet_tech_to_db(folder, filename, database):
    db = Database(database)
    # addresses_fields = ['filename', 'region', 'locality', 'street']
    # addresses_fields = ['filename', 'region', 'locality', 'street', 'house_building']
    addresses_fields = ['filename', 'region', 'locality', 'street', 'house_building', 'house_block']
    provider_fields = ['filename', 'region', 'locality', 'street', 'building', 'building_block', 'house']

    house_rows = db.execute("""
        SELECT * FROM addresses 
         WHERE internet_tech IS NULL
           AND house IS NOT NULL
           AND house <> ""
           AND filename = :filename
    """, {"filename": filename})
    print(len(house_rows))

    # for house_row in house_rows:
    #     print(f"{house_row['street']}, {house_row['house']}")

    current_rows = {}
    for row in house_rows:
        key = get_key(row, addresses_fields)
        house = row['house']
        if house.count('.'):
            house_variants = replace_date_xlsx(row['house'])
            for type_delimiter in ['dot', 'defis', 'slash']:
                house_variant = house_variants[type_delimiter]
                key_variant = key + house_variant
                current_rows[key_variant] = {'id': row['id'], 'house': house_variant}
        else:
            key_single = key + house
            current_rows[key_single] = {'id': row['id'], 'house': house}

    rows = []
    with (open(f'{folder}/{filename}', 'r', encoding='utf-8', newline='') as file):
        for key, namespace in keys.items():
            if filename.startswith(key):
                for i, item in enumerate(csv.DictReader(file, delimiter=',')):
                    internet_tech = item[namespace['internet_tech']] if namespace.get('internet_tech') else None
                    row = {
                        'filename': filename,
                        'fias': item[namespace['fias']] if namespace.get('fias') else None,
                        'region': item[namespace['region']] if namespace.get('region') else None,
                        'locality': item[namespace['locality']] if namespace.get('locality') else None,
                        'street': item[namespace['street']] if namespace.get('street') else None,
                        'house': item[namespace['house']] if namespace.get('house') else None,
                        'building': item[namespace['building']] if namespace.get('building') else None,
                        'building_block': item[namespace['building_block']] if namespace.get(
                            'building_block') else None,
                        'full_address': item[namespace['full_address']] if namespace.get('full_address') else None,
                        'internet_tech': None
                    }
                    key = get_key(row, provider_fields)
                    search_result = current_rows.get(key)
                    if search_result:
                        rows.append({
                            "id": search_result['id'],
                            "internet_tech": internet_tech,
                            "house": search_result['house']
                        })

    print('Данные сверены. Всего', len(rows))
    # print(rows)

    # with sqlite3.connect(database) as conn:
    #     cur = conn.cursor()
    #     cur.executemany("""
    #         UPDATE addresses
    #            SET internet_tech = :internet_tech,
    #                house = :house
    #          WHERE id = :id
    #     """, rows)
    #
    # print('База успешно обновлена!')


def main():
    filename = 'АКАДО АБ.csv'

    folder = '../files'
    database = '../address_base/addresses.db'

    # db = Database(database)
    # db.execute("ALTER TABLE addresses ADD COLUMN internet_tech TEXT;")

    internet_tech_to_db(folder, filename, database)



if __name__ == '__main__':
    main()