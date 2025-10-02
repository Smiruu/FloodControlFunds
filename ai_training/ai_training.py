import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# ------------------------------
# 1. Load dataset
# ------------------------------
df = pd.read_csv("../dataset/csv/angeles_barangay_rainfall_discharge.csv", parse_dates=["time"])

# ------------------------------
# 2. Features & preprocessing
# ------------------------------
df["month"] = df["time"].dt.month
df["day_of_year"] = df["time"].dt.dayofyear
df["weekday"] = df["time"].dt.weekday
df.fillna(0, inplace=True)

feature_cols = [
    "precip", "river_discharge",
    "precip_lag1", "precip_lag2",
    "precip_3d_sum", "precip_7d_sum",
    "month", "day_of_year", "weekday"
]

X = df[feature_cols]

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ==============================
# 3. KMeans Clustering (Flood Risk Levels)
# ==============================
kmeans = KMeans(n_clusters=3, random_state=42)  # 3 clusters = Low, Medium, High risk
df["flood_risk_cluster"] = kmeans.fit_predict(X_scaled)

# Save model + scaler
joblib.dump(kmeans, "models/flood_kmeans.pkl")
joblib.dump(scaler, "models/flood_scaler.pkl")

print("✅ KMeans clustering complete. Risk clusters saved.")

# Visualize cluster distribution
plt.figure(figsize=(6,4))
sns.countplot(x="flood_risk_cluster", data=df, palette="viridis")
plt.title("Flood Risk Clusters (KMeans)")
plt.xlabel("Cluster (0=Low, 1=Medium, 2=High)")
plt.ylabel("Count")
plt.show()

# ==============================
# 4. Isolation Forest (Anomaly Detection)
# ==============================
iso = IsolationForest(contamination=0.05, random_state=42)  # top 5% as anomalies
df["anomaly"] = iso.fit_predict(X_scaled)  # -1 = anomaly, 1 = normal
df["anomaly_score"] = iso.decision_function(X_scaled)

# Save anomaly model
joblib.dump(iso, "models/flood_isolationforest.pkl")

print("✅ IsolationForest anomaly detection complete.")

# Visualize anomaly points over time
plt.figure(figsize=(12,5))
plt.plot(df["time"], df["precip"], label="Rainfall (mm)", color="blue")
plt.scatter(df[df["anomaly"]==-1]["time"], df[df["anomaly"]==-1]["precip"],
            color="red", label="Anomaly (Potential Flood)", marker="x")
plt.title("Rainfall with Anomaly Detection")
plt.xlabel("Time")
plt.ylabel("Rainfall (mm)")
plt.legend()
plt.show()

# ------------------------------
# 5. Save enhanced dataset
# ------------------------------
df.to_csv("../dataset/csv/angeles_barangay_risk.csv", index=False)
print("✅ Enhanced dataset saved with flood_risk_cluster + anomaly columns")
