import json

from agents.team_agent import resolve_team_name


PLAYER_MODEL_NOTE = "Manual player model ratings, not official ratings."


def load_player_profiles(path="data/players.json"):

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def _to_float(value, default=0.0):

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def _profile_available(profile):

    required_fields = {
        "attacking_threat",
        "wide_threat",
        "defensive_age_risk",
        "squad_experience",
    }

    return isinstance(profile, dict) and required_fields.issubset(profile)


def _normalize_profile(team_name, profile):

    return {
        "team": team_name,
        "attacking_threat": _to_float(profile.get("attacking_threat")),
        "wide_threat": _to_float(profile.get("wide_threat")),
        "defensive_age_risk": _to_float(profile.get("defensive_age_risk")),
        "squad_experience": _to_float(profile.get("squad_experience")),
        "note": profile.get("note", PLAYER_MODEL_NOTE),
    }


def build_player_analysis(home_team, away_team, player_profiles=None):

    if player_profiles is None:
        player_profiles = load_player_profiles()

    home_key = resolve_team_name(home_team) or home_team
    away_key = resolve_team_name(away_team) or away_team

    home_profile = player_profiles.get(home_key)
    away_profile = player_profiles.get(away_key)

    if not _profile_available(home_profile) or not _profile_available(away_profile):
        return {
            "enabled": False,
            "home": {
                "team": home_key,
                "available": _profile_available(home_profile),
            },
            "away": {
                "team": away_key,
                "available": _profile_available(away_profile),
            },
            "note": PLAYER_MODEL_NOTE,
        }

    return {
        "enabled": True,
        "home": _normalize_profile(home_key, home_profile),
        "away": _normalize_profile(away_key, away_profile),
        "note": PLAYER_MODEL_NOTE,
    }


def _disabled_player_xg_effect():

    return {
        "enabled": False,
        "note": PLAYER_MODEL_NOTE,
    }


def _build_reason(team_name, adjustment):

    if adjustment > 0.08:
        return (
            f"Player profile gives {team_name} a small attacking/wide "
            "threat boost."
        )

    if adjustment > 0:
        return (
            f"{team_name} receives a limited player-profile adjustment."
        )

    if adjustment < 0:
        return (
            f"Opposition experience trims {team_name}'s player-profile xG."
        )

    return (
        f"{team_name} has a neutral player-profile xG adjustment."
    )


def apply_player_xg_modifier(home_xg, away_xg, player_analysis):

    if not player_analysis or not player_analysis.get("enabled"):
        return home_xg, away_xg, _disabled_player_xg_effect()

    home = player_analysis.get("home", {})
    away = player_analysis.get("away", {})

    if not _profile_available(home) or not _profile_available(away):
        return home_xg, away_xg, _disabled_player_xg_effect()

    home_attacking_edge = _to_float(home.get("attacking_threat")) / 100
    home_wide_edge = _to_float(home.get("wide_threat")) / 100
    away_defensive_risk = _to_float(away.get("defensive_age_risk"))
    away_experience = _to_float(away.get("squad_experience")) / 100

    away_attacking_edge = _to_float(away.get("attacking_threat")) / 100
    away_wide_edge = _to_float(away.get("wide_threat")) / 100
    home_defensive_risk = _to_float(home.get("defensive_age_risk"))
    home_experience = _to_float(home.get("squad_experience")) / 100

    home_adjustment = (
        (home_attacking_edge * 0.08)
        + (home_wide_edge * away_defensive_risk * 0.18)
        - (away_experience * 0.04)
    )
    away_adjustment = (
        (away_attacking_edge * 0.08)
        + (away_wide_edge * home_defensive_risk * 0.18)
        - (home_experience * 0.04)
    )

    home_adjustment = round(_clamp(home_adjustment, -0.10, 0.25), 2)
    away_adjustment = round(_clamp(away_adjustment, -0.10, 0.25), 2)

    adjusted_home_xg = round(max(0.2, home_xg + home_adjustment), 2)
    adjusted_away_xg = round(max(0.2, away_xg + away_adjustment), 2)

    home_team = home.get("team", "Home")
    away_team = away.get("team", "Away")

    player_xg_effect = {
        "enabled": True,
        "home": {
            "team": home_team,
            "xg_adjustment": home_adjustment,
            "reason": _build_reason(home_team, home_adjustment),
        },
        "away": {
            "team": away_team,
            "xg_adjustment": away_adjustment,
            "reason": _build_reason(away_team, away_adjustment),
        },
        "note": PLAYER_MODEL_NOTE,
    }

    return adjusted_home_xg, adjusted_away_xg, player_xg_effect
