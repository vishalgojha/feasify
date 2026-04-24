"""SQLAlchemy database models for Feasify."""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Enum, Boolean, Text, create_engine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()

class ZoningType(str, PyEnum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    PUBLIC = "public"
    GREEN = "green"

class PlotModel(Base):
    """Database model for Plot records."""
    __tablename__ = "plots"
    
    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(String(50), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=False)
    area_sqft = Column(Float, nullable=False)
    zoning_type = Column(Enum(ZoningType), default=ZoningType.RESIDENTIAL)
    owner = Column(String(100))
    market_value = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CTSModel(Base):
    """Database model for CTS records."""
    __tablename__ = "cts_records"
    
    id = Column(Integer, primary_key=True, index=True)
    cts_number = Column(String(50), unique=True, index=True, nullable=False)
    plot_id = Column(String(50), index=True)  # Foreign key reference
    area_sqft = Column(Float, nullable=False)
    location = Column(String(100))
    owner = Column(String(100))
    registration_date = Column(DateTime(timezone=True))
    zoning_type = Column(Enum(ZoningType), default=ZoningType.RESIDENTIAL)
    fsi_allowed = Column(Float, default=1.5)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EstimateModel(Base):
    """Database model for Cost Estimates."""
    __tablename__ = "estimates"
    
    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(String(20), unique=True, index=True)
    plot_id = Column(String(50), index=True)
    area_sqft = Column(Float, nullable=False)
    zone_type = Column(String(50))
    num_floors = Column(Integer, default=1)
    built_up_area_sqft = Column(Float)
    rate_per_sqft = Column(Float)
    base_cost = Column(Float)
    contingency = Column(Float)
    overhead = Column(Float)
    total_cost = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ZoningCache(Base):
    """Cached zoning data."""
    __tablename__ = "zoning_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), unique=True, index=True)
    zone_type = Column(Enum(ZoningType))
    fsi_allowed = Column(Float)
    height_limit = Column(Float)
    data = Column(Text)  # JSON string
    cached_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisRecord(Base):
    """Database model for analysis records."""
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, unique=True, index=True)
    cts_number = Column(String, index=True)
    zone = Column(String)
    verdict = Column(String)
    result_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
