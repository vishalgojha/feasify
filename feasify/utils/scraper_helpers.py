"""Helper functions for web scraping."""
import requests
from typing import Optional, Dict
from requests.exceptions import RequestException
import time

def get_headers() -> Dict[str, str]:
    """Get headers to mimic a real browser."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

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
            response = session.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as e:
            if attempt == max_retries - 1:
                print(f"Request failed after {max_retries} attempts: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

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
