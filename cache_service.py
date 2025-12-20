"""Cache service for storing organization star counts."""
from cachetools import TTLCache
from typing import Optional

from config import CACHE_MAX_SIZE, CACHE_TTL_SECONDS


class StarCountCache:
    """Cache manager for organization star counts."""
    
    def __init__(self):
        self.cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL_SECONDS)
    
    def get(self, org_name: str) -> Optional[int]:
        """Get cached star count for an organization."""
        return self.cache.get(org_name)
    
    def set(self, org_name: str, star_count: int) -> None:
        """Cache star count for an organization."""
        self.cache[org_name] = star_count
    
    def has(self, org_name: str) -> bool:
        """Check if an organization's star count is cached."""
        return org_name in self.cache


# Global cache instance
cache = StarCountCache()

