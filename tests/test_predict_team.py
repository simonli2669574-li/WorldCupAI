from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_predict_team_manual_weather():
    payload = {
        "home_team": "Argentina",
        "away_team": "Japan",
        "stadium_key": "Mexico City",
        "weather_mode": "manual",
        "open_home_odds": 1.9,
        "current_home_odds": 1.75,
        "open_draw_odds": 3.6,
        "current_draw_odds": 3.8,
        "open_away_odds": 4.8,
        "current_away_odds": 5.2,
        "missing_starters": 2,
        "star_player_out": 1,
        "injury_level": 2,
        "bankroll": 10000,
        "max_bet_percent": 3,
        "high_risk_bet_percent": 1,
        "temperature": 22,
        "humidity": 50,
        "wind_speed": 10,
        "rain": 0,
    }

    response = client.post("/predict_team", json=payload)

    assert response.status_code == 200

    data = response.json()
    for field in [
        "home_team",
        "away_team",
        "stadium",
        "weather",
        "market_edges",
        "kelly",
        "risk_control",
        "summary",
        "report",
    ]:
        assert field in data

    assert "style_effect" in data["weather"]
