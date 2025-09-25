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

from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
import networkx as nx
from dataclasses import dataclass
import pandas as pd

from src.services.openalex import fetch_publication_metadata
from src.search_logic_mill import search_logic_mill

@dataclass
class EntityProfile:
    name: str
    entity_type: str  # 'author', 'institution', 'company'
    publication_count: int
    patent_count: int
    collaboration_score: float
    recent_activity: int
    key_topics: List[str]
    geographic_location: str
    contact_info: Dict[str, str]

class CompetitorCollaboratorDiscovery:
    def __init__(self):
        self.collaboration_graph = nx.Graph()
        
    async def identify_key_players(
        self, 
        research_title: str, 
        research_abstract: str,
        domain_focus: str = None
    ) -> Dict[str, List[EntityProfile]]:
        """
        Identify top authors, inventors, and institutions in the domain
        """
        # Get related publications and patents
        similar_docs = search_logic_mill(
            research_title, 
            research_abstract, 
            amount=100,
            indices=["patents", "publications"]
        )
        
        # Analyze authors and institutions
        authors = defaultdict(lambda: {
            'publications': [], 'patents': [], 'institutions': set(),
            'topics': [], 'collaborations': set()
        })
        
        institutions = defaultdict(lambda: {
            'publications': [], 'patents': [], 'authors': set(),
            'topics': [], 'locations': set()
        })
        
        for doc in similar_docs:
            doc_authors = doc.get('authors', [])
            doc_institutions = doc.get('institutions', [])
            doc_topics = doc.get('topics', [])
            doc_type = doc.get('index', 'unknown')
            
            # Process authors
            for author in doc_authors:
                author_name = author if isinstance(author, str) else author.get('display_name', '')
                if author_name:
                    if doc_type == 'publications':
                        authors[author_name]['publications'].append(doc)
                    else:
                        authors[author_name]['patents'].append(doc)
                    
                    authors[author_name]['topics'].extend(doc_topics)
                    authors[author_name]['institutions'].update(doc_institutions)
                    
                    # Track collaborations
                    for other_author in doc_authors:
                        other_name = other_author if isinstance(other_author, str) else other_author.get('display_name', '')
                        if other_name != author_name:
                            authors[author_name]['collaborations'].add(other_name)
            
            # Process institutions
            for institution in doc_institutions:
                inst_name = institution if isinstance(institution, str) else institution.get('display_name', '')
                if inst_name:
                    if doc_type == 'publications':
                        institutions[inst_name]['publications'].append(doc)
                    else:
                        institutions[inst_name]['patents'].append(doc)
                    
                    institutions[inst_name]['topics'].extend(doc_topics)
                    institutions[inst_name]['authors'].update(doc_authors)
        
        # Create entity profiles
        top_authors = self._create_author_profiles(authors)
        top_institutions = self._create_institution_profiles(institutions)
        
        return {
            'top_authors': top_authors,
            'top_institutions': top_institutions,
            'collaboration_clusters': self._identify_collaboration_clusters(authors)
        }
    
    def _create_author_profiles(self, authors_data: Dict) -> List[EntityProfile]:
        """Create profiles for top authors"""
        profiles = []
        
        for author_name, data in authors_data.items():
            pub_count = len(data['publications'])
            patent_count = len(data['patents'])
            
            if pub_count + patent_count < 2:  # Filter out low-activity authors
                continue
                
            # Calculate collaboration score
            collaboration_score = len(data['collaborations']) / max(1, pub_count + patent_count)
            
            # Get most common topics
            topic_counts = Counter(data['topics'])
            key_topics = [topic for topic, count in topic_counts.most_common(5)]
            
            # Calculate recent activity (last 2 years)
            recent_activity = self._count_recent_activity(
                data['publications'] + data['patents']
            )
            
            profile = EntityProfile(
                name=author_name,
                entity_type='author',
                publication_count=pub_count,
                patent_count=patent_count,
                collaboration_score=collaboration_score,
                recent_activity=recent_activity,
                key_topics=key_topics,
                geographic_location='Unknown',  # Would need additional API calls
                contact_info={}
            )
            profiles.append(profile)
        
        return sorted(profiles, key=lambda x: x.publication_count + x.patent_count, reverse=True)[:50]
    
    def _create_institution_profiles(self, institutions_data: Dict) -> List[EntityProfile]:
        """Create profiles for top institutions"""
        profiles = []
        
        for inst_name, data in institutions_data.items():
            pub_count = len(data['publications'])
            patent_count = len(data['patents'])
            
            if pub_count + patent_count < 3:  # Filter out low-activity institutions
                continue
            
            # Calculate collaboration score based on author diversity
            collaboration_score = len(data['authors']) / max(1, pub_count + patent_count)
            
            # Get most common topics
            topic_counts = Counter(data['topics'])
            key_topics = [topic for topic, count in topic_counts.most_common(5)]
            
            # Calculate recent activity
            recent_activity = self._count_recent_activity(
                data['publications'] + data['patents']
            )
            
            profile = EntityProfile(
                name=inst_name,
                entity_type='institution',
                publication_count=pub_count,
                patent_count=patent_count,
                collaboration_score=collaboration_score,
                recent_activity=recent_activity,
                key_topics=key_topics,
                geographic_location='Unknown',
                contact_info={}
            )
            profiles.append(profile)
        
        return sorted(profiles, key=lambda x: x.publication_count + x.patent_count, reverse=True)[:30]
    
    def _identify_collaboration_clusters(self, authors_data: Dict) -> List[Dict]:
        """Identify clusters of collaborating researchers"""
        # Build collaboration graph
        G = nx.Graph()
        
        for author, data in authors_data.items():
            for collaborator in data['collaborations']:
                if collaborator in authors_data:  # Only include authors we have data for
                    G.add_edge(author, collaborator)
        
        # Find communities/clusters
        clusters = []
        try:
            communities = nx.community.greedy_modularity_communities(G)
            
            for i, community in enumerate(communities):
                if len(community) >= 3:  # Only include substantial clusters
                    cluster_info = {
                        'cluster_id': i,
                        'members': list(community),
                        'size': len(community),
                        'internal_connections': G.subgraph(community).number_of_edges(),
                        'key_topics': self._get_cluster_topics(community, authors_data)
                    }
                    clusters.append(cluster_info)
                    
        except Exception as e:
            print(f"Error in community detection: {e}")
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)[:10]
    
    def _count_recent_activity(self, documents: List[Dict]) -> int:
        """Count recent publications/patents (last 2 years)"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=730)  # 2 years
        recent_count = 0
        
        for doc in documents:
            pub_date_str = doc.get('publication_date', '')
            if pub_date_str:
                try:
                    pub_date = datetime.strptime(pub_date_str[:4], '%Y')
                    if pub_date >= cutoff_date:
                        recent_count += 1
                except:
                    continue
                    
        return recent_count
    
    def _get_cluster_topics(self, community: set, authors_data: Dict) -> List[str]:
        """Get most common topics for a collaboration cluster"""
        all_topics = []
        for author in community:
            if author in authors_data:
                all_topics.extend(authors_data[author]['topics'])
        
        topic_counts = Counter(all_topics)
        return [topic for topic, count in topic_counts.most_common(5)]

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class LicensingOpportunity:
    entity_name: str
    entity_type: str  # 'company', 'university', 'research_institute'
    opportunity_type: str  # 'licensing_in', 'licensing_out', 'collaboration'
    relevance_score: float
    patent_portfolio: List[Dict]
    technology_gaps: List[str]
    contact_information: Dict[str, str]
    market_position: str
    licensing_history: List[Dict]
    estimated_value: Optional[str]

class LicensingOpportunityMapper:
    def __init__(self):
        self.opportunity_threshold = 0.7
        
    async def identify_licensing_opportunities(
        self,
        focal_research_group: str,
        research_domain: str,
        patent_portfolio: List[Dict],
        publication_portfolio: List[Dict]
    ) -> List[LicensingOpportunity]:
        """
        Flag entities that may need licenses from the focal research group
        """
        opportunities = []
        
        # Analyze patent landscape to find potential licensees
        potential_licensees = await self._find_potential_licensees(
            focal_research_group, patent_portfolio, research_domain
        )
        
        # Analyze technology gaps that could be filled by licensing
        gap_opportunities = await self._identify_technology_gaps(
            research_domain, patent_portfolio, publication_portfolio
        )
        
        # Combine and rank opportunities
        all_opportunities = potential_licensees + gap_opportunities
        
        return sorted(all_opportunities, key=lambda x: x.relevance_score, reverse=True)
    
    async def _find_potential_licensees(
        self,
        focal_group: str,
        patents: List[Dict],
        domain: str
    ) -> List[LicensingOpportunity]:
        """Find entities that might need licenses for focal group's patents"""
        opportunities = []
        
        # Analyze patent citations and related work
        for patent in patents:
            citing_patents = await self._get_citing_patents(patent['id'])
            
            for citing_patent in citing_patents:
                owner = citing_patent.get('assignee', '')
                if owner and owner != focal_group:
                    # Check if this represents a licensing opportunity
                    relevance = await self._calculate_licensing_relevance(
                        patent, citing_patent, domain
                    )
                    
                    if relevance >= self.opportunity_threshold:
                        opportunity = LicensingOpportunity(
                            entity_name=owner,
                            entity_type=self._classify_entity_type(owner),
                            opportunity_type='licensing_out',
                            relevance_score=relevance,
                            patent_portfolio=[citing_patent],
                            technology_gaps=[],
                            contact_information={},
                            market_position='Unknown',
                            licensing_history=[],
                            estimated_value=self._estimate_licensing_value(patent, citing_patent)
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    async def _identify_technology_gaps(
        self,
        domain: str,
        patents: List[Dict],
        publications: List[Dict]
    ) -> List[LicensingOpportunity]:
        """Identify technology gaps that represent licensing opportunities"""
        opportunities = []
        
        # Analyze research publications to find commercialization gaps
        for pub in publications:
            # Check if research has been commercialized
            commercialization_potential = await self._assess_commercialization_potential(pub)
            
            if commercialization_potential['score'] > 0.8:
                # Look for companies working in similar areas
                related_companies = await self._find_companies_in_domain(
                    pub.get('topics', [])
                )
                
                for company in related_companies:
                    opportunity = LicensingOpportunity(
                        entity_name=company['name'],
                        entity_type='company',
                        opportunity_type='licensing_out',
                        relevance_score=commercialization_potential['score'],
                        patent_portfolio=[],
                        technology_gaps=commercialization_potential['gaps'],
                        contact_information=company.get('contact', {}),
                        market_position=company.get('market_position', 'Unknown'),
                        licensing_history=[],
                        estimated_value=commercialization_potential['estimated_value']
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    async def _get_citing_patents(self, patent_id: str) -> List[Dict]:
        """Get patents that cite the given patent"""
        # This would integrate with patent databases
        # For now, return mock structure
        return []
    
    async def _calculate_licensing_relevance(
        self,
        base_patent: Dict,
        citing_patent: Dict,
        domain: str
    ) -> float:
        """Calculate how relevant a licensing opportunity is"""
        # Analyze patent similarity, market overlap, etc.
        # For now, return a mock score
        return 0.75
    
    def _classify_entity_type(self, entity_name: str) -> str:
        """Classify entity type based on name patterns"""
        entity_lower = entity_name.lower()
        
        if any(term in entity_lower for term in ['university', 'college', 'institute']):
            return 'university'
        elif any(term in entity_lower for term in ['inc', 'corp', 'ltd', 'llc', 'company']):
            return 'company'
        else:
            return 'research_institute'
    
    def _estimate_licensing_value(self, base_patent: Dict, citing_patent: Dict) -> str:
        """Estimate potential licensing value"""
        # This would use market data, patent strength analysis, etc.
        return "Medium ($100K-$1M)"
    
    async def _assess_commercialization_potential(self, publication: Dict) -> Dict:
        """Assess how ready research is for commercialization"""
        # Analyze TRL indicators, market readiness, etc.
        return {
            'score': 0.85,
            'gaps': ['Manufacturing scale-up', 'Regulatory approval'],
            'estimated_value': 'High ($1M+)'
        }
    
    async def _find_companies_in_domain(self, topics: List[str]) -> List[Dict]:
        """Find companies working in similar technology domains"""
        # This would integrate with company databases
        return [
            {
                'name': 'TechCorp Inc.',
                'market_position': 'Market Leader',
                'contact': {'email': 'licensing@techcorp.com'}
            }
        ]

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

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
            return 1.0
        
        # Get highest similarity scores
        max_patent_sim = max([p['similarity_score'] for p in patent_similarities], default=0)
        max_pub_sim = max([p['similarity_score'] for p in publication_similarities], default=0)
        
        # Weight patents more heavily than publications for novelty
        weighted_similarity = (max_patent_sim * 0.7) + (max_pub_sim * 0.3)
        
        # Convert to novelty score (inverse of similarity)
        novelty_score = 1.0 - weighted_similarity
        
        return max(0.0, min(1.0, novelty_score))
    
    def _categorize_novelty(self, novelty_score: float) -> str:
        """Categorize novelty level"""
        if novelty_score >= 0.8:
            return "Highly Novel"
        elif novelty_score >= 0.6:
            return "Moderately Novel"
        elif novelty_score >= 0.3:
            return "Incremental Innovation"
        else:
            return "Limited Novelty"
    
    async def _identify_key_differences(
        self,
        research_text: str,
        similar_documents: List[Dict]
    ) -> List[str]:
        """Identify key differences between research and similar documents"""
        differences = []
        
        # Extract key technical terms from research
        research_terms = self._extract_technical_terms(research_text)
        
        for doc in similar_documents[:5]:  # Analyze top 5 similar documents
            if doc['document_type'] == 'patent':
                doc_text = f"{doc.get('title', '')} {doc.get('abstract', '')}"
            else:
                doc_text = f"{doc.get('title', '')} {doc.get('abstract', '')}"
            
            doc_terms = self._extract_technical_terms(doc_text)
            
            # Find unique terms in research
            unique_terms = research_terms - doc_terms
            if unique_terms:
                differences.append(f"Novel technical aspects: {', '.join(list(unique_terms)[:3])}")
        
        return differences[:10]  # Return top 10 differences
    
    def _extract_technical_terms(self, text: str) -> set:
        """Extract technical terms from text"""
        # Simple technical term extraction (would be enhanced with NLP)
        technical_patterns = [
            r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)+\b',  # CamelCase terms
            r'\b\w+(?:-\w+)+\b',  # Hyphenated terms
            r'\b\w*(?:tion|sion|ment|ness|ity)\b',  # Technical suffixes
        ]
        
        terms = set()
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            terms.update([m.lower() for m in matches if len(m) > 3])
        
        return terms
    
    def _analyze_text_overlap(self, text1: str, text2: str) -> Dict[str, Any]:
        """Analyze overlap between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        overlap = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(overlap) / len(union) if union else 0
        
        return {
            'jaccard_similarity': jaccard_similarity,
            'common_words': len(overlap),
            'unique_words_text1': len(words1 - words2),
            'unique_words_text2': len(words2 - words1)
        }
    
    def _assess_patentability(
        self,
        claims: List[str],
        patent_similarities: List[Dict],
        novelty_score: float
    ) -> Dict[str, Any]:
        """Assess patentability indicators"""
        # Analyze patent claims structure
        claim_analysis = self._analyze_claims_structure(claims)
        
        # Check for prior art issues
        prior_art_issues = []
        for patent in patent_similarities[:5]:
            if patent['similarity_score'] > 0.8:
                prior_art_issues.append({
                    'patent_id': patent['id'],
                    'issue_type': 'High similarity',
                    'similarity_score': patent['similarity_score']
                })
        
        return {
            'novelty_score': novelty_score,
            'claim_strength': claim_analysis['strength'],
            'claim_count': len(claims),
            'prior_art_issues': prior_art_issues,
            'patentability_likelihood': self._calculate_patentability_likelihood(
                novelty_score, claim_analysis, prior_art_issues
            )
        }
    
    def _analyze_claims_structure(self, claims: List[str]) -> Dict[str, Any]:
        """Analyze structure and strength of patent claims"""
        if not claims:
            return {'strength': 'Unknown', 'analysis': 'No claims provided'}
        
        # Simple claim analysis
        independent_claims = [c for c in claims if c.strip().startswith('1.') or 'comprising' in c.lower()]
        dependent_claims = len(claims) - len(independent_claims)
        
        strength = 'Strong' if len(independent_claims) >= 1 and dependent_claims >= 5 else 'Moderate'
        
        return {
            'strength': strength,
            'independent_claims': len(independent_claims),
            'dependent_claims': dependent_claims,
            'total_claims': len(claims)
        }
    
    def _calculate_patentability_likelihood(
        self,
        novelty_score: float,
        claim_analysis: Dict,
        prior_art_issues: List[Dict]
    ) -> str:
        """Calculate likelihood of patent approval"""
        if novelty_score > 0.8 and not prior_art_issues:
            return "High"
        elif novelty_score > 0.6 and len(prior_art_issues) < 2:
            return "Moderate"
        else:
            return "Low"
    
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
            'prior_art_density': len(patent_similarities) + len(publication_similarities),
            'key_prior_art': patent_similarities[:3] + publication_similarities[:3]
        }
    
    def _generate_recommendations(
        self,
        novelty_score: float,
        patentability: Dict,
        similar_patents: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on novelty assessment"""
        recommendations = []
        
        if novelty_score > 0.8:
            recommendations.append("Strong novelty detected - proceed with patent application")
        elif novelty_score > 0.6:
            recommendations.append("Moderate novelty - consider strengthening claims")
        else:
            recommendations.append("Limited novelty - significant differentiation needed")
        
        if patentability['prior_art_issues']:
            recommendations.append("Address prior art issues before filing")
        
        if similar_patents:
            recommendations.append("Conduct detailed prior art search focusing on top similar patents")
        
        return recommendations

import boto3
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

class AlexaDataIntegration:
    def __init__(self, aws_access_key: str = None, aws_secret_key: str = None, region: str = 'us-east-1'):
        """Initialize Alexa integration service"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize AWS clients
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        # Initialize services
        self.comprehend = self.session.client('comprehend')
        self.transcribe = self.session.client('transcribe')
        self.s3 = self.session.client('s3')
        
    async def process_voice_query(
        self, 
        audio_file_path: str,
        research_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process voice queries about patent alerts and research
        """
        try {
            # Transcribe audio to text
            transcription = await self._transcribe_audio(audio_file_path)
            
            # Extract intent and entities
            intent_analysis = await self._analyze_intent(transcription)
            
            # Process based on intent
            response = await self._process_intent(
                intent_analysis, 
                transcription, 
                research_context
            )
            
            return {
                'transcription': transcription,
                'intent': intent_analysis,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing voice query: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text"""
        try {
            # Upload audio to S3 temporarily
            bucket_name = 'patent-alerts-temp'
            object_name = f"audio_{datetime.now().timestamp()}.wav"
            
            self.s3.upload_file(audio_file_path, bucket_name, object_name)
            
            # Start transcription job
            job_name = f"transcription_{datetime.now().timestamp()}"
            
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{bucket_name}/{object_name}'},
                MediaFormat='wav',
                LanguageCode='en-US'
            )
            
            # Wait for completion (simplified - would use async polling in production)
            import time
            time.sleep(10)
            
            # Get results
            result = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Download and parse transcript
            # This is simplified - would need proper URI handling
            return "Mock transcription: Tell me about recent patents in quantum computing"
            
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return "Error in transcription"
    
    async def _analyze_intent(self, text: str) -> Dict[str, Any]:
        """Analyze intent from transcribed text"""
        try {
            # Use AWS Comprehend for entity detection
            entities_response = self.comprehend.detect_entities(
                Text=text,
                LanguageCode='en'
            )
            
            # Simple intent classification
            intents = {
                'search_patents': ['patent', 'patents', 'find', 'search'],
                'get_alerts': ['alert', 'alerts', 'notify', 'notification'],
                'analyze_novelty': ['novel', 'novelty', 'new', 'unique'],
                'find_competitors': ['competitor', 'competitors', 'competition'],
                'licensing_opportunities': ['license', 'licensing', 'opportunity']
            }
            
            detected_intent = 'unknown'
            confidence = 0.0
            
            text_lower = text.lower()
            for intent, keywords in intents.items():
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                intent_confidence = matches / len(keywords)
                
                if intent_confidence > confidence:
                    confidence = intent_confidence
                    detected_intent = intent
            
            return {
                'intent': detected_intent,
                'confidence': confidence,
                'entities': entities_response.get('Entities', []),
                'original_text': text
            }
            
        except Exception as e:
            self.logger.error(f"Intent analysis error: {e}")
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': []}
    
    async def _process_intent(
        self,
        intent_analysis: Dict[str, Any],
        original_text: str,
        research_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process the detected intent and generate response"""
        intent = intent_analysis['intent']
        
        if intent == 'search_patents':
            return await self._handle_patent_search(original_text, research_context)
        elif intent == 'get_alerts':
            return await self._handle_alert_request(original_text, research_context)
        elif intent == 'analyze_novelty':
            return await self._handle_novelty_analysis(original_text, research_context)
        elif intent == 'find_competitors':
            return await self._handle_competitor_search(original_text, research_context)
        elif intent == 'licensing_opportunities':
            return await self._handle_licensing_search(original_text, research_context)
        else:
            return {
                'response_type': 'clarification',
                'message': "I'm not sure what you're looking for. Could you please rephrase your question?",
                'suggestions': [
                    "Search for patents",
                    "Get patent alerts",
                    "Analyze novelty",
                    "Find competitors",
                    "Find licensing opportunities"
                ]
            }
    
    async def _handle_patent_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle patent search requests"""
        # Extract search terms from query
        search_terms = self._extract_search_terms(query)
        
        # This would integrate with your existing search logic
        return {
            'response_type': 'patent_search',
            'message': f"Searching for patents related to: {', '.join(search_terms)}",
            'search_terms': search_terms,
            'action': 'perform_patent_search'
        }
    
    async def _handle_alert_request(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle alert requests"""
        return {
            'response_type': 'alerts',
            'message': "Here are your recent patent alerts",
            'action': 'get_recent_alerts'
        }
    
    async def _handle_novelty_analysis(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle novelty analysis requests"""
        return {
            'response_type': 'novelty_analysis',
            'message': "Analyzing novelty of your research",
            'action': 'perform_novelty_analysis'
        }
    
    async def _handle_competitor_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle competitor search requests"""
        return {
            'response_type': 'competitor_search',
            'message': "Searching for competitors in your research domain",
            'action': 'find_competitors'
        }
    
    async def _handle_licensing_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle licensing opportunity requests"""
        return {
            'response_type': 'licensing_search',
            'message': "Identifying licensing opportunities",
            'action': 'find_licensing_opportunities'
        }
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from natural language query"""
        # Simple term extraction - would be enhanced with NLP
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [word.lower().strip('.,!?') for word in query.split()]
        return [word for word in words if word not in stop_words and len(word) > 2]

    async def create_voice_response(self, response_data: Dict[str, Any]) -> str:
        """Create voice-friendly response"""
        response_type = response_data.get('response_type', 'unknown')
        
        if response_type == 'patent_search':
            return f"I found several patents related to your search. The most relevant ones are in {response_data.get('domain', 'your research area')}."
        elif response_type == 'alerts':
            alert_count = response_data.get('alert_count', 0)
            return f"You have {alert_count} new patent alerts. Would you like me to summarize them?"
        elif response_type == 'novelty_analysis':
            novelty_score = response_data.get('novelty_score', 0)
            return f"Your research shows a novelty score of {novelty_score:.1f} out of 1.0. This indicates {response_data.get('novelty_category', 'moderate')} novelty."
        else:
            return "I've processed your request. You can view the detailed results in your dashboard."

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