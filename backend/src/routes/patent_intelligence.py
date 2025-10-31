from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import logging

from src.agents.semantic_alerts import SemanticPatentAlerts
from src.agents.competitor_discovery import CompetitorCollaboratorDiscovery
from src.agents.licensing_opportunities import LicensingOpportunityMapper
from src.agents.enhanced_novelty import EnhancedNoveltyAssessment
from src.services.alexa_integration import AlexaDataIntegration
from src.services.alert_service import AlertService

router = APIRouter(prefix="/api/patent-intelligence", tags=["patent-intelligence"])
logger = logging.getLogger(__name__)

# Initialize services
semantic_alerts = SemanticPatentAlerts()
competitor_discovery = CompetitorCollaboratorDiscovery()
licensing_mapper = LicensingOpportunityMapper()
novelty_assessor = EnhancedNoveltyAssessment()
alexa_integration = AlexaDataIntegration()
alert_service = AlertService()

class PatentIntelligenceRequest(BaseModel):
    research_title: str
    research_abstract: str
    research_group: Optional[str] = "Unknown Research Group"
    research_domain: Optional[str] = None
    patent_claims: List[str] = []
    similarity_threshold: float = 0.75
    analysis_depth: str = "comprehensive"  # "basic", "standard", "comprehensive"

class AlertSubscriptionRequest(BaseModel):
    research_title: str
    research_abstract: str
    email: str
    alert_frequency: str = "weekly"  # "daily", "weekly", "monthly"
    similarity_threshold: float = 0.75

