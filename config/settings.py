import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"

# Create required directories if they don't exist
for d in [DATA_DIR, UPLOAD_DIR, EXPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Application Settings
def _get_setting(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if not val:
        try:
            import streamlit as st
            if key in st.secrets:
                val = str(st.secrets[key])
        except Exception:
            pass
    return val if val else default

APP_NAME = _get_setting("APP_NAME", "DataInsight Pro")
DATABASE_URL = _get_setting("DATABASE_URL", f"sqlite:///{DATA_DIR}/datainsight.db")
SECRET_KEY = _get_setting("SECRET_KEY", "default-secret-key")
ENVIRONMENT = _get_setting("ENVIRONMENT", "development")
LLM_API_KEY = _get_setting("LLM_API_KEY", "")
