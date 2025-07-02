# backend/app/api/v1/endpoints/brands.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import secrets
from datetime import datetime, timedelta

from app import crud, models, schemas
from app.api.v1 import deps # CORRECTED IMPORT PATH
from app.database import get_db # CORRECT IMPORT
from app.services.notifications import send_team_invitation_email
from app.config.settings import Settings

router = APIRouter()
settings = Settings()

@router.post("/", response_model=schemas.Brand)
def create_brand(
    *,
    db: Session = Depends(get_db), # This will now work
    brand_in: schemas.BrandCreate,
    current_user: models.User = Depends(deps.get_current_active_admin),
):
    """
    Create new brand. (Admin only)
    """
    brand = crud.get_brand_by_name(db, name=brand_in.name)
    if brand:
        raise HTTPException(
            status_code=400,
            detail="A brand with this name already exists.",
        )
    brand = crud.create_brand(db=db, brand=brand_in)
    return brand

@router.get("/", response_model=List[schemas.Brand])
def get_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Get all brands"""
    brands = crud.get_brands(db, skip=skip, limit=limit)
    return brands

@router.get("/{brand_id}", response_model=schemas.Brand)
def get_brand(
    brand_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Get a specific brand"""
    brand = crud.get_brand(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.put("/{brand_id}", response_model=schemas.Brand)
def update_brand(
    brand_id: int,
    brand_update: schemas.BrandUpdate,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Update a brand"""
    brand = crud.update_brand(db, brand_id=brand_id, brand_update=brand_update)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.get("/{brand_id}/tickets", response_model=List[schemas.Ticket])
def read_brand_tickets(
    *,
    db: Session = Depends(get_db),
    brand_id: int,
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: models.User = Depends(deps.get_current_active_brand_user),
):
    """
    Get all tickets for a specific brand. (Brand Users and Admins only)
    Optionally filter by status (e.g., open, in-progress, etc.)
    """
    # Security check: ensure brand user is associated with this brand_id
    if current_user.role == models.RoleEnum.brand_user and current_user.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this brand's tickets")

    tickets = crud.get_tickets_by_brand(db, brand_id=brand_id, skip=skip, limit=limit, status=status)
    return tickets

# Team Invitation Endpoints
@router.post("/{brand_id}/invitations", response_model=schemas.TeamInvitationResponse)
def create_team_invitation(
    brand_id: int,
    invitation: schemas.TeamInvitationCreate,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Create a team invitation for a brand"""
    # Check if user belongs to the brand
    if current_user.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to invite team members for this brand")
    
    # Check if brand exists
    brand = crud.get_brand(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Generate invitation token
    invitation_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    
    # Create invitation
    db_invitation = crud.create_team_invitation(
        db=db,
        invitation=invitation,
        brand_id=brand_id,
        invited_by=current_user.id,
        invitation_token=invitation_token,
        expires_at=expires_at
    )
    
    # Send invitation email
    try:
        # Create invitation link
        base_url = settings.FRONTEND_URL  # Use the configurable frontend URL
        invitation_link = f"{base_url}/team-invitation/{invitation_token}"
        
        # Send email
        email_sent = send_team_invitation_email(
            invitee_email=invitation.email,
            inviter_name=current_user.full_name or "Team Member",
            brand_name=brand.name,
            role=invitation.role.value,
            invitation_link=invitation_link
        )
        
        if not email_sent:
            # Log warning but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send invitation email to {invitation.email}")
    
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending invitation email: {e}")
    
    return db_invitation

@router.get("/{brand_id}/invitations", response_model=List[schemas.TeamInvitationResponse])
def get_team_invitations(
    brand_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Get team invitations for a brand"""
    # Check if user belongs to the brand
    if current_user.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to view team invitations for this brand")
    
    invitations = crud.get_team_invitations_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)
    return invitations

@router.get("/{brand_id}/team-members", response_model=List[schemas.User])
def get_team_members(
    brand_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Get team members for a brand"""
    # Check if user belongs to the brand
    if current_user.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to view team members for this brand")
    
    team_members = crud.get_team_members_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)
    return team_members

@router.delete("/{brand_id}/invitations/{invitation_id}")
def delete_team_invitation(
    brand_id: int,
    invitation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Delete a team invitation"""
    # Check if user belongs to the brand
    if current_user.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete team invitations for this brand")
    
    success = crud.delete_team_invitation(db, invitation_id=invitation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    return {"message": "Invitation deleted successfully"}

@router.get("/invitations/{token}")
def get_invitation_by_token(
    token: str,
    db: Session = Depends(deps.get_db)
):
    """Get invitation details by token (public endpoint)"""
    invitation = crud.get_team_invitation_by_token(db, token=token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if invitation.is_accepted:
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation has expired")
    
    # Get brand details
    brand = crud.get_brand(db, brand_id=invitation.brand_id)
    
    return {
        "invitation_id": invitation.id,
        "email": invitation.email,
        "role": invitation.role,
        "brand_name": brand.name if brand else "Unknown Brand",
        "expires_at": invitation.expires_at
    }

@router.post("/invitations/{token}/accept")
def accept_team_invitation(
    token: str,
    user_data: schemas.TeamInvitationAccept,
    db: Session = Depends(deps.get_db)
):
    """Accept a team invitation (public endpoint)"""
    invitation = crud.get_team_invitation_by_token(db, token=token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if invitation.is_accepted:
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation has expired")
    
    # Accept invitation and create user
    user = crud.accept_team_invitation(db, invitation_id=invitation.id, user_data=user_data)
    
    return {
        "message": "Invitation accepted successfully",
        "user_id": user.id,
        "email": user.email
    }

@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """Delete a brand by ID (admin or brand manager only)"""
    # Only allow if admin or the brand manager (support_email matches current_user.email)
    brand = crud.get_brand(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if current_user.role != "admin" and (not brand.support_email or brand.support_email.lower() != current_user.email.lower()):
        raise HTTPException(status_code=403, detail="Not authorized to delete this brand")
    return crud.delete_brand(db, brand_id=brand_id)