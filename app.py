import streamlit as st
from database.db import engine, Base
from config.settings import APP_NAME
from utils.ui_utils import load_css, brand

st.set_page_config(
    page_title=f"{APP_NAME} | OmniMetrics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database tables without changing the existing data layer.
Base.metadata.create_all(bind=engine)
load_css()
brand()

# Sidebar session context
if "user_id" in st.session_state:
    st.sidebar.markdown(
        f'<div class="om-status"><span class="om-dot"></span> Signed in as '
        f'{st.session_state.get("username", "User")}</div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Sign out", use_container_width=True):
        for key in ("user_id", "username", "role"):
            st.session_state.pop(key, None)
        st.rerun()
else:
    st.sidebar.caption("Sign in to unlock your workspace.")

st.markdown(
    '<section class="om-hero">'
    '<div class="om-chip">✦ AI-POWERED ANALYTICS WORKSPACE</div>'
    '<div class="om-hero-title">Turn data into decisions.</div>'
    '<div class="om-hero-copy">Explore, clean, model and communicate your data in one '
    'connected workspace. Move from raw datasets to explainable insights with OmniMetrics.</div>'
    '</section>',
    unsafe_allow_html=True,
)

if "user_id" in st.session_state:
    st.success(f"Welcome back, {st.session_state.get('username', 'there')}. Your analytics workspace is ready.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Workspace", "Active", help="You are authenticated.")
    c2.metric("Analytics modules", "6", help="Dataset, Cleaning, EDA, Dashboard, ML and Insights.")
    c3.metric("Access level", str(st.session_state.get("role", "user")).title())
    st.markdown('<div class="om-section">Continue your workflow</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.page_link("pages/02_Dataset_Manager.py", label="Open Dataset Manager", icon="🗂️", use_container_width=True)
        st.page_link("pages/03_Data_Cleaning.py", label="Clean a dataset", icon="🧹", use_container_width=True)
    with b:
        st.page_link("pages/04_Exploratory_Data_Analysis.py", label="Explore data", icon="📊", use_container_width=True)
        st.page_link("pages/05_Dashboard_Builder.py", label="Build dashboard", icon="📈", use_container_width=True)
    with c:
        st.page_link("pages/06_Machine_Learning.py", label="Train a model", icon="🤖", use_container_width=True)
        st.page_link("pages/07_Insights_Reports.py", label="Generate insights", icon="✨", use_container_width=True)
else:
    st.info("🔐 You are currently logged out. Sign in to access your private analytics workspace.")
    st.page_link("pages/01_Login.py", label="Go to secure login", icon="🔐")
    st.markdown('<div class="om-section">A complete analytics toolkit</div>', unsafe_allow_html=True)
    features = [
        ("🗂️", "Dataset workspace", "Upload, preview and manage CSV, Excel and JSON datasets."),
        ("🧹", "Smart data cleaning", "Impute missing values, remove duplicates, encode and scale features."),
        ("📊", "Exploratory analysis", "Build interactive charts and generate automated profiling reports."),
        ("📈", "Dashboard builder", "Compose KPI metrics and visualizations for your datasets."),
        ("🤖", "Machine learning studio", "Train classification, regression and clustering models."),
        ("✨", "AI insights & reports", "Surface data quality signals, anomalies and recommendations."),
    ]
    cols = st.columns(3)
    for index, (icon, title, copy) in enumerate(features):
        with cols[index % 3]:
            st.markdown(
                f'<div class="om-feature"><div class="om-feature-icon">{icon}</div>'
                f'<div class="om-feature-title">{title}</div>'
                f'<div class="om-feature-copy">{copy}</div></div>',
                unsafe_allow_html=True,
            )
            st.write("")
st.markdown("---")
st.caption("OmniMetrics · Built with Python and Streamlit · Designed for data-driven teams")
