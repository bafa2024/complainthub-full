# backend/app/api/v1/endpoints/crm.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Query, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.api.v1 import deps
from app.models import Brand, CRMIntegration
from app.schemas import (
    CRMIntegrationCreate, 
    CRMIntegrationUpdate, 
    CRMIntegrationResponse,
    CRMSyncRequest,
    CRMSyncResponse
)
from app.services.integrations.crm import CRMService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/integrations", response_model=CRMIntegrationResponse)
async def create_crm_integration(
    integration: CRMIntegrationCreate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Create a new CRM integration for a brand
    """
    try:
        # Verify brand ownership
        brand = db.query(Brand).filter(Brand.id == integration.brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        if current_user.get("role") != "admin" and brand.owner_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized to manage this brand")
        
        # Test CRM connection
        crm_service = CRMService(db)
        test_config = {
            "crm_type": integration.crm_type,
            "api_key": integration.api_key,
            "base_url": integration.base_url
        }
        
        # Create integration record
        db_integration = CRMIntegration(
            crm_type=integration.crm_type,
            api_key=integration.api_key,
            base_url=integration.base_url,
            webhook_url=integration.webhook_url,
            webhook_secret=integration.webhook_secret,
            brand_id=integration.brand_id,
            is_active=integration.is_active,
            sync_direction=integration.sync_direction,
            auto_sync=integration.auto_sync
        )
        
        db.add(db_integration)
        db.commit()
        db.refresh(db_integration)
        
        return CRMIntegrationResponse.from_orm(db_integration)
        
    except Exception as e:
        logger.error(f"Error creating CRM integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integrations", response_model=List[CRMIntegrationResponse])
async def get_crm_integrations(
    brand_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get CRM integrations for brands
    """
    try:
        query = db.query(CRMIntegration)
        
        if brand_id:
            query = query.filter(CRMIntegration.brand_id == brand_id)
        
        if current_user.get("role") != "admin":
            # Filter by user's brands
            user_brands = db.query(Brand).filter(Brand.owner_id == current_user.get("id")).all()
            brand_ids = [brand.id for brand in user_brands]
            query = query.filter(CRMIntegration.brand_id.in_(brand_ids))
        
        integrations = query.all()
        return [CRMIntegrationResponse.from_orm(integration) for integration in integrations]
        
    except Exception as e:
        logger.error(f"Error getting CRM integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integrations/{integration_id}", response_model=CRMIntegrationResponse)
async def get_crm_integration(
    integration_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get specific CRM integration details
    """
    try:
        integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
        if not integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        # Check authorization
        if current_user.get("role") != "admin":
            brand = db.query(Brand).filter(Brand.id == integration.brand_id).first()
            if not brand or brand.owner_id != current_user.get("id"):
                raise HTTPException(status_code=403, detail="Not authorized")
        
        return CRMIntegrationResponse.from_orm(integration)
        
    except Exception as e:
        logger.error(f"Error getting CRM integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/integrations/{integration_id}", response_model=CRMIntegrationResponse)
async def update_crm_integration(
    integration_id: int,
    integration_update: CRMIntegrationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Update CRM integration configuration
    """
    try:
        integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
        if not integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        # Check authorization
        if current_user.get("role") != "admin":
            brand = db.query(Brand).filter(Brand.id == integration.brand_id).first()
            if not brand or brand.owner_id != current_user.get("id"):
                raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update fields
        update_data = integration_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(integration, field, value)
        
        db.commit()
        db.refresh(integration)
        
        return CRMIntegrationResponse.from_orm(integration)
        
    except Exception as e:
        logger.error(f"Error updating CRM integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/integrations/{integration_id}")
async def delete_crm_integration(
    integration_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Delete CRM integration
    """
    try:
        integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
        if not integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        # Check authorization
        if current_user.get("role") != "admin":
            brand = db.query(Brand).filter(Brand.id == integration.brand_id).first()
            if not brand or brand.owner_id != current_user.get("id"):
                raise HTTPException(status_code=403, detail="Not authorized")
        
        db.delete(integration)
        db.commit()
        
        return {"message": "CRM integration deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting CRM integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/{integration_id}/sync", response_model=CRMSyncResponse)
async def sync_crm_integration(
    integration_id: int,
    sync_request: CRMSyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Manually trigger CRM sync
    """
    try:
        integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
        if not integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        # Check authorization
        if current_user.get("role") != "admin":
            brand = db.query(Brand).filter(Brand.id == integration.brand_id).first()
            if not brand or brand.owner_id != current_user.get("id"):
                raise HTTPException(status_code=403, detail="Not authorized")
        
        # Perform sync
        crm_service = CRMService(db)
        config = {
            "crm_type": integration.crm_type,
            "api_key": integration.api_key,
            "base_url": integration.base_url
        }
        
        if sync_request.sync_direction in ["inbound", "bidirectional"]:
            result = crm_service.sync_from_crm(config)
            if not result.get("success"):
                return CRMSyncResponse(
                    success=False,
                    message="Sync failed",
                    errors=[result.get("error", "Unknown error")]
                )
        
        return CRMSyncResponse(
            success=True,
            message="Sync completed successfully",
            synced_tickets=result.get("synced_count", 0)
        )
        
    except Exception as e:
        logger.error(f"Error syncing CRM integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/{crm_type}")
async def handle_crm_webhook(
    crm_type: str,
    request: Request,
    brand_id: int = Query(..., description="Brand ID for the webhook"),
    db: Session = Depends(deps.get_db)
):
    """
    Handle incoming webhooks from CRM systems for real-time updates
    """
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        # Get webhook signature for verification
        signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Signature')
        
        # Verify webhook signature if provided
        if signature:
            # Get brand's CRM configuration for webhook secret
            crm_integration = db.query(CRMIntegration).filter(
                CRMIntegration.brand_id == brand_id,
                CRMIntegration.crm_type == crm_type,
                CRMIntegration.is_active == True
            ).first()
            
            if crm_integration and crm_integration.webhook_secret:
                webhook_body = await request.body()
                if not crm_service.verify_webhook_signature(
                    webhook_body.decode(), 
                    signature.replace('sha256=', ''), 
                    crm_integration.webhook_secret
                ):
                    raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process webhook
        crm_service = CRMService(db)
        result = crm_service.handle_crm_webhook(crm_type, webhook_data, brand_id)
        
        if not result["success"]:
            logger.error(f"CRM webhook processing failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"CRM webhook processed successfully for {crm_type}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CRM webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")

@router.post("/webhook/{crm_type}/verify")
async def verify_crm_webhook(
    crm_type: str,
    request: Request,
    brand_id: int = Query(..., description="Brand ID for the webhook"),
    db: Session = Depends(deps.get_db)
):
    """
    Verify webhook endpoint for CRM systems (e.g., Facebook verification)
    """
    try:
        # Handle verification challenge
        if crm_type == 'facebook':
            # Facebook webhook verification
            mode = request.query_params.get('hub.mode')
            token = request.query_params.get('hub.verify_token')
            challenge = request.query_params.get('hub.challenge')
            
            if mode == 'subscribe' and token:
                # Verify token matches brand's webhook secret
                crm_integration = db.query(CRMIntegration).filter(
                    CRMIntegration.brand_id == brand_id,
                    CRMIntegration.crm_type == crm_type,
                    CRMIntegration.is_active == True
                ).first()
                
                if crm_integration and crm_integration.webhook_secret == token:
                    return Response(content=challenge, media_type="text/plain")
                else:
                    raise HTTPException(status_code=403, detail="Invalid verify token")
        
        elif crm_type == 'salesforce':
            # Salesforce webhook verification
            challenge = request.query_params.get('challenge')
            if challenge:
                return Response(content=challenge, media_type="text/plain")
        
        elif crm_type == 'zoho':
            # Zoho webhook verification
            challenge = request.query_params.get('challenge')
            if challenge:
                return Response(content=challenge, media_type="text/plain")
        
        # Default verification response
        return {"status": "verified"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying CRM webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify webhook")

@router.get("/webhook/{crm_type}/status")
async def get_webhook_status(
    crm_type: str,
    brand_id: int = Query(..., description="Brand ID"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get webhook status and configuration for a CRM integration
    """
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        crm_integration = db.query(CRMIntegration).filter(
            CRMIntegration.brand_id == brand_id,
            CRMIntegration.crm_type == crm_type
        ).first()
        
        if not crm_integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        return {
            "crm_type": crm_type,
            "brand_id": brand_id,
            "is_active": crm_integration.is_active,
            "webhook_url": f"/api/v1/crm/webhook/{crm_type}?brand_id={brand_id}",
            "verification_url": f"/api/v1/crm/webhook/{crm_type}/verify?brand_id={brand_id}",
            "last_sync": crm_integration.last_sync_at.isoformat() if crm_integration.last_sync_at else None,
            "sync_count": crm_integration.sync_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook status")

@router.get("/supported-crms")
async def get_supported_crms():
    """
    Get list of supported CRM systems
    """
    supported_crms = [
        {
            "id": "salesforce",
            "name": "Salesforce Service Cloud",
            "description": "Enterprise CRM with advanced case management",
            "features": ["Case Management", "Contact Management", "Analytics"],
            "api_docs": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/"
        },
        {
            "id": "zoho",
            "name": "Zoho Desk",
            "description": "Cloud-based customer service platform",
            "features": ["Ticket Management", "Multi-channel Support", "Automation"],
            "api_docs": "https://www.zoho.com/desk/developer-guide/"
        },
        {
            "id": "freshworks",
            "name": "Freshdesk",
            "description": "Modern customer support software",
            "features": ["Ticket Management", "Team Collaboration", "Integrations"],
            "api_docs": "https://developers.freshdesk.com/api/"
        },
        {
            "id": "kapture",
            "name": "Kapture CRM",
            "description": "Indian CRM platform for customer engagement",
            "features": ["Lead Management", "Customer Support", "Analytics"],
            "api_docs": "https://kapturecrm.com/api-documentation/"
        },
        {
            "id": "leadsquared",
            "name": "LeadSquared",
            "description": "Sales automation and CRM platform",
            "features": ["Lead Management", "Sales Automation", "Marketing"],
            "api_docs": "https://developers.leadsquared.com/"
        },
        {
            "id": "hubspot",
            "name": "HubSpot CRM",
            "description": "All-in-one CRM platform",
            "features": ["Contact Management", "Deal Tracking", "Marketing"],
            "api_docs": "https://developers.hubspot.com/docs/api"
        },
        {
            "id": "pipedrive",
            "name": "Pipedrive",
            "description": "Sales CRM focused on deal management",
            "features": ["Deal Management", "Sales Pipeline", "Reporting"],
            "api_docs": "https://developers.pipedrive.com/docs/api/v1"
        }
    ]
    
    return {"supported_crms": supported_crms} 