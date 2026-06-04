import csv
from collections import defaultdict
from tools.db import Database
from address_base import clean
from tools import services as ts


def to_db(database):
    filename = 'Уфанет__Отчет по адресам_выгрузка от 29.12_за период 29.10-29.12.2025.csv'
    keys = {
        'Уфанет__': {
            'fias': None,
            'region': 'Субъект',
            'locality': 'Город',
            'street': 'Улица',
            'house': 'Дом',
            'building': None
        }
    }
    db = Database(database)

    rows = []
    folder = 'files'

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
                        'full_address': item[namespace['full_address']] if namespace.get('full_address') else None,
                    }
                    rows.append(row)

    db.create_table('addresses', rows[0])
    db.insert('addresses', rows)

    print('Всего:', len(rows))


def get_region(database):
    db = Database(database)
    rows = db.execute("""
        SELECT DISTINCT region
          FROM addresses
         WHERE region_name IS NULL
         ORDER BY region
    """)
    return rows


def get_locality(database):
    db = Database(database)
    rows = db.execute("""
        SELECT DISTINCT locality
          FROM addresses
         WHERE locality
           AND NOT (city_name NOT NULL 
                 OR locality_name NOT NULL 
                 OR district_name NOT NULL)
    """)
    return rows


def get_street(database):
    db = Database(database)
    rows = db.execute("""
        SELECT DISTINCT street
          FROM addresses
         WHERE street_name IS NULL
           AND substr(street, 1, 2) NOT IN (
                   'П.',
                   'С.',
                   'Х.', 
                   'Г.', 
                   'Д.', 
                   'М.'
               )
         ORDER BY street
    """)
    return rows


def update_db(database, column, update_rows):
    db = Database(database)
    for i, row in enumerate(update_rows, start=1):
        print()
        print(f"{i}/{str(len(update_rows)):6}", row[column])
        elements = {}
        for col in row['columns']:
            for key, value in col.items():
                elements[key] = value

        items = []
        for col_name, col_value in elements.items():
            text = f'{col_name} = "{col_value}"'
            items.append(text)

        fields = ', '.join(items)
        db.execute(f"""
            UPDATE addresses
               SET {fields}
             WHERE {column} = '{row[column]}'
        """)

        print(row)
        # break


def get_update_rows(rows, column):
    loss_rows = []
    update_rows = []
    for row in rows:
        text = row[column]
        # count = len(locality.split(','))
        # if count == 2:
        columns = []
        items = clean.clean_split_comma(text)
        for item in items:
            result = clean.clean_names(item)
            if result:
                col_name = result['type']
                columns.append({
                    f"{col_name}_name": result['name'],
                    f"{col_name}_prefix": result['prefix']
                })
        if columns:
            update_row = {
                f"{column}": text,
                "columns": columns
            }
            update_rows.append(update_row)
        else:
            print("Не найдено:", text)
            loss_rows.append(text.strip())

    return update_rows, loss_rows


def main():
    database = 'ufanet.db'

    region_rows = get_region(database)
    update_rows, loss_rows = get_update_rows(region_rows, 'region')
    print("\n", "Обновляем базу данных:", "\n")
    update_db(database, 'region', update_rows)

    # locality_rows = get_locality(database)
    # update_rows, loss_rows = get_update_rows(locality_rows, 'locality')
    # print("\n", "Обновляем базу данных:", "\n")
    # update_db(database, 'locality', update_rows)

    # street_rows = get_street(database)
    # update_rows, loss_rows = get_update_rows(street_rows, 'street')
    # print("\n", "Обновляем базу данных:", "\n")
    # update_db(database, 'street', update_rows)


if __name__ == '__main__':
    main()