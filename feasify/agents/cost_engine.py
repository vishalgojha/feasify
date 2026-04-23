"""Cost engine - calculate all project costs including government premiums and professional fees."""
from typing import Dict, Any
from dataclasses import dataclass, field
from feasify.agents.constants import (
    MUMBAI_ASR_LAND_RATE_PER_SQM,
    PWD_BASE_RATES,
    ZONE_MULTIPLIERS,
    AAI_NOC_FEES,
    MCGM_INFRA_LEVY_PER_SQM,
    MCGM_DEVELOPMENT_CESS_PCT,
    ARCHITECT_FEE_PCT,
    PMC_FEE_PCT,
    LEGAL_FEE_FLAT,
    LIAISON_FEE_PCT,
    LABOUR_CESS_PCT,
    GST_PCT,
)
from feasify.agents.live_rates import (
    get_construction_rates,
)
import logging

logger = logging.getLogger(__name__)


@dataclass
class CostBreakdown:
    """Complete cost breakdown for a project."""
    # Land
    land_cost: float = 0.0
    
    # Construction
    base_construction: float = 0.0
    contingency: float = 0.0
    overhead: float = 0.0
    total_construction: float = 0.0
    
    # Government premiums
    additional_fsi_premium: float = 0.0
    fungible_premium: float = 0.0
    development_cess: float = 0.0
    infrastructure_levy: float = 0.0
    total_government: float = 0.0
    
    # Professional fees
    architect_fee: float = 0.0
    pmc_fee: float = 0.0
    legal_fee: float = 0.0
    liaison_fee: float = 0.0
    total_professional: float = 0.0
    
    # Statutory
    clearances_total: float = 0.0
    labour_cess: float = 0.0
    gst: float = 0.0
    
    # Financing
    financing_cost: float = 0.0
    
    # Grand total
    grand_total: float = 0.0
    
    # Metadata
    bua_sqm: float = 0.0
    cost_per_sqft: float = 0.0


def calculate_government_premiums(
    plot_area_sqm: float,
    bua_sqm: float,
    fsi_used: float,
    zonal_basic_fsi: float,
    fungible_sqm: float,
    use: str,
    asr_rate_per_sqm: float = MUMBAI_ASR_LAND_RATE_PER_SQM
) -> Dict[str, Any]:
    """
    Calculate all government levies - premium FSI, fungible, cess, infrastructure.
    
    Args:
        plot_area_sqm: Plot area in sq.m
        bua_sqm: Built-up area in sq.m
        fsi_used: Effective FSI used
        zonal_basic_fsi: Basic FSI from zone
        fungible_sqm: Fungible area in sq.m
        use: Building use type
        asr_rate_per_sqm: ASR land rate per sq.m (FSI 1 basis)
    
    Returns:
        Dictionary with premium breakdown
    """
    # Additional FSI premium (50% of ASR for residential, 60% for commercial)
    premium_pct = 0.5 if use == "residential" else 0.6
    additional_fsi_area = bua_sqm - (plot_area_sqm * zonal_basic_fsi)
    additional_fsi_premium = max(0, additional_fsi_area * asr_rate_per_sqm * premium_pct)
    
    # Fungible premium (same rate, on fungible area)
    fungible_premium = fungible_sqm * asr_rate_per_sqm * premium_pct
    
    # Development cess (100% of DC on BUA above basic FSI)
    bua_above_basic = max(0, bua_sqm - (plot_area_sqm * zonal_basic_fsi))
    development_cess = bua_above_basic * (asr_rate_per_sqm * MCGM_DEVELOPMENT_CESS_PCT)
    
    # Infrastructure levy (MCGM charge per sq.m on BUA above basic)
    infrastructure_levy = bua_above_basic * MCGM_INFRA_LEVY_PER_SQM
    
    total = additional_fsi_premium + fungible_premium + development_cess + infrastructure_levy
    
    return {
        "additional_fsi_premium": round(additional_fsi_premium, 2),
        "fungible_premium": round(fungible_premium, 2),
        "development_cess": round(development_cess, 2),
        "infrastructure_levy": round(infrastructure_levy, 2),
        "total_government_premiums": round(total, 2),
        "basis": {
            "asr_rate_per_sqm": asr_rate_per_sqm,
            "premium_pct": premium_pct,
            "additional_fsi_area_sqm": round(additional_fsi_area, 2),
            "fungible_area_sqm": round(fungible_sqm, 2),
            "bua_above_basic_sqm": round(bua_above_basic, 2),
        }
    }


