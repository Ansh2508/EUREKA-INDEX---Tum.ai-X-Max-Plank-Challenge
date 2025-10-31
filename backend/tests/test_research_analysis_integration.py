"""
Integration tests for Research Analysis API endpoints.
Tests the complete workflow from analysis submission to results retrieval.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time


@pytest.fixture
def integration_client():
    """Create test client for integration tests."""
    from main import app
    return TestClient(app)


@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    return {
        "title": "Advanced Machine Learning for Data Processing",
        "abstract": "This research presents a novel machine learning algorithm for efficient data processing and pattern recognition in large datasets. The algorithm uses advanced neural network architectures to improve accuracy and reduce computational complexity."
    }


def test_research_analysis_complete_workflow(integration_client, sample_research_data):
    """Test the complete research analysis workflow."""
    
    # Step 1: Submit research for analysis
    response = integration_client.post("/api/research/analyze", json=sample_research_data)
    assert response.status_code == 200
    
    analysis_data = response.json()
    assert "id" in analysis_data
    assert analysis_data["title"] == sample_research_data["title"]
    assert analysis_data["status"] == "pending"
    
    analysis_id = analysis_data["id"]
    
    # Step 2: Wait a moment for background processing (in real scenario)
    time.sleep(0.1)
    
    # Step 3: Retrieve analysis results
    response = integration_client.get(f"/api/research/results/{analysis_id}")
    assert response.status_code == 200
    
    result_data = response.json()
    assert result_data["id"] == analysis_id
    # Status should be completed or processing
    assert result_data["status"] in ["completed", "processing", "pending"]


def test_similarity_search_endpoint(integration_client, sample_research_data):
    """Test the similarity search endpoint."""
    
    search_request = {
        **sample_research_data,
        "amount": 10
    }
    
    response = integration_client.post("/api/research/similarity-search", json=search_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "patents_found" in data
    assert "publications_found" in data
    assert "results" in data
    
    # Verify query information
    assert data["query"]["title"] == sample_research_data["title"]
    
    # Verify results structure
    if data["results"]:
        result = data["results"][0]
        assert "id" in result
        assert "score" in result
        assert "title" in result


def test_analysis_history_endpoint(integration_client):
    """Test the analysis history endpoint."""
    
    response = integration_client.get("/api/research/history")
    assert response.status_code == 200
    
    data = response.json()
    assert "analyses" in data
    assert "total" in data
    assert isinstance(data["analyses"], list)
    assert isinstance(data["total"], int)


def test_main_analyze_endpoint_compatibility(integration_client, sample_research_data):
    """Test that the main /analyze endpoint still works with the new service."""
    
    response = integration_client.post("/analyze", json=sample_research_data)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that the response has expected structure from analysis.py
    assert "overall_assessment" in data
    assert "technology_assessment" in data
    assert "market_analysis" in data
    assert "commercial_indicators" in data
    assert "competitive_landscape" in data
    assert "ip_strength_analysis" in data
    
    # Verify no numpy serialization issues
    assert isinstance(data["overall_assessment"]["market_potential_score"], (int, float))


def test_error_handling_invalid_analysis_id(integration_client):
    """Test error handling for invalid analysis ID."""
    
    response = integration_client.get("/api/research/results/invalid-id")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


def test_validation_error_handling(integration_client):
    """Test validation error handling for invalid requests."""
    
    # Test with invalid title (too short)
    invalid_request = {
        "title": "AI",  # Too short
        "abstract": "This is a valid abstract that meets the minimum length requirements for the API."
    }
    
    response = integration_client.post("/api/research/analyze", json=invalid_request)
    assert response.status_code == 422  # FastAPI validation error
    
    # Test with invalid abstract (too short)
    invalid_request = {
        "title": "Valid Title for Machine Learning Research",
        "abstract": "Too short"  # Too short
    }
    
    response = integration_client.post("/api/research/analyze", json=invalid_request)
    assert response.status_code == 422  # FastAPI validation error


@patch('src.services.research_analysis_service.search_logic_mill')
def test_logic_mill_integration(mock_logic_mill, integration_client, sample_research_data):
    """Test Logic Mill API integration."""
    
    # Mock Logic Mill response
    mock_logic_mill.return_value = [
        {
            "id": "test-patent-1",
            "score": 0.95,
            "index": "patents",
            "title": "Test Patent Title",
            "url": "https://example.com/patent/1",
            "year": 2023,
            "citations": 10
        },
        {
            "id": "test-pub-1", 
            "score": 0.88,
            "index": "publications",
            "title": "Test Publication Title",
            "url": "https://example.com/pub/1",
            "year": 2023,
            "citations": 5
        }
    ]
    
    # Test similarity search
    response = integration_client.post("/api/research/similarity-search", json={
        **sample_research_data,
        "amount": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify Logic Mill was called
    mock_logic_mill.assert_called_once()
    
    # Verify response structure
    assert data["total_results"] == 2
    assert data["patents_found"] == 1
    assert data["publications_found"] == 1
    
    # Verify results contain mocked data
    results = data["results"]
    assert len(results) == 2
    assert results[0]["id"] == "test-patent-1"
    assert results[1]["id"] == "test-pub-1"


def test_service_layer_integration(integration_client, sample_research_data):
    """Test that the service layer is properly integrated."""
    
    # Import the service to verify it's working
    from src.services.research_analysis_service import ResearchAnalysisService
    
    service = ResearchAnalysisService()
    
    # Test validation
    validation = service.validate_research_input(
        sample_research_data["title"],
        sample_research_data["abstract"]
    )
    assert validation["valid"] is True
    assert len(validation["errors"]) == 0
    
    # Test that the API uses the service
    response = integration_client.post("/api/research/analyze", json=sample_research_data)
    assert response.status_code == 200
    
    # The response should be properly formatted (no numpy issues)
    data = response.json()
    assert isinstance(data["id"], str)
    assert isinstance(data["title"], str)
    assert data["status"] in ["pending", "processing", "completed"]