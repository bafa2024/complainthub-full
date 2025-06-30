# backend/app/api/v1/endpoints/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api import deps
# Change this line in all endpoint files
from app.database import get_db

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

# ... rest of the file