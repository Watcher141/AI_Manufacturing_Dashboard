"""Alert management API router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from typing import Optional

from app.database import get_db
from app.models.alert import Alert
from app.models.equipment import Equipment
from app.auth_deps import require_admin

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("")
async def list_alerts(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    is_read: Optional[bool] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all alerts with filters."""
    query = select(Alert).where(Alert.is_dismissed == False).order_by(desc(Alert.created_at))

    if type:
        query = query.where(Alert.type == type)
    if severity:
        query = query.where(Alert.severity == severity)
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)

    result = await db.execute(query.limit(limit))
    alerts = result.scalars().all()

    equip_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_result.scalars().all()}

    return [
        {
            "id": a.id,
            "type": a.type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "equipment_id": a.equipment_id,
            "equipment_name": equip_map.get(a.equipment_id) if a.equipment_id else None,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.get("/count")
async def get_alert_counts(db: AsyncSession = Depends(get_db)):
    """Get alert count summary."""
    res_total = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_dismissed == False)
    )
    total_val = res_total.scalar_one()

    res_unread = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_read == False, Alert.is_dismissed == False)
    )
    unread_val = res_unread.scalar_one()

    res_critical = await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "critical", Alert.is_dismissed == False)
    )
    critical_val = res_critical.scalar_one()

    res_warning = await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "warning", Alert.is_dismissed == False)
    )
    warning_val = res_warning.scalar_one()

    res_info = await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "info", Alert.is_dismissed == False)
    )
    info_val = res_info.scalar_one()

    return {
        "total": total_val,
        "unread": unread_val,
        "critical": critical_val,
        "warning": warning_val,
        "info": info_val,
    }


@router.patch("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Mark an alert as read."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_read = True
    await db.flush()
    return {"id": alert_id, "status": "read"}


@router.patch("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Mark all alerts as read."""
    await db.execute(update(Alert).where(Alert.is_read == False).values(is_read=True))
    await db.flush()
    return {"status": "all_read"}


@router.patch("/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Dismiss an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_dismissed = True
    await db.flush()
    return {"id": alert_id, "status": "dismissed"}
