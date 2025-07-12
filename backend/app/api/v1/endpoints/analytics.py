# backend/app/api/v1/endpoints/analytics.py

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.services.analytics import AnalyticsService
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_system_overview(
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get comprehensive system overview analytics
    """
    try:
        analytics_service = AnalyticsService(db)
        overview = analytics_service.get_system_overview(date_range)
        
        if not overview:
            raise HTTPException(status_code=500, detail="Failed to generate analytics overview")
        
        return {
            "status": "success",
            "data": overview,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system overview")

@router.get("/brand/{brand_id}")
async def get_brand_analytics(
    brand_id: int,
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get detailed analytics for a specific brand
    """
    try:
        # Check if user has access to this brand
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand's analytics")
        
        analytics_service = AnalyticsService(db)
        brand_analytics = analytics_service.get_brand_analytics(brand_id, date_range)
        
        if not brand_analytics:
            raise HTTPException(status_code=404, detail="Brand analytics not found")
        
        return {
            "status": "success",
            "data": brand_analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting brand analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get brand analytics")

@router.get("/user/{user_id}")
async def get_user_analytics(
    user_id: int,
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get analytics for a specific user
    """
    try:
        # Check if user has access to this user's data
        if current_user.get("role") != "admin" and current_user.get("id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this user's analytics")
        
        analytics_service = AnalyticsService(db)
        user_analytics = analytics_service.get_user_analytics(user_id, date_range)
        
        if not user_analytics:
            raise HTTPException(status_code=404, detail="User analytics not found")
        
        return {
            "status": "success",
            "data": user_analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user analytics")

@router.get("/realtime")
async def get_real_time_metrics(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get real-time metrics for dashboard
    """
    try:
        analytics_service = AnalyticsService(db)
        real_time_metrics = analytics_service.get_real_time_metrics()
        
        return {
            "status": "success",
            "data": real_time_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get real-time metrics")

@router.post("/reports/{report_type}")
async def generate_report(
    report_type: str,
    filters: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Generate comprehensive reports
    """
    try:
        # Validate report type
        valid_report_types = ["performance", "trends", "financial", "customer_satisfaction", "channel_analysis"]
        if report_type not in valid_report_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid report type. Must be one of: {', '.join(valid_report_types)}"
            )
        
        analytics_service = AnalyticsService(db)
        report = analytics_service.generate_report(report_type, filters)
        
        if not report:
            raise HTTPException(status_code=500, detail="Failed to generate report")
        
        return {
            "status": "success",
            "data": report,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating report {report_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/predictive/{metric}")
async def get_predictive_analytics(
    metric: str,
    days: int = Query(30, description="Number of days to predict", ge=1, le=365),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get predictive analytics for forecasting
    """
    try:
        # Validate metric
        valid_metrics = ["ticket_volume", "resolution_time", "satisfaction"]
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid metric. Must be one of: {', '.join(valid_metrics)}"
            )
        
        analytics_service = AnalyticsService(db)
        predictions = analytics_service.get_predictive_analytics(metric, days)
        
        if not predictions:
            raise HTTPException(status_code=500, detail="Failed to generate predictions")
        
        return {
            "status": "success",
            "data": predictions,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting predictive analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get predictive analytics")

@router.get("/trends")
async def get_trends(
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    metric: str = Query("tickets", description="Metric to analyze: tickets, satisfaction, resolution_time"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get trend analysis for various metrics
    """
    try:
        analytics_service = AnalyticsService(db)
        
        if metric == "tickets":
            trends = analytics_service._calculate_trends(date_range)
        elif metric == "satisfaction":
            start_date = analytics_service._get_start_date(date_range)
            trends = analytics_service._get_sentiment_metrics(start_date)
        elif metric == "resolution_time":
            start_date = analytics_service._get_start_date(date_range)
            trends = analytics_service._calculate_resolution_metrics(start_date)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid metric. Must be one of: tickets, satisfaction, resolution_time"
            )
        
        return {
            "status": "success",
            "data": trends,
            "metric": metric,
            "date_range": date_range,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trends")

@router.get("/comparison")
async def compare_metrics(
    metric: str = Query("resolution_rate", description="Metric to compare"),
    period1: str = Query("7d", description="First period"),
    period2: str = Query("30d", description="Second period"),
    brand_id: Optional[int] = Query(None, description="Brand ID for comparison"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Compare metrics between two time periods
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get data for both periods
        if brand_id:
            data1 = analytics_service.get_brand_analytics(brand_id, period1)
            data2 = analytics_service.get_brand_analytics(brand_id, period2)
        else:
            data1 = analytics_service.get_system_overview(period1)
            data2 = analytics_service.get_system_overview(period2)
        
        # Calculate comparison
        comparison = _calculate_comparison(data1, data2, metric)
        
        return {
            "status": "success",
            "data": {
                "metric": metric,
                "period1": period1,
                "period2": period2,
                "comparison": comparison,
                "period1_data": data1,
                "period2_data": data2
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare metrics")

@router.get("/export/{report_type}")
async def export_report(
    report_type: str,
    format: str = Query("json", description="Export format: json, csv, pdf"),
    filters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Export analytics report in various formats
    """
    try:
        # Validate format
        valid_formats = ["json", "csv", "pdf"]
        if format not in valid_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
            )
        
        analytics_service = AnalyticsService(db)
        report = analytics_service.generate_report(report_type, filters)
        
        if not report:
            raise HTTPException(status_code=500, detail="Failed to generate report for export")
        
        # Format the export
        if format == "json":
            return {
                "status": "success",
                "data": report,
                "format": format,
                "generated_at": datetime.utcnow().isoformat()
            }
        elif format == "csv":
            # Convert to CSV format
            csv_data = _convert_to_csv(report)
            return {
                "status": "success",
                "data": csv_data,
                "format": format,
                "filename": f"{report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                "generated_at": datetime.utcnow().isoformat()
            }
        elif format == "pdf":
            # Convert to PDF format (would require additional libraries)
            return {
                "status": "success",
                "message": "PDF export not yet implemented",
                "format": format,
                "generated_at": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail="Failed to export report")

@router.get("/dashboard")
async def get_dashboard_data(
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get comprehensive dashboard data
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get all dashboard data
        overview = analytics_service.get_system_overview(date_range)
        real_time = analytics_service.get_real_time_metrics()
        
        # Get brand-specific data if user is not admin
        brand_data = None
        if current_user.get("role") != "admin" and current_user.get("brand_id"):
            brand_data = analytics_service.get_brand_analytics(current_user["brand_id"], date_range)
        
        dashboard_data = {
            "overview": overview,
            "real_time": real_time,
            "brand_data": brand_data,
            "user_role": current_user.get("role"),
            "date_range": date_range
        }
        
        return {
            "status": "success",
            "data": dashboard_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/health")
async def get_analytics_health(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get analytics system health
    """
    try:
        analytics_service = AnalyticsService(db)
        health = analytics_service._get_system_health()
        
        return {
            "status": "success",
            "data": health,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics health")

def _calculate_comparison(data1: Dict[str, Any], data2: Dict[str, Any], metric: str) -> Dict[str, Any]:
    """Calculate comparison between two datasets"""
    try:
        # Extract metric values
        value1 = _extract_metric_value(data1, metric)
        value2 = _extract_metric_value(data2, metric)
        
        if value1 is None or value2 is None:
            return {"error": "Metric not found in data"}
        
        # Calculate change
        if value1 == 0:
            change_percent = 100 if value2 > 0 else 0
        else:
            change_percent = ((value2 - value1) / value1) * 100
        
        return {
            "period1_value": value1,
            "period2_value": value2,
            "change": value2 - value1,
            "change_percent": round(change_percent, 2),
            "trend": "increasing" if change_percent > 0 else "decreasing" if change_percent < 0 else "stable"
        }
        
    except Exception as e:
        logger.error(f"Error calculating comparison: {e}")
        return {"error": "Failed to calculate comparison"}

def _extract_metric_value(data: Dict[str, Any], metric: str) -> Optional[float]:
    """Extract metric value from data structure"""
    try:
        if metric == "resolution_rate":
            return data.get("overview", {}).get("resolution_rate", 0)
        elif metric == "total_tickets":
            return data.get("overview", {}).get("total_tickets", 0)
        elif metric == "avg_satisfaction":
            return data.get("overview", {}).get("avg_satisfaction", 0)
        elif metric == "avg_resolution_time":
            return data.get("overview", {}).get("avg_resolution_time", 0)
        else:
            # Try to find metric in nested structure
            for key, value in data.items():
                if isinstance(value, dict):
                    if metric in value:
                        return value[metric]
            return None
            
    except Exception as e:
        logger.error(f"Error extracting metric value: {e}")
        return None

def _convert_to_csv(data: Dict[str, Any]) -> str:
    """Convert report data to CSV format"""
    try:
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Metric", "Value", "Generated At"])
        
        # Flatten the data structure
        flattened_data = _flatten_dict(data)
        
        # Write data rows
        for key, value in flattened_data.items():
            writer.writerow([key, value, datetime.utcnow().isoformat()])
        
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error converting to CSV: {e}")
        return "Error converting data to CSV"

def _flatten_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested dictionary for CSV export"""
    flattened = {}
    
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            flattened.update(_flatten_dict(value, new_key))
        elif isinstance(value, list):
            flattened[new_key] = str(value)
        else:
            flattened[new_key] = value
    
    return flattened 