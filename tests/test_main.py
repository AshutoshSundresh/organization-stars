"""Unit tests for FastAPI main application."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

from main import app, create_badge_response


class TestBadgeResponse:
    """Test cases for badge response creation."""
    
    def test_create_badge_response(self):
        """Test badge response creation with headers."""
        response = create_badge_response("1234", "green", 3600)
        assert response.media_type == "image/svg+xml"
        assert "Cache-Control" in response.headers
        assert "max-age=3600" in response.headers["Cache-Control"]
        assert "image/svg+xml" in response.headers["Content-Type"]


class TestEndpoints:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @patch('main.fetch_total_stars', new_callable=AsyncMock)
    def test_generate_svg_success(self, mock_fetch, client):
        """Test successful badge generation."""
        mock_fetch.return_value = 1234
        
        response = client.get("/?org=test_org")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml; charset=utf-8"
        assert "stars" in response.text.lower()
        assert "1234" in response.text
    
    @patch('main.fetch_total_stars', new_callable=AsyncMock)
    def test_generate_svg_error(self, mock_fetch, client):
        """Test error badge generation."""
        mock_fetch.side_effect = HTTPException(status_code=404, detail="Not found")
        
        response = client.get("/?org=invalid_org")
        assert response.status_code == 200  # Returns error badge, not HTTP error
        assert response.headers["content-type"] == "image/svg+xml; charset=utf-8"
        assert "error" in response.text.lower()
    
    @patch('main.fetch_total_stars', new_callable=AsyncMock)
    def test_get_stars_api_success(self, mock_fetch, client):
        """Test successful API endpoint."""
        mock_fetch.return_value = 5678
        
        response = client.get("/api/stars?org=test_org")
        assert response.status_code == 200
        data = response.json()
        assert data["organization"] == "test_org"
        assert data["total_stars"] == 5678
    
    @patch('main.fetch_total_stars')
    def test_get_stars_api_error(self, mock_fetch, client):
        """Test API endpoint error handling."""
        mock_fetch.side_effect = HTTPException(status_code=404, detail="Not found")
        
        response = client.get("/api/stars?org=invalid_org")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
    
    def test_generate_svg_missing_org_param(self, client):
        """Test missing organization parameter."""
        response = client.get("/")
        assert response.status_code == 422  # Validation error
    
    def test_get_stars_api_missing_org_param(self, client):
        """Test missing organization parameter in API endpoint."""
        response = client.get("/api/stars")
        assert response.status_code == 422  # Validation error

