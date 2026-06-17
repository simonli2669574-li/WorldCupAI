import json
from pathlib import Path


SNAPSHOT_PATH = Path(__file__).resolve().parent / "data" / "match_snapshots.json"


def _normalize_team_name(team_name):
    return " ".join(str(team_name or "").strip().lower().split())


def build_match_key(home_team, away_team):
    return f"{_normalize_team_name(home_team)}::{_normalize_team_name(away_team)}"


def load_match_snapshots():
    try:
        with open(SNAPSHOT_PATH, encoding="utf-8") as file:
            snapshots = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    if not isinstance(snapshots, list):
        return []

    return snapshots


def get_match_snapshot(home_team, away_team):
    match_key = build_match_key(home_team, away_team)
    reverse_key = build_match_key(away_team, home_team)

    for snapshot in load_match_snapshots():
        snapshot_key = snapshot.get("match_key")

        if snapshot_key == match_key:
            return snapshot

        if snapshot_key == reverse_key:
            return snapshot

    return None


def build_data_realism(home_team, away_team, match_input=None):
    snapshot = get_match_snapshot(home_team, away_team)

    if snapshot is None:
        return {
            "available": False,
            "match": f"{home_team} vs {away_team}",
            "summary": "No match-specific data realism snapshot is available."
        }

    data_realism = {
        "available": True,
        "match": snapshot.get("match"),
        "group": snapshot.get("group"),
        "group_match_number": snapshot.get("group_match_number"),
        "stadium_key": snapshot.get("stadium_key"),
        "overall_level": snapshot.get("overall_level"),
        "summary": snapshot.get("summary"),
        "odds": snapshot.get("odds", {}),
        "players": snapshot.get("players", {}),
        "injuries": snapshot.get("injuries", {}),
        "weather": snapshot.get("weather", {}),
        "group_context": snapshot.get("group_context", {}),
        "backtest": snapshot.get("backtest", {}),
        "warnings": snapshot.get("warnings", [])
    }

    if match_input is not None:
        data_realism["input_match"] = {
            "home_team": getattr(match_input, "home_team", home_team),
            "away_team": getattr(match_input, "away_team", away_team),
            "stadium_key": getattr(match_input, "stadium_key", None),
            "weather_mode": getattr(match_input, "weather_mode", None)
        }

    return data_realism
