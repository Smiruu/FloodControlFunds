from .openmeteo import get_openmeteo_data
from .predictor import get_barangays, run_prediction

def get_all_predictions() -> list:
    """
    Orchestrates the full prediction process for all barangays.
    """
    results = []
    barangays = get_barangays() # Get the pre-loaded df

    for _, row in barangays.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        
        # 1. Fetch data from external API
        weather = get_openmeteo_data(lat, lon)
        
        # 2. Run internal ML prediction
        prediction = run_prediction(weather)
        
        # 3. Combine all data for the final response
        final_result = {
            "barangay": row["barangay"],
            "lat": lat,
            "lon": lon,
            "time": weather["time"].strftime("%Y-%m-%d %H:%M:%S"),
            
            # Unpack the raw weather data
            **weather,
            
            # Unpack the prediction results
            **prediction
        }
        results.append(final_result)
        
    return results