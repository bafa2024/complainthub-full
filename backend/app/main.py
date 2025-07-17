# backend/app/main.py

import logging
import traceback
import sys
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .api.v1.endpoints import (
    login, users, brands, tickets, webhook, admin, chat, testing,
    tickets_extended, channels, analytics, billing, ai_management,
    compliance, security, phone_numbers, followup
)
<<<<<<< HEAD
=======
from .api.v1.endpoints.webhook import router as webhook_router
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
from .api.v1.routes import auth
from .database import engine, Base
from .config.settings import settings
from .middleware.security import AuditMiddleware, SecurityMiddleware, RateLimitMiddleware
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize database with error handling
try:
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

app = FastAPI(
    title="Brand Complaint Management System",
    description="API for managing brand complaints through an AI-driven system.",
    version="1.0.0",
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors from Pydantic"""
    try:
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": str(exc),
                "message": "Please check your request data and try again."
            }
        )
    except Exception as e:
        logger.error(f"Error in validation exception handler: {e}")
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error occurred"}
        )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    try:
        logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP error",
                "status_code": exc.status_code,
                "message": str(exc.detail)
            }
        )
    except Exception as e:
        logger.error(f"Error in HTTP exception handler: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all other exceptions"""
    try:
        logger.error(f"Unhandled exception: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "details": str(exc) if settings.PROJECT_NAME == "Development" else "Contact support for assistance."
            }
        )
    except Exception as e:
        logger.error(f"Error in general exception handler: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Critical error occurred"}
        )

<<<<<<< HEAD
# Add CORS middleware
app.add_middleware(CORSMiddleware, allowed_origins=["*"])
=======
# Add security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
app.add_middleware(AuditMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS)
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925

# API Routers with error handling
try:
    api_router = APIRouter() 
    api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
    api_router.include_router(login.router, prefix="/login", tags=["login"])
    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
    api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
    api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
    api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
    api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
    api_router.include_router(testing.router, prefix="/testing", tags=["testing"])
    api_router.include_router(tickets_extended.router, prefix="/tickets_extended", tags=["tickets_extended"])
    api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
    api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
    api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
    api_router.include_router(ai_management.router, prefix="/ai", tags=["ai-management"])
    api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
    api_router.include_router(security.router, prefix="/security", tags=["security"])
    api_router.include_router(phone_numbers.router, prefix="/phone-numbers", tags=["phone-numbers"])
    api_router.include_router(followup.router, prefix="/followup", tags=["followup"])

    app.include_router(api_router, prefix="/api/v1")
    logger.info("API routers configured successfully")
except Exception as e:
    logger.error(f"Failed to configure API routers: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

# Include webhook routes
app.include_router(webhook_router, prefix="/api/v1/webhook", tags=["webhooks"])

@app.get("/")
def read_root():
    """Root endpoint with error handling"""
    try:
        return {"message": "Welcome to the Complaint Management API"}
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health_check():
    """Health check endpoint with comprehensive status"""
    try:
        health_status = {
            "status": "healthy",
            "api_version": "1.0.0",
            "database": "unknown",
            "openai": "unknown",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Check database connection
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["database"] = "disconnected"
            health_status["status"] = "degraded"
        
        # Check OpenAI configuration
        try:
            openai_key = settings.OPENAI_API_KEY
            health_status["openai"] = "configured" if openai_key else "not_configured"
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            health_status["openai"] = "error"
        
        return health_status
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {"status": "error", "message": "Health check failed"}

@app.get("/test")
def test_endpoint():
    """Test endpoint for debugging"""
    return {"message": "Backend is running successfully!"}

@app.get("/register")
def user_registration_page():
    """Serve user registration page"""
    try:
        return FileResponse("user_registration.html")
    except Exception as e:
        logger.error(f"Error serving registration page: {e}")
        raise HTTPException(status_code=404, detail="Registration page not found")

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    try:
<<<<<<< HEAD
        logger.info("Application starting up...")
        # Initialize any startup tasks here
        logger.info("Application startup completed")
=======
        logger.info("Starting Complaint Management API...")
        logger.info(f"Project: {settings.PROJECT_NAME}")
        logger.info(f"API Version: {settings.API_V1_STR}")
        
        # Log configuration status
        if settings.OPENAI_API_KEY:
            logger.info("OpenAI API key is configured")
        else:
            logger.warning("OpenAI API key is not configured - AI features will be limited")
            
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    try:
        logger.info("Application shutting down...")
        # Cleanup tasks here
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 