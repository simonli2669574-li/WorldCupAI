def apply_risk_control(
    kelly_result,
    agent_result,
    bankroll,
    max_bet_percent,
    high_risk_bet_percent
):

    best_value = kelly_result["best_value"]
    total_score = agent_result["total_score"]

    if best_value == "无推荐":
        return {
            "risk_mode": "无推荐",
            "cap_percent": 0,
            "max_bet_allowed": 0,
            "original_suggested_bet": 0,
            "adjusted_suggested_bet": 0,
            "note": "没有正期望投注机会，因此无需进行仓位控制。"
        }

    if best_value == "主胜":
        best_data = kelly_result["home"]
    elif best_value == "平局":
        best_data = kelly_result["draw"]
    else:
        best_data = kelly_result["away"]

    original_bet = best_data["suggested_bet"]

    if abs(total_score) >= 10:
        cap_percent = high_risk_bet_percent
        risk_mode = "高风险限仓"
        note = "Agent 分数波动较大，说明比赛存在明显不确定因素，自动使用高风险仓位上限。"
    else:
        cap_percent = max_bet_percent
        risk_mode = "普通限仓"
        note = "比赛风险处于普通范围，使用常规仓位上限。"

    max_bet_allowed = bankroll * cap_percent / 100

    adjusted_bet = min(
        original_bet,
        max_bet_allowed
    )

    best_data["original_suggested_bet"] = round(original_bet, 2)
    best_data["suggested_bet"] = round(adjusted_bet, 2)
    best_data["risk_cap"] = round(max_bet_allowed, 2)

    return {
        "risk_mode": risk_mode,
        "cap_percent": cap_percent,
        "max_bet_allowed": round(max_bet_allowed, 2),
        "original_suggested_bet": round(original_bet, 2),
        "adjusted_suggested_bet": round(adjusted_bet, 2),
        "note": note
    }