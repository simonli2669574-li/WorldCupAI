import requests


def get_weather_by_location(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "precipitation"
        ),
        "wind_speed_unit": "kmh",
        "timezone": "auto"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
    except requests.exceptions.RequestException as exc:
        return {
            "error": "Weather API request failed",
            "source": "Open-Meteo",
            "detail": str(exc)
        }

    if response.status_code != 200:
        return {
            "error": "Weather API request failed",
            "source": "Open-Meteo",
            "status_code": response.status_code,
            "detail": response.text
        }

    try:
        data = response.json()
    except ValueError as exc:
        return {
            "error": "Weather API JSON parse failed",
            "source": "Open-Meteo",
            "detail": str(exc)
        }

    if "current" not in data:
        return {
            "error": "Weather API response missing current data",
            "source": "Open-Meteo",
            "detail": "Missing current field",
            "raw": data
        }

    current = data["current"]

    return {
        "temperature": current.get("temperature_2m", 22),
        "humidity": current.get("relative_humidity_2m", 50),
        "wind_speed": current.get("wind_speed_10m", 10),
        "rain": current.get("precipitation", 0),
        "source": "Open-Meteo",
        "time": current.get("time")
    }