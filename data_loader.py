import json

def load_teams():

    with open(
        "data/teams.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)