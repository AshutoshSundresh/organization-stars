"""Unit tests for cache service."""
import pytest
from cache_service import StarCountCache


class TestStarCountCache:
    """Test cases for StarCountCache."""
    
    def test_cache_set_and_get(self):
        """Test setting and getting values from cache."""
        cache = StarCountCache()
        cache.set("test_org", 1234)
        assert cache.get("test_org") == 1234
    
    def test_cache_get_nonexistent(self):
        """Test getting a value that doesn't exist."""
        cache = StarCountCache()
        assert cache.get("nonexistent") is None
    
    def test_cache_has(self):
        """Test checking if a key exists in cache."""
        cache = StarCountCache()
        cache.set("test_org", 5678)
        assert cache.has("test_org") is True
        assert cache.has("nonexistent") is False
    
    def test_cache_overwrite(self):
        """Test overwriting an existing cache value."""
        cache = StarCountCache()
        cache.set("test_org", 1000)
        cache.set("test_org", 2000)
        assert cache.get("test_org") == 2000
    
    def test_cache_multiple_orgs(self):
        """Test caching multiple organizations."""
        cache = StarCountCache()
        cache.set("org1", 100)
        cache.set("org2", 200)
        cache.set("org3", 300)
        assert cache.get("org1") == 100
        assert cache.get("org2") == 200
        assert cache.get("org3") == 300

