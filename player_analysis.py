import json

from agents.team_agent import resolve_team_name


PLAYER_MODEL_NOTE = (
    "Manual player profile, not official live roster or official rating."
)

AGGREGATE_FIELDS = {
    "attacking_threat",
    "wide_threat",
    "defensive_age_risk",
    "squad_experience",
}

DEFENSIVE_POSITIONS = {"GK", "CB", "DF", "FB", "LB", "RB", "WB", "DM"}


def load_player_profiles(path="data/players.json"):

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def load_players(path="data/players.json"):

    return load_player_profiles(path)


def _to_float(value, default=0.0):

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def _players_from_profile(profile):

    if not isinstance(profile, dict):
        return []

    players = profile.get("players")

    if not isinstance(players, list):
        return []

    return [
        player
        for player in players
        if isinstance(player, dict)
    ]


def _has_aggregate_profile(profile):

    return isinstance(profile, dict) and AGGREGATE_FIELDS.issubset(profile)


def _has_player_profile(profile):

    return len(_players_from_profile(profile)) > 0


def _profile_available(profile):

    return _has_aggregate_profile(profile) or _has_player_profile(profile)


def _weighted_average(players, field, default=0.0):

    total_weight = 0.0
    weighted_total = 0.0

    for player in players:
        value = _to_float(player.get(field), None)

        if value is None:
            continue

        importance = _clamp(_to_float(player.get("importance"), 0.5), 0.0, 1.0)
        role = player.get("role")

        if role == "starter":
            role_weight = 1.0
        elif role == "rotation":
            role_weight = 0.72
        else:
            role_weight = 0.45

        weight = max(0.05, importance * role_weight)
        weighted_total += value * weight
        total_weight += weight

    if total_weight == 0:
        return default

    return weighted_total / total_weight


def _is_defensive_player(player):

    position = str(player.get("position", "")).upper()
    tags = player.get("tags", [])

    if position in DEFENSIVE_POSITIONS:
        return True

    if not isinstance(tags, list):
        return False

    return any(
        "center_back" in str(tag)
        or "full_back" in str(tag)
        or "defensive" in str(tag)
        or "goalkeeper" in str(tag)
        for tag in tags
    )


def _summarize_key_players(players):

    key_players = sorted(
        players,
        key=lambda player: (
            _to_float(player.get("importance")),
            _to_float(player.get("overall")),
        ),
        reverse=True,
    )

    return [
        {
            "name": player.get("name", ""),
            "position": player.get("position", ""),
            "role": player.get("role", ""),
            "overall": _to_float(player.get("overall")),
            "importance": _to_float(player.get("importance")),
            "tags": player.get("tags", []),
        }
        for player in key_players[:5]
    ]


def _normalize_player_profile(team_name, profile):

    players = _players_from_profile(profile)
    defensive_players = [
        player
        for player in players
        if _is_defensive_player(player)
    ]

    if not defensive_players:
        defensive_players = players

    attacking_threat = round(
        _clamp(_weighted_average(players, "attacking_threat"), 1, 100),
        1,
    )
    wide_threat = round(
        _clamp(_weighted_average(players, "wide_threat"), 1, 100),
        1,
    )
    defensive_age_risk = round(
        _clamp(
            _weighted_average(defensive_players, "age_risk"),
            0.0,
            1.0,
        ),
        2,
    )
    squad_experience = round(
        _clamp(_weighted_average(players, "experience"), 1, 100),
        1,
    )

    return {
        "team": team_name,
        "available": True,
        "attacking_threat": attacking_threat,
        "wide_threat": wide_threat,
        "defensive_age_risk": defensive_age_risk,
        "squad_experience": squad_experience,
        "key_players": _summarize_key_players(players),
        "player_count": len(players),
        "data_source_note": profile.get("data_source_note", PLAYER_MODEL_NOTE),
        "note": profile.get("data_source_note", PLAYER_MODEL_NOTE),
    }


def analyze_team_players(team_name, player_profiles=None):

    if player_profiles is None:
        player_profiles = load_player_profiles()

    team_key = resolve_team_name(team_name) or team_name
    profile = player_profiles.get(team_key)

    if not _profile_available(profile):
        return {
            "team": team_key,
            "available": False,
            "note": PLAYER_MODEL_NOTE,
        }

    return _normalize_profile(team_key, profile)


def _normalize_profile(team_name, profile):

    if _has_player_profile(profile):
        return _normalize_player_profile(team_name, profile)

    return {
        "team": team_name,
        "available": True,
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

    home_profile = analyze_team_players(home_key, player_profiles)
    away_profile = analyze_team_players(away_key, player_profiles)

    if not home_profile.get("available") or not away_profile.get("available"):
        return {
            "enabled": False,
            "home": {
                "team": home_key,
                "available": home_profile.get("available", False),
            },
            "away": {
                "team": away_key,
                "available": away_profile.get("available", False),
            },
            "note": PLAYER_MODEL_NOTE,
        }

    return {
        "enabled": True,
        "home": home_profile,
        "away": away_profile,
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
