import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests

# ------------------------------
# 1. File paths
# ------------------------------
shapefile_path = Path("ph_polygon/gadm41_PHL_3.shp")

# ------------------------------
# 2. Load shapefile
# ------------------------------
gdf = gpd.read_file(shapefile_path).to_crs("EPSG:4326")

# ------------------------------
# 3. Filter Angeles City barangays
# ------------------------------
angeles_bgy = gdf[gdf["NAME_2"] == "Angeles City"].copy()

# ------------------------------
# 4. Compute centroid coordinates
# ------------------------------
angeles_bgy["centroid"] = angeles_bgy.geometry.centroid
angeles_bgy["latitude"] = angeles_bgy.centroid.y
angeles_bgy["longitude"] = angeles_bgy.centroid.x

# ------------------------------
# 5. Batch fetch elevations
# ------------------------------
coords = "|".join([f"{lat},{lon}" for lat, lon in zip(angeles_bgy["latitude"], angeles_bgy["longitude"])])
url = "https://api.open-elevation.com/api/v1/lookup"

try:
    response = requests.get(url, params={"locations": coords}, timeout=30)  # longer timeout
    if response.status_code == 200:
        results = response.json()["results"]
        angeles_bgy["elevation"] = [r["elevation"] for r in results]
    else:
        print(f"⚠️ API error: {response.status_code}")
        angeles_bgy["elevation"] = None
except Exception as e:
    print(f"⚠️ Failed batch fetch: {e}")
    angeles_bgy["elevation"] = None

# ------------------------------
# 6. Static values
# ------------------------------
angeles_bgy["timezone"] = "Asia/Manila"
angeles_bgy["start_date"] = "2020-01-01"
angeles_bgy["end_date"] = "2025-12-31"

# ------------------------------
# 7. Save to CSV
# ------------------------------
df_out = angeles_bgy[["NAME_3", "latitude", "longitude", "elevation", "timezone", "start_date", "end_date"]]
df_out.rename(columns={"NAME_3": "barangay"}, inplace=True)

df_out.to_csv("angeles_barangay_info.csv", index=False)
print("✅ Saved barangay info with elevation to 'angeles_barangay_info.csv'")
print(df_out.head())
