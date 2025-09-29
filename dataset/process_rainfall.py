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

# Check which barangays were found
print("\n📌 Barangays found in shapefile:")
print(angeles_bgy["NAME_3"].value_counts())
print(f"Total barangays found: {len(angeles_bgy)}\n")

# Optional: buffer small polygons to avoid NoDataInBounds
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
# 6. Combine all barangay data and save
# ------------------------------
if results:
    df_all = pd.concat(results, ignore_index=True)
    df_all.to_csv("angeles_barangay_daily_rainfall.csv", index=False)
    print("✅ Saved barangay-level daily rainfall to 'angeles_barangay_daily_rainfall.csv'")
else:
    print("❌ No data processed. CSV not created.")

# ------------------------------
# 7. Quick plot for one barangay
# ------------------------------
bgy_to_plot = "Balibago"
if results:
    df_plot = df_all[df_all["barangay"] == bgy_to_plot]
    df_plot.plot(x="time", y="precip", figsize=(12,5), title=f"Daily Rainfall - {bgy_to_plot}")
    plt.ylabel("Rainfall (mm)")
    plt.show()
