import os
import joblib
import pandas as pd
import warnings
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# --- Suppress warnings ---
warnings.filterwarnings("ignore", message="X has feature names")

def create_app(config_class='config.Config'):
    
    app = Flask(__name__)
    app.config.from_object(config_class) 

    # --- CORS CONFIG ---
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    print(f"--- [INFO] Configuring CORS for origin: {frontend_url} ---")
    CORS(app, 
         origins=[frontend_url],
         supports_credentials=True
    )

    # --- LOAD MODELS *INSIDE* create_app ---
    print("--- [INFO] Loading models and data... ---")
    try:
        # Load models and store them in the app's config
        app.config['KMEANS_MODEL'] = joblib.load(app.config['KMEANS_MODEL_PATH'])
        app.config['ISO_MODEL'] = joblib.load(app.config['ISO_MODEL_PATH'])
        app.config['SCALER'] = joblib.load(app.config['SCALER_PATH'])
        app.config['BARANGAYS_DF'] = pd.read_csv(app.config['BARANGAY_CSV_PATH'])
        
        
        
        print("--- [INFO] Models and data loaded successfully. ---")
        
    except FileNotFoundError as e:
        print(f"--- [FATAL ERROR] Model/CSV file not found: {e} ---")
        print("--- [FATAL ERROR] Please check config.py paths and ensure files are deployed. ---")
        
        app.config['KMEANS_MODEL'] = None
        app.config['ISO_MODEL'] = None
        app.config['SCALER'] = None
        app.config['BARANGAYS_DF'] = pd.DataFrame()
    except Exception as e:
        print(f"--- [FATAL ERROR] A critical error occurred loading models: {e} ---")
        raise e
    # --- END MODEL LOADING ---

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.main_bp)

    return app