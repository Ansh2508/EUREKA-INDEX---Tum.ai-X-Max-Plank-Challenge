from src.services.logic_mill import search_similar_patents_publications

def check_new_semantic_matches(query, last_checked):
    results = search_similar_patents_publications(query)
    new_items = [r for r in results if r.get("date","") > last_checked]
    return new_items
