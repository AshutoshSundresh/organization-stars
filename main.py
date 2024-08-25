from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from github import Github
import pybadges
from cachetools import TTLCache

app = FastAPI()

# Initialize cache with a 1-hour TTL and max size of 1000 items
cache = TTLCache(maxsize=1000, ttl=3600)

def get_total_stars(org_name):
    if org_name in cache:
        return cache[org_name]

    try:
        # Create a GitHub instance
        g = Github()
        # Get the organization from the link
        org = g.get_organization(org_name)
        # Initialize the total number of stars to zero
        total_stars = 0
        # Loop through all repositories in the organization
        for repo in org.get_repos():
            # Add the number of stars for the repository to the total number of stars
            total_stars += repo.stargazers_count
        
        # Cache the result
        cache[org_name] = total_stars
        return total_stars
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching data: {str(e)}")

@app.get("/")
async def generate_svg(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = get_total_stars(org)
        badge = pybadges.badge(left_text='stars', right_text=str(total_stars), right_color='green')
        return Response(content=badge, media_type="image/svg+xml")
    except HTTPException as e:
        error_badge = pybadges.badge(left_text='stars', right_text='error', right_color='red')
        return Response(content=error_badge, media_type="image/svg+xml")

@app.get("/api/stars")
async def get_stars_api(org: str = Query(..., description="GitHub organization name")):
    try:
        total_stars = get_total_stars(org)
        return {"organization": org, "total_stars": total_stars}
    except HTTPException as e:
        return {"error": str(e.detail)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)