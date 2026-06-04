import sqlite3
from pathlib import Path

SOURCE_DB = Path("levels.db")
TARGET_DB = Path("addresses.db")
BATCH_SIZE = 10000


def migrate_back():
    with sqlite3.connect(SOURCE_DB) as src:
        with sqlite3.connect(TARGET_DB) as dst:
            dst_cur = dst.cursor()

            src_cur = src.cursor()
            src_cur.execute("""
                SELECT 
                    addresses_id,
                    region_name, region_prefix,
                    district_name, district_prefix,
                    city_name, city_prefix,
                    locality_name, locality_prefix,
                    street_name, street_prefix,
                    house_name, house_addnum1, house_addnum2
                FROM addresses
            """)

            batch = []
            count = 0

            for row in src_cur:
                src_id = row[0]
                values = row[1:] + (src_id,)
                batch.append(values)
                count += 1

                if len(batch) >= BATCH_SIZE:
                    dst_cur.executemany("""
                        UPDATE addresses SET
                            region_name = ?,
                            region_prefix = ?,
                            district_name = ?,
                            district_prefix = ?,
                            city_name = ?,
                            city_prefix = ?,
                            locality_name = ?,
                            locality_prefix = ?,
                            street_name = ?,
                            street_prefix = ?,
                            house_number = ?,
                            house_block = ?,
                            house_building = ?
                        WHERE id = ?
                    """, batch)
                    dst.commit()
                    print(f"Обновлено {count} записей")
                    batch = []

            if batch:
                dst_cur.executemany("""
                    UPDATE addresses SET
                        region_name = ?,
                        region_prefix = ?,
                        district_name = ?,
                        district_prefix = ?,
                        city_name = ?,
                        city_prefix = ?,
                        locality_name = ?,
                        locality_prefix = ?,
                        street_name = ?,
                        street_prefix = ?,
                        house_number = ?,
                        house_block = ?,
                        house_building = ?
                    WHERE id = ?
                """, batch)
                dst.commit()

            print(f"\nГотово! Обновлено {count} записей")


if __name__ == "__main__":
    migrate_back()