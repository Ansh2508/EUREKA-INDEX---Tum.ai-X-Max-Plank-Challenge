import requests

def fetch_patent_metadata(patent_id):
    url = f"https://worldwide.espacenet.com/patent/search/fetch?patentId={patent_id}"
    response = requests.get(url)
    return response.json()
