import re
import csv
from services.clean import clean_name
from services.clean import stop_words_region
from services.clean import stop_words_locality
from tools.db import Database


def filename_to_db(filename, database):
    db = Database(database)

    keys = {
        'Дом ру': {
            'fias': 'Код ФИАС',
            'region': None,
            'locality': 'Нас. пункт',
            'street': 'Название улицы',
            'house': 'Дом',
            'building': 'Корпус'
        }
    }

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

    db.insert('addresses', rows)

    print('Всего:', len(rows))


def get_region(locality):
    match = re.search(r'\(([^)]+)\)$', locality)
    if match:
        region = match.group(1).strip()
        # Очищаем locality от скобок и лишних пробелов
        clean_locality = re.sub(r'\s*\([^)]+\)$', '', locality).strip()
        return region, clean_locality
    return None


def normalize_locality(database):
    db = Database(database)
    rows = db.execute("""
        SELECT DISTINCT locality 
          FROM addresses 
         WHERE gar IS NULL
           AND locality LIKE '%,%(%)'
    """)
    stop_words = set()
    for row in rows:
        locality = row['locality']
        region, clean_locality = get_region(locality)
        if region:
            region_name, region_prefix = clean_name(region, stop_words_region)
        if clean_locality:
            cls = clean_locality.split(',')
            for cl in cls:
                if cl:
                    result, stop_word = clean_name(cl, stop_words_locality)
                    if stop_word:
                        stop_words.add(stop_word)

    for sw in sorted(stop_words):
        print(sw)
        # print(f"{locality:70} -> {clean_locality:50} -> {region}")


def main():
    filename = 'Дом ру.csv'
    database = '../providers/dom-ru.db'

    # 1. Импортируем записи из файла
    # filename_to_db(filename, database)

    # 2. Нормализуем locality
    normalize_locality(database)


if __name__ == '__main__':
    main()