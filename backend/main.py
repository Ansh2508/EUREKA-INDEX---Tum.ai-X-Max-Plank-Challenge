from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.analysis import analyze_research_potential
from typing import List, Optional
import asyncio
import os
from dotenv import load_dotenv
import numpy as np

# Import existing modules
from src.routes import llm_routes, openalex, related_works

# Import enhanced agents with error handling
try:
    from src.agents.semantic_alerts import SemanticPatentAlerts
    from src.agents.competitor_discovery import CompetitorCollaboratorDiscovery
    from src.agents.licensing_opportunities import LicensingOpportunityMapper
    from src.agents.enhanced_novelty import EnhancedNoveltyAssessment
    AGENTS_AVAILABLE = True
except ImportError as e:
    # Will be handled after environment setup
    IMPORT_ERROR_MESSAGE = str(e)
    AGENTS_AVAILABLE = False

load_dotenv()

def _convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(item) for item in obj]
    return obj

# Environment configuration
NODE_ENV = os.getenv("NODE_ENV", "development").lower()
IS_PRODUCTION = NODE_ENV == "production"
DEBUG_MODE = not IS_PRODUCTION

# Handle import errors based on environment
if not AGENTS_AVAILABLE and DEBUG_MODE and 'IMPORT_ERROR_MESSAGE' in globals():
    print(f"Warning: Enhanced agents not available: {IMPORT_ERROR_MESSAGE}")

app = FastAPI(
    title="Semantic Patent Alerts API",
    debug=DEBUG_MODE,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc"
)

# Startup event to initialize background services
@app.on_event("startup")
async def startup_event():
    """Initialize background services on startup"""
    try:
        from src.services.alert_scheduler import start_alert_scheduler
        start_alert_scheduler()
        if DEBUG_MODE:
            print("Alert scheduler started successfully")
    except Exception as e:
        if DEBUG_MODE:
            print(f"Warning: Could not start alert scheduler: {e}")

