from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.analysis import analyze_research_potential
from src.routes import claude_routes
import os
from dotenv import load_dotenv

load_dotenv()
# TOKEN = os.getenv("LOGIC_MILL_API_TOKEN")
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


app = FastAPI(title="Technology Assessment API")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Claude router under /claude
app.include_router(claude_routes.router, prefix="/claude", tags=["Claude"])


class TechRequest(BaseModel):
    title: str
    abstract: str

@app.post("/analyze")
def analyze_technology(request: TechRequest):
    result = analyze_research_potential(request.title, request.abstract, debug=False)
    return result

@app.get("/")
def read_index():
    # Serve index.html from the static folder
    return FileResponse(os.path.join("static", "index.html"))
