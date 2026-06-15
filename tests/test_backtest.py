from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_backtest_api_returns_summary_and_details():

    response = client.get("/backtest")

    assert response.status_code == 200

    data = response.json()
    summary = data["summary"]

    assert summary["matches_tested"] > 0
    assert "dataset_source" in summary
    assert "dataset_note" in summary
    assert "sample_size" in summary
    assert "competitions" in summary

    for field in [
        "winner_accuracy",
        "top_score_hit_rate",
        "btts_accuracy",
        "over25_accuracy",
    ]:
        assert field in summary

    assert isinstance(data["details"], list)

    first_detail = data["details"][0]

    for field in [
        "match_id",
        "source",
        "competition",
        "match_date",
        "neutral_site",
        "actual_score",
        "actual_winner",
        "predicted_winner",
        "winner_hit",
        "top_score_hit",
        "btts_hit",
        "over25_hit",
    ]:
        assert field in first_detail
