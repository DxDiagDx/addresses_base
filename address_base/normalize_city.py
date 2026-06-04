from tools.db import Database


def main():
    database = "addresses.db"
    db = Database(database)

    rows = db.execute("""
        SELECT locality,
               count(locality) AS count_locality,
               count(city_name) AS count_city_name,
               count(locality_name) AS count_locality_name
          FROM addresses 
         WHERE locality IS NOT NULL 
         GROUP BY locality
         ORDER BY locality
    """)
    print(len(rows))

    for i, row in enumerate(rows, start=1):
        locality = row['locality'].upper()
        count_locality = row['count_locality']
        count_city_name = row['count_city_name']
        count_locality_name = row['count_locality_name']
        if count_locality > count_city_name:
            if "Г " in locality or "Г. " in locality:
                print(row)



if __name__ == '__main__':
    main()