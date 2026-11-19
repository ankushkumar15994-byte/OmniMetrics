# OmniMetrics - Premium AI Analytics Platform

An enterprise-grade, production-ready web application built with Python and Streamlit for comprehensive data analytics. It seamlessly integrates Automated EDA, Data Cleaning, Auto-ML, and AI-powered insights into a single, cohesive workspace.

## 🚀 Features

- **Data Workspace:** Secure dataset management (CSV, Excel, JSON) with drag-and-drop upload, automatic schema validation, and instant data quality profiles.
- **Smart Data Cleaning:** Intuitive tools to handle missing values, duplicates, outliers, and type conversions, featuring "Undo" capabilities and Train/Test splits.
- **Exploratory Data Analysis (EDA):** Interactive, themed Plotly charts and automated comprehensive profiling reports.
- **AutoML Studio:** Train and evaluate Classification, Regression, and Clustering models in parallel. Compare metrics on an interactive leaderboard and export the best models.
- **Visual Analytics Dashboard Builder:** Drag-and-drop interface to assemble custom KPIs and interactive charts for reporting.
- **AI-Powered Insights Engine:** Automatically generates executive summaries, detects dataset anomalies, and recommends actionable next steps with Markdown export.
- **Stitch Design System UI:** Enterprise dark-mode aesthetic with micro-structured borders, live telemetry streams, responsive KPI grids, and custom theme presets.
- **Secure Authentication:** Built-in local authentication and user session management with SQLite and PostgreSQL support.
- **Robust Database Engine:** Built with SQLAlchemy NullPool and automated transaction rollback prevention for high reliability and zero connection pool exhaustion.

## 📸 Screenshots
*(Add screenshots of your application here to showcase the premium dark UI and interactive charts.)*

## 🛠️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd OmniMetrics-main
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application Locally:**
   ```bash
   streamlit run app.py
   ```
   Navigate to `http://localhost:8501` to view the platform.

## ⚙️ Configuration
OmniMetrics uses sensible defaults. Optional configurations can be set via `.env` files or environment variables:
- `DATABASE_URL`: Set to a PostgreSQL string for production (defaults to local SQLite).
- `LLM_API_KEY`: Add your API key if extending the AI Insights tab to use an external LLM. 
*(Note: Never commit real credentials or API keys to source control!)*

## ☁️ Deployment to Streamlit Community Cloud

Deploying OmniMetrics is quick and easy:
1. Ensure your code is pushed to a public or private GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **New app**.
4. Select your repository, branch, and set `app.py` as the Main file path.
5. Expand **Advanced Settings**:
   - Add any environment variables or secrets in the "Secrets" block (e.g., `DATABASE_URL` if using a remote DB).
6. Click **Deploy!**

*Note on Persistence: Streamlit Community Cloud provides an ephemeral filesystem. If using SQLite, uploaded datasets and newly registered users will be lost on container restart. For production deployments, connect to an external PostgreSQL database (e.g., Supabase, Neon) and configure AWS S3 for file storage.*

## 📐 Architecture
Built adhering to SOLID principles and Clean Architecture, utilizing Streamlit's latest layout, caching, and state management features.
