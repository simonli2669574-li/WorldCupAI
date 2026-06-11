VALID_STYLES = [
    "high_press",
    "possession",
    "counter",
    "physical",
    "balanced"
]


def normalize_style(style):

    if style not in VALID_STYLES:
        return "balanced"

    return style


def get_style_weather_adjustment(
    style,
    temperature,
    humidity,
    wind_speed,
    rain
):

    adjustment = 0
    notes = []

    if style == "high_press":
        if temperature >= 30 or humidity >= 75:
            adjustment -= 0.015
            notes.append("high_press reduced by heat or humidity")
        if rain > 0:
            adjustment -= 0.005
            notes.append("high_press slightly reduced by rain")

    elif style == "possession":
        if wind_speed >= 25:
            adjustment -= 0.01
            notes.append("possession reduced by strong wind")
        if rain > 0:
            adjustment -= 0.01
            notes.append("possession reduced by rain")

    elif style == "counter":
        if wind_speed >= 25:
            adjustment += 0.005
            notes.append("counter less exposed to strong wind")
        if rain > 0:
            adjustment += 0.005
            notes.append("counter can benefit from transition errors")

    elif style == "physical":
        if rain > 0:
            adjustment += 0.005
            notes.append("physical style slightly handles rain better")
        if temperature >= 30:
            adjustment -= 0.01
            notes.append("physical style reduced by heat")

    adjustment = max(-0.03, min(0.03, adjustment))

    if len(notes) == 0:
        notes.append("balanced weather style impact")

    return adjustment, notes


def analyze_weather(
    temperature,
    humidity,
    wind_speed,
    rain,
    altitude,
    home_style="balanced",
    away_style="balanced"
):

    home_xg_modifier = 0
    away_xg_modifier = 0
    tempo_modifier = 0
    opinions = []

    home_style = normalize_style(home_style)
    away_style = normalize_style(away_style)

    if temperature >= 30:
        home_xg_modifier -= 0.04
        away_xg_modifier -= 0.06
        tempo_modifier -= 0.06
        opinions.append(
            "High temperature lowers tempo and hurts away stamina more"
        )

    elif temperature <= 5:
        home_xg_modifier -= 0.03
        away_xg_modifier -= 0.03
        tempo_modifier -= 0.04
        opinions.append(
            "Low temperature reduces mobility and attacking efficiency"
        )

    if humidity >= 75:
        home_xg_modifier -= 0.03
        away_xg_modifier -= 0.05
        tempo_modifier -= 0.05
        opinions.append(
            "High humidity increases fatigue and reduces pressing intensity"
        )

    if wind_speed >= 25:
        home_xg_modifier -= 0.04
        away_xg_modifier -= 0.04
        tempo_modifier -= 0.03
        opinions.append(
            "Strong wind lowers crossing, long passing, and shooting quality"
        )

    if rain > 0:
        home_xg_modifier -= 0.02
        away_xg_modifier -= 0.02
        tempo_modifier -= 0.03
        opinions.append(
            "Rain lowers ball control but can increase defensive errors"
        )

    if altitude >= 1200:
        away_xg_modifier -= 0.08
        tempo_modifier -= 0.05
        opinions.append(
            "High altitude affects recovery and especially hurts away teams"
        )

    if len(opinions) == 0:
        opinions.append("Weather conditions are normal with limited impact")

    home_style_adjustment, home_style_notes = get_style_weather_adjustment(
        home_style,
        temperature,
        humidity,
        wind_speed,
        rain
    )
    away_style_adjustment, away_style_notes = get_style_weather_adjustment(
        away_style,
        temperature,
        humidity,
        wind_speed,
        rain
    )

    home_xg_modifier += home_style_adjustment
    away_xg_modifier += away_style_adjustment

    return {
        "home_xg_modifier": round(home_xg_modifier, 3),
        "away_xg_modifier": round(away_xg_modifier, 3),
        "tempo_modifier": round(tempo_modifier, 3),
        "opinion": "; ".join(opinions),
        "style_effect": {
            "home_style": home_style,
            "away_style": away_style,
            "home_xg_adjustment": round(home_style_adjustment, 3),
            "away_xg_adjustment": round(away_style_adjustment, 3),
            "home_notes": home_style_notes,
            "away_notes": away_style_notes
        }
    }
