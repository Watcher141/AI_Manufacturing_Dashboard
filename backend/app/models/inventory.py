"""InventoryItem and ForecastRecord ORM models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # spare_parts, consumables, raw_materials
    current_stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=10)
    max_stock = Column(Integer, nullable=False, default=500)
    reorder_point = Column(Integer, nullable=False, default=50)
    unit_cost = Column(Float, nullable=False)
    lead_time_days = Column(Integer, nullable=False, default=7)
    supplier = Column(String(150), nullable=True)
    location = Column(String(100), nullable=True)  # Warehouse location
    last_restocked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    forecasts = relationship("ForecastRecord", back_populates="item", cascade="all, delete-orphan")


class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    forecast_date = Column(DateTime, nullable=False, index=True)
    predicted_demand = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    actual_demand = Column(Float, nullable=True)  # Filled in later for validation
    model_version = Column(String(20), default="v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    item = relationship("InventoryItem", back_populates="forecasts")
