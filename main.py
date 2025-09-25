from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.analysis import analyze_research_potential
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Technology Assessment API")

# Import routes with error handling for deployment
try:
    from src.routes import claude_routes, llm_routes
    app.include_router(claude_routes.router, prefix="/claude", tags=["Claude"])
    app.include_router(llm_routes.router, prefix="/llm")
except ImportError as e:
    print(f"Warning: Could not import some routes: {e}")

try:
    from src.routes import openalex, related_works
    app.include_router(openalex.router, prefix="/openalex")
    app.include_router(related_works.router)
except ImportError as e:
    print(f"Warning: Could not import additional routes: {e}")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")



class TechRequest(BaseModel):
    title: str
    abstract: str

@app.post("/analyze")
def analyze_technology(request: TechRequest):
    result = analyze_research_potential(request.title, request.abstract, debug=False)
    return result

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Technology Assessment API is running"}

@app.get("/")
def read_index():
    # Serve index.html from the static folder
    return FileResponse(os.path.join("static", "index.html"))
