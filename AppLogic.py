import streamlit as st
from socialmedia import RedditPredictor
from news import ArticleAnalyzer
from histmodel import FootballPrediction
from probcalc import combine_probabilities
from dotenv import load_dotenv, dotenv_values
import altair as alt
import pandas as pd

USER_DATA_FILE = 'user_data.csv'


def Dashboard():
    """Main app functionality"""
    predict_status = True

    df = pd.read_csv(USER_DATA_FILE)

    # API
    load_dotenv()
    api_key = dotenv_values(".env")["API_FOOTBALL_API_KEY"]

    # User Info
    user_email = st.session_state['email']
    name = df[df['email'] == user_email]['name'].values[0]

    # Streamlit app setup
    st.title(f"Match Prediction Console")
    st.write(f'Welcome to the Match Prediction Console {name}. This app uses machine learning models to predict the \
             outcome of football matches based on historical data, news articles, and Fans View')

    # Credit Management
    credits = df[df['email'] == user_email]['credits'].values[0]
    st.write(f"## Available Credits: {credits}")


    # Add More Credits
    add_credits = st.button("Add More Credits")

    # Sidebar inputs
    st.sidebar.header('Configure Inputs')
    if credits != 0:
        config_status = False
    else:
        st.markdown(
            """
            <div style="background-color: #f8d7da; color: #721c24;margin:15px ; padding: 15px; border: 1px solid #f5c6cb; border-radius: 4px;">
                <strong>Attention:</strong> Your current credits are finished. Please Add more credits now to enable input configurations!
            </div></hr>
            """,
            unsafe_allow_html=True
        )        
        config_status = True

    home_team = st.sidebar.text_input('Home Team', '', disabled=config_status)
    away_team = st.sidebar.text_input('Away Team', '',disabled=config_status)
    date_of_match = st.sidebar.date_input('Date of Match', key='Date', disabled=config_status)
    total_articles = st.sidebar.number_input('Total Articles', 5, disabled=config_status)
    num_posts = st.sidebar.number_input('Number of Posts', 3, disabled=config_status)

    if home_team and away_team:
        predict_status = False
    if st.sidebar.button("Predict", disabled = predict_status):
        st.session_state.clear()

        total_steps = 3  # Total number of processes
        progress = [0]   # Use a list to hold the progress value

        football_prediction = FootballPrediction(api_key)
        predictor = RedditPredictor()
        analyzer = ArticleAnalyzer(home_team, away_team, total_articles)

        def update_progress():
            progress[0] += 1
            st.write(f"Progress: {progress[0]}/{total_steps} completed")

        def chart(ht_prob, at_prob):
            data = {
                'Team': [home_team, away_team],
                'Probability': [ht_prob, at_prob]
            }
            df = pd.DataFrame(data)
            # Display the bar chart
            chart = alt.Chart(df).mark_bar(size=30).encode(
                x=alt.X('Team', axis=alt.Axis(title='')),
                y=alt.Y('Probability', scale=alt.Scale(domain=[0, 1])),
                color=alt.Color('Team', scale=alt.Scale(range=['#1f77b4', '#ff7f0e']))
            ).properties(
                width=300,
                height=200
            )
            return st.altair_chart(chart, use_container_width=True)      

        try:
            with st.spinner("Calculating Match Outcome Based on Poisson Distribution, Team Statistics, Recent Form, and Player Performance..."):
                historical_prediction = football_prediction.get_match_prediction(home_team, away_team, date_of_match)
                st.success("Historical performance prediction complete!")
                update_progress()
        except Exception as e:
            st.error(f"Error Making Performance Prediction: {e}")
            st.stop() 

        try:
            with st.spinner("Analyzing Articles..."):
                article_urls = analyzer.fetch_article_links()
                article_contents = analyzer.get_full_article_content(article_urls)
                article_prediction = analyzer.expert_view_prediction(article_contents)
                st.success("Article analysis complete!")
                update_progress()
        except Exception as e:
            st.error(f"Error analyzing articles: {e}")
            st.stop()     

        try:
            reddit_query = f"{home_team} vs {away_team} prediction reddit"
            reddit_urls = predictor.scrape_google_search_urls(reddit_query, num_results=num_posts)
            reddit_data = predictor.fetch_reddit_post_comments(reddit_urls)
            with st.spinner(f"Analyzing {len(reddit_data)} Reddit Posts..."):
                reddit_prediction = predictor.expert_view_prediction(home_team, away_team, reddit_data)
                st.success("Reddit analysis complete!")
                update_progress()
        except Exception as e:
            st.error(f"Error analyzing reddit posts: {e}")
            st.stop()     

        st.write("Process completed!")

        st.subheader('Result Summary')
        # Display results
        try:
            # Credit Subtraction
            df.loc[df['email'] == user_email, 'credits'] -= 5
            df.to_csv(USER_DATA_FILE, index=False)

            st.markdown("<h4>Article Prediction:</h4>", unsafe_allow_html=True)
            chart(round(article_prediction[1],2), round(article_prediction[2],2))

            st.markdown("<h4>Comment Prediction:</h4>", unsafe_allow_html=True)
            chart(round(reddit_prediction[1],2), round(reddit_prediction[2],2))

            st.markdown("<h4>Historical Prediction:</h4>", unsafe_allow_html=True)
            chart(round(historical_prediction[0],2), round(historical_prediction[1],2))

            # Combine predictions
            combined_prob = combine_probabilities(article_prediction[1:], reddit_prediction[1:], historical_prediction)
            if combined_prob == -1:
                st.write("Draw")
            else:
                st.markdown(f"<h4>Combined Probability for Team 1 {home_team}: {combined_prob[0]:.2f}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>Combined Probability for Team 2 {away_team}: {combined_prob[1]:.2f}</h4>", unsafe_allow_html=True)

                chart(round(combined_prob[0],2), round(combined_prob[1],2))

        except Exception as e:
            st.error(f"Error displaying or combining predictions: {e}")

    else:
        st.sidebar.write("*NOTE:-* Please fill in all input fields to enable the **Predict** button.")