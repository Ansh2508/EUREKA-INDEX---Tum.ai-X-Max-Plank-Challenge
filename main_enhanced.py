from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio

# Import existing modules
from src.analysis import analyze_research_potential
from src.routes import claude_routes, llm_routes, openalex, related_works

# Import new enhanced modules
from src.agents.semantic_alerts import SemanticPatentAlerts
from src.agents.competitor_discovery import CompetitorCollaboratorDiscovery
from src.agents.licensing_opportunities import LicensingOpportunityMapper
from src.agents.enhanced_novelty import EnhancedNoveltyAssessment
from src.services.alexa_integration import AlexaDataIntegration

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Semantic Patent Alerts API")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include existing routers
app.include_router(claude_routes.router, prefix="/claude", tags=["Claude"])
app.include_router(llm_routes.router, prefix="/llm")
app.include_router(openalex.router, prefix="/openalex")
app.include_router(related_works.router)

# Initialize enhanced services
semantic_alerts = SemanticPatentAlerts()
competitor_discovery = CompetitorCollaboratorDiscovery()
licensing_mapper = LicensingOpportunityMapper()
novelty_assessor = EnhancedNoveltyAssessment()
alexa_integration = AlexaDataIntegration()

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

class VoiceQueryRequest(BaseModel):
    research_context: dict = {}

# Existing endpoint
@app.post("/analyze")
def analyze_technology(request: TechRequest):
    result = analyze_research_potential(request.title, request.abstract, debug=False)
    return result

# New enhanced endpoints

@app.post("/semantic-alerts")
async def get_semantic_alerts(request: SemanticAlertRequest):
    """
    Detect patents semantically similar to research results
    """
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

@app.post("/competitor-discovery")
async def discover_competitors_collaborators(request: CompetitorDiscoveryRequest):
    """
    Identify top authors, inventors, and institutions in the domain
    Reveal clusters of activity (not just isolated papers/patents)
    """
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

@app.post("/licensing-opportunities")
async def find_licensing_opportunities(request: LicensingRequest):
    """
    Flag entities that may need licenses from the focal research group
    """
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

@app.post("/novelty-assessment")
async def assess_novelty(request: NoveltyRequest):
    """
    Compare claims of existing patents and scientific publications to research
    Automated novelty assessment for TT professionals
    """
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

@app.post("/comprehensive-analysis")
async def comprehensive_analysis(request: TechRequest):
    """
    Run comprehensive analysis including all enhanced features
    """
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

@app.post("/voice-query")
async def process_voice_query(
    request: VoiceQueryRequest,
    audio_file: UploadFile = File(...)
):
    """
    Process voice queries about patent alerts and research (Alexa integration)
    """
    # Save uploaded audio file temporarily
    temp_file_path = f"temp_audio_{audio_file.filename}"
    with open(temp_file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    try:
        # Process voice query
        result = await alexa_integration.process_voice_query(
            audio_file_path=temp_file_path,
            research_context=request.research_context
        )
        
        return result
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/dashboard-data")
async def get_dashboard_data():
    """
    Get aggregated data for the enhanced dashboard
    """
    # This would typically pull from a database
    return {
        "recent_alerts": [],
        "top_competitors": [],
        "licensing_opportunities": [],
        "novelty_assessments": [],
        "system_status": {
            "alerts_service": "active",
            "competitor_discovery": "active",
            "licensing_mapper": "active",
            "novelty_assessor": "active"
        }
    }

@app.get("/")
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/dashboard")
def read_dashboard():
    return FileResponse(os.path.join("static", "enhanced_dashboard.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
