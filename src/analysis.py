import json
from src.search_logic_mill import search_logic_mill

from src.utils import (
    count_recent,
    citation_velocity,
    temporal_gap,
    commercial_ratio,
    family_size_investment,
    geographic_diversity,
    get_trl_category,
    get_market_readiness,
    get_time_to_market,
    get_investment_recommendation,
    get_risk_assessment,
)


def estimate_commercial_activity_from_abstract(abstract):
    """Estimate commercial activity based on abstract keywords."""
    commercial_keywords = [
        "commercial", "product", "company", "corporation", "market", "industry",
        "deployment", "customer", "business", "revenue", "sales", "manufacturing"
    ]
    abstract_lower = abstract.lower()
    commercial_score = sum(1 for kw in commercial_keywords if kw in abstract_lower)
    return min(commercial_score / len(commercial_keywords) * 2, 1.0)  # Scale to 0-1


def estimate_innovation_momentum(publications):
    """Estimate innovation momentum from publication activity."""
    if not publications:
        return 0.0
    # Recent publications indicate active research momentum
    recent_count = count_recent(publications, 2)
    total_count = len(publications)
    momentum = recent_count / max(total_count, 1)
    return min(momentum * 1.5, 1.0)  # Boost recent activity


def estimate_investment_level(abstract):
    """Estimate investment level from abstract sophistication."""
    investment_keywords = [
        "advanced", "next-generation", "cutting-edge", "proprietary", "patented",
        "breakthrough", "revolutionary", "innovative", "state-of-the-art", "optimized"
    ]
    abstract_lower = abstract.lower()
    investment_score = sum(1 for kw in investment_keywords if kw in abstract_lower)
    return max(1.0, min(investment_score * 0.5 + 1.0, 5.0))  # Scale 1-5


def estimate_geographic_reach(abstract, publications):
    """Estimate geographic reach from scale indicators."""
    global_keywords = [
        "global", "worldwide", "international", "transform", "revolution", 
        "industry", "market", "commercial", "deployment", "scale"
    ]
    abstract_lower = abstract.lower()
    global_score = sum(1 for kw in global_keywords if kw in abstract_lower)
    # Add publication diversity boost
    pub_boost = min(len(publications) / 10.0, 0.5)
    return min((global_score * 0.1) + pub_boost, 1.0)


def estimate_market_size(abstract, title):
    """Estimate market size category (TAM/SAM/SOM) based on technology domain."""
    # Market size indicators by domain (in billions USD)
    market_domains = {
        # High-value markets
        "healthcare": {"tam": 500, "keywords": ["drug", "medical", "healthcare", "pharmaceutical", "therapy", "clinical", "diagnostic"]},
        "automotive": {"tam": 300, "keywords": ["automotive", "vehicle", "car", "transportation", "mobility", "electric vehicle"]},
        "energy": {"tam": 250, "keywords": ["energy", "battery", "solar", "renewable", "power", "grid", "storage"]},
        "ai_ml": {"tam": 200, "keywords": ["artificial intelligence", "machine learning", "neural", "deep learning", "AI", "ML"]},
        "semiconductor": {"tam": 180, "keywords": ["semiconductor", "chip", "processor", "microchip", "silicon"]},
        
        # Medium-value markets
        "fintech": {"tam": 120, "keywords": ["financial", "banking", "payment", "blockchain", "cryptocurrency", "fintech"]},
        "cybersecurity": {"tam": 100, "keywords": ["security", "cybersecurity", "encryption", "authentication", "privacy"]},
        "aerospace": {"tam": 90, "keywords": ["aerospace", "aviation", "satellite", "space", "aircraft", "drone"]},
        "telecom": {"tam": 80, "keywords": ["telecommunication", "5G", "network", "wireless", "communication"]},
        "manufacturing": {"tam": 70, "keywords": ["manufacturing", "industrial", "automation", "robotics", "factory"]},
        
        # Specialized markets
        "biotechnology": {"tam": 60, "keywords": ["biotechnology", "biotech", "genetic", "protein", "enzyme", "bio"]},
        "materials": {"tam": 50, "keywords": ["material", "polymer", "composite", "nanotechnology", "coating"]},
        "agriculture": {"tam": 40, "keywords": ["agriculture", "farming", "crop", "agricultural", "food production"]},
        "consumer": {"tam": 30, "keywords": ["consumer", "retail", "e-commerce", "mobile app", "gaming"]},
        "other": {"tam": 20, "keywords": []}  # Default fallback
    }
    
    text = (title + " " + abstract).lower()
    
    # Find best matching domain
    best_domain = "other"
    best_score = 0
    
    for domain, info in market_domains.items():
        if domain == "other":
            continue
        score = sum(1 for keyword in info["keywords"] if keyword in text)
        if score > best_score:
            best_score = score
            best_domain = domain
    
    if best_score == 0:
        best_domain = "other"
    
    tam = market_domains[best_domain]["tam"]
    
    # Estimate SAM (10-30% of TAM) and SOM (1-5% of SAM)
    sam = tam * 0.2  # 20% of TAM
    som = sam * 0.03  # 3% of SAM
    
    return {
        "domain": best_domain,
        "tam_billion_usd": tam,
        "sam_billion_usd": round(sam, 1),
        "som_billion_usd": round(som, 2),
        "market_size_score": min(tam / 100, 10)  # Normalize to 0-10 scale
    }


