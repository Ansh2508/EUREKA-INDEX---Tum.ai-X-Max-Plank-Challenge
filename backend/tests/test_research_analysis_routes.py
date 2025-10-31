import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

@pytest.fixture
def research_client():
    """Create a test client specifically for research analysis routes."""
    from src.routes.research_analysis import router
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def valid_research_request():
    return {
        "title": "Machine Learning Algorithm for Data Processing",
        "abstract": "This research presents a novel machine learning algorithm for efficient data processing and pattern recognition in large datasets. The algorithm uses advanced neural network architectures."
    }

def test_analyze_research_endpoint(research_client, valid_research_request):
    """Test the analyze research endpoint."""
    response = research_client.post("/api/research/analyze", json=valid_research_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert data["title"] == valid_research_request["title"]
    assert data["abstract"] == valid_research_request["abstract"]
    assert data["status"] == "pending"

def test_analyze_research_validation_error(research_client):
    """Test analyze endpoint with invalid data."""
    # Test with short title
    invalid_request = {
        "title": "AI",  # Too short
        "abstract": "This is a valid abstract with sufficient length for testing purposes."
    }
    
    response = research_client.post("/api/research/analyze", json=invalid_request)
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    
    data = response.json()
    assert "detail" in data  # FastAPI validation errors have detail field

def test_analyze_research_missing_fields(research_client):
    """Test analyze endpoint with missing required fields."""
    # Test with missing title
    response = research_client.post("/api/research/analyze", json={"abstract": "Valid abstract"})
    assert response.status_code == 422
    
    # Test with missing abstract
    response = research_client.post("/api/research/analyze", json={"title": "Valid title"})
    assert response.status_code == 422

def test_get_analysis_results_not_found(research_client):
    """Test getting results for non-existent analysis."""
    response = research_client.get("/api/research/results/non-existent-id")
    assert response.status_code == 404

def test_get_analysis_history(research_client):
    """Test getting analysis history."""
    response = research_client.get("/api/research/history")
    assert response.status_code == 200
    
    data = response.json()
    assert "analyses" in data
    assert "total" in data
    assert isinstance(data["analyses"], list)

@patch('src.routes.research_analysis.research_service.search_similar_patents')
def test_similarity_search_endpoint(mock_search, research_client, valid_research_request):
    """Test the similarity search endpoint."""
    # Mock the service response
    mock_results = [
        {
            "id": "patent-1",
            "score": 0.85,
            "index": "patents",
            "title": "Similar Patent",
            "url": "https://example.com/patent1"
        }
    ]
    mock_search.return_value = mock_results
    
    request_data = {**valid_research_request, "amount": 10}
    response = research_client.post("/api/research/similarity-search", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "patents_found" in data
    assert "publications_found" in data
    assert "results" in data
    assert data["results"] == mock_results

def test_similarity_search_validation_error(research_client):
    """Test similarity search with invalid data."""
    invalid_request = {
        "title": "AI",  # Too short
        "abstract": "Short",  # Too short
        "amount": 10
    }
    
    response = research_client.post("/api/research/similarity-search", json=invalid_request)
    assert response.status_code == 422  # FastAPI returns 422 for validation errors