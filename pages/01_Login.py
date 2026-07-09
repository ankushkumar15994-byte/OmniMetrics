import streamlit as st
from database.db import get_db
from authentication.auth_service import authenticate_user, create_user, log_activity

st.set_page_config(page_title="Login/Signup", page_icon="🔐")
from utils.ui_utils import load_css
load_css()

st.title("Authentication")

# Create a database session generator
db = next(get_db())

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            user = authenticate_user(db, username, password)
            if user:
                st.session_state['user_id'] = user.id
                st.session_state['username'] = user.username
                st.session_state['role'] = user.role
                log_activity(db, user.id, "User Logged In")
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

with tab2:
    st.header("Sign Up")
    with st.form("signup_form"):
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_btn = st.form_submit_button("Sign Up")
        
        if signup_btn:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not new_username or not new_email or not new_password:
                st.error("Please fill in all fields.")
            else:
                try:
                    create_user(db, new_username, new_email, new_password)
                    st.success("Account created successfully! You can now log in.")
                except ValueError as e:
                    st.error(str(e))
