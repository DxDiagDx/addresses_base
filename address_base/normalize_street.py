import json
from datetime import datetime
from collections import defaultdict
import clean
from tools.db import Database
from tools import services as ts


def main():
    database = "addresses.db"
    db = Database(database)

    rows = db.execute("""
        SELECT DISTINCT street
          FROM addresses
         WHERE region_name LIKE "МОСК%"
           AND street IS NOT NULL
           AND street_name IS NULL
           AND street <> "-- НЕ ОПРЕДЕЛЕНА --"
           AND locality_name IS NULL
         ORDER BY street
    """)
    print(len(rows))

    for i, row in enumerate(rows, start=1):
        street = row['street']
        print(street)

        # gar = db.execute("""
        #     SELECT gar
        #       FROM addresses
        #      WHERE region_name LIKE "МОСК%"
        #        AND street = :street
        #        AND gar IS NOT NULL
        # """, row)
        # if gar:
        #     street_gar = json.loads(gar[0]['gar'])[-2]
        #     print(f"{street:30} => {street_gar}")
            # if street_gar['typename'] in ['ал.', 'просек', 'тер.', 'г-к', 'тер', 'кв-л', 'пл', 'ул']:
            #     # print(i, street, value, sep='\\')
            #     columns = {
            #         'street': street,
            #         'street_name': street_gar['name'],
            #         'street_prefix': street_gar['typename'],
            #     }
            #     db.execute("""
            #         UPDATE addresses
            #            SET street_name = :street_name,
            #                street_prefix = :street_prefix
            #          WHERE street = :street
            #     """, columns)
            #
            #     print(columns)

        # value = clean.clean_name(street, 'locality', ['микрорайон'])
        # if value:
        #     # print(i, street, value, sep='\\')
        #     columns = {
        #         'street': street,
        #         'locality_name': value['name'],
        #         'locality_prefix': 'мкр',
        #     }
        #     db.execute("""
        #         UPDATE addresses
        #            SET locality_name = :locality_name,
        #                locality_prefix = :locality_prefix
        #          WHERE street = :street
        #            AND region_name LIKE "МОСК%"
        #            AND street IS NOT NULL
        #            AND street_name IS NULL
        #            AND street <> "-- НЕ ОПРЕДЕЛЕНА --"
        #            AND street LIKE "% Микрорайон"
        #     """, columns)
        #     print(i, value)



if __name__ == '__main__':
    main()