#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/complaintdb")

print(f"Fixing database: {DATABASE_URL}")

def add_column_if_not_exists(engine, table_name, column_name, column_definition):
    """Add a column to a table if it doesn't exist"""
    try:
        # Check if column exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        if column_name not in columns:
            print(f"Adding column '{column_name}' to table '{table_name}'...")
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
                conn.commit()
            print(f"✓ Added column '{column_name}' to table '{table_name}'")
        else:
            print(f"✓ Column '{column_name}' already exists in table '{table_name}'")
    except Exception as e:
        print(f"✗ Error adding column '{column_name}' to table '{table_name}': {e}")

def create_enum_if_not_exists(engine, enum_name, enum_values):
    """Create an enum type if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if enum exists
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type 
                    WHERE typname = '{enum_name}'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                print(f"Creating enum '{enum_name}'...")
                values_str = "', '".join(enum_values)
                conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ('{values_str}')"))
                conn.commit()
                print(f"✓ Created enum '{enum_name}'")
            else:
                print(f"✓ Enum '{enum_name}' already exists")
    except Exception as e:
        print(f"✗ Error creating enum '{enum_name}': {e}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ Database connection successful")
    
    # Create enums if they don't exist
    create_enum_if_not_exists(engine, "roleenum", ["user", "brand_user", "admin"])
    create_enum_if_not_exists(engine, "ticketstatusenum", ["new", "open", "in-progress", "resolved", "closed"])
    create_enum_if_not_exists(engine, "ticketcategoryenum", ["Complaint", "Feedback", "Suggestion", "Support"])
    create_enum_if_not_exists(engine, "ticketurgencyenum", ["low", "medium", "high"])
    
    # Fix users table
    print("\n--- Fixing users table ---")
    add_column_if_not_exists(engine, "users", "hashed_password", "VARCHAR")
    add_column_if_not_exists(engine, "users", "full_name", "VARCHAR")
    add_column_if_not_exists(engine, "users", "phone_number", "VARCHAR")
    add_column_if_not_exists(engine, "users", "is_active", "BOOLEAN DEFAULT TRUE")
    add_column_if_not_exists(engine, "users", "role", "roleenum DEFAULT 'user'")
    add_column_if_not_exists(engine, "users", "tts_voice_id", "VARCHAR")
    add_column_if_not_exists(engine, "users", "brand_id", "INTEGER")
    add_column_if_not_exists(engine, "users", "created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
    
    # Fix brands table
    print("\n--- Fixing brands table ---")
    add_column_if_not_exists(engine, "brands", "credit_balance", "FLOAT DEFAULT 0.0")
    add_column_if_not_exists(engine, "brands", "industry", "VARCHAR")
    add_column_if_not_exists(engine, "brands", "logo_url", "VARCHAR")
    add_column_if_not_exists(engine, "brands", "updated_at", "TIMESTAMP WITH TIME ZONE")
    
    # Fix tickets table
    print("\n--- Fixing tickets table ---")
    add_column_if_not_exists(engine, "tickets", "title", "VARCHAR")
    add_column_if_not_exists(engine, "tickets", "status", "ticketstatusenum DEFAULT 'new'")
    add_column_if_not_exists(engine, "tickets", "category", "ticketcategoryenum DEFAULT 'Complaint'")
    add_column_if_not_exists(engine, "tickets", "urgency", "ticketurgencyenum DEFAULT 'medium'")
    add_column_if_not_exists(engine, "tickets", "abuse_level_flag", "BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(engine, "tickets", "satisfaction_rating", "INTEGER")
    add_column_if_not_exists(engine, "tickets", "voice_recording_url", "VARCHAR")
    add_column_if_not_exists(engine, "tickets", "transcript", "TEXT")
    add_column_if_not_exists(engine, "tickets", "is_public", "BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(engine, "tickets", "owner_id", "INTEGER")
    add_column_if_not_exists(engine, "tickets", "assignee_id", "INTEGER")
    add_column_if_not_exists(engine, "tickets", "updated_at", "TIMESTAMP WITH TIME ZONE")
    add_column_if_not_exists(engine, "tickets", "resolved_at", "TIMESTAMP WITH TIME ZONE")
    
    # Add foreign key constraints if they don't exist
    print("\n--- Adding foreign key constraints ---")
    try:
        with engine.connect() as conn:
            # Check if foreign key exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_users_brand_id' 
                AND table_name = 'users'
            """))
            if result.scalar() == 0:
                print("Adding foreign key constraint: users.brand_id -> brands.id")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD CONSTRAINT fk_users_brand_id 
                    FOREIGN KEY (brand_id) REFERENCES brands(id)
                """))
                conn.commit()
                print("✓ Added foreign key constraint")
            else:
                print("✓ Foreign key constraint already exists")
    except Exception as e:
        print(f"✗ Error adding foreign key constraint: {e}")
    
    print("\n✓ Database migration completed successfully!")
    
    # Show final table structure
    print("\n--- Final table structure ---")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    for table in tables:
        print(f"\nTable: {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nMake sure:")
    print("1. PostgreSQL is running")
    print("2. Database 'complaintdb' exists")
    print("3. Your credentials are correct")
    sys.exit(1) 