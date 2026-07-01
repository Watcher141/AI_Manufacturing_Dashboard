"""Defect Detection ML Module.

GradientBoosting classifier for multi-class defect classification
from engineered sensor features.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os
from typing import Dict, Optional, List


DEFECT_CLASSES = ["no_defect", "crack", "corrosion", "misalignment", "surface_scratch", "deformation", "overheating"]

# Equipment criticality weights
CRITICALITY_WEIGHTS = {
    "CNC Machine": 0.9,
    "Robotic Arm": 0.85,
    "Hydraulic Press": 0.8,
    "Industrial Oven": 0.75,
    "Conveyor Belt": 0.6,
}


class DefectDetectionModel:
    """Multi-class defect classification from sensor patterns."""

    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_dir, exist_ok=True)

        self.model: Optional[CalibratedClassifierCV] = None
        self.scaler: Optional[StandardScaler] = None

    def _engineer_features(self, sensor_df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features from sensor data for defect detection."""
        features = {}

        # Basic statistics
        for col in ["temperature", "vibration", "pressure", "power_consumption"]:
            if col in sensor_df.columns:
                features[f"{col}_mean"] = sensor_df[col].mean()
                features[f"{col}_std"] = sensor_df[col].std()
                features[f"{col}_max"] = sensor_df[col].max()
                features[f"{col}_min"] = sensor_df[col].min()
                features[f"{col}_range"] = sensor_df[col].max() - sensor_df[col].min()
                features[f"{col}_skew"] = sensor_df[col].skew()

        # Vibration spectrum (simplified)
        if "vibration" in sensor_df.columns and len(sensor_df) > 1:
            vib = sensor_df["vibration"].values
            features["vib_peak_to_rms"] = np.max(np.abs(vib)) / (np.sqrt(np.mean(vib**2)) + 0.001)
            features["vib_crest_factor"] = np.max(np.abs(vib)) / (np.mean(np.abs(vib)) + 0.001)

        # Temperature deviation patterns
        if "temperature" in sensor_df.columns and len(sensor_df) > 1:
            temp = sensor_df["temperature"].values
            features["temp_trend"] = np.polyfit(range(len(temp)), temp, 1)[0] if len(temp) > 2 else 0
            features["temp_volatility"] = np.std(np.diff(temp)) if len(temp) > 2 else 0

        # Operational cycle proxy
        if "rpm" in sensor_df.columns:
            rpm = sensor_df["rpm"].fillna(0).values
            features["rpm_mean"] = np.mean(rpm)
            features["rpm_variation"] = np.std(rpm)

        # Cross-correlations
        if "temperature" in sensor_df.columns and "vibration" in sensor_df.columns:
            features["temp_vib_corr"] = sensor_df["temperature"].corr(sensor_df["vibration"])
        if "pressure" in sensor_df.columns and "power_consumption" in sensor_df.columns:
            features["pres_power_corr"] = sensor_df["pressure"].corr(sensor_df["power_consumption"])

        # Handle NaN
        features = {k: (0.0 if pd.isna(v) else v) for k, v in features.items()}

        return pd.DataFrame([features])

    def train(self, sensor_data_groups: List[pd.DataFrame], labels: List[str]) -> Dict:
        """Train defect detection model."""
        # Engineer features for each group
        feature_rows = []
        for group in sensor_data_groups:
            features = self._engineer_features(group)
            feature_rows.append(features)

        X = pd.concat(feature_rows, ignore_index=True).fillna(0)
        y = pd.Series(labels)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        # Base classifier
        base_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )

        # Calibrated for proper probability outputs
        self.model = CalibratedClassifierCV(base_model, cv=3)
        self.model.fit(X_train, y_train)

        accuracy = self.model.score(X_test, y_test)
        report = classification_report(y_test, self.model.predict(X_test), output_dict=True, zero_division=0)

        # Save
        joblib.dump(self.model, os.path.join(self.model_dir, "defect_model.joblib"))
        joblib.dump(self.scaler, os.path.join(self.model_dir, "defect_scaler.joblib"))

        return {"accuracy": accuracy, "report": report}

    def load_models(self):
        """Load saved models."""
        model_path = os.path.join(self.model_dir, "defect_model.joblib")
        scaler_path = os.path.join(self.model_dir, "defect_scaler.joblib")

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)

        return self

    def detect(self, sensor_data: pd.DataFrame, equipment_type: str = "CNC Machine") -> Dict:
        """Run defect detection on sensor data window."""
        if self.model is None or self.scaler is None:
            return {"defect_type": "no_defect", "confidence": 0.0, "severity": "low"}

        features = self._engineer_features(sensor_data)
        X_scaled = self.scaler.transform(features.fillna(0))

        probabilities = self.model.predict_proba(X_scaled)[0]
        classes = self.model.classes_

        max_idx = np.argmax(probabilities)
        predicted_class = str(classes[max_idx])
        confidence = float(probabilities[max_idx])

        # Severity assessment
        severity = self._assess_severity(predicted_class, confidence, equipment_type)

        return {
            "defect_type": predicted_class,
            "confidence": round(confidence, 4),
            "severity": severity,
            "all_probabilities": {str(c): round(float(p), 4) for c, p in zip(classes, probabilities)},
        }

    def _assess_severity(self, defect_type: str, confidence: float, equipment_type: str) -> str:
        """Assess defect severity based on type, confidence, and equipment criticality."""
        if defect_type == "no_defect":
            return "low"

        criticality = CRITICALITY_WEIGHTS.get(equipment_type, 0.5)
        severity_score = confidence * criticality

        # Certain defect types are inherently more severe
        type_weights = {
            "crack": 1.3, "deformation": 1.2, "overheating": 1.1,
            "misalignment": 1.0, "corrosion": 0.9, "surface_scratch": 0.7,
        }
        severity_score *= type_weights.get(defect_type, 1.0)

        if severity_score > 0.8:
            return "critical"
        elif severity_score > 0.6:
            return "high"
        elif severity_score > 0.4:
            return "medium"
        return "low"
