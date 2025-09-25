import pytest
import sys
import os
import requests
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all critical modules can be imported."""
    try:
        import main_simple
        assert True, "main_simple imports successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import main_simple: {e}")

    try:
        from src.analysis import analyze_research_potential
        assert True, "analysis module imports successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import analysis module: {e}")

def test_environment_variables():
    """Test environment variable handling."""
    # Test that the app can start without API keys (should not crash)
    from main_simple import app
    assert app is not None
    assert app.title == "Technology Assessment API"

def test_quantumscape_example():
    """Test the improved assessment with QuantumScape example."""
    try:
        from src.analysis import analyze_research_potential
        
        title = "QuantumScape QSE-5 Solid-State Lithium-Metal Battery Technology"
        abstract = """The QSE-5 is QuantumScape's first planned commercial product. 
        It's designed to offer an unmatched combination of energy density, fast-charging, 
        high power, and a safety profile superior to conventional lithium-ion batteries."""
        
        result = analyze_research_potential(title, abstract, debug=False)
        
        # Check that we get reasonable results
        assert "overall_assessment" in result
        assert "market_potential_score" in result["overall_assessment"]
        
        # Should be better than the old broken assessment
        score = result["overall_assessment"]["market_potential_score"]
        assert score > 3.0, f"Expected score > 3.0, got {score}"
        
    except ImportError:
        pytest.skip("Full analysis module not available - using simple version")

def test_api_response_structure():
    """Test that API responses have expected structure."""
    from fastapi.testclient import TestClient
    from main_simple import app
    
    client = TestClient(app)
    
    response = client.post("/analyze", json={
        "title": "Test Technology",
        "abstract": "Test abstract for validation"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    required_keys = ["overall_assessment"]
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
