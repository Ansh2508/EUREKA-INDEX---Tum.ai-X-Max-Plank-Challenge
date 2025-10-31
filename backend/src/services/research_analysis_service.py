"""
Research Analysis Service - Enhanced with LogicMill and Google AI Integration
Provides comprehensive research analysis functionality combining multiple AI services.
"""

from typing import Dict, List, Any, Optional
from src.search_logic_mill import search_logic_mill
from src.analysis import analyze_research_potential
import logging
import json
import numpy as np

# Import Google AI functions with error handling
try:
    from src.llms.google_ai import (
        get_patent_analysis, 
        get_technical_innovation_analysis, 
        get_prior_art_search_strategy,
        get_google_ai_response
    )
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    GOOGLE_AI_AVAILABLE = False
    logging.warning(f"Google AI not available: {e}")

logger = logging.getLogger(__name__)

class ResearchAnalysisService:
    """Service for analyzing research potential and patent similarities."""
    
    def __init__(self):
        self.debug = False
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        return obj
    
    def analyze_research(
        self, 
        title: str, 
        abstract: str, 
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze research potential using existing analysis logic.
        
        Args:
            title: Research title
            abstract: Research abstract
            debug: Enable debug mode
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            self.debug = debug
            if debug:
                logger.info(f"Starting research analysis for: {title[:50]}...")
            
            # Use existing analysis function
            result = analyze_research_potential(title, abstract, debug=debug)
            
            # Convert numpy types to native Python types for JSON serialization
            result = self._convert_numpy_types(result)
            
            if debug:
                logger.info("Research analysis completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in research analysis: {str(e)}")
            raise
    
    def search_similar_patents(
        self, 
        title: str, 
        abstract: str, 
        amount: int = 25,
        debug: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for similar patents using Logic Mill API.
        
        Args:
            title: Research title
            abstract: Research abstract
            amount: Number of results to return
            debug: Enable debug mode
            
        Returns:
            List of similar patents/publications
        """
        try:
            if debug:
                logger.info(f"Searching for similar patents: {amount} results")
            
            # Use existing search logic
            results = search_logic_mill(
                title=title,
                abstract=abstract,
                amount=amount,
                indices=["patents", "publications"],
                debug=debug
            )
            
            if debug:
                logger.info(f"Found {len(results)} similar documents")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar patents: {str(e)}")
            raise
    
    def get_analysis_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get analysis history for a user (placeholder for future implementation).
        
        Args:
            user_id: User identifier
            
        Returns:
            List of previous analyses
        """
        # Placeholder - would integrate with database in full implementation
        return []
    
    def validate_research_input(self, title: str, abstract: str) -> Dict[str, Any]:
        """
        Validate research input parameters.
        
        Args:
            title: Research title
            abstract: Research abstract
            
        Returns:
            Validation result with errors if any
        """
        errors = []
        
        if not title or len(title.strip()) < 5:
            errors.append("Title must be at least 5 characters long")
        
        if not abstract or len(abstract.strip()) < 20:
            errors.append("Abstract must be at least 20 characters long")
        
        if len(title) > 500:
            errors.append("Title must be less than 500 characters")
        
        if len(abstract) > 5000:
            errors.append("Abstract must be less than 5000 characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }