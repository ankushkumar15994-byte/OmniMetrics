import streamlit as st
from database.db import engine, Base
from config.settings import APP_NAME

# Initialize database tables
Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(f"Welcome to {APP_NAME}")
st.write("""
This is an enterprise-grade AI-powered Data Analytics Web Application.
Please use the sidebar to navigate to the **Login** page to get started.
""")

if 'user_id' in st.session_state:
    st.success(f"Logged in as: {st.session_state['username']} ({st.session_state['role']})")
    if st.button("Logout"):
        for key in ['user_id', 'username', 'role']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
else:
    st.info("You are not logged in. Please navigate to the Login page.")
