"""Alert and MaintenanceLog ORM models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class AlertType(str, enum.Enum):
    MAINTENANCE = "maintenance"
    DEFECT = "defect"
    INVENTORY = "inventory"
    SYSTEM = "system"


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    equipment = relationship("Equipment", back_populates="alerts")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    maintenance_type = Column(String(50), nullable=False)  # preventive, corrective, predictive
    performed_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    technician = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parts_replaced = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_logs")
