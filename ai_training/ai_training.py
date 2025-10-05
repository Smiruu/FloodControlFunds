import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

# ------------------------------
# 1. Load dataset
# ------------------------------
df = pd.read_csv("../dataset/csv/angeles_barangay_rainfall_discharge.csv", parse_dates=["time"])

# ------------------------------
# 2. Preprocessing
# ------------------------------
df["month"] = df["time"].dt.month
df["day_of_year"] = df["time"].dt.dayofyear
df["weekday"] = df["time"].dt.weekday
df.fillna(0, inplace=True)

# ------------------------------
# 3. Feature weighting (emphasize rainfall & discharge)
# ------------------------------
df["precip_weighted"] = df["precip"] * 3          # Strongly influence rainfall
df["river_discharge_weighted"] = df["river_discharge"] * 2
df["precip_3d_sum_weighted"] = df["precip_3d_sum"] * 2
df["precip_7d_sum_weighted"] = df["precip_7d_sum"] * 2

feature_cols = [
    "precip_weighted", "river_discharge_weighted",
    "precip_lag1", "precip_lag2",
    "precip_3d_sum_weighted", "precip_7d_sum_weighted",
    "month", "day_of_year", "weekday"
]

X = df[feature_cols]

# ------------------------------
# 4. Standardize
# ------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ------------------------------
# 5. KMeans with smarter initialization
# ------------------------------
# We'll use "k-means++" init for better centroid separation
kmeans = KMeans(n_clusters=3, init="k-means++", random_state=42)
df["flood_risk_cluster"] = kmeans.fit_predict(X_scaled)

# Assign readable labels by comparing cluster means
cluster_means = df.groupby("flood_risk_cluster")[["precip", "river_discharge"]].mean().sort_values("precip")
risk_labels = {cluster: label for cluster, label in zip(cluster_means.index, ["Low", "Medium", "High"])}
df["risk_label"] = df["flood_risk_cluster"].map(risk_labels)

# Save model + scaler
joblib.dump(kmeans, "models/flood_kmeans.pkl")
joblib.dump(scaler, "models/flood_scaler.pkl")

print("✅ KMeans clustering complete with clearer separation.")

# Visualize
plt.figure(figsize=(6,4))
sns.countplot(x="risk_label", data=df, palette="viridis", order=["Low", "Medium", "High"])
plt.title("Flood Risk Clusters (KMeans)")
plt.xlabel("Risk Level")
plt.ylabel("Count")
plt.show()

# ------------------------------
# 6. Isolation Forest (Anomalies)
# ------------------------------
iso = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = iso.fit_predict(X_scaled)
df["anomaly_score"] = iso.decision_function(X_scaled)

joblib.dump(iso, "models/flood_isolationforest.pkl")

print("✅ IsolationForest anomaly detection complete.")

# Visualize anomalies
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
# 7. Save enhanced dataset
# ------------------------------
df.to_csv("../dataset/csv/angeles_barangay_risk.csv", index=False)
print("✅ Enhanced dataset saved with risk_label + anomaly columns")
