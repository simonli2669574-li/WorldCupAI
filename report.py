def generate_value_summary(kelly_result, agent_result):

    best_value = kelly_result["best_value"]
    total_score = agent_result["total_score"]

    if best_value == "无推荐":
        return {
            "main_pick": "无推荐",
            "risk_level": "观望",
            "reason": "模型没有发现明显正期望投注机会，建议跳过本场。"
        }

    if best_value == "主胜":
        best_data = kelly_result["home"]
    elif best_value == "平局":
        best_data = kelly_result["draw"]
    else:
        best_data = kelly_result["away"]

    bet_size = best_data["suggested_bet"]
    kelly_percent = best_data["fractional_kelly"]

    if kelly_percent >= 10:
        risk_level = "高信号，但仍需控制仓位"
    elif kelly_percent >= 5:
        risk_level = "中等机会"
    else:
        risk_level = "轻微机会"

    if total_score <= -10:
        agent_note = "Agent 总分明显偏负，说明存在较强负面因素。"
    elif total_score >= 10:
        agent_note = "Agent 总分明显偏正，说明多项因素支持该方向。"
    else:
        agent_note = "Agent 总分较为中性，市场和球队因素没有极端倾向。"

    return {
        "main_pick": best_value,
        "risk_level": risk_level,
        "suggested_bet": bet_size,
        "reason": f"模型认为{best_value}存在正期望，建议金额约为{bet_size}。{agent_note}这不是保证盈利，只代表当前模型下的价值信号。"
    }


def generate_report(
    home_team,
    away_team,
    home_win,
    draw,
    away_win,
    top_scores,
    market_edges,
    kelly_result,
    risk_control_result,
    agent_result
):

    title = f"{home_team} vs {away_team} 赛前预测报告"

    if home_win >= draw and home_win >= away_win:
        prediction = "模型认为主胜概率最高。"
    elif draw >= home_win and draw >= away_win:
        prediction = "模型认为平局概率最高。"
    else:
        prediction = "模型认为客胜概率最高。"

    best_value = kelly_result["best_value"]

    if best_value == "无推荐":
        value_text = "当前没有发现明显正期望投注方向。"
    else:
        if best_value == "主胜":
            edge_data = market_edges["home"]
        elif best_value == "平局":
            edge_data = market_edges["draw"]
        else:
            edge_data = market_edges["away"]

        value_text = (
            f"{best_value} edge 为 {edge_data['edge']}%，"
            f"模型概率 {edge_data['model_prob']}%，"
            f"赔率隐含概率 {edge_data['implied_prob']}%。"
        )

    score_names = []

    for item in top_scores:
        score_names.append(item["score"])

    score_view = "最可能比分为 " + "、".join(score_names) + "。"

    risk_view = (
        f"{risk_control_result['risk_mode']}，"
        f"单场上限为本金的 {risk_control_result['cap_percent']}%，"
        f"最终建议金额 {risk_control_result['adjusted_suggested_bet']}。"
    )

    total_score = agent_result["total_score"]

    if total_score <= -10:
        agent_view = "Agent 综合判断偏负，说明主队存在明显不利因素。"
    elif total_score >= 10:
        agent_view = "Agent 综合判断偏正，说明主队受到多项因素支持。"
    else:
        agent_view = "Agent 综合判断接近中性，双方外部因素没有明显极端倾向。"

    if best_value == "无推荐":
        final_action = "建议观望，不强行下注。"
    else:
        final_action = f"可考虑小注{best_value}，但必须遵守风控上限。"

    return {
        "title": title,
        "prediction": prediction,
        "score_view": score_view,
        "market_view": value_text,
        "risk_view": risk_view,
        "agent_view": agent_view,
        "final_action": final_action
    }