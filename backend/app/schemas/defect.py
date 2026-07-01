"""Pydantic schemas for DefectRecord."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DefectBase(BaseModel):
    equipment_id: int
    defect_type: str
    severity: str
    confidence_score: float
    description: Optional[str] = None


class DefectCreate(DefectBase):
    timestamp: Optional[datetime] = None
    detected_by: str = "ml_model"


class DefectResponse(DefectBase):
    id: int
    timestamp: datetime
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    detected_by: str
    created_at: datetime
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True


class DefectStatsResponse(BaseModel):
    total_defects: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    resolved_count: int
    unresolved_count: int
    resolution_rate: float
    by_type: dict
    by_equipment: dict


class DefectDetectionRequest(BaseModel):
    equipment_id: Optional[int] = None  # None = scan all
