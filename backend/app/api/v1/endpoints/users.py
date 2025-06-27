# backend/app/api/v1/endpoints/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
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
# ... rest of the file