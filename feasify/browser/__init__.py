"""Camofox browser integration for Feasify - anti-detection browser tools."""
from .client import CamofoxClient
from .tools import (
    browser_create_tab,
    browser_snapshot,
    browser_click,
    browser_type,
    browser_screenshot,
    browser_navigate,
    browser_close_tab,
    google_search,
    youtube_search,
    extract_youtube_transcript
)

__all__ = [
    "CamofoxClient",
    "browser_create_tab",
    "browser_snapshot", 
    "browser_click",
    "browser_type",
    "browser_screenshot",
    "browser_navigate",
    "browser_close_tab",
    "google_search",
    "youtube_search",
    "extract_youtube_transcript"
]
