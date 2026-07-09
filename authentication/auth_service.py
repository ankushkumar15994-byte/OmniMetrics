from sqlalchemy.orm import Session
from database.models import User, ActivityLog
from utils.auth_utils import hash_password, verify_password

def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, username: str, email: str, password: str) -> User:
    # Check if user exists
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise ValueError("Username or Email already registered.")
        
    hashed_pwd = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_activity(db, new_user.id, "User Registered")
    return new_user

def log_activity(db: Session, user_id: int, action: str, details: str = None):
    log = ActivityLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()
