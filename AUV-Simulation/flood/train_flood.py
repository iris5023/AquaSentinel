import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ==========================================
# 1. LOAD DATASET
# ==========================================

data = pd.read_csv("flood_risk_dataset_india.csv")

print("Dataset loaded:", data.shape)


# ==========================================
# 2. CREATE DERIVED FLOOD-RISK TARGET
# ==========================================
# We are keeping the original dataset unchanged.
# The new target is derived from environmental
# conditions already present in the dataset.

def calculate_risk(row):

    score = 0

    # Rainfall
    if row["Rainfall (mm)"] >= 200:
        score += 2
    elif row["Rainfall (mm)"] >= 120:
        score += 1

    # River discharge
    if row["River Discharge (m³/s)"] >= 3500:
        score += 2
    elif row["River Discharge (m³/s)"] >= 2000:
        score += 1

    # Water level
    if row["Water Level (m)"] >= 7:
        score += 2
    elif row["Water Level (m)"] >= 4:
        score += 1

    # Humidity
    if row["Humidity (%)"] >= 75:
        score += 1

    # Elevation
    if row["Elevation (m)"] < 1000:
        score += 2
    elif row["Elevation (m)"] < 3000:
        score += 1

    # Historical floods
    if row["Historical Floods"] >= 1:
        score += 2

    # Convert score into risk class
    if score >= 7:
        return 2       # HIGH
    elif score >= 4:
        return 1       # MEDIUM
    else:
        return 0       # LOW


data["Flood Risk"] = data.apply(
    calculate_risk,
    axis=1
)


# ==========================================
# 3. FEATURES
# ==========================================

features = [
    "Latitude",
    "Longitude",
    "Rainfall (mm)",
    "Temperature (°C)",
    "Humidity (%)",
    "River Discharge (m³/s)",
    "Water Level (m)",
    "Elevation (m)",
    "Population Density",
    "Historical Floods"
]

X = data[features]

y = data["Flood Risk"]


# ==========================================
# 4. CHECK RISK DISTRIBUTION
# ==========================================

print("\nFlood Risk Distribution:")

print(
    y.value_counts()
    .sort_index()
    .rename({
        0: "LOW",
        1: "MEDIUM",
        2: "HIGH"
    })
)


# ==========================================
# 5. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# 6. TRAIN RANDOM FOREST
# ==========================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train,
    y_train
)


# ==========================================
# 7. PREDICTION
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 8. EVALUATION
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n================================")
print("FLOOD ML RESULTS")
print("================================")

print(
    "Accuracy:",
    round(accuracy * 100, 2),
    "%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "LOW",
            "MEDIUM",
            "HIGH"
        ]
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ==========================================
# 9. FEATURE IMPORTANCE
# ==========================================

print("\nFeature Importance:")

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print(importance.to_string(index=False))


# ==========================================
# 10. SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "flood_model.pkl"
)

print("\nModel saved as flood_model.pkl")


# ==========================================
# 11. SAVE FEATURE LIST
# ==========================================

joblib.dump(
    features,
    "flood_features.pkl"
)

print("Features saved as flood_features.pkl")


# ==========================================
# 12. SAVE RISK LABELS
# ==========================================

risk_labels = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH"
}

joblib.dump(
    risk_labels,
    "flood_labels.pkl"
)

print("Risk labels saved as flood_labels.pkl")

print("\nFlood ML training completed successfully.")