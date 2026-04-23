"""Script to test MCGM/DP scraper functionality."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feasify.core.fetcher import MCGMScraper, DPScraper

def test_mcgm_scraper():
    """Test MCGM scraper with sample plot ID."""
    print("Testing MCGM scraper...")
    scraper = MCGMScraper()
    
    # Test with a sample plot ID (replace with real one for actual testing)
    test_plot_id = "1234/567"
    print(f"Fetching data for plot: {test_plot_id}")
    
    details = scraper.fetch_plot_details(test_plot_id)
    print("Result:", details)

def test_dp_scraper():
    """Test DP scraper with sample location."""
    print("\nTesting DP scraper...")
    scraper = DPScraper()
    
    test_location = "andheri_west"
    print(f"Fetching zoning for: {test_location}")
    
    zoning = scraper.fetch_zoning_info(test_location)
    print("Result:", zoning)

if __name__ == "__main__":
    print("=== Feasify Scraper Test ===")
    test_mcgm_scraper()
    test_dp_scraper()
