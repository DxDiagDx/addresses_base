import csv
import sqlite3
from services import p_akado_normalize_house
from tools.db import Database


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


def insert_db(folder, filename, database):
    db = Database(database)

    rows = []
    with open(f'{folder}/{filename}', 'r', encoding='cp1251', newline='') as file:
        for key, namespace in keys.items():
            if filename.startswith(key):
                for i, item in enumerate(csv.DictReader(file, delimiter=';')):
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
                    }
                    rows.append(row)

    db.create_table('addresses', rows[0])
    db.insert('addresses', rows)

    print('Всего:', len(rows))


def internet_tech_to_db(folder, filename, database):
    db = Database(database)

    house_rows = db.execute("""
        SELECT * FROM addresses 
         WHERE internet_tech IS NULL
           AND house IS NOT NULL
           AND house <> ""
           AND filename = :filename
    """, {"filename": filename})

    current_rows = {}
    for row in house_rows:
        house = row['house']
        if house.count('.'):
            house_variants = normalize_house.replace_date_xlsx(row['house'])
            for type_delimiter in ['dot', 'defis', 'slash']:
                house_variant = house_variants[type_delimiter]
                key = ''.join([
                    row['filename'], row['region'], row['locality'], row['street'],
                    house_variant, row['building'], row['building_block']
                ])
                current_rows[key] = {'id': row['id'], 'house': house_variant}
        else:
            key = ''.join([
                row['filename'], row['region'], row['locality'], row['street'],
                house, row['building'], row['building_block']
            ])
            current_rows[key] = {'id': row['id'], 'house': house}

    rows = []
    with open(f'{folder}/{filename}', 'r', encoding='utf-8', newline='') as file:
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
                    key = ''.join([
                        row['filename'], row['region'], row['locality'], row['street'],
                        row['house'], row['building'], row['building_block']
                    ])
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
    database = '../providers/akado.db'
    # database = '../address_base/addresses.db'

    # # первоначальное заполнение базы данных
    # insert_db(folder, filename, database)

    # db = Database(database)
    # db.execute("ALTER TABLE addresses ADD COLUMN internet_tech TEXT;")

    internet_tech_to_db(folder, filename, database)



if __name__ == '__main__':
    main()