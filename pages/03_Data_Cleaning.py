import streamlit as st
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from preprocessing.cleaner import handle_missing_values, remove_duplicates, encode_categorical, scale_features, handle_outliers
from utils.ui_utils import load_css, brand, page_header, require_login

st.set_page_config(page_title="Data Cleaning | OmniMetrics", page_icon="🧹", layout="wide")
load_css(); brand(); require_login()
page_header("Data preparation", "Improve data quality with guided transformations and reversible operations.", "DATA WORKSPACE")
db = next(get_db()); user_id = st.session_state["user_id"]
datasets = get_user_datasets(db, user_id)
if not datasets:
    st.info("Upload a dataset in Dataset Manager before cleaning."); st.stop()
dataset_map = {ds.name: ds for ds in datasets}
selected = st.selectbox("Working dataset", list(dataset_map))
ds = dataset_map[selected]
if "current_df" not in st.session_state or st.session_state.get("current_ds_name") != selected:
    try:
        st.session_state["current_df"] = load_dataset_as_df(ds)
        st.session_state["current_ds_name"] = selected
        st.session_state["history"] = []
    except Exception as exc:
        st.error(f"Could not load dataset: {exc}"); st.stop()
df = st.session_state["current_df"]
def apply_change(new_df, label):
    st.session_state["history"].append((df.copy(), label))
    st.session_state["current_df"] = new_df
    st.rerun()
missing_count = int(df.isna().sum().sum()); duplicates = int(df.duplicated().sum())
a,b,c,d = st.columns(4)
a.metric("Rows", f"{len(df):,}"); b.metric("Columns", len(df.columns)); c.metric("Missing cells", f"{missing_count:,}"); d.metric("Duplicate rows", f"{duplicates:,}")
preview, operations = st.columns([1.55, 1])
with preview:
    st.markdown("### Data preview")
    st.dataframe(df.head(50), use_container_width=True)
    st.markdown("### Missing-value overview")
    missing = df.isna().sum().loc[lambda x: x > 0]
    if len(missing):
        st.dataframe(missing.rename("Missing values").to_frame(), use_container_width=True)
    else:
        st.success("No missing values detected.")
with operations:
    st.markdown("### Cleaning toolkit")
    with st.expander("Fill or remove missing values", expanded=True):
        cols = st.multiselect("Columns", df.columns.tolist(), key="miss_cols")
        strategy = st.selectbox("Strategy", ["Drop Rows", "Drop Columns", "Mean", "Median", "Mode", "Forward Fill", "Backward Fill", "KNN Imputer"])
        if st.button("Apply missing-value strategy", key="impute", type="primary"):
            try: apply_change(handle_missing_values(df, strategy, cols), f"Missing values: {strategy}")
            except Exception as exc: st.error(str(exc))
    with st.expander("Remove duplicate records"):
        st.caption(f"{duplicates:,} duplicate rows detected.")
        if st.button("Remove duplicates"):
            apply_change(remove_duplicates(df), "Removed duplicate rows")
    with st.expander("Encode categorical features"):
        cat = df.select_dtypes(include=["object", "category"]).columns.tolist()
        enc = st.multiselect("Categorical columns", cat, key="enc_cols")
        method = st.selectbox("Encoding method", ["Label Encoding", "One Hot Encoding"])
        if st.button("Apply encoding"):
            if not enc: st.error("Select at least one categorical column.")
            else:
                try: apply_change(encode_categorical(df, method, enc), f"Encoding: {method}")
                except Exception as exc: st.error(str(exc))
    with st.expander("Scale numerical features"):
        numeric = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        scale_cols = st.multiselect("Numerical columns", numeric, key="scale_cols")
        scaler = st.selectbox("Scaler", ["StandardScaler", "MinMaxScaler", "RobustScaler"])
        if st.button("Apply scaling"):
            if not scale_cols: st.error("Select at least one numerical column.")
            else:
                try: apply_change(scale_features(df, scaler, scale_cols), f"Scaling: {scaler}")
                except Exception as exc: st.error(str(exc))
    with st.expander("Handle outliers"):
        out_cols = st.multiselect("Numerical columns", numeric, key="out_cols")
        if st.button("Clip outliers using IQR"):
            if not out_cols: st.error("Select at least one numerical column.")
            else:
                try: apply_change(handle_outliers(df, "IQR (Clip)", out_cols), "Outliers clipped (IQR)")
                except Exception as exc: st.error(str(exc))
st.divider()
x,y,z = st.columns([1,1,3])
with x:
    if st.button("Undo last operation", disabled=not st.session_state["history"]):
        previous, action = st.session_state["history"].pop()
        st.session_state["current_df"] = previous; st.rerun()
with y:
    st.download_button("Download cleaned CSV", data=df.to_csv(index=False), file_name=f"cleaned_{selected.rsplit('.',1)[0]}.csv", mime="text/csv", use_container_width=True)
with z:
    st.caption(f"Transformation history: {len(st.session_state['history'])} reversible operation(s). Changes are held in this session until downloaded.")
