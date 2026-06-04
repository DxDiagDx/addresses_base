import csv
import json
import sqlite3
from openpyxl import Workbook


def dict_factory(cur, row):
    fields = [column[0] for column in cur.description]
    return {key: value for key, value in zip(fields, row)}


def get_internet_tech(internet_tech):
    client, home = None, None

    if not internet_tech:
        return client, home

    if "Технология подключения клиента" in internet_tech:
        items = json.loads(internet_tech)
        client = items[0]['Технология подключения клиента']
        home = items[0]['Технология подключения дома']
        return client, home

    try:
        client = ','.join(json.loads(internet_tech))
        return client, home
    except:
        client = ','.join([internet_tech])
        return client, home


def get_provider(text):
    providers = {
        "akado": "Акадо",
        "beeline": "Билайн",
        "dom-ru": "Дом Ру",
        "megafon": "Мегафон",
        "mts": "МТС",
        "rostelecom": "Ростелеком",
        "ttk": "ТТК",
        "ufanet": "Уфанет"
    }
    if providers.get(text):
        return providers[text]
    return text


def get_rows(database, region_name):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.row_factory = dict_factory
        cur.execute("""
            SELECT provider,
                   region,
                   region_name, region_prefix,
                   district,
                   district_name, district_prefix,
                   city,
                   city_name, city_prefix,
                   locality,
                   locality_name, locality_prefix,
                   street,
                   street_name, street_prefix,
                   house,
                   house_number,
                   house_building,
                   house_block,
                   internet_tech
              FROM addresses
             WHERE region_prefix IS NOT NULL AND region_name IS NOT NULL
               AND region_name LIKE :region_name
             ORDER BY 
                   region_name,
                   city_name,
                   district_name,
                   locality_name,
                   street_name,
                   house_number,
                   house_building,
                   house_block
        """, {'region_name': region_name})
        rows = cur.fetchall()
        return rows


def get_lines(rows):
    lines = []
    for row in rows:
        fields = []
        for key in ['region', 'district', 'city', 'locality', 'street', 'house']:
            if row[key]:
                fields.append(row[key])

        tech_client, tech_home = get_internet_tech(row['internet_tech'])

        full_address = ', '.join(fields)
        line = {
            'Провайдер': get_provider(row['provider']),
            'Регион': row['region_name'],
            'Регион тип': row['region_prefix'],
            'Район': row['district_name'],
            'Район тип': row['district_prefix'],
            'Город': row['city_name'],
            'Город тип': row['city_prefix'],
            'Нас.пункт': row['locality_name'],
            'Нас.пункт тип': row['locality_prefix'],
            'Улица': row['street_name'],
            'Улица тип': row['street_prefix'],
            'Дом': row['house_number'],
            'Корпус': row['house_building'],
            'Строение': row['house_block'],
            'Технология клиента': tech_client,
            'Технология дома': tech_home,
            'Исходный адрес': full_address
        }
        # print(line)
        lines.append(line)
    return lines


def export_csv(folder, region_name, lines):
    filename_out = f'{folder}/{region_name}.csv'
    with open(filename_out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(lines[0]))
        writer.writeheader()
        writer.writerows(lines)


def export_xlsx(folder, region_name, lines):
    if not lines:
        return

    wb = Workbook()
    ws = wb.active

    headers = list(lines[0].keys())
    ws.append(headers)

    for row in lines:
        ws.append([row.get(h, '') for h in headers])

    filename_out = f'{folder}/{region_name}.xlsx'
    wb.save(filename_out)


def main():
    database = 'addresses.db'

    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.row_factory = dict_factory
        cur.execute("""
            SELECT DISTINCT region_name 
              FROM addresses
             WHERE region_name NOT IN (
                'МОСКОВСКАЯ', 'МОСКВА',
                'ЛЕНИНГРАДСКАЯ', 'САНКТ-ПЕТЕРБУРГ'
             )
        """)
        for row in cur.fetchall():
            region_name = row['region_name']

            rows = get_rows(database, region_name)
            print(f"Экспорт {region_name}. {len(rows)} записей")

            lines = get_lines(rows=rows)
            export_xlsx('export_files', region_name, lines)


    # Отдельно выгружаем МОСКВУ
    print("Выгружаем МОСКВУ")
    rows = []
    for region_name in ['МОСКОВСКАЯ', 'МОСКВА']:
        for row in get_rows(database, region_name):
            rows.append(row)
    lines = get_lines(rows=rows)
    export_xlsx('export_files', "МОСКВА", lines)

    # Отдельно выгружаем САНКТ-ПЕТЕРБУРГ
    print("Выгружаем САНКТ-ПЕТЕРБУРГ")
    rows = []
    for region_name in ['ЛЕНИНГРАДСКАЯ', 'САНКТ-ПЕТЕРБУРГ']:
        for row in get_rows(database, region_name):
            rows.append(row)
    lines = get_lines(rows=rows)
    export_xlsx('export_files', "САНКТ-ПЕТЕРБУРГ", lines)


if __name__ == '__main__':
    main()
