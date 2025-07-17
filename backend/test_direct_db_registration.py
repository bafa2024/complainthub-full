import time
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy import text

def test_direct_registration():
    """Test user registration directly in database"""
    print("\n🧪 DIRECT DATABASE USER REGISTRATION TEST")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test database connection
        result = db.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Generate test user data
        timestamp = str(int(time.time()))
        email = f"test_user_{timestamp}@example.com"
        password = "SecurePassword123!"
        
        print(f"\n📝 Creating user: {email}")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user object
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=f"Test User {timestamp}",
            phone_number=f"+1234567{timestamp[-4:]}",
            role="user",
            is_active=True
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("✅ User created successfully!")
        print(f"   ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Role: {new_user.role}")
        print(f"   Active: {new_user.is_active}")
        
        # Verify user exists
        verify_user = db.query(User).filter(User.email == email).first()
        if verify_user:
            print("\n✅ User verified in database")
        else:
            print("\n❌ User not found in database after creation")
            
        # Test duplicate prevention
        print(f"\n📝 Testing duplicate prevention...")
        try:
            duplicate_user = User(
                email=email,
                hashed_password=hashed_password,
                full_name="Duplicate User",
                phone_number="+9999999999",
                role="user"
            )
            db.add(duplicate_user)
            db.commit()
            print("❌ Duplicate was not prevented!")
        except Exception as e:
            print("✅ Duplicate correctly prevented")
            print(f"   Error: {type(e).__name__}")
            db.rollback()
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()
        print("\n📊 Test completed")

if __name__ == "__main__":
    test_direct_registration() 