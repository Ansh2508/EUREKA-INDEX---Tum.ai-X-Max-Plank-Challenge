"""
Enhanced Research Analysis with LogicMill API and Google AI Integration
Provides comprehensive analysis combining patent similarity search and AI insights
"""

import json
from typing import Dict, List, Any, Optional
from src.search_logic_mill import search_logic_mill
from src.analysis import analyze_research_potential
import logging

# Import Google AI functions with error handling
try:
    from src.llms.google_ai import (
        get_patent_analysis, 
        get_technical_innovation_analysis, 
        get_google_ai_response
    )
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    GOOGLE_AI_AVAILABLE = False
    logging.warning(f"Google AI not available: {e}")

logger = logging.getLogger(__name__)

def enhanced_research_analysis(title: str, abstract: str, debug: bool = False) -> Dict[str, Any]:
    """
    Perform comprehensive research analysis using LogicMill API and Google AI.
    
    Args:
        title: Research title
        abstract: Research abstract
        debug: Enable debug mode
        
    Returns:
        Dictionary containing comprehensive analysis results
    """
    try:
        if debug:
            print(f"[ENHANCED] Starting comprehensive analysis for: {title[:50]}...")
        
        # Step 1: Get basic market analysis
        basic_analysis = analyze_research_potential(title, abstract, debug=debug)
        
        # Step 2: Search for similar patents and publications using LogicMill API
        if debug:
            print("[ENHANCED] Searching LogicMill API for similar documents...")
        
        similar_documents = search_logic_mill(
            title=title,
            abstract=abstract,
            amount=50,  # Get more results for comprehensive analysis
            indices=["patents", "publications"],
            debug=debug
        )
        
        # Separate patents and publications
        similar_patents = [doc for doc in similar_documents if doc.get("index") == "patents"]
        similar_publications = [doc for doc in similar_documents if doc.get("index") == "publications"]
        
        if debug:
            print(f"[ENHANCED] Found {len(similar_patents)} patents, {len(similar_publications)} publications")
        
        # Step 3: Generate AI insights using Google AI
        ai_insights = generate_ai_insights(title, abstract, similar_documents, debug=debug)
        
        # Step 4: Generate competitive analysis based on similar patents
        competitive_analysis = analyze_competitive_landscape(similar_patents, similar_publications, debug=debug)
        
        # Step 5: Generate executive summary
        executive_summary = generate_executive_summary(
            basic_analysis, similar_documents, ai_insights, debug=debug
        )
        
        # Step 6: Generate actionable recommendations
        recommendations = generate_smart_recommendations(
            basic_analysis, similar_documents, ai_insights, debug=debug
        )
        
        # Combine all results into comprehensive report
        enhanced_report = {
            "research_query": {
                "title": title,
                "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract
            },
            "basic_analysis": basic_analysis,
            "similarity_search": {
                "total_documents": len(similar_documents),
                "patents_found": len(similar_patents),
                "publications_found": len(similar_publications),
                "search_method": "LogicMill API with Patspecter embeddings",
                "top_patents": similar_patents[:10],  # Top 10 most similar patents
                "top_publications": similar_publications[:10],  # Top 10 most similar publications
                "similarity_distribution": analyze_similarity_scores(similar_documents)
            },
            "ai_insights": ai_insights,
            "competitive_analysis": competitive_analysis,
            "executive_summary": executive_summary,
            "recommendations": recommendations,
            "analysis_metadata": {
                "version": "2.0_enhanced",
                "data_sources": ["LogicMill API", "Google AI API", "OpenAlex", "Market Analysis"],
                "google_ai_available": GOOGLE_AI_AVAILABLE,
                "total_analysis_points": len(similar_documents) + len(recommendations)
            }
        }
        
        # Add similar patents and publications to root level for compatibility
        enhanced_report["similar_patents"] = similar_patents
        enhanced_report["similar_publications"] = similar_publications
        
        if debug:
            print("[ENHANCED] Comprehensive analysis completed successfully")
        
        return enhanced_report
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {str(e)}")
        if debug:
            print(f"[ENHANCED] Error: {str(e)}")
        
        # Fallback to basic analysis
        try:
            basic_result = analyze_research_potential(title, abstract, debug=debug)
            basic_result["error"] = f"Enhanced analysis failed: {str(e)}"
            basic_result["fallback_mode"] = True
            return basic_result
        except Exception as fallback_error:
            return {
                "error": f"All analysis methods failed: {str(fallback_error)}",
                "overall_assessment": {"market_potential_score": 0},
                "trl_assessment": {"trl_score": 0},
                "market_analysis": {"tam_billion_usd": 0},
                "recommendations": ["Analysis temporarily unavailable", "Please try again later"]
            }

