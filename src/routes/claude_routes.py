from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from llms.claude import get_claude_response
import os

router = APIRouter()

class ClaudeRequest(BaseModel):
    prompt: str

@router.post("/")
def ask_claude(request: ClaudeRequest):
    """
    Dedicated endpoint to ask Claude.
    """
    try:
        response = get_claude_response(request.prompt)
    except Exception as e:
        response = f"Claude API error: {str(e)}"
    return {"response": response}

@router.get("/")
def claude_page():
    """
    Serve Claude HTML page.
    """
    return FileResponse(os.path.join("static", "claude.html"))
