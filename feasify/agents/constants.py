"""Hardcoded rates and constants for Mumbai real estate projects.

All values include source comments. Update annually from respective sources.
"""

# ────────────────────────────────────────
# LAND RATES
# ────────────────────────────────────────

# Mumbai Suburban ASR 2024-25 — update annually from IGR Maharashtra
MUMBAI_ASR_LAND_RATE_PER_SQM = 120000  # ₹/sq.m for FSI 1 basis (avg suburban)
MUMBAI_ASR_LAND_RATE_PER_SQFT = MUMBAI_ASR_LAND_RATE_PER_SQM / 10.764

# Island City ASR (South Mumbai) — significantly higher
ISLAND_CITY_ASR_PER_SQM = 300000


# ────────────────────────────────────────
# PWD SCHEDULE OF RATES 2024
# Source: Maharashtra PWD, updated quarterly
# ────────────────────────────────────────

from typing import Dict

PWD_BASE_RATES: Dict[str, float] = {
    "basic": 1500.0,      # ₹/sq.ft - Economy grade
    "standard": 1800.0,   # ₹/sq.ft - Mid-market (default)
    "premium": 2500.0,   # ₹/sq.ft - Luxury grade
    "ultra_premium": 3500.0,  # ₹/sq.ft - Ultra luxury
}

# Zone multipliers (apply to base rate)
ZONE_MULTIPLIERS: Dict[str, float] = {
    "residential": 1.0,
    "commercial": 1.3,
    "industrial": 0.9,
    "public": 0.8,
    "green": 0.7,
    "special": 1.2,
}


# ────────────────────────────────────────
# AAI NOC FEES
# Source: AAI circular 2023 (Airport Authority of India)
# ────────────────────────────────────────

AAI_NOC_FEES: Dict[str, float] = {
    "<45m": 10000.0,    # Height < 45m
    "45-100m": 25000.0, # 45m to 100m
    ">100m": 50000.0,    # > 100m height
}
# Note: CSIA (Mumbai) and JNPA (Navi Mumbai) have 5km radius funnel zones


# ────────────────────────────────────────
# MCGM LEVIES
# Source: MCGM circular 2012 (updated periodically)
# ────────────────────────────────────────

MCGM_INFRA_LEVY_PER_SQM = 500  # ₹/sq.m on BUA above basic FSI
MCGM_DEVELOPMENT_CESS_PCT = 1.0  # 100% of DC on BUA above basic FSI


# ────────────────────────────────────────
# PROFESSIONAL FEES
# Source: AIA India Schedule of Fees 2023
# ────────────────────────────────────────

ARCHITECT_FEE_PCT = 0.025  # 2.5% of construction cost
PMC_FEE_PCT = 0.015      # 1.5% of construction cost
LEGAL_FEE_FLAT = 50000.0  # ₹ flat for liaison
LIAISON_FEE_PCT = 0.005    # 0.5% of construction cost


# ────────────────────────────────────────
# STATUTORY CESSES
# ────────────────────────────────────────

LABOUR_CESS_PCT = 0.01  # 1% - Building and Other Construction Workers Act
GST_PCT = 0.18            # 18% GST on construction services


# ────────────────────────────────────────
# CLEARANCE TIMELINES (in days)
# Source: MCGM citizen charter 2023
# ────────────────────────────────────────

CLEARANCE_TIMELINES = {
    "IOD": 30,          # Intimation of Disapproval (initial)
    "CC": 60,           # Commencement Certificate
    "OC": 45,          # Occupancy Certificate
    "AAI_NOC": 45,      # Airport NOC
    "FIRE_NOC": 30,      # Fire Brigade NOC (>32m)
    "POLLUTION_NOC": 15, # Maharashtra Pollution Control Board
    "TREE_CUT": 30,      # Tree Authority permission
    "HERITAGE": 60,      # Heritage committee clearance
    "CRZ": 90,          # CRZ clearance (if applicable)
}


# ────────────────────────────────────────
# COORDINATES FOR SPATIAL CALCULATIONS
# ────────────────────────────────────────

CSIA_COORDINATES = (19.0896, 72.8656)   # Chhatrapati Shivaji Airport
JNPA_COORDINATES = (19.0667, 73.0511)  # Jawaharlal Nehru Port
MARINE_DRIVE_COAST = (18.9437, 72.8232)  # Marine Drive coastline

# Funnel zone radius (5km from both airports)
AIRPORT_FUNNEL_RADIUS_KM = 5.0
COASTAL_BUFFER_KM = 0.5  # CRZ buffer from high tide line


# ────────────────────────────────────────
# HERITAGE & SPECIAL ZONES
# ────────────────────────────────────────

HERITAGE_WARDS = ["A", "B", "C", "D", "E"]  # South Mumbai heritage precincts
RAILWAY_BUFFER_WARDS = ["L", "M", "N"]  # Near Western/Dcentral Railway lines
