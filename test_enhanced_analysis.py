#!/usr/bin/env python3
"""
Test script for enhanced research analysis functionality
"""

import requests
import json
import time

def test_enhanced_analysis():
    """Test the enhanced analysis endpoint"""
    
    # Test data
    test_data = {
        "title": "AI-Powered Medical Diagnosis System",
        "abstract": "A novel artificial intelligence system that uses machine learning algorithms to analyze medical images and provide accurate diagnostic recommendations for healthcare professionals. The system employs deep learning neural networks trained on large datasets of medical images to detect patterns and anomalies that may indicate various medical conditions. This technology aims to improve diagnostic accuracy, reduce human error, and accelerate the diagnostic process in clinical settings."
    }
    
    print("🔬 Testing Enhanced Research Analysis")
    print("=" * 50)
    print(f"Title: {test_data['title']}")
    print(f"Abstract: {test_data['abstract'][:100]}...")
    print()
    
    try:
        # Test the enhanced analysis endpoint
        print("📡 Calling enhanced analysis endpoint...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/research/enhanced-analysis",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Response time: {duration:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced analysis successful!")
            print()
            
            # Display key results
            if result.get("success") and result.get("report"):
                report = result["report"]
                
                print("📋 ANALYSIS SUMMARY")
                print("-" * 30)
                
                # Basic analysis metrics
                if "basic_analysis" in report:
                    basic = report["basic_analysis"]
                    if "overall_assessment" in basic:
                        market_score = basic["overall_assessment"].get("market_potential_score", "N/A")
                        print(f"Market Potential Score: {market_score}")
                    
                    if "trl_assessment" in basic:
                        trl_score = basic["trl_assessment"].get("trl_score", "N/A")
                        print(f"Technology Readiness Level: {trl_score}")
                
                # Similarity analysis
                if "similarity_analysis" in report:
                    sim = report["similarity_analysis"]
                    print(f"Total Similar Documents: {sim.get('total_results', 0)}")
                    print(f"Patents Found: {sim.get('patents_found', 0)}")
                    print(f"Publications Found: {sim.get('publications_found', 0)}")
                
                # Executive summary
                if "executive_summary" in report:
                    exec_sum = report["executive_summary"]
                    if "opportunity_score" in exec_sum:
                        print(f"Opportunity Score: {exec_sum['opportunity_score']}/10")
                    if "risk_assessment" in exec_sum:
                        print(f"Risk Assessment: {exec_sum['risk_assessment']}")
                
                # AI insights
                if "ai_insights" in report:
                    ai = report["ai_insights"]
                    print(f"AI Insights Available: {len([k for k, v in ai.items() if v and 'Error:' not in str(v)])}/4")
                
                # Recommendations
                if "recommendations" in report:
                    rec_count = len(report["recommendations"])
                    print(f"Recommendations Generated: {rec_count}")
                
                print()
                print("🎯 DATA SOURCES")
                print("-" * 20)
                data_sources = result.get("data_sources", {})
                for source, description in data_sources.items():
                    print(f"• {source}: {description}")
                
                print()
                print("✨ SAMPLE AI INSIGHT")
                print("-" * 25)
                if "ai_insights" in report and "novelty_assessment" in report["ai_insights"]:
                    novelty = report["ai_insights"]["novelty_assessment"]
                    if novelty and "Error:" not in novelty:
                        # Show first 200 characters of AI insight
                        print(novelty[:200] + "..." if len(novelty) > 200 else novelty)
                    else:
                        print("AI insights not available (check Google AI API configuration)")
                
                print()
                print("🎯 SAMPLE RECOMMENDATIONS")
                print("-" * 30)
                recommendations = report.get("recommendations", [])
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"{i}. {rec}")
                
            else:
                print("❌ Unexpected response format")
                print(json.dumps(result, indent=2)[:500] + "...")
        
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {error_detail}")
            except:
                print(f"Error: {response.text}")
    
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (>60 seconds)")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the backend server running on port 8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_basic_analysis():
    """Test the basic analysis endpoint for comparison"""
    
    test_data = {
        "title": "AI-Powered Medical Diagnosis System",
        "abstract": "A novel artificial intelligence system that uses machine learning algorithms to analyze medical images and provide accurate diagnostic recommendations for healthcare professionals."
    }
    
    print("\n🔬 Testing Basic Analysis (for comparison)")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Basic analysis successful!")
            
            # Check if it's the new enhanced format or old format
            if "basic_analysis" in result:
                print("📊 Response format: Enhanced (comprehensive report)")
            else:
                print("📊 Response format: Legacy (basic analysis)")
                
        else:
            print(f"❌ Basic analysis failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Basic analysis error: {e}")

if __name__ == "__main__":
    test_enhanced_analysis()
    test_basic_analysis()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("💡 The enhanced analysis integrates:")
    print("   • LogicMill API for patent/publication similarity search")
    print("   • Google AI API for intelligent insights and recommendations")
    print("   • Comprehensive market and competitive analysis")
    print("   • Executive summary and risk assessment")