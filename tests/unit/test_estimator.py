"""Unit tests for cost estimator."""
import pytest
from feasify.core.estimator import estimate_cost, generate_estimate_record
from feasify.models.estimate import CostEstimate

def test_estimate_cost_basic():
    """Test basic cost estimation."""
    result = estimate_cost(1000.0, "residential", 1)
    
    assert "total_cost" in result
    assert result["plot_area_sqft"] == 1000.0
    assert result["built_up_area_sqft"] == 1000.0
    assert result["zone_type"] == "residential"
    assert result["total_cost"] > 0

def test_estimate_cost_multi_floor():
    """Test cost estimation with multiple floors."""
    result = estimate_cost(1000.0, "residential", 2)
    
    assert result["num_floors"] == 2
    assert result["built_up_area_sqft"] == 2000.0
    assert result["total_cost"] > 1000000  # Should be substantial

def test_estimate_cost_commercial():
    """Test commercial zone estimation."""
    result = estimate_cost(1000.0, "commercial", 1)
    
    assert result["zone_type"] == "commercial"
    # Commercial should be more expensive than residential
    residential = estimate_cost(1000.0, "residential", 1)
    assert result["total_cost"] > residential["total_cost"]

def test_generate_estimate_record():
    """Test generating CostEstimate dataclass."""
    estimate = generate_estimate_record(1200.0, "residential", 2, "PLOT-123")
    
    assert isinstance(estimate, CostEstimate)
    assert estimate.plot_id == "PLOT-123"
    assert estimate.area_sqft == 1200.0
    assert estimate.num_floors == 2
    assert estimate.estimate_id is not None
