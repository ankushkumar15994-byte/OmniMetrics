import streamlit as st
from database.db import get_db
from services.data_manager import save_uploaded_file, get_user_datasets, delete_dataset, load_dataset_as_df
from utils.ui_utils import load_css, brand, page_header, require_login

st.set_page_config(page_title="Dataset Manager | OmniMetrics", page_icon="🗂️", layout="wide")
load_css(); brand(); require_login()
page_header("Dataset workspace", "Bring your data together, inspect its structure and manage source files.", "DATA OPERATIONS")
db = next(get_db()); user_id = st.session_state["user_id"]
datasets = get_user_datasets(db, user_id)
total_rows = sum(ds.rows or 0 for ds in datasets)
total_size = sum(ds.size_bytes or 0 for ds in datasets) / (1024 * 1024)
c1, c2, c3 = st.columns(3)
c1.metric("Datasets", len(datasets)); c2.metric("Total records", f"{total_rows:,}"); c3.metric("Storage used", f"{total_size:.2f} MB")
st.markdown("### Upload a dataset")
with st.container(border=True):
    uploaded = st.file_uploader("Drop a CSV, Excel or JSON file here", type=["csv", "xlsx", "xls", "json"], label_visibility="collapsed")
    if uploaded:
        st.caption(f"Selected: {uploaded.name} · {uploaded.size / 1024:.1f} KB")
        if st.button("Upload and save dataset", type="primary"):
            with st.spinner("Validating and saving dataset..."):
                try:
                    item = save_uploaded_file(db, uploaded, user_id)
                    st.success(f"{item.name} uploaded successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Upload failed: {exc}")
st.markdown("### Your datasets")
if not datasets:
    st.info("No datasets yet. Upload your first file to get started.")
else:
    query = st.text_input("Search datasets", placeholder="Search by filename...")
    visible = [ds for ds in datasets if query.lower() in ds.name.lower()]
    for ds in visible:
        with st.container(border=True):
            a, b, c, d, e = st.columns([3, 1, 1, 1, 1.3])
            a.markdown(f"**{ds.name}**")
            a.caption(f"{(ds.file_type or '').replace('.', '').upper()} · Uploaded {ds.uploaded_at.strftime('%d %b %Y') if ds.uploaded_at else 'date unavailable'}")
            b.metric("Rows", f"{ds.rows:,}")
            c.metric("Columns", ds.columns)
            d.metric("Size", f"{ds.size_bytes / 1048576:.2f} MB")
            with e:
                if st.button("Preview", key=f"prev_{ds.id}", use_container_width=True):
                    st.session_state[f"preview_{ds.id}"] = not st.session_state.get(f"preview_{ds.id}", False)
                if st.button("Delete", key=f"del_{ds.id}", use_container_width=True):
                    delete_dataset(db, ds.id, user_id); st.rerun()
            if st.session_state.get(f"preview_{ds.id}", False):
                try:
                    frame = load_dataset_as_df(ds)
                    st.dataframe(frame.head(20), use_container_width=True)
                    st.caption(f"{len(frame):,} rows × {len(frame.columns)} columns")
                except Exception as exc:
                    st.error(f"Could not load preview: {exc}")
