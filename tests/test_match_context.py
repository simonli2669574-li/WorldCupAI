from fastapi.testclient import TestClient

from main import app
from match_context import (
    build_match_context_effect,
    evaluate_team_context,
    get_group_table,
    load_group_standings,
)


client = TestClient(app)


def get_sample_group_table():

    standings = load_group_standings()

    return get_group_table("Group C", standings)


def test_third_group_match_six_point_team_has_rotation_risk():

    context = evaluate_team_context(
        "Brazil",
        get_sample_group_table(),
        3
    )

    assert context["likely_qualified"] is True
    assert context["rotation_risk"] == "high"
    assert context["xg_multiplier"] < 1


def test_third_group_match_one_point_team_must_win():

    context = evaluate_team_context(
        "Haiti",
        get_sample_group_table(),
        3
    )

    assert context["must_win"] is True
    assert context["attacking_urgency"] == "high"
    assert context["xg_multiplier"] > 1


def test_third_group_match_four_point_team_draw_is_enough():

    context = evaluate_team_context(
        "Morocco",
        get_sample_group_table(),
        3
    )

    assert context["draw_is_enough"] is True
    assert context["xg_multiplier"] < 1


def test_third_group_match_three_point_team_has_pressure():

    context = evaluate_team_context(
        "Scotland",
        get_sample_group_table(),
        3
    )

    assert context["motivation_level"] == "high"
    assert context["xg_multiplier"] > 1


def test_predict_team_auto_context_false_returns_disabled_context():

    payload = {
        "home_team": "Brazil",
        "away_team": "Haiti",
        "group": "Group C",
        "group_match_number": 3,
        "auto_context": False,
        "stadium_key": "Mexico City",
        "weather_mode": "manual",
    }

    response = client.post("/predict_team", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["context_effect"]["enabled"] is False


def test_predict_team_returns_enabled_context_effect():

    payload = {
        "home_team": "Brazil",
        "away_team": "Haiti",
        "group": "Group C",
        "group_match_number": 3,
        "stadium_key": "Mexico City",
        "weather_mode": "manual",
    }

    response = client.post("/predict_team", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "context_effect" in data
    assert data["context_effect"]["enabled"] is True
    assert data["context_effect"]["home"]["team"] == "Brazil"
    assert data["context_effect"]["away"]["team"] == "Haiti"


def test_build_match_context_effect_handles_unknown_group():

    context_effect = build_match_context_effect(
        "Brazil",
        "Japan",
        "Unknown Group",
        3
    )

    assert context_effect["enabled"] is False