def generate_ai_insights(title: str, abstract: str, similar_documents: List[Dict], debug: bool = False) -> Dict[str, Any]:
    """Generate AI-powered insights using Google AI."""
    if not GOOGLE_AI_AVAILABLE:
        return {
            "novelty_assessment": "Google AI API not available - check configuration",
            "technical_analysis": "Google AI API not available - check configuration",
            "patent_landscape_analysis": "Google AI API not available - check configuration",
            "innovation_potential": "Google AI API not available - check configuration"
        }
    
    try:
        research_text = f"Title: {title}\n\nAbstract: {abstract}"
        
        # Build context from similar documents
        similar_context = build_similarity_context(similar_documents[:10])
        
        # Generate novelty assessment
        novelty_prompt = f"""
        As a patent examiner with 15+ years of experience, assess the novelty of this research:
        
        {research_text}
        
        Based on these similar existing patents and publications:
        {similar_context}
        
        Provide a comprehensive novelty assessment including:
        1. Key innovative elements that differentiate this research
        2. Potential prior art concerns and conflicts
        3. Novelty score (1-10) with detailed justification
        4. Recommendations for strengthening patent applications
        """
        
        novelty_assessment = get_google_ai_response(novelty_prompt, max_tokens=1500)
        
        # Generate technical innovation analysis
        technical_analysis = get_technical_innovation_analysis(research_text)
        
        # Generate patent landscape analysis
        landscape_prompt = f"""
        As a technology intelligence analyst, analyze the patent landscape for this research:
        
        {research_text}
        
        Considering these existing patents and publications:
        {similar_context}
        
        Provide:
        1. Patent landscape density and competition level
        2. White space opportunities for innovation
        3. Key players and technology trends
        4. Strategic IP positioning recommendations
        """
        
        landscape_analysis = get_google_ai_response(landscape_prompt, max_tokens=1500)
        
        # Generate innovation potential assessment
        innovation_prompt = f"""
        As an innovation strategist, evaluate the commercial and technical potential:
        
        {research_text}
        
        Market context from similar technologies:
        {similar_context}
        
        Assess:
        1. Innovation potential score (1-10)
        2. Market disruption potential
        3. Technology adoption barriers
        4. Commercialization timeline and strategy
        """
        
        innovation_potential = get_google_ai_response(innovation_prompt, max_tokens=1200)
        
        return {
            "novelty_assessment": novelty_assessment,
            "technical_analysis": technical_analysis,
            "patent_landscape_analysis": landscape_analysis,
            "innovation_potential": innovation_potential
        }
        
    except Exception as e:
        logger.error(f"AI insights generation failed: {str(e)}")
        return {
            "novelty_assessment": f"Error generating AI insights: {str(e)}",
            "technical_analysis": f"Error generating AI insights: {str(e)}",
            "patent_landscape_analysis": f"Error generating AI insights: {str(e)}",
            "innovation_potential": f"Error generating AI insights: {str(e)}"
        }

def build_similarity_context(similar_documents: List[Dict]) -> str:
    """Build context string from similar documents."""
    if not similar_documents:
        return "No similar documents found."
    
    context_parts = []
    for i, doc in enumerate(similar_documents[:8], 1):  # Top 8 most similar
        title = doc.get("title", "Unknown Title")
        score = doc.get("score", 0)
        doc_type = doc.get("index", "unknown")
        url = doc.get("url", "")
        
        context_parts.append(
            f"{i}. {title}\n"
            f"   Type: {doc_type.title()}\n"
            f"   Similarity: {score:.3f}\n"
            f"   URL: {url}\n"
        )
    
    return "\n".join(context_parts)

