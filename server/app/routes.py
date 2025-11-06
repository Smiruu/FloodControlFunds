from flask import jsonify, Blueprint
from .services import get_all_predictions

# Create a "Blueprint", which is a way to organize a group of routes
main_bp = Blueprint('main', __name__)

@main_bp.route("/predict_all", methods=["GET"])
def predict_all():
    """
    API endpoint to fetch predictions for all barangays.
    """
    try:
        # Call the service layer to do all the work
        results = get_all_predictions()
        return jsonify(results)
    
    except Exception as e:
        # Add error handling for your endpoint
        print(f"🔴 Unhandled error in /predict_all endpoint: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500