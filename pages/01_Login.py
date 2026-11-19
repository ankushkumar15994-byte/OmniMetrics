import streamlit as st
from database.db import get_db
from authentication.auth_service import authenticate_user, create_user, log_activity

st.set_page_config(page_title="OmniMetrics - Access Portal", page_icon="🔐", layout="centered")
from utils.ui_utils import load_css
load_css()

# Create database session
db = next(get_db())

# Top Centered Brand Portal Header
st.markdown("""
<div style="text-align: center; margin: 1rem 0 2rem 0;">
    <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); font-size: 28px; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45); margin-bottom: 12px;">
        🔐
    </div>
    <h1 style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; margin: 0;">
        Access <span class="gradient-text">OmniMetrics</span>
    </h1>
    <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 6px;">
        Enterprise Machine Learning & Advanced Analytics Environment
    </p>
</div>
""", unsafe_allow_html=True)

# Auth Tabs
tab1, tab2 = st.tabs(["🔑 Sign In to Workspace", "✨ Register New Account"])

with tab1:
    st.markdown("""
    <div style="margin-bottom: 12px; font-size: 0.88rem; color: #908fa0;">
        Enter your credentials to access your saved datasets, models, and dashboards.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="e.g. data_scientist")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("Sign In →", type="primary", use_container_width=True)
        
        if submit_btn:
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                user = authenticate_user(db, username, password)
                if user:
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.session_state['role'] = user.role
                    log_activity(db, user.id, "User Logged In")
                    st.success(f"Welcome back, {user.username}!")
                    try:
                        st.switch_page("app.py")
                    except Exception:
                        st.rerun()
                else:
                    st.error("Invalid username or password. Please verify your credentials.")

with tab2:
    st.markdown("""
    <div style="margin-bottom: 12px; font-size: 0.88rem; color: #908fa0;">
        Create your localized workspace profile. All data remains encrypted on your machine.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        new_username = st.text_input("Username", placeholder="e.g. alex_ml")
        new_email = st.text_input("Email Address", placeholder="alex@company.com")
        new_password = st.text_input("Choose Password", type="password", placeholder="••••••••")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        signup_btn = st.form_submit_button("Create Account ✨", type="primary", use_container_width=True)
        
        if signup_btn:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not new_username or not new_email or not new_password:
                st.error("Please fill in all required fields.")
            elif len(new_password) < 6:
                st.error("Password should be at least 6 characters long.")
            else:
                try:
                    create_user(db, new_username, new_email, new_password)
                    st.success("Account created successfully! You can now switch to the 'Sign In' tab.")
                except ValueError as e:
                    st.error(str(e))

st.markdown("""
<div style="text-align: center; margin-top: 2rem; font-size: 0.8rem; color: #908fa0;">
    🛡️ Session secured with SHA-256 hashed credentials and local SQLite storage.
</div>
""", unsafe_allow_html=True)
