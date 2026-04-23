"""Live construction cost data fetchers - BMT CPR, material prices, labour indices."""
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


def fetch_bmt_cpr_rates(material_type: str = "cement") -> Dict[str, Any]:
    """
    Fetch BMT CPR (Contractor Price Rate) data.
    REAL_SELECTOR_NEEDED: Verify BMT portal structure.
    
    Args:
        material_type: cement, steel, sand, aggregate, bricks
    
    Returns:
        Dictionary with rates and metadata
    """
    cache_key = f"bmt_cpr_{material_type}"
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    result = {
        "source": "BMT CPR",
        "material_type": material_type,
        "rate_per_unit": None,
        "unit": "",
        "location": "Mumbai",
        "effective_date": None,
        "trend": "stable",
    }
    
    try:
        # REAL_SELECTOR_NEEDED: Verify URL and selectors
        # BMT publishes CPR on their portal - this is a placeholder structure
        url_map = {
            "cement": "https://bmt.gov.in/cpr/cement-rates",
            "steel": "https://bmt.gov.in/cpr/steel-rates",
            "sand": "https://bmt.gov.in/cpr/sand-rates",
            "aggregate": "https://bmt.gov.in/cpr/aggregate-rates",
            "bricks": "https://bmt.gov.in/cpr/brick-rates",
        }
        
        url = url_map.get(material_type.lower())
        if not url:
            logger.warning(f"Unknown material type: {material_type}")
            return result
        
        # REAL_SELECTOR_NEEDED: Implement actual scraper
        # Placeholder rates (update when portal is accessible)
        placeholder_rates = {
            "cement": {"rate": 380.0, "unit": "per bag (50kg)"},
            "steel": {"rate": 68.0, "unit": "per kg"},
            "sand": {"rate": 4500.0, "unit": "per brass (100 CFT)"},
            "aggregate": {"rate": 3200.0, "unit": "per brass (100 CFT)"},
            "bricks": {"rate": 7.5, "unit": "per piece"},
        }
        
        if material_type.lower() in placeholder_rates:
            data = placeholder_rates[material_type.lower()]
            result["rate_per_unit"] = data["rate"]
            result["unit"] = data["unit"]
            result["effective_date"] = datetime.now().strftime("%Y-%m-%d")
            result["note"] = "REAL_SELECTOR_NEEDED: Scrape live BMT CPR portal"
        
        _set_cache(cache_key, result)
        
    except Exception as e:
        logger.error(f"Error fetching BMT CPR for {material_type}: {e}")
        result["error"] = str(e)
    
    return result


def fetch_material_price_index() -> Dict[str, Any]:
    """
    Fetch material price index (cement, steel, etc.).
    REAL_SELECTOR_NEEDED: Use API or scraper for economic indices.
    
    Returns:
        Dictionary with price indices
    """
    cache_key = "material_price_index"
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    result = {
        "source": "Material Price Index",
        "base_period": "2015-16=100",
        "indices": {},
        "last_updated": None,
        "note": "REAL_SELECTOR_NEEDED: Integrate with SteelAuthority, CementMart APIs"
    }
    
    try:
        # REAL_SELECTOR_NEEDED: Implement actual API calls
        # Placeholder indices (Mumbai market)
        result["indices"] = {
            "cement": {"current": 185.2, "unit": "per bag (50kg)", "change_pct": 2.3},
            "steel_tmt": {"current": 68.5, "unit": "per kg", "change_pct": -1.2},
            "steel_angles": {"current": 72.0, "unit": "per kg", "change_pct": 0.8},
            "sand": {"current": 4500.0, "unit": "per brass", "change_pct": 5.0},
            "aggregate_20mm": {"current": 3200.0, "unit": "per brass", "change_pct": 3.2},
            "bricks": {"current": 7.5, "unit": "per piece", "change_pct": 1.5},
            "flooring_vitrified": {"current": 65.0, "unit": "per sq.ft.", "change_pct": 0.0},
            "paint_royal": {"current": 350.0, "unit": "per litre", "change_pct": 2.0},
        }
        result["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        _set_cache(cache_key, result)
        
    except Exception as e:
        logger.error(f"Error fetching material price index: {e}")
        result["error"] = str(e)
    
    return result


def fetch_labour_indices() -> Dict[str, Any]:
    """
    Fetch labour cost indices.
    REAL_SELECTOR_NEEDED: Source from Maharashtra labour department.
    
    Returns:
        Dictionary with labour rates by skill level
    """
    cache_key = "labour_indices"
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    result = {
        "source": "Maharashtra Labour Department",
        "base_period": "2015-16=100",
        "rates": {},
        "last_updated": None,
        "note": "REAL_SELECTOR_NEEDED: Scrape labour department notices"
    }
    
    try:
        # REAL_SELECTOR_NEEDED: Implement actual scraper
        # Placeholder rates (per day, 8 hours)
        result["rates"] = {
            "unskilled": {"current": 600.0, "unit": "per day", "zone": "Mumbai"},
            "semi_skilled": {"current": 800.0, "unit": "per day", "zone": "Mumbai"},
            "skilled": {"current": 1200.0, "unit": "per day", "zone": "Mumbai"},
            "supervisor": {"current": 1500.0, "unit": "per day", "zone": "Mumbai"},
            "engineer_junior": {"current": 2500.0, "unit": "per day", "zone": "Mumbai"},
            "engineer_senior": {"current": 4000.0, "unit": "per day", "zone": "Mumbai"},
        }
        result["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        _set_cache(cache_key, result)
        
    except Exception as e:
        logger.error(f"Error fetching labour indices: {e}")
        result["error"] = str(e)
    
    return result


def fetch_gst_rates() -> Dict[str, Any]:
    """
    Fetch current GST rates for construction materials.
    
    Returns:
        Dictionary with GST rates by category
    """
    return {
        "source": "CBIC GST Portal",
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
        "note": "GST rates are standardized. Verify at https://cbic.gov.in"
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
    
    # Get base rate
    if use_live_rates:
        material_index = fetch_material_price_index()
        labour_index = fetch_labour_indices()
        
        # Adjust base rate based on material price trends
        base_rate = PWD_RATES.get(finish_grade, 1800.0)
        
        # Apply material price adjustment (if indices available)
        if "indices" in material_index:
            cement_index = material_index["indices"].get("cement", {}).get("current", 100.0)
            adjustment_factor = cement_index / 100.0  # Normalize to base 100
            base_rate *= (adjustment_factor * 0.3 + 0.7)  # 30% weight to material prices
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
        "base_rate_source": "live_rates" if use_live_rates else "PWD_RATES",
        "base_cost": round(base_cost, 2),
        "contingency": round(contingency, 2),
        "overhead": round(overhead, 2),
        "total_cost": round(total_cost, 2),
        "material_prices": fetch_material_price_index() if use_live_rates else None,
        "labour_rates": fetch_labour_indices() if use_live_rates else None,
        "gst_rates": fetch_gst_rates(),
    }
