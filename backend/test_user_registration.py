import pytest
import requests
import json
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class TestUserRegistration:
    """Comprehensive test suite for user registration functionality"""
    
    def setup_method(self):
        """Setup method that runs before each test"""
        self.session = requests.Session()
        self.test_users = []
    
    def teardown_method(self):
        """Cleanup method that runs after each test"""
        # Clean up test users if needed
        for user_data in self.test_users:
            try:
                # Try to delete test user if it was created
                if 'access_token' in user_data:
                    headers = {"Authorization": f"Bearer {user_data['access_token']}"}
                    self.session.delete(f"{API_BASE}/users/me", headers=headers)
            except:
                pass
    
    def generate_unique_email(self) -> str:
        """Generate a unique email for testing"""
        timestamp = int(time.time())
        return f"test_user_{timestamp}@example.com"
    
    def test_successful_user_registration(self):
        """Test successful user registration with valid data"""
        print("\n=== Testing Successful User Registration ===")
        
        # Test data
        signup_data = {
            "email": self.generate_unique_email(),
            "password": "TestPassword123!",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "role": "user"
        }
        
        print(f"Attempting to register user: {signup_data['email']}")
        
        # Make registration request
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration Status Code: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        # Assertions
        assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
        
        response_data = response.json()
        assert "id" in response_data, "Response should contain user ID"
        assert response_data["email"] == signup_data["email"], "Email should match"
        assert response_data["full_name"] == signup_data["full_name"], "Full name should match"
        assert response_data["phone_number"] == signup_data["phone_number"], "Phone number should match"
        assert response_data["role"] == signup_data["role"], "Role should match"
        assert response_data["is_active"] == True, "User should be active by default"
        
        print("✓ User registration successful!")
        
        # Store for cleanup
        self.test_users.append(signup_data)
    
    def test_successful_brand_user_registration(self):
        """Test successful brand user registration with brand creation"""
        print("\n=== Testing Brand User Registration ===")
        
        # Test data
        signup_data = {
            "email": self.generate_unique_email(),
            "password": "BrandPassword123!",
            "full_name": "Brand Manager",
            "phone_number": "9876543210",
            "role": "brand_user",
            "brand_name": f"Test Brand {int(time.time())}"
        }
        
        print(f"Attempting to register brand user: {signup_data['email']}")
        print(f"Brand name: {signup_data['brand_name']}")
        
        # Make registration request
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration Status Code: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        # Assertions
        assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
        
        response_data = response.json()
        assert "id" in response_data, "Response should contain user ID"
        assert response_data["email"] == signup_data["email"], "Email should match"
        assert response_data["full_name"] == signup_data["full_name"], "Full name should match"
        assert response_data["role"] == "brand_user", "Role should be brand_user"
        assert response_data["brand_id"] is not None, "Brand ID should be assigned"
        
        print("✓ Brand user registration successful!")
        
        # Store for cleanup
        self.test_users.append(signup_data)
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email should fail"""
        print("\n=== Testing Duplicate Email Registration ===")
        
        # First user registration
        email = self.generate_unique_email()
        signup_data_1 = {
            "email": email,
            "password": "Password123!",
            "full_name": "First User",
            "phone_number": "1111111111",
            "role": "user"
        }
        
        print(f"Registering first user: {email}")
        response_1 = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_1,
            headers={"Content-Type": "application/json"}
        )
        
        assert response_1.status_code == 201, "First registration should succeed"
        
        # Second user with same email
        signup_data_2 = {
            "email": email,
            "password": "DifferentPassword123!",
            "full_name": "Second User",
            "phone_number": "2222222222",
            "role": "user"
        }
        
        print(f"Attempting to register second user with same email: {email}")
        response_2 = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_2,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Second Registration Status Code: {response_2.status_code}")
        print(f"Second Registration Response: {response_2.text}")
        
        # Assertions
        assert response_2.status_code == 400, f"Expected 400 for duplicate email, got {response_2.status_code}"
        
        response_data = response_2.json()
        assert "detail" in response_data, "Error response should contain detail"
        assert "already exists" in response_data["detail"].lower(), "Error should mention duplicate email"
        
        print("✓ Duplicate email registration correctly rejected!")
        
        # Store for cleanup
        self.test_users.append(signup_data_1)
    
    def test_duplicate_brand_name_registration(self):
        """Test brand user registration with duplicate brand name should fail"""
        print("\n=== Testing Duplicate Brand Name Registration ===")
        
        brand_name = f"Duplicate Brand {int(time.time())}"
        
        # First brand user registration
        signup_data_1 = {
            "email": self.generate_unique_email(),
            "password": "Password123!",
            "full_name": "First Brand User",
            "phone_number": "1111111111",
            "role": "brand_user",
            "brand_name": brand_name
        }
        
        print(f"Registering first brand user with brand: {brand_name}")
        response_1 = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_1,
            headers={"Content-Type": "application/json"}
        )
        
        assert response_1.status_code == 201, "First brand registration should succeed"
        
        # Second brand user with same brand name
        signup_data_2 = {
            "email": self.generate_unique_email(),
            "password": "Password123!",
            "full_name": "Second Brand User",
            "phone_number": "2222222222",
            "role": "brand_user",
            "brand_name": brand_name
        }
        
        print(f"Attempting to register second brand user with same brand name: {brand_name}")
        response_2 = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_2,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Second Brand Registration Status Code: {response_2.status_code}")
        print(f"Second Brand Registration Response: {response_2.text}")
        
        # Assertions
        assert response_2.status_code == 400, f"Expected 400 for duplicate brand name, got {response_2.status_code}"
        
        response_data = response_2.json()
        assert "detail" in response_data, "Error response should contain detail"
        assert "brand" in response_data["detail"].lower(), "Error should mention brand"
        
        print("✓ Duplicate brand name registration correctly rejected!")
        
        # Store for cleanup
        self.test_users.append(signup_data_1)
    
    def test_invalid_email_format(self):
        """Test registration with invalid email format should fail"""
        print("\n=== Testing Invalid Email Format ===")
        
        signup_data = {
            "email": "invalid-email-format",
            "password": "Password123!",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "role": "user"
        }
        
        print(f"Attempting to register with invalid email: {signup_data['email']}")
        
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration Status Code: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        # Assertions
        assert response.status_code == 422, f"Expected 422 for invalid email, got {response.status_code}"
        
        print("✓ Invalid email format correctly rejected!")
    
    def test_missing_required_fields(self):
        """Test registration with missing required fields should fail"""
        print("\n=== Testing Missing Required Fields ===")
        
        # Test missing email
        signup_data_no_email = {
            "password": "Password123!",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "role": "user"
        }
        
        print("Testing registration without email")
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_no_email,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"No Email Status Code: {response.status_code}")
        assert response.status_code == 422, f"Expected 422 for missing email, got {response.status_code}"
        
        # Test missing password
        signup_data_no_password = {
            "email": self.generate_unique_email(),
            "full_name": "Test User",
            "phone_number": "1234567890",
            "role": "user"
        }
        
        print("Testing registration without password")
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_no_password,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"No Password Status Code: {response.status_code}")
        assert response.status_code == 422, f"Expected 422 for missing password, got {response.status_code}"
        
        print("✓ Missing required fields correctly rejected!")
    
    def test_registration_and_login_flow(self):
        """Test complete registration and login flow"""
        print("\n=== Testing Registration and Login Flow ===")
        
        # Register user
        signup_data = {
            "email": self.generate_unique_email(),
            "password": "LoginTest123!",
            "full_name": "Login Test User",
            "phone_number": "5555555555",
            "role": "user"
        }
        
        print(f"Registering user: {signup_data['email']}")
        signup_response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert signup_response.status_code == 201, "Registration should succeed"
        user_data = signup_response.json()
        
        # Login with registered user
        print("Attempting to login with registered user")
        login_data = {
            "username": signup_data["email"],
            "password": signup_data["password"]
        }
        
        login_response = self.session.post(
            f"{API_BASE}/auth/login",
            data=login_data,  # Using form data for OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login Status Code: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
        # Assertions
        assert login_response.status_code == 200, f"Login should succeed, got {login_response.status_code}"
        
        login_data = login_response.json()
        assert "access_token" in login_data, "Login response should contain access token"
        assert "token_type" in login_data, "Login response should contain token type"
        assert login_data["token_type"] == "bearer", "Token type should be bearer"
        
        # Test accessing protected endpoint
        print("Testing access to protected endpoint")
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        me_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
        
        print(f"ME Status Code: {me_response.status_code}")
        print(f"ME Response: {me_response.text}")
        
        assert me_response.status_code == 200, "Should be able to access protected endpoint"
        
        me_data = me_response.json()
        assert me_data["email"] == signup_data["email"], "User data should match"
        
        print("✓ Registration and login flow successful!")
        
        # Store for cleanup
        signup_data['access_token'] = login_data['access_token']
        self.test_users.append(signup_data)
    
    def test_password_validation(self):
        """Test password validation (if implemented)"""
        print("\n=== Testing Password Validation ===")
        
        # Test with very short password
        signup_data_short = {
            "email": self.generate_unique_email(),
            "password": "123",  # Very short password
            "full_name": "Test User",
            "phone_number": "1234567890",
            "role": "user"
        }
        
        print("Testing with very short password")
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_short,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Short Password Status Code: {response.status_code}")
        # Note: This might succeed if no password validation is implemented
        print("Password validation test completed (result depends on implementation)")
    
    def test_phone_number_validation(self):
        """Test phone number validation (if implemented)"""
        print("\n=== Testing Phone Number Validation ===")
        
        # Test with invalid phone number format
        signup_data_invalid_phone = {
            "email": self.generate_unique_email(),
            "password": "Password123!",
            "full_name": "Test User",
            "phone_number": "invalid-phone",  # Invalid phone format
            "role": "user"
        }
        
        print("Testing with invalid phone number format")
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=signup_data_invalid_phone,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Invalid Phone Status Code: {response.status_code}")
        # Note: This might succeed if no phone validation is implemented
        print("Phone number validation test completed (result depends on implementation)")


def run_registration_tests():
    """Run all registration tests"""
    print("🚀 Starting User Registration Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_check = requests.get(f"{BASE_URL}/docs", timeout=5)
        if health_check.status_code != 200:
            print("❌ Server is not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000")
        return False
    
    print("✅ Server is running, starting tests...")
    
    # Create test instance and run tests
    test_suite = TestUserRegistration()
    
    test_methods = [
        test_suite.test_successful_user_registration,
        test_suite.test_successful_brand_user_registration,
        test_suite.test_duplicate_email_registration,
        test_suite.test_duplicate_brand_name_registration,
        test_suite.test_invalid_email_format,
        test_suite.test_missing_required_fields,
        test_suite.test_registration_and_login_flow,
        test_suite.test_password_validation,
        test_suite.test_phone_number_validation
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_method()
            passed += 1
            print(f"✅ {test_method.__name__} PASSED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_method.__name__} FAILED: {str(e)}")
        finally:
            test_suite.teardown_method()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    run_registration_tests() 