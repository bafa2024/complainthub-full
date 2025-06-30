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
from .api.v1.endpoints import users, login, tickets, brands, webhook, admin, chat, testing, tickets_extended
from .api.v1.routes import auth
from .database import engine, Base
from .config import settings
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

# CORS Middleware
try:
    origins = [
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS middleware configured successfully")
except Exception as e:
    logger.error(f"Failed to configure CORS middleware: {e}")

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

    app.include_router(api_router, prefix="/api/v1")
    logger.info("API routers configured successfully")
except Exception as e:
    logger.error(f"Failed to configure API routers: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

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
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["database"] = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["database"] = "disconnected"
            health_status["status"] = "degraded"
        
        # Check OpenAI configuration
        try:
            openai_key = settings.get_openai_api_key()
            health_status["openai"] = "configured" if openai_key else "not_configured"
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            health_status["openai"] = "error"
        
        return health_status
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {"status": "error", "message": "Health check failed"}

@app.get("/api/v1/test")
def test_endpoint():
    """Test endpoint with error handling"""
    try:
        return {"message": "API is working!", "path": "/api/v1/test"}
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        raise HTTPException(status_code=500, detail="Test endpoint failed")

@app.get("/register")
def user_registration_page():
    """Serve the user registration HTML page with error handling"""
    try:
        html_file_path = os.path.join(os.path.dirname(__file__), "..", "user_registration.html")
        if os.path.exists(html_file_path):
            return FileResponse(html_file_path, media_type="text/html")
        else:
            logger.error(f"Registration page not found at: {html_file_path}")
            return JSONResponse(
                status_code=404,
                content={"error": "Registration page not found"}
            )
    except Exception as e:
        logger.error(f"Error serving registration page: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to serve registration page"}
        )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event with error handling"""
    try:
        logger.info("Starting Complaint Management API...")
        logger.info(f"Project: {settings.PROJECT_NAME}")
        logger.info(f"API Version: {settings.API_V1_STR}")
        
        # Log configuration status
        if settings.get_openai_api_key():
            logger.info("OpenAI API key is configured")
        else:
            logger.warning("OpenAI API key is not configured - AI features will be limited")
            
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event with error handling"""
    try:
        logger.info("Shutting down Complaint Management API...")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}") 