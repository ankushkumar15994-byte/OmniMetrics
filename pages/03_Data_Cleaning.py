import streamlit as st
import pandas as pd
import io
from database.db import get_db
from services.data_manager import get_user_datasets, load_dataset_as_df
from preprocessing.cleaner import handle_missing_values, remove_duplicates, encode_categorical, scale_features, handle_outliers
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")
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
        <span style="color: #6366f1;">ETL & Hygiene Engine</span>
    </div>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;">
        Smart <span class="gradient-text">Data Cleaning</span>
    </h1>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-top: 4px;">
        Impute missing values, drop duplicates, encode categorical attributes, and isolate statistical outliers with step-by-step undo.
    </p>
</div>
""", unsafe_allow_html=True)

datasets = get_user_datasets(db, user_id)
if not datasets:
    st.warning("No datasets available. Please upload a dataset in the Data Workspace.")
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

col1, col2 = st.columns([7, 4])

with col1:
    st.markdown("### Data Preview")
    st.dataframe(df.head(50), use_container_width=True)
    
    st.markdown("### Data Quality Overview")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        st.metric("Total Rows", df.shape[0])
    with report_col2:
        st.metric("Total Columns", df.shape[1])
    with report_col3:
        st.metric("Duplicate Rows", df.duplicated().sum())
    
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0].reset_index()
    if not missing_data.empty:
        missing_data.columns = ['Column', 'Missing Count']
        st.markdown("**Columns with Missing Values:**")
        st.dataframe(missing_data, use_container_width=True)
    else:
        st.success("No missing values found!")

with col2:
    st.markdown("### Cleaning Operations")
    
    # 0. Drop Columns
    with st.expander("🗑️ Drop Columns"):
        cols_to_drop = st.multiselect("Select columns to remove", df.columns, key="drop_cols")
        if st.button("Drop Selected Columns", type="primary"):
            if cols_to_drop:
                new_df = df.drop(columns=cols_to_drop)
                update_df(new_df, f"Dropped columns: {', '.join(cols_to_drop)}")
            else:
                st.error("Select at least one column.")
                
    # 0.1 Data Type Conversion
    with st.expander("🔄 Convert Data Types"):
        col_to_convert = st.selectbox("Select column to convert", df.columns, key="conv_col")
        new_type = st.selectbox("Target Type", ["numeric (float)", "integer", "datetime", "string", "categorical"])
        if st.button("Convert Type", type="primary"):
            try:
                new_df = df.copy()
                if new_type == "numeric (float)":
                    new_df[col_to_convert] = pd.to_numeric(new_df[col_to_convert], errors='coerce')
                elif new_type == "integer":
                    new_df[col_to_convert] = pd.to_numeric(new_df[col_to_convert], errors='coerce').astype('Int64')
                elif new_type == "datetime":
                    new_df[col_to_convert] = pd.to_datetime(new_df[col_to_convert], errors='coerce')
                elif new_type == "string":
                    new_df[col_to_convert] = new_df[col_to_convert].astype(str)
                elif new_type == "categorical":
                    new_df[col_to_convert] = new_df[col_to_convert].astype('category')
                update_df(new_df, f"Converted {col_to_convert} to {new_type}")
            except Exception as e:
                st.error(f"Conversion failed: {e}")
                
    # 1. Missing Values
    with st.expander("🩹 Missing Values"):
        miss_cols = st.multiselect("Select columns", df.columns, key="miss_cols")
        miss_strat = st.selectbox("Strategy", ["Drop Rows", "Mean", "Median", "Mode", "Forward Fill", "Backward Fill", "KNN Imputer"])
        if st.button("Apply Imputation", type="primary"):
            try:
                new_df = handle_missing_values(df, miss_strat, miss_cols)
                update_df(new_df, f"Handled missing values ({miss_strat})")
            except Exception as e:
                st.error(str(e))
                
    # 2. Duplicates
    with st.expander("✂️ Remove Duplicates"):
        if st.button("Drop Duplicate Rows", type="primary"):
            new_df = remove_duplicates(df)
            update_df(new_df, "Removed duplicates")
            
    # 3. Categorical Encoding
    with st.expander("🔢 Categorical Encoding"):
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        enc_cols = st.multiselect("Select Categorical Columns", cat_cols)
        enc_strat = st.selectbox("Encoding Strategy", ["Label Encoding", "One Hot Encoding"])
        if st.button("Apply Encoding", type="primary"):
            if not enc_cols:
                st.error("Please select at least one column.")
            else:
                try:
                    new_df = encode_categorical(df, enc_strat, enc_cols)
                    update_df(new_df, f"{enc_strat} applied")
                except Exception as e:
                    st.error(str(e))
                
    # 4. Feature Scaling (Warning about data leakage)
    with st.expander("⚖️ Feature Scaling"):
        st.info("⚠️ Note: If you plan to train models, it is better to scale features inside the ML pipeline to prevent data leakage.")
        num_cols = df.select_dtypes(include=['int64', 'float64', 'Int64']).columns.tolist()
        scale_cols = st.multiselect("Select Numerical Columns", num_cols, key="scale_cols")
        scale_strat = st.selectbox("Scaler", ["StandardScaler", "MinMaxScaler", "RobustScaler"])
        if st.button("Apply Scaling", type="primary"):
            if not scale_cols:
                st.error("Please select at least one column.")
            else:
                try:
                    new_df = scale_features(df, scale_strat, scale_cols)
                    update_df(new_df, f"{scale_strat} applied")
                except Exception as e:
                    st.error(str(e))
                
    # 5. Outliers
    with st.expander("🎯 Handle Outliers"):
        out_cols = st.multiselect("Select Numerical Columns", num_cols, key="out_cols")
        out_strat = st.selectbox("Strategy", ["IQR (Clip)"])
        if st.button("Apply Outlier Handling", type="primary"):
            if not out_cols:
                st.error("Please select at least one column.")
            else:
                try:
                    new_df = handle_outliers(df, out_strat, out_cols)
                    update_df(new_df, "Outliers clipped (IQR)")
                except Exception as e:
                    st.error(str(e))
                    
    # 6. Train/Test Split Download
    with st.expander("✂️ Train/Test Split (Download)"):
        st.write("Split your cleaned dataset into training and testing files.")
        target_col = st.selectbox("Target Column (Optional for stratification)", ["None"] + list(df.columns))
        test_size = st.slider("Test Size %", 10, 50, 20)
        if st.button("Generate Split", type="primary"):
            try:
                y = df[target_col] if target_col != "None" else None
                stratify_arg = y if (target_col != "None" and df[target_col].nunique() < 20) else None
                
                train, test = train_test_split(df, test_size=test_size/100, stratify=stratify_arg, random_state=42)
                st.session_state['split_train'] = train
                st.session_state['split_test'] = test
                st.success("Split generated! Download below.")
            except Exception as e:
                st.error(f"Split failed: {e}")
                
        if 'split_train' in st.session_state:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="Download Train Set",
                    data=st.session_state['split_train'].to_csv(index=False),
                    file_name=f"train_{selected_ds_name}.csv",
                    mime="text/csv",
                )
            with col_d2:
                st.download_button(
                    label="Download Test Set",
                    data=st.session_state['split_test'].to_csv(index=False),
                    file_name=f"test_{selected_ds_name}.csv",
                    mime="text/csv",
                )

    st.markdown("---")
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("⏪ Undo Last Action", use_container_width=True) and st.session_state['history']:
            last_df, action = st.session_state['history'].pop()
            st.session_state['current_df'] = last_df
            st.rerun()

    with action_col2:
        if st.button("💾 Download Full Cleaned Dataset", type="primary", use_container_width=True):
            csv = st.session_state['current_df'].to_csv(index=False)
            st.download_button(
                label="Confirm Download",
                data=csv,
                file_name=f"cleaned_{selected_ds_name}.csv",
                mime="text/csv",
                use_container_width=True
            )
