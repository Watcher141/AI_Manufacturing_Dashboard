"""Equipment CRUD + sensor data API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.equipment import Equipment, SensorReading
from app.models.defect import DefectRecord
from app.models.alert import Alert
from app.schemas.equipment import (
    EquipmentResponse, EquipmentDetailResponse, SensorReadingCreate, SensorReadingResponse
)

router = APIRouter(prefix="/api/equipment", tags=["Equipment"])


@router.get("")
async def list_equipment(
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all equipment with optional filters."""
    query = select(Equipment)
    if status:
        query = query.where(Equipment.status == status)
    if type:
        query = query.where(Equipment.type == type)

    result = await db.execute(query.order_by(Equipment.name))
    equipment = result.scalars().all()

    return [
        {
            "id": eq.id, "name": eq.name, "type": eq.type,
            "location": eq.location, "status": eq.status,
            "health_score": eq.health_score, "manufacturer": eq.manufacturer,
            "model_number": eq.model_number,
            "install_date": eq.install_date.isoformat() if eq.install_date else None,
            "last_maintenance": eq.last_maintenance.isoformat() if eq.last_maintenance else None,
        }
        for eq in equipment
    ]


@router.get("/types")
async def get_equipment_types(db: AsyncSession = Depends(get_db)):
    """Get distinct equipment types."""
    result = await db.execute(select(Equipment.type).distinct())
    return [row[0] for row in result.all()]


@router.get("/{equipment_id}")
async def get_equipment_detail(equipment_id: int, db: AsyncSession = Depends(get_db)):
    """Get equipment detail with latest readings."""
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Latest 10 sensor readings
    readings_result = await db.execute(
        select(SensorReading)
        .where(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(10)
    )
    readings = readings_result.scalars().all()

    # Counts
    res_alert_count = await db.execute(
        select(func.count(Alert.id)).where(Alert.equipment_id == equipment_id)
    )
    alert_count_val = res_alert_count.scalar_one()

    res_defect_count = await db.execute(
        select(func.count(DefectRecord.id)).where(
            DefectRecord.equipment_id == equipment_id, DefectRecord.is_resolved == False
        )
    )
    defect_count_val = res_defect_count.scalar_one()

    return {
        "id": equipment.id, "name": equipment.name, "type": equipment.type,
        "location": equipment.location, "status": equipment.status,
        "health_score": equipment.health_score, "manufacturer": equipment.manufacturer,
        "model_number": equipment.model_number,
        "install_date": equipment.install_date.isoformat() if equipment.install_date else None,
        "last_maintenance": equipment.last_maintenance.isoformat() if equipment.last_maintenance else None,
        "alert_count": alert_count_val,
        "defect_count": defect_count_val,
        "latest_readings": [
            {
                "id": r.id, "timestamp": r.timestamp.isoformat(),
                "temperature": r.temperature, "vibration": r.vibration,
                "pressure": r.pressure, "rpm": r.rpm,
                "power_consumption": r.power_consumption,
                "humidity": r.humidity, "noise_level": r.noise_level,
            }
            for r in readings
        ],
    }


@router.get("/{equipment_id}/sensors")
async def get_sensor_history(
    equipment_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Get historical sensor data for charts."""
    since = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.equipment_id == equipment_id, SensorReading.timestamp >= since)
        .order_by(SensorReading.timestamp)
    )
    readings = result.scalars().all()

    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "temperature": r.temperature, "vibration": r.vibration,
            "pressure": r.pressure, "rpm": r.rpm,
            "power_consumption": r.power_consumption,
            "humidity": r.humidity, "noise_level": r.noise_level,
        }
        for r in readings
    ]


@router.post("/{equipment_id}/readings")
async def add_sensor_reading(
    equipment_id: int,
    reading: SensorReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a new sensor reading."""
    equipment = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    if not equipment.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Equipment not found")

    new_reading = SensorReading(
        equipment_id=equipment_id,
        timestamp=reading.timestamp or datetime.utcnow(),
        temperature=reading.temperature,
        vibration=reading.vibration,
        pressure=reading.pressure,
        rpm=reading.rpm,
        power_consumption=reading.power_consumption,
        humidity=reading.humidity,
        noise_level=reading.noise_level,
    )
    db.add(new_reading)
    await db.flush()

    return {"id": new_reading.id, "status": "created"}
