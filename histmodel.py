import requests
from time import sleep

class FootballPrediction:
    def __init__(self, api_key, delay=0):
        self.api_key = api_key
        self.delay = delay
        self.headers = {'x-rapidapi-key': api_key}
    
    def get_team_id(self, team_name):
        url = f"https://v3.football.api-sports.io/teams?name={team_name}"
        response = requests.get(url, headers=self.headers)
        sleep(self.delay)
        data = response.json().get('response', [])
        
        for team in data:
            if team['team']['name'] == team_name:
                return team['team']['id']
        return None

    def get_fixture_id(self, team_1, team_2, date_of_match):
        team_id_1 = self.get_team_id(team_1)
        team_id_2 = self.get_team_id(team_2)

        if not team_id_1:
            raise ValueError(f"Team ID for {team_1} could not be found. Try a different name or match.")
        if not team_id_2:
            raise ValueError(f"Team ID for {team_2} could not be found. Try a different name or match.")

        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={team_id_1}-{team_id_2}&date={date_of_match}"
        response = requests.get(url, headers=self.headers)
        sleep(self.delay)
        data = response.json().get('response', [{}])
        
        if not data:
            raise ValueError("No fixtures found for the given teams and date.")
        
        return data[0]['fixture']['id']

    def get_prediction(self, fixture_id):
        if not fixture_id:
            raise ValueError("No match found for the given fixture ID.")
        
        url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
        response = requests.get(url, headers=self.headers)
        sleep(self.delay)
        data = response.json().get('response', [{}])
        
        if not data:
            raise ValueError("No predictions found for the given fixture ID.")
        
        return data[0]['predictions']['percent']

    def get_match_prediction(self, team_1, team_2, date_of_match):
        fixture_id = self.get_fixture_id(team_1, team_2, date_of_match)
        prediction = self.get_prediction(fixture_id)
        
        home_win = int(prediction['home'].strip('%'))
        away_win = int(prediction['away'].strip('%'))
        draw = int(prediction['draw'].strip('%'))
        
        total_prob = home_win + away_win
        return [home_win/total_prob, away_win/total_prob]


# # Usage
# api_key = "69e9ab5f5c6b12f89c5a06cc50b3b106"
# football_prediction = FootballPrediction(api_key)

# team1 = 'Seattle Sounders'
# team2 = 'Minnesota United FC'
# date_of_match = "2024-07-27"

# try:
#     prediction = football_prediction.get_match_prediction(team1, team2, date_of_match)
#     print(prediction)
# except ValueError as e:
#     print(e)
