import os
import requests

LOGIC_MILL_API_URL = "https://api.logicmill.com/search"
API_TOKEN = os.getenv("LOGIC_MILL_API_TOKEN")

def search_similar_patents_publications(query):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {"query": query}
    response = requests.post(LOGIC_MILL_API_URL, json=payload, headers=headers)
    return response.json()
