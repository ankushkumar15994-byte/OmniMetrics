# OmniMetrics — AI-Powered Data Analytics Platform

An enterprise-style data analytics workspace built with Python and Streamlit. The Midnight Pro interface brings your data preparation, exploration, machine learning and reporting workflows into one application.

## Features
- **Authentication:** Login, signup, session management and role-aware account context.
- **Dataset Manager:** Upload, preview and manage CSV, Excel and JSON datasets.
- **Data Cleaning:** Missing-value handling, duplicate removal, outlier treatment, encoding and scaling.
- **Exploratory Data Analysis:** Interactive Plotly charts and automated profiling.
- **Dashboard Builder:** Compose KPI metrics and interactive visualizations.
- **Machine Learning:** Train and compare classification, regression and clustering models.
- **AI Insights:** Dataset health scoring, anomaly detection and recommendations.
- **Reports:** Export insight summaries as Markdown.
- **Database Integration:** SQLAlchemy-backed metadata and activity records.
- **Activity Logs & Settings:** Review account activity and download a local SQLite backup.

## Setup

```bash
git clone https://github.com/ankushkumar15994-byte/OmniMetrics.git
cd OmniMetrics
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Interface

The app uses the **Midnight Pro** theme configured in `.streamlit/config.toml`, with a shared stylesheet in `assets/style.css` and reusable components in `utils/ui_utils.py`.

## Architecture

The UI layer is separated from the existing authentication, database, data-manager, preprocessing, visualization, machine-learning and insight services. The redesign intentionally retains those service interfaces and does not modify the database schema.

## Notes

- Uploaded files and database storage remain local to the app unless your deployment configures persistent storage.
- Run through the authentication, upload, cleaning, EDA, dashboard, ML, insights and backup flows in your own environment before deploying to production.
