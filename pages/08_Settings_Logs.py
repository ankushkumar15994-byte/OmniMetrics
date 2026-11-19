import streamlit as st
from database.db import get_db
from database.models import ActivityLog
from config.settings import DATA_DIR, BASE_DIR
import os

st.set_page_config(page_title="Settings & Logs", page_icon="⚙️", layout="wide")
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
        <span style="color: #6366f1;">Governance & Auditing</span>
    </div>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;">
        Settings & <span class="gradient-text">Activity Logs</span>
    </h1>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-top: 4px;">
        Audit trail telemetry, database management, and platform configuration.
    </p>
</div>
""", unsafe_allow_html=True)

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
    st.subheader("🎨 Platform Theme & Appearance")
    st.markdown("""
    <div style="font-size: 0.9rem; color: #908fa0; margin-bottom: 1rem;">
        In Streamlit v1.67+, theme settings are configured directly via project configuration. 
        Select a theme preset or fine-tune custom colors below, then click <strong>Save & Apply</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    theme_presets = {
        "Stitch Deep Slate (Active)": {
            "primary": "#6366f1",
            "bg": "#0e1323",
            "card": "#161b2b",
            "text": "#dee1f9",
        },
        "Cyberpunk Neon": {
            "primary": "#00f0ff",
            "bg": "#0a0a14",
            "card": "#14142b",
            "text": "#f0f4f8",
        },
        "Emerald Intelligence": {
            "primary": "#10b981",
            "bg": "#061a14",
            "card": "#0d2b22",
            "text": "#ecfdf5",
        },
        "Nordic Indigo": {
            "primary": "#4f46e5",
            "bg": "#0f172a",
            "card": "#1e293b",
            "text": "#f1f5f9",
        },
        "Clean Minimalist Light": {
            "primary": "#4f46e5",
            "bg": "#f8fafc",
            "card": "#ffffff",
            "text": "#0f172a",
        }
    }
    
    col_preset, col_tune = st.columns([1, 1])
    with col_preset:
        selected_preset = st.selectbox("Choose Theme Preset:", list(theme_presets.keys()))
        preset_vals = theme_presets[selected_preset]
        
    with col_tune:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        customize = st.checkbox("Custom Color Overrides")
        
    if customize:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p_val = st.color_picker("Primary Accent", value=preset_vals["primary"])
        with c2:
            bg_val = st.color_picker("Main Background", value=preset_vals["bg"])
        with c3:
            card_val = st.color_picker("Card Surface", value=preset_vals["card"])
        with c4:
            txt_val = st.color_picker("Text Color", value=preset_vals["text"])
    else:
        p_val = preset_vals["primary"]
        bg_val = preset_vals["bg"]
        card_val = preset_vals["card"]
        txt_val = preset_vals["text"]
        
    if st.button("Save & Apply Theme ✨", type="primary"):
        config_path = BASE_DIR / ".streamlit" / "config.toml"
        new_config = f"""[theme]
primaryColor = "{p_val}"
backgroundColor = "{bg_val}"
secondaryBackgroundColor = "{card_val}"
textColor = "{txt_val}"
font = "sans serif"

[client]
toolbarMode = "developer"
"""
        with open(config_path, "w") as f:
            f.write(new_config)
        st.success(f"Theme '{selected_preset}' saved to config.toml! Refresh your browser to apply.")

    st.markdown("---")
    st.subheader("💾 Database Backup & Export")
    st.write("Download a full backup of your local SQLite database containing all metadata, logs, and users.")
    
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
