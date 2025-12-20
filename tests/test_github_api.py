"""Unit tests for GitHub API client."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from github_api import get_total_stars_graphql, get_total_stars_rest, get_total_stars


class TestGitHubAPIGraphQL:
    """Test cases for GraphQL API."""
    
    @patch('github_api.httpx.post')
    def test_get_total_stars_graphql_single_page(self, mock_post):
        """Test GraphQL API with single page of results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None
                        },
                        "nodes": [
                            {"stargazerCount": 100},
                            {"stargazerCount": 200},
                            {"stargazerCount": 50}
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = get_total_stars_graphql("test_org")
        assert result == 350
        mock_post.assert_called_once()
    
    @patch('github_api.httpx.post')
    def test_get_total_stars_graphql_multiple_pages(self, mock_post):
        """Test GraphQL API with pagination."""
        # First page
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "hasNextPage": True,
                            "endCursor": "cursor123"
                        },
                        "nodes": [
                            {"stargazerCount": 100},
                            {"stargazerCount": 200}
                        ]
                    }
                }
            }
        }
        
        # Second page
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None
                        },
                        "nodes": [
                            {"stargazerCount": 50}
                        ]
                    }
                }
            }
        }
        
        mock_post.side_effect = [mock_response_1, mock_response_2]
        
        result = get_total_stars_graphql("test_org")
        assert result == 350
        assert mock_post.call_count == 2
    
    @patch('github_api.httpx.post')
    def test_get_total_stars_graphql_with_token(self, mock_post):
        """Test GraphQL API with authentication token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [{"stargazerCount": 100}]
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        
        get_total_stars_graphql("test_org", "token123")
        
        # Check that Authorization header was set
        call_args = mock_post.call_args
        assert "Authorization" in call_args.kwargs["headers"]
        assert call_args.kwargs["headers"]["Authorization"] == "token token123"
    
    @patch('github_api.httpx.post')
    def test_get_total_stars_graphql_api_error(self, mock_post):
        """Test GraphQL API error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception, match="GraphQL API returned status 500"):
            get_total_stars_graphql("test_org")
    
    @patch('github_api.httpx.post')
    def test_get_total_stars_graphql_graphql_errors(self, mock_post):
        """Test GraphQL API with GraphQL errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [
                {"message": "Organization not found"}
            ]
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception, match="GraphQL errors"):
            get_total_stars_graphql("test_org")


class TestGitHubAPIREST:
    """Test cases for REST API fallback."""
    
    @patch('github_api.Github')
    def test_get_total_stars_rest(self, mock_github_class):
        """Test REST API fallback."""
        # Mock GitHub client
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        
        # Mock organization
        mock_org = Mock()
        mock_github.get_organization.return_value = mock_org
        
        # Mock repositories
        mock_repo1 = Mock()
        mock_repo1.stargazers_count = 100
        mock_repo2 = Mock()
        mock_repo2.stargazers_count = 200
        mock_org.get_repos.return_value = [mock_repo1, mock_repo2]
        
        result = get_total_stars_rest("test_org")
        assert result == 300
        mock_github.get_organization.assert_called_once_with("test_org")
    
    @patch('github_api.Github')
    def test_get_total_stars_rest_with_token(self, mock_github_class):
        """Test REST API with authentication token."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        
        mock_org = Mock()
        mock_github.get_organization.return_value = mock_org
        mock_org.get_repos.return_value = []
        
        get_total_stars_rest("test_org", "token123")
        
        # Check that Github was initialized with token
        mock_github_class.assert_called_once_with("token123")


class TestGitHubAPIFallback:
    """Test cases for automatic fallback mechanism."""
    
    @patch('github_api.get_total_stars_graphql')
    @patch('github_api.get_total_stars_rest')
    def test_get_total_stars_graphql_success(self, mock_rest, mock_graphql):
        """Test that GraphQL is tried first."""
        mock_graphql.return_value = 500
        result = get_total_stars("test_org")
        assert result == 500
        mock_graphql.assert_called_once_with("test_org", None)
        mock_rest.assert_not_called()
    
    @patch('github_api.get_total_stars_graphql')
    @patch('github_api.get_total_stars_rest')
    def test_get_total_stars_fallback_to_rest(self, mock_rest, mock_graphql):
        """Test fallback to REST API when GraphQL fails."""
        mock_graphql.side_effect = Exception("GraphQL failed")
        mock_rest.return_value = 300
        result = get_total_stars("test_org")
        assert result == 300
        mock_graphql.assert_called_once()
        mock_rest.assert_called_once_with("test_org", None)

