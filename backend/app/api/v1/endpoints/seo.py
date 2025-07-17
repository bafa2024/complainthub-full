# backend/app/api/v1/endpoints/seo.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.api.v1 import deps
from app.models import User, Ticket, Brand
from app.services.seo_indexing_service import SEOIndexingService
from app.tasks.seo_tasks import generate_static_pages_task, cleanup_old_pages_task
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate/{ticket_id}")
async def generate_static_page(
    ticket_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate static HTML page for a specific ticket
    """
    try:
        # Check permissions
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        if current_user.role.value == "brand_user" and ticket.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate static page
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_static_page(ticket_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating static page: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate static page")

@router.post("/generate-seo-content/{ticket_id}")
async def generate_seo_content(
    ticket_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate SEO content from voice transcription
    """
    try:
        # Check permissions
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        if current_user.role.value == "brand_user" and ticket.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate SEO content
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_seo_content_from_transcription(ticket_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SEO content: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SEO content")

@router.post("/bulk-generate")
async def bulk_generate_static_pages(
    limit: int = 100,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Bulk generate static pages for multiple tickets
    """
    try:
        # Check if user is admin or brand user
        if current_user.role.value not in ["admin", "brand_user"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Start background task
        background_tasks.add_task(generate_static_pages_task, limit)
        
        return {
            "success": True,
            "message": f"Bulk generation started for up to {limit} tickets",
            "task_id": f"bulk_generate_{datetime.utcnow().timestamp()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start bulk generation")

@router.post("/generate-sitemap")
async def generate_sitemap(
    include_private: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate XML sitemap
    """
    try:
        # Check permissions
        if current_user.role.value not in ["admin", "brand_user"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate sitemap
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_sitemap(include_private)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate sitemap")

@router.post("/generate-robots")
async def generate_robots_txt(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate robots.txt file
    """
    try:
        # Check permissions
        if current_user.role.value not in ["admin", "brand_user"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate robots.txt
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_robots_txt()
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating robots.txt: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate robots.txt")

@router.post("/cleanup")
async def cleanup_old_pages(
    days: int = 365,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Clean up old static pages
    """
    try:
        # Check permissions
        if current_user.role.value not in ["admin", "brand_user"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Start background task
        background_tasks.add_task(cleanup_old_pages_task, days)
        
        return {
            "success": True,
            "message": f"Cleanup started for pages older than {days} days",
            "task_id": f"cleanup_{datetime.utcnow().timestamp()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting cleanup: {e}")
        raise HTTPException(status_code=500, detail="Failed to start cleanup")

@router.get("/analytics")
async def get_seo_analytics(
    brand_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get SEO analytics
    """
    try:
        # Check permissions
        if current_user.role.value == "brand_user":
            brand_id = current_user.brand_id
        elif current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get analytics
        seo_service = SEOIndexingService(db)
        result = seo_service.get_seo_analytics(brand_id, days)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SEO analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SEO analytics")

@router.get("/public-complaints")
async def get_public_complaints_for_seo(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    brand_id: Optional[int] = None,
    db: Session = Depends(deps.get_db)
):
    """
    Get public complaints for SEO indexing (no authentication required)
    """
    try:
        query = db.query(Ticket).filter(
            Ticket.is_public == True,
            Ticket.transcript.isnot(None),
            Ticket.deleted_at.is_(None)
        )
        
        if category:
            query = query.filter(Ticket.category == category)
        
        if brand_id:
            query = query.filter(Ticket.brand_id == brand_id)
        
        tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
        
        # Format for SEO
        public_complaints = []
        for ticket in tickets:
            complaint = {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "transcript": ticket.transcript,
                "category": ticket.category.value,
                "urgency": ticket.urgency.value,
                "status": ticket.status.value,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                "brand": {
                    "id": ticket.brand.id,
                    "name": ticket.brand.name,
                    "industry": ticket.brand.industry
                } if ticket.brand else None,
                "url": f"/complaint/{ticket.id}"
            }
            public_complaints.append(complaint)
        
        return {
            "success": True,
            "complaints": public_complaints,
            "total": len(public_complaints),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting public complaints: {e}")
        raise HTTPException(status_code=500, detail="Failed to get public complaints")

@router.get("/sitemap.xml")
async def get_sitemap_xml(db: Session = Depends(deps.get_db)):
    """
    Serve sitemap.xml (no authentication required)
    """
    try:
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        sitemap_path = Path("static_pages/sitemap.xml")
        if sitemap_path.exists():
            return FileResponse(sitemap_path, media_type="application/xml")
        else:
            # Generate sitemap if it doesn't exist
            seo_service = SEOIndexingService(db)
            result = seo_service.generate_sitemap()
            if result["success"]:
                return FileResponse(sitemap_path, media_type="application/xml")
            else:
                raise HTTPException(status_code=500, detail="Failed to generate sitemap")
        
    except Exception as e:
        logger.error(f"Error serving sitemap: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve sitemap")

@router.get("/robots.txt")
async def get_robots_txt(db: Session = Depends(deps.get_db)):
    """
    Serve robots.txt (no authentication required)
    """
    try:
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        robots_path = Path("static_pages/robots.txt")
        if robots_path.exists():
            return FileResponse(robots_path, media_type="text/plain")
        else:
            # Generate robots.txt if it doesn't exist
            seo_service = SEOIndexingService(db)
            result = seo_service.generate_robots_txt()
            if result["success"]:
                return FileResponse(robots_path, media_type="text/plain")
            else:
                raise HTTPException(status_code=500, detail="Failed to generate robots.txt")
        
    except Exception as e:
        logger.error(f"Error serving robots.txt: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve robots.txt") 