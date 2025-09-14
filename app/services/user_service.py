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

def check_email_exists(db: Session, email: str, id:int) -> bool:
    if not email:
        return False
    exists = db.query(db.query(User).filter(User.email == email).filter(User.id!=id).exists()).scalar()
    return exists

def update_user(db: Session, user_id: int, username: str = None, email: str = None,password: str = None, phone: str =None) -> User|None:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if username is not None and username != user.username:
            user.username = username
        if email is not None and email != user.email:
            user.email = email
        if password is not None:
            if not verify_password(password, user.hashed_password):
                user.hashed_password = hash_password(password)
        if phone is not None and phone != user.phone:
            user.phone = phone
        if db.is_modified(user):
            db.commit()
            db.refresh(user)
        return user
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error updating user: {str(e)}") from e
    
    