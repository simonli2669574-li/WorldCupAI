from pydantic import BaseModel


class MatchInput(BaseModel):

    home_attack: float
    home_defense: float
    away_attack: float
    away_defense: float

    home_event: float = 0
    away_event: float = 0

    open_home_odds: float = 1.80
    current_home_odds: float = 1.80

    missing_starters: int = 0
    star_player_out: int = 0

    injury_level: float = 0

    formation: str = "4231"


class TeamMatchInput(BaseModel):

    home_team: str
    away_team: str

    stadium_key: str = "Mexico City"
    weather_mode: str = "manual"

    open_home_odds: float = 1.80
    current_home_odds: float = 1.80

    open_draw_odds: float = 3.50
    current_draw_odds: float = 3.50

    open_away_odds: float = 4.00
    current_away_odds: float = 4.00

    missing_starters: int = 0
    star_player_out: int = 0

    injury_level: float = 0

    bankroll: float = 10000

    max_bet_percent: float = 3
    high_risk_bet_percent: float = 1

    temperature: float = 22
    humidity: float = 50
    wind_speed: float = 10
    rain: float = 0
    altitude: float = 0