def analyze_competitive_landscape(patents: List[Dict], publications: List[Dict], debug: bool = False) -> Dict[str, Any]:
    """Analyze competitive landscape from patent and publication data."""
    total_documents = len(patents) + len(publications)
    
    # Calculate competitive metrics
    high_similarity_patents = len([p for p in patents if p.get("score", 0) > 0.8])
    recent_patents = len([p for p in patents if p.get("year", 2000) >= 2020])
    
    # Determine competitive intensity
    if total_documents > 100:
        intensity = "Very High"
        intensity_score = 9
    elif total_documents > 50:
        intensity = "High"
        intensity_score = 7
    elif total_documents > 20:
        intensity = "Medium"
        intensity_score = 5
    else:
        intensity = "Low"
        intensity_score = 3
    
    # Assess market position
    if high_similarity_patents > 10:
        position = "Crowded - High Competition"
    elif high_similarity_patents > 5:
        position = "Competitive - Moderate Competition"
    elif high_similarity_patents > 0:
        position = "Emerging - Some Competition"
    else:
        position = "Open - Low Competition"
    
    return {
        "competitive_intensity": intensity,
        "intensity_score": intensity_score,
        "market_position": position,
        "total_competing_documents": total_documents,
        "high_similarity_patents": high_similarity_patents,
        "recent_patent_activity": recent_patents,
        "patent_to_publication_ratio": len(patents) / max(1, len(publications)),
        "competitive_threat_level": "High" if high_similarity_patents > 5 else "Medium" if high_similarity_patents > 2 else "Low"
    }

def analyze_similarity_scores(documents: List[Dict]) -> Dict[str, Any]:
    """Analyze distribution of similarity scores."""
    if not documents:
        return {"error": "No documents to analyze"}
    
    scores = [doc.get("score", 0) for doc in documents if doc.get("score")]
    
    if not scores:
        return {"error": "No similarity scores found"}
    
    return {
        "average_similarity": round(sum(scores) / len(scores), 3),
        "max_similarity": round(max(scores), 3),
        "min_similarity": round(min(scores), 3),
        "very_high_similarity": len([s for s in scores if s > 0.9]),
        "high_similarity": len([s for s in scores if 0.8 < s <= 0.9]),
        "medium_similarity": len([s for s in scores if 0.6 < s <= 0.8]),
        "low_similarity": len([s for s in scores if s <= 0.6]),
        "similarity_trend": "concerning" if max(scores) > 0.9 else "competitive" if max(scores) > 0.8 else "favorable"
    }

def generate_executive_summary(basic_analysis: Dict, similar_documents: List[Dict], ai_insights: Dict, debug: bool = False) -> Dict[str, Any]:
    """Generate executive summary combining all analysis results."""
    try:
        # Extract key metrics
        market_potential = basic_analysis.get("overall_assessment", {}).get("market_potential_score", 0)
        trl_score = basic_analysis.get("trl_assessment", {}).get("trl_score", 0)
        total_similar = len(similar_documents)
        
        # Calculate opportunity score
        patent_density_factor = max(0, 10 - (total_similar / 10))  # Lower is better
        opportunity_score = (market_potential * 0.4 + trl_score * 1.1 + patent_density_factor * 0.5) / 2
        opportunity_score = min(10, max(0, opportunity_score))
        
        # Assess overall risk
        risk_factors = 0
        if total_similar > 50: risk_factors += 2
        if trl_score < 4: risk_factors += 1
        if market_potential < 5: risk_factors += 1
        
        risk_level = "High" if risk_factors >= 3 else "Medium" if risk_factors >= 2 else "Low"
        
        # Generate AI summary if available
        if GOOGLE_AI_AVAILABLE and ai_insights.get("novelty_assessment"):
            summary_prompt = f"""
            Create a concise 3-paragraph executive summary for this research analysis:
            
            Key Metrics:
            - Market Potential: {market_potential}/10
            - Technology Readiness: {trl_score}/9
            - Similar Documents Found: {total_similar}
            - Opportunity Score: {opportunity_score:.1f}/10
            - Risk Level: {risk_level}
            
            Focus on:
            1. Technology innovation and market opportunity
            2. Competitive landscape and positioning
            3. Key recommendations and strategic next steps
            """
            
            ai_summary = get_google_ai_response(summary_prompt, max_tokens=600)
        else:
            ai_summary = f"This research shows {market_potential}/10 market potential with TRL {trl_score}/9. Found {total_similar} similar documents indicating {'high' if total_similar > 50 else 'moderate' if total_similar > 20 else 'low'} competition. Overall opportunity score: {opportunity_score:.1f}/10."
        
        return {
            "opportunity_score": round(opportunity_score, 1),
            "risk_assessment": risk_level,
            "market_potential_score": market_potential,
            "technology_readiness": trl_score,
            "competitive_density": total_similar,
            "ai_generated_summary": ai_summary,
            "key_insights": [
                f"Market potential rated {market_potential}/10",
                f"Technology at TRL {trl_score}/9",
                f"{total_similar} similar documents found",
                f"Overall risk level: {risk_level}"
            ]
        }
        
    except Exception as e:
        logger.error(f"Executive summary generation failed: {str(e)}")
        return {
            "opportunity_score": 5.0,
            "risk_assessment": "Unknown",
            "ai_generated_summary": f"Summary generation failed: {str(e)}",
            "key_insights": ["Analysis completed with limited insights"]
        }

