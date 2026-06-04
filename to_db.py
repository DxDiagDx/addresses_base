import json
from glob import glob
from pathlib import Path
from tools.db import Database


def get_gar(text):
    if text:
        return json.dumps(text, ensure_ascii=False)
    return None


def get_row_other(line, provider):
    row = {
        "filename": line.get("filename"),
        "provider": provider,
        "fias": line.get("fias"),
        "gar": get_gar(json.loads(line["gar"]) if line.get("gar") else None),
        "region": line.get("region"),
        "region_name": line.get("region_name"),
        "region_prefix": line.get("region_prefix"),
        "district": line.get("district"),
        "district_name": line.get("district_name"),
        "district_prefix": line.get("district_prefix"),
        "city": line.get("city"),
        "city_name": line.get("city_name"),
        "city_prefix": line.get("city_prefix"),
        "locality": line.get("locality"),
        "locality_name": line.get("locality_name"),
        "locality_prefix": line.get("locality_prefix"),
        "street": line.get("street"),
        "street_name": line.get("street_name"),
        "street_prefix": line.get("street_prefix"),
        "house": line.get("house"),
        "house_number": None,  # HouseNumber для МТС
        "house_block": line.get("building_block"),  # HouseBlock для МТС
        "house_building": line.get("building"),  # HouseBuilding для МТС
        "full_address": line.get("full_address"),
    }
    # print(row)
    return row


def get_row_mts(line, provider):
    # print(json.dumps(line, ensure_ascii=False, indent=2))
    row = {
        "filename": line.get("filename"),
        "provider": provider,
        "fias": line.get("FiasCode"),
        "gar": get_gar(json.loads(line["gar"]) if line.get("gar") else None),
        "region": None,
        "region_name": line.get("RegionName"),
        "region_prefix": line.get("RegionPrefix"),
        "district": line.get("district"),
        "district_name": line.get("DistrictName"),
        "district_prefix": line.get("DistrictPrefix"),
        "city": line.get("city"),
        "city_name": line.get("CityName"),
        "city_prefix": line.get("CityPrefix"),
        "locality": line.get("locality"),
        "locality_name": line.get("LocalityName"),
        "locality_prefix": line.get("LocalityPrefix"),
        "street": line.get("street"),
        "street_name": line.get("StreetName"),
        "street_prefix": line.get("StreetPrefix"),
        "house": line.get("house"),
        "house_number": line.get("HouseNumber"),
        "house_block": line.get("HouseBlock"),
        "house_building": line.get("HouseBuilding"),
        "full_address": line.get("full_address"),
    }
    # print(json.dumps(row, ensure_ascii=False, indent=2))
    return row


def main():
    database = "addresses.db"
    all_db = Database(database)

    all_rows = []
    for item in glob('./providers/*.db'):
        provider = Path(item).stem
        print(provider)

        db = Database(item)
        lines = db.execute("SELECT * FROM addresses")
        for line in lines:
            if provider == "mts":
                row = get_row_mts(line, provider)
            else:
                row = get_row_other(line, provider)
            all_rows.append(row)
        # print()

    print(len(all_rows))
    all_db.create_table("addresses", all_rows[0])
    all_db.insert("addresses", all_rows)
    print("Готово!")


if __name__ == '__main__':
    main()