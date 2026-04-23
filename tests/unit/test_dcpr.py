"""Unit tests for Mumbai DCPR-2034 knowledge module."""
import pytest
from feasify.knowledge.dcpr import (
    MumbaiZone, BuildingUse, RoadWidth, FinishGrade,
    FSIProfile, FSI_TABLE, get_fsi, classify_road_width,
    FUNGIBLE_RULES, compute_fungible_area,
    SetbackRequirement, SETBACK_TABLE_A, get_setback_requirement,
    max_permissible_height, PARKING_NORMS,
    FeasibilityInput, calculate_feasibility
)


class TestRoadWidthClassification:
    """Test road width classification."""
    
    def test_narrow_road(self):
        assert classify_road_width(8.0) == RoadWidth.NARROW
        assert classify_road_width(5.0) == RoadWidth.NARROW
    
    def test_medium_low_road(self):
        assert classify_road_width(9.0) == RoadWidth.MEDIUM_LOW
        assert classify_road_width(11.0) == RoadWidth.MEDIUM_LOW
    
    def test_medium_road(self):
        assert classify_road_width(12.0) == RoadWidth.MEDIUM
        assert classify_road_width(15.0) == RoadWidth.MEDIUM
    
    def test_wide_road(self):
        assert classify_road_width(18.0) == RoadWidth.WIDE
        assert classify_road_width(25.0) == RoadWidth.WIDE
    
    def test_very_wide_road(self):
        assert classify_road_width(27.0) == RoadWidth.VERY_WIDE
        assert classify_road_width(50.0) == RoadWidth.VERY_WIDE


class TestFSILookup:
    """Test FSI table lookup."""
    
    def test_suburbs_residential_narrow_road(self):
        profile = get_fsi(MumbaiZone.SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.NARROW)
        assert profile is not None
        assert profile.zonal_basic == 1.0
        assert profile.total_permissible == 1.5
    
    def test_island_city_residential_wide_road(self):
        profile = get_fsi(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.WIDE)
        assert profile is not None
        assert profile.zonal_basic == 1.33
        assert profile.total_permissible == 3.0
    
    def test_island_city_commercial_same_as_residential(self):
        res = get_fsi(MumbaiZone.ISLAND_CITY, BuildingUse.RESIDENTIAL, RoadWidth.NARROW)
        comm = get_fsi(MumbaiZone.ISLAND_CITY, BuildingUse.COMMERCIAL, RoadWidth.NARROW)
        assert res.total_permissible == comm.total_permissible
    
    def test_extended_suburbs_falls_back_to_suburbs(self):
        profile = get_fsi(MumbaiZone.EXTENDED_SUBURBS, BuildingUse.RESIDENTIAL, RoadWidth.MEDIUM)
        assert profile is not None
        assert profile.zone == MumbaiZone.SUBURBS  # Fallback
    
    def test_barc_area_restricted(self):
        profile = get_fsi(MumbaiZone.BARC_AREA, BuildingUse.RESIDENTIAL, RoadWidth.NARROW)
        assert profile is not None
        assert profile.total_permissible == 0.5


class TestFungibleArea:
    """Test fungible compensatory area calculations."""
    
    def test_max_fungible_is_35_percent(self):
        result = compute_fungible_area(1000.0, BuildingUse.RESIDENTIAL)
        assert result["max_fungible_sqm"] == 350.0
        assert result["total_max_bua_with_fungible"] == 1350.0
    
    def test_residential_premium_rate(self):
        result = compute_fungible_area(1000.0, BuildingUse.RESIDENTIAL)
        assert "50%" in result["premium_rate"]
    
    def test_commercial_premium_rate(self):
        result = compute_fungible_area(1000.0, BuildingUse.COMMERCIAL)
        assert "60%" in result["premium_rate"]


