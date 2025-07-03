from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from typing import List, Optional
import traceback
from datetime import datetime

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

def delete_brand(db: Session, brand_id: int):
    """Delete a brand by ID with error handling."""
    brand = get_brand(db, brand_id)
    if not brand:
        logger.warning(f"Brand delete failed - brand not found: {brand_id}")
        raise HTTPException(status_code=404, detail="Brand not found.")
    
    # Check for related records before deletion
    try:
        # Check for users associated with this brand
        users_count = db.query(models.User).filter(models.User.brand_id == brand_id).count()
        if users_count > 0:
            logger.warning(f"Brand delete failed - {users_count} users associated with brand: {brand_id}")
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete brand. There are {users_count} users associated with this brand. Please remove or reassign users first."
            )
        
        # Check for tickets associated with this brand
        tickets_count = db.query(models.Ticket).filter(models.Ticket.brand_id == brand_id).count()
        if tickets_count > 0:
            logger.warning(f"Brand delete failed - {tickets_count} tickets associated with brand: {brand_id}")
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete brand. There are {tickets_count} tickets associated with this brand. Please delete or reassign tickets first."
            )
        
        # Check for team invitations associated with this brand
        invitations_count = db.query(models.TeamInvitation).filter(models.TeamInvitation.brand_id == brand_id).count()
        if invitations_count > 0:
            logger.warning(f"Brand delete failed - {invitations_count} team invitations associated with brand: {brand_id}")
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete brand. There are {invitations_count} team invitations associated with this brand. Please delete invitations first."
            )
        
        # If no related records, proceed with deletion
        db.delete(brand)
        db.commit()
        logger.info(f"Brand deleted successfully: {brand_id}")
        return {"msg": "Brand deleted successfully."}
        
    except HTTPException:
        # Re-raise HTTP exceptions (our custom error messages)
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Brand delete failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete brand.")
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

def get_tickets_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100, status: str = None):
    """Get tickets by brand with optional status filter and error handling"""
    try:
        query = db.query(models.Ticket).filter(models.Ticket.brand_id == brand_id)
        if status:
            query = query.filter(models.Ticket.status == status)
        tickets = query.order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(tickets)} tickets for brand {brand_id} (status={status}, skip={skip}, limit={limit})")
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
    logger.info(f"Starting ticket update - Ticket ID: {ticket_id}")
    logger.info(f"Update data received: {ticket_update.dict()}")
    
    try:
        db_ticket = get_ticket(db, ticket_id)
        if not db_ticket:
            logger.warning(f"Ticket update failed - ticket not found: {ticket_id}")
            return None
        
        logger.info(f"Found ticket - Current status: {db_ticket.status}")
        
        update_data = ticket_update.dict(exclude_unset=True)
        logger.info(f"Fields to update: {update_data}")
        
        for key, value in update_data.items():
            logger.info(f"Setting {key} = {value}")
            setattr(db_ticket, key, value)
        
        logger.info(f"Updated ticket status to: {db_ticket.status}")
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        logger.info(f"Ticket updated successfully: {ticket_id}, New status: {db_ticket.status}")
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

#region Team Invitation CRUD
def create_team_invitation(db: Session, invitation: schemas.TeamInvitationCreate, brand_id: int, invited_by: int, invitation_token: str, expires_at: datetime):
    """Create team invitation with comprehensive error handling"""
    logger.info(f"Creating team invitation for email: {invitation.email}, brand_id: {brand_id}")
    try:
        db_invitation = models.TeamInvitation(
            email=invitation.email,
            role=invitation.role,
            brand_id=brand_id,
            invited_by=invited_by,
            invitation_token=invitation_token,
            expires_at=expires_at
        )
        db.add(db_invitation)
        db.commit()
        db.refresh(db_invitation)
        logger.info(f"Team invitation created successfully with ID: {db_invitation.id}")
        return db_invitation
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating team invitation: {e}")
        raise HTTPException(
            status_code=400,
            detail="Team invitation creation failed due to constraint violation."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating team invitation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while creating the team invitation."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating team invitation: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while creating the team invitation."
        )

def get_team_members_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """Get team members by brand with error handling"""
    try:
        team_members = db.query(models.User).filter(
            models.User.brand_id == brand_id,
            models.User.role.in_([models.RoleEnum.brand_user, models.RoleEnum.admin])
        ).order_by(models.User.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.debug(f"Retrieved {len(team_members)} team members for brand {brand_id}")
        return team_members
    except SQLAlchemyError as e:
        logger.error(f"Database error getting team members for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting team members for brand {brand_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_team_invitation_by_token(db: Session, token: str):
    """Get team invitation by token with error handling"""
    try:
        invitation = db.query(models.TeamInvitation).filter(
            models.TeamInvitation.invitation_token == token
        ).first()
        if invitation:
            logger.debug(f"Team invitation found with token: {token}")
        else:
            logger.debug(f"Team invitation not found with token: {token}")
        return invitation
    except SQLAlchemyError as e:
        logger.error(f"Database error getting team invitation by token {token}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting team invitation by token {token}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_team_invitations_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """Get team invitations by brand with error handling"""
    try:
        invitations = db.query(models.TeamInvitation).filter(
            models.TeamInvitation.brand_id == brand_id
        ).order_by(models.TeamInvitation.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.debug(f"Retrieved {len(invitations)} team invitations for brand {brand_id}")
        return invitations
    except SQLAlchemyError as e:
        logger.error(f"Database error getting team invitations for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error getting team invitations for brand {brand_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

def accept_team_invitation(db: Session, invitation_id: int, user_data: schemas.TeamInvitationAccept):
    """Accept team invitation and create user with error handling"""
    logger.info(f"Accepting team invitation ID: {invitation_id}")
    try:
        # Get the invitation
        invitation = db.query(models.TeamInvitation).filter(
            models.TeamInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            logger.warning(f"Team invitation not found: {invitation_id}")
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        if invitation.is_accepted:
            logger.warning(f"Team invitation already accepted: {invitation_id}")
            raise HTTPException(status_code=400, detail="Invitation already accepted")
        
        if invitation.expires_at < datetime.utcnow():
            logger.warning(f"Team invitation expired: {invitation_id}")
            raise HTTPException(status_code=400, detail="Invitation has expired")
        
        # Check if user already exists
        existing_user = get_user_by_email(db, invitation.email)
        if existing_user:
            logger.warning(f"User already exists with email: {invitation.email}")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = models.User(
            email=invitation.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            role=invitation.role,
            brand_id=invitation.brand_id
        )
        db.add(db_user)
        
        # Mark invitation as accepted
        invitation.is_accepted = True
        invitation.accepted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_user)
        db.refresh(invitation)
        
        logger.info(f"Team invitation accepted successfully. User created with ID: {db_user.id}")
        return db_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error accepting team invitation: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to accept invitation due to constraint violation."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error accepting team invitation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while accepting the invitation."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error accepting team invitation: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while accepting the invitation."
        )

def delete_team_invitation(db: Session, invitation_id: int):
    """Delete team invitation with error handling"""
    try:
        invitation = db.query(models.TeamInvitation).filter(
            models.TeamInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            logger.warning(f"Team invitation not found for deletion: {invitation_id}")
            return False
        
        db.delete(invitation)
        db.commit()
        logger.info(f"Team invitation deleted successfully: {invitation_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting team invitation {invitation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while deleting the invitation."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting team invitation {invitation_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while deleting the invitation."
        )
#endregion