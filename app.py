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

# Landing Page CSS for animations and styling
st.markdown("""
<style>
    .hero-title {
        font-size: 4rem !important;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .feature-box {
        padding: 20px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s;
    }
    .feature-box:hover {
        transform: translateY(-5px);
        border-color: #4facfe;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='hero-title'>Welcome to {APP_NAME}</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>The Enterprise AI-Powered Data Analytics Platform</div>", unsafe_allow_html=True)

if 'user_id' in st.session_state:
    st.success(f"👋 Welcome back, {st.session_state['username']}! Use the sidebar to continue your analysis.")
    if st.button("Logout", type="primary"):
        for key in ['user_id', 'username', 'role']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
else:
    st.info("🔐 You are currently logged out. Please navigate to the **Login** page in the sidebar to securely access the platform.")

st.markdown("---")
st.markdown("### 🚀 Platform Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-box'>
        <h3>📁 Dataset Manager</h3>
        <p>Securely upload and manage your CSV, Excel, and JSON datasets. Tracks metadata and storage natively.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature-box'>
        <h3>📊 Auto EDA & Profiling</h3>
        <p>Generate deep HTML profiling reports and interact with 9 different Plotly charts instantly.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-box'>
        <h3>🧹 Smart Data Cleaning</h3>
        <p>Impute missing values, drop duplicates, encode categories, and handle outliers with built-in undo capabilities.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature-box'>
        <h3>🤖 Auto-ML Studio</h3>
        <p>Train Classification, Regression, and Clustering models in parallel. View leaderboards and download winning models.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-box'>
        <h3>📈 Dashboard Builder</h3>
        <p>Build custom drag-and-drop style dashboards with dynamic KPI metrics and data visualizations.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature-box'>
        <h3>🧠 AI Insights Engine</h3>
        <p>Calculates Dataset Health Scores, detects hidden anomalies, and generates downloadable Markdown reports.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>Built with ❤️ using Python and Streamlit. Adheres to SOLID Principles & Clean Architecture.</p>", unsafe_allow_html=True)
