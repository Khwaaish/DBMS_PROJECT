from flask import Flask, jsonify, request, render_template
import mysql.connector

app = Flask(__name__)

# DB connection
db = None
cursor = None

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123Lakshnya@123",
        database="smart_farming"
    )
    db.autocommit = True
    cursor = db.cursor()
    print("Database connected successfully!")
except Exception as e:
    print(f"Database connection failed: {e}")


def execute_query(query, params=None, fetch=True):
    try:
        if db is None or cursor is None:
            return None, "Database not connected"

        cursor.execute(query, params or ())

        if fetch:
            return cursor.fetchall(), None

        db.commit()
        return cursor.rowcount, None
    except Exception as e:
        return None, str(e)


def render_dashboard():
    status_message = None if db and cursor else "Database connection failed. Check MySQL server."
    return render_template(
        "index.html",
        db_connected=bool(db and cursor),
        status_message=status_message,
    )


# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_dashboard()


# ------------------ GUI ------------------
@app.route('/dashboard')
def dashboard():
    return render_dashboard()


# ------------------ SELECT QUERIES ------------------
@app.route('/top-region')
def top_region():
    result, error = execute_query("""
    SELECT r.region_name, AVG(f.yield)
    FROM Farm_Data f
    JOIN Region r ON f.region_id = r.region_id
    GROUP BY r.region_name
    ORDER BY AVG(f.yield) DESC
    LIMIT 1;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/top-crops')
def top_crops():
    result, error = execute_query("""
    SELECT c.crop_name, AVG(f.yield)
    FROM Farm_Data f
    JOIN Crop c ON f.crop_id = c.crop_id
    GROUP BY c.crop_name
    ORDER BY AVG(f.yield) DESC
    LIMIT 5;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/avg-yield-region')
def avg_yield_region():
    result, error = execute_query("""
    SELECT r.region_name, AVG(f.yield)
    FROM Farm_Data f
    JOIN Region r ON f.region_id = r.region_id
    GROUP BY r.region_name;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/rainy-crops')
def rainy_crops():
    result, error = execute_query("""
    SELECT DISTINCT c.crop_name
    FROM Farm_Data f
    JOIN Crop c ON f.crop_id = c.crop_id
    WHERE f.weather_condition = 'Rainy';
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/fertilizer-count')
def fertilizer_count():
    result, error = execute_query("""
    SELECT COUNT(*)
    FROM Farm_Data
    WHERE fertilizer_used = 1;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/irrigation-count')
def irrigation_count():
    result, error = execute_query("""
    SELECT COUNT(*)
    FROM Farm_Data
    WHERE irrigation_used = 1;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/best-soil')
def best_soil():
    result, error = execute_query("""
    SELECT s.soil_type, AVG(f.yield)
    FROM Farm_Data f
    JOIN Soil s ON f.soil_id = s.soil_id
    GROUP BY s.soil_type
    ORDER BY AVG(f.yield) DESC
    LIMIT 1;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/fast-harvest-crops')
def fast_harvest():
    result, error = execute_query("""
    SELECT DISTINCT c.crop_name
    FROM Farm_Data f
    JOIN Crop c ON f.crop_id = c.crop_id
    WHERE f.days_to_harvest < 100;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/records-per-region')
def records_per_region():
    result, error = execute_query("""
    SELECT r.region_name, COUNT(*)
    FROM Farm_Data f
    JOIN Region r ON f.region_id = r.region_id
    GROUP BY r.region_name;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


@app.route('/highest-yield')
def highest_yield():
    result, error = execute_query("""
    SELECT *
    FROM Farm_Data
    ORDER BY yield DESC
    LIMIT 1;
    """)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result)


# ------------------ DML ------------------
@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.json
    result, error = execute_query("""
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
    ), fetch=False)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Inserted Successfully", "rows_affected": result})


@app.route('/update')
def update_data():
    result, error = execute_query("""
    UPDATE Farm_Data
    SET yield = 4.0
    WHERE id = 1;
    """, fetch=False)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Updated Successfully", "rows_affected": result})


@app.route('/delete')
def delete_data():
    result, error = execute_query("DELETE FROM Farm_Data WHERE id = 1;", fetch=False)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Deleted Successfully", "rows_affected": result})


# ------------------ TCL ------------------
@app.route('/transaction')
def transaction():
    try:
        if db is None or cursor is None:
            return jsonify({"error": "Database not connected"}), 500

        db.start_transaction()
        cursor.execute("""
        UPDATE Farm_Data
        SET yield = yield + 1
        WHERE region_id = 1;
        """)
        db.rollback()
        return jsonify({"message": "Transaction rolled back successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ DCL (run once manually) ------------------
# NOTE: DCL usually not in API for safety

if __name__ == '__main__':
    app.run(debug=True)
