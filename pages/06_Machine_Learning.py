import streamlit as st
import pandas as pd
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from machine_learning.models import train_classification, train_regression, train_clustering, save_model

st.set_page_config(page_title="Machine Learning Studio", page_icon="🤖", layout="wide")
from utils.ui_utils import load_css
load_css()

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("🤖 Machine Learning Studio")
st.write("Train and compare multiple algorithms instantly. (Data will be automatically subset to numerical columns. Please encode categories using the Data Cleaning tab if needed).")

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload one in the Dataset Manager.")
    st.stop()

dataset_names = {ds.name: ds for ds in datasets}
selected_ds_name = st.selectbox("Select a dataset for ML", list(dataset_names.keys()))
dataset_obj = dataset_names[selected_ds_name]

try:
    df = load_dataset_as_df(dataset_obj)
    # Ensure dataframe is numeric for ML
    num_df = df.select_dtypes(include=['number'])
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

if num_df.empty:
    st.error("Dataset must contain numerical columns for Machine Learning. Please clean/encode it first.")
    st.stop()

if len(num_df.columns) < len(df.columns):
    st.info("Note: Non-numerical columns have been automatically excluded for Machine Learning.")

problem_type = st.radio("Select Problem Type", ["Classification", "Regression", "Clustering"], horizontal=True)

target_col = None
if problem_type in ["Classification", "Regression"]:
    target_col = st.selectbox("Select Target Column (y)", num_df.columns)

if st.button("🚀 Train Models", type="primary"):
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
    st.subheader("Leaderboard")
    st.dataframe(st.session_state['ml_results'], use_container_width=True)
    
    st.markdown("---")
    st.subheader("💾 Save Winning Model")
    models = st.session_state['trained_models']
    selected_model_name = st.selectbox("Select a model to save", list(models.keys()))
    
    if st.button("Save Selected Model"):
        model_to_save = models[selected_model_name]
        filename = f"{selected_model_name.replace(' ', '_').lower()}_{selected_ds_name.replace('.csv', '')}.joblib"
        path = save_model(model_to_save, filename)
        st.success(f"Model saved locally at: `{path}`")
        
        with open(path, "rb") as f:
            st.download_button("Download Model File (.joblib)", f, file_name=filename)
