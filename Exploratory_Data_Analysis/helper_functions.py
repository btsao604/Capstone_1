import pandas as pd
import numpy as np

def pace_calculator(FGA, FTA, OREB, OPPDREB, FG, TOV, MIN):
        return 240 * (FGA + 0.4 * FTA - 1.07 * (FGA-FG)* (OREB/(OREB + OPPDREB)) + TOV) / MIN

def points_data(year):
    
    player = '../raw_data/player_stats_'+year+'.csv'
    team = '../raw_data/team_stats_'+year+'.csv'
    player_over='../raw_data/player_overall_15minsplus'+year+'.csv'
    player_position = '../raw_data/player_positions'+year+'.csv'
    starter='../raw_data/starter_bench'+year+'.csv'
    data = pd.read_csv(player)
    team_data = pd.read_csv(team)
    player_overall = pd.read_csv(player_over)
    player_pos = pd.read_csv(player_position)
    starter_bench = pd.read_csv(starter)

    team_data['VS_TEAM_ABBREVIATION'] = team_data['MATCHUP'].str[-3:]
    new_team = team_data[['TEAM_ID','TEAM_ABBREVIATION','VS_TEAM_ABBREVIATION', 'GAME_ID', 'GAME_DATE', 'FGM', 'FTA', 'FGA','OREB','DREB', 'TOV','MIN']]
    cols = ['TEAM_ABBREVIATION','GAME_ID','DREB']
    temp_col = team_data[cols]
    temp_col.columns = ['TEAM_ABBREVIATION','GAME_ID','OPPDREB']
    
    cleaned_team = pd.merge(new_team, temp_col, how='inner', left_on=['GAME_ID','VS_TEAM_ABBREVIATION'], right_on=['GAME_ID','TEAM_ABBREVIATION'], copy=False).drop('TEAM_ABBREVIATION_y', axis=1).rename(columns = {'TEAM_ABBREVIATION_x': 'TEAM_ABBREVIATION'})
    cleaned_team['PACE'] = pace_calculator(FGA = cleaned_team['FGA'], FTA = cleaned_team['FTA'], OREB = cleaned_team['OREB'], OPPDREB=cleaned_team['OPPDREB'], FG = cleaned_team['FGM'], TOV = cleaned_team['TOV'], MIN = cleaned_team['MIN'])
    pace = cleaned_team[['TEAM_ABBREVIATION', 'GAME_ID', 'PACE']]
    cleaned_team2 = pd.merge(cleaned_team, pace, how='inner', left_on=['GAME_ID','VS_TEAM_ABBREVIATION'], right_on=['GAME_ID','TEAM_ABBREVIATION'], copy=False).drop('TEAM_ABBREVIATION_y', axis=1).rename(columns = {'TEAM_ABBREVIATION_x': 'TEAM_ABBREVIATION', 'PACE_x': 'TEAM_PACE', 'PACE_y': 'VS_TEAM_PACE'})
    team_schedule = cleaned_team2[['TEAM_ID','TEAM_ABBREVIATION', 'VS_TEAM_ABBREVIATION','GAME_ID', 'TEAM_PACE', 'VS_TEAM_PACE']].sort_values(['TEAM_ABBREVIATION','GAME_ID'])
    team_schedule['GAME_NUMBER'] = np.array(list(range(82))*30)
    
    player_overall = player_overall[player_overall['GP'] > 30][['PLAYER_ID', 'PLAYER_NAME', 'PTS']]
    players = player_overall['PLAYER_ID'].tolist()
    data = data[data['PLAYER_ID'].isin(players)]
    data_with_number = pd.merge(data, team_schedule, how='left', left_on=['TEAM_ID', 'GAME_ID'], right_on=['TEAM_ID', 'GAME_ID'])
    data_with_number = data_with_number.sort_values(['PLAYER_ID', 'GAME_NUMBER'])    
    data_with_number['YEAR'] = year 
    data_with_number = data_with_number.drop(columns=['Unnamed: 0', 'SEASON_ID','VIDEO_AVAILABLE', 'TEAM_ABBREVIATION_y' ])
    
    data_position = pd.merge(data_with_number,player_pos, how='left', left_on='PLAYER_ID', right_on='PLAYER_ID')
    data_starter_bench = pd.merge(data_position,starter_bench, how='left', left_on='PLAYER_ID', right_on='PLAYER_ID')
    
    return data_starter_bench
