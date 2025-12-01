from typing import Any, Optional
import time
from functools import lru_cache
from fastapi import Depends


class SimpleCache:
    """Simple in-memory cache with TTL """
    
    def __init__(self, ttl: int = 300):
        self._cache = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """Clear cache"""
        self._cache.clear()


# LRU Cache for predictions
@lru_cache(maxsize=128)
def get_cached_prediction(prediction_id: str) -> Optional[Any]:
    """LRU cache for predictions - functional approach"""
    return None


def set_cached_prediction(prediction_id: str, value: Any):
    """Set value in LRU cache - functional wrapper"""
    # This function doesn't directly set in lru_cache since it's read-only
    # In a real implementation, you'd use a different caching approach
    pass


def clear_prediction_cache():
    """Clear the prediction cache"""
    get_cached_prediction.cache_clear()


# Dependency injection for cache
def get_simple_cache() -> SimpleCache:
    """Dependency injection for simple cache"""
    return SimpleCache()


# Global cache instance (for backward compatibility)
prediction_cache = SimpleCache()