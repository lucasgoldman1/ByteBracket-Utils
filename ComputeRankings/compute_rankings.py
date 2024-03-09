import pandas as pd
import numpy as np
from scipy import stats

"""
Your module description
"""

def compute_rankings(event, context):
    teams_df, Ws, Ls = get_teams_df()
    
    rank = pd.Series()
    
    rank["W-L%"] = event["WL%"]
    rank["SOS"] = event["SOS"]
    rank["pf"] = event["PPG"]
    rank["pa"] = event["OPPG"]
    rank['KenPom'] = event["kenpom"]
    rank['3P%'] = event["3PM"]
    rank['FT%'] = event["FTM"]
    rank['TOV'] = event["TO"]
    rank['Takeaways'] = event["STL/BLK"]
    rank['Quad1'] = event["Quad1"]


    sum = rank.sum() 
    rank/=sum
    
    for (columnName, columnData) in rank.iteritems(): 
        teams_df[columnName]*= columnData
    
    teams_df['sum'] = 0.0
    for i, row in teams_df.iterrows():
        teams_df.at[i, 'sum'] = row['W-L%':].sum()
    teams_df['W'] = Ws
    teams_df['L'] = Ls
    teams_df.sort_values(by=['sum'], inplace=True, ascending=False)
    
        
    teams_df['zscores'] = (teams_df['sum'] - teams_df['sum'].mean())/teams_df['sum'].std(ddof=0)
    event['Schools'] = list(teams_df.index)
    event['W'] = list(teams_df['W'])
    event['L'] = list(teams_df['L'])
    event['percentiles'] = list(1 - stats.norm.sf(teams_df['zscores']))
    
    return event
    
def get_teams_df():
    teams_df = pd.read_csv('ncaa.csv', index_col=0)
    teams_df.sort_values(by=['School'], inplace=True, ascending=True)
    Ws =  teams_df['W']
    Ls =  teams_df['L']
    teams_df['Takeaways'] = teams_df['STL'] + teams_df['BLK']
    teams_df.drop(['STL', 'x', 'y', 'z', 'h', 'l', 'BLK', 'W', 'L'], axis=1, inplace= True)
    # Normalize data
    for (columnName, columnData) in teams_df.iteritems(): 
        if columnName != 'School':
            print(columnName)
            teams_df[columnName] = stats.zscore(columnData)
    
    # Invert stats that negatively affect a team
    teams_df[['pa', 'TOV']] *= -1
    return teams_df, Ws, Ls