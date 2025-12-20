# Organization Stars

FastAPI service that generates SVG badges showing total star counts for GitHub organizations.

## Highlights

- Fetches star counts across all repos in a GitHub organization
- Generates SVG badges using PyBadges (compatible with shields.io style)
- Fast responses with 1-hour caching (TTLCache)
- GraphQL API for efficient fetching (100 repos per query)
- Automatic REST API fallback if GraphQL fails
- JSON API endpoint for programmatic access

## Architecture

- **API**: FastAPI with async/await and thread pool execution
- **GitHub API**: GraphQL primary, REST fallback via PyGithub
- **Caching**: TTLCache (1 hour TTL, 1000 item max)
- **Performance**: Async execution with 10s timeout, supports GitHub token for higher rate limits

## Tech Stack

- FastAPI, Uvicorn
- PyGithub, httpx (GraphQL)
- PyBadges, cachetools

## Local Development

1. Install deps: `pip install -r requirements.txt`
2. (Optional) Set `GITHUB_TOKEN` env var for higher rate limits
3. Run: `uvicorn main:app --reload`
4. Test: `pytest`

**Note**: Without a GitHub token, you're limited to 60 requests/hour. With a token, you get 5,000 requests/hour.
