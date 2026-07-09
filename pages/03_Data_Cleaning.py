import streamlit as st
import pandas as pd
import io
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from preprocessing.cleaner import handle_missing_values, remove_duplicates, encode_categorical, scale_features, handle_outliers

st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")

if 'user_id' not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

db = next(get_db())
user_id = st.session_state['user_id']

st.title("🧹 Data Cleaning")

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload a dataset in the Dataset Manager.")
    st.stop()

# Select Dataset
dataset_names = {ds.name: ds for ds in datasets}
selected_ds_name = st.selectbox("Select a dataset to clean", list(dataset_names.keys()))
dataset_obj = dataset_names[selected_ds_name]

if 'current_df' not in st.session_state or st.session_state.get('current_ds_name') != selected_ds_name:
    try:
        st.session_state['current_df'] = load_dataset_as_df(dataset_obj)
        st.session_state['current_ds_name'] = selected_ds_name
        st.session_state['history'] = [] # For undo functionality
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

df = st.session_state['current_df']

def update_df(new_df, action_name):
    st.session_state['history'].append((df.copy(), action_name))
    st.session_state['current_df'] = new_df
    st.rerun()

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Data Preview")
    st.dataframe(df.head(50), use_container_width=True)
    
    st.subheader("Data Quality Report")
    report_col1, report_col2, report_col3 = st.columns(3)
    report_col1.metric("Total Rows", df.shape[0])
    report_col2.metric("Total Columns", df.shape[1])
    report_col3.metric("Duplicate Rows", df.duplicated().sum())
    
    st.write("**Missing Values:**")
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0].reset_index()
    if not missing_data.empty:
        missing_data.columns = ['Column', 'Missing Count']
        st.dataframe(missing_data, use_container_width=True)
    else:
        st.success("No missing values found!")

with col2:
    st.subheader("Cleaning Operations")
    
    # 1. Missing Values
    with st.expander("Missing Values"):
        miss_cols = st.multiselect("Select columns", df.columns, key="miss_cols")
        miss_strat = st.selectbox("Strategy", ["Drop Rows", "Drop Columns", "Mean", "Median", "Mode", "Forward Fill", "Backward Fill", "KNN Imputer"])
        if st.button("Apply Imputation"):
            try:
                new_df = handle_missing_values(df, miss_strat, miss_cols)
                update_df(new_df, f"Handled missing values ({miss_strat})")
            except Exception as e:
                st.error(str(e))
                
    # 2. Duplicates
    with st.expander("Remove Duplicates"):
        if st.button("Drop Duplicate Rows"):
            new_df = remove_duplicates(df)
            update_df(new_df, "Removed duplicates")
            
    # 3. Categorical Encoding
    with st.expander("Categorical Encoding"):
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        enc_cols = st.multiselect("Select Categorical Columns", cat_cols)
        enc_strat = st.selectbox("Encoding Strategy", ["Label Encoding", "One Hot Encoding"])
        if st.button("Apply Encoding"):
            if not enc_cols:
                st.error("Please select at least one column.")
            else:
                try:
                    new_df = encode_categorical(df, enc_strat, enc_cols)
                    update_df(new_df, f"{enc_strat} applied")
                except Exception as e:
                    st.error(str(e))
                
    # 4. Feature Scaling
    with st.expander("Feature Scaling"):
        num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        scale_cols = st.multiselect("Select Numerical Columns", num_cols, key="scale_cols")
        scale_strat = st.selectbox("Scaler", ["StandardScaler", "MinMaxScaler", "RobustScaler"])
        if st.button("Apply Scaling"):
            if not scale_cols:
                st.error("Please select at least one column.")
            else:
                try:
                    new_df = scale_features(df, scale_strat, scale_cols)
                    update_df(new_df, f"{scale_strat} applied")
                except Exception as e:
                    st.error(str(e))
                
    # 5. Outliers
    with st.expander("Handle Outliers"):
        out_cols = st.multiselect("Select Numerical Columns", num_cols, key="out_cols")
        out_strat = st.selectbox("Strategy", ["IQR (Clip)"])
        if st.button("Apply Outlier Handling"):
            if not out_cols:
                st.error("Please select at least one column.")
            else:
                try:
                    new_df = handle_outliers(df, out_strat, out_cols)
                    update_df(new_df, "Outliers clipped (IQR)")
                except Exception as e:
                    st.error(str(e))

    st.markdown("---")
    if st.button("⏪ Undo Last Action") and st.session_state['history']:
        last_df, action = st.session_state['history'].pop()
        st.session_state['current_df'] = last_df
        st.rerun()

    if st.button("💾 Download Cleaned Dataset"):
        csv = st.session_state['current_df'].to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"cleaned_{selected_ds_name}.csv",
            mime="text/csv",
        )
