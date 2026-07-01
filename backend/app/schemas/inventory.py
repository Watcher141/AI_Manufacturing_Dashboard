"""Pydantic schemas for Inventory and Forecast."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InventoryItemBase(BaseModel):
    name: str
    sku: str
    category: str
    current_stock: int
    min_stock: int
    max_stock: int
    reorder_point: int
    unit_cost: float
    lead_time_days: int
    supplier: Optional[str] = None
    location: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemResponse(InventoryItemBase):
    id: int
    last_restocked: Optional[datetime] = None
    created_at: datetime
    stock_status: Optional[str] = None  # computed: healthy, low, critical

    class Config:
        from_attributes = True


class InventoryRestockRequest(BaseModel):
    quantity: int
    notes: Optional[str] = None


class ForecastResponse(BaseModel):
    item_id: int
    item_name: str
    forecast_date: datetime
    predicted_demand: float
    confidence_lower: float
    confidence_upper: float
    actual_demand: Optional[float] = None

    class Config:
        from_attributes = True


class ForecastSummaryResponse(BaseModel):
    item_id: int
    item_name: str
    current_stock: int
    avg_daily_demand: float
    days_until_stockout: Optional[float] = None
    recommended_order_qty: Optional[int] = None
    reorder_needed: bool
    forecasts: List[ForecastResponse]


class InventoryOverviewResponse(BaseModel):
    total_items: int
    total_value: float
    low_stock_count: int
    critical_stock_count: int
    reorder_pending_count: int
    categories: dict
