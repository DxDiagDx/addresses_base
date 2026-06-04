import csv
from tools.db import Database


keys = {
    'Мегафон': {
        'fias': 'Фиас guid',
        'region': 'Регион (Населенный пункт)',
        'locality': 'Населенный пункт',
        'locality_type': 'Сокращение (Населенный пункт)',
        'street': 'Улица',
        'street_type': 'Сокращение (Улица)',
        'house': 'Номер дома'
    }
}


def main():
    filename = 'Мегафон.csv'

    db = Database('megafon.db')

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
                        'locality_type': item[namespace['locality_type']] if namespace.get('locality_type') else None,
                        'street': item[namespace['street']] if namespace.get('street') else None,
                        'street_type': item[namespace['street_type']] if namespace.get('street_type') else None,
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