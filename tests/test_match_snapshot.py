from fastapi.testclient import TestClient

from main import app
from match_snapshot import build_data_realism, load_match_snapshots


client = TestClient(app)


def test_load_match_snapshots_returns_ghana_vs_panama():
    snapshots = load_match_snapshots()

    assert any(
        snapshot.get("match") == "Ghana vs Panama"
        for snapshot in snapshots
    )


def test_build_data_realism_returns_available_for_ghana_vs_panama():
    data_realism = build_data_realism("Ghana", "Panama")

    assert data_realism["available"] is True
    assert data_realism["overall_level"] == "partial"


def test_build_data_realism_handles_panama_vs_ghana():
    data_realism = build_data_realism("Panama", "Ghana")

    assert data_realism["available"] is True
    assert data_realism["overall_level"] == "partial"


def test_build_data_realism_returns_unavailable_for_other_match():
    data_realism = build_data_realism("Brazil", "Haiti")

    assert data_realism["available"] is False


def test_predict_team_returns_data_realism_for_ghana_vs_panama():
    payload = {
        "home_team": "Ghana",
        "away_team": "Panama",
        "stadium_key": "Toronto",
        "weather_mode": "manual",
        "open_home_odds": 2.2,
        "current_home_odds": 2.1,
        "open_draw_odds": 3.4,
        "current_draw_odds": 3.3,
        "open_away_odds": 3.2,
        "current_away_odds": 3.1,
        "missing_starters": 0,
        "star_player_out": 0,
        "injury_level": 0,
        "bankroll": 10000,
        "max_bet_percent": 3,
        "high_risk_bet_percent": 1,
        "temperature": 22,
        "humidity": 50,
        "wind_speed": 10,
        "rain": 0
    }

    response = client.post("/predict_team", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "data_realism" in data
    assert data["data_realism"]["available"] is True
    assert data["data_realism"]["overall_level"] == "partial"
    assert data["data_realism"]["backtest"]["status"] == "synthetic_sample_only"
