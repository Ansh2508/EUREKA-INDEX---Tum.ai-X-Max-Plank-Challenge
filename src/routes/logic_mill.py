from fastapi import APIRouter, Query
from pydantic import BaseModel
from src.search_logic_mill import get_related_works
from src.routes.openalex import get_work

router = APIRouter()

@router.get("/related-works")
def related_works(title: str = Query(...), abstract: str = Query(...), amount: int = 25):
    """
    Returns basic info (id, API URL, title) of related works.
    """
    documents = get_related_works(title, abstract, amount=amount)
    # Each item is already a dict with 'id', 'url', 'title'
    return documents

@router.get("/related-works-all")
async def all_related_works(title: str = Query(...), abstract: str = Query(...), amount: int = 25):
    """
    Returns full OpenAlex data for each related work.
    """
    # print("HIIIIIIIIIIIIIIIIIII")
    
    related_works = get_related_works(title, abstract, amount=amount)
    print(related_works)
    
    related_works_data = []

    for work in related_works:
        data = await get_work(work)  # <-- await here
        related_works_data.append(data)

    return related_works_data


class WorkRequest(BaseModel):
    title: str
    abstract: str
@router.post("/related-works-all")
async def all_related_works(req: WorkRequest):
    """
    Returns full OpenAlex data for each related work.
    Accepts JSON body: {"title": "...", "abstract": "...", "amount": 25}
    """
    related_works = get_related_works(req.title, req.abstract, amount=10)
    
    related_works_data = []
    for work in related_works:
        data = await get_work(work)
        related_works_data.append(data)

    return related_works_data