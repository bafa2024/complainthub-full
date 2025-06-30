# backend/app/api/v1/endpoints/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api import deps
# Change this line in all endpoint files
from app.database import get_db
from app.utils import verify_password, get_password_hash

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(get_db), # This will now work correctly
    user_in: schemas.UserCreate,
):
    """
    Create new user.
    """
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.create_user(db=db, user=user_in)
    return user

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(deps.get_current_active_user)):
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_users_me(
    *,
    db: Session = Depends(get_db),
    user_update: schemas.UserUpdate = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Update current user's profile.
    """
    return crud.update_user(db, user_id=current_user.id, user_update=user_update)

@router.delete("/me", response_model=dict)
def delete_users_me(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Delete current user's account.
    """
    return crud.delete_user(db, user_id=current_user.id)

@router.put("/me/password", response_model=dict)
def update_user_password(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    body: dict = Body(...)
):
    """
    Update current user's password. Requires current and new password.
    """
    current_password = body.get("current_password")
    new_password = body.get("new_password")
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Both current_password and new_password are required.")
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    db.commit()
    return {"msg": "Password updated successfully."}

# ... rest of the file