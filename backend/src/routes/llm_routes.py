from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.llms.claude import get_claude_response
from src.llms.huggingface import get_huggingface_response
from src.llms.google_ai import get_google_ai_response, get_patent_analysis, get_technical_innovation_analysis, get_prior_art_search_strategy
from src.llms.grok import get_grok_response
import os

router = APIRouter()

# Supported LLM providers
LLM_PROVIDERS = {
    "claude": get_claude_response,
    "huggingface": get_huggingface_response,
    "google_ai": get_google_ai_response,
    "grok": get_grok_response
}

class LLMRequest(BaseModel):
    provider: str  # "claude", "huggingface", "google_ai", "grok"
    prompt: str

class PatentAnalysisRequest(BaseModel):
    patent_text: str
    analysis_type: str = "novelty"  # novelty, claims, landscape, infringement

class TechnicalAnalysisRequest(BaseModel):
    technology_description: str

class PriorArtSearchRequest(BaseModel):
    invention_summary: str

@router.get("/providers")
def list_providers():
    """
    Returns all available LLM providers for the frontend dropdown.
    """
    return {"providers": list(LLM_PROVIDERS.keys())}

@router.post("/ask")
def ask_llm(request: LLMRequest):
    """
    Send a prompt to the selected LLM provider.
    """
    provider = request.provider.lower()
    if provider not in LLM_PROVIDERS:
        return {"error": f"Provider '{provider}' not supported. Choose from {list(LLM_PROVIDERS.keys())}"}
    
    try:
        response = LLM_PROVIDERS[provider](request.prompt)
    except Exception as e:
        response = f"{provider.capitalize()} API error: {str(e)}"
    
    return {"response": response}

@router.post("/patent-analysis")
def analyze_patent(request: PatentAnalysisRequest):
    """
    Specialized patent analysis using enhanced Google AI
    """
    try:
        response = get_patent_analysis(request.patent_text, request.analysis_type)
        return {"response": response, "analysis_type": request.analysis_type}
    except Exception as e:
        return {"error": f"Patent analysis error: {str(e)}"}

@router.post("/technical-analysis")
def analyze_technology(request: TechnicalAnalysisRequest):
    """
    Comprehensive technical innovation analysis
    """
    try:
        response = get_technical_innovation_analysis(request.technology_description)
        return {"response": response}
    except Exception as e:
        return {"error": f"Technical analysis error: {str(e)}"}

@router.post("/prior-art-search")
def generate_search_strategy(request: PriorArtSearchRequest):
    """
    Generate comprehensive prior art search strategy
    """
    try:
        response = get_prior_art_search_strategy(request.invention_summary)
        return {"response": response}
    except Exception as e:
        return {"error": f"Search strategy error: {str(e)}"}

@router.get("/")
def llm_page():
    """
    Serve LLM HTML page (frontend will have dropdown + input box).
    """
    return FileResponse(os.path.join("static", "llm.html"))
