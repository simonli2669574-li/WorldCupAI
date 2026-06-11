import requests


url = "http://127.0.0.1:8000/predict_team"

payload = {
    "home_team": "Argentina",
    "away_team": "Japan",

    "stadium_key": "Mexico City",
    "weather_mode": "auto",

    "open_home_odds": 1.9,
    "current_home_odds": 1.75,

    "open_draw_odds": 3.6,
    "current_draw_odds": 3.8,

    "open_away_odds": 4.8,
    "current_away_odds": 5.2,

    "missing_starters": 2,
    "star_player_out": 1,
    "injury_level": 2,

    "bankroll": 10000,

    "max_bet_percent": 3,
    "high_risk_bet_percent": 1,

    "temperature": 22,
    "humidity": 50,
    "wind_speed": 10,
    "rain": 0,
    "altitude": 0
}


response = requests.post(
    url,
    json=payload
)

print("Status Code:", response.status_code)
print(response.json())