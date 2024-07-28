import streamlit as st
from Auth.Login import login
from Auth.Register import register
from DBConnection import get_user_data, set_referral_code

def referral():
    email = st.session_state['email']
    data = get_user_data(email)

    ref_code = data['email'][:3]+data['phone_no'][-4:]
    set_referral_code(email, ref_code)
    if st.sidebar.button('Logout'):
        st.session_state['logged_in'] = False
        st.experimental_rerun()    
    st.title("Invite Your Friends and Earn Credits!")
    st.subheader("Share the love and get rewarded when your friends join us.")
    
    st.markdown("### You Earn")
    st.write("Get 10 Credits for each friend who signs up.")
    
    st.markdown("### They Earn")
    st.write("Your friends get 5 extra Credits. Summing 10 + 5 = 15 Credits")
    
    st.markdown("## How It Works")
    st.write("1. Share your unique code.")
    st.write("2. Your friend signs up using your code.")
    st.write("3. You both receive your credits once they complete their first registeration.")
    
    st.markdown("## Your Referral Link/Code")
    st.code(ref_code.upper())


if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    choice = st.sidebar.selectbox('Select an option', ['Login', 'Register'])
    
    if choice == 'Login':
        login()
    elif choice == 'Register':
        register()
else:
    referral()
