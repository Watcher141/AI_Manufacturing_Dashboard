"""Analytics data API router for charts."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models.equipment import Equipment, SensorReading
from app.models.defect import DefectRecord
from app.models.alert import MaintenanceLog

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/sensor-trends")
async def get_sensor_trends(
    equipment_id: int = None,
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Get sensor data aggregated for charts."""
    since = datetime.utcnow() - timedelta(hours=hours)

    query = select(SensorReading).where(SensorReading.timestamp >= since)
    if equipment_id:
        query = query.where(SensorReading.equipment_id == equipment_id)

    query = query.order_by(SensorReading.timestamp)
    result = await db.execute(query)
    readings = result.scalars().all()

    # Group by equipment
    grouped = {}
    for r in readings:
        if r.equipment_id not in grouped:
            grouped[r.equipment_id] = []
        grouped[r.equipment_id].append({
            "timestamp": r.timestamp.isoformat(),
            "temperature": r.temperature,
            "vibration": r.vibration,
            "pressure": r.pressure,
            "rpm": r.rpm,
            "power_consumption": r.power_consumption,
        })

    # Get equipment names
    equip_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_result.scalars().all()}

    trends = []
    for eid, data in grouped.items():
        # Downsample to max 100 points for chart performance
        step = max(1, len(data) // 100)
        sampled = data[::step]

        trends.append({
            "equipment_id": eid,
            "equipment_name": equip_map.get(eid, f"Equipment-{eid}"),
            "data": sampled,
        })

    return trends


@router.get("/defect-trends")
async def get_defect_trends(
    days: int = Query(default=30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get defect counts grouped by day and type."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(DefectRecord)
        .where(DefectRecord.timestamp >= since)
        .order_by(DefectRecord.timestamp)
    )
    defects = result.scalars().all()

    # Group by date
    daily = {}
    for d in defects:
        date_key = d.timestamp.strftime("%Y-%m-%d")
        if date_key not in daily:
            daily[date_key] = {"date": date_key, "total": 0}
        daily[date_key]["total"] += 1
        daily[date_key][d.defect_type] = daily[date_key].get(d.defect_type, 0) + 1

    return sorted(daily.values(), key=lambda x: x["date"])


@router.get("/maintenance-costs")
async def get_maintenance_costs(db: AsyncSession = Depends(get_db)):
    """Get maintenance cost analytics."""
    result = await db.execute(select(MaintenanceLog).order_by(MaintenanceLog.performed_at))
    logs = result.scalars().all()

    equip_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_result.scalars().all()}

    total_cost = sum(log.cost or 0 for log in logs)

    by_equipment = {}
    by_type = {}
    monthly = {}

    for log in logs:
        ename = equip_map.get(log.equipment_id, f"Equip-{log.equipment_id}")
        by_equipment[ename] = by_equipment.get(ename, 0) + (log.cost or 0)

        by_type[log.maintenance_type] = by_type.get(log.maintenance_type, 0) + (log.cost or 0)

        month_key = log.performed_at.strftime("%Y-%m")
        if month_key not in monthly:
            monthly[month_key] = {"month": month_key, "cost": 0, "count": 0}
        monthly[month_key]["cost"] += log.cost or 0
        monthly[month_key]["count"] += 1

    return {
        "total_cost": round(total_cost, 2),
        "by_equipment": {k: round(v, 2) for k, v in sorted(by_equipment.items(), key=lambda x: -x[1])[:10]},
        "by_type": {k: round(v, 2) for k, v in by_type.items()},
        "monthly_trend": sorted(monthly.values(), key=lambda x: x["month"]),
    }


@router.get("/oee")
async def get_oee(db: AsyncSession = Depends(get_db)):
    """Get Overall Equipment Effectiveness breakdown."""
    equip_result = await db.execute(select(Equipment))
    equipment = equip_result.scalars().all()

    total = len(equipment)
    operational = sum(1 for eq in equipment if eq.status == "operational")

    # Availability = operational / total
    availability = operational / max(total, 1)

    # Performance (simulated based on health scores)
    avg_health = sum(eq.health_score for eq in equipment) / max(total, 1)
    performance = avg_health / 100

    # Quality (based on defect rate)
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    defect_count = await db.execute(
        select(func.count(DefectRecord.id)).where(DefectRecord.timestamp >= week_ago)
    )
    defects = defect_count.scalar_one()
    quality = max(0.5, 1 - (defects / max(total * 50, 1)))

    oee = availability * performance * quality

    return {
        "overall": round(oee * 100, 1),
        "availability": round(availability * 100, 1),
        "performance": round(performance * 100, 1),
        "quality": round(quality * 100, 1),
        "trend": [],  # Would be populated from historical data
    }
