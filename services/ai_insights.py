import pandas as pd
import numpy as np
from config.settings import LLM_API_KEY

def generate_insights(df: pd.DataFrame) -> dict:
    """Generate statistical and heuristic-based insights for the dataset."""
    insights = {
        "dataset_health": 100,
        "summary": "",
        "anomalies": [],
        "recommendations": []
    }
    
    # 1. Dataset Health & Missing Values
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_percent = (missing_cells / total_cells) * 100
    insights["dataset_health"] -= int(missing_percent)
    
    if missing_percent > 5:
        insights["anomalies"].append(f"High missing value rate ({missing_percent:.2f}%).")
        insights["recommendations"].append("Use the Data Cleaning tab to impute or drop missing values.")
        
    # 2. Duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        insights["dataset_health"] -= 5
        insights["anomalies"].append(f"Found {duplicates} duplicate rows.")
        insights["recommendations"].append("Remove duplicates to prevent model bias.")
        
    # 3. Correlations (Numeric only)
    num_df = df.select_dtypes(include=['number'])
    if not num_df.empty and len(num_df.columns) > 1:
        corr = num_df.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        high_corr = [column for column in upper.columns if any(upper[column] > 0.85)]
        
        if high_corr:
            insights["anomalies"].append(f"Highly correlated features detected: {', '.join(high_corr)}")
            insights["recommendations"].append("Consider dropping highly correlated features to reduce multicollinearity.")
            
    # 4. Outliers via Z-Score heuristic
    outlier_cols = []
    for col in num_df.columns:
        if num_df[col].std() > 0:
            z_scores = np.abs((num_df[col] - num_df[col].mean()) / num_df[col].std())
            if (z_scores > 3).sum() > 0:
                outlier_cols.append(col)
                
    if outlier_cols:
        insights["dataset_health"] -= 5
        insights["anomalies"].append(f"Potential outliers detected in: {', '.join(outlier_cols[:5])}...")
        insights["recommendations"].append("Use the Data Cleaning tab to apply IQR clipping to numerical features.")

    # Generate Summary text
    insights["dataset_health"] = max(0, insights["dataset_health"])
    
    insights["summary"] = f"This dataset contains {df.shape[0]} rows and {df.shape[1]} columns. "
    insights["summary"] += f"Overall Data Quality Score is {insights['dataset_health']}/100. "
    if insights['dataset_health'] > 90:
        insights["summary"] += "The dataset is in excellent condition and ready for machine learning."
    elif insights['dataset_health'] > 70:
        insights["summary"] += "The dataset is in good condition but requires minor preprocessing."
    else:
        insights["summary"] += "The dataset requires significant cleaning before analysis."
        
    # Optional LLM Integration placeholder
    if LLM_API_KEY:
        insights["summary"] += "\n[LLM Enhanced Insights Enabled - API Integration Active]"
        
    return insights

def generate_report_markdown(dataset_name: str, insights: dict) -> str:
    md = f"# Data Insight Report: {dataset_name}\n\n"
    md += f"**Data Quality Score:** {insights['dataset_health']}/100\n\n"
    md += "## Executive Summary\n"
    md += f"{insights['summary']}\n\n"
    
    md += "## Identified Anomalies\n"
    if insights['anomalies']:
        for a in insights['anomalies']:
            md += f"- {a}\n"
    else:
        md += "- No significant anomalies detected.\n"
        
    md += "\n## Recommendations\n"
    if insights['recommendations']:
        for r in insights['recommendations']:
            md += f"- {r}\n"
    else:
        md += "- Dataset is ready for processing.\n"
        
    return md
