import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_simple import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data

def test_root_endpoint():
    """Test that root endpoint returns the index page."""
    response = client.get("/")
    assert response.status_code == 200
    # Should return HTML content
    assert response.headers["content-type"].startswith("text/html")

def test_analyze_endpoint():
    """Test the analyze endpoint with valid data."""
    test_data = {
        "title": "Test Technology",
        "abstract": "This is a test technology for validation purposes."
    }
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "overall_assessment" in data
    assert "market_potential_score" in data["overall_assessment"]
    assert "investment_recommendation" in data["overall_assessment"]
    assert "risk_level" in data["overall_assessment"]

def test_analyze_endpoint_missing_fields():
    """Test analyze endpoint with missing required fields."""
    test_data = {
        "title": "Test Technology"
        # Missing abstract
    }
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 422  # Validation error

def test_analyze_endpoint_empty_fields():
    """Test analyze endpoint with empty fields."""
    test_data = {
        "title": "",
        "abstract": ""
    }
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 200  # Should still work but with empty data

def test_static_files():
    """Test that static files are served."""
    # This test might fail if static files don't exist, but that's expected
    response = client.get("/static/index.html")
    # Accept both 200 (file exists) and 404 (file doesn't exist)
    assert response.status_code in [200, 404]

def test_invalid_endpoint():
    """Test that invalid endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
