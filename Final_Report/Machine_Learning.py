# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 14:19:42 2018

@author: boris-tsao
"""
import pandas as pd
import numpy as np
from nba_py.player import PlayerSummary
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
seasons = ['2014-15','2015-16','2016-17']
test_set = '2017-18'

df = pd.DataFrame()
for year in seasons:
    temp_df = pd.read_csv("../raw_data/eda_data"+year+".csv")
    df = pd.concat([df, temp_df])
df= df.drop(['FT_PCT'], axis=1)
df = df.dropna(thresh=3)
players = df[(df['CENTER'] == 'C') | (df['FORWARD'] == 'F') | (df['GUARD'] == 'G')]

players = players.replace({'CENTER': 'C', 'FORWARD': 'F', 'GUARD':'G'}, 1)
players = players.fillna(0)

clean_df = players[['TEAM_ABBREVIATION', 'GAME_ID','GAME_NUMBER', 'PLAYER_ID','CENTER', 'GUARD', 'STARTER', 'FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA','PTS' ]]
lis = ['FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA']
lis_modified = [item + '_AVGLAST3GAMES' for item in lis]
dictionary = dict(zip(lis, lis_modified))

lis_YTD= [item + '_YTD' for item in lis]
YTD = dict(zip(lis, lis_YTD))

player_games_grouped = clean_df.set_index(['GAME_ID']).groupby(['PLAYER_ID'])
player_games_threegame = pd.DataFrame(player_games_grouped.rolling(center=False,window=3,win_type='triang')['FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA'].mean().shift()).rename(index=str, columns=dictionary).reset_index()
players_games_ytd = player_games_grouped['FG2M','FG2A','FG3M', 'FG3A', 'FTM', 'FTA'].expanding(min_periods=2).mean().rename(index=str, columns=YTD).reset_index()
player_games = clean_df[['PTS','PLAYER_ID','GAME_ID','GAME_NUMBER','CENTER','GUARD', 'STARTER']]
training_set = pd.merge(player_games_threegame, players_games_ytd, left_on=['PLAYER_ID', 'GAME_ID'], right_on=['PLAYER_ID','GAME_ID'])
training_set['GAME_ID'] = training_set['GAME_ID'].apply(int)
training_set['PLAYER_ID'] = training_set['PLAYER_ID'].apply(int)
second_set = pd.merge(player_games, training_set, left_on=['PLAYER_ID', 'GAME_ID'], right_on=['PLAYER_ID','GAME_ID'])
final_set = second_set.drop(['PLAYER_ID', 'GAME_ID'], axis=1)
evaluate = pd.get_dummies(final_set, drop_first=True)
evaluate = pd.get_dummies(evaluate, columns=['GAME_ID'], drop_first=True)

evaluate = evaluate.dropna()

X = evaluate.drop(['PTS'], axis=1)
y = evaluate[['PTS']]

#Splitting into training set and test set. Training set is used to train your model. Test set is to set the accuracy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Initializing our regressor
regressor = LinearRegression()

#Fitting our training data to the regressor
regressor.fit(X_train, y_train)

#Checking the score
score = regressor.score(X_test, y_test)

X = evaluate.drop(['PTS'], axis=1)
y = evaluate[['PTS']]

#Splitting into training set and test set. Training set is used to train your model. Test set is to set the accuracy
old_X = evaluate[['FG2M_YTD', 'FG2A_YTD', 'FG3M_YTD', 'FG3A_YTD','FTM_YTD', 'FTA_YTD']]

old_X_train, old_X_test, old_y_train, old_y_test = train_test_split(old_X, y, test_size=0.2, random_state=42)

#Initializing our regressor
old_regressor = LinearRegression()

#Fitting our training data to the regressor
old_regressor.fit(old_X_train, old_y_train)

#Checking the score
old_score = old_regressor.score(old_X_test, old_y_test)
