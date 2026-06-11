def analyze_tactics(formation):

    formation = formation.strip()

    score = 0
    opinion = "阵型中性"

    if formation == "433":
        score = 2
        opinion = "进攻型433"

    elif formation == "4231":
        score = 1
        opinion = "平衡4231"

    elif formation == "352":
        score = 1
        opinion = "双前锋压迫"

    elif formation == "541":
        score = -2
        opinion = "防守型541"

    elif formation == "532":
        score = -1
        opinion = "偏防守532"

    return {
        "score": score,
        "opinion": opinion
    }