"""DefectRecord ORM model."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class DefectType(str, enum.Enum):
    CRACK = "crack"
    CORROSION = "corrosion"
    MISALIGNMENT = "misalignment"
    SURFACE_SCRATCH = "surface_scratch"
    DEFORMATION = "deformation"
    OVERHEATING = "overheating"


class DefectSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectRecord(Base):
    __tablename__ = "defect_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    defect_type = Column(String(30), nullable=False)
    severity = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 - 1.0
    description = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    detected_by = Column(String(50), default="ml_model")  # ml_model or manual
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="defects")
