import streamlit as st
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from machine_learning.models import train_classification, train_regression, train_clustering, save_model
from utils.ui_utils import load_css, brand, page_header, require_login

st.set_page_config(page_title="Machine Learning Studio | OmniMetrics", page_icon="🤖", layout="wide")
load_css(); brand(); require_login()
page_header("Machine learning studio", "Train, compare and export models using your prepared datasets.", "MODEL DEVELOPMENT")
db = next(get_db()); datasets = get_user_datasets(db, st.session_state["user_id"])
if not datasets: st.info("Upload a dataset to begin model training."); st.stop()
mapping = {ds.name:ds for ds in datasets}
selected = st.selectbox("Training dataset",list(mapping)); ds = mapping[selected]
try:
    df = load_dataset_as_df(ds); numeric_df = df.select_dtypes(include=["number"])
except Exception as exc: st.error(f"Could not load dataset: {exc}"); st.stop()
a,b,c = st.columns(3); a.metric("Source rows",f"{len(df):,}"); b.metric("Numeric features",len(numeric_df.columns)); c.metric("Excluded categorical",len(df.columns)-len(numeric_df.columns))
if numeric_df.empty: st.error("The dataset needs numerical features. Encode categorical columns in Data Cleaning first."); st.stop()
if len(numeric_df.columns)<len(df.columns): st.info("Categorical columns are excluded automatically. Encode them first if they should be included.")
st.markdown("### Configure training")
problem = st.radio("Problem type",["Classification","Regression","Clustering"],horizontal=True)
target = st.selectbox("Target variable",numeric_df.columns) if problem in ["Classification","Regression"] else None
if st.button("Train and compare models",type="primary"):
    with st.spinner("Training candidate models..."):
        try:
            if problem=="Classification": results,models=train_classification(numeric_df,target)
            elif problem=="Regression": results,models=train_regression(numeric_df,target)
            else: results,models=train_clustering(numeric_df)
            st.session_state["ml_results"]=results; st.session_state["trained_models"]=models; st.session_state["ml_dataset"]=selected
            st.success("Training completed.")
        except Exception as exc: st.error(f"Training failed: {exc}")
if st.session_state.get("ml_dataset") == selected and "ml_results" in st.session_state:
    st.markdown("### Model leaderboard")
    st.dataframe(st.session_state["ml_results"],use_container_width=True)
    models=st.session_state["trained_models"]
    if models:
        st.markdown("### Export a trained model")
        chosen=st.selectbox("Model to save",list(models.keys()))
        if st.button("Save selected model"):
            try:
                filename=f"{chosen.replace(' ','_').lower()}_{selected.rsplit('.csv',1)[0]}.joblib"
                path=save_model(models[chosen],filename)
                with open(path,"rb") as model_file:
                    st.download_button("Download model (.joblib)",model_file,file_name=filename)
                st.success(f"Model saved locally at {path}")
            except Exception as exc: st.error(f"Could not save model: {exc}")
