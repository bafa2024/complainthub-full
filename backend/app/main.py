# backend/app/main.py

from fastapi import FastAPI, APIRouter # Import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import users, login, tickets, brands, webhook, admin
from app.database import engine, Base

# This will create the tables in the database if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Brand Complaint Management System",
    description="API for managing brand complaints through an AI-driven system.",
    version="1.0.0",
)

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:5173", # Default Vite dev server port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
# Use APIRouter, not FastAPI, for the sub-router
api_router = APIRouter() 
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])


app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Complaint Management API"}