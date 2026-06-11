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


def stadium_to_response(key, stadium):

    return {
        "key": key,
        "country": stadium["country"],
        "city": stadium["city"],
        "stadium": stadium["stadium"],
        "latitude": stadium["latitude"],
        "longitude": stadium["longitude"],
        "altitude": stadium["altitude"]
    }


def list_stadiums():

    stadiums = load_stadiums()

    return [
        stadium_to_response(key, stadiums[key])
        for key in sorted(stadiums)
    ]
