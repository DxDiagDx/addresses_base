import csv
from tools.db import Database


keys = {
    'Ростелеком__03': {
        'region': 'Область',
        'locality': 'Населенный пункт',
        'street': 'Улица',
        'house': 'Дом',
        'building': 'Корпус'
    },
    'Ростелеком__АБ МиМО': {
        'region': 'регион',
        'locality': 'населенный пункт',
        'street': 'улица',
        'house': 'дом',
        'building': 'корп./стр./лит.',
        'fias': 'ФИАС'
    },
    'Ростелеком__АБ СЗ': {
        'region': 'Наименование региона',
        'locality': 'Наименование населенного пункта',
        'street': 'Наименование улицы',
        'house': 'дом',
        'building': 'корпус/литера',
        'fias': 'ФИАС'
    },
    'Ростелеком__АБ Центр оптика': {
        'region': 'Область',
        'locality': 'Населенный пункт',
        'street': 'Улица',
        'house': 'Дом',
        'building': 'Корп.',
        'fias': 'ФИАС',
        'full_address': 'Адрес ОРПОН'
    }
}


def main():
    filename = 'Ростелеком__АБ Центр оптика 01.12.2025 фиас ФТТх ВЕСЬ.csv'

    db = Database('rostelecom.db')

    rows = []
    folder = 'files'

    with open(f'{folder}/{filename}', 'r', encoding='cp1251', newline='') as file:
        for key, namespace in keys.items():
            if filename.startswith(key):
                for i, item in enumerate(csv.DictReader(file, delimiter=';')):
                    row = {
                        'filename': filename,
                        'fias': item[namespace['fias']] if namespace.get('fias') else None,
                        'region': item[namespace['region']] if namespace.get('region') else None,
                        'locality': item[namespace['locality']] if namespace.get('locality') else None,
                        'street': item[namespace['street']] if namespace.get('street') else None,
                        'house': item[namespace['house']] if namespace.get('house') else None,
                        'building': item[namespace['building']] if namespace.get('building') else None,
                        'full_address': item[namespace['full_address']] if namespace.get('full_address') else None,
                    }
                    rows.append(row)

    db.create_table('addresses', rows[0])
    db.insert('addresses', rows)

    print('Всего:', len(rows))


if __name__ == '__main__':
    main()