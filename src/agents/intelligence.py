import networkx as nx
import matplotlib.pyplot as plt

def get_key_players(data):
    authors = {}
    institutions = {}
    for item in data:
        for auth in item.get("authorships", []):
            author = auth["author"]["display_name"]
            authors[author] = authors.get(author, 0) + 1
            for inst in auth.get("institutions", []):
                inst_name = inst["display_name"]
                institutions[inst_name] = institutions.get(inst_name, 0) + 1
    top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
    top_institutions = sorted(institutions.items(), key=lambda x: x[1], reverse=True)
    return top_authors, top_institutions

def find_emerging_trends(data):
    topic_counts = {}
    for item in data:
        for topic in item.get("topics", []):
            name = topic["display_name"]
            topic_counts[name] = topic_counts.get(name, 0) + 1
    underexplored = [t for t in topic_counts if topic_counts[t] < 5]
    return topic_counts, underexplored

def match_to_patents(data, patent_db):
    matches = []
    for item in data:
        for auth in item.get("authorships", []):
            author = auth["author"]["display_name"]
            for patent in patent_db:
                if author in patent.get("inventors", []):
                    matches.append((item["title"], patent["title"]))
    return matches

def prioritize_opportunities(data, topic_counts, patent_db):
    opportunities = []
    for item in data:
        topic_names = [t["display_name"] for t in item.get("topics",[])]
        citations = item.get("cited_by_count", 0)
        for topic in topic_names:
            patent_count = sum(1 for p in patent_db if topic in p.get("classifications", []))
            if patent_count < 2 and citations > 100:
                opportunities.append((item["title"], topic, citations))
    return opportunities

def visualize_collaborations(data):
    G = nx.Graph()
    for item in data:
        authors = [a["author"]["display_name"] for a in item.get("authorships",[])]
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                G.add_edge(authors[i], authors[j])
    nx.draw(G, with_labels=True)
    plt.show()
