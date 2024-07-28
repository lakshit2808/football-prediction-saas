import pyotp
import smtplib
from email.message import EmailMessage
import streamlit as st
import re
import pandas as pd

def validate_email(email):
    # Simple regex for email validation
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return pattern.match(email)

OTP_SECRET = 'JBSWY3DPEHPK3PXP'  # Use a more secure method for production
app_pass = "uspv zxqm heml avwt"
app_email = "kanwalakshit@gmail.com"
USER_DATA_FILE = 'user_data.csv'

def generate_otp(email):
    """Generate and send an OTP to the user's email."""
    totp = pyotp.TOTP(OTP_SECRET, interval = 300)
    otp = totp.now()
    
    # Send the OTP via email
    server = smtplib.SMTP("smtp.gmail.com", 587 )
    server.starttls()
    server.login(app_email, app_pass)
    msg = EmailMessage()
    msg['From'] = app_email
    msg['To'] = email
    msg['Subject'] = 'Your OTP Code'
    msg.set_content(f'Your OTP   is {otp}')
    server.send_message(msg)
    return otp

def verify_otp(otp_input):
    """Verify the provided OTP."""
    totp = pyotp.TOTP(OTP_SECRET, interval= 300)

    return totp.verify(otp_input)

def login():
    """Handle user login"""
    st.header('Login')
    df = pd.read_csv(USER_DATA_FILE)
    email = st.text_input('Email', '')

    if email:
        if not validate_email(email):
            st.error('Invalid Email. Please enter a valid email.')       
        if email not in df['email'].values :
            st.error('Email not found, Please Register Yourself.')

    if st.button('Send OTP'):
        otp = generate_otp(email)
        st.session_state['otp'] = otp
        st.session_state['email'] = email
        st.session_state['otp_sent'] = True
        st.success('OTP has been sent to your email. Please check your inbox.')

    if st.session_state.get('otp_sent'):
        otp_input = st.text_input('Enter OTP', '')
        if st.button('Verify OTP'):
            if verify_otp(otp_input):
                st.session_state['logged_in'] = True
                st.session_state['otp_sent'] = False
                st.success('OTP verified successfully! You are now logged in.')
                st.experimental_rerun()
            else:
                st.error('Invalid OTP. Please try again.')