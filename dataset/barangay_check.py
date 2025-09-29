import geopandas as gpd

# Load shapefile
shapefile = "ph_polygon/gadm41_PHL_3.shp"
gdf = gpd.read_file(shapefile).to_crs("EPSG:4326")

# Filter to Angeles City
angeles_bgy = gdf[gdf["NAME_2"] == "Angeles City"]

# Check the barangays
print(angeles_bgy["NAME_3"].value_counts())
print(f"Total barangays found: {len(angeles_bgy)}")
