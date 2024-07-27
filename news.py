import requests
import ollama
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from time import sleep

class ArticleAnalyzer:
    def __init__(self, team1, team2, totalarticles):
        self.team1 = team1
        self.team2 = team2
        self.totalarticles = totalarticles
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def most_frequent_team(self, team_list):
        print("Most Favoured Team Check...")
        # Initialize a dictionary to count occurrences of each team
        team_count = {}
        
        # Count occurrences of each team in the list
        for team in team_list:
            if team in team_count:
                team_count[team] += 1
            else:
                team_count[team] = 1
        
        # Find the team with the maximum count
        most_frequent_team = None
        max_count = 0
        for team, count in team_count.items():
            if count > max_count:
                max_count = count
                most_frequent_team = team
        
        return most_frequent_team
    
    def get_longest_string(self, str1, str2):
        return str1 if len(str1) > len(str2) else str2
    
    def get_full_article_content(self, urls):
        print("Fetching Content for Articles...")
        contents = []
        for article_url in urls:
            # Check if the URL has a scheme (http:// or https://)
            parsed_url = urlparse(article_url)
            if parsed_url.scheme == '' and parsed_url.netloc == '':
                # Handle relative URLs or malformed URLs here if needed
                continue
            
            # Fetch the article's webpage
            try:
                response = requests.get(article_url, headers=self.headers)
                response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract the full article content from <p>, <span>, and <h1>-<h6> tags
                tags = soup.find_all(['p', 'span'] + [f'h{i}' for i in range(1, 7)])
                full_content = ' '.join([tag.get_text() for tag in tags])
                contents.append(full_content)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching article from {article_url}: {str(e)}")
        
        return contents
    
    def expert_view_prediction(self, contents):
        print(f"Analysing Expert Views for {len(contents)} Articles...")
        results = []
        for body in contents:
            question = f"Based on the sentiment in the article: '{body}', which team is likely to win between {self.team1} and {self.team2}? Just give the team name and don't give any reason, just give name of the team based on the view of author, if it's not understood by you just say NAN"
            context = body
    
            prompt = f"<s>[INST]\n<<SYS>>\n{question}\n{context}\n<</SYS>>\n\n{{user_prompt}}[/INST]"
    
            response = ollama.chat(model='llama2', messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])['message']['content']
    
            question = f"Based on the sentiment that {response}, which team is likely to win between {self.team1} and {self.team2}? Just give the team name and don't give any reason"
            context = response
            prompt = f"<s>[INST]\n<<SYS>>\n{question}\n{context}\n<</SYS>>\n\n{{user_prompt}}[/INST]"
            response = ollama.chat(model='llama2', messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])['message']['content']
    
            if self.team1.lower() in response.lower():
                results.append(self.team1)
            elif self.team2.lower() in response.lower():
                results.append(self.team2)
        
        team1_count = results.count(self.team1)
        team2_count = results.count(self.team2)
        total_count = len(results)

        team1_prob = team1_count / total_count if total_count > 0 else 0
        team2_prob = team2_count / total_count if total_count > 0 else 0

        prediction = self.team1 if team1_prob > team2_prob else self.team2

        return prediction, team1_prob, team2_prob

    def summarize_articles(self, articles,team1, team2, model_name='llama2'):
        """
        Summarizes a list of articles using the specified Ollama model.

        Args:
        articles (list): List of articles to summarize.
        model_name (str): Name of the Ollama model to use for summarization.

        Returns:
        str: Summary of the articles.
        """
        print("Summarizing Articles...")
        # Combine articles into a single context
        context = " ".join(articles)
        
        # Define the question for summarization
        question = f"Please provide a summary of the following articles for thoughts on football matche between {team1} and {team2} in bullet points."
        
        # Generate the prompt
        prompt = f"<s>[INST]\n<<SYS>>\n{question}\n{context}\n<</SYS>>\n\n{{user_prompt}}[/INST]"
        
        # Call the Ollama model to get the summary
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])['message']['content']
        
        return response


    def fetch_article_links(self):
        print("Loading Article Links...")
        team1 = self.team1.replace(" ", "+")
        team2 = self.team2.replace(" ", "+")
        url = f"https://news.google.com/search?for={team1}+vs+{team2}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
    
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all <a> tags with article links
                article_links = []
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        if href.startswith('./articles/') or href.startswith('https://'):
                            href = href[2:]
                            if "articles" in href:
                                article_links.append("https://news.google.com/"+href)
                
                return article_links[:self.totalarticles]  # Return only the first 10 article links
            else:
                print(f"Failed to retrieve content. Status code: {response.status_code}")
                return []
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching article links from {url}: {str(e)}")
            return []
        
# Sample usage of the ArticleAnalyzer class

# Initialize the ArticleAnalyzer with two teams and the number of articles to analyze
# team1 = "Philadelphia Union"
# team2 = "Charlotte"
# total_articles = 5
# analyzer = ArticleAnalyzer(team1, team2, total_articles)

# # Fetch article links related to the match
# article_links = analyzer.fetch_article_links()


# # Retrieve the full content of the fetched articles
# article_contents = analyzer.get_full_article_content(article_links)
# print(article_contents)

# # Perform expert view predictions based on the articles' content
# prediction, team1_prob, team2_prob = analyzer.expert_view_prediction(article_contents)
# print(f"Prediction: {prediction}")
# print(f"Probability for {team1}: {team1_prob * 100:.2f}%")
# print(f"Probability for {team2}: {team2_prob * 100:.2f}%")

# Summarize the comments from the articles
# summary = analyzer.summarize_articles(article_contents,team1,team2)
# print("Summary of the articles:")
# print(summary)
