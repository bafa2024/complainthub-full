# backend/app/api/v1/endpoints/phone_numbers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
<<<<<<< HEAD
from app.api.v1.deps import get_current_user, get_current_brand_user
=======
from app.api.v1.deps import get_current_user, get_current_active_brand_user
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
from app.database import get_db
from app.services.telephony import TelephonyService
from app.schemas import (
    AvailableNumber, NumberGenerationRequest, NumberGenerationResponse,
    PhoneNumber, PhoneNumberRequest, PhoneNumberRequestCreate,
<<<<<<< HEAD
    PhoneNumberUpdate, TelephonyProvider
=======
    PhoneNumberUpdate, TelephonyProvider, PhoneNumberRequestUpdate
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
)
from app.models import User, Brand, RoleEnum
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/providers", response_model=List[dict])
def get_telephony_providers(
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
):
    """Get available telephony providers"""
    try:
        telephony_service = TelephonyService(db)
        providers = telephony_service.get_available_providers()
        return providers
    except Exception as e:
        logger.error(f"Error getting telephony providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get telephony providers"
        )

@router.get("/search", response_model=List[AvailableNumber])
def search_available_numbers(
    country_code: str = "IN",
    number_type: str = "toll-free",
    capabilities: Optional[str] = None,
    provider: Optional[str] = None,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
):
    """Search for available phone numbers"""
    try:
        # Parse capabilities from comma-separated string
        capabilities_list = []
        if capabilities:
            capabilities_list = [cap.strip() for cap in capabilities.split(",")]
        else:
            capabilities_list = ["voice", "sms"]
        
        telephony_service = TelephonyService(db)
        available_numbers = telephony_service.search_available_numbers(
            country_code=country_code,
            number_type=number_type,
            capabilities=capabilities_list,
            provider=provider
        )
        
        return available_numbers
    except Exception as e:
        logger.error(f"Error searching available numbers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search available numbers"
        )

@router.post("/purchase", response_model=NumberGenerationResponse)
def purchase_phone_number(
    request: NumberGenerationRequest,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
):
    """Purchase a phone number"""
    try:
        # Get brand ID from current user
<<<<<<< HEAD
        if not current_user.brand_id:
=======
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        telephony_service = TelephonyService(db)
        
        # Search for available numbers
        available_numbers = telephony_service.search_available_numbers(
            country_code=request.country_code,
            number_type=request.number_type,
            capabilities=request.capabilities,
            provider=request.provider_preference
        )
        
        if not available_numbers:
            return NumberGenerationResponse(
                success=False,
                message="No available numbers found for the specified criteria"
            )
        
        # Select the first available number
        selected_number = available_numbers[0]
        
        # Purchase the number
        result = telephony_service.purchase_number(
            phone_number=selected_number.phone_number,
            provider=selected_number.provider,
<<<<<<< HEAD
            brand_id=current_user.brand_id,
=======
            brand_id=current_brand_user.brand_id,
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            capabilities=selected_number.capabilities
        )
        
        if result["success"]:
            return NumberGenerationResponse(
                success=True,
                phone_number=selected_number.phone_number,
                provider=selected_number.provider,
                cost=selected_number.monthly_cost,
                message="Phone number purchased successfully"
            )
        else:
            return NumberGenerationResponse(
                success=False,
                message=f"Failed to purchase number: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Error purchasing phone number: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purchase phone number"
        )

@router.get("/brand", response_model=List[PhoneNumber])
def get_brand_phone_numbers(
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
):
    """Get all phone numbers for the current brand"""
    try:
        if not current_user.brand_id:
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
):
    """Get all phone numbers for the current brand"""
    try:
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        telephony_service = TelephonyService(db)
<<<<<<< HEAD
        phone_numbers = telephony_service.get_brand_numbers(current_user.brand_id)
=======
        phone_numbers = telephony_service.get_brand_numbers(current_brand_user.brand_id)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
        return phone_numbers
    except Exception as e:
        logger.error(f"Error getting brand phone numbers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get brand phone numbers"
        )

@router.put("/{phone_number}/status", response_model=PhoneNumber)
def update_phone_number_status(
    phone_number: str,
    update_data: PhoneNumberUpdate,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
):
    """Update phone number status"""
    try:
        if not current_user.brand_id:
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
):
    """Update phone number status"""
    try:
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        # Find phone number and verify ownership
        from app.models import PhoneNumber as PhoneNumberModel
        db_phone_number = db.query(PhoneNumberModel).filter(
            PhoneNumberModel.phone_number == phone_number,
<<<<<<< HEAD
            PhoneNumberModel.brand_id == current_user.brand_id
=======
            PhoneNumberModel.brand_id == current_brand_user.brand_id
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
        ).first()
        
        if not db_phone_number:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found"
            )
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_phone_number, field, value)
        
        db.commit()
        db.refresh(db_phone_number)
        
        return db_phone_number
    except Exception as e:
        logger.error(f"Error updating phone number status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update phone number status"
        )

