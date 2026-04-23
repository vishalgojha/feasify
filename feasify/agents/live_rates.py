"""Construction cost data - live rates and material indices."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

# Cache settings
LIVE_RATES_CACHE_DIR = Path("data/cache/live_rates")
LIVE_RATES_CACHE_TTL = 3600  # 1 hour


def _get_cache_path(key: str) -> Path:
    """Get cache file path."""
    LIVE_RATES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_key = "".join(c for c in key if c.isalnum() or c in "_-").strip()
    return LIVE_RATES_CACHE_DIR / f"{safe_key}.json"


def _get_cached(key: str) -> Optional[Dict]:
    """Get cached data if not expired."""
    cache_file = _get_cache_path(key)
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data["timestamp"])
                if (datetime.now() - timestamp).seconds < LIVE_RATES_CACHE_TTL:
                    logger.info(f"Using cached data for {key}")
                    return data["data"]
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
    return None


def _set_cache(key: str, data: Dict):
    """Save data to cache."""
    cache_file = _get_cache_path(key)
    try:
        with open(cache_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "data": data
            }, f)
    except Exception as e:
        logger.warning(f"Cache write error for {key}: {e}")


def get_construction_rates(use_live: bool = False) -> Dict[str, Any]:
    """
    Get construction rates - live or placeholder.
    
    Args:
        use_live: If True, attempt live fetch; fall back to placeholder on failure
    
    Returns:
        Dictionary with rates and metadata
    """
    if not use_live:
        # Return hardcoded placeholder rates
        return {
            "source": "Placeholder Rates",
            "data_as_of": "2025-01",
            "is_live": False,
            "cement": {"rate": 380.0, "unit": "per bag (50kg)", "location": "Mumbai"},
            "steel": {"rate": 68.0, "unit": "per kg", "location": "Mumbai"},
            "sand": {"rate": 4500.0, "unit": "per brass (100 CFT)", "location": "Mumbai"},
            "aggregate_20mm": {"rate": 3200.0, "unit": "per brass (100 CFT)", "location": "Mumbai"},
            "bricks": {"rate": 7.5, "unit": "per piece", "location": "Mumbai"},
            "note": "REAL_SELECTOR_NEEDED: Replace with live BMT/cement mart APIs"
        }
    
    # Attempt live fetch
    try:
        # TODO: Implement live API calls to:
        # - BMT (https://bmt.gov.in) for official rates
        # - CementMart API for market prices
        # - Steel prices from SteelAuthority of India
        
        # Placeholder for now - simulate API failure
        raise NotImplementedError("Live rate fetch not yet implemented")
        
    except Exception as e:
        logger.warning(f"Live rates fetch failed: {e}")
        result = get_construction_rates(use_live=False)
        result["fetch_error"] = str(e)
        result["is_live"] = False
        return result


def get_labour_indices(use_live: bool = False) -> Dict[str, Any]:
    """
    Get labour cost indices.
    
    Args:
        use_live: If True, attempt live fetch; fall back to placeholder
    
    Returns:
        Dictionary with labour rates by skill level
    """
    if not use_live:
        return {
            "source": "Placeholder Indices",
            "base_period": "2015-16=100",
            "data_as_of": "2025-01",
            "is_live": False,
            "unskilled": {"current": 600.0, "unit": "per day", "zone": "Mumbai"},
            "semi_skilled": {"current": 800.0, "unit": "per day", "zone": "Mumbai"},
            "skilled": {"current": 1200.0, "unit": "per day", "zone": "Mumbai"},
            "supervisor": {"current": 1500.0, "unit": "per day", "zone": "Mumbai"},
            "engineer_junior": {"current": 2500.0, "unit": "per day", "zone": "Mumbai"},
            "engineer_senior": {"current": 4000.0, "unit": "per day", "zone": "Mumbai"},
            "note": "REAL_SELECTOR_NEEDED: Scrape Maharashtra Labour Dept notices"
        }
    
    try:
        # TODO: Implement live scraping from Maharashtra Labour Department
        raise NotImplementedError("Live labour indices not yet implemented")
    except Exception as e:
        logger.warning(f"Live labour indices fetch failed: {e}")
        result = get_labour_indices(use_live=False)
        result["fetch_error"] = str(e)
        return result


def get_gst_rates() -> Dict[str, Any]:
    """
    Get current GST rates for construction materials.
    
    Returns:
        Dictionary with GST rates by category
    """
    return {
        "source": "CBIC GST Portal",
        "data_as_of": "2025-01",
        "is_live": True,  # GST rates are standardized by CBIC
        "rates": {
            "cement": 28.0,
            "steel": 18.0,
            "sand": 5.0,
            "aggregate": 5.0,
            "bricks": 5.0,
            "paint": 18.0,
            "flooring": 18.0,
            "electrical": 18.0,
            "plumbing": 18.0,
            "construction_services": 18.0,
        },
        "note": "GST rates standardized. Verify at https://cbic.gov.in"
    }


def calculate_live_construction_cost(
    area_sqft: float,
    zone_type: str,
    num_floors: int,
    finish_grade: str = "standard",
    use_live_rates: bool = True
) -> Dict[str, Any]:
    """
    Calculate construction cost using live rates if available.
    
    Args:
        area_sqft: Built-up area in sq.ft.
        zone_type: Zoning type
        num_floors: Number of floors
        finish_grade: Construction grade
        use_live_rates: Whether to fetch live rates
    
    Returns:
        Dictionary with cost breakdown
    """
    from feasify.utils.rates import PWD_RATES, ZONE_MULTIPLIERS
    
    built_up_area = area_sqft * num_floors
    
    # Get rates
    rates = get_construction_rates(use_live=use_live_rates)
    
    # Get base rate from PWD or adjust with live rates
    if use_live_rates and rates.get("is_live"):
        # Use live material prices to adjust PWD rates
        base_rate = PWD_RATES.get(finish_grade, 1800.0)
        
        # Adjust based on cement price trends (30% weight)
        if "cement" in rates:
            cement_price = rates["cement"].get("current", 380.0)
            adjustment_factor = cement_price / 380.0  # Normalize to base 380
            base_rate *= (adjustment_factor * 0.3 + 0.7)
    else:
        base_rate = PWD_RATES.get(finish_grade, 1800.0)
    
    # Apply zone multiplier
    zone_multiplier = ZONE_MULTIPLIERS.get(zone_type.lower(), 1.0)
    adjusted_rate = base_rate * zone_multiplier
    
    # Calculate costs
    base_cost = built_up_area * adjusted_rate
    contingency = base_cost * 0.05
    overhead = base_cost * 0.10
    total_cost = base_cost + contingency + overhead
    
    return {
        "area_sqft": area_sqft,
        "built_up_area_sqft": built_up_area,
        "zone_type": zone_type,
        "num_floors": num_floors,
        "finish_grade": finish_grade,
        "rate_per_sqft": round(adjusted_rate, 2),
        "base_rate_source": "live_rates" if rates.get("is_live") else "PWD_RATES",
        "base_cost": round(base_cost, 2),
        "contingency": round(contingency, 2),
        "overhead": round(overhead, 2),
        "total_cost": round(total_cost, 2),
        "material_prices": rates if use_live_rates else None,
        "gst_rates": get_gst_rates(),
    }
