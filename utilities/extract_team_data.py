import pandas as pd
import requests
from bs4 import BeautifulSoup
import boto3
from io import StringIO

BUCKET_NAME = 'bytebracket-ncaab-data'
FILE_KEY = 'ncaab-data.csv'

def extract_team_data():
    url = "https://www.sports-reference.com/cbb/seasons/men/2024-school-stats.html#basic_school_stats"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'basic_school_stats'})

    teams = []
    for row in table.find_all('tr'):
        team = {}
        for val in row.find_all('td'):
            if val.attrs['data-stat'] == 'DUMMY':
                continue
            team[val.attrs['data-stat']] = val.text
        if team:
            teams.append(team)

    teams_df = pd.DataFrame(teams)
    teams_df.set_index('school_name', inplace=True)
    teams_df.drop(['g', 'srs', 'wins_conf', 'losses_conf', 'wins_home', 'losses_home', 'wins_visitor', 'losses_visitor', 'mp', 'fg', 'fga', 'fg_pct', 'fg3', 'fg3a', 'fta', 'ft', 'orb', 'pf'], axis=1, inplace=True)
    return teams_df

def upload_to_s3():
    teams_df = extract_team_data()

    # Convert DataFrame to CSV string
    csv_buffer = StringIO()
    teams_df.to_csv(csv_buffer, index=False)

    # Initialize S3 client
    s3 = boto3.client('s3')

    # Upload CSV string to S3
    s3.put_object(Bucket=BUCKET_NAME, Key=FILE_KEY, Body=csv_buffer.getvalue())

if __name__ == '__main__':
    upload_to_s3()