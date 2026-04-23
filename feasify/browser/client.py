"""Python client for Camofox Browser API."""
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class TabInfo:
    """Information about a browser tab."""
    tab_id: str
    url: str
    title: Optional[str] = None
    user_id: str = "default"
    group_id: Optional[str] = None


class CamofoxClient:
    """Client for Camofox Browser REST API."""
    
    def __init__(self, base_url: str = "http://localhost:9377", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Camox API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Camox server is running."""
        return self._request("GET", "/health")
    
    def start_browser(self) -> Dict[str, Any]:
        """Start the browser engine."""
        return self._request("POST", "/start")
    
    def stop_browser(self) -> Dict[str, Any]:
        """Stop the browser engine."""
        return self._request("POST", "/stop")
    
    def create_tab(self, url: str, user_id: str = "default", 
                   session_key: Optional[str] = None) -> TabInfo:
        """Create a new browser tab."""
        data = {"userId": user_id, "url": url}
        if session_key:
            data["sessionKey"] = session_key
        
        result = self._request("POST", "/tabs", json=data)
        return TabInfo(
            tab_id=result.get("tabId", ""),
            url=url,
            user_id=user_id,
            group_id=session_key
        )
    
    def list_tabs(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """List all open tabs for a user."""
        return self._request("GET", "/tabs", params={"userId": user_id})
    
    def get_snapshot(self, tab_id: str, user_id: str = "default",
                     include_screenshot: bool = False) -> Dict[str, Any]:
        """Get accessibility snapshot of a tab."""
        params = {"userId": user_id}
        if include_screenshot:
            params["includeScreenshot"] = "true"
        return self._request("GET", f"/tabs/{tab_id}/snapshot", params=params)
    
    def click(self, tab_id: str, user_id: str, ref: str) -> Dict[str, Any]:
        """Click an element by its ref (e1, e2, etc.)."""
        data = {"userId": user_id, "ref": ref}
        return self._request("POST", f"/tabs/{tab_id}/click", json=data)
    
    def type_text(self, tab_id: str, user_id: str, ref: str, 
                  text: str, press_enter: bool = False) -> Dict[str, Any]:
        """Type text into an element."""
        data = {"userId": user_id, "ref": ref, "text": text, "pressEnter": press_enter}
        return self._request("POST", f"/tabs/{tab_id}/type", json=data)
    
    def navigate(self, tab_id: str, user_id: str, url: str = None,
                 macro: str = None, query: str = None) -> Dict[str, Any]:
        """Navigate to URL or use a search macro."""
        data = {"userId": user_id}
        if url:
            data["url"] = url
        if macro:
            data["macro"] = macro
        if query:
            data["query"] = query
        return self._request("POST", f"/tabs/{tab_id}/navigate", json=data)
    
    def screenshot(self, tab_id: str, user_id: str) -> Dict[str, Any]:
        """Take a screenshot of the tab."""
        return self._request("GET", f"/tabs/{tab_id}/screenshot", 
                          params={"userId": user_id})
    
    def scroll(self, tab_id: str, user_id: str, direction: str = "down") -> Dict[str, Any]:
        """Scroll the page."""
        data = {"userId": user_id, "direction": direction}
        return self._request("POST", f"/tabs/{tab_id}/scroll", json=data)
    
    def close_tab(self, tab_id: str, user_id: str) -> Dict[str, Any]:
        """Close a tab."""
        return self._request("DELETE", f"/tabs/{tab_id}", 
                          params={"userId": user_id})
    
    def get_youtube_transcript(self, url: str, languages: List[str] = None) -> Dict[str, Any]:
        """Extract YouTube video transcript."""
        data = {"url": url}
        if languages:
            data["languages"] = languages
        return self._request("POST", "/youtube/transcript", json=data)
