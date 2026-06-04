import re
from address_base.PREFIXES import PREFIXES


def prepare_stop_words(words):
    """
    Записываем сокращения, добавляем их версии
    в БОЛЬШОМ РЕГИСТРЕ, с первой заглавной и точкой в конце
    """
    words += [word.capitalize() for word in words]
    words += [word.upper() for word in words]
    words += [f"{word}." for word in words]
    return set(words)


def clean_name(text, name_type, prefixes):
    text = text.strip()
    stop_words = list(prefixes)  # копируем список
    stop_words = prepare_stop_words(stop_words)

    # Экранируем точки в стоп-словах
    escaped_words = [re.escape(word) for word in stop_words]

    # Паттерны
    # для начала строки
    pattern_start = r'^(?:' + '|'.join(escaped_words) + r')(?:\.|\s|$)'

    # для конца строки
    pattern_end = r'(?:\s|\.)(?:' + '|'.join(escaped_words) + r')$'

    # слово одно и нет пробелов
    pattern_exact = r'^(?:' + '|'.join(escaped_words) + r')(?:\.?)$'

    name = re.sub(pattern_start, '', text, re.IGNORECASE).strip()
    name = re.sub(pattern_end, '', name, re.IGNORECASE).strip()
    name = re.sub(pattern_exact, '', name, re.IGNORECASE).strip()

    prefix = text.replace(name, '').strip()
    if prefix != "":
        prefix = prefix.replace('.', '').upper()
        name = name.replace("\"", "").upper()
        return {"name": name, "prefix": prefix, "type": name_type}


def clean_names(text):
    """ Удаляет стоп-слов из начала и конца строки """
    for name_type, values in PREFIXES.items():
        result = clean_name(text, name_type, values)
        if result:
            return result


def clean_split_comma(text):
    items = []
    for t in text.split(','):
        item = t.strip().replace("\"", "")
        items.append(item)
    return items


def extract_parenthesis_content(text):
    """ Извлекает теккст из первых круглых скобок """
    match = re.search(r'\(([^)]+)\)', text)
    return match.group(1) if match else None
