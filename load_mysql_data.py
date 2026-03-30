import csv

import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123Lakshnya@123",
    "database": "smart_farming",
}


def bool_to_int(value):
    return 1 if str(value).strip().lower() == "true" else 0


def load_region_table(cursor):
    with open("region_table.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [(int(row["region_id"]), row["Region"]) for row in reader]

    cursor.executemany(
        """
        INSERT IGNORE INTO region (region_id, region_name)
        VALUES (%s, %s)
        """,
        rows,
    )


def load_crop_table(cursor):
    with open("crop_table.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [(int(row["crop_id"]), row["Crop"]) for row in reader]

    cursor.executemany(
        """
        INSERT IGNORE INTO crop (crop_id, crop_name)
        VALUES (%s, %s)
        """,
        rows,
    )


def load_soil_table(cursor):
    with open("soil_table.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [(int(row["soil_id"]), row["Soil_Type"]) for row in reader]

    cursor.executemany(
        """
        INSERT IGNORE INTO soil (soil_id, soil_type)
        VALUES (%s, %s)
        """,
        rows,
    )


def load_farm_data_table(cursor):
    with open("farm_data_table.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            rows.append(
                (
                    int(row["id"]),
                    int(row["region_id"]),
                    int(row["crop_id"]),
                    int(row["soil_id"]),
                    float(row["Rainfall_mm"]),
                    float(row["Temperature_Celsius"]),
                    bool_to_int(row["Fertilizer_Used"]),
                    bool_to_int(row["Irrigation_Used"]),
                    row["Weather_Condition"],
                    int(row["Days_to_Harvest"]),
                    float(row["Yield_tons_per_hectare"]),
                )
            )

    cursor.executemany(
        """
        INSERT IGNORE INTO farm_data
        (
            id, region_id, crop_id, soil_id, rainfall, temperature,
            fertilizer_used, irrigation_used, weather_condition,
            days_to_harvest, `yield`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        rows,
    )


def show_counts(cursor):
    for table in ["region", "crop", "soil", "farm_data"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table}: {cursor.fetchone()[0]}")


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        load_region_table(cursor)
        load_crop_table(cursor)
        load_soil_table(cursor)
        load_farm_data_table(cursor)
        conn.commit()
        print("Data load complete.")
        show_counts(cursor)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
