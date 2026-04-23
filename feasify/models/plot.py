"""Plot, CTS, and Zoning data models."""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from feasify.core.zoning import ZoningType

@dataclass
class CTS:
    """CTS (Chain Tax Survey) number record."""
    number: str
    area_sqft: float
    location: str
    owner: Optional[str] = None
    registration_date: Optional[datetime] = None
    zoning_type: ZoningType = ZoningType.RESIDENTIAL
    fsi_allowed: float = 1.5
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "cts_number": self.number,
            "area_sqft": self.area_sqft,
            "location": self.location,
            "owner": self.owner,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "zoning_type": self.zoning_type.value,
            "fsi_allowed": self.fsi_allowed,
            "coordinates": (self.latitude, self.longitude) if self.latitude and self.longitude else None
        }

@dataclass
class Plot:
    """Plot record with multiple CTS numbers possible."""
    plot_id: str
    address: str
    area_sqft: float
    zoning_type: ZoningType = ZoningType.RESIDENTIAL
    cts_numbers: List[CTS] = field(default_factory=list)
    owner: Optional[str] = None
    market_value: Optional[float] = None
    last_updated: Optional[datetime] = None
    
    def add_cts(self, cts: CTS):
        """Add a CTS record to the plot."""
        self.cts_numbers.append(cts)
        # Update total area if needed
        if cts.area_sqft > 0:
            self.area_sqft = sum(c.area_sqft for c in self.cts_numbers)
    
    def to_dict(self) -> dict:
        return {
            "plot_id": self.plot_id,
            "address": self.address,
            "area_sqft": self.area_sqft,
            "zoning_type": self.zoning_type.value,
            "owner": self.owner,
            "market_value": self.market_value,
            "cts_count": len(self.cts_numbers),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
