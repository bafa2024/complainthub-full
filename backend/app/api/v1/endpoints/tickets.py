# backend/app/api/v1/endpoints/tickets.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import traceback
from datetime import datetime, timedelta
from sqlalchemy import or_

from app import crud, models, schemas
from app.api.v1 import deps # CORRECTED IMPORT PATH
from app.database import get_db

router = APIRouter()

@router.get("/public", response_model=List[schemas.Ticket])
def read_public_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    tickets = crud.get_public_tickets(db, skip=skip, limit=limit)
    return tickets

@router.post("/", response_model=schemas.Ticket)
def create_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_in: schemas.TicketCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    ticket = crud.create_ticket(db=db, ticket=ticket_in, owner_id=current_user.id)
    return ticket

@router.get("/", response_model=List[schemas.Ticket])
def read_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    print(f"Fetching tickets for user: {current_user.id}, role: {current_user.role}")
    
    if current_user.role == models.RoleEnum.admin:
        tickets = crud.get_tickets(db, skip=skip, limit=limit)
        print(f"Admin: Found {len(tickets)} tickets")
    elif current_user.role == models.RoleEnum.brand_user:
        tickets = crud.get_tickets_by_brand(db, brand_id=current_user.brand_id, skip=skip, limit=limit)
        print(f"Brand user: Found {len(tickets)} tickets for brand {current_user.brand_id}")
    else:
        tickets = crud.get_tickets_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
        print(f"Regular user: Found {len(tickets)} tickets for user {current_user.id}")
    
    return tickets

