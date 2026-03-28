from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# DB connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=" ",
    database="smart_farming"
)

cursor = db.cursor()

# ------------------ HOME ------------------
@app.route('/')
def home():
    return "Smart Farming System Running ✅"

# ------------------ SELECT QUERIES ------------------

@app.route('/top-region')
def top_region():
    cursor.execute("""
    SELECT r.region_name, AVG(f.yield)
    FROM Farm_Data f
    JOIN Region r ON f.region_id = r.region_id
    GROUP BY r.region_name
    ORDER BY AVG(f.yield) DESC
    LIMIT 1;
    """)
    return jsonify(cursor.fetchall())


@app.route('/top-crops')
def top_crops():
    cursor.execute("""
    SELECT c.crop_name, AVG(f.yield)
    FROM Farm_Data f
    JOIN Crop c ON f.crop_id = c.crop_id
    GROUP BY c.crop_name
    ORDER BY AVG(f.yield) DESC
    LIMIT 5;
    """)
    return jsonify(cursor.fetchall())


@app.route('/avg-yield-region')
def avg_yield_region():
    cursor.execute("""
    SELECT r.region_name, AVG(f.yield)
    FROM Farm_Data f
    JOIN Region r ON f.region_id = r.region_id
    GROUP BY r.region_name;
    """)
    return jsonify(cursor.fetchall())


@app.route('/rainy-crops')
def rainy_crops():
    cursor.execute("""
    SELECT DISTINCT c.crop_name
    FROM Farm_Data f
    JOIN Crop c ON f.crop_id = c.crop_id
    WHERE f.weather_condition = 'Rainy';
    """)
    return jsonify(cursor.fetchall())


@app.route('/fertilizer-count')
def fertilizer_count():
    cursor.execute("""
    SELECT COUNT(*)
    FROM Farm_Data
    WHERE fertilizer_used = 1;
    """)
    return jsonify(cursor.fetchall())


@app.route('/irrigation-count')
def irrigation_count():
    cursor.execute("""
    SELECT COUNT(*)
    FROM Farm_Data
    WHERE irrigation_used = 1;
    """)
    return jsonify(cursor.fetchall())


@app.route('/best-soil')
def best_soil():
    cursor.execute("""
    SELECT s.soil_type, AVG(f.yield)
    FROM Farm_Data f
    JOIN Soil s ON f.soil_id = s.soil_id
    GROUP BY s.soil_type
    ORDER BY AVG(f.yield) DESC
    LIMIT 1;
    """)
    return jsonify(cursor.fetchall())


@app.route('/fast-harvest-crops')
def fast_harvest():
    cursor.execute("""
    SELECT DISTINCT c.crop_name
    FROM Farm_Data f
    JOIN Crop c ON f.crop_id = c.crop_id
    WHERE f.days_to_harvest < 100;
    """)
    return jsonify(cursor.fetchall())


@app.route('/records-per-region')
def records_per_region():
    cursor.execute("""
    SELECT r.region_name, COUNT(*)
    FROM Farm_Data f
    JOIN Region r ON f.region_id = r.region_id
    GROUP BY r.region_name;
    """)
    return jsonify(cursor.fetchall())


@app.route('/highest-yield')
def highest_yield():
    cursor.execute("""
    SELECT *
    FROM Farm_Data
    ORDER BY yield DESC
    LIMIT 1;
    """)
    return jsonify(cursor.fetchall())

# ------------------ DML ------------------

@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.json
    cursor.execute("""
    INSERT INTO Farm_Data
    (region_id, crop_id, soil_id, rainfall, temperature,
    fertilizer_used, irrigation_used, weather_condition,
    days_to_harvest, yield)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data['region_id'], data['crop_id'], data['soil_id'],
        data['rainfall'], data['temperature'],
        data['fertilizer_used'], data['irrigation_used'],
        data['weather_condition'], data['days_to_harvest'],
        data['yield']
    ))
    db.commit()
    return "Inserted Successfully"


@app.route('/update')
def update_data():
    cursor.execute("""
    UPDATE Farm_Data
    SET yield = 4.0
    WHERE id = 1;
    """)
    db.commit()
    return "Updated Successfully"


@app.route('/delete')
def delete_data():
    cursor.execute("DELETE FROM Farm_Data WHERE id = 1;")
    db.commit()
    return "Deleted Successfully"

# ------------------ TCL ------------------

@app.route('/transaction')
def transaction():
    try:
        cursor.execute("START TRANSACTION;")
        cursor.execute("""
        UPDATE Farm_Data
        SET yield = yield + 1
        WHERE region_id = 1;
        """)
        cursor.execute("ROLLBACK;")
        return "Transaction rolled back successfully"
    except:
        return "Transaction failed"

# ------------------ DCL (run once manually) ------------------
# NOTE: DCL usually not in API for safety

if __name__ == '__main__':
    app.run(debug=True)