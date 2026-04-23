"""Caching utilities for Feasify."""
import time
import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from feasify.config import settings

class FileCache:
    """Simple file-based cache with TTL."""
    
    def __init__(self, cache_dir: Path = None, ttl: int = None):
        self.cache_dir = cache_dir or settings.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl or settings.CACHE_TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        cache_file = self._get_cache_path(key)
        if not cache_file.exists():
            return None
        
        # Check TTL
        if time.time() - cache_file.stat().st_mtime > self.ttl:
            cache_file.unlink()
            return None
        
        with open(cache_file, "r") as f:
            return json.load(f)
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        cache_file = self._get_cache_path(key)
        with open(cache_file, "w") as f:
            json.dump(value, f)
    
    def delete(self, key: str):
        """Delete key from cache."""
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            cache_file.unlink()
    
    def clear(self):
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def _get_cache_path(self, key: str) -> Path:
        safe_key = "".join(c for c in key if c.isalnum() or c in "_-").strip()
        return self.cache_dir / f"{safe_key}.json"

def cached(ttl: int = None):
    """Decorator for caching function results."""
    def decorator(func: Callable):
        cache = FileCache(ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            # Check cache
            cached_val = cache.get(key)
            if cached_val is not None:
                return cached_val
            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator
