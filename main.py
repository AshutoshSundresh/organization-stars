from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import aiohttp
import asyncio
from cachetools import TTLCache
import pybadges

app = FastAPI()

# Initialize cache with a 1-hour TTL and max size of 1000 items
cache = TTLCache(maxsize=1000, ttl=3600)

async def get_total_stars(org_name):
    if org_name in cache:
        return cache[org_name]

    async with aiohttp.ClientSession() as session:
        url = f"https://api.github.com/search/repositories?q=org:{org_name}&sort=stars&order=desc&per_page=1"
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="GitHub API error")
            data = await response.json()
            total_stars = data.get('total_count', 0)

    cache[org_name] = total_stars
    return total_stars

@app.get("/")
async def generate_svg(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = await get_total_stars(org)
        badge = pybadges.badge(left_text='stars', right_text=str(total_stars), right_color='green')
        return Response(content=badge, media_type="image/svg+xml")
    except HTTPException as e:
        error_badge = pybadges.badge(left_text='stars', right_text='error', right_color='red')
        return Response(content=error_badge, media_type="image/svg+xml")

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