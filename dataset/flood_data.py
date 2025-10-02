import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup Open-Meteo API client with cache + retry
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Load your CSV file (make sure it has: latitude,longitude,elevation,timezone,start_date,end_date)
csv_file = "angeles_barangay_info.csv"
df = pd.read_csv(csv_file)

all_results = []

# Loop through each row in the CSV
for idx, row in df.iterrows():
    print(f"Fetching flood data for {row['latitude']}, {row['longitude']}...")

    url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "daily": "river_discharge",
        "start_date": row["start_date"],
        "end_date": row["end_date"],
        "timezone": row["timezone"]
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Extract daily discharge
    daily = response.Daily()
    daily_river_discharge = daily.Variables(0).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "elevation": response.Elevation(),
        "river_discharge": daily_river_discharge
    }

    df_daily = pd.DataFrame(daily_data)
    all_results.append(df_daily)

# Combine all locations into one DataFrame
final_df = pd.concat(all_results, ignore_index=True)

# Save results
final_df.to_csv("flood_data_results.csv", index=False)
print("✅ Flood data saved to flood_data_results.csv")
