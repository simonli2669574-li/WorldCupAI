def calculate_kelly(prob, odds, bankroll, market):

    b = odds - 1

    raw_kelly = ((prob * b) - (1 - prob)) / b

    fractional_kelly = raw_kelly * 0.5

    if fractional_kelly <= 0:
        return {
            "market": market,
            "odds": odds,
            "model_prob": round(prob * 100, 2),
            "raw_kelly": round(raw_kelly * 100, 2),
            "fractional_kelly": 0,
            "suggested_bet": 0,
            "advice": f"不建议投注{market}"
        }

    suggested_bet = bankroll * fractional_kelly

    expected_value = prob * (odds - 1) - (1 - prob)

    return {
        "market": market,
        "odds": odds,
        "model_prob": round(prob * 100, 2),
        "raw_kelly": round(raw_kelly * 100, 2),
        "fractional_kelly": round(fractional_kelly * 100, 2),
        "suggested_bet": round(suggested_bet, 2),
        "expected_value": round(expected_value, 4),
        "advice": f"Value Bet，建议小注{market}"
    }


def calculate_three_way_kelly(
    home_prob,
    draw_prob,
    away_prob,
    home_odds,
    draw_odds,
    away_odds,
    bankroll
):

    home_kelly = calculate_kelly(
        home_prob,
        home_odds,
        bankroll,
        "主胜"
    )

    draw_kelly = calculate_kelly(
        draw_prob,
        draw_odds,
        bankroll,
        "平局"
    )

    away_kelly = calculate_kelly(
        away_prob,
        away_odds,
        bankroll,
        "客胜"
    )

    candidates = [
        ("主胜", home_kelly),
        ("平局", draw_kelly),
        ("客胜", away_kelly)
    ]

    best_name = "无推荐"
    best_value = 0

    for name, result in candidates:
        if result["fractional_kelly"] > best_value:
            best_value = result["fractional_kelly"]
            best_name = name

    return {
        "home": home_kelly,
        "draw": draw_kelly,
        "away": away_kelly,
        "best_value": best_name
    }