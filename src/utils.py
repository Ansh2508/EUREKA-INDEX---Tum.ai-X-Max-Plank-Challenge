from datetime import datetime

def count_recent(items, years=2, date_field="publication_date"):
    """Count items published within the last N years."""
    now_year = datetime.now().year
    count = 0
    for item in items:
        date_str = item.get(date_field, "")
        if date_str:
            try:
                if len(date_str) >= 4:
                    year = int(date_str[:4])
                    if now_year - year <= years:
                        count += 1
            except (ValueError, TypeError):
                continue
    return count


def citation_velocity(patents):
    """Compute average of recent/total citation ratios."""
    if not patents:
        return 0.0
    ratios = []
    for p in patents:
        total_citations_raw = p.get("forward_citations", p.get("citation_count", p.get("citations")))
        recent_citations_raw = p.get("recent_citations", p.get("citation_count_recent"))
        try:
            total_citations = int(total_citations_raw) if total_citations_raw is not None else 0
            recent_citations = int(recent_citations_raw) if recent_citations_raw is not None else 0
            total_citations = max(1, total_citations)
            ratios.append(recent_citations / total_citations)
        except (ValueError, TypeError):
            continue
    return sum(ratios) / len(ratios) if ratios else 0.0


def temporal_gap(publications, patents):
    """Analyze publication vs patent momentum."""
    pub_total, pat_total = len(publications), len(patents)
    if pub_total == 0 or pat_total == 0:
        return 0.0, 0.0, False
    pub_recent = count_recent(publications, 2)
    pat_recent = count_recent(patents, 2)
    pub_momentum = pub_recent / pub_total
    pat_momentum = pat_recent / pat_total
    gap_detected = pub_momentum > pat_momentum * 1.5 and pub_momentum > 0.3
    return pub_momentum, pat_momentum, gap_detected


def commercial_ratio(patents):
    """Calculate ratio of corporate vs academic patents."""
    if not patents:
        return 0.0
    corporate_count = 0
    total_count = len(patents)
    for patent in patents:
        assignee = patent.get("assignee", "").lower()
        assignee_type = patent.get("assignee_type", "").lower()
        if (assignee_type == "corporate" or
            any(corp_word in assignee for corp_word in ["corp", "inc", "ltd", "llc", "company", "technologies"])):
            corporate_count += 1
        elif any(acad_word in assignee for acad_word in ["university", "college", "institute", "school"]):
            continue
        elif assignee and "university" not in assignee and "institute" not in assignee:
            corporate_count += 1
    return corporate_count / total_count if total_count > 0 else 0.0


def family_size_investment(patents):
    """Calculate average patent family size as investment indicator."""
    if not patents:
        return 1.0
    family_sizes = []
    for patent in patents:
        family_size = patent.get("family_size", patent.get("patent_family_size", 1))
        if family_size is not None:
            try:
                family_size = int(family_size)
                if family_size > 0:
                    family_sizes.append(family_size)
            except (ValueError, TypeError):
                continue
    return sum(family_sizes) / len(family_sizes) if family_sizes else 1.0


def geographic_diversity(patents):
    """Calculate geographic distribution of patents."""
    if not patents:
        return 0.0
    countries = set()
    for patent in patents:
        country = patent.get("country", patent.get("jurisdiction", ""))
        if country:
            countries.add(country.upper())
    return min(len(countries) / 10.0, 1.0)


def get_trl_category(trl):
    if trl >= 8:
        return "MARKET_READY"
    elif trl >= 6:
        return "PILOT_DEMONSTRATION"
    elif trl >= 3:
        return "RESEARCH_DEVELOPMENT"
    return "FUNDAMENTAL_RESEARCH"


def get_market_readiness(trl):
    if trl >= 8:
        return "HIGH - Ready for commercial deployment"
    elif trl >= 6:
        return "MEDIUM-HIGH - Near market ready, needs validation"
    elif trl >= 4:
        return "MEDIUM - Significant development still needed"
    return "LOW - Early stage research"


def get_time_to_market(trl):
    time_estimates = {
        1: "10+ years", 2: "8-10 years", 3: "6-8 years",
        4: "5-7 years", 5: "4-6 years", 6: "3-5 years",
        7: "2-4 years", 8: "1-2 years", 9: "0-1 years"
    }
    trl_floor = int(trl)
    return time_estimates.get(trl_floor, "Unknown")


def get_investment_recommendation(score):
    if score >= 8.0:
        return "STRONG BUY - High potential, proceed with patent filing and commercialization"
    elif score >= 6.0:
        return "BUY - Good potential, conduct deeper due diligence"
    elif score >= 4.0:
        return "HOLD - Monitor development, reassess in 6-12 months"
    return "PASS - Insufficient commercial potential at this time"


def get_risk_assessment(market_gap, trl_assessment):
    gap_risk = "LOW" if market_gap['gap_status'] == "CLEAR_MARKET_GAP_IDENTIFIED" else "HIGH"
    trl_risk = "LOW" if trl_assessment['estimated_trl'] >= 6 else "HIGH"
    if gap_risk == "LOW" and trl_risk == "LOW":
        return "LOW RISK - Clear market opportunity with mature technology"
    elif gap_risk == "LOW" or trl_risk == "LOW":
        return "MEDIUM RISK - One major risk factor identified"
    return "HIGH RISK - Multiple risk factors present"
