"""Dashboard overview API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.database import get_db
from app.models.equipment import Equipment, SensorReading
from app.models.defect import DefectRecord
from app.models.inventory import InventoryItem
from app.models.alert import Alert
from app.schemas.analytics import DashboardOverviewResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """Get aggregated dashboard KPIs and summary data."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Equipment counts by status
    equip_result = await db.execute(select(Equipment))
    equipment = equip_result.scalars().all()

    total = len(equipment)
    status_counts = {"operational": 0, "warning": 0, "critical": 0, "maintenance": 0, "offline": 0}
    health_scores = []

    for eq in equipment:
        status_counts[eq.status] = status_counts.get(eq.status, 0) + 1
        health_scores.append(eq.health_score)

    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0

    # Defect counts
    res_defects_today = await db.execute(
        select(func.count(DefectRecord.id)).where(DefectRecord.timestamp >= today_start)
    )
    defects_today_count = res_defects_today.scalar_one()

    res_defects_week = await db.execute(
        select(func.count(DefectRecord.id)).where(DefectRecord.timestamp >= week_start)
    )
    defects_week_count = res_defects_week.scalar_one()

    # Alert counts
    res_critical_alerts = await db.execute(
        select(func.count(Alert.id)).where(
            and_(Alert.severity == "critical", Alert.is_dismissed == False)
        )
    )
    critical_alerts_count = res_critical_alerts.scalar_one()

    res_unread_alerts = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_read == False)
    )
    unread_alerts_count = res_unread_alerts.scalar_one()

    # Inventory low stock
    res_low_stock = await db.execute(
        select(func.count(InventoryItem.id)).where(
            InventoryItem.current_stock <= InventoryItem.reorder_point
        )
    )
    low_stock_count = res_low_stock.scalar_one()

    # Recent alerts
    recent_alerts_result = await db.execute(
        select(Alert).order_by(Alert.created_at.desc()).limit(10)
    )
    recent_alerts = recent_alerts_result.scalars().all()

    # Equipment health summary
    health_summary = []
    for eq in equipment[:20]:
        health_summary.append({
            "id": eq.id,
            "name": eq.name,
            "type": eq.type,
            "health_score": eq.health_score,
            "status": eq.status,
        })

    # OEE calculation (simplified)
    availability = status_counts.get("operational", 0) / max(total, 1)
    performance = 0.85  # Simulated
    quality_rate = 1 - (defects_today_count / max(total * 100, 1))
    oee = availability * performance * quality_rate * 100

    return {
        "total_equipment": total,
        "operational_count": status_counts.get("operational", 0),
        "warning_count": status_counts.get("warning", 0),
        "critical_count": status_counts.get("critical", 0),
        "maintenance_count": status_counts.get("maintenance", 0),
        "offline_count": status_counts.get("offline", 0),
        "avg_health_score": round(avg_health, 1),
        "total_defects_today": defects_today_count,
        "total_defects_week": defects_week_count,
        "critical_alerts": critical_alerts_count,
        "unread_alerts": unread_alerts_count,
        "oee_percentage": round(oee, 1),
        "inventory_low_stock": low_stock_count,
        "recent_alerts": [
            {
                "id": a.id,
                "type": a.type,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "is_read": a.is_read,
                "created_at": a.created_at.isoformat(),
            }
            for a in recent_alerts
        ],
        "equipment_health_summary": health_summary,
    }
