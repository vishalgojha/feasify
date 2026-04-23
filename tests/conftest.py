"""Pytest configuration and fixtures for Feasify."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from feasify.db.session import engine
from feasify.db.models import Base
from feasify.db.models import PlotModel, CTSModel, EstimateModel

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_plot():
    """Sample plot data for testing."""
    from feasify.models.plot import Plot, CTS
    from feasify.core.zoning import ZoningType
    
    cts = CTS(
        number="1234/567",
        area_sqft=2400.0,
        location="Andheri West, Mumbai",
        zoning_type=ZoningType.RESIDENTIAL
    )
    
    return Plot(
        plot_id="PLOT-001",
        address="123, ABC Road, Andheri West, Mumbai",
        area_sqft=2400.0,
        zoning_type=ZoningType.RESIDENTIAL,
        cts_numbers=[cts],
        owner="John Doe"
    )

@pytest.fixture
def sample_estimate():
    """Sample cost estimate for testing."""
    from feasify.models.estimate import CostEstimate
    
    return CostEstimate(
        plot_id="PLOT-001",
        area_sqft=2400.0,
        zone_type="residential",
        num_floors=1,
        total_cost=4500000.0
    )
