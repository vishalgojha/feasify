"""Unit tests for data models."""
import pytest
from datetime import datetime
from feasify.models.plot import Plot, CTS
from feasify.models.estimate import CostEstimate
from feasify.core.zoning import ZoningType

def test_cts_creation():
    """Test CTS model creation."""
    cts = CTS(
        number="CTS-123/456",
        area_sqft=2400.0,
        location="Andheri West"
    )
    
    assert cts.number == "CTS-123/456"
    assert cts.area_sqft == 2400.0
    assert cts.zoning_type == ZoningType.RESIDENTIAL  # Default

def test_plot_add_cts():
    """Test adding CTS to plot."""
    plot = Plot(
        plot_id="PLOT-001",
        address="123 Main St",
        area_sqft=2400.0
    )
    
    cts1 = CTS(number="CTS-1", area_sqft=1200.0, location="Loc1")
    cts2 = CTS(number="CTS-2", area_sqft=1200.0, location="Loc2")
    
    plot.add_cts(cts1)
    plot.add_cts(cts2)
    
    assert len(plot.cts_numbers) == 2
    assert plot.area_sqft == 2400.0  # Sum of CTS areas

def test_cost_estimate_creation():
    """Test CostEstimate creation."""
    estimate = CostEstimate(
        plot_id="PLOT-001",
        area_sqft=2400.0,
        total_cost=5000000.0
    )
    
    assert estimate.estimate_id is not None
    assert len(estimate.estimate_id) == 8  # UUID first 8 chars
    assert isinstance(estimate.created_at, datetime)

def test_plot_to_dict():
    """Test Plot serialization."""
    plot = Plot(
        plot_id="PLOT-001",
        address="123 Main St",
        area_sqft=2400.0,
        zoning_type=ZoningType.COMMERCIAL
    )
    
    data = plot.to_dict()
    assert data["plot_id"] == "PLOT-001"
    assert data["zoning_type"] == "commercial"
