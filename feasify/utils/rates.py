"""PWD rates and multiplier constants for cost estimation."""
from typing import Dict
from pathlib import Path
import json
from datetime import datetime

# Default PWD rates (in ₹ per sq.ft.)
# These should be updated periodically from official sources
PWD_RATES: Dict[str, float] = {
    "residential": 1800.0,
    "commercial": 2200.0,
    "industrial": 1500.0,
    "public": 1200.0,
    "green": 1000.0,
    "special": 2000.0
}

# Zone type multipliers (adjustments to base rates)
ZONE_MULTIPLIERS: Dict[str, float] = {
    "residential": 1.0,
    "commercial": 1.3,
    "industrial": 0.9,
    "public": 0.8,
    "green": 0.7,
    "special": 1.2
}

# FSI (Floor Space Index) limits by zone
FSI_LIMITS: Dict[str, float] = {
    "residential": 1.5,
    "commercial": 2.0,
    "industrial": 1.2,
    "public": 1.0,
    "green": 0.5,
    "special": 1.8
}

def get_current_rates(force_update: bool = False) -> Dict[str, float]:
    """
    Get current PWD rates, optionally updating from source.
    
    Args:
        force_update: Force update from official source
    
    Returns:
        Dictionary of rates by zone type
    """
    rates_file = Path("data/rates/pwd_rates.json")
    
    # Load cached rates if available and not forcing update
    if rates_file.exists() and not force_update:
        with open(rates_file, "r") as f:
            cached = json.load(f)
            # Check if rates are recent (less than 30 days old)
            cached_time = datetime.fromisoformat(cached.get("timestamp", "2000-01-01"))
            days_old = (datetime.now() - cached_time).days
            if days_old < 30:
                return cached.get("rates", PWD_RATES)
    
    # In production, fetch from official PWD website
    # For now, return default rates
    return PWD_RATES

def update_rates(new_rates: Dict[str, float]):
    """Update and cache PWD rates."""
    rates_file = Path("data/rates/pwd_rates.json")
    rates_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "rates": new_rates,
        "timestamp": datetime.now().isoformat(),
        "source": "default"  # Change to "pwd_website" when implemented
    }
    
    with open(rates_file, "w") as f:
        json.dump(data, f, indent=2)

def get_fsi_for_zone(zone_type: str) -> float:
    """Get FSI limit for a zone type."""
    return FSI_LIMITS.get(zone_type.lower(), 1.0)
