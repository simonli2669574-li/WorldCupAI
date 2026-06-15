import json

from agents.team_agent import resolve_team_name


def load_group_standings(path="data/group_standings.json"):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_group_table(group, standings):

    if standings is None:
        return None

    group_data = standings.get(group)

    if group_data is None:
        return None

    return group_data.get("teams")


def rank_group_table(group_table):

    if group_table is None:
        return []

    ranked = sorted(
        group_table,
        key=lambda team: (
            team.get("points", 0),
            team.get("goal_difference", 0),
            team.get("goals_for", 0),
        ),
        reverse=True
    )

    result = []

    for index, team in enumerate(ranked, start=1):
        ranked_team = dict(team)
        ranked_team["group_position"] = index
        result.append(ranked_team)

    return result


def get_team_standing(team_name, group_table):

    standard_name = resolve_team_name(team_name)

    if standard_name is None:
        return None

    for team in rank_group_table(group_table):
        standing_name = resolve_team_name(team.get("team", ""))

        if standing_name == standard_name:
            return team

    return None


def unavailable_team_context(team_name):

    return {
        "team": team_name,
        "available": False,
        "points": None,
        "played": None,
        "group_position": None,
        "likely_qualified": False,
        "must_win": False,
        "draw_is_enough": False,
        "rotation_risk": "unknown",
        "motivation_level": "unknown",
        "attacking_urgency": "unknown",
        "defensive_risk": "unknown",
        "xg_multiplier": 1.0,
        "context_note": "Team context is unavailable in local group standings."
    }


def evaluate_team_context(team_name, group_table, group_match_number):

    standing = get_team_standing(team_name, group_table)

    if standing is None:
        return unavailable_team_context(team_name)

    points = standing.get("points", 0)
    played = standing.get("played", 0)
    group_position = standing.get("group_position")

    context = {
        "team": resolve_team_name(team_name) or team_name,
        "available": True,
        "points": points,
        "played": played,
        "group_position": group_position,
        "likely_qualified": False,
        "must_win": False,
        "draw_is_enough": False,
        "rotation_risk": "low",
        "motivation_level": "medium",
        "attacking_urgency": "medium",
        "defensive_risk": "medium",
        "xg_multiplier": 1.0,
        "context_note": "Early group match context has limited xG impact."
    }

    if group_match_number < 3:
        return context

    context["context_note"] = "Team has standard third-match group pressure."

    if points >= 6:
        context.update({
            "likely_qualified": True,
            "rotation_risk": "high",
            "motivation_level": "medium",
            "attacking_urgency": "low",
            "defensive_risk": "low",
            "xg_multiplier": 0.90,
            "context_note": (
                "Team may rotate because qualification is likely secured."
            )
        })
    elif points <= 1:
        context.update({
            "must_win": True,
            "rotation_risk": "low",
            "motivation_level": "high",
            "attacking_urgency": "high",
            "defensive_risk": "high",
            "xg_multiplier": 1.06,
            "context_note": (
                "Team likely needs a win and may accept more defensive risk."
            )
        })
    elif points == 4:
        context.update({
            "draw_is_enough": True,
            "rotation_risk": "medium",
            "motivation_level": "medium",
            "attacking_urgency": "low",
            "defensive_risk": "low",
            "xg_multiplier": 0.95,
            "context_note": (
                "A draw may be enough, reducing attacking urgency."
            )
        })
    elif points == 3:
        context.update({
            "rotation_risk": "low",
            "motivation_level": "high",
            "attacking_urgency": "medium",
            "defensive_risk": "medium",
            "xg_multiplier": 1.02,
            "context_note": (
                "Team faces meaningful pressure but not a pure must-win state."
            )
        })

    return context


def build_match_context_effect(
    home_team,
    away_team,
    group,
    group_match_number,
    standings=None
):

    if group is None or str(group).strip() == "":
        return {
            "enabled": False
        }

    if standings is None:
        standings = load_group_standings()

    group_table = get_group_table(group, standings)

    if group_table is None:
        return {
            "enabled": False,
            "group": group,
            "group_match_number": group_match_number,
            "context_note": "Group is unavailable in local standings."
        }

    home_context = evaluate_team_context(
        home_team,
        group_table,
        group_match_number
    )
    away_context = evaluate_team_context(
        away_team,
        group_table,
        group_match_number
    )

    return {
        "enabled": True,
        "group": group,
        "group_match_number": group_match_number,
        "home": home_context,
        "away": away_context
    }


def apply_context_xg(home_xg, away_xg, context_effect):

    if not context_effect.get("enabled"):
        return home_xg, away_xg

    home_multiplier = context_effect.get("home", {}).get("xg_multiplier", 1.0)
    away_multiplier = context_effect.get("away", {}).get("xg_multiplier", 1.0)

    adjusted_home_xg = max(0.2, home_xg * home_multiplier)
    adjusted_away_xg = max(0.2, away_xg * away_multiplier)

    return adjusted_home_xg, adjusted_away_xg
