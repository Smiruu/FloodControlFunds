import pandas as pd

# ------------------------------
# 1. Load your existing CSV
# ------------------------------
df = pd.read_csv("angeles_barangay_daily_rainfall.csv", parse_dates=["time"])

# ------------------------------
# 2. Sort values
# ------------------------------
df = df.sort_values(["barangay", "time"]).reset_index(drop=True)

# ------------------------------
# 3. Create rolling sums (cumulative rainfall)
# ------------------------------
df["precip_3d_sum"] = df.groupby("barangay")["precip"].rolling(3).sum().reset_index(0, drop=True)
df["precip_7d_sum"] = df.groupby("barangay")["precip"].rolling(7).sum().reset_index(0, drop=True)

# ------------------------------
# 4. Create lag features
# ------------------------------
df["precip_lag1"] = df.groupby("barangay")["precip"].shift(1)
df["precip_lag2"] = df.groupby("barangay")["precip"].shift(2)

# ------------------------------
# 5. Add seasonal features
# ------------------------------
df["month"] = df["time"].dt.month
df["day_of_year"] = df["time"].dt.dayofyear
df["weekday"] = df["time"].dt.weekday  # Monday=0, Sunday=6

# ------------------------------
# 6. Define flood-prone barangays
# ------------------------------
flood_prone_bgy = [
    "Tabun",
    "Sapalibutad",           # fixed from "Sapang Libutad"
    "Pulungbulu",
    "Capaya",
    "Pulung Cacutud",
    "Balibago",
    "Pulung Maragul",
    "Pampang",
    "San Nicolas",
    "Lourdes Sur",
    "Lourdes Sur East",
    "Lourdes North West",
    "Santa Teresita",
    "Santa Trinidad",
    "Cutcut",
    "Malabanias",
    "Amsic",
    "Claro M. Recto",
    "Salapungan",
    "Santo Cristo",
    "Agapito del Rosario",   # capitalization fixed
    "Santo Rosario",
    "Santo Domingo",
    "Pandan"
]

# ------------------------------
# 7. Generate proxy flood occurrence
# ------------------------------
rain_threshold = 100  # mm in 3-day sum, adjust as needed

df["flood_occurrence"] = (
    (df["barangay"].isin(flood_prone_bgy)) &
    (df["precip_3d_sum"] > rain_threshold)
).astype(int)

# Optional: mark if barangay is flood-prone
df["is_flood_prone"] = df["barangay"].isin(flood_prone_bgy).astype(int)

# ------------------------------
# 8. Save prepared CSV
# ------------------------------
df.to_csv("angeles_barangay_features_proxy.csv", index=False)
print("✅ Saved dataset with proxy flood labels: 'angeles_barangay_features_proxy.csv'")
