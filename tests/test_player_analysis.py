from fastapi.testclient import TestClient

from main import app
from player_analysis import (
    analyze_team_players,
    apply_player_xg_modifier,
    build_player_analysis,
    load_players,
)


client = TestClient(app)


def test_load_players_returns_group_l_profiles():

    players = load_players()

    assert "England" in players
    assert "Croatia" in players
    assert "Ghana" in players
    assert "Panama" in players


def test_analyze_team_players_available_for_england_and_croatia():

    england = analyze_team_players("England")
    croatia = analyze_team_players("Croatia")

    assert england["available"] is True
    assert croatia["available"] is True
    assert england["key_players"]
    assert croatia["key_players"]


def test_build_player_analysis_enabled_for_group_l_matchups():

    england_croatia = build_player_analysis("England", "Croatia")
    england_ghana = build_player_analysis("England", "Ghana")

    assert england_croatia["enabled"] is True
    assert england_ghana["enabled"] is True


def test_apply_player_xg_modifier_returns_effect_for_available_profiles():

    player_analysis = build_player_analysis("Ghana", "Panama")

    adjusted_home_xg, adjusted_away_xg, player_xg_effect = (
        apply_player_xg_modifier(1.1, 0.9, player_analysis)
    )

    assert player_xg_effect["enabled"] is True
    assert player_xg_effect["home"]["team"] == "Ghana"
    assert player_xg_effect["away"]["team"] == "Panama"
    assert -0.10 <= player_xg_effect["home"]["xg_adjustment"] <= 0.25
    assert -0.10 <= player_xg_effect["away"]["xg_adjustment"] <= 0.25
    assert adjusted_home_xg >= 0.2
    assert adjusted_away_xg >= 0.2


def test_apply_player_xg_modifier_enforces_minimum_adjusted_xg():

    player_analysis = {
        "enabled": True,
        "home": {
            "team": "Home",
            "attacking_threat": 0,
            "wide_threat": 0,
            "defensive_age_risk": 0,
            "squad_experience": 100,
        },
        "away": {
            "team": "Away",
            "attacking_threat": 0,
            "wide_threat": 0,
            "defensive_age_risk": 0,
            "squad_experience": 100,
        },
    }

    adjusted_home_xg, adjusted_away_xg, player_xg_effect = (
        apply_player_xg_modifier(0.21, 0.21, player_analysis)
    )

    assert player_xg_effect["enabled"] is True
    assert adjusted_home_xg >= 0.2
    assert adjusted_away_xg >= 0.2


def test_predict_team_returns_player_analysis_and_player_xg_effect():

    payload = {
        "home_team": "Ghana",
        "away_team": "Panama",
        "stadium_key": "Mexico City",
        "weather_mode": "manual",
    }

    response = client.post("/predict_team", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "player_analysis" in data
    assert "player_xg_effect" in data
    assert data["player_analysis"]["enabled"] is True
    assert data["player_xg_effect"]["enabled"] is True


def test_predict_team_england_croatia_returns_player_analysis_and_xg_effect():

    payload = {
        "home_team": "England",
        "away_team": "Croatia",
        "stadium_key": "Mexico City",
        "weather_mode": "manual",
    }

    response = client.post("/predict_team", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "player_analysis" in data
    assert "player_xg_effect" in data
    assert data["player_analysis"]["enabled"] is True
    assert data["player_xg_effect"]["enabled"] is True
