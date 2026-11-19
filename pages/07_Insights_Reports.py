import streamlit as st
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from services.ai_insights import generate_insights, generate_report_markdown
from utils.ui_utils import load_css, brand, page_header, require_login

st.set_page_config(page_title="AI Insights & Reports | OmniMetrics", page_icon="✨", layout="wide")
load_css(); brand(); require_login()
page_header("AI insights & reports", "Translate dataset signals into quality indicators, anomalies and recommended actions.", "INTELLIGENCE ENGINE")
db=next(get_db()); datasets=get_user_datasets(db,st.session_state["user_id"])
if not datasets: st.info("Upload a dataset to generate insights."); st.stop()
lookup={ds.name:ds for ds in datasets}; selected=st.selectbox("Analysis dataset",list(lookup))
try: df=load_dataset_as_df(lookup[selected])
except Exception as exc: st.error(f"Could not load dataset: {exc}"); st.stop()
a,b,c=st.columns(3); a.metric("Records",f"{len(df):,}"); b.metric("Features",len(df.columns)); c.metric("Missing cells",f"{int(df.isna().sum().sum()):,}")
st.markdown("### Insight generation")
if st.button("Generate AI insights",type="primary"):
    with st.spinner("Analyzing quality, patterns and anomalies..."):
        try: st.session_state["current_insights"]=generate_insights(df); st.session_state["insights_dataset"]=selected
        except Exception as exc: st.error(f"Insight generation failed: {exc}")
if st.session_state.get("current_insights") and st.session_state.get("insights_dataset")==selected:
    insights=st.session_state["current_insights"]
    score_col, summary_col=st.columns([1,2])
    with score_col:
        st.metric("Dataset health score",f"{insights['dataset_health']}/100")
        st.progress(max(0,min(100,int(insights["dataset_health"])))/100)
    with summary_col:
        st.markdown("### Executive summary"); st.write(insights["summary"])
    st.divider()
    anomalies,recommendations=st.columns(2)
    with anomalies:
        st.markdown("### Detected anomalies")
        if insights["anomalies"]:
            for item in insights["anomalies"]: st.warning(item)
        else: st.success("No significant anomalies detected.")
    with recommendations:
        st.markdown("### Recommended actions")
        if insights["recommendations"]:
            for item in insights["recommendations"]: st.info(item)
        else: st.success("No additional recommendations.")
    st.markdown("### Export report")
    report=generate_report_markdown(selected,insights)
    st.download_button("Download Markdown report",report,file_name=f"report_{selected.rsplit('.csv',1)[0]}.md",mime="text/markdown",type="primary")
