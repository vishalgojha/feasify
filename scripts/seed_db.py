"""Script to seed database with sample data."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feasify.db.session import engine, init_db
from feasify.db.models import PlotModel, CTSModel, EstimateModel
from sqlalchemy.orm import Session

def seed_database():
    """Seed database with sample data."""
    # Initialize database
    init_db()
    
    with Session(engine) as db:
        # Add sample plot
        plot = PlotModel(
            plot_id="PLOT-001",
            address="123, ABC Road, Andheri West, Mumbai",
            area_sqft=2400.0,
            zoning_type="residential",
            owner="John Doe",
            market_value=5000000.0,
            latitude=19.1197,
            longitude=72.8465
        )
        db.add(plot)
        
        # Add sample CTS
        cts = CTSModel(
            cts_number="CTS-123/456",
            plot_id="PLOT-001",
            area_sqft=2400.0,
            location="Andheri West, Mumbai",
            owner="John Doe",
            zoning_type="residential",
            fsi_allowed=1.5,
            latitude=19.1197,
            longitude=72.8465
        )
        db.add(cts)
        
        # Add sample estimate
        estimate = EstimateModel(
            estimate_id="EST-001",
            plot_id="PLOT-001",
            area_sqft=2400.0,
            zone_type="residential",
            num_floors=1,
            total_cost=4500000.0
        )
        db.add(estimate)
        
        db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
