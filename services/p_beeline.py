import csv
from tools.db import Database


keys = {
    'Билайн': {
        'fias': 'Код ФИАС',
        'region': None,
        'locality': 'Город',
        'street': 'Улица',
        'street_type': 'Тип улицы',
        'house': 'Дом/Строение',
        'building': 'Корпус',
        'full_address': 'Адрес подключенного дома',
    }
}


def main():
    filename = 'Билайн.csv'

    db = Database('beeline.db')

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
                        'building_block': item[namespace['building_block']] if namespace.get('building_block') else None,
                        'full_address': item[namespace['full_address']] if namespace.get('full_address') else None,
                    }
                    rows.append(row)

    db.create_table('addresses', rows[0])
    db.insert('addresses', rows)

    print('Всего:', len(rows))


if __name__ == '__main__':
    main()