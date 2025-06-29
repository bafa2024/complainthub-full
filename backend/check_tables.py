#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/complaintdb")

print(f"Checking database: {DATABASE_URL}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create inspector
    inspector = inspect(engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    
    print(f"\nFound {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")
        
        # Get columns for each table
        columns = inspector.get_columns(table)
        print(f"    Columns: {', '.join([col['name'] for col in columns])}")
    
    # Check specifically for users table
    if 'users' in tables:
        print("\n✓ Users table exists")
    else:
        print("\n✗ Users table does NOT exist")
        
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure:")
    print("1. PostgreSQL is running")
    print("2. Database 'complaintdb' exists")
    print("3. Your credentials are correct")