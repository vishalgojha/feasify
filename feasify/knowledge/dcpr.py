"""Mumbai DCPR-2034 Knowledge Module for Feasify AI Agent
Source: Development Control and Promotion Regulation 2034, MCGM
Effective: 13.11.2018 (Updated 07.12.2018)

This module provides structured, queryable knowledge from DCPR-2034
for use in cost estimation, feasibility analysis, and compliance checks.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ────────────────────────────────────────
# ENUMS
# ────────────────────────────────────────

class MumbaiZone(str, Enum):
    ISLAND_CITY = "island_city"               # South Mumbai (Colaba to Mahim/Sion)
    SUBURBS = "suburbs"                        # Western/Eastern suburbs
    EXTENDED_SUBURBS = "extended_suburbs"      # Borivali, Mulund, Thane fringe
    BARC_AREA = "barc_area"                    # BARC zone from M Ward (special)
    CRZ_AFFECTED = "crz_affected"              # Coastal Regulation Zone areas
    INDUSTRIAL = "industrial"


class BuildingUse(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"


class RoadWidth(str, Enum):
    NARROW = "less_than_9m"           # < 9m
    MEDIUM_LOW = "9m_to_12m"          # ≥9m < 12m
    MEDIUM = "12m_to_18m"             # ≥12m < 18m
    WIDE = "18m_to_27m"               # ≥18m < 27m
    VERY_WIDE = "27m_and_above"       # ≥27m


class FinishGrade(str, Enum):
    BASIC = "basic"         # Economy / affordable housing
    STANDARD = "standard"   # Mid-market residential/commercial
    PREMIUM = "premium"     # Luxury residential / Grade-A commercial


# ────────────────────────────────────────
# CORE DATA: FSI TABLE (Regulation 30, Table 12)
# ────────────────────────────────────────

@dataclass
class FSIProfile:
    """
    FSI breakdown as per DCPR-2034, Regulation 30, Table No. 12
    total_permissible = zonal_basic + additional_premium + admissible_tdr
    """
    zone: MumbaiZone
    use: BuildingUse
    road_width: RoadWidth
    zonal_basic: float          # Base FSI (no extra payment)
    additional_premium: float   # Additional FSI on payment of premium (50% of ASR)
    admissible_tdr: float       # TDR that can be loaded
    total_permissible: float    # Max possible FSI (col 7 of Table 12)
    notes: str = ""


# Regulation 30 Table 12 — Full FSI lookup table
FSI_TABLE: list[FSIProfile] = [

    # ── ISLAND CITY — Residential/Commercial ──────────────────────────
    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.NARROW,
               1.33, 0.50, 0.17, 2.0,
               "Island City <9m road. Basic FSI 1.33."),

    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.MEDIUM_LOW,
               1.33, 0.62, 0.45, 2.4,
               "Island City 9–12m road."),

    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.MEDIUM,
               1.33, 0.73, 0.64, 2.7,
               "Island City 12–18m road."),

    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.WIDE,
               1.33, 0.84, 0.83, 3.0,
               "Island City 18–27m road."),

    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.VERY_WIDE,
               1.33, 0.92, 0.75, 3.0,
               "Island City ≥27m road. Cap remains 3.0."),

    # Commercial same as residential in Island City (same table)
    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.COMMERCIAL, RoadWidth.NARROW,
               1.33, 0.50, 0.17, 2.0),
    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.COMMERCIAL, RoadWidth.MEDIUM_LOW,
               1.33, 0.62, 0.45, 2.4),
    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.COMMERCIAL, RoadWidth.MEDIUM,
               1.33, 0.73, 0.64, 2.7),
    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.COMMERCIAL, RoadWidth.WIDE,
               1.33, 0.84, 0.83, 3.0),
    FSIProfile(MumbaiZone.ISLAND_CITY, BuildingUse.COMMERCIAL, RoadWidth.VERY_WIDE,
               1.33, 0.92, 0.75, 3.0),

    # ── SUBURBS / EXTENDED SUBURBS — Residential/Commercial ───────────────
    # General suburbs (remaining area excl. BARC / CRZ)
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.NARROW,
               1.0, 0.5, 0.0, 1.5,
               "Suburbs <9m road. No TDR."),

    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.MEDIUM_LOW,
               1.0, 0.5, 0.5, 2.0,
               "Suburbs 9–12m road."),

    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.MEDIUM,
               1.0, 0.5, 0.7, 2.2,
               "Suburbs 12–18m road."),

    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.WIDE,
               1.0, 0.5, 0.9, 2.4,
               "Suburbs 18–27m road."),

    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.VERY_WIDE,
               1.0, 0.5, 1.0, 2.5,
               "Suburbs ≥27m road."),

    # Commercial same as residential in suburbs
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.COMMERCIAL, RoadWidth.NARROW,
               1.0, 0.5, 0.0, 1.5),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.COMMERCIAL, RoadWidth.MEDIUM_LOW,
               1.0, 0.5, 0.5, 2.0),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.COMMERCIAL, RoadWidth.MEDIUM,
               1.0, 0.5, 0.7, 2.2),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.COMMERCIAL, RoadWidth.WIDE,
               1.0, 0.5, 0.9, 2.4),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.COMMERCIAL, RoadWidth.VERY_WIDE,
               1.0, 0.5, 1.0, 2.5),

    # Industrial — Suburbs
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.INDUSTRIAL, RoadWidth.NARROW,
               1.0, 0.0, 0.0, 1.0,
               "Industrial, no premium/TDR on narrow road."),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.INDUSTRIAL, RoadWidth.MEDIUM_LOW,
               1.0, 0.0, 0.0, 1.0),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.INDUSTRIAL, RoadWidth.MEDIUM,
               1.0, 0.5, 0.0, 1.0),
    FSIProfile(MumbaiZone.SUBURBS, BuildingUse.INDUSTRIAL, RoadWidth.WIDE,
               1.0, 0.5, 0.0, 1.0),

    # ── BARC / Special Zone ────────────────────────────────────────────
    FSIProfile(MumbaiZone.BARC_AREA, BuildingUse.RESIDENTIAL, RoadWidth.NARROW,
               0.5, 0.0, 0.0, 0.5,
               "BARC zone (M Ward area) — highly restricted."),

    # ── CRZ Affected (Aksa, Marve, Erangal excl. gaothan) ────────────────
    FSIProfile(MumbaiZone.CRZ_AFFECTED, BuildingUse.RESIDENTIAL, RoadWidth.NARROW,
               0.5, 0.0, 0.0, 0.5,
               "CRZ affected areas. Max FSI 0.5 — check CRZ notification separately."),
]


def get_fsi(zone: MumbaiZone, use: BuildingUse, road_width: RoadWidth) -> Optional[FSIProfile]:
    """Look up FSI profile. Falls back to SUBURBS if EXTENDED_SUBURBS not found."""
    for p in FSI_TABLE:
        if p.zone == zone and p.use == use and p.road_width == road_width:
            return p
    # Fallback: extended suburbs = suburbs
    if zone == MumbaiZone.EXTENDED_SUBURBS:
        return get_fsi(MumbaiZone.SUBURBS, use, road_width)
    return None


def classify_road_width(width_m: float) -> RoadWidth:
    """Convert numeric road width to RoadWidth enum."""
    if width_m < 9:
        return RoadWidth.NARROW
    elif width_m < 12:
        return RoadWidth.MEDIUM_LOW
    elif width_m < 18:
        return RoadWidth.MEDIUM
    elif width_m < 27:
        return RoadWidth.WIDE
    else:
        return RoadWidth.VERY_WIDE


# ────────────────────────────────────────
# FUNGIBLE COMPENSATORY AREA (Regulation 31(3))
# ────────────────────────────────────────

FUNGIBLE_RULES = {
    "max_over_permissible_fsi_pct": 35,       # Up to 35% over permissible FSI
    "premium_residential_pct": 50,            # 50% of ASR (for FSI 1) land rate
    "premium_commercial_pct": 60,             # 60% of ASR (for FSI 1) land rate
    "premium_industrial_pct": 60,
    "premium_sharing": {                       # How premium is split
        "MCGM": 50,
        "State_Govt": 30,
        "MSRDC": 20
    },
    "free_fungible_cases": [
        "Redevelopment under Reg 33(7), 33(7A), 33(8), 33(9), 33(9B), 33(20), 33(10) — AH/R&R component",
        "Redevelopment under Reg 33(5), 33(6), 33(7B) — existing BUA portion",
        "Redevelopment availing TDR/Addl FSI on premium — existing BUA portion if use continues",
        "Development under Reg 33(15)",
        "MCGM/State Govt under Reg 33(3)"
    ],
    "note": "Fungible area is usable as regular FSI. Cannot be transferred between rehab tenements."
}


def compute_fungible_area(permissible_bua_sqm: float, use: BuildingUse) -> dict:
    """
    Compute max fungible compensatory area and indicative premium basis.
    Premium rupee amount depends on current ASR rates (not hardcoded here).
    """
    max_fungible = permissible_bua_sqm * 0.35
    premium_pct = (
        FUNGIBLE_RULES["premium_residential_pct"] if use == BuildingUse.RESIDENTIAL
        else FUNGIBLE_RULES["premium_commercial_pct"]
    )
    return {
        "max_fungible_sqm": round(max_fungible, 2),
        "total_max_bua_with_fungible": round(permissible_bua_sqm * 1.35, 2),
        "premium_rate": f"{premium_pct}% of ASR land rate (FSI 1 basis)",
        "premium_sharing": FUNGIBLE_RULES["premium_sharing"],
    }


# ────────────────────────────────────────
# SETBACKS / OPEN SPACES (Regulation 42, Table A)
# ────────────────────────────────────────

@dataclass
class SetbackRequirement:
    building_height_range: str
    plot_size_category: str          # "upto_1000sqm" or "above_1000sqm"
    side_rear_light_vent: str        # Rule expression
    side_rear_dead_wall: str
    notes: str = ""


SETBACK_TABLE_A = [
    # Plot ≤1000 sqm OR avg width/depth <20m
    SetbackRequirement(
        "Up to 32m",
        "upto_1000sqm",
        "Min 3.6m (residential) / 4.5m (commercial), subject to H/5",
        "3.6m",
        "H = building height. Side/rear for light & vent = max(min_value, H/5)"
    ),
    SetbackRequirement(
        ">32m up to 70m",
        "upto_1000sqm",
        "H/5, max 12m",
        "6m",
    ),
    SetbackRequirement(
        ">70m up to 120m",
        "upto_1000sqm",
        "H/5, max 12m",
        "6m",
        "High-rise fire safety requirements mandatory"
    ),
    SetbackRequirement(
        ">120m",
        "upto_1000sqm",
        "Refer fire authority",
        "9m",
    ),

    # Plot >1000 sqm AND avg width/depth ≥20m
    SetbackRequirement(
        "Up to 32m",
        "above_1000sqm",
        "Min 3.6m (residential) / 4.5m (commercial), subject to H/4",
        "3.6m",
        "H/4 rule gives larger setbacks on bigger plots"
    ),
    SetbackRequirement(
        ">32m up to 70m",
        "above_1000sqm",
        "H/4, max 12m",
        "6m",
    ),
    SetbackRequirement(
        ">70m up to 120m",
        "above_1000sqm",
        "H/4 or 16m max",
        "9m",
    ),
    SetbackRequirement(
        ">120m",
        "above_1000sqm",
        "20m max",
        "9m",
    ),
]

# Relaxed setbacks for G+1 or Stilt+2 buildings (Table No. 17)
RELAXED_SETBACKS_TABLE_17 = [
    {"plot_sqm_range": (21, 30),   "type": "Row",           "front": 0.75, "rear": 1.5,  "side": None},
    {"plot_sqm_range": (30, 40),   "type": "Row",           "front": 0.75, "rear": 2.25, "side": None},
    {"plot_sqm_range": (40, 60),   "type": "Row/Semi-det",  "front": 1.0,  "rear": 2.25, "side": 1.0},
    {"plot_sqm_range": (60, 125),  "type": "Row/Semi-det",  "front": 1.5,  "rear": 3.0,  "side": 1.0},
    {"plot_sqm_range": (125, 250), "type": "Row/Semi/Det",  "front": 3.0,  "rear": 3.0,  "side": 1.5},
]


def get_setback_requirement(
    height_m: float,
    plot_area_sqm: float,
    plot_avg_dimension_m: float,
    use: BuildingUse
) -> dict:
    """
    Returns applicable setback rules for a given building height and plot.
    """
    if height_m <= 32:
        h_range = "Up to 32m"
    elif height_m <= 70:
        h_range = ">32m up to 70m"
    elif height_m <= 120:
        h_range = ">70m up to 120m"
    else:
        h_range = ">120m"

    size_cat = "upto_1000sqm" if (plot_area_sqm <= 1000 or plot_avg_dimension_m < 20) else "above_1000sqm"

    for row in SETBACK_TABLE_A:
        if row.building_height_range == h_range and row.plot_size_category == size_cat:
            # Compute actual numeric setback
            divisor = 5 if size_cat == "upto_1000sqm" else 4
            min_val = 3.6 if use == BuildingUse.RESIDENTIAL else 4.5
            computed_side = round(max(min_val, height_m / divisor), 2)
            if h_range == "Up to 32m":
                side_vent = computed_side
            elif h_range in (">32m up to 70m", ">70m up to 120m") and size_cat == "upto_1000sqm":
                side_vent = min(round(height_m / divisor, 2), 12)
            elif h_range == ">32m up to 70m" and size_cat == "above_1000sqm":
                side_vent = min(round(height_m / divisor, 2), 12)
            elif h_range == ">70m up to 120m" and size_cat == "above_1000sqm":
                side_vent = min(round(height_m / divisor, 2), 16)
            elif h_range == ">120m":
                side_vent = 20
            else:
                side_vent = computed_side

            return {
                "height_range": h_range,
                "plot_category": size_cat,
                "side_rear_light_vent_m": side_vent,
                "side_rear_dead_wall_m": float(row.side_rear_dead_wall.replace("m", "").strip()),
                "rule_expression": row.side_rear_light_vent,
                "notes": row.notes,
                "high_rise": height_m > 32,
                "fire_noc_required": height_m > 32,
            }
    return {}


# ────────────────────────────────────────
# HEIGHT REGULATIONS (Regulation 43)
# ────────────────────────────────────────

def max_permissible_height(road_width_m: float, front_setback_m: float) -> float:
    """
    Reg 43(1): Height ≤ 3 × (road_width + front_setback).
    Restriction ceases if road ≥9m AND front setback ≥9m (or ≥12m if road >12m).
    Returns effective height limit in meters. Returns float('inf') if unrestricted.
    """
    # Restriction ceases clause
    if road_width_m >= 9 and front_setback_m >= 9:
        return float('inf')
    return 3 * (road_width_m + front_setback_m)


HEIGHT_STEPBACK_RULES = {
    "up_to_32m": "No stepback required",
    "32m_to_70m": "6m open space at ground (rear + 1 side), 9m on road-accessible side. 1 stepback at upper levels.",
    "70m_to_120m": "9m open space at ground on all sides. 3 stepbacks at upper levels.",
    "above_120m": "9m open space. 4 stepbacks above 120m level.",
    "note": "Stepbacks must maintain required open spaces at each level. Terrace from stepback accessible via common passage only."
}


# ────────────────────────────────────────
# PARKING REQUIREMENTS (Regulation 44, Table 21)
# ────────────────────────────────────────

PARKING_NORMS = {
    BuildingUse.RESIDENTIAL: [
        {"carpet_sqm_range": (0, 45),   "tenements_per_space": 4,   "note": "1 space per 4 units ≤45sqm carpet"},
        {"carpet_sqm_range": (45, 60),  "tenements_per_space": 2,   "note": "1 space per 2 units 45–60sqm"},
        {"carpet_sqm_range": (60, 90),  "tenements_per_space": 1,   "note": "1 space per unit 60–90sqm"},
        {"carpet_sqm_range": (90, 9999),"tenements_per_space": 0.5, "note": "2 spaces per unit >90sqm"},
    ],
    BuildingUse.COMMERCIAL: {
        "office_upto_1500sqm": "1 space per 37.5 sqm",
        "office_above_1500sqm": "1 space per 75 sqm",
        "mercantile_upto_800sqm": "1 space per 40 sqm",
        "mercantile_above_800sqm": "1 space per 80 sqm (min 50sqm free)",
        "visitor_parking": "25% of computed spaces, min 1"
    },
    BuildingUse.INDUSTRIAL: "1 space per 150 sqm, min 2 spaces",
    "parking_space_size_m": "2.5m × 5.5m (motor vehicle); up to 50% can be 2.3×4.5m",
    "visitor_parking_pct": 25,
    "note": "Gaothan/Koliwada/Adivasi Pada on narrow plots (≤9m) — parking may be waived"
}


# ────────────────────────────────────────
# DEVELOPMENT CHARGES & PREMIUM SUMMARY
# ────────────────────────────────────────

PREMIUM_RULES = {
    "additional_fsi_premium": {
        "rate": "50% of ASR land rate (FSI 1 basis) for the year of grant",
        "sharing": {"State_Govt": 25, "MCGM": 25, "MSRDC": 25, "Dharavi_Authority": 25},
        "applicability": "Optional. Can be used before or after TDR in any sequence. Non-transferable.",
        "note": "Addl FSI on premium is granted on application and used on same plot only."
    },
    "development_cess": {
        "rate": "100% of Development Charge on BUA over Zonal Basic FSI",
        "excludes": ["Fungible compensatory area", "BUA handed to MCGM", "FSI-excluded BUA"],
        "note": "In addition to DC under MR&TP Act 1966. Not applicable to Govt/MCGM departmental works."
    },
    "fungible_premium": {
        "residential": "50% of ASR (FSI 1 basis)",
        "commercial_industrial": "60% of ASR (FSI 1 basis)",
        "sharing": {"MCGM": 50, "State_Govt": 30, "MSRDC": 20}
    }
}


# ────────────────────────────────────────
# TENEMENT DENSITY (Regulation 30B)
# ────────────────────────────────────────

TENEMENT_DENSITY = {
    "max_per_ha_at_fsi_1": 450,
    "min_affordable_housing_per_ha_at_fsi_1": 325,
    "scaling": "Proportionally increase/decrease with FSI. e.g. FSI 2.0 → max 900 tenements/ha"
}


# ────────────────────────────────────────
# SPECIAL FSI PROVISIONS (commonly used)
# ────────────────────────────────────────

SPECIAL_FSI = {
    "pre_1969_buildings": {
        "fsi": 3.0,
        "note": "Buildings existing in MCGM area prior to 30.09.1969 get FSI 3.0 on gross plot for redevelopment."
    },
    "slum_rehabilitation_cds": {
        "max_fsi": 4.0,
        "note": "Cluster Development Scheme / SRA schemes. FSI 4.0 on gross plot."
    },
    "affordable_housing": {
        "max_fsi": 2.5,
        "large_plot_above_4000sqm": 4.0,
        "note": "AH plots. FSI up to 4.0 for plots >4000sqm."
    },
    "existing_housing_society_redevelopment": {
        "max_fsi": 3.0,
        "note": "Reg 33(7) redevelopment of existing residential societies."
    },
    "industrial_zone_to_residential": {
        "note": "Conversion permissible. FSI as per residential/commercial zone rates post conversion."
    }
}


# ────────────────────────────────────────
# MAIN FEASIBILITY CALCULATOR
# ────────────────────────────────────────

@dataclass
class FeasibilityInput:
    plot_area_sqm: float
    zone: MumbaiZone
    use: BuildingUse
    road_width_m: float
    floors: int                          # Number of floors above ground (G = 1)
    floor_to_floor_height_m: float = 3.0 # Default 3m per floor
    plot_avg_dimension_m: float = 20.0   # For setback calc
    include_fungible: bool = False        # Whether to include fungible 35% bonus
    finish_grade: FinishGrade = FinishGrade.STANDARD


@dataclass
class FeasibilityOutput:
    # FSI
    zonal_basic_fsi: float
    max_permissible_fsi: float
    effective_fsi_used: float

    # Area
    permissible_bua_sqm: float
    permissible_bua_sqft: float
    fungible_bonus_sqm: float
    total_max_bua_sqm: float

    # Building geometry
    approx_height_m: float
    floors_feasible: int

    # Setbacks
    setback_side_rear_m: float
    setback_dead_wall_m: float
    high_rise: bool
    fire_noc_required: bool

    # Parking
    parking_spaces_required: int

    # Tenement density
    max_tenements: int

    # Warnings / flags
    warnings: list[str] = field(default_factory=list)


def calculate_feasibility(inp: FeasibilityInput) -> FeasibilityOutput:
    """
    Core feasibility calculator integrating DCPR-2034 rules.
    Returns permissible BUA, setbacks, height, parking, tenement density.
    """
    warnings = []

    road_w = classify_road_width(inp.road_width_m)
    fsi_profile = get_fsi(inp.zone, inp.use, road_w)

    if not fsi_profile:
        warnings.append(f"FSI profile not found for zone={inp.zone}, use={inp.use}, road={road_w}. Using defaults.")
        zonal_fsi = 1.0
        max_fsi = 1.5
    else:
        zonal_fsi = fsi_profile.zonal_basic
        max_fsi = fsi_profile.total_permissible

    # BUA
    permissible_bua = inp.plot_area_sqm * max_fsi
    permissible_bua_sqft = permissible_bua * 10.764

    # Fungible
    fungible_sqm = 0.0
    total_max_bua = permissible_bua
    if inp.include_fungible:
        fc = compute_fungible_area(permissible_bua, inp.use)
        fungible_sqm = fc["max_fungible_sqm"]
        total_max_bua = fc["total_max_bua_with_fungible"]

    # Height
    approx_height = inp.floors * inp.floor_to_floor_height_m
    height_limit = max_permissible_height(inp.road_width_m, 3.0)  # Assume 3m front setback
    floors_feasible = inp.floors
    if approx_height > height_limit:
        warnings.append(
            f"Proposed height {approx_height}m exceeds 3×(road+setback) limit of {height_limit}m. "
            f"Increase road width or front setback, or reduce floors."
        )
        floors_feasible = int(height_limit / inp.floor_to_floor_height_m)

    if inp.road_width_m < 9 and approx_height > 32:
        warnings.append("Road width <9m: height above 32m requires minimum 9m road. Check Reg 43.")

    # Setbacks
    sb = get_setback_requirement(approx_height, inp.plot_area_sqm, inp.plot_avg_dimension_m, inp.use)
    side_rear_m = sb.get("side_rear_light_vent_m", 3.6)
    dead_wall_m = sb.get("side_rear_dead_wall_m", 3.6)
    high_rise = sb.get("high_rise", False)
    fire_noc = sb.get("fire_noc_mandatory", False)

    if high_rise:
        warnings.append("High-rise building (>32m): Fire NOC from Mumbai Fire Brigade mandatory before IOD.")

    # Parking
    parking = 0
    if inp.use == BuildingUse.RESIDENTIAL:
        avg_carpet = 60  # Default assumption — standard 2BHK
        tenements = int(total_max_bua / (avg_carpet / 0.7))  # carpet ≈ 70% of BUA
        if avg_carpet <= 45:
            parking = max(1, tenements // 4)
        elif avg_carpet <= 60:
            parking = max(1, tenements // 2)
        elif avg_carpet <= 90:
            parking = tenements
        else:
            parking = tenements * 2
        parking = int(parking * 1.25)  # +25% visitor parking
    elif inp.use == BuildingUse.COMMERCIAL:
        parking = max(1, int(total_max_bua / 37.5))
    else:
        parking = max(2, int(total_max_bua / 150))

    # Tenement density
    area_ha = inp.plot_area_sqm / 10000
    max_tenements = int(TENEMENT_DENSITY["max_per_ha_at_fsi_1"] * max_fsi * area_ha)

    # CRZ warning
    if inp.zone == MumbaiZone.CRZ_AFFECTED:
        warnings.append("CRZ affected zone: Verify CRZ notification separately. FSI may be further restricted.")

    return FeasibilityOutput(
        zonal_basic_fsi=zonal_fsi,
        max_permissible_fsi=max_fsi,
        effective_fsi_used=max_fsi,
        permissible_bua_sqm=round(permissible_bua, 2),
        permissible_bua_sqft=round(permissible_bua_sqft, 2),
        fungible_bonus_sqm=round(fungible_sqm, 2),
        total_max_bua_sqm=round(total_max_bua, 2),
        approx_height_m=approx_height,
        floors_feasible=floors_feasible,
        setback_side_rear_m=side_rear_m,
        setback_dead_wall_m=dead_wall_m,
        high_rise=high_rise,
        fire_noc_required=fire_noc,
        parking_spaces_required=parking,
        max_tenements=max_tenements,
        warnings=warnings,
    )


# ────────────────────────────────────────
# AI AGENT SYSTEM PROMPT FRAGMENT
# (inject this into your agent's system prompt)
# ────────────────────────────────────────

AGENT_KNOWLEDGE_PROMPT = """
## Mumbai DCPR-2034 Knowledge Base

