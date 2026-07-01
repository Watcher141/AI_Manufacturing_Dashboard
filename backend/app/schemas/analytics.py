"""Pydantic schemas for Analytics and Dashboard."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardOverviewResponse(BaseModel):
    total_equipment: int
    operational_count: int
    warning_count: int
    critical_count: int
    maintenance_count: int
    offline_count: int
    avg_health_score: float
    total_defects_today: int
    total_defects_week: int
    critical_alerts: int
    unread_alerts: int
    oee_percentage: float
    inventory_low_stock: int
    recent_alerts: List[Dict[str, Any]]
    equipment_health_summary: List[Dict[str, Any]]


class SensorTrendResponse(BaseModel):
    equipment_id: int
    equipment_name: str
    data: List[Dict[str, Any]]  # [{timestamp, temperature, vibration, pressure, ...}]


class DefectTrendResponse(BaseModel):
    period: str  # daily, weekly, monthly
    data: List[Dict[str, Any]]  # [{date, crack, corrosion, misalignment, ...}]


class MaintenanceCostResponse(BaseModel):
    total_cost: float
    by_equipment: Dict[str, float]
    by_type: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]


class OEEResponse(BaseModel):
    overall: float
    availability: float
    performance: float
    quality: float
    trend: List[Dict[str, Any]]


class AlertResponse(BaseModel):
    id: int
    type: str
    severity: str
    title: str
    message: str
    equipment_id: Optional[int] = None
    equipment_name: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCountResponse(BaseModel):
    total: int
    unread: int
    critical: int
    warning: int
    info: int


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None