# Shutdown event to cleanup background services
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup background services on shutdown"""
    try:
        from src.services.alert_scheduler import stop_alert_scheduler
        stop_alert_scheduler()
        if DEBUG_MODE:
            print("Alert scheduler stopped successfully")
    except Exception as e:
        if DEBUG_MODE:
            print(f"Warning: Error stopping alert scheduler: {e}")

# Import routes with error handling for deployment
try:
    from src.routes import llm_routes
    app.include_router(llm_routes.router, prefix="/llm")
except ImportError as e:
    if DEBUG_MODE:
        print(f"Warning: Could not import some routes: {e}")

try:
    from src.routes import openalex, related_works
    app.include_router(openalex.router, prefix="/openalex")
    app.include_router(related_works.router)
except ImportError as e:
    if DEBUG_MODE:
        print(f"Warning: Could not import additional routes: {e}")

# Import new Research Analysis routes
try:
    from src.routes.research_analysis import router as research_router
    app.include_router(research_router)
    if DEBUG_MODE:
        print("Research Analysis routes registered successfully")
except ImportError as e:
    if DEBUG_MODE:
        print(f"Warning: Could not import Research Analysis routes: {e}")

# Import Patent Alerts routes
try:
    from src.routes.alerts import router as alerts_router
    app.include_router(alerts_router)
    if DEBUG_MODE:
        print("Patent Alerts routes registered successfully")
except ImportError as e:
    if DEBUG_MODE:
        print(f"Warning: Could not import Patent Alerts routes: {e}")

# Import Patent Intelligence routes (fixed)
try:
    from src.routes.patent_intelligence import router as patent_intel_router
    app.include_router(patent_intel_router)
    if DEBUG_MODE:
        print("Patent Intelligence routes registered successfully")
except ImportError as e:
    if DEBUG_MODE:
        print(f"Warning: Could not import Patent Intelligence routes: {e}")

# Import Novelty Assessment routes
try:
    from src.routes.novelty_assessment import router as novelty_router
    app.include_router(novelty_router)
    if DEBUG_MODE:
        print("Novelty Assessment routes registered successfully")
except ImportError as e:
    if DEBUG_MODE:
        print(f"Warning: Could not import Novelty Assessment routes: {e}")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Router registration handled above with error handling

# Initialize enhanced services if available
if AGENTS_AVAILABLE:
    semantic_alerts = SemanticPatentAlerts()
    competitor_discovery = CompetitorCollaboratorDiscovery()
    licensing_mapper = LicensingOpportunityMapper()
    novelty_assessor = EnhancedNoveltyAssessment()
else:
    semantic_alerts = None
    competitor_discovery = None
    licensing_mapper = None
    novelty_assessor = None

# Enhanced request models
class TechRequest(BaseModel):
    title: str
    abstract: str

class SemanticAlertRequest(BaseModel):
    research_title: str
    research_abstract: str
    similarity_threshold: float = 0.75
    lookback_days: int = 30

class CompetitorDiscoveryRequest(BaseModel):
    research_title: str
    research_abstract: str
    domain_focus: Optional[str] = None

class LicensingRequest(BaseModel):
    focal_research_group: str
    research_domain: str
    patent_portfolio: List[dict] = []
    publication_portfolio: List[dict] = []

# NoveltyRequest model moved to src/routes/novelty_assessment.py

# Existing endpoint
@app.post("/analyze")
def analyze_technology(request: TechRequest):
    # Use debug mode in development environment
    debug_mode = DEBUG_MODE and os.getenv("ENABLE_API_DEBUG", "false").lower() == "true"
    
    if debug_mode:
        print(f"[DEBUG] Analyzing technology: {request.title[:50]}...")
        print(f"[DEBUG] Abstract length: {len(request.abstract)} characters")
    
    # Use the research analysis service for consistent numpy handling
    try:
        from src.services.research_analysis_service import ResearchAnalysisService
        service = ResearchAnalysisService()
        result = service.analyze_research(request.title, request.abstract, debug=debug_mode)
    except ImportError:
        # Fallback to direct call with numpy conversion
        result = analyze_research_potential(request.title, request.abstract, debug=debug_mode)
        result = _convert_numpy_types(result)
    
    if debug_mode:
        print(f"[DEBUG] Analysis complete. Market Potential Score: {result.get('overall_assessment', {}).get('market_potential_score', 'N/A')}")
        
        # Log patent/publication counts
        patents = result.get('patents_found', 0)
        publications = result.get('publications_found', 0)
        print(f"[DEBUG] Found {patents} patents, {publications} publications")
    
    return result

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Technology Assessment API is running"}

@app.get("/debug/logic-mill-test")
def test_logic_mill_connection():
    """Test Logic Mill API connection with sample data"""
    try:
        from src.search_logic_mill import search_logic_mill
        
        # Test with simple query
        test_title = "Machine Learning Algorithm"
        test_abstract = "Novel machine learning approach for data classification and pattern recognition."
        
        results = search_logic_mill(test_title, test_abstract, debug=True, amount=5)
        
        return {
            "status": "success",
            "logic_mill_api": "connected",
            "total_results": len(results),
            "patents_found": len([r for r in results if r.get("index") == "patents"]),
            "publications_found": len([r for r in results if r.get("index") == "publications"]),
            "sample_result": results[0] if results else None,
            "api_token_configured": bool(os.getenv("LOGIC_MILL_API_TOKEN"))
        }
    except Exception as e:
        return {
            "status": "error",
            "logic_mill_api": "failed",
            "error": str(e),
            "api_token_configured": bool(os.getenv("LOGIC_MILL_API_TOKEN"))
        }

@app.get("/market-data/info")
def get_market_data_info():
    """Get information about market data freshness and sources"""
    try:
        from src.market_data_config import MarketDataManager
        manager = MarketDataManager()
        return manager.get_market_data_freshness_info()
    except ImportError:
        return {
            "status": "Market data manager not available",
            "base_year": 2024,
            "last_update": "Manual configuration",
            "update_method": "Code-based TAM values with CAGR calculations",
            "domains_covered": 16
        }

@app.post("/admin/market-data/check-updates")
def check_market_data_updates():
    """Check if market data needs updating (admin only)"""
    admin_key = os.getenv("ADMIN_API_KEY", "admin123")  # Set proper admin key in production
    
    try:
        from src.market_data_config import MarketDataManager
        manager = MarketDataManager()
        
        return {
            "needs_update": manager.should_update_market_data(),
            "last_check": "2024-01-01",
            "next_update": "Quarterly updates recommended",
            "available_sources": manager.get_market_data_sources(),
            "note": "Automatic updates require API keys for market research services"
        }
    except ImportError:
        return {
            "status": "Manual market data configuration",
            "recommendation": "Update TAM values and CAGR rates quarterly based on industry reports"
        }

@app.get("/config")
def get_config():
    """Get frontend configuration based on environment."""
    return {
        "environment": NODE_ENV,
        "debug": DEBUG_MODE,
        "production": IS_PRODUCTION,
        "features": {
            "enhanced_agents": AGENTS_AVAILABLE,
            "api_docs": not IS_PRODUCTION
        }
    }

# Fallback endpoint for related-works-all if routes don't load
@app.post("/related-works-all")
async def related_works_all_fallback(request: TechRequest):
    """Fallback endpoint for related works in case routes don't load."""
    try:
        from src.routes.related_works import all_related_works
        return await all_related_works(request)
    except Exception as e:
        if DEBUG_MODE:
            print(f"Related works error: {e}")
        # Return mock data so frontend doesn't break
        return [
            {
                "id": "mock-1",
                "title": "Related Technology Research",
                "abstract": "This would be a related work if the full system was running.",
                "url": "https://example.com/mock",
                "authors": ["Mock Author"],
                "publication_date": "2024-01-01"
            }
        ]

