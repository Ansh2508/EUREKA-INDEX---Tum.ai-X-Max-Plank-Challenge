import json
from src.search_logic_mill import search_logic_mill
from collections import defaultdict, Counter

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
    """Estimate market size category (TAM/SAM/SOM) based on technology domain - Updated September 2025."""
    import datetime
    
    # Market size indicators by domain (in billions USD) - Updated September 2025 with comprehensive research
    market_domains = {
        # MEGA MARKETS (>$500B)
        "healthcare": {
            "tam_2025": 580,  # Updated from research
            "cagr": 0.089,    # 8.9% CAGR
            "keywords": ["drug", "medical", "healthcare", "pharmaceutical", "therapy", "clinical", "diagnostic", "telemedicine", "medical device"],
            "last_updated": "2025-09-26",
            "confidence": 0.92
        },
        
        # ULTRA HIGH-VALUE MARKETS ($300-500B)
        "space_tech": {
            "tam_2025": 485,  # NEW - Space economy boom
            "cagr": 0.15,     # 15% CAGR
            "keywords": ["space", "satellite", "rocket", "orbital", "space technology", "launch", "spacecraft", "space exploration", "space station", "space debris", "lunar", "mars"],
            "last_updated": "2025-09-26",
            "confidence": 0.85
        },
        "automotive": {
            "tam_2025": 420,  # EV revolution acceleration
            "cagr": 0.078,    # 7.8% CAGR 
            "keywords": ["automotive", "vehicle", "car", "transportation", "mobility", "electric vehicle", "autonomous", "self-driving", "EV", "battery vehicle"],
            "last_updated": "2025-09-26",
            "confidence": 0.90
        },
        "ai_ml": {
            "tam_2025": 380,  # Massive growth from 250B in 2024
            "cagr": 0.25,     # 25% CAGR (explosive AI boom)
            "keywords": ["artificial intelligence", "machine learning", "neural", "deep learning", "AI", "ML", "large language model", "computer vision", "NLP", "generative AI", "LLM"],
            "last_updated": "2025-09-26",
            "confidence": 0.88
        },
        "energy": {
            "tam_2025": 340,  # Green energy boom
            "cagr": 0.105,    # 10.5% CAGR
            "keywords": ["energy", "battery", "solar", "renewable", "power", "grid", "storage", "wind energy", "hydrogen", "energy storage", "smart grid"],
            "last_updated": "2025-09-26",
            "confidence": 0.91
        },
        
        # HIGH-VALUE MARKETS ($200-300B)
        "digital_health": {
            "tam_2025": 295,  # NEW - Separated from general healthcare
            "cagr": 0.16,     # 16% CAGR
            "keywords": ["digital health", "healthtech", "telemedicine", "medical app", "health monitoring", "wearable health", "medical AI", "precision medicine", "digital therapeutics", "health data"],
            "last_updated": "2025-09-26",
            "confidence": 0.87
        },
        "cybersecurity": {
            "tam_2025": 285,  # Major growth due to threats
            "cagr": 0.17,     # 17% CAGR
            "keywords": ["security", "cybersecurity", "encryption", "authentication", "privacy", "firewall", "intrusion detection", "malware", "vulnerability", "zero trust", "GDPR", "compliance", "penetration testing", "threat intelligence", "ransomware", "phishing", "endpoint security", "cloud security", "identity management", "blockchain security"],
            "last_updated": "2025-09-26",
            "confidence": 0.93
        },
        "semiconductor": {
            "tam_2025": 245,  # Continued chip demand
            "cagr": 0.082,    # 8.2% CAGR
            "keywords": ["semiconductor", "chip", "processor", "microchip", "silicon", "wafer", "integrated circuit", "CPU", "GPU", "ASIC", "FPGA"],
            "last_updated": "2025-09-26",
            "confidence": 0.89
        },
        "cleantech": {
            "tam_2025": 245,  # Climate urgency
            "cagr": 0.14,     # 14% CAGR
            "keywords": ["clean technology", "environmental", "sustainability", "carbon capture", "waste management", "water treatment", "green energy", "eco-friendly", "circular economy", "emission reduction", "carbon neutral", "ESG"],
            "last_updated": "2025-09-26",
            "confidence": 0.87
        },
        "robotics": {
            "tam_2025": 235,  # NEW - Separated from manufacturing
            "cagr": 0.13,     # 13% CAGR
            "keywords": ["robotics", "robot", "robotic", "automation", "robotic process automation", "industrial robot", "service robot", "humanoid", "drone", "UAV", "robotic surgery"],
            "last_updated": "2025-09-26",
            "confidence": 0.86
        },
        "consumer": {
            "tam_2025": 220,  # Digital consumer boom
            "cagr": 0.12,     # 12% CAGR
            "keywords": ["consumer", "retail", "e-commerce", "mobile app", "gaming", "social media", "entertainment", "user experience", "platform", "digital content", "streaming", "marketplace", "subscription", "freemium", "monetization", "user engagement", "social network", "influencer"],
            "last_updated": "2025-09-26",
            "confidence": 0.89
        },
        
        # MEDIUM-HIGH VALUE MARKETS ($100-200B)
        "fintech": {
            "tam_2025": 185,  # Digital payment boom
            "cagr": 0.14,     # 14% CAGR
            "keywords": ["financial", "banking", "payment", "blockchain", "cryptocurrency", "fintech", "digital payment", "neobank", "defi", "digital wallet", "mobile payment"],
            "last_updated": "2025-09-26",
            "confidence": 0.88
        },
        "iot": {
            "tam_2025": 175,  # IoT everywhere
            "cagr": 0.15,     # 15% CAGR
            "keywords": ["internet of things", "IoT", "connected devices", "smart home", "smart city", "sensors", "edge computing", "mesh network", "device connectivity", "remote monitoring", "industrial IoT"],
            "last_updated": "2025-09-26",
            "confidence": 0.89
        },
        "industry_4_0": {
            "tam_2025": 165,  # NEW - Industry 4.0 boom
            "cagr": 0.12,     # 12% CAGR
            "keywords": ["industry 4.0", "smart factory", "industrial IoT", "digital twin", "predictive maintenance", "industrial automation", "smart manufacturing", "cyber-physical systems"],
            "last_updated": "2025-09-26",
            "confidence": 0.84
        },
        "materials": {
            "tam_2025": 165,  # Advanced materials
            "cagr": 0.08,     # 8% CAGR
            "keywords": ["material", "polymer", "composite", "nanotechnology", "coating", "ceramic", "metal", "crystalline", "molecular", "surface treatment", "smart materials", "biomaterials", "graphene", "carbon fiber", "metamaterials", "thin films", "adhesives", "membranes", "catalysts", "semiconducting materials"],
            "last_updated": "2025-09-26",
            "confidence": 0.86
        },
        "edtech": {
            "tam_2025": 155,  # Post-pandemic growth
            "cagr": 0.19,     # 19% CAGR
            "keywords": ["education", "learning", "e-learning", "training", "educational technology", "online courses", "virtual classroom", "adaptive learning", "assessment", "student engagement", "LMS", "microlearning"],
            "last_updated": "2025-09-26",
            "confidence": 0.85
        },
        "aerospace": {
            "tam_2025": 135,  # Commercial space growth
            "cagr": 0.065,    # 6.5% CAGR
            "keywords": ["aerospace", "aviation", "aircraft", "drone", "aviation technology", "flight", "avionics"],
            "last_updated": "2025-09-26",
            "confidence": 0.88
        },
        "telecom": {
            "tam_2025": 110,  # 5G rollout
            "cagr": 0.052,    # 5.2% CAGR
            "keywords": ["telecommunication", "5G", "network", "wireless", "communication", "cellular", "fiber optic", "broadband"],
            "last_updated": "2025-09-26",
            "confidence": 0.89
        },
        "manufacturing": {
            "tam_2025": 105,  # Traditional manufacturing
            "cagr": 0.065,    # 6.5% CAGR
            "keywords": ["manufacturing", "industrial", "factory", "production", "assembly"],
            "last_updated": "2025-09-26",
            "confidence": 0.87
        },
        
        # EMERGING HIGH-GROWTH MARKETS ($50-100B)
        "biotechnology": {
            "tam_2025": 95,   # Biotech boom
            "cagr": 0.11,     # 11% CAGR
            "keywords": ["biotechnology", "biotech", "genetic", "protein", "enzyme", "bio", "gene therapy", "synthetic biology", "bioinformatics"],
            "last_updated": "2025-09-26",
            "confidence": 0.88
        },
        "edge_computing": {
            "tam_2025": 95,   # NEW - Edge computing boom
            "cagr": 0.18,     # 18% CAGR
            "keywords": ["edge computing", "edge AI", "distributed computing", "fog computing", "edge analytics", "real-time processing", "latency", "edge infrastructure"],
            "last_updated": "2025-09-26",
            "confidence": 0.82
        },
        "blockchain_web3": {
            "tam_2025": 85,   # NEW - Web3 emergence
            "cagr": 0.22,     # 22% CAGR
            "keywords": ["blockchain", "web3", "cryptocurrency", "smart contract", "decentralized", "DeFi", "NFT", "metaverse", "crypto", "distributed ledger"],
            "last_updated": "2025-09-26",
            "confidence": 0.75
        },
        "agriculture": {
            "tam_2025": 75,   # AgTech growth
            "cagr": 0.095,    # 9.5% CAGR
            "keywords": ["agriculture", "farming", "crop", "agricultural", "food production", "precision agriculture", "vertical farming", "agtech", "smart farming"],
            "last_updated": "2025-09-26",
            "confidence": 0.83
        },
        "quantum_computing": {
            "tam_2025": 65,   # NEW - Quantum breakthrough
            "cagr": 0.28,     # 28% CAGR
            "keywords": ["quantum", "quantum computing", "quantum algorithm", "quantum cryptography", "qubit", "quantum supremacy", "quantum machine learning"],
            "last_updated": "2025-09-26",
            "confidence": 0.70
        },
        
        # MAJOR MISSING MARKETS - ELECTRONICS & DEFENSE
        "quantum_materials": {
            "tam_2025": 85,    # NEW - Quantum materials research (Max Planck focus)
            "cagr": 0.22,      # 22% CAGR (emerging field)
            "keywords": ["quantum materials", "quantum matter", "topological materials", "quantum spin", "quantum phase", "superconducting materials", "quantum dots", "quantum wells", "quantum wires", "quantum heterostructures", "quantum confinement", "quantum coherence", "quantum entanglement", "quantum criticality", "quantum magnetism", "quantum optics materials", "quantum photonics", "quantum sensors", "quantum metrology"],
            "last_updated": "2025-09-26",
            "confidence": 0.75
        },
        "defense_tech": {
            "tam_2025": 520,   # NEW - Defense technology market
            "cagr": 0.085,     # 8.5% CAGR (strong government spending)
            "keywords": ["defense", "military", "defense technology", "military technology", "radar", "surveillance", "defense system", "military electronics", "weapons system", "missile", "defense equipment", "military hardware", "tactical", "strategic", "reconnaissance", "electronic warfare", "signal intelligence", "military communication", "armored", "ballistic", "anti-aircraft", "naval defense", "air defense", "homeland security", "military aerospace", "defense contractor"],
            "last_updated": "2025-09-26",
            "confidence": 0.88
        },
        
        # ADDITIONAL MAJOR INDUSTRIES - CONSTRUCTION, FOOD, TEXTILES
        "neuroscience": {
            "tam_2025": 180,    # NEW - Neuroscience research (Max Planck focus)
            "cagr": 0.15,       # 15% CAGR (rapidly growing field)
            "keywords": ["neuroscience", "neurobiology", "brain research", "neural networks", "neuroplasticity", "neuroimaging", "neurotechnology", "brain-computer interface", "neural engineering", "cognitive neuroscience", "computational neuroscience", "systems neuroscience", "molecular neuroscience", "developmental neuroscience", "behavioral neuroscience", "neuropharmacology", "neurogenetics", "neuroprosthetics", "neural stimulation", "brain mapping", "connectomics"],
            "last_updated": "2025-09-26",
            "confidence": 0.88
        },
        "particle_physics": {
            "tam_2025": 45,     # NEW - Particle physics research (Max Planck focus)
            "cagr": 0.08,       # 8% CAGR (fundamental research)
            "keywords": ["particle physics", "high energy physics", "accelerator physics", "detector technology", "particle accelerator", "collider", "elementary particles", "fundamental forces", "standard model", "beyond standard model", "dark matter", "dark energy", "neutrino physics", "quantum field theory", "lattice QCD", "particle detection", "calorimetry", "tracking detector", "muon detector", "neutrino detector"],
            "last_updated": "2025-09-26",
            "confidence": 0.85
        },
        "astrophysics": {
            "tam_2025": 35,     # NEW - Astrophysics research (Max Planck focus)
            "cagr": 0.12,       # 12% CAGR (space exploration boom)
            "keywords": ["astrophysics", "astronomy", "cosmology", "stellar physics", "galactic astronomy", "extragalactic astronomy", "observational astronomy", "theoretical astrophysics", "computational astrophysics", "gravitational waves", "black holes", "neutron stars", "supernovae", "exoplanets", "planetary science", "solar physics", "space telescopes", "radio astronomy", "infrared astronomy", "X-ray astronomy", "gamma-ray astronomy"],
            "last_updated": "2025-09-26",
            "confidence": 0.82
        },
        "other": {
            "tam_2025": 35,   # Default fallback
            "cagr": 0.06,     # 6% CAGR
            "keywords": [],
            "last_updated": "2025-09-26",
            "confidence": 0.80
        }
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
    
    domain_info = market_domains[best_domain]
    
    # Calculate current TAM based on growth from base year 2025
    current_year = datetime.datetime.now().year
    years_since_base = current_year - 2025
    
    # Apply compound annual growth rate (CAGR)
    current_tam = domain_info["tam_2025"] * (1 + domain_info["cagr"]) ** years_since_base
    
    # Estimate SAM (15-25% of TAM) and SOM (1-5% of SAM)
    sam = current_tam * 0.2  # 20% of TAM
    som = sam * 0.03  # 3% of SAM
    
    # Calculate market size score with growth consideration
    market_size_score = min(current_tam / 100, 10)  # Normalize to 0-10 scale
    
    # Project future market size (5-year projection)
    future_tam_5y = current_tam * (1 + domain_info["cagr"]) ** 5
    
    return {
        "domain": best_domain,
        "tam_billion_usd": round(current_tam, 1),
        "sam_billion_usd": round(sam, 1),
        "som_billion_usd": round(som, 2),
        "market_size_score": round(market_size_score, 1),
        "cagr_percent": round(domain_info["cagr"] * 100, 1),
        "future_tam_5y": round(future_tam_5y, 1),
        "base_year": 2025,
        "current_year": current_year,
        "data_source": "September 2025 Market Research Update",
        "last_updated": domain_info["last_updated"],
        "confidence": domain_info.get("confidence", 0.80),
        "total_domains_covered": len(market_domains)
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
        "materials": {"risk": "Medium", "score": 4, "keywords": ["material", "coating", "manufacturing", "composite", "nanotechnology"]},
        "edtech": {"risk": "Medium", "score": 4, "keywords": ["education", "learning", "student", "educational technology"]},
        "cleantech": {"risk": "Medium-High", "score": 6, "keywords": ["environmental", "sustainability", "emission", "waste", "clean technology"]},
        "iot": {"risk": "Medium", "score": 4, "keywords": ["IoT", "connected devices", "smart", "sensors"]},
        "cybersecurity": {"risk": "High", "score": 7, "keywords": ["security", "cybersecurity", "encryption", "privacy", "compliance"]},
        "consumer": {"risk": "Low-Medium", "score": 3, "keywords": ["consumer", "gaming", "social media", "mobile app", "entertainment"]},
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
        "materials": "Safety testing, Environmental compliance, REACH compliance",
        "edtech": "FERPA compliance, Student privacy, Accessibility standards",
        "cleantech": "Environmental permits, EPA compliance, Carbon standards",
        "iot": "FCC certification, Cybersecurity standards, Privacy regulations",
        "cybersecurity": "Security certifications, SOC compliance, GDPR/CCPA",
        "consumer": "Consumer protection, Privacy laws, Platform policies",
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
        "materials": "6-18 months",
        "edtech": "6-12 months",
        "cleantech": "1-3 years",
        "iot": "6-12 months",
        "cybersecurity": "3-9 months",
        "consumer": "3-6 months",
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
        4: ["laboratory", "component validation", "breadboard", "lab scale", "bench testing", "alpha version", "internal testing", "code review"],
        5: ["component validation", "relevant environment", "pilot scale", "small scale production", "beta version", "limited user testing", "integration testing"],
        6: ["system prototype", "relevant environment", "model demonstration", "pilot demonstration", "prototype testing", "clinical trials", "patients", "beta release", "user feedback", "closed beta"],
        7: ["system demonstration", "operational environment", "prototype", "pre-commercial", "field testing", "clinical validation", "patient study", "trial results", "public beta", "production testing", "scalability testing"],
        8: ["system complete", "commercial product", "market ready", "production ready", "commercial deployment", "first commercial", "planned commercial", "clinical approval", "general availability", "production release", "commercial launch"],
        9: ["actual system", "proven commercial", "successful mission", "commercial success", "market deployment", "full commercial", "FDA approved", "widespread adoption", "market leader", "proven scalability"],
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


def extract_key_players_from_openalex(publications):
    """Extract key players from OpenAlex publications using their IDs."""
    try:
        import requests
        import time
        
        authors = defaultdict(lambda: {
            'publications': 0, 
            'patents': 0, 
            'collaborations': set(),
            'institutions': set()
        })
        
        institutions = defaultdict(lambda: {
            'publications': 0, 
            'patents': 0, 
            'authors': set()
        })
        
        # Extract OpenAlex work IDs from publications
        openalex_ids = []
        for pub in publications:
            if pub.get('url') and 'openalex.org' in pub.get('url', ''):
                openalex_ids.append(pub['url'])
        
        print(f"[DEBUG] Found {len(openalex_ids)} OpenAlex publications to fetch metadata for")
        
        # Fetch detailed metadata from OpenAlex API
        for i, work_url in enumerate(openalex_ids[:10]):  # Limit to first 10 for performance
            try:
                # Extract work ID from URL
                work_id = work_url.split('/')[-1]
                
                # Fetch from OpenAlex API
                response = requests.get(f"https://api.openalex.org/works/{work_id}")
                if response.status_code == 200:
                    work_data = response.json()
                    
                    # Extract authors
                    for authorship in work_data.get('authorships', []):
                        author = authorship.get('author', {})
                        author_name = author.get('display_name', '')
                        
                        if author_name:
                            authors[author_name]['publications'] += 1
                            
                            # Track institutions
                            for inst in authorship.get('institutions', []):
                                inst_name = inst.get('display_name', '')
                                if inst_name:
                                    authors[author_name]['institutions'].add(inst_name)
                                    institutions[inst_name]['publications'] += 1
                                    institutions[inst_name]['authors'].add(author_name)
                            
                            # Track collaborations
                            for other_auth in work_data.get('authorships', []):
                                other_name = other_auth.get('author', {}).get('display_name', '')
                                if other_name != author_name and other_name:
                                    authors[author_name]['collaborations'].add(other_name)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[DEBUG] Error fetching OpenAlex data for {work_url}: {e}")
                continue
        
        # Create top authors list
        top_authors = []
        for author_name, data in authors.items():
            if data['publications'] >= 1:
                collaboration_score = len(data['collaborations']) / max(1, data['publications'])
                top_authors.append({
                    'name': author_name,
                    'publication_count': data['publications'],
                    'patent_count': 0,  # No patent data from OpenAlex
                    'collaboration_score': collaboration_score,
                    'total_documents': data['publications']
                })
        
        # Sort by total documents
        top_authors.sort(key=lambda x: x['total_documents'], reverse=True)
        
        # Create top institutions list
        top_institutions = []
        for inst_name, data in institutions.items():
            if data['publications'] >= 1:
                top_institutions.append({
                    'name': inst_name,
                    'publication_count': data['publications'],
                    'patent_count': 0,  # No patent data from OpenAlex
                    'collaboration_score': len(data['authors']),
                    'total_documents': data['publications']
                })
        
        # Sort by total documents
        top_institutions.sort(key=lambda x: x['total_documents'], reverse=True)
        
        return {
            'top_authors': top_authors[:15],
            'top_institutions': top_institutions[:15]
        }
        
    except Exception as e:
        print(f"[DEBUG] Error in extract_key_players_from_openalex: {e}")
        return {
            'top_authors': [],
            'top_institutions': []
        }


def generate_licensing_partners(institutions, abstract, title):
    """Generate potential licensing partners based on institutional analysis."""
    licensing_partners = []
    
    # Keywords to identify industry vs academia
    industry_keywords = ['corp', 'inc', 'ltd', 'company', 'technologies', 'systems', 'solutions', 'pharmaceuticals', 'biotech', 'microsoft', 'google', 'apple', 'ibm', 'intel', 'nvidia']
    academic_keywords = ['university', 'college', 'institute', 'academy', 'school', 'research center']
    
    # Technology domain keywords for licensing potential
    tech_domains = {
        'AI/ML': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning'],
        'Biotech': ['pharmaceutical', 'biotech', 'drug discovery', 'clinical', 'medical'],
        'Energy': ['energy', 'solar', 'battery', 'renewable', 'power'],
        'Quantum': ['quantum', 'qubit', 'superposition'],
        'Cybersecurity': ['security', 'encryption', 'cryptography', 'cyber'],
        'Materials': ['materials', 'nanotechnology', 'semiconductor', 'composite']
    }
    
    # Determine tech domain from abstract and title
    text = f"{title} {abstract}".lower()
    primary_domain = 'General Technology'
    for domain, keywords in tech_domains.items():
        if any(keyword in text for keyword in keywords):
            primary_domain = domain
            break
    
    # Analyze institutions for licensing potential
    for inst in institutions[:10]:  # Top 10 institutions
        inst_name = inst['name'].lower()
        licensing_score = 0.5  # Base score
        partner_type = 'Academic Partner'
        
        # Determine if industry or academic
        if any(keyword in inst_name for keyword in industry_keywords):
            partner_type = 'Industry Partner'
            licensing_score += 0.3  # Industry partners have higher licensing potential
        elif any(keyword in inst_name for keyword in academic_keywords):
            partner_type = 'Academic Partner'
            licensing_score += 0.1
            
        # Boost score based on publication count
        if inst['publication_count'] >= 3:
            licensing_score += 0.2
        
        # Create licensing partner entry
        licensing_partners.append({
            'name': inst['name'],
            'partner_type': partner_type,
            'licensing_score': min(1.0, licensing_score),
            'publications': inst['publication_count'],
            'primary_domain': primary_domain,
            'collaboration_potential': 'High' if licensing_score > 0.7 else 'Medium' if licensing_score > 0.5 else 'Low'
        })
    
    # Sort by licensing score
    licensing_partners.sort(key=lambda x: x['licensing_score'], reverse=True)
    
    return licensing_partners[:8]  # Top 8 potential partners


def extract_key_players(patents, publications):
    """Extract key players using enhanced methods."""
    # Try to get real data from OpenAlex for publications
    key_players_data = extract_key_players_from_openalex(publications)
    
    # If we got real data, generate licensing partners
    if key_players_data['top_institutions']:
        # Pass abstract and title from calling context (will be added as parameters)
        licensing_partners = generate_licensing_partners(
            key_players_data['top_institutions'], 
            "", 
            ""
        )
        key_players_data['licensing_partners'] = licensing_partners
    else:
        key_players_data['licensing_partners'] = []
    
    return key_players_data


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
    if debug:
        print(f"[DEBUG] Starting analysis for: {title[:50]}...")
    
    results = search_logic_mill(title, abstract, debug=debug)

    patents = [r for r in results if r.get("index") == "patents"]
    publications = [r for r in results if r.get("index") == "publications"]
    
    if debug:
        print(f"[DEBUG] Logic Mill API returned {len(results)} total results")
        print(f"[DEBUG] - Patents: {len(patents)}")
        print(f"[DEBUG] - Publications: {len(publications)}")

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

    # Extract key players from the data
    key_players = extract_key_players(patents, publications)
    
    # Generate licensing partners with actual title and abstract
    if key_players['top_institutions']:
        licensing_partners = generate_licensing_partners(
            key_players['top_institutions'], 
            abstract, 
            title
        )
        key_players['licensing_partners'] = licensing_partners

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
        "resource_requirements": resource_requirements,
        "key_players": key_players,
        # Debug information
        "patents_found": len(patents),
        "publications_found": len(publications),
        "total_documents": len(results),
        "logic_mill_api_used": True
    }


def main():
    title = "Quantum ML for Drug Discovery"
    abstract = "Quantum machine learning algorithms for drug discovery optimization using variational quantum circuits"
    result = analyze_research_potential(title, abstract, debug=False)
    print(json.dumps(result, indent=2))
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
