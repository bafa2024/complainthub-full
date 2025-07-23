#!/usr/bin/env python3

"""
Minimal test server for testing signup functionality only
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

# Import only what we need for signup
from app.database import get_db
from app.api.v1.routes.auth import router as auth_router

# Create a minimal FastAPI app
app = FastAPI(title="ComplaintHub Signup Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the auth router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "ComplaintHub Signup Test Server"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)