#!/usr/bin/env python3
"""
Simple test to verify backend is working
"""

import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

def test_analyze():
    """Test analyze endpoint"""
    try:
        data = {
            "title": "Simple AI Test",
            "abstract": "A simple test of artificial intelligence technology for basic analysis."
        }
        
        print("Testing /analyze endpoint...")
        response = requests.post(
            "http://localhost:8000/analyze",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Analyze response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            
            # Check key fields
            if "overall_assessment" in result:
                market_score = result["overall_assessment"].get("market_potential_score", "N/A")
                print(f"Market Potential Score: {market_score}")
            
            if "trl_assessment" in result:
                trl_score = result["trl_assessment"].get("trl_score", "N/A")
                print(f"TRL Score: {trl_score}")
                
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Error text: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    return False

if __name__ == "__main__":
    print("🔧 Testing Backend Endpoints")
    print("=" * 40)
    
    if test_health():
        print("✅ Backend is running")
        if test_analyze():
            print("✅ Analysis endpoint working")
        else:
            print("❌ Analysis endpoint not working")
    else:
        print("❌ Backend not responding")