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


def get_team(team_name):

    teams = load_teams()

    if team_name in teams:
        return teams[team_name]

    stripped_team_name = team_name.strip()

    if stripped_team_name in teams:
        return teams[stripped_team_name]

    normalized_team_name = stripped_team_name.casefold()

    for standard_name, team in teams.items():
        if standard_name.casefold() == normalized_team_name:
            return team

    aliases = load_team_aliases()

    for alias, standard_name in aliases.items():
        if alias.casefold() != normalized_team_name:
            continue

        if standard_name not in teams:
            return None

        return teams[standard_name]

    return None
