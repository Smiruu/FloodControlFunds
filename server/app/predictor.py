import pandas as pd
import warnings
from flask import current_app # This is safe to import

# Suppress irrelevant sklearn warnings
warnings.filterwarnings("ignore", message="X has feature names")

# --- Functions to be called by other services ---

def get_barangays():
    """Returns the pre-loaded DataFrame of barangays."""
    # Get the DF from the app config where it was loaded
    return current_app.config['BARANGAYS_DF']

def run_prediction(weather_data: dict) -> dict:
    """
    Runs the ML prediction on a single row of weather data.
    """
    # --- 1. Get pre-loaded models from app config ---
    kmeans = current_app.config['KMEANS_MODEL']
    iso = current_app.config['ISO_MODEL']
    scaler = current_app.config['SCALER']
    anomaly_map = current_app.config['ANOMALY_MAP']
    risk_map = current_app.config['RISK_MAP']
    
    if not all([kmeans, iso, scaler]):
        print("--- [ERROR] Prediction called, but models are not loaded. ---")
        return {"error": "Models not loaded. Check server logs."}
        
    # --- 2. Feature Engineering ---
    df = pd.DataFrame([weather_data])
    
    # Convert 'time' string from JSON to datetime object
    try:
        df['time'] = pd.to_datetime(df['time'])
    except Exception as e:
        print(f"--- [ERROR] Could not convert 'time' column to datetime: {e} ---")
        return {"error": "Invalid time format in weather_data"}

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

    # --- 3. Scaling ---
    try:
        X_scaled = scaler.transform(X_input)
    except Exception as e:
        print(f"--- [ERROR] Scaling failed: {e} ---")
        return {"error": f"Scaling failed: {e}. Check input data."}

    # --- 4. Prediction ---
    cluster = int(kmeans.predict(X_scaled)[0])
    anomaly = int(iso.predict(X_scaled)[0])

    # --- 5. Mapping Labels ---
    anomaly_label = anomaly_map.get(anomaly, "Unknown")
    risk_label = risk_map.get(cluster, "Unknown")

    return {
        "risk_cluster": cluster,
        "risk_label": risk_label,
        "anomaly": anomaly,
        "anomaly_label": anomaly_label,
        "message": f"Current flood status: {anomaly_label}. Risk level: {risk_label}."
    }