import requests
from datetime import datetime, timezone

def get_openmeteo_data(lat: float, lon: float) -> dict:
    """Fetch rainfall, weather conditions, and river discharge data from Open-Meteo APIs."""
    
    # --- 1️⃣ Weather & Rainfall (past 7 days) ---
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

    # --- 2️⃣ River Discharge (Flood API) ---
    river_url = (
        f"https://flood-api.open-meteo.com/v1/flood?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=river_discharge"
        f"&timezone=Asia/Manila"
    )

    try:
        precip_res = requests.get(precip_url, timeout=10).json()
        river_res = requests.get(river_url, timeout=10).json()
    except Exception as e:
        print("⚠️ Error fetching Open-Meteo data:", e)
        # Return a default structure on failure
        return {
            "time": datetime.now(timezone.utc),
            "precip": 0, "precip_3d_sum": 0, "precip_7d_sum": 0,
            "river_discharge": 0,
            "temp_max": 0, "temp_min": 0,
            "humidity": 0, "pressure": 0, "windspeed": 0,
            "precip_prob": 0
        }

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
        "time": datetime.now(timezone.utc),
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