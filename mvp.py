import math
import random

print("===== 世界杯AI MVP Version 2.1（动态信息流模型） =====")

# -------------------------
# 赔率（支持漂移）
# -------------------------

open_home_odds = float(input("开盘主胜赔率："))
live_home_odds = float(input("即时主胜赔率："))

open_draw_odds = float(input("开盘平局赔率："))
live_draw_odds = float(input("即时平局赔率："))

open_away_odds = float(input("开盘客胜赔率："))
live_away_odds = float(input("即时客胜赔率："))

bankroll = float(input("本金："))

# -------------------------
# 球队基础
# -------------------------

print("\n球队评分（0-100）")

home_attack = float(input("主队进攻力："))
home_defense = float(input("主队防守力："))
away_attack = float(input("客队进攻力："))
away_defense = float(input("客队防守力："))

# -------------------------
# 事件影响（比赛中）
# -------------------------

print("\n比赛事件影响（动态）")

home_event = float(input("主队事件影响（红牌=-30 ~ +10）："))
away_event = float(input("客队事件影响（红牌=-30 ~ +10）："))

# -------------------------
# 赔率市场概率（用即时赔率）
# -------------------------

inv = 1/live_home_odds + 1/live_draw_odds + 1/live_away_odds

p_home_m = (1/live_home_odds) / inv
p_draw_m = (1/live_draw_odds) / inv
p_away_m = (1/live_away_odds) / inv

# -------------------------
# 盘口漂移分析（关键）
# -------------------------

def drift(open_odds, live_odds):
    return (live_odds - open_odds) / open_odds

home_drift = drift(open_home_odds, live_home_odds)
away_drift = drift(open_away_odds, live_away_odds)

# -------------------------
# 强度模型
# -------------------------

home_strength = home_attack - away_defense + home_event
away_strength = away_attack - home_defense + away_event

home_strength = max(10, home_strength + 50)
away_strength = max(10, away_strength + 50)

# -------------------------
# xG基础
# -------------------------

base_goals = 2.7

home_xg = base_goals * (home_strength / (home_strength + away_strength))
away_xg = base_goals * (away_strength / (home_strength + away_strength))

# -------------------------
# 时间衰减（越后越保守）
# -------------------------

def time_factor(minute):
    return 1.2 - (minute / 120)

# -------------------------
# 泊松
# -------------------------

def poisson(lam):
    L = math.exp(-lam)
    k = 0
    p = 1
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

# -------------------------
# 模拟比赛（含时间结构）
# -------------------------

def simulate_match():

    h_total = 0
    a_total = 0

    for minute in [15, 45, 75]:

        tf = time_factor(minute)

        h_goal = poisson(home_xg * tf * 0.4)
        a_goal = poisson(away_xg * tf * 0.4)

        h_total += h_goal
        a_total += a_goal

    return h_total, a_total

# -------------------------
# Monte Carlo
# -------------------------

N = 8000

home_win = 0
draw = 0
away_win = 0

score_map = {}

for _ in range(N):

    h, a = simulate_match()

    score = f"{h}-{a}"
    score_map[score] = score_map.get(score, 0) + 1

    if h > a:
        home_win += 1
    elif h == a:
        draw += 1
    else:
        away_win += 1

# -------------------------
# 概率
# -------------------------

p_home = home_win / N
p_draw = draw / N
p_away = away_win / N

# 市场融合 + drift修正
p_home = 0.75 * p_home + 0.25 * p_home_m * (1 + abs(home_drift))
p_draw = 0.75 * p_draw + 0.25 * p_draw_m
p_away = 0.75 * p_away + 0.25 * p_away_m * (1 + abs(away_drift))

total = p_home + p_draw + p_away

p_home /= total
p_draw /= total
p_away /= total

print("\n===== 胜平负概率 =====")

print(f"主胜：{p_home:.2%}")
print(f"平局：{p_draw:.2%}")
print(f"客胜：{p_away:.2%}")

# -------------------------
# Top比分
# -------------------------

sorted_scores = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

print("\n===== 最可能比分 =====")

for s, c in sorted_scores[:3]:
    print(f"{s}  {c/N:.2%}")

# -------------------------
# BTTS & Over
# -------------------------

btts = 0
over25 = 0

for s, c in score_map.items():
    h, a = map(int, s.split("-"))
    p = c / N

    if h > 0 and a > 0:
        btts += p

    if h + a >= 3:
        over25 += p

print("\n===== 扩展市场 =====")

print(f"BTTS：{btts:.2%}")
print(f"大于2.5球：{over25:.2%}")

# -------------------------
# 凯利
# -------------------------

def kelly(p, odds):
    b = odds - 1
    return ((p * b) - (1 - p)) / b

raw = kelly(p_home, live_home_odds)

kelly_fraction = raw * 0.5

print("\n===== 凯利策略 =====")

if kelly_fraction > 0:

    bet = bankroll * kelly_fraction

    print(f"建议下注：{bet:.2f}")

    if raw > 0:
        print("👉 Value Bet")
    else:
        print("⚠️ 边际优势")
else:
    print("❌ 不建议主胜")