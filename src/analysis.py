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


def assess_technology_readiness_level(abstract, patents):
    """Estimate TRL based on abstract text and patent volume."""
    trl_keywords = {
        1: ["basic principles", "fundamental research", "theoretical", "basic concept"],
        2: ["technology concept", "application formulated", "practical applications", "conceptual design"],
        3: ["proof of concept", "analytical", "experimental", "critical function", "feasibility study"],
        4: ["laboratory", "component validation", "breadboard", "lab scale", "bench testing"],
        5: ["component validation", "relevant environment", "pilot scale", "small scale production"],
        6: ["system prototype", "relevant environment", "model demonstration", "pilot demonstration", "prototype testing"],
        7: ["system demonstration", "operational environment", "prototype", "pre-commercial", "field testing"],
        8: ["system complete", "commercial product", "market ready", "production ready", "commercial deployment", "first commercial", "planned commercial"],
        9: ["actual system", "proven commercial", "successful mission", "commercial success", "market deployment", "full commercial"],
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

    need_keywords = ["problem", "challenge", "limitation", "bottleneck", "inefficient", "conventional", "legacy"]
    solution_keywords = ["novel", "improved", "optimized", "efficient", "innovative", "unmatched", "superior", "enhanced", "next-generation", "transform", "enable greater"]

    need_score = sum(1 for kw in need_keywords if kw in abstract.lower()) / len(need_keywords)
    solution_score = sum(1 for kw in solution_keywords if kw in abstract.lower()) / len(solution_keywords)

    # Enhanced logic for commercial products
    commercial_terms = any(term in abstract.lower() for term in ["commercial product", "planned commercial", "first commercial", "market ready"])
    
    if commercial_terms and solution_score > 0.2:
        status, score = "CLEAR_MARKET_GAP_IDENTIFIED", 8.5
    elif solution_score > 0.3 and (need_score > 0.1 or commercial_terms):
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

    score = (
        market_gap["gap_score"] * 0.40
        + trl_assessment["estimated_trl"] * 0.35
        + (comm_ratio * 10) * 0.15
        + (cit_velocity * 10) * 0.10
    )
    score = round(max(0, min(10, score)), 2)

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
        }
    }


def main():
    title = "Quantum ML for Drug Discovery"
    abstract = "Quantum machine learning algorithms for drug discovery optimization using variational quantum circuits"
    result = analyze_research_potential(title, abstract, debug=False)
    print(json.dumps(result, indent=2))
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
