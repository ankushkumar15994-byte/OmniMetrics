import os
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from database.models import Dataset
from config.settings import UPLOAD_DIR
from authentication.auth_service import log_activity
from datetime import datetime

def save_uploaded_file(db: Session, uploaded_file, user_id: int) -> Dataset:
    """Save an uploaded file to disk and record it in the database."""
    # Ensure unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(uploaded_file.name).suffix
    safe_filename = f"{user_id}_{timestamp}_{uploaded_file.name}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save to disk
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    # Read with pandas to get metadata
    if file_extension == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
    elif file_extension == '.json':
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format")
        
    rows, cols = df.shape
    size_bytes = os.path.getsize(file_path)
    
    # Save to database
    new_dataset = Dataset(
        owner_id=user_id,
        name=uploaded_file.name,
        file_path=str(file_path),
        file_type=file_extension,
        rows=rows,
        columns=cols,
        size_bytes=size_bytes
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    
    log_activity(db, user_id, f"Uploaded Dataset: {uploaded_file.name}")
    return new_dataset

def get_user_datasets(db: Session, user_id: int):
    return db.query(Dataset).filter(Dataset.owner_id == user_id).order_by(Dataset.uploaded_at.desc()).all()

def load_dataset_as_df(dataset: Dataset) -> pd.DataFrame:
    """Loads a dataset from the database record into a pandas DataFrame."""
    if dataset.file_type == '.csv':
        return pd.read_csv(dataset.file_path)
    elif dataset.file_type in ['.xls', '.xlsx']:
        return pd.read_excel(dataset.file_path)
    elif dataset.file_type == '.json':
        return pd.read_json(dataset.file_path)
    else:
        raise ValueError("Unsupported file format")

def delete_dataset(db: Session, dataset_id: int, user_id: int):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == user_id).first()
    if dataset:
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        name = dataset.name
        db.delete(dataset)
        db.commit()
        log_activity(db, user_id, f"Deleted Dataset: {name}")
        return True
    return False
