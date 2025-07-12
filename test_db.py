import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.database import test_database_connection, engine
from app.config.settings import settings

def main():
    print("=== Database Connection Test ===")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Test the connection
    result = test_database_connection()
    print("\nTest Result:")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'error':
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify the database 'complaintdb' exists")
        print("3. Check if the username/password in settings.py is correct")
        print("4. Ensure PostgreSQL is listening on port 5432")

if __name__ == "__main__":
    main()
