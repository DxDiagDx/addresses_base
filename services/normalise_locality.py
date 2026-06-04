import datetime
import sqlite3
import time

from tools.db import Database
from address_base import clean


def prepare_rows(rows, stop_words):
    new_rows = []
    for row in rows:
        text = row['locality'].strip()
        if text:
            name, prefix = clean.clean_name(text, stop_words)
            name = name.upper()
            if prefix:
                prefix = prefix.upper().replace('.', '')
            else:
                # print(f"{text:30} -> {name:30} -> {prefix}")
                prefix = None

            print(f"{text:30} -> {name:30} -> {prefix}")
            new_rows.append({
                'locality': row['locality'],
                'LocalityName': name,
                'LocalityPrefix': prefix
            })
    return new_rows


def update_db(database, new_rows):
    start = datetime.datetime.now()
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.executemany("""
            UPDATE addresses
               SET LocalityName = :LocalityName,
                   LocalityPrefix = :LocalityPrefix
             WHERE locality = :locality
        """, new_rows)

    end = datetime.datetime.now()

    print(f'Готово, время вставки {end - start} сек.')
    return len(new_rows)


def main():
    database = './providers/ufanet.db'

    words = [
        'аал', 'аул',
        'г', 'гп',
        'д', 'дп', 'днп',
        'ж/д_ст', 'жилрайон',
        'кв-л', 'кп',
        'нп',
        'п', 'пгт', 'п/о', 'п/ст',
        'рзд', 'рп', 'р.п',
        'с', 'ст', 'с/о', 'снт', 'сл', 'ст_ж/д', 'сно', 'спк', 'днт',
        'тер', 'тсн',
        'мкр',
        'у', 'улус',
        'х', 'хутор',
        'поселок',
    ]
    stop_words = clean.prepare_stop_words(words)

    db = Database(database)
    # rows = db.execute(f"""
    #     SELECT DISTINCT locality
    #       FROM addresses
    #      WHERE locality IS NOT NULL
    #        AND LocalityName IS NULL
    #      ORDER BY locality
    # """)
    rows = db.execute(f"""
        SELECT DISTINCT locality
          FROM addresses
         WHERE locality LIKE '%,%'
    """)
    print(f'Найдено {len(rows)} записей')
    print()

    new_rows = prepare_rows(rows, stop_words)
    exit()

    total = len(new_rows)

    start = 0
    offset = 100
    while True:
        update_rows = new_rows[start:start+offset]
        if not update_rows:
            break

        uniques = set([item['locality'] for item in update_rows])

        count_rows = db.execute(f"""
            SELECT count(locality) AS count
              FROM addresses
             WHERE locality IN {tuple(uniques)}
        """)
        if not count_rows:
            break

        print(f'Обновляем в базе {count_rows[0]["count"]} записей')

        update_db(database, update_rows)

        total -= offset
        print('Выполнено', round(100 - total * 100 / len(new_rows), 2), '%')
        print('Пауза 3 секунды, чтобы остановить скрипт.')
        time.sleep(3)

        start += offset


if __name__ == '__main__':
    main()