def calculate_professional_fees(
    base_construction_cost: float,
    ec_triggered: bool = False,
    heritage_triggered: bool = False
) -> Dict[str, Any]:
    """
    Calculate professional fees - architect, PMC, legal, liaison.
    
    Args:
        base_construction_cost: Base construction cost (excl. contingencies)
        ec_triggered: Whether EC clearance is required
        heritage_triggered: Whether heritage clearance is required
    
    Returns:
        Dictionary with professional fee breakdown
    """
    architect_fee = base_construction_cost * ARCHITECT_FEE_PCT
    pmc_fee = base_construction_cost * PMC_FEE_PCT
    legal_fee = LEGAL_FEE_FLAT
    liaison_fee = base_construction_cost * LIAISON_FEE_PCT
    
    # Additional fees for complex clearances
    if ec_triggered:
        architect_fee *= 1.2  # 20% extra for EC projects
    if heritage_triggered:
        architect_fee *= 1.5  # 50% extra for heritage
        pmc_fee *= 1.3
    
    total = architect_fee + pmc_fee + legal_fee + liaison_fee
    
    return {
        "architect_fee": round(architect_fee, 2),
        "pmc_fee": round(pmc_fee, 2),
        "legal_fee": round(legal_fee, 2),
        "liaison_fee": round(liaison_fee, 2),
        "total_professional_fees": round(total, 2),
    }


def calculate_financing_cost(
    land_cost: float,
    max_clearance_days: int,
    interest_rate_pct: float = 12.0  # Typical Indian real estate lending rate
) -> Dict[str, Any]:
    """
    Calculate financing cost from clearance timelines on land cost.
    
    Args:
        land_cost: Total land cost
        max_clearance_days: Longest clearance timeline (critical path)
        interest_rate_pct: Annual interest rate
    
    Returns:
        Dictionary with financing cost
    """
    years = max_clearance_days / 365.0
    interest_rate = interest_rate_pct / 100.0
    financing_cost = land_cost * interest_rate * years
    
    return {
        "land_cost": land_cost,
        "max_clearance_days": max_clearance_days,
        "interest_rate_pct": interest_rate_pct,
        "financing_cost": round(financing_cost, 2),
        "basis": f"{max_clearance_days} days at {interest_rate_pct}% p.a. on ₹{land_cost:,.0f}"
    }


def build_cost_stack(
    bua_sqft: float,
    zone_type: str,
    num_floors: int,
    base_construction_cost: float,
    clearance_fees: float,
    land_cost: float = 0.0,
    finish_grade: str = "standard",
    fsi_used: float = 1.0,
    zonal_basic_fsi: float = 1.0,
    fungible_sqm: float = 0.0,
    plot_area_sqm: float = 1000.0,
    use: str = "residential",
    max_clearance_days: int = 90,
    use_live_rates: bool = True
) -> Dict[str, Any]:
    """
    Build complete cost stack with all line items.
    Uses live rates if available, falls back to PWD_RATES.
    
    Returns:
        Dictionary with full cost breakdown
    """
    # Use live rates if requested
    if use_live_rates:
        try:
            from feasify.agents.live_rates import calculate_live_construction_cost
            live = calculate_live_construction_cost(
                area_sqft=bua_sqft,
                zone_type=zone_type,
                num_floors=num_floors,
                finish_grade=finish_grade,
                use_live_rates=True
            )
            # Override with live rate calculation
            base_construction_cost = live["total_cost"]
        except Exception as e:
            logger.warning(f"Failed to fetch live rates: {e}. Using PWD rates.")
    
    bua_sqm = bua_sqft / 10.764
    
    # Government premiums
    gov_premiums = calculate_government_premiums(
        plot_area_sqm, bua_sqm, fsi_used, zonal_basic_fsi, fungible_sqm, use
    )
    
    # Professional fees
    prof_fees = calculate_professional_fees(base_construction_cost)
    
    # Statutory
    labour_cess = base_construction_cost * LABOUR_CESS_PCT
    gst = base_construction_cost * GST_PCT
    
    # Financing
    financing = calculate_financing_cost(land_cost, max_clearance_days)
    
    # Totals
    total_construction = base_construction_cost  # Already includes contingency/overhead
    total_government = gov_premiums["total_government_premiums"]
    total_professional = prof_fees["total_professional_fees"]
    total_clearances = clearance_fees
    total_statutory = labour_cess + gst
    
    grand_total = (
        land_cost +
        total_construction +
        total_government +
        total_professional +
        total_clearances +
        total_statutory +
        financing["financing_cost"]
    )
    
    result = {
        "land_cost": round(land_cost, 2),
        "construction": {
            "base_construction": round(base_construction_cost, 2),
            "total_construction": round(total_construction, 2),
            "rate_source": live.get("base_rate_source", "PWD_RATES") if use_live_rates else "PWD_RATES",
            "material_prices": live.get("material_prices") if use_live_rates else None,
        },
        "government_premiums": gov_premiums,
        "professional_fees": prof_fees,
        "clearances": {
            "total_clearance_fees": round(total_clearances, 2),
        },
        "statutory": {
            "labour_cess": round(labour_cess, 2),
            "gst": round(gst, 2),
            "total_statutory": round(total_statutory, 2),
        },
        "financing": financing,
        "grand_total": round(grand_total, 2),
        "cost_per_sqft": round(grand_total / bua_sqft, 2) if bua_sqft > 0 else 0,
        "cost_per_sqm": round(grand_total / (bua_sqft / 10.764), 2) if bua_sqft > 0 else 0,
    }
    return result
