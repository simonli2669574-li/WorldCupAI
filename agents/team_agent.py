from data_loader import load_teams

def get_team(team_name):

    teams = load_teams()

    if team_name not in teams:
        return None

    return teams[team_name]