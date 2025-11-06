from flask import Blueprint, jsonify
from .services import get_all_predictions # Import the new async service
import time

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Flood Control API is running."

@main_bp.route('/predict_all', methods=['GET'])
async def predict_all():
    """
    Async route to get all predictions.
    """
    print("--- [INFO] /predict_all route hit. ---")
    start_time = time.time()
    
    try:
        # Await the new async function
        results_df = await get_all_predictions()
        
        end_time = time.time()
        print(f"--- [INFO] /predict_all finished. Total time: {end_time - start_time:.2f}s ---")
        
        # Convert the final DataFrame to JSON
        return jsonify(results_df.to_dict(orient="records"))
        
    except Exception as e:
        print(f"--- [ERROR] /predict_all route failed: {e} ---")
        return jsonify({"error": str(e)}), 500
