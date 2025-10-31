import pytest
from fastapi.testclient import TestClient

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data

def test_analyze_endpoint(client, mock_logic_mill, sample_research_data):
    """Test the main analyze endpoint."""
    response = client.post("/analyze", json=sample_research_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check that the response has expected structure
    assert "overall_assessment" in data
    assert "technology_assessment" in data  # Actual field name from analysis.py
    assert "market_analysis" in data

def test_analyze_endpoint_validation(client):
    """Test analyze endpoint with invalid data."""
    # Test with missing title
    response = client.post("/analyze", json={"abstract": "Test abstract"})
    assert response.status_code == 422
    
    # Test with missing abstract
    response = client.post("/analyze", json={"title": "Test title"})
    assert response.status_code == 422

def test_config_endpoint(client):
    """Test the config endpoint."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "environment" in data
    assert "features" in data