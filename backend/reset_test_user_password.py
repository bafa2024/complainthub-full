#!/usr/bin/env python3
"""
Reset test user password
"""

from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

def reset_test_user_password():
    print("🔧 Resetting test user password...")
    
    db = SessionLocal()
    
    try:
        # Find the test user
        test_user = db.query(User).filter(User.email == "testbrand@example.com").first()
        
        if not test_user:
            print("❌ Test user not found!")
            return
        
        print(f"Found user: {test_user.email} (ID: {test_user.id})")
        print(f"Current role: {test_user.role}")
        print(f"Current brand_id: {test_user.brand_id}")
        
        # Reset password
        new_password = "testpass123"
        test_user.hashed_password = get_password_hash(new_password)
        test_user.is_active = True
        test_user.role = "brand_user"
        
        db.commit()
        
        print(f"✅ Password reset successfully!")
        print(f"   Email: {test_user.email}")
        print(f"   Password: {new_password}")
        print(f"   Role: {test_user.role}")
        print(f"   Brand ID: {test_user.brand_id}")
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_test_user_password() 