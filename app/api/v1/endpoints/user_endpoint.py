from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import create_user, get_user_by_id, get_all_users, delete_user_by_id, check_email_exists,update_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED,)
def create_new_user(user: UserCreate, db: Session = Depends(get_db),):
    db_user = create_user(db, user.username, user.email, user.password, user.phone)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User could not be created")
    return UserRead.model_validate(db_user)

@router.get("/", response_model=list[UserRead])
def read_users(db: Session = Depends(get_db)):
    all_db_users = get_all_users(db)
    if not all_db_users:
        raise HTTPException(status_code=404, detail="Users not found")
    return  [UserRead.model_validate(user) for user in all_db_users]

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(db_user)

@router.patch("/{user_id}",  response_model=UserRead)
def patch_user(user_id: int, user_changes: UserUpdate,db: Session = Depends(get_db)):
    update_data = user_changes.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No fields provided for update")
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_changes.email is not None and user_changes.email != db_user.email:
        if check_email_exists(db, user_changes.email, user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user")
    db_user = update_user(db, user_id, user_changes.username, user_changes.email, user_changes.password, user_changes.phone)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found during update")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = delete_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User to delete not found")
