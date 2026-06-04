import re
from tools.db import Database


def clean_col(db, table, col_name):
    "Очищаем колонки от пустых значений и ошибок Excel"
    db.execute(f"""
        UPDATE {table}
           SET {col_name} = NULL
         WHERE {col_name} IN ('#ИМЯ?', '#Н/Д', '', ' ', '0', 'Не определено')
    """)
    #TODO 'нет улицы'
    print(f'Колонка "{col_name}" очищена.')


def clean_name(text, stop_words):
    """ Удаляет стоп-слов их начала и конца строки """
    # Экранируем точки в стоп-словах
    escaped_words = [re.escape(word) for word in stop_words]

    # Паттерны
    # для начала строки
    pattern_start = r'^(?:' + '|'.join(escaped_words) + r')(?:\.|\s|$)'

    # для конца строки
    pattern_end = r'(?:\s|\.)(?:' + '|'.join(escaped_words) + r')$'

    # слово одно и нет пробелов
    pattern_exact = r'^(?:' + '|'.join(escaped_words) + r')(?:\.?)$'

    result = re.sub(pattern_start, '', text, re.IGNORECASE).strip()
    result = re.sub(pattern_end, '', result, re.IGNORECASE).strip()
    result = re.sub(pattern_exact, '', result, re.IGNORECASE).strip()

    stop_word = text.replace(result, '').strip()
    print(f"{text:30} -> {result:30} -> {stop_word}")
    if result:
        return result, stop_word


def main():
    db = Database('./providers/ufanet.db')

    # Очищаем колонки от пустых значений
    # Колонку ФИАС
    # col_fias = 'fias'
    # col_fias = 'FiasCode'
    # clean_col(db, 'addresses', col_fias)

    # Нормализуем колонку УЛИЦА
    # clean_col(db, 'addresses', 'street')
    # exit()

    street_types = ['улица', 'территория улица', 'переулок', 'проезд', 'проспект', 'шоссе']

    # Записываем сокращения, потом добавляем их версии в БОЛЬШОМ РЕГИСТРЕ, потом с точкой
    locality_types = ['тер', 'Пгт', 'пгт', 'С/О', 'г', 'гп', 'д', 'дп',
                      'днп', 'кв-л', 'мкр', 'п', 'П', 'рп', 'с', 'С', 'ст', 'х',
                      'снт', 'сл', 'нп', 'п/о', 'п/ст', 'ААЛ']
    locality_types += [socr.upper() for socr in locality_types]
    locality_types += [f"{socr}." for socr in locality_types]

    rows = db.execute("""
        SELECT DISTINCT locality
          FROM addresses
         WHERE fias IS NULL
           AND locality IS NOT NULL
         ORDER BY locality
    """)

    elems = set()
    elems_edit = set()
    cells = []
    for row in rows:
        text = row['locality']
        if text:
            try:
                elem = text.split('.')[-1] if len(text.split()) > 1 else text
                elems.add(elem)
            except Exception as e:
                print(text, e)
                exit()

        # street, stop_word = clean_name(row['street'], stop_words=street_types)
        locality, stop_word = clean_name(text, stop_words=locality_types)
        elems_edit.add(locality)

        cells.append(locality)

    # for elem_edit in sorted(elems_edit):
    #     print(elem_edit)

    # for elem in sorted(elems):
    #     print(elem)
    print(len(cells))


if __name__ == '__main__':
    main()