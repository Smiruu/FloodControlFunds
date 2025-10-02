import xarray as xr
import rioxarray
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------
# 1. File paths
# ------------------------------
chirps_folder = Path("chirps_data")
shapefile_path = Path("ph_polygon/gadm41_PHL_3.shp")
discharge_path = Path("csv/flood_data_results.csv")

# ------------------------------
# 2. Load CHIRPS NetCDF files
# ------------------------------
nc_files = sorted(chirps_folder.glob("*.nc"))
print(f"Loading {len(nc_files)} CHIRPS files...")
rain = xr.open_mfdataset(nc_files, combine="by_coords")["precip"]

# Prepare CHIRPS for rioxarray
rain = rain.rename({"longitude": "x", "latitude": "y"})
rain.rio.write_crs("EPSG:4326", inplace=True)

# ------------------------------
# 3. Load shapefile
# ------------------------------
gdf = gpd.read_file(shapefile_path).to_crs("EPSG:4326")
print("Shapefile columns:", gdf.columns)

# ------------------------------
# 4. Filter to Angeles City barangays
# ------------------------------
angeles_bgy = gdf[gdf["NAME_2"] == "Angeles City"].copy()

print("\n📌 Barangays found in shapefile:")
print(angeles_bgy["NAME_3"].value_counts())
print(f"Total barangays found: {len(angeles_bgy)}\n")

# Buffer to avoid geometry errors
angeles_bgy["geometry"] = angeles_bgy.geometry.buffer(0.001)

# ------------------------------
# 5. Clip rainfall data per barangay
# ------------------------------
results = []
total = len(angeles_bgy)
print(f"Starting rainfall extraction for {total} barangays...\n")

for idx, (_, row) in enumerate(angeles_bgy.iterrows(), start=1):
    try:
        print(f"[{idx}/{total}] Processing {row['NAME_3']}...")
        rain_clip = rain.rio.clip([row.geometry], angeles_bgy.crs, all_touched=True)

        if rain_clip.notnull().sum() == 0:
            print(f"⚠️ No data for {row['NAME_3']}, skipping.\n")
            continue

        rain_ts = rain_clip.mean(dim=["y", "x"]).to_dataframe().reset_index()
        rain_ts["barangay"] = row["NAME_3"]
        results.append(rain_ts)
        print(f"✅ Finished {row['NAME_3']}\n")
    except Exception as e:
        print(f"⚠️ Skipping {row['NAME_3']}: {e}\n")

print(f"🎯 Completed processing {len(results)}/{total} barangays.\n")

# ------------------------------
# 6. Combine results
# ------------------------------
df_all = pd.concat(results, ignore_index=True)

# Make sure time is datetime (and timezone-naive)
df_all["time"] = pd.to_datetime(df_all["time"]).dt.tz_localize(None)

# ------------------------------
# 7. Load river discharge data
# ------------------------------
discharge_df = pd.read_csv(discharge_path, parse_dates=["date"])
discharge_df = discharge_df.rename(columns={"date": "time"})
discharge_df["time"] = pd.to_datetime(discharge_df["time"]).dt.tz_localize(None)

# ------------------------------
# 8. Merge rainfall with discharge
# ------------------------------
merged = pd.merge(df_all, discharge_df[["time", "river_discharge"]],
                  on="time", how="left")

# ------------------------------
# 9. Add rainfall lag/rolling features
# ------------------------------
merged = merged.sort_values(["barangay", "time"])

# Group by barangay so lags are per-location
merged["precip_lag1"] = merged.groupby("barangay")["precip"].shift(1)
merged["precip_lag2"] = merged.groupby("barangay")["precip"].shift(2)
merged["precip_3d_sum"] = merged.groupby("barangay")["precip"].rolling(3, min_periods=1).sum().reset_index(level=0, drop=True)
merged["precip_7d_sum"] = merged.groupby("barangay")["precip"].rolling(7, min_periods=1).sum().reset_index(level=0, drop=True)

# Add temporal features
merged["month"] = merged["time"].dt.month
merged["day_of_year"] = merged["time"].dt.dayofyear
merged["weekday"] = merged["time"].dt.weekday

# ------------------------------
# 10. Save merged dataset
# ------------------------------
merged.to_csv("angeles_barangay_rainfall_discharge.csv", index=False)
print("✅ Saved merged dataset to 'angeles_barangay_rainfall_discharge.csv'")

# ------------------------------
# 11. Quick plot (rainfall + discharge)
# ------------------------------
bgy_to_plot = "Balibago"
df_plot = merged[merged["barangay"] == bgy_to_plot]

fig, ax1 = plt.subplots(figsize=(12,5))

ax1.set_title(f"Rainfall & River Discharge - {bgy_to_plot}")
ax1.set_xlabel("Date")
ax1.set_ylabel("Rainfall (mm)", color="blue")
ax1.plot(df_plot["time"], df_plot["precip"], color="blue", label="Rainfall")
ax1.tick_params(axis="y", labelcolor="blue")

ax2 = ax1.twinx()
ax2.set_ylabel("River Discharge (m³/s)", color="green")
ax2.plot(df_plot["time"], df_plot["river_discharge"], color="green", label="Discharge")
ax2.tick_params(axis="y", labelcolor="green")

fig.tight_layout()
plt.show()
