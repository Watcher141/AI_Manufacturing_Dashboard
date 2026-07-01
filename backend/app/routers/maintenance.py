"""Predictive Maintenance API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
import pandas as pd

from app.database import get_db
from app.models.equipment import Equipment, SensorReading
from app.models.alert import MaintenanceLog
from app.ml.predictive_maintenance import PredictiveMaintenanceModel

router = APIRouter(prefix="/api/maintenance", tags=["Predictive Maintenance"])

# Load ML model
maintenance_model = PredictiveMaintenanceModel()
maintenance_model.load_models()


@router.get("/predictions")
async def get_all_predictions(db: AsyncSession = Depends(get_db)):
    """Get failure predictions for all equipment."""
    result = await db.execute(select(Equipment).order_by(Equipment.name))
    equipment_list = result.scalars().all()

    predictions = []
    for equip in equipment_list:
        readings_result = await db.execute(
            select(SensorReading)
            .where(SensorReading.equipment_id == equip.id)
            .order_by(desc(SensorReading.timestamp))
            .limit(50)
        )
        readings = readings_result.scalars().all()

        if readings:
            df = pd.DataFrame([{
                "temperature": r.temperature, "vibration": r.vibration,
                "pressure": r.pressure, "rpm": r.rpm,
                "power_consumption": r.power_consumption,
            } for r in readings])

            anomaly = maintenance_model.predict_anomaly(df)
            failure = maintenance_model.predict_failure(df)
            health = maintenance_model.calculate_health_score(df)
        else:
            anomaly = {"anomaly_score": 0, "is_anomaly": False}
            failure = {"failure_probability": 0, "predicted_type": "none", "estimated_ttf_hours": None}
            health = equip.health_score

        predictions.append({
            "equipment_id": equip.id,
            "name": equip.name,
            "type": equip.type,
            "status": equip.status,
            "health_score": health,
            "anomaly_score": anomaly["anomaly_score"],
            "is_anomaly": anomaly.get("is_anomaly", False),
            "failure_probability": failure["failure_probability"],
            "predicted_failure_type": failure["predicted_type"],
            "estimated_ttf_hours": failure.get("estimated_ttf_hours"),
        })

    return predictions


@router.get("/predictions/{equipment_id}")
async def get_equipment_prediction(equipment_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed prediction for specific equipment."""
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equip = result.scalar_one_or_none()
    if not equip:
        return {"error": "Equipment not found"}

    readings_result = await db.execute(
        select(SensorReading)
        .where(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(100)
    )
    readings = readings_result.scalars().all()

    if not readings:
        return {"equipment_id": equipment_id, "message": "No sensor data available"}

    df = pd.DataFrame([{
        "temperature": r.temperature, "vibration": r.vibration,
        "pressure": r.pressure, "rpm": r.rpm,
        "power_consumption": r.power_consumption,
    } for r in readings])

    anomaly = maintenance_model.predict_anomaly(df)
    failure = maintenance_model.predict_failure(df)
    health = maintenance_model.calculate_health_score(df)

    return {
        "equipment_id": equip.id,
        "name": equip.name,
        "type": equip.type,
        "health_score": health,
        "anomaly": anomaly,
        "failure": failure,
        "latest_reading": {
            "timestamp": readings[0].timestamp.isoformat(),
            "temperature": readings[0].temperature,
            "vibration": readings[0].vibration,
            "pressure": readings[0].pressure,
            "rpm": readings[0].rpm,
            "power_consumption": readings[0].power_consumption,
        },
    }


@router.get("/health-scores")
async def get_health_scores(db: AsyncSession = Depends(get_db)):
    """Get health scores for all equipment."""
    result = await db.execute(select(Equipment).order_by(Equipment.name))
    equipment = result.scalars().all()

    scores = []
    for eq in equipment:
        scores.append({
            "equipment_id": eq.id,
            "name": eq.name,
            "type": eq.type,
            "health_score": eq.health_score,
            "status": eq.status,
        })

    return scores


@router.get("/schedule")
async def get_maintenance_schedule(db: AsyncSession = Depends(get_db)):
    """Get recommended maintenance schedule."""
    predictions = await get_all_predictions(db)

    schedule = []
    for pred in predictions:
        if pred["failure_probability"] > 0.3 or pred["health_score"] < 70:
            urgency = "immediate" if pred["failure_probability"] > 0.7 else (
                "high" if pred["failure_probability"] > 0.5 else "moderate"
            )
            schedule.append({
                "equipment_id": pred["equipment_id"],
                "name": pred["name"],
                "type": pred["type"],
                "health_score": pred["health_score"],
                "failure_probability": pred["failure_probability"],
                "predicted_failure_type": pred["predicted_failure_type"],
                "urgency": urgency,
                "recommended_date": (
                    datetime.utcnow() + timedelta(hours=max(2, pred.get("estimated_ttf_hours") or 48) * 0.5)
                ).isoformat(),
                "estimated_downtime_hours": round(2 + pred["failure_probability"] * 6, 1),
            })

    return sorted(schedule, key=lambda x: x["failure_probability"], reverse=True)


@router.get("/logs")
async def get_maintenance_logs(
    equipment_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    """Get maintenance history."""
    query = select(MaintenanceLog).order_by(desc(MaintenanceLog.performed_at))
    if equipment_id:
        query = query.where(MaintenanceLog.equipment_id == equipment_id)

    result = await db.execute(query.limit(50))
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "equipment_id": log.equipment_id,
            "maintenance_type": log.maintenance_type,
            "performed_at": log.performed_at.isoformat(),
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
            "technician": log.technician,
            "description": log.description,
            "parts_replaced": log.parts_replaced,
            "cost": log.cost,
            "notes": log.notes,
        }
        for log in logs
    ]
