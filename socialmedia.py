import requests
from bs4 import BeautifulSoup
import re
import ollama

class RedditPredictor:
    def __init__(self, headers=None):
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        self.headers = headers

    def scrape_google_search_urls(self, query, num_results=10):
        """
        Scrapes Google search result URLs for a given query.

        Args:
        query (str): The search query.
        num_results (int): The number of search results to fetch.

        Returns:
        list: A list of clean URLs from the search results.
        """
        print("Scraping URLS...")
        query = query.replace(' ', '+')
        search_url = f"https://www.google.com/search?q={query}&num={num_results}"

        response = requests.get(search_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        raw_urls = soup.find_all('a', href=True)

        clean_urls = []
        for raw_url in raw_urls:
            href = raw_url['href']
            if 'url?q=' in href and 'reddit.com' in href:
                clean_url = re.search(r'/url\?q=(.*?)&', href).group(1)
                clean_urls.append(clean_url)

        return clean_urls

    def fetch_reddit_post_comments(self, urls):
        """
        Fetches the title, description, and comments from Reddit post JSON URLs.

        Args:
        urls (list): A list of URLs to the Reddit post JSON.

        Returns:
        list: A list of comment bodies.
        """
        print("Fetching Reddit comments...")
        contents = []
        for url in urls:
            try:
                response = requests.get(url + '.json', headers=self.headers).json()

                if len(response) > 1 and 'data' in response[1] and 'children' in response[1]['data']:
                    comments = response[1]['data']['children']

                    for comment in comments:
                        if 'body' in comment['data']:
                            contents.append(comment['data']['body'])
                else:
                    print(f"Unexpected structure in response for URL: {url}")

            except Exception as e:
                print(f"An error occurred while processing URL {url}: {e}")
        return contents

    def most_frequent_team(self, team_list):
        """
        Determines the most frequently mentioned team.

        Args:
        team_list (list): A list of team names.

        Returns:
        str: The most frequently mentioned team.
        """
        print("Most Favoured Team Check...")
        team_count = {}

        for team in team_list:
            if team in team_count:
                team_count[team] += 1
            else:
                team_count[team] = 1

        most_frequent_team = max(team_count, key=team_count.get)
        return most_frequent_team

    def expert_view_prediction(self, team1, team2, contents):
        """
        Predicts the winning team based on Reddit comments.

        Args:
        team1 (str): Name of the first team.
        team2 (str): Name of the second team.
        contents (list): A list of Reddit comment bodies.

        Returns:
        str: The predicted winning team.
        """
        print(f"Analysing Public Views for {len(contents)} Comments...")
        results = []
        team1 = team1.lower()
        team2 = team2.lower()

        for body in contents:
            response = self._get_model_response(body, team1, team2)
            if team1 in response.lower():
                results.append(team1)
            elif team2 in response.lower():
                results.append(team2)


        team1_count = results.count(team1)
        team2_count = results.count(team2)
        total_count = len(results)

        team1_prob = team1_count / total_count if total_count > 0 else 0
        team2_prob = team2_count / total_count if total_count > 0 else 0

        prediction = team1 if team1_prob > team2_prob else team2

        return prediction, team1_prob, team2_prob
    
    def summarize_comments(self, comments, team1, team2, model_name='llama2'):
        """
        Summarizes a list of comments using the specified ollama model.

        Args:
        comments (list): List of comments to summarize.
        model_name (str): Name of the ollama model to use for summarization.

        Returns:
        str: Summary of the comments.
        """
        print('Summarizing Comments...')
        # Combine comments into a single context
        context = " ".join(comments)

        # Define the question for the summary
        question = f"Please provide a summary of the following comments for thoughts on football matche between {team1} and {team2}. Into few bullet points."

        # Generate the prompt
        prompt = f"<s>[INST]\n<<SYS>>\n{question}\n{context}\n<</SYS>>\n\n{{user_prompt}}[/INST]"

        # Call the ollama model to get the summary
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])['message']['content']

        return response

    def _get_model_response(self, body, team1, team2):
        """
        Generates a response from the model based on the given body and teams.

        Args:
        body (str): The content body.
        team1 (str): Name of the first team.
        team2 (str): Name of the second team.

        Returns:
        str: The model's response.
        """
        question = f"Based on the sentiment that {body}, which team is likely to win between {team1} and {team2}? Just give the team name and don't give any reason"
        context = body
        prompt = f"<s>[INST]\n<<SYS>>\n{question}\n{context}\n<</SYS>>\n\n{{user_prompt}}[/INST]"
        response = ollama.chat(model='llama2', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])['message']['content']

        question = f"Based on the sentiment that {response}, which team is likely to win between {team1} and {team2}? Just give the team name and don't give any reason"
        context = response
        prompt = f"<s>[INST]\n<<SYS>>\n{question}\n{context}\n<</SYS>>\n\n{{user_prompt}}[/INST]"
        response = ollama.chat(model='llama2', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])['message']['content']

        return response
    

# home_team = "Philadelphia Union"    
# away_team = "Charlotte"    
# num_posts = 2
# predictor = RedditPredictor()
# reddit_query = f"{home_team} vs {away_team} prediction reddit"
# reddit_urls = predictor.scrape_google_search_urls(reddit_query, num_results=num_posts) 
# reddit_data = predictor.fetch_reddit_post_comments(reddit_urls)
# summary = predictor.summarize_comments(reddit_data, home_team,away_team)
# print(summary)
# reddit_prediction = predictor.expert_view_prediction(home_team, away_team, reddit_data)   
# print(reddit_prediction)