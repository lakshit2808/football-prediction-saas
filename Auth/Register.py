import pandas as pd
import streamlit as st
import re
from Auth.Login import generate_otp, verify_otp
from DBConnection import register_user, referal_code_check, ref_increment_credits, set_referral, increment_credits

INIT_CREDIT = 10

def validate_phone_number(phone_number):
    # Simple regex for phone number validation
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    return pattern.match(phone_number)
def validate_email(email):
    # Simple regex for email validation
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return pattern.match(email)

def register():
    """Handle user registration"""
    st.header('Register')
    name = st.text_input("Name")
    phone_no = st.text_input("Phone", placeholder="+1(123) 456-7890")
    if phone_no:
        if not validate_phone_number(phone_no):
            st.error('Invalid phone number. Please enter a valid phone number.')
    email = st.text_input('Email')
    if email:
        if not validate_email(email):
            st.error('Invalid Email. Please enter a valid email.')    
    referral_code = st.text_input("Referral Code").lower()

    if st.button('Send OTP'):
        otp = generate_otp(email)
        st.session_state['otp'] = otp
        st.session_state['email'] = email
        st.session_state['otp_sent'] = True
        # st.success('OTP has been sent to your email. Please check your inbox.')    

    if st.session_state.get('otp_sent'):
        otp_input = st.text_input('Enter OTP', '')
        if st.button('Verify and Register'):
            if verify_otp(otp_input) and email and phone_no:
                if referral_code == "":
                    if register_user(name, phone_no, email, INIT_CREDIT):
                        st.success('OTP verified successfully! You are now Registered. You can Now Proceed with Login')
                    else:
                        st.error('User already exists. Please choose to login instead of Registering.')
                else:
                    if register_user(name, phone_no, email, INIT_CREDIT):
                        if referal_code_check(referral_code, st):
                            ref_increment_credits(referral_code)
                            set_referral(email, referral_code)
                            increment_credits(email, 5)
                            st.success('Referral code is valid. You have been credited with 5 extra credits.')
                            st.success('OTP verified successfully! You are now Registered. You can Now Proceed with Login')
                        # st.experimental_rerun()
                    else:
                        st.error('User already exists. Please choose to login instead of Registering.')
            else:
                st.error('Invalid OTP. Please try again. Or Regenerate the OTP.')                       
    
