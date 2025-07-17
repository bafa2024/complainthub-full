import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_connection():
    # Get database URL from environment or use default
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/complaintdb")
    
    print(f"\n🔍 Testing database connection to: {db_url}")
    
    try:
        # Create engine with connection pooling and timeout
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}  # 5 second timeout
        )
        
        # Test the connection
        with engine.connect() as connection:
            print("✅ Successfully connected to the database!")
            
            # Get database version
            result = connection.execute(text("SELECT version();"))
            db_version = result.scalar()
            print(f"📊 Database version: {db_version}")
            
            # List all tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"📋 Found {len(tables)} tables: {', '.join(tables) if tables else 'No tables found'}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to the database: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify the database 'complaintdb' exists")
        print("3. Check if the username/password is correct (postgres/root)")
        print("4. Ensure PostgreSQL is listening on port 5432")
        print("5. Check if your firewall allows connections to PostgreSQL")
        return False

if __name__ == "__main__":
    test_connection()
