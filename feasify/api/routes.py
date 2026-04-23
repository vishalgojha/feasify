"""FastAPI routes for Feasify (future implementation)."""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from feasify.db.session import get_db
from feasify.models.estimate import CostEstimate
from feasify.core.estimator import estimate_cost, generate_estimate_record
from feasify.core.fetcher import fetch_plot_data
from pydantic import BaseModel

app = FastAPI(
    title="Feasify API",
    description="Real estate cost estimation API for Mumbai/Pune",
    version="0.1.0"
)

class EstimateRequest(BaseModel):
    area_sqft: float
    zone_type: str
    num_floors: int = 1
    plot_id: Optional[str] = None

class PlotRequest(BaseModel):
    plot_id: str
    source: str = "mcgm"

@app.post("/estimate", response_model=dict)
async def create_estimate(request: EstimateRequest, db: Session = Depends(get_db)):
    """Generate cost estimate."""
    try:
        result = estimate_cost(
            area_sqft=request.area_sqft,
            zone_type=request.zone_type,
            num_floors=request.num_floors
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/plot/{plot_id}")
async def get_plot(plot_id: str, source: str = "mcgm"):
    """Fetch plot details from municipal sources."""
    data = fetch_plot_data(plot_id, source)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.get("/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/zones")
async def list_zones():
    """List available zoning types."""
    return {
        "zones": ["residential", "commercial", "industrial", "public", "green", "special"]
    }
