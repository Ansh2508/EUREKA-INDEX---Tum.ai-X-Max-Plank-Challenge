from fastapi import APIRouter
from src.agents.aggregation import rank_results, extract_contributors
from src.agents.novelty import draft_novelty_report

router = APIRouter()

@router.post("/results")
def get_results(query: str):
    # Call services and agents here
    results = []  # Replace with actual service calls
    ranked = rank_results(results)
    contributors = extract_contributors(results)
    novelty_report = draft_novelty_report(query, [r.get("claim","") for r in results])
    return {
        "ranked_results": ranked,
        "contributors": contributors,
        "novelty_report": novelty_report
    }
