import pandas as pd
import requests
from bs4 import BeautifulSoup

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
    teams_df.to_csv('teams.csv')