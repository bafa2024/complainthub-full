from fastapi import APIRouter
from app.api.v1.endpoints import analytics

router = APIRouter()

# Include all analytics endpoints
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@router.get("/")
def analytics_dashboard():
    return {"message": "Analytics API is running", "endpoints": [
        "/analytics/overview - System overview analytics",
        "/analytics/brand/{brand_id} - Brand-specific analytics", 
        "/analytics/user/{user_id} - User-specific analytics",
        "/analytics/realtime - Real-time metrics",
        "/analytics/reports/{report_type} - Generate reports",
        "/analytics/predictive/{metric} - Predictive analytics",
        "/analytics/trends - Trend analysis",
        "/analytics/comparison - Metric comparison",
        "/analytics/export/{report_type} - Export reports",
        "/analytics/dashboard - Dashboard data",
        "/analytics/health - System health"
    ]}
