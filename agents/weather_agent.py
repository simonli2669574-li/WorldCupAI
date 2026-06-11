def analyze_weather(
    temperature,
    humidity,
    wind_speed,
    rain,
    altitude
):

    home_xg_modifier = 0
    away_xg_modifier = 0
    tempo_modifier = 0
    opinions = []

    # 高温影响：降低比赛节奏
    if temperature >= 30:
        home_xg_modifier -= 0.04
        away_xg_modifier -= 0.06
        tempo_modifier -= 0.06
        opinions.append("高温环境降低比赛节奏，对客队体能影响更明显")

    elif temperature <= 5:
        home_xg_modifier -= 0.03
        away_xg_modifier -= 0.03
        tempo_modifier -= 0.04
        opinions.append("低温环境降低身体灵活性和进攻效率")

    # 高湿影响：体能消耗更大
    if humidity >= 75:
        home_xg_modifier -= 0.03
        away_xg_modifier -= 0.05
        tempo_modifier -= 0.05
        opinions.append("高湿度增加体能消耗，降低持续压迫能力")

    # 大风影响：传中、长传、远射质量下降
    if wind_speed >= 25:
        home_xg_modifier -= 0.04
        away_xg_modifier -= 0.04
        tempo_modifier -= 0.03
        opinions.append("大风影响长传、传中和远射质量")

    # 雨天影响：传控变差，但防守失误增加
    if rain > 0:
        home_xg_modifier -= 0.02
        away_xg_modifier -= 0.02
        tempo_modifier -= 0.03
        opinions.append("降雨降低传控质量，但可能增加防守失误")

    # 高海拔影响：客队更吃亏
    if altitude >= 1200:
        away_xg_modifier -= 0.08
        tempo_modifier -= 0.05
        opinions.append("高海拔影响冲刺恢复，对不适应球队尤其不利")

    if len(opinions) == 0:
        opinions.append("天气条件正常，对比赛影响较小")

    return {
        "home_xg_modifier": round(home_xg_modifier, 3),
        "away_xg_modifier": round(away_xg_modifier, 3),
        "tempo_modifier": round(tempo_modifier, 3),
        "opinion": "；".join(opinions)
    }