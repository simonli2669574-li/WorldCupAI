def analyze_injury(injury_level):

    score = -injury_level * 5

    if injury_level <= 0:
        opinion = "无明显伤病影响"

    elif injury_level == 1:
        opinion = "轻微伤病影响"

    elif injury_level == 2:
        opinion = "中等伤病影响"

    else:
        opinion = "严重伤病影响"

    return {
        "score": score,
        "opinion": opinion
    }