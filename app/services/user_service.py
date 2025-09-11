from app.models.users import User
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password


def create_user(db: Session, username: str, email: str, password: str, phone: str):
    try:
        hashed_password = hash_password(password)
        user = User(username=username, email=email, hashed_password=hashed_password, phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        return None
    
def delete_user_by_id(db: Session, id: int):
    user = db.query(User).filter(User.id == id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    else:
        return None



def get_all_users(db: Session):
    return db.query(User).all()

def check_email_exists_sync(db: Session, email: str, id: int = None) -> bool:
    query = db.query(User).filter(User.email == email).first()
    if id is not None and query.id == id:
        return False
    return True
def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

