"""Clearance engine - identify all required government clearances and fees."""
from typing import List, Dict, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Clearance timelines (days) - MCGM Citizen Charter 2023
CLEARANCE_TIMELINES = {
    "IOD": 30,          # Intimation of Disapproval
    "CC": 60,           # Commencement Certificate
    "OC": 45,          # Occupancy Certificate
    "AAI_NOC": 45,      # Airport NOC
    "FIRE_NOC": 30,      # Fire Brigade NOC
    "POLLUTION_NOC": 15, # Pollution Control Board
    "TREE_CUT": 30,      # Tree Authority
    "HERITAGE": 60,      # Heritage Committee
    "CRZ": 90,          # Coastal Regulation Zone
    "LABOUR_CESS": 7,    # Labour cess registration
    "GST": 7,           # GST registration
}

# AAI NOC fees - AAI circular 2023
AAI_NOC_FEES = {
    "<45m": 10000.0,
    "45-100m": 25000.0,
    "100m+": 50000.0,
}


@dataclass
class ClearanceItem:
    """A single clearance requirement."""
    name: str
    description: str
    timeline_days: int
    fee: float
    risk_level: str  # "low", "medium", "high"
    depends_on: List[str] = field(default_factory=list)
    notes: str = ""


def resolve_clearances(
    height_m: float,
    bua_sqm: float,
    plot_area_sqm: float,
    distance_to_csia_km: float,
    distance_to_coast_km: float,
    ward: str,
    use: str
) -> List[Dict[str, Any]]:
    """
    Identify all clearances triggered by project parameters.
    
    Args:
        height_m: Building height in meters
        bua_sqm: Built-up area in sq.m
        plot_area_sqm: Plot area in sq.m
        distance_to_csia_km: Distance to CSIA airport
        distance_to_coast_km: Distance to coastline
        ward: MCGM ward
        use: Building use type
    
    Returns:
        List of ClearanceItem dictionaries
    """
    clearances = []
    heritage_wards = ["A", "B", "C", "D", "E", "F"]
    railway_wards = ["L", "M", "N", "P", "R"]
    
    # 1. IOD (Intimation of Disapproval) - Always required
    clearances.append({
        "name": "IOD",
        "description": "Intimation of Disapproval from MCGM",
        "timeline_days": CLEARANCE_TIMELINES["IOD"],
        "fee": 5000.0,  # MCGM application fee
        "risk_level": "low",
        "depends_on": [],
        "notes": "First clearance required before starting construction"
    })
    
    # 2. CC (Commencement Certificate) - Always required after IOD
    clearances.append({
        "name": "CC",
        "description": "Commencement Certificate from MCGM",
        "timeline_days": CLEARANCE_TIMELINES["CC"],
        "fee": 10000.0,
        "risk_level": "low",
        "depends_on": ["IOD"],
        "notes": "Required before laying foundation"
    })
    
    # 3. Fire NOC - Required if height > 32m
    if height_m > 32:
        clearances.append({
            "name": "FIRE_NOC",
            "description": "Fire NOC from Mumbai Fire Brigade",
            "timeline_days": CLEARANCE_TIMELINES["FIRE_NOC"],
            "fee": 25000.0,
            "risk_level": "medium",
            "depends_on": ["IOD"],
            "notes": f"Mandatory for high-rise buildings >32m ({height_m:.1f}m proposed)"
        })
    
    # 4. AAI NOC - Required if within 5km of airport
    if distance_to_csia_km <= 5.0:
        fee_key = "<45m" if height_m <= 45 else ("45-100m" if height_m <= 100 else "100m+")
        fee = AAI_NOC_FEES[fee_key]
        clearances.append({
            "name": "AAI_NOC",
            "description": f"Airport Authority NOC (CSIA funnel zone, {distance_to_csia_km:.1f}km)",
            "timeline_days": CLEARANCE_TIMELINES["AAI_NOC"],
            "fee": fee,
            "risk_level": "high" if height_m > 45 else "medium",
            "depends_on": ["IOD"],
            "notes": f"Height {height_m:.1f}m within 5km funnel zone. Fee: ₹{fee:,.0f}"
        })
    
    # 5. Pollution NOC - Required for commercial/industrial >5000 sq.m
    if use in ["commercial", "industrial"] and bua_sqm > 5000:
        clearances.append({
            "name": "POLLUTION_NOC",
            "description": "Maharashtra Pollution Control Board NOC",
            "timeline_days": CLEARANCE_TIMELINES["POLLUTION_NOC"],
            "fee": 15000.0,
            "risk_level": "medium",
            "depends_on": ["IOD"],
            "notes": f"Applicable for {use} use with BUA {bua_sqm:.0f} sq.m > 5000 threshold"
        })
    
    # 6. Tree Cutting Permission - If trees need to be cut
    if plot_area_sqm > 1000:  # Larger plots likely have trees
        clearances.append({
            "name": "TREE_CUT",
            "description": "Tree Authority permission for cutting/transplanting",
            "timeline_days": CLEARANCE_TIMELINES["TREE_CUT"],
            "fee": 5000.0,  # Per tree approx
            "risk_level": "low",
            "depends_on": ["IOD"],
            "notes": "Fee is per tree. Assessment done on-site by Tree Authority"
        })
    
    # 7. Heritage Clearance - If in heritage ward
    if ward.upper() in heritage_wards:
        clearances.append({
            "name": "HERITAGE",
            "description": f"Heritage Committee clearance (Ward {ward})",
            "timeline_days": CLEARANCE_TIMELINES["HERITAGE"],
            "fee": 50000.0,
            "risk_level": "high",
            "depends_on": ["IOD"],
            "notes": "Heritage precinct requires special architectural review. High risk of design changes."
        })
    
    # 8. CRZ Clearance - If within 500m of coastline
    if distance_to_coast_km <= 0.5:
        clearances.append({
            "name": "CRZ",
            "description": f"Coastal Regulation Zone clearance ({distance_to_coast_km:.2f}km from coast)",
            "timeline_days": CLEARANCE_TIMELINES["CRZ"],
            "fee": 100000.0,
            "risk_level": "high",
            "depends_on": ["IOD"],
            "notes": "CRZ notification applies. May restrict FSI to 0.5. High rejection risk."
        })
    
    # 9. OC (Occupancy Certificate) - End of project
    clearances.append({
        "name": "OC",
        "description": "Occupancy Certificate from MCGM",
        "timeline_days": CLEARANCE_TIMELINES["OC"],
        "fee": 15000.0,
        "risk_level": "low",
        "depends_on": ["CC", "FIRE_NOC", "AAI_NOC", "POLLUTION_NOC", "TREE_CUT", "HERITAGE", "CRZ"],
        "notes": "Final clearance to occupy building. Depends on all earlier clearances"
    })
    
    return clearances


