def calculate_market_edges(
    home_prob,
    draw_prob,
    away_prob,
    home_odds,
    draw_odds,
    away_odds
):

    home_implied = 1 / home_odds
    draw_implied = 1 / draw_odds
    away_implied = 1 / away_odds

    total_implied = (
        home_implied
        + draw_implied
        + away_implied
    )

    def build_edge(name, model_prob, odds, implied_prob):

        edge = model_prob - implied_prob

        return {
            "market": name,
            "odds": odds,
            "model_prob": round(model_prob * 100, 2),
            "implied_prob": round(implied_prob * 100, 2),
            "edge": round(edge * 100, 2),
            "value": edge > 0
        }

    return {
        "home": build_edge(
            "主胜",
            home_prob,
            home_odds,
            home_implied
        ),

        "draw": build_edge(
            "平局",
            draw_prob,
            draw_odds,
            draw_implied
        ),

        "away": build_edge(
            "客胜",
            away_prob,
            away_odds,
            away_implied
        ),

        "bookmaker_margin": round(
            (total_implied - 1) * 100,
            2
        )
    }