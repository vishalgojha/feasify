"""Helper functions for web scraping."""
import requests
from typing import Optional, Dict, List
from requests.exceptions import RequestException
import time
import random
import logging

logger = logging.getLogger(__name__)

# REAL_SELECTOR_NEEDED: Verify these UA strings are current
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]

def rotate_user_agent() -> str:
    """Return a random User-Agent string from the pool."""
    return random.choice(USER_AGENTS)


def get_headers() -> Dict[str, str]:
    """Get headers to mimic a real browser."""
    return {
        "User-Agent": rotate_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }


def add_jitter(min_s: float = 1.0, max_s: float = 3.0):
    """Add random delay between requests to avoid rate limiting."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)


def safe_request(
    session: requests.Session,
    url: str,
    method: str = "GET",
    max_retries: int = 3,
    timeout: int = 10,
    **kwargs
) -> Optional[requests.Response]:
    """
    Make a safe HTTP request with retries.
    
    Args:
        session: Requests session object
        url: Target URL
        method: HTTP method (GET, POST, etc.)
        max_retries: Maximum retry attempts
        timeout: Request timeout in seconds
        **kwargs: Additional arguments for requests
    
    Returns:
        Response object or None if failed
    """
    for attempt in range(max_retries):
        try:
            # Rotate User-Agent on each retry
            session.headers["User-Agent"] = rotate_user_agent()
            response = session.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            
            # Check for CAPTCHA before returning
            if handle_captcha_detection(response):
                logger.warning(f"CAPTCHA detected on attempt {attempt + 1} for {url}")
                if attempt < max_retries - 1:
                    add_jitter(5.0, 10.0)  # Longer delay on CAPTCHA
                    continue
                else:
                    raise CaptchaDetectedError(f"CAPTCHA detected on {url} after {max_retries} attempts")
            
            return response
        except RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts: {e}")
                return None
            add_jitter(2 ** attempt, 2 ** (attempt + 1))  # Exponential backoff
    return None


class CaptchaDetectedError(Exception):
    """Raised when a CAPTCHA page is detected."""
    pass


def handle_captcha_detection(response: requests.Response) -> bool:
    """
    Detect if response contains a CAPTCHA challenge.
    
    Args:
        response: HTTP response object
    
    Returns:
        True if CAPTCHA detected, False otherwise
    """
    from bs4 import BeautifulSoup
    
    # Check status code
    if response.status_code == 403:
        return True
    
    # Check for common CAPTCHA indicators in HTML
    content = response.text.lower()
    captcha_indicators = [
        "captcha",
        "recaptcha",
        "human verification",
        "security check",
        "automated requests",
        "unusual traffic",
        "please verify",
        "bot detection"
    ]
    
    for indicator in captcha_indicators:
        if indicator in content:
            return True
    
    # Check for CAPTCHA form elements
    try:
        soup = BeautifulSoup(response.content, 'lxml')
        captcha_selectors = [
            "input[name='captcha']",
            "div.g-recaptcha",
            "div.captcha",
            "#captcha",
            "img[src*='captcha']",
            "iframe[src*='recaptcha']"
        ]
        
        for selector in captcha_selectors:
            if soup.select_one(selector):
                return True
    except Exception as e:
        logger.debug(f"CAPTCHA check parse error: {e}")
    
    return False


def parse_mcgm_table(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Parse MCGM-specific table with Hindi/English mixed headers.
    MCGM tables typically use class="table table-bordered" with mixed language headers.
    
    Args:
        soup: BeautifulSoup object of page
    
    Returns:
        List of dictionaries with cleaned headers as keys
    """
    tables = soup.find_all("table", class_="table-bordered") or soup.find_all("table", class_="table")
    
    if not tables:
        # Fallback to any table
        tables = soup.find_all("table")
    
    results = []
    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue
        
        # Extract headers - handle colspan and mixed content
        header_row = rows[0]
        headers = []
        for th in header_row.find_all(["th", "td"]):
            # Get text, handling nested tags
            header_text = th.get_text(strip=True)
            # Clean: remove Hindi characters if needed, normalize
            header_text = header_text.replace('\n', ' ').strip()
            headers.append(header_text)
        
        # Extract data rows
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) == len(headers):
                row_data = {}
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    # REAL_SELECTOR_NEEDED: Verify MCGM table cell structure
                    row_data[headers[i]] = cell_text
                results.append(row_data)
    
    return results


def parse_table(table_element) -> list:
    """Parse HTML table into list of dictionaries."""
    rows = table_element.find_all("tr")
    if not rows:
        return []
    
    # Extract headers
    headers = [th.text.strip() for th in rows[0].find_all(["th", "td"])]
    
    # Extract data rows
    data = []
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if len(cells) == len(headers):
            row_data = {headers[i]: cell.text.strip() for i, cell in enumerate(cells)}
            data.append(row_data)
    
    return data
