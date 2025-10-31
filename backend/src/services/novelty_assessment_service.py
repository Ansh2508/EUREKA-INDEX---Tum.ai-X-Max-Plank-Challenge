"""
Novelty Assessment Service

This service provides comprehensive novelty assessment functionality for research
and patent applications, including prior art analysis, similarity scoring, and
patentability evaluation.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import logging
from dataclasses import asdict

from src.agents.enhanced_novelty import EnhancedNoveltyAssessment, NoveltyAssessment
from src.services.logic_mill import search_similar_patents_publications
from src.services.openalex import fetch_publication_metadata
from src.services.espacenet import fetch_patent_metadata
from src.services.ai_report_generator import AIReportGenerator

logger = logging.getLogger(__name__)

class NoveltyAssessmentService:
    """Service for conducting comprehensive novelty assessments"""
    
    def __init__(self):
        self.novelty_assessor = EnhancedNoveltyAssessment()
        self.report_generator = AIReportGenerator()
        # In-memory storage for demo - replace with database in production
        self.assessments: Dict[str, Dict[str, Any]] = {}
    
    async def assess_novelty(
        self,
        research_title: str,
        research_abstract: str,
        claims: List[str],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive novelty assessment for research
        
        Args:
            research_title: Title of the research
            research_abstract: Abstract describing the research
            claims: List of specific claims to assess
            user_id: Optional user identifier
            
        Returns:
            Dictionary containing assessment ID and initial status
        """
        assessment_id = str(uuid.uuid4())
        
        # Store initial assessment record
        self.assessments[assessment_id] = {
            "id": assessment_id,
            "research_title": research_title,
            "research_abstract": research_abstract,
            "claims": claims,
            "user_id": user_id,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "assessment": None,
            "report": None
        }
        
        # Start background processing
        asyncio.create_task(self._process_assessment(assessment_id))
        
        return {
            "assessment_id": assessment_id,
            "status": "processing",
            "message": "Novelty assessment started. Use the assessment ID to check progress."
        }
    
    async def _process_assessment(self, assessment_id: str):
        """Background processing of novelty assessment"""
        try:
            assessment_record = self.assessments[assessment_id]
            
            # Search for similar patents and publications
            logger.info(f"Searching for prior art for assessment {assessment_id}")
            
            # Search for similar patents
            similar_patents = await self._search_similar_patents(
                assessment_record["research_title"],
                assessment_record["research_abstract"]
            )
            
            # Search for similar publications
            similar_publications = await self._search_similar_publications(
                assessment_record["research_title"],
                assessment_record["research_abstract"]
            )
            
            # Conduct novelty assessment
            logger.info(f"Conducting novelty assessment for {assessment_id}")
            assessment = await self.novelty_assessor.assess_novelty(
                research_title=assessment_record["research_title"],
                research_abstract=assessment_record["research_abstract"],
                claims=assessment_record["claims"],
                existing_patents=similar_patents,
                existing_publications=similar_publications
            )
            
            # Update assessment record
            assessment_record["assessment"] = asdict(assessment)
            assessment_record["status"] = "completed"
            assessment_record["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Novelty assessment completed for {assessment_id}")
            
        except Exception as e:
            logger.error(f"Error processing assessment {assessment_id}: {str(e)}")
            assessment_record = self.assessments.get(assessment_id, {})
            assessment_record["status"] = "failed"
            assessment_record["error"] = str(e)
            assessment_record["updated_at"] = datetime.utcnow().isoformat()
    
    async def _search_similar_patents(self, title: str, abstract: str) -> List[Dict]:
        """Search for similar patents using Logic Mill API"""
        try:
            query = f"{title}. {abstract}"
            # Note: search_similar_patents_publications might not be async, handle both cases
            try:
                results = await search_similar_patents_publications(query)
            except TypeError:
                # If function is not async, call it normally
                results = search_similar_patents_publications(query)
            
            # Filter for patents only
            patents = []
            for result in results.get("patents", []):
                # Enhance with metadata if available
                try:
                    # Note: fetch_patent_metadata might not be async, handle both cases
                    try:
                        metadata = await fetch_patent_metadata(result.get("id", ""))
                    except TypeError:
                        metadata = fetch_patent_metadata(result.get("id", ""))
                    
                    if metadata:
                        result.update(metadata)
                except Exception as e:
                    logger.warning(f"Could not fetch patent metadata: {e}")
                
                patents.append(result)
            
            return patents[:20]  # Limit to top 20 for processing efficiency
            
        except Exception as e:
            logger.error(f"Error searching similar patents: {e}")
            return []
    
    async def _search_similar_publications(self, title: str, abstract: str) -> List[Dict]:
        """Search for similar publications using OpenAlex API"""
        try:
            query = f"{title}. {abstract}"
            # Note: search_similar_patents_publications might not be async, handle both cases
            try:
                results = await search_similar_patents_publications(query)
            except TypeError:
                # If function is not async, call it normally
                results = search_similar_patents_publications(query)
            
            # Filter for publications only
            publications = []
            for result in results.get("publications", []):
                # Enhance with metadata if available
                try:
                    # Note: fetch_publication_metadata might not be async, handle both cases
                    try:
                        metadata = await fetch_publication_metadata(result.get("id", ""))
                    except TypeError:
                        metadata = fetch_publication_metadata(result.get("id", ""))
                    
                    if metadata:
                        result.update(metadata)
                except Exception as e:
                    logger.warning(f"Could not fetch publication metadata: {e}")
                
                publications.append(result)
            
            return publications[:20]  # Limit to top 20 for processing efficiency
            
        except Exception as e:
            logger.error(f"Error searching similar publications: {e}")
            return []
    
    async def get_assessment_result(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve assessment results by ID
        
        Args:
            assessment_id: Unique assessment identifier
            
        Returns:
            Assessment results or None if not found
        """
        return self.assessments.get(assessment_id)
    
    async def compare_claims(
        self,
        research_claims: List[str],
        patent_claims: List[str],
        patent_id: str
    ) -> Dict[str, Any]:
        """
        Compare specific research claims against patent claims
        
        Args:
            research_claims: Claims from the research
            patent_claims: Claims from existing patent
            patent_id: Patent identifier for reference
            
        Returns:
            Detailed claim comparison analysis
        """
        try:
            # Create embeddings for claim comparison
            research_text = " ".join(research_claims)
            patent_text = " ".join(patent_claims)
            
            # Use the novelty assessor's model for consistency
            research_embedding = self.novelty_assessor.model.encode([research_text])
            patent_embedding = self.novelty_assessor.model.encode([patent_text])
            
            # Calculate similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(research_embedding, patent_embedding)[0][0]
            
            # Analyze individual claim similarities
            claim_comparisons = []
            for i, research_claim in enumerate(research_claims):
                research_claim_embedding = self.novelty_assessor.model.encode([research_claim])
                
                best_match_score = 0
                best_match_claim = ""
                
                for j, patent_claim in enumerate(patent_claims):
                    patent_claim_embedding = self.novelty_assessor.model.encode([patent_claim])
                    claim_similarity = cosine_similarity(research_claim_embedding, patent_claim_embedding)[0][0]
                    
                    if claim_similarity > best_match_score:
                        best_match_score = claim_similarity
                        best_match_claim = patent_claim
                
                claim_comparisons.append({
                    "research_claim_index": i,
                    "research_claim": research_claim,
                    "best_matching_patent_claim": best_match_claim,
                    "similarity_score": float(best_match_score),
                    "conflict_risk": "High" if best_match_score > 0.8 else "Medium" if best_match_score > 0.6 else "Low"
                })
            
            return {
                "patent_id": patent_id,
                "overall_similarity": float(similarity),
                "conflict_assessment": "High Risk" if similarity > 0.8 else "Medium Risk" if similarity > 0.6 else "Low Risk",
                "claim_comparisons": claim_comparisons,
                "recommendations": self._generate_claim_recommendations(similarity, claim_comparisons)
            }
            
        except Exception as e:
            logger.error(f"Error comparing claims: {e}")
            return {
                "error": f"Failed to compare claims: {str(e)}",
                "patent_id": patent_id
            }
    
    def _generate_claim_recommendations(
        self,
        overall_similarity: float,
        claim_comparisons: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on claim comparison"""
        recommendations = []
        
        high_risk_claims = [c for c in claim_comparisons if c["conflict_risk"] == "High"]
        medium_risk_claims = [c for c in claim_comparisons if c["conflict_risk"] == "Medium"]
        
        if overall_similarity > 0.8:
            recommendations.append("High overall similarity detected - significant claim revision recommended")
        elif overall_similarity > 0.6:
            recommendations.append("Moderate similarity - consider narrowing claims to avoid conflicts")
        
        if high_risk_claims:
            recommendations.append(f"{len(high_risk_claims)} claims have high conflict risk - prioritize revision")
        
        if medium_risk_claims:
            recommendations.append(f"{len(medium_risk_claims)} claims have medium conflict risk - review and refine")
        
        if not high_risk_claims and not medium_risk_claims:
            recommendations.append("Claims appear to have low conflict risk with this patent")
        
        return recommendations
    
    async def generate_assessment_report(
        self,
        assessment_id: str,
        include_detailed_analysis: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate comprehensive assessment report
        
        Args:
            assessment_id: Assessment identifier
            include_detailed_analysis: Whether to include detailed AI analysis
            
        Returns:
            Generated report or None if assessment not found
        """
        assessment_record = self.assessments.get(assessment_id)
        if not assessment_record or assessment_record["status"] != "completed":
            return None
        
        try:
            # Prepare data for report generation
            assessment_data = assessment_record["assessment"]
            
            # Generate AI report if requested
            if include_detailed_analysis:
                ai_report = await self.report_generator.generate_comprehensive_report(
                    analysis_data={"novelty_assessment": assessment_data},
                    title=assessment_record["research_title"],
                    abstract=assessment_record["research_abstract"]
                )
                
                assessment_record["report"] = ai_report
                assessment_record["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "assessment_id": assessment_id,
                "report_generated_at": datetime.utcnow().isoformat(),
                "research_title": assessment_record["research_title"],
                "assessment_summary": {
                    "novelty_score": assessment_data["overall_novelty_score"],
                    "novelty_category": assessment_data["novelty_category"],
                    "patentability_likelihood": assessment_data["patentability_indicators"].get("patentability_likelihood", "Unknown"),
                    "prior_art_conflicts": assessment_data["patentability_indicators"].get("prior_art_conflicts", 0),
                    "key_recommendations": assessment_data.get("recommendations", [])
                },
                "detailed_report": assessment_record.get("report") if include_detailed_analysis else None,
                "full_assessment": assessment_data
            }
            
        except Exception as e:
            logger.error(f"Error generating report for assessment {assessment_id}: {e}")
            return {
                "error": f"Failed to generate report: {str(e)}",
                "assessment_id": assessment_id
            }
    
    async def get_user_assessments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all assessments for a specific user"""
        user_assessments = []
        for assessment in self.assessments.values():
            if assessment.get("user_id") == user_id:
                # Return summary information only
                user_assessments.append({
                    "assessment_id": assessment["id"],
                    "research_title": assessment["research_title"],
                    "status": assessment["status"],
                    "created_at": assessment["created_at"],
                    "updated_at": assessment["updated_at"]
                })
        
        return sorted(user_assessments, key=lambda x: x["created_at"], reverse=True)