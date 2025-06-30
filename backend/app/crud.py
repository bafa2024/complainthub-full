from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from typing import List, Optional
import traceback

from . import models, schemas
from .core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

#region User CRUD
def get_user(db: Session, user_id: int):
    """Get user by ID with error handling"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            logger.debug(f"User found with ID: {user_id}")
        else:
            logger.debug(f"User not found with ID: {user_id}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user by ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting user by ID {user_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_user_by_email(db: Session, email: str):
    """Get user by email with error handling"""
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            logger.debug(f"User found with email: {email}")
        else:
            logger.debug(f"User not found with email: {email}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user by email {email}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting user by email {email}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get users with pagination and error handling"""
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(users)} users (skip={skip}, limit={limit})")
        return users
    except SQLAlchemyError as e:
        logger.error(f"Database error getting users: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting users: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def create_user(db: Session, user: schemas.UserCreate):
    """Create user with comprehensive error handling"""
    logger.info(f"Attempting to create user with email: {user.email}")
    
    try:
        # First, check if user already exists to provide a clean error
        db_user_check = get_user_by_email(db, email=user.email)
        if db_user_check:
            logger.warning(f"User creation failed - email already exists: {user.email}")
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
            role=user.role,
            brand_id=getattr(user, 'brand_id', None)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created successfully with ID: {db_user.id}")
        return db_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating user: {e}")
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while creating the user."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while creating the user."
        )

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Update user profile fields with error handling"""
    user = get_user(db, user_id)
    if not user:
        logger.warning(f"User update failed - user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found.")
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User updated successfully: {user_id}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"User update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile.")

def delete_user(db: Session, user_id: int):
    """Delete a user by ID with error handling."""
    user = get_user(db, user_id)
    if not user:
        logger.warning(f"User delete failed - user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        db.delete(user)
        db.commit()
        logger.info(f"User deleted successfully: {user_id}")
        return {"msg": "User deleted successfully."}
    except Exception as e:
        db.rollback()
        logger.error(f"User delete failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user.")
#endregion

#region Brand CRUD
def get_brand(db: Session, brand_id: int):
    """Get brand by ID with error handling"""
    try:
        brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
        if brand:
            logger.debug(f"Brand found with ID: {brand_id}")
        else:
            logger.debug(f"Brand not found with ID: {brand_id}")
        return brand
    except SQLAlchemyError as e:
        logger.error(f"Database error getting brand by ID {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting brand by ID {brand_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_brand_by_name(db: Session, name: str):
    """Get brand by name with error handling"""
    try:
        brand = db.query(models.Brand).filter(models.Brand.name == name).first()
        if brand:
            logger.debug(f"Brand found with name: {name}")
        else:
            logger.debug(f"Brand not found with name: {name}")
        return brand
    except SQLAlchemyError as e:
        logger.error(f"Database error getting brand by name {name}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting brand by name {name}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    """Get brands with pagination and error handling"""
    try:
        brands = db.query(models.Brand).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(brands)} brands (skip={skip}, limit={limit})")
        return brands
    except SQLAlchemyError as e:
        logger.error(f"Database error getting brands: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting brands: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def create_brand(db: Session, brand: schemas.BrandCreate):
    """Create brand with comprehensive error handling"""
    logger.info(f"Creating brand with name: {brand.name}")
    try:
        db_brand = models.Brand(**brand.dict())
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        logger.info(f"Brand created successfully with ID: {db_brand.id}")
        return db_brand
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating brand: {e}")
        raise HTTPException(
            status_code=400,
            detail="A brand with this name already exists."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating brand: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while creating the brand."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating brand: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while creating the brand."
        )

def update_brand(db: Session, brand_id: int, brand_update: schemas.BrandUpdate):
    """Update brand with error handling"""
    try:
        db_brand = get_brand(db, brand_id)
        if not db_brand:
            logger.warning(f"Brand update failed - brand not found: {brand_id}")
            return None
            
        update_data = brand_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_brand, key, value)
        
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        
        logger.info(f"Brand updated successfully: {brand_id}")
        return db_brand
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating brand {brand_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Update failed due to constraint violation."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating brand {brand_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while updating the brand."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating brand {brand_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while updating the brand."
        )
#endregion

#region Ticket CRUD
def get_ticket(db: Session, ticket_id: int):
    """Get ticket by ID with error handling"""
    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if ticket:
            logger.debug(f"Ticket found with ID: {ticket_id}")
        else:
            logger.debug(f"Ticket not found with ID: {ticket_id}")
        return ticket
    except SQLAlchemyError as e:
        logger.error(f"Database error getting ticket by ID {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting ticket by ID {ticket_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_public_tickets(db: Session, skip: int = 0, limit: int = 100):
    """Get public tickets with error handling"""
    try:
        tickets = db.query(models.Ticket).filter(
            models.Ticket.is_public == True,
            models.Ticket.status.notin_([models.TicketStatusEnum.resolved, models.TicketStatusEnum.closed])
        ).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.debug(f"Retrieved {len(tickets)} public tickets (skip={skip}, limit={limit})")
        return tickets
    except SQLAlchemyError as e:
        logger.error(f"Database error getting public tickets: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting public tickets: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_tickets(db: Session, skip: int = 0, limit: int = 100):
    """Get all tickets with error handling"""
    try:
        tickets = db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(tickets)} tickets (skip={skip}, limit={limit})")
        return tickets
    except SQLAlchemyError as e:
        logger.error(f"Database error getting tickets: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting tickets: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_tickets_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """Get tickets by brand with error handling"""
    try:
        tickets = db.query(models.Ticket).filter(models.Ticket.brand_id == brand_id).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(tickets)} tickets for brand {brand_id} (skip={skip}, limit={limit})")
        return tickets
    except SQLAlchemyError as e:
        logger.error(f"Database error getting tickets for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting tickets for brand {brand_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_tickets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get tickets by user with error handling"""
    try:
        tickets = db.query(models.Ticket).filter(models.Ticket.owner_id == user_id).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(tickets)} tickets for user {user_id} (skip={skip}, limit={limit})")
        return tickets
    except SQLAlchemyError as e:
        logger.error(f"Database error getting tickets for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting tickets for user {user_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def create_ticket(db: Session, ticket: schemas.TicketCreate, owner_id: int):
    """Create ticket with comprehensive error handling"""
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
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating ticket: {e}")
        raise HTTPException(
            status_code=400,
            detail="Ticket creation failed due to constraint violation."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating ticket: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while creating the ticket."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating ticket: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while creating the ticket."
        )

def update_ticket(db: Session, ticket_id: int, ticket_update: schemas.TicketUpdate):
    """Update ticket with error handling"""
    try:
        db_ticket = get_ticket(db, ticket_id)
        if not db_ticket:
            logger.warning(f"Ticket update failed - ticket not found: {ticket_id}")
            return None
        
        update_data = ticket_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ticket, key, value)
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        logger.info(f"Ticket updated successfully: {ticket_id}")
        return db_ticket
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Update failed due to constraint violation."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while updating the ticket."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating ticket {ticket_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while updating the ticket."
        )
#endregion