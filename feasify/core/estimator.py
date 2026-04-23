"""Cost estimation engine using PWD rates and multipliers."""
from dataclasses import dataclass
from typing import Dict, Any
from feasify.models.estimate import CostEstimate
from feasify.utils.rates import PWD_RATES, ZONE_MULTIPLIERS

def estimate_cost(
    area_sqft: float,
    zone_type: str,
    num_floors: int = 1,
    rates: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Estimate construction cost for a plot.
    
    Args:
        area_sqft: Plot area in square feet
        zone_type: Zoning type (residential, commercial, industrial)
        num_floors: Number of floors to construct
        rates: Custom PWD rates (uses default if None)
    
    Returns:
        Dictionary with cost breakdown
    """
    if rates is None:
        rates = PWD_RATES
    
    # Get base rate for zone
    zone_key = zone_type.lower()
    base_rate = rates.get(zone_key, rates.get("residential", 1500))
    
    # Apply zone multiplier
    multiplier = ZONE_MULTIPLIERS.get(zone_key, 1.0)
    adjusted_rate = base_rate * multiplier
    
    # Calculate costs
    built_up_area = area_sqft * num_floors
    base_cost = built_up_area * adjusted_rate
    
    # Add contingencies and overhead
    contingency = base_cost * 0.05  # 5%
    overhead = base_cost * 0.10     # 10%
    total_cost = base_cost + contingency + overhead
    
    return {
        "plot_area_sqft": area_sqft,
        "built_up_area_sqft": built_up_area,
        "zone_type": zone_type,
        "num_floors": num_floors,
        "rate_per_sqft": adjusted_rate,
        "base_cost": base_cost,
        "contingency": contingency,
        "overhead": overhead,
        "total_cost": total_cost
    }

def generate_estimate_record(
    area_sqft: float,
    zone_type: str,
    num_floors: int,
    plot_id: str = None
) -> CostEstimate:
    """Generate a CostEstimate dataclass instance."""
    result = estimate_cost(area_sqft, zone_type, num_floors)
    # Remove keys that are passed as explicit arguments to avoid duplicates
    for key in ["plot_area_sqft", "zone_type", "num_floors"]:
        result.pop(key, None)
    return CostEstimate(
        plot_id=plot_id,
        area_sqft=area_sqft,
        zone_type=zone_type,
        num_floors=num_floors,
        **result
    )
