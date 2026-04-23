"""MCGM/DP data scraper for plot information."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from feasify.config import settings
from feasify.utils.scraper_helpers import get_headers, safe_request

class MCGMScraper:
    """Scraper for Mumbai Municipal Corporation (MCGM) data."""
    
    def __init__(self):
        self.base_url = settings.MCGM_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(get_headers())
    
    def fetch_plot_details(self, plot_id: str) -> Dict[str, Any]:
        """
        Fetch plot details from MCGM portal.
        
        Args:
            plot_id: CTS number or plot ID
        
        Returns:
            Dictionary with plot details
        """
        url = f"{self.base_url}/property/lookup/{plot_id}"
        response = safe_request(self.session, url)
        
        if not response:
            return {"error": "Failed to fetch data"}
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # Parse plot details (simplified - actual selectors depend on MCGM portal)
        details = {
            "plot_id": plot_id,
            "source": "MCGM",
            "area_sqft": self._extract_area(soup),
            "zone_type": self._extract_zone(soup),
            "owner": self._extract_owner(soup),
            "address": self._extract_address(soup)
        }
        return details
    
    def _extract_area(self, soup: BeautifulSoup) -> Optional[float]:
        area_elem = soup.select_one(".plot-area")
        if area_elem:
            try:
                return float(area_elem.text.strip().replace(",", ""))
            except ValueError:
                return None
        return None
    
    def _extract_zone(self, soup: BeautifulSoup) -> Optional[str]:
        zone_elem = soup.select_one(".zone-type")
        return zone_elem.text.strip() if zone_elem else None
    
    def _extract_owner(self, soup: BeautifulSoup) -> Optional[str]:
        owner_elem = soup.select_one(".owner-name")
        return owner_elem.text.strip() if owner_elem else None
    
    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        addr_elem = soup.select_one(".property-address")
        return addr_elem.text.strip() if addr_elem else None

class DPScraper:
    """Scraper for Development Plan (DP) data."""
    
    def __init__(self):
        self.base_url = settings.DP_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(get_headers())
    
    def fetch_zoning_info(self, location: str) -> Dict[str, Any]:
        """Fetch zoning information for a location."""
        url = f"{self.base_url}/zoning/{location}"
        response = safe_request(self.session, url)
        
        if not response:
            return {"error": "Failed to fetch zoning data"}
        
        # Simplified parsing
        return {
            "location": location,
            "source": "DP",
            "zone_type": "residential",  # Placeholder
            "fsi_allowed": 1.5,          # Placeholder
            "height_limit": 40           # Placeholder
        }

def fetch_plot_data(plot_id: str, source: str = "mcgm") -> Dict[str, Any]:
    """
    Fetch plot data from specified source.
    
    Args:
        plot_id: Plot ID or CTS number
        source: Data source ("mcgm" or "dp")
    
    Returns:
        Plot details dictionary
    """
    if source.lower() == "mcgm":
        scraper = MCGMScraper()
        return scraper.fetch_plot_details(plot_id)
    elif source.lower() == "dp":
        scraper = DPScraper()
        return scraper.fetch_zoning_info(plot_id)
    else:
        return {"error": f"Unknown source: {source}"}
