import json

from fastapi.testclient import TestClient

from agents.team_agent import get_team, resolve_team_name
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


def test_teams_json_has_48_valid_teams():
    allowed_styles = {
        "high_press",
        "possession",
        "counter",
        "physical",
        "balanced",
    }
    required_fields = {
        "attack",
        "defense",
        "elo",
        "formation",
        "style",
    }

    with open("data/teams.json", encoding="utf-8") as file:
        teams = json.load(file)

    assert len(teams) == 48

    for team in teams.values():
        assert required_fields.issubset(team)
        assert team["style"] in allowed_styles


def test_get_team_supports_common_aliases():
    assert get_team("USA") is not None
    assert get_team("USMNT") is not None
    assert get_team("United States of America") is not None
    assert get_team("Korea Republic") is not None
    assert get_team("South Korea") is not None
    assert get_team("Czech Republic") is not None
    assert get_team("Czechia") is not None
    assert get_team("Holland") is not None
    assert get_team("Not A Real Team") is None


def test_resolve_team_name_supports_common_aliases():
    assert resolve_team_name("USA") == "United States"
    assert resolve_team_name("USMNT") == "United States"
    assert resolve_team_name("Czech Republic") == "Czechia"
    assert resolve_team_name("Not A Real Team") is None


def test_predict_team_returns_standard_team_name_for_alias():
    payload = {
        "home_team": "USA",
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

    assert "error" not in data
    assert data["home_team"] == "United States"
    assert data["input_teams"]["home_team"] == "USA"


def test_teams_api_returns_all_teams():
    response = client.get("/teams")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 48
    assert "name" in data[0]
    assert "style" in data[0]
    assert "formation" in data[0]


def test_teams_search_api_supports_aliases():
    response = client.get("/teams/search", params={"q": "usa"})

    assert response.status_code == 200

    data = response.json()

    assert data[0]["name"] == "United States"
    assert data[0]["matched_by"] == "alias"

    response = client.get("/teams/search", params={"q": "USMNT"})

    assert response.status_code == 200

    data = response.json()

    assert data[0]["name"] == "United States"
    assert data[0]["matched_by"] == "alias"


def test_teams_search_api_returns_empty_for_no_match_or_blank_query():
    response = client.get("/teams/search", params={"q": "notarealteam"})

    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/teams/search", params={"q": "   "})

    assert response.status_code == 200
    assert response.json() == []
