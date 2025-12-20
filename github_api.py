"""GitHub API client for fetching organization repository star counts."""
import httpx
from github import Github
from typing import Optional

from config import GITHUB_TOKEN, GITHUB_GRAPHQL_URL, GITHUB_API_TIMEOUT


def get_total_stars_graphql(org_name: str, github_token: Optional[str] = None) -> int:
    """
    Fetch total stars for an organization using GitHub GraphQL API.
    
    Args:
        org_name: GitHub organization name
        github_token: Optional GitHub personal access token
        
    Returns:
        Total number of stars across all repositories
        
    Raises:
        Exception: If the API request fails
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    total_stars = 0
    cursor = None
    has_next_page = True
    
    # GraphQL query to get all repos with star counts
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
    
    while has_next_page:
        variables = {"org": org_name}
        if cursor:
            variables["cursor"] = cursor
        
        # Make GraphQL request
        response = httpx.post(
            GITHUB_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=GITHUB_API_TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"GraphQL API returned status {response.status_code}")
        
        data = response.json()
        
        if "errors" in data:
            error_messages = [err.get("message", "Unknown error") for err in data["errors"]]
            raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
        
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


def get_total_stars_rest(org_name: str, github_token: Optional[str] = None) -> int:
    """
    Fetch total stars for an organization using GitHub REST API (fallback).
    
    Args:
        org_name: GitHub organization name
        github_token: Optional GitHub personal access token
        
    Returns:
        Total number of stars across all repositories
        
    Raises:
        Exception: If the API request fails
    """
    g = Github(github_token) if github_token else Github()
    org = g.get_organization(org_name)
    total_stars = 0
    
    for repo in org.get_repos():
        total_stars += repo.stargazers_count
    
    return total_stars


def get_total_stars(org_name: str, github_token: Optional[str] = None) -> int:
    """
    Fetch total stars for an organization, trying GraphQL first, then REST as fallback.
    
    Args:
        org_name: GitHub organization name
        github_token: Optional GitHub personal access token
        
    Returns:
        Total number of stars across all repositories
        
    Raises:
        Exception: If both API methods fail
    """
    try:
        return get_total_stars_graphql(org_name, github_token)
    except Exception:
        # Fallback to REST API if GraphQL fails
        return get_total_stars_rest(org_name, github_token)