class TestSetbacks:
    """Test setback requirement calculations."""
    
    def test_low_rise_small_plot(self):
        result = get_setback_requirement(20.0, 500.0, 15.0, BuildingUse.RESIDENTIAL)
        assert result is not None
        assert result["height_range"] == "Up to 32m"
        assert result["plot_category"] == "upto_1000sqm"
    
    def test_high_rise_requires_fire_noc(self):
        result = get_setback_requirement(35.0, 500.0, 15.0, BuildingUse.RESIDENTIAL)
        assert result["high_rise"] == True
        assert result["fire_noc_required"] == True
    
    def test_large_plot_different_divisor(self):
        result = get_setback_requirement(20.0, 1500.0, 25.0, BuildingUse.RESIDENTIAL)
        assert result["plot_category"] == "above_1000sqm"


class TestHeightRegulations:
    """Test height regulation calculations."""
    
    def test_height_calculation(self):
        # 3 * (road_width + front_setback)
        assert max_permissible_height(10.0, 3.0) == 39.0
        assert max_permissible_height(15.0, 5.0) == 60.0
    
    def test_height_unrestricted_with_9m_road_and_setback(self):
        result = max_permissible_height(9.0, 9.0)
        assert result == float('inf')


class TestFeasibilityCalculator:
    """Test main feasibility calculator."""
    
    def test_suburbs_residential_feasibility(self):
        inp = FeasibilityInput(
            plot_area_sqm=500.0,
            zone=MumbaiZone.SUBURBS,
            use=BuildingUse.RESIDENTIAL,
            road_width_m=15.0,
            floors=10,
        )
        result = calculate_feasibility(inp)
        
        assert result.zonal_basic_fsi == 1.0
        assert result.max_permissible_fsi == 2.2  # 12-18m road
        assert result.permissible_bua_sqm == 1100.0
        assert result.approx_height_m == 30.0
        assert result.parking_spaces_required > 0
    
    def test_island_city_feasibility(self):
        inp = FeasibilityInput(
            plot_area_sqm=1000.0,
            zone=MumbaiZone.ISLAND_CITY,
            use=BuildingUse.RESIDENTIAL,
            road_width_m=20.0,
            floors=5,
        )
        result = calculate_feasibility(inp)
        
        assert result.max_permissible_fsi == 3.0
        assert result.permissible_bua_sqm == 3000.0
    
    def test_fungible_included(self):
        inp = FeasibilityInput(
            plot_area_sqm=500.0,
            zone=MumbaiZone.SUBURBS,
            use=BuildingUse.RESIDENTIAL,
            road_width_m=15.0,
            floors=10,
            include_fungible=True,
        )
        result = calculate_feasibility(inp)
        
        assert result.fungible_bonus_sqm > 0
        assert result.total_max_bua_sqm > result.permissible_bua_sqm
    
    def test_crz_affected_warning(self):
        inp = FeasibilityInput(
            plot_area_sqm=500.0,
            zone=MumbaiZone.CRZ_AFFECTED,
            use=BuildingUse.RESIDENTIAL,
            road_width_m=10.0,
            floors=2,
        )
        result = calculate_feasibility(inp)
        
        assert len(result.warnings) > 0
        assert any("CRZ" in w for w in result.warnings)
    
    def test_height_exceeds_limit_warning(self):
        inp = FeasibilityInput(
            plot_area_sqm=500.0,
            zone=MumbaiZone.SUBURBS,
            use=BuildingUse.RESIDENTIAL,
            road_width_m=5.0,
            floors=15,  # Very high for narrow road
        )
        result = calculate_feasibility(inp)
        
        assert len(result.warnings) > 0
        assert any("exceeds" in w.lower() or "height" in w.lower() for w in result.warnings)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_zone_use_combination(self):
        # This should return None and add warning
        inp = FeasibilityInput(
            plot_area_sqm=500.0,
            zone=MumbaiZone.INDUSTRIAL,  # Industrial zone
            use=BuildingUse.RESIDENTIAL,
            road_width_m=15.0,
            floors=5,
        )
        result = calculate_feasibility(inp)
        # Should still produce output with defaults
        assert result.max_permissible_fsi > 0
