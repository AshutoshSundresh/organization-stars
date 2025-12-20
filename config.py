"""Configuration settings for the application."""
import os

# Cache settings
CACHE_MAX_SIZE = 1000
CACHE_TTL_SECONDS = 3600  # 1 hour

# GitHub API settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
GITHUB_API_TIMEOUT = 10.0  # 10 seconds (Vercel free tier limit)

# Thread pool settings
THREAD_POOL_MAX_WORKERS = 2

# Badge cache headers
BADGE_CACHE_MAX_AGE = 3600  # 1 hour
ERROR_BADGE_CACHE_MAX_AGE = 60  # 1 minute

