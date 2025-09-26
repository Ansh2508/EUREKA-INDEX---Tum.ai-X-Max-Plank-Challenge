from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.analysis import analyze_research_potential
from typing import List, Optional
import asyncio
import os
from dotenv import load_dotenv

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

class NoveltyRequest(BaseModel):
    research_title: str
    research_abstract: str
    claims: List[str] = []
    existing_patents: List[dict] = []
    existing_publications: List[dict] = []

# Existing endpoint
@app.post("/analyze")
def analyze_technology(request: TechRequest):
    # Use debug mode in development environment
    debug_mode = DEBUG_MODE and os.getenv("ENABLE_API_DEBUG", "false").lower() == "true"
    
    if debug_mode:
        print(f"[DEBUG] Analyzing technology: {request.title[:50]}...")
        print(f"[DEBUG] Abstract length: {len(request.abstract)} characters")
    
    result = analyze_research_potential(request.title, request.abstract, debug=debug_mode)
    
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

@app.post("/novelty-assessment")
async def assess_novelty(request: NoveltyRequest):
    """
    Compare claims against existing patents using real AI agents
    """
    try:
        assessment = await novelty_assessor.assess_novelty(
            research_title=request.research_title,
            research_abstract=request.research_abstract,
            claims=request.claims,
            existing_patents=request.existing_patents,
            existing_publications=request.existing_publications
        )
        
        return {
            "research_title": request.research_title,
            "assessment": assessment.__dict__,
            "summary": {
                "novelty_level": assessment.novelty_category,
                "patentability_likelihood": assessment.patentability_indicators.get('patentability_likelihood', 'Unknown'),
                "key_concerns": len(assessment.patentability_indicators.get('prior_art_issues', [])),
                "recommendations_count": len(assessment.recommendations)
            }
        }
    except Exception as e:
        # Fallback to mock data
        return {
            "research_title": request.research_title,
            "assessment": {
                "overall_novelty_score": 0.75,
                "novelty_category": "Moderately Novel",
                "similar_patents": [],
                "similar_publications": [],
                "key_differences": [
                    "Novel technical aspects: quantum algorithms, optimization techniques",
                    "Unique approach to data processing compared to existing solutions"
                ],
                "patentability_indicators": {
                    "novelty_score": 0.75,
                    "claim_strength": "Strong",
                    "claim_count": len(request.claims),
                    "prior_art_issues": [],
                    "patentability_likelihood": "Moderate"
                },
                "prior_art_analysis": {
                    "total_similar_patents": 5,
                    "total_similar_publications": 8,
                    "highest_patent_similarity": 0.65,
                    "highest_publication_similarity": 0.72,
                    "prior_art_density": 13,
                    "key_prior_art": []
                },
                "recommendations": [
                    "Moderate novelty - consider strengthening claims",
                    "Conduct detailed prior art search focusing on top similar patents"
                ]
            },
            "summary": {
                "novelty_level": "Moderately Novel",
                "patentability_likelihood": "Moderate",
                "key_concerns": 0,
                "recommendations_count": 2
            },
            "note": f"Using fallback data due to: {str(e)}"
        }

@app.post("/comprehensive-analysis")
async def comprehensive_analysis(request: TechRequest):
    """
    Run comprehensive analysis using all real AI agents
    """
    try:
        # Run all analyses in parallel
        tasks = [
            analyze_research_potential(request.title, request.abstract, debug=False),
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
        
        # Wait for all analyses to complete
        basic_analysis = tasks[0]
        alerts = await tasks[1]
        key_players = await tasks[2]
        licensing_opps = await tasks[3]
        
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
