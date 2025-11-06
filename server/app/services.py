import pandas as pd
import warnings
from flask import current_app
from .openmeteo import get_all_openmeteo_data # Import the new async fetcher

# Suppress irrelevant sklearn warnings
warnings.filterwarnings("ignore", message="X has feature names")

# --- Main Orchestration Service ---

async def get_all_predictions() -> pd.DataFrame:
    """
    Orchestrates the full prediction process:
    1. Fetches all barangay data.
    2. Fetches all weather data CONCURRENTLY.
    3. Runs ONE batch prediction.
    """
    # 1. Get the pre-loaded barangay df
    barangays_df = get_barangays() 
    if barangays_df.empty:
        return pd.DataFrame() # Return empty if models didn't load

    # 2. Fetch all weather data IN PARALLEL
    # This now takes ~1-2 seconds instead of 80+
    weather_data_list = await get_all_openmeteo_data(barangays_df)
    
    # 3. Convert weather data to a DataFrame for batch prediction
    weather_df = pd.DataFrame(weather_data_list)
    
    # 4. Run ONE batch prediction
    print("--- [INFO] Running batch prediction... ---")
    predictions_df = run_prediction_batch(weather_df)
    print("--- [INFO] Batch prediction complete. ---")

    # 5. Combine all data for the final response
    # Reset index to safely join barangays_df (loc) + weather_df (raw) + predictions_df (ml)
    barangays_df.reset_index(drop=True, inplace=True)
    weather_df.reset_index(drop=True, inplace=True)
    predictions_df.reset_index(drop=True, inplace=True)

    final_df = pd.concat([barangays_df, weather_df, predictions_df], axis=1)
    
    # Convert datetime to string for JSON serialization
    final_df['time'] = final_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return final_df

# --- Helper functions ---

def get_barangays():
    """Returns the pre-loaded DataFrame of barangays."""
    # Get the DF from the app config where it was loaded
    df = current_app.config.get('BARANGAYS_DF')
    if df is None:
        print("--- [ERROR] BARANGAYS_DF not found in app config.")
        return pd.DataFrame()
    return df

def run_prediction_batch(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the ML prediction on a BATCH of weather data.
    (This is your function from the previous message)
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
    df = weather_df.copy() 
    df['time'] = pd.to_datetime(df['time'])

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
    results_df.fillna("Unknown", inplace=True)
    
    return results_df