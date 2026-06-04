import psycopg2
import xml.etree.ElementTree as ET
import time
import glob
import os
from typing import List, Tuple

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "database": "gar",
    "user": "gar_user",
    "password": "gar"
}

BASE_PATH = '/mnt/c/Users/lukin/Downloads/gar_xml/'
BATCH_SIZE = 100000


# ============================================================
# ПОДКЛЮЧЕНИЕ К БД
# ============================================================

def get_connection():
    """Создаёт соединение с PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)


def create_tables(cur):
    """Создаёт все необходимые таблицы"""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS addr_obj (
            id BIGINT PRIMARY KEY,
            objectid BIGINT,
            objectguid UUID,
            changeid BIGINT,
            name TEXT,
            typename TEXT,
            level INTEGER,
            opertypeid INTEGER,
            updatedate DATE,
            isactual BOOLEAN,
            isactive BOOLEAN,
            regioncode TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS houses (
            id BIGINT PRIMARY KEY,
            objectid BIGINT,
            houseguid UUID,
            housenum TEXT,
            addnum1 TEXT,
            addnum2 TEXT,
            housetype INTEGER,
            isactual BOOLEAN,
            isactive BOOLEAN
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS hierarchy (
            id BIGINT PRIMARY KEY,
            objectid BIGINT,
            parentobjid BIGINT,
            path TEXT,
            isactive BOOLEAN
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reestr_objects (
            objectid BIGINT PRIMARY KEY,
            objectguid UUID,
            changeid BIGINT,
            levelid INTEGER,
            updatedate DATE,
            isactive BOOLEAN
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS addr_obj_division (
            id BIGINT PRIMARY KEY,
            parentid BIGINT,
            childid BIGINT,
            changeid BIGINT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS mun_hierarchy (
            id BIGINT PRIMARY KEY,
            objectid BIGINT,
            parentobjid BIGINT,
            path TEXT,
            isactive BOOLEAN
        )
        """
    ]

    for sql in tables:
        cur.execute(sql)
    print("✅ Таблицы созданы/проверены")


# ============================================================
# ИМПОРТ ТАБЛИЦ
# ============================================================

def import_table(cur, region_path: str, pattern: str, insert_sql: str, extract_func, table_name: str) -> int:
    """
    Универсальная функция импорта XML в таблицу
    """
    files = glob.glob(os.path.join(region_path, pattern))
    if not files:
        return 0

    tree = ET.parse(files[0])
    root = tree.getroot()

    batch = []
    total = 0
    tag = pattern.replace('*.XML', '').replace('_', '')

    for element in root.findall(f'.//{tag}'):
        batch.append(extract_func(element))
        if len(batch) >= BATCH_SIZE:
            cur.executemany(insert_sql, batch)
            conn.commit()
            total += len(batch)
            print(f"    {table_name}: {total} записей", end='\r')
            batch = []

    if batch:
        cur.executemany(insert_sql, batch)
        conn.commit()
        total += len(batch)

    print(f"    {table_name}: {total} записей")
    return total


def extract_addr_obj(obj):
    return (
        obj.get('ID'), obj.get('OBJECTID'), obj.get('OBJECTGUID'),
        obj.get('CHANGEID'), obj.get('NAME'), obj.get('TYPENAME'),
        obj.get('LEVEL'), obj.get('OPERTYPEID'), obj.get('UPDATEDATE'),
        obj.get('ISACTUAL'), obj.get('ISACTIVE'), None  # regioncode будет позже
    )


def extract_house(house):
    return (
        house.get('ID'), house.get('OBJECTID'), house.get('OBJECTGUID'),
        house.get('HOUSENUM'), house.get('ADDNUM1'), house.get('ADDNUM2'),
        house.get('HOUSETYPE'), house.get('ISACTUAL'), house.get('ISACTIVE')
    )


def extract_hierarchy(item):
    return (
        item.get('ID'), item.get('OBJECTID'), item.get('PARENTOBJID'),
        item.get('PATH'), item.get('ISACTIVE')
    )


def extract_reestr(obj):
    return (
        obj.get('OBJECTID'), obj.get('OBJECTGUID'), obj.get('CHANGEID'),
        obj.get('LEVELID'), obj.get('UPDATEDATE'), obj.get('ISACTIVE')
    )


def extract_division(item):
    return (
        item.get('ID'), item.get('PARENTID'), item.get('CHILDID'), item.get('CHANGEID')
    )


def extract_mun(item):
    return (
        item.get('ID'), item.get('OBJECTID'), item.get('PARENTOBJID'),
        item.get('PATH'), item.get('ISACTIVE')
    )


