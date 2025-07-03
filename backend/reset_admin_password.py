#!/usr/bin/env python3
"""
Reset admin password
"""

from app.database import SessionLocal
from app.models import User, RoleEnum
from app.core.security import get_password_hash

db = SessionLocal()

# Find admin user
admin_user = db.query(User).filter(User.email == "admin@complainthub.com").first()

if admin_user:
    # Reset password to admin123
    admin_user.hashed_password = get_password_hash("admin123")
    db.commit()
    print("✅ Admin password reset to 'admin123'")
else:
    print("❌ Admin user not found")

db.close() 