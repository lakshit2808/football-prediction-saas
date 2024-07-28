import streamlit as st
from DBConnection import get_user_data, update_user_data
from Auth.Login import generate_otp, verify_otp, login
from Auth.Register import register


st.set_page_config(page_title="Account Management")

payment_url = "https://buy.stripe.com/test_7sI8xW8UYglea1aaEE"



def accounts_page():
    """Accounts Page"""
    # Your accounts page logic here
    st.title('Account Management')
    
    email = st.session_state['email']
    user_data = get_user_data(email=email)
    credits = user_data.get("credits")
    st.write(f"## Available Credits: {credits}")
    # Add More Credits
    st.link_button("Add More Credits", payment_url)  

    if st.sidebar.button('Logout'):
        st.session_state['logged_in'] = False
        st.experimental_rerun()   

    if user_data:
        st.subheader("User Details")

        user_id = user_data.get("_id")
        name = st.text_input("Name", user_data.get("name"))
        phone_no = st.text_input("Phone Number", user_data.get("phone_no"))
        email = st.text_input("Email", user_data.get("email"))
        

        st.subheader("Address")
        address = user_data.get("address", {})
        city = st.text_input("City", address.get("city"))
        state = st.text_input("State", address.get("state"))
        country = st.text_input("Country", address.get("country"))

        if st.button("Update User"):
            otp = generate_otp(email)
            st.session_state['otp'] = otp
            st.session_state['email'] = email
            st.session_state['otp_sent'] = True
            # st.success('OTP has been sent to your email. Please check your inbox.')

        if st.session_state.get('otp_sent'):
            otp_input = st.text_input('Enter OTP', '')
            if st.button('Verify OTP'):
                if verify_otp(otp_input):
                    st.session_state['logged_in'] = True
                    st.session_state['otp_sent'] = False
                    updated_data = {
                        "name": name,
                        "phone_no": phone_no,
                        "email": email,
                        "credits": credits,
                        "address": {
                            "city": city,
                            "state": state,
                            "country": country
                        }
                    }

                    if update_user_data(user_id, updated_data):
                        st.success("User updated successfully!")
                    else:
                        st.error("Failed to update user.")
                else:
                    st.error('Invalid OTP. Please try again. Or Regenerate the OTP')


    else:
        st.error("User not found.")

    

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    choice = st.sidebar.selectbox('Select an option', ['Login', 'Register'])
    
    if choice == 'Login':
        login()
    elif choice == 'Register':
        register()
else:
    accounts_page()

