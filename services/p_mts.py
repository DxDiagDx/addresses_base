import csv
from tools.db import Database


def main():
    filename = 'МТС.csv'

    db = Database('mts.db')

    rows = []
    folder = 'files'

    with open(f'{folder}/{filename}', 'r', encoding='cp1251', newline='') as file:
        for i, row in enumerate(csv.DictReader(file, delimiter=';')):
            rows.append(row)

    db.create_table('addresses', rows[0])
    db.insert('addresses', rows)

    print('Всего:', len(rows))


if __name__ == '__main__':
    main()