You have access to structured knowledge from Mumbai's Development Control and Promotion Regulation 2034 (MCGM). Use it for all Mumbai real estate feasibility queries.

### FSI Rules (Regulation 30, Table 12)
**Island City** (South Mumbai, Colaba to Sion/Mahim):
- Basic FSI: 1.33 across all road widths
- Max permissible FSI: 2.0 (<9m road) → 2.4 (9–12m) → 2.7 (12–18m) → 3.0 (18m+)

**Suburbs & Extended Suburbs** (Bandra to Borivali/Mulund):
- Basic FSI: 1.0
- Max permissible FSI: 1.5 (<9m) → 2.0 (9–12m) → 2.2 (12–18m) → 2.4 (18–27m) → 2.5 (27m+)

**Special cases**: Pre-1969 buildings → FSI 3.0. SRA/CDS schemes → FSI 4.0. Redevelopment societies → FSI 3.0.

**Fungible Compensatory Area** (Reg 31(3)): Up to 35% additional BUA above permissible FSI, on payment of premium (50% of ASR for residential, 60% for commercial).

### Setbacks (Regulation 42, Table A)
Buildings up to 32m height:
- Plot ≤1000sqm: Side/rear = max(3.6m, H/5) for residential; max(4.5m, H/5) for commercial
- Plot >1000sqm: Side/rear = max(3.6m, H/4) for residential; max(4.5m, H/4) for commercial

