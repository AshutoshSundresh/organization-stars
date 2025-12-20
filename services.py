"""Service layer for fetching and caching organization star counts."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from fastapi import HTTPException

from config import GITHUB_TOKEN, GITHUB_API_TIMEOUT, THREAD_POOL_MAX_WORKERS
from github_api import get_total_stars
from cache_service import cache


# Thread pool for blocking GitHub API calls
executor = ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS)


async def fetch_total_stars(org_name: str) -> int:
    """
    Fetch total stars for an organization with caching and async execution.
    
    Args:
        org_name: GitHub organization name
        
    Returns:
        Total number of stars across all repositories
        
    Raises:
        HTTPException: If the request times out or fails
    """
    # Check cache first
    cached_stars = cache.get(org_name)
    if cached_stars is not None:
        return cached_stars
    
    # Run blocking call in thread pool with timeout
    try:
        loop = asyncio.get_event_loop()
        total_stars = await asyncio.wait_for(
            loop.run_in_executor(
                executor,
                partial(get_total_stars, org_name, GITHUB_TOKEN)
            ),
            timeout=GITHUB_API_TIMEOUT
        )
        
        # Cache the result
        cache.set(org_name, total_stars)
        return total_stars
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request timed out. The organization may have too many repositories."
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

