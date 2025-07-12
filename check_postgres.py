import psycopg2
from psycopg2 import OperationalError
import time

def check_postgres_connection(host='localhost', port=5432, user='postgres', password='root', dbname='complaintdb'):
    print("🔍 Testing PostgreSQL connection...")
    
    try:
        # Try to connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=5
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        # Get database information
        cursor.execute("""
            SELECT datname, usename, application_name, client_addr, state 
            FROM pg_stat_activity 
            WHERE pid = pg_backend_pid();
        """)
        db_info = cursor.fetchone()
        
        print("✅ Successfully connected to PostgreSQL!")
        print(f"📊 PostgreSQL Version: {db_version[0]}")
        print(f"🔌 Connection Info: Database='{db_info[0]}', User='{db_info[1]}', Application='{db_info[2]}'")
        
        # List all databases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = [db[0] for db in cursor.fetchall()]
        print(f"📚 Available databases: {', '.join(databases)}")
        
        cursor.close()
        conn.close()
        return True
        
    except OperationalError as e:
        print(f"❌ Could not connect to PostgreSQL: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if the database 'complaintdb' exists")
        print("3. Verify the username/password (postgres/root)")
        print("4. Ensure PostgreSQL is listening on port 5432")
        print("5. Check if your firewall allows connections to PostgreSQL")
        print("\nCommon solutions:")
        print("- If you're using XAMPP, make sure the PostgreSQL service is running")
        print("- Try running: `sudo service postgresql start` (Linux/Mac) or start PostgreSQL service in Windows Services")
        print("- If the database doesn't exist, create it with: `createdb complaintdb`")
        return False

if __name__ == "__main__":
    check_postgres_connection()
