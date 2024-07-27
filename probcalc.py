def combine_probabilities(news_prob, sentiment_prob, historical_prob, weights=None):
    # Check for zero probabilities and adjust weights accordingly
    adjusted_weights = [1/3, 1/3, 1/3] if weights is None else weights.copy()
    
    # Adjust weights based on non-zero probabilities
    total_weights = 0
    for i, prob in enumerate([news_prob, sentiment_prob, historical_prob]):
        if prob[0] == 0 and prob[1] == 0:
            adjusted_weights[i] = 0
        total_weights += adjusted_weights[i]
    
    # Normalize weights to ensure they sum to 1
    if total_weights != 0:
        adjusted_weights = [w / total_weights for w in adjusted_weights]
    
    combined_prob_team1 = (adjusted_weights[0] * news_prob[0] + 
                           adjusted_weights[1] * sentiment_prob[0] + 
                           adjusted_weights[2] * historical_prob[0])
    
    combined_prob_team2 = (adjusted_weights[0] * news_prob[1] + 
                           adjusted_weights[1] * sentiment_prob[1] + 
                           adjusted_weights[2] * historical_prob[1])
    
    if combined_prob_team1 == combined_prob_team2:
        return -1 # Draw
    
    return (combined_prob_team1, combined_prob_team2)

# Example usage
# news_prob = [0.4, 0.6]
# sentiment_prob = [0.5, 0.5]
# historical_prob = [1, 0]
# print(combine_probabilities(news_prob, sentiment_prob, historical_prob))
