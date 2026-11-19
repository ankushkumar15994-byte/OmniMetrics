import streamlit as st
import pandas as pd
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from machine_learning.models import train_classification, train_regression, train_clustering, save_model

st.set_page_config(page_title="AutoML Studio", page_icon="🤖", layout="wide")
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
        <span style="color: #6366f1;">Autonomous Modeling Engine</span>
    </div>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;">
        AutoML <span class="gradient-text">Studio</span>
    </h1>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-top: 4px;">
        Train and evaluate Classification & Regression models in parallel with leaderboard ranking and model artifact export.
    </p>
</div>
""", unsafe_allow_html=True)

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload one in the Data Workspace.")
    st.stop()

dataset_names = {ds.name: ds for ds in datasets}
selected_ds_name = st.selectbox("Select a dataset for ML", list(dataset_names.keys()))
dataset_obj = dataset_names[selected_ds_name]

try:
    df = load_dataset_as_df(dataset_obj)
    num_df = df.select_dtypes(include=['number'])
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

if num_df.empty:
    st.error("Dataset must contain numerical columns for Machine Learning. Please clean/encode it first.")
    st.stop()

st.markdown("---")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("### 1. Configuration")
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        problem_type = st.radio("Select Problem Type", ["Classification", "Regression", "Clustering"])
        
        target_col = None
        if problem_type in ["Classification", "Regression"]:
            target_col = st.selectbox("Select Target Column (y)", num_df.columns)
            st.caption("The target column is what you want the model to predict. Ensure it is encoded numerically.")
        
        if len(num_df.columns) < len(df.columns):
            st.info("ℹ️ Non-numerical columns are excluded automatically. Use Data Cleaning to encode them if needed.")
            
        train_btn = st.button("🚀 Train Models", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 2. Leaderboard & Results")
    if train_btn:
        with st.spinner("Training models in parallel..."):
            try:
                if problem_type == "Classification":
                    results_df, trained_models = train_classification(num_df, target_col)
                    st.session_state['ml_results'] = results_df
                    st.session_state['trained_models'] = trained_models
                elif problem_type == "Regression":
                    results_df, trained_models = train_regression(num_df, target_col)
                    st.session_state['ml_results'] = results_df
                    st.session_state['trained_models'] = trained_models
                elif problem_type == "Clustering":
                    results_df, trained_models = train_clustering(num_df)
                    st.session_state['ml_results'] = results_df
                    st.session_state['trained_models'] = trained_models
                st.success("Models trained successfully!")
            except Exception as e:
                st.error(f"Error during training: {e}")
                
    if 'ml_results' in st.session_state:
        st.dataframe(st.session_state['ml_results'].style.highlight_max(axis=0, color='rgba(99, 102, 241, 0.2)'), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 💾 Save & Export")
        models = st.session_state['trained_models']
        selected_model_name = st.selectbox("Select the best model to save", list(models.keys()))
        
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            if st.button("Save Selected Model locally", use_container_width=True):
                model_to_save = models[selected_model_name]
                filename = f"{selected_model_name.replace(' ', '_').lower()}_{selected_ds_name.replace('.csv', '')}.joblib"
                path = save_model(model_to_save, filename)
                st.success(f"Saved at: `{path}`")
                
                with open(path, "rb") as f:
                    st.download_button("Download .joblib", f, file_name=filename, type="primary", use_container_width=True)
