import streamlit as st
from database.db import get_db
from database.models import ActivityLog
from config.settings import DATA_DIR
import os

st.set_page_config(page_title="Settings & Logs", page_icon="⚙️", layout="wide")

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("⚙️ Settings & Activity Logs")

tab1, tab2 = st.tabs(["Activity Logs", "Database & Settings"])

with tab1:
    st.subheader("Your Recent Activity")
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    if not logs:
        st.info("No activity logs found.")
    else:
        log_data = [{"Timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "Action": log.action} for log in logs]
        st.dataframe(log_data, use_container_width=True)

with tab2:
    st.subheader("System Settings")
    st.write("Theme and UI settings are managed natively by Streamlit in the top right menu (⚙️ -> Settings -> Theme).")
    
    st.subheader("Database Backup")
    st.write("Download a full backup of the SQLite database containing all metadata, logs, and users.")
    
    db_path = DATA_DIR / "datainsight.db"
    if os.path.exists(db_path):
        with open(db_path, "rb") as f:
            st.download_button(
                label="Download Database Backup (.db)",
                data=f,
                file_name="datainsight_backup.db",
                mime="application/octet-stream"
            )
    else:
        st.warning("Database file not found.")
