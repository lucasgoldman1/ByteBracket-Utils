import requests
import json

def extract_game_outcomes(API_KEY):
    outcomes_response = requests.get(f'https://api.the-odds-api.com/v4/sports/basketball_ncaab/scores', params={
        'api_key': API_KEY,
        'daysFrom': 1,
    })
    outcomes_json = json.loads(outcomes_response.text)
    outcomes = []
    for outcome in outcomes_json:
        if not outcome['completed']:
            continue
        score = outcome['scores']
        if score[0]['score'] > score[1]['score']:
            outcomes.append((score[0]['name'], score[1]['name']))
        else:
            outcomes.append((score[1]['name'], score[0]['name']))
    return outcomes