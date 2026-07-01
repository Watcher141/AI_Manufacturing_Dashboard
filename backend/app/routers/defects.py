"""Defect Detection API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta
import pandas as pd

from app.database import get_db
from app.models.equipment import Equipment, SensorReading
from app.models.defect import DefectRecord
from app.ml.defect_detection import DefectDetectionModel

router = APIRouter(prefix="/api/defects", tags=["Defect Detection"])

# Load ML model
defect_model = DefectDetectionModel()
defect_model.load_models()


@router.get("")
async def list_defects(
    severity: str = None,
    defect_type: str = None,
    is_resolved: bool = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all detected defects with filters."""
    query = select(DefectRecord).order_by(desc(DefectRecord.timestamp))

    if severity:
        query = query.where(DefectRecord.severity == severity)
    if defect_type:
        query = query.where(DefectRecord.defect_type == defect_type)
    if is_resolved is not None:
        query = query.where(DefectRecord.is_resolved == is_resolved)

    result = await db.execute(query.limit(limit))
    defects = result.scalars().all()

    # Get equipment names
    equip_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_result.scalars().all()}

    return [
        {
            "id": d.id,
            "equipment_id": d.equipment_id,
            "equipment_name": equip_map.get(d.equipment_id, "Unknown"),
            "timestamp": d.timestamp.isoformat(),
            "defect_type": d.defect_type,
            "severity": d.severity,
            "confidence_score": d.confidence_score,
            "description": d.description,
            "is_resolved": d.is_resolved,
            "resolved_at": d.resolved_at.isoformat() if d.resolved_at else None,
            "detected_by": d.detected_by,
        }
        for d in defects
    ]


@router.get("/stats")
async def get_defect_stats(db: AsyncSession = Depends(get_db)):
    """Get defect statistics."""
    total = await db.execute(select(func.count(DefectRecord.id)))
    total_count = total.scalar_one()

    # By severity
    severity_counts = {}
    for sev in ["critical", "high", "medium", "low"]:
        count = await db.execute(
            select(func.count(DefectRecord.id)).where(DefectRecord.severity == sev)
        )
        severity_counts[sev] = count.scalar_one()

    # Resolved / unresolved
    resolved = await db.execute(
        select(func.count(DefectRecord.id)).where(DefectRecord.is_resolved == True)
    )
    resolved_count = resolved.scalar_one()
    unresolved_count = total_count - resolved_count

    # By type
    type_results = await db.execute(
        select(DefectRecord.defect_type, func.count(DefectRecord.id))
        .group_by(DefectRecord.defect_type)
    )
    by_type = {row[0]: row[1] for row in type_results.all()}

    # By equipment
    equip_results = await db.execute(
        select(DefectRecord.equipment_id, func.count(DefectRecord.id))
        .group_by(DefectRecord.equipment_id)
        .order_by(desc(func.count(DefectRecord.id)))
        .limit(10)
    )
    equip_map_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_map_result.scalars().all()}
    by_equipment = {equip_map.get(row[0], f"Equip-{row[0]}"): row[1] for row in equip_results.all()}

    return {
        "total_defects": total_count,
        "critical_count": severity_counts.get("critical", 0),
        "high_count": severity_counts.get("high", 0),
        "medium_count": severity_counts.get("medium", 0),
        "low_count": severity_counts.get("low", 0),
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "resolution_rate": round(resolved_count / max(total_count, 1) * 100, 1),
        "by_type": by_type,
        "by_equipment": by_equipment,
    }


@router.post("/detect")
async def run_defect_detection(
    equipment_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    """Run defect detection on latest sensor data."""
    if equipment_id:
        equip_result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
        equipment_list = [equip_result.scalar_one_or_none()]
        if not equipment_list[0]:
            return {"error": "Equipment not found"}
    else:
        result = await db.execute(select(Equipment))
        equipment_list = result.scalars().all()

    results = []
    for equip in equipment_list:
        readings_result = await db.execute(
            select(SensorReading)
            .where(SensorReading.equipment_id == equip.id)
            .order_by(desc(SensorReading.timestamp))
            .limit(20)
        )
        readings = readings_result.scalars().all()

        if not readings:
            continue

        df = pd.DataFrame([{
            "temperature": r.temperature, "vibration": r.vibration,
            "pressure": r.pressure, "rpm": r.rpm,
            "power_consumption": r.power_consumption,
        } for r in readings])

        detection = defect_model.detect(df, equip.type)
        results.append({
            "equipment_id": equip.id,
            "equipment_name": equip.name,
            **detection,
        })

    return results


@router.patch("/{defect_id}/resolve")
async def resolve_defect(defect_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a defect as resolved."""
    result = await db.execute(select(DefectRecord).where(DefectRecord.id == defect_id))
    defect = result.scalar_one_or_none()

    if not defect:
        return {"error": "Defect not found"}

    defect.is_resolved = True
    defect.resolved_at = datetime.utcnow()
    await db.flush()

    return {"id": defect_id, "status": "resolved"}
