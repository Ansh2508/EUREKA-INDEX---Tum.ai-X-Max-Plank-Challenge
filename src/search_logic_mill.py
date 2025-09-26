import os
import json
from dotenv import load_dotenv
from urllib3.util import Retry
from requests import Session
from requests.adapters import HTTPAdapter
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv("LOGIC_MILL_API_TOKEN")

if not TOKEN:
    raise EnvironmentError("LOGIC_MILL_API_TOKEN not found in .env file")

# Establish session for robust connection
s = Session()
retries = Retry(total=5, backoff_factor=0.1,
                status_forcelist=[500, 501, 502, 503, 504, 524])
s.mount('https://', HTTPAdapter(max_retries=retries))

# API settings
URL = "https://api.logic-mill.net/api/v1/graphql/"
HEADERS = {
    "content-type": "application/json",
    "Authorization": f"Bearer {TOKEN}",
}

# GraphQL query template
QUERY = """
query embedDocumentAndSimilaritySearch($data: [EncodeDocumentPart], $indices: [String], $amount: Int, $model: String!) {
  encodeDocumentAndSimilaritySearch(
    data: $data
    indices: $indices
    amount: $amount
    model: $model
  ) {
    id
    score
    index
    document {
      title
      url
      PatspecterEmbedding
    }
  }
}
"""
def search_logic_mill(
    title: str,
    abstract: str,
    model: str = "patspecter",
    amount: int = 25,
    indices: list = None,
    debug: bool = False
):
    """
    Perform a similarity search against the Logic-Mill API.

    Returns:
        list: List of document dictionaries, each containing:
            id, score, index, title, url, PatspecterEmbedding
    """
    if indices is None:
        indices = ["patents", "publications"]  # Include both patents and publications

    variables = {
        "model": model,
        "data": [
            {"key": "title", "value": title},
            {"key": "abstract", "value": abstract},
        ],
        "amount": amount,
        "indices": indices,
    }

    if debug:
        print(f"[DEBUG] Searching Logic Mill API with indices: {indices}")
        print(f"[DEBUG] Amount: {amount}, Model: {model}")

    r = s.post(URL, headers=HEADERS, json={"query": QUERY, "variables": variables})

    if r.status_code != 200:
        error_msg = f"Logic Mill API Error {r.status_code}: {r.text}"
        if debug:
            print(f"[DEBUG] {error_msg}")
        raise RuntimeError(error_msg)

    response = r.json()
    
    if debug:
        print(f"[DEBUG] Logic Mill API response status: {r.status_code}")
        print(f"[DEBUG] Response keys: {response.keys() if response else 'None'}")

    # Extract documents
    results = response.get("data", {}).get("encodeDocumentAndSimilaritySearch", [])
    documents = []
    patents_count = 0
    publications_count = 0
    
    for item in results:
        doc = item.get("document", {})
        if doc:
            doc_index = item.get("index")
            documents.append({
                "id": item.get("id"),
                "score": item.get("score"),
                "index": doc_index,
                "title": doc.get("title"),
                "url": doc.get("url"),
                "PatspecterEmbedding": doc.get("PatspecterEmbedding"),
                "year": doc.get("year", 2020),  # Default year for calculations
                "citations": doc.get("citations", 0),  # Default citations
            })
            
            if doc_index == "patents":
                patents_count += 1
            elif doc_index == "publications":
                publications_count += 1

    if debug:
        print(f"[DEBUG] Found {len(documents)} total documents:")
        print(f"[DEBUG] - Patents: {patents_count}")
        print(f"[DEBUG] - Publications: {publications_count}")
        
        # Save JSON output
        filename = f"debug_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        print(f"[DEBUG] Extracted documents saved to {filename}")
        
        # Show sample documents
        if documents:
            print(f"[DEBUG] Sample document: {documents[0]}")

    return documents  # ✅ Return list of dicts

def get_ids_and_urls(title: str, abstract: str, model: str = "patspecter", amount: int = 25, indices: list = None, debug: bool = False):
    """
    Wrapper around search_logic_mill to return only document IDs and API URLs.
    
    Ensures each URL ends with the document's ID.
    
    Returns:
        list of dicts: Each dict contains 'id', 'url' (API endpoint), and 'title'.
    """
    documents = search_logic_mill(title, abstract, model, amount, indices, debug)
    result = []
    for doc in documents:
        # Always construct the API URL using the id
        api_url = f"https://api.openalex.org/works/{doc['id']}"
        result.append({
            "id": doc["id"],
            "url": api_url,
            "title": doc["title"]
        })
    return result


def get_related_works(title: str, abstract: str, model: str = "patspecter", amount: int = 25, indices: list = None, debug: bool = False):
    """
    Wrapper around search_logic_mill to return only document IDs and API URLs.
    
    Ensures each URL ends with the document's ID.
    
    Returns:
        list of dicts: Each dict contains 'id', 'url' (API endpoint), and 'title'.
    """
    documents = search_logic_mill(title, abstract, model, amount, indices, debug)
    result = []
    for doc in documents:
        # Always construct the API URL using the id
        api_url = f"https://api.openalex.org/works/{doc['id']}"
        result.append(api_url)
    return result




# def get_ids_and_urls(title: str, abstract: str, model: str = "patspecter", amount: int = 25, indices: list = None, debug: bool = False):
#     """
#     Wrapper around search_logic_mill to return only document IDs and URLs.
    
#     Returns:
#         list of dicts: Each dict contains 'id' and 'url' only.
#     """
#     documents = search_logic_mill(title, abstract, model, amount, indices, debug)
#     return [{"id": doc["id"], "url": doc["url"],"title":doc["title"]} for doc in documents]


# # Example usage
# if __name__ == "__main__":
#     result = search_logic_mill(
#         title="Airbags",
#         abstract="Airbags are one of the most important safety gears...",
#         debug=True
#     )
#     print(json.dumps(result, indent=2))
# Example usage
if __name__ == "__main__":
    urls_and_ids = get_ids_and_urls(
        title="Airbags",
        abstract="Airbags are one of the most important safety gears...",
        debug=True
    )
    print(json.dumps(urls_and_ids, indent=2))