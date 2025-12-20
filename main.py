"""FastAPI application for GitHub organization star count badges."""
import sys
# Workaround for Python 3.13+ where imghdr was removed
if sys.version_info >= (3, 13):
    import importlib.util
    # Create a minimal imghdr module stub
    imghdr_spec = importlib.util.spec_from_loader("imghdr", loader=None)
    imghdr = importlib.util.module_from_spec(imghdr_spec)
    sys.modules["imghdr"] = imghdr

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import pybadges

from config import BADGE_CACHE_MAX_AGE, ERROR_BADGE_CACHE_MAX_AGE
from services import fetch_total_stars

app = FastAPI()

# Add CORS middleware to allow embedding badges
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_badge_response(text: str, color: str, cache_max_age: int) -> Response:
    """Create a badge response with proper headers."""
    badge = pybadges.badge(left_text='stars', right_text=text, right_color=color)
    return Response(
        content=badge,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": f"public, max-age={cache_max_age}, s-maxage={cache_max_age}",
            "Content-Type": "image/svg+xml; charset=utf-8",
        }
    )


@app.get("/")
async def generate_svg(org: str = Query(..., description="GitHub organization name")):
    """Generate an SVG badge showing the total star count for an organization."""
    try:
        total_stars = await fetch_total_stars(org)
        return create_badge_response(str(total_stars), 'green', BADGE_CACHE_MAX_AGE)
    except HTTPException as e:
        return create_badge_response('error', 'red', ERROR_BADGE_CACHE_MAX_AGE)


@app.get("/api/stars")
async def get_stars_api(org: str = Query(..., description="GitHub organization name")):
    """API endpoint to get organization star count as JSON."""
    try:
        total_stars = await fetch_total_stars(org)
        return {"organization": org, "total_stars": total_stars}
    except HTTPException as e:
        return {"error": str(e.detail)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
