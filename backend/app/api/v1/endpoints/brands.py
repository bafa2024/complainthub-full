# backend/app/api/v1/endpoints/brands.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.v1 import deps # CORRECTED IMPORT PATH
from app.database import get_db # CORRECT IMPORT

router = APIRouter()

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
def read_brands(
    db: Session = Depends(get_db), # This will now work
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve all brands.
    """
    brands = crud.get_brands(db, skip=skip, limit=limit)
    return brands

@router.get("/{brand_id}", response_model=schemas.Brand)
def read_brand(
    *,
    db: Session = Depends(get_db), # This will now work
    brand_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get brand by ID.
    """
    brand = crud.get_brand(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.get("/{brand_id}/tickets", response_model=List[schemas.Ticket])
def read_brand_tickets(
    *,
    db: Session = Depends(get_db), # This will now work
    brand_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_brand_user),
):
    """
    Get all tickets for a specific brand. (Brand Users and Admins only)
    """
    # Security check: ensure brand user is associated with this brand_id
    if current_user.role == models.RoleEnum.brand_user and current_user.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this brand's tickets")

    tickets = crud.get_tickets_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)
    return tickets