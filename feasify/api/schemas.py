"""Pydantic schemas for FastAPI request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EstimateCreate(BaseModel):
    """Request schema for creating cost estimate."""
    plot_id: Optional[str] = Field(None, description="Plot ID or CTS number")
    area_sqft: float = Field(..., gt=0, description="Plot area in square feet")
    zone_type: str = Field(..., description="Zoning type")
    num_floors: int = Field(1, ge=1, le=10, description="Number of floors")

class EstimateResponse(BaseModel):
    """Response schema for cost estimate."""
    estimate_id: str
    plot_id: Optional[str]
    area_sqft: float
    zone_type: str
    num_floors: int
    total_cost: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class PlotResponse(BaseModel):
    """Response schema for plot details."""
    plot_id: str
    area_sqft: Optional[float]
    zone_type: Optional[str]
    owner: Optional[str]
    address: Optional[str]
    source: str

class ZoningInfo(BaseModel):
    """Zoning information schema."""
    location: str
    zone_type: str
    fsi_allowed: float
    height_limit: Optional[float] = None
    setback_requirements: Optional[List[float]] = None

class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
