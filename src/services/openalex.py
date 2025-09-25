import requests

def fetch_publication_metadata(publication_id):
    url = f"https://api.openalex.org/works/{publication_id}"
    response = requests.get(url)
    return response.json()
