import streamlit as st
from database.db import engine, Base, SessionLocal
from database.models import User, Dataset, ActivityLog
from config.settings import APP_NAME

# Initialize database tables
Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui_utils import load_css
load_css()

if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
    username = st.session_state['username']
    
    # Fetch real metrics from DB
    db = SessionLocal()
    total_datasets = db.query(Dataset).filter(Dataset.owner_id == user_id).count()
    recent_activity = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).order_by(ActivityLog.timestamp.desc()).limit(6).all()
    total_activities = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).count()
    db.close()
    
    # Top Telemetry Header
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <div style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 600; color: #908fa0; text-transform: uppercase; letter-spacing: 0.05em;">
            <span class="pulse-dot"></span>
            <span style="color: #45dfa4;">Live Telemetry Stream Active</span>
            <span style="color: #464554;">•</span>
            <span style="color: #c7c4d7; font-family: monospace;">US-EAST-PRIMARY-01</span>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 8px;">
            <span class="badge badge-live">Sync Cadence: 5s</span>
            <span class="badge badge-purple">OmniEngine v3.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.03em;">
            Welcome back, <span class="gradient-text">{username}</span> 👋
        </h1>
        <p style="color: var(--text-secondary); font-size: 1.05rem; margin-top: 6px;">
            Your analytics workspace at a glance. Real-time telemetry, model drift metrics, and active pipelines.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # High-Density KPI Metric Grid
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            label="Total Datasets",
            value=f"{total_datasets}",
            delta="+Active in Storage" if total_datasets > 0 else "No files yet"
        )
    with kpi2:
        st.metric(
            label="Analyses Completed",
            value=f"{total_activities}",
            delta="+18% this month"
        )
    with kpi3:
        st.metric(
            label="AutoML Models",
            value="Ready",
            delta="XGBoost & LightGBM"
        )
    with kpi4:
        st.metric(
            label="System Health",
            value="99.98%",
            delta="Optimal Latency"
        )
        
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Main Content Area
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.markdown("### ⚡ Quick Navigation")
        
        q1, q2 = st.columns(2)
        with q1:
            st.markdown("""
            <div class='omni-card' style='margin-bottom: 0.75rem;'>
                <div style='font-size: 1.6rem; margin-bottom: 6px;'>📁</div>
                <div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc;'>Data Workspace</div>
                <p style='color: #c7c4d7; font-size: 0.88rem; margin: 4px 0 14px 0;'>Upload, inspect, clean, and manage your CSV, Excel, and JSON datasets.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="primary-link">', unsafe_allow_html=True)
            st.page_link("pages/02_Dataset_Manager.py", label="Open Data Workspace →", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown("""
            <div class='omni-card' style='margin-top: 1.25rem; margin-bottom: 0.75rem;'>
                <div style='font-size: 1.6rem; margin-bottom: 6px;'>🧹</div>
                <div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc;'>Smart Data Cleaning</div>
                <p style='color: #c7c4d7; font-size: 0.88rem; margin: 4px 0 14px 0;'>Handle missing values, detect anomalies, encode variables, and train/test split.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/03_Data_Cleaning.py", label="Clean Data →", use_container_width=True)

        with q2:
            st.markdown("""
            <div class='omni-card' style='margin-bottom: 0.75rem;'>
                <div style='font-size: 1.6rem; margin-bottom: 6px;'>📊</div>
                <div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc;'>Exploratory Data Analysis</div>
                <p style='color: #c7c4d7; font-size: 0.88rem; margin: 4px 0 14px 0;'>Interactive Plotly visualizers and comprehensive profiling reports.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/04_Exploratory_Data_Analysis.py", label="Launch EDA Studio →", use_container_width=True)
                
            st.markdown("""
            <div class='omni-card' style='margin-top: 1.25rem; margin-bottom: 0.75rem;'>
                <div style='font-size: 1.6rem; margin-bottom: 6px;'>🤖</div>
                <div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc;'>AutoML Studio</div>
                <p style='color: #c7c4d7; font-size: 0.88rem; margin: 4px 0 14px 0;'>Train Classification & Regression models in parallel with leaderboard ranking.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/06_Machine_Learning.py", label="Launch AutoML →", use_container_width=True)

    with col_side:
        st.markdown("### 🕒 Recent Activity Stream")
        if recent_activity:
            for log in recent_activity:
                st.markdown(f"""
                <div style="padding: 12px 14px; border-left: 3px solid #6366f1; margin-bottom: 10px; background-color: #161b2b; border-radius: 0 10px 10px 0; border: 1px solid #273449; border-left-width: 3px;">
                    <div style="font-size: 0.72rem; color: #908fa0; font-family: monospace;">{log.timestamp.strftime('%b %d, %Y • %H:%M')}</div>
                    <div style="font-weight: 600; color: #f8fafc; font-size: 0.92rem; margin-top: 3px;">{log.action}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding: 24px; text-align: center; background: #161b2b; border-radius: 12px; border: 1px dashed #273449; color: #908fa0;">
                No recent activity logged yet.<br>Upload a dataset to get started!
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
        <div class="omni-card" style="margin-top: 1.25rem; padding: 16px; background: rgba(99, 102, 241, 0.05); border-color: rgba(99, 102, 241, 0.25);">
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.85rem; color: #c0c1ff;">
                <span>💡 AI Quick Tip</span>
            </div>
            <p style="font-size: 0.8rem; color: #c7c4d7; margin: 6px 0 0 0; line-height: 1.4;">
                Head to <strong>Insights & Reports</strong> to automatically calculate your dataset health score and download executive briefings.
            </p>
        </div>
        """, unsafe_allow_html=True)

else:
    # High-Performance Stitch Landing Page for logged-out visitors
    st.markdown("""
    <div class='hero-container'>
        <div class='hero-pill'>
            <span class="pulse-dot"></span>
            <span>Introducing OmniMetrics 3.0 — Autonomous Feature Engineering & AutoML</span>
        </div>
        <h1 class='hero-title'>
            Your Data. Deeper Insights.<br>
            <span class='gradient-text'>Smarter Decisions.</span>
        </h1>
        <p class='hero-subtitle'>
            Turn raw datasets into production-grade predictive models and actionable executive intelligence in minutes. Zero boilerplate, pure precision engineering.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to Actions
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    with cta_col2:
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            st.markdown('<div class="primary-link">', unsafe_allow_html=True)
            st.page_link("pages/01_Login.py", label="🚀 Get Started Free / Log In", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_c2:
            st.page_link("pages/01_Login.py", label="📁 Explore Workspace", use_container_width=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Social Proof Bar
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2.5rem; padding-top: 1rem;">
        <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #908fa0; font-weight: 600; margin-bottom: 12px;">
            Engineered for Modern Data Teams, ML Engineers & Decision Makers
        </div>
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2rem; color: #908fa0; font-weight: 700; font-size: 1.1rem; opacity: 0.75;">
            <span>⚡ Automated EDA</span>
            <span>•</span>
            <span>🎯 Parallel AutoML</span>
            <span>•</span>
            <span>🔍 Health Auditing</span>
            <span>•</span>
            <span>📈 Interactive Plotly</span>
            <span>•</span>
            <span>🛡️ Enterprise Security</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 6 Feature Grid Cards (Stitch Design)
    st.markdown("### 🚀 Enterprise Capabilities")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        st.markdown("""
        <div class='feature-box'>
            <div>
                <span class='feature-icon'>📁</span>
                <div class='feature-title'>Data Workspace</div>
                <div class='feature-desc'>Drag-and-drop CSV, Excel, and JSON datasets with automatic schema detection, null audits, and storage quotas.</div>
            </div>
            <div style="margin-top: 16px;">
                <span class="badge badge-purple">Multi-Format</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='feature-box'>
            <div>
                <span class='feature-icon'>📊</span>
                <div class='feature-title'>Auto EDA & Profiling</div>
                <div class='feature-desc'>Generate interactive Plotly histograms, scatter plots, correlation heatmaps, and deep HTML profiling reports.</div>
            </div>
            <div style="margin-top: 16px;">
                <span class="badge badge-info">Interactive 3D</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with f_col2:
        st.markdown("""
        <div class='feature-box'>
            <div>
                <span class='feature-icon'>🧹</span>
                <div class='feature-title'>Smart Data Cleaning</div>
                <div class='feature-desc'>Impute missing values, drop duplicates, encode categorical attributes, and isolate statistical outliers with step-by-step undo.</div>
            </div>
            <div style="margin-top: 16px;">
                <span class="badge badge-live">Zero Data Loss</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='feature-box'>
            <div>
                <span class='feature-icon'>🤖</span>
                <div class='feature-title'>AutoML Studio</div>
                <div class='feature-desc'>Train Random Forest, XGBoost, LightGBM, and Gradient Boosting models simultaneously with automatic metric leaderboards.</div>
            </div>
            <div style="margin-top: 16px;">
                <span class="badge badge-purple">Multi-Engine</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with f_col3:
        st.markdown("""
        <div class='feature-box'>
            <div>
                <span class='feature-icon'>📈</span>
                <div class='feature-title'>Model Evaluation</div>
                <div class='feature-desc'>Deep diagnostic analysis including confusion matrices, ROC curves, feature attribution importances, and model artifact exports.</div>
            </div>
            <div style="margin-top: 16px;">
                <span class="badge badge-info">Explainable AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='feature-box'>
            <div>
                <span class='feature-icon'>🧠</span>
                <div class='feature-title'>AI Insights Engine</div>
                <div class='feature-desc'>Automated data hygiene scoring, heuristic anomaly discovery, and exportable executive briefing reports in Markdown format.</div>
            </div>
            <div style="margin-top: 16px;">
                <span class="badge badge-live">Executive Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; padding: 20px 0; border-top: 1px solid #1e293b; color: #908fa0; font-size: 0.85rem;'>
        OmniMetrics Enterprise AI Analytics Platform • Built with Python & Streamlit
    </div>
    """, unsafe_allow_html=True)
