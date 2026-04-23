"""CostEstimate dataclass for construction cost estimates."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class CostEstimate:
    """Construction cost estimate record."""
    plot_id: Optional[str] = None
    area_sqft: float = 0.0
    zone_type: str = "residential"
    num_floors: int = 1
    built_up_area_sqft: float = 0.0
    rate_per_sqft: float = 0.0
    base_cost: float = 0.0
    contingency: float = 0.0
    overhead: float = 0.0
    total_cost: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    estimate_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.estimate_id:
            import uuid
            self.estimate_id = str(uuid.uuid4())[:8]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "estimate_id": self.estimate_id,
            "plot_id": self.plot_id,
            "area_sqft": self.area_sqft,
            "zone_type": self.zone_type,
            "num_floors": self.num_floors,
            "built_up_area_sqft": self.built_up_area_sqft,
            "rate_per_sqft": self.rate_per_sqft,
            "base_cost": self.base_cost,
            "contingency": self.contingency,
            "overhead": self.overhead,
            "total_cost": self.total_cost,
            "created_at": self.created_at.isoformat()
        }
    
    def to_csv_row(self) -> list:
        """Convert to CSV row."""
        return [
            self.estimate_id,
            self.plot_id or "",
            self.area_sqft,
            self.zone_type,
            self.num_floors,
            self.total_cost,
            self.created_at.strftime("%Y-%m-%d")
        ]