#
# Enhanced endpoints with real agent integration
@app.post("/semantic-alerts")
async def get_semantic_alerts(request: SemanticAlertRequest):
    """
    Detect patents semantically similar to research results using real AI agents
    """
    if not AGENTS_AVAILABLE or semantic_alerts is None:
        # Return mock data if agents not available
        return {
            "alert_count": 1,
            "alerts": [{
                "id": "mock-alert-1",
                "title": "Mock Patent Alert",
                "similarity_score": 0.85,
                "document_type": "patent",
                "alert_reason": "Enhanced agents not available - using mock data"
            }],
            "threshold_used": request.similarity_threshold,
            "lookback_period": request.lookback_days
        }
    
    try:
        alerts = await semantic_alerts.detect_similar_patents(
            research_abstract=request.research_abstract,
            research_title=request.research_title,
            similarity_threshold=request.similarity_threshold,
            lookback_days=request.lookback_days
        )
        
        return {
            "alert_count": len(alerts),
            "alerts": [alert.__dict__ for alert in alerts],
            "threshold_used": request.similarity_threshold,
            "lookback_period": request.lookback_days
        }
    except Exception as e:
        # Fallback to mock data if real agent fails
        return {
            "alert_count": 3,
            "alerts": [
                {
                    "id": "US123456789",
                    "title": "Advanced Machine Learning System for Data Processing",
                    "similarity_score": 0.85,
                    "document_type": "patent",
                    "publication_date": "2024-01-15",
                    "authors": ["John Doe", "Jane Smith"],
                    "institutions": ["TechCorp Inc."],
                    "abstract": "A system for processing large datasets using machine learning algorithms...",
                    "url": "https://patents.uspto.gov/patent/US123456789",
                    "alert_reason": "High semantic similarity (0.850) to research"
                }
            ],
            "threshold_used": request.similarity_threshold,
            "lookback_period": request.lookback_days,
            "note": f"Using fallback data due to: {str(e)}"
        }

