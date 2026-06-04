import sqlite3
import psycopg2

REGION_CODES = {
    "АДЫГЕЯ": "01",
    "АЛТАЙ": "04",
    "АЛТАЙСКИЙ": "22",
    "АМУРСКАЯ": "28",
    "АРХАНГЕЛЬСКАЯ": "29",
    "АСТРАХАНСКАЯ": "30",
    "БАШКОРТОСТАН": "02",
    "БЕЛГОРОДСКАЯ": "31",
    "БРЯНСКАЯ": "32",
    "БУРЯТИЯ": "03",
    "ВЛАДИМИРСКАЯ": "33",
    "ВОЛГОГРАДСКАЯ": "34",
    "ВОЛОГОДСКАЯ": "35",
    "ВОРОНЕЖСКАЯ": "36",
    "ДАГЕСТАН": "05",
    "ЕВРЕЙСКАЯ": "79",
    "ЗАБАЙКАЛЬСКИЙ": "75",
    "ИВАНОВСКАЯ": "37",
    "ИНГУШЕТИЯ": "06",
    "ИРКУТСКАЯ": "38",
    "КАБАРДИНО-БАЛКАРСКАЯ": "07",
    "КАЛИНИНГРАДСКАЯ": "39",
    "КАЛМЫКИЯ": "08",
    "КАЛУЖСКАЯ": "40",
    "КАМЧАТСКИЙ": "41",
    "КАРАЧАЕВО-ЧЕРКЕССКАЯ": "09",
    "КАРЕЛИЯ": "10",
    "КЕМЕРОВСКАЯ": "42",
    "КЕМЕРОВСКАЯ ОБЛАСТЬ - КУЗБАСС": "42",
    "КИРОВСКАЯ": "43",
    "КОМИ": "11",
    "КОСТРОМСКАЯ": "44",
    "КРАСНОДАРСКИЙ": "23",
    "КРАСНОЯРСКИЙ": "24",
    "КРЫМ": "91",
    "КУРГАНСКАЯ": "45",
    "КУРСКАЯ": "46",
    "ЛЕНИНГРАДСКАЯ": "47",
    "ЛИПЕЦКАЯ": "48",
    "МАГАДАНСКАЯ": "49",
    "МАРИЙ ЭЛ": "12",
    "МОРДОВИЯ": "13",
    "МОСКВА": "77",
    "МОСКОВСКАЯ": "50",
    "МУРМАНСКАЯ": "51",
    "НИЖЕГОРОДСКАЯ": "52",
    "НОВГОРОДСКАЯ": "53",
    "НОВОСИБИРСКАЯ": "54",
    "НОВОСИБИРСК": "54",
    "ОМСКАЯ": "55",
    "ОРЕНБУРГСКАЯ": "56",
    "ОРЛОВСКАЯ": "57",
    "ПЕНЗЕНСКАЯ": "58",
    "ПЕРМСКИЙ": "59",
    "ПРИМОРСКИЙ": "25",
    "ПСКОВСКАЯ": "60",
    "РОСТОВСКАЯ": "61",
    "РЯЗАНСКАЯ": "62",
    "САМАРСКАЯ": "63",
    "САНКТ-ПЕТЕРБУРГ": "78",
    "САРАТОВСКАЯ": "64",
    "САХА (ЯКУТИЯ)": "14",
    "САХАЛИНСКАЯ": "65",
    "СВЕРДЛОВСКАЯ": "66",
    "СЕВЕРНАЯ ОСЕТИЯ - АЛАНИЯ": "15",
    "СМОЛЕНСКАЯ": "67",
    "СТАВРОПОЛЬСКИЙ": "26",
    "ТАМБОВСКАЯ": "68",
    "ТАТАРСТАН": "16",
    "ТВЕРСКАЯ": "69",
    "ТОМСКАЯ": "70",
    "ТУЛЬСКАЯ": "71",
    "ТЫВА": "17",
    "ТЮМЕНСКАЯ": "72",
    "УДМУРТСКАЯ": "18",
    "УЛЬЯНОВСКАЯ": "73",
    "ХАБАРОВСКИЙ": "27",
    "ХАКАСИЯ": "19",
    "ХАНТЫ-МАНСИЙСКИЙ АВТОНОМНЫЙ ОКРУГ - ЮГРА": "86",
    "ЧЕЛЯБИНСКАЯ": "74",
    "ЧУВАШСКАЯ РЕСПУБЛИКА - ЧУВАШИЯ": "21",
    "ЧУКОТСКИЙ": "87",
    "ЯМАЛО-НЕНЕЦКИЙ": "89",
    "ЯРОСЛАВСКАЯ": "76",
}

pg_conn = psycopg2.connect(
    host="localhost",
    database="gar",
    user="gar_user",
    password="gar"
)
pg_cur = pg_conn.cursor()

sqlite_conn = sqlite3.connect('localities.sqlite3')
sqlite_cur = sqlite_conn.cursor()

sqlite_cur.execute("""
    CREATE TABLE IF NOT EXISTS localities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region_name TEXT,
        region_code TEXT,
        locality_name TEXT,
        locality_prefix TEXT,
        UNIQUE(region_name, locality_name)
    )
""")

sqlite_cur.execute("DELETE FROM localities")
sqlite_conn.commit()

for region_name, region_code in REGION_CODES.items():
    print(f"Обработка: {region_name} ({region_code})")

    pg_cur.execute("""
        SELECT DISTINCT name, typename
        FROM addr_obj
        WHERE regioncode = %s
          AND level IN (4, 5, 6)
          AND isactive = true
        ORDER BY name
    """, (region_code,))

    localities = pg_cur.fetchall()
    print(f"  Добавлено {len(localities)} населённых пунктов")

    for locality_name, locality_prefix in localities:
        sqlite_cur.execute("""
            INSERT OR IGNORE INTO localities (region_name, region_code, locality_name, locality_prefix)
            VALUES (?, ?, ?, ?)
        """, (region_name, region_code, locality_name, locality_prefix))

    sqlite_conn.commit()

print("Готово!")
pg_cur.close()
pg_conn.close()
sqlite_conn.close()