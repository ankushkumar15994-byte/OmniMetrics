import streamlit as st
from database.db import get_db
from authentication.auth_service import authenticate_user, create_user, log_activity
from utils.ui_utils import load_css, brand, page_header

st.set_page_config(page_title="Sign in | OmniMetrics", page_icon="🔐", layout="wide")
load_css()
brand()
page_header("Your workspace, secured.", "Sign in or create an account to access your analytics workspace.", "IDENTITY & ACCESS")

if "user_id" in st.session_state:
    st.success(f"You're already signed in as {st.session_state.get('username', 'User')}.")
    if st.button("Return to workspace", type="primary"):
        st.switch_page("app.py")
else:
    left, center, right = st.columns([1, 1.25, 1])
    with center:
        db = next(get_db())
        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            st.markdown("### Welcome back")
            st.caption("Enter your credentials to continue.")
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Your username")
                password = st.text_input("Password", type="password", placeholder="Your password")
                submitted = st.form_submit_button("Sign in securely", type="primary", use_container_width=True)
                if submitted:
                    user = authenticate_user(db, username, password)
                    if user:
                        st.session_state.update(user_id=user.id, username=user.username, role=user.role)
                        log_activity(db, user.id, "User Logged In")
                        st.success("Signed in successfully.")
                        st.switch_page("app.py")
                    else:
                        st.error("Invalid username or password.")
        with signup_tab:
            st.markdown("### Create your account")
            st.caption("Set up your personal analytics workspace.")
            with st.form("signup_form", clear_on_submit=True):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="name@company.com")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
                if submitted:
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif not new_username or not new_email or not new_password:
                        st.error("Please complete all fields.")
                    else:
                        try:
                            create_user(db, new_username, new_email, new_password)
                            st.success("Account created. You can now sign in.")
                        except ValueError as exc:
                            st.error(str(exc))
