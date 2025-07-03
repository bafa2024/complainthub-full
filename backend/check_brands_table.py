#!/usr/bin/env python3
"""
Check brands table structure and data
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'complaintdb',
    'user': 'postgres',
    'password': 'root'
}

def check_brands_table():
    """Check brands table structure and data"""
    
    print("🔍 Checking Brands Table Structure")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if brands table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'brands'
        """)
        
        if not cursor.fetchone():
            print("❌ Brands table does not exist!")
            return
        
        print("✅ Brands table exists")
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'brands' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Brands table structure:")
        print("-" * 50)
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable} {default}")
        
        # Check for required columns
        required_columns = ['id', 'name', 'support_email', 'credit_balance', 'created_at']
        existing_columns = [col['column_name'] for col in columns]
        
        print("\n🔍 Checking required columns:")
        for req_col in required_columns:
            if req_col in existing_columns:
                print(f"  ✅ {req_col}")
            else:
                print(f"  ❌ {req_col} - MISSING!")
        
        # Check current data
        cursor.execute("SELECT COUNT(*) as count FROM brands")
        count = cursor.fetchone()['count']
        print(f"\n📊 Current brands count: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM brands ORDER BY created_at DESC LIMIT 3")
            brands = cursor.fetchall()
            print("\n📋 Latest brands:")
            for brand in brands:
                print(f"  ID: {brand['id']}, Name: {brand['name']}, Email: {brand['support_email']}")
        
        # Test inserting a brand directly
        print("\n🧪 Testing direct brand insertion...")
        try:
            cursor.execute("""
                INSERT INTO brands (name, support_email, industry, logo_url, contact_info, credit_balance)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, name, support_email
            """, ('Test Brand Direct', 'test@direct.com', 'Technology', 'https://example.com/logo.png', 'Test contact', 0.0))
            
            new_brand = cursor.fetchone()
            print(f"✅ Direct insertion successful! ID: {new_brand['id']}")
            
            # Clean up
            cursor.execute("DELETE FROM brands WHERE id = %s", (new_brand['id'],))
            print("✅ Test brand cleaned up")
            
        except Exception as e:
            print(f"❌ Direct insertion failed: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_brands_table() 