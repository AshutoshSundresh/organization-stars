from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from github import Github
import pybadges
from cachetools import TTLCache
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import httpx

app = FastAPI()

# Add CORS middleware to allow embedding badges
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache with a 1-hour TTL and max size of 1000 items
cache = TTLCache(maxsize=1000, ttl=3600)

# Thread pool for blocking GitHub API calls
executor = ThreadPoolExecutor(max_workers=2)

def _get_total_stars_sync(org_name, github_token=None):
    """Synchronous function to fetch total stars using GraphQL API for speed"""
    try:
        # Use GraphQL API for faster, single-query fetching
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        total_stars = 0
        cursor = None
        has_next_page = True
        
        # GraphQL query to get all repos with star counts
        while has_next_page:
            query = """
            query($org: String!, $cursor: String) {
              organization(login: $org) {
                repositories(first: 100, after: $cursor) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    stargazerCount
                  }
                }
              }
            }
            """
            
            variables = {"org": org_name}
            if cursor:
                variables["cursor"] = cursor
            
            # Make GraphQL request
            response = httpx.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                # Fallback to REST API if GraphQL fails
                return _get_total_stars_rest_fallback(org_name, github_token)
            
            data = response.json()
            
            if "errors" in data:
                # Fallback to REST API if GraphQL has errors
                return _get_total_stars_rest_fallback(org_name, github_token)
            
            repos = data.get("data", {}).get("organization", {}).get("repositories", {})
            nodes = repos.get("nodes", [])
            page_info = repos.get("pageInfo", {})
            
            # Sum up stars from this page
            for repo in nodes:
                total_stars += repo.get("stargazerCount", 0)
            
            # Check if there are more pages
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")
        
        return total_stars
    except Exception as e:
        # Fallback to REST API on any error
        try:
            return _get_total_stars_rest_fallback(org_name, github_token)
        except:
            raise Exception(f"Error fetching data: {str(e)}")

def _get_total_stars_rest_fallback(org_name, github_token=None):
    """Fallback to REST API if GraphQL fails"""
    g = Github(github_token) if github_token else Github()
    org = g.get_organization(org_name)
    total_stars = 0
    for repo in org.get_repos():
        total_stars += repo.stargazers_count
    return total_stars

async def get_total_stars(org_name):
    """Async wrapper for fetching total stars with caching"""
    # Check cache first
    if org_name in cache:
        return cache[org_name]

    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    
    # Run blocking call in thread pool with timeout
    try:
        loop = asyncio.get_event_loop()
        total_stars = await asyncio.wait_for(
            loop.run_in_executor(
                executor,
                partial(_get_total_stars_sync, org_name, github_token)
            ),
            timeout=10.0  # 10 second timeout (Vercel free tier limit)
        )
        
        # Cache the result
        cache[org_name] = total_stars
        return total_stars
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. The organization may have too many repositories.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/")
async def generate_svg(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = await get_total_stars(org)
        badge = pybadges.badge(left_text='stars', right_text=str(total_stars), right_color='green')
        return Response(
            content=badge,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "public, max-age=3600, s-maxage=3600",
                "Content-Type": "image/svg+xml; charset=utf-8",
            }
        )
    except HTTPException as e:
        error_badge = pybadges.badge(left_text='stars', right_text='error', right_color='red')
        return Response(
            content=error_badge,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "public, max-age=60, s-maxage=60",
                "Content-Type": "image/svg+xml; charset=utf-8",
            }
        )

@app.get("/api/stars")
async def get_stars_api(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = await get_total_stars(org)
        return {"organization": org, "total_stars": total_stars}
    except HTTPException as e:
        return {"error": str(e.detail)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)