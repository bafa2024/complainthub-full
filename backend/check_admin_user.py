#!/usr/bin/env python3
"""
Check admin user details
"""

from app.database import SessionLocal
from app.models import User, RoleEnum
from app.core.security import verify_password

db = SessionLocal()

# Find all admin users
admin_users = db.query(User).filter(User.role == RoleEnum.admin).all()

print("Admin Users:")
print("=" * 50)

for user in admin_users:
    print(f"ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Full Name: {user.full_name}")
    print(f"Role: {user.role}")
    print(f"Is Active: {user.is_active}")
    print("-" * 30)

# Also check the user that was promoted
test_user = db.query(User).filter(User.email == "testbrand@example.com").first()
if test_user:
    print(f"\nTest User (testbrand@example.com):")
    print(f"ID: {test_user.id}")
    print(f"Email: {test_user.email}")
    print(f"Full Name: {test_user.full_name}")
    print(f"Role: {test_user.role}")
    print(f"Is Active: {test_user.is_active}")
    
    # Test some common passwords
    test_passwords = ["password123", "admin123", "test123", "password", "admin"]
    for pwd in test_passwords:
        if verify_password(pwd, test_user.hashed_password):
            print(f"✅ Password found: {pwd}")
            break
    else:
        print("❌ Password not found in common passwords")

db.close() 