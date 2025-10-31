import pytest
from unittest.mock import patch, Mock
from src.services.research_analysis_service import ResearchAnalysisService

@pytest.fixture
def service():
    return ResearchAnalysisService()

@pytest.fixture
def sample_research():
    return {
        "title": "Machine Learning Algorithm for Data Processing",
        "abstract": "This research presents a novel machine learning algorithm for efficient data processing and pattern recognition in large datasets. The algorithm uses advanced neural network architectures to achieve superior performance."
    }

def test_validate_research_input_valid(service, sample_research):
    """Test validation with valid input."""
    result = service.validate_research_input(
        sample_research["title"], 
        sample_research["abstract"]
    )
    assert result["valid"] is True
    assert len(result["errors"]) == 0

def test_validate_research_input_invalid_title(service):
    """Test validation with invalid title."""
    result = service.validate_research_input("", "Valid abstract with sufficient length for testing purposes")
    assert result["valid"] is False
    assert "Title must be at least 5 characters long" in result["errors"]

def test_validate_research_input_invalid_abstract(service):
    """Test validation with invalid abstract."""
    result = service.validate_research_input("Valid Title", "Short")
    assert result["valid"] is False
    assert "Abstract must be at least 20 characters long" in result["errors"]

def test_validate_research_input_too_long(service):
    """Test validation with input that's too long."""
    long_title = "x" * 501
    long_abstract = "x" * 5001
    
    result = service.validate_research_input(long_title, long_abstract)
    assert result["valid"] is False
    assert "Title must be less than 500 characters" in result["errors"]
    assert "Abstract must be less than 5000 characters" in result["errors"]

@patch('src.services.research_analysis_service.analyze_research_potential')
def test_analyze_research(mock_analyze, service, sample_research):
    """Test research analysis."""
    # Mock the analysis function
    mock_result = {
        "overall_assessment": {"market_potential_score": 8.5},
        "trl_assessment": {"trl_score": 6},
        "market_analysis": {"tam_billion_usd": 100}
    }
    mock_analyze.return_value = mock_result
    
    result = service.analyze_research(
        sample_research["title"],
        sample_research["abstract"]
    )
    
    assert result == mock_result
    mock_analyze.assert_called_once_with(
        sample_research["title"],
        sample_research["abstract"],
        debug=False
    )

@patch('src.services.research_analysis_service.search_logic_mill')
def test_search_similar_patents(mock_search, service, sample_research):
    """Test similarity search."""
    # Mock the search function
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
    
    result = service.search_similar_patents(
        sample_research["title"],
        sample_research["abstract"],
        amount=10
    )
    
    assert result == mock_results
    mock_search.assert_called_once_with(
        title=sample_research["title"],
        abstract=sample_research["abstract"],
        amount=10,
        indices=["patents", "publications"],
        debug=False
    )

def test_get_analysis_history(service):
    """Test getting analysis history."""
    result = service.get_analysis_history()
    assert isinstance(result, list)
    # Currently returns empty list as placeholder