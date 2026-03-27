import pandas as pd

# Load dataset
df = pd.read_csv("crop_yield.csv")

# Take 5000 rows
df_sample = df.sample(n=5000, random_state=42)

# Save new file
df_sample.to_csv("final_dataset_5000.csv", index=False)

print("DONE ✅")