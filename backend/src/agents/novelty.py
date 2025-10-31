from difflib import SequenceMatcher

def compare_with_existing_claims(abstract, claims_list):
    scores = []
    for claim in claims_list:
        score = SequenceMatcher(None, abstract, claim).ratio()
        scores.append({"claim": claim, "score": score})
    return scores

def draft_novelty_report(abstract, claims_list):
    scores = compare_with_existing_claims(abstract, claims_list)
    top_claims = sorted(scores, key=lambda x: x["score"], reverse=True)[:5]
    report = f"Novelty assessment for abstract:\n{abstract}\n\nTop similar claims:\n"
    for c in top_claims:
        report += f"- {c['claim']} (score: {c['score']:.2f})\n"
    return report
