from datetime import datetime
from collections import defaultdict
import clean
from tools.db import Database
from tools import services as ts


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


def main():
    database = "addresses.db"
    db = Database(database)

    rows = db.execute("""
        SELECT DISTINCT city_name
          FROM addresses
         WHERE region_name IS NULL
           AND region IS NULL
           AND city_name IS NOT NULL
         ORDER BY locality
    """)
    print(len(rows))

    cities = ts.json_open('cities.json')
    for row in rows:
        city_name = row['city_name']
        region_name, region_prefix = cities[city_name]
        if region_name and region_prefix:
            db.execute("""
                UPDATE addresses
                   SET region_name = :region_name,
                       region_prefix = :region_prefix
                 WHERE city_name IS NOT NULL
                   AND city_name = :city_name 
                   AND region_name IS NULL
            """, {
                'city_name': city_name,
                'region_name': region_name.upper(),
                'region_prefix': region_prefix.replace('.', '').upper()
            })


if __name__ == '__main__':
    main()