import streamlit as st
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from services.ai_insights import generate_insights, generate_report_markdown

st.set_page_config(page_title="AI Insights & Reports", page_icon="🧠", layout="wide")

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("🧠 AI Insights & Reports")
st.write("Generate automated business insights, detect anomalies, and download comprehensive reports.")

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload one in the Dataset Manager.")
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
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Data Quality Score", f"{insights['dataset_health']}/100")
        
    with col2:
        st.subheader("Executive Summary")
        st.write(insights['summary'])
        
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("⚠️ Detected Anomalies")
        if insights['anomalies']:
            for a in insights['anomalies']:
                st.warning(a)
        else:
            st.success("No significant anomalies detected.")
            
    with col4:
        st.subheader("💡 Recommendations")
        if insights['recommendations']:
            for r in insights['recommendations']:
                st.info(r)
        else:
            st.success("Dataset is fully optimized.")
            
    st.markdown("---")
    st.subheader("📄 Export Report")
    
    report_md = generate_report_markdown(selected_ds_name, insights)
    
    st.download_button(
        label="Download Markdown Report",
        data=report_md,
        file_name=f"report_{selected_ds_name.replace('.csv','')}.md",
        mime="text/markdown"
    )
