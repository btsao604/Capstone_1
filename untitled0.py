# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 18:03:45 2018

@author: boris-tsao
"""

from nba_py import league
import matplotlib.pyplot as plt
import pandas as pd

def starter_bench(year):
    starters = league.PlayerStats(season=year, starter_bench='Starters').overall()
    starters = starters[['PLAYER_ID','PLAYER_NAME', 'GP']]
    starters = starters.rename(index=str, columns={'GP': 'STARTER_GAMES'})
    bench = league.PlayerStats(season=year, starter_bench='Bench').overall()
    bench = bench[['PLAYER_ID','PLAYER_NAME', 'GP']]
    
    bench = bench.rename(index=str, columns={'GP': 'BENCH_GAMES'})
    starter_bench = pd.merge(starters, bench, how='outer', on=['PLAYER_ID', 'PLAYER_NAME'])
    starter_bench = starter_bench.fillna(0)
    starter_bench['TOTAL_GAMES'] = starter_bench['STARTER_GAMES'] + starter_bench['BENCH_GAMES']
    starter_bench['PERCENT_STARTS'] = starter_bench['STARTER_GAMES'] / starter_bench['TOTAL_GAMES']
    
    starter_bench['STARTER'] = 'IN_BETWEEN'
    starter_bench['STARTER'][starter_bench['PERCENT_STARTS'] > 0.8] = 'YES'
    starter_bench['STARTER'][starter_bench['PERCENT_STARTS'] < 0.2] = 'NO'

    return starter_bench

seasons = ['2014-15', '2015-16', '2016-17', '2017-18']

for year in seasons:
    df = starter_bench(year)
    df.to_csv(path_or_buf="raw_data/starter_bench"+year+".csv")


starter_bench_2014 = starter_bench('2014-15')
starter_bench_2015 = starter_bench('2015-16')
starter_bench_2016 = starter_bench('2016-17')
starter_bench_2017 = starter_bench('2017-18')

plt.subplot(2, 2, 1)
plt.hist(starter_bench_2014['TOTAL_STARTERS'])
plt.title('2014_15')
plt.subplot(2, 2, 2)
plt.hist(starter_bench_2015['TOTAL_STARTERS'])
plt.title('2015_16')
plt.subplot(2, 2, 3)
plt.hist(starter_bench_2016['TOTAL_STARTERS'])
plt.title('2016_17')
plt.subplot(2, 2, 4)
plt.hist(starter_bench_2017['TOTAL_STARTERS'])
plt.title('2017_18')