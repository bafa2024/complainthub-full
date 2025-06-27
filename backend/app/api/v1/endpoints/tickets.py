# backend/app/api/v1/endpoints/tickets.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
    if current_user.role == models.RoleEnum.admin:
        tickets = crud.get_tickets(db, skip=skip, limit=limit)
    elif current_user.role == models.RoleEnum.brand_user:
        tickets = crud.get_tickets_by_brand(db, brand_id=current_user.brand_id, skip=skip, limit=limit)
    else:
        tickets = crud.get_tickets_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
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
    ticket = crud.get_ticket(db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == models.RoleEnum.brand_user and ticket.brand_id != current_user.brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")

    ticket = crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_in)
    return ticket