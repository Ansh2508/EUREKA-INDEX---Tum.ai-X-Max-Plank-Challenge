from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.analysis import analyze_research_potential
from src.routes import claude_routes,llm_routes,openalex, related_works
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

# Include Claude router under /claude
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

@app.get("/")
def read_index():
    # Serve index.html from the static folder
    return FileResponse(os.path.join("static", "index.html"))
