import streamlit as st
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from visualizations.charts import plot_histogram, plot_scatter, plot_bar, plot_pie, plot_line
from utils.ui_utils import load_css, brand, page_header, require_login

st.set_page_config(page_title="Dashboard Builder | OmniMetrics", page_icon="📈", layout="wide")
load_css(); brand(); require_login()
page_header("Dashboard builder", "Compose an interactive view from KPI metrics and charts.", "REPORTING WORKSPACE")
db = next(get_db()); datasets = get_user_datasets(db, st.session_state["user_id"])
if not datasets: st.info("Upload a dataset before creating a dashboard."); st.stop()
mapping = {ds.name: ds for ds in datasets}
selected = st.selectbox("Source dataset", list(mapping)); ds = mapping[selected]
try: df = load_dataset_as_df(ds)
except Exception as exc: st.error(f"Could not load dataset: {exc}"); st.stop()
state_key = f"dash_elements_{selected}"
if state_key not in st.session_state: st.session_state[state_key] = []
elements = st.session_state[state_key]
with st.expander("＋ Add dashboard element", expanded=not bool(elements)):
    kind = st.radio("Element type", ["KPI Metric","Chart"], horizontal=True)
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    if kind == "KPI Metric":
        name = st.text_input("Metric label", "Total value")
        if numeric:
            col = st.selectbox("Numerical column", numeric); agg = st.selectbox("Aggregation", ["Sum","Average","Count","Max","Min"])
            if st.button("Add KPI", type="primary"):
                elements.append({"type":"kpi","name":name,"col":col,"agg":agg}); st.rerun()
        else: st.warning("No numerical columns are available for KPI metrics.")
    else:
        chart = st.selectbox("Chart type", ["Bar Chart","Line Chart","Scatter Plot","Pie Chart","Histogram"])
        x = st.selectbox("X axis / labels", df.columns.tolist()); y = st.selectbox("Y axis / values", ["None"]+numeric)
        if st.button("Add chart", type="primary"):
            elements.append({"type":"chart","chart_type":chart,"x":x,"y":None if y=="None" else y}); st.rerun()
if not elements:
    st.info("Your canvas is empty. Add a KPI or chart to start building your dashboard.")
else:
    kpis = [e for e in elements if e["type"]=="kpi"]; charts = [e for e in elements if e["type"]=="chart"]
    if kpis:
        st.markdown("### Key performance indicators")
        cols = st.columns(min(len(kpis),4))
        for i,item in enumerate(kpis):
            series = df[item["col"]]
            value = {"Sum":series.sum(),"Average":series.mean(),"Count":series.count(),"Max":series.max(),"Min":series.min()}[item["agg"]]
            cols[i%len(cols)].metric(item["name"], f"{value:,.2f}" if isinstance(value,(float,int)) else str(value))
    if charts:
        st.markdown("### Visualizations")
        for index in range(0,len(charts),2):
            cols = st.columns(2)
            for j,item in enumerate(charts[index:index+2]):
                with cols[j]:
                    st.markdown(f"**{item['chart_type']}**")
                    try:
                        y = item["y"]
                        fig = {"Bar Chart":lambda:plot_bar(df,item["x"],y),"Line Chart":lambda:plot_line(df,item["x"],y),"Scatter Plot":lambda:plot_scatter(df,item["x"],y),"Pie Chart":lambda:plot_pie(df,item["x"],y),"Histogram":lambda:plot_histogram(df,item["x"])}[item["chart_type"]]()
                        try: fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
                        except Exception: pass
                        st.plotly_chart(fig,use_container_width=True)
                    except Exception as exc: st.error(f"Chart could not be displayed: {exc}")
    if st.button("Clear dashboard", type="secondary"):
        st.session_state[state_key] = []; st.rerun()
