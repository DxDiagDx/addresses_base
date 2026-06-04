import sqlite3
from tools.db import Database
from tools import services as ts


def main():
    db = Database('addresses.db')

    # rows = db.execute("""
    #     SELECT DISTINCT locality
    #       FROM addresses
    #      WHERE provider = "dom-ru"
    #        AND gar IS NOT NULL
    # """)
    # localities = []
    # for row in rows:
    #     localities.append(row['locality'])
    # ts.json_save('dom-ru.json', sorted(localities))

    rows = ts.json_open('dom-ru.json')
    count = len(rows)
    for i, locality in enumerate(rows, start=1):
        if 100 < i:
            print(f"{i}/{count}. {locality}")
            items = db.execute("""
                        SELECT id 
                          FROM addresses 
                         WHERE locality = :locality
                           AND provider = "dom-ru"
                           AND gar IS NULL
                    """, {"locality": locality})
            ids = ','.join([str(item['id']) for item in items])
            if len(items) > 0:
                gar = db.execute(f"""
                    SELECT region_name, region_prefix,
                           district_name, district_prefix,
                           city_name, city_prefix,
                           locality_name, locality_prefix
                      FROM addresses
                     WHERE locality = :locality
                       AND provider = "dom-ru"
                       AND gar IS NOT NULL
                     LIMIT 1
                """, {"locality": locality})
                print(gar[0])

                db.execute(f"""
                    UPDATE addresses
                       SET region_name = :region_name,
                           region_prefix = :region_prefix,
                           district_name = :district_name,
                           district_prefix = :district_prefix,
                           city_name = :city_name,
                           city_prefix = :city_prefix
                     WHERE id IN ({ids})
                """, gar[0])
            print(f"Обновлено записей: {len(items)}, если 0 - обновлений не было.")

        # if i == 100:
        #     break


if __name__ == '__main__':
    main()