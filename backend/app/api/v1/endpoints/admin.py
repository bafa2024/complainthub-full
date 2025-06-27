# backend/app/api/v1/endpoints/admin.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.v1 import deps # CORRECTED IMPORT PATH
from app.database import get_db # CORRECT IMPORT

router = APIRouter()

@router.get("/users", response_model=List[schemas.User])
def read_all_users(
    db: Session = Depends(get_db), # This will now work
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
):
    """
    Retrieve all users in the system. (Admins only)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/brands", response_model=List[schemas.Brand])
def read_all_brands(
    db: Session = Depends(get_db), # This will now work
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
):
    """
    Retrieve all brands in the system. (Admins only)
    """
    brands = crud.get_brands(db, skip=skip, limit=limit)
    return brands
    
@router.put("/brands/{brand_id}", response_model=schemas.Brand)
def update_brand_details(
    *,
    db: Session = Depends(get_db), # This will now work
    brand_id: int,
    brand_in: schemas.BrandUpdate,
    current_user: models.User = Depends(deps.get_current_active_admin),
):
    """
    Update brand details. (Admins only)
    """
    brand = crud.get_brand(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=404,
            detail="The brand with this ID does not exist in the system",
        )
    brand = crud.update_brand(db=db, brand_id=brand_id, brand_update=brand_in)
    return brand