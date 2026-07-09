import streamlit as st
import pandas as pd
from database.db import get_db
from services.data_manager import save_uploaded_file, get_user_datasets, delete_dataset, load_dataset_as_df

st.set_page_config(page_title="Dataset Manager", page_icon="📁", layout="wide")

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("📁 Dataset Manager")
st.write("Upload, preview, and manage your datasets (CSV, Excel, JSON).")

# Upload Section
with st.expander("⬆️ Upload New Dataset", expanded=True):
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls', 'json'])
    if uploaded_file is not None:
        if st.button("Upload & Save"):
            with st.spinner("Processing file..."):
                try:
                    dataset = save_uploaded_file(db, uploaded_file, user_id)
                    st.success(f"Dataset '{dataset.name}' uploaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error uploading file: {e}")

# Datasets List Section
st.subheader("Your Datasets")
datasets = get_user_datasets(db, user_id)

if not datasets:
    st.info("No datasets found. Please upload one above.")
else:
    for ds in datasets:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])
            col1.write(f"**{ds.name}**")
            col2.write(f"Rows: {ds.rows}")
            col3.write(f"Cols: {ds.columns}")
            size_mb = ds.size_bytes / (1024 * 1024)
            col4.write(f"{size_mb:.2f} MB")
            
            with col5:
                btn_col1, btn_col2 = st.columns(2)
                if btn_col1.button("Preview", key=f"prev_{ds.id}"):
                    st.session_state[f'preview_{ds.id}'] = not st.session_state.get(f'preview_{ds.id}', False)
                if btn_col2.button("Delete", key=f"del_{ds.id}"):
                    delete_dataset(db, ds.id, user_id)
                    st.rerun()
                    
            if st.session_state.get(f'preview_{ds.id}', False):
                try:
                    df = load_dataset_as_df(ds)
                    st.dataframe(df.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"Could not load preview: {e}")
            st.markdown("---")
