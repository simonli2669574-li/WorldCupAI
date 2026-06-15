from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import MatchInput, TeamMatchInput
from simulation import simulate
from kelly import calculate_three_way_kelly
from risk import apply_risk_control
from market import calculate_market_edges
from report import generate_value_summary, generate_report
from match_context import build_match_context_effect, apply_context_xg

from agents.odds_agent import analyze_odds
from agents.lineup_agent import analyze_lineup
from agents.injury_agent import analyze_injury
from agents.ensemble_agent import combine
from agents.tactics_agent import analyze_tactics
from agents.team_agent import (
    get_team,
    list_teams,
    resolve_team_name,
    search_teams
)
from agents.weather_agent import analyze_weather
from stadium_loader import get_stadium, list_stadiums
from weather_service import get_weather_by_location

APP_VERSION = "6.5"

app = FastAPI(title="WorldCupAI 2.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://simonli2669574-li.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# 请求结构
# -------------------------

# -------------------------
# 泊松
# -------------------------

# -------------------------
# 单场模拟
# -------------------------

# -------------------------
# 核心预测引擎
# -------------------------

def predict_from_teams(home, away):

    home_attack = home["attack"]
    home_defense = home["defense"]

    away_attack = away["attack"]
    away_defense = away["defense"]

    home_strength = home_attack - away_defense + 50
    away_strength = away_attack - home_defense + 50

    base_goals = 2.7

    home_xg = (
        base_goals
        * home_strength
        / (home_strength + away_strength)
    )

    away_xg = (
        base_goals
        * away_strength
        / (home_strength + away_strength)
    )

    return {
        "home_xg": round(home_xg, 2),
        "away_xg": round(away_xg, 2)
    }

def predict(match: MatchInput):

    odds_result = analyze_odds(
        match.open_home_odds,
        match.current_home_odds
    )

    lineup_result = analyze_lineup(
        match.missing_starters,
        match.star_player_out
    )

    injury_result = analyze_injury(
        match.injury_level
    )

    tactics_result = analyze_tactics(
        match.formation
    )

    agent_result = combine(
        odds_result,
        lineup_result,
        injury_result,
        tactics_result
    )

    base_goals = 2.7

    home_strength = (
        match.home_attack
        - match.away_defense
        + match.home_event
        + agent_result["total_score"]
        + 50
    )
    away_strength = match.away_attack - match.home_defense + match.away_event + 50

    home_xg = base_goals * home_strength / (home_strength + away_strength)
    away_xg = base_goals * away_strength / (home_strength + away_strength)

    N = 5000

    home_win = 0
    draw = 0
    away_win = 0

    btts_count = 0
    over25_count = 0

    score_map = {}

    for _ in range(N):

        h, a = simulate(home_xg, away_xg)

        if h > 0 and a > 0:
            btts_count += 1

        if h + a >= 3:
            over25_count += 1

        score = f"{h}-{a}"

        score_map[score] = score_map.get(score, 0) + 1

        if h > a:
            home_win += 1
        elif h == a:
            draw += 1
        else:
            away_win += 1

    sorted_scores = sorted(
        score_map.items(),
        key=lambda x: x[1],
        reverse=True
    )

    btts_prob = btts_count / N
    over25_prob = over25_count / N

    top3 = []

    for score, count in sorted_scores[:3]:
        top3.append({
            "score": score,
            "prob": round(count / N * 100, 2)
        })

    return {
        "home_win": round(home_win / N * 100, 2),
        "draw": round(draw / N * 100, 2),
        "away_win": round(away_win / N * 100, 2),

        "top_scores": top3,

        "markets": {
            "BTTS": round(btts_prob * 100, 2),
            "Over2.5": round(over25_prob * 100, 2)
        },

        "agents": {
            "total_score": agent_result["total_score"],
            "details": agent_result["details"]
        }
    }

# -------------------------
# API接口
# -------------------------

@app.get("/health")
def health_api():

    return {
        "status": "ok",
        "service": "WorldCupAI",
        "version": APP_VERSION
    }


@app.post("/predict")
def predict_api(match: MatchInput):

    result = predict(match)

    return result


@app.get("/teams")
def teams_api():

    return list_teams()


@app.get("/teams/search")
def search_teams_api(q: str = ""):

    return search_teams(q)


@app.get("/stadiums")
def stadiums_api():

    return list_stadiums()


def run_team_prediction(match: TeamMatchInput):

    home_key = resolve_team_name(match.home_team)
    away_key = resolve_team_name(match.away_team)

    if home_key is None:
        return {
            "error": f"找不到球队 {match.home_team}"
        }

    if away_key is None:
        return {
            "error": f"找不到球队 {match.away_team}"
        }

    home = get_team(match.home_team)
    away = get_team(match.away_team)
    stadium = get_stadium(match.stadium_key)

    if home is None:
        return {
            "error": f"找不到球队 {match.home_team}"
        }

    if away is None:
        return {
            "error": f"找不到球队 {match.away_team}"
        }

    if stadium is None:
        return {
            "error": f"找不到球 ?{match.stadium_key}"
        }

    odds_result = analyze_odds(
        match.open_home_odds,
        match.current_home_odds
    )

    lineup_result = analyze_lineup(
        match.missing_starters,
        match.star_player_out
    )

    injury_result = analyze_injury(
        match.injury_level
    )

    tactics_result = analyze_tactics(
        home["formation"]
    )

    weather_altitude = stadium["altitude"]

    if match.weather_mode == "manual":

        weather_input = {
            "temperature": match.temperature,
            "humidity": match.humidity,
            "wind_speed": match.wind_speed,
            "rain": match.rain,
            "source": "manual"
        }

    elif match.weather_mode == "auto":

        weather_input = get_weather_by_location(
            stadium["latitude"],
            stadium["longitude"]
        )

        if "error" in weather_input:
            return {
                "error": weather_input["error"],
                "stadium": stadium,
                "weather_raw": weather_input
            }

    else:

        return {
            "error": "weather_mode 只能 ?manual  ?auto"
        }

    weather_result = analyze_weather(
        weather_input["temperature"],
        weather_input["humidity"],
        weather_input["wind_speed"],
        weather_input["rain"],
        weather_altitude,
        home.get("style", "balanced"),
        away.get("style", "balanced")
    )

    weather_result["input"] = weather_input

    agent_result = combine(
        odds_result,
        lineup_result,
        injury_result,
        tactics_result
    )

    home_attack = home["attack"]
    home_defense = home["defense"]

    away_attack = away["attack"]
    away_defense = away["defense"]

    home_strength = (
        home_attack
        - away_defense
        + agent_result["total_score"]
        + 50
    )

    away_strength = (
        away_attack
        - home_defense
        + 50
    )

    home_strength = max(10, home_strength)
    away_strength = max(10, away_strength)

    base_goals = 2.7

    home_xg = (
        base_goals
        * home_strength
        / (home_strength + away_strength)
    )

    away_xg = (
        base_goals
        * away_strength
        / (home_strength + away_strength)
    )

    home_xg = home_xg * (1 + weather_result["home_xg_modifier"])
    away_xg = away_xg * (1 + weather_result["away_xg_modifier"])

    home_xg = max(0.2, home_xg)
    away_xg = max(0.2, away_xg)

    context_effect = {
        "enabled": False
    }

    if match.auto_context is True and match.group:
        context_effect = build_match_context_effect(
            home_key,
            away_key,
            match.group,
            match.group_match_number
        )
        home_xg, away_xg = apply_context_xg(
            home_xg,
            away_xg,
            context_effect
        )

    N = 5000

    home_win = 0
    draw = 0
    away_win = 0

    btts_count = 0
    over25_count = 0

    score_map = {}

    for _ in range(N):

        h, a = simulate(home_xg, away_xg)

        if h > 0 and a > 0:
            btts_count += 1

        if h + a >= 3:
            over25_count += 1

        score = f"{h}-{a}"

        score_map[score] = score_map.get(score, 0) + 1

        if h > a:
            home_win += 1
        elif h == a:
            draw += 1
        else:
            away_win += 1

    sorted_scores = sorted(
        score_map.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top3 = []

    for score, count in sorted_scores[:3]:
        top3.append({
            "score": score,
            "prob": round(count / N * 100, 2)
        })

    home_prob = home_win / N
    draw_prob = draw / N
    away_prob = away_win / N

    market_edges = calculate_market_edges(
        home_prob,
        draw_prob,
        away_prob,
        match.current_home_odds,
        match.current_draw_odds,
        match.current_away_odds
    )

    kelly_result = calculate_three_way_kelly(
        home_prob,
        draw_prob,
        away_prob,
        match.current_home_odds,
        match.current_draw_odds,
        match.current_away_odds,
        match.bankroll
    )

    risk_control_result = apply_risk_control(
        kelly_result,
        agent_result,
        match.bankroll,
        match.max_bet_percent,
        match.high_risk_bet_percent
    )

    summary_result = generate_value_summary(
        kelly_result,
        agent_result
    )

    report_result = generate_report(
        match.home_team,
        match.away_team,
        home_win / N * 100,
        draw / N * 100,
        away_win / N * 100,
        top3,
        market_edges,
        kelly_result,
        risk_control_result,
        agent_result
    )

    return {
        "home_team": home_key,
        "away_team": away_key,

        "input_teams": {
            "home_team": match.home_team,
            "away_team": match.away_team
        },

        "stadium": stadium,

        "home_xg": round(home_xg, 2),
        "away_xg": round(away_xg, 2),

        "home_win": round(home_win / N * 100, 2),
        "draw": round(draw / N * 100, 2),
        "away_win": round(away_win / N * 100, 2),

        "top_scores": top3,

        "markets": {
            "BTTS": round(btts_count / N * 100, 2),
            "Over2.5": round(over25_count / N * 100, 2)
        },

        "agents": {
            "total_score": agent_result["total_score"],
            "details": agent_result["details"]
        },

        "weather": weather_result,

        "context_effect": context_effect,

        "market_edges": market_edges,

        "kelly": kelly_result,

        "risk_control": risk_control_result,

        "summary": summary_result,

        "report": report_result
    }


@app.post("/predict_team")
def predict_team(match: TeamMatchInput):

    return run_team_prediction(match)


@app.get("/backtest")
def backtest_api():

    from backtest import run_backtest

    return run_backtest()
