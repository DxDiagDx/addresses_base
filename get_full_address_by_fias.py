import re
import json
import sqlite3
import psycopg2
import psycopg2.extras

# Подключение к SQLite
sqlite_conn = sqlite3.connect('./providers/ufanet.db')
sqlite_cur = sqlite_conn.cursor()

# Получаем все непустые fias (GUID)
guid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

sqlite_cur.execute("""
    SELECT DISTINCT fias 
      FROM addresses 
     WHERE fias IS NOT NULL
       AND gar IS NULL
""")
guids = [row[0] for row in sqlite_cur.fetchall() if guid_pattern.match(str(row[0]))]

print(f"Всего: {len(guids)} валидных GUID")
# exit()
# Подключение к PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="gar",
    user="gar_user",
    password="gar"
)
pg_cur = pg_conn.cursor()

# Временная таблица без ограничений
pg_cur.execute("CREATE TEMP TABLE temp_guids (guid UUID)")

# Вставляем все GUID
psycopg2.extras.execute_values(
    pg_cur, 
    "INSERT INTO temp_guids (guid) VALUES %s",
    [(g,) for g in guids],
    page_size=10000
)
pg_conn.commit()

# Удаляем дубликаты, оставляя один
pg_cur.execute("""
    DELETE FROM temp_guids 
    WHERE ctid NOT IN (SELECT MIN(ctid) FROM temp_guids GROUP BY guid)
""")
pg_conn.commit()

# Теперь добавляем первичный ключ
pg_cur.execute("ALTER TABLE temp_guids ADD PRIMARY KEY (guid)")
pg_conn.commit()

print(f"GUID загружены в PostgreSQL")

# Получаем все адреса одним запросом
pg_cur.execute("""
WITH unique_path AS (
    SELECT DISTINCT ON (h.houseguid, a.name)
        h.houseguid,
        a.name,
        a.typename,
        h.housenum,
        h.addnum1,
        h.addnum2,
        MIN(p.pos) as pos
    FROM houses h
    JOIN hierarchy hi ON hi.objectid = h.objectid
    CROSS JOIN LATERAL unnest(string_to_array(hi.path, '.')::BIGINT[]) WITH ORDINALITY AS p(objid, pos)
    JOIN addr_obj a ON a.objectid = p.objid AND a.isactive = true
    WHERE h.houseguid IN (SELECT guid FROM temp_guids)
    GROUP BY h.houseguid, a.name, a.typename, h.housenum, h.addnum1, h.addnum2
)
SELECT 
    houseguid,
    jsonb_agg(jsonb_build_object('typename', typename, 'name', name) ORDER BY pos) ||
    jsonb_build_object(
        'typename', 'д',
        'name', housenum,
        'addnum1', addnum1,
        'addnum2', addnum2
    ) as address_parts
FROM unique_path
GROUP BY houseguid, housenum, addnum1, addnum2;
""")

# Сохраняем результат в словарь
result = {}
for row in pg_cur.fetchall():
    result[row[0]] = row[1]  # row[1] уже JSONB, но PostgreSQL вернёт его как строку
    # print(f"{row[0]}: {row[1]}")
print(f"Найдено адресов: {len(result)}")

# Обновляем SQLite — сохраняем JSON в колонку gar
# Создаём временную таблицу в SQLite
sqlite_cur.execute("CREATE TEMP TABLE updates (fias TEXT PRIMARY KEY, gar TEXT)")

# Загружаем все обновления во временную таблицу
sqlite_cur.executemany("INSERT INTO updates (fias, gar) VALUES (?, ?)", 
                       [(guid, json.dumps(addr) if isinstance(addr, (list, dict)) else addr) 
                        for guid, addr in result.items()])
sqlite_conn.commit()

# Массовое обновление
sqlite_cur.execute("""
    UPDATE addresses SET gar = (
        SELECT gar FROM updates WHERE updates.fias = addresses.fias
    ) WHERE fias IN (SELECT fias FROM updates)
""")
sqlite_conn.commit()

# Удаляем временную таблицу
sqlite_cur.execute("DROP TABLE updates")

print("Готово!")

sqlite_conn.close()
pg_conn.close()