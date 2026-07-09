import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score, silhouette_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
import joblib
import os
from config.settings import BASE_DIR

MODELS_DIR = BASE_DIR / "saved_models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def train_classification(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42)
    }
    
    results = []
    trained_models = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision (Macro)": prec,
            "Recall (Macro)": rec,
            "F1-Score (Macro)": f1
        })
        trained_models[name] = model
        
    return pd.DataFrame(results), trained_models

def train_regression(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42)
    }
    
    results = []
    trained_models = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results.append({
            "Model": name,
            "MSE": mse,
            "MAE": mae,
            "R2 Score": r2
        })
        trained_models[name] = model
        
    return pd.DataFrame(results), trained_models

def train_clustering(df: pd.DataFrame, n_clusters: int = 3):
    models = {
        "K-Means": KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    }
    
    results = []
    trained_models = {}
    
    for name, model in models.items():
        labels = model.fit_predict(df)
        sil = silhouette_score(df, labels) if len(set(labels)) > 1 else -1
        
        results.append({
            "Model": name,
            "Silhouette Score": sil
        })
        trained_models[name] = model
        
    return pd.DataFrame(results), trained_models

def save_model(model, filename: str) -> str:
    path = MODELS_DIR / filename
    joblib.dump(model, path)
    return str(path)
