"""Pydantic schemas for Equipment and SensorReading."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─── Sensor Reading ────────────────────────────────────────────────
class SensorReadingBase(BaseModel):
    temperature: float
    vibration: float
    pressure: float
    rpm: Optional[float] = None
    power_consumption: float
    humidity: Optional[float] = None
    noise_level: Optional[float] = None


class SensorReadingCreate(SensorReadingBase):
    equipment_id: int
    timestamp: Optional[datetime] = None


class SensorReadingResponse(SensorReadingBase):
    id: int
    equipment_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ─── Equipment ─────────────────────────────────────────────────────
class EquipmentBase(BaseModel):
    name: str
    type: str
    location: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None

    model_config = {
        "protected_namespaces": ()
    }


class EquipmentCreate(EquipmentBase):
    install_date: datetime


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    health_score: Optional[float] = None


class EquipmentResponse(EquipmentBase):
    id: int
    status: str
    health_score: float
    install_date: datetime
    last_maintenance: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EquipmentDetailResponse(EquipmentResponse):
    latest_readings: Optional[List[SensorReadingResponse]] = []
    alert_count: int = 0
    defect_count: int = 0


class EquipmentHealthResponse(BaseModel):
    equipment_id: int
    name: str
    type: str
    health_score: float
    status: str
    anomaly_score: Optional[float] = None
    failure_probability: Optional[float] = None
    predicted_failure_type: Optional[str] = None
    estimated_ttf_hours: Optional[float] = None  # Time to failure
