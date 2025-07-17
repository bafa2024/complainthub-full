import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal, engine
from app import models, crud, schemas

# Create test client
client = TestClient(app)

def test_register_user():
    # Test data
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "phone_number": "+1234567890"
    }
    
    # 1. Test successful user registration
    print("\n=== Testing User Registration ===")
    print("1. Testing successful user registration...")
    
    try:
        # First, delete the test user if it exists
        db = SessionLocal()
        existing_user = crud.get_user_by_email(db, email=user_data["email"])
        if existing_user:
            crud.delete_user(db, user_id=existing_user.id)
        
        # Create user
        user_create = schemas.UserCreate(**user_data)
        created_user = crud.create_user(db, user=user_create)
        print(f"✅ User created successfully with ID: {created_user.id}")
        
        # 2. Test duplicate email registration
        print("\n2. Testing duplicate email registration...")
        try:
            duplicate_user = crud.create_user(db, user=user_create)
            print("❌ Test failed: Should not allow duplicate emails")
        except Exception as e:
            if "already exists" in str(e.detail):
                print("✅ Duplicate email test passed")
            else:
                print(f"❌ Unexpected error: {e}")
        
        # 3. Test login with new user
        print("\n3. Testing login with new user...")
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"],
            "grant_type": "password"
        }
        response = client.post("/api/v1/login/access-token", data=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
            print(f"   Access token: {response.json()['access_token'][:30]}...")
        else:
            print(f"❌ Login failed: {response.text}")
        
        # Clean up
        crud.delete_user(db, user_id=created_user.id)
        print("\n✅ Test completed. Test user cleaned up.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_register_user()