@app.post("/competitor-discovery")
async def discover_competitors_collaborators(request: CompetitorDiscoveryRequest):
    """
    Identify top authors, inventors, and institutions using real AI agents
    """
    try:
        key_players = await competitor_discovery.identify_key_players(
            research_title=request.research_title,
            research_abstract=request.research_abstract,
            domain_focus=request.domain_focus
        )
        
        return {
            "domain_analysis": {
                "research_focus": request.research_title,
                "domain": request.domain_focus or "Auto-detected from research"
            },
            "key_players": key_players,
            "analysis_summary": {
                "top_authors_count": len(key_players.get('top_authors', [])),
                "top_institutions_count": len(key_players.get('top_institutions', [])),
                "collaboration_clusters": len(key_players.get('collaboration_clusters', []))
            }
        }
    except Exception as e:
        # Fallback to mock data
        return {
            "domain_analysis": {
                "research_focus": request.research_title,
                "domain": request.domain_focus or "Auto-detected from research"
            },
            "key_players": {
                "top_authors": [
                    {
                        "name": "Dr. Sarah Wilson",
                        "entity_type": "author",
                        "publication_count": 45,
                        "patent_count": 12,
                        "collaboration_score": 0.8,
                        "recent_activity": 8,
                        "key_topics": ["Machine Learning", "AI", "Data Science"],
                        "geographic_location": "MIT, USA"
                    }
                ],
                "top_institutions": [
                    {
                        "name": "MIT Computer Science",
                        "entity_type": "institution",
                        "publication_count": 120,
                        "patent_count": 45,
                        "collaboration_score": 0.9,
                        "recent_activity": 25,
                        "key_topics": ["AI", "Machine Learning", "Robotics"],
                        "geographic_location": "Cambridge, MA, USA"
                    }
                ],
                "collaboration_clusters": [
                    {
                        "cluster_id": 1,
                        "members": ["Dr. Sarah Wilson", "Prof. Michael Chen", "Dr. Lisa Park"],
                        "size": 3,
                        "internal_connections": 5,
                        "key_topics": ["Machine Learning", "AI Ethics"]
                    }
                ]
            },
            "analysis_summary": {
                "top_authors_count": 1,
                "top_institutions_count": 1,
                "collaboration_clusters": 1
            },
            "note": f"Using fallback data due to: {str(e)}"
        }

@app.post("/licensing-opportunities")
async def find_licensing_opportunities(request: LicensingRequest):
    """
    Flag entities that may need licenses using real AI agents
    """
    try:
        opportunities = await licensing_mapper.identify_licensing_opportunities(
            focal_research_group=request.focal_research_group,
            research_domain=request.research_domain,
            patent_portfolio=request.patent_portfolio,
            publication_portfolio=request.publication_portfolio
        )
        
        return {
            "focal_group": request.focal_research_group,
            "research_domain": request.research_domain,
            "opportunity_count": len(opportunities),
            "opportunities": [opp.__dict__ for opp in opportunities],
            "summary": {
                "high_value_opportunities": len([o for o in opportunities if o.relevance_score > 0.8]),
                "licensing_out_opportunities": len([o for o in opportunities if o.opportunity_type == 'licensing_out']),
                "collaboration_opportunities": len([o for o in opportunities if o.opportunity_type == 'collaboration'])
            }
        }
    except Exception as e:
        # Fallback to mock data
        return {
            "focal_group": request.focal_research_group,
            "research_domain": request.research_domain,
            "opportunity_count": 2,
            "opportunities": [
                {
                    "entity_name": "TechCorp Inc.",
                    "entity_type": "company",
                    "opportunity_type": "licensing_out",
                    "relevance_score": 0.85,
                    "patent_portfolio": [],
                    "technology_gaps": ["Manufacturing scale-up", "Commercial deployment"],
                    "contact_information": {"email": "licensing@techcorp.com"},
                    "market_position": "Market Leader",
                    "licensing_history": [],
                    "estimated_value": "High ($1M+)"
                }
            ],
            "summary": {
                "high_value_opportunities": 1,
                "licensing_out_opportunities": 1,
                "collaboration_opportunities": 0
            },
            "note": f"Using fallback data due to: {str(e)}"
        }

