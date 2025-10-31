def rank_results(results, key="similarity_score"):
    return sorted(results, key=lambda x: x.get(key, 0), reverse=True)

def extract_contributors(results):
    contributors = {}
    for item in results:
        for contributor in item.get("contributors", []):
            contributors[contributor] = contributors.get(contributor, 0) + 1
    return sorted(contributors.items(), key=lambda x: x[1], reverse=True)