def assess_competitive_landscape(patents, publications, abstract):
    """Assess competitive landscape intensity and positioning."""
    total_results = len(patents) + len(publications)
    patent_ratio = len(patents) / max(1, total_results)
    
    # Competitive intensity indicators
    competitive_keywords = ["competitive", "superior", "advantage", "outperform", "better than", "improved over"]
    differentiation_keywords = ["novel", "unique", "first", "breakthrough", "revolutionary", "innovative"]
    
    text = abstract.lower()
    competitive_score = sum(1 for kw in competitive_keywords if kw in text) / len(competitive_keywords)
    differentiation_score = sum(1 for kw in differentiation_keywords if kw in text) / len(differentiation_keywords)
    
    # Calculate competitive intensity
    if total_results > 100:
        intensity = "High"
        intensity_score = 8.5
    elif total_results > 50:
        intensity = "Medium-High"  
        intensity_score = 6.5
    elif total_results > 20:
        intensity = "Medium"
        intensity_score = 5.0
    else:
        intensity = "Low"
        intensity_score = 3.0
    
    # Competitive positioning
    if differentiation_score > 0.3 and competitive_score > 0.2:
        positioning = "Strong Differentiator"
        positioning_score = 8.0
    elif differentiation_score > 0.2:
        positioning = "Moderate Differentiator"
        positioning_score = 6.0
    elif competitive_score > 0.2:
        positioning = "Competitive Player"
        positioning_score = 4.0
    else:
        positioning = "Unclear Position"
        positioning_score = 2.0
    
    return {
        "competitive_intensity": intensity,
        "intensity_score": intensity_score,
        "competitive_positioning": positioning,
        "positioning_score": positioning_score,
        "patent_density": round(patent_ratio, 3),
        "total_competing_documents": total_results,
        "landscape_score": round((intensity_score + positioning_score) / 2, 1)
    }


def assess_ip_strength(patents, abstract):
    """Assess intellectual property strength and freedom to operate."""
    if len(patents) == 0:
        # Estimate based on innovation level in abstract
        innovation_keywords = ["patent", "proprietary", "intellectual property", "invention", "novel method"]
        text = abstract.lower()
        innovation_score = sum(1 for kw in innovation_keywords if kw in text) / len(innovation_keywords)
        
        return {
            "patent_count": 0,
            "ip_strength_score": round(innovation_score * 5, 1),  # Scale to 0-5
            "fto_risk": "Medium" if innovation_score > 0.2 else "High",
            "ip_quality": "Unknown - No Patents Found",
            "recommendation": "Consider patent filing for IP protection"
        }
    
    # Calculate patent-based metrics
    avg_citations = sum(p.get("citations", 0) for p in patents) / len(patents)
    recent_patents = sum(1 for p in patents if p.get("year", 2000) >= 2020)
    recent_ratio = recent_patents / len(patents)
    
    # IP strength score (0-10)
    citation_score = min(avg_citations / 10, 5)  # Max 5 points for citations
    recency_score = recent_ratio * 3  # Max 3 points for recency
    volume_score = min(len(patents) / 20, 2)  # Max 2 points for volume
    
    ip_strength = citation_score + recency_score + volume_score
    
    # Freedom to Operate assessment
    if len(patents) > 50:
        fto_risk = "High"
    elif len(patents) > 20:
        fto_risk = "Medium"
    else:
        fto_risk = "Low"
    
    # IP Quality assessment
    if avg_citations > 15:
        ip_quality = "High Quality"
    elif avg_citations > 5:
        ip_quality = "Medium Quality"
    else:
        ip_quality = "Low Quality"
    
    return {
        "patent_count": len(patents),
        "avg_citations": round(avg_citations, 1),
        "recent_patents_ratio": round(recent_ratio, 2),
        "ip_strength_score": round(ip_strength, 1),
        "fto_risk": fto_risk,
        "ip_quality": ip_quality,
        "recommendation": "Conduct detailed FTO analysis" if fto_risk == "High" else "Good IP position"
    }


