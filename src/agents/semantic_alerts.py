import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.services.logic_mill import search_similar_patents_publications
from src.services.openalex import fetch_publication_metadata
from src.services.espacenet import fetch_patent_metadata

@dataclass
class AlertResult:
    id: str
    title: str
    similarity_score: float
    document_type: str  # 'patent' or 'publication'
    publication_date: str
    authors: List[str]
    institutions: List[str]
    abstract: str
    url: str
    alert_reason: str

class SemanticPatentAlerts:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.75
        self.logger = logging.getLogger(__name__)
        
    async def detect_similar_patents(
        self, 
        research_abstract: str, 
        research_title: str,
        similarity_threshold: float = 0.75,
        lookback_days: int = 30
    ) -> List[AlertResult]:
        """
        Detect patents semantically similar to research results using embeddings
        """
        # Get embeddings for the input research
        query_embedding = self.model.encode([f"{research_title}. {research_abstract}"])
        
        # Search for similar documents
        similar_docs = search_similar_patents_publications(
            f"{research_title}. {research_abstract}"
        )
        
        alerts = []
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        for doc in similar_docs:
            try:
                # Calculate semantic similarity
                doc_text = f"{doc.get('title', '')}. {doc.get('abstract', '')}"
                doc_embedding = self.model.encode([doc_text])
                
                similarity = cosine_similarity(query_embedding, doc_embedding)[0][0]
                
                if similarity >= similarity_threshold:
                    # Check if document is recent enough
                    pub_date = self._parse_date(doc.get('publication_date'))
                    if pub_date and pub_date >= cutoff_date:
                        alert = AlertResult(
                            id=doc.get('id'),
                            title=doc.get('title', ''),
                            similarity_score=float(similarity),
                            document_type=doc.get('type', 'unknown'),
                            publication_date=doc.get('publication_date', ''),
                            authors=doc.get('authors', []),
                            institutions=doc.get('institutions', []),
                            abstract=doc.get('abstract', ''),
                            url=doc.get('url', ''),
                            alert_reason=f"High semantic similarity ({similarity:.3f}) to research"
                        )
                        alerts.append(alert)
                        
            except Exception as e:
                self.logger.error(f"Error processing document {doc.get('id')}: {e}")
                continue
                
        return sorted(alerts, key=lambda x: x.similarity_score, reverse=True)
    
    async def monitor_competitive_landscape(
        self,
        research_domain: str,
        competitor_entities: List[str],
        alert_threshold: float = 0.8
    ) -> List[AlertResult]:
        """
        Monitor competitive landscape for new patents from competitors
        """
        alerts = []
        
        for entity in competitor_entities:
            try:
                # Search for recent patents from this entity
                entity_patents = await self._search_entity_patents(entity)
                
                for patent in entity_patents:
                    # Calculate relevance to research domain
                    relevance = await self._calculate_domain_relevance(
                        patent, research_domain
                    )
                    
                    if relevance >= alert_threshold:
                        alert = AlertResult(
                            id=patent.get('id'),
                            title=patent.get('title'),
                            similarity_score=relevance,
                            document_type='patent',
                            publication_date=patent.get('publication_date'),
                            authors=patent.get('inventors', []),
                            institutions=[entity],
                            abstract=patent.get('abstract', ''),
                            url=patent.get('url', ''),
                            alert_reason=f"Competitive patent from {entity}"
                        )
                        alerts.append(alert)
                        
            except Exception as e:
                self.logger.error(f"Error monitoring {entity}: {e}")
                continue
                
        return alerts
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
            
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
            
        return None
    
    async def _search_entity_patents(self, entity: str) -> List[Dict]:
        """Search for patents from a specific entity"""
        # This would integrate with patent databases
        # For now, return mock data structure
        return []
    
    async def _calculate_domain_relevance(
        self, 
        patent: Dict, 
        domain: str
    ) -> float:
        """Calculate how relevant a patent is to a research domain"""
        patent_text = f"{patent.get('title', '')}. {patent.get('abstract', '')}"
        
        patent_embedding = self.model.encode([patent_text])
        domain_embedding = self.model.encode([domain])
        
        return cosine_similarity(patent_embedding, domain_embedding)[0][0] 