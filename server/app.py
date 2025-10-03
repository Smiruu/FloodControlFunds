from flask import Flask, jsonify
import os
import pandas as pd
import joblib
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(app)
# Load models
kmeans = joblib.load("../ai_training/models/flood_kmeans.pkl")
iso = joblib.load("../ai_training/models/flood_isolationforest.pkl")

# Mapping numeric outputs to human-readable labels
anomaly_map = {-1: "Potential Flood", 1: "Normal"}
risk_map = {0: "Low", 1: "Medium", 2: "High"}

# API key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ------------------------------
# Load barangay CSV
# ------------------------------
barangays_df = pd.read_csv("./csv/angeles_barangay_info_corrected_full.csv")  # Your CSV file

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url, timeout=10).json()
    except Exception as e:
        print("Error fetching weather:", e)
        return {"time": datetime.utcnow(), "precip": 0, "river_discharge": 0}

    if "dt" not in res:
        print("OpenWeather API error:", res)
        return {"time": datetime.utcnow(), "precip": 0, "river_discharge": 0}

    precip = 0
    if "rain" in res and "1h" in res["rain"]:
        precip = res["rain"]["1h"]

    return {"time": datetime.utcfromtimestamp(res["dt"]), "precip": precip, "river_discharge": 0}

# ------------------------------
# API Route
# ------------------------------
@app.route("/predict_all", methods=["GET"])
def predict_all():
    results = []

    for _, row in barangays_df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        weather = get_weather(lat, lon)

        # Build input dataframe
        df = pd.DataFrame([weather])
        df["precip_lag1"] = df["precip"]
        df["precip_lag2"] = df["precip"]
        df["precip_3d_sum"] = df["precip"]
        df["precip_7d_sum"] = df["precip"]
        df["month"] = df["time"].dt.month
        df["day_of_year"] = df["time"].dt.dayofyear
        df["weekday"] = df["time"].dt.weekday

        X_input = df[[
            "precip", "river_discharge",
            "precip_lag1", "precip_lag2",
            "precip_3d_sum", "precip_7d_sum",
            "month", "day_of_year", "weekday"
        ]]

        # Run models
        cluster = int(kmeans.predict(X_input)[0])
        anomaly = int(iso.predict(X_input)[0])

        anomaly_label = anomaly_map.get(anomaly, "Unknown")
        risk_label = risk_map.get(cluster, "Unknown")

        results.append({
            "barangay": row["barangay"],
            "lat": lat,
            "lon": lon,
            "time": weather["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "precip": weather["precip"],
            "river_discharge": weather["river_discharge"],
            "risk_cluster": cluster,
            "risk_label": risk_label,
            "anomaly": anomaly,
            "anomaly_label": anomaly_label,
            "message": f"Current flood status: {anomaly_label}. Risk level: {risk_label}."
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