def assess_regulatory_risk(abstract, title):
    """Assess regulatory compliance risk based on technology domain."""
    # Regulatory risk by domain
    regulatory_domains = {
        "medical": {"risk": "Very High", "score": 9, "keywords": ["medical", "drug", "pharmaceutical", "clinical", "healthcare", "therapy"]},
        "automotive": {"risk": "High", "score": 7, "keywords": ["automotive", "vehicle", "safety", "transportation"]},
        "financial": {"risk": "High", "score": 7, "keywords": ["financial", "banking", "payment", "cryptocurrency"]},
        "aerospace": {"risk": "High", "score": 7, "keywords": ["aerospace", "aviation", "aircraft", "drone"]},
        "food": {"risk": "Medium-High", "score": 6, "keywords": ["food", "nutrition", "consumption", "dietary"]},
        "energy": {"risk": "Medium", "score": 5, "keywords": ["energy", "power", "grid", "renewable"]},
        "telecom": {"risk": "Medium", "score": 5, "keywords": ["telecommunication", "wireless", "spectrum"]},
        "software": {"risk": "Low-Medium", "score": 3, "keywords": ["software", "algorithm", "application", "platform"]},
        "materials": {"risk": "Low", "score": 2, "keywords": ["material", "coating", "manufacturing"]},
        "other": {"risk": "Low", "score": 2, "keywords": []}
    }
    
    text = (title + " " + abstract).lower()
    
    # Find best matching domain
    best_domain = "other"
    best_score = 0
    
    for domain, info in regulatory_domains.items():
        if domain == "other":
            continue
        score = sum(1 for keyword in info["keywords"] if keyword in text)
        if score > best_score:
            best_score = score
            best_domain = domain
    
    if best_score == 0:
        best_domain = "other"
    
    domain_info = regulatory_domains[best_domain]
    
    return {
        "regulatory_domain": best_domain,
        "risk_level": domain_info["risk"],
        "risk_score": domain_info["score"],
        "compliance_requirements": get_compliance_requirements(best_domain),
        "estimated_approval_time": get_approval_timeline(best_domain)
    }


def get_compliance_requirements(domain):
    """Get compliance requirements for domain."""
    requirements = {
        "medical": "FDA approval, Clinical trials, GMP compliance",
        "automotive": "Safety standards, Crash testing, Emissions compliance", 
        "financial": "Banking regulations, AML/KYC, Data protection",
        "aerospace": "FAA certification, Safety standards, Export controls",
        "food": "FDA/USDA approval, Safety testing, Labeling requirements",
        "energy": "Grid compliance, Safety standards, Environmental permits",
        "telecom": "FCC approval, Spectrum licensing, Standards compliance",
        "software": "Data protection, Accessibility, Security standards",
        "materials": "Safety testing, Environmental compliance",
        "other": "Standard business regulations"
    }
    return requirements.get(domain, "Standard business regulations")


def get_approval_timeline(domain):
    """Get estimated approval timeline for domain."""
    timelines = {
        "medical": "5-10 years",
        "automotive": "2-4 years",
        "financial": "1-3 years", 
        "aerospace": "2-5 years",
        "food": "1-3 years",
        "energy": "1-2 years",
        "telecom": "6-18 months",
        "software": "3-6 months",
        "materials": "6-12 months",
        "other": "3-12 months"
    }
    return timelines.get(domain, "3-12 months")