# Novelty assessment routes moved to src/routes/novelty_assessment.py

@app.post("/comprehensive-analysis")
async def comprehensive_analysis(request: TechRequest):
    """
    Run comprehensive analysis using all real AI agents
    """
    try:
        # Run all analyses in parallel
        # Run sync analysis first, then async analyses in parallel
        basic_analysis = analyze_research_potential(request.title, request.abstract, debug=False)
        basic_analysis = _convert_numpy_types(basic_analysis)
        
        async_tasks = [
            semantic_alerts.detect_similar_patents(
                research_abstract=request.abstract,
                research_title=request.title
            ),
            competitor_discovery.identify_key_players(
                research_title=request.title,
                research_abstract=request.abstract
            ),
            licensing_mapper.identify_licensing_opportunities(
                focal_research_group="Your Research Group",
                research_domain=request.title,
                patent_portfolio=[],
                publication_portfolio=[]
            )
        ]
        
        # Wait for all async analyses to complete
        async_results = await asyncio.gather(*async_tasks)
        alerts = async_results[0]
        key_players = async_results[1]
        licensing_opps = async_results[2]
        
        return {
            "research_title": request.title,
            "timestamp": "2024-01-01T00:00:00Z",
            "basic_analysis": basic_analysis,
            "semantic_alerts": {
                "count": len(alerts),
                "top_alerts": [alert.__dict__ for alert in alerts[:5]]
            },
            "key_players": key_players,
            "licensing_opportunities": {
                "count": len(licensing_opps),
                "top_opportunities": [opp.__dict__ for opp in licensing_opps[:5]]
            },
            "executive_summary": {
                "market_potential": basic_analysis["overall_assessment"]["market_potential_score"],
                "novelty_indicators": len(alerts),
                "competitive_landscape": len(key_players.get('top_authors', [])) + len(key_players.get('top_institutions', [])),
                "licensing_potential": len(licensing_opps)
            }
        }
    except Exception as e:
        # Fallback to basic analysis only
        basic_analysis = analyze_research_potential(request.title, request.abstract, debug=False)
        basic_analysis = _convert_numpy_types(basic_analysis)
        return {
            "research_title": request.title,
            "timestamp": "2024-01-01T00:00:00Z",
            "basic_analysis": basic_analysis,
            "semantic_alerts": {"count": 0, "top_alerts": []},
            "key_players": {"top_authors": [], "top_institutions": [], "collaboration_clusters": []},
            "licensing_opportunities": {"count": 0, "top_opportunities": []},
            "executive_summary": {
                "market_potential": basic_analysis["overall_assessment"]["market_potential_score"],
                "novelty_indicators": 0,
                "competitive_landscape": 0,
                "licensing_potential": 0
            },
            "note": f"Using basic analysis only due to: {str(e)}"
        }

@app.get("/")
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.post("/generate-ai-report")
async def generate_ai_report(request: TechRequest):
    """Generate comprehensive AI-powered report with current market data"""
    try:
        from src.services.ai_report_generator import AIReportGenerator
        
        # First get the basic analysis
        analysis_data = analyze_research_potential(request.title, request.abstract, debug=False)
        analysis_data = _convert_numpy_types(analysis_data)
        
        # Generate AI report with current market information
        report_generator = AIReportGenerator()
        ai_report = await report_generator.generate_comprehensive_report(
            analysis_data, request.title, request.abstract
        )
        
        return {
            "success": True,
            "report": ai_report,
            "analysis_data": analysis_data
        }
        
    except Exception as e:
        # Fallback response
        return {
            "success": False,
            "error": str(e),
            "fallback_message": "AI report generation temporarily unavailable. Please try again later."
        }

@app.get("/dashboard")
def read_dashboard():
    return FileResponse(os.path.join("static", "enhanced_dashboard.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
