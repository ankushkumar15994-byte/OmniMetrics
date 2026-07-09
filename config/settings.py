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
APP_NAME = os.getenv("APP_NAME", "DataInsight Pro")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/datainsight.db")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
