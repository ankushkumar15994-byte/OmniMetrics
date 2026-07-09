import streamlit as st
import streamlit.components.v1 as components
from ydata_profiling import ProfileReport
import pandas as pd
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from visualizations.charts import (
    plot_histogram, plot_scatter, plot_box, plot_correlation_heatmap,
    plot_bar, plot_pie, plot_line, plot_violin, plot_3d_scatter
)

st.set_page_config(page_title="Exploratory Data Analysis", page_icon="📊", layout="wide")
from utils.ui_utils import load_css
load_css()

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("📊 Exploratory Data Analysis")

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload one in the Dataset Manager.")
    st.stop()

dataset_names = {ds.name: ds for ds in datasets}
selected_ds_name = st.selectbox("Select a dataset for EDA", list(dataset_names.keys()))
dataset_obj = dataset_names[selected_ds_name]

try:
    df = load_dataset_as_df(dataset_obj)
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

tab1, tab2 = st.tabs(["Interactive Charts", "Automated Profiling Report"])

with tab1:
    st.subheader("Manual Data Exploration")
    
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        chart_type = st.selectbox("Chart Type", [
            "Histogram", "Scatter Plot", "Box Plot", "Bar Chart", 
            "Pie Chart", "Line Chart", "Violin Plot", "3D Scatter", "Correlation Heatmap"
        ])
        
        # Dynamic inputs based on chart type
        x_col = y_col = z_col = color_col = None
        
        if chart_type in ["Histogram"]:
            x_col = st.selectbox("X-axis (Feature)", all_cols)
            color_col = st.selectbox("Color By (Optional)", ["None"] + all_cols)
            
        elif chart_type in ["Pie Chart"]:
            x_col = st.selectbox("Names (Categories)", cat_cols if cat_cols else all_cols)
            y_col = st.selectbox("Values (Optional)", ["None"] + num_cols)
            
        elif chart_type in ["Scatter Plot", "Box Plot", "Bar Chart", "Line Chart", "Violin Plot"]:
            x_col = st.selectbox("X-axis", all_cols)
            y_col = st.selectbox("Y-axis", num_cols if num_cols else all_cols)
            color_col = st.selectbox("Color By (Optional)", ["None"] + all_cols)
            
        elif chart_type == "3D Scatter":
            if len(num_cols) < 3:
                st.warning("Need at least 3 numerical columns for 3D scatter.")
            else:
                x_col = st.selectbox("X-axis", num_cols, index=0)
                y_col = st.selectbox("Y-axis", num_cols, index=1)
                z_col = st.selectbox("Z-axis", num_cols, index=2)
                color_col = st.selectbox("Color By (Optional)", ["None"] + all_cols)
            
        if color_col == "None": color_col = None
        if y_col == "None": y_col = None

    with col2:
        if chart_type == "Correlation Heatmap":
            st.plotly_chart(plot_correlation_heatmap(df), use_container_width=True)
        elif chart_type == "Histogram" and x_col:
            st.plotly_chart(plot_histogram(df, x_col, color_col), use_container_width=True)
        elif chart_type == "Scatter Plot" and x_col and y_col:
            st.plotly_chart(plot_scatter(df, x_col, y_col, color_col), use_container_width=True)
        elif chart_type == "Box Plot" and x_col and y_col:
            st.plotly_chart(plot_box(df, x_col, y_col, color_col), use_container_width=True)
        elif chart_type == "Bar Chart" and x_col and y_col:
            st.plotly_chart(plot_bar(df, x_col, y_col, color_col), use_container_width=True)
        elif chart_type == "Pie Chart" and x_col:
            st.plotly_chart(plot_pie(df, x_col, y_col), use_container_width=True)
        elif chart_type == "Line Chart" and x_col and y_col:
            st.plotly_chart(plot_line(df, x_col, y_col, color_col), use_container_width=True)
        elif chart_type == "Violin Plot" and x_col and y_col:
            st.plotly_chart(plot_violin(df, x_col, y_col, color_col), use_container_width=True)
        elif chart_type == "3D Scatter" and x_col and y_col and z_col:
            st.plotly_chart(plot_3d_scatter(df, x_col, y_col, z_col, color_col), use_container_width=True)

with tab2:
    st.subheader("Automated Profiling Report")
    st.info("Generating a profile report might take a minute for large datasets. It uses `ydata-profiling` to calculate deep statistics.")
    if st.button("Generate Profile Report"):
        with st.spinner("Analyzing dataset... This may take a while."):
            try:
                # minimal=True speeds up the process significantly for web apps
                pr = ProfileReport(df, minimal=True)
                report_html = pr.to_html()
                components.html(report_html, height=1000, scrolling=True)
            except Exception as e:
                st.error(f"Failed to generate report: {e}")
