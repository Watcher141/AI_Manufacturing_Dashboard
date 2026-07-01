"""Inventory Forecasting ML Module.

GradientBoosting regressor for time-series demand forecasting
with confidence intervals via quantile regression.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class InventoryForecastModel:
    """Time-series demand forecasting using gradient boosting."""

    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_dir, exist_ok=True)

        self.model: Optional[GradientBoostingRegressor] = None
        self.model_upper: Optional[GradientBoostingRegressor] = None
        self.model_lower: Optional[GradientBoostingRegressor] = None
        self.scaler: Optional[StandardScaler] = None

    def _create_time_features(self, dates: pd.Series) -> pd.DataFrame:
        """Create time-based features from dates."""
        features = pd.DataFrame()
        features["day_of_week"] = dates.dt.dayofweek
        features["day_of_month"] = dates.dt.day
        features["month"] = dates.dt.month
        features["quarter"] = dates.dt.quarter
        features["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)
        features["week_of_year"] = dates.dt.isocalendar().week.astype(int)
        features["day_sin"] = np.sin(2 * np.pi * dates.dt.dayofweek / 7)
        features["day_cos"] = np.cos(2 * np.pi * dates.dt.dayofweek / 7)
        features["month_sin"] = np.sin(2 * np.pi * dates.dt.month / 12)
        features["month_cos"] = np.cos(2 * np.pi * dates.dt.month / 12)
        return features

    def _add_lag_features(self, df: pd.DataFrame, demand_col: str = "demand") -> pd.DataFrame:
        """Add lag and rolling features."""
        if demand_col not in df.columns:
            return df

        for lag in [1, 3, 7, 14, 30]:
            df[f"lag_{lag}"] = df[demand_col].shift(lag).fillna(df[demand_col].mean())

        for window in [3, 7, 14]:
            df[f"rolling_mean_{window}"] = df[demand_col].rolling(window=window, min_periods=1).mean()
            df[f"rolling_std_{window}"] = df[demand_col].rolling(window=window, min_periods=1).std().fillna(0)

        return df

    def train(self, historical_demand: pd.DataFrame) -> Dict:
        """
        Train forecasting models.

        Args:
            historical_demand: DataFrame with columns ['date', 'demand']
        """
        df = historical_demand.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        # Create features
        time_features = self._create_time_features(df["date"])
        df = pd.concat([df, time_features], axis=1)
        df = self._add_lag_features(df, "demand")

        # Prepare X, y
        feature_cols = [c for c in df.columns if c not in ["date", "demand"]]
        X = df[feature_cols].fillna(0)
        y = df["demand"]

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, shuffle=False
        )

        # Mean prediction
        self.model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            loss="squared_error", random_state=42
        )
        self.model.fit(X_train, y_train)

        # Upper bound (90th percentile)
        self.model_upper = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            loss="quantile", alpha=0.9, random_state=42
        )
        self.model_upper.fit(X_train, y_train)

        # Lower bound (10th percentile)
        self.model_lower = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            loss="quantile", alpha=0.1, random_state=42
        )
        self.model_lower.fit(X_train, y_train)

        # Evaluate
        from sklearn.metrics import mean_absolute_error, r2_score
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Save
        joblib.dump(self.model, os.path.join(self.model_dir, "forecast_model.joblib"))
        joblib.dump(self.model_upper, os.path.join(self.model_dir, "forecast_upper.joblib"))
        joblib.dump(self.model_lower, os.path.join(self.model_dir, "forecast_lower.joblib"))
        joblib.dump(self.scaler, os.path.join(self.model_dir, "forecast_scaler.joblib"))

        return {"mae": mae, "r2": r2}

    def load_models(self):
        """Load saved models."""
        paths = {
            "model": "forecast_model.joblib",
            "upper": "forecast_upper.joblib",
            "lower": "forecast_lower.joblib",
            "scaler": "forecast_scaler.joblib",
        }
        for attr, filename in paths.items():
            path = os.path.join(self.model_dir, filename)
            if os.path.exists(path):
                setattr(self, f"model_{attr}" if attr != "model" else "model",
                        joblib.load(path) if attr != "scaler" else None)
                if attr == "scaler":
                    self.scaler = joblib.load(path)
                elif attr == "model":
                    self.model = joblib.load(path)
                elif attr == "upper":
                    self.model_upper = joblib.load(path)
                elif attr == "lower":
                    self.model_lower = joblib.load(path)
        return self

    def forecast(self, historical_demand: pd.DataFrame, horizon_days: int = 30) -> List[Dict]:
        """Generate demand forecasts for future dates."""
        if self.model is None or self.scaler is None:
            # Fallback: simple moving average
            avg = historical_demand["demand"].mean() if "demand" in historical_demand.columns else 10
            now = datetime.utcnow()
            return [
                {
                    "date": (now + timedelta(days=d)).isoformat(),
                    "predicted_demand": round(avg + np.random.normal(0, avg * 0.1), 1),
                    "confidence_lower": round(avg * 0.7, 1),
                    "confidence_upper": round(avg * 1.3, 1),
                }
                for d in range(horizon_days)
            ]

        df = historical_demand.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        forecasts = []
        last_date = df["date"].max()

        for d in range(1, horizon_days + 1):
            forecast_date = last_date + timedelta(days=d)
            forecast_series = pd.Series([forecast_date])

            time_features = self._create_time_features(forecast_series)

            # Use last known demand for lag features
            recent_demand = df["demand"].tail(30).tolist()
            lag_features = {}
            for lag in [1, 3, 7, 14, 30]:
                idx = min(lag - 1, len(recent_demand) - 1)
                lag_features[f"lag_{lag}"] = recent_demand[-(idx + 1)] if recent_demand else 0

            for window in [3, 7, 14]:
                window_data = recent_demand[-window:]
                lag_features[f"rolling_mean_{window}"] = np.mean(window_data) if window_data else 0
                lag_features[f"rolling_std_{window}"] = np.std(window_data) if len(window_data) > 1 else 0

            features = pd.concat([time_features, pd.DataFrame([lag_features])], axis=1)
            X_scaled = self.scaler.transform(features.fillna(0))

            pred = max(0, float(self.model.predict(X_scaled)[0]))
            pred_upper = max(pred, float(self.model_upper.predict(X_scaled)[0])) if self.model_upper else pred * 1.3
            pred_lower = max(0, min(pred, float(self.model_lower.predict(X_scaled)[0]))) if self.model_lower else pred * 0.7

            forecasts.append({
                "date": forecast_date.isoformat(),
                "predicted_demand": round(pred, 1),
                "confidence_lower": round(pred_lower, 1),
                "confidence_upper": round(pred_upper, 1),
            })

            # Add predicted value to recent_demand for next iteration
            recent_demand.append(pred)

        return forecasts

    def calculate_reorder_info(self, current_stock: int, lead_time_days: int,
                               forecasts: List[Dict], safety_factor: float = 1.2) -> Dict:
        """Calculate reorder point and recommended order quantity."""
        if not forecasts:
            return {"reorder_needed": False, "days_until_stockout": None, "recommended_qty": 0}

        daily_demands = [f["predicted_demand"] for f in forecasts[:lead_time_days]]
        avg_daily = np.mean(daily_demands) if daily_demands else 0

        # Days until stockout
        cumulative = 0
        days_until_stockout = None
        for i, f in enumerate(forecasts):
            cumulative += f["predicted_demand"]
            if cumulative >= current_stock:
                days_until_stockout = i + 1
                break

        # Reorder point = avg_demand * lead_time * safety_factor
        reorder_point = avg_daily * lead_time_days * safety_factor

        # Recommended order = demand during lead_time + safety stock
        lead_time_demand = sum(daily_demands)
        safety_stock = avg_daily * lead_time_days * (safety_factor - 1)
        recommended_qty = max(0, int(np.ceil(lead_time_demand + safety_stock - current_stock)))

        return {
            "reorder_needed": bool(current_stock <= reorder_point),
            "days_until_stockout": int(days_until_stockout) if days_until_stockout is not None else None,
            "recommended_qty": int(recommended_qty),
            "avg_daily_demand": float(round(avg_daily, 1)),
            "reorder_point": float(round(reorder_point, 0)),
        }
