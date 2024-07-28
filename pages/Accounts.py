import streamlit as st

st.set_page_config(page_title="Account Management")

def accounts_page():
    """Accounts Page"""
    # Your accounts page logic here
    st.title('Account Management')

    st.subheader('Change Password')
    current_password = st.text_input('Current Password', type='password')
    new_password = st.text_input('New Password', type='password')

    if st.button('Change Password'):
        if current_password and new_password:
            st.success('Password changed successfully!')
        else:
            st.error('Please fill in all fields.')

    st.subheader('Logout')
    if st.button('Logout'):
        st.session_state.clear()
        st.success('Logged out successfully!')
    

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.error('Please log in to access this page.')
else:
    accounts_page()

