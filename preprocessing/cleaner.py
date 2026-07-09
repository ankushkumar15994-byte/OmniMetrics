import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder

def handle_missing_values(df: pd.DataFrame, strategy: str, columns: list = None) -> pd.DataFrame:
    df_clean = df.copy()
    if not columns:
        columns = df_clean.columns

    if strategy == "Drop Rows":
        df_clean = df_clean.dropna(subset=columns)
    elif strategy == "Drop Columns":
        df_clean = df_clean.drop(columns=columns)
    else:
        for col in columns:
            if df_clean[col].dtype in ['float64', 'int64']:
                if strategy == "Mean":
                    df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                elif strategy == "Median":
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                elif strategy == "Mode":
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
                elif strategy == "Forward Fill":
                    df_clean[col].ffill(inplace=True)
                elif strategy == "Backward Fill":
                    df_clean[col].bfill(inplace=True)
                elif strategy == "KNN Imputer":
                    imputer = KNNImputer(n_neighbors=5)
                    # Reshape for single column imputation
                    df_clean[col] = imputer.fit_transform(df_clean[[col]])
            else:
                # For categorical, fallback to mode or fill
                if strategy in ["Mode", "Mean", "Median"]:
                    if not df_clean[col].mode().empty:
                        df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
                elif strategy == "Forward Fill":
                    df_clean[col].ffill(inplace=True)
                elif strategy == "Backward Fill":
                    df_clean[col].bfill(inplace=True)
                    
    return df_clean

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

def encode_categorical(df: pd.DataFrame, strategy: str, columns: list) -> pd.DataFrame:
    df_clean = df.copy()
    if strategy == "Label Encoding":
        le = LabelEncoder()
        for col in columns:
            # Handle possible NaNs before encoding by casting to string
            df_clean[col] = le.fit_transform(df_clean[col].astype(str))
    elif strategy == "One Hot Encoding":
        df_clean = pd.get_dummies(df_clean, columns=columns, drop_first=True)
    return df_clean

def scale_features(df: pd.DataFrame, strategy: str, columns: list) -> pd.DataFrame:
    df_clean = df.copy()
    if not columns:
        return df_clean
        
    if strategy == "StandardScaler":
        scaler = StandardScaler()
    elif strategy == "MinMaxScaler":
        scaler = MinMaxScaler()
    elif strategy == "RobustScaler":
        scaler = RobustScaler()
    else:
        return df_clean
        
    df_clean[columns] = scaler.fit_transform(df_clean[columns])
    return df_clean

def handle_outliers(df: pd.DataFrame, strategy: str, columns: list) -> pd.DataFrame:
    df_clean = df.copy()
    if not columns:
        return df_clean
        
    for col in columns:
        if df_clean[col].dtype in ['float64', 'int64']:
            if strategy == "IQR (Clip)":
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)
    return df_clean
