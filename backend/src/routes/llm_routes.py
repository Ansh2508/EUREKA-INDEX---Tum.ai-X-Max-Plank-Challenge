from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.llms.groq import get_groq_response

from src.llms.claude import get_claude_response
import os

router = APIRouter()

# Supported LLM providers
LLM_PROVIDERS = {
    "groq": get_groq_response,
    "claude": get_claude_response
}

class LLMRequest(BaseModel):
    provider: str  # "groq", "openrouter", "claude"
    prompt: str

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

@router.get("/")
def llm_page():
    """
    Serve LLM HTML page (frontend will have dropdown + input box).
    """
    return FileResponse(os.path.join("static", "llm.html"))
