"""Spatial context calculator - distances to airport, coast, heritage zones."""
import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Airport and coastal coordinates
CSIA_COORDINATES = (19.0896, 72.8656)   # Chhatrapati Shivaji Airport (Mumbai)
JNPA_COORDINATES = (19.0667, 73.0511)  # Jawaharlal Nehru Port (Navi Mumbai)
MARINE_DRIVE_COAST = (18.9437, 72.8232)  # Marine Drive coastline

AIRPORT_FUNNEL_RADIUS_KM = 5.0
COASTAL_BUFFER_KM = 0.5

# Railway buffer zones (wards near tracks)
RAILWAY_BUFFER_WARDS = ["L", "M", "N", "P", "R"]  # Western/Central lines
HERITAGE_WARDS = ["A", "B", "C", "D", "E", "F"]  # South Mumbai heritage


@dataclass
class SpatialContext:
    """Spatial context for a plot."""
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    distance_to_csia_km: float = 0.0
    distance_to_jnpa_km: float = 0.0
    distance_to_coast_km: float = 0.0
    in_airport_funnel: bool = False
    in_coastal_buffer: bool = False
    in_heritage_ward: bool = False
    in_railway_buffer: bool = False
    nearest_airport: str = "CSIA"
    warnings: list[str] = field(default_factory=list)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points in km.
    Uses Haversine formula for accurate earth-surface distance.
    """
    R = 6371.0  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocode address to lat/lng using geopy or similar.
    Placeholder - in production, use Google Maps API or similar.
    
    REAL_SELECTOR_NEEDED: Implement actual geocoding
    Options: geopy with Nominatim, Google Geocoding API, MapMyIndia API
    """
    # Placeholder: Mumbai approximate center
    logger.warning(f"Geocoding not implemented. Using Mumbai center for {address}")
    return (19.0760, 72.8777)  # Mumbai approximate center


def get_spatial_context(
    address: str = "",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    ward: str = ""
) -> Dict[str, Any]:
    """
    Compute spatial context: airport distances, coastal proximity, heritage/railway flags.
    
    Args:
        address: Property address for geocoding
        lat: Latitude (if known)
        lng: Longitude (if known)
        ward: MCGM ward (e.g., "A", "L", etc.)
    
    Returns:
        SpatialContext as dictionary
    """
    # Get coordinates
    if lat is not None and lng is not None:
        coords = (lat, lng)
    elif address:
        coords = get_coordinates_from_address(address)
        if coords is None:
            coords = (19.0760, 72.8777)  # Fallback to Mumbai center
    else:
        coords = (19.0760, 72.8777)
    
    lat, lng = coords
    
    # Calculate distances
    dist_csia = haversine_distance(lat, lng, *CSIA_COORDINATES)
    dist_jnpa = haversine_distance(lat, lng, *JNPA_COORDINATES)
    dist_coast = haversine_distance(lat, lng, *MARINE_DRIVE_COAST)
    
    # Determine nearest airport
    nearest_airport = "CSIA" if dist_csia <= dist_jnpa else "JNPA"
    min_airport_dist = min(dist_csia, dist_jnpa)
    
    # Check zones
    in_funnel = min_airport_dist <= AIRPORT_FUNNEL_RADIUS_KM
    in_coastal = dist_coast <= COASTAL_BUFFER_KM
    in_heritage = ward.upper() in HERITAGE_WARDS
    in_railway = ward.upper() in RAILWAY_BUFFER_WARDS
    
    # Build warnings
    warnings = []
    if in_funnel:
        warnings.append(f"Plot is within {AIRPORT_FUNNEL_RADIUS_KM}km airport funnel zone - height restrictions apply")
    if in_coastal:
        warnings.append(f"Plot is within {COASTAL_BUFFER_KM}km of coastline - CRZ regulations may apply")
    if in_heritage:
        warnings.append(f"Plot is in heritage ward {ward} - heritage committee clearance required")
    if in_railway:
        warnings.append(f"Plot is in railway buffer ward {ward} - additional setbacks from tracks")
    
    return {
        "address": address,
        "lat": lat,
        "lng": lng,
        "distance_to_csia_km": round(dist_csia, 2),
        "distance_to_jnpa_km": round(dist_jnpa, 2),
        "distance_to_coast_km": round(dist_coast, 2),
        "nearest_airport": nearest_airport,
        "in_airport_funnel": in_funnel,
        "in_coastal_buffer": in_coastal,
        "in_heritage_ward": in_heritage,
        "in_railway_buffer": in_railway,
        "warnings": warnings,
    }
