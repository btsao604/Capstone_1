# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 19:19:09 2018

@author: boris-tsao
"""
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
    new_team = team_data[['TEAM_ID','TEAM_ABBREVIATION','VS_TEAM_ABBREVIATION', 'GAME_ID', 'GAME_DATE', 'FGM', 'FTA', 'FGA','OREB','DREB', 'TOV','MIN', 'PTS']]
    cols = ['TEAM_ABBREVIATION','GAME_ID','DREB', 'PTS']
    temp_col = team_data[cols]
    temp_col.columns = ['TEAM_ABBREVIATION','GAME_ID','OPPDREB', 'OPPPTS']
    
    cleaned_team = pd.merge(new_team, temp_col, how='inner', left_on=['GAME_ID','VS_TEAM_ABBREVIATION'], right_on=['GAME_ID','TEAM_ABBREVIATION'], copy=False).drop('TEAM_ABBREVIATION_y', axis=1).rename(columns = {'TEAM_ABBREVIATION_x': 'TEAM_ABBREVIATION'})
    cleaned_team['PACE'] = pace_calculator(FGA = cleaned_team['FGA'], FTA = cleaned_team['FTA'], OREB = cleaned_team['OREB'], OPPDREB=cleaned_team['OPPDREB'], FG = cleaned_team['FGM'], TOV = cleaned_team['TOV'], MIN = cleaned_team['MIN'])
    pace = cleaned_team[['TEAM_ABBREVIATION', 'GAME_ID', 'PACE']]
    cleaned_team2 = pd.merge(cleaned_team, pace, how='inner', left_on=['GAME_ID','VS_TEAM_ABBREVIATION'], right_on=['GAME_ID','TEAM_ABBREVIATION'], copy=False).drop('TEAM_ABBREVIATION_y', axis=1).rename(columns = {'TEAM_ABBREVIATION_x': 'TEAM_ABBREVIATION', 'PACE_x': 'TEAM_PACE', 'PACE_y': 'VS_TEAM_PACE'})
    cleaned_team2['OFF_RATING'] = 100*cleaned_team2['PTS'] / (0.5 * cleaned_team2['MIN']*(cleaned_team2['TEAM_PACE'] + cleaned_team2['VS_TEAM_PACE'])/240)
    cleaned_team2['DEF_RATING'] = 100*cleaned_team2['OPPPTS'] / (0.5 * cleaned_team2['MIN']*(cleaned_team2['TEAM_PACE'] + cleaned_team2['VS_TEAM_PACE'])/240)
    team_schedule = cleaned_team2[['TEAM_ID','TEAM_ABBREVIATION', 'VS_TEAM_ABBREVIATION','GAME_ID', 'TEAM_PACE', 'OFF_RATING', 'DEF_RATING']].sort_values(['TEAM_ABBREVIATION','GAME_ID']).reset_index(drop=True)
    team_schedule['GAME_NUMBER'] = np.array(list(range(82))*30)
    
    grouped_team = team_schedule.groupby(['TEAM_ID'])
    ytd_team = grouped_team['TEAM_PACE', 'OFF_RATING','DEF_RATING'].expanding(min_periods=2).mean().rename(index=str).reset_index()
    final_team = team_schedule.drop(columns=['TEAM_PACE','OFF_RATING', 'DEF_RATING'])
    final_team['PACE'] = ytd_team['TEAM_PACE']
    final_team['OFF_RATING'] = ytd_team['OFF_RATING']
    final_team['DEF_RATING'] = ytd_team['DEF_RATING']
    dummy_df = final_team[['GAME_ID', 'TEAM_ABBREVIATION', 'DEF_RATING', 'PACE']]
    dummy_df = dummy_df.rename(columns={'DEF_RATING': 'OPP_DEF_RATING', 'PACE':'OPP_PACE'})
    final_team = final_team.merge(dummy_df, left_on=['GAME_ID', 'VS_TEAM_ABBREVIATION'], right_on=['GAME_ID', 'TEAM_ABBREVIATION'])
    
    player_overall = player_overall[player_overall['GP'] > 30][['PLAYER_ID', 'PLAYER_NAME', 'PTS','MIN']]
    player_overall = player_overall[['PLAYER_ID', 'MIN']]
    player_overall = player_overall.rename(columns={'MIN': 'AVERAGE_MIN'})
    player_overall['ALL_STAR'] = np.where(player_overall['AVERAGE_MIN']>=32, 'YES', 'NO')
    player_overall = player_overall.drop(columns='AVERAGE_MIN')
    players = player_overall['PLAYER_ID'].tolist()
    data = data[data['PLAYER_ID'].isin(players)]
    data = pd.merge(data, player_overall, how='left', left_on=['PLAYER_ID'], right_on=['PLAYER_ID'])
    data_with_number = pd.merge(data, final_team, how='left', left_on=['TEAM_ID', 'GAME_ID'], right_on=['TEAM_ID', 'GAME_ID'])
    data_with_number = data_with_number.sort_values(['PLAYER_ID', 'GAME_NUMBER'])    
    data_with_number['YEAR'] = year 
    data_with_number = data_with_number.drop(columns=['Unnamed: 0', 'SEASON_ID','VIDEO_AVAILABLE', 'TEAM_ABBREVIATION_y' ])
    
    data_position = pd.merge(data_with_number,player_pos, how='left', left_on='PLAYER_ID', right_on='PLAYER_ID')
    data_starter_bench = pd.merge(data_position,starter_bench, how='left', left_on='PLAYER_ID', right_on='PLAYER_ID')
    data_starter_bench['SEASON'] = year
    data_starter_bench['FG2M'] = data_starter_bench['FGM'] -  data_starter_bench['FG3M']
    data_starter_bench['FG2A'] = data_starter_bench['FGA'] -  data_starter_bench['FG3A']
    data_starter_bench= data_starter_bench.drop(['Unnamed: 0_y','PLAYER_NAME_y', 'Unnamed: 0_x', 'FG3_PCT', 'FG_PCT','FT_PCT'], axis=1)
    data_starter_bench = data_starter_bench.rename(columns={'TEAM_ABBREVIATION_x': 'TEAM_ABBREVIATION', 'PLAYER_NAME_x': 'PLAYER_NAME'})
    data_starter_bench = data_starter_bench.drop(['FGM','FGA','PLUS_MINUS','checker','OREB', 'DREB', 'REB', 'AST','STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS','STARTER_GAMES','BENCH_GAMES','TOTAL_GAMES', 'PERCENT_STARTS'], axis=1)
    return data_starter_bench

training_set = ['2014-15', '2015-16', '2016-17']
test_set = '2017-18'
#training
points_data2014 = points_data('2014-15')
points_data2015 = points_data('2015-16')
points_data2016 = points_data('2016-17')

#test
test_preclean = points_data('2017-18')

def data_cleaning(dataframe):
    df = dataframe
    df['HOME_AWAY'] = np.where(df.MATCHUP.str.contains("@"), "AWAY","HOME")
    clean_df = df[['TEAM_ABBREVIATION', 'GAME_ID','GAME_NUMBER','HOME_AWAY', 'PLAYER_ID','C', 'G', 'ALL_STAR','STARTER','MIN', 'FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA','PTS', 'PACE', 'OFF_RATING','OPP_PACE','OPP_DEF_RATING' ]]
    clean_df['MIN_LASTGAME'] = clean_df.MIN.shift(1)
    clean_df['FG2M_LASTGAME'] = clean_df.FG2M.shift(1)
    clean_df['FG2A_LASTGAME'] = clean_df.FG2A.shift(1)
    clean_df['FG3M_LASTGAME']= clean_df.FG3M.shift(1)
    clean_df['FG3A_LASTGAME']= clean_df.FG3A.shift(1)
    clean_df['FTM_LASTGAME']= clean_df.FTM.shift(1)
    clean_df['FTA_LASTGAME']= clean_df.FTA.shift(1)
    lis = ['PTS','MIN','FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA']
    lis_modified = [item + '_AVGLAST3GAMES' for item in lis]
    dictionary = dict(zip(lis, lis_modified))
    lis_YTD= [item + '_YTD' for item in lis]
    YTD = dict(zip(lis, lis_YTD))

    player_games_grouped = clean_df.set_index(['GAME_ID']).groupby(['PLAYER_ID'])
    player_games_threegame = pd.DataFrame(player_games_grouped.rolling(center=False,window=3,win_type='triang')['PTS','MIN','FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA'].mean().shift()).rename(index=str, columns=dictionary).reset_index()
    players_games_ytd = player_games_grouped['PTS','MIN','FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA'].expanding(min_periods=2).mean().rename(index=str, columns=YTD).reset_index()
    player_games = clean_df[['PTS','PLAYER_ID','GAME_ID','HOME_AWAY','GAME_NUMBER','C','G', 'ALL_STAR','STARTER','MIN_LASTGAME', 'FG2M_LASTGAME','FG2A_LASTGAME','FG3M_LASTGAME', 'FG3A_LASTGAME','FTM_LASTGAME','FTA_LASTGAME','PACE', 'OFF_RATING','OPP_PACE','OPP_DEF_RATING']]
    training_set = pd.merge(player_games_threegame, players_games_ytd, left_on=['PLAYER_ID', 'GAME_ID'], right_on=['PLAYER_ID','GAME_ID'])
    training_set['GAME_ID'] = training_set['GAME_ID'].apply(int)
    training_set['PLAYER_ID'] = training_set['PLAYER_ID'].apply(int)
    second_set = pd.merge(player_games, training_set, left_on=['PLAYER_ID', 'GAME_ID'], right_on=['PLAYER_ID','GAME_ID'])
    observation_set = second_set.drop(['PLAYER_ID', 'GAME_ID'], axis=1)
    learning_set = pd.get_dummies(observation_set, drop_first=True)
    learning_set = pd.get_dummies(learning_set, columns=['GAME_NUMBER'], drop_first=True)
    learning_set = learning_set.dropna()
    observation_set = observation_set.dropna()
    return observation_set

training_2014 = data_cleaning(points_data2014)
training_2015 = data_cleaning(points_data2015)
training_2016 = data_cleaning(points_data2016)

test_observation = data_cleaning(test_preclean)

training_observation=pd.concat([training_2014,training_2015,training_2016])
dictionary = {'test_observation' :test_observation,'training_observation': training_observation}
for key, df in dictionary.items():
    df.to_csv(path_or_buf="../final_dataset/"+key+".csv")
