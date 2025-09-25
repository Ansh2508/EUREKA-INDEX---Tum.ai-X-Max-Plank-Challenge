from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from analysis import analyze_research_potential
import os

app = FastAPI(title="Technology Assessment API")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

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
