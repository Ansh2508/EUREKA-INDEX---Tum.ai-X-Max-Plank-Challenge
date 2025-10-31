import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
from dataclasses import dataclass
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

from src.services.logic_mill import search_similar_patents_publications
from src.services.openalex import fetch_publication_metadata
from src.services.espacenet import fetch_patent_metadata

@dataclass
class NoveltyAssessment:
    overall_novelty_score: float
    novelty_category: str  # 'Highly Novel', 'Moderately Novel', 'Incremental', 'Not Novel'
    similar_patents: List[Dict]
    similar_publications: List[Dict]
    key_differences: List[str]
    patentability_indicators: Dict[str, Any]
    prior_art_analysis: Dict[str, Any]
    recommendations: List[str]

class EnhancedNoveltyAssessment:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.novelty_threshold = 0.85
        
    async def assess_novelty(
        self,
        research_title: str,
        research_abstract: str,
        claims: List[str],
        existing_patents: List[Dict],
        existing_publications: List[Dict]
    ) -> NoveltyAssessment:
        """
        Compare claims of existing patents and scientific publications to research
        """
        # Create embeddings for the research
        research_text = f"{research_title}. {research_abstract}"
        research_claims_text = " ".join(claims)
        full_research_text = f"{research_text} {research_claims_text}"
        
        research_embedding = self.model.encode([full_research_text])
        
        # Analyze similarity to existing patents
        patent_similarities = await self._analyze_patent_similarities(
            research_embedding, full_research_text, existing_patents
        )
        
        # Analyze similarity to existing publications
        publication_similarities = await self._analyze_publication_similarities(
            research_embedding, full_research_text, existing_publications
        )
        
        # Calculate overall novelty score
        overall_novelty = self._calculate_novelty_score(
            patent_similarities, publication_similarities
        )
        
        # Identify key differences
        key_differences = await self._identify_key_differences(
            full_research_text, patent_similarities + publication_similarities
        )
        
        # Assess patentability
        patentability = self._assess_patentability(
            claims, patent_similarities, overall_novelty
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_novelty, patentability, patent_similarities
        )
        
        return NoveltyAssessment(
            overall_novelty_score=overall_novelty,
            novelty_category=self._categorize_novelty(overall_novelty),
            similar_patents=patent_similarities[:10],
            similar_publications=publication_similarities[:10],
            key_differences=key_differences,
            patentability_indicators=patentability,
            prior_art_analysis=self._analyze_prior_art(patent_similarities, publication_similarities),
            recommendations=recommendations
        )
    
    async def _analyze_patent_similarities(
        self,
        research_embedding: np.ndarray,
        research_text: str,
        patents: List[Dict]
    ) -> List[Dict]:
        """Analyze similarities with existing patents"""
        similarities = []
        
        for patent in patents:
            patent_text = f"{patent.get('title', '')}. {patent.get('abstract', '')}"
            if patent.get('claims'):
                patent_text += f" Claims: {' '.join(patent['claims'])}"
            
            if not patent_text.strip():
                continue
                
            patent_embedding = self.model.encode([patent_text])
            similarity = cosine_similarity(research_embedding, patent_embedding)[0][0]
            
            similarity_data = {
                'id': patent.get('id'),
                'title': patent.get('title', ''),
                'similarity_score': float(similarity),
                'publication_date': patent.get('publication_date', ''),
                'assignee': patent.get('assignee', ''),
                'abstract': patent.get('abstract', ''),
                'claims': patent.get('claims', []),
                'document_type': 'patent',
                'overlap_analysis': self._analyze_text_overlap(research_text, patent_text)
            }
            similarities.append(similarity_data)
        
        return sorted(similarities, key=lambda x: x['similarity_score'], reverse=True)
    
    async def _analyze_publication_similarities(
        self,
        research_embedding: np.ndarray,
        research_text: str,
        publications: List[Dict]
    ) -> List[Dict]:
        """Analyze similarities with existing publications"""
        similarities = []
        
        for pub in publications:
            pub_text = f"{pub.get('title', '')}. {pub.get('abstract', '')}"
            
            if not pub_text.strip():
                continue
                
            pub_embedding = self.model.encode([pub_text])
            similarity = cosine_similarity(research_embedding, pub_embedding)[0][0]
            
            similarity_data = {
                'id': pub.get('id'),
                'title': pub.get('title', ''),
                'similarity_score': float(similarity),
                'publication_date': pub.get('publication_date', ''),
                'authors': pub.get('authors', []),
                'abstract': pub.get('abstract', ''),
                'document_type': 'publication',
                'overlap_analysis': self._analyze_text_overlap(research_text, pub_text)
            }
            similarities.append(similarity_data)
        
        return sorted(similarities, key=lambda x: x['similarity_score'], reverse=True)
    
    def _calculate_novelty_score(
        self,
        patent_similarities: List[Dict],
        publication_similarities: List[Dict]
    ) -> float:
        """Calculate overall novelty score"""
        if not patent_similarities and not publication_similarities:
            return 1.0  # Completely novel if no similar documents found
        
        # Get highest similarity scores
        max_patent_sim = max([p['similarity_score'] for p in patent_similarities], default=0)
        max_pub_sim = max([p['similarity_score'] for p in publication_similarities], default=0)
        
        # Weight patents more heavily than publications for novelty assessment
        weighted_similarity = (max_patent_sim * 0.7) + (max_pub_sim * 0.3)
        
        # Convert similarity to novelty (inverse relationship)
        novelty_score = 1.0 - weighted_similarity
        
        return max(0.0, min(1.0, novelty_score))
    
    async def _identify_key_differences(
        self,
        research_text: str,
        similar_documents: List[Dict]
    ) -> List[str]:
        """Identify key differences between research and similar documents"""
        differences = []
        
        # Extract key terms from research
        research_terms = self._extract_key_terms(research_text)
        
        for doc in similar_documents[:5]:  # Analyze top 5 most similar
            doc_text = f"{doc.get('title', '')}. {doc.get('abstract', '')}"
            doc_terms = self._extract_key_terms(doc_text)
            
            # Find terms unique to research
            unique_terms = research_terms - doc_terms
            if unique_terms:
                differences.append(f"Novel aspects vs {doc.get('title', 'document')}: {', '.join(list(unique_terms)[:5])}")
        
        return differences[:10]
    
    def _extract_key_terms(self, text: str) -> set:
        """Extract key technical terms from text"""
        # Simple term extraction - could be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter out common words
        common_words = {'that', 'this', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'would', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'some', 'these', 'many', 'then', 'them', 'well', 'were'}
        return set(word for word in words if word not in common_words and len(word) > 4)
    
    def _analyze_text_overlap(self, text1: str, text2: str) -> Dict[str, Any]:
        """Analyze textual overlap between two documents"""
        terms1 = self._extract_key_terms(text1)
        terms2 = self._extract_key_terms(text2)
        
        overlap = terms1.intersection(terms2)
        overlap_ratio = len(overlap) / max(len(terms1), 1)
        
        return {
            'overlapping_terms': list(overlap)[:10],
            'overlap_ratio': overlap_ratio,
            'unique_to_research': list(terms1 - terms2)[:10]
        }
    
    def _assess_patentability(
        self,
        claims: List[str],
        patent_similarities: List[Dict],
        novelty_score: float
    ) -> Dict[str, Any]:
        """Assess patentability indicators"""
        return {
            'novelty_score': novelty_score,
            'has_technical_merit': len(claims) > 0,
            'prior_art_conflicts': len([p for p in patent_similarities if p['similarity_score'] > 0.8]),
            'patentability_likelihood': 'High' if novelty_score > 0.7 else 'Medium' if novelty_score > 0.4 else 'Low',
            'recommended_claim_focus': self._suggest_claim_focus(claims, patent_similarities)
        }
    
    def _suggest_claim_focus(self, claims: List[str], similar_patents: List[Dict]) -> List[str]:
        """Suggest areas to focus claims on based on prior art"""
        suggestions = []
        
        if not similar_patents:
            suggestions.append("Focus on core technical innovation")
        else:
            suggestions.append("Emphasize novel technical aspects not covered in prior art")
            suggestions.append("Consider narrower claims to avoid prior art conflicts")
        
        return suggestions
    
    def _categorize_novelty(self, score: float) -> str:
        """Categorize novelty score into human-readable categories"""
        if score >= 0.8:
            return 'Highly Novel'
        elif score >= 0.6:
            return 'Moderately Novel'
        elif score >= 0.3:
            return 'Incremental'
        else:
            return 'Not Novel'
    
    def _analyze_prior_art(
        self,
        patent_similarities: List[Dict],
        publication_similarities: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze prior art landscape"""
        return {
            'total_similar_patents': len(patent_similarities),
            'total_similar_publications': len(publication_similarities),
            'highest_patent_similarity': max([p['similarity_score'] for p in patent_similarities], default=0),
            'highest_publication_similarity': max([p['similarity_score'] for p in publication_similarities], default=0),
            'key_prior_art': (patent_similarities + publication_similarities)[:5]
        }
    
    def _generate_recommendations(
        self,
        novelty_score: float,
        patentability: Dict[str, Any],
        similar_patents: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if novelty_score > 0.7:
            recommendations.append("Strong novelty detected - proceed with patent application")
        elif novelty_score > 0.4:
            recommendations.append("Moderate novelty - consider focusing on specific novel aspects")
        else:
            recommendations.append("Low novelty - significant prior art exists, reconsider patenting strategy")
        
        if patentability['prior_art_conflicts'] > 0:
            recommendations.append("Review similar patents for potential claim conflicts")
        
        recommendations.append("Conduct professional prior art search before filing")
        
        return recommendations