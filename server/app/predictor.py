import joblib
import pandas as pd
import warnings
from flask import current_app

# Suppress irrelevant sklearn warnings
warnings.filterwarnings("ignore", message="X has feature names")

# --- Load models & data ONCE when the app starts ---
try:
    # Use current_app.config to get paths from config.py
    kmeans = joblib.load(current_app.config['KMEANS_MODEL_PATH'])
    iso = joblib.load(current_app.config['ISO_MODEL_PATH'])
    scaler = joblib.load(current_app.config['SCALER_PATH'])
    barangays_df = pd.read_csv(current_app.config['BARANGAY_CSV_PATH'])
    
    # Load config maps
    anomaly_map = current_app.config['ANOMALY_MAP']
    risk_map = current_app.config['RISK_MAP']

except FileNotFoundError as e:
    print(f"FATAL ERROR: Model or CSV file not found. {e}")
    print("Please ensure 'models/' and 'csv/' directories are in the root.")
    # In a real app, you might want to exit or use fallback models
    kmeans, iso, scaler, barangays_df = None, None, None, pd.DataFrame()
    anomaly_map, risk_map = {}, {}
except Exception as e:
    print(f"Error loading models or data: {e}")
    raise e

# --- Functions to be called by other services ---

def get_barangays():
    """Returns the pre-loaded DataFrame of barangays."""
    return barangays_df

def run_prediction(weather_data: dict) -> dict:
    """
    Runs the ML prediction on a single row of weather data.
    """
    if not all([kmeans, iso, scaler]):
        return {"error": "Models not loaded"}
        
    # --- 1. Feature Engineering ---
    df = pd.DataFrame([weather_data])
    df["precip_lag1"] = df["precip"]
    df["precip_lag2"] = df["precip"]
    df["month"] = df["time"].dt.month
    df["day_of_year"] = df["time"].dt.dayofyear
    df["weekday"] = df["time"].dt.weekday

    # Define the features our model expects
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
    
    # Rename columns to match what the scaler/model was trained on
    X_input = X_input.rename(columns={
        "precip": "precip_weighted",
        "precip_3d_sum": "precip_3d_sum_weighted",
        "precip_7d_sum": "precip_7d_sum_weighted",
        "river_discharge": "river_discharge_weighted",
    })

    # --- 2. Scaling ---
    try:
        X_scaled = scaler.transform(X_input)
    except Exception as e:
        print("⚠️ Scaling failed:", e)
        X_scaled = X_input.values # Fallback

    # --- 3. Prediction ---
    cluster = int(kmeans.predict(X_scaled)[0])
    anomaly = int(iso.predict(X_scaled)[0])

    # --- 4. Mapping Labels ---
    anomaly_label = anomaly_map.get(anomaly, "Unknown")
    risk_label = risk_map.get(cluster, "Unknown")

    return {
        "risk_cluster": cluster,
        "risk_label": risk_label,
        "anomaly": anomaly,
        "anomaly_label": anomaly_label,
        "message": f"Current flood status: {anomaly_label}. Risk level: {risk_label}."
    }