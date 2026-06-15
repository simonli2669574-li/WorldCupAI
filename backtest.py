import json

from schemas import TeamMatchInput


def load_backtest_matches(path="data/backtest_matches.json"):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_actual_winner(home_goals, away_goals):

    if home_goals > away_goals:
        return "home"

    if home_goals < away_goals:
        return "away"

    return "draw"


def get_predicted_winner(prediction):

    outcomes = {
        "home": prediction["home_win"],
        "draw": prediction["draw"],
        "away": prediction["away_win"]
    }

    return max(outcomes, key=outcomes.get)


def evaluate_match(sample):

    prediction_input = {
        key: value
        for key, value in sample.items()
        if key not in {
            "actual_home_goals",
            "actual_away_goals"
        }
    }

    match = TeamMatchInput(**prediction_input)

    import main

    prediction = main.run_team_prediction(match)

    actual_home_goals = sample["actual_home_goals"]
    actual_away_goals = sample["actual_away_goals"]
    actual_score = f"{actual_home_goals}-{actual_away_goals}"

    actual_winner = get_actual_winner(
        actual_home_goals,
        actual_away_goals
    )
    predicted_winner = get_predicted_winner(prediction)

    top_scores = prediction["top_scores"]
    top_score_values = [
        item["score"]
        for item in top_scores
    ]

    actual_btts = actual_home_goals > 0 and actual_away_goals > 0
    predicted_btts = prediction["markets"]["BTTS"] >= 50

    actual_over25 = actual_home_goals + actual_away_goals > 2.5
    predicted_over25 = prediction["markets"]["Over2.5"] >= 50

    return {
        "home_team": sample["home_team"],
        "away_team": sample["away_team"],
        "actual_score": actual_score,
        "actual_winner": actual_winner,
        "predicted_winner": predicted_winner,
        "winner_hit": predicted_winner == actual_winner,
        "top_score_hit": actual_score in top_score_values,
        "actual_btts": actual_btts,
        "predicted_btts": predicted_btts,
        "btts_hit": predicted_btts == actual_btts,
        "actual_over25": actual_over25,
        "predicted_over25": predicted_over25,
        "over25_hit": predicted_over25 == actual_over25,
        "top_scores": top_scores
    }


def calculate_accuracy(details, field):

    if len(details) == 0:
        return 0

    hits = sum(
        1
        for detail in details
        if detail[field]
    )

    return round(hits / len(details) * 100, 2)


def run_backtest():

    samples = load_backtest_matches()

    details = [
        evaluate_match(sample)
        for sample in samples
    ]

    return {
        "summary": {
            "matches_tested": len(details),
            "winner_accuracy": calculate_accuracy(details, "winner_hit"),
            "top_score_hit_rate": calculate_accuracy(details, "top_score_hit"),
            "btts_accuracy": calculate_accuracy(details, "btts_hit"),
            "over25_accuracy": calculate_accuracy(details, "over25_hit")
        },
        "details": details
    }
