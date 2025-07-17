import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    print("\n=== Testing User Registration ===")
    
    # Test data
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "phone_number": "+1234567890"
    }
    
    # 1. Test user registration endpoint
    print("\n1. Testing user registration endpoint...")
    try:
        response = client.post(
            "/api/v1/users/",
            json=user_data
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 2. Test login with the registered user
    print("\n2. Testing login with registered user...")
    try:
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"],
            "grant_type": "password"
        }
        response = client.post("/api/v1/login/access-token", data=login_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_register_user()
