#!/usr/bin/env python3
"""
Script to check tickets table structure and fix urgency field issues
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_tickets_table():
    """Check the tickets table structure and fix any issues"""
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'database': 'complaintdb',
        'user': 'postgres',
        'password': 'root'
    }
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=== Checking Tickets Table Structure ===")
        
        # Check if tickets table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tickets'
            );
        """)
        
        if not cursor.fetchone()['exists']:
            print("❌ Tickets table does not exist!")
            return
        
        print("✅ Tickets table exists")
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'tickets'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Current table structure:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']}, default: {col['column_default']})")
        
        # Check if urgency column exists and its type
        urgency_col = None
        for col in columns:
            if col['column_name'] == 'urgency':
                urgency_col = col
                break
        
        if not urgency_col:
            print("\n❌ Urgency column does not exist!")
            return
        
        print(f"\n🔍 Urgency column details:")
        print(f"  - Type: {urgency_col['data_type']}")
        print(f"  - Nullable: {urgency_col['is_nullable']}")
        print(f"  - Default: {urgency_col['column_default']}")
        
        # Check if urgency is an enum or integer
        if urgency_col['data_type'] == 'USER-DEFINED':
            # It's an enum, check the enum values
            cursor.execute("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = (
                        SELECT udt_name FROM information_schema.columns 
                        WHERE table_name = 'tickets' AND column_name = 'urgency'
                    )
                )
                ORDER BY enumsortorder;
            """)
            
            enum_values = [row['enumlabel'] for row in cursor.fetchall()]
            print(f"  - Enum values: {enum_values}")
            
            if 'medium' in enum_values:
                print("✅ Urgency enum is correctly configured")
            else:
                print("❌ Urgency enum missing 'medium' value")
                
        elif urgency_col['data_type'] == 'integer':
            print("❌ Urgency is an integer field, but should be an enum!")
            print("This is causing the error. Need to convert to enum.")
            
            # Check current values in urgency column
            cursor.execute("SELECT DISTINCT urgency FROM tickets WHERE urgency IS NOT NULL;")
            current_values = [row['urgency'] for row in cursor.fetchall()]
            print(f"  - Current values: {current_values}")
            
            # Convert integer to enum
            print("\n🛠️  Converting urgency from integer to enum...")
            
            # First, create the enum type
            cursor.execute("""
                CREATE TYPE ticket_urgency_enum AS ENUM ('low', 'medium', 'high');
            """)
            
            # Add a new column with the enum type
            cursor.execute("""
                ALTER TABLE tickets ADD COLUMN urgency_new ticket_urgency_enum;
            """)
            
            # Update the new column based on integer values
            cursor.execute("""
                UPDATE tickets 
                SET urgency_new = CASE 
                    WHEN urgency = 1 THEN 'low'::ticket_urgency_enum
                    WHEN urgency = 2 THEN 'medium'::ticket_urgency_enum
                    WHEN urgency = 3 THEN 'high'::ticket_urgency_enum
                    ELSE 'medium'::ticket_urgency_enum
                END;
            """)
            
            # Drop the old column and rename the new one
            cursor.execute("ALTER TABLE tickets DROP COLUMN urgency;")
            cursor.execute("ALTER TABLE tickets RENAME COLUMN urgency_new TO urgency;")
            
            print("✅ Successfully converted urgency to enum!")
            
        else:
            print(f"⚠️  Unexpected data type for urgency: {urgency_col['data_type']}")
        
        # Test inserting a ticket with enum values
        print("\n🧪 Testing ticket insertion with enum values...")
        
        # Get a user and brand for testing
        cursor.execute("SELECT id FROM users LIMIT 1;")
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ No users found for testing")
            return
        
        cursor.execute("SELECT id FROM brands LIMIT 1;")
        brand_result = cursor.fetchone()
        if not brand_result:
            print("❌ No brands found for testing")
            return
        
        user_id = user_result['id']
        brand_id = brand_result['id']
        
        # Insert a test ticket
        cursor.execute("""
            INSERT INTO tickets (title, description, status, category, urgency, channel, owner_id, brand_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            'Test Ticket',
            'Testing enum values',
            'new',
            'complaint',
            'medium',
            'web',
            user_id,
            brand_id
        ))
        
        ticket_id = cursor.fetchone()['id']
        print(f"✅ Successfully inserted test ticket with ID: {ticket_id}")
        
        # Clean up test ticket
        cursor.execute("DELETE FROM tickets WHERE id = %s;", (ticket_id,))
        print("🧹 Cleaned up test ticket")
        
        conn.commit()
        print("\n✅ All tests passed! Urgency field is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_tickets_table() 