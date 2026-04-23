"""Mumbai DCPR-2034 knowledge module for Feasify."""
from .dcpr import (
    MumbaiZone, BuildingUse, RoadWidth, FinishGrade,
    FSIProfile, FSI_TABLE, get_fsi, classify_road_width,
    FUNGIBLE_RULES, compute_fungible_area,
    SetbackRequirement, SETBACK_TABLE_A, RELAXED_SETBACKS_TABLE_17, get_setback_requirement,
    max_permissible_height, HEIGHT_STEPBACK_RULES,
    PARKING_NORMS,
    PREMIUM_RULES, TENEMENT_DENSITY, SPECIAL_FSI,
    FeasibilityInput, FeasibilityOutput, calculate_feasibility,
    AGENT_KNOWLEDGE_PROMPT
)

__all__ = [
    "MumbaiZone", "BuildingUse", "RoadWidth", "FinishGrade",
    "FSIProfile", "FSI_TABLE", "get_fsi", "classify_road_width",
    "FUNGIBLE_RULES", "compute_fungible_area",
    "SetbackRequirement", "SETBACK_TABLE_A", "RELAXED_SETBACKS_TABLE_17", "get_setback_requirement",
    "max_permissible_height", "HEIGHT_STEPBACK_RULES",
    "PARKING_NORMS",
    "PREMIUM_RULES", "TENEMENT_DENSITY", "SPECIAL_FSI",
    "FeasibilityInput", "FeasibilityOutput", "calculate_feasibility",
    "AGENT_KNOWLEDGE_PROMPT"
]