@router.get("/{ticket_id}", response_model=schemas.Ticket)
def read_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    ticket = crud.get_ticket(db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    is_owner = ticket.owner_id == current_user.id
    is_brand_user = current_user.role == models.RoleEnum.brand_user and ticket.brand_id == current_user.brand_id
    is_admin = current_user.role == models.RoleEnum.admin
    
    if not (is_owner or is_brand_user or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    return ticket

@router.patch("/{ticket_id}", response_model=schemas.Ticket)
def update_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    ticket_in: schemas.TicketUpdate,
    current_user: models.User = Depends(deps.get_current_active_brand_user),
):
    """Update a ticket"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Update ticket request - Ticket ID: {ticket_id}, User ID: {current_user.id}, User Role: {current_user.role}")
    logger.info(f"Update data: {ticket_in.dict()}")
    
    ticket = crud.get_ticket(db, ticket_id=ticket_id)
    if not ticket:
        logger.error(f"Ticket not found - Ticket ID: {ticket_id}")
        raise HTTPException(status_code=404, detail="Ticket not found")

    logger.info(f"Found ticket - Brand ID: {ticket.brand_id}, Owner ID: {ticket.owner_id}")

    if current_user.role == models.RoleEnum.brand_user and ticket.brand_id != current_user.brand_id:
        logger.error(f"Authorization failed - User brand ID: {current_user.brand_id}, Ticket brand ID: {ticket.brand_id}")
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")

    logger.info("Authorization successful, updating ticket...")
    
    try:
        updated_ticket = crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_in)
        logger.info(f"Ticket updated successfully - New status: {updated_ticket.status}")
        return updated_ticket
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to update ticket: {str(e)}")

@router.get("/{ticket_id}/timeline")
def get_ticket_timeline(
    ticket_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get ticket timeline events"""
    try:
        ticket = crud.get_ticket(db, ticket_id=ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check permissions
        if current_user.role == models.RoleEnum.brand_user and ticket.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        elif current_user.role == models.RoleEnum.user and ticket.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate timeline events
        timeline = []
        
        # Ticket creation
        timeline.append({
            "id": 1,
            "event_type": "created",
            "title": "Complaint Submitted",
            "description": f"Complaint submitted via {ticket.channel}",
            "timestamp": ticket.created_at,
            "user_id": ticket.owner_id
        })
        
        # Status changes
        if ticket.status != "new":
            timeline.append({
                "id": 2,
                "event_type": "status_change",
                "title": f"Status Changed to {ticket.status.replace('-', ' ').title()}",
                "description": f"Ticket status updated to {ticket.status}",
                "timestamp": ticket.updated_at or ticket.created_at,
                "user_id": ticket.assignee_id
            })
        
        # Assignment
        if ticket.assignee_id:
            assignee = db.query(models.User).filter(models.User.id == ticket.assignee_id).first()
            timeline.append({
                "id": 3,
                "event_type": "assigned",
                "title": "Assigned to Support Team",
                "description": f"Assigned to {assignee.full_name if assignee else 'Support Team'}",
                "timestamp": ticket.updated_at or ticket.created_at,
                "user_id": ticket.assignee_id
            })
        
        # Resolution
        if ticket.status == "resolved" and ticket.resolved_at:
            timeline.append({
                "id": 4,
                "event_type": "resolved",
                "title": "Complaint Resolved",
                "description": "Complaint has been resolved",
                "timestamp": ticket.resolved_at,
                "user_id": ticket.assignee_id
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return {"timeline": timeline}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeline for ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch timeline")

@router.get("/filter/advanced")
def filter_tickets_advanced(
    status: Optional[str] = None,
    brand_id: Optional[int] = None,
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    days_open_min: Optional[int] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Advanced ticket filtering"""
    try:
        # Build query based on user role
        if current_user.role == models.RoleEnum.admin:
            query = db.query(models.Ticket)
        elif current_user.role == models.RoleEnum.brand_user:
            query = db.query(models.Ticket).filter(models.Ticket.brand_id == current_user.brand_id)
        else:
            query = db.query(models.Ticket).filter(models.Ticket.owner_id == current_user.id)
        
        # Apply filters
        if status:
            query = query.filter(models.Ticket.status == status)
        
        if brand_id:
            query = query.filter(models.Ticket.brand_id == brand_id)
        
        if category:
            query = query.filter(models.Ticket.category == category)
        
        if urgency:
            query = query.filter(models.Ticket.urgency == urgency)
        
        if date_from:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(models.Ticket.created_at >= from_date)
        
        if date_to:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(models.Ticket.created_at <= to_date)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Ticket.title.ilike(search_term),
                    models.Ticket.description.ilike(search_term)
                )
            )
        
        if days_open_min:
            cutoff_date = datetime.utcnow() - timedelta(days=days_open_min)
            query = query.filter(models.Ticket.created_at <= cutoff_date)
        
        # Apply sorting
        if sort_by == "created_at":
            order_column = models.Ticket.created_at
        elif sort_by == "updated_at":
            order_column = models.Ticket.updated_at
        elif sort_by == "status":
            order_column = models.Ticket.status
        elif sort_by == "urgency":
            order_column = models.Ticket.urgency
        else:
            order_column = models.Ticket.created_at
        
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        tickets = query.offset(skip).limit(limit).all()
        
        return {
            "tickets": tickets,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error filtering tickets: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter tickets")

@router.get("/stats/summary")
def get_ticket_stats_summary(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get ticket statistics summary"""
    try:
        # Build base query based on user role
        if current_user.role == models.RoleEnum.admin:
            base_query = db.query(models.Ticket)
        elif current_user.role == models.RoleEnum.brand_user:
            base_query = db.query(models.Ticket).filter(models.Ticket.brand_id == current_user.brand_id)
        else:
            base_query = db.query(models.Ticket).filter(models.Ticket.owner_id == current_user.id)
        
        # Get counts by status
        status_counts = {}
        for status in ["new", "in-progress", "resolved", "closed"]:
            count = base_query.filter(models.Ticket.status == status).count()
            status_counts[status] = count
        
        # Get total count
        total = base_query.count()
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = base_query.filter(models.Ticket.created_at >= week_ago).count()
        
        # Get average resolution time
        resolved_tickets = base_query.filter(
            models.Ticket.status == "resolved",
            models.Ticket.resolved_at.isnot(None)
        ).all()
        
        avg_resolution_time = None
        if resolved_tickets:
            total_time = sum([
                (t.resolved_at - t.created_at).total_seconds() / 3600  # hours
                for t in resolved_tickets
            ])
            avg_resolution_time = total_time / len(resolved_tickets)
        
        return {
            "total_tickets": total,
            "status_counts": status_counts,
            "recent_tickets": recent_count,
            "avg_resolution_time_hours": round(avg_resolution_time, 2) if avg_resolution_time else None,
            "resolution_rate": (status_counts.get("resolved", 0) / total * 100) if total > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting ticket stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")