"""Inventory Forecasting API router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.database import get_db
from app.models.inventory import InventoryItem, ForecastRecord
from app.ml.inventory_forecasting import InventoryForecastModel

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

# Load ML model
forecast_model = InventoryForecastModel()
forecast_model.load_models()


@router.get("")
async def list_inventory(
    category: str = None,
    db: AsyncSession = Depends(get_db),
):
    """List all inventory items with stock status."""
    query = select(InventoryItem).order_by(InventoryItem.name)
    if category:
        query = query.where(InventoryItem.category == category)

    result = await db.execute(query)
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "category": item.category,
            "current_stock": item.current_stock,
            "min_stock": item.min_stock,
            "max_stock": item.max_stock,
            "reorder_point": item.reorder_point,
            "unit_cost": item.unit_cost,
            "lead_time_days": item.lead_time_days,
            "supplier": item.supplier,
            "location": item.location,
            "last_restocked": item.last_restocked.isoformat() if item.last_restocked else None,
            "stock_status": (
                "critical" if item.current_stock <= item.min_stock else
                "low" if item.current_stock <= item.reorder_point else
                "healthy"
            ),
            "stock_value": round(item.current_stock * item.unit_cost, 2),
        }
        for item in items
    ]


@router.get("/overview")
async def get_inventory_overview(db: AsyncSession = Depends(get_db)):
    """Get inventory overview statistics."""
    result = await db.execute(select(InventoryItem))
    items = result.scalars().all()

    total_value = sum(item.current_stock * item.unit_cost for item in items)
    low_stock = sum(1 for item in items if item.current_stock <= item.reorder_point)
    critical_stock = sum(1 for item in items if item.current_stock <= item.min_stock)
    reorder_pending = sum(1 for item in items if item.current_stock <= item.reorder_point)

    categories = {}
    for item in items:
        cat = item.category
        if cat not in categories:
            categories[cat] = {"count": 0, "value": 0}
        categories[cat]["count"] += 1
        categories[cat]["value"] += round(item.current_stock * item.unit_cost, 2)

    return {
        "total_items": len(items),
        "total_value": round(total_value, 2),
        "low_stock_count": low_stock,
        "critical_stock_count": critical_stock,
        "reorder_pending_count": reorder_pending,
        "categories": categories,
    }


@router.get("/{item_id}/forecast")
async def get_item_forecast(
    item_id: int,
    horizon: int = Query(default=30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get demand forecast for a specific item."""
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return {"error": "Item not found"}

    # Get historical forecast data to derive demand
    forecast_result = await db.execute(
        select(ForecastRecord)
        .where(ForecastRecord.item_id == item_id)
        .order_by(ForecastRecord.forecast_date)
    )
    forecasts = forecast_result.scalars().all()

    # Create historical demand from forecasts
    if forecasts:
        historical = pd.DataFrame([{
            "date": f.forecast_date,
            "demand": f.actual_demand if f.actual_demand else f.predicted_demand,
        } for f in forecasts])
    else:
        # Synthetic historical data
        now = datetime.utcnow()
        dates = [now - timedelta(days=d) for d in range(60, 0, -1)]
        base = max(1, item.reorder_point / item.lead_time_days)
        historical = pd.DataFrame({
            "date": dates,
            "demand": [max(0, base + np.random.normal(0, base * 0.2)) for _ in dates],
        })

    future_forecasts = forecast_model.forecast(historical, horizon_days=horizon)
    reorder_info = forecast_model.calculate_reorder_info(
        item.current_stock, item.lead_time_days, future_forecasts
    )

    return {
        "item_id": item.id,
        "item_name": item.name,
        "current_stock": item.current_stock,
        "forecasts": future_forecasts,
        "reorder_info": reorder_info,
    }


@router.get("/forecast/summary")
async def get_forecast_summary(db: AsyncSession = Depends(get_db)):
    """Get forecast summary for all items."""
    result = await db.execute(select(InventoryItem))
    items = result.scalars().all()

    summaries = []
    for item in items:
        # Simple forecast based on reorder point
        avg_daily = max(1, item.reorder_point / max(1, item.lead_time_days))
        days_stockout = item.current_stock / avg_daily if avg_daily > 0 else None

        summaries.append({
            "item_id": item.id,
            "item_name": item.name,
            "category": item.category,
            "current_stock": item.current_stock,
            "reorder_point": item.reorder_point,
            "avg_daily_demand": round(avg_daily, 1),
            "days_until_stockout": round(days_stockout, 0) if days_stockout else None,
            "reorder_needed": item.current_stock <= item.reorder_point,
            "stock_status": (
                "critical" if item.current_stock <= item.min_stock else
                "low" if item.current_stock <= item.reorder_point else
                "healthy"
            ),
        })

    return sorted(summaries, key=lambda x: x.get("days_until_stockout") or 999)


@router.get("/reorder-alerts")
async def get_reorder_alerts(db: AsyncSession = Depends(get_db)):
    """Get items below reorder point."""
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.current_stock <= InventoryItem.reorder_point)
        .order_by(InventoryItem.current_stock)
    )
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "current_stock": item.current_stock,
            "reorder_point": item.reorder_point,
            "min_stock": item.min_stock,
            "unit_cost": item.unit_cost,
            "supplier": item.supplier,
            "lead_time_days": item.lead_time_days,
            "recommended_qty": max(0, item.max_stock - item.current_stock),
            "estimated_cost": round(max(0, item.max_stock - item.current_stock) * item.unit_cost, 2),
        }
        for item in items
    ]


@router.post("/{item_id}/restock")
async def restock_item(item_id: int, quantity: int = 0, db: AsyncSession = Depends(get_db)):
    """Log a restock event."""
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return {"error": "Item not found"}

    item.current_stock += quantity
    item.last_restocked = datetime.utcnow()
    await db.flush()

    return {"id": item.id, "new_stock": item.current_stock, "status": "restocked"}
