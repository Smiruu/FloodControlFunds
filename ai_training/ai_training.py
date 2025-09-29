import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# ------------------------------
# 1. Load dataset
# ------------------------------
df = pd.read_csv("../dataset/angeles_barangay_features_proxy.csv", parse_dates=["time"])

# ------------------------------
# 2. Ensure rolling/lags exist
# ------------------------------
# If not already in CSV, uncomment:
# df["precip_3d_sum"] = df.groupby("barangay")["precip"].rolling(3).sum().reset_index(0, drop=True)
# df["precip_7d_sum"] = df.groupby("barangay")["precip"].rolling(7).sum().reset_index(0, drop=True)
# df["precip_lag1"] = df.groupby("barangay")["precip"].shift(1)
# df["precip_lag2"] = df.groupby("barangay")["precip"].shift(2)

# Seasonal features
df["month"] = df["time"].dt.month
df["day_of_year"] = df["time"].dt.dayofyear
df["weekday"] = df["time"].dt.weekday

# Fill missing lag values
df.fillna(0, inplace=True)

# ------------------------------
# 3. Features and target
# ------------------------------
feature_cols = [
    "precip", "precip_3d_sum", "precip_7d_sum",
    "precip_lag1", "precip_lag2",
    "month", "day_of_year", "weekday",
    "is_flood_prone"
]
X = df[feature_cols]
y = df["flood_occurrence"]

# ------------------------------
# 4. Train/test split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ------------------------------
# 5. RandomForest
# ------------------------------
rf_clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)
rf_clf.fit(X_train, y_train)
y_pred_rf = rf_clf.predict(X_test)
print("\n=== RandomForest ===")
print("Accuracy:", accuracy_score(y_test, y_pred_rf))
print(classification_report(y_test, y_pred_rf))

joblib.dump(rf_clf, "flood_rf_model.pkl")

# ------------------------------
# 6. XGBoost
# ------------------------------
xgb_clf = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric="logloss"
)
xgb_clf.fit(X_train, y_train)
y_pred_xgb = xgb_clf.predict(X_test)
print("\n=== XGBoost ===")
print("Accuracy:", accuracy_score(y_test, y_pred_xgb))
print(classification_report(y_test, y_pred_xgb))

joblib.dump(xgb_clf, "flood_xgb_model.pkl")

# ------------------------------
# 7. MLP Classifier
# ------------------------------
mlp_clf = MLPClassifier(
    hidden_layer_sizes=(64,32),
    max_iter=500,
    random_state=42
)
mlp_clf.fit(X_train, y_train)
y_pred_mlp = mlp_clf.predict(X_test)
print("\n=== MLP Classifier ===")
print("Accuracy:", accuracy_score(y_test, y_pred_mlp))
print(classification_report(y_test, y_pred_mlp))

joblib.dump(mlp_clf, "flood_mlp_model.pkl")

print("\n✅ All models trained and saved: flood_rf_model.pkl, flood_xgb_model.pkl, flood_mlp_model.pkl")
