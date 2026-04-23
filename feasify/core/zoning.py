"""Zoning data models and parser for Mumbai/Pune regions."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import json

class ZoningType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    PUBLIC = "public"
    GREEN = "green"
    SPECIAL = "special"

@dataclass
class ZoningInfo:
    """Zoning information for a location."""
    location: str
    zone_type: ZoningType
    fsi_allowed: float
    height_limit: Optional[float] = None
    setback_requirements: Optional[List[float]] = None
    special_conditions: Optional[List[str]] = None
    
    def to_dict(self) -> dict:
        return {
            "location": self.location,
            "zone_type": self.zone_type.value,
            "fsi_allowed": self.fsi_allowed,
            "height_limit": self.height_limit,
            "setback_requirements": self.setback_requirements,
            "special_conditions": self.special_conditions
        }

class ZoningParser:
    """Parser for zoning data from MCGM/DP documents."""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("data/processed/zoning")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_zoning_map(self, map_path: Path) -> List[ZoningInfo]:
        """
        Parse zoning map data (PDF/GeoJSON).
        
        Args:
            map_path: Path to zoning map file
        
        Returns:
            List of ZoningInfo objects
        """
        if map_path.suffix == ".json":
            return self._parse_geojson(map_path)
        elif map_path.suffix == ".pdf":
            return self._parse_pdf(map_path)
        else:
            raise ValueError(f"Unsupported file format: {map_path.suffix}")
    
    def _parse_geojson(self, json_path: Path) -> List[ZoningInfo]:
        """Parse GeoJSON zoning data."""
        with open(json_path, "r") as f:
            data = json.load(f)
        
        zoning_info = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            zoning_info.append(ZoningInfo(
                location=props.get("location", "Unknown"),
                zone_type=ZoningType(props.get("zone_type", "residential")),
                fsi_allowed=float(props.get("fsi", 1.5)),
                height_limit=float(props.get("height_limit")) if "height_limit" in props else None,
                setback_requirements=props.get("setbacks"),
                special_conditions=props.get("conditions")
            ))
        return zoning_info
    
    def _parse_pdf(self, pdf_path: Path) -> List[ZoningInfo]:
        """Parse PDF zoning document (simplified)."""
        # In production, use pdfplumber or PyPDF2 to extract tables
        return []
    
    def get_cached_zoning(self, location: str) -> Optional[ZoningInfo]:
        """Retrieve cached zoning info for a location."""
        cache_file = self.cache_dir / f"{location.lower().replace(' ', '_')}.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                data = json.load(f)
                return ZoningInfo(**data)
        return None
    
    def cache_zoning(self, zoning: ZoningInfo):
        """Cache zoning info for a location."""
        cache_file = self.cache_dir / f"{zoning.location.lower().replace(' ', '_')}.json"
        with open(cache_file, "w") as f:
            json.dump(zoning.to_dict(), f, indent=2)
