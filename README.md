# Smart Farming DBMS Project (Farmlytics)

Flask + MySQL based DBMS project for smart farming analytics.

## 1. Project Requirements Coverage
1. Database with at least 5000 entries and at least 2 tables: Completed.
2. Basic GUI built and loaded on server: Completed.

Current database status:
1. Database name: `smart_farming`
2. Tables: `region`, `crop`, `soil`, `farm_data`
3. Main fact table rows: `farm_data = 5000`

## 2. Project Objective
Build a normalized agricultural database and a web interface to:
1. run SQL analytics queries,
2. demonstrate DBMS concepts (DDL, DML, TCL, keys, joins, aggregations),
3. show ER model and relational schema views.

## 3. Tech Stack
1. Python 3
2. Flask
3. MySQL
4. Pandas
5. HTML/CSS/JavaScript

## 4. Project Structure
1. `app.py`: Flask backend and all API/UI routes
2. `templates/index.html`: Main dashboard UI
3. `templates/schema_view.html`: ER and relation schema UI pages
4. `static/style.css`: Frontend styling
5. `sample_data.py`: Creates 5000-sample dataset from raw CSV
6. `create_tables.py`: Normalizes sampled dataset into table CSV files
7. `load_mysql_data.py`: Loads CSV data into MySQL tables
8. `crop_yield.csv`: Raw source dataset
9. `final_dataset_5000.csv`: Sampled dataset
10. `region_table.csv`, `crop_table.csv`, `soil_table.csv`, `farm_data_table.csv`: normalized CSV outputs

## 5. Database Schema

### 5.1 Tables and Columns
1. `region(region_id PK, region_name)`
2. `crop(crop_id PK, crop_name)`
3. `soil(soil_id PK, soil_type)`
4. `farm_data(id PK, region_id FK, crop_id FK, soil_id FK, rainfall, temperature, fertilizer_used, irrigation_used, weather_condition, days_to_harvest, yield)`

### 5.2 Relationships
1. `region (1) -> (N) farm_data` via `region_id`
2. `crop (1) -> (N) farm_data` via `crop_id`
3. `soil (1) -> (N) farm_data` via `soil_id`


## 6. Setup and Run

### 6.1 Install dependencies
```bash
pip install flask mysql-connector-python pandas
```

### 6.2 MySQL setup
1. Ensure MySQL server is running.
2. Ensure database `smart_farming` exists with tables:
`region`, `crop`, `soil`, `farm_data` and proper PK/FK constraints.
3. Update DB credentials in `app.py` and `load_mysql_data.py` if needed.

### 6.3 Load data
```bash
python sample_data.py
python create_tables.py
python load_mysql_data.py
```

### 6.4 Start web app
```bash
python app.py
```

Open:
1. Dashboard: `http://127.0.0.1:5000/dashboard`
2. ER Model page: `http://127.0.0.1:5000/er-model`
3. Relational Schema page: `http://127.0.0.1:5000/relation-schema`



