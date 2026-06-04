import csv
import json
import datetime


def str_to_float(text):
    if isinstance(text, int) or isinstance(text, float):
        return text

    if not text:
        return 0.00

    format_text = text.replace('\xa0', '').replace(',', '.').replace(' ', '')
    return float(format_text)


def date_convert(date_str, format_in, format_out):
    if date_str:
        date_format = datetime.datetime.strptime(date_str, format_in)
        date_out = datetime.datetime.strftime(date_format, format_out)
        return date_out


def trim(value):
    items = []
    if value:
        words = value.split()
        for word in words:
            if word:
                word = word.strip()
                items.append(word)
    return ' '.join(items)


def html_open(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def html_save(filename, html):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)


def json_open(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def json_save(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def csv_open(filename, encoding='utf-8', delimiter=','):
    with open(filename, 'r', encoding=encoding, newline='') as file:
        return [item for item in csv.DictReader(file, delimiter=delimiter)]


def print_json(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))