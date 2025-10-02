import pandas as pd

# Load datasets
features_df = pd.read_csv("./csv/angeles_barangay_features_proxy.csv")
flood_df = pd.read_csv("./csv/flood_data_results.csv")

# Convert time columns
features_df["time"] = pd.to_datetime(features_df["time"])
flood_df["date"] = pd.to_datetime(flood_df["date"]).dt.tz_localize(None)

# Merge on date
merged_df = features_df.merge(
    flood_df[["date", "river_discharge"]],
    left_on="time",
    right_on="date",
    how="left"
).drop(columns=["date"])

# Save merged dataset
merged_df.to_csv("angeles_flood_merged.csv", index=False)

print("✅ Merged dataset saved as angeles_flood_merged.csv")
print(merged_df.head())
