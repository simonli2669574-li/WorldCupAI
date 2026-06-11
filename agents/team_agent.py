import json

from data_loader import load_teams


def load_team_aliases():

    try:
        with open(
            "data/team_aliases.json",
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def resolve_team_name(team_name):

    teams = load_teams()

    if team_name in teams:
        return team_name

    stripped_team_name = team_name.strip()

    if stripped_team_name in teams:
        return stripped_team_name

    normalized_team_name = stripped_team_name.casefold()

    for standard_name in teams:
        if standard_name.casefold() == normalized_team_name:
            return standard_name

    aliases = load_team_aliases()

    for alias, standard_name in aliases.items():
        if alias.casefold() != normalized_team_name:
            continue

        if standard_name not in teams:
            return None

        return standard_name

    return None


def get_team(team_name):

    teams = load_teams()
    standard_name = resolve_team_name(team_name)

    if standard_name is None:
        return None

    return teams[standard_name]


def team_to_response(name, team):

    return {
        "name": name,
        "attack": team["attack"],
        "defense": team["defense"],
        "elo": team["elo"],
        "formation": team["formation"],
        "style": team["style"]
    }


def list_teams():

    teams = load_teams()

    return [
        team_to_response(name, teams[name])
        for name in sorted(teams)
    ]


def search_teams(query):

    if query is None:
        return []

    normalized_query = query.strip().casefold()

    if normalized_query == "":
        return []

    teams = load_teams()
    aliases = load_team_aliases()
    results = {}

    for name, team in teams.items():
        if normalized_query not in name.casefold():
            continue

        result = team_to_response(name, team)
        result["matched_by"] = "name"
        result["matched_text"] = name
        results[name] = result

    for alias, standard_name in aliases.items():
        if normalized_query not in alias.casefold():
            continue

        if standard_name not in teams:
            continue

        if standard_name in results:
            continue

        result = team_to_response(standard_name, teams[standard_name])
        result["matched_by"] = "alias"
        result["matched_text"] = alias
        results[standard_name] = result

    return [
        results[name]
        for name in sorted(results)
    ]
