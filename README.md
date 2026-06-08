```markdown
# Адресная база: дедупликация с использованием ГАР

Проект для загрузки, нормализации и дедупликации адресов из разных источников (Ростелеком, МТС, Мегафон, Дом.ру) с использованием официального Государственного адресного реестра (ГАР).

## Описание работы

Выгрузки информации от провайдеров в Excel таблицах содержит разную структуру.
Для приведения структуры к единому виду:
1. Конвертируем XlSX в CSV. 
   Можно использовать OpenCalc для работы с файлами провайдеров. 
   При открытии, всем полям указать тип полей ТЕКС.
   Если открывать в XLS, то номера домов, например 1/5 эксель автоматически преобразует в дату 01.май.
2. В каждом файле распределяем данные по категориям: Регион, Район, Город, Населённый пункт, Улица, Дом, Корпус, Строение, Технология подключения
3. Импортируем всё в единую базу данных

Далее будем работать уже с единой базой данных и в ней унифицировать адреса.
Для облегчения работы рекомендуется использовать ГАР для приведения данных к единому виду. 

## Состав проекта

- `import_gar_full.py` — единый скрипт для полного импорта ГАР в PostgreSQL
- `get_full_address_by_fias.py` — обогащение адресов через ГАР (получение канонического адреса по FIAS)
- `localities_from_gar.py` — выгрузка населённых пунктов из ГАР по регионам
- `clean_addresses.py` — очистка адресов от невалидных значений "#Н/Д", ""

## 🗄️ Структура таблиц

### PostgreSQL (ГАР)

| Таблица | Описание | Кол-во записей |
|---------|----------|----------------|
| `addr_obj` | Адресные объекты (регионы, города, улицы) | ~3 млн |
| `houses` | Дома (номера, корпуса, GUID) | ~80 млн |
| `hierarchy` | Иерархические связи (пути) | ~150 млн |
| `reestr_objects` | Реестр GUID объектов | ~128 млн |
| `addr_obj_division` | Переподчинения | опционально |
| `mun_hierarchy` | Муниципальная иерархия | опционально |

### SQLite (исходные адреса)

| Колонка | Описание |
|---------|----------|
| `id` | Первичный ключ |
| `fias` | GUID дома из ГАР |
| `region_name` / `region_prefix` | Регион |
| `district_name` / `district_prefix` | Район |
| `city_name` / `city_prefix` | Город |
| `locality_name` / `locality_prefix` | Населенный пункт |
| `street_name` / `street_prefix` | Улица |
| `house_number`, `house_building`, `house_block` | Дом |
| `internet_tech` | Технология подключения клиента |
| `gar` | JSON с каноническим адресом из ГАР |

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
# Установка PostgreSQL в WSL
sudo apt update
sudo apt install postgresql-16

# Создание базы
sudo -u postgres psql
CREATE DATABASE gar;
CREATE USER gar_user WITH PASSWORD 'gar';
GRANT ALL PRIVILEGES ON DATABASE gar TO gar_user;
```

### 2. Импорт ГАР

```bash
python3 import_gar_full.py
```

## 📊 Ключевые запросы

### Получить код региона по названию

```sql
SELECT regioncode FROM addr_obj 
WHERE name ILIKE '%кемеровская%' AND typename = 'обл' LIMIT 1;
```

### Найти населённый пункт

```sql
SELECT name, typename FROM addr_obj 
WHERE regioncode = '42' AND name ILIKE '%терентьевское%' LIMIT 1;
```

### Получить полный адрес по GUID дома

```sql
WITH path_parts AS (
    SELECT unnest(string_to_array(
        (SELECT path FROM hierarchy WHERE objectid = (
            SELECT objectid FROM houses WHERE houseguid = 'f39cec3d-3782-4954-a970-7926293f9e03'
        )), '.'))::BIGINT as objectid
)
SELECT STRING_AGG(a.name, ', ') as full_address
FROM path_parts p JOIN addr_obj a ON p.objectid = a.objectid;
```

### Канонический адрес в JSON

```sql
WITH unique_path AS (...)
SELECT jsonb_agg(jsonb_build_object('typename', typename, 'name', name) ORDER BY pos) ||
       jsonb_build_object('typename', 'д', 'name', housenum) as address_parts
FROM unique_path
GROUP BY houseguid, housenum;
```

## 🔧 Нормализация адресов (Python)

```python
def normalize_prefix(prefix, mapping):
    prefix_upper = prefix.upper()
    return mapping.get(prefix_upper, prefix_upper)
```

## ⚡ Советы по оптимизации

- Используйте массовые операции (`executemany`, временные таблицы)
- Создавайте индексы после импорта
- Для массовых обновлений SQLite используйте `CREATE TEMP TABLE`

```python
# Быстрое массовое обновление
cur.execute("CREATE TEMP TABLE updates (fias TEXT, gar TEXT)")
cur.executemany("INSERT INTO updates VALUES (?, ?)", updates)
cur.execute("""
    UPDATE addresses SET gar = (
        SELECT gar FROM updates WHERE updates.fias = addresses.fias
    ) WHERE fias IN (SELECT fias FROM updates)
""")
```

## 📚 Полезные ссылки

- [ФИАС / ГАР](https://fias.nalog.ru) — официальный сайт
- [Документация PostgreSQL](https://www.postgresql.org/docs/)
- [psycopg2](https://www.psycopg.org/docs/)

## 📝 Лицензия

MIT

## 👤 Автор

[DxDiagDx](https://github.com/DxDiagDx)
```