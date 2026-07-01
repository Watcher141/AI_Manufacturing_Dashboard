"""Train all ML models using seeded database data."""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.database import SyncSessionLocal
from app.models.equipment import Equipment, SensorReading
from app.ml.predictive_maintenance import PredictiveMaintenanceModel
from app.ml.defect_detection import DefectDetectionModel
from app.ml.inventory_forecasting import InventoryForecastModel

import random


def train_predictive_maintenance():
    """Train anomaly detection and failure prediction models."""
    print("\n═══ Training Predictive Maintenance Models ═══")

    session = SyncSessionLocal()
    model = PredictiveMaintenanceModel()

    try:
        # Fetch all sensor readings
        readings = session.query(SensorReading).order_by(SensorReading.timestamp).all()
        if not readings:
            print("  ⚠ No sensor readings found. Run seed_data.py first.")
            return

        df = pd.DataFrame([{
            "temperature": r.temperature,
            "vibration": r.vibration,
            "pressure": r.pressure,
            "rpm": r.rpm,
            "power_consumption": r.power_consumption,
        } for r in readings])

        print(f"  → {len(df)} sensor readings loaded")

        # Train anomaly model on all data (assumes mostly normal)
        model.train_anomaly_model(df)
        print("  ✓ Anomaly detection model trained (IsolationForest)")

        # Generate synthetic failure labels for training
        # Label based on anomaly scores: high vibration + high temp = failure scenarios
        labels = []
        failure_types = ["bearing_failure", "overheating", "pressure_leak", "motor_fault", "normal"]

        for _, row in df.iterrows():
            if row["vibration"] > 4.0 and row["temperature"] > 70:
                labels.append("bearing_failure")
            elif row["temperature"] > 80:
                labels.append("overheating")
            elif row["pressure"] < 30 or row["pressure"] > 1800:
                labels.append("pressure_leak")
            elif row["power_consumption"] > 45:
                labels.append("motor_fault")
            else:
                labels.append("normal")

        labels = pd.Series(labels)
        label_dist = labels.value_counts()
        print(f"  → Label distribution: {dict(label_dist)}")

        accuracy = model.train_failure_model(df, labels)
        print(f"  ✓ Failure prediction model trained (RandomForest) — Accuracy: {accuracy:.3f}")

        # Quick test
        test_data = df.tail(20)
        health = model.calculate_health_score(test_data)
        anomaly = model.predict_anomaly(test_data)
        failure = model.predict_failure(test_data)
        print(f"  → Test health score: {health}")
        print(f"  → Test anomaly score: {anomaly['anomaly_score']}")
        print(f"  → Test failure prediction: {failure['predicted_type']} ({failure['failure_probability']:.3f})")

    finally:
        session.close()


def train_defect_detection():
    """Train defect detection model using synthetic data derived from sensor readings."""
    print("\n═══ Training Defect Detection Model ═══")

    session = SyncSessionLocal()
    model = DefectDetectionModel()

    try:
        equipment_list = session.query(Equipment).all()
        readings = session.query(SensorReading).all()

        if not readings:
            print("  ⚠ No sensor readings found.")
            return

        # Group readings by equipment
        readings_by_equip = {}
        for r in readings:
            readings_by_equip.setdefault(r.equipment_id, []).append(r)

        # Create training samples by windowing sensor data
        sensor_groups = []
        labels = []
        defect_types = ["no_defect", "crack", "corrosion", "misalignment", "surface_scratch", "deformation", "overheating"]

        for equip in equipment_list:
            equip_readings = readings_by_equip.get(equip.id, [])
            if len(equip_readings) < 20:
                continue

            df = pd.DataFrame([{
                "temperature": r.temperature,
                "vibration": r.vibration,
                "pressure": r.pressure,
                "rpm": r.rpm,
                "power_consumption": r.power_consumption,
            } for r in equip_readings])

            # Create windows of 20 readings
            window_size = 20
            for start in range(0, len(df) - window_size, window_size):
                window = df.iloc[start:start + window_size]
                sensor_groups.append(window)

                # Label based on sensor patterns
                avg_vib = window["vibration"].mean()
                avg_temp = window["temperature"].mean()
                temp_std = window["temperature"].std()
                vib_std = window["vibration"].std()

                if avg_vib > 3.5 and vib_std > 1.0:
                    labels.append("crack")
                elif avg_temp > 75 and temp_std > 5:
                    labels.append("overheating")
                elif avg_vib > 2.5 and avg_temp > 60:
                    labels.append("misalignment")
                elif vib_std > 1.5:
                    labels.append("deformation")
                elif avg_temp > 50 and window["pressure"].std() > 15:
                    labels.append("corrosion")
                elif avg_vib > 2.0:
                    labels.append("surface_scratch")
                else:
                    labels.append("no_defect")

        print(f"  → {len(sensor_groups)} training samples created")
        print(f"  → Label distribution: {pd.Series(labels).value_counts().to_dict()}")

        result = model.train(sensor_groups, labels)
        print(f"  ✓ Defect detection model trained (GradientBoosting) — Accuracy: {result['accuracy']:.3f}")

    finally:
        session.close()


def train_inventory_forecasting():
    """Train inventory demand forecasting model."""
    print("\n═══ Training Inventory Forecasting Model ═══")

    model = InventoryForecastModel()

    # Generate synthetic historical demand data (90 days)
    now = datetime.utcnow()
    dates = [now - timedelta(days=d) for d in range(90, 0, -1)]

    # Simulate demand with weekly seasonality and trend
    base_demand = 15
    demands = []
    for i, date in enumerate(dates):
        # Weekly cycle
        weekly = 5 * np.sin(2 * np.pi * date.weekday() / 7)
        # Slight upward trend
        trend = i * 0.05
        # Random noise
        noise = np.random.normal(0, 3)
        demand = max(0, base_demand + weekly + trend + noise)
        demands.append(round(demand, 1))

    df = pd.DataFrame({"date": dates, "demand": demands})
    print(f"  → {len(df)} days of historical demand data generated")

    result = model.train(df)
    print(f"  ✓ Inventory forecast model trained (GradientBoosting)")
    print(f"  → MAE: {result['mae']:.2f}, R²: {result['r2']:.3f}")

    # Test forecast
    forecasts = model.forecast(df, horizon_days=7)
    print(f"  → 7-day forecast sample:")
    for f in forecasts[:3]:
        print(f"    {f['date'][:10]}: {f['predicted_demand']:.1f} [{f['confidence_lower']:.1f} – {f['confidence_upper']:.1f}]")


def train_all():
    """Train all ML models."""
    print("🤖 Starting ML model training...")
    print("=" * 50)

    train_predictive_maintenance()
    train_defect_detection()
    train_inventory_forecasting()

    print("\n" + "=" * 50)
    print("🎉 All models trained successfully!")


if __name__ == "__main__":
    train_all()
