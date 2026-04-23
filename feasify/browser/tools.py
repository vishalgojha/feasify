"""Browser automation tools for Feasify using Camofox."""
from typing import Optional, Dict, Any, List
from .client import CamofoxClient, TabInfo


def _get_client() -> CamofoxClient:
    """Get or create a CamofoxClient instance."""
    from feasify.config import settings
    return CamofoxClient(
        base_url=f"http://localhost:{settings.API_PORT}",
        api_key=None  # Add from settings if needed
    )


def browser_create_tab(url: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Create a new browser tab with anti-detection.
    
    Args:
        url: Initial URL to navigate to
        user_id: User session ID for isolation
    
    Returns:
        Dictionary with tab info
    """
    client = _get_client()
    tab = client.create_tab(url, user_id)
    return {
        "tab_id": tab.tab_id,
        "url": tab.url,
        "user_id": tab.user_id
    }


def browser_snapshot(tab_id: str, user_id: str = "default", 
                     include_screenshot: bool = False) -> Dict[str, Any]:
    """
    Get accessibility snapshot of a tab with element refs.
    
    Args:
        tab_id: Tab ID from create_tab
        user_id: User session ID
        include_screenshot: Include base64 PNG screenshot
    
    Returns:
        Dictionary with snapshot text and optional screenshot
    """
    client = _get_client()
    return client.get_snapshot(tab_id, user_id, include_screenshot)


def browser_click(tab_id: str, user_id: str, ref: str) -> Dict[str, Any]:
    """
    Click an element by its ref (e.g., e1, e2).
    
    Args:
        tab_id: Tab ID
        user_id: User session ID
        ref: Element ref from snapshot
    
    Returns:
        Result dictionary
    """
    client = _get_client()
    return client.click(tab_id, user_id, ref)


def browser_type(tab_id: str, user_id: str, ref: str, 
                 text: str, press_enter: bool = False) -> Dict[str, Any]:
    """
    Type text into an element.
    
    Args:
        tab_id: Tab ID
        user_id: User session ID
        ref: Element ref to type into
        text: Text to type
        press_enter: Press Enter after typing
    
    Returns:
        Result dictionary
    """
    client = _get_client()
    return client.type_text(tab_id, user_id, ref, text, press_enter)


def browser_screenshot(tab_id: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Take a screenshot of the current tab.
    
    Args:
        tab_id: Tab ID
        user_id: User session ID
    
    Returns:
        Dictionary with screenshot data (base64 PNG)
    """
    client = _get_client()
    return client.screenshot(tab_id, user_id)


def browser_navigate(tab_id: str, user_id: str, url: Optional[str] = None,
                     macro: Optional[str] = None, query: Optional[str] = None) -> Dict[str, Any]:
    """
    Navigate to URL or use a search macro.
    
    Args:
        tab_id: Tab ID
        user_id: User session ID
        url: URL to navigate to
        macro: Search macro (e.g., "@google_search")
        query: Search query for macro
    
    Returns:
        Result dictionary
    """
    client = _get_client()
    return client.navigate(tab_id, user_id, url, macro, query)


def browser_close_tab(tab_id: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Close a browser tab.
    
    Args:
        tab_id: Tab ID to close
        user_id: User session ID
    
    Returns:
        Result dictionary
    """
    client = _get_client()
    return client.close_tab(tab_id, user_id)


def browser_scroll(tab_id: str, user_id: str, direction: str = "down") -> Dict[str, Any]:
    """
    Scroll the page.
    
    Args:
        tab_id: Tab ID
        user_id: User session ID
        direction: Scroll direction (up/down/left/right)
    
    Returns:
        Result dictionary
    """
    client = _get_client()
    return client.scroll(tab_id, user_id, direction)


def google_search(query: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Search Google using Camox macro.
    
    Args:
        query: Search query
        user_id: User session ID
    
    Returns:
        Snapshot of search results
    """
    client = _get_client()
    tab = client.create_tab("about:blank", user_id)
    result = client.navigate(tab.tab_id, user_id, macro="@google_search", query=query)
    snapshot = client.get_snapshot(tab.tab_id, user_id)
    client.close_tab(tab.tab_id, user_id)
    return {"search_query": query, "snapshot": snapshot, "nav_result": result}


def youtube_search(query: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Search YouTube using Camox macro.
    
    Args:
        query: Search query
        user_id: User session ID
    
    Returns:
        Snapshot of YouTube search results
    """
    client = _get_client()
    tab = client.create_tab("about:blank", user_id)
    result = client.navigate(tab.tab_id, user_id, macro="@youtube_search", query=query)
    snapshot = client.get_snapshot(tab.tab_id, user_id)
    client.close_tab(tab.tab_id, user_id)
    return {"search_query": query, "snapshot": snapshot, "nav_result": result}


def extract_youtube_transcript(url: str, languages: List[str] = None) -> Dict[str, Any]:
    """
    Extract transcript from a YouTube video.
    
    Args:
        url: YouTube video URL
        languages: Preferred languages (e.g., ["en", "es"])
    
    Returns:
        Dictionary with transcript text and metadata
    """
    client = _get_client()
    return client.get_youtube_transcript(url, languages)


def amazon_search(query: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Search Amazon using Camox macro.
    
    Args:
        query: Search query
        user_id: User session ID
    
    Returns:
        Snapshot of Amazon search results
    """
    client = _get_client()
    tab = client.create_tab("about:blank", user_id)
    result = client.navigate(tab.tab_id, user_id, macro="@amazon_search", query=query)
    snapshot = client.get_snapshot(tab.tab_id, user_id)
    client.close_tab(tab.tab_id, user_id)
    return {"search_query": query, "snapshot": snapshot, "nav_result": result}


def reddit_search(query: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Search Reddit using Camox macro.
    
    Args:
        query: Search query
        user_id: User session ID
    
    Returns:
        JSON results from Reddit
    """
    client = _get_client()
    tab = client.create_tab("about:blank", user_id)
    result = client.navigate(tab.tab_id, user_id, macro="@reddit_search", query=query)
    snapshot = client.get_snapshot(tab.tab_id, user_id)
    client.close_tab(tab.tab_id, user_id)
    return {"search_query": query, "snapshot": snapshot, "nav_result": result}
