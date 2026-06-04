import sqlite3


def normalize_prefix(prefix, mapping):
    """Нормализует префикс по словарю mapping"""
    if not prefix:
        return None
    prefix_upper = prefix.upper()
    return mapping.get(prefix_upper, prefix_upper)


def normalize_name(name):
    """Приводит имя к верхнему регистру"""
    return name.upper() if name else None


def update_register_in_db(database, column, prefix_mapping):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()

        # Получаем все записи с регионом
        cur.execute(f"""
            SELECT id, {column}_name, {column}_prefix
              FROM addresses
             WHERE {column}_name IS NOT NULL
        """)
        rows = cur.fetchall()

        updates = []
        for id_, name, prefix in rows:
            # Нормализуем название
            name_norm = normalize_name(name)

            # Нормализуем префикс
            prefix_norm = normalize_prefix(prefix, prefix_mapping)

            updates.append((name_norm, prefix_norm, id_))

        # Массовое обновление
        cur.executemany(f"""
            UPDATE addresses 
               SET {column}_name = ?, 
                   {column}_prefix = ? 
             WHERE id = ?
        """, updates)
        conn.commit()

        print(f"Обновлено {len(updates)} записей")


def main():
    database = "addresses.db"

    city_mapping = {
        "Г.": "Г",
        "Г": "Г",
        "ДЕРЕВНЯ": "Д"
    }
    locality_mapping = {
        'Д  СП': 'Д',
        'Д.': 'Д',
        'ДЕРЕВНЯ': 'Д',
        'ДНП  ДНП': 'ДНП',
        'ДНТ  ДНП': 'ДНП',
        'ДНТ  СНТ': 'СНТ',
        'ДНТ  ТЕР': 'ТЕР',
        'Ж/Д_СТ.': 'Ж/Д_СТ',
        'ЖК  ТЕР': 'ТЕР',
        'КП  ТЕР': 'ТЕР',
        'МАССИВ  ТЕР': 'ТЕР',
        'МИКР.': 'МКР',
        'МКР': 'МКР',
        'МКР.': 'МКР',
        'П.': 'П',
        'ПГТ.': 'ПГТ',
        'ПОС': 'П',
        'ПОСЁЛОК СТАНЦИИ': 'ПОСЁЛОК СТАНЦИИ',
        'ПОСЕЛОК': 'П',
        'ПОСЕЛОК  ХУТОР': 'Х',
        'ПОЧИНОК': 'ПОЧИНОК',
        'ПРОМЗОНА': 'ПРОМЗОНА',
        'РП.': 'РП',
        'С.': 'С',
        'СНО  ТЕР': 'ТЕР',
        'СНТ   ТЕР': 'ТЕР',
        'СНТ  ДСК': 'ДСК',
        'СНТ  СНТ': 'СНТ',
        'СНТ  ТЕР': 'ТЕР',
        'СП.': 'СП',
        'СТ  СНТ': 'СНТ',
        'СТ  ТЕР': 'ТЕР',
        'СТ_Ж/Д': 'Ж/Д_СТ',
        'ТЕР  ГП': 'ГП',
        'ТЕР  СНТ': 'СНТ',
        'ТЕР  СТ': 'СТ',
        'ТЕР.': 'ТЕР',
        'ТЕР. СНТ': 'СНТ',
        'ТЕР.СОСН': 'ТЕР.СОСН',
        'ТЕРСОСН': 'ТЕР.СОСН',
        'ТСН  ТЕР': 'ТЕР',
        'У': 'У',
        'УЛУС': 'У',
        'Х.': 'Х',
        'ХУТОР': 'Х'
    }
    street_mapping = {
        'АЛ.': 'АЛ',
        'АЛЛЕЯ': 'АЛ',
        'Б-Р': 'Б-Р',
        'БУЛ': 'Б-Р',
        'БУЛЬВАР': 'Б-Р',
        'ВЗД.': 'ВЗД',
        'ВЪЕЗД': 'ВЗД',
        'Г-К': 'Г/К',
        'Г/К': 'Г/К',
        'ГСК': 'ГСК',
        'ДНП': 'ДНП',
        'ДНТ': 'ДНТ',
        'ДОР': 'ДОР',
        'ДОР.': 'ДОР',
        'ЗЗД.': 'ЗЗД',
        'ЗОНА': 'ЗОНА',
        'КВ-Л': 'КВ-Л',
        'КВАРТ': 'КВ-Л',
        'КВАРТАЛ': 'КВ-Л',
        'КМ': 'КМ',
        'ЛИНИЯ': 'ЛИНИЯ',
        'ЛН.': 'ЛИНИЯ',
        'МИКР': 'МКР',
        'МКР': 'МКР',
        'МКРН': 'МКР',
        'НАБ': 'НАБ',
        'НАБ.': 'НАБ',
        'НП': 'НП',
        'П.': 'П',
        'ПЕР': 'ПЕР',
        'ПЕР  ПРОЕЗД': 'ПР-Д',
        'ПЕР.': 'ПЕР',
        'ПЕРЕЕЗД': 'ПЕРЕЕЗД',
        'ПЕРЕУЛОК': 'ПЕР',
        'ПЛ': 'ПЛ',
        'ПЛ-КА': 'ПЛ-КА',
        'ПЛОЩАДЬ': 'ПЛ',
        'ПОЧ.ОТД.': 'ПОЧ.ОТД.',
        'ПР': 'ПР',
        'ПР-Д': 'ПР-Д',
        'ПР-ЗД': 'ПР-Д',
        'ПР-КТ': 'ПР-КТ',
        'ПР-Т': 'ПР-КТ',
        'ПРОЕЗД': 'ПР-Д',
        'ПРОМЗОНА': 'ПРОМЗОНА',
        'ПРОСЕК': 'ПРОСЕК',
        'ПРОСП': 'ПР-КТ',
        'ПРОСПЕКТ': 'ПР-КТ',
        'Р-Н': 'Р-Н',
        'РЗД.': 'РЗД',
        'САД': 'САД',
        'СДТ': 'СДТ',
        'СДТ  ТЕР': 'ТЕР',
        'СК': 'СК',
        'СНО': 'СНО',
        'СНТ': 'СНТ',
        'СО': 'СО',
        'СПК': 'СПК',
        'СПУСК': 'СПУСК',
        'СТ.': 'СТ',
        'ТЕР': 'ТЕР',
        'ТЕР.': 'ТЕР',
        'ТЕР. СНТ': 'СНТ',
        'ТЕР. ТСН': 'ТСН',
        'ТРАКТ': 'ТРАКТ',
        'ТСН': 'ТСН',
        'ТУП': 'ТУП',
        'ТУП.': 'ТУП',
        'ТУПИК': 'ТУП',
        'УЛ': 'УЛ',
        'УЛ  ПРОЕЗД': 'УЛ',
        'УЛ.': 'УЛ',
        'УЛИЦА': 'УЛ',
        'УЧ-К': 'УЧ-К',
        'Ш': 'Ш',
        'Ш.': 'Ш',
        'ШОССЕ': 'Ш'
    }

    # update_register_in_db(database, 'street', street_mapping)

    with sqlite3.connect(database) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT street_prefix
              FROM addresses
             WHERE street_prefix IS NOT NULL
             ORDER BY street_prefix
        """)

        rows = cur.fetchall()
        print(len(rows))
        # street_prefixes - было 96, стало 45

        prefixes = set()
        for (row,) in rows:
            prefixes.add(row.upper())

        mapping = {}
        for p in sorted(prefixes):
            mapping[p] = p
        print(mapping)


if __name__ == '__main__':
    main()