Buildings 32–70m: H/5 (small plot) or H/4 (large plot), max 12m
Buildings 70–120m: H/4, max 16m (large plot); or 20m (>120m)

For low-rise (G+1 or Stilt+2): Relaxed setbacks per Table 17 down to 0.75m front on small plots.

### Height (Regulation 43)
Max height = 3 × (road width + front setback). Restriction removed if road ≥9m AND front setback ≥9m.
High-rise (>32m): Fire NOC mandatory. Stepbacks required above 32m.

### Parking (Regulation 44, Table 21)
Residential: 1 space per 4 units (≤45sqm carpet) / 2 units (45–60sqm) / 1 unit (60–90sqm) / 0.5 units (>90sqm) + 25% visitor
Commercial offices: 1 space per 37.5sqm (up to 1500sqm), per 75sqm above
Industrial: 1 per 150sqm, min 2

### Premium Charges
Additional FSI premium: 50% of ASR land rate (FSI 1 basis)
Development cess: 100% of DC on BUA above basic FSI
Fungible premium: 50% (residential) / 60% (commercial/industrial) of ASR

### Always flag
- CRZ zones require separate CRZ notification check
- BARC area (M Ward) heavily restricted
- Airport height restrictions apply near CSIA/JNPA
- Railway buffer zones have separate height rules
- Heritage precincts have special provisions
"""


# ────────────────────────────────────────
# QUICK TEST
# ────────────────────────────────────────

if __name__ == "__main__":
    # Test: 500sqm plot, Andheri (suburbs), residential, 15m road, G+10 building
    test = FeasibilityInput(
        plot_area_sqm=500,
        zone=MumbaiZone.SUBURBS,
        use=BuildingUse.RESIDENTIAL,
        road_width_m=15,
        floors=10,
        floor_to_floor_height_m=3.0,
        plot_avg_dimension_m=22.0,
        include_fungible=True,
        finish_grade=FinishGrade.STANDARD
    )

    result = calculate_feasibility(test)

    print("=" * 60)
    print("FEASIFY — DCPR 2034 Feasibility Output")
    print("=" * 60)
    print(f"Plot:              500 sqm | Suburbs | Residential | 15m road | G+10")
    print(f"Zonal Basic FSI:   {result.zonal_basic_fsi}")
    print(f"Max Perm. FSI:     {result.max_permissible_fsi}")
    print(f"Permissible BUA:   {result.permissible_bua_sqm} sqm ({result.permissible_bua_sqft:.0f} sqft)")
    print(f"Fungible (+35%):   +{result.fungible_bonus_sqm} sqm")
    print(f"Total Max BUA:     {result.total_max_bua_sqm} sqm")
    print(f"Building Height:   {result.approx_height_m}m ({test.floors} floors)")
    print(f"Floors Feasible:   {result.floors_feasible}")
    print(f"Side/Rear Setback: {result.setback_side_rear_m}m (light & vent)")
    print(f"Dead Wall Setback: {result.setback_dead_wall_m}m")
    print(f"High-Rise:         {result.high_rise}")
    print(f"Fire NOC Required: {result.fire_noc_required}")
    print(f"Parking Spaces:    {result.parking_spaces_required}")
    print(f"Max Tenements:     {result.max_tenements}")
    if result.warnings:
        print("\n⚠ WARNINGS:")
        for w in result.warnings:
            print(f"  • {w}")
    print("=" * 60)
