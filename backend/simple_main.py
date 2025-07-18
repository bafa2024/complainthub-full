# Simple backend main file for testing

import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import sqlite3
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Brand Complaint Management System",
    description="API for managing brand complaints through an AI-driven system.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": str(exc),
            "message": "Please check your request data and try again."
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc)
        }
    )

def test_database():
    """Test database connectivity"""
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        conn.close()
        return {"status": "success", "result": result[0]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Complaint Management API", 
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    db_test = test_database()
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "database": db_test["status"],
        "timestamp": datetime.now().isoformat(),
        "message": "Backend is running successfully"
    }

@app.get("/test")
def test_endpoint():
    """Test endpoint for debugging"""
    return {
        "message": "Backend is running successfully!", 
        "timestamp": datetime.now().isoformat(),
        "path": "/test"
    }

# Testing endpoints (simplified versions of the complex ones)
@app.get("/api/v1/testing/")
def testing_dashboard():
    """Main testing dashboard"""
    return {
        "message": "Testing Dashboard",
        "description": "Simplified testing endpoints for development",
        "endpoints": {
            "health_check": "/health",
            "test_endpoint": "/test",
            "database_test": "/api/v1/testing/database",
            "crud_test": "/api/v1/testing/crud",
            "mock_data_test": "/api/v1/testing/mock-data"
        },
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/testing/health")
def testing_health():
    """Testing infrastructure health check"""
    return {
        "status": "healthy",
        "testing_infrastructure": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/testing/database")
def test_database_endpoint():
    """Test database operations"""
    results = {
        "database_connection": "unknown",
        "basic_operations": "unknown",
        "errors": []
    }
    
    try:
        # Test in-memory SQLite
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        results["database_connection"] = "success"
        
        # Test insert
        cursor.execute('''
            INSERT INTO test_table (name, email) VALUES (?, ?)
        ''', ('Test User', 'test@example.com'))
        
        # Test select
        cursor.execute('SELECT COUNT(*) FROM test_table')
        count = cursor.fetchone()[0]
        
        # Test update
        cursor.execute('''
            UPDATE test_table SET name = ? WHERE email = ?
        ''', ('Updated User', 'test@example.com'))
        
        # Test delete
        cursor.execute('DELETE FROM test_table WHERE email = ?', ('test@example.com',))
        
        conn.commit()
        conn.close()
        
        results["basic_operations"] = f"success - processed {count} record(s)"
        
    except Exception as e:
        results["errors"].append(f"Database test failed: {str(e)}")
        results["basic_operations"] = "failed"
    
    return results

@app.get("/api/v1/testing/crud")
def test_crud_operations():
    """Test CRUD operations"""
    results = {
        "create": "unknown",
        "read": "unknown", 
        "update": "unknown",
        "delete": "unknown",
        "errors": []
    }
    
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE crud_test (
                id INTEGER PRIMARY KEY,
                data TEXT,
                created_at TEXT
            )
        ''')
        
        # CREATE
        cursor.execute('''
            INSERT INTO crud_test (data, created_at) VALUES (?, ?)
        ''', ('test data', datetime.now().isoformat()))
        
        test_id = cursor.lastrowid
        results["create"] = f"success - ID: {test_id}"
        
        # READ
        cursor.execute('SELECT * FROM crud_test WHERE id = ?', (test_id,))
        record = cursor.fetchone()
        results["read"] = "success" if record else "failed"
        
        # UPDATE
        cursor.execute('''
            UPDATE crud_test SET data = ? WHERE id = ?
        ''', ('updated test data', test_id))
        results["update"] = "success"
        
        # DELETE
        cursor.execute('DELETE FROM crud_test WHERE id = ?', (test_id,))
        results["delete"] = "success"
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        results["errors"].append(f"CRUD test failed: {str(e)}")
    
    return results

@app.get("/api/v1/testing/mock-data")
def test_mock_data():
    """Test mock data generation"""
    results = {
        "mock_users_created": 0,
        "mock_data_operations": "unknown",
        "data_validation": {},
        "errors": []
    }
    
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE mock_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                created_at TEXT
            )
        ''')
        
        # Create mock data
        mock_users = [
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com'),
            ('Bob Johnson', 'bob@example.com')
        ]
        
        for name, email in mock_users:
            cursor.execute('''
                INSERT INTO mock_users (name, email, created_at) VALUES (?, ?, ?)
            ''', (name, email, datetime.now().isoformat()))
        
        results["mock_users_created"] = len(mock_users)
        
        # Validate data
        cursor.execute('SELECT COUNT(*) FROM mock_users')
        total_count = cursor.fetchone()[0]
        
        results["data_validation"] = {
            "total_records": total_count,
            "expected_records": len(mock_users),
            "validation_status": "pass" if total_count == len(mock_users) else "fail"
        }
        
        results["mock_data_operations"] = "success"
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        results["errors"].append(f"Mock data test failed: {str(e)}")
        results["mock_data_operations"] = "failed"
    
    return results

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Simplified Complaint Management API...")
    logger.info("All endpoints are active and ready for testing")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Simplified API...")

if __name__ == "__main__":
    import uvicorn
    print("Starting ComplaintHub Backend Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press CTRL+C to stop the server")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)