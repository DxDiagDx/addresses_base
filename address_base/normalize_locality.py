import csv
import json
import sqlite3
from datetime import datetime
from collections import defaultdict
import clean
from tools.db import Database
from tools import services as ts
from address_base.PREFIXES import PREFIXES


def split_parenthases(text):
    """ Достаем текст из скобок """
    extract_text = clean.extract_parenthesis_content(text)
    text_clear = text.replace('(', '').replace(')', '')
    text_clear = text_clear.replace(extract_text, '')
    update = {
        'text': text,
        'extract_text': ts.trim(extract_text),
        'text_clear': ts.trim(text_clear)
    }
    return update


def manual():
    database = "addresses.db"
    db = Database(database)

    rows = db.execute("""
            SELECT DISTINCT
                   locality,
                   COUNT(*) as count_locality
              FROM addresses
             WHERE locality IS NOT NULL

               AND locality NOT LIKE "%,%"
               AND locality NOT LIKE "С/О%"

               AND locality_name IS NULL
               AND city_name IS NULL
             GROUP BY locality
             ORDER BY locality;
        """)

    # ts.json_save("localities.json", rows)
    # rows = ts.json_open("localities.json")
    count_rows = len(rows)
    print(count_rows)

    PREFIXES['locality'] += [
        'тер', 'спк', 'остров', 'тер.СОСН', 'сл', 'ж/р',
        'с/с', 'ст-ца', 'кв-л', 'гп', 'с/п', 'зона', 'п/о', 'г-к',
        'починок', 'гп.', 'автодорога', 'рабочий п.', 'рзд',
        'ДАЧНОЕ НЕКОММЕРЧЕСКОЕ ПАРТНЕРСТВО',
        'СЕЛЬСКАЯ АДМИНИСТРАЦИЯ',
        'СЕЛЬСОВЕТ',
        'СОТ',
        'МЕСТЕЧКО',
        'ДАЧНЫЙ ПОСЕЛОК',
        'ДЕРЕВНЯ',
        'поселение',
        'жилрайон', 'ЖИЛОЙ РАЙОН',
        'нст',
        'ГОРОДСКОЙ ПОСЕЛОК'
    ]

    for i, row in enumerate(rows, start=1):
        locality = row['locality']
        # print(f"{str(i):4}", f"{locality}")

        elements = {}
        elements['locality'] = clean.clean_name(locality.strip(), 'locality', PREFIXES['locality'])
        if elements['locality']:
            line = {
                'locality': locality,
                'locality_name': elements['locality']['name'],
                'locality_prefix': elements['locality']['prefix']
            }
            print(line)
            db.execute("""
                    UPDATE addresses
                       SET locality_name = :locality_name,
                           locality_prefix = :locality_prefix
                     WHERE locality = :locality
                """, line)

    print('Всё')


def gar_items_get(database, item):
    db = Database(database)
    rows = db.execute("""
        SELECT locality_name,
               locality_prefix
          FROM localities
         WHERE region_name = :region_name
    """, {'region_name': item['region_name']})
    for row in rows:
        locality_prefix = row['locality_prefix']
        if item['locality'].upper().strip() == row['locality_name'].upper():
            # print(row)
            return locality_prefix.upper()
    return None


def main():
    # manual()  # Ручная проверка

    database = "addresses.db"
    db = Database(database)

    rows = db.execute("""
        SELECT DISTINCT
               region_name,
               locality
          FROM addresses
         WHERE locality IS NOT NULL
           AND locality_name IS NULL
           AND city_name IS NULL

         ORDER BY locality;
    """)

    count_rows = len(rows)
    print(count_rows)

    for i, row in enumerate(rows, start=1):
        locality = row['locality']
        # print(f"{str(i):4}", f"{locality:30} =>")

        # if locality_name:
        #     line = {
        #         'region_name': row['region_name'],
        #         'locality': locality,
        #         'locality_name': locality,
        #         # 'locality_prefix': None
        #     }
        #     print(line)
        #     db.execute("""
        #         UPDATE addresses
        #            SET locality_name = :locality_name
        #          WHERE locality = :locality
        #            AND region_name = :region_name
        #     """, line)

    print('Всё')


if __name__ == '__main__':
    main()