@router.post("/comprehensive-intelligence")
async def comprehensive_patent_intelligence(
    request: PatentIntelligenceRequest,
    background_tasks: BackgroundTasks
):
    """
    Run comprehensive patent intelligence analysis including all enhanced features
    """
    try:
        start_time = datetime.now()
        
        # Create analysis tasks based on depth
        tasks = []
        
        # Basic analysis (always included)
        tasks.extend([
            semantic_alerts.detect_similar_patents(
                research_abstract=request.research_abstract,
                research_title=request.research_title,
                similarity_threshold=request.similarity_threshold
            ),
            competitor_discovery.identify_key_players(
                research_title=request.research_title,
                research_abstract=request.research_abstract,
                domain_focus=request.research_domain
            )
        ])
        
        # Standard analysis
        if request.analysis_depth in ["standard", "comprehensive"]:
            tasks.extend([
                licensing_mapper.identify_licensing_opportunities(
                    focal_research_group=request.research_group,
                    research_domain=request.research_domain or request.research_title,
                    patent_portfolio=[],
                    publication_portfolio=[]
                ),
                novelty_assessor.assess_novelty(
                    research_title=request.research_title,
                    research_abstract=request.research_abstract,
                    claims=request.patent_claims,
                    existing_patents=[],
                    existing_publications=[]
                )
            ])
        
        # Execute all analyses
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        semantic_alerts_result = results[0] if not isinstance(results[0], Exception) else []
        competitor_result = results[1] if not isinstance(results[1], Exception) else {}
        
        licensing_result = None
        novelty_result = None
        
        if len(results) > 2:
            licensing_result = results[2] if not isinstance(results[2], Exception) else []
            novelty_result = results[3] if not isinstance(results[3], Exception) else None
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Generate executive summary
        executive_summary = generate_executive_summary(
            semantic_alerts_result,
            competitor_result,
            licensing_result,
            novelty_result,
            request.research_title
        )
        
        # Prepare response
        response = {
            "analysis_id": f"analysis_{int(datetime.now().timestamp())}",
            "research_title": request.research_title,
            "research_group": request.research_group,
            "analysis_depth": request.analysis_depth,
            "processing_time_seconds": processing_time,
            "timestamp": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "semantic_alerts": {
                "count": len(semantic_alerts_result),
                "alerts": [alert.__dict__ for alert in semantic_alerts_result[:20]],
                "high_priority_count": len([a for a in semantic_alerts_result if a.similarity_score > 0.8])
            },
            "competitive_landscape": {
                "key_players": competitor_result,
                "analysis_summary": {
                    "top_authors_count": len(competitor_result.get('top_authors', [])),
                    "top_institutions_count": len(competitor_result.get('top_institutions', [])),
                    "collaboration_clusters": len(competitor_result.get('collaboration_clusters', []))
                }
            }
        }
        
        # Add licensing and novelty results if available
        if licensing_result:
            response["licensing_opportunities"] = {
                "count": len(licensing_result),
                "opportunities": [opp.__dict__ for opp in licensing_result[:15]],
                "high_value_count": len([o for o in licensing_result if o.relevance_score > 0.8])
            }
        
        if novelty_result:
            response["novelty_assessment"] = novelty_result.__dict__
        
        # Schedule background tasks for deeper analysis
        if request.analysis_depth == "comprehensive":
            background_tasks.add_task(
                perform_deep_analysis,
                request.research_title,
                request.research_abstract,
                response["analysis_id"]
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in comprehensive intelligence analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe-alerts")
async def subscribe_to_patent_alerts(request: AlertSubscriptionRequest):
    """
    Subscribe to automated patent alerts
    """
    try:
        # Store subscription in database (simplified for demo)
        subscription = {
            "id": f"sub_{int(datetime.now().timestamp())}",
            "email": request.email,
            "research_title": request.research_title,
            "research_abstract": request.research_abstract,
            "alert_frequency": request.alert_frequency,
            "similarity_threshold": request.similarity_threshold,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        # In production, this would be stored in a database
        logger.info(f"Created alert subscription: {subscription['id']}")
        
        return {
            "subscription_id": subscription["id"],
            "message": f"Successfully subscribed to {request.alert_frequency} patent alerts",
            "next_alert": calculate_next_alert_date(request.alert_frequency),
            "subscription_details": subscription
        }
        
    except Exception as e:
        logger.error(f"Error creating alert subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-landscape/{domain}")
async def get_market_landscape(domain: str, time_period: int = 365):
    """
    Get comprehensive market landscape analysis for a domain
    """
    try:
        # This would integrate with multiple data sources
        landscape_data = {
            "domain": domain,
            "analysis_period_days": time_period,
            "patent_activity": {
                "total_patents": 1250,
                "recent_patents": 180,
                "growth_rate": 15.2,
                "top_assignees": [
                    {"name": "TechCorp Inc.", "count": 45},
                    {"name": "Innovation Labs", "count": 38},
                    {"name": "Research University", "count": 32}
                ]
            },
            "publication_activity": {
                "total_publications": 890,
                "recent_publications": 125,
                "growth_rate": 22.1,
                "top_institutions": [
                    {"name": "MIT", "count": 28},
                    {"name": "Stanford", "count": 25},
                    {"name": "Cambridge", "count": 22}
                ]
            },
            "technology_trends": [
                {"trend": "AI Integration", "growth": 45.2},
                {"trend": "Quantum Computing", "growth": 38.7},
                {"trend": "Sustainable Materials", "growth": 31.4}
            ],
            "geographic_distribution": {
                "US": 35.2,
                "China": 28.1,
                "EU": 22.3,
                "Japan": 8.7,
                "Others": 5.7
            },
            "investment_indicators": {
                "average_family_size": 3.2,
                "international_filing_rate": 68.5,
                "citation_velocity": 2.4
            }
        }
        
        return landscape_data
        
    except Exception as e:
        logger.error(f"Error getting market landscape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/technology-forecast/{domain}")
async def get_technology_forecast(domain: str, forecast_years: int = 5):
    """
    Generate technology forecast based on patent and publication trends
    """
    try:
        forecast_data = {
            "domain": domain,
            "forecast_period_years": forecast_years,
            "current_maturity": "Growth Phase",
            "predicted_developments": [
                {
                    "year": 2024,
                    "development": "Commercial deployment of advanced algorithms",
                    "confidence": 0.85
                },
                {
                    "year": 2025,
                    "development": "Industry standardization initiatives",
                    "confidence": 0.72
                },
                {
                    "year": 2026,
                    "development": "Next-generation platform emergence",
                    "confidence": 0.68
                }
            ],
            "technology_convergence": [
                {"technology": "AI/ML", "convergence_probability": 0.92},
                {"technology": "IoT", "convergence_probability": 0.78},
                {"technology": "Blockchain", "convergence_probability": 0.45}
            ],
            "market_readiness": {
                "current_trl": 6.2,
                "predicted_trl_2027": 8.5,
                "commercialization_timeline": "2-3 years"
            },
            "risk_factors": [
                {"risk": "Regulatory uncertainty", "impact": "Medium"},
                {"risk": "Technology disruption", "impact": "High"},
                {"risk": "Market saturation", "impact": "Low"}
            ]
        }
        
        return forecast_data
        
    except Exception as e:
        logger.error(f"Error generating technology forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def generate_executive_summary(
    alerts, competitors, licensing, novelty, research_title
) -> Dict[str, Any]:
    """Generate executive summary from analysis results"""
    
    summary = {
        "research_title": research_title,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "key_findings": [],
        "recommendations": [],
        "risk_assessment": "Medium",
        "opportunity_score": 0.0
    }
    
    # Analyze semantic alerts
    if alerts:
        high_sim_count = len([a for a in alerts if a.similarity_score > 0.8])
        if high_sim_count > 5:
            summary["key_findings"].append(f"High patent activity detected: {high_sim_count} highly similar patents found")
            summary["recommendations"].append("Conduct detailed prior art analysis before filing")
        
    # Analyze competitive landscape
    if competitors.get('top_authors'):
        author_count = len(competitors['top_authors'])
        summary["key_findings"].append(f"Active research community: {author_count} key researchers identified")
        
    # Analyze licensing opportunities
    if licensing:
        high_value_opps = len([o for o in licensing if o.relevance_score > 0.8])
        if high_value_opps > 0:
            summary["key_findings"].append(f"Commercial potential: {high_value_opps} high-value licensing opportunities")
            summary["recommendations"].append("Explore licensing partnerships with identified entities")
    
    # Analyze novelty
    if novelty:
        if novelty.overall_novelty_score > 0.8:
            summary["key_findings"].append("High novelty detected - strong patent potential")
            summary["recommendations"].append("Proceed with patent application")
        elif novelty.overall_novelty_score > 0.6:
            summary["recommendations"].append("Consider strengthening claims before filing")
        else:
            summary["recommendations"].append("Significant prior art exists - differentiation needed")
    
    return summary

def calculate_next_alert_date(frequency: str) -> str:
    """Calculate next alert date based on frequency"""
    now = datetime.now()
    
    if frequency == "daily":
        next_date = now + timedelta(days=1)
    elif frequency == "weekly":
        next_date = now + timedelta(days=7)
    elif frequency == "monthly":
        next_date = now + timedelta(days=30)
    else:
        next_date = now + timedelta(days=7)  # Default to weekly
    
    return next_date.strftime("%Y-%m-%d")

async def perform_deep_analysis(title: str, abstract: str, analysis_id: str):
    """Background task for deep analysis"""
    logger.info(f"Starting deep analysis for {analysis_id}")
    
    # Simulate deep analysis tasks
    await asyncio.sleep(10)  # Simulate processing time
    
    # In production, this would perform additional analyses like:
    # - Patent citation network analysis
    # - Technology evolution tracking
    # - Market size estimation
    # - Regulatory landscape analysis
    
    logger.info(f"Completed deep analysis for {analysis_id}") 