# backend/app/tasks/seo_tasks.py

import logging
from datetime import datetime, timedelta
from celery import current_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.seo_indexing_service import SEOIndexingService
from app.celery_app import celery_app
from typing import Optional

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.seo_tasks.generate_static_pages_task")
def generate_static_pages_task(self, limit: int = 100):
    """
    Background task to generate static pages for multiple tickets
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting bulk static page generation for {limit} tickets")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating", "limit": limit}
        )
        
        # Generate static pages
        seo_service = SEOIndexingService(db)
        result = seo_service.bulk_generate_static_pages(limit)
        
        # Update task status
        current_task.update_state(
            state="SUCCESS" if result["success"] else "FAILURE",
            meta={
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Bulk static page generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk static page generation: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.seo_tasks.generate_single_static_page_task")
def generate_single_static_page_task(self, ticket_id: int):
    """
    Background task to generate static page for a single ticket
    """
    db = SessionLocal()
    try:
        logger.info(f"Generating static page for ticket {ticket_id}")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"ticket_id": ticket_id, "status": "generating"}
        )
        
        # Generate static page
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_static_page(ticket_id)
        
        # Update task status
        current_task.update_state(
            state="SUCCESS" if result["success"] else "FAILURE",
            meta={
                "ticket_id": ticket_id,
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Static page generation for ticket {ticket_id} completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating static page for ticket {ticket_id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "ticket_id": ticket_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.seo_tasks.cleanup_old_pages_task")
def cleanup_old_pages_task(self, days: int = 365):
    """
    Background task to cleanup old static pages
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting cleanup of static pages older than {days} days")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "cleaning", "days": days}
        )
        
        # Cleanup old pages
        seo_service = SEOIndexingService(db)
        result = seo_service.cleanup_old_pages(days)
        
        # Update task status
        current_task.update_state(
            state="SUCCESS" if result["success"] else "FAILURE",
            meta={
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Static page cleanup completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in static page cleanup: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.seo_tasks.generate_sitemap_task")
def generate_sitemap_task(self, include_private: bool = False):
    """
    Background task to generate sitemap
    """
    db = SessionLocal()
    try:
        logger.info("Generating sitemap")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating_sitemap"}
        )
        
        # Generate sitemap
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_sitemap(include_private)
        
        # Update task status
        current_task.update_state(
            state="SUCCESS" if result["success"] else "FAILURE",
            meta={
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Sitemap generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.seo_tasks.generate_robots_task")
def generate_robots_task(self):
    """
    Background task to generate robots.txt
    """
    db = SessionLocal()
    try:
        logger.info("Generating robots.txt")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating_robots"}
        )
        
        # Generate robots.txt
        seo_service = SEOIndexingService(db)
        result = seo_service.generate_robots_txt()
        
        # Update task status
        current_task.update_state(
            state="SUCCESS" if result["success"] else "FAILURE",
            meta={
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Robots.txt generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating robots.txt: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(name="app.tasks.seo_tasks.auto_generate_static_pages")
def auto_generate_static_pages():
    """
    Automatically generate static pages for new public tickets
    """
    db = SessionLocal()
    try:
        logger.info("Auto-generating static pages for new public tickets")
        
        # Find tickets that need static pages
        from app.models import Ticket
        
        tickets_needing_pages = db.query(Ticket).filter(
            Ticket.is_public == True,
            Ticket.transcript.isnot(None),
            Ticket.deleted_at.is_(None)
        ).all()
        
        seo_service = SEOIndexingService(db)
        generated_count = 0
        failed_count = 0
        
        for ticket in tickets_needing_pages:
            try:
                result = seo_service.generate_static_page(ticket.id)
                if result["success"]:
                    generated_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"Failed to generate static page for ticket {ticket.id}: {result['error']}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Error generating static page for ticket {ticket.id}: {e}")
        
        # Generate sitemap after creating pages
        sitemap_result = seo_service.generate_sitemap()
        
        return {
            "success": True,
            "generated_count": generated_count,
            "failed_count": failed_count,
            "total_processed": len(tickets_needing_pages),
            "sitemap_generated": sitemap_result["success"]
        }
        
    except Exception as e:
        logger.error(f"Error in auto static page generation: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.seo_tasks.update_seo_analytics")
def update_seo_analytics():
    """
    Update SEO analytics and generate reports
    """
    db = SessionLocal()
    try:
        logger.info("Updating SEO analytics")
        
        seo_service = SEOIndexingService(db)
        analytics = seo_service.get_seo_analytics()
        
        if analytics["success"]:
            # Store analytics in database or cache
            # This could be extended to store analytics in a dedicated table
            logger.info(f"SEO analytics updated: {analytics['analytics']}")
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error updating SEO analytics: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.seo_tasks.optimize_seo_content")
def optimize_seo_content():
    """
    Optimize existing SEO content based on analytics
    """
    db = SessionLocal()
    try:
        logger.info("Optimizing SEO content")
        
        # Get tickets with poor SEO performance
        from app.models import Ticket
        
        # This is a placeholder for SEO optimization logic
        # In a real implementation, you would analyze page performance
        # and update content accordingly
        
        tickets_to_optimize = db.query(Ticket).filter(
            Ticket.is_public == True,
            Ticket.transcript.isnot(None),
            Ticket.deleted_at.is_(None)
        ).limit(50).all()  # Process in batches
        
        optimized_count = 0
        
        for ticket in tickets_to_optimize:
            try:
                # Regenerate SEO content with optimizations
                seo_service = SEOIndexingService(db)
                result = seo_service.generate_seo_content_from_transcription(ticket.id)
                
                if result["success"]:
                    # Update ticket with optimized content
                    # This could involve updating meta tags, descriptions, etc.
                    optimized_count += 1
                    
            except Exception as e:
                logger.error(f"Error optimizing SEO content for ticket {ticket.id}: {e}")
        
        return {
            "success": True,
            "optimized_count": optimized_count,
            "total_processed": len(tickets_to_optimize)
        }
        
    except Exception as e:
        logger.error(f"Error in SEO content optimization: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close() 