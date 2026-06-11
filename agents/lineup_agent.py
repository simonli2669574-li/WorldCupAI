def analyze_lineup(
    missing_starters,
    star_player_out
):

    score = 0
    opinions = []

    score -= missing_starters * 2

    if missing_starters > 0:
        opinions.append(
            f"缺少{missing_starters}名主力"
        )

    if star_player_out == 1:
        score -= 5
        opinions.append(
            "核心球员缺席"
        )

    return {
        "score": score,
        "opinion": ", ".join(opinions)
    }