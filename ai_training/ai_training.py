import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    roc_curve,
    auc
)
import joblib

# ------------------------------
# 1. Load dataset
# ------------------------------
df = pd.read_csv("../dataset/csv/angeles_barangay_features_proxy.csv", parse_dates=["time"])

# ------------------------------
# 2. Features & preprocessing
# ------------------------------
df["month"] = df["time"].dt.month
df["day_of_year"] = df["time"].dt.dayofyear
df["weekday"] = df["time"].dt.weekday
df.fillna(0, inplace=True)

feature_cols = [
    "precip", "precip_3d_sum", "precip_7d_sum",
    "precip_lag1", "precip_lag2",
    "month", "day_of_year", "weekday",
    "is_flood_prone"
]
X = df[feature_cols]
y = df["flood_occurrence"]

# ------------------------------
# 3. Time-based split
# ------------------------------
# Sort by time
df_sorted = df.sort_values("time").reset_index(drop=True)
split_idx = int(len(df_sorted) * 0.8)  # 80% train, 20% test chronologically

X_train = df_sorted.loc[:split_idx, feature_cols]
y_train = df_sorted.loc[:split_idx, "flood_occurrence"]
X_test  = df_sorted.loc[split_idx+1:, feature_cols]
y_test  = df_sorted.loc[split_idx+1:, "flood_occurrence"]

print("Train size:", X_train.shape, "Test size:", X_test.shape)

# ==============================
# Helper: evaluation + plots
# ==============================
def evaluate_model(name, model, X_test, y_test, y_pred):
    print(f"\n=== {name} ===")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred, digits=4))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["No Flood", "Flood"],
                yticklabels=["No Flood", "Flood"])
    plt.title(f"{name} - Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.show()

    # ROC Curve
    if len(set(y_test)) == 2:
        y_prob = model.predict_proba(X_test)[:,1]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(5,4))
        plt.plot(fpr, tpr, color="blue", label=f"AUC = {roc_auc:.2f}")
        plt.plot([0,1], [0,1], linestyle="--", color="gray")
        plt.title(f"{name} - ROC Curve")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend()
        plt.show()

# ------------------------------
# 4. RandomForest
# ------------------------------
rf_clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)
rf_clf.fit(X_train, y_train)
y_pred_rf = rf_clf.predict(X_test)
evaluate_model("RandomForest", rf_clf, X_test, y_test, y_pred_rf)
joblib.dump(rf_clf, "flood_rf_model.pkl")

# ------------------------------
# 5. XGBoost
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
evaluate_model("XGBoost", xgb_clf, X_test, y_test, y_pred_xgb)
joblib.dump(xgb_clf, "flood_xgb_model.pkl")

# ------------------------------
# 6. MLP Classifier
# ------------------------------
mlp_clf = MLPClassifier(
    hidden_layer_sizes=(64,32),
    max_iter=500,
    random_state=42
)
mlp_clf.fit(X_train, y_train)
y_pred_mlp = mlp_clf.predict(X_test)
evaluate_model("MLP Classifier", mlp_clf, X_test, y_test, y_pred_mlp)
joblib.dump(mlp_clf, "flood_mlp_model.pkl")

print("\n✅ Models trained & evaluated with TIME-BASED split")
