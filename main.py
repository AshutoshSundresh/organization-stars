from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import aiohttp
import asyncio
from cachetools import TTLCache
import pybadges

app = FastAPI()

# Initialize cache with a 1-hour TTL and max size of 1000 items
cache = TTLCache(maxsize=1000, ttl=3600)

async def fetch_repo_stars(session, repo_name):
    url = f"https://api.github.com/repos/{repo_name}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("stargazers_count", 0)
        return 0

async def get_total_stars(org_name):
    if org_name in cache:
        return cache[org_name]

    async with aiohttp.ClientSession() as session:
        # First, fetch the list of repositories
        url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100"
        repos = []
        while url:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=404, detail=f"Organization not found or API rate limit exceeded")
                repos.extend(await response.json())
                url = response.links.get('next', {}).get('url')

        # Then, fetch star counts for each repository
        tasks = [fetch_repo_stars(session, repo['full_name']) for repo in repos]
        results = await asyncio.gather(*tasks)

    total_stars = sum(results)
    cache[org_name] = total_stars
    return total_stars

@app.get("/")
async def generate_svg(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = await get_total_stars(org)
        badge = pybadges.badge(left_text='stars', right_text=str(total_stars), right_color='green')
        return Response(content=badge, media_type="image/svg+xml")
    except HTTPException as e:
        # Return an error badge if there's an issue
        error_badge = pybadges.badge(left_text='stars', right_text='error', right_color='red')
        return Response(content=error_badge, media_type="image/svg+xml")

@app.get("/api/stars")
async def get_stars_api(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = await get_total_stars(org)
        return {"organization": org, "total_stars": total_stars}
    except HTTPException as e:
        return {"error": str(e.detail)}