def assess_resource_requirements(abstract, trl_level):
    """Assess resource requirements based on technology complexity."""
    complexity_keywords = {
        "high": ["quantum", "nanotechnology", "biotechnology", "artificial intelligence", "machine learning", "neural network"],
        "medium": ["automation", "software", "algorithm", "system", "platform", "optimization"],
        "low": ["method", "process", "tool", "application", "interface", "analysis"]
    }
    
    text = abstract.lower()
    
    # Calculate complexity
    high_count = sum(1 for kw in complexity_keywords["high"] if kw in text)
    medium_count = sum(1 for kw in complexity_keywords["medium"] if kw in text)
    low_count = sum(1 for kw in complexity_keywords["low"] if kw in text)
    
    if high_count > 0:
        complexity = "High"
        complexity_score = 8
    elif medium_count > low_count:
        complexity = "Medium"
        complexity_score = 5
    else:
        complexity = "Low"
        complexity_score = 3
    
    # Adjust based on TRL
    trl_factor = max(1, trl_level / 5)  # Higher TRL = more resources needed for scaling
    
    # Estimate requirements
    funding_needs = {
        "High": "€10M - €100M+",
        "Medium": "€1M - €10M", 
        "Low": "€100K - €1M"
    }
    
    team_size = {
        "High": "50+ specialists",
        "Medium": "10-50 experts",
        "Low": "3-10 people"
    }
    
    development_time = {
        "High": "5-10 years",
        "Medium": "2-5 years",
        "Low": "6 months - 2 years"
    }
    
    return {
        "complexity_level": complexity,
        "complexity_score": round(complexity_score * trl_factor / 5, 1),
        "estimated_funding": funding_needs[complexity],
        "team_requirements": team_size[complexity],
        "development_timeline": development_time[complexity],
        "resource_risk": "High" if complexity_score > 6 else "Medium" if complexity_score > 3 else "Low"
    }


def assess_technology_readiness_level(abstract, patents):
    """Estimate TRL based on abstract text and patent volume."""
    trl_keywords = {
        1: ["basic principles", "fundamental research", "theoretical", "basic concept"],
        2: ["technology concept", "application formulated", "practical applications", "conceptual design"],
        3: ["proof of concept", "analytical", "experimental", "critical function", "feasibility study"],
        4: ["laboratory", "component validation", "breadboard", "lab scale", "bench testing"],
        5: ["component validation", "relevant environment", "pilot scale", "small scale production"],
        6: ["system prototype", "relevant environment", "model demonstration", "pilot demonstration", "prototype testing", "clinical trials", "patients"],
        7: ["system demonstration", "operational environment", "prototype", "pre-commercial", "field testing", "clinical validation", "patient study", "trial results"],
        8: ["system complete", "commercial product", "market ready", "production ready", "commercial deployment", "first commercial", "planned commercial", "clinical approval"],
        9: ["actual system", "proven commercial", "successful mission", "commercial success", "market deployment", "full commercial", "FDA approved"],
    }
    
    # Additional commercial readiness indicators
    commercial_indicators = [
        "commercial product", "planned commercial", "first commercial", "market ready",
        "production ready", "commercial deployment", "market deployment", "superior to conventional",
        "next-generation", "transform", "mission to transform", "designed to enable"
    ]

    abstract_lower = abstract.lower()
    scores = {}
    for trl, keywords in trl_keywords.items():
        score = sum(1 for kw in keywords if kw in abstract_lower)
        scores[trl] = score / len(keywords)

    # Check for commercial readiness indicators
    commercial_score = sum(1 for indicator in commercial_indicators if indicator in abstract_lower)
    if commercial_score > 0:
        # Boost TRL 7-9 scores for commercial indicators
        scores[7] += commercial_score * 0.3
        scores[8] += commercial_score * 0.5
        scores[9] += commercial_score * 0.2

    estimated_trl = max(scores, key=scores.get) if scores else 1

    # Boost based on patent maturity
    if len(patents) > 50:
        estimated_trl += 2
    elif len(patents) > 20:
        estimated_trl += 1
    elif len(patents) > 5:
        estimated_trl += 0.5

    estimated_trl = min(9, max(1, estimated_trl))

    return {
        "estimated_trl": round(estimated_trl, 1),
        "trl_category": get_trl_category(estimated_trl),
        "market_readiness": get_market_readiness(estimated_trl),
        "time_to_market": get_time_to_market(estimated_trl),
    }


