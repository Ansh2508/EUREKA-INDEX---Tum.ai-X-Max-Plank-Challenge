from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import APIRouter
import httpx


router = APIRouter()


OPENALEX_BASE = "https://api.openalex.org/works"

def parse_abstract(inv_index):
    if not inv_index:
        return "No abstract available"
    # The inverted index is {word: [positions]}, reconstruct by joining words
    words = sorted(inv_index, key=lambda w: min(inv_index[w]))
    return " ".join(words)

@router.get("/id/{work_id}")
async def get_work(work_id_or_work_url: str):
    async with httpx.AsyncClient() as client:
        # Fetch main work
        try:
            if OPENALEX_BASE in work_id_or_work_url:
                url = work_id_or_work_url
            else:
                url = f"{OPENALEX_BASE}/{work_id_or_work_url}"
            
            # print("WORK ID")
            # print(url)
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            print(data)
        except Exception:
            return JSONResponse(status_code=500, content={"error": "Failed to fetch work data"})


        return data
        # # Fetch related works (citing this work)
        # try:
        #     related_resp = await client.get(f"{OPENALEX_BASE}?filter=cites:{work_id}&per-page=5")
        #     related_resp.raise_for_status()
        #     related_data = related_resp.json()
        # except Exception:
        #     related_data = {"results": []}

        # related_works = [
        #     {
        #         "id": w["id"].split("/")[-1],
        #         "title": w["title"],
        #         "url": w["id"]
        #     } for w in related_data.get("results", [])
        # ]

        # return {
        #     "id": work_id,
        #     "title": data.get("title"),
        #     "authors": [a["author"]["display_name"] for a in data.get("authorships", [])],
        #     "year": data.get("publication_year"),
        #     "abstract": parse_abstract(data.get("abstract_inverted_index")),
        #     "topics": [t["display_name"] for t in data.get("topics", [])],
        #     "landing_page": data.get("primary_location", {}).get("landing_page_url"),
        #     "related": related_works
        # }
