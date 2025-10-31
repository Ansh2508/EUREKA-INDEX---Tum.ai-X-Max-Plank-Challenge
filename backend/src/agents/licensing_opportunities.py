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