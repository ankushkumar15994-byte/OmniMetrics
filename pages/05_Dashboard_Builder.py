import streamlit as st
import pandas as pd
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from visualizations.charts import plot_histogram, plot_scatter, plot_bar, plot_pie, plot_line

st.set_page_config(page_title="Dashboard Builder", page_icon="📈", layout="wide")

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("📈 Dashboard Builder")
st.write("Build a custom dashboard by adding KPI metrics and charts.")

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload one in the Dataset Manager.")
    st.stop()

dataset_names = {ds.name: ds for ds in datasets}
selected_ds_name = st.selectbox("Select a dataset to build dashboard on", list(dataset_names.keys()))
dataset_obj = dataset_names[selected_ds_name]

try:
    df = load_dataset_as_df(dataset_obj)
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# Dashboard State
if f'dash_elements_{selected_ds_name}' not in st.session_state:
    st.session_state[f'dash_elements_{selected_ds_name}'] = []

dash_elements = st.session_state[f'dash_elements_{selected_ds_name}']

# --- Sidebar: Add Elements ---
with st.sidebar:
    st.header("Add Dashboard Element")
    elem_type = st.radio("Element Type", ["KPI Metric", "Chart"])
    
    if elem_type == "KPI Metric":
        kpi_name = st.text_input("Metric Name", "Total Sales")
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not num_cols:
            st.error("No numerical columns available for KPI.")
        else:
            kpi_col = st.selectbox("Numerical Column for Metric", num_cols)
            kpi_agg = st.selectbox("Aggregation", ["Sum", "Average", "Count", "Max", "Min"])
            if st.button("Add KPI"):
                dash_elements.append({
                    "type": "kpi",
                    "name": kpi_name,
                    "col": kpi_col,
                    "agg": kpi_agg
                })
                st.rerun()
            
    elif elem_type == "Chart":
        chart_type = st.selectbox("Chart", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram"])
        all_cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        x_col = st.selectbox("X-Axis / Labels", all_cols)
        y_col = st.selectbox("Y-Axis / Values (Optional)", ["None"] + num_cols)
        
        if st.button("Add Chart"):
            dash_elements.append({
                "type": "chart",
                "chart_type": chart_type,
                "x": x_col,
                "y": None if y_col == "None" else y_col
            })
            st.rerun()
            
    st.markdown("---")
    if st.button("Clear Dashboard", type="primary"):
        st.session_state[f'dash_elements_{selected_ds_name}'] = []
        st.rerun()

# --- Main Area: Render Dashboard ---
if not dash_elements:
    st.info("Your dashboard is empty. Use the sidebar to add KPIs and Charts.")
else:
    # Separate KPIs and Charts for better layout
    kpis = [e for e in dash_elements if e['type'] == 'kpi']
    charts = [e for e in dash_elements if e['type'] == 'chart']
    
    # Render KPIs in columns (max 4 per row)
    if kpis:
        st.subheader("Key Performance Indicators")
        # Ensure we have at least 1 column and at most 4
        num_cols = min(len(kpis), 4)
        num_cols = max(num_cols, 1)
        kpi_cols = st.columns(num_cols)
        
        for i, kpi in enumerate(kpis):
            col_idx = i % 4
            val = 0
            if kpi['agg'] == 'Sum': val = df[kpi['col']].sum()
            elif kpi['agg'] == 'Average': val = df[kpi['col']].mean()
            elif kpi['agg'] == 'Count': val = df[kpi['col']].count()
            elif kpi['agg'] == 'Max': val = df[kpi['col']].max()
            elif kpi['agg'] == 'Min': val = df[kpi['col']].min()
            
            kpi_cols[col_idx].metric(label=kpi['name'], value=round(val, 2) if isinstance(val, float) else val)
            
    st.markdown("---")
    
    # Render Charts in columns (2 per row)
    if charts:
        st.subheader("Visualizations")
        for i in range(0, len(charts), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(charts):
                    chart_info = charts[i+j]
                    with cols[j]:
                        st.markdown(f"**{chart_info['chart_type']}**")
                        try:
                            if chart_info['chart_type'] == "Bar Chart":
                                st.plotly_chart(plot_bar(df, chart_info['x'], chart_info['y']), use_container_width=True)
                            elif chart_info['chart_type'] == "Line Chart":
                                st.plotly_chart(plot_line(df, chart_info['x'], chart_info['y']), use_container_width=True)
                            elif chart_info['chart_type'] == "Scatter Plot":
                                st.plotly_chart(plot_scatter(df, chart_info['x'], chart_info['y']), use_container_width=True)
                            elif chart_info['chart_type'] == "Pie Chart":
                                st.plotly_chart(plot_pie(df, chart_info['x'], chart_info['y']), use_container_width=True)
                            elif chart_info['chart_type'] == "Histogram":
                                st.plotly_chart(plot_histogram(df, chart_info['x']), use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not render chart: {e}")
