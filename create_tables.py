import pandas as pd

# Load your 5000 dataset
df = pd.read_csv("final_dataset_5000.csv")

# ------------------ REGION TABLE ------------------
region_df = df[['Region']].drop_duplicates().reset_index(drop=True)
region_df['region_id'] = region_df.index + 1

# ------------------ CROP TABLE ------------------
crop_df = df[['Crop']].drop_duplicates().reset_index(drop=True)
crop_df['crop_id'] = crop_df.index + 1

# ------------------ SOIL TABLE ------------------
soil_df = df[['Soil_Type']].drop_duplicates().reset_index(drop=True)
soil_df['soil_id'] = soil_df.index + 1

# ------------------ MERGE IDS INTO MAIN TABLE ------------------
df = df.merge(region_df, on='Region')
df = df.merge(crop_df, on='Crop')
df = df.merge(soil_df, on='Soil_Type')

# Select final columns
farm_data = df[['region_id', 'crop_id', 'soil_id',
                'Rainfall_mm', 'Temperature_Celsius',
                'Fertilizer_Used', 'Irrigation_Used',
                'Weather_Condition', 'Days_to_Harvest',
                'Yield_tons_per_hectare']]

# Add primary key
farm_data.insert(0, 'id', range(1, len(farm_data) + 1))

# ------------------ SAVE ALL TABLES ------------------
region_df.to_csv("region_table.csv", index=False)
crop_df.to_csv("crop_table.csv", index=False)
soil_df.to_csv("soil_table.csv", index=False)
farm_data.to_csv("farm_data_table.csv", index=False)

print("Tables created successfully ✅")