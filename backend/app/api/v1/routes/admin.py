# backend/app/api/v1/routes/admin.py

from fastapi import APIRouter
from app.api.v1.endpoints import admin

router = APIRouter()

# Include all admin endpoints
router.include_router(admin.router) 