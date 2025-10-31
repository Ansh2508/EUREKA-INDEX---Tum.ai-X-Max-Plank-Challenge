import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from main import app
    return TestClient(app)

@pytest.fixture
def mock_logic_mill():
    """Mock Logic Mill API responses."""
    with patch('src.search_logic_mill.search_logic_mill') as mock:
        mock.return_value = [
            {
                "id": "test-patent-1",
                "score": 0.85,
                "index": "patents",
                "title": "Test Patent Title",
                "url": "https://example.com/patent1",
                "year": 2023,
                "citations": 5
            }
        ]
        yield mock

@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    return {
        "title": "Machine Learning Algorithm for Data Processing",
        "abstract": "This research presents a novel machine learning algorithm for efficient data processing and pattern recognition in large datasets."
    }