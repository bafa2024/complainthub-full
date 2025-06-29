from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional

from . import models, schemas
from .core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

#region User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    logger.info(f"Attempting to create user with email: {user.email}")
    
    # First, check if user already exists to provide a clean error
    db_user_check = get_user_by_email(db, email=user.email)
    if db_user_check:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
        
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone_number=user.phone_number,
        role=user.role
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        # This is a fallback in case of a race condition
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"An unexpected error occurred creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while creating the user."
        )

    logger.info(f"User created successfully with ID: {db_user.id}")
    return db_user
#endregion

#region Brand CRUD
def get_brand(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()

def get_brand_by_name(db: Session, name: str):
    return db.query(models.Brand).filter(models.Brand.name == name).first()

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Brand).offset(skip).limit(limit).all()

def create_brand(db: Session, brand: schemas.BrandCreate):
    logger.info(f"Creating brand with name: {brand.name}")
    try:
        db_brand = models.Brand(**brand.dict())
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        logger.info(f"Brand created successfully with ID: {db_brand.id}")
        return db_brand
    except Exception as e:
        logger.error(f"Error creating brand: {e}")
        db.rollback()
        raise

def update_brand(db: Session, brand_id: int, brand_update: schemas.BrandUpdate):
    db_brand = get_brand(db, brand_id)
    if not db_brand:
        return None
    update_data = brand_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_brand, key, value)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand
#endregion

#region Ticket CRUD
def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def get_public_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ticket).filter(
        models.Ticket.is_public == True,
        models.Ticket.status.notin_([models.TicketStatusEnum.resolved, models.TicketStatusEnum.closed])
    ).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def get_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def get_tickets_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Ticket).filter(models.Ticket.brand_id == brand_id).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def get_tickets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Ticket).filter(models.Ticket.owner_id == user_id).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def create_ticket(db: Session, ticket: schemas.TicketCreate, owner_id: int):
    logger.info(f"Creating ticket titled '{ticket.title}' for brand_id {ticket.brand_id}")
    try:
        db_ticket = models.Ticket(
            **ticket.dict(),
            owner_id=owner_id,
            status=models.TicketStatusEnum.new
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        logger.info(f"Ticket created successfully with ID: {db_ticket.id}")
        return db_ticket
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        db.rollback()
        raise

def update_ticket(db: Session, ticket_id: int, ticket_update: schemas.TicketUpdate):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    
    update_data = ticket_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
#endregion