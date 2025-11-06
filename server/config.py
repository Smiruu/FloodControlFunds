import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    
    MODEL_DIR = os.path.join(BASE_DIR, "models")
    CSV_DIR = os.path.join(BASE_DIR, "csv")

    # --- Model & Scaler Paths ---
    KMEANS_MODEL_PATH = os.path.join(MODEL_DIR, "flood_kmeans.pkl")
    ISO_MODEL_PATH = os.path.join(MODEL_DIR, "flood_isolationforest.pkl")
    SCALER_PATH = os.path.join(MODEL_DIR, "flood_scaler.pkl")

    # --- Data Path ---
    BARANGAY_CSV_PATH = os.path.join(CSV_DIR, "angeles_barangay_info_corrected_full.csv")

    # --- Prediction Maps ---
    ANOMALY_MAP = {-1: "Potential Flood", 1: "Normal"}
    RISK_MAP = {0: "Low", 1: "Medium", 2: "High"}