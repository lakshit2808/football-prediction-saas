'''
Handling Automatic Logout
================
Stripe Credit Purchase
'''

import streamlit as st
import pandas as pd
import os

from Auth.Register import register
from Auth.Login import login
from AppLogic import Dashboard

# Constants for file paths and OTP settings
USER_DATA_FILE = 'user_data.csv'

def initialize_user_data():
    """Initialize the user data CSV file if it does not exist."""
    if not os.path.isfile(USER_DATA_FILE):
        df = pd.DataFrame(columns=['phone_no', 'email'])
        df.to_csv(USER_DATA_FILE, index=False)

def main():
    initialize_user_data()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        Dashboard()
        if st.sidebar.button('Logout'):
            st.session_state['logged_in'] = False
            st.experimental_rerun()
    else:
        choice = st.sidebar.selectbox('Select an option', ['Login', 'Register'])
        
        if choice == 'Login':
            login()
        elif choice == 'Register':
            register()

if __name__ == "__main__":
    main()