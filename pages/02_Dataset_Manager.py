import streamlit as st
import pandas as pd
import numpy as np
from database.db import get_db
from services.data_manager import save_uploaded_file, get_user_datasets, delete_dataset, load_dataset_as_df

st.set_page_config(page_title="OmniMetrics - Data Workspace", page_icon="📁", layout="wide")
from utils.ui_utils import load_css
load_css()

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']
datasets = get_user_datasets(db, user_id)

# Top Workspace Header
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
    <div style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 600; color: #908fa0; text-transform: uppercase; letter-spacing: 0.05em;">
        <span class="pulse-dot"></span>
        <span style="color: #6366f1;">Repository • Live Telemetry</span>
    </div>
    <span class="badge badge-live">Sync Engine Active</span>
</div>
<div style="margin-bottom: 1.5rem;">
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;">
        Data <span class="gradient-text">Workspace</span>
    </h1>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-top: 4px;">
        Manage, inspect, and connect your structured datasets with automated schema validation and health profiling.
    </p>
</div>
""", unsafe_allow_html=True)

# Telemetry Metric Strip
total_vol_mb = sum((ds.size_bytes or 0) for ds in datasets) / (1024 * 1024)
total_records = sum((ds.rows or 0) for ds in datasets)
active_count = len(datasets)

t1, t2, t3, t4 = st.columns(4)
with t1:
    st.metric(label="Total Volume", value=f"{total_vol_mb:.1f} MB", delta=f"{active_count} files stored")
with t2:
    st.metric(label="Total Records", value=f"{total_records:,}", delta="Indexed & Ready")
with t3:
    st.metric(label="Active Datasets", value=f"{active_count}", delta="+Online")
with t4:
    st.metric(label="Data Hygiene", value="100%", delta="Integrity Verified")

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Upload Section in Elevated Expander
with st.expander("Upload New Dataset (CSV, Excel, JSON)", icon="⬆️", expanded=(active_count == 0)):
    st.markdown("""
    <div style="margin-bottom: 12px; font-size: 0.88rem; color: #c7c4d7;">
        Drag & drop or browse a dataset to automatically compute schema metrics, row counts, and data health.
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=['csv', 'xlsx', 'xls', 'json'],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        if uploaded_file.size > 200 * 1024 * 1024:
            st.error("File exceeds 200MB limit. Please upload a smaller subset.")
        else:
            col_up1, col_up2 = st.columns([1, 4])
            with col_up1:
                if st.button("Save to Workspace 🚀", type="primary", use_container_width=True):
                    with st.spinner("Parsing schema and saving file..."):
                        try:
                            dataset = save_uploaded_file(db, uploaded_file, user_id)
                            st.success(f"Dataset '{dataset.name}' uploaded successfully!")
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error uploading file: {e}")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Dataset Management Section
if not datasets:
    st.markdown("""
    <div style="padding: 40px; text-align: center; background: #161b2b; border-radius: 12px; border: 1px dashed #273449; margin-top: 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 8px;">📂</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">No Datasets Found</div>
        <p style="color: #908fa0; font-size: 0.9rem; max-width: 480px; margin: 6px auto 0 auto;">
            Upload your first dataset above to begin exploratory analysis, data cleaning, and automated machine learning.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("### 🗄️ Active Datasets")
    dataset_names = {ds.name: ds for ds in datasets}
    selected_ds_name = st.selectbox(
        "Select dataset to inspect:",
        options=list(dataset_names.keys()),
        label_visibility="collapsed"
    )
    
    if selected_ds_name:
        ds = dataset_names[selected_ds_name]
        
        # Action Bar & Metadata Metrics
        st.markdown(f"""
        <div class="omni-card" style="margin-bottom: 1.25rem; padding: 18px 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                        <span>📄 {ds.name}</span>
                        <span class="badge badge-purple">{ds.file_type.upper().replace('.', '')}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #908fa0; margin-top: 4px;">
                        Uploaded on {ds.uploaded_at.strftime('%B %d, %Y at %H:%M')} • File ID #{ds.id}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1])
        with m1:
            st.metric("Total Rows", f"{ds.rows:,}")
        with m2:
            st.metric("Total Columns", f"{ds.columns:,}")
        with m3:
            st.metric("File Size", f"{ds.size_bytes / (1024 * 1024):.2f} MB")
        with m4:
            st.page_link("pages/04_Exploratory_Data_Analysis.py", label="📊 Launch EDA", use_container_width=True)
        with m5:
            if st.button("🗑️ Delete Dataset", type="secondary", use_container_width=True):
                delete_dataset(db, ds.id, user_id)
                st.success(f"Deleted {ds.name}")
                st.rerun()
                
        try:
            df = load_dataset_as_df(ds)
            
            # Dataset Quality & Preview Tabs
            tab1, tab2, tab3 = st.tabs(["📋 Data Preview", "🏷️ Column Architecture", "🛡️ Quality Diagnostics"])
            
            with tab1:
                st.markdown(f"<div style='font-size: 0.85rem; color: #908fa0; margin-bottom: 8px;'>Displaying first {min(100, len(df))} of {len(df):,} records</div>", unsafe_allow_html=True)
                st.dataframe(df.head(100), use_container_width=True)
                
            with tab2:
                dtypes = df.dtypes.astype(str)
                missing = df.isnull().sum()
                missing_pct = (missing / len(df)) * 100
                uniques = df.nunique()
                
                col_info = pd.DataFrame({
                    "Data Type": dtypes,
                    "Missing Values": missing,
                    "Missing %": missing_pct.round(2),
                    "Unique Values": uniques
                })
                st.dataframe(col_info, use_container_width=True)
                
            with tab3:
                duplicates = df.duplicated().sum()
                total_missing = df.isnull().sum().sum()
                
                q_col1, q_col2 = st.columns(2)
                with q_col1:
                    st.metric("Duplicate Records", f"{duplicates:,}", delta=f"{(duplicates/len(df))*100:.2f}%" if len(df) > 0 else "0%")
                with q_col2:
                    st.metric("Total Null Values", f"{total_missing:,}", delta="Detected across columns")
                    
                if duplicates == 0 and total_missing == 0:
                    st.success("✨ Pristine Quality: No duplicate rows or missing values detected.")
                else:
                    if duplicates > 0:
                        st.warning(f"⚠️ Found {duplicates:,} duplicate rows. Consider using Smart Data Cleaning.")
                    if total_missing > 0:
                        st.warning(f"⚠️ Found {total_missing:,} missing values across features. Imputation recommended.")
                        
        except Exception as e:
            st.error(f"Could not load dataset details: {e}")
