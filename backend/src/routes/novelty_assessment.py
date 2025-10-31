"""
Novelty Assessment API Routes

This module provides REST API endpoints for novelty assessment functionality,
including research novelty evaluation, prior art analysis, and claim comparison.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from src.services.novelty_assessment_service import NoveltyAssessmentService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/novelty", tags=["novelty-assessment"])

# Initialize service
novelty_service = NoveltyAssessmentService()

# Request/Response Models
class NoveltyAssessmentRequest(BaseModel):
    """Request model for novelty assessment"""
    research_title: str = Field(..., description="Title of the research to assess")
    research_abstract: str = Field(..., description="Abstract describing the research")
    claims: List[str] = Field(..., description="List of specific claims to assess")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

class ClaimComparisonRequest(BaseModel):
    """Request model for claim comparison"""
    research_claims: List[str] = Field(..., description="Claims from the research")
    patent_claims: List[str] = Field(..., description="Claims from existing patent")
    patent_id: str = Field(..., description="Patent identifier for reference")

class NoveltyAssessmentResponse(BaseModel):
    """Response model for novelty assessment initiation"""
    assessment_id: str
    status: str
    message: str

class AssessmentResultResponse(BaseModel):
    """Response model for assessment results"""
    assessment_id: str
    status: str
    research_title: str
    created_at: str
    updated_at: str
    assessment: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ClaimComparisonResponse(BaseModel):
    """Response model for claim comparison"""
    patent_id: str
    overall_similarity: float
    conflict_assessment: str
    claim_comparisons: List[Dict[str, Any]]
    recommendations: List[str]

class AssessmentReportResponse(BaseModel):
    """Response model for assessment reports"""
    assessment_id: str
    report_generated_at: str
    research_title: str
    assessment_summary: Dict[str, Any]
    detailed_report: Optional[Dict[str, Any]] = None
    full_assessment: Dict[str, Any]

# API Endpoints

@router.post("/assess", response_model=NoveltyAssessmentResponse)
async def assess_novelty(request: NoveltyAssessmentRequest):
    """
    Initiate novelty assessment for research
    
    This endpoint starts a comprehensive novelty assessment process that includes:
    - Prior art search across patents and publications
    - Similarity analysis using AI models
    - Patentability evaluation
    - Recommendation generation
    
    The assessment runs asynchronously. Use the returned assessment_id to check progress.
    """
    try:
        logger.info(f"Starting novelty assessment for: {request.research_title}")
        
        result = await novelty_service.assess_novelty(
            research_title=request.research_title,
            research_abstract=request.research_abstract,
            claims=request.claims,
            user_id=request.user_id
        )
        
        return NoveltyAssessmentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error initiating novelty assessment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate novelty assessment: {str(e)}"
        )

@router.get("/results/{assessment_id}", response_model=AssessmentResultResponse)
async def get_assessment_result(assessment_id: str):
    """
    Retrieve novelty assessment results
    
    Get the current status and results of a novelty assessment.
    Status can be: 'processing', 'completed', or 'failed'
    """
    try:
        result = await novelty_service.get_assessment_result(assessment_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Assessment with ID {assessment_id} not found"
            )
        
        return AssessmentResultResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assessment result: {str(e)}"
        )

@router.post("/compare-claims", response_model=ClaimComparisonResponse)
async def compare_claims(request: ClaimComparisonRequest):
    """
    Compare research claims against patent claims
    
    Perform detailed comparison between research claims and existing patent claims
    to identify potential conflicts and similarity levels.
    """
    try:
        logger.info(f"Comparing claims against patent: {request.patent_id}")
        
        result = await novelty_service.compare_claims(
            research_claims=request.research_claims,
            patent_claims=request.patent_claims,
            patent_id=request.patent_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        return ClaimComparisonResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing claims: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare claims: {str(e)}"
        )

@router.get("/report/{assessment_id}", response_model=AssessmentReportResponse)
async def get_assessment_report(
    assessment_id: str,
    detailed: bool = Query(True, description="Include detailed AI analysis in report")
):
    """
    Generate comprehensive assessment report
    
    Generate a detailed report for a completed novelty assessment.
    The report includes summary, detailed analysis, and actionable recommendations.
    """
    try:
        logger.info(f"Generating report for assessment: {assessment_id}")
        
        result = await novelty_service.generate_assessment_report(
            assessment_id=assessment_id,
            include_detailed_analysis=detailed
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Assessment with ID {assessment_id} not found or not completed"
            )
        
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        return AssessmentReportResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating assessment report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate assessment report: {str(e)}"
        )

@router.get("/history")
async def get_user_assessments(
    user_id: str = Query(..., description="User identifier to get assessments for")
):
    """
    Get assessment history for a user
    
    Retrieve all novelty assessments for a specific user, ordered by creation date.
    """
    try:
        logger.info(f"Retrieving assessment history for user: {user_id}")
        
        assessments = await novelty_service.get_user_assessments(user_id)
        
        return {
            "user_id": user_id,
            "total_assessments": len(assessments),
            "assessments": assessments
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user assessments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user assessments: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for novelty assessment service"""
    try:
        # Basic service health check
        return {
            "status": "healthy",
            "service": "novelty-assessment",
            "version": "1.0.0",
            "capabilities": [
                "novelty_assessment",
                "prior_art_search",
                "claim_comparison",
                "report_generation"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )