import streamlit as st
from DBConnection import insert_feedback, get_name, increment_credits, add_feedback_status, get_feedback_status
from Auth.Login import login
from Auth.Register import register

def feedback():
    st.title("FPC Feedback Form")
    # Define the marketing message
    marketing_message = """
    # Your Opinion Matters!

    We continuously strive to improve our product and provide you with the best possible experience. Your feedback is invaluable to us, and we would love to hear from you!

    ## Submit Your Feedback and Earn 20 Credits!

    ### Why Participate?

    - **Help Us Improve**: Your insights will help us make our product even better.
    - **Earn Rewards**: As a token of our appreciation, you'll receive 20 credits upon submitting your feedback.
    - **Be Heard**: Your suggestions and comments directly influence our development priorities.

    ### How to Participate?

    1. **Fill Out the Feedback Form**: Share your thoughts, experiences, and suggestions about our product.
    2. **Submit**: Simply submit the form and we'll take care of the rest.
    3. **Receive Your Credits**: After submission, 20 credits will be added to your account as a thank you.
    """
    if st.sidebar.button('Logout'):
        st.session_state['logged_in'] = False
        st.experimental_rerun()             

    # Display the marketing message
    st.markdown(marketing_message)


    user_email = st.session_state['email']
    name = get_name(user_email)
    feedback_credit = 20

    feedback_status = get_feedback_status(user_email,st)

    with st.form(key='feedback_form'):
        # User Information
        st.subheader("User Information")
        name = st.text_input("Name (optional)", name)
        email = st.text_input("Email Address", user_email)
        
        # Company Information
        st.subheader("Company Information")
        company_name = st.text_input("Company Name")
        role_title = st.text_input("Role/Title")
        
        # Product Usage
        st.subheader("Product Usage")
        usage_duration = st.selectbox(
            "How long have you been using the product?",
            ["Less than a month", "1-6 months", "6-12 months", "More than a year"]
        )
        usage_frequency = st.selectbox(
            "How frequently do you use the product?",
            ["Daily", "Weekly", "Monthly", "Rarely"]
        )
        
        # Overall Satisfaction
        st.subheader("Overall Satisfaction")
        overall_satisfaction = st.slider(
            "Overall, how satisfied are you with the product?",
            1, 10
        )
        
        # Feature-specific Feedback
        st.subheader("Feature-specific Feedback")
        most_used_features = st.text_area(
            "Which features do you use the most?"
        )
        most_valuable_features = st.text_area(
            "Which features do you find the most valuable?"
        )
        least_valuable_features = st.text_area(
            "Which features do you find the least valuable?",
        )
        
        # Usability and Experience
        st.subheader("Usability and Experience")
        ease_of_use = st.slider(
            "How easy is it to use the product?",
            1, 10
        )
        difficult_features = st.text_area(
            "Are there any features you find difficult to use?"
        )
        
        # Product Performance
        st.subheader("Product Performance")
        reliability = st.slider(
            "How reliable is the product?",
            1, 10
        )
        bugs_issues = st.text_area(
            "Have you encountered any bugs or issues?"
        )
        
        # Support and Documentation
        st.subheader("Support and Documentation")
        customer_support = st.slider(
            "How would you rate the quality of our customer support?",
            1, 10
        )
        documentation_quality = st.slider(
            "How would you rate the quality of our documentation?",
            1, 10
        )
        
        # Pricing and Value
        st.subheader("Pricing and Value")
        value_for_money = st.slider(
            "How would you rate the product's value for money?",
            1, 10
        )
        fair_pricing = st.selectbox(
            "Do you think the product is fairly priced?",
            ["Yes", "No", "Not Sure"]
        )
        pricing_suggestions = st.text_area(
            "Any suggestions for pricing?"
        )
        
        # Suggestions for Improvement
        st.subheader("Suggestions for Improvement")
        future_features = st.text_area(
            "What features would you like to see in future updates?"
        )
        other_suggestions = st.text_area(
            "Do you have any other suggestions or feedback?"
        )
        
        # Net Promoter Score (NPS)
        st.subheader("Net Promoter Score (NPS)")
        nps = st.slider(
            "How likely are you to recommend our product to others?",
            0, 10
        )
        
        # Additional Feedback
        st.subheader("Additional Feedback")
        additional_comments = st.text_area(
            "Any additional comments or feedback?"
        )
        
        # Submit Button
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            feedback_data = {
                "name": name,
                "email": email,
                "company_name": company_name,
                "role_title": role_title,
                "usage_duration": usage_duration,
                "usage_frequency": usage_frequency,
                "overall_satisfaction": overall_satisfaction,
                "most_used_features": most_used_features,
                "most_valuable_features": most_valuable_features,
                "least_valuable_features": least_valuable_features,
                "ease_of_use": ease_of_use,
                "difficult_features": difficult_features,
                "reliability": reliability,
                "bugs_issues": bugs_issues,
                "customer_support": customer_support,
                "documentation_quality": documentation_quality,
                "value_for_money": value_for_money,
                "fair_pricing": fair_pricing,
                "pricing_suggestions": pricing_suggestions,
                "future_features": future_features,
                "other_suggestions": other_suggestions,
                "nps": nps,
                "additional_comments": additional_comments
            }
            if insert_feedback(feedback_data, st):
                if not feedback_status:
                    increment_credits(email,feedback_credit)
                    add_feedback_status(email, True)
                st.success("Thank you for your feedback! 20 credits have been added to your account.")


if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    choice = st.sidebar.selectbox('Select an option', ['Login', 'Register'])
    
    if choice == 'Login':
        login()
    elif choice == 'Register':
        register()
else:
    feedback()

