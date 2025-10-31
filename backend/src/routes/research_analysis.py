"""
Research Analysis API Routes
Provides REST API endpoints for the Research Analysis feature.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from src.services.research_analysis_service import ResearchAnalysisService
from src.llms.google_ai import get_patent_analysis, get_technical_innovation_analysis, get_prior_art_search_strategy
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research-analysis"])

# Initialize service
research_service = ResearchAnalysisService()

# Request/Response models
class ResearchAnalysisRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=500, description="Research title")
    abstract: str = Field(..., min_length=20, max_length=5000, description="Research abstract")

class ResearchAnalysisResponse(BaseModel):
    id: str
    title: str
    abstract: str
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: str

class SimilaritySearchRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    abstract: str = Field(..., min_length=20, max_length=5000)
    amount: int = Field(default=25, ge=1, le=100, description="Number of results to return")

class AIInsightsRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    abstract: str = Field(..., min_length=20, max_length=5000)
    analysis_type: str = Field(default="novelty", description="Type of analysis: novelty, claims, landscape, infringement")

# In-memory storage for demo (would use database in production)
analysis_storage = {}

@router.post("/analyze", response_model=ResearchAnalysisResponse)
async def analyze_research(
    request: ResearchAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit research for analysis.
    Returns analysis ID and starts background processing.
    """
    try:
        # Validate input
        validation = research_service.validate_research_input(
            request.title, 
            request.abstract
        )
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail={"errors": validation["errors"]}
            )
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Store initial analysis record
        analysis_record = {
            "id": analysis_id,
            "title": request.title,
            "abstract": request.abstract,
            "status": "pending",
            "results": None,
            "created_at": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
        analysis_storage[analysis_id] = analysis_record
        
        # Start background analysis
        background_tasks.add_task(
            perform_analysis,
            analysis_id,
            request.title,
            request.abstract
        )
        
        return ResearchAnalysisResponse(**analysis_record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting research analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/results/{analysis_id}", response_model=ResearchAnalysisResponse)
async def get_analysis_results(analysis_id: str):
    """
    Retrieve analysis results by ID.
    """
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_record = analysis_storage[analysis_id]
        return ResearchAnalysisResponse(**analysis_record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history")
async def get_analysis_history(user_id: Optional[str] = None):
    """
    Get user's analysis history.
    """
    try:
        # For demo, return all analyses (would filter by user in production)
        history = list(analysis_storage.values())
        return {"analyses": history, "total": len(history)}
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/similarity-search")
async def search_similar_patents(request: SimilaritySearchRequest):
    """
    Search for similar patents and publications.
    """
    try:
        # Validate input
        validation = research_service.validate_research_input(
            request.title, 
            request.abstract
        )
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail={"errors": validation["errors"]}
            )
        
        # Perform similarity search
        results = research_service.search_similar_patents(
            title=request.title,
            abstract=request.abstract,
            amount=request.amount,
            debug=False
        )
        
        return {
            "query": {
                "title": request.title,
                "abstract": request.abstract[:100] + "..." if len(request.abstract) > 100 else request.abstract
            },
            "total_results": len(results),
            "patents_found": len([r for r in results if r.get("index") == "patents"]),
            "publications_found": len([r for r in results if r.get("index") == "publications"]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in similarity search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai-insights")
async def get_ai_insights(request: AIInsightsRequest):
    """
    Get AI-powered research insights using Google AI.
    """
    try:
        # Validate input
        validation = research_service.validate_research_input(
            request.title, 
            request.abstract
        )
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail={"errors": validation["errors"]}
            )
        
        # Combine title and abstract for analysis
        research_text = f"Title: {request.title}\n\nAbstract: {request.abstract}"
        
        # Get AI insights based on analysis type
        if request.analysis_type == "technical":
            insights = get_technical_innovation_analysis(research_text)
        elif request.analysis_type == "prior_art":
            insights = get_prior_art_search_strategy(f"Invention Summary: {research_text}")
        else:
            # Default to patent analysis for novelty, claims, landscape, infringement
            insights = get_patent_analysis(research_text, request.analysis_type)
        
        return {
            "analysis_type": request.analysis_type,
            "insights": insights,
            "query": {
                "title": request.title,
                "abstract": request.abstract[:100] + "..." if len(request.abstract) > 100 else request.abstract
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(request: ResearchAnalysisRequest):
    """
    Perform comprehensive analysis combining LogicMill similarity search and Google AI insights.
    """
    try:
        # Validate input
        validation = research_service.validate_research_input(
            request.title, 
            request.abstract
        )
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail={"errors": validation["errors"]}
            )
        
        # Perform similarity search using LogicMill
        similarity_results = research_service.search_similar_patents(
            title=request.title,
            abstract=request.abstract,
            amount=25,
            debug=False
        )
        
        # Get AI insights using Google AI
        research_text = f"Title: {request.title}\n\nAbstract: {request.abstract}"
        
        # Get multiple types of AI analysis
        novelty_analysis = get_patent_analysis(research_text, "novelty")
        technical_analysis = get_technical_innovation_analysis(research_text)
        prior_art_strategy = get_prior_art_search_strategy(f"Invention Summary: {research_text}")
        
        # Combine results
        comprehensive_results = {
            "query": {
                "title": request.title,
                "abstract": request.abstract[:200] + "..." if len(request.abstract) > 200 else request.abstract
            },
            "similarity_search": {
                "total_results": len(similarity_results),
                "patents_found": len([r for r in similarity_results if r.get("index") == "patents"]),
                "publications_found": len([r for r in similarity_results if r.get("index") == "publications"]),
                "results": similarity_results[:10]  # Top 10 results
            },
            "ai_insights": {
                "novelty_analysis": novelty_analysis,
                "technical_analysis": technical_analysis,
                "prior_art_strategy": prior_art_strategy
            },
            "recommendations": [
                "Review similar patents for potential conflicts",
                "Consider filing provisional patent application",
                "Conduct detailed prior art search",
                "Evaluate commercial potential and market size",
                "Develop IP strategy and protection plan"
            ]
        }
        
        return comprehensive_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def perform_analysis(analysis_id: str, title: str, abstract: str):
    """
    Background task to perform the actual analysis.
    """
    try:
        logger.info(f"Starting background analysis for {analysis_id}")
        
        # Update status to processing
        if analysis_id in analysis_storage:
            analysis_storage[analysis_id]["status"] = "processing"
        
        # Perform analysis using service
        results = research_service.analyze_research(
            title=title,
            abstract=abstract,
            debug=False
        )
        
        # Update storage with results
        if analysis_id in analysis_storage:
            analysis_storage[analysis_id]["status"] = "completed"
            analysis_storage[analysis_id]["results"] = results
        
        logger.info(f"Completed background analysis for {analysis_id}")
        
    except Exception as e:
        logger.error(f"Error in background analysis {analysis_id}: {str(e)}")
        
        # Update status to failed
        if analysis_id in analysis_storage:
            analysis_storage[analysis_id]["status"] = "failed"
            analysis_storage[analysis_id]["results"] = {"error": str(e)}