def assess_market_need_gap(abstract, patents, publications):
    """Detect market gap by comparing research vs patent activity."""
    pub_momentum = count_recent(publications, 2) / max(1, len(publications))
    patent_density = len(patents) / 100.0

    need_keywords = ["problem", "challenge", "limitation", "bottleneck", "inefficient", "conventional", "legacy", "invasive", "complex procedures", "recovery times", "complications", "risk"]
    solution_keywords = ["novel", "improved", "optimized", "efficient", "innovative", "unmatched", "superior", "enhanced", "next-generation", "transform", "enable greater", "minimally invasive", "reduced", "success rates", "breakthrough", "autonomous", "accurate", "precise"]

    need_score = sum(1 for kw in need_keywords if kw in abstract.lower()) / len(need_keywords)
    solution_score = sum(1 for kw in solution_keywords if kw in abstract.lower()) / len(solution_keywords)

    # Enhanced logic for commercial products and clinical validation
    commercial_terms = any(term in abstract.lower() for term in ["commercial product", "planned commercial", "first commercial", "market ready"])
    clinical_terms = any(term in abstract.lower() for term in ["clinical trials", "patients", "success rate", "patient study", "clinical validation", "trial results"])
    
    # Strong clinical evidence boost
    if clinical_terms and solution_score > 0.2:
        status, score = "CLEAR_MARKET_GAP_IDENTIFIED", 8.5
    elif commercial_terms and solution_score > 0.2:
        status, score = "CLEAR_MARKET_GAP_IDENTIFIED", 8.5
    elif solution_score > 0.3 and (need_score > 0.1 or commercial_terms or clinical_terms):
        status, score = "POTENTIAL_MARKET_OPPORTUNITY", 7.0
    elif pub_momentum > 0.4 and patent_density < 0.3 and need_score > 0.2:
        status, score = "CLEAR_MARKET_GAP_IDENTIFIED", 8.5
    elif pub_momentum > 0.3 and need_score > 0.1:
        status, score = "POTENTIAL_MARKET_OPPORTUNITY", 6.5
    elif patent_density > 0.7:
        status, score = "SATURATED_MARKET", 3.0
    else:
        status, score = "UNCLEAR_MARKET_NEED", 4.0

    return {
        "gap_status": status,
        "gap_score": score,
        "need_indicators": round(need_score, 2),
        "solution_indicators": round(solution_score, 2),
        "publication_momentum": round(pub_momentum, 2),
        "patent_density": round(patent_density, 2),
    }


def analyze_research_potential(title, abstract, debug=False):
    """Run full analysis pipeline."""
    results = search_logic_mill(title, abstract, debug=debug)

    patents = [r for r in results if r.get("index") == "patents"]
    publications = [r for r in results if r.get("index") == "publications"]

    market_gap = assess_market_need_gap(abstract, patents, publications)
    trl_assessment = assess_technology_readiness_level(abstract, patents)

    cit_velocity = citation_velocity(patents)
    comm_ratio = commercial_ratio(patents)
    avg_family = family_size_investment(patents)
    geo_div = geographic_diversity(patents)
    
    # If no patents, estimate commercial indicators from publications and abstract
    if len(patents) == 0:
        comm_ratio = estimate_commercial_activity_from_abstract(abstract)
        cit_velocity = estimate_innovation_momentum(publications)
        avg_family = estimate_investment_level(abstract)
        geo_div = estimate_geographic_reach(abstract, publications)

    # New comprehensive assessments
    market_size = estimate_market_size(abstract, title)
    competitive_landscape = assess_competitive_landscape(patents, publications, abstract)
    ip_strength = assess_ip_strength(patents, abstract)
    regulatory_risk = assess_regulatory_risk(abstract, title)
    resource_requirements = assess_resource_requirements(abstract, trl_assessment["estimated_trl"])

    # Enhanced scoring with new metrics
    base_score = (
        market_gap["gap_score"] * 0.25
        + trl_assessment["estimated_trl"] * 0.20
        + (comm_ratio * 10) * 0.15
        + (cit_velocity * 10) * 0.10
        + market_size["market_size_score"] * 0.15
        + competitive_landscape["landscape_score"] * 0.10
        + (10 - regulatory_risk["risk_score"]) * 0.05  # Lower risk = higher score
    )
    score = round(max(0, min(10, base_score)), 2)

    return {
        "overall_assessment": {
            "market_potential_score": score,
            "investment_recommendation": get_investment_recommendation(score),
            "risk_level": get_risk_assessment(market_gap, trl_assessment),
        },
        "market_analysis": market_gap,
        "technology_assessment": trl_assessment,
        "commercial_indicators": {
            "citation_velocity": round(cit_velocity, 3),
            "commercial_ratio": round(comm_ratio, 3),
            "avg_family_size": round(avg_family, 2),
            "geographic_diversity": round(geo_div, 3),
        },
        "market_size_analysis": market_size,
        "competitive_landscape": competitive_landscape,
        "ip_strength_analysis": ip_strength,
        "regulatory_risk_analysis": regulatory_risk,
        "resource_requirements": resource_requirements
    }


def main():
    title = "Quantum ML for Drug Discovery"
    abstract = "Quantum machine learning algorithms for drug discovery optimization using variational quantum circuits"
    result = analyze_research_potential(title, abstract, debug=False)
    print(json.dumps(result, indent=2))
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
