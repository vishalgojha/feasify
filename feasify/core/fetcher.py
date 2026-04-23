"""MCGM/DP/iGR data scrapers for plot information."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from feasify.config import settings
from feasify.utils.scraper_helpers import (
    get_headers, safe_request, parse_mcgm_table,
    handle_captcha_detection, add_jitter, CaptchaDetectedError,
    rotate_user_agent
)
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# REAL_SELECTOR_NEEDED: These selectors need verification against live MCGM portal
MCGM_SELECTORS = {
    "plot_area": ["#plotArea", ".plot-area", "td:nth-child(3)", "span.area"],
    "zone_type": ["#zoneType", ".zone-type", "td:nth-child(5)", "span.zone"],
    "owner_name": ["#ownerName", ".owner-name", "td:nth-child(2)", "span.owner"],
    "ward": ["#wardNo", ".ward", "td:nth-child(1)"],
    "address": ["#address", ".property-address", "td:nth-child(4)"],
    "assessment_no": ["#assessmentNo", ".assessment", "td:nth-child(6)"],
    "property_tax": ["#taxDue", ".tax-amount"],
}

# REAL_SELECTOR_NEEDED: DP portal selectors need verification
DP_ZONE_SELECTORS = {
    "zone_type": ["#zoneType", ".zone-designation", "span.zone-type"],
    "fsi_allowed": ["#fsiValue", ".fsi-allowed"],
    "height_limit": ["#heightLimit", ".height-restriction"],
    "overlays": ["div.overlay-zones", "span.special-zone"],
}


# TODO: Verify selectors against live portal before setting USE_MOCK_DATA=False
# Set USE_MOCK_DATA=False only after verifying live portal selectors
# Live portals: https://ptaxportal.mcgm.gov.in

class MCGMScraper:
    """Scraper for Mumbai Municipal Corporation (MCGM) Property Tax Portal."""
    
    def __init__(self):
        self.base_url = "https://ptaxportal.mcgm.gov.in"
        self.session = requests.Session()
        self.session.headers.update(get_headers())
        self.cache_dir = Path(settings.CACHE_DIR) / "mcgm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_plot_details(self, plot_id: str) -> Dict[str, Any]:
        """Fetch plot details from MCGM Property Tax Portal."""
        # Use mock data if configured
        if settings.USE_MOCK_DATA:
            mock = MockMCGMScraper()
            return mock.fetch_plot_details(plot_id)
        
        result = {
            "plot_id": plot_id,
            "source": "MCGM",
            "cts_number": plot_id,
            "area_sqft": None,
            "area_sqm": None,
            "zone_type": None,
            "owner": None,
            "address": None,
            "ward": None,
            "assessment_no": None,
            "property_tax_due": None,
        }
        
        try:
            # Step 1: Load the search page to get session cookies
            search_url = f"{self.base_url}/PropertySearch"
            response = safe_request(self.session, search_url, method="GET")
            
            if not response:
                logger.error(f"Failed to load MCGM search page for {plot_id}")
                return result
            
            # Check for CAPTCHA
            if handle_captcha_detection(response):
                raise CaptchaDetectedError(f"CAPTCHA detected on MCGM search page")
            
            add_jitter(1.0, 2.0)  # Be polite
            
            # Step 2: POST search with CTS number
            # REAL_SELECTOR_NEEDED: Verify form field names against live portal
            search_payload = {
                "ctsNo": plot_id,  # REAL_SELECTOR_NEEDED: Verify field name
                "searchType": "CTS",
                "viewType": "propertyTax",
            }
            
            search_response = safe_request(
                self.session,
                f"{self.base_url}/PropertySearch/Search",
                method="POST",
                data=search_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if not search_response:
                logger.error(f"Search POST failed for CTS {plot_id}")
                return result
            
            if handle_captcha_detection(search_response):
                raise CaptchaDetectedError(f"CAPTCHA on search POST for {plot_id}")
            
            # Parse response
            soup = BeautifulSoup(search_response.content, 'lxml')
            
            # REAL_SELECTOR_NEEDED: Verify actual response structure
            # Try to extract from table or result div
            result_table = soup.select_one("table.table-bordered")
            if result_table:
                table_data = parse_mcgm_table(soup)
                # Map table data to result fields
                for row in table_data:
                    # REAL_SELECTOR_NEEDED: Verify header names
                    if "area" in str(row).lower():
                        result["area_sqft"] = self._extract_area(str(row))
                    if "owner" in str(row).lower():
                        result["owner"] = self._extract_text(row, "owner")
            
            # Try individual field selectors
            for field, selectors in MCGM_SELECTORS.items():
                value = self._extract_with_selectors(soup, selectors)
                if value:
                    if field == "plot_area":
                        result["area_sqft"] = self._extract_area(value)
                    elif field == "zone_type":
                        result["zone_type"] = self._normalize_zone_type(value)
                    elif field == "owner_name":
                        result["owner"] = value
                    elif field == "ward":
                        result["ward"] = value
                    elif field == "address":
                        result["address"] = value
                    elif field == "assessment_no":
                        result["assessment_no"] = value
            
            # If still no area, try regex patterns
            if not result["area_sqft"]:
                result["area_sqft"] = self._extract_area_from_text(soup.get_text())
            
            # Cache successful result
            if any(v for k, v in result.items() if k not in ["plot_id", "source", "cts_number"]):
                self._save_cache(plot_id, result)
            
        except CaptchaDetectedError as e:
            logger.error(f"CAPTCHA detected: {e}")
            result["error"] = "CAPTCHA detected - manual intervention required"
        except Exception as e:
            logger.error(f"Error fetching MCGM data for {plot_id}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first match."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None
    
    def _extract_area(self, text: str) -> Optional[float]:
        """Extract area in sq.ft. from text."""
        import re
        # Look for patterns like "1200 sq.ft.", "1200 sqft", "111.5 sq.m"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*ft',  # 1200 sq.ft
            r'(\d+(?:\.\d+)?)\s*sq\s*m',         # 111.5 sq.m
            r'(\d+(?:\.\d+)?)\s*square feet',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                area = float(match.group(1))
                if 'sq.m' in pattern or 'square meter' in pattern:
                    return area * 10.764  # Convert sq.m to sq.ft
                return area
        return None
    
    def _extract_area_from_text(self, text: str) -> Optional[float]:
        """Fallback: extract area from unstructured text."""
        import re
        # Look for numbers near "area", "sqft", etc.
        area_keywords = ['area', 'sq.ft', 'sqft', 'sq.m', 'sqm']
        lines = text.split('\n')
        for line in lines:
            if any(kw in line.lower() for kw in area_keywords):
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                if numbers:
                    return float(numbers[0])
        return None
    
    def _extract_text(self, data: Dict, key: str) -> Optional[str]:
        """Extract text from parsed table row."""
        for k, v in data.items():
            if key.lower() in k.lower():
                return v
        return None
    
    def _normalize_zone_type(self, zone_str: str) -> str:
        """Normalize zone type string to match ZoningType enum."""
        zone_lower = zone_str.lower()
        if 'res' in zone_lower or 'r1' in zone_lower or 'r2' in zone_lower:
            return 'residential'
        elif 'com' in zone_lower or 'c1' in zone_lower or 'c2' in zone_lower:
            return 'commercial'
        elif 'ind' in zone_lower:
            return 'industrial'
        elif 'pub' in zone_lower:
            return 'public'
        elif 'green' in zone_lower:
            return 'green'
        return zone_str


class DPScraper:
    """Scraper for Development Plan (DP) GIS Portal."""
    
    def __init__(self):
        self.base_url = "https://udri.mcgm.gov.in"
        self.session = requests.Session()
        self.session.headers.update(get_headers())
        self.cache_dir = Path(settings.CACHE_DIR) / "dp"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_zoning_info(self, location: str) -> Dict[str, Any]:
        """
        Fetch zoning information from DP GIS Portal.
        
        Args:
            location: Ward number, area name, or coordinates
        
        Returns:
            Dictionary with zoning details
        """
        result = {
            "location": location,
            "source": "DP",
            "zone_type": None,
            "fsi_allowed": None,
            "height_limit": None,
            "overlays": [],
            "ward": None,
        }
        
        try:
            # REAL_SELECTOR_NEEDED: Verify DP portal URL structure
            # Try ward-based lookup first
            search_url = f"{self.base_url}/GIS/ZoneInfo"
            payload = {
                "wardNo": location,  # REAL_SELECTOR_NEEDED: Verify field name
                "queryType": "ward",
            }
            
            response = safe_request(
                self.session,
                search_url,
                method="POST",
                json=payload,
                timeout=15
            )
            
            if not response:
                logger.warning(f"DP portal request failed for {location}")
                return result
            
            # Try to parse JSON response (if API endpoint)
            try:
                data = response.json()
                result["zone_type"] = data.get("zoneType", data.get("zone_type"))
                result["fsi_allowed"] = data.get("fsi", data.get("fsi_allowed"))
                result["height_limit"] = data.get("heightLimit", data.get("height_limit"))
                result["overlays"] = data.get("overlays", [])
                result["ward"] = data.get("ward")
            except:
                # Parse HTML response
                soup = BeautifulSoup(response.content, 'lxml')
                
                # REAL_SELECTOR_NEEDED: Verify selectors against live portal
                for field, selectors in DP_ZONE_SELECTORS.items():
                    value = self._extract_with_selectors(soup, selectors)
                    if value:
                        if field == "zone_type":
                            result["zone_type"] = self._normalize_zone_type(value)
                        elif field == "fsi_allowed":
                            result["fsi_allowed"] = self._extract_float(value)
                        elif field == "height_limit":
                            result["height_limit"] = self._extract_float(value)
                        elif field == "overlays":
                            result["overlays"] = [v.strip() for v in value.split(',')]
            
        except Exception as e:
            logger.error(f"Error fetching DP zoning for {location}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first match."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None
    
    def _extract_float(self, text: str) -> Optional[float]:
        """Extract float value from text."""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1))
        return None
    
    def _normalize_zone_type(self, zone_str: str) -> str:
        """Normalize zone designation to standard type."""
        zone_lower = zone_str.lower().replace(' ', '')
        # Map DP zone codes to standard types
        zone_mapping = {
            'r1': 'residential', 'r2': 'residential', 'r3': 'residential',
            'c1': 'commercial', 'c2': 'commercial', 'c3': 'commercial',
            'i1': 'industrial', 'i2': 'industrial',
            'p0': 'public', 'g0': 'green',
            'crz': 'green',  # Coastal Regulation Zone
        }
        for code, zone_type in zone_mapping.items():
            if code in zone_lower:
                return zone_type
        return zone_str


class iGRScraper:
    """Scraper for iGR Maharashtra (Registered Document Search)."""
    
    def __init__(self):
        self.base_url = "https://igrmaharashtra.gov.in"
        self.session = requests.Session()
        self.session.headers.update(get_headers())
        self.cache_dir = Path(settings.CACHE_DIR) / "igr"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_document_details(self, survey_no: str) -> Dict[str, Any]:
        """
        Fetch last registered document details by survey/CTS number.
        
        Args:
            survey_no: Survey number or CTS number
        
        Returns:
            Dictionary with registration details
        """
        result = {
            "survey_no": survey_no,
            "source": "iGR",
            "last_transaction_price": None,
            "registration_date": None,
            "area_sqft": None,
            "buyer": None,
            "seller": None,
            "document_type": None,
        }
        
        try:
            # REAL_SELECTOR_NEEDED: Verify iGR portal structure
            # Step 1: Navigate to search page
            search_url = f"{self.base_url}/eASR/Search"
            response = safe_request(self.session, search_url)
            
            if not response:
                return result
            
            add_jitter(1.0, 2.0)
            
            # Step 2: Search by survey number
            # REAL_SELECTOR_NEEDED: Verify form field names
            search_payload = {
                "surveyNo": survey_no,
                "searchType": "Survey",
                "year": "",  # Current year
            }
            
            post_response = safe_request(
                self.session,
                f"{self.base_url}/eASR/SearchResult",
                method="POST",
                data=search_payload
            )
            
            if not post_response:
                return result
            
            soup = BeautifulSoup(post_response.content, 'lxml')
            
            # REAL_SELECTOR_NEEDED: Verify table structure
            tables = soup.select("table.table-bordered")
            if tables:
                table_data = parse_mcgm_table(soup)
                for row in table_data:
                    # Extract relevant fields
                    text = str(row)
                    # Price extraction
                    if any(word in text.lower() for word in ['price', 'consideration', 'amount']):
                        result["last_transaction_price"] = self._extract_price(text)
                    # Date extraction
                    if any(word in text.lower() for word in ['date', 'registered']):
                        result["registration_date"] = self._extract_date(text)
            
        except Exception as e:
            logger.error(f"Error fetching iGR data for {survey_no}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price (in ₹) from text."""
        import re
        # Look for patterns like ₹12,00,000 or 1200000
        patterns = [
            r'₹\s*([\d,]+(?:\.\d{2})?)',  # ₹12,00,000
            r'(\d+(?:,\d+)*)\s*(?:rupees?|inr)',  # 1200000 rupees
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    pass
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        import re
        # Look for DD/MM/YYYY or YYYY-MM-DD patterns
        patterns = [
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None


def fetch_plot_data(plot_id: str, source: str = "mcgm") -> Dict[str, Any]:
    """
    Fetch plot data from specified source.
    
    Args:
        plot_id: Plot ID, CTS number, or location
        source: Data source ("mcgm", "dp", or "igr")
    
    Returns:
        Plot details dictionary
    """
    if source.lower() == "mcgm":
        scraper = MCGMScraper()
        return scraper.fetch_plot_details(plot_id)
    elif source.lower() == "dp":
        scraper = DPScraper()
        return scraper.fetch_zoning_info(plot_id)
    elif source.lower() == "igr":
        scraper = iGRScraper()
        return scraper.fetch_document_details(plot_id)
    else:
        logger.error(f"Unknown source: {source}")
        return {"error": f"Unknown source: {source}. Use 'mcgm', 'dp', or 'igr'."}
