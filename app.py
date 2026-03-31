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


def get_schema_metadata():
    if db is None or cursor is None:
        return None, "Database not connected"

    schema_name = db.database

    columns_result, error = execute_query(
        """
        SELECT table_name, column_name, column_type, is_nullable, column_key
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
        """,
        (schema_name,),
    )
    if error:
        return None, error

    fk_result, error = execute_query(
        """
        SELECT table_name, column_name, referenced_table_name, referenced_column_name
        FROM information_schema.key_column_usage
        WHERE table_schema = %s
          AND referenced_table_name IS NOT NULL
        ORDER BY table_name, column_name;
        """,
        (schema_name,),
    )
    if error:
        return None, error

    table_map = {}
    for table_name, column_name, column_type, is_nullable, column_key in columns_result:
        if table_name not in table_map:
            table_map[table_name] = {
                "name": table_name,
                "attributes": [],
                "primary_keys": [],
                "foreign_keys": [],
            }

        table_map[table_name]["attributes"].append(
            {
                "name": column_name,
                "type": column_type,
                "nullable": is_nullable == "YES",
            }
        )
        if column_key == "PRI":
            table_map[table_name]["primary_keys"].append(column_name)

    relationships = []
    for table_name, column_name, ref_table, ref_column in fk_result:
        if table_name in table_map:
            table_map[table_name]["foreign_keys"].append(
                {
                    "column": column_name,
                    "references_table": ref_table,
                    "references_column": ref_column,
                }
            )

        relationships.append(
            {
                "from_table": table_name,
                "from_column": column_name,
                "to_table": ref_table,
                "to_column": ref_column,
            }
        )

    entities = [table_map[key] for key in sorted(table_map.keys())]
    return {
        "database": schema_name,
        "entities": entities,
        "relationships": relationships,
    }, None


def build_mermaid_er(metadata):
    def node_name(name):
        return "".join(ch if ch.isalnum() else "_" for ch in name).upper()

    lines = ["erDiagram"]

    for entity in metadata["entities"]:
        entity_node = node_name(entity["name"])
        lines.append(f"    {entity_node} {{")
        for attribute in entity["attributes"]:
            raw_type = attribute["type"].split("(")[0].upper()
            marker = " PK" if attribute["name"] in entity["primary_keys"] else ""
            lines.append(f"        {raw_type} {attribute['name']}{marker}")
        lines.append("    }")

    for relation in metadata["relationships"]:
        from_node = node_name(relation["from_table"])
        to_node = node_name(relation["to_table"])
        lines.append(f"    {to_node} ||--o{{ {from_node} : {relation['from_column']}")

    return "\n".join(lines)


def build_relation_schema_lines(metadata):
    lines = []
    for entity in metadata["entities"]:
        fk_by_column = {
            fk["column"]: f"{fk['references_table']}.{fk['references_column']}"
            for fk in entity["foreign_keys"]
        }

        parts = []
        for attribute in entity["attributes"]:
            marks = []
            if attribute["name"] in entity["primary_keys"]:
                marks.append("PK")
            if attribute["name"] in fk_by_column:
                marks.append(f"FK->{fk_by_column[attribute['name']]}")

            marks_suffix = f" [{', '.join(marks)}]" if marks else ""
            parts.append(f"{attribute['name']} {attribute['type']}{marks_suffix}")

        lines.append(f"{entity['name']}({', '.join(parts)})")

    return lines


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


@app.route('/api/er-model')
def er_model_api():
    metadata, error = get_schema_metadata()
    if error:
        return jsonify({"error": error}), 500

    return jsonify(
        {
            "database": metadata["database"],
            "entities": metadata["entities"],
            "relationships": metadata["relationships"],
            "mermaid": build_mermaid_er(metadata),
        }
    )


@app.route('/api/relation-schema')
def relation_schema_api():
    metadata, error = get_schema_metadata()
    if error:
        return jsonify({"error": error}), 500

    return jsonify(
        {
            "database": metadata["database"],
            "entities": metadata["entities"],
            "relation_schema": build_relation_schema_lines(metadata),
            "relationships": metadata["relationships"],
            "mermaid": build_mermaid_er(metadata),
        }
    )


@app.route('/er-model')
def er_model_page():
    return render_template(
        "schema_view.html",
        page_title="ER Model",
        api_endpoint="/api/er-model",
        view_mode="er",
    )


@app.route('/relation-schema')
def relation_schema_page():
    return render_template(
        "schema_view.html",
        page_title="Relational Schema",
        api_endpoint="/api/relation-schema",
        view_mode="schema",
    )


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
