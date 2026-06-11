def combine(*agents):

    total = 0
    details = []

    for a in agents:
        total += a["score"]

        if "opinion" in a:
            details.append(a["opinion"])

    return {
        "total_score": total,
        "details": details
    }