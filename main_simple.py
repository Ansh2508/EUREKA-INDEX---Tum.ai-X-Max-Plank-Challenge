from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Technology Assessment API")

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

class TechRequest(BaseModel):
    title: str
    abstract: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Technology Assessment API is running"}

@app.post("/analyze")
def analyze_technology(request: TechRequest):
    # Simple mock response for deployment testing
    return {
        "overall_assessment": {
            "market_potential_score": 7.5,
            "investment_recommendation": "BUY - Good potential, conduct deeper due diligence",
            "risk_level": "MEDIUM RISK"
        },
        "message": "API is working! Full analysis coming soon."
    }

@app.get("/")
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
