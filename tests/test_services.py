"""Unit tests for services layer."""
import pytest
import asyncio
from unittest.mock import patch, Mock
from fastapi import HTTPException

from services import fetch_total_stars
from cache_service import StarCountCache


class TestFetchTotalStars:
    """Test cases for fetch_total_stars service."""
    
    @pytest.mark.asyncio
    async def test_fetch_total_stars_from_cache(self):
        """Test that cached values are returned immediately."""
        # Create a fresh cache for testing
        test_cache = StarCountCache()
        test_cache.set("cached_org", 1234)
        
        with patch('services.cache', test_cache):
            with patch('services.get_total_stars') as mock_api:
                result = await fetch_total_stars("cached_org")
                assert result == 1234
                # API should not be called if cached
                mock_api.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_fetch_total_stars_from_api(self):
        """Test fetching from API when not cached."""
        test_cache = StarCountCache()
        
        with patch('services.cache', test_cache):
            with patch('services.get_total_stars', return_value=5678):
                result = await fetch_total_stars("new_org")
                assert result == 5678
                # Verify it was cached
                assert test_cache.get("new_org") == 5678
    
    @pytest.mark.asyncio
    async def test_fetch_total_stars_timeout(self):
        """Test timeout handling."""
        test_cache = StarCountCache()
        
        def slow_function(*args, **kwargs):
            import time
            time.sleep(2)  # Simulate slow blocking API call
            return 1000
        
        with patch('services.cache', test_cache):
            with patch('services.get_total_stars', side_effect=slow_function):
                with patch('config.GITHUB_API_TIMEOUT', 0.5):  # Short timeout for testing
                    with patch('services.GITHUB_API_TIMEOUT', 0.5):
                        with pytest.raises(HTTPException) as exc_info:
                            await fetch_total_stars("slow_org")
                        assert exc_info.value.status_code == 504
    
    @pytest.mark.asyncio
    async def test_fetch_total_stars_api_error(self):
        """Test handling of API errors."""
        test_cache = StarCountCache()
        
        with patch('services.cache', test_cache):
            with patch('services.get_total_stars', side_effect=Exception("API Error")):
                with pytest.raises(HTTPException) as exc_info:
                    await fetch_total_stars("error_org")
                assert exc_info.value.status_code == 404
                assert "API Error" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_fetch_total_stars_with_token(self):
        """Test that GitHub token is passed to API."""
        test_cache = StarCountCache()
        
        with patch('services.cache', test_cache):
            with patch('services.get_total_stars') as mock_api:
                with patch('services.GITHUB_TOKEN', 'test_token'):
                    await fetch_total_stars("test_org")
                    mock_api.assert_called_once_with("test_org", 'test_token')