# ============================================================
# ОСНОВНОЙ ПРОЦЕСС
# ============================================================

def main():
    conn = get_connection()
    cur = conn.cursor()

    create_tables(cur)
    conn.commit()

    regions = sorted([d for d in os.listdir(BASE_PATH)
                      if os.path.isdir(os.path.join(BASE_PATH, d)) and d.isdigit()])
    total_regions = len(regions)

    print(f"\n📁 Найдено регионов: {total_regions}")
    print("=" * 60)

    total_start = time.time()
    stats = []

    for idx, region in enumerate(regions, 1):
        region_start = time.time()
        region_path = os.path.join(BASE_PATH, region)

        print(f"\n[{idx}/{total_regions}] Регион {region} ({idx * 100 // total_regions}%)")
        print("-" * 40)

        # 1. addr_obj
        addr_count = import_table(
            cur, region_path, 'AS_ADDR_OBJ_*.XML',
            """INSERT INTO addr_obj (id, objectid, objectguid, changeid, name, typename, level, opertypeid, updatedate, isactual, isactive, regioncode)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""",
            extract_addr_obj, 'addr_obj'
        )

        # Обновляем regioncode для addr_obj
        if addr_count > 0:
            cur.execute("UPDATE addr_obj SET regioncode = %s WHERE regioncode IS NULL", (region,))

        # 2. houses
        houses_count = import_table(
            cur, region_path, 'AS_HOUSES_*.XML',
            """INSERT INTO houses (id, objectid, houseguid, housenum, addnum1, addnum2, housetype, isactual, isactive)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""",
            extract_house, 'houses'
        )

        # 3. hierarchy
        hier_count = import_table(
            cur, region_path, 'AS_ADM_HIERARCHY_*.XML',
            """INSERT INTO hierarchy (id, objectid, parentobjid, path, isactive)
               VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""",
            extract_hierarchy, 'hierarchy'
        )

        # 4. reestr_objects
        reestr_count = import_table(
            cur, region_path, 'AS_REESTR_OBJECTS_*.XML',
            """INSERT INTO reestr_objects (objectid, objectguid, changeid, levelid, updatedate, isactive)
               VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (objectid) DO NOTHING""",
            extract_reestr, 'reestr_objects'
        )

        # 5. addr_obj_division
        division_count = import_table(
            cur, region_path, 'AS_ADDR_OBJ_DIVISION_*.XML',
            """INSERT INTO addr_obj_division (id, parentid, childid, changeid)
               VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""",
            extract_division, 'addr_obj_division'
        )

        # 6. mun_hierarchy
        mun_count = import_table(
            cur, region_path, 'AS_MUN_HIERARCHY_*.XML',
            """INSERT INTO mun_hierarchy (id, objectid, parentobjid, path, isactive)
               VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""",
            extract_mun, 'mun_hierarchy'
        )

        region_time = time.time() - region_start
        stats.append(
            (region, addr_count, houses_count, hier_count, reestr_count, division_count, mun_count, region_time))

        print(f"  ⏱️ Время: {region_time:.2f} сек")

    # Финальный отчёт
    total_time = time.time() - total_start
    print("\n" + "=" * 60)
    print("✅ ИМПОРТ ЗАВЕРШЁН")
    print(f"⏱️ Общее время: {total_time:.2f} сек ({total_time / 60:.2f} мин)")
    print("\n📊 СТАТИСТИКА ПО РЕГИОНАМ:")
    print("-" * 80)
    print(
        f"{'Регион':<6} {'Addr':<10} {'Houses':<12} {'Hier':<12} {'Reestr':<12} {'Div':<10} {'Mun':<10} {'Время':<10}")
    print("-" * 80)

    totals = [0, 0, 0, 0, 0, 0]
    for reg, addr, houses_cnt, hier, reestr, div, mun, rtime in stats:
        print(f"{reg:<6} {addr:<10,} {houses_cnt:<12,} {hier:<12,} {reestr:<12,} {div:<10,} {mun:<10,} {rtime:<10.2f}")
        totals[0] += addr
        totals[1] += houses_cnt
        totals[2] += hier
        totals[3] += reestr
        totals[4] += div
        totals[5] += mun

    print("-" * 80)
    print(
        f"{'ИТОГО':<6} {totals[0]:<10,} {totals[1]:<12,} {totals[2]:<12,} {totals[3]:<12,} {totals[4]:<10,} {totals[5]:<10,} {total_time:<10.2f}")
    print("=" * 80)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()