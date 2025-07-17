# User Registration Test Suite

This directory contains comprehensive test cases for the user registration functionality of the ComplaintHub system.

## Test Files

- `test_user_registration.py` - Main test suite with comprehensive test cases
- `run_registration_tests.py` - Simple test runner script
- `test_requirements.txt` - Testing dependencies
- `test_signup.py` - Original simple test script (legacy)

## Test Coverage

The test suite covers the following scenarios:

### ✅ Positive Test Cases
1. **Successful User Registration** - Tests basic user registration with valid data
2. **Successful Brand User Registration** - Tests brand user registration with brand creation
3. **Registration and Login Flow** - Tests complete registration → login → protected endpoint access

### ❌ Negative Test Cases
4. **Duplicate Email Registration** - Tests rejection of duplicate email addresses
5. **Duplicate Brand Name Registration** - Tests rejection of duplicate brand names
6. **Invalid Email Format** - Tests rejection of malformed email addresses
7. **Missing Required Fields** - Tests rejection when required fields are missing
8. **Password Validation** - Tests password strength requirements (if implemented)
9. **Phone Number Validation** - Tests phone number format validation (if implemented)

## Prerequisites

1. **Backend Server Running**: The FastAPI backend must be running on `http://localhost:8000`
2. **Database Setup**: Database should be initialized and accessible
3. **Dependencies Installed**: Required Python packages should be installed

## Installation

1. **Activate Virtual Environment** (if using one):
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install Testing Dependencies**:
   ```bash
   cd backend
   pip install -r test_requirements.txt
   ```

3. **Install Main Dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

### Method 1: Using the Test Runner (Recommended)
```bash
cd backend
python run_registration_tests.py
```

### Method 2: Using pytest directly
```bash
cd backend
pytest test_user_registration.py -v
```

### Method 3: Running individual test methods
```bash
cd backend
python -c "
from test_user_registration import TestUserRegistration
test = TestUserRegistration()
test.test_successful_user_registration()
"
```

## Starting the Backend Server

Before running tests, ensure the backend server is running:

```bash
cd backend
# Set PYTHONPATH
set PYTHONPATH=%cd%  # Windows
# export PYTHONPATH=$PWD  # Linux/Mac

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test Output

The test suite provides detailed output including:

- ✅ **Pass/Fail Status** for each test
- 📊 **Test Results Summary** at the end
- 🔍 **Detailed Logs** for debugging
- 🧹 **Automatic Cleanup** of test data

Example output:
```
🚀 Starting User Registration Test Suite
==================================================
✅ Server is running, starting tests...

=== Testing Successful User Registration ===
Attempting to register user: test_user_1703123456@example.com
Registration Status Code: 201
Registration Response: {"id": 1, "email": "test_user_1703123456@example.com", ...}
✓ User registration successful!
✅ test_successful_user_registration PASSED

...

==================================================
📊 Test Results: 9 passed, 0 failed
🎉 All tests passed!
```

## Troubleshooting

### Common Issues

1. **Server Not Running**
   ```
   ❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000
   ```
   **Solution**: Start the backend server first

2. **Database Connection Issues**
   ```
   ❌ Database error occurred while creating the user
   ```
   **Solution**: Check database configuration and ensure it's accessible

3. **Missing Dependencies**
   ```
   ❌ Missing required package: requests
   ```
   **Solution**: Install missing packages with `pip install -r test_requirements.txt`

4. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'app'
   ```
   **Solution**: Set PYTHONPATH to the backend directory

### Debug Mode

To run tests with more verbose output:
```bash
python run_registration_tests.py 2>&1 | tee test_output.log
```

## Test Data Management

- **Unique Emails**: Each test generates unique email addresses using timestamps
- **Automatic Cleanup**: Test users are automatically cleaned up after each test
- **Isolated Tests**: Each test runs independently to avoid interference

## Extending the Test Suite

To add new test cases:

1. Add a new test method to the `TestUserRegistration` class
2. Follow the naming convention: `test_<scenario_name>`
3. Include proper assertions and error handling
4. Add cleanup logic if needed

Example:
```python
def test_new_scenario(self):
    """Test description"""
    print("\n=== Testing New Scenario ===")
    
    # Test implementation
    # ...
    
    # Assertions
    assert condition, "Error message"
    
    print("✓ Test completed successfully!")
```

## Integration with CI/CD

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Registration Tests
  run: |
    cd backend
    pip install -r test_requirements.txt
    python run_registration_tests.py
```

## Performance Considerations

- Tests use HTTP requests to the running server
- Each test creates and potentially deletes test data
- Consider running tests against a test database in production
- Tests can be parallelized by running different test methods separately

## Security Notes

- Test passwords are simple and predictable (for testing only)
- Test data is automatically cleaned up
- No sensitive data is logged in test output
- Tests run against local development server only 