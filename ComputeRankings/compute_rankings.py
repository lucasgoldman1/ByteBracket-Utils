import pandas as pd
import numpy as np
from scipy import stats
import pandas as pd
import boto3
from io import StringIO
import os

# Define your S3 bucket and key
BUCKET_NAME = os.environ['BUCKET_NAME'] 
FILE_KEY = os.environ['FILE_KEY']


def compute_rankings(event, context):
    teams_df, Ws, Ls = get_teams_df()
    
    rank = pd.Series()
    
    rank["win_loss_pct"] = event["WL%"]
    rank["sos"] = event["SOS"]
    rank["pts"] = event["PPG"]
    rank["opp_pts"] = event["OPPG"]
    rank['trb'] = event["REB"]
    rank['fg3_pct'] = event["3PM"]
    rank['ft_pct'] = event["FTM"]
    rank['tov'] = event["TO"]
    rank['takeaways'] = event["STL/BLK"]
    rank['ast'] = event["AST"]


    sum = rank.sum() 
    rank/=sum
    
    for (columnName, columnData) in rank.items(): 
        teams_df[columnName]*= columnData
    
    teams_df['sum'] = 0.0
    for i, row in teams_df.iterrows():
        teams_df.at[i, 'sum'] = row['win_loss_pct':].sum()
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
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Read CSV file from S3
    response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    csv_content = response['Body'].read().decode('utf-8')

    # Convert CSV content to DataFrame
    teams_df = pd.read_csv(StringIO(csv_content), index_col=0)
    teams_df.sort_values(by=['school_name'], inplace=True, ascending=True)
    Ws =  teams_df['wins']
    Ls =  teams_df['losses']
    teams_df['takeaways'] = teams_df['stl'] + teams_df['blk']
    teams_df.drop(['stl','blk', 'wins', 'losses'], axis=1, inplace= True)
    # Normalize data
    for (columnName, columnData) in teams_df.items(): 
        if columnName != 'school_name':
            print(columnName)
            teams_df[columnName] = stats.zscore(columnData)
    
    # Invert stats that negatively affect a team
    teams_df[['opp_pts', 'tov']] *= -1
    return teams_df, Ws, Ls