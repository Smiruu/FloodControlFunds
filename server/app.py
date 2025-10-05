from flask import Flask, jsonify
import os
import pandas as pd
import joblib
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask_cors import CORS
import warnings

# Suppress irrelevant sklearn warnings
warnings.filterwarnings("ignore", message="X has feature names")

# ------------------------------
# Setup
# ------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app)

# ------------------------------
# Load models & scaler
# ------------------------------
MODEL_DIR = "../ai_training/models"
kmeans = joblib.load(os.path.join(MODEL_DIR, "flood_kmeans.pkl"))
iso = joblib.load(os.path.join(MODEL_DIR, "flood_isolationforest.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "flood_scaler.pkl"))

# ------------------------------
# Config
# ------------------------------
anomaly_map = {-1: "Potential Flood", 1: "Normal"}
risk_map = {0: "Low", 1: "Medium", 2: "High"}

barangays_df = pd.read_csv("./csv/angeles_barangay_info_corrected_full.csv")

# ------------------------------
# Open-Meteo Rainfall Fetcher
# ------------------------------
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
        # extra weather info (for frontend only)
        "temp_max": temp_max,
        "temp_min": temp_min,
        "humidity": humidity,
        "pressure": pressure,
        "windspeed": windspeed,
        "precip_prob": precip_prob,
    }


# ------------------------------
# Prediction Endpoint
# ------------------------------
@app.route("/predict_all", methods=["GET"])
def predict_all():
    results = []

    for _, row in barangays_df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        weather = get_openmeteo_data(lat, lon)

        df = pd.DataFrame([weather])
        df["precip_lag1"] = df["precip"]
        df["precip_lag2"] = df["precip"]
        df["month"] = df["time"].dt.month
        df["day_of_year"] = df["time"].dt.dayofyear
        df["weekday"] = df["time"].dt.weekday

        
        X_input = df[
            [
                "precip",
                "river_discharge",
                "precip_lag1",
                "precip_lag2",
                "precip_3d_sum",
                "precip_7d_sum",
                "month",
                "day_of_year",
                "weekday",
            ]
        ]

        X_input = X_input.rename(columns={
    "precip": "precip_weighted",
    "precip_3d_sum": "precip_3d_sum_weighted",
    "precip_7d_sum": "precip_7d_sum_weighted",
    "river_discharge": "river_discharge_weighted",
})
        # Apply scaler
        try:
            X_scaled = scaler.transform(X_input)
        except Exception as e:
            print("⚠️ Scaling failed:", e)
            X_scaled = X_input.values

        # Predict
        cluster = int(kmeans.predict(X_scaled)[0])
        anomaly = int(iso.predict(X_scaled)[0])

        anomaly_label = anomaly_map.get(anomaly, "Unknown")
        risk_label = risk_map.get(cluster, "Unknown")

        results.append({
    "barangay": row["barangay"],
    "lat": lat,
    "lon": lon,
    "time": weather["time"].strftime("%Y-%m-%d %H:%M:%S"),
    "precip": weather["precip"],
    "precip_3d_sum": weather["precip_3d_sum"],
    "precip_7d_sum": weather["precip_7d_sum"],
    "river_discharge": weather["river_discharge"],
    "temp_max": weather["temp_max"],
    "temp_min": weather["temp_min"],
    "humidity": weather["humidity"],
    "pressure": weather["pressure"],
    "windspeed": weather["windspeed"],
    "precip_prob": weather["precip_prob"],
    "risk_cluster": cluster,
    "risk_label": risk_label,
    "anomaly": anomaly,
    "anomaly_label": anomaly_label,
    "message": f"Current flood status: {anomaly_label}. Risk level: {risk_label}."
})

    return jsonify(results)

# ------------------------------
# Run Server
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