def calculate_critical_path(clearances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate the critical path (longest dependency chain) for clearances.
    
    Returns:
        Dictionary with total_days, critical_sequence, and bottleneck
    """
    # Build dependency graph
    clearance_map = {c["name"]: c for c in clearances}
    
    # Simple critical path: find longest chain
    def get_chain(name: str, visited: set) -> List[str]:
        if name in visited or name not in clearance_map:
            return []
        visited.add(name)
        clearance = clearance_map[name]
        if not clearance["depends_on"]:
            return [name]
        
        longest = []
        for dep in clearance["depends_on"]:
            chain = get_chain(dep, visited)
            if len(chain) > len(longest):
                longest = chain
        return longest + [name]
    
    # Find the clearance with longest chain
    all_chains = []
    for c in clearances:
        chain = get_chain(c["name"], set())
        all_chains.append((c["name"], len(chain), chain))
    
    # Sort by chain length
    all_chains.sort(key=lambda x: x[1], reverse=True)
    
    if all_chains:
        bottleneck_name, _, bottleneck_chain = all_chains[0]
        bottleneck = clearance_map[bottleneck_name]
        total_days = sum(clearance_map[c]["timeline_days"] for c in bottleneck_chain if c in clearance_map)
        
        return {
            "critical_sequence": bottleneck_chain,
            "total_days": total_days,
            "bottleneck": bottleneck_name,
            "bottleneck_risk": bottleneck["risk_level"],
        }
    
    return {"critical_sequence": [], "total_days": 0, "bottleneck": None, "bottleneck_risk": "low"}
