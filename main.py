from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.analysis import analyze_research_potential
from src.routes import claude_routes, llm_routes, openalex, related_works
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Technology Assessment API")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include existing routers
app.include_router(claude_routes.router, prefix="/claude", tags=["Claude"])
app.include_router(llm_routes.router, prefix="/llm")
app.include_router(openalex.router, prefix="/openalex")
app.include_router(related_works.router)

class TechRequest(BaseModel):
    title: str
    abstract: str

@app.post("/analyze")
def analyze_technology(request: TechRequest):
    result = analyze_research_potential(request.title, request.abstract, debug=False)
    return result

# Enhanced endpoints with mock implementations for now
@app.post("/semantic-alerts")
async def get_semantic_alerts(request: TechRequest):
    """
    Mock implementation for semantic patent alerts
    """
    return {
        "alert_count": 3,
        "alerts": [
            {
                "id": "US123456789",
                "title": "Advanced Machine Learning System for Data Processing",
                "similarity_score": 0.85,
                "document_type": "patent",
                "publication_date": "2024-01-15",
                "authors": ["John Doe", "Jane Smith"],
                "institutions": ["TechCorp Inc."],
                "abstract": "A system for processing large datasets using machine learning algorithms...",
                "url": "https://patents.uspto.gov/patent/US123456789",
                "alert_reason": "High semantic similarity (0.850) to research"
            },
            {
                "id": "US987654321",
                "title": "Neural Network Architecture for Pattern Recognition",
                "similarity_score": 0.78,
                "document_type": "patent",
                "publication_date": "2024-02-01",
                "authors": ["Alice Johnson"],
                "institutions": ["Innovation Labs"],
                "abstract": "Novel neural network design for improved pattern recognition capabilities...",
                "url": "https://patents.uspto.gov/patent/US987654321",
                "alert_reason": "High semantic similarity (0.780) to research"
            }
        ],
        "threshold_used": 0.75,
        "lookback_period": 30
    }

@app.post("/competitor-discovery")
async def discover_competitors_collaborators(request: TechRequest):
    """
    Mock implementation for competitor discovery
    """
    return {
        "domain_analysis": {
            "research_focus": request.title,
            "domain": "Auto-detected from research"
        },
        "key_players": {
            "top_authors": [
                {
                    "name": "Dr. Sarah Wilson",
                    "entity_type": "author",
                    "publication_count": 45,
                    "patent_count": 12,
                    "collaboration_score": 0.8,
                    "recent_activity": 8,
                    "key_topics": ["Machine Learning", "AI", "Data Science"],
                    "geographic_location": "MIT, USA"
                },
                {
                    "name": "Prof. Michael Chen",
                    "entity_type": "author", 
                    "publication_count": 38,
                    "patent_count": 15,
                    "collaboration_score": 0.75,
                    "recent_activity": 6,
                    "key_topics": ["Neural Networks", "Deep Learning"],
                    "geographic_location": "Stanford, USA"
                }
            ],
            "top_institutions": [
                {
                    "name": "MIT Computer Science",
                    "entity_type": "institution",
                    "publication_count": 120,
                    "patent_count": 45,
                    "collaboration_score": 0.9,
                    "recent_activity": 25,
                    "key_topics": ["AI", "Machine Learning", "Robotics"],
                    "geographic_location": "Cambridge, MA, USA"
                }
            ],
            "collaboration_clusters": [
                {
                    "cluster_id": 1,
                    "members": ["Dr. Sarah Wilson", "Prof. Michael Chen", "Dr. Lisa Park"],
                    "size": 3,
                    "internal_connections": 5,
                    "key_topics": ["Machine Learning", "AI Ethics"]
                }
            ]
        },
        "analysis_summary": {
            "top_authors_count": 2,
            "top_institutions_count": 1,
            "collaboration_clusters": 1
        }
    }

@app.post("/licensing-opportunities")
async def find_licensing_opportunities(request: TechRequest):
    """
    Mock implementation for licensing opportunities
    """
    return {
        "focal_group": "Your Research Group",
        "research_domain": request.title,
        "opportunity_count": 2,
        "opportunities": [
            {
                "entity_name": "TechCorp Inc.",
                "entity_type": "company",
                "opportunity_type": "licensing_out",
                "relevance_score": 0.85,
                "patent_portfolio": [],
                "technology_gaps": ["Manufacturing scale-up", "Commercial deployment"],
                "contact_information": {"email": "licensing@techcorp.com"},
                "market_position": "Market Leader",
                "licensing_history": [],
                "estimated_value": "High ($1M+)"
            }
        ],
        "summary": {
            "high_value_opportunities": 1,
            "licensing_out_opportunities": 1,
            "collaboration_opportunities": 0
        }
    }

@app.post("/novelty-assessment")
async def assess_novelty(request: TechRequest):
    """
    Mock implementation for novelty assessment
    """
    return {
        "research_title": request.title,
        "assessment": {
            "overall_novelty_score": 0.75,
            "novelty_category": "Moderately Novel",
            "similar_patents": [],
            "similar_publications": [],
            "key_differences": [
                "Novel technical aspects: quantum algorithms, optimization techniques",
                "Unique approach to data processing compared to existing solutions"
            ],
            "patentability_indicators": {
                "novelty_score": 0.75,
                "claim_strength": "Strong",
                "claim_count": 0,
                "prior_art_issues": [],
                "patentability_likelihood": "Moderate"
            },
            "prior_art_analysis": {
                "total_similar_patents": 5,
                "total_similar_publications": 8,
                "highest_patent_similarity": 0.65,
                "highest_publication_similarity": 0.72,
                "prior_art_density": 13,
                "key_prior_art": []
            },
            "recommendations": [
                "Moderate novelty - consider strengthening claims",
                "Conduct detailed prior art search focusing on top similar patents"
            ]
        },
        "summary": {
            "novelty_level": "Moderately Novel",
            "patentability_likelihood": "Moderate",
            "key_concerns": 0,
            "recommendations_count": 2
        }
    }

@app.post("/comprehensive-analysis")
async def comprehensive_analysis(request: TechRequest):
    """
    Run comprehensive analysis including all enhanced features
    """
    basic_analysis = analyze_research_potential(request.title, request.abstract, debug=False)
    
    # Mock enhanced data
    return {
        "research_title": request.title,
        "timestamp": "2024-01-01T00:00:00Z",
        "basic_analysis": basic_analysis,
        "semantic_alerts": {
            "count": 3,
            "top_alerts": [
                {
                    "id": "US123456789",
                    "title": "Advanced Machine Learning System",
                    "similarity_score": 0.85,
                    "document_type": "patent",
                    "alert_reason": "High semantic similarity"
                }
            ]
        },
        "key_players": {
            "top_authors": [
                {"name": "Dr. Sarah Wilson", "publication_count": 45, "patent_count": 12}
            ],
            "top_institutions": [
                {"name": "MIT Computer Science", "publication_count": 120, "patent_count": 45}
            ],
            "collaboration_clusters": [
                {"cluster_id": 1, "size": 3, "key_topics": ["Machine Learning", "AI"]}
            ]
        },
        "licensing_opportunities": {
            "count": 2,
            "top_opportunities": [
                {
                    "entity_name": "TechCorp Inc.",
                    "opportunity_type": "licensing_out",
                    "relevance_score": 0.85,
                    "estimated_value": "High ($1M+)"
                }
            ]
        },
        "executive_summary": {
            "market_potential": basic_analysis["overall_assessment"]["market_potential_score"],
            "novelty_indicators": 3,
            "competitive_landscape": 3,
            "licensing_potential": 2
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
