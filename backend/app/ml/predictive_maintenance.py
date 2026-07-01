"""Predictive Maintenance ML Module.

Dual-model system:
1. IsolationForest for anomaly detection on sensor readings
2. RandomForestClassifier for failure prediction
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from typing import Dict, Optional, Tuple


class PredictiveMaintenanceModel:
    """Predictive maintenance using anomaly detection and failure classification."""

    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_dir, exist_ok=True)

        self.anomaly_model: Optional[IsolationForest] = None
        self.failure_model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns = ["temperature", "vibration", "pressure", "power_consumption", "rpm"]

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer features from sensor readings."""
        features = df[self.feature_columns].copy()

        # Fill NaN rpm with 0 (for equipment without RPM sensors)
        features["rpm"] = features["rpm"].fillna(0)

        # Add rolling statistics if enough data
        if len(features) >= 4:
            for col in ["temperature", "vibration", "pressure"]:
                features[f"{col}_rolling_mean_4"] = features[col].rolling(window=4, min_periods=1).mean()
                features[f"{col}_rolling_std_4"] = features[col].rolling(window=4, min_periods=1).std().fillna(0)
                features[f"{col}_rate_of_change"] = features[col].diff().fillna(0)

        # Cross-correlations
        features["temp_vib_ratio"] = features["temperature"] / (features["vibration"] + 0.01)
        features["power_per_rpm"] = features["power_consumption"] / (features["rpm"] + 1)

        return features.fillna(0)

    def train_anomaly_model(self, normal_data: pd.DataFrame):
        """Train IsolationForest on normal operating data."""
        features = self._prepare_features(normal_data)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(features)

        self.anomaly_model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            max_features=0.8,
            random_state=42,
        )
        self.anomaly_model.fit(X_scaled)

        # Save models
        joblib.dump(self.anomaly_model, os.path.join(self.model_dir, "anomaly_model.joblib"))
        joblib.dump(self.scaler, os.path.join(self.model_dir, "scaler.joblib"))

        return self

    def train_failure_model(self, data: pd.DataFrame, labels: pd.Series):
        """Train RandomForest classifier for failure type prediction."""
        features = self._prepare_features(data)

        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(features)
        else:
            X_scaled = self.scaler.transform(features)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, labels, test_size=0.2, random_state=42, stratify=labels
        )

        self.failure_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight="balanced",
        )
        self.failure_model.fit(X_train, y_train)

        accuracy = self.failure_model.score(X_test, y_test)
        joblib.dump(self.failure_model, os.path.join(self.model_dir, "failure_model.joblib"))

        return accuracy

    def load_models(self):
        """Load saved models from disk."""
        anomaly_path = os.path.join(self.model_dir, "anomaly_model.joblib")
        failure_path = os.path.join(self.model_dir, "failure_model.joblib")
        scaler_path = os.path.join(self.model_dir, "scaler.joblib")

        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        if os.path.exists(anomaly_path):
            self.anomaly_model = joblib.load(anomaly_path)
        if os.path.exists(failure_path):
            self.failure_model = joblib.load(failure_path)

        return self

    def predict_anomaly(self, sensor_data: pd.DataFrame) -> Dict:
        """Detect anomalies in sensor readings."""
        if self.anomaly_model is None or self.scaler is None:
            return {"anomaly_score": 0.0, "is_anomaly": False}

        features = self._prepare_features(sensor_data)
        X_scaled = self.scaler.transform(features)

        # Get anomaly scores (-1 = anomaly, 1 = normal)
        scores = self.anomaly_model.decision_function(X_scaled)
        predictions = self.anomaly_model.predict(X_scaled)

        # Normalize score to 0-1 range (higher = more anomalous)
        avg_score = float(np.mean(scores))
        normalized = max(0.0, min(1.0, 0.5 - avg_score))

        return {
            "anomaly_score": round(normalized, 4),
            "is_anomaly": bool(np.any(predictions == -1)),
            "anomaly_count": int(np.sum(predictions == -1)),
            "total_readings": len(sensor_data),
        }

    def predict_failure(self, sensor_data: pd.DataFrame) -> Dict:
        """Predict failure type and probability."""
        if self.failure_model is None or self.scaler is None:
            return {"failure_probability": 0.0, "predicted_type": "none"}

        features = self._prepare_features(sensor_data)
        X_scaled = self.scaler.transform(features)

        # Get probabilities for each failure type
        probabilities = self.failure_model.predict_proba(X_scaled)
        avg_proba = np.mean(probabilities, axis=0)

        classes = self.failure_model.classes_
        max_idx = np.argmax(avg_proba)
        max_prob = float(avg_proba[max_idx])

        # Estimate time to failure based on anomaly progression
        anomaly_result = self.predict_anomaly(sensor_data)
        anomaly_score = anomaly_result["anomaly_score"]

        if anomaly_score > 0.3:
            # Rough TTF estimate: higher anomaly = sooner failure
            ttf_hours = max(2, (1 - anomaly_score) * 168)  # Max ~1 week
        else:
            ttf_hours = None

        return {
            "failure_probability": round(max_prob, 4),
            "predicted_type": str(classes[max_idx]) if max_prob > 0.3 else "none",
            "all_probabilities": {str(c): round(float(p), 4) for c, p in zip(classes, avg_proba)},
            "estimated_ttf_hours": round(ttf_hours, 1) if ttf_hours else None,
        }

    def calculate_health_score(self, sensor_data: pd.DataFrame) -> float:
        """Calculate composite health score (0-100)."""
        if sensor_data.empty:
            return 100.0

        anomaly = self.predict_anomaly(sensor_data)
        failure = self.predict_failure(sensor_data)

        # Composite: 40% anomaly, 40% failure prob, 20% sensor thresholds
        anomaly_component = (1 - anomaly["anomaly_score"]) * 40
        failure_component = (1 - failure["failure_probability"]) * 40

        # Sensor threshold check
        latest = sensor_data.iloc[-1]
        threshold_score = 20.0
        if latest.get("temperature", 0) > 80:
            threshold_score -= 5
        if latest.get("vibration", 0) > 4.0:
            threshold_score -= 5
        if latest.get("pressure", 0) > 1500:
            threshold_score -= 5

        score = anomaly_component + failure_component + max(0, threshold_score)
        return round(max(0, min(100, score)), 1)
