import pandas as pd
import streamlit as st
import re
from Auth.Login import generate_otp, verify_otp

USER_DATA_FILE = 'user_data.csv'
INIT_CREDIT = 10

def validate_phone_number(phone_number):
    # Simple regex for phone number validation
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    return pattern.match(phone_number)
def validate_email(email):
    # Simple regex for email validation
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return pattern.match(email)


def register_user(name, phone_no, email):
    """Register a new user by appending their data to the CSV file."""
    df = pd.read_csv(USER_DATA_FILE)
    
    if phone_no in df['phone_no'].values :
        return False  # User already exists
    if email in df['email'].values :
        return False  # User already exists
    
    new_user = pd.DataFrame([[name, phone_no, email, INIT_CREDIT]], columns=["name", 'phone_no', 'email', 'credits'])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_DATA_FILE, index=False)
    return True

def register():
    """Handle user registration"""
    st.header('Register')
    name = st.text_input("Name")
    phone_no = st.text_input("Phone", placeholder="+1(123) 456-7890")
    if phone_no:
        if validate_phone_number(phone_no):
            st.success('Phone number is valid!')
        else:
            st.error('Invalid phone number. Please enter a valid phone number.')
    email = st.text_input('Email')
    if email:
        if validate_email(email):
            st.success('Email is valid!')
        else:
            st.error('Invalid Email. Please enter a valid email.')    

    if st.button('Send OTP'):
        otp = generate_otp(email)
        st.session_state['otp'] = otp
        st.session_state['email'] = email
        st.session_state['otp_sent'] = True
        st.success('OTP has been sent to your email. Please check your inbox.')    

    if st.session_state.get('otp_sent'):
        otp_input = st.text_input('Enter OTP', '')
        if st.button('Verify and Register'):
            if verify_otp(otp_input) and email and phone_no:
                if register_user(name, phone_no, email):
                    st.success('OTP verified successfully! You are now Registered. You can Now Proceed with Login')
                    # st.experimental_rerun()
                else:
                    st.error('User already exists. Please choose to login instead of Registering.')
            else:
                st.error('Invalid OTP. Please try again.')                       
    
