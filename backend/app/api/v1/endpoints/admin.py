# backend/app/api/v1/endpoints/admin.py

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api.v1.deps import get_db, get_current_user
from app.services.analytics import AnalyticsService
from app.services.admin import AdminService
from app.models import User, Brand, Ticket, SystemSettings
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get system overview statistics
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        analytics_service = AnalyticsService(db)
        stats = analytics_service.get_system_overview("30d")
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system stats")

@router.get("/settings")
async def get_system_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get system settings
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        settings = admin_service.get_system_settings()
        
        return {
            "status": "success",
            "data": settings
        }
    except Exception as e:
        logger.error(f"Error getting system settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system settings")

@router.put("/settings")
async def update_system_settings(
    settings: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update system settings
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.update_system_settings(settings)
        
        return {
            "status": "success",
            "message": "System settings updated successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error updating system settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system settings")

@router.post("/test-connection/{service}")
async def test_connection(
    service: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Test external service connection
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.test_connection(service)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/restart-system")
async def restart_system(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Restart system services
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.restart_system()
        
        return {
            "status": "success",
            "message": "System restart initiated",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error restarting system: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart system")

@router.get("/reports/complaints")
async def get_complaints_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get complaints report
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        report = admin_service.get_complaints_report(start_date, end_date)
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Error getting complaints report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get complaints report")

@router.get("/reports/brands")
async def get_brands_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get brands report
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        report = admin_service.get_brands_report(start_date, end_date)
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Error getting brands report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get brands report")

@router.get("/reports/users")
async def get_users_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get users report
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        report = admin_service.get_users_report(start_date, end_date)
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Error getting users report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users report")

@router.get("/reports/revenue")
async def get_revenue_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get revenue report
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        report = admin_service.get_revenue_report(start_date, end_date)
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Error getting revenue report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue report")

@router.post("/reports/generate/{report_type}")
async def generate_report(
    report_type: str,
    format: str = Query("pdf", description="Export format: pdf, csv, json"),
    filters: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and export report
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.generate_report(report_type, format, filters or {})
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/dashboard")
async def get_dashboard_data(
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive dashboard data
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        analytics_service = AnalyticsService(db)
        admin_service = AdminService(db)
        
        # Get all dashboard data
        overview = analytics_service.get_system_overview(date_range)
        real_time = analytics_service.get_real_time_metrics()
        recent_activity = admin_service.get_recent_activity()
        system_health = admin_service.get_system_health()
        top_brands = admin_service.get_top_brands()
        
        dashboard_data = {
            "overview": overview,
            "realTime": real_time,
            "recentActivity": recent_activity,
            "systemHealth": system_health,
            "topBrands": top_brands
        }
        
        return {
            "status": "success",
            "data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get system health status
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        health = admin_service.get_system_health()
        
        return {
            "status": "success",
            "data": health
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")

@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, description="Number of activities to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get recent system activity
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        activity = admin_service.get_recent_activity(limit)
        
        return {
            "status": "success",
            "data": activity
        }
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent activity")

@router.get("/top-brands")
async def get_top_brands(
    limit: int = Query(10, description="Number of brands to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get top performing brands
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        brands = admin_service.get_top_brands(limit)
        
        return {
            "status": "success",
            "data": brands
        }
    except Exception as e:
        logger.error(f"Error getting top brands: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top brands")

@router.post("/backup")
async def create_backup(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create system backup
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.create_backup()
        
        return {
            "status": "success",
            "message": "Backup created successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create backup")

@router.get("/backups")
async def list_backups(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List available backups
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        backups = admin_service.list_backups()
        
        return {
            "status": "success",
            "data": backups
        }
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        raise HTTPException(status_code=500, detail="Failed to list backups")

@router.post("/backup/{backup_id}/restore")
async def restore_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Restore from backup
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.restore_backup(backup_id)
        
        return {
            "status": "success",
            "message": "Backup restored successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore backup")

@router.delete("/backup/{backup_id}")
async def delete_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete backup
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_service = AdminService(db)
        result = admin_service.delete_backup(backup_id)
        
        return {
            "status": "success",
            "message": "Backup deleted successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error deleting backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete backup")