def generate_smart_recommendations(basic_analysis: Dict, similar_documents: List[Dict], ai_insights: Dict, debug: bool = False) -> List[str]:
    """Generate actionable recommendations based on comprehensive analysis."""
    recommendations = []
    
    try:
        # Extract key metrics
        trl_score = basic_analysis.get("trl_assessment", {}).get("trl_score", 0)
        market_potential = basic_analysis.get("overall_assessment", {}).get("market_potential_score", 0)
        patent_count = len([d for d in similar_documents if d.get("index") == "patents"])
        high_similarity_count = len([d for d in similar_documents if d.get("score", 0) > 0.8])
        
        # TRL-based recommendations
        if trl_score <= 3:
            recommendations.extend([
                "Focus on proof-of-concept development and validation",
                "Seek research funding and academic partnerships",
                "Conduct detailed feasibility studies"
            ])
        elif trl_score <= 6:
            recommendations.extend([
                "Develop working prototype and conduct pilot testing",
                "File provisional patent applications to secure IP",
                "Validate market demand through customer interviews"
            ])
        else:
            recommendations.extend([
                "Prepare for commercialization and scale-up",
                "Develop comprehensive go-to-market strategy",
                "Secure strategic partnerships for market entry"
            ])
        
        # Market potential recommendations
        if market_potential > 7:
            recommendations.append("High market potential - prioritize rapid development and funding")
        elif market_potential > 4:
            recommendations.append("Moderate market potential - validate business model thoroughly")
        else:
            recommendations.append("Consider market pivot or niche focus for better positioning")
        
        # Patent landscape recommendations
        if patent_count > 50:
            recommendations.extend([
                "Crowded patent landscape - conduct detailed freedom-to-operate analysis",
                "Consider design-around strategies or licensing agreements"
            ])
        elif patent_count > 20:
            recommendations.append("Active patent area - file strategic patents to build IP portfolio")
        else:
            recommendations.append("Open patent landscape - opportunity for strong IP position")
        
        # High similarity recommendations
        if high_similarity_count > 5:
            recommendations.extend([
                "Multiple highly similar technologies found - differentiate clearly",
                "Consider collaboration or acquisition opportunities"
            ])
        
        # AI-generated recommendations
        if GOOGLE_AI_AVAILABLE and ai_insights.get("innovation_potential"):
            rec_prompt = f"""
            Based on this innovation analysis, provide 3 specific, actionable recommendations:
            
            {ai_insights.get('innovation_potential', '')[:800]}
            
            Focus on immediate next steps for:
            1. Technology development
            2. Market strategy
            3. IP protection
            """
            
            try:
                ai_recommendations = get_google_ai_response(rec_prompt, max_tokens=400)
                if ai_recommendations and "Error:" not in ai_recommendations:
                    # Extract recommendations from AI response
                    ai_rec_lines = [line.strip() for line in ai_recommendations.split('\n') 
                                  if line.strip() and any(char.isalpha() for char in line)]
                    recommendations.extend(ai_rec_lines[:3])
            except Exception as e:
                if debug:
                    print(f"[ENHANCED] AI recommendations failed: {e}")
        
        # Limit and clean recommendations
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations and len(rec) > 10:
                unique_recommendations.append(rec)
        
        return unique_recommendations[:12]  # Limit to 12 recommendations
        
    except Exception as e:
        logger.error(f"Recommendations generation failed: {str(e)}")
        return [
            "Conduct detailed market research and validation",
            "Develop comprehensive IP strategy",
            "Validate technology feasibility and scalability",
            "Build strategic partnerships for market entry"
        ]

# Utility function to convert numpy types for JSON serialization
def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    import numpy as np
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj