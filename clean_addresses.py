import sqlite3
import re

# Путь к вашей базе
DB_PATH = '/mnt/c/Users/lukin/_Projects/addresses_base/providers/rostelecom.db'

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    
    # Отключаем синхронизацию для скорости
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    
    print("1. Начало очистки данных...")
    
    # Очистка колонок от '#Н/Д'
    for col in ['fias', 'region', 'locality', 'street', 'house', 'building', 'full_address']:
        cursor.execute(f"UPDATE addresses SET {col} = NULL WHERE {col} = '#Н/Д' OR {col} = ''")
        print(f"   Очищена колонка: {col}")
    
    # Тримминг и UPPER
    for col in ['region', 'locality', 'street', 'house', 'building']:
        cursor.execute(f"UPDATE addresses SET {col} = TRIM(UPPER({col})) WHERE {col} IS NOT NULL")
        print(f"   Нормализована колонка: {col}")
    
    # Очистка FIAS
    cursor.execute("UPDATE addresses SET fias = TRIM(REPLACE(REPLACE(fias, '\\n', ''), '\\r', '')) WHERE fias IS NOT NULL")
    
    # Удаление префиксов из locality
    for prefix in ['Г.', 'С.', 'Д.', 'РП.', 'ПГТ.', 'П.']:
        cursor.execute(f"UPDATE addresses SET locality = TRIM(REPLACE(locality, '{prefix}', '')) WHERE locality IS NOT NULL")
    
    # Удаление типов улиц
    for stype in ['УЛИЦА', 'ПРОСПЕКТ', 'ПЕРЕУЛОК', 'ПРОЕЗД', 'ШОССЕ', 'БУЛЬВАР']:
        cursor.execute(f"UPDATE addresses SET street = TRIM(REPLACE(street, '{stype}', '')) WHERE street IS NOT NULL")
    
    # Статистика
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN fias IS NOT NULL THEN 1 ELSE 0 END) as has_fias,
            SUM(CASE WHEN region IS NOT NULL THEN 1 ELSE 0 END) as has_region,
            SUM(CASE WHEN locality IS NOT NULL THEN 1 ELSE 0 END) as has_locality,
            SUM(CASE WHEN street IS NOT NULL THEN 1 ELSE 0 END) as has_street,
            SUM(CASE WHEN house IS NOT NULL THEN 1 ELSE 0 END) as has_house
        FROM addresses
    """)
    
    stats = cursor.fetchone()
    print(f"\n   Всего: {stats[0]:,}")
    print(f"   FIAS: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
    print(f"   Регион: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
    print(f"   Город: {stats[3]:,} ({stats[3]/stats[0]*100:.1f}%)")
    print(f"   Улица: {stats[4]:,} ({stats[4]/stats[0]*100:.1f}%)")
    print(f"   Дом: {stats[5]:,} ({stats[5]/stats[0]*100:.1f}%)")
    
    # Примеры
    print("\n3. Примеры очищенных записей (без FIAS):")
    cursor.execute("SELECT id, region, locality, street, house FROM addresses WHERE fias IS NULL LIMIT 10")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} | {row[2]} | {row[3]} | {row[4]}")

print("\n✅ Готово!")