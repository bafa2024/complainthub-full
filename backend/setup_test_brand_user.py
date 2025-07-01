#!/usr/bin/env python3
"""
Setup test brand user for testing ticket access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Brand, RoleEnum, Ticket
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def setup_test_brand_user():
    """Setup a test brand user"""
    db = SessionLocal()
    try:
        print("🔧 Setting up test brand user...")
        print("=" * 50)
        
        # Get the first brand
        brand = db.query(Brand).first()
        if not brand:
            print("❌ No brands found in database!")
            return
        
        print(f"Using brand: {brand.name} (ID: {brand.id})")
        
        # Check if test brand user already exists
        existing_user = db.query(User).filter(User.email == "testbrand@example.com").first()
        if existing_user:
            print(f"✅ Test brand user already exists: {existing_user.email}")
            print(f"   User ID: {existing_user.id}")
            print(f"   Brand ID: {existing_user.brand_id}")
            print(f"   Role: {existing_user.role}")
            return existing_user
        
        # Create test brand user
        test_user = User(
            email="testbrand@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Brand User",
            role=RoleEnum.brand_user,
            brand_id=brand.id,
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Test brand user created successfully!")
        print(f"   Email: {test_user.email}")
        print(f"   Password: password123")
        print(f"   User ID: {test_user.id}")
        print(f"   Brand ID: {test_user.brand_id}")
        print(f"   Role: {test_user.role}")
        
        # Get tickets for this brand
        brand_tickets = db.query(Ticket).filter(Ticket.brand_id == brand.id).all()
        print(f"\n📋 Tickets for this brand: {len(brand_tickets)}")
        for ticket in brand_tickets:
            print(f"   - Ticket ID: {ticket.id}, Title: {ticket.title}, Status: {ticket.status}")
        
        return test_user
        
    except Exception as e:
        print(f"❌ Error setting up test brand user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_brand_user() 