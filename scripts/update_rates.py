"""Script to update PWD rates from official source."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feasify.utils.rates import update_rates, PWD_RATES
from datetime import datetime

def update_pwd_rates():
    """Update PWD rates (placeholder for actual implementation)."""
    print("Fetching latest PWD rates from official source...")
    
    # In production, scrape from https://pwd.maharashtra.gov.in/rates
    # For now, use default rates
    new_rates = PWD_RATES.copy()
    
    # Add timestamp
    print(f"Updating rates: {new_rates}")
    update_rates(new_rates)
    print("Rates updated successfully!")

if __name__ == "__main__":
    update_pwd_rates()
