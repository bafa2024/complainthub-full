#!/usr/bin/env python3
"""
Setup test brand user with brand assignment
"""

from app.database import SessionLocal
from app.models import User, Brand
from app.core.security import get_password_hash

def setup_test_brand_user():
    print("🔧 Setting up test brand user...")
    
    db = SessionLocal()
    
    try:
        # Check if test brand user exists
        test_user = db.query(User).filter(User.email == "testbrand@example.com").first()
        
        if not test_user:
            print("Creating test brand user...")
            test_user = User(
                email="testbrand@example.com",
                hashed_password=get_password_hash("testpass123"),
                full_name="Test Brand User",
                role="brand_user",
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("✅ Test brand user created")
        else:
            print("✅ Test brand user already exists")
        
        # Check if test brand exists
        test_brand = db.query(Brand).filter(Brand.name == "Test Brand").first()
        
        if not test_brand:
            print("Creating test brand...")
            test_brand = Brand(
                name="Test Brand",
                support_email="support@testbrand.com",
                industry="Technology",
                credit_balance=100.0
            )
            db.add(test_brand)
            db.commit()
            db.refresh(test_brand)
            print("✅ Test brand created")
        else:
            print("✅ Test brand already exists")
        
        # Assign brand to user
        if test_user.brand_id != test_brand.id:
            print(f"Assigning brand {test_brand.id} to user {test_user.id}...")
            test_user.brand_id = test_brand.id
            db.commit()
            print("✅ Brand assigned to user")
        else:
            print("✅ User already has brand assigned")
        
        # Verify setup
        print(f"\n📋 Setup Summary:")
        print(f"   User: {test_user.email} (ID: {test_user.id})")
        print(f"   Brand: {test_brand.name} (ID: {test_brand.id})")
        print(f"   User's Brand ID: {test_user.brand_id}")
        print(f"   Login credentials: testbrand@example.com / testpass123")
        
    except Exception as e:
        print(f"❌ Error setting up test brand user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_brand_user() 