from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app import crud, schemas
from app.database import get_db
from app.utils import (
    verify_password,
    create_access_token,
    get_current_user
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.post("/signup", response_model=schemas.User, status_code=201)
def signup(data: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"=== SIGNUP REQUEST ===")
    logger.info(f"Received signup data: full_name={data.full_name}, email={data.email}, phone={data.phone_number}")
    
    # Log database connection info
    logger.info(f"Database connection: {db.bind.url}")
    
    # Check if user already exists
    existing = crud.get_user_by_email(db, data.email)
    if existing:
        logger.warning(f"User already exists: {data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    logger.info(f"Creating new user: {data.email}")
    user = crud.create_user(db, data)
    logger.info(f"User created successfully with ID: {user.id}, Email: {user.email}")
    
    # Verify user was saved
    verification = crud.get_user_by_email(db, user.email)
    if verification:
        logger.info(f"✓ User verified in database: {verification.email}")
    else:
        logger.error(f"✗ User NOT found in database after creation!")
    
    logger.info(f"=== SIGNUP COMPLETE ===")
    
    # Return the created user
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {"sub": user.email}, expires_delta=expires
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
def read_me(current_user = Depends(get_current_user)):
    return current_user