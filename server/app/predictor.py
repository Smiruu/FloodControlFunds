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

def run_prediction_batch(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the ML prediction on a BATCH of weather data.
    """
    # 1. Get pre-loaded models from app config
    kmeans = current_app.config['KMEANS_MODEL']
    iso = current_app.config['ISO_MODEL']
    scaler = current_app.config['SCALER']
    anomaly_map = current_app.config['ANOMALY_MAP']
    risk_map = current_app.config['RISK_MAP']
    
    if not all([kmeans, iso, scaler]):
        raise Exception("Models are not loaded. Check server logs.")
        
    # --- 2. Feature Engineering (on the whole DataFrame) ---
    # Make a copy to avoid warnings
    df = weather_df.copy() 
    
    # Convert 'time' string from JSON to datetime object
    df['time'] = pd.to_datetime(df['time'])

    # These operations are now vectorized (super fast)
    df["precip_lag1"] = df["precip"]
    df["precip_lag2"] = df["precip"]
    df["month"] = df["time"].dt.month
    df["day_of_year"] = df["time"].dt.dayofyear
    df["weekday"] = df["time"].dt.weekday

    X_input = df[
        [
            "precip", "river_discharge", "precip_lag1", "precip_lag2",
            "precip_3d_sum", "precip_7d_sum", "month", "day_of_year", "weekday",
        ]
    ]
    
    X_input = X_input.rename(columns={
        "precip": "precip_weighted",
        "precip_3d_sum": "precip_3d_sum_weighted",
        "precip_7d_sum": "precip_7d_sum_weighted",
        "river_discharge": "river_discharge_weighted",
    })

    # --- 3. Scaling (on the whole batch) ---
    X_scaled = scaler.transform(X_input)

    # --- 4. Prediction (on the whole batch) ---
    clusters = kmeans.predict(X_scaled)
    anomalies = iso.predict(X_scaled)

    # --- 5. Mapping Labels (vectorized) ---
    results_df = pd.DataFrame({
        'risk_cluster': clusters,
        'anomaly': anomalies
    })
    
    results_df['risk_label'] = results_df['risk_cluster'].map(risk_map)
    results_df['anomaly_label'] = results_df['anomaly'].map(anomaly_map)
    
    # Fill any missing labels
    results_df.fillna("Unknown", inplace=True)
    
    return results_df