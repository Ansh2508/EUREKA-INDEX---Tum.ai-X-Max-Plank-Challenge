import asyncio
from typing import List, Dict, Any, Optional
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