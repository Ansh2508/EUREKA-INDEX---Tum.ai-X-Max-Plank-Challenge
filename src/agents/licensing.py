def flag_licensing_opportunities(results, focal_group):
    flagged = []
    for item in results:
        if focal_group not in item.get("owners", []):
            flagged.append(item)
    return flagged
