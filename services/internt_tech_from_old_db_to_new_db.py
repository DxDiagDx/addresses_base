import sqlite3
from tools.db import Database


def main():
    old_database = '../address_base/2026-05-15_addresses.db'
    old_db = Database(old_database)
    rows = old_db.execute("""
        SELECT id, locality, house, internet_tech
          FROM addresses
    """)

    new_database = '../address_base/addresses.db'
    with sqlite3.connect(new_database) as conn:
        cur = conn.cursor()
        cur.executemany("""
            UPDATE addresses
               SET locality = :locality, 
                   house = :house, 
                   internet_tech = :internet_tech
             WHERE id = :id
        """, rows)

    print('Готово')


if __name__ == '__main__':
    main()