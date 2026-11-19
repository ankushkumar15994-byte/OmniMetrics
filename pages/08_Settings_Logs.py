import streamlit as st
import os
from database.db import get_db
from database.models import ActivityLog
from config.settings import DATA_DIR
from utils.ui_utils import load_css, brand, page_header, require_login

st.set_page_config(page_title="Settings & Activity | OmniMetrics", page_icon="⚙️", layout="wide")
load_css(); brand(); require_login()
page_header("Settings & activity", "Review workspace activity and manage local database backup.", "WORKSPACE ADMINISTRATION")
db=next(get_db()); user_id=st.session_state["user_id"]
profile,access=st.columns([1,1])
with profile:
    with st.container(border=True):
        st.markdown("### Account")
        st.markdown(f"**Username**  \n{st.session_state.get('username','User')}")
        st.markdown(f"**Role**  \n{str(st.session_state.get('role','user')).title()}")
with access:
    with st.container(border=True):
        st.markdown("### Workspace appearance")
        st.write("OmniMetrics currently uses the Midnight Pro theme configured for this application.")
        st.caption("The visual theme does not change stored data or account settings.")
logs=db.query(ActivityLog).filter(ActivityLog.user_id==user_id).order_by(ActivityLog.timestamp.desc()).limit(50).all()
st.markdown("### Recent activity")
if logs:
    data=[{"Timestamp":log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),"Action":log.action} for log in logs]
    st.dataframe(data,use_container_width=True,hide_index=True)
else: st.info("No activity has been recorded yet.")
st.markdown("### Database backup")
st.caption("Download a copy of your local SQLite database, including user, dataset metadata and activity records.")
db_path=DATA_DIR/"datainsight.db"
if os.path.exists(db_path):
    with open(db_path,"rb") as file:
        st.download_button("Download database backup",file,file_name="omnimetrics_backup.db",mime="application/octet-stream")
else: st.warning("SQLite database file not found. If you use a remote database, local backup is not available here.")