@router.delete("/{phone_number}")
def release_phone_number(
    phone_number: str,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
):
    """Release a phone number back to the provider"""
    try:
        if not current_user.brand_id:
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
):
    """Release a phone number back to the provider"""
    try:
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        telephony_service = TelephonyService(db)
        result = telephony_service.release_number(phone_number)
        
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    except Exception as e:
        logger.error(f"Error releasing phone number: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to release phone number"
        )

@router.post("/requests", response_model=PhoneNumberRequest)
def create_phone_number_request(
    request: PhoneNumberRequestCreate,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
):
    """Create a phone number request"""
    try:
        if not current_user.brand_id:
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
):
    """Create a phone number request"""
    try:
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        # Create phone number request
        from app.models import PhoneNumberRequest as PhoneNumberRequestModel
        db_request = PhoneNumberRequestModel(
<<<<<<< HEAD
            brand_id=current_user.brand_id,
            user_id=current_user.id,
=======
            brand_id=current_brand_user.brand_id,
            user_id=current_brand_user.id,
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            country_code=request.country_code,
            area_code=request.area_code,
            number_type=request.number_type,
            capabilities=request.capabilities,
            provider_preference=request.provider_preference
        )
        
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        
        return db_request
    except Exception as e:
        logger.error(f"Error creating phone number request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create phone number request"
        )

@router.get("/requests", response_model=List[PhoneNumberRequest])
def get_phone_number_requests(
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
):
    """Get all phone number requests for the current brand"""
    try:
        if not current_user.brand_id:
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
):
    """Get all phone number requests for the current brand"""
    try:
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        telephony_service = TelephonyService(db)
<<<<<<< HEAD
        requests = telephony_service.get_number_requests(current_user.brand_id)
=======
        requests = telephony_service.get_number_requests(current_brand_user.brand_id)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
        return requests
    except Exception as e:
        logger.error(f"Error getting phone number requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get phone number requests"
        )

@router.put("/requests/{request_id}", response_model=PhoneNumberRequest)
def update_phone_number_request(
    request_id: int,
    update_data: PhoneNumberRequestUpdate,
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
):
    """Update a phone number request (admin only)"""
    try:
        # Check if user is admin
<<<<<<< HEAD
        if current_user.role != RoleEnum.admin:
=======
        if current_brand_user.role != RoleEnum.admin:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update phone number requests"
            )
        
        # Find request
        from app.models import PhoneNumberRequest as PhoneNumberRequestModel
        db_request = db.query(PhoneNumberRequestModel).filter(
            PhoneNumberRequestModel.id == request_id
        ).first()
        
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number request not found"
            )
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_request, field, value)
        
        db.commit()
        db.refresh(db_request)
        
        return db_request
    except Exception as e:
        logger.error(f"Error updating phone number request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update phone number request"
        )

@router.get("/analytics")
def get_phone_number_analytics(
    db: Session = Depends(get_db),
<<<<<<< HEAD
    current_user: User = Depends(get_current_brand_user)
):
    """Get phone number analytics for the brand"""
    try:
        if not current_user.brand_id:
=======
    current_brand_user: User = Depends(get_current_active_brand_user)
):
    """Get phone number analytics for the brand"""
    try:
        if not current_brand_user.brand_id:
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a brand"
            )
        
        from app.models import PhoneNumber as PhoneNumberModel
        from sqlalchemy import func
        
        # Get phone number statistics
        total_numbers = db.query(func.count(PhoneNumberModel.id)).filter(
<<<<<<< HEAD
            PhoneNumberModel.brand_id == current_user.brand_id
        ).scalar()
        
        active_numbers = db.query(func.count(PhoneNumberModel.id)).filter(
            PhoneNumberModel.brand_id == current_user.brand_id,
=======
            PhoneNumberModel.brand_id == current_brand_user.brand_id
        ).scalar()
        
        active_numbers = db.query(func.count(PhoneNumberModel.id)).filter(
            PhoneNumberModel.brand_id == current_brand_user.brand_id,
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            PhoneNumberModel.status == "active"
        ).scalar()
        
        # Get monthly cost
        monthly_cost = db.query(func.sum(PhoneNumberModel.monthly_cost)).filter(
<<<<<<< HEAD
            PhoneNumberModel.brand_id == current_user.brand_id,
=======
            PhoneNumberModel.brand_id == current_brand_user.brand_id,
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            PhoneNumberModel.status == "active"
        ).scalar() or 0.0
        
        # Get numbers by provider
        provider_stats = db.query(
            PhoneNumberModel.provider,
            func.count(PhoneNumberModel.id)
        ).filter(
<<<<<<< HEAD
            PhoneNumberModel.brand_id == current_user.brand_id
=======
            PhoneNumberModel.brand_id == current_brand_user.brand_id
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
        ).group_by(PhoneNumberModel.provider).all()
        
        return {
            "total_numbers": total_numbers,
            "active_numbers": active_numbers,
            "inactive_numbers": total_numbers - active_numbers,
            "monthly_cost": monthly_cost,
            "provider_stats": [
                {"provider": provider, "count": count} 
                for provider, count in provider_stats
            ]
        }
    except Exception as e:
        logger.error(f"Error getting phone number analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get phone number analytics"
        ) 