"""Equipment and SensorReading ORM models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class EquipmentStatus(str, enum.Enum):
    OPERATIONAL = "operational"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class EquipmentType(str, enum.Enum):
    CNC_MACHINE = "CNC Machine"
    CONVEYOR_BELT = "Conveyor Belt"
    ROBOTIC_ARM = "Robotic Arm"
    HYDRAULIC_PRESS = "Hydraulic Press"
    INDUSTRIAL_OVEN = "Industrial Oven"


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    status = Column(String(20), default=EquipmentStatus.OPERATIONAL.value)
    health_score = Column(Float, default=100.0)
    install_date = Column(DateTime, nullable=False)
    last_maintenance = Column(DateTime, nullable=True)
    manufacturer = Column(String(100), nullable=True)
    model_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensor_readings = relationship("SensorReading", back_populates="equipment", cascade="all, delete-orphan")
    defects = relationship("DefectRecord", back_populates="equipment", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="equipment", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="equipment", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    temperature = Column(Float, nullable=False)  # Celsius
    vibration = Column(Float, nullable=False)  # mm/s
    pressure = Column(Float, nullable=False)  # PSI
    rpm = Column(Float, nullable=True)  # Revolutions per minute
    power_consumption = Column(Float, nullable=False)  # kW
    humidity = Column(Float, nullable=True)  # Percentage
    noise_level = Column(Float, nullable=True)  # dB

    # Relationships
    equipment = relationship("Equipment", back_populates="sensor_readings")
