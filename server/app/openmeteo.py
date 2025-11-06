import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timezone

# --- Main public function ---

async def get_all_openmeteo_data(barangays_df: pd.DataFrame) -> list:
    """
    Fetches Open-Meteo data for ALL barangays in the DataFrame concurrently.
    """
    # Create an aiohttp "session" to share connections
    async with aiohttp.ClientSession() as session:
        # Create a list of "tasks" to run
        tasks = []
        for _, row in barangays_df.iterrows():
            tasks.append(
                # Run _fetch_one_barangay for each row
                _fetch_one_barangay(session, row["latitude"], row["longitude"])
            )
        
        # Run all tasks in parallel and wait for them all to complete
        print(f"--- [INFO] Fetching weather for {len(tasks)} barangays in parallel... ---")
        weather_data_list = await asyncio.gather(*tasks)
        print("--- [INFO] All weather data fetched. ---")
        return weather_data_list

# --- Private helper functions ---

def _get_urls(lat: float, lon: float) -> tuple[str, str]:
    """Helper to generate the API URLs."""
    precip_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&past_days=7"
        f"&daily=precipitation_sum,precipitation_probability_mean,"
        f"temperature_2m_max,temperature_2m_min,"
        f"relative_humidity_2m_max,surface_pressure_max,"
        f"windspeed_10m_max"
        f"&timezone=Asia/Manila"
    )
    river_url = (
        f"https://flood-api.open-meteo.com/v1/flood?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=river_discharge"
        f"&timezone=Asia/Manila"
    )
    return precip_url, river_url

async def _fetch_one_barangay(session: aiohttp.ClientSession, lat: float, lon: float) -> dict:
    """
    Asynchronously fetches data for a SINGLE barangay.
    """
    precip_url, river_url = _get_urls(lat, lon)
    
    try:
        # Make both API calls concurrently FOR THIS ONE BARANGAY
        async with session.get(precip_url, timeout=10) as precip_resp, \
                     session.get(river_url, timeout=10) as river_resp:
            
            precip_resp.raise_for_status() # Raise error if not 200
            river_resp.raise_for_status()   # Raise error if not 200

            precip_res = await precip_resp.json()
            river_res = await river_resp.json()
            
            # If successful, parse the data
            return _parse_meteo_response(precip_res, river_res)
            
    except Exception as e:
        print(f"⚠️ Error fetching Open-Meteo data for ({lat},{lon}): {e}")
        # Return a default structure on failure
        return _get_default_weather_data()

def _parse_meteo_response(precip_res: dict, river_res: dict) -> dict:
    """Parses the successful JSON responses from Open-Meteo."""
    daily = precip_res.get("daily", {})
    precip_list = daily.get("precipitation_sum", [])
    precip_prob_list = daily.get("precipitation_probability_mean", [])
    temp_max_list = daily.get("temperature_2m_max", [])
    temp_min_list = daily.get("temperature_2m_min", [])
    humidity_list = daily.get("relative_humidity_2m_max", [])
    pressure_list = daily.get("surface_pressure_max", [])
    windspeed_list = daily.get("windspeed_10m_max", [])
    discharge_list = river_res.get("daily", {}).get("river_discharge", [])

    # Handle missing values safely
    precip = precip_list[-1] if precip_list else 0
    precip_3d_sum = sum(precip_list[-3:]) if len(precip_list) >= 3 else sum(precip_list)
    precip_7d_sum = sum(precip_list[-7:]) if len(precip_list) >= 7 else sum(precip_list)
    river_discharge = discharge_list[-1] if discharge_list else 0

    # Extra weather info (latest day)
    temp_max = temp_max_list[-1] if temp_max_list else 0
    temp_min = temp_min_list[-1] if temp_min_list else 0
    humidity = humidity_list[-1] if humidity_list else 0
    pressure = pressure_list[-1] if pressure_list else 0
    windspeed = windspeed_list[-1] if windspeed_list else 0
    precip_prob = precip_prob_list[-1] if precip_prob_list else 0

    return {
        "time": datetime.now(timezone.utc), # Use one consistent timestamp
        "precip": precip,
        "precip_3d_sum": precip_3d_sum,
        "precip_7d_sum": precip_7d_sum,
        "river_discharge": river_discharge,
        "temp_max": temp_max,
        "temp_min": temp_min,
        "humidity": humidity,
        "pressure": pressure,
        "windspeed": windspeed,
        "precip_prob": precip_prob,
    }

def _get_default_weather_data() -> dict:
    """Returns a default dict on API failure."""
    return {
        "time": datetime.now(timezone.utc),
        "precip": 0, "precip_3d_sum": 0, "precip_7d_sum": 0,
        "river_discharge": 0,
        "temp_max": 0, "temp_min": 0,
        "humidity": 0, "pressure": 0, "windspeed": 0,
        "precip_prob": 0
    }