def analyze_odds(open_home, current_home):

    movement = current_home - open_home

    score = movement * -20

    if score > 5:
        score = 5

    if score < -5:
        score = -5

    if score > 0:
        opinion = "市场看好主队"
    elif score < 0:
        opinion = "市场看空主队"
    else:
        opinion = "盘口稳定"

    return {
        "score": score,
        "opinion": opinion
    }