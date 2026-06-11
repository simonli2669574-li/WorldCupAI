import json


def load_stadiums():

    with open(
        "data/stadiums.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_stadium(stadium_key):

    stadiums = load_stadiums()

    if stadium_key not in stadiums:
        return None

    return stadiums[stadium_key]