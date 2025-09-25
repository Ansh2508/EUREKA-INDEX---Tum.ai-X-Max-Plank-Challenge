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


def assess_technology_readiness_level(abstract, patents):
    """Estimate TRL based on abstract text and patent volume."""
    trl_keywords = {
        1: ["basic principles", "fundamental", "theoretical", "concept"],
        2: ["technology concept", "application formulated", "practical applications"],
        3: ["proof of concept", "analytical", "experimental", "critical function"],
        4: ["laboratory", "component validation", "breadboard"],
        5: ["component validation", "relevant environment", "breadboard"],
        6: ["system prototype", "relevant environment", "model demonstration"],
        7: ["system demonstration", "operational environment", "prototype"],
        8: ["system complete", "flight qualified", "test demonstration"],
        9: ["actual system", "flight proven", "successful mission"],
    }

    abstract_lower = abstract.lower()
    scores = {}
    for trl, keywords in trl_keywords.items():
        score = sum(1 for kw in keywords if kw in abstract_lower)
        scores[trl] = score / len(keywords)

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

    need_keywords = ["problem", "challenge", "limitation", "bottleneck", "inefficient"]
    solution_keywords = ["novel", "improved", "optimized", "efficient", "innovative"]

    need_score = sum(1 for kw in need_keywords if kw in abstract.lower()) / len(need_keywords)
    solution_score = sum(1 for kw in solution_keywords if kw in abstract.lower()) / len(solution_keywords)

    if pub_momentum > 0.4 and patent_density < 0.3 and need_score > 0.2:
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
