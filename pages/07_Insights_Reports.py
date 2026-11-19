import streamlit as st
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from services.ai_insights import generate_insights, generate_report_markdown

st.set_page_config(page_title="AI Insights & Reports", page_icon="🧠", layout="wide")
from utils.ui_utils import load_css
load_css()

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 600; color: #908fa0; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
        <span class="pulse-dot"></span>
        <span style="color: #6366f1;">Cognitive Telemetry</span>
    </div>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;">
        AI Insights & <span class="gradient-text">Reports</span>
    </h1>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-top: 4px;">
        Automated dataset hygiene scores, heuristic anomaly detection, and exportable executive briefing reports.
    </p>
</div>
""", unsafe_allow_html=True)

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload one in the Data Workspace.")
    st.stop()

dataset_names = {ds.name: ds for ds in datasets}
selected_ds_name = st.selectbox("Select a dataset for Analysis", list(dataset_names.keys()))
dataset_obj = dataset_names[selected_ds_name]

try:
    df = load_dataset_as_df(dataset_obj)
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

if st.button("Generate AI Insights", type="primary"):
    with st.spinner("Analyzing data patterns..."):
        insights = generate_insights(df)
        st.session_state['current_insights'] = insights

if 'current_insights' in st.session_state:
    insights = st.session_state['current_insights']
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div class='card' style='text-align: center; padding: 40px;'>", unsafe_allow_html=True)
        st.metric("Data Quality Score", f"{insights['dataset_health']}/100")
        if insights['dataset_health'] >= 90:
            st.success("Excellent Quality")
        elif insights['dataset_health'] >= 70:
            st.info("Good Quality")
        else:
            st.error("Needs Cleaning")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Executive Summary")
        st.write(insights['summary'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ⚠️ Detected Anomalies")
        if insights['anomalies']:
            for a in insights['anomalies']:
                st.warning(a)
        else:
            st.success("No significant anomalies detected.")
        st.markdown("</div>", unsafe_allow_html=True)
            
    with col4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 💡 Recommendations")
        if insights['recommendations']:
            for r in insights['recommendations']:
                st.info(r)
        else:
            st.success("Dataset is fully optimized.")
        st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("### 📄 Export Report")
    
    report_md = generate_report_markdown(selected_ds_name, insights)
    
    st.download_button(
        label="Download Markdown Report",
        data=report_md,
        file_name=f"report_{selected_ds_name.replace('.csv','')}.md",
        mime="text/markdown",
        type="primary"
    )
